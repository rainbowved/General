#!/usr/bin/env python3
import argparse, hashlib, json, os, shutil, sqlite3
from pathlib import Path

PACK_VERSION = "v0.1.0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_seed():
    return json.loads(Path('tools/fixtures/seed/pack_seed.json').read_text(encoding='utf-8'))


def validate_seed_exists(seed):
    req=["tags","items","loot_coffers","loot_pools","loot_pool_rows","coffer_pool_map","recipes","recipe_slots","quests","quest_objective_filter_tags","pois"]
    missing=[k for k in req if k not in seed]
    if missing:
        raise SystemExit(f"missing seed keys: {missing}")


def make_db(seed, db_path: Path):
    schema = Path('content/authoring/schema.sql').read_text(encoding='utf-8')
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    try:
        con.executescript(schema)
        cur = con.cursor()
        for t in seed['tags']:
            cur.execute("INSERT INTO tags(tag_id,namespace,code) VALUES(?,?,?)", (t['tag_id'],t['namespace'],t['code']))
        for i in seed['items']:
            cur.execute("INSERT INTO items(item_id,item_class,name) VALUES(?,?,?)", (i['item_id'],i['item_class'],i['name']))
        for c in seed['loot_coffers']:
            cur.execute("INSERT INTO loot_coffers(coffer_id,name) VALUES(?,?)", (c['coffer_id'],c['name']))
        for p in seed['loot_pools']:
            cur.execute("INSERT INTO loot_pools(pool_id,name) VALUES(?,?)", (p['pool_id'],p['name']))
        for r in sorted(seed['loot_pool_rows'], key=lambda x: (x['pool_id'], x['row_id'])):
            cur.execute("INSERT INTO loot_pool_rows(pool_id,row_id,item_id,weight_bp,qty) VALUES(?,?,?,?,?)", (r['pool_id'],r['row_id'],r['item_id'],r['weight_bp'],r['qty']))
        for m in sorted(seed['coffer_pool_map'], key=lambda x: (x['coffer_id'], x['ordering_key'], x['pool_id'])):
            cur.execute("INSERT INTO coffer_pool_map(coffer_id,pool_id,ordering_key) VALUES(?,?,?)", (m['coffer_id'],m['pool_id'],m['ordering_key']))
        for r in seed['recipes']:
            cur.execute("INSERT INTO recipes(recipe_id,name,time_sec) VALUES(?,?,?)", (r['recipe_id'],r['name'],r['time_sec']))
        for s in sorted(seed['recipe_slots'], key=lambda x: (x['recipe_id'], x['slot_no'])):
            cur.execute("INSERT INTO recipe_slots(recipe_id,slot_no,item_id,qty) VALUES(?,?,?,?)", (s['recipe_id'],s['slot_no'],s['item_id'],s['qty']))
        for q in seed['quests']:
            cur.execute("INSERT INTO quests(quest_id,objective_type,reward_coffer_id) VALUES(?,?,?)", (q['quest_id'],q['objective_type'],q['reward_coffer_id']))
        for qt in sorted(seed['quest_objective_filter_tags'], key=lambda x: (x['quest_id'], x['tag_id'])):
            cur.execute("INSERT INTO quest_objective_filter_tags(quest_id,tag_id) VALUES(?,?)", (qt['quest_id'],qt['tag_id']))
        for p in seed['pois']:
            cur.execute("INSERT INTO pois(poi_id,option_text,loot_coffer_id,open_once) VALUES(?,?,?,?)", (p['poi_id'],p['option_text'],p['loot_coffer_id'],p['open_once']))
        con.commit()
    finally:
        con.close()


def build(out_dir: Path):
    seed = load_seed()
    validate_seed_exists(seed)
    pack_dir = out_dir / PACK_VERSION
    if pack_dir.exists():
        shutil.rmtree(pack_dir)
    pack_dir.mkdir(parents=True, exist_ok=True)

    db_path = pack_dir / 'content.db'
    make_db(seed, db_path)
    db_sha = sha256_file(db_path)

    manifest = {
      'pack_version': PACK_VERSION,
      'content_db': 'content.db',
      'content_db_sha256': db_sha,
      'source_fixture': 'tools/fixtures/seed/pack_seed.json',
    }
    report = {
      'pack_version': PACK_VERSION,
      'generated_ids_count': 0,
      'tables_emitted': ['tags','items','loot_coffers','loot_pools','loot_pool_rows','coffer_pool_map','recipes','recipe_slots','quests','quest_objective_filter_tags','pois'],
      'content_db_sha256': db_sha,
      'row_counts': {
        'tags': len(seed['tags']), 'items': len(seed['items']), 'loot_coffers': len(seed['loot_coffers']),
        'loot_pools': len(seed['loot_pools']), 'loot_pool_rows': len(seed['loot_pool_rows']), 'coffer_pool_map': len(seed['coffer_pool_map']),
        'recipes': len(seed['recipes']), 'recipe_slots': len(seed['recipe_slots']), 'quests': len(seed['quests']),
        'quest_objective_filter_tags': len(seed['quest_objective_filter_tags']), 'pois': len(seed['pois'])
      }
    }
    (pack_dir / 'pack_manifest.json').write_text(canonical_json(manifest)+"\n", encoding='utf-8')
    (pack_dir / 'build_report.json').write_text(canonical_json(report)+"\n", encoding='utf-8')
    (pack_dir / 'sha256.txt').write_text(f"{db_sha}  content.db\n", encoding='utf-8')
    return report, db_sha


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repro', action='store_true')
    ap.add_argument('--emit-report')
    ap.add_argument('--compare-golden')
    args=ap.parse_args()

    out = Path('content/dist')
    rep, sha = build(out)

    if args.emit_report:
        Path(args.emit_report).write_text(json.dumps(rep, indent=2) + "\n", encoding='utf-8')
    if args.compare_golden:
        gold = json.loads(Path(args.compare_golden).read_text(encoding='utf-8'))
        if rep != gold:
            print('[ERROR] build report mismatch golden')
            raise SystemExit(1)

    if args.repro:
        rep2, sha2 = build(out)
        if sha != sha2 or rep != rep2:
            print('[ERROR] reproducible build failed')
            raise SystemExit(1)
        print('[PASS] repro_build')
    else:
        print('[PASS] build_pack')


if __name__=='__main__':
    main()
