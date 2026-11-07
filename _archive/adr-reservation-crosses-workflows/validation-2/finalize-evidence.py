import datetime
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

OUT = Path('/tmp/adr-reservation-validation-801-r2')
WT = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-adr-reservation-crosses-workflows')
FLOW = WT.parents[1] / 'docs/dev2'
STATE = FLOW / '.spacedock-state'
TASK = STATE / 'adr-reservation-crosses-workflows.md'
DEST = STATE / 'adr-reservation-crosses-workflows/validation-2'
HEAD = 'ef3ed3e05534e2a997acbdfb055a880fde1f484a'
BASE = 'ba055b8a7a55a787ac989c4cef52d07dd75661ad'

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()

checks = json.loads((OUT / 'checks.json').read_text())
assert len(checks) == 18 and all(c['exit'] == 0 for c in checks), checks
suite = (OUT / 'package-tests.log').read_text()
assert re.search(r'^Ran 966 tests in [\d.]+s\s+OK \(skipped=7\)$', suite, re.M), suite[-2000:]
assert '5/5 ADR lint PASS; acceptance PASS' in (OUT / 'acceptance.log').read_text()
ci = json.loads((OUT / 'ci-final.json').read_text())
assert ci['headSha'] == HEAD and ci['conclusion'] == 'success'
assert git(WT, 'rev-parse', 'HEAD') == HEAD
assert git(WT, 'rev-parse', '--abbrev-ref', 'HEAD') == 'spacedock-ensign/adr-reservation-crosses-workflows'
assert git(WT, 'status', '--porcelain') == ''
assert git(STATE, 'rev-parse', '--abbrev-ref', 'HEAD') == 'spacedock-state/dev2'
impact = json.loads((OUT / 'doc-impact.log').read_text())
dispositions = json.loads((OUT / 'doc-impact-disposition.json').read_text())
assert {r['doc'] for r in impact} == {r['doc'] for r in dispositions}

rows = [{'name': 'Full package suite at ' + HEAD, 'status': 'passed', 'message': '966 tests, 7 optional skips; exit 0', 'file': 'package-tests.log'}]
for check in checks:
    log = (OUT / (check['name'] + '.log')).read_text()
    match = re.search(r'Ran (\d+) tests? in ([\d.]+)s', log)
    if match:
        skip = re.search(r'OK \(skipped=(\d+)\)', log)
        rows.append({'name': check['name'], 'status': 'passed', 'message': match[1] + ' tests; ' + (skip[1] if skip else '0') + ' skips; exit 0', 'file': check['name'] + '.log'})
(OUT / 'tests.json').write_text(json.dumps(rows, indent=2))
checks += [
    {'name': 'full-package', 'command': ['python3', '-B', '-m', 'unittest', 'discover', '-s', 'kc-dev-flow-2/scripts'], 'exit': 0, 'status': 'passed', 'log': 'package-tests.log'},
    {'name': 'fresh-bash-acceptance', 'command': ['bash', '--noprofile', '--norc', str(DEST / 'acceptance.sh')], 'exit': 0, 'status': 'passed', 'log': 'acceptance.log'},
    {'name': 'live-candidate-number-check', 'exit': 0, 'status': 'passed', 'log': 'live-number-check.log', 'scope': 'Successful real-origin fetch into disposable bare Git metadata, no fallback warning'},
]
(OUT / 'all-checks.json').write_text(json.dumps(checks, indent=2))
snapshot = json.loads(subprocess.check_output(['/Users/kent/.local/bin/spacedock', 'status', '--workflow-dir', str(FLOW), '--read', str(TASK), '--json'], text=True))
assert snapshot['frontmatter']['status'] == 'validation', snapshot['frontmatter']
(OUT / 'task-before-report.json').write_text(json.dumps(snapshot, indent=2))
boundary = {'head': HEAD, 'base': BASE, 'product_branch': git(WT, 'rev-parse', '--abbrev-ref', 'HEAD'), 'product_status': git(WT, 'status', '--porcelain'), 'state_branch': git(STATE, 'rev-parse', '--abbrev-ref', 'HEAD'), 'state_status_before_report': git(STATE, 'status', '--porcelain'), 'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT / 'boundary.json').write_text(json.dumps(boundary, indent=2))

report = '''

## Stage Report: validation

- DONE: Independent verdict on PR #801 head ef3ed3e0 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Validation-2 PASSED at `ef3ed3e05534e2a997acbdfb055a880fde1f484a`, base `ba055b8a7a55a787ac989c4cef52d07dd75661ad`; all ten criteria and failing controls rerun from archive exports. Full evidence and four-field dispositions: `adr-reservation-crosses-workflows/validation-2/evidence.md`.
- DONE: Re-validate at the repair head: judge the --prune fix for Codex round-1 P2 (comment 4495187504) with its falsifier, re-run the full package suite and the live number guard check read-only, and carry forward validation-1's evidence only where the diff from 6a0a4aec6 leaves it unchanged
  Original Material finding fixed: deletion releases 0060, keeps origin/main and permits check; removing only --prune causes an assertion failure. `scope.json` proves exactly one fetch argument/one test changed; eight documentary hashes match parent, and dynamic evidence was rerun.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Ran `bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/adr-reservation-crosses-workflows/validation-2/acceptance.sh`, exit 0; five steps and expected/observed output in `evidence.md`/`acceptance.log`. Installed ADR lint `--since ba055b8a7a55a787ac989c4cef52d07dd75661ad --require 0002`: exit 0, 61 checked, 0 legacy.
- DONE: AC-1 through AC-4 published holders, collision refusal, folder tasks and branch-qualified exclusion.
  A1/B1 reserve 0061, A2 refuses held 0060 with exact R8 holder/renumber text, A3 accepts 0061; own pushed copy passes while sibling/foreign same-slug holders refuse. Fetch/scan/R8/folder/exclusion mutations each fail (`mutations.json`, `replay-*.log`).
- DONE: AC-5, AC-6 and AC-8 precedence, diagnostics and help; repair falsifier.
  R5 suppresses R8 on base-held numbers; both warnings and cached-holder refusal pass; help names R1-R8/sources. Twelve behavior/help/repair mutations caught, zero runtime errors; base fails 8 of 10 cross-workflow cases. `falsifiers.json` also records budget, quote, Status and integration controls.
- DONE: AC-7 and AC-9 workflow words and the accepted ADR 0002 amendment.
  Startup 5993→5987, worker 224→221, Reserve 84→84, Check 44→44, Collision 204→201; lint 5933/5933. Two approved passages only; missing -6 step refuses. Exact quote/question match gate; wrong quote and invalid Status refuse (`context-checks.log`).
- DONE: AC-10 full package suite, consumer tests and exact-head hosted CI.
  Full suite: 966 run, 7 optional skips, exit 0; number guards 38/38; dispatch 115 run/1 skip. Empty-stderr assertion restored against candidate fails once, no runtime errors. GitHub run 42324691650 completed/success at the exact candidate, including number guards and pinned dispatch (`ci-final.json`).
- DONE: Supplemental checks, parser compatibility, comments and every affected document.
  `checks.json`: all 18 commands exit 0; extension tests and model-free local dispatch rerun. Parser agrees on 142 committed tasks; eight doc-impact dispositions hash-verified. Comment ratio 1/220=0.5% ≤5%; design surfaces, seven dispatch records and diff checks pass; no CI change, cost per PR not measured.
- DONE: Live number guard read scope and all stated design limits.
  Successful origin fetch into isolated `/tmp/adr-reservation-validation-801-r2/live.git`, PASS/no fallback warning. Own state checkout only (74 sibling paths), seven origin state refs/336 eligible paths; exact SHAs in `live-read-set.json`. Race, invisible/out-of-namespace state and multiple-line limits replayed; failed-fetch warning/cached refusal verified.
- DONE: Goal sufficiency and minimal necessity on the repaired candidate.
  Published-holder route works and base fails it; prune alone removes the false stale holder. Remaining changes serve holder reads/exclusion/diagnostics, exact warning regression, budget or approved ruling. No new store, product flag, version bump or CI trigger; no product files changed by validation.
- DONE: Commit the stage report and validation-2 evidence with the dispatched spacedock state commit; state-branch synchronization is allowed by validation-2-message-1.
  Appended this complete report and task-scoped evidence only; prescribed helper commits/synchronizes `spacedock-state/dev2`. Shared sibling changes are preserved; product publication, PR/review actions and ready/merge remain FO-owned.
- SKIPPED: Native model-worker execution, human gate, delivery-hook body, remote merge and independent RoboRev rerun.
  Outside the command-only proof or FO-owned; optional historical/native inputs remain skipped as recorded. Local extension tests do not substitute for native or RoboRev evidence; hosted CI is independently verified above.

### Summary

Validation-2 PASSED at `ef3ed3e05534e2a997acbdfb055a880fde1f484a`, superseding the prior-head verdict only for this repair. The deleted-branch Material finding is fixed; no open Material, Needs decision or Polish finding. State synchronization is explicitly authorized by validation-2-message-1; FO still owns gate acceptance and delivery.

- F1 Deferred risk: concurrent reserves before state push can collide; two 0061 reserves then R8 after publication were observed. `value-ac[AC-2]` promises published-holder refusal; accepting a visible holder would make this Material.
- F2 Deferred risk: unpublished/no-origin/out-of-namespace state remains invisible, as replayed. ADR 0002 requires unique published state branches; missing a correctly published holder would make this Material.
- F3 Deferred risk: a failed fetch may retain stale refs with the required warning; cached-holder refusal and warning controls pass. Silent fallback or a deleted holder retained after successful fetch would make this Material.
- F4 Deferred risk: multiple reservation lines remain unenforced under Design Limits; both existing lines are returned. A new exact-one obligation or ignored collision line would make this Material; full four-field dispositions are in evidence.md.
'''
assert 'Validation-2 PASSED at' not in TASK.read_text()
(OUT / 'stage-report.md').write_text(report)
files = [p for p in OUT.iterdir() if p.is_file() and p.suffix in {'.py', '.sh', '.md', '.json', '.log', '.diff'}]
for path in files:
    shutil.copyfile(path, DEST / path.name)
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in DEST.iterdir() if p.is_file() and p.name != 'sha256.json'}
(DEST / 'sha256.json').write_text(json.dumps(hashes, indent=2))
before = TASK.read_bytes().split(b'---', 2)[1]
with TASK.open('a') as handle:
    handle.write(report)
assert TASK.read_bytes().split(b'---', 2)[1] == before
print('Appended validation-2 report after line', snapshot['total_lines'], 'and copied', len(files), 'evidence files; frontmatter unchanged.')
