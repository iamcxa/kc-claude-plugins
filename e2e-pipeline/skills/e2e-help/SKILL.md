---
name: e2e-help
description: Use when users need help discovering E2E pipeline commands or want to report doc gaps. Triggers on "e2e help", "/e2e-help", "how do I e2e".
---

# E2E Help -- Interactive Pipeline Guide

Help users discover, understand, and improve the E2E testing pipeline.

## Invocation

```
/e2e-help                            # Overview of all commands
/e2e-help <topic>                    # Deep dive into a topic
/e2e-help --feedback "<message>"     # Report a doc gap or feature request
/e2e-help --list-topics              # Show available help topics
```

## Phase 1 -- Parse Args

| Arg | Mode |
|-----|------|
| *(none)* | Overview (full reference + topics + quick start) |
| `--list-topics` | Topic list only (lightweight) |
| `<topic>` | Topic deep dive |
| `--feedback "<message>"` | Feedback collection |

## Phase 2 -- Overview Mode (no args)

Present a complete command reference by reading live skill data:

```
Read -> ${CLAUDE_PLUGIN_ROOT}/skills/*/SKILL.md  (extract name + description from frontmatter)
Read -> ${CLAUDE_PLUGIN_ROOT}/docs/*.md           (extract filenames for topic mapping)
```

**IMPORTANT: BOTH tables below (Commands AND Topics) are formatting guides only — populate them from the live reads above.** New skills or new doc files added to the plugin MUST appear in the output. Do not emit either template verbatim.

- **Commands table**: One row per skill. Extract `name` and `description` from each `skills/*/SKILL.md` frontmatter.
- **Topics table**: One row per doc file. Derive topic name from filename (strip `.md`, use as-is). Read the first heading or first paragraph to generate the "Covers" column. The keyword mapping in Phase 3 provides aliases, but the topic list itself comes from the live `docs/*.md` scan.

Present (format guide — populate from live data):

```markdown
# E2E Pipeline -- Quick Reference

## Commands

| Command | What it does |
|---------|-------------|
| `/<skill-name>` | <extracted from skill description frontmatter> |
| ... | ... |

## Topics (use `/e2e-help <topic>` for details)

| Topic | Covers |
|-------|--------|
| `<filename-without-extension>` | <derived from doc file first heading or summary> |
| ... | ... |

## Quick Start

**First time?**
1. `/e2e-map` -> map your app
2. `/e2e-flow --smoke` -> generate a smoke test
3. `/e2e-test smoke-navigation` -> run it

**From a plan?**
`/e2e-flow --from plan.md` -> generates + verifies automatically

**Multiple apps?**
`/e2e-test --all-sites` -> runs on every mapped site

**Curated test set?**
`/e2e-test --suite regression` -> runs a defined playlist
```

Always end with:

```
---
Missing something? `/e2e-help --feedback "<description>"` to report a gap.
Full docs: ${CLAUDE_PLUGIN_ROOT}/docs/
```

### --list-topics Mode

When `--list-topics` is used, present ONLY the Topics table (no Commands, no Quick Start). Same live-read derivation from `docs/*.md`.

## Phase 3 -- Topic Deep Dive

**Keyword alias table** — maps common keywords to doc files. This is a convenience layer, NOT the exhaustive list. Doc files found via live `docs/*.md` scan that have no alias entry are still valid topics via their filename.

| Topic keyword(s) | Doc file |
|-------------------|----------|
| `getting-started`, `install`, `setup` | `docs/getting-started.md` |
| `writing-tests`, `flow-format`, `yaml` | `docs/writing-tests.md` |
| `cross-site`, `multi-site`, `sites` | `docs/multi-site-testing.md` |
| `suites`, `suite` | `docs/suites.md` |
| `checkpoints`, `external`, `verify-external`, `execute-external` | `docs/cross-boundary-testing.md` |
| `recording`, `video`, `evidence`, `cli-recording`, `terminal-recording`, `cli-only` | `docs/recording-evidence.md` |
| `ci`, `github-actions`, `compiled` | `docs/ci-integration.md` |
| `debugging`, `troubleshoot`, `fix` | `docs/debugging.md` |
| `architecture`, `design`, `agents` | `docs/architecture.md` |
| `commands`, `flags`, `options` | `docs/commands.md` |
| `pr`, `pr-workflow`, `pull-request` | `docs/pr-workflow.md` |
| `self-improvement`, `learning`, `knowledge` | `docs/self-improvement.md` |

**Resolution order:**

1. Check keyword alias table above for exact match
2. If no alias match, check if `<topic>.md` exists in `${CLAUDE_PLUGIN_ROOT}/docs/`
3. If still not found, list available topics (derived from live `docs/*.md` scan, not from the alias table)

```
Read -> ${CLAUDE_PLUGIN_ROOT}/docs/<topic>.md   (direct filename match)
```

If resolved: read the doc file and present content with a summary header.

If not found after both checks:
```
Topic "<topic>" not recognized.
Available topics (from docs/):
<list derived from live docs/*.md scan>
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
This answer came from internal skill definitions, not user docs.
This suggests a documentation gap. Want me to:
1. Add a section to the relevant doc? (I'll draft for your review)
2. Create a tracking issue?
3. Skip -- one-off question
```

## Phase 4 -- Feedback Mode

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
   - Append to `.claude/e2e/reports/feedback-log.md`
   - Suggest: "Saved locally. Submit manually: https://github.com/iamcxa/kc-claude-plugins/issues/new"

## Phase 5 -- Knowledge Loop

After any interaction, check for improvement opportunities:

- **User asked about undocumented feature** -> Suggest doc update or issue
- **User shared a useful pattern** -> Suggest adding to relevant doc's examples section
- **User found confusing wording** -> Offer to draft a rewrite

Never auto-modify docs. Always present draft and ask for confirmation.
