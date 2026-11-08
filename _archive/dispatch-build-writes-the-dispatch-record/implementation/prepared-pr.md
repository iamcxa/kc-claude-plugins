feat(kc-dev-flow-2): record stage dispatches before building

Stage dispatch records previously depended on FO saving a separate copy before
building the worker artifact. Add `dispatch_stage.py` to write the record from
the build's checklist and scope notes, run both existing record checks, then
build through Spacedock. The pinned stamp commit includes the record; advance
dispatches commit it before returning their envelope. Immediate identical retries
reuse their record, while changed input or an intervening state commit creates a
new round. Failed checks/builds remove the new record, including its index entry.

Keep model/roster supplied by FO and leave the package-version/workflow-checkout
preflights separate. Record the accepted ruling in ADR 0070. Replace the three
approved workflow passages verbatim and lower the word budget from 5933 to 5931.

The additional `kc-dev-flow-2/skills/observer/SKILL.md` edit was authorized by FO
in implementation follow-up 1: its chat-only command entry must match the shortened
README command, as enforced by `lint-skills.py`. The uncorrected entry fails lint;
the updated entry passes. No other observer behavior changes.

Validation: real Spacedock 0.27.2 split-root seam tests, the lint mutation suite,
dispatch-record tests and real dispatch transport checks; thirteen counterexamples
exercise the accepted falsifiers. A fresh-shell acceptance runner exports the
exact candidate without bytecode caches and retains its logs under the task's
`implementation/fresh/` state evidence. Candidate ADR lint, number guards,
comment ratio and document dispositions are recorded there. The installed 0.35.0
ADR linter has the base's known pre-#806 false positive on a deliberate historical
ADR assertion; FO authorized using the candidate's corrected linter. That historical
assertion is unchanged.

The new CI step uses the workflow's existing package/workflow path triggers and
pinned real binary. CI cost per PR: not measured. Hosted CI and RoboRev are not
run by this worker; FO owns product publication and both reviews. No version bump.
