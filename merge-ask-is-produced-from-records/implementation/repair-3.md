# Implementation 3: merge main and share the question guards

Candidate: `5e9afd496a6901cc788252a77d84f355acbf0015`.
Branch: `spacedock-ensign/merge-ask-is-produced-from-records`.
Base: `c2f035b6612f5edb42220576b3414e993531ffd6`.
Evidence: `evidence/implementation-3/`; all commands, exits and logs are joined there.

The assigned candidate `ad41870b72f19d8ad141efaa67cda3afb23f1d4d` was clean when work began. Merge commit `57f796175985d1f5e0bab90cbffe96614ead17c6` merges origin/main without rebasing, preserving PRs 864, 867, 868 and 870. Only lint-skills.py conflicted: both task cuts (-30 and -87) and both new main steps (-2 and +16 with its existing Captain quote) remain. Workflow words and budget are exactly 5996; current main is 6113 and the prior candidate was 5982. No new budget raise or ADR was introduced.

The requested post-merge progress message was attempted once through the FO's Paseo address and rejected with `user rejected MCP tool call`. It was not delivered; no retry or alternative tool send was attempted.

## Result and proof

Two readers now provide text-summary or facts-record inputs to one `question()`, with one mandatory guard sequence and one final return. The separate facts_question function and early route return are removed. Current configuration, reviewer declaration/profile, text/disposition, Captain-step, merge-head, worktree-removal and merge-result checks share the sequence. Legacy summary fields/refusal placement and facts-record digest bindings stay explicit format differences. There is no live pull-request reread at question time; the Chief Engineer/FO deferral is preserved.

The six confirmed paired regression classes pass. Eight independent question-only negative cases are rejected through both readers after a passing producer; disabling their one shared guard makes both unsafe inputs pass. These cover declarations, structured prod trigger, bounded head, current configuration, Captain-step evidence, the Captain's hold-out clause, clean-worktree removal and merge-result not-run placement. Facts digests are refreshed in these isolated mutations to expose the selected guard rather than a different binding failure. No product bytes are mutated. `shared-guard-mutations.json` records the controls and both exits/diagnostics; `question-shape.json` supplements this with the single-return/call structure.

At the exact final candidate all 29 CI-listed direct Python commands pass locally: 1493 unittest cases run, 1482 pass, 11 optional skips, plus two passing native scripts and lint. The native adapter is Spacedock 0.27.2; its plugin mod is unmodified public commit `4d158a484ec73e184861067f8ed1e20087fdc26a`. This is local macOS evidence, not hosted Linux CI. Python uses -B and PYTHONDONTWRITEBYTECODE=1 after owned package caches were cleared, with task-owned TMPDIR. No delegated RoboRev or hosted-CI clean claim is made.

Repository lint, installed ADR lint, number guards, comment ratio, design surfaces and role triggers pass. Comment ratio is 3/550 (0.5%, maximum 5%). The first number-guard state fetch failed in the sandbox; the authorized network retry and final-candidate check pass without that warning. All 20 documents listed by doc_impact.py have an updated/unaffected disposition, plus the four updated contract/reference documents, in `doc-impact-dispositions.json`. Existing rulings remain unchanged; the contract's prose now names the shared question sequence. No changed product diagram requires a new rendering claim.

## AC-6 and falsifiers

Two real public archived task/report/dispatch inputs pass check, question and native local preparation without a hand-written factual summary; the question bytes remain unchanged and the bound JSON summary/reference digests match. Fresh-shell report-reading fixtures replace stale archived Captain-step paths without running historical acceptance commands. The current-main question-only comparison holds for the missing hand-written summary fields.

A real read-only public PR 865 observation saves a held record: check and question both exit 1. Direct native preparation of that record separately proves JSON transport, not a passing delivery preflight or approval. Restoring manual-summary requirements, allowing held ask filenames, including local jobs in the round count, and replacing dispatched heads all fail their recorded controls. Round inventories remain 2/1/1 with duplicate reads unchanged; their historical reviewer identities are FO-recorded inputs, not authenticated event-time provider truth.

Initial failures are retained. The first complete delivery run had one failure and one error from stale source-mutation anchors; both mutations were retargeted, not removed. Focused parity attempts preserve the legacy refusal-fixture location correction. A preliminary CI run was stopped to restore the two required ADR pointers; the full 29 commands were then rerun at the final commit. `adr-lint.log` retains the first pointer failure and `adr-lint-final.log` the passing result.

## Size and handoff

From current main: nine product files, +766/-193. Consolidation after the main merge: three files, +94/-100; delivery_gate.py alone +77/-91. The merge itself imports the authorized main changes. No tenth task product path, version change, CI-definition change, new ADR or budget raise. Full-task net removal, lifecycle-reading reduction, elapsed speedup and CI cost per PR are not measured or claimed.

`implementation/pr.md` has the Conventional Commit title and complete prepared body for the existing Draft PR, preserving the pin-deletion experiment as its own paragraph for the Captain to rule on. Readback of PR 869 is OPEN/Draft at `ad41870b72f19d8ad141efaa67cda3afb23f1d4d`. This candidate and state remain local; no push, PR write, review request, ready transition or merge occurred. FO owns push, RoboRev, hosted CI and independent validation. Truthful human dispositions/waivers, private-record rollout, downstream adoption, question-time live freshness and real green delivery remain outside this proof.

This complete report supersedes earlier implementation assurance for the delivered candidate while preserving all prior runs and their limits. Final suite completed 2026-11-14 02:27:06 UTC; scratch-close output is in `implementation/repair-3-close.txt`.
