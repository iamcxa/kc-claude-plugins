# learn extension

Records an independent read of FO's records and starts the learning loop when a task closes.
A repository uses it by listing `learn` under `extensions:` in its workflow README
frontmatter.

- **Needs:** `gh` authenticated for the code repository, the `kc-dev-flow-2:learn`,
  `kc-dev-flow-2:evaluate-learning` and `kc-dev-flow-2:observer` skills, and the observer
  agent.
- **Joins:** FO, through the package mod, before the landed sentinel of a merged task PR and after its archive.
- **FO step:** the package mod runs `python3 <package>/scripts/pr_watch.py tasks <workflow dir>` at startup and idle. For a merged task PR it runs `python3 <package>/scripts/observer_check.py` before the sentinel, and its output names each next step.
- **Read:** learn's result is its notice (no-change, proposal, pending or uncertain). A
  proposal is delivered only under learn's own delivery authority, never by this step.
  The observer report is one line per finding, each with its quoted rule and evidence.
- **Cannot run:** a learn claim refused because another job is unsettled: when that job's
  delivery is `open`, FO first settles it from its PR as learn's `Follow the delivery to a
  recorded end` says and retries once; otherwise it is reported as
  `learn not run: blocked by job <id>` and not retried; settle or release that job first.
  A hold in learn's closure checks is its reported result, not a failure of this step.
- **Limits:** the check proves a non-blank file is committed, not that the observer wrote it,
  and only FO's reading of this text makes FO run it. Apart from `observer.md`, nothing here
  changes the task, unlocks a delivery or merge, or files an issue. The observer reads
  committed state only, so a rule kept in chat shows as `can't tell`.
