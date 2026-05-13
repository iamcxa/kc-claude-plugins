---
name: kc-pr-create
description: Use when user says 'create pr', 'open pr', '建立 PR', '開 PR', '發 PR', '送審', or when implementation is complete and changes need a pull request on GitHub.
argument-hint: "[--draft-only] [--ci] [--no-announce] [--max-rounds N]"
---

All text output follows unified language preference. See plugin CLAUDE.md for query flow.

# Create PR — Full Lifecycle

Default: create draft PR → self-review & fix → mark ready → announce. One command, no stops.

## Invocation

```
/kc-pr-create [--draft-only] [--ci] [--no-announce] [--max-rounds N]
```

| Flag | Default | Effect |
|------|---------|--------|
| (none) | **ship mode** | Draft → review loop → ready → announce |
| `--draft-only` | — | Create PR only (Steps 1-9), skip ship chain |
| `--ci` | off | After ready: poll CI + offer AI reviewer wait |
| `--no-announce` | — | Ship but skip announce |
| `--max-rounds N` | 3 | Self-review loop iteration limit |

## Process

```
1.  Analyze          ─┐
1.5 E2E Suggestion    │
2.  Title              │ Part A: Create Draft PR
3.  Body               │ (always runs)
4.  Confirm            │
5.  Create (--draft)   │
6.  Annotate           │
7.  Confirm comments   │
8.  Post comments      │
9.  Linear Comment    ─┘
    │
    ├─ --draft-only → Step 13 (Announce, legacy behavior) → Done
    │
10. Self-Review Loop  ─┐
11. Mark Ready          │ Part B: Ship Chain
12. CI + AI Gate (--ci) │ (default, skip if --draft-only)
13. Announce            │
14. Done              ─┘
```

**Small PR shortcut** (<100 lines, single file): skip Steps 6-8.

## Step 1: Analyze

Read → `${CLAUDE_PLUGIN_ROOT}/reference/gh-api-patterns.md` § "PR Detection"

If PR exists, ask user: update or skip.

## Step 1.5: E2E Verification Suggestion (conditional)

**Skip conditions** (any one → skip silently):
- No `.claude/e2e/mappings/` directory (e2e pipeline not set up in this project)
- Diff is single-layer only (frontend-only or backend-only)
- PR is docs-only, deps-only, or test-only

**Detection**: Read → `${CLAUDE_PLUGIN_ROOT}/reference/e2e-verification.md` for layer classification patterns.

After analyzing the diff (Step 1), classify changed files into layers. If diff touches 2+ layers → integration change detected.

**Present suggestion:**

```
⚡ This PR modifies frontend-backend integration:
  - Backend: <list of backend files>
  - Frontend: <list of frontend files>

E2E verification creates a repeatable flow proving the feature works.
  1. /e2e-walkthrough --verify — interactive verification (generates reusable flow)
  2. /e2e-test <existing-flow> --video — replay existing flow with recording
  3. Skip — proceed to PR creation
```

- Option 1/2: pause PR creation, run e2e, return to Step 2 after completion.
- Option 3 or "skip": continue to Step 2 normally.
- If existing verification flows (tagged `verification` in `.claude/e2e/flows/`) match the changed areas, prefer option 2.

## Step 2: Title (Conventional Commit)

**Format:** `<type>(<scope>): <description>` — under 70 chars, lowercase, no period, imperative.

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Scope — two modes:**

| Mode | When | Examples |
|------|------|---------|
| **Issue** | 1 primary ticket | scope = ticket ID: `fix(PROJ-201):`, `feat(issue-335):` |
| **Code** | No ticket, or 3+ tickets | scope = module name: `feat(mcp):`, `chore(deps):` |

**2-ticket PR**: use Issue scope with the primary ticket. Mention the other in body.

**3+ tickets**: use Code scope. List all issues in body.

**Type**: determine from nature of changes, not branch prefix. `fix/` branch with mostly new features → `feat`.

## Step 3: Body

**Project template takes priority.** Check `.github/PULL_REQUEST_TEMPLATE.md` first. If it exists, use it as base structure and fill each section. Merge in `## Summary`, `## Reviewer Guide`, `## Test plan` only where the template has gaps.

If no template, use this adaptive format (scale sections to PR size):

```markdown
## Summary
- **ISSUE-ID**: one-line description (or just a bullet for small PRs)

## Reviewer Guide (large PRs only: >300 lines or 3+ issues)

| Issue | What | Key files / functions |
|-------|------|---------------------|
| ID | What changed | `file.py` → `function()` |

**Design notes for reviewers:**
- Non-obvious decisions

## Test plan
- [ ] test command and result

Closes ISSUE-ID

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Step 4-5: Confirm & Create

Present draft, wait for approval. Then:

```
Read → ~/.claude/kc-plugins-config/identity.yaml
```

**Ship mode (default)** — always create as draft:
```bash
git push -u origin $(git branch --show-current)
gh pr create --draft --title "TITLE" --body "$(cat <<'EOF'
BODY
EOF
)" --assignee @me
```

**`--draft-only` mode** — create normally (no `--draft`):
```bash
git push -u origin $(git branch --show-current)
gh pr create --title "TITLE" --body "$(cat <<'EOF'
BODY
EOF
)" --assignee @me
```

Capture `PR_NUMBER` and `PR_URL` from output for subsequent steps.

**Assignee**: always `--assignee @me` (from identity config; if config file missing, still use `@me`). **DCO**: check project CLAUDE.md/AGENTS.md for "signoff" or "DCO" — if found, add `--signoff`.

## Step 6: Self-Review Annotations

Skip if <100 lines changed. Target 4-8 comments for larger PRs.

**What to annotate:**

| Category | Signal |
|----------|--------|
| Design decisions | "Why X instead of Y" |
| Non-obvious behavior | Intentional try/except, fail-safe patterns |
| Cross-file relationships | Shared constants, imports across modules |
| Priority/ordering logic | Classification order, fallback chains |
| SDK/framework quirks | Workarounds for library behavior |

**Skip:** self-explanatory code, test files, docs-only, deps bumps.

## Step 7-8: Confirm & Post

Present comments table, wait for approval.

Read → `${CLAUDE_PLUGIN_ROOT}/reference/gh-api-patterns.md` § "Review Payload"

## Step 9: Linear Comment

After PR is created, post a brief comment on the linked Linear issue(s).

Read → `${CLAUDE_PLUGIN_ROOT}/reference/linear-integration.md`

**If `--draft-only`**: skip to Step 13 (Announce, legacy behavior) then Done.

---

## Step 10: Self-Review & Fix Loop

Dispatch review agents to identify code issues, fix all findings (including suggestions), repeat until clean.

### 10a. Dispatch Review Agents

Run in parallel — use the same tiering as `kc-pr-review` Step 4 (see `reference/review-triage.md` §4e). Pre-PR self-review must be **at least as strict as** post-PR review, never weaker.

**Lite tier** (`FILTERED_CHANGED < 200` AND no security files):
- `pr-review-toolkit:code-reviewer` — code quality, bugs on the PR diff
- `pr-review-toolkit:comment-analyzer` — comment accuracy, stale references, scope-of-claim docstring verification
- `pr-review-toolkit:silent-failure-hunter` — silent error swallowing, refactor side-effects (try/except now-overbroad), observability gaps in new helpers

**Standard tier** (`200 ≤ FILTERED_CHANGED ≤ 500` OR security files): Lite + 
- `pr-review-toolkit:type-design-analyzer` — asymmetric contracts, redundant sentinels, weak return signatures, sentinel-string overloading
- `pr-review-toolkit:pr-test-analyzer` — missing edge case tests, sibling-site test parity, import-time test gaps

**Full tier** (`> 500 LOC` OR `> 20 files`): Standard with extended context budget (agents may read full files, not just diff).

**Rationale**: pre-PR self-review weaker than post-PR review is the wrong direction — finding bugs after the PR opens means a round trip with the reviewer. The historic 2-agent dispatch caused this gap; PR #1145 shipped with 7 CRITICAL/HIGH silent-failure findings + 1 HIGH type-design finding caught by post-PR review (learned-patterns.md L107). Pressure test on PR #1307 confirmed the same pattern (pressure-test-pr1307.md).

If `pr-review-toolkit` unavailable: run lightweight main-context pre-scan only (CLAUDE.md compliance, stale refs, unused imports). Warn and continue.

Also run main-context pre-scan (parallel with agents):
- CLAUDE.md rule compliance (same logic as kc-pr-review Step 4.5a)
- Stale reference detection (same logic as kc-pr-review Step 4.5b)

### 10b. Classify Findings

| Classification | Ship action |
|----------------|-------------|
| CODE (CRITICAL → NIT) | **Fix** |
| SUGGESTION | **Fix** — all suggestions get addressed |
| DOC/NEW (advisory) | Note in summary, don't block |

### 10c. Fix & Push

```
Ship review round 1/3:
  Fix: 3 items (1 HIGH, 1 MEDIUM, 1 NIT)
  Advisory: 1 DOC item (noted)

  Fixing...
  ✓ config.ts:42 — moved secret to env var
  ✓ handler.ts:88 — removed stale TODO
  ✓ utils.ts:15 — removed unused import
```

Commit: `fix: address self-review findings`
Push immediately after commit.

### 10d. Re-review or Exit

- Still has CODE/SUGGESTION findings → re-run 10a-10c (next round)
- Zero CODE/SUGGESTION → **APPROVE** → proceed to Step 11
- Max rounds reached → report remaining, proceed to Step 11 anyway

```
Ship review: APPROVE after 2 rounds (5 items fixed, 1 advisory noted)
```

## Step 11: Mark Ready

```bash
gh pr ready <PR_NUMBER>
```

```
PR #<NUMBER> marked ready for review.
```

If `--ci` NOT set → skip to Step 13 (Announce).

## Step 12: CI + AI Reviewer Gate (--ci only)

### 12a. CI Gate

Poll CI checks until all pass or timeout (5 min):

```bash
for i in $(seq 1 20); do  # 20 × 15s = 5 min
  STATUS=$(gh pr checks <PR_NUMBER> --json name,state \
    --jq 'if all(.state == "SUCCESS") then "pass"
          elif any(.state == "FAILURE") then "fail"
          else "pending" end')
  case "$STATUS" in
    pass) break ;;
    fail) break ;;
    pending) sleep 15 ;;
  esac
done
```

Present progress:
```
CI checks:
  ✓ lint (12s)
  ✓ test (45s)
  ⏳ deploy-preview... (polling 2/5 min)
```

**On CI pass**: proceed to 12b.

**On CI failure**: report which check failed + log summary. Ask:
```
CI check 'test' failed.
  1. View logs and fix → re-push → re-poll
  2. Skip CI gate, proceed to announce
```

### 12b. AI Reviewer Gate

```
PR ready, CI passed. AI reviewers may auto-trigger.
  1. Wait for AI reviewer response (~1 min)
  2. Skip, proceed to announce
```

If user selects 1 — poll for new reviews:

```bash
BASELINE_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for i in $(seq 1 6); do  # 6 × 10s = ~1 min
  sleep 10
  NEW_REVIEWS=$(gh api repos/OWNER/REPO/pulls/PR_NUM/reviews \
    --jq "[.[] | select(.submitted_at > \"$BASELINE_TS\")] | length")
  [ "$NEW_REVIEWS" -gt 0 ] && break
done
```

**AI reviewer has findings** → fix → push → re-poll CI (back to 12a). Max 2 AI-fix rounds.

```
AI reviewer: Copilot — 2 suggestions
  Fixing... ✓ 2 items fixed, pushed.
  Re-running CI... ✓ All pass (38s)
  Re-polling AI... ✓ No new findings.
```

**No response after 1 min**:
```
No AI reviewer response after 1 min. Proceeding to announce.
(Run /kc-pr-review-resolve later if they respond.)
```

## Step 13: Announce (conditional)

**Detection**: search for demo artifacts in priority order (first match wins):

```bash
# Tier 1: E2E test report (repeatable proof — highest priority)
find .claude/e2e/reports -name "report.md" -newer .git/HEAD 2>/dev/null | head -3
find .claude/e2e/reports -name "*.mp4" -newer .git/HEAD 2>/dev/null | head -3

# Tier 2: E2E flow verification artifacts
find .claude/e2e/reports -name "pr-summary.md" -newer .git/HEAD 2>/dev/null | head -3

# Tier 3: Walkthrough screenshots/video (one-time, not repeatable)
find .claude/e2e/reports -path "*walkthrough*" \( -name "*.png" -o -name "*.webm" -o -name "*.mp4" \) 2>/dev/null | head -5

# Tier 4: Loom URL in PR body
gh pr view --json body --jq '.body' | grep -i "loom.com"
```

**Auto-upload** (Tier 1-3 only, runs after detection):

When local demo artifacts are found, auto-upload to GitHub for shareable URLs:

```bash
BRANCH=$(git branch --show-current)
TAG="e2e-assets-${BRANCH}"

# Create draft release if not exists
gh release view "$TAG" &>/dev/null || \
  gh release create "$TAG" --draft --title "E2E Assets for ${BRANCH}" --notes "Auto-uploaded demo artifacts"

# Upload artifacts (--clobber replaces existing)
gh release upload "$TAG" <detected_artifact_paths...> --clobber

# Get download URLs
gh release view "$TAG" --json assets --jq '.assets[].url'
```

| Upload result | Action |
|---------------|--------|
| Success | Store GitHub URLs, pass to announce skill |
| Failure (no permission / API error) | Warn user, proceed with local paths |
| Tier 4 (Loom URL) | No upload needed — URL already shareable |

**Artifact tier handling:**

| Tier | Found | Message |
|------|-------|---------|
| 1 (e2e-test) | report.md + .mp4 | `📢 Demo artifacts found: E2E test report (repeatable). {upload_status}. Draft announcement?` |
| 2 (verification) | pr-summary.md | `📢 Demo artifacts found: E2E verification summary. {upload_status}. Draft announcement?` |
| 3 (walkthrough) | screenshots/video | `📢 Demo artifacts found: walkthrough screenshots (one-time). {upload_status}. Consider running /e2e-test for repeatable proof before announcing.` |
| 4 (Loom) | Loom URL | `📢 Demo artifacts found: Loom recording. Draft announcement?` |
| None | — | Skip (see below) |

`{upload_status}`: "Uploaded to GitHub (N files)" on success, "Upload failed — local paths only" on failure.

**Skip conditions** (any one → skip with explanation):
- No demo artifacts found at any tier
- `--no-announce` flag
- User explicitly said "skip announce" or "no announce"
- PR is docs-only, deps-only, or test-only

**When skipping, always explain why:**
```
📢 Announce: skipped — {reason}
```

**If demo artifacts found:**
```
📢 {tier message from table above}
  1. Yes — draft announcement (invokes /kc-pr-announce)
  2. No — skip
```

- Option 1: invoke `/kc-pr-announce` with PR context already loaded
- Option 2: skip, proceed to Done

**If invoked from kc-pr-create**, the announcement skill inherits:
- PR URL, title, body (already available)
- Language preference (already resolved in this session)
- Demo artifact **GitHub URLs** (from auto-upload) or local paths (if upload failed)

## Step 14: Done

```
Ship complete:
  PR:          <PR_URL>
  Status:      Ready
  Review:      N rounds, M items fixed, K advisory noted
  CI:          pass / skipped          (--ci only)
  AI review:   clean / N fixed / skipped  (--ci only)
  Announce:    sent to #channel / skipped — {reason}
```

## Common Mistakes

| Problem | Fix |
|---------|-----|
| `--raw-field` with JSON arrays | Use `--input /tmp/pr-review.json` instead |
| `line` uses diff hunk number | Must be line number in NEW file (RIGHT side) |
| Forgot `--signoff` on DCO project | Check AGENTS.md before creating PR |
| Annotating self-explanatory code | Only annotate what a human reviewer can't infer |
| PR title > 70 chars | Move details to body, keep title concise |
| Ignoring project PR template | Always check `.github/PULL_REQUEST_TEMPLATE.md` first |
| Self-review loop exceeds rounds | Report remaining findings, don't block — user can fix manually |
| Posting review comments in ship mode | Ship mode does NOT post review comments to PR — it fixes locally and pushes |
| CI gate without `--ci` | CI gate is opt-in. Default ship skips CI polling |
| Re-polling AI reviewer indefinitely | Hard cap: 1 min poll + max 2 AI-fix rounds |

## Safety Limits

| Limit | Value | Override |
|-------|-------|----------|
| Self-review rounds | 3 | `--max-rounds N` |
| CI poll timeout | 5 min (20 × 15s) | — |
| AI reviewer poll | 1 min (6 × 10s) | — |
| AI-fix → CI re-run | max 2 rounds | — |

Exceeded → report status + proceed (never block indefinitely).

## Reference

Always `--signoff` (when DCO required). Co-author: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

PR title = squash-merge message — make it count.
