---
title: A Paseo daemon in Docker, reached through Paseo Hub, turns one event into one First Officer run that files an ops task with only a scoped GitHub token, and the Captain talks to that agent from the Paseo app
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-paseo-hub-docker-ops-poc
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
started: 2026-10-25T04:19:20Z
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
Release review: not needed: the kc-ops-inbox journey map (branch iamcxa/kc-ops-inbox at 0a1d59ce, not on the trunk) already holds this capability as the open host question on story run-own-instance.

## Stage Report: implementation

- DONE: Read Paseo's own docs and the Hub OpenAPI first, verify each fact the task lists before relying on it, and rehearse everything that needs no outward action locally (a Docker image for the daemon from Paseo's documented Docker setup, the fixture ops event, the in-container credential audit, the ops task and Draft PR step against a local bare remote).
  Facts: the six listed facts match paseo.sh/docs/hub*.md, docker.md and hub.paseo.sh/api/openapi.json (read 2026-10-25); phone push has no match in the hub, docker, security or connectivity pages. Two differ: `deliveryKey` is "durable deduplication" but "not exactly-once, no replay of an earlier response" (hub/api.md), so the second send's response shape is unknown; the official image has git and ssh but no `gh`, `claude` or `spacedock`, so `Dockerfile` adds them (pinned like r1: Claude Code 2.1.303, Spacedock 0.27.2 installer by sha256; base by digest sha256:9832cb6b..., Paseo 0.13.0). Built as `ops-poc-paseo:local`.
  Rehearsed with `--network none`, no mounts but the scripts, placeholder values only: `audit.sh` is clean on the bare image as uid 1000, and exits 1 naming each of NPM_TOKEN, GITHUB_TOKEN, PASEO_PASSWORD, `.netrc`, an ssh key, a gh login file, a non-gh git helper, a provider login file and `hub-relationship.json` when planted. `rehearse-remote.sh` runs `spacedock new` and `state commit` on an `ops/*` branch, pushes it to a bare remote and shows a default-branch push refused with remote master unchanged; with the hook neutered the same script exits 1 ("ACCEPTED"). `send-event.sh` against a local stub sends the contract v1 body with the key redacted, and sends nothing for the r1 fixtures extra-field, bad-signature and missing-source (validate.mjs exit 1).
  The Draft PR step cannot run against a bare remote and was not rehearsed; `ops-event-poc.yml` is not validated (`paseo hub deploy --dry-run` needs a Hub login).
- DONE: Raise every outward action to the First Officer as one decision request naming the exact target, owner, scope and cost if known (Hub account and tokens, registering the daemon, connecting a GitHub App to Hub, running the container, placing the model credential, any push outside your worktree branch); take none on your own judgment and never read or print a credential.
  Taken: none outward. Read-only GETs of the scratch repository with the Captain's `gh` (rulesets, tree, branches, PRs) and the pull of the public image; no credential read or printed.
  Request, recommend approve all as one: (1) Hub: hosted hub.paseo.sh Free plan, owner the Captain, no card; its managed GitHub App means no GitHub App private key on this machine (self-hosting `npx @getpaseo/hub` needs the Captain to create that App and hold its key). (2) One API key, scope `runs:dispatch` only, in a file outside the repository; deploy uses a browser CLI login instead. (3) Install Hub's GitHub App on iamcxa with repository selection `ops-inbox-probe-scratch` only. (4) `POC_ENV_FILE=<captain file> docker compose up -d` on this Mac, port 127.0.0.1:6767, named volumes, no host mount; the entrypoint and `spacedock install` fetch from the network. (5) `docker exec -u paseo ops-poc-paseo paseo hub login https://hub.paseo.sh`, `hub connect`, `hub permissions grant hub.execute`. (6) Model credential `CLAUDE_CODE_OAUTH_TOKEN` and `PASEO_PASSWORD` in that env file, Captain-placed; cost is Captain plan usage of one FO run, not measured. (7) Pushes outside my branch: the run pushes `ops/poc-*` and opens one Draft PR in the scratch repository (ruleset 25482704 forbids deleting the branch, so it stays); `ac2-probe.sh` attempts a push to master and a merge of an existing probe PR, both expected refused. Relay and phone are not used.
- DONE: Record AC-1 to AC-5 with primary evidence, or name each not run with its exact pending approval or blocker; a stop condition that fires ends the stage with a hold report naming the fallback r1 as designed; include one package-value observation.
  AC-1 not run: pending (1)-(6). AC-2 not run: pending (1)-(7). AC-3 rehearsed on the image only (clean baseline); the live run is pending (4)-(6) and is predicted to report two reachable sources, below. AC-4 not run: pending (4)-(6). AC-5 not run: pending (4)-(6), needs `docker compose stop`. No stop condition has fired; none is decided without the live run.
  Unresolved, only settled live: `POST /api/v1/manual-runs` requires `projectSlug` and documents the trigger as part of a project's active configuration, while `ops-event-poc.yml` is the org-level self-contained form; whether that form is addressable by a project slug is unread.
  boundary-crossed: none.
  Package-value observation: the stage's "rehearse first, ask second" ordering already paid before any approval: it found that the daemon's own Hub credential and `PASEO_PASSWORD` sit where the agent can read them, which is AC-3's subject, and that the image lacks the tools the run needs. A reader of AC-3 alone would have taken the "only model and GitHub credentials" claim at face value. The dispatch's 1-day budget and stop conditions stay untouched.

### Review findings and dispositions (roborev:1164, roborev:1166)

- FO item 1, credential reachability: kept as is; the audit counts both, hidden from nothing. Evidence: `daemon Hub relationship credential present: /home/paseo/.paseo/hub-relationship.json (readable by uid 1000)` and `env PASEO_PASSWORD present`, exit 1, on the compose environment shape. Source: relationship-controller.js writes `hub-relationship.json` under PASEO_HOME mode 0600 for the daemon uid, which is the agent uid in the official image; the Claude provider builds the agent environment from `process.env`. Separate uids would mean replacing the base image's entrypoint, not tested here. Predicted AC-3 reading: fails strictly (2 sources), passes on "no Captain credential".
- FO item 2, event in prompt: not removable; Hub's manual-run `input` reaches the agent only as `${{ paseo.prompt }}` text (hub/api.md, hub/workflows.md), typed `inputs` only exist in legacy bundles as enumerated headers. Done instead: `send-event.sh` refuses with contract v1 `validate.mjs` before sending and sends the validated body; the prompt keeps it delimited. Residual: `event` and `limitSource` accept free strings up to 500 characters, so contract v1 does not make the text safe.
- roborev "runs as root": declined. The image keeps `USER root` as Paseo's Docker page instructs; its entrypoint drops to uid 1000, shown by `docker run --rm ops-poc-paseo:local id` giving `uid=1000(paseo)`. `USER paseo` would break the entrypoint's volume setup.
- Gates: comment_ratio `code lines 0, comment lines 0, 0.0%`, not enforced (under 20 code lines). roborev ran twice: evidence=roborev:1164, then evidence=roborev:1166 (only the declined root finding remains).
- Cleanup: remove `ops-poc-paseo:local`, the `/tmp/r1co` and `/tmp/poc-fixture` copies; no ADR added or changed; no PR opened: no push grant.

### Summary

All local rehearsal that needs no outward action is done and committed on spacedock-ensign/paseo-hub-docker-ops-poc (a1275d36); every AC is waiting on the one approval request above. Two reachable credentials (daemon Hub file, daemon password) are the likely AC-3 finding, and Hub gives the event to the agent only as prompt text.
