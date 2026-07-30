#!/usr/bin/env node
'use strict';

const { spawnSync } = require('node:child_process');

const args = process.argv.slice(2);
if (args[0] === 'new-run-id') {
  process.stdout.write('test-browser-run\n');
  process.exit(0);
}

let index = 0;
while (index < args.length) {
  if (
    args[index] === '--run-id' ||
    args[index] === '--app' ||
    args[index] === '--receipt'
  ) {
    index += 2;
    continue;
  }
  break;
}

const browserArgs = args.slice(index);
if (process.env.E2E_COMPILED_BROWSER_ALIAS) {
  browserArgs.unshift('--session', process.env.E2E_COMPILED_BROWSER_ALIAS);
}
const result = spawnSync('agent-browser', browserArgs, {
  env: process.env,
  stdio: 'inherit',
});
if (result.error) {
  process.stderr.write(result.error.message + '\n');
  process.exit(127);
}
process.exit(result.status === null ? 1 : result.status);
