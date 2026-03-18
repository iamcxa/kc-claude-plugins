# Changelog

All notable changes to the e2e-pipeline plugin are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- `docs/pr-workflow.md` — end-to-end guide for posting E2E evidence to PRs
- Media processing pipeline section in `docs/recording-evidence.md`
- Divergence interpretation guide and observe-and-continue model in `docs/debugging.md`
- Element coverage section with JSON examples in `docs/writing-tests.md`
- Background/foreground execution table and `--fg` flag in `docs/commands.md`
- Metrics JSON and quarantine entry examples in `docs/ci-integration.md`
- Cross-references across 5 doc files

## [2.3.0] - 2026-03-18

### Added
- `/e2e-help` skill — interactive help guide with topic deep-dive and feedback collection
- `/e2e-doc-sync` skill + `e2e-doc-scanner` agent — scan skills vs docs for gaps, auto-write updates
- Two-dimension self-improvement framework (D1 skill-level + D2 project-level) for 5 skills
- `docs/multi-site-testing.md` and `docs/suites.md`

### Architecture
- 9 skills, 7 agents (added e2e-doc-scanner)
- Knowledge bootstrap phase: skills read `learned-patterns.md` at startup

## [2.2.0] - 2026-03-17

### Added
- `e2e-media-processor` agent — shared post-processing subagent for GIF (blank frame skip), MP4 (1.5x speed), thumbnail
- `--site <alias>` flag on `/e2e-test` for cross-site flow filtering
- `preconditions:` block in flow YAML for data readiness checks (psql/Supabase MCP)
- PreToolUse hook to guard against hand-written flow YAML
- PostToolUse hook to check plans for missing E2E steps
- Default route for `/e2e-skill-ops` bare invocation
- `--no-verify` next steps and correction summary in `/e2e-flow`
- Draft release media hosting for PR comments

### Changed
- Media generation extracted from browser agents to shared `e2e-media-processor` subagent
- Unified PR report template (`references/pr-report-template.md`) as single source of truth

### Fixed
- `url-not-contains` verification uses polling instead of instant check
- `.gitignore` for `e2e-reports/` preserves `skill-quality-findings.md`
- Flow-writer cross-boundary example and `manual:true` ban

### Docs
- Cross-boundary testing guide with DRC-2880 case study
- Action type chain-completeness checklist in CLAUDE.md
- `common-patterns.md` added to doc maintenance checklist

## [2.1.0] - 2026-03-16

### Added
- `Verify external` generation in flow-writer (auto-detects external services like PostHog, Langfuse)
- `Execute external` checkpoint support (symmetric counterpart to Verify)

### Docs
- Documentation Maintenance convention in CLAUDE.md
- Component removal pattern and flow-writer gotcha

## [2.0.0] - 2026-03-15

### Added
- `/e2e-flow` skill — generate flows from plans/specs/PRs, verify in browser with auto-repair
- `e2e-flow-writer` agent — autonomous flow YAML generation from codebase analysis (no browser)
- `e2e-flow-verifier` agent — adaptive flow validation with selector/step auto-repair
- `/e2e-compile` skill + Node.js compiler — compile flow YAML to standalone bash test scripts
  - Parser, resolver, codegen pipeline (TDD: 471 tests)
  - Cross-site codegen, JUnit XML output, `--coverage` flag
  - `--metrics-output` for quarantine evaluation
  - `--retries`, `--continue-on-error`, `--dry-run`, `--verbose` flags
- `e2e-quarantine.js` CLI — flaky test quarantine with GitHub issue lifecycle and PR comments
- Phase 1.8 auto-compile and divergence analysis in `/e2e-test`
- E2E-first acceptance planning loop — SessionStart hook + PreToolUse hooks
- Observe-and-continue walkthrough model with enhanced trace correlation
- CI gate template (`browser-e2e.yml`) with auth-setup, matrix execution, quarantine

### Changed
- `/e2e-walkthrough` narrowed to exploration/QA/debug/demo (generation moved to `/e2e-flow`)
- `e2e-acceptance` removed, all references replaced with `/e2e-flow`
- Dispatch `--smoke` and `--verify` routes rerouted to `/e2e-flow`

### Fixed
- Dual-browser issue on recording (startup order: `record start` before `open`)
- 6 validation warnings resolved

### Architecture
- 7 skills, 5 agents (added flow-writer, flow-verifier)
- Compiler as deterministic alternative to LLM-based execution
- `docs/` directory restructured from single README

## [1.5.0] - 2026-03-14

### Added
- External verification checkpoints (`action: "Verify external"`) with `--verify` mode on walkthrough
- Auto-gitignore for large binary artifacts (`.webm`, `.mp4`, `trace.zip`)
- Replay instructions in test/walkthrough reports

## [1.4.0] - 2026-03-12

### Added
- MP4 video conversion for test runs (`test-run.mp4`) and walkthroughs (`walkthrough.mp4`)
- PR comment template for posting E2E results
- Merged into kc-claude-plugins marketplace monorepo

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
