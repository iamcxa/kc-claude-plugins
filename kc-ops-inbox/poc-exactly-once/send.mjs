import { createHmac } from "node:crypto";

export function signedRequest({ secret, webhookId, body, timestamp }) {
  const key = Buffer.from(secret.replace(/^whsec_/, ""), "base64");
  const sig = createHmac("sha256", key).update(`${webhookId}.${timestamp}.${body}`).digest("base64");
  return {
    method: "POST",
    headers: {
      "content-type": "application/cloudevents+json",
      "webhook-id": webhookId,
      "webhook-timestamp": String(timestamp),
      "webhook-signature": `v1,${sig}`,
    },
    body,
  };
}

export function fixtureEvent(id) {
  return JSON.stringify({
    specversion: "1.0",
    id,
    source: "urn:ops-inbox-poc:fixture",
    type: "fixture.alert.raised",
    time: new Date().toISOString(),
    data: { note: "synthetic fixture" },
  });
}

// CLI: WEBHOOK_SECRET=... node send.mjs <url> <event-id> [tamper]
if (import.meta.url === `file://${process.argv[1]}`) {
  const [url, id, mode] = process.argv.slice(2);
  let body = fixtureEvent(id);
  const req = signedRequest({ secret: process.env.WEBHOOK_SECRET, webhookId: `msg_${id}`, body, timestamp: Math.floor(Date.now() / 1000) });
  if (mode === "tamper") req.body = body.replace("raised", "raisee");
  const sent = Date.now();
  const res = await fetch(url, req);
  console.log(JSON.stringify({ sentAt: sent, receivedAt: Date.now(), status: res.status, body: await res.json() }));
}
