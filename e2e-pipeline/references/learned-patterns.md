# Learned Patterns

Accumulated cross-project E2E testing patterns. Auto-read during skill execution, auto-appended after skill completion.

**Source**: Skills with self-improvement capability (e2e-test, e2e-flow, e2e-skill-ops, e2e-walkthrough, e2e-map).

**Format**: Each entry follows D1 entry format from `knowledge-capture.md`.

**PR-back**: Curate locally accumulated patterns → PR to plugin origin repo → all users benefit.

---

## Doc scanner misses behavioral branches — snapshot-based detection gap (2026-03-21)

`e2e-doc-scanner` extracts features via surface artifacts: `--flags`, `## headings`, phase definitions, new files. Features implemented as **conditional branches within existing steps** (auto-detect logic, skip conditions, new optional agent fields) are invisible to this model. CLI-only flow support was missed because it had no flag, no heading, no new phase — just a conditional in Discover Mapping step 4. **Fix**: add diff-aware scan mode that compares `git diff` against last version tag. Any new content in SKILL.md or agent .md files gets flagged for doc coverage check, regardless of structural form. Surface extraction remains useful for full audits; diff-aware is essential for incremental doc sync after feature changes.

## CDP resource contention: trace + record causes instability (2026-03-24)

Running `agent-browser trace start` and `record start` simultaneously causes extreme browser instability — timeouts, disconnects, truncated recordings. Root cause: both use the single CDP WebSocket. `record` fires `Page.captureScreenshot` at 10fps (every 100ms), competing with `Tracing.start(recordContinuously)` event stream. **Fix**: remove `record start/stop` entirely. Generate MP4 post-hoc from step screenshots via `e2e-media-processor` (ffmpeg concat, 2s per step). Benefits: (1) stable single CDP channel, (2) `--profile` now works with video (was incompatible with recording contexts), (3) step-paced MP4 is more useful for review than 10fps continuous capture. Trade-off: no real-time video of transitions between steps — but step screenshots capture the meaningful state, and trace.zip has the full interaction timeline for debugging.
