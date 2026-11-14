# Independent validation — PR 869

Verdict: **REJECTED** at `5e9afd496a6901cc788252a77d84f355acbf0015`, base `c2f035b6612f5edb42220576b3414e993531ffd6`. One Material documentation finding, F1, remains. Candidate product bytes are unchanged. This is an independent recommendation, not a gate resolution or merge decision.

## Active scope and findings

Captain amendment 1 withdraws AC-1 through AC-5; AC-6 is the only active numbered criterion. Amendments 2 and 4 also require one owning record contract without losing unique rules, and one shared question guard sequence. Amendment 3/4 budget is three implementation and two validation cycles. Historical seven/nine-summary requirements are not silently reinstated.

- **F1 Material:** The positive second-reviewer declaration was removed from workflow.md but never stated in delivery-record.md. The old instruction was `second reviewer: <name> because <trigger>`; the new contract names shared guards and documents only `Second reviewer: not triggered`. A normal FO with a triggered configured reviewer cannot learn the required positive declaration from the new owning document. The blind reader independently asked what declaration/profile guards require (question 11). Existing paired fixtures show omission → check/question 1/1 on both inputs, while `Second reviewer: copilot because review rules.` → 0/0 on both. This violates amendment 2's unique-rule preservation obligation. See `evidence/validation-1/findings.json` for all four disposition fields and `missing-declaration.json` for reproduced control/counterexample. Recommend the smallest contract-only clarification through the FO repair route; product files were not repaired.

No new Needs decision finding. The Captain's pending ruling on the pin-deletion experiment remains a delivery decision. The earlier FO-declined question-time freshness concern is not reopened.

## Independently exercised

- AC-6 bounded behavior passes: the two archived public task/report/dispatch input replays pass check, question, native preparation, with unchanged question bytes and equal summary/reference JSON digests (`replays.json`). Provider/reviewer facts are controlled fixtures; report-reading Captain steps were freshly executed, not historical acceptance scripts.
- Real read-only PR 865 observation saves a held record: check/question 1/1. Direct isolated native preparation exits 0 only as JSON transport; it is not a successful delivery route (`live.json`).
- Current-main question-only controls fail at exit 1; restoring manual-summary requirements fails the candidate test. Local-job-counting mutation fails all three historical inventories; duplicate reads leave counts unchanged (`goal-check.json`, `mutation.json`, `rounds.json`). Historical review identities are FO-recorded, not authenticated provider history.
- Held `ask-N` filename mutation fails the merge-audit regression. Both changed-dispatch-head cases start at question 0 and then hold at 1 (`candidate-mutations.json`). These and the preceding controls cover every active AC-6 named falsifier.
- All six confirmed regression methods pass. Cases 1–5 reject their unsafe paired inputs. Case 6 intentionally accepts both inputs and emits the count/scope warning; the contract explicitly says warnings do not hold. Thus the dispatch's literal “all six refused” claim is **not made**. Removing each class's owning behavior is detected (`mutations.json`).
- One question function, one return, no separate facts_question (`question-shape.json`). Eight independent question-stage counterexamples have passing producer controls, reject both inputs, then accept both when the selected shared guard is disabled (`shared-guard-mutations.json`). Those eight guards are declaration, structured prod trigger, merge-head token, current configuration, Captain steps, Captain hold-out clause, clean-worktree removal, and merge-result disclosure. Format-specific judgment/refusal parsing and count disclosure remain explicit reader differences; the eight common mutations are not falsely presented as six identical predicates.
- Producer schema conformance and actual argument-parser recipes pass. Omitting `ci` fails conformance; `--record-factz` and `--facts-rekord` are both rejected by the parser with exit 2 (`contract-mutations.json`).
- A fresh blind subagent received only the shipped contract. Its passing/held synthetic records independently conform to the embedded JSON Schema. All 22 questions and assumptions are retained, individually dispositioned in `blind-reader-dispositions.json`; question 11 supplies F1. Invented fixture source bytes are explicitly not workflow-valid or proof of real execution.
- The later check rereads changed provider head and holds at 1; the earlier record then holds at question 1 (`late-head.json`). The workflow also requires final `--match-head-commit`. No real PR head was changed and no merge was attempted. This confirms a later guard, not live freshness at question time.

## Pin deletion and necessity

The separate paragraph in implementation/pr.md accurately limits the deletion experiment: old summary/Candidate wording pins and old-command mutation were deleted without rewriting; existing behavioral pins remain. The original single demonstrated unguarded case was a recipe flag typo missed by static pins/lint, not proof every package test missed it. At this candidate the actual command-parser regression catches that typo. The deletion is not retroactively declared Captain-approved, and no new wording pin or product repair was added by validation.

Nine task product paths remain: the checker implements saved observations/shared guards; the contract and three consumers own/move instructions; delivery/POC/native tests cover the changed boundary; lint records the authorized word cuts. The baseline question-only failures establish goal necessity. Net code reduction and faster delivery are not established. F1 means the contract deduplication is not yet sufficient despite the successful behavior.

## Checks, exact candidate and limits

`hosted-pr.json` was read live: PR 869 OPEN/Draft at the exact candidate; five successful checks, one skipped deploy. The whole 29-command suite was not rerun, as dispatched. Fresh local focused execution and acceptance: 13 delivery tests, 9 POC tests, repository lint, plus the mutations/replays above. `acceptance.log` records actual output, including the POC test's expected internal negative-control diff; overall exit 0.

Installed governance commands: ADR lint (`python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/adr_lint.py docs/adr --since c2f035b6612f5edb42220576b3414e993531ffd6`) exit 0, 79 records; role triggers, 12 dispatch records, design surfaces, document impact, number guards and comment ratio pass. All 20 listed documents have dispositions; validation traced moved duties and found F1 despite the implementation's no-loss assurance. Comments are 3/550 (0.5%, maximum 5%); added comments were read. Workflow is 5996/5996 words. No CI files changed; CI cost per PR not measured.

Initial sandbox GitHub read failed; the narrow authorized network retry passed. Initial number guard had stale-ref warning; first network retry accidentally used the outer cwd (retained as numbers-network.log and not accepted as candidate proof). Explicit assigned-worktree retry passes on 5e9afd496 (`numbers-exact-head.log`). All candidate runtime probes used a `git archive` export; no git worktree was created/removed. Installed governance checks needing git ran read-only in the assigned worktree. See provenance.json for matching product/export digests.

The implementation's remaining limits stand: no green live delivery; no authenticated historical reviewer inventory or report/step execution truth; no proof of every conditional reviewer/waiver or truthful human disposition; no complete moved-trunk lifecycle or future trunk lock; no private-repository rollout, installed adoption, downstream consumer migration or general secret classifier; no newly rendered Mermaid layout (no changed product diagram), and no measured dynamic reading/elapsed-time gain. Hosted CI is now verified at this head; RoboRev remains FO-owned and its historical results were not recertified. Public allowlisting/private-or-unknown refusal were exercised, which does not prove universal content classification.

## Minimal Captain acceptance

No user-visible screen changes. Run the following exact command in a fresh shell; it contains four numbered steps, exports this exact SHA, runs 13 focused delivery and 9 POC tests, then lint. Requires the named local repository, git, tar and Python 3; no network or extra install. Expected exit 0 and `ACCEPTANCE PASSED` in under five minutes (command completed with exit 0; full wall duration was not separately measured). Both original and exact documented-command runs exited 0; their output is retained as `evidence/validation-1/acceptance.log` and `acceptance-exact-command.log`.

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/merge-ask-is-produced-from-records/validation/acceptance.sh
```

The script checks bounded behavior; it does not clear F1, certify real review/acceptance execution, or authorize delivery. The contract's missing declaration requires FO-dispositioned repair and a separate validation recheck.
