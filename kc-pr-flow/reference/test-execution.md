# Test Execution During Review

Run the PR's own tests in a worktree to catch issues that static analysis misses. Test results are a first-class review signal — they can upgrade or downgrade the review event.

## Activation Conditions

**ALL must be true:**

1. `IS_MY_REPO=true` (have local repo access + can create worktree)
2. Changed files include testable code (not docs-only)
3. PR branch is accessible (`git fetch` succeeds)

**Skip when:**

- `IS_MY_REPO=false` — no local repo, can't run tests
- Docs-only PR — no `.ts`, `.tsx`, `.py`, `.go`, `.rs` files changed
- User explicitly says "skip tests" or "quick review"

## Worktree Setup

```bash
# 1. Fetch PR branch
git fetch origin <headRefName>

# 2. Create isolated worktree
git worktree add .worktrees/<pr-number>-review origin/<headRefName>

# 3. Install dependencies (project-specific)
cd .worktrees/<pr-number>-review/<frontend-dir> && pnpm install --frozen-lockfile
# or: pip install -e . / uv pip install -e .

# 4. Copy env files if needed (eval tests need API keys)
cp <project-root>/<app-dir>/.env.local .worktrees/<pr-number>-review/<app-dir>/.env.local
```

**Always clean up** after tests:

```bash
git worktree remove .worktrees/<pr-number>-review
```

## Test Selection Strategy

Match changed files against test commands. Run from most targeted to broadest:

### Tier 1: Directly related tests (always run)

| Changed file pattern | Test command |
|---------------------|-------------|
| `*.test.ts`, `*.test.tsx`, `*.spec.*` | Run those test files directly |
| Source files with co-located tests | `vitest related --run <changed-source-files>` |
| Python source files | `pytest <changed-test-files>` or project test command |

### Tier 2: Prompt/skill/eval tests (run when prompt content changes)

| Changed file pattern | Test command | Rationale |
|---------------------|-------------|-----------|
| `**/skillLoader*`, `**/FALLBACK_*`, prompt constants | Unit tests for the prompt module + eval tests | Prompt changes affect LLM behavior — unit tests verify structure, evals verify behavioral intent |
| `**/agent*.ts`, `**/route.ts` (agent endpoints) | Agent-related test files + eval | Agent changes need both correctness and behavioral verification |
| `**/eval/**` | Run the eval tests themselves | Eval changes must pass their own assertions |

### Tier 3: Broader validation (run when time allows)

| Scope | Test command |
|-------|-------------|
| Type check | `tsc --noEmit` / `mypy` |
| Lint | `biome check` / `ruff check` |
| Full test suite | `make test-web` / `make test-server` |

**Default**: Run Tier 1 always, Tier 2 when matched, Tier 3 only if PR body claims clean results and you want to verify.

**CI environment gotchas:**
- **ARIA selectors fail in headless CI** — `[aria-label="X"]` selectors don't resolve in headless environments because the accessible name tree is not rendered. Use `data-testid` or visible-text selectors in test files reviewed for CI compatibility.

## Eval Test Considerations

Eval tests call external LLM APIs — they are:

- **Slow** (30s-3min per scenario)
- **Non-deterministic** (LLM output varies)
- **Costly** (API tokens)
- **Require API keys** (.env.local with `ANTHROPIC_API_KEY`, `LANGFUSE_*`)

**Run evals when:**

- PR modifies LLM prompt content (fallback constants, skill prompts, system prompts)
- PR adds new eval scenarios (must verify they actually pass)
- PR changes tool descriptions or tool response formats (affects agent behavior)

**Interpreting eval results:**

| Result | Meaning | Impact on review |
|--------|---------|-----------------|
| All pass | Prompt changes don't break behavioral expectations | No impact (good signal) |
| Existing scenarios fail | Prompt change broke existing behavior | **Blocker** — flag as CRITICAL |
| New scenarios fail deterministically (2+ runs) | New assertions don't match agent behavior | **MEDIUM** — flag the gap between expectation and reality |
| New scenarios fail intermittently | Assertions too strict or borderline behavior | **LOW** — note flakiness, suggest broadening assertions |

**Eval maxTurns must cover workflow depth** — If the eval workflow has N sequential steps, set `maxTurns ≥ N`. A too-low ceiling cuts the agent mid-workflow, producing a false failure that looks like a prompt regression but is actually a configuration gap.

## Results Integration

Test results feed into Step 5 as `TEST` source and appear in:

### Step 5 classification

- A test failure for NEW code in the PR → `CODE` finding (the PR itself has a bug)
- A test failure for EXISTING code exposed by PR changes → `DOC` finding (pre-existing)
- An eval assertion mismatch → `CODE` finding on the eval test, with root cause analysis

### Step 6 draft — Verification Summary table

```
### Verification Summary

| Check | Result |
|-------|--------|
| Unit tests (N related) | M/N pass |
| Eval — existing scenarios | pass / FAIL (list) |
| Eval — new scenarios | pass / FAIL (list) |
| Type check | clean / N errors |
```

### Review event impact

| Test outcome | Default review event |
|-------------|---------------------|
| All tests pass | No change (APPROVE if no CODE findings) |
| Unit test failures | REQUEST_CHANGES (code is broken) |
| Eval failures (existing scenarios) | REQUEST_CHANGES (regression) |
| Eval failures (new scenarios only) | COMMENT (aspirational tests don't block, but must be acknowledged) |
