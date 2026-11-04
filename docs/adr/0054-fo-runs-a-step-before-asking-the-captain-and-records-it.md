# 0054. FO runs a step before asking the Captain and records it

Date: 2026-11-03

## Status

Accepted

## Context

The relay PR #412 validation gate was presented at b7732d43 before FO ran
its acceptance script at e623efd2. The Captain said 「都准。但注意，412 你以後應該要自己先測試過才轉給我 UAT，這是 dev2 規範有缺，還是寫得不夠好沒有讓你執行？」
(relay chat, 2026-10-21, relayed in the task's Scope). Separately, the qnow
Captain card named a fixture script at a path moved into the archive before
the ask. The task fo-tries-what-it-asks-the-captain records both sources.
The existing acceptance-script rule was unenforced; ad-hoc asks had no rule.
This triggers ADR 0024's reopen clause for a broken listed rule.

## Decision

**Words:** 「可以」 — Captain, chat, 2026-11-03, ideation gate of
fo-tries-what-it-asks-the-captain.

**Asked:** 「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成『在 kc-journey-map 登記 journey-progress/v1，預算放寬為兩個 PR，kc-journey-map 那個先合併』，可以嗎？」
The gate record accepts every recommendation in this task's design: chat
checks run by FO, a 55-word workflow budget raise (5781 to 5836), and reversing
ADR 0024 D3 under its reopen clause.

**Options considered:**
- FO records every requested step and runs the existing delivery-gate script;
  validation preparation requires a passing record at the dispatched candidate
  (chosen).
- Keep only the acceptance-script rule within its old word budget; ad-hoc asks
  remain uncovered.
- Build outgoing-message hooks in each host; that is another product's scope.
- Leave acceptance observations chat-only under ADR 0024 D3; no later reader
  can check them.

**Recommended:** The recorded steps, FO-run check, +55-word budget raise and
reversal of ADR 0024 D3, as accepted at the ideation gate.

**Protects:** none

Before asking the Captain to run or look at anything, FO exercises the steps
as written in a fresh shell or real browser up to his credentials, writes
Asked, Ran, Observed and any Only he can reason in captain-steps/N.md, and
runs delivery_gate.py steps against the message. The message shows each step
beside its output and the part only he can do. Validation summaries name the
passing record on Captain steps:, bound to a latest dispatched Candidate.
The observer reads these records; the acceptance-step phrase leaves its
chat-only list. Other ADR 0024 decisions remain in force.

## Consequences

An adopter's next validation question holds until FO supplies the record;
in-flight tasks gain no exemption. Each ask adds a record and every FO startup
reads 55 more words, partly offset by shortening the validation passage.
The script checks form, paths and coverage; it never executes commands or
proves an observation true. A prose ask or chat sent without running the
check can escape it. FO never uses the Captain's credentials. Reopen if these
limits require host enforcement or recorded steps still miss a demonstrated
untried ask.
