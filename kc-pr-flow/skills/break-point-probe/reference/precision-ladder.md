# Precision Ladder

Four-level framework for choosing the right probe depth. Higher levels give more confidence but cost more tokens/time. The ladder is **not a menu** — execute the highest level you can actually run, and honestly declare that level.

## Level A — Static trace

**Always executable. Always required.**

What it does:
- Read the diff to locate `break_point`
- Grep all callers of changed symbols
- Confirm fix sits on at least one live code path from user input to symptom

What it proves:
- Fix is syntactically correct in its file
- Fix is not dead code (at least one caller exists)

What it does NOT prove:
- Fix is on the ACTUAL runtime path used by the bug's trigger
- No upstream path bypasses the fix
- No middleware / decorator / override modifies behavior

Cost: ~3-5K tokens. Time: ~1 min.

Execution:
```bash
# Trace callers
grep -rn "<changed_symbol>" <repo_root>

# Check if any caller is in a test-only path vs production path
grep -n "tests/\|__tests__\|\.test\.\|\.spec\." <caller_files>
```

Evidence format:
```yaml
evidence:
  - "file path/to/caller.py:123 — calls changed_symbol in production handler foo_endpoint"
  - "2 other callers: tests/test_foo.py (test-only), scripts/migrate.py (script-only)"
```

---

## Level B — Test + wiring audit

**Executable when repo is local and test runner works. Always attempt if conditions met.**

What it does:
- Run the PR's added/modified tests: `pytest <new_test_file>` or `vitest related <changed_files>`
- Grep consumers of changed symbols and verify they pass unchanged-to-modified argument shape
- Check for upstream normalization that might preprocess the input before the fix sees it
- Verify test fixtures match real-world input shapes (compare against production DB sample or API response shape if available)

What it proves:
- PR's claimed tests actually pass
- Callers pass config/data to changed function without mutation in between
- No upstream normalizer silently "already fixed" the bug (making the fix a no-op)

What it does NOT prove:
- Production runtime actually hits this path (storage-layer idempotency, caching, feature flags can bypass)
- External system behaves as expected

Cost: ~5-10K tokens. Time: ~2-5 min.

Execution:
```bash
# Run the tests
cd <repo_root>
pytest tests/<new_test_file>.py -v
# or
pnpm exec vitest related --run <changed_files>

# Audit upstream
grep -rn "<argument_name>" <upstream_callers>
# look for: .strip(), .lower(), .replace(), .sub(), or typed model constructors that might normalize
```

Evidence format:
```yaml
evidence:
  - "pytest output: 12 passed in 0.34s"
  - "Upstream caller api_server/apis/foo.py:45 passes config dict unchanged"
  - "No upstream normalization detected in 3 consumer paths"
```

---

## Level C — Live runtime probe

**Executable when local stack is warm (backend + DB reachable). Attempt opportunistically; gracefully degrade to B on any failure.**

What it does:
- Autodetect stack warmth via health endpoint or port probe
- Construct minimal probe: API call with input that exercises the break-point
- Execute the probe and inspect the resulting runtime artifact (log, DB row, generated file, returned JSON)
- Compare artifact to expected post-fix shape

What it proves:
- Real runtime path reaches the fix
- Storage/caching/middleware don't bypass the fix
- Generated artifact (e.g., profile.yml, computed field, emitted event) has the post-fix shape

What it does NOT prove:
- External third-party system behavior (that's Level D)
- Edge cases not covered by probe inputs

Cost: ~20-40K tokens. Time: 10-30 min (5 min if stack warm, 30 min if cold-start needed).

### C.1 Stack-warm detection

Before attempting a Level C probe, verify the stack is reachable. **Detection must be tool-robust — a tool-blocked signal is NOT the same as a cold-stack signal.**

Run detection in this order, take the first non-inconclusive result:

```bash
# 1. Preferred: curl to health / openapi endpoints
curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://localhost:9527/openapi.json 2>/dev/null
curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://localhost:9527/health 2>/dev/null
curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://localhost:3000/api/health 2>/dev/null

# 2. If curl output is literal "FAILED: curl" or empty (indicates sandbox-block, not cold stack),
#    fall through to python urllib:
python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:9527/openapi.json', timeout=3).status)" 2>&1

# 3. If both fail, check what's listening on the port — distinguishes cold vs hung:
lsof -iTCP -sTCP:LISTEN -P | grep -E ':(9527|3000|8080)'
#   - nothing listening → truly cold → degrade to B
#   - listener exists but HTTP times out → stack hung → degrade to B with "hung" reason
#   - listener exists and responds → stack warm → proceed

# 4. If a probe recipe exists, use its explicit health check instead:
cat <target_repo>/.claude/break-point-probes/_stack.yaml
```

**Classification rules** — `degrade_reason` must distinguish:

| Signal | Classification | Degrade reason text |
|--------|---------------|---------------------|
| All probes return non-2xx, nothing on port | `stack_cold` | "Local stack not running" |
| Listener exists, HTTP times out | `stack_hung` | "Stack process exists on port N but not responding — may be reloading or crashed" |
| `curl` outputs "FAILED: curl" or empty | `tool_blocked` | "curl denied by sandbox policy; fell back to urllib" (then retry with urllib — do NOT degrade if urllib succeeds) |
| `urllib` also fails | (follow rule 1 or 2 based on listener state) | |

**Auto-start policy** (context-dependent):

| Invocation context | Policy |
|-------------------|--------|
| Auto-invoked by kc-pr-review during PR review | **Never auto-start.** PR review is a background-type action; starting dev stack is side-effect. Degrade to B. |
| User-invoked directly (`/break-point-probe`) | **May ask** whether to auto-start. If user confirms, run `make start` (or repo's documented start command) and retry detection. If no confirmation, degrade to B with reason "stack cold, user chose not to auto-start". |
| Stack is hung (not cold) | **Never auto-restart.** Flag to user with specific command (`pkill -f uvicorn && make start-server`) and wait. Stale server overwrite is destructive. |

The difference: auto-invoke has no explicit "verify deeply" signal; user-invoke does.

### C.2 Probe recipes

For repeatable domains, probe recipes live in `<target_repo>/.claude/break-point-probes/<domain>.md`. Recipe template:

```markdown
# Probe Recipe: <domain name>

## Trigger
<pattern that selects this recipe — e.g., "PR touches api_server/apis/utils/warehouse.py">

## Prerequisites
- Local stack running (make start)
- Test organization/project seeded (make seed-test-data)

## Probe
\`\`\`bash
# Step 1: create connection with trigger input
curl -X POST http://localhost:9527/api/v2/warehouse-connections \
  -H "Authorization: Bearer $LOCAL_TEST_TOKEN" \
  -d '{"name": "probe-test", "type": "snowflake", "config": {"account": "myacct.snowflakecomputing.com", ...}}'

# Step 2: trigger downstream that generates artifact
curl -X POST http://localhost:9527/api/v2/sessions/probe-test/launch

# Step 3: inspect artifact
docker exec probe-test-recce cat /tmp/profiles.yml | grep account
\`\`\`

## Expected post-fix output
\`\`\`
account: myacct
\`\`\`

## Cleanup
\`\`\`bash
curl -X DELETE http://localhost:9527/api/v2/warehouse-connections/probe-test
\`\`\`
```

Without a recipe, construct probe ad hoc from PR context — but recipes are the cheaper path for recurring domains.

### C.3 Ad-hoc probe construction

When no recipe exists:

1. Identify the API endpoint that owns the code path (grep `@router.post`, `@app.route`, route definitions)
2. Identify required auth (extract from existing integration tests)
3. Identify required input shape (from Pydantic model or request schema)
4. Identify the observable artifact:
   - Return value of endpoint → inspect response JSON
   - Side effect on DB → query DB after call
   - Side effect on log / file → `docker exec` or tail log
5. Execute + inspect + compare

If any step cannot be constructed confidently (e.g., auth not obvious, artifact not observable), degrade to B with a clear reason.

### C.3.5 Direct runtime invocation (alternative Level C)

When the fix is a pure function (transform / validator / serializer) and the full API wire probe is blocked or gives wrong-code results, **direct runtime invocation via repo import is a valid Level C**:

```bash
# From repo root, with venv activated:
source .venv/bin/activate
python3 -c "
from <module_path> import <fixed_function>
result = <fixed_function>(<realistic_input>)
assert <post_fix_expected>, f'probe failed: got {result}'
print('probe pass:', result)
"
```

**When direct invocation is PREFERRED over API POST**:

- Running stack is on a stale branch/worktree that does NOT have the fix (POST would show the bug, not verify the fix)
- Fix is a pure transform with no side effects (no DB, no external I/O)
- Auth setup cost exceeds probe value for a low-severity fix
- API POST path wraps the function with other logic you're not auditing in THIS invocation

**When API POST is PREFERRED over direct invocation**:

- Fix involves storage round-trip (encryption, serialization, persistence)
- Fix sits behind middleware that might short-circuit (caching, rate limit, auth-bypass)
- Bug manifested at the API layer, not at the function layer
- Multiple callers exist and you need to prove the fix is on the one the bug reporter used

**Honest labeling for direct invocation**: declare `verified_at: C` with explicit scope note:

```yaml
probe_decision:
  verified_at: C
  method: "Direct import + invocation of <function> with 5 realistic cases"
  c_scope_note: |
    Level C achieved via direct runtime invocation, NOT via API POST wire, because <reason>.
    Does NOT exercise: <list of failure_chain steps still inferred>.
```

The `c_scope_note` field is mandatory when C is achieved via direct invocation (not full-stack POST).

### C.4 Evidence format

```yaml
evidence:
  - "Stack health: GET localhost:9527/health returned 200"
  - "Probe request: POST /warehouse-connections with account='myacct.snowflakecomputing.com' → 201"
  - "Post-fix artifact: docker exec … /tmp/profiles.yml contains 'account: myacct' (no suffix)"
  - "Cleanup: DELETE returned 204"
```

---

## Level D — Full external E2E

**Never auto-execute. Always recommend to human.**

What it does:
- Full user-path E2E including connection to real third-party system (Snowflake, Stripe, GitHub, etc.)
- Verifies not just that our fix is wired, but that the downstream system accepts the post-fix output

What it proves:
- Production-path end-to-end success

What it does NOT prove:
- Anything beyond this specific input case (standard E2E caveats)

Cost: ~50K+ tokens + credentials + potential infrastructure cost (Snowflake query charges, etc.). Time: 30+ min.

### Why never auto-execute

- Requires third-party credentials (usually not in agent env)
- Has real-world cost (API quotas, query charges)
- May have observable side effects (creates resources in the third-party account)
- Flaky — network, third-party quotas, etc. cause false negatives

### Recommend to human format

```yaml
recommended_human_probe:
  - action: |
      1. Start local stack with Snowflake credentials in `.env.local`
      2. Run `make start`
      3. Follow the probe recipe at .claude/break-point-probes/snowflake-connection.md
      4. Confirm dbt-snowflake connection succeeds end-to-end
    covers_steps: [6, 7, 8]
    cost: "30 min"
    confidence_gain: "C→D"
```

---

## Decision tree

```
Given PR context:

1. Execute A.                        [always]
2. Is repo local and tests runnable? ─ no → STOP at A.
                                      ─ yes → Execute B.
3. Is local stack warm?              ─ no → STOP at B.
                                      ─ yes → Attempt C.
4. Did C execute successfully?       ─ no → Degrade to B, record degrade_reason.
                                      ─ yes → STOP at C.
5. D is always recommended to human, never executed.
```

## Honest labeling rules

- A result cannot claim level B unless tests were actually run. "Tests would pass because I read them" is level A.
- B cannot claim C unless an actual HTTP/RPC call was made to a running stack.
- C cannot claim D unless external system was actually contacted. Mocking doesn't count.

**Cross-check**: the `evidence` list must contain entries consistent with the claimed level. A reviewer reading evidence should be unable to argue "that's only level A evidence labeled as B".
