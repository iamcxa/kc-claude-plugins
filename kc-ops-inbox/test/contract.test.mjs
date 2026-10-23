import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync, readdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";
import { parseEvent, jsonSchemaFor, TYPES, signBody, SCHEMA_BASE } from "../core/inbox-core.mjs";
import { FIXTURES, FIXTURE_SECRET } from "../contract/generate.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const validate = (name, extra = []) =>
  spawnSync("node", [join(root, "contract/validate.mjs"), join(root, "contract/fixtures", name), ...extra], { encoding: "utf8" });

test("valid fixtures print the type and both keys, exit 0", () => {
  for (const name of ["relay-ceiling-near.json", "relay-ceiling-full.json", "sentry-issue.json"]) {
    const r = validate(name);
    assert.equal(r.status, 0, name);
    assert.match(r.stdout, /^valid (relay\.capacity\.ceiling|sentry\.issue\.alert) [0-9a-f]{64} [0-9a-f]{64}\n$/);
  }
});

test("each invalid fixture is refused with its own reason, exit 1", () => {
  const want = {
    "missing-source.json": "missing-attribute: source",
    "missing-subject.json": "missing-attribute: subject",
    "bad-signature.json": "signature-mismatch",
    "extra-field.json": "field-not-allowed: data.user",
  };
  for (const [name, reason] of Object.entries(want)) {
    const r = validate(name);
    assert.equal(r.status, 1, name);
    assert.equal(r.stdout.trim(), reason, name);
  }
});

test("validator exits 2 on a usage error", () => {
  assert.equal(spawnSync("node", [join(root, "contract/validate.mjs")], { encoding: "utf8" }).status, 2);
  assert.equal(validate("relay-ceiling-near.json", ["--now", "abc"]).status, 2);
});

test("a fixture checked an hour later is refused as stale", () => {
  const r = validate("relay-ceiling-near.json", ["--now", String(FIXTURES["relay-ceiling-near.json"].now + 3600)]);
  assert.equal(r.status, 1);
  assert.equal(r.stdout.trim(), "timestamp-out-of-tolerance");
});

test("the near and full events share an incident key and differ in dedupe key", () => {
  const keys = (n) => validate(n).stdout.trim().split(" ").slice(2);
  const [nearDedupe, nearIncident] = keys("relay-ceiling-near.json");
  const [fullDedupe, fullIncident] = keys("relay-ceiling-full.json");
  assert.equal(nearIncident, fullIncident);
  assert.notEqual(nearDedupe, fullDedupe);
});

function signed(event, nowS = 1_800_000_000) {
  const body = JSON.stringify(event);
  const id = "msg_t";
  const headers = new Headers({ "webhook-id": id, "webhook-timestamp": String(nowS), "webhook-signature": signBody({ secret: FIXTURE_SECRET, id, timestamp: String(nowS), body }) });
  return { secret: FIXTURE_SECRET, headers, body, nowS };
}
const base = () => JSON.parse(FIXTURES["relay-ceiling-near.json"].body);

test("contract rules beyond the fixtures", () => {
  const cases = [
    ["unknown type", { ...base(), type: "other.thing" }, "unknown-type: other.thing"],
    ["dataschema of another version", { ...base(), dataschema: `${SCHEMA_BASE.replace("/v1", "/v2")}/relay.capacity.ceiling.json` }, "invalid-value: dataschema"],
    ["unknown envelope attribute", { ...base(), extension: "x" }, "field-not-allowed: extension"],
    ["subject shape", { ...base(), subject: "ceiling/signed-in" }, "invalid-value: subject"],
    ["subject day differs from data day", { ...base(), subject: "ceiling/signed-in/2026-10-21" }, "subject-mismatch"],
    ["count not an integer", { ...base(), data: { ...base().data, count: "40" } }, "invalid-value: data.count"],
    ["required data field missing", { ...base(), data: { ...base().data, count: undefined } }, "missing-attribute: data.count"],
    ["bad time", { ...base(), time: "yesterday" }, "invalid-value: time"],
  ];
  for (const [label, ev, reason] of cases) {
    const r = parseEvent(signed(ev));
    assert.equal(r.ok, false, label);
    assert.equal(r.status, 400, label);
    assert.equal(r.reason, reason, label);
  }
  assert.equal(parseEvent(signed(base())).ok, true);
});

test("a body over 16 KiB is refused before it is trusted", () => {
  const r = parseEvent(signed({ ...base(), padding: "x".repeat(20000) }));
  assert.deepEqual([r.status, r.reason], [413, "body-too-large"]);
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
  for (const [name, f] of Object.entries(FIXTURES)) {
    assert.deepEqual(JSON.parse(readFileSync(join(root, "contract/fixtures", name), "utf8")), f, name);
  }
});
