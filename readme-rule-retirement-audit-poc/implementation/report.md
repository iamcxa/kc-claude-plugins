# README rule-retirement audit — stopped at the approved threshold

N = **15** rule sentences examined; M = **0** covered whole with a recorded nonzero violation exit; K = **0 bytes** removable. Four sentences have partial format coverage and eleven have no identified behavioral enforcement in the searched boundary. **Stop applied: 0 < 3 after sentence 15.** No removal is proposed by this audit.

The task's prescribed early-stop conclusion is “the README is not where the bloat is.” This is the agreed stopping heuristic for this sample, not a measurement of all README bloat: the other five sections were not examined. The Captain retains the removal decision.

## Exact source and boundary

- Source, base and unchanged product candidate: `c2f035b6612f5edb42220576b3414e993531ffd6`; branch `spacedock-ensign/readme-rule-retirement-audit-poc`. `HEAD` and the local `origin/main` tracking ref both named this commit. No fetch was run, so this does not claim the remote has remained at this commit.
- Source: `docs/dev2/README.md`, 41076 bytes, SHA-256 `284e9c88cb38a0a5b183fa7c66784d1a41b1ea78a2cbfe252d4965aa243a9f8c`.
- Product worktree was clean before and after the probes; no repository file, test, script, README or product commit changed. No product push, pull request, review request or external diagnostic traffic occurred. No PR text is prepared because the accepted outcome expressly expects no PR.
- The task gate approves a read-only POC (bounded proof of concept), with one implementation and one validation cycle. The installed 0.41.0 role-trigger preflight exited 0: implementation spent 1, validation spent 0. Lifecycle scripts use the dispatch's installed package; the audit checks are the requested source scripts exported from the pinned repository commit.
- Prior implementation reports: none in this task. The linked study is input data, not evidence for these counts. The neighboring reform tasks own different experiments; no linked PR or sibling retirement report is named by this task. Reused existing record parsers and test fixtures rather than building a replacement check.
- Governing architecture decision records 0003, 0024, 0037 and 0048 are `Accepted` at the pin; byte digests and paths are in [governing-adrs.json](../evidence/implementation-1/governing-adrs.json). They distinguish instructions, text transmission and actor compliance. No new ruling or ADR is created.

## Counting and verdict method

Proceed in the six named sections' README order, preserving a complete sentence as the unit, including semicolon-linked obligations. Markdown labels and line wrapping do not create extra units. The Team role/handoff sentence is included as a normative role duty; the question embedded in the next instruction ends that instruction. This deterministic rule produces the first fifteen sentences entirely in `Dispatch facts`: eight Team, two Signal, two Package and three Secrets sentences. Quotes below preserve every word, with line wrapping normalized to spaces.

`covered whole` requires a quoted behavioral check that rejects a constructed violation with a recorded nonzero exit and covers every obligation of that sentence. `covered part` means a narrower input-format requirement is checked while actor obligations remain outside it. A test that only insists the prose is still present is a text-presence check, not whole-class enforcement. `uncovered` means no whole or partial behavioral enforcement was identified in this bounded search; it does not assert absence of every possible adopter or host guard.

Two bounded searches cover production `kc-dev-flow-2/scripts/*.py` and their `test_*.py` files, with patterns and public-safe matches saved in [bounded-searches.txt](../evidence/implementation-1/bounded-searches.txt). Source excerpts and exact check quotes are in [source-quotes.md](../evidence/implementation-1/source-quotes.md). In particular, `test_sd_dispatch.py:50` asserts `"complete Team rule missing or duplicated"`; that protects delivery of the words, not what the worker does. ADR 0003 explicitly assigns secret enforcement to adopters and ships no package hook. No secret, guard bypass, peer message or unauthorized worker action was actually performed.

## Single rule table — the reached prefix

Every row identifies its separately saved synthetic violating witness (`rule-NN`) in [rows.json](../evidence/implementation-1/rows.json), the fixture input, and its actual `python3 -B` command and stdout/stderr in [runs.json](../evidence/implementation-1/runs.json) and [runs.log](../evidence/implementation-1/runs.log). These are record-parser probes: witnesses describe disallowed behavior as inert data; their acceptance proves that the parser does not inspect that behavior, not that a real worker performed it. A zero exit in the table never counts toward M.

| Rule sentence (quoted) | Enforcing check (quoted), or bounded absence | Exit on constructed violation | Verdict |
| --- | --- | --- | --- |
| 1. “You are one worker in a team completing the project goal; your stage and handoff serve that goal.” | None identified for this behavior in the searched scripts/tests. `test_sd_dispatch.py:50`: `"complete Team rule missing or duplicated"` checks instruction text only. The record-parser probe is a negative scope control, not an enforcing check. | `rule-01`: **0** (negative control; no enforcing exit found) | uncovered |
| 2. “Before substantial work or retrying a failure, check this task's prior reports, linked sibling tasks and PRs, and relevant workflow state: did someone already do this, hit this, or own it now?” | None identified for this behavior in the searched scripts/tests. `test_sd_dispatch.py:50`: `"complete Team rule missing or duplicated"` checks instruction text only. The record-parser probe is a negative scope control, not an enforcing check. | `rule-02`: **0** (negative control; no enforcing exit found) | uncovered |
| 3. “If your environment cannot run a required checklist check, tell FO before building work that depends on it.” | None identified for this behavior in the searched scripts/tests. `test_sd_dispatch.py:50`: `"complete Team rule missing or duplicated"` checks instruction text only. The record-parser probe is a negative scope control, not an enforcing check. | `rule-03`: **0** (negative control; no enforcing exit found) | uncovered |
| 4. “Ask FO early about overlapping ownership, repeated failures, missing authority or evidence, or infeasible targets.” | None identified for this behavior in the searched scripts/tests. `test_sd_dispatch.py:50`: `"complete Team rule missing or duplicated"` checks instruction text only. The record-parser probe is a negative scope control, not an enforcing check. | `rule-04`: **0** (negative control; no enforcing exit found) | uncovered |
| 5. “Give checked sources, findings, attempts and the specific question.” | None identified for this behavior in the searched scripts/tests. `test_sd_dispatch.py:50`: `"complete Team rule missing or duplicated"` checks instruction text only. The record-parser probe is a negative scope control, not an enforcing check. | `rule-05`: **0** (negative control; no enforcing exit found) | uncovered |
| 6. “With a mid-run FO channel, pause dependent work and continue safe independent work; without one, end your turn with that handback instead of waiting.” | None identified for this behavior in the searched scripts/tests. `test_sd_dispatch.py:50`: `"complete Team rule missing or duplicated"` checks instruction text only. The record-parser probe is a negative scope control, not an enforcing check. | `rule-06`: **0** (negative control; no enforcing exit found) | uncovered |
| 7. “Never answer your own or your reviewers' permission requests; route them to FO.” | None identified for this behavior in the searched scripts/tests. `test_sd_dispatch.py:50`: `"complete Team rule missing or duplicated"` checks instruction text only. The record-parser probe is a negative scope control, not an enforcing check. | `rule-07`: **0** (negative control; no enforcing exit found) | uncovered |
| 8. “FO coordinates peers and decisions; do not message peers or change others' work.” | None identified for this behavior in the searched scripts/tests. `test_sd_dispatch.py:50`: `"complete Team rule missing or duplicated"` checks instruction text only. The record-parser probe is a negative scope control, not an enforcing check. | `rule-08`: **0** (negative control; no enforcing exit found) | uncovered |
| 9. “send the completion message once, to the first officer by the name your session lists as addressable (`main` under Claude Code dispatch).” | `dispatch_records.py:75,85-86`: `"a scope-notes line naming main as the completion recipient"`. Wrong-recipient control exits 1; correct instruction plus a duplicate/wrong send or team-lead fallback witness exits 0. `test_dispatch_records.py:293-304` checks recipient syntax, not delivery, multiplicity or report history. | `rule-09`: **0**; `wrong-recipient`: **1** (partial only) | covered part |
| 10. “The completion block's `team-lead` is Spacedock's default and is not registered there (spacedock-dev/spacedock #523, #608); do not try it first and do not describe a fallback in the report.” | `dispatch_records.py:75,85-86`: `"a scope-notes line naming main as the completion recipient"`. Wrong-recipient control exits 1; correct instruction plus a duplicate/wrong send or team-lead fallback witness exits 0. `test_dispatch_records.py:293-304` checks recipient syntax, not delivery, multiplicity or report history. | `rule-10`: **0**; `wrong-recipient`: **1** (partial only) | covered part |
| 11. “`<package>` in stage text is the `Package root:` line of the kc-dev-flow-2 skill you loaded; your dispatch's scope notes state the same path, and if they differ, use the skill's.” | `dispatch_records.py:83-84`: `"a 'Package root:' line with an absolute path in its scope notes"`. Relative root exits 1; an arbitrary absolute root conflicting with the witnessed skill root exits 0. `test_dispatch_records.py:343-353` checks presence/location/absolute syntax, not agreement with the skill. | `rule-11`: **0**; `relative-root`: **1** (partial only) | covered part |
| 12. “Run package scripts only from it; never search the filesystem, `/tmp` or another install for them.” | `dispatch_records.py:207-209`: `"bare package script name {name}"`; `return 1 if found else 0`. Bare name exits 1; an absolute command under an unassigned root exits 0. Neither actual execution nor filesystem-search behavior is observed. | `rule-12`: **0**; `bare-script`: **1**; `arbitrary-absolute-script`: **0** | covered part |
| 13. “`<wrapper>` is the only route to a development secret: run a command that needs one as `<wrapper> <command>`.” | None identified in the package scripts/tests. ADR 0003: `"The package does not ship a secret-read hook."` Adopter/user enforcement is outside this audit; inert witness accepted by the record parser. | `rule-13`: **0** (negative control; no enforcing exit found) | uncovered |
| 14. “Never read or print a value.” | None identified in the package scripts/tests. ADR 0003: `"The package does not ship a secret-read hook."` Adopter/user enforcement is outside this audit; inert witness accepted by the record parser. | `rule-14`: **0** (negative control; no enforcing exit found) | uncovered |
| 15. “If a guard refuses a command that only mentions a secret-reading tool, rephrase it; do not split, encode or wrap the command to pass the guard.” | None identified in the package scripts/tests. ADR 0003: `"The package does not ship a secret-read hook."` Adopter/user enforcement is outside this audit; inert witness accepted by the record parser. | `rule-15`: **0** (negative control; no enforcing exit found) | uncovered |

## Stop condition and section coverage

The audit stopped immediately after the fifteenth rule sentence was assessed: zero met the required minimum of three. The full six-section table requested for a non-stopped run is therefore intentionally not produced. Unexamined sentences are neither silently counted nor labelled uncovered.

- `Dispatch facts`: all 15 reached sentences examined, as quoted above.
- `Review-finding disposition`: not examined — approved stop condition.
- `FO steps: review findings`: not examined — approved stop condition.
- `Number guards`: not examined — approved stop condition.
- `FO steps: number guards`: not examined — approved stop condition.
- `Decision records`: not examined — approved stop condition.

Accordingly `delivery_gate.py`, `number_guards.py`, `decision_ledger.py` and `adr_lint.py` were not exercised for the later rule families. Imported dependencies are not counted as independent audit coverage. Existing broad test suites, native worker behavior, private adopters, CI costs and effects of removing prose were not measured. The assignment's 45–90 minutes is a supplied budget judgment, not a measured result; reaching the early stop is the completed bounded outcome.

## Reproduction and falsifiers

The replay script [audit.py](../evidence/implementation-1/audit.py) uses only Python's standard library, Git and the pinned public repository objects. Run it against a clean assigned worktree whose HEAD and local origin/main both still equal the pin, with an empty directory inside the validator's own scratch allocation and a separate output directory:

```sh
python3 -B <evidence>/audit.py --repo <assigned-worktree> --scratch <task-scratch>/replay --out <replay-evidence>
```

It exports the pinned source into that scratch directory and runs each recorded command from there. It does not check out a branch, alter Git config, fetch, push, open a PR or write a product file. Its 21 CLI runs include two clean baselines, three nonzero format controls, one accepted unassigned-root control, and fifteen separately constructed witnesses; [runs.json](../evidence/implementation-1/runs.json) holds their actual commands and exits. Fixtures are also archived byte-for-byte, so a validator can rerun an individual command after exporting the pinned source to `snapshot/`.

Falsifiers: a wrong-recipient control returning 0 invalidates that partial-coverage claim; a relative root returning 0 invalidates the root-format claim; an accepted bare-script control invalidates the names claim. Conversely, an existing check that actually rejects every breach of one quoted sentence with nonzero output would change that row and M. A successful metadata control alone cannot change a row to covered whole. Rejecting any inert witness on a new broad text rule also would not by itself establish real actor enforcement.

K counts actual source bytes that would be removed for sentences qualified as covered whole, not normalized quote lengths: the qualified set is empty, so its byte union is exactly 0. No README deletion candidate was generated.

## Handoff and cleanup

Implementation deliverable is this state-only report and its public synthetic evidence. Independent validation and the Captain's ruling remain FO-owned; the copy beside the study is explicitly FO-owned. No product candidate commit, product push or PR exists for this audit. `roborev not run: read-only measurement with no code candidate to review`.

Scratch close-out command exited 0. Exact output:

```text
Scratch removed: /private/tmp/dev2/kc-claude-plugins-0a31751399576cc5/readme-rule-retirement-audit-poc/implementation-1 (2855269 bytes)
Evidence: evidence/implementation-1/ (51 files, 60.5 KiB)
```

The retained evidence manifest is `evidence/implementation-1/SHA256SUMS`; no throwaway worktree was registered, and the assigned product worktree remains in place. The close-out log is `scratch-removed.txt` in this task folder.
