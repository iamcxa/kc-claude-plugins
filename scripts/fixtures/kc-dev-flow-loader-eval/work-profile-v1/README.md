# Work-profile evaluator prototype

Status: preserved research input, not a product dependency or a passing
validation instrument.

This branch keeps the evaluator-specific bytes removed from the proportional
work-profile product slice. They were recovered from rejected candidate
`9634a70960e2b26687545edc8c88c3604bb17ceb` on top of validated product head
`7c1b12d68316a99cf7093bd0f13e11f9933b1f8f`.

## Potentially reusable seams

- exact-ref materialization and digest-bound manifests;
- four closed work-profile scenarios;
- conditional-package observations;
- explicit no-retry and timebox metadata;
- fail-closed `UNKNOWN` intent when required evidence is unavailable.

## Known invalid seams

- transaction actor and authority labels are copied from fixtures rather than
  authenticated from the Local Profile;
- promotion topology can be constructed by a test instead of observed at the
  originating runtime boundary;
- a candidate can receive a positive pair result when its known-bad baseline is
  `UNKNOWN`;
- provider model-usage keys do not count repeated provider responses;
- the correction-cycle frozen run stopped after one of sixteen declared sample
  responses, so it supplied no complete behavioral verdict.

The exact failures and preserved run receipts are recorded in
`docs/dev/.spacedock-state/proportional-work-profile.md`, validation cycles 1
and 2.

## Re-entry boundary

Do not merge or cherry-pick this commit as accepted evaluator behavior. A future
evaluation task may use `git cherry-pick -n` and harvest selected seams after
adding falsifiers for the invalid seams above. The change-impact authority is
`skill-ablation-harness` (5b); absolute review-quality ground truth belongs to
`review-effectiveness-benchmark` (62). Neither task is activated, funded, or
validated by this preservation branch.
