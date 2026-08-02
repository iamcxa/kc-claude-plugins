'use strict';

const { test, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync, spawnSync } = require('node:child_process');

const PLUGIN_ROOT = path.join(__dirname, '..', '..');
const GATE = path.join(PLUGIN_ROOT, 'scripts', 'diff-scoped-mapping-lint.js');
const LINTER = path.join(PLUGIN_ROOT, 'scripts', 'lint-mapping.sh');
const WORKFLOW_TEMPLATE = path.join(PLUGIN_ROOT, 'templates', 'browser-e2e.yml');
const scratchDirs = [];

afterEach(function () {
  while (scratchDirs.length > 0) {
    fs.rmSync(scratchDirs.pop(), { recursive: true, force: true });
  }
});

function git(cwd, args) {
  return execFileSync('git', args, { cwd: cwd, encoding: 'utf8' }).trim();
}

function gitRaw(cwd, args) {
  return execFileSync('git', args, { cwd: cwd, encoding: 'utf8' });
}

function write(root, relativePath, lines) {
  const target = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, lines.join('\n') + '\n', 'utf8');
}

function changedMappingRepo(newSelector) {
  newSelector = newSelector || 'button >> nth=1';
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'mapping-lint-ci-'));
  scratchDirs.push(root);
  git(root, ['init', '-q']);
  git(root, ['config', 'user.email', 'test@example.com']);
  git(root, ['config', 'user.name', 'Mapping Lint Test']);

  write(root, '.claude/e2e/mappings/a-clean.yaml', [
    'version: 2',
    'pages:',
    '  home:',
    '    elements:',
    '      title:',
    "        selector: '[data-testid=\"title\"]'",
  ]);
  write(root, '.claude/e2e/mappings/z-violating.yaml', [
    'version: 2',
    'pages:',
    '  home:',
    '    elements:',
    '      legacy:',
    "        selector: 'button:has-text(\"Legacy\")'",
  ]);
  git(root, ['add', '.claude/e2e/mappings/a-clean.yaml', '.claude/e2e/mappings/z-violating.yaml']);
  git(root, ['commit', '-qm', 'baseline']);
  const base = git(root, ['rev-parse', 'HEAD']);

  fs.appendFileSync(
    path.join(root, '.claude/e2e/mappings/a-clean.yaml'),
    '      subtitle:\n        selector: \'text=Welcome\'\n',
    'utf8'
  );
  fs.appendFileSync(
    path.join(root, '.claude/e2e/mappings/z-violating.yaml'),
    '      new_button:\n        selector: \'' + newSelector + '\'\n',
    'utf8'
  );
  git(root, ['add', '.claude/e2e/mappings/a-clean.yaml', '.claude/e2e/mappings/z-violating.yaml']);
  git(root, ['commit', '-qm', 'change mappings']);

  return { root: root, base: base, head: git(root, ['rev-parse', 'HEAD']) };
}

function renamedMappingRepo(editSelector) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'mapping-lint-rename-'));
  scratchDirs.push(root);
  git(root, ['init', '-q']);
  git(root, ['config', 'user.email', 'test@example.com']);
  git(root, ['config', 'user.name', 'Mapping Lint Test']);

  const oldPath = '.claude/e2e/mappings/old-name.yaml';
  const newPath = '.claude/e2e/mappings/new-name.yaml';
  write(root, oldPath, [
    'version: 2',
    'pages:',
    '  home:',
    '    elements:',
    '      legacy:',
    "        selector: 'button:has-text(\"Legacy\")'",
    '      target:',
    "        selector: '[data-testid=\"target\"]'",
  ]);
  git(root, ['add', oldPath]);
  git(root, ['commit', '-qm', 'baseline']);
  const base = git(root, ['rev-parse', 'HEAD']);

  git(root, ['mv', oldPath, newPath]);
  if (editSelector) {
    const target = path.join(root, newPath);
    const before = fs.readFileSync(target, 'utf8');
    fs.writeFileSync(target, before.replace('[data-testid="target"]', editSelector), 'utf8');
  }
  git(root, ['add', newPath]);
  git(root, ['commit', '-qm', editSelector ? 'rename and edit mapping' : 'rename mapping']);

  return {
    root: root,
    base: base,
    head: git(root, ['rev-parse', 'HEAD']),
    oldPath: oldPath,
    newPath: newPath,
  };
}

function singleChangedLegacyRepo() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'mapping-lint-protocol-'));
  scratchDirs.push(root);
  git(root, ['init', '-q']);
  git(root, ['config', 'user.email', 'test@example.com']);
  git(root, ['config', 'user.name', 'Mapping Lint Test']);
  const mapping = '.claude/e2e/mappings/legacy.yaml';
  write(root, mapping, [
    'version: 2',
    'pages:',
    '  home:',
    '    elements:',
    '      legacy:',
    "        selector: 'button:has-text(\"Legacy\")'",
  ]);
  git(root, ['add', mapping]);
  git(root, ['commit', '-qm', 'baseline']);
  const base = git(root, ['rev-parse', 'HEAD']);
  fs.appendFileSync(
    path.join(root, mapping),
    '      clean:\n        selector: \'text=Welcome\'\n',
    'utf8'
  );
  git(root, ['add', mapping]);
  git(root, ['commit', '-qm', 'change clean selector']);
  return { root: root, base: base, head: git(root, ['rev-parse', 'HEAD']) };
}

function fakeLinter(repo, lines) {
  const linter = path.join(repo.root, 'fake-linter.sh');
  fs.writeFileSync(linter, ['#!/usr/bin/env bash'].concat(lines, ['exit 2', '']).join('\n'), 'utf8');
  return linter;
}

function runGate(repo, linter) {
  return spawnSync('node', [
    GATE,
    '--base', repo.base,
    '--head', repo.head,
    '--linter', linter || LINTER,
  ], { cwd: repo.root, encoding: 'utf8' });
}

test('blocks when a clean changed mapping sorts before a violating changed mapping', function () {
  const repo = changedMappingRepo();
  const changed = git(repo.root, [
    'diff', '--name-only', repo.base, repo.head, '--', '.claude/e2e/mappings/*.yaml',
  ]).split('\n');
  assert.deepEqual(
    changed,
    ['.claude/e2e/mappings/a-clean.yaml', '.claude/e2e/mappings/z-violating.yaml'],
    'arrangement precondition: both files are changed and the clean file sorts first'
  );

  const result = runGate(repo);
  assert.equal(result.status, 2, String(result.stderr || result.error || ''));
});

test('annotates a violation on an added mapping line as a blocking error', function () {
  const repo = changedMappingRepo();
  const result = runGate(repo);

  assert.match(
    result.stdout,
    /::error file=\.claude\/e2e\/mappings\/z-violating\.yaml,line=8,title=Mapping selector policy \(>>nth\)::/
  );
});

test('annotates a violation on a modified mapping line as a blocking error', function () {
  const repo = changedMappingRepo();
  repo.base = repo.head;
  const mapping = path.join(repo.root, '.claude/e2e/mappings/z-violating.yaml');
  const before = fs.readFileSync(mapping, 'utf8');
  fs.writeFileSync(mapping, before.replace('button >> nth=1', 'button:has-text("New")'), 'utf8');
  git(repo.root, ['add', '.claude/e2e/mappings/z-violating.yaml']);
  git(repo.root, ['commit', '-qm', 'modify selector']);
  repo.head = git(repo.root, ['rev-parse', 'HEAD']);

  const result = runGate(repo);
  assert.match(
    result.stdout,
    /::error file=\.claude\/e2e\/mappings\/z-violating\.yaml,line=8,title=Mapping selector policy \(has-text\)::/
  );
});

test('annotates a finding on an untouched legacy line as a non-blocking warning', function () {
  const repo = changedMappingRepo('text=Welcome');
  const result = runGate(repo);

  assert.deepEqual(
    {
      status: result.status,
      warning: /::warning file=\.claude\/e2e\/mappings\/z-violating\.yaml,line=6,title=Mapping selector policy \(has-text\)::/.test(result.stdout),
    },
    { status: 0, warning: true }
  );
});

test('the CI template runs the reusable gate before browser setup', function () {
  const workflow = fs.readFileSync(WORKFLOW_TEMPLATE, 'utf8');

  assert.match(
    workflow,
    / {2}mapping-lint:\n {4}name: Mapping Selector Lint\n[\s\S]*?fetch-depth: 0[\s\S]*?node kc-claude-plugins\/e2e-pipeline\/scripts\/diff-scoped-mapping-lint\.js[\s\S]*?--base "\$\{\{ github\.event\.pull_request\.base\.sha \|\| github\.event\.before \}\}"[\s\S]*?--head "\$\{\{ github\.sha \}\}"[\s\S]*? {2}auth-setup:\n {4}name: Auth Setup\n {4}needs: \[mapping-lint\]/
  );
});

test('a pure R100 rename keeps untouched legacy debt non-blocking', function () {
  const repo = renamedMappingRepo();
  const nameStatus = gitRaw(repo.root, ['diff', '--name-status', '-z', '-M', repo.base, repo.head]);
  assert.equal(
    nameStatus,
    'R100\0' + repo.oldPath + '\0' + repo.newPath + '\0',
    'arrangement precondition: Git recognizes a pure rename and reports both paths'
  );

  const result = runGate(repo);
  assert.deepEqual(
    {
      status: result.status,
      warning: result.stdout.includes('::warning file=' + repo.newPath + ',line=6,title=Mapping selector policy (has-text)::'),
      error: result.stdout.includes('::error file=' + repo.newPath + ',line=6,title=Mapping selector policy (has-text)::'),
    },
    { status: 0, warning: true, error: false }
  );
});

test('a rename plus selector edit warns on untouched debt and blocks the edited line', function () {
  const repo = renamedMappingRepo('button >> nth=1');
  const nameStatus = gitRaw(repo.root, ['diff', '--name-status', '-z', '-M', repo.base, repo.head]);
  assert.match(
    nameStatus,
    /^R\d+\0\.claude\/e2e\/mappings\/old-name\.yaml\0\.claude\/e2e\/mappings\/new-name\.yaml\0$/,
    'arrangement precondition: Git recognizes the edited file as a rename'
  );

  const result = runGate(repo);
  assert.deepEqual(
    {
      status: result.status,
      legacyWarning: result.stdout.includes('::warning file=' + repo.newPath + ',line=6,title=Mapping selector policy (has-text)::'),
      legacyError: result.stdout.includes('::error file=' + repo.newPath + ',line=6,title=Mapping selector policy (has-text)::'),
      editedError: result.stdout.includes('::error file=' + repo.newPath + ',line=8,title=Mapping selector policy (>>nth)::'),
    },
    { status: 2, legacyWarning: true, legacyError: false, editedError: true }
  );
});

test('rc=2 with empty stderr is an infrastructure failure', function () {
  const repo = singleChangedLegacyRepo();
  const result = runGate(repo, fakeLinter(repo, []));
  assert.deepEqual(
    { status: result.status, diagnostic: /invalid lint-mapping protocol/.test(result.stderr) },
    { status: 1, diagnostic: true }
  );
});

test('rc=2 with malformed stderr is an infrastructure failure', function () {
  const repo = singleChangedLegacyRepo();
  const result = runGate(repo, fakeLinter(repo, [
    "printf '%s\\n' 'not the lint-mapping protocol' >&2",
  ]));
  assert.deepEqual(
    { status: result.status, diagnostic: /invalid lint-mapping protocol/.test(result.stderr) },
    { status: 1, diagnostic: true }
  );
});

test('rc=2 with a mismatched FAIL count is an infrastructure failure', function () {
  const repo = singleChangedLegacyRepo();
  const result = runGate(repo, fakeLinter(repo, [
    "printf '%s:6: has-text: selector: button:has-text(Legacy)\\n' \"$1\" >&2",
    "printf 'lint-mapping: %s — FAIL (2 banned token(s) found)\\n' \"$1\" >&2",
  ]));
  assert.deepEqual(
    { status: result.status, diagnostic: /invalid lint-mapping protocol/.test(result.stderr) },
    { status: 1, diagnostic: true }
  );
});

test('rc=2 with a mismatched mapping identity is an infrastructure failure', function () {
  const repo = singleChangedLegacyRepo();
  const result = runGate(repo, fakeLinter(repo, [
    "printf '%s:6: has-text: selector: button:has-text(Legacy)\\n' \"$1\" >&2",
    "printf '%s\\n' 'lint-mapping: .claude/e2e/mappings/other.yaml — FAIL (1 banned token(s) found)' >&2",
  ]));
  assert.deepEqual(
    { status: result.status, diagnostic: /invalid lint-mapping protocol/.test(result.stderr) },
    { status: 1, diagnostic: true }
  );
});
