// Runs the report query functions of a reconstructed mira-app tree against a recording db.js and prints what each one opened.
// usage: node readonly_probe.mjs <tree>   (tree/src/*.js, tree/package.json with "type": "module")
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';

const tree = process.argv[2];
const db = await import(pathToFileURL(join(tree, 'src', 'db.js')).href);
const mod = await import(pathToFileURL(join(tree, 'src', 'report_queries.js')).href);
const importOpens = db.opened.slice().map((o) => ({ ...o }));

const calls = {
  dailyTotals: ['s1', '2026-10-01'],
  topItems: ['s1', '2026-10-01'],
  weeklyTotals: ['s1', '2026-10-01'],
  markReportSent: ['r1', '2026-10-01T00:00:00Z'],
};
const out = { import_opens: importOpens, calls: {} };
for (const [name, args] of Object.entries(calls)) {
  if (typeof mod[name] !== 'function') {
    out.calls[name] = { missing: true };
    continue;
  }
  db.opened.length = 0;
  try {
    await mod[name](...args);
    out.calls[name] = { opened: db.opened.map((o) => ({ ...o })) };
  } catch (e) {
    out.calls[name] = { error: String((e && e.message) || e), opened: db.opened.map((o) => ({ ...o })) };
  }
}
console.log(JSON.stringify(out));
