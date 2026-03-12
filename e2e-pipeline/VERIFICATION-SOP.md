# E2E Pipeline — Component Verification SOP

> Reusable checklist extracted from the pilot verification of `e2e-test` skill + `e2e-test-runner` agent (Tasks 1-9).
> Apply this SOP to each remaining skill and agent in the plugin.

---

## Skill Verification Checklist (apply `/writing-skills`)

### 1. Frontmatter — Description & Triggers

- [ ] Description starts with "Use when..."
- [ ] Description has NO workflow summary (no "resolves", "dispatches", "orchestrates", "processes")
- [ ] Trigger keywords cover all realistic user phrases (test with 4+ positive phrases, 4+ negative phrases)
- [ ] Cross-skill collision risk assessed (identify sibling skills with shared keywords, document separation mechanism)
- [ ] Under 500 chars

**Trigger testing method** (from Round 1):

| Test Type | What to Check | Example |
|-----------|---------------|---------|
| Positive coverage | Each expected phrase matches at least one keyword | "run the e2e tests" -> "run e2e", "e2e test" |
| Negative separation | Unrelated phrases do NOT trigger | "write a unit test" -> no match in "browser E2E" context |
| Cross-skill collision | Shared keywords have clear separation | `e2e-test` vs `e2e-dispatch`: overlap intentional (dispatch routes TO e2e-test) |
| Gaps | Plausible phrases that are missing | "browser test" (without "e2e"), "playwright test" |

### 2. Behavior — Phase-by-Phase Walk

- [ ] Each phase has an explicit transition (not implied)
- [ ] Phase 0 (resolution/validation) covers: input scan, schema validation, format migration guidance
- [ ] Agent dispatch input contract lists ALL fields in a table (field, source, required/optional)
- [ ] Compare dispatch template fields against the field table — every field in one must appear in the other
- [ ] Error paths have actionable messages: what happened + WHY + what to do next
- [ ] Multi-mode paths (Route A/B/C) are clearly separated with distinct entry conditions
- [ ] Result handling covers: single success, single failure, batch partial failure

**Contract alignment method** (from Round 2):

Build a field-by-field table comparing skill dispatch vs agent expectation:
```
| Field          | Skill sends? | Agent expects? | Aligned? |
|----------------|-------------|----------------|----------|
| flow_path      | YES         | YES            | ALIGNED  |
| suite_context  | NO          | YES            | **GAP**  |
```
Any GAP = the agent silently runs without the field, potentially causing subtle bugs.

### 3. Edge Cases & Robustness

- [ ] Missing input files -> clear error with remediation (explain WHY the file is needed + how to create it)
- [ ] Bad format / legacy format -> migration guidance (list specific field changes needed)
- [ ] Partial failure in batch -> continues remaining items, marks failed as ERROR with reason
- [ ] Cross-domain guard (e.g., flow targets app A but mapping is for app B) -> caught before dispatch
- [ ] Non-existent references -> warning with actionable format (element name, step id, page)

**Edge case testing method** (from Round 3):

| Scenario | What to Verify | Expected Behavior |
|----------|----------------|-------------------|
| No input files at all | Error message exists | States what's missing, why it's needed, how to create it |
| Legacy format detected | Migration path documented | Lists exact field renames / structural changes |
| One item in batch is invalid | Other items still execute | Invalid item marked ERROR with parse reason in results |
| Element ref not in mapping | Warning (not error) | Shows: element name, step ID, page — user can decide to proceed |

---

## Agent Verification Checklist (apply `/agent-development`)

### 1. Frontmatter

- [ ] `name`: 3-50 chars, lowercase-hyphens
- [ ] `description`: starts with role, has 2-4 `<example>` blocks (context/user/assistant/commentary)
- [ ] `model`: `inherit` (unless specific need documented)
- [ ] `color`: distinct from other agents in plugin
- [ ] `tools`: minimum necessary — justify each tool against actual usage in agent body

**Tools audit method** (from Task 6):

For each tool listed in frontmatter, search the agent body for actual usage:
- `Bash` — look for CLI commands, curl, file operations
- `Read` — look for file reads (YAML, config, references)
- `Grep` — look for content search patterns (may be indirect, e.g., searching output files)
- `Glob` — look for file discovery patterns. If agent always reads by explicit path, remove Glob.
- `Write` — look for file creation (reports, snapshots)

If a tool has zero explicit or plausible implicit usage, **remove it**.

### 2. System Prompt Structure

- [ ] "You are..." role opening
- [ ] Explicit "Core Responsibilities" list (numbered, 4-8 items)
- [ ] Explicit "Input Contract" section: table of all expected fields with Required/Optional + descriptions
- [ ] STOP guard for missing required fields: `"Missing required field: '<field>'. The orchestrator must provide all required fields."`
- [ ] Step-by-step process (phases numbered with sub-steps)
- [ ] Output format defined (exact heading/structure agent must emit)
- [ ] Critical rules are actionable: WHAT to do + HOW to detect + concrete example
- [ ] Edge cases with handling instructions (failure recovery, partial results)

### 3. Self-Contained Check

- [ ] Zero `Skill: "..."` references (subagents cannot load skills)
- [ ] Reference file paths are absolute or plugin-relative
- [ ] All domain knowledge inline (not depending on external docs the agent can't access)

### 4. I/O Contract Alignment (Skill <-> Agent)

- [ ] Build field comparison table: every field the skill dispatches vs every field the agent's Input Contract lists
- [ ] Every field the orchestrator sends is documented in the agent
- [ ] Every required field the agent expects is present in the skill's dispatch template
- [ ] Agent output format matches what the orchestrator parses in its results phase
- [ ] Optional fields have documented defaults in both skill and agent

### 5. Live Behavior Test (Optional but Recommended)

- [ ] Dispatch agent with valid input -> check structured output matches expected format
- [ ] Dispatch agent with intentionally mismatched input -> check it detects and reports the mismatch
- [ ] Verify report/artifact files are written to expected paths

---

## Common Fix Patterns

### Skill Fixes

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Description summarizes workflow | "Orchestrator for...", "Resolves X then dispatches Y" | Rewrite: "Use when [situation]. Triggers on [keywords]" |
| Missing trigger keywords | Users phrase request differently and skill doesn't trigger | Add user-facing phrases from real usage; test with positive/negative phrase matrix |
| Implicit phase transition | Reader can't tell where Phase N ends and N+1 begins | Add explicit "After Phase N completes, proceed to Phase N+1" |
| Agent input contract incomplete | Field exists in dispatch template but not in field table (or vice versa) | Sync both: add to field table AND dispatch template |
| Dispatch field missing entirely | Agent expects field but skill never sends it | Add to skill's field table with source + add to dispatch template |
| Error message lacks WHY | "No mapping found. Stop." | Add: "No mapping files found in '<path>'. Mappings define selectors and page structure that flows depend on. Run '/e2e-map' first to create one." |
| Element ref warning vague | "Warning: element not found" | Show: element name, step ID, page — actionable format: `Element not in mapping: "<element>" (step <id>, page <page>). Test may fail at runtime.` |
| Batch error handling incomplete | Parse errors abort entire batch | "If a flow has invalid YAML or fails schema validation, mark as ERROR with parse reason, skip, continue remaining." |
| No pre-dispatch validation | Mismatch between flow target and execution context caught only at runtime | Add guard in Phase 0: validate flow's target matches the provided mapping/base_url before dispatch |

### Agent Fixes

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Description lacks examples | Agent triggers inaccurately or fails to trigger | Add 2-4 `<example>` blocks with context/user/assistant/commentary |
| Tools list not justified | Unused tools inflate agent's capability surface | Audit each tool against agent body usage; remove any with zero actual usage |
| Critical rule is declarative only | "Use absolute paths" with no concrete example | Add: what to do + how to detect + example: "use `{{report_dir}}/filename`, never bare `./filename`" |
| Input contract implicit | Fields referenced via `{{placeholder}}` but never formally declared | Add explicit table before Phase 1: field, required/optional, description, plus STOP guard |
| Missing Core Responsibilities | Role is implied by intro sentence but not enumerated | Add numbered list (4-8 items) after intro paragraph covering all agent duties |
| Skill reference in agent body | `Skill: "..."` that subagent can't load | Inline the knowledge or point to a reference file the agent can Read |

---

## Verification Workflow

### Per-Component Process

1. **Read** the skill/agent file completely
2. **Apply** the relevant checklist above (skill or agent)
3. **Build** the contract alignment table (for skill-agent pairs)
4. **Document** findings in VERIFICATION-LOG.md with: Finding, Before/After, Fix Applied
5. **Fix** issues directly in the component file
6. **Optional**: Run a live behavior test for agents

### Ordering Recommendation

Verify in dependency order:
1. **Skills first** — fix description, triggers, dispatch contract
2. **Agents second** — fix frontmatter, input contract, self-containment
3. **Alignment last** — cross-reference skill dispatch vs agent input contract

This order avoids rework: fixing the skill's dispatch contract first means the agent alignment check runs against the corrected version.

### Log Format

Each finding in VERIFICATION-LOG.md should follow this structure:

```markdown
### Finding N: [Short title]
- **Component**: [skill/agent name]
- **Check**: [Which checklist item]
- **Before**: [What it looked like]
- **After**: [What it looks like now]
- **Rule**: [Which principle/guideline applies]
- **SOP Pattern**: [Reusable lesson, if any]
```

For batch findings (e.g., trigger analysis), use tables as in the pilot log.
