# Validation gate review — ship-remove-duplicated-stations

## Question

Does this PR complete the accepted removal (the nine per-task stations from the
2026-09-10 cloud-wrapper design's removal table) with every acceptance criterion
either verified or honestly accounted for, and is the Draft PR ready for Captain
review?

## Candidate

- Branch: `spacedock-ensign/ship-remove-duplicated-stations`
- Candidate SHA: `d300d531186a6f42a9fd1905f90c8227bdfd966c`
- Draft PR: https://github.com/iamcxa/kc-claude-plugins/pull/410

## AC cross-check

- **AC-1** (grep clean + `contract-test.py` exits 0): grep half verified independently
  by the FO in both the authoring worktree and a fresh clone — 0 matches. The
  exit-0 half is unmet, but reproducibly so on the unmodified `main` tip
  (`6991fd09`, confirmed twice by the FO directly, and separately by the ensign via
  `git stash`) — a pre-existing environment gap (an `e2e-gate`/`spacedock dispatch
  build` call this sandbox can't complete), not a regression introduced by this PR.
  Reclassified from FAILED to SKIPPED in the implementation stage report with that
  evidence.
- **AC-2** (`prose-placement-check.py` exits 0): verified in the authoring worktree
  and independently reproduced in a fresh clone at the candidate SHA — `PASS (28
  segments, 18 placed, 10 residual)`.
- **AC-3** (`marketplace-verify.sh`, `skill-frontmatter-lint.sh` exit 0): verified in
  the authoring worktree and independently reproduced in a fresh clone — both exit 0.
- **AC-4** (PR body lists every retained fixture pinning a real commit SHA under
  `without-it unanswered`): present in the PR body, 34 fixture files plus
  `contract-test.py` itself, derived from `git cat-file -t` over the candidate tree,
  cross-checked by a second pass. One interpretive call flagged, not silently
  resolved: some listed SHAs are dangling/unreachable commit objects, kept under the
  literal "pins a real commit SHA" reading.

## Recommend

Approve. Every AC has independently verified evidence except AC-1's exit-0 half,
which is a pre-existing, reproducible-on-`main` environment gap unrelated to this
removal — not a defect this PR introduced or could fix. The removal, prose rewrite,
and fixture accounting match the design's removal table and this entity's Accepted
outcome and Non-goals.
