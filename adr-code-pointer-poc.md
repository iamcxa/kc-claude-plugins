---
title: Does a code-side pointer to the protecting ADR stop an agent from undoing a choice whose reason the code does not show?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:adr-code-pointer-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-code-pointer-poc-backlog-1
              briefing:
                id: briefing:adr-code-pointer-poc:backlog:attempt-1:revision-1
                digest: sha256:ce770ddd976f4aaef4a1e368d2a6e53504ca4d3f7f3d62d81fd5880bb6e209f9
                room-ref: ./adr-code-pointer-poc/review/backlog/briefing-1
---

Filed on the Captain's 「可以，先測試這個，然後再考慮其他方案。」 (chat, 2026-10-23), answering FO's 「我建議的下一步：撤回這道關卡，先開一個 POC。同一題，在程式碼旁加上那行註解，Claude 和 Codex 各跑 2 次，共 4 次。…要撤回這道關卡、改開註解 POC 嗎？」, after FO proposed a code-side comment as a cheaper alternative to an edit-time hook (dev2 task `adr-protected-path-guard`, its backlog gate withdrawn).

## Scope

- Question: in the archived S14 scenario of `adr-hidden-reason-poc`, add one line at the protected code site in `src/report_mailer.js` pointing at the protecting ADR (for example `// read-back is deliberate: see docs/adr/0024-…`), with the ADR present and kc-adr not installed; does the agent keep the choice?
- Comparison: the archived S14 A0 cells (ADR present, no comment, no kc-adr): 1 of 4 undone; the archived control (no ADR): 4 of 4 undone.
- Decision it feeds: if the comment holds, kc-adr's writing rule asks for a code-side pointer and the linter checks that each declared file carries it, with no hook; if it does not, the edit-time hook in `adr-protected-path-guard` is reconsidered with the other options the Captain named.
- Upstream first: copy `_archive/adr-hidden-reason-poc/harness/` in this state checkout into this task's folder; the pass rule, task prompt and grader stay as archived; the only world change is the comment line.
- Budget and stop point: one arm (comment), Claude and Codex, two runs each, 4 counted runs; an infrastructure failure gets one retry per cell, then stop and report.
- Fictional data only. Non-goals: building the linter check or a hook; changing kc-adr.

## Acceptance criteria

**AC-1**: The harness copy differs from the archived one only by the comment line at the protected site and the new arm's wiring; the diff is committed before the first run, and the archived falsifiers still pass.
**AC-2**: The comment arm runs on Claude and Codex, two runs each, scored by the archived pass rule.
**AC-3**: The report gives each run's result with its run record, whether the agent kept, moved or deleted the comment, and whether it read the ADR, and states which of "code-side pointer" or "reconsider the hook" the result supports, with limits, without choosing.

## FO alignment

Alignment: not needed before implementation: the Captain approved the arm and the run count in chat; POC skips ideation.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no shipped change.
