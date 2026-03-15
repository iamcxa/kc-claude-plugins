# Proposals: e2e-pipeline improvements (run 2)

## 1. Cross-component sync enforcement in skill-ops

### Signal
- ID: sig-20260314-006
- Source: memory
- Date: 2026-03-14
- Confidence: medium
- Related proxy signal: pipeline-friction

### Current State
When an agent adds a feature (e.g., new output file), the orchestrating skill must be updated to present the new artifact. This sync is currently manual — the Impact Matrix in e2e-skill-ops doesn't enforce checking the dispatching skill after agent changes.

### Suggested Change
Add a "Dispatch Sync" check to e2e-skill-ops: after any agent .md change, automatically scan the dispatching skill for references to the agent's output contract. If the skill doesn't mention the new artifact, flag it as a sync gap.

### Impact Scope
- Files likely affected: `skills/e2e-skill-ops/SKILL.md`
- Cross-plugin dependencies: none

### North Star Alignment
Prevents silent feature loss when agents evolve faster than orchestrating skills.
