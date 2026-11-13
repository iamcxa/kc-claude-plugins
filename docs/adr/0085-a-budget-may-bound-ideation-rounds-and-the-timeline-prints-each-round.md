# 0085. A budget may bound ideation rounds and the timeline prints each round

Date: 2026-11-13

## Status

Accepted

## Context

ADR 0077's per-stage forms count implementation and validation, while ADR 0084
holds a third Pilot design dispatch through a First Officer instruction. ADR 0080
counts dispatches and times a stage but does not print each round. The local probe
of budget-form-counts-ideation-rounds-and-times-each-round replayed a real task's
three design dispatches: a bound of two held the third, and the timeline recovered
three rounds. Across 247 tasks the probe changed no held/not-held result; 23
outputs changed in text. The Captain approved all five design recommendations.

## Decision

**Words:** 「核准預算寫法的設計，五項都照建議」 — Captain, chat,
2026-11-13, ideation gate of
budget-form-counts-ideation-rounds-and-times-each-round.

**Asked:** 「決定：要不要核准「預算把設計輪數算進去」的設計並開始實作？建議核准，五個決定都照建議：一、寫法用你的原話「N ideation, N implementation and M validation cycles」，既有的兩種寫法意思不變；二、Pilot 的預算沒寫設計輪數時預設兩輪、由程式把關，流程文件裡那句靠我記得的規則刪掉（少 2 個字）；三、設計派工時只檢查預算，不檢查欠不欠顧問諮詢；四、新增一份決策紀錄，是擴充既有三份，不取代；五、每一輪的結果取自那一輪關掉的關卡紀錄，不看階段報告。 同意即接受：有一張待辦任務的預算剛好寫了「一輪設計」，上線後它第二次設計派工會被擋下來問你；預設兩輪不會顯示在預算那一行，只顯示在派工時的提示（每次多 6 個字）；Prod 和沒寫可計數預算的任務不受設計輪數限制；到目前為止沒有任何任務的設計派到第三次，所以這道把關還沒有被真實需要過。」

**Options considered:**
- D1: accept `N ideation, N implementation and M validation cycles`, with digits
  or English one to ten, preserving the existing forms (chosen).
- D2: add a script-enforced default of two ideation rounds to countable Pilot
  budgets without an explicit ideation count (chosen), rather than retain only
  the prose hold or require every existing budget to be rewritten.
- D3: check budget alone at ideation dispatch (chosen); the full role check would
  newly hold a design dispatch on an owed engineering-reviewer call.
- D4: extend ADRs 0077, 0080 and 0084 with one record (chosen), rather than
  supersede them.
- D5: use the gate outcomes closed within a round, joined in order (chosen),
  rather than infer a per-round result from stage reports.

**Recommended:** D1 through D5 as the ideation gate recommended and the Captain
approved.

**Protects:**
- `kc-dev-flow-2/scripts/role_triggers.py` — ideation bounds, Pilot default and budget-only mode
- `kc-dev-flow-2/scripts/dispatch_stage.py` — budget-only check before building an ideation dispatch
- `kc-dev-flow-2/scripts/task_timeline.py` — per-round times and results

The new form extends ADR 0077. Highest plain ideation record number counts the
rounds, including the pending dispatch. A countable Pilot budget without that
bound gains two ideation rounds, including a budget with a total-dispatch cap;
both caps apply. Prod and uncountable budgets gain no implicit ideation cap.
ADR 0077's first-record exemption, amendment authority, total counting and default
hold outcome remain in force. Ideation dispatch checks only the budget, removes
an unbuilt record on hold and prints the count when applicable; implementation
and validation retain the full special-role check.

This makes ADR 0084's D4 hold script-enforced, amending only the hold portion of
its consequence “instructions, not script enforcement.” Its other probe bounds,
branch cleanup and profile rules remain unchanged. The workflow loses two words
under ADR 0020; no word-budget raise is granted here.

The timeline extends ADR 0080 with each round's start, end, minutes and result.
Its result is the gate outcomes closed in that round, else `gate open`, `running`,
`redispatched`, `next <stage>` or `archived` from the following record boundary.
Stage reports do not determine a round's result. Minutes still spend no budget.

## Consequences

The count appears in dispatch output rather than rewriting an implicit bound into
the Budget line. Pilot build/check output grows by six words; design dispatches
gain a budget line. A worker failure without a closed gate reads `redispatched`,
and late-committed records can yield zero-minute rounds. The probe is replay and
fixture evidence, not a released live third-dispatch hold or a speed measurement.
Reopen if released dispatches bypass the bound or the shared records cannot
supply useful per-round boundaries.
