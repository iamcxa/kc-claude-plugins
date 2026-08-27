You are reviewing a pull request that the repository owner was asked to review.

PR: __PR_URL__
Repo: __REPO__
Head branch: __BRANCH__
Head commit: __HEAD_SHA__

The workspace is checked out on that branch. Confirm HEAD is __HEAD_SHA__ before you
start; if the branch has moved on, check that commit out and review it, because that
is the commit this review was requested for.

Run the review skill against it: `/kc-pr-review __PR_URL__`

If that skill is not available to you, do not try to install it — say so on the
first line of your final message and fall back to a manual differential review:
read the diff, read the repository AGENTS.md and CLAUDE.md for project
conventions, and report findings grouped by severity with file and symbol
references. A missing skill is a finding about the environment, not something to
work around silently.

Hard constraints:

- Never merge, never approve, never force-push. Review and comment only.
- Scope is the PR diff. Do not open unrelated work.
- Project conventions in AGENTS.md and CLAUDE.md win over generic best practice.

Finish with a short verdict line: BLOCKING / NON-BLOCKING / CLEAN, and the count
of findings per severity.
