#!/usr/bin/env node
'use strict';

const { spawnSync } = require('node:child_process');

function parseArgs(argv) {
  const options = {};
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i];
    const value = argv[i + 1];
    if (!key || !key.startsWith('--') || value === undefined) {
      throw new Error('Usage: diff-scoped-mapping-lint.js --base <sha> --head <sha> --linter <path>');
    }
    options[key.slice(2)] = value;
  }
  for (const required of ['base', 'head', 'linter']) {
    if (!options[required]) {
      throw new Error('Missing required option --' + required);
    }
  }
  return options;
}

function run(command, args, cwd) {
  return spawnSync(command, args, { cwd: cwd, encoding: 'utf8' });
}

function changedLines(base, head, mapping, cwd) {
  const diff = run('git', [
    'diff', '--unified=0', '--no-color', base, head, '--', mapping,
  ], cwd);
  if (diff.status !== 0) {
    throw new Error(diff.stderr || 'git diff failed for ' + mapping);
  }

  const lines = new Set();
  for (const line of diff.stdout.split('\n')) {
    const hunk = /^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@/.exec(line);
    if (!hunk) continue;
    const start = Number(hunk[1]);
    const count = hunk[2] === undefined ? 1 : Number(hunk[2]);
    for (let offset = 0; offset < count; offset += 1) lines.add(start + offset);
  }
  return lines;
}

function parseFindings(stderr) {
  const findings = [];
  for (const line of String(stderr || '').split('\n')) {
    const finding = /^(.*):(\d+): ([^:]+): (.*)$/.exec(line);
    if (!finding) continue;
    findings.push({
      file: finding[1],
      line: Number(finding[2]),
      classId: finding[3],
      source: finding[4],
    });
  }
  return findings;
}

function escapeCommandValue(value) {
  return String(value)
    .replaceAll('%', '%25')
    .replaceAll('\r', '%0D')
    .replaceAll('\n', '%0A')
    .replaceAll(':', '%3A')
    .replaceAll(',', '%2C');
}

function escapeCommandMessage(value) {
  return String(value)
    .replaceAll('%', '%25')
    .replaceAll('\r', '%0D')
    .replaceAll('\n', '%0A');
}

function annotation(level, finding) {
  return '::' + level +
    ' file=' + escapeCommandValue(finding.file) +
    ',line=' + finding.line +
    ',title=' + escapeCommandValue('Mapping selector policy (' + finding.classId + ')') +
    '::' + escapeCommandMessage(finding.source) + '\n';
}

function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    process.stderr.write(error.message + '\n');
    return 1;
  }

  const diff = run('git', [
    'diff', '--name-only', '-z', '--diff-filter=ACMR', options.base, options.head,
    '--', '.claude/e2e/mappings/*.yaml',
  ], process.cwd());
  if (diff.status !== 0) {
    process.stderr.write(diff.stderr || 'git diff failed\n');
    return 1;
  }

  const mappings = diff.stdout.split('\0').filter(Boolean);
  let violations = false;
  for (const mapping of mappings) {
    const lint = run('bash', [options.linter, mapping], process.cwd());
    process.stdout.write(lint.stdout || '');
    if (lint.status === 2) {
      let touched;
      try {
        touched = changedLines(options.base, options.head, mapping, process.cwd());
      } catch (error) {
        process.stderr.write(error.message + '\n');
        return 1;
      }
      for (const finding of parseFindings(lint.stderr)) {
        if (touched.has(finding.line)) {
          process.stdout.write(annotation('error', finding));
          violations = true;
        } else {
          process.stdout.write(annotation('warning', finding));
        }
      }
      continue;
    }
    if (lint.status !== 0) {
      process.stderr.write(lint.stderr || 'mapping linter failed for ' + mapping + '\n');
      return 1;
    }
  }

  return violations ? 2 : 0;
}

process.exitCode = main();
