---
name: pr-merge
description: Push branches and create/track GitHub PRs for workflow entities
version: 0.11.0
changelog:
  0.11.0:
    - Replaced Hook post-create with carlove-derived two-track review pattern
      (Copilot reviewer-request + 6-min mandatory wait, parallel local kc-pr-review
      with skill-resolution chain and always-post-advisory rule, gated triage via
      kc-pr-review-resolve combining both review streams).
    - Confidence assessment kept but downgraded to informational (does NOT gate);
      bot-driven review gates replace the old confidence-tier ≥90 threshold.
    - Added classification heuristic for FO to decide CLEAN / BLOCKING / PROMPT_CAPTAIN
      from posted comment severity tags (no re-reading skill output).
    - Self-PR caveat documented: GitHub blocks self-APPROVE; review posts as comment
      with explicit would-be-APPROVE note when author == reviewer.
    - D2 auto-accept under workflow dispatch (captain pre-approved at adopt time;
      no per-PR confirmation gate that blocks autonomous flow).
  0.10.1:
    - Initial post-create hook with Copilot request + assign + confidence ≥90 gate.
---

# PR Merge

Manages the PR lifecycle for workflow entities processed in worktree stages. Pushes branches, creates PRs, detects merged PRs, and advances entities accordingly.

## Hook: startup

**VCS detection**: Before running any PR command, detect VCS provider: `git remote -v | grep -q "github\.com" && echo "vcs=github" || git remote -v | grep -q "gitlab\.com" && echo "vcs=gitlab" || echo "vcs=unknown"`. If github → use `gh` CLI. If gitlab → use `glab` CLI. If unknown → warn captain and skip PR state checks.

Scan all entity files (in the workflow directory only, not `_archive/`) for entities with a non-empty `pr` field and a non-terminal status. For each, extract the PR number (strip any `#`, `owner/repo#` prefix) and check:
- **GitHub**: `gh pr view {number} --json state --jq '.state'`
- **GitLab**: `glab mr view {number} --output json | jq -r '.state'`

If `MERGED` (GitHub) or `merged` (GitLab), advance the entity to its terminal stage: set `status` to the terminal stage, `completed` to ISO 8601 now, `verdict: PASSED`, clear `worktree`, archive the file, and clean up any worktree/branch. Report each auto-advanced entity to the captain.

If `CLOSED` (closed without merge), report to the captain: "{entity title} has PR {pr number} which was closed without merging. How to proceed? Options: reopen the PR, create a new PR from the same branch, or clear `pr` and fall back to local merge." Wait for the captain's direction before taking action.

If `OPEN`, no action needed — the PR is still in review.

If the VCS CLI tool (`gh` for GitHub, `glab` for GitLab) is not available, warn the captain and skip PR state checks.

## Hook: idle

Check PR-pending entities using the same logic as the startup hook: scan entity files for non-empty `pr` and non-terminal status, run the VCS-detected PR view command for each, and advance merged PRs. This provides a periodic re-check in case the event loop's built-in PR scan missed a state change (defense in depth). Report any advanced entities to the captain.

## Hook: merge

**PR APPROVAL GUARDRAIL — Do NOT push or create a PR without explicit captain approval.** Before pushing, present a draft PR summary to the captain:

- **Title:** {entity title}
- **Branch:** {branch} -> main
- **Changes:** {N} file(s) changed across {N} commit(s)
- **Files:** {list of changed files}

Wait for the captain's explicit approval before pushing. Do NOT infer approval from silence, acknowledgment of the summary, or the gate approval that preceded this step — only an explicit "push it", "go ahead", "yes", or equivalent counts.

**On approval:** First, push main to ensure the remote is up to date with local state commits: `git push origin main`. Then rebase the worktree branch onto main: `git rebase main` (from the worktree directory). Then push the worktree branch: `git push origin {branch}`. If any step fails (no remote, auth error, rebase conflict), report to the captain and fall back to local merge.

Before constructing the PR body, compute the short SHA for the audit link by running `git rev-parse --short HEAD` in the worktree directory. If the command exits non-zero (no commits, detached HEAD), substitute the literal string `main` into the audit-link template instead and report the fallback to the captain. Resolve the owner/repo via:
- **GitHub**: `gh repo view --json nameWithOwner --jq '.nameWithOwner'`
- **GitLab**: `glab repo view --output json | jq -r '.path_with_namespace'`

Create a PR using the VCS-detected command:
- **GitHub**: `gh pr create --base main --head {branch} --title "{entity title}" --body "{constructed body}"`
- **GitLab**: `glab mr create --source-branch {branch} --target-branch main --title "{entity title}" --description "{constructed body}"`

If the VCS CLI tool (`gh` for GitHub, `glab` for GitLab) is not available, warn the captain and fall back to local merge. If `vcs=unknown` → warn the captain and fall back to local merge.

### PR body resolution

**Ship stage PR Draft takes priority.** Before applying the generic template below, check the entity file for `### PR Draft` under either `## Ship` (post-2026-04-19 layout) or `## Ship Output` (legacy). If present, use its `Body:` content verbatim as the PR body — the ship stage already formatted it with workflow-specific UAT tables, DC verification commands, and reviewer reproduction steps. Only append the audit link (`[{entity-id}](...)`), `Closes`, and `Related` lines if they are not already in the draft.

**Fallback to generic template** only when no `### PR Draft` section exists in the entity file (e.g., workflows without a ship stage, or entities that skipped ship).

### PR body template (fallback)

Lead with motivation + end-user value; audit metadata goes at the bottom. The goal is that a reviewer or future debugger sees the "why" first and the audit link last.

**Template structure (top to bottom):**

| Section | Required | Content |
|---|---|---|
| Motivation lead | **yes** | 1 sentence, ≤ 25 words, blending motivation and end-user value. No parentheticals. |
| `## What changed` | **yes** | Action-verb bullets, 3–5 total, each ≤ 15 words. One change per bullet. No rationale inside the bullet — if a change needs justification, it belongs in the task body, not the PR. |
| `## Evidence` | **yes when validation ran** | Test suites with `N/N passed` format, 1–2 bullets. Do not include per-test-class breakdowns or enumerated suite lists — one pass ratio per suite, plus at most one line confirming live-probe verification. |
| `## Review guidance` | optional | 1 line pointing reviewer at the critical file or risky change — include only when a stage report explicitly flagged it |
| `---` separator + `[{entity-id}](/{owner}/{repo}/blob/{short-sha}/{path-to-entity-file})` | **yes** | Audit link, at the bottom |
| `Closes {issue}` | **yes when issue set** | Under the audit link, using the value exactly as it appears in frontmatter, e.g., `#48` or `owner/repo#48` |
| `Related: {siblings}` | optional | Under Closes, only when stage reports flagged follow-ups |

**Extraction rules (apply deterministically from the entity file):**

| PR body section | Source in entity file | Transformation |
|---|---|---|
| Motivation lead | Entity body paragraph(s) between closing `---` and the first `##` heading | Condense first paragraph to 1-2 sentences. Lead with impact or action verb — not "This PR" or "This task". Blend motivation + value. |
| What changed | Implementation stage report's `[x]` DONE items | One action-verb bullet per meaningful unit. Collapse sibling bullets that describe the same thing. Drop `[x]` markers. Do NOT include "what we deliberately did NOT change" bullets — scope boundaries belong in the task body, not the PR, unless a validation stage report flagged them as risk. |
| Evidence | Validation stage report items that assert AC verification (typically rerun-test items) | One bullet per suite with `N/N passed` format. Include any quantitative result the stage report explicitly called out (wallclock delta, size %, perf). Fallback to implementation report's self-test items if no validation stage exists. |
| Review guidance | Explicit "focus on X" / "risk here" notes in either stage report | 1 line. **Omit if no such note exists.** |
| Audit link | Entity id from frontmatter, path from the file's repo-relative location, short SHA from `git rev-parse --short HEAD` run in the worktree directory | Format as `[{id}](/{owner}/{repo}/blob/{short-sha}/{path})` |
| Closes | Entity frontmatter `issue` field (exactly as written) | Prefix `Closes ` |
| Related | Explicit "related task" / "follow-up" mentions in stage reports | 1 line. **Omit if none.** |

Target total length: **60-120 words**.

**Key design decisions:**

1. **Lead with motivation + end-user value.** First content is a 1-2 sentence user-facing impact statement. The audit link moves to the bottom as audit metadata.
2. **Prescribed sections + extraction rules** — not a strict verbatim template, not free-form. The mod specifies headings and source subsections; the FO paraphrases rather than pasting.
3. **Evidence section is conditional on validation stage.** Non-validated workflows fall back to implementation self-test evidence.
4. **Review guidance and Related are opt-in.** They appear only when stage reports explicitly flagged them, to prevent bloat.

Set the entity's `pr` field to the PR number (e.g., `#57`). Report the PR to the captain.

**Merge strategy note (when captain merges on GitHub/GitLab web UI):** Recommend **"Create a merge commit"** (GitHub) or **"Merge commit"** (GitLab) — NOT squash. Reason (MEMORY.md line 11): when execute stage merged `main` INTO the PR branch to resolve parallel-session divergence, squash collapses parallel-session commits into OUR squash commit, stealing their authorship. Merge-commit preserves every commit's original SHA and author. Include this recommendation in the captain-facing PR summary so it's visible when they approve the merge.

**On decline:** Do NOT automatically fall back to local merge. Ask the captain how to proceed — options include local merge or leaving the branch unmerged. Only act on the captain's explicit choice.

Do NOT archive yet. The entity stays at its current stage with `pr` set until the PR is merged. The FO handles advancement to the terminal stage and archival when it detects the merge (via the event loop PR check, idle hook, or startup hook).

## Hook: post-create (PR auto-review)

After ship stage produces a PR (or entity ships with `pr` set), the FO runs the carlove-derived two-track review pattern: external Copilot review + parallel local kc-pr-review, both gated on a 6-minute arrival window before any merge action. Pattern source: `carlove/docs/ship-flow/_mods/pr-merge.md` post-create hook (battle-tested across 100+ ship-flow PRs as of 2026-05).

### Confidence assessment (FO computes; informational, does NOT gate per carlove rationalization)

| Signal | Weight |
|---|---|
| Verify gate: 100% checklist DONE, 0 FAILED | +40 |
| Quality gates all green (type-check + tests + lint per detected stack) | +30 |
| No outstanding feedback cycle in execute or verify | +15 |
| Rebase clean OR conflict resolution captain-approved | +10 |
| Token spend within budget envelope | +5 |
| **Total** | 100 |

FO surfaces the score in the auto-finalize summary message (e.g., "PR #N: confidence 95"). Score is **informational only** — it does NOT gate the post-create flow. The bot-driven gates below (Copilot + kc-pr-review VETO loop) replace the old confidence-tier ≥90 threshold (carlove 2026-04-28 captain decision).

### Policy steps (in order, after rebase clean + push)

#### Step 1 — Request Copilot code review + mandatory 6-minute wait

Request Copilot review through GitHub's reviewer-request surface (not via PR comment — comment-based requests don't produce full inline review):

```bash
# Preferred: gh CLI wrapper for reviewer-request API (gh ≥ 2.40)
gh pr edit --help | grep -q 'Use "@copilot" to request review from Copilot'
gh pr edit {pr} --add-reviewer @copilot

# Fallback for older gh versions
gh api repos/{owner}/{repo}/pulls/{pr}/requested_reviewers \
  --method POST \
  -f 'reviewers[]=copilot-pull-request-reviewer[bot]'
```

Verify the request landed via either path (REST `.requested_reviewers[]` briefly shows login `Copilot`, then moves to `reviews.author.login = copilot-pull-request-reviewer` once Copilot submits):

```bash
gh api repos/{owner}/{repo}/pulls/{pr} \
  --jq '.requested_reviewers[]? | select(.login == "Copilot" or .login == "copilot-pull-request-reviewer[bot]")'
gh pr view {pr} --json reviews \
  --jq '.reviews[]? | select(.author.login == "copilot-pull-request-reviewer" or .author.login == "Copilot")'
```

If the repo doesn't have Copilot review wired (permissions / availability / reviewer-not-found error), log + skip; do NOT halt. Record `Copilot reviewer request sent | submitted | skipped: <reason>` in the stage report. A `@copilot please review` PR comment is a manual fallback only — not the default path.

**Mandatory wait (6 minutes / 360 seconds)** after the first successful Copilot review request OR PR creation. During this window:
- Do NOT mark Ready
- Do NOT arm auto-merge
- Do NOT tag `@claude` (or any final-review trigger)
- Do NOT post the kc-pr-review comment yet (drafted in Step 2 in parallel; posting waits for Step 3 collection)

Rationale: Copilot commonly posts review comments asynchronously after the PR exists; immediate finalization can miss actionable feedback. The 6-minute window is empirically tuned (carlove n>50; 95th percentile of Copilot first-comment arrival was 4-5 min).

After the 6-minute wait, re-check Copilot response:
- If Copilot review submitted → record findings, proceed to Step 3 collection.
- If Copilot was successfully requested but has not responded → wait one additional 120-second interval and re-check.
- If still absent after 8 minutes total → surface "Copilot review not observed after 8 minutes" and continue WITHOUT Copilot findings; record the skip reason.

#### Step 2 — Dispatch local /kc-pr-review in parallel (always-post-advisory)

In parallel with Step 1's wait window, dispatch a local PR review via the kc-pr-review skill chain. This produces a self-review pass that's posted to the PR regardless of outcome (always-with-advisory; the post is non-gating informational evidence for the captain + future review-resolve pass).

**Skill resolution chain** (use first available; degrade gracefully):

| Order | Source | Notes |
|---|---|---|
| 1 | `Skill: kc-pr-flow:kc-pr-review` | Preferred — full flow with verification matrix, break-point probe, ToB security, advisory tables |
| 2 | `Skill: pr-review-toolkit:review-pr` | Fallback when kc-pr-flow plugin not installed — runs the standard agent matrix (code-reviewer + silent-failure-hunter + security-reviewer) |
| 3 | Spawn fresh-context Agent for external code review | Last resort — generic agent dispatch with the diff + CLAUDE.md context, asks for structured findings table |

**Dispatch via named teammate** (avoid FO context pollution):

```
Agent(
    subagent_type="general-purpose",
    model="sonnet",
    team_name="pitch-{entity-id}",
    name="pr-reviewer",
    description="kc-pr-review on PR #{pr}",
    prompt="<self-contained brief: PR number, entity id, captain-accepted deviations
    to skip, project CLAUDE.md path, the skill chain order above; ALWAYS-POST-ADVISORY
    rule (post the review with both inline CODE comments AND advisory DOC/NEW items
    in the body, not just gate on CODE); return structured findings table via SendMessage>"
)
```

The pr-reviewer teammate runs the resolved skill in its own fresh context and **always posts the review to the PR** (even when verdict = APPROVE / no BLOCKING). The advisory items go in the review body — they're not a gate, they're an audit trail for the review-resolve pass in Step 7 to address alongside Copilot findings.

**Self-PR caveat**: GitHub blocks self-APPROVE. When PR author == reviewer, the skill posts as `--comment` with an explicit "(would-be-APPROVE; self-PR)" note in the body. Captain merges anyway since the gate is informational.

**Why "always post advisory"** (carlove evolution rationale): early carlove iterations posted only inline CODE comments and dropped DOC/NEW findings. Result: post-merge review-resolve had no record of advisory findings to address; D2 knowledge captures evaporated. Always-with-advisory ensures every review pass leaves an audit trail visible on the PR timeline + retrievable by review-resolve.

**Graceful degradation**: if the entire skill chain fails (no plugin available, agent dispatch fails, repeated SendMessage timeout), log + surface to captain. Skip ONLY this gate, continue from Step 4 (Mark Ready). Steps 5-7 still run when their preconditions hold.

#### Step 3 — Wait for both reviews; address combined findings via /kc-pr-review-resolve

After the 6-minute (or 8-minute extended) wait elapses AND the local pr-reviewer's SendMessage reply lands:

1. **Collect both review streams**:
   - Copilot inline comments + summary review (Step 1)
   - Local pr-reviewer inline + advisory (Step 2)

2. **Dispatch `Skill: kc-pr-flow:kc-pr-review-resolve`** to address the combined findings as a single triage pass. Resolve handles:
   - Reading both review streams
   - Classifying each finding (CODE / DOC / NEW × severity)
   - Auto-fixing trivial CODE-NIT inline (mechanical, ≤5 LOC, no logic)
   - For BLOCKING / WARNING items: dispatch executer (or fresh sonnet fallback) with structured fix list
   - Re-pushing fixes; re-running the cheap gates
   - Replying to inline threads with resolution evidence

   Round cap: 2 consecutive resolve rounds. Round 3 → halt + PROMPT_CAPTAIN with all rounds of findings + a recommendation (typically "merge with known caveats" vs "abandon and re-shape").

3. **Gate on resolve verdict**:
   - **CLEAN** (no remaining BLOCKING after resolve) → proceed to Step 4 (Mark Ready)
   - **BLOCKING persists** → keep PR as Draft (`gh pr ready --undo {pr}` if it was promoted; idempotent)
   - **PROMPT_CAPTAIN** (resolve surfaces findings the FO can't classify) → halt + present to captain

   The kc-pr-review-resolve VETO loop is **distinct** from the /ship Step 5 cross-review VETO and the /ship Step 7 captain-smoke VETO — all three caps are independent and tracked separately per PR.

4. **D2 auto-accept under workflow dispatch**: when kc-pr-review-resolve is dispatched by this mod (not invoked manually by the captain), D2 project-level pattern writes to CLAUDE.md are auto-accepted without user confirmation. Include `auto_accept_d2=true` in the dispatch prompt; the agent skips the D2 confirmation gate entirely. Rationale: captain has approved this workflow-level policy at adopt time; per-PR confirmation gates would block the autonomous flow. Captain reviews D2 writes via `git diff` post-merge or via the resolve agent's commit messages.

#### Step 4 — Mark Ready

`gh pr ready {pr}` — converts Draft → Ready, triggers CI. Idempotent, safe if already not Draft.

#### Step 5 — Arm auto-merge (only when cheap-feedback handled and final-base eligible)

If all preconditions hold, surface that auto-merge is armed and waiting for formal approval. Do NOT run `gh pr merge {pr} --auto --squash --delete-branch` at PR-creation time, before the 6-minute wait, or while any actionable Copilot / pr-reviewer / human feedback remains. GitHub native auto-merge merges immediately when approval arrives and bypasses the captain-cancellable countdown — the idle hook's Auto-Merge on Approval section owns the countdown.

Preconditions:
- PR base is `main` or the configured release target
- PR is not a stacked child waiting on a parent
- `gh pr checks` is green or only has explicitly accepted non-blocking optional checks
- `gh pr view {pr} --json mergeable,mergeStateStatus` reports `MERGEABLE` / `CLEAN`
- No unresolved Copilot / pr-reviewer / human cheap-review findings remain
- Branch protection requirements known; this step does not satisfy or replace approval

#### Step 6 — Assign + tag final reviewer

```bash
gh pr edit {pr} --add-assignee @me   # PR creator ownership marker
```

Tagging `@claude review` (or whatever final-review trigger the adopter uses) via PR comment is **opt-in per adopter** — only after the cheap-review gates above are clean and auto-merge is armed. Skip when the action isn't installed in the adopter repo (a stale comment with no responder is noise).

#### Step 7 — Schedule review-resolve continuation

Record the PR in the entity's `review_resolve_pending: true` frontmatter field. The idle hook's Auto-Merge on Approval section detects this and dispatches `kc-pr-review-resolve` once human approval arrives, addressing any post-cheap-gate human findings.

#### Continue next wave immediately

After Steps 0-7 complete (or are gracefully skipped due to known limitations), the FO does **NOT wait** for PR merge. Proceed immediately to:
- Dispatching the next entity in the captain queue
- Filing newly-triggered entities (e.g., "if X-1 merges, file X-2" → file X-2 + dispatch shape now since X-1 PR is in flight)

This mod's `idle` hook handles merge detection later. The FO does not poll PR state actively — pr-merge startup/idle hooks scan `status --where "pr !="` on each FO event-loop tick.

### kc-pr-review classification heuristic (FO uses to decide CLEAN vs BLOCKING vs PROMPT_CAPTAIN)

After the pr-reviewer teammate returns its SendMessage reply, the FO inspects the GitHub PR for posted review comments and uses this rubric (does NOT manually re-read the kc-pr-review output to score it):

| Signal | Verdict |
|---|---|
| 0 inline comments posted, OR all comments classified as `nit` / `informational` | **CLEAN** |
| ≥1 comment classified as `must-fix` / `blocking` / `bug` (per kc-pr-review's own severity tag) | **BLOCKING** |
| Mixed signals OR severity tags unclear | **PROMPT_CAPTAIN** |

The advisory items in the review body (DOC/NEW) are NOT part of this classification — they're audit-trail evidence for review-resolve, not gates.

### Failure handling

If any step fails (auth, permission, missing reviewer): log the error in the stage report's `## Canonical Docs Update` (or equivalent) section, surface to captain, do NOT halt ship-stage. The PR is still valid; manual review assignment is the fallback. If the Copilot reviewer request fails, record the failure and continue with human review or a captain-approved manual fallback. Do not invent alternate Copilot reviewer ids during ship-final.

### Copilot bot-head guardrail

If Copilot responds by pushing commits, verify the current head author and checks
before merge. Commits authored by `copilot-swe-agent[bot]` can leave GitHub
Actions runs in `action_required` with empty jobs. This is not a real test
failure, but it blocks required checks until a human grants workflow approval or
the same diff is re-authored as a human-authored commit.

Required diagnostic on the current head:

```bash
gh pr checks {pr}
gh run list --branch {branch} --commit {sha} --limit 5
git show --no-patch --format=fuller HEAD
```

If the SHA-scoped `gh run list` shows `action_required` on the current head and
`git show` shows `copilot-swe-agent[bot]`, either request explicit workflow
approval from the captain or re-author the commit locally as a human-authored
commit (`git commit --amend --reset-author --no-edit` followed by `git push
--force-with-lease`). Re-run
`gh pr checks` afterward and require `ci-gate` success on the current head
before merge.

### Confidence signals — extraction rules

| Signal | Source in entity file | Pass criteria |
|---|---|---|
| Verify gate | `verify.md` `### Verdict status:` line | exact match `passed` (not `pending` / `partial` / `blocked`) |
| Quality gates | `verify.md` `## Quality Gate` table OR equivalent test-run evidence | all rows show PASS / exit 0; pre-existing baseline failures noted as such |
| Outstanding feedback | `execute.md` + `verify.md` `## Knowledge Captures` / `## Issues Found` sections | no entries marked `BLOCKING`, no open `VETO` cycle |
| Rebase clean | `git status --porcelain` after rebase OR captain-approved manual conflict resolution commit | clean working tree post-rebase OR explicit captain ACK on conflict-resolution commit |
| Token spend | stage cost lines in execute / verify / review reports | sum within entity appetite envelope (small-batch ≤$10, medium-batch ≤$30, big-batch ≤$80) |

The FO computes the score deterministically from these sources; do not infer from conversation transcript. If a source is missing entirely (e.g., no `## Quality Gate` table), score that signal as 0 and surface the gap in the captain prompt.
