#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { parseEvent, isUsableKey, ENVIRONMENTS } from "./contract.mjs";

const USAGE = "usage: node validate.mjs <fixture.json> [--now <epoch-seconds>]\n" +
  "fixture: { secret? | keys?: [{secret, environments, sources}], now?, headers: {webhook-id, webhook-timestamp, webhook-signature}, body: <raw string> }\n" +
  "secret (or OPS_WEBHOOK_SECRET) is one key allowed for every environment and source; now falls back to the clock";

const args = process.argv.slice(2);
const nowIdx = args.indexOf("--now");
const nowArg = nowIdx >= 0 ? args.splice(nowIdx, 2)[1] : undefined;
if (args.length !== 1 || (nowIdx >= 0 && !/^\d+$/.test(nowArg ?? ""))) {
  console.error(USAGE);
  process.exit(2);
}

let fixture;
try {
  fixture = JSON.parse(readFileSync(args[0], "utf8"));
} catch (err) {
  console.error(`cannot read fixture: ${err.message}`);
  process.exit(2);
}
const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const secret = fixture?.secret ?? process.env.OPS_WEBHOOK_SECRET;
const keys = fixture?.keys ?? (secret ? [{ secret, environments: ENVIRONMENTS, sources: ["urn:"] }] : []);
if (!isObject(fixture) || !isObject(fixture.headers) || typeof fixture.body !== "string" || !Array.isArray(keys) || keys.length === 0 || !keys.every(isUsableKey) ||
  (fixture.now !== undefined && !Number.isFinite(fixture.now))) {
  console.error(USAGE);
  process.exit(2);
}

const nowS = nowArg !== undefined ? Number(nowArg) : fixture.now ?? Math.floor(Date.now() / 1000);
let result;
try {
  result = parseEvent({ keys, headers: new Headers(fixture.headers), body: fixture.body, nowS });
} catch (err) {
  console.error(`cannot validate fixture: ${err.message}`);
  process.exit(2);
}
if (!result.ok) {
  console.log(result.reason);
  process.exit(1);
}
console.log(`valid ${result.event.type} ${result.keys.dedupe} ${result.keys.incident}`);
