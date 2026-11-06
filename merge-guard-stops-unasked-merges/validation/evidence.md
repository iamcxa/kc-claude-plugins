# Validation evidence — PR #794

Candidate: 871c6b2f4ebccfc2c67df91d7d39ad038aa0710f
Base: b804d81d3abc94c9c321326dc75e7cac927c5252 (origin/main at dispatch)
Date: 2026-11-06
Verdict: PASSED at this candidate and the accepted Pilot boundary.

## Reproduction and identity

Code was exported with git archive into /tmp/validate-merge-guard-871c6b2-z7onrnpk/source. No product file was changed, no repository worktree was added/removed, and no shared git configuration was written. Read-only Git audits used the pinned assigned worktree; candidate programs ran from the export. source-sha256.json confirms all seven changed files equal the candidate blobs. PR #794 remained OPEN, draft, at this SHA on the final GitHub read. PR #793 was OPEN/draft at 5b3e290a7eaceb0fe70f489d25d622314598b9f0 when read; its prescribed first-merge order and any subsequent integration/revalidation remain FO-owned.

The installed validation skill resolved its package to /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0; audit commands used that root. The dispatch's explicitly requested ADR command was also run verbatim from its /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0 root, exit 0.

## Checks and counterexamples

- AC-1: python3 -B source/kc-dev-flow-2/scripts/test_merge_guard.py: 16 passed. Full/prefix identity, newest-only records, other PR/repo, missing/short head, multiple merges, flags/URL/origin, archive and _merges, nonmerge and host decisions are covered. Newest-to-oldest, Codex ask and removal of _merges glob each fail the designated test (six-mutation script/logs).
- AC-2: real temporary Git repository and linked spacedock-state/x worktree; uncommitted on-disk record carries, switching that fixture to another branch stops. Replacing disk reads with git show HEAD fails the same test. These fixture worktrees belong to new /tmp repositories, not the shared product clone.
- AC-3: native missing script and injected Python exception exit 2 via the wrapper on both hosts; unreadable newest records ask/deny, all with zero fake merges. Removing the wrapper makes Claude see hook exit 1 and run the fake merge once.
- AC-4: Claude 2.1.318 native auto headless: unmatched permission_denials with zero fake merges; matched one fake merge. Interactive transcript shows the full command, the guard reason and “Do you want to proceed?”; Esc cancels, zero fake merges. The no-wrapper native counterexample removes the stop. The initial trust-choice and later Enter calls were refused by FO, not Captain; FO corrected the trust navigation and authorized Esc. No merge request was approved by this validator. Session 89581 exited 0 before FO's final no-more-keys message; no further keys sent.
- AC-5: Codex 0.162.1 native unmatched deny with rules ignored and with operator rules loaded; the latter hook payload is plain gh pr merge and fake gh was on PATH with login=false. Both have zero fake merges. Matching record runs once. Codex ask mutation is rejected by the candidate's host-output test. Native command/result/hook/exit logs are saved under native/.
- AC-6: package replay over the saved 84-PR data: 54 pass / 30 stop, recount 74 pass / 10 stop, no differences from ideation. #672's original question is refused for missing head 6c972e7. Removing that record check gives 75 pass / 9 stop and passes #672. Recount questions for the other ancillary PRs remain explicitly synthetic, not historical approvals.
- AC-7: both registration bodies, wrappers, deny-only, Paseo loading, record route and stop-count assumptions checked; stale no-equivalent-hook sentence absent. lint-skills.py exits 0 at unchanged 5939-word budget. Removing the documented Codex wrapper fails the documentation contract check; AC-3 demonstrates why that clause matters.
- AC-8: ADR 0063 matches both recorded rulings and the full second-gate question for the four approved decisions. The seven-file diff excludes workflow.md and _mods; delivery_gate.py changes only ASK/ASK_UNQUOTED closing text. test_delivery_gate.py: 156 pass, one pre-existing skip (the five committed gate-presentation replay fixture requires GATE_PRESENTATION_STATE and was not configured). Reverting just the new reminder causes the named FoWriteRuleTests test to fail.
- AC-9: next numbering, URL/#number, head/answer requirements, refusal output and no-write cases pass. Removing the PR digit boundary fails the record refusal test. A copy of the adopted workflow README with a disposable task gives byte-identical spacedock status output before/after _merges (status.json, both exits 0). Two preliminary hand-built fixture headers were invalid and replaced with the adopted README; those failures were fixture setup, not product verdicts.
- AC-10: read captain-steps/1.md and task observation: Captain “看得到，也答了”, FO's post-answer no-pending-permission and one fake-merge observation. The source negative control removes that answer and is rejected. This is evidence integrity, not a new phone run or proof that the package SHA was on the phone. The criterion explicitly carries the prior POC/Captain observation.

## Additional required checks

ADR lint: 62 records, 0 legacy, exit 0; number guard exit 0, migrations not applicable; comment ratio 349 code / 3 comment lines = 0.9%, maximum 5%, exit 0. All added comments were read: module-purpose descriptions and ADR enforcement pointer, no narrative or review/task provenance.
doc_impact.py, dispatch_records.py (four records), design_surfaces.py, git diff --check all exit 0. The implementation checklist traces to accepted criteria/rulings.
Affected-document dispositions confirmed: ADR 0044 unaffected (summary/legacy behavior retained); ADR 0051 unaffected (round-count check retained); ADR 0062 unaffected (quoted-question grant unchanged); ADR 0063 updated; package README unaffected (installation still automatic nowhere; CI-listed test command added).
Reading cost independently reproduced: ASK 40→57, ASK_UNQUOTED 39→56, adoption 2347→2598, workflow 5939→5939 (reading-cost.json).
CI cost per PR was not measured. Existing package-path triggers are unchanged; the only workflow change adds this test command. Final PR read reports successful applicable hosted checks and skipped deployment; it is a provider observation, not a local hosted rerun.

## Minimal acceptance script

Run exactly:
```sh
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/merge-guard-stops-unasked-merges/validation/acceptance.sh
```

The script has five steps: export pinned clean candidate; run 16 guard tests; observe stop → record → pass → moved-head stop without executing gh; run delivery tests/lint; run the reserved ADR check. It declares the required local clone and installed 0.35.0 package paths. Expected final line: “Acceptance passed; no hook installed and no merge executed.” It was run unchanged in a fresh bash shell; acceptance.log is the observed output, exit 0, under five minutes. The script exposes command behavior; there is no product UI. It does not repeat the native-host/interactive/phone runs, persistent user registration, publication or merge.

## Sufficiency, necessity, findings and limits

The accepted mistaken-merge journey works through record discovery, host interception, refusal, record creation and retry at this head. Without the new script/registration there is no runtime stop; without the head check #672 passes; without || exit 2 a Python failure allows Claude's fake merge. Tests, the CI step, bounded reminder, adoption instructions and ADR each serve those accepted obligations; no extra runtime surface was retained.

No new Material, Deferred risk, Polish or Needs decision finding was established. Existing explicitly approved limits remain: records do not authenticate Captain identity or infer approval intent; an agent with Paseo permission tools can answer another agent's request; registration is manual, machine-specific and unverified on Captain settings; text mentions can false-stop, foreign repository records outside this clone are unavailable, short head prefixes are accepted as designed. This guards ordinary mistaken requests, not a hostile same-user actor or arbitrary obfuscated shell syntax. User-level hook-file installation/trust flow was not performed: native tests used equivalent temporary session hook settings.

Native isolation followed the implementation's recorded allowance: normal HOME/auth, Claude --setting-sources project plus temporary settings, headless no-session-persistence, Codex ignore-user-config/ephemeral and rules read-only. Initial sandbox host attempts failed before inference; authorized retries outside it produced the cited evidence. Interactive Claude wrote its own temporary-path trust/session metadata. No Captain hook settings or rules were edited; no real merge was attempted. All owned native processes finished; the interactive session exited 0 and fake log stayed empty. Test exports/evidence are retained under /tmp for review; CLI trust/session metadata is not deleted.

Validation recommends PASSED for this SHA. FO retains #793-first integration, independent review disposition, ready/merge gate, state push and post-release registration/rollout; none is implied by this report.

