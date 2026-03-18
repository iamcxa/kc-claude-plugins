---
name: e2e-doc-sync
description: Use when E2E pipeline features have been added or changed and documentation needs updating. Scans skills and agents against docs to find gaps, proposes outlines for approval, then dispatches a subagent to write updates. Triggers on "sync e2e docs", "update e2e documentation", "doc sync", "e2e-doc-sync", "check doc coverage".
---

# E2E Doc Sync — Documentation Gap Scanner & Writer

Keep documentation in sync with skill and agent definitions after feature changes.

## Invocation

```
/e2e-doc-sync                    # Scan for gaps, propose fixes
/e2e-doc-sync --fix              # Scan + auto-write approved gaps
/e2e-doc-sync --check            # Report-only mode (no writes)
```

## Phase 1 — Scan for Gaps

Dispatch the `e2e-doc-scanner` agent to analyze the gap between implementation and documentation:

```
Agent(subagent_type="e2e-pipeline:e2e-doc-scanner"):
  "Scan for documentation gaps:
   plugin_root: ${CLAUDE_PLUGIN_ROOT}
   mode: scan"
```

The agent cross-references:
- **Skills** (`skills/*/SKILL.md`) — flags, modes, concepts, features
- **Agents** (`agents/*.md`) — capabilities, input contracts, behaviors
- **Docs** (`docs/*.md`) — covered topics, examples, sections
- **CHANGELOG.md** — recent feature additions
- **README.md** — quick start coverage, docs table completeness

Returns a structured gap report with entries classified by severity:

| Severity | Meaning |
|----------|---------|
| **Critical** | Feature implemented in skills/agents, zero doc coverage |
| **Warning** | Feature partially documented (e.g., flag listed but not explained) |
| **Info** | Could be improved (cross-reference missing, example would help) |

## Phase 2 — Present & Confirm Outlines

Present gaps to the user organized by severity:

```markdown
## Documentation Gaps Found

### Critical (N)
1. **<feature>** — <skill> defines it but no doc covers it
   - Proposed: new `docs/<name>.md`
   - Outline: [section1, section2, ...]

### Warning (N)
2. **<flag>** — listed in commands.md but no explanation
   - Proposed: expand `docs/commands.md`

### Info (N)
3. **<topic>** — documented in one place but not cross-referenced
   - Proposed: add section to `docs/<file>.md`

Approve all? (a = all, s = select individually, e = edit outlines, q = quit)
```

**User interaction**:
- `a` → approve all, proceed to write
- `s` → present each gap for individual y/n
- `e` → user edits outlines inline, then approve
- `q` → stop, no writes

## Phase 3 — Write Documentation

For approved gaps, dispatch the doc-scanner agent in write mode:

```
Agent(subagent_type="e2e-pipeline:e2e-doc-scanner"):
  "Write documentation updates:
   plugin_root: ${CLAUDE_PLUGIN_ROOT}
   mode: write
   approved_gaps: <JSON list of approved gaps with outlines>
   style_guide:
     - Practical examples over abstract explanations
     - Each doc ends with contributing CTA (PR link + /e2e-help --feedback)
     - Cross-reference related docs in a Related section
     - Include troubleshooting table for complex topics
     - Match tone and depth of existing docs"
```

The agent:
1. Reads source files (skills/agents) for authoritative content
2. Reads existing docs for style matching
3. Writes new docs or updates existing ones
4. Updates README.md docs table if new files were created
5. Updates `docs/commands.md` flag descriptions if new flags were found
6. Returns list of files created/modified

## Phase 4 — Verify & Report

After writing:

1. **Link check**: Grep all docs for `](docs/` and `](./` references, verify targets exist
2. **README sync**: Verify README.md docs table includes all `docs/*.md` files
3. **Dispatch routing**: If new skills were added, check `skills/e2e-dispatch/SKILL.md` routing table
4. **CLAUDE.md counts**: Verify skill/agent counts in CLAUDE.md match actual directories

Present summary:

```markdown
## Doc Sync Complete

| Action | File | Status |
|--------|------|--------|
| Created | docs/multi-site-testing.md | ✅ |
| Updated | docs/commands.md | ✅ |
| Verified | README.md docs table | ✅ |

### Remaining
- No remaining gaps (or: N gaps deferred by user)

Run `/e2e-doc-sync --check` to verify no remaining gaps.
```

## Phase 5 — Knowledge Loop Triggers

After completing a doc sync, check:

1. **e2e-help topic map**: If new docs were created, verify the topic-to-file mapping in `skills/e2e-help/SKILL.md` Phase 3 includes them
2. **Feedback log**: Read `e2e-reports/feedback-log.md` (if exists) for unresolved user feedback that the new docs might address
3. **Suggest closing issues**: If gaps were filled that match open GitHub issues tagged `documentation`, suggest closing them

## When to Run

This skill should be invoked:
- After bumping the plugin version (features changed)
- After adding/removing/renaming skills or agents
- After adding new flags or modes to existing skills
- Before `/kc-marketplace-sync` (ensure docs match what's published)
- Periodically as maintenance (monthly or after major changes)

## Common Patterns

### After a feature PR

```
# 1. Implement feature
# 2. Run doc sync
/e2e-doc-sync --fix

# 3. Review generated docs
# 4. Commit docs alongside feature
```

### CI check mode

```
/e2e-doc-sync --check
# Returns: "3 gaps found" or "All docs in sync"
# Non-zero conceptual exit if gaps exist
```
