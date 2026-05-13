---
name: kc-pr-review
description: Use when reviewing a GitHub PR and posting inline review comments. Triggered by PR number, PR URL, 'review this PR', 'review current branch PR'.
---

**Language rule (two layers)**:
- **Conversation-facing text** (status updates, confirmation prompts, findings tables shown to the user) — follows unified language preference. See plugin CLAUDE.md for query flow.
- **PR-facing artifacts** (review body, inline comment bodies, anything POSTed to GitHub) — **default to English** regardless of the conversation language, matching the convention for PR title / commit messages / code comments. Override only if the target repo's CLAUDE.md explicitly requires otherwise.

## Process Flow

```dot
digraph review_pr {
  rankdir=TB;
  node [shape=box];

  detect [label="Detect PR\n(number, URL, or current branch)"];
  fetch [label="Fetch PR metadata + diff"];
  concerns [label="Extract user concerns\n→ verification matrix"];
  ownership [label="Check repo ownership"];
  triage [label="Triage: filter noise,\nsize + security + archetype\n→ agent selection"];

  subgraph cluster_parallel {
    label="Parallel dispatch";
    style=dashed;
    prescan [label="Pre-scan (main context)\nCLAUDE.md rules\n+ stale refs\n+ dependency chains\n+ prompt consistency\n+ runtime data shape\n+ lint gate\n+ non-code scan\n+ dead export detection"];
    review [label="Review agents\n(code-reviewer,\ncomment-analyzer)"];
    tests [label="Test execution\n(worktree)\nunit + eval"];
    audit_prep [label="Compliance prep\n(5a: read docs,\n5b: match skills)"];
    knowledge [label="Knowledge layer\n(5a-k: episodic memory\n+ review-lessons.md)"];
    tob_security [label="ToB security reviewer\n(differential review,\nadversarial modeling)"];
    tob_supply [label="ToB supply chain\n(dep risk + insecure defaults)\n[conditional]"];
    tob_actions [label="ToB actions auditor\n(AI agent CI/CD vectors)\n[conditional]"];
    probe [label="Break-point probe\n(failure chain + A/B/C/D\n+ residual uncertainty)\n[bugfix/cross-stack]"];
  }

  classify [label="5c: Cross-reference\nagent + test findings\n+ root cause classify"];
  draft [label="Draft review:\nCODE table\n+ DOC/NEW advisory"];

  node [shape=diamond];
  confirm [label="User confirms\nreview?"];

  node [shape=box];
  post [label="Post review via\ngh pr review"];
  review_url [label="Return review URL"];

  node [shape=diamond];
  has_learning [label="Learning\ninsights exist?"];

  node [shape=box];
  capture [label="8: Learning\nD1: skill patterns\nD2: project knowledge"];
  write_knowledge [label="D1: auto-append\nD2: threshold → confirm\n→ write + commit"];
  end_node [label="Done"];

  detect -> fetch -> concerns -> ownership -> triage;
  triage -> prescan;
  triage -> review;
  triage -> tests;
  triage -> audit_prep;
  triage -> knowledge;
  triage -> tob_security;
  triage -> tob_supply [label="deps changed"];
  triage -> tob_actions [label="workflows changed"];
  triage -> probe [label="bugfix/cross-stack"];
  prescan -> classify;
  review -> classify;
  tests -> classify;
  audit_prep -> classify;
  knowledge -> classify;
  tob_security -> classify;
  tob_supply -> classify;
  tob_actions -> classify;
  probe -> classify;
  classify -> draft -> confirm;
  confirm -> post [label="approved"];
  confirm -> draft [label="edit requested"];
  post -> review_url -> has_learning;
  has_learning -> capture [label="yes"];
  has_learning -> end_node [label="none"];
  capture -> write_knowledge [label="approved"];
  capture -> end_node [label="skip"];
  write_knowledge -> end_node;
}
```

## Step 1: Detect PR

Accept PR number (`962`), PR URL (`https://github.com/owner/repo/pull/962` or `/changes` suffix), or no input (detect from current branch). Extract `owner/repo` dynamically — never hardcode.

Read → ${CLAUDE_PLUGIN_ROOT}/reference/gh-api-patterns.md § "PR Detection"

## Step 2: Fetch PR Metadata

Fetch title, body, diff, additions/deletions, changed files, commits, and author login. Save `PR_AUTHOR` for use in Step 7.

Read → ${CLAUDE_PLUGIN_ROOT}/reference/gh-api-patterns.md § "PR Metadata Fetch"

## Step 2.5: Extract User Concerns

Scan the PR body, linked issue descriptions, and user's review request message for **explicit verification concerns** — things the author or reviewer specifically calls out as "must not break", "should be unaffected", or "please verify".

Build a **verification matrix**:

```
## Verification Matrix (from PR body / linked issues / user request)

| # | Concern | Source | Verified? |
|---|---------|--------|-----------|
| V1 | PROJ-202 must not be affected | PR body | ⬜ |
| V2 | Langfuse tracing hierarchy preserved | User request | ⬜ |
| V3 | Prompt dual-path (Langfuse + fallback) | PR body | ⬜ |
```

Each concern becomes a **mandatory verification item** that must be addressed in the review body (Step 6). Agents are NOT responsible for these — the reviewer (you) performs targeted verification by reading the relevant code paths.

If no explicit concerns are found, skip this step. Do NOT invent concerns.

## Step 3: Check Repo Ownership

Determine `IS_MY_REPO` to decide which CLAUDE.md rule scope applies. **MUST execute the commands below — never infer ownership from PR authorship, branch name, or any other context.**

```bash
# 1. Get repo owner and your username (run both)
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
MY_USERNAME=$(gh api user --jq '.login')

# 2. Compare — if different, check org admin role
if [ "$REPO_OWNER" != "$MY_USERNAME" ]; then
  ORG_ROLE=$(gh api "orgs/${REPO_OWNER}/memberships/${MY_USERNAME}" --jq '.role' 2>/dev/null || echo "none")
fi
```

**Output checkpoint** (must display before proceeding):

```text
Ownership: REPO_OWNER=<value> MY_USERNAME=<value> ORG_ROLE=<value|n/a>
→ IS_MY_REPO=<true|false> (reason: <personal repo | org admin | not admin>)
```

- `IS_MY_REPO=true` (personal repo OR org admin): Apply `~/.claude/CLAUDE.md` + project `CLAUDE.md`.
- `IS_MY_REPO=false` (org member or external): Only the target repo's own `CLAUDE.md`/`AGENTS.md`. Do NOT apply personal rules.

## Step 4: Triage — Agent Selection

Calculate filtered diff size (noise files excluded), detect security-sensitive files, and select the agent tier (Lite / Standard / Full). Display the triage decision and estimated token cost before dispatching. Run agents in parallel with Steps 5a and 5b.

Read → ${CLAUDE_PLUGIN_ROOT}/reference/review-triage.md

## Step 4-ToB: Security Agent Dispatch (parallel with Step 4 agents)

Dispatch Trail of Bits security agents alongside existing review agents. Each agent returns structured YAML that feeds into Step 5 classification as `TOB` source.

### 4-ToB-a. tob-security-reviewer (always dispatch)

Dispatch the `tob-security-reviewer` agent with:
- `pr_number`, `owner_repo`, `changed_files` from Step 2
- `security_tier`: `full` if triage tier is Full, otherwise `standard`

This agent performs differential security review: risk triage, blast radius analysis, adversarial modeling, and attack scenario generation.

### 4-ToB-b. tob-supply-chain-checker (conditional)

**Activate when**: changed files include dependency manifests:
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- `requirements.txt`, `pyproject.toml`, `poetry.lock`, `Pipfile.lock`
- `Cargo.toml`, `Cargo.lock`
- `go.mod`, `go.sum`
- `Gemfile`, `Gemfile.lock`

Dispatch the `tob-supply-chain-checker` agent with:
- `pr_number`, `owner_repo`
- `dep_files`: filtered list of changed dependency files

This agent audits new/bumped dependencies for supply chain risk and scans for insecure default patterns.

**Skip when**: no dependency files changed.

### 4-ToB-c. tob-actions-auditor (conditional)

**Activate when**: changed files include `.github/workflows/*.yml` or `.github/workflows/*.yaml`.

Dispatch the `tob-actions-auditor` agent with:
- `pr_number`, `owner_repo`
- `workflow_files`: list of changed workflow file paths

This agent scans for 9 attack vectors targeting AI agents in CI/CD pipelines (expression injection, env var intermediary, dangerous sandbox, etc.).

**Skip when**: no workflow files changed.

### ToB findings integration

ToB agent findings merge into Step 5 classification:
- ToB findings with `severity: CRITICAL | HIGH` → classify as `CODE` (inline comment candidates)
- ToB findings with `severity: MEDIUM` → classify as `CODE` or `DOC` based on actionability
- ToB findings with `severity: LOW` → classify as `DOC` (advisory)
- ToB `clean_patterns` and `limitations` → include in review body as verification evidence

## Step 4.5: Pre-scan (main context, parallel with agents)

Lightweight checks that catch issues agents structurally cannot — rule violations, stale references, broken dependency chains. Runs in the main context alongside agent dispatch (~15K tokens, 15 seconds). Each check activates only when its condition matches.

### 4.5a. CLAUDE.md Rule Compliance

**Activate when**: any changed file's directory (or ancestor) contains a `CLAUDE.md`.

1. For each changed file, walk `dirname` upward to find the nearest `CLAUDE.md`
2. Extract lines containing MUST, NEVER, required, always, mandatory (case-insensitive)
3. Check each extracted rule against the diff — are any violated?

Only report violations with a specific file + rule citation. Do NOT report "I checked and found nothing."

### 4.5b. Stale Reference Detection

**Activate when**: diff removes or renames identifiers (function names, job names, export names, type names).

1. From `git diff --unified=0`, extract names that appear in removed lines (`^-`) but not in added lines (`^+`)
2. For each removed name, grep the repo for remaining references (excluding the diff itself)
3. Report stale references with file:line

Domain-specific patterns:

| File type | Identifier pattern | Grep scope |
|-----------|-------------------|------------|
| `.github/workflows/*.yaml` | Job names (`^  [a-z][-a-z]+:$`), step IDs | `needs:`, `outputs`, same + other workflow files |
| `*.ts` | `export` names | `import.*from`, `require(` |
| `domains/*/types.ts` | Event/command type names | Other domain `types.ts`, saga files |

### 4.5c. Dependency Chain Validation

**Activate when**: changed files match a domain with chain semantics.

| File pattern | Validation |
|-------------|-----------|
| `.github/workflows/*.yaml` | Every `needs:` value must reference an existing job key in the same file. Every renamed job must be updated in all `needs:` arrays. |
| `tsconfig*.json` path changes | Aliases must resolve to existing directories |

Use `grep`/`yq` — zero LLM tokens.

### 4.5d. Prompt Consistency Review

**Activate when**: diff modifies multi-line string literals or template literals (20+ lines) containing LLM instruction sections.

Detection (any of):
- Changed lines inside a template literal or multi-line string with section markers (`##`, `###`, `Step N`, `MUST`, `NEVER`, `Output format`)
- File contains prompt identifiers: `*_PROMPT`, `buildSystemPrompt`, `SYSTEM_PROMPT`, `systemPrompt`
- Diff touches a function that returns or assembles prompt text

**Process:**

1. **Extract full prompt text** — read the complete rendered prompt (not just diff hunks). If the prompt is assembled from multiple constants or conditionals, reconstruct the full text for each mode
2. **List conditional modes** — identify branches (`if/else`, ternary, `${condition ? A : B}`, function params like `skipRecce`) that produce different prompt variants
3. **Per-mode section audit** — for each mode, enumerate active sections and their directives (MUST/NEVER/always/required rules)
4. **Cross-check directive pairs** within each mode:

| Contradiction pattern | Example |
|----------------------|---------|
| Inclusion vs exclusion | "MUST include all sections" + "skip Section X" in same mode |
| Format vs flow | Output format expects field Y, but mode's flow never generates Y |
| Exhaustive quantifier vs conditional skip | "ALL findings" / "every check" language in a mode that skips checks |
| Ordering assumption | "after completing all checks" but mode skips some checks |
| Stale cross-reference | Section references "Step N above" but conditional reordering moves it |

5. **Report** each contradiction with:
   - The two conflicting lines (quoted)
   - Which mode triggers the conflict
   - Suggested resolution (scope the quantifier, add mode guard, or restructure)

**Scope limit**: Only review prompt text that the PR actually modifies. Do not audit unchanged prompts in the same file.

### 4.5e. Runtime Data Shape Audit

**Activate when**: diff modifies a function that transforms, strips, or re-renders structured input from an external source — agent output, API responses, webhook payloads, parsed files, MCP tool results.

Detection (any of):
- Function uses regex `.sub()`, `.replace()`, `JSON.parse` on input received from another system
- Function strips/replaces part of a text block (fenced blocks, JSON, XML sections)
- Rendering strategy changed (inline → builder, template → component, etc.)

**Process:**

1. **Identify the input source** — where does the data come from? Agent prompt? API? File parse? Another repo?
2. **Reconstruct full input shape** — find test fixtures, production examples, or cross-repo contracts that show the complete runtime input. If none exist, flag as a gap.
3. **Check for orphaned artifacts** — when the diff strips part of the input (e.g., a JSON block), check if the input has related structure BEFORE or AFTER the stripped part (headings, separators, metadata lines) that the diff doesn't handle.
4. **Check for dual rendering** — if the diff moves rendering from location A to location B, verify location A is fully cleaned (not just the data, but also surrounding markup).

**Report** each finding with:
- The input source and its full shape (or "shape unknown — no fixture/contract")
- The specific artifact the diff leaves orphaned
- Suggested fix (strip the artifact, or add a test with realistic input)

**Example (PROJ-203)**: PR strips a JSON fenced block from agent output and delegates rendering to a builder. But the agent also writes a heading before the JSON block. The heading is not in the diff — it's runtime behavior from a different repo's prompt. Result: orphaned heading + builder section = duplicate. Fix: strip the heading too.

### 4.5f. Lint Gate

**Activate when**: `IS_MY_REPO=true` AND changed files include lintable code (`.ts`, `.tsx`, `.js`, `.jsx`, `.py`).

**Skip when**: `IS_MY_REPO=false`, docs-only PR, or no linter config detected.

1. **Detect project linter** from config files in the repo root:
   - `biome.json` or `biome.jsonc` → `biome check` (TS/JS files only)
   - `.eslintrc*` or `eslint.config.*` → `eslint` (TS/JS files only)
   - `pyproject.toml` with `[tool.ruff]` → `ruff check` (Python files only)
   - Multiple linters → run each on its respective file types
2. **Run linter on changed files only** — filter `gh pr diff --name-only` by file extension, pass to linter
3. **Report violations as findings** with severity MEDIUM and source `PRESCAN`
4. **Non-null assertion special case**: if the project's CLAUDE.md explicitly disallows non-null assertions (`!`), flag biome `noNonNullAssertion` warnings as MEDIUM (not just info)

**Why agents miss this**: Review agents read code but don't execute linters. Format violations and lint errors are invisible to LLM-based analysis — they require tool output.

### 4.5g. Non-Code File Scan

**Activate when**: diff includes non-code files (config, fixtures, gitignore, lockfiles, dotfiles).

1. **Config file review** — for each changed config file (`.claude/settings.json`, `.env*`, `*.yaml` in config dirs):
   - Check for credentials, API keys, tokens (regex: `(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]+`)
   - Check for auto-install hooks that run unvetted dependencies (`pip install`, `uv pip install` in hook commands)
   - Check for daemon-starting hooks (`--daemon`, `guard`, background process spawning)
2. **Fixture PII scan** — for each changed `.json` file in `test*/`, `fixtures/`, `__fixtures__/`:
   - Scan for email patterns matching real domains (not `@example.com`, `@test.com`)
   - Scan for phone numbers, IP addresses, real names in structured data
   - Skip files under `node_modules/` or lockfiles
3. **Gitignore consistency** — if `.gitignore` is changed:
   - Check if newly gitignored paths have files committed in this PR (contradiction)
   - Check if committed files match existing gitignore patterns (accidentally force-added)
4. **Ephemeral file detection** — flag files that look developer-local:
   - `*.bak`, `*.swp`, `*.pid`, `*.lock` (non-package-manager locks)
   - Files under `.remember/`, temp directories
   - Settings backup files (`settings.*.bak`)

Report findings as MEDIUM (PII, credentials) or HIGH (auto-install hooks in shared config) with source `PRESCAN`.

### 4.5h. Dead Export Detection

**Activate when**: diff adds new `export` statements (TypeScript/JavaScript files).

1. **Extract new exports** — from `git diff` added lines (`^+`), find:
   - `export const NAME`, `export function NAME`, `export class NAME`
   - `export { NAME }` re-exports
   - Skip `export type` / `export interface` (type-only, no runtime impact)
2. **For each new export**, grep the repo for imports:
   - `grep -rn "import.*NAME" --include='*.ts' --include='*.tsx'` (excluding the defining file)
   - Also check barrel files (`index.ts`) that re-export it
3. **Flag zero-import exports** as NIT findings with source `PRESCAN`:
   - "New export `NAME` in `file.ts` has zero imports — verify it's wired into consumers or delete"
   - Exclude test files from the "must be imported" check (test exports are self-contained)

**Why agents miss this**: TypeScript compiles successfully with unused exports. LLM reviewers see the export and assume it's used — they don't grep for import counts.

### 4.5i. Helper Rollout Cross-File Pre-scan

**Activate when**: diff adds a new helper function whose body wraps a single underlying API call, AND the same diff replaces ≥3 existing call sites of that underlying API with the helper.

Detection:

1. From `git diff --unified=0`, find added function definitions (`+def NAME(`, `+function NAME(`, `+const NAME = (`, `+async function NAME(`, etc.)
2. For each added function, identify the wrapped call inside the function body — a single dominant API call the helper is a thin wrapper for (e.g. `sentry_sdk.set_tag`, `logger.info`, `httpx.get`). Skip helpers that wrap multiple distinct APIs (too noisy for auto-detection)
3. Count diff-level replacements: lines where the underlying API appears as removed (`^-`) and the helper appears on a corresponding added line (`^+`). Threshold: **≥3 replacements** in the diff itself
4. If the threshold is met, the diff is performing a **helper rollout**

Process:

1. **Grep the rest of the repo for remaining direct calls** to the underlying API:
   - `git grep -n "<api-call-pattern>" -- '<language-glob>'`
   - Exclude the helper-defining file (where the wrapped call legitimately lives inside the helper body)
   - Exclude files already touched by the diff (rollout's own context)
2. **For each remaining direct call**, report as a candidate "missed rollout" finding:
   - File:line, exact line content
   - Severity: **LOW** (the direct call may be intentional — protected by surrounding context, lives in a different abstraction layer, or is deliberately exempt)
   - Message: ``Helper `NAME` replaces `<api-call>` at N sites in this diff; `file:line` still calls `<api-call>` directly — verify intentional or part of follow-up rollout``
3. Report findings as source `PRESCAN`

**Why agents miss this**: `silent-failure-hunter` and `code-reviewer` analyze the diff and the files it touches, not the rest of the repo. This is a **cross-file consistency** check that requires the diff to define what "consistency" means (the new helper), then grep beyond the diff. Pure pre-scan — zero LLM tokens.

**Example pattern**: PR introduces `_set_tag(name, value)` wrapping `sentry_sdk.set_tag` in try/except. Diff replaces 14 of 17 call sites in the API layer. 3 remaining `sentry_sdk.set_tag` calls in a middleware file are NOT touched — they were always there, protected by a different outer try/except. The PR's "all sites use helper now" claim doesn't survive a cross-file grep. Whether to fix is an author judgment call; surfacing the inconsistency is the pre-scan job.

**Related pattern**: see `reference/learned-patterns.md` "Telemetry safety helper completeness — wrap ALL related calls or none (2026-05-06)" for the broader D1 class this operationalizes.

### Pre-scan output

Findings feed into Step 5 classification as `PRESCAN` source (alongside agent findings). They follow the same CODE/DOC/NEW classification in Step 5d.

## Step 4.5t: Test Execution (parallel with agents)

Run the PR's own tests in an isolated worktree to catch issues that static analysis misses. **Test results are a first-class review signal** — they can downgrade APPROVE to COMMENT or upgrade a finding's severity.

**Activate when**: `IS_MY_REPO=true` AND changed files include testable code (`.ts`, `.tsx`, `.py`, etc.).

**Skip when**: `IS_MY_REPO=false`, docs-only PR, or user requests "quick review" / "skip tests".

1. Create worktree from PR branch, install deps, copy `.env.local` if eval tests are needed
2. **Tier 1** (always): run `vitest related` / `pytest` on changed files
3. **Tier 2** (when prompt/skill/eval files changed): run eval tests for affected scenarios
4. Clean up worktree
5. Feed results into Step 5 as `TEST` source

**Eval test failures change the review event:**

| Outcome | Effect |
|---------|--------|
| Unit test failure | REQUEST_CHANGES |
| Existing eval scenario fails | REQUEST_CHANGES (regression) |
| New eval scenario fails deterministically | COMMENT (not APPROVE) |
| All pass | No change |

Read → ${CLAUDE_PLUGIN_ROOT}/reference/test-execution.md

## Step 4.5p: Break-point Probe (parallel with agents)

Verify that the fix is actually on the runtime path, not just correct in isolation. **Prevents APPROVE-on-unit-tests-alone theater** for bugfix / cross-stack PRs.

**Activate when** ANY of:
- PR body contains an unchecked "manual verification" / "QA" / "UAT" checkbox
- `PR_ARCHETYPE = bugfix` AND diff spans ≥ 2 layers (UI ↔ backend, backend ↔ external, domain ↔ storage)
- `PR_ARCHETYPE = cross-stack`
- User explicitly requests "deep verify" / "break-point check" / "pressure-test this fix"

**Skip when**:
- Docs-only / refactor / style PR
- PR is purely internal utility with no user-facing path
- `IS_MY_REPO = false` (can't run level B/C probes reliably)

**Execution:**

Invoke `Skill: kc-pr-flow:break-point-probe` with PR context (diff, body, linked issue). The skill returns a strict YAML output contract declaring:
- `break_point` (file:line of fix)
- `failure_chain` (ordered user→symptom steps)
- `unit_coverage` vs `runtime_gap`
- `probe_decision.verified_at` (A/B/C/D)
- `residual_uncertainty` (what could still be wrong)
- `recommended_human_probe` (concrete follow-up steps)

**Silent-failure prevention:** The skill's output contract forbids empty `residual_uncertainty` and forbids claiming a higher probe level than what was actually executed. If the probe output shows `verified_at: A` but classification of the PR called for `C`, treat it as a gap — not a pass.

**Integration with Step 5 and Step 6:**
- Probe output is an input to Step 5 classification as source `PROBE`
- `residual_uncertainty` items appear in Step 6 draft under a dedicated **Break-point Coverage** section of the review body
- If `probe_decision.verified_at` is only A/B but the failure chain touches external systems (dbt, Stripe, etc.), the default review event becomes COMMENT (not APPROVE), and the user is prompted at the confirmation gate to either accept residuals or run the recommended human probe before merge

Read → ${CLAUDE_PLUGIN_ROOT}/skills/break-point-probe/SKILL.md

## Step 5: Compliance Audit

Read relevant CLAUDE.md/AGENTS.md sections, identify applicable skills by dynamic discovery, and search episodic memory + project review-lessons + skill learned-patterns for past insights in the affected areas. Cross-reference agent findings **and test results**: run baseline consistency validation (does unchanged code in the same file already exhibit the same pattern?), then classify each surviving finding as CODE / DOC / NEW. Test failures from Step 4.5t are classified as `TEST` source — a unit test failure on new code is `CODE`, an eval assertion mismatch on new scenarios is `CODE` on the eval file. Break-point probe output from Step 4.5p is classified as `PROBE` source — `residual_uncertainty` items become `DOC`-advisory in the review body under "Break-point Coverage", and `recommended_human_probe` entries are surfaced at the confirmation gate so the user can decide whether to run them before merge.

Read → ${CLAUDE_PLUGIN_ROOT}/reference/compliance-audit.md

## Step 6: Draft Review & Confirm

Present findings in **two separate tables**: one for actionable inline comments (CODE), one for advisory items (DOC/NEW). This prevents DOC/NEW items from being accidentally posted.

### 6a. Inline Comments (CODE) — will be posted

```
## PR #962 — Inline Comments

| # | File:Line | Severity | Summary |
|---|-----------|----------|---------|
| 1 | config.jsonl:11 | CRITICAL | API key in plaintext |
| 2 | .gitignore:421 | HIGH | *.db pattern too broad |
| 3 | handler.ts:88 | MEDIUM | Stale TODO from 2024, feature already shipped |

Event: REQUEST_CHANGES
```

### 6b. Advisory Items (DOC/NEW) — will NOT be posted

```
## PR #962 — Advisory (not posted as PR comments)

| # | File:Line | Root | Summary | Suggested Action |
|---|-----------|------|---------|------------------|
| A | AGENTS.md:349 | DOC | Contradicts Linear usage — rule outdated | Update CLAUDE.md |
| B | utils.ts:12 | NEW | New retry pattern, undocumented | Add to CLAUDE.md or create skill |
```

### 6b½. Verification Summary (when tests were run)

When Step 4.5t executed, include a verification table in the review body:

```
### Verification Summary

| Check | Result |
|-------|--------|
| Unit tests (N related) | M/N pass |
| Eval — existing scenarios | pass / FAIL (list) |
| Eval — new scenarios | pass / FAIL (list) |
| Type check | clean / N errors |
```

This table appears in the review body between the inline comments section and the advisory section. It provides concrete evidence for the review event choice.

### 6b¾. Break-point Coverage (when Step 4.5p ran)

When Step 4.5p executed, include a coverage summary in the review body:

```
### Break-point Coverage

Break-point: <file:line>
Failure chain: N steps total, M verified at level X

Verified runtime steps: [<indices>]
Unverified runtime steps: [<indices>]

Residual uncertainty:
- <assumption> (probability: <level>) → <failure_mode>

Recommended follow-up (optional, before merge):
- <action> — covers steps [<indices>], cost <estimate>, gain <level up>
```

Placement: between Verification Summary and the advisory section.

**Event modifier**: If `probe_decision.verified_at` ∈ {A, B} AND failure chain touches an external system (third-party API, DB/cache with its own semantics, CI/CD), the default event becomes COMMENT instead of APPROVE. User can override at the confirmation gate if they explicitly accept the residual uncertainty.

### 6c. User confirmation gate

**GATE — Do not post without user confirmation.** Always present both tables and then offer structured options:

```
Ready to post. Choose an option:

1. Post inline comments only (CODE items)
2. Post inline comments + advisory (CODE + DOC/NEW in review body)
3. Edit — move/remove/reword items, change event
4. Cancel — don't post
```

Wait for explicit selection. If user picks **3**, let them:
- Move items between tables (e.g., reclassify DOC → CODE to post it)
- Remove comments they disagree with
- Edit comment text
- Change the review event (APPROVE / REQUEST_CHANGES / COMMENT)

Then re-present the tables and options.

## Step 7: Post Review

Prefer `gh pr review` CLI. Use `gh api` as fallback for inline comments (CLI lacks native inline support). Write JSON payload to temp file to avoid shell escaping issues; always tag `@PR_AUTHOR` in the review body.

Read → ${CLAUDE_PLUGIN_ROOT}/reference/gh-api-patterns.md § "Review Payload"

## Step 8: Learning (MANDATORY — run immediately after Step 7)

**BLOCKING**: Do NOT respond to other user requests between Step 7 and Step 8. Complete learning evaluation first, then address any pending requests. Mid-flow interruptions (e.g., user asks to modify skill, resolve findings) must queue until Step 8 finishes.

After review completion, evaluate findings for knowledge capture across two dimensions.

**Dimension 1 (skill-level)**: General review patterns discovered during this session → auto-append to `${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md`. No confirmation gate.

**Dimension 2 (project-level)**: Project-specific insights from DOC/NEW findings and recurring CODE patterns → apply write threshold (severity gate + three-question test), present candidates, confirm before writing to project's `CLAUDE.md` or `.claude/review-lessons.md`.

**Skip when**: No insights in either dimension.

Read → ${CLAUDE_PLUGIN_ROOT}/reference/knowledge-capture.md

## Rules

- **Confirm before posting** — never submit a review without user approval
- **Dynamic repo detection** — use `gh repo view`, never hardcode owner/repo
- **Ownership check** — only apply personal CLAUDE.md rules to repos you own (personal or org admin)
- **Temp file for JSON** — avoid `--raw-field` for complex payloads; use `--input`
- **One review per submission** — batch all inline comments into a single review API call
- **Severity labels** — use CRITICAL / HIGH / MEDIUM / LOW / NIT consistently
- **Root cause classification** — every finding MUST have a Root label (CODE / DOC / NEW); only CODE items become inline comments
- **DOC/NEW findings are advisory** — present them to the user but do NOT post as PR comments; suggest filing a separate issue or updating CLAUDE.md
- **Comment-analyzer always runs** — abnormal comments (stale TODOs, commented-out code, debug leftovers) are first-class findings, not afterthoughts
- **Skills are reference only** — during compliance audit, read skill descriptions to understand best practices but do NOT invoke skills
- **Tag the PR author** — always include `@PR_AUTHOR` in the review body to ensure GitHub notification delivery. Fetch author login in Step 2 via `gh pr view NUMBER --json author --jq '.author.login'`
- **PR-facing artifacts in English** — the review body and every inline comment body POSTed to GitHub default to English regardless of the user's conversation language. This matches the convention for PR title / commit messages / code comments and keeps non-Chinese-speaking reviewers / authors unblocked. Conversation summaries, confirmation prompts, and findings tables shown to the user still use the conversation language. Override only if the target repo's CLAUDE.md explicitly requires the review body in another language. **Apply at draft time, not after posting** — translating in place via API is possible but leaves "edited" markers on every comment.
- **Refactoring PRs — behavioral equivalence first** — when `PR_ARCHETYPE = refactor`, prioritize verifying that moved code is functionally identical. Style suggestions on moved-but-unchanged code are noise; only flag actual behavioral changes hidden in the move
- **Refactoring PRs — consumer audit** — verify all importers of moved symbols have been updated. Use `Grep` to find all imports of the original module and confirm they now point to the new location (or a re-export barrel)
- **Refactoring PRs — API surface diff** — list any symbols that became newly public (exported from a new module that were previously file-private). Flag unintentional exposure
- **Refactoring PRs — stale references** — JSDoc `@see`, cross-file comments like "see route.ts", and section banners referencing the pre-refactor file structure must be updated
- **Verification matrix in review body** — when Step 2.5 produces verification items, include a completed matrix table in the review body showing how each concern was verified. This replaces ad-hoc "I also checked X" prose
- **D1 auto-append** — skill-level patterns are appended to `learned-patterns.md` without gate; briefly notify user what was added
- **D2 gated write** — project-level patterns require write threshold (severity gate + three-question test) + user confirmation
- **Minimal knowledge edits** — when writing to CLAUDE.md, make the smallest possible change; never rewrite unrelated sections
- **review-lessons.md is project-scoped** — create in the reviewed project root (`.claude/review-lessons.md`), never in the plugin directory
- **Separate knowledge commit** — D2 writes get their own commit (`docs: capture review lessons from PR #NNN`), never bundled with other changes
- **Actionable rules only** — captured rules must be specific and testable; reject vague "be careful with X" formulations
- **Step 8 is not deferrable** — "user asked something else" is NOT a reason to skip Learning. Queue the user's request, complete Step 8 (typically <30s), then address it. The rationalization "I'll come back to it" never materializes after context switch
- **Tests before verdict** — never decide APPROVE/COMMENT/REQUEST_CHANGES based on static analysis alone when tests are available. Test results are ground truth; static analysis is advisory
- **Test failures override static analysis** — if static analysis finds no issues but tests fail, the review event must reflect the test failures (COMMENT or REQUEST_CHANGES), never APPROVE
- **Eval tests need double confirmation** — eval tests are non-deterministic. A single failure may be flaky. Run at least twice (with retry) before reporting as a deterministic failure. 4 consecutive failures (2 runs x 2 retries) = deterministic
- **Worktree cleanup is mandatory** — always `git worktree remove` after test execution, even on failure. Never leave stale worktrees
- **Break-point probe for bugfix/cross-stack** — invoke `kc-pr-flow:break-point-probe` in Step 4.5p for bugfix or cross-stack PRs, or when PR body has an unchecked manual-verification checkbox. Skipping is a gap, not an optimization
- **Probe evidence must match claimed level** — a probe report claiming `verified_at: C` must include evidence of an actual runtime call (HTTP/RPC/subprocess output). Static trace is A, test runs are B. Silent level-inflation is worse than no probe
- **Probe must declare residual uncertainty** — unless `verified_at: D`, `residual_uncertainty` must be non-empty. An empty list claims omniscience and is always wrong
- **External-system fixes default to COMMENT, not APPROVE** — when the failure chain touches a third-party system (dbt, Stripe, Snowflake, GitHub API, etc.) and probe verified only at A or B, the default review event is COMMENT. User can override at the confirmation gate after acknowledging the gap
