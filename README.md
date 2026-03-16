# kc-claude-plugins

Claude Code plugin marketplace by [Kent Chen](https://github.com/iamcxa).

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
```

## Available Plugins

| Plugin | Version | Description | Install |
|--------|---------|-------------|---------|
| [e2e-pipeline](./e2e-pipeline/) | 2.0.0 | Browser E2E testing with context-isolating subagents — map UI, generate flows, verify & test, walk through apps, record video | `/plugin install e2e-pipeline@kc-claude-plugins` |

## Usage

After installing a plugin, use its skills directly:

```
/e2e-map                              # Map your app's UI elements
/e2e-test login-flow                  # Run a test flow
/e2e-test login-flow --video          # Run with video recording + MP4
/e2e-test login-flow --pr 940         # Run, record, post results to PR
/e2e-walkthrough                      # Interactive walkthrough (records by default)
/e2e-dispatch                         # Unified entry point
```

## Adding to Your Project

To make this marketplace available to your team, add to `.claude/settings.json`:

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
