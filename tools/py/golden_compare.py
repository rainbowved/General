#!/usr/bin/env python3
import json
from pathlib import Path

build_report = json.loads(Path('_logs/build_report.json').read_text(encoding='utf-8'))
gold_report = json.loads(Path('tools/fixtures/golden/build_expected.json').read_text(encoding='utf-8'))
if build_report != gold_report:
    print('[ERROR] golden build report mismatch')
    raise SystemExit(1)
actual_sha = Path('content/dist/v0.1.0/sha256.txt').read_text(encoding='utf-8').strip()
gold_sha = Path('tools/fixtures/golden/content_db_sha256.txt').read_text(encoding='utf-8').strip()
if actual_sha != gold_sha:
    print('[ERROR] golden content db sha mismatch')
    raise SystemExit(1)
print('[PASS] golden_compare')
