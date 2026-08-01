# kc-claude-plugins

Claude Code plugin marketplace by [Kent Chen](https://github.com/iamcxa).

## Install

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
```

## Available Plugins

### [e2e-pipeline](./e2e-pipeline/)

Browser & CLI E2E testing with context-isolating subagents. Map your app's UI, generate test flows from plans, verify in browser with auto-repair, run tests with video recording, record CLI-only flows via terminal recording (asciinema), and verify static UI computed styles via the new declarative `/ui-verify` skill. Codex platform manifest ships alongside Claude Code.

**Use when:** You need automated browser or CLI testing for a web app — from first mapping to CI integration.

**Prerequisite:** [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally.

```bash
/plugin install e2e-pipeline@kc-claude-plugins
```

### [kc-plugin-forge](./kc-plugin-forge/)

One-command plugin quality pipeline. Validates structure, TDD-tests skills under pressure (or via `skill-creator` benchmarking with `--use-skill-creator`), audits SKILL.md frontmatter against the official Claude Code spec (Phase 2.4), smoke-tests skills in clean profile (`--bare` mode, ~$0.025/test), optionally optimizes skill descriptions for trigger reliability (Phase 2.6 via `--optimize-desc`), verifies agent definitions, detects Agent Teams capability, and scaffolds self-improvement (D1/D2 learning) and doc-sync capabilities. Supports `--parallel` mode for concurrent Phase 2/3 execution via teammates. Codex platform manifest ships alongside Claude Code.

**Use when:** You're building or maintaining Claude Code plugins and want automated quality assurance.

**Prerequisites:** `superpowers` + `plugin-dev` marketplace plugins. Optional: `skill-creator` for `--use-skill-creator` and `--optimize-desc` modes.

```bash
/plugin install kc-plugin-forge@kc-claude-plugins
```

### [kc-nightwatch](./kc-nightwatch/)

Autonomous nightly plugin improvement cycle. Runs forge validation, harvests signals from journal/Sentry/E2E/git, and generates improvement proposals aligned to north-star goals.

**Use when:** You want continuous, automated quality monitoring across your plugin ecosystem.

```bash
/plugin install kc-nightwatch@kc-claude-plugins
```

### [kc-hyperfocus](./kc-hyperfocus/)

Session lifecycle & context efficiency. Detects context pressure and enforces cleanup before session end. Cross-session handoff/resume via integrated journal (with vector embedding search via MiniLM). Context Lake (SQLite FTS5) caches codebase insights for faster exploration. MCP context firewall: the `mcp-summarizer` subagent keeps raw payloads from Linear/Sentry/Notion/Supabase/Figma/Slack/Langfuse out of main context, and a PreToolUse nudge proactively suggests it on first read-op per MCP family per session. Includes a standalone statusline with Anthropic 5h/7d usage quota display. Cross-platform install verified by CI matrix (linux-x64, darwin-arm64, darwin-x64) via the new postinstall verify step.

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

### [kc-team-ops](./kc-team-ops/)

Team operations pipeline for engineering managers. EM triage with strategic lens (depth-adaptive routing, team context cache), project pulse updates, codebase exploration, issue decomposition, structured Linear management, and **cross-model second opinion** via Google's agy / Antigravity CLI (`/gemini review|challenge|consult` — same usage as `/codex`, routed through Google's `agy` for a non-OpenAI outside voice; participates in a gstack cross-model review dashboard when gstack is installed).

**Use when:** You're an EM running triage on Linear issues, drafting weekly pulse updates, decomposing oversized issues with team context, or want an independent cross-model review / adversarial challenge / consult from Gemini.

**Prerequisite:** Linear MCP enabled.

```bash
/plugin install kc-team-ops@kc-claude-plugins
```

### [kc-pr-flow](./kc-pr-flow/)

End-to-end PR lifecycle workflow. Create (full ship chain: draft → review → fix → ready → announce), review with tiered multi-agent dispatch (5 `pr-review-toolkit` agents covering correctness, comments, silent failures, type design, and test coverage — plus Trail of Bits security subagents for differential review, supply chain audit, and GitHub Actions security; **optional Codex cross-model second opinion** for bugfix-cross-stack PRs, with **cross-model reconciliation (§5.5) + optional Gemini arbitration (§5.6)** of conflicting findings — Codex runs blind, conflicts are arbitrated in a single Gemini call that adjusts confidence through the existing gate and never auto-posts) and **optional 8-pass mode** for bugfix-cross-layer / cross-stack PRs (forced verdict per review dimension to prevent silent misses). Every finding carries a **1-10 confidence score** — collator gates suppress noise (3-4 demoted to advisory, 1-2 dropped) without losing high-signal recall. Resolve review threads with **cross-AI thread dedup** (groups parallel findings from multiple bots into single issues) AND **cross-review verdict persistence** (suppress prior-dismissed findings across review cycles, most valuable in daemon mode). Pre-scan includes helper-rollout cross-file consistency check (§4.5i) and **doc-claim grounding check** (§4.5j — greps cited subjects to catch forward-looking / ungrounded claims in diffs). Plus commit reorg, Slack announcement, and an automated PR daemon. `kc-pr-create` Step 10a pre-PR self-review uses the same tiering as `kc-pr-review` so self-review is never weaker than post-PR review.

**Use when:** You want a one-command PR workflow that handles creation, review, resolving feedback, and announcements consistently.

**Prerequisite:** `gh` CLI authenticated. Optional: `pr-review-toolkit` (provides the 5 review agents), `feature-dev`, `superpowers` marketplace plugins for graceful enhancement. Optional CLIs: `codex` (cross-model second opinion) and `gemini` (conflict arbitration) — both degrade to a silent skip when absent.

Repository-level [product](./PRODUCT.md) and [architecture](./ARCHITECTURE.md) contracts define the staged agent-native review runtime, its evidence gates, and its authority boundaries.

```bash
/plugin install kc-pr-flow@kc-claude-plugins
```

### [kc-dev-flow](./kc-dev-flow/)

Portable development-flow kernel for Claude Code and Codex. It binds existing
project context, work-item, sprint, execution, delivery, and observation
authorities instead of replacing them. `adopt-dev-flow` audits or upgrades the
binding; `continue-dev-flow` keeps an approved sprint moving through fresh
validation and delivery without unnecessary captain pauses.

**Use when:** You want multiple repositories or agent harnesses to share a lean,
evidence-bound workflow while retaining their local tracker and runtime.

```bash
/plugin install kc-dev-flow@kc-claude-plugins
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
    "kc-hyperfocus@kc-claude-plugins": true,
    "kc-team-ops@kc-claude-plugins": true,
    "kc-pr-flow@kc-claude-plugins": true,
    "kc-dev-flow@kc-claude-plugins": true
  }
}
```

## License

[MIT](LICENSE)
