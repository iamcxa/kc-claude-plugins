---
title: When an ADR-protected choice shows no reason in the code, does an agent undo it during an unrelated refactor, and does kc-adr change that?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:adr-hidden-reason-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-hidden-reason-poc-backlog-1
              briefing:
                id: briefing:adr-hidden-reason-poc:backlog:attempt-1:revision-1
                digest: sha256:3d3a1467a9819ac11eaf8318ea58cc84e466317972954f241eef94cec7409009
                room-ref: ./adr-hidden-reason-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-hidden-reason-poc:backlog:1
                briefing: briefing:adr-hidden-reason-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T07:42:35.278987Z"
                decision: approve
                reason: 'Captain 「准」 (2026-10-23) to the backlog gate: accepts the question, the no-ADR control, 12 counted runs and the stop point, profile poc.'
              application:
                target-stage: implementation
                state: consumed
---

Filed on the Captain's 「開」 (chat, 2026-10-23), answering FO's 「要不要開「理由藏起來」POC？做法是 ADR 保護的設計在程式碼上看不出理由，再加一組對照，確認題目真的會讓 agent 犯錯。」, after `adr-silent-undo-poc` closed with no cell needing the ADR because the protected flag was visible at every call site.

## Scope

- Question: an accepted ADR protects a choice whose reason the code does not show (no flag, comment or sibling that marks it deliberate); in a refactor task that does not mention ADRs, do agents undo it, with and without kc-adr?
- Decision it feeds: if agents undo it, kc-adr gains a deterministic guard (an ADR declares the code paths it protects, and a check flags a diff touching them); if they keep it, kc-adr stays at writing, superseding and placement.
- Control: the same scenario with the ADR removed. The control must show agents change the choice, or the scenario cannot detect the failure and the arms prove nothing.
- Upstream first: copy the harness from `_archive/adr-silent-undo-poc/harness/` in this state checkout (S13 world, `score.py --rule s13`, recording-db grader) into this task's folder and add the new scenario there.
- Fictional data only; nothing from a private decision repository.
- Budget and stop point: arms C (no ADR), A0 (ADR, no kc-adr) and B1 (ADR, kc-adr at main a476b5ff) on Claude and Codex, two runs per cell, 12 counted runs. If the control does not change the choice in at least 3 of its 4 runs, stop after the control and report; do not run A0 or B1.
- Non-goals: building the guard, adding an AGENTS.md pointer or a code-side comment, or changing kc-adr.

## Acceptance criteria

**AC-1**: The harness gains one scenario whose protected choice has no visible reason at the code site, with the pass rule (choice unchanged, or the agent stops and names the ADR), grader and falsifiers committed before the first run.
**AC-2**: The control runs first on Claude and Codex, two runs each; A0 and B1 run only if the control changed the choice in at least 3 of 4 runs, two runs per cell on each host, scored by the committed rule.
**AC-3**: The report gives each run's result with its run record and states which of "add the guard" or "stop at the current three points" the result supports, with its limits, without choosing.

## FO alignment

Alignment: not needed before implementation: the Captain approved the question and the control; POC skips ideation.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no shipped change.
