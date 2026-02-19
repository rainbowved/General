from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from wt_client.core.error_reporter import ErrorContext, ErrorReporter

from wt_client.core.action_dispatcher import ActionDispatcher
from wt_client.core.changelog_engine import ChangelogApplyError, ChangelogEngine
from wt_client.core.master_changelog import apply_master_changelog, parse_master_changelog
from wt_client.core.content_pack import ContentPack, ContentPackLoader
from wt_client.core.config import AppConfig, resolve_repo_config_path
from wt_client.core.node_interactions import NodeInteractions
from wt_client.core.recent_actions import get_cursor, get_recent_delta_events, set_cursor
from wt_client.core.rng_engine import RngEngine
from wt_client.core.save_store import SaveIOError, SaveStore
from wt_client.core.logging_setup import setup_logging
from wt_client.core.schema_validate import validate_turnpack
from wt_client.core.turnpack_builder import TurnpackBuilder, TurnpackMeta
from wt_client.core.validate_pack import format_health_report, validate_pack
from wt_client.core.save_workflow import apply_master_changelog_and_autosave, dispatch_and_autosave
from wt_client.core.support_bundle import create_support_bundle
from wt_client.core.migrations import migrate_save_payload
from wt_client.core.loot_resolver import LootResolver
from wt_client.core.craft_resolver import CraftResolver, CookResolver, AlchemyResolver
from wt_client.core.inventory_delta import build_add_instances, apply_add_instances, count_item_qty
from wt_client.ui.app import run_app


def _read_json(path: str | Path) -> Any:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def _print_list(title: str, xs: List[str]) -> None:
    if not xs:
        return
    print(title)
    for x in xs:
        print(" -", x)


def _extract_demo_save(pack: ContentPack, save_root: Path) -> Path:
    runtime = save_root / "demo_runtime_cli"
    if runtime.exists():
        shutil.rmtree(runtime)
    runtime.mkdir(parents=True, exist_ok=True)

    for rel in pack.list_files():
        reln = rel.replace("\\", "/").lstrip("/")
        if reln.startswith("demo/save/") or reln.startswith("demo/session/"):
            data = pack.open_binary(reln)
            dst = runtime / reln.split("demo/", 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)

    return runtime


def _build_turnpack(state: Mapping[str, Any]) -> Dict[str, Any]:
    meta = TurnpackMeta.from_state(state)
    delta = get_recent_delta_events(state, last_actions=10)
    return TurnpackBuilder().build(state, recent_actions=delta, meta=meta)


def _load_rng_spec(pack: ContentPack) -> Dict[str, Any]:
    files = set(pack.list_files())
    for rel in (
        "content/core/rng.json",  # db_bundle format
        f"{pack.layout.specs_dir}/rng_streams.json" if pack.layout.specs_dir else None,
    ):
        if not rel:
            continue
        if rel in files:
            doc = pack.load_json(rel)
            if isinstance(doc, dict) and isinstance(doc.get("streams"), list):
                return doc
    # Fallback minimal spec
    return {
        "schema_version": "rng_streams.fallback.v1",
        "streams": [
            {"stream_id": "RNG_LOOT"},
            {"stream_id": "RNG_CRAFT"},
            {"stream_id": "RNG_COMBAT"},
            {"stream_id": "RNG_SPAWN"},
            {"stream_id": "RNG_VENDOR"},
        ],
    }


def _find_items_sqlite(pack: ContentPack) -> Optional[str]:
    # Reuse the same heuristics as CraftResolver, but keep it local for CLI.
    names = [p.replace("\\", "/") for p in pack.list_files()]
    candidates = [p for p in names if p.endswith("rpg_items.sqlite") or p.endswith("rpg_items_write.sqlite")]
    if candidates:
        return sorted(candidates)[0]
    return None


def _query_one_item(pack: ContentPack, sql: str, params: tuple = ()) -> Optional[str]:
    import sqlite3

    p = _find_items_sqlite(pack)
    if not p:
        return None
    # For zip packs, open via pack.open_binary and materialize into temp file.
    # Simpler: ContentPack already extracts zip to a temp folder; for zip it is not.
    # So here we read bytes and use a NamedTemporaryFile.
    try:
        data = pack.open_binary(p)
    except Exception:
        return None
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=True) as tf:
        tf.write(data)
        tf.flush()
        con = sqlite3.connect(tf.name)
        try:
            cur = con.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            if row and isinstance(row[0], str):
                return row[0]
        finally:
            con.close()
    return None


def _main_subcommands(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="wt_client")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # --- loot ---
    ap_loot = sub.add_parser("loot", help="Loot tools")
    sub_loot = ap_loot.add_subparsers(dest="loot_cmd", required=True)

    ap_loot_demo = sub_loot.add_parser("demo", help="Resolve a loot_pool and optionally apply to a save")
    ap_loot_demo.add_argument("--content", required=True, help="Path to db_bundle zip/folder or full datapack")
    ap_loot_demo.add_argument("--pool", default=None, help="loot_pool_id (default: first pool in items_loot.json)")
    ap_loot_demo.add_argument("--picks", type=int, default=3)
    ap_loot_demo.add_argument("--seed", type=str, default="seed_loot_demo")
    ap_loot_demo.add_argument("--save", type=str, default=None, help="Optional SAVE directory to mutate")
    ap_loot_demo.add_argument("--write", action="store_true", help="If --save is provided, write back to disk")

    # --- craft/cook/alchemy ---
    def _add_recipe_run_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--content", required=True, help="Path to db_bundle zip/folder or full datapack")
        p.add_argument("--recipe", required=True, help="recipe_id")
        p.add_argument("--seed", type=str, default="seed_craft_demo")
        p.add_argument("--save", type=str, default=None, help="Optional SAVE directory to mutate")
        p.add_argument("--write", action="store_true", help="If --save is provided, write back to disk")
        p.add_argument(
            "--autofill",
            action="store_true",
            help="If no --save is provided, auto-grant required ingredients into a minimal state",
        )

    ap_craft = sub.add_parser("craft", help="Run recipes (any craft_kind)")
    sub_craft = ap_craft.add_subparsers(dest="craft_cmd", required=True)
    ap_craft_run = sub_craft.add_parser("run", help="Run a recipe")
    _add_recipe_run_args(ap_craft_run)

    ap_cook = sub.add_parser("cook", help="Run COOKING recipes")
    sub_cook = ap_cook.add_subparsers(dest="cook_cmd", required=True)
    ap_cook_run = sub_cook.add_parser("run", help="Run a COOKING recipe")
    _add_recipe_run_args(ap_cook_run)

    ap_alch = sub.add_parser("alchemy", help="Run ALCHEMY recipes")
    sub_alch = ap_alch.add_subparsers(dest="alch_cmd", required=True)
    ap_alch_run = sub_alch.add_parser("run", help="Run an ALCHEMY/ALCHEMY_ENDGAME recipe")
    _add_recipe_run_args(ap_alch_run)

    args = ap.parse_args(argv)

    # Common helpers
    loader = ContentPackLoader()

    if args.cmd == "loot" and args.loot_cmd == "demo":
        with loader.load(str(args.content)) as pack:
            rng_spec = _load_rng_spec(pack)
            rng = RngEngine(rng_spec)
            rng.init(args.seed)
            state: Dict[str, Any]
            store = SaveStore()
            if args.save:
                state = store.load_save(Path(args.save))
            else:
                state = {"inventory": {"items": []}}

            loot = LootResolver(pack)
            pool_id = args.pool
            if not pool_id:
                # pick first pool id deterministically
                pools = sorted([p for p in loot._pool_items.keys()])  # type: ignore[attr-defined]
                if not pools:
                    print("ERROR: no loot pools found")
                    return 3
                pool_id = pools[0]

            res = loot.apply_loot_pool(pool_id, state, rng, picks=int(args.picks), ts="1970-01-01T00:00:00Z")
            print(json.dumps({"loot_pool_id": res.loot_pool_id, "instances": [r.__dict__ for r in res.instances], "events": list(res.events)}, ensure_ascii=False, indent=2))

            if args.save and args.write:
                store.save_save(Path(args.save), state)
                print(f"\nSaved: {args.save}")
        return 0

    if args.cmd in ("craft", "cook", "alchemy"):
        with loader.load(str(args.content)) as pack:
            rng_spec = _load_rng_spec(pack)
            rng = RngEngine(rng_spec)
            rng.init(args.seed)

            store = SaveStore()
            state: Dict[str, Any]
            if getattr(args, "save", None):
                state = store.load_save(Path(args.save))
            else:
                state = {"inventory": {"items": []}}

            if args.cmd == "cook":
                resolver: CraftResolver = CookResolver(pack)
            elif args.cmd == "alchemy":
                resolver = AlchemyResolver(pack)
            else:
                resolver = CraftResolver(pack)

            if not getattr(args, "save", None) and getattr(args, "autofill", False):
                # Auto-grant ingredients for a minimal demo run.
                recipe = resolver.get_recipe(args.recipe)
                grants: List[Dict[str, Any]] = []
                for i, (iid, qty) in enumerate(recipe.ingredients):
                    if iid.startswith("GROUP_"):
                        cand = _query_one_item(
                            pack,
                            "SELECT item_id FROM items WHERE type='SERUM' AND rarity='legendary' ORDER BY item_id LIMIT 1"
                            if iid == "GROUP_HERITAGE_SERUM_ANY"
                            else "SELECT item_id FROM items WHERE rarity='legendary' AND type IN ('LEG_MATERIAL','LEG_CORE') ORDER BY item_id LIMIT 1",
                        )
                        if not cand:
                            raise SystemExit(f"Cannot autofill group ingredient: {iid}")
                        grants.append({"instance_id": f"AUTO_{iid}_{i}", "item_id": cand, "qty": int(qty)})
                    else:
                        grants.append({"instance_id": f"AUTO_{iid}_{i}", "item_id": iid, "qty": int(qty)})
                inst = build_add_instances(grants, origin={"kind": "cli_autofill"})
                apply_add_instances(state, inst)

            before = count_item_qty(state)
            res = resolver.apply_craft(args.recipe, state, rng, ts="1970-01-01T00:00:00Z")
            after = count_item_qty(state)

            print(
                json.dumps(
                    {
                        "recipe_id": res.recipe_id,
                        "resolved_ingredients": list(res.resolved_ingredients),
                        "produced": list(res.produced),
                        "events": list(res.events),
                        "inventory_before": before,
                        "inventory_after": after,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

            if getattr(args, "save", None) and getattr(args, "write", False):
                store.save_save(Path(args.save), state)
                print(f"\nSaved: {args.save}")
        return 0

    print("ERROR: unknown command")
    return 2


def main(argv: Optional[List[str]] = None) -> int:
    argv_list = list(argv) if argv is not None else list(sys.argv[1:])
    if argv_list and argv_list[0] in {"loot", "craft", "cook", "alchemy"}:
        # Modern subcommand CLI (used by stage 9 demos).
        return _main_subcommands(argv_list)

    ap = argparse.ArgumentParser(prog="wt_client", description="WT client (C31)")

    ap.add_argument("--pack", type=str, default=None, help="Path to WT_data_release_candidate.zip (optional, overrides config)")
    ap.add_argument("--config", type=str, default=None, help="Path to wt_client/config.json (optional)")


    ap.add_argument("--db-audit", action="store_true", help="Read-only audit of db_bundle sqlite schema")
    ap.add_argument("--health", action="store_true", help="Validate content pack")
    ap.add_argument("--health-datapack", action="store_true", help="Strict datapack health")
    ap.add_argument("--health-dbbundle", action="store_true", help="Validate bare db_bundle")

    ap.add_argument("--demo", action="store_true", help="Use demo save (extracted from pack)")
    ap.add_argument("--save", type=str, default=None, help="Path to SAVE directory")

    ap.add_argument("--list-backups", action="store_true", help="List available backups for the save")
    ap.add_argument("--restore-backup", type=str, default=None, help="Restore backup ZIP into the save")
    ap.add_argument("--restore-backup-index", type=int, default=None, help="Restore backup by index (use --list-backups)")

    ap.add_argument("--apply-changelog", type=str, default=None, help="Apply master changelog JSON to the save")
    ap.add_argument(
        "--lenient",
        action="store_true",
        help="Lenient changelog mode: ignore unknown events with warnings (strict by default)",
    )

    ap.add_argument("--act", type=str, default=None, help="Action request JSON string or path")
    ap.add_argument("--export-turnpack", type=str, default=None, help="Export TURNPACK to file")

    ap.add_argument(
        "--support-bundle",
        nargs="?",
        const="AUTO",
        default=None,
        help="Create a support bundle ZIP (optional output path; default is logs_dir/support_bundles)",
    )

    ap.add_argument("--ui", action="store_true", help="Run Tkinter UI")
    ap.add_argument("--migrate-save", action="store_true", help="Migrate save file JSON")
    ap.add_argument("--in", dest="migrate_in", type=str, default=None, help="Input save json path")
    ap.add_argument("--out", dest="migrate_out", type=str, default=None, help="Output save json path")

    args = ap.parse_args(argv_list)

    if args.migrate_save:
        if not args.migrate_in or not args.migrate_out:
            print("ERROR: --migrate-save requires --in and --out")
            return 2
        src = Path(args.migrate_in)
        dst = Path(args.migrate_out)
        doc = json.loads(src.read_text(encoding="utf-8"))
        out_doc, rep = migrate_save_payload(doc)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(out_doc, ensure_ascii=False, sort_keys=True, indent=2)+"\n", encoding="utf-8")
        bak = dst.with_suffix(dst.suffix + ".backup.json")
        bak.write_text(json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2)+"\n", encoding="utf-8")
        print(f"Migrated -> {dst}")
        for st in rep.steps:
            print(f" - {st}")
        return 0

    # Error UX hardening (C15): never print tracebacks in CLI.
    reporter = ErrorReporter(".wt_logs")
    reporter.install_sys_excepthook()
    try:
        setup_logging(".wt_logs")
    except Exception:
        # Logging is best-effort; keep running.
        pass

    # Resolve pack path: CLI --pack overrides config.json.
    cfg_path = args.config or resolve_repo_config_path()
    try:
        cfg = AppConfig.load(cfg_path)
    except Exception as e:
        # Broken config should not kill CLI with a traceback.
        reporter.write_traceback(type(e), e, e.__traceback__, context=ErrorContext(where="config.load"))
        if cfg_path:
            print(f"ERROR: invalid config file: {cfg_path}: {e}")
        else:
            print(f"ERROR: invalid config: {e}")
        cfg = AppConfig.defaults()
    pack_path = args.pack or cfg.datapack_path
    if not pack_path:
        print("ERROR: datapack path is required (use --pack or set datapack_path in wt_client/config.json)")
        return 2

    try:
        pack = ContentPackLoader().load(pack_path)
    except FileNotFoundError:
        print(f"ERROR: datapack not found: {pack_path}")
        print("Hint: use --pack <path> or set datapack_path in wt_client/config.json")
        print(f"See log: {reporter.logfile}")
        return 2
    except Exception as e:
        reporter.write_traceback(type(e), e, e.__traceback__, context=ErrorContext(where="pack.load"))
        print(f"ERROR: failed to load datapack: {pack_path}")
        print(f"Reason: {e}")
        print(f"See log: {reporter.logfile}")
        return 2

    try:
        if args.health or args.health_datapack:
            rep = validate_pack(pack, mode="datapack")
            print(format_health_report(rep), end="")
            return 0 if rep.ok else 3

        if args.health_dbbundle:
            rep = validate_pack(pack, mode="dbbundle")
            print(format_health_report(rep), end="")
            return 0 if rep.ok else 3

        if args.db_audit:
            try:
                from wt_client.core.db_bundle_audit import audit_db_bundle

                rep = audit_db_bundle(pack)
                print("[WT DB_BUNDLE AUDIT]")
                if not rep.sqlite_files:
                    print("No sqlite files found in pack.")
                else:
                    print("sqlite files:")
                    for p in rep.sqlite_files:
                        print(f" - {p}")
                for a in rep.audits:
                    if a.items_guess is None:
                        continue
                    g = a.items_guess
                    print("items schema guess:")
                    print(f" sqlite: {a.relpath}")
                    print(f" table: {g.table} (id={g.id_col}, name={g.name_col})")
                    if g.tags_col:
                        print(f" tags: {g.tags_col}")
                    if g.desc_col:
                        print(f" description: {g.desc_col}")
                    if g.notes:
                        for n in g.notes:
                            print(f" note: {n}")
                    break
                return 0
            except Exception as e:
                reporter.write_traceback(type(e), e, e.__traceback__, context=ErrorContext(where="db_audit"))
                print(f"ERROR: db audit failed: {e}")
                print(f"See log: {reporter.logfile}")
                return 3

        if args.ui:
            try:
                run_app(pack)
            except Exception as e:
                # Tk init/callback errors must never dump a traceback.
                reporter.write_traceback(type(e), e, e.__traceback__, context=ErrorContext(where="ui"))
                print(f"ERROR: UI failed: {type(e).__name__}: {e}")
                print(f"See log: {reporter.logfile}")
                return 7
            return 0
    finally:
        try:
            pack.close()
        except Exception:
            pass

    # NOTE: pack is closed above for --health/--ui early exits.
    # For CLI flow below we need a live pack: reload it (lightweight; zip handle only).
    try:
        pack = ContentPackLoader().load(pack_path)
    except Exception as e:
        reporter.write_traceback(type(e), e, e.__traceback__, context=ErrorContext(where="pack.reload"))
        print(f"ERROR: failed to load datapack: {pack_path}")
        print(f"Reason: {e}")
        print(f"See log: {reporter.logfile}")
        return 2

    try:
        # Determine save dir
        save_dir: Optional[Path] = None
        if args.demo:
            save_dir = _extract_demo_save(pack, Path(".wt_cli_tmp"))
        elif args.save:
            save_dir = Path(args.save).expanduser()

        if not save_dir:
            print("ERROR: provide --demo or --save")
            return 2

        store = SaveStore()

        # Restore / list backups (operate on disk, before load).
        if args.list_backups:
            bps = store.list_backups(save_dir)
            if not bps:
                print("No backups found.")
            else:
                print("Backups:")
                for i, p in enumerate(bps):
                    print(f" [{i}] {p.name}")
            return 0

        if args.restore_backup or args.restore_backup_index is not None:
            try:
                if args.restore_backup:
                    store.restore_backup(save_dir, args.restore_backup)
                    print(f"Restored backup: {args.restore_backup}")
                else:
                    bps = store.list_backups(save_dir)
                    idx = int(args.restore_backup_index)
                    if idx < 0 or idx >= len(bps):
                        print(f"ERROR: backup index out of range: {idx}")
                        return 2
                    store.restore_backup(save_dir, bps[idx])
                    print(f"Restored backup: {bps[idx].name}")
            except SaveIOError as e:
                print("Restore failed:")
                print(str(e))
                return 4

        try:
            state = store.load_save(save_dir)
        except Exception as e:
            print("Load save failed:")
            print(str(e))
            return 3

        cursor = get_cursor(state) or {"seen_event_ids": [], "seen_hash": ""}

        # If demo: apply demo changelog exactly once (idempotent by cursor)
        if args.demo:
            try:
                demo_doc = pack.load_json("demo/changelog/changelog.json")
                demo_events = parse_master_changelog(demo_doc).events
                ce = ChangelogEngine()
                state, cursor, applied = ce.apply(demo_events, state, cursor=cursor)
                set_cursor(state, cursor)
                # sync RNG snapshot
                try:
                    rng = RngEngine(pack.load_json("specs/rng_streams.json"))
                    ses = state.get("session")
                    if isinstance(ses, dict) and isinstance(ses.get("rng_state"), dict):
                        rng.restore(ses.get("rng_state"))
                        state["rng"] = rng.snapshot()
                except Exception:
                    pass
                if applied > 0:
                    store.save_save(save_dir, state)
            except ChangelogApplyError as e:
                _print_list("Demo changelog apply failed:", list(e.problems))
                return 4
            except SaveIOError as e:
                print("Autosave failed:")
                print(str(e))
                return 4

        if args.apply_changelog:
            try:
                doc = _read_json(args.apply_changelog)
                state, cursor, summary, ar = apply_master_changelog_and_autosave(
                    doc,
                    store=store,
                    save_dir=save_dir,
                    state=state,
                    cursor=cursor,
                    lenient=bool(args.lenient),
                )
                # sync RNG snapshot
                try:
                    rng = RngEngine(pack.load_json("specs/rng_streams.json"))
                    ses = state.get("session")
                    if isinstance(ses, dict) and isinstance(ses.get("rng_state"), dict):
                        rng.restore(ses.get("rng_state"))
                        state["rng"] = rng.snapshot()
                except Exception:
                    pass
                print("Master CHANGELOG summary:")
                print(f" - events_total: {summary.events_total}")
                print(f" - applied: {summary.applied}")
                print(f" - skipped_duplicates: {summary.skipped_duplicates}")
                print(f" - autosave: {'yes' if ar.saved else 'no'}")
                if args.lenient:
                    print(f" - unknown_ignored: {summary.unknown_ignored}")
                if summary.warnings:
                    _print_list("Warnings:", summary.warnings)
            except (ValueError, ChangelogApplyError, SaveIOError) as e:
                if isinstance(e, ChangelogApplyError):
                    _print_list("Apply failed:", list(e.problems))
                else:
                    # Schema errors are already path+reason in the message.
                    print("Apply failed:")
                    print(str(e))
                return 4

        if args.act:
            try:
                act_arg = args.act
                if Path(act_arg).exists():
                    act = _read_json(act_arg)
                else:
                    act = json.loads(act_arg)
                if not isinstance(act, dict):
                    raise ValueError("--act expects a JSON object")

                interactions = NodeInteractions(pack.load_json("specs/node_interactions.json"))
                rng = RngEngine(pack.load_json("specs/rng_streams.json"))
                dispatcher = ActionDispatcher(pack, interactions, rng)
                res, ar = dispatch_and_autosave(
                    dispatcher,
                    store=store,
                    save_dir=save_dir,
                    action_request=act,
                    state=state,
                    cursor=cursor,
                )

                _print_list("Warnings:", res.warnings)
                _print_list("Errors:", res.errors)
                for line in res.ui_log:
                    print(line)

                if not res.ok:
                    return 5

                state, cursor = res.new_state, res.new_cursor
                print(f"autosave={'yes' if ar.saved else 'no'}")

            except Exception as e:
                print("ERROR:", str(e))
                return 5

        if args.export_turnpack:
            try:
                tp = _build_turnpack(state)
                schema_json = pack.load_json("specs/turnpack_schema.json")
                ok, errs = validate_turnpack(tp, schema_json)
                if not ok:
                    raise ValueError("TURNPACK schema errors: " + "; ".join([str(e) for e in errs]))
                Path(args.export_turnpack).write_text(json.dumps(tp, ensure_ascii=False, indent=2), encoding="utf-8")
                # Track last exported TURNPACK for support bundles.
                try:
                    Path(".wt_logs").mkdir(parents=True, exist_ok=True)
                    Path(".wt_logs", "last_turnpack.json").write_text(
                        json.dumps(tp, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                except Exception:
                    pass
                print(f"Wrote TURNPACK: {args.export_turnpack}")
            except Exception as e:
                print("TURNPACK export failed:", str(e))
                return 6

        if args.support_bundle is not None:
            try:
                out = None if args.support_bundle == "AUTO" else str(args.support_bundle)
                res = create_support_bundle(
                    logs_dir=".wt_logs",
                    save_dir=save_dir,
                    pack_path=pack.source_path,
                    state=state,
                    out_path=out,
                )
                print(f"Support bundle: {res.path} (files={res.files_added})")
            except Exception as e:
                print("Support bundle failed:")
                print(str(e))
                print(f"See log: {reporter.logfile}")
                return 7

        return 0
    finally:
        try:
            pack.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
