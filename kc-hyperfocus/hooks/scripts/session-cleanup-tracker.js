#!/usr/bin/env node
// Session Cleanup Tracker - PostToolUse hook
// Passively tracks whether cleanup tools were called during a session
// where CRITICAL context pressure was triggered.
//
// Reads the statusline bridge file to detect CRITICAL state,
// then tracks journal and GSD tool invocations. Writes state to
// /tmp/claude-cleanup-{session_id}.json for the Stop hook enforcer.
//
// Performance: ~5ms per invocation (1 JSON read, 1 JSON write)
// Never outputs anything — purely passive tracking.

const fs = require('fs');
const os = require('os');
const path = require('path');

const CRITICAL_THRESHOLD = 17; // remaining_percentage <= 17%
const STALE_SECONDS = 300;     // 5 minutes — auto-reset for cross-session protection

let input = '';
// Timeout guard: exit silently if stdin doesn't close within 3s
const stdinTimeout = setTimeout(() => process.exit(0), 3000);
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  clearTimeout(stdinTimeout);
  try {
    const data = JSON.parse(input);
    const sessionId = data.session_id;
    const toolName = data.tool_name;
    const toolInput = data.tool_input || {};

    if (!sessionId) {
      process.exit(0);
    }

    const tmpDir = os.tmpdir();
    const statePath = path.join(tmpDir, `claude-cleanup-${sessionId}.json`);

    // Read or initialize state
    let state = {
      session_id: sessionId,
      critical_triggered: false,
      journal_done: false,
      journal_has_feelings: false,
      journal_has_project_notes: false,
      gsd_done: false,
      enforcement_count: 0,
      last_updated: Math.floor(Date.now() / 1000),
    };

    if (fs.existsSync(statePath)) {
      try {
        const existing = JSON.parse(fs.readFileSync(statePath, 'utf8'));
        // Auto-reset stale state (cross-session protection)
        const now = Math.floor(Date.now() / 1000);
        if (existing.last_updated && (now - existing.last_updated) > STALE_SECONDS) {
          // Stale — use fresh state
        } else {
          state = { ...state, ...existing };
        }
      } catch (e) {
        // Corrupted file — use fresh state
      }
    }

    // Track journal tool calls (feelings + project_notes fields)
    if (toolName === 'mcp__private-journal__process_thoughts') {
      state.journal_done = true;
      const feelings = typeof toolInput === 'object' ? (toolInput.feelings || '') : '';
      if (feelings.trim().length > 0) {
        state.journal_has_feelings = true;
      }
      const projectNotes = typeof toolInput === 'object' ? (toolInput.project_notes || '') : '';
      if (projectNotes.trim().length > 0) {
        state.journal_has_project_notes = true;
      }
    }

    // Track GSD skill invocations
    if (toolName === 'Skill') {
      const skillName = typeof toolInput === 'object'
        ? (toolInput.skill || '')
        : String(toolInput);
      if (skillName.startsWith('gsd:')) {
        state.gsd_done = true;
      }
    }

    // Check statusline bridge file for CRITICAL threshold
    const bridgePath = path.join(tmpDir, `claude-ctx-${sessionId}.json`);
    if (fs.existsSync(bridgePath)) {
      try {
        const bridge = JSON.parse(fs.readFileSync(bridgePath, 'utf8'));
        if (bridge.remaining_percentage != null && bridge.remaining_percentage <= CRITICAL_THRESHOLD) {
          state.critical_triggered = true;
        }
      } catch (e) {
        // Ignore bridge read errors
      }
    }

    // Update timestamp and write state
    state.last_updated = Math.floor(Date.now() / 1000);
    fs.writeFileSync(statePath, JSON.stringify(state, null, 2));

    // Never output anything — purely passive tracking
    process.exit(0);
  } catch (e) {
    // Silent fail — never block tool execution
    process.exit(0);
  }
});
