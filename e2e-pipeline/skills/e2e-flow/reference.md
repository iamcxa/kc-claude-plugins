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

### External Service Discovery

Scan for SDK integration files that represent external service side-effects:

```
Grep: posthog\.capture|posthog\.identify|analytics\.track
Grep: langfuse\.trace|langfuse\.generation|langfuse\.span
Grep: sentry\.captureException|sentry\.captureMessage
Grep: webhook|sendWebhook|notifyExternal
Grep: fetch\(.*(slack|discord|sendgrid|twilio)
Grep: SLACK_WEBHOOK|DISCORD_WEBHOOK|SENDGRID_API|TWILIO_
```

For each match, record: service name, file path, SDK call pattern.

**Cap**: Share the 20 file-read budget with other discovery phases. External service discovery uses grep only (no file reads) — unless a match needs surrounding context to determine the service name.

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

External services detected:
  PostHog: src/lib/analytics.ts — capture('cta_clicked', { page, variant })
  Langfuse: src/lib/tracing.ts — langfuse.trace({ name: 'ai-chat' })
```

**Cap:** Max 20 file reads during the entire scan phase.

---

## External Verification Templates

Generation templates for the flow-writer when constructing `Verify external` steps. These parallel `references/common-patterns.md` execution patterns but are framed as **generation guidance** (what to write) rather than execution guidance (how to run).

### Analytics (PostHog, Mixpanel)

```yaml
- id: verify-tracking-event
  action: "Verify external"
  description: "After <trigger>, verify <service> received the <event> event"
  wait: 10
  verify:
    posthog:
      - event: <event_name>
        expect: "count > 0 in last 5 minutes"
        properties:
          page: "<expected_page>"
  on_fail: warn
```

### Tracing (Langfuse, Sentry)

```yaml
- id: verify-ai-trace
  action: "Verify external"
  description: "After <AI interaction>, verify <service> recorded the trace"
  wait: 15
  verify:
    langfuse:
      - check: "Recent trace named '<trace_name>' with output"
  on_fail: warn
```

### Generic REST / Webhook / Database

```yaml
- id: verify-side-effect
  action: "Verify external"
  description: "After <action>, verify <target> reflects the change"
  wait: 5
  verify:
    custom:
      - check: "<natural language description of what to query/verify>"
  on_fail: warn
```

## External Execution Templates

Generation templates for the flow-writer when constructing `Execute external` steps. These trigger non-browser actions (CLI, API calls, scripts) as part of the test flow.

### CLI Commands

```yaml
- id: trigger-cli-action
  action: "Execute external"
  description: "Run <command> to <purpose>"
  execute:
    cli:
      - run: "<command>"
        repeat: 3             # optional
        expect: "exit code 0"
  wait_after: 10              # wait for backend to process
  on_fail: fail
```

### API Triggers

```yaml
- id: trigger-api-call
  action: "Execute external"
  description: "Call <endpoint> to trigger <side-effect>"
  execute:
    api:
      - run: "curl -X POST <endpoint> -H 'Authorization: Bearer $TOKEN' -d '{...}'"
        expect: "HTTP 200 or 201"
  wait_after: 5
  on_fail: fail
```

### Data Seeding / Setup

```yaml
- id: seed-test-data
  action: "Execute external"
  description: "Insert test records before browser verification"
  execute:
    db:
      - run: "Insert 3 test orders into the orders table"
        expect: "3 rows inserted"
  wait_after: 2
  on_fail: fail
```

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
      report_dir: <absolute path to .claude/e2e/reports/timestamp/>
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

### PR Summary and Acceptance Report Templates

See [pr-report-template.md](../../references/pr-report-template.md) for the unified PR report skeleton and field specifications. All `pr-summary.md` files follow that template.

**e2e-flow-specific extensions** (insert between `### Steps` and `### Health`):

1. **Corrections** (always present when corrections > 0):

```markdown
### Corrections

| Change | Type | Detail |
|--------|------|--------|
| +step 3.1 | auto-inserted | Confirm dialog after "Add Connection" |
| fix step 2 | selector repair | `add_btn` → `add_connection_button` |
```

2. **Acceptance Mapping** (when `--from plan/spec` used):

```markdown
### Acceptance Mapping

| # | Criterion | Steps | Status |
|---|-----------|-------|--------|
| 1 | User can create project | step-1 → step-4 | ✅ Covered |
| 2 | Success toast appears | step-5 | ✅ Covered |
| 3 | PostHog event tracked | verify-tracking | ⚠️ SKIP (no API key) |
```

3. **Checkpoint Results** (when flow has external checkpoints):

```markdown
### Checkpoint Results

| Checkpoint | Type | Result | Detail |
|-----------|------|--------|--------|
| trigger-sessions | Execute | PASS | recce-cloud run ×3, exit 0 |
| verify-posthog | Verify | SKIP | POSTHOG_API_KEY not set |
```
