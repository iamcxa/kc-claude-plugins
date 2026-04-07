#!/usr/bin/env bun
/**
 * backfill-embeddings.ts — Compute content embeddings for existing insights.
 *
 * Iterates rows with NULL content_embedding, generates embedding via
 * EmbeddingService (MiniLM-L6-v2), stores the BLOB back on the row.
 *
 * Idempotent — safe to re-run. Skips rows that already have embeddings.
 *
 * Usage:
 *   cd kc-claude-plugins/kc-hyperfocus
 *   bun scripts/backfill-embeddings.ts <repo-root>
 */

import { openLake } from "../lib/context-lake";
import { EmbeddingService } from "../lib/embeddings";

const repoRoot = process.argv[2];
if (!repoRoot) {
  console.error("Usage: bun scripts/backfill-embeddings.ts <repo-root>");
  process.exit(1);
}

console.log(`[backfill] Opening context lake for: ${repoRoot}`);
const db = openLake(repoRoot);

// Find rows missing embeddings
const rows = db
  .query(
    "SELECT id, file_path, content FROM insights WHERE content_embedding IS NULL"
  )
  .all() as { id: number; file_path: string; content: string }[];

if (rows.length === 0) {
  console.log("[backfill] All insights already have embeddings. Nothing to do.");
  db.close();
  process.exit(0);
}

console.log(`[backfill] Found ${rows.length} insights needing embeddings`);

// Load MiniLM
console.log(`[backfill] Initializing embedding model...`);
const svc = EmbeddingService.getInstance();
await svc.initialize();
console.log(`[backfill] Model ready. Generating embeddings...`);

let processed = 0;
for (const row of rows) {
  try {
    const t0 = performance.now();
    const embedding = await svc.generateEmbedding(row.content);
    const t1 = performance.now();

    // Serialize Float32Array → Uint8Array (matches embeddingToBlob in lib)
    const f32 = new Float32Array(embedding);
    const blob = new Uint8Array(f32.buffer, f32.byteOffset, f32.byteLength);

    db.query("UPDATE insights SET content_embedding = ? WHERE id = ?").run(
      blob,
      row.id
    );

    processed++;
    console.log(
      `[backfill] id=${row.id} ${row.file_path} — ${(t1 - t0).toFixed(0)}ms`
    );
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`[backfill] id=${row.id} FAILED: ${msg}`);
  }
}

console.log(`[backfill] Done: ${processed}/${rows.length} embeddings stored`);
db.close();
