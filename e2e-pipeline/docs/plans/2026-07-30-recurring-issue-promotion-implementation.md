# Recurring Pipeline Issue Promotion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a fail-closed, opt-in mechanism that promotes a pipeline defect
to one deduplicated GitHub issue after two distinct E2E runs observe it.

**Architecture:** A pure CommonJS module owns candidate validation,
fingerprinting, observation persistence, threshold evaluation, and issue body
rendering. A small Node CLI owns configuration and best-effort GitHub calls.
`e2e-test` invokes the CLI only for concrete pipeline-defect candidates.

**Tech Stack:** Node.js built-ins, `node:test`, GitHub CLI, Markdown skill
contracts.

### Task 1: Candidate and Observation Contract

**Files:**
- Create: `compiler/issue-promotion.js`
- Create: `compiler/test/issue-promotion.test.js`

1. Write failing tests for strict `pipeline-defect` input and unsafe-text
   rejection.
2. Run `node --test compiler/test/issue-promotion.test.js` and verify RED
   because the module does not exist.
3. Implement the minimum validator and stable SHA-256 fingerprint.
4. Add a failing test proving two files with the same run ID count once.
5. Implement atomic per-run observation files and distinct-run counting.
6. Run the focused test and verify GREEN.

### Task 2: Proposal and GitHub Deduplication

**Files:**
- Modify: `compiler/issue-promotion.js`
- Create: `bin/e2e-issue-promotion.js`
- Create: `compiler/test/issue-promotion-cli.test.js`

1. Write failing CLI tests proving the default mode writes a proposal without
   invoking `gh`.
2. Implement argument parsing, config loading, and proposal output.
3. Write failing tests proving `auto` requires config authorization and
   searches all issue states before creating.
4. Implement label setup, fingerprint-marker deduplication, closed-issue
   suppression, creation, and best-effort remote failure output.
5. Run both focused test files and verify GREEN.

### Task 3: Agent Contract

**Files:**
- Create: `references/issue-promotion.md`
- Modify: `skills/e2e-test/SKILL.md`
- Modify: `compiler/test/browser-runtime-contract.test.js`

1. Add a failing structural contract test for the post-run promotion step,
   candidate exclusions, two-run threshold ownership, and explicit auto-mode
   authorization.
2. Run the structural test and verify RED.
3. Add the concise shared reference and the `e2e-test` post-run invocation.
4. Run the structural test and verify GREEN.

### Task 4: Package and Documentation

**Files:**
- Modify: `package.json`
- Modify: `docs/self-improvement.md`
- Modify: `references/doc-sync-context.md`

1. Add the executable to the package bin map.
2. Document pipeline-defect promotion beside D1/D2 capture without changing
   their existing semantics.
3. Record the new reference in the doc-sync context.

### Task 5: Verification

1. Run:
   `node --test compiler/test/issue-promotion.test.js compiler/test/issue-promotion-cli.test.js compiler/test/browser-runtime-contract.test.js`.
2. Run `npm test`.
3. Run `npm run lint -- --max-diagnostics=20`.
4. Run `git diff --check`.
5. Inspect `git status --short` and `git diff --stat`.
6. Present the exact touched-file list and request commit authorization before
   staging any file.
