---
title: hermes boots as the ops First Officer on exe.dev with a Codex token, and stops at the Captain's gate
status: validation
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

## Stage Report: implementation (cycle 2, slice run 2 FAILED, stopped)

Run https://github.com/iamcxa/ops-inbox-probe-scratch/actions/runs/39449196966, 2026-10-20 15:31:26Z to 15:31:55Z (about 29 s), master at `ea02925` (candidate a320f34c). Second and last attempt.

- DONE: Land the fix. Ruleset 25482703 disabled, master pushed (`b3ff9ce..ea02925`), re-enabled and read back (`active`, `bypass_actors: []`); probe re-run: AC-6 PASS, AC-7..AC-10 PASS; `OPS_APP_TOKEN` re-minted and re-set via stdin (token expiry 16:31:00Z).
- FAILED: AC-11 First Officer run. The PATH fix worked (spacedock found, "launching claude as your first officer", workflow `docs/ops` detected, in-job audit "no other GitHub credential source found", job env credential names only `CLAUDE_CODE_OAUTH_TOKEN` and `OPS_APP_TOKEN`). `claude` then exited 1: `Error: Input must be provided either through stdin or as a prompt argument when using --print`; no model call, no branch, no PR.
- Cause (mine): `claude` options `--allowedTools` and `--add-dir` take a variable number of values. `spacedock claude "<task>" -- ...` appends the task after the forwarded options, so the last variadic option swallowed it. The previous attempt's form (`--allowedTools` last) had the same latent defect; my added `--add-dir` last made it fire. Reproduced locally with the identical flags: order A (variadic last) fails with the same message; order B (scalar option last) and order C (`--allowedTools="..." --add-dir=...`) both returned READY. The local smoke earlier passed only because its last option was scalar.
- AC-12 not run (no Draft PR to review).

### Proposed materially different approach (not run)

The two failures were both launch-line defects that only a real launch exposes, and each remote attempt cost the Captain a ruleset off/on and a master push. Before a third remote attempt: run the whole First Officer once locally on a disposable clone first, with the exact `run_fo.sh` launch line (candidate e86aca75, variadic options now as `name=value`), a local bare remote instead of GitHub, and a recording `gh` shim on PATH for `gh pr create`; cost cap `--max-budget-usd 5` on the Captain's local Claude login, no credential handled by me. That measures what is still unmeasured (does a headless `-p` First Officer dispatch the triage worker and reach the gate) at zero GitHub side effects. Only after it passes: one more remote dispatch (re-mint token, one ruleset off/on, master push).

### State left behind

- Master of the scratch repository holds the run-2 files (the `-p` argument-order defect included). Local fix e86aca75 is not on GitHub.
- Probe branches `ops/probe-1792508024`, `-1792508099`, `-1792509891`, `-1792510266` and Draft PRs #1 to #4; two secrets; `OPS_APP_TOKEN` expires 16:31:00Z.
- Captain's local Claude plugin cache still holds spacedock 0.27.3 beside 0.27.0; doctor: OK.
- roborev not re-run on the last three small commits; comment_ratio and doc_impact unchanged in kind.

## Stage Report: implementation (cycle 2, local full rehearsal PASSED)

Local rehearsal at candidate 4a42f9ec (launch line moved unchanged into `slice/launch_fo.sh`), 2026-10-20 15:36:06Z to 15:38:28Z. Disposable clone of the assembled scratch tree, local bare remote, recording `gh` shim first on PATH, the Captain's default local Claude login (not handled by me), `--max-budget-usd 5`, `--output-format json` added only for the measurement. No GitHub side effect; no credential handled. Not exercised locally: the clean `env -i` environment and the in-job credential audit (run on the runner twice already), because the clean HOME has no Claude login.

- DONE: The headless First Officer dispatched the triage worker.
  Commits on the branch show the worker's work: `dispatch: ... entering triage`, `triage: ... diagnosis, options, recommendation`, `triage: stage report`; the task body holds Event, Diagnosis (known and unknown separated, no cause asserted), Options (three, each with a cost), Recommendation and the worker's Stage Report (3 of 3 checklist items DONE).
- DONE: It reached the decision gate and stopped there.
  `spacedock status --next --json` after the run: `ready_gates` row `current: decision`, `readiness: awaiting-captain`; the gate room is committed (`docs/ops/<slug>/review/decision/briefing-1/index.json`). No `gate record`, `gate consume` or merge was run (the FO's own report says so); the branch diff against master is exactly the task file and that room file.
- DONE: Only the ops branch was pushed and the PR call was the expected one.
  Remote branches: `master` (still `8e80b27`) and `ops/relay-bound-ceiling-near-2026-10-20`. The shim log holds the single call `pr create --draft --base master --head ops/<slug> --title ... --body ...`.
- DONE: Measured cost and duration.
  Claude Code JSON result: `duration_ms` 133138 (2 m 13 s model time; 2 m 22 s wall clock), `num_turns` 21, `is_error` false, `permission_denials` 0, `total_cost_usd` 0.7396 (imputed on the Captain's subscription login, not a bill). The runner step budget of 20 min and `--max-budget-usd 5` were far from reached.
- Observation, not a defect: the worker tried to send its completion message to `team-lead` (not registered in a headless run); the FO accepted the worker's blocking return plus the committed stage report as completion and said so.

### Findings for FO

- Run 1 and run 2 failures were launch-line defects; this rehearsal used the same launch line the runner uses and passed, so the remaining unmeasured risks are the runner image only (Claude Code and plugin install already succeeded there twice) and whether GitHub triggers `ops-gate.yml` for the Captain's review of an App-authored Draft PR.
- A third remote dispatch is a separate request: it needs the ruleset off/on and a master push (to land 4a42f9ec), a token re-mint and re-set, and one `gh workflow run`.

## Stage Report: implementation (cycle 3, final)

Candidate aae7041b on `spacedock-ensign/hermes-ops-fo-exe-dev-poc`. The scratch repository's master (`fbccbc3`) holds candidate 4a42f9ec, which lacks the last fix. Task elapsed: 2026-10-20 13:51Z to 2026-10-21 (well inside the 2-day budget).

- SKIPPED: Exercise the riskiest claim first: a hermes instance (pinned Hermes Agent commit) boots by default as the Spacedock First Officer of the minimal ops workflow and stops at the ops decision gate without self-approving (AC-2, AC-3), rehearsed locally before any outward action.
  Retired by Captain amendment 1 (2026-10-20); never run (the editable install was denied by the permission layer, no hermes login was made). The hermes skill and guard plugin are shelved as committed; the rehearsal residue was deleted.
- DONE: Every outward action (exe.dev VM, any spend, Codex token placement, test GitHub repository and ruleset, machine account, Slack app, any message to a human) is raised to the First Officer as a decision request and waited on before it is taken; none is taken on your own judgment.
  Taken only after a relayed Captain yes each: scratch repository and both rulesets, the five-step probe, three ruleset off/on cycles with master pushes, `OPS_APP_TOKEN` re-set before each run, one extra App push, three manual dispatches. No exe.dev VM, Slack app, Codex token, message to a human or spend beyond model use occurred.
- FAILED: AC-1 to AC-5 each carry primary evidence in the stage report, or are named not run with the exact pending approval or blocker; a stop condition that fires ends the stage with a hold report.
  AC-1..AC-5 are superseded; AC-6 to AC-11 below carry evidence; AC-12 FAILED (cause named below).

### Evidence for AC-6 to AC-12 (primary, real GitHub unless stated)

- AC-6 PASS: push to `master` declined, "push declined due to repository rule violations", master sha unchanged; re-proved after each ruleset re-enable (last 2026-10-20 16:02Z). Rulesets 25482703 and 25482704 read back with `bypass_actors: []`.
- AC-7 PASS: API merge of a ready (non-draft) App PR: HTTP 405 "Repository rule violations found. New changes require approval from someone other than the last pusher."; PR stays open. (A merge on a Draft is refused as a draft and is not counted.)
- AC-8 PASS: App self-approval REFUSED, HTTP 422 `Review Can not approve your own pull request`; zero reviews recorded. It was refused, not accepted-and-not-counted; the latter case is unmeasured.
- AC-9 PASS: push to `ops/probe-*` accepted, Draft PR opened (HTTP 201, `draft: true`, author `ops-inbox-probe-iamcxa[bot]`).
- AC-10 PASS: probe under empty `env -i` HOME: no other GitHub credential; token permissions `{contents: write, metadata: read, pull_requests: write}`, repository-selected; ruleset creation as the App: HTTP 403; an App push editing `.github/workflows/ops-gate.yml`: refused "without `workflows` permission".
- AC-11 PASS (run 3, https://github.com/iamcxa/ops-inbox-probe-scratch/actions/runs/39453880412, 16:02:22Z to 16:03:48Z, 86 s, success): fixture event in; Claude Code 2.1.303 `--model sonnet` launched as First Officer by `spacedock claude -p`; triage worker dispatched through `spacedock dispatch build`; one task file `docs/ops/relay-bound-ceiling-near-2026-10-20.md` plus its gate room on `ops/relay-bound-ceiling-near-2026-10-20`; Draft PR #6 by the App; `verify_slice.sh` PASS twice; master unchanged. In-job credential names: only `CLAUDE_CODE_OAUTH_TOKEN` and `OPS_APP_TOKEN`; audit inside the First Officer's `env -i` environment: "no other GitHub credential source found". Runs 1 and 2 (39448281871, 39449196966) failed at launch on my PATH ordering and `claude` argument-order defects; the local rehearsal passed first (133 s, 21 turns, imputed 0.74 USD, 0 permission denials).
- AC-12 FAILED: the Captain submitted CHANGES_REQUESTED on PR #6 at head 51260a9848, body "test request changes" (review 5587945359, user `iamcxa`). `ops-gate.yml` DID trigger (run 39454533717, event `pull_request_review`, 16:06:43Z to 16:06:53Z, success) and recorded NOTHING: its log shows `curl: (22) ... 403` fetching the reviews, then "no-op: no review by iamcxa on 51260a98...". Cause (mine): the job's `permissions` omitted `pull-requests: read`, so the GITHUB_TOKEN could not list reviews; the recorder also reported a fetch failure as a harmless no-op. Result: gate still `awaiting-captain` (no `gate record`), nothing approved, nothing merged (PR #6 open, Draft, `mergeable_state: blocked`; master `fbccbc3`). Failing safe, not failing right.

### Fix prepared, not landed

aae7041b adds `pull-requests: read` to the gate job and makes a failed review fetch exit 1 (only "no review by the Captain on this head" stays a no-op). Local proof on a real inline workflow with a fake API: reviews 403 -> exit 1, gate stays open; empty list -> no-op; Captain CHANGES_REQUESTED "test request changes" -> `gate record --decision revise --actor person:captain`, reason `GitHub review 5 by iamcxa on <head>: test request changes`. To close AC-12 on GitHub: ruleset off/on, master push, then the Captain submits a new review (a rerun of run 39454533717 would reuse the old workflow definition). That is a separate request.

### Material limits and findings

- roborev on aae7041b (evidence=roborev:948, exit 1), two Critical: (1) shelved hermes guard regex bypassable, moot while shelved; (2) real: `run_fo.sh` and `ops-gate.yml` execute `install.sh` fetched from the mutable `main` branch of spacedock-dev/spacedock while the App token, GITHUB_TOKEN and model token are present (the script checksum-verifies the tarball, not itself). Accepted for a scratch POC; production needs the script pinned to a tag or commit and verified. comment_ratio: 1.0%, max 5% met. doc_impact: `kc-ops-inbox/ops-workflow/README.md` unaffected: it states the recorder's role, which the fix does not change.
- Not shown: an App approving someone else's PR counted or not; that a First Officer on a self-hosted or longer-lived runner stays credential-clean; that `OPS_APP_TOKEN` can be minted inside the workflow (the App key stayed local; the pre-minted token lasts 1 h); GitHub Actions minutes (about 2 min per attempt, plan Pro, included allowance not re-read); real subscription cost (imputed only).
- `design_surfaces.py check` still fails on `## FO alignment` (FO-owned `Surfaces:` and `Visible change:`).
- Disclosed side effect: a local smoke launch of `spacedock claude -p` auto-refreshed the Captain's local Claude plugin, adding `~/.claude/plugins/cache/spacedock/spacedock/0.27.3` beside 0.27.0 (`spacedock doctor --host claude`: OK).
- Left on GitHub for the Captain to delete: the scratch repository (workflows, probe branches `ops/probe-*` and Draft PRs #1 to #6 with their `ops/` branches, both secrets, the App `ops-inbox-probe-iamcxa` and its key at `~/.config/ops-inbox-probe/app.pem`).

### Summary

The authority boundary at GitHub held in every probe: the App token could not reach main, merge, self-approve or edit workflows, and the First Officer ran headless on a hosted runner and filed one task and one Draft PR under a clean credential audit. The gate recording from the Captain's review did not work in the one run it got, because of a missing job permission; the fix is written and locally proven but not on GitHub.

## Stage Report: implementation (cycle 3, AC-12 second failure)

- FAILED: AC-12 second attempt. After the fix landed on master (`bdff186`, `pull-requests: read`), the Captain submitted a second review on PR #6 (review 5588252635, CHANGES_REQUESTED, "test request changes", head 51260a9848). `ops-gate.yml` run 39458087494 (`pull_request_review`, 16:30:45Z to 16:30:54Z) failed: `curl: (22) ... 403`, "fail: cannot read the reviews of PR 6", exit 1. The gate stayed `awaiting-captain`; nothing was recorded, approved or merged. The fail-closed path of aae7041b worked as designed.
- Root cause (confirmed by me on GitHub, 2026-10-20 ~16:35Z): a `pull_request_review` run uses the workflow file from the pull request's merge commit, not from master. That run's job log lists GITHUB_TOKEN permissions `Contents: write`, `Metadata: read` only. `refs/pull/6/merge` (`38109b9`) still holds the old `ops-gate.yml` with `permissions: contents: write` only, while master `bdff186` holds `contents: write` plus `pull-requests: read`. The merge ref of an open PR is not recomputed when only the base branch moves (re-read twice, 20 s apart, still `38109b9`), so a fix to a PR-triggered workflow reaches an existing PR only after its head or state changes.
- Consequence for the design: any fix to `ops-gate.yml` must be on master before the First Officer opens the PR it governs. A second consequence found while planning the approved third FO run: its slug (`relay-bound-ceiling-near-2026-10-20`, from the fixture's event and day) is the name of the branch already on the remote, and the `ops/**` ruleset blocks force-push and deletion, so a run from current master would collide; a new slug needs either a second fixture on master (a ruleset off/on) or no new run at all.

## Stage Report: implementation (cycle 4, final)

Candidate aae7041b on `spacedock-ensign/hermes-ops-fo-exe-dev-poc`; scratch repository master `bdff186` carries it. This report supersedes the cycle 3 "final" report's AC-12 verdict; its AC-6 to AC-11 evidence stands unchanged.

- SKIPPED: Exercise the riskiest claim first: a hermes instance (pinned Hermes Agent commit) boots by default as the Spacedock First Officer of the minimal ops workflow and stops at the ops decision gate without self-approving (AC-2, AC-3), rehearsed locally before any outward action.
  Retired by Captain amendment 1; never run (editable install denied by the permission layer; no hermes login made); hermes skill and guard plugin shelved as committed.
- DONE: Every outward action (exe.dev VM, any spend, Codex token placement, test GitHub repository and ruleset, machine account, Slack app, any message to a human) is raised to the First Officer as a decision request and waited on before it is taken; none is taken on your own judgment.
  Each taken action followed a relayed Captain yes: scratch repository and rulesets, the probe, four ruleset off/on cycles with master pushes (`ea02925`, `fbccbc3`, `bdff186` and the first setup commit `b3ff9ce`), `OPS_APP_TOKEN` sets, one extra App push, three dispatches, one empty App commit to the PR branch. No exe.dev VM, Slack app, Codex token or message to a human.
- DONE: AC-1 to AC-5 each carry primary evidence in the stage report, or are named not run with the exact pending approval or blocker; a stop condition that fires ends the stage with a hold report.
  AC-1..AC-5 superseded by amendment 1. AC-6 to AC-12 evidence, one line each (results unchanged from the cycle 3 report):
  AC-6 PASS: push to `master` declined ("push declined due to repository rule violations"), master sha unchanged, re-proved after every ruleset re-enable (last at master `bdff186`); rulesets 25482703 and 25482704 read back with `bypass_actors: []`.
  AC-7 PASS: API merge of a ready (non-draft) App PR returned HTTP 405 "Repository rule violations found. New changes require approval from someone other than the last pusher."; the PR stayed open.
  AC-8 PASS: the App's self-approval was refused, HTTP 422 `Review Can not approve your own pull request`, zero reviews recorded (refused, not accepted-and-not-counted).
  AC-9 PASS: push to `ops/probe-*` accepted and a Draft PR opened (HTTP 201, `draft: true`, author `ops-inbox-probe-iamcxa[bot]`).
  AC-10 PASS: probe under an empty `env -i` HOME found no other GitHub credential; token permissions `{contents: write, metadata: read, pull_requests: write}`; ruleset creation as the App returned 403; an App push editing `.github/workflows/ops-gate.yml` was refused without the `workflows` permission.
  AC-11 PASS: run 39453880412 (86 s, success): headless First Officer filed one task on `ops/relay-bound-ceiling-near-2026-10-20` and Draft PR #6; `verify_slice.sh` PASS twice; in-job credential audit clean.
  AC-12 PASS: the gate was recorded by script `ops-gate` run 39522787636 from the Captain's review 5593555088; detail in the AC-12 section below.

### AC-12 evidence (PASS)

- Captain's review of PR #6: id 5593555088, user `iamcxa`, on head `8329b5a3f3c3d707ce26bfb08165213bcc370dcb`, body "a new test approval", submitted APPROVED 2026-10-21 00:40:58Z.
- Gate run 39522787636 (`pull_request_review`, 00:41:00Z to 00:41:09Z, success). Its log lists GITHUB_TOKEN permissions `Contents: write`, `Metadata: read`, `PullRequests: read` (the fixed workflow, read from the refreshed merge ref `a66e1fa`), then `recorded gate=gate:relay-bound-ceiling-near-2026-10-20:decision ... state=closed` and `Committed ... nothing pushed` followed by the job's own push.
- Gate record on the ops branch (`docs/ops/relay-bound-ceiling-near-2026-10-20.md`, commit `1f01f013c0` by `ops-gate`): `by: person:captain`, `decision: approve`, `reason: 'GitHub review 5593555088 by iamcxa on 8329b5a3f3c3d707ce26bfb08165213bcc370dcb: a new test approval'`, application `target-stage: resolution`, `state: pending` (approved, not consumed; no worker was dispatched).
- Nothing merged: PR #6 `state: open`, `draft: true`, `merged: false`, `mergeable_state: blocked`; master still `bdff186`.
- The gate was recorded by the script, not by a model; the earlier two reviews (CHANGES_REQUESTED on 51260a9848) were correctly not recorded: the first run lacked a permission, the second ran the old workflow from a stale merge ref (cycle 3 reports).

### Why the approval now shows DISMISSED, and what it means for merging

The gate job pushes its record commit (`1f01f013c0`) onto the PR branch, which moves the PR head off `8329b5a3f3`. The main-protect ruleset has `dismiss_stale_reviews_on_push: true`, so GitHub dismissed the Captain's approval (review 5593555088 now `DISMISSED`) because it no longer matches the head. The recorded gate decision stands in the task file, but GitHub's required review for merging is not satisfied: PR #6 is blocked until the Captain approves the new head `1f01f013c0`. `require_last_push_approval` is satisfied by him because the last pusher is the `ops-gate` job, not him. So in this design a gate approval and a merge approval are two separate reviews. If one review should do both, the recorder would have to push nothing to the PR branch (state kept elsewhere) or the ruleset would have to stop dismissing on push; neither was tried.

### Material limits and findings

- A fix to a PR-triggered workflow reaches an open PR only when its merge ref is rebuilt: `pull_request_review` runs the workflow file from the PR merge commit, and the merge ref did not refresh when only master moved (found with run 39458087494; refreshed by one empty App commit).
- roborev on aae7041b (evidence=roborev:948): `run_fo.sh` and `ops-gate.yml` execute `install.sh` from the mutable `main` branch of spacedock-dev/spacedock with tokens present; accepted for this scratch POC, pin it before production. The shelved hermes guard regex is bypassable (moot).
- Not shown: an App approving someone else's PR counted or not; First Officer credential-cleanliness on a self-hosted or longer-lived runner; in-workflow minting of the App token (a pre-minted 1 hour token was used, App key stayed in `~/.config/ops-inbox-probe/app.pem`); Actions minutes beyond about 2 min for each FO run and 10 s for each gate run (plan Pro, allowance not re-read); real subscription cost (imputed 0.74 USD for the local rehearsal only).
- comment_ratio 1.0% (max 5% met); doc_impact: `ops-workflow/README.md` unaffected (the recorder's role is unchanged). `design_surfaces.py check` still fails on the FO-owned `## FO alignment` (`Surfaces:`, `Visible change:`).
- Disclosed side effect: a local smoke launch of `spacedock claude -p` auto-refreshed the Captain's local Claude plugin and added `~/.claude/plugins/cache/spacedock/spacedock/0.27.3` beside `0.27.0` (`spacedock doctor --host claude`: OK).
- Left on GitHub for the Captain to delete: scratch repository `iamcxa/ops-inbox-probe-scratch` (workflows, probe branches, Draft PRs #1 to #7, the `ops/` branch behind #6), secrets `OPS_APP_TOKEN` (expired) and `CLAUDE_CODE_OAUTH_TOKEN`, the App `ops-inbox-probe-iamcxa` and its key file.

### Summary

All of AC-6 to AC-12 now carry real GitHub evidence: the App token cannot reach main, merge, self-approve or edit workflows; a headless Claude Code First Officer on a hosted runner filed one task and one Draft PR under a clean credential audit; and the gate was recorded by a script only after the Captain's own GitHub review, with nothing merged. The one design wrinkle found is that the gate record commit invalidates the approval it records, so merging needs a second approval.

## Stage Report: validation

Recommend PASSED for the amended outcome (AC-6 to AC-12) at POC depth, with the limits below. Artifact: candidate aae7041b on `spacedock-ensign/hermes-ops-fo-exe-dev-poc` (base ad44f0cb, 28 files, 747 added lines, all under `kc-ops-inbox/`); live repository `iamcxa/ops-inbox-probe-scratch` read 2026-10-21 with the Captain's `gh` login, reads only. Scratch master `bdff186` equals the candidate's assembled tree (`make_scratch_tree.sh` output hashed against 11 files on master: all same).

- DONE: Independently verify AC-6 to AC-12 against the exact artifacts with read-only checks, and name any claim only the implementer's report supports.
  Read back live: both rulesets active, `bypass_actors` empty, main-protect requires 1 approval with last-push approval and stale-review dismissal; master history has only the Captain's pushes (made with the ruleset off) and no App commit; 7 PRs open, 0 merged, all by the App; PRs 1-5 and 7 have 0 reviews (supports AC-6, AC-7, AC-8 by consequence); PR #6 is Draft, 2 files (one task, one gate room), run 39453880412 success with log `no other GitHub credential source found` and 2 `PASS AC-11` lines; the task at `8329b5a3f3` has no `resolution:`, at `1f01f013c0` it has `by: person:captain`, `decision: approve`, reason citing review 5593555088 by `iamcxa`; the commit `dispatch: ... entering triage` is the text `dispatch build --stamp` writes (found in the spacedock binary), so the FO did go through `dispatch build`. Only the implementer's report supports: the refusal texts and codes (push declined, 405, 422, 403) because probe stdout is not retained; the token's permission set (mint response); the empty-HOME AC-10a result; that the Captain personally submitted the three reviews (the API shows only login `iamcxa`); all three mutation proofs; the 0.74 USD and 133 s local rehearsal.
- DONE: Write a minimal acceptance script of read-only commands the First Officer can run exactly as written in a fresh shell, each with its expected output.
  Script below; every command was run once by me and produced the stated output.
- DONE: Give the verdict on goal sufficiency and minimal necessity, run adr_lint with its exit code, and list unverified obligations.
  Sufficiency: met at POC depth, with the AC-12 wording caveat. Necessity: `hermes-profile/` and `rehearsal/` (9 files, 268 of 747 lines) map to retired AC-1..AC-5, not to the amended outcome; the rest maps to AC-6..AC-12. `python3 .../adr_lint.py docs/adr --since ad44f0cbf42274ff65802cabc52ebe919f159fd5`: `26 ADR file(s) checked, 0 legacy`, exit 0. Other checks: comment_ratio exit 0 (see limit below), doc_impact exit 0, design_surfaces exit 0, dispatch_records exit 0 (18 complete). `boundary-crossed:` none; see limits.

### Acceptance script (read-only; needs `gh` signed in as a user who can read the private repo, and the worktree for step 6)

    R=iamcxa/ops-inbox-probe-scratch

1. Rulesets on the default branch and on `ops/**` have no bypass actor.
       for id in 25482703 25482704; do gh api repos/$R/rulesets/$id --jq '[.enforcement,(.bypass_actors|length),.conditions.ref_name.include[0],([.rules[].type]|join(","))]|@tsv'; done
   Expect two lines: `active	0	~DEFAULT_BRANCH	deletion,non_fast_forward,pull_request` and `active	0	refs/heads/ops/**	deletion,non_fast_forward`.
2. Default branch holds only the Captain's setup pushes and nothing was merged.
       gh api repos/$R/branches/master --jq .commit.sha; gh pr list -R $R --state all --json mergedAt,author --jq '[(map(select(.mergedAt!=null))|length),(map(select(.author.login!="app/ops-inbox-probe-iamcxa"))|length),length]|@tsv'
   Expect `bdff186a3181b1bfbeae4a3b582460bd824b2767` then `0	0	7` (merged, not by the App, total).
3. AC-11: the headless First Officer run produced one Draft PR with one task and a clean credential audit.
       gh api repos/$R/pulls/6 --jq '[.user.login,.draft,.merged,.head.ref]|@tsv'; gh api repos/$R/pulls/6/files --jq '[.[].filename]|join(" ")'; gh run view 39453880412 -R $R --log | grep -c "PASS AC-11"; gh run view 39453880412 -R $R --log | grep -o "no other GitHub credential source found"
   Expect `ops-inbox-probe-iamcxa[bot]	true	false	ops/relay-bound-ceiling-near-2026-10-20`; the two files `docs/ops/relay-bound-ceiling-near-2026-10-20.md docs/ops/relay-bound-ceiling-near-2026-10-20/review/decision/briefing-1/index.json`; `2`; `no other GitHub credential source found`.
4. AC-12: the gate was open on the head the Captain reviewed, and is recorded from his review.
       F=docs/ops/relay-bound-ceiling-near-2026-10-20.md; gh api repos/$R/pulls/6/reviews --jq '.[]|select(.id==5593555088)|[.user.login,.commit_id]|@tsv'; gh api "repos/$R/contents/$F?ref=8329b5a3f3c3d707ce26bfb08165213bcc370dcb" --jq .content | base64 -d | grep -c "resolution:"; gh api "repos/$R/contents/$F?ref=1f01f013c0daebb56ab7839fbe425ae5fdfea8b2" --jq .content | base64 -d | grep -E "^ +(by|decision|reason):"
   Expect `iamcxa	8329b5a3f3c3d707ce26bfb08165213bcc370dcb`; `0`; then `by: person:captain`, `decision: approve`, `reason: 'GitHub review 5593555088 by iamcxa on 8329b5a3f3c3d707ce26bfb08165213bcc370dcb: a new test approval'`.
5. Not satisfied for merging: the record commit dismissed the approval.
       gh api repos/$R/pulls/6 --jq '[.merged,.mergeable_state]|@tsv'; gh api repos/$R/pulls/6/reviews --jq '.[]|select(.id==5593555088)|.state'
   Expect `false	blocked` and `DISMISSED`.
6. Local only, shows what does NOT enforce AC-12 (the boundary is the ops-gate script plus the FO prompt, not Spacedock).
       D=$(mktemp -d) && cd "$D" && gh repo clone iamcxa/ops-inbox-probe-scratch r -- -q && cd r && git checkout -q 8329b5a3f3c3d707ce26bfb08165213bcc370dcb && /Users/kent/.local/bin/spacedock gate record relay-bound-ceiling-near-2026-10-20 --workflow-dir docs/ops --decision approve --actor person:captain --reason "local probe" | cut -c1-60; cd /tmp && rm -rf "$D"
   Expect `recorded gate=gate:relay-bound-ceiling-near-2026-10-20:decis` (a plain caller string is accepted as the Captain; nothing is pushed).

Does not cover: the refusal behaviour itself (push to the default branch, API merge, self-approval, ruleset creation, workflow edit); that needs a write with the App token and is only in the implementer's report plus the consequences in steps 1-2. Nor a reviewer other than `iamcxa`, nor a fresh run.

### Verdict

- Goal sufficiency: the amended outcome is shown at POC depth: the App token's reach ended at `ops/*` + Draft PR on the one real run, a headless Claude Code First Officer on a hosted runner filed one task and one Draft PR, and the gate was recorded from the Captain's review with his words. Caveat for the Captain to accept: AC-12 says "the First Officer reads" the review; a workflow script read it, not the FO. The Verified-by line is met either way.
- Minimal necessity: keep `github-probe/`, `slice/`, `ops-workflow/` (each maps to AC-6..AC-12, a named falsifier or the safety boundary). `hermes-profile/` and `rehearsal/` (9 files, 268 lines) have no consumer in the amended outcome and carry two open roborev High findings (guard regex bypass, skill never loaded); they are a removal candidate for the Captain, not deleted by me. `kc-ops-inbox/README.md` still describes the old workflow (`inbox -> resolution -> done`) and the hermes credential table, and now misdescribes the ops workflow (`triage -> decision -> resolution -> done`): Polish.

### Material limits and unverified obligations

- AC-12 "only after" is not enforced by the platform: any caller of `spacedock gate record` can put `person:captain` on a gate (step 6), and the FO is allowed `Bash(spacedock:*)`. In the one run the FO did not do it, because its prompt forbids it; the GitHub review is checked only by the `ops-gate` script and the PR merge rule. Observed once, not tested adversarially. Deferred risk: becomes Material if an untrusted event can steer the FO.
- Not exercised on GitHub: a reviewer other than `iamcxa` (only the local mutation shows the login filter), an App approving someone else's PR, in-workflow App-token minting (a pre-minted 1 hour token was used), a self-hosted or long-lived runner, Actions minutes beyond about 2 min per FO run, real subscription cost (0.74 USD is imputed).
- AC-11 audit ran in the same `env -i` array the FO is launched with, not inside the claude process; the FO also holds the Captain's `CLAUDE_CODE_OAUTH_TOKEN` and the App token. AC-10 limits only GitHub credentials.
- roborev:948 Critical, accepted for a scratch POC: `run_fo.sh` and `ops-gate.yml` run `install.sh` from the mutable `main` of spacedock-dev/spacedock while tokens are present. The gate approval and the merge approval are two reviews (the gate job's push dismisses the first).
- comment_ratio (1.0%) measures only the one `.py` file in this diff (101 code lines); I counted the shell and YAML comments by hand: about 30 header lines, all usage or contract facts, none narrating the change.
- Left on GitHub (a fixture, not a running service): scratch repository with 8 branches, PRs #1-#7, two secrets, the App and its key file. `boundary-crossed:` none, since nothing here must persist; if the Captain wants `ops-gate` to keep running as an ops inbox, that is `external-seam` and `beyond-session` work and returns to profile selection. Local side effect disclosed earlier: spacedock 0.27.3 plugin cache beside 0.27.0.

### Summary

PASSED recommended: AC-6 to AC-12 hold on live GitHub state I read myself, with the refusal outputs themselves resting on the implementer's report. The Captain's calls are the AC-12 wording (script, not FO), removing the 268 lines of shelved hermes work, and the unenforced gate attribution if this ever leaves POC.
