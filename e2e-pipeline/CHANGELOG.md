# Changelog

All notable changes to the e2e-pipeline plugin are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [2.9.0](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v2.8.1...e2e-pipeline-v2.9.0) (2026-07-14)


### Features

* **e2e-pipeline:** add secure runtime capture and finalizers ([#41](https://github.com/iamcxa/kc-claude-plugins/issues/41)) ([390a16d](https://github.com/iamcxa/kc-claude-plugins/commit/390a16d5916f9d6fe901c5c1fc08bc2a9efe7c17))


### Bug Fixes

* **e2e-pipeline:** close SC-1032 verify gaps ([#42](https://github.com/iamcxa/kc-claude-plugins/issues/42)) ([267d499](https://github.com/iamcxa/kc-claude-plugins/commit/267d499f5803ba4709c4e9649fbdcf339d97c7c1))
* **e2e-pipeline:** enforce nested readback contracts ([#43](https://github.com/iamcxa/kc-claude-plugins/issues/43)) ([e9dd6d2](https://github.com/iamcxa/kc-claude-plugins/commit/e9dd6d28b54287879db2af5841db7071b5f80630))
* **e2e-pipeline:** preserve assertion probe failures ([#38](https://github.com/iamcxa/kc-claude-plugins/issues/38)) ([56f43e7](https://github.com/iamcxa/kc-claude-plugins/commit/56f43e7cecde4881bbd59a91350b05e04a021f55))

## [2.8.1] - 2026-05-28 — Negation grammar: text-not-visible + page-qualified element-not-visible

Closes 2 of 3 grammar gaps in compile-ready flow expects. Previously these forms fell through to `deferred` (runtime echoed `TODO`, no actual assertion).

### Added
- **`text 'X' not on page`** / **`text "X" not visible`** — new `text-not-visible` expect type. Codegen emits an inverted snapshot grep (fails if the text IS found).
- **`element not visible on <page>`** / **`element is not visible on <page>`** — page-qualified variants of the existing `element-not-visible` type. Routes to the same codegen path; symmetric with the positive `element visible on <page>` form.

### Notes
- Surfaced by a downstream compile experiment for `DataRecce/recce-cloud-infra#1383` (`signin-error-handling.yaml` went from 12 active / 3 deferred to 15 active / 0 deferred after this patch).
- `element href = 'X'` attribute equality (the third gap) remains out of scope — grammar design pending.
- Pattern ordering preserves the precedence convention: page-qualified before bare, negated before positive (mirrors existing `url-not-contains` listed before `url-contains`).

## [2.8.0] - 2026-05-06 — UI Verify skill + Codex manifest

Adds a deterministic static-UI verification skill and ships the Codex platform manifest alongside the existing Claude Code plugin manifest.

### Added
- **`ui-verify` skill** — declarative computed-style regression check. YAML-driven, browser-driven via `agent-browser`, machine-judged pass/fail per check. Pseudo-element checks supported. Reuses `.claude/e2e/mappings/<app>.yaml` for `base_url` + `auth.test_accounts`. Runner at `skills/ui-verify/bin/run.js` (Node, uses plugin's `js-yaml` dep). Report at `.claude/e2e/reports/ui-verify-<stem>-<ts>.md`.
- **Codex plugin manifest** (`.codex-plugin/plugin.json`) — enables installation in Codex alongside Claude Code. Auto-discovers skills under `./skills/`.

### Changed
- **Skill count**: 10 → 11 (CLAUDE.md Architecture section + skills directory listing updated).

### Notes
- Scope of `ui-verify` is intentionally Mode B only (fixed selectors × fixed expected values). Forensics / dynamic queries deliberately defer to `agent-browser` REPL.
- Complements rather than replaces `e2e-flow` — flow checks dynamic behavior, ui-verify checks static computed style.

## [2.7.0] - 2026-05-04 — Selector Grammar Alignment

Aligns mapper output with agent-browser CLI runtime contract per issue #7.

### Changed
- **e2e-mapper**: Selector Priority rewritten to emit native agent-browser forms (`find role <r> --name "<v>"` subcommand strings, CSS attribute selectors, `:nth-of-type(N)` pseudo-class). Banned Playwright vocabulary: `role=X[name=Y]`, `>> nth=N`, bare `text=`, `has-text(`.
- **e2e-test-runner**: Removed silent eval-fallback for selector mismatches. Native-form selectors that fail to resolve now fail loud. New `eval_fallback_hits` counter in trace + final report.
- **e2e-flow-verifier / e2e-debug-observe**: Aligned to new contract; do not accept eval-fallback as silent-pass evidence.
- **compiler**: Promoted `selectorToA11yPattern` to canonical translator at `compiler/lib/selector-translate.js`. Single definition site across the plugin.
- **fixtures**: Regenerated to canonical form. Backward-compat retained in translator.

### Added
- **scripts/lint-mapping.sh** — linter rejects 4 banned Playwright token classes from mapping YAMLs. Use in CI to prevent regression.
- **scripts/measure-fallback-baseline.sh** — orchestrates per-flow eval_fallback_hits measurement; emits baseline JSON for regression bounds.
- **test/integration-smoke.sh** — full /e2e-map → linter → /e2e-test smoke pipeline.
- **test-fixture-flow.yaml** — self-contained smoke flow using canonical mapping forms.

### Captain Bet
After ship: captain observes `eval_fallback_hits = 0` on a fresh `/e2e-map → /e2e-test` cycle (within 1 week). Pre-mortem mitigation: baseline measured pre-T2.2 to bound regression wave.

### References
- Issue: https://github.com/iamcxa/kc-claude-plugins/issues/7
- Pitch: docs/ship-flow/001-selector-grammar-alignment/
- Design: design.md (Candidate 1 chosen — find role <r> --name "<v>" subcommand)

### Course correction (PR #8 review)

Copilot static-contract review of PR #8 caught that the Priority 2 canonical form originally chosen — `find role <r> --name "<v>"` as a `selector:` value in mapping YAML — is a **subcommand chain** parsed by the agent-browser CLI, not a selector string. Passing it to selector-accepting commands (e.g., `is visible`, `wait`, compiled script grep patterns) causes silent mishandling. The canonical Priority 2 form is updated to **Candidate 2**: `[role="<r>"][aria-label="<v>"]` (CSS attribute selector). All agent prompts, skill docs, and references updated accordingly. The old form is now marked DEPRECATED in the Selector Priority sections; the linter already rejects the BANNED Playwright `role=X[name=Y]` form and is unaffected by this change.

## [Unreleased]

## [2.4.0] - 2026-03-20

### Added
- **CLI terminal recording mode** for cross-boundary flows — `asciinema rec` → `agg` → GIF → `ffmpeg` → MP4
- `e2e-media-processor` agent: `cast_path`, `cast_cols`, `cast_rows` input fields for CLI mode
- CLI-only flow detection in `e2e-flow` (Phase 2.5), `e2e-test` (Phase 1.5), `e2e-walkthrough` (Phase 4)
- `docs/assets/cli-recording-demo.gif` — demo of terminal recording pipeline
- `doc-probe` agent: added missing `color: yellow` field
- `docs/commands.md` § CLI-Only Flow Recording
- `docs/cross-boundary-testing.md` § Recording CLI-Only Flows (with demo GIF)
- `e2e-help` topic keywords: `cli-recording`, `terminal-recording`, `cli-only`
- Troubleshooting entry for missing `asciinema`/`agg` in `docs/debugging.md`
- CLI recording prerequisites in `docs/getting-started.md`
- CI runner note for `asciinema`/`agg` in `docs/ci-integration.md`

### Changed
- Default report output directory from `e2e-reports/` to `.claude/e2e/reports/`, unifying all E2E artifacts under `.claude/e2e/` (DEV-2)

### Documentation
- `docs/pr-workflow.md` — end-to-end guide for posting E2E evidence to PRs
- Media processing pipeline section in `docs/recording-evidence.md` (browser + CLI dual-track)
- Divergence interpretation guide and observe-and-continue model in `docs/debugging.md`
- Element coverage section with JSON examples in `docs/writing-tests.md`
- Background/foreground execution table and `--fg` flag in `docs/commands.md`
- Metrics JSON and quarantine entry examples in `docs/ci-integration.md`
- Cross-references across 9 doc files for CLI recording discoverability

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
