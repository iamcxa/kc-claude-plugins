import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";
import { parseEvent, validateBody, verifySignature, isUsableKey, jsonSchemaFor, TYPES, signBody, SCHEMA_BASE, ENVIRONMENTS, MIN_KEY_BYTES } from "../contract/contract.mjs";
import { FIXTURES, FIXTURE_SECRET, PROD_KEY, PREVIEW_KEY } from "../contract/generate.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const validate = (name, extra = []) =>
  spawnSync("node", [join(root, "contract/validate.mjs"), join(root, "contract/fixtures", name), ...extra], { encoding: "utf8" });

test("valid fixtures print the type and both keys, exit 0", () => {
  const valid = ["relay-crossed", "relay-recovered", "relay-heartbeat", "qnow-crossed", "qnow-recovered", "qnow-heartbeat", "sentry-issue", "sentry-preview", "key-allowed"];
  for (const name of valid) {
    const r = validate(`${name}.json`);
    assert.equal(r.status, 0, name);
    assert.match(r.stdout, /^valid (ops\.metric\.(crossed|recovered|heartbeat)|sentry\.issue\.alert) [0-9a-f]{64} [0-9a-f]{64}\n$/, name);
  }
});

test("each refusal fixture is refused with its own reason, exit 1", () => {
  const want = {
    "missing-limit.json": "missing-attribute: data.limit",
    "extra-field.json": "field-not-allowed: data.user",
    "id-not-derived.json": "id-not-deterministic",
    "recovered-id-without-cause.json": "id-not-deterministic",
    "bad-signature.json": "signature-mismatch",
    "unknown-environment.json": "invalid-value: environment",
    "unknown-severity.json": "invalid-value: severity",
    "free-text-limit-source.json": "invalid-value: data.limitSource",
    "duplicate-key.json": "non-canonical-body",
    "key-not-allowed.json": "key-not-allowed",
    "key-not-allowed-no-environment.json": "key-not-allowed",
    "heartbeat-offset-time.json": "invalid-value: time",
    "sentry-free-level.json": "invalid-value: data.level",
  };
  assert.deepEqual(Object.keys(want).concat(["relay-crossed", "relay-recovered", "relay-heartbeat", "qnow-crossed", "qnow-recovered", "qnow-heartbeat", "sentry-issue", "sentry-preview", "key-allowed"].map((n) => `${n}.json`)).sort(), Object.keys(FIXTURES).sort());
  for (const [name, reason] of Object.entries(want)) {
    const r = validate(name);
    assert.equal(r.status, 1, name);
    assert.equal(r.stdout.trim(), reason, name);
  }
});

test("the preview key's copy is refused and the prod key's copy of the same event is valid", () => {
  const body = (n) => JSON.parse(FIXTURES[n].body);
  assert.deepEqual(body("key-allowed.json"), body("key-not-allowed.json"));
  assert.equal(body("key-allowed.json").environment, "prod");
  assert.deepEqual(FIXTURES["key-allowed.json"].keys, FIXTURES["key-not-allowed.json"].keys);
});

test("validator exits 2 on a usage error", () => {
  assert.equal(spawnSync("node", [join(root, "contract/validate.mjs")], { encoding: "utf8" }).status, 2);
  assert.equal(validate("relay-crossed.json", ["--now", "abc"]).status, 2);
});

test("a fixture checked an hour later is refused as stale", () => {
  const r = validate("relay-crossed.json", ["--now", String(FIXTURES["relay-crossed.json"].now + 3600)]);
  assert.equal(r.status, 1);
  assert.equal(r.stdout.trim(), "timestamp-out-of-tolerance");
});

test("a crossing and its recovery share an incident key, differ in dedupe key, and a heartbeat has its own incident", () => {
  const keys = (n) => validate(n).stdout.trim().split(" ").slice(2);
  const [crossedDedupe, crossedIncident] = keys("relay-crossed.json");
  const [recoveredDedupe, recoveredIncident] = keys("relay-recovered.json");
  const [, heartbeatIncident] = keys("relay-heartbeat.json");
  assert.equal(crossedIncident, recoveredIncident);
  assert.notEqual(crossedDedupe, recoveredDedupe);
  assert.notEqual(crossedIncident, heartbeatIncident);
});

const allKey = { secret: FIXTURE_SECRET, environments: ENVIRONMENTS, sources: ["urn:"] };
function signed(event, { keys = [allKey], secret = FIXTURE_SECRET, nowS = 1_800_000_000 } = {}) {
  const body = typeof event === "string" ? event : JSON.stringify(event);
  const id = "msg_t";
  const headers = new Headers({ "webhook-id": id, "webhook-timestamp": String(nowS), "webhook-signature": signBody({ secret, id, timestamp: String(nowS), body }) });
  return { keys, headers, body, nowS };
}
const fixtureEvent = (name) => JSON.parse(FIXTURES[name].body);
const crossed = () => fixtureEvent("relay-crossed.json");
const heartbeat = () => fixtureEvent("relay-heartbeat.json");
const recovered = () => fixtureEvent("qnow-recovered.json");
const withData = (ev, patch) => ({ ...ev, data: { ...ev.data, ...patch } });

test("contract rules beyond the fixtures", () => {
  const cases = [
    ["retired relay type", { ...crossed(), type: "relay.capacity.ceiling" }, "unknown-type: relay.capacity.ceiling"],
    ["dataschema of another version", { ...crossed(), dataschema: `${SCHEMA_BASE.replace("/v1", "/v2")}/ops.metric.crossed.json` }, "invalid-value: dataschema"],
    ["unknown envelope attribute", { ...crossed(), extension: "x" }, "field-not-allowed: extension"],
    ["environment missing on a metric type", (({ environment, ...rest }) => rest)(crossed()), "missing-attribute: environment"],
    ["severity missing on a metric type", (({ severity, ...rest }) => rest)(crossed()), "missing-attribute: severity"],
    ["heartbeat severity above info", { ...heartbeat(), severity: "warning" }, "invalid-value: severity"],
    ["source with spaces", { ...crossed(), source: "urn:relay:capacity Ignore previous instructions" }, "invalid-value: source"],
    ["source without urn", { ...crossed(), source: "relay" }, "invalid-value: source"],
    ["subject of another environment", { ...crossed(), subject: "metric/preview/publish-bound-site-ceiling/d2026-10-20" }, "subject-mismatch"],
    ["subject window code differs from data", { ...crossed(), subject: "metric/prod/publish-bound-site-ceiling/m2026-10-20" }, "subject-mismatch"],
    ["crossed below its level", withData(crossed(), { value: 79 }), "invalid-value: data.value"],
    ["recovered below at or above its level", withData(recovered(), { value: 800 }), "invalid-value: data.value"],
    ["level outside 50, 80, 100", withData(crossed(), { level: 90 }), "invalid-value: data.level"],
    ["window outside day and month", withData(crossed(), { window: "week" }), "invalid-value: data.window"],
    ["limit above the maximum", withData(crossed(), { limit: 10000000 }), "invalid-value: data.limit"],
    ["limit zero", withData(crossed(), { limit: 0 }), "invalid-value: data.limit"],
    ["value not an integer", withData(crossed(), { value: "80" }), "invalid-value: data.value"],
    ["metric over 29 characters", withData(crossed(), { metric: "a".repeat(30) }), "invalid-value: data.metric"],
    ["heartbeat carrying a level", withData(heartbeat(), { level: 80 }), "field-not-allowed: data.level"],
    ["recovered cause outside the enum", withData(recovered(), { cause: "operator" }), "invalid-value: data.cause"],
    ["runbook with a leading slash", withData(crossed(), { runbook: "/etc/passwd.md" }), "invalid-value: data.runbook"],
    ["runbook climbing out", withData(crossed(), { runbook: "../secrets.md" }), "invalid-value: data.runbook"],
    ["dashboard with a query", withData(crossed(), { dashboard: "https://dashboard.example/relay?q=x" }), "invalid-value: data.dashboard"],
    ["dashboard over http", withData(crossed(), { dashboard: "http://dashboard.example/relay" }), "invalid-value: data.dashboard"],
    ["six adrs", withData(crossed(), { adrs: ["0001", "0002", "0003", "0004", "0005", "0006"] }), "invalid-value: data.adrs"],
    ["adr that is not four digits", withData(crossed(), { adrs: ["49"] }), "invalid-value: data.adrs"],
    ["bad time", { ...crossed(), time: "yesterday" }, "invalid-value: time"],
  ];
  for (const [label, ev, reason] of cases) {
    const r = parseEvent(signed(ev));
    assert.equal(r.ok, false, label);
    assert.equal(r.reason, reason, label);
    assert.equal(r.status, 400, label);
  }
  assert.equal(parseEvent(signed(crossed())).ok, true);
});

test("a non-canonical body is refused whatever its type", () => {
  const pretty = JSON.stringify(heartbeat(), null, 1);
  assert.equal(parseEvent(signed(pretty)).reason, "non-canonical-body");
  const sentry = JSON.stringify(fixtureEvent("sentry-issue.json")).replace('"project":"demo"', '"project":"x","project":"demo"');
  assert.equal(parseEvent(signed(sentry)).reason, "non-canonical-body");
});

test("heartbeat ids are cut to the hour or the day of time", () => {
  const hourly = { ...heartbeat(), data: { ...heartbeat().data, every: "hour" }, id: "publish-bound-site-ceiling.prod.hbd.2026-10-20T03" };
  assert.equal(parseEvent(signed(hourly)).ok, true);
  assert.equal(parseEvent(signed({ ...hourly, id: "publish-bound-site-ceiling.prod.hbd.2026-10-20" })).reason, "id-not-deterministic");
});

test("the four ids of relay's ceiling in one day are distinct and derive from the event", () => {
  const stem = "publish-bound-site-ceiling.prod.d2026-10-20";
  const steps = [
    ["crossed", { value: 80, level: 80, limit: 100 }, `${stem}.c80.l100`],
    ["recovered", { value: 80, level: 80, limit: 200, cause: "below" }, `${stem}.r80b.l200`],
    ["crossed", { value: 160, level: 80, limit: 200 }, `${stem}.c80.l200`],
    ["recovered", { value: 160, level: 80, limit: 200, cause: "period-ended" }, `${stem}.r80p.l200`],
  ];
  for (const [kind, data, id] of steps) {
    const ev = { ...crossed(), type: `ops.metric.${kind}`, id, dataschema: `${SCHEMA_BASE}/ops.metric.${kind}.json`, data: { ...crossed().data, ...data } };
    assert.equal(parseEvent(signed(ev)).ok, true, id);
  }
  assert.equal(new Set(steps.map((s) => s[2])).size, 4);
});

test("the longest id fits the id pattern and a 30-character metric does not exist", () => {
  const metric = "a".repeat(29);
  const ev = {
    ...crossed(), environment: "preview", id: `${metric}.preview.m2026-10-20.r100p.l9999999`, type: "ops.metric.recovered",
    dataschema: `${SCHEMA_BASE}/ops.metric.recovered.json`, subject: `metric/preview/${metric}/m2026-10-20`,
    data: { ...crossed().data, metric, window: "month", level: 100, limit: 9999999, cause: "period-ended" },
  };
  assert.equal(ev.id.length, 64);
  assert.equal(parseEvent(signed(ev)).ok, true);
});

test("a key signs only the environments and the source prefixes it lists", () => {
  const key = (environments, sources, secret = FIXTURE_SECRET) => ({ secret, environments, sources });
  const cases = [
    ["environment not listed", crossed(), [key(["preview", "dev"], ["urn:relay:"])]],
    ["source prefix not listed", crossed(), [key(ENVIRONMENTS, ["urn:qnow:"])]],
    ["an event without environment needs a prod key", fixtureEvent("sentry-issue.json"), [key(["preview", "dev"], ["urn:"])]],
  ];
  for (const [label, ev, keys] of cases) assert.equal(parseEvent(signed(ev, { keys })).reason, "key-not-allowed", label);
  assert.equal(parseEvent(signed(fixtureEvent("sentry-issue.json"), { keys: [key(["prod"], ["urn:sentry:"])] })).ok, true);
  assert.equal(parseEvent(signed(crossed(), { keys: [PROD_KEY, PREVIEW_KEY], secret: PROD_KEY.secret })).ok, true);
});

test("a non-prod event is keyed apart from the prod event with the same source and id, whatever the type", () => {
  const keys = (n) => validate(n).stdout.trim().split(" ").slice(2);
  const sha = (x) => createHash("sha256").update(x).digest("hex");
  const [prodDedupe, prodIncident] = keys("sentry-issue.json");
  const [previewDedupe, previewIncident] = keys("sentry-preview.json");
  assert.notEqual(previewDedupe, prodDedupe);
  assert.notEqual(previewIncident, prodIncident);
  const { source, id, subject } = fixtureEvent("sentry-issue.json");
  assert.deepEqual([prodDedupe, prodIncident], [sha(`${source}\n${id}`), sha(`${source}\n${subject}`)]);
  assert.equal(keys("relay-crossed.json")[0], sha("urn:relay:capacity\npublish-bound-site-ceiling.prod.d2026-10-20.c80.l100"));

  const preview = { ...crossed(), environment: "preview", severity: "critical", id: "publish-bound-site-ceiling.preview.d2026-10-20.c80.l100", subject: "metric/preview/publish-bound-site-ceiling/d2026-10-20" };
  const result = parseEvent(signed(preview));
  assert.equal(result.ok, true);
  assert.equal(result.keys.dedupe, sha(`preview\nurn:relay:capacity\n${preview.id}`));
  assert.equal(result.keys.incident, sha(`preview\nurn:relay:capacity\n${preview.subject}`));
  const colliding = { ...fixtureEvent("sentry-issue.json"), type: "ops.inbox.selftest", id: preview.id, subject: `selftest/${preview.id}`, source: "urn:relay:capacity", dataschema: `${SCHEMA_BASE}/ops.inbox.selftest.json`, data: { v: 1, project: "o/n" } };
  assert.notEqual(parseEvent(signed(colliding)).keys.dedupe, result.keys.dedupe);
});

test("a signature header with an old and a new key's signature is accepted by either key", () => {
  const ev = signed(crossed());
  const other = signBody({ secret: PREVIEW_KEY.secret, id: "msg_t", timestamp: "1800000000", body: ev.body });
  ev.headers.set("webhook-signature", `${other} ${ev.headers.get("webhook-signature")}`);
  assert.equal(parseEvent(ev).ok, true);
});

test("a body over 16 KiB is refused before it is trusted", () => {
  const r = parseEvent(signed({ ...crossed(), padding: "x".repeat(20000) }));
  assert.deepEqual([r.status, r.reason], [413, "body-too-large"]);
});

test("a bad signature is a 401 and wins over a contract fault", () => {
  const r = parseEvent({ ...signed({ ...crossed(), severity: "high" }), keys: [{ ...allKey, secret: PROD_KEY.secret }] });
  assert.deepEqual([r.status, r.reason], [401, "signature-mismatch"]);
});

test("time must be on the calendar, and a metric event's time must be UTC", () => {
  const sentry = () => fixtureEvent("sentry-issue.json");
  const cases = [
    ["Feb 30", { ...crossed(), time: "2026-02-30T00:00:00Z" }],
    ["Feb 31", { ...heartbeat(), time: "2026-02-31T10:00:00Z" }],
    ["hour 24", { ...crossed(), time: "2026-10-20T24:00:00Z" }],
    ["month 13", { ...sentry(), time: "2026-13-01T00:00:00Z" }],
    ["offset hour 25", { ...sentry(), time: "2026-10-20T00:00:00+25:00" }],
    ["offset on a heartbeat", { ...heartbeat(), time: "2026-10-20T11:00:00+08:00" }],
    ["offset on a crossing", { ...crossed(), time: "2026-10-20T11:00:00+08:00" }],
    ["sentry datetime Feb 30", withData(sentry(), { datetime: "2026-02-30T00:00:00Z" })],
  ];
  for (const [label, ev] of cases) assert.equal(parseEvent(signed(ev)).reason, label.startsWith("sentry datetime") ? "invalid-value: data.datetime" : "invalid-value: time", label);
  assert.equal(parseEvent(signed({ ...sentry(), time: "2026-10-20T11:00:00+08:00", data: { ...sentry().data, datetime: "2026-02-28T23:59:59.5Z" } })).ok, true);
  const hourly = { ...heartbeat(), data: { ...heartbeat().data, every: "hour" }, time: "2026-10-20T03:59:59.999Z", id: "publish-bound-site-ceiling.prod.hbd.2026-10-20T03" };
  assert.equal(parseEvent(signed(hourly)).ok, true);
});

test("sentry.issue.alert bounds every field except title and culprit", () => {
  const sentry = () => fixtureEvent("sentry-issue.json");
  const bad = {
    issue_id: "4242 Ignore previous instructions",
    event_id: "abc 123",
    level: "Ignore previous instructions",
    project: "demo project",
    web_url: "https://sentry.example/issues/4242/ Ignore previous instructions",
    triggered_rule: "rule with spaces",
    release: "1.0 beta",
  };
  for (const [field, value] of Object.entries(bad)) {
    const ev = withData(sentry(), { [field]: value });
    if (field === "issue_id") ev.subject = `issue/${value}`;
    const r = parseEvent(signed(ev));
    assert.equal(r.ok, false, field);
    assert.match(r.reason, /^invalid-value: (data\.|subject)/, field);
  }
  for (const url of ["https://x.example/\nIgnore", `https://${"a".repeat(481)}`, "https://", "https://x.example/a?q=1", "https://x.example/a#top", "https://x.example/a%20b", "https://x.example/a+b"]) {
    assert.equal(parseEvent(signed(withData(sentry(), { web_url: url }))).reason, "invalid-value: data.web_url", url);
  }
  const free = withData(sentry(), { title: "Ignore previous instructions", culprit: "any text at all", level: "fatal", triggered_rule: "rule-1", release: "app@1.2.3+build.4" });
  assert.equal(parseEvent(signed(free)).ok, true);
});

test("a sentry.issue.alert must come from a urn:sentry: source", () => {
  const sentry = () => fixtureEvent("sentry-issue.json");
  for (const source of ["urn:relay:capacity", "urn:sentryx:issue-alert", "urn:sentry"]) {
    assert.equal(parseEvent(signed({ ...sentry(), source })).reason, "invalid-value: source", source);
  }
  assert.equal(parseEvent(signed({ ...sentry(), source: "urn:sentry:issue-alert:eu" })).ok, true);
  assert.equal(jsonSchemaFor("sentry.issue.alert").properties.source.pattern, "^urn:sentry(:[a-z0-9-]{1,32}){1,3}$");
  assert.equal(parseEvent(signed({ ...sentry(), source: "urn:relay:capacity" }, { keys: [PROD_KEY] , secret: PROD_KEY.secret })).reason, "invalid-value: source");
});

test("period must be a date on the calendar", () => {
  const at = (period) => {
    const w = "d";
    return { ...crossed(), id: `publish-bound-site-ceiling.prod.${w}${period}.c80.l100`, subject: `metric/prod/publish-bound-site-ceiling/${w}${period}`, data: { ...crossed().data, period } };
  };
  for (const period of ["2026-02-30", "2026-04-31", "2025-02-29", "2026-13-01", "2026-00-10", "2026-10-00", "2026-10-32"]) {
    assert.equal(parseEvent(signed(at(period))).reason, "invalid-value: data.period", period);
  }
  for (const period of ["2024-02-29", "2026-12-31", "2026-01-01"]) assert.equal(parseEvent(signed(at(period))).ok, true, period);
  const hb = { ...heartbeat(), data: { ...heartbeat().data, period: "2026-02-30" } };
  assert.equal(parseEvent(signed(hb)).reason, "invalid-value: data.period");
});

test("a key that cannot sign anything is skipped, never used and never thrown on", () => {
  const good = { secret: FIXTURE_SECRET, environments: ENVIRONMENTS, sources: ["urn:"] };
  const unusable = {
    "empty secret": { ...good, secret: "" },
    "prefix-only secret": { ...good, secret: "whsec_" },
    "no environments": { ...good, environments: [] },
    "empty environment": { ...good, environments: [""] },
    "environment not a string": { ...good, environments: [1] },
    "no sources": { ...good, sources: [] },
    "empty source prefix": { ...good, sources: [""] },
    "prefix without trailing colon": { ...good, sources: ["urn:relay"] },
    "source not a string": { ...good, sources: [null] },
    "environments not an array": { ...good, environments: "prod" },
  };
  for (const [label, key] of Object.entries(unusable)) {
    assert.equal(isUsableKey(key), false, label);
    const r = parseEvent(signed(crossed(), { keys: [key], secret: key.secret === "whsec_" || key.secret === "" ? key.secret : FIXTURE_SECRET }));
    assert.deepEqual([r.ok, r.reason], [false, "signature-mismatch"], label);
  }
  assert.equal(isUsableKey(good), true);
  assert.equal(parseEvent(signed(crossed(), { keys: [unusable["no sources"], good] })).ok, true);
});

test("a secret that decodes to fewer than 16 bytes verifies no signature, forged or not", () => {
  const weak = ["whsec_=", "whsec_!!!", "!!!", "whsec_a", "whsec_ ", "whsec_AAAAAAAAAAAAAAA", "whsec_" + Buffer.alloc(MIN_KEY_BYTES - 1, 7).toString("base64")];
  for (const secret of weak) {
    const forged = signed(crossed(), { secret });
    const key = { secret, environments: ENVIRONMENTS, sources: ["urn:"] };
    assert.equal(isUsableKey(key), false, secret);
    assert.deepEqual([parseEvent({ ...forged, keys: [key] }).ok, parseEvent({ ...forged, keys: [key] }).reason], [false, "signature-mismatch"], secret);
    const id = forged.headers.get("webhook-id");
    const signatureHeader = forged.headers.get("webhook-signature");
    assert.equal(verifySignature({ secret, id, timestamp: "1800000000", signatureHeader, body: forged.body, nowS: 1_800_000_000 }), "signature-mismatch", secret);
  }
  const edge = "whsec_" + Buffer.alloc(MIN_KEY_BYTES, 7).toString("base64");
  assert.equal(isUsableKey({ secret: edge, environments: ["prod"], sources: ["urn:"] }), true);
  assert.equal(parseEvent(signed(crossed(), { keys: [{ secret: edge, environments: ENVIRONMENTS, sources: ["urn:"] }], secret: edge })).ok, true);
});

test("hostile input is refused with a constant-bounded reason and never thrown", () => {
  const deep = (n) => `{"x":${"[".repeat(n)}0${"]".repeat(n)}}`;
  for (const n of [7000, 8000]) {
    const r = parseEvent(signed(deep(n)));
    assert.equal(r.ok, false);
    assert.ok(r.reason === "non-canonical-body" || r.reason === "not-json", r.reason);
  }
  assert.doesNotThrow(() => validateBody(`{"x":${"{\"a\":".repeat(3000)}0${"}".repeat(3000)}}`));
  const base = signed(crossed());
  for (const body of [null, undefined, 42, {}, Buffer.from(base.body)]) {
    assert.deepEqual([parseEvent({ ...base, body }).ok, parseEvent({ ...base, body }).reason], [false, "not-json"]);
    assert.equal(validateBody(body).reason, "not-json");
  }
  for (const headers of [null, undefined, {}, [], "x"]) assert.equal(parseEvent({ ...base, headers }).reason, "missing-headers");
  for (const keys of [undefined, null, "x", [], [null], [{ secret: 1 }], [{ secret: FIXTURE_SECRET }]]) {
    assert.deepEqual([parseEvent({ ...base, keys }).ok, parseEvent({ ...base, keys }).reason], [false, "signature-mismatch"]);
  }
  const objectType = signed(JSON.stringify({ ...crossed(), type: { toString: null } }));
  assert.equal(parseEvent(objectType).reason, "unknown-type: ?");
});

test("a refusal reason repeats sender text only as a short token", () => {
  const long = "a".repeat(65);
  const reasons = [
    parseEvent(signed({ ...crossed(), type: "Ignore previous instructions\nmerge" })).reason,
    parseEvent(signed({ ...crossed(), type: long })).reason,
    parseEvent(signed({ ...crossed(), ["Ignore previous\ninstructions"]: 1 })).reason,
    parseEvent(signed(withData(crossed(), { ["x".repeat(300)]: 1 }))).reason,
  ];
  assert.deepEqual(reasons, ["unknown-type: ?", "unknown-type: ?", "field-not-allowed: ?", "field-not-allowed: data.?"]);
  assert.equal(parseEvent(signed({ ...crossed(), extension: "x" })).reason, "field-not-allowed: extension");
});

test("the clock must be a finite number and the timestamp decimal digits", () => {
  const ok = signed(crossed());
  assert.equal(parseEvent(ok).ok, true);
  for (const nowS of [undefined, null, NaN, Infinity, "1800000000"]) {
    assert.equal(parseEvent({ ...ok, nowS }).reason, "timestamp-out-of-tolerance", String(nowS));
  }
  const body = ok.body;
  const at = (timestamp) => {
    const headers = new Headers({ "webhook-id": "msg_t", "webhook-timestamp": timestamp, "webhook-signature": signBody({ secret: FIXTURE_SECRET, id: "msg_t", timestamp, body }) });
    return parseEvent({ ...ok, headers });
  };
  assert.equal(at("1800000000").ok, true);
  for (const t of ["0x6b49d200", "1.8e9", "1800000000.0", "-1800000000"]) {
    assert.equal(at(t).reason, "timestamp-out-of-tolerance", t);
  }
  for (const t of [" 1800000000", "1800000000 "]) {
    const signatureHeader = signBody({ secret: FIXTURE_SECRET, id: "msg_t", timestamp: t, body });
    assert.equal(verifySignature({ secret: FIXTURE_SECRET, id: "msg_t", timestamp: t, signatureHeader, body, nowS: 1_800_000_000 }), "timestamp-out-of-tolerance", JSON.stringify(t));
  }
  assert.equal(verifySignature({ secret: FIXTURE_SECRET, id: "a", timestamp: "1", signatureHeader: "v1,x", body: "{}", nowS: undefined }), "timestamp-out-of-tolerance");
});

test("an ops.inbox.selftest subject must be selftest/<id>", () => {
  const selftest = (subject) => ({ ...fixtureEvent("sentry-issue.json"), type: "ops.inbox.selftest", id: "one", subject, dataschema: `${SCHEMA_BASE}/ops.inbox.selftest.json`, data: { v: 1, project: "o/n" } });
  assert.equal(parseEvent(signed(selftest("selftest/one"))).ok, true);
  assert.equal(parseEvent(signed(selftest("selftest/two"))).reason, "subject-mismatch");
});

test("the validator exits 2 on a malformed fixture and never mistakes a crash for a refusal", () => {
  const dir = mkdtempSync(join(tmpdir(), "ops-contract-fixture-"));
  try {
    const good = FIXTURES["relay-crossed.json"];
    const bad = {
      "null.json": "null",
      "array.json": "[]",
      "headers-null.json": JSON.stringify({ ...good, headers: null }),
      "headers-array.json": JSON.stringify({ ...good, headers: [] }),
      "headers-name.json": JSON.stringify({ ...good, headers: { "bad name": "x" } }),
      "body-number.json": JSON.stringify({ ...good, body: 42 }),
      "keys-string.json": JSON.stringify({ keys: "x", headers: good.headers, body: good.body }),
      "keys-empty.json": JSON.stringify({ keys: [], headers: good.headers, body: good.body }),
      "key-no-secret.json": JSON.stringify({ keys: [{ environments: [], sources: [] }], headers: good.headers, body: good.body }),
      "key-prefix-only-secret.json": JSON.stringify({ keys: [{ secret: "whsec_", environments: ["prod"], sources: ["urn:"] }], headers: good.headers, body: good.body }),
      "key-short-secret.json": JSON.stringify({ keys: [{ secret: "whsec_a", environments: ["prod"], sources: ["urn:"] }], headers: good.headers, body: good.body }),
      "key-source-without-colon.json": JSON.stringify({ keys: [{ secret: FIXTURE_SECRET, environments: ["prod"], sources: ["urn:relay"] }], headers: good.headers, body: good.body }),
      "key-empty-environments.json": JSON.stringify({ keys: [{ secret: FIXTURE_SECRET, environments: [], sources: ["urn:"] }], headers: good.headers, body: good.body }),
      "now-text.json": JSON.stringify({ ...good, now: "bad" }),
    };
    for (const [name, text] of Object.entries(bad)) {
      writeFileSync(join(dir, name), text);
      const r = spawnSync("node", [join(root, "contract/validate.mjs"), join(dir, name)], { encoding: "utf8" });
      assert.equal(r.status, 2, name);
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("validateBody applies the contract rules without a signature", () => {
  assert.equal(validateBody(JSON.stringify(crossed())).ok, true);
  assert.equal(validateBody(JSON.stringify({ ...crossed(), severity: "high" })).reason, "invalid-value: severity");
});

test("the published schemas equal the ones derived from the code and match the pinned digests", () => {
  const pins = JSON.parse(readFileSync(join(root, "contract/contract-versions.json"), "utf8")).v1;
  assert.deepEqual(Object.keys(pins).sort(), Object.keys(TYPES).sort());
  assert.deepEqual(readdirSync(join(root, "contract/v1")).sort(), Object.keys(TYPES).map((t) => `${t}.json`).sort());
  for (const type of Object.keys(TYPES)) {
    const file = readFileSync(join(root, "contract/v1", `${type}.json`));
    assert.deepEqual(JSON.parse(file), jsonSchemaFor(type), `${type}: schema file differs from code; run contract/generate.mjs`);
    assert.equal(`sha256:${createHash("sha256").update(file).digest("hex")}`, pins[type], `${type}: v1 changed; an incompatible change needs v2, a compatible one re-pins`);
  }
});

test("the committed fixtures equal the generated ones", () => {
  assert.deepEqual(readdirSync(join(root, "contract/fixtures")).sort(), Object.keys(FIXTURES).sort());
  for (const [name, f] of Object.entries(FIXTURES)) {
    assert.deepEqual(JSON.parse(readFileSync(join(root, "contract/fixtures", name), "utf8")), f, name);
  }
});
