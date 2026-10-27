#!/usr/bin/env node
// Reads every setup step back from the live resources and sends one signed self-test event.
// Exit 0 only when every row is PASS. Prints no secret value.
import { spawnSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";
import { signBody, SCHEMA_BASE } from "../contract/contract.mjs";
import { namedOption } from "./record-gate.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const SETUP = join(here, "../setup");
const RULESETS = {
  R15: ["main", "ruleset-main.json", "project"],
  R16: ["ops-branches", "ruleset-ops-branches.json", "project"],
  R17: ["state-branch", "ruleset-state-branch.json", "project"],
  R19: ["trigger-main", "ruleset-trigger-main.json", "trigger"],
};
const AGENT_CREATIONS = "ruleset-agent-creations.json";
const ID_RE = /^[a-z0-9._/-]+\/[a-z0-9._-]+$/i;

export const ROW_DEFS = [
  ["R1", "S1", "trigger repository is private"],
  ["R2", "S1", "trigger repository holds 1 workflow pinned to a commit, 1 branch"],
  ["R3", "S2", "inbox site exists and this folder is linked to it"],
  ["R4", "S8", "inbox answers with contract v1 and all settings"],
  ["R5", "S8", "trigger variables set"],
  ["R6", "S9", "state branch spacedock-state/ops exists"],
  ["R7", "S3", "dispatch token: actions write on the trigger repository only"],
  ["R8", "S3", "dispatch App cannot start or re-run anything in the project"],
  ["R9", "S4", "agent token: contents and PR write on the project only"],
  ["R10", "S5", "dispatch App key stored on the inbox (name only)"],
  ["R11", "S6", "signing secret matches the inbox"],
  ["R12", "S6", "model token stored (name only)"],
  ["R13", "S7", "Slack webhook accepted the self-test notice"],
  ["R14", "S13", "self-test notice seen in the channel"],
  ["R15", "S10", "ruleset main matches its file, no bypass"],
  ["R16", "S10", "ruleset ops-branches matches its file, no bypass"],
  ["R17", "S10", "ruleset state-branch matches its file, no bypass"],
  ["R18", "S10", "no project workflow holds a secret or a write token an agent branch could reach"],
  ["R19", "S10", "ruleset trigger-main matches its file, no bypass"],
  ["R20", "S11", "ops-gate.yml is on the default branch, pinned to a commit"],
  ["R21", "S9", "project variable OPS_CAPTAIN_LOGIN is set"],
  ["R22", "S13", "every recorded gate names the Captain's review on that pull request's head"],
  ["R23", "S6", "inbox key list: every key has its secret, and none signs both prod and a non-prod environment"],
  ["R24", "S12", "inbox trigger rules are valid, and the Captain's Slack user is set when a rule routes to him"],
];
const GATE_DECISIONS = { approve: ["APPROVED"], revise: ["CHANGES_REQUESTED", "COMMENTED"] };

const norm = (v) => JSON.stringify(sortKeys(v));
function sortKeys(v) {
  if (Array.isArray(v)) return v.map(sortKeys);
  if (v && typeof v === "object") return Object.fromEntries(Object.keys(v).sort().map((k) => [k, sortKeys(v[k])]));
  return v;
}
const subset = (want, got) => {
  if (Array.isArray(want)) return Array.isArray(got) && want.length === got.length && want.every((w, i) => subset(w, got[i]));
  if (want && typeof want === "object") return got && typeof got === "object" && Object.keys(want).every((k) => subset(want[k], got[k]));
  return want === got;
};

// The file's rules must all be present with the file's parameters, and the live ruleset may hold no other rule or bypass actor.
export function rulesetMatches(file, live) {
  if (live.name !== file.name || live.target !== file.target || live.enforcement !== file.enforcement) return "name, target or enforcement differ";
  if (norm(live.bypass_actors ?? []) !== norm(file.bypass_actors ?? [])) return `bypass actors differ (file ${(file.bypass_actors ?? []).length}, live ${(live.bypass_actors ?? []).length})`;
  if (!subset(file.conditions, live.conditions)) return "conditions differ";
  if ((live.rules ?? []).length !== file.rules.length) return `rule count differs (file ${file.rules.length}, live ${(live.rules ?? []).length})`;
  for (const rule of file.rules) {
    const found = live.rules.find((r) => r.type === rule.type);
    if (!found) return `rule ${rule.type} missing`;
    if (rule.parameters && !subset(rule.parameters, found.parameters ?? {})) return `rule ${rule.type} parameters differ`;
  }
  return null;
}

// Any use of the secrets context holds a secret; only an exact GITHUB_TOKEN reference does not.
export function holdsSecret(text) {
  const rest = text.replace(/secrets\.GITHUB_TOKEN\b/g, "").replace(/secrets\[\s*(['"])GITHUB_TOKEN\1\s*\]/g, "");
  return /\$\{\{[^}]*\bsecrets\b/.test(rest) || /^\s*secrets:\s*inherit\b/m.test(rest);
}

const parseWorkflow = (text) => {
  try {
    const doc = parseYaml(text);
    return doc && typeof doc === "object" && !Array.isArray(doc) ? doc : null;
  } catch {
    return null;
  }
};

const grantsWrite = (perms) =>
  perms === "write-all" || (perms && typeof perms === "object" && !Array.isArray(perms) && Object.values(perms).some((v) => String(v).toLowerCase() === "write"));
const isPermissions = (p) => p === "read-all" || p === "write-all" || (p !== null && typeof p === "object" && !Array.isArray(p));

// The automatic GITHUB_TOKEN may write unless every job's effective permissions are explicit and none grants write.
// A workflow that does not parse, has no jobs map, or leaves a job without explicit permissions counts as write-capable.
export function tokenCanWrite(text) {
  const doc = parseWorkflow(text);
  if (!doc || !doc.jobs || typeof doc.jobs !== "object" || Array.isArray(doc.jobs) || Object.keys(doc.jobs).length === 0) return true;
  if (doc.permissions !== undefined && !isPermissions(doc.permissions)) return true;
  for (const job of Object.values(doc.jobs)) {
    if (!job || typeof job !== "object") return true;
    const effective = job.permissions !== undefined ? job.permissions : doc.permissions;
    if (!isPermissions(effective) || grantsWrite(effective)) return true;
  }
  return false;
}

const globToRe = (g) => new RegExp(`^${g.replace(/[.+^${}()|\\]/g, "\\$&").replace(/\*\*/g, "\u0000").replace(/\*/g, "[^/]*").replace(/\u0000/g, ".*")}$`);
const AGENT_REFS = ["ops/x", "spacedock-state/ops"];

// The workflow's events and push filters from its parsed `on:`; anything unreadable counts as exposed.
export function triggersOf(text) {
  const doc = parseWorkflow(text);
  const on = doc ? (doc.on !== undefined ? doc.on : doc.true) : undefined;
  if (on === undefined || on === null) return { unreadable: true, events: new Set(), push: null };
  let events;
  let push = null;
  if (typeof on === "string") events = new Set([on]);
  else if (Array.isArray(on)) events = new Set(on.map(String));
  else events = new Set(Object.keys(on));
  if (events.has("push")) {
    const cfg = !Array.isArray(on) && typeof on === "object" ? on.push : null;
    const list = (v) => (v === undefined || v === null ? null : [].concat(v).map(String));
    push = { branches: list(cfg?.branches), ignore: list(cfg?.["branches-ignore"]), tags: list(cfg?.tags) };
  }
  return { events, push };
}

// Workflows that hold a secret or a write-capable token and could run on a ref the agent can write: a pull request or workflow_run event, or a push to
// an ops/* or state ref, or (when the agent may create any branch) to any ref but the default branch.
export function exposedWorkflows(files, { defaultBranch, agentCreationsApplied }) {
  const out = [];
  for (const f of files) {
    if (!holdsSecret(f.text) && !tokenCanWrite(f.text)) continue;
    const t = triggersOf(f.text);
    const pullish = t.unreadable || [...t.events].some((e) => /^(pull_request|pull_request_target|pull_request_review|workflow_run|issue_comment|issues)$/.test(e));
    let pushHit = false;
    if (t.push) {
      const pats = t.push.branches;
      if (t.push.ignore || pats === null) pushHit = true;
      else if (agentCreationsApplied) pushHit = pats.some((g) => AGENT_REFS.some((r) => globToRe(g).test(r)));
      else pushHit = !pats.every((g) => g === defaultBranch);
    }
    if (pullish || pushHit) out.push(f.name);
  }
  return out;
}

const row = (id, v, obs, next) => ({ id, v, obs, ...(next ? { next } : {}) });

export function makeCtx(env = process.env) {
  const sh = (cmd, args, input) => {
    const r = spawnSync(cmd, args, { encoding: "utf8", input, env, maxBuffer: 64 * 1024 * 1024 });
    return { ok: r.status === 0, status: r.status, out: r.stdout ?? "", err: (r.stderr ?? "").trim().slice(0, 200) };
  };
  const ghJson = (args) => {
    const r = sh("gh", args);
    if (!r.ok) return { ok: false, err: r.err || `gh exited ${r.status}` };
    try { return { ok: true, json: JSON.parse(r.out) }; } catch { return { ok: false, err: "gh printed no JSON" }; }
  };
  return { sh, ghJson, fetch: (url, init) => fetch(url, { signal: AbortSignal.timeout(60000), ...init }), now: () => Date.now(), sleep: (ms) => new Promise((r) => setTimeout(r, ms)), env };
}

export async function readback(ctx, { project, trigger, inbox, slackLink, workflowsChecked }) {
  const rows = new Map();
  const set = (id, v, obs, next) => rows.set(id, row(id, v, obs, next));
  const guard = async (ids, fn) => {
    try { await fn(); } catch (err) { for (const id of ids) if (!rows.has(id)) set(id, "ERROR", `could not read: ${err.message}`, "fix the read, then read back again"); }
  };
  const gh = (id, args, on) => {
    const r = ctx.ghJson(args);
    if (!r.ok) { set(id, "ERROR", `could not read: ${r.err}`, "check your gh login and the repository name"); return null; }
    return r.json;
  };

  await guard(["R1"], async () => {
    const repo = gh("R1", ["api", `repos/${trigger}`]);
    if (repo) set("R1", repo.private === true ? "PASS" : "FAIL", `private: ${repo.private}`, repo.private === true ? null : "make the trigger repository private (S1)");
  });

  await guard(["R2"], async () => {
    const wfs = gh("R2", ["api", `repos/${trigger}/actions/workflows`]);
    const branches = wfs && gh("R2", ["api", `repos/${trigger}/branches`]);
    const file = branches && gh("R2", ["api", `repos/${trigger}/contents/.github/workflows/ops-event.yml`]);
    if (!file) return;
    const text = Buffer.from(file.content ?? "", "base64").toString("utf8");
    const pin = text.match(/^\s*ref: ([0-9a-f]{40})\s*$/m);
    const ok = wfs.total_count === 1 && branches.length === 1 && pin && !text.includes("__KC_OPS_INBOX_SHA__");
    set("R2", ok ? "PASS" : "FAIL", `${wfs.total_count} workflow(s), ${branches.length} branch(es), pinned commit ${pin ? pin[1].slice(0, 12) : "none"}`, ok ? null : "the trigger repository must hold only ops-event.yml with a 40-hex commit in place of the placeholder (S1)");
  });

  await guard(["R3"], async () => {
    const site = new URL(inbox).hostname.split(".")[0];
    const r = ctx.sh("netlify", ["status", "--json"]);
    const ok = r.ok && r.out.includes(site);
    set("R3", ok ? "PASS" : "FAIL", ok ? `linked to ${site}` : `netlify status ${r.ok ? `does not name ${site}` : `failed: ${r.err}`}`, ok ? null : "run S2 in this folder, then log in with netlify login");
  });

  await guard(["R4"], async () => {
    const res = await ctx.fetch(`${inbox.replace(/\/$/, "")}/health`);
    const h = await res.json();
    const ok = res.status === 200 && h.contract === "v1" && h.settings.present === h.settings.total && h.secrets.present === h.secrets.total;
    set("R4", ok ? "PASS" : "FAIL", `contract ${h.contract}, settings ${h.settings.present} of ${h.settings.total}, secrets ${h.secrets.present} of ${h.secrets.total}${h.secrets.missing?.length ? `, missing ${[...h.secrets.missing, ...h.settings.missing].join(" ")}` : ""}`, ok ? null : "set the missing names (S5 to S8), redeploy, read back again");
    set("R10", h.secrets.missing?.some((n) => n !== "SLACK_WEBHOOK_URL") ? "FAIL" : "PASS", `inbox secrets present ${h.secrets.present} of ${h.secrets.total}`, "set DISPATCH_APP_PRIVATE_KEY on the inbox (S5)");
    const c = h.config ?? { ok: false, keys: { error: "health reports no config" }, rules: { error: "health reports no config" } };
    const keyFault = Array.isArray(c.keys) ? null : c.keys?.error;
    const mixed = Array.isArray(c.keys) ? c.keys.filter((k) => k.environments.includes("prod") && k.environments.some((e) => e !== "prod")).map((k) => k.name) : [];
    set("R23", keyFault || mixed.length ? "FAIL" : "PASS", keyFault ?? (mixed.length ? `key ${mixed.join(", ")} signs prod and a non-prod environment` : c.keys.map((k) => `${k.name}: ${k.environments.join("+")} ${k.sources.join("+")}`).join("; ")), "set OPS_KEYS and each key's secret, one key for prod and one for preview and dev (S6)");
    const ruleFault = c.rules?.error ?? c.captain?.error ?? null;
    set("R24", ruleFault ? "FAIL" : "PASS", ruleFault ?? `${c.rules.source} rule list, ${c.rules.count} rules`, "fix OPS_RULES or set OPS_CAPTAIN_SLACK_USER, redeploy (S13)");
  });

  await guard(["R5"], async () => {
    const vars = gh("R5", ["variable", "list", "-R", trigger, "--json", "name"]);
    if (!vars) return;
    const names = vars.map((v) => v.name);
    const missing = ["OPS_PROJECT_REPO", "OPS_AGENT_APP_CLIENT_ID"].filter((n) => !names.includes(n));
    set("R5", missing.length ? "FAIL" : "PASS", `${2 - missing.length} of 2${missing.length ? `, missing ${missing.join(" ")}` : ""}`, missing.length ? "set the missing variable (S8)" : null);
  });

  await guard(["R6"], async () => {
    const r = ctx.sh("gh", ["api", `repos/${project}/branches/spacedock-state%2Fops`]);
    set("R6", r.ok ? "PASS" : "FAIL", r.ok ? "present" : "branch spacedock-state/ops not found", r.ok ? null : "run S9");
  });

  await guard(["R21"], async () => {
    const vars = gh("R21", ["variable", "list", "-R", project, "--json", "name"]);
    if (vars) set("R21", vars.some((v) => v.name === "OPS_CAPTAIN_LOGIN") ? "PASS" : "FAIL", vars.some((v) => v.name === "OPS_CAPTAIN_LOGIN") ? "set" : "missing", "run make-setup-pr.sh again or set the variable (S9)");
  });

  await guard(["R12"], async () => {
    const secrets = gh("R12", ["secret", "list", "-R", trigger, "--json", "name"]);
    if (!secrets) return;
    const names = secrets.map((s) => s.name);
    set("R12", names.includes("CLAUDE_CODE_OAUTH_TOKEN") ? "PASS" : "FAIL", names.includes("CLAUDE_CODE_OAUTH_TOKEN") ? "present" : "CLAUDE_CODE_OAUTH_TOKEN not found", "store the model token (S6)");
    if (!names.includes("OPS_AGENT_APP_PRIVATE_KEY") && rows.get("R10")?.v === "PASS") set("R10", "FAIL", "OPS_AGENT_APP_PRIVATE_KEY not found in the trigger repository", "store the agent App key (S5)");
  });

  const projectRuns = () => { const r = ctx.ghJson(["api", `repos/${project}/actions/runs?per_page=1`]); return r.ok ? r.json.total_count : null; };
  const before = projectRuns();
  await guard(["R7", "R8", "R9", "R11", "R13"], async () => {
    const secret = ctx.env.OPS_READBACK_SECRET;
    if (!secret) throw new Error("OPS_READBACK_SECRET is not in the environment; run through your secrets wrapper");
    const id = `readback-selftest-${randomUUID()}`;
    const event = JSON.stringify({ specversion: "1.0", id, source: "urn:ops-inbox:readback", type: "ops.inbox.selftest", subject: `selftest/${id}`, time: new Date(ctx.now()).toISOString(), dataschema: `${SCHEMA_BASE}/ops.inbox.selftest.json`, data: { v: 1, project } });
    const ts = String(Math.floor(ctx.now() / 1000));
    const res = await ctx.fetch(inbox, { method: "POST", headers: { "content-type": "application/cloudevents+json", "webhook-id": `msg_${id}`, "webhook-timestamp": ts, "webhook-signature": signBody({ secret, id: `msg_${id}`, timestamp: ts, body: event }) }, body: event });
    const out = await res.json().catch(() => ({}));
    set("R11", res.status === 200 ? "PASS" : "FAIL", `signed POST answered ${res.status}${out.error ? ` (${out.error})` : ""}`, res.status === 401 ? "OPS_READBACK_SECRET differs from the inbox's readback key, or that key does not allow prod and urn:ops-inbox: (S6)" : "read the inbox log, then read back again");
    if (res.status !== 200) return;
    const exact = out.mint_trigger?.permissions?.actions === "write" && Object.keys(out.mint_trigger.permissions).length === 1 && out.mint_trigger.repositories?.length === 1 && out.mint_trigger.repositories[0] === trigger;
    set("R7", exact ? "PASS" : "FAIL", `actions:${out.mint_trigger?.permissions?.actions}, repositories ${JSON.stringify(out.mint_trigger?.repositories)}`, "install the dispatch App on the trigger repository only, Actions write only (S3)");
    const refused = (s) => s >= 400;
    const after = projectRuns();
    const unchanged = before !== null && after === before;
    const ok = refused(out.mint_project?.status) && refused(out.project_dispatch?.status) && refused(out.project_rerun?.status) && unchanged;
    set("R8", ok ? "PASS" : "FAIL", `mint for project ${out.mint_project?.status}, dispatch ${out.project_dispatch?.status}, re-run ${out.project_rerun?.status}, project run count ${before} -> ${after}`, "the dispatch App must not be installed on the project (S3)");
    set("R13", out.slack?.status === 200 ? "PASS" : "FAIL", `webhook answered ${out.slack?.status ?? "no notice"}`, "store a working Slack webhook (S7)");
    const runId = out.run_id;
    const pollMs = Number(ctx.env.READBACK_POLL_MS || 5000);
    const deadline = ctx.now() + Number(ctx.env.READBACK_RUN_WAIT_S || 300) * 1000;
    let run = null;
    while (runId && ctx.now() < deadline) {
      const r = ctx.ghJson(["api", `repos/${trigger}/actions/runs/${runId}`]);
      if (r.ok && r.json.status === "completed") { run = r.json; break; }
      await ctx.sleep(pollMs);
    }
    if (!runId) set("R9", "FAIL", "the dispatch returned no run id", "the inbox must dispatch with return_run_details");
    else if (!run) set("R9", "ERROR", `trigger run ${runId} did not finish in time`, "open the run, then read back again");
    else set("R9", run.conclusion === "success" ? "PASS" : "FAIL", `trigger run ${runId} ${run.conclusion}: the agent token was exactly contents and PR write on the project`, run.conclusion === "success" ? null : "install the agent App on the project only, Contents and Pull requests write (S4)");
  });

  await guard(["R14"], async () => {
    if (!slackLink) return set("R14", "WAIT", "no message link given", "open the self-test notice in Slack, Copy link, rerun with --slack-link <link>");
    const ok = /^https:\/\/[a-z0-9-]+\.slack\.com\/archives\/[A-Z0-9]+\/p\d+/.test(slackLink);
    set("R14", ok ? "PASS" : "FAIL", ok ? `link ${slackLink.replace(/^https:\/\//, "")}` : "not a Slack message link", ok ? null : "use the link from Copy link on the notice");
  });

  await guard(["R15", "R16", "R17", "R19"], async () => {
    const cache = {};
    for (const [id, [, fileName, where]] of Object.entries(RULESETS)) {
      const repo = where === "trigger" ? trigger : project;
      cache[repo] ??= ctx.ghJson(["api", `repos/${repo}/rulesets?per_page=100`]);
      if (!cache[repo].ok) { set(id, "ERROR", `could not read: ${cache[repo].err}`, "check your gh login (rulesets need admin)"); continue; }
      const file = JSON.parse(readFileSync(join(SETUP, fileName), "utf8"));
      const summary = cache[repo].json.find((r) => r.name === file.name);
      if (!summary) { set(id, "FAIL", `ruleset ${file.name} not found`, `run the line of S10 for ${fileName} only, then read back again`); continue; }
      const live = ctx.ghJson(["api", `repos/${repo}/rulesets/${summary.id}`]);
      if (!live.ok) { set(id, "ERROR", `could not read: ${live.err}`, "check your gh login"); continue; }
      const why = rulesetMatches(file, live.json);
      set(id, why ? "FAIL" : "PASS", why ? `${file.name}: ${why}` : `${file.name} matches`, why ? `delete ruleset ${summary.id}, then run the line of S10 for ${fileName}` : null);
    }
  });

  await guard(["R18"], async () => {
    const all = ctx.ghJson(["api", `repos/${project}/rulesets?per_page=100`]);
    if (!all.ok) return set("R18", "ERROR", `could not read: ${all.err}`, "check your gh login");
    const wanted = JSON.parse(readFileSync(join(SETUP, AGENT_CREATIONS), "utf8"));
    const creation = all.json.find((r) => r.name === wanted.name);
    let applied = false;
    let rulesetNote = "no agent-creations ruleset";
    if (creation) {
      const live = ctx.ghJson(["api", `repos/${project}/rulesets/${creation.id}`]);
      const why = live.ok ? rulesetMatches(wanted, live.json) : live.err;
      if (why) return set("R18", "FAIL", `agent-creations ruleset: ${why}`, "fix or delete the ruleset (S10)");
      applied = true;
      rulesetNote = "agent-creations ruleset matches";
    }
    const repo = ctx.ghJson(["api", `repos/${project}`]);
    const list = ctx.ghJson(["api", `repos/${project}/contents/.github/workflows`]);
    if (!repo.ok || !list.ok) return set("R18", "ERROR", `could not read the project's workflows: ${repo.ok ? list.err : repo.err}`, "check your gh login");
    const files = [];
    for (const f of list.json.filter((x) => /\.ya?ml$/.test(x.name))) {
      const r = ctx.ghJson(["api", `repos/${project}/contents/.github/workflows/${f.name}`]);
      if (!r.ok) return set("R18", "ERROR", `could not read ${f.name}: ${r.err}`, "read back again");
      files.push({ name: f.name, text: Buffer.from(r.json.content ?? "", "base64").toString("utf8") });
    }
    const exposed = exposedWorkflows(files, { defaultBranch: repo.json.default_branch, agentCreationsApplied: applied });
    const seen = `${rulesetNote}; ${files.filter((f) => holdsSecret(f.text)).length} of ${files.length} workflows use a secret and ${files.filter((f) => tokenCanWrite(f.text)).length} can write with GITHUB_TOKEN; reachable from an agent ref: ${exposed.length ? exposed.join(", ") : "none"}`;
    if (!exposed.length) return set("R18", "PASS", seen);
    if (workflowsChecked) return set("R18", "PASS", `Captain read ${exposed.join(", ")} and attested no secret job runs for an agent branch or pull request; ${seen}`);
    set("R18", "FAIL", seen, "guard or remove the listed workflows' secrets, apply ruleset-agent-creations.json (S10), or read them and rerun with --workflows-checked");
  });

  await guard(["R22"], async () => {
    const tree = ctx.ghJson(["api", `repos/${project}/git/trees/spacedock-state%2Fops?recursive=1`]);
    if (!tree.ok) return set("R22", "ERROR", `could not read the state branch: ${tree.err}`, "check S9 and your gh login");
    const tasks = tree.json.tree.filter((e) => /^[^/]+\/index\.md$/.test(e.path)).map((e) => e.path.split("/")[0]);
    const captain = ctx.ghJson(["variable", "get", "OPS_CAPTAIN_LOGIN", "-R", project, "--json", "value"]);
    const login = captain.ok ? captain.json.value : null;
    if (!login) return set("R22", "ERROR", "could not read OPS_CAPTAIN_LOGIN", "set it (S9)");
    let checked = 0;
    const forged = [];
    for (const slug of tasks) {
      const file = ctx.ghJson(["api", `repos/${project}/contents/${slug}/index.md?ref=spacedock-state%2Fops`]);
      if (!file.ok) return set("R22", "ERROR", `could not read ${slug}: ${file.err}`, "read back again");
      const text = Buffer.from(file.json.content ?? "", "base64").toString("utf8");
      const resolutions = [...text.matchAll(/^\s+decision: (\w+)\n\s+reason: (.+)$/gm)];
      if (!resolutions.length) continue;
      const pr = ctx.ghJson(["api", `repos/${project}/pulls?state=all&head=${project.split("/")[0]}:ops/${slug}`]);
      const prs = pr.ok ? pr.json : [];
      const reviews = prs[0] ? ctx.ghJson(["api", `repos/${project}/pulls/${prs[0].number}/reviews?per_page=100`]) : { ok: false, json: [] };
      for (const [, decision, reasonRaw] of resolutions) {
        checked += 1;
        const reason = reasonRaw.replace(/^'|'$/g, "").replace(/''/g, "'");
        const m = reason.match(/^GitHub review (\d+) by (\S+) on ([0-9a-f]{40}):/);
        const rev = m && reviews.ok ? reviews.json.find((r) => String(r.id) === m[1]) : null;
        const ok = m && rev && m[2] === login && rev.user?.login === login && rev.commit_id === m[3] && prs[0].head.sha === m[3] && GATE_DECISIONS[decision]?.includes(rev.state) && (rev.state !== "COMMENTED" || namedOption(rev.body));
        if (!ok) forged.push(`${slug} (${decision})`);
      }
    }
    set("R22", forged.length ? "FAIL" : "PASS", `${checked} recorded gate(s) checked${forged.length ? `; no matching review by ${login} on the head: ${forged.join(", ")}` : ""}`, forged.length ? "the gate record does not follow from a review: treat the task's decision as unrecorded and investigate who pushed spacedock-state/ops" : null);
  });

  await guard(["R20"], async () => {
    const file = gh("R20", ["api", `repos/${project}/contents/.github/workflows/ops-gate.yml`]);
    if (!file) return;
    const text = Buffer.from(file.content ?? "", "base64").toString("utf8");
    const pins = [...text.matchAll(/^\s*ref: ([0-9a-f]{40})\s*$/gm)];
    const ok = pins.length >= 1 && !text.includes("__KC_OPS_INBOX_SHA__");
    set("R20", ok ? "PASS" : "FAIL", ok ? `present, pinned commit ${pins[0][1].slice(0, 12)}` : "ops-gate.yml has no pinned commit", "merge the setup PR (S11)");
  });

  return ROW_DEFS.map(([id, step, what]) => ({ id, step, what, ...(rows.get(id) ?? row(id, "ERROR", "not read", "report this: the read-back skipped the row")) }));
}

export function render(rows, { banner }) {
  const out = [banner, ""];
  for (const r of rows) {
    out.push(`${r.v === "PASS" ? " " : ">"} ${r.id.padEnd(4)} ${r.step.padEnd(4)} ${r.v.padEnd(5)} ${r.what}`);
    out.push(`        observed: ${r.obs}`);
    if (r.next) out.push(`        next: ${r.next}`);
  }
  const n = (v) => rows.filter((r) => r.v === v).length;
  const bad = rows.some((r) => r.v !== "PASS");
  out.push("", `${n("PASS")} PASS, ${n("FAIL")} FAIL, ${n("ERROR")} ERROR, ${n("WAIT")} WAIT of ${rows.length}${bad ? "  (FAIL read back but wrong · ERROR could not read · WAIT needs you)" : ""}`);
  out.push(!bad ? "Connected: a signed event can reach Slack and wake only this project's ops workflow. Exit 0." : "The project is not connected. Exit 1.");
  return out.join("\n");
}

export function parseArgs(argv) {
  const o = { workflowsChecked: false };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--workflows-checked") o.workflowsChecked = true;
    else if (["--project", "--trigger", "--inbox", "--slack-link"].includes(a) && argv[i + 1]) o[a.slice(2).replace(/-(\w)/g, (_, c) => c.toUpperCase())] = argv[++i];
    else return null;
  }
  if (!o.project || !o.trigger || !o.inbox || !ID_RE.test(o.project) || !ID_RE.test(o.trigger) || !/^https:\/\//.test(o.inbox)) return null;
  return o;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = parseArgs(process.argv.slice(2));
  if (!args) {
    console.error("usage: node readback.mjs --project <owner/name> --trigger <owner/name> --inbox <https://.../inbox> [--slack-link <link>] [--workflows-checked]\nneeds OPS_READBACK_SECRET in the environment (use your secrets wrapper)");
    process.exit(2);
  }
  const rows = await readback(makeCtx(), args);
  console.log(render(rows, { banner: `kc-ops-inbox read-back · contract v1 · ${rows.length} rows · ${args.project} · trigger ${args.trigger} · inbox ${args.inbox}` }));
  process.exit(rows.every((r) => r.v === "PASS") ? 0 : 1);
}
