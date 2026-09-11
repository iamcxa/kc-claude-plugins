# Independent local validation

Verdict: PASS for the exact local two-file candidate. No scoped product finding requires a correction. This is one fresh existing-host review, not delivery acceptance or native task closure.

Base: `0ec3380f590cbaf5b01ee1c325eb222da99a3c5a`. Exact `git diff --binary <base>` SHA256: `c1d7ed2b15b237450dea31c6ca1de0fb288986d49516b311d544560d83cdd21c`. Product candidate commit: unavailable because it remains uncommitted. Only `kc-dev-flow/scripts/surface-map-check.py` and `scripts/kc-dev-flow-contract-test.py` differ: 48 additions plus 2 deletions. The checker needs the one suffix addition; six new contract scenarios protect that behavior and its boundaries. The timeout change bounds the existing checker subprocess; no dependency, CI configuration or unrelated product scope was added.

## Observed behavior — AC-2, AC-4

`independent-results.json` retains Python executable/version, exact variant hashes, real fixture commit identities, evidence contents, all 34 command stdout/stderr/exit records, and 11 discriminating checks. Independently generated fixture commits are evidence inputs only. The exact producer fixture was additionally rerun with the frozen baseline and candidate: default exit 1→0 on unchanged fixture objects. Product diff hash is checked both before and after.

- Candidate excludes only the new Go test suffix in this case; strict mode still reports the missing mapping.
- Explicit unknown acceptance target and unbound stub commands return failure; a valid explicit mapping checks one file.
- Ordinary `task.go`, `contest.go`, and suffix-lookalike `task_test.go.bak` remain checked.
- Frozen baseline reproduces the selected failure. A deliberately overbroad `.go` copy and a deliberately bypassed explicit-map copy return incorrect success on their discriminating cases; the reviewer identifies these as defective, never ready.
- Producer's retained actual contract-section runs were inspected: old checker fails the new default-exclusion assertion, candidate passes, and overbroad checker fails the ordinary-Go assertion. The independent reviewer used a separately authored behavior harness; unrelated suites were not rerun.

Reproduce with Python 3.11+ and Git: `python3 <worktree>/.context/independent-go-review/review.py <worktree> <entity>/validation-evidence/local-go-test-exclusion`. A copy of the executed harness is retained as `reproduce.py`; first copy it into that worktree-local scratch path if absent. It reads the producer's retained fixture/evidence and creates disposable fixtures under the assigned worktree, retaining their paths. If the producer fixture is no longer present, exact-producer-fixture replay is unavailable; fresh independent cases still have retained raw results. This is a declared local evidence composition, not an installed runner. Each subprocess has 60 seconds and no automatic retry. One initial successful run was repeated only after making scratch-fixture allocation safe for reruns; it was not an additional case or repair loop.

## Selection and duplicate limits — AC-1

Raw `implementation-evidence/local-go-test-exclusion/queue.json` contains successful PR listing, complete empty review/thread pages and empty general-comment arrays for the three eligible kc-dev-flow PRs at captured heads; the other open PR titles were disposed as unrelated plugins or a broad release. Four issue bodies and dispositions support the narrower existing finding selection. This is historical captured queue evidence, not a claim about present GitHub state; reviewer made no external request.

`selection.json` binds one stable finding identity and existing owner, and records refusal of a second identical manual input with no duplicate launch. AC-1 is met only at the accepted single manual-session level: one selected case, explicit manual owner check, zero automatic retries. This is an operator decision record rather than an executable selector/launch trace; durable, concurrent or unattended deduplication is unproved. No scheduler assurance or automated duplicate test is claimed.

## Actor accounting and remaining limits — AC-3, AC-5

Producer-time `usage.json` remains historical and untouched. The independent reviewer has now run; reviewer input, cached input, output and reasoning are all unknown because no unique attributable usage source is exposed. Inherited root thread identity was not attributed to this worker. The first-officer snapshot remains attributed partial coordination usage, not the first officer's final total or whole-cycle cost. Other workers remain unknown. Cached input is a subset of input; reasoning is a subset of output. No complete cost, efficiency improvement or measured hard cost cap is supported.

Optional separate-model/provider observation and precommit product-object-based mapping remain unavailable, not passing. No new provider/runtime/cloud call, product modification/commit/push, external post, PR, installation, merge, upstream or stopped-tree access occurred. No CI configuration changed; per-PR CI cost was not measured. Exact-file product approval remains Captain-owned. Original/native knowledge terminalization, archive, cleanup and final check remain incomplete and separately owned. Current task state, gates, pins and historical Briefing authority were not edited or consumed; this report cannot terminalize them.
