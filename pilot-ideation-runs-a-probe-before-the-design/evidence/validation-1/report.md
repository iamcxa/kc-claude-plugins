# Independent validation of PR #864

Verdict: **REJECTED** at `f0e00d30ce00542b2895f13173bd41075cc8bfd4`, base `88f86f2749dadb6f4ef0cf9aa089c1827096865b`. No product repair was made. The candidate implements the seven approved decisions, but the accepted evidence clause for AC-3 needs a Captain amendment, and the cold worker run did not record a complete command/exit/output ledger for every criterion.

Start: 2026-11-13 15:35:25 Asia/Taipei, first recorded `clock.curr_time` reading (UTC +08:00). This report concerns independent validation, not approval, merge, release or adoption.

## Findings and workflow disposition

- **F1 — Needs decision: the approved AC-3 evidence command is false-red.** Normal user/workflow: the Captain or validator runs the approved acceptance command on the exact candidate. Observable harm: a conforming candidate cannot satisfy its recorded exit-0 evidence clause. Boundary: `value-ac[AC-3]` requires no duplicate ban and no repeat finding, plus an exit-0 command. Trigger: `AC-3.log` records lint exit 0, zero ban copies/exception entries, and “repeat findings: 1”; that one line is lint's success message. `AC-3-corrected.log` records exit 0 with `^FAIL:.*repeats`, and reintroducing the ban is rejected in `mutation-AC-3-duplicate-ban.log`. The criterion statement holds. Recommend a Captain amendment to its evidence clause, preserving the original block and assigning a fresh criterion id under the existing amendment procedure; the validator cannot silently replace approved text.
- **F2 — Material: the cold worker omits the proof ledger for its third criterion.** Normal user/workflow: a fresh Pilot ideation worker reads the candidate's native built dispatch, without FO-authored probe instructions. Observable harm: the design reader cannot rerun or check the claimed third proof from its saved record. Boundary: `value-ac[AC-8]` requires a probe plus command, exit and output path beside every criterion. Trigger: `live/task.md:156` calls worker AC-3 passed but offers only a generic `git merge-base --is-ancestor` and byte-comparison hint; `live/source-identity.json` contains facts/booleans, no command or exit. The first two criteria have complete JSON ledgers; the third does not (`live/criterion-coverage.json`). Return through the workflow's finding disposition; do not fill in the test subject's missing record after observing it.

No newly demonstrated product harm is attributed to the acknowledged prose round cap, per-round timing gap or deferred release cleanup. Those are the Captain-approved limits, not new repair findings.

## Candidate and isolation

The assigned product worktree was clean on the required branch and exact head. All candidate execution used an export; read-only diffs used the pinned refs. `replay_dispatch.py` internally creates worktrees, so its repository arguments were independent fixture repositories under the assigned scratch directory. It never created or removed a worktree in the product repository's shared metadata.

The native replay tool, its exported package and generated show-stage-def command were used unchanged. The historical task's hand-written `Trial` paragraph also granted probe permission, beyond the stripped checklist/scope inputs. I removed that paragraph in the isolated task before the sole model run, retaining `live-seed-adjustment.diff`. This isolates candidate text as the probe instruction source. It also changes Scope relative to the frozen historical backlog gate, so the subject's final design-surfaces refusal is a **fixture consequence**, not a candidate regression or an “existing” product finding.

Private adopter repositories inspected: 0. No private adopter names, logs or personal author identities are retained in this evidence pack. Full source/state fixture repositories were not archived.

## Criteria and falsifiers

- **AC-1 passes.** Both named historical dispatches carry permission, bounds, proof-run, unavailable-proof and round wording; each base arm carries only the ban. `AC-1.log` and `AC-1/dispatch-content.json`. Substituting base for the candidate exits 1 (`mutation-AC-1-base-as-candidate.log`). The original accepted command was rerun unchanged, with only fixture repository and temporary-directory locations substituted.
- **AC-2 passes.** Derived POC workflow equals base (`AC-2.log`); an outside-ideation change yields DIFFER/exit 1 (`mutation-AC-2-outside-ideation.log`).
- **AC-3 statement passes; original evidence fails.** See F1. Original and corrected outputs are retained; copied-ban mutation exits 1.
- **AC-4 passes.** Lint reports 6099/6099 with the approved +66 step (`AC-4.log`). The quoted words and bound question match the task's ideation gate and briefing; loaded moment names FO startup/resume and Pilot dispatch. Removing the raise exits 1 (`mutation-AC-4-remove-raise.log`).
- **AC-5 passes.** Startup 6033 -> 6099 (+66); worker stage +66, worker skill reading +135, implementation profile +15. The trial scope/checklist has zero hand-written probe lines. Full count source: `AC-5/words-by-moment.json`, `AC-5.log`. A 6100-word mutation exits 1 (`mutation-AC-5-word-6100.log`).
- **AC-6 passes.** Native dispatch contract suite exits 0, covering its declared route/host and negative controls (`AC-6/test_sd_dispatch.log`); explicitly removing the Team clause fails the suite's own assertion (`mutation-AC-6-lost-team.log`). The 47 lint tests pass (`test-lint.log`).
- **AC-7 passes.** The archived task shows ideation dispatches 2, repeats 1 and stage start/end (`AC-7-corrected-fixture/timeline.txt`). A real one-dispatch task yields 1/0 and fails the required 2/1 observation (`mutation-AC-7-one-round.log`). The first attempt incorrectly supplied a bare state fixture; that setup error is retained in `AC-7.log`. Repeating the same accepted command with a checked-out state fixture passes; assertions and product bytes were unchanged.
- **AC-8 fails as a whole.** The probe-before-design portion was observed, but F2 prevents the every-criterion ledger claim. Details below.
- **AC-9 remains unverified after release**, as accepted at design. The current task's old probe ref is absent (`cleanup-observation.json`); implementation's earlier deletion log was read. Neither proves a released worker deletes its probe after committing a future candidate. No post-release run or post-release falsifier is claimed.

## Cold worker observation

One history-free collaboration worker, inherited model **gpt-6-astra**, was a **test subject, not a second validator**. It read the built ideation dispatch and authoritative candidate skill files. No model rerun or corrective follow-up was sent.

It created `poc/pr-watch-tasks-foreign-worktree-replay` at base `88f86f27`, committed a runnable probe as `318fc7caf416a88a000c7e16f2155b547a7ceb81`, exercised the real CLI with a refusing provider shim, removed the probe worktree and retained the branch. The original branch name already existed in the cloned fixture, so the suffix was an isolation accommodation. The selected task's repair already existed; the worker correctly recommended returning the overturned premise, rather than a duplicate product patch.

At 2026-11-13 15:46:58 Asia/Taipei, I independently observed the committed probe and successful command evidence while the task still had no Design heading (`live-midrun-observation.json`). The subsequent report commit is recorded in `live/commits.json`. Both absent-worktree and no-worktree-field cases have exact argv, exit 0 and saved stdout. Provider calls, task mutation and watch-state creation are checked by the probe. The third provenance criterion lacks the ledger fields described in F2.

I reran the saved absent-worktree probe independently: unchanged candidate exits 0; restoring an actionable `next:` output exits 1 (`AC-8-independent-results.json`, `AC-8-positive/`, `AC-8-negative/`). My first attempt omitted the fixture's required committed inputs and returned 2; those setup errors are explicitly retained. The corrected rerun uses the subject's actual committed fixture, changes no expected result, and detects the known bad output.

Limits: one worker/model and one already-fixed task; not cross-model reliability, general compliance, a completed design-gate pass, or proof of better delivery speed/quality. The fixture intentionally prevents external/adopter/provider work. It does not exercise the third-dispatch hold or AC-9.

## Approved decisions and amendment

- **D1:** Expected unless the design explains why not — present in the workflow; the cold subject actually built a probe.
- **D2:** Local branch, never pushed/deployed, no credential/shared environment — candidate text matches. This replay remained in independent local fixtures, with provider calls refused.
- **D3:** Probe line records branch/base/last commit and hypotheses/results; ideation removes worktree/retains branch, implementation reads/deletes after committing — both profile texts match. Ideation half observed; released implementation half deferred under AC-9.
- **D4:** One ideation dispatch per round; FO holds a third, including revises — text matches the approved prose cap. Timeline counts/time remain unchanged. No new grammar or runtime enforcement was silently added.
- **D5:** Approved +66 words, exact Captain quote/bound question and reading moment — verified against the gate record; deletion mutation fails.
- **D6:** ADR 0084 supersedes ADR 0005's write-ban/throwaway-worktree rejection only for Pilot — verified. Prod and amendment/design-gate authority stay in force.
- **D7:** Pilot points to the first POC implementation paragraph and keeps widening in Pilot — verified; POC files and derived workflow are unchanged.
- **Captain amendment 1:** The hypothesis/check/widen direction is expressed through the POC pointer; the later approved two-step decision leaves machine-enforced ideation budgets and per-round timing to the follow-up. The implementation stays inside that ruling.

## Required checks and document judgment

Installed package command `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/adr_lint.py docs/adr --since 88f86f2749dadb6f4ef0cf9aa089c1827096865b --require 0084` exits **0**, checking 77 ADR files (`adr-lint-corrected-fixture.log`). It ran against exported candidate bytes with an independent Git index. The initial empty bare-fixture index made every ADR look untracked and returned 1; `adr-lint.log` retains that diagnostic. Populating the fixture index from the same pinned candidate removed the setup defect; no ADR or expectation changed.

Number guards, design surfaces for the real task, dispatch records and comment ratio all exit 0 (`other-results.json` and corresponding logs). Comment ratio is 1 required ADR pointer / 4 added code lines = 25%; the configured maximum does not apply below 20 added code lines (`comment-ratio.log`). The added comment is an ADR pointer, not narrated code.

`doc-impact.log` lists 11 documents. I independently verified the implementation's dispositions: ADR 0084 updated; ADRs 0020, 0037, 0049, 0052 and 0080 retain valid budget/model/permission/timeline claims; both adopted workflow READMEs await their separately authorized post-release sync and POC derivation is unchanged; package README entry/maintenance commands, maintain-flow skill and historical learning remain accurate. ADR 0005 was additionally read for the explicitly limited supersession.

Goal sufficiency: native dispatch carries the rule, POC stays unchanged and the cold worker builds before writing its design, but F2 leaves the all-criteria proof outcome insufficient. Minimal necessity: the six changed files map to the admitted permission, removal of its contradictory duplicate/exception, bounded POC pointer, lifecycle cleanup duty, quoted budget or decision record; the controls reject removing the supported rule/budget, restoring the duplicate or changing POC. No unrelated product surface or CI trigger changed.

Hosted PR observation: OPEN, Draft, at the exact candidate, with six successful checks and one skipped deployment (`pr-state.json`); this is not a required-check gate or delivery claim. CI cost per PR was not measured. RoboRev, review disposition, merge, release and adoption remain FO/Captain-owned.

## Commands rerun

Exact environment/argv records are in `check-results.json`, `other-results.json`, `extra-falsifier-results.json`, `mutation-results.json` and `AC-8-independent-results.json`.

- `bash evidence/ideation-1/bin/accept.sh AC-1..AC-7 <output>`, each AC separately; the original AC-3 failure retained.
- `bash evidence/implementation-1/bin/accept.sh AC-3 <output>`, corrected failure-only pattern.
- `python3 -B kc-dev-flow-2/scripts/test_lint_skills.py`.
- `python3 <installed-package>/scripts/adr_lint.py docs/adr --since <pinned-base> --require 0084`.
- `python3 <installed-package>/scripts/number_guards.py check --repo <export> --base <pinned-base> --head <pinned-head> --workflow-dir <workflow> --task <task>`.
- `python3 <installed-package>/scripts/comment_ratio.py <pinned-base> <pinned-head> --workflow-dir <workflow>`.
- `python3 <installed-package>/scripts/dispatch_records.py <task-folder>`.
- `python3 <installed-package>/scripts/design_surfaces.py check <task-file>`.
- `python3 <installed-package>/scripts/doc_impact.py <pinned-base> <pinned-head> --repo <export>`.
- `python3 -B <saved-probe>/ideation-probe.py <package> <committed-fixture> <evidence> absent`, unchanged and mutated package arms.
- `gh pr view 864 --repo iamcxa/kc-claude-plugins --json number,state,isDraft,headRefOid,statusCheckRollup`.

## Captain acceptance command

Requires git, Bash, Python 3/PyYAML and network access to the public repository. This is the sole runnable acceptance command; it creates its own scratch, downloads the exact head/base, and does not need the product worktree or any scratch retained from this session.

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/validation-1/captain-accept.sh
```

Its four steps and expected observations:
- Fetch exact public candidate: STEP 1 PASS with full head.
- Run package lint, 47 regression tests and ADR check: STEP 2 PASS; tests OK; 77 ADR files.
- Compare POC derivation and startup count: STEP 3 PASS; equal POC; 6033 -> 6099 (+66).
- Expose original AC-3 false match and verify statement: STEP 4 PASS; original pattern 1, corrected failure pattern 0.

Executed exactly in a fresh Bash shell: exit 0 in 29 seconds (`captain-accept.log`, `captain-accept-result.json`). The sandbox's first network refusal is retained separately; the identical command succeeded with authorized network access. No UI exists. This script checks text/regressions and the known evidence defect; it does not repeat a model run, demonstrate the missing worker ledger, enforce a third-dispatch hold, run post-release cleanup or approve delivery.

## Handoff

FO disposition is required for F2 and Captain amendment authority for F1. AC-9 remains the expressly accepted release obligation. Product head/branch are unchanged; this report makes no gate, publication or delivery decision.

