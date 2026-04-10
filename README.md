# kc-claude-plugins

Claude Code plugin marketplace by [Kent Chen](https://github.com/iamcxa).

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
```

## Available Plugins

### [e2e-pipeline](./e2e-pipeline/) `v2.6.0`

Browser & CLI E2E testing with context-isolating subagents. Map your app's UI, generate test flows from plans, verify in browser with auto-repair, run tests with video recording, and record CLI-only flows via terminal recording (asciinema).

**Use when:** You need automated browser or CLI testing for a web app — from first mapping to CI integration.

**Prerequisite:** [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally.

```bash
/plugin install e2e-pipeline@kc-claude-plugins
```

### [kc-plugin-forge](./kc-plugin-forge/) `v1.8.0`

One-command plugin quality pipeline. Validates structure, TDD-tests skills under pressure (or via `skill-creator` benchmarking with `--use-skill-creator`), audits SKILL.md frontmatter against the official Claude Code spec (Phase 2.4), smoke-tests skills in clean profile (`--bare` mode, ~$0.025/test), optionally optimizes skill descriptions for trigger reliability (Phase 2.6 via `--optimize-desc`), verifies agent definitions, detects Agent Teams capability, and scaffolds self-improvement (D1/D2 learning) and doc-sync capabilities. Supports `--parallel` mode for concurrent Phase 2/3 execution via teammates.

**Use when:** You're building or maintaining Claude Code plugins and want automated quality assurance.

**Prerequisites:** `superpowers` + `plugin-dev` marketplace plugins. Optional: `skill-creator` for `--use-skill-creator` and `--optimize-desc` modes.

```bash
/plugin install kc-plugin-forge@kc-claude-plugins
```

### [kc-nightwatch](./kc-nightwatch/) `v0.4.0`

Autonomous nightly plugin improvement cycle. Runs forge validation, harvests signals from journal/Sentry/E2E/git, and generates improvement proposals aligned to north-star goals.

**Use when:** You want continuous, automated quality monitoring across your plugin ecosystem.

```bash
/plugin install kc-nightwatch@kc-claude-plugins
```

### [kc-hyperfocus](./kc-hyperfocus/) `v1.6.0`

Session lifecycle & context efficiency. Detects context pressure and enforces cleanup before session end. Cross-session handoff/resume via integrated journal (with vector embedding search via MiniLM). Context Lake (SQLite FTS5) caches codebase insights for faster exploration. MCP context firewall: the `mcp-summarizer` subagent keeps raw payloads from Linear/Sentry/Notion/Supabase/Figma/Slack/Langfuse out of main context, and a PreToolUse nudge proactively suggests it on first read-op per MCP family per session. Includes a standalone statusline with Anthropic 5h/7d usage quota display.

| Skills | Purpose |
|--------|---------|
| `/kc-session-handoff` | Write journal + produce resume prompt with handoff ID |
| `/kc-session-resume` | Restore context from journal handoff entry (O(1) with ID) |
| `/kc-cache-insight` | Manual cache insight + lake status + metrics view |
| `/kc-statusline-setup` | Install statusline with model, branch, context bar, usage quota |

**Use when:** You want automatic context pressure warnings, enforced session handoff, cross-session context restoration, and codebase insight caching.

**Requires:** `bun` runtime (for Context Lake MCP server and hooks).

```bash
/plugin install kc-hyperfocus@kc-claude-plugins
```

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
    "kc-nightwatch@kc-claude-plugins": true,
    "kc-hyperfocus@kc-claude-plugins": true
  }
}
```

## License

[MIT](LICENSE)
