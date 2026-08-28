# KC Dev Flow Planning and Development Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reshape Draft PR #306 so KC Dev Flow accepts provider-backed or standalone briefs, returns POC/Spike evidence to planning, and leaves runtime topology outside the portable kernel.

**Architecture:** Keep one profile engine. Pilot and Production consume a required Development Brief; POC consumes the existing v3 Exploration Brief fields; an optional complete Planning Receipt activates the existing provider reader and read-only comparator. Spacedock and repository workflow prose remain adapters, while the portable kernel contains no task, worktree, worker, or delivery cardinality.

**Tech Stack:** Markdown skill contracts, Python 3 deterministic contract tests, Python 3 mutation/ablation tests, existing Spacedock adapter scripts.

**Spec:** `docs/superpowers/specs/2026-08-28-kc-dev-flow-planning-development-boundary-design.md`

## Global Constraints

- Preserve POC, Pilot, and Production routes; add no profile or workflow stage.
- Add no planning plugin, stored planning schema, provider sync, projection, or CI job.
- A Development Brief is required for Pilot and Production.
- The existing v3 POC receipt fields are the Exploration Brief.
- A Planning Receipt is optional, complete, and read-only reconciled when present.
- Standalone work has no fake provider, Cycle, or Release/Milestone.
- POC/Spike evidence returns to planning before any delivery work is created.
- Goal sufficiency and minimal necessity remain the terminal kernel checks.
- Keep `kc-dev-flow/references/kernel.md` and `docs/dev/_mods/kernel.md` byte-identical.
- Do not change plugin versions or marketplace versions; release-please owns them.
- Do not commit, amend, push, or change Draft status without the Captain's explicit authorization.

---

### Task 1: Replace runtime-coupled admission with brief plus optional receipt

**Files:**

- Modify: `kc-dev-flow/references/kernel.md`
- Modify: `docs/dev/_mods/kernel.md`
- Modify: `kc-dev-flow/skills/adopt-dev-flow/SKILL.md`
- Modify: `kc-dev-flow/skills/continue-dev-flow/SKILL.md`
- Modify: `kc-dev-flow/skills/choose-work-profile/SKILL.md`
- Modify: `kc-dev-flow/README.md`
- Modify: `docs/dev/README.md`
- Modify: `scripts/kc-dev-flow-contract-test.py`
- Modify: `scripts/kc-dev-flow-minimal-stack-ablation.test.py`

**Interfaces:**

- Consumes: committed work item, `kc-dev-flow-work-profile/v3`, and the optional exact provider tuple `source`, `planning-window`, `planning-outcome`; current Ready membership is re-read from the provider.
- Produces: one of `provider-backed Development Brief`, `standalone Development Brief`, or `Exploration Brief`; provider reconcile runs only for the first route.

- [ ] **Step 1: Add fail-first contract assertions**

Replace the PR #306 assertions that require one task and one execution context
with assertions for the approved boundary. Use exact bounded phrases so later
prose changes cannot silently reverse the contract:

```python
for phrase in [
    "Development Brief is required",
    "Planning Receipt is optional",
    "complete or absent",
    "partial Planning Receipt",
    "Captain-approved committed work item",
    "does not invoke the planning reader or comparator",
]:
    require(phrase in normalized_kernel, f"kernel omits brief boundary: {phrase}")

for forbidden in [
    "one planning item to one SD task and one isolated execution context",
    "refusing a second task or execution context for the same admitted source",
    "The fresh executor receives",
]:
    require(forbidden not in normalized_kernel, f"kernel owns runtime topology: {forbidden}")
```

Update continuation ordering checks to accept two explicit branches:

```python
for phrase in [
    "all Planning Receipt fields are absent",
    "all Planning Receipt fields are present",
    "report `planning receipt incomplete`",
    "run provider reconcile only for the provider-backed branch",
]:
    require(phrase in normalized_continue, f"continuation omits receipt branch: {phrase}")
```

Replace `one-to-many-execution-restored` with four mutations:

```python
run_manual_contract_mutant(
    "required-development-brief-removed",
    "kc-dev-flow/references/kernel.md",
    "A Development Brief is required",
    "A Development Brief is optional",
    "kernel omits brief boundary: Development Brief is required",
)
run_manual_contract_mutant(
    "standalone-path-removed",
    "kc-dev-flow/references/kernel.md",
    "A Planning Receipt is optional",
    "A Planning Receipt is required",
    "kernel omits brief boundary: Planning Receipt is optional",
)
run_manual_contract_mutant(
    "partial-receipt-accepted",
    "kc-dev-flow/skills/continue-dev-flow/SKILL.md",
    "report `planning receipt incomplete`",
    "continue with the available planning fields",
    "continuation omits receipt branch: report `planning receipt incomplete`",
)
run_manual_contract_mutant(
    "runtime-topology-restored",
    "kc-dev-flow/references/kernel.md",
    "Runtime adapters own task and execution-context cardinality.",
    "Runtime adapters own task and execution-context cardinality. A portable rule must not bind one planning item to one SD task and one isolated execution context.",
    "kernel owns runtime topology: one planning item to one SD task and one isolated execution context",
)
```

- [ ] **Step 2: Run the focused tests and confirm the old PR fails**

Run:

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-manual-cycle-release-admission-path
cd "$WT" && rtk python3 scripts/kc-dev-flow-contract-test.py
```

Expected: FAIL because the current kernel lacks the Development Brief and
optional Planning Receipt phrases and still owns runtime cardinality.

- [ ] **Step 3: Rewrite the portable kernel boundary**

Replace `Planning and execution`, `Manual admission and route-back`, and the
universal scheduling exit bar with this semantic contract:

```markdown
## Brief admission

A Development Brief is required for Pilot and Production. It fixes the problem,
accepted outcome, complete non-goal list, acceptance evidence, and route-back
conditions. The v3 POC decision, falsifier, budget, and stop condition form the
Exploration Brief.

A Planning Receipt is optional and must be complete or absent. It is exactly the
source, planning-window, and planning-outcome tuple. When present, engage re-reads
current Ready membership and reconciles provider state. A partial Planning
Receipt stops as invalid input. Local sprint and sprint-readiness fields are
runtime mechanics, not receipt evidence.

Without a Planning Receipt, the Captain-approved committed work item is the
planning authority. It does not invoke the planning reader or comparator and it
does not invent a provider, planning window, or planning outcome.

Runtime adapters own task and execution-context cardinality.
```

Retain exact goal/non-goal comparison and structured route-back. Delete the
one-task, one-context, fresh-executor, retry, and candidate-cardinality clauses.

- [ ] **Step 4: Branch `continue-dev-flow` before provider access**

Make authority resolution follow this order:

```text
1. Read the exact committed work item and selected brief.
2. If all Planning Receipt fields are absent, use the Captain-approved committed brief.
3. If all Planning Receipt fields are present, run provider reconcile only for the provider-backed branch.
4. Otherwise report `planning receipt incomplete` and stop before execution-state reads or mutation.
5. Read execution state, load the selected profile contract, and continue the profile route.
```

Keep the existing fail-closed comparator behavior inside the provider-backed
branch. Remove the manual one-task/one-context and fresh-executor steps.

- [ ] **Step 5: Align adoption and profile selection**

In `adopt-dev-flow`, bind a planning reader and comparator only when the adopter
supports Planning Receipts. A standalone adopter binds the committed work item
and Captain as authority and installs no provider adapter.

In `choose-work-profile`, replace the universal "when it is scheduled" test with
the brief admission test. Keep `sprint` and `sprint-readiness` only as local
Spacedock execution-group mechanics when that runtime uses them; they do not
prove a provider Cycle or Release/Milestone.

State explicitly that feature and bug labels do not select a route. A clear
urgent bug may use a standalone Development Brief; an uncertain bug uses POC;
scheduled features and bugs may carry a Planning Receipt.

- [ ] **Step 6: Align package and repository documentation**

Update `kc-dev-flow/README.md` with the three accepted inputs. In
`docs/dev/README.md`, keep GitHub Project #4 as this repository's optional
planning provider but add the standalone branch and remove the `Agent execution
contract` runtime mapping. Keep the readable brief shape:

```markdown
## The problem

## Accepted outcome

## Non-goals

## Acceptance evidence

## Route-back conditions
```

The repository template may carry provider fields for scheduled work; all such
fields stay empty for standalone work. Do not restore the redundant
`## Human-readable release brief` wrapper.

- [ ] **Step 7: Synchronize the vendored kernel and run Task 1 tests**

After applying the same patch to both kernel copies, run:

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-manual-cycle-release-admission-path
cd "$WT" && rtk cmp kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md
cd "$WT" && rtk python3 scripts/kc-dev-flow-contract-test.py
cd "$WT" && rtk python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py
```

Expected: all commands exit 0; the ablation output rejects all four new mutants
for their named reasons.

- [ ] **Step 8: Prepare the Task 1 commit for Captain confirmation**

Show the exact diff and named file list. After explicit confirmation only:

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-manual-cycle-release-admission-path
rtk git -C "$WT" add kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md kc-dev-flow/skills/adopt-dev-flow/SKILL.md kc-dev-flow/skills/continue-dev-flow/SKILL.md kc-dev-flow/skills/choose-work-profile/SKILL.md kc-dev-flow/README.md docs/dev/README.md scripts/kc-dev-flow-contract-test.py scripts/kc-dev-flow-minimal-stack-ablation.test.py docs/superpowers/specs/2026-08-28-kc-dev-flow-planning-development-boundary-design.md docs/superpowers/plans/2026-08-28-kc-dev-flow-planning-development-boundary.md
rtk git -C "$WT" commit -m "refactor(kc-dev-flow): separate planning from development inputs"
```

---

### Task 2: Make POC and Spike return evidence to planning

**Files:**

- Modify: `kc-dev-flow/references/profiles/poc-exploration/base.md`
- Modify: `kc-dev-flow/references/profiles/poc-exploration/prove.md`
- Modify: `kc-dev-flow/skills/continue-dev-flow/SKILL.md`
- Modify: `kc-dev-flow/scripts/poc-close-guard.py`
- Modify: `kc-dev-flow/scripts/poc-close-guard.test.py`
- Modify: `docs/dev/_mods/profiles/poc-exploration/base.md`
- Modify: `docs/dev/_mods/profiles/poc-exploration/prove.md`
- Modify: `docs/dev/_mods/poc-close-guard.py`
- Modify: `docs/dev/README.md`
- Modify: `scripts/kc-dev-flow-contract-test.py`
- Modify: `scripts/kc-dev-flow-minimal-stack-ablation.test.py`

**Interfaces:**

- Consumes: v3 fields `poc_decision`, `poc_falsifier`, `poc_budget`, `poc_stop_when` and one validated `poc_outcome`.
- Produces: a terminal exploration result returned to planning; no downstream Spacedock entity or preselected delivery profile.

- [ ] **Step 1: Add fail-first exploration boundary tests**

Change the package contract test from requiring `poc_handoff` and
`source: poc:<exact-source-id>` to requiring route-back and forbidding downstream
creation:

```python
for phrase in [
    "return the POC outcome to planning",
    "does not create downstream delivery work",
    "planning decides whether a new Development Brief exists",
]:
    require(phrase in normalized_continue, f"POC route-back omits: {phrase}")

poc_guard = read("kc-dev-flow/scripts/poc-close-guard.py")
require('commands.add_parser("create")' not in poc_guard, "POC guard still creates downstream work")
require("poc_handoff" not in normalized_continue, "continuation still owns downstream POC handoff")
```

Add an ablation mutation that changes `return the POC outcome to planning` to
`continue directly into delivery`; require the contract test to reject it with
`POC route-back omits`.

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run:

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-manual-cycle-release-admission-path
cd "$WT" && rtk python3 kc-dev-flow/scripts/poc-close-guard.test.py
cd "$WT" && rtk python3 scripts/kc-dev-flow-contract-test.py
```

Expected: the close-guard test still exercises `create`, and the contract test
reports the missing planning route-back.

- [ ] **Step 3: Subtract downstream creation from the POC close guard**

Keep `prepare` and `consume`. Delete:

```text
parse_handoff
find_downstream
validate_delivery_body
emit_result
the create subcommand
the Spacedock new invocation
```

Make `validate()` return the work-item ID and validated `poc_outcome` direction.
`consume` validates the outcome and delegates only `spacedock gate consume`.
Neither command creates another entity.

- [ ] **Step 4: Rewrite POC completion semantics**

In the POC base, prove contract, continuation skill, and repository adapter, state:

```markdown
After proof, return the POC outcome to planning. KC Dev Flow does not create
downstream delivery work or preselect its profile. Planning decides whether a
new Development Brief exists; that item enters KC Dev Flow independently.
```

Keep `poc_outcome` direction, evidence, strongest limit, reversal fact, and
cleanup. Remove `poc_handoff` and `source: poc:<exact-source-id>` from the KC Dev
Flow contract.

- [ ] **Step 5: Rewrite the close-guard tests around the smaller command set**

Keep invalid-outcome and gate delegation cases. Delete downstream body and fake
`new` cases. Add this behavioral assertion after `consume`:

```python
calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
require(
    calls[-1]["argv"][:3] == ["gate", "consume", "poc123exact"]
    and all(call["argv"][:1] != ["new"] for call in calls),
    "POC consume created downstream work",
)
```

- [ ] **Step 6: Synchronize vendored files and run Task 2 tests**

Run:

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-manual-cycle-release-admission-path
cd "$WT" && rtk cmp kc-dev-flow/scripts/poc-close-guard.py docs/dev/_mods/poc-close-guard.py
cd "$WT" && rtk cmp kc-dev-flow/references/profiles/poc-exploration/base.md docs/dev/_mods/profiles/poc-exploration/base.md
cd "$WT" && rtk cmp kc-dev-flow/references/profiles/poc-exploration/prove.md docs/dev/_mods/profiles/poc-exploration/prove.md
cd "$WT" && rtk python3 kc-dev-flow/scripts/poc-close-guard.test.py
cd "$WT" && rtk python3 scripts/kc-dev-flow-contract-test.py
cd "$WT" && rtk python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py
```

Expected: all commands exit 0; no POC test invokes `spacedock new`; the
route-back mutant is rejected.

- [ ] **Step 7: Prepare the Task 2 commit for Captain confirmation**

Show the exact diff and named file list. After explicit confirmation only:

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-manual-cycle-release-admission-path
rtk git -C "$WT" add kc-dev-flow/references/profiles/poc-exploration/base.md kc-dev-flow/references/profiles/poc-exploration/prove.md kc-dev-flow/skills/continue-dev-flow/SKILL.md kc-dev-flow/scripts/poc-close-guard.py kc-dev-flow/scripts/poc-close-guard.test.py docs/dev/_mods/profiles/poc-exploration/base.md docs/dev/_mods/profiles/poc-exploration/prove.md docs/dev/_mods/poc-close-guard.py docs/dev/README.md scripts/kc-dev-flow-contract-test.py scripts/kc-dev-flow-minimal-stack-ablation.test.py
rtk git -C "$WT" commit -m "refactor(kc-dev-flow): return exploration outcomes to planning"
```

---

### Task 3: Validate the kernel claim and reshape Draft PR #306

**Files:**

- Verify: all files changed by Tasks 1 and 2
- Update after authorization: Draft PR #306 body only

**Interfaces:**

- Consumes: exact candidate revision produced by Tasks 1 and 2.
- Produces: bounded local proof for claimed outcome, minimal stack, without-it evidence, and an accurate Draft PR description.

- [ ] **Step 1: Run the complete relevant test stack**

Run:

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-manual-cycle-release-admission-path
cd "$WT" && rtk python3 scripts/kc-dev-flow-contract-test.py
cd "$WT" && rtk python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py
cd "$WT" && rtk python3 kc-dev-flow/scripts/profile-contract-loader.test.py
cd "$WT" && rtk python3 kc-dev-flow/scripts/poc-close-guard.test.py
cd "$WT" && rtk python3 kc-dev-flow/scripts/profile-spacedock-route.test.py
cd "$WT" && rtk python3 scripts/kc-dev-flow-loader-eval.test.py
cd "$WT" && rtk bash scripts/marketplace-verify.sh
cd "$WT" && rtk bash scripts/version-parity-check.sh
cd "$WT" && rtk bash scripts/skill-frontmatter-lint.sh
rtk git -C "$WT" diff --check
```

Expected: every command exits 0. No CI workflow or trigger changes are planned,
so this plan adds no incremental CI job.

- [ ] **Step 2: Audit the three kernel claims at the exact candidate**

Record only evidence that supports these bounded conclusions:

```text
Claimed outcome: provider-backed and standalone work both reach the same profile engine; POC/Spike returns to planning.
Minimum stack: no new plugin, profile, stage, schema, provider writer, or runtime coordinator exists.
Without-it: the four admission mutants and the exploration route-back mutant fail for their named reasons.
```

Check the exact diff for any remaining task/worktree/fresh-executor cardinality in
the portable kernel or skills. Delete any such portable rule or move a necessary
repository-specific fact to `docs/dev/README.md`.

- [ ] **Step 3: Verify clean ownership and prepare the Draft PR update**

Run:

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-manual-cycle-release-admission-path
rtk git -C "$WT" status --short --branch
rtk git -C "$WT" diff --stat origin/main...HEAD
rtk gh pr view 306 --json state,isDraft,headRefOid,url
```

Expected: only named task files are changed before commit; after authorized
commits, the worktree is clean and PR #306 remains open and Draft.

- [ ] **Step 4: Ask for delivery authorization**

Present the exact head, local test results, changed-file list, and the revised PR
claim. Ask separately for push and Draft PR body mutation. Do not mark Ready,
merge, release, or publish under this plan.
