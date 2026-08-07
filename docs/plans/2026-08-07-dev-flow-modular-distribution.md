# Dev Flow Modular Distribution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace binding-based `kc-dev-flow` distribution with locally vendored
kernel and stage-selected policy mods, including cursor-based debrief improvement
coordination.

**Architecture:** Preserve the current canonical proof kernel and absolutes checker.
Change adoption and continuation around it: README Local Profile binds authority,
`_mods/` presence records adoption, stage lists select policy, and
`_improvements/state.yaml` prevents repeated debrief analysis.

**Tech Stack:** Markdown skills and references, Python package-contract tests, shell
test runners, git worktrees.

### Task 1: Make the package contract describe the new product

**Files:**

- Modify: `scripts/kc-dev-flow-contract-test.py`
- Delete later: `scripts/verify-binding.test.sh`

1. Add assertions requiring `references/project-context-maintenance.md`, Local
   Profile adoption, stage `Policy mods`, local kernel reads, and improvement cursor
   semantics.
2. Add assertions forbidding the binding template, verifier, and their references.
3. Run `./scripts/kc-dev-flow-contract-test.py` and verify RED reports the legacy
   binding surface and missing project-context mod.
4. Commit the RED contract separately if the repository hooks allow a failing test
   commit; otherwise retain the observed failure in the execution record.

### Task 2: Preserve the canonical kernel and add the maintenance policy

**Files:**

- Modify: `kc-dev-flow/references/kernel.md`
- Create: `kc-dev-flow/references/project-context-maintenance.md`
- Modify: `kc-dev-flow/references/absolutes.registry`
- Modify: `docs/dev/_mods/kernel.md`

1. Patch only the kernel introduction, continuation, and self-improvement ownership;
   retain the existing authority and proof clauses.
2. Add the Claude-approved project-context maintenance policy.
3. Update the self-adopted kernel byte-for-byte from the canonical file.
4. Run the absolutes checker, observe its expected RED on changed/unregistered blocks,
   update the registry, and rerun to GREEN.

### Task 3: Replace binding adoption with vendored-policy adoption

**Files:**

- Modify: `kc-dev-flow/skills/adopt-dev-flow/SKILL.md`
- Modify: `kc-dev-flow/README.md`
- Delete: `kc-dev-flow/assets/kernel-binding.template.yaml`
- Delete: `kc-dev-flow/scripts/verify-binding.py`
- Delete: `scripts/verify-binding.test.sh`

1. Use the existing skill as the RED baseline on a repository with Local Profile and
   vendored mods but no binding; record that it incorrectly routes back to adoption.
2. Rewrite audit/adopt/upgrade around Local Profile and explicit byte-for-byte
   vendoring.
3. Remove legacy binding assets and verifier tests.
4. Run the package contract and frontmatter lint to GREEN.

### Task 4: Make continue load local policy and consume debriefs once

**Files:**

- Modify: `kc-dev-flow/skills/continue-dev-flow/SKILL.md`
- Modify: `scripts/kc-dev-flow-contract-test.py`

1. Add a pressure fixture with two processed debriefs, no new debrief, a local kernel,
   and stage policy mods. Verify the old skill requests a binding or repeats analysis.
2. Specify discovery, local kernel loading, stage-lazy policy loading, and fail-closed
   missing-policy behavior.
3. Define the minimal `_improvements/state.yaml` receipt and cursor transition,
   including no-op behavior on a second run.
4. Forward-test the new skill on the same fixture and verify it resumes work without
   re-proposing an old finding.

### Task 5: Migrate this repository's self-adoption

**Files:**

- Modify: `docs/dev/README.md`
- Delete: `docs/dev/kernel-binding.yaml`
- Modify as required: `scripts/dev-flow-work-context-check.py`
- Modify as required: `scripts/dev-flow-work-context-check.test.sh`

1. Replace the binding section with a Local Profile preserving the same authorities.
2. Remove verifier commands and the binding file.
3. Keep source-package policy and adopter policy separate; do not auto-adopt
   project-context maintenance unless stage lists explicitly select it.
4. Run the repository's dev-flow checks and confirm no legacy binding reference
   remains.

### Task 6: Verify the complete package

**Files:**

- Modify only if a failing gate identifies a scoped defect.

1. Run `./scripts/kc-dev-flow-contract-test.py`.
2. Run `./scripts/skill-frontmatter-lint.sh`.
3. Run `./scripts/marketplace-verify.sh`.
4. Run `./scripts/version-parity-check.sh`.
5. Run `git diff --check` and inspect the exact `origin/main...HEAD` diff.
6. Obtain a fresh read-only review, disposition every finding, and rerun affected
   gates.

### Task 7: Prepare adopter refit handoff

**Files:**

- Create: `.context/relay-dev-flow-refit.md` (gitignored handoff only)

1. Record that relay must replace its compressed kernel with the canonical package
   kernel after this feature lands.
2. Name the required Local Profile and stage-policy parity checks.
3. Do not mutate the relay worktree from this branch.

