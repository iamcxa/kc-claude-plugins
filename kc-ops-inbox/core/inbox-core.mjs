import { createSign } from "node:crypto";
import { CONTRACT_VERSION, ENVIRONMENTS, parseEvent } from "../contract/contract.mjs";

// How each event type reads in a Slack notice and in the record's title. The contract owns what an
// event may carry; this table only chooses which of it to show.
const clip = (t, n) => (t.length > n ? `${t.slice(0, n)}…` : t);
const metricHead = (ev, what) => `${ev.source.split(":").slice(1).join(" ")} · ${ev.data.metric} ${what}`;
const metricBody = (ev) => `${ev.data.value} of ${ev.data.limit} per ${ev.data.window} (${ev.environment}, ${ev.severity}; limit source: ${ev.data.limitSource})`;
const DESCRIBE = {
  "ops.metric.crossed": (ev) => ({ head: metricHead(ev, `crossed ${ev.data.level}%`), body: metricBody(ev) }),
  "ops.metric.recovered": (ev) => ({ head: metricHead(ev, `recovered (${ev.data.cause})`), body: metricBody(ev) }),
  "ops.metric.heartbeat": (ev) => ({ head: metricHead(ev, "heartbeat"), body: metricBody(ev) }),
  "sentry.issue.alert": (ev) => ({ head: `sentry · ${ev.data.level}`, body: clip([ev.data.title, ev.data.culprit].filter(Boolean).join(" · "), 200) }),
  "ops.inbox.selftest": (ev) => ({ head: `Read-back self-test · ${ev.data.project}`, body: "Signature verified; the dispatch App reaches only the trigger repository." }),
};
export const describeEvent = (ev) => DESCRIBE[ev.type](ev);

// The one key this instance verifies with; per-environment and per-source keys are a runtime gap the
// contract README assigns to r1.
const keysFrom = (env) => [{ secret: env.WEBHOOK_SECRET, environments: ENVIRONMENTS, sources: ["urn:"] }];

// ---- Notices ---------------------------------------------------------------

const slackEscape = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const runLink = (url, label) => `<${url}|${label}>`;

export function incidentBranch(ev, incident) {
  const safe = ev.subject.replace(/[^A-Za-z0-9._-]/g, "-").replace(/-+/g, "-").replace(/^[-.]+|[-.]+$/g, "").toLowerCase();
  return `${safe.slice(0, 80)}-${incident.slice(0, 8)}`;
}

// kind: opened | joined | refused | uncertain | selftest
export function buildNotice(kind, { ev, branch, runUrl, number, status, triggerRepo }) {
  const { head, body } = describeEvent(ev);
  const agent = {
    opened: `:white_check_mark: New incident \`${slackEscape(ev.subject)}\` · agent started · ${runLink(runUrl, "run for this incident")}; its Draft PR links from the run`,
    joined: `:link: Joins incident \`${slackEscape(ev.subject)}\` (event ${number}) · recorded on its ops task, no new agent run · ${runLink(runUrl, "run that opened it")}`,
    refused: `:x: Needs action · GitHub refused the dispatch (HTTP ${status}), so no agent runs for this event. Run the setup read-back. If the sender retries, the retry posts its own notice.`,
    uncertain: `:question: Needs a look · agent start UNCERTAIN: GitHub did not answer in time or answered 5xx, and the inbox will not resend this event. ${runLink(`https://github.com/${triggerRepo}/actions`, "open the trigger repository's runs")}`,
    selftest: `:test_tube: ${runLink(runUrl, "Self-test run")} started; no task is filed. Captain: paste this message's link into the read-back.`,
  }[kind];
  const blocks = [
    { type: "section", text: { type: "mrkdwn", text: `*${slackEscape(head)}*\n${slackEscape(body)}` } },
    { type: "section", text: { type: "mrkdwn", text: agent } },
    { type: "context", elements: [{ type: "mrkdwn", text: slackEscape(`event ${ev.id} · source ${ev.source} · contract ${CONTRACT_VERSION}`) }] },
  ];
  const text = `${slackEscape(head)}: ${slackEscape(body)}`;
  const color = { refused: "#d00000", uncertain: "#e8890c" }[kind];
  return color ? { text, attachments: [{ color, blocks }] } : { text, blocks };
}

// ---- GitHub ----------------------------------------------------------------

const b64u = (b) => Buffer.from(b).toString("base64url");

export function appJwt({ appId, privateKeyPem, nowS }) {
  const head = b64u(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claims = b64u(JSON.stringify({ iat: nowS - 60, exp: nowS + 540, iss: appId }));
  return `${head}.${claims}.${b64u(createSign("RSA-SHA256").update(`${head}.${claims}`).sign(privateKeyPem))}`;
}

const SETTINGS = ["OPS_TRIGGER_REPO", "OPS_WORKFLOW", "DISPATCH_APP_ID", "DISPATCH_INSTALLATION_ID"];
const SECRETS = ["WEBHOOK_SECRET", "DISPATCH_APP_PRIVATE_KEY", "SLACK_WEBHOOK_URL"];

export function health(env) {
  const present = (names) => ({ present: names.filter((n) => env[n]).length, total: names.length, missing: names.filter((n) => !env[n]) });
  return { contract: CONTRACT_VERSION, settings: present(SETTINGS), secrets: present(SECRETS) };
}

const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

// ---- Handler ---------------------------------------------------------------
// Platform-neutral: a Web Request in, a Web Response out.
// store: { set(key, value, { onlyIfNew }) -> { modified }, get(key) -> string | null, delete(key) }

export async function handle(req, deps) {
  const { store, fetchImpl, env, now = Date.now, log = console.log, timeoutMs = 10000 } = deps;
  const t = { arrival: now() };
  const api = (path, token, init = {}) =>
    fetchImpl(`${env.OPS_GITHUB_API_URL || "https://api.github.com"}${path}`, {
      ...init,
      signal: AbortSignal.timeout(timeoutMs),
      headers: {
        authorization: `Bearer ${token}`,
        accept: "application/vnd.github+json",
        "x-github-api-version": "2022-11-28",
        "content-type": "application/json",
        "user-agent": "kc-ops-inbox",
      },
    });
  const post = async (notice) => {
    if (!env.SLACK_WEBHOOK_URL) return null;
    try {
      const res = await fetchImpl(env.SLACK_WEBHOOK_URL, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(notice), signal: AbortSignal.timeout(5000) });
      return res.status;
    } catch (err) {
      log(JSON.stringify({ evt: "slack-failed", error: String(err.message) }));
      return null;
    }
  };

  if (req.method === "GET" && new URL(req.url).pathname.endsWith("/health")) return json(200, health(env));
  if (req.method !== "POST") return json(405, { error: "method" });

  const body = await req.text();
  const parsed = parseEvent({ keys: keysFrom(env), headers: req.headers, body, nowS: Math.floor(t.arrival / 1000) });
  if (!parsed.ok) {
    log(JSON.stringify({ evt: "rejected", reason: parsed.reason, status: parsed.status }));
    return json(parsed.status, { error: parsed.reason });
  }
  const { event: ev, keys } = parsed;
  const triggerRepo = env.OPS_TRIGGER_REPO;

  const eventClaim = `event.${keys.dedupe}`;
  const first = await store.set(eventClaim, JSON.stringify({ id: ev.id, source: ev.source, claimedAt: now() }), { onlyIfNew: true });
  if (!first.modified) {
    log(JSON.stringify({ evt: "duplicate", id: ev.id }));
    return json(200, { status: "duplicate", id: ev.id });
  }

  const selftest = ev.type === "ops.inbox.selftest";
  const branch = selftest ? null : incidentBranch(ev, keys.incident);
  const incidentClaim = `incident.${keys.incident}`;
  let mode = "selftest";
  let opening = null;
  let madeIncident = false;
  if (!selftest) {
    const made = await store.set(incidentClaim, JSON.stringify({ branch, firstEventId: ev.id, runId: null, runUrl: null }), { onlyIfNew: true });
    madeIncident = made.modified;
    mode = madeIncident ? "open" : "join";
    if (!madeIncident) opening = JSON.parse((await store.get(incidentClaim)) ?? "{}");
  }
  const release = async () => {
    await store.delete(eventClaim);
    if (madeIncident) await store.delete(incidentClaim);
  };

  let token;
  let mint;
  try {
    const jwt = appJwt({ appId: env.DISPATCH_APP_ID, privateKeyPem: env.DISPATCH_APP_PRIVATE_KEY, nowS: Math.floor(now() / 1000) });
    const res = await api(`/app/installations/${env.DISPATCH_INSTALLATION_ID}/access_tokens`, jwt, {
      method: "POST",
      body: JSON.stringify({ repositories: [triggerRepo.split("/")[1]], permissions: { actions: "write" } }),
    });
    if (res.status !== 201) throw Object.assign(new Error(`token-mint-${res.status}`), { status: res.status });
    mint = await res.json();
    token = mint.token;
  } catch (err) {
    await release();
    const status = err.status ?? 0;
    log(JSON.stringify({ evt: "dispatch-failed", id: ev.id, mode, stage: "mint", error: String(err.message), released: true }));
    await post(buildNotice("refused", { ev, status: status || "no answer", triggerRepo }));
    return json(502, { error: "dispatch-refused" });
  }

  let run;
  try {
    const res = await api(`/repos/${triggerRepo}/actions/workflows/${env.OPS_WORKFLOW}/dispatches`, token, {
      method: "POST",
      body: JSON.stringify({
        ref: env.OPS_REF || "main",
        inputs: { mode, branch: branch ?? "", incident: keys.incident, event: body, opening_run: String(opening?.runId ?? ""), received: new Date(t.arrival).toISOString() },
        return_run_details: true,
      }),
    });
    if (res.status !== 200 && res.status !== 204) throw Object.assign(new Error(`dispatch-${res.status}`), { status: res.status });
    run = res.status === 200 ? await res.json() : { workflow_run_id: null, html_url: `https://github.com/${triggerRepo}/actions` };
  } catch (err) {
    if (err.status && err.status < 500) {
      await release();
      log(JSON.stringify({ evt: "dispatch-failed", id: ev.id, mode, stage: "dispatch", error: err.message, released: true }));
      await post(buildNotice("refused", { ev, status: err.status, triggerRepo }));
      return json(502, { error: "dispatch-refused" });
    }
    log(JSON.stringify({ evt: "dispatch-failed", id: ev.id, mode, stage: "dispatch", error: String(err.message), released: false }));
    await post(buildNotice("uncertain", { ev, triggerRepo }));
    return json(504, { error: "dispatch-ambiguous" });
  }

  const runId = run.workflow_run_id ?? null;
  const runUrl = run.html_url;
  let slack;
  const out = { status: "dispatched", mode, id: ev.id, run_id: runId, run_url: runUrl };

  if (selftest) {
    const project = ev.data.project;
    const projectMint = await api(`/app/installations/${env.DISPATCH_INSTALLATION_ID}/access_tokens`, appJwt({ appId: env.DISPATCH_APP_ID, privateKeyPem: env.DISPATCH_APP_PRIVATE_KEY, nowS: Math.floor(now() / 1000) }), {
      method: "POST",
      body: JSON.stringify({ repositories: [project.split("/")[1]], permissions: { actions: "write" } }),
    });
    const projectDispatch = await api(`/repos/${project}/actions/workflows/${env.OPS_PROJECT_WORKFLOW || "ci.yml"}/dispatches`, token, { method: "POST", body: JSON.stringify({ ref: "main" }) });
    const projectRerun = await api(`/repos/${project}/actions/runs/1/rerun`, token, { method: "POST" });
    slack = await post(buildNotice("selftest", { ev, runUrl, triggerRepo }));
    Object.assign(out, {
      status: "selftest",
      mint_trigger: { permissions: mint.permissions, repositories: (mint.repositories ?? []).map((r) => r.full_name ?? r.name) },
      mint_project: { status: projectMint.status },
      project_dispatch: { status: projectDispatch.status },
      project_rerun: { status: projectRerun.status },
      slack: { status: slack },
    });
    log(JSON.stringify({ evt: "selftest", id: ev.id, run_id: runId, mint_project: projectMint.status, project_dispatch: projectDispatch.status, project_rerun: projectRerun.status, slack }));
    return json(200, out);
  }

  if (madeIncident) {
    await store.set(incidentClaim, JSON.stringify({ ...opening, branch, firstEventId: ev.id, runId, runUrl }));
    slack = await post(buildNotice("opened", { ev, branch, runUrl }));
  } else {
    let number = 2;
    while (number < 100 && !(await store.set(`${incidentClaim}.event.${number}`, ev.id, { onlyIfNew: true })).modified) number += 1;
    slack = await post(buildNotice("joined", { ev, branch, runUrl: opening.runUrl ?? runUrl, number }));
    out.event_number = number;
  }
  log(JSON.stringify({ evt: "delivered", id: ev.id, mode, branch, run_id: runId, slack }));
  return json(202, out);
}
