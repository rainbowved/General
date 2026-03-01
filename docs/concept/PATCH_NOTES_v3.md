# Patch Notes — AUTO_OPTIMIZE_CONCEPT_FOR_CHAT v2

Дата (UTC): 2026-02-28 13:38

## Что сделано
### 1) Доменные блоки (wrappers) внутри B-разделов
Добавлены (idempotent):
- @@BEGIN:B09.SURVIVAL@@ ... @@END:B09.SURVIVAL@@ (1x)
- @@BEGIN:B10.ECONOMY@@ ... @@END:B10.ECONOMY@@ (1x)
- @@BEGIN:B12.SPELLS@@ ... @@END:B12.SPELLS@@ (1x)
- @@BEGIN:B22.LUCK@@ ... @@END:B22.LUCK@@ (1x)

### 2) Под-якоря по маркерам [CANON]/[DATA]/[QA] внутри доменных блоков
Добавлены автоматически, строго по строкам-маркерам (без угадываний границ):
- B09.SURVIVAL: 11 blocks
- B10.ECONOMY: 15 blocks
- B12.SPELLS: 186 blocks
- B22.LUCK: 15 blocks
Итого: 227 под-якорей.

Формат: @@BEGIN:<Bxx>.<DOMAIN>.<TAG>.<NN>@@ ... @@END:<...>@@
где TAG ∈ {CANON,DATA,QA}, NN — порядковый номер внутри доменного блока.

### 3) Заголовки Bxx приведены к единообразию для чтения и навигации
Внутри каждого @@BEGIN:Bxx@@ первый заголовок преобразован к:
- '## Bxx — ...'

### 4) TOC добавлен в master-md
В файле CONCEPT_OPTIMIZED_v2.md добавлен раздел '## TOC' после @@END:CHAT_RULES@@.

## Что НЕ менялось
- Игровые правила, смысл, канон.
- Численные значения (всё что было — осталось, только структура/якоря).

## GAP / ограничения
- HOME: отдельного B23 в текущем документе не обнаружено → якоря HOME.* не добавлены.
- LOOT: выделенного “одного” доменного раздела нет (LOOT/COFFER рассредоточены по нескольким Bxx) → отдельный доменный wrapper LOOT не создавался в v2 (чтобы не резать “на глаз”).


## Update: Добавлен B23 и очищен GAP (UTC: 2026-02-28 13:59)
### Что изменилось
- Добавлен новый раздел: `@@BEGIN:B23@@ ... @@END:B23@@` (HOME_HUB_PERSONAL_CORNER, V_NEXT) по кальке из backup v11.
- Из B22 удалён “встроенный” B23-контент (HOME state/ops/data/ui) и перенесён в B23.
- В B22 оставлено только то, что относится к LUCK:
  - home-scoped policy (HOME_LUCK_POLICY, LuckEffHome формулы, anti-reroll),
  - требования к coffer-паттерну для HOME outputs.
- В `GAP_v2.md` удалён пункт про отсутствие B23 (не актуален).
- В `PARAM_REGISTRY_v2.md`:
  - HOME_RESTED_DURATION_SEC и FAT_AWAKE_RATE_MULT_PCT переведены в домен HOME и used_in=B23,
  - добавлены отсутствующие параметры HOME_LUCK_MULT_PCT и RESTED_LUCK_MULT_PCT (used_in=B22).

### QA
- Смысл/геймдизайн не менялся; изменения структурные (перенос/перекомпоновка) + реестр параметров.
- Идемпотентность якорей сохранена: повторный прогон не должен дублировать блоки.


## Update: Собран LOOT-домен (B24) и очищен LOOT GAP (UTC: 2026-02-28 14:19)
### Что изменилось
- Добавлен новый раздел: `@@BEGIN:B24@@ ... @@END:B24@@` (LOOT: COFFER/POOLS/LOOT_OPEN).
- В B24 собраны (verbatim, без изменения смысла) явно помеченные LOOT-куски из:
  - B12 (LOOT_COFFERS_DB_SPEC / LOOT_OPEN контракт / ITEM_GRANT_VIA_COFFERS / COFFER_OPEN_CANON / mappings),
  - B10 (service outputs через LOOT_OPEN),
  - B18 (quest:archive_sample coffer-only; детерминизм reward coffer 18.5–18.6),
  - B19 (elite bonus loot через coffer/loot пайплайн),
  - B22 (LUCK↔COFFER) добавлены как ссылки (без дублирования).
- B12: LOOT-блоки заменены на `REF:` и сохранены как alias-анкоры для обратной совместимости (anchor IDs не пропали).
- Исправлена структурная проблема: `@@END:INDEX@@` выделен в отдельную строку (раньше был склеен с текстом).
- Исправлена структурная проблема: `LOOT.COFFERS.ITEM_GRANT_VIA_COFFERS_RULE` больше не вложен внутрь `B12.SPELLS.CANON.133` (раньше ломал вложенность).
- GAP: удалён старый LOOT-gap; оставлены только “неявные” упоминания как GAP_CANDIDATE.
- PARAM_REGISTRY: добавлена запись `COFFER_SLOT_COUNTS_BY_GRADE`.

### Что НЕ менялось
- Игровой смысл/канон/алгоритмы.
- Численные значения: перенесены как есть (где были указаны явно).



## Patch Batch — DB_FILL_GATE v1
Дата (UTC): 2026-02-28 16:05

### Цель
Закрыть S4-блокеры для старта массового DB-fill мира: registries (tags/classes), identity (region/route), единая ось тиров, расширение LOOT_ROW для квестовых тегов без доп. RNG.

### Изменения в Concept_WORKING_v3.md
- B17: добавлены 17.0.1/17.0.2/17.0.3 (Minimum Content Schema + World Identity registries + Tier Axis).
- B18: ARCHIVE_CHAPTER_DEF нормализован на tier_id (T1..T5) + добавлен DB_SPEC addendum для tag_registry/class_registry/allowlist.
- B24: LOOT_ROW_DEF расширен опциональными spawn_tags_add и force_unidentified; валидаторы дополнены проверками ссылок на tag_registry; добавлена data-note о маппинге Grade→tier_axis.

### Совместимость
- Изменения добавочные; существующий контент может продолжать использовать tier:int 1..5 на этапе authoring, но build-step обязан нормализовать в tier_id.
- Новые поля LOOT_ROW_DEF опциональны; отсутствие не меняет поведение.
