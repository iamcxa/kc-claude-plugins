---
name: kc-plugin-forge-help
description: Use when users need help with Plugin Forge commands, want to discover available routes, or report documentation gaps. Triggers on "forge help", "how do I forge", "what forge commands", "kc-plugin-forge-help", "help with plugin forge", "what can forge do", "plugin forge help".
---

# Plugin Forge Help — Interactive Guide

Help users discover, understand, and improve the Plugin Forge pipeline.

## Invocation

```
/kc-plugin-forge-help                        # Overview of all commands
/kc-plugin-forge-help <topic>                # Deep dive into a topic
/kc-plugin-forge-help --feedback "<message>" # Report a doc gap or feature request
/kc-plugin-forge-help --list-topics          # Show available help topics
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
Read → ${CLAUDE_PLUGIN_ROOT}/reference/*.md      (extract filenames for topic mapping)
```

Use the template below as a **formatting guide only**. Populate the Commands table from the live reads above — do not emit hardcoded rows that differ from what the file system contains.

Present:

```markdown
# Plugin Forge — Quick Reference

## Commands

| Command | What it does |
|---------|-------------|
| `/kc-plugin-forge <path>` | Full pipeline: validate → TDD → agents → report |
| `/kc-plugin-forge new <name>` | Scaffold a new plugin, then full pipeline |
| `/kc-plugin-forge validate-only` | Phase 1 only — structure check |
| `/kc-plugin-forge skill-tdd-only` | Phase 2 only — TDD cycle per skill |
| `/kc-plugin-forge agent-verify-only` | Phase 3 only — verify agent definitions |
| `/kc-plugin-forge self-forge` | Forge audits itself (Phase 2 + 4) |
| `/kc-plugin-forge-help` | This help screen |

## Pipeline Phases

| Phase | What it does |
|-------|-------------|
| 1. Structure | Validate plugin.json, file layout, agent frontmatter |
| 1.5 Autonomy | A: Self-Learning (D1/D2) + B: Doc Self-Iteration |
| 2. Skill TDD | RED/GREEN/REFACTOR cycle per skill |
| 3. Agent Verify | Check examples, tools, prompts per agent |
| 4. Report | Re-validate + summary + learning capture |

## Topics (use `/kc-plugin-forge-help <topic>` for details)

| Topic | Covers |
|-------|--------|
| `getting-started` | Install, prerequisites, first forge run |
| `phases` | Deep dive into Phase 1 → 4 |
| `routes` | All routes explained (full, validate-only, skill-tdd, etc.) |
| `self-improvement` | D1/D2 learning framework, learned-patterns.md |
| `doc-sync` | Template-based doc self-iteration |
| `self-forge` | Running forge on itself |
| `gotchas` | Common pitfalls from quality-pipeline.md |
| `prerequisites` | Required marketplace plugins |

## Quick Start

**First time? Validate an existing plugin:**
1. Install prerequisites: `superpowers` + `plugin-dev` marketplace plugins
2. `/kc-plugin-forge path/to/my-plugin` → runs full 4-phase pipeline
3. Review report → fix any FAIL items

**Creating a new plugin?**
`/kc-plugin-forge new my-plugin` → scaffold + full pipeline

**Just checking structure?**
`/kc-plugin-forge validate-only` → Phase 1 only

**Periodic self-audit?**
`/kc-plugin-forge self-forge` → forge audits its own skill quality
```

Always end with:

```
---
Missing something? `/kc-plugin-forge-help --feedback "<description>"` to report a gap.
Contribute: https://github.com/iamcxa/kc-claude-plugins
```

## Phase 3 — Topic Deep Dive

Map topic names to reference files:

| Topic keyword(s) | Source | Section |
|-------------------|--------|---------|
| `getting-started`, `install`, `setup`, `prerequisites` | `reference/quality-pipeline.md` | Prerequisites |
| `phases`, `pipeline`, `phase-1`, `phase-2`, `phase-3`, `phase-4` | `skills/kc-plugin-forge/SKILL.md` | Phase 1 → Phase 4 |
| `routes`, `commands`, `flags` | `skills/kc-plugin-forge/SKILL.md` | Routing + Route Selection Rules |
| `self-improvement`, `learning`, `d1`, `d2`, `evolution` | `reference/skill-evolution.md` | Full file |
| `doc-sync`, `documentation`, `doc-iteration` | `reference/doc-sync-templates.md` | Full file |
| `self-forge`, `self-audit` | `skills/kc-plugin-forge/SKILL.md` | Route Selection Rules → `self-forge` |
| `gotchas`, `pitfalls`, `lessons` | `reference/quality-pipeline.md` | All Gotcha sections |
| `patterns`, `learned` | `reference/learned-patterns.md` | Full file |

1. Resolve topic keyword → source file: `${CLAUDE_PLUGIN_ROOT}/<source>`
2. Read the file (or relevant section)
3. Present content with a summary header

If topic not found:
```
Topic "<topic>" not recognized.
Available: getting-started, phases, routes, self-improvement, doc-sync, self-forge, gotchas, prerequisites, patterns
```

After presenting, always append:
```
---
> Want more detail? Source file: `<source-path>`.
> Found a gap? `/kc-plugin-forge-help --feedback "<what's missing>"`
> Know a better pattern? PRs welcome: https://github.com/iamcxa/kc-claude-plugins
```

### Gap Detection

If answering the user's question required reading a SKILL.md section that has no corresponding reference doc, note this:

```
This answer came from internal skill definitions, not reference docs.
This suggests a documentation gap. Want me to:
1. Add a section to the relevant reference? (I'll draft for your review)
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

**Title**: [kc-plugin-forge] [<type>] <summary>
**Body**: <details with context>
**Labels**: documentation, kc-plugin-forge (or enhancement, bug)

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
   - Append feedback to `${CLAUDE_PLUGIN_ROOT}/feedback-log.md` (local persistence)
   - Suggest: "Saved locally. Submit manually: https://github.com/iamcxa/kc-claude-plugins/issues/new"

## Phase 5 — Knowledge Loop

After any interaction, check for improvement opportunities:

- **User asked about undocumented feature** → Suggest doc update or issue
- **User shared a useful pattern** → Suggest adding to `reference/learned-patterns.md`
- **User found confusing wording** → Offer to draft a rewrite

Never auto-modify docs. Always present draft and ask for confirmation.
