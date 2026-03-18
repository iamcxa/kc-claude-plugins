# Getting Started

## Install

Via the [kc-claude-plugins](https://github.com/iamcxa/kc-claude-plugins) marketplace:

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
/plugin install e2e-pipeline@kc-claude-plugins
```

## Prerequisites

- [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally
- Node.js 20+ (required for the compiler and quarantine CLI)
- Run `npm install` in the plugin directory (for `/e2e-compile` dependencies)

## Quick Start

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

---

> **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
> **Docs unclear?** Use `/e2e-help --feedback "<description>"` to let us know.
