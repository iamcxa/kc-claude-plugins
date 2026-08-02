#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const {
  buildProbeExpression,
  classifyVisibility,
  judgeVisibility,
  unwrapEvalEnvelope,
} = require('../compiler/lib/visibility-probe');

function usage(message) {
  if (message) process.stderr.write('e2e-visibility-probe: ' + message + '\n');
  process.stderr.write(
    'usage: e2e-visibility-probe expression --selector <css>\n' +
    '       e2e-visibility-probe judge --policy <policy> --assert <visible|not-visible|enabled|disabled> ' +
    '--transport-exit <n>\n'
  );
  return 64;
}

function parseFlags(argv) {
  const flags = Object.create(null);
  for (let index = 0; index < argv.length; index += 2) {
    const name = argv[index];
    const value = argv[index + 1];
    if (!name || !name.startsWith('--') || value === undefined || flags[name] !== undefined) {
      return null;
    }
    flags[name] = value;
  }
  return flags;
}

function sameKeys(flags, expected) {
  return Object.keys(flags).sort().join('\n') === expected.slice().sort().join('\n');
}

function main(argv) {
  const command = argv[0];
  const flags = parseFlags(argv.slice(1));
  if (!flags) return usage('invalid arguments');

  if (command === 'expression') {
    if (!sameKeys(flags, ['--selector'])) return usage('expression requires --selector');
    process.stdout.write(buildProbeExpression(flags['--selector']) + '\n');
    return 0;
  }

  if (command === 'judge') {
    if (!sameKeys(flags, ['--policy', '--assert', '--transport-exit'])) {
      return usage('judge requires --policy, --assert, and --transport-exit');
    }
    if (!/^(?:0|[1-9][0-9]*)$/.test(flags['--transport-exit'])) {
      return usage('--transport-exit must be a non-negative integer');
    }
    const raw = fs.readFileSync(0, 'utf8');
    const evidence = unwrapEvalEnvelope(raw, Number(flags['--transport-exit']));
    const classified = classifyVisibility(evidence, flags['--policy']);
    const judged = judgeVisibility(classified, flags['--assert']);
    process.stdout.write(JSON.stringify(judged) + '\n');
    return judged.exit_code;
  }

  return usage('unknown command: ' + String(command || ''));
}

try {
  process.exitCode = main(process.argv.slice(2));
} catch (error) {
  process.stderr.write('e2e-visibility-probe: ' + String(error?.message || error) + '\n');
  process.exitCode = 64;
}
