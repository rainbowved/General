# VALIDATION_RULESET (Stage C verified)

| rule_id | Description | canon_anchor | severity |
|---|---|---|---|
| R-SCHEMA-001 | No REAL/NUMERIC column types in authoring schema. | B04.FIXED_POINT | ERROR |
| R-SCHEMA-002 | No CSV/JSON content columns (`*_csv`, `*_json`). | B24.LOOT.CANON.01 | ERROR |
| R-SCHEMA-003 | Quest filter tags stored normalized in `quest_objective_filter_tags`. | B18 | ERROR |
| R-SCHEMA-004 | Loot relations use normalized map tables (`coffer_pool_map`, `loot_pool_rows`). | B24.LOOT.CANON.01 | ERROR |
| R-SCHEMA-005 | POI row requires explicit `loot_coffer_id` column. | B20 | ERROR |
| R-SCHEMA-006 | Ration recipe schema supports deterministic slots and integer values only. | B21 | ERROR |
| R-VAL-001 | Seed pack must satisfy deterministic LOOT_OPEN mapping invariants. | B24 | ERROR |
| R-VAL-002 | Quest objective type is fixed to archive delivery path. | B18 | ERROR |
| R-VAL-003 | LUCK bonus pool must not include forbidden equip classes. | B22.LUCK.CANON.03 | ERROR |
