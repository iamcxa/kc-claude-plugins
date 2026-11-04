# Independent validation of claims-name-their-source

Verdict: **REJECTED pending two Needs decision dispositions**, at product commit `f79711ca8d6325c1c14781342cf23855dd62b10a`. This report assesses the accepted Pilot scope. It grants no repair, gate approval, delivery, or new replay authority.

## Identity and command provenance

- Assigned code branch: `spacedock-ensign/claims-name-their-source`; its HEAD and clean status were verified before work. All product execution used the detached candidate under the assigned worktree's `.context/validation-777`.
- Fetched `origin/main`: `e1bee223c47a1cd534a665a47776b683375b34fc`. It was kept for the required checks.
- Actual PR #777 base and merged-in parent: `spacedock-ensign/fo-tries-what-it-asks-the-captain`, commit `128fe3e3fed70fa64ded8657f5a1b36933af3ced`. PR #773 was still open when queried; `sibling-pr.json` is the read-only receipt.
- `candidate-pr.json` confirms Draft/open PR #777 at the exact candidate and five successful hosted checks when queried. It establishes observed check state, not review completeness or merge permission.
- Commands, working directories, dates and exits are in `checks.json`; replay command is `python3 -B audit_replay.py <detached-candidate>`, and mutation/recount command is `python3 -B prove.py`. This validation ran on 2026-11-04 Asia/Taipei; machine UTC stamps are in the manifest.
- The loaded Codex validation skill resolves its package to `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`. The dispatch-named Claude ADR lint was also run exactly with `docs/adr --since origin/main --require 0055`; exit 0, 52 records and 0 legacy. `package-identity.json` shows those two ADR scripts are byte-identical.

## Criteria and falsifiers

`criteria.json` is the per-criterion verdict and evidence map. AC-3 was withdrawn into Captain amendment 1 and is not separately judged.

- **AC-1 passes:** both approved sentences and the startup loading ledger are present; repository lint reports 5891/5891. The +55 quote matches the ideation gate record. Removing only this task's budget step in a throwaway copy exits 1 and names the required +55 raise.
- **AC-2 passes:** existing fixtures exercise both `question` and `check` on success, holds and unreadable input, preserving exit codes 0/1/2. The source reminder occurs once and precedes the final ASK line. Removing only the emit in `check` fails its test; the `question` control remains green.
- **AC-4 passes at its stated static proof depth:** the new chat-only phrase is in the observer list; the committed-summary sentence is outside that exclusion. Rewording the workflow phrase in the copied fixture makes lint fail with the required chat-only mismatch. No new observer agent was started; this does not claim native observer compliance.
- **AC-5 passes:** the task-only comparison is against the pinned stacked parent: workflow 5836 to 5891, mod 48 to 48, question output 3 to 30 words and check 57 to 84, with unchanged successful exit codes. `pr_watch.py`, `design_surfaces.py` and the mod are byte-identical to that parent, covering idle/archive/ideation moments. An independent `wc -w` agrees on source-file counts. Deleting the rule in the count probe changes the delta from +55 to 0 and is detected. The `origin/main` workflow has 5781 words: the combined +110 includes the parent's separately accepted +55, not a larger rise by this task.
- **AC-6 passes:** the exact full discovery command exits 0, 892 tests and six skips (`full-suite.log`, `suite-result.json`). ADR lint passes; removing required ADR 0055 from a copied ADR folder exits 1. The suite's intentional diagnostic/error fixture output is retained; it did not produce a failing test. The parent forward merge had not been covered by implementation's older 891-test receipt; this run replaces that gap.
- **AC-7 is mechanically passing but insufficient for an independent all-green verdict:** unchanged grader P 6/6 and K 6/6; reference P 1/3 and K 3/3. Raw provider results, saved answer texts, prompt hashes and reconstructed frozen prompts agree for all 18 answered runs. Both harness manifests verify, and the candidate workflow hash equals this exact product commit. The four preregistered original/corrected falsifiers were rerun unchanged and matched. The additional title-only counterexample demonstrates the defect they missed.

## F1 Needs decision: the K grader cannot establish the target-count bar

Released user and normal workflow: First Officer writing the accepted validation summary from the supplied worker reports.

Observable harm: the unchanged grader counts an unattributed historical wrong-count statement as a pass, allowing an unsupported claim that the reporting fix met its five-of-six bar.

Affected value: `value-ac[AC-7]` retains the original K wording: the limit names three cells, names its actually run counting command, or labels the disputed count as the validator's report, not run.

Trigger evidence: independent reading of saved K candidate answers finds the target limit labelled only in runs 1, 5 and 6. Runs 2, 3 and 4 label other claims but leave that limit unlabelled. `semantic-read.json` records the extracted lines and source files; the fixed grader remains unchanged. A summary titled “Validation gate summary: read-adr reporting rule” with only the wrong two-cell statement passes; removing that title makes it fail (`replay-audit.json` controls).

The implementation report accurately disclosed this narrower 3/6 result and the base false-pass. Its mechanical 6/6 result is reproducible, but it is not sufficient evidence of the accepted target behavior. The validator does not silently replace the fixed rubric. FO must route the discrepancy for a recorded Captain disposition before a product repair, rubric change or further model runs; the 22/30 attempt count is not permission to spend the remaining attempts.

## F2 Needs decision: the assigned trunk number check and stacked delivery disagree

Released user and normal workflow: First Officer running the required reservation check before the candidate's merge ask.

Observable harm: `number_guards.py check --base origin/main --head f79711ca8...` exits 1, reporting that parent ADR 0054 is absent from this task's reservation. This cannot be reported as a green required check.

Affected boundary: `contract[kc-dev-flow-2/references/sd/workflow.md#number-guards]` requires the candidate check; this dispatch explicitly named `origin/main`.

Trigger evidence: `number-guards.log` contains the exact R4 failure. Parent task `fo-tries-what-it-asks-the-captain.md` reserves 0054, and PR #773's head is the parent of this candidate. Against that pinned parent, this task's number check passes (`number-guards-stacked.log`). No reservation or base was changed to conceal the trunk result.

FO must reconcile the assigned comparison with the stacked delivery order, or complete the parent through its own authority and recheck the resulting candidate. This is not a request for this validator to change the sibling.

## Implementation limits, sufficiency and necessity

- **Claude-only boundary:** the Captain amendment explicitly drops the Codex half. Current `codex exec --help` still exposes no explicit global AGENTS.md isolation flag; `--ignore-user-config` describes config.toml, not instructions. This validates the reported tested-route limit, not a universal impossibility claim.
- **Instruction isolation:** stored Claude help documents `--safe-mode` disabling CLAUDE.md and user customization while preserving auth and built-in plugins. All answered metadata records the Opus route and the safe-mode argv. There is no file-open trace, so “global instructions were not loaded” remains supported by the documented mode, not independently observed file access. No credentials were read or copied by this validation.
- **Attempts and tokens:** 22 stored attempts across implementation 1–3, 18 answered, no new provider run here. Re-summing raw result usage gives 328245 input tokens including cache and 16519 output tokens for implementation 2–3. These are provider usage fields, not a billing measurement. The four earlier no-answer attempts remain separate.
- **Replay strength:** six candidate samples per scenario on one model; base remains three per scenario. K combines the README and reminder, so their individual effects are not separated. The base's P 1/3 cannot reach 5/6 even with three hypothetical later passes, so no base-saturation removal result is established. P supports improved attribution; K's target-count benefit is unproven. Neither proves behavior in Kent's daily First Officer.
- **Written-rule boundary:** a correctly attributed but false report may still reach the Captain, and the scripts add no semantic source hold. This is the accepted design following ADR 0027, not a new defect. Sources improve checkability, not truth.
- **Documents and comments:** `doc_impact.py origin/main <head>` names eight documents; every implementation disposition was checked and retained in `doc-dispositions.json`. No unique content is removed by this task. All added task comments/docstrings were read; the installed comment counter reports 0.2% against its 5% maximum for the combined range, exit 0. No CI trigger changed; CI cost per PR was not measured.
- **Consumers:** existing delivery callers and tests were searched; reminder-aware assertions retain the final ASK semantics and record contents. `delivery-callers.log` and the passing suite cover the source inspection and regression evidence. This task adds no runtime parser.
- **Installed checker drift:** active Codex dispatch checking passes all five records. A diagnostic run of the dispatch-named Claude copy rejects their valid final-reply completion shape; its bytes differ from the active skill's copy. This is the known installed grammar drift, not evidence that five handoffs are missing. The required skill-routed check passes; no source or dispatch record was repaired.
- **Delivery:** hosted check state was read, but no RoboRev or other review was requested, no PR was edited/commented/readied, and no code was pushed or merged. FO retains exact-head review and gate/delivery duties. Product and frontmatter remain unchanged.

## Minimal acceptance script

Run `/bin/bash --noprofile --norc acceptance.sh` from this evidence folder, or use its absolute path. It has six exact steps with expected output, names the required local checkout/package/state paths, creates an exact detached candidate and removes it. The recorded fresh-shell run exited 0; complete observed output is `acceptance.log`. An initial sandbox attempt exited before checkout because shared Git metadata was not writable; `acceptance-sandbox-first.log` preserves it, and the unchanged script succeeded with authorized filesystem access.

The script demonstrates local outputs and both known holds; successful reproduction is **not** a passed delivery verdict. It does not rerun models, repair the grader, prove instruction file isolation, execute a live Captain/FO workflow, establish review completeness, or approve merge. No GUI surface is owed: the task records `Surfaces: none` and `Visible change: none`.

