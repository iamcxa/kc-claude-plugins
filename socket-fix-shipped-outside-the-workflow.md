---
id: 4j3cvgz8tman49xbz0afz451
title: "A browser-runtime defect fix shipped without an entity or a validation stage"
status: backlog
source: "self-reported process breach, 2026-08-01 — PR #135"
product: repo-platform
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design:
lane:
---

## Problem

PR #135 (socket namespace sized against the session-named socket) was found, fixed,
reviewed and merged during a session that had not loaded `docs/dev/README.md`. It never
existed as an entity, so it skipped backlog capture, the Defect-lane classification and its
four required outputs, the `validation` stage, and the evidence block.

What the change does have: RED-before-GREEN with observed RED, 949 tests / 948 pass locally,
real-runtime verification against agent-browser 0.32.0, and a fresh-context
`ship-flow:science-officer-em` verdict that independently re-derived the byte counts, re-ran
the suite, swept session lengths 1..90, and ran 200k truncation-collision trials.

What it does not have, and is owed by the contract:

- `Cross-model:` — never `N/A` under the validation clause, and it was not run against this
  diff. The EM pass is Claude, the same vendor as the session, so it does not satisfy the
  cross-vendor requirement.
- `Adversarial:` — no claim-breaking edit was made against the new budget.
- `Lenses:` — the diff touches socket and namespace lifecycle, so `resource-lifecycle`
  should have fired; no reviewer agent ran.
- `Diff coverage:` — `bin/e2e-browser-runtime.js` is an executable surface, so the 85%
  diff-coverage bar applies and was not measured.

`E2E:` is the one line that is satisfied: the fix was exercised by opening a real browser
and reading the resulting socket path off disk.

**What is exposed.** Four validation gates went unrun on code that is already on `main`,
and the sibling seed [[e2e-pipeline-suite-has-no-ci-job]] establishes that no CI job runs
this plugin's suite either. Two independent safety nets are absent on the same surface at
the same time, so nothing downstream is positioned to catch what those gates would have.

**Not retro-filed as a `done` entity.** The product-delivery route requires an authenticated
`pr_artifact_v1` hashing to the digest in a `pr-merge:product-pr:v1:{digest}` `mod-block`;
#135 never entered that chain, and that chain cannot be reconstructed honestly after the
fact. This seed is the record instead.

That is not the only route the contract names, which is why the choice is the captain's and
not the FO's. `done` also documents a `pr=direct-commit:{sha}` form that "never invents an
artifact field" and takes a read-only terminal route requiring only that the commit be
reachable from current `origin/main` — `27bff48` is, and the form is in live use elsewhere
on this state branch today (`absolute-claims-need-an-enforcement-point.md`). Two reasons it
may still be wrong here: the schema calls it "historically" that form and `done` frames it
as *historical* tasks, which reads as legacy read-support rather than a route to newly
adopt; and #135 is a merged PR with a merge commit, not a direct commit, so using it would
stretch the form's meaning.

Captain decides among: collect the owed evidence against the merged commit, accept the
breach on record, or rule that `direct-commit:{sha}` may be adopted for this case.
