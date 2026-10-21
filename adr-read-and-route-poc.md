---
id:
title: Agents consult the governing ruling and route new information to its right home
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-adr-read-and-route-poc
pr:
gates:
    version: 1
    records:
        - id: gate:adr-read-and-route-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-read-and-route-poc-backlog-1
              briefing:
                id: briefing:adr-read-and-route-poc:backlog:attempt-1:revision-1
                digest: sha256:72e549fa889a0d1e074885f27aec4e19dc101a5f34863e6fb3e44150151ef1f4
                room-ref: ./adr-read-and-route-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-read-and-route-poc:backlog:1
                briefing: briefing:adr-read-and-route-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T06:13:26.845458Z"
                decision: approve
                reason: Captain replied 「照建議」 to the six-item batch (2026-10-21), whose item 2 approved this POC backlog gate as filed, starting after kc-decision-log-cli merges. Consume waits for that start condition.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-21T06:22:26Z
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

## Captain amendments

### Amendment 1 — 2026-10-21, chat
Captain: 「先跑 poc」 (P1 FO's Paseo session "decision-log P1 重切與 dev2 交接")
Asked: 「請你決定一件事：先用預覽工具跑四組條件的 POC，再決定任務一的規模嗎？」 with the proposal: 「1. 現在就跑 POC，用設計階段那個可以實際操作的預覽工具。」「2. 多加第四種條件，專門比 CLI 本身：「skill 教 agent 用 git 加 shasum 讀、看 Status 行」對比「skill 加 CLI」。量三件事：做決定前有沒有去查；交接時版本和指紋對不對；資訊放得對不對。」「3. 先講好判斷規則：CLI 那組沒有明顯勝過 git 那組，任務一就縮成「skill 加設定檔」（只有情境裡真的出現主題衝突，才保留一個判斷生效的小腳本）；勝過就照原設計做。」「POC 從約 60 次執行增加到約 80 次。」
Supersedes: none

### Amendment 2 — 2026-10-21, chat
Captain: 「可以」 (P1 FO's Paseo session, reply to a two-item batch)
Asked: 「1. Codex 的第四組（上一則）：只在 Claude 上跑，不繞過 Codex 的 hook 信任機制。」「2. 重建測試世界：照上面「真實規模、不偏袒 CLI、拿掉查詢提示」的做法重建，第一組重跑。總共約 90 次執行：已經用掉的 20 次加上接下來 70 次，在 worker 設的上限 96 次以內。」
Supersedes: none
