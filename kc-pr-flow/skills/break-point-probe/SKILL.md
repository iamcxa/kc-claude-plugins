---
name: break-point-probe
description: Use when verifying that a fix actually reaches the bug's break-point in the real runtime path — not just at unit-test level. Primary trigger is bugfix / cross-stack PR review (invoked by kc-pr-review). Also invoke standalone when pressure-testing a fix claim, pre-merge verification of cross-layer wiring, or debugging "why is this still broken". Output is a strict YAML contract declaring precision level (A/B/C/D), verified vs unverified failure-chain steps, residual uncertainty, and recommended human probes. Designed to prevent silent verification failure where an agent reports "verified" without actually exercising the runtime path.
---

All text output follows unified language preference.

## Purpose

Unit tests prove a function is correct **in isolation**. They do not prove the function is **on the runtime path** of the bug. Approving a bugfix PR based on unit tests alone is review theater when:

- The fix lives deep in a transform pipeline that has upstream normalization
- The frontend might preprocess the input before it ever reaches the backend
- There are multiple code paths that generate the same artifact, and the fix only touches one
- The bug's observable symptom depends on an external system (dbt, Stripe, Snowflake, etc.)

This skill produces **auditable evidence** of what was actually verified, in which runtime steps, at which precision level. The output contract makes it **impossible for the agent to silently under-verify** — every unverified step must be declared.

## When to invoke

Invoke when ANY of these hold:
- PR body contains an unchecked "manual verification" / "QA" / "UAT" checkbox
- PR archetype is `bugfix` AND the diff spans ≥ 2 layers (UI ↔ backend, backend ↔ external system, domain ↔ storage)
- PR archetype is `cross-stack`
- User asks "is this fix actually wired?" / "verify the break-point" / "pressure-test this fix"
- A previous review claimed APPROVE based only on unit tests and the fix touches a transform or wiring path

Skip when:
- Docs-only PR
- Refactor PR (behavioral equivalence is the review focus, there's no "break-point")
- Style / lint / formatting PR
- PR is purely internal utility with no upstream/downstream callers in production path

## Input

Accept any of:
- PR context: `pr_number`, `owner_repo`, `diff`, `pr_body`, `linked_issue_body`
- Free-form bug description: symptom + suspected fix location

## Process

### Step 1 — Build the failure chain

Read diff + PR description + linked issue. Trace the bug's **full path from user action to observable symptom**. Write it as an ordered list.

Example (DRC-3288, PR #1241):

```
1. User types "xxx.snowflakecomputing.com" in Snowflake Account field       [layer: ui]
2. Frontend POST to /warehouse-connections with config dict                  [layer: api]
3. Backend encrypts + stores config in DB                                    [layer: storage]
4. Later, recce session launch fetches config via get_warehouse_connection   [layer: domain]
5. warehouse_config_to_profile_yml() generates profiles.yml                  [layer: domain]  ← FIX HERE
6. Recce instance container reads profiles.yml                               [layer: infra]
7. dbt-snowflake appends ".snowflakecomputing.com" to account field          [layer: external]
8. Connects to "xxx.snowflakecomputing.com.snowflakecomputing.com" → fails   [layer: external]  ← SYMPTOM
```

**The fix lives at step 5. The bug manifests at step 8.**

### Step 2 — Identify the break-point

Point at the single step where the fix operates. Cite `file:line`.

```
break_point:
  file: api_server/apis/utils/warehouse.py
  line: 49
  description: Strip .snowflakecomputing.com suffix from account before yaml.dump
```

### Step 3 — Classify unit-test coverage vs runtime gap

For each step in the failure chain, answer: **is this step exercised by the PR's unit tests, or only inferred by reading code?**

```
unit_coverage:
  covered_steps: [5]                 # unit tests call warehouse_config_to_profile_yml directly
runtime_gap:
  uncovered_steps: [1, 2, 3, 4, 6]   # frontend wiring, API path, storage round-trip, caller wiring, container read
  reason: |
    Unit tests construct the config dict inline and call warehouse_config_to_profile_yml
    directly. They do not exercise the API POST path, storage encryption round-trip, or
    the caller wiring in recce_task_func.py / recce_share_instance_func.py.
```

### Step 4 — Select and execute probe

Use the **precision ladder** (see `reference/precision-ladder.md`). Choose the highest level you can execute given available tooling/env:

| Level | Method | Who can run |
|-------|--------|-------------|
| A | Read diff + trace caller references | Any agent, any context |
| B | Run PR's own tests + grep all call sites of changed symbols | Any agent with repo access |
| C | Execute runtime probe against local stack (curl / direct invocation) | Agent when local stack is warm |
| D | Full external E2E (connects to real third-party system) | Human only; never auto-execute |

**Execution rules:**

1. **Always execute A.** Read the diff, grep all callers, verify the fix is on the hot path.
2. **Always execute B if repo is local.** Run `pytest`/`vitest` on PR's changed tests, grep all consumers of changed symbols.
3. **Attempt C if autodetected feasible.** Check for local stack via health endpoint or port probe. If reachable, build the minimal probe request and execute it. If not reachable, gracefully degrade to B.
4. **Never auto-execute D.** Always recommend to human.

When a higher level is attempted but fails (e.g., C probe timeout, credential missing, endpoint 500), **downgrade honestly**: declare the lower level actually achieved + record failure reason under `probe_decision.degrade_reason`.

### Step 5 — Emit output contract

**Mandatory fields — no field may be omitted:**

```yaml
break_point:
  file: <path>
  line: <line>
  description: <what the fix does at this point>

failure_chain:
  - step: 1
    description: <ordered user→symptom step>
    layer: ui | api | domain | storage | infra | external

unit_coverage:
  covered_steps: [<indices into failure_chain>]

runtime_gap:
  uncovered_steps: [<indices>]
  reason: <why unit tests don't cover these>

probe_decision:
  verified_at: A | B | C | D
  method: <description of what was actually run>
  evidence:
    - <tool output excerpt, file:line ref, or command output>
  degrade_reason: <set only if a higher level was attempted and failed; otherwise omit>

residual_uncertainty:
  - assumption: <what could still be wrong in production>
    probability: low | medium | high
    failure_mode: <what happens if assumption is false>

recommended_human_probe:
  - action: <concrete command or step-by-step>
    covers_steps: [<failure_chain indices>]
    cost: <time estimate>
    confidence_gain: <A→B | B→C | C→D>
```

**Silent-failure prevention (HARD rules):**

- `verified_at` MUST match what was actually executed. Declaring `C` without running a runtime probe = lying. If audit finds mismatch, skill is considered broken.
- `residual_uncertainty` MUST be non-empty unless `verified_at == D` with all failure_chain steps covered. Empty uncertainty claims omniscience.
- `recommended_human_probe` MUST be non-empty unless `verified_at == D`. If the agent can't suggest a human probe, it must declare "no further verification achievable without <specific resource>" as the single recommendation.
- If the agent CANNOT produce any of these fields honestly, it must emit `abort: <reason>` and nothing else. Partial output is worse than no output.
- **Tool-blocked ≠ stack cold.** If `curl` output is empty or literally `"FAILED: curl"`, that means sandbox denial, not a cold stack. Fall back to `python3 -c "import urllib.request; ..."` before degrading. `degrade_reason` must distinguish `tool_blocked`, `stack_cold`, and `stack_hung` (listener exists, HTTP times out) — never conflate them.
- **Direct invocation requires `c_scope_note`.** When Level C is achieved via direct Python/Node import instead of API POST, `probe_decision.c_scope_note` is mandatory and must state which failure_chain steps remain inferred (typically: API POST wire, storage round-trip, container read). Omitting the note inflates perceived coverage.
- **Running server must match probed branch.** Before running Level C via API POST, verify the running server's checkout has the fix (`git log --oneline -1` in its worktree, or version-endpoint check). If stale, either (a) restart server with correct branch, (b) fall through to direct invocation with `c_scope_note`, or (c) declare `degrade_reason: running_server_stale_branch`.
- **Direct-invocation working-tree must match probed branch (by hash).** Python/Node `import` resolves from filesystem, NOT from `git branch --show-current`. Earlier `git checkout <other-branch> -- .` overlays or forgotten stashes can silently make you test the wrong (or accidentally right) code. Before Level C direct invocation, run:
  ```bash
  # For each file touched by the fix:
  git hash-object <file>                              # working tree hash
  git rev-parse <expected-branch>:<file>              # expected branch hash
  # They MUST be equal. If not, state what's actually on disk.
  ```
  If hashes diverge, either (a) clean checkout via `git worktree add .worktrees/probe-<name> <expected-branch>` and re-run probe from there, or (b) declare `degrade_reason: working_tree_differs_from_probed_branch` + dump the actual hash as evidence. **Never silently assume working tree == branch.** This is how probes accidentally pass (or fail) against phantom code.

### Step 6 — Return

Return the YAML output to the caller (typically kc-pr-review). The caller decides how to surface to the user (inline in review body, separate comment, or blocking gate).

## Output rendering (when invoked standalone, not via kc-pr-review)

When called directly by the user (not from a parent skill), after emitting YAML also display a human-readable summary:

```
## Break-point probe result

Break-point: <file>:<line>
Failure chain: N steps total
Runtime gap: N steps unverified by unit tests

Probe level achieved: <A|B|C|D>
Method: <summary>

Residual uncertainty:
- <assumption> (probability: <level>) → <failure_mode>

Recommended human follow-up:
- <action> (cost: <estimate>, gains: <level up>)
```

## Rules

- **Never claim a probe level you didn't execute.** Evidence must match level.
- **Empty `residual_uncertainty` is forbidden at levels A/B/C.** There is always something unverified short of full external E2E.
- **Degradation is honest, not shameful.** "Attempted C, stack not warm, achieved B" is correct output.
- **No scope creep.** This skill verifies ONE break-point per invocation. If the PR has multiple independent fixes, invoke once per fix and combine outputs in the caller.
- **Don't propose fixes.** This skill verifies coverage, not correctness. If the probe reveals a bug, report it; don't design the fix here.
- **Probe recipes are additive.** If `.claude/break-point-probes/<domain>.md` exists in the target repo, use it as a template for Level C. Absent a recipe, construct probe ad hoc from PR context.
- **Stay within PR scope.** Don't probe paths unrelated to the diff just because the failure chain touches them.

## Reference documents

- `reference/precision-ladder.md` — detailed guidance for each probe level, including stack-warm detection and recipe template
- `reference/case-study-drc-3288.md` — walkthrough of PR #1241 showing the pattern in practice

## Invocation by kc-pr-review

kc-pr-review invokes this skill at Step 4.5p (parallel with pre-scan and agent dispatch). Output merges into Step 5 classification as source `PROBE`, and appears in the Step 6 draft under a "Break-point Coverage" section. `residual_uncertainty` items are surfaced to the user at the confirmation gate — user can choose to post them as advisory in the review body or dismiss.
