# Self-Improvement

The pipeline accumulates knowledge after every execution. Skills learn from failures, divergence, and novel observations -- then apply those lessons on the next run.

## The Two-Dimension Framework

Knowledge is captured along two axes:

| Dimension | Scope | Storage | Gate | Example |
|-----------|-------|---------|------|---------|
| **D1** (skill-level) | Cross-project patterns | `references/learned-patterns.md` (plugin repo) | Auto-append, no gate | "`has-text()` times out in agent-browser" |
| **D2** (project-level) | Project-specific patterns | `.claude/e2e-lessons.md` (project repo) | Severity gate + 3-question test + user confirmation | "POST /api/orders takes 5s+, use timeout: 10" |

**D1** makes the plugin smarter for everyone. **D2** makes tests smarter for one project.

## Which Skills Learn

| Skill | D1 (auto) | D2 (gated) | When |
|-------|-----------|------------|------|
| `e2e-test` | Yes | Yes | After presenting test results |
| `e2e-skill-ops` | Yes | Yes (--evaluate only) | After gap analysis |
| `e2e-flow` | Yes | No | After generation + verification |
| `e2e-walkthrough` | Yes | No | After walkthrough completion |
| `e2e-map` | Yes | No | After mapping exploration |
| `e2e-compile` | No (deterministic) | No | -- |
| `e2e-dispatch` | No (router) | No | -- |

## Where Patterns Are Stored

### D1: `references/learned-patterns.md`

Lives in the plugin directory. Accumulated entries look like:

```markdown
### [2026-03-18] Login flow — Regex selector needs literal prefix for grep -F

**Pattern**: When converting `role=X[name=/pattern/]` to a grep pattern,
extract the longest literal prefix before the first regex metacharacter.
**Applies to**: Any compiled flow using regex selectors
**Action**: Use literal prefix extraction, not full regex string with grep -F
```

Every skill reads this file at startup (Knowledge Bootstrap phase) to avoid re-discovering known patterns.

### D2: `.claude/e2e/e2e-lessons.md`

Lives in the project repo. Contains project-specific timing, auth, and data dependency rules:

```markdown
### [2026-03-15] audit-options — Modal animation delay

**Pattern**: Audit options modal has a 3s CSS transition.
LLM and compiled runs always diverge on modal steps.
**Impact**: Flaky test results on audit-related flows
**Prevention**: Add `timeout: 5` to all modal interaction steps in audit flows
```

## How Patterns Are Captured

After every skill execution, a Learning phase runs automatically:

1. **Scan results** for novel observations -- selector strategies, divergence patterns, framework behaviors, timing issues
2. **Check for duplicates** -- search `learned-patterns.md` before appending
3. **D1 candidates** -- auto-append with notification: "Appended pattern: [title]"
4. **D2 candidates** (e2e-test and e2e-skill-ops only) -- pass through severity gate, then three-question test:

| # | Question | Filters out |
|---|----------|-------------|
| 1 | **Recurs?** Will future runs hit this? | One-off flakes |
| 2 | **Non-obvious?** Would a new dev miss it? | Self-evident fixes |
| 3 | **Ruleable?** Can you say "do X / never Y + because Z"? | Vague "be careful" |

D2 candidates that pass all three are presented for user confirmation before writing.

### Skip Conditions

Learning is skipped when there is nothing to learn:
- Zero failures AND zero divergence AND no novel observations
- All findings already exist in `learned-patterns.md`

## PR-Back Flow

D1 patterns accumulate in your local plugin installation. To share them with all users:

1. Curate `references/learned-patterns.md` -- remove project-specific noise, keep general patterns
2. Open a PR to the [plugin origin repo](https://github.com/iamcxa/kc-claude-plugins/pulls)
3. After merge, all plugin users benefit on next update

This creates a flywheel: test runs produce patterns, patterns improve future test runs, and the best patterns propagate to the community.

```
Test/Explore --> Findings --> D1: skill gets smarter     --> D2: project tests get smarter
  ^                                |                              |
  |                     learned-patterns.md              e2e-lessons.md
  |                                |                              |
  +-- Next run reads both sources (Knowledge Bootstrap) ----------+
```

## Related

- [Commands](commands.md) -- all skill invocations and flags
- [Architecture](architecture.md) -- skill-to-agent model and pipeline design
- [Writing Tests](writing-tests.md) -- flow YAML format and preconditions
- [Debugging](debugging.md) -- using `/e2e-skill-ops --evaluate` findings to improve

---

> **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
> **Docs unclear?** Use `/e2e-help --feedback "<description>"` to let us know.
