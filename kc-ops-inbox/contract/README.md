# kc-ops-inbox contract v1

What a project sends to its ops inbox, and what the inbox does with it. The rules are executable in `contract.mjs` (`parseEvent`, `validateBody`); the published schemas in `v1/` are derived from the same `TYPES` table by `generate.mjs`, and `contract-versions.json` pins each schema's digest. The module imports only `node:crypto`, so a project can copy or pin it without installing anything.

Pin a commit of this directory on the default branch. Rules in this file that the validator does not check are marked **runtime**: they belong to the inbox runtime, which is owned by the task `ops-inbox-r1-setup-and-isolation` ("r1"), not to this contract; the list of what is not built is under [Inbox runtime gaps](#inbox-runtime-gaps-owned-by-r1). Source labels (C, F, D, ER, Q, VR) are defined under [Sources](#sources).

## Transport

`POST` the CloudEvent as the raw request body (structured JSON, at most 16 KiB) with the Standard Webhooks headers:

| Header | Value |
| --- | --- |
| `webhook-id` | by convention `msg_<event id>`; the contract does not check it, because dedupe is on `source` and `id` (VR 7) |
| `webhook-timestamp` | decimal digits only (`^\d+$`), Unix seconds, fresh on each attempt; the inbox refuses a difference over 300 s from its clock, and refuses every timestamp when its clock value is not a finite number (VR 4) |
| `webhook-signature` | `v1,<base64 HMAC-SHA256 of "<webhook-id>.<webhook-timestamp>.<raw body>">`, key = the base64 part of the `whsec_` secret; several space-separated `v1,` signatures are accepted |

The raw body must equal `JSON.stringify(JSON.parse(body))` (reason `non-canonical-body`). The body is a string; any other input is refused as `not-json` and nothing is thrown (VR 3). A sender that serializes with `JSON.stringify` already conforms; a body with a duplicate key does not, because `JSON.parse` keeps the last copy and the raw bytes keep both (ER P1-1).

## Envelope

| Attribute | Rule | Source |
| --- | --- | --- |
| `specversion` | `"1.0"` | CloudEvents |
| `id` | `^[A-Za-z0-9._-]{1,64}$`; for `ops.metric.*` it must equal the derived id below | F1, ER P2-1 |
| `source` | `^urn:[a-z0-9-]{1,32}(:[a-z0-9-]{1,32}){1,3}$`, for example `urn:relay:capacity`; the producing project | F1 (a source with spaces passed before), ER P3-1 |
| `type` | `ops.metric.crossed`, `ops.metric.recovered`, `ops.metric.heartbeat`, `sentry.issue.alert` or `ops.inbox.selftest` | C3, D2 |
| `subject` | `^[A-Za-z0-9._/-]{1,100}$` and the per-type rule below; names the incident within the source | F2 |
| `time` | RFC 3339 with calendar-valid components (Feb 30, hour 24 and month 13 are refused as `invalid-value: time`); on `ops.metric.*` it must end in `Z` | F2, VR 1 |
| `environment` | `prod`, `preview` or `dev`. Required on `ops.metric.*`; optional on the other types, which the key check treats as `prod` | C7, D5, ER P3-2 |
| `severity` | `info`, `warning` or `critical`. Required on `ops.metric.*`; a heartbeat's must be `info` | C7 |
| `dataschema` | `https://github.com/iamcxa/kc-claude-plugins/blob/main/kc-ops-inbox/contract/v1/<type>.json`; an identifier the validator compares, nothing fetches it | F2, ER P3-5 |
| `datacontenttype` | optional, `application/json` | F2 |
| `data` | the per-type fields below | F2 |

Any other attribute, and any `data` field outside the type's list, is refused, not dropped.

## Types

`environment` and `severity` are envelope attributes so the inbox can route before it parses `data` (design choice; the alternative, fields inside `data`, was not chosen).

### `ops.metric.crossed`, `ops.metric.recovered`, `ops.metric.heartbeat`

Generic: a new project adds no type. The project-specific parts are `source` and `data.metric`.

| `data` field | Rule | Types | Source |
| --- | --- | --- | --- |
| `metric` | `^[a-z][a-z0-9.-]{0,28}$` (at most 29 characters, so the longest id is 64) | all | C3, ER P2-1 |
| `window` | `day` or `month` | all | F6, F10 |
| `period` | `YYYY-MM-DD`, the UTC start of the window; a month window may start on any day | all | F10 |
| `value` | integer, 0 or more (a safe integer) | all | C2 |
| `limit` | integer, 1 to 9999999 | all | F6 |
| `limitSource` | `default` or `override` | all | F6 |
| `level` | 50, 80 or 100 (percent of `limit`) | crossed, recovered | Q1 |
| `cause` | `below` or `period-ended` | recovered | C7, ER P2-1 |
| `every` | `hour` or `day` | heartbeat | C7 |
| `runbook` | optional; `^[A-Za-z0-9_-]{1,32}(/[A-Za-z0-9_-]{1,32}){0,3}\.md$`, a repository-relative path (no leading `/`, no `..`) | all | C7, ER P3-1 |
| `dashboard` | optional; `^https://[a-z0-9.-]{1,64}/[A-Za-z0-9._~/-]{0,100}$` (no query or fragment); a link for the Captain, which the agent does not fetch (**runtime**) | all | C7, ER P2-5 |
| `adrs` | optional; at most 5 strings `^[0-9]{4}$`, ADR numbers the agent resolves at the commit it checks out (**runtime**) | all | C7 |

### Deterministic id

Cross-field checks (reasons `invalid-value: data.value`, `subject-mismatch`, `id-not-deterministic`, checked in that order):

- crossed: `value × 100 ≥ level × limit`. Recovered with cause `below`: `value × 100 < level × limit`.
- subject, with `<w>` = `d` for `day` and `m` for `month`: `metric/<environment>/<metric>/<w><period>` for crossed and recovered; `heartbeat/<environment>/<metric>/<w>` for a heartbeat.
- id, with `<c>` = `b` for `below` and `p` for `period-ended`:
  - crossed: `<metric>.<environment>.<w><period>.c<level>.l<limit>`
  - recovered: `<metric>.<environment>.<w><period>.r<level><c>.l<limit>`
  - heartbeat: `<metric>.<environment>.hb<w>.<bucket>`, `<bucket>` = the UTC `time` string cut to `YYYY-MM-DDTHH` for `every: hour` and to `YYYY-MM-DD` for `every: day` (`time` must end in `Z`, so the cut is the UTC hour or day; VR 1)

The id is derived from the event's own fields, so a retry, a resend or a second process produces the same id (source: C3, Q1). `limit` is in the id, so a level crossed again after a limit raise is a new event; `window` and `cause` are in the id so a day and a month window, or a `below` and a `period-ended` recovery, derive different ids (ER P2-1; `test/contract.test.mjs`, "the four ids of relay's ceiling"). `environment` is in the id and the subject, so a preview crossing does not suppress or join a production one.

Stated limit (ER P2-1): a limit lowered back, within one period, to a value it already had re-derives that value's ids, and the repeat is answered `200 duplicate`. Accepted because only an operator lowers a limit; a sequence number would need project state.

### No free text

On these three types every string is an enumerated value or matches a bounded pattern that excludes whitespace, so no field carries a sentence. Residual (ER P3-1): no spaces is not no text; `metric`, `runbook`, the `dashboard` path and `source` can spell a kebab-case phrase. The agent prompt's rule that event content is data, never instructions, stays the second guard (**runtime**).

### `sentry.issue.alert`, `ops.inbox.selftest`

`sentry.issue.alert` — subject `issue/<issue_id>`. Data: required `issue_id`, `title`, `level`, `project`, `web_url`; optional `event_id`, `culprit`, `triggered_rule`, `datetime`, `release`. `title` and `culprit` (at most 500 characters) are the only free-text fields of this type, and the residual is as r1 recorded it (F4). Every other field is bounded (VR 2): `issue_id`, `event_id`, `project` and `triggered_rule` match `^[A-Za-z0-9._-]{1,64}$`; `level` is `fatal`, `error`, `warning`, `info` or `debug`; `release` matches `^[A-Za-z0-9._@+-]{1,100}$`; `web_url` matches `^https://[A-Za-z0-9._~:/?#@!$&*+,;=%-]{1,480}$`; `datetime` is a calendar-valid RFC 3339 time. A producer whose rule names or projects contain spaces slugs them before sending.

`ops.inbox.selftest` — sent by the setup read-back; subject `selftest/<id>` (checked, reason `subject-mismatch`); data `v`, `project` (`owner/name`). It files no task.

### Retired

`relay.capacity.ceiling` is not in v1 (reason `unknown-type`). Its free `event` and `limitSource` reached an agent prompt (F4), and relay never sent it (F6). Relay's ceiling is an `ops.metric.*` event (D2).

## Project side, inbox side, shared

| Side | Rule | Source |
| --- | --- | --- |
| Project | Measures the metric atomically where the unit happens and owns the count, the limit and the levels. | C2, F6, F10, D1 |
| Project | Sends `crossed` from the write that moves the count from below a level to at or above it, and `recovered` when that condition clears (the limit was raised, or the period ended). Sends counts only: no account, user, phone, address, share or Briefing identifier. | Q1, F5 |
| Project | Sends a heartbeat at least once per declared `every`. | C7 |
| Project | Decides which period a unit belongs to at its own boundary instant; `period` stays the UTC date of that instant. | D7 |
| Project | Follows the sender rules below. | C7 |
| Inbox | Verifies the signature and the key's environments and source prefix, validates this contract, drops a repeat of `source` and `id`, groups by `source` and `subject`, routes by the table below, and keeps the raw event (**runtime**). | F2, F3, C4 |
| Inbox | Does not count units and does not hold a project's thresholds; it holds the routing table, last seen per environment and metric, and the incident claims (**runtime**). | D1 |
| Inbox | Projects stored events to PostHog; the store is the truth and PostHog can be rebuilt from it. Not built; the store choice is recorded in the task, not decided here (**runtime**). | C4, C5, C6 |
| Shared | Type names, the fixed fields, the id derivation, the enumerated values, signing-secret provisioning and rotation, and pre-inbox delivery with the same body. | Q1, C3 |

## Routing

Default table, applied by the inbox (**runtime**). An inbox instance may change a cell in its own configuration, which the Captain owns.

| environment \ severity | info | warning | critical |
| --- | --- | --- | --- |
| prod | record | agent | captain |
| preview | record | record | agent |
| dev | record | record | record |

| Route | What the inbox does | Answer | Source |
| --- | --- | --- | --- |
| record (record-and-close) | Keeps the event in its store. No dispatch, no notice, no write to any ops task, even when the incident is open: the inbox holds only a dispatch credential, and a trigger run writes the state branch. | `200 recorded` | C7, F3 |
| agent (wake the agent) | Opens or joins the incident, posts a notice, and an agent run files one recommendation. | `202` | C7, F2 |
| captain | The agent path, and the notice mentions the Captain's Slack user from the instance configuration. The NOT started and UNCERTAIN notices carry the same mention. | `202` | C7, D4, ER P2-4 |
| `recovered` | With an open incident claim, a join dispatch (no model run) whose run writes the event and marks the task closable; it does not close or merge the Draft PR. Without one, `200 recorded`. | `202` or `200 recorded` | D3 |

A heartbeat does not open or join an incident. An event without `environment`, such as a Sentry alert, keeps r1's route (agent) (F2). Preview with critical routes to the agent so r1's live test from a preview deploy stays possible.

## Sender rules

| Rule | Source |
| --- | --- |
| **Same id on retry.** The id is derived, so a retry, a resend or a second process produces the same id; `webhook-id` is `msg_<id>` by convention (not checked); `webhook-timestamp` is fresh on each attempt. | C7, Q1 |
| **Check order at the inbox:** 413 size, then 401 signature and timestamp, then 400 contract (canonical body first), then 401 key not allowed. The key check comes last because `environment` and `source` are read from the validated body; all four run before any claim. `parseEvent` implements this order. | ER P3-2 |
| **Retry budget:** up to 3 attempts inside the request that detected the change (0 s, 1 s, 4 s). Then the next heartbeat run resends every `crossed` and `recovered` event of the open periods (the current period and the one before) with the same ids; the inbox dedupes, so a resend costs one read. | C7, ER P3-3 |
| **Crossings-only cap:** at most 8 `crossed` events per incident (`source` and `subject`). `recovered` is never capped, because a capped recovery would leave the incident open. There are at most 3 levels, so one limit yields at most 3 crossings; 8 covers the first limit and one full raise (6) with 2 to spare. Over the cap the sender stops sending crossings. | C7, ER P2-2 |
| **Claim retention (inbox, runtime):** an event claim is kept at least 70 days, so a resend of a `period-ended` recovery after a month window is still a duplicate. | ER P3-3 |

Response codes (the codes in rows without "new" exist in r1's `handle()`; "new" is not built):

| Answer | Meaning | Sender | Source |
| --- | --- | --- | --- |
| 202 | accepted and an agent was dispatched (open or join) | done | F2 |
| 200 `duplicate` | this `source` and `id` were already accepted | done | F2 |
| 200 `recorded` (new) | stored, routed record | done | C7 |
| 400 `<reason>` | not contract v1 | do not retry; log the reason; a sender bug | F2 |
| 401 `timestamp-out-of-tolerance` | clock skew over 300 s | retry once with a fresh timestamp | F2 |
| 401 other, including `key-not-allowed` | wrong key, or a key not allowed for this environment or source | do not retry; a Captain key step | D5, ER P3-2 |
| 413 | body over 16 KiB | do not retry | F2 |
| 429 `incident-cap` (new) | a `crossed` event on an incident that already holds 8 crossings | do not retry | ER P2-2 |
| 502 `dispatch-refused` | GitHub answered 4xx (or the token mint did) and the inbox released its claims | retry with the same id | F2, ER P2-3 |
| 504 `dispatch-ambiguous` | GitHub did not answer within 10 s or answered 5xx, so a run may exist; the claims are kept | do not retry (a retry gets `200 duplicate`); an event whose dispatch never happened is lost at-most-once | F3, D8, ER P2-4 |
| other 5xx, network error, no answer | unknown | retry with the same id | C7 |

502 is for a GitHub 4xx only. Today `handle()` also answers 502 for a GitHub 5xx (F2); the rule above is safe until then only because no producer sends live. The accepted loss at 504 is D8 (Captain, C9).

## Signing

The signature, timestamp and clock rules are under [Transport](#transport). Secrets are a Captain-only runbook step (C7 provisioning, D5):

- **Provision:** per project, one secret for `prod` and one for `preview` and `dev`, each `whsec_` plus 32 random bytes in base64, set through stdin on the inbox and on the project's matching deploy context. The inbox stores each secret with the environments it may sign and the `source` prefix it may sign (`urn:<project>:`); `parseEvent({ keys })` takes `[{ secret, environments, sources }]` and refuses an event outside either scope with 401 `key-not-allowed`. An event without `environment` needs a key whose environments include `prod`. Source for the prefix: ER P3-2.
- **Rotate:** (1) add the new secret to the inbox as a second key for the same environments; (2) the project switches, and may sign with both during the switch (several `v1,` signatures in one header are accepted); (3) after the first heartbeat verified with the new key arrives, remove the old one. A suspected leak follows the same steps at once.

## Pre-inbox delivery

Before a project's inbox is live, the project sends the same body to its pre-inbox sink; going live changes where the body is sent. The project has one builder and one transport switch, and its CI runs `validate.mjs` over bodies the builder produces (Q1, C1). For PostHog: event name = `type`, `distinct_id` = `source` (not a person), properties = every `data` field plus `ce_id`, `ce_subject`, `ce_environment`, `ce_severity`, `ce_time`; insights count distinct `ce_id`, because PostHog's uuid deduplication is not established (F9, C6).

## Keys

- dedupe: `sha256(source + "\n" + id)`; a repeat is accepted once.
- incident: `sha256(source + "\n" + subject)`; events with one incident key join one ops task. A crossing and its recovery share a subject; a heartbeat has its own.
- An event of any type that names a non-prod `environment` has `<environment>\n` prepended to both hashes, so a preview key cannot claim a dedupe key or join an incident of the same `source` and `id` or `subject` as a prod event, even when the types differ. A `prod` event and an event without `environment` are keyed as before (ER P3-2, D5, VR 5). Metric ids and subjects are unchanged.

## Versions

An incompatible change gets `v2` with its own schemas and `dataschema`. A compatible change to v1 re-pins `contract-versions.json` in the same commit, and `test/contract.test.mjs` fails until it does. Adding a `level` value is compatible, but an adopter on an older pin refuses it, so a producer re-pins before it emits a new level (ER P3-5).

## Check an event

```
node contract/validate.mjs contract/fixtures/relay-crossed.json
```

Fixture shape: `{ secret? | keys?, now?, headers, body }`. `secret` (falling back to `OPS_WEBHOOK_SECRET`) is one key allowed for every environment and source; `keys` is `[{ secret, environments, sources }]`; `now` falls back to the clock and `--now <epoch>` overrides it. Exit 0 prints `valid <type> <dedupe key> <incident key>`. Exit 1 prints one reason: `missing-attribute: <name>`, `signature-mismatch`, `timestamp-out-of-tolerance`, `missing-headers`, `key-not-allowed`, `non-canonical-body`, `field-not-allowed: <path>`, `unknown-type: <type>`, `invalid-value: <path>`, `subject-mismatch`, `id-not-deterministic`, `not-json`, `body-too-large`. A reason repeats sender text only as a token of `[A-Za-z0-9._-]{1,64}` (otherwise `?`; VR 6). Exit 2 is a usage error or a malformed fixture (`null`, headers that are not an object, a non-string body, malformed `keys`, a non-numeric `now`) and a crash of the validator; exit 1 always means a refusal (VR 3).

Fixtures (a published test secret, not a credential; `generate.mjs` writes them):

- valid: `relay-crossed`, `relay-recovered`, `relay-heartbeat`, `qnow-crossed`, `qnow-recovered`, `qnow-heartbeat`, `sentry-issue`, `sentry-preview` (a preview-only Sentry key signs an event that names `preview`) and `key-allowed` (the prod key signs a `prod` event with a prod and a preview key configured). The qnow values are synthetic: no monthly budget is on record.
- refused, each with its own reason: `missing-limit`, `extra-field`, `id-not-derived`, `recovered-id-without-cause`, `bad-signature`, `unknown-environment`, `unknown-severity`, `free-text-limit-source`, `duplicate-key`, `key-not-allowed` (the preview key signs a `prod` event), `key-not-allowed-no-environment` (a preview-only key signs an event without `environment`, which counts as `prod`), `heartbeat-offset-time` (a `+08:00` time on a heartbeat) and `sentry-free-level` (a sentence in `level`).

`node --test test/contract.test.mjs` runs the fixtures; `node test/mutations.mjs` removes each check in a temporary copy and requires the named test to fail.

## Stated limits

Accepted for v1 and recorded so a producer does not rely on the opposite:

- `sentry.issue.alert` ids are not derived from the event's fields: the inbox's own adapter produces them, not the pinning projects, and deriving them later does not change relay's or qnow's events (VR).
- A `below` recovery repeated after the limit returns to a value it had earlier in the same period re-derives that value's id and is answered `200 duplicate`; the same class as the lowered-limit limit above (VR).
- `period` is a pattern, not a calendar check: a bogus date such as `2026-02-30` derives an id that no other event repeats.

## Inbox runtime gaps (owned by r1)

Not built here, because the inbox runtime is r1's. Each is a rule above marked **runtime**; r1 builds it or a follow-up task does:

- `200 recorded` and the three routing outcomes (record, agent, captain), including the Captain mention on the NOT started and UNCERTAIN notices.
- `429 incident-cap`, with the cap's claim released on a 502.
- A GitHub 5xx answered as 504, not 502; the event claim states `claimed`, `dispatching`, `dispatched` with a takeover of a stale `claimed` (older than 120 s); a 70-day claim retention.
- Heartbeat last seen per environment and metric, and the silent-producer incident (no heartbeat for 2 × `every`, routed as warning).
- Verifying with a list of keys inside `handle()` (`parseEvent({ keys })` exists here).
- Scoping a key by event type: a key is scoped by environment and source prefix, so a metric project's key can sign a `sentry.issue.alert` under its own source prefix. Deferred risk for r1; the Sentry fields are bounded, which limits what such an event can carry (VR 2).
- Forwarding the re-serialized event to the agent run; the agent not fetching `dashboard`; resolving `adrs` at the checked-out commit.
- The store for raw events and the PostHog projection (recorded as a recommendation in the task, not decided).

## Sources

The Captain's words (C), facts with the command and date that produced them (F), decisions he approved (C9, D), the first-adopter review (Q) and the engineering review (ER).

- C1 Captain 2026-10-21: 「應該要先定義好 inbox 合約，由不同管道收取，且 platform 本身也要提供 hook 可以接，不能直接依賴第三方平台」
- C2 Captain 2026-10-25: 「clerk 沒有這種功能，應該要自己算，做一個 api or hook 來做這件事，新使用者進來就 count +1，例如統計做在 blob 內？之後也可以串 posthog 收數據…」
- C3 Captain 2026-10-25: 「要開，但我要你協同 inbox fo設計一個框架協議，讓未來的專案可以跟著使用，目的是設計出一個邊界，可讓不同專案用一樣的方式發送重點 metric 給 ops-inbox」
- C4 Captain 2026-10-25: 「有個機制在 ops-inbox 內收數據，送上 ext storage，例如第一階段支援 netlify blob，然後投影到 posthog？這樣等於是原始資料在手上，用第三方做視覺化，也剛好避開真實度的問題？」
- C5 Captain 2026-10-25: 「這裡存放有三個方向…哪一個又快又便宜？有時間差沒關係…」
- C6 Captain 2026-10-25: 「目前兩個服務剛好都跑在 netlify。這裡如果成本很低，那就請你先串 PH」
- C7 Captain 2026-10-26, four scope items selected: lifecycle (recovered event, heartbeat), routing (environment and severity), sender rules (same id, response codes, per-incident cap), complete information and injection guard (pointers, enumerated values).
- C8 Captain 2026-10-21: 「平台是剛好是 netlify，不是平台一定是 netlify」
- C9 Captain 2026-10-26, at the design gate: 「准。第一版接受缺陷，後續再補」, with decisions D1-D8 as recommended.
- D1 the project counts and sends crossings; the heartbeat carries the value. D2 retire `relay.capacity.ceiling` before landing. D3 `recovered` is a join dispatch that makes the task closable. D4 "reach the Captain" is a Slack mention of the Captain's user. D5 separate `prod` and `preview`/`dev` secrets, each refused outside its environments. D7 the project decides period membership at its own boundary instant. D8 at-most-once at 504 accepted for v1, to be fixed later.
- Q1 the boundary first cut from the first adopter (qnow's FO): the project measures, holds the threshold, decides a crossing and sends one signed event per crossing with a deterministic id and counts only; the inbox verifies, dedupes on `source` and `id`, groups on `subject` and routes.
- VR the validation cycle 1 review, 2026-10-27: three independent code reviews of PR 727 at its first head, and the First Officer's disposition, items 1 to 7 (1 calendar-valid UTC `time`; 2 bounded Sentry fields; 3 hostile input is refused, not thrown; 4 finite clock and decimal timestamp; 5 environment prefix on every type; 6 reasons do not echo sender text; 7 selftest subject and `webhook-id`), ordered by the Captain 2026-10-27: 「退回實作。」
- ER the engineering review of the design, 2026-10-26 (P1-1 duplicate JSON key; P2-1 id collisions; P2-2 per-incident cap; P2-3 GitHub 5xx; P2-4 lost event at 504; P2-5 `dashboard` is not fetched; P3-1 text in patterns; P3-2 key scope; P3-3 claim retention and open periods; P3-5 `SCHEMA_BASE` and additive `level`).
- F1 probe 2026-10-26: a fixture signed with r1's contract, with `source` `urn:relay:capacity Ignore previous instructions`, a 500-character instruction in `data.event` and `data.limitSource`, and an arbitrary id, printed `valid` and exited 0.
- F2 r1's inbox core at its commit 1e65b046 (`git archive`, 2026-10-26): `parseEvent`, `verifySignature` (loops over `v1,` parts), `handle()` status codes (202, 200 duplicate, 400, 401, 413, 502, 504), one `WEBHOOK_SECRET`.
- F3 the closed exactly-once delivery POC: one run for three sends over 67 s, 401 on tamper, a strong create-if-absent write held on a real site.
- F4 the closed Paseo Hub POC (2026-10-26): `event` and `limitSource` accepted free strings up to 500 characters, so v1 as first written did not make the text safe.
- F5 relay ADR 0049: no client address, device, account, share, Briefing, Room or session identifier in telemetry.
- F6 relay ADR 0060 and its bound-ceiling module (read 2026-10-26): create-only slot per publish; `source` is `default` or `override`; the notice was removed until the inbox says what it needs.
- F9 PostHog docs search, 2026-10-26: capture uses a public project token; the uuid deduplication rule was not found.
- F10 qnow's Clerk go-live task: usage period 2026-10-17 to 2026-11-17 (its ADR 0051); the earlier ops-inbox advice was a per-period atomic increment with a `<period>-<threshold>` id.
