# learn extension

Records an independent read of FO's records and starts the learning loop when a task closes.
A repository uses it by listing `learn` under `extensions:` in its workflow README
frontmatter.

- **Needs:** `gh` authenticated for the code repository, the `kc-dev-flow-2:learn`,
  `kc-dev-flow-2:evaluate-learning` and `kc-dev-flow-2:observer` skills, and the observer
  agent.
- **Joins:** FO, after it observes the task's PR merged and before it writes the landed
  sentinel (`status --set <slug> pr=pr-merge:<N>`), which the `pr-merge` startup and idle hooks
  follow at once with `state commit` and `merge guard`; and again right after the archive.
- **FO step:** before the sentinel, FO runs `python3 <package>/scripts/observer_check.py <state>
  <slug>`. Exit 0 lets the sentinel, `state commit` and `merge guard` run. Exit 1: FO
  dispatches `kc-dev-flow-2:observer` with only the state checkout, the slug and this README's
  path, saves the report unedited as `<task>/observer.md`, commits it with `spacedock state
  commit <slug> --workflow-dir <dir>` and runs the check again; an archived task's state is
  publish-only, so that commit would be refused after the archive. Exit 2: FO holds and
  reports the cause. After the archive FO runs the check once more. Exit 1 there means the
  step was missed: FO dispatches the observer over both path pairs of the archived task,
  saves the report unedited as `_archive/<slug>/observer.md`, stages and commits that path alone
  with `git -C <state> add -- _archive/<slug>/observer.md && git -C <state> commit -m <message>
  -- _archive/<slug>/observer.md`, publishes it with
  `spacedock state commit <slug> --workflow-dir <dir>`, and says in the Captain's message that
  the observer ran after the archive. FO then runs `kc-dev-flow-2:learn` for the archived slug
  and presents both results to the Captain in one message: learn's notice, then the observer
  report unedited. FO does not answer a finding in that message; the Captain rules on the
  ones he wants acted on.
- **Read:** learn's result is its notice (no-change, proposal, pending or uncertain). A
  proposal is delivered only under learn's own delivery authority, never by this step.
  The observer report is one line per finding, each with its quoted rule and evidence.
- **Cannot run:** a learn claim refused because another job is unsettled is reported as
  `learn not run: blocked by job <id>` and not retried; settle or release that job first.
  An observer that cannot be dispatched is reported as `observer not run: <reason>`, and FO
  commits that one line as `observer.md` so the check passes and the Captain sees it. A
  hold in learn's closure checks is its reported result, not a failure of this step.
- **Limits:** the check proves a non-blank file is committed, not that the observer wrote it,
  and only FO's reading of this text makes FO run it. Apart from `observer.md`, nothing here
  changes the task, unlocks a delivery or merge, or files an issue. The observer reads
  committed state only, so a rule kept in chat shows as `can't tell`.
