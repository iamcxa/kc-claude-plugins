---
title: Dispatches name the reachable FO, the package's script paths and the secret wrapper, and a report never ends in a false FAILED line
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Four dispatch and report defects from qnow dogfooding (2026-09-28..30) that cost retries or leaked secrets.

## Scope

Captain 2026-09-30, approving the FO's batching of the dev2 fixes: 「可以」 — batch A (guardrails) first. This task covers issues #526, #527, #528 and #530.
Evidence (qnow): every worker reported "team-lead was unreachable, sent to main"; a report line "- FAILED: none." blocked `spacedock status --set`; one worker searched the whole filesystem for comment_ratio.py for about three hours; two workers printed the Clerk development secret key despite dispatch-note bans, and a user-level PreToolUse(Bash) guard (block Netlify environment and database API reads, 1Password value reads and reveals, Keychain password reads) has held since.
Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: the name the runtime actually exposes for the dispatching FO; how every dispatch carries the absolute scripts directory of the installed package version; the report-template rule that FAILED marks only an unmet item; and whether kc-dev-flow-2 ships the secret guard for adopters or documents it, plus how dispatches name one run-time secret wrapper.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
