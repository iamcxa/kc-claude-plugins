# claude-plugins

Claude Code plugin marketplace by [Kent Chen](https://github.com/iamcxa).

## Install

```bash
/plugin marketplace add iamcxa/claude-plugins
```

## Available Plugins

| Plugin | Description | Install |
|--------|-------------|---------|
| [e2e-pipeline](https://github.com/iamcxa/claude-e2e-pipeline) | Browser E2E testing with context-isolating subagents — map UI, run tests, walk through apps, record video | `/plugin install e2e-pipeline@claude-plugins` |

## Usage

After installing a plugin, use its skills directly:

```
/e2e-map                              # Map your app's UI elements
/e2e-test login-flow                  # Run a test flow
/e2e-test login-flow --video          # Run with video recording
/e2e-walkthrough                      # Interactive walkthrough (records by default)
/e2e-dispatch                         # Unified entry point
```

## Adding to Your Project

To make this marketplace available to your team, add to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "claude-plugins": {
      "source": {
        "source": "github",
        "repo": "iamcxa/claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "e2e-pipeline@claude-plugins": true
  }
}
```

## License

[MIT](LICENSE)
