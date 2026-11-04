## Stage Report: implementation

- DONE: Update docs/adr/0055-a-claim-names-its-source-and-the-gate-scripts-print-the-rule.md to the ruled proof under Captain amendments 1 and 3, quote his words verbatim, and remove "Claude and Codex, three runs per cell".
  Candidate `69f4988612d17c5524887f99c872a0ef384d05c9`, branch `spacedock-ensign/claims-name-their-source`, repair base `eb556c61a775f148fa7ae6410b5d106ff32d917c` (FO's merged-main head). Only ADR 0055 changes (`git diff --name-only <repair-base> HEAD`, 2026-11-04); no runtime, test, version or criterion edits.
  ADR 0055 quotes amendment 1's 「可以」 and amendment 3's 「甲」 with their exact Asked questions. `ruling-proof.json` compares both answers/questions with the task, confirms the superseded host/sample statement absent, and the named follow-up present (2026-11-04).
- DONE: Record Claude-only proof (claude-opus-5-5, --safe-mode), the Codex half not runnable here, P 6 of 6 against base 1 of 3, K 3 of 6 labelled against base 0 of 3 as the known limit, the K grader's base false-pass, and follow-up counts-name-the-run-that-produced-them.
  `python3 -B audit.py`, `proof-audit.json` (2026-11-04): saved model/flag records and answer hashes agree; P grader counts are 6/6 vs 1/3; K target-label counts are 3/6 vs 0/3 from validation-2's independent manual classifications. The unchanged K grader still gives 6/6 vs 3/3 by false-passing the base's title plus “not re-run”. No rubric change or new provider call.
  The ADR distinguishes the faulty mechanical score from the accepted target-claim limit, names candidate runs 1/5/6, and records the existing follow-up. It retains one-model/small-sample, combined K wording, documented safe-mode rather than file-open tracing, and daily-FO limits. No reliable count-correction claim.
- DONE: Run the ADR lint with --require 0055 and the full suite at the updated candidate.
  `adr-lint.log`: `python3 -B <package>/scripts/adr_lint.py docs/adr --since eb556c61a775f148fa7ae6410b5d106ff32d917c --require 0055` exits 0, 53 ADRs checked. `python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'` exits 0: 906 tests, 6 skips (`full-suite.log`, 2026-11-04). Commands ran 2026-11-04; package is the active skill root, `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`.
- DONE: Recheck the post-parent number guard, comment ratio and affected-document list.
  `number-guards.log`: `number_guards.py check --base origin/main --head HEAD` exits 0, bound to main `2bda2e98304261d46b0ae7205a29ddc9038d2b4d` and the candidate. `comment-ratio.log`: 0 code/0 comment lines; maximum not enforced below its code-line floor, exit 0. `doc-impact.txt`: 0 documents mention the changed ADR, exit 0.
- DONE: Commit locally and prepare an updated PR body stating the narrowed proof; append a complete implementation report with the new head.
  Local commit is the candidate above. Exact title/body: `claims-name-their-source/validation/implementation-1-message-1/pr-title.txt` and `pr-body.md`; report, commands and source hash in the same folder. Task frontmatter and Captain amendments unchanged by this worker.
- DONE: Preserve the already implemented source rule, approved budget ledger, reminder outputs and observer boundary.
  Carried implementation and validation evidence remains in implementation-1, implementation-2/3 and validation-2; this repair changes only the retained decision record. New full discovery checks callers at the current candidate; historical replay outputs are audited, not regenerated.
- SKIPPED: Product push, PR #777 update, exact-head RoboRev, fresh independent validation and hosted CI.
  FO owns these steps under the existing dispatch. No PR comment, review request, ready or merge action. CI cost per PR is not measured; no CI trigger changed. This report grants no delivery approval.

### Summary

This complete report supersedes earlier implementation reports for the current candidate. ADR 0055 and the prepared PR body now state the Captain's narrowed Claude-only proof and accepted K 3-of-6 limit with the grader false-pass and named follow-up visible. The required local checks pass; FO retains fresh validation, review and delivery.
