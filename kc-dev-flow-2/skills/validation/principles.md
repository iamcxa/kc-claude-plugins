# Validation principles

Check the exact delivered artifact against the approved outcome and relevant
primary evidence. Separate checks actually run, evidence only read, and work
not verified. Observe the selected failure boundary as well as the successful
path when that boundary determines acceptance. At the same candidate, assess both
goal sufficiency and minimal necessity: does the accepted goal work at the selected
profile's depth, and does the without-it observation justify each retained change
or removal? Check that remaining surfaces map to the goal, a named falsifier,
safety boundary or required lifecycle obligation; a deletion earns its place by
the same standard as retention. Use existing evidence, not a new proof harness.

Read every comment the candidate adds. A comment that narrates the change, restates
the code beside it, cites a line number or marks a section is a repair finding.
Measure them with
`python3 <package>/scripts/comment_ratio.py <base> <candidate> --workflow-dir <workflow-dir>`
and report its output. Exit 1 (a ratio above the maximum, or a comment citing task
numbering, review provenance, a PR or issue number or a `file:line`) is a repair
finding returned through feedback; exit 2 is a configuration error that returns to FO.
The citation scan finds the named classes only, so still read every added comment.
When the task has a `## Number guards` section, rerun its `check` at the candidate; exit 1 is a repair
finding returned through feedback and exit 2 is a configuration error that returns to FO.
Validation runs `python3 <package>/scripts/adr_lint.py docs/adr --since <base>`, which
requires every record the candidate added or changed, plus `--require <numbers>` for
each `ADR:` number the task's `## Number guards` reserves and any number the
implementation report names; exit 1 or a missing record returns through the existing
feedback route, and exit 2 is a configuration error that returns to FO.
Read the task's dispatch records (`<task>/dispatch/` in the state checkout) for the
implementation cycles you validate, and run
`python3 <package>/scripts/dispatch_records.py <task folder>`; a missing or incomplete
record (its exit 1), or a requirement in it that traces to no accepted criterion or
Captain ruling, is a finding for FO.
When the change alters what a user sees, the evidence includes a screenshot of the
changed screen at the candidate; reading the code or a passing render test is not
seeing it.
When the task's `Surfaces:` include `ui` and it has a `Design review:` line, dispatch
`kc-dev-flow-2:design-director` with that screenshot (pass 2a: `Screenshots:`,
`Criteria:` naming the criteria whose text names the running screen, `ADR folder:` as
in [design-review.md](../ideation/design-review.md)). Give `Screenshots:` as the path relative to the task folder (for example
`design/built-1.png`) and add `Task folder:` with its absolute path so the director can open it;
the report's `preview:` copies that relative path, which is the form the check resolves and
the only one it accepts. Save its report as
`design/validation-<N>.yaml` and write `Built screen review: design/validation-<N>.yaml`
in your validation Stage Report (the check reads the last one) with one `Built screen finding <n>:` line per finding: `F<N>` for a MAJOR, naming
its bullet in your report, and `declined: <reason>` or `Needs decision: <text>` for a
MINOR. Send each MINOR you would decline to the director first (pass 2b), save the
rulings as `design/validation-declines-<N>.yaml` and name them on a
`Built screen decline check:` line; a decline it overrules or sends to a decision
becomes `Needs decision:`. Only the Captain's quoted words waive the review:
`Built screen review: waived 「<his words>」`.

For a decisive check, identify evidence that it detects the relevant known error.
Reuse applicable negative or mutation evidence; only when it is missing, run the
smallest counterexample needed. Do not rerun every check or an already-green suite
just to demonstrate this principle.

Every validation stage ends with a minimal acceptance script the Captain can run
himself: three to six steps, five minutes or less, each naming the action and the
expected observation, written for someone outside this session — an exact command
or URL, no internal identifier to look up, no secret in the text. FO runs it as
written before the gate, so it runs unchanged in a fresh shell and names any checkout
or install it needs. State what it
does not cover, so a pass is not mistaken for proof of the whole change. When the
change has no user-visible surface, the script says so and substitutes the
smallest observable command whose output he can read, rather than being
omitted silently.

Report verdict, artifact identity, evidence and material limits in the existing
SD stage report. List each finding as its own `- F<N> <Class>: …` bullet, and split a
finding with parts into one bullet per part. A code repair returns through implementation feedback; scope or
profile changes return to the affected user decision. The user or named owner
retains gate and delivery authority. Green checks do not prove merge or adoption.
Do not invoke local fallback, push the trunk, merge, or clean up an owned worktree unless
the specific action is authorized.
