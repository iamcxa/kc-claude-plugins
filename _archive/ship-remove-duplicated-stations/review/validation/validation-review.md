# Validation gate review — ship-remove-duplicated-stations

## Question

Does this PR complete the accepted removal (the nine per-task stations from the
2026-09-10 cloud-wrapper design's removal table) with every acceptance criterion
either verified or honestly accounted for, and is the Draft PR ready for Captain
review?

## Candidate

- Branch: `spacedock-ensign/ship-remove-duplicated-stations`
- Candidate SHA: `e5c2df15dbae6b829f4dc832db0e4e99966f1ee0`
- Draft PR: https://github.com/iamcxa/kc-claude-plugins/pull/410 (title/body conform to the `pr-merge` mod template; no Linear reference, per this sprint's ruling)
- Required checks: GitGuardian, multi-profile route gate, and version parity — all green at the candidate SHA

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

## Ship FO's four-item answer (2026-09-10), addressed in order

1. Backlog gate's git-root reference recovered from `spacedock-state/dev-recovery-9826ffcf`
   (fetched, not edited); gate record left untouched as instructed.
2. `version parity` required check was failing; reproduced with
   `scripts/kc-dev-flow-contract-test.py`, root-caused to a stale close-receipt hash
   chain from this PR's own body edit, fixed and pushed (`69d99d25`); a second,
   independent break in the same CI job (`kc-ship-flow/scripts/contract-test.py`'s
   placement.tsv mutation fixture pointing at a row this PR turned residual) was
   found and fixed the same way (`e5c2df15`). All three required checks are green
   at the candidate SHA above.
3. PR title retitled to a bare Conventional Commit subject, `(DEV-157)` dropped; no
   Linear reference anywhere in the PR.
4. PR body rebuilt to the `pr-merge` mod's exact template shape (motivation lead,
   `## What changed`, `## Evidence 5/5`, `---`, audit link), `without-it unanswered`
   kept verbatim, "Review guidance" and "Native stack exception" dropped/folded.

## Recommend

Approve. Every AC has independently verified evidence except AC-1's exit-0 half,
which is a pre-existing, reproducible-on-`main` environment gap unrelated to this
removal — not a defect this PR introduced or could fix. The removal, prose rewrite,
and fixture accounting match the design's removal table and this entity's Accepted
outcome and Non-goals, and the Draft PR now carries a green required-check surface
and a template-conformant title/body.
