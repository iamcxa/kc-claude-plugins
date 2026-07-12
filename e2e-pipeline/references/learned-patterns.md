# Learned Patterns

Accumulated cross-project E2E testing patterns. Auto-read during skill execution, auto-appended after skill completion.

**Source**: Skills with self-improvement capability (e2e-test, e2e-flow, e2e-skill-ops, e2e-walkthrough, e2e-map).

**Format**: Each entry follows D1 entry format from `knowledge-capture.md`.

**PR-back**: Curate locally accumulated patterns → PR to plugin origin repo → all users benefit.

---

## Cross-component sync rule — orchestrator must surface new agent artifacts (2026-03-16)

When an agent adds a feature (new output file, new report section, new artifact type), the orchestrator skill that dispatches it MUST be updated to present the new artifact to the user. Use e2e-skill-ops Impact Matrix during development, not just `--maintain`. Without this, agents produce valuable outputs that the user never sees because the skill's result summary doesn't include them. **Applies to**: any skill-agent pipeline where the agent's output contract expands.

## Shared post-processing subagent pattern (2026-03-17)

When 3+ agents duplicate the same post-processing logic (GIF/MP4/thumbnail generation), extract to a shared subagent dispatched by the orchestrator skill. Key constraint: subagents can't dispatch subagents → the skill must be the dispatch hub. Creates a clean pipeline: browser agent → skill → media agent → skill → trace agent. Without extraction, each agent carries its own ffmpeg/media logic, diverges over time, and bugs must be fixed N times. **Applies to**: any plugin where multiple agents share a common output-processing step.

## Recording startup order matters — record before open (2026-03-16)

`agent-browser record start → open` = 1 window (single context). `open → record start` = 2 windows (orphan + recording context). `record start` can independently launch the daemon. `--profile` is daemon-level, incompatible with recording contexts. Getting the order wrong creates orphan browser windows that consume resources and confuse subsequent commands. **Applies to**: any skill or agent that uses agent-browser recording. Note: as of v2.2.0, step-screenshot-based MP4 replaced `record start/stop` for most flows, but walkthrough still uses recording.

## Symmetric action type design — differentiate by semantics, not structure (2026-03-16)

When adding a paired action type (Execute external vs Verify external), make the schema deliberately symmetric (same structure, different field names) — differentiate by semantics (do vs check), not by structural differences. This makes the compiler, verifier, and test-runner handling consistent: same parsing logic, different execution paths. Asymmetric schemas force each consumer to handle two different shapes for conceptually paired operations. **Applies to**: any flow schema with paired action types (request/response, setup/teardown, trigger/verify).

## Doc scanner misses behavioral branches — snapshot-based detection gap (2026-03-21)

`e2e-doc-scanner` extracts features via surface artifacts: `--flags`, `## headings`, phase definitions, new files. Features implemented as **conditional branches within existing steps** (auto-detect logic, skip conditions, new optional agent fields) are invisible to this model. CLI-only flow support was missed because it had no flag, no heading, no new phase — just a conditional in Discover Mapping step 4. **Fix**: add diff-aware scan mode that compares `git diff` against last version tag. Any new content in SKILL.md or agent .md files gets flagged for doc coverage check, regardless of structural form. Surface extraction remains useful for full audits; diff-aware is essential for incremental doc sync after feature changes.

## Liveness re-check before every Teams command dispatch (2026-04-04)

A teammate can crash between sending `BROWSER_READY` and receiving its first command — the health check window between spawn and first command is the most fragile. Always verify team member presence in `~/.claude/teams/<team>/config.json` immediately before `SendMessage`, not just after spawn. Without this, `SendMessage` to a dead teammate hangs until timeout. **Applies to**: any skill using Agent Teams with pre-warm or idle-wait patterns.

## Crash recovery should preserve partial artifacts (2026-04-04)

When a multi-phase pipeline crashes mid-execution (e.g., verifier timeout, observer crash), already-generated artifacts (flow YAML, reports, partial history) should be kept on disk. Present an error report with the artifact paths and recovery instructions (e.g., `--verify-only`, `--continue`) rather than silently skipping all output or cleaning up everything. **Applies to**: any multi-phase orchestrator where early phases produce reusable outputs.

## Pre-dispatch safety gate for LLM-generated commands (2026-04-04)

When a skill generates shell commands via LLM judgment and dispatches them to a subagent for execution, the skill must validate command safety before dispatch — don't rely solely on the subagent's internal safety checks. The generator and executor should both enforce safety independently (defense in depth). An allowed/blocked pattern list at the skill level catches dangerous commands before they reach the agent. **Applies to**: any skill that generates CLI commands for subagent execution (doc-sync probes, debug experiments).

## Partial MCP degradation over all-or-nothing (2026-04-04)

When a skill depends on multiple independent MCP tools (e.g., journal search + episodic memory + file reads), check each tool's availability independently. Skipping an entire phase because one of N tools is unavailable discards value from the N-1 available tools. Pattern: try each tool, collect results from available ones, note which were unavailable. **Applies to**: any skill with multi-source enrichment phases.

## Exploration mode rationalization bypass (2026-04-04)

When a skill's Role/description emphasizes discovery or exploration, agents rationalize that blocking prerequisites (like mapping existence) don't apply because "exploration doesn't need structure." Anti-rationalization must be co-located with the gate itself, not just in the Role redirect section. If the gate says "mapping required" but the Role says "explore freely," agents cite the Role to skip the gate. **Applies to**: any skill with both structured and exploratory modes sharing a common preamble.

## Missing scan target is a finding, not a skip (2026-04-04)

When a validation matrix references files that don't exist (renamed, removed, never created), agents silently skip the row. But the absence itself is signal — it may indicate a broken reference, incomplete migration, or missing component. Record it as a finding rather than silently skipping. Distinct from "filter-to-zero" (where items exist but are filtered out by context). **Applies to**: any skill with file-based validation matrices or impact tables.

## Startup failure is distinct from mid-flow crash in Teams mode (2026-04-04)

`BROWSER_READY` timeout (startup failure) and mid-command timeout use the same 30s value from `agent-teams.md § 4`, but the failure handling should differ. Startup failure warrants full fallback to subagent mode (the teammate never worked). Mid-flow crash should skip that runner's remaining steps but preserve already-collected results. Skills should distinguish these two failure modes in their error handling. **Applies to**: any skill using Agent Teams with browser teammates.

## CDP resource contention: trace + record causes instability (2026-03-24)

Running `agent-browser trace start` and `record start` simultaneously causes extreme browser instability — timeouts, disconnects, truncated recordings. Root cause: both use the single CDP WebSocket. `record` fires `Page.captureScreenshot` at 10fps (every 100ms), competing with `Tracing.start(recordContinuously)` event stream. **Fix**: remove `record start/stop` entirely. Generate MP4 post-hoc from step screenshots via `e2e-media-processor` (ffmpeg concat, 2s per step). Benefits: (1) stable single CDP channel, (2) `--profile` now works with video (was incompatible with recording contexts), (3) step-paced MP4 is more useful for review than 10fps continuous capture. Trade-off: no real-time video of transitions between steps — but step screenshots capture the meaningful state, and trace.zip has the full interaction timeline for debugging.

## Negative assertions must preserve probe status (2026-07-12)

Never use `|| true` around a probe whose empty output can satisfy a negative assertion. A status-safe negative check has three distinct outcomes: literal `false` means the asserted absence is confirmed, literal `true` may be retried until timeout, and a nonzero command status or any other output is an infrastructure/protocol failure. Snapshot-backed text assertions need the same separation: capture the snapshot status before grepping so a failed snapshot cannot become an empty tree that passes `text-not-visible`. Preserve session arguments when routing probes through shared helpers. **Applies to**: generated tests and wrappers where absence, emptiness, or negation can otherwise convert missing evidence into a pass.

## Validate identifiers before shell code generation (2026-07-12)

Shell-quoting an input at argv boundaries is not sufficient when the same value also becomes part of a variable name, assignment, or parameter expansion. Validate identifier-bearing inputs once at the parser/resolver boundary before generating any code. For shell identifiers, use `^[A-Za-z_][A-Za-z0-9_]*$`, reject prototype-reserved object keys, and detect collisions after normalization to derived environment keys. Retain argv quoting as defense in depth. **Applies to**: aliases, site/session names, environment-variable stems, and other user-defined values used in both data and syntax positions.
