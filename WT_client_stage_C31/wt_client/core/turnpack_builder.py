from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TurnpackMeta:
    schema_version: str
    content_version: str
    db_bundle_version: str
    cursor: int

    @staticmethod
    def from_state(state: Mapping[str, Any], *, schema_version: str = "0.6.6-turnpack1") -> "TurnpackMeta":
        meta = state.get("meta")
        pack_ver = ""
        if isinstance(meta, dict) and isinstance(meta.get("pack_version"), str):
            pack_ver = meta.get("pack_version")

        # Cursor in schema is an int; we map it to length of seen_event_ids.
        cursor_int = 0
        ses = state.get("session")
        if isinstance(ses, dict):
            cur = ses.get("cursor")
            if isinstance(cur, dict) and isinstance(cur.get("seen_event_ids"), list):
                cursor_int = len(cur.get("seen_event_ids"))
        prog = state.get("progress")
        if cursor_int == 0 and isinstance(prog, dict):
            cur = prog.get("cursor")
            if isinstance(cur, dict) and isinstance(cur.get("seen_event_ids"), list):
                cursor_int = len(cur.get("seen_event_ids"))

        return TurnpackMeta(
            schema_version=schema_version,
            content_version=pack_ver or "",
            db_bundle_version=pack_ver or "",
            cursor=int(cursor_int),
        )


class TurnpackBuilder:
    """Build a TURNPACK payload that matches specs/turnpack_schema.json.

    TURNPACK is a *contract*; keep it small and deterministic.

    NOTE: recent_actions here is already a flattened list of delta_events.
    """

    def build(
        self,
        state: Mapping[str, Any],
        *,
        recent_actions: List[Dict[str, Any]],
        meta: TurnpackMeta | Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if meta is None:
            tm = TurnpackMeta.from_state(state)
        elif isinstance(meta, TurnpackMeta):
            tm = meta
        elif isinstance(meta, Mapping):
            tm = TurnpackMeta(
                schema_version=str(meta.get("schema_version") or "0.6.6-turnpack1"),
                content_version=str(meta.get("content_version") or ""),
                db_bundle_version=str(meta.get("db_bundle_version") or ""),
                cursor=int(meta.get("cursor") or 0),
            )
        else:
            tm = TurnpackMeta.from_state(state)

        snapshot = self._build_snapshot_min(state)
        delta_events = self._normalize_events(recent_actions)

        return {
            "versions": {
                "schema_version": tm.schema_version,
                "content_version": tm.content_version,
                "db_bundle_version": tm.db_bundle_version,
            },
            "cursor": int(tm.cursor),
            "snapshot_min": snapshot,
            "delta_events": delta_events,
        }

    def _build_snapshot_min(self, state: Mapping[str, Any]) -> Dict[str, Any]:
        # Location
        loc = (((state.get("world") or {}).get("world") or {}).get("location") or {})
        region = loc.get("region")
        location_id = loc.get("location_id")
        sub_id = loc.get("sub_id")
        node_id = ":".join([str(x) for x in [region, location_id, sub_id] if x]) or "UNKNOWN"

        # Active mode: prefer explicit state; fallback to heuristic.
        active_mode = None
        ses = state.get("session")
        if isinstance(ses, dict) and isinstance(ses.get("active_mode"), str) and ses.get("active_mode"):
            active_mode = str(ses.get("active_mode"))
        if not active_mode:
            active_mode = "CITY" if region == "CITY" else "TRAVEL"

        # Meters
        meters = (state.get("player") or {}).get("meters") or {}
        meters_out = {
            "hp": meters.get("hp_current"),
            "hp_max": meters.get("hp_max_cached"),
            "shield": meters.get("shield_current"),
            "shield_max": meters.get("shield_max_cached"),
            "fat": meters.get("fat_current"),
            "fat_max": meters.get("fat_max_cached"),
            "hunger": meters.get("hunger"),
            "thirst": meters.get("thirst"),
        }

        # Stats
        ch = (state.get("player") or {}).get("character") or {}
        base = ch.get("attributes_base") or {}
        bonus = ch.get("attributes_perm_bonus") or {}
        stats_out: Dict[str, Any] = {}
        for k in ["STR", "DEX", "VIT", "INT", "SPD", "LCK"]:
            if k in base or k in bonus:
                stats_out[k] = (base.get(k) or 0) + (bonus.get(k) or 0)

        statuses = (state.get("player") or {}).get("statuses")
        if not isinstance(statuses, list):
            statuses = []

        return {
            "location": {
                "node_id": node_id,
                "region_id": region,
            },
            "active_mode": active_mode,
            "summary": {
                "meters": meters_out,
                "stats": stats_out,
                "statuses": [str(s) for s in statuses],
            },
        }

    def _normalize_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[dict] = []
        for ev in events or []:
            if not isinstance(ev, dict):
                continue

            event_id = ev.get("event_id")
            ts = ev.get("ts")
            typ = ev.get("type")
            payload = ev.get("payload")

            if not event_id:
                event_id = "EV_" + _sha(str(ev))[:16]
            if not ts:
                ts = "0"
            if not typ:
                typ = "UNKNOWN"
            if not isinstance(payload, dict):
                payload = {}

            out.append({"event_id": str(event_id), "ts": str(ts), "type": str(typ), "payload": payload})

        return out
