# ideation dispatch 1

Model: opus
Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0

## Checklist

1. Author the design for AC-1 to AC-5 in the task file with each criterion's reproducible evidence clause, and name for the Captain each unresolved decision with one recommendation: delivery semantics (at-most-once or at-least-once with reconciliation), the mechanism that limits the inbox credential to one workflow, where the gate record lives so a push does not dismiss the approval, the inbox host, and the form of the setup command.
2. Exercise the riskiest unverified mechanism before the gate with the smallest read-only or local probe (for example how a credential can be limited to one workflow), and record what ran and what is only from docs; no deployment, App, secret, ruleset or push.
3. Deliver the PRFAQ and Mermaid with matching actors, order, branches, approvals and stops, the `ui` surface artifact (the Slack message and the setup command output), and one package-value observation.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (pass it as --workflow-dir on every spacedock command).
Model: opus, chosen by FO because the contract and the authority boundary are hard to reverse (README ideation rule).

Ideation writes no repository file, branch or commit; the design, criteria and any ADR draft live in the task file.
Inputs to read first:
- POC1 (closed PASSED 2026-10-21): /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state/_archive/hermes-ops-fo-exe-dev-poc.md and its folder (observer.md, validation report).
- POC2 (closed PASSED 2026-10-23): .../_archive/inbox-exactly-once-delivery-poc.md and its folder (findings F1 Slack leg unmeasured, F2 Actions write is repository-wide, F4 Blobs atomicity under parallel retries unproven; at-most-once chosen).
- Code reference (not a candidate): branches spacedock-ensign/hermes-ops-fo-exe-dev-poc (aae7041b) and spacedock-ensign/inbox-exactly-once-delivery-poc (cd079cb8) on origin iamcxa/kc-claude-plugins.
- Journey map: docs/journey/kc-ops-inbox/ on branch iamcxa/kc-ops-inbox at 0a1d59ce (local branch in /Users/kent/.paseo/worktrees/2cmr9mcu/kc-ops-inbox).
- The engineering-reviewer findings of 2026-10-21 are summarized in POC2's Scope and FO alignment.
Read third-party mechanisms from their own docs (GitHub Apps and fine-grained permissions, Actions workflow_dispatch and repository_dispatch, rulesets, Slack incoming webhooks, CloudEvents, Standard Webhooks) and cite URL and date.
Do not touch relay, qnow, the scratch repository, the scratch Netlify site or any secret.
Captain standing ask, 2026-10-21: 「請持續針對套件的意義做觀察與回饋」.
