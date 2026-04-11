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
  // Repo-scope routing
  repo_slug?: string;
  session_handoff?: boolean;
  branch?: string;
  description?: string;
}

// ---------------------------------------------------------------------------
// Corruption detection — catches LLM XML emit errors before writing
// ---------------------------------------------------------------------------

const XML_POLLUTION_PATTERNS: RegExp[] = [
  /<\/parameter>/,
  /<parameter\s+name=/,
  /<\/feelings>/,
  /<\/project_notes>/,
  /<\/technical_insights>/,
  /<\/user_context>/,
  /<\/world_knowledge>/,
  /<invoke\s+name=/,
  /<function_calls>/,
];

export function detectFieldCorruption(thoughts: ThoughtsInput): void {
  for (const [field, value] of Object.entries(thoughts)) {
    if (typeof value !== "string") continue;
    for (const pattern of XML_POLLUTION_PATTERNS) {
      if (pattern.test(value)) {
        throw new Error(
          `Field '${field}' contains tool-call XML marker (${pattern}). ` +
          `This indicates an LLM emit parse error. Retry the call.`
        );
      }
    }
  }
}

// Fields whose values the LLM can corrupt by collapsing adjacent parameter
// blocks. Routing fields (repo_slug, session_handoff, branch, description)
// are excluded — they aren't content and don't contain multi-line strings.
const CORRUPTIBLE_FIELDS = [
  "feelings",
  "project_notes",
  "user_context",
  "technical_insights",
  "world_knowledge",
] as const;
type CorruptibleField = (typeof CORRUPTIBLE_FIELDS)[number];

function isCorruptibleField(s: string): s is CorruptibleField {
  return (CORRUPTIBLE_FIELDS as readonly string[]).includes(s);
}

// Salvages data from LLM XML emit corruption before validation.
//
// When the LLM emits a tool call with multiple parameter blocks, it sometimes
// collapses the closing tag of one parameter with the opening of the next,
// producing bled content like:
//
//   feelings: "real feelings</feelings>\n<parameter name=\"project_notes\">real notes"
//
// This function detects `</SOURCE>\s*<parameter name="TARGET">` boundaries,
// splits the content, and re-routes the bled fragment to TARGET. Subsequent
// `</parameter>\s*<parameter name="...">` transitions inside the bled
// fragment are also walked. Called before detectFieldCorruption so only
// truly unsalvageable corruption still throws.
export function repairFieldCorruption(thoughts: ThoughtsInput): ThoughtsInput {
  const repaired: ThoughtsInput = { ...thoughts };

  for (const source of CORRUPTIBLE_FIELDS) {
    const value = repaired[source];
    if (typeof value !== "string") continue;

    const firstBleed = value.match(
      new RegExp(`</${source}>\\s*<parameter\\s+name="([^"]+)">`)
    );
    if (!firstBleed || firstBleed.index === undefined) continue;

    repaired[source] = value.slice(0, firstBleed.index);

    let currentField: string = firstBleed[1];
    let rest = value.slice(firstBleed.index + firstBleed[0].length);

    while (true) {
      const nextBoundary = rest.match(
        /<\/parameter>\s*<parameter\s+name="([^"]+)">/
      );
      if (!nextBoundary || nextBoundary.index === undefined) {
        const content = rest.replace(/<\/parameter>\s*$/, "");
        if (isCorruptibleField(currentField)) {
          repaired[currentField] = content;
        }
        break;
      }

      const content = rest.slice(0, nextBoundary.index);
      if (isCorruptibleField(currentField)) {
        repaired[currentField] = content;
      }
      currentField = nextBoundary[1];
      rest = rest.slice(nextBoundary.index + nextBoundary[0].length);
    }
  }

  return repaired;
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

  async writeThoughts(
    rawThoughts: ThoughtsInput
  ): Promise<{
    path: string;
    entryId: string;
    repoSlug: string | null;
    projectPath?: string;
    userPath?: string;
  }> {
    // Repair LLM XML emit corruption before validation — salvages data that
    // would otherwise be rejected. Unsalvageable corruption still throws.
    const thoughts = repairFieldCorruption(rawThoughts);
    detectFieldCorruption(thoughts);

    const timestamp = new Date();
    // Compute timestamp parts ONCE — formatTimestamp uses Math.random for the
    // microsecond suffix, so calling it multiple times produces different file
    // names. We need a single deterministic ID shared across project + user
    // writes so the returned handoff_id corresponds to the actual files on disk.
    const dateStr = this.formatDate(timestamp);
    const timeStr = this.formatTimestamp(timestamp);
    const entryId = `${dateStr}/${timeStr}`;

    // ── Repo-scoped write: ALL fields → single file under _repos/{slug}/ ──
    if (thoughts.repo_slug) {
      const repoBasePath = join(this.userPath, "_repos", thoughts.repo_slug);
      const filePath = await this.writeToLocation(
        thoughts,
        timestamp,
        repoBasePath,
        dateStr,
        timeStr
      );
      return {
        path: filePath,
        entryId,
        repoSlug: thoughts.repo_slug,
        userPath: filePath,
      };
    }

    // ── Legacy dual-write: project_notes → project dir, others → user dir ──
    const writes: Array<Promise<{ kind: "project" | "user"; path: string }>> = [];

    if (thoughts.project_notes) {
      writes.push(
        this.writeToLocation(
          { project_notes: thoughts.project_notes },
          timestamp,
          this.projectPath,
          dateStr,
          timeStr
        ).then((path) => ({ kind: "project" as const, path }))
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
      writes.push(
        this.writeToLocation(
          userThoughts,
          timestamp,
          this.userPath,
          dateStr,
          timeStr
        ).then((path) => ({ kind: "user" as const, path }))
      );
    }

    const results = await Promise.all(writes);
    const projectPath = results.find((r) => r.kind === "project")?.path;
    const userPath = results.find((r) => r.kind === "user")?.path;

    return {
      path: userPath ?? projectPath ?? "",
      entryId,
      repoSlug: null,
      projectPath,
      userPath,
    };
  }

  private async writeToLocation(
    thoughts: ThoughtsInput,
    timestamp: Date,
    basePath: string,
    dateStr: string,
    timeStr: string
  ): Promise<string> {
    const dayDir = join(basePath, dateStr);
    if (!existsSync(dayDir)) mkdirSync(dayDir, { recursive: true });

    const filePath = join(dayDir, `${timeStr}.md`);
    const content = this.formatThoughts(thoughts, timestamp);
    writeFileSync(filePath, content, "utf8");

    // Fire-and-forget embedding generation (2026-04-07 perf fix).
    // Previously this was `await`-ed, blocking the write response on
    // MiniLM-L6-v2 inference (~30-100ms per call). The try/catch was there
    // but the await was unnecessary — embedding failures are non-fatal and
    // search_journal for very recent entries is acceptable-to-miss.
    // The returned file path is safe to use immediately; embedding populates
    // the search index in the background.
    void this.generateEmbeddingForEntry(filePath, content, timestamp).catch(
      () => {
        // Silent — search just won't find this entry until a retry/next write
      }
    );

    return filePath;
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

    // Build optional frontmatter fields for repo-scope routing
    const extraFrontmatter: string[] = [];
    if (thoughts.repo_slug) {
      extraFrontmatter.push(`repo_slug: ${thoughts.repo_slug}`);
    }
    if (thoughts.session_handoff) {
      extraFrontmatter.push(`session_handoff: true`);
    }
    if (thoughts.branch) {
      extraFrontmatter.push(`branch: ${thoughts.branch}`);
    }
    if (thoughts.description) {
      extraFrontmatter.push(`description: "${thoughts.description}"`);
    }
    const extraBlock = extraFrontmatter.length > 0
      ? "\n" + extraFrontmatter.join("\n")
      : "";

    return `---
title: "${timeDisplay} - ${dateDisplay}"
date: ${timestamp.toISOString()}
timestamp: ${timestamp.getTime()}${extraBlock}
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
