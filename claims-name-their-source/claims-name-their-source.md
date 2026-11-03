
## Stage Report: implementation

- DONE: Move Captain amendment 1 into `## Acceptance criteria`: replace AC-3 with AC-7 carrying "Amended by Captain, amendment 1" and his ruling's words only.
  AC-3's block moved verbatim to `Superseded text:` in Amendment 1; AC-7 carries the Asked words and the amendment label, no other text. `python3 <package>/scripts/design_surfaces.py check claims-name-their-source.md` printed "design surfaces presentable", exit 0 (2026-11-04).
- DONE: Run 3 more candidate runs per scenario (P and K) with the same preregistered harness, claude-opus-5-5, `claude -p --safe-mode`, normal HOME, scratch cwd; record tokens per run; stay within 30 attempts.
  `validation/implementation-3/`: harness hashes verified, candidate README hash equals the worktree's workflow.md at f79711ca8. 6 of 6 answered, 0 retries; attempts 16 + 6 = 22 of 30. Tokens per run in `results.md` and each `meta.json`: 110,673 input and 5,974 output in total. No credential copied. "CLAUDE.md not loaded" rests on documented `--safe-mode`; no file-open trace.
- DONE: Judge AC-7 by the preregistered grader and the original bar of 5 of 6 per scenario.
  Candidate P 6 of 6 and K 6 of 6 (runs 1-3 from implementation-2 plus runs 4-6): the bar is met for both. Each cell is n=6, one model.
- DONE: Report the K grader's base false-pass as found, without changing the rubric; record the Codex half as not runnable.
  K base answers pass because a title containing "Validation ... report" plus "not re-run" satisfies the "attributed" branch while they state two cells unlabelled (`results.md`). Narrower read, not the verdict: the wrong-count limit is itself labelled in 3 of 6 K candidate runs (1, 5, 6); the other 3 label the other counts only. Codex: `codex exec --help` lists no way to skip ~/.codex/AGENTS.md.
- DONE: AC-1, AC-2, AC-4, AC-5, AC-6 and ADR 0055.
  Carried from `validation/implementation-1/`, not re-run here (this dispatch changed no product file). Product head now f79711ca8d6325c1c14781342cf23855dd62b10a, which FO moved after implementation-2; I did not re-run the suite on it.
- SKIPPED: Push, Draft PR, RoboRev, CI on the PR head.
  FO's duties; none done or claimed.
- DONE: Commit evidence to the state checkout.
  `spacedock state commit claims-name-their-source --workflow-dir <workflow>`, receipt below in the completion message.

### Summary

This supersedes the earlier `## Stage Report: implementation`. Amendment 1 now sits in the criteria as AC-7 (AC-3 withdrawn into its entry), and AC-7 is met by the preregistered grader: the candidate passed P 6 of 6 and K 6 of 6 on Claude. The K result cannot show a base-versus-candidate difference because the grader passes the base answers too; on a narrower read only 3 of 6 K candidate runs label the wrong-count limit itself, so the evidence that the rule changes K behavior is weaker than 6 of 6 suggests, while P is clean. The product-level checks were not re-run on the new head f79711ca8.
