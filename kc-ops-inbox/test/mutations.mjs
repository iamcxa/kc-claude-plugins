#!/usr/bin/env node
// Removes one check at a time from a temporary copy of the contract and requires the named test to fail.
// A mutation whose text is no longer in contract.mjs fails the run, so an edit cannot silently turn one into a no-op.
import { spawnSync } from "node:child_process";
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const REFUSALS = "each refusal fixture is refused with its own reason, exit 1";
const RULES = "contract rules beyond the fixtures";

const MUTATIONS = [
  ["missing required data field", "for (const name of spec.required) if (!(name in data)) return refuse(`missing-attribute: data.${name}`);", "", REFUSALS],
  ["data field outside the allowlist", "for (const name of Object.keys(data)) if (!Object.hasOwn(spec.fields, name)) return refuse(`field-not-allowed: data.${name}`);", "", REFUSALS],
  ["id not derived", 'if (spec.deriveId && ev.id !== spec.deriveId(ev)) return refuse("id-not-deterministic");', "", REFUSALS],
  ["recovered id without its cause letter", '${ev.data.cause === "below" ? "b" : "p"}', "", REFUSALS],
  ["bad signature", 'return "signature-mismatch";', "return null;", REFUSALS],
  ["unknown environment", 'name === "environment" ? ENVIRONMENTS', 'name === "environment" ? [...ENVIRONMENTS, "staging"]', REFUSALS],
  ["unknown severity", ": spec.severities ?? SEVERITIES;", ': [...SEVERITIES, "high"];', REFUSALS],
  ["free text in an enumerated field", "if (spec.enum && !spec.enum.includes(value)) return invalid;", "", REFUSALS],
  ["duplicate key, non-canonical body", 'if (body !== JSON.stringify(ev)) return refuse("non-canonical-body");', "", REFUSALS],
  ["key environments: any configured key's environments count", "k.environments.includes(environment)", "keys.some((x) => x.environments.includes(environment))", REFUSALS],
  ["key environments: no scope check", "if (!signed.some(", "if (false && !signed.some(", REFUSALS],
  ["key source prefix", "k.sources.some((prefix) => source.startsWith(prefix))", "true", "a key signs only the environments and the source prefixes it lists"],
  ["environment-less event counts as prod", 'const { environment = "prod", source }', 'const { environment = "dev", source }', REFUSALS],
  ["non-prod environment not in the keys of a non-metric type", '!TYPES[ev.type].metric && ev.environment && ev.environment !== "prod" ? `${ev.environment}\\n` : ""', '""', "a non-prod event of a non-metric type is keyed apart from the prod event with the same source and id"],
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
  MUTATIONS.forEach(([label, find, replace, expected], i) => {
    const dir = copy(`m${i}`);
    const file = join(dir, "contract/contract.mjs");
    const text = readFileSync(file, "utf8");
    if (text.split(find).length !== 2) { console.log(`ERROR  ${label}: mutation text not found exactly once`); bad++; return; }
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
