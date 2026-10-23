# kc-ops-inbox contract v1

What a producer sends to the inbox. The rules are executable in `core/inbox-core.mjs` (`parseEvent`); the published schemas in `v1/` are derived from the same table by `generate.mjs`, and `contract-versions.json` pins each schema's digest.

## Transport

`POST` the CloudEvent as the raw request body (structured JSON, at most 16 KiB) with the Standard Webhooks headers:

| Header | Value |
| --- | --- |
| `webhook-id` | any string unique to this send's event, for example `msg_<event id>` |
| `webhook-timestamp` | Unix seconds; the inbox refuses a difference over 300 s from its clock |
| `webhook-signature` | `v1,<base64 HMAC-SHA256 of "<webhook-id>.<webhook-timestamp>.<raw body>">`, key = the base64 part of the `whsec_` secret |

A retry may re-sign (new timestamp) and must keep the CloudEvent `id`: the inbox drops a repeat of `source` + `id`.

## Envelope

| Attribute | Rule |
| --- | --- |
| `specversion` | `"1.0"` |
| `id` | `^[A-Za-z0-9._-]{1,64}$`; unique within `source` |
| `source` | non-empty, at most 200 characters; names the producer |
| `type` | `relay.capacity.ceiling` or `sentry.issue.alert` |
| `subject` | `^[A-Za-z0-9._/-]{1,100}$` and the per-type rule below; the incident within the source |
| `time` | RFC 3339 |
| `dataschema` | `https://github.com/iamcxa/kc-claude-plugins/blob/main/kc-ops-inbox/contract/v1/<type>.json` |
| `datacontenttype` | optional, `application/json` |
| `data` | the per-type fields below |

Any other attribute, and any `data` field outside the list, is refused, not dropped.

## Types

`relay.capacity.ceiling` — subject `ceiling/<tier>/<day>`, `<day>` equal to `data.day`. Data (all required): `v` (integer >= 1), `event`, `at` (RFC 3339), `day` (`YYYY-MM-DD`), `count`, `limit` (integers >= 0), `limitSource`. Holds no account identifier (relay ADR 0049).

`sentry.issue.alert` — subject `issue/<issue_id>`. Data: required `issue_id`, `title`, `level`, `project`, `web_url` (`https://`); optional `event_id`, `culprit`, `triggered_rule`, `datetime`, `release`. Strings are at most 500 characters.

## Keys

- dedupe: `sha256(source + "\n" + id)` — a repeat is accepted once.
- incident: `sha256(source + "\n" + subject)` — events with one incident key join one ops task.

## Versions

An incompatible change gets `v2` with its own schemas and `dataschema`. A compatible change to v1 re-pins `contract-versions.json` in the same commit, and `test/contract.test.mjs` fails until it does.

## Check an event

```
node contract/validate.mjs contract/fixtures/relay-ceiling-near.json
```

Fixture shape: `{ secret?, now?, headers, body }` (`secret` falls back to `OPS_WEBHOOK_SECRET`; `now` to the clock; `--now <epoch>` overrides). Exit 0 prints `valid <type> <dedupe key> <incident key>`; exit 1 prints one reason (`missing-attribute: <name>`, `signature-mismatch`, `timestamp-out-of-tolerance`, `missing-headers`, `field-not-allowed: <path>`, `unknown-type: <type>`, `invalid-value: <path>`, `subject-mismatch`, `not-json`, `body-too-large`); exit 2 is a usage error. The fixtures use a published test secret, not a credential.
