# Development comparison readiness — HOLD

Prepared 2026-09-20. This is the model-free implementation checkpoint for the
Pilot (attended limited real use). The approved [design](../design.md) remains
unchanged. No validation verdict, gate transition, model call, product edit,
product commit, PR publication or spending approval is recorded here.

## Recommended Captain decision

**Approve the concrete CLI-backed one-pair development proposal below with four
USD 4.9612 budget-stop thresholds (USD 19.8448 nominal total), accepting that these
are not a proven maximum invoice.** This single backend-and-spend decision is the
recommended adjustment to the original native/hard-ceiling proposal. Execution
remains held pending explicit Captain acceptance; the approved design is not
rewritten here. No product edit or new enforcement system is requested.

The strict proposed aggregate dollar ceiling cannot be substantiated by the
inspected interfaces: CLI stopping is triggered by already-reported cost, and the
maximum in-flight overshoot is unknown. If Kent requires USD 19.8448 to be an
absolute maximum charge, retain HOLD and do not launch this alternative. This
is the exact spending limitation, not a reason to build a new cost platform.

The native-host contract requires a 120-second total deadline for every worker
(`kc-pr-flow/skills/kc-pr-review/SKILL.md`, candidate lines 165–169). Inspection did
not establish a matching native control: a documentation gap, not a reproduced
defect or proof of unavailable capability. The existing optional CLI backend,
however, uses `communicate(timeout=prepared["plan"]["timeout_seconds"])` and process-
group SIGKILL in `finally` (`review-capability.py:957–1031`). It shares the planner,
result validation and outer-reviewer/finalization seam, but starts separate
Read-disabled, tools-disabled model processes with inline evidence. It is a small
experiment-method revision; results would concern that CLI-backed treatment and
could not prove native-worker performance or reliability. This path was inspected,
not executed or silently selected.

The proposed revision should describe four USD 4.9612 **budget-stop thresholds**
(USD 19.8448 nominal total), not promise a zero-overshoot invoice ceiling. Current
vendor documentation supports inclusive native-child accounting and stopping when
a threshold is reached; it does not establish reservation of in-flight requests.
For the proposed CLI treatment only, reserve USD 2.4806 for the outer process and
USD 2.4806 for all CLI capability attempts. The existing adapter divides the
capability budget by twice the number of selected workers, reserving one retry;
for this five-worker plan that is USD 0.24806 per attempt. These are potentially
inadequate allowances, not predicted prices. No transfer between portions or
second run is proposed. Separate-process child costs must be added to the outer
cost once; they are not native children in its aggregate. This budget interpretation
and host-method change require Captain approval; neither is adopted here.

## Frozen comparison

| Input | Exact selection |
| --- | --- |
| Development PR | [iamcxa/kc-claude-plugins#434](https://github.com/iamcxa/kc-claude-plugins/pull/434), merged historical development fix |
| Objective | Size the one-journey banner from its actual text and width, retaining the draw's 10-pixel subtraction so wrapped text fits |
| Target base | `33ffd50b217004411f58277cf986ccee7974fe55` |
| Target head | `29007f90fc628ae40faf2903dd02d9895f4dcffe` |
| Control whole plugin | `6bf62d1d7d3c343a97c973a7abd7424d03676437`, metadata 1.12.0; typed/profiled flags both `off` |
| Treatment whole plugin | `0d2e3164ccd2d60006688c5443717b818825a305`, metadata 1.12.0; typed/profiled flags both `on` |
| Other flags | Shadow and once-only-post `off`; no full-pass, cross-model or manual profile forcing |
| Host | Claude Code 2.1.273; absolute resolved binary and SHA-256 in `evidence.json` |
| Model / effort | `claude-opus-5`, `high`; same for outer agent, native children, single admission call and independent judge |
| Existing dependency plugin | `pr-review-toolkit` installed version `c447c3207a42`; complete local file hashes in `evidence.json` |
| Order | Control, then treatment; one random bit sampled before any outcome, retained in `evidence.json`; no redraw |
| Total arm interval | 1,200 seconds, starting at Kent's start message before any arm checkout/acquisition; no subtraction |
| Native attempt | 120 seconds per worker; at most one authorized transient retry within the original arm and budget |
| Mechanical policy | Source/syntax only: `node --check` on the two changed files, each at most 240 seconds; no installs, browser launch, model tests or build scripts |
| Calibration | Three synthetic cases in `calibration.md`; human answer-key check pending; no real target defect claim |

The target is a normal two-file bug fix (33 additions, 2 deletions), with a
substantive public objective, immutable locally available commits, and a Node
runtime meeting its package's Node >=22.13 requirement. Selection used one bounded
scan of the latest 65 local commits, metadata/size/toolchain suitability, and one
successful PR lookup. The larger popup feature seen in that history was unsuitable
for Lite by size; no review outcomes were used. One earlier provider lookup used
the wrong repository owner and failed before the remote URL was corrected.
This is a development sample, not a randomly representative PR. Its patch, PR,
close variants and known-defect derivatives are permanently excluded from later
held-out evaluation. The old PR #1693 repair was not selected.

`sample.json` retains the full public PR wording; `sample.patch` retains the
base-to-head binary-capable diff. Hash and merge-base evidence are in
`evidence.json`. The PR is merged; historical review is intentional. Both arms
must reacquire/read that frozen material inside their timed intervals, use fresh
contexts/checkouts, and verify the live PR still identifies the frozen head.
Any drift or unavailable input stops this single pair, with no replacement search.

## Admission and test boundary

The actual candidate `plan()` function ran locally with the retained
`planner-input.json`; `planner-output.json` is its unedited result. It selected
Lite, bugfix, and all four mode booleans false. It required code correctness,
documentation accuracy, goal alignment, security risk and silent failure.
The catalog produced no path signals for these `.mjs` files, so `test_evidence`
is not required and the planner selected no mechanical test commands. This is
an observed property of this pinned candidate, not permission to add a question
or change its catalog. The common syntax commands remain available to either arm;
retain which commands each actually uses. Their results cannot establish rendered
banner correctness. Neither arm receives readiness analysis or planner results.

Legacy control triage has **not run**. Its eventual independently returned six
modes must be retained verbatim and must also be Lite/bugfix with full_pass,
probe_required, cross_model and noise_filter false. Our size/archetype expectation
is provisional. A different triage outcome stops this candidate; no forced Lite,
second candidate or admission retry is funded. Deterministic planning must be
rerun against the identical paid-admission identity, then inside treatment.

Node, Python, Git and shell tools are installed; versions are pinned in the audit.
`node_modules` is absent from the owned checkout. No dependency was installed.
The launch policy deliberately authorizes syntax checks only, not the PR's claimed
77 tests or browser smoke. Those historical PR-body claims remain unverified review
data; both reviewers and the judge must distinguish them from observed test output.
A request to add dependency installation or browser validation changes this frozen
policy and must be settled before spend, not improvised during either arm.

## Existing controls and evidence strength

| Claim | Evidence and limit |
| --- | --- |
| Whole journey elapsed | External operator stopwatch, at least 0.1-second resolution, and actual start/delivery observation. This is the measurement, not a new automated instrument. No arm timestamps exist yet. |
| Local total cancellation | GNU timeout 9.4 returned 124 for a 0.1-second deadline around `sleep 5` (0.108 seconds observed). This exercises one local process only; it does not prove native-child/API cancellation. |
| Native attempt deadline | Candidate fixes 120 seconds and delegates enforcement to host. CLI help and official subagent/env references did not identify a matching total-duration control. Stall timeout resets on progress and cannot be substituted. No paid behavior probe ran. |
| Aggregate dollars | Current CLI/SDK docs say `total_cost_usd` includes native children and budget exhaustion stops background children on versions >=2.1.217. Installed 2.1.273 qualifies by version; this particular run has not exercised that behavior. |
| Aggregate tokens | Use final `modelUsage` across the tree; top-level `usage` excludes children. Retain raw request IDs to deduplicate streamed chunks. Do not add child subtotals to an already inclusive final total. |
| Billing | Host dollar total is a local estimate; provider usage/billing evidence owns actual charge. No billing mode, account-specific rates, dedicated ceiling or usage export was established here. Unknown costs cannot pass the joint goal. |
| Model identity | Existing local transcripts contain `claude-opus-5`; only model/usage keys were inspected. Explicit main/subagent configuration is proposed. Actual per-call IDs and effort inheritance still require run evidence; no model-availability call occurred. |
| Tools | Candidate worker frontmatter is Read-only and model-inherit. Control dependencies include fixed model aliases; use the documented force setting below to keep both arms on one named model, then verify emitted IDs. This is an experiment configuration, not a plugin edit. |

Primary vendor references, inspected 2026-09-20:
[CLI budget flag](https://code.claude.com/docs/en/cli-reference),
[whole-tree cost fields](https://code.claude.com/docs/en/agent-sdk/cost-tracking),
[budget stopping semantics](https://code.claude.com/docs/en/agent-sdk/agent-loop),
[cost estimate versus billing](https://code.claude.com/docs/en/costs),
[subagent controls](https://code.claude.com/docs/en/sub-agents), and
[environment controls](https://code.claude.com/docs/en/env-vars).
Documentation is stronger than a help flag but is not a live cancellation test.
The searches were confined to this selected native host; no provider comparison ran.

## Spend and data ownership

The historical basis remains the six review-bearing daemon iterations in
[the prior audit](../source-audit.json), maximum USD 4.9612, without model/version
attribution. It is not a current Opus 5 estimate or a guarantee any envelope fits.
Retain separate non-transferable proposed envelopes for admission, control,
treatment (all children/retries/synthesis), and judge (calibration plus adjudication).
Do not spend any of them yet. Admission failure, calibration failure, invalid
output, intervention, timeout or budget termination ends this pair; retain failed
and not-run arms. Unused money buys neither repair nor replacement.

Kent is the proposed external operator and data custodian. The independent judge
must have a fresh context, no worker/synthesis role, no arm mapping or timing, and
no access to the other contexts. Kent keeps the answer key, randomized label
mapping, timing, complete transcripts, raw outputs and billing receipts private
under the task's `.context/pr-review-lite-value-pilot/runs/dev434/` directory.
Only sanitized summaries and artifact hashes belong in shared state. The author
of this readiness package is not an independent judge. Human calibration checking
and a 0.1-second stopwatch are prerequisites, not claims already fulfilled.

Freeze the judge's accepted findings, same-defect groups, maximum severities,
false positives and coverage before unsealing timing. Both arms must complete;
treatment coverage must be complete; no accepted Critical/High control defect may
be missed; treatment false positives cannot exceed control. Only then calculate
`1 - treatment_seconds / control_seconds`. At least 0.333 plus known treatment
cost no greater than control supports proposing the separately unfunded five-pair
evaluation. Unknown cost or phase timing allows no joint saving/causal claim.
The approved five-pair acceptance gates, denominator and one-backup rule remain
unchanged; this package funds or runs none of them.

## Preservation and launch prerequisites

Recomputed candidate totals remain 18 files / 5,884 changed lines / 1,903 focused
lines against `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`, within the unchanged
20 / 6,600 / 1,903 limits. No denominator reset, rebase, product patch, default
change, historical-record rewrite or automated-measurement repair was performed.

Before any model prompt: separate Captain spending/measurement acceptance,
existing native 120-second deadline/cancellation evidence, billing attribution,
human-checked calibration and operator readiness must be present. The templates
in [runbook.md](runbook.md) are concrete held instructions, not dispatch authority.
For the proposed CLI alternative, its existing source-owned deadline replaces
the unresolved native deadline prerequisite; no native-control probe is proposed.
A documentation-only timeout gap must not be reported as a proven product defect.
If an existing matching control is identified, record it here through a later
readiness update; do not invent a new system or silently relax the candidate.
