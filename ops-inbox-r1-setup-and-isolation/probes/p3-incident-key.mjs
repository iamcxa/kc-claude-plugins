// P3: what makes two events one incident. Local only, no network.
import { createHash } from "node:crypto";
const h = (s) => createHash("sha256").update(s).digest("hex").slice(0, 12);
const R = "https://relay.example/ops"; // relay source (one per deploy)
const S = "https://sentry.io/qnow";     // sentry source
// Relay ceiling events: field set of POC1's fixture-event.json; subject per the proposed v1 rule.
const relay = (id, tier, day, count, limit, event) => ({ source: R, id, type: "relay.capacity.ceiling",
  subject: `ceiling/${tier}/${day}`, data: { v: 1, event, at: `${day}T12:00:00Z`, day, count, limit, limitSource: "default" } });
const sentry = (id, issue) => ({ source: S, id, type: "sentry.issue.alert", subject: `issue/${issue}`,
  data: { issue_id: issue, event_id: id } });
// Expected grouping = one Captain decision per incident: the remedy for a bound-tier ceiling on day D
// (scripts/bound-ceiling record, relay ADR 0060) differs from the anonymous one (env var, ADR 0043) and lapses at midnight.
const seq = [
  [relay("bound-2026-10-20-80", "bound", "2026-10-20", 120, 150, "bound-ceiling-near"), "A"],
  [relay("bound-2026-10-20-80", "bound", "2026-10-20", 121, 150, "bound-ceiling-near"), "dup"],   // producer retry, same id
  [relay("bound-2026-10-20-100", "bound", "2026-10-20", 150, 150, "bound-ceiling-full"), "A"],    // full after near, same day
  [relay("anon-2026-10-20-100", "anonymous", "2026-10-20", 50, 50, "anon-ceiling-full"), "B"],    // other tier, same day
  [relay("bound-2026-10-21-80", "bound", "2026-10-21", 120, 150, "bound-ceiling-near"), "C"],     // next day
  [sentry("e1", "4501"), "D"], [sentry("e2", "4501"), "D"], [sentry("e3", "4502"), "E"],
];
const candidates = {
  "source+id (dedupe key)": (e) => `${e.source}\n${e.id}`,
  "source+type": (e) => `${e.source}\n${e.type}`,
  "source+type+data.day": (e) => `${e.source}\n${e.type}\n${e.data.day ?? ""}`,
  "source+subject (proposed)": (e) => `${e.source}\n${e.subject}`,
};
const seen = new Set(); const events = [];
for (const [e, want] of seq) { const d = h(`${e.source}\n${e.id}`); if (seen.has(d)) { console.log(`dedupe: ${e.id} dropped before grouping`); continue; } seen.add(d); events.push([e, want]); }
for (const [name, key] of Object.entries(candidates)) {
  let wrong = 0;
  for (let i = 0; i < events.length; i++) for (let j = i + 1; j < events.length; j++) {
    const same = key(events[i][0]) === key(events[j][0]); const want = events[i][1] === events[j][1];
    if (same !== want) wrong++;
  }
  const groups = new Set(events.map(([e]) => h(key(e)))).size;
  console.log(`${name.padEnd(28)} groups=${groups} expected=5 wrong-pairs=${wrong}`);
}
