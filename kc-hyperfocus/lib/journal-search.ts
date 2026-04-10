/**
 * journal-search.ts — Search, list, and read journal entries.
 * Vector similarity search via embeddings, recent listing, single-entry read.
 *
 * Ported from obra/private-journal-mcp, adapted for Bun runtime.
 */

import {
  readdirSync,
  readFileSync,
  statSync,
  existsSync,
} from "node:fs";
import { join } from "node:path";
import { EmbeddingService, type EmbeddingData } from "./embeddings.ts";
import {
  resolveProjectJournalPath,
  resolveUserJournalPath,
} from "./journal.ts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SearchResult {
  path: string;
  score: number;
  text: string;
  sections: string[];
  timestamp: number;
  excerpt: string;
  type: "project" | "user";
}

export interface SearchOptions {
  limit?: number;
  minScore?: number;
  sections?: string[];
  dateRange?: { start?: Date; end?: Date };
  type?: "project" | "user" | "both";
}

// ---------------------------------------------------------------------------
// Search service
// ---------------------------------------------------------------------------

export class JournalSearchService {
  private embeddingService: EmbeddingService;
  private projectPath: string;
  private userPath: string;

  constructor(projectPath?: string, userPath?: string) {
    this.embeddingService = EmbeddingService.getInstance();
    this.projectPath = projectPath || resolveProjectJournalPath();
    this.userPath = userPath || resolveUserJournalPath();
  }

  // -------------------------------------------------------------------------
  // search — vector similarity
  // -------------------------------------------------------------------------

  async search(
    query: string,
    options: SearchOptions = {}
  ): Promise<SearchResult[]> {
    const {
      limit = 10,
      minScore = 0.1,
      sections,
      dateRange,
      type = "both",
    } = options;

    const queryEmbedding =
      await this.embeddingService.generateEmbedding(query);

    const all = this.collectEmbeddings(type);

    const filtered = all.filter((e) => {
      if (sections?.length) {
        const match = sections.some((s) =>
          e.sections.some((es) =>
            es.toLowerCase().includes(s.toLowerCase())
          )
        );
        if (!match) return false;
      }
      if (dateRange) {
        const d = new Date(e.timestamp);
        if (dateRange.start && d < dateRange.start) return false;
        if (dateRange.end && d > dateRange.end) return false;
      }
      return true;
    });

    return filtered
      .map((e) => ({
        path: e.path,
        score: this.embeddingService.cosineSimilarity(
          queryEmbedding,
          e.embedding
        ),
        text: e.text,
        sections: e.sections,
        timestamp: e.timestamp,
        excerpt: this.generateExcerpt(e.text, query),
        type: e.type,
      }))
      .filter((r) => r.score >= minScore)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }

  // -------------------------------------------------------------------------
  // listRecent — chronological
  // -------------------------------------------------------------------------

  listRecent(options: SearchOptions & {
    repoSlug?: string;
    sessionHandoffOnly?: boolean;
  } = {}): SearchResult[] {
    const { limit = 10, type = "both", dateRange, repoSlug, sessionHandoffOnly } = options;

    let all = this.collectEmbeddings(type);

    if (dateRange) {
      all = all.filter((e) => {
        const d = new Date(e.timestamp);
        if (dateRange.start && d < dateRange.start) return false;
        if (dateRange.end && d > dateRange.end) return false;
        return true;
      });
    }

    // Apply frontmatter-based filters
    if (repoSlug || sessionHandoffOnly) {
      all = all.filter((e) => {
        const fm = this.readFrontmatter(e.path);
        if (repoSlug && fm.repo_slug !== repoSlug) return false;
        if (sessionHandoffOnly && fm.session_handoff !== "true") return false;
        return true;
      });
    }

    return all
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit)
      .map((e) => ({
        path: e.path,
        score: 1,
        text: e.text,
        sections: e.sections,
        timestamp: e.timestamp,
        excerpt: this.generateExcerpt(e.text, "", 150),
        type: e.type,
      }));
  }

  // -------------------------------------------------------------------------
  // readEntry — single file read
  // -------------------------------------------------------------------------

  readEntry(filePath: string): string | null {
    try {
      return readFileSync(filePath, "utf8");
    } catch (e: any) {
      if (e?.code === "ENOENT") return null;
      throw e;
    }
  }

  // -------------------------------------------------------------------------
  // Private helpers
  // -------------------------------------------------------------------------

  private collectEmbeddings(
    type: "project" | "user" | "both"
  ): Array<EmbeddingData & { type: "project" | "user" }> {
    const result: Array<EmbeddingData & { type: "project" | "user" }> = [];

    if (type === "both" || type === "project") {
      result.push(...this.loadEmbeddingsFromPath(this.projectPath, "project"));
    }
    if (type === "both" || type === "user") {
      result.push(...this.loadEmbeddingsFromPath(this.userPath, "user"));
      // Also scan _repos/* slug dirs under user path
      const reposDir = join(this.userPath, "_repos");
      if (existsSync(reposDir)) {
        try {
          const slugDirs = readdirSync(reposDir);
          for (const slug of slugDirs) {
            const slugPath = join(reposDir, slug);
            try {
              if (!statSync(slugPath).isDirectory()) continue;
            } catch { continue; }
            result.push(...this.loadEmbeddingsFromPath(slugPath, "project"));
          }
        } catch {
          // Skip unreadable _repos dir
        }
      }
    }

    return result;
  }

  private readFrontmatter(embeddingPath: string): Record<string, string> {
    const mdPath = embeddingPath.replace(/\.embedding$/, ".md");
    try {
      const content = readFileSync(mdPath, "utf8");
      const lines = content.split("\n");
      if (lines[0]?.trim() !== "---") return {};
      const meta: Record<string, string> = {};
      for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim() === "---") break;
        const colonIdx = lines[i].indexOf(":");
        if (colonIdx === -1) continue;
        const key = lines[i].slice(0, colonIdx).trim();
        let value = lines[i].slice(colonIdx + 1).trim();
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }
        meta[key] = value;
      }
      return meta;
    } catch {
      return {};
    }
  }

  private loadEmbeddingsFromPath(
    basePath: string,
    type: "project" | "user"
  ): Array<EmbeddingData & { type: "project" | "user" }> {
    const embeddings: Array<EmbeddingData & { type: "project" | "user" }> = [];
    if (!existsSync(basePath)) return embeddings;

    try {
      const dayDirs = readdirSync(basePath);

      for (const dayDir of dayDirs) {
        const dayPath = join(basePath, dayDir);
        try {
          if (
            !statSync(dayPath).isDirectory() ||
            !/^\d{4}-\d{2}-\d{2}$/.test(dayDir)
          )
            continue;
        } catch {
          continue;
        }

        const files = readdirSync(dayPath).filter((f) =>
          f.endsWith(".embedding")
        );

        for (const file of files) {
          try {
            const data = JSON.parse(
              readFileSync(join(dayPath, file), "utf8")
            ) as EmbeddingData;
            embeddings.push({ ...data, type });
          } catch {
            // Skip corrupt embedding files
          }
        }
      }
    } catch {
      // Silently skip unreadable directories
    }

    return embeddings;
  }

  private generateExcerpt(
    text: string,
    query: string,
    maxLength = 200
  ): string {
    if (!query || query.trim() === "") {
      return text.slice(0, maxLength) + (text.length > maxLength ? "..." : "");
    }

    const queryWords = query.toLowerCase().split(/\s+/);
    const textLower = text.toLowerCase();

    let bestPos = 0;
    let bestScore = 0;

    for (let i = 0; i <= Math.max(0, text.length - maxLength); i += 20) {
      const window = textLower.slice(i, i + maxLength);
      const score = queryWords.reduce(
        (sum, w) => sum + (window.includes(w) ? 1 : 0),
        0
      );
      if (score > bestScore) {
        bestScore = score;
        bestPos = i;
      }
    }

    let excerpt = text.slice(bestPos, bestPos + maxLength);
    if (bestPos > 0) excerpt = "..." + excerpt;
    if (bestPos + maxLength < text.length) excerpt += "...";
    return excerpt;
  }
}
