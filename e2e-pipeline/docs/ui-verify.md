# UI Verify

Declarative static-UI difference check. Use when you need to confirm that a known DOM element has the expected computed CSS — design tokens, theme changes, layout dimensions, pseudo-element styles. Pass/fail per check, machine-judged via string equality.

## When to Use

| Skill | What it compares | Judgment |
|-------|------------------|----------|
| **`ui-verify`** (this) | **Static UI** — computed styles, tokens, pseudo-elements, dimensions | Machine (equality) |
| [`e2e-flow`](commands.md) / [`e2e-test`](commands.md) | **Dynamic behavior** — navigation, state transitions, user actions | Machine (flow asserts) |
| [`e2e-walkthrough`](commands.md) | Subjective visual QA, exploration, demo recording | Human |

| Question | Skill |
|----------|-------|
| "Did the sidebar bg change to `#FAFAF8`?" | **`ui-verify`** |
| "Clicking Submit navigates to `/success`?" | `e2e-flow` |
| "Does the new layout look right?" | `e2e-walkthrough` |

## Scope

**In scope** (Mode B only):

- Fixed selectors × fixed expected computed-style values
- `getComputedStyle(selector)[property]` equality checks
- Pseudo-element (`::before`, `::after`) computed value checks
- Optional pre-check setup actions (`goto`, `click`, `fill`, `wait`, `press`)
- Per-check screenshot capture + pass/fail report

**Out of scope** — use `agent-browser` REPL directly:

- Dynamic queries (find any element with bg = X, walk parent chain, `elementFromPoint`)
- Computed-style forensics across many candidate elements
- CSS specificity wars / injected-style inspection
- Any check where the selector is not known upfront

If the verification requires forensics → defer to `agent-browser`. `ui-verify` is for cases where you already know **which element** to check and **what value** to expect.

## Pipeline Position

```
/e2e-map       → mapping.yaml               (map UI + auth)
/ui-verify     → ui-verify.yaml + report    (check computed styles)
/e2e-flow      → flow.yaml                  (dynamic behavior)
/e2e-test      → flow replay + report
```

`ui-verify` reuses `.claude/e2e/mappings/<app>.yaml` for `base_url` and `auth.test_accounts` — same convention as the rest of the pipeline.

## Invocation

```
/ui-verify <yaml-path> [--no-screenshot] [--bail-on-first-fail]
```

| Arg | Effect |
|-----|--------|
| `<yaml-path>` | Path to ui-verify YAML (e.g. `.claude/e2e/ui-verify/sec-19-layout-tokens.yaml`) |
| `--no-screenshot` | Skip per-check screenshots (faster, less artifact) |
| `--bail-on-first-fail` | Stop on first failed check (default: run all checks, report aggregate) |

## Prerequisites

1. `agent-browser` installed globally
2. Dev server running at the mapping's `base_url`
3. Mapping file exists at `.claude/e2e/mappings/<mapping>.yaml` with an `auth` block

## YAML Schema

```yaml
version: 1
mapping: secha-office           # name (without .yaml) of mapping in .claude/e2e/mappings/
auth_account: tenant_admin      # key in mapping.auth.test_accounts; omit → no login
title: "SEC-19 Layout chrome tokens"

setup:                          # optional pre-check actions, run once after login
  - action: goto
    url: "/dashboard/home"      # relative to base_url
  - action: click
    selector: "text=儀表板首頁"  # any agent-browser selector form
  - action: wait
    ms: 300

checks:
  - name: "Sidebar bg = --office-color-bg-layout"
    selector: ".ant-layout-sider.ant-pro-sider"
    expect:
      backgroundColor: "rgb(250, 250, 248)"

  - name: "Active menu: bg + text + accent bar"
    selector: ".ant-menu-item-only-child.ant-menu-item-active"
    expect:
      backgroundColor: "rgb(246, 240, 255)"
      color: "rgb(178, 105, 255)"
    pseudo:
      "::before":
        backgroundColor: "rgb(178, 105, 255)"
        width: "3px"
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `version` | yes | Schema version. Currently `1`. |
| `mapping` | yes | Filename (no `.yaml`) in `.claude/e2e/mappings/`. Supplies `base_url` + `auth`. |
| `auth_account` | no | Key under `mapping.auth.test_accounts`. Omit to skip login. |
| `title` | yes | Human-readable title used in report. |
| `setup` | no | Ordered list of actions run after login, before checks. |
| `setup[].action` | yes | One of `goto`, `click`, `fill`, `wait`, `press`. |
| `checks` | yes | Flat list of checks. Order independent. |
| `checks[].name` | yes | Short identifier used in report. |
| `checks[].selector` | yes | CSS selector. First match is checked. |
| `checks[].expect` | yes | Object of `computedStyleProperty: expectedStringValue`. |
| `checks[].pseudo` | no | Map of pseudo-element name (`::before`, `::after`) → expected values. |

**Expected values are STRING compared** (after whitespace normalization). Use the exact string `getComputedStyle` returns (e.g. `rgb(250, 250, 248)`, not `#FAFAF8`). Hex literals will fail equality.

### Setup Action Reference

| Action | Fields | Effect |
|--------|--------|--------|
| `goto` | `url:` (relative to base_url) | Navigate, then wait for networkidle |
| `click` | `selector:` (any agent-browser form) | Direct click; falls back to snapshot ref resolution |
| `fill` | `selector:`, `value:` | Set input value via `agent-browser fill` |
| `wait` | `ms:` (number) | Pause for N milliseconds |
| `press` | `key:` | Send keypress (e.g., `Enter`, `Escape`) |

## Phases

| Phase | What runs | Failure mode |
|-------|-----------|--------------|
| 0 — Resolve | Read YAML, resolve `mapping`, extract auth account | Missing mapping or account → exit 2 |
| 1 — Login | Skip if already authenticated; else fill credentials | Login failure → exit 2 |
| 2 — Setup | Run `setup[]` actions in order | Action failure → abort with reason |
| 3 — Run Checks | For each check: `getComputedStyle` → compare → record result | Selector not found → check fails (others continue unless `--bail-on-first-fail`) |
| 4 — Report | Write `.claude/e2e/reports/ui-verify-<stem>-<YYYY-MM-DD-HHmm>.md` | — |

### Exit Codes

- `0` — all checks pass
- `1` — any check fails
- `2` — setup, login, or YAML schema error

## Report Output

```markdown
# UI Verify — SEC-19 Layout chrome tokens

**YAML:** .claude/e2e/ui-verify/sec-19-layout-tokens.yaml
**Run:** 2026-05-06 14:30
**Result:** PASS 5/5

| Check | Property | Expected | Actual | Result |
|-------|----------|----------|--------|--------|
| Sidebar bg | backgroundColor | rgb(250, 250, 248) | rgb(250, 250, 248) | ✅ |
| Active menu bg | backgroundColor | rgb(246, 240, 255) | rgb(246, 240, 255) | ✅ |
| Active menu text | color | rgb(178, 105, 255) | rgb(178, 105, 255) | ✅ |
| Active menu ::before bg | backgroundColor | rgb(178, 105, 255) | rgb(178, 105, 255) | ✅ |
| Active menu ::before width | width | 3px | 3px | ✅ |
```

## Runner Architecture

The runner is a single Node.js script at `${CLAUDE_PLUGIN_ROOT}/skills/ui-verify/bin/run.js`. It reuses the plugin's `js-yaml` dependency for parsing. The main agent invokes it via Bash — no subagent dispatch (deterministic, single pass).

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/ui-verify/bin/run.js" <yaml-path> [flags]
```

## Red Flags

- **Writing YAML with `each_descendant:` or `find_any:` semantics** — that's forensics; wrong skill.
- **Using non-exact expected values** (e.g., "should contain violet") — normalize expected to the exact `getComputedStyle` string.
- **Selector not known upfront** — resolve it first via `agent-browser`, then hardcode the selector in YAML.
- **Checking behavior instead of style** (e.g., "button should navigate to /success") — wrong skill; use [`e2e-flow`](commands.md).

## Related

- [Commands](commands.md) — full skill list and flag reference
- [Writing Tests](writing-tests.md) — flow YAML format for dynamic-behavior checks
- [Architecture](architecture.md) — pipeline position of `ui-verify`

Found a gap? Run `/e2e-help --feedback "<description>"`.
