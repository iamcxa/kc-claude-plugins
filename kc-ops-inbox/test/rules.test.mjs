import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";
import { spawnSync } from "node:child_process";
import { rig, signedRequest, relayEvent, recoveredEvent, heartbeatEvent, sentryEvent, PREVIEW_SECRET, READBACK_SECRET, KEYS, CAPTAIN_USER } from "./rig.mjs";
import { DEFAULT_RULES, loadConfig, parseRules, routeFor } from "../core/inbox-config.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const secretFor = (environment) => (environment === "prod" ? undefined : PREVIEW_SECRET);
const send = (r, event, environment = "prod") => r.call(signedRequest(event, { secret: secretFor(environment) }));
const agentLine = (n) => (n.blocks ? n.blocks[1].text.text : n.attachments[0].blocks[1].text.text);

// The approved routing table (archived task ops-metric-event-protocol, "Routing (inbox side)").
const TABLE = {
  prod: { info: "record", warning: "agent", critical: "captain" },
  preview: { info: "record", warning: "record", critical: "agent" },
  dev: { info: "record", warning: "record", critical: "record" },
};

for (const [environment, row] of Object.entries(TABLE)) {
  for (const [severity, receiver] of Object.entries(row)) {
    test(`default rules: ${environment} x ${severity} is ${receiver}`, async () => {
      const r = await rig();
      const event = relayEvent(80, { environment, severity });
      const res = await send(r, event, environment);
      const body = await res.json();
      assert.equal(routeFor(event, DEFAULT_RULES).receiver, receiver);
      if (receiver === "record") {
        assert.deepEqual([res.status, body.status], [200, "recorded"]);
        assert.equal(r.state.dispatches.length + r.state.mints.length + r.state.slack.length, 0);
        const kept = [...r.store.m.values()].map((v) => JSON.parse(v)).find((v) => v.id === event.id);
        assert.equal(kept.route, "record");
        assert.equal(kept.event, JSON.stringify(event));
        assert.ok(![...r.store.m.keys()].some((k) => k.startsWith("incident.")));
      } else {
        assert.equal(res.status, 202);
        assert.equal(r.state.dispatches.length, 1);
        assert.equal(agentLine(r.state.slack[0]).includes(`<@${CAPTAIN_USER}>`), receiver === "captain");
      }
      r.close();
    });
  }
}

test("a resent recorded event is a duplicate, and a recorded event on an open incident writes nothing to its task", async () => {
  const r = await rig();
  await send(r, relayEvent(80));
  const before = r.state.dispatches.length;
  const info = relayEvent(100, { severity: "info" });
  assert.equal((await (await send(r, info)).json()).status, "recorded");
  assert.equal((await (await send(r, info)).json()).status, "duplicate");
  assert.equal(r.state.dispatches.length, before);
  assert.equal(r.state.slack.length, 1);
  r.close();
});

test("a recovered event joins its open incident whatever its severity, and is recorded when none is open", async () => {
  const r = await rig();
  const lone = await (await send(r, recoveredEvent(80))).json();
  assert.equal(lone.status, "recorded");
  assert.equal(r.state.dispatches.length, 0);
  await send(r, relayEvent(80));
  const joined = await send(r, recoveredEvent(100, { severity: "info" }));
  assert.equal(joined.status, 202);
  assert.deepEqual(r.state.dispatches.map((d) => d.inputs.mode), ["open", "join"]);
  assert.equal(r.state.dispatches[1].inputs.branch, r.state.dispatches[0].inputs.branch);
  assert.match(agentLine(r.state.slack[1]), /Joins incident/);
  r.close();
});

test("a heartbeat opens and joins nothing, even under a rule that routes everything to the agent", async () => {
  const r = await rig();
  r.env.OPS_RULES = JSON.stringify([{ name: "all", match: {}, receiver: "agent" }]);
  await send(r, relayEvent(80));
  const res = await send(r, heartbeatEvent());
  assert.equal((await res.json()).status, "recorded");
  assert.equal(r.state.dispatches.length, 1);
  assert.equal(routeFor(heartbeatEvent(), parseRules(r.env.OPS_RULES)).receiver, "record");
  r.close();
});

test("rules: first match wins, a field lists alternatives, fields combine, and a missing attribute never matches a condition", async () => {
  const rules = parseRules(JSON.stringify([
    { name: "relay-warn", match: { source: ["urn:relay:"], severity: ["warning", "critical"] }, receiver: "captain" },
    { name: "crossed-any", match: { type: ["ops.metric.crossed"] }, receiver: "record" },
    { name: "sentry-prod", match: { environment: ["prod"] }, receiver: "record" },
    { name: "rest", match: {}, receiver: "agent" },
  ]));
  const route = (e) => routeFor(e, rules).rule;
  assert.equal(route(relayEvent(80)), "relay-warn");
  assert.equal(route(relayEvent(80, { severity: "info" })), "crossed-any");
  assert.equal(route(heartbeatEvent()), "heartbeat");
  assert.equal(route(sentryEvent("s1", "x")), "rest");
  assert.equal(route({ ...sentryEvent("s1", "x"), environment: "prod" }), "sentry-prod");
});

test("the default list has the five rules and ends in a catch-all", () => {
  assert.equal(DEFAULT_RULES.length, 5);
  assert.deepEqual(DEFAULT_RULES.at(-1).match, {});
  assert.equal(routeFor(sentryEvent("s1", "x"), DEFAULT_RULES).receiver, "agent");
});

const INVALID_RULES = {
  "not JSON": "[",
  "an object": "{}",
  "an empty list": "[]",
  "an unknown rule field": JSON.stringify([{ name: "a", match: {}, receiver: "agent", extra: 1 }]),
  "an unknown receiver": JSON.stringify([{ name: "a", match: {}, receiver: "slack" }]),
  "an unknown match field": JSON.stringify([{ name: "a", match: { subject: ["x"] }, receiver: "agent" }]),
  "an environment outside the contract": JSON.stringify([{ name: "a", match: { environment: ["staging"] }, receiver: "agent" }]),
  "an empty value list": JSON.stringify([{ name: "a", match: { severity: [] }, receiver: "agent" }]),
  "a source prefix without a trailing colon": JSON.stringify([{ name: "a", match: { source: ["urn:relay"] }, receiver: "agent" }]),
  "an unknown type": JSON.stringify([{ name: "a", match: { type: ["relay.capacity.ceiling"] }, receiver: "agent" }]),
  "a repeated name": JSON.stringify([{ name: "a", match: { severity: ["info"] }, receiver: "record" }, { name: "a", match: {}, receiver: "agent" }]),
  "a malformed name": JSON.stringify([{ name: "Bad Name", match: {}, receiver: "agent" }]),
  "a last rule that does not match everything": JSON.stringify([{ name: "a", match: { severity: ["info"] }, receiver: "record" }]),
};

for (const [label, text] of Object.entries(INVALID_RULES)) {
  test(`an invalid rule list (${label}) fails closed: 500, nothing claimed, health names the fault`, async () => {
    const r = await rig();
    r.env.OPS_RULES = text;
    assert.throws(() => loadConfig(r.env), /OPS_RULES/);
    const res = await send(r, relayEvent(80));
    assert.deepEqual([res.status, (await res.json()).error], [500, "inbox-misconfigured"]);
    assert.equal(r.state.dispatches.length + r.state.mints.length + r.state.slack.length + r.store.m.size, 0);
    assert.ok(r.logs.some((l) => l.evt === "misconfigured"));
    const health = await (await r.call({ method: "GET" }, "http://inbox.test/inbox/health")).json();
    assert.equal(health.config.ok, false);
    assert.match(health.config.rules.error, /OPS_RULES/);
    r.close();
  });
}

test("a rule that routes to the captain needs the captain's Slack user, and a list without one does not", async () => {
  const r = await rig();
  delete r.env.OPS_CAPTAIN_SLACK_USER;
  assert.throws(() => loadConfig(r.env), /OPS_CAPTAIN_SLACK_USER/);
  assert.equal((await send(r, relayEvent(80))).status, 500);
  r.env.OPS_RULES = JSON.stringify([{ name: "all", match: {}, receiver: "agent" }]);
  assert.equal((await send(r, relayEvent(80))).status, 202);
  r.env.OPS_CAPTAIN_SLACK_USER = "not a user id";
  r.env.OPS_RULES = "";
  assert.throws(() => loadConfig(r.env), /OPS_CAPTAIN_SLACK_USER/);
  r.close();
});

test("the captain route mentions him on the opening notice, and on the NOT started and UNCERTAIN notices", async () => {
  const mention = `<@${CAPTAIN_USER}>`;
  const critical = () => relayEvent(100, { severity: "critical" });
  const refused = await rig({ dispatchStatus: 403 });
  await send(refused, critical());
  assert.ok(agentLine(refused.state.slack[0]).startsWith(mention));
  assert.match(agentLine(refused.state.slack[0]), /GitHub refused the dispatch/);
  const unsure = await rig({ hangDispatch: true, timeoutMs: 200 });
  assert.equal((await send(unsure, critical())).status, 504);
  assert.ok(agentLine(unsure.state.slack[0]).startsWith(mention));
  assert.match(agentLine(unsure.state.slack[0]), /UNCERTAIN/);
  const agent = await rig({ dispatchStatus: 403 });
  await send(agent, relayEvent(80));
  assert.ok(!agentLine(agent.state.slack[0]).includes(mention));
  refused.close(); unsure.close(); agent.close();
});

test("keys: each signs only the environments and source prefixes it lists (D5)", async () => {
  const r = await rig();
  const prodByPreviewKey = await r.call(signedRequest(relayEvent(80), { secret: PREVIEW_SECRET }));
  const previewByProdKey = await r.call(signedRequest(relayEvent(80, { environment: "preview" })));
  const relayByReadbackKey = await r.call(signedRequest(relayEvent(80), { secret: READBACK_SECRET }));
  assert.equal(prodByPreviewKey.status, 401);
  assert.equal((await prodByPreviewKey.json()).error, "key-not-allowed");
  assert.equal((await previewByProdKey.json()).error, "key-not-allowed");
  assert.equal((await relayByReadbackKey.json()).error, "key-not-allowed");
  assert.equal(r.state.dispatches.length + r.state.mints.length + r.state.slack.length + r.store.m.size, 0);
  assert.equal((await send(r, relayEvent(80, { environment: "preview", severity: "critical" }), "preview")).status, 202);
  r.close();
});

const withKeys = (mutate) => (env) => { const keys = JSON.parse(JSON.stringify(KEYS)); mutate(keys, env); env.OPS_KEYS = JSON.stringify(keys); };
const INVALID_KEYS = {
  "no list": (env) => { delete env.OPS_KEYS; },
  "not JSON": (env) => { env.OPS_KEYS = "{"; },
  "an empty list": (env) => { env.OPS_KEYS = "[]"; },
  "a repeated name": withKeys((k) => { k[1].name = "prod"; }),
  "a shared secret variable": withKeys((k) => { k[1].secretEnv = "KEY_PROD"; }),
  "a reserved secret variable": withKeys((k) => { k[1].secretEnv = "DISPATCH_APP_PRIVATE_KEY"; }),
  "an unset secret": (env) => { delete env.KEY_PREVIEW; },
  "a short secret": (env) => { env.KEY_PREVIEW = "whsec_a"; },
  "no environments": withKeys((k) => { k[0].environments = []; }),
  "an environment outside the contract": withKeys((k) => { k[0].environments = ["staging"]; }),
  "a source prefix without a trailing colon": withKeys((k) => { k[0].sources = ["urn:relay"]; }),
  "an unknown key field": withKeys((k) => { k[0].secret = "whsec_x"; }),
};

for (const [label, apply] of Object.entries(INVALID_KEYS)) {
  test(`an invalid key list (${label}) fails closed: 500, nothing claimed, health names the fault`, async () => {
    const r = await rig();
    apply(r.env);
    assert.throws(() => loadConfig(r.env), /OPS_KEYS/);
    const res = await send(r, relayEvent(80));
    assert.deepEqual([res.status, (await res.json()).error], [500, "inbox-misconfigured"]);
    assert.equal(r.state.dispatches.length + r.state.mints.length + r.state.slack.length + r.store.m.size, 0);
    const health = await (await r.call({ method: "GET" }, "http://inbox.test/inbox/health")).json();
    assert.match(health.config.keys.error, /OPS_KEYS/);
    assert.ok(!JSON.stringify(health).includes(r.env.KEY_PROD));
    r.close();
  });
}

const closure = (dir) => spawnSync("node", [join(root, "bin/import-closure.mjs"), dir], { encoding: "utf8" });

test("the core's import closure leaves the package only through node:crypto", () => {
  const r = closure(root);
  assert.deepEqual([r.status, r.stdout], [0, "node:crypto\n"]);
});

test("the closure walk follows relative imports and reports every external one", () => {
  const dir = mkdtempSync(join(tmpdir(), "ops-closure-"));
  try {
    mkdirSync(join(dir, "core"));
    mkdirSync(join(dir, "lib"));
    writeFileSync(join(dir, "core/a.mjs"), 'import { createHash } from "node:crypto";\nimport { x } from "../lib/b.mjs";\n');
    writeFileSync(join(dir, "lib/b.mjs"), 'import { readFileSync } from "node:fs";\nexport { y } from "yaml";\nexport const x = () => import("left-pad");\n');
    const r = closure(dir);
    assert.equal(r.status, 1);
    assert.deepEqual(r.stdout.trim().split("\n"), ["dynamic:\"left-pad\"", "node:crypto", "node:fs", "yaml"]);
    writeFileSync(join(dir, "lib/b.mjs"), 'import { readFileSync } from "node:fs";\nexport const x = 1;\n');
    const fsOnly = closure(dir);
    assert.deepEqual([fsOnly.status, fsOnly.stdout], [1, "node:crypto\nnode:fs\n"]);
    writeFileSync(join(dir, "lib/b.mjs"), "export const x = 1;\n");
    assert.deepEqual([closure(dir).status, closure(dir).stdout], [0, "node:crypto\n"]);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
