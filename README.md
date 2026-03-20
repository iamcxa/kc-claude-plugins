# kc-claude-plugins

Claude Code plugin marketplace by [Kent Chen](https://github.com/iamcxa).

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
```

## Available Plugins

| Plugin | Version | Description | Install |
|--------|---------|-------------|---------|
| [e2e-pipeline](./e2e-pipeline/) | 2.3.0 | Browser E2E testing pipeline — map UI, generate & verify flows, run tests, interactive walkthroughs, video recording | `/plugin install e2e-pipeline@kc-claude-plugins` |

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
| `/e2e-help` | Interactive help guide, topic deep-dive, feedback collection |
| `/e2e-doc-sync` | Scan docs for gaps against skills/agents, write updates |
| `/e2e-pipeline-doc-sync` | Full doc sync: static scan + history + write + live probe verify |

### Architecture

8 agents + 10 skills. Skills run in main conversation as thin orchestrators; agents run as subagents to keep verbose data out of context.

```
User ──→ /e2e-map ──→ e2e-mapper agent ──→ mapping YAML
     ──→ /e2e-flow ──→ e2e-flow-writer + e2e-flow-verifier + e2e-trace-analyzer + e2e-media-processor
     ──→ /e2e-test ──→ e2e-test-runner + e2e-trace-analyzer + e2e-media-processor
     ──→ /e2e-walkthrough ──→ (main context) + e2e-trace-analyzer + e2e-media-processor
     ──→ /e2e-compile ──→ Node.js CLI (no LLM needed, 30-50x faster)
     ──→ /e2e-doc-sync ──→ e2e-doc-scanner agent
     ──→ /e2e-pipeline-doc-sync ──→ doc-probe agent (live verification)
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

### Compiled Scripts

`/e2e-compile` transforms flow YAML into standalone bash scripts that call `agent-browser` directly — no Claude Code or LLM needed at runtime. 30-50x faster than LLM-driven execution.

```bash
/e2e-compile login-flow          # compile one flow
/e2e-compile --all               # compile all flows in .claude/e2e/flows/
/e2e-compile --all --coverage    # compile + element coverage report
/e2e-compile --dry-run login-flow  # validate without writing output
```

Output goes to `.claude/e2e/compiled/<flow>.sh`. Each script is self-contained:

```bash
.claude/e2e/compiled/login-flow.sh                      # run directly
.claude/e2e/compiled/login-flow.sh --headed              # visible browser
.claude/e2e/compiled/login-flow.sh --junit results.xml   # JUnit output for CI
.claude/e2e/compiled/login-flow.sh --screenshot-dir ./ss # capture screenshots
```

**Auto-compile**: `/e2e-test` automatically compiles + runs the compiled script after each LLM-driven test and compares results. Divergence between LLM and compiled execution is flagged — this catches selector drift and flow ambiguities early.

### CI Integration

Compiled scripts are the bridge to CI — commit them to your repo and run in GitHub Actions without Claude Code:

```yaml
# .github/workflows/e2e.yml
- run: .claude/e2e/compiled/login-flow.sh --junit results.xml
```

The plugin provides a full GHA template with auth session reuse, matrix parallelism, quarantine system, and JUnit reporting. See [CI Integration docs](./e2e-pipeline/docs/ci-integration.md) for setup.

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
