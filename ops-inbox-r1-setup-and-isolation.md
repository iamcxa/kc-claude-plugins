---
title: A project connects to its own ops inbox in one setup step, a signed event reaches a person and an agent, and the inbox can wake only that project's ops workflow
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:ops-inbox-r1-setup-and-isolation:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:ops-inbox-r1-setup-and-isolation-backlog-1
              briefing:
                id: briefing:ops-inbox-r1-setup-and-isolation:backlog:attempt-1:revision-1
                digest: sha256:1bc2b0c394fd8bcc1d00cc489d1fb65b6a81b4fd6a88af859d4a03f022954e7e
                room-ref: ./ops-inbox-r1-setup-and-isolation/review/backlog/briefing-1
---

inbox-r1 of the `kc-ops-inbox` package. Two POCs closed PASSED: `hermes-ops-fo-exe-dev-poc` (2026-10-21: a GitHub App token under no-bypass rulesets reaches only ops/* branches and Draft PRs; a headless Claude Code First Officer on a hosted runner files one ops task; the Captain's own GitHub review is the recorded decision) and `inbox-exactly-once-delivery-poc` (2026-10-23: three sends of one signed CloudEvents event gave one workflow run; a tampered send started nothing; the inbox credential could not push; the inbox core imports only node:crypto). Both proved the inbox code is small; the cost is the per-project setup the Captain did by hand (two Apps, rulesets, secrets, Slack webhook) and permission isolation.

Captain's words:
- Outcome (2026-10-19, design brief): 「拉出一個ops inbox抽象，確保必要資訊可以一次到位到inbox 變成一個聚合事件，然後後面可以投影到slack，或是投影給agent … 目的是人要知道，然後agent要同步進行解決方案呈現，要有一個repo內的ops workflow，來按照sd流程進行排查」
- Authority (2026-10-19): 「被叫起來的agent有source存取權限，可以跑 ops flow推entity task到separate branch，但是沒有權限做危險動作例如推main且沒有權限合併pr」
- Contract (2026-10-21): 「應該要先定義好 inbox 合約，由不同管道收取，且 platform 本身也要提供 hook 可以接，不能直接依賴第三方平台」
- Platform (2026-10-21): 「你要注意一件事，平台是剛好是 netlify，不是平台一定是 netlify。」
- Focus (2026-10-23): 「好」 to: r1 Pilot 的範圍改成以兩件事為主：設定流程（一步就能把專案接上 inbox，替你處理這次那六件手動設定）與權限隔離（inbox 只能叫起它自己的那個 workflow）；合約 v1 仍是 r1 的第一件事。

## Scope

- Contract v1: CloudEvents 1.0 attributes and Standard Webhooks signing, an allowlisted data field set, the dedupe key, and a version; published in the package with a validator and fixtures for relay's ceiling event and a Sentry-shaped event. Relay's own hook is written by relay against this contract in a relay task, not here.
- Setup: one command connects a project to its inbox: it creates or updates what an agent may create, lists each step only the Captain may do (App creation, keys, Slack webhook, secrets, ruleset changes) with the exact command, and reads every step back.
- Isolation: the inbox's credential can start only the project's ops workflow (POC2 finding F2: Actions write is repository-wide).
- Event to person and agent: a signed event yields one Slack notice whose arrival is observed, and an FO on a GitHub-hosted runner files one ops task with one recommendation on an ops/* branch and a Draft PR; the Captain's GitHub review is recorded without pushing to the PR branch, so the approval is not dismissed (POC1 finding).
- Platform-neutral core: the same core runs under the Netlify adapter and under a second adapter or plain Node harness.
- Non-goals: relay's live producer, raise-from-link, Slack Q&A, qnow live, the in-service FO, Spacedock gate-actor authentication (upstream), guaranteed delivery and reconciliation (POC2 chose at-most-once; ideation states the delivery semantics for the Captain).
- Budget: at most 3 days (FO proposal; the Captain sets it).
- Stop conditions: isolation needs a credential that can push or start other workflows; the setup cannot read back a step it claims; the estimate exceeds the budget. Each returns a planning delta to the Captain.

## Acceptance criteria

**AC-1**: Contract v1 validates the relay-shaped and Sentry-shaped fixtures and rejects a fixture with a missing attribute, a bad signature or a field outside the allowlist.
Verified by: the validator's output on each fixture, with exit codes.

**AC-2**: On a scratch project, the setup command completes the agent-doable steps, prints each Captain-only step with its exact command, and reports every step as verified by read-back.
Verified by: one full setup run log on a scratch project, and the read-back of each created resource.

**AC-3**: The inbox's credential starts the project's ops workflow and is refused when it tries to start any other workflow in that repository.
Verified by: one accepted dispatch and one refused dispatch with the same credential, against a repository holding a second workflow with secrets.

**AC-4**: A signed event produces one Slack message seen in the channel and one ops task with one recommendation on an ops/* branch with a Draft PR; after the Captain's review, the gate is recorded with his words and his approval still stands on the PR.
Verified by: the Slack message with its time, the task and Draft PR, the gate record, and the PR's review state after recording.

**AC-5**: The inbox core passes the same tests under the Netlify adapter and under a second adapter or plain Node harness.
Verified by: both test runs and the core's import list.

## FO alignment

Direction alignment before ideation: not needed; the Captain set the focus on 2026-10-23 and the contract direction on 2026-10-21. Ideation runs on opus (contract and authority boundary are hard to reverse).
Surfaces: ui
Visible change: An operator runs one setup command for a project; afterwards each signed event shows up as one Slack message and one ops task with a Draft PR that the Captain decides by GitHub review.
Release review: not needed: the kc-ops-inbox journey map (inbox-r1) is only on branch iamcxa/kc-ops-inbox at 0a1d59ce and not on the trunk; set journey fields when it lands.
Captain standing ask, 2026-10-21: 「請持續針對套件的意義做觀察與回饋」. FO reports a package-value observation at each gate.
