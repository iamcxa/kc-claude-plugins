---
name: kc-cache-insight
description: Manually cache an insight about a file or module to the context lake. Use when you want to preserve understanding about code you just explored. Also shows lake status and metrics.
allowed-tools:
  - mcp__plugin_kc-hyperfocus_context-lake__store_insight
  - mcp__plugin_kc-hyperfocus_context-lake__search_insights
  - mcp__plugin_kc-hyperfocus_context-lake__get_metrics
  - mcp__plugin_kc-hyperfocus_context-lake__lake_status
---

# /kc-cache-insight [file_path | --dashboard | --search | --status | --metrics]

Cache an insight about a file to the context lake, or view cache status.

## Routes

### No args or `<file_path>`

1. If `<file_path>` provided → generate insight for that file
2. If no args → generate insight for the most recently discussed file in conversation
3. **If no file can be determined** (no args AND no file discussed in conversation) → fall back to `--status` route. Do NOT guess a file path or error out silently.
4. **Read the target file** to validate it exists and refresh your understanding. If Read fails (file not found), report: "File {path} not found — cannot generate insight." and stop. Do NOT fabricate an insight for a nonexistent file.
5. Produce a 3-8 sentence summary **in English** answering:
   - What does this file do?
   - How is it used? (callers, consumers)
   - What are the key functions/classes?
   - What are the gotchas / dependencies / limitations?
   **Language rule: Always write insights in English**, regardless of the conversation language. This ensures consistency for FTS5 search and cross-session readability.
6. Present the insight to the user for confirmation
7. On confirmation → call `store_insight` with `source: "manual"`
8. Report: "Cached insight for {file_path} to context lake"

### `--search [query | file_path]`

Search cached insights. Two modes:
- `--search src/foo.ts` → exact file path lookup
- `--search "impact analysis"` → FTS5 keyword search across all cached insights

Call `search_insights` with `file_path` (if looks like a path) or `query` (if looks like keywords).
Present each result with: file path, source, freshness (fresh/stale), and the full insight content.

**If no results found**, report: "No cached insights found for '{query}'. Try a broader search term, or cache an insight first with `/kc-cache-insight <file_path>`."

### `--dashboard`

Overview of ALL repos' context lake status. Run this Bash command and present the output as a table:

```bash
bun -e "
import { Database } from 'bun:sqlite';
import { readdirSync, existsSync } from 'fs';
import { join } from 'path';
const dir = (process.env.HOME || '/tmp') + '/.claude/context-lake';
if (!existsSync(dir)) { console.log('[]'); process.exit(0); }
const dbs = readdirSync(dir).filter(f => f.endsWith('.db'));
const rows = [];
for (const f of dbs) {
  try {
    const db = new Database(join(dir, f), { readonly: true });
    db.run('PRAGMA busy_timeout=5000');
    const ic = db.query('SELECT COUNT(*) as total, SUM(CASE WHEN stale=0 THEN 1 ELSE 0 END) as fresh, SUM(CASE WHEN stale=1 THEN 1 ELSE 0 END) as stale FROM insights').get();
    const mc = db.query('SELECT event, COUNT(*) as cnt FROM metrics GROUP BY event').all();
    const counts = Object.fromEntries(mc.map(r => [r.event, r.cnt]));
    const hits = counts.hit || 0;
    const misses = counts.miss || 0;
    const rate = hits + misses > 0 ? Math.round(hits / (hits + misses) * 1000) / 10 : null;
    // Savings: sum fileLines from hit details (recorded since v1.2.1)
    // Each hit line ≈ 1.5 tokens of reasoning overhead saved
    const sl = db.query("SELECT SUM(json_extract(details, '$.fileLines')) as total FROM metrics WHERE event='hit' AND details IS NOT NULL").get();
    const savedLines = sl?.total || 0;
    const savedTokens = Math.round(savedLines * 1.5);
    const handoffs = counts.handoff || 0;
    const resumes = counts.resume || 0;
    rows.push({ repo: f.replace('.db',''), insights: ic.total||0, fresh: ic.fresh||0, stale: ic.stale||0, hits, misses, hitRate: rate, nudges: counts.nudge||0, stores: counts.store||0, savedTokens, handoffs, resumes });
    db.close();
  } catch {}
}
rows.sort((a,b) => b.insights - a.insights);
console.log(JSON.stringify(rows));
"
```

Present the JSON output as TWO markdown tables:

**Table 1 — Context Lake (cache performance)**
Columns: Repo, Insights (fresh/stale), Hit Rate, Hits, Misses, Nudges, Stores, Est. Saved Tokens.
Format `savedTokens` as `Nk` for thousands (e.g., `13500` → `13.5k`). Add a footnote: "Est. saved = fileLines × 1.5 tokens reasoning overhead per hit. Only counts hits with recorded fileLines (tracking started v1.2.1)."

**Table 2 — Session Lifecycle (handoff/resume)**
Columns: Repo, Handoffs, Resumes, Resume Rate.
Calculate resume rate as `resumes / handoffs * 100`. Only show repos with handoffs > 0. Add a footnote: "Handoff/resume tracking started v1.2.1 — historical handoffs via journal are not counted."

**Empty state**: If the JSON output is `[]` (no DBs found), report: "No context lake databases found yet. Cache an insight with `/kc-cache-insight <file_path>` to get started."

### `--status`

Call `lake_status` and present the results in a readable format (current repo only).

**If the MCP tool returns an error** (e.g., DB not initialized for this repo), report: "Context lake not initialized for this repo yet. Cache an insight with `/kc-cache-insight <file_path>` to create the database."

### `--metrics [since]`

Call `get_metrics` with optional `since` date (default: 7 days ago, format: ISO date string).
Present:
- Hit rate percentage
- Nudge count and conversion rate (nudges that led to stores)
- Total stores / hits / misses
- Top cached files by hit count

**If the MCP tool returns an error or empty data** (e.g., DB not initialized, no metrics recorded yet), report: "No metrics data available yet. The context lake records metrics automatically as you work — use `/kc-cache-insight <file_path>` to cache your first insight."
