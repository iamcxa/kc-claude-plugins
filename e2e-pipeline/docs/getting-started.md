# Getting Started

## Install

Via the [kc-claude-plugins](https://github.com/iamcxa/kc-claude-plugins) marketplace:

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
/plugin install e2e-pipeline@kc-claude-plugins
```

## Prerequisites

- [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally
  (`npm install -g agent-browser`). A peer CLI, not an npm dependency of this plugin —
  `npm install` below does not provide it. `E2E_AGENT_BROWSER_BIN` overrides the lookup
  when the executable is not on `PATH`.
- Node.js 20+ (required for the compiler and quarantine CLI)
- Run `npm install` in the plugin directory (for `/e2e-compile` dependencies)
- `zip` on `PATH` to run the test suite (trace archive validation shells out to it;
  present on macOS and on GitHub's `ubuntu-latest`, absent from a bare `node` container)
- For CLI-only flow recording: `brew install asciinema agg` (optional)

## Quick Start

> **No browser app? Testing a CLI tool or backend service?**
> Skip steps 1-2. Run `/e2e-flow` directly — the skill auto-detects CLI-only intent
> when no mapping exists and your source material contains CLI/API signals
> (shell commands, API calls, migration scripts). The resulting flow records via
> `asciinema` instead of browser screenshots. See
> [Cross-Boundary Testing: CLI-Only Flows](cross-boundary-testing.md#cli-only-flows-no-mapping-required)
> for details, including `asciinema` and `agg` prerequisites.

### 1. Map your app's UI

```
/e2e-map
```

Creates a YAML mapping of pages, elements, and selectors in `.claude/e2e/mappings/<app>.yaml`.

### 2. Generate a flow from a plan or spec

```
/e2e-flow --from <plan.md>
```

Analyzes your codebase and mapping to generate a flow YAML, then verifies it in a real browser with auto-repair.

### 3. Smoke test all mapped pages

```
/e2e-flow --smoke
```

Generates and runs a visit-all-pages flow from the mapping -- quick sanity check after changes.

### 4. Run a test flow

```
/e2e-test <flow-name>
/e2e-test <flow-name> --video        # with screen recording
/e2e-test <flow-name> --pr 940       # record + post results to PR
```

Replays a flow file from `.claude/e2e/flows/` against the mapped UI. Use `--video` for recording or `--pr` to post evidence directly to a pull request (see [PR Workflow](pr-workflow.md)).

Flows can include [preconditions](writing-tests.md#preconditions) that validate data readiness (e.g., database records exist) before the browser launches.

### 5. Walk through interactively

```
/e2e-walkthrough
```

Human-guided browser exploration for visual QA, debugging, or demo recording.

### 6. Compile for CI

```
/e2e-compile --all
```

Compiles all flow YAML files to standalone bash scripts in `.claude/e2e/compiled/`, ready for headless CI execution without Claude Code.

## Related

- [Commands](commands.md) -- all skills, CLI tools, and flags
- [Writing Tests](writing-tests.md) -- flow YAML format, preconditions, cross-site flows
- [Recording & Evidence](recording-evidence.md) -- video recording, screenshots, trace replay
- [PR Workflow](pr-workflow.md) -- posting E2E evidence to pull requests
- [Suites](suites.md) -- organizing tests into named suites
- [Debugging](debugging.md) -- troubleshooting test failures by type
- [Cross-Boundary Testing](cross-boundary-testing.md) -- CLI-only flows, mixed browser + CLI tests

---

> **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
> **Docs unclear?** Use `/e2e-help --feedback "<description>"` to let us know.
