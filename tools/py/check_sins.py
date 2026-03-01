#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path

TEXT_EXT = {'.py', '.sh', '.ps1', '.sql', '.json', '.md', '.cs', '.yml', '.yaml', '.txt'}
EXCLUDE_DIRS = {'.git', '_out', '__pycache__', '.venv'}
EXCLUDE_FILES = {'tools/py/check_sins.py', 'docs/SINS_REPORT.md'}
EXCLUDE_PATH_PREFIXES = {
    '_logs/',
    'client/_out/',
    'content/dist/',
}

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


def rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        kept_dirs = []
        for d in dirnames:
            if d in EXCLUDE_DIRS:
                continue
            rel_dir = rel_posix(current / d, root)
            if any(rel_dir.startswith(prefix) for prefix in EXCLUDE_PATH_PREFIXES):
                continue
            kept_dirs.append(d)
        dirnames[:] = kept_dirs
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() not in TEXT_EXT:
                continue
            rel = rel_posix(p, root)
            if any(rel.startswith(prefix) for prefix in EXCLUDE_PATH_PREFIXES):
                continue
            if rel in EXCLUDE_FILES or rel.startswith('tools/src/CheckSins/'):
                continue
            yield p


def is_canonical_path(rel_path: str) -> bool:
    return any(rel_path.startswith(h) for h in CANONICAL_PATH_HINTS)


def scan_file(p: Path, root: Path):
    findings = []
    rel = rel_posix(p, root)
    text = p.read_text(encoding='utf-8', errors='ignore')
    for i, line in enumerate(text.splitlines(), start=1):
        l = line.strip()
        if not l:
            continue

        for pat in SECRET_PATTERNS:
            if pat.search(line) and 're.compile(' not in line:
                findings.append((rel, i, 'SECRET', line.strip()))

        for pat in ENTROPY_PATTERNS:
            if pat.search(line):
                findings.append((rel, i, 'ENTROPY', line.strip()))

        for pat in NETWORK_PATTERNS:
            if pat.search(line):
                findings.append((rel, i, 'NETWORK', line.strip()))

        if is_canonical_path(rel):
            lower = l.lower()
            if p.suffix.lower() in {'.py', '.cs', '.sql', '.sh', '.ps1'}:
                if 'float' in lower:
                    if not lower.startswith('#') and 'no float' not in lower and 'без float' not in lower:
                        findings.append((rel, i, 'FLOAT', line.strip()))

        if 'PHASE 7 DONE' in line:
            status = root / 'docs/PHASE_STATUS.md'
            has_refs = status.exists() and 'VERIFY_LOG' in status.read_text(encoding='utf-8', errors='ignore')
            if not has_refs:
                findings.append((rel, i, 'PHASE_DONE_CLAIM', line.strip()))

    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--report', default='docs/SINS_REPORT.md')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    files = list(iter_files(root))

    all_findings = []
    for p in files:
        all_findings.extend(scan_file(p, root))

    report = (root / args.report).resolve() if not Path(args.report).is_absolute() else Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# SINS_REPORT',
        '',
        '- scanned_root: `.`',
        f'- files_scanned: {len(files)}',
        f'- findings_count: {len(all_findings)}',
        '',
        '## Findings',
    ]
    if not all_findings:
        lines.append('- none')
    else:
        for rel, ln, kind, excerpt in all_findings:
            lines.append(f'- [{kind}] `{rel}:{ln}` — `{excerpt}`')

    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    if all_findings:
        print(f'[FAIL] check_sins findings={len(all_findings)}')
        raise SystemExit(1)
    print('[PASS] check_sins')


if __name__ == '__main__':
    main()
