# Local correction batch — incomplete, focused cap failed

This is the single approved local correction batch after approval commit `dab22663d8500df0b8c11ab48087ab27c3679771` and FO's independent readback confirmation. It is not a completed candidate, validation PASS or isolation integration. The one-batch pin exception expires when this report is returned.

## Exact product and count boundary

- Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot`; branch `feature/kc-pr-review-capability-protocol-pilot`.
- HEAD remains `9bb526170156a44cff90e2a2fab9eeab081e0eb1`; six modified paths remain **uncommitted and unpushed**. No untracked product paths. Cumulative base is `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`.
- [counts.json](counts.json) binds each of the 20 final product files, the dirty batch patch and cumulative diff by SHA-256. [batch.patch](batch.patch) preserves the exact six-path uncommitted change against HEAD. Tests below exercised these working-tree bytes, not clean HEAD alone.
- Standard cumulative `git diff --numstat <base>` additions plus deletions: **6,443 / 20 files / 1,903 complete focused**, against **6,600 / 20 / 1,800**. Total has 157 lines headroom; file limit is full; focused remains **103 over**. No new limit is proposed or assumed.

| Complete focused owner | Added + deleted relative to cumulative base |
| --- | ---: |
| Capability schema | 376 |
| Capability catalog | 96 |
| Protocol tests | 966 |
| Corpus | 7 |
| Runtime tests | 47 |
| All ablation test changes | 411 |
| Total | 1,903 |

The starting 1,939 focused footprint decreased 36 net after adding regressions. Equivalent same-file fixtures and two merged journeys retained existing assertions but were insufficient; [reduction and RED/GREEN evidence](red-green.md) describes the actual changes. No minification, excluded shell tests, uncredited relocation or second reduction/redesign cycle.

## Finding disposition and verification scope

F1/F2/F3/F9 use the existing adapter/schema owners: full minted identity, malformed provider raw-attempt closure, positive integer monotonic units and exact configuration invalidation. F4/F7 use the existing runner/telemetry owner: terminal and available/unknown cost without success seal, and pinned-arm adapter evaluation. F8/F12 retain findings while closing recommendation labels and ambiguous inline placement. F10/F11 add named missing-input/re-entry refusals before Path/exclusive-write failures. No new ledger, CLI surface, dependency, service, sandbox or retry lifecycle was added.

Actual focused RED/GREEN and five removal mutations are detailed in [red-green.md](red-green.md); raw mutation logs retain nonzero failures. Full protocol and ablation logs are preserved separately. A raw initial focused log was not saved; its observed tool result is identified as a transcript excerpt, never synthesized into raw evidence.

Final working-tree verification (same code/test bytes; only documentation changed after launch):

- `/usr/bin/time -p python -B kc-pr-flow/scripts/review-capability.test.py`: **25 tests OK**, 434.246 s test / 434.47 s wall, exit 0; [raw protocol.log](protocol.log). The two provenance-refusal diagnostics are expected negative assertions, not ignored failures.
- `/usr/bin/time -p bash kc-pr-flow/scripts/review-ablation.test.sh`: **83 passed / 0 failed**, 57.73 s wall, exit 0; [raw ablation.log](ablation.log). Both suites ran in independently owned temporary fixtures.
- `python -B /tmp/capability-correction.CGT81m/mutations.py`: five expected failures observed, instrument exit 0; [mutation results](mutations.json). The permanent refusal tests remained in the green full ablation suite.
- `git diff --check`: exit 0. No runtime/posting/daemon/CI owner changed; no broader unchanged suite was restarted.

Exact batch diff SHA-256: `fa9108f8bb0646139be7a8e222daeaa1a990d732706af6702d835931c779ee1e`; cumulative diff SHA-256: `cde4e8ec5e63ea1e517236a000158c81eb68323d955313d753b1e08af7d962eb`. Mechanical samples within the existing protocol run: prepare 0.948 s, projection 81.336/83.187 s, rehydrate 6.473/6.645 s. These are deterministic local overhead only, not hosted cost or model-review speed.

The full protocol suite includes actual runtime rehydrate, successful confirmation/posting-observation binding, High cross-capability merging, missing required evidence and incomplete fallback paths. The runtime/posting/daemon owners are unchanged this batch; the evidence manifest includes unchanged runtime hashes. The full ablation suite retains historical comparisons, whole-arm trees, admissions, blind seal, costs/unknown usage, credential fixtures and stalled-host cases. Stub and mechanical timings are not real-review speed or provider cost evidence.

## Documentation and project context

Only existing runtime usage prose changed: private raw stdout artifacts, positive monotonic integer units, recommendation vocabulary, repeated-phase refusal and ambiguous inline placement. No Mermaid block changed in this batch; earlier render evidence is retained, not rerun. Bound PRODUCT.md, ARCHITECTURE.md and CLAUDE.md were checked against these corrections: `project_context impact: none`, because existing default-off/Lite, authority, cost-unknown and private-artifact claims remain unchanged. No new product direction or root document rewrite. Fresh external validation of this classification is pending; author checks are not reviewer PASS.

## Still blocking or unproven

- **F6 remains BLOCKING**: same-authority arbitrary Bash can rewrite runner measurement; actual join accepted forged 1 ms. No isolation/trusted measurement remedy or acceptance of that defect occurred.
- F14 historical CI-trigger/measurement sequence remains unresolved; hosted incremental CI cost per PR is **unmeasured**. No CI file or trigger changed this batch.
- Real five-pair quality and 33.3% speed criteria, corpus/cost approval and all other unmet accepted obligations remain pending. No paid/model/cloud/reviewer/implementation-exit observation occurred; exit observation is **NOT PERFORMED**, not passed.
- F5 outer retry remains disproved as a required repair; F13 remains conditional, not silently completed. Prior rejected evidence and the one-round canonical-format deferral are preserved, not generalized into waivers.

Task remains held **validation**; historical pin SHA-256 is `8dbc54e264711a9d9da98a160726a3a9b4f846bed2d4e4b23196581fb5c67ea8`. No stage/status/pin/gate/review-round, branch, product commit/push, PR, merge, release or unrelated file change. The state-only report is the batch handoff; FO owns the next decision.
