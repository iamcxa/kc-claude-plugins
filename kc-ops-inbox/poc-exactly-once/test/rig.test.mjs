import test from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { generateKeyPairSync, createVerify, randomBytes } from "node:crypto";
import { handle } from "../inbox-core.mjs";
import { signedRequest, fixtureEvent } from "../send.mjs";

const SECRET = "whsec_" + randomBytes(24).toString("base64");

function memoryStore(delayMs = 0) {
  const m = new Map();
  return {
    m,
    async set(k, v, { onlyIfNew } = {}) {
      if (delayMs) await new Promise((r) => setTimeout(r, delayMs));
      if (onlyIfNew && m.has(k)) return { modified: false };
      m.set(k, v);
      return { modified: true, etag: "e" };
    },
    async delete(k) { m.delete(k); },
  };
}

async function rig({ failDispatch = false, noRunDetails = false } = {}) {
  const { privateKey, publicKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
  const state = { dispatches: [], mints: [], slack: [], refused: [] };
  const server = http.createServer(async (req, res) => {
    let raw = "";
    for await (const c of req) raw += c;
    const auth = (req.headers.authorization || "").replace("Bearer ", "");
    const send = (s, b) => { res.writeHead(s, { "content-type": "application/json" }); res.end(JSON.stringify(b)); };
    if (req.url === "/slack") { state.slack.push(JSON.parse(raw)); return send(200, {}); }
    if (req.url === "/app/installations/7/access_tokens") {
      const [h, c, s] = auth.split(".");
      const ok = createVerify("RSA-SHA256").update(`${h}.${c}`).verify(publicKey, Buffer.from(s, "base64url"));
      if (!ok) return send(401, {});
      const want = JSON.parse(raw);
      state.mints.push(want);
      return send(201, { token: "ghs_fake", permissions: want.permissions });
    }
    if (req.url === "/repos/o/r/actions/workflows/w.yml/dispatches") {
      if (auth !== "ghs_fake") return send(401, {});
      const b = JSON.parse(raw);
      if (failDispatch) return send(500, {});
      if (noRunDetails) { state.dispatches.push(b); res.writeHead(204); return res.end(); }
      if (b.return_run_details !== true) return send(204, {});
      state.dispatches.push(b);
      return send(200, { workflow_run_id: 1000 + state.dispatches.length, run_url: "u", html_url: `https://example.test/run/${1000 + state.dispatches.length}` });
    }
    if (req.url.startsWith("/repos/o/r/git/refs")) { state.refused.push(req.url); return send(403, { message: "Resource not accessible by integration" }); }
    send(404, {});
  });
  await new Promise((r) => server.listen(0, r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const store = memoryStore(5);
  const env = {
    WEBHOOK_SECRET: SECRET, OPS_REPO: "o/r", OPS_WORKFLOW: "w.yml", OPS_REF: "master", OPS_GITHUB_API_URL: base,
    DISPATCH_APP_ID: "42", DISPATCH_INSTALLATION_ID: "7", DISPATCH_APP_PRIVATE_KEY: privateKey.export({ type: "pkcs8", format: "pem" }),
    SLACK_WEBHOOK_URL: `${base}/slack`,
  };
  const logs = [];
  const call = (init) => handle(new Request("http://inbox.test/inbox", init), { store, fetchImpl: fetch, env, log: (l) => logs.push(l) });
  return { state, store, call, logs, close: () => server.close() };
}

test("three sends of one webhook-id, third re-signed 61s later, start exactly one run", { timeout: 90000 }, async () => {
  const r = await rig();
  const body = fixtureEvent("evt-1");
  const nowS = Math.floor(Date.now() / 1000);
  const first = signedRequest({ secret: SECRET, webhookId: "msg_evt-1", body, timestamp: nowS });
  const statuses = [(await r.call(first)).status, (await r.call(first)).status];
  // a retry 61s later is a fresh signature over the same webhook-id and body
  const realNow = Date.now;
  let lateTs = nowS + 61;
  if (process.env.RIG_REAL_WAIT) {
    await new Promise((res) => setTimeout(res, 61500));
    lateTs = Math.floor(Date.now() / 1000);
  } else {
    Date.now = () => realNow() + 61000;
  }
  const late = signedRequest({ secret: SECRET, webhookId: "msg_evt-1", body, timestamp: lateTs });
  statuses.push((await r.call(late)).status);
  Date.now = realNow;
  assert.deepEqual(statuses, [202, 200, 200]);
  assert.equal(r.state.dispatches.length, 1);
  assert.equal(r.state.dispatches[0].inputs.event_id, "evt-1");
  assert.equal(r.state.dispatches[0].return_run_details, true);
  assert.equal(r.state.slack.length, 1);
  r.close();
});

test("concurrent identical sends dispatch once", async () => {
  const r = await rig();
  const req = signedRequest({ secret: SECRET, webhookId: "msg_evt-2", body: fixtureEvent("evt-2"), timestamp: Math.floor(Date.now() / 1000) });
  const out = await Promise.all([r.call(req), r.call(req), r.call(req)]);
  assert.equal(out.filter((x) => x.status === 202).length, 1);
  assert.equal(r.state.dispatches.length, 1);
  r.close();
});

test("one altered byte is rejected and starts nothing", async () => {
  const r = await rig();
  const body = fixtureEvent("evt-3");
  const req = signedRequest({ secret: SECRET, webhookId: "msg_evt-3", body, timestamp: Math.floor(Date.now() / 1000) });
  req.body = body.replace("raised", "raisee");
  const res = await r.call(req);
  assert.equal(res.status, 401);
  assert.equal(r.state.dispatches.length, 0);
  assert.equal(r.state.mints.length, 0);
  assert.equal(r.store.m.size, 0);
  r.close();
});

test("stale timestamp is rejected", async () => {
  const r = await rig();
  const req = signedRequest({ secret: SECRET, webhookId: "msg_evt-4", body: fixtureEvent("evt-4"), timestamp: Math.floor(Date.now() / 1000) - 3600 });
  assert.equal((await r.call(req)).status, 401);
  assert.equal(r.state.dispatches.length, 0);
  r.close();
});

test("branch-unsafe id is rejected before any claim", async () => {
  const r = await rig();
  const req = signedRequest({ secret: SECRET, webhookId: "msg_x", body: fixtureEvent("a/../b"), timestamp: Math.floor(Date.now() / 1000) });
  assert.equal((await r.call(req)).status, 400);
  assert.equal(r.store.m.size, 0);
  r.close();
});

test("the minted dispatch token asks for Actions: write on one repository only", async () => {
  const r = await rig();
  const req = signedRequest({ secret: SECRET, webhookId: "msg_evt-5", body: fixtureEvent("evt-5"), timestamp: Math.floor(Date.now() / 1000) });
  const res = await r.call(req);
  assert.deepEqual(r.state.mints, [{ repositories: ["r"], permissions: { actions: "write" } }]);
  assert.deepEqual((await res.json()).tokenPermissions, { actions: "write" });
  r.close();
});

test("a failed dispatch releases the claim so the sender's retry can start the run", async () => {
  const bad = await rig({ failDispatch: true });
  const req = signedRequest({ secret: SECRET, webhookId: "msg_evt-6", body: fixtureEvent("evt-6"), timestamp: Math.floor(Date.now() / 1000) });
  assert.equal((await bad.call(req)).status, 502);
  assert.equal(bad.store.m.size, 0);
  bad.close();
});

test("a 204 dispatch reply keeps the claim, since the run did start", async () => {
  const r = await rig({ noRunDetails: true });
  const req = signedRequest({ secret: SECRET, webhookId: "msg_evt-7", body: fixtureEvent("evt-7"), timestamp: Math.floor(Date.now() / 1000) });
  assert.equal((await r.call(req)).status, 202);
  assert.equal((await r.call(req)).status, 200);
  assert.equal(r.state.dispatches.length, 1);
  r.close();
});
