import test from "node:test";
import assert from "node:assert/strict";
import { makeHandler, config } from "../netlify/functions/inbox.mjs";
import { memoryStore, rig, signedRequest, relayEvent } from "./rig.mjs";

// The adapter's own seam: the Blobs store it opens, its name and consistency, and the paths it claims. Blobs' real atomicity is not exercised here.
test("under the Netlify adapter the core takes an event, drops its repeat and answers /inbox/health", async () => {
  const r = await rig();
  const opened = [];
  const store = memoryStore();
  const adapter = makeHandler((opts) => { opened.push(opts); return store; }, r.env);
  const post = (init, url = "http://inbox.test/inbox") => adapter(new Request(url, init));

  const req = signedRequest(relayEvent(80));
  const first = await post(req);
  const again = await post(req);
  assert.deepEqual([first.status, again.status], [202, 200]);
  assert.equal(r.state.dispatches.length, 1);
  assert.deepEqual(opened[0], { name: "ops-inbox", consistency: "strong" });
  assert.ok([...store.m.keys()].some((k) => k.startsWith("event.")) && [...store.m.keys()].some((k) => k.startsWith("incident.")));
  const health = await post({ method: "GET" }, "http://inbox.test/inbox/health");
  assert.equal((await health.json()).contract, "v1");
  assert.deepEqual(config.path, ["/inbox", "/inbox/health"]);
  r.close();
});
