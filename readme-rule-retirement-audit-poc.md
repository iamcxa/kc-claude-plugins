---
id:
title: Which README rule sentences does a check already enforce whole (read-only retirement audit; a list for the Captain's ruling)
status: implementation
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
