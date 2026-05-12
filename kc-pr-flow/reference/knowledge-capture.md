# Knowledge Capture

Post-review learning for kc-pr-flow skills (kc-pr-review + kc-pr-review-resolve). Two dimensions of knowledge accumulation.

## Dimension 1: Skill-Level (auto-append, no gate)

General review patterns discovered during this review session. Written to the plugin's own reference files.

| Insight type | Target |
|-------------|--------|
| New review pattern | `${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md` |
| New false-positive pattern | `${CLAUDE_PLUGIN_ROOT}/reference/compliance-audit.md` → Red Flags |
| New triage heuristic | `${CLAUDE_PLUGIN_ROOT}/reference/review-triage.md` |
| Agent prompt improvement | `${CLAUDE_PLUGIN_ROOT}/reference/review-triage.md` → agent focus |

**Write mode**: Auto-append. Briefly notify user: "Appended pattern to learned-patterns.md: [title]"

### D1 entry format

```
### [YYYY-MM-DD] <project> — Title

**Pattern**: What was discovered
**Applies to**: What project types this matters for
**Action**: How this changes future reviews
```

## Dimension 2: Project-Level (gated with threshold)

Project-specific insights from DOC/NEW findings and recurring CODE patterns. Written to the reviewed project's files.

### Write Threshold

**Severity gate** (pre-filter — must pass before three-question test):

| Severity | Condition | Candidate? |
|----------|-----------|------------|
| CRITICAL / HIGH | DOC or NEW classification | Yes |
| MEDIUM | Same issue type 2+ times | Yes |
| MEDIUM | Once only | No |
| LOW / NIT | — | Always no |

**Three-question test** (all must be YES):

| # | Question | Filters out |
|---|----------|-------------|
| 1 | **Recurs?** — Future PRs will hit this? | One-off mistakes |
| 2 | **Non-obvious?** — Unfamiliar devs would miss it? | Self-evident fixes |
| 3 | **Ruleable?** — "do X / never Y + because Z"? | Vague "be careful" |

### Target selection

| Finding type | Target | Action |
|-------------|--------|--------|
| DOC (stale rule) | Project `CLAUDE.md` | Edit existing rule |
| DOC (contradicted) | Project `CLAUDE.md` | Remove or update |
| NEW (convention) | Project `CLAUDE.md` | Add new rule |
| NEW (gotcha) | `.claude/review-lessons.md` | Append lesson entry |
| CODE (recurring) | Project `CLAUDE.md` | Add prevention rule |

**CLAUDE.md vs review-lessons.md**: Enforceable rule (do X / never Y) → CLAUDE.md. Contextual gotcha (watch out when...) → review-lessons.md.

### D2 entry format (review-lessons.md)

```
### [YYYY-MM-DD] PR #NNN — Title

**Pattern**: What the problematic code looked like
**Impact**: Why this matters in this project
**Prevention**: Rule or check to catch this next time
```

If `.claude/review-lessons.md` doesn't exist, create with:

```
# Review Lessons

Accumulated insights from code reviews. Auto-read during PR review compliance audit.

---
```

## Present & Confirm

```
## Knowledge Capture — N items from PR #962

| # | Dim | Type | Target | Summary |
|---|-----|------|--------|---------|
| K1 | D1 | Pattern | learned-patterns.md | [auto-appended] |
| K2 | D2 | DOC fix | CLAUDE.md § Frontend | React 18 → 19 |
| K3 | D2 | New rule | CLAUDE.md § Testing | act() wrap required |
| K4 | D2 | Gotcha | .claude/review-lessons.md | Empty catch masks 500s |

D1 items auto-appended. D2 items: apply which? [all / 2,3 / none]
```

**GATE — D2 writes require user confirmation.** D1 writes are auto-appended with notification.

## Write & Commit

1. D1: auto-append via Edit (or Write if new file) — no commit needed (plugin repo)
2. D2: apply approved edits via Edit (CLAUDE.md) or Write (new review-lessons.md)
3. D2 commit: `docs: capture review lessons from PR #NNN`

## Flywheel

```
Review → Findings → D1: skill gets smarter    → D2: project gets smarter
  ↑                        ↓                          ↓
  │              learned-patterns.md          CLAUDE.md / review-lessons.md
  │                        ↓                          ↓
  └── Next review reads both sources (Step 5a-k) ────┘
```

D1 learnings can be PR'd back to origin repo → community benefits.

## Red Flags

- Writing vague rule ("be careful with X") → must be specific and testable
- Adding CLAUDE.md rule that contradicts existing one → update/remove old first
- Capturing one-off finding that won't generalize → skip
- Modifying unrelated CLAUDE.md sections → surgical edits only
- Writing D2 without passing severity gate + three-question test → threshold exists for a reason
