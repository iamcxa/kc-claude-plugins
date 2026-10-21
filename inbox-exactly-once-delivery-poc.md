---
title: A signed event sent three times wakes the ops workflow exactly once, and the inbox cannot push code
status: backlog
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:inbox-exactly-once-delivery-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:inbox-exactly-once-delivery-poc-backlog-1
              briefing:
                id: briefing:inbox-exactly-once-delivery-poc:backlog:attempt-1:revision-1
                digest: sha256:d47faa0fe293d6907a0cdd832659441bac780a94a9b691f67c168f3bd7e74362
                room-ref: ./inbox-exactly-once-delivery-poc/review/backlog/briefing-1
---

Second proof for `kc-ops-inbox`, before the inbox-r1 Pilot is admitted. The riskiest unexecuted assumption, named by the engineering-reviewer on 2026-10-21: an event entering a real inbox reaches a running First Officer exactly once, at a measured latency, even when the sender retries. The first POC (`hermes-ops-fo-exe-dev-poc`, closed PASSED 2026-10-21) never sent anything through an inbox.

Captain's words:
- 「可以，但為了避免誤差，我希望可以派一個 worker 再做一次研究確認這個方向可行，因為這會是一個輕量的 agentic ops 服務，我不希望一開始就因為我的誤差走錯方向」 (2026-10-21)
- 「應該要先定義好 inbox 合約，由不同管道收取，且 platform 本身也要提供 hook 可以接，不能直接依賴第三方平台」 (2026-10-21)
- 「可以先跑這個 poc。」 (2026-10-21, to the probe presented from the engineering-reviewer's report)

## Scope

- One Netlify function on a scratch Netlify site receives a Standard-Webhooks-signed fixture event whose body carries CloudEvents 1.0 attributes (`id`, `source`, `type`, `specversion`). It verifies the signature, dedupes on `source` + `id` with a strong-consistency Netlify Blobs `onlyIfNew` write, calls `workflow_dispatch` on the scratch repository `iamcxa/ops-inbox-probe-scratch` with a credential that has only Actions: write, and posts the returned run link to Slack.
- The dispatched workflow mints its own App installation token with `actions/create-github-app-token` and explicit permissions, and creates one `ops/<id>` branch.
- Non-goals: relay's real hook, the Sentry adapter, FO triage content, where the gate record lives, raise-from-link, qnow.
- Each outward action asks the Captain first: the scratch Netlify site, its environment secrets, the Slack destination, any GitHub App permission change, and the workflow push to the scratch repository's default branch.
- Budget: at most 1 day.
- Stop conditions: duplicate runs or a missed strong-consistency read after two materially different attempts; a Netlify function cannot verify and dispatch within its limits; the inbox needs a credential that can push code.

## Acceptance criteria

**AC-1**: The same signed event sent three times with one `webhook-id`, once more than 60 seconds after the first, produces exactly one workflow run and one `ops/<id>` branch.
Verified by: the function's responses for all three sends, the scratch repository's run list and branch list after the last send.

**AC-2**: The same event with one altered byte is rejected and starts nothing.
Verified by: the rejecting response and no new run or branch.

**AC-3**: The time from the event's arrival to the Slack notice and to the workflow run starting is measured and recorded.
Verified by: timestamps from the function log, the Slack message and the run's start time, for the accepted send.

**AC-4**: The inbox holds only a credential that can start the workflow; the push-capable token exists only inside the workflow run.
Verified by: the inbox credential's permission set read back, a refused push attempt with it, and the in-workflow token's permissions printed without its value.

## FO alignment

Direction alignment before implementation: not needed; the Captain approved running this probe in chat on 2026-10-21, and each outward action asks first.
Surfaces: none
Visible change: none
