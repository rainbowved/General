#!/usr/bin/env python3
from pathlib import Path
text=Path('docs/COVERAGE_REPORT.md').read_text(encoding='utf-8')
if '- gate_pass: true' in text:
    print('[PASS] coverage_gate')
else:
    print('[ERROR] coverage_gate failed')
    raise SystemExit(1)
