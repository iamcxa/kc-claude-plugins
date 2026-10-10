# release-acceptance — ideation, cycle 1

Dispatched: 2026-10-10 from state commit 2932240d84831fe6713a880c9cb6cfda0e474e29; base origin/main 2256b2288e8c15a1ecd2b7356859249d75b4d6f6
Model: sonnet (the build default; no override)

## Checklist

Design (PRFAQ with Mermaid) for release-scale acceptance as a standard mechanism, per the Captain's ruling recorded in ## Scope: the kc-dev-flow-2 half (when the acceptance task opens, who walks it, what the report carries, how a cross-task failure routes back to release review as signal 3), the kc-journey-map half (a mode that produces the walk list: stories in order, entry points, the release proof line; and takes the result back to card status), and the declared contract between them, read against origin/main 2256b2288e8c15a1ecd2b7356859249d75b4d6f6 (kc-dev-flow-2 references/sd/workflow.md § Release review; kc-journey-map's review-release mode)
Issue #571's second half designed too: enforcing the pre-implementation release review at implementation dispatch, with the R4 instance (an implementation dispatched without the signal-4 review) as the failing case
Acceptance criteria with reproducible Verified-by clauses, each traceable to the Captain's words or the issue, using the two hand-run walks in this task's folder (r3-acceptance.md, r4-acceptance.md) as fixtures; and Captain decisions one per line with a recommendation, including the environment question the R4 walk raised (credentials the walk needs, such as an opt-in secret)

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.14.0
kc-journey-map package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-journey-map/1.5.1
Repository: kc-claude-plugins (public). Packages kc-dev-flow-2 and kc-journey-map. Read issue #571 with gh. The Captain's 2026-09-06 rule applies: plan / dev / ship flows connect only by declared input and output contracts, schemas live with the producer.
Never git stash. Ideation writes no repository file, branch or commit.
