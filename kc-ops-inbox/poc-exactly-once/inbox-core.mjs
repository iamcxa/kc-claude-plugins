import { createHmac, createHash, createSign, timingSafeEqual } from "node:crypto";

const TOLERANCE_S = 300;
const ID_RE = /^[A-Za-z0-9._-]{1,64}$/;
const MAX_BODY = 65536;

const json = (status, body) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export function verifySignature({ secret, id, timestamp, signatureHeader, body, nowS }) {
  if (!id || !timestamp || !signatureHeader) return "missing-headers";
  const ts = Number(timestamp);
  if (!Number.isInteger(ts) || Math.abs(nowS - ts) > TOLERANCE_S) return "timestamp-out-of-tolerance";
  const key = Buffer.from(secret.replace(/^whsec_/, ""), "base64");
  const expected = createHmac("sha256", key).update(`${id}.${timestamp}.${body}`).digest();
  for (const part of signatureHeader.split(" ")) {
    const [version, sig] = part.split(",");
    if (version !== "v1" || !sig) continue;
    const got = Buffer.from(sig, "base64");
    if (got.length === expected.length && timingSafeEqual(got, expected)) return null;
  }
  return "signature-mismatch";
}

const b64u = (b) => Buffer.from(b).toString("base64url");

export function appJwt({ appId, privateKeyPem, nowS }) {
  const head = b64u(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claims = b64u(JSON.stringify({ iat: nowS - 60, exp: nowS + 540, iss: appId }));
  const sig = createSign("RSA-SHA256").update(`${head}.${claims}`).sign(privateKeyPem);
  return `${head}.${claims}.${b64u(sig)}`;
}

async function gh(fetchImpl, env, path, token, init = {}) {
  return fetchImpl(`${env.OPS_GITHUB_API_URL || "https://api.github.com"}${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${token}`,
      accept: "application/vnd.github+json",
      "x-github-api-version": "2022-11-28",
      "content-type": "application/json",
      "user-agent": "ops-inbox-poc",
    },
  });
}

// The dispatch-only App can only be granted Actions: write; the token request
// repeats that bound so a wider installation grant still yields a narrow token.
async function dispatchToken({ env, fetchImpl, nowS }) {
  if (env.GITHUB_DISPATCH_TOKEN) return { token: env.GITHUB_DISPATCH_TOKEN, permissions: null };
  const jwt = appJwt({ appId: env.DISPATCH_APP_ID, privateKeyPem: env.DISPATCH_APP_PRIVATE_KEY, nowS });
  const res = await gh(fetchImpl, env, `/app/installations/${env.DISPATCH_INSTALLATION_ID}/access_tokens`, jwt, {
    method: "POST",
    body: JSON.stringify({ repositories: [env.OPS_REPO.split("/")[1]], permissions: { actions: "write" } }),
  });
  if (res.status !== 201) throw Object.assign(new Error(`token-mint-${res.status}`), { refused: true });
  const out = await res.json();
  return { token: out.token, permissions: out.permissions };
}

export async function handle(req, deps) {
  const { store, fetchImpl, env, now = Date.now, log = console.log } = deps;
  const t = { arrival: now() };
  if (req.method !== "POST") return json(405, { error: "method" });

  const body = await req.text();
  if (body.length > MAX_BODY) return json(413, { error: "too-large" });

  const bad = verifySignature({
    secret: env.WEBHOOK_SECRET,
    id: req.headers.get("webhook-id"),
    timestamp: req.headers.get("webhook-timestamp"),
    signatureHeader: req.headers.get("webhook-signature"),
    body,
    nowS: Math.floor(t.arrival / 1000),
  });
  if (bad) {
    log(JSON.stringify({ evt: "rejected", reason: bad, t }));
    return json(401, { error: bad });
  }
  t.verified = now();

  let ev;
  try { ev = JSON.parse(body); } catch { return json(400, { error: "json" }); }
  const ok = ev && ev.specversion === "1.0" && typeof ev.source === "string" && ev.source.length > 0 &&
    ev.source.length <= 200 && typeof ev.type === "string" && typeof ev.id === "string" && ID_RE.test(ev.id);
  if (!ok) return json(400, { error: "not-a-cloudevent" });

  const key = createHash("sha256").update(`${ev.source}\n${ev.id}`).digest("hex");
  const claim = await store.set(key, JSON.stringify({ id: ev.id, source: ev.source, claimedAt: t.verified }), { onlyIfNew: true });
  t.claimed = now();
  if (!claim.modified) {
    log(JSON.stringify({ evt: "duplicate", id: ev.id, t }));
    return json(200, { status: "duplicate", id: ev.id });
  }

  let run;
  let tokenPermissions;
  try {
    const cred = await dispatchToken({ env, fetchImpl, nowS: Math.floor(now() / 1000) });
    tokenPermissions = cred.permissions;
    t.minted = now();
    const res = await gh(fetchImpl, env, `/repos/${env.OPS_REPO}/actions/workflows/${env.OPS_WORKFLOW}/dispatches`, cred.token, {
      method: "POST",
      body: JSON.stringify({
        ref: env.OPS_REF,
        inputs: { event_id: ev.id, event_source: ev.source, event_type: ev.type },
        return_run_details: true,
      }),
    });
    if (res.status !== 200 && res.status !== 204) throw Object.assign(new Error(`dispatch-${res.status}`), { refused: true });
    run = res.status === 200 ? await res.json() : { workflow_run_id: null, html_url: `https://github.com/${env.OPS_REPO}/actions` };
  } catch (err) {
    // A transport error may follow a dispatch GitHub already accepted, so only a definite refusal releases the claim.
    if (err.refused) await store.delete(key);
    log(JSON.stringify({ evt: "dispatch-failed", id: ev.id, error: String(err.message), released: Boolean(err.refused), t }));
    return json(err.refused ? 502 : 504, { error: err.refused ? "dispatch-refused" : "dispatch-ambiguous" });
  }
  t.dispatched = now();

  if (env.SLACK_WEBHOOK_URL) {
    try {
      await fetchImpl(env.SLACK_WEBHOOK_URL, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ text: `ops event ${ev.id} (${ev.type}) started ${run.html_url}` }),
      });
    } catch (err) {
      log(JSON.stringify({ evt: "slack-failed", error: String(err.message) }));
    }
  }
  t.slack = now();

  const out = { status: "dispatched", id: ev.id, run_id: run.workflow_run_id, run_url: run.html_url, t, tokenPermissions };
  log(JSON.stringify({ evt: "delivered", ...out }));
  return json(202, out);
}
