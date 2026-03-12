---
name: e2e-map
description: Use when creating or updating UI element mappings for E2E testing — mapping page selectors, capturing app structure, or refreshing stale mappings. Triggers on "e2e map", "map the UI", "update mapping", "refresh mapping", "map selectors", "create mapping".
---

# E2E Map — Orchestrator

Generate or update the UI element mapping for a web application. Codebase analysis and user interaction run in main context; browser exploration is delegated to the `e2e-mapper` agent.

## Invocation

```
/e2e-map [--scope page|full] [--page <page-name>] [--interactive]
```

- No args: full exploration (all pages)
- `--scope page --page dashboard`: re-explore a single page
- `--interactive`: skip agent dispatch, run browser exploration inline (for debugging)

### `--page` Mode Behavior

When `--page <name>` is specified:
- **Phase 1**: Scope codebase analysis to the target page's route file only
- **Phase 2**: Agent navigates ONLY to the specified page
- **Phase 4**: Show unexplored dialogs/modals for THIS page only
- **Phase 5**: Merge strategy — update only `pages.<name>` and any dialogs with `trigger_page: <name>`. Preserve all other pages unchanged.

## Prerequisites & Pre-Flight

1. **agent-browser** installed globally

**If no mapping exists yet** (first map for this app):
- Ask user for `base_url` (e.g., "What URL is your dev server running at?")
- Ask user for `app` name (e.g., "What should I call this app?")
- Skip auth — it will be discovered by the mapper agent.

**If mapping exists**, read `base_url` and `app` from it.

```bash
agent-browser --version
curl -s -o /dev/null -w "%{http_code}" <base_url>
ls ~/.agent-browser/<app>/ 2>/dev/null && echo "OK" || echo "MISSING"
```

If agent-browser is not installed: `"agent-browser CLI not found. Install it globally — the mapper agent needs it to explore pages and extract selectors. See: https://github.com/anthropics/agent-browser"` Stop.

If the dev server is unreachable (non-2xx/3xx or connection error): `"Server not reachable at <base_url>. The mapper agent navigates real pages to extract selectors — the dev server must be running. Start it and retry."` Stop.

Any 2xx or 3xx HTTP response means the server is running.

**First-Run Auth (if mapping exists but profile missing):**

- If `auth.type: none` in mapping: skip auth entirely.
- Otherwise: `agent-browser --profile ~/.agent-browser/<app> --headed open <base_url>`, read `auth.manual_prompt` from mapping and present to user. Verify using `auth.verification` condition. If verification fails, re-prompt user. Profile persists — login is one-time only.
- **If no mapping yet**, skip auth here — the mapper agent handles discovery.

## Phase 1 — Codebase Analysis (~30s)

Use subagents in parallel to gather UI structure from source code.

### 1a. Discover Routes
```
Glob: <codebase.routes_glob> (from mapping; skip if not defined)
```

### 1b. Find Interactive Elements

If no mapping exists yet (first map) and no `routes_glob`: ask user for source directory or skip codebase analysis. If user skips, proceed to Phase 2 (browser-only exploration).

Search in source directory (infer from `routes_glob` path prefix, or use the directory provided by user). These are examples — adapt patterns to the project's framework:

```
Grep for: data-testid="  in <source_dir>
Grep for: aria-label="   in <source_dir>
Grep for: Dialog|Drawer|Modal|Popover  in <source_dir>  (React/Vue)
```

### 1c. Identify Navigation Structure
Read sidebar/navigation components. Adapt globs to the project's framework:
```
React/Next.js: <source_dir>/**/Sidebar*.tsx, Nav*.tsx, layout.tsx
Django/Flask:   <source_dir>/**/urls.py, views.py
Generic:        <source_dir>/**/*nav*, *sidebar*, *menu*
```

**Non-file-based routing:** Some frameworks (Refine, admin panels) define routes via config objects instead of file-based routing. If standard route patterns yield nothing, ask the user for the framework's route configuration approach.

Compile a route map from discovered paths.

**If codebase analysis yields no results**, proceed to Phase 2 with browser-only exploration — the agent will discover pages by following links from `base_url`.

After Phase 1 completes (or is skipped), proceed to Phase 2.

## Phase 2 — Dispatch Mapper Agent

After Phase 1, prepare the agent input and dispatch.

### Prepare Agent Input

| Field | Source | Required? |
|-------|--------|-----------|
| `base_url` | From existing mapping or user prompt | Required |
| `app` | From existing mapping or user prompt | Required |
| `auth_profile` | `~/.agent-browser/<app>/` | Required |
| `report_dir` | `$(pwd)/e2e-reports/$(date +%Y%m%d-%H%M%S)-map` | Required |
| `routes` | Phase 1 codebase analysis output (may be empty) | Optional |
| `existing_mapping_path` | Path to current mapping (if updating) | Optional |
| `target_page` | From `--page` flag | Optional |
| `auth_config` | `{type, verification, manual_prompt}` from existing mapping | Optional |
| `headed` | `true` (default; set `false` for headless) | Optional |

### Dispatch

```
Agent(subagent_type="e2e-mapper"):
  base_url: <url>
  app: <app name>
  auth_profile: ~/.agent-browser/<app>/
  routes: [list from Phase 1 codebase analysis]
  existing_mapping_path: <path if updating>
  target_page: <page name if --page mode>
  report_dir: $(pwd)/e2e-reports/$(date +%Y%m%d-%H%M%S)-map
  auth_config: {type, verification, manual_prompt} from existing mapping
  headed: true
```

Agent returns:
- `mapping_path` — draft YAML written to report_dir
- `pages_found` — list of pages explored
- `elements_mapped` — count of elements
- `unexplored_areas` — dialogs/modals behind triggers (feeds Phase 4)
- Screenshots in `report_dir/`

**If agent fails** (no Summary block, or reports 0 pages found): Report the agent's output to the user with: `"Mapper agent did not return a valid mapping. Check the report at <report_dir> for details. Common causes: server went down during exploration, auth session expired, or no navigable pages found."` Ask user whether to retry or switch to `--interactive` mode.

**If `--interactive` flag:** Skip agent dispatch. Run browser exploration in main context using `agent-browser` directly — navigate each route, snapshot, extract elements, build mapping inline. Use `Skill: "agent-browser"` patterns.

After Phase 2 completes (agent returns summary or interactive exploration finishes), proceed to Phase 4.

## Phase 4 — User Direction

Show the user what was found and what remains unexplored (dialogs, modals, drawers behind triggers). When user picks an area:
1. Navigate to the page containing the trigger
2. Click the trigger to reveal the dialog/drawer/modal
3. Run `snapshot` + `screenshot --annotate` on the revealed content
4. Add new elements to the mapping draft
5. Close the dialog and return

Repeat until user says "done." After user confirms done, proceed to Phase 5.

## Phase 5 — Finalize

1. Write mapping YAML to `.claude/e2e/mappings/<app>.yaml`. **If the file already exists** (re-mapping with `--page`), read the current mapping first and **merge** — update changed elements, add new elements, preserve unchanged pages. Never overwrite the entire file.
   - **No changes detected:** If comparison with existing mapping shows no differences, report `"Mapping for <page> is up to date. No changes needed."` Skip writing the file and proceed to step 3.
   - **Mapping file safety:** Before writing, re-read the file to check for concurrent modifications (compare with the version loaded at skill start). If the file has changed since loading, present both versions and ask the user which to keep.
2. Present the final mapping for review
3. Ask: "Which flow would you like to test first?" — suggest 2-3 candidates
4. Ask: "Want me to create a flow YAML in `.claude/e2e/flows/` and run `/e2e-test`?"

**Generated flow MUST use v2 format:**
```yaml
name: <flow-name>
description: "<description>"
tags: [smoke]
mapping: <mapping-filename-no-ext>   # REQUIRED

steps:
  - id: <unique-step-id>            # REQUIRED — not `name:`
    action: "<natural language>"
    expect:
      - "<element_name> is visible"  # grammar strings — NOT structured objects
    screenshot: true
```
**Never generate v1 format** (`app:` instead of `mapping:`, step `name:` instead of `id:`, structured expect objects).

5. Ask user if they want to commit
6. Ask if ready to close browser: `agent-browser close`

### Multi-Site Hints

After writing the mapping, check if other mappings exist:
```bash
ls .claude/e2e/mappings/*.yaml
```

If other mappings found, suggest multi-site commands (`/e2e-test --all-sites`, etc.). If this is the only mapping, skip the hint.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Overwriting existing mapping | Always `Read` the current mapping first; merge, don't replace |
| Missing hidden elements | Phase 4 exists for this — list what needs interaction to reveal |
| Agent returns stale auth | Check profile exists in pre-flight; re-auth before dispatch if needed |
| Skipping codebase analysis | Phase 1 gives the agent a route list — without it, exploration is slower and may miss pages |
