# Independent validation of PR #809

Verdict: **REJECTED** at candidate `b36fbeeec3a6699c0a82a021dc4ee0142410f6c8`, base `139feeaee7ce037a0c6535568cd6bd103155cbae`. The deterministic audit behavior passed. AC-6 did not pass the fresh native observer run: its immutable report claims the audit exited 0, although that number was the presentation pipeline's last command, not the audit. The observer confirmed this without revising its report. No product bytes were changed.

## Evidence and acceptance criteria

- **AC-1 PASS.** `replay-live-network.log` is a new real GitHub read using the exported candidate and the exact requested archived window, exit **1**. It shows carried 54 of 82; no-ask PRs 704, 762, 774, 776, 778, 784, 785, 789; release 707, 717, 723, 731, 739, 746, 752, 760, 768; sync 715, 718, 725, 733, 741, 747, 753, 761, 781; learning 726, 782. PR 785 has head 0c38dd60b562. `snapshot/` independently reruns all set assertions and PR 727 as carried. `mutations/release-removed-snapshot-replay.log` makes PR 707 a missing record when its producer classifier is removed.
- **AC-2 PASS.** The PR 7 A/B fixture passed, and `mutations/pr-number-only.log` rejects matching solely by PR number. `snapshot/727-wrong-head.log` separately changes PR 727's head and gets a head-difference finding, exit 1.
- **AC-3 PASS.** Producer-prefix, learning-length, sync-title, renamed-release and matching recorded-release cases passed. `mutations/kind-before-record.log` rejects classifying the recorded release before its matching record.
- **AC-4 PASS.** The 17-test baseline exercises remote-only refs, fetch warning/local fallback, ref SHA/time, exact window bounds, post-TO committed records, uncommitted-record exclusion, gh failures, 1000 results, malformed input, absent origin and absent refs. `mutations/records-at-to.log` fails when current ref-tip records are replaced with TO records. The first live attempt `replay-live.log` exited 2 on sandbox network failure; the unchanged escalated command succeeded in collecting evidence and exited 1 for its eight findings. This is environment evidence, not a product defect.
- **AC-5 PASS.** A committed sibling observer report collapses PR 9; deleting it restores the finding. Uncommitted and own reports do not suppress it. `mutations/collapse-removed.log` rejects removing this behavior.
- **AC-6 FAILED.** Fresh Sonnet 5.5 observers were given only STATE, TASK, RULES, FROM/TO and the selected package. Candidate agent `fbe7c937-5309-473b-be32-776cba046bd0` ran the archive export; base agent `3e58869e-4f45-437a-a99a-3428ed99482d` ran installed 0.35.0. The candidate correctly emits carried, named kinds and all eight can't-tell identifiers with one missing-record caveat under Coverage; the base emits none of the new merge audit lines. However, `observer-candidate.md` contains the false exit status and abbreviated line forms. `observer-exit-clarification.md` preserves its admission that `merge_audit.py ... | cut ...; echo "$?"` reported cut's status. No corrected report or outcome-selected rerun replaced this evidence.
- **AC-7 PASS within the accepted simulation boundary.** `candidate-files.json` verifies exactly four changed product paths and hashes each exported file against the candidate. Lint passes with the original 5933-word workflow ceiling, unchanged workflow and unchanged lint script. `words/` reruns the pinned original 54-window corpus; `independent-words.py` independently reconstructs every rendered line from candidate audit outputs and matches the existing recount: median 60, maximum 320, uncollapsed maximum 422. Its extra-one-word falsifier produces median 61 and maximum 321 and is rejected. This is chronological simulated verbatim quoting, not a guarantee for arbitrary native model prose.

## Review-finding disposition

### F1 — Material: native observer attributes pipeline success to the audit

1. Released user and normal workflow: an adopter's FO runs the Sonnet observer on an archived task and relays the report unchanged, as the accepted observer journey specifies.
2. Observable harm: the report records `(merge_audit, exit 0)` for an audit that directly returns 1 with eight findings. The saved report therefore contains false execution evidence; the clarification confirms that the audit exit was never captured. This finding does **not** claim the missing-record PRs were unauthorized or that the eight can't-tell rows disappeared.
3. Affected value/boundary: `value-ac[AC-6]` requires the observer's actual audit report in the specified evidence form; `contract[kc-dev-flow-2/skills/observer/SKILL.md#prove-each-finding]` requires reported evidence to be verifiable. The report's exit claim fails that boundary.
4. Trigger evidence: `observer-candidate.md`, `observer-exit-clarification.md`, the native activity transcript, and the direct live replay exit 1. The native command piped through cut without pipefail and captured the final pipeline status.
Disposition requested: FO handles this through Review-finding disposition. Preserve the script's status before rendering output and repeat native acceptance under whatever repair/revalidation authorization FO records; validation has made no product fix.

### F2 — Polish: native report abbreviates the specified line forms

The same ordinary observer run omits `evidence:` and the gh source on all three named-kind rows, and omits per-row rule/evidence fields on the eight missing-record rows. All merge identifiers and 12-hex heads survive, the shared rule is quoted above, and no classification or repeat token is lost; no additional supported-workflow harm is established. This is an observed formatting deviation from AC-6, not a separate claim of unauthorized merges. It would become Material if evidence provenance were lost for an actual finding or future repeat collapse failed.

## Checks and limits

- All **27 local package commands** succeeded: **1199 unittest cases, 11 skips**. `suite-summary.json` and `suite/` contain commands and outputs; the skipped cases are not promoted to passed coverage.
- `checks.json`: candidate lint, installed-package ADR lint, number guards, design check, comment ratio, document-impact check and diff check all exited 0. ADR lint checked 62 files, 0 legacy. The exact command was `python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 139feeaee7ce037a0c6535568cd6bd103155cbae`, run from the export with read-only GIT_DIR/GIT_WORK_TREE bindings. Comment ratio was 2/431, 0.5%, below 5%; the added code comments are interpreter shebangs.
- `doc-impact.json` lists `kc-dev-flow-2/README.md`: **unaffected**, because its instruction to run each named CI command remains true after adding the new test step. No changed product diagram or graphical screen exists (`Surfaces: none`).
- `dispatch-records-final.log`: all four dispatch records, including FO's state-push clarification, are complete.
- The CI change adds one standard-library test command to the existing unit-test job. Existing package/workflow path filters, main-only push trigger, permissions, runner and setup are unchanged. This is the narrow existing trigger that also catches changes to audit producers/consumers elsewhere in the package. **Hosted CI cost per PR was not measured.** Local runtime is not a hosted cost estimate.
- Local integration used Spacedock CLI 0.27.2 with installed plugin files 0.27.3; it does not establish the hosted pinned installation. **roborev not run: FO owns the local daemon review.** The PR body says FO reviewed it, but this validation does not promote that statement into independently reproduced review evidence.
- Matching asks at current ref tips do not establish that an approval existed at merge time, nor that its question named the merge. State in another repository and approvals in chat remain outside the audit. Named kinds rely on the approved branch/title conventions; renamed releases or unconventional sync titles become gaps.
- The word-count corpus remains pinned, while record inputs intentionally use current ref tips. All read refs and timestamps are in the replay output. The independent renderer proves the accepted simulation, not model-output length or fidelity; the native candidate report is 819 whitespace-delimited words, and the base also exceeds the pre-existing 500-word report instruction. Neither is represented as a passing native word-limit check.
- Scope sufficiency: the CLI surfaces the intended gaps with safe can't-tell wording, but the report handoff has not passed. Minimal necessity: audit helper, tests, explicit CI test step and observer instructions each map directly to this journey; removing each loses classification, falsifiability, CI execution or observer invocation. No extra product files or version changes were introduced.

## Captain acceptance script

Five steps, no graphical surface. Prerequisites and expected observations are comments in `acceptance.sh`. It creates a fresh /tmp archive and uses the declared local checkout, state corpus and package; no product or state writes, network access, deployment or merge are performed by the script.

Run exactly:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/observer-lists-unasked-merges/validation/acceptance.sh
```

The validator ran the same script bytes in a fresh bash shell; `acceptance.log` holds the observed output and exit 0. It prints the four changed paths, all saved-window assertions, 17 baseline tests plus five rejected mutations, the 54-window word counts, 62 ADR records, and `PASS: deterministic checks only; native observer report remains separately judged.` This pass does not close AC-6, prove hosted CI/RoboRev, or grant merge authority.

## Ownership

Product checkout remains on `spacedock-ensign/observer-lists-unasked-merges` at the exact candidate, clean. PR #809 was verified open and Draft at that head. State report/evidence commits use the mandated Spacedock helper; FO's `validation-1-message-1.md` explicitly permits its state-only push. Unrelated state writers were preserved. FO retains findings disposition, gate, revalidation and delivery decisions.

