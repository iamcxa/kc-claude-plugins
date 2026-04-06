#!/usr/bin/env bun
/**
 * stale-checker.js — SessionStart hook
 *
 * Runs at session start to maintain Context Lake freshness:
 * 1. Invalidate insights for files changed in recent commits
 * 2. Cold-evict ancient/idle insights
 * 3. Sync technical insights from private journal entries (last 3 days)
 *
 * Never crashes — all errors caught and silently swallowed (exit 0).
 * No stdout output (silent hook).
 */

import { openLake, invalidateStale, coldEvict, storeInsight } from "../../lib/context-lake.ts";
import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";

// ---------------------------------------------------------------------------
// Stdin reader (async, same pattern as other hooks)
// ---------------------------------------------------------------------------

let input = "";
const stdinTimeout = setTimeout(() => process.exit(0), 3000);
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
  clearTimeout(stdinTimeout);
  let result = null;
  try {
    result = main(input);
  } catch {
    // Never crash
  }
  if (result) {
    process.stdout.write(JSON.stringify(result));
  }
  process.exit(0);
});

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

/**
 * Resolve repo root consistently across main context and subagents.
 * CLAUDE_PROJECT_DIR is the authoritative project root.
 */
function resolveRepoRoot(cwd) {
  const projectDir = process.env.CLAUDE_PROJECT_DIR;
  if (projectDir) {
    try {
      return execFileSync("git", ["rev-parse", "--show-toplevel"], {
        cwd: projectDir,
        encoding: "utf-8",
      }).trim();
    } catch { /* fall through */ }
  }
  return execFileSync("git", ["rev-parse", "--show-toplevel"], {
    cwd,
    encoding: "utf-8",
  }).trim();
}

function main(rawInput) {
  const data = JSON.parse(rawInput || "{}");
  const cwd = data.cwd || process.cwd();

  // Step 1: Detect repo root
  const repoRoot = resolveRepoRoot(cwd);

  // Get current git hash
  const gitHash = execFileSync("git", ["rev-parse", "HEAD"], {
    cwd,
    encoding: "utf-8",
  })
    .trim()
    .slice(0, 12);

  // Step 2: Open DB
  const db = openLake(repoRoot);

  // Step 3: Invalidate stale insights for recently changed files
  try {
    const diffOutput = execFileSync(
      "git",
      ["diff", "--name-only", "HEAD~10..HEAD"],
      { cwd, encoding: "utf-8" }
    ).trim();

    if (diffOutput) {
      const changedFiles = diffOutput
        .split("\n")
        .map((f) => f.trim())
        .filter(Boolean)
        .map((f) => resolve(repoRoot, f));
      invalidateStale(db, changedFiles);
    }
  } catch {
    // git diff may fail if fewer than 10 commits — that's fine
  }

  // Step 4: Cold eviction
  coldEvict(db, { maxAgeDays: 30, minIdleDays: 7 });

  // Step 5: Journal sync — scan last 3 days
  syncJournalInsights(db, gitHash);

  // Step 6: Close DB
  db.close();

  // Step 7: Detect pending handoffs from recent journal entries
  const projectDir = process.env.CLAUDE_PROJECT_DIR || cwd;
  const handoff = detectPendingHandoff(projectDir);
  if (handoff) {
    return {
      additionalContext: `Previous session handoff detected: ${handoff.description} (${handoff.date}). User can resume with: resume ${handoff.id}`,
      systemMessage: `Pending handoff: ${handoff.description}\n  resume ${handoff.id}`,
    };
  }
  return null;
}

// ---------------------------------------------------------------------------
// Handoff detection
// ---------------------------------------------------------------------------

/**
 * Scans recent journal entries for "Session Handoff:" markers.
 * Returns the most recent handoff found (last 3 days), or null.
 */
function detectPendingHandoff(projectDir) {
  try {
    const journalDir = join(projectDir, ".private-journal");
    if (!existsSync(journalDir)) return null;

    const now = new Date();
    for (let i = 0; i < 3; i++) {
      const d = new Date(now);
      d.setDate(d.getDate() - i);
      const dateStr = d.toISOString().slice(0, 10);
      const dayPath = join(journalDir, dateStr);
      if (!existsSync(dayPath)) continue;

      let entries;
      try {
        entries = readdirSync(dayPath)
          .filter((f) => f.endsWith(".md"))
          .sort()
          .reverse(); // newest first
      } catch {
        continue;
      }

      for (const entry of entries) {
        try {
          const content = readFileSync(join(dayPath, entry), "utf-8");
          if (!content.includes("Session Handoff:")) continue;

          const handoffMatch = content.match(/Session Handoff:\s*(.+)/);
          if (!handoffMatch) continue;

          const id = `${dateStr}/${entry.replace(".md", "")}`;
          const description = handoffMatch[1].trim();
          return { id, date: dateStr, description };
        } catch {
          continue;
        }
      }
    }
    return null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Journal sync
// ---------------------------------------------------------------------------

/**
 * Scans ~/.private-journal/ for entries from the last 3 days.
 * Parses "## Technical Insights" sections and extracts file-associated insights.
 */
function syncJournalInsights(db, gitHash) {
  try {
    const home = process.env.HOME || process.env.USERPROFILE || "/tmp";
    const journalDir = join(home, ".private-journal");

    if (!existsSync(journalDir)) return;

    // Compute date range: last 3 days
    const now = new Date();
    const dateDirs = [];
    for (let i = 0; i < 3; i++) {
      const d = new Date(now);
      d.setDate(d.getDate() - i);
      const dateStr = d.toISOString().slice(0, 10); // YYYY-MM-DD
      dateDirs.push(dateStr);
    }

    for (const dateDir of dateDirs) {
      const dayPath = join(journalDir, dateDir);
      if (!existsSync(dayPath)) continue;

      let entries;
      try {
        entries = readdirSync(dayPath).filter((f) => f.endsWith(".md"));
      } catch {
        continue;
      }

      for (const entry of entries) {
        try {
          const content = readFileSync(join(dayPath, entry), "utf-8");
          const insights = extractTechnicalInsights(content);

          for (const insight of insights) {
            for (const filePath of insight.filePaths) {
              storeInsight(db, {
                filePath,
                content: insight.text,
                source: "journal",
                gitHash,
              });
            }
          }
        } catch {
          // Skip unreadable entries
        }
      }
    }
  } catch {
    // Best-effort — skip entirely on any error
  }
}

// ---------------------------------------------------------------------------
// Parsing helpers
// ---------------------------------------------------------------------------

/**
 * Extracts the "## Technical Insights" section from a journal markdown file.
 * Returns an array of { text, filePaths } for each insight paragraph
 * that references at least one file path.
 */
function extractTechnicalInsights(markdown) {
  // Find "## Technical Insights" section — capture everything until the next ## heading or EOF
  const sectionMatch = markdown.match(
    /## Technical Insights\n([\s\S]*?)(?=\n## |\n---\s*$|$)/
  );
  if (!sectionMatch) return [];

  const sectionBody = sectionMatch[1].trim();
  if (!sectionBody) return [];

  // Split into paragraphs (separated by blank lines)
  const paragraphs = sectionBody.split(/\n\n+/).filter(Boolean);

  const results = [];
  for (const para of paragraphs) {
    const filePaths = extractFilePaths(para);
    if (filePaths.length > 0) {
      results.push({ text: para.trim(), filePaths });
    }
  }

  return results;
}

/**
 * Extracts file paths from text. Looks for:
 * 1. Backtick-wrapped paths: `path/to/file.ext` or `/absolute/path/to/file.ext`
 * 2. Explicit path patterns: words containing / and a file extension
 */
function extractFilePaths(text) {
  const paths = new Set();

  // Pattern 1: backtick-wrapped paths with extensions
  const backtickPaths = text.matchAll(
    /`([^`]*\/[^`]*\.(?:ts|js|py|md|yaml|yml|json|toml|sh|css|html|tsx|jsx|sql|rs|go))`/g
  );
  for (const m of backtickPaths) {
    paths.add(m[1]);
  }

  // Pattern 2: bare paths with / and extension (not inside backticks)
  const barePaths = text.matchAll(
    /(?:^|\s)((?:\/|\.\/|~\/)?[\w\-.]+(?:\/[\w\-.]+)+\.(?:ts|js|py|md|yaml|yml|json|toml|sh|css|html|tsx|jsx|sql|rs|go))(?:\s|$|[),;:])/gm
  );
  for (const m of barePaths) {
    paths.add(m[1]);
  }

  return [...paths];
}
