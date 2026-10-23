import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const bin = join(dirname(fileURLToPath(import.meta.url)), "../bin/check-citations.mjs");
const sh = (cwd, ...args) => execFileSync("git", args, { cwd, encoding: "utf8" }).trim();

function projectClone() {
  const dir = mkdtempSync(join(tmpdir(), "cite-"));
  sh(dir, "init", "-q", "-b", "main");
  sh(dir, "config", "user.email", "t@example.invalid");
  sh(dir, "config", "user.name", "t");
  sh(dir, "remote", "add", "origin", "https://github.com/o/relay.git");
  mkdirSync(join(dir, "docs/adr"), { recursive: true });
  const adr = (n, title, status) => `# ${n}. ${title}\n\nDate: 2026-01-01\n\n## Status\n\n${status}\n\n## Context\n\nc\n`;
  writeFileSync(join(dir, "docs/adr/0060-ceiling.md"), adr("0060", "ceiling", "Accepted"));
  writeFileSync(join(dir, "docs/adr/0003-old.md"), adr("0003", "old", "Superseded by 0021"));
  sh(dir, "add", "-A");
  sh(dir, "commit", "-q", "-m", "adrs");
  return { dir, commit: sh(dir, "rev-parse", "HEAD") };
}
const digestOf = (dir, path) => `sha256:${createHash("sha256").update(readFileSync(join(dir, path))).digest("hex")}`;

function record({ commit, blocks, options = "1. Hold [ADR 0060]." }) {
  const body = blocks.map((b) => `### ADR ${b.adr}\n- path: ${b.path}\n- digest: ${b.digest}\n- status: ${b.status ?? "Accepted"}${b.commit ? `\n- commit: ${b.commit}` : ""}\n`).join("\n");
  return `# ops: test\n\n## Options\n\n${options}\n\n## Rulings cited\n\nRepository: o/relay\nCommit: ${commit}\n\n${body}\n## Measures\n\nx\n`;
}

function run(dir, text, extra = []) {
  const file = join(mkdtempSync(join(tmpdir(), "rec-")), "record.md");
  writeFileSync(file, text);
  const r = spawnSync("node", [bin, file, "--repo", dir, ...extra], { encoding: "utf8" });
  return { status: r.status, out: r.stdout, file };
}

test("the true block passes, each of four faults is refused with its own reason", () => {
  const { dir, commit } = projectClone();
  const good = { adr: "0060", path: "docs/adr/0060-ceiling.md", digest: digestOf(dir, "docs/adr/0060-ceiling.md") };
  assert.equal(run(dir, record({ commit, blocks: [good] })).status, 0);

  const faults = {
    "digest-mismatch": { ...good, digest: "sha256:" + "0".repeat(64) },
    "path-missing": { ...good, path: "docs/adr/0099-nope.md" },
    "commit-missing": { ...good, commit: "1".repeat(40) },
    "not-in-force(Superseded by 0021)": { adr: "0003", path: "docs/adr/0003-old.md", digest: digestOf(dir, "docs/adr/0003-old.md"), status: "Superseded by 0021" },
  };
  for (const [reason, block] of Object.entries(faults)) {
    const r = run(dir, record({ commit, blocks: [block], options: `1. Hold [ADR ${block.adr}].` }));
    assert.equal(r.status, 1, reason);
    assert.match(r.out, new RegExp(`REFUSED ${reason.replace(/[()]/g, "\\$&")} ADR ${block.adr}`), reason);
  }
});

test("one refused block among good ones fails the record, and annotate marks only that block and its option", () => {
  const { dir, commit } = projectClone();
  const good = { adr: "0060", path: "docs/adr/0060-ceiling.md", digest: digestOf(dir, "docs/adr/0060-ceiling.md") };
  const bad = { adr: "0003", path: "docs/adr/0003-old.md", digest: digestOf(dir, "docs/adr/0003-old.md"), status: "Superseded by 0021" };
  const r = run(dir, record({ commit, blocks: [good, bad], options: "1. A [ADR 0060]. 2. B [ADR 0003]." }), ["--annotate"]);
  assert.equal(r.status, 1);
  assert.match(r.out, /Citations: 1 OK, 1 REFUSED\./);
  const text = readFileSync(r.file, "utf8");
  assert.match(text, /### ADR 0060\n- check: OK\n/);
  assert.match(text, /### ADR 0003\n- check: REFUSED not-in-force\(Superseded by 0021\)\n/);
  assert.match(text, /2\. B \[ADR 0003 REFUSED\]\./);
  assert.match(text, /1\. A \[ADR 0060\]\./);
});

test("a ruling cited in the options without a block is refused", () => {
  const { dir, commit } = projectClone();
  const good = { adr: "0060", path: "docs/adr/0060-ceiling.md", digest: digestOf(dir, "docs/adr/0060-ceiling.md") };
  const r = run(dir, record({ commit, blocks: [good], options: "1. A [ADR 0060]. 2. B [ADR 0099]." }));
  assert.equal(r.status, 1);
  assert.match(r.out, /REFUSED cited-without-block ADR 0099/);
});

test("a record naming another repository than the clone's origin is refused", () => {
  const { dir, commit } = projectClone();
  const good = { adr: "0060", path: "docs/adr/0060-ceiling.md", digest: digestOf(dir, "docs/adr/0060-ceiling.md") };
  const r = run(dir, record({ commit, blocks: [good] }).replace("Repository: o/relay", "Repository: o/other"));
  assert.equal(r.status, 1);
  assert.match(r.out, /REFUSED repo-mismatch ADR 0060/);
});

test("a record with no blocks is refused unless --allow-none", () => {
  const { dir, commit } = projectClone();
  const none = record({ commit, blocks: [], options: "1. Hold." });
  assert.equal(run(dir, none).status, 1);
  assert.equal(run(dir, none, ["--allow-none"]).status, 0);
});

test("a usage error exits 2", () => {
  assert.equal(spawnSync("node", [bin], { encoding: "utf8" }).status, 2);
});

test("status is judged at the cited commit and again at the clone's head", () => {
  const { dir, commit } = projectClone();
  const path = "docs/adr/0060-ceiling.md";
  const atCommit = { adr: "0060", path, digest: digestOf(dir, path) };
  writeFileSync(join(dir, path), readFileSync(join(dir, path), "utf8").replace("Accepted", "Superseded by 0061"));
  sh(dir, "commit", "-q", "-am", "supersede");
  const laterHead = run(dir, record({ commit, blocks: [atCommit] }));
  assert.equal(laterHead.status, 1);
  assert.match(laterHead.out, /REFUSED not-in-force\(Superseded by 0061\) ADR 0060/);

  writeFileSync(join(dir, path), readFileSync(join(dir, path), "utf8").replace("Superseded by 0061", "Proposed"));
  sh(dir, "commit", "-q", "-am", "proposed");
  const proposed = sh(dir, "rev-parse", "HEAD");
  const accepted = readFileSync(join(dir, path), "utf8").replace("Proposed", "Accepted");
  writeFileSync(join(dir, path), accepted);
  sh(dir, "commit", "-q", "-am", "accept");
  const acceptedLater = run(dir, record({ commit: proposed, blocks: [{ adr: "0060", path, digest: `sha256:${createHash("sha256").update(execFileSync("git", ["show", `${proposed}:${path}`], { cwd: dir })).digest("hex")}`, status: "Proposed" }] }));
  assert.equal(acceptedLater.status, 1);
  assert.match(acceptedLater.out, /REFUSED not-in-force\(Proposed\) ADR 0060/);
});
