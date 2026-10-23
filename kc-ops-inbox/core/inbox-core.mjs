import { createHmac, createHash, timingSafeEqual } from "node:crypto";

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
