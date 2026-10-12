# copilot extension

Requests and reads GitHub Copilot code review rounds on a delivery PR. A repository uses it
by listing `copilot` under `extensions:` in its workflow README frontmatter.

- **Needs:** `gh` 2.92 or later authenticated for the repository, and Copilot code review
  available to the account that requests it.
- **Joins:** FO delivery: when a PR is marked ready, after each push to it, FO steps:
  review findings, step 5 (counting external-review rounds), and the merge ask.
- **Request:** FO runs `gh pr edit <N> --repo <owner/repo> --add-reviewer @copilot` when the
  PR is marked ready and after each push. If the PR timeline then shows no
  `review_requested` event for Copilot newer than that push, FO requests it with `gh api -X POST
  repos/<owner/repo>/pulls/<N>/requested_reviewers -f 'reviewers[]=copilot-pull-request-reviewer[bot]'`.
  FO does not mention `@copilot` in a PR comment: Copilot reads a mention as a request for
  new work, and kc-pr-flow saw spurious PRs and duplicate reviews from it.
- **Watch:** FO adds the PR with `python3 <package>/scripts/pr_watch.py add --copilot
  <owner/repo>#<N>`, so `<package>/scripts/pr_watch.py wait` also wakes on a Copilot verdict.
- **Read:** FO reads each round with `python3 <package>/extensions/copilot/copilot_review.py
  <owner/repo> <pr>`: exit 0 is a clean round on the head, exit 1 its findings, exit 3
  (requested, not yet answered) or 4 (no review of the head) is no verdict, so the round
  is not counted and merge is not asked for. FO counts one round per `evidence=` id it
  prints. Copilot's High severity, and any level above it, counts as P1. Exit 2 is a
  configuration error, reported as `copilot not run: <reason>`.
- **Limits:** the reader reads the review shapes Copilot posted in 2026: the
  `ccr-overview-v2` overview, clean only with "Approval recommended", "0 open findings" and
  no "Previously missed" item (a "Needs a closer look" review with 0 open findings carried
  one), with severity icons counted outside the "resolved since last review" list; and the
  older "Pull request overview" that "generated no comments". It does not use a documented API. A
  shape it does not recognize reads as findings when Copilot left a line comment and as
  no verdict otherwise, never as clean. Copilot may write the review body in another
  language; the reader keys only on those markers and on the reviewed commit. On
  2026-10-12 a request took about two minutes to answer. Each review uses the requesting
  account's Copilot allowance. On 2026-10-12 a request made three seconds after a push was
  answered five minutes later with a review of the new head; the reader still counts only
  a review whose commit is the head.
