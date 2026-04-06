// post-explore-nudge.js — PostToolUse:Agent
// After an Explore agent completes, nudge Claude to cache insights via store_insight.
// Also records the Explore completion to a temp file for handoff safety net.

import { readFileSync, writeFileSync, existsSync } from "fs";

async function main() {
  const input = JSON.parse(await Bun.stdin.text());

  // Only handle completed Agent tool calls
  if (input.tool_name !== "Agent") process.exit(0);

  // Check if this was an Explore agent by looking at tool_input
  const subagentType = input.tool_input?.subagent_type;
  if (subagentType !== "Explore") process.exit(0);

  const sessionId = input.session_id;
  const prompt = input.tool_input?.prompt ?? "";
  const promptSnippet = prompt.slice(0, 200);

  // 1. Record Explore completion for handoff safety net
  if (sessionId) {
    const trackFile = `/tmp/claude-lake-explores-${sessionId}.json`;
    let explores = { completed: [] };
    if (existsSync(trackFile)) {
      try {
        explores = JSON.parse(readFileSync(trackFile, "utf-8"));
      } catch { /* corrupt file, reset */ }
    }
    explores.completed.push({
      prompt: promptSnippet,
      timestamp: new Date().toISOString(),
    });
    writeFileSync(trackFile, JSON.stringify(explores));
  }

  // 2. Nudge Claude to cache insights
  const output = {
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: [
        "[context-lake] 📝 Explore agent just completed.",
        "If you gained deep understanding of specific files during this exploration,",
        "call `store_insight` (via context-lake MCP) for each key file to cache your insights for future sessions.",
        "Write all insights in English for consistency.",
        "Focus on files where you now understand: purpose, key functions, dependencies, and gotchas.",
        "Skip files you only glanced at.",
      ].join(" "),
    },
  };
  process.stdout.write(JSON.stringify(output));
}

main().catch(() => process.exit(0));
