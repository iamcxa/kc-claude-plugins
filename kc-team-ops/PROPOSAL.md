# Proposals: kc-em-triage improvements (run 2)

## 1. Agent boundary unclear for decompose operations

### Signal
- ID: sig-20260310-002
- Source: journal
- Date: 2026-03-10
- Confidence: high
- Related proxy signal: triage-friction

### Current State
The boundary between em-triage skill (decompose from issue) and design-spec-writer agent (decompose from document) is not self-evident. User had to correct agent twice during design when the agent attempted layer-specific decomposition outside its scope.

### Suggested Change
Add an explicit disambiguation table at the top of the decompose flow reference: "Issue → em-triage decomposes into sub-issues. Document/spec → design-spec-writer produces design spec. Never decompose by technical layer."

### Impact Scope
- Files likely affected: `reference/decompose-flow.md`, `skills/kc-em-triage/SKILL.md`
- Cross-plugin dependencies: none

### North Star Alignment
EM can triage without confusion about which tool handles which input type.

---

## 2. Skill TDD loopholes apply to em-triage

### Signal
- ID: sig-20260315-005
- Source: memory
- Date: 2026-03-15
- Confidence: medium
- Related proxy signal: triage-completeness

### Current State
The cycle assignment gap (Step 6 mentions assignment but agents skip it) is an instance of "process inconsistency" — one of 3 known TDD loopholes. The skill lacks pressure test scenarios targeting these patterns.

### Suggested Change
Add 3 pressure test scenarios to em-triage targeting: (1) cycle assignment actually happens in Step 6, (2) all reference file cross-refs resolve, (3) acceptance criteria in each step are verifiable by agent.

### Impact Scope
- Files likely affected: test scenarios (new), `skills/kc-em-triage/SKILL.md` (strengthen Step 6)
- Cross-plugin dependencies: none

### North Star Alignment
Prevents silent step-skipping during triage, improving completeness.
