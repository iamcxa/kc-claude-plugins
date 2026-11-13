# 0083. Workers check the existing chain before new work

Date: 2026-11-13

## Status

Accepted

## Context

The existing capability audit applies only to a bounded class of existing-code
changes and skips greenfield work, named broken seams and mechanical edits.
The Team dispatch fact checks shared work and ownership; neither rule covers a
new task's whole relevant dependency chain. ADR 0037 explicitly kept this broader
upstream/decision check as a separate following task.
The task new-work-checks-what-exists-first tried a single principle home linked
from ideation. Source-loading checks and one unblinded same-worker dispatch replay
were observed; independent worker compliance and savings were not established.

## Decision

**Words:** 「照上面這個理解，開「先查上游」這張任務」 — Captain, chat, 2026-10-23,
as quoted in the task's Scope.

「這裡的問題是，做新需求時應該要先查上游，不管幹嘛都要先確認已有的東西才去評估怎樣加入新的東西。說明一下你的理解是怎樣」
— Captain, chat, 2026-10-23, as quoted in the same Scope.

「放階段原則（建議）」 — Captain, host question dialog, 2026-11-13,
ideation gate attempt 1 of new-work-checks-what-exists-first; recorded at
2026-11-12T17:37:04.390686Z.

**Asked:** 「「做新東西前先查既有的」這條規則要放在哪裡？我建議放進階段原則（worker 每個階段都會讀的守則）。worker 已用這個放法做出試作：沒有這段文字時檢查不過，加上後通過，並在一次重播的派工中先寫出查了什麼、找到什麼才開始設計。核准等於接受這個放法，同一個 worker 接著實作。」

The Scope also relays the Captain's 「讓 agent 務必先查既有狀態的機制，ADR也是一種既有狀態」
and the accepted sentence 「生效中的 ADR 也算既有狀態，worker 必須列出管到這次要動的檔案或行為的 ADR，沒有就寫「無」。」
from the kc-adr FO's session. The operative sentence below follows the accepted
Scope; this record does not turn the relayed source into a new direct ruling.

**Options considered:**
- Stage principles: one check in implementation principles, linked from ideation
  before design, and read by POC before coding (chosen).
- Seed: capture findings at admission, before the worker investigates, with a
  new field/check and stale-record risk.
- Gate content: expose findings at review, after design; POC has no design gate.

**Recommended:** Stage principles with one home linked from ideation, the probed
option the Captain selected.

**Protects:** none

Before designing or coding a task, inspect its own repository, relevant upstream
packages/frameworks, sibling projects and third-party tools. A tool's own docs
or source define its contract; a sibling's usage does not. Name in-force ADRs
governing the files or behavior, or write none. State what was checked, what was
found, inaccessible sources and whether the addition uses, extends, changes or
replaces what exists in the existing design/report. Reuse a completed check and
recheck changed scope or facts. The narrower capability audit remains intact.
POC checks before coding without gaining ideation or another gate.

## Consequences

The existing stage-skill loading path carries the instruction. Implementation
principles gain 106 whitespace-separated words; ideation links to that section
while its direct principles text shrinks by six words. No shared workflow-word
budget rise, runtime enforcement, receipt schema, dependency, extra POC gate or
adopter-specific upstream list is introduced.
The instruction can still be skipped. The recorded local replay does not prove
cold-worker behavior, cross-host compliance, independent acceptance or saved
time. Revisit if ordinary dispatches fail to produce checked/found findings
before a proposal, or if the additional reading costs more than the check yields.
