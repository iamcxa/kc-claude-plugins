# Diagnostic Init Hook Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a fail-closed, repeated pre-navigation diagnostic script input to
the owned browser runtime, with immutable provenance, observed first-navigation
continuity, typed projection retrieval, scoped cleanup, and complete consumer
wiring.

**Architecture:** The runtime validates caller sources, creates isolated
runtime-owned wrappers and a private manifest, and passes wrappers through
`agent-browser 0.32` repeated `--init-script` flags. Each wrapper registers one
typed projection. Receipts retain hashes and statuses but no projection values;
the `diagnostic-projection` pseudo-command retrieves only schema-validated data.

**Tech Stack:** Node.js CommonJS, `node:test`, Bash/Markdown consumer contracts,
`agent-browser 0.32.0`, Chrome for Testing.

### Task 1: Fail-closed input validation

**Files:**
- Modify: `bin/e2e-browser-runtime.js`
- Modify: `compiler/test/browser-runtime-lifecycle.test.js`

**Step 1: Write failing tests**

Add tests that invoke repeated `--diagnostic-init-script` options and assert:

- relative paths fail before the fixture records an `open`;
- missing paths fail before `open`;
- directories fail before `open`;
- symlinks fail before `open`;
- a regular current-user-owned file reaches the owned `about:blank` launch.

**Step 2: Verify RED**

Run:

```bash
node --test compiler/test/browser-runtime-lifecycle.test.js
```

Expected: the regular-file case and validation diagnostics fail because the
runtime does not parse the option.

**Step 3: Implement minimal validation**

Extend `parseArgs()` with `diagnosticInitScripts: []`. Add descriptor-based
validation that returns:

```js
{
  sourcePath,
  basename,
  pathSha256,
  contentSha256,
  byteLength,
  device,
  inode,
  uid,
}
```

Run validation before executable discovery and browser invocation.

**Step 4: Verify GREEN**

Run the focused lifecycle test and `node --check
bin/e2e-browser-runtime.js`.

### Task 2: Runtime-owned wrappers, manifest, and mutation detection

**Files:**
- Modify: `bin/e2e-browser-runtime.js`
- Modify: `compiler/test/browser-runtime-lifecycle.test.js`
- Modify: `compiler/test/fixtures/agent-browser-032-fixture.js`

**Step 1: Write failing tests**

Add tests for:

- two scripts producing two repeated native `--init-script` flags plus the
  private probe;
- receipt provenance containing hashes but neither source contents nor raw
  absolute paths;
- source mutation after `about:blank` failing before the application URL;
- wrapper or manifest substitution failing closed.

**Step 2: Verify RED**

Run the focused lifecycle test and confirm the fixture sees only the existing
private probe.

**Step 3: Implement wrappers and manifest**

Create one mode-0600 wrapper per source and one mode-0600 manifest beside the
receipt. Authenticate manifest and wrapper paths before reads or deletion.
Revalidate caller descriptors and hashes before the first application
navigation. Pass the private probe first, then each wrapper as:

```text
--init-script <private-probe>
--init-script <diagnostic-wrapper-0>
--init-script <diagnostic-wrapper-1>
open
```

**Step 4: Verify GREEN**

Run the focused test, `git diff --check`, and a targeted scan proving caller
source paths are never passed to `unlink`.

### Task 3: Observation and typed projections

**Files:**
- Modify: `bin/e2e-browser-runtime.js`
- Modify: `compiler/test/browser-runtime-lifecycle.test.js`
- Modify: `compiler/test/fixtures/agent-browser-032-fixture.js`

**Step 1: Write failing tests**

Cover:

- every wrapper marker observed after first navigation;
- a missing marker records the script ordinal and fails infrastructure;
- invalid projection schema/value fails before any application conclusion;
- `diagnostic-projection` returns current allowlisted values but the receipt
  contains none of them;
- forced page reset remains a failure;
- two parallel runs retrieve different projections and closing one leaves the
  peer and both caller files intact.

**Step 2: Verify RED**

Run the focused lifecycle test.

**Step 3: Implement projection contract**

Generate a wrapper-local `publishDiagnosticProjection(schema, reader)` binding.
Accept only:

```text
boolean
integer with finite min/max bounds
enum with a non-empty bounded string set
sha256 with exactly 64 lowercase hex characters
```

Add the `diagnostic-projection` pseudo-command. It uses fixed
runtime-generated `eval` expressions, validates the returned object again in
Node, and prints one JSON document.

**Step 4: Verify GREEN**

Run lifecycle, ownership, and browser-runtime contract tests.

### Task 4: Consumer and compiler wiring

**Files:**
- Modify: `agents/e2e-mapper.md`
- Modify: `agents/e2e-test-runner.md`
- Modify: `agents/e2e-flow-verifier.md`
- Modify: `agents/e2e-debug-observe.md`
- Modify: `skills/e2e-map/SKILL.md`
- Modify: `skills/e2e-test/SKILL.md`
- Modify: `skills/e2e-flow/SKILL.md`
- Modify: `skills/e2e-walkthrough/SKILL.md`
- Modify: `skills/e2e-walkthrough/reference.md`
- Modify: `skills/e2e-debug/SKILL.md`
- Modify: `compiler/codegen.js`
- Modify: `compiler/test/browser-runtime-contract.test.js`
- Modify: `compiler/test/codegen.test.js`
- Modify: `references/commands.md`
- Modify: `references/agent-teams.md`

**Step 1: Write failing contract tests**

Require every browser consumer to:

- declare optional `diagnostic_init_scripts`;
- render each absolute path as a repeated runtime option;
- preserve the field in Teams/re-run handoffs;
- prohibit raw `agent-browser --init-script` and `addinitscript`.

Require compiled flows to translate a newline-delimited
`E2E_DIAGNOSTIC_INIT_SCRIPTS` environment value into repeated runtime arguments
without shell evaluation.

**Step 2: Verify RED**

Run:

```bash
node --test \
  compiler/test/browser-runtime-contract.test.js \
  compiler/test/codegen.test.js
```

**Step 3: Implement the shared contract**

Keep the option absent for ordinary runs. Treat paths as data, reject relative
or empty entries, and route them only through the runtime prefix.

**Step 4: Verify GREEN**

Run the focused contract/codegen suites and generated Bash syntax checks.

### Task 5: Documentation, real probe, and full verification

**Files:**
- Modify: `docs/recording-evidence.md`
- Modify: `docs/commands.md`
- Modify: `README.md`
- Modify: `compiler/test/browser-runtime-lifecycle.test.js`

**Step 1: Document safety and usage**

Document the script API, typed projection, field-specific failure states, and
the prohibition on uploading or committing profiles, cookies, tokens, storage
dumps, raw HAR, or credential-bearing screenshots.

**Step 2: Run a real 0.32 local-page probe**

Start an owned local HTTP server serving a page whose inline application script
reads a marker installed by the diagnostic init script. Open it through the
runtime with real `agent-browser 0.32.0` and Chrome for Testing, retrieve
`diagnostic-projection`, and verify:

- the marker existed before application code;
- the receipt reports every script observed;
- the receipt contains no projection values;
- close removes runtime-owned files and leaves the caller script.

**Step 3: Run complete verification**

```bash
npm test
npm run lint
node --check bin/e2e-browser-runtime.js
./scripts/version-parity-check.sh
npm pack --dry-run --json
```

Run `scripts/version-parity-check.sh` from the repository root. Record existing
lint warnings separately from errors.

**Step 4: Review and publish**

Run an exact-head code review, resolve actionable findings, commit only named
files, push, and open a Draft PR that closes #110. Convert to ready only after
exact-head CI is green.
