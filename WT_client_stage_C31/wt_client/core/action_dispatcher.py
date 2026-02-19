from __future__ import annotations

import copy
import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .changelog_engine import ChangelogApplyError, ChangelogEngine
from .craft_resolver import CraftError, CraftResolver
from .encounter_resolver import EncounterResolver
from .inventory_delta import build_add_instances
from .loot_resolver import LootResolver
from .node_interactions import NodeInteractions
from .recent_actions import append_recent_action, get_cursor, set_cursor
from .rng_engine import RngEngine
from .turnpack_builder import TurnpackBuilder, TurnpackMeta
from .world_resolver import WorldResolver, WorldResolverError
from .meter_engine import apply_meter_action


log = logging.getLogger("wt_client.dispatch")


@dataclass
class DispatchResult:
    ok: bool
    new_state: Dict[str, Any]
    new_cursor: Dict[str, Any]
    events: List[Dict[str, Any]]
    ui_log: List[str]
    errors: List[str]
    warnings: List[str]
    applied: int = 0


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _get_save_id(state: Mapping[str, Any]) -> str:
    meta = state.get("meta")
    if isinstance(meta, dict) and isinstance(meta.get("save_id"), str) and meta.get("save_id"):
        return str(meta.get("save_id"))
    # fallback: player.save_id
    player = state.get("player")
    if isinstance(player, dict) and isinstance(player.get("save_id"), str) and player.get("save_id"):
        return str(player.get("save_id"))
    return "SAVE_UNKNOWN"


def _get_turn_no(state: Mapping[str, Any]) -> int:
    ses = state.get("session")
    if isinstance(ses, dict) and isinstance(ses.get("active_turn"), int):
        return int(ses.get("active_turn"))
    return 0


def _action_event_id(
    state: Mapping[str, Any],
    action_type: str,
    payload: Mapping[str, Any],
    cursor: Optional[Mapping[str, Any]],
) -> str:
    save_id = _get_save_id(state)
    turn_no = _get_turn_no(state)
    # IMPORTANT: do NOT include cursor/seenset in the event id.
    # Idempotency is enforced *by* the cursor (seen_event_ids), but the id itself
    # must remain stable across replays.
    _ = cursor  # kept for backward signature compatibility
    s = f"{save_id}|{turn_no}|{action_type}|{_canonical_json(payload)}"
    return _sha256_hex(s)[:16]


def _cursor_has(cursor: Optional[Mapping[str, Any]], event_id: str) -> bool:
    if not isinstance(cursor, Mapping):
        return False
    seen = cursor.get("seen_event_ids")
    return isinstance(seen, list) and event_id in seen


def _derive_child_event_id(root_event_id: str, tag: str) -> str:
    return _sha16(f"{root_event_id}|{tag}")


class ActionDispatcher:
    """Single execution point for player actions.

    Invariants:
    - atomic: uses deepcopy + commit via ChangelogEngine
    - idempotent: root event_id is sha256(save_id+turn+type+payload)+cursor digest
    - deterministic: given same state+cursor+action_request => same events and result
    """

    def __init__(self, pack: Any, interactions: NodeInteractions, rng: RngEngine):
        self._pack = pack
        self._interactions = interactions
        self._rng = rng
        self._world = WorldResolver(pack)
        self._enc = EncounterResolver(pack)
        self._loot = LootResolver(pack)
        self._craft = CraftResolver(pack)
        self._changelog = ChangelogEngine()

    # --- capabilities helpers (UI/CLI) ---
    # NOTE: this is NOT a new mechanic; it's a read-only declaration of what the
    # dispatcher can apply locally.
    _LOCAL_EFFECT_NODE_ACTION_IDS = frozenset(
        {
            # Produces real state-changing events (WORLD_MOVE / MODE_SET / inventory deltas).
            "PROCEED",
            "REST",
            "CAMP_REST",
            "EXIT_CITY",
            "ENTER_CITY",
            "ENTER_TOWER",
        }
    )

    @classmethod
    def local_effect_node_action_ids(cls) -> set[str]:
        return set(cls._LOCAL_EFFECT_NODE_ACTION_IDS)

    @classmethod
    def is_record_only_node_action_id(cls, action_id: str) -> bool:
        return str(action_id) not in cls._LOCAL_EFFECT_NODE_ACTION_IDS

    # --- public API ---
    def dispatch(
        self,
        action_request: Mapping[str, Any],
        state: Mapping[str, Any],
        cursor: Optional[Dict[str, Any]],
    ) -> DispatchResult:
        ui_log: List[str] = []
        warnings: List[str] = []
        errors: List[str] = []

        if not isinstance(action_request, Mapping):
            return DispatchResult(
                ok=False,
                new_state=copy.deepcopy(state) if isinstance(state, Mapping) else {},
                new_cursor=cursor or {},
                events=[],
                ui_log=[],
                errors=["action_request: expected object"],
                warnings=[],
            )

        act_type = action_request.get("type")
        if not isinstance(act_type, str) or not act_type:
            return DispatchResult(
                ok=False,
                new_state=copy.deepcopy(state) if isinstance(state, Mapping) else {},
                new_cursor=cursor or {},
                events=[],
                ui_log=[],
                errors=["action_request.type: expected non-empty string"],
                warnings=[],
            )

        # Determine effective cursor (caller-provided overrides stored state cursor).
        cur_in = cursor if cursor is not None else get_cursor(state) or None

        # Canonical payload for idempotency.
        payload = {k: v for k, v in action_request.items() if k != "type"}
        root_eid = _action_event_id(state, act_type, payload, cur_in)
        ts = str(_get_turn_no(state))

        if _cursor_has(cur_in, root_eid):
            # Idempotent replay: no events, no changes.
            return DispatchResult(
                ok=True,
                new_state=copy.deepcopy(state) if isinstance(state, Mapping) else {},
                new_cursor=copy.deepcopy(cur_in) if isinstance(cur_in, Mapping) else {},
                events=[],
                ui_log=["♻️ Повтор действия: уже применено (idempotent)."],
                errors=[],
                warnings=[],
                applied=0,
            )

        # Work on a copy only after we know we'll do something.
        work_state: Dict[str, Any] = copy.deepcopy(state) if isinstance(state, Mapping) else {}

        try:
            if act_type == "move":
                evs, ui = self._handle_move(root_eid, action_request, work_state, ts)
                ui_log.extend(ui)
                events = evs
            elif act_type == "node_action":
                evs, ui, warn = self._handle_node_action(root_eid, action_request, work_state, ts)
                ui_log.extend(ui)
                warnings.extend(warn)
                events = evs
            elif act_type == "craft":
                # Craft uses RNG.
                self._ensure_rng_initialized(work_state)
                evs, ui = self._handle_craft(root_eid, action_request, work_state, ts)
                ui_log.extend(ui)
                events = evs
            else:
                return DispatchResult(
                    ok=False,
                    new_state=work_state,
                    new_cursor=copy.deepcopy(cur_in) if isinstance(cur_in, Mapping) else {},
                    events=[],
                    ui_log=[],
                    errors=[f"Unsupported action_request.type: {act_type}"],
                    warnings=[],
                )

        except (ValueError, WorldResolverError, CraftError) as e:
            errors.append(str(e))
            return DispatchResult(
                ok=False,
                new_state=copy.deepcopy(state) if isinstance(state, Mapping) else {},
                new_cursor=copy.deepcopy(cur_in) if isinstance(cur_in, Mapping) else {},
                events=[],
                ui_log=ui_log,
                errors=errors,
                warnings=warnings,
            )
        except Exception as e:
            # keep user output clean
            log.exception("dispatch failed")
            errors.append(f"Internal error: {type(e).__name__}")
            return DispatchResult(
                ok=False,
                new_state=copy.deepcopy(state) if isinstance(state, Mapping) else {},
                new_cursor=copy.deepcopy(cur_in) if isinstance(cur_in, Mapping) else {},
                events=[],
                ui_log=ui_log,
                errors=errors,
                warnings=warnings,
            )

        # Pure no-op: keep state/cursor unchanged.
        if not events:
            return DispatchResult(
                ok=True,
                new_state=copy.deepcopy(state) if isinstance(state, Mapping) else {},
                new_cursor=copy.deepcopy(cur_in) if isinstance(cur_in, Mapping) else {},
                events=[],
                ui_log=ui_log,
                errors=[],
                warnings=warnings,
                applied=0,
            )

        # Apply as changelog (atomic + cursor-based idempotency).
        try:
            new_state, new_cursor, applied = self._changelog.apply(events, work_state, cursor=cur_in)
        except ChangelogApplyError as e:
            return DispatchResult(
                ok=False,
                new_state=copy.deepcopy(state) if isinstance(state, Mapping) else {},
                new_cursor=copy.deepcopy(cur_in) if isinstance(cur_in, Mapping) else {},
                events=[],
                ui_log=ui_log,
                errors=list(e.problems),
                warnings=warnings,
            )

        # If RNG is initialized, snapshot it for persistence.
        if self._rng.is_initialized:
            try:
                new_state["rng"] = self._rng.snapshot()
            except Exception:
                pass

        # Persist cursor and recent_actions into the state.
        try:
            set_cursor(new_state, new_cursor)
        except Exception:
            pass

        try:
            append_recent_action(new_state, action_request, events)
        except Exception:
            pass

        # Return only the events that were actually applied.
        out_events = events if applied > 0 else []

        return DispatchResult(
            ok=True,
            new_state=new_state,
            new_cursor=new_cursor,
            events=out_events,
            ui_log=ui_log,
            errors=[],
            warnings=warnings,
            applied=applied,
        )

    # Convenience for CLI/UI export
    def build_turnpack(self, state: Mapping[str, Any]) -> Dict[str, Any]:
        from .recent_actions import get_recent_delta_events

        meta = TurnpackMeta.from_state(state)
        delta = get_recent_delta_events(state, last_actions=10)
        pack = TurnpackBuilder().build(state, recent_actions=delta, meta=meta)
        return pack

    # --- handlers ---
    def _handle_move(self, root_eid: str, req: Mapping[str, Any], state: Mapping[str, Any], ts: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        to_node_id = req.get("to_node_id")
        if not isinstance(to_node_id, str) or not to_node_id:
            raise ValueError("move.to_node_id: expected non-empty string")
        try:
            _ns, mv = self._world.move(to_node_id, state, ts=ts)
        except WorldResolverError as e:
            raise ValueError(str(e)) from e

        mv = dict(mv)
        mv["event_id"] = root_eid
        mv.setdefault("source", "player")
        mv["ts"] = ts
        frm = (mv.get("payload") or {}).get("from") or {}
        st2 = apply_meter_action(state, "move")
        meters = ((st2.get("player") or {}).get("meters") or {})
        meter_events = [
            {"event_id": _derive_child_event_id(root_eid, "meter:fat"), "ts": ts, "source": "system", "type": "METER_SET", "payload": {"key": "fat_current", "value": int(meters.get("fat_current", 0))}},
            {"event_id": _derive_child_event_id(root_eid, "meter:thirst"), "ts": ts, "source": "system", "type": "METER_SET", "payload": {"key": "thirst", "value": int(meters.get("thirst", 0))}},
        ]
        return [mv] + meter_events, [f"🚶 Перемещение: {frm.get('sub_id')} → {to_node_id}"]

    def _handle_node_action(
        self, root_eid: str, req: Mapping[str, Any], state: Dict[str, Any], ts: str
    ) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
        action_id = req.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            raise ValueError("node_action.action_id: expected non-empty string")

        node = self._world.get_current_node(state)
        available = {a["action_id"] for a in self._world.get_available_actions(node, state)}
        if action_id not in available:
            # Not available => true no-op.
            return [], [f"🛑 Действие '{action_id}' недоступно в текущей локации."], []

        loc = (((state.get("world") or {}).get("world") or {}).get("location") or {})
        root_event = {
            "event_id": root_eid,
            "ts": ts,
            "source": "player",
            "type": "action.request",
            "payload": {
                "action_id": action_id,
                "at": {
                    "region": loc.get("region"),
                    "location_id": loc.get("location_id"),
                    "sub_id": loc.get("sub_id"),
                },
                "args": {k: v for k, v in req.items() if k not in ("type", "action_id")},
            },
        }

        # --- supported handlers (C11) ---
        if action_id == "PROCEED":
            # PROCEED uses RNG.
            self._ensure_rng_initialized(state)
            return self._handle_node_proceed(root_event, root_eid, node, state, ts)

        if action_id in {"REST", "CAMP_REST"}:
            mode = "REST" if action_id == "REST" else "CAMP"
            mode_event = {
                "event_id": _derive_child_event_id(root_eid, f"mode:{mode}"),
                "ts": ts,
                "source": "system",
                "type": "MODE_SET",
                "payload": {"mode": mode},
            }
            txt = "😴 Отдых" if action_id == "REST" else "⛺ Лагерь: отдых"
            st2 = apply_meter_action(state, action_id)
            meters = ((st2.get("player") or {}).get("meters") or {})
            meter_events = [
                {"event_id": _derive_child_event_id(root_eid, "meter:fat"), "ts": ts, "source": "system", "type": "METER_SET", "payload": {"key": "fat_current", "value": int(meters.get("fat_current", 0))}}
            ]
            return [root_event, mode_event] + meter_events, [txt], []

        if action_id in {"EXIT_CITY", "ENTER_CITY", "ENTER_TOWER"}:
            evs, ui = self._handle_cross_location_move(root_eid, root_event, action_id, state, ts)
            return evs, ui, []

        if action_id == "WATER_REFILL":
            st2 = apply_meter_action(state, action_id)
            meters = ((st2.get("player") or {}).get("meters") or {})
            meter_ev = {"event_id": _derive_child_event_id(root_eid, "meter:thirst"), "ts": ts, "source": "system", "type": "METER_SET", "payload": {"key": "thirst", "value": int(meters.get("thirst", 0))}}
            return [root_event, meter_ev], ["💧 Набор воды."], []

        # Known-but-not-implemented actions: safe no-op, but still record action.request.
        return [root_event], [f"🧊 '{action_id}' пока не поддержано (safe no-op, без изменений сейва)."], []

    def _handle_node_proceed(
        self,
        root_event: Dict[str, Any],
        root_eid: str,
        node: Dict[str, Any],
        state: Dict[str, Any],
        ts: str,
    ) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
        sel, enc_events = self._enc.maybe_spawn_encounter(state, self._rng)
        if sel is None:
            return [root_event], ["🔎 Вы продвигаетесь вперёд… пока тихо."], []

        pool_id = self._enc.resolve_encounter_to_loot(sel)
        warn: List[str] = []
        if not pool_id:
            links = node.get("links") if isinstance(node, dict) else None
            if isinstance(links, dict) and isinstance(links.get("loot_pool_id"), str):
                pool_id = str(links.get("loot_pool_id"))
                warn.append("Encounter has no loot_pool_id; used node.links.loot_pool_id fallback")

        if not pool_id:
            return [root_event] + list(enc_events), ["⚔️ Встреча произошла, но лут не определён."], warn

        if not self._loot.pool_exists(pool_id):
            raise ValueError(f"Loot pool not found: {pool_id}")

        lr = self._loot.resolve_loot_pool(
            pool_id,
            self._rng,
            picks=3,
            scope_id=sel.node_id,
            ts=ts,
        )

        add_instances = build_add_instances(
            [
                {"instance_id": r.instance_id, "item_id": r.item_id, "qty": r.qty}
                for r in lr.instances
            ],
            origin={"kind": "LOOT", "id": lr.loot_job_id, "ts": ts},
        )

        inv_add_event = {
            "event_id": _derive_child_event_id(root_eid, f"inv_add:{lr.loot_job_id}"),
            "ts": ts,
            "source": "system",
            "type": "INVENTORY_ADD_INSTANCES",
            "payload": {"instances": add_instances, "reason": "loot"},
        }

        got = ", ".join([f"{r.item_id}×{r.qty}" for r in lr.instances])
        ui = [f"🧺 Лут: {got}"] if got else ["🧺 Лут: (пусто)"]

        return [root_event] + list(enc_events) + list(lr.events) + [inv_add_event], ui, warn

    def _handle_cross_location_move(
        self,
        root_eid: str,
        root_event: Dict[str, Any],
        action_id: str,
        state: Dict[str, Any],
        ts: str,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Cross-graph transition based on existing world graphs.

        This is *not* a new mechanic: it just formalizes entering/leaving areas.
        """
        # Determine destination by action_id.
        if action_id == "EXIT_CITY":
            to = {"region": "OUTWALLS", "location_id": "OVERWALL", "sub_id": self._world.get_graph_start("OVERWALL")}
            note = "Выход из города"
            ui = "🚪 Вы вышли из города"
        elif action_id == "ENTER_CITY":
            to = {"region": "CITY", "location_id": "CITYHUB", "sub_id": self._world.get_graph_start("CITYHUB")}
            note = "Вход в город"
            ui = "🏙️ Вы вошли в город"
        elif action_id == "ENTER_TOWER":
            to = {"region": "TOWER", "location_id": "TOWER", "sub_id": self._world.get_graph_start("TOWER")}
            note = "Вход в Башню"
            ui = "🗼 Вы вошли в Башню"
        else:
            return [root_event], [f"🧊 '{action_id}' пока не поддержано (safe no-op)."]

        loc = (((state.get("world") or {}).get("world") or {}).get("location") or {})
        frm = {
            "region": loc.get("region"),
            "location_id": loc.get("location_id"),
            "sub_id": loc.get("sub_id"),
        }

        mv_event = {
            "event_id": _derive_child_event_id(root_eid, f"world_move:{to['location_id']}:{to['sub_id']}"),
            "ts": ts,
            "source": "system",
            "type": "WORLD_MOVE",
            "payload": {"from": frm, "to": to, "note": note},
        }

        return [root_event, mv_event], [ui]

    def _handle_craft(self, root_eid: str, req: Mapping[str, Any], state: Dict[str, Any], ts: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        recipe_id = req.get("recipe_id")
        if not isinstance(recipe_id, str) or not recipe_id:
            raise ValueError("craft.recipe_id: expected non-empty string")
        times = req.get("times", 1)
        try:
            times_i = int(times)
        except Exception:
            raise ValueError("craft.times: expected integer")
        if times_i < 1:
            raise ValueError("craft.times: must be >= 1")

        root_event = {
            "event_id": root_eid,
            "ts": ts,
            "source": "player",
            "type": "craft.request",
            "payload": {"recipe_id": recipe_id, "times": times_i},
        }

        shadow = copy.deepcopy(state)
        all_events: List[Dict[str, Any]] = [root_event]
        produced_total: Dict[str, int] = {}

        for i in range(times_i):
            try:
                res = self._craft.apply_craft(recipe_id, shadow, self._rng, ts=ts, source="player")
            except CraftError as e:
                raise ValueError(str(e)) from e
            all_events.extend(list(res.events))
            for p in res.produced:
                pid = str(p.get("item_id"))
                pq = int(p.get("qty")) if isinstance(p.get("qty"), int) else 1
                produced_total[pid] = produced_total.get(pid, 0) + pq

        if produced_total:
            ui = ["🛠️ Крафт: " + ", ".join([f"{k}×{v}" for k, v in sorted(produced_total.items())])]
        else:
            ui = ["🛠️ Крафт: (ничего не произведено)"]

        return all_events, ui

    def _ensure_rng_initialized(self, state: Mapping[str, Any]) -> None:
        if self._rng.is_initialized:
            return

        snap = state.get("rng")
        if isinstance(snap, Mapping):
            self._rng.restore(snap)
            return

        ses = state.get("session")
        if isinstance(ses, dict) and isinstance(ses.get("rng_state"), Mapping):
            self._rng.restore(ses.get("rng_state"))
            return

        w = state.get("world")
        if isinstance(w, dict) and isinstance(w.get("rng_state"), Mapping):
            self._rng.restore(w.get("rng_state"))
            return

        self._rng.init(_get_save_id(state))


# Legacy helper kept for compatibility with earlier stages.

def build_turnpack_for_dispatch(dispatcher: ActionDispatcher, state: Mapping[str, Any]) -> Dict[str, Any]:
    """Build TURNPACK using recent_actions stored in state."""
    try:
        return dispatcher.build_turnpack(state)
    except Exception as e:
        # Historically this helper wrapped schema validation exceptions.
        # Keep permissive to avoid breaking callers.
        raise ValueError(str(e)) from e
