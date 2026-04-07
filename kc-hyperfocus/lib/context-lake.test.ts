import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { Database } from "bun:sqlite";
import { mkdirSync, rmSync } from "node:fs";
import {
  openLake,
  storeInsight,
  searchInsights,
  searchInsightsByEmbedding,
  invalidateStale,
  recordMetric,
  getMetricsSummary,
  coldEvict,
  normalizeFilePath,
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

  // ---------------------------------------------------------------------------
  // Path normalization (2026-04-07)
  // ---------------------------------------------------------------------------

  describe("normalizeFilePath", () => {
    const REPO = "/Users/kent/Project/kc-claude-workspace";

    it("strips repoRoot prefix from absolute path inside repo", () => {
      expect(
        normalizeFilePath(
          "/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-hyperfocus/lib/journal.ts",
          REPO
        )
      ).toBe("kc-claude-plugins/kc-hyperfocus/lib/journal.ts");
    });

    it("passes through absolute path outside repo unchanged", () => {
      expect(
        normalizeFilePath(
          "/Users/kent/.claude/plugins/cache/foo/bar.md",
          REPO
        )
      ).toBe("/Users/kent/.claude/plugins/cache/foo/bar.md");
    });

    it("passes through already-relative path unchanged", () => {
      expect(normalizeFilePath("src/components/Button.tsx", REPO)).toBe(
        "src/components/Button.tsx"
      );
    });

    it("strips .worktrees/<name>/ prefix from relative path", () => {
      expect(
        normalizeFilePath(".worktrees/ensign-foo/docs/bar.md", REPO)
      ).toBe("docs/bar.md");
    });

    it("strips both repoRoot and .worktrees prefix from absolute worktree path", () => {
      expect(
        normalizeFilePath(
          "/Users/kent/Project/kc-claude-workspace/.worktrees/ensign-foo/docs/bar.md",
          REPO
        )
      ).toBe("docs/bar.md");
    });

    it("is idempotent — normalizing twice produces same result", () => {
      const once = normalizeFilePath(
        "/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/foo.ts",
        REPO
      );
      const twice = normalizeFilePath(once, REPO);
      expect(once).toBe(twice);
      expect(once).toBe("kc-claude-plugins/foo.ts");
    });

    it("does not strip a path that only partially matches repoRoot (no trailing slash)", () => {
      // "/Users/kent/Project/kc-claude-workspace2" must not match repo "/Users/kent/Project/kc-claude-workspace"
      expect(
        normalizeFilePath(
          "/Users/kent/Project/kc-claude-workspace2/foo.ts",
          REPO
        )
      ).toBe("/Users/kent/Project/kc-claude-workspace2/foo.ts");
    });
  });

  // ---------------------------------------------------------------------------
  // storeInsight + searchInsights with repoRoot auto-normalization (2026-04-07)
  // ---------------------------------------------------------------------------

  it("storeInsight with repoRoot normalizes absolute path before storage", () => {
    const repoRoot = "/fake/repo/my-project";

    storeInsight(
      db,
      {
        filePath: "/fake/repo/my-project/src/auth/login.ts",
        content: "Login handler with OAuth2 integration.",
        source: "handoff",
        gitHash: "normalize1",
      },
      repoRoot
    );

    // Lookup by relative path succeeds (storage was canonicalized)
    const relResults = searchInsights(db, {
      filePath: "src/auth/login.ts",
    });
    expect(relResults).toHaveLength(1);
    expect(relResults[0].filePath).toBe("src/auth/login.ts");

    // Lookup by absolute path WITHOUT repoRoot fails (because DB key is relative now)
    const absNoNorm = searchInsights(db, {
      filePath: "/fake/repo/my-project/src/auth/login.ts",
    });
    expect(absNoNorm).toHaveLength(0);

    // Lookup by absolute path WITH repoRoot succeeds (search normalizes too)
    const absWithNorm = searchInsights(
      db,
      { filePath: "/fake/repo/my-project/src/auth/login.ts" },
      repoRoot
    );
    expect(absWithNorm).toHaveLength(1);
    expect(absWithNorm[0].filePath).toBe("src/auth/login.ts");
  });

  it("storeInsight without repoRoot preserves input path as-is (backward compat)", () => {
    // Tests that don't pass repoRoot must continue to work with whatever path format they use
    storeInsight(db, {
      filePath: "/absolute/path/without/normalization.ts",
      content: "Test insight",
      source: "manual",
      gitHash: "nohint",
    });

    const results = searchInsights(db, {
      filePath: "/absolute/path/without/normalization.ts",
    });
    expect(results).toHaveLength(1);
    expect(results[0].filePath).toBe("/absolute/path/without/normalization.ts");
  });

  it("invalidateStale with repoRoot normalizes absolute paths before matching", () => {
    const repoRoot = "/fake/repo/my-project";

    storeInsight(
      db,
      {
        filePath: "/fake/repo/my-project/src/stale.ts",
        content: "Will be invalidated",
        source: "handoff",
        gitHash: "stale1",
      },
      repoRoot
    );

    // Invalidate using absolute path + repoRoot → matches normalized row
    const count = invalidateStale(
      db,
      ["/fake/repo/my-project/src/stale.ts"],
      repoRoot
    );
    expect(count).toBe(1);

    const r = searchInsights(db, { filePath: "src/stale.ts" });
    expect(r[0].stale).toBe(1);
  });

  // ---------------------------------------------------------------------------
  // Embedding storage + cosine similarity search (2026-04-07)
  // ---------------------------------------------------------------------------

  describe("embedding search", () => {
    // Helper: make a 4-dim test vector (real MiniLM is 384-dim, but cosine math
    // is dimension-agnostic — 4-dim is easier to reason about in tests).
    const vec = (a: number, b: number, c: number, d: number) =>
      new Float32Array([a, b, c, d]);

    it("openLake ALTER TABLE is idempotent (reopening existing DB doesn't error)", () => {
      // Close the current DB and reopen it — should not throw due to
      // duplicate column
      db.close();
      db = openLake("/fake/repo/my-project", { basePath: TEST_DIR });

      // Verify the column exists
      const col = db
        .query(
          "SELECT name FROM pragma_table_info('insights') WHERE name = 'content_embedding'"
        )
        .get() as { name: string } | null;
      expect(col?.name).toBe("content_embedding");
    });

    it("storeInsight persists content_embedding, searchInsightsByEmbedding finds exact match", () => {
      storeInsight(db, {
        filePath: "src/auth/login.ts",
        content: "OAuth2 login flow",
        source: "manual",
        gitHash: "emb1",
        embedding: vec(1, 0, 0, 0),
      });

      const results = searchInsightsByEmbedding(db, vec(1, 0, 0, 0));
      expect(results).toHaveLength(1);
      expect(results[0].filePath).toBe("src/auth/login.ts");
      expect(results[0].similarity).toBeCloseTo(1.0, 5);
    });

    it("searchInsightsByEmbedding ranks results by cosine similarity desc", () => {
      // Three rows with known vectors — query vec(1,0,0,0) should rank:
      // row A (identical) > row B (45°) > row C (90°, perpendicular)
      storeInsight(db, {
        filePath: "a.ts",
        content: "A",
        source: "manual",
        gitHash: "a",
        embedding: vec(1, 0, 0, 0),
      });
      storeInsight(db, {
        filePath: "b.ts",
        content: "B",
        source: "manual",
        gitHash: "b",
        embedding: vec(1, 1, 0, 0), // ~0.707 similarity to (1,0,0,0)
      });
      storeInsight(db, {
        filePath: "c.ts",
        content: "C",
        source: "manual",
        gitHash: "c",
        embedding: vec(0, 1, 0, 0), // 0.0 similarity (perpendicular)
      });

      const results = searchInsightsByEmbedding(db, vec(1, 0, 0, 0), {
        minSimilarity: 0.0,
      });

      expect(results.map((r) => r.filePath)).toEqual(["a.ts", "b.ts", "c.ts"]);
      expect(results[0].similarity).toBeCloseTo(1.0, 5);
      expect(results[1].similarity).toBeCloseTo(0.7071, 3);
      expect(results[2].similarity).toBeCloseTo(0.0, 5);
    });

    it("searchInsightsByEmbedding filters by minSimilarity threshold", () => {
      storeInsight(db, {
        filePath: "close.ts",
        content: "close",
        source: "manual",
        gitHash: "c",
        embedding: vec(1, 0.2, 0, 0),
      });
      storeInsight(db, {
        filePath: "far.ts",
        content: "far",
        source: "manual",
        gitHash: "f",
        embedding: vec(0, 0, 1, 0),
      });

      // minSimilarity 0.5 → only "close" qualifies
      const results = searchInsightsByEmbedding(db, vec(1, 0, 0, 0), {
        minSimilarity: 0.5,
      });

      expect(results).toHaveLength(1);
      expect(results[0].filePath).toBe("close.ts");
    });

    it("searchInsightsByEmbedding respects limit parameter", () => {
      for (let i = 0; i < 5; i++) {
        storeInsight(db, {
          filePath: `file${i}.ts`,
          content: `file ${i}`,
          source: "manual",
          gitHash: `g${i}`,
          embedding: vec(1, i * 0.1, 0, 0),
        });
      }

      const results = searchInsightsByEmbedding(db, vec(1, 0, 0, 0), {
        limit: 2,
        minSimilarity: 0.0,
      });

      expect(results).toHaveLength(2);
    });

    it("searchInsightsByEmbedding excludes stale rows by default, includes when excludeStale=false", () => {
      storeInsight(db, {
        filePath: "fresh.ts",
        content: "fresh",
        source: "manual",
        gitHash: "f",
        embedding: vec(1, 0, 0, 0),
      });
      storeInsight(db, {
        filePath: "stale.ts",
        content: "stale",
        source: "manual",
        gitHash: "s",
        embedding: vec(1, 0, 0, 0),
      });
      invalidateStale(db, ["stale.ts"]);

      const defaultResults = searchInsightsByEmbedding(db, vec(1, 0, 0, 0));
      expect(defaultResults.map((r) => r.filePath)).toEqual(["fresh.ts"]);

      const allResults = searchInsightsByEmbedding(db, vec(1, 0, 0, 0), {
        excludeStale: false,
      });
      const paths = allResults.map((r) => r.filePath).sort();
      expect(paths).toEqual(["fresh.ts", "stale.ts"]);
    });

    it("searchInsightsByEmbedding ignores rows without embeddings", () => {
      storeInsight(db, {
        filePath: "with.ts",
        content: "with",
        source: "manual",
        gitHash: "w",
        embedding: vec(1, 0, 0, 0),
      });
      storeInsight(db, {
        filePath: "without.ts",
        content: "without",
        source: "manual",
        gitHash: "wo",
        // no embedding
      });

      const results = searchInsightsByEmbedding(db, vec(1, 0, 0, 0));
      expect(results).toHaveLength(1);
      expect(results[0].filePath).toBe("with.ts");
    });

    it("searchInsightsByEmbedding returns [] for zero query vector", () => {
      storeInsight(db, {
        filePath: "a.ts",
        content: "a",
        source: "manual",
        gitHash: "a",
        embedding: vec(1, 0, 0, 0),
      });

      const results = searchInsightsByEmbedding(db, vec(0, 0, 0, 0));
      expect(results).toHaveLength(0);
    });

    it("storeInsight upsert preserves existing embedding when new embedding omitted", () => {
      // Initial store with embedding
      storeInsight(db, {
        filePath: "preserve.ts",
        content: "v1",
        source: "journal",
        gitHash: "v1",
        embedding: vec(1, 0, 0, 0),
      });

      // Update without embedding (same or higher priority)
      storeInsight(db, {
        filePath: "preserve.ts",
        content: "v2",
        source: "handoff",
        gitHash: "v2",
        // no embedding — should inherit from v1
      });

      // Can still be found by embedding search
      const results = searchInsightsByEmbedding(db, vec(1, 0, 0, 0));
      expect(results).toHaveLength(1);
      expect(results[0].filePath).toBe("preserve.ts");
      expect(results[0].content).toBe("v2"); // content updated
      expect(results[0].source).toBe("handoff");
    });

    it("storeInsight upsert replaces embedding when new one supplied", () => {
      storeInsight(db, {
        filePath: "replace.ts",
        content: "v1",
        source: "journal",
        gitHash: "v1",
        embedding: vec(1, 0, 0, 0),
      });

      // Update with a DIFFERENT embedding
      storeInsight(db, {
        filePath: "replace.ts",
        content: "v2",
        source: "handoff",
        gitHash: "v2",
        embedding: vec(0, 1, 0, 0),
      });

      // Old vector should no longer match; new vector should
      const oldMatch = searchInsightsByEmbedding(db, vec(1, 0, 0, 0), {
        minSimilarity: 0.5,
      });
      expect(oldMatch).toHaveLength(0);

      const newMatch = searchInsightsByEmbedding(db, vec(0, 1, 0, 0));
      expect(newMatch).toHaveLength(1);
      expect(newMatch[0].filePath).toBe("replace.ts");
    });
  });
});

// ---------------------------------------------------------------------------
// MCP-level source enum coercion (server/schemas.ts)
// Tests the .catch().default() contract: invalid/missing → "manual"
// ---------------------------------------------------------------------------

import { sourceSchema } from "../server/schemas";

describe("sourceSchema", () => {
  it("passes through valid enum values unchanged", () => {
    expect(sourceSchema.parse("handoff")).toBe("handoff");
    expect(sourceSchema.parse("read")).toBe("read");
    expect(sourceSchema.parse("journal")).toBe("journal");
    expect(sourceSchema.parse("manual")).toBe("manual");
  });

  it("coerces undefined to 'manual' via default", () => {
    expect(sourceSchema.parse(undefined)).toBe("manual");
  });

  it("coerces invalid string to 'manual' via catch", () => {
    expect(sourceSchema.parse("Junk-Value-Not-In-Enum")).toBe("manual");
    expect(sourceSchema.parse("Manual")).toBe("manual"); // wrong case
    expect(sourceSchema.parse("")).toBe("manual");
    expect(sourceSchema.parse("HANDOFF")).toBe("manual"); // case-sensitive
  });

  it("coerces non-string types to 'manual' via catch", () => {
    expect(sourceSchema.parse(42)).toBe("manual");
    expect(sourceSchema.parse(null)).toBe("manual");
    expect(sourceSchema.parse(true)).toBe("manual");
  });
});
