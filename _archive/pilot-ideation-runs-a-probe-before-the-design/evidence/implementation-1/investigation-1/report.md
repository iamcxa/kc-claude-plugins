# F2 investigation before repair authorization

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

- `dispatch.md`: NOT RECOVERED; expected `a537f52dadf207254570e934a407d457ea3a70a710224dd4c6b459eed5e043ff`; regenerated `1bf76f0b80d0dfdd09ed02398432fedf99fbd712795f89e0680f0c2d6fe873f7`.
- `checklist.txt`: MATCH; expected `94508bdcfa6324406c56a727606d7b26e1164203e311212c500947da5e0197d7`; regenerated `94508bdcfa6324406c56a727606d7b26e1164203e311212c500947da5e0197d7`.
- `scope.txt`: NOT RECOVERED; expected `1bc8a3fa81dad26e4e3af19cbdfe3f4a933d62a1fdffd1ef343778300eae2d3b`; regenerated `72f69272d40719cc05bb24aca211c1367a83448d407db070406dea63ff344cb2`.
- `package/kc-dev-flow-2/skills/ideation/profiles/pilot.md`: MATCH; expected `ef0ca54df016464d8f726dc252c4f8def1afb5941a73b87befd92c355f41e9a3`; regenerated `ef0ca54df016464d8f726dc252c4f8def1afb5941a73b87befd92c355f41e9a3`.

Only checklist.txt and the Pilot ideation profile match. Dispatch.md and scope.txt do not match. Transparent relocation-only comparisons, replacing the new scratch prefix with the validator's old prefix, also fail for both, so path movement alone does not reproduce their hashes. The unknown residual cannot be diagnosed from digests. No extra cold-run scope/checklist wording is inferred.

`stage-def.regenerated.txt` was regenerated by executing the helper-emitted `spacedock dispatch show-stage-def` command on the reconstructed candidate README; it was not recovered from the original run. Its permission/proof wording matches the pinned candidate. Because dispatch and scope are unrecovered and no read trace survives, the enumeration below is **declared reading order only**, not an observed sequence or an exhaustive claim about unknown instructions in those two original files. The SKILL load order is shared Pilot principles, stage principles, Pilot stage reference; linked Before new work and POC paragraph are shown at their call sites. The framework adds no command/exit/output ledger or provenance exception. No unrelated conditional UI/data rules apply to this provenance criterion.

## Relevant instructions in declared reading order

Counts use Python str.split on the exact source span; line wraps are collapsed only for display. Each entry retains its source line in instructions.json. Short directive fragments from the checklist/stage output are included as well as sentences; adjacent explanatory statements are included where they can affect how evidence is interpreted.

1. `live/checklist.txt:3` — 24 words. Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

2. `stage-def.regenerated.txt:15` — 22 words. Each criterion's evidence command runs once on it, recording command, exit and output path; what cannot run goes under `Not provable now`.

3. `stage-def.regenerated.txt:21` — 16 words. Current design definition and acceptance criteria with reproducible evidence clauses; unresolved decisions identified for the user.

4. `stage-def.regenerated.txt:29` — 18 words. Required diagram defects or missing current-stage evidence block recommendation and gate preparation/presentation; honest unverified future checks do not.

5. `live/package/kc-dev-flow-2/skills/ideation/SKILL.md:15` — 17 words. Required inputs: the exact work item, recorded variant/profile, current stage, approved scope and the stage's available artifact/evidence.

6. `live/package/kc-dev-flow-2/skills/ideation/SKILL.md:29` — 24 words. Select the recorded row and read its shared profile principles first, then [stage principles](principles.md), then that row's stage reference and relevant adopted project learning.

7. `live/package/kc-dev-flow-2/references/profiles/pilot.md:10` — 11 words. Test owned behavior and real seams rather than stable vendor internals.

8. `live/package/kc-dev-flow-2/skills/ideation/principles.md:15` — 17 words. Use or repair what exists before adding a replacement; record the conclusion and observation in this design.

9. `live/package/kc-dev-flow-2/skills/implementation/principles.md:55` — 29 words. Before designing or coding a task, check what already exists in its own repository, the upstream packages/frameworks it depends on, relevant sibling projects and third-party tools it will use.

10. `live/package/kc-dev-flow-2/skills/implementation/principles.md:59` — 27 words. In the existing design or report, state what you checked, what you found, any inaccessible sources, and whether the proposed work uses, extends, changes or replaces it.

11. `live/package/kc-dev-flow-2/skills/ideation/principles.md:17` — 32 words. In `### Worth questions`, answer per scope part: which Captain words it serves; what breaks without it; which single premise would make the task unneeded and what cheap test checks it now.

12. `live/package/kc-dev-flow-2/skills/ideation/principles.md:18` — 13 words. Use one PRFAQ with a future-facing proposition, short FAQ and acceptance evidence plan.

13. `live/package/kc-dev-flow-2/skills/ideation/principles.md:31` — 15 words. Before reporting, run `python3 <package>/scripts/design_surfaces.py check <task>` and cite its output in the Stage Report.

14. `live/package/kc-dev-flow-2/skills/ideation/principles.md:33` — 64 words. The gate is not presentable without the artifact each recorded surface owes, or without a usable `## Acceptance criteria` section: the first line that equals that heading in any case once surrounding whitespace is trimmed, up to the next `## ` line, must hold at least one `**AC-<id>**` bold declaration, the grammar `spacedock status --read --ac-scan` reads; a `- AC-1:` list is not one.

15. `live/package/kc-dev-flow-2/skills/ideation/principles.md:41` — 20 words. Correct contradictions in depicted or required boundaries and missing current-stage evidence before reporting completion; if blocked, report the concrete gap.

16. `live/package/kc-dev-flow-2/skills/ideation/principles.md:43` — 6 words. Future implementation checks may remain unverified.

17. `live/package/kc-dev-flow-2/skills/ideation/principles.md:44` — 21 words. In the existing Stage Report checklist, name each acceptance criterion separately with its actual current evidence or an honest not-yet-verified statement.

18. `live/package/kc-dev-flow-2/skills/ideation/principles.md:45` — 18 words. A range such as AC-1..AC-3 is not per-criterion mapping; a future proof plan is not a passed result.

19. `live/package/kc-dev-flow-2/skills/ideation/profiles/pilot.md:3` — 18 words. Define the smallest useful end-to-end slice, who will use it, its real seams, acceptance evidence and explicit non-goals.

20. `live/package/kc-dev-flow-2/skills/ideation/profiles/pilot.md:9` — 29 words. Build the probe as the first paragraph of [POC implementation](../../implementation/profiles/poc.md) builds a proof: falsify the riskiest assumption first; when it holds, widen toward the slice and check the next.

21. `live/package/kc-dev-flow-2/skills/implementation/profiles/poc.md:3` — 15 words. Build the smallest real path that can falsify the recorded assumption within the accepted budget.

22. `live/package/kc-dev-flow-2/skills/implementation/profiles/poc.md:4` — 17 words. Record observed outcome, elapsed limit, primary evidence, cleanup and what the proof leaves unanswered; avoid production scaffolding.

23. `live/package/kc-dev-flow-2/skills/implementation/profiles/poc.md:6` — 11 words. Record `boundary-crossed:` as the shared profile defines it when it applies.

24. `live/package/kc-dev-flow-2/skills/ideation/profiles/pilot.md:11` — 27 words. Under `Probe:` in the design, record the branch, base and last commit and each hypothesis with its result; remove the worktree before reporting and keep the branch.

The sole direct command/exit/output requirement is entry 2 (22 words). Per-criterion report placement is separately requested as actual evidence in entry 17 (21 words), without those field names. The Pilot Probe record in entry 24 (27 words) calls for branch/base/commit/hypothesis/results. The POC first paragraph is 43 words total (entries 21–23); its 17-word evidence sentence asks for primary evidence, not the three-field ledger. These instructions do not formally exempt provenance, but do not join all of the required reporting details in one place either.

## Smallest proposed clarification — not applied

File: kc-dev-flow-2/references/sd/workflow.md, the existing proof sentence beginning on line 188 under ### ideation. Replace only that sentence, with no new instruction home, profile/criteria change, automation or added startup words.

Remove (22 words):

> Each criterion's evidence command runs once on it, recording command, exit and output path; what cannot run goes under `Not provable now`.

Add (22 words):

> For every criterion, including provenance, run its proof once; record command, exit and output path beside it; if unrunnable: `Not provable now`.

The exact line-preserving proposed diff is in proposed-wording.diff. The proposed text joins universal coverage, provenance, the single proof run, all three fields, per-criterion placement and the unrunnable case in one sentence. Whitespace counting gives 6099 before and 6099 after, so no budget raise or lint-budget step is proposed. This is a clarification to try, not a proven behavioral fix; the separately authorized repair and final one-worker validation remain with FO/Captain. No change was made to the candidate, product worktree or criteria.

## Separate evidence-preservation finding

The validator's cold-run dispatch.md, checklist.txt, scope.txt and fetched stage definition were not archived before its scratch close-out. The pack keeps hashes and a path to removed scratch; FO confirms no original copy exists (message 39fa730e-c8cf-4303-a91f-09ebddeac618). A validator or FO checking exactly what the model was given therefore cannot inspect those bytes after close-out, and this reconstruction recovers only part of them. This limits exhaustive input and causal claims; it is separate from candidate wording and F2's directly observed missing ledger. The close-out contract says to copy cited evidence into the task folder before removal (installed scratch.py notes_for); the helper's checksum manifest does not check that all cited inputs were retained. This investigation proposes no product repair for that preservation gap. The regenerated inputs, hash comparisons and regenerated stage are retained here, clearly labeled, so this investigation does not repeat the same archival omission.

## Captain amendment and handoff

Captain amendment 2 stands: the parent task's AC-3 evidence command is settled by the Captain, the statement stands, the budget is unchanged and one validation cycle remains. This investigation does not reopen F1, alter any acceptance criterion, change product bytes or run another worker. The validation-1 REJECTED verdict remains its original independent verdict. FO decides whether to authorize the proposed wording repair, then validation-2 can test that candidate once; a second rejection returns to the Captain as recorded.
