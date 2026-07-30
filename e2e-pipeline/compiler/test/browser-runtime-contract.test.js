'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const PIPELINE = path.join(__dirname, '..', '..');

function read(relativePath) {
  return fs.readFileSync(path.join(PIPELINE, relativePath), 'utf8');
}

test('e2e-test propagates one browser run identity to every browser runner', function() {
  const skill = read('skills/e2e-test/SKILL.md');

  assert.match(skill, /\| `browser_runtime` \|/);
  assert.match(skill, /\| `browser_run_id` \|/);
  assert.match(skill, /new-run-id/);
  assert.match(
    skill,
    /All browser teammates spawned for this invocation receive the same `browser_run_id`/
  );
  assert.match(
    skill,
    /A fresh\s+`\/e2e-test` replay MUST generate a new `browser_run_id`/
  );

  assert.match(
    skill,
    /name="runner"[\s\S]{0,900}browser_runtime:[^\n]+browser_run_id:/
  );
  assert.match(
    skill,
    /name="runner-<site\.alias>"[\s\S]{0,900}browser_runtime:[^\n]+browser_run_id:/
  );
  assert.match(
    skill,
    /Subagent mode[\s\S]+Execute E2E flow:[\s\S]{0,500}browser_runtime:[^\n]+browser_run_id:/
  );
});

test('e2e-test-runner routes browser commands through the shared runtime', function() {
  const runner = read('agents/e2e-test-runner.md');

  assert.match(runner, /\| `browser_runtime` \| Required \|/);
  assert.match(runner, /\| `browser_run_id` \| Required \|/);
  assert.match(
    runner,
    /browser_command: node "\{\{browser_runtime\}\}" --run-id "\{\{browser_run_id\}\}" --app "\{\{app\}\}"/
  );
  assert.match(runner, /Bare\s+`agent-browser` commands are prohibited/);
  assert.doesNotMatch(runner, /^\s*agent-browser\s/m);
});

test('canonical commands reference defines the isolated runtime prefix', function() {
  const commands = read('references/commands.md');

  assert.match(commands, /## E2E Browser Runtime \(Required\)/);
  assert.match(commands, /e2e-browser-runtime\.js/);
  assert.match(commands, /Chrome for Testing/);
  assert.match(commands, /--run-id "\$BROWSER_RUN_ID"/);
  assert.match(commands, /--app "\$APP"/);
  assert.match(commands, /Do not use `--auto-connect`, `--cdp`, or `connect`/);
});

test('e2e-test browser handoff closes through the owned runtime', function() {
  const skill = read('skills/e2e-test/SKILL.md');

  assert.doesNotMatch(skill, /agent-browser[^\n]*close/);
  assert.match(
    skill,
    /Browser handoff:[\s\S]{0,400}node "<absolute browser_runtime>" --run-id "<browser_run_id>" --app "<app>" --receipt "<browser_receipt>" close/
  );
});

test('shared Agent Teams guidance gives e2e-test runtime ownership precedence conditionally', function() {
  const teams = read('references/agent-teams.md');

  assert.match(teams, /shared runtime precedence/i);
  assert.match(
    teams,
    /Every browser teammate dispatch includes `browser_runtime`, `browser_run_id`,[\s\S]{0,500}takes precedence/
  );
  assert.match(teams, /Never fall back to a current\/default browser daemon/);
});

test('fresh e2e-test invocations recreate the team with full invocation state', function() {
  const skill = read('skills/e2e-test/SKILL.md');
  const teams = read('references/agent-teams.md');

  assert.match(skill, /fresh `\/e2e-test` invocation MUST NOT reuse an existing `e2e-test` team/);
  assert.match(
    skill,
    /app`, `auth_profile`, `base_url`, or `report_dir`[\s\S]{0,500}shutdown_request[\s\S]{0,500}TeamDelete\(\)[\s\S]{0,500}TeamCreate/
  );
  assert.match(skill, /Only a same-invocation `RE-RUN` may reuse the current teammates/);
  assert.doesNotMatch(skill, /new identity[\s\S]{0,200}closes only its old owned namespace/i);

  assert.match(
    teams,
    /fresh `\/e2e-test` invocation[\s\S]{0,500}teardown[\s\S]{0,500}full invocation fields/
  );
  assert.match(teams, /same-invocation `RE-RUN`[\s\S]{0,200}reuse/);
});

test('e2e-test runner rejects a different browser run identity without partial switching', function() {
  const runner = read('agents/e2e-test-runner.md');

  assert.match(
    runner,
    /Different identity:[\s\S]{0,500}reject[\s\S]{0,500}recreate the `e2e-test` team/i
  );
  assert.match(runner, /recoverable: false/);
  assert.doesNotMatch(runner, /close the old browser[\s\S]{0,300}update both fields/i);
  assert.doesNotMatch(runner, /fresh-identity switch rule/i);
});

test('every browser consumer receives the shared runtime ownership fields', function() {
  const consumers = [
    'skills/e2e-map/SKILL.md',
    'agents/e2e-mapper.md',
    'skills/e2e-walkthrough/SKILL.md',
    'skills/e2e-walkthrough/reference.md',
    'skills/e2e-flow/SKILL.md',
    'agents/e2e-flow-verifier.md',
  ];

  for (const consumer of consumers) {
    const source = read(consumer);
    assert.match(source, /browser_runtime/, consumer);
    assert.match(source, /browser_run_id/, consumer);
    assert.match(source, /browser_receipt/, consumer);
    assert.match(source, /e2e-browser-runtime\.js|browser_command/, consumer);
    assert.doesNotMatch(
      source,
      /^\s*agent-browser(?:\s|$)/m,
      consumer + ' contains a raw browser command'
    );
  }
});

test('compiled flows wrap every browser call with the owned runtime', function() {
  const codegen = read('compiler/codegen.js');
  const compiler = read('compiler/compiler.js');

  assert.match(codegen, /function generateBrowserRuntime/);
  assert.match(codegen, /E2E_BROWSER_RUNTIME/);
  assert.match(codegen, /E2E_BROWSER_RUN_ID/);
  assert.match(codegen, /E2E_BROWSER_RECEIPT_DIR/);
  assert.match(codegen, /agent-browser\(\)/);
  assert.match(codegen, /node "\$E2E_BROWSER_RUNTIME"/);
  assert.match(compiler, /browserApps/);
});

test('every orchestrator uses the shared local-service runtime without shell wait -n', function() {
  const consumers = [
    'skills/e2e-test/SKILL.md',
    'skills/e2e-map/SKILL.md',
    'skills/e2e-walkthrough/SKILL.md',
    'skills/e2e-flow/SKILL.md',
    'agents/e2e-test-runner.md',
    'agents/e2e-mapper.md',
    'agents/e2e-flow-verifier.md',
    'references/common-patterns.md',
  ];
  for (const consumer of consumers) {
    const source = read(consumer);
    assert.match(source, /service_runtime/, consumer);
    assert.match(source, /service_run_id/, consumer);
    assert.match(source, /service_state_dir/, consumer);
    assert.doesNotMatch(source, /\bwait\s+-n\b/, consumer);
  }
});

test('compiled flows supervise optional local services before browser work', function() {
  const codegen = read('compiler/codegen.js');

  assert.match(codegen, /function generateLocalServiceRuntime/);
  assert.match(codegen, /E2E_SERVICE_MANIFEST/);
  assert.match(codegen, /E2E_SERVICE_RUNTIME/);
  assert.match(codegen, /E2E_SERVICE_STATE_DIR/);
  assert.match(codegen, /preflight/);
  assert.match(codegen, /start/);
  assert.match(codegen, /stop/);
  assert.match(codegen, /local-service cleanup failed/);
  assert.doesNotMatch(
    codegen,
    /E2E_SERVICE_RUNTIME" stop[^\n]*\|\| true/
  );
  assert.doesNotMatch(codegen, /\bwait\s+-n\b/);
});

test('e2e-test promotes only recurring pipeline defects through the executable contract', function() {
  const skill = read('skills/e2e-test/SKILL.md');
  const reference = read('references/issue-promotion.md');

  assert.match(skill, /Read → `\$\{CLAUDE_PLUGIN_ROOT\}\/references\/issue-promotion\.md`/);
  assert.match(skill, /after results and D1\/D2 knowledge capture/i);
  assert.match(skill, /two distinct `browser_run_id` values/i);
  assert.match(skill, /Application bugs, ordinary test failures, model mistakes/i);
  assert.match(skill, /mode: auto[\s\S]{0,300}explicit repository-local authorization/i);
  assert.match(skill, /--candidate "\$REPORT_DIR\/issue-promotion-candidate\.json"/);
  assert.match(skill, /--run-id "\$browser_run_id"/);
  assert.match(skill, /--state-dir "\$PROMOTION_STATE"/);
  assert.match(
    skill,
    /node "\$\{CLAUDE_PLUGIN_ROOT\}\/bin\/e2e-issue-promotion\.js" "\$\{PROMOTION_ARGS\[@\]\}"/
  );

  assert.match(reference, /"kind": "pipeline-defect"/);
  assert.match(reference, /specific `e2e-pipeline\/` target/);
  assert.match(
    reference,
    /Do not include URLs,[\s\S]{0,80}credentials, selectors, test data/i
  );
  assert.match(reference, /default mode is `propose`/i);
  assert.match(reference, /closed match is not reopened/i);
});
