#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { parseEvent } from "../core/inbox-core.mjs";

const USAGE = "usage: node validate.mjs <fixture.json> [--now <epoch-seconds>]\n" +
  "fixture: { secret?, now?, headers: {webhook-id, webhook-timestamp, webhook-signature}, body: <raw string> }\n" +
  "secret falls back to OPS_WEBHOOK_SECRET; now falls back to the clock";

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
const secret = fixture.secret ?? process.env.OPS_WEBHOOK_SECRET;
if (!secret || typeof fixture.body !== "string" || typeof fixture.headers !== "object") {
  console.error(USAGE);
  process.exit(2);
}

const nowS = nowArg !== undefined ? Number(nowArg) : fixture.now ?? Math.floor(Date.now() / 1000);
const result = parseEvent({ secret, headers: new Headers(fixture.headers), body: fixture.body, nowS });
if (!result.ok) {
  console.log(result.reason);
  process.exit(1);
}
console.log(`valid ${result.event.type} ${result.keys.dedupe} ${result.keys.incident}`);
