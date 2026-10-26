# implementation dispatch 1

Model: sonnet
Dispatched: 7a5c79c64249ee15dac1c1da378c60f36dd0ed3e

## Checklist

1. Read Paseo's own docs and the Hub OpenAPI first, verify each fact the task lists before relying on it, and rehearse everything that needs no outward action locally (a Docker image for the daemon from Paseo's documented Docker setup, the fixture ops event, the in-container credential audit, the ops task and Draft PR step against a local bare remote).
2. Raise every outward action to the First Officer as one decision request naming the exact target, owner, scope and cost if known (Hub account and tokens, registering the daemon, connecting a GitHub App to Hub, running the container, placing the model credential, any push outside your worktree branch); take none on your own judgment and never read or print a credential.
3. Record AC-1 to AC-5 with primary evidence, or name each not run with its exact pending approval or blocker; a stop condition that fires ends the stage with a hold report naming the fallback r1 as designed; include one package-value observation.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc (pass it as --workflow-dir on every spacedock command).

Sources: Paseo docs at https://paseo.sh (llms.txt, docs/hub*.md, docs/docker.md, docs/security.md, docs/mcp.md, docs/plugins/reference.md) and https://hub.paseo.sh/api/openapi.json; the local paseo CLI 0.13.0 (/Users/kent/.local/bin/paseo, read --help only); the paseo, paseo-help and paseo-plugin skills under ~/.agents/skills (read, do not invoke operations). The Captain's kc-paseo-plugins repo (/Users/kent/Project/kc-paseo-plugins: spacedock-bridge, project-env ADR 0001 and 0005) is reference, read only.
Scratch repository for AC-2: iamcxa/ops-inbox-probe-scratch (default branch master; rulesets 25482703 and 25482704 have no bypass). r1 reference code: branch spacedock-ensign/ops-inbox-r1-setup-and-isolation on origin (contract fixtures under kc-ops-inbox/contract/fixtures, ops workflow under kc-ops-inbox/ops-workflow).
Do not touch relay, qnow, the r1 trigger repository spacedock-dev/subspace-relay-ops-trigger, the Netlify sites, or the Captain's running desktop daemon and its agents. Do not use the Captain's own Paseo desktop daemon as the POC daemon; the POC daemon runs in Docker.
Commit POC artifacts under kc-ops-inbox/poc-paseo-hub/ in your stamped worktree branch.
Budget 1 day. Stop conditions are in the task's Scope.
Captain standing ask, 2026-10-21: 「請持續針對套件的意義做觀察與回饋」.

roborev: Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0/extensions/roborev/roborev_gate.py --repo <your stamped worktree path> --base 7a5c79c64249ee15dac1c1da378c60f36dd0ed3e`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
