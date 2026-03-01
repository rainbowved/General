# VALIDATION_RULESET (PHASE 1 draft)

| rule_id | Description | canon_anchor | severity |
|---|---|---|---|
| R-SCHEMA-001 | No REAL/NUMERIC column types in authoring schema. | B14 | ERROR |
| R-SCHEMA-002 | No CSV/JSON content columns (`*_csv`, `*_json`). | B03 | ERROR |
| R-SCHEMA-003 | Quest filter tags stored normalized in `quest_objective_filter_tags`. | B18 | ERROR |
| R-SCHEMA-004 | Loot relations use normalized map tables (`coffer_pool_map`, `loot_pool_rows`). | B24 | ERROR |
| R-SCHEMA-005 | POI row requires explicit `loot_coffer_id` column. | B20 | ERROR |
| R-SCHEMA-006 | Ration recipe schema supports deterministic slots and integer values only. | B21 | ERROR |
