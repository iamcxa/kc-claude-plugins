'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');

const {
  validateExpectEntries,
  summarizeSyntheticRunnerResults,
} = require('../e2e-test-contract.js');

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
