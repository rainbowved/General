# EVIDENCE_LEDGER.md (Stage C verified)
> NRWA: нет правила без anchor+цитата+impl+test.
>
> evidence_excerpt ниже — буквальные короткие цитаты из `docs/concept/CONCEPT_OPTIMIZED_v3.md` (≤25 слов).

| rule_id | canon_anchor | evidence_excerpt (<=25 words) | impl_ref | test_ref | severity | owner_phase |
|---|---|---|---|---|---|---|
| R-B24-001 | B24.LOOT.CANON.01 | "Этот раздел агрегирует и нормализует LOOT/COFFER-канон в одном месте." | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg01_missing_coffer_map.json | ERROR | P2 |
| R-B24-002 | B24.LOOT.CANON.10 | "row_id:string ... immutable в пределах pool_id." | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg08_duplicate_pool_row.json | ERROR | P2 |
| R-B24-003 | B24.LOOT.CANON.10 | "item_id:string (immutable ref)." | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg02_unknown_item_ref.json | ERROR | P2 |
| R-B24-004 | B24.LOOT.CANON.01 | "LOOT_POOL (пул строк), LOOT_ROW (строка пула), COFFER." | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg02_unknown_item_ref.json | ERROR | P2 |
| R-B21-001 | B21 | "time_sec:int ∈ {30,60,120} (строго по тиру)" | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg03_recipe_time_invalid.json | ERROR | P2 |
| R-B21-002 | B21 | "components[3]: ровно 3 компонента" | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg04_recipe_slot_count.json | ERROR | P2 |
| R-B18-001 | B18 | "B18 — QUESTS: контракты задач, статусы, награды" | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg05_quest_not_deliver.json | ERROR | P2 |
| R-B18-002 | B18 | "reward ... coffer" | tools/py/validate_pack.py | tools/fixtures/seed/pack_seed.json | ERROR | P2 |
| R-B18-003 | B18 | "filter_tags_all" | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg10_missing_quest_filter_tags.json | ERROR | P2 |
| R-B20-001 | B20 | "B20 — POI" | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg06_poi_missing_loot.json | ERROR | P2 |
| R-B22-001 | B22.LUCK.CANON.03 | "Запрещено ... превращать LUCK в новую боевую механику" | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg07_luck_forbidden_class.json | ERROR | P2 |
| R-B03-001 | B03 | "event_id и scope_id обязаны использовать run_id/session_id" | tools/py/validate_pack.py | tools/fixtures/validate_neg/neg09_tag_namespace_mismatch.json | ERROR | P2 |
| R-SCHEMA-001 | B04.FIXED_POINT | "запрещены десятичные коэффициенты ... Разрешена только явная целочисленная арифметика" | tools/py/schema_contract.py | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-002 | B24.LOOT.CANON.01 | "DB-fill ready ... без последующих миграций" | tools/py/schema_contract.py | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-003 | B18 | "QUESTS" | content/authoring/schema.sql | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-004 | B24 | "LOOT_POOL_DEF ... LOOT_ROW_DEF ... COFFER_DEF" | content/authoring/schema.sql | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-005 | B20 | "POI" | content/authoring/schema.sql | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-SCHEMA-006 | B21 | "Детерминизм крафта ... идентичный результат" | content/authoring/schema.sql | docs/schema_contracts/authoring_schema_contract.json | ERROR | P2 |
| R-CI-001 | B03.STABLE_ORDERING_GLOBAL | "Запрещено полагаться на порядок обхода dict/hashmap/сетов." | tools/py/ci.py | _logs/ci.log | ERROR | P2 |
| R-CI-002 | B03.EVENT_ID_AND_ORDERING | "Порядок применения (stable): sort_key = (t_sec, event_seq, event_id)." | tools/py/ci.py | _logs/ci.log | ERROR | P2 |
| R-CI-003 | B03.RNG_STATE_POLICY | "пересчёт результата обязан работать без rng_state" | tools/py/ci.py | _logs/schema_contract.status | ERROR | P2 |
| R-VAL-001 | B24 | "LOOT: COFFER/POOLS/LOOT_OPEN (MVP)" | tools/validate_pack.sh | _logs/validate_seed.log | ERROR | P2 |
| R-VAL-002 | B24 | "LOOT_ROW_DEF" | tools/validate_pack.sh | _logs/validate_neg.log | ERROR | P2 |
| R-VAL-003 | B03 | "один и тот же вход ... один и тот же результат" | tools/validate_pack.sh | tools/fixtures/golden/validate_expected.json | ERROR | P2 |
| R-COV-001 | B03 | "реплей был трассируем" | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-002 | B03.EVENT_ID_AND_ORDERING | "Idempotency: ... повтор — SKIP" | tools/py/coverage_gate.py | _logs/coverage_gate.log | ERROR | P2 |
| R-COV-003 | B24 | "LOOT/COFFER-канон" | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-004 | B21 | "Детерминизм крафта" | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-005 | B18 | "QUESTS" | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-006 | B20 | "POI" | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
| R-COV-007 | B22 | "LUCK (MVP)" | tools/py/coverage_report.py | docs/COVERAGE_REPORT.md | ERROR | P2 |
