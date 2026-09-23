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
When the change alters what a user sees, the evidence includes a screenshot of the
changed screen at the candidate; reading the code or a passing render test is not
seeing it.

For a decisive check, identify evidence that it detects the relevant known error.
Reuse applicable negative or mutation evidence; only when it is missing, run the
smallest counterexample needed. Do not rerun every check or an already-green suite
just to demonstrate this principle.

Every validation stage ends with a minimal acceptance script the Captain can run
himself: three to six steps, five minutes or less, each naming the action and the
expected observation, written for someone outside this session — an exact command
or URL, no internal identifier to look up, no secret in the text. State what it
does not cover, so a pass is not mistaken for proof of the whole change. When the
change has no user-visible surface, the script says so and substitutes the
smallest observable command whose output he can read, rather than being
omitted silently.

Report verdict, artifact identity, evidence and material limits in the existing
SD stage report. A code repair returns through implementation feedback; scope or
profile changes return to the affected user decision. The user or named owner
retains gate and delivery authority. Green checks do not prove merge or adoption.
