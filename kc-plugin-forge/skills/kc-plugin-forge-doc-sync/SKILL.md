---
name: kc-plugin-forge-doc-sync
description: >
  Use when plugin documentation needs updating after feature changes,
  when verifying existing docs accurately reflect actual skill/agent behavior,
  or for periodic documentation maintenance. Scans source code, enriches
  with usage history from journal and memory, writes or updates docs,
  then reports gaps.
---

# kc-plugin-forge-doc-sync

## Routing

| Input | Route |
|-------|-------|
| bare invocation | → Full Sync |
| `--check` | → Report Only |
| `--auto` | → Full Sync (skip confirmation) |
| `--section <doc-file>` | → Targeted Sync (one doc file) |

## Phase 1: Static Scan

1. Read `reference/doc-sync-context.md` → load Source Map, Doc Structure, Post-Sync Hooks
2. Inventory source files:
   - Glob `skills/*/SKILL.md` → for each: extract skill name, description, all `--flags`, modes (from routing tables), key concepts
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

1. Search episodic memory: `search("kc-plugin-forge")` → extract usage patterns, user workflows, reported issues
2. Search journal: `search_journal("kc-plugin-forge")` → extract technical insights, debug findings, failed attempts
3. Read MEMORY.md → extract known plugin knowledge entries
4. Enrich each gap:
   - History mentions this feature with usage context? → add context to gap (improves doc writing quality)
   - History contradicts current docs? → escalate gap to `accuracy_risk` (priority fix)
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

> Doc-probe agent not scaffolded (Light variant). Live probing disabled.
> To enable: run `/kc-plugin-forge kc-plugin-forge` and select Full for Doc Self-Iteration.

Skip this phase.

## Phase 5: Self-Update Reference

1. Compare current skills/hooks inventory (from Phase 1) vs `doc-sync-context.md`
2. New source files found → append to Source Map with inferred Doc Target
3. Removed source files → mark as deprecated in Source Map (warn user, don't auto-delete)
4. Update frontmatter: `last_sync` date, `version` to current plugin version

## Phase 6: Report + Knowledge Loop

1. Output summary:
   | Metric | Value |
   |--------|-------|
   | Gaps found | N |
   | Gaps fixed | N |
   | Accuracy risks found | N |
   | Docs created | N |
   | Docs updated | N |
   | Reference self-updated | yes/no |

2. D1 learning: check for reusable patterns worth capturing:
   - History enrichment found risk confirmed → user-reported issue validated
   - New skill had no doc coverage → expansion rule for doc structure
   If pattern found → append to `reference/learned-patterns.md`

3. Auto-issue: if unfixed gaps remain (user declined):
   - Offer to create GitHub issue with gap details
   - Format: title = "Doc sync: N gaps remaining", body = gap list with severity

4. Post-sync hooks: read and execute plugin-specific actions from `doc-sync-context.md` Post-Sync Hooks section

## Rules

- **Docs conform to Code** — when behavior and docs disagree, fix the docs, not the code
- **Phase 2 graceful degradation** — MCP unavailable → skip history, run static-only
- **Preserve hand-written content** — check `auto-sync` flag before overwriting
- **Report first, fix second** — `--check` never writes docs
