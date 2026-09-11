# Validation gate review — ship-remove-duplicated-stations (feedback round 2)

## Question

Does PR #410 now address all four findings from the batch First Officer's
verification at af020cf4 (skill rename, stale instructions, design-doc
reference, and the #411 merge), with a green required-check surface, ready
for Captain review?

## Candidate

- Branch: `spacedock-ensign/ship-remove-duplicated-stations`
- Candidate SHA: `375315e1` (real two-parent merge of this branch and #411's
  `c1564b21` at merge commit `75883772`, plus one follow-up commit)
- Draft PR: https://github.com/iamcxa/kc-claude-plugins/pull/410
- Required checks at this candidate: GitGuardian, multi-profile route gate,
  and version parity all green (`gh pr checks 410`)

## Findings addressed

1. **Skill renamed.** `kc-ship-flow/skills/first-officer/` -> `run-batch/`,
   frontmatter `name: run-batch`, no collision with Spacedock's own
   `first-officer` skill. Every reference (`docs/ship/README.md`,
   `local-profile-check.py` docstring) updated; `kernel.md`/`placement.tsv`/
   `contract-test.py` never actually named the old skill path (checked, not
   assumed). `skill-frontmatter-lint.sh` stays green.
2. **Stale instructions removed.** The per-station `pin.py write/check
   --station` lines, the plan-receipt-argument `e2e-gate.py` invocation, and
   the `docs/plan-flow/schema/validate-receipt.py` reference are all gone
   from the renamed skill; it now states only what the surviving scripts do.
3. **Design-doc reference fixed.** Now points at
   `docs/dev/.spacedock-state/ship-cloud-dispatch-and-watch/design/2026-09-10-ship-flow-cloud-wrapper-design.md`
   on `spacedock-state/dev`, confirmed to exist there.
4. **#411 merged.** Real `git merge` (not rebase) of `origin/main` after
   #411 landed; `contract-test.py` and `uat-doc.test.py` conflicts resolved
   keeping #411's new `close.py`/v2 cases together with this PR's own
   station deletions. One additional overlap (a stale legacy-compat comment
   in the auto-merged `uat-doc.py` naming already-removed stations) was
   caught and fixed on the same pass, not left for a future round.

## Independent verification (not taken on the ensign's word)

Fresh clone refreshed to `375315e1`: AC-1 grep clean, AC-2/AC-3 pass,
`kc-dev-flow-contract-test.py` PASS. Confirmed the skill directory rename,
the absence of the three stale instruction lines, and the corrected
design-doc path directly in the file tree. Confirmed the merge is real via
`git log --graph`'s two-parent commit. Independently re-ran the full
`git cat-file -t`-over-hex-strings AC-4 scan (not reused from either
implementation report) and caught one real discrepancy: the earlier scans
undercounted by missing abbreviated (7-40 char) commit hashes, and the PR
body carried one stale line claiming `contract-test.py` itself pinned a real
SHA, which no longer resolves as a git object at this candidate — corrected
both the count (34, unchanged) and the PR body.

## Recommend

Approve. All four round-2 findings are addressed with independently
reproduced evidence; the FO's own AC-4 recount correction is disclosed with
its method and result, not silently applied. All three required CI checks
are green at the final candidate.
