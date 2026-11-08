# Independent validation of PR #806

Candidate: `f429f0fac40511c6480fd92e2cccd4c0e94b2454`.
Base: `139feeaee7ce037a0c6535568cd6bd103155cbae` (`main` in the saved PR receipt).
Verdict: **PASSED** for the approved Pilot scope, AC-1 through AC-5. No new Material or Needs decision finding; the three known limits retain the classifications below. This is not gate approval, publication, merge, or release evidence.

## Captain acceptance: five steps in one fresh shell

There is no changed screen. The observable result is the linter's exit and diagnostic, plus controlled failures when the fix or its boundaries are broken.
Dependencies: Python 3.11+, bash, git, tar, `shasum`, the assigned repository with the named candidate/base/history commits, the installed dev2 0.35.0 package, and Spacedock. The validation host resolves `spacedock` to `/Users/kent/.local/bin/spacedock` (CLI 0.27.2); the native test uses the explicitly named plugin 0.27.3. The script declares the exact checkout/package/state paths. It uses no secrets or external network, and does not configure or mutate the product repository.

Run this exact command; all five steps and their actual commands are in the script:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/adr-lint-tells-supersession-assertion-from-pointer/validation/acceptance.sh
```

1. Export the exact candidate into a fresh `/tmp` directory; verify all four changed files equal the candidate. Expect `Step 1: exported f429f0fac40511c6480fd92e2cccd4c0e94b2454`.
2. Run the ADR suite, document checks, native dispatch integration, and copy parity. Expect exits 0; detailed logs contain 25 and 9 passing tests plus native integration PASS lines.
3. Run full and changed-record lint on the unsplit real citation; compare the installed checker with base. Expect candidate exits 0 and 62 records checked; installed exit 1 with `points at ADR 0047, Superseded by 0050`. Exit 1 is an expected observation, not a falsely green installed check.
4. Re-run the implementation's existing archive-only mutation/history proof and seven small limit probes. Expect 11 proof outcomes and seven limit observations to match; negative controls actually exit 1.
5. Re-run skill lint, surface, number, comment, document-impact, dispatch-record and whitespace checks; recheck the product remains clean at the exact head. Expect exits 0 and `PASS: all expected outcomes; evidence: /tmp/adr806-acceptance.XXXXXX/results`.

`acceptance.log` is the observed output from the exact command above, run in a fresh bash shell. `results/` preserves its raw logs and structured results. The first rehearsal used identical script bytes from `/tmp`; `initial-acceptance.log` is retained separately. The final-path replay verifies the delivered script's relative helper lookup.

The script writes only throwaway exports and evidence under `/tmp`; tests create and remove their own synthetic Git repositories there. Read-only Git metadata is provided only to commands requiring history, never to the test suites. It neither creates nor removes a worktree of this repository. This is local evidence, with synthetic native-dispatch fixtures, not a real model/host dispatch, human gate, delivery hook, remote CI, RoboRev, merge or installed-package upgrade.

## Evidence and falsifiers

- **AC-1:** candidate `test_asserting_the_recorded_supersession_is_not_a_stale_pointer` passes. The candidate test against base checker and the removed-exception mutation each fail with the 0002/0003 diagnostic (`results/proof/base-fails-assertion.log`, `removed-exception-fails.log`). The escaped-newline assertion also catches an incorrect leading word boundary.
- **AC-2:** authority on a separate line remains an error; the existing both-pointer and full-path/number-only tests remain byte-unchanged. File-wide successor forgiveness makes the existing both-pointer test fail (`file-wide-successor-fails.log`). `results/limits.json` independently confirms that an assertion elsewhere does not forgive a stale authority line.
- **AC-3:** wrong successors 0004 and 00030 remain errors, and the assertion cannot supply the successor's own pointer. Accept-any-successor and fabricated-pointer mutations each make the relevant test fail (`wrong-successor-fails.log`, `invented-successor-pointer-fails.log`).
- **AC-4:** the candidate retains the natural `docs/adr/0047-...` literal; full lint and `--since 139feeaee7ce037a0c6535568cd6bd103155cbae --require 0064` both exit 0. The `ae7750375` archive with the one-line unsplit exits 1 under its old checker, then 0 when only the checker is replaced (`historical-unsplit-fails.log`, `historical-candidate-passes.log`).
- **AC-5:** the 25-test, 9-test and native dispatch suites plus copy-sync check pass. One-copy drift makes parity exit 1, then restoration passes. Source and dev2 copy share SHA-256 `7313e02238830471138d23508c1106bf4ff15ab8b166c060ec1d6e5a160e719f`.

## Installed-checker disposition

The exact required installed command was executed, with read-only metadata connecting the archive to the named base:

```bash
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 139feeaee7ce037a0c6535568cd6bd103155cbae
```

Observed exit **1**, with only the known ADR 0047/0050 false-positive diagnostic (`results/installed-since.log`). Installed SHA-256 `203f097c37799e051718ca339035aad64f240b8134c20afb3dfd66cc381b25f4` equals the base checker byte-for-byte. The unchanged candidate checker passes the same real tree with `--require 0064`. Therefore the FO disposition in `../dispatch/implementation-1-message-1.md` is justified: **SKIPPED as an acceptance requirement**, while its execution/failure remains recorded. No installed file was changed.

## Review-finding disposition and limits

These are the approved design's existing limits, independently exercised, not newly established Material defects. `findings.json` contains the same disposition for machine-readable review.

- **F1 Deferred risk:** multiline/regex assertions still report a stale pointer. User/workflow: a maintainer writes an assertion outside the approved same-line shape. Observable harm: that unsupported assertion would require reformatting or a later discriminator change. Protected value: none; AC-1 explicitly scopes the exception to one line with the recorded successor. Trigger evidence: the multiline and regex cases in `results/limits.json`, each exit 1. Becomes Material if such forms enter an accepted workflow/criterion.
- **F2 Deferred risk:** a same-line `see docs/adr/0002-a.md; Superseded by 0003` comment is forgiven. User/workflow: maintainer annotates the old citation with its recorded successor. Observable harm: no supported-workflow loss demonstrated; the checker does not establish semantic assertion intent. Protected value: none; the approved design expressly permits this form. Trigger evidence: the same-line comment case exits 0, but an authority citation on another line exits 1. Reopen if an accepted requirement needs semantic discrimination or supported stale authority lacks an accurate governing successor under this exception.
- **F3 Polish:** wrong-successor assertions retain the instruction to point at the correct successor. User/workflow: author writes a broken same-line assertion. Observable harm: the wording may distract from fixing the assertion. Protected value: none; AC-3's rejection remains correct. Trigger evidence: wrong-successor and overlong-successor cases exit 1 with the retained diagnostic. No repair needed to meet this scope.

The implementation's publication/RoboRev/CI limits are correctly separate from local acceptance. The saved live PR receipt now confirms FO has published Draft PR #806 at the named candidate; it does not prove review or CI completion. This validator ran neither RoboRev nor remote CI. No CI configuration changed; cost per PR was not measured. Number guards pass; migrations are explicitly skipped because the adopted workflow declares no migrations path. Native integration used CLI 0.27.2 and plugin 0.27.3; its passing synthetic checks do not establish arbitrary version combinations or native model execution.

## Affected documents and necessity

`results/doc-impact.log` lists six documents. Each has an implementation disposition, and direct inspection supports it:

- `docs/adr/0064-a-round-three-declined-finding-becomes-a-backlog-task-only-with-a-bite.md`: unaffected; unchanged ROUND_RULE and follow-up wording pins remain its protected content.
- `docs/journey/kc-decision-log/p1-technical-contract.md`: unaffected; existing format/status/target and exit-code statements remain true. No new status format or semantic authority decision is introduced.
- `docs/journey/kc-decision-log/slice-map.md`: unaffected; unchanged native-format references, command contract and checker link.
- `kc-dev-flow-2/README.md`: unaffected; its native integration command is the command exercised here.
- `kc-dev-flow-2/references/sd/adoption.md`: unaffected; the dispatch entrance and package-root argument remain unchanged and exercised.
- `learning.md`: unaffected; its historical dispatch wording examples are unchanged.

Goal sufficiency: the real unsplit citation now passes and authority misuse remains rejected within the accepted discriminator. Minimal necessity: removing the source exception restores the false positive; dropping its synchronized copy fails parity and leaves dev2 users on the defect; dropping the new tests loses the demonstrated boundary falsifiers. Restoring the natural path removes the original evasion and makes the real bite an integration control; without it, base would still pass the split-path site. The diff contains only the four approved files, no version/manifest/CI/instruction changes, and no diagnostic-string change. Lifecycle instruction words therefore have zero delta at the five named moments; the repaired case loses only its false-error line. Comment measurement is 53 code lines, zero added comment lines (0.0%; maximum 5%).

## Ownership

Product bytes and revision remain unchanged. Report/evidence are the only state changes. `../dispatch/validation-1-message-1.md` explicitly allows the required state helper's push to `spacedock-state/dev2`; product pushes, PR edits/reviews/ready and merging remain outside this validation. FO must replay Captain steps, disposition the report, and retain the delivery/gate decision.
