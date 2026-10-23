import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";
import { readback, render, rulesetMatches, secretWorkflows, parseArgs, ROW_DEFS } from "../bin/readback.mjs";
import { handle } from "../core/inbox-core.mjs";
import { rig, SECRET, TRIGGER, PROJECT } from "./rig.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const setup = (f) => JSON.parse(readFileSync(join(root, "setup", f), "utf8"));
const b64 = (s) => Buffer.from(s).toString("base64");
const SHA = "a".repeat(40);
const INBOX = "https://site.netlify.app/inbox";

// A live GitHub, as the Captain's gh login would read it, with each resource correct unless a test breaks it.
function world(over = {}) {
  const w = {
    triggerPrivate: true, workflows: 1, branches: 1, triggerWorkflow: `    ref: ${SHA}\n`, vars: ["OPS_PROJECT_REPO", "OPS_AGENT_APP_CLIENT_ID"], projectVars: ["OPS_CAPTAIN_LOGIN"],
    secrets: ["CLAUDE_CODE_OAUTH_TOKEN", "OPS_AGENT_APP_PRIVATE_KEY"], stateBranch: true, gate: `  ref: ${SHA}\n`, projectWorkflows: [{ name: "ci.yml", text: "on: push\njobs: {}\n" }],
    runCount: 5, runConclusion: "success", rulesets: { project: ["ruleset-main.json", "ruleset-ops-branches.json", "ruleset-state-branch.json"], trigger: ["ruleset-trigger-main.json"] },
    ...over,
  };
  return w;
}

function ctxFor(w, gh, { slackKnown = true } = {}) {
  const store = new Map();
  const ids = { project: 100, trigger: 200 };
  const live = (repo, f) => ({ id: store.size + 1, ...setup(f) });
  const answer = (args) => {
    const path = args[0] === "api" ? args[1] : null;
    const key = args.join(" ");
    const fail = (e = "HTTP 404") => ({ ok: false, err: e });
    const ok = (json) => ({ ok: true, json });
    if (path === `repos/${TRIGGER}`) return ok({ private: w.triggerPrivate });
    if (path === `repos/${TRIGGER}/actions/workflows`) return ok({ total_count: w.workflows });
    if (path === `repos/${TRIGGER}/branches`) return ok(Array.from({ length: w.branches }, () => ({})));
    if (path === `repos/${TRIGGER}/contents/.github/workflows/ops-event.yml`) return ok({ content: b64(w.triggerWorkflow) });
    if (key === `variable list -R ${TRIGGER} --json name`) return ok(w.vars.map((name) => ({ name })));
    if (key === `variable list -R ${PROJECT} --json name`) return ok(w.projectVars.map((name) => ({ name })));
    if (key === `secret list -R ${TRIGGER} --json name`) return ok(w.secrets.map((name) => ({ name })));
    if (path === `repos/${PROJECT}/actions/runs?per_page=1`) return ok({ total_count: w.runCount });
    if (path?.startsWith(`repos/${TRIGGER}/actions/runs/`)) return ok({ status: "completed", conclusion: w.runConclusion });
    const rs = path?.match(/^repos\/([^/]+\/[^/]+)\/rulesets(\?per_page=100|\/(\d+))?$/);
    if (rs) {
      const where = rs[1] === TRIGGER ? "trigger" : "project";
      const files = w.rulesets[where];
      if (!rs[3]) return ok(files.map((f, i) => ({ id: i + 1, name: setup(f).name })));
      return ok(w.liveOverride?.[files[Number(rs[3]) - 1]] ?? setup(files[Number(rs[3]) - 1]));
    }
    if (path === `repos/${PROJECT}/contents/.github/workflows`) return ok(w.projectWorkflows.map((f) => ({ name: f.name })));
    if (path?.startsWith(`repos/${PROJECT}/contents/.github/workflows/ops-gate.yml`)) return w.gate === null ? fail() : ok({ content: b64(w.gate) });
    if (path?.startsWith(`repos/${PROJECT}/contents/.github/workflows/`)) return ok({ content: b64(w.projectWorkflows.find((f) => path.endsWith(f.name)).text) });
    return fail(`unexpected ${key}`);
  };
  return {
    env: { WEBHOOK_SECRET: SECRET, READBACK_POLL_MS: "1" },
    ghJson: (args) => answer(args),
    sh: (cmd, args) => {
      if (cmd === "netlify") return { ok: w.netlifyLinked !== false, out: JSON.stringify({ siteData: { name: "site" } }), err: "" };
      if (cmd === "gh" && args[0] === "api" && args[1] === `repos/${PROJECT}/branches/spacedock-state%2Fops`) return { ok: w.stateBranch, out: "{}", err: "" };
      return { ok: false, out: "", err: `unexpected ${cmd}` };
    },
    fetch: async (url, init) => {
      if (url.endsWith("/health")) return gh.call({ method: "GET" }, "http://inbox.test/inbox/health");
      return gh.call(init, "http://inbox.test/inbox");
    },
    now: Date.now, sleep: async () => {},
  };
}

const args = (extra = {}) => ({ project: PROJECT, trigger: TRIGGER, inbox: INBOX, slackLink: "https://x.slack.com/archives/C0123/p1792665727000100", workflowsChecked: true, ...extra });
const verdicts = (rows) => Object.fromEntries(rows.map((r) => [r.id, r.v]));

test("a fully set up project reads back every row PASS, with the self-test going through the real inbox core", async () => {
  const gh = await rig();
  const rows = await readback(ctxFor(world(), gh), args());
  assert.deepEqual(rows.filter((r) => r.v !== "PASS").map((r) => `${r.id} ${r.v} ${r.obs}`), []);
  assert.equal(rows.length, ROW_DEFS.length);
  assert.equal(gh.state.dispatches[0].inputs.mode, "selftest");
  assert.match(render(rows, { banner: "b" }), /^21 PASS, 0 FAIL, 0 ERROR, 0 WAIT of 21|\n21 PASS, 0 FAIL, 0 ERROR, 0 WAIT of 21\nConnected/);
  gh.close();
});

test("each broken resource fails its own row and no other, and the run is not connected", async () => {
  const cases = [
    ["R1", { triggerPrivate: false }], ["R2", { workflows: 2 }], ["R2", { triggerWorkflow: "ref: __KC_OPS_INBOX_SHA__\n" }], ["R5", { vars: ["OPS_PROJECT_REPO"] }],
    ["R6", { stateBranch: false }], ["R12", { secrets: ["OPS_AGENT_APP_PRIVATE_KEY"] }], ["R20", { gate: null }], ["R20", { gate: "ref: __KC_OPS_INBOX_SHA__\n" }],
    ["R21", { projectVars: [] }], ["R9", { runConclusion: "failure" }], ["R3", { netlifyLinked: false }],
    ["R15", { rulesets: { project: ["ruleset-ops-branches.json", "ruleset-state-branch.json"], trigger: ["ruleset-trigger-main.json"] } }],
    ["R19", { rulesets: { project: ["ruleset-main.json", "ruleset-ops-branches.json", "ruleset-state-branch.json"], trigger: [] } }],
  ];
  for (const [id, over] of cases) {
    const gh = await rig();
    const rows = await readback(ctxFor(world(over), gh), args());
    const bad = rows.filter((r) => r.v !== "PASS");
    assert.ok(bad.some((r) => r.id === id), `${id} should not pass with ${JSON.stringify(over)}: ${JSON.stringify(verdicts(rows))}`);
    assert.ok(bad.every((r) => ["FAIL", "ERROR"].includes(r.v)));
    assert.match(render(rows, { banner: "b" }), /The project is not connected\. Exit 1\./);
    gh.close();
  }
});

test("a ruleset with a bypass actor, an extra rule or changed parameters does not match its file", () => {
  const file = setup("ruleset-main.json");
  assert.equal(rulesetMatches(file, file), null);
  assert.match(rulesetMatches(file, { ...file, bypass_actors: [{ actor_id: 1, actor_type: "Team", bypass_mode: "always" }] }), /bypass actors differ/);
  assert.match(rulesetMatches(file, { ...file, rules: [...file.rules, { type: "creation" }] }), /rule count differs/);
  const loose = structuredClone(file); loose.rules[2].parameters.required_approving_review_count = 0;
  assert.match(rulesetMatches(file, loose), /parameters differ/);
  assert.match(rulesetMatches(file, { ...file, enforcement: "evaluate" }), /enforcement/);
});

test("a dispatch App that can reach the project fails R7 and R8; a signing secret the inbox does not share fails R11", async () => {
  const gh = await rig();
  const ctx = ctxFor(world(), gh);
  const realFetch = ctx.fetch;
  ctx.fetch = async (url, init) => {
    const res = await realFetch(url, init);
    if (init?.method !== "POST") return res;
    const out = await res.json();
    out.mint_project = { status: 201 }; out.project_dispatch = { status: 204 };
    return new Response(JSON.stringify(out), { status: 200 });
  };
  const rows = await readback(ctx, args());
  assert.equal(verdicts(rows).R8, "FAIL");
  const wrong = await rig(); wrong.env.WEBHOOK_SECRET = "whsec_" + Buffer.from("other").toString("base64");
  const rows2 = await readback(ctxFor(world(), wrong), args());
  assert.equal(verdicts(rows2).R11, "FAIL");
  assert.match(rows2.find((r) => r.id === "R11").next, /differs from the inbox/);
  gh.close(); wrong.close();
});

test("a project run started during the self-test fails R8", async () => {
  const gh = await rig();
  const w = world();
  const ctx = ctxFor(w, gh);
  const base = ctx.ghJson;
  let calls = 0;
  ctx.ghJson = (a) => { if (a[1] === `repos/${PROJECT}/actions/runs?per_page=1`) { calls += 1; return { ok: true, json: { total_count: calls === 1 ? 5 : 6 } }; } return base(a); };
  assert.equal(verdicts(await readback(ctx, args())).R8, "FAIL");
  gh.close();
});

test("without a Slack link R14 waits, and with only R14 waiting the exit is still 1", async () => {
  const gh = await rig();
  const rows = await readback(ctxFor(world(), gh), args({ slackLink: undefined }));
  assert.deepEqual(rows.filter((r) => r.v !== "PASS").map((r) => r.id), ["R14"]);
  assert.equal(rows.find((r) => r.id === "R14").v, "WAIT");
  assert.ok(!rows.every((r) => r.v === "PASS"));
  const bad = await readback(ctxFor(world(), gh), args({ slackLink: "https://example.com/x" }));
  assert.equal(verdicts(bad).R14, "FAIL");
  gh.close();
});

test("R18 waits for the Captain's workflow check unless the agent-creations ruleset is applied, and lists workflows holding secrets", async () => {
  const gh = await rig();
  const w = world({ projectWorkflows: [{ name: "release.yml", text: "env:\n  T: ${{ secrets.NPM_TOKEN }}\n" }, { name: "ci.yml", text: "env:\n  T: ${{ secrets.GITHUB_TOKEN }}\n" }] });
  const rows = await readback(ctxFor(w, gh), args({ workflowsChecked: false }));
  const r18 = rows.find((r) => r.id === "R18");
  assert.equal(r18.v, "WAIT");
  assert.match(r18.obs, /release\.yml/);
  assert.ok(!/ci\.yml/.test(r18.obs));
  const applied = world({ rulesets: { project: ["ruleset-main.json", "ruleset-ops-branches.json", "ruleset-state-branch.json", "ruleset-agent-creations.json"], trigger: ["ruleset-trigger-main.json"] } });
  assert.equal(verdicts(await readback(ctxFor(applied, gh), args({ workflowsChecked: false }))).R18, "PASS");
  assert.deepEqual(secretWorkflows([{ name: "a", text: "${{ secrets.GITHUB_TOKEN }}" }, { name: "b", text: "${{ secrets.X }}" }]), ["b"]);
  gh.close();
});

test("an unreadable resource is ERROR, not FAIL, and the run does not stop", async () => {
  const gh = await rig();
  const ctx = ctxFor(world(), gh);
  const base = ctx.ghJson;
  ctx.ghJson = (a) => (a[1] === `repos/${TRIGGER}` ? { ok: false, err: "HTTP 403" } : base(a));
  const rows = await readback(ctx, args());
  assert.equal(verdicts(rows).R1, "ERROR");
  assert.equal(verdicts(rows).R2, "PASS");
  gh.close();
});

test("argument checking", () => {
  assert.equal(parseArgs(["--project", "o/p"]), null);
  assert.equal(parseArgs(["--project", "o/p", "--trigger", "o/t", "--inbox", "http://x/inbox"]), null);
  assert.equal(parseArgs(["--project", "o/p", "--trigger", "o/t", "--inbox", "https://x/inbox", "--bogus"]), null);
  assert.deepEqual(parseArgs(["--project", "o/p", "--trigger", "o/t", "--inbox", "https://x/inbox", "--slack-link", "l", "--workflows-checked"]), { project: "o/p", trigger: "o/t", inbox: "https://x/inbox", slackLink: "l", workflowsChecked: true });
});

test("the runbook gives every step an owner and a command, and names exactly the rows the read-back reports", () => {
  const text = readFileSync(join(root, "setup/RUNBOOK.md"), "utf8");
  const steps = [...text.matchAll(/^## (S\d+) · (CAPTAIN ONLY|AGENT MAY RUN|ANYONE) · .+$([\s\S]*?)(?=^## S\d+ ·|(?![\s\S]))/gm)];
  assert.deepEqual(steps.map((m) => m[1]), Array.from({ length: 12 }, (_, i) => `S${i + 1}`));
  for (const [, id, , body] of steps) assert.match(body, /^    \S/m, `${id} has no command`);
  const named = steps.flatMap(([, id, , body]) => { const m = body.match(/^Read back by: (.+)$/m); assert.ok(m, `${id} names no rows`); return m[1] === "every row" ? [] : m[1].split(/\s+/).map((r) => [r, id]); });
  const defs = Object.fromEntries(ROW_DEFS.map(([r, s]) => [r, s]));
  for (const [r, s] of named) assert.equal(defs[r], s, `${r} is read back in ${defs[r]}, the runbook puts it in ${s}`);
  assert.deepEqual(named.map(([r]) => r).sort(), Object.keys(defs).sort());
  for (const f of readdirSync(join(root, "setup")).filter((n) => n.endsWith(".json") || n.endsWith(".sh"))) if (!/agent-creations/.test(f)) assert.ok(text.includes(f), `${f} is not used by the runbook`);
});
