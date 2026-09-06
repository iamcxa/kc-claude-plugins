## PR #379 — feat(ship-flow): pick a batch's UAT-ready CLI e2e shape from its milestone

**What this PR changes:** `e2e-gate.py` derives the milestone's flow path from its name, computes the stacked head from the close receipt, and either runs `e2e-cli.sh` there, records `e2e: not applicable` with a reason, or exits non-zero; plus this batch's own flow file and three fixture pairs.
**Why (per author):** DEV-105 — UAT-ready needs one of three e2e shapes, and this batch had no flow to run.
**Claimed goal:** DEV-105 AC-1..AC-5. **Linked issue:** DEV-105.
**Goal-achievement verdict:** ⚠️ Partially — all three shapes reproduce on the fixtures (FO ran ac2/ac3/ac4 and the flow at the head), but the run branch executes candidate-tree scripts with the FO's full credentials, and the shipped flow only exercises the not-applicable branch.

Tier: Lite (184 lines) + ToB. Agents: code-reviewer, silent-failure-hunter, comment-analyzer, tob-security-reviewer. Head 470b3e41 unchanged.

### Inline Comments (CODE)
| # | File:Line | Severity | Conf | Category | Summary |
|---|---|---|---|---|---|
| 1 | scripts/ship-flow/e2e-gate.py:97 | HIGH | 7/10 | security | The gate feeds a worker-supplied candidate SHA to `e2e-cli.sh`, which checks it out and `eval`s the flow's `run:` strings with cwd in that worktree and the FO's full environment; the flow calls `scripts/ship-flow/accept-evidence.sh` and `e2e-gate.py` by relative path, so a candidate's modified copies run with the FO's tokens. `without-it.sh` strips seven credential vars for exactly this case; `e2e-cli.sh`/`e2e-gate.py` strip none. |
| 2 | scripts/ship-flow/e2e-gate.py:56 | HIGH | 7/10 | correctness | `milestones.get(milestone_id, name)` — a dangling milestone id silently reuses the previous issue's milestone name; the gate then runs the wrong journey at the right head. Use `milestones[milestone_id]` and let the outer `except` turn it into exit 2. |
| 3 | scripts/ship-flow/e2e-gate.py:41 | HIGH | 8/10 | correctness | `slugify` is ASCII-only: a Chinese milestone name collapses to whatever Latin fragment it contains (`从派工到一条 Slack 消息` → `slack`) or to `""`; the Captain writes milestone names in Chinese. |
| 4 | scripts/ship-flow/e2e-gate.py:60-67 | MEDIUM | 9/10 | correctness | The candidate is never validated as a fixed commit (fixture uses `"HEAD"`); the report prints the raw ref, so the evidence does not pin what ran. `git rev-parse --verify --end-of-options "<c>^{commit}"`, print the resolved SHA. |
| 5 | scripts/fixtures/ship-flow/e2e-gate/*.ac2.*, *.ac4.* | MEDIUM | 9/10 | test-coverage | MULTI-SOURCE: code-reviewer + silent-failure + ToB — the run branch and the no-candidate/no-milestone errors have fixtures but nothing wired runs them; the shipped flow only hits `not applicable`. (FO ran them by hand: ac2 exit 0 with log, ac4 exit 1.) |
| 6 | scripts/ship-flow/e2e-gate.py:22 | MEDIUM | 8/10 | docs | MULTI-SOURCE: comment-analyzer + silent-failure — exit-code table says 2 = "usage or receipt-parsing error", but `e2e-cli.sh`'s own exit 2 (broken flow) propagates under that label. |
| 7 | scripts/ship-flow/e2e-gate.py:11-12 | MEDIUM | 6/10 | docs | Medium confidence — verify: "since an accepted-without-PR layer carries neither" states an unenforced pairing between the last milestone-bearing and last candidate-bearing issue; nothing checks they are the same issue. |

### Advisory (DOC/NEW) — not posted
| # | File:Line | Root | Summary |
|---|---|---|---|
| A | e2e-gate.py:74-81 | NEW | `TypeError`/`AttributeError` on a JSON-valid but wrongly shaped receipt escapes as a traceback (exit 1, not the documented 2). |
| B | e2e-gate.py:40 | NEW | slug is many-to-one; two milestones can share a flow file silently. |
| C | e2e-gate.py:97-101 | NEW | run log written to a never-cleaned `NamedTemporaryFile`. |
| D | e2e-cli.sh cleanup (pre-existing) | DOC | worktree removal failure swallowed with no log line. |
| E | docs/ship-flow/README.md:346-347 | DOC | slug description omits the trailing-hyphen strip. |
| F | scripts (comment ratio) | DOC | 24% of the diff is prose; the docstring's Shape block restates `main()`. |

### Verification Summary
| Check | Result |
|---|---|
| e2e-gate ac2 / ac3 / ac4 | exit 0 with log / not applicable / exit 1 |
| flow at head via e2e-cli.sh | exit 0 |
| milestone name `../../etc/passwd` | slugified to `etc-passwd`, no traversal |
| comment ratio | 1% (code); prose-heavy docstring noted |

Event (if posted): REQUEST_CHANGES. **Not posted** — findings written to disk for the disposition station.
