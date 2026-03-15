# E2E Flow — Reference

Detailed procedures for codebase scanning, smoke mode, agent dispatch, and report templates. Loaded on demand from SKILL.md.

---

## Codebase Scan Strategy

Build a `context_summary` text block for the flow-writer agent. The scan identifies routes, components, and API endpoints relevant to the flow's scope.

### Route Discovery

**Next.js (App Router):**
```
Glob: app/**/page.{tsx,jsx,ts,js}
Pattern: path segments map to URL segments
  app/projects/page.tsx → /projects
  app/projects/[id]/page.tsx → /projects/${id}
  app/(dashboard)/settings/page.tsx → /settings (group ignored)
```

**Next.js (Pages Router):**
```
Glob: pages/**/*.{tsx,jsx,ts,js}
Exclude: pages/api/**, pages/_app.*, pages/_document.*
Pattern: file path = URL path
  pages/projects/index.tsx → /projects
  pages/projects/[id].tsx → /projects/${id}
```

**React Router:**
```
Grep: createBrowserRouter|<Route|<Routes
Read the router config file to extract path → component mappings
```

**Fallback (framework-agnostic):**
```
Grep: path:\s*["']/   (route config objects)
Grep: navigate\(["']/  (programmatic navigation targets)
```

### Component Discovery

For pages relevant to the description:

```
Glob: src/components/*Form*.{tsx,jsx}
Glob: src/components/*Dialog*.{tsx,jsx}
Glob: src/components/*Modal*.{tsx,jsx}
Grep: <form|onSubmit|handleSubmit   (in route component files)
Grep: <Dialog|<Modal|<Drawer        (in route component files)
```

### API Endpoint Discovery

```
Grep: fetch\(|axios\.|useMutation|useQuery
Grep: POST|PUT|DELETE|PATCH    (in component files, not test files)
Glob: app/api/**/route.{ts,js}  (Next.js API routes)
Glob: pages/api/**/*.{ts,js}    (Next.js Pages API)
```

### Assembling context_summary

Format the scan results as a structured text block:

```
Routes found:
  /projects → src/app/projects/page.tsx
  /projects/new → src/app/projects/new/page.tsx
  /settings → src/app/(dashboard)/settings/page.tsx

Components in scope:
  src/components/ProjectForm.tsx — fields: name, description, template
  src/components/ConfirmDialog.tsx — trigger: delete button, action: DELETE /api/projects/:id

API endpoints:
  POST /api/projects — creates project (src/app/api/projects/route.ts)
  DELETE /api/projects/:id — deletes project
  GET /api/projects — lists projects

Mapping pages: projects-page (6 elements), new-project-page (4 elements), settings-page (8 elements)
```

**Cap:** Max 20 file reads during the entire scan phase.

---

## Smoke Mode Rules

Migrated from `/e2e-walkthrough --smoke`. When `--smoke` is used, the flow-writer agent generates a visit-all-pages flow using only the mapping (no codebase scan needed).

### Page Selection (7 rules, in order)

1. **Include** pages with non-empty `elements:` AND a navigable `url_pattern`
2. **Exclude** pages with `url_pattern` containing unresolvable parameters (`${id}`, `${traceId}`, `${sessionId}`)
3. **Exclude** pages matching `auth.signin_path` (navigating there would log out)
4. **Exclude** pages with `note:` containing "Requires admin" or "admin access" (unless user specifies otherwise)
5. **RBAC-aware**: Elements with `note:` containing role requirements → mark `expected: conditional` (not failures)
6. **Onboarding pages**: Include only if user is in onboarding state (or mark `optional: true`)
7. **Minimum elements**: Skip pages with fewer than 2 elements (likely utility/redirect pages)

### Ordering

1. Shared sidebar/navigation (verify nav structure first)
2. Main pages (by mapping order)
3. Settings pages
4. Onboarding pages (last, often conditional)

### Per-Page Template

Each page gets 2-3 steps:
1. Navigate to `url_pattern`
2. Verify 2-3 key elements (prefer headings and primary action buttons)
3. Screenshot on key page

### Dialog Handling

For pages with `dialogs:` section:
- Add one open-close cycle for the primary dialog (first dialog whose `trigger_page` matches)
- Open: click trigger element
- Verify: dialog elements visible
- Close: click cancel/close button or press Escape

### Smoke Flow Naming

- Auto-name: `smoke-<app>-<YYYYMMDD-HHmmss>.yaml`
- Tags: `[smoke, auto-generated]`

---

## Agent Dispatch Patterns

### flow-writer dispatch

```
Agent tool (e2e-pipeline:e2e-flow-writer):
  description: "Generate E2E flow from <source>"
  prompt: |
    Generate E2E flow:
      description: <extracted criteria or feature description>
      mapping_path: <absolute path to mapping YAML>
      context_summary: <assembled codebase scan text block>
      output_dir: <absolute path to .claude/e2e/flows/>
      flow_name: <optional, user-specified or omit for auto>
      source_text: <optional, full plan/spec/PR diff text>
      smoke_mode: <true|false>
```

### flow-verifier dispatch

```
Agent tool (e2e-pipeline:e2e-flow-verifier):
  description: "Verify E2E flow in browser"
  prompt: |
    Verify E2E flow:
      flow_path: <absolute path to flow YAML>
      mapping_path: <absolute path to mapping YAML>
      auth_profile: ~/.agent-browser/<app>/
      base_url: <from mapping>
      app: <from mapping>
      report_dir: <absolute path to e2e-reports/timestamp/>
      record: <true|false>
```

### trace-analyzer dispatch

```
Agent tool (e2e-pipeline:e2e-trace-analyzer):
  description: "Analyze trace from flow verification"
  prompt: |
    Analyze trace:
      trace_path: <absolute path to trace.zip>
      report_dir: <same as verifier>
      step_log_path: <absolute path to step-log.json, if exists>
```

---

## Report Templates

### PR Summary (for --pr posting)

```markdown
## E2E Verification: <flow-name>

<STATUS_EMOJI> **<STATUS>** (<N> steps, <K> corrections applied)

### Flow Coverage

<brief description of what this flow tests>

### Corrections from draft

| Change | Type | Detail |
|--------|------|--------|
| +step 3.1 | auto-inserted | Confirm dialog after "Add Connection" |
| fix step 2 | selector repair | `add_btn` → `add_connection_button` |

### Step screenshots

| Step | Screenshot | Status |
|------|-----------|--------|
| 1. Navigate to settings | ![](step-1.png) | PASS |

<VIDEO_LINK_IF_AVAILABLE>

---
Generated by `/e2e-flow` · [e2e-pipeline](https://github.com/iamcxa/kc-claude-plugins/tree/main/e2e-pipeline)
```

### Acceptance Report (for --from plan/spec)

```markdown
## E2E Acceptance: <source>

### Criteria Mapping

| # | Criterion | Flow Step | Status |
|---|-----------|-----------|--------|
| 1 | User can create project | step-1 to step-4 | ✅ Covered |
| 2 | Success toast appears | step-5 expect | ✅ Covered |
| 3 | PostHog event tracked | N/A | ⚠️ Not verifiable in E2E |

### Coverage

- **Covered:** M/N criteria
- **Not coverable:** K criteria (external-only, no UI signal)
- **Missing from mapping:** L elements need `/e2e-map` update
```
