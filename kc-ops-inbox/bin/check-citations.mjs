#!/usr/bin/env node
// Re-reads every ADR reference block of an ops record with git and sha256, the machine half of kc-adr's read-adr step 2.
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

const USAGE = "usage: node check-citations.mjs <record.md> --repo <clone> [--annotate] [--allow-none]";

export function parseRecord(text) {
  const lines = text.split("\n");
  const start = lines.findIndex((l) => /^## Rulings cited\s*$/.test(l));
  if (start < 0) return { blocks: [], start: -1, end: -1, lines, defaults: {} };
  let end = lines.findIndex((l, i) => i > start && /^## /.test(l));
  if (end < 0) end = lines.length;
  const defaults = {};
  const blocks = [];
  let current = null;
  for (let i = start + 1; i < end; i += 1) {
    const heading = lines[i].match(/^### ADR (\d{4})\s*$/);
    if (heading) {
      current = { adr: heading[1], line: i, fields: {} };
      blocks.push(current);
      continue;
    }
    const field = lines[i].match(/^(?:- )?(repository|commit|path|digest|status):\s*(.*?)\s*$/i);
    if (field) (current ? current.fields : defaults)[field[1].toLowerCase()] = field[2];
  }
  return { blocks, start, end, lines, defaults };
}

function git(repo, args, { buffer = false } = {}) {
  return execFileSync("git", ["-C", repo, ...args], { stdio: ["ignore", "pipe", "ignore"], ...(buffer ? {} : { encoding: "utf8" }) });
}
const tryGit = (repo, args, opts) => { try { return git(repo, args, opts); } catch { return null; } };

const statusOf = (content) => {
  const m = content.toString("utf8").match(/^## Status\s*\n+\s*([^\n]+)/m);
  return m ? m[1].trim() : "";
};

// Returns null when the block holds, otherwise the reason.
export function checkBlock(block, defaults, repo) {
  const f = { ...defaults, ...block.fields };
  const repository = f.repository;
  const remote = tryGit(repo, ["remote", "get-url", "origin"]);
  if (!repository || !remote || !remote.trim().replace(/\.git$/, "").endsWith(`/${repository}`)) return "repo-mismatch";
  if (!/^[0-9a-f]{40}$/.test(f.commit ?? "") || tryGit(repo, ["cat-file", "-e", `${f.commit}^{commit}`]) === null) return "commit-missing";
  if (!f.path || tryGit(repo, ["cat-file", "-e", `${f.commit}:${f.path}`]) === null) return "path-missing";
  const bytes = git(repo, ["show", `${f.commit}:${f.path}`], { buffer: true });
  const digest = `sha256:${createHash("sha256").update(bytes).digest("hex")}`;
  if (f.digest !== digest) return "digest-mismatch";
  const status = statusOf(bytes);
  if (status !== "Accepted") return `not-in-force(${status || "no status"})`;
  const head = tryGit(repo, ["show", `HEAD:${f.path}`], { buffer: true });
  const atHead = head === null ? "removed at HEAD" : statusOf(head);
  if (atHead !== "Accepted") return `not-in-force(${atHead || "no status"})`;
  if (f.status !== "Accepted") return "status-mismatch";
  return null;
}

export function checkRecord(text, repo) {
  const parsed = parseRecord(text);
  const results = parsed.blocks.map((b) => ({ block: b, reason: checkBlock(b, parsed.defaults, repo) }));
  const blockAdrs = new Set(parsed.blocks.map((b) => b.adr));
  const outside = parsed.start < 0 ? parsed.lines : [...parsed.lines.slice(0, parsed.start), ...parsed.lines.slice(parsed.end)];
  const cited = new Set([...outside.join("\n").matchAll(/\[ADR (\d{4})(?: REFUSED)?\]/g)].map((m) => m[1]));
  const unbacked = [...cited].filter((n) => !blockAdrs.has(n));
  return { parsed, results, unbacked };
}

export function annotate(text, { parsed, results }) {
  const lines = [...parsed.lines];
  for (const { block, reason } of [...results].reverse()) lines.splice(block.line + 1, 0, `- check: ${reason ? `REFUSED ${reason}` : "OK"}`);
  let out = lines.join("\n");
  for (const { block, reason } of results) if (reason) out = out.replaceAll(`[ADR ${block.adr}]`, `[ADR ${block.adr} REFUSED]`);
  return out;
}

export function summary(results) {
  const refused = results.filter((r) => r.reason).length;
  return `Citations: ${results.length - refused} OK, ${refused} REFUSED.`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  const take = (flag) => { const i = args.indexOf(flag); return i < 0 ? null : args.splice(i, flag === "--annotate" || flag === "--allow-none" ? 1 : 2).slice(1)[0] ?? true; };
  const doAnnotate = take("--annotate") !== null;
  const allowNone = take("--allow-none") !== null;
  const repo = take("--repo");
  if (args.length !== 1 || !repo || repo === true) { console.error(USAGE); process.exit(2); }
  let text;
  try { text = readFileSync(args[0], "utf8"); } catch (err) { console.error(`cannot read record: ${err.message}`); process.exit(2); }
  const out = checkRecord(text, repo);
  for (const { block, reason } of out.results) console.log(reason ? `REFUSED ${reason} ADR ${block.adr}` : `OK ADR ${block.adr}`);
  for (const n of out.unbacked) console.log(`REFUSED cited-without-block ADR ${n}`);
  if (out.results.length === 0 && !allowNone) console.log("REFUSED no-blocks");
  console.log(summary(out.results));
  if (doAnnotate) writeFileSync(args[0], annotate(text, out));
  const bad = out.results.some((r) => r.reason) || out.unbacked.length > 0 || (out.results.length === 0 && !allowNone);
  process.exit(bad ? 1 : 0);
}
