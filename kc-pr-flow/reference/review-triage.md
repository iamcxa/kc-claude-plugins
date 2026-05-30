# Review Triage

## Step 4: Triage — Agent Selection

Use PR metadata from Step 2 to determine which review agents to dispatch. This saves context by avoiding unnecessary agents on small PRs.

### 4a. Calculate PR size

From the metadata already fetched:
- `TOTAL_CHANGED = additions + deletions`
- `CHANGED_FILES` = file list from `gh pr diff NUMBER --name-only`

### 4b. Filter noise files (large PRs)

When `TOTAL_CHANGED > 1000`, scan the file list for generated/vendored files that inflate the diff without review value. Exclude them from the diff passed to agents:

```
NOISE_PATTERNS:
  **/data-seed*.sql        # seed data
  **/*.snap, **/*.snaplet*  # snapshot files
  **/generated/**, **/gen/** # code-gen output
  **/types/generated*       # generated type defs
  **/package-lock.json, **/pnpm-lock.yaml  # lockfiles
  **/*.min.js, **/*.min.css # minified assets
  **/migrations/*.sql       # auto-generated migrations (review separately if needed)
```

Display filtered stats:

```
- Raw diff: 19,813 lines (142 files)
- After noise filter: 4,200 lines (38 files) — skipped 104 noise files
- Noise files skipped: data-seed.sql (15K lines), .snaplet/ (12 files), ...
```

**Always show what was skipped** so the user can override. If user says "include all", disable filtering.

### 4c. Detect security-sensitive files

Check if any changed file matches security patterns:

```
SECURITY_PATTERNS: **/auth*, **/rls*, **/middleware*, **/webhook*, **/permission*, **/rbac*, **/vault*, **/secret*, **/token*, **/.env*
```

`HAS_SECURITY_FILES = true` if any changed file matches.

### 4d. Detect PR archetype

Scan PR title, body, and commit messages for archetype signals:

| Archetype | Signals | Effect |
|-----------|---------|--------|
| **Refactor** | Title/body contains "refactor", "decompose", "extract", "split", "move to", "break up"; high file-add + file-delete count with similar line counts; commit messages like "extract X into Y" | Adjust agent focus (see §4e) |
| **Feature** | Title starts with "feat", body describes new behavior | Default agent focus |
| **Bugfix** | Title starts with "fix", linked issue is a bug | Default agent focus |
| **Docs** | Only `.md` files changed, or title starts with "docs" | Prioritize comment-analyzer (see §4f) |

Set `PR_ARCHETYPE` = refactor / feature / bugfix / mixed. When archetype is **refactor**, display:

```
⚙ Detected PR archetype: **Refactor** (decomposition/extraction)
  Adjusting agent focus → behavioral equivalence over style
```

### 4d-probe. Detect break-point probe activation

Break-point probe (Step 4.5p) prevents approving a fix based on unit tests alone when the fix lives on a cross-layer runtime path.

**Set `PROBE_REQUIRED = true` when ANY of**:

1. PR body contains an unchecked manual verification checkbox. Detect via:
   ```bash
   gh pr view <N> --json body --jq .body | grep -E '^\s*-?\s*\[\s\]' | grep -iE 'manual|verif|qa|uat|e2e|end-to-end'
   ```
2. `PR_ARCHETYPE = bugfix` AND the diff touches files across ≥ 2 of: `ui`, `api`, `domain`, `storage`, `external-adapter` layers (use same layer patterns as `e2e-verification.md`).
3. `PR_ARCHETYPE = cross-stack` (frontend + backend changes in same PR).
4. User explicitly requests "deep verify" / "break-point check" / "pressure-test this fix" / "驗 wiring".

**Set `PROBE_REQUIRED = false` when ANY of**:
- `PR_ARCHETYPE = docs` or `refactor` or `style`
- `IS_MY_REPO = false` (probe needs local env access)
- Diff is purely internal utility with no caller in production path (grep callers; if all callers are tests/scripts, skip)

**Display** when probe is activated:

```
⚙ Break-point probe: ACTIVATED (reason: <unchecked manual verification | cross-layer bugfix | cross-stack | user request>)
  Will invoke kc-pr-flow:break-point-probe at Step 4.5p
  Estimated additional cost: ~10-25K tokens (level A/B) or ~30-50K (level C if stack warm)
```

### 4d-passmode. Detect 8-pass mode activation

8-pass mode forces structured coverage across 8 review dimensions, ensuring no dimension is silently skipped. Each dimension either produces findings or an explicit "Clean — verified by `<evidence>`" verdict. Same agents as the selected tier; pass-framing is a prompt-layer addition with ~0 token overhead.

**Set `FULL_PASS_MODE = true` when ANY of**:

1. User explicitly requests it: `--full-pass` / `--pass-all` flag, OR phrases like "8-pass review", "full pass", "全面複查", "do all passes", "deep review".
2. `PR_ARCHETYPE = bugfix` AND the diff touches files across ≥ 2 of: `ui`, `api`, `domain`, `storage`, `external-adapter` layers (same criteria as Step 4.5p probe activation).
3. `PR_ARCHETYPE = cross-stack` (frontend + backend changes in the same PR).
4. User accepted a "deep review" recommendation from a prior failure analysis or daemon report.

**Precedence**: explicit user intent wins. If the user requests `--full-pass` / `--pass-all` / "8-pass review", keep `FULL_PASS_MODE = true` even for small, docs, refactor, or style PRs. Only an explicit "skip passes" / "lite review" / "quick review" request can override an explicit full-pass request.

**Set `FULL_PASS_MODE = false` when no true condition above matched AND ANY of**:

- `PR_ARCHETYPE = docs`, `refactor`, or `style`.
- `FILTERED_CHANGED < 100` AND no security files AND no probe activation.
- User explicitly says "skip passes" / "lite review" / "quick review".

**Display** when 8-pass mode is activated:

```
⚙ Full-pass mode: ACTIVATED (reason: <bugfix cross-layer | cross-stack | user request>)
  Will run 8-pass coverage in Step 4-Pass; review body will include Pass Coverage table
  Additional cost: ~0 tokens (same agents; pass-framing is prompt-layer)
```

8-pass mode and break-point probe (Step 4.5p) share an activation profile by design — both respond to the "this is a real cross-layer change, not a refactor" signal. They are complementary: probe verifies the fix reaches the bug's break-point at runtime; 8-pass mode ensures every review dimension produces a verdict instead of a silent gap.

### 4e. Select agent tier

Use **filtered** line count (after noise removal) for tier selection:

| Tier | Condition | Agents | Est. cost (base) |
|------|-----------|--------|-------------------|
| **Lite** | `FILTERED_CHANGED < 200` AND no security files | `code-reviewer` + `comment-analyzer` + `silent-failure-hunter` (3) | ~140K tokens |
| **Standard** | `200 ≤ FILTERED_CHANGED ≤ 500` OR security files | Lite + `type-design-analyzer` + `pr-test-analyzer` (5) | ~200K tokens |
| **Full** | `FILTERED_CHANGED > 500` OR `CHANGED_FILES > 20` | Standard with extended context budget (full-file reads enabled per agent) | ~240K tokens |

**Cost scaling caveat:** Base estimates assume ~200 lines. For larger PRs, expect ~1K tokens per 100 lines of diff per agent. A 4,000-line filtered diff with 5 agents ≈ 200K + overhead ≈ **230-280K tokens**. Add ~15K for pre-scan + ~20K for compliance audit.

**Security coverage**: `tob-security-reviewer` always dispatches via Step 4-ToB-a regardless of tier — it is not part of the table above. `tob-supply-chain-checker` and `tob-actions-auditor` activate conditionally per Step 4-ToB-b/c. There is no separate `security-reviewer` in `pr-review-toolkit`; do not reference one.

**Override**: User can request a specific tier (e.g., "full review" or "quick review") regardless of PR size.

**8-pass mode tier floor**: When `FULL_PASS_MODE = true` (set in §4d-passmode) AND the size-based tier would be `Lite`, promote to `Standard`. Passes 1 (Correctness) and 5 (Test Coverage) require `type-design-analyzer` and `pr-test-analyzer` as primary owners — Lite tier doesn't dispatch them. Display the promotion: `Lite → Standard (8-pass mode requires type-design + pr-test owners)`.

**Display the triage decision** before dispatching:

```
## Triage Result
- PR size: 142 lines changed (8 files)
- Security files: none detected
- Agent tier: **Lite** (code-reviewer + comment-analyzer + silent-failure-hunter)
- Estimated context cost: ~140K tokens

Proceeding with Lite review. Say "full review" to override.
```

### 4f. Dispatch selected agents

Lite tier base agents (always dispatched): `pr-review-toolkit:code-reviewer`, `pr-review-toolkit:comment-analyzer`, `pr-review-toolkit:silent-failure-hunter`. Standard and Full add `pr-review-toolkit:type-design-analyzer` and `pr-review-toolkit:pr-test-analyzer`.

Dispatch all agents in parallel. **Also start Step 5a and 5b in parallel** — they only need the file list and project docs, not agent results.

**Default focus areas** (feature / bugfix / mixed):
- **code-reviewer**: Logic errors, bugs, style/convention violations, documentation accuracy. **GitHub Actions specific**: step sets output indicating failure but does NOT `exit 1` — downstream `if: success()` / `if: failure()` won't reflect actual status; the job always "succeeds" even when the step's output says failure.
- **comment-analyzer**: Stale TODOs/FIXMEs, commented-out code, misleading comments, debug leftovers, comment rot. **Scope-of-claim verification** (mandatory): for every "function X does Y" docstring or comment, ask **is Y actually possible at the point in the data flow where X operates?** Example: a docstring claims to strip tokens/emails/session-IDs but the implementation only extracts hostnames — those leak vectors live in path/query, not hostnames, so the claim's described capability is a no-op given the function's scope. This is *not* the same as "does the function do what the doc says" — it's "does the doc's claim even apply to the input X sees?" Also catch: count-drift in banner comments ("Five tests" when 4 follow), ephemeral identifiers in long-lived comments ("Round-1 review", "the new helper" — replace with PR# / commit SHA / stable anchor), endpoint enumerations in generic helpers (drift as callers change), dead defensive try/except clauses whose stated exception types can never fire.
- **silent-failure-hunter**: Empty catch/except blocks, swallowed errors (catch + log but no re-throw in critical paths), inappropriate fallbacks (returning default data instead of propagating errors), `continue-on-error` / `|| true` that silently mask failures, broad exception catching, mock/fake implementations leaking into production paths, **observability gaps in new helpers** (e.g. a new `_set_tag` that swallows without logging), **refactor side-effects** (existing outer `try/except` blocks that became over-broad after inner calls were moved into a self-swallowing helper — they now hide coding bugs instead of safety failures).
- **type-design-analyzer** (Standard+): Asymmetric contracts (parameters clamped/validated but defaults bypass the same guard), redundant sentinel members in allowlists, weak return signatures where a `Literal` would enforce the invariant, sentinel string overloading on real value channels (e.g. `"none"` / `"invalid"` mixed with real hostnames), tag-name + tag-value co-variance (each tag name has a tight value vocabulary).
- **pr-test-analyzer** (Standard+): Missing edge case tests for documented behavior (especially when the docstring promises stripping/protection but the test exercises a happier path), **sibling-site parity** (when a PR fixes a regression class on site A, are siblings B/C/D pinned with the same test? if not, the regression class is open at the unfixed sites), import-time / module-load test gaps (test calls helper, not the import site the helper was extracted from), happy-path forwarding tests for new helpers, `BaseException` propagation.

**Docs focus overrides** (when `PR_ARCHETYPE = docs`):
- **comment-analyzer** (PRIMARY): Terminology consistency with tool/API reference names, cross-reference completeness (Next Steps, See Also links), naming gaps between narrative and formal definitions. This agent catches text-accuracy issues that code-reviewer deprioritizes.
- **code-reviewer**: Validate code snippets in markdown against actual API (async/await, imports, param types). Check structural consistency between categorization tables and workflow/usage sections (items in wrong steps relative to their category).
- **silent-failure-hunter / type-design-analyzer / pr-test-analyzer**: Skip — no code paths to audit.

**Refactor focus overrides** (when `PR_ARCHETYPE = refactor`):
- **code-reviewer**: Behavioral equivalence (function bodies byte-identical after move), import graph correctness, re-export completeness, no accidental API surface expansion (newly-public symbols must be intentional)
- **comment-analyzer**: JSDoc/comment accuracy after move — file path references, cross-module `@see` links, section banners that reference old locations
- **silent-failure-hunter**: Restrict to error handling that was actually restructured (check commit messages). For pure code-move refactors, error handling review adds noise. **But always run** the refactor-side-effect check — outer `try/except` blocks around now-moved code are the #1 silent regression class in refactors.
- **type-design-analyzer**: Only when types are moved or re-exported. Flag API surface widening.
- **pr-test-analyzer**: Verify moved tests still cover the same behaviors at the new location; no new test coverage required.

When refactoring, also add this to each agent prompt:

> This PR is a **refactoring/decomposition**. The author's intent is to reorganize code without changing behavior. Prioritize verifying behavioral equivalence over suggesting style improvements. Flag only: (1) logic changes hidden in the move, (2) broken imports/exports, (3) stale documentation references, (4) unintentional API surface changes.

**Baseline context in agent prompts:** When dispatching each agent, include this instruction:

> Before flagging a pattern as an issue, check whether the SAME pattern exists in unchanged code in the same file (sibling methods, existing handlers). If it does, note it as "follows existing convention" rather than flagging it as a violation. Read the full source file, not just the diff.

This prevents agents from producing false positives where new code follows established conventions that happen to be imperfect.

**Baseline-convention check at meta level (extension):** apply the same primitive at a wider scope when reviewing SKILL.md output, reference docs, or cross-skill claims — not just code diffs. Before flagging a pattern in a `*.md` / `skills/**` / `reference/**` / `agents/**` file as an issue:

1. Grep the rest of the plugin (and adjacent plugins under the same repo / `~/.claude/skills/`) for the same pattern. Bound the search to ≤500 matches; if more, the pattern is unambiguously established
2. Count occurrences in unchanged code — if **3+ sibling sites** already use the pattern, treat it as an established convention, NOT a violation. Note it as "follows existing convention; consider standardizing or documenting if intentional"
3. **Explicit-instruction trump card**: if the pattern is documented as the convention in the same skill or a parent doc (e.g., a "use placeholder `OWNER/REPO` for examples" line in the skill body), treat as intentional regardless of sibling count

This suppresses false positives when one skill (e.g. `/review` from gstack) reviews another skill's output and the apparent "inconsistency" is actually the codebase's standard. **Example (kc-pr-flow PR #18 F1):** `/review` flagged `OWNER/REPO` placeholder usage as inconsistent; grep showed 7+ existing sites + an explicit instruction at SKILL.md L67 → false positive. The meta-level check catches this automatically.

**Confidence calibration in agent prompts:** When dispatching each agent, append this instruction to the prompt:

> For every finding you report, attach a **confidence score** (1-10):
>
> | Score | Meaning |
> |-------|---------|
> | 9-10  | Verified by reading specific code; concrete bug / exploit / contract violation demonstrated |
> | 7-8   | High-confidence pattern match; very likely correct given the code you read |
> | 5-6   | Moderate; could be a false positive given surrounding code you did not read |
> | 3-4   | Low confidence; pattern is suspicious but may be fine |
> | 1-2   | Speculation; only report if severity would be CRITICAL |
>
> Use the format: `[SEVERITY] (confidence: N/10) file:line — description`. If you cannot read enough surrounding context to attach a calibrated score, default to **6** with a "verify" caveat note.

**Pre-emit evidence requirement (append to every agent prompt):**

> For EACH finding, before you report it, quote the exact motivating line(s): `file:line` plus the verbatim source text that triggered the finding. Then re-read your own quote and ask: *does the quoted code actually say what my finding claims?*
> - "X doesn't exist" → quote the class/type/schema/`Meta` block where X would live.
> - "this branch/probe is dead/unreachable" → quote BOTH the guard you assume AND the decider/handler it duplicates; if they read different stores (e.g. a materialized view vs an event store in CQRS), they can diverge and the path IS reachable — do not report it as dead.
> - "this was reformatted / newly introduced" → quote the pre-PR line via `git show <base>:<file>`; if it pre-existed, do not report it.
> If you cannot produce a motivating quote that survives this self-check, set confidence to **4-5** and mark it `unverified`. Do NOT inflate to 7+ to bypass this. A finding with no surviving quote is a coverage note, not a defect.

The Step 6 collator applies these gates before populating the inline comments / advisory tables:

| Confidence | Destination |
|------------|-------------|
| 7-10       | Inline Comments (CODE) — show normally |
| 5-6        | Inline Comments (CODE) — show with caveat `"Medium confidence — verify"` |
| 3-4        | Advisory (DOC) — do not post as a PR comment |
| 1-2        | Drop entirely (exception: CRITICAL severity bypasses the drop) |

Findings without an explicit confidence score default to **6**. When the same finding appears from multiple sources (e.g. `code-reviewer` + `silent-failure-hunter`), take the **max** score and tag `MULTI-SOURCE: <sources>` to surface specialist agreement.

**Why this matters:** Agents over-report low-confidence patterns when they cannot read the full context window. The confidence dimension lets the collator suppress noise without losing real findings — preserving recall at high scores while filtering precision-misses at low scores.

**Timeout expectations:** Agents typically finish in 1-3 min for <500 lines. For 1,000+ filtered lines, expect 3-6 min per agent. If an agent exceeds 8 min, check its output file directly.

## Triage Heuristics — AI Reviewer Patterns

Triage refinements for handling AI-reviewer output (Copilot, summary bots, code-reviewer agents). These rules apply during Step 3 (review collection) and Step 4 (agent selection) — and equally to post-review comment triage in `kc-pr-review-resolve`.

### PR-level summary reviewer bodies are not noise

AI summary reviewers cross-reference multiple inline-thread findings and can elevate severity, surface impact patterns, or identify second-order effects that individual inline comments miss. Example seen in production: one reviewer flagged a "negative discount total" as advisory, another discussed the same area from a type perspective, and the summary bot cross-referenced both and elevated to CRITICAL with concrete impact ("revenue aggregates will be corrupted"). Treating "no inline threads from this reviewer" as a signal to skip their PR-level body discards real cross-reviewer synthesis.

**Triage rule**: Always read PR-level review bodies in full, even from summary bots. Skip only when the body is pure restatement of inline findings with no new cross-reference, severity adjustment, or impact analysis. The "summary" label is descriptive, not a quality signal.

### Empty-string placeholders in event-sourced sagas may be intentional

In event-sourced systems with an enrichment adapter (e.g., a publisher that resolves cross-domain references between emit and dispatch), sagas legitimately emit commands with empty-string placeholders for fields that require cross-domain lookups (`customer_id: ''`, `branch_id: ''`). The adapter enriches them to real values before they reach the target domain. AI reviewers commonly flag these as UUID/type-validation violations across multiple files (middleware schema, view evolve, router response mapping) — surfacing what looks like 4 distinct bugs but is one architectural decision viewed from different angles.

**Triage rule**: When an AI reviewer flags empty-string or placeholder values in a saga command as a type violation, trace the dispatch path for an enrichment adapter. If enrichment exists, the upstream schema intentionally uses lenient validation (e.g., `z.string()` not `z.string().uuid()`) and the AI finding is a false positive at the upstream layer. Group all related threads as one decision, reply once with the architectural rationale, and mark the cluster resolved together rather than litigating each thread independently.
