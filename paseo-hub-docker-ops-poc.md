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
Captain ruling, 2026-10-26 (chat): 「好」. Asked: 「接受 AC-4 沒過，把這個 POC 送去驗證嗎？」, after FO's account that on the unattended run Hub closed and archived the agent 3 min 20 s after start, so no window existed for his message, that the same approach had failed twice, that the 1-day budget was spent, and that Hub's documented continuation-key mechanism, the PASEO_HUB_CONFIG_JSON contents and separate daemon and agent accounts move to the next step (self-hosted Hub on exe.dev).

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

## Stage Report: implementation (cycle 2)

- DONE: Read Paseo's own docs and the Hub OpenAPI first, verify each fact the task lists before relying on it, and rehearse everything that needs no outward action locally (a Docker image for the daemon from Paseo's documented Docker setup, the fixture ops event, the in-container credential audit, the ops task and Draft PR step against a local bare remote).
  Done in cycle 1 (f4921948). Cycle 2 changed the image to Codex 0.162.1 (npm version verified), commits b4dc790c and c0cf7488 on spacedock-ensign/paseo-hub-docker-ops-poc.
- DONE: Raise every outward action to the First Officer as one decision request naming the exact target, owner, scope and cost if known (Hub account and tokens, registering the daemon, connecting a GitHub App to Hub, running the container, placing the model credential, any push outside your worktree branch); take none on your own judgment and never read or print a credential.
  The Captain approved the seven actions (「同意」, relayed 2026-10-25) with PASEO_PASSWORD unset and Codex via ChatGPT device login. No credential value was printed; the API key file was sourced into the sender's environment only. One request was refused by the permission layer and not worked around: reading the agent's `PASEO_HUB_CONFIG_JSON` from `/proc` (see AC-3).
- DONE: Record AC-1 to AC-5 with primary evidence, or name each not run with its exact pending approval or blocker; a stop condition that fires ends the stage with a hold report naming the fallback r1 as designed; include one package-value observation.
  AC-1 met: key ac1c-poc-20261025T151021 sent twice, both HTTP 200 with receipt 1ae1abb2-d9f5-4df3-ad80-1de45f50c734 and run 06585fa7-1a46-4867-acbd-5b26467df148, and `paseo ls -a` in the container lists exactly one agent (2e9a99f).
  AC-2 met: the agent opened Draft PRs 8 and 9 in iamcxa/ops-inbox-probe-scratch (https://github.com/iamcxa/ops-inbox-probe-scratch/pull/8 and /pull/9) as paseo-bot[bot] on ops/poc-20261025t151042z and ops/poc-20261026t131558z; with its Hub-minted token a push to master was rejected (repository rule violations), a merge of PR 7 was refused, and `gh issue create` was refused (Resource not accessible by integration); the token's permission object reads all false, so the grant is shown by behaviour, not a listing.
  AC-3 not met as written, met for "no Captain credential": the live agent's audit lists hub-relationship.json, daemon-keypair.json and local-credential in /home/paseo/.paseo (readable by the agent uid) plus the allowed Codex auth.json; PASEO_HUB_CONFIG_JSON contents are unknown.
  AC-4 not met on both attempts, nothing from the Captain appears in either timeline: agent 2e9a99f (held open by the operator) was archived by Hub at 2026-10-25T15:39:40Z; on the unattended run agent ab1f5c9 finished and was archived at 2026-10-26T13:18:48Z, 3 min 20 s after start. The Captain accepted this on 2026-10-26: 「好」, to the FO question 「接受 AC-4 沒過，把這個 POC 送去驗證嗎？」.
  AC-5 first half not met (offline sends were answered HTTP 200 running, not a refusal); second half met (after the 14:47:23Z restart, 6 minutes with an empty agent list and no create request).
  Stop conditions: none fired; the fallback r1 as designed is not triggered. Package-value observation: see Findings.

### AC results

- AC-1 met (second attempt). Key `ac1c-poc-20261025T151021`, project `default`, two sends 35 s apart: both HTTP 200, same `providerEventReceiptId` 1ae1abb2-d9f5-4df3-ad80-1de45f50c734 and `triggerRunId` 06585fa7-1a46-4867-acbd-5b26467df148; `paseo ls -a` in the container shows exactly one agent (2e9a99f, codex, created at the first send). Hub dedupes by key; the repeat does not start a second agent. The two attempts before it (keys `ac1-poc-20261025T143236`, `ac1b-poc-20261025T145558`) were dedupe-correct but failed inside Hub, see Root cause.
- AC-2 met. Draft PR https://github.com/iamcxa/ops-inbox-probe-scratch/pull/8, author `paseo-bot[bot]`, head `ops/poc-20261025t151042z`, base master, files `docs/ops/poc-20261025t151042z.md` and its gate briefing json; master unchanged at fe8dd63c. The agent ran `/opt/poc/ac2-probe.sh 7` with its Hub-provided environment: installation repositories lists only `iamcxa/ops-inbox-probe-scratch`; push to master was `remote rejected (push declined due to repository rule violations)`; merge of PR 7 was refused ("New changes require approval from someone other than the last pusher"); `gh issue create` was refused (`Resource not accessible by integration (createIssue)`). Limits: the "another repository" probe read the public `iamcxa/kc-claude-plugins`, which any token can read, so it proves nothing; the token's `permissions` object from `/installation/repositories` reads all false and does not show contents/pull_requests write. Read-back of the grant is therefore by behaviour (branch push and Draft PR accepted, issue write refused), not by a permissions listing.
- AC-3 fails on its text, passes on "no Captain credential". Audit run by the live agent (names only): `hub-relationship.json`, `daemon-keypair.json`, `local-credential` in `/home/paseo/.paseo` (readable by uid 1000, the agent's uid) plus the allowed `/home/paseo/.codex/auth.json`; no PASEO_PASSWORD (unset), no gh login, ssh key, netrc or git helper other than Hub's. The Hub CLI login file was an empty shell after logout. Env names show `GH_TOKEN`, five `GIT_CONFIG_*` pairs and `PASEO_HUB_CONFIG_JSON`; that last variable is not matched by the audit and its content was not inspected (permission layer refused the `/proc` read), so whether it carries an execution credential is unknown. `GH_PAGER` was a false audit hit, now noted.
- AC-4 not run, pending: needs the Captain to add host `127.0.0.1:6768` (no password) in the Paseo app and message agent "Hub agent" (2e9a99f); the answer is read with `paseo logs 2e9a99f`.
- AC-5 first half not met, second half met. With the container stopped, every send was HTTP 200 `running` (key `ac5-poc-143340` and seven more over 180 s); the documented 409 `daemon_not_connected` never appeared, so the sender saw no refusal. After the restart at 14:47:23 UTC and 6 minutes of watching, the agent list stayed `[]`, the daemon log had no create request, and the pending runs read `failed` on re-send. Hub's UI showed those runs as "Running" while offline.

### Root cause of the earlier failed runs

Hub's GitHub App installation 175142369 lacked the scratch repository or its permissions (docs: "Requested authority cannot exceed the GitHub App installation"); the Captain fixed the grant (「補好了」) and the next run started. Hub gave no failure detail anywhere the Captain or my key could read, which cost three attempts.

### Findings

- Docs vs behaviour: the docs promise `daemon_not_connected` and "nothing is queued"; observed, offline sends are accepted as `running` and silently end `failed` later. A sender cannot learn the daemon was down from the API response.
- `deliveryKey` dedupe works at the receipt level and a repeat returns the current status (it flipped running to failed on the failed runs), matching "no replay of an earlier response".
- Hub starts the agent as a normal Paseo agent; the Codex agent dispatched a Spacedock triage worker and opened the Draft PR on its own from the delimited prompt, with `mode: full-access` and thinking `low`. To keep the token alive for the probes I steered the agent not to call `hub.finish_execution`; that is an operator action, not part of the unattended path.
- The hosted Hub proves the flow only; the Captain's plan is a self-hosted Hub at the exe.dev step.
- Cleanup: remove `ops-poc-paseo`, its two named volumes and image `ops-poc-paseo:local`; the trigger `ops-event-poc` cannot be disabled from the Hub UI and stays active until removed with a Hub CLI login; Draft PR 8 and branch `ops/poc-20261025t151042z` stay (ruleset forbids deleting `ops/*`). The GitHub token expires about 16:10 UTC.
- Gates after cycle 2: roborev not re-run on c0cf7488 (docs/config edits only); comment_ratio 0 comment lines.
- Package-value observation: the dispatch's rule "name each not run with its exact blocker" held up; what the package lacked was a way to see why a Hub run failed, so the FO-side audit of the GitHub grant found in minutes what three live attempts did not. A pre-flight check of the App installation's repository and permissions, before the first send, would have saved two failed runs.

### Summary

AC-1, AC-2, AC-3 (qualified) and AC-5 second half are recorded with primary evidence; AC-4 waits on the Captain's message, and AC-5's sender-visible refusal does not exist in Hub as observed. No stop condition fired; the fallback r1 as designed is not triggered by these results.

### Cycle 2 addendum (2026-10-26): AC-4

- AC-4 not met on the evidence: agent 2e9a99f's timeline (`paseo logs 2e9a99f`, read 2026-10-26T13:07Z) holds three `[User]` entries (the Hub prompt and my two operator steers) and no message from the Captain, no PONG, no answer after 15:19 UTC on 2026-10-25. The Captain reports he sent a message from the Paseo desktop app to "Hub agent" on 127.0.0.1:6768 and that the app asked for no password (「送了，沒有要求密碼」); that password-free connection is his statement, backed by the daemon log showing direct loopback client connections with no password configured (PASEO_PASSWORD unset), not by an in-app capture.
- Likely reason found: `paseo agent ls` shows agent 2e9a99f as `Archived: true`, `ArchivedAt 2026-10-25T15:39:40Z`, and the daemon log has `archive_workspace_request` from the Hub connection at 15:39:41Z, 29 minutes after the run began, while the agent was idle and the execution held open. Hub archived the workspace itself; a default `paseo ls` (and so likely the app's list) hides archived agents. The Captain's message may have gone to another agent or not been deliverable. I did not send the message myself: AC-4 asks for his message from the app.
- Limits: the phone path was not tested; the contents of `PASEO_HUB_CONFIG_JSON` in the agent environment are unknown (the permission layer refused a /proc read); the operator steered the agent not to call `hub.finish_execution`, so the unattended path (run to finish with no operator) was not shown end to end, and Hub's archive at 15:39 may be the consequence of that held execution.
- Open: to meet AC-4 the Captain needs a live agent to talk to. That means either a new fresh event (a third run, one more Codex run) and a message sent while the agent is still unarchived and idle, or restoring the archived workspace through Hub, which I have no verified command for.

### Cycle 2 addendum 2 (2026-10-26): unattended run and AC-4

- Fresh event, key `ac4-poc-20261026T131524`, sent 13:15:24Z, run `d4608b88-9432-4b0c-8fbc-7d9bd5bfdb5e`, no steering. Agent `ab1f5c9` (name "Hub agent", codex) was created 13:15:28Z, opened Draft PR https://github.com/iamcxa/ops-inbox-probe-scratch/pull/9 (head `ops/poc-20261026t131558z`), called `hub.finish_execution`, and ended `status closed`, `Archived: true`, `ArchivedAt 2026-10-26T13:18:48Z`: 3 min 20 s after start, at the moment it finished. It was never idle and unarchived, so there was no window for the Captain's message, and none was sent to it (timeline holds the Hub prompt and the agent's own turns only).
- Finding: on the unattended path Hub closes and archives the agent when `hub.finish_execution` is called. The Captain can talk to a Hub-started agent only while its execution is still open (cycle 1's held agent was archived by Hub at 29 min, 15:39Z). "Agent that files the ops task, then the Captain talks to it" therefore needs the agent to stay unfinished, or a continuation, which Hub documents as restoring an archived workspace when a later event arrives for the same continuation key. Not tested here.
- AC-4 stays not met; no Captain message from the Paseo app was ever recorded in either agent's timeline.
