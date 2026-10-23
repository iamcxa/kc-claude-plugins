# implementation dispatch 1

Model: sonnet
Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0

## Checklist

1. Exercise the riskiest path first and locally: signature verify, strong-consistency onlyIfNew dedupe on source+id, and the workflow_dispatch call, with three sends of one webhook-id (one more than 60 seconds later) and one tampered send against a local fake GitHub API, before any outward action.
2. Raise every outward action to the First Officer as one decision request naming the exact target, owner, permissions and cost if known (scratch Netlify site and its environment variables, the Slack destination, the dispatch-only credential, Actions secrets, the workflow push to the scratch repository's default branch), and take none on your own judgment.
3. Record AC-1 to AC-4 with primary evidence from the real scratch site and repository, the measured latencies, and one package-value observation: what these measurements say about whether an inbox in front of Spacedock is worth building.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc (pass it as --workflow-dir on every spacedock command).

Design inputs (engineering-reviewer, opus, 2026-10-21; verify each against the vendor's own docs before relying on it): CloudEvents 1.0 attributes (id, source, type, specversion; identical source+id are duplicates); Standard Webhooks signing (webhook-id, webhook-timestamp, webhook-signature over id.timestamp.body, HMAC-SHA256 v1); Netlify Blobs default to eventual consistency, so open the store with strong consistency and dedupe with set(..., { onlyIfNew: true }); workflow_dispatch needs Actions: write, returns the run id and html_url, and the workflow file must be on the default branch; mint the push-capable token inside the workflow with actions/create-github-app-token and explicit permission-* inputs. Pin every action and tool by commit SHA or exact version; do not pipe a mutable-branch installer.
Reuse the scratch repository iamcxa/ops-inbox-probe-scratch (default branch master; ruleset 25482703 requires a PR, so a workflow push needs the Captain's ruleset off/on, which you request). The existing App ops-inbox-probe-iamcxa (id 5397558, installation 173426167, contents and pull_requests write) may serve the in-workflow mint; the inbox's dispatch-only credential is a separate decision you propose.
Secrets: never read, print or copy a credential. The Captain sets Netlify environment variables, Actions secrets and any Slack webhook URL himself; you give him the exact names and commands. Environment-variable reads on Netlify are blocked by a local hook; do not work around it.
Do not touch relay, qnow or any other repository or Netlify site. Commit POC artifacts under kc-ops-inbox/ in your stamped worktree branch; no plugin.json, no marketplace entry.
Budget 1 day. Stop and hold-report on: duplicate runs or a missed strong read after two materially different attempts; a Netlify function cannot verify and dispatch within its limits; the inbox needs a push-capable credential.

roborev: Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <your stamped worktree path> --base c27e76590c1d2dc910e7fa2d332242a7534df0b0`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
