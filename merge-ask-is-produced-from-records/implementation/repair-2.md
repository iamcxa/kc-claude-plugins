# Authorized repair: record-route guards and disclosures

Candidate: `ad41870b72f19d8ad141efaa67cda3afb23f1d4d`. Branch: `spacedock-ensign/merge-ask-is-produced-from-records`. Base: `bfc53d82510006b52baf41569c1e25176e99d87a`; repair starts from `de564ef9e2b608d4106d96c56448e22f31a6fc5b`. Product and state remain local; FO owns push, RoboRev and hosted CI.

Investigation started 2026-11-14 00:53:19 Asia/Taipei; repair started 01:31:54. Time source: clock.curr_time UTC +08:00. Evidence completion time is recorded in completion.json.

All six confirmed classes are repaired. All 29 CI-listed direct Python commands pass on this exact candidate: 1457 unittest cases passed, 11 optional skips, and 2 additional native scripts without unittest totals. Repository lint is included; installed comment ratio, ADR lint, number guards, role/design checks and doc-impact review also completed. Full command/exit/output joins are in `commands.json`, `ci-tests-final.json` and their logs under `evidence/implementation-2-message-2/`.

## What changed

1. Findings/answered observations require one FO judgment bound to the observed reviewer/evidence identity in the unchanged question. `findings` requires `disposed`; Copilot `answered` requires `clean` or `disposed`. Both record commands call the same `reviewer_problems` declaration/profile guard used by the text route. This is a judgment-presence safeguard: it does not authenticate each finding's severity, repair, classification or Captain waiver.
2. A known Copilot exit-5 observation requires the question's unread decision and conditional retry offer. The retry predicate is shared with the text route. No raw refusal quote/source boilerplate or new adapter outcome grammar is restored.
3. Missing/duplicate/wrong second-reviewer declarations and empty triggers are refused; quoted prod uses the existing parsed profile guard. Pilot not-triggered remains valid; structured prod/db cannot waive the reviewer.
4. Both question routes use the extracted existing head-token predicate: a nonempty bounded 7–40-hex token set must match the candidate. Empty, nonhex and overlong values now hold.
5. Record question rereads existing reviewer configuration and compares configured remote reviewers with PR-scope saved observations. Local RoboRev observations remain excluded from remote completeness and round counts.
6. The same count/scope readers produce required `unchecked_counts` and `scope_disclosure` fields, including cited/marked counts and `（未對過紀錄）`. The question's bytes do not change; claim prose is not copied into the public record. This implements FO's disclosure decision while preserving the immutable-question design.

The contract/schema, checker and two existing test files changed. There is no tenth product path, new ADR, version change, workflow-budget raise or adapter change. ADRs 0072/0082 keep their warning semantics through record fields; FO's message-2 decision resolves the earlier disclosure-mechanism question. Workflow/observer/Copilot references still point to the one contract.

## Tests and falsifiers

Exactly six new test methods, one per confirmed class, compare record and text routes and keep passing controls. The final tests reject the original checker in all six methods (seven failing subcases, zero errors); each targeted in-memory guard mutation is also caught. `base-control.json`, `mutations.json` and their logs bind those failures. These are behavioral assertions, not source wording pins. Existing record/POC fixtures were corrected to declare no remote reviewers when their reader double intentionally returns no observations; no new test method was added for that setup correction.

The first CI attempt at `925e0fc9e` found the POC fixture mismatch and was interrupted after 15 completed commands; it is not reported as a complete suite. The intermediate retry still exposed the fixture's declared Codex/empty-observation mismatch. Both failed logs remain. Initial red/green harness setup failures and the baseline subcase-grouping correction remain in the evidence; the final baseline control has six failing methods without errors, and the final complete suite is green.

Every listed Python file ran directly from the product worktree, with PYTHONDONTWRITEBYTECODE=1 and task-owned TMPDIR. Independent Python files ran in up to four processes; the three native transport commands ran in order with the assigned SPACEDOCK_BIN (0.27.2). The native mod bytes match the retained CI-pin digest at commit 4d158a484ec73e184861067f8ed1e20087fdc26a. This is local macOS evidence, not hosted Linux CI.

## AC-6 rerun

Both archived public-input cases pass check/question/native preparation, retain the FO question bytes and bind JSON summary/reference bytes unchanged. A fresh-shell report-read fixture supplies current Captain-step observations; historical acceptance commands were not executed. The fixture question now explicitly carries the unread/retry decision required by this repair.

Actual read-only public PR 865 observation saves a held record: check/question both exit 1; separate direct native preparation exits 0 and proves transport only. No green live delivery, approval or merge is claimed. The initial sandbox network failure and successful authorized network retry are retained. Round inventories still exclude local jobs. Restoring manual summary fields, admitting held ask filenames, counting local jobs and changing dispatched heads are all caught by rerun reverse mutations with passing controls before head replacement (`candidate-mutations.json`, `mutation.json`, `goal-check.json`). No PR write or review request was made.

## Measured size

Repair from de564ef9e: 4 files, +167/-14. Entire task from base: 9 files, +727/-148. Method: whitespace-delimited str.split() over UTF-8 git object bytes; no generated caches.

| Repair file | Added | Removed |
|---|---:|---:|
| kc-dev-flow-2/references/delivery-record.md | 19 | 2 |
| kc-dev-flow-2/scripts/delivery_gate.py | 49 | 8 |
| kc-dev-flow-2/scripts/test_delivery_gate.py | 98 | 3 |
| kc-dev-flow-2/scripts/test_poc_readme.py | 1 | 1 |

Workflow: 6099 → 5982 words from base; 5982 → 5982 in this repair, exactly its existing budget. Contract: 1373 → 1585. All package Markdown: 46577 → 47527 → 47739; all tracked UTF-8 package text: 219019 → 221445 → 222507. These static counts do not measure total lifecycle reading, elapsed delivery time or cost per PR. Net line removal remains unachieved. CI definition/cost was not changed; CI cost per PR was not measured.

## Handoff limits

FO reported Draft PR #869 and RoboRev job 1857 against the prior candidate; this repair has not been pushed, run through RoboRev or verified in hosted CI. FO's truthful dispositions, per-finding Captain waiver authority, complete provider history, private-repository use, downstream adoption and a real green merge remain separate obligations. No private task bodies or reviewer prose are archived; retained public/synthetic evidence is path-normalized with a SHA-256 manifest.

Evidence finalized: 2026-11-14 02:01:13 Asia/Taipei, clock.curr_time UTC +08:00. Final state commit/delivery checks follow. Scratch close output: `implementation/repair-2-close.txt`; new evidence is verified separately from the canonical implementation-2 evidence rechecked by close.
