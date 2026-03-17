# e2e-pipeline

Browser E2E testing pipeline for Claude Code. Maps UI elements, generates and verifies test flows, runs automated tests, and walks through apps interactively — all with context-isolating subagents that keep browser data out of your main conversation.

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
/plugin install e2e-pipeline@kc-claude-plugins
```

**Prerequisite:** [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally.

## Quick Start

```
/e2e-map                    # 1. Map your app's UI → .claude/e2e/mappings/<app>.yaml
/e2e-flow --from <plan>     # 2. Generate + verify flow from plan/spec/PR
/e2e-flow --smoke           # 3. Smoke test all mapped pages
/e2e-test <flow-name>       # 4. Replay a test flow automatically
/e2e-walkthrough            # 5. Walk through interactively (exploration, QA, debug)
/e2e-compile --all          # 6. Compile to standalone bash scripts for CI
```

## The Pipeline

**Map → Generate → Verify → Test → Analyze → Repair → Re-test**

Write tests in natural language — element names from your mapping, not CSS selectors:

```yaml
steps:
  - id: submit-form
    action: Click submit_button on login
    expect: url contains /dashboard
```

When selectors break, re-map the page. When flows change, re-walk. The pipeline self-heals.

## Documentation

| Guide | What it covers |
|-------|---------------|
| [Getting Started](docs/getting-started.md) | Install, prerequisites, quick start walkthrough |
| [Commands](docs/commands.md) | All skills, CLI tools, and flags |
| [Writing Tests](docs/writing-tests.md) | Flow YAML format, mapping, walkthrough-generated flows, handling UI changes |
| [Cross-Boundary Testing](docs/cross-boundary-testing.md) | CLI + browser + analytics flows, `Execute external` / `Verify external` steps |
| [CI Integration](docs/ci-integration.md) | GitHub Actions setup, quarantine system, auth, metrics |
| [Recording & Evidence](docs/recording-evidence.md) | Video, screenshots, traces, PR review evidence |
| [Debugging](docs/debugging.md) | Static/dynamic/intermittent issues, troubleshooting table |
| [Architecture](docs/architecture.md) | Pipeline design, skill→agent model, file structure |

## License

[MIT](LICENSE)
