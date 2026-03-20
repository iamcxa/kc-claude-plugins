# Doc-Sync Templates

Template components scaffolded by forge during Phase 1.5 (Autonomy Decision → B: Doc Self-Iteration).
Three components: skill, agent, reference. Forge replaces `{{PLUGIN_NAME}}` with the actual plugin name at scaffold time.

## Template: Skill SKILL.md

Full variant (all 6 phases active). For Light variant: replace Phase 4 content with the Light Phase 4 block at the bottom.

```
---
name: {{PLUGIN_NAME}}-doc-sync
description: >
  Use when plugin documentation needs updating after feature changes,
  when verifying existing docs accurately reflect actual skill/agent behavior,
  or for periodic documentation maintenance. Scans source code, enriches
  with usage history from journal and memory, writes or updates docs,
  then verifies accuracy via live behavioral probes.
---

# {{PLUGIN_NAME}}-doc-sync

## Routing

| Input | Route |
|-------|-------|
| bare invocation | → Full Sync |
| `--check` | → Report Only |
| `--probe-only` | → Verify Existing Docs |
| `--auto` | → Full Sync (skip confirmation) |
| `--section <doc-file>` | → Targeted Sync (one doc file) |

## Phase 1: Static Scan

1. Read `reference/doc-sync-context.md` → load Source Map, Doc Structure, Probe Config, Post-Sync Hooks
2. Inventory source files:
   - Glob `skills/*/SKILL.md` → for each: extract skill name, description, all `--flags`, modes (from routing tables), key concepts
   - Glob `agents/*.md` → for each: extract agent name, tools, input contract fields, dispatch trigger
   - Glob `hooks/` → for each: extract event type, trigger condition, affected tools
3. Inventory documentation:
   - Glob `docs/*.md` + `README.md` → for each: extract title, section headings, mentioned features, example count
4. Cross-reference: for each Source Map entry, search its Doc Target for coverage of every extracted feature
5. Classify gaps:
   - **Critical**: source feature exists, zero mention in any doc
   - **Warning**: mentioned in one doc but not explained (e.g., flag listed in table but no usage guide)
   - **Info**: documented but could be improved (missing example, stale cross-reference)
6. Meta-doc consistency check: verify CLAUDE.md skill/agent counts, README docs table completeness, plugin.json description accuracy

If `--section <doc-file>`: filter Source Map to entries targeting that doc file only.

Output: gap_report + feature_inventory

## Phase 2: History Enrichment

**Prerequisite**: MCP tools `episodic-memory` and `private-journal`. If unavailable, skip Phase 2 with warning: "History enrichment skipped — MCP tools unavailable. Running static-only mode." Proceed to Phase 3 with unenriched gaps.

1. Search episodic memory: `search("{{PLUGIN_NAME}}")` → extract usage patterns, user workflows, reported issues
2. Search journal: `search_journal("{{PLUGIN_NAME}}")` → extract technical insights, debug findings, failed attempts
3. Read MEMORY.md → extract known plugin knowledge entries
4. Enrich each gap:
   - History mentions this feature with usage context? → add context to gap (improves doc writing quality)
   - History contradicts current docs? → escalate gap to `accuracy_risk` (priority for probe verification)
5. Features found in history but NOT in gap report → add as new Info-level gap ("undocumented but used")

If `--check`: skip to Phase 6 after this phase.

Output: enriched_gaps

## Phase 3: Write / Update Docs

Unless `--auto`, present enriched_gaps grouped by severity (Critical first):
- **approve all (a)**: proceed with all gaps
- **select (s)**: pick which gaps to address
- **edit (e)**: modify proposed doc outline for a specific gap before writing
- **quit (q)**: abort, skip to Phase 6

For each approved gap:

1. Determine action: **CREATE** new doc file or **UPDATE** existing section
2. If UPDATE:
   - Read full target doc file
   - Locate target section (guided by Source Map)
   - Check `auto-sync` flag in Doc Structure:
     - `yes` → rewrite section entirely from source
     - `partial` → edit only the specific subsection, preserve hand-written content
   - Apply changes via Edit tool
3. If CREATE:
   - Read one sibling doc file for style calibration (tone, structure, heading conventions)
   - Follow Style Guide from `doc-sync-context.md`
   - Write complete doc with sections derived from source features
4. After all writes:
   - Sync index files: update README.md docs table if new files created
   - Meta-doc consistency: update CLAUDE.md counts if skill/agent inventory changed

## Phase 4: Live Probe

**Skip if**: doc-probe agent was not scaffolded (Light variant) or `--check` mode.

1. **Extract behavioral claims** — Read each doc written/updated in Phase 3. Identify sentences asserting observable behavior ("X shows Y", "when you run X, Y happens", "X supports Y"). For each claim, generate structured claim object: assertion text, probe command (from Probe Config), expected output signals. This is LLM judgment, not regex.
2. Filter claims to `method: cli` only (skip claims for skills marked `skip` in Probe Config)
3. Write claims to `/tmp/{{PLUGIN_NAME}}-doc-probe/claims.json`
4. Dispatch `doc-probe` agent:
   - plugin_root: `${CLAUDE_PLUGIN_ROOT}` (standard Claude Code env var, auto-available in plugin skill context)
   - claims_path: `/tmp/{{PLUGIN_NAME}}-doc-probe/claims.json`
   - report_dir: `/tmp/{{PLUGIN_NAME}}-doc-probe/report`
5. Read `probe-results.json`:
   - All pass → proceed to Phase 5
   - Any `fail`:
     a. Read source code for the failing skill to understand actual behavior
     b. Fix the doc to match actual behavior (docs conform to code)
     c. Re-extract claims for fixed sections only
     d. Re-dispatch probe (max 3 total rounds — if still failing after 3, log and move on)
   - `error:env_dependent` → log, don't retry, note in report
   - `error:crash` → log, suggest manual investigation

If `--section <doc-file>`: only extract claims from that doc file.

## Phase 5: Self-Update Reference

1. Compare current skills/agents/hooks inventory (from Phase 1) vs `doc-sync-context.md`
2. New source files found → append to Source Map with inferred Doc Target
3. Removed source files → mark as deprecated in Source Map (warn user, don't auto-delete)
4. New skills → classify probe safety using Probe Safety Heuristic → add to Probe Config
5. Skills that probed as `error:env_dependent` → update Probe Config to `skip` (self-correcting)
6. Update frontmatter: `last_sync` date, `version` to current plugin version

## Phase 6: Report + Knowledge Loop

1. Output summary:
   | Metric | Value |
   |--------|-------|
   | Gaps found | N |
   | Gaps fixed | N |
   | Accuracy risks found | N |
   | Probes run | N |
   | Probe pass rate | N% |
   | Docs created | N |
   | Docs updated | N |
   | Reference self-updated | yes/no |

2. D1 learning: check for reusable patterns worth capturing:
   - Probe found mismatch static scan missed → doc described removed/changed feature
   - History enrichment found risk confirmed by probe → user-reported issue validated
   - New skill had no doc coverage → expansion rule for doc structure
   - Retry loop needed >1 round → initial generation quality insight
   If pattern found and plugin has D1 evolution enabled → append to `reference/learned-patterns.md`

3. Auto-issue: if unfixed gaps remain (user declined, env_dependent probes, crash errors):
   - Offer to create GitHub issue with gap details
   - Format: title = "Doc sync: N gaps remaining", body = gap list with severity

4. Post-sync hooks: read and execute plugin-specific actions from `doc-sync-context.md` Post-Sync Hooks section

## Rules

- **Docs conform to Code** — when behavior and docs disagree, fix the docs, not the code
- **Probe Config is optimistic** — default to `cli`, let `env_dependent` self-correct to `skip`
- **Phase 2 graceful degradation** — MCP unavailable → skip history, run static-only
- **Max 3 probe rounds** — prevent infinite fix→probe loop
- **Preserve hand-written content** — check `auto-sync` flag before overwriting
- **Report first, fix second** — `--check` and `--probe-only` never write docs
```

## Light Phase 4 Block

Replace Phase 4 in the template above with this for Light variant:

```
## Phase 4: Live Probe

> Doc-probe agent not scaffolded (Light variant). Live probing disabled.
> To enable: run `/kc-plugin-forge <plugin-path>` and select Full for Doc Self-Iteration.

Skip this phase.
```

## Template: Agent doc-probe.md

```
---
name: doc-probe
description: >
  Verifies documentation accuracy by executing live probes against plugin skills.
  Receives behavioral claims extracted from docs, runs each probe command,
  compares output against expected signals, returns structured pass/fail report.
  Dispatched by {{PLUGIN_NAME}}-doc-sync skill during Phase 4 (Live Probe).
model: sonnet
tools:
  - Bash
  - Read
  - Grep
  - Write
---

You are a documentation accuracy verifier. Your job is mechanical: execute probes, compare outputs, report results.

## Input

Read `{claims_path}` for the list of claims to verify. Each claim has:
- `id`: unique identifier
- `source_doc`: which doc file makes this claim
- `section`: which section
- `claim`: human-readable description of the claimed behavior
- `probe.method`: "cli" or "skip"
- `probe.command`: the command to execute
- `probe.timeout`: max seconds (default 30)
- `expected`: list of strings that should appear in output

## Execution Protocol

For each claim where method = "cli":

1. **Safety check**: Reject if command contains destructive patterns
   (rm, delete, push, --force, reset, drop). Mark as `skipped: unsafe`.

2. **Execute**: Run via Bash with timeout.
   - If command starts with `claude -p`: add `--no-input` flag if not present
   - Add `--plugin-dir {plugin_root}` if not present
   - Capture stdout, stderr, exit code
   - Wait 2 seconds between probes to avoid rate limiting

3. **Compare**: For each expected signal, case-insensitive search in
   combined stdout+stderr.
   - All found → pass
   - Partial → fail (list which signals missing)
   - Command errored → classify:
     - timeout → error:timeout
     - exit code != 0 + stderr mentions missing file/dir/not found → error:env_dependent
     - exit code != 0 + other → error:crash

4. **Do NOT interpret or fix**: You report, you don't diagnose.
   The skill handles remediation.

## Output

Write `{report_dir}/probe-report.md`:

```markdown
## Probe Report

| # | Claim | Doc | Result | Details |
|---|-------|-----|--------|---------|
| 1 | ... | ... | ✅ pass / ❌ fail / ⚠️ error / ⏭️ skipped | ... |

### Failures Detail

(For each fail/error, include: claim text, actual output excerpt, classification)

### Summary
- Total: N claims probed
- Pass: N, Fail: N, Error: N, Skipped: N
- Confidence: N% (pass / (pass + fail))
```

Write `{report_dir}/probe-results.json`:

```json
{
  "total": 5,
  "pass": 3,
  "fail": 1,
  "error": 1,
  "skipped": 0,
  "claims": [
    { "id": "...", "result": "pass", "details": "all 3 signals found" },
    { "id": "...", "result": "fail", "details": "missing: 'compile', found: 'exit code 0'" }
  ]
}
```

<example>
Context: Skill dispatches probe for plugin documentation claims
user: "Verify docs: plugin_root=/path/to/e2e-pipeline,
  claims_path=/tmp/doc-probe/claims.json,
  report_dir=/tmp/doc-probe/report"
assistant: "Reads claims.json (3 claims), executes 2 cli probes
  (1 skipped: e2e-map needs browser), writes probe-report.md
  and probe-results.json. Results: 2 pass, 0 fail, 0 error, 1 skipped."
</example>

<example>
Context: Probe finds mismatch between docs and actual behavior
user: "Verify docs: plugin_root=/path/to/plugin,
  claims_path=/tmp/doc-probe/claims.json,
  report_dir=/tmp/doc-probe/report"
assistant: "Reads claims.json (4 claims), executes 3 cli probes.
  Claim 'help --list shows 10 topics' failed: output shows 8 topics.
  Results: 1 pass, 1 fail, 1 error, 1 skipped."
</example>
```

## Template: Reference doc-sync-context.md

This is a SCAFFOLD template — forge fills in the tables by scanning the target plugin.

```
---
plugin: {{PLUGIN_NAME}}
version: {{PLUGIN_VERSION}}
last_sync: {{SCAFFOLD_DATE}}
---

# Doc-Sync Context

Domain knowledge for {{PLUGIN_NAME}}-doc-sync. Auto-generated by kc-plugin-forge, self-maintained by the doc-sync skill.

## Source Map

| Source | Type | Doc Target | Section |
|--------|------|------------|---------|
{{FORGE_GENERATED_SOURCE_MAP}}

## Doc Structure

| File | Purpose | Auto-sync |
|------|---------|-----------|
{{FORGE_GENERATED_DOC_STRUCTURE}}

auto-sync values:
- `yes`: fully regenerable from source — safe to rewrite entirely
- `partial`: has hand-written content — only update specific sections

## Style Guide

- Lead with practical example, not abstract explanation
- Troubleshooting: table format (Issue | Cause | Fix)
- Cross-reference: Related section linking sibling docs
- Code examples: use actual plugin commands, not pseudocode
- Match existing doc tone: read a sibling doc before writing

## Probe Config

| Skill | Probe Method | Safe Input | Expected Signal |
|-------|-------------|------------|-----------------|
{{FORGE_GENERATED_PROBE_CONFIG}}

Methods:
- `cli`: safe to execute via `claude -p` subprocess
- `skip`: needs external dependencies (browser, running app, MCP)

## Post-Sync Hooks

(Plugin-specific actions to execute after doc sync completes. Added manually or by forge.)

```

## Probe Safety Heuristic

Used by forge scaffold AND by Phase 5 runtime self-update to classify skills:

| Signal in SKILL.md | → skip | Reason |
|---|---|---|
| References `agent-browser`, `browser`, `headed`, `snapshot` | skip | Needs browser |
| References `base_url`, `localhost`, `running app` | skip | Needs external server |
| Dispatches agents with `Bash` that interact with browser | skip | Indirect browser dependency |
| References MCP tools (`mcp__`) as required input | skip | Needs MCP configured |
| Writes outside plugin dir (deploy, publish, push) | skip | Side effects |
| Has `--dry-run` or `--check` mode | cli (use that mode) | Safe subset available |
| Pure read/analyze/report skill | cli | No side effects |
| Default (no skip signals) | cli | Optimistic — self-corrects via env_dependent |

The heuristic is optimistic: default to `cli`. If probe fails with env_dependent, Phase 5 updates Probe Config to `skip`. Self-correcting.
