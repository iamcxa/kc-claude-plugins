from pathlib import Path
import json,subprocess,shutil,hashlib
s=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1');w=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-pilot-ideation-runs-a-probe-before-the-design');state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state');task=state/'pilot-ideation-runs-a-probe-before-the-design'
refs=json.loads((s/'out/refs.json').read_text()); checks=json.loads((s/'out/check-results.json').read_text());assert len(checks['results'])==7 and all(r['exit']==0 for r in checks['results'])
assert refs['candidate']=='45d5ebb9d24665c0904aca5412123a7224d056cc'
assert subprocess.check_output(['git','-C',str(w),'rev-parse','HEAD'],text=True).strip()==refs['candidate']
assert not subprocess.check_output(['git','-C',str(w),'status','--porcelain'],text=True)
old=subprocess.check_output(['git','-C',str(w),'show',refs['previous_candidate']+':kc-dev-flow-2/references/sd/workflow.md'],text=True)
new=(w/'kc-dev-flow-2/references/sd/workflow.md').read_text(); phrase='evidence command runs once on it, recording command, exit and output path';assert phrase in new and len(new.split())==len(old.split())==6099
paths=subprocess.check_output(['git','-C',str(w),'diff','--name-only',refs['previous_candidate'],refs['candidate']],text=True).splitlines();assert paths==['kc-dev-flow-2/references/sd/workflow.md']
(s/'out/repair.diff').write_bytes(subprocess.check_output(['git','-C',str(w),'diff',refs['previous_candidate'],refs['candidate'],'--','kc-dev-flow-2/references/sd/workflow.md']))
(s/'out/final-code-state.json').write_text(json.dumps(dict(candidate=refs['candidate'],branch=refs['branch'],changed_files=0,product_paths_since_validated_candidate=paths,proof_phrase_raw_contiguous=True,workflow_words=6099,product_pushed=False,live_worker_runs=0),indent=2)+'\n')
mut=json.loads((s/'out/mutation-results.json').read_text()); assert all(r['exit']==1 for r in mut)
assert json.loads((s/'out/mutation-AC-1-result.json').read_text())['exit']==1
criteria=[dict(name='AC-10' if r['name']=='AC-3' else r['name'],status='passed',command=r['command'],exit=0,evidence=r['output']) for r in checks['results']]
criteria += [dict(name='AC-8',status='untested',detail='Fresh live worker validation owed for this new candidate; prior validation verdict is preserved.'),dict(name='AC-9',status='untested',detail='Accepted post-release obligation; no new released worker run.')]
(s/'out/acceptance.json').write_text(json.dumps(criteria,indent=2)+'\n')
current=json.loads((s/'out/doc-impact.json').read_text()); prior=json.loads((task/'evidence/implementation-1/doc-impact-verdicts.json').read_text());assert {r['doc'] for r in current}=={r['doc'] for r in prior}; verdict={r['doc']:r['verdict'] for r in prior}
for r in current:r['verdict']=verdict[r['doc']]
(s/'out/doc-impact-verdicts.json').write_text(json.dumps(current,indent=2)+'\n')
report='''# F2 wording repair

Candidate: 45d5ebb9d24665c0904aca5412123a7224d056cc; base: 88f86f2749dadb6f4ef0cf9aa089c1827096865b; branch: spacedock-ensign/pilot-ideation-runs-a-probe-before-the-design. Local commits only, no product push. Start: 2026-11-13 16:18:17 Asia/Taipei, clock.curr_time UTC +08:00. Final completion reply records the end from the same source.

The repair changes one existing workflow sentence and nothing else in the product. Its final words are:

> Every criterion's evidence command runs once on it, recording command, exit and output path per criterion, provenance included; unrunnable: `Not provable now`.

The sentence is 22 words, replacing 22. The approved checker's phrase is verbatim and contiguous even in the raw file. The workflow remains 6099 words. Ideation SKILL.md, principles.md, its Pilot profile and the shared Pilot profile contain no second version of the command/exit/output-ledger instruction. Their current-evidence and Probe provenance duties are complementary and unchanged; exact hashes are in skill-profile-review.json.

The first authorized wording was committed locally as 8fd752939e85b07a095d950ba68fb27c0e004abe and made the original AC-1 checker fail because its searched phrase was removed. FO declined an evidence-procedure change and replaced the wording assignment with message-3. The replacement commit 45d5ebb9 is on top, as directed. The original failed attempt is retained separately in attempt-1; none of its results is used as proof of the final candidate. No checker was edited or replaced. approved-procedures.json verifies the original evidence procedures' bytes.

All approved runnable acceptance evidence commands pass unchanged on the new candidate: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7 and AC-10. AC-10 is the fresh-id replacement under Captain amendment 2, and still executes the corrected accept.sh AC-3 command. Exact environment, argv, exits and outputs are in check-results.json; acceptance.json maps commands to current criterion IDs. Both candidate native dispatches carry all five required properties, and both base arms are ban-only. The native suite is model-free; it does not prove the repaired wording changes a worker's behavior.

The four disposable-copy falsifiers return the expected failing exit 1 for an outside-ideation POC change, a copied ban, a removed raise and a 6100-word README (mutation-results.json). Substituting base as candidate also returns 1 (mutation-AC-1-result.json). They ran with python3 -B and bytecode disabled. All 47 lint tests pass at the final candidate; repository lint prints 6099/6099. AC-5 records the unchanged lifecycle word deltas against base.

Installed 0.41.0 ADR lint exits 0, requiring ADR 0084 against base; number guard exits 0 at the exact new head. Comment ratio exits 0 under its fewer-than-20-code-lines exemption: 4 code lines, 1 required ADR pointer, 25.0%; this is not a claim of a ratio below the 5% maximum. The same 11 document impacts retain their recorded dispositions (doc-impact-verdicts.json); no new document or product surface is needed for the clarification.

The real-task design-surfaces check initially returned 1 because amendment 2 reused the superseded AC-3 ID. FO corrected the form to fresh AC-10 and directed a pull. That unchanged command now exits 0 (design-surfaces-result.json); the earlier failure is preserved as design-surfaces-before-fo-correction.log. This worker edited no criterion. The statement and evidence procedure are the Captain's amended ones.

AC-8 remains unverified at this new head until the final independent live-worker observation; the earlier REJECTED verdict and its causal limits are preserved. AC-9 remains the accepted post-release obligation. RoboRev, hosted CI, product publication, final validation, merge and release are FO/Captain-owned and not run by this repair. One validation cycle remains. CI cost per PR was not measured; no CI trigger changed.
'''
(s/'out/report.md').write_text(report)
e=task/'evidence/implementation-1/repair-1';e.mkdir(parents=True)
for p in (s/'out').iterdir():
    if p.is_dir():shutil.copytree(p,e/p.name)
    else:shutil.copy2(p,e/p.name)
shutil.copytree(s/'attempt-1',e/'attempt-1')
for name in ['run-repair-checks.py','run-mutations.py','package-repair.py']:shutil.copy2(s/name,e/name)
(task/'implementation/pr.md').write_text('''feat(kc-dev-flow-2): try Pilot designs on a local probe

Pilot ideation currently carries a blanket write ban, so FO must hand-write probe instructions. The workflow now expects a bounded local probe unless the design explains why not, requires every criterion's evidence command and command/exit/output record (provenance included), and holds a third ideation dispatch for the Captain. Pilot reuses the POC proof paragraph; implementation reads and deletes the recorded probe branch after committing its candidate.

The duplicate ban and lint exception are removed. The approved 66-word raise carries the Captain's words and loaded moments; ADR 0084 supersedes only ADR 0005's Pilot write ban. POC derivation, Prod's ban and the design gate are preserved. The F2 clarification replaces 22 words with 22; the workflow remains 6099 words and retains the approved evidence checker's literal phrase. Skill/profile instructions remain consistent and unchanged.

Local candidate: 45d5ebb9d24665c0904aca5412123a7224d056cc. All approved runnable evidence commands pass unchanged: AC-1, AC-2, AC-4 to AC-7 and AC-10. Captain amendment 2 assigns fresh AC-10 to the settled no-duplicate-ban criterion; its corrected command remains accept.sh AC-3. All 47 lint tests, repository lint, native model-free dispatch suite, POC equality, timeline count, ADR lint, number guard and real-task design-surface check pass. Five named mutation controls fail as expected. Comment ratio passes its small-change exemption (4 code lines, 1 required ADR pointer).

AC-8 needs final independent live-worker validation at this new head; AC-9 remains the accepted post-release cleanup obligation. The earlier worker's omission is confirmed, but its cause was not established from one run. No behavioral success claim is made from this wording repair. RoboRev, hosted CI, publication and release checks remain FO-owned and were not run here. CI cost per PR was not measured; no CI trigger changed. No speed or defect-reduction claim.
''')
print('Packaged final repair evidence and refreshed PR text with AC-10; final candidate is local only.')
