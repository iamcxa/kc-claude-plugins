# 0081. Held and closed tasks are named at startup and idle

Date: 2026-11-12

## Status

Accepted

## Context

The task held-and-closed-tasks-leave-the-design-queue found ten held tasks
listed as ideation work. Spacedock already derives gate-readiness as
not-applicable and excludes them from status --next. The startup and idle
tasks output did not name them. Captain amendment 1 permits this record of
the ideation ruling; it adds no other decision.

## Decision

**Words:** 「五份都核准（建議）」 — Captain, host question dialog,
2026-11-12, ideation gate attempt 1.

**Asked, relevant passage:** 「四、擱置的任務：啟動和閒置檢查多印一行列出擱置中的任務，每張擱置任務引你的原話寫明何時重開或已關閉；已關閉的任務留在原階段、不用強制手段歸檔；其中「進場檢查要求對齊結果」那張記為已關閉、「關卡摘要逐項寫理由」那張維持擱置、「旅程畫布託管試作」那張不動，留給它所屬的工作階段問你。」

**Options considered:**
- Name held tasks in startup and idle output; require a verbatim reopen or
  close line in each Held section; retain closed tasks at their stage (chosen).
- Force-archive held tasks as rejected, or request an upstream close route
  instead of retaining them at their stage (not chosen).
- Add a dispatch guard for held tasks (not chosen).

**Recommended:** the approved design's held-task output and quoted Held
sections, with closed tasks retained without force-archiving, subject to the
Captain's three task-specific dispositions quoted above.

**Protects:**
- `kc-dev-flow-2/scripts/pr_watch.py` — held_lines, the startup and idle held-task output

The tasks command names held tasks by stage and asks FO to write a Held
section whose Reopen when or Closed text occurs verbatim in the newest hold
reason or a Captain amendment. Missing instructions go to the Captain at
the next sitting. The query fails visibly if held tasks cannot be read.
FO owns the task-body edits; gate records remain intact. No new stage,
state field, dispatch guard or forced archive is introduced.

## Consequences

Startup and idle gain one fact line and a next line while Held sections are
missing or unverified. Plain status still lists closed tasks at their
original stage; the readiness field and startup/idle output distinguish
them from waiting work. The journey-canvas task remains unchanged pending
its own workflow's question. This records the approved direction, not a
new ruling about when that task reopens.
