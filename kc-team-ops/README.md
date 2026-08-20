# kc-team-ops

Team operations pipeline for Claude Code. EM triage, project pulse updates, codebase exploration, issue decomposition, and structured Linear management.

## Installation

```bash
# Load as plugin directory
claude --plugin-dir /path/to/kc-team-ops
```

Register in marketplace if using local plugin management:
1. Add to `~/.claude/plugins/local/.claude-plugin/marketplace.json`
2. Enable in `~/.claude/settings.json`: `"kc-team-ops@local": true`
3. Restart Claude Code session

## Usage

```
/kc-em-triage          # EM triage pipeline (with strategic lens)
/kc-em-sync            # Sync team context (initiatives, projects, members) to local cache
/kc-project-pulse      # Project status updates
/kc-rules-review       # Audit CLAUDE.md / AGENTS.md against real session history
```

Invoke with Linear issue IDs, filter criteria, document input, or meeting notes.

## Dependencies

Required MCP servers:
- **Linear** — issue read/write, customer needs, cycles, labels
- **Context7** (optional) — library documentation lookup for research agent

Required plugins:
- **episodic-memory** — conversation history search for knowledge layer exploration
- **feature-dev** — `code-explorer` agent for multi-layer codebase analysis

## Components

### Skills

- **kc-em-triage** — Main orchestrator with strategic lens. Depth-adaptive triage: EM Lens entry → explore → deliberate → EM Lens exit → discuss → post.
- **kc-em-sync** — Team context sync. Fetches initiatives, projects, members, cycles, customers from Linear into `~/.claude/kc-team-ops/<team>-context.yaml`.
- **kc-project-pulse** — Project status update drafting and posting to Linear.
- **kc-journey-map** — Draw a user journey from the code, or check an existing journey against it. Three lanes per step (person / system / invariant), every system claim cited to `file:line`, and a mandatory status card for what is unproven, unmerged, or undeployed. FigJam when available, self-contained HTML + PNG otherwise.

- **kc-rules-review** — Audit an operating rule set against what actually happened in the user's sessions. Measures friction (how often the user repaired the output) against firing (how often the rule left a trace), because a rule with high friction and low firing is not missing — it has no trigger. Optional route propagates the result to repo `AGENTS.md`.

### Agents

- **em-lens-scanner** — Lightweight strategic scanner (Haiku). Reads team context cache, verifies issue content against codebase, produces EM Lens cards with depth recommendations.
- **em-researcher** — Tech feasibility researcher. Investigates unfamiliar libraries, version compatibility, API surfaces using Context7 and web sources.
- **design-spec-writer** — Design specification writer. Synthesizes multi-layer exploration findings into formal design spec documents for async review.

### Reference Files

| File | Purpose |
|------|---------|
| `exploration-discipline.md` | Rationalization patterns to guard against exploration skipping |
| `research-methodology.md` | Source priority and verification rules for research agent |
| `design-spec-flow.md` | Design spec process steps |
| `estimate-inference.md` | Team estimate scale inference procedure |
| `decompose-flow.md` | Issue and document decomposition flows |
| `meeting-notes-flow.md` | Meeting notes → Customer Needs pipeline |
| `health-assessment.md` | Health assessment heuristic for project pulse updates |
| `project-creation-flow.md` | Linear project creation process and structured description format |
| `strategic-lens.md` | EM Lens depth routing logic, estimate scale mapping, card formats |

### Scripts

| File | Purpose |
|------|---------|
| `scripts/rule-firing-report.sh` | Counts friction and rule-firing across Claude Code session logs for `kc-rules-review`. `--help` for usage. |

## License

MIT
