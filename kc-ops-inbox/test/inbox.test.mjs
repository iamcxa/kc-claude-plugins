import test from "node:test";
import assert from "node:assert/strict";
import { rig, signedRequest, relayEvent, sentryEvent, selftestEvent, PROJECT, TRIGGER, READBACK_SECRET } from "./rig.mjs";

const near = () => relayEvent(80);
const full = () => relayEvent(100);
const agentLine = (n) => n.blocks ? n.blocks[1].text.text : n.attachments[0].blocks[1].text.text;

test("a new incident opens: one dispatch in mode open, one 'New incident' notice", async () => {
  const r = await rig();
  const res = await r.call(signedRequest(near()));
  assert.equal(res.status, 202);
  assert.equal(r.state.dispatches.length, 1);
  const d = r.state.dispatches[0];
  assert.equal(d.inputs.mode, "open");
  assert.equal(JSON.parse(d.inputs.event).id, near().id);
  assert.match(d.inputs.branch, /^metric-prod-capacity\.signed-in-d2026-10-20-[0-9a-f]{8}$/);
  assert.equal(d.return_run_details, true);
  assert.match(d.inputs.received, /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
  assert.equal(r.state.slack.length, 1);
  assert.match(agentLine(r.state.slack[0]), /New incident `metric\/prod\/capacity\.signed-in\/d2026-10-20` · agent started/);
  r.close();
});

test("a later event of the same incident joins: mode join, the opening run named, 'Joins incident (event 2)'", async () => {
  const r = await rig();
  await r.call(signedRequest(near()));
  const res = await r.call(signedRequest(full()));
  assert.equal(res.status, 202);
  assert.equal((await res.json()).event_number, 2);
  assert.deepEqual(r.state.dispatches.map((d) => d.inputs.mode), ["open", "join"]);
  assert.equal(r.state.dispatches[1].inputs.opening_run, "1001");
  assert.equal(r.state.dispatches[1].inputs.branch, r.state.dispatches[0].inputs.branch);
  assert.match(agentLine(r.state.slack[1]), /Joins incident `metric\/prod\/capacity\.signed-in\/d2026-10-20` \(event 2\) · recorded on its ops task, no new agent run/);
  r.close();
});

test("another subject is a second incident, opened separately", async () => {
  const r = await rig();
  await r.call(signedRequest(near()));
  await r.call(signedRequest(relayEvent(100, { metric: "capacity.anonymous" })));
  assert.deepEqual(r.state.dispatches.map((d) => d.inputs.mode), ["open", "open"]);
  assert.notEqual(r.state.dispatches[0].inputs.branch, r.state.dispatches[1].inputs.branch);
  r.close();
});

test("a resent copy of an accepted event gives no notice, dispatch or claim, even re-signed", async () => {
  const r = await rig();
  await r.call(signedRequest(near()));
  const size = r.store.m.size;
  const again = await r.call(signedRequest(near()));
  const resigned = await r.call(signedRequest(near(), { timestamp: Math.floor(Date.now() / 1000) + 5 }));
  assert.deepEqual([again.status, resigned.status], [200, 200]);
  assert.equal(r.state.dispatches.length, 1);
  assert.equal(r.state.slack.length, 1);
  assert.equal(r.store.m.size, size);
  r.close();
});

test("concurrent sends: identical copies dispatch once; different events of one incident open exactly once", async () => {
  const r = await rig();
  const same = signedRequest(near());
  const out = await Promise.all([r.call(same), r.call(same), r.call(same)]);
  assert.equal(out.filter((x) => x.status === 202).length, 1);
  const r2 = await rig();
  const mixed = await Promise.all([50, 80, 100].map((level) => r2.call(signedRequest(relayEvent(level)))));
  assert.deepEqual(mixed.map((x) => x.status), [202, 202, 202]);
  assert.equal(r2.state.dispatches.filter((d) => d.inputs.mode === "open").length, 1);
  assert.equal(r2.state.dispatches.filter((d) => d.inputs.mode === "join").length, 2);
  const numbers = (await Promise.all(mixed.map((x) => x.json()))).map((b) => b.event_number).filter(Boolean).sort();
  assert.deepEqual(numbers, [2, 3]);
  r.close(); r2.close();
});

test("a tampered, stale or non-contract send is refused and claims nothing", async () => {
  const r = await rig();
  const bad = await r.call(signedRequest(near(), { tamper: true }));
  const stale = await r.call(signedRequest(near(), { timestamp: Math.floor(Date.now() / 1000) - 3600 }));
  const offContract = await r.call(signedRequest({ ...near(), extra: 1 }));
  assert.deepEqual([bad.status, stale.status, offContract.status], [401, 401, 400]);
  assert.equal(r.state.dispatches.length, 0);
  assert.equal(r.state.mints.length, 0);
  assert.equal(r.store.m.size, 0);
  assert.equal(r.state.slack.length, 0);
  r.close();
});

test("a refused dispatch releases the claims, says NOT started, and the sender's retry opens the incident", async () => {
  const r = await rig({ dispatchStatus: 403 });
  const res = await r.call(signedRequest(near()));
  assert.equal(res.status, 502);
  assert.equal(r.store.m.size, 0);
  assert.match(agentLine(r.state.slack[0]), /Needs action · GitHub refused the dispatch \(HTTP 403\), so no agent runs/);
  assert.equal(r.state.slack[0].attachments[0].color, "#d00000");
  r.state.flags.dispatchStatus = 200;
  const retry = await r.call(signedRequest(near()));
  assert.equal(retry.status, 202);
  assert.equal(r.state.dispatches[0].inputs.mode, "open");
  r.close();
});

test("a refused join releases only its own event claim and leaves the incident open", async () => {
  const r = await rig();
  await r.call(signedRequest(near()));
  r.state.flags.dispatchStatus = 403;
  const res = await r.call(signedRequest(full()));
  assert.equal(res.status, 502);
  assert.ok([...r.store.m.keys()].some((k) => k.startsWith("incident.")));
  assert.ok(![...r.store.m.keys()].some((k) => k.startsWith("event.") && JSON.parse(r.store.m.get(k)).id === full().id));
  r.close();
});

test("an unanswered dispatch keeps the claims (at-most-once), says UNCERTAIN, and a resend starts nothing", async () => {
  const r = await rig({ hangDispatch: true, timeoutMs: 200 });
  const res = await r.call(signedRequest(near()));
  assert.equal(res.status, 504);
  assert.match(agentLine(r.state.slack[0]), /Needs a look · agent start UNCERTAIN/);
  assert.equal(r.state.slack[0].attachments[0].color, "#e8890c");
  r.state.flags.hangDispatch = false;
  const resend = await r.call(signedRequest(near()));
  assert.equal((await resend.json()).status, "duplicate");
  assert.equal(r.state.dispatches.length, 0);
  assert.ok(r.logs.some((l) => l.evt === "dispatch-failed" && l.released === false));
  r.close();
});

test("a GitHub 5xx on dispatch keeps the claims like an unanswered one: 504, UNCERTAIN, a resend starts nothing", async () => {
  const r = await rig({ dispatchStatus: 500 });
  const res = await r.call(signedRequest(near()));
  assert.equal(res.status, 504);
  assert.equal((await res.json()).error, "dispatch-ambiguous");
  assert.match(agentLine(r.state.slack[0]), /Needs a look · agent start UNCERTAIN/);
  assert.ok(r.logs.some((l) => l.evt === "dispatch-failed" && l.released === false));
  r.state.flags.dispatchStatus = 200;
  const resend = await r.call(signedRequest(near()));
  assert.equal((await resend.json()).status, "duplicate");
  assert.equal(r.state.dispatches.length, 0);
  r.close();
});

test("a key whose secret decodes to fewer than 16 bytes, or is unset, refuses every event, even one signed with it", async () => {
  for (const secret of ["whsec_=", "whsec_!!!", "whsec_a", undefined]) {
    const r = await rig();
    r.env.KEY_PROD = secret;
    const res = await r.call(signedRequest(near(), { secret: secret ?? "whsec_=" }));
    assert.equal(res.status, 500, String(secret));
    assert.equal(r.state.dispatches.length + r.state.mints.length + r.state.slack.length + r.store.m.size, 0, String(secret));
    r.close();
  }
});

test("a refused token mint releases the claims and starts nothing", async () => {
  const r = await rig({ mintStatus: 403 });
  const res = await r.call(signedRequest(near()));
  assert.equal(res.status, 502);
  assert.equal(r.store.m.size, 0);
  assert.equal(r.state.dispatches.length, 0);
  r.close();
});

test("the mint asks only for actions:write on the trigger repository", async () => {
  const r = await rig();
  await r.call(signedRequest(near()));
  assert.deepEqual(r.state.mints[0], { repositories: ["trigger"], permissions: { actions: "write" } });
  r.close();
});

test("event text is escaped before Slack and cut at 200 characters", async () => {
  const r = await rig();
  await r.call(signedRequest(sentryEvent("s1", "TypeError: <!channel> total & more")));
  assert.match(r.state.slack[0].blocks[0].text.text, /&lt;!channel&gt; total &amp; more/);
  assert.ok(!JSON.stringify(r.state.slack[0]).includes("<!channel>"));
  const r2 = await rig();
  await r2.call(signedRequest(sentryEvent("s2", "x".repeat(400))));
  assert.match(r2.state.slack[0].blocks[0].text.text, /x{200}…/);
  assert.ok(!/x{201}/.test(r2.state.slack[0].blocks[0].text.text));
  r.close(); r2.close();
});

test("a Slack outage does not fail the event", async () => {
  const r = await rig({ slackStatus: 500 });
  const res = await r.call(signedRequest(near()));
  assert.equal(res.status, 202);
  assert.equal(r.state.dispatches.length, 1);
  r.close();
});

test("the self-test reports the trigger mint, the refused project calls and the Slack answer, and files no task", async () => {
  const r = await rig();
  const res = await r.call(signedRequest(selftestEvent("readback-selftest-1"), { secret: READBACK_SECRET }));
  const out = await res.json();
  assert.equal(res.status, 200);
  assert.deepEqual(out.mint_trigger, { permissions: { actions: "write" }, repositories: [TRIGGER] });
  assert.equal(out.mint_project.status, 422);
  assert.equal(out.project_dispatch.status, 404);
  assert.equal(out.project_rerun.status, 404);
  assert.equal(out.slack.status, 200);
  assert.equal(r.state.dispatches[0].inputs.mode, "selftest");
  assert.ok(![...r.store.m.keys()].some((k) => k.startsWith("incident.")));
  assert.deepEqual(r.state.refused.sort(), [`/repos/${PROJECT}/actions/runs/1/rerun`, `/repos/${PROJECT}/actions/workflows/ci.yml/dispatches`].sort());
  assert.match(agentLine(r.state.slack[0]), /Self-test run/);
  r.close();
});

test("GET /inbox/health counts settings and secrets by name and never returns a value", async () => {
  const r = await rig();
  delete r.env.SLACK_WEBHOOK_URL;
  const res = await r.call({ method: "GET" }, "http://inbox.test/inbox/health");
  const out = await res.json();
  assert.deepEqual(out.settings, { present: 4, total: 4, missing: [] });
  assert.deepEqual(out.secrets, { present: 1, total: 2, missing: ["SLACK_WEBHOOK_URL"] });
  assert.equal(out.config.ok, true);
  assert.deepEqual(out.config.rules, { source: "default", count: 6 });
  assert.deepEqual(out.config.keys.map((k) => k.name), ["prod", "preview", "readback"]);
  for (const secret of [r.env.KEY_PROD, r.env.KEY_PREVIEW, r.env.KEY_READBACK]) assert.ok(!JSON.stringify(out).includes(secret));
  r.close();
});

