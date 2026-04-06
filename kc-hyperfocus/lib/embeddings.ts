/**
 * embeddings.ts — Local embedding service for semantic journal search.
 * Uses @xenova/transformers (MiniLM) for vector generation.
 * Stores embeddings as .embedding sidecar files alongside .md journal entries.
 *
 * Ported from obra/private-journal-mcp, adapted for Bun runtime.
 */

import { pipeline, type FeatureExtractionPipeline } from "@xenova/transformers";
import { readFileSync, writeFileSync, existsSync } from "node:fs";

export interface EmbeddingData {
  embedding: number[];
  text: string;
  sections: string[];
  timestamp: number;
  path: string;
}

export class EmbeddingService {
  private static instance: EmbeddingService;
  private extractor: FeatureExtractionPipeline | null = null;
  private readonly modelName = "Xenova/all-MiniLM-L6-v2";
  private initPromise: Promise<void> | null = null;

  private constructor() {}

  static getInstance(): EmbeddingService {
    if (!EmbeddingService.instance) {
      EmbeddingService.instance = new EmbeddingService();
    }
    return EmbeddingService.instance;
  }

  async initialize(): Promise<void> {
    if (this.initPromise) return this.initPromise;
    this.initPromise = this.doInitialize();
    return this.initPromise;
  }

  private async doInitialize(): Promise<void> {
    try {
      console.error("Loading embedding model...");
      this.extractor = await pipeline("feature-extraction", this.modelName);
      console.error("Embedding model loaded successfully");
    } catch (error) {
      console.error("Failed to load embedding model:", error);
      throw error;
    }
  }

  async generateEmbedding(text: string): Promise<number[]> {
    if (!this.extractor) await this.initialize();
    if (!this.extractor) throw new Error("Embedding model not initialized");

    const result = await this.extractor(text, {
      pooling: "mean",
      normalize: true,
    });
    return Array.from(result.data as Float32Array);
  }

  cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) {
      throw new Error("Vectors must have same length");
    }

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    if (normA === 0 || normB === 0) return 0;
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  saveEmbedding(filePath: string, data: EmbeddingData): void {
    const embeddingPath = filePath.replace(/\.md$/, ".embedding");
    writeFileSync(embeddingPath, JSON.stringify(data, null, 2), "utf8");
  }

  loadEmbedding(filePath: string): EmbeddingData | null {
    const embeddingPath = filePath.replace(/\.md$/, ".embedding");
    if (!existsSync(embeddingPath)) return null;
    try {
      return JSON.parse(readFileSync(embeddingPath, "utf8"));
    } catch {
      return null;
    }
  }

  extractSearchableText(markdown: string): {
    text: string;
    sections: string[];
  } {
    // Remove YAML frontmatter
    const withoutFrontmatter = markdown.replace(/^---\n.*?\n---\n/s, "");

    // Extract section names
    const sections: string[] = [];
    const sectionMatches = withoutFrontmatter.match(/^## (.+)$/gm);
    if (sectionMatches) {
      sections.push(...sectionMatches.map((m) => m.replace("## ", "")));
    }

    // Clean for embedding
    const cleanText = withoutFrontmatter
      .replace(/^## .+$/gm, "")
      .replace(/\n{3,}/g, "\n\n")
      .trim();

    return { text: cleanText, sections };
  }
}
