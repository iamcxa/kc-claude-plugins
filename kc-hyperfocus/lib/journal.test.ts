import { describe, it, expect } from "bun:test";
import { detectFieldCorruption } from "./journal.ts";

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
