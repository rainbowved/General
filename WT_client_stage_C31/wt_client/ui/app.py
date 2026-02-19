from __future__ import annotations

import json
import os
import re
import shutil
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from typing import Any, Dict, List, Optional

from wt_client.core.error_reporter import ErrorContext, ErrorReporter

from wt_client.core.action_dispatcher import ActionDispatcher
from wt_client.core.changelog_engine import ChangelogApplyError, ChangelogEngine
from wt_client.core.action_catalog import ActionCatalog, ActionCatalogError
from wt_client.core.content_pack import ContentPack
from wt_client.core.master_changelog import parse_master_changelog
from wt_client.core.recent_actions import get_cursor, get_recent_delta_events, set_cursor
from wt_client.core.rng_engine import RngEngine
from wt_client.core.save_store import SaveIOError, SaveStore
from wt_client.core.save_workflow import apply_master_changelog_and_autosave, dispatch_and_autosave
from wt_client.core.logging_setup import setup_logging
from wt_client.core.schema_validate import validate_turnpack
from wt_client.core.turnpack_builder import TurnpackBuilder, TurnpackMeta
from wt_client.core.inventory_delta import count_item_qty
from wt_client.core.item_catalog import ItemCatalog, ItemCatalogError
from wt_client.core.world_node_view import resolve_current_node_view
from wt_client.core.support_bundle import create_support_bundle


def _extract_demo_save(pack: ContentPack, save_root: Path) -> Path:
    runtime = save_root / "demo_runtime"
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


def _sync_rng_snapshot(state: Dict[str, Any], streams_spec: Dict[str, Any]) -> None:
    try:
        ses = state.get("session")
        if isinstance(ses, dict) and isinstance(ses.get("rng_state"), dict):
            rng = RngEngine(streams_spec)
            rng.restore(ses.get("rng_state"))
            state["rng"] = rng.snapshot()
    except Exception:
        pass

# --- Save slots (C18) ---

_INVALID_SLOT_CHARS = r'<>:"/\|?*'


def _sanitize_slot_name(name: str) -> str:
    """Make a filename-safe slot name (Windows-friendly)."""
    name = (name or '').strip()
    if not name:
        return ''
    out = []
    for ch in name:
        if ch in _INVALID_SLOT_CHARS or ord(ch) < 32:
            out.append('_')
        else:
            out.append(ch)
    s = ''.join(out)
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.rstrip(' .')
    return s


def _copy_demo_template_to_slot(pack: ContentPack, slot_root: Path) -> None:
    """Create a new save slot by copying demo/save + demo/session from the pack."""
    tmp = slot_root.parent / f'.slot_tmp_{slot_root.name}_{os.getpid()}_{os.urandom(4).hex()}'
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)

    copied = 0
    for rel in pack.list_files():
        reln = rel.replace('\\', '/').lstrip('/')
        if reln.startswith('demo/save/') or reln.startswith('demo/session/'):
            data = pack.open_binary(reln)
            dst = tmp / reln.split('demo/', 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            copied += 1

    if copied == 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError('Datapack has no demo template (missing demo/save or demo/session)')

    try:
        _ = SaveStore().load_save(tmp)
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f'Demo template is not a valid save: {e}')

    if slot_root.exists():
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f'Slot already exists: {slot_root}')
    tmp.rename(slot_root)


def _choose_save_slot_dialog(root: tk.Tk, pack: ContentPack, *, default_root: Path) -> Optional[Path]:
    """Modal dialog to pick or create a save slot."""
    result: Dict[str, Optional[Path]] = {'path': None}

    dlg = tk.Toplevel(root)
    dlg.title('Save slot')
    dlg.geometry('520x220')
    dlg.transient(root)
    dlg.grab_set()

    msg = (
        'Выбери слот сохранения:\n'
        '• Открыть существующий слот (папка сейва)\n'
        '• Создать новый слот из demo template (из datapack RC)\n'
    )
    tk.Label(dlg, text=msg, justify='left', anchor='w').pack(fill='x', padx=12, pady=10)

    status_var = tk.StringVar(value='')
    tk.Label(dlg, textvariable=status_var, anchor='w').pack(fill='x', padx=12)

    btns = tk.Frame(dlg)
    btns.pack(fill='x', padx=12, pady=12)

    def close_with(path: Optional[Path]) -> None:
        result['path'] = path
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()

    def on_open_existing() -> None:
        p = filedialog.askdirectory(title='Select SAVE folder', initialdir=str(default_root))
        if not p:
            return
        cand = Path(p).expanduser()
        try:
            _ = SaveStore().load_save(cand)
        except Exception as e:
            status_var.set(f'Не похоже на сейв: {e}')
            return
        close_with(cand)

    def on_create_from_demo() -> None:
        parent = filedialog.askdirectory(title='Select folder for new slot', initialdir=str(default_root))
        if not parent:
            return
        name = simpledialog.askstring('New slot', 'Имя слота (папка):', parent=dlg)
        name = _sanitize_slot_name(name or '')
        if not name:
            status_var.set('Имя слота пустое/некорректное')
            return
        slot = Path(parent).expanduser() / name
        try:
            _copy_demo_template_to_slot(pack, slot)
        except Exception as e:
            status_var.set(str(e))
            return
        close_with(slot)

    def on_cancel() -> None:
        close_with(None)

    tk.Button(btns, text='Открыть существующий…', command=on_open_existing).pack(side='left', padx=4)
    tk.Button(btns, text='Новый из demo…', command=on_create_from_demo).pack(side='left', padx=4)
    tk.Button(btns, text='Отмена', command=on_cancel).pack(side='right', padx=4)

    dlg.protocol('WM_DELETE_WINDOW', on_cancel)
    root.wait_window(dlg)
    return result['path']



@dataclass
class WTAppModel:
    pack: ContentPack
    store: SaveStore
    save_dir: Path
    state: Dict[str, Any]

    def cursor(self) -> Dict[str, Any]:
        return get_cursor(self.state) or {"seen_event_ids": [], "seen_hash": ""}

    def delta_events(self) -> List[Dict[str, Any]]:
        return get_recent_delta_events(self.state, last_actions=10)


def run_app(pack: ContentPack) -> None:
    # Error UX hardening (C15): keep UI free from tracebacks.
    logs_dir = ".wt_logs"
    reporter = ErrorReporter(logs_dir)
    reporter.install_sys_excepthook()
    try:
        setup_logging(logs_dir)
    except Exception:
        pass

    try:
        root = tk.Tk()
    except tk.TclError as e:
        reporter.write_traceback(type(e), e, e.__traceback__, context=ErrorContext(where="tk.init"))
        # In headless environments we cannot show message boxes.
        raise RuntimeError(f"UI unavailable: {e}")

    root.title("WT Client (C31)")
    root.geometry("1100x720")

    def _tk_report_callback_exception(exc, val, tb):
        # This prevents Tk from dumping tracebacks to stderr.
        try:
            reporter.write_traceback(exc, val, tb, context=ErrorContext(where="tk.callback"))
        except Exception:
            pass
        try:
            messagebox.showerror("WT Client error", f"{exc.__name__}: {val}\n\nSee log: {reporter.logfile}")
        except Exception:
            # Last resort: keep it silent.
            pass

    root.report_callback_exception = _tk_report_callback_exception  # type: ignore[assignment]

    try:
        default_root = Path("./saves")
        default_root.mkdir(parents=True, exist_ok=True)
        chosen = _choose_save_slot_dialog(root, pack, default_root=default_root)
        if chosen is None:
            root.destroy()
            return
        save_dir = chosen
        store = SaveStore()
        try:
            state = store.load_save(save_dir)
        except Exception as e:
            try:
                messagebox.showerror("Load save failed", str(e))
            except Exception:
                pass
            root.destroy()
            return
        m = WTAppModel(pack=pack, store=store, save_dir=save_dir, state=state)
    except Exception as e:
        reporter.write_traceback(type(e), e, e.__traceback__, context=ErrorContext(where="ui.start"))
        try:
            messagebox.showerror("WT Client startup failed", f"{type(e).__name__}: {e}\n\nSee log: {reporter.logfile}")
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass
        raise RuntimeError(f"UI startup failed: {type(e).__name__}: {e}")

    catalog = ActionCatalog(pack)
    interactions = catalog.interactions

    # UI widgets
    top = tk.Frame(root)
    top.pack(fill=tk.X, padx=8, pady=6)

    info_var = tk.StringVar(value="")
    info = tk.Label(top, textvariable=info_var, anchor="w")
    info.pack(side=tk.LEFT, fill=tk.X, expand=True)

    slot_controls = tk.Frame(top)
    slot_controls.pack(side=tk.RIGHT)


    def refresh_info() -> None:
        loc = ((((m.state.get("world") or {}).get("world") or {}).get("location") or {}))
        cur = m.cursor()
        de = m.delta_events()
        info_var.set(
            f"Slot: {str(m.save_dir)}  | "
            f"Loc: {loc.get('region')}/{loc.get('location_id')}/{loc.get('sub_id')}  | "
            f"cursor={len(cur.get('seen_event_ids') or [])}  | delta_events={len(de)}"
        )

    # Tabs (C19): Actions/Logs, Inventory (read-only), Node card (read-only)
    tabs = ttk.Notebook(root)
    tabs.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    tab_main = ttk.Frame(tabs)
    tab_inv = ttk.Frame(tabs)
    tab_node = ttk.Frame(tabs)
    tabs.add(tab_main, text="Actions")
    tabs.add(tab_inv, text="Inventory")
    tabs.add(tab_node, text="Node")

    buttons = tk.Frame(tab_main)
    buttons.pack(fill=tk.X, padx=0)

    # Backups UX (C18): show rolling backups and restore by click.
    backups_panel = tk.LabelFrame(tab_main, text="Rolling backups")
    backups_panel.pack(fill=tk.X, padx=0, pady=(6, 0))

    backups_list: List[Path] = []

    backups_lb = tk.Listbox(backups_panel, height=5)
    backups_lb.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=6)

    backups_side = tk.Frame(backups_panel)
    backups_side.pack(side=tk.RIGHT, padx=6, pady=6)

    def _fmt_backup_name(p: Path) -> str:
        # Expected: YYYYMMDD_HHMMSS_cursor000123_000.zip
        m = re.match(r"(\d{8}_\d{6})_cursor(\d+)_\d+\.zip$", p.name)
        if m:
            ts, cur = m.group(1), int(m.group(2))
            return f"{ts}  cursor={cur}"
        return p.name

    def refresh_backups() -> None:
        nonlocal backups_list
        try:
            items = m.store.list_backups(m.save_dir)
        except Exception:
            items = []
        # newest first
        backups_list = list(reversed(items))
        backups_lb.delete(0, tk.END)
        for bp in backups_list:
            backups_lb.insert(tk.END, _fmt_backup_name(bp))

    def on_restore_selected_backup() -> None:
        sel = backups_lb.curselection()
        if not sel:
            messagebox.showinfo("Restore", "Select a backup first")
            return
        bp = backups_list[int(sel[0])]
        if not messagebox.askyesno("Restore", f"Restore backup?\n\n{bp.name}\n\nCurrent save will be replaced."):
            return
        try:
            m.store.restore_backup(m.save_dir, bp)
            m.state = m.store.load_save(m.save_dir)
            refresh_info()
            refresh_actions()
            refresh_backups()
            refresh_inventory()
            refresh_node_card()
            refresh_neighbors()
            log(f"✅ Restored backup: {bp.name}")
        except SaveIOError as e:
            messagebox.showerror("Restore", str(e))
        except Exception as e:
            messagebox.showerror("Restore", str(e))

    tk.Button(backups_side, text="Refresh", command=refresh_backups).pack(fill=tk.X, pady=(0, 6))
    tk.Button(backups_side, text="Restore selected", command=on_restore_selected_backup).pack(fill=tk.X)


    lenient_var = tk.BooleanVar(value=False)

    actions_panel = tk.LabelFrame(tab_main, text="Доступные действия здесь")
    actions_panel.pack(fill=tk.X, padx=0, pady=(6, 0))

    log_box = scrolledtext.ScrolledText(tab_main, height=22)
    log_box.pack(fill=tk.BOTH, expand=True, padx=0, pady=8)

    def log(msg: str) -> None:
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)

    # --- Inventory viewer (C19, read-only) ---
    inv_top = tk.Frame(tab_inv)
    inv_top.pack(fill=tk.X, padx=6, pady=6)

    inv_status_var = tk.StringVar(value="")
    tk.Label(inv_top, textvariable=inv_status_var, anchor="w").pack(fill=tk.X)

    inv_body = tk.Frame(tab_inv)
    inv_body.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

    inv_list = tk.Listbox(inv_body, width=48)
    inv_list.pack(side=tk.LEFT, fill=tk.Y)

    inv_card = scrolledtext.ScrolledText(inv_body)
    inv_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

    item_catalog: Optional[ItemCatalog] = None
    inv_rows: List[Dict[str, Any]] = []

    def _ensure_item_catalog() -> Optional[ItemCatalog]:
        nonlocal item_catalog
        if item_catalog is not None:
            return item_catalog
        try:
            item_catalog = ItemCatalog(m.pack)
            log(f"📚 Item DB: {item_catalog.sqlite_relpath}")
            return item_catalog
        except ItemCatalogError as e:
            inv_status_var.set(f"Item DB unavailable: {e}")
            item_catalog = None
            return None
        except Exception as e:
            inv_status_var.set(f"Item DB unavailable: {e}")
            item_catalog = None
            return None

    def refresh_inventory() -> None:
        nonlocal inv_rows
        inv_list.delete(0, tk.END)
        inv_card.delete("1.0", tk.END)

        totals = count_item_qty(m.state)
        cat = _ensure_item_catalog()

        rows: List[Dict[str, Any]] = []
        for item_id, qty in totals.items():
            name = str(item_id)
            if cat:
                rec = cat.get(str(item_id))
                if rec:
                    name = rec.name_ru
            rows.append({"item_id": str(item_id), "qty": int(qty), "name": name})

        rows.sort(key=lambda r: (str(r.get("name") or ""), str(r.get("item_id") or "")))
        inv_rows = rows

        total_qty = sum(r["qty"] for r in rows)
        inv_status_var.set(f"Unique items: {len(rows)} | Total qty: {total_qty}")

        for r in rows:
            inv_list.insert(tk.END, f"{r['qty']:>4}  {r['name']}  ({r['item_id']})")

    def _render_item_card(item_id: str) -> str:
        cat = _ensure_item_catalog()
        rec = cat.get(item_id) if cat else None
        if not rec:
            return f"{item_id}\n\n(нет записи в items DB)"
        lines: List[str] = []
        lines.append(f"{rec.name_ru}  [{rec.item_id}]")
        lines.append("")
        lines.append(f"type: {rec.type}")
        lines.append(f"group: {rec.group}")
        lines.append(f"class: {rec.class_}")
        if rec.tier is not None:
            lines.append(f"tier: {rec.tier}")
        if rec.rarity:
            lines.append(f"rarity: {rec.rarity}")
        if rec.tags:
            lines.append(f"tags: {', '.join(rec.tags)}")
        if rec.description:
            lines.append("")
            lines.append(rec.description)
        if rec.extra:
            lines.append("")
            lines.append("extra:")
            try:
                lines.append(json.dumps(rec.extra, ensure_ascii=False, indent=2))
            except Exception:
                lines.append(str(rec.extra))
        return "\n".join(lines)

    def on_inv_select(_evt=None) -> None:
        sel = inv_list.curselection()
        if not sel:
            return
        r = inv_rows[int(sel[0])]
        inv_card.delete("1.0", tk.END)
        inv_card.insert(tk.END, _render_item_card(str(r.get("item_id") or "")))

    inv_list.bind("<<ListboxSelect>>", on_inv_select)

    # --- Node (C20): card + neighbors + quick actions ---
    node_split = ttk.PanedWindow(tab_node, orient=tk.HORIZONTAL)
    node_split.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    node_left = ttk.Frame(node_split)
    node_right = ttk.Frame(node_split)
    node_split.add(node_left, weight=3)
    node_split.add(node_right, weight=2)

    node_box = scrolledtext.ScrolledText(node_left)
    node_box.pack(fill=tk.BOTH, expand=True)

    nav_panel = tk.LabelFrame(node_right, text="Навигация (соседние узлы)")
    nav_panel.pack(fill=tk.BOTH, expand=False)

    nav_status_var = tk.StringVar(value="")
    tk.Label(nav_panel, textvariable=nav_status_var, anchor="w", justify="left").pack(fill=tk.X, padx=6, pady=(6, 2))

    nav_controls = tk.Frame(nav_panel)
    nav_controls.pack(fill=tk.X, padx=6, pady=(0, 6))

    def _go_selected_neighbor() -> None:
        nid = selected_neighbor_var.get().strip()
        if not nid:
            messagebox.showinfo("Move", "Сначала выбери соседа")
            return
        on_dispatch({"type": "move", "to_node_id": nid})

    tk.Button(nav_controls, text="Перейти выбранный", command=_go_selected_neighbor).pack(side=tk.LEFT)
    tk.Button(nav_controls, text="Сброс", command=lambda: (selected_neighbor_var.set(""), refresh_neighbors())).pack(
        side=tk.LEFT, padx=6
    )

    neighbors_frame = tk.Frame(nav_panel)
    neighbors_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

    node_actions_panel = tk.LabelFrame(node_right, text="Действия (capabilities)")
    node_actions_panel.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    selected_neighbor_var = tk.StringVar(value="")

    def refresh_node_card() -> None:
        node_box.delete("1.0", tk.END)
        loc = _cur_loc(m.state)
        graph_id = str(loc.get("location_id") or "")
        node_id = str(loc.get("sub_id") or "")
        node_box.insert(tk.END, f"Location: {loc.get('region')}/{graph_id}/{node_id}\n\n")

        view = None
        try:
            view = resolve_current_node_view(m.pack, m.state)
        except Exception as e:
            node_box.insert(tk.END, f"Node view unavailable: {e}\n")
            return
        if not view:
            node_box.insert(tk.END, "Node view unavailable: no world graph/ui data found in pack.\n")
            return

        ui = view.ui
        title = ui.get("title")
        desc = ui.get("description")
        services = ui.get("services")
        tags = ui.get("tags")
        links = ui.get("links")

        if title:
            node_box.insert(tk.END, f"title: {title}\n")
        if desc:
            node_box.insert(tk.END, f"description: {desc}\n")
        if services is not None:
            node_box.insert(tk.END, "\nservices:\n")
            try:
                node_box.insert(tk.END, json.dumps(services, ensure_ascii=False, indent=2) + "\n")
            except Exception:
                node_box.insert(tk.END, str(services) + "\n")
        if tags is not None:
            node_box.insert(tk.END, "\ntags:\n")
            try:
                node_box.insert(tk.END, json.dumps(tags, ensure_ascii=False, indent=2) + "\n")
            except Exception:
                node_box.insert(tk.END, str(tags) + "\n")
        if links is not None:
            node_box.insert(tk.END, "\nlinks:\n")
            try:
                node_box.insert(tk.END, json.dumps(links, ensure_ascii=False, indent=2) + "\n")
            except Exception:
                node_box.insert(tk.END, str(links) + "\n")

        node_box.insert(tk.END, "\nraw_node:\n")
        try:
            node_box.insert(tk.END, json.dumps(view.raw_node, ensure_ascii=False, indent=2) + "\n")
        except Exception:
            node_box.insert(tk.END, str(view.raw_node) + "\n")

    def _cur_loc(st: Dict[str, Any]) -> Dict[str, Any]:
        return ((((st.get("world") or {}).get("world") or {}).get("location") or {}))

    def _fmt_tags(v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            try:
                return ", ".join([str(x) for x in v])
            except Exception:
                return str(v)
        if isinstance(v, dict):
            # common: {"type":"SHOP"} or similar
            try:
                return ", ".join([f"{k}:{v[k]}" for k in sorted(v.keys())])
            except Exception:
                return str(v)
        return str(v)

    def refresh_neighbors() -> None:
        # Clear
        for child in list(neighbors_frame.winfo_children()):
            child.destroy()

        loc = _cur_loc(m.state)
        graph_id = str(loc.get("location_id") or "")
        node_id = str(loc.get("sub_id") or "")

        try:
            from wt_client.core.world_resolver import WorldResolver, WorldResolverError

            wr = WorldResolver(m.pack)
            nbs = wr.get_neighbors(m.state)
        except Exception as e:
            nav_status_var.set(f"Loc: {loc.get('region')}/{graph_id}/{node_id} | neighbors: ? (ошибка: {e})")
            tk.Label(neighbors_frame, text=f"(не удалось получить соседей: {e})").pack(anchor="w")
            return

        nav_status_var.set(
            f"Loc: {loc.get('region')}/{graph_id}/{node_id} | neighbors: {len(nbs)} | selected: {selected_neighbor_var.get() or '—'}"
        )

        if not nbs:
            tk.Label(neighbors_frame, text="(соседей нет — тупик или граф без рёбер)").pack(anchor="w")
            return

        def _row_for(nid: str) -> None:
            try:
                node = wr.get_node_by_id(m.state, nid)
            except Exception:
                node = {"node_id": nid}

            ui = node.get("ui") if isinstance(node, dict) else None
            ui = dict(ui) if isinstance(ui, dict) else {}
            title = ui.get("title") or ui.get("title_ru") or node.get("title") or nid

            typ = (
                node.get("node_type")
                or node.get("type")
                or node.get("kind")
                or ui.get("type")
                or ui.get("kind")
                or ""
            )
            tags = ui.get("tags") or node.get("tags")
            tag_s = _fmt_tags(tags)
            info = ""
            if typ:
                info += str(typ)
            if tag_s:
                info += (" | " if info else "") + tag_s

            row = tk.Frame(neighbors_frame)
            row.pack(fill=tk.X, pady=2)

            def _select() -> None:
                selected_neighbor_var.set(str(nid))
                nav_status_var.set(
                    f"Loc: {loc.get('region')}/{graph_id}/{node_id} | neighbors: {len(nbs)} | selected: {nid}"
                )

            def _go() -> None:
                selected_neighbor_var.set(str(nid))
                on_dispatch({"type": "move", "to_node_id": str(nid)})

            tk.Button(row, text="Выбрать", command=_select, width=8).pack(side=tk.LEFT)
            tk.Button(row, text="Перейти", command=_go, width=8).pack(side=tk.LEFT, padx=(4, 8))
            tk.Label(row, text=str(title), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
            if info:
                tk.Label(row, text=f"[{info}]", anchor="e").pack(side=tk.RIGHT)

        for nid in nbs:
            _row_for(str(nid))

    def refresh_actions() -> None:
        def _render_into(panel: tk.Widget, *, write_log: bool) -> None:
            # Clear
            for child in list(panel.winfo_children()):
                child.destroy()

            loc = _cur_loc(m.state)
            graph_id = str(loc.get("location_id") or "")
            node_id = str(loc.get("sub_id") or "")
            if not graph_id or not node_id:
                tk.Label(panel, text="(локация не определена)").pack(anchor="w", padx=6, pady=4)
                return

            try:
                items = catalog.list_actions(graph_id, node_id)
            except (ActionCatalogError, Exception) as e:
                tk.Label(panel, text=f"(не удалось получить действия: {e})").pack(anchor="w", padx=6, pady=4)
                return

            if not items:
                tk.Label(panel, text="(нет доступных действий)").pack(anchor="w", padx=6, pady=4)
                return

            order = ["travel", "explore", "rest", "service", "other"]
            ru = {
                "travel": "Путь / переход",
                "explore": "Исследование",
                "rest": "Отдых",
                "service": "Сервисы",
                "other": "Другое",
            }
            grouped: Dict[str, List[Any]] = {k: [] for k in order}
            for it in items:
                grouped.setdefault(it.group, []).append(it)

            def on_node_action(meta: Any) -> None:
                if write_log:
                    hint = f"▶️ {meta.label} [{meta.action_id}]"
                    if meta.record_only:
                        hint += " (record-only)"
                    log(hint)
                    if meta.description:
                        log("   " + meta.description)
                on_dispatch({"type": "node_action", "action_id": meta.action_id})

            for g in order:
                xs = grouped.get(g) or []
                if not xs:
                    continue
                box = tk.LabelFrame(panel, text=ru.get(g, g))
                box.pack(fill=tk.X, padx=6, pady=4)
                row = tk.Frame(box)
                row.pack(fill=tk.X, padx=4, pady=4)

                for it in xs:
                    txt = f"{it.label} [{it.action_id}]"
                    if it.record_only:
                        txt += "*"
                    tk.Button(row, text=txt, command=lambda m=it: on_node_action(m)).pack(
                        side=tk.LEFT, padx=3, pady=2
                    )

            tk.Label(panel, text="* — действие фиксируется и ждёт ответа мастера").pack(
                anchor="w", padx=10, pady=(0, 6)
            )

        _render_into(actions_panel, write_log=True)
        _render_into(node_actions_panel, write_log=False)

    def _load_slot(new_save_dir: Path) -> bool:
        try:
            st = m.store.load_save(new_save_dir)
        except Exception as e:
            messagebox.showerror("Load save", str(e))
            return False
        m.save_dir = Path(new_save_dir)
        m.state = st
        log(f"📁 Active slot: {m.save_dir}")
        refresh_info()
        refresh_actions()
        refresh_inventory()
        refresh_node_card()
        refresh_neighbors()
        refresh_backups()
        refresh_inventory()
        refresh_node_card()
        refresh_neighbors()
        refresh_backups()
        refresh_inventory()
        refresh_node_card()
        return True

    def on_change_slot() -> None:
        default_root = Path("./saves")
        default_root.mkdir(parents=True, exist_ok=True)
        chosen = _choose_save_slot_dialog(root, m.pack, default_root=default_root)
        if chosen is None:
            return
        _load_slot(chosen)

    # Slot control buttons (top-right)
    tk.Button(slot_controls, text="Change slot…", command=on_change_slot).pack(side=tk.RIGHT, padx=4)



    def _apply_events_to_state(events: List[Dict[str, Any]]) -> None:
        ce = ChangelogEngine()
        cur = m.cursor()
        st, new_cur, applied = ce.apply(events, m.state, cursor=cur)
        m.state = st
        set_cursor(m.state, new_cur)
        try:
            _sync_rng_snapshot(m.state, m.pack.load_json("specs/rng_streams.json"))
        except Exception:
            pass
        if applied > 0:
            m.store.save_save(m.save_dir, m.state)
            log(f"✅ Applied: {applied} event(s) (autosaved)")
        else:
            log("ℹ️ No changes (duplicates); autosave skipped")

    def on_apply_demo() -> None:
        try:
            demo_doc = m.pack.load_json("demo/changelog/changelog.json")
            evs = parse_master_changelog(demo_doc).events
            _apply_events_to_state(evs)
            refresh_info()
            refresh_actions()
            refresh_inventory()
            refresh_node_card()
            refresh_neighbors()
        except (ValueError, ChangelogApplyError, SaveIOError) as e:
            msg = "\n".join(e.problems) if isinstance(e, ChangelogApplyError) else str(e)
            messagebox.showerror("Apply demo changelog", msg)

    def on_apply_master_changelog() -> None:
        path = filedialog.askopenfilename(
            title="Select master changelog.json",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            doc = json.loads(Path(path).read_text(encoding="utf-8"))

            st, cur, summary, ar = apply_master_changelog_and_autosave(
                doc,
                store=m.store,
                save_dir=m.save_dir,
                state=m.state,
                cursor=m.cursor(),
                lenient=bool(lenient_var.get()),
            )
            m.state = st
            try:
                _sync_rng_snapshot(m.state, m.pack.load_json("specs/rng_streams.json"))
            except Exception:
                pass
            autosaved = bool(ar.saved)

            lines = [
                "✅ Master CHANGELOG applied",
                f"events_total={summary.events_total}",
                f"applied={summary.applied}",
                f"skipped_duplicates={summary.skipped_duplicates}",
            ]
            lines.append("autosave=yes" if autosaved else "autosave=skipped")
            if lenient_var.get():
                lines.append(f"unknown_ignored={summary.unknown_ignored}")
            if summary.warnings:
                lines.append("warnings:")
                lines.extend([" - " + w for w in summary.warnings[:20]])
                if len(summary.warnings) > 20:
                    lines.append(f"... +{len(summary.warnings) - 20} more")

            for ln in lines:
                log(ln)
            messagebox.showinfo("Apply master changelog", "\n".join(lines))

            refresh_info()
            refresh_actions()
            refresh_inventory()
            refresh_node_card()
            refresh_neighbors()
        except (ValueError, ChangelogApplyError, SaveIOError) as e:
            msg = "\n".join(e.problems) if isinstance(e, ChangelogApplyError) else str(e)
            messagebox.showerror("Apply master changelog", msg)

    def on_dispatch(act: Dict[str, Any]) -> None:
        rng = RngEngine(m.pack.load_json("specs/rng_streams.json"))
        dispatcher = ActionDispatcher(m.pack, interactions, rng)

        before_loc = _cur_loc(m.state)
        res, ar = dispatch_and_autosave(
            dispatcher,
            store=m.store,
            save_dir=m.save_dir,
            action_request=act,
            state=m.state,
            cursor=m.cursor(),
        )

        for w in res.warnings:
            log("⚠️ " + w)
        for u in res.ui_log:
            log(u)
        for e in res.errors:
            log("❌ " + e)

        if not res.ok:
            return

        m.state = res.new_state
        if res.applied > 0 and not ar.saved:
            log("❌ Autosave failed: " + str(ar.message))
        if res.applied <= 0:
            log("ℹ️ No changes (duplicates/no-op); autosave skipped")

        after_loc = _cur_loc(m.state)
        if before_loc != after_loc:
            log(
                f"📍 Локация: {before_loc.get('region')}/{before_loc.get('location_id')}/{before_loc.get('sub_id')}"
                f" → {after_loc.get('region')}/{after_loc.get('location_id')}/{after_loc.get('sub_id')}"
            )
        log(f"📦 events={len(res.events)} applied={res.applied}")

        # For record-only node actions, be explicit.
        if act.get("type") == "node_action" and isinstance(act.get("action_id"), str):
            if catalog.is_record_only(str(act.get("action_id"))):
                log("🧾 Запрос зафиксирован, изменения ожидаются ответом мастера.")

        refresh_info()
        refresh_actions()

    def on_move() -> None:
        try:
            # naive pick: first neighbor
            from wt_client.core.world_resolver import WorldResolver

            wr = WorldResolver(m.pack)
            nbs = wr.get_neighbors(m.state)
            if not nbs:
                log("🧱 Нет соседних узлов для перемещения")
                return
            to_id = nbs[0]
            on_dispatch({"type": "move", "to_node_id": to_id})
        except Exception as e:
            log("❌ " + str(e))

    def on_proceed() -> None:
        on_dispatch({"type": "node_action", "action_id": "PROCEED"})

    def on_export_turnpack() -> None:
        try:
            meta = TurnpackMeta.from_state(m.state)
            delta = m.delta_events()
            tp = TurnpackBuilder().build(m.state, recent_actions=delta, meta=meta)

            schema_json = m.pack.load_json("specs/turnpack_schema.json")
            ok, errs = validate_turnpack(tp, schema_json)
            if not ok:
                msg = "\n".join([str(e) for e in errs])
                messagebox.showerror("TURNPACK validation", msg)
                return

            path = filedialog.asksaveasfilename(
                title="Save TURNPACK.json",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if not path:
                return
            Path(path).write_text(json.dumps(tp, ensure_ascii=False, indent=2), encoding="utf-8")
            # Track last exported TURNPACK for support bundles (no gameplay impact).
            try:
                Path(logs_dir).mkdir(parents=True, exist_ok=True)
                Path(logs_dir, "last_turnpack.json").write_text(
                    json.dumps(tp, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            except Exception:
                pass
            log(f"💾 TURNPACK saved: {path}")
        except Exception as e:
            messagebox.showerror("Export TURNPACK", str(e))

    def on_support_bundle() -> None:
        try:
            res = create_support_bundle(
                logs_dir=logs_dir,
                save_dir=m.save_dir,
                pack_path=m.pack.source_path,
                state=m.state,
            )
            log(f"🧰 Support bundle created: {res.path} (files={res.files_added})")
            try:
                messagebox.showinfo("Support bundle", f"Created:\n{res.path}\n\nFiles: {res.files_added}")
            except Exception:
                pass
        except Exception as e:
            # Keep UX clean; details go to log via logger.exception in support_bundle.
            try:
                messagebox.showerror("Support bundle", str(e))
            except Exception:
                pass

    def on_export_delta_changelog() -> None:
        try:
            delta = m.delta_events()
            path = filedialog.asksaveasfilename(
                title="Save delta CHANGELOG.json",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
            )
            if not path:
                return
            doc = {"events": delta}
            Path(path).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
            log(f"💾 Delta CHANGELOG saved: {path}")
        except Exception as e:
            messagebox.showerror("Export CHANGELOG", str(e))

    def on_restore_backup() -> None:
        bdir = Path(m.save_dir) / m.store.BACKUPS_DIRNAME
        initial_dir = str(bdir) if bdir.exists() else str(m.save_dir)
        path = filedialog.askopenfilename(
            title="Select backup ZIP",
            initialdir=initial_dir,
            filetypes=[("Backup ZIP", "*.zip"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            m.store.restore_backup(m.save_dir, path)
            m.state = m.store.load_save(m.save_dir)
            refresh_info()
            refresh_actions()
            refresh_inventory()
            refresh_node_card()
            refresh_neighbors()
            log(f"✅ Restored backup: {Path(path).name}")
            messagebox.showinfo("Restore", "Backup restored successfully")
        except SaveIOError as e:
            messagebox.showerror("Restore", str(e))
        except Exception as e:
            messagebox.showerror("Restore", str(e))

    tk.Button(buttons, text="Apply demo changelog", command=on_apply_demo).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Apply master changelog…", command=on_apply_master_changelog).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Restore (file)…", command=on_restore_backup).pack(side=tk.LEFT, padx=4)
    tk.Checkbutton(buttons, text="Lenient (ignore unknown)", variable=lenient_var).pack(side=tk.LEFT, padx=10)
    tk.Button(buttons, text="Move (first neighbor)", command=on_move).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="PROCEED", command=on_proceed).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Export TURNPACK…", command=on_export_turnpack).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Export delta CHANGELOG…", command=on_export_delta_changelog).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Support bundle…", command=on_support_bundle).pack(side=tk.LEFT, padx=10)

    refresh_info()
    refresh_actions()
    refresh_backups()
    refresh_inventory()
    refresh_node_card()
    refresh_neighbors()
    log("WT Client UI ready.")
    root.mainloop()
