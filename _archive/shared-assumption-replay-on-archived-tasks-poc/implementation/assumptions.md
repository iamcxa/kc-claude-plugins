# Final five assumptions before opening any dispatch 3

This file supersedes the counted set in evidence/implementation-1/assumptions.md; that earlier frozen file remains unchanged. All five below use implementation, the earliest eligible implementation/validation stage with at least three saved dispatches. No third dispatch has been opened.

## Replacement and exposure

delivery-gate-verdict-form is the first FO-listed replacement and is not named in the learning.md read. No earlier replacement was skipped; the other two were not reached.

Excluded: ui-design-review-in-ideation. The required learning.md read disclosed its later fence-blind Surfaces-count/corpus-verdict repair; it stays outside the count.

Allowed-input temporal leakage: report ordinals do not map one-to-one to dispatch ordinals. Later fixes may already appear in the first two reports; this limits blind prediction, even if the hypotheses precede opening dispatch 3.

Scoring: Record literal causal-premise match to dispatch 3 separately from blind-prediction support. Prior knowledge supplied by an allowed worker report is disclosed and is not independent evidence the stop prompt predicted a later cause. Never count the excluded UI row.

## Frozen hypotheses

### fo-lifecycle-mod

**Named assumption:** Moving lifecycle instructions into mods and testing their hook order is enough to make every real merge path run the intended observer/watch work before a sentinel is written.

**Check I would run (proposed, not executed):** In a throwaway workflow, run the real merge guard with pr empty and pr populated, force the observer check to fail, then inspect whether any pr-merge path still writes the merged sentinel or starts a second watch. Failure of either ordering refutes the premise.

**Quotations from allowed input:**

> `case pr != ""` returns `signalBlocked` before `arm` is reached

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/fo-lifecycle-mod.md:458-474` (report 1).

> a failed observer check cannot stop `pr-merge`'s own scan from writing the sentinel

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/fo-lifecycle-mod.md:475-494` (report 2).

**Input limit:** The first report stopped before changing code; the second reports an amended implementation. These are not two failed fixes of one check.

### merge-gatekeeper

**Named assumption:** A passing delivery check and a merge line pinned to the current head remain sufficient authorization until the head changes, even if a failure record or a grant changes at that same head.

**Check I would run (proposed, not executed):** After producing a passing head-pinned merge line in a throwaway repository, add a failure record or remove the grant without moving the product head; attempt the supported merge entrance and require refusal. A still-runnable line refutes the premise.

**Quotations from allowed input:**

> prints a head-pinned merge line only for a class with a valid README grant

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/merge-gatekeeper.md:363-376` (report 1).

> the printed merge line stays runnable after a later failure record or grant removal

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/merge-gatekeeper.md:377-387` (report 2).

**Input limit:** Dispatch 2 is an in-flight security-review message already covered by report 1. Report 2 is a later pin repair, so dispatch/report ordinals do not identify two sequential attempts.

### prod-security-review-gates

**Named assumption:** Changing the brief or splitting the review by gate can make an unchanged reviewer find the same runtime write-limit defect when validation is confined to a diff that does not touch the responsible handlers.

**Check I would run (proposed, not executed):** On the saved design and validation diff, identify the public entrance and trace it to the session/comment write handlers; compare whether the existing validation review scope includes those handlers. If they are out of scope, another brief-only attempt cannot establish that runtime coverage; return the scope decision instead of patching the wording again.

**Quotations from allowed input:**

> the brief cannot make the unmodified reviewer name the unbounded session or comment creation finding

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/prod-security-review-gates.md:371-387` (report 1).

> the finding lives in handlers the diff does not touch and standard tier does not trace them

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/prod-security-review-gates.md:388-406` (report 2).

**Input limit:** Dispatch 2 only supplies a reserved ADR number. Report 2 already contains a gate-splitting amendment and a later validation replay; it is not a report of an independent second dispatched fix.

### dev2-laws-check

**Named assumption:** A latest representation, or just the newest addition of a dispatch-record path, is a sufficient proxy for all historical additions that the law must judge.

**Check I would run (proposed, not executed):** In a throwaway history, add a violating record, correct it, delete it, and re-add a corrected record at the same path; judge the original event and require it to stay a violation. Compare this with judging only the tip or newest add; either erasing the original violation refutes the premise.

**Quotations from allowed input:**

> `--rev <commit>` replaced by the tip (AC-3c)

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/dev2-laws-check.md:372-394` (report 1).

> a later fix, deletion or sibling deletion must not clear a violation

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/dev2-laws-check.md:451-469` (report 2).

> a record deleted and re-added corrected at the same path leaves its first add unjudged

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/dev2-laws-check.md:451-469` (report 2).

**Input limit:** Dispatch 2 only reserves an ADR number. Report 2 already describes fixes requested after external review; its cycle label is also cycle 1. Historical-event scope is an inference, not evidence that the first two dispatches were two failed fixes.

### delivery-gate-verdict-form

**Named assumption:** A syntactically recognizable Verdict/PASSED label is enough to recover the current validation decision, even when the label is qualified as prior or candidate lookup can fall back to an older passing section.

**Check I would run (proposed, not executed):** On throwaway report strings, put Prior Verdict: PASSED before the real Verdict: REJECTED, then put a same-head later REJECTED section over an older PASSED section and a latest PASSED without a candidate over an older one with a candidate. Require no current passing candidate in all three cases; accepting one refutes the premise.

**Quotations from allowed input:**

> a qualified label (Independent Verdict: PASSED, Prior Verdict: PASSED) is accepted as the verdict

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/delivery-gate-verdict-form/dispatch/implementation-2.md` (dispatch 2).

> the latest section with a candidate still wins

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/delivery-gate-verdict-form.md:424-444` (report 1).

> the latest validation section with a counting Verdict form now decides

Source: `.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/delivery-gate-verdict-form.md:503-518` (report 2).

**Input limit:** Dispatch 2 is read-only investigation, not a second attempted repair. The allowed report 2 already describes cycle-3 repair under a later amendment; any matching corrective premise may therefore be known from the permitted report input. Before selection, the allowed laws report 2 also named this task implementation-4 as a bare-script-name example; that is disclosed and not used as the verdict hypothesis.

## Commit/read boundary

No archived implementation-3 content has been opened. FO will commit implementation/assumptions.md and reply committed <sha> before any third-dispatch read. Original five (including excluded UI) remain frozen separately at 9bc6c6e699def6958069d85e4374bb344b95e4e3.

FO direction: record `dispatch/implementation-1-message-1.md` and the worker-thread FO note of this dispatch. The report will identify the actual commit and verify these bytes before opening the third records.
