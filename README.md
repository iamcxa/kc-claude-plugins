# kc-claude-plugins

Claude Code plugin marketplace by [Kent Chen](https://github.com/iamcxa).

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
```

## Available Plugins

### [e2e-pipeline](./e2e-pipeline/) `v2.4.0`

Browser & CLI E2E testing with context-isolating subagents. Map your app's UI, generate test flows from plans, verify in browser with auto-repair, run tests with video recording, and record CLI-only flows via terminal recording (asciinema).

**Use when:** You need automated browser or CLI testing for a web app — from first mapping to CI integration.

**Prerequisite:** [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally.

```bash
/plugin install e2e-pipeline@kc-claude-plugins
```

### [kc-plugin-forge](./kc-plugin-forge/) `v1.3.0`

One-command plugin quality pipeline. Validates structure, TDD-tests skills under pressure, verifies agent definitions, and scaffolds self-improvement (D1/D2 learning) and doc-sync capabilities into your plugins.

**Use when:** You're building or maintaining Claude Code plugins and want automated quality assurance.

**Prerequisites:** `superpowers` + `plugin-dev` marketplace plugins.

```bash
/plugin install kc-plugin-forge@kc-claude-plugins
```

### [kc-nightwatch](./kc-nightwatch/) `v0.4.0`

Autonomous nightly plugin improvement cycle. Runs forge validation, harvests signals from journal/Sentry/E2E/git, and generates improvement proposals aligned to north-star goals.

**Use when:** You want continuous, automated quality monitoring across your plugin ecosystem.

```bash
/plugin install kc-nightwatch@kc-claude-plugins
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
    "kc-nightwatch@kc-claude-plugins": true
  }
}
```

## License

[MIT](LICENSE)
