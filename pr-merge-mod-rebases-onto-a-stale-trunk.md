---
title: "The pr-merge mod's delivery step syncs the wrong branch and rebases onto a stale local trunk"
status: validation
source: Captain ruling 2026-09-14 in FO session, after the defect bit during PR #444 delivery
product: repo-platform
planning-window:
planning-outcome:
sprint: repo-platform/S2
sprint-readiness: ready
started: 2026-09-14T13:43:33Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-pr-merge-mod-rebases-onto-a-stale-trunk
issue:
pr: pr-merge:453
mod-block: merge:pr-merge
id: ab8tk40pm0t0wv2jpt7551d6
gates:
    version: 1
    records:
        - id: gate:ab8tk40pm0t0wv2jpt7551d6:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:ab8tk40pm0t0wv2jpt7551d6-backlog-1
              briefing:
                id: briefing:ab8tk40pm0t0wv2jpt7551d6:backlog:attempt-1:revision-1
                digest: sha256:b4b5fb22b6072ee06356a7bd5e709d025e922db6ad4926e0f41a7481f55c4c06
                room-ref: ./pr-merge-mod-rebases-onto-a-stale-trunk/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ab8tk40pm0t0wv2jpt7551d6:backlog:1
                briefing: briefing:ab8tk40pm0t0wv2jpt7551d6:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T13:43:03.714887Z"
                decision: approve
                reason: 'Captain said 派 for both ready items, after selecting POC and opening repo-platform/S2 for this one. The seed carries the problem with the observed PR #444 evidence, accepted outcome, non-goals, AC-1..AC-4 and the v3 POC receipt.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:ab8tk40pm0t0wv2jpt7551d6:validation
          stage: validation
          attempts:
            - id: gate-attempt:ab8tk40pm0t0wv2jpt7551d6-validation-1
              briefing:
                id: briefing:ab8tk40pm0t0wv2jpt7551d6:validation:attempt-1:revision-1
                digest: sha256:fce7c6cf644f5e38b3eb714d5de5695e486335d651eb80d1d568dd698f97b17e
                room-ref: ./pr-merge-mod-rebases-onto-a-stale-trunk/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ab8tk40pm0t0wv2jpt7551d6:validation:1
                briefing: briefing:ab8tk40pm0t0wv2jpt7551d6:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T14:18:10.709874Z"
                decision: approve
                reason: Captain approved at the validation gate. A fresh reviewer independently reproduced the mutation proof in both directions in its own sandbox, settled the re-pinned pr_merge_released_body.sha256 as repository-local with named evidence, and confirmed the package-owned extension block untouched. poc_outcome is proceed.
              application:
                target-stage: done
                state: pending
---

## The problem

`docs/dev/_mods/pr-merge.md` line 73 opens the on-approval delivery sequence with `git push origin
"$BASE"`, justified as pushing "the trunk to ensure the remote is up to date with local state
commits". That reason only holds for an inline workflow, where entity state lives on the trunk. This
workflow is split-root: its README declares `state: .spacedock-state`, and `spacedock state commit`
publishes to `spacedock-state/dev`. No state commit ever reaches `main`, so the step syncs nothing
the workflow owns while pushing whatever the local trunk happens to hold to a shared branch.

The same line then rebases with `git rebase "$BASE"`. `$BASE` comes from `spacedock dispatch trunk`,
which emits a bare branch name, so this rebases onto the **local** trunk ref rather than the fetched
remote one. Both defects were observed during the `retire-the-provider-backed-planning-path`
delivery on 2026-09-14: the trunk push was refused non-fast-forward because the local trunk was
stale, which is exactly the state in which the following line would have rebased the candidate onto
an old base and opened a pull request already behind the trunk. The First Officer deviated and
rebased onto `origin/main`, which is what surfaced three real conflicts; the literal sequence would
have deferred them to the merge on GitHub.

Line 73 sits before the `<!-- kc-dev-flow runtime extension:start -->` marker at line 119, so this
is the repository's own policy half of the mod, not the package-owned extension.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  basis: >-
    Kent selected POC on 2026-09-14. The correction is two lines of prose in this
    repository's own policy half of the mod; there is no design question a shape
    stage would answer. One thing is genuinely unproven: that the corrected
    sequence lands the candidate on the remote tip under the exact condition that
    bit during PR #444, a stale local trunk.
  route: [build, prove]
  obligations:
    architecture:
      - Change only the local half; the package-owned extension block is off limits.
    implementation:
      - Remove the trunk push, add the fetch, and name the remote-tracking ref in the rebase.
    testing:
      - AC-1 to AC-4, with AC-4 replayed against a deliberately stale local trunk.
  scope_boundary: >-
    The accepted outcome and complete non-goal list in this task remain unchanged.
    Excludes the extension block, the captain-approval guardrail, the local-merge
    fallback, and any other repository's mod.
  poc_decision: Whether the corrected delivery sequence is the one the pr-merge mod should carry.
  poc_falsifier: >-
    Mutation: set the local trunk deliberately behind the remote, replay the
    corrected sequence, and see whether the candidate still lands on the remote
    tip. The current sequence does not; if the corrected one also does not, the
    correction is wrong.
  poc_budget: One dispatch, and decision-ready inside 15 minutes — the same ceiling the Captain set for the other POC in this session on 2026-09-14, not a derived one.
  poc_stop_when: >-
    With the local trunk set behind the remote, the replayed sequence produces a
    candidate whose merge-base with origin/main equals origin/main's tip and
    `python3 scripts/kc-dev-flow-contract-test.py` exits 0 — or it does not, and
    the exact command output showing the stale base is recorded. Work stops at
    that observation whichever way it falls.
  poc_artifact: retained
  poc_safety_boundary: the local half of docs/dev/_mods/pr-merge.md, above the extension start marker
  poc_decision_ready_minutes: 15
  decision:
    authority: Kent (Captain)
    at: 2026-09-14T00:00:00Z
```

## Accepted outcome

The delivery sequence fetches the remote trunk and rebases the candidate onto it, and no longer
pushes the trunk. A reader of the mod cannot come away believing this workflow's state lives on the
trunk.

## Non-goals

- Editing anything between the `kc-dev-flow runtime extension` start and end markers.
- Weakening or moving the captain-approval guardrail that precedes the push.
- Changing the fall-back-to-local-merge clause.
- Changing any other repository's mod.

## Acceptance criteria

- **AC-1** The local half of `docs/dev/_mods/pr-merge.md` contains no `git push origin "$BASE"`, and
  no remaining sentence claims the trunk carries this workflow's state commits.
- **AC-2** The delivery sequence fetches before it rebases, and the rebase names the remote-tracking
  ref rather than the bare branch name.
- **AC-3** `python3 scripts/kc-dev-flow-contract-test.py` exits 0, proving the package-owned
  extension block is byte-identical after the edit.
- **AC-4** Replaying the corrected sequence by hand against a deliberately stale local trunk rebases
  the candidate onto the remote tip, shown by the resulting merge-base equalling `origin/main`.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names
the changed premise, affected acceptance evidence, and recommended change or stop.

## Stage Report: implementation

- DONE: Removed the local half's `git push origin "$BASE"` trunk push and its
  "up to date with local state commits" claim.
  `docs/dev/_mods/pr-merge.md` line 73, commit 88bb7eb9 on
  `spacedock-ensign/pr-merge-mod-rebases-onto-a-stale-trunk`.
- DONE: On-approval sequence now fetches `origin "$BASE"` and rebases onto
  `"origin/$BASE"` instead of the bare local ref.
  Same line; line 51's use-site list updated from "the push" to "the fetch".
- DONE: Package-owned extension block (lines 119-542, between the start/end
  markers) left byte-identical; only the pre-marker released body changed.
  `python3 scripts/kc-dev-flow-contract-test.py` exits 0 after re-pinning
  `kc-dev-flow/contract-manifest.json` `pr_merge_released_body.sha256` to
  `754856b5…` / 10607 bytes (was `ea187ab4…` / 10551), the byte delta the
  two-line edit produced.
- DONE: AC-4 mutation proof — built a throwaway bare remote + local clone,
  advanced the remote past the local's cached `origin/main` (staleness
  confirmed: pre-fetch `origin/main` == stale local `main`), then replayed
  both sequences from that identical stale starting point.
  OLD sequence (`git push origin "$BASE"` then `git rebase "$BASE"`): push
  rejected non-fast-forward ("Updates were rejected... fetch first"); rebase
  then no-ops onto the stale local ref; resulting
  `git merge-base feature origin/main` = `e7a7660…` != `origin/main` tip
  `8a09030…` — candidate stayed behind, reproducing the PR #444 defect.
  CORRECTED sequence (`git fetch origin "$BASE"` then
  `git rebase "origin/$BASE"`): fetch updates the tracking ref
  (`e7a7660..8a09030 main -> origin/main`), rebase replays `feature` onto it;
  resulting merge-base = `8a09030…` == `origin/main` tip — match.
- DONE: `poc_outcome: proceed` — the corrected sequence is the one the
  pr-merge mod should carry. Settling command output: the AC-4 mutation
  above (merge-base match for corrected, mismatch for old, from the same
  stale start) plus `python3 scripts/kc-dev-flow-contract-test.py` → PASS
  (exit 0).

### Summary

Two-line fix in `docs/dev/_mods/pr-merge.md`'s local half: the delivery
sequence no longer pushes the trunk or claims it carries this split-root
workflow's state, and it fetches before rebasing onto the remote-tracking
ref rather than the bare (local) branch name. Re-pinned the released-body
contract hash for the byte delta; extension block untouched.
Proven by mutation against a deliberately stale local trunk in a disposable
git sandbox, not by re-reading the prose.

## Stage Report: validation

- DONE: Re-ran the mutation proof myself in a fresh disposable sandbox
  (bare remote + two independent clones, one advancing `main` past the
  other's cached `origin/main` to reproduce the exact staleness condition).
  OLD sequence (`git push origin "$BASE"` then `git rebase "$BASE"`): push
  rejected non-fast-forward, rebase no-ops onto the stale cached ref,
  `git merge-base feature origin/main` = `03f1e73…` while the actual remote
  tip is `8b59ed7…` — mismatch, reproducing the PR #444 defect independent
  of the implementer's own run. CORRECTED sequence (`git fetch origin
  "$BASE"` then `git rebase "origin/$BASE"`), replayed from the same stale
  starting point in a second disposable sandbox: fetch updates
  `origin/main` (`9ed301d..4ec8cd8`), rebase replays onto it, resulting
  `git merge-base feature origin/main` = `4ec8cd8…` == the remote tip
  `4ec8cd8…` — match. Both directions shown, not read from the
  implementation report.
- DONE: `pr_merge_released_body.sha256` scope settled — it stays
  repository-local, does not propagate to adopters. Evidence: neither
  `kc-dev-flow/contract-manifest.json` nor
  `scripts/kc-dev-flow-contract-test.py` exists anywhere under the checked
  adopter worktrees (`subspace-v0/quebec-v1`, `carlove-v1/kyoto`); carlove's
  own `docs/dev/_mods/pr-merge.md` has no runtime-extension marker at all
  and a completely different on-approval sequence, so nothing currently
  syncs this file or its pin outward. The pinned pre-marker body is this
  repo's own dogfooded copy of the upstream Spacedock `pr-merge` release,
  vendored once at adopt time — not part of the extension block that
  `spacedock:refit` / `adopt-dev-flow` push to adopters. The script is
  classified `release-proof` (top-level `scripts/`, absent from
  `contract-manifest.json`'s own `resources` list), i.e. a pre-publish
  self-check kc-claude-plugins runs on itself, not a shipped runtime
  artifact.
- DONE: Extension-block byte-identity re-checked directly rather than
  trusting the implementation report's `python3
  scripts/kc-dev-flow-contract-test.py` run. Literal diff against the
  current `origin/main` tip (`0bbf6233`) shows the extension block
  differs — but only because `origin/main` advanced two unrelated commits
  (`da3f287f`, `58748d73`, a PR-title-refusal feature) past this branch's
  merge-base (`7b103a10`) after the branch forked; both `docs/dev/_mods/pr-merge.md`
  and `kc-dev-flow/references/pr-merge-extension.md` moved together on
  main, so the two files stay mutually consistent for anyone rebasing.
  Diffing the extension block between HEAD and the branch's own
  merge-base is byte-identical (empty diff), confirming this candidate's
  edit itself never touched the extension range; `python3
  scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate commit
  in this worktree, checked directly, not re-read. Residual: this branch
  needs an ordinary rebase onto current `origin/main` before delivery to
  pick up the unrelated title-refusal commits — routine pre-merge
  housekeeping, not a defect in this change.
- DONE: AC-1 and AC-2 re-checked by direct grep against the candidate
  file rather than the stage report's prose: no `git push origin "$BASE"`
  and no "up to date with local state commits" sentence remain anywhere
  in the file; the on-approval line now reads `git fetch origin "$BASE"`
  then `git rebase "origin/$BASE"`.

### Summary

Independently reproduced both directions of the AC-4 mutation proof in a
fresh sandbox (old sequence loses the rebase target under a stale local
trunk, corrected sequence lands on the remote tip), confirmed AC-1/AC-2 by
direct grep, confirmed AC-3 (contract test exits 0) at the candidate
commit, and settled the re-pinned hash's scope as repository-local — no
adopter currently vendors `contract-manifest.json` or the contract-test
script, and carlove's own mod file has already diverged past the point
where a shared pin could apply. The extension-block "byte-identical to
origin/main" check needed refinement: literal diff against the current tip
shows drift, but that drift is entirely from two unrelated commits that
landed on main after this branch forked, not from this edit — verified by
diffing the extension block against the branch's own merge-base instead,
which is empty. Recommend: proceed to delivery after an ordinary rebase
onto current `origin/main`.
