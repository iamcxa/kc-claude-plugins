---
title: hermes boots as the ops First Officer on exe.dev with a Codex token, and stops at the Captain's gate
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:hermes-ops-fo-exe-dev-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:hermes-ops-fo-exe-dev-poc-backlog-1
              briefing:
                id: briefing:hermes-ops-fo-exe-dev-poc:backlog:attempt-1:revision-1
                digest: sha256:7873820c9a15ab58c15bdecf5642a0da830af438a0b42b98c111ef11b927ac54
                room-ref: ./hermes-ops-fo-exe-dev-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:hermes-ops-fo-exe-dev-poc:backlog:1
                briefing: briefing:hermes-ops-fo-exe-dev-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-20T13:49:38.919445Z"
                decision: approve
                reason: Captain answered 「可以」 in chat on 2026-10-20 to the presented entry (title, five acceptance criteria, non-goals, 2-day budget, stop conditions, outward actions each asked first, profile poc), after directing 「不，第一版我想先 poc 讓 hermes 預設 boot FO，用exe.dev 接 codex token」. Accepts direction and entry to implementation only; no VM, token placement, repository, ruleset, Slack app, PR or merge authority is inferred.
              application:
                target-stage: implementation
                state: consumed
---

First proof for the new `kc-ops-inbox` package: one always-on hermes instance acts as the First Officer of an `ops` Spacedock workflow, so an event reaches a person and an agent at once and every step lands in a repository task. The riskiest claim is unexercised: no recorded run has a Hermes Agent instance act as a Spacedock First Officer (`kc-hermes-spacedock` main at 556217b, 2026-08-25, still launches the FO as a separate Claude process; Spacedock 0.27 lists Claude Code, Codex and Pi as tier-1 and Hermes-class agents as "through skill systems").

Captain's words:
- Outcome (2026-10-19, design brief): 「拉出一個ops inbox抽象，確保必要資訊可以一次到位到inbox 變成一個聚合事件，然後後面可以投影到slack，或是投影給agent 例如gpt dot…或是netlify agent，目的是人要知道，然後agent要同步進行解決方案呈現，要有一個repo內的ops workflow，來按照sd流程進行排查」
- Authority (2026-10-19): 「被叫起來的agent有source存取權限，可以跑 ops flow推entity task到separate branch，但是沒有權限做危險動作例如推main且沒有權限合併pr」
- Host (2026-10-20): 「第一版hermes 應該要架在類似 exe.dev 上，避免斷線，而我自己的 qnow 則會放在 mini 上」
- FO runtime (2026-10-20): 「hermes 可以跑 spacedock workflow，所以我才做那個 plugin，可以讓 hermes agent 自己成為 fo」
- This POC (2026-10-20): 「不，第一版我想先 poc 讓 hermes 預設 boot FO，用exe.dev 接 codex token<」
- Admission (2026-10-20, chat): 「可以」 to the presented entry: the five criteria below, non-goals, a 2-day budget and the stop conditions.

## Scope

- One hermes profile on an exe.dev VM, model authenticated with a Codex token, running as a service. On boot it acts as the Spacedock First Officer by default for an `ops` workflow in a disposable test repository.
- A synthetic relay capacity event (signed-in publishing ceiling near or full; fields modelled on relay's removed `DiagnosisRecord`: `v`, `event`, `at`, `day`, `count`, `limit`, `limitSource`) arrives Standard-Webhooks-signed at hermes's built-in webhook route.
- POC artifacts (hermes profile configuration, the ops triage skill, the minimal ops workflow README, evidence) live under `kc-ops-inbox/` on branch `iamcxa/kc-ops-inbox` in kc-claude-plugins. No `plugin.json`, no marketplace entry, no release.
- Each outward action needs the Captain's separate yes at the moment it is taken: creating the exe.dev VM (cost unmeasured), placing the Codex token on it, creating the test GitHub repository and its ruleset, choosing the machine account, and creating a Slack app.
- Non-goals: a real relay producer, Sentry and PostHog, dedupe and aggregation, UI, ChatGPT dot, narrow operator tools, a hermes plugin, qnow and the mac mini, auto-merge, production writes by an agent.
- Budget: at most 2 days.
- Stop conditions:
  - hermes cannot boot the First Officer after two materially different attempts.
  - The hermes FO passes any gate without the Captain's reply.
  - exe.dev cannot keep the service running or accept an inbound HTTPS request.

  Each one stops the POC and returns to the Captain with the fallback "hermes launches Claude Code as the FO".

## Acceptance criteria

**AC-1**: On the exe.dev VM, hermes authenticated with a Codex token runs as a service and is back after a VM reboot without manual action.
Verified by: service status and a hermes health/readback before and after one reboot, with timestamps; the token itself never appears in any record.

**AC-2**: A correctly signed synthetic relay ceiling event makes hermes, with no human prompt, act as the First Officer and file exactly one ops task on the test repository's ops state branch; the same event with one changed byte is rejected and files nothing.
Verified by: the webhook delivery log for both requests, the state-branch commit for the valid one, and no new commit for the altered one.

**AC-3**: The FO posts its diagnosis and options in a Slack thread and stops at the ops decision gate; with no Captain reply the gate stays open.
Verified by: the Slack thread, and the gate record still unresolved after a stated wait.

**AC-4**: The Captain's reply in that thread is recorded as the gate result with his words, attributed to the Captain; a reply from a user outside the allowlist is refused and recorded nowhere as a decision.
Verified by: the gate record after the Captain's reply, and the refusal for a second, non-allowlisted Slack user.

**AC-5**: The machine account the FO uses cannot push to the test repository's default branch or merge a pull request there; a GitHub ruleset enforces it.
Verified by: the refused push output and the refused merge attempt, plus the ruleset read back with `gh api`, showing that account is not on the bypass list.

## FO alignment

Direction alignment before implementation: not needed; host, FO runtime and model were set by the Captain in chat on 2026-10-20 and the entry was admitted as presented. Each outward action in Scope still asks first.
