#!/usr/bin/env node
// Removes one check at a time from a temporary copy of the contract and requires the named test to fail.
// A mutation whose text is no longer in its file fails the run, so an edit cannot silently turn one into a no-op.
import { spawnSync } from "node:child_process";
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const REFUSALS = "each refusal fixture is refused with its own reason, exit 1";
const RULES = "contract rules beyond the fixtures";
const TIME = "time must be on the calendar, and a metric event's time must be UTC";
const SENTRY = "sentry.issue.alert bounds every field except title and culprit";
const HOSTILE = "hostile input is refused with a constant-bounded reason and never thrown";
const ECHO = "a refusal reason repeats sender text only as a short token";
const CLOCK = "the clock must be a finite number and the timestamp decimal digits";
const KEYED = "a non-prod event is keyed apart from the prod event with the same source and id, whatever the type";
const VALIDATOR = "the validator exits 2 on a malformed fixture and never mistakes a crash for a refusal";
const PERIOD = "period must be a date on the calendar";
const SHORT = "a secret that decodes to fewer than 16 bytes verifies no signature, forged or not";
const KEYS = "a key that cannot sign anything is skipped, never used and never thrown on";
const SCHEMAS = "the published schemas equal the ones derived from the code and match the pinned digests";
const sentryField = (name, pattern) => [`sentry ${name} bounded`, `${name}: ${pattern}`, `${name}: str`, SENTRY];

const MUTATIONS = [
  ["missing required data field", "for (const name of spec.required) if (!(name in data)) return refuse(`missing-attribute: data.${name}`);", "", REFUSALS],
  ["data field outside the allowlist", "for (const name of Object.keys(data)) if (!Object.hasOwn(spec.fields, name)) return refuse(`field-not-allowed: data.${echo(name)}`);", "", REFUSALS],
  ["id not derived", 'if (spec.deriveId && ev.id !== spec.deriveId(ev)) return refuse("id-not-deterministic");', "", REFUSALS],
  ["recovered id without its cause letter", '${ev.data.cause === "below" ? "b" : "p"}', "", REFUSALS],
  ["bad signature", '  }\n  return "signature-mismatch";\n}', "  }\n  return null;\n}", REFUSALS],
  ["unknown environment", 'name === "environment" ? ENVIRONMENTS', 'name === "environment" ? [...ENVIRONMENTS, "staging"]', REFUSALS],
  ["unknown severity", ": spec.severities ?? SEVERITIES;", ': [...SEVERITIES, "high"];', REFUSALS],
  ["free text in an enumerated field", "if (spec.enum && !spec.enum.includes(value)) return invalid;", "", REFUSALS],
  ["duplicate key, non-canonical body", 'if (body !== canonical) return refuse("non-canonical-body");', "", REFUSALS],
  ["key environments: any configured key's environments count", "k.environments.includes(environment)", "keys.some((x) => x.environments.includes(environment))", REFUSALS],
  ["key environments: no scope check", "if (!signed.some(", "if (false && !signed.some(", REFUSALS],
  ["key source prefix", "k.sources.some((prefix) => source.startsWith(prefix))", "true", "a key signs only the environments and the source prefixes it lists"],
  ["environment-less event counts as prod", 'const { environment = "prod", source }', 'const { environment = "dev", source }', REFUSALS],
  ["non-prod environment prefix skipped for metric types", 'const keyScope = (ev) => (ev.environment && ev.environment !== "prod" ?', 'const keyScope = (ev) => (ev.environment && ev.environment !== "prod" && !ev.type.startsWith("ops.metric") ?', KEYED],
  ["calendar-valid time", "d.toISOString().slice(0, 19) === m[1]", "true", TIME],
  ["offset hours and minutes in range", "[+-](?:[01]\\d|2[0-3]):[0-5]\\d", "[+-]\\d{2}:\\d{2}", TIME],
  ["metric time must be UTC", 'if (spec.metric && !ev.time.endsWith("Z")) return refuse("invalid-value: time");', "", REFUSALS],
  // The validator bounds issue_id through the subject rule; the data pattern is for the published schema.
  [...sentryField("issue_id", '{ ...str, pattern: "^[A-Za-z0-9._-]{1,64}$" }').slice(0, 3), SCHEMAS],
  sentryField("event_id", '{ ...str, pattern: "^[A-Za-z0-9._-]{1,64}$" }'),
  sentryField("level", 'enumOf("fatal", "error", "warning", "info", "debug")'),
  sentryField("project", '{ ...str, pattern: "^[A-Za-z0-9._-]{1,64}$" }'),
  sentryField("web_url", '{ ...str, pattern: "^https://[A-Za-z0-9._~:/@!$&*,;=-]{1,480}$" }'),
  ["web_url excludes query, fragment, percent and plus", "https://[A-Za-z0-9._~:/@!$&*,;=-]{1,480}", "https://[A-Za-z0-9._~:/?#@!$&*+,;=%-]{1,480}", SENTRY],
  sentryField("triggered_rule", '{ ...str, pattern: "^[A-Za-z0-9._-]{1,64}$" }'),
  sentryField("release", '{ ...str, pattern: "^[A-Za-z0-9._@+-]{1,100}$" }'),
  ["canonical re-serialization does not throw", 'try { canonical = JSON.stringify(ev); } catch { return refuse("non-canonical-body"); }', "canonical = JSON.stringify(ev);", HOSTILE],
  ["validateBody refuses a non-string body", 'if (typeof body !== "string") return refuse("not-json");', "", HOSTILE],
  ["parseEvent refuses a non-string body", 'if (typeof body !== "string") return { ok: false, status: 400, reason: "not-json" };', "", HOSTILE],
  ["parseEvent refuses headers without get", 'if (!headers || typeof headers.get !== "function") return { ok: false, status: 401, reason: "missing-headers" };', "", HOSTILE],
  ["parseEvent ignores unusable keys", "Array.isArray(keys) ? keys.filter(isUsableKey) : []", "keys", HOSTILE],
  ["reason does not echo the type", "unknown-type: ${echo(ev.type)}", "unknown-type: ${ev.type}", ECHO],
  ["reason does not echo an attribute name", "`field-not-allowed: ${echo(name)}`", "`field-not-allowed: ${name}`", ECHO],
  ["reason does not echo a data field name", "`field-not-allowed: data.${echo(name)}`", "`field-not-allowed: data.${name}`", ECHO],
  ["clock must be finite", " || !Number.isFinite(nowS)", "", CLOCK],
  ["timestamp must be decimal digits", "!/^\\d+$/.test(timestamp)", "Number.isNaN(Number(timestamp))", CLOCK],
  ["selftest subject", "subjectOf: (ev) => `selftest/${ev.id}`,", "", "an ops.inbox.selftest subject must be selftest/<id>"],
  ["period calendar roundtrip", "new Date(`${d}T00:00:00Z`).toISOString().slice(0, 10) === d", "true", PERIOD],
  ["period format is checked", 'period: { ...str, pattern: DAY_RE.source, format: "date" },', "period: { ...str, pattern: DAY_RE.source },", PERIOD],
  ["sentry source must be urn:sentry:", 'if (spec.sourcePattern && !new RegExp(spec.sourcePattern).test(ev.source)) return refuse("invalid-value: source");', "", "a sentry.issue.alert must come from a urn:sentry: source"],
  ["key secret of at least 16 bytes (decode)", "return key.length >= MIN_KEY_BYTES ? key : null;", "return key.length > 0 ? key : null;", SHORT],
  ["isUsableKey applies the length check", "keyBytes(k.secret) !== null &&", "typeof k.secret === \"string\" &&", SHORT],
  ["verifySignature applies the length check", 'const key = keyBytes(secret);\n  if (!key) return "signature-mismatch";', 'const key = Buffer.from(String(secret).replace(/^whsec_/, ""), "base64");', SHORT],
  ["key needs an environment and a source", "a.length > 0 && ", "", KEYS],
  ["key environments and sources are non-empty strings", 'a.every((v) => typeof v === "string" && v.length > 0)', "true", KEYS],
  ["key environments and sources are arrays", "Array.isArray(a) && ", "", KEYS],
  ["key source prefix ends with a colon", 'k.sources.every((p) => p.endsWith(":"))', "true", KEYS],
  ["validator rejects an unusable key", " || !keys.every(isUsableKey)", "", VALIDATOR, "contract/validate.mjs"],
  ["validator rejects a fixture whose headers are not an object", "!isObject(fixture.headers) || ", "", VALIDATOR, "contract/validate.mjs"],
  ["validator reports a crash as exit 2", "console.error(`cannot validate fixture: ${err.message}`);\n  process.exit(2);", "console.error(`cannot validate fixture: ${err.message}`);\n  process.exit(1);", VALIDATOR, "contract/validate.mjs"],
  ["heartbeat severity above info", 'severities: ["info"],', "severities: SEVERITIES,", RULES],
  ["crossed value below its level", "valueAgrees: (d) => d.value * 100 >= d.level * d.limit,", "valueAgrees: () => true,", RULES],
  ["subject of another environment", 'if (spec.subjectOf && ev.subject !== spec.subjectOf(ev)) return refuse("subject-mismatch");', "", RULES],
  ["source with spaces", 'if (typeof ev.source !== "string" || !SOURCE_RE.test(ev.source)) return refuse("invalid-value: source");', "", RULES],
];

function runTests(dir) {
  const r = spawnSync("node", ["--test", "--test-reporter=tap", join(dir, "test/contract.test.mjs")], { encoding: "utf8" });
  return { status: r.status, failed: [...r.stdout.matchAll(/^not ok \d+ - (.*)$/gm)].map((m) => m[1]) };
}

const tmp = mkdtempSync(join(tmpdir(), "ops-contract-mutation-"));
let bad = 0;
try {
  const copy = (name) => {
    const dir = join(tmp, name);
    cpSync(root, dir, { recursive: true, filter: (src) => !src.includes("node_modules") });
    return dir;
  };
  const base = runTests(copy("baseline"));
  if (base.status !== 0) { console.log("baseline fails; fix the tests first"); process.exit(1); }
  MUTATIONS.forEach(([label, find, replace, expected, target = "contract/contract.mjs"], i) => {
    const dir = copy(`m${i}`);
    const file = join(dir, target);
    const text = readFileSync(file, "utf8");
    if (text.split(find).length !== 2) { console.log(`ERROR  ${label}: mutation text not found exactly once in ${target}`); bad++; return; }
    writeFileSync(file, text.replace(find, () => replace));
    const r = runTests(dir);
    const ok = r.status !== 0 && r.failed.includes(expected);
    if (!ok) bad++;
    console.log(`${ok ? "caught  " : "SURVIVED"} ${label} -> ${r.failed.join("; ") || "no test failed"}`);
  });
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
process.exit(bad === 0 ? 0 : 1);
