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
    /Browser handoff:[\s\S]{0,400}node "<absolute browser_runtime>" --run-id "<browser_run_id>" --app "<app>" close/
  );
});

test('shared Agent Teams guidance gives e2e-test runtime ownership precedence conditionally', function() {
  const teams = read('references/agent-teams.md');

  assert.match(teams, /e2e-test runtime precedence/i);
  assert.match(
    teams,
    /When a dispatch includes both `browser_runtime` and `browser_run_id`[\s\S]{0,500}takes precedence/
  );
  assert.match(teams, /Other consumers that do not provide both runtime fields[\s\S]{0,300}shared protocol/);
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
