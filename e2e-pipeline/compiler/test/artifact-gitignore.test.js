'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { test } = require('node:test');

const pluginRoot = path.resolve(__dirname, '..', '..');
const ensureGitignore = path.join(
  pluginRoot,
  'scripts',
  'ensure-e2e-gitignore.sh'
);
const requiredPatterns = [
  '.claude/e2e/reports/**/*.webm',
  '.claude/e2e/reports/**/*.mp4',
  '.claude/e2e/reports/**/trace.zip',
  '.claude/e2e/reports/**/trace.json',
  '.claude/e2e/reports/**/trace.invalid-*.zip',
  '.claude/e2e/reports/**/trace.invalid-*.json',
  '.claude/e2e/reports/**/*.gif',
];

function run(projectRoot) {
  return spawnSync('bash', [ensureGitignore, '--project-root', projectRoot], {
    encoding: 'utf8',
  });
}

function runForReportDir(reportDir) {
  return spawnSync('bash', [ensureGitignore, '--report-dir', reportDir], {
    encoding: 'utf8',
  });
}

test('adds every missing E2E artifact rule and remains idempotent', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-gitignore-'));
  const gitignore = path.join(directory, '.gitignore');
  try {
    fs.writeFileSync(
      gitignore,
      [
        '# existing rules',
        '.claude/e2e/reports/**/trace.invalid-*.json',
        '# .claude/e2e/reports/**/trace.json',
        '',
      ].join('\n')
    );

    const first = run(directory);
    assert.equal(first.status, 0, first.stderr);
    const second = run(directory);
    assert.equal(second.status, 0, second.stderr);

    const lines = fs.readFileSync(gitignore, 'utf8').split('\n');
    for (const pattern of requiredPatterns) {
      assert.equal(
        lines.filter((line) => line === pattern).length,
        1,
        `${pattern} must be present exactly once`
      );
    }
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('preserves an existing unterminated rule before appending artifact rules', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-gitignore-'));
  const gitignore = path.join(directory, '.gitignore');
  try {
    fs.writeFileSync(gitignore, 'node_modules/');

    const first = run(directory);
    assert.equal(first.status, 0, first.stderr);
    const second = run(directory);
    assert.equal(second.status, 0, second.stderr);

    const lines = fs.readFileSync(gitignore, 'utf8').split('\n');
    assert.equal(lines[0], 'node_modules/');
    for (const pattern of requiredPatterns) {
      assert.equal(
        lines.filter((line) => line === pattern).length,
        1,
        `${pattern} must be present exactly once`
      );
    }
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('does not rewrite a complete read-only gitignore only to add a newline', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-gitignore-'));
  const gitignore = path.join(directory, '.gitignore');
  const contents = requiredPatterns.join('\n');
  try {
    fs.writeFileSync(gitignore, contents, { mode: 0o444 });

    const result = run(directory);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(fs.readFileSync(gitignore, 'utf8'), contents);
  } finally {
    if (fs.existsSync(gitignore)) {
      fs.chmodSync(gitignore, 0o600);
    }
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('creates the artifact ignore file but rejects a symlink destination', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-gitignore-'));
  const target = path.join(directory, 'foreign-ignore');
  const gitignore = path.join(directory, '.gitignore');
  try {
    const created = run(directory);
    assert.equal(created.status, 0, created.stderr);
    assert.ok(fs.existsSync(gitignore));

    fs.rmSync(gitignore);
    fs.writeFileSync(target, 'foreign\n');
    fs.symlinkSync(target, gitignore);
    const rejected = run(directory);
    assert.notEqual(rejected.status, 0);
    assert.match(rejected.stderr, /regular file|symlink/i);
    assert.equal(fs.readFileSync(target, 'utf8'), 'foreign\n');
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('every browser artifact producer uses the shared gitignore helper', () => {
  for (const [relativePath, reportDir] of [
    ['agents/e2e-test-runner.md', '"{{report_dir}}"'],
    ['agents/e2e-flow-verifier.md', '"{{report_dir}}"'],
    ['skills/e2e-walkthrough/reference.md', '"$REPORT_DIR"'],
  ]) {
    const content = fs.readFileSync(path.join(pluginRoot, relativePath), 'utf8');
    assert.match(
      content,
      /\$\{CLAUDE_PLUGIN_ROOT\}\/scripts\/ensure-e2e-gitignore\.sh/,
      `${relativePath} must invoke the shared gitignore helper`
    );
    assert.ok(
      content.includes(`--report-dir ${reportDir}`),
      `${relativePath} must derive the app root from its report directory`
    );
  }
});

test('derives project roots from nested report directories', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-gitignore-'));
  const reportDir = path.join(
    directory,
    '.claude',
    'e2e',
    'reports',
    'run-1',
    'site-a'
  );
  try {
    fs.mkdirSync(reportDir, { recursive: true });

    const result = runForReportDir(reportDir);
    assert.equal(result.status, 0, result.stderr);
    assert.ok(fs.existsSync(path.join(directory, '.gitignore')));
    assert.ok(!fs.existsSync(path.join(reportDir, '.gitignore')));
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('writes app-local rules that Git honors below a nested monorepo package', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-gitignore-'));
  const nestedProject = path.join(directory, 'packages', 'app');
  const reportDir = path.join(
    nestedProject,
    '.claude',
    'e2e',
    'reports',
    'run-1'
  );
  try {
    fs.mkdirSync(reportDir, { recursive: true });
    const initialized = spawnSync('git', ['init', '-q', directory], {
      encoding: 'utf8',
    });
    assert.equal(initialized.status, 0, initialized.stderr);

    const result = runForReportDir(reportDir);
    assert.equal(result.status, 0, result.stderr);
    assert.ok(!fs.existsSync(path.join(directory, '.gitignore')));
    assert.ok(fs.existsSync(path.join(nestedProject, '.gitignore')));

    const artifact = path.join(reportDir, 'video.mp4');
    fs.writeFileSync(artifact, 'not-real-media');
    const ignored = spawnSync(
      'git',
      [
        '-C',
        directory,
        'check-ignore',
        '-q',
        path.relative(directory, artifact),
      ],
      { encoding: 'utf8' }
    );
    assert.equal(ignored.status, 0, ignored.stderr);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('report-based producers delegate project-root discovery to the helper', () => {
  for (const relativePath of [
    'agents/e2e-test-runner.md',
    'agents/e2e-flow-verifier.md',
  ]) {
    const content = fs.readFileSync(path.join(pluginRoot, relativePath), 'utf8');
    assert.match(
      content,
      /ensure-e2e-gitignore\.sh" --report-dir "\{\{report_dir\}\}"/,
      `${relativePath} must delegate report-root discovery to the helper`
    );
  }
});

test('common artifact guidance delegates app-root discovery to the helper', () => {
  const content = fs.readFileSync(
    path.join(pluginRoot, 'references/common-patterns.md'),
    'utf8'
  );
  assert.ok(
    content.includes('--report-dir "$REPORT_DIR"'),
    'common artifact guidance must derive the app root from its report directory'
  );
});
