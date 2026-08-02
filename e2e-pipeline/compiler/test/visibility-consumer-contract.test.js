'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const yaml = require('js-yaml');

const { compile } = require('../compiler.js');
const { generate } = require('../codegen.js');

const PIPELINE = path.join(__dirname, '..', '..');
const RUNTIME_SHIM = path.join(__dirname, 'fixtures', 'browser-runtime-shim.js');
const CONSUMERS = [
  ['mapper', 'agents/e2e-mapper.md'],
  ['runner', 'agents/e2e-test-runner.md'],
  ['verifier', 'agents/e2e-flow-verifier.md'],
  ['walkthrough', 'skills/e2e-walkthrough/reference.md'],
];

function read(relativePath) {
  return fs.readFileSync(path.join(PIPELINE, relativePath), 'utf8');
}

function envelope(matchCount, rendered, zeroRect, nonStyle) {
  return JSON.stringify({
    success: true,
    data: {
      result: {
        probe_version: 1,
        probe_scope: 'current-document',
        match_count: matchCount,
        nonzero_layout_visible_count: rendered,
        style_visible_zero_rect_count: zeroRect,
        non_style_visible_count: nonStyle,
        candidate_evidence_limit: 10,
        candidate_evidence_truncated: false,
        candidates: [],
      },
    },
  });
}

const MATRIX = [
  ['no_match', envelope(0, 0, 0, 0), 'strict', 'visible', 1],
  ['all_non_rendered', envelope(2, 0, 1, 1), 'strict', 'visible', 1],
  ['unique_rendered', envelope(1, 1, 0, 0), 'strict', 'visible', 0],
  ['raw_multi_match', envelope(2, 1, 1, 0), 'strict', 'visible', 2],
  [
    'unique_rendered_with_retained_zero_rect',
    envelope(2, 1, 1, 0),
    'retained-zero-rect',
    'visible',
    0,
  ],
  ['raw_multi_match', envelope(2, 1, 0, 1), 'retained-zero-rect', 'visible', 2],
  ['multiple_rendered', envelope(2, 2, 0, 0), 'strict', 'visible', 2],
  [
    'invalid_selector',
    JSON.stringify({
      success: true,
      data: {
        result: {
          probe_version: 1,
          probe_scope: 'current-document',
          match_count: null,
          nonzero_layout_visible_count: null,
          style_visible_zero_rect_count: null,
          non_style_visible_count: null,
          candidate_evidence_limit: 10,
          candidate_evidence_truncated: false,
          candidates: [],
          error: { kind: 'invalid_selector', name: 'SyntaxError', message: 'invalid CSS' },
        },
      },
    }),
    'strict',
    'not-visible',
    2,
  ],
];

function consumerRecipe(relativePath) {
  const blocks = Array.from(read(relativePath).matchAll(/```bash\n([\s\S]*?)```/g), function (match) {
    return match[1];
  });
  const recipe = blocks.find(function (block) {
    return block.includes('e2e-visibility-probe.js') && block.includes('judge --policy');
  });
  assert.ok(recipe, relativePath + ': executable visibility recipe is missing');
  return recipe.replaceAll('{{browser_command}}', 'browser_command')
    .replaceAll('<browser_command>', 'browser_command');
}

function exerciseConsumer(relativePath, raw, policy, assertion) {
  const recipe = consumerRecipe(relativePath);
  const script = [
    'set -u',
    'browser_command() {',
    '  if [ "$1" != "eval" ]; then return 71; fi',
    '  printf \'%s\\n\' "$VISIBILITY_ENVELOPE"',
    '}',
    'effective_selector="#fixture"',
    'visibility_policy="' + policy + '"',
    'assertion="' + assertion + '"',
    recipe,
    'printf \'%s\\n\' "$judged"',
    'printf \'selector=%s\\npolicy=%s\\nattempts=%s\\nelapsed=%s\\n\' "$effective_selector" "$visibility_policy" "$attempts" "$elapsed_seconds"',
    'exit "$judge_exit"',
  ].join('\n');
  const result = childProcess.spawnSync('/bin/bash', ['-c', script], {
    encoding: 'utf8',
    env: Object.assign({}, process.env, {
      CLAUDE_PLUGIN_ROOT: PIPELINE,
      VISIBILITY_ENVELOPE: raw,
    }),
  });
  const lines = result.stdout.trim().split('\n');
  return { result: result, judged: lines[0] ? JSON.parse(lines[0]) : null, output: lines.slice(1) };
}

test('mapper, runner, verifier, and walkthrough execute their own shared-protocol recipes', function () {
  for (const [name, relativePath] of CONSUMERS) {
    const vectors = name === 'mapper'
      ? MATRIX.filter(function (entry) { return entry[2] === 'strict' && entry[3] === 'visible'; })
      : MATRIX;
    for (const [expectedResult, raw, policy, assertion, expectedExit] of vectors) {
      const actual = exerciseConsumer(relativePath, raw, policy, assertion);
      assert.equal(actual.result.status, expectedExit,
        name + ': ' + expectedResult + ': ' + actual.result.stdout + actual.result.stderr);
      assert.equal(actual.judged.result, expectedResult, name + ': ' + expectedResult);
      assert.equal(actual.judged.match_count,
        expectedResult === 'invalid_selector' ? null : JSON.parse(raw).data.result.match_count);
      assert.ok(actual.output.includes('selector=#fixture'), name);
      assert.ok(actual.output.some(function (line) { return line.startsWith('attempts='); }), name);
      assert.ok(actual.output.some(function (line) { return line.startsWith('elapsed='); }), name);
    }
  }
});

function generatedVisibilityScript(cssSelector, policy) {
  return generate({
    name: 'visibility-report-fixture',
    steps: [{
      id: 'mapped-visibility',
      action: 'Wait 0',
      type: 'wait',
      operands: { seconds: 0 },
      expects: [{
        type: 'element-visible',
        raw: 'heading visible on home',
        elementName: 'heading',
        selector: 'role=heading[name="Heading"]',
        cssSelector: cssSelector,
        visibilityPolicy: policy,
      }],
    }],
  }, 'visibility-report-fixture');
}

test('compiled metrics retain final bounded visibility report fields', function (t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'visibility-report-'));
  t.after(function () { fs.rmSync(root, { recursive: true, force: true }); });
  const browser = path.join(root, 'agent-browser');
  const sleep = path.join(root, 'sleep');
  const metrics = path.join(root, 'metrics.json');
  fs.writeFileSync(browser, [
    '#!/usr/bin/env bash',
    'case " $* " in *" close "*) exit 0 ;; esac',
    'printf \'%s\\n\' "${VISIBILITY_ENVELOPE:?}"',
  ].join('\n'), { mode: 0o755 });
  fs.writeFileSync(sleep, '#!/usr/bin/env bash\nexit 0\n', { mode: 0o755 });
  const result = childProcess.spawnSync('/bin/bash', [
    '-c',
    generatedVisibilityScript('#heading', 'strict'),
    '--',
    '--metrics-output',
    metrics,
  ], {
    encoding: 'utf8',
    env: Object.assign({}, process.env, {
      PATH: root + path.delimiter + process.env.PATH,
      E2E_BROWSER_RUNTIME: RUNTIME_SHIM,
      VISIBILITY_ENVELOPE: envelope(1, 1, 0, 0),
      WAIT_TIMEOUT: '1',
    }),
  });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  const report = JSON.parse(fs.readFileSync(metrics, 'utf8'));
  assert.equal(report.visibility_results.length, 1);
  assert.equal(report.visibility_results[0].result_class, 'unique_rendered');
  assert.equal(report.visibility_results[0].effective_selector, '#heading');
  assert.equal(report.visibility_results[0].visibility_policy, 'strict');
  assert.equal(report.visibility_results[0].match_count, 1);
  assert.equal(report.visibility_results[0].attempts, 1);
  assert.equal(typeof report.visibility_results[0].elapsed_seconds, 'number');
  assert.deepEqual(report.visibility_results[0].candidate_evidence, []);
});

function documentationExamples(source) {
  const section = source.slice(source.indexOf('## Deterministic mapped visibility'));
  const blocks = Array.from(section.matchAll(/```yaml\n([\s\S]*?)```/g), function (match) {
    return match[1];
  });
  return {
    mapping: blocks.find(function (block) { return block.includes('# file: mappings/visibility-example.yaml'); }),
    flow: blocks.find(function (block) { return block.includes('# file: flows/visibility-example.yaml'); }),
  };
}

test('published deterministic visibility YAML compiles and executes through generated support', async function (t) {
  const examples = documentationExamples(read('docs/writing-tests.md'));
  assert.ok(examples.mapping, 'published mapping example is missing');
  assert.ok(examples.flow, 'published flow example is missing');
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'visibility-doc-example-'));
  t.after(function () { fs.rmSync(root, { recursive: true, force: true }); });
  const mappings = path.join(root, 'mappings');
  const output = path.join(root, 'compiled');
  fs.mkdirSync(mappings);
  const mappingPath = path.join(mappings, 'visibility-example.yaml');
  const flowPath = path.join(root, 'visibility-example.yaml');
  fs.writeFileSync(mappingPath, examples.mapping, 'utf8');
  fs.writeFileSync(flowPath, examples.flow, 'utf8');
  assert.equal(yaml.load(examples.mapping).pages.home.elements.page_heading.visibility_policy, 'retained-zero-rect');
  const compiled = await compile(flowPath, mappings, output, {});
  assert.equal(compiled.success, true, compiled.errors?.join('\n'));
  const browser = path.join(root, 'agent-browser');
  const sleep = path.join(root, 'sleep');
  fs.writeFileSync(browser, [
    '#!/usr/bin/env bash',
    'case " $* " in *" close "*) exit 0 ;; esac',
    'printf \'%s\\n\' "${VISIBILITY_ENVELOPE:?}"',
  ].join('\n'), { mode: 0o755 });
  fs.writeFileSync(sleep, '#!/usr/bin/env bash\nexit 0\n', { mode: 0o755 });
  const executed = childProcess.spawnSync('/bin/bash', [compiled.outputPath], {
    encoding: 'utf8',
    env: Object.assign({}, process.env, {
      PATH: root + path.delimiter + process.env.PATH,
      E2E_BROWSER_RUNTIME: RUNTIME_SHIM,
      VISIBILITY_ENVELOPE: envelope(2, 1, 1, 0),
      WAIT_TIMEOUT: '1',
    }),
  });
  assert.equal(executed.status, 0, executed.stdout + executed.stderr);
});
