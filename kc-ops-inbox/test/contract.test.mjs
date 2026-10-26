import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";
import { parseEvent, validateBody, jsonSchemaFor, TYPES, signBody, SCHEMA_BASE, ENVIRONMENTS } from "../contract/contract.mjs";
import { FIXTURES, FIXTURE_SECRET, PROD_KEY, PREVIEW_KEY } from "../contract/generate.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const validate = (name, extra = []) =>
  spawnSync("node", [join(root, "contract/validate.mjs"), join(root, "contract/fixtures", name), ...extra], { encoding: "utf8" });

test("valid fixtures print the type and both keys, exit 0", () => {
  const valid = ["relay-crossed", "relay-recovered", "relay-heartbeat", "qnow-crossed", "qnow-recovered", "qnow-heartbeat", "sentry-issue", "key-allowed"];
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
  };
  assert.deepEqual(Object.keys(want).concat(["relay-crossed", "relay-recovered", "relay-heartbeat", "qnow-crossed", "qnow-recovered", "qnow-heartbeat", "sentry-issue", "key-allowed"].map((n) => `${n}.json`)).sort(), Object.keys(FIXTURES).sort());
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
