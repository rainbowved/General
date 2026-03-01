# CANON_MAP_CHECK

| Bxx | Section title (from concept) | Short meaning | Used in |
|---|---|---|---|
| B03 | PLATFORM: детерминизм, Save/Replay, Changelog, RNG, версии | Stable ordering, event identity, replay/idempotency basis. | docs/CANON_MAP.md, docs/EVIDENCE_LEDGER.md, tools/py/ci.py |
| B04 | MATH: fixed-point bp, rounding, caps, stacking | Integer-only math and chance basis points. | docs/VALIDATION_RULESET.md, tools/py/validate_pack.py |
| B14 | ITEMS: инвентарь, контейнеры, формат предметов | Item/inventory canonical semantics for runtime. | docs/CANON_MAP.md |
| B18 | (Archive quest block) | Quest objective/reward constraints. | docs/VALIDATION_RULESET.md, tools/py/validate_pack.py |
| B20 | (POI block) | POI interaction requires loot coffer linkage. | docs/VALIDATION_RULESET.md, tools/py/validate_pack.py |
| B21 | (Field ration recipes block) | Recipe strict slots/time deterministic contract. | docs/VALIDATION_RULESET.md, tools/py/validate_pack.py |
| B22 | LUCK (MVP) | Luck effects and forbidden class constraints. | docs/VALIDATION_RULESET.md, tools/py/validate_pack.py |
| B24 | LOOT: COFFER/POOLS/LOOT_OPEN (MVP) | Primary LOOT_OPEN and coffer/pool data contract. | docs/CANON_MAP.md, docs/EVIDENCE_LEDGER.md, tools/py/validate_pack.py |
