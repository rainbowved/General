#!/usr/bin/env python3
import subprocess

cmd = [
    'python3', 'client/py/game_client.py',
    '--db', 'content/dist/v0.1.0/content.db',
    '--run-script', 'client/scripts/smoke_play.json',
    '--emit-summary', 'client/_out/smoke_summary.json',
    '--compare-golden', 'client/scripts/smoke_expected.json',
]
raise SystemExit(subprocess.call(cmd))
