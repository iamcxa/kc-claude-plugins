# GitHub API Patterns

Consolidated `gh` CLI and `gh api` patterns used across kc-pr-flow skills.
Skills load specific sections at runtime via `Read → ${CLAUDE_PLUGIN_ROOT}/reference/gh-api-patterns.md`.

---

## PR Detection

Detect the current PR from a number, URL, or current branch. Never hardcode owner/repo.

```bash
# Get PR number from current branch
gh pr view --json number,url,headRefName --jq '{number, url, headRefName}'

# Minimal — number only
gh pr view --json number,url --jq '.number'

# Check whether a PR already exists for the current branch
gh pr list --head $(git branch --show-current) --json number --jq '.[0].number'

# Extract owner/repo dynamically
gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'
```

If a PR number or URL is provided by the user, use it directly and skip branch detection.

---

## PR Metadata Fetch

```bash
# Full metadata including author login (needed for @tagging in reviews)
gh pr view NUMBER --json title,body,baseRefName,headRefName,additions,deletions,changedFiles,commits,author

# Changed file names only
gh pr diff NUMBER --name-only

# Full diff
gh pr diff NUMBER
```

Capture the author login for use in review body tagging:

```bash
PR_AUTHOR=$(gh pr view NUMBER --json author --jq '.author.login')
```

Also capture the base commit info for use in `commit_id`:

```bash
git log main..HEAD --oneline
git diff main..HEAD --stat
```

---

## Repo Ownership Check

Determines whether personal `~/.claude/CLAUDE.md` rules apply (own repo / org admin) or only the target repo's docs apply (external contributor).

```bash
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
MY_USERNAME=$(gh api user --jq '.login')

if [ "$REPO_OWNER" = "$MY_USERNAME" ]; then
  IS_MY_REPO=true
else
  # Check if I'm an admin of this org
  ORG_ROLE=$(gh api "orgs/${REPO_OWNER}/memberships/${MY_USERNAME}" --jq '.role' 2>/dev/null || echo "none")
  if [ "$ORG_ROLE" = "admin" ]; then
    IS_MY_REPO=true
  else
    IS_MY_REPO=false
  fi
fi
```

- `IS_MY_REPO=true` (personal repo OR org admin): Apply `~/.claude/CLAUDE.md` + project `CLAUDE.md` — flag contradictions.
- `IS_MY_REPO=false` (org member or no access): Only consider the target repo's own `CLAUDE.md`/`AGENTS.md`. Do NOT apply personal rules to avoid false-positive "contradiction" comments.

---

## Review Payload (gh API)

**Prefer `gh pr review` CLI. Use `gh api` as fallback when inline comments are needed.**

### Primary: `gh pr review`

```bash
# Approve
gh pr review NUMBER --approve --body "LGTM"

# Request changes
gh pr review NUMBER --request-changes --body "See inline comments."

# Comment only
gh pr review NUMBER --comment --body "Some observations."
```

**Self-review restriction:** `gh pr review --approve` fails with "Can not approve your own pull request". When the PR author matches the current user (`PR_AUTHOR == MY_USERNAME`), auto-downgrade to `--comment` event. Detect with: `PR_AUTHOR=$(gh pr view NUMBER --json author --jq '.author.login')` vs `MY_USERNAME=$(gh api user --jq '.login')`.

**Limitation:** `gh pr review` does not support inline comments natively. Use the `gh api` fallback below for inline comments.

### Fallback: `gh api` with JSON `--input`

Write payload to a temp file to avoid shell escaping issues. Always tag the PR author to ensure GitHub sends a notification.

```bash
cat > /tmp/pr-review.json << 'EOF'
{
  "commit_id": "LATEST_SHA",
  "event": "REQUEST_CHANGES",
  "body": "@PR_AUTHOR Review summary here.",
  "comments": [
    {
      "path": "relative/file/path",
      "line": 42,
      "body": "Comment body in markdown."
    }
  ]
}
EOF

gh api repos/OWNER/REPO/pulls/NUMBER/reviews \
  --method POST --input /tmp/pr-review.json
```

Batch **all** inline comments into a single review API call.

---

## GraphQL Queries

### Fetch unresolved review threads

```bash
gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") {
  pullRequest(number: PR_NUM) { reviewThreads(last: 50) { nodes {
    id, isResolved, comments(first: 5) { nodes { author { login } body path line } }
} } } } }' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)'
```

If zero unresolved threads are returned, check PR-level reviews before stopping.

---

## PR-Level Reviews

PR-level reviews are top-level review summaries (body text at the top of a review submission). They do NOT appear in `reviewThreads` — a separate REST query is required.

```bash
# Fetch reviews with substantive body text
gh api repos/OWNER/REPO/pulls/PR_NUM/reviews \
  --jq '.[] | select(.body != "" and .body != null) | {id, user: .user.login, user_type: .user.type, state, body: (.body | split("\n")[0:5] | join("\n"))}'
```

**Filtering guidance**:
- Include: `COMMENTED`, `CHANGES_REQUESTED` with actionable body
- Exclude: `APPROVED` with body like "LGTM" (no action needed)
- Exclude: reviews where all points are covered by resolved inline threads (avoid double-counting)
- Body is truncated to first 5 lines in the query — read full body when validating

**Reply strategy**: PR-level reviews are replied to via `gh pr comment` with a quote (see GraphQL Mutations § "Reply to a PR-level comment"). They cannot be "resolved" like inline threads.

---

## GraphQL Mutations

### Reply strategy by comment type

| Type | How to Identify | How to Reply |
|------|----------------|-------------|
| **Inline thread** (review comment on a code line) | Has `path` field (file + line) in GraphQL response | `addPullRequestReviewThreadReply` directly in that thread |
| **PR-level comment** (top-level, not on code) | No `path` field — general PR comment | `gh pr comment` quoting the original text |

### Reply to an inline thread (fixed)

```bash
gh api graphql -f query="mutation { addPullRequestReviewThreadReply(input: {
  pullRequestReviewThreadId: \"THREAD_ID\",
  body: \"Fixed in abc1234 — now uses controlledPagination.total for accurate total count.\"
}) { comment { id } } }"
```

### Reply to an inline thread (not fixed)

```bash
gh api graphql -f query="mutation { addPullRequestReviewThreadReply(input: {
  pullRequestReviewThreadId: \"THREAD_ID\",
  body: \"Acknowledged — pre-existing pattern outside this PR scope. Tracked in SC-XXX.\"
}) { comment { id } } }"
```

### Resolve a thread

```bash
gh api graphql -f query="mutation { resolveReviewThread(input: {
  threadId: \"THREAD_ID\"
}) { thread { isResolved } } }"
```

### Reply to a PR-level comment

```bash
gh pr comment PR_NUM --body "> Original comment text here

Response explaining how it was addressed."
```

Escape GraphQL strings: avoid unescaped single quotes and backticks in mutation `body` values.

---

## Review Request Timeline

Fetch review request events to identify who requested each reviewer. Critical for AI reviewer detection — maps AI bots back to the human who requested them.

```bash
# Fetch review request events (who requested whom)
gh api repos/OWNER/REPO/issues/PR_NUM/timeline --paginate --jq '
  [.[] | select(.event == "review_requested" and .requested_reviewer != null) |
  {reviewer: .requested_reviewer.login, reviewer_type: .requested_reviewer.type,
   requested_by: .actor.login}]'
```

Response structure:

```json
[
  {"reviewer": "copilot", "reviewer_type": "Bot", "requested_by": "kentwelcome"},
  {"reviewer": "senior-dev", "reviewer_type": "User", "requested_by": "kentwelcome"}
]
```

### Detect AI/Bot reviewers

A reviewer is classified as AI/Bot if ANY condition matches:

| Signal | Example |
|--------|---------|
| `reviewer_type` is `"Bot"` | Timeline event's `requested_reviewer.type` field |
| Username ends with `[bot]` | `dependabot[bot]`, `github-actions[bot]` |
| Known AI reviewer username | `copilot`, `copilot-pull-request-reviewer` |

```bash
# Alternative: check a specific user's type directly
gh api users/USERNAME --jq '.type'
# Returns "User" or "Bot"
```

### Re-request AI review safely

**Never @mention AI bots in PR comments** — some bots (notably Copilot) interpret @mentions as new action requests, producing unwanted side effects (spurious PRs, duplicate reviews).

```bash
# ✅ CORRECT for collaborator bots (Claude, Coderabbit paid, etc.)
gh pr edit PR_NUM --add-reviewer <bot-username>

# ✅ CORRECT for GitHub Copilot — requires direct API with [bot] suffix
# (gh pr edit --add-reviewer copilot silently no-ops; do NOT use it for Copilot)
gh api -X POST repos/OWNER/REPO/pulls/PR_NUM/requested_reviewers \
  -f 'reviewers[]=copilot-pull-request-reviewer[bot]'

# ❌ WRONG — @mentioning bot in comment body triggers unwanted actions
gh pr comment PR_NUM --body "Addressed feedback. @copilot-pull-request-reviewer"
```

See `reference/learned-patterns.md` "Requesting Copilot review needs the `[bot]` suffix via direct API" for why `gh pr edit --add-reviewer copilot` fails silently and verification details from PR #17.

### Fallback: unknown requester

If the timeline event's `actor` is a bot or GitHub Action (no clear human), fall back to the PR author as the human to notify.

---

## Comment CRUD

```bash
# List all inline comments on a PR
gh api repos/OWNER/REPO/pulls/NUMBER/comments \
  --jq '.[] | {id, path, line, body: (.body | split("\n")[0])}'

# Delete a specific inline comment
gh api repos/OWNER/REPO/pulls/comments/COMMENT_ID --method DELETE
```

---

## Common Gotchas

| Gotcha | Detail |
|--------|--------|
| `--raw-field` with JSON arrays | Treats arrays as strings — always use `--input /tmp/pr-review.json` for complex payloads |
| `line` field | Must be the line number in the **NEW file** (right side of diff), NOT the diff hunk number |
| `commit_id` | Must be the **latest commit SHA** on the PR head branch, not the merge base |
| GraphQL string escaping | Avoid unescaped `'` and `` ` `` in mutation body strings |
| One review per submission | Batch all inline comments into a single `POST .../reviews` call; multiple calls create multiple review events |
| Tag the PR author | Always include `@PR_AUTHOR` in the review body — `gh pr review --body` alone may not trigger a GitHub notification to the author |
| `mergeStateStatus` ≠ freshness | `CLEAN` means mergeable, not up-to-date. Use the `behindBy` field to check whether the branch is behind base. |
