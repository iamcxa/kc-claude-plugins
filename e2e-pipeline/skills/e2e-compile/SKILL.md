---
name: e2e-compile
description: Use when compiling E2E flow YAML to standalone bash test scripts. Triggers on "/e2e-compile", "compile flow", "recompile flow".
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
| `--coverage` | Produce static coverage report (elements reached vs verified). Single flow: the data arrives in the JSON document's `coverage` key. Batch (`--all`): the batch document has no `coverage` key, so no coverage data reaches the skill |
| `--coverage-output <dir>` | Directory for coverage JSON when the compiler is invoked directly. The skill's `--json` path writes no coverage files, so nothing is written here via `/e2e-compile` |

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

After locating the binary, verify npm dependencies are installed:

```bash
node -e "require('<compiler_dir>/compiler/compiler.js')" 2>&1
```

Where `<compiler_dir>` is the parent directory of `bin/`. If this fails with `Cannot find module`, stop: "Compiler dependencies missing. Run `npm install` in `<compiler_dir>` first."

## Phase 2 — Invoke Compiler

Run via Bash tool from the **project root** (so default directory paths resolve correctly).
Always add `--json` — it is this skill's internal contract with the compiler (a single parseable
document on stdout, with repair candidates where the compiler already has them), not a
user-facing option; humans invoking the compiler directly still get the prose default.

**Single flow:**
```bash
node "<compiler_path>" --json <flow-name>
```

**Batch:**
```bash
node "<compiler_path>" --json --all
```

**Dry-run:**
```bash
node "<compiler_path>" --json --dry-run <flow-name>
```

**Verbose (add to any mode):**
```bash
node "<compiler_path>" --json --verbose <flow-name>
node "<compiler_path>" --json --verbose --all
```

Default directories (resolved relative to project root):
- Flows: `.claude/e2e/flows`
- Mappings: `.claude/e2e/mappings`
- Output: `.claude/e2e/compiled`

**Note:** Flow files may contain a `preconditions:` top-level block (data readiness checks executed by e2e-test skill). The compiler ignores this block — it is not compiled into the output script.

## Phase 3 — Present Results

For the two supported invocations (`--json <flow>` and `--json --all`) stdout carries one JSON
document: single flow `{ok, flow, stats, errors, coverage}`; `--all` `{ok, flows: [...], summary:
{passed, failed}}`, each entry shaped like the single-flow document, plus an optional top-level
`errors` array when the batch could not start. Parse it and map fields to a conversational
presentation — no prose regex-parsing needed. **If stdout does not parse as JSON** — a usage error
such as `--json --help` or a malformed flag prints prose there instead — fall back to stderr and
the exit code rather than assuming the run succeeded:

| Field | Presents as |
|-------|-------------|
| `ok: true` | `Compiled: <flow>` / `Output: .claude/e2e/compiled/<flow>.sh` / `Steps: stats.total (stats.activeExpects expects active)` |
| `ok: false` with deferred assertion errors | Present as compilation failures and show the raw unsupported `expect:` text plus repair guidance |
| `stats.notAutomatedExpects > 0` | Add: `Not automated: N expects declared with not_automated` |
| `ok: false` | `Compilation failed: <flow>`, then one line per `errors[]` entry |
| `errors[].message` | The line text for that error |
| `errors[].candidates` non-empty | Append: `did you mean: <candidates.join(', ')>?` — a repairable error (the compiler already found these); when empty, no such name exists in the mapping at all |
| `coverage` non-null | `Coverage: X/Y elements (Z%) verified`; list `reached_but_not_verified` / `untouched` from `coverage.elements` |

After a successful single-flow compile, mention: "You can run the compiled script directly: `bash .claude/e2e/compiled/<flow-name>.sh`"

Batch (`--all`): present as `Batch compilation complete: summary.passed OK, summary.failed
failed`, then list each `flows[]` entry's `flow` name under "Succeeded" (`ok: true`) or under
"Failed" with its first `errors[].message` (`ok: false`). If the document carries a **top-level**
`errors` array, the batch never started — present those messages instead of the counts.

An **empty** flows directory returns `{ok: true, flows: [], summary: {passed: 0, failed: 0}}`,
exit 0 — present as: "No flow files found in `.claude/e2e/flows/`. Create flows with `/e2e-flow`
(from a plan or spec) or `/e2e-walkthrough` (interactive browser exploration)."

A **missing or unreadable** flows directory is a different result: `{ok: false, flows: [],
summary: {passed: 0, failed: 0}, errors: [{message}]}`, exit 1 — present the `errors[].message`
(it names the path it could not read). Do not report this as "no flows found": that would hide a
mistyped `--flows-dir` as an empty project.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Element not in mapping | Run `/e2e-map` to update the mapping, then recompile |
| Flow uses v1 format (`app:`, `name:`) | Migrate to v2: `app:`→`mapping:`, `name:`→`id:` |
| No mapping file | Run `/e2e-map` first to create `.claude/e2e/mappings/*.yaml` |
| `--dry-run` with `--all` | Dry-run works with `--all`; validation runs per flow |
| Recompile overwrites eval patches | Login flows with manual `agent-browser eval` workarounds (for headless CI) are overwritten by recompile. **Re-apply eval patches after recompiling `gate-login-flow`**. See [Headless CI Limitations](../../docs/ci-integration.md#headless-ci-limitations). |
| Compiled script fails in CI but passes locally | Playwright `fill`/`click`/`is visible` fail in headless Chrome on Linux CI. Visibility checks use `_poll_snapshot_contains` (auto-generated). Fill/click need manual eval patches for login flows. |
| `combobox` pattern too broad in a11y grep | `[role="combobox"][aria-label="..."]` CSS attribute selector converts to grep pattern on the `aria-label` value. If aria-label is absent, pattern falls back to `combobox` which matches any combobox — acceptable when page has only one; add `aria-label` or `data-testid` to the element for disambiguation. Former `find role combobox --name "..."` as a `selector:` value is DEPRECATED (subcommand chain — PR #8). Former `role=combobox >> nth=0` form is BANNED (BANNED — see e2e-pipeline/scripts/lint-mapping.sh). |
| `Cannot find module` on first run | npm dependencies not installed. Run `npm install` in the e2e-pipeline plugin directory. |
| Unsupported action type (e.g., `Drag`, `Hover`) | Compiler emits `# Unknown action type` comment in output script. Supported types: Navigate, Click, Fill, Wait, Take snapshot, Verify, Execute external, Verify external, and typed `capture-url-query`. Rewrite the step using a supported action or use `Execute external` with a CLI command. Runtime values and ordered HTTP finalizers use `runtime_values`/`runtime_ref`/`finally`. |
