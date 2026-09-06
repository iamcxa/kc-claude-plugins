## PR #381 — feat(ship-flow): the close receipt refuses an undispositioned defect and carries the dev and ship debriefs

Scope: DEV-107's own layer (`8983967…9282343`); the two lower layers were reviewed as #379/#380.
**What this PR changes:** close-receipt schema gains `accepted_residual` and two debrief objects with minimum fields; `validate-receipt.py` refuses an entry with neither disposition and a missing debrief or field; two writers draft each debrief from the batch record; three steps appended to the batch's flow.
**Claimed goal:** DEV-107 AC-1..AC-6. **Linked issue:** DEV-107.
**Goal-achievement verdict:** ⚠️ Partially — the recorded draft is refused naming S24/S25/S26 and the dispositioned receipt passes (FO reproduced), but the refusal is a truthiness check that whitespace defeats, and the writers produce plausible zeros from missing inputs.

Tier: Lite + ToB, four agents. Head 9282343c unchanged.

### Inline Comments (CODE)
| # | File:Line | Severity | Conf | Category | Summary |
|---|---|---|---|---|---|
| 1 | docs/plan-flow/schema/validate-receipt.py:68 | HIGH | 9/10 | security | MULTI-SOURCE: silent-failure + ToB — `not d.get("accepted_residual")` accepts `"   "`; a defect is dispositioned by whitespace and `CLOSE OK` prints. The gate that exists to stop an undispositioned defect fails open on its own input (PoC). `.strip()` plus a `\S` pattern on `accepted_residual`, `disposition`, `candidate_correction`. |
| 2 | docs/plan-flow/schema/validate-receipt.py:70-81 | HIGH | 9/10 | correctness | With `jsonschema` absent the new checks are presence-only: empty `candidate_correction` and a malformed `fix_ticket` pass (PoC). Same class as DEV-109; replicate the checks in Python or fail closed. |
| 3 | scripts/ship-flow/dev-debrief.py:37-43,73; ship-debrief.py:63-66 | HIGH | 8/10 | correctness | MULTI-SOURCE: 3 agents — missing evidence/README/`rounds`/`minutes` become `rounds: 0`, `[]`, `{}` with exit 0 and no stderr; and `code_refusals` is a verbatim copy of `residuals` (S35). A plausible, wrong debrief passes the gate. |
| 4 | scripts/ship-flow/dev-debrief.py:38-40 | HIGH | 9/10 | correctness | `sorted(glob)[0]` picks the alphabetically-first `worker-evidence-<ISSUE>*.md`; a refused round 1 beats an accepted round 2 (reproduced; the FO worked around it by moving files aside). |
| 5 | scripts/ship-flow/ship-debrief.py:13,43-44 | HIGH | 9/10 | correctness | `overturned` is `"correction" in line.lower()`: it flags the correction note itself, misses "retracted", never marks the decision that was overturned (PoC on the real README); and the bullet parser drops `*` bullets and truncates wrapped lines — `uat-doc.py` in the same tree already parses both. |
| 6 | docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json:8,93 | MEDIUM | 9/10 | correctness | `dev_debrief`/`ship_debrief` are not in top-level `required` (only the script refuses their absence); `disposition` and `decision` have no `minLength`. |
| 7 | docs/plan-flow/schema/validate-receipt.py:74 | MEDIUM | 8/10 | correctness | `per_issue` keys are never compared to the plan receipt's issue set, and `defects_disposition` ids are never compared to `defects_returned` (both PoC'd: an issue or defect vanishes from a debrief with `CLOSE OK`). |
| 8 | docs/ship-flow/flows/…yaml:22; fixtures missing-*.json | MEDIUM | 8/10 | test-coverage | MULTI-SOURCE: silent-failure + ToB — the "refuses undispositioned" step is satisfied by three unrelated causes (missing debriefs, stale approval hash); the two negative fixtures and both writers are wired into nothing. |
| 9 | dev-debrief.py:7,13; schema:49,60,84 | MEDIUM | 7/10 | docs | "accept-station refusals" are never captured; exit-code docstrings omit the traceback path; schema descriptions state process timing and an overturn semantics the code does not implement. |

### Advisory (DOC/NEW)
| # | File:Line | Root | Summary |
|---|---|---|---|
| A | schema `code_refusals` description | DOC | describes a semantic the copy does not enforce. |
| B | e2e-cli.sh strip list | DOC | `env -u` of seven names, not a clean environment (pre-existing; stated for the record). |

### Verification Summary
| Check | Result |
|---|---|
| DRAFT / dispositioned / missing-debrief / missing-rounds | refused S24-26 / CLOSE OK / refused naming field / refused naming field |
| flow (5 steps) at head | exit 0 |
| writers on the live record | ran; `code_refusals` = residuals, `evidence_refusals` = observed line (S35) |
| new flow steps go through `run_stripped` | yes |

Event (if posted): REQUEST_CHANGES. **Not posted** — findings to disk for the disposition station.
