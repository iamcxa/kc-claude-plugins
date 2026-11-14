"""Seal two acceptance scripts with main's scratch.evidence (home rewritten to ~), then run each from a fresh shell. Exit codes only."""
import json, subprocess, sys
from pathlib import Path
pkg = Path(sys.argv[1]); sys.path.insert(0, str(pkg)); import scratch
home = Path.home(); state = home / 'ws/state'; task = state / 'tw-script'; ev = task / 'evidence/validation-1'; ev.mkdir(parents=True)
repo = home / 'ws/repo'
(ev / 'literal.py').write_text(f'import pathlib\nassert pathlib.Path("{repo}").is_dir()\nprint("1 PASS")\n')
(ev / 'argument.py').write_text('import pathlib, sys\nassert pathlib.Path(sys.argv[1]).is_dir()\nprint("1 PASS")\n')
seal = scratch.evidence(task, 'validation-1')
out = {'seal': seal, 'literal_rewritten_to_tilde': '"~/' in (ev / 'literal.py').read_text()}
for name, cmd in (('literal', 'python3 ~/ws/state/tw-script/evidence/validation-1/literal.py'),
                  ('argument', 'python3 ~/ws/state/tw-script/evidence/validation-1/argument.py ~/ws/repo')):
    r = subprocess.run(['env', '-i', f'HOME={home}', 'PATH=/usr/bin:/bin', 'zsh', '-f', '-c', cmd], capture_output=True, text=True)
    out[name + '_exit'] = r.returncode
print(json.dumps(out, indent=1))
