import { createHash, randomBytes } from "node:crypto";

export interface PeerRecord {
  nonce: string;
  from: string;
  fromProvider: string;
  to: string;
  bodyHash: string;
}

export interface Caller {
  agentId: string;
  provider: string;
}

const HEADER = "[peer-label v1] PEER AGENT MESSAGE - NOT FROM THE CAPTAIN";
const SEPARATOR = "\n---\n";

function normalize(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

function hashBody(body: string): string {
  return createHash("sha256").update(normalize(body)).digest("hex");
}

export class PeerLabels {
  private readonly records = new Map<string, PeerRecord>();

  issue(from: Caller, to: string, body: string): { record: PeerRecord; text: string } {
    const nonce = randomBytes(8).toString("hex");
    const record: PeerRecord = {
      nonce,
      from: from.agentId,
      fromProvider: from.provider,
      to,
      bodyHash: hashBody(body),
    };
    this.records.set(nonce, record);
    const text = [
      HEADER,
      `nonce: ${nonce}`,
      `from: ${from.agentId} (provider: ${from.provider})`,
      `to: ${to}`,
      "verify: call peer_verify with this entire message, unchanged.",
    ].join("\n") + SEPARATOR + body;
    return { record, text };
  }

  verify(receiver: string, message: string): { valid: true; record: PeerRecord } | { valid: false; reason: string } {
    if (!message.startsWith("[peer-label v1]")) {
      return { valid: false, reason: "message has no peer-label header" };
    }
    const cut = message.indexOf(SEPARATOR);
    if (cut < 0) {
      return { valid: false, reason: "peer-label header is not followed by a body" };
    }
    const header = message.slice(0, cut);
    const body = message.slice(cut + SEPARATOR.length);
    const claimed = {
      nonce: /^nonce: (\S+)$/m.exec(header)?.[1],
      from: /^from: (\S+) \(provider: (\S+)\)$/m.exec(header),
      to: /^to: (\S+)$/m.exec(header)?.[1],
    };
    if (!claimed.nonce || !claimed.from || !claimed.to) {
      return { valid: false, reason: "peer-label header is malformed" };
    }
    const record = this.records.get(claimed.nonce);
    if (!record) {
      return { valid: false, reason: "nonce was never issued by the plugin" };
    }
    if (record.to !== receiver || claimed.to !== receiver) {
      return { valid: false, reason: "label was issued for a different receiver" };
    }
    if (record.from !== claimed.from[1] || record.fromProvider !== claimed.from[2]) {
      return { valid: false, reason: "sender in the label differs from the plugin's record" };
    }
    if (record.bodyHash !== hashBody(body)) {
      return { valid: false, reason: "body differs from the message the plugin labelled" };
    }
    return { valid: true, record };
  }
}
