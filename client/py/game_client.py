#!/usr/bin/env python3
import argparse, hashlib, json, sqlite3
from pathlib import Path


def keyed_roll(key: str, n: int) -> int:
    h = hashlib.sha256(key.encode('utf-8')).digest()
    v = int.from_bytes(h[:8], 'big')
    return v % n


def load_db(db_path: str):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def load_narratives(path='client/scripts/narratives.json'):
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding='utf-8'))


def pick_narrative(narratives, key: str, scope_event_id: str):
    variants = narratives.get(key, [])
    if not variants:
        return None
    idx = keyed_roll(f"{scope_event_id}|{key}", len(variants))
    return variants[idx]


def open_loot(con, coffer_id: str, event_id: str):
    rows = con.execute(
        """
        SELECT lpr.item_id, lpr.qty
        FROM coffer_pool_map cpm
        JOIN loot_pool_rows lpr ON lpr.pool_id = cpm.pool_id
        WHERE cpm.coffer_id = ?
        ORDER BY cpm.ordering_key, lpr.row_id
        """,
        (coffer_id,),
    ).fetchall()
    if not rows:
        raise RuntimeError(f"coffer has no rows: {coffer_id}")
    idx = keyed_roll(f"{event_id}|{coffer_id}", len(rows))
    r = rows[idx]
    return {"item_id": r["item_id"], "qty": int(r["qty"]), "source": "LOOT_OPEN"}


def run_script(db_path: str, script_path: str):
    script = json.loads(Path(script_path).read_text(encoding='utf-8'))
    con = load_db(db_path)
    try:
        inv = {}
        quests = set()
        opened_poi = set()
        grants = []
        steps = []
        narratives = load_narratives()
        for i, cmd in enumerate(script.get('commands', []), start=1):
            op = cmd['op']
            if op == 'new-run':
                steps.append({'step': i, 'op': op, 'ok': True})
            elif op == 'accept-quest':
                quests.add(cmd['quest_id'])
                narrative = pick_narrative(narratives, 'archive.accept', f"{script.get('run_id','run')}|{i}|accept")
                steps.append({'step': i, 'op': op, 'quest_id': cmd['quest_id'], 'narrative': narrative, 'ok': True})
            elif op == 'open-poi':
                poi_id = cmd['poi_id']
                poi = con.execute("SELECT poi_id, loot_coffer_id, open_once FROM pois WHERE poi_id=?", (poi_id,)).fetchone()
                if poi is None:
                    raise RuntimeError(f'unknown poi {poi_id}')
                if int(poi['open_once']) == 1 and poi_id in opened_poi:
                    raise RuntimeError('poi already opened once')
                opened_poi.add(poi_id)
                grant = open_loot(con, poi['loot_coffer_id'], f"{script.get('run_id','run')}|{i}")
                # strict runtime assert: item grants only via LOOT_OPEN
                if grant.get('source') != 'LOOT_OPEN':
                    raise RuntimeError('item grant source violation')
                inv[grant['item_id']] = inv.get(grant['item_id'], 0) + grant['qty']
                grants.append(grant)
                narrative = pick_narrative(narratives, 'poi.camp.open', f"{script.get('run_id','run')}|{i}")
                steps.append({'step': i, 'op': op, 'poi_id': poi_id, 'grant': grant, 'narrative': narrative, 'ok': True})
            elif op == 'submit-quest':
                qid = cmd['quest_id']
                if qid not in quests:
                    raise RuntimeError(f'quest not accepted {qid}')
                q = con.execute('SELECT reward_coffer_id FROM quests WHERE quest_id=?', (qid,)).fetchone()
                if q is None:
                    raise RuntimeError(f'unknown quest {qid}')
                reward = open_loot(con, q['reward_coffer_id'], f"{script.get('run_id','run')}|{i}|quest")
                if reward.get('source') != 'LOOT_OPEN':
                    raise RuntimeError('item grant source violation')
                inv[reward['item_id']] = inv.get(reward['item_id'], 0) + reward['qty']
                grants.append(reward)
                narrative = pick_narrative(narratives, 'archive.submit', f"{script.get('run_id','run')}|{i}|quest")
                steps.append({'step': i, 'op': op, 'quest_id': qid, 'grant': reward, 'narrative': narrative, 'ok': True})
            elif op == 'show-inventory':
                steps.append({'step': i, 'op': op, 'inventory': dict(sorted(inv.items())), 'ok': True})
            else:
                raise RuntimeError(f'unsupported op {op}')

        summary = {
            'run_id': script.get('run_id', 'run'),
            'commands_total': len(script.get('commands', [])),
            'inventory': dict(sorted(inv.items())),
            'grants': grants,
            'steps': steps,
        }
        norm = json.dumps(summary, sort_keys=True, separators=(',', ':'))
        summary['state_hash'] = hashlib.sha256(norm.encode('utf-8')).hexdigest()
        return summary
    finally:
        con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    ap.add_argument('--run-script', required=True)
    ap.add_argument('--emit-summary')
    ap.add_argument('--compare-golden')
    args = ap.parse_args()

    summary = run_script(args.db, args.run_script)
    if args.emit_summary:
        Path(args.emit_summary).write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    if args.compare_golden:
        g = json.loads(Path(args.compare_golden).read_text(encoding='utf-8'))
        if summary != g:
            print('[ERROR] client smoke summary mismatch golden')
            raise SystemExit(1)
    print('[PASS] client_smoke')


if __name__ == '__main__':
    main()
