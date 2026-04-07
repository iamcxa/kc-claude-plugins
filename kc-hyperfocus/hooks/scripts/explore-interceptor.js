#!/usr/bin/env bun
// Explore Interceptor — PreToolUse hook for Read + Agent(Explore)
//
// Read path: looks up cached insight for the file being read.
//   Hit  → allow + inject prior context as additionalContext
//   Miss → silent exit
//
// Explore path: FTS5 search on keywords from the Explore prompt.
//   >=3 fresh hits → DENY (saves the entire Explore dispatch)
//   <3 fresh but some results → allow + inject partial cache
//   No hits → silent exit
//
// Never crashes — all logic wrapped in try/catch, always exits 0.

import { execFileSync } from "node:child_process";
import { openLake, searchInsights, recordMetric } from "../../lib/context-lake.ts";

/**
 * Strip .worktrees/<name>/ prefix from relative paths so worktree reads
 * match insights stored under the canonical repo-relative path.
 * e.g., ".worktrees/ensign-foo/docs/bar.md" → "docs/bar.md"
 */
function stripWorktreePrefix(relativePath) {
  const match = relativePath.match(/^\.worktrees\/[^/]+\/(.+)$/);
  return match ? match[1] : relativePath;
}

/**
 * Resolve repo root consistently across main context and subagents.
 * CLAUDE_PROJECT_DIR is the authoritative project root — same in main and subagent context.
 * Falls back to git rev-parse from cwd if env var not set.
 */
function resolveRepoRoot(cwd) {
  // Prefer CLAUDE_PROJECT_DIR — consistent across main context and subagents
  const projectDir = process.env.CLAUDE_PROJECT_DIR;
  if (projectDir) {
    try {
      return execFileSync("git", ["rev-parse", "--show-toplevel"], {
        cwd: projectDir,
        encoding: "utf-8",
      }).trim();
    } catch {
      // projectDir might not be a git repo, fall through
    }
  }
  // Fallback to cwd
  return execFileSync("git", ["rev-parse", "--show-toplevel"], {
    cwd,
    encoding: "utf-8",
  }).trim();
}

try {
  const raw = await Bun.stdin.text();
  const input = JSON.parse(raw);

  const toolName = input?.tool_name;
  const toolInput = input?.tool_input;
  const cwd = input?.cwd;
  const sessionId = input?.session_id;

  if (!toolName || !toolInput || !cwd) process.exit(0);

  // --- Read path ---
  if (toolName === "Read") {
    const filePath = toolInput.file_path;
    if (!filePath) process.exit(0);

    // Determine repo root
    let repoRoot;
    try {
      repoRoot = resolveRepoRoot(cwd);
    } catch {
      // Not a git repo — nothing to look up
      process.exit(0);
    }

    // Convert absolute path to relative, strip worktree prefix
    let relativePath = filePath;
    if (filePath.startsWith(repoRoot)) {
      relativePath = filePath.slice(repoRoot.length + 1); // +1 for trailing /
    }
    relativePath = stripWorktreePrefix(relativePath);

    const db = openLake(repoRoot);
    try {
      const results = searchInsights(db, { filePath: relativePath });

      if (results.length > 0) {
        const insight = results[0];

        // Count file lines for savings estimation
        let fileLines = null;
        try {
          const stat = Bun.file(filePath);
          const text = await stat.text();
          fileLines = text.split("\n").length;
        } catch {
          // File might not exist or be unreadable — skip
        }

        recordMetric(db, {
          event: "hit",
          filePath: relativePath,
          details: fileLines != null ? { fileLines } : undefined,
          sessionId: sessionId ?? undefined,
        });

        const snippet =
          insight.content.length > 300
            ? insight.content.slice(0, 300) + "..."
            : insight.content;

        const isAuto = insight.source === "auto";
        const label = isAuto
          ? `Auto-summary for ${relativePath} (upgradeable)`
          : `Prior insight for ${relativePath} (${insight.source}, ${insight.stale ? "stale" : "fresh"})`;
        const suffix = isAuto
          ? "\nThis is an auto-extracted summary. Call store_insight with a richer description to upgrade."
          : "";

        console.log(
          JSON.stringify({
            hookSpecificOutput: {
              hookEventName: "PreToolUse",
              permissionDecision: "allow",
              additionalContext: `[context-lake] ${label}:\n${snippet}${suffix}`,
            },
          })
        );
      } else {
        recordMetric(db, {
          event: "miss",
          filePath: relativePath,
          sessionId: sessionId ?? undefined,
        });
        // Silent exit — no stdout
      }
    } finally {
      db.close();
    }

    process.exit(0);
  }

  // --- Explore path ---
  if (toolName === "Agent" && toolInput.subagent_type === "Explore") {
    const prompt = toolInput.prompt;
    if (!prompt) process.exit(0);

    // Determine repo root
    let repoRoot;
    try {
      repoRoot = resolveRepoRoot(cwd);
    } catch {
      process.exit(0);
    }

    // Extract keywords: strip non-word chars, keep words >3 chars, first 10
    // Filter out common stop words that cause false-positive FTS5 matches
    const STOP_WORDS = new Set([
      "explore", "find", "search", "look", "check", "what", "where", "which",
      "this", "that", "these", "those", "with", "from", "about", "into",
      "have", "does", "their", "them", "they", "will", "would", "could",
      "should", "been", "being", "each", "every", "some", "more", "most",
      "other", "using", "used", "also", "need", "help", "understand",
    ]);

    const keywords = prompt
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length > 3)
      .filter((w) => !STOP_WORDS.has(w.toLowerCase()))
      .slice(0, 10);

    if (keywords.length === 0) process.exit(0);

    // FTS5 query: join keywords with OR for broad match
    const ftsQuery = keywords.join(" OR ");

    const db = openLake(repoRoot);
    try {
      const results = searchInsights(db, { query: ftsQuery });

      if (results.length === 0) {
        recordMetric(db, {
          event: "miss",
          sessionId: sessionId ?? undefined,
        });
        // Silent exit
        process.exit(0);
      }

      // Count fresh results (stale === 0)
      const freshResults = results.filter((r) => r.stale === 0);

      // Always ALLOW Explore — never deny based on keyword matching alone.
      // FTS5 OR queries produce false positives (e.g., "models" matches
      // unrelated dbt insights when user wants to explore a different module).
      // Instead, inject cached insights as additionalContext so Claude can
      // judge relevance and skip redundant exploration on its own.
      const topResults = freshResults.length > 0 ? freshResults : results;
      const fileList = topResults
        .slice(0, 5)
        .map(
          (r) =>
            `  - ${r.filePath} (${r.stale ? "stale" : "fresh"}): ${r.content.slice(0, 80)}`
        )
        .join("\n");

      recordMetric(db, {
        event: "explore_allowed",
        details: {
          totalResults: results.length,
          freshCount: freshResults.length,
          keywords,
        },
        sessionId: sessionId ?? undefined,
      });

      console.log(
        JSON.stringify({
          hookSpecificOutput: {
            hookEventName: "PreToolUse",
            permissionDecision: "allow",
            additionalContext: `[context-lake] Found ${topResults.length} cached insights that may be relevant. Review before exploring — skip if these already cover your question:\n${fileList}`,
          },
        })
      );
    } finally {
      db.close();
    }

    process.exit(0);
  }

  // All other tool_name / subagent_type combos — exit silently
  process.exit(0);
} catch {
  // Never crash — a broken cache hook must never block normal agent operation
  process.exit(0);
}
