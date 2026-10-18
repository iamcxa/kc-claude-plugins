Draft text for `skills/observer/SKILL.md`, placed after the "Check at least" paragraph. Not a repository file.

Replay the design check. For each backlog and ideation briefing, take the sha in its artifact `uri`
(`git-root://state/<sha>/<TASK>.md`), extract `<TASK>.md` and, when it exists at that sha, `<TASK>/` with
`git archive` into a new empty temporary directory, and run
`python3 <package>/scripts/design_surfaces.py check [--seed, for backlog] <that copy of <TASK>.md>`.
Report "FO runs `design_surfaces.py check`" as `ok` on exit 0, and as `violation` quoting its first line on exit 1.

Where `<TASK>/merge/ask-<N>.json` exists it is `delivery_gate.py check`'s saved passing run. Report "FO runs
`delivery_gate.py check` before the merge ask" as `ok` when its `time` is before the commit of that ask's
briefing and its `head` starts with the head the question names; when no file exists the task may predate the
record, so report `can't tell`. When the file holds `sufficiency` and `necessity` values, report "FO confirms both
goal sufficiency and minimal necessity" as `ok`, quoting both; when it holds neither key it predates that check, so
report `can't tell`.

Do not report these rules. Their only witness is the Captain's chat or a shell run that leaves no record, so
the report would only say `can't tell`:

<!-- chat-only-rules -->
- presents every step in full beside its observed output
- FO answers a question the Captain asks at a gate before dispatching on it
- scripts/package_version.py
- scripts/workflow_checkout.py
- dispatch_records.py --names
- assess the four evidence fields above
<!-- /chat-only-rules -->

A rule outside this list that you cannot judge stays `can't tell`.
