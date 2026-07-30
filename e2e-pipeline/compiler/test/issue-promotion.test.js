'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  buildProposal,
  fingerprintCandidate,
  markerForFingerprint,
  recordObservation,
  validateCandidate,
} = require('../issue-promotion.js');

function candidate(overrides) {
  return Object.assign(
    {
      version: 1,
      kind: 'pipeline-defect',
      code: 'owned-runtime-reuse',
      source_skill: 'e2e-test',
      target: 'e2e-pipeline/bin/e2e-browser-runtime.js',
      summary: 'Owned browser guard accepted a reused daemon.',
      proposed_change: 'Reject reused daemon evidence before browser actions.',
    },
    overrides || {}
  );
}

test('validates a generic pipeline-defect candidate', function() {
  assert.deepEqual(validateCandidate(candidate()), candidate());
});

test('rejects candidates that are not actionable pipeline defects', function() {
  assert.throws(
    function() {
      validateCandidate(candidate({ kind: 'application-bug' }));
    },
    /kind must be pipeline-defect/
  );
  assert.throws(
    function() {
      validateCandidate(candidate({ target: '../consumer-app/login.js' }));
    },
    /target must name a file under e2e-pipeline/
  );
  assert.throws(
    function() {
      validateCandidate(candidate({ code: 'Maybe the browser is wrong' }));
    },
    /code must be a stable lowercase identifier/
  );
  for (const target of [
    'e2e-pipeline/',
    'e2e-pipeline/bin/',
    'e2e-pipeline/bin/runtime script.js',
    'e2e-pipeline/bin/runtime?.js',
  ]) {
    assert.throws(
      function() {
        validateCandidate(candidate({ target: target }));
      },
      /target must name a file under e2e-pipeline/
    );
  }
});

test('rejects unsafe issue text before it reaches local state or GitHub', function() {
  const unsafeValues = [
    'Failure at https://customer.example.test/login',
    'Failure at /Users/operator/private-project',
    'Failure at (/private/var/folders/operator/project)',
    'Failure at C:\\Users\\operator\\private-project',
    'Observed token=secret-value during the run',
    'First line\nsecond line',
  ];

  for (const unsafe of unsafeValues) {
    assert.throws(
      function() {
        validateCandidate(candidate({ summary: unsafe }));
      },
      /summary contains unsafe or project-specific text/
    );
  }
});

test('fingerprint is stable across wording changes for the same defect contract', function() {
  const first = fingerprintCandidate(candidate());
  const second = fingerprintCandidate(
    candidate({
      summary: 'A reused browser daemon passed the ownership guard.',
      proposed_change: 'Fail before issuing any browser command when reuse is detected.',
    })
  );

  assert.equal(first, second);
  assert.match(first, /^[a-f0-9]{64}$/);
});

test('same-run retries count once and a second distinct run qualifies', function() {
  const stateDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-issue-promotion-'));
  const first = recordObservation({
    candidate: candidate(),
    runId: 'run-one',
    stateDir: stateDir,
    observedAt: '2026-07-30T10:00:00.000Z',
  });
  const retry = recordObservation({
    candidate: candidate(),
    runId: 'run-one',
    stateDir: stateDir,
    observedAt: '2026-07-30T10:05:00.000Z',
  });
  const second = recordObservation({
    candidate: candidate(),
    runId: 'run-two',
    stateDir: stateDir,
    observedAt: '2026-07-30T11:00:00.000Z',
  });

  assert.equal(first.distinctRuns, 1);
  assert.equal(first.qualified, false);
  assert.equal(first.recorded, true);
  assert.equal(retry.distinctRuns, 1);
  assert.equal(retry.qualified, false);
  assert.equal(retry.recorded, false);
  assert.equal(second.distinctRuns, 2);
  assert.equal(second.qualified, true);

  const observationDir = path.join(
    stateDir,
    'observations',
    first.fingerprint
  );
  assert.deepEqual(fs.readdirSync(observationDir).sort(), [
    'run-one.json',
    'run-two.json',
  ]);
});

test('proposal is actionable, fingerprinted, and contains no raw run evidence', function() {
  const normalized = validateCandidate(candidate());
  const fingerprint = fingerprintCandidate(normalized);
  const proposal = buildProposal({
    candidate: normalized,
    fingerprint: fingerprint,
    distinctRuns: 2,
  });

  assert.match(proposal.title, /^e2e-pipeline: /);
  assert.match(proposal.body, /## Pipeline defect/);
  assert.match(proposal.body, /`e2e-pipeline\/bin\/e2e-browser-runtime\.js`/);
  assert.match(proposal.body, /Reject reused daemon evidence/);
  assert.match(proposal.body, /Observed in 2 distinct runs/);
  assert.match(proposal.body, new RegExp(markerForFingerprint(fingerprint)));
  assert.doesNotMatch(proposal.body, /run-one|run-two|customer|credential/i);
});
