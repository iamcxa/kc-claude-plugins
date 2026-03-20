# kc-claude-plugins

Claude Code plugin marketplace by [Kent Chen](https://github.com/iamcxa).

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
```

## Available Plugins

| Plugin | Version | Description | Install |
|--------|---------|-------------|---------|
| [e2e-pipeline](./e2e-pipeline/) | 2.3.0 | Browser E2E testing — map UI, generate & verify flows, run tests, walkthroughs, video | `/plugin install e2e-pipeline@kc-claude-plugins` |
| [kc-plugin-forge](./kc-plugin-forge/) | 1.3.0 | Plugin quality pipeline — scaffold, TDD skills, verify agents, doc self-iteration | `/plugin install kc-plugin-forge@kc-claude-plugins` |
| [kc-nightwatch](./kc-nightwatch/) | 0.4.0 | Nightly improvement — forge validation, multi-source signals, proposals & alerts | `/plugin install kc-nightwatch@kc-claude-plugins` |

---

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

### CI Integration

Compiled scripts are the bridge to CI — commit them to your repo and run in GitHub Actions without Claude Code:

```yaml
# .github/workflows/e2e.yml
- run: .claude/e2e/compiled/login-flow.sh --junit results.xml
```

The plugin provides a full GHA template with auth session reuse, matrix parallelism, quarantine system, and JUnit reporting. See [CI Integration docs](./e2e-pipeline/docs/ci-integration.md) for setup.

---

## kc-plugin-forge

One-command plugin development and quality pipeline. Orchestrates marketplace skills to scaffold, TDD-test, validate, and improve Claude Code plugins.

**Prerequisites:** `superpowers` + `plugin-dev` marketplace plugins.

### Skills

| Command | Purpose |
|---------|---------|
| `/kc-plugin-forge <path>` | Full pipeline: validate → TDD → agents → report |
| `/kc-plugin-forge new <name>` | Scaffold a new plugin, then full pipeline |
| `/kc-plugin-forge validate-only` | Phase 1 only — structure check |
| `/kc-plugin-forge skill-tdd-only` | Phase 2 only — TDD cycle per skill |
| `/kc-plugin-forge self-forge` | Forge audits itself (Phase 2 + 4) |
| `/kc-plugin-forge-help` | Interactive guide, topic deep-dive, feedback → issue |

### Pipeline

| Phase | What | Uses |
|-------|------|------|
| 1. Structure | Validate plugin.json, layout, agents | `plugin-dev:plugin-validator` |
| 1.5 Autonomy | Self-Learning (D1/D2) + Doc Self-Iteration | — |
| 2. Skill TDD | RED/GREEN/REFACTOR per skill | `superpowers:writing-skills` |
| 3. Agent Verify | Examples, tools, prompts | `plugin-dev:agent-development` |
| 4. Report | Re-validate + learning capture | `plugin-dev:plugin-validator` |

### Self-Improvement

Lessons accumulate in `reference/learned-patterns.md` (D1, cross-project) and `reference/quality-pipeline.md` (forge-specific gotchas). Phase 1.5 lets you choose the self-improvement level for each plugin you forge.

---

## kc-nightwatch

Autonomous nightly plugin improvement cycle. Runs forge validation, harvests signals from multiple sources, and generates improvement proposals.

### Skills

| Command | Purpose |
|---------|---------|
| `/kc-nightwatch` | Run full pipeline (forge + signals + proposals) |
| `/kc-nightwatch-report` | View last run, compare runs, review proposals |
| `/kc-nightwatch-config` | Configure schedule, Slack channel, target plugins |

### Signal Sources

4 scanner agents harvest signals in parallel:

| Agent | Source | Finds |
|-------|--------|-------|
| signal-harvester | Journal + episodic memory + MEMORY.md | Past insights, user feedback |
| sentry-scanner | Sentry MCP | Production errors, regressions |
| e2e-scanner | E2E test reports | Failure trends, coverage gaps |
| git-scanner | Git history | Churn hotspots, stale code |

---

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
    "e2e-pipeline@kc-claude-plugins": true,
    "kc-plugin-forge@kc-claude-plugins": true,
    "kc-nightwatch@kc-claude-plugins": true
  }
}
```

## License

[MIT](LICENSE)
