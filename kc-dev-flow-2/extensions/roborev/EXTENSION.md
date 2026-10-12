# roborev extension

Runs a local roborev review of the implementation's committed changes before the worker
reports. A repository uses it by listing `roborev` under `extensions:` in its workflow
README frontmatter.

- **Needs:** `roborev` on the PATH with its daemon running (`roborev status`) and a review
  agent configured.
- **Joins:** implementation, before the stage report.
- **Instruction FO adds to the scope notes:** "Before reporting, commit your changes and run
  `python3 <package>/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`.
  On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and
  report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:`
  line on exit 3, in the stage report."
- **Read:** exit 0 is clean, 1 findings, 2 bad arguments, 3 incomplete (roborev missing, its
  daemon not running, uncommitted changes, a timeout, or a job not bound to the base and
  head). Incomplete is reported as `roborev not run: <reason>` and never counts as clean.
- **Limits:** `roborev review --local` is not used: it exits 0 with findings, stores no
  result, and reviews an older commit against the current files. roborev findings are
  development feedback for the worker, not an external review round, and validation stays
  independent of them. A RoboRev review posted on the PR is an external round under FO steps:
  review findings, step 5; this local gate never is.
