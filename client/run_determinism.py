#!/usr/bin/env python3
import json, subprocess
from pathlib import Path

base = [
    'python3', 'client/py/game_client.py',
    '--db', 'content/dist/v0.1.0/content.db',
    '--run-script', 'client/scripts/golden_trace.json',
]

subprocess.check_call(base + ['--emit-summary', 'client/_out/determinism_run1.json'])
subprocess.check_call(base + ['--emit-summary', 'client/_out/determinism_run2.json'])

r1 = json.loads(Path('client/_out/determinism_run1.json').read_text(encoding='utf-8'))
r2 = json.loads(Path('client/_out/determinism_run2.json').read_text(encoding='utf-8'))
if r1 != r2:
    print('[ERROR] determinism mismatch between run1 and run2')
    raise SystemExit(1)

expected = Path('client/scripts/golden_trace_expected_hash.txt').read_text(encoding='utf-8').strip()
if r1.get('state_hash') != expected:
    print('[ERROR] golden trace hash mismatch')
    raise SystemExit(1)

report = {
    'state_hash': r1['state_hash'],
    'runs_equal': True,
    'expected_hash': expected,
    'commands_total': r1.get('commands_total', 0)
}
Path('client/_out/determinism_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('[PASS] determinism')
