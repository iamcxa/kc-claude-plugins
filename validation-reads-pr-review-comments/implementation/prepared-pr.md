fix(kc-dev-flow-2): frame validation around merge readiness

**HOLD: AC-3 is not met. This is prepared handoff text, not a published PR.**

Validation previously focused on the artifact and acceptance criteria while an
unaddressed PR review comment at the candidate head remained unread. The proposed
one-file change frames the verdict as whether the Captain can merge that candidate
at its head, including the open PR and other relevant evidence. PASSED answers the
question and retains the Captain's merge authority.

Only kc-dev-flow-2/skills/validation/principles.md changes: 826 to 877 words.
The workflow remains 5931 words; no version or ADR change.

Static skill lint, installed ADR lint, number guards, comment ratio and design-
surfaces checks pass, and the registered counterexamples detect their mutations.
The behavioral replay attempted 12 scheduled cells on Claude claude-opus-5-5 and
Codex gpt-6-astra xhigh. There were 14 raw attempts and only
7 valid reports; five scheduled fixture gaps (including both candidate timeouts)
prevent the required three-per-arm samples. Claude's original wording already
scores 3/3, so a strict improvement
over that baseline is impossible in this reconstruction.

**The primary and post-hoc counts disagree on whether candidate beats base in the
available Codex subset:** registered 1/2
base versus 2/2 candidate;
post-hoc 2/2 versus
2/2, tied. The
manual column was defined after the first valid result; the registered grader is
unchanged. Neither subset satisfies AC-3. The Captain rules on this distinction at
the validation gate if work is advanced after an authorized evidence revision.

No wording 2 or third wording was used. All evidence, raw reports, shim logs,
reported token usage, historical substitutions and falsifiers are under the task's
implementation/replay folder in state. Recommend holding this candidate and
returning the evidence route to FO/Captain, not claiming behavioral improvement.

Product candidate: 7f47317bb278931a873c0ec63302fbc70fc53fc4
Base: e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e
Branch: spacedock-ensign/validation-reads-pr-review-comments

FO owns push, Draft PR creation, RoboRev and hosted CI. No product push or PR
was made here. RoboRev not run: FO owns local review under the dispatch.
CI cost per PR was not measured; no CI configuration or trigger changes.
