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
  <owner/repo>#<N>`, so `<package>/scripts/pr_watch.py wait` also wakes when Copilot answers.
- **Read:** `python3 <package>/extensions/copilot/copilot_review.py <owner/repo> <pr>` says
  only whether Copilot has answered the head: exit 0 names the review (`evidence=review:<id>`,
  one round per id), its heading line and its line-comment count; exit 3 (requested, not
  answered) or 4 (no review of the head) is no verdict, so the round is not counted and
  merge is not asked for; exit 2 is a configuration error, reported as `copilot not run:
  <reason>`. On exit 0 FO reads that review with `gh api repos/<owner/repo>/pulls/<N>/reviews/<id>`
  and its line comments, and records the round in the committed gate summary with the
  heading line quoted. The round is clean only when Copilot recommends approval and lists
  no open or previously missed finding and no line comment; otherwise each finding goes
  through FO steps: review findings, and Copilot's High severity, or any level above it,
  counts as P1.
- **Limits:** Copilot's review text has no documented format and changed layout three times
  in the reviews read for this extension, so the script does not judge it; whether a round
  is clean is FO's reading, and the observer can check that reading against the quoted
  heading. Copilot may write the review body in another language. On 2026-10-12 a request
  was answered in about two minutes, and a request made three seconds after a push was
  answered five minutes later with a review of the new head. Each review uses the
  requesting account's Copilot allowance.
