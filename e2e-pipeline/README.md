# e2e-pipeline

Browser E2E testing pipeline for Claude Code. Maps UI elements, generates and verifies test flows, runs automated tests, and walks through apps interactively -- all with context-isolating subagents that keep browser data out of your main conversation.

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
/plugin install e2e-pipeline@kc-claude-plugins
```

**Prerequisite:** [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally.

## Quick Start

```
/e2e-map                    # 1. Map your app's UI -> .claude/e2e/mappings/<app>.yaml
/e2e-flow --from <plan>     # 2. Generate + verify flow from plan/spec/PR
/e2e-flow --smoke           # 3. Smoke test all mapped pages
/e2e-test <flow-name>       # 4. Replay a test flow automatically
/e2e-test --suite smoke     # 5. Run a curated test suite
/e2e-test --all-sites       # 6. Run flows across all mapped sites
/e2e-walkthrough            # 7. Walk through interactively (exploration, QA, debug)
/e2e-compile --all          # 8. Compile to standalone bash scripts for CI
/e2e-help                   # 9. Interactive help & topic guide
```

## The Pipeline

**Map -> Generate -> Verify -> Test -> Analyze -> Repair -> Re-test**

Write tests in natural language -- element names from your mapping, not CSS selectors:

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
| [Multi-Site Testing](docs/multi-site-testing.md) | Cross-site flows (`sites:`), `--site`, `--all-sites`, session isolation |
| [Test Suites](docs/suites.md) | Suite file format, site assignment, CI suite patterns |
| [Cross-Boundary Testing](docs/cross-boundary-testing.md) | CLI + browser + analytics flows, `Execute external` / `Verify external` steps |
| [CI Integration](docs/ci-integration.md) | GitHub Actions setup, quarantine system, auth, metrics |
| [Recording & Evidence](docs/recording-evidence.md) | Video, screenshots, traces, PR review evidence |
| [Debugging](docs/debugging.md) | Static/dynamic/intermittent issues, troubleshooting table |
| [Architecture](docs/architecture.md) | Pipeline design, skill->agent model, file structure |
| [Self-Improvement](docs/self-improvement.md) | Knowledge bootstrap, D1/D2 patterns, PR-back flow |

> **New to the pipeline?** Try `/e2e-help` for an interactive guide. Found a gap? `/e2e-help --feedback "<description>"`

## Contributing

Found a gap? Have a better pattern? See [CONTRIBUTING.md](CONTRIBUTING.md) for how to help -- from one-minute feedback to full feature PRs.

## License

[MIT](LICENSE)
