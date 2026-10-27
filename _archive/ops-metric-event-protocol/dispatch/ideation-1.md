# ideation dispatch 1

Model: opus
Dispatched: a11707d5ec19ee34777c7bdeac4c4d100bc84857

## Checklist

1. Author the protocol design in the task file for AC-1 to AC-4 with reproducible evidence clauses: the project-side and inbox-side boundary, the metric event type and its fixed fields, crossing, recovered and heartbeat events, environment and severity routing, sender rules (same id on retry, response codes and retry, per-incident cap), context pointers and enumerated values, signing-secret provisioning and rotation, pre-inbox delivery with the same body, and how relay.capacity.ceiling and qnow's SMS usage map onto it; name each unresolved decision with one recommendation.
2. Record, without building, a store recommendation for raw events, counts and threshold records and the PostHog projection, ranked for a Netlify runtime and for one long-running process, using the evidence already gathered; and check the contract v1 on branch spacedock-ensign/ops-inbox-r1-setup-and-isolation for what must change.
3. Send the draft to qnow dev2 FO (Paseo agent 519ab4c8) as first-adopter reviewer through FO only (send it to me; I relay), and deliver the PRFAQ and Mermaid plus one package-value observation.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (pass it as --workflow-dir on every spacedock command).
Model: opus, chosen by FO because a cross-project contract is hard to reverse.

Ideation writes no repository file, branch or commit; the design and criteria live in the task file.
Read first: this task's Scope, FO alignment (the Captain's words relayed by qnow FO, including the storage direction and 「目前兩個服務剛好都跑在 netlify」), and both backlog briefings.
Inputs: contract v1 at kc-claude-plugins origin branch spacedock-ensign/ops-inbox-r1-setup-and-isolation (kc-ops-inbox/contract/, CloudEvents attributes, Standard Webhooks signing, allowlisted data per type, source+id dedupe, subject incident key); r1 task ops-inbox-r1-setup-and-isolation (dev2 state) design; closed POCs in docs/dev2-poc state _archive (inbox-exactly-once-delivery-poc: Blobs consistency, onlyIfNew; paseo-hub-docker-ops-poc: Hub archives at finish, free strings up to 500 characters reached the prompt); relay ADRs 0049 (no account identifiers) and 0060 (ceiling); qnow's Clerk facts as relayed (sms.created unverified; Platform usage endpoint).
The inbox runtime is not decided (Captain 2026-10-21: 「平台是剛好是 netlify，不是平台一定是 netlify」); r1 keeps Netlify Functions plus a GitHub-hosted runner.
Do not message other agents directly; route qnow FO review through me. Do not touch relay, qnow or any secret.
Captain standing ask, 2026-10-21: 「請持續針對套件的意義做觀察與回饋」.
