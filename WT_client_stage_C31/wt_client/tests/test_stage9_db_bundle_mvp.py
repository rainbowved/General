from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.loot_resolver import LootResolver
from wt_client.core.rng_engine import RngEngine
from wt_client.core.craft_resolver import CraftResolver
from wt_client.core.inventory_delta import count_item_qty


def _make_min_bundle(tmp: Path) -> Path:
    # Minimal bare db_bundle layout:
    #   rpg_items.sqlite
    #   json/items_loot.json
    #   content/core/rng.json
    (tmp / "json").mkdir(parents=True, exist_ok=True)
    (tmp / "content" / "core").mkdir(parents=True, exist_ok=True)

    # RNG spec
    (tmp / "content" / "core" / "rng.json").write_text(
        json.dumps({"schema_version": "rng.v1", "streams": [{"stream_id": "RNG_LOOT"}, {"stream_id": "RNG_CRAFT"}]}),
        encoding="utf-8",
    )

    # Loot pools
    (tmp / "json" / "items_loot.json").write_text(
        json.dumps(
            {
                "pool_items": [
                    {"pool_id": "POOL_TEST", "item_id": "IT_APPLE", "weight": 1, "qty_min": 1, "qty_max": 2},
                    {"pool_id": "POOL_TEST", "item_id": "IT_BONE", "weight": 1, "qty_min": 1, "qty_max": 1},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # SQLite schema (subset)
    dbp = tmp / "rpg_items.sqlite"
    con = sqlite3.connect(dbp)
    try:
        cur = con.cursor()
        cur.executescript(
            """
            CREATE TABLE items(
              item_id TEXT PRIMARY KEY,
              name_ru TEXT,
              type TEXT,
              "group" TEXT,
              rarity TEXT,
              tags_json TEXT,
              stackable INTEGER,
              stack_max INTEGER
            );
            CREATE TABLE recipes(
              recipe_id TEXT PRIMARY KEY,
              craft_kind TEXT,
              result_item_id TEXT,
              output_qty INTEGER,
              station_id TEXT,
              tier INTEGER
            );
            CREATE TABLE recipe_ingredients(
              recipe_id TEXT,
              item_id TEXT,
              qty INTEGER
            );
            """
        )

        items = [
            ("IT_APPLE", "Яблоко", "FOOD", "", "common", "[]", 1, 99),
            ("IT_BONE", "Кость", "COMPONENT", "", "common", "[]", 1, 99),
            ("IT_SOUP", "Суп", "FOOD", "", "common", "[]", 0, None),
            ("SER_HER", "Сыворотка", "SERUM", "", "legendary", "[]", 0, None),
            ("LEG_MAT", "Легенд. мат", "LEG_MATERIAL", "", "legendary", "[]", 0, None),
        ]
        cur.executemany("INSERT INTO items VALUES (?,?,?,?,?,?,?,?)", items)

        # A normal recipe
        cur.execute(
            "INSERT INTO recipes VALUES (?,?,?,?,?,?)",
            ("R_SOUP", "COOKING", "IT_SOUP", 1, "ST_COOK", 1),
        )
        cur.executemany(
            "INSERT INTO recipe_ingredients VALUES (?,?,?)",
            [("R_SOUP", "IT_APPLE", 1), ("R_SOUP", "IT_BONE", 1)],
        )

        # A GROUP_* recipe that relies on fallback selectors
        cur.execute(
            "INSERT INTO recipes VALUES (?,?,?,?,?,?)",
            ("R_GROUP", "ALCHEMY", "SER_HER", 1, "ST_ALCH", 5),
        )
        cur.executemany(
            "INSERT INTO recipe_ingredients VALUES (?,?,?)",
            [("R_GROUP", "GROUP_HERITAGE_SERUM_ANY", 1), ("R_GROUP", "GROUP_BOSS_LEG_MATERIAL_ANY", 1)],
        )

        con.commit()
    finally:
        con.close()

    return tmp


def test_bare_db_bundle_layout_and_loot_and_recipe(tmp_path: Path) -> None:
    bundle = _make_min_bundle(tmp_path / "bundle")

    loader = ContentPackLoader()
    with loader.load(str(bundle)) as pack:
        assert pack.layout.db_bundle_dir == "."

        rng_spec = pack.load_json("content/core/rng.json")
        rng = RngEngine(rng_spec)
        rng.init("seed")

        state = {"inventory": {"items": []}}

        loot = LootResolver(pack)
        res = loot.apply_loot_pool("POOL_TEST", state, rng, picks=3)
        assert res.loot_pool_id == "POOL_TEST"
        assert any(e.get("type") == "INVENTORY_ADD_INSTANCES" for e in res.events)
        assert len(state["inventory"]["items"]) == 3

        craft = CraftResolver(pack)
        # Add ingredients for normal recipe
        # (Loot already added 3 items, but we ensure at least 1 apple+1 bone)
        have = count_item_qty(state)
        if have.get("IT_APPLE", 0) < 1:
            state["inventory"]["items"].append({"instance_id": "x1", "item_id": "IT_APPLE", "qty": 1})
        if have.get("IT_BONE", 0) < 1:
            state["inventory"]["items"].append({"instance_id": "x2", "item_id": "IT_BONE", "qty": 1})

        rng2 = RngEngine(rng_spec)
        rng2.init("seed2")
        out = craft.apply_craft("R_SOUP", state, rng2)
        assert out.recipe_id == "R_SOUP"
        assert any(e.get("type") == "INVENTORY_ADD_INSTANCES" for e in out.events)

        # GROUP_* recipe: we must ensure candidate items exist in inventory.
        state["inventory"]["items"].append({"instance_id": "g1", "item_id": "SER_HER", "qty": 1})
        state["inventory"]["items"].append({"instance_id": "g2", "item_id": "LEG_MAT", "qty": 1})
        rng3 = RngEngine(rng_spec)
        rng3.init("seed3")
        out2 = craft.apply_craft("R_GROUP", state, rng3)
        assert out2.recipe_id == "R_GROUP"

