'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const PIPELINE = path.join(__dirname, '..', '..');
const CLI = path.join(PIPELINE, 'bin', 'e2e-issue-promotion.js');

function candidate() {
  return {
    version: 1,
    kind: 'pipeline-defect',
    code: 'owned-runtime-reuse',
    source_skill: 'e2e-test',
    target: 'e2e-pipeline/bin/e2e-browser-runtime.js',
    summary: 'Owned browser guard accepted a reused daemon.',
    proposed_change: 'Reject reused daemon evidence before browser actions.',
  };
}

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-issue-cli-'));
  const binDir = path.join(root, 'bin');
  const candidatePath = path.join(root, 'candidate.json');
  const stateDir = path.join(root, 'state');
  const ghLog = path.join(root, 'gh.log');
  fs.mkdirSync(binDir);
  fs.writeFileSync(candidatePath, JSON.stringify(candidate(), null, 2));
  const fakeGh = path.join(binDir, 'gh');
  fs.writeFileSync(
    fakeGh,
    [
      '#!/usr/bin/env node',
      "'use strict';",
      "const fs = require('node:fs');",
      'const args = process.argv.slice(2);',
      "fs.appendFileSync(process.env.GH_LOG, args.join(' ') + '\\n');",
      "if (args[0] === 'issue' && args[1] === 'list') {",
      "  process.stdout.write(process.env.GH_ISSUES_JSON || '[]');",
      '  process.exit(Number(process.env.GH_LIST_RC || 0));',
      '}',
      "if (args[0] === 'label' && args[1] === 'create') {",
      '  process.exit(Number(process.env.GH_LABEL_RC || 0));',
      '}',
      "if (args[0] === 'issue' && args[1] === 'create') {",
      "  process.stdout.write(process.env.GH_CREATE_URL || 'https://github.com/iamcxa/kc-claude-plugins/issues/123');",
      '  process.exit(Number(process.env.GH_CREATE_RC || 0));',
      '}',
      'process.exit(2);',
      '',
    ].join('\n')
  );
  fs.chmodSync(fakeGh, 0o755);
  return {
    root: root,
    binDir: binDir,
    candidatePath: candidatePath,
    stateDir: stateDir,
    ghLog: ghLog,
  };
}

function runCli(work, runId, options) {
  const args = [
    CLI,
    '--candidate',
    work.candidatePath,
    '--run-id',
    runId,
    '--state-dir',
    work.stateDir,
  ];
  if (options?.configPath) {
    args.push('--config', options.configPath);
  }
  const result = spawnSync(process.execPath, args, {
    cwd: work.root,
    encoding: 'utf8',
    env: Object.assign({}, process.env, {
      GH_LOG: work.ghLog,
      GH_ISSUES_JSON: '[]',
      PATH: work.binDir + path.delimiter + process.env.PATH,
    }, options?.env || {}),
  });
  return result;
}

function parseResult(result) {
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
}

function writeAutoConfig(work) {
  const configPath = path.join(work.root, 'issue-promotion.json');
  fs.writeFileSync(
    configPath,
    JSON.stringify({
      version: 1,
      mode: 'auto',
      repo: 'iamcxa/kc-claude-plugins',
      min_distinct_runs: 2,
    })
  );
  return configPath;
}

function issueWithFingerprint(first, overrides) {
  return JSON.stringify([
    Object.assign(
      {
        number: 76,
        state: 'OPEN',
        url: 'https://github.com/iamcxa/kc-claude-plugins/issues/76',
        body:
          '<!-- e2e-pipeline-improvement:v1:' +
          first.fingerprint +
          ' -->',
      },
      overrides || {}
    ),
  ]);
}

test('default proposal mode records two runs without invoking GitHub', function() {
  const work = fixture();
  const first = parseResult(runCli(work, 'run-one'));
  const second = parseResult(runCli(work, 'run-two'));

  assert.equal(first.status, 'recorded');
  assert.equal(first.distinct_runs, 1);
  assert.equal(second.status, 'proposal');
  assert.equal(second.distinct_runs, 2);
  assert.equal(fs.existsSync(second.proposal_path), true);
  assert.equal(fs.existsSync(work.ghLog), false);
});

test('auto mode is enabled only by explicit repository config', function() {
  const work = fixture();
  const invalidConfig = path.join(work.root, 'invalid-config.json');
  fs.writeFileSync(
    invalidConfig,
    JSON.stringify({
      version: 1,
      mode: 'auto',
      min_distinct_runs: 2,
    })
  );

  parseResult(runCli(work, 'run-one', { configPath: invalidConfig }));
  const second = parseResult(
    runCli(work, 'run-two', { configPath: invalidConfig })
  );

  assert.equal(second.status, 'proposal');
  assert.match(second.config_warning, /falling back to propose mode/);
  assert.equal(fs.existsSync(work.ghLog), false);
});

test('auto mode cannot redirect filing away from the plugin origin repo', function() {
  const work = fixture();
  const configPath = path.join(work.root, 'redirect-config.json');
  fs.writeFileSync(
    configPath,
    JSON.stringify({
      version: 1,
      mode: 'auto',
      repo: 'someone-else/unrelated-repo',
      min_distinct_runs: 2,
    })
  );

  parseResult(runCli(work, 'run-one', { configPath: configPath }));
  const second = parseResult(
    runCli(work, 'run-two', { configPath: configPath })
  );

  assert.equal(second.status, 'proposal');
  assert.match(second.config_warning, /falling back to propose mode/);
  assert.equal(fs.existsSync(work.ghLog), false);
});

test('auto mode searches all issue states before creating one issue', function() {
  const work = fixture();
  const configPath = writeAutoConfig(work);
  parseResult(runCli(work, 'run-one', { configPath: configPath }));
  const second = parseResult(
    runCli(work, 'run-two', { configPath: configPath })
  );

  assert.equal(second.status, 'filed');
  assert.equal(
    second.issue_url,
    'https://github.com/iamcxa/kc-claude-plugins/issues/123'
  );
  const calls = fs.readFileSync(work.ghLog, 'utf8').trim().split('\n');
  assert.match(
    calls[0],
    /^issue list .*--state all .*--limit 100 .*--json number,state,url,body/
  );
  assert.match(calls[1], /^label create e2e-pipeline-improvement /);
  assert.match(calls[2], /^issue create /);
});

test('label failure files without a label and preserves a manual-label warning', function() {
  const work = fixture();
  const configPath = writeAutoConfig(work);
  parseResult(runCli(work, 'run-one', { configPath: configPath }));
  const second = parseResult(
    runCli(work, 'run-two', {
      configPath: configPath,
      env: { GH_LABEL_RC: '1' },
    })
  );

  assert.equal(second.status, 'filed');
  assert.equal(second.label_applied, false);
  const calls = fs.readFileSync(work.ghLog, 'utf8').trim().split('\n');
  assert.match(calls[1], /^label create e2e-pipeline-improvement /);
  assert.match(calls[2], /^issue create /);
  assert.doesNotMatch(calls[2], /--label e2e-pipeline-improvement/);
  assert.equal(fs.existsSync(second.proposal_path + '.unlabeled'), false);
});

test('a matching closed issue suppresses resurrection', function() {
  const work = fixture();
  const configPath = writeAutoConfig(work);
  const first = parseResult(
    runCli(work, 'run-one', { configPath: configPath })
  );
  assert.equal(first.status, 'recorded');

  const closedIssue = issueWithFingerprint(first, {
    number: 77,
    state: 'CLOSED',
    url: 'https://github.com/iamcxa/kc-claude-plugins/issues/77',
  });
  const second = parseResult(
    runCli(work, 'run-two', {
      configPath: configPath,
      env: { GH_ISSUES_JSON: closedIssue },
    })
  );

  assert.equal(second.status, 'suppressed_closed');
  assert.equal(second.issue_number, 77);
  const calls = fs.readFileSync(work.ghLog, 'utf8').trim().split('\n');
  assert.equal(calls.length, 1);
  assert.match(calls[0], /^issue list /);
});

test('a matching open issue is deduplicated without another write', function() {
  const work = fixture();
  const configPath = writeAutoConfig(work);
  const first = parseResult(
    runCli(work, 'run-one', { configPath: configPath })
  );
  const second = parseResult(
    runCli(work, 'run-two', {
      configPath: configPath,
      env: { GH_ISSUES_JSON: issueWithFingerprint(first) },
    })
  );

  assert.equal(second.status, 'deduplicated');
  assert.equal(second.issue_number, 76);
  const calls = fs.readFileSync(work.ghLog, 'utf8').trim().split('\n');
  assert.deepEqual(calls.map((call) => call.split(' ').slice(0, 2).join(' ')), [
    'issue list',
  ]);
});

test('an open match wins when both closed and open matches exist', function() {
  const work = fixture();
  const configPath = writeAutoConfig(work);
  const first = parseResult(
    runCli(work, 'run-one', { configPath: configPath })
  );
  const marker =
    '<!-- e2e-pipeline-improvement:v1:' + first.fingerprint + ' -->';
  const matches = JSON.stringify([
    {
      number: 70,
      state: 'CLOSED',
      url: 'https://github.com/iamcxa/kc-claude-plugins/issues/70',
      body: marker,
    },
    {
      number: 71,
      state: 'OPEN',
      url: 'https://github.com/iamcxa/kc-claude-plugins/issues/71',
      body: marker,
    },
  ]);

  const second = parseResult(
    runCli(work, 'run-two', {
      configPath: configPath,
      env: { GH_ISSUES_JSON: matches },
    })
  );

  assert.equal(second.status, 'deduplicated');
  assert.equal(second.issue_number, 71);
});

test('a same-run retry never reaches GitHub after qualification', function() {
  const work = fixture();
  const configPath = writeAutoConfig(work);
  parseResult(runCli(work, 'run-one', { configPath: configPath }));
  parseResult(runCli(work, 'run-two', {
    configPath: configPath,
    env: { GH_LIST_RC: '1' },
  }));
  fs.writeFileSync(work.ghLog, '');

  const retry = parseResult(
    runCli(work, 'run-two', { configPath: configPath })
  );

  assert.equal(retry.status, 'duplicate_run');
  assert.equal(fs.readFileSync(work.ghLog, 'utf8'), '');
});

test('GitHub failure preserves the local proposal and does not fail the run', function() {
  const work = fixture();
  const configPath = writeAutoConfig(work);
  parseResult(runCli(work, 'run-one', { configPath: configPath }));
  const second = parseResult(
    runCli(work, 'run-two', {
      configPath: configPath,
      env: { GH_LIST_RC: '1' },
    })
  );

  assert.equal(second.status, 'filing_failed');
  assert.match(second.error, /GitHub issue search failed/);
  assert.equal(fs.existsSync(second.proposal_path), true);
});
