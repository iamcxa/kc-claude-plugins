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

function runGate(repo) {
  return spawnSync('node', [
    GATE,
    '--base', repo.base,
    '--head', repo.head,
    '--linter', LINTER,
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
