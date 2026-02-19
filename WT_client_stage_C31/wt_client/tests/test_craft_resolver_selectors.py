from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from wt_client.core.content_pack import ContentPackLoader
from wt_client.core.craft_resolver import CraftResolver
from wt_client.core.rng_engine import RngEngine
from wt_client.core.save_store import SaveStore


_p = os.environ.get("WT_TEST_PACK")
PACK_PATH = Path(_p).expanduser() if _p else None


def _extract_demo_to(tmp_path: Path) -> Path:
    out = tmp_path / "demo_save"
    out.mkdir(parents=True, exist_ok=True)
    assert PACK_PATH is not None
    with zipfile.ZipFile(str(PACK_PATH), "r") as z:
        names = z.namelist()
        prefix = None
        for n in names:
            if n.endswith("demo/save/player.json"):
                prefix = n[: -len("demo/save/player.json")]
                break
        assert prefix is not None
        wanted = [
            "demo/save/player.json",
            "demo/save/world.json",
            "demo/save/progress.json",
            "demo/save/inventory.json",
            "demo/session/session.json",
        ]
        for rel in wanted:
            src = prefix + rel
            if src not in names:
                if rel.endswith("session.json"):
                    continue
                raise AssertionError(f"Missing demo file in pack: {src}")
            dst = out / rel.split("demo/", 1)[1]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(z.read(src))
    return out


def _add_stack(state: dict, item_id: str, qty: int, *, idx: int = 0) -> None:
    inv = state["inventory"]
    items = inv.setdefault("items", [])
    assert isinstance(items, list)
    items.append(
        {
            "instance_id": f"TEST_{item_id}_{idx}",
            "item_id": item_id,
            "qty": int(qty),
            "container": "bag",
            "slot": None,
            "equipped": False,
            "condition": 100,
        }
    )


@pytest.mark.rc_pack
def test_selector_determinism(tmp_path: Path) -> None:
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        craft = CraftResolver(pack)
        streams = pack.load_json(f"{pack.layout.specs_dir}/rng_streams.json")
        rng1 = RngEngine(streams)
        rng1.init("seed_select")

        # Prepare minimal state with candidates for GROUP_HERITAGE_SERUM_ANY
        demo_root = _extract_demo_to(tmp_path)
        state = SaveStore().load_save(demo_root)
        state["inventory"]["items"] = []
        # candidates for GROUP_BOSS_LEG_MATERIAL_ANY (so group recipe can resolve fully)
        _add_stack(state, "MAT_LUNAR_WATER", 1, idx=0)
        _add_stack(state, "MAT_ECTO_CORE", 1, idx=3)
        _add_stack(state, "STAT_HERITAGE_STR", 2, idx=1)
        _add_stack(state, "STAT_HERITAGE_DEX", 2, idx=2)

        recipe = craft.get_recipe("RC_ALCH_APOTHEOSIS_SERUM")
        resolved_a = craft.resolve_group_ingredients(recipe, state=state, rng=rng1)

        # Same seed -> same resolution
        rng2 = RngEngine(streams)
        rng2.init("seed_select")
        resolved_b = craft.resolve_group_ingredients(recipe, state=state, rng=rng2)
        assert resolved_a == resolved_b


@pytest.mark.rc_pack
@pytest.mark.parametrize(
    "recipe_id,inputs",
    [
        ("RC_ALCH_POT_ANALGESIC", [("R2", 1), ("R3", 1)]),
        ("RC_ALCH_POT_ANTISEPTIC", [("R2", 1), ("R9", 1)]),
        ("RC_ALCH_POT_COAGULANT", [("R1", 1), ("R4", 1)]),
        ("RC_ALCH_POT_DETOX_MINOR", [("CAT_VOID_MICRO", 1), ("R2", 1)]),
        ("RC_ALCH_POT_HEAL_MINOR", [("R2", 1), ("R4", 1)]),
        ("RC_ALCH_POT_HEAL_STANDARD", [("POT_HEAL_MINOR", 1), ("R4", 1)]),
        ("RC_ALCH_POT_REGEN_MINOR", [("R1", 1), ("R4", 1)]),
    ],
)
def test_craft_end_to_end_simple_recipes(tmp_path: Path, recipe_id: str, inputs: list[tuple[str, int]]) -> None:
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        craft = CraftResolver(pack)
        streams = pack.load_json(f"{pack.layout.specs_dir}/rng_streams.json")
        rng = RngEngine(streams)
        rng.init("seed_craft")

        demo_root = _extract_demo_to(tmp_path)
        state = SaveStore().load_save(demo_root)
        state["inventory"]["items"] = []
        for i, (iid, qty) in enumerate(inputs):
            _add_stack(state, iid, qty, idx=i)

        recipe = craft.get_recipe(recipe_id)
        before = {k: v for k, v in craft.resolve_group_ingredients(recipe, state=state, rng=rng)}

        res = craft.apply_craft(recipe_id, state, rng, ts="2000-01-01T00:00:00Z")
        assert res.recipe_id == recipe_id
        # All inputs consumed
        inv_ids = {it["item_id"] for it in state["inventory"]["items"]}
        for iid, _q in before.items():
            assert iid not in inv_ids
        # Output present
        assert any(it["item_id"] == recipe.result_item_id for it in state["inventory"]["items"])
        assert any(e["type"].startswith("INVENTORY_") for e in res.events)


@pytest.mark.rc_pack
def test_craft_group_recipe_apotheosis(tmp_path: Path) -> None:
    assert PACK_PATH is not None
    loader = ContentPackLoader()
    with loader.load(str(PACK_PATH)) as pack:
        craft = CraftResolver(pack)
        streams = pack.load_json(f"{pack.layout.specs_dir}/rng_streams.json")
        rng = RngEngine(streams)
        rng.init("seed_group")

        demo_root = _extract_demo_to(tmp_path)
        state = SaveStore().load_save(demo_root)
        state["inventory"]["items"] = []

        # fixed ingredients
        _add_stack(state, "ARC_CATALYST", 1, idx=1)
        _add_stack(state, "CAT_VOID_FULL", 1, idx=2)
        _add_stack(state, "MAT_BIND", 1, idx=3)

        # candidates for GROUP_BOSS_LEG_MATERIAL_ANY (qty=1)
        _add_stack(state, "MAT_LUNAR_WATER", 1, idx=10)
        _add_stack(state, "MAT_ECTO_CORE", 1, idx=11)

        # candidates for GROUP_HERITAGE_SERUM_ANY (qty=2)
        _add_stack(state, "STAT_HERITAGE_STR", 2, idx=20)
        _add_stack(state, "STAT_HERITAGE_DEX", 2, idx=21)

        res = craft.apply_craft("RC_ALCH_APOTHEOSIS_SERUM", state, rng, ts="2000-01-01T00:00:00Z")
        assert any(it["item_id"] == "APOTHEOSIS_SERUM" for it in state["inventory"]["items"])
        # group picks should have consumed exactly one of the candidate materials, and exactly one of the serum types
        remaining = {it["item_id"]: it.get("qty", 1) for it in state["inventory"]["items"]}
        # fixed ingredients removed
        assert "ARC_CATALYST" not in remaining
        assert "CAT_VOID_FULL" not in remaining
        assert "MAT_BIND" not in remaining
        # one of legendary materials remains
        assert ("MAT_LUNAR_WATER" in remaining) ^ ("MAT_ECTO_CORE" in remaining)
        # one of serum types remains with qty=2
        serum_left = []
        for k in ("STAT_HERITAGE_STR", "STAT_HERITAGE_DEX"):
            if k in remaining:
                serum_left.append((k, remaining[k]))
        assert len(serum_left) == 1
        assert serum_left[0][1] == 2
        # events include inventory add/remove
        types = [e["type"] for e in res.events]
        assert "INVENTORY_REMOVE_INSTANCES" in types
        assert "INVENTORY_ADD_INSTANCES" in types
