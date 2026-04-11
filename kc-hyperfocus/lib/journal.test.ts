import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import {
  detectFieldCorruption,
  repairFieldCorruption,
  JournalWriter,
  type ThoughtsInput,
} from "./journal.ts";
import { mkdirSync, readFileSync, rmSync, existsSync } from "node:fs";
import { join } from "node:path";

describe("detectFieldCorruption", () => {
  it("throws on </parameter> in feelings field", () => {
    expect(() =>
      detectFieldCorruption({
        feelings: 'Good session.</feelings><parameter name="project_notes">Session Handoff:...',
      })
    ).toThrow("tool-call XML marker");
  });

  it("throws on <parameter name= in project_notes field", () => {
    expect(() =>
      detectFieldCorruption({
        project_notes: '<parameter name="feelings">leaked content',
      })
    ).toThrow("tool-call XML marker");
  });

  it("throws on <invoke name= pattern", () => {
    expect(() =>
      detectFieldCorruption({
        technical_insights: '<invoke name="some_tool">',
      })
    ).toThrow("tool-call XML marker");
  });

  it("passes clean content through without throwing", () => {
    expect(() =>
      detectFieldCorruption({
        feelings: "Productive session — solved the staging import blocker cleanly.",
        project_notes: "Session Handoff: gsd/v2.0 — Phase 24 done\n\n## Completed\n- Batch UPDATE refactor",
        technical_insights: "Batched UPDATE ... FROM (VALUES ...) AS data(...) is 500x faster than per-row.",
      })
    ).not.toThrow();
  });

  it("passes when all fields are undefined", () => {
    expect(() => detectFieldCorruption({})).not.toThrow();
  });

  it("includes field name in error message", () => {
    expect(() =>
      detectFieldCorruption({
        world_knowledge: "some text </parameter> more text",
      })
    ).toThrow("world_knowledge");
  });
});

describe("repairFieldCorruption", () => {
  it("splits feelings when </feelings><parameter name='project_notes'> bleed occurs", () => {
    const corrupted: ThoughtsInput = {
      feelings:
        'Good session.</feelings>\n<parameter name="project_notes">Session Handoff: test',
    };
    const repaired = repairFieldCorruption(corrupted);
    expect(repaired.feelings).toBe("Good session.");
    expect(repaired.project_notes).toBe("Session Handoff: test");
  });

  it("strips trailing </parameter> from the bled field", () => {
    const corrupted: ThoughtsInput = {
      feelings:
        'Good.</feelings>\n<parameter name="project_notes">Notes here</parameter>',
    };
    const repaired = repairFieldCorruption(corrupted);
    expect(repaired.feelings).toBe("Good.");
    expect(repaired.project_notes).toBe("Notes here");
  });

  it("preserves fields not affected by bleed", () => {
    const corrupted: ThoughtsInput = {
      feelings:
        'Curious.</feelings>\n<parameter name="project_notes">Handoff notes',
      technical_insights: "Already passed cleanly",
    };
    const repaired = repairFieldCorruption(corrupted);
    expect(repaired.feelings).toBe("Curious.");
    expect(repaired.project_notes).toBe("Handoff notes");
    expect(repaired.technical_insights).toBe("Already passed cleanly");
  });

  it("handles multi-field bleed across three parameter blocks", () => {
    const corrupted: ThoughtsInput = {
      feelings:
        'Good.</feelings>\n<parameter name="project_notes">Handoff</parameter>\n<parameter name="technical_insights">Learned X',
    };
    const repaired = repairFieldCorruption(corrupted);
    expect(repaired.feelings).toBe("Good.");
    expect(repaired.project_notes).toBe("Handoff");
    expect(repaired.technical_insights).toBe("Learned X");
  });

  it("is a no-op when no corruption markers present", () => {
    const clean: ThoughtsInput = {
      feelings: "All good",
      project_notes: "Handoff notes",
    };
    const repaired = repairFieldCorruption(clean);
    expect(repaired.feelings).toBe("All good");
    expect(repaired.project_notes).toBe("Handoff notes");
  });

  it("leaves detectFieldCorruption passing after repair", () => {
    const corrupted: ThoughtsInput = {
      feelings:
        'Good.</feelings>\n<parameter name="project_notes">Handoff notes',
    };
    const repaired = repairFieldCorruption(corrupted);
    expect(() => detectFieldCorruption(repaired)).not.toThrow();
  });

  it("preserves non-routing fields through repair", () => {
    const corrupted: ThoughtsInput = {
      feelings:
        'Good.</feelings>\n<parameter name="project_notes">Handoff',
      repo_slug: "spacedock",
      session_handoff: true,
      branch: "main",
      description: "test",
    };
    const repaired = repairFieldCorruption(corrupted);
    expect(repaired.repo_slug).toBe("spacedock");
    expect(repaired.session_handoff).toBe(true);
    expect(repaired.branch).toBe("main");
    expect(repaired.description).toBe("test");
  });
});

const TEST_BASE = "/tmp/journal-test";
const TEST_USER_PATH = join(TEST_BASE, "user");

describe("JournalWriter repo-scope routing", () => {
  beforeEach(() => {
    rmSync(TEST_BASE, { recursive: true, force: true });
    mkdirSync(TEST_BASE, { recursive: true });
  });

  afterEach(() => {
    rmSync(TEST_BASE, { recursive: true, force: true });
  });

  it("writes to _repos/{slug}/ when repo_slug is provided", async () => {
    const writer = new JournalWriter(join(TEST_BASE, "project"), TEST_USER_PATH);
    const result = await writer.writeThoughts({
      project_notes: "Session Handoff: test",
      feelings: "test feelings",
      repo_slug: "carlove",
    });

    expect(result.path).toContain("_repos/carlove/");
    expect(result.repoSlug).toBe("carlove");
    expect(existsSync(result.path)).toBe(true);
  });

  it("writes to flat user path when repo_slug is absent", async () => {
    const writer = new JournalWriter(join(TEST_BASE, "project"), TEST_USER_PATH);
    const result = await writer.writeThoughts({
      feelings: "just feelings",
    });

    expect(result.path).toContain(TEST_USER_PATH);
    expect(result.path).not.toContain("_repos");
    expect(result.repoSlug).toBeNull();
    expect(existsSync(result.path)).toBe(true);
  });

  it("merges all fields into one file when repo_slug is provided", async () => {
    const writer = new JournalWriter(join(TEST_BASE, "project"), TEST_USER_PATH);
    const result = await writer.writeThoughts({
      feelings: "Productive",
      project_notes: "Session Handoff: test\n\n## Completed\n- Task 1",
      technical_insights: "Batched UPDATEs are faster",
      repo_slug: "carlove",
      session_handoff: true,
      branch: "feat/test",
      description: "Test handoff",
    });

    const content = readFileSync(result.path, "utf8");
    expect(content).toContain("## Feelings");
    expect(content).toContain("## Project Notes");
    expect(content).toContain("## Technical Insights");
    expect(content).toContain("repo_slug: carlove");
    expect(content).toContain("session_handoff: true");
    expect(content).toContain("branch: feat/test");
    expect(content).toContain('description: "Test handoff"');
  });

  it("does NOT write repo_slug to frontmatter when absent", async () => {
    const writer = new JournalWriter(join(TEST_BASE, "project"), TEST_USER_PATH);
    const result = await writer.writeThoughts({
      feelings: "Just a note",
    });

    const content = readFileSync(result.path, "utf8");
    expect(content).not.toContain("repo_slug:");
    expect(content).not.toContain("session_handoff:");
  });

  it("repairs XML-bled fields before writing and persists both cleanly", async () => {
    const writer = new JournalWriter(join(TEST_BASE, "project"), TEST_USER_PATH);
    const result = await writer.writeThoughts({
      feelings:
        'Productive session.</feelings>\n<parameter name="project_notes">Session Handoff: repaired',
      repo_slug: "carlove",
    });

    expect(existsSync(result.path)).toBe(true);
    const content = readFileSync(result.path, "utf8");
    expect(content).toContain("## Feelings\n\nProductive session.");
    expect(content).toContain("## Project Notes\n\nSession Handoff: repaired");
    expect(content).not.toContain("<parameter");
    expect(content).not.toContain("</feelings>");
  });

  it("still throws when corruption is unsalvageable (bare </parameter>)", async () => {
    const writer = new JournalWriter(join(TEST_BASE, "project"), TEST_USER_PATH);
    await expect(
      writer.writeThoughts({
        feelings: "just closing tag </parameter> mid-sentence",
        repo_slug: "carlove",
      })
    ).rejects.toThrow("tool-call XML marker");
  });
});
