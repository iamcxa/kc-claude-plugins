import datetime, hashlib, json, os, pathlib, re, shutil, subprocess
O=pathlib.Path(__file__).parent
I=json.loads((O/'identity.json').read_text()); W=pathlib.Path(I['worktree'])
S=W.parent.parent/'docs/dev2/.spacedock-state'; T=S/'counts-name-the-run-that-produced-them.md'
DEST=T.with_suffix('')/'validation/validation-2'
def sha(b): return hashlib.sha256(b).hexdigest()
def git(*args): return subprocess.check_output(['git','-C',str(W),*args],text=True).strip()
assert git('rev-parse','HEAD')==I['head'] and git('status','--porcelain')==''
assert git('branch','--show-current')=='spacedock-ensign/counts-name-the-run-that-produced-them'
assert subprocess.check_output(['git','-C',str(S),'branch','--show-current'],text=True).strip()=='spacedock-state/dev2'
scope=git('diff','--name-only',I['base'],I['head']).splitlines()
assert len(scope)==9 and not any('workflow.md' in x or '/mods/' in x or '/_mods/' in x or x.startswith('.github/') for x in scope)
assert git('diff','--name-only',I['previous'],I['head'])=='kc-dev-flow-2/scripts/count_tokens.py'
trees=[]
for label,revision in [('candidate',I['head']),('previous',I['previous']),('merged',I['merge_tree'])]:
    listing=subprocess.check_output(['git','--git-dir='+str(O/'objects.git'),'ls-tree','-rz',revision])
    checked=[]
    for entry in listing.split(b'\0'):
        if not entry: continue
        attrs,name=entry.split(b'\t',1); mode,kind,expected=attrs.decode().split(); name=name.decode()
        if kind!='blob': continue
        p=O/label/name
        b=os.readlink(p).encode() if mode=='120000' else p.read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        assert actual==expected,(label,name,actual,expected)
        checked.append([name,expected])
    trees.append(dict(export=label,revision=revision,tracked_blobs_match=True,paths=checked))
(O/'source-integrity.json').write_text(json.dumps(dict(worktree=str(W),head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),status=git('status','--porcelain'),scope=scope,trees=trees),indent=2)+'\n')
required=['probe','baseline','mutations','retained-mutations','suite-candidate','suite-merged','lint','adr','adr-dispatch','comments','doc-impact','design','dispatch','words','extra-falsifiers','numbers-refreshed','github-pr-refreshed','github-review-comments-refreshed','gate-replay','learn-replay','replay-differences-current','acceptance']
verified=[]
for name in required:
    d=json.loads((O/(name+'.json')).read_text())
    assert d['exit']==0,(name,d['exit'])
    assert d['sha256']==sha((O/d['log']).read_bytes())
    assert d['identity']['head']==I['head']
    verified.append(dict(name=name,exit=d['exit'],log_sha256=d['sha256']))
assert 'warning:' not in (O/'numbers-refreshed.log').read_text()
assert (DEST/'acceptance.sh').read_bytes()==(O/'acceptance.sh').read_bytes()
assert (O/'cycle-record.json').read_bytes()==(T.with_suffix('')/'validation/validation-1/cycle-record.json').read_bytes()
gate=[json.loads(x) for x in (O/'gate-replay.log').read_text().splitlines()][1:]
learn=[json.loads(x) for x in (O/'learn-replay.log').read_text().splitlines()][1:]
assert sum(r['after']['briefings'] for r in gate)==30 and sum(r['after']['nonzero_disclosure'] for r in gate)==23
assert sum(r['entries'] for r in learn)==28
assert {x['job'][:8] for r in learn for x in r['refused']}=={'441fe280','d829872c'}
suite={name:re.search(r'Ran (\d+) tests.*?OK \(skipped=(\d+)\)',(O/(name+'.log')).read_text(),re.S).groups() for name in ['suite-candidate','suite-merged']}
pr=json.loads((O/'github-pr-refreshed.log').read_text())
assert pr['headRefOid']==I['head'] and pr['state']=='OPEN' and pr['isDraft']
assert json.loads((O/'github-review-comments-refreshed.log').read_text())==[]
docs={
'0044':'unaffected: optional separate-summary review facts and legacy combined calls retain their checks.',
'0051':'unaffected: External rounds remains independently required by check; count disclosure does not clear holds.',
'0062':'unaffected: quoted bound-question approval and merge authority are unchanged.',
'0071':'unaffected: newest matching delivery record and reference binding are unchanged.',
'0072':'updated in original PR: automatic disclosure and learn reference join match runtime. The bounded sequence exception has its ruling home in task Amendment 2 and AC-9, with no new decision or ADR rewrite.'}
(O/'document-verdicts.json').write_text(json.dumps(docs,indent=2)+'\n')
(O/'findings.json').write_text('[]\n')
(O/'acceptance-results.json').write_text(json.dumps([dict(name='AC-'+str(n),status='passed',evidence=e) for n,e in [(1,'acceptance.log; learn-join.log'),(4,'gate-replay.log; learn-replay.log; replay-differences-current.log; extra-falsifiers.log'),(5,'words.log; budget-mutant.log'),(6,'suite-candidate.log; suite-merged.log; lint.log; source-integrity.json'),(7,'probe.log; acceptance.log; number-in-file.log; writer.log'),(8,'acceptance.log; pr-body.log; writer.log'),(9,'probe.log; baseline.log; mutations.log')]],indent=2)+'\n')
(O/'verification.json').write_text(json.dumps(dict(verdict='PASSED',head=I['head'],checks=verified,suites=suite,prior_finding='F1 Needs decision resolved by Captain Amendment 2 and AC-9 evidence',new_findings=[],verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
readme=f'''# Independent validation after Captain amendment 2

PASSED at PR #822 head `{I['head']}`. F1 from validation-1 (ordinal citation refused as a count) is resolved by the explicit Captain ruling and independently reproduced AC-9 behavior. No new Material, Deferred risk, Polish or Needs decision finding was observed. This is a validation recommendation, not gate approval or merge authority.

## Identity and method

Run date: 2026-11-10 UTC. Original base `{I['base']}`; freshly fetched origin/main `{I['main']}`. `identity.json` records the conflict-free merge-tree result `{I['merge_tree']}`. Candidate, previous head and merged tree were exported under /tmp; no product worktree was created or removed, no product code or repository configuration changed. `source-integrity.json` verifies exported tracked blobs still match their Git trees after all checks, and pins the assigned clean branch. Only count_tokens.py differs from the rejected candidate; the complete original PR scope remains the authorized files listed there.

Every NAME.json receipt records exact argv, cwd, UTC start/end, producer PID/exit, candidate identity and NAME.log hash. Baseline receipt intentionally executes the `previous` export identified by `identity.previous`; suite-merged executes `identity.merge_tree`. `verification.json` checks accepted receipts and hashes. Reused scripts were read before execution: validation-1 replay/word/negative drivers and implementation-4 historical/mutation drivers; only export paths, pinned candidate and the explicitly documented live-store delta were adapted. No model worker or external mutation was used.

## Criteria and falsifiers

| Criterion | Independently observed | Falsifier run |
| --- | --- | --- |
| AC-1 | acceptance.log exercises actual claim/complete with 18 versus referenced 15; refusal leaves pending token usable, correction completes; legacy reads remain valid. | retained-mutations.log / learn-join.log: remove evaluation's join, refusal test fails without ERROR. |
| AC-4 | replay.py gate-replay.log: 23 of 30 recent summaries across the four pinned state revisions require nonzero disclosure. learn-replay.log: 28 add entries across five stores refuse only 441fe280 and d829872c. | extra-falsifiers.log restores the old comma pattern and recovers `2, round`; mutations.log restores the ordinal refusal. |
| AC-5 | words.log independently recounts base/candidate: startup 5931+48 unchanged, validation 826→848, evaluator 877→896; zero-count question 92→97 and check 84→89 words. | extra-falsifiers.log / budget-mutant.log: one added startup word makes native lint reject the unchanged budget. |
| AC-6 | suite-candidate.log: Ran {suite['suite-candidate'][0]} tests, OK (skipped={suite['suite-candidate'][1]}); suite-merged.log: Ran {suite['suite-merged'][0]} tests, OK (skipped={suite['suite-merged'][1]}). Each receipt exit 0. Lint, ADR, design, dispatch and refreshed number checks pass. | budget-mutant.log fails native lint; retained-mutations.log removes the POC writer and both route assertions fail. source-integrity.json confirms scope and unchanged exports. |
| AC-7 | probe.log and acceptance.log exercise actual question writes, wrong/missing/duplicate disclosure, checked 3, unsupported 2, derived ratios, fences, containment, legacy callers and existing holds. | number-in-file.log and writer.log each show required test failure with no ERROR. |
| AC-8 | acceptance.log covers the gh-stub PR body, automatic ask rewrite, idempotence and failure before a merge record on write error. | pr-body.log and writer.log fail their retained tests. |
| AC-9 | probe.log uses the original ed2d3ee1 entry and evidence unchanged; completion exits 0 and stored decision equals the original. Unsupported 2 cells is refused and same-token correction to 3 completes. Each named sequence label/case and adjacent real count is exercised, plus gate disclosure. | baseline.log confirms prior-head refusal; ordinal-exclusion-removed.log restores that failure; plain-count-scan-removed.log permits the unsupported count and therefore fails the probe. |

Both full-suite commands are `SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'`, executed in separate candidate/merged exports. No merge-main repair is needed on these exact bytes. Superseded AC-2/AC-3 are not requirements; AC-7/AC-8 and new AC-9 follow the recorded amendments.

## Replay differences and environmental attempts

`replay-differences-current.log` explains every changed gate sentence by removal of a named sequence identifier and verifies that existing learn-record hashes remain unchanged. Recent nonzero gate summaries decrease from validation-1's 24 to this run's 23; the removed learn refusal is ed2d3ee1 only. No comma defect reappears. The live qnow store gained one completed no-change record afdf39d8 since validation-1; replay-store-drift.json proves its decisions are no-change and proposal null, so add-entry counts and refusal results are unaffected. The initial replay-differences.log failure is the old all-records-identical assertion detecting that real addition, not a product failure; the corrected driver checks exactly that allowed addition and still asserts equality for every old record. It does not broadly ignore drift.

The first wrapped GitHub reads failed inside the sandbox; github-pr-refreshed and github-review-comments-refreshed are the authorized successful reruns. Initial numbers.log disclosed a failed state fetch; numbers-refreshed.log has no warning and is the accepted reservation check. Earlier detached replay launch attempts produced no receipts and are not evidence; the tracked replay runs above completed normally. adr.log uses the selected Codex skill package root; adr-dispatch.log additionally runs the exact dispatch-specified Claude package ADR command, both exit 0. package-parity.json confirms those ADR checkers and skill entrypoints are byte-identical.

## Documents, sufficiency and necessity

doc-impact.log returns ADR 0044, 0051, 0062, 0071 and 0072; document-verdicts.json gives a disposition for each after reading their decisions. comments.log measures 3 ADR-link comments among 227 added code lines (1.3%, maximum 5%); each added comment was read and is a governing-document pointer. No workflow, mod, version or CI topology change occurred; CI cost per PR was not measured.

At Pilot depth the accepted goal is sufficient: ordinal source references complete unchanged, unsupported measured numbers stay correctable before completion, and gate disclosures continue to be written. Necessity is supported by the previous-head failure and the targeted removals of sequence exclusion, count scan, learn join, cited-number comparison, automatic writer and PR-body scan. The POC expected-output adjustment preserves the approved forwarding behavior and its holds. No extra policy, parser layer or production obligation was added.

## Limits judged

- A number present in cited material proves presence only, not truth or which command produced it; stale or unrelated numbers may pass. This is an accepted design limit of ADR 0072, not widened by the repair.
- The original outside-adopter issue #811 record is unavailable. The 18/15 CLI case reproduces its reported shape; the historical ed2d3ee1 record and local replay are the declared observed data.
- Derived gate counts remain unchecked without a hold; derived learn numbers must appear in references. These are the accepted distinct behaviors.
- Chat, spelled-out quantities, implicit lists, stage-report text outside summaries and PR readers who never see the ask remain outside scanning. Named sequence labels are excluded by Captain Amendment 2, including their case variants; arbitrary natural-language classification is not claimed.
- Existing completed records remain readable, and historical bytes were not rewritten. Local fixtures/replays do not establish host-wide adoption, native agent writing behavior or unattended reliability.
- The implementation's prior state-publication hold was not assumed resolved from prose: the shared state was clean on entry, and this validation publishes only its own report/evidence. The product remained unchanged.
- github-pr-refreshed.log observes this exact head still OPEN/Draft, test CI successful, docs deploy skipped, and completed Codex review with no major issues; inline review comments are empty. This is read-only provider evidence, not completion of FO's entire delivery workflow. RoboRev, readiness, Captain gate/merge decision and adoption remain FO/Captain-owned and were not performed here.

## Captain acceptance script

Run unchanged in a fresh shell:

```sh
bash --noprofile --norc {DEST}/acceptance.sh
```

The four commented steps export the pinned candidate, run the unchanged historical entry plus refusal/correction probes, run retained learning/disclosure/forwarding tests, then check amendment presentation. Expected: `Exported {I['head']}`, historical completion_exit 0, unsupported refusal_exit 1 and correction_exit 0, `Ran 10 tests` / `OK`, `design surfaces presentable`, and `Acceptance passed for {I['head']}`. acceptance.json/.log record this exact published-path fresh-shell execution with exit 0. Required inputs are Git, tar, Python 3, the pinned repository object, this committed evidence folder, and the explicit installed package/Spacedock paths in the script. It creates a disposable /tmp export. No graphical surface exists; this is observable CLI acceptance. It does not repeat the full suite, corpus, mutations, hosted review or merge, and grants no delivery authority.
'''
(O/'README.md').write_text(readme)
before=T.read_bytes(); front=before.split(b'---',2)[:2]
report=f'''

## Stage Report: validation

- DONE: Independent verdict on PR #822 head 4a146449 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states.
  PASSED at {I['head']}; validation/validation-2/README.md and acceptance-results.json map all current criteria to this validator's commands and falsifiers, classify validation-1 F1 as resolved under Amendment 2, and record no new findings.
- DONE: Focused re-validation after the Amendment 2 repair: validation-1 REJECTED only on F1 (an ordinal citation refused as a count); judge the new criterion for Amendment 2 and re-run validation-1's evidence only where the repair could change it, including the ed2d3ee1 'Cycle 1 FO line' entry completing unchanged and the merge with current origin/main.
  probe.log completes that original entry unchanged and retains unsupported-count refusal plus same-token correction; baseline.log and mutations.log detect both reversals. merge.log merges current main {I['main']} cleanly into tree {I['merge_tree']}; suite-candidate.log and suite-merged.log exit 0 (respectively Ran {suite['suite-candidate'][0]} and {suite['suite-merged'][0]} tests, each skipped={suite['suite-candidate'][1]}), so these bytes need no merge-main repair.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition.
  bash --noprofile --norc {DEST}/acceptance.sh exits 0 (acceptance.json/.log); README.md gives its four steps, expected output and limits. adr-dispatch.json/.log records the exact named ADR command with --since {I['base']} --require 0072, exit 0. findings.json is empty; previous F1 Needs decision is resolved, not waived.
- DONE: AC-1, AC-7 and AC-8 retain their actual failure, correction and disclosure boundaries.
  acceptance.log and both full suites cover learn join, pending token, legacy reads, K-shaped disclosure, derived ratios, PR body, containment, fences and write errors; retained-mutations.log requires FAIL without ERROR after removal of learn join, source comparison, writer, PR-body scan or POC forwarding write.
- DONE: AC-4 rerun final gate/learn replays and explain every difference.
  replay.py at this candidate, 2026-11-10 UTC: gate-replay.log has 23 of 30 recent summaries with nonzero disclosure; learn-replay.log has 28 add entries and only 441fe280/d829872c refused. replay-differences-current.log accounts for excluded sequence identifiers, the removed ed2d3ee1 refusal, unchanged old record hashes and one new no-change qnow record; extra-falsifiers.log catches the old comma grammar.
- DONE: AC-5 reading cost and AC-6 scope, guards, dispatch records and retained documents.
  words.log: startup 5931+48 unchanged, validation 826→848, evaluator 877→896, zero-count question 92→97 and check 84→89; budget-mutant.log rejects one extra startup word. lint/adr/design/dispatch/numbers-refreshed receipts exit 0; comments.log is 1.3% below 5%; document-verdicts.json covers every doc-impact result. source-integrity.json confirms clean product and authorized scope; no CI change, cost per PR unmeasured.
- DONE: Judge sufficiency, necessity and all implementation limits at the exact candidate.
  README.md binds necessity to the prior-head failure and targeted removals; accepted presence-only, derived-count, outside-scan and unavailable-adopter limits remain. No native-agent, adoption or delivery proof is claimed; GitHub review/CI observations are separately saved.
- SKIPPED: Product repair/push, PR comments, review requests, readiness, RoboRev, merge, adoption and worktree cleanup.
  FO/Captain own these actions. github-pr-refreshed.log observes OPEN/Draft at the exact head with successful test CI and completed Codex review; no inline findings. Source bytes, task frontmatter and prior reports are preserved.

### Summary

Independent validation recommends PASSED for {I['head']}, superseding validation-1's rejection after the Captain-authorized ordinal correction. The original historical entry now completes unchanged, actual counts retain their refusal/recovery behavior, and current-main merge plus the fresh-shell acceptance pass; the remaining delivery decision belongs to FO/Captain.
'''
assert 'validation/validation-2/README.md' not in before.decode()
T.write_bytes(before+report.encode())
assert T.read_bytes().startswith(before) and T.read_bytes().split(b'---',2)[:2]==front
(O/'append.json').write_text(json.dumps(dict(task=str(T),before_sha256=sha(before),after_sha256=sha(T.read_bytes()),previous_bytes_preserved=True,frontmatter_unchanged=True),indent=2)+'\n')
for p in O.iterdir():
    if p.is_file() and p.suffix in {'.py','.json','.log','.patch','.sh','.md'} and not p.name.endswith('-running.json'):
        shutil.copy2(p,DEST/p.name)
manifest=[dict(file=p.name,sha256=sha(p.read_bytes())) for p in sorted(DEST.iterdir()) if p.is_file() and p.name!='manifest.json']
(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(verdict='PASSED',head=I['head'],report=str(T),evidence=str(DEST),accepted_checks=len(verified))))
