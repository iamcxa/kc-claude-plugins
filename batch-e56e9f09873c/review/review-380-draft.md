## PR #380 — feat(ship-flow): generate the batch UAT document and send one idempotent Slack ping

**What this PR changes:** `uat-doc.py` renders one UAT document from a batch directory's receipts, README decisions list, and Evidence blocks; `notify.sh` records one message per batch id under a state dir — dry-run only, no real send path; fixtures copy two real batch records; README paragraph.
**Why (per author):** DEV-106 — the Captain's day ends with one document and one message.
**Claimed goal:** DEV-106 AC-1..AC-4. **Linked issue:** DEV-106.
**Goal-achievement verdict:** ❌ Not achieved for the message half — `notify.sh` has no real-send path by design of the dispatch (the FO forbade sending during the build and no channel or credential was ever specified); ⚠️ Partially for the document — headings and PR set match the hand-written reference, but the document can vanish an issue and still say "none stuck", and it stamps worker self-reports as FO-verified.

Tier: Lite (320 non-fixture lines) + ToB. Agents: code-reviewer, silent-failure-hunter, comment-analyzer, tob-security-reviewer. Head dea62ed6 unchanged.

### Inline Comments (CODE)
| # | File:Line | Severity | Conf | Category | Summary |
|---|---|---|---|---|---|
| 1 | scripts/ship-flow/uat-doc.py:161-167 | HIGH | 6/10 | security | Worker-controlled `BRANCH`/`CANDIDATE_SHA` are interpolated unescaped into backtick spans; a value containing `` ` `` and `[text](url)` breaks out and plants a link in the document the Captain reads to decide merges (ToB PoC). Reject non-ref-safe characters or escape. |
| 2 | scripts/ship-flow/uat-doc.py:159-174,199-224 | CRITICAL | 10/10 | correctness | An issue with no Evidence file and no close-receipt entry renders an empty layer and the summary asserts `none stuck.` (FO reproduced with a synthetic DEV-999). A false negative in the one artifact meant to let the Captain ask nothing. |
| 3 | scripts/ship-flow/uat-doc.py:178-181 | HIGH | 8/10 | correctness | `contract test PASS` and "FO ran verbatim" are rendered from the worker's own `TESTS` / `WITHOUT_IT_OBSERVED` fields; nothing FO-sourced feeds them. Relabel as worker self-report or source from the close receipt. |
| 4 | scripts/ship-flow/uat-doc.py:161,164-167 | HIGH | 9/10 | correctness | MULTI-SOURCE: code-reviewer + silent-failure — a missing Evidence file renders literal `None` with a confident `(main)` base label; `base_label()` cannot distinguish "main" from "never recorded". |
| 5 | scripts/ship-flow/uat-doc.py:161 | MEDIUM | 8/10 | correctness | `close_issue.get("candidate") and worker.get("BRANCH") or worker.get("BRANCH")` always yields `worker.get("BRANCH")`; the intent is not implemented. |
| 6 | scripts/ship-flow/uat-doc.py:156 | MEDIUM | 7/10 | security | A receipt-sourced string with an embedded newline (issue title) forges a second `## For the Captain` section (ToB PoC). Single-line-normalize every external string before rendering. |
| 7 | scripts/ship-flow/uat-doc.py:62-73 | MEDIUM | 8/10 | correctness | MULTI-SOURCE: code-reviewer + silent-failure — decisions parser keeps only lines starting with `- `; `*` bullets, indented sub-bullets, and wrapped lines are dropped silently while the trailer count stays self-consistent. |
| 8 | scripts/ship-flow/uat-doc.py:14,25-29 | MEDIUM | 8/10 | docs | MULTI-SOURCE: 3 agents — docstring promises exit 2 for a missing receipt; malformed JSON or a missing key exits 1 with a traceback. |
| 9 | scripts/ship-flow/notify.sh:2-8,32-42 | MEDIUM | 7/10 | docs | MULTI-SOURCE: code-reviewer + comment-analyzer — "sends exactly one message" is a check-then-act on marker existence (two parallel runs both print "sent"); the absolute names no enforcement point; and a dry-run marker will block a future real send. |
| 10 | scripts/ship-flow/uat-doc.py:55 | LOW | 7/10 | correctness | `worker-evidence-{issue}*.md` is an unanchored prefix: DEV-9 matches DEV-90's file. |
| 11 | scripts/fixtures/ship-flow/uat-doc/…/uat.md.reference | MEDIUM | 7/10 | test-coverage | MULTI-SOURCE: comment-analyzer + silent-failure + ToB — the reference has no reader and already diverges in 9 hunks; neither script is referenced by the contract test or CI. |

### Advisory (DOC/NEW) — not posted
| # | File:Line | Root | Summary |
|---|---|---|---|
| A | notify.sh:42,55 | NEW | writes follow a pre-existing symlink in the state dir (needs local write access to that dir). |
| B | uat-doc.py:39-49 | NEW | `setdefault` keeps the first of repeated keys (SURFACE); inert today. |
| C | fixtures | DOC | copies of two batch records: `duckbase-co` slug and Linear UUIDs already public at base; the e56e copy lacks a close receipt so its own generated doc says "no PR" while its README says #378/#379 — frozen data with no reader. Captain's call on retention. |
| D | uat-doc.py:210-219 | DOC | "For the Captain" lists each PR independently; the stack constraint the hand-written doc carried is not a record field. |
| E | README:350-353 | DOC | the skip is gated by the marker file, not by comparing the message id. |

### Verification Summary
| Check | Result |
|---|---|
| uat-doc on both fixture batches | exit 0; headings and PR set equal the reference; 31-line phrasing diff |
| synthetic issue with no evidence | empty layer + `none stuck.` (finding #2 reproduced) |
| notify dry-run twice | sent / skip, one marker |
| notify without --dry-run | exit 2, no send path |
| non-fixture comment ratio | 3% |

Event (if posted): REQUEST_CHANGES. **Not posted** — findings to disk for the disposition station.
