#!/usr/bin/env node
// Walks the import closure of the inbox core and prints every import that leaves the package.
// Exit 0 when the only external import is node:crypto, 1 otherwise, 2 on a usage error.
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2] ?? join(here, ".."));
const ALLOWED = new Set(["node:crypto"]);
const entries = readdirSync(join(root, "core")).filter((f) => f.endsWith(".mjs")).map((f) => join(root, "core", f));
if (entries.length === 0) { console.error("usage: node import-closure.mjs [package-root]"); process.exit(2); }

const external = new Set();
const seen = new Set();
const walk = (file) => {
  if (seen.has(file)) return;
  seen.add(file);
  const text = readFileSync(file, "utf8");
  const specs = [...text.matchAll(/^\s*(?:import|export)\b[^;]*?\bfrom\s*["']([^"']+)["']/gms)].map((m) => m[1]);
  specs.push(...[...text.matchAll(/^\s*import\s*["']([^"']+)["']/gm)].map((m) => m[1]));
  specs.push(...[...text.matchAll(/\bimport\s*\(\s*([^)]*)\)/g)].map((m) => `dynamic:${m[1].trim()}`));
  for (const spec of specs) {
    if (spec.startsWith("./") || spec.startsWith("../")) walk(resolve(dirname(file), spec));
    else external.add(spec);
  }
};
entries.forEach(walk);
for (const spec of [...external].sort()) console.log(spec);
process.exit([...external].every((s) => ALLOWED.has(s)) ? 0 : 1);
