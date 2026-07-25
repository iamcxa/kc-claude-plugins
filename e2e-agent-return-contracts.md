---
title: Give agent returns a contract the orchestrator can reject
status: backlog
source: sprint-3 (skill-layer prose control flow) entity; identified in the original agent-native audit, filed once the sprint boundary made it cohesive
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: eyqabwsxe0pwpcacfv3p69f6
---

## Problem

Every handoff between a skill and its agents is free text parsed by prose instruction. The
mapper is told to "end your response with this exact structured block (the orchestrator parses
it)" and emits a markdown `## Summary` with `mapping_path`, `pages_found`, `elements_mapped`,
`unexplored_areas`, `screenshots`; the flow-writer returns `flow_path`, `step_count`,
`warnings`, `coverage_notes` as loose lines; the verifier returns a longer variant. Nothing
validates any of it. When the block is malformed or absent, the documented recovery is to
report the agent's raw output to the user and ask whether to retry.

This is the same defect as the compiler's silent acceptance, one layer up: the contract is
stated in prose to the party that must honour it, and the party that depends on it cannot
refuse a violation. An agent that returns a plausible-looking summary with a wrong path or an
invented count is indistinguishable from one that succeeded, and the orchestrator proceeds on
it.

## Notes for ideation

- Cheapest shape that closes it: have each agent write its result to a file at a path the
  orchestrator supplies, in a defined structure, and have the orchestrator read and validate
  that file rather than parse the reply. The reply becomes narration; the artifact becomes the
  contract. This also removes the verbose block from the orchestrator's context.
- Scope the structure to what the orchestrator actually branches on. Fields nobody reads are
  cost without contract — check each declared field against its consumer in the skill before
  carrying it forward.
- Coordinate the definition with [[e2e-schema-contract]], which owns the artifact schemas.
  This entity should not mint a second, parallel notion of "validated structure".
- Falsification: an agent returning a malformed or absent result artifact must halt the
  orchestrator with a specific error, not a request for user triage. Restoring the prose parse
  must make the malformed case pass silently again.
