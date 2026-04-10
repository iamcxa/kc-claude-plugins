#!/usr/bin/env node
// MCP Firewall Nudge - PreToolUse hook
// Nudges main agent to dispatch the `mcp-summarizer` subagent when calling
// read-type MCP tools whose responses tend to bloat context (Linear, Sentry,
// Notion, Supabase, Figma, Slack, Langfuse, episodic-memory).
//
// Design:
//   - Matcher (in hooks.json) pre-filters on namespace prefix — fast path
//   - This script filters further: only read-ops (list/search/get/...) nudge
//   - Per-namespace, per-session dedup: first call of each MCP family nudges,
//     subsequent calls in the same family are silent until a new session
//   - Subagent self-immunity: if no statusline metrics file exists, we are
//     running inside a subagent (including mcp-summarizer itself) → silent
//     exit, otherwise mcp-summarizer would nudge itself on every call
//
// Output contract: stdout JSON with optional `additionalContext` field.
// Empty JSON `{}` = no nudge. Never blocks (no `deny`).
//
// Failure mode: on any error, exit silently with empty JSON — never block
// tool execution because of a nudge hook.

const fs = require('fs');
const os = require('os');
const path = require('path');

const READ_VERBS = new Set([
  'list', 'search', 'get', 'find', 'read', 'fetch', 'query', 'extract',
]);

// Namespaces mirrored from mcp-summarizer agent's `tools:` declaration.
// Keep in sync: kc-hyperfocus/agents/mcp-summarizer.md line 28.
const NAMESPACE_LABELS = {
  'mcp__claude_ai_Linear__': 'linear',
  'mcp__plugin_linear_linear__': 'linear',
  'mcp__claude_ai_Sentry__': 'sentry',
  'mcp__plugin_sentry_sentry__': 'sentry',
  'mcp__claude_ai_Notion__': 'notion',
  'mcp__claude_ai_Supabase__': 'supabase',
  'mcp__plugin_episodic-memory_episodic-memory__': 'episodic-memory',
  'mcp__claude_ai_Figma__': 'figma',
  'mcp__claude_ai_Slack__': 'slack',
  'mcp__langfuse-docs__': 'langfuse',
};

function silent() {
  process.stdout.write('{}');
  process.exit(0);
}

function parseToolName(toolName) {
  // Example: "mcp__claude_ai_Linear__list_issues"
  //   → namespace = "mcp__claude_ai_Linear__"
  //   → action    = "list_issues"
  //   → verb      = "list"
  for (const prefix of Object.keys(NAMESPACE_LABELS)) {
    if (toolName.startsWith(prefix)) {
      const action = toolName.slice(prefix.length);
      const verb = action.split('_')[0];
      return { namespace: prefix, label: NAMESPACE_LABELS[prefix], action, verb };
    }
  }
  return null;
}

function buildNudge(parsed) {
  const { label, action } = parsed;
  return [
    `⚡ MCP Firewall Nudge: about to call \`${parsed.namespace}${action}\` (${label}).`,
    '',
    'For responses likely > 50 lines, dispatch `mcp-summarizer` so the raw',
    'payload stays out of main context:',
    '',
    '```',
    'Agent(subagent_type="mcp-summarizer",',
    `      prompt="<describe the ${label} query, include scope limits>")`,
    '```',
    '',
    'Proceed directly for small / one-shot queries (single ID lookup, status check).',
    `This message fires once per MCP family per session (current: ${label}).`,
  ].join('\n');
}

let input = '';
const stdinTimeout = setTimeout(() => silent(), 3000);
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => (input += chunk));
process.stdin.on('end', () => {
  clearTimeout(stdinTimeout);
  try {
    const data = JSON.parse(input || '{}');
    const sessionId = data.session_id;
    const toolName = data.tool_name || '';

    if (!sessionId || !toolName) silent();

    // Subagent self-immunity: statusline only writes metrics in the MAIN
    // agent context. Subagents (including mcp-summarizer) have no metrics
    // file → skip to avoid nudging subagents about using themselves.
    const metricsPath = path.join(os.tmpdir(), `claude-ctx-${sessionId}.json`);
    if (!fs.existsSync(metricsPath)) silent();

    const parsed = parseToolName(toolName);
    if (!parsed) silent();

    // Only nudge on read-like operations. Writes are small and need domain
    // expertise, not summarization.
    if (!READ_VERBS.has(parsed.verb)) silent();

    // Per-namespace, per-session dedup.
    const dedupPath = path.join(os.tmpdir(), `claude-mcp-firewall-${sessionId}.json`);
    let seen = {};
    if (fs.existsSync(dedupPath)) {
      try {
        seen = JSON.parse(fs.readFileSync(dedupPath, 'utf8')) || {};
      } catch {
        seen = {};
      }
    }
    if (seen[parsed.label]) silent();

    seen[parsed.label] = Math.floor(Date.now() / 1000);
    try {
      fs.writeFileSync(dedupPath, JSON.stringify(seen));
    } catch {
      // Non-fatal: nudge will fire again if we can't persist dedup state.
    }

    const response = {
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        additionalContext: buildNudge(parsed),
      },
    };
    process.stdout.write(JSON.stringify(response));
    process.exit(0);
  } catch {
    silent();
  }
});
