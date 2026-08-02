#!/usr/bin/env node
'use strict';

const { spawnSync } = require('node:child_process');
const fs = require('node:fs');

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

function changedLines(base, head, oldPath, newPath, cwd) {
  const paths = oldPath === newPath ? [newPath] : [oldPath, newPath];
  const diff = run('git', [
    'diff', '--unified=0', '--no-color', '-M', base, head, '--', ...paths,
  ], cwd);
  if (diff.status !== 0) {
    throw new Error(diff.stderr || 'git diff failed for ' + newPath);
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

function changedMappings(base, head, cwd) {
  const diff = run('git', [
    'diff', '--name-status', '-z', '-M', '--diff-filter=ACMR', base, head,
    '--', '.claude/e2e/mappings/*.yaml',
  ], cwd);
  if (diff.status !== 0) {
    throw new Error(diff.stderr || 'git diff failed\n');
  }

  const fields = diff.stdout.split('\0');
  if (fields[fields.length - 1] === '') fields.pop();
  const mappings = [];
  for (let i = 0; i < fields.length;) {
    const status = fields[i++];
    if (/^[RC]\d+$/.test(status)) {
      const oldPath = fields[i++];
      const newPath = fields[i++];
      mappings.push({ oldPath: oldPath, newPath: newPath });
    } else {
      const mapping = fields[i++];
      mappings.push({ oldPath: mapping, newPath: mapping });
    }
  }
  return mappings;
}

function parseLintFailure(stderr, mapping) {
  const findings = [];
  let summary = null;
  for (const line of String(stderr || '').split('\n').filter(Boolean)) {
    const finding = /^(.*):(\d+): ([^:]+): (.*)$/.exec(line);
    if (finding) {
      if (finding[1] !== mapping) {
        throw new Error('finding names ' + finding[1] + ' instead of ' + mapping);
      }
      findings.push({
        file: finding[1],
        line: Number(finding[2]),
        classId: finding[3],
        source: finding[4],
      });
      continue;
    }

    const parsedSummary = /^lint-mapping: (.*) — FAIL \((\d+) banned token\(s\) found\)$/.exec(line);
    if (!parsedSummary || summary) {
      throw new Error('unrecognized or duplicate stderr line: ' + line);
    }
    summary = { mapping: parsedSummary[1], count: Number(parsedSummary[2]) };
  }

  if (!summary) throw new Error('missing FAIL summary');
  if (summary.mapping !== mapping) {
    throw new Error('FAIL summary names ' + summary.mapping + ' instead of ' + mapping);
  }
  if (summary.count !== findings.length || summary.count === 0) {
    throw new Error(
      'FAIL summary count ' + summary.count + ' does not match ' + findings.length + ' finding(s)'
    );
  }
  return findings;
}

function validateFindingIdentity(findings, mapping) {
  const lines = fs.readFileSync(mapping, 'utf8').split('\n');
  if (lines[lines.length - 1] === '') lines.pop();
  for (const finding of findings) {
    if (!Number.isSafeInteger(finding.line) || finding.line <= 0 || finding.line > lines.length) {
      throw new Error('finding line ' + finding.line + ' is outside ' + mapping);
    }
    if (finding.source !== lines[finding.line - 1]) {
      throw new Error('finding source does not match ' + mapping + ':' + finding.line);
    }
  }
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

  let mappings;
  try {
    mappings = changedMappings(options.base, options.head, process.cwd());
  } catch (error) {
    process.stderr.write(error.message + '\n');
    return 1;
  }

  let violations = false;
  for (const changed of mappings) {
    const mapping = changed.newPath;
    const lint = run('bash', [options.linter, mapping], process.cwd());
    process.stdout.write(lint.stdout || '');
    if (lint.status === 2) {
      let findings;
      try {
        findings = parseLintFailure(lint.stderr, mapping);
        validateFindingIdentity(findings, mapping);
      } catch (error) {
        process.stderr.write('invalid lint-mapping protocol for ' + mapping + ': ' + error.message + '\n');
        return 1;
      }
      let touched;
      try {
        touched = changedLines(
          options.base,
          options.head,
          changed.oldPath,
          changed.newPath,
          process.cwd()
        );
      } catch (error) {
        process.stderr.write(error.message + '\n');
        return 1;
      }
      for (const finding of findings) {
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
