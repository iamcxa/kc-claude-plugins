import { createHmac, createHash, timingSafeEqual } from "node:crypto";

export const CONTRACT_VERSION = "v1";
export const TOLERANCE_S = 300;
export const MAX_BODY_BYTES = 16384;
export const SCHEMA_BASE = "https://github.com/iamcxa/kc-claude-plugins/blob/main/kc-ops-inbox/contract/v1";

export const ENVIRONMENTS = ["prod", "preview", "dev"];
export const SEVERITIES = ["info", "warning", "critical"];

const ID_RE = /^[A-Za-z0-9._-]{1,64}$/;
const SUBJECT_RE = /^[A-Za-z0-9._/-]{1,100}$/;
const SOURCE_RE = /^urn:[a-z0-9-]{1,32}(:[a-z0-9-]{1,32}){1,3}$/;
const TIME_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/;
const DAY_RE = /^\d{4}-\d{2}-\d{2}$/;
const METRIC_RE = /^[a-z][a-z0-9.-]{0,28}$/;
const MAX_STRING = 500;

const REQUIRED_ATTRS = ["specversion", "id", "source", "type", "subject", "time", "dataschema"];
const ALLOWED_ATTRS = new Set([...REQUIRED_ATTRS, "datacontenttype", "data", "environment", "severity"]);

const str = { kind: "string" };
const int = { kind: "integer" };
const enumOf = (...values) => ({ kind: typeof values[0] === "number" ? "integer" : "string", enum: values });

const windowCode = (data) => (data.window === "day" ? "d" : "m");

// Fields shared by the three metric types; the per-type fields are added below.
const metricFields = {
  metric: { ...str, pattern: METRIC_RE.source },
  window: enumOf("day", "month"),
  period: { ...str, pattern: DAY_RE.source },
  value: { ...int, minimum: 0 },
  limit: { ...int, minimum: 1, maximum: 9999999 },
  limitSource: enumOf("default", "override"),
  runbook: { ...str, pattern: "^[A-Za-z0-9_-]{1,32}(/[A-Za-z0-9_-]{1,32}){0,3}\\.md$" },
  dashboard: { ...str, pattern: "^https://[a-z0-9.-]{1,64}/[A-Za-z0-9._~/-]{0,100}$" },
  adrs: { kind: "array", maxItems: 5, items: { ...str, pattern: "^[0-9]{4}$" } },
};
const metricRequired = ["metric", "window", "period", "value", "limit", "limitSource"];
const metricSubject = (ev) => `metric/${ev.environment}/${ev.data.metric}/${windowCode(ev.data)}${ev.data.period}`;
const metricSubjectPattern = `^metric/(${ENVIRONMENTS.join("|")})/[a-z][a-z0-9.-]{0,28}/[dm]\\d{4}-\\d{2}-\\d{2}$`;
const idStem = (ev) => `${ev.data.metric}.${ev.environment}.${windowCode(ev.data)}${ev.data.period}`;

// One entry per event type: the data allowlist, which fields are required, the subject rule and,
// for metric types, the derived id. `metric: true` requires the environment and severity attributes.
export const TYPES = {
  "ops.metric.crossed": {
    title: "A metric crossed a threshold level",
    metric: true,
    severities: SEVERITIES,
    subjectPattern: metricSubjectPattern,
    fields: { ...metricFields, level: enumOf(50, 80, 100) },
    required: [...metricRequired, "level"],
    subjectOf: metricSubject,
    deriveId: (ev) => `${idStem(ev)}.c${ev.data.level}.l${ev.data.limit}`,
    valueAgrees: (d) => d.value * 100 >= d.level * d.limit,
  },
  "ops.metric.recovered": {
    title: "A metric condition cleared",
    metric: true,
    severities: SEVERITIES,
    subjectPattern: metricSubjectPattern,
    fields: { ...metricFields, level: enumOf(50, 80, 100), cause: enumOf("below", "period-ended") },
    required: [...metricRequired, "level", "cause"],
    subjectOf: metricSubject,
    deriveId: (ev) => `${idStem(ev)}.r${ev.data.level}${ev.data.cause === "below" ? "b" : "p"}.l${ev.data.limit}`,
    valueAgrees: (d) => d.cause !== "below" || d.value * 100 < d.level * d.limit,
  },
  "ops.metric.heartbeat": {
    title: "A metric producer is still sending",
    metric: true,
    severities: ["info"],
    subjectPattern: `^heartbeat/(${ENVIRONMENTS.join("|")})/[a-z][a-z0-9.-]{0,28}/[dm]$`,
    fields: { ...metricFields, every: enumOf("hour", "day") },
    required: [...metricRequired, "every"],
    subjectOf: (ev) => `heartbeat/${ev.environment}/${ev.data.metric}/${windowCode(ev.data)}`,
    deriveId: (ev) => `${ev.data.metric}.${ev.environment}.hb${windowCode(ev.data)}.${ev.time.slice(0, ev.data.every === "hour" ? 13 : 10)}`,
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
    subjectOf: (ev) => `issue/${ev.data.issue_id}`,
  },
  "ops.inbox.selftest": {
    title: "Setup read-back self-test",
    subjectPattern: "^selftest/[A-Za-z0-9._-]{1,64}$",
    fields: { v: { ...int, minimum: 1 }, project: { ...str, pattern: "^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$" } },
    required: ["v", "project"],
  },
};

export const sha256hex = (s) => createHash("sha256").update(s).digest("hex");
// A non-metric event that names a non-prod environment is keyed apart from the prod event with the same
// source and id or subject (metric ids and subjects already carry the environment).
const keyScope = (ev) => (!TYPES[ev.type].metric && ev.environment && ev.environment !== "prod" ? `${ev.environment}\n` : "");
export const dedupeKey = (ev) => sha256hex(`${keyScope(ev)}${ev.source}\n${ev.id}`);
export const incidentKey = (ev) => sha256hex(`${keyScope(ev)}${ev.source}\n${ev.subject}`);

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
  const invalid = `invalid-value: ${path}`;
  if (spec.enum && !spec.enum.includes(value)) return invalid;
  if (spec.kind === "array") {
    if (!Array.isArray(value) || value.length > spec.maxItems) return invalid;
    return value.some((item) => checkValue(spec.items, item, path)) ? invalid : null;
  }
  if (spec.kind === "string") {
    if (typeof value !== "string" || value.length > MAX_STRING) return invalid;
    if (spec.pattern && !new RegExp(spec.pattern).test(value)) return invalid;
    if (spec.format === "date-time" && !(TIME_RE.test(value) && !Number.isNaN(Date.parse(value)))) return invalid;
    return null;
  }
  if (!Number.isSafeInteger(value) || value < (spec.minimum ?? -Infinity) || value > (spec.maximum ?? Infinity)) return invalid;
  return null;
}

// `keys` is a list of { secret, environments, sources }: a signature from a key counts only for
// events whose environment (prod when absent) and source prefix that key lists.
// Returns { ok: true, event, keys } or { ok: false, status, reason }.
// 413 and 401 (signature) are decided before the body is trusted; 400 means the signed body is not
// contract v1; the key's scope is checked last, because environment and source come from the body.
export function parseEvent({ keys, headers, body, nowS }) {
  if (Buffer.byteLength(body) > MAX_BODY_BYTES) return { ok: false, status: 413, reason: "body-too-large" };
  const signed = [];
  let reason = "signature-mismatch";
  for (const key of keys) {
    const bad = verifySignature({
      secret: key.secret,
      id: headers.get("webhook-id"),
      timestamp: headers.get("webhook-timestamp"),
      signatureHeader: headers.get("webhook-signature"),
      body,
      nowS,
    });
    if (bad) reason = bad;
    else signed.push(key);
  }
  if (signed.length === 0) return { ok: false, status: 401, reason };
  const result = validateBody(body);
  if (!result.ok) return result;
  const { environment = "prod", source } = result.event;
  if (!signed.some((k) => k.environments.includes(environment) && k.sources.some((prefix) => source.startsWith(prefix)))) {
    return { ok: false, status: 401, reason: "key-not-allowed" };
  }
  return result;
}

// The contract rules without the signature, for a receiver that got the body from the inbox.
export function validateBody(body) {
  const refuse = (reason) => ({ ok: false, status: 400, reason });

  let ev;
  try { ev = JSON.parse(body); } catch { return refuse("not-json"); }
  if (ev === null || typeof ev !== "object" || Array.isArray(ev)) return refuse("not-json-object");
  if (body !== JSON.stringify(ev)) return refuse("non-canonical-body");
  for (const name of REQUIRED_ATTRS) if (!(name in ev)) return refuse(`missing-attribute: ${name}`);
  for (const name of Object.keys(ev)) if (!ALLOWED_ATTRS.has(name)) return refuse(`field-not-allowed: ${name}`);

  if (ev.specversion !== "1.0") return refuse("invalid-value: specversion");
  if (typeof ev.id !== "string" || !ID_RE.test(ev.id)) return refuse("invalid-value: id");
  if (typeof ev.source !== "string" || !SOURCE_RE.test(ev.source)) return refuse("invalid-value: source");
  if (typeof ev.type !== "string" || !Object.hasOwn(TYPES, ev.type)) return refuse(`unknown-type: ${ev.type}`);
  if (typeof ev.subject !== "string" || !SUBJECT_RE.test(ev.subject)) return refuse("invalid-value: subject");
  if (typeof ev.time !== "string" || !TIME_RE.test(ev.time) || Number.isNaN(Date.parse(ev.time))) return refuse("invalid-value: time");
  if (ev.dataschema !== `${SCHEMA_BASE}/${ev.type}.json`) return refuse("invalid-value: dataschema");
  if ("datacontenttype" in ev && ev.datacontenttype !== "application/json") return refuse("invalid-value: datacontenttype");

  const spec = TYPES[ev.type];
  for (const name of ["environment", "severity"]) {
    if (!(name in ev)) {
      if (spec.metric) return refuse(`missing-attribute: ${name}`);
      continue;
    }
    const allowed = name === "environment" ? ENVIRONMENTS : spec.severities ?? SEVERITIES;
    if (!allowed.includes(ev[name])) return refuse(`invalid-value: ${name}`);
  }
  if (!new RegExp(spec.subjectPattern).test(ev.subject)) return refuse("invalid-value: subject");
  const data = ev.data;
  if (data === null || typeof data !== "object" || Array.isArray(data)) return refuse("missing-attribute: data");
  for (const name of spec.required) if (!(name in data)) return refuse(`missing-attribute: data.${name}`);
  for (const name of Object.keys(data)) if (!Object.hasOwn(spec.fields, name)) return refuse(`field-not-allowed: data.${name}`);
  for (const [name, value] of Object.entries(data)) {
    const err = checkValue(spec.fields[name], value, `data.${name}`);
    if (err) return refuse(err);
  }
  if (spec.valueAgrees && !spec.valueAgrees(data)) return refuse("invalid-value: data.value");
  if (spec.subjectOf && ev.subject !== spec.subjectOf(ev)) return refuse("subject-mismatch");
  if (spec.deriveId && ev.id !== spec.deriveId(ev)) return refuse("id-not-deterministic");

  return { ok: true, event: ev, keys: { dedupe: dedupeKey(ev), incident: incidentKey(ev) } };
}

function propertySchema(f) {
  if (f.kind === "array") return { type: "array", maxItems: f.maxItems, items: propertySchema(f.items) };
  return {
    type: f.kind,
    ...(f.enum && { enum: f.enum }),
    ...(f.format && { format: f.format }),
    ...(f.pattern && { pattern: f.pattern }),
    ...(f.minimum !== undefined && { minimum: f.minimum }),
    ...(f.maximum !== undefined && { maximum: f.maximum }),
    ...(f.kind === "string" && { maxLength: MAX_STRING }),
  };
}

// The published JSON Schema of one type, derived from TYPES so the code and the file cannot differ.
export function jsonSchemaFor(type) {
  const spec = TYPES[type];
  const properties = {};
  for (const [name, f] of Object.entries(spec.fields)) properties[name] = propertySchema(f);
  return {
    $schema: "https://json-schema.org/draft/2020-12/schema",
    $id: `${SCHEMA_BASE}/${type}.json`,
    title: spec.title,
    type: "object",
    required: REQUIRED_ATTRS.concat("data", spec.metric ? ["environment", "severity"] : []),
    additionalProperties: false,
    properties: {
      specversion: { const: "1.0" },
      id: { type: "string", pattern: ID_RE.source },
      source: { type: "string", pattern: SOURCE_RE.source },
      type: { const: type },
      subject: { type: "string", pattern: spec.subjectPattern },
      time: { type: "string", format: "date-time" },
      environment: { enum: ENVIRONMENTS },
      severity: { enum: spec.severities ?? SEVERITIES },
      dataschema: { const: `${SCHEMA_BASE}/${type}.json` },
      datacontenttype: { const: "application/json" },
      data: { type: "object", required: spec.required, additionalProperties: false, properties },
    },
  };
}
