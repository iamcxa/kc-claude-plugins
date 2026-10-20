# implementation dispatch 1

Model: sonnet
Dispatched: ad44f0cbf42274ff65802cabc52ebe919f159fd5

## Checklist

1. Exercise the riskiest claim first: a hermes instance (pinned Hermes Agent commit) boots by default as the Spacedock First Officer of the minimal ops workflow and stops at the ops decision gate without self-approving (AC-2, AC-3), rehearsed locally before any outward action.
2. Every outward action (exe.dev VM, any spend, Codex token placement, test GitHub repository and ruleset, machine account, Slack app, any message to a human) is raised to the First Officer as a decision request and waited on before it is taken; none is taken on your own judgment.
3. AC-1 to AC-5 each carry primary evidence in the stage report, or are named not run with the exact pending approval or blocker; a stop condition that fires ends the stage with a hold report.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc (pass it as --workflow-dir on every spacedock command).

Authority and outward actions (Captain, 2026-10-20: each outward action asks first):
- Before creating an exe.dev VM, spending money, creating a GitHub repository, ruleset, machine account or collaborator grant, creating a Slack app, or posting to any human, stop and SendMessage(to="main") a decision request naming the exact action, target and cost if known. Wait for the answer; the First Officer relays it to the Captain.
- Never read, print, copy or handle the Codex token or any other credential. The Captain places the token on the VM himself; you document where hermes expects it.
- Do not edit subspace-relay, qnow, kc-hermes-spacedock or any Spacedock state other than this task's stage report.

Where artifacts go:
- Commit POC artifacts (hermes profile configuration, webhook route, ops triage skill, minimal ops workflow README for the test repository, rehearsal scripts, evidence) under kc-ops-inbox/ in your stamped worktree branch. That branch supersedes the branch name in the task Scope (FO note: dispatch build creates the worktree branch).
- No .claude-plugin/plugin.json, no marketplace entry, no release edits.

Read third-party mechanisms from their own docs and source:
- Hermes Agent: github.com/NousResearch/hermes-agent. Pin one commit SHA and cite files there. FO research at HEAD 31df1227890643eb9f5f08db6b2a5c37d4a6f5cc (2026-10-20) found: generic webhook platform at /webhooks/<route> (website/docs messaging/webhooks.md; gateway/platforms/webhook.py) with Standard Webhooks signature support, per-route prompt/skills/toolsets/deliver/coalesce; approvals.unattended_mode deny for webhook sessions by default; allowlists via *_ALLOWED_USERS / GATEWAY_ALLOWED_USERS (default deny); pre_tool_call hooks can block in code; profiles isolate HERMES_HOME; Slack adapter is Socket Mode with Block Kit approval buttons; a Codex app-server runtime exists (features/codex-app-server-runtime.md). Verify each before relying on it, and establish from hermes docs how a Codex token authenticates the model.
- Spacedock 0.27 README: Claude Code, Codex and Pi are tier-1; Hermes-class agents run Spacedock "through skill systems". No recorded run of hermes as First Officer exists; kc-hermes-spacedock (main 556217b) launches the FO as a separate Claude process, so it is pattern prior art (Briefing/Resolution tooling, posix-dispatch), not evidence of hermes-as-FO.
- exe.dev: read its own docs for always-on service, inbound HTTPS, Docker and price before proposing the VM.

Synthetic event: model fields on relay's removed DiagnosisRecord at subspace-relay PR #400 head 55ad4c8e (netlify/lib/capacity-notice.ts): v, event (bound-ceiling-near | bound-ceiling-full), at, day, count, limit, limitSource. Read-only; do not push to relay.

Budget and stops: at most 2 days. Stop and hold-report if hermes cannot boot the First Officer after two materially different attempts, if the hermes FO passes any gate without the Captain's reply, or if exe.dev cannot keep the service running or accept inbound HTTPS. The fallback named for the Captain is "hermes launches Claude Code as the FO".

roborev: Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/extensions/roborev/roborev_gate.py --repo <your stamped worktree path> --base ad44f0cbf42274ff65802cabc52ebe919f159fd5`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
