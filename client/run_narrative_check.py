#!/usr/bin/env python3
import json
from pathlib import Path

narratives = json.loads(Path('client/scripts/narratives.json').read_text(encoding='utf-8'))
allowed = {
    'accept-quest': set(narratives.get('archive.accept', [])),
    'open-poi': set(narratives.get('poi.camp.open', [])),
    'submit-quest': set(narratives.get('archive.submit', [])),
}

summary = json.loads(Path('client/_out/smoke_summary.json').read_text(encoding='utf-8'))
errors = []
for step in summary.get('steps', []):
    op = step.get('op')
    if op in allowed:
        n = step.get('narrative')
        if not n:
            errors.append(f'missing narrative for op={op}')
        elif n not in allowed[op]:
            errors.append(f'invalid narrative variant for op={op}')

if errors:
    for e in errors:
        print(f'[ERROR] {e}')
    raise SystemExit(1)

print('[PASS] narrative_check')
