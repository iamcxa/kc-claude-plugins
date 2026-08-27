You are reviewing a pull request that the repository owner was asked to review.

PR: __PR_URL__
Repo: __REPO__
Head branch: __BRANCH__ (already checked out in this workspace)

Steps:

1. Install the review toolkit, then confirm the skill is loadable:

   claude plugin marketplace add iamcxa/kc-claude-plugins
   claude plugin install kc-pr-flow@kc-claude-plugins

2. Run the review skill against this PR: `/kc-pr-review __PR_URL__`

   If the skill is not available after step 1, say so explicitly at the top of
   your final message, then fall back to a manual differential review: read the
   diff, read the repository AGENTS.md and CLAUDE.md for project conventions,
   and report findings grouped by severity with file and symbol references.

3. Post the review to the PR as inline review comments plus a summary.

Hard constraints:

- Never merge, never approve, never force-push. Review and comment only.
- Scope is the PR diff. Do not open unrelated work.
- Project conventions in AGENTS.md and CLAUDE.md win over generic best practice.

Finish with a short verdict line: BLOCKING / NON-BLOCKING / CLEAN, and the count
of findings per severity.
