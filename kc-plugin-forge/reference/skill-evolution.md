# Skill Evolution Framework

Two-dimension self-improvement for forge-generated skills. Every skill that analyzes or evaluates should accumulate knowledge.

## Dimension 1: Skill-Level (General Domain Knowledge)

Patterns that apply across ANY project. Accumulated in the plugin's own reference files.

- **Target**: `${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md` (or existing reference files for enhancements)
- **Write mode**: Auto-append with brief notification — no confirmation gate (skill author is the user)
- **Example**: "GitHub Actions `continue-on-error` masks failure status" — applies to any project using GHA

### D1 entry format

```
### [YYYY-MM-DD] <context> — Title

**Pattern**: What was discovered
**Applies to**: What project types this matters for
**Action**: How this changes future reviews
```

### Where to place D1 insights

| Insight type | Target |
|-------------|--------|
| New general pattern | `reference/learned-patterns.md` |
| Enhancement to existing checklist | The specific reference file (e.g., add Red Flag) |
| New false-positive pattern | The reference handling validation/triage |

## Dimension 2: Project-Level (Project-Specific Knowledge)

Patterns specific to the project being operated on. Written to the project's own files.

- **Target**: Project `CLAUDE.md` (enforceable rules) or `.claude/<context>-lessons.md` (contextual gotchas)
- **Write mode**: Gated — must pass write threshold
- **Example**: "This project's webhook handlers must re-throw after logging" — specific to this codebase

### Write Threshold (D2 only)

**Severity gate** (pre-filter):

| Severity | Condition | Candidate? |
|----------|-----------|------------|
| CRITICAL / HIGH | DOC or NEW classification | Yes |
| MEDIUM | Same issue type 2+ times | Yes |
| MEDIUM | Once only | No |
| LOW / NIT | — | Always no |

**Three-question test** (all YES to capture):

| # | Question | Filters out |
|---|----------|-------------|
| 1 | **Recurs?** — Will future work hit this? | One-off mistakes |
| 2 | **Non-obvious?** — Would unfamiliar devs miss it? | Self-evident fixes |
| 3 | **Ruleable?** — "do X / never Y + because Z"? | Vague warnings |

### D2 target selection

| Insight type | Target |
|-------------|--------|
| Enforceable rule (do X / never Y) | Project `CLAUDE.md` |
| Contextual gotcha (watch out when...) | `.claude/<context>-lessons.md` |
| Stale documentation | Project `CLAUDE.md` (edit existing) |

### D2 entry format (for lessons files)

```
### [YYYY-MM-DD] PR #NNN — Title

**Pattern**: What the problematic code looked like
**Impact**: Why this matters in this project
**Prevention**: Rule or check to catch this next time
```

## Integration Pattern

### Adding self-improvement to a skill

1. Create `reference/learned-patterns.md` in the plugin (if not already present)
2. Add a **Learning step** as the skill's final step using the Detection → Capture / Light Reflection structure:
   - **Detection** (mandatory): scan for hard signals (unexpected failure, workaround, pattern not in references, same issue 2+ times)
   - **Capture** (conditional): hard signals found → check against existing knowledge base → write D1 (and D2 if Full level) if not covered
   - **Light Reflection** (fallback): no hard signals → "What was most unexpected?" → three-question test → capture or done
3. In the skill's setup/analysis phase, **read** `learned-patterns.md` + project's lessons file
4. Add rules: D1 auto-append, D2 gated write (if Full), actionable rules only, surgical edits
5. **"Nothing novel" must be explicitly permitted** — zero learning output is valid and encouraged

### Level-specific scaffolding

| Level | Learning step | D2 gates | Rules |
|-------|--------------|----------|-------|
| Full (D1 + D2) | Detection → Capture (D1+D2) / Light Reflection | Yes (severity gate + three-question test) | D1 auto-append + D2 gated write |
| D1 only | Detection → Capture (D1 only) / Light Reflection | No | D1 auto-append only |
| Skip | None | None | None |

### Applicability

Self-improvement level is decided at forge Phase 1.5 (Evolution Decision). The forge presents a choice based on intent detection:

| Detected Intent | Recommended Level | Rationale |
|----------------|-------------------|-----------|
| analysis (review, audit, triage, evaluate) | Full (D1 + D2) | Discovers both general and project-specific patterns |
| mixed or ambiguous | Full (D1 + D2) | Downgrade is easier than upgrade |
| data processing | D1 only | May discover general patterns, no project writes needed |
| utility (sync, bump, scaffold, convert) | Skip | Nothing to learn from — pure transformation |

The user always makes the final choice. Intent detection is a recommendation, not a decision.

## PR-Back Flow (Community Knowledge)

D1 learnings accumulate locally in each user's plugin installation. To contribute back:

1. **Curate**: Review `learned-patterns.md` — remove duplicates, sharpen language
2. **PR**: Create pull request to the plugin's origin repo with curated entries
3. **Review**: Maintainer verifies generality (applies to >1 project) and quality (specific, testable)
4. **Merge**: Accepted entries benefit all users

```
User → discovers pattern → local learned-patterns.md → curate → PR → origin
                                                                        ↓
                                           All users benefit ← next release
```

## Forge Verification Checklist

- [ ] Skill has Learning step as final step
- [ ] Plugin has `reference/learned-patterns.md`
- [ ] Setup/analysis phase reads learned-patterns.md + project lessons
- [ ] D2 writes reference write threshold (severity gate + three-question test)
- [ ] Rules include D1 auto-append + D2 gated write + actionable-only
- [ ] Phase 1.5 evolution choice was recorded (for new/retrofit plugins)
- [ ] "Nothing novel" is explicitly permitted in skill rules

## Learning Step Templates

Templates injected into generated plugin skills during Phase 1.5 scaffold.

### Full (D1 + D2)

```
## Learning

After completing the main workflow, capture insights from this run.

### Detection — scan for hard signals

| Signal | Source |
|--------|--------|
| Unexpected failure or retry | Something non-obvious broke |
| Workaround instead of direct fix | Tool/process limitation discovered |
| Pattern not in learned-patterns.md | New general knowledge |
| Same issue type seen 2+ times | Recurring problem worth documenting |

Hard signals found → proceed to **Capture**.
No hard signals → proceed to **Light Reflection**.

### Capture (conditional)

For each hard signal:
1. Check `${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md` — already covered?
   - Yes → skip (note: "covered by: [pattern name]")
   - No → write D1 entry (auto-append, notify user)
2. D2 check (project-specific): pass severity gate + three-question test?
   - Yes → write to project CLAUDE.md or `.claude/<context>-lessons.md`
   - No → skip

### Light Reflection (no hard signals)

One question: **"What was most unexpected in this run?"**
- Has answer → apply three-question test (Recurs? Non-obvious? Ruleable?) → all YES → capture D1
- Nothing → done. No output is a valid outcome.
```

### D1 Only

```
## Learning

After completing the main workflow:

1. **Detection**: Any unexpected failure, workaround, or pattern not in learned-patterns.md?
   - Yes → check `${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md`, if not covered → append D1 entry
   - No → one question: "What was most unexpected?" → three-question test → capture or done
2. "Nothing novel" is a valid and encouraged outcome.
```

### learned-patterns.md Scaffold

```
# Learned Patterns

Cross-project patterns accumulated during <plugin-name> operations.

Curate periodically and PR valuable entries back to the origin repo.

---

(Patterns will be added here as the plugin discovers them during use.)
```
