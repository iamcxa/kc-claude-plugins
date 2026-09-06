## PR #378 — feat(ship-flow): open the Draft PR and disposition kc-pr-review findings, refusing empty output as absence

**What this PR changes:** two scripts for ship-flow's review station — `open-pr.sh` opens a Draft PR from an accepted Evidence block and prints the PR number; `disposition.py` reads a findings JSON and returns block / listed / reviewer-absent by the approval `defaults`. Plus fixtures and a README paragraph.
**Why (per author):** the review skill runs only in a Claude session, so the station is two scripts either side of that session run (Brief DEV-104).
**Claimed goal:** AC-1..AC-4 of DEV-104. **Linked issue:** DEV-104.
**Goal-achievement verdict:** ⚠️ Partially — the four ACs hold on the fixtures (FO re-ran all three dispositions, the missing-file path, and open-pr with the stub gh), but the scripts accept inputs the station exists to distrust (below).

Tier: Lite (196 lines, no security files) + ToB security. Agents: code-reviewer, silent-failure-hunter, comment-analyzer, tob-security-reviewer. Pre-scan: CLAUDE.md absolutes, comment ratio, fixture scan, test execution. Head 3a733578 unchanged during review.

### Inline Comments (CODE)

| # | File:Line | Severity | Conf | Category | Summary |
|---|---|---|---|---|---|
| 1 | scripts/ship-flow/open-pr.sh:44,72 | HIGH | 7/10 | security | MULTI-SOURCE: ToB + silent-failure — `BRANCH` from the block is passed to `gh pr create --head` unbound to `CANDIDATE_SHA`; `gh` accepts `<user>:<branch>`, and the upstream station's `ls-remote origin "$BRANCH"` check soft-passes on an empty result (accept-evidence.sh:159-160), so a fork branch opens a PR whose diff is not the reviewed commit under a title that says it is. |
| 2 | scripts/ship-flow/disposition.py:52 | HIGH | 8/10 | security | MULTI-SOURCE: silent-failure + ToB — exact, case-sensitive match against `("security","data-loss","compatibility")`; `"Security"` or any variant is silently `listed`. The gate fails open on the one input class it exists for. Reproduced. |
| 3 | scripts/ship-flow/open-pr.sh:80 | HIGH | 8/10 | correctness | MULTI-SOURCE: silent-failure + ToB — PR number = last digit run in stdout+stderr merged (`2>&1` at :72); a `gh` notice containing a number yields the wrong PR number with exit 0. Reproduced. Parse `pull/[0-9]+` from stdout only. |
| 4 | scripts/ship-flow/open-pr.sh:12-13,18 | HIGH | 9/10 | correctness | MULTI-SOURCE: 4 agents — header promises exit 1 for a `gh` failure; `die` always exits 2; five distinct failure paths share one code. Fix the code or the comment. |
| 5 | scripts/ship-flow/open-pr.sh:31,39 | MEDIUM | 6/10 | correctness | Medium confidence — verify: `sed -n '/^## Evidence$/,/^$/p'` + `head -1` reads the FIRST of several blocks; a file with a stale block first opens the stale PR. Refuse a second `## Evidence`. |
| 6 | docs/ship-flow/README.md:344-345 | MEDIUM | 7/10 | docs | "runs only inside a Claude session, never headless" is false in this repo: `kc-pr-flow/scripts/review-ablation.sh` runs `kc-pr-review` headless (27 recorded runs). Repo rule: an absolute names its enforcement point or becomes bounded. |
| 7 | scripts/ship-flow/disposition.py:54-58 | MEDIUM | 7/10 | correctness | Non-dict entries are dropped from the blocking check but counted in `findings_count`; a malformed writer output reads as a normal listed finding. |
| 8 | scripts/ship-flow/open-pr.sh, disposition.py | MEDIUM | 8/10 | test-coverage | MULTI-SOURCE: code-reviewer + ToB + comment-analyzer — nothing in `kc-dev-flow-contract-test.py` or CI references either script or the new fixtures; the only runs on record are the worker's and the FO's manual ones. |

### Advisory (DOC/NEW) — not posted

| # | File:Line | Root | Summary |
|---|---|---|---|
| A | disposition.py:34-45 | DOC | four failure modes (missing, unreadable, malformed, wrong shape) collapse to one silent `None`; by design, but no diagnostic trail. |
| B | disposition.py:38 | NEW | `UnicodeDecodeError` not caught; loud, outside the documented exit contract. |
| C | open-pr.sh:36,50 | NEW | "missing FIELD" cannot distinguish absent from empty. |
| D | scripts (comment ratio) | DOC | 35 comment lines of 154 script lines (23%); mostly a docstring carrying schema facts, plus the incomplete exit-code header (#4). |
| E | fake-gh/gh:2 | DOC | "without-it falsifier" it names has no runner in the tree (see #8). |

### Verification Summary
| Check | Result |
|---|---|
| disposition fixtures (security / style / empty / missing) | block / listed / reviewer-absent / reviewer-absent |
| open-pr.sh with stub gh | prints 777, exit 0 |
| branch value `--evil=1` | passed as a quoted value, not an option |
| fixtures creds/PII | none |
| contract test at head | exit 0 (worker + station) |

Event (if posted): REQUEST_CHANGES. **Not posted** — the ship-flow review station writes findings to disk for `disposition.py`; the Captain sees them in the UAT document.
