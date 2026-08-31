# Changelog

All notable changes to the e2e-pipeline plugin are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [3.3.5](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.3.4...e2e-pipeline-v3.3.5) (2026-08-31)


### Bug Fixes

* **e2e-pipeline:** require declared profile liveness before verification ([#289](https://github.com/iamcxa/kc-claude-plugins/issues/289)) ([2e8595f](https://github.com/iamcxa/kc-claude-plugins/commit/2e8595f0a1fa4448bc14a56baedd18214824158e))

## [3.3.4](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.3.3...e2e-pipeline-v3.3.4) (2026-08-19)


### Bug Fixes

* **e2e-pipeline:** anchor the click action grammar so no click is accepted on a prefix ([#191](https://github.com/iamcxa/kc-claude-plugins/issues/191)) ([03f0325](https://github.com/iamcxa/kc-claude-plugins/commit/03f0325515c110bc12a022fc5bbf662ec7887821))

## [3.3.3](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.3.2...e2e-pipeline-v3.3.3) (2026-08-10)


### Bug Fixes

* **e2e-pipeline:** empty the CI exclusion list — all three [#174](https://github.com/iamcxa/kc-claude-plugins/issues/174) residuals ([#186](https://github.com/iamcxa/kc-claude-plugins/issues/186)) ([e6069c2](https://github.com/iamcxa/kc-claude-plugins/commit/e6069c23fe6091629b36d1a0ce12a074fec41803))
* **e2e-pipeline:** refuse ${...} in a fill value, which two executors read differently ([#179](https://github.com/iamcxa/kc-claude-plugins/issues/179)) ([#184](https://github.com/iamcxa/kc-claude-plugins/issues/184)) ([bd2b142](https://github.com/iamcxa/kc-claude-plugins/commit/bd2b1421ddb0d3fff6053ddc044f9575f08c2df4))

## [3.3.2](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.3.1...e2e-pipeline-v3.3.2) (2026-08-09)


### Bug Fixes

* **e2e-pipeline:** give the fidelity states an order, found by running them ([#148](https://github.com/iamcxa/kc-claude-plugins/issues/148)) ([#169](https://github.com/iamcxa/kc-claude-plugins/issues/169)) ([952371f](https://github.com/iamcxa/kc-claude-plugins/commit/952371f6e41e267e7d56b72918a1703c81ec7ff5))
* **e2e-pipeline:** say on the receipt what verified did not cover ([#149](https://github.com/iamcxa/kc-claude-plugins/issues/149)) ([#163](https://github.com/iamcxa/kc-claude-plugins/issues/163)) ([5018dea](https://github.com/iamcxa/kc-claude-plugins/commit/5018deae9b614ae1b2a23e08580cd8b7a8f308dd))
* **e2e-pipeline:** test the temp-root property, not a proxy for it ([#174](https://github.com/iamcxa/kc-claude-plugins/issues/174)) ([#175](https://github.com/iamcxa/kc-claude-plugins/issues/175)) ([0f6af32](https://github.com/iamcxa/kc-claude-plugins/commit/0f6af32ae7fdca42075519320343f040d3eeea39))

## [3.3.1](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.3.0...e2e-pipeline-v3.3.1) (2026-08-07)


### Bug Fixes

* **e2e-pipeline:** sprint S2 — make every green artifact mean what it says ([#122](https://github.com/iamcxa/kc-claude-plugins/issues/122) [#150](https://github.com/iamcxa/kc-claude-plugins/issues/150) [#148](https://github.com/iamcxa/kc-claude-plugins/issues/148) [#121](https://github.com/iamcxa/kc-claude-plugins/issues/121) [#124](https://github.com/iamcxa/kc-claude-plugins/issues/124)) ([#157](https://github.com/iamcxa/kc-claude-plugins/issues/157)) ([fe3c9f4](https://github.com/iamcxa/kc-claude-plugins/commit/fe3c9f4466c2fd8e7688680688b93613b9117b39))

## [3.3.0](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.2.0...e2e-pipeline-v3.3.0) (2026-08-04)


### Features

* **e2e-pipeline:** define deterministic visibility semantics ([#91](https://github.com/iamcxa/kc-claude-plugins/issues/91)) ([#140](https://github.com/iamcxa/kc-claude-plugins/issues/140)) ([3cbdb48](https://github.com/iamcxa/kc-claude-plugins/commit/3cbdb481f09aca051c7725ca618793beea448946))

## [3.2.0](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.1.1...e2e-pipeline-v3.2.0) (2026-08-02)


### Features

* **e2e-pipeline:** add diff-scoped mapping lint gate ([d3a8046](https://github.com/iamcxa/kc-claude-plugins/commit/d3a804650ab626b6ff8cb48f3bf419fb52ff1f5c)), closes [#126](https://github.com/iamcxa/kc-claude-plugins/issues/126)
* **e2e-pipeline:** enforce the selector grammar at compile time ([#88](https://github.com/iamcxa/kc-claude-plugins/issues/88)) ([#128](https://github.com/iamcxa/kc-claude-plugins/issues/128)) ([8634d89](https://github.com/iamcxa/kc-claude-plugins/commit/8634d8933056da5a13ca7914a336cde93fc6bc78))


### Bug Fixes

* **e2e-pipeline:** size the socket namespace against the session-named socket ([#135](https://github.com/iamcxa/kc-claude-plugins/issues/135)) ([27bff48](https://github.com/iamcxa/kc-claude-plugins/commit/27bff48004e7d046959fd6a5614668770fa00118))
* **kc-plugin-forge:** package release helper contracts ([#133](https://github.com/iamcxa/kc-claude-plugins/issues/133)) ([0af7a71](https://github.com/iamcxa/kc-claude-plugins/commit/0af7a7124d98bd08a0ba93e43fb1bb23da3fe174))

## [3.1.1](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.1.0...e2e-pipeline-v3.1.1) (2026-08-01)


### Bug Fixes

* **e2e-pipeline:** land the selector-grammar canon correction ([#123](https://github.com/iamcxa/kc-claude-plugins/issues/123)) ([7108495](https://github.com/iamcxa/kc-claude-plugins/commit/71084954a55e2b57371486367ff51d00508b1973))

## [3.1.0](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.0.1...e2e-pipeline-v3.1.0) (2026-07-30)


### Features

* **e2e-pipeline:** add runtime-owned diagnostic init hooks ([#115](https://github.com/iamcxa/kc-claude-plugins/issues/115)) ([58d6969](https://github.com/iamcxa/kc-claude-plugins/commit/58d69694f02078b9c9543920973e62b7d84e4a29))

## [3.0.1](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v3.0.0...e2e-pipeline-v3.0.1) (2026-07-30)


### Bug Fixes

* **e2e-pipeline:** align trace producer and artifact formats ([#106](https://github.com/iamcxa/kc-claude-plugins/issues/106)) ([90135a2](https://github.com/iamcxa/kc-claude-plugins/commit/90135a25669df8dd62bde07d6193c69f4fac3195))
* **e2e-pipeline:** bind browser snapshots and first navigation ([#108](https://github.com/iamcxa/kc-claude-plugins/issues/108)) ([ec9502c](https://github.com/iamcxa/kc-claude-plugins/commit/ec9502cb60611a22fb65d4ba2b850dbc58fd33d3))

## [3.0.0](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v2.9.1...e2e-pipeline-v3.0.0) (2026-07-30)


### ⚠ BREAKING CHANGES

* **e2e-pipeline:** Unsupported expect forms now fail compilation; the deferred-success warning/count/runtime-TODO contract is removed. Rewrite them with supported grammar or mark genuinely manual coverage as {not_automated: <reason>}.

### Features

* **e2e-pipeline:** add --json structured diagnostics to e2e-compile ([4bf875e](https://github.com/iamcxa/kc-claude-plugins/commit/4bf875ef2d7984de4f5eb535e8bb79b327371aee))
* **e2e-pipeline:** promote recurring pipeline defects ([2067bc9](https://github.com/iamcxa/kc-claude-plugins/commit/2067bc9524d6c0ffe0d9319cd0b2c5404a17c908))
* **e2e-pipeline:** recognize text visibility predicate forms ([4bf875e](https://github.com/iamcxa/kc-claude-plugins/commit/4bf875ef2d7984de4f5eb535e8bb79b327371aee))
* **e2e-pipeline:** require explicit handling for unsupported expects ([4bf875e](https://github.com/iamcxa/kc-claude-plugins/commit/4bf875ef2d7984de4f5eb535e8bb79b327371aee))


### Bug Fixes

* **e2e-pipeline:** bind page-qualified element assertions ([4bf875e](https://github.com/iamcxa/kc-claude-plugins/commit/4bf875ef2d7984de4f5eb535e8bb79b327371aee))
* **e2e-pipeline:** bound trace finalization and reject invalid archives ([#95](https://github.com/iamcxa/kc-claude-plugins/issues/95)) ([c8d6d61](https://github.com/iamcxa/kc-claude-plugins/commit/c8d6d6192182e0a0d5b56c6e93b492bdbd02df43))
* **e2e-pipeline:** clear release blockers ([4bf875e](https://github.com/iamcxa/kc-claude-plugins/commit/4bf875ef2d7984de4f5eb535e8bb79b327371aee))
* **e2e-pipeline:** harden runtime ownership and local services ([#100](https://github.com/iamcxa/kc-claude-plugins/issues/100)) ([3922aa8](https://github.com/iamcxa/kc-claude-plugins/commit/3922aa89fa34958412b9e7e7d325cc74e8c38b4c))
* **e2e-pipeline:** isolate browser runtime to Chrome for Testing ([#96](https://github.com/iamcxa/kc-claude-plugins/issues/96)) ([4f0fe13](https://github.com/iamcxa/kc-claude-plugins/commit/4f0fe13794efae9e341a931ea255e7df583bc7e8))
* **e2e-pipeline:** report manual-only compiled steps separately ([4bf875e](https://github.com/iamcxa/kc-claude-plugins/commit/4bf875ef2d7984de4f5eb535e8bb79b327371aee))
* **e2e-pipeline:** stop reporting a matched snapshot as a no-match under pipefail ([#68](https://github.com/iamcxa/kc-claude-plugins/issues/68)) ([d79f9ea](https://github.com/iamcxa/kc-claude-plugins/commit/d79f9ea200200b02e9f4819a95bab6c5a7f502f4))
* **e2e-pipeline:** support isolated flow-managed auth ([#97](https://github.com/iamcxa/kc-claude-plugins/issues/97)) ([d5bc97a](https://github.com/iamcxa/kc-claude-plugins/commit/d5bc97ad73ca433e4cdde5c9571a827a19955c54))

## [2.9.1](https://github.com/iamcxa/kc-claude-plugins/compare/e2e-pipeline-v2.9.0...e2e-pipeline-v2.9.1) (2026-07-14)


### Bug Fixes

* **marketplace:** repair release version propagation ([#45](https://github.com/iamcxa/kc-claude-plugins/issues/45)) ([4f8b44c](https://github.com/iamcxa/kc-claude-plugins/commit/4f8b44cfe3df0fde7f2b4ab3f1414561e149e427))

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
