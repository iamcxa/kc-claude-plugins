import { ENVIRONMENTS, SEVERITIES, TYPES, isUsableKey } from "../contract/contract.mjs";

export const RECEIVERS = ["record", "agent", "captain"];

// First match wins. The cells of the approved routing table (environment x severity) come first; an event
// without environment, such as a Sentry alert, falls through to the last rule and keeps the agent route.
export const DEFAULT_RULES = [
  { name: "prod-critical", match: { environment: ["prod"], severity: ["critical"] }, receiver: "captain" },
  { name: "prod-warning", match: { environment: ["prod"], severity: ["warning"] }, receiver: "agent" },
  { name: "preview-critical", match: { environment: ["preview"], severity: ["critical"] }, receiver: "agent" },
  { name: "other-environments", match: { environment: ENVIRONMENTS }, receiver: "record" },
  { name: "no-environment", match: {}, receiver: "agent" },
];

const NAME = /^[a-z][a-z0-9-]{0,31}$/;
const SOURCE_PREFIX = /^urn:[a-z0-9-]{1,32}(:[a-z0-9-]{1,32}){0,3}:$/;
const SECRET_ENV = /^[A-Z][A-Z0-9_]{0,63}$/;
const CAPTAIN_USER = /^[UW][A-Z0-9]{2,20}$/;
const MATCH_FIELDS = { type: (v) => Object.hasOwn(TYPES, v), source: (v) => SOURCE_PREFIX.test(v), environment: (v) => ENVIRONMENTS.includes(v), severity: (v) => SEVERITIES.includes(v) };
const RESERVED_ENV = ["OPS_RULES", "OPS_KEYS", "OPS_CAPTAIN_SLACK_USER", "DISPATCH_APP_PRIVATE_KEY", "SLACK_WEBHOOK_URL"];

const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const only = (o, allowed) => Object.keys(o).every((k) => allowed.includes(k));

function parseJson(text, what) {
  try { return JSON.parse(text); } catch { throw new Error(`${what}: not JSON`); }
}

// Throws an Error whose message names the first fault; the message holds no value from the input beyond a rule or key name that matched NAME.
export function parseRules(text) {
  if (text === undefined || text === "") return DEFAULT_RULES;
  const rules = parseJson(text, "OPS_RULES");
  if (!Array.isArray(rules) || rules.length === 0 || rules.length > 50) throw new Error("OPS_RULES: needs 1 to 50 rules");
  const seen = new Set();
  rules.forEach((rule, i) => {
    const at = `OPS_RULES[${i}]`;
    if (!isObject(rule) || !only(rule, ["name", "match", "receiver"])) throw new Error(`${at}: only name, match and receiver`);
    if (typeof rule.name !== "string" || !NAME.test(rule.name) || seen.has(rule.name)) throw new Error(`${at}: name missing, malformed or repeated`);
    seen.add(rule.name);
    if (!RECEIVERS.includes(rule.receiver)) throw new Error(`${at}: receiver is one of ${RECEIVERS.join(", ")}`);
    if (!isObject(rule.match) || !only(rule.match, Object.keys(MATCH_FIELDS))) throw new Error(`${at}: match holds only ${Object.keys(MATCH_FIELDS).join(", ")}`);
    for (const [field, values] of Object.entries(rule.match)) {
      if (!Array.isArray(values) || values.length === 0 || values.length > 20 || !values.every((v) => typeof v === "string" && MATCH_FIELDS[field](v))) throw new Error(`${at}: match.${field} must be a non-empty list of allowed values`);
    }
  });
  if (Object.keys(rules[rules.length - 1].match).length !== 0) throw new Error("OPS_RULES: the last rule must match everything (match {})");
  return rules;
}

const anyOf = (list, value) => value !== undefined && list.includes(value);

export function routeFor(event, rules) {
  if (event.type === "ops.metric.heartbeat") return { rule: "heartbeat", receiver: "record" };
  const m = (rule) => {
    const c = rule.match;
    return (!c.type || anyOf(c.type, event.type)) && (!c.source || (c.source.some((p) => event.source.startsWith(p)))) &&
      (!c.environment || anyOf(c.environment, event.environment)) && (!c.severity || anyOf(c.severity, event.severity));
  };
  const rule = rules.find(m);
  return { rule: rule.name, receiver: rule.receiver };
}

// Keys name the environment variable that holds each secret, so the list can sit in a plain setting.
export function parseKeys(text, env) {
  if (text === undefined || text === "") throw new Error("OPS_KEYS: not set");
  const list = parseJson(text, "OPS_KEYS");
  if (!Array.isArray(list) || list.length === 0 || list.length > 20) throw new Error("OPS_KEYS: needs 1 to 20 keys");
  const names = new Set();
  const envs = new Set(RESERVED_ENV);
  return list.map((k, i) => {
    const at = `OPS_KEYS[${i}]`;
    if (!isObject(k) || !only(k, ["name", "secretEnv", "environments", "sources"])) throw new Error(`${at}: only name, secretEnv, environments and sources`);
    if (typeof k.name !== "string" || !NAME.test(k.name) || names.has(k.name)) throw new Error(`${at}: name missing, malformed or repeated`);
    names.add(k.name);
    if (typeof k.secretEnv !== "string" || !SECRET_ENV.test(k.secretEnv) || envs.has(k.secretEnv)) throw new Error(`${at} (${k.name}): secretEnv missing, malformed, reserved or shared`);
    envs.add(k.secretEnv);
    if (!Array.isArray(k.environments) || !k.environments.every((e) => ENVIRONMENTS.includes(e)) || new Set(k.environments).size !== k.environments.length) throw new Error(`${at} (${k.name}): environments must be listed values of ${ENVIRONMENTS.join(", ")}`);
    if (!Array.isArray(k.sources) || !k.sources.every((p) => typeof p === "string" && SOURCE_PREFIX.test(p))) throw new Error(`${at} (${k.name}): sources must be urn prefixes ending in ":"`);
    const key = { name: k.name, secret: env[k.secretEnv], environments: k.environments, sources: k.sources };
    if (!isUsableKey(key)) throw new Error(`${at} (${k.name}): secret ${k.secretEnv} is not set, decodes to fewer than 16 bytes, or the key lists no environment or source`);
    return key;
  });
}

const captainFault = (rules, env) =>
  rules.some((r) => r.receiver === "captain") && !CAPTAIN_USER.test(env.OPS_CAPTAIN_SLACK_USER ?? "")
    ? "OPS_CAPTAIN_SLACK_USER: a rule routes to the captain, so a Slack user id is required" : null;

// Everything the inbox reads from its settings, checked at once; any fault throws, and the caller answers nothing but 500.
export function loadConfig(env) {
  const rules = parseRules(env.OPS_RULES);
  const keys = parseKeys(env.OPS_KEYS, env);
  const fault = captainFault(rules, env);
  if (fault) throw new Error(fault);
  return { rules, keys, captainUser: env.OPS_CAPTAIN_SLACK_USER ?? null };
}

// What GET /health may say: names and counts, never a value. Each part is checked on its own so one fault does not hide another.
export function configReport(env) {
  const out = { ok: true };
  const attempt = (name, fn) => {
    try { out[name] = fn(); } catch (err) { out.ok = false; out[name] = { error: err.message }; }
  };
  let rules = null;
  attempt("rules", () => { rules = parseRules(env.OPS_RULES); return { source: env.OPS_RULES ? "configured" : "default", count: rules.length }; });
  attempt("keys", () => parseKeys(env.OPS_KEYS, env).map((k) => ({ name: k.name, environments: k.environments, sources: k.sources })));
  const fault = rules && captainFault(rules, env);
  if (fault) { out.ok = false; out.captain = { error: fault }; }
  return out;
}
