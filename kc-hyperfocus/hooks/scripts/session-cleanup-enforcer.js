#!/usr/bin/env node
// Session Cleanup Enforcer - Stop hook
// When Claude tries to stop, checks if mandatory cleanup was performed
// during a CRITICAL context session. If not, outputs instructions to
// stdout which forces Claude to continue.
//
// Safety: Max 2 enforcement attempts to prevent infinite loops.
// Staleness: Auto-resets if state is older than 5 minutes.
//
// Mandatory: journal with feelings + project_notes (~500 tokens)
// Optional:  GSD todo (tracked but not enforced — too expensive under context pressure)
//
// Flow:
//   1. Read cleanup state from /tmp/claude-cleanup-{session_id}.json
//   2. If no CRITICAL was triggered → exit 0 (Claude stops normally)
//   3. If CRITICAL + journal incomplete → output enforcement → Claude continues
//   4. If enforcement_count >= 2 → exit 0 (safety valve)

const fs = require('fs');
const os = require('os');
const path = require('path');

const MAX_ENFORCEMENT = 2;
const STALE_SECONDS = 300; // 5 minutes

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

    if (!sessionId) {
      process.exit(0);
    }

    const tmpDir = os.tmpdir();
    const statePath = path.join(tmpDir, `claude-cleanup-${sessionId}.json`);

    // No state file → no CRITICAL was ever triggered → let Claude stop
    if (!fs.existsSync(statePath)) {
      process.exit(0);
    }

    let state;
    try {
      state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
    } catch (e) {
      process.exit(0);
    }

    // Stale state → auto-reset, let Claude stop
    const now = Math.floor(Date.now() / 1000);
    if (state.last_updated && (now - state.last_updated) > STALE_SECONDS) {
      process.exit(0);
    }

    // No CRITICAL triggered → let Claude stop
    if (!state.critical_triggered) {
      process.exit(0);
    }

    // Check what's missing (only journal is mandatory under context pressure)
    const missing = [];
    if (!state.journal_done) {
      missing.push('journal (with feelings + project_notes)');
    } else if (!state.journal_has_feelings) {
      missing.push('journal feelings (journal was written but missing feelings field)');
    } else if (!state.journal_has_project_notes) {
      missing.push('journal project_notes (journal was written but missing project_notes for session handoff)');
    }
    // GSD todo is optional under context pressure — not enforced here

    // All mandatory cleanup done → let Claude stop
    if (missing.length === 0) {
      process.exit(0);
    }

    // Safety valve: max enforcement attempts reached → force stop
    if ((state.enforcement_count || 0) >= MAX_ENFORCEMENT) {
      process.exit(0);
    }

    // Increment enforcement count and save
    state.enforcement_count = (state.enforcement_count || 0) + 1;
    state.last_updated = now;
    fs.writeFileSync(statePath, JSON.stringify(state, null, 2));

    const attempt = state.enforcement_count;
    const missingStr = missing.join(' + ');

    // Build targeted instruction
    const instructions = [];
    instructions.push(
      `MANDATORY CLEANUP BEFORE STOPPING (attempt ${attempt}/${MAX_ENFORCEMENT}):`,
      `You triggered CRITICAL context pressure but have NOT completed: ${missingStr}.`
    );

    if (!state.journal_done) {
      instructions.push(
        'Invoke /kc-session-handoff skill — it handles journal writing + resume ID generation. Do NOT call process_thoughts directly (bypasses resume ID → next session must manually search). The skill will write feelings + project_notes internally.'
      );
    } else if (!state.journal_has_feelings) {
      instructions.push(
        'Journal feelings missing: Call mcp__private-journal__process_thoughts again with the feelings field (1-2 sentences about your current state).'
      );
    } else if (!state.journal_has_project_notes) {
      instructions.push(
        'Journal project_notes missing: Call mcp__private-journal__process_thoughts again with project_notes field (what was done, remaining work, key decisions — this is your session handoff).'
      );
    }

    instructions.push(
      'Complete these items, then you may stop.'
    );

    process.stdout.write(instructions.join(' '));
  } catch (e) {
    // Silent fail — let Claude stop if something goes wrong
    process.exit(0);
  }
});
