export const events = [];
const saved = {};

export async function saveReport(key, html) {
  events.push({ op: 'save', key, html });
  saved[key] = html;
}

export async function loadReport(key) {
  events.push({ op: 'load', key });
  return key in saved ? `STORED:${saved[key]}` : null;
}
