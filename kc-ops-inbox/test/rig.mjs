import http from "node:http";
import { generateKeyPairSync, createVerify } from "node:crypto";
import { handle } from "../core/inbox-core.mjs";
import { signBody, SCHEMA_BASE } from "../contract/contract.mjs";
import { FIXTURE_SECRET, PREVIEW_KEY } from "../contract/generate.mjs";

export const SECRET = FIXTURE_SECRET;
export const PREVIEW_SECRET = PREVIEW_KEY.secret;
export const READBACK_SECRET = "whsec_" + Buffer.from("readback-key-for-tests-0123456789").toString("base64");
export const CAPTAIN_USER = "U0CAPTAIN1";
export const KEYS = [
  { name: "prod", secretEnv: "KEY_PROD", environments: ["prod"], sources: ["urn:relay:", "urn:sentry:"] },
  { name: "preview", secretEnv: "KEY_PREVIEW", environments: ["preview", "dev"], sources: ["urn:relay:"] },
  { name: "readback", secretEnv: "KEY_READBACK", environments: ["prod"], sources: ["urn:ops-inbox:"] },
];
export const TRIGGER = "o/trigger";
export const PROJECT = "o/project";

export function memoryStore(delayMs = 0) {
  const m = new Map();
  return {
    m,
    async set(k, v, { onlyIfNew } = {}) {
      if (delayMs) await new Promise((r) => setTimeout(r, delayMs));
      if (onlyIfNew && m.has(k)) return { modified: false };
      m.set(k, v);
      return { modified: true };
    },
    async get(k) { return m.has(k) ? m.get(k) : null; },
    async delete(k) { m.delete(k); },
  };
}

// A relay-shaped ops.metric.crossed event with its derived id (contract README, "Deterministic id").
// The value is the smallest count that reaches the level.
export function relayEvent(level, { metric = "capacity.signed-in", day = "2026-10-20", environment = "prod", severity = "warning", limit = 50 } = {}) {
  return {
    specversion: "1.0", id: `${metric}.${environment}.d${day}.c${level}.l${limit}`, source: "urn:relay:capacity", type: "ops.metric.crossed",
    subject: `metric/${environment}/${metric}/d${day}`, time: `${day}T00:00:00Z`, environment, severity,
    dataschema: `${SCHEMA_BASE}/ops.metric.crossed.json`, datacontenttype: "application/json",
    data: { metric, window: "day", period: day, value: (level * limit) / 100, limit, limitSource: "default", level },
  };
}

export function recoveredEvent(level, { metric = "capacity.signed-in", day = "2026-10-20", environment = "prod", severity = "warning", limit = 50, cause = "period-ended" } = {}) {
  return {
    ...relayEvent(level, { metric, day, environment, severity, limit }), type: "ops.metric.recovered",
    id: `${metric}.${environment}.d${day}.r${level}${cause === "below" ? "b" : "p"}.l${limit}`, dataschema: `${SCHEMA_BASE}/ops.metric.recovered.json`,
    data: { metric, window: "day", period: day, value: cause === "below" ? 0 : limit, limit, limitSource: "default", level, cause },
  };
}

export function heartbeatEvent({ metric = "capacity.signed-in", day = "2026-10-20", environment = "prod", limit = 50 } = {}) {
  return {
    specversion: "1.0", id: `${metric}.${environment}.hbd.${day}`, source: "urn:relay:capacity", type: "ops.metric.heartbeat",
    subject: `heartbeat/${environment}/${metric}/d`, time: `${day}T03:00:00Z`, environment, severity: "info",
    dataschema: `${SCHEMA_BASE}/ops.metric.heartbeat.json`, datacontenttype: "application/json",
    data: { metric, window: "day", period: day, value: 3, limit, limitSource: "default", every: "day" },
  };
}

export function sentryEvent(id, title) {
  return {
    specversion: "1.0", id, source: "urn:sentry:issue-alert", type: "sentry.issue.alert", subject: "issue/4242",
    time: "2026-10-20T00:00:00Z", dataschema: `${SCHEMA_BASE}/sentry.issue.alert.json`,
    data: { issue_id: "4242", title, level: "error", project: "demo", web_url: "https://sentry.example/issues/4242/" },
  };
}

export function selftestEvent(id, project = PROJECT) {
  return {
    specversion: "1.0", id, source: "urn:ops-inbox:readback", type: "ops.inbox.selftest", subject: `selftest/${id}`,
    time: new Date().toISOString(), dataschema: `${SCHEMA_BASE}/ops.inbox.selftest.json`, data: { v: 1, project },
  };
}

export function signedRequest(event, { secret = SECRET, timestamp = Math.floor(Date.now() / 1000), tamper = false } = {}) {
  let body = JSON.stringify(event);
  const id = `msg_${event.id}`;
  const signature = signBody({ secret, id, timestamp: String(timestamp), body });
  if (tamper) body = body.replace('"value":', '"value":1');
  return { method: "POST", headers: { "webhook-id": id, "webhook-timestamp": String(timestamp), "webhook-signature": signature }, body };
}

// A fake GitHub and Slack on one local port. `mode` flags make single calls fail.
export async function rig({ dispatchStatus = 200, slackStatus = 200, mintStatus = 201, hangDispatch = false, timeoutMs = 10000 } = {}) {
  const { privateKey, publicKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
  const state = { dispatches: [], mints: [], slack: [], refused: [], flags: { dispatchStatus, slackStatus, mintStatus, hangDispatch } };
  const server = http.createServer(async (req, res) => {
    let raw = "";
    for await (const c of req) raw += c;
    const auth = (req.headers.authorization || "").replace("Bearer ", "");
    const send = (s, b) => { res.writeHead(s, { "content-type": "application/json", connection: "close" }); res.end(JSON.stringify(b)); };
    if (req.url === "/slack") {
      state.slack.push(JSON.parse(raw));
      return send(state.flags.slackStatus, {});
    }
    if (req.url === "/app/installations/7/access_tokens") {
      const [h, c, s] = auth.split(".");
      if (!createVerify("RSA-SHA256").update(`${h}.${c}`).verify(publicKey, Buffer.from(s, "base64url"))) return send(401, {});
      const want = JSON.parse(raw);
      state.mints.push(want);
      if (want.repositories[0] === PROJECT.split("/")[1]) return send(422, { message: "repositories not installed" });
      if (state.flags.mintStatus !== 201) return send(state.flags.mintStatus, {});
      return send(201, { token: "ghs_fake", permissions: want.permissions, repositories: [{ full_name: TRIGGER }] });
    }
    if (req.url === `/repos/${TRIGGER}/actions/workflows/ops-event.yml/dispatches`) {
      if (auth !== "ghs_fake") return send(401, {});
      if (state.flags.hangDispatch) return;
      if (state.flags.dispatchStatus !== 200) return send(state.flags.dispatchStatus, { message: "no" });
      const b = JSON.parse(raw);
      state.dispatches.push(b);
      return send(200, { workflow_run_id: 1000 + state.dispatches.length, html_url: `https://example.test/run/${1000 + state.dispatches.length}` });
    }
    if (req.url.startsWith(`/repos/${PROJECT}/`)) { state.refused.push(req.url); return send(404, { message: "Not Found" }); }
    send(404, {});
  });
  await new Promise((r) => server.listen(0, r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const store = memoryStore(2);
  const env = {
    OPS_KEYS: JSON.stringify(KEYS), KEY_PROD: SECRET, KEY_PREVIEW: PREVIEW_SECRET, KEY_READBACK: READBACK_SECRET, OPS_CAPTAIN_SLACK_USER: CAPTAIN_USER,
    OPS_TRIGGER_REPO: TRIGGER, OPS_WORKFLOW: "ops-event.yml", OPS_REF: "main", OPS_GITHUB_API_URL: base,
    DISPATCH_APP_ID: "42", DISPATCH_INSTALLATION_ID: "7", DISPATCH_APP_PRIVATE_KEY: privateKey.export({ type: "pkcs8", format: "pem" }),
    SLACK_WEBHOOK_URL: `${base}/slack`,
  };
  const logs = [];
  const call = (init, url = "http://inbox.test/inbox") => handle(new Request(url, init), { store, fetchImpl: fetch, env, log: (l) => logs.push(JSON.parse(l)), timeoutMs });
  return { state, store, env, call, logs, close: () => { server.closeAllConnections?.(); server.close(); } };
}
