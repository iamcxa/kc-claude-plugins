/**
 * context-lake-mcp.ts — MCP server exposing 5 Context Lake tools.
 *
 * Transport: stdio (JSON-RPC over stdin/stdout).
 * Claude Code auto-discovers via .mcp.json at plugin root.
 *
 * CRITICAL: No console.log — stdout is reserved for JSON-RPC protocol.
 * Use console.error for debug logging only.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { execFileSync } from "node:child_process";
import { z } from "zod";

import {
  openLake,
  storeInsight,
  searchInsights,
  invalidateStale,
  recordMetric,
  getMetricsSummary,
  coldEvict,
} from "../lib/context-lake";

// ---------------------------------------------------------------------------
// Git helpers
// ---------------------------------------------------------------------------

function getRepoRoot(): string {
  return execFileSync("git", ["rev-parse", "--show-toplevel"], {
    encoding: "utf-8",
  }).trim();
}

function getGitHash(): string {
  return execFileSync("git", ["rev-parse", "HEAD"], {
    encoding: "utf-8",
  }).trim();
}

// ---------------------------------------------------------------------------
// MCP Server
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "context-lake",
  version: "1.0.0",
});

// Lazily open DB on first use (repo root depends on CWD at invocation time)
let _db: ReturnType<typeof openLake> | null = null;
let _repoRoot: string | null = null;

function getDb() {
  if (!_db) {
    _repoRoot = getRepoRoot();
    _db = openLake(_repoRoot);
    console.error(`[context-lake] DB opened for repo: ${_repoRoot}`);
  }
  return _db;
}

// ---------------------------------------------------------------------------
// Tool: store_insight
// ---------------------------------------------------------------------------

server.tool(
  "store_insight",
  "Store an insight (summary/annotation) for a file path. Auto-detects git hash.",
  {
    file_path: z.string().describe("Relative or absolute path to the file"),
    content: z.string().describe("The insight content (summary, annotation, etc.)"),
    source: z.enum(["handoff", "read", "journal", "manual"]).describe(
      "How this insight was generated"
    ),
  },
  async ({ file_path, content, source }) => {
    try {
      const db = getDb();
      const gitHash = getGitHash();

      storeInsight(db, {
        filePath: file_path,
        content,
        source,
        gitHash,
      });

      recordMetric(db, { event: "store", filePath: file_path });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              status: "stored",
              file_path,
              source,
              git_hash: gitHash,
            }),
          },
        ],
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] store_insight error: ${msg}`);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: search_insights
// ---------------------------------------------------------------------------

server.tool(
  "search_insights",
  "Search stored insights by full-text query and/or exact file path. Returns matching insights sorted by freshness.",
  {
    query: z.string().optional().describe("FTS5 full-text search query"),
    file_path: z.string().optional().describe("Exact file path to look up"),
    freshness_days: z
      .number()
      .optional()
      .default(7)
      .describe("Only return insights updated within N days (default 7)"),
  },
  async ({ query, file_path, freshness_days }) => {
    try {
      const db = getDb();

      const results = searchInsights(db, {
        query: query ?? undefined,
        filePath: file_path ?? undefined,
        freshnessDays: freshness_days,
      });

      // Record hit or miss metric
      const eventType = results.length > 0 ? "hit" : "miss";
      recordMetric(db, {
        event: eventType,
        filePath: file_path ?? undefined,
        details: query ? { query } : undefined,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              count: results.length,
              insights: results.map((r) => ({
                file_path: r.filePath,
                content: r.content,
                source: r.source,
                stale: r.stale === 1,
                git_hash: r.gitHash,
                updated_at: r.updatedAt,
              })),
            }),
          },
        ],
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] search_insights error: ${msg}`);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: invalidate_stale
// ---------------------------------------------------------------------------

server.tool(
  "invalidate_stale",
  "Mark insights for given file paths as stale (e.g., after git changes). Stale insights are still searchable but flagged.",
  {
    changed_files: z
      .array(z.string())
      .describe("List of file paths whose insights should be marked stale"),
  },
  async ({ changed_files }) => {
    try {
      const db = getDb();
      const updated = invalidateStale(db, changed_files);

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              status: "invalidated",
              files_requested: changed_files.length,
              insights_marked_stale: updated,
            }),
          },
        ],
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] invalidate_stale error: ${msg}`);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: get_metrics
// ---------------------------------------------------------------------------

server.tool(
  "get_metrics",
  "Get aggregated metrics (hit rate, store count, etc.) for the context lake. Optionally filter by date or record a new event.",
  {
    since: z
      .string()
      .optional()
      .describe("ISO date string — only count events after this date"),
    event: z
      .string()
      .optional()
      .describe(
        "If provided, record this event type (hit, miss, store, explore_allowed) before returning metrics"
      ),
  },
  async ({ since, event }) => {
    try {
      const db = getDb();

      // Optionally record a new event
      if (event) {
        recordMetric(db, { event });
      }

      const summary = getMetricsSummary(db, {
        since: since ?? undefined,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              total_hits: summary.totalHits,
              total_misses: summary.totalMisses,
              total_stores: summary.totalStores,
              total_explore_hints: summary.totalExploreHints,
              hit_rate_pct: summary.hitRate,
              ...(since ? { since } : {}),
            }),
          },
        ],
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] get_metrics error: ${msg}`);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: lake_status
// ---------------------------------------------------------------------------

server.tool(
  "lake_status",
  "Get overall status of the context lake: DB path, repo, insight count, stale count, and cold eviction stats.",
  {},
  async () => {
    try {
      const db = getDb();

      const totalRow = db
        .query("SELECT COUNT(*) as cnt FROM insights")
        .get() as { cnt: number };
      const staleRow = db
        .query("SELECT COUNT(*) as cnt FROM insights WHERE stale = 1")
        .get() as { cnt: number };
      const metricsRow = db
        .query("SELECT COUNT(*) as cnt FROM metrics")
        .get() as { cnt: number };

      // Run cold eviction (dry-run-like: just report, then actually evict)
      const evicted = coldEvict(db);

      const summary = getMetricsSummary(db);

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              repo_root: _repoRoot,
              total_insights: totalRow.cnt,
              stale_insights: staleRow.cnt,
              fresh_insights: totalRow.cnt - staleRow.cnt,
              total_metric_events: metricsRow.cnt,
              hit_rate_pct: summary.hitRate,
              cold_evicted_now: evicted,
            }),
          },
        ],
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] lake_status error: ${msg}`);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Start server
// ---------------------------------------------------------------------------

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[context-lake] MCP server started on stdio");
}

main().catch((err) => {
  console.error("[context-lake] Fatal error:", err);
  process.exit(1);
});
