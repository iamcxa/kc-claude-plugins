---
name: pr-merge
description: Push branches and create/track GitHub PRs for workflow entities
version: 0.12.2
---

# PR Merge

Manages the PR lifecycle for workflow entities processed in worktree stages. Pushes branches, creates PRs, detects merged PRs, and advances entities accordingly.

## Hook: startup

Scan all entity files (in the workflow directory only, not `_archive/`) for entities with a non-empty `pr` field and a non-terminal status. For each, extract the PR number (strip any `#`, `owner/repo#` prefix) and check: `gh pr view {number} --json state --jq '.state'`.

If `MERGED`, advance the entity to its terminal stage. Because a `mod-block` may be set while the PR is pending, the clear and the terminalization are two separate `--set` calls (the mechanism refuses combining `mod-block=` with terminal fields):
1. `spacedock status --workflow-dir {dir} --set {slug} mod-block=` when a `mod-block` is set (skip when empty);
2. `spacedock status --workflow-dir {dir} --set {slug} status={terminal} completed verdict=PASSED worktree=`, then `spacedock status --workflow-dir {dir} --archive {slug}`.

Clean up any worktree/branch. Report each auto-advanced entity to the captain.

If `CLOSED` (closed without merge), report to the captain: "{entity title} has PR {pr number} which was closed without merging. How to proceed? Options: reopen the PR, create a new PR from the same branch, or clear `pr` and fall back to local merge." Wait for the captain's direction before taking action.

If `OPEN`, no action needed — the PR is still in review.

If `gh` is not available, warn the captain and skip PR state checks.

## Hook: idle

Check PR-pending entities using the same logic as the startup hook: scan entity files for non-empty `pr` and non-terminal status, run `gh pr view` for each, and advance merged PRs (two-step `mod-block=` clear then terminalize). This is the workflow's PR-pending scan: the generic event loop fires this idle hook and owns no PR scan of its own, so a workflow with no `pr-merge` mod never reaches for `gh` in its loop. Report any advanced entities to the captain.

## Hook: merge

Resolve the PR base once: `BASE=$(spacedock dispatch trunk --workflow-dir {dir})` — the workflow's configured integration trunk (default `main` when no `trunk:` key is set). `dispatch trunk` emits exactly a **bare branch name** (e.g. `main`), so `$( )` yields `$BASE` clean (command substitution strips the single trailing newline). Always quote `"$BASE"` at use sites — the push, the rebase, the draft, and the `gh pr create --base` below.

**PR APPROVAL GUARDRAIL — Do NOT push or create a PR without explicit captain approval.** Before presenting the draft, construct the full PR body so the captain reviews the actual prose that will land on GitHub.

Compute the audit link with the marked recipe. It resolves the entity once through `spacedock status --workflow-dir {dir} --resolve {entity ref} --json`. Inline state keeps the worktree's short SHA and code-repository-relative path (if worktree `rev-parse` exits non-zero, substitute `main` and report the fallback); split-root state uses the resolved state checkout's full SHA and state-root-relative path. Both tuples must name a blob before the link is accepted. Owner/repo still resolves from the code repository, so this cut does not guarantee a state checkout hosted in a different GitHub repository.

Execute the marked recipe with the worktree directory, workflow directory, and entity reference:

```bash
# pr-merge-audit-link-recipe:start
# shellcheck shell=bash
pr_merge_audit_link() {
  local worktree_dir="$1"
  local workflow_dir="$2"
  local entity_ref="$3"
  local resolve_json workflow_type path_type
  local resolved_workflow resolved_path workflow_root resolved_root
  local entity_dir entity_name audit_repo audit_sha audit_path
  local owner_repo short_id

  if ! resolve_json=$(spacedock status --workflow-dir "$workflow_dir" --resolve "$entity_ref" --json); then
    printf 'pr-merge audit link: resolver command failed for %s\n' "$entity_ref" >&2
    return 1
  fi
  if ! printf '%s\n' "$resolve_json" | jq -e 'type == "object"' >/dev/null 2>&1; then
    printf 'pr-merge audit link: resolver returned malformed JSON for %s\n' "$entity_ref" >&2
    return 1
  fi
  if ! printf '%s\n' "$resolve_json" | jq -e 'has("workflow")' >/dev/null; then
    printf 'pr-merge audit link: resolver result missing workflow for %s\n' "$entity_ref" >&2
    return 1
  fi
  if ! printf '%s\n' "$resolve_json" | jq -e 'has("path")' >/dev/null; then
    printf 'pr-merge audit link: resolver result missing path for %s\n' "$entity_ref" >&2
    return 1
  fi

  workflow_type=$(printf '%s\n' "$resolve_json" | jq -r '.workflow | type') || return 1
  if [ "$workflow_type" != string ]; then
    printf 'pr-merge audit link: resolver result has non-string workflow for %s\n' "$entity_ref" >&2
    return 1
  fi
  path_type=$(printf '%s\n' "$resolve_json" | jq -r '.path | type') || return 1
  if [ "$path_type" != string ]; then
    printf 'pr-merge audit link: resolver result has non-string path for %s\n' "$entity_ref" >&2
    return 1
  fi

  resolved_workflow=$(printf '%s\n' "$resolve_json" | jq -r '.workflow') || return 1
  if [ -z "$resolved_workflow" ]; then
    printf 'pr-merge audit link: resolver result has empty workflow for %s\n' "$entity_ref" >&2
    return 1
  fi
  resolved_path=$(printf '%s\n' "$resolve_json" | jq -r '.path') || return 1
  if [ -z "$resolved_path" ]; then
    printf 'pr-merge audit link: resolver result has empty path for %s\n' "$entity_ref" >&2
    return 1
  fi

  if ! workflow_root=$(cd "$workflow_dir" 2>/dev/null && pwd -P); then
    printf 'pr-merge audit link: workflow directory unavailable for %s\n' "$entity_ref" >&2
    return 1
  fi
  if ! resolved_root=$(cd "$resolved_workflow" 2>/dev/null && pwd -P); then
    printf 'pr-merge audit link: resolved workflow unavailable for %s\n' "$entity_ref" >&2
    return 1
  fi

  entity_dir=$(dirname "$resolved_path") || return 1
  entity_name=$(basename "$resolved_path") || return 1
  if ! audit_path=$(git -C "$entity_dir" ls-files --full-name -- "$entity_name"); then
    printf 'pr-merge audit link: resolved entity path unavailable for %s\n' "$entity_ref" >&2
    return 1
  fi
  if [ -z "$audit_path" ]; then
    printf 'pr-merge audit link: resolved entity is not tracked for %s\n' "$entity_ref" >&2
    return 1
  fi

  if [ "$resolved_root" = "$workflow_root" ]; then
    audit_repo=$worktree_dir
    if ! audit_sha=$(git -C "$worktree_dir" rev-parse --short HEAD); then
      audit_sha=main
      printf 'pr-merge audit link: worktree HEAD unavailable; using main\n' >&2
    fi
  else
    audit_repo=$resolved_root
    if ! audit_sha=$(git -C "$resolved_root" rev-parse HEAD); then
      printf 'pr-merge audit link: state HEAD unavailable for %s\n' "$entity_ref" >&2
      return 1
    fi
  fi

  if ! git -C "$audit_repo" cat-file -e "$audit_sha:$audit_path"; then
    printf 'pr-merge audit link: resolved blob missing for %s: %s:%s\n' \
      "$entity_ref" "$audit_sha" "$audit_path" >&2
    return 1
  fi
  owner_repo=$(cd "$worktree_dir" && gh repo view --json nameWithOwner --jq '.nameWithOwner') || return 1
  short_id=$(spacedock status --workflow-dir "$workflow_dir" --short-id "$entity_ref") || return 1

  printf '[%s](/%s/blob/%s/%s)\n' \
    "$short_id" "$owner_repo" "$audit_sha" "$audit_path"
}
# pr-merge-audit-link-recipe:end
```

Build the full PR body using the template below — motivation lead, `## What changed`, `## Evidence`, `---` separator, `[{short-id}](...)` audit link, and `Closes {issue}` line if frontmatter `issue` is set. This is the body that will be passed to `gh pr create` verbatim; do not reconstruct it after approval.

Then present the draft to the captain:

- **Title:** {entity title}
- **Branch:** {branch} -> $BASE
- **Changes:** {N} file(s) changed across {N} commit(s)
- **Files:** {list of changed files}
- **Body:**

  ```
  {constructed body}
  ```

Wait for the captain's explicit approval before pushing. Do NOT infer approval from silence, acknowledgment of the summary, or the gate approval that preceded this step — only an explicit "push it", "go ahead", "yes", or equivalent counts.

**On approval:** First, push the trunk to ensure the remote is up to date with local state commits: `git push origin "$BASE"`. Then rebase the worktree branch onto the trunk: `git rebase "$BASE"` (from the worktree directory). Then push the worktree branch: `git push origin {branch}`. If any step fails (no remote, auth error, rebase conflict), report to the captain and fall back to local merge.

Then create the PR by running `gh pr create --base "$BASE" --head {branch} --title "{entity title}" --body "{constructed body}"` against the body already constructed above — do not rebuild it. If `gh` is not available, warn the captain and fall back to local merge.

### PR body template

Lead with motivation + end-user value; audit metadata goes at the bottom. The goal is that a reviewer or future debugger sees the "why" first and the audit link last.

**Template structure (top to bottom):**

| Section | Required | Content |
|---|---|---|
| Motivation lead | **yes** | 1 sentence, ≤ 25 words, blending motivation and end-user value. No parentheticals. |
| `## What changed` | **yes** | Action-verb bullets, 3–5 total, each ≤ 15 words. One change per bullet. No rationale inside the bullet — if a change needs justification, it belongs in the task body, not the PR. |
| `## Evidence` | **yes when validation ran** | Test suites with `N/N passed` format, 1–2 bullets. Do not include per-test-class breakdowns or enumerated suite lists — one pass ratio per suite, plus at most one line confirming live-probe verification. |
| `## Review guidance` | optional | 1 line pointing reviewer at the critical file or risky change — include only when a stage report explicitly flagged it |
| `---` separator + `[{entity-id}](/{owner}/{repo}/blob/{audit-sha}/{audit-path})` | **yes** | Audit link, at the bottom; inline state uses the code worktree tuple, split-root state the resolved state tuple |
| `Closes {issue}` | **yes when issue set** | Under the audit link, using the value exactly as it appears in frontmatter, e.g., `#48` or `owner/repo#48` |
| `Related: {siblings}` | optional | Under Closes, only when stage reports flagged follow-ups |

**Extraction rules (apply deterministically from the entity file):**

| PR body section | Source in entity file | Transformation |
|---|---|---|
| Motivation lead | Entity body paragraph(s) between closing `---` and the first `##` heading | Condense first paragraph to 1-2 sentences. Lead with impact or action verb — not "This PR" or "This task". Blend motivation + value. |
| What changed | Implementation stage report's `[x]` DONE items | One action-verb bullet per meaningful unit. Collapse sibling bullets that describe the same thing. Drop `[x]` markers. Do NOT include "what we deliberately did NOT change" bullets — scope boundaries belong in the task body, not the PR, unless a validation stage report flagged them as risk. |
| Evidence | Validation stage report items that assert AC verification (typically rerun-test items) | One bullet per suite with `N/N passed` format. Include any quantitative result the stage report explicitly called out (wallclock delta, size %, perf). Fallback to implementation report's self-test items if no validation stage exists. |
| Review guidance | Explicit "focus on X" / "risk here" notes in either stage report | 1 line. **Omit if no such note exists.** |
| Audit link | Short entity id from `spacedock status --short-id {entity ref}` (shortest-unique-prefix for sd-b32, literal stored ID for sequential and slug); canonical workflow/path from the marked recipe's single `status --resolve` call; owner/repo from the code repository | Format inline state as `[{short-id}](/{owner}/{repo}/blob/{code-short-sha}/{code-repo-relative-path})`; format split-root state with its full state SHA and state-root-relative path |
| Closes | Entity frontmatter `issue` field (exactly as written) | Prefix `Closes ` |
| Related | Explicit "related task" / "follow-up" mentions in stage reports | 1 line. **Omit if none.** |

Target total length: **60-120 words**.

**Key design decisions:**

1. **Lead with motivation + end-user value.** First content is a 1-2 sentence user-facing impact statement. The audit link moves to the bottom as audit metadata.
2. **Prescribed sections + extraction rules** — not a strict verbatim template, not free-form. The mod specifies headings and source subsections; the FO paraphrases rather than pasting.
3. **Evidence section is conditional on validation stage.** Non-validated workflows fall back to implementation self-test evidence.
4. **Review guidance and Related are opt-in.** They appear only when stage reports explicitly flagged them, to prevent bloat.

Set the entity's `pr` field to the PR number (e.g., `#57`). Report the PR to the captain.

**On decline:** Do NOT automatically fall back to local merge. Ask the captain how to proceed — options include local merge or leaving the branch unmerged. Only act on the captain's explicit choice.

Do NOT archive yet. The entity stays at its current stage with `pr` set until the PR is merged. The FO handles advancement to the terminal stage and archival when it detects the merge (via this idle hook, the startup hook, or the reconcile sweep's un-advanced-pr class).
