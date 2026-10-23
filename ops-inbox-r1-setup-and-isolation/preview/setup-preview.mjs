#!/usr/bin/env node
// DISPOSABLE preview of the proposed `ops-inbox setup` output and the Slack notice.
// Prints fixed text for a fictional project; calls no network, reads no secret, writes only with `html`.
// node setup-preview.mjs plan | apply [first|rerun|noyes] | verify [ok|failed|waiting] | slack <state> | html
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const P = "example-owner/mira-shop";
const T = "example-owner/mira-shop-ops-trigger";
const SITE = "mira-shop-ops-inbox";
const INBOX = `https://${SITE}.netlify.app/inbox`;
const head = (cmd) => [`$ ops-inbox setup ${cmd} --project ${P} --host netlify`,
  `kc-ops-inbox setup · contract v1 · <project> ${P} · <trigger> ${T} · <inbox> ${INBOX}`, ""];

const captainSteps = [
  ["C1", "Register the dispatch App and install it on <trigger> only; note its App ID and installation ID",
    [`open "https://github.com/settings/apps/new?name=mira-shop-ops-dispatch&public=false&webhook_active=false&url=https://github.com/${P}&actions=write"`,
     `then Install App > Only select repositories > ${T}`]],
  ["C2", "Register the agent App and install it on <project> only; note its Client ID",
    [`open "https://github.com/settings/apps/new?name=mira-shop-ops-agent&public=false&webhook_active=false&url=https://github.com/${P}&contents=write&pull_requests=write"`,
     `then Install App > Only select repositories > ${P}`]],
  ["C3", "Store the two App keys, then delete the downloaded files",
    [`netlify env:set DISPATCH_APP_PRIVATE_KEY --secret --site ${SITE} "$(cat ~/Downloads/mira-shop-ops-dispatch.*.private-key.pem)"`,
     `gh secret set OPS_AGENT_APP_PRIVATE_KEY -R ${T} < ~/Downloads/mira-shop-ops-agent.*.private-key.pem`]],
  ["C4", "Store the signing secret in the inbox and the producer, and the model token",
    [`ops-inbox secret new | tee >(netlify env:set WEBHOOK_SECRET --secret --site ${SITE}) | <producer's secret-set command>`,
     `claude setup-token, then: gh secret set CLAUDE_CODE_OAUTH_TOKEN -R ${T}`]],
  ["C5", "Create a Slack incoming webhook for one channel and store its URL",
    [`netlify env:set SLACK_WEBHOOK_URL --secret --site ${SITE}   (paste the URL when asked)`]],
  ["C6", "Apply the four rulesets (files written by setup apply)",
    [`gh api -X POST repos/${P}/rulesets --input .ops-inbox/ruleset-main.json`,
     `gh api -X POST repos/${P}/rulesets --input .ops-inbox/ruleset-ops-branches.json`,
     `gh api -X POST repos/${P}/rulesets --input .ops-inbox/ruleset-state-branch.json`,
     `gh api -X POST repos/${T}/rulesets --input .ops-inbox/ruleset-trigger-main.json`]],
  ["C7", "Review and merge the setup PR", [`gh pr view ops-inbox-setup -R ${P} --web`]],
];
const agentSteps = [
  ["A1", "Create <trigger>, private", [`gh repo create ${T} --private --add-readme`]],
  ["A2", "Commit its only workflow", [`gh api -X PUT repos/${T}/contents/.github/workflows/ops-event.yml -f message="add ops-event" -f content=@.ops-inbox/ops-event.yml.b64`]],
  ["A3", "Create the state branch spacedock-state/ops in <project>", [`gh api -X POST repos/${P}/git/refs -f ref=refs/heads/spacedock-state/ops -f sha=<root commit of .ops-inbox/state-root>`]],
  ["A4", "Open the setup Draft PR (ops-gate.yml, docs/ops/README.md)", [`git push origin ops-inbox-setup`, `gh pr create -R ${P} --draft --head ops-inbox-setup --title "chore(ops): connect the ops inbox" --body-file .ops-inbox/setup-pr.md`]],
  ["A5", "Deploy the inbox, set its non-secret settings (needs C1's ids)", [`netlify sites:create --name ${SITE}`, `netlify deploy --prod --site ${SITE} --dir .ops-inbox/site --functions .ops-inbox/site/functions`, `netlify env:set OPS_TRIGGER_REPO ${T} --site ${SITE}   (also OPS_WORKFLOW, OPS_PROJECT_REPO, DISPATCH_APP_ID, DISPATCH_INSTALLATION_ID)`]],
  ["A6", "Set <trigger>'s variables (needs C2's Client ID)", [`gh variable set OPS_PROJECT_REPO -R ${T} --body ${P}`, `gh variable set OPS_AGENT_APP_CLIENT_ID -R ${T} --body <C2 Client ID>`]],
];

function plan() {
  const out = head("plan");
  out.push("1. Captain first, because apply needs their ids:");
  for (const [id, what, cmds] of captainSteps.slice(0, 2)) { out.push(`  ${id}  ${what}`); for (const c of cmds) out.push(`        ${c}`); }
  out.push("", `2. Agent steps, run by: ops-inbox setup apply --yes --dispatch-app-id <C1> --dispatch-installation-id <C1> --agent-client-id <C2>`,
    "   (apply is not interactive: --yes is its confirmation; without it apply prints this list and stops)");
  for (const [id, what, cmds] of agentSteps) { out.push(`  ${id}  ${what}`); for (const c of cmds) out.push(`        ${c}`); }
  out.push("", "3. Captain-only steps (run each yourself; setup never sees a key, secret or webhook URL):");
  for (const [id, what, cmds] of captainSteps.slice(2)) { out.push(`  ${id}  ${what}`); for (const c of cmds) out.push(`        ${c}`); }
  out.push("", "4. ops-inbox setup verify", "", "Nothing was changed. Exit 0.");
  return out.join("\n");
}

function apply(mode = "first") {
  if (mode === "noyes") return [...head("apply"), "Would run A1 A2 A3 A4 A5 A6 (see setup plan). Nothing was changed.",
    "Add --yes to run them. Exit 2."].join("\n");
  const out = head("apply --yes --dispatch-app-id 1408871 --dispatch-installation-id 93120455" + (mode === "rerun" ? " --agent-client-id Iv23liExample" : ""));
  const rows = mode === "rerun"
    ? [["A1", "PASS", "unchanged", "already private"], ["A2", "PASS", "unchanged", "ops-event.yml matches"], ["A3", "PASS", "unchanged", "spacedock-state/ops present"],
       ["A4", "PASS", "unchanged", "Draft PR #12 open"], ["A5", "PASS", "deployed", INBOX], ["A6", "PASS", "set", "2 of 2 variables"]]
    : [["A1", "PASS", "created", "private"], ["A2", "PASS", "committed", "1 workflow"], ["A3", "PASS", "created", "spacedock-state/ops"],
       ["A4", "PASS", "opened", "Draft PR #12"], ["A5", "FAIL", "not deployed", "netlify deploy: 'Not logged in' (run: netlify login)"],
       ["A6", "WAIT", "skipped", "needs --agent-client-id from C2"]];
  out.push(`  step  verdict  action        result`);
  for (const [id, v, did, what] of rows) out.push(`  ${id.padEnd(4)}  ${v.padEnd(7)}  ${did.padEnd(12)}  ${what}`);
  const bad = rows.filter((r) => r[1] !== "PASS").length;
  out.push("", "wrote .ops-inbox/ (the four ruleset files C6 applies, ops-event.yml, setup-pr.md)", `${rows.length - bad} of ${rows.length} agent steps done; a rerun changes only what differs.`);
  if (bad) out.push("next: fix A5's login, finish C2, then rerun the same command with --agent-client-id. Exit 1.");
  else out.push("next: Captain-only steps C3 to C7 (see setup plan), then ops-inbox setup verify. Exit 0.");
  return out.join("\n");
}

const verified = [
  ["A1", "trigger repository is private", "gh api repos/<trigger>", "private: true"],
  ["A2", "trigger repository: 1 workflow, 1 branch", "gh api repos/<trigger>/actions/workflows", "1 workflow, 1 branch"],
  ["A3", "state branch spacedock-state/ops exists", "gh api repos/<project>/branches/spacedock-state%2Fops", "present"],
  ["A5", "inbox answers, contract v1, settings present", "GET <inbox>/health", "5 of 5 settings present"],
  ["A6", "trigger variables set", "gh variable list -R <trigger>", "2 of 2"],
  ["C1a", "dispatch token: actions write, 1 repository", "self-test: inbox token mint", "actions:write, <trigger> only"],
  ["C1b", "dispatch App cannot reach the project", "self-test: mint for <project>", "refused (422), as required"],
  ["C2", "agent token: contents, PRs, 1 repository", "self-test run: create-github-app-token", "contents+PR write, <project> only"],
  ["C3", "App keys stored (names only)", "gh secret list; <inbox>/health", "2 of 2"],
  ["C4a", "signing secret matches", "self-test: signed POST <inbox>", "accepted (202)"],
  ["C4b", "model token stored (name only)", "gh secret list -R <trigger>", "present"],
  ["C5a", "Slack webhook accepted the self-test notice", "self-test: webhook reply", "ok"],
  ["C5b", "self-test notice seen in the channel", "Captain: --slack-permalink <link>", "posted 10:42:07Z"],
  ["C6", "4 rulesets match the files, no bypass actor", "gh api repos/<project|trigger>/rulesets", "4 of 4"],
  ["C7", "setup PR merged: ops-gate.yml on default branch (also A4)", "gh api repos/<project>/contents/.github/workflows/ops-gate.yml", "present"],
].map(([id, what, by, obs]) => ({ id, v: "PASS", what, by, obs }));

function verify(scenario = "ok") {
  const out = head("verify" + (scenario === "ok" ? " --slack-permalink https://example.slack.com/archives/C0EXAMPLE/p1792665727000100" : ""));
  const rows = verified.map((r) => ({ ...r }));
  if (scenario === "failed") {
    Object.assign(rows[13], { v: "FAIL", obs: "main-protect has 1 bypass actor, expected 0", next: "remove the bypass actor in <project> Settings > Rules > Rulesets, then verify again" });
    Object.assign(rows[3], { v: "ERROR", obs: "could not read: <inbox> did not answer in 10 s", next: "check the site is deployed (A5), then verify again" });
  }
  if (scenario === "waiting" || scenario === "failed")
    Object.assign(rows[12], { v: "WAIT", obs: "no message link given", next: "open the self-test notice in Slack, Copy link, rerun verify with --slack-permalink <link>" });
  out.push(`  ${"step".padEnd(4)}  ${"verdict".padEnd(7)}  ${"what is read back".padEnd(56)}  ${"read by".padEnd(62)}  observed`);
  for (const r of rows) {
    out.push(`  ${r.id.padEnd(4)}  ${r.v.padEnd(7)}  ${r.what.padEnd(56)}  ${r.by.padEnd(62)}  ${r.obs}`);
    if (r.next) out.push(`  ${"".padEnd(4)}  ${"".padEnd(7)}  next: ${r.next}`);
  }
  out.push("", "PASS read back as set · FAIL read back but wrong · ERROR could not be read · WAIT needs the Captain");
  const n = (v) => rows.filter((r) => r.v === v).length;
  out.push("", `${n("PASS")} PASS, ${n("FAIL")} FAIL, ${n("ERROR")} ERROR, ${n("WAIT")} WAIT of ${rows.length}.`);
  if (rows.some((r) => r.v !== "PASS")) out.push("Setup is not complete. Exit 1.");
  else out.push("Setup complete: a signed event can reach Slack and wake only this project's ops workflow. Exit 0.");
  return out.join("\n");
}

const ceiling = { head: "relay · signed-in ceiling near", body: "40 of 50 signed-in publishes today (limit source: default)" };
const runLink = (n, label) => `<https://github.com/${T}/actions/runs/${n}|${label}>`;
const slackStates = {
  started: { ...ceiling, agent: `:white_check_mark: Agent started · ${runLink(39750507891, "mira-shop ops run")}; its Draft PR links from the run` },
  refused: { ...ceiling, agent: ":warning: Needs action · agent NOT started: GitHub refused the dispatch (HTTP 403). Run ops-inbox setup verify; the sender's next retry can still start it." },
  retried: { ...ceiling, agent: `:white_check_mark: Agent started after a retry · ${runLink(39750519304, "mira-shop ops run")}; its Draft PR links from the run` },
  uncertain: { ...ceiling, agent: `:question: Needs a look · agent start UNCERTAIN: GitHub did not answer in 10 s, and the inbox will not resend this event. <https://github.com/${T}/actions|Check the runs>` },
  selftest: { head: "Setup self-test · example-owner/mira-shop", body: "Signature verified; the dispatch App reaches only the trigger repository.",
    agent: `:white_check_mark: ${runLink(39750511120, "Self-test run")} started; no task is filed. Captain: paste this message's link into setup verify.`, id: "setup-selftest-7f3a91c2", source: "urn:ops-inbox:setup" },
  long: { ...ceiling, agent: `:white_check_mark: Agent started · ${runLink(39750507891, "mira-shop ops run")}; its Draft PR links from the run`,
    id: "relay-ceiling-20261020-a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e" },
  sentry: { head: "sentry-shaped · error", body: "TypeError: <!channel> total is undefined · checkout/pay",
    agent: `:white_check_mark: Agent started · ${runLink(39750509002, "mira-shop ops run")}; its Draft PR links from the run`, id: "sentry-4471-91ab", source: "urn:sentry:mira-shop" },
  longtext: { head: "sentry-shaped · error", body: ("Error: request to payments provider failed after 3 attempts while confirming order totals for a basket with many items and a discount code applied at checkout, " +
    "then the fallback path also failed because the session store returned an unexpected shape for the stored cart").slice(0, 200) + "…",
    agent: `:white_check_mark: Agent started · ${runLink(39750509917, "mira-shop ops run")}; its Draft PR links from the run`, id: "sentry-4472-02cd", source: "urn:sentry:mira-shop" },
  nofields: { head: "relay · signed-in ceiling near", body: "(the event sent no allowlisted fields)",
    agent: `:white_check_mark: Agent started · ${runLink(39750510233, "mira-shop ops run")}; its Draft PR links from the run`, id: "relay-ceiling-20261021-c3d4" },
};

const slackEscape = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function slackPayload(state) {
  const s = slackStates[state];
  const id = s.id || "relay-ceiling-20261020-a1b2";
  const ctx = `event ${id} · source ${s.source || "urn:relay:prod"} · contract v1`;
  return { text: `${slackEscape(s.head)}: ${slackEscape(s.body)}`, blocks: [
    { type: "section", text: { type: "mrkdwn", text: `*${slackEscape(s.head)}*\n${slackEscape(s.body)}` } },
    { type: "section", text: { type: "mrkdwn", text: s.agent } },
    { type: "context", elements: [{ type: "mrkdwn", text: slackEscape(ctx) }] }] };
}

const GLYPH = { ":white_check_mark:": "✅", ":warning:": "⚠️", ":question:": "❓" };
const html = (t) => t.replace(/&(?!lt;|gt;|amp;)/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const mrk = (t) => html(t).replace(/&lt;[^|&]+\|([^&]+)&gt;/g, "<u>$1</u>").replace(/:[a-z_]+:/g, (g) => GLYPH[g] || g);
function slackCard(state, theme) {
  const p = slackPayload(state);
  const [h, b] = p.blocks[0].text.text.replace(/^\*/, "").split("*\n");
  const warn = state === "refused" || state === "uncertain" ? " warn" : "";
  return `<div class="msg ${theme}"><div class="avatar">OI</div><div class="col">
<div class="who"><b>ops-inbox</b> <span class="app">APP</span> <span class="ts">08:48</span></div>
<div class="h">${h}</div><div>${b}</div><div class="agent${warn}">${mrk(p.blocks[1].text.text)}</div>
<div class="ctx">${p.blocks[2].elements[0].text}</div></div></div>`;
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
.ctx{font-size:12px;color:#616061;margin-top:4px}.dark .ctx{color:#ababad}
.phone .msg{max-width:358px}pre{background:#0d1117;color:#e6edf3;padding:12px;font-size:12px;border-radius:6px;white-space:pre-wrap;word-break:break-all;max-width:1340px}`;
  const light = ["started", "refused", "retried", "uncertain", "selftest", "long", "sentry", "longtext", "nofields"];
  const slack = `<!doctype html><meta charset="utf-8"><title>Slack notice preview</title><style>${css}</style>
<h2>Slack notice, proposed (DISPOSABLE mock drawn locally; Slack draws the real one)</h2>
<p class="note">One notice per event and outcome. A repeat send of an event that already started, or whose start is uncertain, posts nothing. A repeat after "NOT started" posts at most one more notice: "started after a retry", or nothing if GitHub refuses again. Event text is escaped: the sentry card's "&lt;!channel&gt;" is plain text, not a mention. Field text is cut at 200 characters.</p>
<h2>Light theme, desktop width: started, NOT started, started after a retry, UNCERTAIN, self-test, longest event id (64), escaped mention, long field text, no allowlisted fields</h2>
${light.map((s) => slackCard(s, "light")).join("\n")}
<h2>Dark theme</h2>${["started", "refused", "uncertain", "selftest"].map((s) => slackCard(s, "dark")).join("\n")}
<h2>Phone width (390 px)</h2><div class="phone">${["started", "refused", "longtext", "selftest"].map((s) => slackCard(s, "light")).join("\n")}</div>`;
  writeFileSync(join(dir, "slack.html"), slack);
  const blocks = [["setup plan", plan()], ["setup apply without --yes", apply("noyes")], ["setup apply, first run (one step failed, one waiting)", apply("first")],
    ["setup apply, rerun (idempotent)", apply("rerun")], ["setup verify, all PASS", verify("ok")],
    ["setup verify, FAIL, ERROR and WAIT rows", verify("failed")], ["setup verify, only the Slack step waiting", verify("waiting")]];
  const term = `<!doctype html><meta charset="utf-8"><title>Setup output preview</title><style>${css}</style>
<h2>ops-inbox setup output, proposed (DISPOSABLE; printed by setup-preview.mjs; long lines wrap as a terminal wraps them)</h2>
${blocks.map(([t, b]) => `<h2>${t}</h2><pre>${html(b)}</pre>`).join("\n")}`;
  writeFileSync(join(dir, "terminal.html"), term);
  return `wrote slack.html and terminal.html in ${dir}`;
}

const [mode = "plan", arg] = process.argv.slice(2);
const here = dirname(fileURLToPath(import.meta.url));
const run = { plan, apply: () => apply(arg), verify: () => verify(arg), html: () => writeHtml(here),
  slack: () => slackStates[arg || "started"] ? JSON.stringify(slackPayload(arg || "started"), null, 2) : null }[mode];
const text = run && run();
if (!text) { console.error("usage: setup-preview.mjs plan|apply [first|rerun|noyes]|verify [ok|failed|waiting]|slack <state>|html"); process.exit(2); }
console.log(text);
const code = /Exit (\d)\.$/.exec(text);
process.exit(code ? Number(code[1]) : 0);
