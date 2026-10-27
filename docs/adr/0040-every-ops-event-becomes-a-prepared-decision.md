# 0040. Every ops event becomes a decision an agent has prepared, and each decision makes the next easier to hand to an agent

Date: 2026-10-23

## Status

Accepted

## Context

kc-ops-inbox began from the Captain's outcome of 2026-10-19: 「拉出一個ops inbox抽象，確保必要資訊可以一次到位到inbox 變成一個聚合事件，然後後面可以投影到slack，或是投影給agent … 目的是人要知道，然後agent要同步進行解決方案呈現，要有一個repo內的ops workflow，來按照sd流程進行排查」. Two POCs closed PASSED (`hermes-ops-fo-exe-dev-poc`, 2026-10-21; `inbox-exactly-once-delivery-poc`, 2026-10-23). The first r1 design centred on a one-step setup command and permission isolation. Before its gate the First Officer proposed a day-2 axis and a ten-item priority: Netlify and Sentry already notify, so the value is not a faster alert. The Captain confirmed it, and r1 was sent back and re-cut around it (task `ops-inbox-r1-setup-and-isolation`, amendment 1).

## Decision

**Words:** 「對，這樣可以，這可以使用 kc-adr 紀錄嗎？還是用 dev2 adr 紀錄？」 — Captain, 2026-10-23, in chat, to the First Officer's axis and priority (verbatim question in the task folder, `asked-day2-axis-2026-10-23.md`)

**Words:** 「同意」 — Captain, 2026-10-23, in chat, to 「照這樣做嗎？具體是：把現在 r1 的 ideation 退回；第一件事寫這份主軸 ADR；再照優先順序重擬 r1：聚合、帶脈絡的診斷、真的接上 relay 放前面，設定自動化延後。」

**Options considered:**
- each ops event reaches the person as a decision an agent has already prepared, and each decision makes the next easier to hand to an agent (chosen)
- a faster alert: Netlify and Sentry already notify
- setup automation and permission isolation first (the attempt-1 r1 focus, 2026-10-23)

**Recommended:** the axis and the priority order, as the First Officer proposed them.

kc-ops-inbox work is ordered by this priority, highest first: 0 (precondition) the platform limits the agent's authority, so it cannot push the default branch or merge; 1 the agent investigates at the same time and presents a solution; 2 the necessary information arrives complete and the events of one matter aggregate into one; 3 the person knows at once; 4 every step is recorded in the repository's ops workflow, with the Captain's words; 5 decisions connect to kc-decision-log or the project's ADRs; 6 more response adapters (dot, a Netlify agent and others); 7 live streaming, live conversation with the agent, the simplest UI; 8 independent deployment per project and a generic flow with per-project configuration; 9 versioned evolution such as ops and ops2. A release does not take a lower item at the cost of a higher one. Progress is measured by two numbers: the time from an event to a recommendation the person can decide on directly, and the share of the person's decisions that follow the agent's recommendation.

## Consequences

Easier: deciding what a release takes, and turning each recorded decision into precedent. Harder: setup stays a written runbook with Captain-only steps until item 8 is taken. Not built: kc-decision-log; any decision the agent takes alone, which needs its own ruling (kc-claude-plugins ADR 0011 governs delegation to the First Officer). Reopen when the Captain reorders the items, or when the second measure is high enough that he asks for delegation.
