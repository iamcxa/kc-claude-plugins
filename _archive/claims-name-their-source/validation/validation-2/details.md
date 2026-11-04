# Independent validation, cycle 2

Verdict: **PASSED under Captain amendments 2 and 3**. Candidate: f79711ca8d6325c1c14781342cf23855dd62b10a, iamcxa/kc-claude-plugins PR #777. Profile: Pilot. No product byte, criterion, reservation, frontmatter or recorded historical verdict was edited.

## Authority and identity

This rerun uses Captain amendments 2 and 3, committed after validation-1 (ruling-history.log). Amendment 2 permits number guards against the open stacked parent now, then origin/main after it merges. Amendment 3 withdraws AC-7, accepts K 3/6 as the known limit and requests a follow-up. AC-8 contains that ruling; AC-3 and AC-7 remain verbatim under their superseding entries. The existing task counts-name-the-run-that-produced-them is committed at 6d31cbe9c and records the specific wrong-count limitation.

The assigned branch and clean status were verified. Product checks ran in a detached throwaway checkout under the assigned worktree at the full candidate SHA above. PR #777 remains Draft/open at that exact SHA, with PR #773's branch as its base. PR #773 remains Draft/open at 128fe3e3fed70fa64ded8657f5a1b36933af3ced. Fetched origin/main is e1bee223c47a1cd534a665a47776b683375b34fc. Read-only provider receipts are pr-777.json and pr-773.json; successful hosted checks are observed status, not a new review or delivery grant.

Commands were run 2026-11-04 Asia/Taipei; manifest.json, checks.json, extra-checks.json and the logs name commands, working directories, UTC timestamps and exits. Product execution and mutations used only the assigned tree and disposable descendants. Evidence scripts are copies of the earlier validator's probes, reviewed before reuse, with candidate/output paths changed; every claimed check was executed in this run.

## Every active acceptance criterion

- AC-1 passes: lint reports 5891/5891 workflow words. The two approved sentences, exact +55 ruling and startup ledger are retained. Removing this task's ledger step makes lint fail, naming a missing raise of 55 (mutation-budget.log); restoring it passes.
- AC-2 passes: question/check pass, hold and unreadable-input fixtures preserve exits 0/1/2 and print the reminder once, before the final ASK. Removing only check's emit fails its test while question's control stays green (focused-tests.log, mutation-check.log, mutation-question-control.log).
- AC-4 passes at its stated static depth: the chat clause is the observer exclusion, while the summary clause remains judged. Rewording the README clause fails lint with the chat-only mismatch (mutation-chat.log). No native observer agent was launched or claimed.
- AC-5 passes: independently executed base and candidate commands give workflow 5836 to 5891, mod 48 unchanged, question 3 to 30 words and check 57 to 84 words; exits remain 0. wc independently agrees on workflow counts. Idle/archive/ideation sources are unchanged relative to the stacked parent. Deleting the rule makes the +55 test fail with zero delta (word-counts.json, count-falsifier.json). Against origin/main, the combined +110 contains the parent's separately accepted +55.
- AC-6 passes: the exact full discovery command exited 0, 892 tests, 6 skips (full-suite.log, suite-result.json). Both required ADR lint copies pass, including the dispatch's exact .claude path with docs/adr --since origin/main --require 0055: 52 records, 0 legacy. Removing required ADR 0055 from a copied folder exits 1 (adr-missing-falsifier.log). Consumer search found helper imports and tests, with no additional runtime output parser needing repair (delivery-callers.log).
- AC-8 passes: independent reading of all saved K target-count bullets and headings agrees that candidate runs 1, 5 and 6 label the disputed count, while runs 2, 3 and 4 do not; base labels none. semantic-read.json binds that manual judgment to answer hashes and excerpts. The unchanged grader still says P 6/6 and K 6/6, with base P 1/3 and K 3/3. Regrading validates raw answers, prompts, harness hashes and the exact candidate workflow; all original/corrected falsifiers reproduce. The title-only wrong-count control still false-passes, preserved in replay-audit.json. accepted_state.py verifies the ruling and filed follow-up, and rejects missing-follow-up and hidden-limit controls. It checks the record, not actual count accuracy.

## Prior findings re-judged

- F1 Deferred risk, settled for this stage by Captain amendment 3: the grader defect and K 3/6 are accepted limitations under AC-8, not a new success claim under the withdrawn AC-7. This run confirms rather than hides them. The four disposition evidence fields are retained in findings.json. It becomes material if a delivery summary claims count reliability or omits the limit; the follow-up owns future behavior.
- F2 Deferred risk, resolved for this stage by Captain amendment 2: number guards pass against the pinned PR #773 head. The diagnostic origin/main comparison still exits 1 for the parent's ADR 0054. That does not block this permitted parent-head validation, but FO must fetch and repeat against origin/main after #773 merges and before delivery. Neither the task's reservation nor the base ref was changed to conceal the diagnostic failure.

No new Material or Needs decision finding arose. The earlier rejection remains in history; this report judges the changed accepted criteria, not a repaired product.

## Implementation limits, sufficiency and necessity

The saved P answers all attribute the preview-path claim (6/6 candidate versus 1/3 base by the frozen grader). That supports the bounded attribution improvement; it is not a truth check or a measured daily-work effect. K remains an accepted known limit. The base did not meet both scenario bars; no evidence establishes that the README increase is unnecessary. The two reminder positions, written rule, observer boundary and ledger each map to a named criterion and falsifier; no unrelated product changes are present.

There were 22 stored attempts, 18 answered, and no new provider calls or agents in this validation. Re-summing raw usage reproduces 328245 input tokens including cache and 16519 output tokens for implementation-2/3; these are provider fields, not measured billing. Four prior no-answer attempts remain distinct. The one-model, six-candidate/three-base samples, combined README plus reminder in K and lack of daily First Officer observations remain limits. Safe-mode isolation rests on saved documented help and argv, without a file-open trace. The excluded Codex route remains untested; current exec help supplies no explicit global AGENTS.md isolation flag, which is a tested-route limitation, not proof that every route is impossible. No credentials were accessed.

An honestly attributed but incorrect report can still reach the Captain. The written rule and advisory reminders deliberately add no semantic hold, following the accepted design and ADR 0027. The accepted count limit does not become a claim of correct counts.

The eight doc_impact.py dispositions match the implementation list and were checked against candidate behavior (doc-dispositions.json). All added comments were read; the existing counter reports 0.2%, below 5%, with no provenance finding. No CI trigger changed; CI cost per PR was not measured. Seven dispatch records pass the active skill's checker; requirements trace to the accepted design and recorded amendments. No installed package or workflow was repaired.

## Captain acceptance script

Run the exact six-step acceptance.sh with /bin/bash --noprofile --norc. It declares the required checkout, state and installed package paths; creates the exact detached candidate; runs lint and both reminder fixtures; re-audits stored outputs and the accepted limitation; runs ADR, amendment-form and stacked-parent checks; and verifies cleanup. It ran unchanged, exit 0; acceptance.log is the complete observed output, and manifest.json pins its bytes.

The task declares no GUI surface. These observable commands substitute for a screen test. The script does not rerun models or the full suite, prove count truth or global-instruction file access, establish external review completeness, or authorize delivery. The post-parent trunk check remains FO-owned.

## Delivery boundary

No code was pushed, PR edited/commented/readied, review requested or merge performed. This is a validation recommendation. FO retains the gate, external reviews, publication and the post-parent trunk number check. State report commit/sync and disposable-checkout cleanup are recorded separately; they do not deliver code.
