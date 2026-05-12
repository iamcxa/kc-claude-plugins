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

### 4e. Select agent tier

Use **filtered** line count (after noise removal) for tier selection:

| Tier | Condition | Agents | Est. cost (base) |
|------|-----------|--------|-------------------|
| **Lite** | `FILTERED_CHANGED < 200` AND no security files | `code-reviewer` + `comment-analyzer` | ~100K tokens |
| **Standard** | `200 ≤ FILTERED_CHANGED ≤ 500` OR security files | `code-reviewer` + `comment-analyzer` | ~140K tokens |
| **Full** | `FILTERED_CHANGED > 500` OR `CHANGED_FILES > 20` | `code-reviewer` + `comment-analyzer` + `security-reviewer` | ~210K tokens |

**Cost scaling caveat:** Base estimates assume ~200 lines. For larger PRs, expect ~1K tokens per 100 lines of diff per agent. A 4,000-line filtered diff with 3 agents ≈ 120K + overhead ≈ **150-200K tokens**. Add ~15K for pre-scan + ~20K for compliance audit.

**Note:** Error handling patterns (formerly `silent-failure-hunter`) are merged into `code-reviewer`'s prompt — same coverage, one fewer agent dispatch.

**Override**: User can request a specific tier (e.g., "full review" or "quick review") regardless of PR size.

**Display the triage decision** before dispatching:

```
## Triage Result
- PR size: 142 lines changed (8 files)
- Security files: none detected
- Agent tier: **Lite** (code-reviewer + comment-analyzer)
- Estimated context cost: ~120K tokens

Proceeding with Lite review. Say "full review" to override.
```

### 4f. Dispatch selected agents

Use `pr-review-toolkit:code-reviewer` and `pr-review-toolkit:comment-analyzer` as base agents (always dispatched). Add others per tier.

Dispatch all agents in parallel. **Also start Step 5a and 5b in parallel** — they only need the file list and project docs, not agent results.

**Default focus areas** (feature / bugfix / mixed):
- **code-reviewer**: Logic errors, bugs, style/convention violations, documentation accuracy. **Also check error handling**: empty catch/except blocks, swallowed errors (catch + log but no re-throw in critical paths), inappropriate fallbacks (returning default data instead of propagating errors), `continue-on-error` / `|| true` that silently mask failures. **GitHub Actions specific**: step sets output indicating failure but does NOT `exit 1` — downstream `if: success()` / `if: failure()` won't reflect actual status; the job always "succeeds" even when the step's output says failure.
- **comment-analyzer**: Stale TODOs/FIXMEs, commented-out code, misleading comments, debug leftovers, comment rot
- **security-reviewer**: Credential leaks, injection, OWASP top 10, RLS policy gaps

**Docs focus overrides** (when `PR_ARCHETYPE = docs`):
- **comment-analyzer** (PRIMARY): Terminology consistency with tool/API reference names, cross-reference completeness (Next Steps, See Also links), naming gaps between narrative and formal definitions. This agent catches text-accuracy issues that code-reviewer deprioritizes.
- **code-reviewer**: Validate code snippets in markdown against actual API (async/await, imports, param types). Check structural consistency between categorization tables and workflow/usage sections (items in wrong steps relative to their category).
- **security-reviewer**: Skip unless docs contain credential examples or config samples.

**Refactor focus overrides** (when `PR_ARCHETYPE = refactor`):
- **code-reviewer**: Behavioral equivalence (function bodies byte-identical after move), import graph correctness, re-export completeness, no accidental API surface expansion (newly-public symbols must be intentional)
- **comment-analyzer**: JSDoc/comment accuracy after move — file path references, cross-module `@see` links, section banners that reference old locations
- **code-reviewer error handling focus**: Skip error handling patterns unless error handling was restructured (check commit messages). For pure code-move refactors, error handling review adds noise.
- **security-reviewer**: Only if moved code touches auth/RLS paths

When refactoring, also add this to each agent prompt:

> This PR is a **refactoring/decomposition**. The author's intent is to reorganize code without changing behavior. Prioritize verifying behavioral equivalence over suggesting style improvements. Flag only: (1) logic changes hidden in the move, (2) broken imports/exports, (3) stale documentation references, (4) unintentional API surface changes.

**Baseline context in agent prompts:** When dispatching each agent, include this instruction:

> Before flagging a pattern as an issue, check whether the SAME pattern exists in unchanged code in the same file (sibling methods, existing handlers). If it does, note it as "follows existing convention" rather than flagging it as a violation. Read the full source file, not just the diff.

This prevents agents from producing false positives where new code follows established conventions that happen to be imperfect.

**Timeout expectations:** Agents typically finish in 1-3 min for <500 lines. For 1,000+ filtered lines, expect 3-6 min per agent. If an agent exceeds 8 min, check its output file directly.
