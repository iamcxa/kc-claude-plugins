# Compliance Audit

After agents finish, cross-reference findings against the project's documented best practices. The goal: **determine whether discrepancies are code bugs or documentation drift.**

## 5a. Identify relevant documentation

From the changed files list, find applicable rules:

```bash
# Read project CLAUDE.md and AGENTS.md
cat CLAUDE.md AGENTS.md 2>/dev/null

# If IS_MY_REPO=true, also consider personal ~/.claude/CLAUDE.md
```

Identify which **sections** of CLAUDE.md/AGENTS.md are relevant based on:
- File types changed (e.g., `.tsx` → Frontend rules, `.py` → Backend rules)
- Directories changed (match directory names against section headings in CLAUDE.md)
- Patterns in the diff (test files → Testing rules, imports → Code style rules)

## 5a-k. Knowledge layer (parallel with 5a/5b)

Dispatch `episodic-memory:search-conversations` to find past review lessons for the affected areas:

1. Extract 2-3 search terms from changed files (domain names, feature areas, key file names)
2. Search for past review experiences: "review {area}", "{filename} issue", "{domain} gotcha"
3. Note any findings as additional context for Steps 5c-5d:
   - Past false-positive patterns specific to this codebase
   - Known areas where baseline validation matters most
   - Previous documentation drift that was caught (or missed)
4. Read `.claude/review-lessons.md` if it exists in the project root — structured lessons from past reviews (written by Step 8). These are high-signal, project-specific insights that complement episodic memory search.

**Skip if**: PR is trivial (<50 lines, purely cosmetic) or changed files are in an area with no prior review history.

5. Read `${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md` for cross-project review patterns accumulated by this skill (D1 learnings). These are general insights that enhance review quality across all projects.

**Cost**: ~1 agent dispatch + 1-2 file reads, lightweight. Runs in parallel with 5a/5b — no added latency.

## 5b. Identify relevant skills

Dynamically discover applicable skills from the current session — do NOT rely on a hardcoded mapping.

**Discovery process:**

1. Collect the file extensions and top-level directories from the changed files list
2. Scan the session's available skill list (from system-reminder) for skills whose descriptions match:
   - File types in the diff (e.g., `.tsx` → skills mentioning "frontend", "React", "CSS")
   - Directory names (e.g., `agent/` → skills mentioning "agent development")
   - Domain keywords (e.g., `auth` → skills mentioning "security", "authentication")
3. Also check CLAUDE.md for explicit skill references or domain-to-skill mappings specific to the project

**Common domain categories to look for:**

| Signal in changed files | Domain | Skill keywords to match |
|------------------------|--------|------------------------|
| `*.tsx`, `*.css`, `src/app/` | Frontend | "frontend", "design", "component", "web" |
| `*.py`, `*.go`, `*.rs` | Backend | "backend", "api", "server", language name |
| `.github/workflows/`, `Makefile`, `Dockerfile` | CI/CD | "github-actions", "ci", "deploy" |
| `*.test.*`, `*.spec.*` | Testing | "test", "spec", "quality" |
| `*.sql`, `migrations/`, `supabase/` | Database | "database", "migration", "sql" |
| `cdk/`, `*.tf`, `*.yaml` (infra) | Infra | "infra", "secrets", "env" |

**Do NOT invoke these skills.** Only note their names and descriptions as reference for what best practices exist.

## 5c. Baseline consistency validation

**CRITICAL STEP — this prevents the most common false-positive pattern.**

Before classifying any agent finding, run this check:

1. **Read the full source file** (not just the diff) for each file with findings
2. For each finding, ask: **"Does unchanged code in the same file exhibit the same pattern?"**
   - Check sibling methods, existing handlers, neighboring functions
   - If YES → the finding is **at most NIT** — the PR follows established convention
   - If NO → proceed to root cause classification

**Common false-positive patterns to catch:**
- "Missing X" (validation, error handling, `run_in_executor`) when other handlers in the same file also don't have X
- "Should use pattern Y" when sibling methods don't use Y either
- "Edge case Z not handled" when the practical domain makes Z a <1% scenario — verify with domain context (which databases, which users, which inputs actually occur)
- "Inconsistent with existing code" based on one cherry-picked example rather than the full baseline

**Gate function symmetry:**
- "Gate function with asymmetric paths" — when a guard/gate has an early return for condition A but falls through for condition B, only path B is exposed at runtime. PRs with gate functions should verify ALL paths are guarded symmetrically. Sentry reports on the un-guarded path; treat as HIGH if on a security/auth boundary.

**Bash retry loop off-by-one:**
- When reviewing bash retry/loop logic with `-ge` vs `-gt` exit conditions: `if [ "$_retry" -ge "$RETRIES" ]` with `--retries 1` exits immediately after first failure (1 >= 1 = true → zero actual retries). `-ge` means "max counter value", `-gt` means "number of retries". The semantics are non-obvious and off-by-one bugs are common. Verify by tracing the counter with N=1.

**URL construction with pre-existing query params:**
- When a helper returns a URL with query params already attached (e.g., UTM tracking), appending a new path segment via string concatenation puts the path after the existing query string, producing a malformed URL. Tests miss this when they use clean URLs without query params. For PRs with URL construction that appends path segments, verify the base URL is clean (no query params). If two URL builders exist (display links with UTM vs programmatic deep links), the deep-link builder must use the pre-UTM base.

**Monorepo dependency version pins:**
- When reviewing dependency version pins in a monorepo with published packages, verify: (1) the pin is applied to ALL `package.json` files that declare the dependency — `pnpm.overrides` only protect the workspace install, not the published package's dependency range; (2) dep automation config (Dependabot `ignore` rules or Renovate `packageRules`) includes the pinned package to prevent re-bumping. Use `grep` across all `package.json` files for the package name, and check `.github/dependabot.yml` for matching ignore rules.

**Zustand store lifecycle reset at flow boundaries:**
- When a PR adds or modifies a Zustand store for a multi-step flow (booking wizard, onboarding, checkout), verify that `store.reset()` is called at the flow's terminal screen (success, confirmation, completion). The store and the terminal screen are typically separate files — the PR author may modify the store without touching the terminal screen. Symptom: stale draft data carries over to the next flow session. Grep for `reset()` call sites; if none exist at flow boundaries, flag it.

**Event sourcing removal PRs — layer-by-layer verification:**
- When a PR removes fields/commands/endpoints from an event-sourced domain, the primary review risk is **incomplete removal across layers**, not code quality in added code. Standard code-review agents focus on "what was added" — they're less effective at detecting "what was missed in removal." Use a layer-verification matrix (types → decider → view → contract → router → infra → seeds → frontend → permissions → tests) with grep confirmation. Also: legacy event types must be KEPT (not removed) with no-op view evolve for replay safety, and reason unions (e.g., DeletionBlocked) should be narrowed to match remaining guard conditions.

**Guard function coverage across ALL code paths:**
- When a PR introduces a guard function (e.g., `ensureEventStream()` for legacy data bootstrap), verify it's applied to ALL call sites of the guarded operation — not just the primary handlers in the changed files. Secondary code paths (clone, batch operations, migration scripts) that perform the same operation via different code locations are the most likely to be missed. Grep for all call sites of the guarded operation (e.g., `handleCommand`), then verify each has the guard.

**Docs grouping vs workflow cross-section consistency:**
- When documentation organizes items into semantic groups (e.g., "Metadata tools" vs "Diff tools" based on warehouse-access requirement) AND describes a workflow using those items (e.g., "Step 1: Understand → Step 2: Validate"), cross-check that items appear in workflow steps consistent with their category. Items may be described correctly in isolation but contradict their group classification when placed in the wrong workflow step.

**Severity calibration:** Even when a finding survives the baseline check, calibrate severity by asking:
- Does the issue have a mitigating factor? (e.g., per-tool warnings exist even if global instruction is stale → HIGH not CRITICAL)
- Is the affected code path exercised in practice? (edge case column casing → NIT)
- Is the behavior intentional and tested? (bare `except: pass` with a test validating it → MEDIUM not HIGH)

## 5d. Cross-reference and classify

For each review finding that **survives the baseline check**, classify its **root cause**:

| Root Cause | Meaning | Action |
|------------|---------|--------|
| `CODE` | Code violates a valid, current rule in CLAUDE.md/skills | Flag as inline comment on PR |
| `DOC` | Code is intentional/correct, but CLAUDE.md or a skill is outdated | Recommend documentation update (not a PR comment) |
| `NEW` | New pattern in the code not yet documented anywhere | Suggest adding to CLAUDE.md or creating a skill |

**Test failure classification (from Step 4.5t):**

| Test failure type | Root | Rationale |
|-------------------|------|-----------|
| Unit test fails on NEW code in the PR | `CODE` | The PR introduced a bug |
| Unit test fails on EXISTING code exposed by PR | `DOC` | Pre-existing issue, not caused by PR |
| New eval scenario fails deterministically | `CODE` (on the eval test) | Assertion doesn't match agent behavior — either fix the prompt or fix the assertion |
| Existing eval scenario fails after prompt change | `CODE` | Regression caused by PR |

**Key heuristic:** If the PR author clearly made an intentional design choice that contradicts a rule, and the choice is defensible, it's likely `DOC` (documentation drift), not `CODE`.

## 5e. Produce compliance summary

```
## Compliance Audit

### Rules checked:
- CLAUDE.md § "Frontend Test Quality" (clean output, act() wrapping)
- CLAUDE.md § "Pre-Commit Hook Behavior" (vitest related)
- Skill: web-agent-development (classifier, tool loop patterns)

### Documentation drift detected:
- CLAUDE.md § "Frontend Stack" says React 18 but PR uses React 19 `<Activity>` → DOC
- Skill `{backend-skill}` doesn't mention new test pattern found in PR → NEW

### No issues:
- AGENTS.md commit conventions ✓
- CLAUDE.md import patterns ✓
```

## Red Flags — STOP and Reconsider

- About to classify findings without running baseline validation (5c) — this is the #1 source of false positives
- Skipping CLAUDE.md/AGENTS.md read because "the agents already checked" — agents don't know project rules
- Posting DOC/NEW findings as inline PR comments — these are advisory only
- Ignoring knowledge layer results that contradict an agent's finding
- Flagging a pattern as CODE when 3+ unchanged files in the same repo use the same pattern — it's convention, not violation
- Reducing audit scope on large PRs without user's explicit override
- About to APPROVE based on static analysis alone when tests were available but not run — test results are ground truth
- Dismissing eval test failures as "non-deterministic" after only 1 attempt — run at least 2x with retry before concluding
- Accepting an AI reviewer finding that cites a general architectural principle (e.g., "domain layer must be pure") without checking project CLAUDE.md for an explicit override — project-specific conventions take precedence over general principles. Grep CLAUDE.md and convention docs before accepting
