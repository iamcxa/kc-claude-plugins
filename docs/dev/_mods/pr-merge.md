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

Compute the audit-link inputs first: short SHA via `git rev-parse --short HEAD` in the worktree directory (if it exits non-zero — no commits, detached HEAD — substitute the literal string `main` and report the fallback to the captain); owner/repo via `gh repo view --json nameWithOwner --jq '.nameWithOwner'`; short entity-id slot via `spacedock status --short-id {entity ref}` from the workflow directory (shortest-unique-prefix for sd-b32 workflows, literal stored ID for sequential and slug, matching the status table's ID column).

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

Then create the PR by running `gh pr create --draft --base "$BASE" --head {branch} --title "{entity title}" --body "{constructed body}"` against the body already constructed above — do not rebuild it. If `gh` is not available, warn the captain and fall back to local merge.

### PR body template

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
| Audit link | Short entity id from `spacedock status --short-id {entity ref}` (shortest-unique-prefix for sd-b32, literal stored ID for sequential and slug), path from the file's repo-relative location, short SHA from `git rev-parse --short HEAD` run in the worktree directory | Format as `[{short-id}](/{owner}/{repo}/blob/{short-sha}/{path})` |
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
<!-- kc-dev-flow runtime extension:start -->
## Local extension: Draft delivery and split-root audit links

This bounded kc-dev-flow extension retains the exact released Spacedock
`pr-merge` 0.12.2 body with one `--draft` adjustment, then overrides its unsafe
delivery and split-root seams below. The structural hash assertion in
`scripts/kc-dev-flow-contract-test.py` rejects any other drift in the released
body. The runtime entry remains
`spacedock merge guard {slug} --verdict passed|rejected --workflow-dir {dir}`.

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

| Layer | `UNIT_BASE_BRANCH` | `UNIT_BASE_SHA` |
| --- | --- | --- |
| bottom | trunk `$BASE` | approved trunk `$BASE_SHA` |
| each higher | branch immediately below | approved `UNIT_CANDIDATE_SHA` immediately below |

Invoke the canonical bottom delivery unit unchanged for every layer. The
bottom unit's full approved candidate therefore becomes the exact preflight
base SHA for the next unit. For parallel delivery, invoke independent units
whose base branch and approved base SHA both resolve to trunk; none targets a
sibling branch.

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
