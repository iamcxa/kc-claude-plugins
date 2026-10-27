# implementation follow-up message 1 (live worker, cycle 2)

Model: sonnet
Dispatched: cc91120449f0aac994632095c818f83279b03f26

## Checklist

1. Apply Captain amendment 3 (`## Captain amendments`): move AC-13 verbatim into amendment 3 under `Superseded text:`, and write its replacement as a new `**AC-14**` ("Amended by Captain, amendment 3"): the inbox core and every module it imports, transitively, import only `node:crypto` from outside the package, and its tests pass under the Netlify adapter; verified by a script that walks the core's import closure and prints each external import, and the core's test run under the Netlify adapter with zero failures. Write the new trigger-rules and key-list criteria as `**AC-15**` and `**AC-16**` the same way, each with a `Verified by:` line a test can fail.
2. Before designing the rules, read Paseo Hub's own trigger documentation (paseo.sh/docs, the hub pages, and hub.paseo.sh/api/openapi.json) and record, with URL and read date, how a Hub trigger names its channel, its match conditions and its receiver. Mirror those names and match semantics where they fit; say where and why r1 differs. Do not depend on Hub at runtime.
3. Build trigger rules in the inbox: an ordered list of rules in the instance configuration, each matching only enumerated or pattern-bounded contract fields (type, source prefix, environment, severity), first match wins, each naming one receiver (record, agent, captain). The default rule list must reproduce the routing table approved in the archived task `_archive/ops-metric-event-protocol.md` (`### Routing (inbox side)`) exactly, including heartbeat and recovered handling and `200 recorded`; a test asserts each table cell. An invalid rule list fails closed at startup.
4. Build the key list: `handle()` takes several keys from configuration and uses the contract's `parseEvent` key scoping (environments and source prefix), so a preview key cannot sign prod (D5). The read-back and runbook name each key and who creates it; secrets stay values the Captain sets, never read or printed.
5. Rerun `npm test`, `node test/mutations.mjs` and `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>` (fix within scope, at most twice), push the branch, and append `## Stage Report: implementation (cycle 3)` with plain `### Checks` and `### Summary`.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
Rulings on your cycle-2 questions: AC-13 is settled by amendment 3 (item 1). The CI job rename is accepted: main's required checks are only version parity and the multi-profile route gate (read 2026-10-27). Not in this round: 429 cap, heartbeat last seen and silent producer, claim states, key scope by type, the dashboard and adrs prompt rule; leave them listed as gaps. Outward actions stay held as before.
