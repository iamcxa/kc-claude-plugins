import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { Database } from "bun:sqlite";
import { mkdirSync, rmSync } from "node:fs";
import {
  openLake,
  storeInsight,
  searchInsights,
  invalidateStale,
  recordMetric,
  getMetricsSummary,
  coldEvict,
} from "./context-lake";

const TEST_DIR = "/tmp/context-lake-test";

describe("context-lake", () => {
  let db: Database;

  beforeEach(() => {
    rmSync(TEST_DIR, { recursive: true, force: true });
    mkdirSync(TEST_DIR, { recursive: true });
    db = openLake("/fake/repo/my-project", { basePath: TEST_DIR });
  });

  afterEach(() => {
    db.close();
    rmSync(TEST_DIR, { recursive: true, force: true });
  });

  it("openLake creates DB with insights, metrics, insights_fts tables", () => {
    const tables = db
      .query(
        "SELECT name FROM sqlite_master WHERE type IN ('table', 'table') AND name NOT LIKE 'sqlite_%' ORDER BY name"
      )
      .all() as { name: string }[];

    const names = tables.map((t) => t.name).sort();
    expect(names).toContain("insights");
    expect(names).toContain("metrics");

    // FTS5 virtual tables show up differently
    const allObjects = db
      .query("SELECT name, type FROM sqlite_master ORDER BY name")
      .all() as { name: string; type: string }[];
    const ftsNames = allObjects.map((o) => o.name);
    expect(ftsNames).toContain("insights_fts");
  });

  it("openLake sets journal_mode=WAL and busy_timeout=5000", () => {
    const journalMode = db.query("PRAGMA journal_mode").get() as {
      journal_mode: string;
    };
    expect(journalMode.journal_mode).toBe("wal");

    const busyTimeout = db.query("PRAGMA busy_timeout").get() as {
      timeout: number;
    };
    expect(busyTimeout.timeout).toBe(5000);
  });

  it("storeInsight + searchInsights by exact filePath", () => {
    storeInsight(db, {
      filePath: "src/components/Button.tsx",
      content:
        "A reusable button component with primary and secondary variants. Uses Tailwind for styling.",
      source: "handoff",
      sourceSession: "session-123",
      sourceModel: "claude-opus-4-6",
      gitHash: "abc1234",
    });

    const results = searchInsights(db, {
      filePath: "src/components/Button.tsx",
    });

    expect(results).toHaveLength(1);
    expect(results[0].filePath).toBe("src/components/Button.tsx");
    expect(results[0].content).toContain("reusable button component");
    expect(results[0].source).toBe("handoff");
    expect(results[0].gitHash).toBe("abc1234");
  });

  it("storeInsight upserts same file_path (last-write-wins)", () => {
    storeInsight(db, {
      filePath: "src/utils/format.ts",
      content: "First version: basic date formatting utility.",
      source: "journal",
      gitHash: "aaa1111",
    });

    storeInsight(db, {
      filePath: "src/utils/format.ts",
      content:
        "Updated: comprehensive formatting utility with date, number, and currency support.",
      source: "handoff",
      gitHash: "bbb2222",
    });

    const results = searchInsights(db, {
      filePath: "src/utils/format.ts",
    });

    expect(results).toHaveLength(1);
    expect(results[0].content).toContain("comprehensive formatting utility");
    expect(results[0].gitHash).toBe("bbb2222");
    expect(results[0].source).toBe("handoff");
  });

  it("source priority: manual insight not overwritten by handoff", () => {
    storeInsight(db, {
      filePath: "src/core/auth.ts",
      content:
        "Authentication module with OAuth2 and session management. Critical path — do not cache stale.",
      source: "manual",
      gitHash: "ccc3333",
    });

    // Attempt to overwrite with lower-priority source
    storeInsight(db, {
      filePath: "src/core/auth.ts",
      content: "Auth module handles login.",
      source: "handoff",
      gitHash: "ddd4444",
    });

    const results = searchInsights(db, {
      filePath: "src/core/auth.ts",
    });

    expect(results).toHaveLength(1);
    // Should retain the manual insight, not the handoff one
    expect(results[0].source).toBe("manual");
    expect(results[0].content).toContain("Critical path");
    expect(results[0].gitHash).toBe("ccc3333");
  });

  // ---------------------------------------------------------------------------
  // Task 2: invalidateStale
  // ---------------------------------------------------------------------------

  it("invalidateStale marks matching files stale, leaves others untouched", () => {
    storeInsight(db, {
      filePath: "src/a.ts",
      content: "File A insight",
      source: "journal",
      gitHash: "aaa",
    });
    storeInsight(db, {
      filePath: "src/b.ts",
      content: "File B insight",
      source: "journal",
      gitHash: "bbb",
    });
    storeInsight(db, {
      filePath: "src/c.ts",
      content: "File C insight",
      source: "journal",
      gitHash: "ccc",
    });

    const count = invalidateStale(db, ["src/a.ts", "src/c.ts"]);

    expect(count).toBe(2);

    // a.ts and c.ts should be stale
    const a = searchInsights(db, { filePath: "src/a.ts" });
    expect(a[0].stale).toBe(1);
    const c = searchInsights(db, { filePath: "src/c.ts" });
    expect(c[0].stale).toBe(1);

    // b.ts should remain fresh
    const b = searchInsights(db, { filePath: "src/b.ts" });
    expect(b[0].stale).toBe(0);
  });

  // ---------------------------------------------------------------------------
  // Task 2: recordMetric + getMetricsSummary
  // ---------------------------------------------------------------------------

  it("recordMetric stores events, getMetricsSummary returns hit/miss/hitRate", () => {
    recordMetric(db, { event: "hit", filePath: "src/a.ts" });
    recordMetric(db, { event: "hit", filePath: "src/b.ts" });
    recordMetric(db, { event: "hit", filePath: "src/a.ts", sessionId: "s1" });
    recordMetric(db, { event: "miss", filePath: "src/c.ts" });
    recordMetric(db, { event: "store", filePath: "src/d.ts", details: { reason: "handoff" } });
    recordMetric(db, { event: "explore_allowed" });

    const summary = getMetricsSummary(db);

    expect(summary.totalHits).toBe(3);
    expect(summary.totalMisses).toBe(1);
    expect(summary.totalStores).toBe(1);
    expect(summary.totalExploreHints).toBe(1);
    // hitRate = hits / (hits + misses) = 3/4 = 75
    expect(summary.hitRate).toBe(75);
  });

  // ---------------------------------------------------------------------------
  // Task 2: coldEvict
  // ---------------------------------------------------------------------------

  it("coldEvict removes old insights with no recent hits, keeps recent ones", () => {
    // Insert an "old" insight by manipulating updated_at directly
    db.query(
      `INSERT INTO insights (file_path, content, source, git_hash, created_at, updated_at)
       VALUES (?, ?, ?, ?, datetime('now', '-60 days'), datetime('now', '-60 days'))`
    ).run("old/stale.ts", "Old stale insight", "journal", "old1");
    // Sync FTS for this row
    const oldRow = db.query("SELECT id, file_path, content FROM insights WHERE file_path = ?")
      .get("old/stale.ts") as { id: number; file_path: string; content: string };
    db.query("INSERT INTO insights_fts(rowid, file_path, content) VALUES(?, ?, ?)")
      .run(oldRow.id, oldRow.file_path, oldRow.content);

    // Insert an "old" insight that HAS a recent hit — should be kept
    db.query(
      `INSERT INTO insights (file_path, content, source, git_hash, created_at, updated_at)
       VALUES (?, ?, ?, ?, datetime('now', '-60 days'), datetime('now', '-60 days'))`
    ).run("old/active.ts", "Old but active insight", "journal", "old2");
    const activeRow = db.query("SELECT id, file_path, content FROM insights WHERE file_path = ?")
      .get("old/active.ts") as { id: number; file_path: string; content: string };
    db.query("INSERT INTO insights_fts(rowid, file_path, content) VALUES(?, ?, ?)")
      .run(activeRow.id, activeRow.file_path, activeRow.content);
    // Record a recent hit for this file
    recordMetric(db, { event: "hit", filePath: "old/active.ts" });

    // Insert a recent insight — should be kept regardless
    storeInsight(db, {
      filePath: "recent/fresh.ts",
      content: "Fresh insight",
      source: "journal",
      gitHash: "new1",
    });

    const evicted = coldEvict(db, { maxAgeDays: 30, minIdleDays: 7 });

    expect(evicted).toBe(1); // only old/stale.ts evicted

    // old/stale.ts should be gone
    const staleResults = searchInsights(db, { filePath: "old/stale.ts" });
    expect(staleResults).toHaveLength(0);

    // old/active.ts should remain (had recent hit)
    const activeResults = searchInsights(db, { filePath: "old/active.ts" });
    expect(activeResults).toHaveLength(1);

    // recent/fresh.ts should remain (not old enough)
    const freshResults = searchInsights(db, { filePath: "recent/fresh.ts" });
    expect(freshResults).toHaveLength(1);

    // FTS should also be cleaned — searching for the evicted content should return nothing
    const ftsResults = searchInsights(db, { query: "Old stale insight" });
    expect(ftsResults).toHaveLength(0);
  });

  // ---------------------------------------------------------------------------
  // Task 2: FTS5 search relevance
  // ---------------------------------------------------------------------------

  it("FTS5 search returns relevant insights ranked by relevance", () => {
    storeInsight(db, {
      filePath: "src/auth/login.ts",
      content: "Authentication login flow with OAuth2 provider integration and token refresh.",
      source: "journal",
      gitHash: "f1",
    });
    storeInsight(db, {
      filePath: "src/auth/logout.ts",
      content: "Authentication logout handler that clears session tokens and revokes OAuth2 grants.",
      source: "journal",
      gitHash: "f2",
    });
    storeInsight(db, {
      filePath: "src/utils/format.ts",
      content: "Date and currency formatting utilities. No authentication involved.",
      source: "journal",
      gitHash: "f3",
    });

    // FTS5 implicit AND: both terms must appear in a row
    const results = searchInsights(db, { query: "authentication OAuth2" });

    // login.ts and logout.ts both contain "authentication" AND "OAuth2"
    expect(results.length).toBeGreaterThanOrEqual(2);
    const paths = results.map((r) => r.filePath);
    expect(paths).toContain("src/auth/login.ts");
    expect(paths).toContain("src/auth/logout.ts");

    // OR query should find all three (each has "authentication")
    const orResults = searchInsights(db, { query: "authentication" });
    expect(orResults.length).toBe(3);

    // format.ts should NOT appear in the AND query
    expect(paths).not.toContain("src/utils/format.ts");
  });
});
