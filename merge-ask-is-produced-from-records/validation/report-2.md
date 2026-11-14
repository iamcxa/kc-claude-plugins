# Independent validation cycle 2 — PR 869

Recommendation: **PASSED** at `a5657edd6531916cd01f659b888feaa021219ead`, against base `c2f035b6612f5edb42220576b3414e993531ffd6`. The prior Material F1 (missing positive second-reviewer declaration) is resolved. No new Material, Deferred risk, Polish or Needs decision finding is raised. This is an independent validator recommendation; FO acceptance, Captain gate/merge authority, release and adoption remain separate.

## Scope and repair

AC-6 is the only active numbered acceptance criterion; Captain amendment 1 superseded AC-1 through AC-5. Amendments 2 and 4 require preservation of unique rules in one contract and one shared question guard sequence. This is the second and last validation cycle under the existing three implementation/two validation budget. The repair from `5e9afd496a6901cc788252a77d84f355acbf0015` touches only the contract, one PUBLIC visibility guard line and tests (three paths); the whole candidate has nine product paths. No product bytes were changed by validation.

The original F1 trigger was rerun with the same paired fixture: omitted declaration holds check/question at 1/1 on both legacy and record routes; the shipped contract example passes 0/0 on both (`missing-declaration-fixed.json`). A fresh blind reader, given only the shipped contract and a synthetic scenario, wrote the second-reviewer declaration, external-round line, reviewer outcome and Captain-step pointer. Its literal lines pass all four corresponding guards; its declaration also passes both full routes (`blind-reader/result.json`, `blind-guards.json`). Removing each of these four contract forms causes the new contract check to fail with one assertion failure and no errors (`contract-form-mutations.json`). F1 is recorded fixed in `findings.json`.

The blind reader's three questions concern the actual provider outcome/human disposition, the saved evidence token, and an actual legacy review heading absent from the synthetic scenario. None prevents writing the requested forms. The contract reserves these observations/judgments to their sources, and the reader correctly declines to invent them; all three have explicit dispositions (`blind-reader-dispositions.json`). This does not claim that contract-only reading supplies real review evidence or every workflow policy.

Only explicit `visibility: PUBLIC` saves an observation. PUBLIC controls pass; PRIVATE, missing and INTERNAL with isPrivate=false all exit 2 and create no record. Restoring the old boolean criterion fails the INTERNAL case with one assertion failure/no errors (`visibility-proof.json`, `visibility-controls.log`, `visibility-reverse-mutation.log`). The unmocked public observation also passes visibility and saves a held record (`live.json`).

## Active criterion and regression evidence

All paths below are under `evidence/validation-2/` unless otherwise specified.

- AC-6: the two existing public archive-input replays again pass check/question/native local preparation at 0/0/0, preserving question bytes and matching bound JSON digests (`replays.json`). Historical task/report/dispatch inputs are real public records; provider/reviewer outcomes and new report-reading Captain-step fixtures are controlled. They do not authenticate historical acceptance execution.
- Fresh read-only public PR 865 observation: check/question remain 1/1, with direct isolated native preparation 0 only for JSON transport (`live.json`). It is a held observation, not a green delivery or real gate decision.
- Both base question-only cases hold at 1; restoring the removed manual-summary requirement fails the candidate control (`goal-check.json`, `candidate-mutations.json`). This shows why the retained producer/reader change is necessary for the accepted removal.
- Three real FO-recorded review inventories remain 2/1/1 and repeated observations do not increase counts (`rounds.json`). Restored local-job counting is detected in all three (`mutation.json`). Historical identities remain FO-recorded inputs, not independently authenticated history.
- Held-record-as-ask mutation fails the merge-audit regression, and changing each replay's dispatched head changes question from 0 to 1 (`candidate-mutations.json`). All named active AC-6 falsifiers were rerun.
- The six paired regression methods and their six owning mutations pass (`mutations.json`). Cases 1–5 refuse unsafe inputs; case 6 intentionally accepts and discloses count/scope warnings, as the accepted contract specifies. Eight shared question-guard omissions each turn both unsafe input routes into false passes only after producer controls pass (`shared-guard-mutations.json`). One question function/one return remains (`blind-guards.json`). No previously passing class regressed.
- Producer omission of required ci is detected; both documented-command flag typos are rejected with parser exit 2 (`contract-mutations.json`). The prior pin-deletion experiment and its separately stated limits are unchanged by this repair; no new static pin or product repair was introduced.
- Later provider-head change still holds check at 1 and invalidates the earlier record's question at 1 (`late-head.json`). This is a mocked later-stage falsifier, not a real push or merge. FO-declined job 1859 (no live question-time reread, shared with base) is not reopened. Job 1863 (no Sufficiency/Necessity label presence test on the record route) is also not reopened: the accepted design deliberately removes that presence requirement; no new harm was found.

The moved-rule list was checked against the narrow repair and the owning contract: the repaired positive declaration, legacy rounds and step pointer now reside there; workflow/observer/Copilot consumers were not changed by this repair. The remaining retained surfaces map to the approved producer/reader boundary, schema, shared guards, legacy compatibility, or the authorized wording-budget reduction. No additional production obligation, service, adapter or runtime was introduced. The existing checks demonstrate the bounded goal and necessity; they do not establish faster delivery or net source reduction.

## Exact-head checks and limits

Live hosted PR 869 metadata confirms this exact head, OPEN and Draft, five successful checks and one skipped deploy (`hosted-pr.json`). As instructed, the whole hosted test list was read, not rerun locally. The fresh-shell four-step acceptance runs 14 focused delivery tests, nine POC tests and repository lint, all passing (`acceptance-exact-command.log`). POC emits an expected internal negative-control diff; its suite exits 0. Workflow budget is 5996/5996. The implementation's reported full delivery-suite run is read evidence, not claimed as an independent full-suite rerun here.

Installed governance commands pass (`governance.json`): ADR lint exits 0 with 79 records (`adr-lint.log`); 15 dispatch records are complete (`dispatch.log`); design check and doc-impact exit 0. All 20 affected-document dispositions remain applicable after the three-path repair (`doc-impact-validation.json`). Added comments were read; comment ratio is 3/562 = 0.5%, below 5% (`comments.log`). No task Number guards section, reserved/new ADR or migration is present; no new number allocation check is owed. No CI definition changed; cost per PR was not measured.

Both repair dispatches were read: contract forms and fail-closed public visibility trace to F1/amendment 2 and the explicit repair scope. Role triggers passed at entry and the current budget is not exceeded. Runtime checks use a git-archive export; read-only git/governance checks use the assigned worktree. Its clean head and all nine exported product-file hashes match (`provenance.json`). No product worktree was created/removed, no repository configuration was changed, and no product branch/PR/review/gate was written.

Remaining limits from implementation/validation-1 are upheld: no successful live delivery preflight; no authentication of old reviewer history or actual report/step execution from stored hashes; not every conditional reviewer/waiver or truthful human disposition is proved; no complete moved-trunk lifecycle/future trunk lock, private-adopter rollout, installed adoption, downstream migration or general secret classifier; no new rendered Mermaid (no changed product diagram); no dynamic-reading or elapsed-time improvement measurement. Hosted CI is now independently read at this head, while local RoboRev remains FO-owned. These limits do not block the accepted bounded public Pilot outcome.

The first hosted API read was denied by the sandbox network; a narrow authorized retry passed. An initial exact acceptance run used Python's auto-cleaned system temporary directories, then the final script explicitly set TMPDIR inside its owned export and was rerun unchanged in a fresh shell. Initial and final successful logs are retained; no candidate defect was attributed to that harness correction.

## Captain acceptance — four steps

No screen changes. Requires git, tar, Python 3 and the named local repository with the exact candidate object. Run this exact command; it exports the fixed head, runs 14 record/parity tests, nine POC tests, and repository lint, then removes its export. Expected exit 0 and `ACCEPTANCE PASSED`; each step's expected output is in the script. This is the same four-step acceptance from validation-1 updated for the repaired head/new contract test and an explicit owned TMPDIR. No network or secret is required.

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/merge-ask-is-produced-from-records/validation/acceptance-2.sh
```

Observed output: `evidence/validation-2/acceptance-exact-command.log`; exit 0. This does not establish live review truth, real delivery, merge approval or installed adoption.

Required ADR command (assigned product worktree cwd), exit 0:

```bash
python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/adr_lint.py docs/adr --since c2f035b6612f5edb42220576b3414e993531ffd6
```

Evidence retention/cleanup: `validation/close-2.txt` contains the exact scratch-close output. The state-only report/evidence commit and push are authorized by dispatch; FO owns the next acceptance replay and gate/delivery steps.
