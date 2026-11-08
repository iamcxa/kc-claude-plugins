# Hosted AC-8 refresh: independent final verdict

**PASSED** at PR #812 head `778367adde2e20e0b3e51966ddba2d9f77f9e614`, profile pilot. This is the bounded follow-up in `dispatch/validation-3-message-2.md`: independently read the third hosted attempt and update the verdict only. No product, criterion, Captain amendment, acceptance script or earlier evidence was changed.

## Primary evidence read independently

- Run `42468880068`, **attempt 3**, reports `head_sha=778367adde2e20e0b3e51966ddba2d9f77f9e614`, `status=completed`, `conclusion=success`; see `run-attempt-3.json`.
- `run-pipeline.json` confirms `Install pinned Spacedock`, `test_dispatch_stage.py`, `test_sd_dispatch.py`, and `test_observer_recovery.py` all completed successfully. The metadata was requested explicitly with `--attempt 3`, not inferred from the current PR badge.
- `seam-steps.log` is an unmodified selection of those four steps from the independently fetched attempt-3 log. It shows Spacedock v0.27.2, the downloaded binary archive passing its SHA256 check, the actual `SPACEDOCK_BIN` command running 20 dispatch-stage tests with `OK`, the real transport assertions, and the observer recovery success. The full raw log remains at `/tmp/pr812-ac8-refresh.ISBYdu/run-attempt-3.log`.
- `pr.json` independently confirms the PR still has the same head, remains OPEN/Draft, has mergeStateStatus CLEAN, and shows 7 SUCCESS checks and 1 SKIPPED check. This is a state observation, not merge permission.
- `verified.json` records the successful identity/status/step assertions over the provider responses. The local product worktree is clean and remains on the assigned branch/head.

Exact read-only commands (each output saved beside this note):

```bash
gh api repos/iamcxa/kc-claude-plugins/actions/runs/42468880068/attempts/3
gh run view 42468880068 --attempt 3 --repo iamcxa/kc-claude-plugins --json name,displayTitle,status,conclusion,event,headBranch,headSha,url,createdAt,updatedAt,jobs
gh run view 42468880068 --attempt 3 --repo iamcxa/kc-claude-plugins --log
gh pr view 812 --repo iamcxa/kc-claude-plugins --json headRefOid,isDraft,state,mergeStateStatus,statusCheckRollup,url
```

Source: https://github.com/iamcxa/kc-claude-plugins/actions/runs/42468880068/attempts/3

## Criterion and verdict

AC-8 now passes. The actual real-binary seam step passed on the exact candidate; the previously executed missing-binary and deleted-step falsifiers remain applicable at those unchanged bytes. Earlier HTTP 504 logs and the REJECTED-for-external-evidence report are preserved as history, not overwritten.

The prior independent local evidence remains in `../evidence.md`, `../acceptance/`, `../package-tests/`, `../scope-falsifiers/` and the other cycle-3 artifacts. It includes the 92-row matrix/98 preserved snapshots, the original and class falsifiers, all 28 CI-listed commands (1223 tests reported, 11 optional skips), the fresh-shell Captain script, and both required ADR-linter results. None of those suites was rerun for this narrowly authorized hosted-evidence refresh.

AC-9 still replaces superseded AC-5 under Captain amendment 1. The old F1 data-loss finding is fixed; F2 remains settled by that amendment. No open Material, Deferred risk, Polish or Needs decision finding remains. The known installed-0.35.0 ADR 0047 false positive remains explicitly recorded with the authorized candidate-linter exit 0; it is not relabelled as installed success.

The complete appended Stage Report carries forward all local criterion dispositions and limits and replaces only the missing AC-8 evidence and overall verdict. It supersedes earlier validation verdicts. The retained minimal script is `../acceptance.sh`; its previous fresh-shell passing observation is in `../captain-run-amended.log`.

Exclusive same-task ownership, caller-supplied model/roster, separate preflights, manual follow-ups and direct-builder bypass limits remain unchanged. Local RoboRev/external review disposition, model execution, post-release adoption, gate, merge and release remain outside this validation claim. CI cost per PR remains unmeasured; no CI configuration or trigger was changed. FO/Captain retain delivery authority.
