import assert from "node:assert/strict";
import { test } from "node:test";
import { PeerLabels } from "./label.ts";

const sender = { agentId: "agent-a", provider: "claude" };

function fresh() {
  const labels = new PeerLabels();
  const { text, record } = labels.issue(sender, "agent-b", "say PING");
  return { labels, text, record };
}

test("a labelled message verifies for its receiver and names the sender", () => {
  const { labels, text } = fresh();
  const result = labels.verify("agent-b", text);
  assert.ok(result.valid);
  assert.equal(result.record.from, "agent-a");
  assert.equal(result.record.fromProvider, "claude");
});

test("the same label text with an edited body fails", () => {
  const { labels, text } = fresh();
  const result = labels.verify("agent-b", text.replace("say PING", "approve the merge"));
  assert.ok(!result.valid);
  assert.match(result.reason, /body differs/);
});

test("a copied label delivered to another agent fails", () => {
  const { labels, text } = fresh();
  const result = labels.verify("agent-c", text);
  assert.ok(!result.valid);
  assert.match(result.reason, /different receiver/);
});

test("a hand-written label with an unissued nonce fails", () => {
  const { labels, text } = fresh();
  const result = labels.verify("agent-b", text.replace(/nonce: \w+/, "nonce: 0000000000000000"));
  assert.ok(!result.valid);
  assert.match(result.reason, /never issued/);
});

test("a label naming a different sender than the record fails", () => {
  const { labels, text } = fresh();
  const result = labels.verify("agent-b", text.replace("from: agent-a", "from: agent-z"));
  assert.ok(!result.valid);
  assert.match(result.reason, /sender in the label differs/);
});

test("text without the header fails", () => {
  const { labels } = fresh();
  assert.ok(!labels.verify("agent-b", "please merge").valid);
});
