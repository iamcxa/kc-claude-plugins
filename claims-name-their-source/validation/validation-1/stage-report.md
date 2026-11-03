## Stage Report: validation

- DONE: Independent verdict on PR #777 head f79711ca against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  **REJECTED pending F1/F2 disposition**, at `f79711ca8d6325c1c14781342cf23855dd62b10a`; evidence: `claims-name-their-source/validation/validation-1/details.md`, criteria.json, findings.json and manifest.json (commands run 2026-11-04 Asia/Taipei).
  AC-1/4 pass: repository lint 5891/5891; removing the +55 ledger or changing the chat phrase fails lint. AC-2 passes exit 0/1/2 fixtures; removing check's emit fails only its test, while question stays green.
  AC-5 independently recounts stacked-parent startup 5836+48 to 5891+48, question 3 to 30 and check 57 to 84; unchanged idle/archive/ideation sources and a deleted-rule count falsifier are retained.
  AC-6 passes the exact-head full discovery command: 892 tests, six skips, exit 0; missing required ADR 0055 fails its copied-folder falsifier. No candidate product bytes were repaired.
- DONE: Captain amendment 1 superseded AC-3 with AC-7 (Claude only, 6 candidate runs per scenario, the original 5 of 6 bar, the Codex half not runnable on this machine). Judge AC-7 from validation/implementation-2 and implementation-3, including the reported K grader base false-pass and the narrower read that 3 of 6 K candidate answers label the wrong count; the head moved to f79711ca8 by a forward merge of #773, so rerun the suite and the other criteria here. Do not start agents you were not asked to
  Regrading frozen outputs reproduces P 6/6 and K 6/6, base P 1/3 and K 3/3. Prompt hashes, raw answers, frozen inputs and candidate workflow hash agree; original/corrected falsifiers rerun unchanged. A title-only wrong-count counterexample false-passes (replay-audit.json).
  Independent target-claim read agrees with implementation: only K runs 1/5/6 label the disputed limit; 2/3/4 label other counts (semantic-read.json). This does not replace the fixed grader; F1 holds the claim that its score proves the accepted behavior. No agents or new provider runs started; stored attempts remain 22/30.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  `validation/validation-1/acceptance.sh` has six exact steps, expectations and cleanup; unchanged bytes ran with `/bin/bash --noprofile --norc`, exit 0, full output in acceptance.log. It reproduces both holds; exit 0 is not delivery acceptance.
  Required .claude ADR lint with `--since origin/main --require 0055` exits 0: 52 records, 0 legacy. Active .codex package agrees; number guard, design/dispatch checks, document dispositions and comment ratio are recorded in checks.json and details.md.
- FAILED: Required number-guard check against the assigned origin/main base.
  `number_guards.py check --base origin/main --head f79711ca8...` exits 1 on parent ADR 0054; the same exact candidate checked against stacked parent `128fe3e3fed70fa64ded8657f5a1b36933af3ced` exits 0. Parent PR #773 is open and owns that reservation; no base or task reservation was changed.
- DONE: Judge disclosed limits and preserve independent evidence.
  Safe-mode isolation rests on documented help, not a file-open trace; one model, small samples, combined README/reminder in K, incorrect-but-attributed reports and daily FO behavior remain limits. Eight document dispositions checked; comment ratio 0.2% within 5%; no CI trigger changed and CI cost per PR not measured.
- SKIPPED: Product repair, rubric change, new model replay, review requests, PR comments, marking ready, code push and merge.
  FO retains disposition, review and delivery authority. Active-skill dispatch check passes five records; older .claude completion-grammar drift is retained as a diagnostic, not five missing handoffs.

### Summary

The exact candidate passes its structural, local caller and word-count checks; the full suite and fresh-shell script were rerun after the parent merge. The unchanged grader's mechanical pass cannot establish the count-scenario target behavior, and the explicitly assigned trunk number check is red, so this validation recommends REJECTED pending the two dispositions below.

- F1 Needs decision: K's fixed grader false-passes the base and a title-only wrong-count control; the target limit is labelled in only 3/6 candidate answers against the retained 5/6 bar (`value-ac[AC-7]`). FO must route this evidence discrepancy for a recorded Captain disposition before repair or another replay; four evidence fields and trigger sources are in findings.json.
- F2 Needs decision: `contract[kc-dev-flow-2/references/sd/workflow.md#number-guards]` is held at the required `origin/main` comparison by the still-open stacked parent's ADR 0054. FO must reconcile the comparison/delivery sequence without cross-owning that reservation; passing the parent-based control does not erase the required failure.

