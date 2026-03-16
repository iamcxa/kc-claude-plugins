---
name: e2e-compile
description: Use when compiling E2E flow YAML files to standalone bash test scripts — invoke with "/e2e-compile <flow-name>" or "/e2e-compile --all". Triggers on "/e2e-compile", "compile flow", "e2e compile", "compile the flow", "generate test script", "compile e2e", "recompile flow".
---

# E2E Compile — Flow YAML to Bash Script

Compile E2E flow YAML files into standalone bash test scripts using the e2e-compile CLI.

## Invocation

```
/e2e-compile [flow-name|--all] [--dry-run] [--verbose] [--coverage] [--coverage-output <dir>]
```

| Arg | Effect |
|-----|--------|
| `flow-name` | Compile a single flow (without `.yaml` extension) |
| `--all` | Compile every flow in `.claude/e2e/flows/` |
| `--dry-run` | Validate flow + mapping coherence without writing output |
| `--verbose` | Show resolved step details (operands, expects) during compilation |
| `--coverage` | Produce static coverage report (elements reached vs verified) after compilation |
| `--coverage-output <dir>` | Output directory for coverage JSON (default: `.claude/e2e/coverage`) |

## Prerequisites

1. **Flow files** in `.claude/e2e/flows/*.yaml` — run `/e2e-flow` or `/e2e-walkthrough` to create them
2. **Mapping files** in `.claude/e2e/mappings/*.yaml` — run `/e2e-map` first if missing

## Phase 0 — Parse Arguments

Determine compilation mode from the user's request:

- Explicit flow name → single flow mode
- `--all` → batch mode (all flows in `.claude/e2e/flows/`)
- `--dry-run` → validation-only mode (no output file written)
- `--verbose` → add step detail output during compilation (combinable with any mode)

If no flow name and no `--all`: show help and stop.

## Phase 1 — Locate Compiler

Find the `e2e-compile.js` CLI binary:

1. Check `${CLAUDE_PLUGIN_ROOT}/bin/e2e-compile.js` (set when plugin is loaded)
2. If `CLAUDE_PLUGIN_ROOT` is not set, search installed locations:

```bash
find ~/.claude/plugins -name "e2e-compile.js" -path "*/e2e-pipeline/bin/*" -print -quit 2>/dev/null
```

If the binary is not found, stop: "Cannot find e2e-compile.js. Ensure the e2e-pipeline plugin is installed."

## Phase 2 — Invoke Compiler

Run via Bash tool from the **project root** (so default directory paths resolve correctly):

**Single flow:**
```bash
node "<compiler_path>" <flow-name>
```

**Batch:**
```bash
node "<compiler_path>" --all
```

**Dry-run:**
```bash
node "<compiler_path>" --dry-run <flow-name>
```

**Verbose (add to any mode):**
```bash
node "<compiler_path>" --verbose <flow-name>
node "<compiler_path>" --verbose --all
```

Default directories (resolved relative to project root):
- Flows: `.claude/e2e/flows`
- Mappings: `.claude/e2e/mappings`
- Output: `.claude/e2e/compiled`

## Phase 3 — Present Results

Parse stdout/stderr from the compiler and present conversationally.

### Single flow — success

Compiler stdout:
```
Compiled: N steps, M expects active, K expects deferred (Phase 2)
OK: <flow-name>
```

Present as:
```
Compiled: <flow-name>
  Output:   .claude/e2e/compiled/<flow-name>.sh
  Steps:    N (M expects active)
  Warnings: K expects deferred (unrecognized format — will emit TODO echo at runtime)
```

Omit the "Warnings" line entirely when deferred count is 0.

After success, mention: "You can run the compiled script directly: `bash .claude/e2e/compiled/<flow-name>.sh`"

### Single flow — error

Compiler writes ERROR lines to stderr. Present them clearly:
```
Compilation failed: <flow-name>
  ERROR: <message from stderr>
```

### Batch — success

Compiler stdout (one line per flow):
```
OK: flow-a
FAIL: flow-b — element 'bar' not found in mapping
Batch complete: N OK, M failed
```

Present as:
```
Batch compilation complete: N OK, M failed

  Succeeded (N):
    - flow-a
    - flow-c

  Failed (M):
    - flow-b — element 'bar' not found in mapping
```

### Dry-run

Compiler writes to stderr: `DRY RUN: would write <path> (N bytes, M steps)`

Present as:
```
Dry-run: <flow-name>
  Validation: PASS (no output file written)
  Would write: .claude/e2e/compiled/<flow-name>.sh (N steps)
```

For dry-run errors, present the ERROR lines from stderr.

### No flows found

If the flows directory has no YAML files, suggest next steps:
"No flow files found in `.claude/e2e/flows/`. Create flows with `/e2e-flow` (from a plan or spec) or `/e2e-walkthrough` (interactive browser exploration)."

### Coverage report (when --coverage)

Compiler stdout appends coverage summary after compilation output:
```
Compiled: N steps, M expects active, K expects deferred (Phase 2)
Coverage: X/Y elements (Z%) verified across 1 flow
  Reached (but not verified): elem_a, elem_b (N elements)
  Untouched: elem_c, elem_d (N elements)
OK: <flow-name>
```

Present as:
```
Compiled: <flow-name>
  Output:   .claude/e2e/compiled/<flow-name>.sh
  Steps:    N (M expects active)
  Coverage: X/Y elements (Z%) verified
    Reached but not verified: elem_a, elem_b
    Untouched: elem_c, elem_d
  Coverage JSON: .claude/e2e/coverage/coverage.json
```

If coverage regression warning appears (::warning:: line), present prominently:
"Warning: Coverage dropped N% from previous run (was X%, now Y%)"

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Element not in mapping | Run `/e2e-map` to update the mapping, then recompile |
| Flow uses v1 format (`app:`, `name:`) | Migrate to v2: `app:`→`mapping:`, `name:`→`id:` |
| No mapping file | Run `/e2e-map` first to create `.claude/e2e/mappings/*.yaml` |
| `--dry-run` with `--all` | Dry-run works with `--all`; validation runs per flow |
