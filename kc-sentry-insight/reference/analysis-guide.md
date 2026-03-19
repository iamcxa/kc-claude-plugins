# Sentry Analysis Guide

This guide tells you — the sentry-analyzer agent — exactly how to query Sentry, classify what you find, and filter noise. Follow these rules precisely. This is not documentation for humans; it is your operating manual.

---

## Section 1 — Structured Strategy Query Patterns

Use the structured strategy when the profile specifies `strategy: structured` or when you are monitoring MCP server tool calls via Sentry's performance instrumentation.

### span.op Filter

MCP tool calls are instrumented as spans with `span.op: mcp.server`. To find errors on specific tools:

```
search_events(
  organizationSlug: "{sentry_org}",
  query: "span.op:mcp.server has:error",
  project: ["{project_slug}"],
  dataset: "spansIndexed",
  fields: ["span.description", "span.op", "error", "timestamp", "trace"],
  limit: 50
)
```

`span.description` holds the tool name (e.g., `mcp.server/list_issues`). Group results by `span.description` to compute per-tool error rates.

### Per-Tool Error Rate Extraction

After fetching span events, group by `span.description`:

- Total calls per tool = count of spans with that description in the time window
- Error calls per tool = count of spans where `error` field is truthy
- Error rate = error calls / total calls

Flag any tool with error rate > 5% as a signal candidate.

### Silent JSON-RPC Errors

MCP servers may return JSON-RPC error objects (`{"error": {"code": ..., "message": ...}}`) in the response body without throwing an exception. These do not appear as Sentry exceptions — they appear as spans with a non-2xx status or a custom tag.

To detect them:
```
search_events(
  query: "span.op:mcp.server span.status:internal_error OR span.status:invalid_argument",
  ...
)
```

Also search for events tagged with `mcp.error_code` if the MCP server emits that tag. A high count of silent errors with no corresponding exception issues = JSON-RPC error responses being swallowed.

### Session ID Grouping

For stateful debugging (e.g., multi-step MCP flows), group events by `session.id` or a custom trace attribute like `mcp.session_id`. Use `get_trace_details` when you have a trace ID to reconstruct the full call sequence.

```
get_trace_details(
  organizationSlug: "{sentry_org}",
  traceId: "{trace_id}"
)
```

This reveals whether errors occur early (auth/init), mid-flow (tool execution), or late (cleanup/finalization).

### Example Tool Calls

Verify project access first:
```
find_projects(
  organizationSlug: "{sentry_org}",
  regionUrl: "https://us.sentry.io"
)
```

Fetch span-level events for MCP monitoring:
```
search_events(
  organizationSlug: "{sentry_org}",
  query: "span.op:mcp.server",
  project: ["{project_slug}"],
  dataset: "spansIndexed",
  fields: ["span.description", "span.op", "timestamp", "trace", "error"],
  sort: "-timestamp",
  limit: 100
)
```

---

## Section 2 — Keyword Strategy Query Patterns

Use the keyword strategy when the profile specifies `strategy: keyword` or when no span-level instrumentation exists. This is the default strategy and mirrors the kc-nightwatch sentry-scanner approach.

### search_issues with Keyword Combinations

Run 2-3 queries per project, varying keyword combinations. Always sort by frequency and scope to the last 14 days:

```
search_issues(
  organizationSlug: "{sentry_org}",
  query: "{keyword1} {keyword2}",
  project: ["{project_slug}"],
  sortBy: "date",
  limit: 25
)
```

`sortBy: "date"` returns the most recently active issues first. For frequency ranking use `sortBy: "freq"`.

### Primary + Secondary Keywords

Split keywords from the profile into two tiers:

- **Primary keywords** (domain terms): the core feature words from `profile.keywords`. Example: `checkout`, `booking`, `order`.
- **Secondary keywords** (related terms): synonyms or adjacent terms. Example: `payment`, `cart`, `invoice`.

Query 1 uses primary keywords. Query 2 uses secondary keywords. Do not mix primary and secondary in one query — overlap produces noisier results.

### Optional Error-Type Keywords

Run a third query targeting error types when the profile's domain involves user-facing transactions:

```
search_issues(
  query: "unhandled OR exception OR 500",
  project: ["{project_slug}"],
  sortBy: "freq",
  limit: 25
)
```

Use this query only for projects with user-facing APIs. Skip for infrastructure-only or internal tooling projects.

### Sorting and Time Scoping

- Always pass a `limit` of 25-50. More than 50 issues rarely adds signal.
- The Sentry MCP `search_issues` tool scopes to the last 14 days by default. Do not override this.
- If `get_issue_details` shows `firstSeen` outside 14 days, the issue is recurrent, not new — adjust classification accordingly.

---

## Section 3 — Classification Heuristics

After fetching issues and their details, classify each into a confidence level. Apply these rules in order — the first rule that matches wins.

### Confidence Rating Rules

| Level | Criteria |
|-------|----------|
| **high** | Event spike: current 7d events > 3x the prior 7d events. OR Regression: `status` was `resolved` but issue is now active (reopened). OR User-facing critical path with > 10 events in 7d. |
| **medium** | New issue: `firstSeen` within last 7 days. OR Recurring: 3–10 events in the issue lifetime and still unresolved. |
| **low** | Single occurrence (1-2 events total). OR Matches infrastructure noise patterns (see Section 4). |

When in doubt between high and medium, prefer medium. Never assign high to a single-event issue regardless of the error message.

### Error Type Classification

Derive `error_type` from the issue title and stack trace:

| Error Type | Detection Signal |
|------------|-----------------|
| `permission_denied` | Title contains "403", "Forbidden", "PermissionDenied", "Unauthorized" |
| `timeout` | Title contains "timeout", "ETIMEDOUT", "deadline exceeded" |
| `not_found` | Title contains "404", "NotFound", "does not exist" |
| `unhandled` | Title contains "UnhandledPromiseRejection", "unhandled exception" |
| `auth_failure` | Title contains "401", "token invalid", "session expired" |
| `data_integrity` | Title contains "integrity", "constraint", "duplicate key", "foreign key" |
| `rate_limited` | Title contains "429", "rate limit", "too many requests" |
| `payment_error` | Title contains "payment", "charge", "stripe", "billing", "invoice" |
| `unknown` | None of the above match |

### Impact Hint Generation

Derive a short `impact_hint` (one sentence) from the error context:

- If `error_type` is `permission_denied` and the stack mentions a user role → "Affects [role] users attempting [action]"
- If `error_type` is `not_found` and the stack mentions a product or entity → "Breaks [entity] lookup on [feature]"
- If `error_type` is `payment_error` → "Blocks payment processing — high business impact"
- If the issue has a `user` tag in Sentry with count > 0 → "Affects [user_count] unique users"
- If no context available → omit `impact_hint` rather than fabricating one

---

## Section 4 — Noise Detection

Apply noise detection after classification. Remove issues that match any exclude rule before building the final signals list.

### Include: Signal-Worthy Issues

Keep an issue if it matches any of these:

- User-facing errors: errors originating in UI endpoints, public API routes, or checkout/booking/transaction flows
- API failures on core paths: any endpoint tagged as critical in the profile's `core_paths` list
- Unhandled exceptions in production: `error_type: unhandled` or title contains "UnhandledPromiseRejection"
- Regressions: issue was previously `resolved` and is now active
- Payment or critical-domain errors: `error_type: payment_error`, or issue title matches `profile.critical_keywords`

### Exclude: Noise Issues

Discard an issue if it matches any of these:

- Infrastructure noise: `error_type` is `timeout` OR `rate_limited`, or title matches patterns like "CORS preflight", "DNS NXDOMAIN", "health check"
- Assigned issues: `assignee` field is non-null in `get_issue_details` response — someone is already working on it
- Bot/crawler errors: event details show `user-agent` matching known bot patterns (`Googlebot`, `bingbot`, `DatadogSynthetics`, `UptimeRobot`)
- Health check endpoints: issue URL or stack contains `/healthz`, `/health`, `/ping`, `/status`, `/_ah/health`
- Ignored or archived: `status` is `ignored` or `archived`

### Applying noise_patterns from Profile

The profile may include a `noise_patterns` list of regex strings. For each candidate issue:

1. Concatenate the issue title and the first frame of the stack trace into one string
2. Test each regex in `noise_patterns` against this string
3. If any pattern matches → discard the issue

Example profile entry:
```yaml
noise_patterns:
  - "ThrottlingException"
  - "SocketHangUp"
  - "health.*check"
```

Apply case-insensitive matching. A match on any pattern = exclude.

---

## Section 5 — Events Trend Calculation

When building output for each issue, compute these three fields. These go into the `events_trend` block of the output YAML.

### events_7d

The count of events in the 7-day window ending on the scan date (today).

Use `get_issue_details` response field `count` if it reflects a 7d window, or use `search_events` with a time range filter:

```
search_events(
  query: "issue.id:{sentry_issue_id}",
  start: "{scan_date - 7 days}T00:00:00Z",
  end: "{scan_date}T23:59:59Z"
)
```

Use the result count as `events_7d`.

### events_prior_7d

The count of events in the 7-day window immediately before `events_7d` (days 8–14 before scan date).

```
search_events(
  query: "issue.id:{sentry_issue_id}",
  start: "{scan_date - 14 days}T00:00:00Z",
  end: "{scan_date - 8 days}T23:59:59Z"
)
```

If `get_issue_details` shows `firstSeen` within the last 7 days, the prior window predates the issue's existence. Set `events_prior_7d: null`.

If the `search_events` call returns an error or empty result for the prior period → set `events_prior_7d: null`.

### events_trend

Calculate as a percentage string:

```
trend = (events_7d - events_prior_7d) / events_prior_7d
```

Format rules:
- Positive trend → `"+{N}%"` (e.g., `"+88%"`)
- Negative trend → `"-{N}%"` (e.g., `"-23%"`)
- Zero → `"0%"`
- Round to nearest integer

Set `events_trend: null` when:
- `events_prior_7d` is null (issue is newly detected or data unavailable)
- `events_prior_7d` is 0 (division by zero — treat as new spike, but still null for the trend field)

In the null case, the confidence classifier should use `events_7d` alone to assign `medium` or `high` confidence based on absolute event count.
