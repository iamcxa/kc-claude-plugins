---
title: A Paseo daemon in Docker, reached through Paseo Hub, turns one event into one First Officer run that files an ops task with only a scoped GitHub token, and the Captain talks to that agent from the Paseo app
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:paseo-hub-docker-ops-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:paseo-hub-docker-ops-poc-backlog-1
              briefing:
                id: briefing:paseo-hub-docker-ops-poc:backlog:attempt-1:revision-1
                digest: sha256:cb18189c6b22695ed9728f5f1217911a914bcfb62362cc5443f1567bc065bed3
                room-ref: ./paseo-hub-docker-ops-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:paseo-hub-docker-ops-poc:backlog:1
                briefing: briefing:paseo-hub-docker-ops-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T04:18:31.203372Z"
                decision: approve
                reason: Captain answered 「准」 in chat on 2026-10-25 to the backlog gate question, which stated that approving accepts the five criteria, non-goals, the 1-day budget and the stop conditions as written, enters implementation, and lets FO move the dev2-poc workflow checkout to origin/main; each outward action still asks first.
              application:
                target-stage: implementation
                state: consumed
---

Tests whether Paseo Hub plus a deployed Paseo daemon can replace kc-ops-inbox r1's internet-facing inbox, trigger repository and GitHub-hosted runner, and add live conversation with the agent (the Captain's priority 7), without losing platform-enforced agent authority (priority 0). r1 (`ops-inbox-r1-setup-and-isolation`, dev2) is built locally and its live setup is paused until this POC closes.

Captain's words:
- 「評估一下直接整合 paseo hub，把 kc-ops 做成 SD +paseo plugin 這條路」 (2026-10-25)
- 「不要考慮 macbook 而是應該考慮被部署的地方，我的 mbp 只是部署的其中一個可能性」 (2026-10-25)
- 「可以，先用 docker 做 poc，如果可行再測試 exe.dev，然後拉回 doceker 繼續整合」 (2026-10-25)

Facts read 2026-10-25 (Paseo docs at paseo.sh and the Hub OpenAPI at hub.paseo.sh/api/openapi.json, read by an FO research worker; verify before relying): Hub turns GitHub, Slack, Discord and manual events into a workflow step on a registered daemon; `POST /api/v1/manual-runs` takes scope `runs:dispatch` and a `deliveryKey`; an offline daemon fails dispatch with `daemon_not_connected` and nothing is queued; `hub.execute` is granted per daemon; Hub's `github` block mints a scoped App token and does not read the host git identity; provider modes can bypass approval prompts and Hub does not sandbox the provider; the daemon can run in Docker (docs/docker.md). Phone push is not documented.

## Scope

- One Paseo daemon in a Docker container on the Captain's Mac, registered with Paseo Hub, holding no credential except the model credential and what Hub provides for GitHub; hosted Hub (hub.paseo.sh) unless setup shows self-hosting is needed.
- A manual run sent through Hub's API with a fixture ops event starts one First Officer run in the container that writes one ops task on `ops/*` and opens a Draft PR in the existing scratch repository `iamcxa/ops-inbox-probe-scratch`, under its existing no-bypass rulesets.
- The Captain continues that agent's conversation from the Paseo app.
- Non-goals: exe.dev (the next step only if this passes), relay, aggregation, ADR citation, Slack, a Paseo plugin or UI, r1 code changes.
- Each outward action asks the Captain first: Hub account and tokens, registering the daemon, connecting a GitHub App to Hub, running the container, placing the model credential, any push outside the worktree branch.
- Budget: at most 1 day (FO proposal).
- Stop conditions: Hub cannot dispatch a manual run without a credential that also reaches other daemons or repositories; Hub's GitHub token cannot be limited to the scratch repository with contents and pull-request write; the container needs a Captain credential beyond the model token; the Paseo app cannot reach the container's agent. Each returns to the Captain with the fallback "r1 as designed".

## Acceptance criteria

**AC-1**: The same fixture event sent twice through Hub's manual-run API with one `deliveryKey` starts exactly one agent run in the container.
Verified by: both API responses, the Hub activity record and the daemon's agent list after the second send.

**AC-2**: That run files one ops task on an `ops/*` branch and opens one Draft PR in the scratch repository using only a Hub-minted token, and the same token is refused a push to the default branch and a merge.
Verified by: the branch, the Draft PR with its author, the token's permissions read back without its value, and the two refusals.

**AC-3**: Inside the container, no credential other than the model credential and the Hub-provided GitHub token is reachable.
Verified by: an in-container audit of environment, files, keychain and git credential helpers, with its output.

**AC-4**: The Captain sends a message to that agent from the Paseo app and the agent answers in the same session.
Verified by: the agent's timeline showing the Captain's message from the app and the answer, with times.

**AC-5**: An event sent while the daemon is stopped is answered by Hub with a refusal the sender can see, and nothing runs when the daemon comes back.
Verified by: the API response for that send and the agent list after the daemon restarts.

## FO alignment

Direction alignment before implementation: not needed; the Captain set the path in chat on 2026-10-25. Each outward action still asks first.
Surfaces: none
Visible change: none
Captain standing ask, 2026-10-21: 「請持續針對套件的意義做觀察與回饋」. FO reports a package-value observation at each gate.
