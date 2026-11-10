from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent
meta=json.loads((p/'identity.json').read_text());summary=json.loads((p/'tests-summary.json').read_text());checks=json.loads((p/'checks.json').read_text());corpus=json.loads((p/'corpus-reconciliation.json').read_text())
assert summary['failed_files']==[] and summary['test_files']==27,summary
assert all(r['exit']==0 for r in checks)
assert sum(r['L4_events'] for r in corpus)==7
assert json.loads((p/'acceptance-exit.json').read_text())['exit']==1
assert len(json.loads((p/'mutations.json').read_text()))==9
assert len(json.loads((p/'reverted-fix.json').read_text())['tests'])==3
criteria=[
 {'name':'AC-1: original introducing event and predicate falsifiers','status':'passed','evidence':'candidate-bite.log; base-bite.log; mutations.json'},
 {'name':'AC-2: legitimate shapes and invalid unmarked move','status':'failed','note':'Original fixtures pass; F3 tilde example hides an unmarked real replacement.','evidence':'review-example-tilde.log'},
 {'name':'AC-3: report a defect once at introduction','status':'failed','note':'F1 partial repair fixed; F2 loses the known introducing diagnostic when another task cannot be read.','evidence':'reverted-fix.json; review-probes.json'},
 {'name':'AC-5: registry, documentation bound and FO reading','status':'passed','evidence':'artifact.json; mutation-heading-0.log; lint.log'},
 {'name':'AC-6: shared marker and unchanged design-check compatibility','status':'passed','evidence':'test_design_surfaces.log; check-comparison.json; mutations.json'},
 {'name':'AC-7: hosted activation','status':'blocked','note':'Deferred by approved D2 until release, Captain pin approval and observed state push.','evidence':'activation-limit.json'},
 {'name':'AC-8: seven events and per-entry structural skip','status':'passed','evidence':'corpus-reconciliation.json; corpus-comparison.json; current-tail.json; mutations.json'}]
(p/'acceptance.json').write_text(json.dumps(criteria,indent=2)+'\n')
report=f'''## Stage Report: validation

- DONE: Independent verdict on PR #828 head d7502656 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at `{meta['head']}`, base `{meta['base']}`; evidence under `amendment-checked-when-written/validation/cycle-2/`. F1 is repaired, but independently reproduced F2/F3 remain Material; AC-7 and its hosted falsifier remain deferred by approved D2.
- FAILED: Recheck of the Cycle 1 repair: finding F1 of validation-1 is closed at this head (partial repair adds no event; growth reports only added ids; mixed removal and addition), AC-3 is green, and the seven corpus events are unchanged
  `reverted-fix.json` and `test_laws_check.log` close F1; `corpus-comparison.json` proves all seven event payloads unchanged. The combined item cannot pass because new F2 independently violates AC-3 by losing the only known introducing diagnostic.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  `README.md`/`acceptance.sh`: six exact steps, run with `bash --noprofile --norc`; steps 1–5 pass, step 6 prints two False results and exits 1 (`acceptance.log`, `acceptance-exit.json`). Declared-package ADR lint against the pinned base exits 0, 65 records (`adr-lint.log`); explicit 0017/0041/0057 requirements also pass.
- DONE: AC-1 — introducing commit reports both defects and each predicate falsifier removes its own diagnostic.
  `candidate-bite.log` reports one event with reused AC-1/AC-2/AC-4 plus unmarked replacement; `base-bite.log` has no L4. `mutation-{{reuse,marker}}-bite.log` and `mutations.json` prove removal of either predicate loses its diagnostic and fails its test.
- FAILED: AC-2 — every moved amendment without a real marked replacement is refused.
  Original record-only/marked/waived controls pass and the payload mutation fails; `review-example-tilde.log` nevertheless exits 0 for a real unmarked move whose only marker is an example. Backtick-only control exits 1 (`review-example-backtick.log`): F3.
- FAILED: AC-3 — report each defect at its introducing commit without repeating or losing it.
  Partial/growth/mixed repair regressions pass; reverting the repair fails all three (`reverted-fix.json`), and the first-parent mutation fails. `review-unreadable-{{solo,combined,repair,later}}.log` shows F2: diagnostic present alone, lost in combined push, never recovered on later unrelated edits.
- DONE: AC-5 — registry, documentation budget and FO reading boundaries.
  `artifact.json`: exactly four approved files, laws.md 1345 to 1587 words (+242 <=250), workflow/skills/dispatch/CI template/versions unchanged. `lint.log` passes; removing the L4 heading fails `mutation-heading-0.log`.
- DONE: AC-6 — one shared marker predicate, preserved design-check behavior and existing tests.
  `test_design_surfaces.log` runs 217 cases with four skips; `check-comparison.json` retains 1,032 identical candidate/base check/seed verdicts. Disabling the shared predicate fails both suites (`mutation-marker-{{0,1}}.log`); F3 is an inherited fence-helper gap newly exposed through L4, not an alleged design-check regression.
- SKIPPED: AC-7 — containing release, Captain-approved pin and observed hosted state-push run, including its hosted old-pin falsifier.
  `activation-limit.json`, `dev2-laws.yml` and `old-pin-bite.log` confirm the local old pin and no L4; this is only a local negative control. Approved D2 leaves hosted activation open; no release or adopter edit was made.
- DONE: AC-8 — seven historical events, valid siblings and first-judgeable heading repairs.
  `corpus-reconciliation.json` proves 3/3/1 events; `corpus-comparison.json` proves exact prior-candidate L4 payload equality; `current-tail.json` finds no extra event at newer local tips. Full CLI exits 2 for pre-existing L3 ambiguity. Per-entry/heading-repair controls and their restored-skip mutations pass/fail as required.
- DONE: Independently rerun every package test-file command and the existing mutation/reverted-fix evidence.
  `tests-summary.json`/`tests.json`: {summary['test_files']} commands exit 0, {summary['unittest_cases']} unittest cases with {summary['skipped_cases']} skips plus model-free CLI assertions; nine mutation rejections and three reverted-fix assertion failures are separately recorded. Local CLI 0.27.2/plugin 0.27.3; no hosted/model-execution claim.
- DONE: Required checks, implementation dispatches, Captain amendments and added-comment review.
  `checks.json`: lint, ADR, comment ratio (0/246, 0%, max 5%), number guards, doc-impact, task design, role triggers and nine dispatch records pass; `criterion-move.json` proves verbatim AC-4 withdrawal/fresh AC-8. Initial archive metadata error was corrected; number-guard fetch remains local-ref-only and this task changes/reserves no number.
- DONE: Every affected document has an independent updated or unaffected disposition.
  `doc-verdicts.json`: ADR 0041 unaffected (seed admission unchanged), ADR 0057 unaffected (word comparison unchanged), laws.md updated (event claims still fail F2/F3), learning.md unaffected (historical practices retained and applied).
- DONE: Assess goal sufficiency, minimal necessity, all implementation limits and current review evidence at the same candidate.
  `README.md` binds each of four files to detection, existing event wiring, falsifiers or registry docs; sufficiency fails F2/F3. Post-push, record-only, in-place, quote, local-tool and fixture-skip limits remain; CI cost per PR/state push is unmeasured. `pr-threads.json` records both unresolved exact-head review findings; PR body still cites the previous candidate.
- SKIPPED: Product repair/publication, PR edits or replies, review resolution, release/adoption, hosted CI, gate decision and merge.
  These remain FO/Captain work; this worker changes only its state evidence/report and publishes that prescribed state commit. Product candidate/branch stay unchanged; green unit suites do not discharge the two reproduced Material findings.
- F2 Material: An unrelated unreadable task discards already known L4 violations; `kc-dev-flow-2/scripts/laws_check.py:380` lets Cannot escape the whole law.
  User/workflow: adopter pushes several tasks and repairs an unreadable one; harm: the readable task's sole introducing diagnostic vanishes; boundary: `value-ac[AC-3]` and `contract[docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md#decision]` report new events at introduction; trigger/control: `review-unreadable-*.log`, `review-probes.json`. Fields and source review: `findings.json`.
- F3 Material: A tilde-fenced example supplies a fake live marker; `kc-dev-flow-2/scripts/design_surfaces.py:419` uses a backtick-only live-section filter.
  User/workflow: worker includes a standard Markdown example with a move; harm: a real unmarked replacement passes with exit 0; boundary: `value-ac[AC-2]` invalid moves must fail and `contract[kc-dev-flow-2/references/sd/laws.md#l4-amendment-moves-use-fresh-ids]` requires a live/moved declaration; trigger/control: `review-example-{{tilde,backtick}}.log`. Full fields: `findings.json`.

### Summary

Cycle 2 independently recommends REJECTED for PR #828 at `{meta['head']}`: the Cycle 1 F1 repair works and preserves the seven historical events, while two newly completed review findings are independently reproduced as Material. Return F2/F3 through FO disposition before any repair; AC-7 remains open for the approved later release/adoption sequence. This supersedes prior validation readiness, not gate, delivery or review authority; product bytes and all preceding reports are preserved.
'''
assert len(report.splitlines())<=50,len(report.splitlines())
(p/'stage-report.md').write_text(report)
print('Prepared report:',len(report.splitlines()),'lines; REJECTED, F1 repaired, F2/F3 open.')
