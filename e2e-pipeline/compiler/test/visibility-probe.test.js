'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const MODULE_PATH = path.join(__dirname, '..', 'lib', 'visibility-probe.js');
const CLI_PATH = path.join(__dirname, '..', '..', 'bin', 'e2e-visibility-probe.js');
const {
  buildProbeExpression,
  classifyVisibility,
  judgeVisibility,
  renderStandaloneSupport,
  unwrapEvalEnvelope,
} = require(MODULE_PATH);

function evidence(matchCount, rendered, zeroRect, nonStyle) {
  return {
    probe_version: 1,
    probe_scope: 'current-document',
    match_count: matchCount,
    nonzero_layout_visible_count: rendered,
    style_visible_zero_rect_count: zeroRect,
    non_style_visible_count: nonStyle,
    candidate_evidence_limit: 10,
    candidate_evidence_truncated: matchCount > 10,
    candidates: [],
  };
}

test('visibility probe exposes the shared compiler and CLI seam', function () {
  const probe = require(MODULE_PATH);

  assert.deepEqual(Object.keys(probe).sort(), [
    'buildProbeExpression',
    'classifyVisibility',
    'judgeVisibility',
    'renderStandaloneSupport',
    'unwrapEvalEnvelope',
  ]);
  assert.equal(fs.existsSync(CLI_PATH), true);
});

const ALGEBRA_CASES = [
  ['no matches', evidence(0, 0, 0, 0), 'strict', 'no_match'],
  ['one non-rendered match', evidence(1, 0, 0, 1), 'strict', 'all_non_rendered'],
  ['multiple non-rendered matches', evidence(3, 0, 2, 1), 'strict', 'all_non_rendered'],
  ['one rendered match', evidence(1, 1, 0, 0), 'strict', 'unique_rendered'],
  ['strict ghost duplicate', evidence(2, 1, 1, 0), 'strict', 'raw_multi_match'],
  [
    'eligible retained-zero-rect duplicate',
    evidence(2, 1, 1, 0),
    'retained-zero-rect',
    'unique_rendered_with_retained_zero_rect',
  ],
  [
    'display-none, visibility-hidden, or opacity-hidden extra',
    evidence(2, 1, 0, 1),
    'retained-zero-rect',
    'raw_multi_match',
  ],
  ['two rendered matches', evidence(2, 2, 0, 0), 'retained-zero-rect', 'multiple_rendered'],
];

for (const [name, probeEvidence, policy, expected] of ALGEBRA_CASES) {
  test('classifyVisibility: ' + name + ' -> ' + expected, function () {
    const classified = classifyVisibility(probeEvidence, policy);
    assert.equal(classified.result, expected);
    assert.equal(classified.policy, policy);
    assert.equal(classified.match_count, probeEvidence.match_count);
  });
}

test('classifyVisibility: invalid policy and inconsistent aggregates fail as probe_error', function () {
  assert.equal(classifyVisibility(evidence(1, 1, 0, 0), 'any-visible').result, 'probe_error');
  assert.equal(classifyVisibility(evidence(2, 1, 0, 0), 'strict').result, 'probe_error');
});

test('classifyVisibility: missing protocol fields fail as probe_error, never absence', function () {
  const complete = evidence(0, 0, 0, 0);
  for (const field of [
    'probe_version',
    'probe_scope',
    'candidate_evidence_limit',
    'candidate_evidence_truncated',
    'candidates',
  ]) {
    const incomplete = Object.assign({}, complete);
    delete incomplete[field];
    const classified = classifyVisibility(incomplete, 'strict');
    assert.equal(classified.result, 'probe_error', field);
    assert.equal(classified.match_count, null, field);
  }
});

const JUDGMENT_CASES = [
  ['probe_error', 'visible', 'terminal', 2],
  ['invalid_selector', 'not-visible', 'terminal', 2],
  ['raw_multi_match', 'visible', 'terminal', 2],
  ['multiple_rendered', 'not-visible', 'terminal', 2],
  ['no_match', 'visible', 'retryable', 1],
  ['all_non_rendered', 'visible', 'retryable', 1],
  ['unique_rendered', 'visible', 'satisfied', 0],
  ['unique_rendered_with_retained_zero_rect', 'visible', 'satisfied', 0],
  ['no_match', 'not-visible', 'satisfied', 0],
  ['all_non_rendered', 'not-visible', 'satisfied', 0],
  ['unique_rendered', 'not-visible', 'retryable', 1],
  ['unique_rendered_with_retained_zero_rect', 'not-visible', 'retryable', 1],
];

for (const [result, assertion, expectedJudgment, expectedExit] of JUDGMENT_CASES) {
  test('judgeVisibility: ' + result + ' + ' + assertion, function () {
    const judged = judgeVisibility({ result: result }, assertion);
    assert.equal(judged.judgment, expectedJudgment);
    assert.equal(judged.exit_code, expectedExit);
    assert.equal(judged.assertion, assertion);
  });
}

function fakeElement(options) {
  const values = Object.assign({
    tag: 'DIV', role: null, testId: null, label: 'candidate', ariaHidden: null,
    inert: false, checkVisible: true, rects: [], display: 'block', visibility: 'visible',
    opacity: '1', boundingRect: { x: 0, y: 0, width: 0, height: 0 },
  }, options || {});
  return {
    tagName: values.tag,
    inert: values.inert,
    textContent: values.label,
    value: 'must-not-leak',
    innerHTML: '<secret>must-not-leak</secret>',
    getAttribute: function (name) {
      if (name === 'role') return values.role;
      if (name === 'data-testid') return values.testId;
      if (name === 'aria-label') return values.label;
      if (name === 'aria-hidden') return values.ariaHidden;
      return null;
    },
    checkVisibility: values.checkVisibilityMissing ? undefined : function () {
      if (values.checkVisibilityError) throw new Error('predicate\u0000 exploded');
      return values.checkVisible;
    },
    getClientRects: function () { return values.rects; },
    getBoundingClientRect: function () { return values.boundingRect; },
    __style: {
      display: values.display,
      visibility: values.visibility,
      opacity: values.opacity,
    },
  };
}

function runExpression(expression, candidates, queryError, selectorSink) {
  return vm.runInNewContext(expression, {
    document: {
      querySelectorAll: function (selector) {
        if (selectorSink) selectorSink.push(selector);
        if (queryError) throw queryError;
        return candidates;
      },
    },
    getComputedStyle: function (element) { return element.__style; },
  });
}

test('buildProbeExpression quotes hostile selectors as data, not executable source', function () {
  const hostile = 'main > [data-label="x\' ); globalThis.pwned = true; //\nline"]';
  const seen = [];
  const result = runExpression(buildProbeExpression(hostile), [], null, seen);

  assert.deepEqual(seen, [hostile]);
  assert.equal(result.match_count, 0);
  assert.equal(result.error, undefined);
});

test('buildProbeExpression computes uncapped aggregates before truncating candidate evidence', function () {
  const candidates = [];
  for (let index = 0; index < 11; index++) {
    candidates.push(fakeElement({
      label: 'ghost\u0000-' + index + '-long-label',
      role: index === 0 ? 'r'.repeat(200) : null,
      testId: index === 0 ? 't'.repeat(200) : null,
      ariaHidden: index === 0 ? 'a'.repeat(200) : null,
      rects: index === 0
        ? Array.from({ length: 7 }, function (_, rectIndex) {
            return { x: rectIndex, y: 0, width: 0, height: 0 };
          })
        : [{ x: index, y: 0, width: 0, height: 0 }],
    }));
  }
  candidates.push(fakeElement({
    label: 'rendered',
    rects: [{ x: 1, y: 2, width: 30, height: 40 }],
    boundingRect: { x: 1, y: 2, width: 30, height: 40 },
  }));

  const result = runExpression(buildProbeExpression('h1'), candidates);
  assert.equal(result.match_count, 12);
  assert.equal(result.nonzero_layout_visible_count, 1);
  assert.equal(result.style_visible_zero_rect_count, 11);
  assert.equal(result.non_style_visible_count, 0);
  assert.equal(result.candidate_evidence_limit, 10);
  assert.equal(result.candidate_evidence_truncated, true);
  assert.equal(result.candidates.length, 10);
  assert.equal(classifyVisibility(result, 'retained-zero-rect').result,
    'unique_rendered_with_retained_zero_rect');
  assert.equal(JSON.stringify(result).includes('must-not-leak'), false);
  assert.equal(result.candidates[0].label.includes('\u0000'), false);
  assert.equal(result.candidates[0].role.length, 120);
  assert.equal(result.candidates[0].data_testid.length, 120);
  assert.equal(result.candidates[0].aria_hidden.length, 120);
  assert.equal(result.candidates[0].client_rect_count, 7);
  assert.equal(result.candidates[0].client_rects.length, 5);
  assert.equal(result.candidates[0].client_rects_truncated, true);
});

test('buildProbeExpression retains invalid CSS as invalid_selector with null count', function () {
  const result = runExpression(buildProbeExpression('['), [], new SyntaxError('Invalid selector\n['));
  assert.equal(result.match_count, null);
  assert.equal(result.error.kind, 'invalid_selector');
  assert.equal(result.error.name, 'SyntaxError');
  assert.equal(result.error.message.includes('\n'), false);
  assert.equal(classifyVisibility(result, 'strict').result, 'invalid_selector');
});

test('buildProbeExpression fails closed when checkVisibility is missing or throws', function () {
  for (const candidate of [
    fakeElement({ checkVisibilityMissing: true }),
    fakeElement({ checkVisibilityError: true }),
  ]) {
    const result = runExpression(buildProbeExpression('div'), [candidate]);
    assert.equal(result.match_count, null);
    assert.equal(result.error.kind, 'probe_error');
    assert.equal(classifyVisibility(result, 'strict').result, 'probe_error');
  }
});

test('unwrapEvalEnvelope accepts one complete successful agent-browser envelope', function () {
  const expected = evidence(0, 0, 0, 0);
  const raw = JSON.stringify({ success: true, data: { result: expected } });
  assert.deepEqual(unwrapEvalEnvelope(raw, 0), expected);
});

test('unwrapEvalEnvelope makes nonzero transport and malformed envelopes probe_error, never no_match', function () {
  const cases = [
    [JSON.stringify({ success: true, data: { result: evidence(0, 0, 0, 0) } }), 17, 'transport'],
    ['', 0, 'empty'],
    ['{broken', 0, 'valid JSON'],
    ['{"success":true,"success":true,"data":{"result":{}}}', 0, 'duplicate JSON field'],
    [JSON.stringify({ success: false, data: { result: evidence(0, 0, 0, 0) } }), 0, 'successful'],
    [JSON.stringify({ success: true, data: {} }), 0, 'data.result'],
    [JSON.stringify({ success: true, data: { result: false } }), 0, 'object'],
  ];
  for (const [raw, transportExit, message] of cases) {
    const result = unwrapEvalEnvelope(raw, transportExit);
    assert.equal(result.result, 'probe_error');
    assert.equal(result.match_count, null);
    assert.match(result.error.message, new RegExp(message));
  }
});

function runCli(args, input) {
  return spawnSync(process.execPath, [CLI_PATH].concat(args), {
    encoding: 'utf8',
    input: input || '',
  });
}

test('visibility CLI expression preserves hostile selector quoting through stdout', function () {
  const hostile = 'button[data-name="quote\'\\n$()"]';
  const result = runCli(['expression', '--selector', hostile]);
  assert.equal(result.status, 0, result.stderr);
  const seen = [];
  const probeResult = runExpression(result.stdout.trim(), [], null, seen);
  assert.deepEqual(seen, [hostile]);
  assert.equal(probeResult.match_count, 0);
});

const CLI_JUDGMENTS = [
  ['no-match negative satisfied', evidence(0, 0, 0, 0), 'strict', 'not-visible', 0, 'satisfied'],
  ['no-match positive retryable', evidence(0, 0, 0, 0), 'strict', 'visible', 1, 'retryable'],
  ['singleton positive satisfied', evidence(1, 1, 0, 0), 'strict', 'visible', 0, 'satisfied'],
  ['strict duplicate terminal', evidence(2, 1, 1, 0), 'strict', 'visible', 2, 'terminal'],
];

for (const [name, probeEvidence, policy, assertion, expectedExit, expectedJudgment] of CLI_JUDGMENTS) {
  test('visibility CLI judge: ' + name, function () {
    const envelope = JSON.stringify({ success: true, data: { result: probeEvidence } });
    const result = runCli([
      'judge', '--policy', policy, '--assert', assertion, '--transport-exit', '0',
    ], envelope);
    assert.equal(result.status, expectedExit, result.stderr);
    const output = JSON.parse(result.stdout);
    assert.equal(output.judgment, expectedJudgment);
    assert.equal(output.exit_code, expectedExit);
  });
}

test('visibility CLI judge returns terminal JSON for invalid policy, transport, and envelope', function () {
  const cases = [
    [['judge', '--policy', 'any-visible', '--assert', 'visible', '--transport-exit', '0'],
      JSON.stringify({ success: true, data: { result: evidence(0, 0, 0, 0) } })],
    [['judge', '--policy', 'strict', '--assert', 'not-visible', '--transport-exit', '9'], ''],
    [['judge', '--policy', 'strict', '--assert', 'not-visible', '--transport-exit', '0'], '{bad'],
  ];
  for (const [args, input] of cases) {
    const result = runCli(args, input);
    assert.equal(result.status, 2, result.stderr);
    const output = JSON.parse(result.stdout);
    assert.equal(output.result, 'probe_error');
    assert.equal(output.match_count, null);
    assert.equal(output.judgment, 'terminal');
  }
});

test('renderStandaloneSupport emits the same dependency-free probe and classifier API', function () {
  const support = vm.runInNewContext(renderStandaloneSupport(), { Buffer: Buffer });
  assert.deepEqual(Object.keys(support).sort(), [
    'buildProbeExpression',
    'classifyVisibility',
    'judgeVisibility',
    'unwrapEvalEnvelope',
  ]);

  const vector = evidence(2, 1, 1, 0);
  assert.equal(support.classifyVisibility(vector, 'strict').result,
    classifyVisibility(vector, 'strict').result);
  assert.equal(support.buildProbeExpression('button[data-x="\'quoted\'"]'),
    buildProbeExpression('button[data-x="\'quoted\'"]'));
});
