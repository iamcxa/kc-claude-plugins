# learn extension

Starts the learning loop and an independent read of FO's records when a task is archived.
A repository uses it by listing `learn` under `extensions:` in its workflow README
frontmatter.

- **Needs:** `gh` authenticated for the code repository, the `kc-dev-flow-2:learn`,
  `kc-dev-flow-2:evaluate-learning` and `kc-dev-flow-2:observer` skills, and the observer
  agent.
- **Joins:** FO, right after `merge guard --verdict passed` archives a task and its state
  is published.
- **FO step:** FO runs `kc-dev-flow-2:learn` for the archived slug, and dispatches
  `kc-dev-flow-2:observer` with only the state checkout, the slug and this README's path.
  It presents both results to the Captain in one message: learn's notice, then the
  observer report unedited. FO does not answer a finding in that message; the Captain
  rules on the ones he wants acted on.
- **Read:** learn's result is its notice (no-change, proposal, pending or uncertain). A
  proposal is delivered only under learn's own delivery authority, never by this step.
  The observer report is one line per finding, each with its quoted rule and evidence.
- **Cannot run:** a learn claim refused because another job is unsettled is reported as
  `learn not run: blocked by job <id>` and not retried; settle or release that job first.
  An observer that cannot be dispatched is reported as `observer not run: <reason>`. A
  hold in learn's closure checks is its reported result, not a failure of this step.
- **Limits:** nothing here changes the closed task, unlocks a delivery or merge, or files
  an issue. The observer reads committed state only, so a rule kept in chat shows as
  `can't tell`.
