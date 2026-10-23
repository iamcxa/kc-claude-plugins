#!/usr/bin/env node
// DISPOSABLE preview of r1 (ideation cycle 2): the setup runbook, the read-back script's output,
// the Slack notice per event, and the ops record the Captain reviews in the Draft PR.
// Prints fixed text; calls no network, reads no secret, writes only with `html`.
// node r1-preview.mjs runbook | readback [ok|waiting|failed] | slack <state> | record [opened|joined|refused] | html
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const P = "spacedock-dev/subspace-relay";
const T = "spacedock-dev/subspace-relay-ops-trigger";
const SITE = "subspace-relay-ops-inbox";
const INBOX = `https://${SITE}.netlify.app/inbox`;
const RB = "node kc-ops-inbox/bin/readback.mjs";

// [id, owner, short action, explanation or null, commands, read-back row ids]
const steps = [
  ["S1", "agent may run", "Create the trigger repository", "Private, holding only ops-event.yml.",
    [`gh repo create ${T} --private --add-readme`,
     `gh api -X PUT repos/${T}/contents/.github/workflows/ops-event.yml -f message="add ops-event" -f content="$(base64 < kc-ops-inbox/trigger/ops-event.yml)"`], "R1 R2"],
  ["S2", "agent may run", "Create the inbox site and link this folder to it", null,
    [`netlify sites:create --name ${SITE}`, `netlify link --name ${SITE}`], "R3"],
  ["S3", "Captain only", "Register the dispatch App (in the browser)", "Actions write only; install it on <trigger> only. Prints: App ID, installation ID.",
    [`open "https://github.com/settings/apps/new?name=relay-ops-dispatch&public=false&webhook_active=false&url=https://github.com/${P}&actions=write"`,
     `on the page: Create GitHub App > Generate a private key > Install App > Only select repositories > ${T} > Install`], "R7 R8"],
  ["S4", "Captain only", "Register the agent App (in the browser)", "Contents and pull requests write; install it on <project> only. Prints: Client ID.",
    [`open "https://github.com/settings/apps/new?name=relay-ops-agent&public=false&webhook_active=false&url=https://github.com/${P}&contents=write&pull_requests=write"`,
     `on the page: Create GitHub App > Generate a private key > Install App > Only select repositories > ${P} > Install`], "R9"],
  ["S5", "Captain only", "Store the two App keys", "Then delete the two downloaded files.",
    [`netlify env:set DISPATCH_APP_PRIVATE_KEY "$(cat ~/Downloads/relay-ops-dispatch.*.private-key.pem)" --secret`,
     `gh secret set OPS_AGENT_APP_PRIVATE_KEY -R ${T} < ~/Downloads/relay-ops-agent.*.private-key.pem`], "R10"],
  ["S6", "Captain only", "Create and store the signing secret and the model token", "The signing secret goes to the inbox and to relay's deploy previews only.",
    [`V=$(node kc-ops-inbox/bin/secret-new.mjs)`,
     `netlify env:set WEBHOOK_SECRET "$V" --secret`,
     `(cd <relay checkout> && netlify env:set RELAY_OPS_INBOX_SECRET "$V" --secret --context deploy-preview); unset V`,
     `claude setup-token`,
     `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R ${T}   # paste the token setup-token printed; gh reads it from standard input`], "R11 R12"],
  ["S7", "Captain only", "Store the Slack webhook", "Create an incoming webhook for one channel in Slack first. R14, seeing the notice in the channel, is proven in S12.",
    [`read -rs V   # paste the webhook URL; it stays out of shell history`, `netlify env:set SLACK_WEBHOOK_URL "$V" --secret; unset V`], "R13"],
  ["S8", "agent may run", "Deploy the inbox and set its settings", "Needs S3's App ID and installation ID and S4's Client ID.",
    [`netlify deploy --prod --site ${SITE} --dir kc-ops-inbox/site --functions kc-ops-inbox/site/functions`,
     `netlify env:set OPS_TRIGGER_REPO ${T}`, `netlify env:set OPS_WORKFLOW ops-event.yml`,
     `netlify env:set DISPATCH_APP_ID <S3 App ID>`, `netlify env:set DISPATCH_INSTALLATION_ID <S3 installation ID>`,
     `gh variable set OPS_PROJECT_REPO -R ${T} --body ${P}`, `gh variable set OPS_AGENT_APP_CLIENT_ID -R ${T} --body <S4 Client ID>`], "R4 R5"],
  ["S9", "agent may run", "Create the state branch and open the setup Draft PR", "The PR adds ops-gate.yml and docs/ops/README.md.",
    [`gh api -X POST repos/${P}/git/refs -f ref=refs/heads/spacedock-state/ops -f sha=$(node kc-ops-inbox/bin/state-root.mjs --project ${P})`,
     `gh pr create -R ${P} --draft --head ops-inbox-setup --title "chore(ops): connect the ops inbox" --body-file kc-ops-inbox/setup/setup-pr.md`], "R6"],
  ["S10", "Captain only", "Apply the five rulesets, one command each", "agent-creations: only ops/** and spacedock-state/ops may be created, except by the repository admin role and the release bot listed in the file. The other four have an empty bypass list. Rerun only the line a read-back row names.",
    [`gh api -X POST repos/${P}/rulesets --input kc-ops-inbox/setup/ruleset-main.json`,
     `gh api -X POST repos/${P}/rulesets --input kc-ops-inbox/setup/ruleset-ops-branches.json`,
     `gh api -X POST repos/${P}/rulesets --input kc-ops-inbox/setup/ruleset-state-branch.json`,
     `gh api -X POST repos/${P}/rulesets --input kc-ops-inbox/setup/ruleset-agent-creations.json`,
     `gh api -X POST repos/${T}/rulesets --input kc-ops-inbox/setup/ruleset-trigger-main.json`], "R15 R16 R17 R18 R19"],
  ["S11", "Captain only", "Merge the setup PR", "So ops-gate.yml is on the default branch before any ops PR opens.", [`gh pr merge ops-inbox-setup -R ${P} --squash`], "R20"],
  ["S12", "anyone", "Read every step back", "Reads with your gh and netlify logins and sends one signed self-test event. The first run always waits on R14: open the self-test notice in Slack, Copy link, and run the same command again with --slack-link <link>.",
    [`<wrapper> ${RB} --project ${P} --trigger ${T} --inbox ${INBOX} [--slack-link <link>]`], "all"],
];

function runbook() {
  const out = ["# Connect a project to its ops inbox (runbook, r1)", "",
    `<project>        ${P}`, `<trigger>        ${T}`, `<inbox>          ${INBOX}  (site ${SITE}; netlify commands run in the folder S2 linked)`,
    `<relay checkout> your local clone of ${P}, linked to relay's Netlify site`,
    `<wrapper>        your secrets wrapper, which puts WEBHOOK_SECRET in the read-back's environment without printing it`, "",
    "Run the steps in order. \"Captain only\" steps touch an App, a key, a secret, a webhook or a ruleset; nobody else runs them.",
    "Each step names the read-back rows that prove it; S12 runs them all.", ""];
  for (const [id, who, what, why, cmds, rb] of steps) {
    out.push(`## ${id} · ${who.toUpperCase()} · ${what}`);
    if (why) out.push(why);
    out.push("");
    for (const c of cmds) out.push(`    ${c}`);
    out.push("", `Read back by: ${rb === "all" ? "every row" : rb}`, "");
  }
  return out.join("\n");
}

const rows = [
  ["R1", "S1", "trigger repository is private", "gh api repos/<trigger>", "private: true"],
  ["R2", "S1", "trigger repository holds 1 workflow, 1 branch", "gh api repos/<trigger>/actions/workflows", "1 workflow, 1 branch"],
  ["R3", "S2", "inbox site exists and this folder is linked to it", "netlify status", "linked"],
  ["R4", "S8", "inbox answers with contract v1, 4 of 4 settings", "GET <inbox>/health", "contract v1, 4 of 4"],
  ["R5", "S8", "trigger variables set", "gh variable list -R <trigger>", "2 of 2"],
  ["R6", "S9", "state branch spacedock-state/ops exists", "gh api repos/<project>/branches/spacedock-state%2Fops", "present"],
  ["R7", "S3", "dispatch token: actions write on <trigger> only", "self-test: inbox mint response", "actions:write, 1 repository"],
  ["R8", "S3", "dispatch App cannot reach <project>", "self-test: mint for <project>", "refused (422), as required"],
  ["R9", "S4", "agent token: contents and PR write on <project> only", "self-test run: create-github-app-token", "2 permissions, 1 repository"],
  ["R10", "S5", "both App keys stored (names only)", "gh secret list -R <trigger>; <inbox>/health", "2 of 2"],
  ["R11", "S6", "signing secret matches the inbox", "self-test: signed POST <inbox>", "accepted (202)"],
  ["R12", "S6", "model token stored (name only)", "gh secret list -R <trigger>", "present"],
  ["R13", "S7", "Slack webhook accepted the self-test notice", "self-test: webhook reply", "ok"],
  ["R14", "S12", "self-test notice seen in the channel", "Captain: --slack-link <link>", "posted 10:42:07Z"],
  ["R15", "S10", "ruleset main matches its file, no bypass", "gh api repos/<project>/rulesets", "match"],
  ["R16", "S10", "ruleset ops-branches matches its file, no bypass", "gh api repos/<project>/rulesets", "match"],
  ["R17", "S10", "ruleset state-branch matches its file, no bypass", "gh api repos/<project>/rulesets", "match"],
  ["R18", "S10", "ruleset agent-creations matches its file and bypass list", "gh api repos/<project>/rulesets", "match"],
  ["R19", "S10", "ruleset trigger-main matches its file, no bypass", "gh api repos/<trigger>/rulesets", "match"],
  ["R20", "S11", "ops-gate.yml is on the default branch", "gh api repos/<project>/contents/.github/workflows/ops-gate.yml", "present"],
].map(([id, step, what, by, obs]) => ({ id, step, v: "PASS", what, by, obs }));

function readback(scenario = "ok") {
  const out = [`$ <wrapper> ${RB} --project ${P} --trigger ${T} --inbox ${INBOX}` + (scenario === "ok" ? " --slack-link https://example.slack.com/archives/C0EXAMPLE/p1792665727000100" : ""),
    `kc-ops-inbox read-back · contract v1 · ${rows.length} rows · reads only, plus one signed self-test event`, ""];
  const r = rows.map((x) => ({ ...x }));
  const set = (id, o) => Object.assign(r.find((x) => x.id === id), o);
  if (scenario === "failed") {
    set("R18", { v: "FAIL", obs: "ruleset agent-creations not found", next: "run the fourth line of S10 only, then read back again" });
    set("R4", { v: "ERROR", obs: "could not read: <inbox> did not answer in 10 s", next: "check the inbox is deployed (S8), then read back again" });
  }
  if (scenario === "failed" || scenario === "waiting")
    set("R14", { v: "WAIT", obs: "no message link given", next: "open the self-test notice in Slack, Copy link, rerun with --slack-link <link>" });
  out.push(`  ${"".padEnd(1)} ${"row".padEnd(4)}  ${"step".padEnd(4)}  ${"verdict".padEnd(7)}  ${"what is read back".padEnd(56)}  ${"read by".padEnd(60)}  observed`);
  for (const x of r) {
    out.push(`  ${x.v === "PASS" ? " " : ">"} ${x.id.padEnd(4)}  ${x.step.padEnd(4)}  ${x.v.padEnd(7)}  ${x.what.padEnd(56)}  ${x.by.padEnd(60)}  ${x.obs}`);
    if (x.next) out.push(`    ${"".padEnd(4)}  ${"".padEnd(4)}  ${"".padEnd(7)}  next: ${x.next}`);
  }
  const n = (v) => r.filter((x) => x.v === v).length;
  const bad = r.some((x) => x.v !== "PASS");
  out.push("", `${n("PASS")} PASS, ${n("FAIL")} FAIL, ${n("ERROR")} ERROR, ${n("WAIT")} WAIT of ${r.length}` + (bad ? "  (FAIL read back but wrong · ERROR could not read · WAIT needs you)" : ""));
  const onlySlack = bad && r.every((x) => x.v === "PASS" || x.id === "R14");
  out.push(!bad ? "Connected: a signed event can reach Slack and wake only this project's ops workflow. Exit 0."
    : onlySlack ? "Waiting for the Slack link only: rerun with --slack-link <link>. Exit 1." : "The project is not connected. Exit 1.");
  return out.join("\n");
}

const near = { head: "relay · signed-in ceiling near", body: "120 of 150 signed-in publishes today (limit source: default)" };
const full = { head: "relay · signed-in ceiling full", body: "150 of 150 signed-in publishes today (limit source: default)" };
const inc = "ceiling/bound/2026-10-20";
const runLink = (n, label) => `<https://github.com/${T}/actions/runs/${n}|${label}>`;
const longText = ("Error: request to payments provider failed after 3 attempts while confirming order totals for a basket with many items and a discount code applied at checkout, " +
  "then the fallback path also failed because the session store returned an unexpected shape for the stored cart").slice(0, 200) + "…";
const slackStates = {
  opened: { ...near, agent: `:white_check_mark: New incident \`${inc}\` · agent started · ${runLink(39750507891, "run for this incident")}; its Draft PR links from the run`, id: "bound-2026-10-20-80" },
  joined: { ...full, agent: `:link: Joins incident \`${inc}\` (event 2) · recorded on its ops task, no new agent run · ${runLink(39750507891, "run that opened it")}`, id: "bound-2026-10-20-100" },
  other: { head: "relay · anonymous ceiling full", body: "50 of 50 anonymous publishes today (limit source: RELAY_ANON_SITE_DAILY_BRIEFING_LIMIT)",
    agent: `:white_check_mark: New incident \`ceiling/anonymous/2026-10-20\` · agent started · ${runLink(39750512210, "run for this incident")}; its Draft PR links from the run`, id: "anon-2026-10-20-100" },
  refused: { ...near, agent: ":x: Needs action · GitHub refused the dispatch (HTTP 403), so no agent runs for this event. Run the setup read-back. If the sender retries, the retry posts its own notice (below).", id: "bound-2026-10-20-80", bar: "red" },
  retried: { ...near, agent: `:white_check_mark: New incident \`${inc}\` · agent started on the sender's retry · ${runLink(39750519304, "run for this incident")}; its Draft PR links from the run`, id: "bound-2026-10-20-80" },
  uncertain: { ...near, agent: `:question: Needs a look · agent start UNCERTAIN: GitHub did not answer in 10 s, and the inbox will not resend this event. <https://github.com/${T}/actions|open the trigger repository's runs>`, id: "bound-2026-10-20-80", bar: "orange" },
  selftest: { head: `Read-back self-test · ${P}`, body: "Signature verified; the dispatch App reaches only the trigger repository.",
    agent: `:test_tube: ${runLink(39750511120, "Self-test run")} started; no task is filed. Captain: paste this message's link into the read-back.`, id: "readback-selftest-7f3a91c2", source: "urn:ops-inbox:readback" },
  escaped: { head: "sentry-shaped · error", body: "TypeError: <!channel> total is undefined · checkout/pay",
    agent: `:white_check_mark: New incident \`issue/4501\` · agent started · ${runLink(39750509002, "run for this incident")}; its Draft PR links from the run`, id: "e1a2b3c4", source: "urn:sentry:example" },
  long: { head: "sentry-shaped · error", body: longText,
    agent: `:white_check_mark: New incident \`issue/4502\` · agent started · ${runLink(39750509917, "run for this incident")}; its Draft PR links from the run`, id: "e5f6a7b8", source: "urn:sentry:example" },
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
  const refused = mode === "refused";
  const out = [];
  if (mode === "joined") out.push("**PR description, first line (the join run edits it; the record file below does not change):**", "",
    "> Event 2 (bound-ceiling-full, 150 of 150) joined at 11:02:40Z, after this recommendation was written. See the comment at the end.", "", "---", "");
  if (refused) out.push("**PR description, first line:**", "", "> Citations: 2 OK, 1 REFUSED. Do not rely on the refused one.", "", "---", "");
  out.push(`# ops: relay signed-in ceiling, 2026-10-20`, "",
    `Incident \`${inc}\` · source https://<relay deploy>/ops · contract v1 · ops task \`${inc.replace(/\//g, "-")}\` on spacedock-state/ops`, "",
    "## Events", "", "| # | received | event id | what | fields |", "| - | - | - | - | - |",
    "| 1 | 08:48:03Z | `bound-2026-10-20-80` | bound-ceiling-near | count 120; limit 150; limitSource default |", "",
    "## Diagnosis", "",
    "- Known: 120 of 150 signed-in publishes by 08:48 UTC; no override record today, so the default 150 applies.",
    "- Not known: who is publishing; relay telemetry carries no account identifier [ADR 0049]. Whether the rate continues.", "",
    "## Options", "",
    "1. **Hold.** At 150 the ceiling refuses with 429 until 00:00 UTC; a refused publish spends nothing [ADR 0060]. Cost: signed-in publishers refused for the rest of the day.",
    "2. **Raise today's limit to 300.** You run `scripts/bound-ceiling --production --limit 300 --reason \"<why>\"`; it lapses at midnight, at most 1000 [ADR 0060]. The agent holds no store credential. Cost: up to 150 more Briefings' credits.",
    `3. **Change the default.** A code change to \`RELAY_BOUND_SITE_DAILY_BRIEFING_LIMIT\` goes to a dev task, not this ops task; adding a silent ceiling elsewhere needs a new ruling ${refused ? "[ADR 0001 REFUSED]" : "[ADR 0001]"}.`, "",
    "## Recommendation", "", "Option 1, hold: 120 by 08:48 is the first near event, and a raise can follow the full event within seconds.", "",
    "**How to decide:** approve this pull request to accept the recommendation; to choose another option, submit a review with \"Request changes\" or \"Comment\" whose text names the option (for example \"Option 2\"). Your review is the recorded decision; a review that names no single option is recorded with your words and leaves the option open. In r1 nothing runs after it: you carry out the option yourself, and merging keeps this record on the default branch.", "",
    "## Rulings cited", "", `Read by kc-adr read-adr, step 1, in ${P} at commit \`${C}\`. Each block was checked with git and shasum.`, "",
    ...cites.flatMap(([n, p, d], i) => (refused && i === 2)
      ? [`- relay ADR ${n} · **REFUSED: digest-mismatch** (the file at that commit does not have this digest)`, `  - path: ${p}`, `  - digest: sha256:0000000000000000000000000000000000000000000000000000000000000000`]
      : [`- relay ADR ${n} · OK · Accepted`, `  - path: ${p}`, `  - digest: sha256:${d}`]), "",
    "## Measures", "", "- Event received 08:48:03Z · recommendation ready (Draft PR opened) 08:50:31Z · 2 min 28 s",
    "- Your decision: ops-gate records it from your review on the ops task (state branch), not in this file, with followed: yes when you approve, otherwise no");
  if (mode === "joined") out.push("", "---", "", "**Comment by relay-ops-agent[bot], 11:02:40Z**", "",
    "Event 2 joined this incident: `bound-2026-10-20-100` · bound-ceiling-full · count 150; limit 150. It is recorded on the ops task (`events/bound-2026-10-20-100.json`).",
    "The recommendation above was written before this event; r1 runs no new agent for a joined event.");
  return out.join("\n");
}

const GLYPH = { ":white_check_mark:": "✅", ":x:": "❌", ":question:": "❓", ":link:": "🔗", ":test_tube:": "🧪" };
const esc = (t) => t.replace(/&(?!lt;|gt;|amp;)/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const mrk = (t) => esc(t).replace(/&lt;[^|&]+\|([^&]+)&gt;/g, "<u>$1</u>").replace(/`([^`]+)`/g, "<code class=\"nw\">$1</code>").replace(/:[a-z_]+:/g, (g) => GLYPH[g] || g);
function slackCard(state, theme, ts) {
  const p = slackPayload(state);
  const [h, b] = p.blocks[0].text.text.replace(/^\*/, "").split("*\n");
  const warn = slackStates[state].bar ? ` warn ${slackStates[state].bar}` : "";
  return `<div class="msg ${theme}"><div class="avatar">OI</div><div class="col">
<div class="who"><b>ops-inbox</b> <span class="app">APP</span> <span class="ts">${ts || "08:48"}</span></div>
<div class="h">${h}</div><div>${b}</div><div class="agent${warn}">${mrk(p.blocks[1].text.text)}</div>
<div class="ctx">${p.blocks[2].elements[0].text}</div></div></div>`;
}
function md(text) { // tiny renderer for the record preview: headings, tables, lists, bold, code
  const lines = text.split("\n"); const out = []; let table = null, list = false;
  const inl = (t) => esc(t).replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code class=\"nw\">$1</code>").replace(/\[ADR (\d{4})\]/g, '<span class="cite">ADR $1</span>').replace(/\[ADR (\d{4}) REFUSED\]/g, '<span class="cite bad">ADR $1 REFUSED</span>');
  const flush = () => { if (table) { out.push(`<table>${table.join("")}</table>`); table = null; } if (list) { out.push("</ul>"); list = false; } };
  for (const l of lines) {
    if (l.startsWith("|")) { if (/^\| -/.test(l)) continue; const cells = l.split("|").slice(1, -1).map((c) => inl(c.trim()));
      if (!table) { flush(); table = [`<tr>${cells.map((c) => `<th>${c}</th>`).join("")}</tr>`]; } else table.push(`<tr>${cells.map((c) => `<td>${c}</td>`).join("")}</tr>`); continue; }
    if (/^\s*(-|\d+\.) /.test(l)) { if (table) flush(); if (!list) { out.push("<ul>"); list = true; } const sub = /^\s{2}/.test(l);
      out.push(`<li class="${sub ? "sub" : ""}">${inl(l.replace(/^\s*(-|\d+\.) /, (m, g) => (/\d/.test(g) ? g + " " : "")))}</li>`); continue; }
    flush();
    if (l.startsWith("# ")) out.push(`<h1>${inl(l.slice(2))}</h1>`); else if (l.startsWith("## ")) out.push(`<h3>${inl(l.slice(3))}</h3>`);
    else if (l === "---") out.push('<hr>'); else if (l.startsWith("> ")) out.push(`<blockquote>${inl(l.slice(2))}</blockquote>`); else if (l.trim()) out.push(`<p>${inl(l)}</p>`);
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
.agent{margin-top:4px}.agent.warn{border-left:3px solid #e8912d;padding-left:6px}.agent.warn.red{border-left:4px solid #e01e5a}.nw{white-space:nowrap}.agent u{color:#1264a3;text-decoration:none}.dark .agent u{color:#1d9bd1}
.agent code{font-size:13px;background:#f6f6f6;border:1px solid #ddd;border-radius:3px;padding:0 3px;color:#c01343}.dark .agent code{background:#222529;border-color:#444;color:#e8a6b6}
.ctx{font-size:12px;color:#616061;margin-top:4px}.dark .ctx{color:#ababad}
.phone .msg{max-width:358px}pre{background:#0d1117;color:#e6edf3;padding:12px;font-size:12px;border-radius:6px;white-space:pre-wrap;word-break:break-all;max-width:1340px}
.gh{background:#fff;color:#1f2328;border:1px solid #d0d7de;border-radius:6px;padding:16px 24px;max-width:860px;font-size:14px;line-height:1.5}
.gh.dark{background:#0d1117;color:#e6edf3;border-color:#30363d}.gh h1{font-size:22px;border-bottom:1px solid #d0d7de;padding-bottom:6px}.gh.dark h1{border-color:#30363d}
.gh h3{font-size:16px;margin:18px 0 6px}.gh table{border-collapse:collapse}.gh td,.gh th{border:1px solid #d0d7de;padding:4px 8px;font-size:13px}.gh.dark td,.gh.dark th{border-color:#30363d}
.gh code{background:rgba(175,184,193,.2);padding:0 4px;border-radius:4px;font-size:12px}.gh ul{padding-left:20px}.gh li.sub{list-style:circle;margin-left:18px;font-size:12px}
.cite{background:#ddf4ff;color:#0969da;border-radius:10px;padding:0 6px;font-size:12px;white-space:nowrap}.gh.dark .cite{background:#121d2f;color:#4493f8}
.cite.bad{background:#ffebe9;color:#cf222e}.gh.phone{max-width:358px;padding:12px}.gh blockquote{margin:0;padding:6px 12px;border-left:4px solid #bf8700;background:#fff8c5;color:#3b2300}.gh.dark blockquote{background:#272115;color:#e3b341;border-color:#9e6a03}.gh hr{border:0;border-top:1px solid #d0d7de}`;
  const slack = `<!doctype html><meta charset="utf-8"><title>Slack notice preview, r1 cycle 2</title><style>${css}</style>
<h2>Slack notice, proposed (DISPOSABLE mock drawn locally; Slack draws the real one from the Block Kit payload)</h2>
<p class="note">One notice per accepted event and outcome. A resent copy of an accepted event (same source and id) posts nothing; after NOT started the claim is released, so the sender's retry is accepted and posts its own notice. The first event of an incident (same source and subject) says "New incident" and starts the agent; a later one says "Joins incident" and starts no agent. NOT started has a red bar, UNCERTAIN an orange one. The read-back self-test is a fifth kind, posted only by the setup read-back. Event text is escaped: "&lt;!channel&gt;" below is plain text, not a mention. Field text is cut at 200 characters (the last light notice).</p>
<h2>Light theme, desktop width: one day's channel in order (new incident, its later event, another incident), then NOT started and the sender's retry that started it, UNCERTAIN, read-back self-test, escaped mention, field text cut at 200</h2>
${slackCard("opened", "light", "08:48")}${slackCard("joined", "light", "11:02")}${slackCard("other", "light", "14:20")}
${slackCard("refused", "light", "08:48")}${slackCard("retried", "light", "08:49")}${["uncertain", "selftest", "escaped", "long"].map((s) => slackCard(s, "light")).join("\n")}
<h2>Dark theme: every agent-line kind</h2>${slackCard("opened", "dark", "08:48")}${slackCard("joined", "dark", "11:02")}${slackCard("refused", "dark")}${slackCard("uncertain", "dark")}${slackCard("selftest", "dark")}
<h2>Phone width (390 px): every agent-line kind</h2><div class="phone">${slackCard("opened", "light", "08:48")}${slackCard("joined", "light", "11:02")}${slackCard("refused", "light")}${slackCard("uncertain", "light")}${slackCard("selftest", "light")}</div>`;
  writeFileSync(join(dir, "slack.html"), slack);
  const term = `<!doctype html><meta charset="utf-8"><title>Runbook and read-back preview, r1 cycle 2</title><style>${css}</style>
<h2>Setup runbook (DISPOSABLE; the written runbook replaces the setup command; printed by r1-preview.mjs runbook; the real file is Markdown, whose code blocks scroll instead of wrapping)</h2><pre>${esc(runbook())}</pre>
<h2>Read-back, every row PASS</h2><pre>${esc(readback("ok"))}</pre>
<h2>Read-back, first run: only the Slack row waiting</h2><pre>${esc(readback("waiting"))}</pre>
<h2>Read-back, one FAIL, one ERROR and the Slack row waiting (non-passing rows start with &gt;)</h2><pre>${esc(readback("failed"))}</pre>`;
  writeFileSync(join(dir, "terminal.html"), term);
  const rec = `<!doctype html><meta charset="utf-8"><title>Ops record preview, r1 cycle 2</title><style>${css}</style>
<h2>The ops record docs/ops/&lt;incident&gt;.md as the Captain reads it in the Draft PR (DISPOSABLE; GitHub draws the real one)</h2>
<p class="note">Light, desktop: the record when the PR opens. Then the same PR after a later event joined: the record file is unchanged, the PR description's first line says the recommendation predates the event, and the event arrives as a comment and on the task. Then a record with one refused citation, the joined state in dark, and phone width. An event whose agent did not start has no record: its Slack notice is the only trace. An incident holds at most two relay events (80% and full) per tier and day.</p>
<div class="gh">${md(record("opened"))}</div><h2>After a later event joined (light, desktop)</h2><div class="gh">${md(record("joined"))}</div>
<h2>One citation refused by the check (light, desktop)</h2><div class="gh">${md(record("refused"))}</div>
<h2>Dark theme, after a later event joined</h2><div class="gh dark">${md(record("joined"))}</div><h2>Phone width (390 px)</h2><div class="gh phone">${md(record("joined"))}</div>`;
  writeFileSync(join(dir, "record.html"), rec);
  return `wrote slack.html, terminal.html and record.html in ${dir}`;
}

const [mode = "runbook", arg] = process.argv.slice(2);
const here = dirname(fileURLToPath(import.meta.url));
const run = { runbook, readback: () => readback(arg), record: () => record(arg), html: () => writeHtml(here),
  slack: () => slackStates[arg || "opened"] ? JSON.stringify(slackPayload(arg || "opened"), null, 2) : null }[mode];
const text = run && run();
if (!text) { console.error("usage: r1-preview.mjs runbook | readback [ok|waiting|failed] | slack <state> | record [opened|joined|refused] | html"); process.exit(2); }
console.log(text);
const code = /Exit (\d)\.$/.exec(text);
process.exit(code ? Number(code[1]) : 0);
