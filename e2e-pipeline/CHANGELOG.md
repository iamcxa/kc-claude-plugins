# Changelog

## [1.1.0] - 2026-03-09

### Added
- 5 skills: e2e-dispatch, e2e-map, e2e-test, e2e-walkthrough, e2e-skill-ops
- 3 context-isolating subagents: e2e-mapper, e2e-test-runner, e2e-trace-analyzer
- Multi-site testing support with session isolation
- YAML-based UI mappings and flow definitions
- Trace analysis for API failures and console errors
- Reference docs: commands.md, common-patterns.md

### Architecture
- Skills run as thin orchestrators in main context
- Browser-heavy work delegated to subagents to protect context window
- agent-browser CLI as the single browser automation backend
