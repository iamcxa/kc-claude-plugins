---
name: ui-verify
description: Use when verifying static UI differences — computed CSS values on specific DOM elements, design tokens, theme changes, layout dimensions, pseudo-element styles. Declarative YAML input, browser-driven, pass/fail per check. Complements e2e-flow (which verifies dynamic behavior). Triggers on "ui verify", "check ui tokens", "computed style regression", "design token check".
---

# UI Verify — Declarative UI Difference Check

Compare **static** UI properties (computed CSS values on known selectors) against expected tokens. Declarative YAML input, browser-driven via `agent-browser`, machine-judged pass/fail with report.

## Role in the Pipeline

| Skill | What it compares | Judgment |
|-------|------------------|----------|
| **`ui-verify`** (this) | **Static UI** — computed styles, tokens, pseudo-elements, dimensions | Machine (equality) |
| `e2e-flow` / `e2e-test` | **Dynamic behavior** — navigation, state transitions, user actions | Machine (flow asserts) |
| `e2e-walkthrough` | Subjective visual QA, exploration, demo recording | Human |

If you need to check "did the sidebar bg change to #FAFAF8?" → **`ui-verify`**.
If you need to check "clicking Submit navigates to /success?" → `e2e-flow`.
If you need "does the new layout look right?" → `e2e-walkthrough`.

## Scope

**In scope:**
- Fixed selectors × fixed expected computed-style values
- `getComputedStyle(selector)[property]` equality checks
- Pseudo-element (`::before`, `::after`) computed value checks
- Optional pre-check setup actions (goto, click, wait) — needed when the target state is transient
- Screenshot capture + pass/fail report

**Out of scope (use `agent-browser` directly):**
- Dynamic queries (find elements with bg = X, walk parent chain, `elementFromPoint`)
- Computed-style forensics across many candidate elements
- CSS specificity wars / injected-style inspection
- Any check where the selector is not known upfront

If the verification requires forensics → use `agent-browser` REPL-style. This skill is for cases where you already know WHICH element to check and WHAT value to expect.

## Pipeline Context

```
/e2e-map       → mapping.yaml               (map UI + auth)
/ui-verify     → ui-verify.yaml + report    (check computed styles)
/e2e-flow      → flow.yaml                  (dynamic behavior)
/e2e-test      → flow replay + report
```

`ui-verify` reuses `.claude/e2e/mappings/*.yaml` for auth + base_url — same convention as the rest of the e2e-pipeline.

## Invocation

```
/ui-verify <yaml-path> [--no-screenshot] [--bail-on-first-fail]
```

| Arg | Effect |
|-----|--------|
| `<yaml-path>` | Path to ui-verify YAML (e.g. `.claude/e2e/ui-verify/sec-19-layout-tokens.yaml`) |
| `--no-screenshot` | Skip per-check screenshots (faster, less artifact) |
| `--bail-on-first-fail` | Stop on first failed check (default: run all, report aggregate) |

## Prerequisites

1. `agent-browser` installed globally
2. Dev server running (see mapping's `base_url`)
3. Mapping file exists at `.claude/e2e/mappings/<mapping>.yaml` with `auth` block

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

### Field reference

| Field | Required | Description |
|-------|----------|-------------|
| `version` | yes | Schema version. Currently `1`. |
| `mapping` | yes | Filename (no `.yaml`) in `.claude/e2e/mappings/`. Supplies `base_url` + `auth`. |
| `auth_account` | no | Key under `mapping.auth.test_accounts`. Omit to skip login. |
| `title` | yes | Human-readable title used in report. |
| `setup` | no | Ordered list of actions after login, before checks. |
| `setup[].action` | yes | One of `goto`, `click`, `fill`, `wait`, `press`. |
| `checks` | yes | Flat list of checks. Order independent. |
| `checks[].name` | yes | Short identifier used in report. |
| `checks[].selector` | yes | CSS selector. First match is checked. |
| `checks[].expect` | yes | Object of `computedStyleProperty: expectedStringValue`. |
| `checks[].pseudo` | no | Map of pseudo-element name → expected values. |

**Expected values** are STRING compared (after whitespace normalization). Use the exact string `getComputedStyle` returns (e.g. `rgb(250, 250, 248)` not `#FAFAF8`).

## Phases

### Phase 0 — Resolve Mapping

1. Read `<yaml-path>`, validate required fields.
2. Resolve `.claude/e2e/mappings/<mapping>.yaml`. Error if missing.
3. Extract `base_url` + `auth.test_accounts[auth_account]` (email/password/phone/otp).
4. If `auth_account` present but account not found → error with available keys.

### Phase 1 — Login

1. Check if browser already authenticated (post-open URL doesn't match `auth.verification.url_not_contains`). Skip login if yes.
2. Otherwise `agent-browser open <base_url><auth.signin_path>`.
3. Fill credentials (supports `password` / `email` / `manual` if account has email+password).
4. Wait for post-login URL verification.
5. If login fails → abort.

### Phase 2 — Setup

Run `setup[]` actions in order:

- `goto` → `agent-browser open <base_url><url>` + wait networkidle
- `click` → resolve selector → click (tries direct click, falls back to snapshot + ref resolution)
- `fill` → `agent-browser fill <selector> <value>`
- `wait ms=<n>` → `agent-browser wait <n>`
- `press <key>` → `agent-browser press <key>`

### Phase 3 — Run Checks

For each `check`:

1. Resolve selector via `document.querySelector(selector)`. If null → check fails with "selector not found".
2. For each `expect` property, `getComputedStyle(el)[property]` → normalize → compare to expected string.
3. For each `pseudo[name]` property, `getComputedStyle(el, name)[property]` → normalize → compare.
4. Record `{ name, selector, results: [{prop, actual, expected, pass}] }`.

### Phase 4 — Report

Write `.claude/e2e/reports/ui-verify-<yaml-filename-stem>-<YYYY-MM-DD-HHmm>.md`:

```markdown
# UI Verify — <title>

**YAML:** <path>
**Run:** <timestamp>
**Result:** <PASS / FAIL N/M>

| Check | Property | Expected | Actual | Result |
|-------|----------|----------|--------|--------|
| Sidebar bg | backgroundColor | rgb(250, 250, 248) | rgb(250, 250, 248) | ✅ |
...
```

Exit code:
- `0` all pass
- `1` any fail
- `2` setup/login/yaml error

## Runner

The runner lives at `${CLAUDE_PLUGIN_ROOT}/skills/ui-verify/bin/run.js` (Node.js, reuses plugin's `js-yaml` dep). Invoke via:

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/ui-verify/bin/run.js <yaml-path> [flags]
```

The main agent invokes the runner via Bash — no subagent dispatch (deterministic, single pass).

## Acceptance

1. YAML validates against schema (all required fields present)
2. Login succeeds OR browser already authenticated
3. Every `check.selector` resolves to exactly one element (first match)
4. Report file created at `.claude/e2e/reports/ui-verify-*.md`
5. Exit code reflects aggregate pass/fail

## Not in scope

- Forensics / dynamic queries → use `agent-browser` REPL
- Running full app flow → use `e2e-flow` / `e2e-test`
- Element discovery / mapping updates → use `e2e-map`
- Video recording → use `e2e-test --video` or `e2e-walkthrough`
- Subjective "does this look right" → use `e2e-walkthrough`

## Red Flags

- **Writing YAML with `each_descendant:` or `find_any:` semantics** — that's forensics; wrong skill.
- **Using non-exact expected values** (e.g., "should contain violet") — normalize expected to the exact `getComputedStyle` string.
- **Selector not known upfront** — resolve it first via agent-browser, then hardcode the selector in YAML.
- **Checking behavior instead of style** (e.g., "button should navigate to /success") — wrong skill; use `e2e-flow`.
