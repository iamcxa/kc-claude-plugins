#!/usr/bin/env node
// Hyperfocus Statusline — model │ dir branch ██░░ used% │ 5h:N% 7d:N%
// Standalone statusline with Anthropic usage quota display.
// Does NOT depend on GSD or any other plugin.

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

// ---------------------------------------------------------------------------
// Git branch (fast, no optional locks)
// ---------------------------------------------------------------------------
function getGitBranch(dir) {
  try {
    const result = spawnSync('git', ['-C', dir, '--no-optional-locks', 'rev-parse', '--abbrev-ref', 'HEAD'], {
      encoding: 'utf8',
      timeout: 2000
    });
    if (result.status === 0) return result.stdout.trim();
  } catch (e) {}
  return null;
}

// ---------------------------------------------------------------------------
// Anthropic usage quota (5h / 7d) — 5-minute cache in /tmp
// ---------------------------------------------------------------------------
function getAnthropicUsage() {
  const cacheFile = path.join(os.tmpdir(), 'claude-usage-cache.json');
  const CACHE_TTL = 5 * 60 * 1000;

  try {
    const cache = JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
    if (Date.now() - cache.ts < CACHE_TTL) return cache.data;
  } catch (e) {}

  // Read OAuth token from macOS Keychain
  let token = null;
  try {
    const keychainResult = spawnSync(
      'security',
      ['find-generic-password', '-s', 'Claude Code-credentials', '-a', os.userInfo().username, '-w'],
      { encoding: 'utf8', timeout: 3000 }
    );
    if (keychainResult.status === 0 && keychainResult.stdout) {
      const creds = JSON.parse(keychainResult.stdout.trim());
      token = creds?.claudeAiOauth?.accessToken || null;
    }
  } catch (e) {}

  if (!token) return null;

  const fetchScript = `
const https = require('https');
const token = process.env._ANTHROPIC_TOKEN;
const options = {
  hostname: 'api.anthropic.com',
  path: '/api/oauth/usage',
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token,
    'anthropic-beta': 'oauth-2025-04-20'
  }
};
let body = '';
const req = https.request(options, res => {
  res.on('data', d => body += d);
  res.on('end', () => process.stdout.write(body));
});
req.on('error', () => process.exit(1));
req.setTimeout(4000, () => { req.destroy(); process.exit(1); });
req.end();
`;

  try {
    const result = spawnSync('node', ['-e', fetchScript], {
      encoding: 'utf8',
      timeout: 6000,
      env: { ...process.env, _ANTHROPIC_TOKEN: token }
    });
    if (result.status !== 0 || !result.stdout) return null;

    const json = JSON.parse(result.stdout);
    const h5 = json.five_hour?.utilization ?? null;
    const d7 = json.seven_day?.utilization ?? null;
    const data = { h5, d7 };

    fs.writeFileSync(cacheFile, JSON.stringify({ ts: Date.now(), data }));
    return data;
  } catch (e) {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
let input = '';
const stdinTimeout = setTimeout(() => process.exit(0), 3000);
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  clearTimeout(stdinTimeout);
  try {
    const data = JSON.parse(input);
    const model = data.model?.display_name || 'Claude';
    const dir = data.workspace?.current_dir || process.cwd();
    const session = data.session_id || '';
    const remaining = data.context_window?.remaining_percentage;

    // Context window — normalize to usable range (exclude autocompact buffer)
    const AUTO_COMPACT_BUFFER_PCT = 16.5;
    let ctx = '';
    if (remaining != null) {
      const usableRemaining = Math.max(0, ((remaining - AUTO_COMPACT_BUFFER_PCT) / (100 - AUTO_COMPACT_BUFFER_PCT)) * 100);
      const used = Math.max(0, Math.min(100, Math.round(100 - usableRemaining)));

      // Write bridge file for context-pressure-monitor hook
      if (session) {
        try {
          const bridgePath = path.join(os.tmpdir(), `claude-ctx-${session}.json`);
          fs.writeFileSync(bridgePath, JSON.stringify({
            session_id: session,
            remaining_percentage: remaining,
            used_pct: used,
            timestamp: Math.floor(Date.now() / 1000)
          }));
        } catch (e) {}
      }

      // Progress bar (10 segments)
      const filled = Math.floor(used / 10);
      const bar = '\u2588'.repeat(filled) + '\u2591'.repeat(10 - filled);

      if (used < 50) {
        ctx = ` \x1b[32m${bar} ${used}%\x1b[0m`;
      } else if (used < 65) {
        ctx = ` \x1b[33m${bar} ${used}%\x1b[0m`;
      } else if (used < 80) {
        ctx = ` \x1b[38;5;208m${bar} ${used}%\x1b[0m`;
      } else {
        ctx = ` \x1b[5;31m\uD83D\uDC80 ${bar} ${used}%\x1b[0m`;
      }
    }

    // Git branch (truncate long names)
    const branch = getGitBranch(dir);
    let branchDisplay = branch;
    if (branch && branch.length > 30) {
      branchDisplay = `${branch.slice(0, 20)}\u2026${branch.slice(-8)}`;
    }
    const branchStr = branchDisplay ? ` \x1b[35m${branchDisplay}\x1b[0m` : '';

    // Anthropic usage quota
    let usageStr = '';
    const usage = getAnthropicUsage();
    if (usage) {
      const parts = [];
      if (usage.h5 != null) parts.push(`\x1b[2m5h:\x1b[22;32m${Math.round(usage.h5)}%\x1b[0m`);
      if (usage.d7 != null) parts.push(`\x1b[2m7d:\x1b[22;32m${Math.round(usage.d7)}%\x1b[0m`);
      if (parts.length > 0) usageStr = ` \u2502 ${parts.join(' ')}`;
    }

    // Output
    const dirname = path.basename(dir);
    process.stdout.write(`\x1b[2m${model}\x1b[0m \u2502 \x1b[2m${dirname}\x1b[0m${branchStr}${ctx}${usageStr}`);
  } catch (e) {}
});
