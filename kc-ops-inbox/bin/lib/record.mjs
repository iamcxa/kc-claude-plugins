import { TYPES, CONTRACT_VERSION } from "../../core/inbox-core.mjs";

const PLACEHOLDER = "(to be written by the First Officer)";

const cell = (v) => String(v).replace(/\|/g, "\\|").replace(/\n/g, " ");

export function eventRow(n, ev, received) {
  const what = ev.data.event ?? ev.type;
  const fields = Object.entries(ev.data).filter(([k]) => !["v", "event", "at"].includes(k)).map(([k, v]) => `${k} ${v}`).join("; ");
  return `| ${n} | ${received} | \`${ev.id}\` | ${cell(what)} | ${cell(fields)} |`;
}

// The part of the record the inbox knows; the First Officer fills the four marked sections.
export function skeleton({ ev, slug, received }) {
  const { head } = TYPES[ev.type].describe(ev);
  return [
    `# ops: ${head}`,
    "",
    `Incident \`${ev.subject}\` · source ${ev.source} · contract ${CONTRACT_VERSION} · ops task \`${slug}\` on spacedock-state/ops`,
    "",
    "## Events",
    "",
    "| # | received | event id | what | fields |",
    "| - | - | - | - | - |",
    eventRow(1, ev, received),
    "",
    "## Diagnosis",
    "",
    PLACEHOLDER,
    "",
    "## Options",
    "",
    PLACEHOLDER,
    "",
    "## Recommendation",
    "",
    PLACEHOLDER,
    "",
    "## Rulings cited",
    "",
    PLACEHOLDER,
    "",
  ].join("\n");
}

export const REQUIRED_SECTIONS = ["Events", "Diagnosis", "Options", "Recommendation", "Rulings cited"];

// Names the sections still empty or missing, so an unfinished record is stated in the PR instead of passing as done.
export function incompleteSections(text) {
  return REQUIRED_SECTIONS.filter((name) => {
    const m = text.match(new RegExp(`^## ${name}\\s*\\n([\\s\\S]*?)(?=^## |(?![\\s\\S]))`, "m"));
    return !m || m[1].trim() === "" || m[1].includes(PLACEHOLDER);
  });
}

const HOW_TO_DECIDE = "**How to decide:** approve this pull request to accept the recommendation; to choose another option, submit a review with \"Request changes\", or \"Comment\" naming exactly one option (for example \"Option 2\"). Your review is the recorded decision, with your words. A Comment that names no single option is a question: it records nothing and the decision stays open. In r1 nothing runs after the decision: you carry out the option yourself, and merging keeps this record on the default branch.";

// Adds the fixed decision text after the Recommendation and the measures at the end.
export function finalize(text, { received, recommended }) {
  let out = text.replace(/\n+$/, "\n");
  if (!/^\*\*How to decide:\*\*/m.test(out)) {
    const at = out.search(/^## Rulings cited/m);
    out = at < 0 ? `${out}\n${HOW_TO_DECIDE}\n` : `${out.slice(0, at)}${HOW_TO_DECIDE}\n\n${out.slice(at)}`;
  }
  const seconds = Math.max(0, Math.round((Date.parse(recommended) - Date.parse(received)) / 1000));
  return [
    out.replace(/\n+$/, ""),
    "",
    "## Measures",
    "",
    `- Event received ${received} · recommendation ready ${recommended} · ${Math.floor(seconds / 60)} min ${seconds % 60} s`,
    "- Your decision: ops-gate records it from your review on the ops task (state branch), not in this file, with followed: yes when you approve, otherwise no",
    "",
  ].join("\n");
}

export function recommendationSentence(text) {
  const m = text.match(/^## Recommendation\s*\n+([^\n]+)/m);
  return m ? m[1].replace(/\*\*/g, "").slice(0, 300) : "see the record";
}
