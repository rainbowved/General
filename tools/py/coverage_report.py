#!/usr/bin/env python3
import re
from pathlib import Path

ledger=Path('docs/EVIDENCE_LEDGER.md').read_text(encoding='utf-8').splitlines()
gaps=Path('docs/GAPS_DECISIONS.md').read_text(encoding='utf-8') if Path('docs/GAPS_DECISIONS.md').exists() else ''

rows=[]
for ln in ledger:
    if ln.startswith('| ') and '---' not in ln and 'rule_id' not in ln:
        parts=[p.strip() for p in ln.strip('|').split('|')]
        if len(parts)>=7: rows.append(parts)

total=len(rows)
without_anchor=sum(1 for r in rows if not r[1] or r[1]=='[ASSUMPTION]')
anchor_counts={k:0 for k in ['B24','B21','B18','B20','B22']}
for r in rows:
    for a in anchor_counts:
        if str(r[1]).startswith(a): anchor_counts[a]+=1
assumptions=len(re.findall(r'^### A-',gaps,flags=re.M))
conflicts=len(re.findall(r'\[CONFLICT\]',gaps))
unmet=[]
if total<30: unmet.append('total_rules<30')
if without_anchor!=0: unmet.append('rules_without_anchor!=0')
if assumptions>20: unmet.append('assumptions_count>20')
for a,c in anchor_counts.items():
    if c<1: unmet.append(f'anchor_{a}_missing')

gate_pass= len(unmet)==0
lines=[
'# COVERAGE_REPORT.md (GENERATED)',
'> Генерируется tools/coverage_report. Ручные правки запрещены.',
'',
'## Summary',
f'- total_rules: {total}',
f'- rules_without_anchor: {without_anchor}',
f'- assumptions_count: {assumptions}',
f'- conflicts_count: {conflicts}',
'',
'## Coverage by Anchor (Bxx)',
'| anchor | rule_count |','|---|---|',
]
for a,c in anchor_counts.items(): lines.append(f'| {a} | {c} |')
lines += ['', '## Gate', f'- gate_pass: {str(gate_pass).lower()}', f"- unmet_requirements: {', '.join(unmet) if unmet else 'none'}"]
Path('docs/COVERAGE_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('[PASS] coverage_report' if gate_pass else '[WARN] coverage_report generated with unmet requirements')
