# engineering-reviewer (opus) code review of PR #727 at 36973c77, 2026-10-27 (hand-back; a reviewer's words, not a ruling)

Verdict: sound with fixes. No P1.

- P2. The heartbeat id is cut from the raw `time` string, offset included, and `time` accepts impossible calendar values (`TYPES["ops.metric.heartbeat"].deriveId`, `TIME_RE` plus `Date.parse` in `validateBody`). Probe: `hb 10:30Z ok id=…hbd.2026-10-20T10 dedupe=27e5fc32794e`; `hb 11:30Z as -01:00 ok id=…hbd.2026-10-20T10 dedupe=27e5fc32794e`; `+14:00` gives bucket `2026-10-21T00`; `2026-02-31T10:00:00Z` and `2026-10-20T24:00:00Z` print `ok`. Pin-locked. Fix on `ops.metric.*`: require `time` to end in `Z` and `new Date(t).toISOString().slice(0,19) === t.slice(0,19)`; do not derive the bucket from `toISOString()` (Feb 31 rolls to March).
- P3-1. Refusal reasons repeat sender text (`unknown-type: ${ev.type}`, `field-not-allowed: ${name}`, `field-not-allowed: data.${name}`): 364- and 2053-character reasons with newlines and instruction text; object type gives `unknown-type: [object Object]`. Fix: cut to `[A-Za-z0-9._-]{1,64}` or drop.
- P3-2. README understates `sentry.issue.alert` free text: `event_id`, `level`, `project`, `triggered_rule`, `release` are bare strings up to 500 characters; `issue_id` limited only via `subject-mismatch`. Fix: list every free field; optionally restrict `level` to Sentry's five values now.
- P3-3. Transport rule `webhook-id` = `msg_<event id>` is neither checked by `parseEvent` nor marked runtime.
- Holds: canonical body (duplicate keys, `1e3`, `-0`, escaped non-ASCII refused); key scope; derived ids do not collide, longest 64; no crash found with `__proto__`, 8000-deep arrays, 3000-deep objects (FO probe 2026-10-27 contradicts this: `validateBody` on 7000- and 8000-deep arrays throws `RangeError: Maximum call stack size exceeded`).
- Design vs code: matches; the `keyScope` prefix for non-prod non-metric events is an addition consistent with D5 and ER P3-2.
Evidence: node v24.18.0, 19/19 tests, all mutations caught; probe /tmp/er-probe-opsmetric/probe.mjs.
