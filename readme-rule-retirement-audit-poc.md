---
id:
title: Which README rule sentences does a check already enforce whole (read-only retirement audit; a list for the Captain's ruling)
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
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
