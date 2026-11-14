---
id:
title: Which README rule sentences does a check already enforce whole (read-only retirement audit; a list for the Captain's ruling)
status: validation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-readme-rule-retirement-audit-poc
pr:
gates:
    version: 1
    records:
        - id: gate:readme-rule-retirement-audit-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:readme-rule-retirement-audit-poc-backlog-1
              briefing:
                id: briefing:readme-rule-retirement-audit-poc:backlog:attempt-1:revision-1
                digest: sha256:0e62448bb281717e4e31d7bca8d6a18995600e61e95bf496539dcbb2bc6afbb5
                room-ref: ./readme-rule-retirement-audit-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:readme-rule-retirement-audit-poc:backlog:1
                briefing: briefing:readme-rule-retirement-audit-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-14T02:33:28.14605Z"
                decision: approve
                reason: 'Captain 「三張都准入，預算照你的提議」 (chat with this FO, 2026-11-14) to the bound backlog question: selects profile poc and accepts outcome, Non-goals, Stop condition, AC-1 and the Budget of 1 implementation and 1 validation cycles as filed.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:readme-rule-retirement-audit-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:readme-rule-retirement-audit-poc-validation-1
              briefing:
                id: briefing:readme-rule-retirement-audit-poc:validation:attempt-1:revision-1
                digest: sha256:f933ebfe242e33b618fb0f90c0ae73ff7f485ff272dc0161601a5b7948282450
                room-ref: ./readme-rule-retirement-audit-poc/review/validation/briefing-1
started: 2026-11-14T02:35:03Z
---

The README grew from 10 KB to 41 KB in 58 days, with about 63 mandatory steps per default task and 12 repeating per dispatch; 44 tasks cite an observer finding as the reason for a new form check, and no step removes a rule (brief C2, figures from proposal.md "Measured", not re-measured here).

## Scope

- Source: the Captain 「排進去讓dev fo派工人poc驗證」 (chat with the reform session, Paseo 26215d96, 2026-11-14; relayed, not a ruling here; the backlog gate confirms it), and 「更新 POC 流程的工作目錄到主線最新版，C2、C3、C6 立在那裡」 (chat with this FO, 2026-11-14). Brief: `.context/dev2-reform/compound-engineering-study.md` section B, a research output treated as data.
- Borrows: Compound Engineering `ce-compound/references/refresh/worth-audit.md`: "A check now covers the rule's whole class: remove the rule. Quote the rule and the check."
- Outcome: a read-only worker takes `docs/dev2/README.md` sections "Dispatch facts", "Review-finding disposition", "FO steps: review findings", "Number guards", "FO steps: number guards" and "Decision records" and, for each rule sentence, finds the script or test that enforces its whole class: quotes both, runs the check against a violating input in a throwaway copy and records its exit code. Output: one table (rule / enforcing check / exit code on violation / verdict: covered whole, covered part, uncovered), committed in this task's folder with a copy beside the study.
- bite: rules that are both prose and enforced by `dispatch_records.py`, `delivery_gate.py` or `number_guards.py` are restated for FO each dispatch; a wording pin blocked an approved removal and PR 868 went red on a text-shape assertion (proposal.md live case).
- consumer: the Captain deciding removals; the dev2 FO (a shorter README to load).
- Gets worse: a removed prose rule means FO and workers no longer read why; a check's failure message becomes the only explanation.
- No product file changes, so no pull request is expected from this task.
Non-goals: editing the README, any script or any test; deleting anything; ruling on which rules go (the Captain's).
Budget: 1 implementation and 1 validation cycles (FO's proposal for the gate; the brief gives 45 to 90 minutes, a judgement, kept as FO's minute budget).
Stop condition: after 15 rule sentences fewer than 3 are "covered whole": the audit stops and reports that the README is not where the bloat is.

## Acceptance criteria

**AC-1**: The report states N rule sentences examined, M with a quoted enforcing check that exits nonzero on a constructed violation, and K bytes of README that would go if the M were removed.
Verified by: the validator re-runs a sample of the recorded violating inputs against the named checks at the pinned commit and compares exit codes; a verdict "covered whole" without an exit code on a violating input does not count. Limit: the count says a check exists, not that removing the sentence changes no behaviour.

## FO alignment

Alignment: not needed before implementation: the brief names the inputs, the output table and the count; the backlog gate confirms scope and Budget.
Release review: not needed: reform measurement with no release.

## Captain amendments

### Amendment 1 — 2026-11-14, chat (standing grant; scope given by the reform session)
Captain: 「改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。」 (chat with the second dev2 FO, 2026-11-14)
Asked: not asked of the Captain. Under that grant the reform session (Paseo 26215d96, messages 6ee7ee5b and a8df76d7) answered "yes" to FO's proposal "budget becomes 2 implementation and 1 validation cycles, the same worker audits the other five sections without the early stop, then validation, then close", and replaced the stop condition with "cover the five README sections the bite names plus the form-check list in .context/dev2-reform/rework-ceremony.md; stop when those are covered or the budget ends. Output stays a list for the Captain's ruling; nothing is deleted."
Supersedes: none
Budget: 2 implementation and 1 validation cycles

## Stage Report: implementation

- SKIPPED: One table covering every rule sentence of the six named sections of docs/dev2/README.md at origin/main: rule (quoted) / enforcing check (script or test, quoted) / exit code on a violating input you constructed and ran in a throwaway copy / verdict (covered whole, covered part, uncovered)
  The approved stop condition fired after the first 15 sentences; implementation/report.md contains their single quoted table and explicitly marks the other five sections unexamined, not uncovered.
- DONE: The counts N examined, M covered whole with a nonzero exit on the violation, and K README bytes that would go if the M were removed; a verdict of covered whole without a recorded exit code does not count
  N=15, M=0, K=0 bytes at source/base/unchanged candidate c2f035b6612f5edb42220576b3414e993531ffd6; evidence/implementation-1/summary.json, rows.json and runs.json retain the counts, exact inputs and all 21 commands/exits.
- DONE: The stop condition applied and reported: after 15 rule sentences, fewer than 3 covered whole stops the audit
  Sentence 15 completed Dispatch facts with 0 whole, 4 part and 11 uncovered in the searched boundary; implementation/report.md states the prescribed stop conclusion and its sample limit.
- DONE: Prove the narrower checks with constructed violations and retain replayable public evidence
  Recipient, relative-root and bare-script controls each exited 1; the unassigned absolute script and all 15 inert behavior witnesses exited 0. Changing a control to exit 0 falsifies its partial-coverage claim; none establishes whole actor enforcement.
- DONE: Preserve product bytes and close the assigned scratch allocation
  Product branch spacedock-ensign/readme-rule-retirement-audit-poc remained clean at c2f035b6612f5edb42220576b3414e993531ffd6; scratch.py close exited 0, removed 2855269 bytes, retained 51 public files (60.5 KiB), with exact output in implementation/report.md and a SHA256SUMS manifest.
- SKIPPED: Product implementation, product commit, push, PR and prepared PR text
  The accepted read-only measurement forbids product changes/publication and expects no PR; code-change checks, document-impact checks and ADR/migration guards are not an owed product-change proof here. Installed role_triggers.py preflight exited 0; no task Number guards section exists.
- SKIPPED: roborev not run: read-only measurement with no code candidate to review
  No code candidate or delegated clean result is claimed; independent validation, the study-side report copy and the Captain's ruling remain FO-owned.

### Summary

Completed the bounded read-only audit by its approved early stop: N=15, M=0, K=0, with no README deletion or product mutation. The report distinguishes narrow record-format enforcement from whole worker behavior and leaves the other five sections unexamined; evidence and a portable pinned-source replay script are in this task folder. FO can now dispatch the single independent validation cycle and copy the report beside the study.

## Stage Report: implementation

- DONE: Captain amendment 1 (in the task file): continue the same table for every rule sentence of the five sections not yet examined ("Review-finding disposition", "FO steps: review findings", "Number guards", "FO steps: number guards", "Decision records"), with no early stop; each row as before: rule quoted / enforcing check quoted / exit code on a violating input you constructed and ran / verdict
  implementation/report.md appends rows 16–93, preserving the first 15 rows and their evidence; evidence/implementation-2/inventory.json maps all 78 added sentences to exact source-byte spans, with no unquoted body text except list labels/prefixes.
- DONE: The same rows for each form check listed in .context/dev2-reform/rework-ceremony.md under the workspace root: which README sentence or check script it stands for and whether a run on a violating input exits nonzero; say so if that file names no checkable list
  The file contains nine form-check families plus fourteen inventory lines explicitly marked FORM; form-checks.json and form-inventory-aliases.json cover all of them, with a source digest/excerpt in form-list-source.md and exact rejecting/accepting controls in runs.json.
- DONE: Final counts over all six sections: N, M covered whole with a recorded nonzero exit, K README bytes removable if the M went; output is a list for the Captain's ruling and nothing is deleted
  N=93, M=1, K=68 bytes at unchanged source/base/candidate c2f035b6612f5edb42220576b3414e993531ffd6; row 71 has isolated R2 edit/delete exits 1 and an unchanged exit 0, with the exact 68-byte source slice in evidence/implementation-2/summary.json.
- DONE: Apply Captain amendment 1 and the replacement stop condition
  Installed role_triggers.py exited 0 with Budget 2 implementation and 1 validation cycles, spent implementation 2/validation 0; Supersedes is none, so no AC block moved. All five sections and the form list are covered; FO did not end the budget.
- DONE: Record actual probes and their limits without changing product bytes
  146 native CLI/function-adapter runs are retained with pre-command file bytes, observed exits/stdout/stderr and any tool-authored scratch-file changes. Row-71 edit/delete returning 0 falsifies M=1; duplicate live AC IDs, false round counts, missing applied records and synthetic reviewer lines remain accepted counterexamples, not hidden passes.
- DONE: Retain public evidence and close implementation-2 scratch
  scratch.py close exited 0, removed 16015445 bytes and retained 14 files (551.0 KiB); exact output is in implementation/report.md, hashes in evidence/implementation-2/SHA256SUMS, and the first-cycle evidence manifest remains intact.
- SKIPPED: State commit and synchronization
  This dispatch explicitly says not to run spacedock state commit and that FO commits; all authorized entity/report/evidence changes are left uncommitted for FO. No git add fallback, product commit, push, PR, review request or external diagnostic operation was run.
- SKIPPED: Live POC design-surface obligation, full package suites and roborev
  The dispatch excludes design_surfaces.py check on this POC route; only Pilot-shaped throwaway fixtures audit the research list. roborev not run: read-only measurement with no code candidate to review; full suite, native agent behavior, live deployments and database resets are not claimed.

### Summary

This report supersedes the earlier implementation stage report and early-stop aggregate conclusion under Captain amendment 1, while preserving its first 15 rows. The expanded read-only audit finishes all six README sections and the listed form checks with N=93, M=1, K=68 bytes; no rule is deleted and the product branch remains clean at the same pinned commit. FO owns the pending state commit, independent validation and study-side report copy.

## Stage Report: validation

- DONE: Re-count the rule sentences of at least two of the six sections at the pinned commit and compare with the report's rows
  README at c2f035b66 has the reported SHA-256 and 41076 bytes. I re-counted four sections by hand: Review-finding disposition 15, Decision records 2, Number guards 9, FO steps: number guards 16. All four match all-rows.json. All 78 inventory byte spans equal their quoted rule text. Not re-counted: Dispatch facts (15), FO steps: review findings (36).
- DONE: Re-run the single "covered whole" row's violating input and at least eight other recorded probes, and compare exit codes
  Row 71 (`check` freezes a migration in a commit recorded `Applied at:`): I built my own git fixture, not the author's. Edit of the applied migration exits 1 (R2), deleting it exits 1, unchanged exits 0, edit with no record exits 0 (evidence/validation-1/row71-own-probe.sh and .log). I also ran the author's expand.py in scratch against the clean pinned worktree: 146 of 146 exit codes match (expand-replay-compare.log). That is the same harness, not independent. Recorded input_files alone cannot replay a probe; replay.py got 20 of 119 matching, the rest needing files the record omits.
- DONE: For at least eight rows judged covered part or uncovered, try to find an existing check that rejects every breach; name any row whose verdict I would change, and what that does to M and K
  I found no check that rejects every breach for rows 16, 21, 72, 76, 77, 83, 65 and 66. Row 76: `reserve --kind migration` on a poc task exits 0 and prints `Migration: 0002`, so "reserves no number" is unenforced. Rows 21, 72, 77, 83, 16: no non-test script contains `value-ac[`, `Not applied`, `Applied: none`, `boundary-crossed` or `candidate revision`; `number_guards.py` matches only `Applied at:`. Rows 65 and 66: `decision_ledger.py` rejects a missing, lowercase or typoed declaration, but `Recommendation: followed` beside a contrary choice exits 0. One row I would argue the other way: row 86 (108 bytes). Each clause has a probed exit (db task without path exits 2, POC unguarded exits 0, `none` rejects an added numbered SQL file exits 1); the author held it at part only because a declaration does not prove absence. If the Captain reads the sentence as a description of tool behaviour, M=2 and K=176 bytes. Row 71 stays covered whole by the author's own rule, with limits below. Under the strictest reading M=0 and K=0.
- DONE: A minimal acceptance script FO can run, the limits of what I checked, and unverified obligations
  Acceptance: export `kc-dev-flow-2/scripts` at c2f035b66 and run `bash evidence/validation-1/row71-own-probe.sh <that dir>`; expect exits 0,1,1,0,0,0 in order. To replay all 146 probes run the author's `evidence/implementation-2/expand.py --repo <clean worktree at the pin> --scratch <empty dir> --out <empty dir>`; it asserts every expected exit itself. Limits: R2 only matches `^Applied at:<env> <sha>` lines in the task's `## Number guards` section and only files named `NNNN_name.sql` (the script's own Limits text), so an `Applied at:` line under another heading, a lowercase label or a record with no environment token does not freeze (exit 0 in my probe); a README reading where "recorded" means anywhere in the task would make row 71 part. Not verified: Dispatch facts and FO steps: review findings sentence counts; the nine form-check families and their rows; the count of covered part (29) and uncovered (63) beyond my sample; that removing a sentence changes no behaviour (AC-1's stated limit). Probes run singly out of order after the full run differed because the author's fixture files are rewritten between runs; that is a replay-order limit, not a mismatch.
- DONE: Run adr_lint.py and record the exit code
  `adr_lint.py docs/adr --since c2f035b66` exit 0, 79 files checked, no ADR added (evidence/validation-1/adr_lint.log). design_surfaces.py not run, per the dispatch.
- SKIPPED: roborev
  roborev not run: read-only measurement with no code candidate to review.
- DONE: Scratch close
  `scratch.py close` output: "Scratch removed: <scratch>/validation-1 (5303838 bytes); Evidence: evidence/validation-1/ (6 files, 3.5 KiB)". Product worktree status clean; no product change, push or PR.

### Summary

AC-1 verdict: PASSED with the limits above. The counts N=93 and K=68 re-derive for the four sections I re-counted and for row 71's byte span; M=1 holds by the author's rule, from my own edit/delete probes (exit 1) against a control (exit 0). The report's covered-part and uncovered verdicts held on all eight sampled rows; one borderline row (86) could move M to 2, K to 176. FO should present M as 1, with the reading-dependent range 0 to 2, to the Captain.
