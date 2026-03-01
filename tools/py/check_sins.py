#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path

TEXT_EXT = {'.py', '.sh', '.ps1', '.sql', '.json', '.md', '.cs', '.yml', '.yaml', '.txt'}
EXCLUDE_DIRS = {'.git', '_out', '__pycache__', '.venv'}
EXCLUDE_FILES = {'tools/py/check_sins.py', 'docs/SINS_REPORT.md'}

CANONICAL_PATH_HINTS = (
    'client/',
    'tools/',
    'content/',
)

SECRET_PATTERNS = [
    re.compile(r'ghp_[A-Za-z0-9]{20,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),
    re.compile(r'xoxb-[A-Za-z0-9-]{20,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'BEGIN PRIVATE KEY'),
]

ENTROPY_PATTERNS = [
    re.compile(r'\brandom\.'),
    re.compile(r'\bRandom\('),
    re.compile(r'datetime\.now', re.IGNORECASE),
    re.compile(r'time\.time\('),
    re.compile(r'perf_counter\('),
]

NETWORK_PATTERNS = [
    re.compile(r'\brequests\.'),
    re.compile(r'\burllib\.'),
    re.compile(r'\bcurl\b'),
    re.compile(r'\bwget\b'),
]


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            ps = p.as_posix()
            if ps in EXCLUDE_FILES or ps.startswith('tools/src/CheckSins/'):
                continue
            if p.suffix.lower() in TEXT_EXT:
                yield p


def is_canonical_path(p: Path) -> bool:
    s = p.as_posix()
    return any(h in s for h in CANONICAL_PATH_HINTS)


def scan_file(p: Path):
    findings = []
    text = p.read_text(encoding='utf-8', errors='ignore')
    for i, line in enumerate(text.splitlines(), start=1):
        l = line.strip()
        if not l:
            continue

        for pat in SECRET_PATTERNS:
            if pat.search(line) and 're.compile(' not in line:
                findings.append((p, i, 'SECRET', line.strip()))

        for pat in ENTROPY_PATTERNS:
            if pat.search(line):
                findings.append((p, i, 'ENTROPY', line.strip()))

        for pat in NETWORK_PATTERNS:
            if pat.search(line):
                findings.append((p, i, 'NETWORK', line.strip()))

        if is_canonical_path(p):
            lower = l.lower()
            if p.suffix.lower() in {'.py', '.cs', '.sql', '.sh', '.ps1'}:
                if 'float' in lower:
                    if not lower.startswith('#') and 'no float' not in lower and 'без float' not in lower:
                        findings.append((p, i, 'FLOAT', line.strip()))

        if 'PHASE 7 DONE' in line:
            status = Path('docs/PHASE_STATUS.md')
            has_refs = status.exists() and 'VERIFY_LOG' in status.read_text(encoding='utf-8', errors='ignore')
            if not has_refs:
                findings.append((p, i, 'PHASE_DONE_CLAIM', line.strip()))

    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--report', default='docs/SINS_REPORT.md')
    args = ap.parse_args()

    all_findings = []
    for p in iter_files(Path(args.root)):
        all_findings.extend(scan_file(p))

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# SINS_REPORT',
        '',
        f'- scanned_root: `{Path(args.root).resolve()}`',
        f'- files_scanned: {sum(1 for _ in iter_files(Path(args.root)))}',
        f'- findings_count: {len(all_findings)}',
        '',
        '## Findings',
    ]
    if not all_findings:
        lines.append('- none')
    else:
        for p, ln, kind, excerpt in all_findings:
            lines.append(f'- [{kind}] `{p.as_posix()}:{ln}` — `{excerpt}`')

    Path(args.report).write_text('\n'.join(lines) + '\n', encoding='utf-8')

    if all_findings:
        print(f'[FAIL] check_sins findings={len(all_findings)}')
        raise SystemExit(1)
    print('[PASS] check_sins')


if __name__ == '__main__':
    main()
