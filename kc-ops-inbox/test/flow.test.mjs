import test from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync, existsSync, chmodSync } from "node:fs";
import { createHash, generateKeyPairSync } from "node:crypto";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { run } from "../bin/ops-run.mjs";
import { recordGate, pickReview, namedOption } from "../bin/record-gate.mjs";
import { relayEvent } from "./rig.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const readme = readFileSync(join(here, "../ops-workflow/README.md"), "utf8");
const have = spawnSync("spacedock", ["--version"]).status === 0;
const opts = have ? {} : process.env.OPS_REQUIRE_SPACEDOCK ? {} : { skip: "spacedock not on PATH" };
if (!have && process.env.OPS_REQUIRE_SPACEDOCK) throw new Error("OPS_REQUIRE_SPACEDOCK is set but spacedock is not on PATH");

const sh = (cwd, ...a) => execFileSync("git", a, { cwd, encoding: "utf8" }).trim();
const PROJECT = "o/project";
const CAPTAIN = "captain";

function fixture() {
  const root = mkdtempSync(join(tmpdir(), "flow-"));
  const bare = join(root, "o", "project.git");
  mkdirSync(join(root, "o"), { recursive: true });
  execFileSync("git", ["init", "-q", "--bare", "-b", "main", bare]);
  const seed = join(root, "seed");
  execFileSync("git", ["clone", "-q", bare, seed], { stdio: "ignore" });
  sh(seed, "config", "user.email", "t@example.invalid"); sh(seed, "config", "user.name", "t");
  mkdirSync(join(seed, "docs/ops"), { recursive: true }); mkdirSync(join(seed, "docs/adr"), { recursive: true });
  writeFileSync(join(seed, "docs/ops/README.md"), readme);
  const adr = "# 0060. Ceiling\n\nDate: 2026-01-01\n\n## Status\n\nAccepted\n\n## Context\n\nc\n";
  writeFileSync(join(seed, "docs/adr/0060-ceiling.md"), adr);
  sh(seed, "add", "-A"); sh(seed, "commit", "-q", "-m", "init"); sh(seed, "branch", "-M", "main"); sh(seed, "push", "-q", "origin", "main");
  sh(seed, "remote", "set-url", "origin", `https://github.com/${PROJECT}.git`);
  sh(seed, "checkout", "-q", "--orphan", "spacedock-state/ops"); sh(seed, "rm", "-rfq", "."); sh(seed, "commit", "-q", "--allow-empty", "-m", "root");
  sh(seed, "push", "-q", `file://${bare}`, "spacedock-state/ops");
  const digest = `sha256:${createHash("sha256").update(adr).digest("hex")}`;
  const commit = execFileSync("git", ["-C", bare, "rev-parse", "main"], { encoding: "utf8" }).trim();
  return { root, bare, digest, commit };
}

async function fakeGithub(f) {
  const { privateKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
  const state = { prs: [], comments: [], patches: [], reviews: [], runs: {}, headSha: null };
  const server = http.createServer(async (req, res) => {
    let raw = ""; for await (const c of req) raw += c;
    const send = (s, b) => { res.writeHead(s, { "content-type": "application/json" }); res.end(JSON.stringify(b)); };
    const u = req.url;
    if (u === `/repos/${PROJECT}/installation`) return send(200, { id: 7 });
    if (u === "/app/installations/7/access_tokens") return send(201, { token: "ghs_fake", permissions: { contents: "write", pull_requests: "write", metadata: "read" }, repositories: [{ full_name: PROJECT }] });
    if (u === `/repos/${PROJECT}`) return send(200, { default_branch: "main" });
    if (u.startsWith(`/repos/${PROJECT}/pulls?state=open`)) {
      const head = decodeURIComponent(u.split("head=")[1]);
      return send(200, state.prs.filter((p) => p.state === "open" && `o:${p.head.ref}` === head));
    }
    if (u === `/repos/${PROJECT}/pulls` && req.method === "POST") {
      const b = JSON.parse(raw);
      const sha = execFileSync("git", ["-C", f.bare, "rev-parse", b.head], { encoding: "utf8" }).trim();
      const pr = { number: state.prs.length + 1, state: "open", draft: b.draft, title: b.title, body: b.body, head: { ref: b.head, sha } };
      state.prs.push(pr); return send(201, pr);
    }
    let m;
    if ((m = u.match(new RegExp(`^/repos/${PROJECT}/pulls/(\\d+)$`)))) {
      const pr = state.prs[Number(m[1]) - 1];
      if (req.method === "PATCH") { Object.assign(pr, JSON.parse(raw)); state.patches.push(JSON.parse(raw)); }
      return send(200, pr);
    }
    if ((m = u.match(new RegExp(`^/repos/${PROJECT}/pulls/(\\d+)/reviews`)))) return send(200, state.reviews);
    if ((m = u.match(new RegExp(`^/repos/${PROJECT}/issues/(\\d+)/comments$`)))) { if (state.commentStatus) return send(state.commentStatus, {}); state.comments.push(JSON.parse(raw).body); return send(201, {}); }
    if ((m = u.match(/^\/repos\/o\/trigger\/actions\/runs\/(\d+)$/))) return send(200, { status: state.runs[m[1]] ?? "in_progress" });
    send(404, { message: u });
  });
  await new Promise((r) => server.listen(0, r));
  return { state, url: `http://127.0.0.1:${server.address().port}`, privateKey: privateKey.export({ type: "pkcs8", format: "pem" }), close: () => { server.closeAllConnections?.(); server.close(); } };
}

function fakeFo(f, { cite = true } = {}) {
  const script = join(f.root, "fo.sh");
  const rulings = cite
    ? `Repository: o/project\nCommit: ${f.commit}\n\n### ADR 0060\n- path: docs/adr/0060-ceiling.md\n- digest: ${cite === "bad" ? "sha256:" + "0".repeat(64) : f.digest}\n- status: Accepted\n`
    : "none";
  writeFileSync(script, `#!/bin/bash
set -e
r="docs/ops/$SLUG.md"
python3 - "$r" <<'PY'
import sys,re
p=sys.argv[1]; t=open(p).read()
fill={"Diagnosis":"- Known: 40 of 50.","Options":"1. Hold [ADR 0060].\\n2. Raise.","Recommendation":"Option 1, hold: first near event.","Rulings cited":${JSON.stringify(rulings)}}
for k,v in fill.items():
    t=re.sub(r"(## "+k+r"\\n\\n)\\(to be written by the First Officer\\)",lambda m:m.group(1)+v,t)
open(p,"w").write(t)
PY
`);
  chmodSync(script, 0o755);
  return `bash ${script}`;
}

const baseEnv = (f, gh, ev, extra = {}) => ({
  ...process.env, GITHUB_API_URL: gh.url, OPS_GIT_BASE: `file://${f.root}`, OPS_AGENT_APP_CLIENT_ID: "42", OPS_AGENT_APP_PRIVATE_KEY: gh.privateKey,
  PROJECT_REPO: PROJECT, TRIGGER_REPO: "o/trigger", TRIGGER_RUN_URL: "https://example.test/run/1", GITHUB_TOKEN: "ghs_trigger",
  OPS_EVENT: JSON.stringify(ev), OPS_BRANCH: "ceiling-signed-in-2026-10-20-abcd1234", OPS_RECEIVED: "2026-10-20T00:00:00.000Z", OPS_POLL_MS: "50", OPS_JOIN_WAIT_S: "5",
  ...extra,
});

const withEnv = async (env, fn) => {
  const saved = { ...process.env };
  Object.assign(process.env, env);
  const lines = []; const log = console.log; console.log = (...a) => lines.push(a.join(" "));
  try { await fn(env); } finally { console.log = log; for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k]; Object.assign(process.env, saved); }
  return lines;
};

const near = relayEvent("signed-in-2026-10-20-80", "bound-ceiling-near", 40);
const full = relayEvent("signed-in-2026-10-20-100", "bound-ceiling-full", 50);
const branch = "ceiling-signed-in-2026-10-20-abcd1234";

async function openIncident(f, gh, extra = {}) {
  const env = baseEnv(f, gh, near, { OPS_MODE: "open", FO_CMD: fakeFo(f, { cite: extra.fo ?? true }), ...extra.env });
  return withEnv(env, () => run(env));
}

test("open: an ops/<incident> branch, one Draft PR, the task and its first event on the state branch, the gate prepared", opts, async () => {
  const f = fixture(); const gh = await fakeGithub(f);
  await openIncident(f, gh);
  assert.equal(gh.state.prs.length, 1);
  const pr = gh.state.prs[0];
  assert.equal(pr.draft, true);
  assert.equal(pr.head.ref, `ops/${branch}`);
  assert.match(pr.body, /^Citations: 1 OK, 0 REFUSED\./);
  const record = execFileSync("git", ["-C", f.bare, "show", `ops/${branch}:docs/ops/${branch}.md`], { encoding: "utf8" });
  assert.match(record, /\[ADR 0060\]/);
  assert.match(record, /### ADR 0060\n- check: OK/);
  assert.match(record, /\*\*How to decide:\*\*/);
  assert.match(record, /## Measures\n\n- Event received 2026-10-20T00:00:00.000Z · recommendation ready /);
  const files = execFileSync("git", ["-C", f.bare, "ls-tree", "-r", "--name-only", "spacedock-state/ops"], { encoding: "utf8" });
  assert.match(files, new RegExp(`${branch}/index.md`));
  assert.match(files, new RegExp(`${branch}/events/signed-in-2026-10-20-80.json`));
  assert.match(files, new RegExp(`${branch}/measures.json`));
  const changed = execFileSync("git", ["-C", f.bare, "diff", "--name-only", `main...ops/${branch}`], { encoding: "utf8" }).trim();
  assert.equal(changed, `docs/ops/${branch}.md`);
  const task = execFileSync("git", ["-C", f.bare, "show", `spacedock-state/ops:${branch}/index.md`], { encoding: "utf8" });
  assert.match(task, /status: decision/);
  assert.match(task, /decision-1/);
  gh.close();
});

test("open: a refused citation is marked inline and counted in the PR's first line, not removed", opts, async () => {
  const f = fixture(); const gh = await fakeGithub(f);
  await openIncident(f, gh, { fo: "bad" });
  assert.match(gh.state.prs[0].body, /^Citations: 0 OK, 1 REFUSED\./);
  const record = execFileSync("git", ["-C", f.bare, "show", `ops/${branch}:docs/ops/${branch}.md`], { encoding: "utf8" });
  assert.match(record, /\[ADR 0060 REFUSED\]/);
  assert.match(record, /REFUSED digest-mismatch/);
  gh.close();
});

test("open: an unfinished record is named in the PR instead of passing as done", opts, async () => {
  const f = fixture(); const gh = await fakeGithub(f);
  await openIncident(f, gh, { env: { FO_CMD: "true" } });
  assert.match(gh.state.prs[0].body, /Incomplete sections: Diagnosis, Options, Recommendation, Rulings cited\./);
  gh.close();
});

test("join: the event lands as a file on the task and a PR comment, the PR's first line says it came later, no second PR", opts, async () => {
  const f = fixture(); const gh = await fakeGithub(f);
  await openIncident(f, gh);
  const env = baseEnv(f, gh, full, { OPS_MODE: "join", OPS_OPENING_RUN: "1001" });
  await withEnv(env, () => run(env));
  assert.equal(gh.state.prs.length, 1);
  assert.equal(gh.state.comments.length, 1);
  assert.match(gh.state.comments[0], /Event 2 joined this incident/);
  assert.match(gh.state.prs[0].body, /^Events joined after this recommendation: 1 \(latest signed-in-2026-10-20-100/);
  assert.match(gh.state.prs[0].body, /Citations: 1 OK/);
  const files = execFileSync("git", ["-C", f.bare, "ls-tree", "-r", "--name-only", "spacedock-state/ops"], { encoding: "utf8" });
  assert.match(files, /events\/signed-in-2026-10-20-100.json/);
  gh.close();
});

test("join fails loudly when the PR comment is refused, so the run is red and the inbox's notice is not the only record", opts, async () => {
  const f = fixture(); const gh = await fakeGithub(f);
  await openIncident(f, gh);
  gh.state.commentStatus = 403;
  const env = baseEnv(f, gh, full, { OPS_MODE: "join", OPS_OPENING_RUN: "1001" });
  await assert.rejects(withEnv(env, () => run(env)), /comment-403/);
  gh.close();
});

test("join after a failed opening run opens a new incident branch instead of waiting", opts, async () => {
  const f = fixture(); const gh = await fakeGithub(f);
  gh.state.runs["1001"] = "completed";
  const env = baseEnv(f, gh, full, { OPS_MODE: "join", OPS_OPENING_RUN: "1001", FO_CMD: fakeFo(f) });
  await withEnv(env, () => run(env));
  assert.equal(gh.state.prs.length, 1);
  assert.equal(gh.state.prs[0].head.ref, `ops/${branch}-signed-in-2026-10-20-100`);
  assert.equal(gh.state.comments.length, 0);
  gh.close();
});

test("open when ops/<incident> already exists treats the event as joined (the ref create is the backstop)", opts, async () => {
  const f = fixture(); const gh = await fakeGithub(f);
  await openIncident(f, gh);
  const second = relayEvent("signed-in-2026-10-20-100", "bound-ceiling-full", 50);
  const env = baseEnv(f, gh, second, { OPS_MODE: "open", FO_CMD: fakeFo(f) });
  await withEnv(env, () => run(env));
  assert.equal(gh.state.prs.length, 1);
  assert.equal(gh.state.comments.length, 1);
  gh.close();
});

test("the self-test reads the agent token back and fails when it is wider than contents and pull requests on the project", opts, async () => {
  const f = fixture(); const gh = await fakeGithub(f);
  const env = baseEnv(f, gh, near, { OPS_MODE: "selftest" });
  const lines = await withEnv(env, () => run(env));
  assert.match(lines.join("\n"), /"evt":"selftest-agent-token".*"ok":true/);
  gh.close();
});

function review(id, state, login, sha, body = "") { return { id, state, body, commit_id: sha, user: { login } }; }

test("pickReview takes only the Captain's latest deciding review on the current head", () => {
  const rows = [review(1, "APPROVED", "other", "h"), review(2, "APPROVED", CAPTAIN, "old"), review(3, "COMMENTED", CAPTAIN, "h", "Option 2"), review(4, "DISMISSED", CAPTAIN, "h")];
  assert.equal(pickReview(rows, CAPTAIN, "h").id, 3);
  assert.equal(pickReview([review(5, "COMMENTED", CAPTAIN, "h", "why is the limit 50?")], CAPTAIN, "h"), null);
  assert.equal(namedOption("option 1 or option 2?"), null);
  assert.equal(namedOption("Option 2, as written in Option 2"), "2");
  assert.equal(pickReview(rows.slice(0, 2), CAPTAIN, "h"), null);
});

async function gateFixture() {
  const f = fixture(); const gh = await fakeGithub(f);
  await openIncident(f, gh);
  const checkout = join(f.root, "gate-checkout");
  execFileSync("git", ["clone", "-q", join(f.bare), checkout], { stdio: "ignore" });
  sh(checkout, "remote", "set-url", "origin", f.bare);
  return { f, gh, checkout };
}
const gateEnv = (gh) => ({ ...process.env, GITHUB_API_URL: gh.url, GITHUB_TOKEN: "t", PROJECT_REPO: PROJECT, PR_NUMBER: "1", OPS_CAPTAIN_LOGIN: CAPTAIN });

test("gate: the Captain's approval on the head records approve with his words and the two measures, and moves no ops/* branch", opts, async () => {
  const { f, gh, checkout } = await gateFixture();
  const head = gh.state.prs[0].head.sha;
  gh.state.reviews = [review(77, "APPROVED", CAPTAIN, head, "Go with option one.")];
  const out = await recordGate(gateEnv(gh), checkout);
  assert.deepEqual([out.result, out.decision, out.followed], ["recorded", "approve", "yes"]);
  const task = execFileSync("git", ["-C", f.bare, "show", `spacedock-state/ops:${branch}/index.md`], { encoding: "utf8" });
  assert.match(task, /by: person:captain/);
  assert.match(task, /decision: approve/);
  assert.match(task, /GitHub review 77 by captain on [0-9a-f]{40}: Go with option one\. \| received 2026-10-20T00:00:00.000Z; recommended .*followed yes/s);
  const measures = JSON.parse(execFileSync("git", ["-C", f.bare, "show", `spacedock-state/ops:${branch}/measures.json`], { encoding: "utf8" }));
  assert.equal(measures.followed, "yes");
  assert.equal(typeof measures.seconds_to_recommendation, "number");
  assert.equal(execFileSync("git", ["-C", f.bare, "rev-parse", `ops/${branch}`], { encoding: "utf8" }).trim(), head);
  const again = await recordGate(gateEnv(gh), checkout);
  assert.equal(again.result, "no-op");
  gh.close();
});

test("gate: a changes-requested review records revise and followed no; another reviewer, a stale head or no review records nothing", opts, async () => {
  const { f, gh, checkout } = await gateFixture();
  const head = gh.state.prs[0].head.sha;
  gh.state.reviews = [review(1, "APPROVED", "stranger", head), review(2, "APPROVED", CAPTAIN, "0".repeat(40))];
  assert.equal((await recordGate(gateEnv(gh), checkout)).result, "no-op");
  gh.state.reviews.push(review(3, "CHANGES_REQUESTED", CAPTAIN, head, "Option 2"));
  const out = await recordGate(gateEnv(gh), checkout);
  assert.deepEqual([out.decision, out.followed], ["revise", "no"]);
  gh.close();
});

test("gate: a Comment question leaves the gate open, so the Captain's later approval still records", opts, async () => {
  const { gh, checkout } = await gateFixture();
  const head = gh.state.prs[0].head.sha;
  gh.state.reviews = [review(1, "COMMENTED", CAPTAIN, head, "Why 50?")];
  assert.equal((await recordGate(gateEnv(gh), checkout)).result, "no-op");
  gh.state.reviews.push(review(2, "APPROVED", CAPTAIN, head, "ok"));
  const out = await recordGate(gateEnv(gh), checkout);
  assert.deepEqual([out.result, out.decision], ["recorded", "approve"]);
  gh.close();
});

test("gate: a Comment naming one option records revise with that review", opts, async () => {
  const { gh, checkout } = await gateFixture();
  gh.state.reviews = [review(3, "COMMENTED", CAPTAIN, gh.state.prs[0].head.sha, "Option 2 please")];
  const out = await recordGate(gateEnv(gh), checkout);
  assert.deepEqual([out.decision, out.followed], ["revise", "no"]);
  gh.close();
});

test("gate: a pull request from a non-ops branch is ignored", opts, async () => {
  const { gh, checkout } = await gateFixture();
  gh.state.prs[0].head.ref = "feature/x";
  gh.state.reviews = [review(1, "APPROVED", CAPTAIN, gh.state.prs[0].head.sha)];
  const out = await recordGate(gateEnv(gh), checkout);
  assert.deepEqual([out.result, out.why], ["no-op", "branch feature/x is not ops/*"]);
  gh.close();
});
