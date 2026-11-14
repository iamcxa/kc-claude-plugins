"""Run candidate gate, evidence, and sealing behavior on an invented local workflow."""
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

code, base, output = map(lambda x: Path(x).resolve(), sys.argv[1:4])
binary = sys.argv[4]
home = base / 'home'
home.mkdir(parents=True)
repo = home / 'product'
workflow = repo / 'docs/dev2'
state = workflow / '.spacedock-state'
remote = base / 'remote.git'
identifiers = base / 'invented-identifiers.tsv'
private = 'invented-private-repository'
identifiers.write_text('private-repo\t' + private + '\n')
env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
env.update(HOME=str(home), KC_DEV2_IDENTIFIERS=str(identifiers), PYTHONDONTWRITEBYTECODE='1',
           GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1',
           GIT_AUTHOR_NAME='Fixture', GIT_COMMITTER_NAME='Fixture',
           GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_EMAIL='fixture@example.invalid',
           GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='commit.gpgsign', GIT_CONFIG_VALUE_0='false',
           GIT_CONFIG_KEY_1='user.email', GIT_CONFIG_VALUE_1='fixture@example.invalid')
os.environ.update(env)
sys.path.insert(0, str(code / 'kc-dev-flow-2/scripts'))
import scratch

commands = []
def run(argv, expected=0, cwd=None, shell_env=None):
    p = subprocess.run(list(map(str, argv)), cwd=cwd or repo, env=shell_env or env,
                       text=True, capture_output=True, timeout=60)
    def safe(s):
        return s.replace(str(home), '<fixture-home>').replace(str(base), '<scratch>').replace(str(code), '<candidate>').replace(binary, '<spacedock>')
    commands.append(dict(argv=[safe(str(a)) for a in argv], exit=p.returncode,
                         stdout=safe(p.stdout), stderr=safe(p.stderr)))
    if expected is not None:
        assert p.returncode == expected, commands[-1]
    return p

def git(*args, expected=0):
    return run(['git', '-C', state, *args], expected)

def commit(label, expected=0):
    git('add', '--', 'probe.md', 'probe')
    return git('commit', '-qm', label, '--', 'probe.md', 'probe', expected=expected)

workflow.mkdir(parents=True)
(workflow / 'README.md').write_text((code / 'kc-dev-flow-2/references/sd/workflow.md').read_text())
(repo / '.gitignore').write_text('**/.spacedock-state/\n')
run(['git', 'init', '-q', '-b', 'main', repo])
run(['git', '-C', repo, 'init', '-q', '--bare', remote])
run(['git', '-C', repo, 'remote', 'add', 'origin', remote])
run(['git', '-C', repo, 'add', '.gitignore', 'docs/dev2/README.md'])
run(['git', '-C', repo, 'commit', '-qm', 'test: seed'])
run(['git', '-C', repo, 'worktree', 'add', '--detach', state])
git('checkout', '--orphan', 'spacedock-state/dev2')
git('rm', '-rf', '.')
(state / 'seed').write_text('public state\n')
git('add', 'seed')
git('commit', '-qm', 'test: seed state')
git('push', 'origin', 'spacedock-state/dev2')
run(['git', '-C', repo, 'config', 'extensions.worktreeConfig', 'true'])
guard = code / 'kc-dev-flow-2/scripts/state_guard.py'
run([sys.executable, '-B', guard, 'install', state, '--refuse', 'home,private-repo'])
run([sys.executable, '-B', guard, 'check', state])

head = subprocess.run(['git', '-C', str(code), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
task = state / 'probe.md'
folder = state / 'probe'
evidence = folder / 'evidence/validation-1'
evidence.mkdir(parents=True)
script = evidence / 'argument.py'
script.write_text('import pathlib, sys\nassert pathlib.Path(sys.argv[1]).is_dir()\nprint("PASS")\n')
literal = evidence / 'literal.py'
literal.write_text('import pathlib\nassert pathlib.Path(' + repr(str(repo)) + ').is_dir()\n')
seal_result = scratch.evidence(folder, 'validation-1')
tilde = lambda p: '~/' + p.relative_to(home).as_posix()
command = 'python3 ' + tilde(script) + ' ' + tilde(repo)
shells = {}
for shell, flags in (('bash', ['--noprofile', '--norc']), ('zsh', ['-f'])):
    fresh = dict(HOME=str(home), PATH='/usr/bin:/bin')
    shells[shell] = run([shell, *flags, '-c', command], shell_env=fresh).returncode
literal_exit = run(['zsh', '-f', '-c', 'python3 ' + tilde(literal)], expected=None,
                   shell_env=dict(HOME=str(home), PATH='/usr/bin:/bin')).returncode
assert literal_exit != 0
literal.unlink()
scratch.evidence(folder, 'validation-1')
report = '## Stage Report: validation\n\n- DONE: acceptance command\n\n```sh\n' + command + '\n```\n'
task.write_text('---\ntitle: Public fixture gate\nstatus: validation\nvariant: kc-dev-flow-2\nprofile: pilot\n---\n\n' + report)
(folder / 'dispatch').mkdir()
(folder / 'dispatch/validation-1.md').write_text('# validation\nCandidate: ' + head + '\n\n## Checklist\n\n- check\n')
(folder / 'captain-steps').mkdir()
record = folder / 'captain-steps/1.md'
record.write_text('Candidate: ' + head + '\n\n### Step 1\nAsked: ' + command +
                  '\nRan: fresh shell, 2026-11-14T13:00:00Z, exit 0\nObserved: PASS\n')
question = folder / 'question.md'
message = 'Accept this public fixture? Run this command:\n\n```sh\n' + command + '\n```\n'
question.write_text(message)
summary = folder / 'summary.md'
summary.write_text('Sufficiency: the public acceptance command works.\nNecessity: the validator supplies a runnable gate step.\nExternal rounds: 0\nCaptain steps: captain-steps/1.md\n')
delivery = code / 'kc-dev-flow-2/scripts/delivery_gate.py'
steps = run([sys.executable, '-B', delivery, 'steps', record, '--text-file', question])
q = run([sys.executable, '-B', delivery, 'question', task, '--text-file', question,
         '--summary-file', summary, '--workflow-dir', workflow])
artifact = folder / 'review.md'
artifact.write_text('The fixture is ready for a local review.\n')
commit('test: commit gate source before preparation')
prepare = run([binary, 'gate', 'prepare', 'probe', '--question', message,
               '--artifact', artifact, '--summary', summary.read_text(), '--workflow-dir', workflow])
clean_commit = commit('test: clean gate')
git('push', 'origin', 'spacedock-state/dev2')
clean_tip = git('rev-parse', 'HEAD').stdout.strip()
blob_ids = set(git('ls-tree', '-r', clean_tip).stdout.splitlines())
hits = {'home': 0, 'private-repo': 0}
for entry in blob_ids:
    sha = entry.split()[2]
    raw = subprocess.run(['git', '-C', str(state), 'cat-file', 'blob', sha], capture_output=True, check=True).stdout
    hits['home'] += str(home).encode() in raw
    hits['private-repo'] += private.encode() in raw
assert hits == {'home': 0, 'private-repo': 0}

absolute = command.replace(tilde(script), str(script)).replace(tilde(repo), str(repo))
record.write_text(record.read_text().replace(command, absolute))
question.write_text(message.replace(command, absolute))
task.write_text(task.read_text().replace(command, absolute))
run([sys.executable, '-B', delivery, 'question', task, '--text-file', question,
     '--summary-file', summary, '--workflow-dir', workflow])
absolute_commit = commit('test: absolute gate refused', expected=1)
for p in (record, question):
    p.write_text(p.read_text().replace(absolute, command))
mixed = run([sys.executable, '-B', delivery, 'question', task, '--text-file', question,
             '--summary-file', summary, '--workflow-dir', workflow], expected=1)
assert 'S5: unrecorded command' in mixed.stdout
task.write_text(task.read_text().replace(absolute, command))
git('add', '--', 'probe.md', 'probe')

private_log = evidence / 'private.log'
private_log.write_text(('public data\n' * 30000) + private + '\n')
scratch.evidence(folder, 'validation-1')
refused = commit('test: sealed private evidence refused', expected=1)
assert 'private-repo identifier' in refused.stderr and private not in refused.stderr
(evidence / 'private.log.gz').unlink()
with task.open('a') as f:
    f.write('\nNot archived (private): the invented adopter log; reproduce: python3 check.py ~/' + private + '\n')
scratch.evidence(folder, 'validation-1')
reproduce_refused = commit('test: private reproduction refused', expected=1)
task.write_text(task.read_text().replace('~/' + private, '<adopter checkout>'))
accepted = commit('test: drop private evidence and record reproduction')
git('push', 'origin', 'spacedock-state/dev2')
assert 'private.log' not in (evidence / 'SHA256SUMS').read_text()

clean = gzip.compress(b'public evidence\n', mtime=0)
header_results = []
for flag, field in ((8, private.encode() + b'\0'), (16, private.encode() + b'\0'),
                    (4, len(private).to_bytes(2, 'little') + private.encode())):
    packed = clean[:3] + bytes([flag]) + clean[4:10] + field + clean[10:]
    assert private.encode() not in gzip.decompress(packed)
    p = evidence / 'header.gz'
    p.write_bytes(packed)
    c = commit('test: header refused', expected=1)
    assert private not in c.stderr and 'private-repo identifier' in c.stderr
    header_results.append(dict(flag=flag, refused_exit=c.returncode, name_printed=private in c.stderr))
    p.unlink()
git('add', '--', 'probe.md', 'probe')
result = dict(candidate=head, AC1=dict(steps_exit=steps.returncode, question_exit=q.returncode,
              gate_prepare_exit=prepare.returncode, clean_commit_exit=clean_commit.returncode,
              committed_blob_hits=hits, fresh_shells=shells, absolute_commit_exit=absolute_commit.returncode),
              AC2=dict(sealed_refused_exit=refused.returncode, private_printed=private in refused.stderr,
                       reproduce_refused_exit=reproduce_refused.returncode,
                       corrected_commit_exit=accepted.returncode, stale_manifest_entry=False),
              AC4=header_results, AC5=dict(seal=seal_result, argument_exit=shells['zsh'], literal_exit=literal_exit))
output.mkdir(parents=True, exist_ok=True)
(output / 'probe.json').write_text(json.dumps(result, indent=2) + '\n')
(output / 'probe-commands.json').write_text(json.dumps(commands, indent=2) + '\n')
print(json.dumps(result, indent=2))
