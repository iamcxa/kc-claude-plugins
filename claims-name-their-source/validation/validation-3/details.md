# Validation cycle 3: source claims after the parent merged

Candidate: `69f4988612d17c5524887f99c872a0ef384d05c9` (PR #777). Base: fetched `origin/main` at `2bda2e98304261d46b0ae7205a29ddc9038d2b4d`. Profile: Pilot. Commands and direct reads performed 2026-11-04 Asia/Taipei. The detached checkout is recorded in identity.json; no candidate bytes were repaired.

Verdict: **PASSED** within Captain amendments 2 and 3; no new Material or Needs decision finding.

## Authority and scope

Captain amendment 2 now requires the trunk number check because parent PR #773 is merged. `gh pr view 773 --repo iamcxa/kc-claude-plugins --json number,state,headRefOid,baseRefName,isDraft,url,mergeCommit,mergedAt` confirmed the merge; the receipt is pr-773.json. `gh pr view 777` confirmed the assigned head and main target (pr-777.json). GitHub snapshots are read-only evidence, not review or delivery approval.

Amendment 3 withdraws AC-7 and accepts AC-8: ship the existing source rule, disclose the count scenario's 3-of-6 limit, and file the numeric-source follow-up. The follow-up is committed at the revision in followup-commit.log. This pass applies that later ruling without rewriting the earlier rejected report. ADR 0055 now quotes the recorded questions and answers verbatim and describes the narrowed evidence. The historical design's earlier thresholds are withdrawn, not silently claimed met.

## Checks and falsifiers

- AC-1: `python3 -B kc-dev-flow-2/scripts/lint-skills.py` exits 0 at 5891/5891 words. The budget's quoted question matches the ideation ruling, with `loaded="startup"`. Removing only its +55 entry produces the named raise-of-55 failure (mutation-budget.log).
- AC-2: both focused gate tests exercise pass, hold and unreadable-input exits 0/1/2 and one reminder, before the final ASK on success. Removing only `check`'s emission fails that test; the `question` control remains green (mutation-check.log and mutation-question-control.log). No source-pattern hold was added.
- AC-4: observer chat list and workflow phrase agree; changing the phrase produces the chat-only-rule lint failure (mutation-chat.log). Observer enforcement remains a reader contract for committed summaries; these checks do not prove a model obeys it.
- AC-5: independent `str.split()` plus `wc -w` recount uses the current main blobs: workflow 5836 to 5891, mod 48 to 48; question pass output 3 to 30; check pass output 57 to 84. The two gate outputs each add 27 words. Idle/archive/ideation source files are byte-identical to main. Deleting the source rule changes the measured +55 to zero (word-counts.json, count-falsifier.json).
- AC-6: full discovery exits 0: 906 tests, 6 skips, no failures/errors (suite-result.json and full-suite.log). Both active Codex-package and dispatch-named Claude-package ADR lint runs use `--since origin/main --require 0055`, exit 0, 53 records/0 legacy. Deleting reserved ADR 0055 in a copied folder exits 1 (adr-missing-falsifier.log).
- AC-8: imported the unchanged grader only, regraded every retained answer, checked prompt/answer/harness hashes and compared candidate workflow bytes. Independently read all target-count answers: candidate 1/5/6 attribute the disputed limit (3/6), base 0/3. The old grader still returns K 6/6 against base 3/3, and a title-only wrong-count control false-passes. P is 6/6 against base 1/3. There were no new provider calls; retained attempts remain 22/30 (audit_replay.py, replay-audit.json, semantic-read.json).
- Missing follow-up and hidden-limit controls reject in accepted_state.py. retained_record.py also rejects changing the Captain's quoted answer, hiding the ADR's limit, or omitting its follow-up. These are bounded record checks, not an alternative behavioral grader.

`checks.json` and `extra-checks.json` retain literal argv, cwd, date and exit code. Required number guards now exit 0 against main (number-guards-main.log, number-guards-trunk.log); the earlier stacked-parent reservation hold is resolved. Design form check passes. Dispatch check reports nine complete records and two advisory absent-Symptom lines; exit is 0, with no missing/incomplete dispatch finding. Every implementation dispatch was read against accepted criteria/rulings; the latest follow-up requires only the ADR proof update and rechecks.

All eight affected-document dispositions were reread and retained (doc-dispositions.json). Consumer search found no non-test parser of question/check stdout; existing runtime consumers import unchanged helpers/regexes. Added code comments: none; the added docstring states the observable entry behavior. comment_ratio.py measured 57 code lines and 0 comment lines, 0.0%, within 5% (comment-ratio.log). `git diff --check origin/main 69f4988612d17c5524887f99c872a0ef384d05c9` exits 0. No CI trigger changed; CI cost per PR was not measured.

## Goal sufficiency and necessity

The accepted bounded goal works: the source instruction is in the startup workflow, both write-time commands print its reminder, and the observer's chat exclusion stays explicit. The preview-claim saved baseline/candidate contrast supports the text's retained value; removing the rule, ledger, output or observer phrase is detected by the named controls. Count correction and the separate effects of README/reminder in K are not demonstrated; the Captain accepted that limit and ordered its follow-up. No extra hold, service, background loop or adopter edit was introduced.

## Acceptance script and environment limits

acceptance.sh has six exact steps with expected observations and declared local paths. Unchanged bytes ran under `/bin/bash --noprofile --norc`; exit 0 and full output are in acceptance-rerun.log, with the script hash in acceptance-result.json. An initial attempt could not create Git's worktree metadata under the filesystem sandbox (exit 128); the approved retry ran the same script and removed its own checkout. This is environment evidence, not a product failure. Read-only GitHub reads were likewise retried with network permission after sandbox connection failures.

The script covers local output, required post-parent guards and retained proof records. It creates no provider runs and proves neither daily First Officer behavior nor external reviews, adoption, merge or release. `claude --help` still documents safe-mode customization exclusion; no file-open trace was taken. `codex exec --help` supplies no supported skip-global-AGENTS switch; the Codex half remains outside the ruled replay. One model, small samples, normal HOME with documented safe-mode, combined README/reminder in K and honestly attributed but false reports remain explicit limits.

## Disposition and handoff

F1 remains the accepted Deferred risk under value-ac[AC-8], with four evidence fields and its materiality trigger in findings.json: reliable-count-correction claims or hidden limits would reopen it. The prior number-check finding is resolved by the fetched-main check. No new Material or Needs decision finding was identified.

Only this report and evidence are handed back. No code push, PR change, comment, review request, ready action, model worker or merge was performed. The dispatch's explicit no-push instruction overrides its generic state-sync paragraph: use a path-scoped local state commit and leave synchronization to the First Officer. The state-syncing helper is not invoked because its documented flow includes sync and no local-only flag is advertised; this exception does not change candidate validation.
