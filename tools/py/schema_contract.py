#!/usr/bin/env python3
import argparse
import json
import fnmatch
import sqlite3
from pathlib import Path


def load_contract(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def create_db(db_path: Path, schema_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
      db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        con.executescript(schema_path.read_text(encoding="utf-8"))
        con.commit()
    finally:
        con.close()


def actual_schema(con):
    rows = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    schema = {}
    for (table,) in rows:
        cols = con.execute(f"PRAGMA table_info({table})").fetchall()
        schema[table] = [f"{c[1]}:{(c[2] or '').upper()}" for c in cols]
    return schema


def check_contract(db_path: Path, contract_path: Path):
    contract = load_contract(contract_path)
    con = sqlite3.connect(db_path)
    try:
        schema = actual_schema(con)
    finally:
        con.close()

    errors = []
    expected_tables = contract.get("tables", {})
    for table, expected_cols in expected_tables.items():
        if table not in schema:
            errors.append(f"MISSING_TABLE:{table}")
            continue
        actual_cols = schema[table]
        for col in expected_cols:
            if col not in actual_cols:
                errors.append(f"MISSING_COLUMN:{table}.{col}")

    forbidden_types = set(contract.get("forbidden_types", []))
    patterns = contract.get("forbidden_column_name_patterns", [])
    for table, cols in schema.items():
        for col in cols:
            name, typ = col.split(":", 1)
            if typ in forbidden_types:
                errors.append(f"FORBIDDEN_TYPE:{table}.{name}:{typ}")
            for p in patterns:
                if fnmatch.fnmatch(name, p):
                    errors.append(f"FORBIDDEN_COLUMN_PATTERN:{table}.{name}:{p}")

    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--schema")
    ap.add_argument("--contract", required=True)
    ap.add_argument("--create-db", action="store_true")
    args = ap.parse_args()

    db = Path(args.db)
    contract = Path(args.contract)
    if args.create_db:
        if not args.schema:
            raise SystemExit("--schema required with --create-db")
        create_db(db, Path(args.schema))

    errs = check_contract(db, contract)
    if errs:
        for e in errs:
            print(f"[ERROR] {e}")
        raise SystemExit(1)
    print("[PASS] schema_contract")


if __name__ == "__main__":
    main()
