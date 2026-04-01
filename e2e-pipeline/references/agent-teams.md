# Agent Teams Protocol — Shared Reference

Shared protocol for all e2e-pipeline skills and agents that support Agent Teams mode. Individual skills define their own command formats; this file covers the common infrastructure.

## 1. Teams Mode Detection

**Skill-side (lead context):**

1. Check if `TeamCreate` tool is available (requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
2. Check if `--no-teams` flag is set
3. **Teams mode**: TeamCreate available AND `--no-teams` not set
4. **Subagent mode**: TeamCreate unavailable OR `--no-teams` set

When Teams mode is active, the skill spawns agents as **teammates** (persistent, async messaging) instead of **subagents** (blocking, return-on-complete).

## 2. Team Lifecycle

### Create team (first invocation)

```
TeamCreate(team_name="e2e-<skill>", description="<purpose>")
```

Convention: team name = `e2e-<skill>` (e.g., `e2e-debug`, `e2e-test`).

### Detect existing team (subsequent invocations)

```bash
cat ~/.claude/teams/e2e-<skill>/config.json 2>/dev/null
# Look for expected member names in members array
```

If team exists and expected members are present → **reuse** (skip TeamCreate and browser open). The browser is already running.

### Spawn teammates

```
Agent(
  team_name="e2e-<skill>",
  name="<role-name>",
  subagent_type="e2e-pipeline:<agent-type>",
  prompt="TEAMS MODE. <role-specific instructions>"
)
```

Naming convention for `name`:
- Single runner: `"runner"`
- Multi-role by site: `"runner-<site-alias>"` (e.g., `runner-admin`, `runner-customer`)
- Debug observer: `"observer"`
- CLI runner: `"runner-cli"`

### Teardown

Trigger teardown when:
- All work is confirmed done (root cause found, all tests passed)
- User explicitly requests (`--cleanup --teardown`)
- Error recovery requires fresh state

Teardown procedure:
1. `SendMessage(to="<name>", message={type: "shutdown_request", reason: "<reason>"})` — for each active member
2. Wait for `shutdown_response` (members close browser before approving)
3. `TeamDelete()`

## 3. Browser Teammate Startup Protocol

All browser-operating teammates follow this sequence on first spawn:

### Standard startup (headless)

1. Open browser: `agent-browser open "<url>"`
2. Wait for load: `agent-browser wait --load networkidle`
3. Clear baseline: `agent-browser console --clear` + `agent-browser errors --clear`
4. Send ready:
   ```
   SendMessage(to="lead", message="BROWSER_READY\ntarget_url: <url>\nrole: <role-name>", summary="<role> browser ready")
   ```
5. Stop turn → go idle

### Auth startup (headed / --headed)

1. Open browser headed: `agent-browser open "<url>"` (with `--profile <path>` if applicable)
2. Send auth request:
   ```
   SendMessage(to="lead", message="WAITING_FOR_AUTH\nrole: <role-name>\ntarget_url: <url>", summary="<role> waiting for auth")
   ```
3. Stop turn → go idle
4. On receiving `AUTH_COMPLETE` from lead → clear baseline → send `BROWSER_READY`

### Lead-side auth handling

When lead receives `WAITING_FOR_AUTH`:
1. Present to user: `"<role> browser 已開啟，請手動登入。完成後輸入 'continue' 或 '已登入'"`
2. On user confirmation: `SendMessage(to="<role-name>", message="AUTH_COMPLETE")`

For multi-role spawn with auth: present all auth requests at once, then send `AUTH_COMPLETE` to each after user confirms all.

## 4. Command-Response Protocol

Each skill defines its own command and response formats. The shared envelope is:

### Lead → Teammate (command)

```
SendMessage(
  to="<teammate-name>",
  message="<COMMAND_TYPE>\n<payload>",
  summary="<brief description>"
)
```

Command types are skill-specific:
- `e2e-debug`: `VERIFY` (steps + log_tags + filters)
- `e2e-test`: `EXECUTE_STEP` (step definition + context)
- `e2e-test`: `EXECUTE_FLOW` (full flow for parallel suite mode)

### Teammate → Lead (response)

```
SendMessage(
  to="lead",
  message="<RESULT_TYPE>\n<structured data>",
  summary="<brief: N pass, M fail>"
)
```

Response types are skill-specific, but always start with a keyword line for easy parsing:
- `OBSERVATION COMPLETE` (e2e-debug)
- `STEP COMPLETE` (e2e-test, per-step)
- `FLOW COMPLETE` (e2e-test, full flow)

### Error responses

```
EXECUTION ERROR
step: <step-id or "startup">
error: <description>
recoverable: true|false
```

On error, teammate goes idle. Lead decides: retry, skip, or teardown.

### Hard crash (teammate dies without sending a message)

If the lead sends a command (or shutdown_request) and receives no response within **30 seconds**, assume hard crash. This also applies when a teammate is still executing its first turn (mid-startup) — the 30s timeout is the universal backstop regardless of teammate state:
1. Check if team member still exists in `~/.claude/teams/<team>/config.json`
2. If member gone → teammate process died. Log warning.
3. Fall back to subagent mode for the remaining work. Set any Teams-specific diagnosis mode (e.g., auto-loop) back to interactive.
4. Attempt `TeamDelete()` to clean up.

### TeamCreate / spawn failure

If `TeamCreate` or `Agent(team_name=...)` fails (name collision, filesystem error, experimental feature bug):
1. Log warning: `"Teams infrastructure failed: <error>. Falling back to subagent mode."`
2. **Clean up partial state**: if TeamCreate succeeded but Agent spawn failed → `TeamDelete()` to remove the empty team. If multi-member spawn partially succeeded (some members alive, some failed) → send `shutdown_request` to alive members, wait for response, then `TeamDelete()`. Do not leave orphaned teams.
3. **Do NOT halt.** Proceed with subagent dispatch (original behavior).
4. If the failure changes the diagnosis mode (e.g., auto-loop → interactive), notify the user.

This ensures Teams is always a **progressive enhancement** — failure degrades to subagent, never blocks execution.

## 5. Browser Persistence Rules

| Event | Browser action |
|-------|---------------|
| Command received | Navigate / refresh (browser already open) |
| Command complete | **Stay open**, go idle |
| Error during command | **Stay open**, report error, go idle |
| Teammate idle timeout | **Stay open** (no auto-close) |
| Shutdown request received | **Close browser**, then approve shutdown |
| Session ends (process killed) | Browser daemon may survive — use `agent-browser close` on next session |

Key: `agent-browser open "<url>"` on an already-open browser **navigates within the existing session** (no new window). Teammates can just `open` each time without checking browser state.

### Browser state isolation on reuse

When reusing a teammate for a **different** flow/task (e.g., `--verify-only` after a prior run):
- If `auth_profile` or `base_url` differs → teammate must close and reopen browser with new profile: `agent-browser close` → `agent-browser open "<new_url>"`. Lead should include `base_url` and `auth_profile` in every command so the teammate can detect mismatches.
- If same auth + same base_url → navigate is sufficient. Cookies/localStorage carry over (usually desired — avoids re-login).
- When in doubt → clear console/errors baseline at minimum. For full isolation, close + reopen.

## 6. Multi-Runner Coordination (Lead-side)

When the lead manages multiple teammates:

### Parallel dispatch

Send commands to different teammates without waiting:

```
SendMessage(to="runner-admin", message="EXECUTE_STEP\n...", summary="admin step 1")
SendMessage(to="runner-customer", message="EXECUTE_STEP\n...", summary="customer step 1")
# Both execute in parallel
```

Responses arrive asynchronously. Lead processes as they come in.

### Sequential with data passing

When step B depends on step A's output:

```
SendMessage(to="runner-admin", message="EXECUTE_STEP\nid: create-order\n...")
← runner-admin: "STEP COMPLETE\nresult: PASS\ndata: order_id=12345"

# Lead extracts data, passes to next runner
SendMessage(to="runner-customer", message="EXECUTE_STEP\nid: verify-order\ncontext: order_id=12345\n...")
← runner-customer: "STEP COMPLETE\nresult: PASS"
```

### Site-step routing for cross-site flows

For flows with `sites:` and `site:` per step, the lead routes:

```python
for step in flow.steps:
    target = f"runner-{step.site}"
    send(target, step)
    # Wait for response before next step to same site
    # Steps to different sites with no data dependency: can parallel
```

**Parallel eligibility**: consecutive steps to DIFFERENT sites where the later step does NOT reference variables from the earlier step's output → can be dispatched in parallel.

### Failure handling in multi-step routing

When a step returns `result: FAIL`:

1. **Continue dispatching** — follow subagent-mode convention ("continue on failure, collect maximum evidence")
2. **Dependency cascade**: if a step returns `result: FAIL`:
   - **Detection**: scan all remaining steps' `context:` fields (in the flow YAML) for variable references matching the failed step's expected `data:` keys. This is static analysis of the flow definition at dispatch time.
   - Mark matched downstream steps as `SKIP` with reason `"dependency failed: <failed-step-id>"`
   - Do NOT dispatch them with empty context (causes misleading secondary failures)
   - **Partial data rule**: `FAIL` status always triggers the cascade, even if the response includes partial `data:`. Partial data from a failed step is unreliable — the entity may be in an inconsistent state. Safer to SKIP than to propagate potentially invalid state.
3. **Independent steps continue** — steps that don't reference the failed step's data proceed normally, regardless of which site they're on
4. **Lead logs** the cascade for the final report: `"Steps skipped due to dependency: <list>"`

## 7. Subagent Fallback

When Teams mode is unavailable, skills fall back to original subagent dispatch:

```
Agent(subagent_type="e2e-pipeline:<agent-type>", prompt="<standard subagent prompt>")
```

Agent `.md` files include both modes:
- **Subagent mode** (default): execute all work → return summary
- **Team mode** (prompt starts with "TEAMS MODE"): per-command execution via SendMessage

The agent detects mode from the prompt prefix. No runtime detection needed.

## 7.5. Cross-Skill Teams Coexistence

Multiple e2e-pipeline skills can have **independent teams alive simultaneously**. Each skill uses a unique team name (`e2e-debug`, `e2e-test`, `e2e-flow`) — no name collisions by convention.

**Resource awareness**: Each team with a browser teammate holds an open browser instance. Multiple headed browsers consume significant memory and can confuse users (multiple windows). Skills should:
- Check for existing teams from OTHER skills before spawning: `ls ~/.claude/teams/ 2>/dev/null`
- If other teams exist, inform the user: `"Note: team '<name>' is also active (from a prior /<skill> invocation). Multiple browser windows may be open."`
- Do NOT auto-teardown other skills' teams — the user may want both alive

**Transition pattern**: After `/e2e-test` finds a failure, the lead may offer `/e2e-debug`. If the user accepts:
- `e2e-test` team can stay alive (browser at the failing page)
- `e2e-debug` creates its own team with observer
- Two browsers open simultaneously is acceptable (debug observes different data than test runner)
- On debug completion, user decides which teams to tear down

## 8. Agent Team Mode Template

Standard section to add to any browser-operating agent `.md` file:

```markdown
## Team Mode Protocol

When your spawn prompt starts with **"TEAMS MODE"**, you operate as a persistent
browser teammate instead of a one-shot subagent.

### Startup
1. Open browser and complete initial setup as normal
2. Send BROWSER_READY to lead (see references/agent-teams.md § 3)
3. Stop turn — go idle

### On receiving <COMMAND> message
1. Parse command payload
2. Execute (skill-specific logic)
3. Send structured result to lead
4. DO NOT close browser
5. Stop turn — go idle

### On receiving shutdown_request
1. Close browser: `agent-browser close`
2. Respond with shutdown_response approve=true

### Key differences from subagent mode
- Results via SendMessage (not return summary)
- Browser stays open across commands
- Go idle between commands (lead controls pace)
```

## 9. Model Guidelines

Browser-operating teammates do navigation, fill, click, and visibility checks — not deep reasoning. Use the cheapest model that can handle the task.

| Role | Default model | When to upgrade |
|------|--------------|-----------------|
| Test runner (`e2e-test`) | `haiku` | Complex assertion logic or multi-step data extraction |
| Debug observer (`e2e-debug`) | `haiku` | Diagnostic-heavy sessions (`--model sonnet`) |
| Flow verifier (`e2e-flow`) | inherit | Verifier does selector repair — needs more reasoning |

**Rationale** (A/B tested 2026-03-29 on carlove login-flow):
- Haiku: 7/7 pass, 44K tokens, 258s, 59 tool calls
- Sonnet: 4/7 pass, 40K tokens, 322s, 41 tool calls
- Haiku was faster, cheaper, and more successful for browser interaction
- Sonnet produced better diagnostic detail (listed all stale selectors with correct values)
- Conclusion: haiku for execution, sonnet for diagnosis

**Override**: Skills expose `--model` flag. Lead passes model choice to `Agent(model=...)` at spawn time.

<!-- Last updated: 2026-03-29 -->
