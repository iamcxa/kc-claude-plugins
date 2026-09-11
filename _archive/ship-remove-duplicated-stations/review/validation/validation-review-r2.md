# Validation gate review — ship-remove-duplicated-stations (feedback round 1)

## Question

Does PR #410 now address all four findings from the batch First Officer's
verification at e5c2df15, with a green required-check surface, ready for
Captain review?

## Candidate

- Branch: `spacedock-ensign/ship-remove-duplicated-stations`
- Candidate SHA: `af020cf4c6f80636af46834062d81cdae0f122fb`
- Draft PR: https://github.com/iamcxa/kc-claude-plugins/pull/410
- Required checks at this candidate: GitGuardian pass, multi-profile route gate
  pass, version parity pass — all three green (`gh pr checks 410`)

## Findings addressed

1. **Merge #406, not rebuild from stale main.** Real `git merge origin/main`
   (commit `4556588d`), origin/main's already-station-clean
   `docs/ship/README.md` kept whole on the sole conflict.
2. **Delete the stations `dispatch.sh` supersedes.** `fenced-dispatch.sh` (+
   test), `intent.sh`, `holder.sh`, `worker-transcript.sh`, their
   `references/stations/*.md`, fixtures, and `contract-test.py` cases removed;
   7 `placement.tsv` rows repointed to `residual`. `pin.py`, `e2e-gate.py`,
   `e2e-cli.sh`, `uat-doc.py`, `local-profile-check.py`,
   `parse-execute-external.py` untouched. Independently confirmed absent in a
   fresh clone.
3. **Wire `dispatch.test.sh`/`watch.test.sh` into `contract-test.py`.** Done,
   with one FO-authored deviation from the literal instruction: gated on
   `conductor` being on `PATH`, because the unconditional wiring the round
   literally asked for turned the real required CI check red (GitHub Actions
   has no Conductor CLI; verified directly from the failing CI run log before
   fixing). Named-skip, not silent pass, when absent.
4. **PR title/body per the `pr-merge` mod template.** Retitled to a bare
   Conventional Commit subject, no Linear id. Body rebuilt to motivation lead +
   `## What changed` (5 bullets) + `## Evidence` (N/N form) + `## Residuals`
   (3 bullets) + `## without-it unanswered` + `---` + the resolved-state-tuple
   audit link per the mod's Split-root audit-link correction.

## Independent verification (not taken on the ensign's word)

Fresh clone at `/tmp/validate-clone-r2`, candidate `af020cf4`: AC-1 grep clean,
AC-2 `prose-placement-check.py` PASS, AC-3 both scripts exit 0,
`kc-dev-flow-contract-test.py` PASS. Confirmed the four superseded stations
are absent from the clone. Confirmed `contract-test.py`'s conductor-skip guard
by stripping this sandbox's unrelated `conductor` binary from `PATH` and
observing the named skip line, then hitting only the pre-existing, previously
identified `e2e-gate ac2` sandbox gap (reproduced on unmodified `main`).
Confirmed real CI green directly via `gh pr checks 410` at this candidate.

## Recommend

Approve. All four batch-FO findings are addressed with independently
reproduced evidence; the one deviation from the literal round-2 instruction
(gating the test wiring on `conductor` presence) is disclosed with its
rationale and evidence, not silently applied. All three required CI checks
are green at the candidate SHA.
