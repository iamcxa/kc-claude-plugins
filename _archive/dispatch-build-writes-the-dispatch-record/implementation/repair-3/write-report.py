#!/usr/bin/env python3
"""Append the complete repair report after exact-head acceptance succeeds."""
import json
from pathlib import Path
import re
import subprocess

state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
slug='dispatch-build-writes-the-dispatch-record'
entity=state/(slug+'.md'); out=state/slug/'implementation/repair-3'
wt=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record')
sha='bd9d4abce4e0c61a69079d4e822b6ded45cfdc20'
assert subprocess.check_output(['git','-C',str(wt),'rev-parse','HEAD'],text=True).strip()==sha
assert not subprocess.check_output(['git','-C',str(wt),'status','--porcelain'],text=True)
assert (out/'fresh/candidate.txt').read_text().strip()==sha
ci=json.loads((out/'package-ci/results.json').read_text())
assert len(ci)==28 and all(r['exit']==0 for r in ci)
seam=json.loads((out/'fresh/dispatch-stage.json').read_text())
assert len(seam)==22 and all(r['status']=='passed' for r in seam)
for rel,size in (('fresh/falsifiers/results.json',13),('scope-falsifiers/results.json',9),('warning-falsifiers/results.json',4)):
 rows=json.loads((out/rel).read_text()); assert len(rows)==size and all(r['status']=='passed' for r in rows)
scope=json.loads((out/'scope-summary.json').read_text()); assert scope['all_preserved'] and scope['refusal_snapshots']==98
counts=dict(commands=len(ci),tests=sum(r['tests'] or 0 for r in ci),skipped=sum(r['skipped'] for r in ci))
(out/'verification.json').write_text(json.dumps(dict(candidate=sha,package=counts,seam_tests=22,original_falsifiers=13,scope_falsifiers=9,warning_falsifiers=4,scope=scope,publication='not run; FO-owned'),indent=2)+'\n')
first=Path('/tmp/spacedock-dispatch/5c030106-8d82-4542-855e-1498b2563c69-spacedock-ensign-dispatch-build-writes-the-implementation.md').read_text()
original=[l for l in first.split('### Completion checklist\n',1)[1].split('### Summary',1)[0].splitlines() if l.strip()]
latest=(state/slug/'dispatch/implementation-1-message-6.md').read_text()
repair=[re.sub(r'^\d+\. ','',l) for l in latest.split('## Checklist\n',1)[1].split('## Scope notes',1)[0].splitlines() if re.match(r'^\d+\. ',l)]
assert len(original)==4 and len(repair)==3
ratio=(out/'fresh/comment-ratio.log').read_text().splitlines()[0]
items=[
('SKIPPED',original[0],f'Candidate {sha} is locally committed on the assigned branch, parent 778367adde2e20e0b3e51966ddba2d9f77f9e614, base 334d91e3165953b2ca7191e3308d80b6c02c4a99. Only dispatch_stage.py and test_dispatch_stage.py change; PR #812 remains on the parent (pr-readonly.json). FO owns the product push and review reply; no product push or PR write.'),
('DONE',original[1],'ADR 0070, its protected writer pointer and the Captain quote are retained. ADR 0026 still owns diagnosis counts/questions; this repairs their transport to FO. FO-supplied model/roster, separate preflights, observer correction and approved README passages remain unchanged; no new ADR/version.'),
('SKIPPED',original[2],'All local exact-head acceptance and package commands pass (fresh/candidate.txt, verification.json); the original thirteen, nine preservation and four warning mutations fail as intended. Hosted AC-8 and independent validation on this new head are not run; the parent hosted/validation verdict is not transferred.'),
('SKIPPED',original[3],f'Fresh repository lint, authorized candidate ADR lint, number guards and diff check exit 0; {ratio}, below 5%. Installed 0.35.0 ADR lint still exits 1 on the unchanged historical ADR 0047 assertion; follow-up 2 authorizes the candidate linter. Prepared PR is in repair-3/prepared-pr.md and /tmp/impl-dispatch-build-writes-the-dispatch-record-pr.md. FO owns publication/RoboRev/hosted CI; CI cost per PR unmeasured, triggers unchanged.'),
('DONE',repair[0],'regression-before.log and its command JSONL reproduce both successful real builds losing the checker warning on the parent writer. regression-after.log passes both tests after the two-line success-path forward; failure/checker/cleanup and builder output handling remain unchanged.'),
('DONE',repair[1],'Two real 0.27.2 tests assert the three questions and one shared reminder on stderr, a committed second same-Symptom record and JSON envelope, and retain an older stage\'s distinct warning. An observing executable reads the wrapper stderr at invocation before delegating to the real binary. warning-falsifiers/ rejects removed/duplicate/late forwarding and whole-stream deduplication at the matching assertions; failed checks keep their existing branch.'),
('DONE',repair[2],f'Unchanged acceptance.sh in fresh bash exits 0 at {sha}; fresh/ has 22 seam, 47 lint and 115 record tests plus real dispatch transport and thirteen counterexamples. package-ci/results.json: {counts["commands"]} CI-listed Python commands exit 0, {counts["tests"]} tests reported, {counts["skipped"]} optional skips. Product commit is local, stage report appended, no PR reply.'),
('DONE','Retain live AC-1 through AC-4, AC-6, AC-7, AC-9 and local AC-8 behavior, including the whole-scope preservation repair.','Exact-head seam/transport tests and original controls retain received bytes, owned cleanup, retry/new-input/later-commit numbering, advance commit/envelope and missing-binary wiring. Scope evidence has 92 matrix cases and 98 unchanged snapshots; nine mutations detect bypasses. Captain amendment 1/AC-9 and the accepted outside-staged no-op retry limit remain intact. Exclusive same-task ownership through check/build/commit/cleanup is still required; there is no transaction-lock/concurrent-writer safety claim.'),
('DONE','Required local consistency checks and itemized document dispositions.','design-surfaces.log exits 0 (presentable; Scope scan not run at validation); doc-impact-verdicts.json covers every listed document below. This repair edits no documentation or diagram; the original base-relative ADR disposition is retained. Task frontmatter, Captain amendment and earlier reports stay intact; new-head external assurance remains FO-owned.'),
]
report='\n\n## Stage Report: implementation\n\n'+'\n'.join(f'- {s}: {i}\n  {e}' for s,i,e in items)
report+='\n\n### Document dispositions\n\n'
for r in json.loads((out/'doc-impact-verdicts.json').read_text()):
 report+=f'- `{r["doc"]}` — {r["verdict"]}: {r["reason"]}\n'
report+='\n### Summary\n\n'
report+=f'This complete implementation report supersedes earlier implementation reports at candidate {sha}: successful record-check warnings now reach FO before building, repeated lines print once, and distinct stage reminders remain visible. All required local exact-head checks pass; Captain amendment 1, data-preservation and exclusive-writer limits remain, and FO owns the new head\'s publication, hosted CI, review reply and independent validation. Evidence is under `{slug}/implementation/repair-3/`.\n'
(out/'stage-report.md').write_text(report)
read=subprocess.run(['/Users/kent/.local/bin/spacedock','status','--read',slug,'--workflow-dir',str(state.parent),'--json'],check=True,capture_output=True,text=True)
(out/'task-before-report.json').write_text(read.stdout)
assert int(json.loads(read.stdout)['total_lines'])==len(entity.read_text().splitlines())
assert sha not in entity.read_text().split('## Stage Report: implementation')[-1]
with entity.open('a') as f:f.write(report)
# Regenerate the prepared PR around final behavior and exact-candidate evidence.
pr=f'''feat(kc-dev-flow-2): record stage dispatches before building

Build stage-worker dispatches through a package script that writes a record from
the actual checklist/scope notes, runs both record checks, then invokes Spacedock.
The stamp commit includes the record; advance commits before returning its envelope.
Successful checker warnings reach FO before the build, with identical lines printed
once and distinct stage reminders retained. Checker success chatter stays out of
the JSON envelope; existing failure diagnostics and cleanup ownership are preserved.

The wrapper checks the complete task commit scope before selecting a record.
HEAD, index and raw worktree bytes/modes must agree, with no nonignored untracked
work; conflicts, hidden index flags and unsupported types/escapes hold without
builder/cleanup calls. Owners must preserve/reconcile staged and worktree versions
before intentionally committing. Exclusive same-task ownership must last through
check/build/commit/cleanup: this precondition is not a transaction lock and makes
no concurrent-writer safety guarantee.

Captain amendment 1 replaces AC-5 with AC-9 and accepts the pinned Spacedock 0.27.2
no-op retry limit: identical retry succeeds without other tasks' staged content;
with it, retry exits 1 with no envelope and no file/index change, because upstream
checks the whole checkout's staged content before an empty task-scoped commit.
After unstaging that other task, retry recovers without a second record. The old
criterion is preserved verbatim; evidence (a)/(c) and its three falsifiers remain.
Changed input or a later state commit still creates the next round. Failed checks
or builds remove only an invocation-created record still absent from HEAD.

ADR 0070 records the approved package seam. Model/roster stay FO-supplied and
package/workflow preflights remain separate. The three approved workflow passages
reduce the budget from 5933 to 5931; FO follow-up 1 authorizes the observer's
matching chat-only entry. No version bump. The installed 0.35.0 ADR linter has a
known historical ADR 0047 assertion false positive; FO follow-up 2 authorizes the
candidate linter, with the assertion unchanged.

Validation at local candidate {sha}: original fresh-shell
acceptance passed; {counts['commands']} checked-in CI Python commands exit 0
({counts['tests']} tests reported, {counts['skipped']} optional skips). Evidence:
implementation/repair-3, including 22 real-binary seam tests, 98 unchanged refusal
snapshots, 13 original + 9 scope + 4 warning counterexamples. The warning observer
reads stderr before invoking the real binary; missing, duplicate, late and
whole-stream-only forwarding each fail matching assertions. The original and
scope controls retain committed inputs, clean retry, numbering, advance,
reconciliation and failure recovery contracts.

Product branch remains local; FO owns pushing this candidate, PR review reply,
new-head hosted CI and independent validation. Prior hosted evidence applies to
parent 778367adde2e20e0b3e51966ddba2d9f77f9e614. CI cost per PR is unmeasured;
existing package/workflow path triggers and CI configuration are unchanged by
this repair.
'''
(out/'prepared-pr.md').write_text(pr)
Path('/tmp/impl-dispatch-build-writes-the-dispatch-record-pr.md').write_text(pr)
print(json.dumps(dict(candidate=sha,report_lines=len(report.splitlines()),**counts)))
