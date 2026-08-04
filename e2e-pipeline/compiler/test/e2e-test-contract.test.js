'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { test, describe } = require('node:test');
const assert = require('node:assert/strict');

const {
  validateExpectEntries,
  summarizeSyntheticRunnerResults,
} = require('../e2e-test-contract.js');

const pluginRoot = path.resolve(__dirname, '..', '..');
const testRunnerAgent = path.join(pluginRoot, 'agents', 'e2e-test-runner.md');
const testSkill = path.join(pluginRoot, 'skills', 'e2e-test', 'SKILL.md');

describe('e2e-test not_automated contract harness', function() {
  test('strict v1 detector allows only exact not_automated objects', function() {
    const valid = validateExpectEntries([
      'email_input is visible',
      { not_automated: 'Verify the legal disclaimer copy with product counsel.' },
    ]);
    assert.deepEqual(valid.errors, []);

    const invalid = validateExpectEntries([
      { not_automated: 'Verify manually.', extra: true },
      { not_automated: '' },
      { not_automated: 12 },
      { manual: 'Verify manually.' },
    ]);
    assert.equal(invalid.errors.length, 4);
  });

  test('synthetic runner executes following step and reports not_automated separately', function() {
    const flow = {
      steps: [
        {
          id: 'active-and-hatch',
          expect: [
            'email_input is visible',
            { not_automated: 'Verify the legal disclaimer copy with product counsel.' },
          ],
        },
        {
          id: 'following-executable',
          expect: ['dashboard_heading is visible'],
        },
        {
          id: 'hatch-only',
          expect: [
            { not_automated: 'Verify third-party email delivery manually.' },
          ],
        },
      ],
    };

    const result = summarizeSyntheticRunnerResults(flow, {
      'email_input is visible': true,
      'dashboard_heading is visible': true,
    });

    assert.deepEqual(result.validationErrors, []);
    assert.deepEqual(result.executedStepIds, ['active-and-hatch', 'following-executable', 'hatch-only']);
    assert.equal(result.summary.passed, 2);
    assert.equal(result.summary.failed, 0);
    assert.equal(result.summary.skipped, 0);
    assert.equal(result.summary.not_automated, 2);
    assert.equal(result.steps[0].status, 'PASS');
    assert.equal(result.steps[1].status, 'PASS');
    assert.equal(result.steps[2].status, 'NOT_AUTOMATED');
  });
});

/**
 * #148. A run improvised past a step and then printed `Executed flow EXACTLY as
 * written`. That string is prose the runner model writes, not a deterministic
 * emission, so there was no conditional to make it contingent on — the only
 * enforcement point available is the instruction text itself. These assertions are
 * that enforcement point: they fail if the deviation ledger, the fidelity states, or
 * the ban on unearned exactness vocabulary is edited back out.
 */
describe('e2e-test run fidelity contract', function() {
  test('the runner tracks deviations and is told not to claim exactness', function() {
    const runner = fs.readFileSync(testRunnerAgent, 'utf8');

    assert.match(
      runner,
      /deviation: null\|\{did, instead_of\}/,
      'per-step result shape must carry a deviation field'
    );
    assert.match(
      runner,
      /Never assert exactness you did not track/,
      'the runner must be told not to claim exactness'
    );
    for (const banned of [
      'EXACTLY',
      'exactly as\\s+written',
      'faithfully replayed',
    ]) {
      assert.match(
        runner,
        new RegExp('Do not write[^.]*' + banned, 'i'),
        'the banned exactness vocabulary must name ' + banned
      );
    }
    assert.match(
      runner,
      /Executed 32\/34 steps; 1 step improvised/,
      'the honest replacement form must be shown, not merely described'
    );
    assert.match(
      runner,
      /A blocked control is a finding, not an obstacle to route around/,
      'improvising past a blocked control must be refused, since that is what hid the product defect'
    );
  });

  test('fidelity states are defined and unverified is reachable without the compiled check', function() {
    const runner = fs.readFileSync(testRunnerAgent, 'utf8');
    const skill = fs.readFileSync(testSkill, 'utf8');

    assert.match(runner, /\| Step Fidelity \|/, 'the summary must report step fidelity');
    for (const state of ['as-written', 'N deviation\\(s\\)', 'unverified']) {
      assert.match(
        runner,
        new RegExp('`' + state + '`'),
        'fidelity state ' + state + ' must be defined'
      );
    }
    assert.match(
      runner,
      /Do not upgrade\s+`unverified` to `as-written` on the strength of an empty ledger/,
      'an empty self-reported ledger must not be laundered into an as-written claim'
    );
    assert.match(
      skill,
      /Whenever this phase is skipped for any reason, the report's `Step Fidelity` row is\s+`unverified`/,
      'skipping the compiled cross-check must force the unverified fidelity state'
    );
  });
});
