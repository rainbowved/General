# EVIDENCE_LEDGER.md (TEMPLATE)
> NRWA: нет правила без anchor+цитата+impl+test.
>
> Заполняй строки. Не удаляй колонки. Не меняй формат без patch-pack.

| rule_id | canon_anchor | evidence_excerpt (<=25 words) | impl_ref | test_ref | severity | owner_phase |
|---|---|---|---|---|---|---|
| R-B24-001 | B24 | coffer→pool mapping must exist | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg01_missing_coffer_map.json | ERROR | P2 |
| R-B24-002 | B24 | pool rows must be unique by (pool,row_id) | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg08_duplicate_pool_row.json | ERROR | P2 |
| R-B24-003 | B24 | loot row item refs must exist | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg02_unknown_item_ref.json | ERROR | P2 |
| R-B24-004 | B24 | loot row pool refs must exist | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg02_unknown_item_ref.json | ERROR | P2 |
| R-B21-001 | B21 | ration time_sec only 30/60/120 | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg03_recipe_time_invalid.json | ERROR | P2 |
| R-B21-002 | B21 | ration recipe uses exactly 3 slots | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg04_recipe_slot_count.json | ERROR | P2 |
| R-B18-001 | B18 | archive objective type must DELIVER | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg05_quest_not_deliver.json | ERROR | P2 |
| R-B18-002 | B18 | quest reward must resolve to coffer | tools/py/validate_pack.py | tools/fixtures/seed/pack_seed.json | ERROR | P2 |
| R-B18-003 | B18 | quest requires filter_tags_all mapping | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg10_missing_quest_filter_tags.json | ERROR | P2 |
| R-B20-001 | B20 | POI option requires loot_coffer_id | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg06_poi_missing_loot.json | ERROR | P2 |
| R-B22-001 | B22 | luck excludes weapon/armor/equip | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg07_luck_forbidden_class.json | ERROR | P2 |
| R-B03-001 | B03 | tag namespace must be canonical | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg09_tag_namespace_mismatch.json | ERROR | P2 |
| R-SCHEMA-001 | B14 | schema disallows REAL/NUMERIC | tools/py/schema_contract.py | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-002 | B03 | schema disallows *_csv/*_json | tools/py/schema_contract.py | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-003 | B18 | quest tags normalized join table | content/authoring/schema.sql | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-004 | B24 | loot normalized mapping tables | content/authoring/schema.sql | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-005 | B20 | poi loot_coffer_id required | content/authoring/schema.sql | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-006 | B21 | recipes use integer deterministic slots | content/authoring/schema.sql | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-CI-001 | B14 | CI logs every step status deterministically | tools/ci.sh | _logs/ci.log | ERROR | P2 |
| R-CI-002 | B14 | phase gating escalates requirements | tools/ci.sh | _logs/ci.log | ERROR | P2 |
| R-CI-003 | B14 | schema contract required at phase>=1 | tools/ci.sh | _logs/schema_contract.status | ERROR | P2 |
| R-VAL-001 | B24 | seed fixture must validate cleanly | tools/validate_pack.sh | _logs/validate_seed.log | ERROR | P2 |
| R-VAL-002 | B24 | negative fixtures must fail | tools/validate_pack.sh | _logs/validate_neg.log | ERROR | P2 |
| R-VAL-003 | B14 | seed validation report compared with golden | tools/validate_pack.sh | tools/fixtures/golden/validate_expected.json | ERROR | P2 |
| R-COV-001 | B14 | coverage report generated from ledger/gaps | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-002 | B14 | coverage gate fails if anchors missing | tools/py/coverage_gate.py | _logs/coverage_gate.log | ERROR | P2 |
| R-COV-003 | B24 | anchor B24 minimum rule coverage | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-004 | B21 | anchor B21 minimum rule coverage | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-005 | B18 | anchor B18 minimum rule coverage | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-006 | B20 | anchor B20 minimum rule coverage | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-007 | B22 | anchor B22 minimum rule coverage | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
