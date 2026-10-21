---
id:
title: Agents consult the governing ruling and route new information to its right home
status: backlog
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
---

P1 proves the mechanics only: a task description tells the worker to use the skill, so it does. The value the user wants is unproven. Does an agent consult the governing ruling before deciding when nobody reminds it, and does it put new information in the right home rather than turning everything into an ADR? The user, 2026-10-21: 「確保 skill/hook 可以讓 agent 知道要讀 ADR 之外還要知道可以怎樣區分，因為不是全部資訊都要寫到 ADR」; he approved building this POC (「建立這個 POC」). The result also decides whether kc-decision-log could later replace dev2's ADR reading, which must first be proven easier for agents (boundary contract draft, PR #691).

## Scope

Riskiest assumption: a short skill, or a skill plus a session-start hook listing ruling titles, changes what an agent does at decision time.

- Rule under test: the routing table in `docs/journey/kc-decision-log/boundary-contract.md` (PR #691; the draft as the Captain last saw it).
- About ten realistic scenarios over a fictional decision space and a fictional repository with dev2 ADRs. The scenarios cover a cross-repo direction, a task-only trade-off, a working preference, a deferred user-facing feature, an engineering constraint, and a scenario where an existing ruling already settles the question.
- Three conditions: no help; the `read-ruling` skill only; the skill plus a session-start hook that lists ruling titles. Each condition runs on Claude and on Codex, with the model pinned per run and recorded.
- Two measures per run: did the agent consult the governing ruling before deciding (from its tool calls), and did it place each new piece of information in the home the table names. Expected answers are written by hand before any run.
- Uses the CLI and skill from `kc-decision-log-cli`, so it starts after that task merges. The hook is a disposable POC harness, not the shipped S30 hook nor dev2's `agent-reads-governing-adr` hook. Its results and scenarios are offered to that dev2 task.

Non-goals: shipping a hook or a rule; changing dev2; real private rulings (fictional data only); deciding the replacement question (this returns evidence for the next planning decision).

Budget: one working day of active effort. The run count is declared before launch: about 10 scenarios x 3 conditions x 2 hosts, about 60 agent runs; token cost unmeasured. Stop when the declared runs finish, when either host cannot run the harness, or when the run count would exceed the declaration by more than 20%.

## Acceptance criteria

**AC-1**: A results table gives, per condition and host, the share of scenarios where the agent consulted the governing ruling before deciding, and the share where each new piece of information went to the home the table names. Each cell traces to the run's recorded tool calls and outputs.
Verified by: the committed harness re-run from its README reproduces the table's counts within run-to-run variation, which the report states.

**AC-2**: Expected answers for every scenario were committed before the first run, and no scenario or expectation changed after a run without a recorded reason.
Verified by: commit order of the expectations file and the first run log.

**AC-3**: The report states what the result does not prove: sample size, fictional data, the pinned models, the hook being a harness. It also states which rows of the routing table the agents most often got wrong.
Verified by: the report section, checked against the results table.

## FO alignment

Not needed before implementation. The Captain asked for this POC and approved building it (「建立這個 POC」, 2026-10-21); the scope above restates the design he was shown. Release review: not needed: the task belongs to no release (it informs deferred story S30 and dev2 task `agent-reads-governing-adr`).
