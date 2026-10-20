---
title: hermes boots as the ops First Officer on exe.dev with a Codex token, and stops at the Captain's gate
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-hermes-ops-fo-exe-dev-poc
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
started: 2026-10-20T13:51:57Z
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

**AC-6**: Amended by Captain, amendment 1. With only a GitHub App installation token, a push to the scratch repository's `main` is refused and `main` is unchanged.
Verified by: `kc-ops-inbox/github-probe/probe.sh` line `AC-6` (refused push output, `main` sha equal before and after), plus both ruleset definitions read back with `gh api` showing an empty bypass list.

**AC-7**: Amended by Captain, amendment 1. With only that token, merging a pull request through the API is refused and the pull request stays open.
Verified by: probe line `AC-7` (HTTP status and message, pull request state read back).

**AC-8**: Amended by Captain, amendment 1. With only that token, approving the App's own pull request does not satisfy the required review.
Verified by: probe line `AC-8` (the approval's HTTP status, `mergeable_state` not clean, a second merge attempt still refused).

**AC-9**: Amended by Captain, amendment 1. With only that token, pushing a branch under `ops/` and opening a Draft pull request succeed.
Verified by: probe lines `AC-9a` and `AC-9b` (push accepted, Draft pull request number and `draft: true`).

**AC-10**: Amended by Captain, amendment 1. The runner holds no GitHub credential other than the installation token, and the token carries no Administration permission.
Verified by: probe lines `AC-10a` (credential sources named by presence, no value) and `AC-10b` (creating a ruleset refused), plus the permissions the token mint reports (`contents` and `pull_requests` write only).

**AC-11**: Amended by Captain, amendment 1. Given a fixture relay capacity event, a First Officer on host Claude Code or Codex, started through `spacedock dispatch build`, files exactly one ops task on an `ops/*` branch and opens one Draft pull request with the App token.
Verified by: the dispatch artifact, the task commit on the `ops/*` branch, the Draft pull request, and the credential audit run in the First Officer's own environment.

**AC-12**: Amended by Captain, amendment 1. The ops gate is recorded only after the First Officer reads the Captain's own GitHub review of that pull request, with his words and attributed to him.
Verified by: the gate record, the review it cites (reviewer login and state), and the gate still open before that review.

## FO alignment

Direction alignment before implementation: not needed; host, FO runtime and model were set by the Captain in chat on 2026-10-20 and the entry was admitted as presented. Each outward action in Scope still asks first.
Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-20 — after the Captain paused the POC to ask for mainstream day-2 practice: resume hermes-as-FO with confinement, re-shape to read-only agent with GitHub-authenticated approval, or something smaller. Advice: escalate; first run a GitHub App token versus main-ruleset probe on a scratch repo (push main, API merge, self-approve refused; ops/* push and Draft PR accepted), then one vertical slice with a host claude or codex FO.
Surfaces: none
Visible change: none

## Captain amendments

### Amendment 1 — 2026-10-20, chat
Captain: 「可以，所以在 slack 回應的 agnet 跟實際調查動手的應該是兩個，但是共享某種資源，對嗎？」 (chat, 2026-10-20, while the POC was paused)
Asked: 「第一版放棄「hermes 開機就當 FO」，權限邊界改放在 GitHub（App token 加 ruleset，加上你本人在 GitHub 的 review），然後先跑上面那個憑證測試，可以嗎？」 The test presented: with only a GitHub App token, 推 main、用 API 合併 PR、核准自己開的 PR are expected to be refused, and 推 ops/* 分支、開草稿 PR is expected to succeed; if those pass, 一個手動餵入的假事件，用 Spacedock 第一級支援的 Claude Code 或 Codex 跑 FO，寫一張 ops 任務到 ops/* 分支、開一個草稿 PR，你在 GitHub 上 review 核准.
Supersedes: AC-1, AC-2, AC-3, AC-4, AC-5
Superseded text:

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

## Stage Report: implementation

HOLD: the local hermes rehearsal is blocked on one permission. Candidate commit 638ef2117 on `spacedock-ensign/hermes-ops-fo-exe-dev-poc` (artifacts under `kc-ops-inbox/`).

- FAILED: Exercise the riskiest claim first: a hermes instance (pinned Hermes Agent commit) boots by default as the Spacedock First Officer of the minimal ops workflow and stops at the ops decision gate without self-approving (AC-2, AC-3), rehearsed locally before any outward action.
  Not run. Captain approved the install (isolated venv and HERMES_HOME under /tmp, pin 31df1227, 127.0.0.1) and `hermes auth add openai-codex` by himself, but `uv pip install -p /tmp/hermes-venv/bin/python -e '/tmp/hermes-src/repo[messaging]'` was denied by the permission layer ("Code from External"); the preceding non-editable install was allowed and failed at build (setup.py refuses wheels; editable is the documented route). No workaround attempted; FO told. Pending: that one command allowed, then running `/tmp/hermes-venv/bin/hermes` with HERMES_HOME=/tmp/ops-rehearsal/hermes-home.
- DONE: Every outward action (exe.dev VM, any spend, Codex token placement, test GitHub repository and ruleset, machine account, Slack app, any message to a human) is raised to the First Officer as a decision request and waited on before it is taken; none is taken on your own judgment.
  None taken. Requests sent to `main`: local install and rehearsal model (answered), install retry (open). Still to raise before use: exe.dev VM (Personal plan $15/month per exe.dev/pricing read 2026-10-20; standalone VM $0.105 per 2 vCPU/4 GiB hour), Slack app, test repository and ruleset, machine account.
- FAILED: AC-1 to AC-5 each carry primary evidence in the stage report, or are named not run with the exact pending approval or blocker; a stop condition that fires ends the stage with a hold report.
  Not all met; each AC below is named. No stop condition has fired (hermes boot not yet attempted twice).

### Evidence so far (primary, read or run today)

- AC-1 not run: pending exe.dev VM approval; local `systemd`-style persistence cannot be shown on macOS. Docs read: exe.dev VMs are persistent Linux VMs, HTTPS proxy (exe.dev/docs/proxy.md): default private behind exe.dev login, one port may be set public (3000-9999 range), hermes must listen beyond loopback for the proxy to reach it.
- AC-2 not run (needs hermes). Verified by source at pin 31df1227: `gateway/platforms/webhook.py` `_validate_svix_signature` accepts Standard Webhooks headers `webhook-id`, `webhook-timestamp`, `webhook-signature` (`v1,<base64 hmac-sha256 of id.timestamp.body>`), rejects stale timestamps, and a bad signature gets HTTP 401 before any agent run (docs: messaging/webhooks.md). Spacedock side ran: `rehearsal/spacedock_mechanics.sh` files one task (`spacedock new` + `state commit`) on the `spacedock-state/ops` branch, 2 state commits, gate `awaiting-captain`.
- AC-3 not run with a model. Mechanics ran: after `gate prepare` + `state commit` the gate row reads `readiness: awaiting-captain` and stays so with no reply (nothing in spacedock times a gate out).
- AC-4 not run in Slack. Finding: `spacedock gate record ... --actor person:captain` accepts the actor as a plain caller string (ran it; resolution `by: person:captain`), so "attributed to the Captain" is enforced only by what Hermes lets reach `gate record`. Hermes side, by source: `gateway/authz_mixin.py` `_principal_authorized` is default-deny with `SLACK_ALLOWED_USERS`; `unauthorized_dm_behavior: ignore` set because the default is a pairing prompt; webhook sessions are always authorized (HMAC only).
- AC-5 not run: pending test repository, ruleset and machine account approvals.
- Codex login: ChatGPT-subscription OAuth, device code, stored in `$HERMES_HOME/auth.json` (hermes_cli/auth_codex.py docstring; docs integrations/providers.md); not an API key. Logout command, documented at website/docs/reference/cli-commands.md (`hermes auth logout <provider>`) and implemented in `hermes_cli/auth.py` `logout_command`: `hermes auth logout openai-codex`. It clears local state only; I read no server-side revoke, so revoking in ChatGPT settings is the Captain's.

### Design facts the FO should know

- Spacedock `dispatch build --host` accepts claude|codex|pi; there is no hermes host and no hermes First Officer runtime adapter. The ops workflow makes the `inbox` stage initial and gated, so the First Officer files the task and stops at its gate with no worker dispatch; skill `ops-first-officer` maps the shared-core steps onto the `spacedock` CLI. It does not load Spacedock's own first-officer skill. What this does not prove: that Spacedock's full FO core runs on hermes.
- Guard plugin `ops-gate-guard` (platform enforcement of AC-3/AC-4 only) has `OPS_GUARD_MODE=log|block`, so the real model's own behaviour and the guard's refusals can be reported separately. `rehearsal/test_ops_gate_guard.py`: 6 tests; each fails if `decide` allows a webhook or non-Captain session (webhook, other Slack user, unset captain id), or misses a chained/env-prefixed command.

### Findings for FO

- roborev (evidence=roborev:935, 1 round, exit 1): High, `ops-gate-guard/__init__.py`: the regex sees only the top-level terminal command, so a session can bypass it via a script or built-up arguments. Agreed, it is a known limit of a command-text guard, not fixed: the real boundary is OS-level (a wrapper or separate unprivileged account for the webhook session). Left for the Captain's call; the POC reports guard refusals and model behaviour separately instead.
- comment_ratio: `code lines 101, comment lines 1, 1.0%`, maximum 5% met, exit 0. doc_impact: 0 documents mention what changed.

### Summary

Authored the minimal ops workflow, hermes profile (config, SOUL, skill, guard plugin), signed-event sender and a hermes-free mechanics script; the Spacedock half of AC-2/3/4 runs. The hermes half is unrun because the editable install is denied; the Captain's two approvals (local install, own Codex login) stand and removal after rehearsal is recorded as a condition. No outward action was taken.

## Stage Report: implementation (cycle 2)

HOLD at the outward-action decision request. Candidate b4da27a8 on `spacedock-ensign/hermes-ops-fo-exe-dev-poc`; nothing run against GitHub yet.

- DONE: Apply Captain amendment 1: move AC-1 to AC-5 verbatim into the amendment entry under `Superseded text:`, write replacement criteria AC-6 onward, each "Amended by Captain, amendment 1".
  AC-1..AC-5 moved verbatim (indented block) under the entry's `Superseded text:`; AC-6 push to main refused, AC-7 API merge refused, AC-8 self-approval does not satisfy review, AC-9 `ops/*` push and Draft PR succeed, AC-10 no other credential and no Administration, AC-11 fixture event to one ops task and Draft PR via `spacedock dispatch build`, AC-12 gate recorded only after the Captain's GitHub review. No criterion id reused; frontmatter and the FO's entry lines untouched.
- DONE: Prepare the probe locally with no outward action: App permission set, the two ruleset definitions, a probe script that uses only the installation token.
  `kc-ops-inbox/github-probe/`: `app-permissions.json`, `ruleset-main.json` (pull request with 1 approval, last-push approval, no deletion, no force-push, empty bypass list), `ruleset-ops.json` (`ops/**`: no deletion, no force-push), `mint_token.sh`, `probe.sh`, `credential_audit.sh`, `askpass.sh`. Field names checked against GitHub's published OpenAPI description (rulesets, access_tokens, pulls) read today. Local proof against a fake API plus a local bare repo with a refusing pre-receive hook: verdict lines for AC-6..AC-10 all PASS; three mutations each flipped the matching line to FAIL (API accepts merge -> AC-7 and AC-8; remote accepts a main push -> AC-6; stray `GH_TOKEN` in env -> AC-10a). This proves the probe's verdict logic only; real GitHub behaviour (including whether an App's self-approval is refused or merely not counted) is unmeasured.
- DONE: Send one decision request naming each outward action exactly, and wait.
  Sent to `main` after this report; no outward action taken.
- DONE: Clean the hermes rehearsal residue.
  Ran `rm -rf /tmp/hermes-venv /tmp/hermes-src /tmp/ops-rehearsal /tmp/hermes-install.log /tmp/exe-docs /tmp/exe-docs.html` (and `/tmp/gh-oapi`, `/tmp/probe-test.*`, my two later scratch dirs). `ls -d` on each afterwards: "No such file or directory" for all; `~/.hermes` does not exist. No hermes login was ever made, so no `hermes auth logout` was needed (command, for the record: `hermes auth logout openai-codex`, hermes_cli/auth.py `logout_command`).

### Findings for FO

- `design_surfaces.py check` exits 1 on `## FO alignment`: needs a non-empty `Surfaces:` line and a `Visible change:` line. FO-owned text; I did not write them.
- roborev on b4da27a8 (evidence=roborev:938, exit 1, no findings in `github-probe/`); both High findings are in the shelved hermes artifacts, not fixed per "do not extend": the guard regex is bypassable by shell expansion (same class as roborev:935), and `hermes-profile/config.yaml` never points hermes at the skill directory (`skills.external_dirs` empty), so the skill would not load. Both are moot while hermes-as-FO is shelved.
- comment_ratio: `code lines 101, comment lines 1, 1.0%`, max 5% met, exit 0. doc_impact: 0 documents mention what changed (nothing to mark).
- The slice runner must not inherit the Captain's own `gh` login, ssh keys or git credential helper; AC-11 therefore runs the credential audit inside the First Officer's actual environment, which for host Claude Code or Codex is not the empty-HOME probe environment.

### Summary

Amendment 1 applied to the entity; the credential probe is built and its logic proven locally, with real-GitHub behaviour still unmeasured. The hermes residue is gone. Next step is the Captain's yes to the named outward actions.

## Stage Report: implementation (cycle 2, probe results)

Candidate 232aad69 on `spacedock-ensign/hermes-ops-fo-exe-dev-poc`. Real GitHub run, 2026-10-20 14:54Z, scratch repository `iamcxa/ops-inbox-probe-scratch` (private, default branch `master`), App `ops-inbox-probe-iamcxa` (id 5397558, installation 173426167). Neither the key nor the token was opened or printed.

- DONE: AC-6 push to the default branch is refused and the branch is unchanged.
  `git push origin HEAD:master` exit 1, "push declined due to repository rule violations"; `master` still `d2994f976f` "Initial commit" per `gh api`.
- DONE: AC-7 API merge is refused and the PR stays open.
  On a ready PR (#2, marked ready through GraphQL `markPullRequestReadyForReview`, HTTP 200): `PUT .../merge` HTTP 405 "Repository rule violations found. New changes require approval from someone other than the last pusher."; PR #2 `state: open, merged: false, mergeable_state: blocked`. A merge attempt on the still-Draft PR also gave 405 "Pull Request is still a draft"; that one is not rule evidence and is labelled NOTE in the probe.
- DONE: AC-8 the App cannot satisfy the required review with its own approval.
  REFUSED, not "not counted": `POST .../reviews {"event":"APPROVE"}` HTTP 422 "Unprocessable Entity", errors `['Review Can not approve your own pull request']`; `gh api .../pulls/2/reviews` returns 0 reviews. The "accepted but not counted" case did not occur, so it is unmeasured; whether an App approving someone else's PR counts toward the rule is not tested here.
- DONE: AC-9 push to `ops/*` and opening a Draft PR succeed.
  `ops/probe-1792508099` push accepted; Draft PR #2 created (HTTP 201, `draft: true`, author `ops-inbox-probe-iamcxa[bot]`). An earlier run left `ops/probe-1792508024` and Draft PR #1.
- DONE: AC-10 no other credential, no Administration.
  Probe ran under `env -i` with an empty HOME: "no other GitHub credential source found". The mint response reports permissions `{contents: write, metadata: read, pull_requests: write}`, `repository_selection: selected`. `POST .../rulesets` as the App: HTTP 403 "Resource not accessible by integration". Rulesets read back with empty `bypass_actors` (main-protect 25482703, ops-branches 25482704).
- DONE: Re-run the three mutation proofs against the current `probe.sh`.
  Against a fake API plus a local bare remote with a refusing hook (default branch `master`): API accepts merge -> `AC-7` FAIL; remote accepts a default-branch push -> `AC-6` FAIL; stray `GH_TOKEN` -> `AC-10a` FAIL, other lines PASS. One harness slip: a combined run showed `AC-6` also failing under the `GH_TOKEN` mutation because the previous mutation had left the remote changed; a fresh-remote rerun flipped `AC-10a` alone.

### Findings for FO

- roborev on 232aad69 (evidence=roborev:942, exit 1): the single High finding is again the shelved hermes guard regex; nothing in `github-probe/`. comment_ratio: 1.0%, max 5% met, exit 0.
- Limits of this probe: it shows the ruleset and token behave as designed for one repository and one App; it does not show how a First Officer process on a real host keeps the Captain's own `gh` login out of reach (AC-11). The ops ruleset blocks deletion, so two probe branches and PRs #1 and #2 remain until the scratch repository is deleted by the Captain.

## Stage Report: implementation (cycle 2, slice prepared)

Candidate 4cbc6516 on `spacedock-ensign/hermes-ops-fo-exe-dev-poc`. Nothing of the slice has run on GitHub. HOLD at the outward-action decision request.

- DONE: Prepare the vertical slice (AC-11, AC-12) to run the FO on a GitHub-hosted Actions runner.
  `kc-ops-inbox/slice/`: `workflows/ops-fo.yml` (manual `workflow_dispatch`, `permissions: {}`, 20 min), `run_fo.sh` (installs spacedock and Claude Code 2.1.303, launches `spacedock claude -p --model sonnet --max-budget-usd 5`), `fo-prompt.md`, `verify_slice.sh`, `workflows/ops-gate.yml` (`pull_request_review`, only reviewer `iamcxa`, only `ops/*` PRs from this repository, 5 min) and `record_gate_from_review.sh`; `make_scratch_tree.sh` assembles the 10 files for the scratch repository. `ops-workflow/README.md` is now triage -> decision (gate) -> resolution -> done, inline (no state branch), so the task, the gate and its review room all live on `ops/<slug>`. Claude Code auth documented at anthropics/claude-code-action docs/setup.md: `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`); Codex action (openai/codex-action README) takes `openai-api-key` only and hides it behind a proxy.
- DONE: Rehearse every part possible locally with no outward action.
  Gate recorder against a fake reviews API on a real inline spacedock workflow: Captain approves current head -> gate closed, `by: person:captain`, reason carries his words and the review id; other user, older commit, or a plain comment -> no-op, gate stays `awaiting-captain`; changes requested -> `revise`; removing the login filter lets another user approve (mutation caught). `run_fo.sh` end to end with a stub FO, a local bare remote and a fake API: job-env credential names listed, audit inside the FO environment passes, `verify_slice.sh` PASS; mutations each flip the right line: extra file outside `docs/ops/` -> FAIL, non-draft PR -> FAIL, `GITHUB_TOKEN` added to the FO env -> audit FAIL and the run stops. `actionlint` 1.7.11 clean on both workflows; `spacedock status --validate` VALID on the workflow; `spacedock dispatch build --host claude` produced an ensign artifact for the triage stage. `spacedock claude "<task>" -- -p --max-budget-usd 0.5 --permission-prompts none` launched headless and answered (flags checked against `claude --help` 2.1.303; `--max-turns` does not exist there and was dropped).
  Side effect to disclose: that smoke launch auto-refreshed the Captain's local Claude plugin, adding `~/.claude/plugins/cache/spacedock/spacedock/0.27.3` beside 0.27.0; `spacedock doctor --host claude` reports OK.
  Not rehearsed: the real model driving the FO (cost and credential), the runner image itself, and whether `-p` headless FO dispatches the triage worker; the first real run is that experiment.
- DONE: Run the credential audit inside the runner job itself.
  `run_fo.sh` runs `credential_audit.sh` under the same `env -i` environment array the FO is launched with (fresh HOME, no gh login, no git helper, no ssh) before launch, with only `PROBE_TOKEN`, `GH_TOKEN` (the App token) and the one model variable allowed; the job's own credential-shaped names are printed first. Not run on a runner yet.
- DONE: Send me one decision request listing each outward action exactly, then wait.
  Sent to `main`.

### Findings for FO

- roborev on a0805740 (evidence=roborev:943, exit 1): two High findings, both declined as wrong: it assumed the old split-root workflow (`.spacedock-state` worktree and a state branch); the current ops README has no `state:` field, and the local run showed the task, gate and review room committed on the `ops/<slug>` branch (compare listed `docs/ops/<slug>.md` and `docs/ops/<slug>/review/decision/briefing-1/index.json`). comment_ratio 1.0%, max 5% met.
- Gap I cannot close without GitHub: the Captain's review can only be recorded if `ops-gate.yml` triggers on a review of an App-authored Draft PR; unmeasured until the run. The recorder runs from a fresh clone of the default branch, not the PR branch, so the App cannot edit the recorder; the App also lacks the `workflows` permission, which GitHub is documented to require for pushes touching `.github/workflows` (to be shown by one extra push, requested in the decision).

## Stage Report: implementation (cycle 2, slice run 1 FAILED, stopped)

Run https://github.com/iamcxa/ops-inbox-probe-scratch/actions/runs/39448281871, 2026-10-20 15:25:37Z to 15:26:07Z (about 30 s of runner time), `ubuntu-24.04` image 20261012.334.1, candidate 4cbc6516 on master of the scratch repository (setup commit `b3ff9ce`). One attempt only, per instruction.

- DONE: Setup. Ruleset 25482703 set `disabled`, setup commit pushed to master, ruleset set `active` and read back (`bypass_actors: []`, rules deletion, non_fast_forward, pull_request); probe re-run after re-enable: AC-6 PASS (push declined by repository rules), AC-7, AC-8, AC-9, AC-10 PASS (Draft PR #3, branch `ops/probe-1792509891`). `OPS_APP_TOKEN` set from the token file by stdin (list shows it at 15:25:34Z); the Captain's `CLAUDE_CODE_OAUTH_TOKEN` was listed at 15:21:31Z. Extra App push touching `.github/workflows/ops-gate.yml` on `ops/probe-workflow-edit`: REFUSED, "refusing to allow a GitHub App to create or update workflow `.github/workflows/ops-gate.yml` without `workflows` permission"; no such branch exists afterwards.
- FAILED: AC-11 First Officer run. Step "Run the First Officer" exited 127 at "== launch First Officer": `env: 'spacedock': No such file or directory`. Cause (mine): `run_fo.sh` built the `env -i PATH="$PATH"` array before the install block exported the new PATH, so the cleaned environment could not find the freshly installed `spacedock`. The FO never started; no model call was made; no ops branch or PR was created.
- DONE (partial evidence for AC-11/AC-10): from the run log. Job-environment credential-shaped names were exactly `CLAUDE_CODE_OAUTH_TOKEN` and `OPS_APP_TOKEN`; install resolved spacedock stable v0.27.3 (binary and plugin "compatible" per `spacedock doctor --host claude`), Claude Code 2.1.303; the in-job audit under the First Officer's `env -i` environment printed "no other GitHub credential source found". The GITHUB_TOKEN of the job had Metadata: read only.
- AC-12 not run (no Draft PR to review).

### Next step and state left behind

- Fix committed locally at the candidate (not on the scratch repository): the environment array is built after the install and a `command -v spacedock` check fails the run early. The local stub rehearsal could not have caught this bug (spacedock was already on the local PATH); it is checked only by syntax and by reading.
- Landing the fix needs the ruleset off/on again (same steps as before). `OPS_APP_TOKEN` expires at 16:24:45Z; a second run after that needs a re-mint and re-set.
- Left on GitHub: workflows and scripts on master; probe branches `ops/probe-1792508024`, `ops/probe-1792508099`, `ops/probe-1792509891` and Draft PRs #1 to #3; the two secrets. The Captain's local Claude plugin cache still holds spacedock 0.27.3 beside 0.27.0 from the earlier smoke launch (doctor: OK).
