'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const yaml = require('js-yaml');

const PIPELINE = path.join(__dirname, '..', '..');

function read(relativePath) {
  return fs.readFileSync(path.join(PIPELINE, relativePath), 'utf8');
}

function assertMessageContract(source, verb, expectedCount) {
  const pattern = new RegExp('message="(' + verb + '\\\\n[^"]*)"', 'g');
  const messages = Array.from(source.matchAll(pattern), function(match) {
    return match[1];
  });
  assert.equal(messages.length, expectedCount, verb + ' template count');
  for (const message of messages) {
    for (const field of [
      'browser_runtime',
      'browser_run_id',
      'auth_mode',
      'canonical_auth_profile',
      'auth_profile',
      'auth_profile_freshness',
    ]) {
      assert.match(message, new RegExp('(?:^|\\\\n)' + field + ':'), verb + ' missing ' + field);
    }
    if (message.includes('auth_mode: persistent\\n')) {
      assert.doesNotMatch(message, /(?:^|\\n)ephemeral_auth_profile:/);
    } else {
      assert.match(message, /(?:^|\\n)ephemeral_auth_profile:/);
    }
  }
}

test('RED fixture declares login as flow-managed behavior', function() {
  const fixture = yaml.load(read('compiler/test/fixtures/flow-managed-auth.yaml'));

  assert.equal(fixture.auth_mode, 'flow-managed');
  assert.equal(fixture.steps[0].action, 'Navigate to /auth/login');
  assert.match(fixture.steps[0].expect.join('\n'), /email_input visible/);
});

test('e2e-test validates flow-managed auth and prepares a fresh profile per replay', function() {
  const skill = read('skills/e2e-test/SKILL.md');

  assert.match(skill, /`auth_mode`[\s\S]{0,200}`persistent`[\s\S]{0,200}`flow-managed`/);
  assert.match(skill, /prepare-flow-managed-profile/);
  assert.match(
    skill,
    /canonical_auth_profile[\s\S]{0,500}ephemeral_auth_profile[\s\S]{0,500}auth_profile_freshness/
  );
  assert.match(
    skill,
    /same-invocation `RE-RUN`[\s\S]{0,700}(?:new|different) (?:fresh )?(?:ephemeral )?profile/i
  );
  assert.match(skill, /Phase 1\.8 skipped — flow-managed auth/);
});

test('runner skips setup auth only for flow-managed mode and reports lifecycle', function() {
  const runner = read('agents/e2e-test-runner.md');

  assert.match(runner, /\| `auth_mode` \| Required \| `persistent` or `flow-managed`/);
  assert.match(
    runner,
    /If `auth_mode` is `flow-managed`[\s\S]{0,500}skip[\s\S]{0,500}(?:verification|auto-login)/i
  );
  assert.match(
    runner,
    /If `auth_mode` is `persistent`[\s\S]{0,500}(?:verify|verification)[\s\S]{0,500}auto-login/i
  );
  assert.match(runner, /verify-flow-managed-profile/);
  assert.match(runner, /cleanup-flow-managed-profile/);
  assert.match(runner, /ephemeral_auth_profile[\s\S]{0,200}equal[\s\S]{0,200}auth_profile/i);
  assert.match(runner, /\{\{runtime_base_command\}\} --version/);
  assert.match(
    runner,
    /Auth Profile Lifecycle[\s\S]{0,800}freshness[\s\S]{0,800}binding[\s\S]{0,800}cleanup/i
  );
});

test('cross-skill browser guidance preserves persistent default and declared isolation', function() {
  const flow = read('skills/e2e-flow/SKILL.md');
  const verifier = read('agents/e2e-flow-verifier.md');
  const walkthrough = read('skills/e2e-walkthrough/SKILL.md');
  const walkthroughReference = read('skills/e2e-walkthrough/reference.md');
  const teams = read('references/agent-teams.md');
  const common = read('references/common-patterns.md');
  const commands = read('references/commands.md');

  for (const source of [flow, verifier, walkthrough, walkthroughReference, teams, common, commands]) {
    assert.match(source, /flow-managed/);
  }
  assert.match(
    verifier,
    /persistent verifier accepts only `auth_mode: persistent`[\s\S]{0,200}flow-managed/i
  );
  assert.match(teams, /RE-RUN[\s\S]{0,700}(?:new|different) (?:fresh )?(?:ephemeral )?profile/i);
  assert.match(common, /canonical[\s\S]{0,500}(?:unchanged|unmodified)/i);
});

test('Teams examples repeat complete auth and runtime contracts and finalize routed flows', function() {
  const skill = read('skills/e2e-test/SKILL.md');
  const runner = read('agents/e2e-test-runner.md');

  assertMessageContract(skill, 'EXECUTE_FLOW', 2);
  assertMessageContract(skill, 'EXECUTE_STEP', 2);
  assertMessageContract(skill, 'RE-RUN', 2);
  assert.match(
    skill,
    /FINALIZE_FLOW[\s\S]{0,4000}Wait for `TRACE FINALIZED`[\s\S]{0,500}before Phase 1\.75 trace analysis[\s\S]{0,100}aggregation/i
  );
  assert.match(
    runner,
    /On receiving FINALIZE_FLOW[\s\S]{0,3000}team-trace-lifecycle\.sh[\s\S]{0,2000}cleanup-flow-managed-profile[\s\S]{0,2000}TRACE FINALIZED/i
  );
});

test('Teams suites prepare and serialize fresh flow-managed bindings per runner command', function() {
  const skill = read('skills/e2e-test/SKILL.md');
  const teams = skill.slice(
    skill.indexOf('### Teams mode — Multi-role parallel testing'),
    skill.indexOf('## Phase 1.5')
  );

  assert.match(
    teams,
    /immediately before[\s\S]{0,500}`EXECUTE_FLOW`[\s\S]{0,500}`BEGIN_FLOW`[\s\S]{0,500}prepare-flow-managed-profile/i
  );
  assert.match(
    teams,
    /one active[\s\S]{0,300}(?:command|flow)[\s\S]{0,500}(?:FLOW COMPLETE|TRACE FINALIZED)[\s\S]{0,500}cleanup/i
  );
  assert.match(
    teams,
    /sequential suite entr(?:y|ies)[\s\S]{0,800}(?:new|different)[\s\S]{0,300}profile/i
  );
});

test('Teams flow commands adopt and verify each prepared profile before trace or steps', function() {
  const runner = read('agents/e2e-test-runner.md');
  const startup = runner.slice(
    runner.indexOf('### Startup'),
    runner.indexOf('### On receiving EXECUTE_FLOW')
  );
  const executeFlow = runner.slice(
    runner.indexOf('### On receiving EXECUTE_FLOW'),
    runner.indexOf('### On receiving EXECUTE_STEP')
  );
  const beginFlow = runner.slice(
    runner.indexOf('### On receiving BEGIN_FLOW'),
    runner.indexOf('### On receiving FINALIZE_FLOW')
  );

  for (const section of [executeFlow, beginFlow]) {
    assert.match(
      section,
      /flow-managed[\s\S]{0,1800}prepared[\s\S]{0,800}\{\{browser_command\}\} --headed open[\s\S]{0,500}verify-flow-managed-profile/i
    );
    assert.match(
      section,
      /after (?:the )?prior\s+cleanup[\s\S]{0,600}(?:new|different|differ)[\s\S]{0,300}profile/i
    );
    assert.match(section, /fail closed/i);
  }
  assert.match(
    startup,
    /flow-managed[\s\S]{0,1200}(?:does not|do not)[\s\S]{0,400}open[\s\S]{0,400}profile/i
  );
  assert.match(startup, /active_auth_profile[\s\S]{0,200}(?:empty|unset)/i);
  assert.ok(
    executeFlow.indexOf('{{browser_command}} --headed open') <
      executeFlow.indexOf('Start one fresh trace'),
    'EXECUTE_FLOW must adopt the profile before trace start'
  );
  assert.ok(
    beginFlow.indexOf('{{browser_command}} --headed open') <
      beginFlow.indexOf('"$TRACE_LIFECYCLE" begin'),
    'BEGIN_FLOW must adopt the profile before trace start'
  );
});

test('FLOW COMPLETE exposes independent flow trace and profile lifecycle results', function() {
  const runner = read('agents/e2e-test-runner.md');
  const section = runner.slice(
    runner.indexOf('### On receiving EXECUTE_FLOW'),
    runner.indexOf('### On receiving EXECUTE_STEP')
  );
  const match = section.match(/message="(FLOW COMPLETE\\n[^"]*)"/);

  assert.ok(match, 'FLOW COMPLETE outbound template must exist');
  for (const field of [
    'flow_verdict',
    'trace_infrastructure_result',
    'profile_infrastructure_result',
    'auth_profile_binding',
    'auth_profile_cleanup',
    'canonical_profile',
    'profile_retained',
    'profile',
  ]) {
    assert.match(match[1], new RegExp('(?:^|\\\\n)' + field + ':'), 'FLOW COMPLETE missing ' + field);
  }
  assert.match(
    section,
    /preserve[\s\S]{0,800}flow_verdict[\s\S]{0,800}trace_infrastructure_result[\s\S]{0,800}profile_infrastructure_result/i
  );
});

test('flow authoring preserves auth_mode and defers canonical pre-warm until mode is known', function() {
  const flow = read('skills/e2e-flow/SKILL.md');
  const verifier = read('agents/e2e-flow-verifier.md');
  const walkthroughReference = read('skills/e2e-walkthrough/reference.md');

  assert.match(
    flow,
    /defer[\s\S]{0,300}(?:pre-warm|browser)[\s\S]{0,500}auth_mode[\s\S]{0,500}persistent/i
  );
  assert.doesNotMatch(
    flow,
    /spawn the verifier teammate BEFORE dispatching the writer/i
  );
  assert.match(
    flow,
    /name="verifier"[\s\S]{0,1000}flow_path:[^\n]+\n\s+mapping_path:[^\n]+\n\s+auth_mode: persistent/
  );
  assert.doesNotMatch(
    verifier,
    /pre-warms you during flow generation|browser is ready before the flow YAML exists/i
  );
  assert.match(
    walkthroughReference,
    /valid keys:[^\n]*`auth_mode`/
  );
});

test('FINALIZE_FLOW persists trace evidence before profile cleanup', function() {
  const runner = read('agents/e2e-test-runner.md');
  const section = runner.slice(
    runner.indexOf('### On receiving FINALIZE_FLOW'),
    runner.indexOf('### On receiving shutdown_request')
  );

  assert.match(section, /trace_path: \{\{report_dir\}\}\/runs\/<flow_run_id>\/trace\.zip/);
  assert.match(section, /team-trace-lifecycle\.sh/);
  assert.match(section, /cleanup-flow-managed-profile/);
  assert.ok(
    section.indexOf('"$TRACE_LIFECYCLE" finalize') <
      section.indexOf('cleanup-flow-managed-profile'),
    'shared bounded trace finalizer must precede profile cleanup'
  );
  assert.match(
    section,
    /trace `infrastructure_result`[\s\S]{0,1200}profile_infrastructure_result/i
  );
  assert.match(
    section,
    /cleanup[\s\S]{0,300}`removed`[\s\S]{0,300}active_auth_profile[\s\S]{0,300}regardless[\s\S]{0,300}trace/i
  );
  assert.match(section, /profile_retained: false/);
});
