---
name: pr-merge
description: Push branches and create/track GitHub PRs for workflow entities
version: 9.9.9
---

# PR Merge

Manages the PR lifecycle for workflow entities processed in worktree stages. Pushes branches, creates PRs, detects merged PRs, and advances entities accordingly.

The terminal merge ceremony keys off the pending terminal-target application that `spacedock gate consume` produces (route `approved-awaiting-merge`) — not off the entity's stage: `merge guard` discovers and arms this hook at delivery time, and a failed delivery that needs rework sends the entity back through its declared `feedback-to` via `merge guard --rework`.

## Hook: startup

Scan all entity files (in the workflow directory only, not `_archive/`) for entities with a non-empty `pr` field and either non-terminal status, terminal status with `mod-block: merge:pr-merge`, or terminal status carrying a valid merged sentinel (`pr-merge:` or `local-merge:`). A sentinel row already proves MERGED: bypass `gh`, run `spacedock merge guard {slug} --workflow-dir {dir} --verdict passed` directly, and stop processing that row. For every bare PR row, preserve its repository qualifier while parsing it: `owner/repo#N` is PR `N` in `owner/repo`, while `#N` or `N` is PR `N` in the entity's current code repository. Check qualified references with `gh pr view {N} --repo {owner}/{repo} --json state --jq '.state'`. For an unqualified reference, resolve the current code repository from the entity's `{worktree}` using `git -C {worktree} remote get-url origin` and `gh repo view {code-origin-url} --json nameWithOwner --jq '.nameWithOwner'`, then use that value in `gh pr view {N} --repo {code-owner}/{code-repo} --json state --jq '.state'`. Stop and report an unresolved worktree or repository instead of consulting the launch directory.

If `MERGED`, first record and commit the landed merge sentinel with `spacedock status --workflow-dir {dir} --set {slug} pr=pr-merge:{N}` then `spacedock state commit {slug} --workflow-dir {dir}`; next finalize through `spacedock merge guard {slug} --workflow-dir {dir} --verdict passed`. The sentinel is the restart-safe durable signal; the guard clears any in-flight `mod-block`, terminalizes, archives, and commits the archive move atomically. Clean up any worktree/branch and report each auto-advanced entity to the captain.

If `CLOSED` (closed without merge), report to the captain: "{entity title} has PR {pr number} which was closed without merging. How to proceed? Options: reopen the PR, create a new PR from the same branch, fall back to local merge, or send the entity back for rework." Wait for the captain's direction before taking action. On captain direction to send back: `spacedock merge guard {slug} --rework --workflow-dir {dir}` routes the entity through its declared `feedback-to` and clears `pr`/`mod-block` — do not edit frontmatter by hand. Retryable trouble (reopen, new PR, local merge) keeps the pending approval and the delivery retry; only `--rework` supersedes it.

If `OPEN`, no action needed — the PR is still in review.

If `gh` is not available, warn the captain and skip PR state checks.

## Hook: idle

Check PR-pending entities using the same logic as the startup hook: a terminal row carrying a valid merged sentinel (`pr-merge:` or `local-merge:`) bypasses `gh` and resumes `merge guard` directly, while bare PR rows (including terminal rows still carrying `mod-block: merge:pr-merge`) run `gh pr view` and advance through the same committed sentinel then guard path. This is the workflow's PR-pending scan: the generic event loop fires this idle hook and owns no PR scan of its own, so a workflow with no `pr-merge` mod never reaches for `gh` in its loop. Report any advanced entities to the captain.

## Hook: merge

Resolve the PR base once: `BASE=$(spacedock dispatch trunk --workflow-dir {dir})` — the workflow's configured integration trunk (default `main` when no `trunk:` key is set). `dispatch trunk` emits exactly a **bare branch name** (e.g. `main`), so `$( )` yields `$BASE` clean (command substitution strips the single trailing newline). Retain the workflow-supplied `{branch}` as the data value `BRANCH`. Always quote `"$BASE"` and `"$BRANCH"` at use sites; do not evaluate either as shell syntax.

**PR APPROVAL GUARDRAIL — Do NOT push or create a PR without explicit captain approval.** Before presenting the draft, construct the full PR body so the captain reviews the actual prose that will land on GitHub.

Record the exact code commit being submitted before constructing the draft: `CANDIDATE_SHA=$(git -C {worktree} rev-parse HEAD)`. Resolve every other input explicitly rather than from the launch directory:

- Compute the candidate's short SHA with `git -C {worktree} rev-parse --short "$CANDIDATE_SHA"`; if it exits non-zero, report the error and stop. Use this recorded candidate for every later candidate identity—never read ambient `HEAD` after approval.
- Resolve the code repository with `git -C {worktree} remote get-url origin`, then pass that URL as the repository argument to `gh repo view {code-origin-url} --json nameWithOwner --jq '.nameWithOwner'` and retain its result as `CODE_REPO`.
- Locate entity state through the launcher: run `spacedock status --workflow-dir {dir} --resolve {entity ref} --json` and consume its `path` field as `ENTITY_PATH`. Derive `STATE_ROOT` with `git -C "$(dirname "$ENTITY_PATH")" rev-parse --show-toplevel`, the immutable state commit with `git -C "$STATE_ROOT" rev-parse HEAD`, and the state-relative entity path with `git -C "$STATE_ROOT" ls-files --full-name -- "$ENTITY_PATH"`. Resolve the state repository by passing `git -C "$STATE_ROOT" remote get-url origin` as the repository argument to `gh repo view ... --json nameWithOwner --jq '.nameWithOwner'`. Stop if the entity is not tracked or any resolution fails.
- Compute the short entity-id slot with `spacedock status --workflow-dir {dir} --short-id {entity ref}` (shortest-unique-prefix for sd-b32 workflows, literal stored ID for sequential and slug, matching the status table's ID column).

Build the full PR body using the template below — motivation lead, `## What changed`, `## Evidence`, `---` separator, `[{short-id}](...)` audit link, and `Closes {issue}` line if frontmatter `issue` is set. Create a mode-0600 temporary file `PR_BODY_FILE`, then write those exact bytes directly to it without a shell-interpolated heredoc or command string. Present the body by reading that file. This is the file that will be passed to `gh pr create`; do not reconstruct or rewrite it after approval.

Then present the draft to the captain:

- **Title:** {entity title}
- **Branch:** $BRANCH -> $BASE
- **Candidate:** $CANDIDATE_SHA
- **Changes:** {N} file(s) changed across {N} commit(s), computed from `git -C {worktree}` and `$BASE`
- **Files:** {list of changed files from `git -C {worktree}` and `$BASE`}
- **Body:**

  ```
  {constructed body}
  ```

Always present the draft. Then wait for the captain's explicit approval before pushing. Do NOT infer approval from silence, acknowledgment of the summary, or the gate approval that preceded this step — only an explicit "push it", "go ahead", "yes", or equivalent counts.

A standing conn counts as that approval only when the captain's own words grant push or PR authority. A conn for gates is not one. Present the draft, quote the grant as the authority, and proceed.

**On approval:** First, push the trunk from the code worktree to ensure the remote is up to date: `git -C {worktree} push origin "$BASE"`. If that push fails (no remote, auth error), report to the captain and fall back to local merge.

Resolve the current integration tip as `BASE_SHA=$(git -C {worktree} rev-parse "$BASE")`, then exercise the approved commit against it without changing the candidate ref, index, or worktree: `git -C {worktree} merge-tree --write-tree "$BASE_SHA" "$CANDIDATE_SHA"`. Inspect its stdout, stderr, exit status, and repository context; the exit status is one signal, not the semantic verdict.

- If the evidence indicates a clean merge, continue without rebasing.
- If the evidence indicates an actual content conflict, stop PR and local-merge delivery, surface the conflict evidence, and preserve the pending delivery authority. Do not rebase, automatically resolve, or use force operations; leave reconciliation owner selection to the consuming workflow.
- If the command fails or the evidence is incomplete or ambiguous, mergeability is unknown: report the error, preserve the pending authority, and stop delivery; do not rebase or use local merge as a fallback.

For a clean result, push the approved commit with the exact-SHA refspec: `git -C {worktree} push origin "${CANDIDATE_SHA}:refs/heads/${BRANCH}"`. If that push fails, report to the captain and fall back to local merge.

Then invoke `gh pr create` against the resolved code repository with title, branch, base, and body file as separate arguments: `gh pr create --repo "$CODE_REPO" --base "$BASE" --head "$BRANCH" --title "$PR_TITLE" --body-file "$PR_BODY_FILE"`. Supply `CODE_REPO`, `BRANCH`, and `PR_TITLE` as data values from the resolutions and workflow context above; never interpolate entity text into executable shell syntax or use `eval`. The submitted body must be the exact reviewed bytes in `PR_BODY_FILE`. Remove the temporary file after success or failure. If `gh` is not available, warn the captain and fall back to local merge.

### Stacked mode

Read this section only when the candidate is one layer of a stack.

**A stack exists so one expensive check run at the tip proves every layer beneath it.** The tip's tree contains all of them, so a green tip is evidence for the whole stack, and a middle layer's own lanes prove one layer in isolation at the same cost. Approve checks at the tip. When a middle layer needs its own run for any reason, ask the captain and name what that run can falsify that the tip cannot.

Run `gh skill preview github/gh-stack gh-stack` and follow it for every `gh stack` mechanic. This ceremony overrides it three times:

- Do NOT use `gh stack submit`. It auto-generates the title, so the approved bytes never reach GitHub. Create each layer with the `gh pr create` call above, then join them with `gh stack link`.
- Give `gh stack link` only PR numbers confirmed by `gh pr view {N} --repo "$CODE_REPO" --json number`. An unmatched number becomes a branch push.
- This ceremony keeps no local stack tracking, so `gh stack rebase`, `sync`, `push`, and `view` do not apply. Rebase and push each layer with the git commands below, and use their conflict rule in place of `gh stack rebase --continue`.

Use the branch below the layer as `$BASE` in place of the trunk, and skip the trunk push on approval. That push sends the parent layer, including commits the captain has not approved.

**Confirm the layer contains its parent.** All three conditions must hold:

```
git -C {worktree} merge-base --is-ancestor "$PARENT_HEAD" "$LAYER_HEAD"   # exit 0
test "$PARENT_HEAD" != "$LAYER_HEAD"                                     # exit 0
git -C {worktree} rev-list --count "$PARENT_HEAD" --not "$TRUNK_SHA"      # 1 or more
```

Resolve each value with `git -C {worktree} rev-parse`, and stop on a non-zero exit: `rev-parse` prints its own argument to stdout on failure. `$PARENT_HEAD` and `$LAYER_HEAD` come from the `origin/` refs. `$TRUNK_SHA` comes from `origin/` plus `spacedock dispatch trunk --workflow-dir {dir}`.

Exit 1 on the first condition means the layer is parallel: rebase it. Exit 128 means a ref is gone, such as a merged parent's deleted branch: stop, do NOT rebase. Equal heads or a count of 0 mean the layer or the parent holds no work: stop and report.

CAUTION: A parallel layer passes every other check — correct base, clean `merge-tree`, mergeable, and a diff of only its own files. A check on a parallel top layer exercises nothing below it. Test all three conditions before every push, draft, create, and link, and again after every rebase.

Branch a layer only from a parent that already holds committed work. Do not build two layers at once.

**Rebase a layer** when the parent moves, not only when it merges. This procedure rewrites a layer already on the remote. A layer not yet pushed rebases locally and reaches the remote through the approval step above.

1. `OLD_PARENT=$(git -C {worktree} rev-parse "origin/$PARENT_BRANCH")` — the parent commit the layer sits on. Read it before the fetch, because the fetch moves that ref and step 3 needs the old value.
2. `git -C {worktree} fetch origin`.
3. `git -C {worktree} rebase --onto "origin/$PARENT_BRANCH" "$OLD_PARENT" "$BRANCH"`. Plain `git rebase "$PARENT_BRANCH"` replays from the old merge base and leaves the layer parallel. On conflict: `rebase --abort`, then surface the exact paths and the moved base. Resolve nothing and force nothing. Hand the abort to the workflow's conflict-owner handoff, which routes one reconciliation assignment to the worker recorded for that layer's registered branch and worktree. Restacking an unmerged stack is routine, so this is a per-entity hold, not a delivery failure: keep the entity at its stage with its pending approval and `mod-block`, mutate no refs while routing, and do not take `--rework`. Other entities continue. Re-run this procedure against the owner's new head. A cold or unowned checkout has no recorded owner, so report it and stop.
4. `NEW_HEAD=$(git -C {worktree} rev-parse HEAD)`. Re-test the three conditions.
5. Replace `CANDIDATE_SHA` with `$NEW_HEAD`. The rebase abandoned the approved commit that the PR body and the merge report cite.
6. Run the tests of this layer and every layer below it.
7. `git -C {worktree} push --force-with-lease --force-if-includes origin "${NEW_HEAD}:refs/heads/${BRANCH}"`. Brace every variable in the refspec. Pass no value to the lease. A bare lease expects the remote-tracking ref, and `--force-if-includes` refuses the push unless your local branch actually incorporates what the last fetch brought — together they reject a peer's commit without naming a value. Naming `$OLD_HEAD` also rejects your own push whenever your local branch is ahead of the remote, which is the ordinary state after a local commit.

The rule against force operations above governs a two-writer content conflict on the candidate, and it still holds. This push rewrites one layer branch the ceremony owns, after a clean rebase.

**After a link, confirm each PR's base with `gh pr view {N} --repo "$CODE_REPO" --json baseRefName`.** `gh stack link` reports success when GitHub refused the change, and it rewrites bases to fit its own chain. Stack membership is display only.

**Read check results only after they appear.** A new PR reports no checks for a short time after a create or a push, and an empty list does not prove the repository runs none. Wait 30 seconds and query again. After three empty results, report and stop. Do NOT start a second run to compensate: a duplicate spends the same resources twice and does not attach to the PR.

**A top layer is complete** when its base is the trunk and `git -C {worktree} log --oneline "$TRUNK_SHA..$LAYER_HEAD"` lists only its own commits. A squash-merged parent passes the ancestry condition while the layer still carries the parent's original commits.


### PR body template

Lead with motivation + end-user value; audit metadata goes at the bottom. The goal is that a reviewer or future debugger sees the "why" first and the audit link last.

**Template structure (top to bottom):**

| Section | Required | Content |
|---|---|---|
| Motivation lead | **yes** | 1 sentence, ≤ 25 words, blending motivation and end-user value. No parentheticals. |
| `## What changed` | **yes** | Action-verb bullets, 3–5 total, each ≤ 15 words. One change per bullet. No rationale inside the bullet — if a change needs justification, it belongs in the entity body, not the PR. |
| `## Evidence` | **yes when verification ran** | Test suites with `N/N passed` format, 1–2 bullets. Do not include per-test-class breakdowns or enumerated suite lists — one pass ratio per suite, plus at most one line confirming live-probe verification. |
| `## Review guidance` | optional | 1 line pointing reviewer at the critical file or risky change — include only when a stage report explicitly flagged it |
| `---` separator + `[{entity-id}](/{state-owner}/{state-repo}/blob/{state-sha}/{state-relative-path})` | **yes** | Audit link, at the bottom |
| `Closes {issue}` | **yes when issue set** | Under the audit link, using the value exactly as it appears in frontmatter, e.g., `#48` or `owner/repo#48` |
| `Related: {siblings}` | optional | Under Closes, only when stage reports flagged follow-ups |

**Extraction rules (apply deterministically from the entity file):**

| PR body section | Source in entity file | Transformation |
|---|---|---|
| Motivation lead | Entity body paragraph(s) between closing `---` and the first `##` heading | Condense first paragraph to 1-2 sentences. Lead with impact or action verb — not "This PR" or "This task". Blend motivation + value. |
| What changed | Latest stage report whose declared stage outputs describe completed deliverable work | Use DONE items as one action-verb bullet per meaningful unit. Collapse sibling bullets that describe the same thing. Do NOT include "what we deliberately did NOT change" bullets — scope boundaries belong in the entity body, unless a later verification report flagged them as risk. Select this report by the stage's declared outputs and content, never by requiring a particular stage name. |
| Evidence | Latest stage report whose declared stage outputs independently verify the candidate against acceptance criteria | One bullet per suite with `N/N passed` format. Include any quantitative result the report explicitly called out (wallclock delta, size %, perf). If the workflow declares no independent verification-report role, fall back to self-test evidence in the deliverable-work report. Select by the declared role and content, never by requiring a particular stage name. |
| Review guidance | Explicit "focus on X" / "risk here" notes in either stage report | 1 line. **Omit if no such note exists.** |
| Audit link | Short entity id from `spacedock status --workflow-dir {dir} --short-id {entity ref}`; resolved state-repository owner/name, immutable state commit, and state-relative entity path from the explicit state resolution above | Format as `[{short-id}](/{state-owner}/{state-repo}/blob/{state-sha}/{state-relative-path})` |
| Closes | Entity frontmatter `issue` field (exactly as written) | Prefix `Closes ` |
| Related | Explicit "related entity" / "follow-up" mentions in stage reports | 1 line. **Omit if none.** |

Target total length: **60-120 words**.

**Key design decisions:**

1. **Lead with motivation + end-user value.** First content is a 1-2 sentence user-facing impact statement. The audit link moves to the bottom as audit metadata.
2. **Prescribed sections + extraction rules** — not a strict verbatim template, not free-form. The mod specifies headings and source subsections; the FO paraphrases rather than pasting.
3. **Evidence follows declared report roles.** Workflows without an independent verification report fall back to deliverable-report self-test evidence.
4. **Review guidance and Related are opt-in.** They appear only when stage reports explicitly flagged them, to prevent bloat.

Set the entity's `pr` field to the PR number (e.g., `#57`). Report the PR to the captain.

**On decline:** Do NOT automatically fall back to local merge. Ask the captain how to proceed — options include local merge or leaving the branch unmerged. Only act on the captain's explicit choice.

Do NOT archive yet. The entity stays at its current stage with `pr` set until the PR is merged. The FO handles advancement to the terminal stage and archival when it detects the merge through this portable startup or idle hook. A runtime may invoke the same hook check as a generic backstop; no host-specific reconcile class is required.

<!-- kc-dev-flow runtime extension:start -->
## Local extension: Draft delivery and split-root audit links

This bounded kc-dev-flow extension retains the exact released Spacedock
`pr-merge` 0.12.2 body with one `--draft` adjustment, then overrides its unsafe
delivery and split-root seams below. Every adopter contract test compares its
`docs/dev/_mods/pr-merge.md` released body (everything before this marker)
against the sha256 pinned at `contract-manifest.json`
`pr_merge_released_body.sha256`, and fails naming the pin key when the body
drifts. The runtime entry remains
`spacedock merge guard {slug} --verdict passed|rejected --workflow-dir {dir}`.

Content an adopter appends after this file's own closing runtime-extension
end marker is an adopter-owned local region. The contract test's drift
comparison is bounded at that marker and does not read or restrict what an
adopter writes below it. When adopter
prose in that region and this marked block instruct differently on the same
subject, follow this marked block -- that precedence is a declared operating
rule for the first officer, not something the byte-equality comparison above
enforces on the adopter's region.

### Residuals and without-it sections

Two optional PR body sections extend the released template. When present, each
is placed after `## Evidence` and before the `---` separator; each is omitted
entirely when its source entity has no items for it.

| Section | Bullets | Content |
| --- | --- | --- |
| `## Residuals` | at most three | Each bullet is a known limit. "Not tested" is never a residual. |
| `## without-it unanswered` | one line per item | One retained durable addition the author cannot justify per line, cited by path or greppable symbol. |

**Extraction rules:**

| PR body section | Source in entity file | Transformation |
| --- | --- | --- |
| Residuals | Validation stage report's residual items | Copy at most three; drop any item phrased as "not tested". |
| without-it unanswered | Implementation stage report's `without-it unanswered` items | One line per item, path or greppable symbol. |

The released template's 60-120 word target excludes both sections.

### Portable delivery hardening from shipped Spacedock v0.27.0-pre3

The comparison source is the shipped `mods/pr-merge.md` from the formal
`v0.27.0-pre3` tag at peeled commit
`ffaeaef696cad492c8d40ab84939178e242aff2e`, whose template SHA-256 begins
`0f2a4628`. No final v0.27.0 release exists. This extension backports only the
parts executable by installed Spacedock 0.26. Do not use the 0.27-only commands named `spacedock gate consume` or `merge guard --rework`; installed 0.26 does not provide them.

#### Canonical Draft delivery unit

One parameterized unit owns every single-PR delivery operation:

| Field | Exact binding |
| --- | --- |
| Worktree | `UNIT_WORKTREE` from `{worktree}` |
| Code repository | `UNIT_CODE_REPO` from the worktree origin |
| Branch | `UNIT_BRANCH` from `{branch}` |
| Base branch | caller-supplied `UNIT_BASE_BRANCH` |
| Base SHA | approved `UNIT_BASE_SHA` |
| Candidate SHA | full approved `UNIT_CANDIDATE_SHA` |
| Title | reviewed `UNIT_TITLE` |
| Body file | mode-0600 reviewed `UNIT_BODY_FILE` |

For provider-backed single-PR delivery, bind `UNIT_BRANCH` byte-for-byte to `delivery.branch` and append `delivery.close_line` exactly once to the reviewed PR body.
For a provider-backed native stack, reserve both provider values for the top layer.
Every lower layer uses its own explicitly reviewed delivery-unit branch and base, carries no provider close line, and has a branch distinct from every other layer.
Both provider values must come from the current successful
provider adapter result for the exact reconciled source. A missing, malformed,
or source-mismatched provider binding stops before push or PR creation.
For provider-backed work, this extension supersedes the released `Closes {issue}` rule above:
do not read or append the legacy frontmatter `issue`. Standalone work keeps the
released rule and has no provider delivery binding.

A single PR binds exactly one approved delivery unit. A caller may invoke the
same unit more than once, but it must supply and approve all eight values for
each invocation; no value carries across units or comes from the launch
directory.

Resolve `UNIT_CODE_REPO` by reading the origin URL with
`git -C "$UNIT_WORKTREE" remote get-url origin` and passing that URL to
`gh repo view ... --json nameWithOwner --jq '.nameWithOwner'`. Record the full
`UNIT_CANDIDATE_SHA` before review. Resolve and present the exact
`UNIT_BASE_SHA` before approval; preflight that approved pair without rereading
ambient refs:

`git -C "$UNIT_WORKTREE" merge-tree --write-tree "$UNIT_BASE_SHA" "$UNIT_CANDIDATE_SHA"`

Create the reviewed body with `PR_BODY_FILE=$(mktemp)` and `chmod 600 "$PR_BODY_FILE"`, then bind `UNIT_BODY_FILE` to that path. Write Markdown directly as data, never through shell interpolation, and include this audit-metadata line exactly once:

```text
Candidate: {full approved SHA}
```

The placeholder is the full `UNIT_CANDIDATE_SHA`. Backticks, `$()`, dollar
prefixes, and embedded newlines remain literal file bytes. Present that exact
file and do not rewrite it after approval.

After clean preflight, push only the approved candidate:

`git -C "$UNIT_WORKTREE" push origin "${UNIT_CANDIDATE_SHA}:refs/heads/${UNIT_BRANCH}"`

This is the only active PR-create command; do not execute the released inline-body command above.

`gh pr create --draft --repo "$UNIT_CODE_REPO" --base "$UNIT_BASE_BRANCH" --head "$UNIT_BRANCH" --title "$UNIT_TITLE" --body-file "$UNIT_BODY_FILE" --assignee "@me"`

Do not rebase after approval. Any unresolved binding, byte mismatch, conflict,
command failure, incomplete result, or ambiguous result stops the unit and
preserves pending authority and state.

#### PR reference resolution

| Stored `pr` | Number | Repository |
| --- | --- | --- |
| `owner/repo#N` | `N` | stored `owner/repo` qualifier |
| `#N` | `N` | `CODE_REPO` from entity worktree |
| `N` | `N` | `CODE_REPO` from entity worktree |

Keep a qualified stored reference byte-for-byte while it remains pending.
Resolve an unqualified reference's `CODE_REPO` from the entity worktree origin;
never consult the launch directory. Bind the result as explicit `PR_REPO` and
the number as `PR_NUMBER`.

#### GitHub PR feedback observation

Use one restartable GitHub-native observation, not a daemon or a second ledger.
Run it at validation entry when a PR already exists, before Ready, immediately
before merge, and before terminalization. A brand-new delivery completes local
validation first, creates its Draft only after the captain-approved push, and
takes its first mandatory observation before Ready. No PR before initial Draft
creation is not `UNKNOWN` and does not block creation. A resumed delivery whose
PR already exists observes at validation entry. No startup or idle observation
is added because neither authorizes one of these boundaries.

For a single PR, bind `FEEDBACK_REPO` and `FEEDBACK_PR_NUMBER` from the explicit
`PR_REPO` and `PR_NUMBER` above, and bind `FEEDBACK_LAYER` as `single`. For a
native stack, bind the same repository plus each layer's integer PR number and
stable ordered layer identity. Require `FEEDBACK_REPO` to parse unambiguously as
one owner/name pair and require a positive integer PR number. Start with:

`gh pr view "$FEEDBACK_PR_NUMBER" --repo "$FEEDBACK_REPO" --json author,headRefOid,isDraft,number,state,url`

Require the returned number and URL to identify that explicit repository and PR,
a non-empty PR-author login, a full `headRefOid`, and the state required by the
calling boundary. Split the already-validated repository into `owner` and
`name`; do not consult ambient repository state. Query thread pages with typed
GraphQL variables. Invoke `gh api graphql` with `-F owner="$FEEDBACK_OWNER"`,
`-F name="$FEEDBACK_NAME"`, and `-F number="$FEEDBACK_PR_NUMBER"`; omit the
optional cursor on the first page and pass `-f cursor="$FEEDBACK_CURSOR"` on
later pages. Use this selection:

```graphql
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      number
      headRefOid
      author { login }
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          comments(first: 100) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              author { login }
              body
              commit { oid }
            }
          }
        }
      }
    }
  }
}
```

Continue with `endCursor` until `hasNextPage` is false; a true flag requires a
non-empty next cursor and another page. The bounded comment-page contract is
deliberately fail closed: any nested comments page with `hasNextPage=true` is
incomplete. Separately fetch every REST review page:

`gh api --paginate --slurp "repos/$FEEDBACK_REPO/pulls/$FEEDBACK_PR_NUMBER/reviews?per_page=100"`

Require every slurped page to be an array, flatten all pages, and reject missing,
malformed, or duplicate IDs. Keep each unresolved thread with at least one
external comment, where external means the comment author login differs from the
PR author's login. Keep each external PR-level review when the review author
login differs from the PR author's login and its trimmed body is non-empty or
its state is `CHANGES_REQUESTED`. Bots remain external reviewers.
Conversation-tab issue comments are outside this slice.

Repeat the repository-explicit PR view after both paginated reads. The GraphQL
identity and all observed `headRefOid` values must equal the starting head;
otherwise the observation is not a snapshot. Observe and disposition every
stack layer independently; a top-layer result never covers another layer.

Canonicalize one UTF-8 JSON object with scheme `github-pr-feedback/v1`, the
repository, PR number, stack-layer identity, and exact head. Normalize every ID
to a string, sort retained items by kind and stable GitHub ID, and sort a
thread's comments by stable ID. A review item includes its author, state, commit
ID when present, and body hash. A thread item includes its resolution state and
all comments, including each comment's author, commit ID when present, and body
hash. In other words the input covers every item's kind and stable GitHub ID;
author, review state or thread resolution state, and commit ID when present; and
the SHA-256 of every mutable review body and thread comment body. Each body hash
is lowercase hex over the exact UTF-8 body string; encode an absent body or
commit ID as JSON null. Serialize with object keys sorted lexicographically, the
defined array order, and no insignificant whitespace. Hash those canonical
UTF-8 bytes with SHA-256. A resolved, edited, deleted, or newly added retained
item therefore changes the fingerprint. Do not persist an untrusted review body
in workflow state.

The current validation report stores one compact single-line `PR feedback:` JSON
record for each PR or layer. It carries the scheme, repository, PR number, layer,
head, `sha256:<hex>` fingerprint, and exactly one evidence-bearing disposition
for every normalized kind-and-ID pair, with no duplicate or extra disposition.
`fixed` requires a fix revision and
verification-evidence reference; `rejected-with-reason` requires a non-empty
reason; `out-of-scope-and-filed` requires a filed work-item reference. A fixed
revision must be a full revision contained by the exact observed head. An empty
normalized population has an empty disposition list, but is clean only after
the complete observation succeeds.

Observation and repair are separate. `kc-pr-flow:kc-pr-review-resolve` is an
optional repair accelerator and supplies neither observation nor gate authority.
Do not install or simulate the optional skill. When it is unavailable and
feedback needs action or a disposition is missing, route the complete set to the
ordinary implementation worker, then return to fresh validation after any code
change. Its absence is never clean-feedback evidence; only the complete native
observation can establish an empty population. The observer may provide the
same complete set to the optional skill when installed, but the validation
report remains the restart fact consumed by this delivery gate.

At each boundary, repeat the complete observation and require the report's
scheme, identity, head, fingerprint, item population, and disposition evidence
to match before any readiness, merge, or terminal state mutation. Incomplete
pagination; ambiguous repository, PR, or layer identity; head drift; content or
fingerprint drift; missing fix evidence, rejection reason, or filed reference;
API failure; malformed data; or any parse or read uncertainty must record
`UNKNOWN`, preserve pending state, and block the boundary. A code-changing
disposition creates a new head, invalidates the prior report, and requires fresh
validation. `UNKNOWN`, resolver absence, and silence never mean clean.

#### Single-PR completion decision

The startup and idle hooks use this exact fail-closed decision:

| Evidence | Required result | Otherwise |
| --- | --- | --- |
| PR repository | explicit `PR_REPO` | stop |
| Approved candidate | exactly one full `Candidate:` SHA in approved body | stop |
| GitHub PR | `headRefOid` equals Candidate and `mergedAt` is non-empty | stop |
| PR feedback | current exact-head fingerprint and evidenced dispositions | stop |
| Required checks | explicit-repository required checks succeed | stop |
| Sentinel commit | set and state commit both succeed | only then guard |

Fetch the proof without ambient repository context:

`gh pr view "$PR_NUMBER" --repo "$PR_REPO" --json body,headRefOid,mergedAt`

Parse exactly one `Candidate:` line containing a full approved SHA from the
returned body. Require that SHA to equal `headRefOid`, require non-empty
`mergedAt`, then repeat the complete GitHub PR feedback observation at that head
and require its current fingerprint plus evidenced dispositions before running:

`gh pr checks "$PR_NUMBER" --repo "$PR_REPO" --required`

Any missing, multiple, malformed, mismatched, ambiguous, or failing evidence
stops before state mutation. Only after every row passes, run in order:

1. `spacedock status --workflow-dir {dir} --set {slug} pr=pr-merge:{N}`
2. `spacedock state commit {slug} --workflow-dir {dir}`
3. `spacedock merge guard {slug} --workflow-dir {dir} --verdict passed`

If the sentinel set fails, stop. If state commit fails, stop; do not invoke the guard. A pre-existing valid sentinel may resume at the ordinary guard only after its committed state is proven. Never clear, terminalize, archive, or continue past failed proof from the hook itself.

#### Local failure-policy override

This is a local kc-dev-flow compatibility override, not shipped pre3 parity.
For push, mergeability, repository-resolution, and `gh` failures, stop, preserve pending delivery authority and state, and report. Do not fall back to local merge. The workflow's terminal `done` state requires an authenticated merged product PR, which those failure paths cannot provide.

Captain decline remains an explicit choice prompt: ask whether to keep the
branch pending, revise the proposed delivery, or cancel it. If the captain asks
about local delivery, explain that local merge cannot authenticate the product PR required for terminalization and do not claim or write terminal success.

### Released title override

This overrides the released draft-presentation line
`**Title:** {entity title}` and the released inline-body create command's
`--title "{entity title}"` argument; do not present or send either
`{entity title}` substitution. Every delivery unit's title is the refusal-
checked `UNIT_TITLE` from the canonical Draft delivery unit above -- the
single-PR case and every layer of a native stack, since each layer carries
its own reviewed title.

A pull request title release-please cannot parse under its own conventional-
commits grammar produces no release and drops that pull request's commits
from every future changelog by type, permanently and without a symptom,
whenever the delivery authority squash-merges under `COMMIT_OR_PR_TITLE`.

Resolve `KC_DEV_FLOW_ROOT` as the activated `kc-dev-flow` package root, the
same root `skills/continue-dev-flow/SKILL.md` resolves
`scripts/profile-contract-loader.py` from. An unresolvable root, or an absent
`scripts/check-pr-title.py`, is a stop, not a skip: do not present an
unchecked draft and do not fall back to local merge -- the local
failure-policy override above already forbids that fallback for delivery
failures.

Before presenting the draft, run:

`python3 "$KC_DEV_FLOW_ROOT/scripts/check-pr-title.py" "$UNIT_TITLE"`

Exit `0`: present the draft with `UNIT_TITLE` as its title; the checker's
stdout names the type it read. Exit `1`: refuse -- do not present the draft
and do not reach the create command above. Exit `2`: the checker could not
decide, treated the same as exit `1`.

On captain approval, chain that same refusal-checked `UNIT_TITLE` bytes ahead
of the canonical Draft delivery unit's create command above with `&&`, so a
non-zero exit from the check means the create command never runs.

For a native stack, repeat the refusal check once per layer against that
layer's own reviewed title before that layer's own draft presentation; an
unchecked layer title stops the stack before any push.

If the captain asks to proceed past a refusal, explain that the refusal is
the rule, not a tooling detour, and offer a corrected subject. Only a
captain-authorised scope change to the work item removes the rule.

### The title rule's oracle

`check-pr-title.py` does not invent the grammar that decides a title. It
implements the `<type>[(<scope>)][!]: <text>` shape release-please's own
conventional-commits parser accepts, and self-tests that implementation
against a committed fixture, `scripts/fixtures/pr-title/release-please-verdicts.tsv`,
before it evaluates any real title -- see the fixture's own header for the
release-please version and date it was captured from. The self-test proves
only that the checker agrees with that captured version; it says nothing
about whatever release-please version an adopter's own pipeline actually
runs. Captured 2026-09-12 from release-please `17.3.0`; the same 13 rows were
separately re-derived against `17.11.1` -- the version `subspace-relay` pins
-- on 2026-09-12, and all agreed.

**Version-skew stop condition.** A mismatch between the adopter's installed
release-please version and the fixture's captured version, or a reported
adopter skew, is a stop, not a skip: do not trust the self-test and do not
re-derive the fixture from an adopter checkout -- re-derivation reaches the
parser directly out of this repository's root-level
`scripts/fixtures/release-please-runtime`, so it is structurally a
`kc-dev-flow` maintainer action. Report the skew upstream to `kc-dev-flow`
instead of assuming agreement across versions.

### Delivery topology decision

Classify the reviewed change before constructing titles or bodies. A green layer
is independently reviewable and independently verifiable. Mark dependent green
layers `yes` only when at least two green layers must land bottom to top. Mark
independent green slices `yes` only when multiple green slices can land from
trunk in any order.

Measure the merge-base diff at review request. Numeric trigger: `gross additions + deletions > 1,500 OR changed files > 20`. Mechanical, generated, vendor, and lock-file changes stay in both counts and are named separately. Counts choose topology only; they do not relax quality boundaries or justify padding, compression, unsafe deletion, or responsibility splitting.

| Dependent green layers? | Independent green slices? | Numeric trigger? | Required topology |
| --- | --- | --- | --- |
| yes | any | any | Native stack at any size |
| no | yes | any | Parallel Draft PRs from trunk |
| no | no | yes | One Draft PR with `## Native stack exception` |
| no | no | no | One Draft PR |

For an exception row, include the exact heading `## Native stack exception` in
the PR body. Explain why no layer can be independently reviewed and verified,
and name the mechanical, generated, vendor, and lock-file share without
subtracting it. A reviewer must explicitly acknowledge the exception before
the PR becomes ready or merges; author approval is insufficient.

#### Native stack delivery-unit composition

Bind one approved canonical Draft delivery unit per layer in bottom-to-top order.
Use the unit defined above without changing its Draft, explicit repository,
body-file, exact-base preflight, or exact-candidate refspec contract:

| Layer | `UNIT_BRANCH` | `UNIT_BASE_BRANCH` | `UNIT_BASE_SHA` | Provider close line |
| --- | --- | --- | --- | --- |
| bottom | explicitly reviewed layer-unique delivery-unit branch | trunk `$BASE` | approved trunk `$BASE_SHA` | omit |
| each middle | explicitly reviewed layer-unique delivery-unit branch | branch immediately below | approved `UNIT_CANDIDATE_SHA` immediately below | omit |
| top | exact `delivery.branch` | branch immediately below | approved `UNIT_CANDIDATE_SHA` immediately below | append exact `delivery.close_line` once |

Invoke the canonical Draft delivery unit once per table row. The bottom unit's
full approved candidate becomes the exact preflight base SHA for the next unit.
For parallel delivery, invoke independent units whose base branch and approved
base SHA both resolve to trunk; none targets a sibling branch.

Each unit gets its own reviewed title, mode-0600 body file containing its full
`Candidate:` SHA, code repository, branch, base branch, base SHA, candidate SHA,
and worktree. Each layer remains independently green, with pull_request CI for every layer against its declared base.

Before any unit push, creation, or link mutation, present one stack draft and
get explicit captain approval. The captain must approve every title, full body, and bottom-to-top branch order, including every unit's Candidate and base SHA.
Do not reuse single-PR approval for a stack or infer approval from silence.

After all canonical units have created Draft PRs, retain their full GitHub PR
URLs. Link only those already-created URLs in bottom-to-top order:

`gh stack link --base "$BASE" "$BOTTOM_PR_URL" "$NEXT_PR_URL" ... "$TOP_PR_URL"`

Full URLs prevent branch pushing and ambient-repository selection by the link
step. Do not pass `--open`. Stop and preserve authority on any unit or link
failure. After linking succeeds, track the top PR as a qualified repository and
number in the entity `pr` field.

Only after each layer's required checks and review are green, its complete PR
feedback observation matches the validation report, and the captain explicitly
authorizes readiness, repeat that observation and run `gh pr ready
"$LAYER_PR_URL"` for every layer in bottom-to-top order. Preserve Draft state on
any missing evidence, refusal, or failure. Do not call `gh stack merge` while any
layer remains Draft. Immediately before an authorized atomic merge, repeat the
complete observation for every layer and block the merge if any result no longer
matches.

Use GitHub native atomic stack merge through `gh stack merge` or the native UI; never merge an individual PR.

#### Native stack completion decision

The stored top PR is completion evidence only after this public-preview stack
proof passes:

| Evidence | Required result | Otherwise |
| --- | --- | --- |
| Stack lookup | exactly one stack for stored top PR | stop |
| Base | `base.ref` equals trunk | stop |
| Top position | stored top PR is final ordered entry | stop |
| Atomic landing | every ordered `pull_requests[].merged_at` is non-empty | stop |
| Candidate | each `head.sha` and explicit PR `headRefOid` equal body Candidate | stop |
| PR feedback | each layer has a current exact-head fingerprint and evidenced dispositions | stop |
| Required checks | each explicit-repository required check succeeds | stop |
| Completion time | stored top PR `mergedAt` is non-empty | only then sentinel and guard |

Resolve the stored qualified top reference into `STACK_REPO` and
`TOP_PR_NUMBER`, then query the repository-explicit endpoint:

`gh api --method GET "repos/$STACK_REPO/stacks?pull_request=$TOP_PR_NUMBER"`

The public-preview response contract uses `number`, `base.ref`, and ordered `pull_requests[]` entries containing `number`, `merged_at`, `head.ref`, and `head.sha`. Require exactly one returned stack, its trunk base, and the stored top PR as the final ordered entry.

For every ordered entry, query the same explicit repository:

`gh pr view "$LAYER_PR_NUMBER" --repo "$STACK_REPO" --json body,headRefOid,mergedAt`

Require exactly one full `Candidate:` SHA in the approved body and require both
the entry's `head.sha` and the PR's `headRefOid` to equal it. Repeat the complete
GitHub PR feedback observation for that layer, require its current fingerprint
plus evidenced dispositions, and then run:

`gh pr checks "$LAYER_PR_NUMBER" --repo "$STACK_REPO" --required`

Every entry must have non-empty `merged_at`; the stored top PR's non-empty
`mergedAt` is the completion timestamp. Then and only then invoke the canonical
sentinel, state-commit, and ordinary 0.26 guard transcript once for the stored
top PR. A top PR merged outside exactly one matching native stack stops without sentinel or guard. Missing, multiple, reordered, mismatched, unchecked, or
partially merged evidence also stops without state mutation.

### Split-root audit-link correction

This subsection overrides the released audit-link inputs for this split-root
workflow. The released code-worktree SHA, ambient repository, and
code-relative entity path do not identify the entity state committed on
`spacedock-state/dev`.

Before constructing a PR body, resolve the state tuple explicitly:

```bash
RESOLVED=$(spacedock status --workflow-dir {dir} --resolve {entity ref} --json)
ENTITY_PATH=$(printf '%s\n' "$RESOLVED" | jq -er '.path | strings | select(length > 0)')
STATE_ROOT=$(git -C "$(dirname "$ENTITY_PATH")" rev-parse --show-toplevel)
STATE_SHA=$(git -C "$STATE_ROOT" rev-parse HEAD)
STATE_RELATIVE_PATH=$(git -C "$STATE_ROOT" ls-files --full-name -- "$ENTITY_PATH")
git -C "$STATE_ROOT" cat-file -e "$STATE_SHA:$STATE_RELATIVE_PATH"
STATE_ORIGIN=$(git -C "$STATE_ROOT" remote get-url origin)
STATE_REPO=$(gh repo view "$STATE_ORIGIN" --json nameWithOwner --jq '.nameWithOwner')
SHORT_ID=$(spacedock status --workflow-dir {dir} --short-id {entity ref})
```

Every command must exit zero, and `ENTITY_PATH`, `STATE_ROOT`, `STATE_SHA`,
`STATE_RELATIVE_PATH`, `STATE_ORIGIN`, `STATE_REPO`, and `SHORT_ID` must be
non-empty. Stop if entity state is unresolved, untracked, or absent from the state commit. Do not fall back to the code-worktree SHA, code-relative path, or `main`.

For both the released PR-body template row and its audit-link extraction rule,
replace the released tuple with the resolved state tuple:

```markdown
[{short-id}](/{state-owner}/{state-repo}/blob/{state-sha}/{state-relative-path})
```

Here `{state-owner}/{state-repo}` is `STATE_REPO`, `{state-sha}` is the full
`STATE_SHA`, and `{state-relative-path}` is `STATE_RELATIVE_PATH`. Construct the
reviewed body from that immutable tuple; never reconstruct it after approval.
<!-- kc-dev-flow runtime extension:end -->
