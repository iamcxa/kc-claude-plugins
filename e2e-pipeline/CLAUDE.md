# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin (`e2e-pipeline`) that automates browser E2E testing via context-isolating subagents. The pipeline: **Map UI** -> **Generate Flows** -> **Verify & Test** -> **Analyze**.

## Architecture

**Skills** (11) run in main conversation context as thin orchestrators. They handle pre-flight checks, codebase analysis, user interaction, and media post-processing.

**Agents** (8) run as subagents for heavy work, keeping verbose data out of main context:
- `e2e-mapper` -- explores pages, generates YAML mappings
- `e2e-flow-writer` -- analyzes codebase + mapping to generate flow YAML (no browser)
- `e2e-flow-verifier` -- runs flows in browser, auto-repairs selectors/steps, produces reports
- `e2e-test-runner` -- executes flow files, validates expectations
- `e2e-trace-analyzer` -- analyzes Playwright ZIP API/console evidence or bounded Chrome Trace JSON performance evidence
- `e2e-media-processor` -- blank-frame-trimmed GIF, MP4 video, thumbnail from screenshots/recordings
- `doc-probe` -- verifies documentation accuracy via live behavioral probes (dispatched by e2e-doc-sync)
- `e2e-debug-observe` -- executes reproduction steps in browser, collects [E2E-DBG] console logs for debug pipeline. Supports **Teams mode**: persistent browser session across hypothesis-verify rounds (requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)

```
skills/e2e-dispatch/     -> router (auth gate + skill selection)
skills/e2e-map/          -> mapping orchestrator -> dispatches e2e-mapper agent
skills/e2e-test/         -> test orchestrator -> dispatches e2e-test-runner + trace-analyzer
skills/e2e-walkthrough/  -> interactive exploration (main context)
skills/e2e-flow/         -> generate & verify flows -> dispatches flow-writer + flow-verifier + trace-analyzer
skills/e2e-compile/      -> compile flow YAML to standalone bash test scripts (requires npm deps)
skills/e2e-skill-ops/    -> meta-skill for debugging/maintaining the pipeline itself
skills/e2e-help/         -> interactive help guide, topic deep-dive, feedback collection
skills/e2e-doc-sync/     -> doc sync: diff-aware scan + history enrichment + write + live probe verification
skills/e2e-debug/        -> debug orchestrator: inject logs → dispatch e2e-debug-observe → diagnose → cleanup (Teams mode: persistent observer)
skills/ui-verify/        -> static UI computed-style verification (declarative YAML, deterministic Node runner)
agents/                  -> subagent definitions (e2e-mapper, e2e-flow-writer, e2e-flow-verifier, e2e-test-runner, e2e-trace-analyzer, e2e-media-processor, doc-probe, e2e-debug-observe)
hooks/                   -> E2E pipeline hooks (SessionStart context + pre-commit check + plan E2E check)
references/              -> agent-browser CLI commands, common browser testing patterns, knowledge capture framework
```

## Self-Improvement

6 of 8 core skills accumulate knowledge after execution via a two-dimension framework (`references/knowledge-capture.md`):

| Skill | D1 (skill-level) | D2 (project-level) |
|-------|-------------------|---------------------|
| e2e-test | Auto-append to `learned-patterns.md` | Gated write to `.claude/e2e-lessons.md` |
| e2e-skill-ops | Auto-append to `learned-patterns.md` | Gated write (--evaluate mode only) |
| e2e-flow | Auto-append to `learned-patterns.md` | -- |
| e2e-walkthrough | Auto-append to `learned-patterns.md` | -- |
| e2e-map | Auto-append to `learned-patterns.md` | -- |
| e2e-debug | Auto-append to `learned-patterns.md` | -- |
| e2e-compile | -- (deterministic) | -- |
| e2e-dispatch | -- (router) | -- |

**D1** = cross-project patterns (selector strategies, framework behaviors, agent-browser gotchas). Auto-append, no gate.
**D2** = project-specific patterns (timing, auth, data dependencies). Severity gate + three-question test + user confirmation.

All skills read `learned-patterns.md` at startup (Knowledge Bootstrap phase). D2-capable skills also read `.claude/e2e-lessons.md`.

PR-back flow: users curate local `learned-patterns.md` -> PR to plugin origin -> all users benefit.

## Data Flow

```
/e2e-map           -> .claude/e2e/mappings/<app>.yaml
/e2e-walkthrough   -> .claude/e2e/flows/walkthrough-*.yaml + .claude/e2e/reports/<ts>/flow-report.md
/e2e-flow          -> .claude/e2e/flows/<feature>.yaml + .claude/e2e/reports/<ts>/report.md
/e2e-test <flow>   -> .claude/e2e/reports/<ts>/report.md, detected trace artifact, screenshots, video
/e2e-compile       -> .claude/e2e/compiled/<flow>.sh (standalone bash test scripts)
/e2e-debug         -> .claude/e2e/debug/manifest.yaml, report.md, history/<session>-r<N>.yaml
```

## YAML Format Conventions (v2 only)

**Mapping files** -- page names in `kebab-case`, element names in `snake_case`:
```yaml
version: 2
app: <name>
base_url: <url>
pages:
  <kebab-case-page>:
    url_pattern: "/path"
    elements:
      <snake_case_element>:
        selector: '[data-testid="value"]'
        description: "..."
```

**Flow files** -- use `mapping:` (not `app:`), steps use `id:` (not `name:`):
```yaml
name: <flow-name>
mapping: <app-name>
steps:
  - id: <step-id>
    action: "Click <element> on <page>"
    expect: ["<element> visible on <page>"]
```

Flow files may also include an optional `preconditions:` block for data readiness checks (see `references/common-patterns.md`).

Using `app:` or `name:` in steps means v1 format -- rejected by the test runner.

## Selector Priority

**This is the single authority for mapping `selector:` grammar.** Other files
must not restate this table — point back here instead. Enforcement lives in
`compiler/lib/selector-policy.js` (the banned-class table), which both
`scripts/lint-mapping.sh` and the compiler read, and `compiler/lib/selector-translate.js`
(how each form is consumed). The compiler **blocks** at compile and dry-run time on a
banned selector the flow resolves, and warns on the rest of the mapping file; pre-existing
violations go in a baseline the compile path only ever opens for reading — the
enforcement point for that being true is the byte-compare in
`compiler/test/selector-gate.test.js` (AC-4), not the wording here
(`docs/ci-integration.md`).
One banned-class table, two traversals — the enforcement point for that being true of the
linter is `compiler/test/selector-lint-drift.test.js`, not a convention.

**`selector:` is a plugin-internal locator DSL, not a raw CLI argument you hand
to `agent-browser`.** Mapped `expect:` visibility resolves an effective DOM
selector and uses `compiler/lib/visibility-probe.js`: `css_selector` when
present, otherwise `selector` only when it is literal CSS. Non-CSS locator DSL
without `css_selector` fails before browser execution. Literal text assertions
remain accessibility snapshot checks; they are not mapped selector visibility.
`click`/`fill` actions are a separate path: the raw `selector:` value **is** passed to
`agent-browser click|fill` as a literal argument there (unless the element also
declares `css_selector:`, see below), so its syntax must actually resolve on
that path. Measured three months post-launch: the CSS-attribute form
(`[role="<r>"][aria-label="<v>"]`) was emitted 0 times across 32 real mapping
files against a banned-but-actually-fine `role=<r>[name="<v>"]` emitted 2,183
times, because `aria-label` is only present on ~2.8% of components in the
primary target app — the CSS form requires literal attributes the DOM mostly
doesn't have. Full record: `docs/dev/.spacedock-state/e2e-selector-canon-review.md`.

1. `[data-testid="value"]` -- best stability, explicit test anchor
2. `role=<r>[name="<v>"]` -- primary form for elements without a test ID. Matches
   the *computed* accessible name and *implicit* role exactly as the mapper
   observes them in the a11y snapshot (e.g., `role=button[name="Save"]`).
   **Forms 2 and 3 are non-CSS locator DSL.** Handed to
   `agent-browser click|fill` literally they return `false`/not-found, because
   agent-browser drives CDP and does not implement Playwright's selector engines.
   Probed live against agent-browser 0.32.0 + Chrome for Testing on a fixture
   whose snapshot showed the element: `is visible 'role=button[name="AlphaBtn"]'`
   and `is visible 'text=AlphaBtn'` both returned `false`, while
   `[role="button"][aria-label="通知"]` and `h1` returned `true`. So an element
   these forms locate and a step **clicks, fills, or asserts mapped visibility**
   needs `css_selector:` (below). Without it the resolver fails loud with the
   mapping path, page, element, and remediation.
   The regex variant `role=<r>[name=/<re>/]` is **accepted**: it translates to the
   literal prefix of `<re>` before the first regex metacharacter. That prefix is a
   substring match, so an over-short prefix can match a longer unintended string
   (`/holder.*X/` -> `holder`, which matches inside `placeholder`) — hazard tracked
   by the `e2e-regex-prefix-false-match` entity, not fixed here.
3. `text=<v>` -- role-agnostic text match, for elements with no stable role.
   It also requires `css_selector` for mapped visibility. A trailing
   ` >> nth=N` chord is banned by `compiler/lib/selector-policy.js`. The regex
   variant `text=/<re>/` has no fixed DOM identity and must not be approximated.
4. `[role="<r>"][aria-label="<v>"]` -- secondary form. Use ONLY when the
   component genuinely carries a literal `aria-label` attribute (rare — verify,
   don't assume). Not a default output.
5. `[role="<r>"]` -- role only; combine with `:nth-of-type(N)` if repeated
6. `[aria-label="<v>"]` -- when role isn't stable
7. Never use `has-text()` -- broken in agent-browser, causes timeout (BANNED — see `compiler/lib/selector-policy.js`)
8. BANNED: ` >> nth=N` Playwright nth chord -> use `:nth-of-type(N)` CSS pseudo (BANNED — see `compiler/lib/selector-policy.js`)
9. DEPRECATED as a `selector:` value: `find role|text|testid|label <r> [--name "<v>"]` -- this is an
   agent-browser CLI subcommand chain, not selector grammar (BANNED — see `compiler/lib/selector-policy.js` CLASS 5).
   Valid only as an interactive CLI command during exploration, never as a stored `selector:` value.

**`css_selector:`** -- optional element field, a literal CSS selector distinct
from `selector:`. It is the DOM identity authority for mapped visibility and is used for an eval-based
`querySelector().click()` on `click` steps (more reliable than `agent-browser
click` in headless CI) and **required** for `value: {runtime_ref: ...}`
sensitive fills (SC-1032) — the secret is written via `querySelector`, never
argv. Must be valid CSS (it is never translated).

**`visibility_policy:`** -- optional `strict` or `retained-zero-rect`; absence
means `strict`. Strict requires one raw DOM match and one nonzero-layout-visible
candidate. The exception is eligible only when exactly one candidate is
nonzero-layout-visible and every extra candidate is style-visible with no
positive-area client rect. Mapper/verifier may propose the exception with
evidence but never auto-apply it. `invalid_selector`, `probe_error`,
`raw_multi_match`, and `multiple_rendered` are terminal for positive and
negative assertions. Reports retain the result class, effective selector and
policy, counts/aggregates, attempts/elapsed, and bounded candidate evidence.

## Key Gotchas

- **`e2e-flow-writer` has no Bash tool**: intentional -- it does pure codebase analysis, never opens a browser. Adding Bash would break isolation.
- **`@ref` is ephemeral**: snapshot `@ref` values change on every DOM mutation. Mappings store stable selectors, not `@ref`.
- **Raw `is visible` is diagnostic only**: it checks the first DOM match, always exits 0, and collapses invalid CSS into `false`. Product assertions use the shared judge protocol.
- **React Native Web**: text elements render twice. Use `:nth-of-type(2)` CSS pseudo, `role=<r>[name="<v>"]`, or `text=<v>` — all match the computed accessible name once. `>> nth=N` is BANNED regardless of prefix (see `e2e-pipeline/compiler/lib/selector-policy.js`).
- **Ant Design CSS-hidden inputs**: map/probe the rendered control identity instead of substituting accessibility text for mapped visibility.
- **Snapshot doesn't expose `data-testid`/`aria-label`**: use `css_selector` with the shared deterministic visibility probe for mapped verification.
- **Don't pass-through what you can execute**: If an agent has the tools to attempt a step (e.g., verifier has Bash -> can run CLI commands), it should attempt it best-effort rather than blindly skipping. Silent skip = the user discovers broken commands only at execution time, not verification time. External checkpoint failures in the verifier use `on_fail: warn` override so they never block browser verification.
- **Headless CI: snapshot works, actionability differs**: mapped visibility uses the shared DOM classifier through an `eval` IIFE; literal text stays snapshot-based. `nativeInputValueSetter` and `querySelector.click()` remain the fill/click workarounds.
- **Ant Design `Input.Password` drops `name` attribute**: `Input.Password` doesn't pass `name` to the inner `<input>`. Use `input[type="password"]` selector instead of `input[name="password"]`.
- **`agent-browser eval` shares global scope**: Consecutive `eval` calls share the same JS global scope. Redeclaring `const`/`let` causes SyntaxError. Wrap each eval in an IIFE: `(()=>{...})()`.

## Editing Skills and Agents

When modifying skill or agent definitions:
- Skills have a main `SKILL.md` and optional `reference.md` for detailed mechanics
- Cross-reference step numbers between `SKILL.md` (summary) and `reference.md` (details)
- Run the **e2e-skill-ops 5 rules**: search before diagnose, 3-skill impact scan, verify after fix, write back findings, propose (don't ship) SKILL.md changes without review
- Quality findings persist in `.claude/e2e/reports/skill-quality-findings.md`

**Adding or changing action types (e.g., new `action:` value in flow YAML):**
Trace the full chain and update EVERY layer. No layer may be skipped:

| Layer | File | Question |
|-------|------|----------|
| Generator | `agents/e2e-flow-writer.md` | Can it produce the new action type? |
| Verifier | `agents/e2e-flow-verifier.md` | Can it attempt execution (not just skip)? Check available tools. |
| Test-runner | `agents/e2e-test-runner.md` | Can it execute at full fidelity? |
| Compiler | `bin/e2e-compile.js` | Does it handle or explicitly SKIP the type? |
| Skill | `skills/e2e-flow/SKILL.md` | Does the result summary show the new type's output? |
| Reference | `references/common-patterns.md` | Are execution patterns documented? |
| CLAUDE.md | `CLAUDE.md` draft flow template | Is the new type in the example? |

Rule: if a layer has the tools to attempt a step, it MUST attempt it (best-effort). "Skip because another layer handles it" is only valid when the layer genuinely lacks the capability.

Runtime-state compiler actions follow the same chain. Keep `runtime_values` environment-backed,
use typed `runtime_ref` edges, require exact-one `capture-url-query`, and run ordered `finally`
HTTP cancellation/readback before metrics and JUnit emission. Finalizer failure is lane failure.

**Removing a skill or agent:**
1. Delete the directory/file
2. Run: `grep -rn "<name>" e2e-pipeline/ --include="*.md" --include="*.json" --include="*.sh" | grep -v skill-quality-findings | grep -v node_modules | grep -v docs/superpowers/`
3. Update every hit -- replace with successor or remove
4. Update `skills/e2e-dispatch/SKILL.md` routing table + reroute removed flags to successor
5. Re-run grep to verify zero active references (historical in findings/specs is OK)

## Soft Dependencies

- **`e2e-debug` -> `systematic-debugging`** (superpowers plugin): Phase 0 Path B invokes `Skill("systematic-debugging")` for hypothesis generation when bug description is vague. Graceful fallback: if unavailable, best-effort grep + user confirmation. Debug skill works fully without it.
- **`e2e-debug` -> `feature-dev:code-explorer`** (feature-dev plugin): Phase 0 Path A dispatches `code-explorer` agent for codebase tracing when the bug description is clear (maps architecture layers, data flow, dependencies). Graceful fallback: if unavailable, grep + direct file reads. Debug skill works fully without it.
- **Agent Teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`): Skills with browser agents can spawn persistent teammates instead of one-shot subagents. Shared protocol in `references/agent-teams.md`. Currently supported: `e2e-debug` (persistent observer for hypothesis loop), `e2e-test` (multi-role parallel + cross-site coordination). Graceful fallback to subagent mode when Teams unavailable. Use `--no-teams` to force subagent mode.

## Documentation Maintenance

### Doc Sync

`/e2e-doc-sync` is the unified doc sync skill combining diff-aware scanning, history enrichment, doc writing, and live probe verification. The `doc-probe` agent handles behavioral verification.

### Pre-Publish Gate (before the feature PR is ready)

**Before syncing this plugin to the marketplace, the following gate MUST pass:**

1. Run `/e2e-doc-sync --check` -- reports gaps between skills/agents and docs
2. If gaps found -> run `/e2e-doc-sync --fix` to resolve, or acknowledge as intentional
3. Only mark the feature PR ready after docs are in sync; release-please owns
   the later version and marketplace propagation

This gate exists because SKILL.md definitions are authoritative but not user-facing. Publishing a version where docs lag behind skills means users can't discover features.

### Manual Checklist

When adding, removing, or renaming skills or agents, update these files:

1. `README.md` -- quick start commands, pipeline summary, docs table
2. `docs/commands.md` -- command table with all flags
3. `docs/architecture.md` -- skill->agent table and plugin file tree
4. `docs/getting-started.md` -- step-by-step guide
5. `docs/writing-tests.md` and `docs/recording-evidence.md` -- check for stale references
5b. `docs/multi-site-testing.md` and `docs/suites.md` -- cross-site and suite features
5c. `references/common-patterns.md` -- external checkpoint patterns, combined flow examples
6. `.claude-plugin/plugin.json` -- bump version
7. `CLAUDE.md` (this file) -- Architecture section counts, directory listing, Recording Defaults table

**Prefer `/e2e-doc-sync --fix` over the manual checklist** -- it scans the same items automatically and catches gaps the checklist misses (e.g., new flags added to an existing skill).

## Video Defaults

Video is generated from step screenshots by the `e2e-media-processor` agent — no simultaneous browser recording needed. Each step gets 2 seconds in the MP4.

| Skill | Video Default | Override |
|-------|--------------|----------|
| `/e2e-walkthrough` | ON | `--no-video` |
| `/e2e-flow --verify-only` | ON | `--no-video` |
| `/e2e-test` | OFF | `--video` or `--pr` |
| CLI-only flows | ON (asciinema) | `--no-video` |
| `/e2e-map` | No video | -- |

All media post-processing (GIF, MP4, thumbnail) is handled by the `e2e-media-processor` agent, dispatched by each skill after browser work completes. Browser agents produce step screenshots plus the capability-detected trace artifact (`trace.json` for Chrome Trace Event JSON or `trace.zip` for a Playwright archive). `record start/stop` is no longer used — it caused instability when running alongside trace.

## Planning Integration (E2E-First Acceptance)

Enforced by four layers -- any planning framework (superpowers, GSD, plan mode, or bare conversation) is covered:

| Layer | Mechanism | When | Strength |
|-------|-----------|------|----------|
| **Upstream** | SessionStart hook | Every session in a project with mappings | Injects reminder into context |
| **Plan gate** | PostToolUse hook on Write | Plan file written in E2E-enabled project | Warns if plan has no E2E steps |
| **Bridge** | `/e2e-flow` skill | During or after planning | Generates structured flow YAML from plan/spec/PR |
| **Downstream** | PreToolUse hook on `git commit` | Every commit in a project with mappings | Warns if no recent E2E report |

**Closed loop:**
```
SessionStart --> "E2E infrastructure detected, use /e2e-flow"
     |
     v
Planning (any framework)
     |
     v
Write plan --> hook checks --> "Plan has no E2E steps!" (if missing)
     |
     v
/e2e-flow --from <plan>  -->  .claude/e2e/flows/<feature>.yaml
     |                         (generates + verifies in browser)
     v
/e2e-test <feature>  -->  .claude/e2e/reports/*/report.md
     |                                    ^
     v                                    | (no flow? create one first)
git commit  -->  hook checks      /e2e-flow --from <plan>
                                         +-> generates flow -> verifies -> future /e2e-test
```

**Worktree E2E**: When working in a git worktree, the dev server typically runs from the main repo, not the worktree. E2E tests need a running server. Options: (1) start dev server from the worktree, (2) merge to main first and run E2E from the main repo. Plan accordingly -- don't defer E2E without noting this constraint.

**Verification decision**: Draft flow exists -> `/e2e-test` (automated, subagent). No flow -> `/e2e-flow --from <plan>` (generates + verifies automatically). For interactive exploration -> `/e2e-walkthrough`.

**Draft flow template** (for plans that embed acceptance criteria inline):

```yaml
# draft -- validate against mapping before use
name: <feature-name>
description: "<what this verifies>"
tags: [acceptance, <feature-tag>]
mapping: <app-name>                    # must match an existing mapping

steps:
  - id: navigate-to-feature
    action: "Navigate to <path>"
    expect:
      - "<key_element> visible on <page>"

  - id: perform-action
    action: "Click <element> on <page>"
    expect:
      - "url contains <expected-path>"
      - "text '<success message>' on <page>"

  # Optional: external execution checkpoint (trigger non-browser actions)
  - id: trigger-side-effect
    action: "Execute external"
    description: "Run <command> to <purpose>"
    execute:
      cli:
        - run: "<command>"
          expect: "exit code 0"
    wait_after: 5
    on_fail: fail

  # Optional: external verification checkpoint (check side-effects)
  - id: verify-side-effect
    action: "Verify external"
    description: "Confirm <service> received the expected event"
    wait: 5
    verify:
      <service>:
        - event: <event_name>
          expect: "count > 0 in last 5 minutes"
    on_fail: warn
```

**Rules for draft flows:**
- Element/page names MUST match the mapping exactly (`snake_case` elements, `kebab-case` pages)
- 5-12 steps -- focused acceptance path, not exhaustive coverage
- Every step needs `expect:` -- bare navigation is insufficient for acceptance
- `Execute external` for triggering non-browser actions (CLI, API, scripts)
- `Verify external` for checking external service side-effects
- External checkpoints only at real integration boundaries
- Use `/e2e-flow --from <plan>` to generate from plan; manual embedding is fallback

## Compiler Dependencies

The `/e2e-compile` skill uses a Node.js CLI (`bin/e2e-compile.js`) that requires npm packages. Run `npm install` in the plugin directory if `node_modules/` is missing. Dependencies are declared in `package.json`.

## Plugin Runtime Variable

`${CLAUDE_PLUGIN_ROOT}` is set by Claude Code at session start to the plugin's installation directory. Skills and hooks use this to resolve paths to `references/`, `hooks/scripts/`, and `bin/`. It is only available within the plugin context (skills, agents, hooks) -- not in user code.

## Git Conventions

Semantic commit prefixes: `feat`, `fix`, `docs`, `chore`. Do not bump plugin or
marketplace versions in a feature PR; root release-please configuration owns
version propagation and publishing. After its Release PR merges, use
`kc-plugin-forge:kc-plugin-release` for local Claude Code and Codex install
synchronization.
