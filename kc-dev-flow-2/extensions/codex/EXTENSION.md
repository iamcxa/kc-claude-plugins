# codex extension

Reads Codex GitHub review rounds on a delivery PR. A repository uses it by listing
`codex` under `extensions:` in its workflow README frontmatter.

- **Needs:** `gh` authenticated for the repository, and Codex GitHub review set up on it.
- **Joins:** FO steps: review findings, step 5 (counting external-review rounds), and the
  merge ask.
- **Read:** FO reads each round with `python3 <package>/extensions/codex/codex_review.py
  <owner/repo> <pr>`: exit 0 is a clean round on the head, exit 1 its findings, exit 3 or 4
  no verdict on the head yet, so the round is not counted and merge is not asked for; FO
  counts one round per `evidence=` id it prints. Exit 5 is a Codex comment on the head that the
  reader does not recognize (`unrecognized=comment:<id>`): no round and never clean; FO keeps
  waiting as for exit 4 until `<package>/scripts/pr_watch.py wait` gives up on it, then does the
  `next:` lines it prints. Exit 6 is a code review of the head that Codex's summary shows running with no
  update for 30 minutes and no verdict on the head yet (`stalled=<time>`): no round and never clean.
  `<package>/scripts/pr_watch.py wait` then prints the `next:` line: comment `@codex review` once; if it
  stalls again, report `codex not run: review stalled twice on <head>` and name Codex as not read in the
  merge ask. Exit 2 is a configuration error, reported
  as `codex not run: <reason>`.
- **After a repair:** when FO pushes a repair to the PR, it comments `@codex review` there,
  because a push brings no new review by itself.
- **Limits:** the reader is a compatibility adapter for the comment and reaction shapes
  Codex leaves, not a documented API. A shape it does not recognize reads as findings or
  as no verdict, never as clean. Once the summary carries a state marker it decides; an eyes
  reaction counts only without one.
