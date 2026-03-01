# Concept_13 (OPTIMIZED_MD_MASTER v3)

@@BEGIN:INDEX@@
CONCEPT_INDEX (AUTO_OPTIMIZE)

HOW TO USE
- Source of truth: this document (CANON) + DB_SPEC/PARAM_REGISTRY (DATA). If conflict: CANON wins.
- Addressing rule: analysis/patch requests MUST reference @@BEGIN:...@@ anchors.
- Patch rule: EXTRACT -> PATCH -> REINSERT. No global rewrites.

TOP-LEVEL MAP (B-blocks)
- B00 - META: рамка, клиент, канон/контент
- B01 - ONE-PAGER: MVP-контракт
- B02 - ROLES: Master vs Client
- B03 - PLATFORM: детерминизм, Save/Replay, Changelog, RNG, версии
- B04 - MATH: fixed-point bp, rounding, caps, stacking
- B05 - TIME: t_sec, TIME_ADVANCE, WORLD_TICK
- B06 - GEOMETRY: distance_m, range
- B07 - COMBAT: цикл боя, раунды, действия, завершение
- B08 - DAMAGE/DEFENSE: щит, броня, барьер, HP, травмы
- B09 - SURVIVAL: голод/жажда/усталость/среда/перевес
- B10 - ECONOMY: магазины, цены, сервисы, CU
- B11 - PROGRESSION: access_tier, перки, unlock/validation
- B12 - MAGIC: концентрация, земной ток, заклинания
- B13 - PRODUCTION: кулинария, алхимия, крафт, легендарное
- B14 - ITEMS: инвентарь, контейнеры, формат предметов
- B15 - WORLD: лор, город, башня, территории
- B16 - BESTIARY: монстры и встречи
- B17 - CONTENT: POI-PATTERNS (MVP) — CACHES / CHOKE / FIELD-SHELTER
- B18 - QUEST_TEMPLATE_IDENTIFY_BATCH (MVP) — «Архивная опись»
- B19 - ELITE_MOD_PROTOCOL_GLITCH (MVP) — "Сбой протокола"
- B20 - POI_FO_HUNTER_CAMP_ABANDONED (MVP) — “Брошенный лагерь”
- B21 - RECIPE_PACK_FIELD_RATIONS (MVP) — "Полевые пайки"
  - note: Цель: дать простой кулинарный пак для экспедиций (scarcity-first). Пайки закрывают “бытовую математику” выживания (HUNGER/THIRST → косвенная стабилизация EffectiveMaxHP) без новых механик. Используется канон COOKING: рецепт = 3 компонента, T1=30s, T2=60s, T3=120s (time_sec:int). Без RNG успеха, без новых статусов, без лечения выше EffectiveMaxHP.
- B22 - LUCK (MVP) — «Удача: экономика глубины + мягкий контроль риска»
- B23 - HOME_HUB_PERSONAL_CORNER (V_NEXT) — «Личный уголок»
- B24 - LOOT: COFFER/POOLS/LOOT_OPEN (MVP)

CRITICAL ANCHORS (stable IDs)
- @@BEGIN:B03.EVENT_ID_AND_ORDERING@@ ... @@END:B03.EVENT_ID_AND_ORDERING@@
- @@BEGIN:B03.RNG_STATE_POLICY@@ ... @@END:B03.RNG_STATE_POLICY@@
- @@BEGIN:B03.STABLE_ORDERING_GLOBAL@@ ... @@END:B03.STABLE_ORDERING_GLOBAL@@
- @@BEGIN:B04.FIXED_POINT@@ ... @@END:B04.FIXED_POINT@@
- @@BEGIN:LOOT.COFFERS.ITEM_GRANT_VIA_COFFERS_RULE@@ ... @@END:LOOT.COFFERS.ITEM_GRANT_VIA_COFFERS_RULE@@
- @@BEGIN:B24.LOOT@@ ... @@END:B24.LOOT@@
- @@BEGIN:B10.PRICE_PIPELINE_SPELLS@@ ... @@END:B10.PRICE_PIPELINE_SPELLS@@
- @@BEGIN:B12.M0@@ ... @@END:B12.M0@@
- @@BEGIN:B12.M1@@ ... @@END:B12.M1@@
- @@BEGIN:B12.SPELLS.INDEX@@ ... @@END:B12.SPELLS.INDEX@@

DATA POINTERS
- PARAM_REGISTRY.md - extracted balance/default parameters with evidence and usage anchors.
- Concept_WORKING.md - flat text export with anchors for fast retrieval/patching.
@@END:INDEX@@

@@BEGIN:CHAT_RULES@@
RULES_FOR_CHAT_EDITING (CANON)

1) Any change request must specify anchor_id (prefer @@BEGIN:...@@), goal (add/replace/delete), and constraints (CANON/DATA/UI/ASSUMPTION).
2) Allowed edit mode only: EXTRACT -> PATCH -> REINSERT. No global rewrites.
3) If target fragment has no anchor_id: first add anchor markers, then do the content edit.
4) DATA values (tables/weights/defaults/thresholds/chances) must live in DB_SPEC / PARAM_REGISTRY; in text keep only param_id + meaning + pointer.
5) Idempotency: repeated application must not duplicate blocks or anchors.
6) Canon safety: do not change gameplay meaning; only structure, addressability, and data pointers.
@@END:CHAT_RULES@@

@@BEGIN:B00@@
## B00 — META: рамка, клиент, канон/контент
ПК-КЛИЕНТ: АРХИТЕКТУРА, ФАЙЛЫ И ПРАВИЛА ДАННЫХ
Задача этого раздела — сделать так, чтобы ПК-клиент мог считать 95% “игры в цифрах”, а мастер (chatGPT) занимался только описанием мира, выбором намерений NPC/врагов и выдачей сюжетных развилок. Всё, что можно посчитать и проверить — считает и проверяет клиент.
Ключевой принцип: один и тот же вход (сейв + пак контента + seed) ⇒ один и тот же результат. Это убирает “мастер мне занизил лут” и делает отладку возможной.
[CANON] Разделение «канон vs контент»: канон — это только правила/инварианты/формулы/форматы данных. Любые конкретные числовые таблицы (пороги T1–T5, проценты сетов, списки предметов/ресурсов/рецептов, конкретные веса/шансы/коэффициенты), если они не помечены как [CANON], считаются [DATA]/примером и должны жить в контент-паках/DB_SPEC. При конфликте «числа из таблицы» vs «правило канона» — всегда побеждает канон.
@@END:B00@@
@@BEGIN:B01@@
## B01 — ONE-PAGER: MVP-контракт
ONE-PAGER (CANON)
Обещание игроку: Ты управляешь героем, который выживает в суровом мире, добывает ресурсы, исследует процедурно созданные локации, вступает в бои и выполняет контракты, возвращаясь в город для восстановления и развития. Игра строится на полной прозрачности: один и тот же сейв и пак контента всегда дают один и тот же результат.
Опорные столпы: детерминизм (случайности — вычислимы на клиенте); цикл «город → вылазка → риск → добыча → возврат»; отсутствие микроменеджмента (нет прочности/износа); магия основана на концентрации и земном токе; прогресс через перки и доступ к новым тирами.
Core loop: подготовься в городе (ремонт, торговля, алхимия) → отправься на вылазку → исследуй, сражайся, рискуй, добывай лут → вернись в город → обслужи персонажа (лечи травмы, обслужи экипировку) → планируй следующую вылазку.
Failure/Recovery: смерть или провал контракта приводит к потере временных бафов, депозита и части ресурса; постоянный прогресс (открытые перки, тира доступа) сохраняется.
MVP scope: только ключевые системы (бой, выживание, лут, крафт, сервисы города, магия концентрации, рост перков) входят в MVP. Всё, что помечено как TBD/N или V_NEXT, не влияет на вычисления и будет реализовано после MVP.

@@END:B01@@
@@BEGIN:B02@@
## B02 — ROLES: Master vs Client
Роли и границы ответственности (Master vs Client)
Мастер (chatGPT) делает:
• Нарратив: описание сцен, диалоги, последствия решений, художественные детали.
• Выбор намерений противников (intent) и “тактических целей”, если ты не хочешь полноценный AI в клиенте.
• Генерацию/уточнение локаций, если их ещё нет в паке контента (но итог — в формате данных, пригодном клиенту).
Клиент делает:
• Детерминированную симуляцию: все формулы, округления, caps/clamps, стакинг эффектов.
• Время: t_sec/таймеры/кулдауны; TIME_ADVANCE как единственный способ протекания времени вне боя; в бою — по канону COMBAT_ROUND_SEC.
• RNG: все случайности вычисляет клиент (keyed RNG/PCG32 по канону). Мастер не присылает roll/result.
• Валидации: схемы контента/сейва/инварианты; fail-fast при нарушениях.
• Генерацию идентификаторов событий (event_id/event_seq) по канону и идемпотентное применение changelog.
• Explain/Trace: заполняет explain[] и meta.trace для реплеев.
[CANON] Запрещено: мастер выполняет расчёт результата (урон/лут/шанс) или присылает “готовый исход броска”.

@@END:B02@@
@@BEGIN:B03@@
## B03 — PLATFORM: детерминизм, Save/Replay, Changelog, RNG, версии
PLATFORM (CANON): время, события, сейв, реплей, RNG, версии
Время: внутреннее время t_sec — целое число секунд; SimpleAction=1s. Боевой раунд=10s. Все длительности хранятся в секундах.
Порядок событий (CANON): все события (changelog) сортируются и применяются строго по sort_key = (t_sec, event_seq, event_id). Поле ts используется только для UI/логов и не влияет на симуляцию или merge.
@@BEGIN:B03.EVENT_ID_AND_ORDERING@@
[CANON] EVENT_ID_AND_ORDERING:
• В CHANGELOG каждое событие имеет t_sec:int, event_seq:int (монотонно в рамках SAVE; next_event_seq хранится в save и увеличивается только при записи события), event_id:string (стабильный ID).
• Порядок применения (stable): sort_key = (t_sec, event_seq, event_id).
• Генерация event_id (канон, без опциональности): event_id = HEX16(HASH_U64(save_id, event_seq, event_type)). save_id обязателен; вне сейва вместо save_id использовать run_id/session_id.
• HEX16(u64): строка из 16 hex-символов (lowercase) для uint64; форматирование, не криптография. HEX64 — legacy alias, равнозначен HEX16 (в новых текстах не использовать).
• ID-словарь (MVP): save_id — стабильный ID сейва; run_id — стабильный ID запуска (run) внутри сейва; session_id — ID клиентской сессии. Вне сейва event_id и scope_id обязаны использовать run_id/session_id как корень идентичности; запрещено использовать t_sec/actor_id/UI-артефакты как “соль”.
• Emission order (канон): если одна команда порождает несколько событий, их порядок фиксируется каноном конкретной системы; event_seq назначается последовательно в этом порядке. UI/параллелизм не влияет.
• Idempotency: клиент хранит applied_event_ids (set event_id); повтор — SKIP без побочных эффектов.
• Merge: объединять по sort_key; при коллизии event_id — SYS_CONFLICT: ALREADY_FINALIZED.
@@END:B03.EVENT_ID_AND_ORDERING@@
Сейв/реплей: сейв хранит world_seed, day_index (cache), t_sec и значения всех прогресс- и контентных полей. replay_pack экспортируется как список событий с инвариантами. Смена схемы требует увеличения schema_version и миграции.
Минимальные классы событий (MVP):
• WORLD_ADD — добавить/описать сущность мира (локации, связи, описания).
• WORLD_UPD — обновить сущность мира (патч полей, связи, описания).

EXPLAIN_PAYLOAD (канон): формат "почему так" от core к UI
• explain[] — упорядоченный список шагов ExplainStep, который core добавляет в payload события/ответа, чтобы UI мог показать причину решения и чтобы реплей был трассируем.
• ExplainStep (рекомендовано; поля опциональны, но rule_id обязателен):
- rule_id: string (обязателен; стабильный ID правила, например RULE_CAP_CLAMP).
- msg: string? (короткая человекочитаемая причина).
- meta: object? (только примитивы: int/string/bool; ключи должны быть стабильными; при сериализации для реплея ключи сортируются лексикографически).
- before/after: object? (опциональные снимки ключевых чисел до/после, например {hp, barrier, cold, heat}).
- expected/got: object? (для валидационных конфликтов).
- suggested_fix: string? (например RELOAD_SAVE/IGNORE_EVENT/REQUEST_WORLD_ADD).

RNG: используется keyed RNG. Для каждой операции определяется ключ (кортеж из world_seed, идентификаторов и счётчиков). seed = HASH_U64(key). Из seed инициализируется PRNG PCG32 со state = seed, inc = (HASH_U64(seed|“INC”) | 1), затем делается строго фиксированное число draw по спецификации операции. rng_state в сейве — только debug-cache, не влияет на результат. Для отладки: при seed = 1 первые пять uint32 равны [2598659341, 3246176901, 3870701483, 3858098844, 3922599954].
[CANON] RNG_MODEL_UNIFICATION:
@@BEGIN:B03.RNG_STATE_POLICY@@
RNG_STATE_POLICY (CANON, MVP)
• Primary truth: keyed RNG (RngKey = world_seed + rng_stream + context + scope_id + draw_index).
• Поля rng_state в save/session допустимы ТОЛЬКО как audit/debug-cache: НЕ используются как энтропия и НЕ используются для 'продолжения потока' как истины.
• Валидатор может проверять согласованность rng_state, но пересчёт результата обязан работать без rng_state.
• SYS_RNG_* события разрешены только как audit-trace и replay-agnostic (не влияют на результат).
• Primary model: keyed RNG. Каждый RNG-use определяется RngKey = (world_seed, rng_stream, context, scope_id, draw_index).
• rng_stream — namespace (RNG_COMBAT/RNG_LOOT/…), входит в key; обязательного “состояния потока” как истины нет.
• draw_index — локальный индекс draw внутри операции по фиксированному draw_spec; не обязателен как глобальное состояние.

• Любые SYS_RNG_* события допустимы только как debug/audit-trace и НЕ участвуют в пересчёте результата (replay-agnostic).
@@END:B03.RNG_STATE_POLICY@@
@@BEGIN:B03.STABLE_ORDERING_GLOBAL@@
[CANON] STABLE_ORDERING_GLOBAL (MVP)
• Запрещено полагаться на порядок обхода dict/hashmap/сетов. Любой список кандидатов/слотов/предметов, полученный из неупорядоченных структур, обязан быть отсортирован канонически-стабильно перед выбором/списанием/применением.
• Базовые stable keys: candidate_id/item_instance_id/entity_id/row_id — asc. Если сортировка по score/весу/дистанции — тайбрейк по стабильному id asc.
• Если правило использует «первый подходящий», порядок кандидатов обязан быть явно определён в этом разделе/подсистеме; иначе — fail-fast (SYS_CONFLICT: PRECONDITION_FAILED) как контентная ошибка неоднозначности.
@@END:B03.STABLE_ORDERING_GLOBAL@@
Версии: любое ломающее изменение схемы данных или правил требует увеличения schema_version и миграции сейвов.
• INVENTORY_ADD / INVENTORY_REM / EQUIP / UNEQUIP
SYS_CONFLICT payload (канон):
• event_id: string (id события-конфликта); ts / t_sec как у обычных событий.
• failed_event_id: string (id входящего события, которое не применилось).
• reason_code: enum (минимум: MISSING_ENTITY, CONTENT_REF_MISSING, PRECONDITION_FAILED, INVALID_VALUE, VERSION_MISMATCH, ALREADY_FINALIZED). Допустимо расширение списка без ломания канона (новые значения = новые валидаторы).
• expected/got: опционально (короткие значения для дебага, без гигантских дампов).
• suggested_fix: опционально (например: “RELOAD_SAVE”, “IGNORE_EVENT”, “REQUEST_WORLD_ADD”).
Важное правило: мастер не присылает “результат броска”. Он присылает только намерение или факт мира. Результат броска — детерминированно в клиенте.
Как развивать проект, чтобы контент рос (и не ломал сейвы)
• Контент добавляется новыми pack_*.json, старые ID не переименовываются.
• Баланс меняется коэффициентами в core (или в отдельном balance.json), а не массовой правкой 500 карточек.
• Любая новая механика проходит “три вопроса”: (1) клиент сможет посчитать без мастера? (2) это не добавляет 5 новых шкал? (3) это можно объяснить игроку одной фразой?
• Раз в N версий: прогон валидатора (битые ссылки), прогон “симуляционных тестов” (1000 боёв по seed’ам).
Техническое приложение: Протокол данных ПК-клиента (SAVE/SESSION/CHANGELOG/CORE/RNG)
Этот раздел добавляет в канон форматы данных и протоколы Stage 1–5. Он нужен, чтобы ПК-клиент мог хранить сейвы, применять события (идемпотентно), пересобирать кэш, считать механику по /content/core и поддерживать детерминированные реплеи.
Подробные машиночитаемые файлы и схемы см. в пакете WT_BACKBONE_BUNDLE_STAGES1-5_v0_1: docs/specs/SPEC_STAGE1…SPEC_STAGE5, content/core/.json, schemas/.schema.json, tools/*.
• schema_version/pack_version присутствуют и совместимы; save_id стабилен.
• core_manifest.json — список core-файлов + версии (schema_version/pack_version/core_version) + sha256; проверяется валидатором.
• Цель: одинаковый SAVE + одинаковые решения игрока → одинаковые результаты. Стабильность достигается разделением RNG на независимые потоки (streams) и фиксированным draw_spec для каждой операции; draw_index — локальный индекс внутри операции (НЕ глобальный счётчик потока).
• caps.json — капы и лимиты (MaxActions, ограничения вложенности контейнеров, лимит meta и др.).
• formulas.json — формулы и правила стакинга процентов: human_text + machine_spec (структурный JSON).
• aliases.json — маппинги совместимости (RU/EN/старые ID → canonical_id), чтобы не править существующий контент.
[CANON] DB_FILL_PATCH::CONTENT_ID_IMMUTABILITY (MVP)
• *_id immutable: item_id, tag_id, class_id, pool_id, row_id, shop_id, recipe_id, service_id, coffer_id, loot_table_id.
• Переименование запрещено. Совместимость — только через alias -> canonical_id (без правки уже созданных строк).
• Удаление сущности: deprecated=true. Опционально: convert_to_id для миграции инстансов (когда это явно включено мигратором).
• Запрещены нестабильные ключи (name как key). Локализация — только через name_key/desc_key (UI).
• Content compatibility: pack_version/schema_version gating; несовместимый пак — load-time fail-fast.

• rng.json — канон RNG (engine, streams, routing, режимы логирования).
E. Детерминированный RNG и реплеи (протокол).
• Цель: одинаковый SAVE + одинаковые решения игрока → одинаковые результаты. Стабильность достигается разделением RNG на независимые потоки (streams) и фиксированным draw_spec для каждой операции; draw_index — локальный индекс внутри операции (НЕ глобальный счётчик потока).
• engine: pcg32 (канон в core/rng.json).
• seed_policy: world_seed + производные run_seed/session_seed (по правилам Stage4).
• streams: RNG_COMBAT, RNG_INJURY, RNG_LOOT, RNG_CRAFT, RNG_SPAWN, RNG_VENDOR, RNG_ECONOMY (расширяемо).
• Каждый use RNG обязан указывать rng_purpose + context (например combat.hit_roll) + scope_id (combat_id/craft_job_id/loot_id). rng_state может храниться в save/world.json ТОЛЬКО как audit/debug-cache (optional, v2); session/session.json может держать rng_state как кэш.
• RngAliasMapping (legacy совместимость боя): combat_action_seq -> rng_state (optional debug).seed/draw_index; legacy roll -> rng_purpose=RNG_COMBAT; context=combat.legacy_roll; scope_id=combat_id.
• RNG-события в CHANGELOG: SYS_RNG_INIT; SYS_RNG_ADVANCE (audit mode); SYS_RNG_AUDIT_MARK (compact mode). legacy SYS_RNG_SYNC допустим для обратной совместимости, но рекомендуется миграция на тройку выше.
• tools/validate.py — проверяет core (manifest+sha256+schemas), save (schemas+инварианты), changelog (schemas+RNG инварианты), content-db (SQLite: таблицы/колонки/ссылки).
• validate.py (дополнение, MVP): проверяет day-ticks ledger’ы (для каждой подсистемы last_applied_day_index:int) и инвариант last_applied_day_index <= day_index; при нарушении — fail-fast (SYS_CONFLICT: INVALID_VALUE/VERSION_MISMATCH по policy).
• /schemas/ — Pydantic-схемы + автопроверка; validate.py использует их (CLI validate).
• tools/migrate_save.py — пошаговые миграции save между schema_version; по умолчанию НЕ in-place, всегда делает backup/.bak.
• Не тащим: полный инвентарь/всю БД/весь /content/core — только ID/версии (pack_version/core_version/schema_version), чтобы мастер мог ссылаться на канон.
[UI/EXAMPLE] schema_version examples: save.inventory.v0_2, changelog.v0_2 (пример; источник истины — /schemas в репозитории).

@@END:B03@@
@@BEGIN:B04@@
## B04 — MATH: fixed-point bp, rounding, caps, stacking
EFFECT STACK CANON (MVP)
@@BEGIN:B04.FIXED_POINT@@
[CANON: FIXED-POINT]
• Все мультипликаторы, коэффициенты и вероятности в core-расчетах хранятся как basis points (bp): 10000bp = x1.00 (100%).
• Поля вида *_Pct допустимы только как [UI]/[DATA] (целые проценты). При загрузке: bp = pct * 100.
• В каноне/данных запрещены десятичные коэффициенты (1_25/0_12, 1.25 и т.п.) и формы вида (...)/10000 как «коэффициент». Разрешена только явная целочисленная арифметика через floor_div/ceil_div.
• Вероятности: ChanceBp (0..10000). Проверка: draw = rand_int(0..9999); success = (draw < ChanceBp).
[CANON] rand_int(lo, hi): возвращает int в диапазоне [lo, hi] inclusive; нотация a..b эквивалентна a,b; mapping из PCG32: span=hi-lo+1; value=lo+(u32 % span) (bias допустим в MVP; unbiased mapping — V_NEXT). Источник u32: u32 = rng_u32(RngKey) (см. B03 RNG_STATE_POLICY); rand_int не имеет собственного состояния.
• float запрещен. Все вычисления выполняются в int (рекомендуемо int64 для промежуточных произведений).
@@END:B04.FIXED_POINT@@
[CANON: HELPERS]
• clamp_int(x, lo, hi).
• floor_div(a, b) = a // b (a>=0, b>0).
• ceil_div(a, b) = (a + b - 1) // b (a>=0, b>0).
• round_half_up_div(a, b) = (a + floor_div(b,2)) // b (a>=0, b>0).
• apply_bp(x_int, mult_bp) = apply_bp_floor(x_int, mult_bp).
• apply_bp_floor(x_int, mult_bp) = floor_div(x_int * mult_bp, 10000).
• apply_bp_ceil(x_int, mult_bp) = ceil_div(x_int * mult_bp, 10000).
• mul_bp(bp_a, bp_b) = floor_div(bp_a * bp_b, 10000) (bp x bp -> bp).
[CANON: STACKING & CAPS]
• Для эффектов с суффиксом *_MULT_PCT суммарное влияние по семейству вычисляется как sum_pct = Σ pct, затем mult_bp = clamp_int(10000 + sum_pct*100, min_bp, max_bp).
• Источник caps: CAP_BY_EFFECT_ID (приоритет) -> CAP_BY_FAMILY (дефолт). Формат cap в данных: cap_pct (int) -> max_bp = 10000 + cap_pct*100; min_bp аналогично.
• Если clamp сработал, в explain[] добавляется шаг с rule_id=RULE_CAP_CLAMP и meta{family/effect_id, sum_pct, unclamped_bp, clamped_bp, min_bp, max_bp}.
• Цепочка мультипликаторов разных семейств применяется последовательно, в фиксированном порядке, определенном соответствующей системой (например, FAT: MultArmor * MultEncumbrance * MultStatus * MultUnderwear). На каждом шаге используется apply_bp_*; запрещено перемножать 3+ bp в одном числителе без промежуточного деления (во избежание переполнений/расхождений).
[CANON: RATE MULTS]
• Для эффектов *_RATE_MULT_PCT: mult_bp = clamp_int(10000 + sum_pct*100, 5000, max_bp) (минимум 5000bp = -50%).
• Для signed-rate величин: *_RATE_MULT_PCT применяется только если rate_per_hour_base 0, если явно не указано обратное (мульты не должны ускорять восстановление «в плюс»).
[CANON: ROUNDING TABLE]
• FAMILY: ECONOMY — все цены CU: int >= 0. Цена игроку (shop_sell_unit, сервисы) -> ceil на последнем шаге; выплата игроку (shop_buy_unit) -> floor. round_half_up используется только там, где явно указано.
• FAMILY: COMBAT — Shield/Armor/Barrier reductions: floor. HP application: int. Micro-damage: см. единый канон в B08 (Damage pipeline). В B04 остаётся только правило округления и ссылка.
• FAMILY: DERIVED STATS / MOVEMENT — производные метрики только fixed-point; итоговые метры/очки -> floor.
• FAMILY: TIME / COOLDOWN — *_cost_sec: int >=1. *_delay_sec/_cooldown_sec/_left_sec: int >=0. При уменьшении длительностей (редукции) -> ceil_div на последнем шаге; затем clamp_int >=0 (или >=1 для cost).
@@END:B04@@
@@BEGIN:B05@@
## B05 — TIME: t_sec, TIME_ADVANCE, WORLD_TICK
СТАНДАРТ ВРЕМЕНИ (КАНОН)
• Внутреннее время: t_sec — целое число секунд (1 секунда = минимальный квант времени).
• SimpleAction=1s (минимальное атомарное действие/ожидание).
• сутки=86400s; 1 час=3600s; 1 минута=60s.
• Боевой раунд (Round) — шаг обработки боя и период пересчёта многих эффектов: 10s (COMBAT_ROUND_SEC=10).
• Термины «раунд/ход» — логический слой; внутреннее время и данные хранят длительности в секундах (…_sec).
WORLD TICK (канон вне боя):
• Вне боя нет скрытой симуляции “каждые 10 секунд”.
• Любое изменение времени ВНЕ БОЯ происходит только через событие TIME_ADVANCE {delta_sec}. В БОЮ время продвигается дискретно шагом COMBAT_ROUND_SEC на ROUND_END (см. B07) и считается эквивалентом внутреннего time-advance раунда.
• Инвариант: delta_sec — int >= 0. Если delta_sec < 0 → событие отклоняется (SYS_CONFLICT: INVALID_VALUE).
• Если delta_sec == 0 → no-op (t_sec и состояния не меняются).
• При TIME_ADVANCE клиент применяет деградации/реген/таймеры статусов на интервал delta_sec (целые секунды).
• Для эффектов «per 10 sec» допускается детерминированная чанковка: n=floor_div(delta_sec,10), tail=delta_sec%10; применить n раз по 10s, затем (если tail>0) 1 раз tail. Чанковка применяется только к «per 10 sec»; кулдауны/таймеры уменьшаются напрямую на delta_sec без чанков.
• Если игрок “стоит” без TIME_ADVANCE — ничего не тикает и не меняется.
Примеры: [UI] примеры свернуты; см. реплей/EXPLAIN для трассировки.
TIME_ADVANCE: какие шкалы пересчитываются и в каком порядке (канон MVP, 2-pass)
• TIME_ADVANCE_AFFECTS (минимум): HUNGER, THIRST, FAT, HYGIENE, COLD, HEAT, INFECTION, HP (реген/DoT), SPELL_TICKS (эффекты «per 10 sec»), BARRIER, TIMERS/COOLDOWNS.
• Порядок TIME_ADVANCE{delta_sec} (канон): t0=t_sec_before; t1=t0+delta_sec; t_sec=t1. day_prev=floor_div(t0,86400); day_index=floor_div(t1,86400). day_index в save допускается как кэш и MUST recompute on load. Если day_index>day_prev, клиент обязан детерминированно обработать пересечение границ суток (day-ticks) в фиксированном порядке; все RNG внутри day-ticks обязаны быть keyed к соответствующему day_index.
• DAY_TICKS_IDEMPOTENCY (MVP): каждый daily-tick обязан иметь ledger-поле last_applied_day_index:int в save (по подсистемам: economy/quest_board/…); повторная обработка одного и того же day запрещена. Обработка выполняется строго для day in (last_applied_day_index+1..day_index) последовательно; порядок day-ticks фиксирован каноном (например: ECONOMY_RESTOCK → QUEST_BOARD_REFRESH → …).
TIME_ADVANCE_INTERVAL_CANON (MVP, deterministic)
• Определения: t0 = t_sec_before, t1 = t0 + delta_sec. Событие TIME_ADVANCE логируется с t_sec=t1, но расчёт использует интервал (t0,t1).
• DayIndex: вычисляется по t1: day_index = floor_div(t1, 86400). Поле day_index в save — cache и MUST recompute on load.
• Для эффекта/статуса с time_left_sec (int>=0): active_sec = min(delta_sec, time_left_sec_before). Периодические тики считаются ТОЛЬКО на active_sec. После тиков: time_left_sec_after = max(0, time_left_sec_before - delta_sec); при 0 эффект снимается.
• Для бессрочных эффектов: active_sec = delta_sec.
• Для эффектов 'per 10 sec': n=floor_div(active_sec,10), tail=active_sec%10; применить n раз по 10s, затем (если tail>0) 1 раз tail.
• Таймеры/кулдауны (не periodic ticks): left_sec = max(0, left_sec - delta_sec) (без чанковки).
• PASS A — EFFECT_TICKS: обновить timers/durations/cooldowns и применить периодические эффекты, зависящие от статусов/заклинаний (учитывать истечения и срывы концентрации).
- таймеры/кулдауны: left_sec = max(0, left_sec - delta_sec).
- BARRIER (вне боя): RechargeCooldownSec = max(0, RechargeCooldownSec - delta_sec); если RechargeCooldownSec == 0 → BarrierCurrent = BarrierMax (мгновенно).
• PASS B — SCENE_FLAGS: пересчитать scene.light_level/temperature_band/wetness по локации/погоде/времени суток и активным эффектам; затем применить «метры среды» (COLD/HEAT/HYGIENE/INFECTION) по SURVIVAL_RATES на delta_sec; затем метаболизм (HUNGER/THIRST) и фоновую усталость (FAT) на delta_sec.
• PASS B (дополнение): при расчёте «метров среды» для COLD/HEAT учитываются модификаторы нижнего белья (см. UNDERWEAR / ENVIRONMENT MODS).
• Канон протокола: при старте сцены/боя клиент ОБЯЗАН фиксировать SCENE_FLAGS snapshot в COMBAT_START/WORLD_SCENE_START payload (для реплеев и воспроизведения).

@@END:B05@@
@@BEGIN:B06@@
## B06 — GEOMETRY: distance_m, range
GEOMETRY_DISTANCE_CANON (MVP): единая метрика расстояния (Manhattan, без float)
• Единица: 1 клетка = 1 метр. Пространство = 2D/3D grid (x,y,z) в целых метрах.
• Позиция сущности: pos = {x_m:int, y_m:int, z_m:int}. По умолчанию z_m=0.
• Ключ клетки: cell_key = “x:y:z”. В одной клетке может лежать несколько предметов.
• Канон расстояния: distance_m = |dx| + |dy| + |dz| (Manhattan). Никаких sqrt/float.
• Проверка дальности (range_m): цель в дальности если distance_m <= range_m.
• AOE по радиусу (aoe_m): задевает клетки/цели с distance_m <= aoe_m.
• MOVE: если MOVE_METERS задано (см. [DATA]), за 1 действие можно перейти в любую клетку с distance_m <= MOVE_METERS.
- [CANON, MVP-упрощение] Геометрия не моделирует препятствия/проходимость; если в данных локации нет явной схемы блоков, считаем, что клетка достижима.
• ESCAPE_DISTANCE_M и прочие проверки дистанции используют тот же distance_m (см. COMBAT_END).
[DATA]
• MOVE_METERS, ESCAPE_DISTANCE_M и любые ограничения проходимости/коллизий — в контент-паке или в константах боя (не в этом разделе).

@@END:B06@@
@@BEGIN:B07@@
## B07 — COMBAT: цикл боя, раунды, действия, завершение
STR, DEX, VIT, INT, SPD, LUCK
DERIVED_SCORES (CANON): базовые веса формул (bp)
• RunScoreBp = SPD*5000bp + DEX*3000bp + STR*2000bp (сумма весов = 10000bp).
• JumpScoreBp = STR*7000bp + DEX*3000bp.
• InitiativeScoreBp = SPD*7000bp + DEX*3000bp.
• Для сравнений (инициатива) сравниваем именно *Bp (без деления).
• Тайбрейк: DEX desc, затем LUCK desc, затем entity_id asc.
• Базовый шаг по высоте: игрок может подняться на +1 z_m (куб 1м). Маппинг JumpScoreBp→бóльшая высота — V_NEXT.

Текущее состояние боя (CANON, MVP)
HP (текущее/макс)
Барьер: BarrierCurrent, BarrierMax, RechargeCooldownSec, RechargeDelaySec
[CANON] Барьер не является «врождённой шкалой» монстров. По умолчанию у NPC/противников BarrierMax=0 и BarrierCurrent=0. Барьер может появиться только как результат явно заданного эффекта (например, SPELL_BARRIER/аффикс/спец-сущность), и должен быть видим в explain.
Статусы (если статус временный: time_left_sec — оставшееся время в секундах, int>=0)
Если цель под SPELL_MISTFORM: mistform_hp_taken_this_round:int (сброс в ROUND_START; используется для капа MISTFORM_HP_CAP_PER_ROUND).
Позиции (канон): pos = {x_m:int, y_m:int, z_m:int} для каждой сущности.
• distance_m вычисляется только по канону B06 (Manhattan).
• DistanceTo[...] допускается только как [UI]/cache; перед правилами (escape/range/target_visible) MUST recompute по pos.

Общий цикл боя по раундам (CANON)
• Шаг боя: COMBAT_ROUND_SEC = 10.
• В конце каждого раунда: t_sec = t_sec + COMBAT_ROUND_SEC; day_index = floor_div(t_sec, 86400) (cache; MUST recompute on load).

2_1 Порядок обработки каждого раунда (каждые 10 сек, строго такой)
Фаза A — UPKEEP (обслуживание раунда)
Уменьшить длительности временных статусов: time_left_sec = max(0, time_left_sec - COMBAT_ROUND_SEC) (если стало 0 — снять).
Если цель под SPELL_MISTFORM: mistform_hp_taken_this_round = 0 (сброс капа урона на раунд).
Барьер (в бою):
• [CANON] Перед апдейтом барьера вычислить RechargeDelaySec_final по B08 (BARRIER_RECHARGE_DELAY_REDUCE_PCT, caps, ceil_div).
• RechargeDelaySec_eff = max(RechargeDelaySec_final, COMBAT_ROUND_SEC) (локальная переменная; базу не мутируем).
• если RechargeCooldownSec 0 → RechargeCooldownSec = max(0, RechargeCooldownSec - COMBAT_ROUND_SEC).
• если RechargeCooldownSec == 0 → BarrierCurrent = BarrierMax (мгновенно).
• Инвариант стыковки с уроном: при событии DMG, если BarrierCurrent стал 0 из положительного значения, core обязан выставить RechargeCooldownSec = max(RechargeCooldownSec, RechargeDelaySec_eff).
Поддерживаемая магия:
• если Grounded=false → эффекты не действуют, но слоты концентрации заняты.
Обновить переменные сцены, если надо (свет/температура/мокрота и т.п. — шагом COMBAT_ROUND_SEC).

Фаза B — ACTION PHASE (ходы участников)
Определить порядок ходов по инициативе (см. DERIVED_SCORES).
Каждый участник выполняет ActionsPerRound действий при лимите времени раунда:
• actions_left = ActionsPerRound; time_budget_sec = COMBAT_ROUND_SEC.
• Инвариант: 1 <= ActionCostSec <= COMBAT_ROUND_SEC.
• Действие исполнимо только если actions_left 0 и time_budget_sec >= ActionCostSec.
• После действия: actions_left -= 1; time_budget_sec -= ActionCostSec.

Фаза C — END (конец раунда)
Проверить окончание боя (см. COMBAT_END).
Сформировать CHANGELOG записи результатов раунда.

COMBAT_END (канон): как бой заканчивается (формально, без “мастер решает на глаз”)
• Бой проверяется на завершение в конце каждого раунда (ROUND_END) и также сразу после событий, которые меняют состав/состояние участников (DMG/STATUS_APPLY/ACT:RETREAT/WORLD_MOVE).
• Участник считается “выведен из боя”, если HP <= 0 (incapacitated). В этот же момент он перестает совершать действия.
• Победа (VICTORY): у стороны игрока нет активных hostile-участников (все incapacitated или FLED).
• Поражение (DEFEAT): игрок incapacitated (HP <= 0).

ESCAPE_DISTANCE_CANON (MVP): порог побега через ACT:RETREAT
• Константа: ESCAPE_DISTANCE_M:int = 30 (MVP).
• Если scene.escape_blocked=false и игрок выполняет ACT:RETREAT: после применения перемещения пересчитать distance_m до каждого hostile. Если для каждого hostile distance_m ESCAPE_DISTANCE_M, core обязан выставить player.FLED=true.
• В COMBAT_END: бой считается завершённым, если player.FLED=true (escape).

ESCAPE_BLOCKED_CANON (MVP): анти-абуз побега
• scene.escape_blocked:boolean (по умолчанию false). Источник: client (location tags/encounter flags: узкий проход, удержание босса, ловушка).
• Если escape_blocked=true, ACT:RETREAT не может завершить бой (не выставляет FLED); действие только увеличивает distance_m (через изменение pos).
• Побег возможен только через WORLD_MOVE (если доступно) или через исход боя (VICTORY/DEFEAT).
• При попытке ACT:RETREAT при escape_blocked=true core обязан вернуть explain шаг RULE_ESCAPE_BLOCKED.

ACTION_AVAILABILITY_BY_LIGHT_LEVEL (MVP): доступность действий по освещению
• Канон видимости цели: target_visible = (scene.light_level != DARK) OR (distance_m <= 1) OR (actor имеет активный Night Vision).
• DARK: ranged attacks = запрещены; targeted spells (требующие visible target) = запрещены; stealth actions = разрешены; melee/взаимодействия с целью разрешены только если target_visible=true.
• DIM: все атаки/targeted spells разрешены (при target_visible=true); stealth разрешён.
• NORMAL: все атаки/targeted spells разрешены; stealth разрешён.
• BRIGHT: все атаки/targeted spells разрешены; Night Vision при активном использовании может давать BLIND (см. BLIND).
@@END:B07@@
@@BEGIN:B08@@
## B08 — DAMAGE/DEFENSE: щит, броня, барьер, HP, травмы
BARRIER MODIFIERS (CANON)
DAMAGE_TYPING_CANON (MVP): единый damage_amount, без резистов по “режущий/колющий/дробящий”
• В бою существует один числовой урон damage_amount:int (после попадания/защиты).
• DamageProfile/HitZone используются только для правил травм/зон/FX; они не вводят отдельные типы урона и не требуют матрицы резистов.
• Прямой “боевой магии” (нанести урон заклинанием) в MVP нет: магия влияет через бафы/дебафы/контроль/окружение.
[CANON] Модификаторы барьера, влияющие на RechargeDelaySec, агрегируются по effect_id как signed-процент (плюс = быстрее, минус = медленнее). Запрещены float; расчёт в bp.
sum_pct = Σ pct по effect_id=BARRIER_RECHARGE_DELAY_REDUCE_PCT (pct:int, может быть <0). factor_bp_unclamped = 10000 - sum_pct*100. factor_bp = clamp_int(factor_bp_unclamped, min_bp, max_bp) (caps: CAP_BY_EFFECT_ID→CAP_BY_FAMILY). RechargeDelaySec_final = ceil_div(RechargeDelaySec_base * factor_bp, 10000).
[CANON] Caps/Explain: если factor_bp был ограничен clamp’ом, добавить ExplainStep{rule_id=RULE_CAP_CLAMP, meta{effect_id, sum_pct, unclamped_bp=factor_bp_unclamped, clamped_bp=factor_bp, min_bp, max_bp}} (формат meta как в B04).
Система выживания строится на барьерных артефактах.
Пояснение к параметрам брони ShieldMax и ShieldRegen (они относятся к SPELL_BARRIER/барьеру): ShieldMax увеличивает ёмкость барьера (BarrierMax) на указанный процент. ShieldRegen влияет на задержку восстановления барьера: при положительном значении уменьшает RechargeDelaySec, при отрицательном — увеличивает (signed). Примечание: названия ShieldMax/ShieldRegen — исторические. Это модификаторы Barrier, а не отдельная шкала “Shield”. [CANON] Маппинг UI→effects: ShieldMax(UI pct:int) → effect_id=BARRIER_MAX_MULT_PCT (pct=ShieldMax); ShieldRegen(UI pct:int) → effect_id=BARRIER_RECHARGE_DELAY_REDUCE_PCT (pct=ShieldRegen). Caps/Explain — по общему канону CAP_BY_EFFECT_ID/CAP_BY_FAMILY и RULE_CAP_CLAMP.
[DATA] BALANCE TABLES (T1–T5): броня/щит/редукции/штрафы — вынесены в content/DB_SPEC.
В каноне остаются только поля/форматы и алгоритмы применения (B04/B08): порядок редукций, caps/clamps, rounding и wiring ShieldMax/ShieldRegen → Barrier effects.
BALANCE TABLES (T1–T5) вынесены: конкретные проценты/штрафы/иммунитеты — только в данных; при конфликте числа vs канон — побеждает канон.
[CANON] ArmorPen (бронепробитие) — параметр источника урона (оружия/атаки), влияющий только на этап «броня» в B08.
• ArmorPct_def:int — броня цели в процентных пунктах (0..100), но в MVP применяется с капом ARMOR_PCT_CAP_MVP (см. caps).
• ArmorPenPct_atk:int — бронепробитие источника урона в процентных пунктах (0..ARMOR_PEN_PCT_CAP_MVP).
• EffectiveArmorPct = clamp_int(ArmorPct_def - ArmorPenPct_atk, 0, ARMOR_PCT_CAP_MVP).
• factor_bp = 10000 - EffectiveArmorPct*100 (т.е. 1 pct = 100bp).
• dmg_after_armor = apply_bp_floor(dmg_after_shield, factor_bp). (округление вниз по канону COMBAT: Shield/Armor reductions = floor)
[CANON] Caps: ARMOR_PCT_CAP_MVP = 70; ARMOR_PEN_PCT_CAP_MVP = 70. (Пробитие выше капа бессмысленно и должно clamp’иться валидатором.)
[DATA] Wiring: ArmorPenPct_atk берётся из данных источника урона:
• ORDINARY_ATTACK / RANGED_ATTACK: из weapon/attack-профиля (content/DB_SPEC).
• APPLY_DAMAGE_ITEM: из item-def (если предмет наносит урон как «оружие»).
• HOSTILE_SPELL: по умолчанию ArmorPenPct_atk=0 (в MVP нет прямого урона заклинаниями; если появится исключение — оно должно быть явно помечено в данных как weapon_like).
Расчёт урона (клиент): щит (если сработал) → броня (процентная порезка, с капом) → барьер (поглощение) → HP.
Барьер может полностью поглотить удар: HPDamage = 0.
Правило микро-урона применяется только когда Барьер уже исчерпан (BarrierCurrent = 0 до удара): если после щита/брони получилось 0 при ненулевом исходном уроне, считать HPDamage = 1. Если цель под «Дымка», микро-урон не отменяется, но итоговый HPDamage всё равно ограничивается MISTFORM_HP_CAP_PER_ROUND за раунд.
OFFENSIVE_ACTION_CANON (MVP): что считается hostile действием
offensive_action (канон enum): ORDINARY_ATTACK | RANGED_ATTACK | HOSTILE_SPELL | APPLY_DAMAGE_ITEM.
[DATA] Для HOSTILE_SPELL: в данных заклинания/эффекта должен быть флаг offensive:boolean (или tag OFFENSIVE) — только он определяет, что применение считается offensive_action.
Канон классификации (минимум кода, без системы отношений): offensive_action=true если действие приводит к любому из: (a) наносит HPDamage>0 хотя бы одной цели; (b) пытается применить предмет/эффект с семейством APPLY_DAMAGE_ITEM; (c) применяет hostile-эффект (контроль/дебафф), помеченный в данных как offensive=true. В MVP предполагается, что боевые цели — только hostile участники encounter; таргетинг FRIENDLY/NEUTRAL в бою запрещён валидатором (если появится в V_NEXT — AoE, задевающий FRIENDLY, тоже offensive_action).
Канон последствий: любая offensive_action немедленно срывает SPELL_MISTFORM (срыв концентрации).
Канон концентрации: offensive_action НЕ обязана срывать другие поддерживаемые заклинания, если в описании конкретного заклинания не указано иное (минимум кода, детерминизм).
Травмы/негативные статусы от удара проверяются только если Барьера нет (BarrierStart = 0) или удар пробил Барьер (BarrierBrokenThisHit = true).
Бижутерия играет роль носителя зачарования. Типы бижутерии: Серьга, кольцо, подвеска. У каждого типа по пять тиров.
UNDERWEAR / ENCHANT (EXCEPTION, MVP)
• Базовое правило сохраняется: основным носителем зачарований остаётся бижутерия.
• Исключение (allowlist, 1 аффикс): нижнее бельё может иметь ровно один специальный аффикс барьера «Aegis Underwear» (шутливый лор-дисплей, механика серьёзная).
• Эффект аффикса: BARRIER_MAX_MULT_PCT = +10 (то есть +1000bp к множителю BarrierMax).
• Стакинг/кап: эффект стакается по общему правилу *_MULT_PCT и учитывается в CAP_BY_EFFECT_ID для BARRIER_MAX_MULT_PCT.
• Ограничение: бельё НЕ становится полноценным enchant-slot; любые другие зачарования на белье запрещены валидатором (кроме этого allowlist-аффикса).

@@END:B08@@
@@BEGIN:B09@@
## B09 — SURVIVAL: голод/жажда/усталость/среда/перевес
@@BEGIN:B09.SURVIVAL@@
• Все расчёты: бой, урон, статусы, барьер, перемещение, усталость, голод/жажда, нагруженность.
• Все случайности (детерминированный RNG): проки щита, травм, лута, редких ресурсов.
• Инвентарь/крафт/алхимия/кулинария/ремесло: проверка условий, списание компонентов, выдача результата (через LOOT_OPEN(output_coffer_id), даже если выход детерминирован).
• Валидацию данных: “невозможные” рецепты, битые ссылки, несуществующие ID — ловятся до запуска игры.

@@BEGIN:B09.SURVIVAL.CANON.01@@
[CANON] Общие шкалы и тиры (T1–T5)
• Стадийные шкалы (meters) задаются как meter_pct:int в диапазоне 0..100, где 0 = OK, 100 = CRITICAL.
• Тир по meter_pct (унификация): T1 ≥20, T2 ≥40, T3 ≥60, T4 ≥80, T5 ≥95. T0 = нет статуса.
• Вне боя изменение meters происходит только внутри TIME_ADVANCE{delta_sec} (см. B05).
• В бою изменения/тик-эффекты считаются на ROUND_END шагом COMBAT_ROUND_SEC=10 (см. B07).

@@END:B09.SURVIVAL.CANON.01@@
@@BEGIN:B09.SURVIVAL.CANON.02@@
[CANON] EffectiveMaxHP — потолок лечения
• EffectiveMaxHP — текущий “потолок лечения”. Любое лечение/реген не может поднять HP выше EffectiveMaxHP (см. B08/B13).
• Порезки применяются к MaxHP, а не к HP:
cut_total_bp = clamp_int(Σ cut_bp(status_i), 0, 8000) (макс. -80%)
EffectiveMaxHP = max(apply_bp_floor(MaxHP, 10000 - cut_total_bp), apply_bp_floor(MaxHP, 2000)) (мин. 20% MaxHP)
• Дефолт-лесенка cut_bp для стадийных статусов, влияющих на организм:
T1: 0bp; T2: 500bp; T3: 1000bp; T4: 2000bp; T5: 3000bp
• Исключения фиксируются отдельно: THIRST/HUNGER используют свои значения (см. ниже).

@@END:B09.SURVIVAL.CANON.02@@
@@BEGIN:B09.SURVIVAL.CANON.03@@
[CANON] THIRST (жажда) — порезка и DoT
• Порезка EffectiveMaxHP от THIRST:
T1: 0bp; T2: 500bp; T3: 1000bp; T4: 2000bp; T5: 3000bp
• DoT THIRST на T5: THIRST_T5_HP_DOT_PER_HOUR:int (HP за 3600s) — [DATA] (balance).
Вне боя: TIME_ADVANCE, PASS A, периодический эффект без float:
acc = thirst_dot_rem + THIRST_T5_HP_DOT_PER_HOUR * delta_sec
hp_dmg = floor_div(acc, 3600); thirst_dot_rem = acc % 3600
HP = HP - hp_dmg (дальше общие правила B08).
В бою: то же на ROUND_END, где delta_sec = COMBAT_ROUND_SEC.

@@END:B09.SURVIVAL.CANON.03@@
@@BEGIN:B09.SURVIVAL.CANON.04@@
[CANON] FAT (усталость) — состояние и базовая формула
• FATCurrent:int ≥ 0; FATMax:int ≥ 60.
• Для детерминированной дробной математики допускается хранение fat_milli:int и fat_milli_rem:int (milli-FAT).
• FATMax = max(60, 100 + 5*(VIT-10) + 3*(SPD-10)).

@@END:B09.SURVIVAL.CANON.04@@
@@BEGIN:B09.SURVIVAL.CANON.05@@
[CANON] Фоновая усталость (бодрствование)
• BASE_AWAKE_GAIN_PER_HOUR:int (FAT за 3600s) — [DATA] (balance).
• Реализация без float (milli-FAT): base_gain_per_hour_milli = 7000.
• На TIME_ADVANCE для интервала бодрствования delta_awake_sec:
num = base_gain_per_hour_milli * delta_awake_sec
gain_milli = floor_div(num, 3600); rem_add = num % 3600
fat_milli_rem = fat_milli_rem + rem_add; перенос +1 milli при fat_milli_rem ≥ 3600; fat_milli_rem %= 3600
• Мультипликаторы фоновой усталости (bp) применяются последовательно (см. B04):
gain_milli = apply_bp_floor(gain_milli, MultArmor)
gain_milli = apply_bp_floor(gain_milli, MultEncumbrance)
gain_milli = apply_bp_floor(gain_milli, MultStatus)
gain_milli = apply_bp_floor(gain_milli, MultCombat)
gain_milli = apply_bp_floor(gain_milli, MultUnderwear)
Итог: fat_milli += gain_milli; FATCurrent = floor_div(fat_milli, 1000).

@@END:B09.SURVIVAL.CANON.05@@
@@BEGIN:B09.SURVIVAL.CANON.06@@
[CANON] Действийная усталость (стоимость действий)
• Стоимости задаются как FATAction10s_milli:int (milli-FAT за 10 секунд активной нагрузки).
• Для действия с ActionCostSec (1..10, см. B07):
gain_milli = floor_div(FATAction10s_milli * ActionCostSec, 10)
• Мультипликаторы для действийной усталости: только MultArmor × MultEncumbrance × MultUnderwear (без MultStatus).
• [DATA] Таблица FATAction10s_milli по ActionType живёт в DB_SPEC/balance.

@@END:B09.SURVIVAL.CANON.06@@
@@BEGIN:B09.SURVIVAL.CANON.07@@
[CANON] Сон и отдых — восстановление FAT
• Сон считается блоками по 3600s. [DATA] SLEEP_RECOVERY_PER_HOUR_BY_BLOCK задаётся в DB_SPEC/balance; применяется через apply_bp_floor (в milli-FAT).
блоки 1–2: 20; блоки 3–4: 10; блоки 5+: 3.
• QualityMult_bp ∈ {7000, 10000, 11000}; применяется через apply_bp_floor к recovery (в milli-FAT).
• Отдых без сна (REST): REST_RECOVERY_PER_HOUR:int — [DATA]; дополнительные условия (например rest_has_food/rest_has_water) — как булевы флаги сцены (ASSUMPTION ниже).
ASSUMPTION: rest_has_food/rest_has_water задаются валидатором сцены как bool.

@@END:B09.SURVIVAL.CANON.07@@
@@BEGIN:B09.SURVIVAL.CANON.08@@
[CANON] Тиры усталости и эффекты (FAT tiers)
• fat_ratio_bp = floor_div(FATCurrent * 10000, FATMax). Пороги: 2000/4000/6000/8000/9500.
• Эффекты:
T1: EffectiveSPD = apply_bp_floor(EffectiveSPD, 9500)
T2: EffectiveSPD = apply_bp_floor(EffectiveSPD, 9000)
T3: EffectiveSPD = apply_bp_floor(EffectiveSPD, 8000); в бою: ActionsPerRound = max(1, ActionsPerRound - 1)
T4: EffectiveSPD = apply_bp_floor(EffectiveSPD, 7000); в бою: ActionsPerRound = 1
T5 (коллапс):
вне боя: без RNG — если fat_ratio_bp ≥ 9500 и персонаж не спит, то в TIME_ADVANCE интервал бодрствования ограничен delta_awake_sec = min(delta_sec, 20); остаток интерпретируется как сон/отдых по правилам выше.
в бою: ActionsPerRound = 1; offensive_action (ATTACK_*) запрещены, пока fat_ratio_bp ≥ 9500.
• Выход из “края”: для выхода из T4+ нужно fat_ratio_bp < 8000.

@@END:B09.SURVIVAL.CANON.08@@
@@BEGIN:B09.SURVIVAL.CANON.09@@
[CANON] MultTotal для фоновой усталости (bp)
• MultTotal = MultArmor × MultEncumbrance × MultStatus × MultCombat × MultUnderwear.
• MultArmor (пример значений — [DATA] в balance): ткань 10000bp, кожа 10500bp, кольчуга 11000bp, железо тяжёлое 12500bp.
• MultEncumbrance определяется тиром перевеса (см. ниже).
• MultStatus: включает только “сильные стадии” (например, THIRST T3+, HUNGER T3+, COLD/HEAT T3+, BLOOD_LOSS T2+ и т.п.).
CAP: MultStatus_total_bp MUST be clamped через CAP_BY_FAMILY (см. B11) для семейства FAT_STATUS_MULT.
• MultCombat: COMBAT=true → 11000bp; иначе 10000bp.
• MultUnderwear: по умолчанию 10000bp; если ArmorType == IRON_HEAVY и underwear.heavy_armor_comfort=true → 9500bp.
ASSUMPTION: underwear.heavy_armor_comfort:boolean; валидатор: true разрешён только для категории UNDERWEAR.

@@END:B09.SURVIVAL.CANON.09@@
@@BEGIN:B09.SURVIVAL.CANON.10@@
[CANON] Перевес (Encumbrance) — алгоритм
• CarriedWeight_g считается по схеме предметов/контейнеров (см. B14). Единицы веса и поля weight_g_per_unit/stack_count фиксируются там.
• CarryLimit_g = max(20000, 35000 + 2000*(STR-10) + 1000*(VIT-10) + GearBonus_g).
• AbsoluteMax_g = apply_bp_floor(CarryLimit_g, 15000). Если CarriedWeight_g AbsoluteMax_g — MOVE/TAKE запрещены (только DROP/TRANSFER).
• r_bp = floor_div(CarriedWeight_g * 10000, CarryLimit_g). Тиры:
None: r_bp ≤ 9000
T1: 9000 < r_bp ≤ 10000
T2: 10000 < r_bp ≤ 11500
T3: 11500 < r_bp ≤ 13000
T4: 13000 < r_bp ≤ 15000
T5: r_bp 15000 или CarriedWeight_g AbsoluteMax_g
• Эффекты:
EffectiveSPD = apply_bp_floor(EffectiveSPD, EncumbranceSpeedMult_bp[tier])
MultEncumbrance = FATGainMult_bp[tier]

@@END:B09.SURVIVAL.CANON.10@@
@@BEGIN:B09.SURVIVAL.DATA.01@@
[DATA] Где живут таблицы/дефолты
• Дефолты весов по категориям, GearBonus_g, конкретные таблицы MultArmor/MultStatus/EncumbranceSpeedMult_bp/FATGainMult_bp — в DB_SPEC/balance. В каноне остаётся только формат и алгоритмы.

@@END:B09.SURVIVAL.DATA.01@@@@END:B09.SURVIVAL@@
@@END:B09@@
@@BEGIN:B10@@
## B10 — ECONOMY: магазины, цены, сервисы, CU
@@BEGIN:B10.ECONOMY@@
S3.2–S3.4 SHOP/EXCHANGE: цены, спред, склад, ресток (CANON, минимум)
@@BEGIN:B10.ECONOMY.DATA.01@@
[DATA] ECONOMY_DEFAULTS (DB_SPEC/balance; значения по умолчанию, не канон алгоритмов)
• V_MARKET_BP:int (см. PARAM_REGISTRY / DB_SPEC); V_ITEM_BP:int (см. PARAM_REGISTRY / DB_SPEC).
• K_SCARCITY_BP:int (см. PARAM_REGISTRY / DB_SPEC); S_MIN_BP:int (см. PARAM_REGISTRY / DB_SPEC); S_MAX_BP:int (см. PARAM_REGISTRY / DB_SPEC).
• OVERSTOCK_CAP:int (см. PARAM_REGISTRY / DB_SPEC).
• SHOP_EXCHANGE defaults: BUY_MULT_EXCH_BP:int (см. PARAM_REGISTRY / DB_SPEC); SELL_MULT_EXCH_BP:int (см. PARAM_REGISTRY / DB_SPEC); FEE_EXCH_BP:int (см. PARAM_REGISTRY / DB_SPEC).
• shop_kind default multipliers (если price_policy{} пуст): SHOP_EXCHANGE/SHOP_SMITH/SHOP_ALCHEMY/SHOP_BASIC — значения в DB_SPEC/balance (были в тексте; перенесены в данные).
• S3.2 Цена (целые CU): P_base priority = SHOP.inventory.price_base_cu (alias price_base) -> ItemDefinition.price_base_cu (alias price_base) -> not tradable; M_day_bp = 10000 + rand_int(-V_MARKET_BP, +V_MARKET_BP); RNG_ECONOMY keyed-RNG: (world_seed, rng_stream=RNG_ECONOMY, context="market.day_mult", scope_id=day_index, draw_index=0). P_ref = round_half_up_div(P_base * M_day_bp, 10000). VarBuy_bp/VarSell_bp = 10000 + rand_int(-V_ITEM_BP, +V_ITEM_BP); RNG_VENDOR keyed-RNG: (world_seed, rng_stream=RNG_VENDOR, context="shop.price_var.buy"/"shop.price_var.sell", scope_id=(day_index, shop_id, item_id), draw_index=0).
@@END:B10.ECONOMY.DATA.01@@
@@BEGIN:B10.ECONOMY.CANON.01@@
[CANON] DB_FILL_PATCH::ITEM_ECON_FLAGS (MVP)
• ItemDefinition.econ_flags: tradable, shop_sellable, exchange_eligible, quest_bound, no_sell (или экв.).
• Приоритеты effective.flags: no_sell > quest_bound > (shop_sellable/exchange_eligible) > tradable.
• price_base_cu:int>=0 — базовая цена (CU). Валидно только если effective.tradable=true. Legacy alias (без миграции): price_base == price_base_cu.
• Legacy compatibility (без миграции): если econ_flags отсутствуют, effective.tradable = (price_base_cu задан), остальные флаги вычисляются data-policy подсистем (шоп/обмен/квест). Build-step даёт WARN; load не падает.
• Операции SHOP_*/EXCHANGE обязаны reject: no_sell=true или quest_bound=true (не UI-правило, а валидация).
• Anti-loop валидатор (build-step): граф buy/sell/exchange не должен содержать положительных циклов при фиксированных спред/комиссиях.

• Формулы (bp, без float): buy_mult_bp=BUY_MULT_BP; sell_mult_bp=SELL_MULT_BP. shop_buy_unit = max(0, apply_bp_floor(apply_bp_floor(P_ref, buy_mult_bp), VarBuy_bp)). shop_sell_unit = max(1, apply_bp_ceil(apply_bp_floor(apply_bp_floor(P_ref, sell_mult_bp), VarSell_bp), Scarcity_bp)). Финальная защёлка (канон): если shop_sell_unit < shop_buy_unit + 1 ⇒ shop_sell_unit = shop_buy_unit + 1. (SHOP_SPREAD_ROUNDING_GUARD).

@@BEGIN:B10.PRICE_PIPELINE_SPELLS@@
@@END:B10.ECONOMY.CANON.01@@
@@BEGIN:B10.ECONOMY.CANON.02@@
[CANON] SPELL_FAIR_TRADE_PRICE_PIPELINE (MVP)
- Applies only if SPELL_FAIR_TRADE is active on the buyer actor and grounded=true.
- Inputs: buy_mult_bp, sell_mult_bp (from shop_kind defaults or price_policy), spread_reduction_bp from spell.
- Modify multipliers BEFORE VarBuy/VarSell RNG and BEFORE Scarcity and BEFORE SHOP_SPREAD_ROUNDING_GUARD:
  - signed delta_buy = buy_mult_bp - 10000; buy_mult_bp = 10000 + floor_div(delta_buy * (10000 - spread_reduction_bp), 10000).
  - signed delta_sell = sell_mult_bp - 10000; sell_mult_bp = 10000 + floor_div(delta_sell * (10000 - spread_reduction_bp), 10000).
- Then continue canonical price calc (VarBuy/VarSell, Scarcity, rounding guard).
- This spell does not bypass no_sell/quest_bound flags and does not change P_ref or RNG streams.
@@END:B10.PRICE_PIPELINE_SPELLS@@
• Scarcity влияет только на shop_sell_unit (в bp): K_SCARCITY_BP, S_MIN_BP, S_MAX_BP — [DATA]. stock_target = max(1, round_half_up_div(stock_min + stock_max, 2)). Если stock <= stock_target: diff_bp = floor_div((stock_target - stock) * 10000, stock_target); Scarcity_bp = clamp_int(10000 + apply_bp_floor(diff_bp, K_SCARCITY_BP), S_MIN_BP, S_MAX_BP). Иначе: diff_bp = floor_div((stock - stock_target) * 10000, stock_target); Scarcity_bp = clamp_int(10000 - apply_bp_floor(diff_bp, K_SCARCITY_BP), S_MIN_BP, S_MAX_BP).
• S3.3 Операции: OVERSTOCK_CAP — [DATA]; stock_limit = stock_max*OVERSTOCK_CAP. SHOP_SELL: accepted=min(qty, max(0, stock_limit-stock_cur)); inventory-=accepted; CU+=payout; stock+=accepted. SHOP_BUY: require stock>=qty & CU>=cost; CU-=cost; inventory+=qty; stock-=qty.
• Ресток (EconomyDailyTick): если day_index>last_restock_day ⇒ stock[item_id]=rand_int(stock_min,stock_max) по RNG_VENDOR keyed-RNG: (world_seed, rng_stream=RNG_VENDOR, context="shop.restock", scope_id=(day_index, shop_id, item_id), draw_index=0). Save: shop_state[shop_id]={last_restock_day:int, stock:map[item_id->int]}; invariant stock>=0.
• S3.4 SHOP_EXCHANGE: BUY_MULT_EXCH_BP/SELL_MULT_EXCH_BP/FEE_EXCH_BP — [DATA]; финальная защёлка: cost_unit >= payout_unit + 1. Опционально rate_by_tag: по tag_priority[]; P_ref_exch = round_half_up_div(P_ref * RateTagMult_bp, 10000) перед спредом. fee_bp = FEE_EXCH_BP; cost_unit = ceil_div(shop_sell_unit_exch * (10000 + fee_bp), 10000); payout_unit = floor_div(shop_buy_unit_exch * (10000 - fee_bp), 10000).
• Дефолты множителей по shop_kind (если price_policy{} пуст) — [DATA] в DB_SPEC/balance (не держать числа в [CANON]).
• TRACE_FIELDS_FOR_REPLAY (MVP): meta.trace {operation_id, inputs_hash, outputs_hash, explain_hash}; *_hash=HASH_U64(...); explain_hash=HASH_U64(rule_id|delta|after по explain[]). Для SHOP_BUY/SHOP_SELL/REPAIR добавить fee_exch и unit_price_before_fee/unit_price_after_fee (payload). rule_id для explain/trace (канон, минимум): RULE_MARKET_DAY, RULE_SHOP_MULTS, RULE_SPREAD_LATCH.
S3.8 Схемы данных Content/Save, валидации, CHANGELOG (кратко)
Почему нет бесконечной печати денег: (1) спред-защёлка; (2) M_day общий; (3) Var малы и детерминированы; (4) Scarcity не влияет на shop_buy_unit; (5) OVERSTOCK_CAP; (6) обменник хуже профильных; (7) депозит+cooldown.
[UI/EXAMPLE] Эталонные корзины подготовки (ориентир): T1 ~83 CU; T3 ~221 CU; T5 ~718 CU (расходники + сервисы + депозит) при дефолтных множителях.
@@END:B10.ECONOMY.CANON.02@@
@@BEGIN:B10.ECONOMY.DATA.02@@
[DATA] Награды контрактов: tmp_cu = round_half_up_div(BaseByTier[tier] * KindMult_bp[kind], 10000); reward_cu = round_half_up_div(tmp_cu * VarQuestMult_bp, 10000). VarQuestMultPct=rand_int(-10..10) (целое; детерминировано); VarQuestMult_bp = 10000 + VarQuestMultPct*100; BaseByTier: T1=60,T2=140,T3=280,T4=600,T5=1200; KindMult_bp: GATHER=10000, DELIVERY=9000, BOUNTY=12000, TOWER=13000. [CANON] VarQuestMultPct/VarQuestMult_bp обязаны быть keyed к offer_id: (world_seed, rng_stream=RNG_ECONOMY, context="quest.offer.var_mult", scope_id=offer_id, draw_index=0).
S3.7 Баланс-скелет (Tier 1-5) + примеры
Anti-abuse (канон): лимит активных=3; депозит; обязательный cooldown для repeatable при любом исходе.
QUEST_UPDATE типы: KILLCOUNT (по kill event), GATHER (по получению qty), DELIVER (по явной сдаче + списание предметов). Completion по сдаче (возврат в город).
QuestInstance (Save): quest_instance_id, quest_id, offer_id, state(ACTIVE/COMPLETED/FAILED/ABANDONED), started_at, expires_at, reward_cu, deposit_cu, objectives_progress[].
Repeatable cooldown: Save хранит quest_state.cooldowns[quest_id]=available_at_t_sec. При complete/fail/abandon/expiry: available_at_t_sec = t_sec + cooldown_sec.
WEIGHTED_SAMPLING_CANON (MVP, deterministic, no-float)
• Input: кандидаты {id, weight_int>=0}. weight=0 → игнор.
• Stable order: сортировать кандидатов по id asc (или иной канонически-стабильный порядок).
• One pick (roulette): total=Σweight; r=rand_int(0, total-1); идём в stable order, prefix+=weight; выбран первый где prefix>r.
• Without replacement (K picks): повторить K раз: One pick, затем weight выбранного=0 и пересчитать total.
• Draw spec: 1 draw на 1 pick; draw_index = pick_index (0..K-1).
• RNG key template: RngKey=(world_seed, rng_stream, context, scope_id, draw_index).
Сэмплирование офферов: weighted sampling without replacement по board_weight; RNG_ECONOMY keyed-RNG: (world_seed, rng_stream=RNG_ECONOMY, context="quest_board.offers", scope_id=(day_index, quest_board_id), draw_index=offer_index). Инвариант: draw_index = offer_index = pick_index (0..N_OFFERS-1), 1 draw на 1 pick.
Фильтр eligible_templates: tier_min<=access_tier<=tier_max; repeatable либо доступен по cooldown; flags (progress_flags) не блокируют.
Offer (вычисляемый объект): offer_id=HASH(world_seed, day_index, quest_board_id, slot_index), quest_id, tier, expires_at=day_indexDAY_SEC+ttl_daysDAY_SEC, reward_cu, deposit_cu, objectives[]. Save может хранить только кэш UI; истина - вычисление.
@@END:B10.ECONOMY.DATA.02@@
@@BEGIN:B10.ECONOMY.DATA.03@@
[DATA] Константы: N_OFFERS=6, MAX_ACTIVE_CONTRACTS=3, DEFAULT_OFFER_TTL_DAYS=3, DEFAULT_REPEATABLE_COOLDOWN_SEC=86400.
S3.6 Доска контрактов (QUEST_BOARD): офферы, жизненный цикл, ограничения
@@END:B10.ECONOMY.DATA.03@@
@@BEGIN:B10.ECONOMY.DATA.04@@
[DATA] Депозит контракта (анти-абуз и sink): deposit_cu = ceil_div(reward_cu * DEPOSIT_FRAC_BP, 10000), DEPOSIT_FRAC_BP=2000 (20%); списывается при QUEST_TAKE; возвращается только при QUEST_COMPLETE; сгорает при fail/abandon/expiry.
@@END:B10.ECONOMY.DATA.04@@
@@BEGIN:B10.ECONOMY.CANON.03@@
[CANON] DB_FILL_PATCH::SERVICE_ELIGIBILITY (MVP)
• ServiceDefinition имеет eligibility: requires_tags_all[] / forbids_tags_any[] / requires_class_any[] (или экв.).
• Service применим к item_instance только если eligibility проходит; никакой UI-магии.
• Eligibility проверяется до списания CU и до мутаций инвентаря; при fail → SYS_CONFLICT(PRECONDITION_FAILED).
• Salvage outputs: либо фиксированный [DATA] mapping, либо через coffer/loot-паттерн с keyed-RNG (rng_stream=RNG_LOOT, context="service.salvage", scope_id=service_call_id, draw_index=slot_i).
@@END:B10.ECONOMY.CANON.03@@
@@BEGIN:B10.ECONOMY.CANON.04@@
[CANON] DB_FILL_PATCH::SERVICES_OUTPUTS_DB_SPEC (MVP)
• Цель: закрыть churn для сервисов с выдачей предметов (repair/salvage/discard/identify) и зафиксировать deterministic outputs.

ServiceDefinition (content, минимальный контракт)
• service_id:string (immutable).
• service_type (enum или family): REPAIR_BROKEN | SALVAGE | DISCARD | HEAL | IDENTIFY (или экв. существующим SERVICE_*).
• eligibility: requires_tags_all[] / forbids_tags_any[] / requires_class_any[] (см. DB_FILL_PATCH::SERVICE_ELIGIBILITY).
• price_base_cu/int и/или формула цены — канон; конкретные коэффициенты — [DATA].

Outputs (нормализация к coffer; runtime выдача предметов только через LOOT_OPEN)
• outputs_fixed[]: {item_id, qty} — authoring-удобство. Build-step MUST материализовать детерминированный coffer и записать output_coffer_id.
• output_map (repair_map/repair_yield): authoring-удобство. Build-step MUST материализовать mapping input_item_id -> output_coffer_id (детерминированные coffers) и использовать его при ремонте.
• output_coffer_id: coffer_id — единый runtime-канал выдачи (в т.ч. для детерминированных выходов; вариативность допускается только внутри COFFER_OPEN_CANON).

@@END:B10.ECONOMY.CANON.04@@
@@BEGIN:B10.ECONOMY.CANON.05@@
[CANON] RNG/Scope для service outputs (через LOOT_OPEN)
• LOOT_OPEN(output_coffer_id) обязателен использовать:
- rng_stream=RNG_LOOT
- context = "service.<service_id>.open" (или "service.salvage" как общий контекст, если уже каноничен)
- scope_id = event_id (SERVICE_PAY) или иной сохранённый idempotency-key этого вызова
- draw_index = slot_i (0..K-1) по базовым слотам кофера
• Следствие: «no reroll by reload» достигается автоматически — повтор применения одного event_id не меняет исход (и вообще должен быть SKIP).
• Термин совместимости: если в тексте/коде встречается service_call_id — в MVP это alias на event_id соответствующего SERVICE_PAY.

@@END:B10.ECONOMY.CANON.05@@
@@BEGIN:B10.ECONOMY.CANON.06@@
[CANON] Идемпотентность и детерминизм сервисов
• Любой сервис применяется только через событие SERVICE_PAY (идемпотентность по event_id).
• Проверка eligibility и всех предусловий — до списания CU и до мутаций инвентаря.
• Если сервис потребляет предметы: выбор удаляемых инстансов строго детерминирован (item_instance_id asc; см. DB_FILL_PATCH::STABLE_SERIALIZATION).

SERVICE_REPAIR_BROKEN:
• Цена: для repair_map cost=max(SERVICE_MIN_COST_CU, ceil_div(P_ref(intact) * REPAIR_MAP_FRAC_BP, 10000)); для repair_yield cost=max(SERVICE_MIN_COST_CU, ceil_div(sum(P_ref(mat) * qty) * REPAIR_YIELD_FRAC_BP, 10000)). [DATA] SERVICE_MIN_COST_CU, REPAIR_MAP_FRAC_BP, REPAIR_YIELD_FRAC_BP — DB_SPEC/balance.
• Эффект: удалить broken_item; затем выполнить LOOT_OPEN по coffer_id, выбранному data-only из repair_map/repair_yield (после нормализации build-step), и применить INVENTORY_ADD по результатам.
• Ограничения (анти-арбитраж): сервис работает только для предметов с тегом BROKEN_LOOT. BROKEN_LOOT не имеет price_base_cu (alias price_base), не продаётся/не покупается магазинами; ремонт через сервис не должен давать экономической выгоды.
SERVICE_HEAL:
• Эффект: удалить статус (полностью).
• Цена за статус: cost_one = apply_bp_ceil(apply_bp_floor(HEAL_BASE_CU, TierFactor_bp(access_tier)), SeverityFactor_bp(severity)). [DATA] HEAL_BASE_CU, TierFactor_bp(tier), SeverityFactor_bp(severity) задаются в DB_SPEC/balance.
• Лечит только статусы из HEALABLE_STATUS_SET={INJURY, INFECTION, POISONED}.
SERVICE_IDENTIFY:
• Цена: cost=max(IDENTIFY_MIN_CU, ceil_div(P_ref(item) * IDENTIFY_FEE_MULT_BP, 10000)). [DATA] IDENTIFY_FEE_MULT_BP и IDENTIFY_MIN_CU задаются в DB_SPEC/balance.
• Эффект: is_identified=true; снять UNIDENTIFIED.
@@END:B10.ECONOMY.CANON.06@@
@@BEGIN:B10.ECONOMY.DATA.05@@
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
Общий принцип: сервис применяется только через SERVICE_PAY (idempotent). Это не “прочность”: сервисы не завязаны на износ от боя; они работают с UNIDENTIFIED, лечением негативных статусов и BROKEN_LOOT находками.
S3.5 Городские сервисы (денежные sinks) + депозит
@@END:B10.ECONOMY.DATA.05@@
@@BEGIN:B10.ECONOMY.DATA.06@@
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
T1–T2:
@@END:B10.ECONOMY.DATA.06@@
@@BEGIN:B10.ECONOMY.DATA.07@@
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
T2–T3:
@@END:B10.ECONOMY.DATA.07@@
@@BEGIN:B10.ECONOMY.DATA.08@@
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
T3–T5:
@@END:B10.ECONOMY.DATA.08@@
@@BEGIN:B10.ECONOMY.DATA.09@@
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
Рекомендация для генератора: хранить для каждого spawn-band набор loot_tag’ов и encounter_tag’ов,и подмешивать контент таблицами (LOOT_*), не хардкодом. Тогда добавление “новой темы этажей” = новый пакет JSON.
Решение: основные кривые (рост HP, WDB, шанс травм, цены) держать в баланс-таблицах, а карточки хранить “как сущность”, не как баланс-истину.

@@END:B10.ECONOMY.DATA.09@@@@END:B10.ECONOMY@@
@@END:B10@@
@@BEGIN:B11@@
## B11 — PROGRESSION: access_tier, перки, unlock/validation
ACCESS_TIER (CANON)
Сохранение: поле access_tier хранится в save.progress и отражает наивысший достигнутый tier контента (T1–T5).
Обновление: access_tier увеличивается, когда игрок впервые успешно входит в локацию или этаж соответствующего tier, и никогда не уменьшается.
Использование: access_tier влияет на допустимые шаблоны контрактов, коэффициенты цен, открываемые перки и уровни сервисов. Формулы в экономике и прогрессии должны ссылаться на access_tier.
VALIDATION_ADDENDUM_PERKS (MVP)
Добавить к VALIDATION_LIST следующие проверки для перков/разблоков:
• perk_id уникальны; запрещено переименование существующих perk_id.
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
• CAP_BY_EFFECT_ID обязан содержать все effect_id, которые встречаются в PERK_DEF; иначе ошибка валидации.
• UNLOCK_RULES: pool_id существует; cond_type валиден; BOSS_KILLED должен ссылаться на boss_id из MONSTER/BOSS DEF (если нет — ASSUMPTION: boss_id строкой фиксируется в encounter/boss event).
• При нарушении валидации: клиент не запускает сессию (fail-fast) и пишет SYS_CONFLICT reason_code=CONTENT_REF_MISSING или INVALID_VALUE (policy определяется таблицей).
ID-стандарты:
Регион: OUTWALLS_FOREST
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
POI: POI_FO_*
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.

@@END:B11@@
@@BEGIN:B12@@
## B12 — MAGIC: концентрация, земной ток, заклинания
@@BEGIN:B12.SPELLS@@
Магия концентрации и земного тока (стандарт v1_0)
Источник энергии
Персонаж черпает энергию из земного тока (силы, текущей по поверхности земли).  Зачарованный камень не хранит энергию: он задаёт “форму” заклинания и эффективность преобразования потока в эффект.
Концентрация
Все заклинания — поддерживаемые (maintained): эффект существует только пока персонаж поддерживает его концентрацией.
Чтобы заклинание работало, одновременно нужны:
Зачарованный предмет с соответствующим SpellID.
Свободная ячейка концентрации (Concentration Slot).
ConcentrationCost — сколько слотов занимает одно активное заклинание.  Для простоты и отсутствия двусмысленности в этом стандарте:  ➡️ ConcentrationCost = 1 для каждого из 22 заклинаний.
Семя концентрации
В мире можно добывать “семя концентрации”.  Приняв семя, персонаж навсегда получает +1 слот концентрации.
Интеллект = ширина канала
Интеллект задаёт максимальную “пропускную способность” канала персонажа.
Вводим единицу клиента: CP (Channel Points).
ChannelCapacityCP = Intelligence × 10
Пример: Интеллект 10 → 100 CP.
Нагрузка заклинаний на канал
Каждое активное заклинание потребляет часть канала — ChannelLoadCP.  Условие работы:
Σ ChannelLoadCP ≤ ChannelCapacityCP
Если включение нового заклинания приведёт к превышению ёмкости — заклинание не включается (и слот концентрации не занимает).
Качество камня = КПД и сила
Качество камня задаётся числом Q = 1..5 (T1..T5).
Канон fixed-point (bp): - PotencyMult_bp(Q) = 10000 + 1500(Q-1) - EfficiencyMult_bp(Q) = 10000 + 2000(Q-1)
Ползунок мощности
PowerLevelPct ∈ {25,50,75,100}. PowerLevel_bp = PowerLevelPct * 100.
Политика мощности (power_level_policy, на уровне spell_id):
• USER_SELECTABLE (дефолт): игрок выбирает PowerLevelPct ∈ {25,50,75,100} при включении заклинания; значение должно сохраняться для детерминизма.
• FIXED_100: PowerLevelPct фиксирован = 100 (PowerLevel_bp=10000); UI-ползунок отключён; любые попытки задать другое значение отклоняются валидатором.
Нагрузка на канал (округление вверх): - ChannelLoadCP = ceil_div(BaseLoadCP * PowerLevel_bp, EfficiencyMult_bp(Q))
Сила эффекта (округление вниз): - EffectStrength = apply_bp_floor(apply_bp_floor(BaseStrength, PowerLevel_bp), PotencyMult_bp(Q))
Дальность (если есть) задаётся политикой range_policy на уровне spell_id (см. B12.M0):
• range_policy=SCALED: RangeMeters = apply_bp_floor(apply_bp_floor(BaseRange_m, PowerLevel_bp), PotencyMult_bp(Q)); затем RangeMeters = apply_bp_floor(RangeMeters, EnvMult_bp).
• range_policy=FIXED: RangeMeters = BaseRange_m (без масштабирования Power/Q; EnvMult_bp не меняет дальность, если карточка заклинания явно не говорит иначе).
• range_policy=NONE: дальности нет; любые проверки/таргетинг/scan по дистанции для этого spell_id запрещены валидатором (использовать только SELF без дистанционного гейтинга).
Контакт с землёй
Условие питания:
Если Grounded = false (персонаж изолирован от земли), все поддерживаемые заклинания приостанавливаются: эффект = 0, но ConcentrationCost считается занятым.
Если Grounded = true, эффекты возобновляются автоматически.
Правило простоты: один SpellID — один активный экземпляр
Чтобы не было спорных “два одинаковых барьера в два слота”:
На персонаже может быть активен только один экземпляр каждого SpellID.  Если надеты два предмета с одним SpellID, включить можно только один из них.
Исключение (чтобы не усложнять): заклинания, действие которых применяется к конкретному предмету и влияет только на него (например, SPELL_WEIGHT_DOWN и SPELL_WEIGHT_UP), могут быть активны одновременно на разных предметах. Каждый такой активный предмет занимает отдельный слот концентрации.
Пакет заклинаний (прототип): базовые 1–22 + расширение (дополнения ниже). Полные описания, без двусмысленности.

@@BEGIN:B12.M0@@
@@BEGIN:B12.SPELLS.CANON.01@@
[CANON] MAGIC_RUNTIME_CONTRACT_SPELLPACK (v1_1)
- Terms: bp:int (10000=1.00), ChanceBp:int (0..10000), ticks10s:int (1 tick=10 sec), t_sec:int.
- Common ops (no float):
  - floor_div(a,b), ceil_div(a,b) on int.
  - apply_bp_floor(x:int, mult_bp:int) = floor_div(x * mult_bp, 10000).
  - apply_bp_ceil(x:int, mult_bp:int) = ceil_div(x * mult_bp, 10000).

@@END:B12.SPELLS.CANON.01@@
@@BEGIN:B12.SPELLS.CANON.02@@
[CANON] Spell instance + source
- Each active spell is bound to a concrete source item_instance_id (enchant stone carrier).
- spell_instance_id (stable) = (actor_id, source_item_instance_id, spell_id).
- All toggles/procs reference spell_instance_id in scope_id templates.

@@END:B12.SPELLS.CANON.02@@
@@BEGIN:B12.SPELLS.CANON.03@@
[CANON] PowerLevel policy
- Default: PowerLevelPct in {25,50,75,100}. Stored in runtime as power_level_bp = PowerLevelPct*100.
- power_level_policy: USER_SELECTABLE | FIXED_100. FIXED_100 locks power_level_bp=10000 and UI slider disabled.
- Storage: power_level_bp is a runtime choice stored per spell_instance_id while active; it is NOT a property of the source item.
- Event: RULE_SPELL_TOGGLE(on=true) must carry power_level_bp for USER_SELECTABLE; allowed set {2500,5000,7500,10000}.
- Validation: if power_level_policy=FIXED_100 then effective power_level_bp=10000; provided power_level_bp !=10000 => reject (RULE_SPELL_PRECONDITION_FAIL, reason_code=INVALID_VALUE).

@@END:B12.SPELLS.CANON.03@@
@@BEGIN:B12.SPELLS.CANON.04@@
[CANON] Q policy
- Q:int in {1..5}. PotencyMult_bp(Q)=10000+1500*(Q-1). EfficiencyMult_bp(Q)=10000+2000*(Q-1).

@@END:B12.SPELLS.CANON.04@@
@@BEGIN:B12.SPELLS.CANON.05@@
[CANON] Channel + concentration
- ChannelCapacityCP = Intelligence * 10.
- Each spell consumes ConcentrationCost slots (in this pack: ConcentrationCost=1 everywhere).
- Enable preconditions (fail-fast, no side effects):
  - has free concentration slots
  - Sum(ChannelLoadCP_active + ChannelLoadCP_new) <= ChannelCapacityCP
- ChannelLoadCP (ceil): ChannelLoadCP = ceil_div(BaseLoadCP * power_level_bp, EfficiencyMult_bp(Q)).
- When grounded=false, concentration and channel load remain reserved, but effect output is 0.

@@END:B12.SPELLS.CANON.05@@
@@BEGIN:B12.SPELLS.CANON.06@@
[CANON] One SpellID vs stacking
- Default policy: stack_policy=UNIQUE_BY_SPELLID (only one active instance per actor+spell_id).
- Exceptions must be explicit in [DATA] SpellDefinition.stack_policy:
  - ITEM_BOUND (multiple allowed if different source_item_instance_id)
  - WEAPON_BOUND (multiple allowed if different weapon instance)
  - MULTI_INSTANCE_ADD (multiple allowed; effect bonuses sum in bp; used only where explicitly stated, e.g. SPELL_VITAL_RESERVE).

@@END:B12.SPELLS.CANON.06@@
@@BEGIN:B12.SPELLS.CANON.07@@
[CANON] Grounded + ground quality
- grounded:bool (hard gate). If grounded=false => spell_effective=0 (but reservations remain).
- ground_quality_pct:int in 0..100 is an env query at actor position (if subsystem absent, treat as 100).
- For most spells: env_mult_bp = ground_quality_pct*100 (0..10000).
- SPELL_GROUNDING adds compensation: env_mult_bp = clamp_int(ground_quality_pct*100 + grounding_comp_bp, 0, 10000).
- env_mult_bp applies to: strength and range outputs. For SCAN_PROGRESS spells, it also scales progress per 10s tick (see below).

@@END:B12.SPELLS.CANON.07@@
@@BEGIN:B12.SPELLS.CANON.08@@
[CANON] Scaling formulas (strength/range/ticks)
- Strength (int output): strength_int = apply_bp_floor(apply_bp_floor(base_strength_int, power_level_bp), PotencyMult_bp(Q)); then strength_int = apply_bp_floor(strength_int, env_mult_bp).
- Strength (bp output): strength_bp = apply_bp_floor(apply_bp_floor(base_strength_bp, power_level_bp), PotencyMult_bp(Q)); then strength_bp = apply_bp_floor(strength_bp, env_mult_bp).
- Range (meters int): if range_policy=SCALED => range_m = apply_bp_floor(apply_bp_floor(base_range_m, power_level_bp), PotencyMult_bp(Q)); then range_m = apply_bp_floor(range_m, env_mult_bp).
- Range fixed: range_policy=FIXED => range_m = base_range_m (env_mult does not change fixed ranges unless explicitly stated by spell card).
- Range none: range_policy=NONE => range_m is absent and treated as 0; any binding_kind=TARGET or tick_model=SCAN_PROGRESS that depends on range MUST be rejected at build/load-time.
- Param naming: base_range_m is the canonical param_key for single-range spells (both SCALED and FIXED). The key 'range_m' is reserved for computed runtime only and must not appear in DB_SPEC.
- Tick scaling (delay/duration in ticks10s): ticks10s_scaled = ceil_div(base_ticks10s * 10000, PotencyMult_bp(Q)). (env_mult does NOT change delays/durations; only SCAN progress rate.)

@@END:B12.SPELLS.CANON.08@@
@@BEGIN:B12.SPELLS.CANON.09@@
[CANON] Tick model + time integration
- PER_10S: effect applies on combat ROUND_END (10s) and on TIME_ADVANCE via canonical chunking (B05). No background ticks.
- SCAN_PROGRESS: progress_bp increments per 10s tick by progress_step_bp = env_mult_bp (0..10000).
  - required_ticks10s is an int. Completion condition: progress_bp >= required_ticks10s*10000.
  - If spell toggled off or target out of range => progress_bp resets to 0 (unless spell card says otherwise).

@@END:B12.SPELLS.CANON.09@@
@@BEGIN:B12.SPELLS.CANON.10@@
[CANON] Explain/Replay (minimal)
- RULE_SPELL_TOGGLE meta{event_id, actor_id, spell_id, source_item_instance_id, on:bool, power_level_bp?, reason_code?}.
- RULE_SPELL_TICK meta{event_id, actor_id, spell_id, tick_kind, tick_index, delta_sec}.
- RULE_SPELL_SCAN_PROGRESS meta{event_id, actor_id, spell_id, progress_bp_after, required_bp}.
- RULE_SPELL_PROC meta{event_id, actor_id, spell_id, op_id, draw_index, draw_u16, success:bool}.
- RULE_SPELL_PRECONDITION_FAIL meta{event_id, actor_id, spell_id, reason_code}.

@@END:B12.SPELLS.CANON.10@@
@@BEGIN:B12.SPELLS.CANON.11@@
[CANON] Validation (runtime)
- V_SPELL_CHANNEL: enable rejects if channel would exceed capacity.
- V_SPELL_UNIQUE: enforce stack_policy.
- V_SPELL_GROUNDED: grounded=false => output 0 (no mutation except counters if spell card allows).
- V_SPELL_RANGE: for TARGET spells, out of range => auto-off or suspend per spell card (must be deterministic).

@@END:B12.SPELLS.CANON.11@@
@@BEGIN:B12.SPELLS.CANON.12@@
[CANON] Validation (build/load-time)
- All spell_id references must exist; unknown => fail-fast.
- All params required by a spell card must exist and match types/ranges; unknown params => fail-fast.
- Any chance pct stored as ChanceBp (0..10000).
@@END:B12.M0@@

@@BEGIN:B12.M1@@
@@END:B12.SPELLS.CANON.12@@
@@BEGIN:B12.SPELLS.DATA.01@@
[DATA] DB_SPEC: SPELL_DEF + SPELL_PARAM_DEF (MVP)
SPELL_DEF (content)
- spell_id:string (immutable).
- display_name:string (ui-only).
- concentration_cost:int (def=1).
- base_load_cp:int (>=0).
- binding_kind: SELF | TARGET | ITEM_BOUND | WEAPON_BOUND.
- tick_model: NONE | PER_10S | ON_HIT | ON_BLOCK | ON_SCENE_LOOT | SCAN_PROGRESS | SHOP_PRICE | DIALOGUE_STEP.
- stack_policy: UNIQUE_BY_SPELLID | ITEM_BOUND | WEAPON_BOUND | MULTI_INSTANCE_ADD.
- power_level_policy: USER_SELECTABLE | FIXED_100.
- range_policy: SCALED | FIXED | NONE.
- feature_gate:string? (empty = enabled in MVP).

SPELL_PARAM_DEF (content)
- spell_id:string (ref).
- param_key:string (immutable within spell_id).
- param_type: INT | BP | CHANCE_BP | TICKS10S | METER_INT.
- value_int:int (used for INT/TICKS10S/METER_INT).
- value_bp:int (used for BP/CHANCE_BP; 0..10000 for CHANCE_BP).
- constraints: min/max implicit by param_type + spell card rules.

@@END:B12.SPELLS.DATA.01@@
@@BEGIN:B12.SPELLS.DATA.02@@
[DATA] Enchant source vs runtime settings (recommended)
- ItemInstance.enchant{spell_id, q:int, source_item_instance_id} (serialized in save). q is a property of the stone/source and MUST be stable for the item instance.
- power_level_bp is NOT stored on the item. It is a runtime choice per active spell_instance_id.
- Save (recommended minimal): ActiveSpellState{spell_instance_id, on:bool, power_level_bp:int, target_id?:string, progress_bp?:int, cooldown_ticks10s?:int, misc_state?:object}.
- For power_level_policy=FIXED_100: power_level_bp may be omitted from state (implicitly 10000); if present must be 10000.
@@END:B12.M1@@

@@BEGIN:B12.SPELLS.INDEX@@
@@END:B12.SPELLS.DATA.02@@
@@BEGIN:B12.SPELLS.CANON.13@@
[CANON] SPELL_PACK_INDEX (1..39)
1  SPELL_BARRIER - Barrier
2  SPELL_REGEN - Regeneration
3  SPELL_LIGHT - Light
4  SPELL_STR_BOOST - Strength boost
5  SPELL_SPD_BOOST - Speed boost
6  SPELL_DEX_BOOST - Dexterity boost
7  SPELL_VIT_BOOST - Vitality boost
8  SPELL_AURA_SIGHT - Aura sight
9  SPELL_NIGHT_VISION - Night vision
10 SPELL_IDENTIFY - Identify (scan)
11 SPELL_ORE_SCAN - Ore scan (scan)
12 SPELL_LUCK_BOOST - Luck boost
13 SPELL_IRON_SKIN - Iron skin
14 SPELL_ACCURACY - Accuracy (damage bonus)
15 SPELL_MISTFORM - Mistform (escape)
16 SPELL_WEIGHT_DOWN - Weight down (item)
17 SPELL_VAMPIRISM - Vampirism (on hit)
18 SPELL_WEIGHT_UP - Weight up (item)
19 SPELL_STEAL_STR - Steal strength stacks
20 SPELL_STEAL_AGI - Steal agility stacks
21 SPELL_STEAL_SPD - Steal speed stacks
22 SPELL_GEAR_CLEAN - Gear clean (per10s)
23 SPELL_GROUNDING - Grounding (env mult)
24 SPELL_SILENT_STEP - Silent step
25 SPELL_HERB_SCAN - Herb scan (scan)
26 SPELL_INERTIA_STRIKE - Inertia strike (stun proc)
27 SPELL_BLEEDING_FLETCH - Bleeding fletch (bleed proc)
28 SPELL_ARROW_RECLAIM - Arrow reclaim (scene loot)
29 SPELL_SHIELD_FOCUS - Shield focus (block chance)
30 SPELL_DEFLECTION_ANGLE - Deflection angle (block reduction)
31 SPELL_SHIELD_COUNTERSTUN - Shield counter-stun (on block)
32 SPELL_CALM_AURA - Calm aura (social)
33 SPELL_EMPATHY_READ - Empathy read (social)
34 SPELL_PLAINNESS_VEIL - Plainness veil (social)
35 SPELL_CONVERSATION_HUSH - Conversation hush (social)
36 SPELL_FAIR_TRADE - Fair trade (shop price)
37 SPELL_INTIMIDATION_EDGE - Intimidation edge (social)
38 SPELL_VITAL_RESERVE - Vital reserve (max HP +)
39 SPELL_VITAL_SUPPRESSION - Vital suppression (max HP - target)
@@END:B12.SPELLS.INDEX@@

@@BEGIN:B12.SPELL.SPELL_BARRIER.C0@@
SPELL::SPELL_BARRIER
@@END:B12.SPELLS.CANON.13@@
@@BEGIN:B12.SPELLS.CANON.14@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_BARRIER.C0@@

@@BEGIN:B12.SPELL.SPELL_BARRIER.C1@@
@@END:B12.SPELLS.CANON.14@@
@@BEGIN:B12.SPELLS.CANON.15@@
[CANON] Math + Rounding
- units: t_sec:int, ticks10s:int, bp:int, HP:int
- barrier_max_hp:int = scaled_strength_int(base_barrier_hp).
- barrier_current_hp:int in [0..barrier_max_hp].
- absorb order: shield -> armor -> barrier -> HP (B08).
- absorb: absorb_hp = min(barrier_current_hp, dmg_after_armor_hp).
  - barrier_current_hp -= absorb_hp; hp_damage = dmg_after_armor_hp - absorb_hp.
- microdamage: applies only if barrier_current_hp==0 BEFORE hit and dmg_after_armor_hp==0 and dmg_before_def>0 => hp_damage=1; exception: Mistform cap still applies (B08).
- recharge delay (no regen):
  - base_recharge_delay_ticks10s:int (param)
  - recharge_delay_ticks10s = ceil_div(base_recharge_delay_ticks10s*10000, PotencyMult_bp(Q)).
  - last_damage_t_sec updated on any incoming dmg_before_def>0 (even if fully absorbed).
  - if (now_t_sec - last_damage_t_sec) >= recharge_delay_ticks10s*10 => barrier_current_hp = barrier_max_hp.
@@END:B12.SPELL.SPELL_BARRIER.C1@@

@@BEGIN:B12.SPELL.SPELL_BARRIER.C2@@
@@END:B12.SPELLS.CANON.15@@
@@BEGIN:B12.SPELLS.CANON.16@@
[CANON] Runtime wiring
- hooks: DMG_PIPELINE (absorb + last_damage_t_sec), TIME_ADVANCE/ROUND_END (recharge check).
- ordering: absorb after shield+armor, before HP apply.
- state fields: barrier_current_hp:int, barrier_max_hp:int, last_damage_t_sec:int.
- explain: RULE_SPELL_TICK tick_kind='barrier.recharge_check'; RULE_SPELL_TOGGLE; optional RULE_SPELL_CAP_CLAMP for clamping barrier_current.
@@END:B12.SPELL.SPELL_BARRIER.C2@@

@@BEGIN:B12.SPELL.SPELL_BARRIER.D0@@
@@END:B12.SPELLS.CANON.16@@
@@BEGIN:B12.SPELLS.DATA.03@@
[DATA] Params (DB_SPEC)
- base_barrier_hp:INT:HP:int>=0
- base_recharge_delay_ticks10s:TICKS10S:int>=0
- note: BaseLoadCP=30 lives in SPELL_DEF.base_load_cp.
@@END:B12.SPELL.SPELL_BARRIER.D0@@

@@BEGIN:B12.SPELL.SPELL_BARRIER.Q0@@
@@END:B12.SPELLS.DATA.03@@
@@BEGIN:B12.SPELLS.QA.01@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 FullAbsorb: barrier_current>=dmg_after_armor => hp_damage=0 and barrier_current decreases.
- T07 DepleteThenMicro: if barrier_current==0 before hit and dmg_after_armor rounds to 0 with dmg_before_def>0 => hp_damage=1 (unless Mistform cap).
- T08 RechargeInstant: after delay with no dmg, barrier_current resets to barrier_max.
- T09 NoGradualRegen: during delay barrier_current stays constant.
- T10 DeterministicDelay: recharge_delay_ticks10s uses ceil_div and depends only on Q.
@@END:B12.SPELL.SPELL_BARRIER.Q0@@

@@BEGIN:B12.SPELL.SPELL_REGEN.C0@@
SPELL::SPELL_REGEN
@@END:B12.SPELLS.QA.01@@
@@BEGIN:B12.SPELLS.CANON.17@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: PER_10S
- rng_ops: (none)
@@END:B12.SPELL.SPELL_REGEN.C0@@

@@BEGIN:B12.SPELL.SPELL_REGEN.C1@@
@@END:B12.SPELLS.CANON.17@@
@@BEGIN:B12.SPELLS.CANON.18@@
[CANON] Math + Rounding
- units: ticks10s:int (1=10s), HP:int, sec:int
- heal_hp_per_tick:int = scaled_strength_int(base_heal_hp_per_tick).
- recovery_extra_sec_per_tick:int = scaled_strength_int(base_recovery_extra_sec_per_tick).
- PER_10S tick:
  - HPCurrent = min(EffectiveMaxHP, HPCurrent + heal_hp_per_tick).
  - For each status_instance where status_tag in REGEN_ACCEL_STATUS_SET:
    time_left_sec = max(0, time_left_sec - recovery_extra_sec_per_tick).
- Regen is maintained (not instant). No effect at toggle time besides enabling.
@@END:B12.SPELL.SPELL_REGEN.C1@@

@@BEGIN:B12.SPELL.SPELL_REGEN.C2@@
@@END:B12.SPELLS.CANON.18@@
@@BEGIN:B12.SPELLS.CANON.19@@
[CANON] Runtime wiring
- hooks: ROUND_END (combat), TIME_ADVANCE (chunked per10s).
- ordering: apply after damage resolution for the tick; before hunger/thirst etc ordering is per B05.
- state fields: none beyond on/off.
- explain: RULE_SPELL_TICK tick_kind='regen.per10s' with delta_hp and affected_status_count.
@@END:B12.SPELL.SPELL_REGEN.C2@@

@@BEGIN:B12.SPELL.SPELL_REGEN.D0@@
@@END:B12.SPELLS.CANON.19@@
@@BEGIN:B12.SPELLS.DATA.04@@
[DATA] Params (DB_SPEC)
- base_heal_hp_per_tick:INT:HP:int>=0
- base_recovery_extra_sec_per_tick:INT:sec:int>=0
- regen_accel_status_tags_any: (DATA allowlist) status:* tags eligible for acceleration.
@@END:B12.SPELL.SPELL_REGEN.D0@@

@@BEGIN:B12.SPELL.SPELL_REGEN.Q0@@
@@END:B12.SPELLS.DATA.04@@
@@BEGIN:B12.SPELLS.QA.02@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 HealClamp: HP never exceeds EffectiveMaxHP.
- T07 StatusAccelOnly: only statuses in allowlist are accelerated.
- T08 NoInstant: toggle on does not change HP without a tick.
- T09 TimeAdvanceChunk: delta_sec=25 applies 2 full ticks + 1 tail tick per B05 rules.
- T10 GroundedPauseTick: grounded=false => tick produces 0 deltas.
@@END:B12.SPELL.SPELL_REGEN.Q0@@

@@BEGIN:B12.SPELL.SPELL_LIGHT.C0@@
SPELL::SPELL_LIGHT
@@END:B12.SPELLS.QA.02@@
@@BEGIN:B12.SPELLS.CANON.20@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_LIGHT.C0@@

@@BEGIN:B12.SPELL.SPELL_LIGHT.C1@@
@@END:B12.SPELLS.CANON.20@@
@@BEGIN:B12.SPELLS.CANON.21@@
[CANON] Math + Rounding
- ranges fixed: bright_range_m=20, dim_range_m=30 (range_policy=FIXED).
- brightness scales: bright_lux_int = scaled_strength_int(base_brightness_bright); dim_lux_int = scaled_strength_int(base_brightness_dim).
- stealth hard rule: while SPELL_LIGHT active => stealth attempts forbidden (0% success), regardless of other modifiers.
@@END:B12.SPELL.SPELL_LIGHT.C1@@

@@BEGIN:B12.SPELL.SPELL_LIGHT.C2@@
@@END:B12.SPELLS.CANON.21@@
@@BEGIN:B12.SPELLS.CANON.22@@
[CANON] Runtime wiring
- hooks: perception/visibility evaluation, stealth system gate (if stealth absent => treat as UI rule + V_NEXT hook).
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE only.
@@END:B12.SPELL.SPELL_LIGHT.C2@@

@@BEGIN:B12.SPELL.SPELL_LIGHT.D0@@
@@END:B12.SPELLS.CANON.22@@
@@BEGIN:B12.SPELLS.DATA.05@@
[DATA] Params (DB_SPEC)
- base_brightness_bright:INT:int>=0 (units: candela or lux, UI-defined)
- base_brightness_dim:INT:int>=0
- bright_range_m:METER_INT:int=20
- dim_range_m:METER_INT:int=30
@@END:B12.SPELL.SPELL_LIGHT.D0@@

@@BEGIN:B12.SPELL.SPELL_LIGHT.Q0@@
@@END:B12.SPELLS.DATA.05@@
@@BEGIN:B12.SPELLS.QA.03@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 RangeFixed: range does not change with Q or power_level.
- T07 BrightnessScales: brightness changes with Q/power_level and env_mult.
- T08 StealthForbidden: any stealth action returns PRECONDITION_FAILED while active.
- T09 GroundedPause: grounded=false => light off (no brightness), but reservations remain.
- T10 MultipleLightReject: UNIQUE_BY_SPELLID enforced.
@@END:B12.SPELL.SPELL_LIGHT.Q0@@

@@BEGIN:B12.SPELL.SPELL_STR_BOOST.C0@@
SPELL::SPELL_STR_BOOST
@@END:B12.SPELLS.QA.03@@
@@BEGIN:B12.SPELLS.CANON.23@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_STR_BOOST.C0@@

@@BEGIN:B12.SPELL.SPELL_STR_BOOST.C1@@
@@END:B12.SPELLS.CANON.23@@
@@BEGIN:B12.SPELLS.CANON.24@@
[CANON] Math + Rounding
- bonus_bp:int = scaled_strength_bp(base_bonus_bp_str).
- StatFinal = floor_div(StatBase * (10000 + bonus_bp_total), 10000).
- If multiple sources allowed (policy MULTI_INSTANCE_ADD), bonuses sum in bp; else UNIQUE_BY_SPELLID.
- Disable: on off or grounded=false => bonus_bp=0 (StatFinal recomputed).
@@END:B12.SPELL.SPELL_STR_BOOST.C1@@

@@BEGIN:B12.SPELL.SPELL_STR_BOOST.C2@@
@@END:B12.SPELLS.CANON.24@@
@@BEGIN:B12.SPELLS.CANON.25@@
[CANON] Runtime wiring
- hooks: derived-stats recompute (on toggle, on grounded change, on equipment change).
- state: none beyond on/off; optional cached bonus_bp for explain.
- explain: RULE_SPELL_TOGGLE; optional RULE_SPELL_CAP_CLAMP for stat clamp if system has caps.
@@END:B12.SPELL.SPELL_STR_BOOST.C2@@

@@BEGIN:B12.SPELL.SPELL_STR_BOOST.D0@@
@@END:B12.SPELLS.CANON.25@@
@@BEGIN:B12.SPELLS.DATA.06@@
[DATA] Params (DB_SPEC)
- base_bonus_bp_str:BP:bp:int>=0 (10000=+100%)
@@END:B12.SPELL.SPELL_STR_BOOST.D0@@

@@BEGIN:B12.SPELL.SPELL_STR_BOOST.Q0@@
@@END:B12.SPELLS.DATA.06@@
@@BEGIN:B12.SPELLS.QA.04@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ExactFloor: StatFinal uses floor_div, no float.
- T07 DisableInstant: toggle off removes bonus immediately.
- T08 EnvMult: poor ground scales bonus down via env_mult.
- T09 StackPolicy: UNIQUE_BY_SPELLID rejects second instance.
- T10 DeterministicRecompute: repeated recompute yields same value.
@@END:B12.SPELL.SPELL_STR_BOOST.Q0@@

@@BEGIN:B12.SPELL.SPELL_SPD_BOOST.C0@@
SPELL::SPELL_SPD_BOOST
@@END:B12.SPELLS.QA.04@@
@@BEGIN:B12.SPELLS.CANON.26@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_SPD_BOOST.C0@@

@@BEGIN:B12.SPELL.SPELL_SPD_BOOST.C1@@
@@END:B12.SPELLS.CANON.26@@
@@BEGIN:B12.SPELLS.CANON.27@@
[CANON] Math + Rounding
- bonus_bp:int = scaled_strength_bp(base_bonus_bp_spd).
- StatFinal = floor_div(StatBase * (10000 + bonus_bp_total), 10000).
- If multiple sources allowed (policy MULTI_INSTANCE_ADD), bonuses sum in bp; else UNIQUE_BY_SPELLID.
- Disable: on off or grounded=false => bonus_bp=0 (StatFinal recomputed).
@@END:B12.SPELL.SPELL_SPD_BOOST.C1@@

@@BEGIN:B12.SPELL.SPELL_SPD_BOOST.C2@@
@@END:B12.SPELLS.CANON.27@@
@@BEGIN:B12.SPELLS.CANON.28@@
[CANON] Runtime wiring
- hooks: derived-stats recompute (on toggle, on grounded change, on equipment change).
- state: none beyond on/off; optional cached bonus_bp for explain.
- explain: RULE_SPELL_TOGGLE; optional RULE_SPELL_CAP_CLAMP for stat clamp if system has caps.
@@END:B12.SPELL.SPELL_SPD_BOOST.C2@@

@@BEGIN:B12.SPELL.SPELL_SPD_BOOST.D0@@
@@END:B12.SPELLS.CANON.28@@
@@BEGIN:B12.SPELLS.DATA.07@@
[DATA] Params (DB_SPEC)
- base_bonus_bp_spd:BP:bp:int>=0 (10000=+100%)
@@END:B12.SPELL.SPELL_SPD_BOOST.D0@@

@@BEGIN:B12.SPELL.SPELL_SPD_BOOST.Q0@@
@@END:B12.SPELLS.DATA.07@@
@@BEGIN:B12.SPELLS.QA.05@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ExactFloor: StatFinal uses floor_div, no float.
- T07 DisableInstant: toggle off removes bonus immediately.
- T08 EnvMult: poor ground scales bonus down via env_mult.
- T09 StackPolicy: UNIQUE_BY_SPELLID rejects second instance.
- T10 DeterministicRecompute: repeated recompute yields same value.
@@END:B12.SPELL.SPELL_SPD_BOOST.Q0@@

@@BEGIN:B12.SPELL.SPELL_DEX_BOOST.C0@@
SPELL::SPELL_DEX_BOOST
@@END:B12.SPELLS.QA.05@@
@@BEGIN:B12.SPELLS.CANON.29@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_DEX_BOOST.C0@@

@@BEGIN:B12.SPELL.SPELL_DEX_BOOST.C1@@
@@END:B12.SPELLS.CANON.29@@
@@BEGIN:B12.SPELLS.CANON.30@@
[CANON] Math + Rounding
- bonus_bp:int = scaled_strength_bp(base_bonus_bp_dex).
- StatFinal = floor_div(StatBase * (10000 + bonus_bp_total), 10000).
- If multiple sources allowed (policy MULTI_INSTANCE_ADD), bonuses sum in bp; else UNIQUE_BY_SPELLID.
- Disable: on off or grounded=false => bonus_bp=0 (StatFinal recomputed).
@@END:B12.SPELL.SPELL_DEX_BOOST.C1@@

@@BEGIN:B12.SPELL.SPELL_DEX_BOOST.C2@@
@@END:B12.SPELLS.CANON.30@@
@@BEGIN:B12.SPELLS.CANON.31@@
[CANON] Runtime wiring
- hooks: derived-stats recompute (on toggle, on grounded change, on equipment change).
- state: none beyond on/off; optional cached bonus_bp for explain.
- explain: RULE_SPELL_TOGGLE; optional RULE_SPELL_CAP_CLAMP for stat clamp if system has caps.
@@END:B12.SPELL.SPELL_DEX_BOOST.C2@@

@@BEGIN:B12.SPELL.SPELL_DEX_BOOST.D0@@
@@END:B12.SPELLS.CANON.31@@
@@BEGIN:B12.SPELLS.DATA.08@@
[DATA] Params (DB_SPEC)
- base_bonus_bp_dex:BP:bp:int>=0 (10000=+100%)
@@END:B12.SPELL.SPELL_DEX_BOOST.D0@@

@@BEGIN:B12.SPELL.SPELL_DEX_BOOST.Q0@@
@@END:B12.SPELLS.DATA.08@@
@@BEGIN:B12.SPELLS.QA.06@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ExactFloor: StatFinal uses floor_div, no float.
- T07 DisableInstant: toggle off removes bonus immediately.
- T08 EnvMult: poor ground scales bonus down via env_mult.
- T09 StackPolicy: UNIQUE_BY_SPELLID rejects second instance.
- T10 DeterministicRecompute: repeated recompute yields same value.
@@END:B12.SPELL.SPELL_DEX_BOOST.Q0@@

@@BEGIN:B12.SPELL.SPELL_VIT_BOOST.C0@@
SPELL::SPELL_VIT_BOOST
@@END:B12.SPELLS.QA.06@@
@@BEGIN:B12.SPELLS.CANON.32@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_VIT_BOOST.C0@@

@@BEGIN:B12.SPELL.SPELL_VIT_BOOST.C1@@
@@END:B12.SPELLS.CANON.32@@
@@BEGIN:B12.SPELLS.CANON.33@@
[CANON] Math + Rounding
- bonus_bp:int = scaled_strength_bp(base_bonus_bp_vit).
- StatFinal = floor_div(StatBase * (10000 + bonus_bp_total), 10000).
- If multiple sources allowed (policy MULTI_INSTANCE_ADD), bonuses sum in bp; else UNIQUE_BY_SPELLID.
- Disable: on off or grounded=false => bonus_bp=0 (StatFinal recomputed).
@@END:B12.SPELL.SPELL_VIT_BOOST.C1@@

@@BEGIN:B12.SPELL.SPELL_VIT_BOOST.C2@@
@@END:B12.SPELLS.CANON.33@@
@@BEGIN:B12.SPELLS.CANON.34@@
[CANON] Runtime wiring
- hooks: derived-stats recompute (on toggle, on grounded change, on equipment change).
- state: none beyond on/off; optional cached bonus_bp for explain.
- explain: RULE_SPELL_TOGGLE; optional RULE_SPELL_CAP_CLAMP for stat clamp if system has caps.
@@END:B12.SPELL.SPELL_VIT_BOOST.C2@@

@@BEGIN:B12.SPELL.SPELL_VIT_BOOST.D0@@
@@END:B12.SPELLS.CANON.34@@
@@BEGIN:B12.SPELLS.DATA.09@@
[DATA] Params (DB_SPEC)
- base_bonus_bp_vit:BP:bp:int>=0 (10000=+100%)
@@END:B12.SPELL.SPELL_VIT_BOOST.D0@@

@@BEGIN:B12.SPELL.SPELL_VIT_BOOST.Q0@@
@@END:B12.SPELLS.DATA.09@@
@@BEGIN:B12.SPELLS.QA.07@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ExactFloor: StatFinal uses floor_div, no float.
- T07 DisableInstant: toggle off removes bonus immediately.
- T08 EnvMult: poor ground scales bonus down via env_mult.
- T09 StackPolicy: UNIQUE_BY_SPELLID rejects second instance.
- T10 DeterministicRecompute: repeated recompute yields same value.
@@END:B12.SPELL.SPELL_VIT_BOOST.Q0@@

@@BEGIN:B12.SPELL.SPELL_AURA_SIGHT.C0@@
SPELL::SPELL_AURA_SIGHT
@@END:B12.SPELLS.QA.07@@
@@BEGIN:B12.SPELLS.CANON.35@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true (special: effect suspended if grounded=false)
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_AURA_SIGHT.C0@@

@@BEGIN:B12.SPELL.SPELL_AURA_SIGHT.C1@@
@@END:B12.SPELLS.CANON.35@@
@@BEGIN:B12.SPELLS.CANON.36@@
[CANON] Math + Rounding
- range_m:int = scaled_range(base_range_m=10).
- aura_contrast_int:int = scaled_strength_int(base_aura_contrast_int).
- UI-only: render living vs non-living aura with contrast scaling.
@@END:B12.SPELL.SPELL_AURA_SIGHT.C1@@

@@BEGIN:B12.SPELL.SPELL_AURA_SIGHT.C2@@
@@END:B12.SPELLS.CANON.36@@
@@BEGIN:B12.SPELLS.CANON.37@@
[CANON] Runtime wiring
- hooks: perception overlay; no gameplay mutation.
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE only (optional).
@@END:B12.SPELL.SPELL_AURA_SIGHT.C2@@

@@BEGIN:B12.SPELL.SPELL_AURA_SIGHT.D0@@
@@END:B12.SPELLS.CANON.37@@
@@BEGIN:B12.SPELLS.DATA.10@@
[DATA] Params (DB_SPEC)
- base_range_m:METER_INT:int=10
- base_aura_contrast_int:INT:int>=0
@@END:B12.SPELL.SPELL_AURA_SIGHT.D0@@

@@BEGIN:B12.SPELL.SPELL_AURA_SIGHT.Q0@@
@@END:B12.SPELLS.DATA.10@@
@@BEGIN:B12.SPELLS.QA.08@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GroundedRequired: grounded=false => aura overlay disabled.
- T07 RangeScales: range increases with power/Q and env_mult.
- T08 NoGameplay: no changes to damage/loot/etc.
- T09 ToggleIdempotent: duplicate toggle event -> no double side effects.
- T10 StableTargetList: if overlay lists entities, stable order by entity_id asc.
@@END:B12.SPELL.SPELL_AURA_SIGHT.Q0@@

@@BEGIN:B12.SPELL.SPELL_NIGHT_VISION.C0@@
SPELL::SPELL_NIGHT_VISION
@@END:B12.SPELLS.QA.08@@
@@BEGIN:B12.SPELLS.CANON.38@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_NIGHT_VISION.C0@@

@@BEGIN:B12.SPELL.SPELL_NIGHT_VISION.C1@@
@@END:B12.SPELLS.CANON.38@@
@@BEGIN:B12.SPELLS.CANON.39@@
[CANON] Math + Rounding
- power_level_policy=FIXED_100 (power_level_bp=10000).
- range fixed: range_m=base_range_m=50 (range_policy=FIXED).
- vision_clarity_int = scaled_strength_int(base_clarity_int).
- daylight penalty: if env_light_level >= DAYLIGHT_THRESHOLD (data) and spell active => apply status_tag 'status:BLINDNESS' while active.
@@END:B12.SPELL.SPELL_NIGHT_VISION.C1@@

@@BEGIN:B12.SPELL.SPELL_NIGHT_VISION.C2@@
@@END:B12.SPELLS.CANON.39@@
@@BEGIN:B12.SPELLS.CANON.40@@
[CANON] Runtime wiring
- hooks: vision shader/visibility, status apply/remove for blindness (if status system absent => V_NEXT gate).
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE; optional RULE_STATUS_APPLY/REMOVE (existing canon).
@@END:B12.SPELL.SPELL_NIGHT_VISION.C2@@

@@BEGIN:B12.SPELL.SPELL_NIGHT_VISION.D0@@
@@END:B12.SPELLS.CANON.40@@
@@BEGIN:B12.SPELLS.DATA.11@@
[DATA] Params (DB_SPEC)
- base_range_m:METER_INT:int=50
- base_clarity_int:INT:int>=0
- daylight_threshold_int:INT:int>=0 (env query units, data)
- blindness_status_tag:string='status:BLINDNESS' (data mapping)
@@END:B12.SPELL.SPELL_NIGHT_VISION.D0@@

@@BEGIN:B12.SPELL.SPELL_NIGHT_VISION.Q0@@
@@END:B12.SPELLS.DATA.11@@
@@BEGIN:B12.SPELLS.QA.09@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 PowerFixed: UI cannot set power !=100%.
- T07 RangeFixed: range always 50m.
- T08 DaylightBlindness: in daylight -> blindness status present; in darkness -> absent.
- T09 NoBlindnessOnPause: grounded=false => effect 0, blindness removed.
- T10 DeterministicEnv: blindness depends only on deterministic env_light query.
@@END:B12.SPELL.SPELL_NIGHT_VISION.Q0@@

@@BEGIN:B12.SPELL.SPELL_IDENTIFY.C0@@
SPELL::SPELL_IDENTIFY
@@END:B12.SPELLS.QA.09@@
@@BEGIN:B12.SPELLS.CANON.41@@
[CANON] Classification
- maintained=true
- binding: TARGET
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: SCAN_PROGRESS
- rng_ops: (none)
@@END:B12.SPELL.SPELL_IDENTIFY.C0@@

@@BEGIN:B12.SPELL.SPELL_IDENTIFY.C1@@
@@END:B12.SPELLS.CANON.41@@
@@BEGIN:B12.SPELLS.CANON.42@@
[CANON] Math + Rounding
- range_m:int = scaled_range(base_range_m=10).
- required_ticks10s:int = ceil_div(base_scan_ticks10s*10000, PotencyMult_bp(Q)).
- detail_level_int:int = scaled_strength_int(base_detail_level_int).
- scan progress: progress_bp += env_mult_bp per 10s tick while target in range; completion at required_ticks10s*10000.
- IMPORTANT: spell does NOT set is_identified=true and does NOT remove UNIDENTIFIED. It only produces an analysis report (UI).
@@END:B12.SPELL.SPELL_IDENTIFY.C1@@

@@BEGIN:B12.SPELL.SPELL_IDENTIFY.C2@@
@@END:B12.SPELLS.CANON.42@@
@@BEGIN:B12.SPELLS.CANON.43@@
[CANON] Runtime wiring
- hooks: ROUND_END/TIME_ADVANCE for progress, target distance check each tick.
- state fields: target_id, progress_bp:int (0..required*10000).
- completion event emits analysis report to UI/log; no inventory mutation.
- explain: RULE_SPELL_SCAN_PROGRESS; RULE_SPELL_TICK tick_kind='identify.scan'.
@@END:B12.SPELL.SPELL_IDENTIFY.C2@@

@@BEGIN:B12.SPELL.SPELL_IDENTIFY.D0@@
@@END:B12.SPELLS.CANON.43@@
@@BEGIN:B12.SPELLS.DATA.12@@
[DATA] Params (DB_SPEC)
- base_range_m:METER_INT:int=10
- base_scan_ticks10s:TICKS10S:int>=1
- base_detail_level_int:INT:int>=0
@@END:B12.SPELL.SPELL_IDENTIFY.D0@@

@@BEGIN:B12.SPELL.SPELL_IDENTIFY.Q0@@
@@END:B12.SPELLS.DATA.12@@
@@BEGIN:B12.SPELLS.QA.10@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 NoIdentifyMutation: after completion, item.is_identified unchanged.
- T07 ResetOnBreak: if target out of range or toggle off => progress resets to 0.
- T08 EnvMultProgress: poor ground slows progress deterministically.
- T09 DeterministicComplete: same time steps -> completes on same tick.
- T10 StableReport: revealed fields depend only on detail_level and deterministic item data.
@@END:B12.SPELL.SPELL_IDENTIFY.Q0@@

@@BEGIN:B12.SPELL.SPELL_ORE_SCAN.C0@@
SPELL::SPELL_ORE_SCAN
@@END:B12.SPELLS.QA.10@@
@@BEGIN:B12.SPELLS.CANON.44@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: SCAN_PROGRESS
- rng_ops: (none)
@@END:B12.SPELL.SPELL_ORE_SCAN.C0@@

@@BEGIN:B12.SPELL.SPELL_ORE_SCAN.C1@@
@@END:B12.SPELLS.CANON.44@@
@@BEGIN:B12.SPELLS.CANON.45@@
[CANON] Math + Rounding
- range_m:int = scaled_range(base_range_m=10).
- detect_ticks10s:int = ceil_div(base_detect_ticks10s*10000, PotencyMult_bp(Q)).
- refine_ticks10s:int = ceil_div(base_refine_ticks10s*10000, PotencyMult_bp(Q)).
- resolution_int:int = scaled_strength_int(base_ore_resolution_int).
- This spell reveals ore nodes from world data. It does not create ore.
- Vein behavior is a property of world ore distribution (deterministic, seeded by world_seed).
@@END:B12.SPELL.SPELL_ORE_SCAN.C1@@

@@BEGIN:B12.SPELL.SPELL_ORE_SCAN.C2@@
@@END:B12.SPELLS.CANON.45@@
@@BEGIN:B12.SPELLS.CANON.46@@
[CANON] Runtime wiring
- hooks: TIME_ADVANCE only (out of combat).
- state: stage (0/1/2), progress_bp:int, last_result_hash:u64 (optional).
- feature gate: WORLD_SCAN (if gate off => spell not spawnable, enable rejects).
@@END:B12.SPELL.SPELL_ORE_SCAN.C2@@

@@BEGIN:B12.SPELL.SPELL_ORE_SCAN.D0@@
@@END:B12.SPELLS.CANON.46@@
@@BEGIN:B12.SPELLS.DATA.13@@
[DATA] Params (DB_SPEC)
- feature_gate:string='WORLD_SCAN'
- base_range_m:METER_INT:int=10
- base_detect_ticks10s:TICKS10S:int>=1
- base_refine_ticks10s:TICKS10S:int>=1
- base_ore_resolution_int:INT:int>=0
@@END:B12.SPELL.SPELL_ORE_SCAN.D0@@

@@BEGIN:B12.SPELL.SPELL_ORE_SCAN.Q0@@
@@END:B12.SPELLS.DATA.13@@
@@BEGIN:B12.SPELLS.QA.11@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: if WORLD_SCAN disabled => enable rejects.
- T07 StageProgress: after detect stage -> 'has ore yes/no'; after refine -> type/richness fields appear.
- T08 ResetOnStop: toggle off => progress resets to 0 and stage resets.
- T09 NoWorldMutation: no changes to ore nodes or inventory.
- T10 DeterministicWorldQuery: same world_seed+pos -> same ore query result.
@@END:B12.SPELL.SPELL_ORE_SCAN.Q0@@

@@BEGIN:B12.SPELL.SPELL_LUCK_BOOST.C0@@
SPELL::SPELL_LUCK_BOOST
@@END:B12.SPELLS.QA.11@@
@@BEGIN:B12.SPELLS.CANON.47@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_LUCK_BOOST.C0@@

@@BEGIN:B12.SPELL.SPELL_LUCK_BOOST.C1@@
@@END:B12.SPELLS.CANON.47@@
@@BEGIN:B12.SPELLS.CANON.48@@
[CANON] Math + Rounding
- bonus_bp:int = scaled_strength_bp(base_bonus_bp_luck).
- StatFinal = floor_div(StatBase * (10000 + bonus_bp_total), 10000).
- If multiple sources allowed (policy MULTI_INSTANCE_ADD), bonuses sum in bp; else UNIQUE_BY_SPELLID.
- Disable: on off or grounded=false => bonus_bp=0 (StatFinal recomputed).
@@END:B12.SPELL.SPELL_LUCK_BOOST.C1@@

@@BEGIN:B12.SPELL.SPELL_LUCK_BOOST.C2@@
@@END:B12.SPELLS.CANON.48@@
@@BEGIN:B12.SPELLS.CANON.49@@
[CANON] Runtime wiring
- hooks: derived-stats recompute (on toggle, on grounded change, on equipment change).
- state: none beyond on/off; optional cached bonus_bp for explain.
- explain: RULE_SPELL_TOGGLE; optional RULE_SPELL_CAP_CLAMP for stat clamp if system has caps.
@@END:B12.SPELL.SPELL_LUCK_BOOST.C2@@

@@BEGIN:B12.SPELL.SPELL_LUCK_BOOST.D0@@
@@END:B12.SPELLS.CANON.49@@
@@BEGIN:B12.SPELLS.DATA.14@@
[DATA] Params (DB_SPEC)
- base_bonus_bp_luck:BP:bp:int>=0 (10000=+100%)
@@END:B12.SPELL.SPELL_LUCK_BOOST.D0@@

@@BEGIN:B12.SPELL.SPELL_LUCK_BOOST.Q0@@
@@END:B12.SPELLS.DATA.14@@
@@BEGIN:B12.SPELLS.QA.12@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ExactFloor: StatFinal uses floor_div, no float.
- T07 DisableInstant: toggle off removes bonus immediately.
- T08 EnvMult: poor ground scales bonus down via env_mult.
- T09 StackPolicy: UNIQUE_BY_SPELLID rejects second instance.
- T10 DeterministicRecompute: repeated recompute yields same value.
@@END:B12.SPELL.SPELL_LUCK_BOOST.Q0@@

@@BEGIN:B12.SPELL.SPELL_IRON_SKIN.C0@@
SPELL::SPELL_IRON_SKIN
@@END:B12.SPELLS.QA.12@@
@@BEGIN:B12.SPELLS.CANON.50@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_IRON_SKIN.C0@@

@@BEGIN:B12.SPELL.SPELL_IRON_SKIN.C1@@
@@END:B12.SPELLS.CANON.50@@
@@BEGIN:B12.SPELLS.CANON.51@@
[CANON] Math + Rounding
- protection_level_int = scaled_strength_int(base_protection_level_int).
- immunities: while active, status apply attempts for tags in iron_skin_immunity_status_tags_any are rejected (fail-fast, no RNG).
- speed_penalty_bp = apply_bp_floor(base_speed_penalty_bp, power_level_bp) (no potency scaling per spec).
- weight_penalty_bp = apply_bp_floor(base_weight_penalty_bp, power_level_bp).
- stealth forbidden while active (hard rule).
@@END:B12.SPELL.SPELL_IRON_SKIN.C1@@

@@BEGIN:B12.SPELL.SPELL_IRON_SKIN.C2@@
@@END:B12.SPELLS.CANON.51@@
@@BEGIN:B12.SPELLS.CANON.52@@
[CANON] Runtime wiring
- hooks: status apply validation, movement speed calc, encumbrance calc, stealth gate.
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE; optional RULE_SPELL_CAP_CLAMP on speed/weight multipliers.
@@END:B12.SPELL.SPELL_IRON_SKIN.C2@@

@@BEGIN:B12.SPELL.SPELL_IRON_SKIN.D0@@
@@END:B12.SPELLS.CANON.52@@
@@BEGIN:B12.SPELLS.DATA.15@@
[DATA] Params (DB_SPEC)
- base_protection_level_int:INT:int>=0
- base_speed_penalty_bp:BP:bp:int>=0
- base_weight_penalty_bp:BP:bp:int>=0
- iron_skin_immunity_status_tags_any: string[] (status:* allowlist)
@@END:B12.SPELL.SPELL_IRON_SKIN.D0@@

@@BEGIN:B12.SPELL.SPELL_IRON_SKIN.Q0@@
@@END:B12.SPELLS.DATA.15@@
@@BEGIN:B12.SPELLS.QA.13@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 StatusReject: immune statuses do not apply while active.
- T07 SpeedPenalty: speed mult reduced deterministically; removed on off.
- T08 StealthForbidden: stealth attempts reject while active.
- T09 GroundedPause: grounded=false => immunities and penalties are suspended.
- T10 NoDamageChange: does not alter damage pipeline directly.
@@END:B12.SPELL.SPELL_IRON_SKIN.Q0@@

@@BEGIN:B12.SPELL.SPELL_ACCURACY.C0@@
SPELL::SPELL_ACCURACY
@@END:B12.SPELLS.QA.13@@
@@BEGIN:B12.SPELLS.CANON.53@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: true
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_ACCURACY.C0@@

@@BEGIN:B12.SPELL.SPELL_ACCURACY.C1@@
@@END:B12.SPELLS.CANON.53@@
@@BEGIN:B12.SPELLS.CANON.54@@
[CANON] Math + Rounding
- damage_bonus_bp = scaled_strength_bp(base_damage_bonus_bp).
- Applied to outgoing attack base damage BEFORE target defenses:
  damage_out = apply_bp_floor(damage_base, 10000 + damage_bonus_bp).
- Then target pipeline: shield -> armor -> barrier -> HP.
@@END:B12.SPELL.SPELL_ACCURACY.C1@@

@@BEGIN:B12.SPELL.SPELL_ACCURACY.C2@@
@@END:B12.SPELLS.CANON.54@@
@@BEGIN:B12.SPELLS.CANON.55@@
[CANON] Runtime wiring
- hooks: HIT_RESOLVE / damage compute (attacker-side).
- ordering: modify DamageBase before target defense stage.
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE; RULE_ATTACK_DAMAGE_MOD meta{spell_id, bonus_bp} if such rule exists; else fold into existing explain for attack.
@@END:B12.SPELL.SPELL_ACCURACY.C2@@

@@BEGIN:B12.SPELL.SPELL_ACCURACY.D0@@
@@END:B12.SPELLS.CANON.55@@
@@BEGIN:B12.SPELLS.DATA.16@@
[DATA] Params (DB_SPEC)
- base_damage_bonus_bp:BP:bp:int>=0
@@END:B12.SPELL.SPELL_ACCURACY.D0@@

@@BEGIN:B12.SPELL.SPELL_ACCURACY.Q0@@
@@END:B12.SPELLS.DATA.16@@
@@BEGIN:B12.SPELLS.QA.14@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 PreDefenseOnly: bonus applied before shield/armor/barrier.
- T07 DisableInstant: off removes bonus.
- T08 NoRNG: does not change hit chance unless separate system exists.
- T09 EnvMult: poor ground reduces bonus.
- T10 DeterministicRound: same inputs -> same damage_out.
@@END:B12.SPELL.SPELL_ACCURACY.Q0@@

@@BEGIN:B12.SPELL.SPELL_MISTFORM.C0@@
SPELL::SPELL_MISTFORM
@@END:B12.SPELLS.QA.14@@
@@BEGIN:B12.SPELLS.CANON.56@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_MISTFORM.C0@@

@@BEGIN:B12.SPELL.SPELL_MISTFORM.C1@@
@@END:B12.SPELLS.CANON.56@@
@@BEGIN:B12.SPELLS.CANON.57@@
[CANON] Math + Rounding
- speed_bonus_bp = scaled_strength_bp(base_speed_bonus_bp).
- action restrictions: while active, actor cannot perform attacks and cannot start non-move actions (move allowed).
- damage model aligns with B08: HPDamage is not forced to 0. Instead, per round cap applies:
  - mistform_hp_taken_this_round:int tracked per actor per combat round.
  - cap_per_round_hp:int is [DATA] MISTFORM_HP_CAP_PER_ROUND.
  - final_hp_damage = min(hp_damage_raw, max(0, cap_per_round_hp - mistform_hp_taken_this_round)).
  - then mistform_hp_taken_this_round += final_hp_damage.
- microdamage is not cancelled; it is still capped by the per-round cap.
@@END:B12.SPELL.SPELL_MISTFORM.C1@@

@@BEGIN:B12.SPELL.SPELL_MISTFORM.C2@@
@@END:B12.SPELLS.CANON.57@@
@@BEGIN:B12.SPELLS.CANON.58@@
[CANON] Runtime wiring
- hooks: action validation (deny), movement speed calc, DMG_PIPELINE cap stage after barrier and before applying HP.
- state: mistform_hp_taken_this_round:int (combat-only, reset at ROUND_START/ROUND_END per canon).
- explain: RULE_SPELL_TOGGLE; RULE_DMG_CAP meta{spell_id, cap_hp, before, after}.
@@END:B12.SPELL.SPELL_MISTFORM.C2@@

@@BEGIN:B12.SPELL.SPELL_MISTFORM.D0@@
@@END:B12.SPELLS.CANON.58@@
@@BEGIN:B12.SPELLS.DATA.17@@
[DATA] Params (DB_SPEC)
- base_speed_bonus_bp:BP:bp:int>=0
- mistform_hp_cap_per_round_hp:INT:HP:int>=0 (DATA balance)
@@END:B12.SPELL.SPELL_MISTFORM.D0@@

@@BEGIN:B12.SPELL.SPELL_MISTFORM.Q0@@
@@END:B12.SPELLS.DATA.17@@
@@BEGIN:B12.SPELLS.QA.15@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ActionDenied: attempt attack while active -> PRECONDITION_FAILED.
- T07 CapWorks: incoming damage reduced only by cap, not set to 0.
- T08 CapReset: cap resets deterministically each combat round.
- T09 MicrodamageStill: microdamage can produce 1 hp but still respects cap.
- T10 GroundedPause: grounded=false => restrictions and speed bonus suspended.
@@END:B12.SPELL.SPELL_MISTFORM.Q0@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_DOWN.C0@@
SPELL::SPELL_WEIGHT_DOWN
@@END:B12.SPELLS.QA.15@@
@@BEGIN:B12.SPELLS.CANON.59@@
[CANON] Classification
- maintained=true
- binding: ITEM_BOUND
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_WEIGHT_DOWN.C0@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_DOWN.C1@@
@@END:B12.SPELLS.CANON.59@@
@@BEGIN:B12.SPELLS.CANON.60@@
[CANON] Math + Rounding
- reduction_bp = scaled_strength_bp(base_weight_reduction_bp).
- Applies only to the bound item instance while it is owned by the actor (inventory or equipped).
- weight_final_g = max(0, apply_bp_floor(weight_base_g, 10000 - reduction_bp)).
- Auto-off: if item not owned by actor => spell auto disables (deterministic).
@@END:B12.SPELL.SPELL_WEIGHT_DOWN.C1@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_DOWN.C2@@
@@END:B12.SPELLS.CANON.60@@
@@BEGIN:B12.SPELLS.CANON.61@@
[CANON] Runtime wiring
- hooks: inventory change (ownership transfer/drop), encumbrance calc.
- state: bound_item_instance_id, on/off.
- explain: RULE_SPELL_TOGGLE; RULE_SPELL_PRECONDITION_FAIL if enable without owning item.
@@END:B12.SPELL.SPELL_WEIGHT_DOWN.C2@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_DOWN.D0@@
@@END:B12.SPELLS.CANON.61@@
@@BEGIN:B12.SPELLS.DATA.18@@
[DATA] Params (DB_SPEC)
- base_weight_reduction_bp:BP:bp:int in [0..10000]
@@END:B12.SPELL.SPELL_WEIGHT_DOWN.D0@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_DOWN.Q0@@
@@END:B12.SPELLS.DATA.18@@
@@BEGIN:B12.SPELLS.QA.16@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ItemBoundOnly: affects only the stone carrier item.
- T07 AutoOffOnDrop: dropping item disables spell; weight returns instantly.
- T08 NoNegativeWeight: clamp to >=0.
- T09 MultipleItemsAllowed: stack_policy=ITEM_BOUND allows multiple on different items.
- T10 DeterministicOwnership: transfer triggers auto-off once.
@@END:B12.SPELL.SPELL_WEIGHT_DOWN.Q0@@

@@BEGIN:B12.SPELL.SPELL_VAMPIRISM.C0@@
SPELL::SPELL_VAMPIRISM
@@END:B12.SPELLS.QA.16@@
@@BEGIN:B12.SPELLS.CANON.62@@
[CANON] Classification
- maintained=true
- binding: WEAPON_BOUND
- offensive: true
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: ON_HIT
- rng_ops: (none)
@@END:B12.SPELL.SPELL_VAMPIRISM.C0@@

@@BEGIN:B12.SPELL.SPELL_VAMPIRISM.C1@@
@@END:B12.SPELLS.CANON.62@@
@@BEGIN:B12.SPELLS.CANON.63@@
[CANON] Math + Rounding
- heal_hp_fixed:int = 1 (not scaled).
- cooldown_ticks10s:int = ceil_div(base_cooldown_ticks10s*10000, PotencyMult_bp(Q)).
- Trigger condition: on successful attack where final_hp_damage_to_target >= 1 (after all defenses and caps).
- If cooldown_remaining_ticks10s>0 => no trigger; else heal owner by 1 HP and set cooldown_remaining_ticks10s=cooldown_ticks10s.
@@END:B12.SPELL.SPELL_VAMPIRISM.C1@@

@@BEGIN:B12.SPELL.SPELL_VAMPIRISM.C2@@
@@END:B12.SPELLS.CANON.63@@
@@BEGIN:B12.SPELLS.CANON.64@@
[CANON] Runtime wiring
- hooks: HIT_RESOLVE (after final HP damage computed), ROUND_END/TIME_ADVANCE to decrement cooldown by ticks.
- state: cooldown_remaining_ticks10s:int (>=0).
- explain: RULE_SPELL_PROC op_id='vampirism.heal' (success true/false) + heal delta.
@@END:B12.SPELL.SPELL_VAMPIRISM.C2@@

@@BEGIN:B12.SPELL.SPELL_VAMPIRISM.D0@@
@@END:B12.SPELLS.CANON.64@@
@@BEGIN:B12.SPELLS.DATA.19@@
[DATA] Params (DB_SPEC)
- base_cooldown_ticks10s:TICKS10S:int>=1
- note: heal fixed to 1 HP by canon of this spell card.
@@END:B12.SPELL.SPELL_VAMPIRISM.D0@@

@@BEGIN:B12.SPELL.SPELL_VAMPIRISM.Q0@@
@@END:B12.SPELLS.DATA.19@@
@@BEGIN:B12.SPELLS.QA.17@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 TriggerOnlyOnHPDamage: barrier-only hits do not heal.
- T07 CooldownWorks: cannot heal again until cooldown expires.
- T08 DeterministicCooldown: cooldown reduces via per10s ticks only.
- T09 WeaponBound: only attacks with bound weapon can trigger.
- T10 NoScale: heal amount independent of Q/power.
@@END:B12.SPELL.SPELL_VAMPIRISM.Q0@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_UP.C0@@
SPELL::SPELL_WEIGHT_UP
@@END:B12.SPELLS.QA.17@@
@@BEGIN:B12.SPELLS.CANON.65@@
[CANON] Classification
- maintained=true
- binding: ITEM_BOUND
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_WEIGHT_UP.C0@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_UP.C1@@
@@END:B12.SPELLS.CANON.65@@
@@BEGIN:B12.SPELLS.CANON.66@@
[CANON] Math + Rounding
- increase_bp = scaled_strength_bp(base_weight_increase_bp).
- weight_final_g = apply_bp_ceil(weight_base_g, 10000 + increase_bp).
- Auto-off on transfer/drop (same as SPELL_WEIGHT_DOWN).
@@END:B12.SPELL.SPELL_WEIGHT_UP.C1@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_UP.C2@@
@@END:B12.SPELLS.CANON.66@@
@@BEGIN:B12.SPELLS.CANON.67@@
[CANON] Runtime wiring
- hooks: inventory change, encumbrance calc.
- state: bound_item_instance_id, on/off.
- explain: RULE_SPELL_TOGGLE.
@@END:B12.SPELL.SPELL_WEIGHT_UP.C2@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_UP.D0@@
@@END:B12.SPELLS.CANON.67@@
@@BEGIN:B12.SPELLS.DATA.20@@
[DATA] Params (DB_SPEC)
- base_weight_increase_bp:BP:bp:int>=0
@@END:B12.SPELL.SPELL_WEIGHT_UP.D0@@

@@BEGIN:B12.SPELL.SPELL_WEIGHT_UP.Q0@@
@@END:B12.SPELLS.DATA.20@@
@@BEGIN:B12.SPELLS.QA.18@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ItemBoundOnly: affects only bound item weight.
- T07 AutoOffOnDrop: drop disables and weight returns.
- T08 CeilApplied: uses apply_bp_ceil for weight increase.
- T09 MultipleItemsAllowed: ITEM_BOUND allows multiple on different items.
- T10 DeterministicEncumbrance: carried weight recalculates deterministically.
@@END:B12.SPELL.SPELL_WEIGHT_UP.Q0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_STR.C0@@
SPELL::SPELL_STEAL_STR
@@END:B12.SPELLS.QA.18@@
@@BEGIN:B12.SPELLS.CANON.68@@
[CANON] Classification
- maintained=true
- binding: WEAPON_BOUND
- offensive: true
- requires_grounded: true (special: if grounded=false, bonus=0 but stacks preserved)
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: ON_HIT
- rng_ops: (none)
@@END:B12.SPELL.SPELL_STEAL_STR.C0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_STR.C1@@
@@END:B12.SPELLS.CANON.68@@
@@BEGIN:B12.SPELLS.CANON.69@@
[CANON] Math + Rounding
- stack_bonus_bp = scaled_strength_bp(base_stack_bonus_bp_str).
- max_stacks:int = round_half_up_div(base_max_stacks_int * PotencyMult_bp(Q), 10000).
- On each successful hit with the bound weapon: if stacks < max_stacks => stacks += 1.
- total_bonus_bp = stacks * stack_bonus_bp.
- StatFinal = floor_div(StatBase * (10000 + total_bonus_bp_effective), 10000).
- grounded=false => total_bonus_bp_effective=0, but stacks counter is NOT cleared.
- toggle off => stacks cleared to 0.
@@END:B12.SPELL.SPELL_STEAL_STR.C1@@

@@BEGIN:B12.SPELL.SPELL_STEAL_STR.C2@@
@@END:B12.SPELLS.CANON.69@@
@@BEGIN:B12.SPELLS.CANON.70@@
[CANON] Runtime wiring
- hooks: HIT_RESOLVE to increment stacks; derived stats recompute; grounded gate.
- state: stacks:int, max_stacks:int (cached optional).
- explain: RULE_SPELL_PROC op_id='steal_stack.add' + stacks_after.
@@END:B12.SPELL.SPELL_STEAL_STR.C2@@

@@BEGIN:B12.SPELL.SPELL_STEAL_STR.D0@@
@@END:B12.SPELLS.CANON.70@@
@@BEGIN:B12.SPELLS.DATA.21@@
[DATA] Params (DB_SPEC)
- base_stack_bonus_bp_str:BP:bp:int>=0
- base_max_stacks_int:INT:int>=0
@@END:B12.SPELL.SPELL_STEAL_STR.D0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_STR.Q0@@
@@END:B12.SPELLS.DATA.21@@
@@BEGIN:B12.SPELLS.QA.19@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 StackCap: cannot exceed max_stacks.
- T07 ResetOnOff: toggle off clears stacks.
- T08 PauseKeepsStacks: grounded=false keeps stacks but bonus=0.
- T09 WeaponBound: only bound weapon hits add stacks.
- T10 DeterministicHitCounting: hit_seq in scope_id prevents double counting.
@@END:B12.SPELL.SPELL_STEAL_STR.Q0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_AGI.C0@@
SPELL::SPELL_STEAL_AGI
@@END:B12.SPELLS.QA.19@@
@@BEGIN:B12.SPELLS.CANON.71@@
[CANON] Classification
- maintained=true
- binding: WEAPON_BOUND
- offensive: true
- requires_grounded: true (special: if grounded=false, bonus=0 but stacks preserved)
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: ON_HIT
- rng_ops: (none)
@@END:B12.SPELL.SPELL_STEAL_AGI.C0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_AGI.C1@@
@@END:B12.SPELLS.CANON.71@@
@@BEGIN:B12.SPELLS.CANON.72@@
[CANON] Math + Rounding
- stack_bonus_bp = scaled_strength_bp(base_stack_bonus_bp_agi).
- max_stacks:int = round_half_up_div(base_max_stacks_int * PotencyMult_bp(Q), 10000).
- On each successful hit with the bound weapon: if stacks < max_stacks => stacks += 1.
- total_bonus_bp = stacks * stack_bonus_bp.
- StatFinal = floor_div(StatBase * (10000 + total_bonus_bp_effective), 10000).
- grounded=false => total_bonus_bp_effective=0, but stacks counter is NOT cleared.
- toggle off => stacks cleared to 0.
@@END:B12.SPELL.SPELL_STEAL_AGI.C1@@

@@BEGIN:B12.SPELL.SPELL_STEAL_AGI.C2@@
@@END:B12.SPELLS.CANON.72@@
@@BEGIN:B12.SPELLS.CANON.73@@
[CANON] Runtime wiring
- hooks: HIT_RESOLVE to increment stacks; derived stats recompute; grounded gate.
- state: stacks:int, max_stacks:int (cached optional).
- explain: RULE_SPELL_PROC op_id='steal_stack.add' + stacks_after.
@@END:B12.SPELL.SPELL_STEAL_AGI.C2@@

@@BEGIN:B12.SPELL.SPELL_STEAL_AGI.D0@@
@@END:B12.SPELLS.CANON.73@@
@@BEGIN:B12.SPELLS.DATA.22@@
[DATA] Params (DB_SPEC)
- base_stack_bonus_bp_agi:BP:bp:int>=0
- base_max_stacks_int:INT:int>=0
@@END:B12.SPELL.SPELL_STEAL_AGI.D0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_AGI.Q0@@
@@END:B12.SPELLS.DATA.22@@
@@BEGIN:B12.SPELLS.QA.20@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 StackCap: cannot exceed max_stacks.
- T07 ResetOnOff: toggle off clears stacks.
- T08 PauseKeepsStacks: grounded=false keeps stacks but bonus=0.
- T09 WeaponBound: only bound weapon hits add stacks.
- T10 DeterministicHitCounting: hit_seq in scope_id prevents double counting.
@@END:B12.SPELL.SPELL_STEAL_AGI.Q0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_SPD.C0@@
SPELL::SPELL_STEAL_SPD
@@END:B12.SPELLS.QA.20@@
@@BEGIN:B12.SPELLS.CANON.74@@
[CANON] Classification
- maintained=true
- binding: WEAPON_BOUND
- offensive: true
- requires_grounded: true (special: if grounded=false, bonus=0 but stacks preserved)
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: ON_HIT
- rng_ops: (none)
@@END:B12.SPELL.SPELL_STEAL_SPD.C0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_SPD.C1@@
@@END:B12.SPELLS.CANON.74@@
@@BEGIN:B12.SPELLS.CANON.75@@
[CANON] Math + Rounding
- stack_bonus_bp = scaled_strength_bp(base_stack_bonus_bp_spd).
- max_stacks:int = round_half_up_div(base_max_stacks_int * PotencyMult_bp(Q), 10000).
- On each successful hit with the bound weapon: if stacks < max_stacks => stacks += 1.
- total_bonus_bp = stacks * stack_bonus_bp.
- StatFinal = floor_div(StatBase * (10000 + total_bonus_bp_effective), 10000).
- grounded=false => total_bonus_bp_effective=0, but stacks counter is NOT cleared.
- toggle off => stacks cleared to 0.
@@END:B12.SPELL.SPELL_STEAL_SPD.C1@@

@@BEGIN:B12.SPELL.SPELL_STEAL_SPD.C2@@
@@END:B12.SPELLS.CANON.75@@
@@BEGIN:B12.SPELLS.CANON.76@@
[CANON] Runtime wiring
- hooks: HIT_RESOLVE to increment stacks; derived stats recompute; grounded gate.
- state: stacks:int, max_stacks:int (cached optional).
- explain: RULE_SPELL_PROC op_id='steal_stack.add' + stacks_after.
@@END:B12.SPELL.SPELL_STEAL_SPD.C2@@

@@BEGIN:B12.SPELL.SPELL_STEAL_SPD.D0@@
@@END:B12.SPELLS.CANON.76@@
@@BEGIN:B12.SPELLS.DATA.23@@
[DATA] Params (DB_SPEC)
- base_stack_bonus_bp_spd:BP:bp:int>=0
- base_max_stacks_int:INT:int>=0
@@END:B12.SPELL.SPELL_STEAL_SPD.D0@@

@@BEGIN:B12.SPELL.SPELL_STEAL_SPD.Q0@@
@@END:B12.SPELLS.DATA.23@@
@@BEGIN:B12.SPELLS.QA.21@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 StackCap: cannot exceed max_stacks.
- T07 ResetOnOff: toggle off clears stacks.
- T08 PauseKeepsStacks: grounded=false keeps stacks but bonus=0.
- T09 WeaponBound: only bound weapon hits add stacks.
- T10 DeterministicHitCounting: hit_seq in scope_id prevents double counting.
@@END:B12.SPELL.SPELL_STEAL_SPD.Q0@@

@@BEGIN:B12.SPELL.SPELL_GEAR_CLEAN.C0@@
SPELL::SPELL_GEAR_CLEAN
@@END:B12.SPELLS.QA.21@@
@@BEGIN:B12.SPELLS.CANON.77@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: PER_10S
- rng_ops: (none)
@@END:B12.SPELL.SPELL_GEAR_CLEAN.C0@@

@@BEGIN:B12.SPELL.SPELL_GEAR_CLEAN.C1@@
@@END:B12.SPELLS.CANON.77@@
@@BEGIN:B12.SPELLS.CANON.78@@
[CANON] Math + Rounding
- clean_units_per_tick:int = scaled_strength_int(base_clean_units_per_tick).
- PER_10S: for each equipped item with dirt_value_int>0: dirt_value_int = max(0, dirt_value_int - clean_units_per_tick).
- If dirt subsystem absent => feature_gate='DIRT_SYSTEM' (spell disabled in MVP).
@@END:B12.SPELL.SPELL_GEAR_CLEAN.C1@@

@@BEGIN:B12.SPELL.SPELL_GEAR_CLEAN.C2@@
@@END:B12.SPELLS.CANON.78@@
@@BEGIN:B12.SPELLS.CANON.79@@
[CANON] Runtime wiring
- hooks: TIME_ADVANCE only (out of combat).
- state: none beyond on/off.
- explain: RULE_SPELL_TICK tick_kind='gear_clean.per10s'.
@@END:B12.SPELL.SPELL_GEAR_CLEAN.C2@@

@@BEGIN:B12.SPELL.SPELL_GEAR_CLEAN.D0@@
@@END:B12.SPELLS.CANON.79@@
@@BEGIN:B12.SPELLS.DATA.24@@
[DATA] Params (DB_SPEC)
- feature_gate:string='DIRT_SYSTEM'
- base_clean_units_per_tick:INT:int>=0
@@END:B12.SPELL.SPELL_GEAR_CLEAN.D0@@

@@BEGIN:B12.SPELL.SPELL_GEAR_CLEAN.Q0@@
@@END:B12.SPELLS.DATA.24@@
@@BEGIN:B12.SPELLS.QA.22@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: if DIRT_SYSTEM disabled => enable rejects.
- T07 EquippedOnly: only equipped items are cleaned.
- T08 ClampToZero: dirt never negative.
- T09 NoCombat: enable in combat rejects.
- T10 DeterministicPerItem: stable order by item_instance_id asc.
@@END:B12.SPELL.SPELL_GEAR_CLEAN.Q0@@

@@BEGIN:B12.SPELL.SPELL_GROUNDING.C0@@
SPELL::SPELL_GROUNDING
@@END:B12.SPELLS.QA.22@@
@@BEGIN:B12.SPELLS.CANON.80@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true (still requires grounded=true; this spell improves quality only)
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_GROUNDING.C0@@

@@BEGIN:B12.SPELL.SPELL_GROUNDING.C1@@
@@END:B12.SPELLS.CANON.80@@
@@BEGIN:B12.SPELLS.CANON.81@@
[CANON] Math + Rounding
- grounding_comp_bp = scaled_strength_bp(base_grounding_comp_bp).
- env_mult_bp for all spells = clamp_int(ground_quality_pct*100 + grounding_comp_bp, 0, 10000).
- This does not allow magic when grounded=false. It only compensates low ground quality when grounded=true.
@@END:B12.SPELL.SPELL_GROUNDING.C1@@

@@BEGIN:B12.SPELL.SPELL_GROUNDING.C2@@
@@END:B12.SPELLS.CANON.81@@
@@BEGIN:B12.SPELLS.CANON.82@@
[CANON] Runtime wiring
- hooks: env_mult computation used by all spells (central).
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE.
@@END:B12.SPELL.SPELL_GROUNDING.C2@@

@@BEGIN:B12.SPELL.SPELL_GROUNDING.D0@@
@@END:B12.SPELLS.CANON.82@@
@@BEGIN:B12.SPELLS.DATA.25@@
[DATA] Params (DB_SPEC)
- base_grounding_comp_bp:BP:bp:int>=0 (10000=+100 percentage points)
@@END:B12.SPELL.SPELL_GROUNDING.D0@@

@@BEGIN:B12.SPELL.SPELL_GROUNDING.Q0@@
@@END:B12.SPELLS.DATA.25@@
@@BEGIN:B12.SPELLS.QA.23@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 NoAirMagic: grounded=false still disables all effects.
- T07 EnvMultClamp: env_mult_bp clamped 0..10000.
- T08 AffectsAllSpells: strength and range scaled by env_mult when this is active.
- T09 NoTimingChange: delays/durations unchanged; only scan progress rate changes.
- T10 DeterministicEnvMult: depends only on ground_quality_pct and spell params.
@@END:B12.SPELL.SPELL_GROUNDING.Q0@@

@@BEGIN:B12.SPELL.SPELL_SILENT_STEP.C0@@
SPELL::SPELL_SILENT_STEP
@@END:B12.SPELLS.QA.23@@
@@BEGIN:B12.SPELLS.CANON.83@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_SILENT_STEP.C0@@

@@BEGIN:B12.SPELL.SPELL_SILENT_STEP.C1@@
@@END:B12.SPELLS.CANON.83@@
@@BEGIN:B12.SPELLS.CANON.84@@
[CANON] Math + Rounding
- noise_reduction_bp = scaled_strength_bp(base_noise_reduction_bp).
- NoiseFinal = apply_bp_floor(NoiseBase, 10000 - noise_reduction_bp).
- Precedence: if SPELL_LIGHT active => stealth forbidden regardless of noise reduction.
- If stealth/noise subsystem absent => feature_gate='STEALTH_SYSTEM' (spell disabled).
@@END:B12.SPELL.SPELL_SILENT_STEP.C1@@

@@BEGIN:B12.SPELL.SPELL_SILENT_STEP.C2@@
@@END:B12.SPELLS.CANON.84@@
@@BEGIN:B12.SPELLS.CANON.85@@
[CANON] Runtime wiring
- hooks: movement noise evaluation, stealth checks (if present).
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE.
@@END:B12.SPELL.SPELL_SILENT_STEP.C2@@

@@BEGIN:B12.SPELL.SPELL_SILENT_STEP.D0@@
@@END:B12.SPELLS.CANON.85@@
@@BEGIN:B12.SPELLS.DATA.26@@
[DATA] Params (DB_SPEC)
- feature_gate:string='STEALTH_SYSTEM'
- base_noise_reduction_bp:BP:bp:int in [0..10000]
@@END:B12.SPELL.SPELL_SILENT_STEP.D0@@

@@BEGIN:B12.SPELL.SPELL_SILENT_STEP.Q0@@
@@END:B12.SPELLS.DATA.26@@
@@BEGIN:B12.SPELLS.QA.24@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: if STEALTH_SYSTEM disabled => enable rejects.
- T07 NoiseReduces: noise decreases deterministically.
- T08 LightOverrides: SPELL_LIGHT forbids stealth even with silent step.
- T09 Clamp: noise_reduction_bp <=10000.
- T10 NoCombatSpecial: works same in/out of combat (unless stealth rules restrict).
@@END:B12.SPELL.SPELL_SILENT_STEP.Q0@@

@@BEGIN:B12.SPELL.SPELL_HERB_SCAN.C0@@
SPELL::SPELL_HERB_SCAN
@@END:B12.SPELLS.QA.24@@
@@BEGIN:B12.SPELLS.CANON.86@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: SCAN_PROGRESS
- rng_ops:
  - op_id='herb.classify' rng_stream='RNG_SPAWN' context='spell.herb_scan.classify' scope_id_template='(scan_session_id, herb_node_id, spell_instance_id)' draw_index_spec='0'
@@END:B12.SPELL.SPELL_HERB_SCAN.C0@@

@@BEGIN:B12.SPELL.SPELL_HERB_SCAN.C1@@
@@END:B12.SPELLS.CANON.86@@
@@BEGIN:B12.SPELLS.CANON.87@@
[CANON] Math + Rounding
- range_m:int = scaled_range(base_range_m=10).
- detect_ticks10s:int = ceil_div(base_detect_ticks10s*10000, PotencyMult_bp(Q)).
- locate_ticks10s:int = ceil_div(base_locate_ticks10s*10000, PotencyMult_bp(Q)).
- identify_ticks10s:int = ceil_div(base_identify_ticks10s*10000, PotencyMult_bp(Q)).
- scan_accuracy_chance_bp = scaled_strength_bp(base_scan_accuracy_chance_bp).
- Stage model (progress_bp vs required ticks):
  - Stage1 done at detect_ticks10s*10000 => output has_any:bool.
  - Stage2 done at locate_ticks10s*10000 => output adds positions (stable order by herb_node_id asc).
  - Stage3 done at identify_ticks10s*10000 => output adds classification; classification may be wrong with chance (see RNG).
- RNG classify: draw=rand_int(0..9999); ok = (draw < scan_accuracy_chance_bp). If not ok => return 'unknown_or_wrong_group' (data-mapped).
@@END:B12.SPELL.SPELL_HERB_SCAN.C1@@

@@BEGIN:B12.SPELL.SPELL_HERB_SCAN.C2@@
@@END:B12.SPELLS.CANON.87@@
@@BEGIN:B12.SPELLS.CANON.88@@
[CANON] Runtime wiring
- hooks: TIME_ADVANCE only. No combat.
- state: scan_session_id (event_id of toggle-on), progress_bp, stage.
- feature_gate: WORLD_SCAN (shared with ore scan).
- explain: RULE_SPELL_SCAN_PROGRESS + RULE_SPELL_PROC for classify draw at stage3 completion.
@@END:B12.SPELL.SPELL_HERB_SCAN.C2@@

@@BEGIN:B12.SPELL.SPELL_HERB_SCAN.D0@@
@@END:B12.SPELLS.CANON.88@@
@@BEGIN:B12.SPELLS.DATA.27@@
[DATA] Params (DB_SPEC)
- feature_gate:string='WORLD_SCAN'
- base_range_m:METER_INT:int=10
- base_detect_ticks10s:TICKS10S:int>=1
- base_locate_ticks10s:TICKS10S:int>=1
- base_identify_ticks10s:TICKS10S:int>=1
- base_scan_accuracy_chance_bp:CHANCE_BP:bp:int in [0..10000]
@@END:B12.SPELL.SPELL_HERB_SCAN.D0@@

@@BEGIN:B12.SPELL.SPELL_HERB_SCAN.Q0@@
@@END:B12.SPELLS.DATA.27@@
@@BEGIN:B12.SPELLS.QA.25@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: if WORLD_SCAN disabled => enable rejects.
- T07 StageOrder: cannot reach stage3 without stage1/2.
- T08 RNGKeyStable: scope_id uses herb_node_id and scan_session_id; no reroll by UI.
- T09 NoSpawn: if no herbs in range, stage1 returns has_any=false and later stages return empty.
- T10 DeterministicPositions: stage2 positions stable order.
@@END:B12.SPELL.SPELL_HERB_SCAN.Q0@@

@@BEGIN:B12.SPELL.SPELL_INERTIA_STRIKE.C0@@
SPELL::SPELL_INERTIA_STRIKE
@@END:B12.SPELLS.QA.25@@
@@BEGIN:B12.SPELLS.CANON.89@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: true (status proc)
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: ON_HIT
- rng_ops:
  - op_id='stun.proc' rng_stream='RNG_COMBAT' context='combat.spell.inertia_stun' scope_id_template='(combat_id, actor_id, target_id, round_index, action_seq, spell_instance_id)' draw_index_spec='0'
@@END:B12.SPELL.SPELL_INERTIA_STRIKE.C0@@

@@BEGIN:B12.SPELL.SPELL_INERTIA_STRIKE.C1@@
@@END:B12.SPELLS.CANON.89@@
@@BEGIN:B12.SPELLS.CANON.90@@
[CANON] Math + Rounding
- stun_chance_bp = scaled_strength_bp(base_stun_chance_bp).
- stun_duration_ticks10s:int = base_stun_duration_ticks10s (not scaled).
- On each successful melee hit: draw=rand_int(0..9999); if draw < stun_chance_bp => apply status_tag 'status:STUN' for stun_duration_ticks10s*10 sec, unless target immune.
@@END:B12.SPELL.SPELL_INERTIA_STRIKE.C1@@

@@BEGIN:B12.SPELL.SPELL_INERTIA_STRIKE.C2@@
@@END:B12.SPELLS.CANON.90@@
@@BEGIN:B12.SPELLS.CANON.91@@
[CANON] Runtime wiring
- hooks: HIT_RESOLVE (melee only), status apply pipeline.
- ordering: proc after hit confirmed, before end-of-action.
- state: none beyond on/off.
- explain: RULE_SPELL_PROC with draw+success; status apply logged by existing status explain.
@@END:B12.SPELL.SPELL_INERTIA_STRIKE.C2@@

@@BEGIN:B12.SPELL.SPELL_INERTIA_STRIKE.D0@@
@@END:B12.SPELLS.CANON.91@@
@@BEGIN:B12.SPELLS.DATA.28@@
[DATA] Params (DB_SPEC)
- base_stun_chance_bp:CHANCE_BP:bp:int in [0..10000]
- base_stun_duration_ticks10s:TICKS10S:int>=1
- stun_status_tag:string='status:STUN' (data mapping)
@@END:B12.SPELL.SPELL_INERTIA_STRIKE.D0@@

@@BEGIN:B12.SPELL.SPELL_INERTIA_STRIKE.Q0@@
@@END:B12.SPELLS.DATA.28@@
@@BEGIN:B12.SPELLS.QA.26@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 MeleeOnly: ranged hits never proc.
- T07 RNGDrawOnce: exactly 1 draw per eligible hit.
- T08 ImmunityRespected: if target immune => no status apply even on success draw.
- T09 FixedDuration: duration not scaled by Q/power.
- T10 DeterministicScope: action_seq prevents double-proc on replay.
@@END:B12.SPELL.SPELL_INERTIA_STRIKE.Q0@@

@@BEGIN:B12.SPELL.SPELL_BLEEDING_FLETCH.C0@@
SPELL::SPELL_BLEEDING_FLETCH
@@END:B12.SPELLS.QA.26@@
@@BEGIN:B12.SPELLS.CANON.92@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: true (status proc)
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: ON_HIT
- rng_ops:
  - op_id='bleed.proc' rng_stream='RNG_COMBAT' context='combat.spell.bleed_fletch' scope_id_template='(combat_id, actor_id, target_id, round_index, action_seq, spell_instance_id)' draw_index_spec='0'
@@END:B12.SPELL.SPELL_BLEEDING_FLETCH.C0@@

@@BEGIN:B12.SPELL.SPELL_BLEEDING_FLETCH.C1@@
@@END:B12.SPELLS.CANON.92@@
@@BEGIN:B12.SPELLS.CANON.93@@
[CANON] Math + Rounding
- bleed_chance_bp = scaled_strength_bp(base_bleed_chance_bp).
- bleed_duration_ticks10s:int = base_bleed_duration_ticks10s (fixed).
- Trigger: successful hit by arrow (bow).
- draw=rand_int(0..9999); if draw < bleed_chance_bp => apply status_tag 'status:BLEEDING' for bleed_duration_ticks10s*10 sec, unless immune.
@@END:B12.SPELL.SPELL_BLEEDING_FLETCH.C1@@

@@BEGIN:B12.SPELL.SPELL_BLEEDING_FLETCH.C2@@
@@END:B12.SPELLS.CANON.93@@
@@BEGIN:B12.SPELLS.CANON.94@@
[CANON] Runtime wiring
- hooks: HIT_RESOLVE (projectile kind=ARROW), status apply pipeline.
- state: none beyond on/off.
- explain: RULE_SPELL_PROC.
@@END:B12.SPELL.SPELL_BLEEDING_FLETCH.C2@@

@@BEGIN:B12.SPELL.SPELL_BLEEDING_FLETCH.D0@@
@@END:B12.SPELLS.CANON.94@@
@@BEGIN:B12.SPELLS.DATA.29@@
[DATA] Params (DB_SPEC)
- base_bleed_chance_bp:CHANCE_BP:bp:int in [0..10000]
- base_bleed_duration_ticks10s:TICKS10S:int>=1
- bleed_status_tag:string='status:BLEEDING' (data mapping)
@@END:B12.SPELL.SPELL_BLEEDING_FLETCH.D0@@

@@BEGIN:B12.SPELL.SPELL_BLEEDING_FLETCH.Q0@@
@@END:B12.SPELLS.DATA.29@@
@@BEGIN:B12.SPELLS.QA.27@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 ArrowOnly: melee and non-arrow ranged do not proc.
- T07 RNGDrawOnce: 1 draw per arrow hit.
- T08 ImmunityRespected: immune target never gets bleeding.
- T09 FixedDuration: duration fixed.
- T10 ScopeDeterministic: uses action_seq.
@@END:B12.SPELL.SPELL_BLEEDING_FLETCH.Q0@@

@@BEGIN:B12.SPELL.SPELL_ARROW_RECLAIM.C0@@
SPELL::SPELL_ARROW_RECLAIM
@@END:B12.SPELLS.QA.27@@
@@BEGIN:B12.SPELLS.CANON.95@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: ON_SCENE_LOOT
- rng_ops:
  - op_id='arrow.recover' rng_stream='RNG_LOOT' context='spell.arrow_recover' scope_id_template='(scene_id, actor_id, spell_instance_id)' draw_index_spec='i:0..SpentArrowsEligible-1'
@@END:B12.SPELL.SPELL_ARROW_RECLAIM.C0@@

@@BEGIN:B12.SPELL.SPELL_ARROW_RECLAIM.C1@@
@@END:B12.SPELLS.CANON.95@@
@@BEGIN:B12.SPELLS.CANON.96@@
[CANON] Math + Rounding
- recover_chance_bp = scaled_strength_bp(base_recover_chance_bp).
- Trigger: SCENE_LOOT event (end of combat/episode/explicit search).
- Count candidates: SpentArrowsEligible = SpentArrows - UnrecoverableArrows (deterministic accounting).
- For each candidate i: draw=rand_int(0..9999); success=(draw < recover_chance_bp) => return 1 arrow.
- This spell never creates arrows; only returns arrows that were actually spent and not flagged unrecoverable.
@@END:B12.SPELL.SPELL_ARROW_RECLAIM.C1@@

@@BEGIN:B12.SPELL.SPELL_ARROW_RECLAIM.C2@@
@@END:B12.SPELLS.CANON.96@@
@@BEGIN:B12.SPELLS.CANON.97@@
[CANON] Runtime wiring
- hooks: SCENE_LOOT only; no background ticks.
- state: none beyond on/off.
- explain: RULE_SPELL_PROC repeated with draw_index=i; optional RULE_INVENTORY_ADD for returned arrows.
@@END:B12.SPELL.SPELL_ARROW_RECLAIM.C2@@

@@BEGIN:B12.SPELL.SPELL_ARROW_RECLAIM.D0@@
@@END:B12.SPELLS.CANON.97@@
@@BEGIN:B12.SPELLS.DATA.30@@
[DATA] Params (DB_SPEC)
- base_recover_chance_bp:CHANCE_BP:bp:int in [0..10000]
@@END:B12.SPELL.SPELL_ARROW_RECLAIM.D0@@

@@BEGIN:B12.SPELL.SPELL_ARROW_RECLAIM.Q0@@
@@END:B12.SPELLS.DATA.30@@
@@BEGIN:B12.SPELLS.QA.28@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 SceneLootOnly: no effect during combat ticks.
- T07 CandidateFilter: unrecoverable arrows excluded deterministically.
- T08 RNGDrawPerArrow: exactly 1 draw per eligible arrow candidate.
- T09 NoCreate: returned arrows <= spent eligible.
- T10 StableScope: scope_id includes scene_id and spell_instance_id.
@@END:B12.SPELL.SPELL_ARROW_RECLAIM.Q0@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_FOCUS.C0@@
SPELL::SPELL_SHIELD_FOCUS
@@END:B12.SPELLS.QA.28@@
@@BEGIN:B12.SPELLS.CANON.98@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true (suspended if grounded=false)
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_SHIELD_FOCUS.C0@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_FOCUS.C1@@
@@END:B12.SPELLS.CANON.98@@
@@BEGIN:B12.SPELLS.CANON.99@@
[CANON] Math + Rounding
- block_bonus_bp = scaled_strength_bp(base_block_chance_bonus_bp).
- Requires equipped shield; else effect=0 (enable allowed but has no effect).
- Final chances (bp) with cap 95%:
  shield_melee_chance_bp = min(9500, shield_melee_base_bp + block_bonus_bp).
  shield_ranged_chance_bp = min(9500, shield_ranged_base_bp + block_bonus_bp).
- Uses existing SHIELD_PROC_CANON RNG draw (B12).
@@END:B12.SPELL.SPELL_SHIELD_FOCUS.C1@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_FOCUS.C2@@
@@END:B12.SPELLS.CANON.99@@
@@BEGIN:B12.SPELLS.CANON.100@@
[CANON] Runtime wiring
- hooks: shield proc chance getter in combat.
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE; shield proc explain stays as is.
@@END:B12.SPELL.SPELL_SHIELD_FOCUS.C2@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_FOCUS.D0@@
@@END:B12.SPELLS.CANON.100@@
@@BEGIN:B12.SPELLS.DATA.31@@
[DATA] Params (DB_SPEC)
- base_block_chance_bonus_bp:BP:bp:int>=0 (10000=+100% points)
@@END:B12.SPELL.SPELL_SHIELD_FOCUS.D0@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_FOCUS.Q0@@
@@END:B12.SPELLS.DATA.31@@
@@BEGIN:B12.SPELLS.QA.29@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 NoShieldNoEffect: without shield equipped, no chance change.
- T07 Cap95: final chance never exceeds 9500.
- T08 GroundedPause: grounded=false => bonus 0.
- T09 DeterministicCombine: base + bonus uses int add and min.
- T10 CompatibleWithShieldProcCanon: RNG key unchanged.
@@END:B12.SPELL.SPELL_SHIELD_FOCUS.Q0@@

@@BEGIN:B12.SPELL.SPELL_DEFLECTION_ANGLE.C0@@
SPELL::SPELL_DEFLECTION_ANGLE
@@END:B12.SPELLS.QA.29@@
@@BEGIN:B12.SPELLS.CANON.101@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_DEFLECTION_ANGLE.C0@@

@@BEGIN:B12.SPELL.SPELL_DEFLECTION_ANGLE.C1@@
@@END:B12.SPELLS.CANON.101@@
@@BEGIN:B12.SPELLS.CANON.102@@
[CANON] Math + Rounding
- extra_reduction_bp = scaled_strength_bp(base_extra_reduction_bp).
- If shield block succeeds, replace default shield reduction with boosted reduction:
  melee_reduction_bp = min(8000, 5000 + extra_reduction_bp).
  ranged_reduction_bp = min(7000, 3000 + extra_reduction_bp).
- DamageAfterShield = apply_bp_floor(DamageBeforeShield, 10000 - reduction_bp).
- Does not override microdamage rule (microdamage applies only when barrier depleted before hit).
@@END:B12.SPELL.SPELL_DEFLECTION_ANGLE.C1@@

@@BEGIN:B12.SPELL.SPELL_DEFLECTION_ANGLE.C2@@
@@END:B12.SPELLS.CANON.102@@
@@BEGIN:B12.SPELLS.CANON.103@@
[CANON] Runtime wiring
- hooks: shield reduction computation on successful block.
- state: none beyond on/off.
- explain: existing shield explain can include final reduction_bp; no extra RNG.
@@END:B12.SPELL.SPELL_DEFLECTION_ANGLE.C2@@

@@BEGIN:B12.SPELL.SPELL_DEFLECTION_ANGLE.D0@@
@@END:B12.SPELLS.CANON.103@@
@@BEGIN:B12.SPELLS.DATA.32@@
[DATA] Params (DB_SPEC)
- base_extra_reduction_bp:BP:bp:int>=0
@@END:B12.SPELL.SPELL_DEFLECTION_ANGLE.D0@@

@@BEGIN:B12.SPELL.SPELL_DEFLECTION_ANGLE.Q0@@
@@END:B12.SPELLS.DATA.32@@
@@BEGIN:B12.SPELLS.QA.30@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 NeedsShield: without shield, no effect.
- T07 Caps: melee<=8000, ranged<=7000.
- T08 WorksOnlyOnBlock: no block => no damage reduction change.
- T09 Ordering: applies at shield stage, before armor/barrier.
- T10 DeterministicReduction: uses apply_bp_floor.
@@END:B12.SPELL.SPELL_DEFLECTION_ANGLE.Q0@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.C0@@
SPELL::SPELL_SHIELD_COUNTERSTUN
@@END:B12.SPELLS.QA.30@@
@@BEGIN:B12.SPELLS.CANON.104@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: true (status proc)
- requires_grounded: true
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: ON_BLOCK
- rng_ops:
  - op_id='counterstun.proc' rng_stream='RNG_COMBAT' context='combat.spell.shield_counterstun' scope_id_template='(combat_id, defender_id, attacker_id, round_index, action_seq, spell_instance_id)' draw_index_spec='0'
@@END:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.C0@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.C1@@
@@END:B12.SPELLS.CANON.104@@
@@BEGIN:B12.SPELLS.CANON.105@@
[CANON] Math + Rounding
- chance_bp = scaled_strength_bp(base_counterstun_chance_bp).
- duration_ticks10s:int = base_stun_duration_ticks10s (fixed).
- Trigger: successful shield block in melee.
- draw=rand_int(0..9999); if draw < chance_bp => apply status_tag 'status:STUN' to attacker for duration, unless immune.
@@END:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.C1@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.C2@@
@@END:B12.SPELLS.CANON.105@@
@@BEGIN:B12.SPELLS.CANON.106@@
[CANON] Runtime wiring
- hooks: BLOCK_RESOLVE (melee shield).
- state: none beyond on/off.
- explain: RULE_SPELL_PROC with draw+success.
@@END:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.C2@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.D0@@
@@END:B12.SPELLS.CANON.106@@
@@BEGIN:B12.SPELLS.DATA.33@@
[DATA] Params (DB_SPEC)
- base_counterstun_chance_bp:CHANCE_BP:bp:int in [0..10000]
- base_stun_duration_ticks10s:TICKS10S:int>=1
- stun_status_tag:string='status:STUN'
@@END:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.D0@@

@@BEGIN:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.Q0@@
@@END:B12.SPELLS.DATA.33@@
@@BEGIN:B12.SPELLS.QA.31@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 MeleeOnly: ranged blocks do not proc counterstun.
- T07 RequiresBlock: no block => no proc.
- T08 RNGKeyStable: action_seq included.
- T09 FixedDuration: duration fixed.
- T10 ImmunityRespected: immune attacker not stunned.
@@END:B12.SPELL.SPELL_SHIELD_COUNTERSTUN.Q0@@

@@BEGIN:B12.SPELL.SPELL_CALM_AURA.C0@@
SPELL::SPELL_CALM_AURA
@@END:B12.SPELLS.QA.31@@
@@BEGIN:B12.SPELLS.CANON.107@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: DIALOGUE_STEP
- rng_ops: (none)
@@END:B12.SPELL.SPELL_CALM_AURA.C0@@

@@BEGIN:B12.SPELL.SPELL_CALM_AURA.C1@@
@@END:B12.SPELLS.CANON.107@@
@@BEGIN:B12.SPELLS.CANON.108@@
[CANON] Math + Rounding
- aggro_gain_reduction_bp = scaled_strength_bp(base_aggro_gain_reduction_bp).
- If dialogue system present: AggroDeltaFinal = apply_bp_floor(AggroDeltaBase, 10000 - aggro_gain_reduction_bp).
- If dialogue system absent => feature_gate='SOCIAL_SYSTEM' (spell disabled in MVP).
@@END:B12.SPELL.SPELL_CALM_AURA.C1@@

@@BEGIN:B12.SPELL.SPELL_CALM_AURA.C2@@
@@END:B12.SPELLS.CANON.108@@
@@BEGIN:B12.SPELLS.CANON.109@@
[CANON] Runtime wiring
- hooks: DIALOGUE_STEP only.
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE; optional RULE_DIALOGUE_AGGRO_DELTA if exists.
@@END:B12.SPELL.SPELL_CALM_AURA.C2@@

@@BEGIN:B12.SPELL.SPELL_CALM_AURA.D0@@
@@END:B12.SPELLS.CANON.109@@
@@BEGIN:B12.SPELLS.DATA.34@@
[DATA] Params (DB_SPEC)
- feature_gate:string='SOCIAL_SYSTEM'
- base_aggro_gain_reduction_bp:BP:bp:int in [0..10000]
@@END:B12.SPELL.SPELL_CALM_AURA.D0@@

@@BEGIN:B12.SPELL.SPELL_CALM_AURA.Q0@@
@@END:B12.SPELLS.DATA.34@@
@@BEGIN:B12.SPELLS.QA.32@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: SOCIAL_SYSTEM disabled => enable rejects.
- T07 NoFriendship: reduces escalation only; does not change faction/relations directly.
- T08 DeterministicDelta: pure multiply, no RNG.
- T09 NoCombat: enable in combat rejects.
- T10 Range: applies only within dialogue distance (data).
@@END:B12.SPELL.SPELL_CALM_AURA.Q0@@

@@BEGIN:B12.SPELL.SPELL_EMPATHY_READ.C0@@
SPELL::SPELL_EMPATHY_READ
@@END:B12.SPELLS.QA.32@@
@@BEGIN:B12.SPELLS.CANON.110@@
[CANON] Classification
- maintained=true
- binding: TARGET
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: DIALOGUE_STEP
- rng_ops: (none)
@@END:B12.SPELL.SPELL_EMPATHY_READ.C0@@

@@BEGIN:B12.SPELL.SPELL_EMPATHY_READ.C1@@
@@END:B12.SPELLS.CANON.110@@
@@BEGIN:B12.SPELLS.CANON.111@@
[CANON] Math + Rounding
- range_m:int = scaled_range(base_range_m=10).
- detail_level_int = scaled_strength_int(base_emotion_detail_level_int).
- If social checks exist: SocialDCFinal = max(0, SocialDCBase - detail_level_int).
- If social system absent => feature_gate='SOCIAL_SYSTEM'.
@@END:B12.SPELL.SPELL_EMPATHY_READ.C1@@

@@BEGIN:B12.SPELL.SPELL_EMPATHY_READ.C2@@
@@END:B12.SPELLS.CANON.111@@
@@BEGIN:B12.SPELLS.CANON.112@@
[CANON] Runtime wiring
- hooks: DIALOGUE_STEP/targeting, UI hint rendering.
- state: target_id (during dialogue), none else.
- explain: RULE_SPELL_TOGGLE (optional).
@@END:B12.SPELL.SPELL_EMPATHY_READ.C2@@

@@BEGIN:B12.SPELL.SPELL_EMPATHY_READ.D0@@
@@END:B12.SPELLS.CANON.112@@
@@BEGIN:B12.SPELLS.DATA.35@@
[DATA] Params (DB_SPEC)
- feature_gate:string='SOCIAL_SYSTEM'
- base_range_m:METER_INT:int=10
- base_emotion_detail_level_int:INT:int>=0
@@END:B12.SPELL.SPELL_EMPATHY_READ.D0@@

@@BEGIN:B12.SPELL.SPELL_EMPATHY_READ.Q0@@
@@END:B12.SPELLS.DATA.35@@
@@BEGIN:B12.SPELLS.QA.33@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: SOCIAL_SYSTEM disabled => enable rejects.
- T07 TargetRange: out of range => no hints.
- T08 NoMindRead: never reveals secrets/memory; only coarse state tags (data).
- T09 DeterministicHints: depends only on NPC state and detail_level.
- T10 NonEmotive: constructs/undead may yield empty hint set (data).
@@END:B12.SPELL.SPELL_EMPATHY_READ.Q0@@

@@BEGIN:B12.SPELL.SPELL_PLAINNESS_VEIL.C0@@
SPELL::SPELL_PLAINNESS_VEIL
@@END:B12.SPELLS.QA.33@@
@@BEGIN:B12.SPELLS.CANON.113@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_PLAINNESS_VEIL.C0@@

@@BEGIN:B12.SPELL.SPELL_PLAINNESS_VEIL.C1@@
@@END:B12.SPELLS.CANON.113@@
@@BEGIN:B12.SPELLS.CANON.114@@
[CANON] Math + Rounding
- attention_reduction_bp = scaled_strength_bp(base_attention_reduction_bp).
- If notice system exists: NoticeChanceFinal = apply_bp_floor(NoticeChanceBase, 10000 - attention_reduction_bp).
- If SPELL_LIGHT active, veil provides no practical cover in darkness (UI note); no extra math needed.
- If notice system absent => feature_gate='SOCIAL_SYSTEM'.
@@END:B12.SPELL.SPELL_PLAINNESS_VEIL.C1@@

@@BEGIN:B12.SPELL.SPELL_PLAINNESS_VEIL.C2@@
@@END:B12.SPELLS.CANON.114@@
@@BEGIN:B12.SPELLS.CANON.115@@
[CANON] Runtime wiring
- hooks: notice/recognition checks (if exist).
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE.
@@END:B12.SPELL.SPELL_PLAINNESS_VEIL.C2@@

@@BEGIN:B12.SPELL.SPELL_PLAINNESS_VEIL.D0@@
@@END:B12.SPELLS.CANON.115@@
@@BEGIN:B12.SPELLS.DATA.36@@
[DATA] Params (DB_SPEC)
- feature_gate:string='SOCIAL_SYSTEM'
- base_attention_reduction_bp:BP:bp:int in [0..10000]
@@END:B12.SPELL.SPELL_PLAINNESS_VEIL.D0@@

@@BEGIN:B12.SPELL.SPELL_PLAINNESS_VEIL.Q0@@
@@END:B12.SPELLS.DATA.36@@
@@BEGIN:B12.SPELLS.QA.34@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: SOCIAL_SYSTEM disabled => enable rejects.
- T07 NotInvisibility: does not bypass deliberate search (system-level immunity).
- T08 DeterministicNotice: pure multiply.
- T09 LightInteraction: if light on, stealth/veil cannot claim darkness cover.
- T10 NoCombat: enable in combat rejects.
@@END:B12.SPELL.SPELL_PLAINNESS_VEIL.Q0@@

@@BEGIN:B12.SPELL.SPELL_CONVERSATION_HUSH.C0@@
SPELL::SPELL_CONVERSATION_HUSH
@@END:B12.SPELLS.QA.34@@
@@BEGIN:B12.SPELLS.CANON.116@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: DIALOGUE_STEP
- rng_ops: (none)
@@END:B12.SPELL.SPELL_CONVERSATION_HUSH.C0@@

@@BEGIN:B12.SPELL.SPELL_CONVERSATION_HUSH.C1@@
@@END:B12.SPELLS.CANON.116@@
@@BEGIN:B12.SPELLS.CANON.117@@
[CANON] Math + Rounding
- eavesdrop_reduction_bp = scaled_strength_bp(base_eavesdrop_reduction_bp).
- If eavesdrop model exists: EavesdropChanceFinal = apply_bp_floor(EavesdropChanceBase, 10000 - eavesdrop_reduction_bp).
- Hard limit: at 1-2m distance, eavesdrop chance is unchanged (data threshold).
- If subsystem absent => feature_gate='SOCIAL_SYSTEM'.
@@END:B12.SPELL.SPELL_CONVERSATION_HUSH.C1@@

@@BEGIN:B12.SPELL.SPELL_CONVERSATION_HUSH.C2@@
@@END:B12.SPELLS.CANON.117@@
@@BEGIN:B12.SPELLS.CANON.118@@
[CANON] Runtime wiring
- hooks: DIALOGUE_STEP / scene eavesdrop check.
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE.
@@END:B12.SPELL.SPELL_CONVERSATION_HUSH.C2@@

@@BEGIN:B12.SPELL.SPELL_CONVERSATION_HUSH.D0@@
@@END:B12.SPELLS.CANON.118@@
@@BEGIN:B12.SPELLS.DATA.37@@
[DATA] Params (DB_SPEC)
- feature_gate:string='SOCIAL_SYSTEM'
- base_eavesdrop_reduction_bp:BP:bp:int in [0..10000]
- eavesdrop_min_distance_m:METER_INT:int>=0 (data)
@@END:B12.SPELL.SPELL_CONVERSATION_HUSH.D0@@

@@BEGIN:B12.SPELL.SPELL_CONVERSATION_HUSH.Q0@@
@@END:B12.SPELLS.DATA.37@@
@@BEGIN:B12.SPELLS.QA.35@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: SOCIAL_SYSTEM disabled => enable rejects.
- T07 DistanceLimit: within min distance, no reduction applies.
- T08 Deterministic: pure multiply, no RNG.
- T09 NoSilenceBubble: does not mute; only affects eavesdrop checks.
- T10 NoCombat: enable in combat rejects.
@@END:B12.SPELL.SPELL_CONVERSATION_HUSH.Q0@@

@@BEGIN:B12.SPELL.SPELL_FAIR_TRADE.C0@@
SPELL::SPELL_FAIR_TRADE
@@END:B12.SPELLS.QA.35@@
@@BEGIN:B12.SPELLS.CANON.119@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: SHOP_PRICE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_FAIR_TRADE.C0@@

@@BEGIN:B12.SPELL.SPELL_FAIR_TRADE.C1@@
@@END:B12.SPELLS.CANON.119@@
@@BEGIN:B12.SPELLS.CANON.120@@
[CANON] Math + Rounding
- spread_reduction_bp = scaled_strength_bp(base_price_spread_reduction_bp).
- Applied to shop multipliers as a pull-to-1.0 effect (bp):
  - delta_bp = mult_base_bp - 10000 (signed).
  - mult_final_bp = 10000 + floor_div(delta_bp * (10000 - spread_reduction_bp), 10000).
- Apply to both buy_mult_bp and sell_mult_bp BEFORE VarBuy/VarSell and Scarcity and before SHOP_SPREAD_ROUNDING_GUARD.
- Does not create discounts below 1.0 unless base mult already <1.0 (e.g. exchange).
@@END:B12.SPELL.SPELL_FAIR_TRADE.C1@@

@@BEGIN:B12.SPELL.SPELL_FAIR_TRADE.C2@@
@@END:B12.SPELLS.CANON.120@@
@@BEGIN:B12.SPELLS.CANON.121@@
[CANON] Runtime wiring
- hooks: SHOP_PRICE_CALC only (out of combat).
- state: none beyond on/off.
- explain: include mult_base_bp and mult_final_bp in shop price trace if enabled.
@@END:B12.SPELL.SPELL_FAIR_TRADE.C2@@

@@BEGIN:B12.SPELL.SPELL_FAIR_TRADE.D0@@
@@END:B12.SPELLS.CANON.121@@
@@BEGIN:B12.SPELLS.DATA.38@@
[DATA] Params (DB_SPEC)
- base_price_spread_reduction_bp:BP:bp:int in [0..10000]
@@END:B12.SPELL.SPELL_FAIR_TRADE.D0@@

@@BEGIN:B12.SPELL.SPELL_FAIR_TRADE.Q0@@
@@END:B12.SPELLS.DATA.38@@
@@BEGIN:B12.SPELLS.QA.36@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 NoCombat: enable in combat rejects.
- T07 PullToOne: mult_final closer to 10000 than mult_base for reduction>0.
- T08 GuardStillApplies: SHOP_SPREAD_ROUNDING_GUARD enforced after spell modification.
- T09 DeterministicPrice: no extra RNG; only modifies multipliers.
- T10 ClampReduction: reduction_bp in 0..10000.
@@END:B12.SPELL.SPELL_FAIR_TRADE.Q0@@

@@BEGIN:B12.SPELL.SPELL_INTIMIDATION_EDGE.C0@@
SPELL::SPELL_INTIMIDATION_EDGE
@@END:B12.SPELLS.QA.36@@
@@BEGIN:B12.SPELLS.CANON.122@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true
- allowed_in_combat: false
- allowed_out_of_combat: true
- tick_model: DIALOGUE_STEP
- rng_ops: (none)
@@END:B12.SPELL.SPELL_INTIMIDATION_EDGE.C0@@

@@BEGIN:B12.SPELL.SPELL_INTIMIDATION_EDGE.C1@@
@@END:B12.SPELLS.CANON.122@@
@@BEGIN:B12.SPELLS.CANON.123@@
[CANON] Math + Rounding
- intimidation_bonus_bp = scaled_strength_bp(base_intimidation_bonus_bp).
- If intimidate chance model exists: IntimidateChanceFinalBp = min(9500, IntimidateChanceBaseBp + intimidation_bonus_bp).
- Immunity: targets tagged status:FEARLESS ignore bonus (data).
- If subsystem absent => feature_gate='SOCIAL_SYSTEM'.
@@END:B12.SPELL.SPELL_INTIMIDATION_EDGE.C1@@

@@BEGIN:B12.SPELL.SPELL_INTIMIDATION_EDGE.C2@@
@@END:B12.SPELLS.CANON.123@@
@@BEGIN:B12.SPELLS.CANON.124@@
[CANON] Runtime wiring
- hooks: dialogue/social action resolve.
- state: none beyond on/off.
- explain: RULE_SPELL_TOGGLE; optional RULE_SOCIAL_CHECK.
@@END:B12.SPELL.SPELL_INTIMIDATION_EDGE.C2@@

@@BEGIN:B12.SPELL.SPELL_INTIMIDATION_EDGE.D0@@
@@END:B12.SPELLS.CANON.124@@
@@BEGIN:B12.SPELLS.DATA.39@@
[DATA] Params (DB_SPEC)
- feature_gate:string='SOCIAL_SYSTEM'
- base_intimidation_bonus_bp:BP:bp:int>=0
- fearless_tag:string='status:FEARLESS' (data)
@@END:B12.SPELL.SPELL_INTIMIDATION_EDGE.D0@@

@@BEGIN:B12.SPELL.SPELL_INTIMIDATION_EDGE.Q0@@
@@END:B12.SPELLS.DATA.39@@
@@BEGIN:B12.SPELLS.QA.37@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 GateOffReject: SOCIAL_SYSTEM disabled => enable rejects.
- T07 Cap95: final chance <=9500.
- T08 Immunity: fearless targets ignore bonus.
- T09 Deterministic: no RNG introduced by spell.
- T10 Consequences: relationship impact is narrative-only (no hidden math).
@@END:B12.SPELL.SPELL_INTIMIDATION_EDGE.Q0@@

@@BEGIN:B12.SPELL.SPELL_VITAL_RESERVE.C0@@
SPELL::SPELL_VITAL_RESERVE
@@END:B12.SPELLS.QA.37@@
@@BEGIN:B12.SPELLS.CANON.125@@
[CANON] Classification
- maintained=true
- binding: SELF
- offensive: false
- requires_grounded: true (if grounded=false => bonus 0, slot still occupied)
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: NONE
- rng_ops: (none)
@@END:B12.SPELL.SPELL_VITAL_RESERVE.C0@@

@@BEGIN:B12.SPELL.SPELL_VITAL_RESERVE.C1@@
@@END:B12.SPELLS.CANON.125@@
@@BEGIN:B12.SPELLS.CANON.126@@
[CANON] Math + Rounding
- maxhp_bonus_bp = scaled_strength_bp(base_maxhp_bonus_bp).
- stack_policy=MULTI_INSTANCE_ADD: if multiple active instances, sum maxhp_bonus_bp across them: total_bonus_bp = Σ bonus_bp_i.
- MaxHPFinal = floor_div(MaxHPBase * (10000 + total_bonus_bp), 10000).
- Toggle on does not heal (HPCurrent unchanged).
- On disable or grounded=false: recompute MaxHPFinal back toward MaxHPBase; if HPCurrent > MaxHPFinal => HPCurrent = MaxHPFinal (not damage, no triggers).
@@END:B12.SPELL.SPELL_VITAL_RESERVE.C1@@

@@BEGIN:B12.SPELL.SPELL_VITAL_RESERVE.C2@@
@@END:B12.SPELLS.CANON.126@@
@@BEGIN:B12.SPELLS.CANON.127@@
[CANON] Runtime wiring
- hooks: derived stats recompute, HP clamp on change.
- state: none beyond on/off; may cache total_bonus_bp for explain.
- explain: RULE_SPELL_TOGGLE; RULE_SPELL_CAP_CLAMP meta{hp_before, hp_after, maxhp_before, maxhp_after}.
@@END:B12.SPELL.SPELL_VITAL_RESERVE.C2@@

@@BEGIN:B12.SPELL.SPELL_VITAL_RESERVE.D0@@
@@END:B12.SPELLS.CANON.127@@
@@BEGIN:B12.SPELLS.DATA.40@@
[DATA] Params (DB_SPEC)
- base_maxhp_bonus_bp:BP:bp:int>=0
- stack_policy:MULTI_INSTANCE_ADD (in SPELL_DEF)
@@END:B12.SPELL.SPELL_VITAL_RESERVE.D0@@

@@BEGIN:B12.SPELL.SPELL_VITAL_RESERVE.Q0@@
@@END:B12.SPELLS.DATA.40@@
@@BEGIN:B12.SPELLS.QA.38@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 NoHealOnEnable: HPCurrent unchanged when max increases.
- T07 ClampOnDisable: HPCurrent clamped down if above new max.
- T08 MultiStackAdds: multiple instances sum bonuses deterministically (stable order).
- T09 GroundedPauseClamps: grounded=false sets bonus 0 and clamps HP if needed.
- T10 NoDamageTrigger: clamp does not trigger 'on damage' effects.
@@END:B12.SPELL.SPELL_VITAL_RESERVE.Q0@@

@@BEGIN:B12.SPELL.SPELL_VITAL_SUPPRESSION.C0@@
SPELL::SPELL_VITAL_SUPPRESSION
@@END:B12.SPELLS.QA.38@@
@@BEGIN:B12.SPELLS.CANON.128@@
[CANON] Classification
- maintained=true
- binding: TARGET
- offensive: true (debuff)
- requires_grounded: true (grounded=false => effect 0, slot occupied)
- allowed_in_combat: true
- allowed_out_of_combat: true
- tick_model: PER_10S
- rng_ops: (none)
@@END:B12.SPELL.SPELL_VITAL_SUPPRESSION.C0@@

@@BEGIN:B12.SPELL.SPELL_VITAL_SUPPRESSION.C1@@
@@END:B12.SPELLS.CANON.128@@
@@BEGIN:B12.SPELLS.CANON.129@@
[CANON] Math + Rounding
- range_m:int = scaled_range(base_range_m=10).
- raw_reduction_bp = scaled_strength_bp(base_maxhp_reduction_bp).
- cap_bp = cap_maxhp_reduction_bp (or cap_boss_bp if target has tag 'boss').
- reduction_bp = min(raw_reduction_bp, cap_bp).
- MaxHPFinal = max(1, floor_div(MaxHPBase * (10000 - reduction_bp), 10000)).
- If HPCurrent > MaxHPFinal => HPCurrent = MaxHPFinal (not damage).
- Range rule: each PER_10S tick, if target out of range => spell auto-off (deterministic).
- Uniqueness: only one target at a time per caster for this spell_id; re-cast retargets (auto-off old).
@@END:B12.SPELL.SPELL_VITAL_SUPPRESSION.C1@@

@@BEGIN:B12.SPELL.SPELL_VITAL_SUPPRESSION.C2@@
@@END:B12.SPELLS.CANON.129@@
@@BEGIN:B12.SPELLS.CANON.130@@
[CANON] Runtime wiring
- hooks: ROUND_END/TIME_ADVANCE tick checks, range checks, derived stats clamp.
- state: target_id, reduction_bp_cached (optional).
- explain: RULE_SPELL_TICK tick_kind='vital_suppression.range_check'; RULE_SPELL_CAP_CLAMP for HP/maxHP clamp.
@@END:B12.SPELL.SPELL_VITAL_SUPPRESSION.C2@@

@@BEGIN:B12.SPELL.SPELL_VITAL_SUPPRESSION.D0@@
@@END:B12.SPELLS.CANON.130@@
@@BEGIN:B12.SPELLS.DATA.41@@
[DATA] Params (DB_SPEC)
- base_range_m:METER_INT:int=10
- base_maxhp_reduction_bp:BP:bp:int>=0
- cap_maxhp_reduction_bp:BP:bp:int=5000 (DATA)
- cap_boss_reduction_bp:BP:bp:int=2000 (DATA)
- boss_tag:string='threat:BOSS' or status/tag mapping (data)
@@END:B12.SPELL.SPELL_VITAL_SUPPRESSION.D0@@

@@BEGIN:B12.SPELL.SPELL_VITAL_SUPPRESSION.Q0@@
@@END:B12.SPELLS.DATA.41@@
@@BEGIN:B12.SPELLS.QA.39@@
[QA] Edge cases + tests
- T01 DeterminismToggle: same inputs (save+content+event_id) -> same on/off + no extra events.
- T02 GroundedPause: grounded=false => output 0; on grounded=true resume without reroll.
- T03 ChannelCap: enable that would exceed CP => reject with RULE_SPELL_PRECONDITION_FAIL.
- T04 IdempotentEvent: duplicate event_id => SKIP/NOOP (no double effects).
- T05 StableOrder: when multiple instances processed, order by spell_id asc, then source_item_instance_id asc.
- T06 CapApplied: reduction never exceeds cap (boss cap if applicable).
- T07 ClampNotDamage: HP clamp does not trigger damage listeners.
- T08 AutoOffOnRange: leaving range turns spell off deterministically.
- T09 OneTarget: second cast retargets and clears previous target effect.
- T10 MinMaxHP: MaxHPFinal >=1 always.
@@END:B12.SPELL.SPELL_VITAL_SUPPRESSION.Q0@@

@@BEGIN:QA.MATRIX.MAGIC@@
@@END:B12.SPELLS.QA.39@@
@@BEGIN:B12.SPELLS.QA.40@@
[QA] MAGIC_SPELLPACK_CHECKLIST (execute in client tests)
- Q01 NoFloat: grep/validator ensures no float usage in spell math.
- Q02 KeyedRng: every rng_op defines stream/context/scope_id/draw_index; 1 draw per op.
- Q03 Time: per10s effects only via TIME_ADVANCE/ROUND_END chunking.
- Q04 Idempotency: toggle/tick/proc/scan completion events are idempotent by event_id.
- Q05 StableOrder: all multi-entity loops are deterministic and sorted.
- Q06 Grounded: grounded=false suspends effects but keeps reservations; resume deterministic.
- Q07 FeatureGates: disabled gates prevent spawn/enable; enabled gates pass validators.
- Q08 CombatVsOut: out-of-combat restricted spells reject in combat (ore/herb/gear clean/social).
- Q09 Economy: Fair trade modifies buy/sell mult before RNG var and before rounding guard; anti-arbitrage holds.
- Q10 Identify: spell identify never changes is_identified; service identify does; archive quest filter unchanged.
@@END:QA.MATRIX.MAGIC@@

@@BEGIN:PATCH.NOTES@@
PATCH_NOTES::SPELLPACK_INTEGRATION
- Added structured spellpack integration blocks with stable @@BEGIN/@@END@@ anchors.
- Added B12.M0 contract: grounded, env_mult, stack_policy, scan_progress_bp, explain rule ids.
- Added B12.M1 DB_SPEC schema for SPELL_DEF/SPELL_PARAM_DEF.
- Added per-spell integration cards for SPELL_BARRIER .. SPELL_VITAL_SUPPRESSION.
- Aligned SPELL_MISTFORM to existing B08 per-round HP cap model (no forced HPDamage=0).
- Clarified SPELL_IDENTIFY as analysis-only (does not flip is_identified, does not remove UNIDENTIFIED).
- Added SPELL_FAIR_TRADE integration to shop multiplier pipeline (pull-to-1.0, respects spread guard).
- Marked world/social subsystem dependent spells as feature-gated (WORLD_SCAN, SOCIAL_SYSTEM, STEALTH_SYSTEM, DIRT_SYSTEM).
- Clarified power_level_policy semantics: runtime storage, toggle event payload, and validation for FIXED_100.
- Clarified range_policy semantics, including NONE, and aligned preamble math to policy-based range.
- Normalized single-range param naming to base_range_m (fixed NIGHT_VISION DB_SPEC param key).
@@END:PATCH.NOTES@@

Ниже у каждого заклинания указаны:
SpellID
ConcentrationCost
BaseLoadCP
Что делает
Сила / Дальность / Время (сек.)
Как считается нагрузка и эффект
Ограничения и визуальные признаки (если есть)
Барьер
@@END:B12.SPELLS.QA.40@@
@@BEGIN:B12.SPELLS.DATA.42@@
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
Алгоритм события “осмотр/лут”:
ARROW_RECOVER_RNG_CANON (MVP)
• UI/DATA: RecoverChancePct:int (0..100). Core: RecoverChanceBp = clamp_int(RecoverChancePct*100, 0, 10000).
• Для каждого кандидата-стрелы i (0..SpentArrows-1) после фильтрации 'физически недоступных':
- rng_stream=RNG_LOOT; context='spell.arrow_recover'; scope_id=(scene_id, actor_id, spell_id_or_instance_id); draw_index=i.
- draw=rand_int(0..9999); success = (draw < RecoverChanceBp).
• Draw spec: ровно 1 draw на 1 стрелу-кандидата.
клиент берёт число потраченных стрел в сцене: SpentArrows
для каждой из этих стрел выполняется проверка с шансом RecoverChancePct
каждое успешное срабатывание возвращает 1 стрелу в колчан/инвентарь
стрелы, помеченные как физически недоступные, не участвуют в проверке (см. ограничения)
Дальность
Только на владельца (работает на его потраченные стрелы).
Период
Заклинание действует постоянно, пока поддерживается. Эффект проявляется только в момент события “осмотр/лут”.
Ограничения
Если стрела физически недоступна (упала в пропасть, сгорела, унесена водой, осталась в недоступной зоне) — она не может быть возвращена и не участвует в проверке.
Заклинание не создаёт новые стрелы, не клонирует и не “материализует” их — только повышает вероятность восстановления реально существующих.
Фокус щита
@@END:B12.SPELLS.DATA.42@@
@@BEGIN:B12.SPELLS.DATA.43@@
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
Формат пула (LOOT_POOL)
Формат кофера (COFFER)
@@END:B12.SPELLS.DATA.43@@
@@BEGIN:B12.SPELLS.CANON.131@@
REF: перенесено в @@BEGIN:B24.LOOT.CANON.10@@ ... @@END:B24.LOOT.CANON.10@@ (B24 — LOOT).
NOTE: якорь B12.SPELLS.CANON.131 сохранён как alias для обратной совместимости.
@@END:B12.SPELLS.CANON.131@@
@@BEGIN:B12.SPELLS.CANON.132@@
REF: перенесено в @@BEGIN:B24.LOOT.CANON.11@@ ... @@END:B24.LOOT.CANON.11@@ (B24 — LOOT).
NOTE: якорь B12.SPELLS.CANON.132 сохранён как alias для обратной совместимости.
@@END:B12.SPELLS.CANON.132@@
@@BEGIN:B12.SPELLS.CANON.133@@
REF: перенесено в @@BEGIN:B24.LOOT.CANON.12@@ ... @@END:B24.LOOT.CANON.12@@ (B24 — LOOT).
NOTE: якорь B12.SPELLS.CANON.133 сохранён как alias для обратной совместимости.
@@END:B12.SPELLS.CANON.133@@
@@BEGIN:LOOT.COFFERS.ITEM_GRANT_VIA_COFFERS_RULE@@
REF: спецификация LOOT/COFFER перенесена в B24 (LOOT):
- @@BEGIN:B24.LOOT.CANON.12@@ ... @@END:B24.LOOT.CANON.12@@ (RNG/Scope для LOOT_OPEN)
- @@BEGIN:B24.LOOT.CANON.13@@ ... @@END:B24.LOOT.CANON.13@@ (ITEM_GRANT_VIA_COFFERS)
- @@BEGIN:B24.LOOT.DATA.10@@ ... @@END:B24.LOOT.DATA.10@@ (SOURCE->COFFER_ID)
- @@BEGIN:B24.LOOT.CANON.14@@ ... @@END:B24.LOOT.CANON.14@@ (COFFER_OPEN_CANON)
@@END:LOOT.COFFERS.ITEM_GRANT_VIA_COFFERS_RULE@@
@@BEGIN:B12.SPELLS.CANON.134@@
REF: перенесено в @@BEGIN:B24.LOOT.CANON.13@@ ... @@END:B24.LOOT.CANON.13@@ (B24 — LOOT).
NOTE: якорь B12.SPELLS.CANON.134 сохранён как alias для обратной совместимости.
@@END:B12.SPELLS.CANON.134@@
@@BEGIN:B12.SPELLS.DATA.44@@
REF: перенесено в @@BEGIN:B24.LOOT.DATA.10@@ ... @@END:B24.LOOT.DATA.10@@ (B24 — LOOT).
NOTE: якорь B12.SPELLS.DATA.44 сохранён как alias для обратной совместимости.
@@END:B12.SPELLS.DATA.44@@
Алгоритм открытия ресурсного кофера (COOK/ALCH/CRAFT)
@@BEGIN:B12.SPELLS.CANON.135@@
REF: перенесено в @@BEGIN:B24.LOOT.CANON.14@@ ... @@END:B24.LOOT.CANON.14@@ (B24 — LOOT).
NOTE: якорь B12.SPELLS.CANON.135 сохранён как alias для обратной совместимости.
@@END:B12.SPELLS.CANON.135@@
@@BEGIN:B12.SPELLS.DATA.45@@
REF: перенесено в @@BEGIN:B24.LOOT.DATA.11@@ ... @@END:B24.LOOT.DATA.11@@ (B24 — LOOT).
NOTE: якорь B12.SPELLS.DATA.45 сохранён как alias для обратной совместимости.
@@END:B12.SPELLS.DATA.45@@
@@BEGIN:B12.SPELLS.DATA.46@@
REF: перенесено в @@BEGIN:B24.LOOT.DATA.12@@ ... @@END:B24.LOOT.DATA.12@@ (B24 — LOOT).
NOTE: якорь B12.SPELLS.DATA.46 сохранён как alias для обратной совместимости.
@@END:B12.SPELLS.DATA.46@@
@@BEGIN:B12.SPELLS.DATA.47@@
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
SHIELD_PROC_CANON (MVP)
• Shield (щит) — предмет в руке. Шанс срабатывания задаётся данными предмета:
- ShieldProcMeleeChanceBp:int (0..10000)
- ShieldProcRangedChanceBp:int (0..10000)
• Проверка: draw = rand_int(0..9999); success = (draw < ChanceBp).
• RNG key (keyed): rng_stream=RNG_COMBAT; context='combat.shield_proc'; scope_id=(combat_id, actor_id, target_id, round_index, action_seq); draw_index=0.
• Конкретные значения (например 5000/3000) — это [DATA] balance, не канон текста.

@@END:B12.SPELLS.DATA.47@@@@END:B12.SPELLS@@
@@END:B12@@
@@BEGIN:B13@@
## B13 — PRODUCTION: кулинария, алхимия, крафт, легендарное
КУЛИНАРИЯ (COOKING)
Кулинария — это простой слой выживания: уменьшает Голод/Жажду, помогает держать EffectiveMaxHP “в норме”, даёт редкие мягкие бонусы (без новых систем).
Шкалы и что делает еда (вписывается в общий стандарт T1–T5)
Голод (HUNGER) и Жажда (THIRST) — стадийные шкалы 0…100%, где 0% = всё ок, 100% = критично.
Тиры считаются по общим порогам:
T1: ≥ 20%
T2: ≥ 40%
T3: ≥ 60%
T4: ≥ 80%
T5: ≥ 95%
Важно (стыковка с HP):
Голод режет EffectiveMaxHP с T3+, Жажда — с T2+ (опаснее голода).
Еда/эликсиры/магия не могут лечить выше EffectiveMaxHP (если “стакан сжался” дебаффами — лечишься только до него).
Смерть только по правилу: HP ≤ 0.
Базовая механика готовки (без нагромождения)
Что нужно:
Источник тепла (костёр/печь/жаровня) + простая посуда (котелок ИЛИ сковорода).
Если нет тепла/посуды — можно есть только ингредиенты “как есть” (см. ниже), блюдо приготовить нельзя.
Как работает приготовление:
Рецепт всегда = 3 компонента (3 слота).
Тир блюда определяется строгой “формулой” (чтобы клиент мог проверять автоматически):
T1 блюдо = ингредиент + ингредиент + ингредиент
T2 блюдо = ингредиент + ингредиент + блюдо T1
T3 блюдо = блюдо T1 + блюдо T1 + блюдо T2
Время (в секундах; для UI можно округлять до шагов 10 сек):
T1: 30 сек
T2: 60 сек
T3: 120 сек
(В бою готовка обычно недоступна как действие — это “вне боя”. В бою можно только USE_ITEM: съесть/выпить готовое.)
Навык «Кулинария» (MVP): • В MVP нет отдельной шкалы навыка и нет XP. • Доступ к рецептам/тирам блюд определяется access_tier и перками (progress), без бросков и без случайностей. • Приготовление не вводит проверок “успех/провал”: если есть ингредиенты и условия, блюдо готовится гарантированно.
Стандарт эффектов еды (чтобы баланс был читаемый)
Каждый съедобный объект имеет эффекты:
HungerDownPct: на сколько п.п. уменьшает шкалу Голод (HUNGER)
ThirstDownPct: на сколько п.п. уменьшает шкалу Жажда (THIRST)
HPDelta: мгновенное лечение/урон по HP (опционально; лечение не выше EffectiveMaxHP)
FoodPoisonChancePct: шанс FOOD_POISONING (обычно только у сырого/сомнительного)
Правило случайностей:
Правило вероятностей (ChanceBp 0..10000 и проверка draw=rand_int(0..9999)) — см. B04 [CANON: FIXED-POINT].
[DATA NOTICE — NON-NORMATIVE]
Следующие списки ингредиентов/блюд приведены как пример/контент и НЕ являются каноном.
Источник истины: DB_SPEC::cooking_* / content packs. При конфликте чисел побеждает канон правил (B04/B05 и др.).
Ингредиенты (сырые) — пак
Примечание: “сырое” — это не “запрещено”, это “риск/побочка”.
4_1 Растительные ингредиенты (PLANT_ING)
Ягоды (berries)
HungerDownPct: 4 ThirstDownPct: 6 HPDelta: 0 FoodPoisonChancePct: 0
Яблоко/плод (fruit)
HungerDownPct: 6 ThirstDownPct: 5 HPDelta: 0 FoodPoisonChancePct: 0
Корнеплод (root)
HungerDownPct: 7 ThirstDownPct: 1 HPDelta: 0 FoodPoisonChancePct: 0
Зелень/листья (greens)
HungerDownPct: 3 ThirstDownPct: 2 HPDelta: 0 FoodPoisonChancePct: 0
Лук дикий (wild_onion)
HungerDownPct: 2 ThirstDownPct: 0 HPDelta: 0 FoodPoisonChancePct: 0
Травы/пряности (herbs_spices)
HungerDownPct: 1 ThirstDownPct: 0 HPDelta: 0 FoodPoisonChancePct: 0
Орехи (nuts)
HungerDownPct: 8 ThirstDownPct: -2 HPDelta: 0 FoodPoisonChancePct: 0
Зерно (grain)
HungerDownPct: 5 ThirstDownPct: -1 HPDelta: 0 FoodPoisonChancePct: 0
Мука (flour)
Сырое есть можно, но “сухомятка”.
HungerDownPct: 4 ThirstDownPct: -4 HPDelta: 0 FoodPoisonChancePct: 0
Грибы “не обработанные” (raw_mushroom)
Негатив: риск отравления + лёгкий урон.
HungerDownPct: 3 ThirstDownPct: 1 HPDelta: -1 FoodPoisonChancePct: 25
Сушёные ягоды (dried_berries)
HungerDownPct: 6 ThirstDownPct: -3 HPDelta: 0 FoodPoisonChancePct: 0
Капуста/жёсткие овощи (cabbage_veg)
HungerDownPct: 6 ThirstDownPct: 2 HPDelta: 0 FoodPoisonChancePct: 0
Бобовые (beans)
Сырыми тяжело: можно, но неприятно.
HungerDownPct: 6 ThirstDownPct: -2 HPDelta: 0 FoodPoisonChancePct: 5
4_2 Животные ингредиенты (ANIMAL_ING)
Сырое мясо (raw_meat)
Негатив: риск FOOD_POISONING + урон по HP.
HungerDownPct: 10 ThirstDownPct: -2 HPDelta: -2 FoodPoisonChancePct: 30
Сырая рыба (raw_fish)
HungerDownPct: 8 ThirstDownPct: -1 HPDelta: -1 FoodPoisonChancePct: 20
Жир/сало (fat)
HungerDownPct: 10 ThirstDownPct: -4 HPDelta: 0 FoodPoisonChancePct: 0
Яйцо сырое (raw_egg)
HungerDownPct: 6 ThirstDownPct: -1 HPDelta: 0 FoodPoisonChancePct: 10
Молоко (milk)
HungerDownPct: 5 ThirstDownPct: 4 HPDelta: 0 FoodPoisonChancePct: 5
Сыр (cheese)
HungerDownPct: 8 ThirstDownPct: -2 HPDelta: 0 FoodPoisonChancePct: 0
Кости/обрезь (bones_trimmings)
Сырыми не едят (в рецептах для бульона).
HungerDownPct: 0 ThirstDownPct: 0 HPDelta: 0 FoodPoisonChancePct: 0
Словарь алиасов → канонический ID (для данных клиента): raw_meat → ING_MEAT_RAW raw_fish → ING_FISH_RAW raw_mushroom → ING_MUSHROOM_RAW raw_berries → ING_BERRY_RAW dried_berries → ING_BERRY_DRIED cabbage → ING_CABBAGE wild_onion → ING_ONION_WILD greens → ING_GREENS nuts → ING_NUTS beans → ING_BEANS herbs_spices → CMP_SPICE_MIX fat → ING_FAT raw_egg → ING_EGG_RAW milk → ING_MILK cheese → ING_CHEESE bones_trimmings → ING_BONES_TRIMMINGS water_clean → CMP_CLEAN_WATER (или CNT_WATERSKIN_* как контейнер жидкости)
Блюда (до T3) — пак рецептов
Правило: приготовленное блюдо “снимает” риски сырого продукта (FoodPoisonChancePct = 0), если не указано иначе.
5_1 Блюда T1 (ING + ING + ING)
Шашлык охотника (DISH_T1_HUNTER_SKEWER)
Рецепт: raw_meat + wild_onion + herbs_spices
Эффект: HungerDownPct 18, ThirstDownPct 0, HPDelta +2
Жареная рыба с зеленью (DISH_T1_FISH_FRY)
Рецепт: raw_fish + greens + herbs_spices
Эффект: HungerDownPct 16, ThirstDownPct 0, HPDelta +2
Грибная сковорода (DISH_T1_MUSHROOM_PAN)
Рецепт: raw_mushroom + wild_onion + herbs_spices
Эффект: HungerDownPct 14, ThirstDownPct 0, HPDelta +1
Сырная лепёшка (DISH_T1_CHEESE_FLATBREAD)
Рецепт: flour + cheese + raw_egg
Эффект: HungerDownPct 18, ThirstDownPct -2, HPDelta +2
Орехово-ягодный перекус (DISH_T1_NUT_BERRY_MIX)
Рецепт: nuts + berries + dried_berries
Эффект: HungerDownPct 16, ThirstDownPct 3, HPDelta 0
Травяной настой (DISH_T1_HERB_TEA)
Рецепт: herbs_spices + berries + greens
Эффект: HungerDownPct 4, ThirstDownPct 18, HPDelta 0
Овощная похлёбка (лёгкая) (DISH_T1_VEG_PORRIDGE)
Рецепт: root + cabbage_veg + herbs_spices
Эффект: HungerDownPct 14, ThirstDownPct 6, HPDelta +1
Сытная яичница (DISH_T1_EGG_PAN)
Рецепт: raw_egg + fat + wild_onion
Эффект: HungerDownPct 16, ThirstDownPct -2, HPDelta +2
Молочно-зерновая каша (DISH_T1_MILK_GRAIN)
Рецепт: milk + grain + herbs_spices
Эффект: HungerDownPct 16, ThirstDownPct 6, HPDelta +1
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
АЛХИМИЯ (ALCHEMY)
Роль алхимии в игре
Алхимия — ключевая система выживания и усилений, которая:
даёт ранний доступ к лечению/регену (баланс выздоровления завязан на зельях),
помогает работать с травмами/состояниями (кровотечение/кровопотеря, боль, инфекция),
даёт временные баффы статов (плоские и процентные),
даёт эндгейм-крафт: редкие многосоставные эликсиры, которые перманентно повышают характеристики.
Базовый предохранитель баланса: любое лечение и реген не может поднять HP выше EffectiveMaxHP.
Базовые сущности алхимии
2_1 Ингредиент (RAW)
Сырьё. Не даёт алхимических свойств, пока не обработано.
Параметры RAW:
происхождение: plant / animal / undead / mineral / legendary
состояние: свежий / нормальный / испорченный / загрязнённый (влияет на качество Q и риск побочек, но не вводит “скверну”)
редкость: common / uncommon / rare / epic / legendary
2_2 Реагент (REAGENT)
Результат обработки RAW. Используется в рецептах.
Аспекты реагентов (10 шт., достаточно на всю алхимию): VITAL / BLOOD / CLEAN / PAIN / HEAT / IRON / GRACE / MIND / SWIFT / VOID
2_3 Зелье/сыворотка (POTION)
Готовый продукт (эффект, длительность, вклад в INTOX).
Обработка ингредиентов (обязательный этап)
Правило: большинство рецептов использует только реагенты, а не сырьё.
3_1 Инструменты (минимум)
ступка/пестик (помол)
котёл/кастрюля (выварка/упаривание)
фильтр/марля/уголь (фильтрация/очищение)
колбы/флаконы
перегонный куб/алембик (дистилляция)
тигель/горн (кальцинация)
3_2 Операции обработки (время в секундах; шаг квантизации 10 сек для UI/лога)
Сушка — 600 сек
Помол — 60 сек
Настой — 600 сек
Выварка — 600 сек
Упаривание — 300 сек
Фильтрация — 60 сек
Очищение (уголь/серебро) — 120 сек
Дистилляция — 900 сек
Кальцинация — 600 сек
Стабилизация (соль/масло/смола) — 60 сек
Качество зелий (Q1–Q5)
Эффекты ниже — Q2 (обычное). Множитель силы/длительности:
Q1: 8000bp
Q2: 10000bp
Q3: 12000bp
Q4: 14000bp
Q5: 17000bp
Q влияет на силу/длительность/побочки/иногда выход (2 флакона на высоком Q).
Алхимическая интоксикация (INTOX) T1–T5
Единый балансир “алхимического спама”. INTOX растёт от употребления зелий, снижается со временем/отдыхом/водой/детоксом.
5_1 Нарастание INTOX при употреблении
медицина/хил/антисептик/коагулянт: +1
сыворотки баффов (процентные): +2
овердрайвы (боевые): +4
если в рецепте есть VOID (полная доза, не микродоза): +1 дополнительно
если Q1: +1 дополнительно
5_2 Ограничение по INTOX (просто и жёстко)
при INTOX T3+ запрещено употреблять сыворотки и овердрайвы, разрешены только медицина + детокс (так алхимия остаётся сильной, но не бесконечной)
Использование зелий (Action)
Выпить — 1 Action
Нанести на рану (антисептик/коагулянт) — 1 Action
Крафт обычно вне боя (или отдельными “крафтовыми действиями” по клиенту)
СТАРТОВЫЙ КОНТЕНТ : 15 RAW + 10 REAGENT + 10 базовых зелий
[CANON] PRODUCTION_DATA_RELOCATION: списки RAW/REAGENT/POTION/рецептов и любые конкретные значения эффектов/времён — это [DATA] и должны жить в content packs / DB_SPEC (DB_SPEC::alchemy_*, DB_SPEC::cooking_*).
В концепте остаются только: формат сущностей, правило времени в секундах (time_sec:int), deterministic craft (без RNG если не указано), caps/clamps и правила INTOX.
Мини-добавка для клиента (чтобы мастер вообще не думал)
По аналогии с твоим боевым CHANGELOG:
CRAFT_START {recipe_id, station_id, qty}
CRAFT_COMPLETE {recipe_id, consume, produce} (legacy alias: CRAFT_DONE {item_id, qty})
SALVAGE_START {item_id, station_id}
SALVAGE_DONE {outputs…}
LEGENDARY_INFUSE {base_item_id, leg_core_id}
Это позволит клиенту считать всё сам, а мастер пусть остаётся “голосом мира”, а не бухгалтером кузницы

@@END:B13@@
@@BEGIN:B14@@
## B14 — ITEMS: инвентарь, контейнеры, формат предметов
CONTAINERS / АССОРТИМЕНТ КОНТЕЙНЕРОВ
[CANON] Вес предметов и стак (ITEMS)
• Единица веса: граммы. Поле предмета: weight_g_per_unit:int (>=0). Все расчёты веса — только int.
• Стак: stack_count:int (>=1). Вес стака: stack_weight_g = weight_g_per_unit * stack_count.
• Учет переносимого веса: CarriedWeight_g = Σ stack_weight_g по инвентарю + экипировка + содержимое контейнеров (см. [CANON] Контейнеры).
[CANON] DB_FILL_PATCH::STACK_MODEL_SPLIT (MVP)
• ItemDefinition.stack_max:int>=1 — максимум единиц в одном стэке (DB_SPEC item-карточек).
• ItemInstance.qty:int>=1 — текущее количество единиц в инстансе/стэке (save/changelog).
• Legacy alias (без миграции): stack_count == qty (инстанс-уровень) и stack_count в item-card == stack_max; loader/build-step нормализует в canonical поля.
• Вес инстанса: weight_g = weight_g_per_unit * qty (int).
• Merge разрешён только если item_id совпадает и meta совместимо (см. NO_MIX_META). Partial consume разрешён; пустой стэк удаляется (INVENTORY_REM).
[CANON] DB_FILL_PATCH::ITEM_INSTANCE_CONTRACT (MVP)
• ItemInstance: item_instance_id (immutable), item_id, qty, is_identified:bool, instance_tags_add[] (опц.), meta_kv (опц.; только примитивы).
• NO_MIX_META: merge/split/transfer запрещены, если meta_kv различается (если нужно — сначала “очистка/снятие” меты явным событием).
• Подсистемы обязаны явно указывать, работают ли они по ItemDefinition.tags[] или по instance_tags_add[].
• Запрещено хранить “текущее состояние” (qty/is_identified/instance_tags/meta_kv) в ItemDefinition.
[CANON] DB_FILL_PATCH::STABLE_SERIALIZATION (MVP)
• Все массивы *_id без семантического порядка сериализуются отсортированными asc (canonical form).
• Выбор удаляемых предметов (consume/deliver/craft inputs) детерминирован: candidates сортируются по item_instance_id asc; затем списание по qty до выполнения.
• Для операций с кандидатами (TRANSFER/HOME_TRANSFER/SHOP_SELL/CRAFT_CONSUME) применяется тот же stable order; UI-порядок игнорируется.
• Explain/replay фиксируют stable ordering (иначе replay-diff шумит).

[CANON] Контейнеры (CONTAINERS)
• Контейнер — предмет с полями: container_capacity_g:int(>=0), container_self_weight_g:int(>=0), optional allowed_categories[], optional carry_bonus_g:int.
• Инвариант вместимости: Σ weight_g(contents) <= container_capacity_g (валидация до запуска и при TRANSFER).
• Вес контейнера в переносимом весе: container_total_weight_g = container_self_weight_g + Σ weight_g(contents).
[DATA] Ниже — DB_SPEC::items (каталог предметов). Все конкретные числа/веса/стаки/редкости — данные контент-паков; канон — только формат и валидаторы.
[CANON] CURRENCY_MODEL (MVP):
• Экономика использует одну валюту: CU (целое число, хранится как inventory.currency.cu:int).
• Любые “монеты/слитки/ценности” в каталоге предметов — это [DATA] trade goods/лут для нарратива/визуала.
• В MVP запрещено вводить несколько валютных балансов. Если монеты используются как предметы, их ценность конвертируется в CU только на уровне контента/UX и не меняет канон расчётов.
[DATA NOTICE — NON-NORMATIVE]
Следующий каталог предметов/валюты приведён как контентный пример.
Источник истины: DB_SPEC::items (SQLite) / content packs. Канон B14 — только формат полей/валидаторы.
ECON / ВАЛЮТА + ЦЕННОСТИ
========================
CUR_COIN_COPPER — Монета медная
Тип: TRADE_GOOD
Группа: ECON
Класс: CURRENCY
МатКачество: —
Редкость: common
Стак: да (999)
weight_g_per_unit: 5
Назначение: мелкие покупки/сдача
Получение: лут/награды/обмен
CUR_COIN_SILVER — Монета серебряная
Тип: TRADE_GOOD
Группа: ECON
Класс: CURRENCY
МатКачество: —
Редкость: common
Стак: да (999)
weight_g_per_unit: 10
Назначение: основная валюта
Получение: лут/награды/обмен
CUR_COIN_GOLD — Монета золотая
Тип: TRADE_GOOD
Группа: ECON
Класс: CURRENCY
МатКачество: —
Редкость: uncommon
Стак: да (999)
weight_g_per_unit: 10
Назначение: крупные сделки/услуги
Получение: редкий лут/награды/обмен
TRD_FUR_BUNDLE — Связка мехов
Тип: TRADE_GOOD
Группа: ECON
Класс: TRADE_GOOD
МатКачество: Q1–Q5
Редкость: common
Стак: да (10)
weight_g_per_unit: 1500
Назначение: продажа/ремесло (кожа/одежда по рецептам)
Получение: лут с животных/покупка
TRD_GEM_CHIP — Осколок самоцвета
Тип: TRADE_GOOD
Группа: ECON
Класс: TRADE_GOOD
МатКачество: Q1–Q5
Редкость: uncommon
Стак: да (99)
weight_g_per_unit: 50
Назначение: продажа/иногда ингредиент эндгейма
Получение: лут/коферы
TRD_OLD_RELIC — Старинная реликвия
Тип: TRADE_GOOD
Группа: ECON
Класс: TRADE_GOOD
МатКачество: Q1–Q5
Редкость: rare
Стак: нет
weight_g_per_unit: 500
Назначение: продажа/редкая награда
Получение: лут/коферы/события
====================
WATER / ТАРА И ВОДА
====================
==========================
SURVIVAL / БЫТОВЫЕ УТИЛИТЫ
==========================
MED_BANDAGE — Бинт
Тип: CONSUMABLE
Группа: MED
Класс: CONSUMABLE
МатКачество: Q1–Q5
Редкость: common
Стак: да (20)
weight_g_per_unit: 50
Назначение: перевязка (сценарное “остановить кровотечение/кровопотерю”)
Получение: крафт/покупка/лут
MED_ANTISEPTIC — Антисептик
Тип: CONSUMABLE
Группа: MED
Класс: CONSUMABLE
МатКачество: Q1–Q5
Редкость: uncommon
Стак: да (10)
weight_g_per_unit: 150
Назначение: обработка ран/профилактика осложнений
Получение: алхимия/покупка
=========================
COOKING / РАСТИТЕЛЬНЫЕ ИНГРЫ
=========================
COOKING / ИНГРЫ (ЖИВОТН.)
=========================
COOKING / БЛЮДА (ГОТОВЫЕ)
=========================
COOKING / ИНСТРУМЕНТЫ ГОТОВКИ
=========================
ALCH / БАЗОВЫЕ АЛХИМ-ИНГРЫ
=========================
ALCH / ЗЕЛЬЯ И СЫВОРОТКИ (КАНОНИЧЕСКИЕ ITEM-ID)
=========================
ALCH / ОВЕРДРАЙВЫ (боевые, без отката; упираются в INTOX)
ALCH / НАСЛЕДИЕ (перманентные усиления; эндгейм)
METAL / РУДЫ → СЛИТКИ → ЗАГОТОВКИ
=========================
PLATE_IRON — Пластина железная
Тип: MATERIAL
Группа: CRAFT_METAL
Класс: MATERIAL
МатКачество: Q1–Q5
Редкость: common
Стак: да (50)
weight_g_per_unit: 1000
Назначение: броня/оружие (заготовка)
Получение: кузня/крафт
WIRE_IRON — Проволока железная (моток)
Тип: MATERIAL
Группа: CRAFT_METAL
Класс: MATERIAL
МатКачество: Q1–Q5
Редкость: uncommon
Стак: да (50)
weight_g_per_unit: 200
Назначение: крепёж/кольца/ремесло
Получение: кузня/крафт
MAIL_RING_IRON — Кольца кольчуги (пучок)
Тип: MATERIAL
Группа: CRAFT_METAL
Класс: MATERIAL
МатКачество: Q1–Q5
Редкость: common
Стак: да (50)
weight_g_per_unit: 300
Назначение: кольчужная броня (заготовка)
Получение: кузня/крафт
=========================
LEATHER/TEXTILE / КОЖА, ТКАНЬ, ФУРНИТУРА
=========================
RAW_HIDE — Шкура сырая
Тип: RAW
Группа: CRAFT_LEATHER
Класс: MATERIAL
МатКачество: Q1–Q5
Редкость: common
Стак: да (20)
weight_g_per_unit: 1200
Назначение: выделка кожи
Получение: лут с животных
=========================


@@END:B14@@
@@BEGIN:B15@@
## B15 — WORLD: лор, город, башня, территории
ЛОР И МИР (v1): ПАДЕНИЕ ЦИВИЛИЗАЦИИ, ГОРОД И БАШНЯ
Этот лор специально написан так, чтобы не требовать новых механик: всё объясняется через уже существующие системы (нежить = монстры, аномалии = зоны/ресурсы, прогресс = крафт/тиражи/боссы).
Что случилось с миром (короткая хронология)
• Эпоха Машин: до падения существовала техно-цивилизация. Мир был связан сетью энергетических узлов и “городов-узлов”.
• Ночь Тишины: сеть вышла из строя каскадом. Электричество умерло не “везде сразу”, а пятнами. Начались голод, миграции, войны за остатки инфраструктуры.
• Башня проснулась: в центре одного города активировалась Башня — древний автономный комплекс, который начал “перезапуск” собственной логики безопасности.
• Падение стен: город выжил, когда вокруг него возвели стену из разборных модулей/камня/железа (как решишь визуально). Внутри — анклав ремесла. Снаружи — дикая зона.
Природа нежити (без “скверны”, но логично)
Рабочая теория (и она же “правда лора”): нежить — это не магия, а сбой “похоронных протоколов” Башни.
Башня умеет собирать биомассу и создавать обслуживающих “трудовых марионеток” (скелеты-слуги, костяные стражи). После катастрофы она потеряла критерии “свой/чужой/живой” и стала поднимать всех погибших в зоне доступа как “материал”.
Отсюда понятные факты для игрока:
• Нежить чаще вокруг Башни и в руинах инфраструктуры (там, где сохранились узлы энергии).
• Чем глубже этажи — тем “умнее” и страннее формы (больше INT/контроль/барьер у боссов).
• Вне зон — нежити меньше, но есть зверьё/мутировавшая фауна (у тебя уже есть FOREST-контент).
[DATA] Каталог NPC вынесен в DB_SPEC::npcs. В концепте остаются: поля NPC, services[] и привязки к LOC/SHOP/QUEST.
ГОРОД-ХАБ (v0.6_3): протокол данных + лор + квест-пак
Город — это безопасная (в основном) логистическая машина: подготовка → рейд → разбор добычи → восстановление → снова в темноту.
Ключевые роли города:
• Рынок/Снабжение — расходники, контейнеры, стрелы, базовые инструменты.
• Мастерские — ремонт, обслуживание станков (кузня/кожевня/алхимия/кулинария).
• Лазарет — лечение травм/инфекций (как услуга, без новых механик).
• Архив/Библиотека — идентификация материалов, знания о Башне, выдача сюжетных контрактов.
• Ворота/Казармы — контракты, безопасность, доступ за стену.
• Башенный квартал/Коллектор — рискованные короткие пути и редкие сделки.
Минимальный протокол данных (чтобы клиент мог считать город так же, как предметы):
• LOC (район/точка): loc_id, name_ru, kind, services[], tags[], description, extra{neighbors[], npc_slots[]}.
• FACTION: faction_id, name_ru, motto, services[], description, tags[].
• NPC: npc_id, name_ru, role, faction_id, home_loc_id, services[], shop_id?, quest_board(0/1), schedule{}, dialogue_hints.
• SHOP: shop_id, name_ru, loc_id, npc_id?, kind, price_policy{}, restock{}, inventory[item_id,qmin,qmax,stock_min,stock_max,price_base] (правила цен/рестока/торговых операций см. раздел “ЭКОНОМИКА ГОРОДА И КВЕСТ-ПЕТЛЯ (S3, канон)”).
• QUEST: quest_id, title_ru, giver_npc_id, loc_id, tier_min/tier_max, kind, objective{steps[]}, rewards{}, repeatable (правила доски контрактов/офферов/депозита/жизненного цикла см. раздел “ЭКОНОМИКА ГОРОДА И КВЕСТ-ПЕТЛЯ (S3, канон)”).
Пак города добавлен в базы (см. json/city_pack.json):
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
Примечание по интеграции: городские сущности заведены отдельными таблицами city_* в SQLite (не ломают существующие items/recipes/pools).
S3 Checklist (сводный)
CHANGELOG события (минимум): SHOP_RESTOCK_APPLY, SHOP_BUY, SHOP_SELL, SERVICE_PAY, QUEST_TAKE, QUEST_UPDATE, QUEST_COMPLETE, QUEST_FAIL, QUEST_ABANDON, TIME_ADVANCE (если используется).
Валидации: qmin<=qmax; stock_min<=stock_max; stock>=0; 0<=BUY_MULT<1; SELL_MULT>1; fee_exch_bp<=2000; spred invariant; repeatable->cooldown_sec>=1; progress 0..required; MAX_ACTIVE_CONTRACTS соблюдён.
Save (минимум): inventory.currency.cu; economy.last_applied_day_index; economy.shop_state[shop_id]{last_restock_day, stock map}; quest_state.active_instances; quest_state.cooldowns; applied_event_ids (idempotency guard).
Content (минимум): city_shops(shop_id,kind,price_policy,restock,inventory[]); exchange_rules(buy/sell/fee, tag_priority, rate_by_tag); city_services(provider->services); repair_rules(output_coffer_by_input_item_id / repair_yield_coffer_id); city_quests(templates with extra{board_weight,offer_ttl_days,cooldown_sec}).
ерритории за стеной — Лес (OUTWALLS_FOREST)
Суть региона: зона вылазок за городские стены. Это не «второй город», а полевой контент: охота, сбор, разведка, зачистки, редкие находки. Опасность и ценность наград растут по мере удаления от стены.
Жёсткие правила совместимости (чтобы не конфликтовать с уже созданным миром):

@@END:B15@@
@@BEGIN:B16@@
## B16 — BESTIARY: монстры и встречи
BESTIARY (v1_1) — стандарт + пак монстров (лес + башня)
Стандарт карточки монстра
Карточка:
MonsterID
Type: MONSTER
Region: OUTWALLS_FOREST | TOWER
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
ближний бой, преследование
при низком HP — чаще отступает
MON_FO_BOAR_PIGLET — Молодой кабан
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
ближний бой; если держат дистанцию — MOVE → удар
MON_FO_RAVEN_SWARM — Воронья туча
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
если может — SENSORY, затем LIGHT
если цель далеко — MOVE
MON_FO_WOLF_SCOUT — Волк-разведчик
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
обход/сближение, затем ближний бой
при наличии союзников: чаще “поддавливает темпом”
(RARE) MON_FO_SKUNK_SPRAYER — Скунс-распылитель
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
SENSORY → укус → отход
при низком HP — уходит
(RARE) MON_FO_TICK_SWARM — Клещи (стая)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
липнет к ближайшей цели, почти не отступает
(RARE) MON_FO_GOOSE_GUARD — Дикая гусыня-страж
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
HISS → PECK, преследует
(VAR) MON_FO_WOLF_SCOUT_NIGHT — Волк-разведчик (ночной)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
чаще SENSORY, затем врыв
2_2 FOREST_RING_2 (T2) — лес огрызается
MON_FO_WOLF_PACKHUNTER — Волк-охотник стаи
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
ближний бой, преследование
MON_FO_BOAR_ADULT — Кабан-секач
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
если дистанция >1: MOVE → CHARGE
иначе давит ближним
MON_FO_SNAKE_VENOM — Ядовитая змея
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
hit&run: удар → отход
MON_FO_SPIDER_HUNTERLING — Паук-охотник (молодой)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
TRAP на дистанции, затем врыв
MON_FO_BEAR_YOUNG — Молодой медведь
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
ближний бой, чаще HEAVY против “танчащих”
(RARE) MON_FO_LYNX_STALKER — Рысь-скиталец
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
MOVE → POUNCE, затем отход (hit&run)
(RARE) MON_FO_STONEBACK_TURTLE — Камнеспинная черепаха
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
стоит “стеной”, почти не двигается
(RARE) MON_FO_WASP_NEST — Осиное гнездо (рой)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
держит 1–2м, давит темпом
(RARE) MON_FO_RIVER_PIKE — Речной щукарь (прибрежные чанки)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
предпочитает врыв (особенно “у воды”)
(VAR) MON_FO_BOAR_ADULT_RAZOR — Кабан-секач (бритва-клык)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
преследует агрессивнее обычного секача
(VAR) MON_FO_BEAR_YOUNG_CURSED — Молодой медведь (шрамованный)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
чаще выбирает HEAVY
2_3 FOREST_RING_3 (T3) — появляются элиты
MON_FO_DIREWOLF — Лютоволк
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
фокус по слабой цели, преследование
MON_FO_OWL_STALKER — Ночной филин-охотник
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
SENSORY при возможности, затем врыв
MON_FO_MOSS_TROLL — Моховой тролль
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
ближний бой, давит “стеной”
MON_FO_BRIAR_ENT_SAPLING — Терновый энт (саженец)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
меньше MOVE, держит позицию
MON_FO_SPIDER_HUNTER — Паук-охотник (взрослый)
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
TRAP → врыв → повтор TRAP
(RARE) MON_FO_MIST_STALKER — Туманник
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
SENSORY → сближение → LIGHT
(RARE) MON_FO_FUNGUS_SHAMBLER — Грибной шатун
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
TRAP по группе/быстрым целям, иначе HEAVY
(RARE) MON_FO_BOG_LEECH_MASS — Болотная пиявочная масса
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
TRAP на “быстрых”, затем REND
(RARE) MON_FO_BRUTE_BADGER — Бешеный барсук
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
всегда в ближний, чаще HEAVY против “танков”
2_4 FOREST_RING_4 (T4) — опасная зона
MON_FO_ANCIENT_BEAR — Старый медведь
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
давит ближним, наказывает темпом
MON_FO_STAG_CHARGER — Олень-таран
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
дистанция → MOVE → CHARGE
в упоре делает шаг и снова CHARGE (ритм боя)
MON_FO_ROOT_GOLEM — Корневой голем
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
бросок на дистанции, crush вблизи
(RARE) MON_FO_GIANT_STAG_KING — Великий олень-король
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
любит разбег/врыв, в упоре STOMP
(RARE) MON_FO_THORN_BRAMBLEHOUND — Терновый гончий
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
TRAP по убегающим, затем REND
(RARE) MON_FO_FALLEN_OAK_GUARDIAN — Поваленный дуб-страж
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
далеко — бросок, близко — LOG_ROLL
2_5 FOREST_RING_5 (T5) — финал леса + боссы
MON_FO_ALPHA_DIREWOLF — Альфа лютоволков
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
HOWL → фокус → преследование
MON_FO_BROODMOTHER_SPIDER — Паучья матка
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
TRAP на дистанции, вблизи — REND
MON_FO_OLDROOT_ENT — Древокорень
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
далеко — THORN_RAIN, близко — SLAM
(RARE-mini) MON_FO_MOONWOLF — Лунный волк
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
HOWL → фокус → преследование
(RARE-mini) MON_FO_IRONHIDE_BOAR — Железношкурый секач
[DATA] Перечень/записи вынесены в DB_SPEC соответствующей сущности.
AI:
почти всегда CHARGE, не отпускает
ELITE-версии — стандарт
[CANON] ELITE-рецепт, routing, RNG и валидаторы: см. B19 — ELITE_MOD_PROTOCOL_GLITCH (19.0–19.6).
[DATA] Готовые MON_*_ELITE карточки и любые численные статы/табы элит — только в DB_SPEC::monsters (runtime pack). В B16 не дублировать.
@@END:B16@@
@@BEGIN:B17@@
## B17 — CONTENT: POI-PATTERNS (MVP) — CACHES / CHOKE / FIELD-SHELTER
Цель: описать переносимые паттерны POI как контент, не вводя новых валют/XP/прогресс-слоев и не добавляя недетерминизм. Все расчеты и RNG — на клиенте. Время — t_sec:int. Проценты/мульты — bp:int. Мастер выдаёт только нарратив/интент, не "результат броска".
17.0 CONTENT ENTITIES USED (DATA, DB_SPEC)
• POI_DEF: poi_id, region_id, tags[], tier_band, one_shot, time_cost_sec, loot_coffer_id, spawn_table_id, extra_flags.
• LOOT_COFFER_DEF / LOOT_POOL_DEF: алгоритм открытия кофера и выбор слотов — как в каноне COFFER/LOOT.
• SPAWN_TABLE_DEF: таблица кандидатов энкаунтера (группы врагов) с weight_int и ограничениями по tags. (Термин "ENCOUNTER" допустим как синоним.)
• QUEST_TEMPLATE_DEF: шаблон контракта для доски контрактов.
• ELITE_MOD_DEF: контентный мод-метка, которая маршрутизирует на derived MON_*_ELITE карточки (без рантайм-генерации).
17.1 POI_INSTANCE_STATE (CANON, MVP)
Нужно, чтобы некоторые POI могли быть одноразовыми (тайники) и/или иметь локальное состояние (например, "открыто"). Состояние обязано быть детерминированным и воспроизводимым из save+content_pack+seed.
[CANON] POI_INSTANCE_ID
• poi_instance_id:string — стабильный идентификатор инстанса POI в рамках одного run (session_id/run_id).
• poi_instance_id обязан быть детерминированно воспроизводим из: world_seed + run_id + region_id + route_node_id + poi_id. Запрещено генерировать UUID на лету.
• Рекомендуемая форма: poi_instance_id = "POI@" + HEX16(HASH_U64(world_seed, run_id, region_id, route_node_id, poi_id)).
• HEX16(x) — строка из 16 hex-символов (форматирование, не криптография).
[CANON] SAVE::poi_state
• save.world.poi_state[poi_instance_id] = { opened:bool, opened_at_t_sec:int }
• opened=false по умолчанию. Если opened=true, opened_at_t_sec >= 0.
• Повторное применение события открытия не должно менять состояние (идемпотентность через event_id).
[CANON] CHANGELOG / IDEMPOTENCY
• Открытие POI, которое меняет save (например, ставит opened=true), оформляется как событие CHANGELOG с event_id:string по канону EVENT_ID_AND_ORDERING.
• Повтор event_id должен быть SKIP без побочных эффектов (replay-proof).
17.2 POI_CACHE_* — одноразовые схроны/тайники (CANON, MVP)
Роль в петле: дать игроку точку выбора в экспедиции (потратить время) ради малой, но полезной добычи. Тайники не выдают валюту напрямую и не ломают экономику.
[DATA] POI_DEF: поля (в DB_SPEC)
• poi_id = "POI_*_CACHE_*"
• tags включает: poi:cache и тематические теги (world:forest / world:ruins / tone:scarcity и т.п.).
• one_shot=true (тайник одноразовый).
• loot_coffer_id:string (кофер лута).
• time_cost_sec:int (опционально; если 0 — вскрытие без цены времени).
[CANON] POI_CACHE_OPEN алгоритм
• Если save.world.poi_state[poi_instance_id].opened=true -> вернуть ExplainStep RULE_POI_ALREADY_OPENED и НЕ выдавать лут.
• Иначе: (1) если time_cost_sec>0 -> TIME_ADVANCE{time_cost_sec}; (2) выполнить LOOT_OPEN по loot_coffer_id; (3) применить INVENTORY_ADD по слотам; (4) поставить opened=true и opened_at_t_sec=t_sec.
• TIME_ADVANCE — единственный способ "платы временем" вне боя (см. канон TIME).
[CANON] RNG для тайника
• RngKey = (world_seed, rng_stream=RNG_LOOT, context="poi.cache.open", scope_id=poi_instance_id, draw_index=slot_i).
• draw_index=0..k_slots-1 (строго фиксированное число draw на слот).
[CANON] Ограничения тайников
• Запрещено класть прямую выдачу CU в тайники. Валюта живет в экономике/квестах/сервисах.
• Запрещено выдавать "готовую легендарку" из обычных тайников (см. канон про коферы/легендарное).
• one_shot=true обязателен; повторное вскрытие — только explain, без лута.
[CANON] Failure/Consequence
• Провал как таковой отсутствует: цена тайника — время и риск оказаться в худших условиях (ночь/холод/перевес) по общим правилам TIME_ADVANCE/Survival.
[CANON] Explain (минимум)
• RULE_POI_CACHE_OPEN meta{poi_id, poi_instance_id, loot_coffer_id, k_slots, time_cost_sec}.
• RULE_TIME_ADVANCE meta{delta_sec} (если применимо).
• RULE_LOOT_PICK meta{pool_id, draw_index, item_id, qty}.
• RULE_POI_ALREADY_OPENED meta{poi_id, poi_instance_id}.
17.3 POI_CHOKE_* / ENCOUNTER_VARIANT_CHOKE — узкие места и запрет побега (CANON, MVP)
"Узкое место" — контентный флаг, который использует уже существующую механику scene.escape_blocked. Нового алгоритма боя не добавляет.
[DATA] Источник escape_blocked
• escape_blocked может задаваться в poi_def (extra_flags: escape_blocked=true) и/или в spawn_table/variant (escape_blocked=true).
• Мастер не включает/выключает escape_blocked "по настроению". Истина — данные.
[CANON] Поведение в бою (ссылка на B07)
• Если scene.escape_blocked=true: ACT:RETREAT не может завершить бой. Побег возможен только через WORLD_MOVE (если доступно) или через исход энкаунтера.
• При попытке RETREAT при escape_blocked=true core обязан вернуть ExplainStep RULE_ESCAPE_BLOCKED.
[CANON] Баланс-правило CHOKE
• CHOKE-POI обязан компенсировать риск одним из способов (data-only): (a) более жирный coffer; (b) меньшая цена времени на проход; (c) выше шанс элиты внутри choke (но не глобально).
[CANON] Failure/Consequence
• Провал в choke проявляется как невозможность безопасно отступить: игрок платит ресурсами/HP/временем по базовым правилам боя/выживания.
17.4 POI_FIELD_SHELTER_* — полевой лагерь (CANON, MVP)
Полевой лагерь дает передышку только ценой времени и риска. Запрещена "бесплатная безопасная ночь" в экспедиции.
[DATA] POI_DEF: полевая стоянка
• poi_id = "POI_*_FIELD_SHELTER_*"
• tags включает: poi:shelter, tone:scarcity, опционально env:* (cold/dark/wet).
• one_shot=true (рекомендуемо для MVP; иначе потребуется счетчик использований -> V_NEXT).
• rest_options[]: каждая опция задаёт delta_sec:int и visit_chance_bp:int (0..10000).
• visit_spawn_table_id:string (таблица визитов/засад).
[CANON] FIELD_SHELTER_REST алгоритм (без фоновой симуляции)
• Игрок выбирает rest_option -> выполнить TIME_ADVANCE{delta_sec}. TIME_ADVANCE остается единственным способом протекания времени вне боя (см. канон TIME).
• После TIME_ADVANCE выполнить одну проверку визита: ChanceBp=visit_chance_bp. При success -> стартовать бой по visit_spawn_table_id.
[CANON] RNG для визита
• RngKey = (world_seed, rng_stream=RNG_SPAWN, context="poi.shelter.visit", scope_id=(poi_instance_id, rest_seq), draw_index=0).
• Для MVP при one_shot=true: rest_seq=0. Если разрешить multiple use -> нужен счетчик в save (V_NEXT).
[CANON] Failure/Consequence
• Неудача = визит/засада после отдыха. Это детерминированно (ChanceBp + keyed RNG) и полностью объяснимо в explain.
[CANON] Explain
• RULE_TIME_ADVANCE meta{delta_sec}.
• RULE_SHELTER_VISIT_ROLL meta{chance_bp, draw_0_9999, success}.
• RULE_SHELTER_VISIT_START meta{spawn_table_id}.
[V_NEXT] multiple-use shelters
• Если нужно разрешить N использований одного shelter-POI, требуется новое состояние save.world.poi_state[poi_instance_id].uses:int и валидатор. Это V_NEXT (новый state-счетчик).
17.5 EDGE CASES CHECKLIST (MVP)
• Повтор входа в тот же poi_instance_id: тайник не переоткрывается, shelter не повторяется (при one_shot).
• Побег/выход из боя: в CHOKE действует escape_blocked, в обычных POI — как обычно.
• Перегруз: лут из тайника может быть недоступен при перегрузе, если это правило уже есть (иначе: allow pickup, но movement penalties).
• Ночь/темнота/холод: вся цена времени проходит через TIME_ADVANCE и существующие шкалы.
17.9 COVERAGE_MAP (MVP) — дыры по петле
• EXPEDITION: мало точек выбора (время/риск/маршрут) помимо боя.
• RETURN: слабая связка "принес добычу -> город реагирует" кроме продажи.
• TOWER: риск есть, но мало вариативных POI по этажам без новой боевки.
• CITY: сервисы есть, но мало контентных причин ходить в Identify/Repair/Archive.
Закрытие MVP-паттернами: POI_CACHE (выбор и микро-награда), POI_CHOKE (наказание за плохой маршрут), POI_FIELD_SHELTER (управление временем), а также квесты описи/ремонта и elite mods для редкой опасности.
@@END:B17@@
@@BEGIN:B18@@
## B18 — QUEST_TEMPLATE_IDENTIFY_BATCH (MVP) — «Архивная опись»
[CONTENT] Коротко о смысле (в петле, без новой механики)
Архив — инфраструктура города, которая покупает устранение неопределённости, а не “знание предмета”. Игрок сдаёт UNIDENTIFIED образцы по контракту: разгружает инвентарь, снижает риск “сомнительного хлама”, получает гарантированную контрактную награду (CU по доске + утилитарный reward coffer). Идентификация остаётся отдельным сервисом: квест не раскрывает “что это”.
[CONTENT] Голос/тон для офферов (data-only оформление)
• Короткие строки, канцелярит без шуток.
• Угроза = “ответственность/инцидент/утилизация”, а не “монстры”.
• Слова-опоры: ведомость, акт, пломба, партия, санобработка, несовпадение, нулевая метка.
• Мастер (LLM) может менять формулировки только в рамках этого стиля; факты/теги/условия оффера — из данных.
[DATA] Контент-пак B18 (без “простыней” в каноне)
ARCHIVE_CHAPTER_DEF (темы описи как теги данных, без механики)
• chapter_id: string (например ARCH_CH_DUST / ARCH_CH_BATCH / ARCH_CH_MISMATCH / ARCH_CH_ZERO / ARCH_CH_GLITCH)
• chapter_tag: string (например "archive:chapter_dust")
• tier: int (1..5) (рекомендовано 1:1 с T1..T5)
• title_stub: string (короткий заголовок)
• hook_line: string (1 строка тона)
ARCHIVE_OFFER_TEXT_PACK (варианты карточек доски контрактов)
• chapter_id, tier
• variants[]: {title, body_1, body_2?}
[DATA NOTICE] Полные списки вариантов живут в контент-паках; в каноне держать ≤ 3–5 примеров.
Примеры (минимум, не канон механики):
• «Опись: Пыльный фонд» — “Стертые метки. Сдать образцы под пломбу.”
• «Опись: Партия без происхождения» — “Одинаковое. Разный след. Нужны образцы для сверки.”
• «Опись: Нулевая метка» — “Класса нет. В учёте — красная строка. Сдать без вскрытия.”
• «Опись: Несовпадение протокола» — “Форма обычная. Протокол молчит. Нужны образцы.”
• «Опись: Сбой протокола» — “Это симптом. Мы фиксируем симптом. Доставьте образцы.”
ARCHIVE_DOSSIER_DEF (лор-разблок, без боевых/экономических эффектов)
• dossier_id: string (например ARCHIVE_DOSSIER_T3_01)
• tier: int (1..5)
• text_short: string (1–2 строки)
• ui_key: string (ключ записи в журнале/архиве)

[CANON] 18.1 Правило MVP (и происхождение quest:archive_sample — coffer-only)
[CANON] DB_FILL_PATCH::TAG_REGISTRY (MVP)
• tag_id immutable; смысл тега не меняется без нового tag_id.
• Минимальные namespaces (используются в каноне): quest:*, item:*, trade:*, status:*, service:*, loot:*, archive:*, poi:*, world:*, env:*, tone:*, flavor:*, ration:*, legendary:*, threat:*, elite:*.
• Unknown tag_id / class_id forbidden: build-step и load-time fail-fast.
• Каждая подсистема имеет allowlist по tag_namespace (в [DATA]/DB_SPEC): QUESTS, SHOPS/EXCHANGE, CRAFT, LOOT, IDENTIFY, REPAIR, SALVAGE. Теги вне allowlist → reject (валидация), не UI.
• Фильтры используют tags_all/tags_any/tags_none (или экв.); списки сортируются asc при сериализации/хешах.
• Квест «Опись» НЕ идентифицирует предметы игроку.
• Он принимает только UNIDENTIFIED образцы с тегом quest:archive_sample и выдаёт награду по шаблону контракта.
• Сдаваемые предметы удаляются из инвентаря: INVENTORY_REM (см. 18.4.2).
Происхождение quest:archive_sample (строго: только из LOOT_OPEN результата)
• Тег quest:archive_sample не может:
• быть добавлен игроком/UI-действием,
• появиться “постфактум” после получения предмета,
• приходить из путей, которые не являются результатом LOOT_OPEN.
• quest:archive_sample назначается только при создании item_instance как часть результата LOOT_OPEN (data-driven: spawn_tags_add=["quest:archive_sample"] или эквивалент).
• Никаких отдельных RNG-вызовов “ради назначения тега” не вводится: тег — атрибут уже выбранного loot entry.
• Инвариант: item_instance с quest:archive_sample создаётся как UNIDENTIFIED.
Поведение при идентификации (чтобы квест не “съедал” опознанное)
• После SERVICE_IDENTIFY предмет перестаёт быть UNIDENTIFIED и не проходит фильтр сдачи filter_tags_all=["UNIDENTIFIED","quest:archive_sample"].
(Опционально: клиент может снимать quest:archive_sample при идентификации как data-санитарию; для логики квеста не требуется.)
[CANON] DB_FILL_PATCH::IDENTIFY_MODEL (MVP)
• UNIDENTIFIED — instance-level состояние (is_identified=false и/или instance_tag), не def-tag.
• MVP (минимум churn): SERVICE_IDENTIFY не меняет item_id; только is_identified=true и (опц.) снимает UNIDENTIFIED.
• V_NEXT (feature-gate): если понадобится “после идентификации другой item_id” — ItemDefinition.identified_item_id. До фиксации модели — запрещено для массового DB-fill.

@@BEGIN:B18.IDENTIFY_ALIGNMENT@@
[CANON] SPELL_IDENTIFY vs SERVICE_IDENTIFY vs ARCHIVE_QUEST (MVP)
- SERVICE_IDENTIFY is the only operation that mutates item instance identify state: is_identified=true and/or removes UNIDENTIFIED (see 18.1/18.2).
- SPELL_IDENTIFY produces an analysis report (UI/trace) but must NOT:
  - set is_identified=true,
  - remove UNIDENTIFIED,
  - remove quest:archive_sample,
  - change item_id.
- Therefore, running SPELL_IDENTIFY on an archive sample does not disqualify it from the archive quest filter_tags_all=['UNIDENTIFIED','quest:archive_sample'].
- Spell output gating by detail_level: what fields are revealed is [DATA] allowlist per item class/tag; unknown or restricted fields remain hidden.
- Anti-abuse: spell identify may not reveal exact sell_price/buy_price or other economy-critical hidden fields unless already public by design (data).
@@END:B18.IDENTIFY_ALIGNMENT@@

Data-policy (MVP)
• quest:archive_sample помечаются только те UNIDENTIFIED результаты LOOT_OPEN, которые не имеют канонического канала конвертации в CU через городские операции (см. 18.7).

[DATA] 18.2 Шаблон квеста (DB_SPEC) — углублённая спецификация
Сущность: QUEST (городской квест/контракт; офферы и награды — по канону QUEST_BOARD)
Идентификаторы / тиры
• quest_id = "QUEST_IDENTIFY_BATCH_Tx" где x=1..5
• tier_min = x; tier_max = x (жёстко по тиру)
• repeatable = true
Локация / выдача
• loc_id = LOC_CITY_ARCHIVE (или канонический loc_id Архива)
• giver_npc_id (опционально)
Kind (для формулы наград доски контрактов)
• kind = DELIVERY
Objective
• objective.steps[1] (один шаг, сдача в городе)
• step_kind = DELIVER
• qty_required:int
• filter_tags_all = ["UNIDENTIFIED", "quest:archive_sample"]
• (опционально, вариативность без изменения механики)
• filter_tags_all += ["archive:chapter_dust"] (или иной конкретный chapter_tag)
• только если соответствующие образцы реально появляются через LOOT_OPEN с тем же тегом (data-policy контент-пака)
Rewards (предметы — строго через coffer)
• rewards.reward_coffer_id:string — обязателен
• Рекомендованный нейминг: COF_ARCHIVE_OPIS_T1..T5 (или COF_ARCHIVE_OPIS_T3_*)
• Ограничение: CU внутри reward_coffer запрещены (валюта выдаётся только как reward_cu доски контрактов)
Extra (для генерации офферов)
• extra.board_weight:int (>=0)
• extra.offer_ttl_days:int (если не задан — дефолт доски)
• extra.cooldown_sec:int (если не задан — дефолт доски)
Примечание (важно)
• reward_cu и deposit_cu не хардкодятся в шаблоне: вычисляются на стороне Offer по канону доски контрактов.
• Offer — вычисляемый объект (save может кэшировать для UI, но истина = пересчёт):
• offer_id = HASH(world_seed, day_index, quest_board_id, slot_index)
• expires_at = day_indexDAY_SEC + ttl_daysDAY_SEC
• reward_cu (по формуле доски контрактов)
• deposit_cu = ceil_div(reward_cu * DEPOSIT_FRAC_BP, 10000)

[CANON] 18.3 RNG/офферы (доска контрактов)
• Eligible templates:
• tier_min <= access_tier <= tier_max
• repeatable → не в кулдауне по quest_state.cooldowns[quest_id]
• progress_flags (если используются) не блокируют шаблон
• extra.board_weight 0 (weight=0 → игнор)
• Stable order кандидатов: сортировать кандидатов канонически-стабильно (рекомендуемо quest_id asc).
• Сэмплирование офферов: weighted sampling without replacement по extra.board_weight:
• 1 pick = 1 draw
• offer_index = pick_index = 0..N_OFFERS-1
• RNG (stream = RNG_ECONOMY):
• keyed-RNG: (world_seed, RNG_ECONOMY, context="quest_board.offers", scope_id=(day_index, quest_board_id), draw_index=offer_index)
• offer_id (стабильный ID слота): slot_index = offer_index; offer_id = HASH(world_seed, day_index, quest_board_id, slot_index)
• Любые derived поля оффера (VarQuestMultPct и т.п.) обязаны быть keyed к offer_id (фиксированный context + draw_index), чтобы offer_id → {reward_cu, deposit_cu, expires_at, objectives} был стабилен.
• Инвариант: одинаковые (world_seed, day_index, quest_board_id) при тех же gating-входах (access_tier/cooldowns/progress_flags/content_pack) → те же офферы.

18.4 Завершение и награда (через coffer-паттерн)
18.4.1 Предусловия / валидации (fail-fast)
• Idempotency guard: если event_id уже в applied_event_ids → SKIP без побочных эффектов.
• quest_instance_id существует и quest_instance.state == ACTIVE.
• t_sec < quest_instance.expires_at (если expires_at используется); иначе сдача запрещена.
• В objective есть шаг DELIVER: qty_required:int>=1 и filter_tags_all[] непустой.
• rewards.reward_coffer_id задан и валиден.
• В инвентаре есть минимум qty_required единиц, удовлетворяющих filter_tags_all (см. 18.4.2).
При нарушении → SYS_CONFLICT (без мутаций save):
• MISSING_ENTITY / PRECONDITION_FAILED / INVALID_VALUE (reason_code по канону SYS_CONFLICT).
18.4.2 Детерминированный выбор и списание (INVENTORY_REM)
Примечание (канон): 18.4.2 описывает детерминированный выбор (removal_plan). Фактическая мутация инвентаря и логирование выполняются РОВНО ОДИН РАЗ событием INVENTORY_REM в 18.4.3; повтор события защищён идемпотентностью по event_id.
• eligible(item_instance) := содержит ВСЕ теги из filter_tags_all (all-of).
• qty_required — количество единиц (если стаки, учитывается qty, а не число стеков).
Алгоритм (канонически-стабильный, UI-независимый):
candidates[] = все item_instance, где eligible=true.
Stable order: sort candidates по item_instance_id asc.
qty_found = Σ candidates[i].qty (если qty нет → qty=1). Если qty_found < qty_required → SYS_CONFLICT PRECONDITION_FAILED и STOP.
Сформировать план списания (removal_plan) ровно на qty_required единиц в порядке candidates: remaining=qty_required; для c в candidates: consume=min(remaining, c.qty); добавить в removal_plan {item_instance_id=c.id, consume_qty=consume}; remaining-=consume; stop если remaining==0. Применение removal_plan выполняется в 18.4.3 событием INVENTORY_REM (см. примечание выше).
18.4.3 Порядок завершения и выдачи (строго)
После успешного 18.4.2:
INVENTORY_REM (применить removal_plan из 18.4.2; ровно qty_required).
CU: начислить reward_cu + refund(deposit_cu) по офферу/инстансу.
LOOT_OPEN(reward_coffer_id) → стандартный coffer/loot pipeline (см. 18.5 + канон COFFER/LOOT).
quest_instance.state = COMPLETED; прогресс шага DELIVER = qty_required.
Для repeatable: поставить cooldown (quest_state.cooldowns[quest_id]=t_sec+cooldown_sec) по канону доски.
18.4.4 Идемпотентность “награда один раз”
• Повтор того же event_id → SKIP (applied_event_ids/ledger), без повторной награды.
• Завершение инстанса при state!=ACTIVE → SYS_CONFLICT ALREADY_FINALIZED, без изменений.
18.4.5 Explain/Trace (минимум, детерминизм-first)
• RULE_QUEST_DELIVER meta{quest_id, qty} (qty=qty_required)
• RULE_QUEST_REWARD meta{quest_id, cu_delta} (cu_delta=reward_cu+deposit_refund)
• RULE_QUEST_REWARD_COF meta{quest_id, reward_coffer_id}
• Далее — стандартные RULE_LOOT_PICK … (по канону coffers), в порядке draw_index.

[CANON] 18.5 Детерминизм наградного кофера (Quest Reward Coffer)
Цель: LOOT_OPEN(reward_coffer_id) в рамках QUEST_COMPLETE должен быть детерминированным и идемпотентным по event_id (повтор обработки события завершения не выдаёт награду повторно).
18.5.1 Термины и входы
• quest_instance_id — стабильный id инстанса.
• event_id — id события завершения, являющийся ключом идемпотентности награды.
• k_slots — число слотов наградного кофера (для данного reward_coffer_id).
[ASSUMPTION] k_slots берётся из данных кофера/таблиц и фиксируется в момент завершения (чтобы не “поплыть” при смене данных).
18.5.2 RNG-контракт (строго)
• rng_stream = RNG_LOOT
• context = "quest.archive_reward.open"
• scope_id = quest_instance_id
• draw_index = slot_i (0..k_slots-1)
Запрещено: доп. RNG “внутри слота”, перероллы, зависимость от времени/FPS/порядка обхода коллекций.
18.5.3 Правило “1 draw → 1 результат”
Для каждого slot_i выполняется ровно один pick из slot_table_id[slot_i].
Если нужна вариативность qty — она кодируется разными строками таблицы (item_id/qty как часть entry), без дополнительных RNG.
18.5.4 Идемпотентность (ledger)
• Повтор event_id не должен повторно делать INVENTORY_ADD/изменять валюту.
• Детерминированный “повторный показ” результата допускается из сохранённого resolved-результата.
[DATA] RewardClaimLedger (минимум): event_id, quest_instance_id, context, k_slots, reward_lines_resolved[], applied=true.

[CANON] 18.6 Контент наград (COF_ARCHIVE_OPIS_T1..T5) — совместимо с 18.5 (1 draw на слот)
COF_ARCHIVE_OPIS_T1..T5 — reward_coffer_id для «Архивной описи». Они дают только утилитарные награды (поддержка вылазки/базового крафта) + опциональный лор-разблок (досье), без ускорения прогрессии.
18.6.1 Запреты состава (fail-fast валидатором)
Запрещено в COF_ARCHIVE_OPIS_* (в любых slot_table):
• Любая валюта/суррогаты денег.
• Любые предметы со стат-ростом/перманентной силой/XP/перк-токенами.
• Любые item_id, имеющие канонический путь конвертации в CU через SHOP_SELL/SHOP_EXCHANGE (см. 18.7.3–18.7.5).
18.6.2 Слоты по tier (структура слотов = структура slot_table_id[])
(Примеры table_id — рекомендованный нейминг, не механика; механика = “одна таблица на слот”.)
• T1: k_slots=2
• slot0: LT_ARCHIVE_CONSUMABLE_T1
• slot1: LT_ARCHIVE_MATERIAL_T1
• T2: k_slots=2
• slot0: LT_ARCHIVE_CONSUMABLE_T2
• slot1: LT_ARCHIVE_MATERIAL_T2
• (лор-досье допускается как редкая строка в одной из этих таблиц; см. 18.6.3)
• T3: k_slots=3
• slot0: LT_ARCHIVE_CONSUMABLE_T3
• slot1: LT_ARCHIVE_MATERIAL_T3
• slot2: LT_ARCHIVE_COMPONENT_T3
• T4: k_slots=3
• slot0: LT_ARCHIVE_CONSUMABLE_T4
• slot1: LT_ARCHIVE_MATERIAL_T4
• slot2: LT_ARCHIVE_COMPONENT_T4
• T5: k_slots=4
• slot0: LT_ARCHIVE_CONSUMABLE_T5
• slot1: LT_ARCHIVE_MATERIAL_T5
• slot2: LT_ARCHIVE_COMPONENT_T5
• slot3: LT_ARCHIVE_FLEX_T5 (Flex реализуется составом одной таблицы: смешанные строки из категорий с нужными weight_int; без отдельного “выбора категории” и без доп. RNG)
18.6.3 ARCHIVE_DOSSIER_* (лор-разблок, без статов)
• ARCHIVE_DOSSIER_* может выпадать как редкая строка в slot_table (рекомендуемо — в Material/Flex таблицах соответствующих tiers).
• Досье не должно быть источником экономической выгоды:
• item_id досье отсутствует в city_shops[*].inventory и не eligible для SHOP_EXCHANGE,
• досье не конвертируется в ресурсы/валюту при дубликатах (data-policy + валидатор).
[ASSUMPTION] Если нужен “чистый journal unlock” без инвентарного предмета — оформить как отдельный apply-эффект loot entry (в рамках существующей системы progress_flags/journal), но без изменения RNG-контракта (всё равно 1 pick на слот).
[DATA] 18.6.D1 Мини-структуры (без контент-простыней)
• COFFER_DEF: coffer_id, k_slots, slot_table_id[]
• LOOT_TABLE_DEF: table_id, rows[]
• LOOT_ROW_DEF: row_id, item_id, qty:int>=1, weight_int>=0, spawn_tags_add[] (опц.)

[CANON] 18.7 Анти-абуз (MVP, упрощённый)
Цель: квест «Опись» не печатает CU (через перепродажу образцов/лута) и не позволяет бесплатный спам контрактов. Инструменты: data-policy + валидаторы + уже канонические депозит/cooldown/MAX_ACTIVE_CONTRACTS + идемпотентность event_id.
18.7.1 Threat Model (MVP)
• A) Конвертация в CU через SHOP_SELL/SHOP_EXCHANGE.
• B) Спам take→abandon/expiry→take без цены.
• C) Дубли выдачи из-за re-entrancy/replay/краша.
18.7.2 Data-policy: quest:archive_sample (enforceable)
• Инварианты происхождения — см. 18.1.
• Enforceable критерии (MVP): любой item_id, который может появляться с quest:archive_sample:
• не встречается в city_shops[*].inventory[].item_id,
• не eligible для SHOP_EXCHANGE по exchange_rules.
18.7.3 Data-policy: COF_ARCHIVE_OPIS_* (низкая ликвидность)
• Для любого item_id, встречающегося в slot_table_id[] кофера COF_ARCHIVE_OPIS_:
• не встречается в city_shops[].inventory[].item_id,
• не eligible для SHOP_EXCHANGE.
• Для ARCHIVE_DOSSIER_ — те же ограничения + запрет “конвертации дубликата” в ресурсы/валюту.
18.7.4 Экономические тормоза спама (deposit/cooldown/max active)
Инварианты — по канону доски контрактов (см. 18.3–18.4 и B10):
• deposit_cu списывается при QUEST_TAKE; возвращается только при QUEST_COMPLETE; сгорает при fail/abandon/expiry.
• cooldown ставится при любом исходе; MAX_ACTIVE_CONTRACTS ограничивает параллельный спам.
18.7.5 Валидаторы (обязательные, fail-fast)
Build/Load-time (DB/content validation):
• V_ARCHIVE_SAMPLE_ENTRY:
• loot entry со spawn_tags_add содержит "quest:archive_sample" → item_id не TRADE_GOOD/CURRENCY (или эквиваленты),
• item_id отсутствует в city_shops[].inventory[],
• item_id не eligible для SHOP_EXCHANGE,
• item_instance создаётся как UNIDENTIFIED.
• V_ARCHIVE_OPIS_TABLES:
• для каждого table_id в COF_ARCHIVE_OPIS_: запреты по тегам/классам (CURRENCY/STAT_BOOST/XP/PERK_TOKEN/…),
• каждый item_id из этих таблиц отсутствует в city_shops[].inventory[] и не eligible для SHOP_EXCHANGE.
• V_NO_CU_IN_COFFERS:
• в COF_ARCHIVE_OPIS_ запрещены любые формы “денег”; CU выдаётся только через reward_cu доски контрактов.
Runtime (без новых механик):
• Идемпотентность: applied_event_ids/ledger (повтор event_id → SKIP/NOOP).
• Сдача: списание ровно qty_required по stable order (18.4.2).
• Награда: CU + LOOT_OPEN выполняются один раз на event_id (18.4.4–18.5).
18.7.6 Explain/Trace (минимум)
Использовать канонические rule_id (см. 18.8): RULE_QUEST_ACCEPT / RULE_QUEST_DELIVER / RULE_QUEST_REWARD / RULE_QUEST_REWARD_COF / RULE_LOOT_PICK.
Для SYS_CONFLICT: reason_code + expected/got (коротко), без “простыней”.

[CANON] 18.8 Explain (стыковка с EXPLAIN_PAYLOAD)
Цель: explain[] детерминированный, минимальный, replay-proof: одинаковый вход → одинаковый explain[] (порядок и meta).
18.8.1 Канонические rule_id квестов (минимум)
RULE_QUEST_ACCEPT meta{quest_id}
RULE_QUEST_DELIVER meta{quest_id, qty}
RULE_QUEST_REWARD meta{quest_id, cu_delta}
RULE_QUEST_REWARD_COF meta{quest_id, reward_coffer_id}
RULE_LOOT_PICK meta{pool_id, draw_index, item_id, qty} (по канону LOOT_OPEN/coffer)
18.8.2 Нормативный порядок explain[] (QUEST_COMPLETE успех)
RULE_QUEST_DELIVER
RULE_QUEST_REWARD
RULE_QUEST_REWARD_COF
RULE_LOOT_PICK* (строго по draw_index 0..K-1)
SYS_CONFLICT: без успешных шагов награды; источник истины = reason_code + expected/got.

[CANON] 18.9 QA (MVP)
18.9.1 Инварианты
A) Детерминизм офферов: одинаковые (world_seed, day_index, quest_board_id) при тех же gating-входах → те же офферы.
B) Сдача: списывается ровно qty_required единиц по stable order item_instance_id asc; UI порядок не влияет.
C) Награда/идемпотентность: на event_id — ровно одна выдача (CU + LOOT_OPEN); повтор event_id → SKIP/NOOP.
D) Fail/Abandon/Expiry: депозит сгорает; cooldown ставится; награды не выдаются.
E) SYS_CONFLICT: без мутаций save, без “успешных” шагов награды в explain.
18.9.2 Мини-матрица тестов (свернуто)
• SameKeySameOffers / StableCandidateOrder / WeightZeroIgnored.
• ExactQtyRemoval / StableRemovalOrder / PartialStackHandling.
• OrderIsFixed (DELIVER→CU→COF→PICK) / IdempotentByEventId / AlreadyFinalizedForbidden.
• DepositSink / CooldownAlwaysSet / NoRewardOnFailPaths.
• Negative: NotEnoughItems / EmptyFilterOrBadQty / MissingEntities / Expired


@@END:B18@@
@@BEGIN:B19@@
## B19 — ELITE_MOD_PROTOCOL_GLITCH (MVP) — "Сбой протокола"
Цель: увеличить вариативность и редкую угрозу через контентные ELITE-варианты без добавления новых боевых механик.
Лор: “Сбой протокола”. Механика: data-only маршрутизация на заранее подготовленные derived-карточки MON_*_ELITE + фиксированный ELITE-рецепт статов (bp/int + caps).

19.0 Canon-Alignment / Инварианты (MVP)
[CANON] Инварианты (обязательные)
• ELITE не вводит новые правила боя: никаких новых ActionType/фаз/типов урона/скрытых пост-роллов. Только изменение существующих статов/параметров через bp/int и caps/clamps.
• Fixed-point: все мультипликаторы/вероятности — bp/ChanceBp:int; округления только apply_bp_floor/apply_bp_ceil/ceil_div/floor_div (см. [CANON: FIXED-POINT]).
• RNG: только keyed RNG по канону RNG_MODEL_UNIFICATION; никаких “extra RNG” сверх draw_spec.
• ELITE возникает только как выбор строки спавна (data-only): запрещён “elite roll поверх спавна” без явного draw_spec/ключей RNG.
• Derived entities: MON_*_ELITE обязаны существовать как готовые сущности в финальном runtime content-pack (Variant A: prederived; Variant B: build-step генерация/нормализация). Рантайм-генерация запрещена.
• Anti-reroll: один и тот же spawn_instance_id обязан давать тот же pick (candidate_id, monster_id). UUID/случайные компоненты для scope_id запрещены.
• Anti-abuse: ELITE не является источником печати CU/валюты/денежных суррогатов. Любые “элитные надбавки” — только item-based через стандартный loot/coffer пайплайн и enforceable валидаторами.

19.1 Data model (DB_SPEC / content pack)
[DATA] ELITE_MOD_DEF (если используется маршрутизация в исходниках контента)
• elite_mod_id:string = "ELITE_MOD_PROTOCOL_GLITCH"
• mode:string = "ROUTE_TO_DERIVED"
• derived_suffix:string = "_ELITE"
• tags_add[]: включает "elite:protocol_glitch" (UI/контент-маркер; не влияет на симуляцию, кроме explain/UI)
• ui_label/ui_badge/ui_fx_tag — опциональные UI-поля

[DATA] MON_DEF / MONSTER_CARD (минимум для base↔derived)
• monster_id:string
• rank:string (для ELITE = "elite")
• base_monster_id:string (опционально; для derived)
[ASSUMPTION] Если base_monster_id отсутствует, base_id для MON_*_ELITE восстанавливается удалением суффикса "_ELITE".
• stats_base{STR,DEX,VIT,INT,SPD,LUCK}:int; hp_max:int; armor_pct:int; attacks[]; ai_profile_id:string?; tags[]
[CANON] MONSTER_CARD не задаёт барьер. Для противников базовая норма: BarrierMax=0 (см. B07). Любой барьер у NPC допускается только как явный эффект/особенность контента (allowlist), чтобы не ломать лор «барьер = магия/артефакт», и чтобы объяснение (explain) всегда могло указать источник барьера.

[DATA] SPAWN_TABLE_DEF (энкаунтер/группа кандидатов)
• spawn_table_id:string
• entries[]: { candidate_id:string, weight_int:int>=0, monster_id:string, tags_all[]?, tags_any[]?, tags_none[]?, extra_flags{}? }
• candidate_id обязателен и уникален в рамках spawn_table_id (используется как stable-order ключ).
[ASSUMPTION] Если исходные авторские данные не имеют candidate_id, build-step обязан присвоить его детерминированно и сохранить в финальном паке.
• elite_mod_id:string? допускается только в исходниках build-step и не допускается в runtime pack (см. 19.4 валидатор V_RUNTIME_ROUTING_NORMALIZED).

19.2 ELITE-рецепт (нормативно, фиксированный MVP)
[CANON] ELITE = derived MON_X_ELITE от base MON_X (без расширения механики)
Для базового MON_X допускается derived MON_X_ELITE со следующими преобразованиями:
• Rank: "elite".
• HPMax: ×16500bp, округление вверх:
 HPMax_final = apply_bp_ceil(HPMax_base, 16500).
• ArmorPct: +6, с капом 70:
 ArmorPct_final = clamp_int(ArmorPct_base + 6, 0, 70).
• Stats (int-дельты):
 STR +4, DEX +4, VIT +4, INT +2, SPD +2, LUCK +2.
• WeaponDamageBase (WDB) всех атак: ×12500bp, округление вниз:
 WDB_final = apply_bp_floor(WDB_base, 12500).
• Attacks/Action IDs: набор attacks и их идентификаторы не меняются (меняется только WDB).
• AI: допускается только смена параметров “агрессивнее/меньше отступает” в рамках уже существующего ai_profile_id; запрещено добавлять новые действия/способности.
[DATA] Конкретные базовые значения MON_X (статы/атаки/AI-профили) — контент.

19.3 Routing / Selection / RNG (spawn.pick)
[CANON] Где возникает ELITE (data-only)
• ELITE определяется только содержимым SPAWN_TABLE_DEF: ELITE-строки — это строки, где monster_id оканчивается на "_ELITE".
• Если исходники контента используют elite_mod_id="ELITE_MOD_PROTOCOL_GLITCH", то это build-step артефакт: на build-step entry нормализуется в monster_id = base_monster_id + "_ELITE"; elite_mod_id удаляется/игнорируется в runtime.

[CANON] Алгоритм выбора кандидата
• One pick по WEIGHTED_SAMPLING_CANON:
 eligible = entries где weight_int>0 и tags_* проходят (если применимо);
 stable order = сортировка eligible по candidate_id asc;
 roulette pick = один rand_int по total.
• Draw spec: 1 draw на 1 pick; draw_index=0.
• RngKey: (world_seed, rng_stream=RNG_SPAWN, context="spawn.pick", scope_id=spawn_instance_id, draw_index=0).

[CANON] spawn_instance_id / anti-reroll (обязательное)
• spawn_instance_id:string — стабильный идентификатор “попытки спавна” (scope_id для spawn.pick).
• spawn_instance_id обязан быть детерминированно воспроизводим из:
 world_seed + run_id + region_id + route_node_id + spawn_table_id + spawn_seq
• Рекомендуемая форма:
 spawn_instance_id = "SPAWN@" + HEX16(HASH_U64(world_seed, run_id, region_id, route_node_id, spawn_table_id, spawn_seq)).
• spawn_seq:int — счётчик попыток спавна в рамках route_node_id:
 увеличивается только при атомарной фиксации факта “энкаунтер стартовал” (через CHANGELOG/event_id),
 и не увеличивается при UI-предпросмотре/перерисовке/повторном запросе explain.
• Запрещено: UUID/случайные компоненты в spawn_instance_id.

[CANON] Локальное повышение встречаемости ELITE (риск↔награда, data-only)
• Допускается только через контент конкретных POI/узлов (например CHOKE из B17):
 повышать weight_int у ELITE-строк и/или добавлять ELITE-строки только внутри таких “опасных” POI/узлов.
• Запрещено (MVP): глобальные модификаторы “+X% ELITE в мире” и пост-ролл “elite chance” поверх spawn.pick.

19.4 Bonus loot ELITE (опционально, без новых механик)
[CANON] Если у MON_*_ELITE есть “бонус-лут”, он обязан быть реализован через стандартный coffer/loot пайплайн (см. 18.5) без новых RNG
• rng_stream=RNG_LOOT
• context="elite.bonus_loot.open"
• scope_id=spawn_instance_id
• draw_index=slot_i (0..k_slots-1)
• Идемпотентность: по event_id/RewardClaimLedger (паттерн как в 18.5). Повтор обработки не меняет инвентарь и возвращает ранее resolved результат.
• Запрещено: доп. RNG “внутри слота”, перероллы, зависимость от времени/FPS/порядка обхода неупорядоченных коллекций.

[CANON] Anti-abuse для бонус-лута (enforceable)
• Запрещено содержать CU/валюту/денежные суррогаты.
• (Если в проекте есть городские магазины/обмен) запрещено содержать item_id, которые:
 встречаются в city_shops[*].inventory[] или eligible для SHOP_EXCHANGE по exchange_rules (иначе канал CU-печати).
[ASSUMPTION] Если сущностей city_shops/exchange_rules ещё нет в MVP, минимум — запрет CU/валюты и предметов класса CURRENCY/TRADE_GOOD по тегам/классам.

19.5 Build/Load-time validation (fail-fast)
[CANON] Валидаторы (минимум)
• V_SPAWN_CANDIDATE_ID_UNIQUE: candidate_id уникален в рамках spawn_table_id.
• V_SPAWN_TABLE_NONEMPTY: после tags_* и weight_int>0 остаётся ≥1 eligible entry.
• V_ELITE_BASE_SUFFIX_RESERVED: ни один base monster_id не оканчивается на "_ELITE".
• V_ELITE_DERIVED_EXISTS: если где-либо встречается monster_id с суффиксом "_ELITE", такая карточка обязана существовать в финальном паке.
• V_ELITE_BASE_EXISTS: для каждого MON_X_ELITE существует base MON_X (по base_monster_id или de-suffix).
• V_ELITE_RECIPE_CONSISTENT: MON_X_ELITE строго соответствует рецепту 19.2 (равенства по hp/armor/stats/WDB и неизменность набора attack_id).
• V_NO_ELITE_POSTROLL: запрещено наличие отдельного “elite_chance”/пост-ролла поверх spawn.pick.
• V_RUNTIME_ROUTING_NORMALIZED: в runtime pack запрещено требовать elite_mod_id для выбора; runtime использует только monster_id (включая *_ELITE).
• V_NO_CU_IN_ELITE_LOOT: элитный bonus coffer/pool не содержит CU/валюту/денежные суррогаты.
• (Опционально) V_NO_SHOP_SELLABLE_IN_ELITE_LOOT / V_NO_EXCHANGE_ELIGIBLE_IN_ELITE_LOOT — если включены городские операции.
• (Опционально) V_STABLE_ORDER_REQUIRED: loot-таблицы бонус-лута имеют явный стабильный ключ строк (row_id/row_index).

19.6 Explain/Trace (минимум, replay-proof)
[CANON] Explain payload — по общему канону EXPLAIN_PAYLOAD (meta: только int/string/bool; ключи стабильны; сериализация лексикографическая)
• RULE_SPAWN_PICK meta{spawn_table_id, spawn_instance_id, candidate_id, monster_id}
• Если monster_id оканчивается на "_ELITE":
 RULE_ELITE_TAG meta{elite_mod_id:"ELITE_MOD_PROTOCOL_GLITCH", base_monster_id, elite_monster_id}
• Если открыт bonus coffer (см. 19.4 и 18.5):
 RULE_ELITE_BONUS_COF meta{spawn_instance_id, bonus_coffer_id, k_slots}
 Далее — стандартные RULE_LOOT_PICK … (по 18.5), в порядке draw_index.
[UI] UI обязан показывать явный маркер “ELITE / Сбой протокола”; UI не показывает веса/шансы и raw seed.
@@END:B19@@
@@BEGIN:B20@@
## B20 — POI_FO_HUNTER_CAMP_ABANDONED (MVP) — “Брошенный лагерь”
[CANON] Роль в петле (экспедиция)
• POI-узел выбора в лесной экспедиции: “снять пользу быстро” vs “копаться дольше”, где цена — только время (через TIME_ADVANCE) и риск визита/засады (через visit_chance_bp + spawn_table), без новых механик.
• Без фракций/репутаций/соц-счётчиков: последствия выражаются только через стандартные системы (время → среда/метаболизм; визит → обычный энкаунтер).
• Это “cache-like” точка: одноразовая, без прямой выдачи CU, без экономических суррогатов; ценность — предметная (еда/расходники/сырьё) и микро-нарратив.
[DATA] POI_DEF (DB_SPEC) — поля и инварианты
• poi_id:string = "POI_FO_HUNTER_CAMP_ABANDONED".
• tags:string включает: world:forest, poi:cache, threat:human, tone:scarcity.
• one_shot:bool = true.
• time_cost_sec:int = 0 (цена времени задаётся опцией; прямой фиксированной цены у POI нет).
• search_options:POI_SEARCH_OPTION (строго 2 для MVP):
– option_id:string (stable key; рекомендуется UPPER_SNAKE или короткие FAST/DEEP).
– ui_label:string (для UI; не влияет на симуляцию).
– delta_sec:int (>=0).
– loot_coffer_id:string (кофер лута для этой опции; data-only выбор “малый/большой” достигается разными coffer_id).
– visit_chance_bp:int (0..10000).
• visit_spawn_table_id:string = "SPAWN_TRESPASSERS" (таблица визитов/засад: мародёры/вернувшиеся охотники).
• extra_flags:map<string, scalar> (опционально; для базового B20 пусто; CHOKE/escape_blocked — только data-only в reskin’ах).
[CANON] POI_INSTANCE_ID / состояние (совместимость с POI_CACHE_*)
• poi_instance_id:string обязан быть детерминированно воспроизводим из: world_seed + run_id + region_id + route_node_id + poi_id.
• Рекомендуемая форма: poi_instance_id = "POI@" + HEX16(HASH_U64(world_seed, run_id, region_id, route_node_id, poi_id)).
• save.world.poi_state[poi_instance_id] = { opened:bool, opened_at_t_sec:int }.
• Повторное применение события с тем же event_id → SKIP/NOOP без побочных эффектов (идемпотентность).
[CANON] Алгоритм взаимодействия (строгий порядок)
• Preconditions / fail-fast:
– Если save.world.poi_state[poi_instance_id].opened=true → вернуть ExplainStep RULE_POI_ALREADY_OPENED и завершить (без TIME_ADVANCE, без LOOT_OPEN, без визита).
– Проверить, что option_id ∈ search_options и search_options длиной ровно 2 (MVP); иначе SYS_CONFLICT(PRECONDITION_FAILED / INVALID_VALUE).
• Выполнение (opened=false):
Игрок выбирает search_option.
TIME_ADVANCE{delta_sec=option.delta_sec} (если delta_sec>0; если 0 — шаг может быть опущен, но порядок explain сохраняется через отсутствие RULE_TIME_ADVANCE).
Выполнить LOOT_OPEN по option.loot_coffer_id (коферная механика; выдача идёт через стандартные RULE_LOOT_PICK по слотам).
Применить INVENTORY_ADD по результатам лута (как в coffer-паттерне).
Зафиксировать POI как вскрытый: save.world.poi_state[poi_instance_id].opened=true; opened_at_t_sec=t_sec.
Выполнить одну проверку визита: ChanceBp=option.visit_chance_bp. При success → стартовать энкаунтер по visit_spawn_table_id.
• Важно:
– Визит/засада НЕ является отдельной “второй попыткой лута”: никаких дополнительных LOOT_OPEN/пост-роллов.
– one_shot=true: после opened=true повторных опций/попыток нет (anti-reroll через state + event_id).
[CANON] RNG-контракт
• LOOT_OPEN (кофер опции):
– rng_stream=RNG_LOOT.
– context="poi.cache.open" (единый контекст для cache-like вскрытий).
– scope_id=poi_instance_id.
– draw_index=slot_i (0..k_slots-1), строго фиксированный порядок слотов.
– Запрещено: дополнительные draw “внутри слота” сверх draw_spec кофера.
• VISIT_ROLL (проверка визита после вскрытия):
– rng_stream=RNG_SPAWN.
– context="poi.cache.visit".
– scope_id=(poi_instance_id, option_id).
– draw_index=0 (ровно 1 draw на 1 визит-ролл).
– Success критерий: draw_0_9999 < chance_bp (ChanceBp=visit_chance_bp).
• SPAWN_START (если визит success):
– Энкаунтер использует spawn.pick по WEIGHTED_SAMPLING_CANON (stable order по candidate_id asc; 1 draw).
– RngKey для pick: (world_seed, rng_stream=RNG_SPAWN, context="spawn.pick", scope_id=spawn_instance_id, draw_index=0).
– spawn_instance_id вычисляется по канону spawn_instance_id/anti-reroll:
* scope inputs: world_seed + run_id + region_id + route_node_id + spawn_table_id + spawn_seq.
* spawn_seq:int увеличивается только при атомарной фиксации факта “энкаунтер стартовал” (через CHANGELOG/event_id), и не увеличивается при UI-предпросмотре/перерисовке/повторном запросе explain.
[CANON] Explain/Trace (минимум, фиксированный порядок)
• Если already opened:
– RULE_POI_ALREADY_OPENED meta{poi_id, poi_instance_id}.
• Если opened=false (нормальный путь):
RULE_POI_CAMP_SEARCH meta{poi_id, poi_instance_id, option_id, delta_sec, loot_coffer_id, visit_chance_bp, visit_spawn_table_id}.
RULE_TIME_ADVANCE meta{delta_sec} (только если delta_sec>0).
RULE_LOOT_PICK* meta{pool_id, draw_index, item_id, qty} (строго по draw_index 0..k_slots-1).
RULE_CAMP_VISIT_ROLL meta{chance_bp, draw_0_9999, success}.
(если success) RULE_CAMP_VISIT_START meta{spawn_table_id, spawn_instance_id}.
• Примечание по UI: UI может показать “риск/время” и “была засада/не было”, но не обязан раскрывать chance_bp и не должен показывать raw seed/веса.
[CANON] Валидации (build/load-time и runtime)
• Build/load-time (контент):
– poi_id уникален; tags содержат poi:cache.
– one_shot=true обязателен для MVP.
– search_options длиной ровно 2; option_id уникальны; delta_sec:int>=0; visit_chance_bp:int∈[0..10000].
– loot_coffer_id и visit_spawn_table_id должны существовать и проходить базовые валидаторы кофера/спавна.
– Запрещено: прямая выдача CU через coffer’ы этого POI (применим валидатор класса V_NO_CU_IN_COFFERS / эквивалентный).
• Runtime (сейв/события):
– poi_instance_id детерминирован и стабилен; UUID запрещены.
– opened=true → никакие side effects не выполняются (ни TIME_ADVANCE, ни LOOT_OPEN, ни VISIT_ROLL).
– Идемпотентность: повтор event_id → SKIP целиком.
[CANON] Edge cases (MVP)
• delta_sec=0: TIME_ADVANCE пропускается; остальной порядок сохраняется.
• visit_chance_bp=0 или 10000: правило успеха остаётся тем же (draw < chance); результат детерминирован; дополнительных ветвлений/extra RNG не вводить.
• Double click / replay / crash:
– При повторном применении того же event_id — SKIP.
– При повторном входе в тот же poi_instance_id после фиксации opened=true — только RULE_POI_ALREADY_OPENED.
• Перегруз/инвентарь:
– Если каноническое правило “лут недоступен при перегрузе” уже существует — применить его; иначе [ASSUMPTION] разрешить получение лута, а штрафы/ограничения проявятся через правила перемещения/веса (без новых механик в B20).
• CHOKE/escape_blocked:
– В базовом B20 не используется; если включено в reskin’е — только data-only через extra_flags/spawn_table, без мастер-решений “по настроению”.
[DATA] Варианты (reskins, data-only; без новых механик)
• POI_FO_LOGGERS_CAMP_ABANDONED (лесорубы):
– tags: threat:human, tone:scarcity; смещение лута в scrap/материалы; меньший food.
– visit_spawn_table_id может остаться тем же или быть “SPAWN_LOGGERS_TRESPASSERS” (data-only).
• POI_FO_SCOUT_POST_RUINED (развед-пост):
– смещение лута в стрелы/контейнеры/расходники; повысить visit_chance_bp на “тщательной” опции (баланс — [DATA]).
• POI_FO_SMUGGLER_HIDEOUT_EMPTY (контрабандисты):
– смещение лута в relic-направление (через coffer/pools).
– допускается CHOKE: extra_flags.escape_blocked=true (и/или spawn_table entry/variant), строго по канону CHOKE (scene.escape_blocked data-only).
[CANON] QA (MVP) — мини-матрица тестов
• SameSaveSameResult: одинаковые (save+content+world_seed) → одинаковые LOOT_PICK и VISIT_ROLL результаты для данного poi_instance_id/option_id.
• OneShotNoLootAfterOpen: после opened=true повторный интеракт → только RULE_POI_ALREADY_OPENED, без лута/визита/времени.
• OptionValidation: неизвестный option_id → SYS_CONFLICT(INVALID_VALUE), без мутаций save.
• DeltaSecApplied: delta_sec>0 → присутствует RULE_TIME_ADVANCE и t_sec увеличен (в пределах одного события).
• DeltaSecZero: delta_sec=0 → RULE_TIME_ADVANCE отсутствует, остальное работает.
• LootOrderStable: RULE_LOOT_PICK идёт строго по draw_index 0..k-1, без пропусков/перестановок.
• VisitRollAlwaysOnce: при opened=false выполняется ровно один VISIT_ROLL (draw_index=0) и больше никаких RNG_SPAWN draw до spawn.pick.
• VisitRollKeyCorrect: RngKey VISIT_ROLL использует (RNG_SPAWN, "poi.cache.visit", scope_id=(poi_instance_id, option_id), draw_index=0).
• SpawnStartOnlyOnSuccess: RULE_CAMP_VISIT_START появляется только при success=true.
• SpawnPickKeyCorrect: spawn.pick использует (RNG_SPAWN, "spawn.pick", scope_id=spawn_instance_id, draw_index=0).
• SpawnSeqConsumption: spawn_seq увеличивается только при факте старта энкаунтера; UI-перерисовка/повтор explain не меняет spawn_seq.
• NoCurrencyInLoot: коферы опций не содержат прямой CU (валидатор контента).
• IdempotentByEventId: повтор того же event_id → SKIP целиком, без повторного лута/визита.
• AlreadyOpenedIsNoSideEffects: already opened → нет TIME_ADVANCE, нет LOOT_OPEN, нет VISIT_ROLL.
• ReskinDataOnly: изменение reskin’а достигается только POI_DEF/coffer/spawn_table; никаких новых правил/фаз.
[CANON] SELF-CHECK (MVP)
• NoNewMechanics: PASS — только TIME_ADVANCE + coffer LOOT_OPEN/LOOT_PICK + визит через ChanceBp + стандартный spawn.pick/энкаунтер.
• RNGKeyedOnly: PASS — LOOT: ("poi.cache.open", scope_id=poi_instance_id); VISIT: ("poi.cache.visit", scope_id=(poi_instance_id, option_id)); SPAWN: ("spawn.pick", scope_id=spawn_instance_id).
• IdempotentByEventId: PASS — guard: повтор event_id → SKIP; guard state: opened=true → RULE_POI_ALREADY_OPENED без side effects.
• ExplainOrderStable: PASS — RULE_POI_CAMP_SEARCH → (RULE_TIME_ADVANCE?) → RULE_LOOT_PICK* → RULE_CAMP_VISIT_ROLL → (RULE_CAMP_VISIT_START?).

@@END:B20@@
@@BEGIN:B21@@
## B21 — RECIPE_PACK_FIELD_RATIONS (MVP) — "Полевые пайки"
Цель: дать простой кулинарный пак для экспедиций (scarcity-first). Пайки закрывают “бытовую математику” выживания (HUNGER/THIRST → косвенная стабилизация EffectiveMaxHP) без новых механик. Используется канон COOKING: рецепт = 3 компонента, T1=30s, T2=60s, T3=120s (time_sec:int). Без RNG успеха, без новых статусов, без лечения выше EffectiveMaxHP.
[CANON] Роль в петле (expedition / scarcity)
• Пайки — переносимая, предсказуемая “страховка” на длинные TIME_ADVANCE: уменьшают HUNGER/THIRST и тем самым помогают держать EffectiveMaxHP ближе к “норме” (за счёт снятия дебаффов голода/жажды), но не дают боевой силы и не ускоряют прогресс.
• Использование:
– Вне боя: COOK (крафт) + USE_ITEM (съесть/выпить готовое).
– В бою: только USE_ITEM готового блюда (готовка в бою не предполагается).
• Экономика/прогресс: пайки не создают новых “постоянных ресурсов” (мана/энергия), не вводят новые прогресс-оси и не дают перманентных усилений.
[DATA] Сущности (content-pack / DB_SPEC::cooking_)
• Новые item_id блюд (пример нейминга, не список-истина):
– T1: DISH_T1_FIELD_RATION_SALTY, DISH_T1_FIELD_RATION_SWEET
– T2: DISH_T2_FIELD_RATION_HEARTY, DISH_T2_FIELD_RATION_WARM
– T3: DISH_T3_FIELD_RATION_LONGHAUL
• Для каждого DISH_ (минимальный контракт полей еды по канону):
– HungerDownPct:int (п.п. шкалы HUNGER)
– ThirstDownPct:int (п.п. шкалы THIRST)
– HPDelta:int (для пайков — см. [CANON] ниже)
– FoodPoisonChancePct:int (для пайков — см. [CANON] ниже)
– tags[]: включая dish:field_ration и flavor:* (см. [DATA] варианты)
– weight_g_per_unit:int (>=0), stack_count:int (стандарт ITEMS)
• Новые recipe_id: RECIPE_FIELD_RATION_* (каждый рецепт фиксирован, без “любой из группы”):
– recipe_id:string (stable key)
– time_sec:int ∈ {30,60,120} (строго по тиру)
– components[3]: ровно 3 компонента (каждый: item_id:string, qty:int>=1)
– station_req_tags[] (если модель станций поддерживает): heat_source + cookware (котелок/сковорода)
– produce: item_id блюда (DISH_*), qty:int>=1
– output_coffer_id: coffer_id (опционально в authoring; если отсутствует — build-step выводит детерминированный coffer из produce, runtime использует только coffer)
[CANON] Ограничения пайков (нормативно)
• Детерминизм крафта: одинаковые ингредиенты + одинаковый save → идентичный результат (нет RNG).
• Запрет RNG: у рецептов пайков отсутствуют success_chance / fail_chance и любые пост-роллы.
• Пайки — “еда, не медицина”:
– HPDelta для всех DISH_FIELD_RATION должен быть 0.
– Пояснение: “поддержка EffectiveMaxHP” достигается косвенно — через уменьшение HUNGER/THIRST (и снятие/ослабление дебаффов, которые режут EffectiveMaxHP), а не прямым лечением HP.
• Отсутствие статусов:
– FoodPoisonChancePct для всех пайков должен быть 0 (пайки не являются источником FOOD_POISONING).
– Пайки не применяют status_id и не вводят новые статусы/бафы.
• Время: time_sec:int строго; никаких диапазонов “30–45 сек”.
• “Тёплый” вариант: допускается только как тег/UX-метка (см. [DATA]) и/или взаимодействие с уже существующими env-правилами. Запрещено вводить новые статусные эффекты “warmth”.
[CANON] Крафт пайков (протокол применения, детерминизм-first)
• Событие (минимум, MVP): CRAFT_START {recipe_id, station_id, qty}.
• Preconditions / fail-fast (без мутаций save при нарушении):
– qty:int>=1.
– recipe_id существует и относится к RECIPE_FIELD_RATION_*.
– recipe.time_sec ∈ {30,60,120}.
– recipe.components длиной ровно 3.
– station_id валиден и удовлетворяет требованиям готовки (heat_source + cookware).
– В инвентаре есть достаточно компонентов для qty-кратного крафта (см. списание).
– Если симуляция “в бою” активна → SYS_CONFLICT(PRECONDITION_FAILED): готовка запрещена, разрешён только USE_ITEM готового блюда.
• Выполнение (строгий порядок внутри применения события):
Валидации (см. выше).
TIME_ADVANCE{delta_sec = recipe.time_sec * qty} (всё протекание времени — только через TIME_ADVANCE).
Детерминированное списание компонентов из инвентаря (qty-кратно, порядок UI-независим):
– Для каждого требуемого (component_item_id, component_qty_per_one): требуется total_qty = component_qty_per_one * qty.
– candidates[] = все item_instance с item_id == component_item_id.
– Stable order: sort candidates по item_instance_id asc.
– Списать ровно total_qty в порядке candidates (как в каноне INVENTORY_REM): partial consume из стека разрешён; пустые стеки удаляются.
Выдача результата (через coffer): выполнить LOOT_OPEN по recipe.output_coffer_id (если в authoring задан produce, build-step может вывести output_coffer_id детерминированно). Для batch qty:int>=1 допускается повторить LOOT_OPEN qty раз с scope_id=(event_id, craft_seq), затем применить INVENTORY_ADD по результатам.
Запрещено: бонус-выход, побочные “обрезки”, автоконверсия, пост-роллы.
[CANON] Build/Load-time validation (fail-fast)
• V_FIELD_RATION_RECIPE_3SLOTS: у каждого RECIPE_FIELD_RATION_* ровно 3 компонента.
• V_FIELD_RATION_TIME_STRICT: time_sec:int и time_sec ∈ {30,60,120}.
• V_NO_COOK_RNG: запрещены поля success_chance / fail_chance / crit_* и любые RNG-параметры в рецепте пайка.
• V_FIELD_RATION_NO_HPDELTA: для всех DISH_FIELD_RATION поле HPDelta == 0.
• V_FIELD_RATION_NO_POISON: FoodPoisonChancePct == 0.
• V_NO_NEW_STATUS: блюдо не содержит ссылок на status_id и не заявляет применение статусов.
• V_TAGS_ONLY_FOR_ENV: env:* теги допустимы только как метки; наличие env:* не должно требовать новых правил/статусов.
• V_CONTENT_IDS: уникальность item_id/recipe_id; все item_id в components[] и produce.item_id существуют в финальном паке; qty:int>=1.
[CANON] Explain/Trace (минимум, replay-proof; порядок фиксированный)
• RULE_CRAFT_START meta{recipe_id, station_id, qty}.
• RULE_TIME_ADVANCE meta{delta_sec}.
• RULE_CRAFT_CONSUME meta{item_id, qty} — по одному шагу на каждый component_item_id (qty = total_qty на весь крафт).
• RULE_CRAFT_PRODUCE meta{item_id, qty} (qty = produce.qty * qty).
• При отказе по предусловиям: SYS_CONFLICT с expected/got (по канону), без side effects.
[DATA] Варианты (минимум ассетов, максимум вариативности; без новых механик)
• Солёный паёк (T1): tags += [flavor:savory, ration:salty]; смещение эффекта в сторону THIRST (баланс — [DATA]).
• Сладкий паёк (T1): tags += [flavor:sweet, ration:sweet]; смещение эффекта в сторону HUNGER (баланс — [DATA]).
• Сытный паёк (T2): tags += [ration:hearty]; “универсальный” (баланс — [DATA]), без HPDelta.
• Тёплый паёк (T2): tags += [ration:warm] и (опционально) env:cold как UI/env-метка; если env-правил нет — эффект только нарратив/UX (без статусов).
• Дальний паёк (T3): tags += [ration:longhaul]; дороже по ингредиентам, рассчитан на длинные TIME_ADVANCE (баланс — [DATA]); без HPDelta/статусов.
[CANON] QA (MVP) — мини-матрица тестов
• SameIngredientsSameResult: при одинаковых входах (save+content) крафт даёт одинаковый результат (нет RNG).
• StrictTimeSec: time_sec строго 30/60/120 (и только int); неверное значение → fail-fast.
• ExactConsumption: списывается ровно qty-кратный набор компонентов, детерминированно по item_instance_id asc.
• NoHealAboveEffectiveMaxHP: HPDelta у пайков = 0; проверки “вылечить выше EffectiveMaxHP” не возникают.
• NoStatusNoPoison: FoodPoisonChancePct=0; нет статусов/применения status_id.
• StationPreconditions: отсутствие heat_source/cookware (или невалидный station_id) → SYS_CONFLICT(PRECONDITION_FAILED), без TIME_ADVANCE и без списаний.
• CombatDenied: попытка готовки в бою → SYS_CONFLICT(PRECONDITION_FAILED), без side effects.
• InvalidDataFailFast: рецепт не 3 слота / несуществующий item_id / qty<1 → fail-fast, без мутаций save.
@@END:B21@@
@@BEGIN:B22@@
## B22 — LUCK (MVP) — «Удача: экономика глубины + мягкий контроль риска»
@@BEGIN:B22.LUCK@@

@@BEGIN:B22.LUCK.CANON.01@@
[CANON] 22.1 Статус-кво (аудит)
- В текущем каноне LUCK участвует:
 - как тайбрейк инициативы: DEX desc → LUCK desc → entity_id asc.
 - как часть ELITE-рецепта (Stats: … LUCK +2).
 - как поле stats_base{… LUCK}:int в сущностях.
- Иных “потребителей” LUCK (loot/survival/combat procs) в каноне нет → этот блок вводит их, не ломая детерминизм.

@@END:B22.LUCK.CANON.01@@
@@BEGIN:B22.LUCK.CANON.02@@
[CANON] 22.2 Роль LUCK (инварианты)
- LUCK = стат “в глубину”:
 - основной вклад: повышает EV лута через bonus ingredient slots в COFFER (в т.ч. легендарные ингридиенты/ядра там, где это разрешено данными).
 - дополнительный вклад (мягко): снижает частоту негативных survival-роллов и слегка усиливает полезные proc-роллы.
- Запрещено:
 - вводить reroll/перерисовку исходов.
 - добавлять RNG “внутри базового слота” кофера сверх его draw_spec.
 - превращать LUCK в новую боевую механику (криты/новые фазы/новые типы урона).

@@END:B22.LUCK.CANON.02@@
@@BEGIN:B22.LUCK.CANON.03@@
[CANON] 22.3 LUCK_BONUS_ING_SLOTS — бонусные слоты ингредиентов в COFFER (основной эффект)
Назначение
- Для любого LOOT_OPEN (rng_stream=RNG_LOOT) LUCK может добавить условные “Bonus Ingredient Slot” (дополнительные попытки/пики) ПОСЛЕ базовых слотов кофера.
- Базовые слоты кофера (k_slots или K picks) не меняются и считаются как раньше.

Определения
- 100% = 10000 bp; 10% = 1000 bp; 0.1% = 10 bp.
- Bonus Ingredient Slot = (trigger draw) + (условно) (bonus pick draw) из отдельного пула ингредиентов.
- actor_luck = actor.stats.LUCK на момент выполнения LOOT_OPEN.
- luck_nonneg = max(actor_luck, 0).

Механика слотов (ровно как задано, без “тумблеров”)
1) Количество потенциальных бонус-слотов:
- n_slots_raw = ceil_div(luck_nonneg, 100)
- n_slots = clamp_int(n_slots_raw, 0, LUCK_BONUS_SLOTS_MAX) // perf guard из [DATA]

2) Для i-го слота (i = 0..n_slots-1):
- band_luck = clamp_int(luck_nonneg - i*100, 0, 100)
- slot_chance_bp = clamp_int(band_luck * 10, 0, 1000) // 0.1%/pt, cap 10%/slot

Смысл (примерная интерпретация, без “итогов бросков”)
- LUCK=100 → 1 слот с шансом 10%.
- LUCK=100..200 → 2 слота: slot0=10%, slot1 растёт 0.1%/pt сверх 100 до 10%.
- Каждые 100 LUCK добавляют ещё один потенциальный слот; cap 10% на слот соблюдён.

RNG-contract / draw_spec (строго; без скрытых draw)
Пусть базовый LOOT_OPEN имеет базовый диапазон draw_index:
- Slot-table coffer: базовые пики draw_index = 0..k_slots-1.
- K-picks coffer: базовые пики draw_index = 0..K-1.
Определим:
- BASE_END = k_slots (для slot-table) или BASE_END = K (для K-picks).

Для каждого i = 0..n_slots-1 выполняется:
A) Trigger draw (ровно 1 draw на слот, всегда):
- rng_stream = RNG_LOOT
- context = <тот же context, что у данного LOOT_OPEN>
- scope_id = <тот же scope_id, что у данного LOOT_OPEN>
- draw_index = BASE_END + i*2
- success критерий: draw_0_9999 < slot_chance_bp

B) Bonus pick (только если success=true):
- rng_stream = RNG_LOOT
- context = <тот же context, что у данного LOOT_OPEN>
- scope_id = <тот же scope_id, что у данного LOOT_OPEN>
- draw_index = BASE_END + i*2 + 1
- pool_id = COFFER_DEF.luck_bonus_ing_pool_id (см. [DATA])
@@END:B22.LUCK.CANON.03@@
@@BEGIN:B22.LUCK.CANON.04@@
[CANON] DB_FILL_PATCH::LUCK_BONUS_POOL_CONTRACT (MVP)
• luck_bonus_* pools допускают только item_class ∈ {MATERIAL, INGREDIENT, CONSUMABLE_UTILITY, TRADE_GOOD}.
• Запрещены equip/weapon/armor классы в luck_bonus pools (build-step validator).
• No reroll by reload: scope_id включает стабильный instance_id (quest_instance_id/poi_instance_id/coffer_instance_id); draw_index фиксирован; повтор LOOT_OPEN по одному instance_id не меняет исход.

- pick = стандартный WEIGHTED_SAMPLING_CANON (stable order; deterministic; no-float)

Инварианты
- Никаких reroll: 1 trigger draw на слот, и максимум 1 bonus pick на слот.
- Успех/неуспех trigger НЕ влияет на индексацию следующих trigger (i*2), поэтому трасса воспроизводима.
- Запрет “доп. RNG внутри базового слота” соблюдён: LUCK-дроу идут только ПОСЛЕ базовых слотов.

Explain/Trace (минимум; stable keys)
- RULE_LUCK_BONUS_ING_TRY meta{
 context, scope_id, draw_index,
 i_slot, luck, band_luck, slot_chance_bp
 }
- RULE_LUCK_BONUS_ING_RESULT meta{
 context, scope_id, draw_index,
 i_slot, success
 }
- При success=true дополнительно:
 - RULE_LOOT_PICK meta{pool_id, draw_index, item_id, qty}
 - (опц.) RULE_LOOT_PICK_SOURCE meta{source="luck_bonus_ing_slot", i_slot}

Fail-fast
- Если LUCK-механика включена для кофера, но luck_bonus_ing_pool_id отсутствует или Σweights==0 → SYS_CONFLICT(PRECONDITION_FAILED) (content bug).

@@END:B22.LUCK.CANON.04@@
@@BEGIN:B22.LUCK.CANON.05@@
[CANON] 22.4 “Легендарный двигатель” (коферы с legendary ингредиентами)
- Инвариант: обычные коферы не выдают готовую легендарную экипировку; допускаются только legendary:ingredient / legendary:core (для LEGENDARY_INFUSE).
- Legendary-эффект реализуется ДАННЫМИ:
 - если COFFER_DEF.luck_bonus_ing_pool_id указывает на “leg”-пул, bonus pick может дать legendary:ingredient/core.
 - если пул “nonleg”, bonus pick никогда не выдаёт legendary:ingredient/core.

@@END:B22.LUCK.CANON.05@@
@@BEGIN:B22.LUCK.CANON.06@@
[CANON] 22.5 LUCK — мягкое влияние “в моменте” (survival + procs, без новых механик)
Общий принцип
- LUCK в этих проверках НЕ добавляет новые draw, а только модифицирует порог ChanceBp перед стандартной проверкой draw < chance_bp.
- Чтобы LUCK не стал “бог-статом”, применяется отдельный мягкий cap по используемому luck:
 - luck_misc = clamp_int(max(actor_luck,0), 0, LUCK_MISC_CAP_STAT) // [DATA], обычно 100.

22.5.1 Survival: FOOD_POISONING (негативный ролл)
- base_chance_bp = clamp_int(FoodPoisonChancePct * 100, 0, 10000).
- chance_bp = clamp_int(base_chance_bp - luck_misc * LUCK_POISON_STEP_BP_PER_POINT, 0, 10000).
- RNG-contract (если ранее не был формализован):
 - rng_stream = RNG_INJURY
 - context = "survival.food_poison"
 - scope_id = (scene_id, actor_id, item_instance_id, use_seq)
 - draw_index = 0
- Explain:
 - RULE_LUCK_CHANCE_MOD meta{kind="food_poison", base_chance_bp, chance_bp, luck=luck_misc}
 - RULE_SURVIVAL_ROLL meta{kind="food_poison", draw_index, success}

22.5.2 Survival: POI визиты/засады после отдыха/вскрытия (негативный ролл visit_chance_bp)
- Для любых проверок, где ChanceBp = visit_chance_bp и RNG уже каноничен (например poi.shelter.visit / poi.cache.visit):
 - chance_bp = clamp_int(visit_chance_bp - luck_misc * LUCK_VISIT_STEP_BP_PER_POINT, 0, 10000).
- RNG ключи/streams/contexts/scope_id/draw_index НЕ меняются (сохраняется existing contract).
- Explain:
 - RULE_LUCK_CHANCE_MOD meta{kind="poi_visit", base_chance_bp=visit_chance_bp, chance_bp, luck=luck_misc}

22.5.3 Combat proc: SHIELD_PROC (полезный proc)
- Для ShieldProcMeleeChanceBp / ShieldProcRangedChanceBp:
 - chance_bp = clamp_int(base_chance_bp + luck_misc * LUCK_SHIELD_STEP_BP_PER_POINT, 0, 10000).
- RNG-contract сохраняется как в SHIELD_PROC_CANON (rng_stream/context/scope_id/draw_index не меняются).
- Explain:
 - RULE_LUCK_CHANCE_MOD meta{kind="shield_proc", base_chance_bp, chance_bp, luck=luck_misc}

22.5.4 Loot-side proc: ARROW_RECOVER (полезный proc)
- Для RecoverChanceBp:
 - chance_bp = clamp_int(base_chance_bp + luck_misc * LUCK_ARROW_RECOVER_STEP_BP_PER_POINT, 0, 10000).
- RNG-contract сохраняется как в ARROW_RECOVER_RNG_CANON (rng_stream/context/scope_id/draw_index не меняются).
- Explain:
 - RULE_LUCK_CHANCE_MOD meta{kind="arrow_recover", base_chance_bp, chance_bp, luck=luck_misc}

@@END:B22.LUCK.CANON.06@@
@@BEGIN:B22.LUCK.DATA.01@@
[DATA] 22.6 Поля/таблицы и политики (enforceable)
22.6.1 Константы
- LUCK_BONUS_SLOTS_MAX:int
 - perf guard; рекомендуемо 6..10 (чтобы LUCK=1000 не создавал сотни draw).
- LUCK_MISC_CAP_STAT:int
 - cap для “мягких” эффектов (survival/procs); рекомендуемо 100.
- LUCK_POISON_STEP_BP_PER_POINT:int
 - на сколько bp уменьшать шанс poison за 1 LUCK (после luck_misc cap); рекомендуемо “малое”.
- LUCK_VISIT_STEP_BP_PER_POINT:int
 - на сколько bp уменьшать шанс визита/засады за 1 LUCK; рекомендуемо “малое”.
- LUCK_SHIELD_STEP_BP_PER_POINT:int
 - на сколько bp увеличивать шанс shield proc за 1 LUCK; рекомендуемо “очень малое”.
- LUCK_ARROW_RECOVER_STEP_BP_PER_POINT:int
 - на сколько bp увеличивать шанс arrow recover за 1 LUCK; рекомендуемо “очень малое”.

22.6.2 COFFER_DEF (расширение данных)
- COFFER_DEF:
 - coffer_id:string
 - k_slots:int
 - slot_table_id[]:string
 - luck_bonus_ing_pool_id?:string // если отсутствует → LUCK bonus slots выключены для данного кофера

22.6.3 Пулы бонусных ингредиентов (2 семейства)
- Рекомендуемые pool_id (конвенции):
 - POOL_LUCK_ING_NONLEG_*: без legendary:ingredient/core
 - POOL_LUCK_ING_LEG_*: допускает legendary:ingredient/core (и только их из “legendary”)
- Контент-наполнение NONLEG:
 - rare/epic реагенты/материалы (но не legendary),
 - расходники выживания (медицина/антисептик/ремнаборы/боеприпасы),
 - компоненты/инструменты крафта (ускоряют подготовку к следующему риску).
- Контент-наполнение LEG:
 - legendary:ingredient / legendary:core (как “двигатель легендарок”),
 - допускаются также high-quality nonleg ингредиенты (по желанию баланса).

22.6.4 Data-policy (валидаторы; fail-fast)
- V_LUCK_BONUS_POOL_NONEMPTY:
 - если coffer_def.luck_bonus_ing_pool_id задан → Σweights(pool)>0.
- V_LUCK_BONUS_POOL_INGREDIENT_ONLY:
 - все entries в bonus pool должны быть ingredient/core (запрещено equip:*).
- V_LUCK_BONUS_POOL_LEGENDARY_ONLY_ING_CORE:
 - если entry имеет legendary:* → только legendary:ingredient или legendary:core.
- V_NO_LEGENDARY_EQUIP_FROM_BONUS_POOLS:
 - запрещено наличие “готовой legendary экипировки” в любых luck bonus pools.
- V_ARCHIVE_ANTI_ABUSE_COMPAT (если coffer относится к низкой ликвидности / архивным):
 - bonus pool для таких coffer обязан удовлетворять их анти-абуз ограничениям (не появляется в city_shops[].inventory и не eligible для SHOP_EXCHANGE).

@@END:B22.LUCK.DATA.01@@
[ASSUMPTION] 22.7 (минимальные допущения)
- FOOD_POISONING: RNG-contract (context/scope_id) ранее не был явно фиксирован в survival-блоке; этот раздел формализует его как "survival.food_poison" на RNG_INJURY.
- Если в проекте уже существует другой каноничный context/scope_id для пищевого отравления, использовать его вместо указанного, сохранив формулу модификации ChanceBp от LUCK.

[UI] 22.8 Отображение (ощущаемость без раскрытия seed)
- Описание стата LUCK:
 - “Каждые 100 LUCK добавляют бонусный слот ингредиента для COFFER.”
 - “Внутри каждой сотни: +0.1% за 1 LUCK к шансу слота, cap 10% на слот.”
 - “Для обычных coffer бонус-пул без легендарных ингредиентов; для особых coffer бонус-пул может содержать legendary ингредиенты/ядра.”
 - “Дополнительно: удача немного снижает риск отравления/засад и слегка повышает шанс полезных проков (щит/возврат стрел).”
- Экран результата лута:
 - При success бонус-слота показывать отдельной строкой: “Бонус удачи: ингредиент” (без чисел seed/весов).
- Для отладки/реплея полная математика идёт в explain (RULE_*), UI может её скрывать.

@@BEGIN:B22.LUCK.QA.01@@
[QA] 22.9 Инварианты и тесты (MVP)
Детерминизм / RNG
- SameInputSameResult: одинаковые (save+content_pack+world_seed+actor_luck+scope_id+решения) ⇒ одинаковые explain и лут.
- DrawSpecStable (coffer):
 - базовые draw_index не меняются;
 - bonus trigger draw_index = BASE_END + i*2;
 - bonus pick draw_index = BASE_END + i*2 + 1 (только при success).
- NoHiddenReroll: количество draw определяется draw_spec; не зависит от времени/FPS/UI.

Капы/границы
- SlotCap: slot_chance_bp ∈ [0..1000] для любого i.
- SlotsMax: n_slots ≤ LUCK_BONUS_SLOTS_MAX всегда.
- MiscCap: luck_misc ≤ LUCK_MISC_CAP_STAT всегда.

Контент/инварианты
- NoLegendaryEquip: в bonus pools отсутствует equip:* легендарной экипировки.
- NonlegCofferUsesNonlegPool: coffer, не предназначенный для легендарок, указывает на POOL_LUCK_ING_NONLEG_*.
- LegCofferUsesLegPool: coffer, предназначенный для легендарок, указывает на POOL_LUCK_ING_LEG_*.
- ArchiveCompatibility (если применимо): архивные/низколиквидные коферы используют bonus pool, удовлетворяющий их анти-абуз валидаторам.

Survival/Procs (мягкий эффект)
- PoisonChanceReduced: при увеличении luck_misc chance_bp для poison не растёт.
- VisitChanceReduced: при увеличении luck_misc chance_bp для poi visit не растёт.
- ProcChanceIncreased: при увеличении luck_misc chance_bp для shield_proc/arrow_recover не падает.
- NoExtraDraws: в survival/procs нет дополнительных RNG-use; меняется только порог ChanceBp.

PATCH NOTES
- Добавлен новый блок: B22 — LUCK (MVP).
- Добавлено правило: LUCK_BONUS_ING_SLOTS для LOOT_OPEN (RNG_LOOT) с фиксированным draw_spec (BASE_END + i*2 / +1).
- COFFER_DEF расширен полем luck_bonus_ing_pool_id? (data-only opt-in).
- Добавлены [DATA] константы: LUCK_BONUS_SLOTS_MAX, LUCK_MISC_CAP_STAT и шаги bp/point для poison/visit/procs.
- Формализован RNG-contract для FOOD_POISONING (если ранее не был явно зафиксирован) и добавлен LUCK-модификатор ChanceBp.
- Добавлены explain rule_id: RULE_LUCK_BONUS_ING_TRY, RULE_LUCK_BONUS_ING_RESULT, RULE_LUCK_CHANCE_MOD.
Добавлены валидаторы контента для bonus pools (ingredient-only, запрет legendary equip, non-empty, совместимость с анти-абузом для низколиквидных коферов).
@@END:B22.LUCK.QA.01@@
@@BEGIN:B22.LUCK.CANON.07@@
[CANON] 22.VN1 LUCK в HOME-контекстах (V_NEXT) — назначение и границы
- HOME не меняет глобальную LUCK в экспедициях/бою и не “подкручивает мир” вне дома.
- HOME вводит *home-scoped* усиление удачи только для контекстов, относящихся к дому (например salvage/craft/home coffers).
- Усиление применяется только в тех процедурах, где LUCK уже является входом по канону (например LUCK_BONUS_ING_SLOTS и/или luck_misc, если они включены).
- Активируется data-driven правилом по префиксу контекста (см. HOME_LUCK_POLICY). Рекомендуемый префикс: "home.".

Ссылка
- Спецификация HOME_HUB (storage/sleep/stations/salvage/upgrade) находится в B23 (V_NEXT).
@@END:B22.LUCK.CANON.07@@
@@BEGIN:B22.LUCK.CANON.08@@
[CANON] 22.VN2 LuckEffHome (как считается, fixed-point, без “магии”)
Определения
- LuckBase = текущая удача актёра (derived stat) по существующему канону.
- LuckHomeMultBp = bp-мультипликатор, задаваемый окружением/эффектами дома.

Расчёт (формулы — как контракт, без вычисления результата Master/LLM)
- LuckHomeMultBp =
  clamp_bp(
    10000 + (HOME_LUCK_MULT_PCT + RESTED_LUCK_MULT_PCT) * 100,
    10000,
    10000 + HOME_LUCK_CAP_PCT * 100
  )
- LuckEffHome = apply_bp_floor(LuckBase, LuckHomeMultBp)

Капы/стакинг
- Оформлять через общий механизм CAP_BY_EFFECT_ID / CAP_BY_FAMILY:
  либо family LUCK_MULT_PCT,
  либо отдельная family LUCK_HOME_MULT_PCT (если в проекте принято разделять дом/вне дома).

Save/cache
- luck_eff_home допускается как cache-only поле (например в home_effects_cache).
- MUST recompute on load (кэш не является источником истины).
@@END:B22.LUCK.CANON.08@@
@@BEGIN:B22.LUCK.CANON.09@@
[CANON] 22.VN3 RNG/LOOT интеграция в HOME (без reroll, без extra RNG “в слоте”)
Ключевой принцип
- HOME не добавляет “перероллы” и не создаёт дополнительных RNG-процедур.
- HOME лишь подаёт *actor_luck = LuckEffHome* вместо LuckBase для HOME-контекстов, а далее работает существующий LUCK-контракт.

Требование по реализации HOME-выдачи (outputs)
- Любые HOME-операции, которые могут выдавать вариативные outputs (например salvage или side-yield),
  оформляются через LOOT/COFFER-паттерн, чтобы LUCK работала через bonus slots appended after base_end.
- Контекст для keyed-RNG должен быть явным и стабильным (например "home.salvage.open" / "home.craft.side_yield").
- RNG key (канон): (world_seed, RNG_LOOT, context, scope_id, draw_index).

Анти-абуз
- scope_id обязан включать уникальный id действия (salvage_id / craft_action_id), чтобы “перезаход” не давал новый pick.
@@END:B22.LUCK.CANON.09@@
@@BEGIN:B22.LUCK.CANON.10@@
[CANON] 22.VN4 HOME Salvage через coffer (рекомендуемый V_NEXT путь)
- Salvage выдача оформляется как открытие “salvage coffer”, привязанного к item_id/station_id.
- LOOT_OPEN meta{pool_id=salvage_pool_id, context="home.salvage.open", scope_id=salvage_id}
- Base slots: draw_index = 0..(k_base_slots-1) — фиксированный порядок.
- LUCK bonus slots: строго по канону LUCK (bonus slots appended after base_end; без изменения базовых слотов).

[DATA] связывание
- k_base_slots, salvage_pool_id и каталоги выходов — в B23/SALVAGE_TABLE и LOOT_TABLE_DEF.
@@END:B22.LUCK.CANON.10@@
@@BEGIN:B22.LUCK.CANON.11@@
[CANON] 22.VN5 HOME Craft (если когда-нибудь нужен RNG-aspect)
- Крафт по умолчанию детерминированен (без RNG успеха/провала).
- Если нужен RNG-аспект (например “side-yield”), он оформляется через coffer-паттерн:
  LOOT_OPEN meta{pool_id=..., context="home.craft.side_yield", scope_id=craft_action_id}
- LUCK работает через те же bonus slots (без “самодельных перероллов”).
@@END:B22.LUCK.CANON.11@@
@@BEGIN:B22.LUCK.CANON.12@@
[CANON] 22.VN6 Non-goals (жёсткие запреты)
- Никаких “перероллов если не понравилось”.
- Никаких дополнительных бросков внутри базового слота кофера поверх его draw_spec.
- Никаких новых RNG-stream’ов для “удачи дома” — только существующий RNG_LOOT с явным context/scope_id.
- Никакого превращения LUCK в новую боевую механику (криты/новые фазы/новые типы урона).
@@END:B22.LUCK.CANON.12@@
@@BEGIN:B22.LUCK.DATA.02@@
[DATA] (DB_SPEC) — LUCK (домашная привязка, V_NEXT)
HOME_LUCK_POLICY:
use_luck_eff_home_only_for_context_prefix = "home."
luck_misc_enabled_for_home_contexts: bool (если в LUCK-каноне есть luck_misc-процедуры)
(опционально) luck_bonus_ing_pool_id (если coffer_def требует отдельную ссылку)

Параметры множителя удачи дома (все значения — [DATA], см. PARAM_REGISTRY/DB_SPEC)
RESTED_LUCK_MULT_PCT
HOME_LUCK_MULT_PCT
HOME_LUCK_CAP_PCT
@@END:B22.LUCK.DATA.02@@
[UI]
- В UI статов показывать LUCK как int.
- В HOME UI (если включён HOME_LUCK_POLICY): показывать “эффективная удача дома” (LuckEffHome) как derived показатель без раскрытия seed/весов.
- В UI кофера/сальважа: допускается пометка “удача может добавить бонус-ингредиент” без вероятностей.
@@END:B22.LUCK@@
@@END:B22@@
@@BEGIN:B23@@
## B23 — HOME_HUB_PERSONAL_CORNER (V_NEXT) — «Личный уголок»
@@BEGIN:B23.HOME@@

@@BEGIN:B23.HOME.CANON.01@@
[CANON] Назначение и границы
HOME_HUB — безопасный хаб персонажа: storage + отдых/сон + станции + salvage/discard + апгрейды.
HOME_HUB не является симулятором поселения: нет фоновых тиков/прогресса без явного TIME_ADVANCE.
HOME_HUB не даёт “бесконечный перенос”: бесконечность допустима только как ёмкость стационарного storage, при сохранении всех правил переносимого веса/перевеса для carried-инвентаря.
@@END:B23.HOME.CANON.01@@

@@BEGIN:B23.HOME.CANON.02@@
[CANON] State (Save)
save.home.home_state[home_id]:
home_id: string
home_tier: int
home_quality_tier: int (качество окружения/быта)
home_storage_policy_id: string
home_storage: map[item_instance_id -> {item_id, qty, ...}]
placed_stations: array[{slot_index:int, station_id:string}]
rested_status?: {status_id:"HOME_RESTED", time_left_sec:int}
home_effects_cache?: { fat_rate_eff_bp:int, ... } (cache-only, MUST recompute on load)
home_ledgers:
applied_event_ids: set[event_id] (общий guard идемпотентности)
daily_ledger?: { last_applied_day_index:int } (если используются daily-эффекты)
job_ledger?: map[job_id -> {status, claimed:bool}] (если используется job/queue)
@@END:B23.HOME.CANON.02@@

@@BEGIN:B23.HOME.CANON.03@@
[CANON] Operations / CHANGELOG
Все HOME-события обязаны быть идемпотентны по event_id (повтор → SKIP/NOOP без side effects). Порядок применения событий — общий канон сортировки changelog.

Навигация / режим
HOME_OPEN meta{home_id}
HOME_LEAVE meta{home_id}
Preconditions: carried состояние валидно (см. переносимый вес).

Хранилище
HOME_TRANSFER meta{home_id, dir, item_instance_id, qty}
dir ∈ {TO_HOME, TO_CARRIED}

TO_CARRIED:
- применяет те же проверки/капсы/запреты, что и обычный TAKE/MOVE в общем инвентаре (включая AbsoluteMax-гейт).
- если перенос делает carried невалидным → SYS_CONFLICT(PRECONDITION_FAILED) и никаких мутаций.

Детерминизм выбора стака/экземпляров при частичном списании:
- stable order по item_instance_id asc.

Сон/отдых
HOME_SLEEP meta{home_id, sleep_blocks:int}
sleep_blocks >= 1, delta_sec = sleep_blocks * 3600
Выполнение: TIME_ADVANCE{delta_sec} + восстановление по канону сна через QualityMult_bp, зависящий от home_quality_tier (см. [DATA]).

HOME_REST meta{home_id, rest_sec:int}
rest_sec > 0, выполнение строго через TIME_ADVANCE{rest_sec}

Rested статус
HOME_REST_APPLY meta{home_id, reason}
Preconditions: actor находится в HOME; критерии отдыха выполнены (см. [DATA] thresholds).
Effects:
- установить/обновить rested_status.time_left_sec = HOME_RESTED_DURATION_SEC
- при повторном применении: разрешено “refresh” (с тем же event_id — нет; с новым — да).

HOME_REST_TICK не существует как отдельное событие:
- таймеры уменьшаются только внутри TIME_ADVANCE.

Станции / апгрейды
HOME_PLACE_STATION meta{home_id, slot_index:int, station_id:string}
Preconditions: slot_index доступен в home_tier; station_id разрешён и выполнены требования.
Effects: поставить/заменить станцию в слоте.

HOME_BUILD_UPGRADE meta{home_id, upgrade_id:string}
Consume: списание ресурсов детерминированно (stable order).
Time: включает TIME_ADVANCE{upgrade_time_sec}.
Apply: изменить home_tier/home_quality_tier/unlocks согласно [DATA].

Salvage / Discard
HOME_SALVAGE_START meta{home_id, item_instance_id, qty, station_id}
Preconditions: предмет/qty валидны; станция подходит; предмет не “protected” (см. [DATA]).
Time: TIME_ADVANCE{salvage_time_sec}.

HOME_SALVAGE_DONE meta{home_id, salvage_id, outputs_ref}
Effects:
- списать входы (stable order), добавить outputs.
- Outputs получаются через LOOT/COFFER-паттерн (через LOOT_OPEN), чтобы вариативные выдачи были детерминированы и единообразны.
  (Если включены бонус-слоты удачи для HOME-контекстов — это описано в B22.)

HOME_DISCARD_ITEM meta{home_id, item_instance_id, qty}
Time: опционально TIME_ADVANCE{discard_time_sec} (чтобы это было “действием”, а не мгновенной кнопкой).
Apply: списать qty (stable order).
@@END:B23.HOME.CANON.03@@

@@BEGIN:B23.HOME.CANON.04@@
[CANON] TIME
Вне боя время течёт только через TIME_ADVANCE{delta_sec}.
“Сутки” для длительностей эффектов: 86400s.
rested_status.time_left_sec уменьшается в TIME_ADVANCE на active_sec = min(delta_sec, time_left_sec); при 0 статус считается снятым.
@@END:B23.HOME.CANON.04@@

@@BEGIN:B23.HOME.CANON.05@@
[CANON] Effects (fixed-point)
1) Rested (HOME_RESTED)
- Rested влияет на фоновую усталость (rate в TIME_ADVANCE), а не на “стоимость действий”.
- Эффект задаётся как FAT_AWAKE_RATE_MULT_PCT (в [DATA], применяется как bp).
- Duration: HOME_RESTED_DURATION_SEC (в [DATA]).

Примечание
- Интеграция LUCK в HOME-контекстах (LuckEffHome, HOME_LUCK_POLICY, coffer contract) описана в B22 (V_NEXT).
@@END:B23.HOME.CANON.05@@

@@BEGIN:B23.HOME.DATA.01@@
[DATA] (DB_SPEC)
HOME_STORAGE_POLICY
policy_id
infinite_slots: bool = true
remote_access: bool = false
transfer_requires_in_home: bool = true
to_carried_validates_encumbrance: bool = true

HOME_UPGRADES
upgrade_id -> {req_home_tier, cost_items[], upgrade_time_sec, add_station_slots, set_quality_tier, unlock_station_tags[]}

HOME_QUALITY_TIER_TABLE
home_quality_tier -> QualityMult_bp (используется сном/восстановлением)

HOME_RESTED_PARAMS
HOME_RESTED_DURATION_SEC
FAT_AWAKE_RATE_MULT_PCT
REST_APPLY_REQUIREMENTS (минимальные условия: минимум блоков сна, качество, и т.п.)

HOME_STATION_CATALOG
station_id -> {slot_tag, req_home_tier, build_cost[], supported_ops[]}

SALVAGE_TABLE
salvage_recipe_id -> {input_item_tags_all, station_req, salvage_time_sec, salvage_pool_id, k_base_slots}
salvage_pool_id -> LOOT_TABLE_DEF (weights/каталог в data)

DISCARD_RULES
deny_tags_any[] (например quest/unique/equipped)
allow_if_no_salvage: bool
discard_time_sec
(опционально) discard_fee_cu (если нужно как денежный “сжигатель мусора”)
@@END:B23.HOME.DATA.01@@

@@BEGIN:B23.HOME.UI.01@@
[UI]
HOME tabs: Storage / Stations / Sleep&Rest / Salvage / Discard / Upgrades

Sleep&Rest показывает:
- home_quality_tier (как понятный “уровень уюта/быта”)
- прогноз восстановления (без “скрытых бросков”)
- активный Rested + таймер

Salvage screen:
- выбранный предмет
- ожидаемые категории outputs (без вероятностей)
- пометка о детерминированности выдачи (через coffer), без раскрытия seed/весов
@@END:B23.HOME.UI.01@@

@@END:B23.HOME@@
@@END:B23@@

@@BEGIN:B24@@
## B24 — LOOT: COFFER/POOLS/LOOT_OPEN (MVP)
@@BEGIN:B24.LOOT@@

@@BEGIN:B24.LOOT.CANON.01@@
[CANON] Назначение и границы (сборка домена LOOT)
• Этот раздел агрегирует и нормализует LOOT/COFFER-канон в одном месте.
• Источники: B10 (services), B12 (craft/cook/alch выдачи), B18 (quest reward coffer), B19 (elite bonus loot), B22 (LUCK↔COFFER).
• Канон/алгоритмы не менялись: перенос только структурный; [DATA] остаётся в DB_SPEC/PARAM_REGISTRY.
@@END:B24.LOOT.CANON.01@@

@@BEGIN:B24.LOOT.CANON.10@@
[CANON] DB_FILL_PATCH::LOOT_COFFERS_DB_SPEC (MVP)
• Цель: сделать LOOT_POOL_DEF/COFFER_DEF «DB-fill ready» без последующих миграций; без контентных каталогов.
• Термины: LOOT_POOL (пул строк), LOOT_ROW (строка пула), COFFER (обёртка над пулом/пулами + число базовых слотов).

LOOT_POOL_DEF (content)
• pool_id:string (immutable).
• rows[]: LOOT_ROW_DEF.
LOOT_ROW_DEF (content)
• row_id:string (рекомендуется; immutable в пределах pool_id). Если row_id отсутствует — build-step обязан присвоить детерминированный row_id и зафиксировать его в runtime pack.
• item_id:string (immutable ref).
• qty:int>=1 (фиксированное; в MVP нет RNG количества внутри строки. Вариативность количества — через несколько строк).
• weight_int:int>=0 (вес для WEIGHTED_SAMPLING_CANON).
• Примечание: в MVP нет cond_* на строке. Условность выражается выбором другого pool_id/coffer_id в [DATA].

COFFER_DEF (content)
• coffer_id:string (immutable).
• k_slots:int>=1 — число базовых pick-слотов (K).
• mode: "SLOT_TABLE" | "K_PICKS" (если отсутствует: mode = SLOT_TABLE при наличии slot_pool_ids[], иначе K_PICKS).
• K_PICKS (один pool на K слотов):
- pool_id:string (ref). Открытие — COFFER_OPEN_CANON: Pass A without-replacement, Pass B with-replacement (только если K>pool_size). draw_index=i (0..K-1).
• SLOT_TABLE (таблица слотов, один pool на слот):
- slot_pool_ids[]: pool_id[] длиной k_slots (порядок семантический, НЕ сортировать). Legacy aliases допускаются: slot_loot_table_ids / loot_table_ids.
- Слот i: 1 pick по WEIGHTED_SAMPLING_CANON из pool=slot_pool_ids[i], draw_index=i (0..k_slots-1).
• (опц.) luck_bonus_ing_pool_id:pool_id — включение LUCK-bonus по канону B22; отсутствие поля = LUCK-bonus выключен для данного кофера.
@@END:B24.LOOT.CANON.10@@

@@BEGIN:B24.LOOT.CANON.11@@
[CANON] Валидаторы (build-step + load-time, fail-fast)
• pool_id/coffer_id/row_id/item_id references должны существовать; unknown → fail-fast.
• LOOT_POOL_DEF: row_id уникален в пределах pool_id; qty>=1; weight_int>=0; Σweight_int по eligible rows > 0 (иначе pool считается пустым).
• COFFER_DEF: k_slots>=1; для SLOT_TABLE: len(slot_pool_ids)==k_slots и каждый pool существует; для K_PICKS: pool_id существует.
• Stable order: pool.rows обходятся в порядке row_id asc (или экв. стабильный порядок, зафиксированный в runtime pack).
@@END:B24.LOOT.CANON.11@@

@@BEGIN:B24.LOOT.CANON.12@@
[CANON] RNG/Scope контракт (для всех LOOT_OPEN, deterministic)
• LOOT_OPEN всегда задаёт: rng_stream=RNG_LOOT, context:string, scope_id:string, draw_index:int.
• context — стабильный литерал (например "quest.archive_reward.open" / "poi.cache.open" / "service.salvage" / "craft.output.open").
• scope_id — стабильный instance_id из save/changelog (quest_instance_id / poi_instance_id / event_id); запрещено: real-time, FPS, UI-seed, «случайные» UUID без сохранения.
• Никаких дополнительных draw «внутри слота»: 1 draw на 1 pick; всё сверх базовых слотов допускается только как отдельные, явно задокументированные слоты (пример: LUCK bonus после BASE_END).
@@END:B24.LOOT.CANON.12@@

@@BEGIN:B24.LOOT.CANON.13@@
[CANON] ITEM_GRANT_VIA_COFFERS (MVP) — «Единый кран выдачи предметов»
• Определение: item_grant = появление новых item_instance/стаков у игрока (не transfer существующих).
• Правило: любой item_grant MUST происходить только через LOOT_OPEN(coffer_id) + применение результатов (RULE_LOOT_PICK -> INVENTORY_ADD).
• Запрещено: прямое INVENTORY_ADD предметов как «награда/ремонт/крафт/сервис» минуя coffer-пайплайн.
• Исключения: (A) CU/статусы/прогресс — не предметы; (B) transfer между контейнерами/слотами/владельцами — не item_grant.
• Следствие: все источники предметов (квест/бой/POI/контейнер/крафт/сервисы) обязаны ссылаться на coffer_id (data-only), даже если выход детерминирован (кофер с 1 строкой, weight=1).
@@END:B24.LOOT.CANON.13@@

@@BEGIN:B24.LOOT.DATA.10@@
[DATA] SOURCE->COFFER_ID MAPPING (DB_SPEC)
• quest rewards: rewards.reward_coffer_id
• combat/encounter rewards: reward_coffer_id / bonus_coffer_id (elite)
• POI containers/caches: loot_coffer_id / open_coffer_id
• services with item outputs: output_coffer_id (или mapping input_item_id -> output_coffer_id для repair)
• craft/cook/alch outputs: output_coffer_id (или build-step derived coffer из recipe.produce)
@@END:B24.LOOT.DATA.10@@

@@BEGIN:B24.LOOT.CANON.14@@
[CANON] COFFER_OPEN_CANON (MVP, deterministic)
• Кофер открывается как последовательность K pick-слотов; результат = K строк {item_id, qty} в фиксированном порядке draw_index.
• Eligible rows: строки пула/таблицы с weight_int>0. Stable order rows обязателен: row_id asc (предпочтительно). Если row_id отсутствует — валидатор build-step обязан присвоить row_id детерминированно и сохранить в runtime pack.
• Draw spec (строго): ровно 1 draw на 1 pick; никаких дополнительных draw “внутри слота”, перероллов и зависимостей от порядка обхода коллекций.
• Pass A (without replacement): k1 = min(K, pool_size). Для i=0..k1-1 выполнить WEIGHTED_SAMPLING_CANON (roulette) по текущим weight_int; после выбора строки её weight_int устанавливается в 0 для следующих picks. draw_index=i.
• Pass B (with replacement, только если K>pool_size): для i=k1..K-1 выполнить WEIGHTED_SAMPLING_CANON с повторами по исходному набору eligible rows (веса не “обнуляются” между picks Pass B). draw_index=i.
• RNG key template (keyed): RngKey=(world_seed, rng_stream=RNG_LOOT, context, scope_id, draw_index=i). context/scope_id задаёт вызывающая подсистема (craft/loot/quest/elite/poi) и MUST быть стабильной строкой/ID.
• Explain/Trace: RULE_LOOT_PICK meta{pool_id, draw_index, item_id, qty} — строго по draw_index 0..K-1.
• Fail-fast: если K<=0 или pool_size==0 → SYS_CONFLICT(INVALID_VALUE/PRECONDITION_FAILED) без мутаций.
@@END:B24.LOOT.CANON.14@@

@@BEGIN:B24.LOOT.DATA.11@@
[DATA] COFFER_SLOT_COUNTS_BY_GRADE (пример/дефолты; DB_SPEC): P=7, N=10, R=14, BOSS=20.
@@END:B24.LOOT.DATA.11@@

@@BEGIN:B24.LOOT.DATA.12@@
[DATA] Веса сложности (мультипликатор к base_weight по Grade; DB_SPEC/balance): G1/A1=10000bp; G2/A2=6000bp; G3/A3=3000bp; G4/A4=2000bp; G5/A5=1200bp. (Можно зашить в base_weight вручную.)
Легендарное правило: обычные коферы не выдают готовую легендарную экипировку; вместо этого они могут (очень редко) добавить легендарный ресурс/ядро для крафта/LEGENDARY_INFUSE.
@@END:B24.LOOT.DATA.12@@

@@BEGIN:B24.LOOT.CANON.20@@
[CANON] RNG/Scope для service outputs (через LOOT_OPEN)
• LOOT_OPEN(output_coffer_id) обязателен использовать:
- rng_stream=RNG_LOOT
- context = "service.<service_id>.open" (или "service.salvage" как общий контекст, если уже каноничен)
- scope_id = event_id (SERVICE_PAY) или иной сохранённый idempotency-key этого вызова
- draw_index = slot_i (0..K-1) по базовым слотам кофера
• Следствие: «no reroll by reload» достигается автоматически — повтор применения одного event_id не меняет исход (и вообще должен быть SKIP).
• Термин совместимости: если в тексте/коде встречается service_call_id — в MVP это alias на event_id соответствующего SERVICE_PAY.
@@END:B24.LOOT.CANON.20@@

@@BEGIN:B24.LOOT.CANON.30@@
[CANON] 18.1 Правило MVP (и происхождение quest:archive_sample — coffer-only)
[CANON] DB_FILL_PATCH::TAG_REGISTRY (MVP)
• tag_id immutable; смысл тега не меняется без нового tag_id.
• Минимальные namespaces (используются в каноне): quest:*, item:*, trade:*, status:*, service:*, loot:*, archive:*, poi:*, world:*, env:*, tone:*, flavor:*, ration:*, legendary:*, threat:*, elite:*.
• Unknown tag_id / class_id forbidden: build-step и load-time fail-fast.
• Каждая подсистема имеет allowlist по tag_namespace (в [DATA]/DB_SPEC): QUESTS, SHOPS/EXCHANGE, CRAFT, LOOT, IDENTIFY, REPAIR, SALVAGE. Теги вне allowlist → reject (валидация), не UI.
• Фильтры используют tags_all/tags_any/tags_none (или экв.); списки сортируются asc при сериализации/хешах.
• Квест «Опись» НЕ идентифицирует предметы игроку.
• Он принимает только UNIDENTIFIED образцы с тегом quest:archive_sample и выдаёт награду по шаблону контракта.
• Сдаваемые предметы удаляются из инвентаря: INVENTORY_REM (см. 18.4.2).
Происхождение quest:archive_sample (строго: только из LOOT_OPEN результата)
• Тег quest:archive_sample не может:
• быть добавлен игроком/UI-действием,
• появиться “постфактум” после получения предмета,
• приходить из путей, которые не являются результатом LOOT_OPEN.
• quest:archive_sample назначается только при создании item_instance как часть результата LOOT_OPEN (data-driven: spawn_tags_add=["quest:archive_sample"] или эквивалент).
• Никаких отдельных RNG-вызовов “ради назначения тега” не вводится: тег — атрибут уже выбранного loot entry.
• Инвариант: item_instance с quest:archive_sample создаётся как UNIDENTIFIED.
Поведение при идентификации (чтобы квест не “съедал” опознанное)
• После SERVICE_IDENTIFY предмет перестаёт быть UNIDENTIFIED и не проходит фильтр сдачи filter_tags_all=["UNIDENTIFIED","quest:archive_sample"].
(Опционально: клиент может снимать quest:archive_sample при идентификации как data-санитарию; для логики квеста не требуется.)
[CANON] DB_FILL_PATCH::IDENTIFY_MODEL (MVP)
• UNIDENTIFIED — instance-level состояние (is_identified=false и/или instance_tag), не def-tag.
• MVP (минимум churn): SERVICE_IDENTIFY не меняет item_id; только is_identified=true и (опц.) снимает UNIDENTIFIED.
• V_NEXT (feature-gate): если понадобится “после идентификации другой item_id” — ItemDefinition.identified_item_id. До фиксации модели — запрещено для массового DB-fill.
@@END:B24.LOOT.CANON.30@@

@@BEGIN:B24.LOOT.CANON.31@@
[CANON] 18.5 Детерминизм наградного кофера (Quest Reward Coffer)
Цель: LOOT_OPEN(reward_coffer_id) в рамках QUEST_COMPLETE должен быть детерминированным и идемпотентным по event_id (повтор обработки события завершения не выдаёт награду повторно).
18.5.1 Термины и входы
• quest_instance_id — стабильный id инстанса.
• event_id — id события завершения, являющийся ключом идемпотентности награды.
• k_slots — число слотов наградного кофера (для данного reward_coffer_id).
[ASSUMPTION] k_slots берётся из данных кофера/таблиц и фиксируется в момент завершения (чтобы не “поплыть” при смене данных).
18.5.2 RNG-контракт (строго)
• rng_stream = RNG_LOOT
• context = "quest.archive_reward.open"
• scope_id = quest_instance_id
• draw_index = slot_i (0..k_slots-1)
Запрещено: доп. RNG “внутри слота”, перероллы, зависимость от времени/FPS/порядка обхода коллекций.
18.5.3 Правило “1 draw → 1 результат”
Для каждого slot_i выполняется ровно один pick из slot_table_id[slot_i].
Если нужна вариативность qty — она кодируется разными строками таблицы (item_id/qty как часть entry), без дополнительных RNG.
18.5.4 Идемпотентность (ledger)
• Повтор event_id не должен повторно делать INVENTORY_ADD/изменять валюту.
• Детерминированный “повторный показ” результата допускается из сохранённого resolved-результата.
[DATA] RewardClaimLedger (минимум): event_id, quest_instance_id, context, k_slots, reward_lines_resolved[], applied=true.

[CANON] 18.6 Контент наград (COF_ARCHIVE_OPIS_T1..T5) — совместимо с 18.5 (1 draw на слот)
COF_ARCHIVE_OPIS_T1..T5 — reward_coffer_id для «Архивной описи». Они дают только утилитарные награды (поддержка вылазки/базового крафта) + опциональный лор-разблок (досье), без ускорения прогрессии.
18.6.1 Запреты состава (fail-fast валидатором)
Запрещено в COF_ARCHIVE_OPIS_* (в любых slot_table):
• Любая валюта/суррогаты денег.
• Любые предметы со стат-ростом/перманентной силой/XP/перк-токенами.
• Любые item_id, имеющие канонический путь конвертации в CU через SHOP_SELL/SHOP_EXCHANGE (см. 18.7.3–18.7.5).
18.6.2 Слоты по tier (структура слотов = структура slot_table_id[])
(Примеры table_id — рекомендованный нейминг, не механика; механика = “одна таблица на слот”.)
• T1: k_slots=2
• slot0: LT_ARCHIVE_CONSUMABLE_T1
• slot1: LT_ARCHIVE_MATERIAL_T1
• T2: k_slots=2
• slot0: LT_ARCHIVE_CONSUMABLE_T2
• slot1: LT_ARCHIVE_MATERIAL_T2
• (лор-досье допускается как редкая строка в одной из этих таблиц; см. 18.6.3)
• T3: k_slots=3
• slot0: LT_ARCHIVE_CONSUMABLE_T3
• slot1: LT_ARCHIVE_MATERIAL_T3
• slot2: LT_ARCHIVE_COMPONENT_T3
• T4: k_slots=3
• slot0: LT_ARCHIVE_CONSUMABLE_T4
• slot1: LT_ARCHIVE_MATERIAL_T4
• slot2: LT_ARCHIVE_COMPONENT_T4
• T5: k_slots=4
• slot0: LT_ARCHIVE_CONSUMABLE_T5
• slot1: LT_ARCHIVE_MATERIAL_T5
• slot2: LT_ARCHIVE_COMPONENT_T5
• slot3: LT_ARCHIVE_FLEX_T5 (Flex реализуется составом одной таблицы: смешанные строки из категорий с нужными weight_int; без отдельного “выбора категории” и без доп. RNG)
18.6.3 ARCHIVE_DOSSIER_* (лор-разблок, без статов)
• ARCHIVE_DOSSIER_* может выпадать как редкая строка в slot_table (рекомендуемо — в Material/Flex таблицах соответствующих tiers).
• Досье не должно быть источником экономической выгоды:
• item_id досье отсутствует в city_shops[*].inventory и не eligible для SHOP_EXCHANGE,
• досье не конвертируется в ресурсы/валюту при дубликатах (data-policy + валидатор).
[ASSUMPTION] Если нужен “чистый journal unlock” без инвентарного предмета — оформить как отдельный apply-эффект loot entry (в рамках существующей системы progress_flags/journal), но без изменения RNG-контракта (всё равно 1 pick на слот).
[DATA] 18.6.D1 Мини-структуры (без контент-простыней)
• COFFER_DEF: coffer_id, k_slots, slot_table_id[]
• LOOT_TABLE_DEF: table_id, rows[]
• LOOT_ROW_DEF: row_id, item_id, qty:int>=1, weight_int>=0, spawn_tags_add[] (опц.)
@@END:B24.LOOT.CANON.31@@

@@BEGIN:B24.LOOT.CANON.40@@
[CANON] Если у MON_*_ELITE есть “бонус-лут”, он обязан быть реализован через стандартный coffer/loot пайплайн (см. 18.5) без новых RNG
• rng_stream=RNG_LOOT
• context="elite.bonus_loot.open"
• scope_id=spawn_instance_id
• draw_index=slot_i (0..k_slots-1)
• Идемпотентность: по event_id/RewardClaimLedger (паттерн как в 18.5). Повтор обработки не меняет инвентарь и возвращает ранее resolved результат.
• Запрещено: доп. RNG “внутри слота”, перероллы, зависимость от времени/FPS/порядка обхода неупорядоченных коллекций.

[CANON] Anti-abuse для бонус-лута (enforceable)
• Запрещено содержать CU/валюту/денежные суррогаты.
• (Если в проекте есть городские магазины/обмен) запрещено содержать item_id, которые:
 встречаются в city_shops[*].inventory[] или eligible для SHOP_EXCHANGE по exchange_rules (иначе канал CU-печати).
[ASSUMPTION] Если сущностей city_shops/exchange_rules ещё нет в MVP, минимум — запрет CU/валюты и предметов класса CURRENCY/TRADE_GOOD по тегам/классам.
@@END:B24.LOOT.CANON.40@@

@@BEGIN:B24.LOOT.CANON.90@@
[CANON] LUCK ↔ COFFER интеграция — ссылки на канон (не дублировать)
• LUCK bonus slots в COFFER (MVP): @@BEGIN:B22.LUCK.CANON.03@@ ... @@END:B22.LUCK.CANON.03@@
• Контракт bonus pools (MVP): @@BEGIN:B22.LUCK.CANON.04@@ ... @@END:B22.LUCK.CANON.04@@
• Legendary engine (MVP): @@BEGIN:B22.LUCK.CANON.05@@ ... @@END:B22.LUCK.CANON.05@@
• COFFER_DEF расширение (luck_bonus_ing_pool_id) и pool конвенции: @@BEGIN:B22.LUCK.DATA.01@@ ... @@END:B22.LUCK.DATA.01@@
• HOME (V_NEXT) использует LOOT_OPEN для salvage/side-yield: @@BEGIN:B22.LUCK.CANON.09@@ ... @@END:B22.LUCK.CANON.09@@ и @@BEGIN:B22.LUCK.CANON.10@@ ... @@END:B22.LUCK.CANON.10@@
@@END:B24.LOOT.CANON.90@@

@@BEGIN:B24.LOOT.QA.01@@
[QA] QA pointers (детерминизм / стабильные слоты / anti-reroll)
• Stable ordering: @@BEGIN:B03.STABLE_ORDERING_GLOBAL@@ ... @@END:B03.STABLE_ORDERING_GLOBAL@@
• RNG policy: @@BEGIN:B03.RNG_STATE_POLICY@@ ... @@END:B03.RNG_STATE_POLICY@@
• LUCK/COFFER draw_spec invariants: @@BEGIN:B22.LUCK.QA.01@@ ... @@END:B22.LUCK.QA.01@@
@@END:B24.LOOT.QA.01@@

@@END:B24.LOOT@@
@@END:B24@@
