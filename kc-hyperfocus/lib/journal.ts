/**
 * journal.ts — Journal write + path resolution.
 * Dual-write: project_notes → project dir, other sections → user dir.
 * Generates embeddings on write for semantic search.
 *
 * Ported from obra/private-journal-mcp, adapted for Bun runtime.
 */

import { mkdirSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { EmbeddingService, type EmbeddingData } from "./embeddings.ts";

// ---------------------------------------------------------------------------
// Path resolution
// ---------------------------------------------------------------------------

export function resolveProjectJournalPath(): string {
  const cwd = process.cwd();
  if (cwd !== "/" && cwd !== "/System" && cwd !== "/usr") {
    return join(cwd, ".private-journal");
  }
  return join(process.env.HOME || "/tmp", ".private-journal");
}

export function resolveUserJournalPath(): string {
  const home = process.env.HOME || process.env.USERPROFILE || "/tmp";
  return join(home, ".private-journal");
}

// ---------------------------------------------------------------------------
// Thoughts input
// ---------------------------------------------------------------------------

export interface ThoughtsInput {
  feelings?: string;
  project_notes?: string;
  user_context?: string;
  technical_insights?: string;
  world_knowledge?: string;
}

// ---------------------------------------------------------------------------
// Journal writer
// ---------------------------------------------------------------------------

export class JournalWriter {
  private projectPath: string;
  private userPath: string;
  private embeddingService: EmbeddingService;

  constructor(projectPath?: string, userPath?: string) {
    this.projectPath = projectPath || resolveProjectJournalPath();
    this.userPath = userPath || resolveUserJournalPath();
    this.embeddingService = EmbeddingService.getInstance();
  }

  async writeThoughts(thoughts: ThoughtsInput): Promise<void> {
    const timestamp = new Date();

    // Split: project_notes → project dir, rest → user dir
    if (thoughts.project_notes) {
      await this.writeToLocation(
        { project_notes: thoughts.project_notes },
        timestamp,
        this.projectPath
      );
    }

    const userThoughts: ThoughtsInput = {
      feelings: thoughts.feelings,
      user_context: thoughts.user_context,
      technical_insights: thoughts.technical_insights,
      world_knowledge: thoughts.world_knowledge,
    };
    const hasUserContent = Object.values(userThoughts).some((v) => v != null);
    if (hasUserContent) {
      await this.writeToLocation(userThoughts, timestamp, this.userPath);
    }
  }

  private async writeToLocation(
    thoughts: ThoughtsInput,
    timestamp: Date,
    basePath: string
  ): Promise<void> {
    const dateStr = this.formatDate(timestamp);
    const timeStr = this.formatTimestamp(timestamp);

    const dayDir = join(basePath, dateStr);
    if (!existsSync(dayDir)) mkdirSync(dayDir, { recursive: true });

    const filePath = join(dayDir, `${timeStr}.md`);
    const content = this.formatThoughts(thoughts, timestamp);
    writeFileSync(filePath, content, "utf8");

    // Best-effort embedding generation
    try {
      await this.generateEmbeddingForEntry(filePath, content, timestamp);
    } catch {
      // Don't fail write if embedding fails
    }
  }

  private formatDate(d: Date): string {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  private formatTimestamp(d: Date): string {
    const h = String(d.getHours()).padStart(2, "0");
    const m = String(d.getMinutes()).padStart(2, "0");
    const s = String(d.getSeconds()).padStart(2, "0");
    const us = String(
      d.getMilliseconds() * 1000 + Math.floor(Math.random() * 1000)
    ).padStart(6, "0");
    return `${h}-${m}-${s}-${us}`;
  }

  private formatThoughts(thoughts: ThoughtsInput, timestamp: Date): string {
    const timeDisplay = timestamp.toLocaleTimeString("en-US", {
      hour12: true,
      hour: "numeric",
      minute: "2-digit",
      second: "2-digit",
    });
    const dateDisplay = timestamp.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    const sections: string[] = [];
    if (thoughts.feelings) sections.push(`## Feelings\n\n${thoughts.feelings}`);
    if (thoughts.project_notes)
      sections.push(`## Project Notes\n\n${thoughts.project_notes}`);
    if (thoughts.user_context)
      sections.push(`## User Context\n\n${thoughts.user_context}`);
    if (thoughts.technical_insights)
      sections.push(
        `## Technical Insights\n\n${thoughts.technical_insights}`
      );
    if (thoughts.world_knowledge)
      sections.push(`## World Knowledge\n\n${thoughts.world_knowledge}`);

    return `---
title: "${timeDisplay} - ${dateDisplay}"
date: ${timestamp.toISOString()}
timestamp: ${timestamp.getTime()}
---

${sections.join("\n\n")}
`;
  }

  private async generateEmbeddingForEntry(
    filePath: string,
    content: string,
    timestamp: Date
  ): Promise<void> {
    const { text, sections } =
      this.embeddingService.extractSearchableText(content);
    if (text.trim().length === 0) return;

    const embedding = await this.embeddingService.generateEmbedding(text);
    const data: EmbeddingData = {
      embedding,
      text,
      sections,
      timestamp: timestamp.getTime(),
      path: filePath,
    };
    this.embeddingService.saveEmbedding(filePath, data);
  }
}
