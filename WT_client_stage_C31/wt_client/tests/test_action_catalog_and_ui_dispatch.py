from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from wt_client.core.action_catalog import ActionCatalog
from wt_client.core.action_dispatcher import ActionDispatcher
from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.node_interactions import NodeInteractions
from wt_client.core.rng_engine import RngEngine


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_min_pack(root: Path) -> Path:
    """Create a tiny self-contained pack directory for tests."""
    # --- specs ---
    node_interactions = {
        "schema": "node_interactions_v1",
        "rules": [
            {
                "node_type": "CITY_SAFE",
                "match": {"region": "city", "tags_any": ["SAFE"]},
            },
            {
                "node_type": "DEFAULT",
                "match": {},
            },
        ],
        "node_types": {
            "CITY_SAFE": {"actions": ["PROCEED", "REST"]},
            "DEFAULT": {"actions": ["PROCEED"]},
        },
        "service_to_actions": {
            "SHOP_BASIC": ["SHOP_OPEN_BASIC"],
        },
        "priority_order": ["SHOP_OPEN_BASIC", "REST", "PROCEED"],
        "action_catalog": {
            "PROCEED": {"ru": "Продвинуться", "description_ru": "Перейти к следующему узлу."},
            "REST": {"label_ru": "Отдохнуть", "description_ru": "Короткий отдых в безопасном месте."},
            "SHOP_OPEN_BASIC": {"label_ru": "Открыть лавку", "description_ru": "Покупка/продажа (пока record-only)."},
        },
    }
    _write_json(root / "specs" / "node_interactions.json", node_interactions)

    # rng streams spec required by RngEngine init
    _write_json(
        root / "specs" / "rng_streams.json",
        {
            "streams": [
                {"stream_id": "RNG_WORLD"},
                {"stream_id": "RNG_SPAWN"},
                {"stream_id": "RNG_LOOT"},
                {"stream_id": "RNG_CRAFT"},
            ]
        },
    )

    # selectors spec required by CraftResolver init
    _write_json(root / "specs" / "ingredient_selectors.json", {"selectors": {}})

    # --- world graph ---
    graph = {
        "graph_id": "CITYHUB",
        "start_node_id": "N1",
        "nodes": [
            {
                "node_id": "N1",
                "region": "city",
                "tags": ["SAFE"],
                "ui": {"services": ["SHOP_BASIC"]},
            },
            {
                "node_id": "N2",
                "region": "city",
                "tags": [],
                "ui": {},
            },
        ],
        "edges": [
            {"from": "N1", "to": "N2", "bidirectional": True},
        ],
    }
    _write_json(root / "db_bundle" / "content" / "world" / "CITYHUB_graph.json", graph)

    # --- encounters tables required by EncounterResolver init ---
    enc = {
        "tables": [
            {
                "table_id": "T1",
                "entries": [
                    {"entry_id": "E1", "spawn_band_id": "B1", "weight": 1, "loot_pool_id": "P1"}
                ],
            }
        ]
    }
    _write_json(root / "db_bundle" / "content" / "encounters" / "encounter_tables.json", enc)

    # --- loot pools required by LootResolver init ---
    loot = {
        "pool_items": [
            {"pool_id": "P1", "item_id": "IT_TEST", "weight": 1, "qty_min": 1, "qty_max": 1}
        ]
    }
    _write_json(root / "db_bundle" / "json" / "items_loot.json", loot)

    # --- sqlite required by CraftResolver init ---
    db_path = root / "db_bundle" / "rpg_items.sqlite"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    try:
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE items (item_id TEXT PRIMARY KEY, type TEXT, `group` TEXT, tags_json TEXT, stackable INTEGER, stack_max INTEGER)"
        )
        cur.execute(
            "INSERT INTO items (item_id, type, `group`, tags_json, stackable, stack_max) VALUES (?,?,?,?,?,?)",
            ("IT_TEST", "RESOURCE", "TEST", "[]", 1, 999),
        )
        cur.execute(
            "CREATE TABLE recipes (recipe_id TEXT PRIMARY KEY, craft_kind TEXT, result_item_id TEXT, output_qty INTEGER, station_id TEXT, tier TEXT)"
        )
        cur.execute(
            "CREATE TABLE recipe_ingredients (recipe_id TEXT, item_id TEXT, qty INTEGER)"
        )
        con.commit()
    finally:
        con.close()

    return root


def test_action_catalog_lists_actions_for_demo_node(tmp_path: Path) -> None:
    pack_dir = _make_min_pack(tmp_path / "pack")
    loader = ContentPackLoader()
    with loader.load(str(pack_dir)) as pack:
        cat = ActionCatalog(pack)
        actions = cat.list_actions("CITYHUB", "N1")

    assert [a.action_id for a in actions] == ["SHOP_OPEN_BASIC", "REST", "PROCEED"]
    assert actions[0].label.startswith("Открыть")
    assert actions[0].group == "service"
    assert actions[0].record_only is True
    assert actions[-1].label  # has fallback label


def test_ui_action_request_dispatches(tmp_path: Path) -> None:
    pack_dir = _make_min_pack(tmp_path / "pack")
    loader = ContentPackLoader()
    with loader.load(str(pack_dir)) as pack:
        rng = RngEngine(pack.load_json("specs/rng_streams.json"))
        interactions = NodeInteractions(pack.load_json("specs/node_interactions.json"))
        dispatcher = ActionDispatcher(pack, interactions, rng)

        state = {
            "player": {"name": "Test", "save_id": "S1"},
            "world": {"world": {"location": {"region": "city", "location_id": "CITYHUB", "sub_id": "N1"}}},
            "session": {"active_turn": 1, "cursor": {"seen_event_ids": [], "seen_hash": ""}},
            "inventory": {"items": []},
            "progress": {},
        }

        req = {"type": "node_action", "action_id": "SHOP_OPEN_BASIC"}
        r1 = dispatcher.dispatch(req, state, cursor=None)
        assert r1.ok
        assert len(r1.events) == 1
        assert r1.events[0].get("type") == "action.request"
        assert r1.new_state["world"]["world"]["location"] == state["world"]["world"]["location"]

        # Idempotent on cursor
        r2 = dispatcher.dispatch(req, r1.new_state, cursor=r1.new_cursor)
        assert r2.ok
        assert r2.events == []
