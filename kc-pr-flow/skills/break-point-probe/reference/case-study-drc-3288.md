# Case Study: DRC-3288 / PR #1241

**Context**: Bug where Snowflake connections failed because dbt-snowflake appends `.snowflakecomputing.com` to the `account` field. If the user entered the full domain, the final URL had the suffix twice. The fix adds `normalize_snowflake_account()` that strips the suffix before YAML profile generation.

**What the original review did**: APPROVED based on 12 passing unit tests + code-level caller trace. No runtime probe. Manual verification checkbox in PR body was left unchecked.

**What break-point-probe would have produced**: the full output contract below, surfacing the runtime gap explicitly.

---

## Sample output for PR #1241

```yaml
break_point:
  file: api_server/apis/utils/warehouse.py
  line: 49
  description: |
    Strip .snowflakecomputing.com suffix from config["account"] before yaml.dump.
    Runs inside warehouse_config_to_profile_yml() only when config["type"] == "snowflake".

failure_chain:
  - step: 1
    description: User types "xxx.snowflakecomputing.com" in Snowflake Account input
    layer: ui
  - step: 2
    description: Frontend POST /warehouse-connections with config dict
    layer: api
  - step: 3
    description: Backend encrypts and stores config (encrypted_config column)
    layer: storage
  - step: 4
    description: Recce session launch fetches config via get_warehouse_connection_config
    layer: domain
  - step: 5
    description: warehouse_config_to_profile_yml generates profiles.yml content  # FIX HERE
    layer: domain
  - step: 6
    description: Recce instance container reads profiles.yml
    layer: infra
  - step: 7
    description: dbt-snowflake appends .snowflakecomputing.com to account
    layer: external
  - step: 8
    description: Connects to xxx.snowflakecomputing.com.snowflakecomputing.com (invalid)  # SYMPTOM
    layer: external

unit_coverage:
  covered_steps: [5]

runtime_gap:
  uncovered_steps: [1, 2, 3, 4, 6]
  reason: |
    Unit tests construct config dict inline and call warehouse_config_to_profile_yml directly.
    Not exercised:
      - step 1-2: frontend → API wire (does the frontend preprocess the account field?)
      - step 3: storage round-trip (does decrypt yield the same dict shape?)
      - step 4: caller wiring in recce_task_func.py (3 call sites) and recce_share_instance_func.py (1)
      - step 6: profiles.yml is actually what the container reads

probe_decision:
  verified_at: B
  method: |
    - A: grepped 4 call sites of warehouse_config_to_profile_yml — all pass config from
      get_warehouse_connection_config without mutation. Fix is on hot path.
    - B: ran pytest tests/test_warehouse.py — 39/39 passed (12 new + 27 existing).
      Grepped consumers of config["account"] across backend — no upstream normalizer.
      Verified SnowflakeAdapter.tsx handleInputChange passes raw value to form state
      (no .replace, no URL parsing).
  evidence:
    - "api_server/apis/recce_task_func.py:199 calls with warehouse_connection_config unchanged"
    - "api_server/apis/recce_task_func.py:1239 same pattern"
    - "api_server/apis/recce_share_instance_func.py:351 same pattern"
    - "pytest tests/test_warehouse.py: 39 passed in 0.42s"
    - "SnowflakeAdapter.tsx:102 — value={config.account}, no preprocessing"
  degrade_reason: |
    Attempted C: curl http://localhost:9527/health returned connection refused.
    Local stack not warm. Degraded to B.

residual_uncertainty:
  - assumption: "Production DB-stored accounts decrypt to the same string the user entered"
    probability: low
    failure_mode: |
      If encryption mangles string (unlikely, AES-GCM is lossless), account field would
      contain unexpected bytes that normalize_snowflake_account's endswith check would miss.
  - assumption: "No other code path generates profiles.yml for Snowflake connections"
    probability: low
    failure_mode: |
      If a bypass path exists (e.g., admin tool, migration script), it would still emit
      profiles.yml with the unnormalized account. Grep found no such path in main branch.
  - assumption: "Frontend doesn't proxy the account field through a form validator that mutates it"
    probability: low
    failure_mode: |
      A validation middleware that normalizes to lowercase or trims would change agreement
      between test and production. Static read of SnowflakeAdapter.tsx shows direct binding.

recommended_human_probe:
  - action: |
      1. make start (brings up local stack)
      2. Create Snowflake warehouse connection via UI with account="myacct.snowflakecomputing.com"
      3. Trigger a recce session that uses this connection
      4. `docker exec <recce-instance-container> cat /tmp/profiles.yml | grep account`
      5. Expect: `account: myacct` (no suffix)
    covers_steps: [1, 2, 3, 4, 6]
    cost: "10-15 min if stack warm, 30 min cold"
    confidence_gain: "B→C"
  - action: |
      Full Level D verification: do the above, then actually connect via recce session
      and run a query against Snowflake. Requires real Snowflake test account credentials.
    covers_steps: [7, 8]
    cost: "30+ min + Snowflake test creds"
    confidence_gain: "C→D"
```

## What this output changes in kc-pr-review

Instead of this original review:

> Event: APPROVE
> LGTM, 12 unit tests passing, narrow fix.

The review becomes:

> Event: APPROVE with noted residual uncertainty
>
> **Break-point Coverage**
> - Break-point at `warehouse.py:49`, bug manifests at dbt-snowflake URL construction
> - Verified at level B (unit tests + caller wiring audit)
> - Unverified: UI → API wire, storage round-trip, container read of generated profiles.yml
> - Residual uncertainty (low probability): no alternate profile generation path exists; frontend doesn't preprocess
>
> **Recommended human probe** (optional, before production rollout):
> - Bring up local stack, create Snowflake connection with full-domain input, inspect generated profiles.yml
>
> LGTM on the fix's isolated correctness. Flagging the runtime gap so reviewer/author can judge whether the low-probability residuals are worth a 15-min UAT.

## Why this is better than the original review

1. **Honest about what was verified**: "level B" with explicit evidence, not "approved" as a black-box verdict.
2. **Honest about what was NOT verified**: five runtime-gap steps listed, with probability and failure-mode for each.
3. **Makes the unchecked manual verification item in PR body actionable**: directly corresponds to recommended_human_probe entry.
4. **Prevents silent fake-verification**: if an agent ran only A and claimed B, the `evidence` list would contradict the claim on audit.
5. **Caller (kc-pr-review) or human can choose**: merge on B with residuals noted, or request the 15-min probe before merge. Not a binary approve/reject.

## Lessons extractable from this case

1. **Unit tests passing ≠ fix is on runtime path.** Always audit call sites.
2. **"Manual verification" unchecked is a diagnostic signal.** The author themselves didn't close the loop.
3. **Level B is achievable cheaply (~10K tokens)** and catches upstream-normalizer bypasses that unit tests miss.
4. **Level C requires a warm stack** — worth investing in stack-warm autodetect so C becomes the default when feasible.
5. **Recipes amortize Level C cost.** A `.claude/break-point-probes/snowflake-connection.md` recipe would make Level C on future Snowflake PRs cost <5 min.
