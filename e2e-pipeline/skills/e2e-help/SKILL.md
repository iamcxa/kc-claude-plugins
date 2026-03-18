---
name: e2e-help
description: Use when users need help with E2E pipeline commands, want to discover available skills, or report documentation gaps. Triggers on "e2e help", "how do I e2e", "what e2e commands", "e2e-help", "help with e2e testing", "what can e2e do", "e2e pipeline help".
---

# E2E Help — Interactive Pipeline Guide

Help users discover, understand, and improve the E2E testing pipeline.

## Invocation

```
/e2e-help                            # Overview of all commands
/e2e-help <topic>                    # Deep dive into a topic
/e2e-help --feedback "<message>"     # Report a doc gap or feature request
/e2e-help --list-topics              # Show available help topics
```

## Phase 1 — Parse Args

| Arg | Mode |
|-----|------|
| *(none)* or `--list-topics` | Overview |
| `<topic>` | Topic deep dive |
| `--feedback "<message>"` | Feedback collection |

## Phase 2 — Overview Mode (no args)

Present a complete command reference by reading live skill data:

```
Read → ${CLAUDE_PLUGIN_ROOT}/skills/*/SKILL.md  (extract name + description from frontmatter)
Read → ${CLAUDE_PLUGIN_ROOT}/docs/*.md           (extract filenames for topic mapping)
```

Present:

```markdown
# E2E Pipeline — Quick Reference

## Commands

| Command | What it does |
|---------|-------------|
| `/e2e-map` | Map your app's UI elements → YAML mapping |
| `/e2e-test <flow>` | Run a test flow against mapped UI |
| `/e2e-test --suite <name>` | Run a curated suite of flows |
| `/e2e-test --all-sites` | Auto-discover sites and run flows |
| `/e2e-test --tag smoke` | Run all flows tagged with `smoke` |
| `/e2e-flow --from <plan>` | Generate + verify flow from a plan/spec |
| `/e2e-flow --smoke` | Generate visit-all-pages smoke flow |
| `/e2e-flow --verify-only <flow>` | Verify existing flow with auto-repair |
| `/e2e-walkthrough` | Interactive browser exploration |
| `/e2e-compile --all` | Compile flows to standalone CI scripts |
| `/e2e-dispatch` | Unified entry point (routes to right skill) |
| `/e2e-doc-sync` | Scan and update documentation gaps |
| `/e2e-skill-ops` | Debug, maintain, or evaluate pipeline skills |
| `/e2e-help` | This help screen |

## Topics (use `/e2e-help <topic>` for details)

| Topic | Covers |
|-------|--------|
| `getting-started` | Install, prerequisites, first test |
| `writing-tests` | Flow YAML format, element names, expectations |
| `cross-site` | Testing across multiple apps (sites:, --site, --all-sites) |
| `suites` | Grouping flows into test suites |
| `checkpoints` | Execute external + Verify external steps |
| `recording` | Video, screenshots, traces, PR evidence |
| `ci` | GitHub Actions, quarantine, compiled scripts |
| `debugging` | Troubleshooting test failures |
| `architecture` | Pipeline design, skill→agent model |
| `commands` | All flags and CLI options |

## Quick Start

**First time?**
1. `/e2e-map` → map your app
2. `/e2e-flow --smoke` → generate a smoke test
3. `/e2e-test smoke-navigation` → run it

**From a plan?**
`/e2e-flow --from plan.md` → generates + verifies automatically

**Multiple apps?**
`/e2e-test --all-sites` → runs on every mapped site

**Curated test set?**
`/e2e-test --suite regression` → runs a defined playlist
```

Always end with:

```
---
Missing something? `/e2e-help --feedback "<description>"` to report a gap.
Full docs: ${CLAUDE_PLUGIN_ROOT}/docs/
```

## Phase 3 — Topic Deep Dive

Map topic names to doc files:

| Topic keyword(s) | Doc file |
|-------------------|----------|
| `getting-started`, `install`, `setup` | `docs/getting-started.md` |
| `writing-tests`, `flow-format`, `yaml` | `docs/writing-tests.md` |
| `cross-site`, `multi-site`, `sites` | `docs/multi-site-testing.md` |
| `suites`, `suite` | `docs/suites.md` |
| `checkpoints`, `external`, `verify-external`, `execute-external` | `docs/cross-boundary-testing.md` |
| `recording`, `video`, `evidence` | `docs/recording-evidence.md` |
| `ci`, `github-actions`, `compiled` | `docs/ci-integration.md` |
| `debugging`, `troubleshoot`, `fix` | `docs/debugging.md` |
| `architecture`, `design`, `agents` | `docs/architecture.md` |
| `commands`, `flags`, `options` | `docs/commands.md` |

1. Resolve topic keyword → doc file: `${CLAUDE_PLUGIN_ROOT}/<doc-file>`
2. Read the doc file
3. Present content with a summary header

If topic not found:
```
Topic "<topic>" not recognized.
Available: getting-started, writing-tests, cross-site, suites, checkpoints, recording, ci, debugging, architecture, commands
```

After presenting, always append:
```
---
> Want more detail? Full doc at `<doc-file>`.
> Found a gap? `/e2e-help --feedback "<what's missing>"`
> Know a better pattern? PRs welcome: https://github.com/iamcxa/kc-claude-plugins
```

### Gap Detection

If answering the user's question required reading a SKILL.md or agent definition (not a doc file), note this:

```
💡 This answer came from internal skill definitions, not user docs.
This suggests a documentation gap. Want me to:
1. Add a section to the relevant doc? (I'll draft for your review)
2. Create a tracking issue?
3. Skip — one-off question
```

## Phase 4 — Feedback Mode

When `--feedback "<message>"` is provided:

1. Read the message
2. Classify: **doc-gap** (missing/unclear docs), **feature-request** (new capability), or **bug** (broken behavior)
3. Present proposed action:

```markdown
## Feedback: <type>

**Message**: "<user message>"

### Proposed GitHub Issue

**Title**: [<type>] <summary>
**Body**: <details with context>
**Labels**: documentation, e2e-pipeline (or enhancement, bug)

Create this issue? (y/n/edit)
```

4. On confirmation, attempt:

```bash
gh issue create \
  --repo iamcxa/kc-claude-plugins \
  --title "<title>" \
  --body "<body>" \
  --label "<labels>"
```

5. If `gh` is unavailable or fails:
   - Append to `${CLAUDE_PLUGIN_ROOT}/e2e-reports/feedback-log.md`
   - Suggest: "Saved locally. Submit manually: https://github.com/iamcxa/kc-claude-plugins/issues/new"

## Phase 5 — Knowledge Loop

After any interaction, check for improvement opportunities:

- **User asked about undocumented feature** → Suggest doc update or issue
- **User shared a useful pattern** → Suggest adding to relevant doc's examples section
- **User found confusing wording** → Offer to draft a rewrite

Never auto-modify docs. Always present draft and ask for confirmation.
