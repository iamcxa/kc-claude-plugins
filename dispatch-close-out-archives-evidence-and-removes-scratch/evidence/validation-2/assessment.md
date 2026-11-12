# Independent validation 2

Verdict: **PASSED** for candidate `d4fe39e54dc7069b099d61c4b0e3fa2e5aecd8c6`
of Draft PR 854, base `8ce0eb6050c889b21baccf50fec35231bc888d66`.
This is pre-release candidate validation, not the Captain's gate decision,
merge, release, adoption or completed task stop condition.
Start: 2026-11-12 19:13:04 Asia/Taipei. End is recorded in cleanup.json and the final report.

## Identity and scope

`candidate-files.json` checks the seven changed files byte-for-byte against the
Git candidate. The code worktree stays clean on the assigned branch. The repair
above `223dbb6d1b5e895a45d11537b9494aa08610c8f8` changes only scratch.py's
instruction and test_dispatch_stage.py/test_scratch.py regression tests; cleanup
logic, other product files, versions, CI triggers and workflow README are unchanged.
`pr-live.json` independently confirms the open Draft PR at the candidate.
All execution used exports or installed package checks; Git-bound checks read
the pinned code worktree. No product commit, product push, PR comment or review request.

## Criteria and falsifiers

| Criterion | Reproduced observation | Falsifier run |
| --- | --- | --- |
| AC-1 | `ac1-grep.log`: exact grep returns 1 with exit 0 on the native generated record; replay retains both record and native artifact | Removing the paragraph makes the record count 0 and the test fail (`mutations/AC1-paragraph-removed.log`) |
| AC-2 | `ac2.log`: removed report path exits 0 without S4; identical missing FO-message path exits 1 with S4 | Reintroducing report scanning fails the report case (`mutations/AC2-reports-scanned.log`) |
| AC-4 | Exact named unittest exits 0 (`ac4.log`); actual CLI replay leaves own registration count 0 and peer registration count 1, preserving its dirty file (`replay/replay.json`) | Skipping own worktree removal leaves count 1; deleting the peer removes its asserted file (`mutations/AC4-*.log`) |

## Earlier findings, independently resolved

- F1, previously Material, **kind: build**, fixed. The released maintainer's normal
  package-built dispatch exposed the archive instruction to a worker. Its omitted
  blanket exclusion risked publishing private-repository evidence; protected
  boundary: `captain-ruling[2026-11-12]` D3 forbids all such evidence. The prior
  native build fails the new regression assertion (`privacy-previous-native.log`),
  while this candidate's native record/artifact contains the whole private
  repository, secrets, personal-data and reproduction rule (`replay/`). Removing
  only the private-repository phrase fails again. No actual private disclosure
  is claimed. The old standalone probe's secrets matcher only recognizes the old
  wording; its false secrets field on the repaired wording is not verdict evidence.
- F2, previously Needs decision, **kind: aim or scope**, resolved by amendment 2.
  The normal two-dispatch case correctly leaves the other dispatch registered;
  global zero would require deleting another worker's files. Protected boundary:
  `captain-ruling[2026-11-12]` owned-root deletion and former `value-ac[AC-3]`.
  `amendment-proof.json` compares the previous task version: AC-3 moved verbatim,
  AC-4 uses the exact requirement in the bound Asked text, AC-1/AC-2 and Design
  are unchanged. The replay matches that requirement without broadening deletion.

No new rejection finding. F1's earlier evidence and F2's conflict are reproduced,
not accepted on either author's authority. Scope/design remain the Captain's;
there is no new private-evidence scanner or additional product policy.

Goal sufficiency is demonstrated at the pilot's bounded seams: native dispatch,
actual close, committed restore, and peer survival. Minimal necessity follows the
same route: the dispatch paragraph supplies AC-1; scratch.py owns restoration and
bounded deletion; pr_watch.py supplies the approved fallback for ended roots;
the tests detect their removal and the ownership safety loss. ADR 0079 is expressly
required by amendment 1. AC-2 already passes unchanged, so delivery_gate.py was
correctly left outside the diff. No retained production surface lacks a named goal
or safety purpose.

## Design checks formerly not provable

- Dispatch refusal: native tests reject outside /tmp paths before record/build;
  removing the refusal makes the negative test fail.
- Close refusals: missing record, mismatched derived root, traversal, symlink root
  and parent, and foreign ownership preserve their sentinels in the scratch suite.
  The symlink mutation is killed by a changed diagnostic because ownership still
  refuses it; it does not demonstrate that one removed guard alone loses data.
- Close/compression: own dirty registered checkout is removed with file counts;
  outside/peer registrations survive. 256 KiB stays plain, larger evidence gzips,
  the 1 MiB retained cap refuses cleanup, repeat close preserves manifest/log.
- Restore: native CLI replay commits synthetic gzip and restores matching bytes;
  truncated gzip is rejected. `implementation-restore.json` independently restores
  all 146 manifested implementation files from the fetched state ref. Own committed
  evidence restoration is recorded separately after the evidence commit.
- Post-archive: the real observer checker and learning prompt results stay identical
  before/after a committed synthetic scratch-removed.txt (`watch.json`).
- Idle: old and archived roots prompt cleanup, current/unknown roots survive;
  merged cleanup precedes merge recording. This is controlled CLI behavior, not
  evidence that every human/agent follows the prompt.
- Words: `word-budget.json` records 52 worker prose words (54 including Scratch
  line) against ceiling 66, and 20 emitted idle words against ceiling 21.
  No startup/workflow text change.
- Post-release real-task stop condition: **unverified**, because this candidate
  is an open Draft PR. FO retains the release/adopter check and delivery decision.

## Other repair and required checks

Same-basename repositories and same-origin clones retain different namespaces
and peer uncommitted files (`collision/results.json`); ownership refusal mutations
also fail. The namespace is `<origin-name>-<16-hex identity>`, the prior disclosed
safety refinement of the design's `<repo>` placeholder. No change this cycle.
The basename-only mutation is blocked by ownership during the setup; it does not
claim an observed private loss. Actual candidate collision runs both succeed.

`required-checks.json` records seven local checks, all exit 0. The first number
guard run warns that sandbox fetch failed; `number-guards-live.log` is the exact
fresh-ref rerun with no warning, also exit 0. ADR lint was:
`python3 <declared 0.39.1 package>/scripts/adr_lint.py docs/adr --since 8ce0eb6050c889b21baccf50fec35231bc888d66 --require 0079`.
ADR 0079 records only the approved D1-D4 under amendment 1. The five added comments
were read; all are required decision pointers/import lint annotation. Comment
ratio is 0.9%, below 5% (`comment-ratio.log`). `doc-impact.log` lists ADRs 0070,
0074 and 0077 as reviewed: their writer, role, model and budget rules remain
unchanged; 0079 is the updated record. No additional affected document is omitted.
CI cost per PR was not measured; no CI trigger changed. Hosted CI/local RoboRev
were not rerun by this validator and are not claimed clean.

## Counts, raw failures and limits

`tests.json` has 338 distinct passing tests: 50 dispatch, 152 watch/cleanup
(including the 13 scratch tests), 136 dispatch-record tests. The initially
skipped real-builder test was rerun with the declared Spacedock plugin root
and passed (`records-native.json`); standalone scratch reruns are not double-counted.
`mutations.json` has 16 rejected changes; logs above distinguish assertion failures
from defense-in-depth refusals. Each live AC has a direct behavior falsifier.

Unmodified /tmp-export dispatch tests are **not** green: 50 tests recorded 78
failure events and 3 errors because the fixture itself supplies a forbidden
Package root under /tmp (`dispatch-native.log`). The disclosed existing adapter
changes only three fixture input strings, never assertions/product bytes; the
adapted suite passes. Python 3.15 additionally needs module import metadata in the
acceptance adapter, documented with the preserved initial failure. There is no
claim of unchanged raw-export acceptance or arbitrary worker privacy compliance.

`acceptance.md` and `acceptance.sh` give the five exact fresh-Bash steps, observed
in `captain-verified.log`, including cleanup; 20 results pass. Earlier exploratory
runs are retained and not counted as extra acceptance coverage. Only synthetic
and public evidence was accessed/archived. Cleanup roots and exact removals are
recorded separately; no /tmp copy is retained as evidence.
