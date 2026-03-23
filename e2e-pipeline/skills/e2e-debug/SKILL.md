---
name: e2e-debug
description: Use when debugging frontend runtime bugs by injecting console.log, observing in browser, and auto-cleaning up. Triggers on "e2e debug", "e2e-debug", "debug in browser", "inject logs", "runtime debug", "why is this empty", "data shape bug". Also triggered by /e2e-dispatch menu or systematic-debugging experiment dispatch.
---

# E2E Debug — Inject-Observe-Cleanup Orchestrator

Debug frontend runtime bugs by injecting `console.log` probes into suspect code, observing their output in a browser, diagnosing root cause, and cleaning up all injections. Runs in main context. Dispatches only one agent: `e2e-debug-observe`.

**Invariant: Phase 4 (Cleanup) MUST execute regardless of any failure in prior phases.** Treat every phase after Phase 1 as if wrapped in try/finally where finally = Phase 4.

## Invocation

```
/e2e-debug "<bug description>"                                              # standalone (UC1)
/e2e-debug --url <url> --suspect "<file>"                                   # standalone with hints
/e2e-debug --experiment --inject '[...]' --steps "..." --url <url>          # experiment (UC2)
/e2e-debug --continue                                                       # next round with previous context
/e2e-debug --cleanup                                                        # force cleanup of residual injections
```

| Arg | Effect |
|-----|--------|
| `"<description>"` | Bug description — used for hypothesis formation |
| `--url <url>` | Target URL for browser observation |
| `--suspect "<file>"` | File(s) to focus analysis on (comma-separated) |
| `--experiment` | Experiment mode — skip analysis, injection points pre-specified by caller |
| `--inject '[...]'` | JSON array of injection specs (experiment mode only) |
| `--steps "..."` | Reproduction steps as semicolon-separated string (experiment mode only) |
| `--headed` | Open visible browser — user can manually log in before agent continues |
| `--continue` | Resume from previous round's conclusions |
| `--cleanup` | Force cleanup — skip all phases, run Phase 4 only |

**No args:** Ask user to describe the bug or provide `--experiment` parameters. Do not proceed without input.

**Experiment mode validation:** When `--experiment` is set, all three are required: `--inject`, `--steps`, `--url`. If any is missing, ask the user for the missing parameter(s) before proceeding. Do NOT skip Phase 0 as a fallback — experiment mode means the caller already did the analysis.

## Knowledge Bootstrap (before Phase 0)

Read accumulated patterns to inform debug analysis:

```
Read -> ${CLAUDE_PLUGIN_ROOT}/references/learned-patterns.md
```

Use loaded patterns to:
- Recognize previously-seen data shape issues
- Avoid re-investigating known framework behaviors
- Inform hypothesis formation in Phase 0

---

## Phase 0 — Analyze

**Skip conditions:** `--experiment` (injection points pre-specified) | `--cleanup` (cleanup only)

### Path A: Clear description (user provides steps + symptom)

1. Dispatch `feature-dev:code-explorer` agent to trace the execution path from the described symptom — it maps architecture layers, data flow, and dependencies more effectively than generic grep
2. From explorer results: identify key data flow points (variable assignments, function returns, API response handlers, React hook returns)
3. Determine injection points: pick 2-5 locations where `console.log` will reveal the data shape at each stage of the flow
4. Determine reproduction steps: translate user's description into ordered browser actions
5. Resolve `--url` (explicit or infer from dev server / code routes)

### Path B: Vague description (symptom only, e.g., "workspace list is empty")

1. Check if `Skill("systematic-debugging")` is available via tool list
2. **If available:** invoke it — receive hypotheses + suggested investigation points. Use its output to determine injection points.
3. **If unavailable:** best-effort analysis:
   - Grep for keywords from the symptom (component names, variable names, route paths)
   - Read the most relevant 2-3 files
   - Form a hypothesis based on common patterns (double-wrapping, undefined access, stale cache, race condition)
   - **If grep yields nothing useful and no target URL can be determined:** tell the user what information is needed (suspect file, URL, or reproduction steps) before proceeding. Do not attempt blind injection.
4. Present hypothesis to user for confirmation before proceeding

### Path C: `--continue` mode

1. Read latest history from `.claude/e2e/debug/history/` — find most recent `*-r<N>.yaml`
2. Load its `session_id`, `hypothesis`, `observations`, `verdict`, `next_investigation`
3. If `manifest.yaml` exists (previous round didn't cleanup): run Phase 4 cleanup first
4. Build new injection points based on `next_investigation` and prior observations
5. Increment round number

**Output of Phase 0:** `injection_plan` (list of `{file, line, tag, code, original_line}`) + `reproduction_steps` (ordered string list) + `hypothesis` + `target_url`

---

## Phase 1 — Inject

### Pre-check: Residual detection

```
Grep for '\[E2E-DBG\]' across project source directories (apps/ src/ lib/ components/)
```

If matches found:
- Warn: "Found residual [E2E-DBG] injections from a previous session. Clean up first?"
- If user confirms (or in `--experiment` mode): run Phase 4 cleanup, then proceed
- If user declines: abort

### Injection loop

For each point in `injection_plan`:

1. Read the target file
2. Locate `original_line` — verify it exists at or near the expected line number
3. Insert the injection code **BEFORE** the original line using Edit tool
4. Record the injection in the manifest

**Injection format** (reference: `reference.md` Section 4):
```typescript
console.log('[E2E-DBG:<module>:<variable>]', JSON.stringify(<value>));
```

Rules:
- Tag format: `[E2E-DBG:<module>:<variable>]` — always this exact prefix
- Always `console.log` — never `console.error` (conflicts with agent-browser error collection)
- Always `JSON.stringify()` — prevents `[object Object]` in output
- Insert **BEFORE** the observed line, not after
- One log per data point — do not combine multiple values

### Write manifest

Write manifest to `.claude/e2e/debug/manifest.yaml` — schema in `reference.md` Section 1.

```
mkdir -p .claude/e2e/debug/history
Write -> .claude/e2e/debug/manifest.yaml
```

**From this point forward, Phase 4 cleanup is MANDATORY. If any subsequent phase fails, skip to Phase 4.**

---

## Phase 2 — Observe

Dispatch the `e2e-debug-observe` agent to open a browser, execute reproduction steps, and collect debug output.

### Prepare dispatch payload

Build from manifest + Phase 0 outputs:

| Field | Source |
|-------|--------|
| `target_url` | From `--url` or Phase 0 analysis |
| `reproduction_steps` | From Phase 0 or `--steps` |
| `report_dir` | `.claude/e2e/debug/` (absolute path) |
| `auth_profile` | Detect from `.agent-browser/` profiles if auth is needed for the URL |
| `headed` | `true` if `--headed` flag provided (user needs to log in manually) |
| `log_tags` | `["E2E-DBG"]` (always) |
| `network_filters` | Extract from manifest `network_filters` if present |

### Dispatch

```
Agent(subagent_type="e2e-pipeline:e2e-debug-observe"):
  Observe debug:
    target_url: <url>
    reproduction_steps:
      - <step 1>
      - <step 2>
      ...
    report_dir: <absolute_path>/.claude/e2e/debug
    auth_profile: <path if needed>
    log_tags:
      - E2E-DBG
    network_filters:
      - <filter 1>
      ...
```

### Handle agent result

- **Success:** Agent returns structured summary with console output, errors, network data. Proceed to Phase 3.
- **Failure:** Note the failure reason. **Still proceed to Phase 4 (cleanup).** Skip Phase 3 — report that observation failed and suggest manual reproduction.

---

## Phase 3 — Diagnose

### Read and analyze report

1. Read `.claude/e2e/debug/report.md`
2. Extract the `[E2E-DBG] Console Output` table — map each tag to its observed value and step number
3. Cross-reference with the injection plan: for each tag, what was expected vs. what was observed?

### Present diagnosis

**Standalone mode (no `--experiment`):**

```markdown
## Debug Diagnosis

**Hypothesis:** <the hypothesis from Phase 0>
**Root cause:** <description based on observed vs expected>
**Evidence:** <tag X shows Y at step N, but code expects Z>
**Suggested fix:** <specific code change with file + line>

Apply this fix? (y/n/need more investigation -> --continue)
```

- **User says yes:** Apply the fix using Edit tool. Then proceed to Phase 4.
- **User says "need more investigation":** Save history (see below), then proceed to Phase 4. Suggest `--continue` for next round.
- **User says no:** Proceed to Phase 4 only.

**Experiment mode (`--experiment`):**

Skip user interaction. Build and return structured `experiment_result` YAML (schema in `reference.md` Section 6):

```yaml
experiment_result:
  hypothesis: "<from caller>"
  observations:
    - tag: "<tag>"
      value: "<observed>"
      step: <N>
  errors: [...]
  network: [...]
  verdict: "confirmed | unconfirmed | inconclusive"
```

Then proceed to Phase 4.

### Save history (if `--continue` possible)

Write to `.claude/e2e/debug/history/<session_id>-r<round>.yaml` — schema in `reference.md` Section 3.

---

## Phase 4 — Cleanup (MANDATORY)

```
╔══════════════════════════════════════════════════════════════╗
║  ALWAYS EXECUTE — regardless of prior phase outcomes.       ║
║  Phase 2 failed? Still cleanup. Phase 3 skipped? Still      ║
║  cleanup. User aborted? Still cleanup. Only exception:       ║
║  Phase 1 was never reached (no injections were made).        ║
╚══════════════════════════════════════════════════════════════╝
```

Three-layer fallback (detailed procedure in `reference.md` Section 5):

### Layer 1 — Manifest-driven (preferred)

1. Read `.claude/e2e/debug/manifest.yaml`
2. Iterate `injections[]` in **REVERSE order** (LIFO — last injected = first removed)
3. For each injection:
   - Read the file
   - Verify `original_line` is still present near expected location
   - Use Edit tool to remove the `code` line (exact string match)
4. If any Edit fails: fall through to Layer 2

### Layer 2 — Grep fallback

```
Grep for '\[E2E-DBG\]' across cleanup_scope from manifest (default: apps/ src/ lib/)
```

For each match: use Edit tool to remove the entire matching line.

### Layer 3 — Verification

```
Grep for '\[E2E-DBG\]' across apps/ src/ lib/ components/
```

- **0 matches:** Cleanup complete. Delete manifest file and report file.
- **>0 matches:** Alert user with exact file paths + line numbers. Suggest: `git checkout -- <file>` as nuclear option.

### Post-cleanup

- Delete `.claude/e2e/debug/manifest.yaml`
- Delete `.claude/e2e/debug/report.md` (if exists)
- Keep history files (`.claude/e2e/debug/history/`) — needed for `--continue`

---

## D1 Knowledge Capture

After a successful diagnosis (verdict = `confirmed` and fix applied), check if the root cause is generalizable (not project-specific one-off):

**Three-question test:**
1. Could this pattern appear in other projects? (e.g., double-wrapped API response, stale hook dependency)
2. Is the detection method reusable? (which [E2E-DBG] tag pattern reveals it)
3. Is it NOT already in `learned-patterns.md`?

If all three = yes, auto-append to `${CLAUDE_PLUGIN_ROOT}/references/learned-patterns.md`:

```markdown
### [E2E-DBG] <pattern title> (YYYY-MM-DD)
**Symptom**: <what the user sees>
**Root cause**: <what's actually wrong>
**Detection**: <which [E2E-DBG] tag reveals it>
```

---

## Red Flags / Common Mistakes

| # | Mistake | Why it's wrong | Correct approach |
|---|---------|---------------|-----------------|
| 1 | Skipping Phase 4 cleanup | Leaves debug code in production source | Phase 4 is unconditional — always runs |
| 2 | Using `console.error` | Conflicts with agent-browser JS error collection | Always `console.log` |
| 3 | Injecting AFTER the observed line | Log fires after the variable is used, may miss the relevant state | Insert BEFORE the line |
| 4 | Logging without `JSON.stringify` | Objects render as `[object Object]` in console | Always wrap in `JSON.stringify()` |
| 5 | Skipping pre-check grep | May inject on top of residual injections from a crashed session | Always grep for `[E2E-DBG]` first |
| 6 | Too many injection points (>5) | Console noise makes diagnosis harder | 2-5 targeted points per round |
| 7 | Injecting in node_modules or build output | Will be overwritten or ignored | Only inject in source files |
| 8 | Not saving history before cleanup | Loses context for `--continue` | Save history BEFORE Phase 4 |
| 9 | Combining multiple values in one log | Hard to parse which value is which | One `console.log` per data point |
| 10 | Forgetting to create `.claude/e2e/debug/` directory | manifest.yaml write fails | `mkdir -p` at start of Phase 1 |
