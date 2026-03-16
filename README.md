# kc-claude-plugins

Claude Code plugin marketplace by [Kent Chen](https://github.com/iamcxa).

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
```

## Available Plugins

| Plugin | Version | Description | Install |
|--------|---------|-------------|---------|
| [e2e-pipeline](./e2e-pipeline/) | 2.1.0 | Browser E2E testing pipeline — map UI, generate & verify flows, run tests, interactive walkthroughs, video recording | `/plugin install e2e-pipeline@kc-claude-plugins` |

## e2e-pipeline

Browser E2E testing with context-isolating subagents. The pipeline: **Map → Generate → Verify → Test → Analyze**.

**Prerequisite:** [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally.

### Skills

| Command | Purpose |
|---------|---------|
| `/e2e-map` | Map UI elements → `.claude/e2e/mappings/<app>.yaml` |
| `/e2e-flow --from <plan>` | Generate + verify flow YAML from plan, spec, or PR |
| `/e2e-flow --smoke` | Generate visit-all-pages smoke flow from mapping |
| `/e2e-flow --verify-only <flow>` | Verify existing flow in browser with auto-repair |
| `/e2e-test <flow>` | Run a test flow automatically |
| `/e2e-test <flow> --video` | Run with video recording + MP4 |
| `/e2e-test <flow> --pr <num>` | Run, record, post results to PR |
| `/e2e-walkthrough` | Interactive walkthrough (records video by default) |
| `/e2e-compile --all` | Compile flow YAML to standalone bash scripts for CI |
| `/e2e-dispatch` | Unified entry point (routes to the right skill) |
| `/e2e-skill-ops` | Debug, maintain, or evaluate pipeline skills |

### Architecture

5 agents + 7 skills. Skills run in main conversation as thin orchestrators; agents run as subagents to keep verbose data out of context.

```
User ──→ /e2e-map ──→ e2e-mapper agent ──→ mapping YAML
     ──→ /e2e-flow ──→ e2e-flow-writer agent (codebase analysis, no browser)
                   ──→ e2e-flow-verifier agent (browser verification + auto-repair)
     ──→ /e2e-test ──→ e2e-test-runner agent ──→ e2e-trace-analyzer agent
     ──→ /e2e-walkthrough ──→ (main context, interactive)
     ──→ /e2e-compile ──→ Node.js CLI (no LLM needed, 30-50x faster)
```

### Flow YAML

Write tests in natural language — element names from your mapping, not CSS selectors:

```yaml
name: login-flow
mapping: my-app
steps:
  - id: fill-credentials
    action: "Type 'user@example.com' into email_input on login"
    expect: ["email_input has value 'user@example.com' on login"]

  - id: submit-login
    action: "Click submit_button on login"
    expect: ["url contains /dashboard"]

  # External execution checkpoint (trigger non-browser actions)
  - id: trigger-sync
    action: "Execute external"
    description: "Run data sync CLI"
    execute:
      cli:
        - run: "npx sync-data --env test"
          expect: "exit code 0"
    on_fail: fail

  # External verification checkpoint (check side-effects)
  - id: verify-analytics
    action: "Verify external"
    description: "Confirm PostHog received page_view event"
    wait: 5
    verify:
      posthog:
        - event: page_view
          expect: "count > 0 in last 5 minutes"
    on_fail: warn
```

### CI Integration

Compiled flows run as standalone bash scripts — no Claude Code or LLM needed:

```bash
npx e2e-compile --all                        # compile all flows
.claude/e2e/compiled/login-flow.sh            # run directly
.claude/e2e/compiled/login-flow.sh --junit results.xml  # JUnit output
```

See [CI Integration docs](./e2e-pipeline/docs/ci-integration.md) for GitHub Actions setup.

## Adding to Your Project

Add to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "kc-claude-plugins": {
      "source": {
        "source": "github",
        "repo": "iamcxa/kc-claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "e2e-pipeline@kc-claude-plugins": true
  }
}
```

## License

[MIT](LICENSE)
