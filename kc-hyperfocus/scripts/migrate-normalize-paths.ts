#!/usr/bin/env bun
/**
 * migrate-normalize-paths.ts — One-off migration for context-lake insights.
 *
 * Applies the 2026-04-07 normalizeFilePath contract to existing DB rows:
 * 1. SELECT all insights
 * 2. For each row, compute normalized file_path (relative to repoRoot)
 * 3. UPDATE row if the normalized path differs from stored value
 * 4. Re-sync the FTS5 index for updated rows
 *
 * Idempotent — safe to run multiple times. Uses the same openLake() function
 * the MCP server uses to resolve the DB path.
 *
 * Usage:
 *   cd ~/.claude/plugins/local/kc-hyperfocus
 *   bun scripts/migrate-normalize-paths.ts <repo-root>
 *
 * Example:
 *   bun scripts/migrate-normalize-paths.ts /Users/kent/Project/kc-claude-workspace
 */

import { openLake, normalizeFilePath } from "../lib/context-lake";

const repoRoot = process.argv[2];
if (!repoRoot) {
  console.error("Usage: bun scripts/migrate-normalize-paths.ts <repo-root>");
  process.exit(1);
}

console.log(`[migrate] Opening context lake for: ${repoRoot}`);
const db = openLake(repoRoot);

// Step 1: Fetch all insights
const rows = db
  .query("SELECT id, file_path, content FROM insights ORDER BY id")
  .all() as { id: number; file_path: string; content: string }[];

console.log(`[migrate] Found ${rows.length} insights to inspect`);

let updatedCount = 0;
let skippedCount = 0;

// Step 2+3: Compute normalized path, update if different (in a transaction)
const txn = db.transaction(() => {
  for (const row of rows) {
    const normalized = normalizeFilePath(row.file_path, repoRoot);
    if (normalized === row.file_path) {
      skippedCount++;
      continue;
    }

    console.log(
      `[migrate] id=${row.id}:\n  BEFORE: ${row.file_path}\n  AFTER:  ${normalized}`
    );

    // Check if the normalized path already exists in the DB (conflict) —
    // this can happen if two rows were stored with different normalizations
    // of the same file (e.g. one absolute, one relative).
    const conflict = db
      .query("SELECT id FROM insights WHERE file_path = ? AND id != ?")
      .get(normalized, row.id) as { id: number } | null;

    if (conflict) {
      console.log(
        `[migrate] id=${row.id}: CONFLICT — normalized path already owned by id=${conflict.id}, deleting old row`
      );
      // Remove FTS entry for the duplicate row
      db.query(
        "INSERT INTO insights_fts(insights_fts, rowid, file_path, content) VALUES('delete', ?, ?, ?)"
      ).run(row.id, row.file_path, row.content);
      db.query("DELETE FROM insights WHERE id = ?").run(row.id);
      updatedCount++;
      continue;
    }

    // Step 4: UPDATE + re-sync FTS index
    // Delete old FTS entry (keyed by rowid)
    db.query(
      "INSERT INTO insights_fts(insights_fts, rowid, file_path, content) VALUES('delete', ?, ?, ?)"
    ).run(row.id, row.file_path, row.content);

    // Update the insights row
    db.query(
      "UPDATE insights SET file_path = ?, updated_at = datetime('now') WHERE id = ?"
    ).run(normalized, row.id);

    // Insert new FTS entry with the normalized path
    db.query(
      "INSERT INTO insights_fts(rowid, file_path, content) VALUES(?, ?, ?)"
    ).run(row.id, normalized, row.content);

    updatedCount++;
  }
});

txn();

console.log(`[migrate] Done: ${updatedCount} updated, ${skippedCount} already canonical`);
db.close();
