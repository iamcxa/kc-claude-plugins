import { createHmac, createHash, createSign, timingSafeEqual } from "node:crypto";

// ---- Contract v1 -----------------------------------------------------------

export const CONTRACT_VERSION = "v1";
export const TOLERANCE_S = 300;
export const MAX_BODY_BYTES = 16384;
export const SCHEMA_BASE = "https://github.com/iamcxa/kc-claude-plugins/blob/main/kc-ops-inbox/contract/v1";

const ID_RE = /^[A-Za-z0-9._-]{1,64}$/;
const SUBJECT_RE = /^[A-Za-z0-9._/-]{1,100}$/;
const TIME_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/;
const DAY_RE = /^\d{4}-\d{2}-\d{2}$/;
const MAX_STRING = 500;

const REQUIRED_ATTRS = ["specversion", "id", "source", "type", "subject", "time", "dataschema"];
const ALLOWED_ATTRS = new Set([...REQUIRED_ATTRS, "datacontenttype", "data"]);

const str = { kind: "string" };
const int = { kind: "integer" };

// One entry per event type: the data allowlist, which fields are required, and the subject rule.
export const TYPES = {
  "relay.capacity.ceiling": {
    title: "Relay capacity ceiling crossed",
    subjectPattern: "^ceiling/[a-z][a-z-]*/\\d{4}-\\d{2}-\\d{2}$",
    fields: {
      v: { ...int, minimum: 1 },
      event: str,
      at: { ...str, format: "date-time" },
      day: { ...str, pattern: DAY_RE.source },
      count: { ...int, minimum: 0 },
      limit: { ...int, minimum: 0 },
      limitSource: str,
    },
    required: ["v", "event", "at", "day", "count", "limit", "limitSource"],
    // the subject ends in the data's day, so one incident cannot span days
    subjectAgrees: (subject, data) => subject.endsWith(`/${data.day}`),
    describe: (ev) => {
      const tier = ev.subject.split("/")[1];
      const level = /full$/.test(ev.data.event) ? "full" : /near$/.test(ev.data.event) ? "near" : ev.data.event;
      return { head: `relay · ${tier} ceiling ${level}`, body: `${ev.data.count} of ${ev.data.limit} ${tier} publishes today (limit source: ${ev.data.limitSource})` };
    },
  },
  "sentry.issue.alert": {
    title: "Sentry issue alert",
    subjectPattern: "^issue/[A-Za-z0-9._-]{1,64}$",
    fields: {
      issue_id: str,
      event_id: str,
      title: str,
      level: str,
      culprit: str,
      project: str,
      web_url: { ...str, pattern: "^https://" },
      triggered_rule: str,
      datetime: { ...str, format: "date-time" },
      release: str,
    },
    required: ["issue_id", "title", "level", "project", "web_url"],
    subjectAgrees: (subject, data) => subject === `issue/${data.issue_id}`,
    describe: (ev) => {
      const text = [ev.data.title, ev.data.culprit].filter(Boolean).join(" · ");
      return { head: `sentry · ${ev.data.level}`, body: text.length > 200 ? `${text.slice(0, 200)}…` : text };
    },
  },
  "ops.inbox.selftest": {
    title: "Setup read-back self-test",
    subjectPattern: "^selftest/[A-Za-z0-9._-]{1,64}$",
    fields: { v: { ...int, minimum: 1 }, project: { ...str, pattern: "^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$" } },
    required: ["v", "project"],
    subjectAgrees: () => true,
    describe: (ev) => ({ head: `Read-back self-test · ${ev.data.project}`, body: "Signature verified; the dispatch App reaches only the trigger repository." }),
  },
};

export const sha256hex = (s) => createHash("sha256").update(s).digest("hex");
export const dedupeKey = (ev) => sha256hex(`${ev.source}\n${ev.id}`);
export const incidentKey = (ev) => sha256hex(`${ev.source}\n${ev.subject}`);

export function verifySignature({ secret, id, timestamp, signatureHeader, body, nowS }) {
  if (!id || !timestamp || !signatureHeader) return "missing-headers";
  const ts = Number(timestamp);
  if (!Number.isInteger(ts) || Math.abs(nowS - ts) > TOLERANCE_S) return "timestamp-out-of-tolerance";
  const key = Buffer.from(secret.replace(/^whsec_/, ""), "base64");
  const expected = createHmac("sha256", key).update(`${id}.${timestamp}.${body}`).digest();
  for (const part of signatureHeader.split(" ")) {
    const [version, sig] = part.split(",");
    if (version !== "v1" || !sig) continue;
    const got = Buffer.from(sig, "base64");
    if (got.length === expected.length && timingSafeEqual(got, expected)) return null;
  }
  return "signature-mismatch";
}

export function signBody({ secret, id, timestamp, body }) {
  const key = Buffer.from(secret.replace(/^whsec_/, ""), "base64");
  return `v1,${createHmac("sha256", key).update(`${id}.${timestamp}.${body}`).digest("base64")}`;
}

function checkValue(spec, value, path) {
  if (spec.kind === "string") {
    if (typeof value !== "string" || value.length > MAX_STRING) return `invalid-value: ${path}`;
    if (spec.pattern && !new RegExp(spec.pattern).test(value)) return `invalid-value: ${path}`;
    if (spec.format === "date-time" && !(TIME_RE.test(value) && !Number.isNaN(Date.parse(value)))) return `invalid-value: ${path}`;
    return null;
  }
  if (!Number.isInteger(value) || value < (spec.minimum ?? -Infinity)) return `invalid-value: ${path}`;
  return null;
}

// Returns { ok: true, event, keys } or { ok: false, status, reason }.
// 413/401 are decided before the body is trusted; 400 means the signed body is not contract v1.
export function parseEvent({ secret, headers, body, nowS }) {
  if (Buffer.byteLength(body) > MAX_BODY_BYTES) return { ok: false, status: 413, reason: "body-too-large" };
  const bad = verifySignature({
    secret,
    id: headers.get("webhook-id"),
    timestamp: headers.get("webhook-timestamp"),
    signatureHeader: headers.get("webhook-signature"),
    body,
    nowS,
  });
  if (bad) return { ok: false, status: 401, reason: bad };
  return validateBody(body);
}

// The contract rules without the signature, for a receiver that got the body from the inbox.
export function validateBody(body) {
  const refuse = (reason) => ({ ok: false, status: 400, reason });

  let ev;
  try { ev = JSON.parse(body); } catch { return refuse("not-json"); }
  if (ev === null || typeof ev !== "object" || Array.isArray(ev)) return refuse("not-json-object");
  for (const name of REQUIRED_ATTRS) if (!(name in ev)) return refuse(`missing-attribute: ${name}`);
  for (const name of Object.keys(ev)) if (!ALLOWED_ATTRS.has(name)) return refuse(`field-not-allowed: ${name}`);

  if (ev.specversion !== "1.0") return refuse("invalid-value: specversion");
  if (typeof ev.id !== "string" || !ID_RE.test(ev.id)) return refuse("invalid-value: id");
  if (typeof ev.source !== "string" || ev.source.length === 0 || ev.source.length > 200) return refuse("invalid-value: source");
  if (typeof ev.type !== "string" || !Object.hasOwn(TYPES, ev.type)) return refuse(`unknown-type: ${ev.type}`);
  if (typeof ev.subject !== "string" || !SUBJECT_RE.test(ev.subject)) return refuse("invalid-value: subject");
  if (typeof ev.time !== "string" || !TIME_RE.test(ev.time) || Number.isNaN(Date.parse(ev.time))) return refuse("invalid-value: time");
  if (ev.dataschema !== `${SCHEMA_BASE}/${ev.type}.json`) return refuse("invalid-value: dataschema");
  if ("datacontenttype" in ev && ev.datacontenttype !== "application/json") return refuse("invalid-value: datacontenttype");

  const spec = TYPES[ev.type];
  if (!new RegExp(spec.subjectPattern).test(ev.subject)) return refuse("invalid-value: subject");
  const data = ev.data;
  if (data === null || typeof data !== "object" || Array.isArray(data)) return refuse("missing-attribute: data");
  for (const name of spec.required) if (!(name in data)) return refuse(`missing-attribute: data.${name}`);
  for (const name of Object.keys(data)) if (!Object.hasOwn(spec.fields, name)) return refuse(`field-not-allowed: data.${name}`);
  for (const [name, value] of Object.entries(data)) {
    const err = checkValue(spec.fields[name], value, `data.${name}`);
    if (err) return refuse(err);
  }
  if (!spec.subjectAgrees(ev.subject, data)) return refuse("subject-mismatch");

  return { ok: true, event: ev, keys: { dedupe: dedupeKey(ev), incident: incidentKey(ev) } };
}

// The published JSON Schema of one type, derived from TYPES so the code and the file cannot differ.
export function jsonSchemaFor(type) {
  const spec = TYPES[type];
  const properties = {};
  for (const [name, f] of Object.entries(spec.fields)) {
    properties[name] = {
      type: f.kind,
      ...(f.format && { format: f.format }),
      ...(f.pattern && { pattern: f.pattern }),
      ...(f.minimum !== undefined && { minimum: f.minimum }),
      ...(f.kind === "string" && { maxLength: MAX_STRING }),
    };
  }
  return {
    $schema: "https://json-schema.org/draft/2020-12/schema",
    $id: `${SCHEMA_BASE}/${type}.json`,
    title: spec.title,
    type: "object",
    required: REQUIRED_ATTRS.concat("data"),
    additionalProperties: false,
    properties: {
      specversion: { const: "1.0" },
      id: { type: "string", pattern: ID_RE.source },
      source: { type: "string", minLength: 1, maxLength: 200 },
      type: { const: type },
      subject: { type: "string", pattern: spec.subjectPattern },
      time: { type: "string", format: "date-time" },
      dataschema: { const: `${SCHEMA_BASE}/${type}.json` },
      datacontenttype: { const: "application/json" },
      data: { type: "object", required: spec.required, additionalProperties: false, properties },
    },
  };
}

// ---- Notices ---------------------------------------------------------------

const slackEscape = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const runLink = (url, label) => `<${url}|${label}>`;

export function incidentBranch(ev, incident) {
  const safe = ev.subject.replace(/[^A-Za-z0-9._-]/g, "-").replace(/-+/g, "-").replace(/^[-.]+|[-.]+$/g, "").toLowerCase();
  return `${safe.slice(0, 80)}-${incident.slice(0, 8)}`;
}

// kind: opened | joined | refused | uncertain | selftest
export function buildNotice(kind, { ev, branch, runUrl, number, status, triggerRepo }) {
  const { head, body } = TYPES[ev.type].describe(ev);
  const agent = {
    opened: `:white_check_mark: New incident \`${slackEscape(ev.subject)}\` · agent started · ${runLink(runUrl, "run for this incident")}; its Draft PR links from the run`,
    joined: `:link: Joins incident \`${slackEscape(ev.subject)}\` (event ${number}) · recorded on its ops task, no new agent run · ${runLink(runUrl, "run that opened it")}`,
    refused: `:x: Needs action · GitHub refused the dispatch (HTTP ${status}), so no agent runs for this event. Run the setup read-back. If the sender retries, the retry posts its own notice.`,
    uncertain: `:question: Needs a look · agent start UNCERTAIN: GitHub did not answer in time, and the inbox will not resend this event. ${runLink(`https://github.com/${triggerRepo}/actions`, "open the trigger repository's runs")}`,
    selftest: `:test_tube: ${runLink(runUrl, "Self-test run")} started; no task is filed. Captain: paste this message's link into the read-back.`,
  }[kind];
  const blocks = [
    { type: "section", text: { type: "mrkdwn", text: `*${slackEscape(head)}*\n${slackEscape(body)}` } },
    { type: "section", text: { type: "mrkdwn", text: agent } },
    { type: "context", elements: [{ type: "mrkdwn", text: slackEscape(`event ${ev.id} · source ${ev.source} · contract ${CONTRACT_VERSION}`) }] },
  ];
  const text = `${slackEscape(head)}: ${slackEscape(body)}`;
  const color = { refused: "#d00000", uncertain: "#e8890c" }[kind];
  return color ? { text, attachments: [{ color, blocks }] } : { text, blocks };
}

// ---- GitHub ----------------------------------------------------------------

const b64u = (b) => Buffer.from(b).toString("base64url");

export function appJwt({ appId, privateKeyPem, nowS }) {
  const head = b64u(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claims = b64u(JSON.stringify({ iat: nowS - 60, exp: nowS + 540, iss: appId }));
  return `${head}.${claims}.${b64u(createSign("RSA-SHA256").update(`${head}.${claims}`).sign(privateKeyPem))}`;
}

const SETTINGS = ["OPS_TRIGGER_REPO", "OPS_WORKFLOW", "DISPATCH_APP_ID", "DISPATCH_INSTALLATION_ID"];
const SECRETS = ["WEBHOOK_SECRET", "DISPATCH_APP_PRIVATE_KEY", "SLACK_WEBHOOK_URL"];

export function health(env) {
  const present = (names) => ({ present: names.filter((n) => env[n]).length, total: names.length, missing: names.filter((n) => !env[n]) });
  return { contract: CONTRACT_VERSION, settings: present(SETTINGS), secrets: present(SECRETS) };
}

const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

// ---- Handler ---------------------------------------------------------------
// Platform-neutral: a Web Request in, a Web Response out.
// store: { set(key, value, { onlyIfNew }) -> { modified }, get(key) -> string | null, delete(key) }

export async function handle(req, deps) {
  const { store, fetchImpl, env, now = Date.now, log = console.log, timeoutMs = 10000 } = deps;
  const t = { arrival: now() };
  const api = (path, token, init = {}) =>
    fetchImpl(`${env.OPS_GITHUB_API_URL || "https://api.github.com"}${path}`, {
      ...init,
      signal: AbortSignal.timeout(timeoutMs),
      headers: {
        authorization: `Bearer ${token}`,
        accept: "application/vnd.github+json",
        "x-github-api-version": "2022-11-28",
        "content-type": "application/json",
        "user-agent": "kc-ops-inbox",
      },
    });
  const post = async (notice) => {
    if (!env.SLACK_WEBHOOK_URL) return null;
    try {
      const res = await fetchImpl(env.SLACK_WEBHOOK_URL, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(notice), signal: AbortSignal.timeout(5000) });
      return res.status;
    } catch (err) {
      log(JSON.stringify({ evt: "slack-failed", error: String(err.message) }));
      return null;
    }
  };

  if (req.method === "GET" && new URL(req.url).pathname.endsWith("/health")) return json(200, health(env));
  if (req.method !== "POST") return json(405, { error: "method" });

  const body = await req.text();
  const parsed = parseEvent({ secret: env.WEBHOOK_SECRET, headers: req.headers, body, nowS: Math.floor(t.arrival / 1000) });
  if (!parsed.ok) {
    log(JSON.stringify({ evt: "rejected", reason: parsed.reason, status: parsed.status }));
    return json(parsed.status, { error: parsed.reason });
  }
  const { event: ev, keys } = parsed;
  const triggerRepo = env.OPS_TRIGGER_REPO;

  const eventClaim = `event.${keys.dedupe}`;
  const first = await store.set(eventClaim, JSON.stringify({ id: ev.id, source: ev.source, claimedAt: now() }), { onlyIfNew: true });
  if (!first.modified) {
    log(JSON.stringify({ evt: "duplicate", id: ev.id }));
    return json(200, { status: "duplicate", id: ev.id });
  }

  const selftest = ev.type === "ops.inbox.selftest";
  const branch = selftest ? null : incidentBranch(ev, keys.incident);
  const incidentClaim = `incident.${keys.incident}`;
  let mode = "selftest";
  let opening = null;
  let madeIncident = false;
  if (!selftest) {
    const made = await store.set(incidentClaim, JSON.stringify({ branch, firstEventId: ev.id, runId: null, runUrl: null }), { onlyIfNew: true });
    madeIncident = made.modified;
    mode = madeIncident ? "open" : "join";
    if (!madeIncident) opening = JSON.parse((await store.get(incidentClaim)) ?? "{}");
  }
  const release = async () => {
    await store.delete(eventClaim);
    if (madeIncident) await store.delete(incidentClaim);
  };

  let token;
  let mint;
  try {
    const jwt = appJwt({ appId: env.DISPATCH_APP_ID, privateKeyPem: env.DISPATCH_APP_PRIVATE_KEY, nowS: Math.floor(now() / 1000) });
    const res = await api(`/app/installations/${env.DISPATCH_INSTALLATION_ID}/access_tokens`, jwt, {
      method: "POST",
      body: JSON.stringify({ repositories: [triggerRepo.split("/")[1]], permissions: { actions: "write" } }),
    });
    if (res.status !== 201) throw Object.assign(new Error(`token-mint-${res.status}`), { status: res.status });
    mint = await res.json();
    token = mint.token;
  } catch (err) {
    await release();
    const status = err.status ?? 0;
    log(JSON.stringify({ evt: "dispatch-failed", id: ev.id, mode, stage: "mint", error: String(err.message), released: true }));
    await post(buildNotice("refused", { ev, status: status || "no answer", triggerRepo }));
    return json(502, { error: "dispatch-refused" });
  }

  let run;
  try {
    const res = await api(`/repos/${triggerRepo}/actions/workflows/${env.OPS_WORKFLOW}/dispatches`, token, {
      method: "POST",
      body: JSON.stringify({
        ref: env.OPS_REF || "main",
        inputs: { mode, branch: branch ?? "", incident: keys.incident, event: body, opening_run: String(opening?.runId ?? ""), received: new Date(t.arrival).toISOString() },
        return_run_details: true,
      }),
    });
    if (res.status !== 200 && res.status !== 204) throw Object.assign(new Error(`dispatch-${res.status}`), { status: res.status });
    run = res.status === 200 ? await res.json() : { workflow_run_id: null, html_url: `https://github.com/${triggerRepo}/actions` };
  } catch (err) {
    if (err.status) {
      await release();
      log(JSON.stringify({ evt: "dispatch-failed", id: ev.id, mode, stage: "dispatch", error: err.message, released: true }));
      await post(buildNotice("refused", { ev, status: err.status, triggerRepo }));
      return json(502, { error: "dispatch-refused" });
    }
    log(JSON.stringify({ evt: "dispatch-failed", id: ev.id, mode, stage: "dispatch", error: String(err.message), released: false }));
    await post(buildNotice("uncertain", { ev, triggerRepo }));
    return json(504, { error: "dispatch-ambiguous" });
  }

  const runId = run.workflow_run_id ?? null;
  const runUrl = run.html_url;
  let slack;
  const out = { status: "dispatched", mode, id: ev.id, run_id: runId, run_url: runUrl };

  if (selftest) {
    const project = ev.data.project;
    const projectMint = await api(`/app/installations/${env.DISPATCH_INSTALLATION_ID}/access_tokens`, appJwt({ appId: env.DISPATCH_APP_ID, privateKeyPem: env.DISPATCH_APP_PRIVATE_KEY, nowS: Math.floor(now() / 1000) }), {
      method: "POST",
      body: JSON.stringify({ repositories: [project.split("/")[1]], permissions: { actions: "write" } }),
    });
    const projectDispatch = await api(`/repos/${project}/actions/workflows/${env.OPS_PROJECT_WORKFLOW || "ci.yml"}/dispatches`, token, { method: "POST", body: JSON.stringify({ ref: "main" }) });
    const projectRerun = await api(`/repos/${project}/actions/runs/1/rerun`, token, { method: "POST" });
    slack = await post(buildNotice("selftest", { ev, runUrl, triggerRepo }));
    Object.assign(out, {
      status: "selftest",
      mint_trigger: { permissions: mint.permissions, repositories: (mint.repositories ?? []).map((r) => r.full_name ?? r.name) },
      mint_project: { status: projectMint.status },
      project_dispatch: { status: projectDispatch.status },
      project_rerun: { status: projectRerun.status },
      slack: { status: slack },
    });
    log(JSON.stringify({ evt: "selftest", id: ev.id, run_id: runId, mint_project: projectMint.status, project_dispatch: projectDispatch.status, project_rerun: projectRerun.status, slack }));
    return json(200, out);
  }

  if (madeIncident) {
    await store.set(incidentClaim, JSON.stringify({ ...opening, branch, firstEventId: ev.id, runId, runUrl }));
    slack = await post(buildNotice("opened", { ev, branch, runUrl }));
  } else {
    let number = 2;
    while (number < 100 && !(await store.set(`${incidentClaim}.event.${number}`, ev.id, { onlyIfNew: true })).modified) number += 1;
    slack = await post(buildNotice("joined", { ev, branch, runUrl: opening.runUrl ?? runUrl, number }));
    out.event_number = number;
  }
  log(JSON.stringify({ evt: "delivered", id: ev.id, mode, branch, run_id: runId, slack }));
  return json(202, out);
}
