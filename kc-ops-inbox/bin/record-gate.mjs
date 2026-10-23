#!/usr/bin/env node
// Records the gate from the Captain's decision on the head commit. Writes only the state branch,
// so the head does not move and the decision stands.
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { client } from "./lib/github.mjs";

const WORKFLOW_DIR = "docs/ops";
const DECISIONS = { APPROVED: "approve", CHANGES_REQUESTED: "revise", COMMENTED: "revise" };

// A Comment review decides only when it names exactly one option; otherwise it is a question and the gate stays open, because `gate record` closes the attempt.
export const namedOption = (body) => {
  const found = new Set([...(body ?? "").matchAll(/\boption\s*([1-9])\b/gi)].map((m) => m[1]));
  return found.size === 1 ? [...found][0] : null;
};

// The latest review by the Captain that is on the current head and decides something.
export function pickReview(reviews, captain, headSha) {
  const rows = reviews.filter((r) => r.user?.login === captain && r.commit_id === headSha && Object.hasOwn(DECISIONS, r.state) && (r.state !== "COMMENTED" || namedOption(r.body)));
  return rows.length ? rows[rows.length - 1] : null;
}

async function allReviews(gh, project, pr) {
  const out = [];
  for (let page = 1; page < 20; page += 1) {
    const r = await gh("GET", `/repos/${project}/pulls/${pr}/reviews?per_page=100&page=${page}`);
    if (r.status !== 200) throw new Error(`reviews-read-${r.status}`);
    out.push(...r.json);
    if (r.json.length < 100) return out;
  }
  return out;
}

const exec = (cmd, args, opts = {}) => {
  const r = spawnSync(cmd, args, { encoding: "utf8", ...opts });
  if (r.status !== 0 && !opts.allowFail) throw new Error(`${cmd} ${args[0]} failed (${r.status}): ${(r.stderr || r.stdout || "").trim().slice(0, 400)}`);
  return r;
};

export async function recordGate(env = process.env, cwd = process.cwd()) {
  const { PROJECT_REPO: project, PR_NUMBER: number, OPS_CAPTAIN_LOGIN: captain } = env;
  if (!project || !number || !captain) throw new Error("PROJECT_REPO, PR_NUMBER and OPS_CAPTAIN_LOGIN are required");
  const sdBin = env.SPACEDOCK_BIN || "spacedock";
  const gh = client(env, env.GITHUB_TOKEN);

  const pr = await gh("GET", `/repos/${project}/pulls/${number}`);
  if (pr.status !== 200) throw new Error(`pull-read-${pr.status}`);
  const ref = pr.json.head.ref;
  if (!ref.startsWith("ops/")) return { result: "no-op", why: `branch ${ref} is not ops/*` };
  if (pr.json.state !== "open") return { result: "no-op", why: "pull request is not open" };
  const slug = ref.slice(4);
  const head = pr.json.head.sha;

  const review = pickReview(await allReviews(gh, project, number), captain, head);
  if (!review) return { result: "no-op", why: `no review by ${captain} on ${head}` };

  const sd = (args, opts = {}) => exec(sdBin, [...args, "--workflow-dir", WORKFLOW_DIR], { cwd, ...opts });
  exec("git", ["config", "user.name", "ops-gate"], { cwd });
  exec("git", ["config", "user.email", "ops-gate@users.noreply.github.com"], { cwd });
  const gitDir = join(cwd, ".git/info/exclude");
  if (existsSync(gitDir)) writeFileSync(gitDir, `${readFileSync(gitDir, "utf8")}\n${WORKFLOW_DIR}/.spacedock-state/\n`);
  if (!existsSync(join(cwd, WORKFLOW_DIR, ".spacedock-state"))) {
    exec("git", ["fetch", "-q", "--depth", "1", "origin", "+spacedock-state/ops:refs/heads/spacedock-state/ops"], { cwd });
    sd(["state", "init"]);
  }

  const next = JSON.parse(sd(["status", "--next", "--json"]).stdout);
  const awaiting = (next.ready_gates ?? []).some((g) => g.slug === slug && g.readiness === "awaiting-captain");
  if (!awaiting) return { result: "no-op", why: `gate for ${slug} is not awaiting the Captain` };

  const taskDir = join(cwd, WORKFLOW_DIR, ".spacedock-state", slug);
  const measuresFile = join(taskDir, "measures.json");
  const measures = existsSync(measuresFile) ? JSON.parse(readFileSync(measuresFile, "utf8")) : {};
  const decision = DECISIONS[review.state];
  const followed = review.state === "APPROVED" ? "yes" : "no";
  const words = (review.body ?? "").split(/\s+/).filter(Boolean).join(" ") || "(no comment)";
  const seconds = measures.received && measures.recommended ? Math.round((Date.parse(measures.recommended) - Date.parse(measures.received)) / 1000) : null;
  const reason = `GitHub review ${review.id} by ${captain} on ${head}: ${words} | received ${measures.received ?? "unknown"}; recommended ${measures.recommended ?? "unknown"}; seconds-to-recommendation ${seconds ?? "unknown"}; followed ${followed}`;

  sd(["gate", "record", slug, "--decision", decision, "--actor", "person:captain", "--reason", reason]);
  writeFileSync(measuresFile, `${JSON.stringify({ ...measures, review: review.id, decision, followed, seconds_to_recommendation: seconds }, null, 2)}\n`);
  sd(["state", "commit", slug]);
  return { result: "recorded", slug, review: review.id, decision, followed, seconds };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  recordGate().then((r) => console.log(JSON.stringify(r)), (err) => {
    console.error(`record-gate failed: ${err.message}`);
    process.exit(1);
  });
}
