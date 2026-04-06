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
    // Handoff savings: each resume saves ~15K tokens vs re-exploring from scratch
    // Subtract actual handoff entry size (entryTokens) if recorded
    const ht = db.query("SELECT SUM(json_extract(details, '$.entryTokens')) as total FROM metrics WHERE event='handoff' AND details IS NOT NULL").get();
    const handoffTokens = ht?.total || (handoffs * 700); // fallback: 700 tokens avg
    const resumeSaved = resumes > 0 ? (resumes * 15000) - handoffTokens : 0;
    rows.push({ repo: f.replace('.db',''), insights: ic.total||0, fresh: ic.fresh||0, stale: ic.stale||0, hits, misses, hitRate: rate, nudges: counts.nudge||0, stores: counts.store||0, savedTokens, handoffs, resumes, resumeSaved });
    db.close();
  } catch {}
}
rows.sort((a,b) => b.insights - a.insights);
console.log(JSON.stringify(rows));
"
```

Then run a **second** Bash command for journal statistics:

```bash
bun -e "
import { readdirSync, statSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';
const HOME = process.env.HOME || '/tmp';
const CWD = process.cwd();
const sources = [];

// User-level journal
const userDir = join(HOME, '.private-journal');
if (existsSync(userDir)) sources.push({ type: 'user', path: userDir, label: '~/.private-journal' });

// Project-level journal (CWD)
const projDir = join(CWD, '.private-journal');
if (existsSync(projDir)) sources.push({ type: 'project', path: projDir, label: CWD.split('/').pop() });

// Scan other project dirs for journals
const projectRoot = join(HOME, 'Project');
if (existsSync(projectRoot)) {
  try {
    for (const d of readdirSync(projectRoot)) {
      const jp = join(projectRoot, d, '.private-journal');
      if (existsSync(jp) && jp !== projDir) {
        sources.push({ type: 'project', path: jp, label: d });
      }
    }
  } catch {}
}

const results = [];
for (const src of sources) {
  try {
    const dayDirs = readdirSync(src.path).filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d));
    let totalEntries = 0, totalEmbeddings = 0, totalSections = { feelings: 0, project_notes: 0, technical_insights: 0, user_context: 0, world_knowledge: 0 };
    const now = Date.now();
    let last7d = 0, last30d = 0;
    for (const dd of dayDirs) {
      const dp = join(src.path, dd);
      try {
        const files = readdirSync(dp);
        const mds = files.filter(f => f.endsWith('.md'));
        const embs = files.filter(f => f.endsWith('.embedding'));
        totalEntries += mds.length;
        totalEmbeddings += embs.length;
        // Parse date from dir name for recency
        const dirDate = new Date(dd + 'T00:00:00');
        const age = now - dirDate.getTime();
        if (age <= 7 * 86400000) last7d += mds.length;
        if (age <= 30 * 86400000) last30d += mds.length;
        // Count sections in md files (sample up to 20 per day)
        for (const md of mds.slice(0, 20)) {
          try {
            const content = readFileSync(join(dp, md), 'utf8');
            if (content.includes('## Feelings')) totalSections.feelings++;
            if (content.includes('## Project Notes')) totalSections.project_notes++;
            if (content.includes('## Technical Insights')) totalSections.technical_insights++;
            if (content.includes('## User Context')) totalSections.user_context++;
            if (content.includes('## World Knowledge')) totalSections.world_knowledge++;
          } catch {}
        }
      } catch {}
    }
    results.push({ label: src.label, type: src.type, entries: totalEntries, embeddings: totalEmbeddings, embeddingPct: totalEntries > 0 ? Math.round(totalEmbeddings / totalEntries * 100) : 0, last7d, last30d, ...totalSections });
  } catch {}
}
console.log(JSON.stringify(results));
"
```

Present the combined output as THREE markdown tables:

**Table 1 — Context Lake (cache performance)**
Columns: Repo, Insights (fresh/stale), Hit Rate, Hits, Misses, Nudges, Stores, Est. Saved Tokens.
Format `savedTokens` as `Nk` for thousands (e.g., `13500` → `13.5k`). Add a footnote: "Est. saved = fileLines × 1.5 tokens reasoning overhead per hit. Only counts hits with recorded fileLines (tracking started v1.2.1)."

**Table 2 — Session Lifecycle (handoff/resume)**
Columns: Repo, Handoffs, Resumes, Resume Rate, Est. Saved Tokens.
Calculate resume rate as `resumes / handoffs * 100`. Format `resumeSaved` as `Nk`. Only show repos with handoffs > 0. Add a footnote: "Each resume saves ~15K tokens vs re-exploring from scratch. Handoff entry cost (~700 tokens avg) subtracted. Tracking started v1.2.1."

**Table 3 — Journal (entry statistics)**
Columns: Source, Type, Entries, Last 7d, Last 30d, Embeddings %, Feelings, Project Notes, Tech Insights.
- `Source` = the `label` field
- `Type` = user or project
- `Embeddings %` = `embeddingPct` (100% means all entries have vector embeddings for search)
- Feelings/Project Notes/Tech Insights = section counts from `totalSections`
- Skip `user_context` and `world_knowledge` columns if all zeros across all sources.
- Add a footnote: "Embedding % shows how many entries have vector embeddings for semantic search. Run `search_journal` to trigger lazy embedding generation for entries without embeddings."

**Empty state for journal**: If the journal JSON output is `[]`, report: "No journal entries found. Use `/kc-session-handoff` to write your first journal entry."

**Empty state for context lake**: If the context lake JSON output is `[]` (no DBs found), report: "No context lake databases found yet. Cache an insight with `/kc-cache-insight <file_path>` to get started."

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
