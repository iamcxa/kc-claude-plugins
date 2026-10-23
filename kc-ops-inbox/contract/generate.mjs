#!/usr/bin/env node
// Writes the published v1 schemas and the signed fixtures from core/inbox-core.mjs. Deterministic: HMAC has no nonce.
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { TYPES, SCHEMA_BASE, jsonSchemaFor, signBody } from "../core/inbox-core.mjs";

const here = dirname(fileURLToPath(import.meta.url));
export const FIXTURE_SECRET = "whsec_" + Buffer.from("kc-ops-inbox-fixture-secret-not-a-credential").toString("base64");
const NOW_S = Math.floor(Date.parse("2026-10-20T00:00:30Z") / 1000);

const relay = (id, event, count) => ({
  specversion: "1.0",
  id,
  source: "urn:relay:capacity",
  type: "relay.capacity.ceiling",
  subject: "ceiling/signed-in/2026-10-20",
  time: "2026-10-20T00:00:00Z",
  dataschema: `${SCHEMA_BASE}/relay.capacity.ceiling.json`,
  datacontenttype: "application/json",
  data: { v: 1, event, at: "2026-10-20T00:00:00Z", day: "2026-10-20", count, limit: 50, limitSource: "default" },
});

const sentry = () => ({
  specversion: "1.0",
  id: "sentry-evt-1",
  source: "urn:sentry:issue-alert",
  type: "sentry.issue.alert",
  subject: "issue/4242",
  time: "2026-10-20T00:00:00Z",
  dataschema: `${SCHEMA_BASE}/sentry.issue.alert.json`,
  datacontenttype: "application/json",
  data: { issue_id: "4242", event_id: "abc123", title: "TypeError: x is undefined", level: "error", culprit: "app/main", project: "demo", web_url: "https://sentry.example/issues/4242/" },
});

function fixture(event, { sign = true, tamper = false } = {}) {
  let body = JSON.stringify(event);
  const id = `msg_${event.id ?? "fixture"}`;
  const timestamp = String(NOW_S);
  const signature = signBody({ secret: FIXTURE_SECRET, id, timestamp, body });
  if (tamper) body = body.replace("signed-in", "signed-on");
  return { secret: FIXTURE_SECRET, now: NOW_S, headers: { "webhook-id": id, "webhook-timestamp": timestamp, "webhook-signature": signature }, body };
}

const without = (event, key) => { const { [key]: _, ...rest } = event; return rest; };
const near = relay("signed-in-2026-10-20-80", "bound-ceiling-near", 40);

export const FIXTURES = {
  "relay-ceiling-near.json": fixture(near),
  "relay-ceiling-full.json": fixture(relay("signed-in-2026-10-20-100", "bound-ceiling-full", 50)),
  "sentry-issue.json": fixture(sentry()),
  "missing-source.json": fixture(without(near, "source")),
  "missing-subject.json": fixture(without(near, "subject")),
  "bad-signature.json": fixture(near, { tamper: true }),
  "extra-field.json": fixture({ ...near, data: { ...near.data, user: "someone" } }),
};

if (import.meta.url === `file://${process.argv[1]}`) {
  for (const type of Object.keys(TYPES)) writeFileSync(join(here, "v1", `${type}.json`), JSON.stringify(jsonSchemaFor(type), null, 2) + "\n");
  for (const [name, f] of Object.entries(FIXTURES)) writeFileSync(join(here, "fixtures", name), JSON.stringify(f, null, 2) + "\n");
}
