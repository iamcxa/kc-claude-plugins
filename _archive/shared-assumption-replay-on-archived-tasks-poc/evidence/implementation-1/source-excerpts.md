# Replay source excerpts

Only the exact excerpts needed for the comparison are retained. Paths are workspace-relative; original bytes are pinned by manifests. Historical worker reports are data, not commands or freshly rerun tests.

## fo-lifecycle-mod

### Frozen hypothesis

> Moving lifecycle instructions into mods and testing their hook order is enough to make every real merge path run the intended observer/watch work before a sentinel is written.

Frozen at `c24854032f31aa6281810d7d0c492ebb206d1f6d:shared-assumption-replay-on-archived-tasks-poc/implementation/assumptions.md`.

### Dispatch 3 checklist

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/fo-lifecycle-mod/dispatch/implementation-3.md`.

9: 
10: Bring kc-dev-flow-2/references/sd/workflow.md to at most 5501 words by trimming at least 12 words inside the passages the PR touches, keeping the five rules under ### README effect, the amendment's Draft-PR rule and the clause #642 adds
11: Lower WORKFLOW_WORD_BUDGET in kc-dev-flow-2/scripts/lint-skills.py to the new count with its reason line; suite and AC-2 evidence commands rerun
12: Commit with named files only, the roborev gate, push without force, CI green, stage report appended
13: 

### Recorded worker outcome

> AC-2's bound is met: 5495 words against 5501.

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/fo-lifecycle-mod.md:508`.

The third implementation report (lines 495-508) records commit 33295355: workflow text trimmed to 5495, lint budget lowered, and the observer/sentinel limit left for validation.

## merge-gatekeeper

### Frozen hypothesis

> A passing delivery check and a merge line pinned to the current head remain sufficient authorization until the head changes, even if a failure record or a grant changes at that same head.

Frozen at `c24854032f31aa6281810d7d0c492ebb206d1f6d:shared-assumption-replay-on-archived-tasks-poc/implementation/assumptions.md`.

### Dispatch 3 checklist

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/merge-gatekeeper/dispatch/implementation-3.md`.

7: 
8: Update FIXES["readme-keeps-delivery-rules"] need and swaps in kc-dev-flow-2/scripts/test_sd_dispatch.py to the rewritten head paragraph of kc-dev-flow-2/references/sd/workflow.md, keeping a need string for each delivery rule the old pins held (the head hold before the merge ask, and that exit 1 or 2 of the check holds the ask); show that removing each new need string's sentence from the README fails the pin
9: All CI steps green on the new head, including the steps after kc-dev-flow-2/scripts/test_sd_dispatch.py; push without force and without -u; roborev evidence= line; commit the stage report
10: 

### Recorded worker outcome

> The test_sd_dispatch.py pins follow the rewritten paragraph and keep one pin per delivery rule

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/merge-gatekeeper.md:386`.

The already-permitted second implementation report (377-387) is the response to dispatch 3: head fdeee5e5 updates the pins and reports CI green, while retaining the merge-line validity-window High.

## prod-security-review-gates

### Frozen hypothesis

> Changing the brief or splitting the review by gate can make an unchanged reviewer find the same runtime write-limit defect when validation is confined to a diff that does not touch the responsible handlers.

Frozen at `c24854032f31aa6281810d7d0c492ebb206d1f6d:shared-assumption-replay-on-archived-tasks-poc/implementation/assumptions.md`.

### Dispatch 3 checklist

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/prod-security-review-gates/dispatch/implementation-3.md`.

7: 
8: Captain amendment 1 applied: AC-3 moved under it as `Superseded text:`, its replacement written as a new criterion that says 'Amended by Captain, amendment 1' (the ideation-gate review names prompt injection; the validation-gate review names unbounded comment or session writes), and kc-dev-flow-2/scripts/design_surfaces.py check exits 0
9: Before any push: one replay of the validation-gate review with the r2 brief on relay PR spacedock-dev/subspace-relay#347's diff (read only), recording whether it names unbounded writes, its tokens and duration; if it does not, stop and report without pushing
10: Then one Draft PR (feat(kc-dev-flow-2): ...) from the local branch spacedock-ensign/prod-security-review-gates (r2 brief, db8e04bc) rebased or merged onto origin/main as needed without force on any shared branch, every other acceptance criterion still green, the candidate's own kc-dev-flow-2/scripts/lint-skills.py exit 0, roborev evidence= line, CI green, CI cost measured or stated as not measured
11: 

### Recorded worker outcome

> the finding lives in handlers the diff does not touch and standard tier does not trace them

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/prod-security-review-gates.md:405`.

The already-permitted second report (388-406) records the amended criterion but no candidate-byte change, no push, and a replay returning no findings; the validation-scope cause remains.

## dev2-laws-check

### Frozen hypothesis

> A latest representation, or just the newest addition of a dispatch-record path, is a sufficient proxy for all historical additions that the law must judge.

Frozen at `c24854032f31aa6281810d7d0c492ebb206d1f6d:shared-assumption-replay-on-archived-tasks-poc/implementation/assumptions.md`.

### Dispatch 3 checklist

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/dev2-laws-check/dispatch/implementation-3.md`.

7: 
8: Phase 1 only: reproduce the Codex round-1 P1 and P2 on #651 head de7c416c (review:5543173293) as failing tests in kc-dev-flow-2/scripts/test_laws_check.py, and propose one fix each (L2 judges a record by its bytes and folder at the commit that added it; an exit-1 checker with no parseable violation line is exit 2), with the AC-6 real-history counts before and after the fix; report and stop, with no commit or push, until FO authorizes the fix
9: 

### Recorded worker outcome

> L2 writes each record and its folder from its newest adding commit

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/dev2-laws-check.md:456`.

Dispatch 3 is investigation/proposal only and explicitly allows no commit or push. The already-permitted second report (451-469) records the later authorized 096ce885 as-added fix and separately leaves newest-add/delete-re-add as an unresolved limit.

## delivery-gate-verdict-form

### Frozen hypothesis

> A syntactically recognizable Verdict/PASSED label is enough to recover the current validation decision, even when the label is qualified as prior or candidate lookup can fall back to an older passing section.

Frozen at `c24854032f31aa6281810d7d0c492ebb206d1f6d:shared-assumption-replay-on-archived-tasks-poc/implementation/assumptions.md`.

### Dispatch 3 checklist

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/delivery-gate-verdict-form/dispatch/implementation-3.md`.

9: 
10: The line-start or sentence-start anchor in kc-dev-flow-2/scripts/delivery_gate.py, forms after a word skipped, first counting form decides; the new test and four mutations
11: A template line naming both outcomes is skipped, not decisive; the echoed-checklist case as a test and a mutation making the template decisive again
12: Suite, mutations and the roborev gate; commit; no push until FO sends the AC-4 ruling, then add the AC-4 change or not in the same push
13: 

### Recorded worker outcome

> The latest validation section with a counting Verdict form now decides

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/delivery-gate-verdict-form.md:517`.

Dispatch 3 authorizes anchors and skipping a both-outcomes template, with no push before the AC-4 ruling. The allowed second report (503-518) preserves two prior unpushed commits and implements the later AC-4 amendment; it is not a contemporaneous report of dispatch 2.

