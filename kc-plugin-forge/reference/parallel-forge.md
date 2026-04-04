# Parallel Forge Reference

Teammate dispatch templates and coordination patterns for `--parallel` mode. Based on Teams v1 protocol.

## When Active

`--parallel` flag is set AND `TeamCreate` tool is available. Otherwise, forge runs in sequential mode (default behavior).

## Team Lifecycle

```
forge --parallel <plugin-path>
  │
  ├─ TeamCreate("forge-<plugin-name>")
  ├─ Phase 1 + 1.5 (lead, sequential)
  │
  ├─ Phase 2: spawn N skill-tdd teammates
  │   → collect results → D1 writes → Phase 2.7 (lead)
  │   → shutdown Phase 2 teammates
  │
  ├─ Phase 2.5: parallel Bash (no teammates)
  │
  ├─ Phase 3: spawn M agent-verify teammates
  │   → collect results → shutdown Phase 3 teammates
  │
  ├─ Phase 4 (lead) → TeamDelete
  └─ done
```

## Phase 2: Skill TDD Teammate Template

Dispatch one teammate per skill in `skills/` directory.

### Teammate name convention

`tdd-<skill-name>` (e.g., `tdd-kc-pr-review`, `tdd-kc-pr-create`)

### Dispatch prompt

```
You are a skill TDD teammate for Plugin Forge parallel mode.

TARGET SKILL: <plugin-path>/skills/<skill-name>/SKILL.md

YOUR TASK:
1. Read these reference files for context:
   - <forge-plugin-root>/reference/quality-pipeline.md
   - <forge-plugin-root>/reference/learned-patterns.md
   - <forge-plugin-root>/reference/skill-evolution.md

2. Invoke the TDD skill:
   Skill("superpowers:writing-skills")

3. Run the full RED → GREEN → REFACTOR cycle on the target skill.
   - RED: Design 3-4 pressure scenarios appropriate to the skill's domain
   - GREEN: Modify the SKILL.md to address failures
   - REFACTOR: Find rationalizations, plug loopholes

4. After TDD completes, also verify:
   - Evolution setup (step 6): Does the skill have the correct D1/D2 level?
     Expected level: <Full|D1|Skip>
   - Teams setup (step 7): Does the skill have correct Teams support?
     Expected level: <Full|Skip>

5. Send your result to lead with this structure:
   SKILL_TDD_COMPLETE
   skill: <skill-name>
   status: PASS | FAIL
   scenarios_tested: <count>
   scenarios_passed: <count>
   changes_made: <brief summary of SKILL.md edits, or "none">
   evolution_check: PASS | FAIL | SKIP
   teams_check: PASS | FAIL | SKIP
   findings: <list of potential D1 patterns, or "none">

RULES:
- Do NOT write to learned-patterns.md — return findings only
- Do NOT modify files outside skills/<skill-name>/
- Accept defaults for any interactive prompts
- If TDD requires reading the target plugin's other files (references, agents), read them
```

### Lead-side collection

After all Phase 2 teammates report:

1. Parse each `SKILL_TDD_COMPLETE` message
2. Aggregate: total scenarios, pass rate, changes summary
3. For each teammate's `findings`: apply three-question test (Recurs? Non-obvious? Ruleable?)
4. Write qualifying D1 findings to `learned-patterns.md` sequentially
5. If any teammate status is FAIL → note in Phase 4 report

## Phase 2.5: Parallel Smoke Tests

No teammates needed — use shell-level parallelism:

```bash
PIDS=()
RESULTS=()

for skill_name in $SKILLS; do
  (
    ${CLAUDE_PLUGIN_ROOT}/reference/clean-profile-test.sh \
      "$PLUGIN_DIR" "$TRIGGER" "$TIMEOUT" "${ASSERTIONS[@]}" \
      > "/tmp/forge-smoke-${skill_name}.log" 2>&1
    echo "$?" > "/tmp/forge-smoke-${skill_name}.exit"
  ) &
  PIDS+=($!)
done

for i in "${!PIDS[@]}"; do
  wait "${PIDS[$i]}"
  exit_code=$(cat "/tmp/forge-smoke-${SKILLS[$i]}.exit")
  RESULTS+=("${SKILLS[$i]}:${exit_code}")
done
```

Each smoke test is an independent `claude --bare` process — natural isolation.

## Phase 3: Agent Verify Teammate Template

Dispatch one teammate per agent in `agents/` directory.

### Teammate name convention

`verify-<agent-name>` (e.g., `verify-sentry-analyzer`, `verify-e2e-mapper`)

### Dispatch prompt

```
You are an agent verification teammate for Plugin Forge parallel mode.

TARGET AGENT: <plugin-path>/agents/<agent-name>.md

YOUR TASK:
1. Read the forge quality reference:
   - <forge-plugin-root>/reference/quality-pipeline.md (Phase 3 section)
   - <forge-plugin-root>/reference/agent-teams-quality.md (if Teams check needed)

2. Invoke the agent verification skill:
   Skill("plugin-dev:agent-development")

3. Verify all checklist items:
   - Name format, description with <example> blocks
   - Model choice, color, tools restriction
   - System prompt in 2nd person
   - Input/output contract, rules + anti-patterns
   - Reference paths use ${CLAUDE_PLUGIN_ROOT}

4. Run 1 dispatch test: simulate a matching scenario

5. If Teams level is Full, also verify:
   - A1-A4 (agent checklist from agent-teams-quality.md)

6. Send result to lead:
   AGENT_VERIFY_COMPLETE
   agent: <agent-name>
   status: PASS | FAIL | WARN
   items_checked: <count>
   items_passed: <count>
   items_failed: <list or "none">
   teams_check: PASS | FAIL | SKIP
   dispatch_test: PASS | FAIL

RULES:
- Do NOT modify any files — this is read-only verification
- If dispatch test requires tools the agent doesn't have, note as SKIP (not FAIL)
```

## Shared Resource Protection

Teammates must NOT write to these files:

| File | Reason |
|------|--------|
| `reference/learned-patterns.md` | Multiple concurrent appends → data loss |
| `reference/quality-pipeline.md` | Forge-internal, lead writes only |
| `reference/*.md` (any shared reference) | Lead coordinates D1 writes after collection |
| `.claude-plugin/plugin.json` | Version bump is lead's responsibility |

Teammates CAN write to:
- `skills/<their-assigned-skill>/SKILL.md` (Phase 2 only, each has a unique target)

## Rate Limit Protocol

Parallel teammates increase API call density. Protection:

1. **Stagger spawn**: 2-second delay between teammate spawns to avoid burst
2. **Monitor**: If a teammate reports rate limit in its error, lead pauses spawn
3. **Circuit breaker**: 2nd rate limit across any teammate → stop spawning new teammates, let existing ones drain, process remaining skills sequentially
4. **Cost awareness**: N teammates × writing-skills TDD ≈ N × ~120K tokens. Show estimate before spawning:
   ```
   Parallel mode: spawning 5 teammates for Phase 2
   Estimated cost: ~600K tokens (5 × ~120K)
   Proceed? [y/n]
   ```

## Error Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Teammate spawn fails | Agent() returns error | Log warning, run that skill sequentially |
| Teammate crashes (no response) | 120s timeout after spawn | Shutdown team member if possible, run sequentially |
| Teammate returns malformed result | Message doesn't start with expected keyword | Ask teammate to re-send, or mark as FAIL |
| TeamCreate fails | Tool returns error | Abort parallel mode, run entire forge sequentially |
| All teammates fail | 0 successful results from Phase 2 | Log critical warning, ask user: retry sequential or abort? |

## Metrics Collection

Track for Phase 4 report:

```
parallel_metrics:
  mode: parallel
  team_name: forge-<plugin>
  phase2:
    teammates_spawned: N
    teammates_succeeded: M
    wall_time_seconds: T
    sequential_estimate_seconds: T * N  # rough comparison
  phase2_5:
    processes_spawned: N
    wall_time_seconds: T
  phase3:
    teammates_spawned: M
    teammates_succeeded: K
    wall_time_seconds: T
```

<!-- Based on Teams v1 protocol. Last updated: 2026-04-04 -->
