#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

VALID_CI_LEVELS = {'probe', 'full'}


def parse_ci_level() -> str:
    value = os.getenv('CI_LEVEL', 'probe').strip().lower()
    if value not in VALID_CI_LEVELS:
        raise SystemExit(f"[ERROR] CI_LEVEL must be one of {sorted(VALID_CI_LEVELS)}, got: {value!r}")
    return value


def parse_phase_target() -> int:
    raw = os.getenv('PHASE_TARGET', '0').strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise SystemExit(f"[ERROR] PHASE_TARGET must be an integer, got: {raw!r}") from exc
    if value < 0:
        raise SystemExit(f"[ERROR] PHASE_TARGET must be >= 0, got: {value}")
    return value


CI_LEVEL = parse_ci_level()
PHASE_TARGET = parse_phase_target()

LOGS = Path('_logs')
LOGS.mkdir(parents=True, exist_ok=True)
CI_LOG = LOGS / 'ci.log'


def w(line: str):
    print(line)
    with CI_LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def step_status(step: str, status: str):
    w(f'[STATUS] {step} = {status}')
    (LOGS / f'{step}.status').write_text(status, encoding='utf-8')


def require_if(required: int, step: str):
    if required == 1 and CI_LEVEL == 'full':
        p = LOGS / f'{step}.status'
        if not p.exists():
            raise SystemExit(f'[ERROR] Missing status file for {step}')
        st = p.read_text(encoding='utf-8').strip()
        if st in {'SKIPPED', 'UNVERIFIED', 'MISSING'}:
            raise SystemExit(f'[ERROR] Required step {step} is {st} (PHASE_TARGET={PHASE_TARGET})')


def run_step(step: str, cmd: str):
    log = LOGS / f'{step}.log'
    w('')
    w(f'[STEP] {step}')
    w(f'[CMD]  {cmd}')
    with log.open('w', encoding='utf-8') as lf:
        proc = subprocess.run(cmd, shell=True, stdout=lf, stderr=subprocess.STDOUT)
    if proc.returncode == 0:
        step_status(step, 'OK')
        return

    step_status(step, 'ERROR')
    w(f'[ERROR] Step {step} failed. See {log}')
    try:
        lines = log.read_text(encoding='utf-8', errors='ignore').splitlines()
    except OSError:
        lines = []
    if lines:
        tail = lines[-40:]
        w(f'[ERROR] Last {len(tail)} line(s) from {log}:')
        for line in tail:
            w(f'  {line}')
    raise SystemExit(2)


def has(path: str) -> bool:
    return Path(path).exists()


def main():
    CI_LOG.write_text('', encoding='utf-8')
    w('== CI v3.7 ==')
    w(f'CI_LEVEL={CI_LEVEL} PHASE_TARGET={PHASE_TARGET}')

    req = {
        'check_sins': 1,
        'schema': 1 if PHASE_TARGET >= 1 else 0,
        'coverage': 1,
        'validate': 1 if PHASE_TARGET >= 2 else 0,
        'build': 1 if PHASE_TARGET >= 3 else 0,
        'client': 1 if PHASE_TARGET >= 5 else 0,
        'det': 1 if PHASE_TARGET >= 6 else 0,
        'golden': 1 if PHASE_TARGET >= 5 else 0,
        'coverage_gate': 1 if PHASE_TARGET >= 2 else 0,
        'narrative': 1 if PHASE_TARGET >= 7 else 0,
    }
    if PHASE_TARGET >= 6:
        req['golden'] = 1

    w("-- Required steps: schema={schema} validate={validate} build={build} client={client} det={det} golden={golden} coverage_gate={coverage_gate} narrative={narrative}".format(**req))

    # check_sins
    if has('tools/py/check_sins.py'):
        run_step('check_sins', 'python3 tools/py/check_sins.py --report docs/SINS_REPORT.md')
    elif has('tools/check_sins.sh'):
        run_step('check_sins', 'bash tools/check_sins.sh')
    else:
        w('[STEP] check_sins')
        w('[WARN] check_sins tool missing')
        step_status('check_sins', 'MISSING')
    require_if(req['check_sins'], 'check_sins')

    # schema
    if has('tools/schema_contract.sh'):
        run_step('schema_contract', 'bash tools/schema_contract.sh')
    elif has('tools/py/schema_contract.py'):
        run_step('schema_contract', 'python3 tools/py/schema_contract.py --db _out/authoring.db --schema content/authoring/schema.sql --contract docs/schema_contracts/authoring_schema_contract.json --create-db')
    else:
        w('[STEP] schema_contract')
        w('[WARN] schema contract tool missing')
        step_status('schema_contract', 'SKIPPED')
    require_if(req['schema'], 'schema_contract')

    # coverage
    if has('tools/coverage_report.sh'):
        run_step('coverage', 'bash tools/coverage_report.sh')
    elif has('tools/py/coverage_report.py'):
        run_step('coverage', 'python3 tools/py/coverage_report.py')
    else:
        w('[STEP] coverage')
        w('[WARN] coverage tool missing')
        step_status('coverage', 'SKIPPED')
    require_if(req['coverage'], 'coverage')

    # validate
    if has('tools/validate_pack.sh'):
        run_step('validate_seed', 'bash tools/validate_pack.sh --seed')
        run_step('validate_neg', 'bash tools/validate_pack.sh --neg')
    elif has('tools/py/validate_pack.py'):
        run_step('validate_seed', 'python3 tools/py/validate_pack.py --seed')
        run_step('validate_neg', 'python3 tools/py/validate_pack.py --neg')
    else:
        w('[STEP] validate_seed/validate_neg')
        w('[WARN] validate tool missing')
        step_status('validate_seed', 'SKIPPED')
        step_status('validate_neg', 'SKIPPED')
    require_if(req['validate'], 'validate_seed')
    require_if(req['validate'], 'validate_neg')

    # build
    if has('tools/build_pack.sh'):
        run_step('build', 'bash tools/build_pack.sh')
        run_step('repro_build', 'bash tools/build_pack.sh --repro')
    elif has('tools/py/build_pack.py'):
        run_step('build', 'python3 tools/py/build_pack.py')
        run_step('repro_build', 'python3 tools/py/build_pack.py --repro')
    else:
        w('[STEP] build/repro_build')
        w('[WARN] build tool missing')
        step_status('build', 'SKIPPED')
        step_status('repro_build', 'SKIPPED')
    require_if(req['build'], 'build')
    require_if(req['build'], 'repro_build')

    # golden compare
    if has('tools/golden_compare.sh'):
        run_step('golden_compare', 'bash tools/golden_compare.sh')
    elif has('tools/py/golden_compare.py'):
        run_step('golden_compare', 'python3 tools/py/golden_compare.py')
    else:
        step_status('golden_compare', 'SKIPPED')
    require_if(req['golden'], 'golden_compare')

    # client smoke
    if has('client/run_smoke.sh'):
        run_step('client_smoke', 'bash client/run_smoke.sh')
    elif has('client/run_smoke.py'):
        run_step('client_smoke', 'python3 client/run_smoke.py')
    else:
        step_status('client_smoke', 'SKIPPED')
    require_if(req['client'], 'client_smoke')

    # determinism
    if has('client/run_determinism.sh'):
        run_step('determinism', 'bash client/run_determinism.sh')
    elif has('client/run_determinism.py'):
        run_step('determinism', 'python3 client/run_determinism.py')
    else:
        step_status('determinism', 'SKIPPED')
    require_if(req['det'], 'determinism')

    # narrative
    if has('client/run_narrative_check.sh'):
        run_step('narrative_check', 'bash client/run_narrative_check.sh')
    elif has('client/run_narrative_check.py'):
        run_step('narrative_check', 'python3 client/run_narrative_check.py')
    else:
        step_status('narrative_check', 'SKIPPED')
    require_if(req['narrative'], 'narrative_check')

    # coverage gate
    if has('tools/coverage_gate.sh'):
        run_step('coverage_gate', 'bash tools/coverage_gate.sh')
    elif has('tools/py/coverage_gate.py'):
        run_step('coverage_gate', 'python3 tools/py/coverage_gate.py')
    else:
        step_status('coverage_gate', 'SKIPPED')
    require_if(req['coverage_gate'], 'coverage_gate')

    w('')
    w('== CI done ==')


if __name__ == '__main__':
    main()
