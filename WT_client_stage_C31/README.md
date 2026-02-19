# WT Client — Stages C0–C10 (ActionDispatcher + Vertical Slice UI)

Минимальный, но правильный каркас клиента для WT (RPG). Пока без игровых механик: инфраструктура + smoke/health проверки datapack.

## Структура

```
wt_client/
  core/    # логика (конфиг, логирование, smoke)
  ui/      # минимальный Tkinter UI (C9)
  tests/   # pytest
  tools/   # утилиты/скрипты (в следующих стадиях)
```

## Быстрый старт

1) Создай виртуальное окружение и установи зависимости для тестов:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Запусти demo-smoke (использует `wt_client/config.json`, если он есть, иначе fallback):

```bash
python -m wt_client --demo
```

3) Проверка конкретного ZIP:

```bash
python -m wt_client --pack /path/to/WT_data_release_candidate.zip
```

4) Health-валидатор (ZIP или распакованная папка):

```bash
python -m wt_client --pack /path/to/WT_data_release_candidate.zip --health
```

5) Сборка и экспорт TURNPACK по demo (save + changelog) с JSON Schema validation:

```bash
python -m wt_client --demo --export-turnpack out.json

# (C10) Выполнение действия + экспорт TURNPACK (action_request как JSON строка или путь к файлу)
python -m wt_client --demo --act '{"type":"move","to_node_id":"<NODE_ID>"}' --export-turnpack out.json

python -m wt_client --demo --act action.json --export-turnpack out.json
```

6) Минимальный UI (вертикальный срез):

```bash
python -m wt_client --ui
```

UI делает цикл: Load → Apply demo changelog → Move/Perform action → Export TURNPACK.

## Конфиг

`wt_client/config.json`:

- `datapack_path` — путь к datapack ZIP
- `save_root` — корень для сейвов (пока не используется)
- `logs_dir` — каталог логов

## Smoke vs Health

- Открывает ZIP
- Проверяет наличие top-level каталогов: `concept/`, `db_bundle/`, `specs/`, `demo/`
- Печатает короткий отчёт и пишет лог в файл + stdout

Health (`--health`) делает больше (минимальный аудит "на входе"):

- умеет грузить datapack как ZIP **или** как распакованную папку
- детектит "обёрнутый" корень (когда внутри ZIP один верхний каталог)
- проверяет required пути (concept/specs/demo/db_bundle)
- парсит все `specs/*.json` и отдельно проверяет `turnpack_schema.json` и `rng_streams.json`

## Stage C34-C37 quick commands

- Health datapack: `python -m wt_client --pack <path> --health-datapack`
- Health dbbundle: `python -m wt_client --pack <path_or_db_bundle> --health-dbbundle`
- Save migration: `python -m wt_client --migrate-save --in old.json --out new.json`
- Golden demo generate: `PYTHONPATH=. python -m wt_client.tools.golden_demo generate --pack <path>`
- Golden demo verify: `PYTHONPATH=. python -m wt_client.tools.golden_demo verify --pack <path>`
- Run 10 turns replay: `PYTHONPATH=. python tools/run_10_turns.py`
- Build clean stage zip: `python scripts/make_stage_zip.py --out stage_clean.zip --manifest manifest.json`
