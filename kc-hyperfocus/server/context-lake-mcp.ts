/**
 * context-lake-mcp.ts — MCP server exposing Context Lake + Private Journal tools.
 *
 * Context Lake: 5 tools (store, search, invalidate, metrics, status)
 * Private Journal: 4 tools (process_thoughts, search_journal, read_journal_entry, list_recent_entries)
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
import { JournalWriter } from "../lib/journal";
import { JournalSearchService } from "../lib/journal-search";

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
// Journal: lazily initialized writer + search
// ---------------------------------------------------------------------------

let _journalWriter: JournalWriter | null = null;
let _journalSearch: JournalSearchService | null = null;

function getJournalWriter(): JournalWriter {
  if (!_journalWriter) _journalWriter = new JournalWriter();
  return _journalWriter;
}

function getJournalSearch(): JournalSearchService {
  if (!_journalSearch) _journalSearch = new JournalSearchService();
  return _journalSearch;
}

// ---------------------------------------------------------------------------
// Tool: process_thoughts
// ---------------------------------------------------------------------------

server.tool(
  "process_thoughts",
  "Your PRIVATE JOURNAL for learning and reflection. Write to any combination of these completely private spaces. Nobody but you will ever see this.",
  {
    feelings: z
      .string()
      .optional()
      .describe(
        "YOUR PRIVATE SPACE to be completely honest about what you're feeling and thinking. No judgment, no performance, no filters."
      ),
    project_notes: z
      .string()
      .optional()
      .describe(
        "Your PRIVATE TECHNICAL LABORATORY for capturing insights about the current project."
      ),
    user_context: z
      .string()
      .optional()
      .describe(
        "Your PRIVATE FIELD NOTES about working with your human collaborator."
      ),
    technical_insights: z
      .string()
      .optional()
      .describe(
        "Your PRIVATE SOFTWARE ENGINEERING NOTEBOOK for capturing broader learnings beyond the current project."
      ),
    world_knowledge: z
      .string()
      .optional()
      .describe(
        "Your PRIVATE LEARNING JOURNAL for everything else that's interesting or useful."
      ),
  },
  async (args) => {
    try {
      const hasContent = Object.values(args).some((v) => v != null);
      if (!hasContent) {
        return {
          content: [
            {
              type: "text" as const,
              text: "Error: At least one thought category must be provided",
            },
          ],
          isError: true,
        };
      }

      await getJournalWriter().writeThoughts(args);

      return {
        content: [
          { type: "text" as const, text: "Thoughts recorded successfully." },
        ],
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] process_thoughts error: ${msg}`);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: search_journal
// ---------------------------------------------------------------------------

server.tool(
  "search_journal",
  "Search through your private journal entries using natural language queries. Returns semantically similar entries ranked by relevance.",
  {
    query: z
      .string()
      .describe(
        "Natural language search query (e.g., 'times I felt frustrated with TypeScript')"
      ),
    limit: z.number().optional().default(10).describe("Max results (default 10)"),
    type: z
      .enum(["project", "user", "both"])
      .optional()
      .default("both")
      .describe("Search scope (default: both)"),
    sections: z
      .array(z.string())
      .optional()
      .describe("Filter by section types (e.g., ['feelings', 'technical_insights'])"),
  },
  async ({ query, limit, type, sections }) => {
    try {
      const results = await getJournalSearch().search(query, {
        limit: limit ?? 10,
        type: (type as "project" | "user" | "both") ?? "both",
        sections: sections ?? undefined,
      });

      const text =
        results.length > 0
          ? `Found ${results.length} relevant entries:\n\n${results
              .map(
                (r, i) =>
                  `${i + 1}. [Score: ${r.score.toFixed(3)}] ${new Date(r.timestamp).toLocaleDateString()} (${r.type})\n` +
                  `   Sections: ${r.sections.join(", ")}\n` +
                  `   Path: ${r.path}\n` +
                  `   Excerpt: ${r.excerpt}\n`
              )
              .join("\n")}`
          : "No relevant entries found.";

      return { content: [{ type: "text" as const, text }] };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] search_journal error: ${msg}`);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: read_journal_entry
// ---------------------------------------------------------------------------

server.tool(
  "read_journal_entry",
  "Read the full content of a specific journal entry by file path.",
  {
    path: z.string().describe("File path to the journal entry (from search results)"),
  },
  async ({ path: filePath }) => {
    try {
      const content = getJournalSearch().readEntry(filePath);
      if (content === null) {
        return {
          content: [{ type: "text" as const, text: "Entry not found" }],
          isError: true,
        };
      }
      return { content: [{ type: "text" as const, text: content }] };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] read_journal_entry error: ${msg}`);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: list_recent_entries
// ---------------------------------------------------------------------------

server.tool(
  "list_recent_entries",
  "Get recent journal entries in chronological order.",
  {
    limit: z.number().optional().default(10).describe("Max entries (default 10)"),
    type: z
      .enum(["project", "user", "both"])
      .optional()
      .default("both")
      .describe("List scope (default: both)"),
    days: z
      .number()
      .optional()
      .default(30)
      .describe("Number of days back to search (default 30)"),
  },
  async ({ limit, type, days }) => {
    try {
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - (days ?? 30));

      const results = getJournalSearch().listRecent({
        limit: limit ?? 10,
        type: (type as "project" | "user" | "both") ?? "both",
        dateRange: { start: startDate },
      });

      const text =
        results.length > 0
          ? `Recent entries (last ${days ?? 30} days):\n\n${results
              .map(
                (r, i) =>
                  `${i + 1}. ${new Date(r.timestamp).toLocaleDateString()} (${r.type})\n` +
                  `   Sections: ${r.sections.join(", ")}\n` +
                  `   Path: ${r.path}\n` +
                  `   Excerpt: ${r.excerpt}\n`
              )
              .join("\n")}`
          : `No entries found in the last ${days ?? 30} days.`;

      return { content: [{ type: "text" as const, text }] };
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[context-lake] list_recent_entries error: ${msg}`);
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
  console.error("[context-lake] MCP server started on stdio (context-lake + journal)");
}

main().catch((err) => {
  console.error("[context-lake] Fatal error:", err);
  process.exit(1);
});
