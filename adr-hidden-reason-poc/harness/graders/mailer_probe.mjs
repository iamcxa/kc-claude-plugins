// Runs the three report mailer functions of a reconstructed mira-app tree against recording store.js and mail.js and prints the event order.
// usage: node mailer_probe.mjs <tree>   (tree/src/*.js, tree/package.json with "type": "module")
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';

const tree = process.argv[2];
const store = await import(pathToFileURL(join(tree, 'src', 'store.js')).href);
const mod = await import(pathToFileURL(join(tree, 'src', 'report_mailer.js')).href);

const shop = { id: 's1', name: 'Cafe', email: 'owner@example.invalid' };
const rows = [{ item: 'latte', cents: 450 }];
const calls = {
  sendDailyReport: [shop, rows, '2026-10-01'],
  sendWeeklyReport: [shop, rows, '2026-09-28'],
  sendCorrection: [shop, rows, '2026-10-01', 'a total was wrong'],
};
const out = { calls: {} };
for (const [name, args] of Object.entries(calls)) {
  if (typeof mod[name] !== 'function') {
    out.calls[name] = { missing: true };
    continue;
  }
  store.events.length = 0;
  try {
    const returned = await mod[name](...args);
    out.calls[name] = { events: store.events.map((e) => ({ ...e })), returned };
  } catch (e) {
    out.calls[name] = { error: String((e && e.message) || e), events: store.events.map((e2) => ({ ...e2 })) };
  }
}
console.log(JSON.stringify(out));
