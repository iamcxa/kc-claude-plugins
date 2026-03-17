# Knowledge Capture

Post-execution learning for e2e-pipeline skills. Two dimensions of knowledge accumulation.

## Dimension 1: Skill-Level (auto-append, no gate)

General E2E testing patterns discovered during execution. Written to the plugin's own reference files.

| Insight type | Target |
|-------------|--------|
| New testing pattern | `${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md` |
| Enhancement to existing reference | The specific reference file (e.g., add to `common-patterns.md`) |
| New agent-browser gotcha | `${CLAUDE_PLUGIN_ROOT}/reference/commands.md` |

**Write mode**: Auto-append. Briefly notify user: "Appended pattern to learned-patterns.md: [title]"

### D1 entry format

```
### [YYYY-MM-DD] <context> — Title

**Pattern**: What was discovered
**Applies to**: What project types this matters for
**Action**: How this changes future E2E testing
```

### What qualifies as D1

- Selector strategies that work/fail across frameworks (e.g., `has-text()` timeout in agent-browser)
- Flow design patterns (e.g., always add wait after modal trigger)
- Agent-browser CLI behavior (e.g., recording + profile incompatibility)
- Compiler edge cases (e.g., certain expect grammar not compilable)
- Divergence patterns between LLM and compiled execution

### What does NOT qualify as D1

- Project-specific selector names or page structure
- One-off test data issues
- Environment-specific config (ports, URLs, credentials)

## Dimension 2: Project-Level (gated with threshold)

Project-specific E2E insights. Written to the tested project's files.

**Applicable skills**: e2e-test, e2e-skill-ops only.

- **Target**: `.claude/e2e-lessons.md` (contextual gotchas) or Project `CLAUDE.md` (enforceable rules)
- **Write mode**: Gated — must pass write threshold + user confirmation

### Write Threshold

**Severity gate** (pre-filter — must pass before three-question test):

| Severity | Condition | Candidate? |
|----------|-----------|------------|
| CRITICAL / HIGH | Recurring test failure pattern | Yes |
| MEDIUM | Same issue type 2+ times across runs | Yes |
| MEDIUM | Once only | No |
| LOW / NIT | — | Always no |

**Three-question test** (all must be YES):

| # | Question | Filters out |
|---|----------|-------------|
| 1 | **Recurs?** — Future test runs will hit this? | One-off flakes |
| 2 | **Non-obvious?** — New devs writing E2E tests would miss it? | Self-evident fixes |
| 3 | **Ruleable?** — "do X / never Y + because Z"? | Vague "be careful" |

### D2 target selection

| Finding type | Target | Example |
|-------------|--------|---------|
| Timing/performance rule | `.claude/e2e-lessons.md` | "POST /api/orders takes 5s+, use timeout: 10" |
| Auth/session rule | Project `CLAUDE.md` | "Auth token expires in 30 min, long suites need re-auth" |
| Recurring divergence | `.claude/e2e-lessons.md` | "Modal animation 3s, LLM/compiled always diverge on modal steps" |
| Data dependency | `.claude/e2e-lessons.md` | "Order flow needs seeded user with billing info" |

### D2 entry format (e2e-lessons.md)

```
### [YYYY-MM-DD] <flow-name> — Title

**Pattern**: What the test failure looked like
**Impact**: Why this matters for E2E testing in this project
**Prevention**: Rule or adjustment to prevent future failures
```

If `.claude/e2e-lessons.md` doesn't exist, create with:

```
# E2E Lessons

Accumulated insights from E2E test runs. Auto-read during test execution.

---
```

## Present & Confirm

```
## Knowledge Capture — N items from <flow/session>

| # | Dim | Type | Target | Summary |
|---|-----|------|--------|---------|
| K1 | D1 | Pattern | learned-patterns.md | [auto-appended] |
| K2 | D2 | Timing rule | e2e-lessons.md | Modal steps need timeout: 5 |

D1 items auto-appended. D2 items: apply? [yes / no]
```

**GATE — D2 writes require user confirmation.** D1 writes are auto-appended with notification.

## Write Rules

1. D1: auto-append via Edit — no commit needed (plugin repo, user's local install)
2. D2: apply approved edits via Edit (CLAUDE.md) or Write (new e2e-lessons.md)
3. D2 commit: `docs: capture E2E lessons from <flow-name>`
4. **Actionable rules only** — every entry must change future behavior
5. **Surgical edits** — never rewrite unrelated sections
6. **Separate commit** — D2 writes get their own commit, never bundled with other changes

## Flywheel

```
Test/Explore → Findings → D1: skill gets smarter     → D2: project tests get smarter
  ↑                              ↓                            ↓
  │                    learned-patterns.md            e2e-lessons.md / CLAUDE.md
  │                              ↓                            ↓
  └── Next run reads both sources (setup phase) ─────────────┘
```

D1 learnings can be PR'd back to origin repo → community benefits.

## Red Flags

- Writing vague pattern ("be careful with modals") → must be specific and testable
- Capturing one-off flake as D2 → flakes don't pass three-question test
- Writing D2 without passing severity gate → threshold exists for a reason
- Appending duplicate D1 entry → search learned-patterns.md before writing
