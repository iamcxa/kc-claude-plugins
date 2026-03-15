# Proposals: e2e-pipeline improvements

## 1. Proactive stale-mapping detection and re-run suggestion

### Signal
- ID: sig-20260305-001
- Source: journal+episodic-memory
- Date: 2026-03-05
- Confidence: high
- Related proxy signal: mapping-freshness

### Current State
When e2e-test or e2e-walkthrough detects selectors that don't match the current DOM (stale mapping), no skill proactively suggests re-running e2e-map to refresh. Users must manually recognize the drift and invoke re-mapping.

### Suggested Change
Add mapping freshness check at the start of e2e-test and e2e-walkthrough: compare mapping file's last-modified timestamp against recent app deploys or git changes in UI directories. If stale (>7 days or relevant code changed), prompt: "Mapping may be stale — run /e2e-map --target {page} to refresh?"

### Impact Scope
- Files likely affected: `skills/e2e-test/SKILL.md`, `skills/e2e-walkthrough/SKILL.md`
- Cross-plugin dependencies: none

### North Star Alignment
Moves toward zero manual selector maintenance — stale mappings are detected before they cause test failures.

---

## 2. Cross-skill browser state reset protocol

### Signal
- ID: sig-20260306-003
- Source: journal
- Date: 2026-03-06
- Confidence: high
- Related proxy signal: pipeline-friction

### Current State
Skills share browser session state without protocol. When e2e-test runs after e2e-walkthrough, it inherits page URL, auth state, and dark-mode settings from the prior skill. This caused 4 BLOCKER-level failures in pressure testing.

### Suggested Change
Define a "clean slate" protocol: each skill that opens a browser should (a) navigate to base_url first, (b) verify auth state, (c) clear session-specific state (dark mode, locale). Add this as a pre-flight step in e2e-test, e2e-walkthrough, and e2e-map agents.

### Impact Scope
- Files likely affected: `agents/e2e-mapper.md`, `agents/e2e-test-runner.md`, `references/common-patterns.md`
- Cross-plugin dependencies: none

### North Star Alignment
Eliminates flaky tests caused by inherited browser state — each test run starts from a known state.
