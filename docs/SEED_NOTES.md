# SEED_NOTES (PHASE 4)

## Seed values and rationale
- `recipe.ration.time_sec = 60` to satisfy B21 allowed set {30,60,120} while keeping MVP cycle fast.
- `recipe_slots = 3` strictly matching B21 three-slot invariant.
- `coffer.start -> pool.start (ordering_key=1)` ensures deterministic B24 mapping and stable ordering baseline.
- `loot_pool_rows.weight_bp = 10000` provides deterministic single-item pick baseline for MVP smoke flows.
- `quest.archive.1.objective_type = DELIVER` and `reward_coffer_id=coffer.start` satisfy B18 canonical objective/reward path.
- `poi.camp.loot_coffer_id=coffer.start` and `open_once=1` satisfy B20 open-option constraints.
- `luck_bonus_pool.item_class = consumable` avoids forbidden B22 classes (weapon/armor/equip).

## Revert plan
1. Revert seed fixture and dist artifacts to previous commit if any rule update invalidates current seed.
2. Re-run `bash tools/validate_pack.sh --seed` and `bash tools/build_pack.sh --repro` before promoting seed changes.
3. Update golden only through `tools/update_golden.sh --accept-golden` and log rationale in `docs/2P_REVIEW_LOG.md`.
