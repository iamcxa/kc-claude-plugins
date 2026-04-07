#!/usr/bin/env bun
// Read Tracker — PostToolUse:Read hook
//
// 1. Records file paths read during a session to /tmp/claude-lake-touched-{session_id}.json.
//    This data is consumed by session-handoff to know which files the agent explored.
//
// 2. Checks context lake for cached insight. Tracks uncached-read count.
//
// 3. When uncached reads cross a threshold, nudges Claude to cache insights
//    for the most-read uncached modules.
//
// Silent unless nudge threshold crossed. Always exits 0.

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { openLake, searchInsights, recordMetric, storeInsight } from "../../lib/context-lake.ts";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const NUDGE_FIRST = 15; // uncached reads before first nudge
const NUDGE_INTERVAL = 30; // uncached reads between subsequent nudges
const NUDGE_MAX = 3; // max nudges per session

const SKIP_EXTENSIONS = new Set([
  ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
  ".pdf",
  ".zip", ".tar", ".gz", ".tgz", ".bz2", ".7z", ".rar",
  ".lock", ".lockb",
  ".woff", ".woff2", ".ttf", ".eot",
  ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv",
]);

const SKIP_LOCK_FILES = new Set([
  "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
]);

const SKIP_PATH_PREFIXES = [
  ".planning/",
  ".claude/",
  ".git/",
  "node_modules/",
  ".worktrees/",
  ".superpowers/",
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function resolveRepoRoot(cwd) {
  const projectDir = process.env.CLAUDE_PROJECT_DIR;
  if (projectDir) {
    try {
      return execFileSync("git", ["rev-parse", "--show-toplevel"], {
        cwd: projectDir,
        encoding: "utf-8",
      }).trim();
    } catch {
      // fall through
    }
  }
  return execFileSync("git", ["rev-parse", "--show-toplevel"], {
    cwd,
    encoding: "utf-8",
  }).trim();
}

function toRelativePath(filePath, repoRoot) {
  let rel = filePath;
  if (filePath.startsWith(repoRoot + "/")) {
    rel = filePath.slice(repoRoot.length + 1);
  }
  return stripWorktreePrefix(rel);
}

/**
 * Strip .worktrees/<name>/ prefix so worktree reads match canonical paths.
 * e.g., ".worktrees/ensign-foo/docs/bar.md" → "docs/bar.md"
 */
function stripWorktreePrefix(relativePath) {
  const match = relativePath.match(/^\.worktrees\/[^/]+\/(.+)$/);
  return match ? match[1] : relativePath;
}

function isCodePath(relativePath) {
  // Skip absolute paths (outside repo, e.g., GSD workflows, plugin references)
  if (relativePath.startsWith("/")) return false;
  // Skip known non-code prefixes
  if (SKIP_PATH_PREFIXES.some((p) => relativePath.startsWith(p))) return false;
  return true;
}

// ---------------------------------------------------------------------------
// Auto-extract: lightweight insight from file content
// ---------------------------------------------------------------------------

const MAX_SCAN_LINES = 50;
const MAX_INSIGHT_CHARS = 600;

// Patterns that indicate structural declarations across languages
const DECLARATION_RE =
  /^(?:export\s+(?:default\s+)?(?:function|class|const|let|type|interface|enum)|(?:def|class|async def)\s+\w|(?:func|fn)\s+\w|pub\s+(?:fn|struct|enum|trait)\s+\w)/;

function autoExtract(filePath) {
  try {
    const text = readFileSync(filePath, "utf8");
    const lines = text.split("\n").slice(0, MAX_SCAN_LINES);

    const parts = [];

    // 1. Extract leading comment block (first consecutive comment lines)
    const commentLines = [];
    let inBlock = false;
    for (const line of lines) {
      const trimmed = line.trim();
      if (!inBlock && commentLines.length === 0) {
        // Skip shebangs and empty lines at top
        if (trimmed === "" || trimmed.startsWith("#!")) continue;
        if (
          trimmed.startsWith("//") ||
          trimmed.startsWith("/*") ||
          trimmed.startsWith("*") ||
          trimmed.startsWith('"""') ||
          trimmed.startsWith("#")
        ) {
          inBlock = trimmed.startsWith("/*") && !trimmed.includes("*/");
          commentLines.push(trimmed);
          continue;
        }
        break; // First non-comment line — stop
      }
      if (inBlock) {
        commentLines.push(trimmed);
        if (trimmed.includes("*/")) inBlock = false;
        continue;
      }
      if (
        trimmed.startsWith("//") ||
        trimmed.startsWith("*") ||
        trimmed.startsWith("#")
      ) {
        commentLines.push(trimmed);
        continue;
      }
      break;
    }

    if (commentLines.length > 0) {
      parts.push(commentLines.slice(0, 8).join("\n"));
    }

    // 2. Extract declarations (exports, functions, classes)
    const decls = [];
    for (const line of lines) {
      if (DECLARATION_RE.test(line.trim())) {
        // Clean up: take signature only (strip body opener)
        const sig = line.trim().replace(/\s*\{.*$/, "").replace(/\s*:.*$/, "");
        if (sig.length > 10) decls.push(sig);
      }
    }
    if (decls.length > 0) {
      parts.push("Declarations: " + decls.slice(0, 10).join(", "));
    }

    if (parts.length === 0) return null;

    let content = parts.join("\n");
    if (content.length > MAX_INSIGHT_CHARS) {
      content = content.slice(0, MAX_INSIGHT_CHARS) + "…";
    }
    return content;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

try {
  const raw = await Bun.stdin.text();
  const input = JSON.parse(raw);

  const filePath = input?.tool_input?.file_path;
  const sessionId = input?.session_id;
  const cwd = input?.cwd;

  if (!filePath || !sessionId) process.exit(0);

  // Skip non-code extensions
  const dotIdx = filePath.lastIndexOf(".");
  const ext = dotIdx !== -1 ? filePath.slice(dotIdx).toLowerCase() : "";
  if (SKIP_EXTENSIONS.has(ext)) process.exit(0);

  // Skip lock files
  const basename = filePath.slice(filePath.lastIndexOf("/") + 1);
  if (SKIP_LOCK_FILES.has(basename)) process.exit(0);

  // Load session state
  const touchedPath = `/tmp/claude-lake-touched-${sessionId}.json`;
  let data = { files: [], uncachedCount: 0, lastNudgeAt: 0, nudgeCount: 0 };
  try {
    const existing = JSON.parse(readFileSync(touchedPath, "utf8"));
    data.files = Array.isArray(existing.files) ? existing.files : [];
    data.uncachedCount =
      typeof existing.uncachedCount === "number" ? existing.uncachedCount : 0;
    data.lastNudgeAt =
      typeof existing.lastNudgeAt === "number" ? existing.lastNudgeAt : 0;
    data.nudgeCount =
      typeof existing.nudgeCount === "number" ? existing.nudgeCount : 0;
  } catch {
    // File doesn't exist yet — use defaults
  }

  // Record touched file (deduplicated)
  if (!data.files.includes(filePath)) {
    data.files.push(filePath);
  }

  // Resolve repo root for cache lookup
  let repoRoot;
  try {
    repoRoot = resolveRepoRoot(cwd);
  } catch {
    // Not a git repo — save touched list, skip cache logic
    writeFileSync(touchedPath, JSON.stringify(data));
    process.exit(0);
  }

  const relativePath = toRelativePath(filePath, repoRoot);

  // Only track cache status for code paths
  if (isCodePath(relativePath)) {
    const db = openLake(repoRoot);
    try {
      const results = searchInsights(db, { filePath: relativePath });
      if (results.length === 0) {
        data.uncachedCount++;

        // Auto-extract: store a lightweight insight so future reads are cache hits.
        // source: "auto" (priority 0) — any manual/handoff/journal write overwrites.
        const content = autoExtract(filePath);
        if (content) {
          let gitHash = "";
          try {
            gitHash = execFileSync("git", ["rev-parse", "HEAD"], {
              cwd: repoRoot,
              encoding: "utf-8",
            }).trim();
          } catch {
            // Non-critical — store without hash
          }
          storeInsight(db, {
            filePath: relativePath,
            content,
            source: "auto",
            gitHash,
          }, repoRoot);
        }
      }
    } finally {
      db.close();
    }
  }

  // Save state before potential nudge
  writeFileSync(touchedPath, JSON.stringify(data));

  // Check nudge threshold
  if (data.nudgeCount >= NUDGE_MAX) process.exit(0);

  const threshold =
    data.lastNudgeAt === 0 ? NUDGE_FIRST : data.lastNudgeAt + NUDGE_INTERVAL;

  if (data.uncachedCount >= threshold) {
    // Find uncached code files from this session
    const codePaths = data.files
      .map((f) => toRelativePath(f, repoRoot))
      .filter(isCodePath);

    if (codePaths.length === 0) process.exit(0);

    // Find files with auto-only insights (upgradeable) or no insights at all
    const db = openLake(repoRoot);
    try {
      const placeholders = codePaths.map(() => "?").join(",");
      const cachedRows = db
        .query(
          `SELECT file_path, source FROM insights WHERE file_path IN (${placeholders})`
        )
        .all(...codePaths);
      const cachedMap = new Map(cachedRows.map((r) => [r.file_path, r.source]));

      // Files with auto insights that could be upgraded
      const autoOnlyPaths = codePaths.filter((f) => cachedMap.get(f) === "auto");
      // Files with no insight at all (auto-extract may have failed)
      const uncachedPaths = codePaths.filter((f) => !cachedMap.has(f));

      const upgradeable = [...autoOnlyPaths, ...uncachedPaths];
      if (upgradeable.length === 0) process.exit(0);

      const topFiles = upgradeable.slice(0, 5);
      const remaining = upgradeable.length - topFiles.length;
      const fileList = topFiles
        .map((f) => {
          const src = cachedMap.get(f);
          return src === "auto" ? `  - ${f} (auto — upgrade)` : `  - ${f} (no cache)`;
        })
        .join("\n");
      const remainingSummary =
        remaining > 0
          ? `\n  (+ ${remaining} more)`
          : "";

      // Record nudge metric
      recordMetric(db, {
        event: "nudge",
        details: {
          autoFiles: autoOnlyPaths.length,
          uncachedFiles: uncachedPaths.length,
          topFiles,
          sessionNudgeCount: data.nudgeCount + 1,
        },
        sessionId: sessionId ?? undefined,
      });

      // Update nudge state
      data.lastNudgeAt = data.uncachedCount;
      data.nudgeCount++;
      writeFileSync(touchedPath, JSON.stringify(data));

      const exampleFile = topFiles[0];

      process.stdout.write(
        JSON.stringify({
          hookSpecificOutput: {
            hookEventName: "PostToolUse",
            additionalContext: [
              `[context-lake] ${upgradeable.length} files have auto-generated or missing insights. Upgrade the most important ones:`,
              fileList + remainingSummary,
              `Call store_insight with: file_path, content (English, 3-8 sentences: purpose, key patterns, dependencies, gotchas), source: "manual".`,
              `Example — store_insight({ file_path: "${exampleFile}", content: "...", source: "manual" })`,
              `Upgrade top 3 when you have a natural pause, then continue your work.`,
            ].join("\n"),
          },
        })
      );
    } finally {
      db.close();
    }
  }
} catch {
  // Never crash — silent exit
}

process.exit(0);
