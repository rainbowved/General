#!/usr/bin/env python3
import argparse, json, hashlib
from pathlib import Path


def validate(data):
    errors=[]
    tags={t['tag_id']:t for t in data.get('tags',[])}
    items={i['item_id']:i for i in data.get('items',[])}
    coffers={c['coffer_id']:c for c in data.get('loot_coffers',[])}
    pools={p['pool_id']:p for p in data.get('loot_pools',[])}

    # B24 mapping + refs + stable row uniqueness
    if not data.get('coffer_pool_map'):
        errors.append('R-B24-001:missing coffer_pool_map')
    seen_rows=set()
    for r in data.get('loot_pool_rows',[]):
        key=(r['pool_id'],r['row_id'])
        if key in seen_rows: errors.append('R-B24-002:duplicate pool row')
        seen_rows.add(key)
        if r['item_id'] not in items: errors.append('R-B24-003:unknown item ref')
        if r['pool_id'] not in pools: errors.append('R-B24-004:unknown pool ref')

    # B21 recipe strict
    for rec in data.get('recipes',[]):
        if rec['time_sec'] not in (30,60,120): errors.append('R-B21-001:invalid time_sec')
        slots=[s for s in data.get('recipe_slots',[]) if s['recipe_id']==rec['recipe_id']]
        if len(slots)!=3: errors.append('R-B21-002:recipe must have 3 slots')

    # B18 quests
    for q in data.get('quests',[]):
        if q['objective_type']!='DELIVER': errors.append('R-B18-001:objective must DELIVER')
        if q['reward_coffer_id'] not in coffers: errors.append('R-B18-002:reward coffer missing')
        f=[x for x in data.get('quest_objective_filter_tags',[]) if x['quest_id']==q['quest_id']]
        if not f: errors.append('R-B18-003:missing filter tags')

    # B20 poi
    for p in data.get('pois',[]):
        if not p.get('loot_coffer_id'): errors.append('R-B20-001:poi requires loot_coffer_id')

    # B22 luck
    for x in data.get('luck_bonus_pool',[]):
        if x.get('item_class') in {'weapon','armor','equip'}:
            errors.append('R-B22-001:forbidden luck item_class')

    # B03 tags
    for t in tags.values():
        if t['namespace'] not in {'food','quest','poi','loot'}:
            errors.append('R-B03-001:invalid namespace')
    return errors


def report_for(path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    errors=validate(data)
    return {
      'fixture': str(path),
      'ok': len(errors)==0,
      'error_count': len(errors),
      'errors': errors,
      'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed', action='store_true')
    ap.add_argument('--neg', action='store_true')
    ap.add_argument('--emit-report')
    ap.add_argument('--compare-golden')
    args=ap.parse_args()

    if args.seed:
        rep=report_for('tools/fixtures/seed/pack_seed.json')
        if args.emit_report: Path(args.emit_report).write_text(json.dumps(rep,indent=2),encoding='utf-8')
        if args.compare_golden:
            gold=json.loads(Path(args.compare_golden).read_text(encoding='utf-8'))
            if rep!=gold: print('[ERROR] validate report mismatch golden'); raise SystemExit(1)
        if not rep['ok']: print('\n'.join(rep['errors'])); raise SystemExit(1)
        print('[PASS] validate_seed')
        return

    if args.neg:
        reports=[]
        failed=0
        for p in sorted(Path('tools/fixtures/validate_neg').glob('*.json')):
            rep=report_for(p)
            reports.append(rep)
            if rep['ok']:
                print(f'[ERROR] expected fail but passed: {p.name}')
                failed+=1
            else:
                print(f'[PASS] neg fixture failed as expected: {p.name} ({rep["error_count"]} errors)')
        if args.emit_report: Path(args.emit_report).write_text(json.dumps(reports,indent=2),encoding='utf-8')
        if failed: raise SystemExit(1)
        print('[PASS] validate_neg')
        return

    raise SystemExit('use --seed or --neg')

if __name__=='__main__':
    main()
