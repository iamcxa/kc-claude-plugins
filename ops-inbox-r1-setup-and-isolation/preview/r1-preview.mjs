#!/usr/bin/env node
// DISPOSABLE preview of r1 (ideation cycle 2): the setup runbook, the read-back script's output,
// the Slack notice per event, and the ops record the Captain reviews in the Draft PR.
// Prints fixed text; calls no network, reads no secret, writes only with `html`.
// node r1-preview.mjs runbook | readback [ok|failed] | slack <state> | record [opened|joined] | html
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const P = "spacedock-dev/subspace-relay";
const T = "spacedock-dev/subspace-relay-ops-trigger";
const SITE = "subspace-relay-ops-inbox";
const INBOX = `https://${SITE}.netlify.app/inbox`;
const RB = "node kc-ops-inbox/bin/readback.mjs";

// [id, owner, what, commands, read-back row ids]
const steps = [
  ["S1", "agent may run", "Create <trigger>, private, holding only ops-event.yml",
    [`gh repo create ${T} --private --add-readme`, `gh api -X PUT repos/${T}/contents/.github/workflows/ops-event.yml -f message="add ops-event" -f content="$(base64 < kc-ops-inbox/trigger/ops-event.yml)"`], "R1 R2"],
  ["S2", "Captain only", "Register the dispatch App (Actions write) and install it on <trigger> only",
    [`open "https://github.com/settings/apps/new?name=relay-ops-dispatch&public=false&webhook_active=false&url=https://github.com/${P}&actions=write"`, `then Install App > Only select repositories > ${T}; note the App ID and installation ID`], "R6 R7"],
  ["S3", "Captain only", "Register the agent App (contents, pull requests write) and install it on <project> only",
    [`open "https://github.com/settings/apps/new?name=relay-ops-agent&public=false&webhook_active=false&url=https://github.com/${P}&contents=write&pull_requests=write"`, `then Install App > Only select repositories > ${P}; note the Client ID`], "R8"],
  ["S4", "Captain only", "Store the two App keys, then delete the downloaded files",
    [`netlify env:set DISPATCH_APP_PRIVATE_KEY --secret --site ${SITE} "$(cat ~/Downloads/relay-ops-dispatch.*.private-key.pem)"`, `gh secret set OPS_AGENT_APP_PRIVATE_KEY -R ${T} < ~/Downloads/relay-ops-agent.*.private-key.pem`], "R9"],
  ["S5", "Captain only", "Create the signing secret; store it in the inbox and in relay's deploy; store the model token",
    [`node kc-ops-inbox/bin/secret-new.mjs | tee >(netlify env:set WEBHOOK_SECRET --secret --site ${SITE}) | netlify env:set RELAY_OPS_INBOX_SECRET --secret --site <relay site> --context deploy-preview`, `claude setup-token, then: gh secret set CLAUDE_CODE_OAUTH_TOKEN -R ${T}`], "R10 R11"],
  ["S6", "Captain only", "Create a Slack incoming webhook for one channel and store its URL",
    [`netlify env:set SLACK_WEBHOOK_URL --secret --site ${SITE}   (paste the URL when asked)`], "R12 R13"],
  ["S7", "agent may run", "Deploy the inbox and set its non-secret settings and <trigger>'s variables (needs S2's and S3's ids)",
    [`netlify sites:create --name ${SITE} && netlify deploy --prod --site ${SITE} --dir kc-ops-inbox/site --functions kc-ops-inbox/site/functions`,
     `netlify env:set OPS_TRIGGER_REPO ${T} --site ${SITE}   (also OPS_WORKFLOW, DISPATCH_APP_ID, DISPATCH_INSTALLATION_ID)`,
     `gh variable set OPS_PROJECT_REPO -R ${T} --body ${P}; gh variable set OPS_AGENT_APP_CLIENT_ID -R ${T} --body <S3 Client ID>`], "R3 R4"],
  ["S8", "agent may run", "Create spacedock-state/ops in <project> and open the setup Draft PR (ops-gate.yml, docs/ops/README.md)",
    [`gh api -X POST repos/${P}/git/refs -f ref=refs/heads/spacedock-state/ops -f sha=<root commit printed by kc-ops-inbox/bin/state-root.mjs>`,
     `gh pr create -R ${P} --draft --head ops-inbox-setup --title "chore(ops): connect the ops inbox" --body-file kc-ops-inbox/setup/setup-pr.md`], "R5"],
  ["S9", "Captain only", "Apply the five rulesets; agent-creations lets only the repository admin role and the listed release bot create branches outside ops/** and spacedock-state/ops, the other four have an empty bypass list",
    [`for f in main ops-branches state-branch agent-creations; do gh api -X POST repos/${P}/rulesets --input kc-ops-inbox/setup/ruleset-$f.json; done`,
     `gh api -X POST repos/${T}/rulesets --input kc-ops-inbox/setup/ruleset-trigger-main.json`], "R14"],
  ["S10", "Captain only", "Review and merge the setup PR, so ops-gate.yml is on the default branch", [`gh pr view ops-inbox-setup -R ${P} --web`], "R15"],
  ["S11", "anyone", "Read every step back (sends one signed self-test event; the secret comes from your secrets wrapper)",
    [`<wrapper> ${RB} --project ${P} --trigger ${T} --inbox ${INBOX} [--slack-link <link>]`], "all"],
];

function runbook() {
  const out = ["# Connect a project to its ops inbox (runbook, r1)", "",
    `Project <project> = ${P} · trigger repository <trigger> = ${T} · inbox <inbox> = ${INBOX}`,
    "Run the steps in order. \"Captain only\" steps touch an App, a key, a secret, a webhook or a ruleset; nobody else runs them.",
    "Each step names the read-back rows (R1 to R15) that prove it; S11 runs them all.", ""];
  for (const [id, who, what, cmds, rb] of steps) {
    out.push(`## ${id} · ${who} · ${what}`, "");
    for (const c of cmds) out.push(`    ${c}`);
    out.push("", `Read back by: ${rb === "all" ? "every row" : rb}`, "");
  }
  return out.join("\n");
}

const rows = [
  ["R1", "S1", "trigger repository is private", "gh api repos/<trigger>", "private: true"],
  ["R2", "S1", "trigger repository holds 1 workflow, 1 branch", "gh api repos/<trigger>/actions/workflows", "1 workflow, 1 branch"],
  ["R3", "S7", "inbox answers with contract v1, 4 of 4 settings", "GET <inbox>/health", "contract v1, 4 of 4"],
  ["R4", "S7", "trigger variables set", "gh variable list -R <trigger>", "2 of 2"],
  ["R5", "S8", "state branch spacedock-state/ops exists", "gh api repos/<project>/branches/spacedock-state%2Fops", "present"],
  ["R6", "S2", "dispatch token: actions write on <trigger> only", "self-test: inbox mint response", "actions:write, 1 repository"],
  ["R7", "S2", "dispatch App cannot reach <project>", "self-test: mint for <project>", "refused (422), as required"],
  ["R8", "S3", "agent token: contents and PR write on <project> only", "self-test run: create-github-app-token", "2 permissions, 1 repository"],
  ["R9", "S4", "both App keys stored (names only)", "gh secret list -R <trigger>; <inbox>/health", "2 of 2"],
  ["R10", "S5", "signing secret matches the inbox", "self-test: signed POST <inbox>", "accepted (202)"],
  ["R11", "S5", "model token stored (name only)", "gh secret list -R <trigger>", "present"],
  ["R12", "S6", "Slack webhook accepted the self-test notice", "self-test: webhook reply", "ok"],
  ["R13", "S6", "self-test notice seen in the channel", "Captain: --slack-link <link>", "posted 10:42:07Z"],
  ["R14", "S9", "5 rulesets match the files and their bypass lists","gh api repos/<project|trigger>/rulesets", "5 of 5"],
  ["R15", "S10", "ops-gate.yml is on the default branch", "gh api repos/<project>/contents/.github/workflows/ops-gate.yml", "present"],
].map(([id, step, what, by, obs]) => ({ id, step, v: "PASS", what, by, obs }));

function readback(scenario = "ok") {
  const out = [`$ <wrapper> ${RB} --project ${P} --trigger ${T} --inbox ${INBOX}` + (scenario === "ok" ? " --slack-link https://example.slack.com/archives/C0EXAMPLE/p1792665727000100" : ""),
    `kc-ops-inbox read-back · contract v1 · 15 rows · reads only, plus one signed self-test event`, ""];
  const r = rows.map((x) => ({ ...x }));
  if (scenario === "failed") {
    Object.assign(r[13], { v: "FAIL", obs: "agent-creations ruleset missing (4 of 5)", next: "run S9 again for ruleset-agent-creations.json, then read back again" });
    Object.assign(r[2], { v: "ERROR", obs: "could not read: <inbox> did not answer in 10 s", next: "check the inbox is deployed (S7), then read back again" });
    Object.assign(r[12], { v: "WAIT", obs: "no message link given", next: "open the self-test notice in Slack, Copy link, rerun with --slack-link <link>" });
  }
  out.push(`  ${"row".padEnd(4)}  ${"step".padEnd(4)}  ${"verdict".padEnd(7)}  ${"what is read back".padEnd(52)}  ${"read by".padEnd(60)}  observed`);
  for (const x of r) {
    out.push(`  ${x.id.padEnd(4)}  ${x.step.padEnd(4)}  ${x.v.padEnd(7)}  ${x.what.padEnd(52)}  ${x.by.padEnd(60)}  ${x.obs}`);
    if (x.next) out.push(`  ${"".padEnd(4)}  ${"".padEnd(4)}  ${"".padEnd(7)}  next: ${x.next}`);
  }
  out.push("", "PASS read back as set · FAIL read back but wrong · ERROR could not be read · WAIT needs the Captain");
  const n = (v) => r.filter((x) => x.v === v).length;
  out.push("", `${n("PASS")} PASS, ${n("FAIL")} FAIL, ${n("ERROR")} ERROR, ${n("WAIT")} WAIT of ${r.length}.`);
  out.push(r.some((x) => x.v !== "PASS") ? "The project is not connected. Exit 1." : "Connected: a signed event can reach Slack and wake only this project's ops workflow. Exit 0.");
  return out.join("\n");
}

const near = { head: "relay · signed-in ceiling near", body: "120 of 150 signed-in publishes today (limit source: default)" };
const full = { head: "relay · signed-in ceiling full", body: "150 of 150 signed-in publishes today (limit source: default)" };
const inc = "ceiling/bound/2026-10-20";
const runLink = (n, label) => `<https://github.com/${T}/actions/runs/${n}|${label}>`;
const slackStates = {
  opened: { ...near, agent: `:white_check_mark: New incident \`${inc}\` · agent started · ${runLink(39750507891, "ops run")}; its Draft PR links from the run`, id: "bound-2026-10-20-80" },
  joined: { ...full, agent: `:heavy_plus_sign: Joins incident \`${inc}\` (event 2) · recorded on its ops task, no new agent run · ${runLink(39750507891, "first run")}`, id: "bound-2026-10-20-100" },
  other: { head: "relay · anonymous ceiling full", body: "50 of 50 anonymous publishes today (limit source: RELAY_ANON_SITE_DAILY_BRIEFING_LIMIT)",
    agent: `:white_check_mark: New incident \`ceiling/anonymous/2026-10-20\` · agent started · ${runLink(39750512210, "ops run")}; its Draft PR links from the run`, id: "anon-2026-10-20-100" },
  refused: { ...near, agent: ":warning: Needs action · agent NOT started: GitHub refused the dispatch (HTTP 403). Run the read-back (S11); the sender's next retry can still start it.", id: "bound-2026-10-20-80" },
  uncertain: { ...near, agent: `:question: Needs a look · agent start UNCERTAIN: GitHub did not answer in 10 s, and the inbox will not resend this event. <https://github.com/${T}/actions|Check the runs>`, id: "bound-2026-10-20-80" },
  selftest: { head: `Read-back self-test · ${P}`, body: "Signature verified; the dispatch App reaches only the trigger repository.",
    agent: `:white_check_mark: ${runLink(39750511120, "Self-test run")} started; no task is filed. Captain: paste this message's link into the read-back.`, id: "readback-selftest-7f3a91c2", source: "urn:ops-inbox:readback" },
  escaped: { head: "sentry-shaped · error", body: "TypeError: <!channel> total is undefined · checkout/pay",
    agent: `:white_check_mark: New incident \`issue/4501\` · agent started · ${runLink(39750509002, "ops run")}; its Draft PR links from the run`, id: "e1a2b3c4", source: "urn:sentry:example" },
};
const slackEscape = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function slackPayload(state) {
  const s = slackStates[state];
  const ctx = `event ${s.id} · source ${s.source || "https://<relay deploy>/ops"} · contract v1`;
  return { text: `${slackEscape(s.head)}: ${slackEscape(s.body)}`, blocks: [
    { type: "section", text: { type: "mrkdwn", text: `*${slackEscape(s.head)}*\n${slackEscape(s.body)}` } },
    { type: "section", text: { type: "mrkdwn", text: s.agent } },
    { type: "context", elements: [{ type: "mrkdwn", text: slackEscape(ctx) }] }] };
}

// Reference blocks: real paths and digests, read-only from relay's clone at origin/main 485306242b80 (probe P5, 2026-10-23).
const C = "485306242b806b0bbeea8fc1ff0abfe6568de959";
const cites = [
  ["0060", "docs/adr/0060-the-signed-in-tier-has-its-own-exact-site-wide-daily-ceiling.md", "bd63ef2d6aa7e58a9ee87dc73a5d7fa85f69e4ac96298ebd3be7c7824c33d5a3"],
  ["0049", "docs/adr/0049-refusals-are-counted-from-log-lines-and-never-stored.md", "7fdadd7f72315258236532df243f6567e7ac1b785454feb08d9461962779ba61"],
  ["0001", "docs/adr/0001-no-upper-bound-on-daily-quota-overrides.md", "c4f794037330a48808cd74e6602705f0213de5421e2d87d0ec6609054ce2bcf0"],
];
function record(mode = "opened") {
  const out = [`# ops: relay signed-in ceiling, 2026-10-20`, "",
    `Incident \`${inc}\` · source https://<relay deploy>/ops · contract v1 · ops task \`${inc.replace(/\//g, "-")}\` on spacedock-state/ops`, "",
    "## Events", "", "| # | received | event id | what | fields |", "| - | - | - | - | - |",
    "| 1 | 08:48:03Z | bound-2026-10-20-80 | bound-ceiling-near | count 120 · limit 150 · limitSource default |", "",
    "## Diagnosis", "",
    "- Known: 120 of 150 signed-in publishes by 08:48 UTC; no override record today, so the default 150 applies.",
    "- Not known: who is publishing; relay telemetry carries no account identifier [ADR 0049]. Whether the rate continues.", "",
    "## Options", "",
    "1. **Hold.** At 150 the ceiling refuses with 429 until 00:00 UTC; a refused publish spends nothing [ADR 0060]. Cost: signed-in publishers refused for the rest of the day.",
    "2. **Raise today's limit to 300.** You run `scripts/bound-ceiling --production --limit 300 --reason \"<why>\"`; it lapses at midnight, at most 1000 [ADR 0060]. The agent holds no store credential. Cost: up to 150 more Briefings' credits.",
    "3. **Change the default.** A code change to `RELAY_BOUND_SITE_DAILY_BRIEFING_LIMIT` goes to a dev task, not this ops task; adding a silent ceiling elsewhere needs a new ruling [ADR 0001].", "",
    "## Recommendation", "", "Option 1, hold: 120 by 08:48 is the first near event, and a raise can follow the full event within seconds.", "",
    "## Rulings cited", "", "Read per kc-adr read-adr, step 1, at the commit this run checked out. Each block passed the citation check.", "",
    ...cites.flatMap(([n, p, d]) => [`- relay ADR ${n} · OK`, `  - repo: ${P}`, `  - path: ${p}`, `  - commit: ${C}`, `  - digest: sha256:${d}`, `  - status: Accepted`]), "",
    "## Measures", "", "- Event received 08:48:03Z · recommendation ready (Draft PR opened) 08:50:31Z · 2 min 28 s",
    "- Your decision: filled in by ops-gate from your review (followed the recommendation: yes or no)"];
  if (mode === "joined") out.push("", "---", "", "**Comment by relay-ops-agent[bot], 11:02:40Z**", "",
    "Event 2 joined this incident: `bound-2026-10-20-100` · bound-ceiling-full · count 150 · limit 150. It is recorded on the ops task (`events/bound-2026-10-20-100.json`).",
    "The recommendation above was written before this event; r1 runs no new agent for a joined event.");
  return out.join("\n");
}

const GLYPH = { ":white_check_mark:": "✅", ":warning:": "⚠️", ":question:": "❓", ":heavy_plus_sign:": "➕" };
const esc = (t) => t.replace(/&(?!lt;|gt;|amp;)/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const mrk = (t) => esc(t).replace(/&lt;[^|&]+\|([^&]+)&gt;/g, "<u>$1</u>").replace(/`([^`]+)`/g, "<code>$1</code>").replace(/:[a-z_]+:/g, (g) => GLYPH[g] || g);
function slackCard(state, theme, ts) {
  const p = slackPayload(state);
  const [h, b] = p.blocks[0].text.text.replace(/^\*/, "").split("*\n");
  const warn = state === "refused" || state === "uncertain" ? " warn" : "";
  return `<div class="msg ${theme}"><div class="avatar">OI</div><div class="col">
<div class="who"><b>ops-inbox</b> <span class="app">APP</span> <span class="ts">${ts || "08:48"}</span></div>
<div class="h">${h}</div><div>${b}</div><div class="agent${warn}">${mrk(p.blocks[1].text.text)}</div>
<div class="ctx">${p.blocks[2].elements[0].text}</div></div></div>`;
}
function md(text) { // tiny renderer for the record preview: headings, tables, lists, bold, code
  const lines = text.split("\n"); const out = []; let table = null, list = false;
  const inl = (t) => esc(t).replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\[ADR (\d{4})\]/g, '<span class="cite">ADR $1</span>');
  const flush = () => { if (table) { out.push(`<table>${table.join("")}</table>`); table = null; } if (list) { out.push("</ul>"); list = false; } };
  for (const l of lines) {
    if (l.startsWith("|")) { if (/^\| -/.test(l)) continue; const cells = l.split("|").slice(1, -1).map((c) => inl(c.trim()));
      if (!table) { flush(); table = [`<tr>${cells.map((c) => `<th>${c}</th>`).join("")}</tr>`]; } else table.push(`<tr>${cells.map((c) => `<td>${c}</td>`).join("")}</tr>`); continue; }
    if (/^\s*(-|\d+\.) /.test(l)) { if (table) flush(); if (!list) { out.push("<ul>"); list = true; } const sub = /^\s{2}/.test(l);
      out.push(`<li class="${sub ? "sub" : ""}">${inl(l.replace(/^\s*(-|\d+\.) /, (m, g) => (/\d/.test(g) ? g + " " : "")))}</li>`); continue; }
    flush();
    if (l.startsWith("# ")) out.push(`<h1>${inl(l.slice(2))}</h1>`); else if (l.startsWith("## ")) out.push(`<h3>${inl(l.slice(3))}</h3>`);
    else if (l === "---") out.push('<hr>'); else if (l.trim()) out.push(`<p>${inl(l)}</p>`);
  }
  flush(); return out.join("\n");
}

function writeHtml(dir) {
  const css = `body{font-family:-apple-system,Helvetica,Arial,sans-serif;margin:16px;background:#f3f3f3}
h2{font-size:15px;margin:18px 0 6px}.note{font-size:12px;color:#444;margin:0 0 6px;max-width:720px}
.msg{display:flex;gap:10px;padding:10px 14px;border-radius:6px;margin:6px 0;font-size:15px;line-height:1.4;max-width:720px}
.msg.light{background:#fff;color:#1d1c1d}.msg.dark{background:#1a1d21;color:#d1d2d3}
.avatar{width:36px;height:36px;border-radius:6px;background:#4a154b;color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;flex:none}
.col{min-width:0;overflow-wrap:anywhere}.app{font-size:10px;background:#ddd;color:#555;padding:1px 3px;border-radius:2px}
.dark .app{background:#333;color:#aaa}.ts{font-size:12px;color:#616061}.h{font-weight:700}
.agent{margin-top:4px}.agent.warn{border-left:3px solid #e8912d;padding-left:6px}.agent u{color:#1264a3;text-decoration:none}.dark .agent u{color:#1d9bd1}
.agent code{font-size:13px;background:#f6f6f6;border:1px solid #ddd;border-radius:3px;padding:0 3px;color:#c01343}.dark .agent code{background:#222529;border-color:#444;color:#e8a6b6}
.ctx{font-size:12px;color:#616061;margin-top:4px}.dark .ctx{color:#ababad}
.phone .msg{max-width:358px}pre{background:#0d1117;color:#e6edf3;padding:12px;font-size:12px;border-radius:6px;white-space:pre-wrap;word-break:break-all;max-width:1340px}
.gh{background:#fff;color:#1f2328;border:1px solid #d0d7de;border-radius:6px;padding:16px 24px;max-width:860px;font-size:14px;line-height:1.5}
.gh.dark{background:#0d1117;color:#e6edf3;border-color:#30363d}.gh h1{font-size:22px;border-bottom:1px solid #d0d7de;padding-bottom:6px}.gh.dark h1{border-color:#30363d}
.gh h3{font-size:16px;margin:18px 0 6px}.gh table{border-collapse:collapse}.gh td,.gh th{border:1px solid #d0d7de;padding:4px 8px;font-size:13px}.gh.dark td,.gh.dark th{border-color:#30363d}
.gh code{background:rgba(175,184,193,.2);padding:0 4px;border-radius:4px;font-size:12px}.gh ul{padding-left:20px}.gh li.sub{list-style:circle;margin-left:18px;font-size:12px}
.cite{background:#ddf4ff;color:#0969da;border-radius:10px;padding:0 6px;font-size:12px;white-space:nowrap}.gh.dark .cite{background:#121d2f;color:#4493f8}
.gh.phone{max-width:358px;padding:12px}.gh hr{border:0;border-top:1px solid #d0d7de}`;
  const slack = `<!doctype html><meta charset="utf-8"><title>Slack notice preview, r1 cycle 2</title><style>${css}</style>
<h2>Slack notice, proposed (DISPOSABLE mock drawn locally; Slack draws the real one from the Block Kit payload)</h2>
<p class="note">One notice per accepted event and outcome. A resent event (same source and id) posts nothing. The first event of an incident (same source and subject) says "New incident" and starts the agent; a later one says "Joins incident" and starts no agent. Event text is escaped: "&lt;!channel&gt;" below is plain text, not a mention. Field text is cut at 200 characters.</p>
<h2>Light theme, desktop width: one day's channel in order (new incident, its later event, another incident), then NOT started, UNCERTAIN, read-back self-test, escaped mention</h2>
${slackCard("opened", "light", "08:48")}${slackCard("joined", "light", "11:02")}${slackCard("other", "light", "14:20")}
${["refused", "uncertain", "selftest", "escaped"].map((s) => slackCard(s, "light")).join("\n")}
<h2>Dark theme</h2>${slackCard("opened", "dark", "08:48")}${slackCard("joined", "dark", "11:02")}${slackCard("uncertain", "dark")}
<h2>Phone width (390 px)</h2><div class="phone">${slackCard("opened", "light", "08:48")}${slackCard("joined", "light", "11:02")}${slackCard("refused", "light")}</div>`;
  writeFileSync(join(dir, "slack.html"), slack);
  const term = `<!doctype html><meta charset="utf-8"><title>Runbook and read-back preview, r1 cycle 2</title><style>${css}</style>
<h2>Setup runbook (DISPOSABLE; the written runbook replaces the setup command; printed by r1-preview.mjs runbook)</h2><pre>${esc(runbook())}</pre>
<h2>Read-back, every row PASS</h2><pre>${esc(readback("ok"))}</pre>
<h2>Read-back, one FAIL, one ERROR and the Slack row waiting</h2><pre>${esc(readback("failed"))}</pre>`;
  writeFileSync(join(dir, "terminal.html"), term);
  const rec = `<!doctype html><meta charset="utf-8"><title>Ops record preview, r1 cycle 2</title><style>${css}</style>
<h2>The ops record docs/ops/&lt;incident&gt;.md as the Captain reads it in the Draft PR (DISPOSABLE; GitHub draws the real one)</h2>
<p class="note">Light, desktop: the record when the PR opens. Below it: the same PR after a later event joined (the record is unchanged; the event arrives as a comment and on the task). Then dark, and phone width.</p>
<div class="gh">${md(record("opened"))}</div><h2>After a later event joined (light, desktop)</h2><div class="gh">${md(record("joined"))}</div>
<h2>Dark theme</h2><div class="gh dark">${md(record("opened"))}</div><h2>Phone width (390 px)</h2><div class="gh phone">${md(record("joined"))}</div>`;
  writeFileSync(join(dir, "record.html"), rec);
  return `wrote slack.html, terminal.html and record.html in ${dir}`;
}

const [mode = "runbook", arg] = process.argv.slice(2);
const here = dirname(fileURLToPath(import.meta.url));
const run = { runbook, readback: () => readback(arg), record: () => record(arg), html: () => writeHtml(here),
  slack: () => slackStates[arg || "opened"] ? JSON.stringify(slackPayload(arg || "opened"), null, 2) : null }[mode];
const text = run && run();
if (!text) { console.error("usage: r1-preview.mjs runbook | readback [ok|failed] | slack <state> | record [opened|joined] | html"); process.exit(2); }
console.log(text);
const code = /Exit (\d)\.$/.exec(text);
process.exit(code ? Number(code[1]) : 0);
