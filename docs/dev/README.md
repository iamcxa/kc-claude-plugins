---
commissioned-by: spacedock@0.25.0
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 2
  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
    - name: implementation
      worktree: true
    - name: validation
      worktree: true
      fresh: true
      feedback-to: implementation
      gate: true
    - name: done
      terminal: true
---

# kc-claude-plugins — Development Workflow

Tasks move `backlog → ideation → implementation → validation → done`.
Spacedock owns stage transitions, gate records, worktrees, and state durability;
this file binds repository authority and the judgment needed at each stage.
Repo-wide delivery and version rules remain in `CLAUDE.md`.

## Local Profile

Read [`_mods/kernel.md`](./_mods/kernel.md) completely before continuing work.
It is vendored byte-for-byte from `kc-dev-flow/references/kernel.md`, enforced by
`scripts/kc-dev-flow-contract-test.py`. Then read only the current stage's
declared `Policy mods` below. No binding YAML, digest registry, or installed
package fallback participates in continuation.

| Role | Bound local authority |
|---|---|
| Project context | Root `PRODUCT.md`, `ARCHITECTURE.md`, and `CLAUDE.md` |
| Work items | Spacedock entities under `docs/dev/` |
| Iteration | Captain-owned product sprint headings in `docs/dev/ROADMAP.md` |
| Execution state | Split-root `docs/dev/.spacedock-state` on `spacedock-state/dev`, owned by Spacedock |
| Delivery | One independently deliverable squash-merge PR to `main` by default; conditional stacks follow the implementation rule below; GitHub required checks; release-please owns versions and tags |
| Gate verdicts | Exactly one fresh EM under `Gate Authority` at ideation and validation |
| Scope and irreversibility | Captain |
| Observation | none |

The normal route uses all five stages. A known-cause, single-seam defect with a
mechanical acceptance test may skip ideation, but it keeps implementation,
validation, delivery, and every evidence bar. The adopted optional control is
`bound_field_validation`, implemented by
`scripts/dev-flow-work-context-check.py`.

This repository authors `kc-dev-flow`, so package references and adopted `_mods/`
copies are separate. The contract test keeps the adopted kernel,
reverse-recovery audit, and Work Control Profile byte-identical to the package.

## State layout and prerequisite

Each task is `{slug}.md`, or `{slug}/index.md` when it has stage artifacts.
Slugs are lowercase hyphenated words. State lives in a per-workspace split-root
worktree so task transitions do not churn the product branch.

Only the workspace whose state checkout is on `spacedock-state/dev` is the
holder. Before filing, reading for an outward action, mutating, or resuming after
an approval pause, run:

```bash
scripts/dev-flow-state-prereq.sh
```

Exit 0 establishes a clean holder equal to the freshly fetched state tip. A
non-holder must not attach, emulate, or mutate the holder; use a private detached
worktree for an authorized append and preserve it until its push is observed.

For a normal state mutation, keep the setter and durability step together:

```bash
spacedock status --workflow-dir "$WORKFLOW_DIR" \
  --set "$SLUG" "${EXACT_FIELD_ASSIGNMENTS[@]}" &&
  spacedock state commit --workflow-dir "$WORKFLOW_DIR" "$SLUG"
```

Do not rerun the clean-holder prerequisite between those commands: the setter is
expected to make the holder dirty.
Read [`runbooks/state-recovery.md`](./runbooks/state-recovery.md) only after the
prerequisite returns 75, 76, or 77, a state transaction is interrupted, or an
archive move is partial. Ordinary continuation does not load that runbook.

### Queryable fields

| Field | Rule |
|---|---|
| `id`, `title`, `source` | Stable identity and provenance |
| `status` | `backlog`, `ideation`, `implementation`, `validation`, `done` |
| `product` | Required marketplace plugin slug or reserved `repo-platform` |
| `sprint` | Blank until scheduled; then product-local `S<number>` present in ROADMAP |
| `started`, `completed` | First departure from backlog; authenticated product PR `mergedAt` |
| `verdict` | `PASSED` or `REJECTED` at final validation |
| `worktree` | Set on worktree dispatch; cleared after terminal merge |
| `issue`, `pr`, `mod-block` | Delivery references and merge lifecycle guard |
| `design` | `required` or `trivial-pass`; set at ideation or defect classification |
| `lane` | `main` or `defect`; set when routing out of backlog |
| `ledger_pr`, `ledger_artifact_v1` | Legacy bytes only; preserve but never consume for authority |

Sprint identity is the pair (`product`, `sprint`); write `kc-dev-flow/S1`, not
bare `S1`, in cross-product reports. A task belongs to the plugin owning its
primary outcome even when it touches a shared file. Multi-plugin, marketplace,
CI, root configuration, or workflow-schema outcomes use `repo-platform`.

After the holder prerequisite, validate the exact task at capture, when changing
`product` or `sprint`, and at each transition review:

```bash
python3 scripts/dev-flow-work-context-check.py validate \
  --task "$TASK_FILE" \
  --marketplace .claude-plugin/marketplace.json \
  --roadmap docs/dev/ROADMAP.md
```

Exit 1 is `FAIL`; exit 2 is `UNKNOWN`. Both block the controlled-field boundary.
For a complete-population authority claim, use the same program's `audit` mode
against the clean state holder; filtered results remain advisory until its
corresponding authority flag is true.

## Proof Policy

`_mods/kernel.md` owns outcome and verification discipline. Local checks are:

- `scripts/kc-dev-flow-contract-test.py` for the portable/adopted contract;
- `scripts/kc-dev-flow-loader-eval.test.py` for the deterministic capture adapter
  contract with a fake Spacedock executable;
- `scripts/version-parity-check.sh` for release propagation and version parity;
- `scripts/marketplace-verify.sh` for marketplace schema and local-source install;
- `scripts/skill-frontmatter-lint.sh` for skill frontmatter;
- exact-head GitHub checks for workflow and merge evidence.

For workflow-behavior evidence, capture the installed loader boundary manually
against two exact commit refs; keep the new receipt directory outside the
checkout:

```bash
python3 scripts/kc-dev-flow-loader-eval.py \
  --known-bad-ref <exact-commit> \
  --candidate-ref <exact-commit> \
  --output-dir "$RECEIPT"
```

The capture records exact implementation-stage bytes, tool/ref/fixture
provenance, and opaque Q08 runner prompts. It does not run or grade a model.
Fresh paired model pressure and hidden-rubric grading are validation-only
evidence. A deterministic contract pass does not establish loader equality;
loader equality does not establish worker behavior.

For proportional-work-profile validation, use the same capture adapter in its
closed mode after both refs are committed:

```bash
python3 scripts/kc-dev-flow-loader-eval.py \
  --mode work-profile-v1 \
  --known-bad-ref <exact-commit> \
  --candidate-ref <exact-commit> \
  --output-dir "$RECEIPT"
```

That mode snapshots the ideation stage and conditional chooser, copies four
frozen fixtures and `score.jq`, and writes a sixteen-slot manifest: no retry,
four-way maximum concurrency, model stop at minute 15, and the same-clock
20-minute ceiling. It performs no model call. Validation supplies each recorded
response and runs the copied expression as
`jq -c -f score.jq <fixture-result-input.json>`; missing output remains
`UNKNOWN`, never a clean or zero-cost sample.

A negative result carries the kernel's positive-claim bar. Sampled text matches
do not prove a population; a check offered as evidence must name what change
would make it fail. An absolute claim in a reference, comment, or commit message
names its enforcement point or is rewritten as a bounded claim.

## Stages

Each stage report starts with the verdict or decision. Link raw commands and
full diffs; do not replay the session narrative.

### `backlog` — capture

Policy mods: [`_mods/work-control-profile.md`](./_mods/work-control-profile.md).

Capture `title`, `source`, `product`, and one problem paragraph. Leave `sprint`,
`lane`, and `design` blank unless the captain has scheduled or classified the
item. Capture grants no design, scheduling, or execution authority.

A defect may route directly to implementation only when all four hold:

1. root cause is cited at `file:line`;
2. one mechanical test fails before and passes after;
3. one seam changes, with no schema or cross-layer ripple;
4. no design choice remains.

At that transition, record `lane: defect`, `design: trivial-pass`, the mechanical
AC, appetite/tolerance, and one-dispatch sizing. If any condition fails, use the
main route through ideation.

### `ideation` — decide scope, route, and acceptance

Policy mods: [`_mods/engineering-judgment.md`](./_mods/engineering-judgment.md),
[`_mods/journey-slicing.md`](./_mods/journey-slicing.md),
[`_mods/reverse-recovery-audit.md`](./_mods/reverse-recovery-audit.md), and
[`_mods/work-control-profile.md`](./_mods/work-control-profile.md).

- Re-read the exact work item and its `## Work profile receipt`. If it is valid
  and its basis is unchanged, consume it without another question. If it is
  missing, or the audience, lifespan, mutation boundary, authority need, or
  operational commitment changed, invoke `kc-dev-flow:choose-work-profile`.
  The chooser recommends and asks through the host's best structured question
  capability or one concise plain-chat fallback; the dispatched ideation actor
  compares the exact entity, commits only its state path, syncs it, and re-reads
  the committed receipt.
  Only after the committed receipt is re-read may inherited criteria be normalized or acceptance criteria be expanded.
  Tasks already beyond ideation are not reopened without an observed promotion
  trigger, and the bounded mechanical-defect route keeps its valid ideation skip.
- Ask the captain what value is protected, the appetite and tolerance, what to
  keep if cut, explicit non-goals, and the assumption most likely to be wrong.
- Record the fastest path and smallest cut. Take the cheaper route when it
  satisfies the same ACs; a dropped or deferred value surface is a captain-owned
  scope cut.
- Record one pre-mortem: if the accepted design ships and still fails, why?
- Record `design: required` with the concrete decision, or `trivial-pass` with
  the reason. A missing determination returns the gate unread.
- Before `build/add`, run the reverse-recovery audit against fresh `origin/main`.
  Classify existing layers and repair one broken seam instead of rebuilding.
- For non-trivial brownfield work, trace candidate surfaces backward from the
  accepted outcome and record the kernel's subtractive result. Return a proposed
  new surface unless its without-it instrument produces a named AC failure;
  preserve an existing `UNKNOWN` surface without claiming it is irreducible.
- Return a proposed gate, check, harness, automation, or registry unread unless
  its necessity record names three labeled facts: `Criterion:` the value-level
  AC it serves; `Alternative:` the simplest existing or lower-authority path and
  why it is insufficient; and `Escape:` a specific past defect it would have
  caught, proved by mutation. With no past escape, require
  `Escape: speculative until YYYY-MM-DD; review <work-item ref>` and resolve the
  reference to a backlog seed in this README's work-item authority before the
  gate. At that review, removal is the default recommendation; the seed grants
  neither deletion nor renewal authority. This ideation refusal is the
  enforcement point; a text or existence check does not prove the behavior.
- Write end-state ACs with `Verified by:` and a concrete falsifier. At least one
  AC measures the accepted value. Run `status --read <ref> --ac-scan` before the
  gate and keep each bold AC heading on one line.
- Require E2E evidence for user-visible or full-stack behavior; record the
  docs/config/CI-only reason when it does not apply.
- Propose affected PRODUCT/ARCHITECTURE wording, spike the riskiest unproven
  mechanism, and size one worker by default. Split only for more than about 90
  minutes, three independent behaviors, or real parallel wall-clock value.

Every ideation gate receives exactly one fresh-context EM verdict through
`kc-dev-flow:science-officer-em`. Prefer a capability tier above the authoring
worker; when none exists, use the highest available tier in fresh context with
high reasoning. The EM returns one advisory engineering_judgment record; Gate
Authority decides whether it advances or reaches the captain.

### `implementation` — build the smallest accepted slice

Policy mods: [`_mods/work-control-profile.md`](./_mods/work-control-profile.md).

Links to mods not listed in `Policy mods` are inactive locators, not active
policy, until their stage-native trigger is satisfied.

Implementation opens no reviewer loop. If an accepted premise changes, return
the decision to its owning stage; do not adjudicate it while coding.

- Use an isolated worktree. For each behavior, record a failing RED test, write
  the minimum change, then record GREEN. RED and GREEN close in one session and
  commit together.
- Every behavior assertion must be reachable and able to fail in RED; label
  arrangement/precondition assertions that intentionally stay green.
- When behavior changes, audit tests that arrange the old behavior so fixtures
  are not silently narrowed.
- Run scoped tests while iterating, then the full relevant suite once at exit;
  fix and rerun any surfaced failure. Run only ripple checks earned by the diff.
- Compare local versus CI OS, pinned-tool, and timeout conditions when the diff
  depends on them. Exact-head CI remains merge authority.
- Apply the ideation-approved doc diff. No unrelated refactor or speculative
  mechanism belongs in the deliverable.
- Before validation, map every changed file to an AC. Delete an unmapped file or
  ask the captain to authorize its scope.
- After a candidate revision, changed-file map, merge-base diff size, and
  independent/dependent slice assessment all exist, read only the authoritative
  Delivery topology decision in
  [`_mods/pr-merge.md`](./_mods/pr-merge.md#delivery-topology-decision). Before
  those four facts exist, leave `_mods/pr-merge.md` unread. Once loaded, use its
  dependent green layers, independent green slices, and numeric trigger
  predicates without adding another readiness condition here. Stack shape is
  delivery topology, not minimality evidence.

### `validation` — fresh, adversarial evidence

Policy mods: [`_mods/engineering-judgment.md`](./_mods/engineering-judgment.md)
and [`_mods/work-control-profile.md`](./_mods/work-control-profile.md).

Read [`runbooks/validation-evidence.md`](./runbooks/validation-evidence.md) when entering validation;
it is not part of backlog, ideation, or implementation reading. A fresh-context
validator checks the exact deliverable against ideation ACs and never finishes
the implementation.

At validation entry, when an existing product PR or stack layer exists, load the
GitHub-native observation defined by the active `pr-merge` delivery hook as
validation input. A brand-new delivery with no PR completes local validation and
creates its Draft only after captain push approval; absence before that initial
creation is not an error, but the Draft must be observed before Ready.

The validation report records one compact `PR feedback:` entry per PR or layer.
It binds `github-pr-feedback/v1` to the explicit repository, PR or layer, exact
head, fingerprint, complete normalized item population, and an evidence-bearing
disposition for every item. Feedback is a claim to verify, not authority to
obey. If work is required, use the ordinary implementation worker and re-enter
fresh validation after a code change. The optional
`kc-pr-flow:kc-pr-review-resolve` skill may accelerate repair, but it does not
supply observation or gate authority; its absence never establishes clean
feedback.

The stage report records: `Lenses:`, `Diff coverage:`, `Adversarial:`,
`Cross-model:`, `E2E:`, and `Origin re-observation:`. When origin evidence
applies, its line includes `Reported scenario:`, `Originating runtime kind:`,
`Re-observation artifact/revision:`, `Equivalent-runtime rationale:`,
`Falsifier kind:`, and `Result:`. An inaccessible originating runtime is missing
evidence and is not an `N/A` condition.

Every validation gate receives exactly one fresh-context EM verdict through
`kc-dev-flow:science-officer-em` against the exact revision and governing ACs.
The engineering_judgment advisory record includes adjudications, dissent, a
disproof condition, and the authority boundary.

The validator challenges every retained new surface, or inseparable surface
group, with its recorded without-it instrument. A named AC failure may support
bounded irreducibility. Green or `UNKNOWN` evidence returns a proposed addition;
for an existing surface, green produces only a captain-owned removal candidate
and `UNKNOWN` preserves it outside the irreducibility claim. Wiring claims keep
the kernel's same-kind runtime observation boundary.

Multi-model review is optional. The EM records `recommended` only for a
contested, irreversible, low-confidence, or unresolved call; otherwise it
records `not_needed`. The FO asks the captain whether to add the pass only on
`recommended`, and silence is not approval. This optional pass never replaces
the one EM verdict.

Reject with concrete evidence and return to implementation. Re-enter validation
fresh after correction. After two consecutive rejected cycles at the same gate,
the EM recommends one of: another bounded correction, ideation reset, narrower
captain-approved scope, or stop. Preserve accepted measurement evidence in the
entity; delivery never depends on token accounting.

### `done` — terminalize after delivery

Policy mods: [`_mods/work-control-profile.md`](./_mods/work-control-profile.md).

Only an authenticated product PR observed merged with required checks green on
its exact HEAD authorizes terminalization. Repeat the complete provider
observation before terminalization and require current
`github-pr-feedback/v1` proof for every PR or stack layer at that same head. A
stale, incomplete, mismatched, or `UNKNOWN` result blocks terminalization and
preserves `mod-block`. Only then clear the product `mod-block`, set `completed`
from the PR's `mergedAt`, set the passed verdict and `done`, commit the live
entity, then run the path-scoped archive transaction. Terminal state is not
archive proof; preserve the live entity when archive validation fails and load
the recovery runbook.

## Continuation and handoff

Resuming a branch or session does not inherit validation. Inventory committed
and uncommitted work, re-anchor on the source requirement, re-classify the diff,
and reconcile fresh `origin/main`. A fresh validator re-runs validation; the
resuming implementer does not self-certify.

In Conductor, sibling workspaces have separate worktrees, but two sessions in
one workspace can change the same checkout. Read the tree you are standing in
and commit from an isolated worktree when it is contended.

## Gate Authority

| Seat | Holds |
|---|---|
| Captain | Scope, architecture/schema, irreversible or merge-governing changes, costly_no recommendations, accepted red residuals, and seat disagreement |
| EM (`kc-dev-flow:science-officer-em`) | One bounded ideation or validation recommendation: `proceed`, `narrow`, `return`, `block`, or `costly_no` |
| FO | Checklist accounting, dispatch, evidence presence, state mechanics, and delivery mechanics; no adjudication |

The EM is the default gate seat. The FO supplies the exact revision, ACs,
receipts, and findings; it does not pre-resolve them. When the decision is
reversible, every AC has evidence, and no Material finding survives, EM approves
and FO advances. Notify the captain in one line; do not ask for a repeated gate.

Escalate only when one of these holds:

- the call is irreversible or changes merge rules;
- scope is authored or cut;
- a Material finding changes what ships;
- a red residual needs acceptance;
- EM and FO disagree;
- two consecutive rejected cycles close at the same gate.

Every escalation starts with `換句話說` and states what breaks, reversal cost,
and the concrete choice. If there is no decision the captain owns, return it to
EM. Prior approval never authorizes a later gate.

Irreversible, schema, scope-cut, and `costly_no` calls require fresh independent
EM synthesis before presentation. A validation verdict for one change is not a
merge-rule change. Provider labels and mechanical green carry no authority.

## Canonical docs ownership

| File | Owner and update point |
|---|---|
| PRODUCT.md / ARCHITECTURE.md | Ideation proposes, implementation applies, validation verifies |
| ROADMAP.md | Captain or sprint commander at scheduling/strategy changes |
| This README | Captain-approved workflow revision only |
| Trigger-loaded runbooks | Same change that alters their referenced mechanism |

## Task Template

```yaml
---
id:
title:
status: backlog
source:
product:
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design:
lane:
---

## Problem

## Proposed approach

## Design determination

## Acceptance criteria

**AC-1 — <end-state property>.**
Verified by: <external check>. Falsified by: <change that flips it>.

## Test plan

## Measurement

## Doc diff

## Out of scope
```

## Commit Discipline

- State commits are entity-root-scoped through Spacedock; never stage another
  task or use broad `git add`.
- Product commits land on the isolated feature worktree and follow
  `<type>(<scope>): <description>`.
- Merge only after exact-revision validation and required CI are green.
