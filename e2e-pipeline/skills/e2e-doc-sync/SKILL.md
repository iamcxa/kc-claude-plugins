---
name: e2e-doc-sync
description: Use when syncing E2E plugin documentation after skill/agent changes. Diff-aware scan, history enrichment, and live probe verification. Triggers on "e2e doc sync", "/e2e-doc-sync", "check doc coverage".
---

# E2E Doc Sync — Documentation Gap Scanner, Writer & Verifier

## Routing

| Input | Route |
|-------|-------|
| bare invocation | → Full Sync |
| `--fix` | → Full Sync (alias for bare — kept for backward compat) |
| `--check` | → Report Only (no writes) |
| `--probe-only` | → Verify Existing Docs (skip Phases 1-3 and 5, run Phase 4 on all existing docs, then Phase 6) |
| `--auto` | → Full Sync (skip confirmation) |
| `--section <doc-file>` | → Targeted Sync (one doc file) |
| `--diff <ref>` | → Use explicit git diff base instead of auto-detect |

## Phase 1: Static Scan

### Step 0 — Diff-Aware Pre-Processing (automatic)

Before inventorying files, compute a diff of changed skill/agent content since the last version tag. This catches **behavioral branches** and other features that surface-level extraction (flags, headings) would miss.

**Find diff base:**

```bash
# Auto-detect: find the most recent e2e-pipeline version tag
DIFF_BASE=$(git -C ${CLAUDE_PLUGIN_ROOT} tag -l "e2e-pipeline-v*" --sort=-v:refname | head -1)
# If --diff <ref> provided, use that instead
# If no tags exist, use HEAD~10 as fallback — warn user: "No version tags found, using HEAD~10. Diff coverage may be incomplete for older changes."
```

**Extract changed content:**

```bash
git -C ${CLAUDE_PLUGIN_ROOT} diff ${DIFF_BASE}..HEAD \
  -- 'skills/*/SKILL.md' 'agents/*.md' \
  | grep '^+' | grep -v '^+++' | sed 's/^+//'
```

Group added lines by source file. Cap diff summary at 2000 chars.

### Step 1 — Inventory & Cross-Reference

1. Read `references/doc-sync-context.md` → load Source Map, Doc Structure, Probe Config, Post-Sync Hooks
2. Inventory source files:
   - Glob `skills/*/SKILL.md` → for each: extract skill name, description, all `--flags`, modes (from routing tables), key concepts
   - Glob `agents/*.md` → for each: extract agent name, tools, input contract fields, dispatch trigger
   - Glob `hooks/` → for each: extract event type, trigger condition, affected tools
3. Inventory documentation:
   - Glob `docs/*.md` + `README.md` → for each: extract title, section headings, mentioned features, example count
4. Cross-reference: for each Source Map entry, search its Doc Target for coverage of every extracted feature
   - If diff summary exists: additionally check whether diff-added content has doc coverage
   - **Orphan check**: source files found in Step 2 inventory but absent from Source Map → classify as Critical gap ("source exists, no Source Map entry — doc target unknown"). Include file path and inferred doc target in gap report. This catches newly added skills/agents that Phase 5 hasn't registered yet.
5. Classify gaps:
   - **Critical**: source feature exists, zero mention in any doc
   - **Warning**: mentioned in one doc but not explained (e.g., flag listed in table but no usage guide)
   - **Info**: documented but could be improved (missing example, stale cross-reference)
6. Meta-doc consistency check: verify CLAUDE.md skill/agent counts, README docs table completeness, plugin.json description accuracy

If `--section <doc-file>`: filter Source Map to entries targeting that doc file only. Note: the orphan check (Step 4) always runs against the FULL Source Map, not the filtered subset — orphaned source files must be reported regardless of `--section` scope.

Output: gap_report + feature_inventory

## Phase 2: History Enrichment

**Prerequisite**: MCP tools `episodic-memory` and `private-journal`. Check each independently:
- Both unavailable → skip Phase 2 with warning: "History enrichment skipped — MCP tools unavailable. Running static-only mode."
- One unavailable → run available source, warn: "Partial enrichment — <tool> unavailable, skipping <source>."
- Both available → full enrichment.

Proceed to Phase 3 with whatever enrichment was possible (full, partial, or none).

1. Search episodic memory (if available): `search("e2e-pipeline")` → extract usage patterns, user workflows, reported issues
2. Search journal (if available): `search_journal("e2e-pipeline")` → extract technical insights, debug findings, failed attempts
3. Read MEMORY.md → extract known plugin knowledge entries (always available, no MCP dependency)
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
- **quit (q)**: abort doc writing, skip to Phase 5 (self-update still runs), then Phase 6

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

1. **Extract behavioral claims** — Read each doc written/updated in Phase 3. For `--probe-only` mode (Phase 3 skipped): read ALL docs listed in Doc Structure from `doc-sync-context.md`. Identify sentences asserting observable behavior ("X shows Y", "when you run X, Y happens", "X supports Y"). For each claim, generate structured claim object: assertion text, probe command (from Probe Config), expected output signals. This is LLM judgment, not regex.
2. Filter claims to `method: cli` only (skip claims for skills marked `skip` in Probe Config)
3. **Pre-dispatch safety gate** — Before writing claims, validate every generated probe command:
   - **Allowed**: `claude -p` invocations with `--no-input`, read-only CLI (`--help`, `--check`, `--list-*`), `cat`, `grep`, `ls`
   - **Blocked**: any command containing `rm`, `delete`, `push`, `--force`, `reset`, `drop`, `truncate`, `>` (redirect overwrite), `git checkout --`, `mv`, `chmod`, `chown`, pipe to `xargs` with write operations
   - If a generated command fails the safety gate → replace with `skip` and note: "unsafe probe command filtered"
   - Do NOT rely solely on the doc-probe agent's internal safety check — filter before dispatch
4. Write claims to `/tmp/e2e-doc-probe/claims.json`
5. Dispatch `doc-probe` agent:
   - plugin_root: `${CLAUDE_PLUGIN_ROOT}` (standard Claude Code env var, auto-available in plugin skill context)
   - claims_path: `/tmp/e2e-doc-probe/claims.json`
   - report_dir: `/tmp/e2e-doc-probe/report`
6. Read `probe-results.json`:
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

**Skip if**: `--probe-only` mode (Phase 1 inventory not available) or `--check` mode (report-only, no writes).

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
- **Phase 2 partial degradation** — check each MCP tool independently; run what's available, warn about what's not. MEMORY.md is always readable (no MCP dependency). Do NOT skip all of Phase 2 when only one MCP source is unavailable.
- **Max 3 probe rounds** — prevent infinite fix→probe loop
- **Preserve hand-written content** — check `auto-sync` flag before overwriting
- **Report first, fix second** — `--check` and `--probe-only` never write docs
- **Orphan detection in all modes** — `--check` skips Phase 5 (Self-Update), so the Source Map may be stale. Phase 1 Step 4 orphan check compensates: source files not in the Source Map are still flagged as Critical gaps. Do NOT rationalize "the glob found it, so it's covered" — without a Source Map entry, there is no doc target to verify against.
- **Pre-dispatch safety is skill-side** — the skill filters unsafe probe commands BEFORE dispatching to doc-probe. Do not rely solely on the agent's internal safety check. The skill generates the commands; the skill validates them.
