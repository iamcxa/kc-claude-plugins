# implementation dispatch 2

Model: sonnet
Dispatched: 1e65b046f26efd067366c943b75f3ccedbce33dd

## Checklist

1. Merge origin/main (contract v1 landed at d7eeeef2) into this branch; main's `kc-ops-inbox/contract/` is authoritative: take it, delete r1's own contract copy, and make the inbox core and every bin script import the contract module instead of duplicating parse, signature or key logic. All existing tests pass again, with relay fixtures changed to `ops.metric.*` (D2) and Sentry fixtures to a `urn:sentry:` source.
2. Renumber the axis ADR from 0031 to 0040 (file name, heading, every reference); `python3 kc-adr/scripts/adr_lint.py docs/adr --require 0040` exit 0 and the `**Words:**` quotes still byte-equal to their sources.
3. Fix H1 in the contract: a key is unusable when its secret decodes to fewer than 16 bytes (`"whsec_="`, `"whsec_!!!"`, `"!!!"`, `"whsec_a"`, `"whsec_ "` must no longer verify a forged signature), with a test and a mutation; update the contract README.
4. List each inbox-runtime gap the contract README assigns to r1 (routing by environment and severity, 200 recorded, 429 cap, heartbeat last seen, silent producer, 5xx to 504, claim states) and say for each whether r1's accepted criteria AC-7 to AC-13 need it; build only what an accepted criterion needs, and return the rest to FO as a decision, not built.
5. Run the full `kc-ops-inbox` test suite and the roborev gate; report the new head.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0
Send your completion message to `main` (the appended completion block names `team-lead`; use `main`).

Resume of a paused implementation. Read the task file first: `## FO alignment` (the resume note dated 2026-10-27, the pause and the 2026-10-26 collision and follow-up notes), `## Number guards` (ADR: 0040), `## Acceptance criteria`, and your predecessor's `## Stage Report: implementation`. Your worktree is the existing `.worktrees/spacedock-ensign-ops-inbox-r1-setup-and-isolation` at 1e65b046; the branch is already pushed to origin with no PR.

The protocol task that landed the contract is archived at `.spacedock-state/_archive/ops-metric-event-protocol.md`; its design and its three rounds of code review are the reason main's contract differs from r1's. Do not weaken any contract rule while merging; if r1 code depends on behaviour main's contract now refuses, change r1's code, not the contract (H1 is the only contract change in scope).

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Outward actions stay held: you may push this branch; do not open a PR, deploy, touch the Netlify site, the trigger repository, any GitHub App, secret, Slack, or relay. Commit hooks run normally. Append `## Stage Report: implementation (cycle 2)` with plain `### Checks` and `### Summary` subheadings.
