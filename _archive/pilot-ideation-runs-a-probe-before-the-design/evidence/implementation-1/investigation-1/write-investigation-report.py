from pathlib import Path
import hashlib,json,shutil
s=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
task=state/'pilot-ideation-runs-a-probe-before-the-design'; v=task/'evidence/validation-1'
rows=json.loads((s/'instructions.json').read_text()); inputs=json.loads((s/'input-comparison.json').read_text()); proposal=json.loads((s/'proposed-wording.json').read_text())
report='''# F2 investigation before repair authorization

Start: 2026-11-13 16:02:59 Asia/Taipei. Time source: clock.curr_time returned 2026-11-13 08:02:59 UTC; add UTC+08:00. The final completion reply records this investigation's end from the same source.

## Finding

F2's observed reporting omission is confirmed: the subject called its third criterion passed, named an output file, but recorded neither the exact command nor an exit code for that criterion. The record does not establish why the subject made that choice. This is not an inherent inability to prove a provenance criterion: the subject itself names Git ancestry and byte comparison as checks. One run cannot distinguish a wording-caused omission from a one-run instruction-following miss.

The candidate already says **each** criterion's command runs once and names command, exit and output path together. It grants no provenance exception. It does **not** say those three fields must be beside every criterion in that same instruction. The separate ideation principles ask only for per-criterion actual evidence or an honest not-yet-verified statement, and the POC pointer asks for primary evidence. A narrower operational reading is therefore available: run/record commands for executable probe cases, but treat the provenance criterion as an evidence statement supported by a facts JSON. That reading is consistent with the observed output, not proven to be the subject's reasoning and not a finding that this record meets the accepted AC-8.

## What the third criterion was and what it recorded

Source: `evidence/validation-1/live/task.md:156` (the subject's own AC-3, not this parent task's amended AC-3):

> **AC-3** No duplicate product patch and exact existing-fix identity. Evidence: source-identity.json; exported script equals pinned git-show bytes; existing fix is an ancestor; probe commit retained and worktree removed. Reproduce with git merge-base --is-ancestor and byte comparison against authoritative package. Falsifier: product delta or mismatched export invalidates no-change premise. Passed for fixture source only.

The subject's stage report at lines 172–173 calls this DONE and repeats a base, existing-fix commit, retained probe and absent product delta. `source-identity.json` has six fields: base, existing_fix, probe_branch, probe_commit, exported_pr_watch_equals_pinned_source=true and source_changed=false. It contains no command, exit or captured command output. The criterion supplies the output file name and a generic reproduction hint, not a full runnable invocation or the observed result of that invocation. This investigation did not fill in the missing ledger or rerun that proof on the subject's behalf.

By comparison, `live/absent.json` and `live/bare.json` each contain exact argv, cwd, exit=0 and a saved output path. The saved `live/criterion-coverage.json` accurately distinguishes those two ledgers from the third. This confirms a provenance-shaped omission, not that the third check was never executed.

## Reconstructed inputs and limits

The shared state checkout was pulled first with `git pull --ff-only origin spacedock-state/dev2`; it was already current. Candidate remains f0e00d30ce00542b2895f13173bd41075cc8bfd4 on its assigned branch, with no product worktree changes. The installed trigger check exits 0 and reports implementation 1 / validation 1 against the unchanged 1 implementation / 2 validation budget.

Following FO's recovery instruction, the pinned candidate's unmodified replay_dispatch.py was run under the assigned scratch root, using independent bare local clones so replay's worktree operations never touched product/shared-state metadata. It used the recorded historical task pr-watch-tasks-foreign-worktree, historical state 08d61c3e48d7365f7e058d16bea85fd61906539a, code/base 88f86f2749dadb6f4ef0cf9aa089c1827096865b, the saved stripped checklist/scope inputs and the base adopter README. The exact command is in `rebuild-command.json`. The saved Trial-paragraph removal was applied in the disposable state task before analysis, matching `live-seed-adjustment.diff`; no model was started. The original full cold-run build argv was not archived, so this is the recorded reconstruction, not an assertion that every original option is known.

SHA-256 comparison with `validation-1/live/input-digests.json`:

'''
for r in inputs:
    report += '- `'+r['file']+'`: '+('MATCH' if r['raw_match'] else 'NOT RECOVERED')+'; expected `'+r['expected']+'`; regenerated `'+r['regenerated_sha256']+'`.\n'
report+='''
Only checklist.txt and the Pilot ideation profile match. Dispatch.md and scope.txt do not match. Transparent relocation-only comparisons, replacing the new scratch prefix with the validator's old prefix, also fail for both, so path movement alone does not reproduce their hashes. The unknown residual cannot be diagnosed from digests. No extra cold-run scope/checklist wording is inferred.

`stage-def.regenerated.txt` was regenerated by executing the helper-emitted `spacedock dispatch show-stage-def` command on the reconstructed candidate README; it was not recovered from the original run. Its permission/proof wording matches the pinned candidate. Because dispatch and scope are unrecovered and no read trace survives, the enumeration below is **declared reading order only**, not an observed sequence or an exhaustive claim about unknown instructions in those two original files. The SKILL load order is shared Pilot principles, stage principles, Pilot stage reference; linked Before new work and POC paragraph are shown at their call sites. The framework adds no command/exit/output ledger or provenance exception. No unrelated conditional UI/data rules apply to this provenance criterion.

## Relevant instructions in declared reading order

Counts use Python str.split on the exact source span; line wraps are collapsed only for display. Each entry retains its source line in instructions.json. Short directive fragments from the checklist/stage output are included as well as sentences; adjacent explanatory statements are included where they can affect how evidence is interpreted.

'''
for r in rows:
    report+=str(r['order'])+'. `'+r['file']+':'+str(r['line'])+'` — '+str(r['words'])+' words. '+r['text']+'\n\n'
report+='''The sole direct command/exit/output requirement is entry 2 (22 words). Per-criterion report placement is separately requested as actual evidence in entry 17 (21 words), without those field names. The Pilot Probe record in entry 24 (27 words) calls for branch/base/commit/hypothesis/results. The POC first paragraph is 43 words total (entries 21–23); its 17-word evidence sentence asks for primary evidence, not the three-field ledger. These instructions do not formally exempt provenance, but do not join all of the required reporting details in one place either.

## Smallest proposed clarification — not applied

File: kc-dev-flow-2/references/sd/workflow.md, the existing proof sentence beginning on line 188 under ### ideation. Replace only that sentence, with no new instruction home, profile/criteria change, automation or added startup words.

Remove (22 words):

> '''+' '.join(proposal['removed'].split())+'''

Add (22 words):

> '''+' '.join(proposal['added'].split())+'''

The exact line-preserving proposed diff is in proposed-wording.diff. The proposed text joins universal coverage, provenance, the single proof run, all three fields, per-criterion placement and the unrunnable case in one sentence. Whitespace counting gives 6099 before and 6099 after, so no budget raise or lint-budget step is proposed. This is a clarification to try, not a proven behavioral fix; the separately authorized repair and final one-worker validation remain with FO/Captain. No change was made to the candidate, product worktree or criteria.

## Separate evidence-preservation finding

The validator's cold-run dispatch.md, checklist.txt, scope.txt and fetched stage definition were not archived before its scratch close-out. The pack keeps hashes and a path to removed scratch; FO confirms no original copy exists (message 39fa730e-c8cf-4303-a91f-09ebddeac618). A validator or FO checking exactly what the model was given therefore cannot inspect those bytes after close-out, and this reconstruction recovers only part of them. This limits exhaustive input and causal claims; it is separate from candidate wording and F2's directly observed missing ledger. The close-out contract says to copy cited evidence into the task folder before removal (installed scratch.py notes_for); the helper's checksum manifest does not check that all cited inputs were retained. This investigation proposes no product repair for that preservation gap. The regenerated inputs, hash comparisons and regenerated stage are retained here, clearly labeled, so this investigation does not repeat the same archival omission.

## Captain amendment and handoff

Captain amendment 2 stands: the parent task's AC-3 evidence command is settled by the Captain, the statement stands, the budget is unchanged and one validation cycle remains. This investigation does not reopen F1, alter any acceptance criterion, change product bytes or run another worker. The validation-1 REJECTED verdict remains its original independent verdict. FO decides whether to authorize the proposed wording repair, then validation-2 can test that candidate once; a second rejection returns to the Captain as recorded.
'''
(s/'report.md').write_text(report)
findings=[dict(severity='high',title='F2: provenance criterion lacks command and exit',file='evidence/validation-1/live/task.md',line=156,detail='Observed omission confirmed. The causal role of wording is not decidable from one run; no provenance exemption is explicit. Proposed clarification remains unapplied.'),dict(severity='medium',title='Cold-run inputs were not archived before close-out',file='evidence/validation-1/live/input-digests.json',detail='Checklist/profile hashes match the reconstruction; original dispatch and scope do not. Enumerated order is declared only; stage definition is regenerated, not recovered.')]
(s/'findings.json').write_text(json.dumps(findings,indent=2)+'\n')
e=task/'evidence/implementation-1/investigation-1'; e.mkdir(parents=True)
for name in ['report.md','findings.json','instructions.json','file-words.json','proposed-wording.json','proposed-wording.diff','input-comparison.json','rebuild-command.json','seed-adjustment-check.json','stage-def.regenerated.txt','read-only-baseline.json','role-triggers-investigation.log','rebuild.log','rebuild-investigation.py','analyze-instructions.py','write-investigation-report.py']:
    shutil.copy2(s/name,e/name)
# Keep every regenerated input and the candidate source spans cited by the enumeration, without the historical task seed or cloned repositories.
keep=['live/dispatch.md','live/checklist.txt','live/scope.txt']+[r['file'] for r in rows if r['file'].startswith('live/package/')]+['live/package/kc-dev-flow-2/references/sd/workflow.md']
for name in sorted(set(keep)):
    dst=e/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s/name,dst)
print('Retained investigation report, all reconstructed input files, hash comparisons and the unapplied wording diff.')
