import concurrent.futures, json, subprocess, sys
from pathlib import Path
out = Path(__file__).resolve().parent
def run(row):
    cmd = [sys.executable, '-B', str(out / 'candidate/kc-dev-flow-2/scripts/laws_check.py'), row['state'], '--before', row['before'], '--after', row['after'], '--readme', row['readme']]
    with (out / ('corpus-' + row['name'] + '.log')).open('w') as log:
        result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    (out / ('corpus-' + row['name'] + '-exit.json')).write_text(json.dumps({**row, 'argv': cmd, 'exit': result.returncode}, indent=2) + '\n')
    print(row['name'], 'exit', result.returncode, flush=True)
    return result.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(run, json.loads((out / 'corpus-inputs.json').read_text())))
assert all(code in (0,1,2) for code in results)
