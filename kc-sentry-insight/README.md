# kc-sentry-insight

Scan Sentry for production errors with diff tracking, profile-based domain knowledge, and optional Linear push. Supports Sentry native MCP monitoring (span.op) and keyword-based search.

## Prerequisites

- **Sentry MCP connection** (required): Connected Sentry instance via MCP for error scanning and analysis
- **Linear MCP connection** (optional): For pushing selected issues to Linear as tasks/subtasks

## Command Reference

| Command | Action |
|---------|--------|
| `/kc-sentry-insight <keyword>` | Scan + generate report (auto-bootstrap profile if needed) |
| `/kc-sentry-insight <keyword> --learn` | Scan + emphasize profile iteration proposals |
| `/kc-sentry-insight push <keyword> --issues 1,3,5` | Push selected issues from latest report to Linear |
| `/kc-sentry-insight push <keyword> --issues 1,3 --report 2026-03-18` | Push from a specific historical report |
| `/kc-sentry-insight profiles` | List all profiles for current project |

## Profile Schema

Profile YAML files are stored per-project at `${project}/.claude/insight/sentry/profiles/<keyword>.yaml`.

Each profile captures domain knowledge for a keyword:
- Issue categorization rules
- Known false positives
- Environment-specific patterns
- Custom filters and grouping logic
- Related Linear projects/teams

Profiles are auto-bootstrapped on first scan and can be iteratively refined using the `--learn` flag.

## Data Organization

All plugin data is stored per-project:

```
${project}/.claude/insight/sentry/
├── profiles/              # Domain knowledge profiles per keyword
│   ├── <keyword>.yaml
│   └── ...
└── reports/               # Scan reports organized by keyword
    └── <keyword>/
        └── YYYY-MM-DD.md
```

## Architecture

- **Scanner agent**: Queries Sentry API (MCP) for errors matching keyword or span.op filters
- **Profile manager**: Loads/persists domain knowledge YAML per keyword
- **Report generator**: Creates timestamped reports with diff tracking against previous scans
- **Linear pusher**: Converts selected issues to Linear tasks (optional)

## Getting Started

1. Ensure Sentry MCP is connected: `claude --mcp "sentry" -p "hello"`
2. Run first scan: `/kc-sentry-insight <your-keyword>`
3. Review generated profile and report
4. Optionally push to Linear: `/kc-sentry-insight push <keyword> --issues 1,2,3`
