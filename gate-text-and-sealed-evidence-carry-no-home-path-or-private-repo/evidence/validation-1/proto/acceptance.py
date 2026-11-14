"""Three observable acceptance steps; all machine paths are caller arguments."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

p = argparse.ArgumentParser()
p.add_argument('candidate', type=Path)
p.add_argument('scratch', type=Path)
p.add_argument('spacedock', type=Path)
a = p.parse_args()
code, scratch, sd = [v.expanduser().resolve() for v in (a.candidate,a.scratch,a.spacedock)]
scratch.mkdir(parents=True,exist_ok=True)
base = Path(tempfile.mkdtemp(prefix='acceptance-',dir=scratch))
runs = base/'runs'
runs.mkdir()
expected = 'd8ce3421219a8ff6112628de7cbf5f46274c634a'
head = subprocess.check_output(['git','-C',str(code),'rev-parse','HEAD'],text=True).strip()
print('Step 1: candidate identity: '+head,flush=True)
if head != expected:
    sys.exit('Candidate differs from the assigned validation head.')
print('Step 2: clean gate, refused sealed evidence, recorded recovery, fresh shells: expect exit 0',flush=True)
gate = subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('gate_probe.py')),
                       str(code),str(base/'gate'),str(runs),str(sd)],capture_output=True,text=True)
(runs/'gate.log').write_text(gate.stdout+gate.stderr)
print('Step 2 exit: '+str(gate.returncode),flush=True)
print('Step 3: adversarial gzip members: expect all private identifiers refused',flush=True)
attack = subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('gzip_probe.py')),
                         str(code),str(base/'gzip'),str(runs)],capture_output=True,text=True)
(runs/'gzip.log').write_text(attack.stdout+attack.stderr)
print('Step 3 exit: '+str(attack.returncode),flush=True)
if (runs/'gzip-probe.json').is_file():
    cases = json.loads((runs/'gzip-probe.json').read_text())
    print('Unexpected acceptance: '+', '.join(x['name'] for x in cases if not x['passed']),flush=True)
print('Evidence retained under caller scratch: '+base.name,flush=True)
print('Limit: no live install, hosted review, state replay, or future rollout is proved.',flush=True)
sys.exit(int(bool(gate.returncode or attack.returncode)))
