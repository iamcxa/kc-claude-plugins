---
title: Any project sends a key metric to its ops inbox the same way, and kc-ops-inbox's contract v1 lands on main so projects can depend on it
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:ops-metric-event-protocol:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:ops-metric-event-protocol-backlog-1
              briefing:
                id: briefing:ops-metric-event-protocol:backlog:attempt-1:revision-1
                digest: sha256:e45198ee9013ca4fe71b8d304aa335538188da59c6491e9582f93b14c8cccb6b
                room-ref: ./ops-metric-event-protocol/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-10-26T14:31:05.182949Z"
                reason: 'Captain widened the protocol scope before ruling (2026-10-26 Ask UI: lifecycle, routing, sender rules, complete information and injection guard); the briefing no longer matches the scope.'
---

A shared protocol for key-metric events, owned by kc-ops-inbox, with qnow as its first adopter and relay's capacity ceiling as the shape to generalize. It also lands contract v1 (today only on the paused r1 branch) on the kc-claude-plugins default branch, because no project can depend on a contract that lives on an unmerged branch.

Captain's words:
- 「clerk 沒有這種功能，應該要自己算，做一個 api or hook 來做這件事，新使用者進來就 count +1，例如統計做在 blob 內？之後也可以串 posthog 收數據，這裡跟 ops-inbox fo 討論一下怎麼做比較好…我們會接下來需要實作 day2 agent manage flow」 (2026-10-25, relayed by qnow dev2 FO)
- 「要開，但我要你協同 inbox fo設計一個框架協議，讓未來的專案可以跟著使用，目的是設計出一個邊界，可讓不同專案用一樣的方式發送重點 metric 給 ops-inbox」 (2026-10-25, relayed by qnow dev2 FO)
- 「應該要先定義好 inbox 合約，由不同管道收取，且 platform 本身也要提供 hook 可以接，不能直接依賴第三方平台」 (2026-10-21)

Inputs: contract v1 at kc-claude-plugins branch spacedock-ensign/ops-inbox-r1-setup-and-isolation (kc-ops-inbox/contract/, committed 6e1098a7 and later); qnow dev2 task `sms-usage-alert` and qnow FO's boundary first cut (project side measures, holds the threshold, decides a crossing and sends one signed event per crossing with a deterministic id and counts only; inbox side verifies, dedupes on source+id, groups on subject and routes; shared: type naming, fixed metric data fields, signing-key provisioning, and delivery before the inbox is live using the same event body).

## Scope

- The metric-event protocol: the project-side and inbox-side boundary, the event type and data fields for a key metric, whether periodic snapshots are in v1, how a project obtains and rotates its signing secret, and how a project delivers the same event body before its inbox is live.
- Contract v1 and the metric type landed on the default branch with the validator, schemas, fixtures for relay's ceiling and qnow's SMS usage, and the contract-digest test.
- Decide, not build, the inbox-side store for raw events, counts and threshold records and the PostHog projection, as a recorded recommendation for the Captain; the build waits until the inbox runtime is settled.
- Non-goals: any inbox runtime or store build (r1 owns the runtime; the Paseo Hub POC closed 2026-10-26 with r1 kept); qnow's or relay's own emitter code (each project's task); live delivery.
- Budget: at most 1 day (FO proposal).
- Stop conditions: the protocol needs a field that carries personal data; the Paseo Hub POC result changes the event body (not only the transport); the estimate exceeds the budget.

## Acceptance criteria

**AC-1**: The protocol document states the project side, the inbox side and the shared rules, and every rule traces to the Captain's words or to a verified fact.
Verified by: the document on the default branch and a reviewer's trace of each rule to its source.

**AC-2**: The validator accepts the relay ceiling and qnow SMS usage fixtures under the metric type and refuses a metric event with a missing field, a field outside the allowlist, a non-deterministic id or a bad signature.
Verified by: the validator's output and exit code on each fixture.

**AC-3**: Contract v1 is on the kc-claude-plugins default branch at a commit qnow and relay can pin.
Verified by: the merged PR and `git ls-tree` of the contract at that commit.

## FO alignment

Direction alignment before ideation: not needed; the Captain asked for this protocol on 2026-10-25 through qnow FO. Ideation runs on opus (a cross-project contract is hard to reverse). qnow dev2 FO (Paseo agent 519ab4c8) reviews drafts as the first adopter.
Surfaces: none
Visible change: none
Release review: not needed: the kc-ops-inbox journey map (branch iamcxa/kc-ops-inbox at 0a1d59ce, not on the trunk) holds this as its contract and more-events stories.
Captain standing ask, 2026-10-21: 「請持續針對套件的意義做觀察與回饋」. FO reports a package-value observation at each gate.
Ideation inputs relayed by qnow dev2 FO, Captain 2026-10-25 (verbatim, in order): 「有個機制在 ops-inbox 內收數據，送上 ext storage，例如第一階段支援 netlify blob，然後投影到 posthog？這樣等於是原始資料在手上，用第三方做視覺化，也剛好避開真實度的問題？」; 「這裡存放有三個方向，你們倆個評估一下：1. 用類似 DDB 的東西 2. PSQL 3. jsonl 按某種單位分段，例如檔案大小，或時間；用檔案路徑分段，例如時間。哪一個又快又便宜？有時間差沒關係，即時不是要真的 real time 就是很接近就好」; 「目前兩個服務剛好都跑在 netlify。這裡如果成本很低，那就請你先串 PH」. Whether DDB means DynamoDB or DuckDB is unanswered. These words do not decide the inbox runtime: the Captain said on 2026-10-21 「平台是剛好是 netlify，不是平台一定是 netlify」, and the Paseo Hub POC is evaluating a daemon host. FO proposes adding the inbox-side store to this task's ideation.
