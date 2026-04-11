import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { JournalSearchService } from "./journal-search.ts";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

describe("JournalSearchService.readEntry", () => {
  const TEST_DIR_NAME = `.private-journal-test-${process.pid}`;
  const TEST_DIR_ABS = join(homedir(), TEST_DIR_NAME);
  const TEST_FILE_NAME = "readentry-test.md";
  const TEST_FILE_ABS = join(TEST_DIR_ABS, TEST_FILE_NAME);
  const TEST_CONTENT = "# Test Entry\n\nContent here.";

  beforeEach(() => {
    rmSync(TEST_DIR_ABS, { recursive: true, force: true });
    mkdirSync(TEST_DIR_ABS, { recursive: true });
    writeFileSync(TEST_FILE_ABS, TEST_CONTENT, "utf8");
  });

  afterEach(() => {
    rmSync(TEST_DIR_ABS, { recursive: true, force: true });
  });

  it("reads entry when given an absolute path", () => {
    const service = new JournalSearchService();
    const content = service.readEntry(TEST_FILE_ABS);
    expect(content).toBe(TEST_CONTENT);
  });

  it("expands tilde prefix to the user's home directory", () => {
    const service = new JournalSearchService();
    const tildePath = `~/${TEST_DIR_NAME}/${TEST_FILE_NAME}`;
    const content = service.readEntry(tildePath);
    expect(content).toBe(TEST_CONTENT);
  });

  it("returns null for nonexistent tilde path without throwing", () => {
    const service = new JournalSearchService();
    const content = service.readEntry(
      `~/${TEST_DIR_NAME}/nonexistent.md`
    );
    expect(content).toBeNull();
  });

  it("returns null for nonexistent absolute path", () => {
    const service = new JournalSearchService();
    const content = service.readEntry(
      "/tmp/absolutely-nonexistent-journal-file.md"
    );
    expect(content).toBeNull();
  });

  it("does not mangle paths that start with a single ~ but no slash", () => {
    // Edge: a path like "~foo" means "user foo's home" in shell, but we
    // only treat "~/" as tilde expansion. A bare "~foo.md" should pass
    // through unchanged (and fail as nonexistent).
    const service = new JournalSearchService();
    const content = service.readEntry("~not-a-real-user-file.md");
    expect(content).toBeNull();
  });
});
