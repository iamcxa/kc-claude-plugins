# Pitfalls Research

**Domain:** Adding parallel execution, per-target scheduling, auto PR/Linear creation, and outcomes tracking to existing Bun + Hono + Preact/HTM worker-based dashboard (v2.0 milestone)
**Researched:** 2026-03-21
**Confidence:** HIGH (based on direct codebase inspection of worker/index.ts, executor.ts, scheduler.ts, shared/types.ts, server/ipc.ts, run-store.ts, policy.ts + known project-specific patterns)

> Note: This file covers v2.0 pitfalls only. For v1.0 infrastructure pitfalls (Claude CLI hang, socket cleanup, SSE memory leaks, IPC heartbeat, YAML concurrent writes) and v1.1 UI pitfalls (toast z-index, polling interval leaks, Notification permission), see the commit history for those research files.

---

## Critical Pitfalls

### Pitfall 1: Parallel execution uses a single `activePids` Set — cross-target cancellation kills the wrong process

**What goes wrong:**
`executor.ts` uses `export const activePids = new Set<number>()` as a module-level singleton. In the current serial model (max concurrency 1), there is at most one PID in the set at any time. With parallel execution, multiple `executeRun` calls run simultaneously. When the cancel handler fires `for (const pid of activePids) process.kill(pid, 'SIGTERM')`, it kills ALL active runs across ALL targets — not just the target the user requested to cancel.

**Why it happens:**
The `activePids` Set was designed for a single-run world. The cancel IPC handler in `worker/index.ts:153–157` does `for (const pid of activePids)` — this was correct when only one run could be active. The parallel model invalidates this assumption completely.

**How to avoid:**
- Replace `activePids: Set<number>` with `activePids: Map<string, number>` keyed by `run_id`. The run_id is available at `executeRun` call time.
- Update the cancel handler to look up the specific PID by run_id: `const pid = activePids.get(run_id); if (pid) process.kill(pid, 'SIGTERM')`
- Update `killAllActive()` to iterate the Map values, not the Set.
- Update the `run:started` IPC message to carry `run_id → pid` association so the server can also track it.

**Warning signs:**
- Cancelling a dry-run also kills a production run on a different target running in parallel
- `activePids.size` consistently matches the number of active runs rather than always being 0 or 1
- Test: start two parallel runs, cancel one, verify only one stops

**Phase to address:** Phase 1 (parallel execution refactor). Change `activePids` to a Map before starting any parallel execution work — this is the foundation.

---

### Pitfall 2: Single global queue becomes per-target queues but state snapshot `IpcMessage` still sends one `queue` array — server-side state diverges from worker state

**What goes wrong:**
`worker/index.ts` currently sends `{ type: 'state', queue: [...queue], current: currentRun }` on every state change. The server stores `lastWorkerState` as `{ queue: Run[]; current?: Run }`. With per-target parallelism, there is no single "current run" — there are N current runs, one per target. Sending a flat `queue` array with a single `current` makes the server's state snapshot permanently stale for parallel runs.

**Why it happens:**
The `state` IPC message type was designed for the serial (max-1) model. It maps 1:1 to the UI's "one running + one queue" mental model. Parallel execution requires rethinking the state shape before any UI changes.

**How to avoid:**
- Redefine the state message to carry an `active: Run[]` array (not a single `current?: Run`) plus the full `queue: Run[]` of waiting runs.
- Update `shared/types.ts` `WorkerToServer` union: `{ type: 'state'; queue: Run[]; active: Run[] }` (remove `current` field — it was `Run | undefined`, which is just an array of length 0 or 1).
- Keep the existing `current` field temporarily with a deprecation comment that maps `current = active[0]` for any UI code not yet updated. Remove it once all consumers are migrated.
- Update `getLastWorkerState()` to return the new shape. Update all frontend callers that read `state.current` to handle `state.active`.

**Warning signs:**
- Dashboard shows only one running run even when two are executing in parallel
- "current run" indicator shows undefined while runs are genuinely active
- `GET /api/worker/state` returns `current: undefined` during parallel execution

**Phase to address:** Phase 1 (state shape). Settle the new IPC shape first. Every other parallel execution feature depends on it.

---

### Pitfall 3: Per-target scheduler timers are module-level singletons — replacing the global scheduler leaks old timers

**What goes wrong:**
`worker/scheduler.ts` has `let schedulerTimer: ReturnType<typeof setInterval> | null = null`. There is one timer for one global schedule. The v2.0 feature requires per-target intervals (each target can have its own `interval_hours`). A naive implementation creates N scheduler instances, each holding their own `setInterval`. When a target is updated or removed via the config editor, the old timer is not cleared because the module-level singleton only tracks one timer.

**Why it happens:**
The current `startScheduler` / `stopScheduler` pair assumes single-instance semantics. Calling `startScheduler` for target A, then `startScheduler` for target B would call `stopScheduler()` at the top, which only clears `schedulerTimer` (singular). Target A's timer is gone; target B's timer starts. But if the caller passes each target separately in a loop: `targets.forEach(t => startScheduler(t.config, enqueue))`, the first call starts and immediately `stopScheduler` in the next call kills it.

**How to avoid:**
- Change the scheduler to manage a `Map<string, ReturnType<typeof setInterval>>` keyed by target name.
- `startTargetScheduler(targetName, config, enqueue)` — adds/replaces the timer for that target.
- `stopTargetScheduler(targetName)` — clears only that target's timer.
- `stopAllSchedulers()` — iterates the Map and clears all (used on worker shutdown, replacing `stopScheduler()`).
- `getNextRunAtForTarget(targetName)` — per-target next-run timestamp.
- Keep the global fallback: if a target has no `interval_hours`, apply the global schedule config.
- Minimum interval enforcement (10min) must be applied in `startTargetScheduler`, not in the caller.

**Warning signs:**
- Only one target receives scheduled runs even though multiple have intervals configured
- After editing a target's schedule, the old interval continues firing AND the new one starts (double-fire)
- `clearInterval` is never called on worker shutdown for all timers

**Phase to address:** Phase 2 (per-target scheduling). Refactor scheduler before wiring config UI changes.

---

### Pitfall 4: Multiple concurrent `claude -p` processes under safehouse contend on shared config files — YAML corruption under concurrent writes

**What goes wrong:**
All targets share `~/.claude/kc-plugins-config/` for YAML state files (`nightwatch-targets.yaml`, `nightwatch-runs.yaml`, `nightwatch-improvement-log.md`, etc.). In the serial model, only one `claude -p` process runs at a time. With parallel execution, two `claude -p` processes may simultaneously:
1. Read `nightwatch-improvement-log.md` at phase 0 (signal dedup check)
2. Write new entries to `nightwatch-improvement-log.md` at phase 4 (after taking action)

Concurrent writes to the same YAML/Markdown file without a lock produce interleaved or truncated content. The NW skill uses bash `echo >> file` style appends — these are not atomic on most filesystems.

**Why it happens:**
The skill itself has no concurrency awareness. It was written assuming sequential execution. The `allowed_operations` config in `safety.yaml` controls what operations are allowed but says nothing about ordering or locking. The `yaml-store.ts` in the app does have read-modify-write logic but the skill runs as a separate `claude -p` process with its own file access — not mediated by `yaml-store.ts`.

**How to avoid:**
- `nightwatch-improvement-log.md` — append-only. On most filesystems, appending (O_APPEND) is atomic per-line. Instruct the skill to append entries rather than rewrite. This is already the case. Flag a risk but this is low severity.
- `nightwatch-runs.yaml` — the app controls this via `run-store.ts`. The skill should not write to this file directly. Verify the skill only writes to its own output files (per-target summary.yaml in the run artifact dir).
- High-risk: if the skill writes to any shared file that another concurrent run is simultaneously reading+writing, add a file lock. Use `flock` (available on macOS/Linux) as a shell advisory lock. The worker can acquire the lock before spawning `claude -p` and release it after completion — but this serializes only the locked resource, not the whole run.
- Safest approach: make each run's outputs target-scoped. The skill writes `~/.claude/nightwatch/memory/{target_name}/` (already per-target) and `runs/{run_id}/` (already per-run). The risk area is `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` — verify if the skill writes there directly.

**Warning signs:**
- `nightwatch-improvement-log.md` has truncated entries or entries that appear mid-write (text cuts off mid-line)
- Two runs for different targets report working on the same signal ID on the same day (dedup check failed due to race)
- `yaml.parse()` throws in run-store.ts after a concurrent run (YAML file is invalid)

**Phase to address:** Phase 1 (parallel execution). Audit exactly which files the NW skill writes to. Document safe vs. unsafe concurrent writes before enabling parallelism.

---

### Pitfall 5: Run cleanup (`cleanupOldRuns`) deletes runs from disk while another run is actively writing to the same directory

**What goes wrong:**
`cleanupOldRuns` in `executor.ts:43–66` scans the `runs/` directory and deletes the oldest entries when count exceeds `KEEP_RUNS_COUNT`. With parallel execution, multiple runs exist simultaneously. If run A finishes and triggers cleanup, it might delete the artifact directory for run B which is still actively writing its `log.jsonl`. The `KEEP_RUNS_COUNT = 50` constant means this only occurs after 50 simultaneous-ish runs, but the logic is unsafe regardless.

**Why it happens:**
`cleanupOldRuns` was written for the serial model where only one run is "in progress" at a time. It deletes runs sorted by mtime — the oldest could be a freshly started run with a recent mtime (so it would be safe), but a run that started 28 minutes ago on a different target could have an older mtime and still be running.

**How to avoid:**
- Before deleting a run artifact directory, check if the run_id is in `activePids.keys()` (with the Map change from Pitfall 1). If it is active, skip deletion.
- Alternative: cleanup only at worker startup (before any runs begin), not after each run completes.
- Pass the set of active run IDs to `cleanupOldRuns` and exclude them: `cleanupOldRuns(runsDir, keepCount, activeRunIds: Set<string>)`.

**Warning signs:**
- `log.jsonl` for an in-progress run disappears mid-execution
- `executeRun` throws "ENOENT: no such file or directory" when writing to `log.jsonl`
- Parallel run B's stream SSE returns no events because its log file was deleted

**Phase to address:** Phase 1 (parallel execution). Modify `cleanupOldRuns` signature before enabling parallel execution.

---

### Pitfall 6: Auto PR creation runs `gh pr create` as a subprocess inside `claude -p` — if the repo already has an open PR on the same branch, `gh pr create` fails silently and the outcome is never recorded

**What goes wrong:**
The NW skill's auto-create PR flow calls `gh pr create` on a freshly created branch. If nightwatch ran within the last 7 days and created a proposal branch `kc-nightwatch/2026-03-14-e2e-pipeline-proposal` that was never merged or closed, a subsequent run for the same target + signal will try to create the same-named branch (or re-use it). `gh pr create` on an existing open PR returns exit code 1 with "a pull request for branch X already exists". The skill treats this as a failure and may not record the outcome.

**Why it happens:**
The cooldown mechanism (`cooldown_per_signal: 7d`) prevents re-processing the same signal within 7 days. But the cooldown is checked against the signal ID in `improvement-log.md`, not against open PR status. If a PR is created but the user never reviews it (leaves it open), the signal re-enters cooldown after 7 days and a new run might attempt to re-create the branch.

**How to avoid:**
- Before calling `gh pr create`, run `gh pr list --head {branch_name} --json url` to check for existing PRs. If one exists, skip creation and return the existing PR URL as the outcome.
- This check is cheap (one `gh` call) and prevents the failure path entirely.
- In the outcomes tracking system (Phase 0.6), treat "PR already exists" as a valid outcome state — not a failure. The outcome card should link to the existing PR.
- The NW skill should emit a structured outcome even on "PR already exists" so the dashboard can surface it.

**Warning signs:**
- `gh pr create` exits non-zero inside a run but the skill continues silently
- Outcomes page shows no PR link for a target that clearly had changes proposed
- `improvement-log.md` has an action entry but `actions[].pr_url` is empty

**Phase to address:** Phase 3 (auto PR creation). Add the pre-flight `gh pr list` check before any `gh pr create` call.

---

### Pitfall 7: Auto Linear issue creation fires on every run for the same unresolved signal — creates duplicate issues

**What goes wrong:**
Phase 3 auto-creates Linear issues from improvement signals. If the NW skill runs every 24 hours for the same target and signal X has `action_type: linear-issue` but the issue has never been resolved (it stays open in Linear), the next day's run sees the same signal again (cooldown has not expired or the signal is recurring), creates another Linear issue, and the user now has 7 duplicate issues for the same root problem over a week.

**Why it happens:**
Linear issue creation is treated as a "fire and forget" action in the current feedback model. The feedback collection only tracks PR merge status (`collectImplicitFeedback` checks `pr_url`), not Linear issue resolution status. Without checking whether an open issue already exists, every run that triggers this signal creates a new issue.

**How to avoid:**
- Before creating a Linear issue, search for existing open issues with the same title or signal ID label. The Linear MCP exposes search capability. Use it.
- Use a consistent issue title template: `[NW] {signal_summary} [{target_name}]`. The `[NW]` prefix + target name makes dedup searchable.
- Record created issue URLs in `improvement-log.md` alongside signal entries. On subsequent runs, if a signal matches a log entry with an existing `linear_url` that is still open (check Linear status), skip creation.
- The `kc-nightwatch-feedback.yaml` + `collectImplicitFeedback` mechanism already tracks `linear_status`. Extend it to gate issue creation: if a previous issue for this signal is still open, do not create another.

**Warning signs:**
- Linear project shows 5+ issues with nearly identical titles for the same target
- `improvement-log.md` has multiple entries for the same signal_id with `linear_url` fields pointing to different issue URLs
- User feedback rate in `feedback.yaml` spikes (user rejecting duplicates)

**Phase to address:** Phase 3 (auto Linear creation). Implement dedup check before issue creation, using improvement-log.md as the source of truth for existing issues.

---

### Pitfall 8: Per-target scheduling IPC message carries a single `ScheduleConfig` — updating one target's schedule resets all others

**What goes wrong:**
The current `schedule` IPC message type is `{ type: 'schedule'; config: ScheduleConfig }` carrying a single global config. The server sends this when the schedule changes. With per-target scheduling, updating target A's interval must not affect target B's active timer. But if the server sends `{ type: 'schedule'; config: globalConfig }` and the worker calls `startScheduler(config, enqueue)` which first calls `stopScheduler()` — all per-target timers are wiped and only the global fallback is restarted.

**Why it happens:**
The `schedule` IPC message was designed for a single config object. The server's schedule route likely re-reads the config and sends the updated global schedule. Per-target scheduling requires either (a) a new `schedule:target` IPC message type, or (b) sending the full targets map when any schedule changes so the worker can reconcile all per-target timers.

**How to avoid:**
- Add a new IPC message type: `{ type: 'schedule:target'; target_name: string; config: ScheduleConfig }` that updates only the named target's timer.
- When the config editor saves changes, identify which fields changed (global schedule vs. per-target interval) and emit the appropriate IPC message.
- Worker handles `schedule:target` by calling `startTargetScheduler(msg.target_name, msg.config, enqueue)` which replaces only that target's timer.
- Keep `schedule` (global) working for the "enable/disable all scheduling" toggle.

**Warning signs:**
- After updating target B's schedule in the config editor, target A's runs stop occurring on their expected interval
- Worker log shows `Scheduler stopped` followed by only one target being scheduled instead of all targets
- `getNextRunAt()` returns the global interval time even though a target has a custom shorter interval

**Phase to address:** Phase 2 (per-target scheduling). Extend IPC message types before wiring the scheduler refactor.

---

### Pitfall 9: SSE log streaming sends all parallel run logs to `/api/runs/:id/stream` but the worker sends `run:log` IPC without associating it clearly to the correct `run_id` under high parallelism — log lines interleave

**What goes wrong:**
`executor.ts` calls `opts.onMessage({ type: 'run:log', run_id: run.id, event })` for every log line. The server's `handleWorkerMessage` routes this to `fanOutLogEvent(msg.run_id, msg.event)`. This looks correct, but the actual bottleneck is in the worker's IPC channel itself: all runs share a single `process.send()` channel. Under parallel execution, multiple `executeRun` calls concurrently push `run:log` messages onto the same IPC channel. Bun/Node IPC serializes these messages in arrival order, which means log events from run A and run B are interleaved in the channel. The server correctly demultiplexes them by `run_id`, but if the IPC channel's backpressure causes message drops (unlikely but possible at high log volume), the stream for a specific run may silently miss lines.

**Why it happens:**
The current design works correctly for the serial case because only one run generates log events at a time. The parallel case sends N times more events through the same single IPC channel. The risk is low (Bun's IPC has a large internal buffer) but worth understanding.

**How to avoid:**
- This is NOT a rewrite-forcing problem. The existing design is architecturally correct for parallel use — `run_id` is the demultiplexer.
- Monitor IPC message throughput during parallel runs in development. If log events are dropped, add a `seq: number` field to `run:log` messages so the client can detect gaps.
- The real risk is the opposite: the SSE writers for different run streams write concurrently to `stream.writeSSE()`. Hono's streaming handles this per-connection, so two separate browser tabs watching two different run SSE streams are safe. One browser watching run A's stream will not see run B's events.
- Set up a test: run two targets in parallel, open both streams in two browser tabs, verify no cross-contamination.

**Warning signs:**
- Browser watching `/api/runs/{A}/stream` sees log lines with `run_id: B` in the payload
- Log viewer shows phases from a different target mid-stream
- IPC channel log shows `[warn] IPC send buffer full` (Bun internal message)

**Phase to address:** Phase 1 (parallel execution). Add the `run_id` correctness assertion to the test suite early.

---

### Pitfall 10: `AppConfigSchema` has `max_concurrent_runs: z.literal(1)` — adding parallel execution requires a schema migration that existing config files will fail

**What goes wrong:**
`shared/types.ts:62` has `max_concurrent_runs: z.literal(1)`. This Zod schema validates the app config YAML and will reject any value other than `1`. When v2.0 adds parallel execution, the config needs to express per-target concurrency (or drop this field entirely). Any user running with an existing `app-config.yaml` that has `max_concurrent_runs: 1` will have that config fail validation if the schema changes to `z.number().min(1)` without a compat migration.

**Why it happens:**
The field was added as a `z.literal(1)` to explicitly document the current constraint. It was not meant to be user-configurable — it documented an architectural decision. But it exists in the config YAML, so it has a migration story.

**How to avoid:**
- Per-target concurrency is not a single `max_concurrent_runs` number — it is "different targets run in parallel; same target queues". This cannot be expressed as a simple integer.
- Remove `max_concurrent_runs` from `AppConfigSchema` entirely in v2.0. The behavior is now "unlimited cross-target concurrency, per-target serial queue" — this is an architectural property, not a config value.
- For migration: use `z.coerce.number().optional()` during a transition period that reads (and ignores) the old value without failing. Then remove it.
- Add a migration step at startup: if `max_concurrent_runs` exists in the loaded config, log a deprecation warning and ignore it.

**Warning signs:**
- App fails to start after v2.0 upgrade with "ZodError: invalid_literal" on `max_concurrent_runs`
- Existing users who have explicitly set `max_concurrent_runs: 1` in their config get startup failure
- `bun typecheck` shows `AppConfig` type as changed but the config loading code still expects the old shape

**Phase to address:** Phase 1 (parallel execution). Remove or migrate the schema before any other work — it is a compile-time blocker.

---

### Pitfall 11: Outcomes tracking (`ImplementationOutcome`) writes before-value at PR creation time and after-value at "next measurement" — but the measurement happens in the same run that processes the outcome, creating a chicken-and-egg problem

**What goes wrong:**
`shared/types.ts` defines `ImplementationOutcome` with `before: number`, `after: number`, `delta: number`. The "before" value is the indicator baseline measured at Phase 0.5 when the PR was proposed. The "after" value should be measured N days after the PR is merged. But the current pipeline design runs Phase 0.5 (measure) at the start of every run — meaning the "after" measurement is taken by the same run that might also be proposing new changes. If the PR was merged 2 days ago and the indicator improved, the "after" value is captured, the delta is computed, and a new signal from the indicator (still above threshold) might immediately trigger another proposal in the same run.

**Why it happens:**
The pipeline phases run sequentially: 0.5 (measure) → 1 → 2 → 3 → 4. Phase 0.6 (outcomes) was designed to happen after 0.5 but before 1. However, if Phase 0.6 sees that a PR was merged and the indicator improved, it marks the outcome as effective — but the signal from that indicator has already been harvested in Phase 1 and may still trigger a new action in Phase 4.

**How to avoid:**
- Phase 0.6 should run AFTER Phase 1 (signal harvest) but BEFORE Phase 2 (dedup). This way, if Phase 0.6 marks an indicator as "recently resolved by merged PR", Phase 2 can suppress signals for that indicator using a short cooldown.
- Add a `recently_resolved` flag to the cooldown check: if an indicator has a merged PR within the last N days (e.g., 14d), signals from that indicator get a longer cooldown automatically.
- Do not measure "after" in the same run that proposes new changes. The "after" measurement should be gated: only measure if the PR was merged at least `min_measurement_window` days ago (e.g., 3d). If the window has not passed, record `after: null` and defer.

**Warning signs:**
- Outcomes page shows "effective: true" but a new proposal for the same indicator is created in the same run
- `improvement-log.md` shows two consecutive actions for the same indicator within a single run
- A merged PR that fully fixed an issue triggers 3 more proposals before the outcomes tracking catches up

**Phase to address:** Phase 4 (outcomes tracking / Phase 0.6). Define the pipeline ordering explicitly before implementing.

---

### Pitfall 12: Multiple concurrent safehouse processes each launch their own `agent-browser` daemon on the same profile — they collide

**What goes wrong:**
The safehouse policy includes agent-browser access via `--enable=agent-browser` (from MEMORY.md: alias `cc` uses `--enable=shell-init,agent-browser`). If two concurrent `claude -p` processes both have agent-browser enabled and both try to launch the browser daemon on the same user profile, they get a collision on the daemon socket or the profile lock file. The second process's browser calls fail or silently use a shared (dirty) browser context.

**Why it happens:**
agent-browser uses a profile-based daemon model. The daemon is started per-profile. If two NW processes both have `--enable=agent-browser`, both call the same daemon start sequence and may conflict.

**How to avoid:**
- The NW skill does NOT need agent-browser — it uses `gh` CLI, Linear MCP, and git. Remove `--enable=agent-browser` from the safehouse flags used by the worker (check `buildSafehouseFlags` in `policy.ts`).
- Currently `policy.ts` does not pass `--enable=agent-browser` — this is correct. The risk is if someone adds it later as a "nice to have". Document this explicitly in `policy.ts` as a comment: "Never add agent-browser here — concurrent NW runs collide on the browser daemon."
- If a future NW feature genuinely needs browser access (e.g., scraping a metrics page), it must use a per-run browser profile via `--profile=nw-{run_id}` and clean it up after.

**Warning signs:**
- `claude -p` for a NW run hangs at "Starting agent-browser daemon" while another run is already using the browser
- Two runs both succeed but one has all-empty browser action results
- `ps aux | grep agent-browser` shows two daemon processes for the same profile

**Phase to address:** Phase 1 (parallel execution). Add a comment to `policy.ts` before parallelism is enabled. Run a quick audit that agent-browser is not in the safehouse flags.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Keep `current?: Run` in state IPC message alongside new `active: Run[]` | No UI code changes needed immediately | Server and UI drift: some code uses `current`, some uses `active[0]` — both track the same thing inconsistently | Only acceptable as a temporary compat shim for 1 phase. Remove in phase following migration. |
| Use one global queue for all targets, dequeue by round-robin | Simpler than per-target queues | "Same target queues" constraint becomes impossible to enforce without scanning the whole queue for same-target runs | Never — the constraint requires per-target queue tracking from day one |
| Skip dedup check before `gh pr create` | 5 fewer lines of code | Creates duplicate PRs on re-runs; user trust erodes fast | Never — always pre-flight check |
| Store `ImplementationOutcome` only in `summary.yaml` (per-run artifact) | No persistent store changes | Outcomes are lost when run is cleaned up after `KEEP_RUNS_COUNT` is exceeded (50 runs ≈ ~2 months at current cadence) | Never for outcome data — outcomes must persist in a separate store beyond run artifact lifecycle |
| Auto-create Linear issues without a title dedup search | Faster to implement | Duplicate issues accumulate; user becomes noise-immune (stops checking Linear) | Never — the Linear API search is cheap and the downside is catastrophic for trust |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| GitHub CLI (`gh pr create`) | Assuming `gh` is auth'd in the safehouse context | The safehouse restricts env vars. Verify `GH_TOKEN` or `~/.config/gh/hosts.yml` is accessible. The safehouse `--add-dirs-ro` for `~/.config/gh` may need to be added to `buildSafehouseFlags`. |
| Linear MCP (`linear_*` tools) | Hardcoding the MCP tool name prefix (e.g., `linear_createIssue`) | Use `ToolSearch "+linear save"` to discover the actual prefix at runtime — tool names vary by MCP server version. This pattern is already documented in MEMORY.md (kc-sentry-insight). |
| Linear MCP issue creation | Creating an issue without a `team` ID | Linear issues require a team. Always resolve the team ID at Phase 0 from the target's config (not hardcoded). See kc-nightwatch v0.3.0 lesson: `team` required, not just `project`. |
| `gh` CLI inside safehouse | `gh pr list` fails if the repo's git remote is not accessible | safehouse may block network in some configurations. Verify that `gh` API calls work from within a safehouse-wrapped `claude -p`. Test with a dry-run that calls `gh repo view`. |
| Bun IPC (`process.send`) under parallel load | Sending hundreds of `run:log` messages per second per run × N parallel runs | IPC is synchronous in the sense that `process.send()` enqueues the message. The channel does not block, but very high throughput may cause the child process to slow down if the parent's IPC handler is blocking. Keep `handleWorkerMessage` non-blocking (already the case). |
| YAML concurrent reads via `yaml-store.ts` | `readYamlFile` + `writeYamlFile` are not atomic | The existing `yaml-store.ts` does read-then-write without a lock. For files written only by the app (not by the NW skill processes), this is safe because the app is single-threaded (Bun event loop). For files written by NW skill processes too, there is a TOCTOU window. |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| N parallel `claude -p` processes each read `nightwatch-targets.yaml` at startup | N reads × N runs per day = O(N²) file reads | Worker caches `targetsMap` at startup (already done in `worker/index.ts:29–35`). Runs use the cached map, not re-reading on each spawn. | Not a current concern — already cached. Risk if someone adds `readTargets()` inside `executeRun`. |
| SSE fan-out for N parallel runs multiplied by M browser subscribers | M browsers × N runs × log event rate = quadratic SSE writes | `sseSubscribers` Map already isolates per run_id. SSE writes are fire-and-forget. Issue only arises if many runs are streaming simultaneously to many open browser tabs. | Not a concern at current scale (1 user, <10 parallel targets). |
| `cleanupOldRuns` stat() calls for all run dirs on every run completion | N parallel completions each trigger `Bun.Glob.scan()` + `stat()` × total_dirs | Move cleanup to worker startup only (not post-run). Or rate-limit cleanup to once per hour. | Breaks when parallel run completions fire simultaneously and each triggers a cleanup scan. |
| Linear MCP search for dedup before every issue creation | One API call per issue-creation attempt, may add 2–3s per run | Acceptable — issue creation is rare (1–3 per run). Linear API p95 < 1s. | Not a concern unless a run creates >20 issues (would indicate config miscalibration, not a perf issue). |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| PR description includes the full NW skill prompt context | Sensitive system-level instructions (skill contents) visible in public GitHub PRs | Only include the improvement description and diff summary in PR body. Never include `--append-system-prompt` content in the PR. |
| Linear issue title echoes the signal content verbatim, which may include internal commit messages or file paths | Internal codebase structure leaked to Linear (project management tool, potentially accessible to more people) | Sanitize: include only the high-level summary and indicator name. Strip file paths. |
| Per-run MCP config (`nw-journal.json`) in `runs/{id}/` is readable by any process with `runs/` access | `runs/` is an artifact dir, not a secrets dir. The journal MCP config includes the journal path but no auth tokens — low risk | Keep current behavior. Do not add secrets to per-run MCP configs. |
| `auth_token` for remote mode dashboard is passed as an env var to `claude -p` subprocess | Could leak to subprocesses | Auth token is for the Hono server only, not forwarded to spawned processes. Verify `buildSafehouseFlags` and `claudeArgs` in `executor.ts` do not include `auth_token`. |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Outcomes page shows all PRs/issues ever created with no grouping | 50+ rows with no context; user cannot tell what helped vs. what failed | Group by target, then by status (open/merged/closed). Show indicator improvement delta prominently for merged PRs. |
| Auto-created PR title is generic ("NW improvement for e2e-pipeline") | User cannot distinguish improvements without reading each PR | Include the signal summary and indicator in the title: "[NW] Reduce test flakiness: fix race in e2e-flow-verifier (test_reliability)" |
| NW-Claude chat says "I don't know about PR #123" when user asks about an outcome | Breaks trust in the AI assistant | NW-Claude must have access to outcomes data. Wire the MCP tool `get_outcomes` to `ImplementationOutcome[]` before the chat panel is connected. |
| Parallel runs all show as "running" simultaneously in target list — no visual distinction | User cannot tell which run is far along vs. just started | Show phase progress per target. Parse `phase` field from `ParsedLogEvent` (already populated in `log-parser.ts`) and expose it in per-target state. |
| Auto-created issues/PRs appear with no link in the dashboard until the run completes | User triggers a run; 30 min later sees a PR was created but had no visibility during execution | Emit a `run:action-created` IPC message when the skill creates a PR/issue mid-run. Display it in the live log view. |

---

## "Looks Done But Isn't" Checklist

- [ ] **Parallel execution**: Cancel one target's run while another target's run is ongoing. Verify only the cancelled target's process is killed (`ps aux | grep claude` before and after).
- [ ] **Per-target scheduler**: Set target A to every-2h and target B to every-3h. After 6h, A should have fired 3 times and B should have fired 2 times. Check `nightwatch-runs.yaml` counts.
- [ ] **Auto PR dedup**: Run NW twice in quick succession on the same target without merging the first PR. Second run should NOT create a second PR. Verify `gh pr list` shows only one open PR.
- [ ] **Auto Linear dedup**: Trigger two runs for the same target with the same unresolved signal. Linear project should show exactly one open issue, not two.
- [ ] **Outcomes tracking after merge**: Merge a NW-created PR. Next run should measure the "after" indicator value and record `delta`. Verify `effective: true/false` is set in `implementation_outcomes`.
- [ ] **Config schema migration**: Start the app with an existing `app-config.yaml` that has `max_concurrent_runs: 1`. App should start without error (field silently ignored or migrated).
- [ ] **Run cleanup safety**: Start 3 parallel runs; the moment the first completes, verify its run dir is NOT deleted if 2 others are still active.
- [ ] **GitHub auth in safehouse**: Run `gh repo view` from within a safehouse-wrapped process with the same flags used by `buildSafehouseFlags`. Verify exit 0.
- [ ] **NW-Claude outcomes awareness**: Ask "Did the PR for e2e-pipeline test flakiness actually help?" in the NW-Claude chat after a merged PR outcome exists. Verify the answer references the specific delta.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| `activePids` Set cancels wrong process | LOW | Add `activePids` → Map change. Already isolated to `executor.ts` — no cascading changes except the cancel handler in `worker/index.ts`. |
| Duplicate Linear issues created | MEDIUM | Manually close duplicates in Linear. Add `linear_url` field to `improvement-log.md` entries retroactively by running a migration script against the YAML. Then add dedup check to skill. |
| Scheduler timer leak (old timer not cleared) | LOW | Worker restart clears all timers. Add `stopAllSchedulers()` call to the existing `shutdown` IPC handler which already calls `stopScheduler()`. |
| YAML corruption from concurrent writes | HIGH | Restore from git history (improvement-log.md and targets.yaml are in `~/.claude/kc-plugins-config/` which is not git-tracked — manual recovery or last-known-good from `safety.yaml` `backup_before_fix: true` backup). Prevention is far cheaper than recovery. |
| Outcomes store cleaned up with run artifacts | MEDIUM | Move `implementation_outcomes` to a dedicated persistent YAML file (e.g., `nightwatch-outcomes.yaml` alongside `nightwatch-runs.yaml`). Running `cleanupOldRuns` only deletes `log.jsonl` artifacts, not outcomes. |
| `max_concurrent_runs: z.literal(1)` startup failure after upgrade | LOW | Remove the field from `app-config.yaml` manually, or add the schema migration code to the startup path. |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| `activePids` Set cancels wrong process in parallel | Phase 1 (parallel execution refactor) | Cancel test: kill one target, verify other is unaffected |
| Single `current` in IPC state breaks parallel visibility | Phase 1 (state IPC shape) | Worker state endpoint shows all active runs, not just one |
| Scheduler timer module singleton leaks on per-target config | Phase 2 (per-target scheduling) | Multiple targets have distinct `setInterval` handles; stopping one leaves others running |
| Shared YAML files written concurrently without locks | Phase 1 (parallel execution) | Audit which files NW skill writes; add guards before enabling parallelism |
| `cleanupOldRuns` deletes active run artifacts | Phase 1 (parallel execution) | Start N parallel runs; cleanup skips all active run dirs |
| `gh pr create` on existing open PR fails silently | Phase 3 (auto PR creation) | Pre-flight `gh pr list` check; second run for same target reuses existing PR URL |
| Duplicate Linear issues from re-runs | Phase 3 (auto Linear creation) | `improvement-log.md` lookup gates creation; only one issue per open signal |
| Schedule IPC wipes all per-target timers | Phase 2 (per-target scheduling) | Updating target A schedule leaves target B timer unchanged |
| SSE log cross-contamination under parallel load | Phase 1 (parallel execution) | Integration test: two parallel runs, two SSE streams, zero cross-contamination |
| `max_concurrent_runs: z.literal(1)` startup failure | Phase 1 (parallel execution) | Existing `app-config.yaml` with old field starts cleanly after migration |
| Outcomes chicken-and-egg with same-run signal harvest | Phase 4 (outcomes tracking) | Merged PR outcome does not trigger new proposal in same run |
| agent-browser daemon collision from concurrent safehouse | Phase 1 (parallel execution) | Verify `policy.ts` buildSafehouseFlags has no `--enable=agent-browser` |

---

## Sources

- Direct codebase inspection: `worker/index.ts`, `worker/executor.ts`, `worker/scheduler.ts`, `worker/policy.ts`, `server/ipc.ts`, `server/routes/api.ts`, `server/services/run-store.ts`, `shared/types.ts`, `shared/constants.ts`, `config/safety.yaml`
- MEMORY.md: known project-specific patterns — NW skill Linear team requirement (v0.3.0), `ToolSearch` for MCP prefix discovery (kc-sentry-insight), agent-browser profile collision risk, Bun IPC child-to-parent verified working, YAML concurrent write risk in yaml-store.ts
- Known project decisions (PROJECT.md): "Per-target isolation — different targets concurrent, same target queued" as the explicit v2.0 concurrency model
- GitHub CLI `gh pr create` exit-code behavior: HIGH confidence (standard `gh` behavior, documented in gh CLI docs)
- Linear issue dedup pattern: MEDIUM confidence (based on kc-sentry-insight's `date-based cleanup over consecutive-count` lesson in MEMORY.md, applied to issue creation)
- Bun IPC throughput under load: MEDIUM confidence (Bun docs state IPC uses Node-compatible message passing; no official throughput limits documented; empirical evidence from existing NW runs)

---
*Pitfalls research for: Nightwatch Dashboard v2.0 (parallel execution, per-target scheduling, auto PR/Linear creation, outcomes tracking)*
*Researched: 2026-03-21*
