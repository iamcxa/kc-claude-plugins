import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";
import { readback, render, rulesetMatches, holdsSecret, tokenCanWrite, triggersOf, exposedWorkflows, parseArgs, ROW_DEFS } from "../bin/readback.mjs";
import { handle } from "../core/inbox-core.mjs";
import { rig, READBACK_SECRET, KEYS, TRIGGER, PROJECT } from "./rig.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const setup = (f) => JSON.parse(readFileSync(join(root, "setup", f), "utf8"));
const b64 = (s) => Buffer.from(s).toString("base64");
const SHA = "a".repeat(40);
const INBOX = "https://site.netlify.app/inbox";

// A live GitHub, as the Captain's gh login would read it, with each resource correct unless a test breaks it.
function world(over = {}) {
  const w = {
    triggerPrivate: true, workflows: 1, branches: 1, triggerWorkflow: `    ref: ${SHA}\n`, vars: ["OPS_PROJECT_REPO", "OPS_AGENT_APP_CLIENT_ID"], projectVars: ["OPS_CAPTAIN_LOGIN"],
    secrets: ["CLAUDE_CODE_OAUTH_TOKEN", "OPS_AGENT_APP_PRIVATE_KEY"], stateBranch: true, gate: `  ref: ${SHA}\n`, projectWorkflows: [{ name: "ci.yml", text: "on: push\npermissions:\n  contents: read\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps: []\n" }],
    gates: {}, reviews: {}, prHead: "b".repeat(40), runCount: 5, runConclusion: "success", rulesets: { project: ["ruleset-main.json", "ruleset-ops-branches.json", "ruleset-state-branch.json"], trigger: ["ruleset-trigger-main.json"] },
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
    if (path === `repos/${PROJECT}`) return ok({ default_branch: "main" });
    if (path === `repos/${PROJECT}/git/trees/spacedock-state%2Fops?recursive=1`) return ok({ tree: Object.keys(w.gates).map((slug) => ({ path: `${slug}/index.md` })) });
    if (key === `variable get OPS_CAPTAIN_LOGIN -R ${PROJECT} --json value`) return ok({ value: "captain" });
    let g;
    if ((g = path?.match(/^repos\/[^/]+\/[^/]+\/contents\/([^/]+)\/index\.md\?ref=/))) return ok({ content: b64(w.gates[g[1]]) });
    if ((g = path?.match(/^repos\/[^/]+\/[^/]+\/pulls\?state=all&head=o:ops\/(.+)$/))) return ok([{ number: 1, head: { sha: w.prHead } }]);
    if (path?.match(/\/pulls\/1\/reviews/)) return ok(w.reviews[Object.keys(w.gates)[0]] ?? []);
    if (path === `repos/${PROJECT}/contents/.github/workflows`) return ok(w.projectWorkflows.map((f) => ({ name: f.name })));
    if (path?.startsWith(`repos/${PROJECT}/contents/.github/workflows/ops-gate.yml`)) return w.gate === null ? fail() : ok({ content: b64(w.gate) });
    if (path?.startsWith(`repos/${PROJECT}/contents/.github/workflows/`)) return ok({ content: b64(w.projectWorkflows.find((f) => path.endsWith(f.name)).text) });
    return fail(`unexpected ${key}`);
  };
  return {
    env: { OPS_READBACK_SECRET: READBACK_SECRET, READBACK_POLL_MS: "1" },
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
  assert.match(render(rows, { banner: "b" }), new RegExp(`${ROW_DEFS.length} PASS, 0 FAIL, 0 ERROR, 0 WAIT of ${ROW_DEFS.length}\\nConnected`));
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

test("R23 and R24 read the inbox's own key and rule configuration from its health", async () => {
  const cases = [
    ["R23", (env) => { env.OPS_KEYS = JSON.stringify([{ ...KEYS[0], environments: ["prod", "preview"] }, KEYS[2]]); }],
    ["R23", (env) => { delete env.KEY_PROD; }],
    ["R24", (env) => { env.OPS_RULES = "[]"; }],
    ["R24", (env) => { delete env.OPS_CAPTAIN_SLACK_USER; }],
  ];
  for (const [id, apply] of cases) {
    const gh = await rig();
    apply(gh.env);
    const row = (await readback(ctxFor(world(), gh), args())).find((r) => r.id === id);
    assert.equal(row.v, "FAIL", `${id}: ${row.obs}`);
    gh.close();
  }
  const gh = await rig();
  const rows = await readback(ctxFor(world(), gh), args());
  assert.match(rows.find((r) => r.id === "R23").obs, /prod: prod urn:relay:\+urn:sentry:; preview: preview\+dev urn:relay:; readback: prod urn:ops-inbox:/);
  assert.match(rows.find((r) => r.id === "R24").obs, /default rule list, 6 rules/);
  gh.close();
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
  const wrong = await rig(); wrong.env.KEY_READBACK = "whsec_" + Buffer.from("a-different-readback-secret-123").toString("base64");
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

const NPM = { name: "release.yml", text: "on:\n  push:\n    branches: [main]\nenv:\n  T: ${{ secrets.NPM_TOKEN }}\n" };
const withWf = (wfs, rulesetApplied = false) => world({ projectWorkflows: wfs, rulesets: { project: ["ruleset-main.json", "ruleset-ops-branches.json", "ruleset-state-branch.json", ...(rulesetApplied ? ["ruleset-agent-creations.json"] : [])], trigger: ["ruleset-trigger-main.json"] } });
const r18 = async (w, a = {}) => { const gh = await rig(); const rows = await readback(ctxFor(w, gh), args({ workflowsChecked: false, ...a })); gh.close(); return rows.find((r) => r.id === "R18"); };

test("R18 passes only by the workflows' triggers: a secret job on the default branch alone passes, one an agent ref can reach fails", async () => {
  assert.equal((await r18(withWf([NPM]))).v, "PASS", "a push to the default branch alone is safe even without the ruleset");
  const develop = { name: "release.yml", text: "on:\n  push:\n    branches: [main, develop]\nenv:\n  T: ${{ secrets.NPM_TOKEN }}\n" };
  assert.equal((await r18(withWf([develop]))).v, "FAIL", "without the ruleset the agent can create a develop branch");
  assert.equal((await r18(withWf([develop], true))).v, "PASS", "with the ruleset only ops/** and the state branch remain");
  const reached = (await r18(withWf([{ name: "ci.yml", text: "on:\n  pull_request:\njobs:\n  a:\n    env:\n      T: ${{ secrets.X }}\n" }], true)));
  assert.equal(reached.v, "FAIL");
  assert.match(reached.obs, /reachable from an agent ref: ci\.yml/);
});

test("R18 does not pass on the ruleset alone: a secret job triggered on ops/** fails with the ruleset applied", async () => {
  const opsPush = { name: "deploy.yml", text: "on:\n  push:\n    branches:\n      - main\n      - 'ops/**'\njobs:\n  a:\n    steps:\n      - run: x\n        env:\n          T: ${{ secrets.DEPLOY }}\n" };
  const row = await r18(withWf([opsPush], true));
  assert.equal(row.v, "FAIL");
  assert.match(row.obs, /agent-creations ruleset matches.*deploy\.yml/);
  assert.equal((await r18(withWf([opsPush], true), { workflowsChecked: true })).v, "PASS", "the Captain's attestation names the files and overrides");
  assert.equal((await r18(withWf([{ name: "s.yml", text: "on: push\nenv: ${{ secrets.X }}\n" }], true))).v, "FAIL", "push with no branch filter reaches ops/**");
  assert.equal((await r18(withWf([{ name: "t.yml", text: "on: [workflow_dispatch]\nenv: ${{ secrets.X }}\n" }], true))).v, "PASS");
});

const job = (extra = "") => `jobs:\n  a:\n    runs-on: ubuntu-latest\n${extra}    steps: []\n`;

test("a workflow an agent branch can trigger fails R18 when its automatic token can write, with no secret in it", async () => {
  const wf = (body) => ({ name: "lint.yml", text: `on:\n  pull_request:\n${body}` });
  const writes = {
    "no permissions": job(),
    "write-all": `permissions: write-all\n${job()}`,
    "top-level write": `permissions:\n  contents: write\n${job()}`,
    "flow-style write": `permissions: { contents: write }\n${job()}`,
    "quoted write": `permissions:\n  "contents": "write"\n${job()}`,
    "job-level write under a read top level": `permissions:\n  contents: read\n${job("    permissions:\n      pull-requests: write\n")}`,
    "job-level flow write": `permissions: read-all\n${job("    permissions: { issues: 'write' }\n")}`,
    "one job read, another unset": `jobs:\n  a:\n    permissions: {}\n    steps: []\n  b:\n    steps: []\n`,
    "no jobs": `permissions:\n  contents: read\n`,
    "a malformed document": `permissions: [unclosed\n${job()}`,
  };
  for (const [label, body] of Object.entries(writes)) {
    const row = await r18(withWf([wf(body)], true));
    assert.equal(row.v, "FAIL", label);
  }
  const reads = {
    "top-level read": `permissions:\n  contents: read\n${job()}`,
    "flow-style read": `permissions: { contents: read, pull-requests: read }\n${job()}`,
    "read-all": `permissions: read-all\n${job()}`,
    "empty set": `permissions: {}\n${job()}`,
    "every job explicit, none top-level": `jobs:\n  a:\n    permissions: { contents: read }\n    steps: []\n  b:\n    permissions: {}\n    steps: []\n`,
    "job narrows a write-free top level": `permissions:\n  contents: read\n${job("    permissions: {}\n")}`,
  };
  for (const [label, body] of Object.entries(reads)) assert.equal((await r18(withWf([wf(body)], true))).v, "PASS", label);
  assert.match((await r18(withWf([wf(job())], true))).obs, /can write with GITHUB_TOKEN; reachable from an agent ref: lint\.yml/);
  assert.equal(tokenCanWrite("jobs:\n  a:\n    permissions:\n      pull-requests: write\n"), true);
  assert.equal(tokenCanWrite("permissions: {}\njobs:\n  a:\n    steps: []\n"), false);
});

test("every form of the secrets context counts as holding a secret, and an exact GITHUB_TOKEN reference does not", () => {
  for (const t of ["${{ secrets.NPM_TOKEN }}", "${{ secrets['NPM_TOKEN'] }}", '${{ secrets["NPM_TOKEN"] }}', "${{ secrets[matrix.name] }}", "${{ toJSON(secrets) }}", "jobs:\n  c:\n    uses: ./.github/workflows/x.yml\n    secrets: inherit\n", "${{ secrets.GITHUB_TOKEN_X }}", "${{ secrets.GITHUB_TOKEN }} ${{ secrets.Y }}"]) assert.equal(holdsSecret(t), true, t);
  for (const t of ["${{ secrets.GITHUB_TOKEN }}", "${{ secrets['GITHUB_TOKEN'] }}", "run: echo no secrets here", "name: secretsmith"]) assert.equal(holdsSecret(t), false, t);
});

test("triggers are read from the inline, list and block forms of on:", () => {
  assert.deepEqual([...triggersOf("on: push\n").events], ["push"]);
  assert.deepEqual([...triggersOf("on: [push, pull_request]\n").events], ["push", "pull_request"]);
  const t = triggersOf("on:\n  push:\n    branches: [main, 'ops/**']\n  workflow_dispatch:\njobs: {}\n");
  assert.deepEqual([...t.events], ["push", "workflow_dispatch"]);
  assert.deepEqual(t.push.branches, ["main", "ops/**"]);
  assert.deepEqual([...triggersOf('"on": { push: { branches: ["main"] } }\n').events], ["push"]);
  assert.deepEqual(triggersOf("on:\n  push:\n    branches-ignore: [docs]\n").push.ignore, ["docs"]);
  assert.equal(exposedWorkflows([{ name: "x", text: "name: n\njobs: {}\n${{ secrets.A }}" }], { defaultBranch: "main", agentCreationsApplied: true }).length, 1, "no on: block is unreadable and counts as exposed");
});

const GATE = (id, login, sha, decision = "approve") => `---\ngates:\n    records:\n        - attempts:\n            - resolution:\n                by: person:captain\n                decision: ${decision}\n                reason: 'GitHub review ${id} by ${login} on ${sha}: ok | followed yes'\n---\n`;
const HEAD = "b".repeat(40);
const gateRow = async (over) => { const gh = await rig(); const rows = await readback(ctxFor(world(over), gh), args()); gh.close(); return rows.find((r) => r.id === "R22"); };
const rev = (id, state, login = "captain", sha = HEAD, body = "") => ({ id, state, commit_id: sha, user: { login }, body });

test("R22 passes for a gate that follows from the Captain's review on the head and fails for a forged one", async () => {
  assert.equal((await gateRow({})).v, "PASS");
  const good = await gateRow({ gates: { inc: GATE(9, "captain", HEAD) }, reviews: { inc: [rev(9, "APPROVED")] } });
  assert.equal(good.v, "PASS");
  assert.match(good.obs, /1 recorded gate\(s\) checked/);
  const option = await gateRow({ gates: { inc: GATE(9, "captain", HEAD, "revise") }, reviews: { inc: [rev(9, "COMMENTED", "captain", HEAD, "Option 2")] } });
  assert.equal(option.v, "PASS");
  const forged = [
    ["no such review", { gates: { inc: GATE(9, "captain", HEAD) }, reviews: { inc: [rev(8, "APPROVED")] } }],
    ["review by someone else", { gates: { inc: GATE(9, "captain", HEAD) }, reviews: { inc: [rev(9, "APPROVED", "stranger")] } }],
    ["gate names another login", { gates: { inc: GATE(9, "stranger", HEAD) }, reviews: { inc: [rev(9, "APPROVED", "stranger")] } }],
    ["review on an old commit", { gates: { inc: GATE(9, "captain", "c".repeat(40)) }, reviews: { inc: [rev(9, "APPROVED", "captain", "c".repeat(40))] } }],
    ["decision differs from the review", { gates: { inc: GATE(9, "captain", HEAD, "approve") }, reviews: { inc: [rev(9, "CHANGES_REQUESTED")] } }],
    ["a Comment that names no option", { gates: { inc: GATE(9, "captain", HEAD, "revise") }, reviews: { inc: [rev(9, "COMMENTED", "captain", HEAD, "why not?")] } }],
    ["a Comment that names two options", { gates: { inc: GATE(9, "captain", HEAD, "revise") }, reviews: { inc: [rev(9, "COMMENTED", "captain", HEAD, "Option 1 or option 2")] } }],
    ["a reason that cites no review", { gates: { inc: "---\n                decision: approve\n                reason: trust me\n---\n" }, reviews: { inc: [] } }],
  ];
  for (const [label, over] of forged) {
    const row = await gateRow(over);
    assert.equal(row.v, "FAIL", label);
    assert.match(row.obs, /inc \((approve|revise)\)/, label);
  }
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
  assert.deepEqual(steps.map((m) => m[1]), Array.from({ length: 13 }, (_, i) => `S${i + 1}`));
  for (const [, id, , body] of steps) assert.match(body, /^    \S/m, `${id} has no command`);
  const named = steps.flatMap(([, id, , body]) => { const m = body.match(/^Read back by: (.+)$/m); assert.ok(m, `${id} names no rows`); return m[1] === "every row" ? [] : m[1].split(/\s+/).map((r) => [r, id]); });
  const defs = Object.fromEntries(ROW_DEFS.map(([r, s]) => [r, s]));
  for (const [r, s] of named) assert.equal(defs[r], s, `${r} is read back in ${defs[r]}, the runbook puts it in ${s}`);
  assert.deepEqual(named.map(([r]) => r).sort(), Object.keys(defs).sort());
  for (const f of readdirSync(join(root, "setup")).filter((n) => n.endsWith(".json") || n.endsWith(".sh"))) if (!/agent-creations/.test(f)) assert.ok(text.includes(f), `${f} is not used by the runbook`);
});
