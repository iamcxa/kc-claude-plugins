#!/usr/bin/env node
// Reads every setup step back from the live resources and sends one signed self-test event.
// Exit 0 only when every row is PASS. Prints no secret value.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { signBody, SCHEMA_BASE } from "../core/inbox-core.mjs";

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
  ["R10", "S5", "App key and signing secret stored (names only)"],
  ["R11", "S6", "signing secret matches the inbox"],
  ["R12", "S6", "model token stored (name only)"],
  ["R13", "S7", "Slack webhook accepted the self-test notice"],
  ["R14", "S12", "self-test notice seen in the channel"],
  ["R15", "S10", "ruleset main matches its file, no bypass"],
  ["R16", "S10", "ruleset ops-branches matches its file, no bypass"],
  ["R17", "S10", "ruleset state-branch matches its file, no bypass"],
  ["R18", "S10", "no project workflow holds a secret an agent branch could reach"],
  ["R19", "S10", "ruleset trigger-main matches its file, no bypass"],
  ["R20", "S11", "ops-gate.yml is on the default branch, pinned to a commit"],
  ["R21", "S9", "project variable OPS_CAPTAIN_LOGIN is set"],
];

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

export function secretWorkflows(files) {
  return files.filter((f) => /\$\{\{\s*secrets\.(?!GITHUB_TOKEN\b)\w+/.test(f.text)).map((f) => f.name);
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
    set("R10", h.secrets.missing?.some((n) => n !== "SLACK_WEBHOOK_URL") ? "FAIL" : "PASS", `inbox secrets present ${h.secrets.present} of ${h.secrets.total}`, "set DISPATCH_APP_PRIVATE_KEY and WEBHOOK_SECRET on the inbox (S5, S6)");
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
    const secret = ctx.env.WEBHOOK_SECRET;
    if (!secret) throw new Error("WEBHOOK_SECRET is not in the environment; run through your secrets wrapper");
    const id = `readback-selftest-${ctx.now().toString(36)}`;
    const event = JSON.stringify({ specversion: "1.0", id, source: "urn:ops-inbox:readback", type: "ops.inbox.selftest", subject: `selftest/${id}`, time: new Date(ctx.now()).toISOString(), dataschema: `${SCHEMA_BASE}/ops.inbox.selftest.json`, data: { v: 1, project } });
    const ts = String(Math.floor(ctx.now() / 1000));
    const res = await ctx.fetch(inbox, { method: "POST", headers: { "content-type": "application/cloudevents+json", "webhook-id": `msg_${id}`, "webhook-timestamp": ts, "webhook-signature": signBody({ secret, id: `msg_${id}`, timestamp: ts, body: event }) }, body: event });
    const out = await res.json().catch(() => ({}));
    set("R11", res.status === 200 ? "PASS" : "FAIL", `signed POST answered ${res.status}${out.error ? ` (${out.error})` : ""}`, res.status === 401 ? "WEBHOOK_SECRET differs from the inbox's (S6)" : "read the inbox log, then read back again");
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
    const creation = all.json.find((r) => r.name === JSON.parse(readFileSync(join(SETUP, AGENT_CREATIONS), "utf8")).name);
    if (creation) {
      const live = ctx.ghJson(["api", `repos/${project}/rulesets/${creation.id}`]);
      const why = live.ok ? rulesetMatches(JSON.parse(readFileSync(join(SETUP, AGENT_CREATIONS), "utf8")), live.json) : live.err;
      return set("R18", why ? "FAIL" : "PASS", why ? `agent-creations ruleset: ${why}` : "agent-creations ruleset matches: the agent can create only ops/** and the state branch", why ? "fix or delete the ruleset (S10)" : null);
    }
    const list = ctx.ghJson(["api", `repos/${project}/contents/.github/workflows`]);
    const names = list.ok ? list.json.filter((f) => /\.ya?ml$/.test(f.name)).map((f) => f.name) : [];
    const files = names.map((name) => {
      const f = ctx.ghJson(["api", `repos/${project}/contents/.github/workflows/${name}`]);
      return { name, text: f.ok ? Buffer.from(f.json.content ?? "", "base64").toString("utf8") : "" };
    });
    const holding = secretWorkflows(files);
    const seen = `workflows using a secret besides GITHUB_TOKEN: ${holding.length ? holding.join(", ") : "none"}`;
    if (workflowsChecked) return set("R18", "PASS", `Captain checked: no workflow runs with a secret on a push to a non-default branch or a pull request from any author; ${seen}`);
    set("R18", "WAIT", seen, holding.length === 0 ? "no workflow uses a secret: rerun with --workflows-checked" : "read each listed workflow; if none runs with its secret on a push to a non-default branch or a pull request from any author rerun with --workflows-checked, otherwise apply ruleset-agent-creations.json (S10, last line)");
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
    console.error("usage: node readback.mjs --project <owner/name> --trigger <owner/name> --inbox <https://.../inbox> [--slack-link <link>] [--workflows-checked]\nneeds WEBHOOK_SECRET in the environment (use your secrets wrapper)");
    process.exit(2);
  }
  const rows = await readback(makeCtx(), args);
  console.log(render(rows, { banner: `kc-ops-inbox read-back · contract v1 · ${rows.length} rows · ${args.project} · trigger ${args.trigger} · inbox ${args.inbox}` }));
  process.exit(rows.every((r) => r.v === "PASS") ? 0 : 1);
}
