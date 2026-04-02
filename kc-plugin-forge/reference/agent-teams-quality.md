# Agent Teams Quality Reference

Verification patterns for plugins that support Claude Code Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Based on Teams v1 protocol as implemented in e2e-pipeline.

## When This Applies

Only when the plugin chose **Full Teams** in Phase 1.5 C. Plugins that chose Skip have no Teams-related checks.

## Agent Checklist (per browser-operating agent)

| # | Check | PASS criteria |
|---|-------|--------------|
| A1 | Team Mode Protocol section exists | Agent `.md` has `## Team Mode Protocol` heading |
| A2 | Startup → Command → Shutdown complete | All three documented as sub-headings or numbered list |
| A3 | Mode detection via prompt prefix | Mentions "TEAMS MODE" prefix as mode discriminator |
| A4 | Subagent mode preserved | Agent's one-shot behavior (execute all → return summary) is not broken by Teams section |

### A4 detail

The Team Mode Protocol section must be **additive** — it describes an alternative execution mode, not a replacement. The agent's existing instructions (subagent mode) must remain functional when the spawn prompt does NOT start with "TEAMS MODE".

## Skill Checklist (per dispatch skill)

| # | Check | PASS criteria |
|---|-------|--------------|
| S1 | Teams mode detection | Skill checks `TeamCreate` tool availability AND `--no-teams` flag |
| S2 | Fallback path | Explicit subagent dispatch path when Teams unavailable |
| S3 | Error handling | TeamCreate/spawn failure → cleanup partial state → fallback (never halt) |
| S4 | Shutdown protocol | Teardown procedure: send `shutdown_request` → wait response → `TeamDelete()` |
| S5 | `--no-teams` flag | Documented in argument table, forces subagent mode |

### S3 detail — Error handling template

```
If TeamCreate or Agent(team_name=...) fails:
  1. Log warning with error details
  2. Clean up partial state:
     - TeamCreate succeeded but spawn failed → TeamDelete()
     - Partial spawn (some members alive) → shutdown_request to alive → TeamDelete()
  3. Proceed with subagent dispatch (original behavior)
  4. Never halt execution due to Teams failure
```

## Plugin-Level Checklist

| # | Check | PASS criteria |
|---|-------|--------------|
| P1 | Shared protocol reference | `references/agent-teams.md` exists and is Read by agents/skills |
| P2 | Team naming convention | All team names use `<plugin-short>-<skill>` format (e.g., `e2e-debug`) |
| P3 | No name collisions | Each skill uses a unique team name — verify across all skills |

## TDD Pressure Scenarios

Use these during Phase 2 Skill TDD for skills that dispatch Teams agents.

### T1: TeamCreate unavailable

```
Scenario: User runs the skill but CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 is not set.
TeamCreate tool does not exist in the session.

Expected: Skill detects unavailability, logs informational message,
proceeds with standard subagent dispatch. No error, no halt.
```

### T2: Teammate hard crash

```
Scenario: Teammate is spawned successfully but dies mid-command.
SendMessage to teammate gets no response for 30+ seconds.

Expected: Skill detects timeout, logs warning, cleans up team
(TeamDelete), falls back to subagent for remaining work.
```

### T3: --no-teams flag

```
Scenario: User explicitly passes --no-teams flag.
TeamCreate tool IS available.

Expected: Skill skips Teams entirely, uses subagent dispatch.
No TeamCreate call, no team lifecycle management.
```

### T4: Mode detection in agent

```
Scenario: Agent is spawned as a subagent (no "TEAMS MODE" prefix).
Agent definition has a Team Mode Protocol section.

Expected: Agent executes in one-shot mode (execute all work → return
summary). Does NOT send SendMessage, does NOT go idle between steps.
Team Mode Protocol section is ignored.
```

## Agent Team Mode Protocol Template

Add this section to any agent `.md` that should support Teams mode:

```markdown
## Team Mode Protocol

When your spawn prompt starts with **"TEAMS MODE"**, you operate as a persistent
teammate instead of a one-shot subagent.

### Startup
1. Complete initial setup (open browser, load resources, etc.)
2. Send ready message to lead:
   ```
   SendMessage(to="lead", message="READY\nrole: <role-name>", summary="<role> ready")
   ```
3. Stop turn — go idle

### On receiving command message
1. Parse command payload
2. Execute (role-specific logic)
3. Send structured result to lead:
   ```
   SendMessage(to="lead", message="COMPLETE\nresult: <structured data>", summary="<brief>")
   ```
4. Stop turn — go idle

### On receiving shutdown_request
1. Clean up resources (close browser, flush state)
2. Respond: `SendMessage(to="lead", message="shutdown_response\napprove: true")`

### Key differences from subagent mode
- Results via SendMessage (not return summary)
- Resources stay open across commands
- Go idle between commands (lead controls pace)
- Never self-terminate — wait for shutdown_request
```

## Skill Teams Detection Template

Add this to the skill's pre-flight or argument processing section:

```markdown
### Teams Mode Detection

1. Check if `TeamCreate` tool is available (requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
2. Check if `--no-teams` flag is set
3. **Teams mode**: TeamCreate available AND `--no-teams` not set
4. **Subagent mode**: TeamCreate unavailable OR `--no-teams` set

When Teams mode is active, spawn agents as teammates (persistent, async messaging)
instead of subagents (blocking, return-on-complete).

When Teams mode fails (TeamCreate error, spawn failure, teammate crash):
1. Log warning with error details
2. Clean up partial state (TeamDelete if team was created)
3. Fall back to subagent mode — never halt execution
```

## Common Gotchas

- **Orphaned teams**: If skill exits without teardown (crash, context exceeded), teams persist in `~/.claude/teams/`. Next session should detect and clean up orphaned teams from the same plugin.
- **Browser persistence**: Each teammate with a browser holds an open browser instance. Multiple headed browsers consume memory and confuse users. Log active teams when spawning new ones.
- **Mode detection is prompt-based**: The agent checks if its spawn prompt starts with "TEAMS MODE". This is a convention, not a system feature. If the skill sends a prompt without the prefix, the agent runs in subagent mode even if spawned via `Agent(team_name=...)`.
- **SendMessage not available in subagents**: One-shot subagents do NOT have `SendMessage`. Agent code that unconditionally calls `SendMessage` will fail in subagent mode. The Team Mode Protocol section must be conditional on the mode prefix.
- **TeamCreate is experimental**: The API may change. Reference files should note "based on Teams v1 protocol" and be updated when the API stabilizes.
- **Cross-skill team coexistence**: Multiple skills can have independent teams alive simultaneously. Each skill MUST use a unique team name. Check `ls ~/.claude/teams/` before spawning to inform the user about other active teams.

<!-- Based on Teams v1 protocol. Last updated: 2026-04-02 -->
