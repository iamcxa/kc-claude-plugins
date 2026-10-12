# codex extension

Reads Codex GitHub review rounds on a delivery PR. A repository uses it by listing
`codex` under `extensions:` in its workflow README frontmatter.

- **Needs:** `gh` authenticated for the repository, and Codex GitHub review set up on it.
- **Joins:** FO steps: review findings, step 5 (counting external-review rounds), and the
  merge ask.
- **Read:** FO reads each round with `python3 <package>/extensions/codex/codex_review.py
  <owner/repo> <pr>`: exit 0 is a clean round on the head, exit 1 its findings, exit 3 or 4
  no verdict on the head yet, so the round is not counted and merge is not asked for; FO
  counts one round per `evidence=` id it prints. Exit 2 is a configuration error, reported
  as `codex not run: <reason>`.
- **After a repair:** when FO pushes a repair to the PR, it comments `@codex review` there,
  because a push brings no new review by itself.
- **Limits:** the reader is a compatibility adapter for the comment and reaction shapes
  Codex leaves, not a documented API. A shape it does not recognize reads as findings or
  as no verdict, never as clean.
