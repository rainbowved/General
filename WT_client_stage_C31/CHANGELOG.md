# CHANGELOG — WT Client Stages C0–C11

- Создан каркас репозитория `wt_client/` с разделением `core/`, `ui/`, `tests/`, `tools/`.
- Добавлен CLI: `python -m wt_client --demo` и `python -m wt_client --pack <zip>`.
- Добавлен `config.json` (пути: datapack_path, save_root, logs_dir) + безопасный fallback.
- Добавлено логирование в stdout и файл.
- Реализован demo-smoke: проверка структуры datapack ZIP и печать отчёта.
- Добавлены минимальные unit tests (pytest).

## Stage C1 — ContentPackLoader + Validator

- Добавлен модуль `core/content_pack.py`:
  - `ContentPack` (абстракция поверх ZIP/директории)
  - `ContentPackLoader.load(path) -> ContentPack` с детектом "обёрнутого" корня
  - API: `list_files`, `open_text`, `open_binary`, `load_json`, `open_sqlite` (best-effort read-only)
- Добавлен валидатор `core/validate_pack.py`:
  - `validate_required_paths`
  - `validate_specs_json_parse`
  - `validate_turnpack_schema_load`
  - `validate_rng_streams_load`
  - форматированный `Health Report`
- CLI: `python -m wt_client --pack <path> --health`
- Добавлены тесты на загрузку ZIP и распакованной папки.

## Stage C2 — SaveStore + Migrations Skeleton

- Добавлен `core/save_store.py`:
  - детектирует layout сейва по demo (`save/` + опционально `session/`) или плоский (`*.json` в корне)
  - `load_save(save_dir) -> GameState(dict)` с чёткими секциями: `player/world/progress/inventory/session/meta/extras`
  - строгая валидация: обязательные файлы + обязательные поля/типы +一致ность `save_id`
  - `save_save(save_dir, state)` с детерминированной сериализацией JSON
- Добавлен каркас миграций `core/migrations.py`:
  - реестр `MIGRATIONS: {schema_version: fn}`
  - `apply_migrations_to_document(...)` (с hard-cap от бесконечных циклов)
- Добавлены тесты:
  - `test_load_demo_save`
  - `test_save_roundtrip`
  - `test_missing_file_validation`

## Stage C3 — ChangelogEngine (cursor + идемпотентность)

- Добавлен `core/changelog_engine.py`:
  - `ChangelogEngine.apply(events, state, cursor) -> (new_state, new_cursor, applied_count)`
  - курсор `cursor_v1`: список `seen_event_ids` + `seen_hash` (sha256), bounded (`max_size`, default 10000)
  - идемпотентность по `event_id` (повторное применение не меняет state)
  - атомарность: изменения откатываются при ошибке в одном событии
  - поддержаны типы событий из demo: `WORLD_MOVE`, `SYS_TURN_BEGIN/END`, `SYS_RNG_INIT/ADVANCE`, `INVENTORY_ADD_INSTANCES`
  - narrative-события (`encounter.select`, `combat.*`, `loot.generate`) обрабатываются как safe no-op (не мутируют SAVE)
- Добавлены тесты:
  - `test_demo_changelog_apply`
  - `test_demo_changelog_idempotent`

## Stage C4 — RngEngine (streams + counter=0 + snapshot)

- Добавлен детерминированный RNG по спекам `specs/rng_streams.json`:
  - `core/rng_state.py`: PCG32 (stable) + derive-per-stream seeding + skip-ahead (`advance`)
  - `core/rng_engine.py`: `init`, `next_u32`, `next_float01`, `advance`, `counter`, `snapshot/restore`
  - запрет использования до `init()` (явная ошибка)
  - поддержка восстановления из legacy demo `world.rng_state` (seed + streams:{index})
- Добавлены тесты:
  - `test_no_use_before_init`
  - `test_determinism_same_seed_and_snapshot_restore`
  - `test_stream_counter_increments_and_isolated`

## Stage C5 — TurnpackBuilder + JSON Schema validation

- Добавлен `core/turnpack_builder.py`:
  - `TurnpackBuilder.build(state, recent_actions, meta) -> dict`
  - минимальный `snapshot_min` (location/active_mode/summary)
  - нормализация `delta_events` с безопасными fallback для обязательных полей
- Добавлен `core/schema_validate.py`:
  - `validate_turnpack(turnpack, schema_json) -> (ok, errors)` на базе `jsonschema` draft-07
  - ошибки форматируются с путями (`cursor`, `delta_events[0].event_id`, ...)
- CLI:
  - `python -m wt_client --demo --export-turnpack out.json`
  - при невалидной схеме печатает список ошибок и возвращает exit code != 0
- Добавлены тесты:
  - TURNPACK по demo проходит schema validation
  - искусственная порча поля ловится валидатором

## Stage C6 — WorldResolver + NodeInteractions → доступные действия

- Добавлен `core/node_interactions.py`:
  - интерпретация `specs/node_interactions.json`
  - определение `node_type` по первому совпавшему rule
  - сбор действий: `node_types[node_type].actions` + `service_to_actions` по `ui.services`
  - детерминированная сортировка по `priority_order` (дубликаты удаляются)
  - выдача `sources` (почему действие доступно: `node_type:*` / `service:*`)
- Добавлен `core/world_resolver.py`:
  - загрузка world graph-ов из `db_bundle*/content/world/*_graph.json`
  - `get_current_node(state)` по `state.world.world.location`
  - `get_available_actions(node, state)` на базе NodeInteractions
  - `get_neighbors(state)` и `move(to_node_id, state)` с проверкой ребра графа
  - минимальные события для TURNPACK: `WORLD_MOVE` и `action.request`
- Добавлены тесты:
  - `test_actions_exist_for_demo_node`
  - `test_move_updates_location_and_turnpack_snapshot`

## Stage C7 — Encounter/Loot Resolver MVP (детерминированный лут)

- Добавлен `core/encounter_resolver.py`:
  - выбор энкаунтера для текущего узла по `node.links.encounter_table_id`
  - weighted selection из `content/encounters/encounter_tables.json` через `RNG_SPAWN`
  - минимальные события CHANGELOG: `SYS_RNG_ADVANCE`, `encounter.select`
- Добавлен `core/loot_resolver.py`:
  - резолв `loot_pool_id` через `db_bundle/json/items_loot.json` (pool_items)
  - deterministic pick+qty: 1 roll (u32) на 1 pick, без дополнительных RNG вызовов
  - детерминированные `instance_id`/`event_id` (hash-based)
  - события: `SYS_RNG_ADVANCE`, `loot.generate`
- Добавлен `core/inventory_delta.py`:
  - нормализация ItemInstance (location/origin)
  - применение add-instance дельт к `state.inventory.items` без стакинга (без новых механик)
- Добавлены тесты:
  - `test_demo_loot_deterministic`
  - `test_loot_pool_exists_on_demo_node`

## Stage C8 — CraftResolver + GROUP_* selectors

- Добавлен `core/selector_resolver.py`:
  - загрузка и интерпретация `specs/ingredient_selectors.json`
  - фильтры: `type_in`, `group_in`, `tags_all`, `tags_any`, `item_id_prefix_any`, `any_of/all_of`
  - детерминированный выбор кандидата: сортировка + tie-break через `RNG_CRAFT` (если инициализирован)
  - понятные ошибки: “нет кандидатов”
- Добавлен `core/craft_resolver.py`:
  - чтение рецептов из `db_bundle*/rpg_items.sqlite` (`recipes` + `recipe_ingredients`)
  - `GROUP_*` ингредиенты резолвятся через SelectorResolver
  - **feasibility-aware** выбор: селектор не выбирает кандидата, который “съест” явный ингредиент (если не хватает количества)
  - consume → produce: меняет `state.inventory.items` и генерирует события `INVENTORY_REMOVE_INSTANCES` / `INVENTORY_ADD_INSTANCES`
  - при выборе из нескольких кандидатов логирует `SYS_RNG_ADVANCE` по `RNG_CRAFT`
- Расширен `core/inventory_delta.py`:
  - `count_item_qty(state)`
  - `consume_item_qty(state, item_id, qty)` (детерминированное списание по `instance_id`)
- Добавлены тесты:
  - `test_selector_determinism` (GROUP выбор стабилен при фиксированном seed)
  - end-to-end крафт 7 реальных алхимических рецептов + GROUP-рецепт `RC_ALCH_APOTHEOSIS_SERUM`

Примечание по данным: в текущем datapack найден **ровно 1** рецепт с `GROUP_*` ингредиентами (Apotheosis Serum), поэтому покрытие “5–10 GROUP-рецептов” технически невозможно без расширения контента — но крафт и селекторы прогоняются на реальных данных и на нескольких рецептах (включая этот GROUP).

## Stage C9 — UI Vertical Slice (Load → Apply → Act → Export)

- Добавлен минимальный Tkinter UI: `python -m wt_client --ui`.
- UI позволяет:
  - выбрать datapack (ZIP или распакованная папка)
  - выбрать save (по умолчанию — demo save, извлечённый из datapack в `save_root/demo_runtime_ui`)
  - применить demo changelog (через `ChangelogEngine`, с курсором)
  - увидеть текущую локацию, список соседей (Move) и список доступных действий (Perform action → очередь событий)
  - экспортировать TURNPACK с локальной draft-07 schema validation и понятным списком ошибок.
- Добавлен лог событий в UI (последние N строк).
- CLI сохранён: `--demo`, `--pack`, `--health`, `--export-turnpack` работают как раньше.

## Stage C10 — ActionDispatcher (единый слой исполнения действий)

- Добавлен `core/action_dispatcher.py`:
  - `ActionDispatcher.dispatch(action_request, state, cursor) -> DispatchResult`
  - атомарность: все изменения выполняются на deepcopy и коммитятся только при успехе
  - идемпотентность по `event_id` через курсор (повторная отправка того же payload → `events=[]`)
  - простая схема `event_id`: `sha256(f"{save_id}:{turn}:{type}:{canonical_json(payload)}")[:16]`
  - snapshot/restore RNG в `state["rng"]`
  - человекочитаемые ошибки/варнинги без стектрейса для UI
- Поддержаны action types (MVP):
  - `move` → вызывает `WorldResolver.move()` и пишет `WORLD_MOVE`
  - `node_action` → проверка доступности по `NodeInteractions` + safe no-op для неподдержанных
    - реализован реальный обработчик `PROCEED`: `maybe_spawn_encounter → resolve_loot_pool → INVENTORY_ADD_INSTANCES`
  - `craft` → `CraftResolver` (GROUP_* селекторы) + события `INVENTORY_REMOVE_INSTANCES/INVENTORY_ADD_INSTANCES`
- Расширен `ChangelogEngine` поддержкой `INVENTORY_REMOVE_INSTANCES`.
- CLI расширен:
  - `python -m wt_client --demo --act <json_or_path> --export-turnpack out.json`
    - `--act` принимает JSON-строку или путь к `.json` файлу
    - если dispatch неуспешен → печатает список ошибок и exit code != 0
- UI (C9) подключён к `ActionDispatcher`:
  - кнопки Move/Perform action теперь делают `dispatch(...)` вместо прямых мутаций
  - события из `DispatchResult.events` добавляются в очередь для экспорта TURNPACK
- Добавлены тесты `test_action_dispatcher.py`:
  - `test_dispatch_move_commits_location`
  - `test_dispatch_idempotent_same_event_id`
  - `test_dispatch_craft_changes_inventory`
  - `test_dispatch_unknown_action_noop`

## Stage C11 — Замкнутый цикл TURNPACK → master CHANGELOG → apply

### 1) Node actions: расширены обработчики без новых механик

- `core/action_dispatcher.py` расширен набором **минимальных** handler-ов по данным `specs/node_interactions.json`.
- Поддержано (помимо уже существующих `PROCEED`):
  - `REST` / `CAMP_REST` → событие `MODE_SET` (только метка режима, без расчётов метров)
  - `ENTER_CITY` / `EXIT_CITY` / `ENTER_TOWER` → формализованный `WORLD_MOVE` на стартовый узел соответствующего графа
  - `WATER_REFILL` → **только** `action.request` (фиксация запроса, без новых вычислений)
- Любые другие `action_id`:
  - если действие доступно в текущей локации → **safe no-op**: пишем `action.request`, сейв не мутируем
  - если недоступно → true no-op (0 событий) с понятным UI-логом

### 2) RecentActions (очередь последних действий) для TURNPACK

- Добавлен `core/recent_actions.py`:
  - хранение в `state['progress'].recent_actions` (без файлов/скрытых путей)
  - после каждого `dispatch(...)` записывается: `turn_no`, `action_request`, `event_ids`, минимальные `events`
  - экспорт TURNPACK детерминированно берёт последние N действий и “плоский” список `delta_events`

### 3) Импорт CHANGELOG от мастера и apply (CLI)

## Stage C21 — Support bundle (репорт-zip для багов)

- Добавлен модуль `core/support_bundle.py`:
  - `create_support_bundle(...)` собирает `support_bundle_*.zip` в `.wt_logs/support_bundles/`.
  - Внутри: логи (`.wt_logs/*`, без вложенных support_bundles), последний экспортированный TURNPACK (`.wt_logs/last_turnpack.json`, если есть), и `meta/support_meta.json` (cursor/seed/pack_id + тех. окружение).
  - Полный сейв **не** включается (только мета без персональных данных).
- UI: кнопка `Support bundle…` + запись `last_turnpack.json` при Export TURNPACK.
- CLI: `--support-bundle [out.zip]` + запись `last_turnpack.json` при `--export-turnpack`.
- Тест: `test_support_bundle_creates_zip_with_logs_and_meta`.

- CLI теперь умеет применять мастерский changelog:
  - `python -m wt_client --pack <WT_data_release_candidate.zip> --save <SAVE_DIR> --apply-changelog <changelog.json>`
  - формат входа: `list[events]` **или** `{ "events": [...] }`
- Применение идемпотентно (через `ChangelogEngine` + cursor `seen_event_ids`).
- После apply синхронизируется RNG snapshot в `state['rng']` (best-effort).

### 4) UI wiring

- В Tkinter UI добавлена кнопка **“Apply master changelog…”**:
  - выбор файла JSON → apply через `ChangelogEngine` → refresh UI
- Экспорт TURNPACK теперь берёт `delta_events` из `recent_actions` (последние dispatch-результаты), чтобы исключить рассинхрон.

### 5) Тесты

- Обновлён/поправлен `test_action_dispatcher.py` (в т.ч. гарантия идемпотентности повторного действия).

## Stage C12 — Action Catalog → UI (клики вместо ручного JSON)

- Добавлен `core/action_catalog.py`:
  - читает `specs/node_interactions.json` из datapack
  - для заданного `(graph_id, node_id)` выдаёт стабильный список доступных `action_id`
  - метаданные: label/description (если есть в `action_catalog`), иначе fallback
  - флаг `record_only` (для действий без локального эффекта)
- UI (`ui/app.py`):
  - новый блок **«Доступные действия здесь»** с группировкой: travel / explore / rest / service / other
  - клик по действию отправляет `{"type":"node_action","action_id":...}` в `ActionDispatcher.dispatch(...)`
  - логирует: `events`, `applied`, и смену локации (если была)
  - для record-only действий явно пишет: “Запрос зафиксирован, изменения ожидаются ответом мастера.”
  - исправлен Move: `get_neighbors` вызывается на state, а не на node
- Добавлены тесты (самодостаточные, без внешнего datapack):
  - `test_action_catalog_lists_actions_for_demo_node`
  - `test_ui_action_request_dispatches`

## Stage C13 — Master CHANGELOG: JSON Schema + валидация + UX ошибок

### 1) Строгий контракт Master→Client CHANGELOG

- Добавлен парсер контейнера `core/master_changelog.py`:
  - поддержка форматов:
    - A) `[...]` (список событий)
    - B) `{ "events": [...], ...meta }`
  - `parse_master_changelog(input_json) -> (events, meta)`

### 2) JSON Schema для master changelog

- Добавлен файл `wt_client/specs/master_changelog_schema.json`.
- В строгом режиме валидируется:
  - контейнер (list или object с `events: list`)
  - события (обязательные поля `event_id`, `type`)
  - `type` ограничен только поддерживаемыми типами, которые реально обрабатывает `ChangelogEngine`.

Поддерживаемые типы (strict):
- `WORLD_MOVE`
- `SYS_TURN_BEGIN`, `SYS_TURN_END`
- `SYS_RNG_INIT`, `SYS_RNG_ADVANCE`
- `MODE_SET`
- `INVENTORY_ADD_INSTANCES`, `INVENTORY_REMOVE_INSTANCES`
- (narrative no-op) `encounter.select`, `combat.start`, `combat.end`, `loot.generate`, `action.request`, `craft.request`

### 3) Валидация и режимы strict/lenient (CLI + UI)

- CLI:
  - `python -m wt_client --pack <path> --save <dir> --apply-changelog <file.json>`
  - добавлен `--lenient`: неизвестные события пропускаются с warning (в строгом режиме — ошибка валидации)
  - выводит понятный Summary:
    - `events_total`, `applied`, `skipped_duplicates`, `unknown_ignored` (lenient), warnings
- UI:
  - кнопка **“Apply master changelog…”** валидирует вход перед apply
  - добавлен чекбокс **Lenient (ignore unknown)**
  - показывает Summary (и пишет в лог), без traceback

### 4) Идемпотентность apply

- Повторное применение того же master changelog:
  - `applied=0`, `skipped_duplicates>0`
  - state остаётся стабильным
  - курсор `seen_event_ids` используется как прежде (логика не менялась)

### 5) Тесты

- Добавлены тесты (самодостаточные, без внешнего datapack):
  - `test_master_changelog_schema_accepts_list_or_object`
  - `test_apply_master_changelog_idempotent`
  - `test_master_changelog_rejects_unknown_event_strict`
  - `test_master_changelog_lenient_skips_unknown_with_warning`

## Stage C14 — Save workflow: атомарные сейвы + rolling backups + restore

### 1) Crash-safe (атомарная) запись сейва

- `SaveStore.save_save(...)` теперь пишет в временную папку и **только потом** делает swap (rename) в целевой `SAVE/`.
- При сбое записи текущий сейв не портится: либо остаётся старый `SAVE/`, либо он откатывается из `.bak`.
- В UI/CLI ошибки показываются как короткое сообщение **без traceback** (traceback уходит в логгер).

### 2) Autosave policy (без новых механик)

- Автосохранение происходит **только если реально что-то применилось**:
  - после `dispatch(action)` — если `applied > 0`
  - после `apply master CHANGELOG` — если `summary.applied > 0`
- Если повтор/дубликаты (`applied == 0`) — state не меняется, autosave пропускается и это явно логируется.

### 3) Rolling backups (последние N)

- При каждом успешном autosave создаётся backup ZIP в `<save_dir>/backups/`.
- Имя: `YYYYMMDD_HHMMSS_cursorNNNNNN_seq.zip` (seq гарантирует уникальность в пределах секунды).
- Хранится последние `N` (по умолчанию 10). Старые удаляются детерминированно (по имени файла).
- В backup не попадают вложенные `backups/` и временные папки.

### 4) Restore из backup (CLI + UI)

- CLI:
  - `--list-backups` — вывести список доступных бэкапов
  - `--restore-backup <path.zip>` — восстановить конкретный ZIP
  - `--restore-backup-index <k>` — восстановить по индексу из `--list-backups`
- UI:
  - кнопка **“Restore from backup…”** (выбор ZIP, атомарное восстановление, reload state)

### 5) Микро-миграции/нормализация (без изменения механик)

- При load/save добавлена безопасная нормализация:
  - гарантируется наличие `cursor` (для идемпотентности) в `session` или `progress`
  - гарантируется `progress.recent_actions: []`
  - никаких пользовательских полей не удаляется

### 6) Тесты

- `test_autosave_after_dispatch_writes_save`
- `test_autosave_not_called_on_dispatch_error`
- `test_backup_created_and_rolling_limit`
- `test_restore_backup_roundtrip_state_equal`
- `test_failed_apply_does_not_corrupt_existing_save`

## Stage C15 — Error UX hardening (clean exits)

- CLI: любые пользовательские ошибки (missing pack, invalid save, invalid changelog, schema fail) показываются коротко **без traceback**.
- UI: перехват `TclError` и исключений в Tk callback-ах (через `root.report_callback_exception`) — без traceback.
- Полные traceback пишутся **только** в `.wt_logs/traceback.log`.
- Поправлен вывод `--health`: теперь печатает форматированный отчёт `format_health_report(...)` и корректный exit code.

## Stage C17 — Windows-safe saves + IO resilience

- SaveStore: атомарная запись сейва теперь использует **Windows-safe swap директорий**:
  - `dst_root` переименовывается в **уникальный** `swapbak` (без перезаписи фиксированного `.bak`)
  - затем `tmp_root` переименовывается в `dst_root` (когда `dst_root` уже отсутствует)
  - при сбое выполняется best-effort rollback `swapbak -> dst_root`
  - старый `swapbak` удаляется best-effort; при ошибке остаётся для ручного восстановления
- Resilience тесты: добавлены проверки, что сбой посередине swap не портит старый сейв и не оставляет мусорных temp/backup директорий.
- Централизация workflow: UI/CLI используют `save_workflow` для autosave после dispatch и apply master changelog; cursor гарантированно персистится перед записью.

## Stage C18 — Product Save Slot + Restore UX

- UI: добавлен менеджер “слотов сохранения” (без изменения механик):
  - при запуске появляется диалог выбора слота:
    - открыть существующий слот (папка сейва)
    - создать новый слот **из demo template** (копированием `demo/save/*` + `demo/session/*` из datapack)
  - в верхней строке UI показывается активный слот (путь) + cursor + краткий статус
  - кнопка **Change slot…** позволяет переключить слот в процессе работы

- UI: улучшен Restore UX:
  - виджет “Rolling backups” показывает список ZIP‑бэкапов из `<save_dir>/backups/` (новые сверху)
  - восстановление выбранного бэкапа по клику с подтверждением
  - ошибки restore показываются коротко в UI; traceback — только в лог

- CLI: обновлён banner/version string до C18.

## Stage C22 — Schema reconnaissance по db_bundle/RC (интеграционные гарантии)

- Добавлен read-only аудит `core/db_bundle_audit.py`:
  - перечисляет `.sqlite` в pack (приоритет `db_bundle/`)
  - снимает схему таблиц/колонок
  - делает **best-effort** guess “items table” (где есть `item_id` + колонка имени)
  - никаких записей/изменений контента

- `core/item_catalog.py` стал устойчивым к вариациям схемы:
  - больше нет хардкода `FROM items` и обязательных колонок
  - таблица/колонки выбираются через schema-guess
  - если нет name/description/tags/extra — viewer деградирует (показывает `item_id`, пустые поля) без краша

- `validate_pack --health` теперь включает мягкую проверку ItemCatalog (в warnings):
  - показывает какой sqlite выбран для items
  - при проблемах не валит CLI traceback-ом

- CLI: добавлена команда `--db-audit` (печать краткого отчёта по db_bundle).

- Тесты:
  - `test_db_bundle_audit_and_item_catalog_minimal`: минимальный sqlite (item_defs) → schema-guess + viewer работают.
  - RC-интеграции (маркер `rc_pack`):
    - `test_db_bundle_audit_rc_does_not_crash`
    - `test_item_viewer_can_resolve_at_least_one_demo_inventory_item`
