/**
 * context-lake.ts — Shared SQLite module for Context Lake POC.
 *
 * Provides DB lifecycle (openLake), insight CRUD (storeInsight, searchInsights),
 * with FTS5 full-text search and source-priority conflict resolution.
 *
 * DB driver: bun:sqlite (zero dependency, FTS5 included).
 */

import { Database } from "bun:sqlite";
import { mkdirSync } from "node:fs";
import { basename, join } from "node:path";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Insight {
  id: number;
  filePath: string;
  content: string;
  source: string;
  sourceSession: string | null;
  sourceModel: string | null;
  gitHash: string;
  stale: number;
  createdAt: string;
  updatedAt: string;
}

export interface StoreInsightInput {
  filePath: string;
  content: string;
  source: string;
  sourceSession?: string;
  sourceModel?: string;
  gitHash: string;
}

export interface SearchInsightsInput {
  query?: string;
  filePath?: string;
  freshnessDays?: number;
}

export interface MetricParams {
  event: string;
  filePath?: string;
  details?: Record<string, any>;
  sessionId?: string;
}

export interface MetricsSummary {
  totalHits: number;
  totalMisses: number;
  totalStores: number;
  totalExploreHints: number;
  hitRate: number | null;
}

export interface ColdEvictOptions {
  maxAgeDays?: number;
  minIdleDays?: number;
}

// ---------------------------------------------------------------------------
// Source priority: higher number = higher priority
// ---------------------------------------------------------------------------

export const SOURCE_PRIORITY: Record<string, number> = {
  manual: 3,
  handoff: 2,
  journal: 1,
};

// ---------------------------------------------------------------------------
// Schema DDL
// ---------------------------------------------------------------------------

const SCHEMA_DDL = `
CREATE TABLE IF NOT EXISTS insights (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_path TEXT NOT NULL UNIQUE,
  content TEXT NOT NULL,
  source TEXT NOT NULL,
  source_session TEXT,
  source_model TEXT,
  git_hash TEXT NOT NULL,
  stale INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_insights_file ON insights(file_path);

CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event TEXT NOT NULL,
  file_path TEXT,
  details TEXT,
  session_id TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_metrics_event ON metrics(event);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(created_at);
`;

// FTS5 virtual tables don't support IF NOT EXISTS, so we check first.
const FTS_DDL = `
CREATE VIRTUAL TABLE insights_fts USING fts5(
  file_path, content,
  content=insights, content_rowid=id
);
`;

// ---------------------------------------------------------------------------
// openLake
// ---------------------------------------------------------------------------

interface OpenLakeOptions {
  /** Override the base directory (default: ~/.claude/context-lake/) */
  basePath?: string;
}

/**
 * Opens (or creates) the Context Lake SQLite DB for the given repo root.
 *
 * @param repoRoot - Absolute path to the git repository root
 *                   (typically from `git rev-parse --show-toplevel`).
 * @param options  - Optional overrides (basePath for testing).
 */
export function openLake(repoRoot: string, options?: OpenLakeOptions): Database {
  const slug = basename(repoRoot);
  const baseDir = options?.basePath ?? join(homedir(), ".claude", "context-lake");
  mkdirSync(baseDir, { recursive: true });

  const dbPath = join(baseDir, `${slug}.db`);
  const db = new Database(dbPath);

  // PRAGMAs — WAL for concurrent access, busy_timeout for contention
  db.exec("PRAGMA journal_mode=WAL");
  db.exec("PRAGMA busy_timeout=5000");

  // Schema
  db.exec(SCHEMA_DDL);

  // FTS5 — check if the virtual table already exists
  const ftsExists = db
    .query(
      "SELECT name FROM sqlite_master WHERE type='table' AND name='insights_fts'"
    )
    .get();
  if (!ftsExists) {
    db.exec(FTS_DDL);
  }

  return db;
}

// ---------------------------------------------------------------------------
// storeInsight
// ---------------------------------------------------------------------------

/**
 * Stores an insight for a file path. Implements:
 * - Source priority guard: won't overwrite higher-priority sources
 * - FTS5 manual sync (external content mode)
 * - Last-write-wins for equal or higher priority
 */
export function storeInsight(db: Database, input: StoreInsightInput): void {
  const { filePath, content, source, sourceSession, sourceModel, gitHash } = input;

  // Check existing insight for source priority guard
  const existing = db
    .query("SELECT id, source, file_path, content FROM insights WHERE file_path = ?")
    .get(filePath) as { id: number; source: string; file_path: string; content: string } | null;

  if (existing) {
    const existingPriority = SOURCE_PRIORITY[existing.source] ?? 0;
    const newPriority = SOURCE_PRIORITY[source] ?? 0;

    // If existing has higher priority, skip the write
    if (existingPriority > newPriority) {
      return;
    }

    // Wrap FTS delete + UPDATE + FTS insert in a transaction for atomicity
    const txn = db.transaction(() => {
      // Delete old FTS entry before updating
      db.query(
        "INSERT INTO insights_fts(insights_fts, rowid, file_path, content) VALUES('delete', ?, ?, ?)"
      ).run(existing.id, existing.file_path, existing.content);

      // Update the existing row
      db.query(
        `UPDATE insights
         SET content = ?, source = ?, source_session = ?, source_model = ?,
             git_hash = ?, stale = 0, updated_at = datetime('now')
         WHERE file_path = ?`
      ).run(content, source, sourceSession ?? null, sourceModel ?? null, gitHash, filePath);

      // Get the updated row for FTS sync
      const updated = db
        .query("SELECT id, file_path, content FROM insights WHERE file_path = ?")
        .get(filePath) as { id: number; file_path: string; content: string };

      // Insert new FTS entry
      db.query(
        "INSERT INTO insights_fts(rowid, file_path, content) VALUES(?, ?, ?)"
      ).run(updated.id, updated.file_path, updated.content);
    });
    txn();
  } else {
    // No existing row — wrap INSERT + FTS insert in a transaction for atomicity
    const txn = db.transaction(() => {
      db.query(
        `INSERT INTO insights (file_path, content, source, source_session, source_model, git_hash)
         VALUES (?, ?, ?, ?, ?, ?)`
      ).run(filePath, content, source, sourceSession ?? null, sourceModel ?? null, gitHash);

      // Get the inserted row for FTS sync
      const inserted = db
        .query("SELECT id, file_path, content FROM insights WHERE file_path = ?")
        .get(filePath) as { id: number; file_path: string; content: string };

      // Insert FTS entry
      db.query(
        "INSERT INTO insights_fts(rowid, file_path, content) VALUES(?, ?, ?)"
      ).run(inserted.id, inserted.file_path, inserted.content);
    });
    txn();
  }
}

// ---------------------------------------------------------------------------
// searchInsights
// ---------------------------------------------------------------------------

/**
 * Search insights by exact file path or FTS5 full-text query.
 * Returns matching Insight[] sorted by updated_at desc.
 */
export function searchInsights(db: Database, input: SearchInsightsInput): Insight[] {
  const { query, filePath, freshnessDays } = input;

  let rows: RawInsightRow[];

  if (filePath) {
    // Exact file path match
    let filePathSql = `SELECT id, file_path, content, source, source_session, source_model,
                git_hash, stale, created_at, updated_at
         FROM insights
         WHERE file_path = ?`;
    const filePathParams: (string | number)[] = [filePath];

    if (freshnessDays != null) {
      filePathSql += ` AND updated_at >= datetime('now', ?)`;
      filePathParams.push(`-${freshnessDays} days`);
    }

    filePathSql += ` ORDER BY updated_at DESC`;

    rows = db.query(filePathSql).all(...filePathParams) as RawInsightRow[];
  } else if (query) {
    // FTS5 full-text search
    let sql = `SELECT i.id, i.file_path, i.content, i.source, i.source_session,
                      i.source_model, i.git_hash, i.stale, i.created_at, i.updated_at
               FROM insights_fts fts
               JOIN insights i ON i.id = fts.rowid
               WHERE insights_fts MATCH ?`;

    const params: (string | number)[] = [query];

    if (freshnessDays != null) {
      sql += ` AND i.updated_at >= datetime('now', ?)`;
      params.push(`-${freshnessDays} days`);
    }

    sql += ` ORDER BY i.updated_at DESC`;

    rows = db.query(sql).all(...params) as RawInsightRow[];
  } else {
    // No filter — return all
    rows = db
      .query(
        `SELECT id, file_path, content, source, source_session, source_model,
                git_hash, stale, created_at, updated_at
         FROM insights
         ORDER BY updated_at DESC`
      )
      .all() as RawInsightRow[];
  }

  return rows.map(rowToInsight);
}

// ---------------------------------------------------------------------------
// invalidateStale
// ---------------------------------------------------------------------------

/**
 * Marks insights for the given file paths as stale (stale=1).
 * Returns the number of rows actually updated.
 */
export function invalidateStale(db: Database, changedFiles: string[]): number {
  if (changedFiles.length === 0) return 0;

  const placeholders = changedFiles.map(() => "?").join(",");
  const result = db
    .query(
      `UPDATE insights SET stale = 1, updated_at = datetime('now')
       WHERE file_path IN (${placeholders}) AND stale = 0`
    )
    .run(...changedFiles);

  return result.changes;
}

// ---------------------------------------------------------------------------
// recordMetric
// ---------------------------------------------------------------------------

/**
 * Records a metric event (hit, miss, store, explore_allowed, etc.).
 */
export function recordMetric(db: Database, params: MetricParams): void {
  const { event, filePath, details, sessionId } = params;
  db.query(
    `INSERT INTO metrics (event, file_path, details, session_id)
     VALUES (?, ?, ?, ?)`
  ).run(
    event,
    filePath ?? null,
    details ? JSON.stringify(details) : null,
    sessionId ?? null
  );
}

// ---------------------------------------------------------------------------
// getMetricsSummary
// ---------------------------------------------------------------------------

/**
 * Returns aggregated metric counts and hit rate.
 * Optional `since` parameter filters to events after that date.
 */
export function getMetricsSummary(
  db: Database,
  options?: { since?: string }
): MetricsSummary {
  let sql = `SELECT event, COUNT(*) as cnt FROM metrics`;
  const params: string[] = [];

  if (options?.since) {
    sql += ` WHERE created_at >= ?`;
    params.push(options.since);
  }

  sql += ` GROUP BY event`;

  const rows = db.query(sql).all(...params) as { event: string; cnt: number }[];

  const counts: Record<string, number> = {};
  for (const row of rows) {
    counts[row.event] = row.cnt;
  }

  const totalHits = counts["hit"] ?? 0;
  const totalMisses = counts["miss"] ?? 0;
  const totalStores = counts["store"] ?? 0;
  const totalExploreHints = counts["explore_allowed"] ?? 0;

  const denominator = totalHits + totalMisses;
  const hitRate = denominator > 0 ? Math.round((totalHits / denominator) * 100) : null;

  return { totalHits, totalMisses, totalStores, totalExploreHints, hitRate };
}

// ---------------------------------------------------------------------------
// coldEvict
// ---------------------------------------------------------------------------

/**
 * Removes insights that are:
 * 1. Older than `maxAgeDays` (based on updated_at)
 * 2. Have no "hit" events in the metrics table within `minIdleDays`
 *
 * Also cleans up the corresponding FTS entries. Uses a transaction for atomicity.
 * Returns the number of evicted rows.
 */
export function coldEvict(
  db: Database,
  options?: ColdEvictOptions
): number {
  const maxAgeDays = options?.maxAgeDays ?? 30;
  const minIdleDays = options?.minIdleDays ?? 7;

  const txn = db.transaction(() => {
    // Find candidates: old insights with no recent hits
    const candidates = db
      .query(
        `SELECT i.id, i.file_path, i.content
         FROM insights i
         WHERE i.updated_at < datetime('now', ?)
           AND NOT EXISTS (
             SELECT 1 FROM metrics m
             WHERE m.file_path = i.file_path
               AND m.event = 'hit'
               AND m.created_at >= datetime('now', ?)
           )`
      )
      .all(`-${maxAgeDays} days`, `-${minIdleDays} days`) as {
      id: number;
      file_path: string;
      content: string;
    }[];

    if (candidates.length === 0) return 0;

    // Delete FTS entries first, then main rows
    for (const row of candidates) {
      db.query(
        "INSERT INTO insights_fts(insights_fts, rowid, file_path, content) VALUES('delete', ?, ?, ?)"
      ).run(row.id, row.file_path, row.content);

      db.query("DELETE FROM insights WHERE id = ?").run(row.id);
    }

    return candidates.length;
  });

  return txn();
}

// ---------------------------------------------------------------------------
// Internals
// ---------------------------------------------------------------------------

interface RawInsightRow {
  id: number;
  file_path: string;
  content: string;
  source: string;
  source_session: string | null;
  source_model: string | null;
  git_hash: string;
  stale: number;
  created_at: string;
  updated_at: string;
}

function rowToInsight(row: RawInsightRow): Insight {
  return {
    id: row.id,
    filePath: row.file_path,
    content: row.content,
    source: row.source,
    sourceSession: row.source_session,
    sourceModel: row.source_model,
    gitHash: row.git_hash,
    stale: row.stale,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

/** Cross-platform homedir (avoids importing os just for this). */
function homedir(): string {
  return process.env.HOME ?? process.env.USERPROFILE ?? "/tmp";
}
