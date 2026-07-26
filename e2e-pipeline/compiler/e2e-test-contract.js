'use strict';

function isNotAutomatedExpect(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  var keys = Object.keys(value);
  return keys.length === 1 &&
    keys[0] === 'not_automated' &&
    typeof value.not_automated === 'string' &&
    value.not_automated.trim().length > 0;
}

function validateExpectEntries(expects) {
  var errors = [];
  var entries = Array.isArray(expects) ? expects : [];
  entries.forEach(function(expect, index) {
    if (typeof expect === 'string') return;
    if (isNotAutomatedExpect(expect)) return;
    errors.push({
      index: index,
      message: 'expect entries must be strings or exactly {not_automated: <non-empty string>}',
    });
  });
  return { errors: errors };
}

function summarizeSyntheticRunnerResults(flow, activeExpectResults) {
  var validationErrors = [];
  var executedStepIds = [];
  var steps = [];
  var summary = {
    total_steps: (flow.steps || []).length,
    passed: 0,
    failed: 0,
    skipped: 0,
    not_automated: 0,
  };

  (flow.steps || []).forEach(function(step) {
    var expects = Array.isArray(step.expect) ? step.expect : [];
    var validation = validateExpectEntries(expects);
    validation.errors.forEach(function(error) {
      validationErrors.push({ stepId: step.id, index: error.index, message: error.message });
    });
    if (validation.errors.length > 0) {
      steps.push({ id: step.id, status: 'SKIP', expectations: [] });
      summary.skipped++;
      return;
    }

    executedStepIds.push(step.id);
    var expectationResults = [];
    var activeCount = 0;
    var failedCount = 0;
    var notAutomatedCount = 0;

    expects.forEach(function(expect) {
      if (isNotAutomatedExpect(expect)) {
        notAutomatedCount++;
        summary.not_automated++;
        expectationResults.push({
          status: 'not_automated',
          reason: expect.not_automated.trim(),
        });
        return;
      }

      activeCount++;
      if (activeExpectResults && activeExpectResults[expect] === false) {
        failedCount++;
        expectationResults.push({ status: 'fail', raw: expect });
      } else {
        expectationResults.push({ status: 'pass', raw: expect });
      }
    });

    var status;
    if (failedCount > 0) {
      status = 'FAIL';
      summary.failed++;
    } else if (activeCount > 0) {
      status = 'PASS';
      summary.passed++;
    } else if (notAutomatedCount > 0) {
      status = 'NOT_AUTOMATED';
    } else {
      status = 'PASS';
      summary.passed++;
    }
    steps.push({ id: step.id, status: status, expectations: expectationResults });
  });

  return {
    validationErrors: validationErrors,
    executedStepIds: executedStepIds,
    steps: steps,
    summary: summary,
  };
}

module.exports = {
  isNotAutomatedExpect: isNotAutomatedExpect,
  validateExpectEntries: validateExpectEntries,
  summarizeSyntheticRunnerResults: summarizeSyntheticRunnerResults,
};
