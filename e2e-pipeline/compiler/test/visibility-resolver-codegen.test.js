// biome-ignore-all lint/suspicious/noTemplateCurlyInString: mapping and shell fixtures intentionally preserve literal ${...} placeholders.
'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { resolve, resolveMultiSite } = require('../resolver.js');
const { generate } = require('../codegen.js');
const { compile } = require('../compiler.js');

const BROWSER_RUNTIME_SHIM = path.join(__dirname, 'fixtures', 'browser-runtime-shim.js');

function mapping(elements) {
  return {
    version: 2,
    app: 'visibility-fixture',
    base_url: 'https://example.test',
    pages: {
      home: {
        url_pattern: '/',
        elements: elements,
      },
    },
  };
}

function flowWithExpects(expects, extra) {
  return Object.assign({
    name: 'visibility-fixture',
    steps: [{
      id: 'verify-visibility',
      type: 'snapshot',
      action: 'Take snapshot',
      expect: expects,
    }],
  }, extra || {});
}

test('resolver carries selector, effective DOM selector, and policy through mapped visibility forms', function () {
  const fixture = mapping({
    legacy: {
      selector: 'role=heading[name="Legacy"]',
      css_selector: '[data-testid="legacy"]',
      visibility_policy: 'retained-zero-rect',
    },
    positive: { selector: '.positive' },
    negative: { selector: '#negative' },
    enabled_control: { selector: 'button.enabled' },
    disabled_control: { selector: 'button.disabled' },
    alternate: {
      selector: 'text=Alternate',
      css_selector: '[data-testid="alternate"]',
    },
  });
  const result = resolve(flowWithExpects([
    'legacy is visible',
    'positive visible on home',
    'negative not visible on home',
    'enabled_control enabled on home',
    'disabled_control disabled on home',
    'positive visible or alternate visible',
  ]), fixture, { mappingPath: '/fixtures/visibility-map.yaml' });

  assert.deepEqual(result.errors, [], result.errors.join('\n'));
  const expects = result.resolved.steps[0].expects;
  assert.deepEqual(
    expects.map(function (expect) { return expect.type; }),
    ['active', 'element-visible', 'element-not-visible', 'element-enabled', 'element-disabled', 'or-visible']
  );
  assert.deepEqual(expects[0], {
    type: 'active',
    raw: 'legacy is visible',
    elementName: 'legacy',
    selector: 'role=heading[name="Legacy"]',
    cssSelector: '[data-testid="legacy"]',
    visibilityPolicy: 'retained-zero-rect',
  });
  assert.equal(expects[1].cssSelector, '.positive');
  assert.equal(expects[1].visibilityPolicy, 'strict');
  assert.equal(expects[2].cssSelector, '#negative');
  assert.equal(expects[3].cssSelector, 'button.enabled');
  assert.equal(expects[4].cssSelector, 'button.disabled');
  assert.deepEqual(expects[5].elements.map(function (element) {
    return [element.elementName, element.selector, element.cssSelector, element.visibilityPolicy];
  }), [
    ['positive', '.positive', '.positive', 'strict'],
    ['alternate', 'text=Alternate', '[data-testid="alternate"]', 'strict'],
  ]);
});

test('resolver substitutes parameterized selector and css_selector while retaining template identity', function () {
  const fixture = mapping({
    branch_item: {
      selector: 'role=button[name="${branchName}"]',
      css_selector: '[data-branch="${branchName}"]',
      visibility_policy: 'retained-zero-rect',
    },
  });
  const result = resolve(
    flowWithExpects(['branch_item(branchName=feature/o\'hare) visible on home']),
    fixture,
    { mappingPath: '/fixtures/parameterized.yaml' }
  );

  assert.deepEqual(result.errors, [], result.errors.join('\n'));
  const expect = result.resolved.steps[0].expects[0];
  assert.equal(expect.elementName, 'branch_item');
  assert.equal(expect.selector, 'role=button[name="${branchName}"]');
  assert.equal(expect.selectorTemplate, 'role=button[name="${branchName}"]');
  assert.equal(expect.cssSelectorTemplate, '[data-branch="${branchName}"]');
  assert.equal(expect.effectiveSelector, 'role=button[name="feature/o\'hare"]');
  assert.equal(expect.cssSelector, '[data-branch="feature/o\'hare"]');
  assert.equal(expect.visibilityPolicy, 'retained-zero-rect');
});

test('built-in visibility owns literal CSS and strict policy', function () {
  const result = resolve(flowWithExpects(['dialog not visible']), mapping({}), {
    mappingPath: '/fixtures/empty.yaml',
  });

  assert.deepEqual(result.errors, [], result.errors.join('\n'));
  assert.deepEqual(result.resolved.steps[0].expects[0], {
    type: 'element-not-visible',
    raw: 'dialog not visible',
    elementName: 'dialog',
    selector: 'role=dialog',
    cssSelector: 'dialog,[role="dialog"]',
    visibilityPolicy: 'strict',
  });
});

test('resolved non-CSS visibility without css_selector fails with mapping identity and remediation', function () {
  const fixture = mapping({
    missing_dom_identity: { selector: 'role=heading[name="Missing CSS"]' },
  });
  const result = resolve(flowWithExpects(['missing_dom_identity visible on home']), fixture, {
    mappingPath: '/fixtures/missing-css.yaml',
  });

  assert.equal(result.resolved.steps[0].expects, undefined);
  assert.equal(result.errors.length, 1);
  assert.match(result.errors[0], /\/fixtures\/missing-css\.yaml/);
  assert.match(result.errors[0], /home\.missing_dom_identity/);
  assert.match(result.errors[0], /role=heading/);
  assert.match(result.errors[0], /css_selector/);
  assert.match(result.errors[0], /literal CSS/);
});

test('multi-site resolver carries DOM selector and policy into the named session', function () {
  const siteMapping = mapping({
    heading: {
      selector: 'role=heading[name="Office"]',
      css_selector: 'main > h1',
      visibility_policy: 'retained-zero-rect',
    },
  });
  const result = resolveMultiSite({
    name: 'cross-site-visibility',
    steps: [{
      id: 'office-heading',
      site: 'office',
      type: 'snapshot',
      action: 'Take snapshot',
      expect: ['heading visible on home'],
    }],
  }, {
    office: { mappingName: 'office-map', mapping: siteMapping },
  }, { mappingDir: '/fixtures' });

  assert.deepEqual(result.errors, [], result.errors.join('\n'));
  assert.equal(result.resolved.steps[0].session, 'office');
  assert.deepEqual(result.resolved.steps[0].expects[0], {
    type: 'element-visible',
    raw: 'heading visible on home',
    elementName: 'heading',
    selector: 'role=heading[name="Office"]',
    cssSelector: 'main > h1',
    visibilityPolicy: 'retained-zero-rect',
  });
});

function mappedExpect(type, name, cssSelector, policy) {
  return {
    type: type,
    raw: name + ' visible',
    elementName: name,
    selector: 'role=button[name="' + name + '"]',
    cssSelector: cssSelector,
    visibilityPolicy: policy || 'strict',
  };
}

function generatedVisibilityFlow(expects, session) {
  return generate({
    name: 'generated-visibility',
    description: 'Generated visibility probe fixture',
    steps: [{
      id: 'visibility-step',
      action: 'Wait 0',
      type: 'wait',
      operands: { seconds: 0 },
      session: session || undefined,
      expects: expects,
    }],
  }, 'generated-visibility');
}

test('codegen emits shared standalone support for mapped positive and negative visibility only', function () {
  const hostile = '[data-label="quote\' $() newline\\n"]';
  const script = generatedVisibilityFlow([
    mappedExpect('element-visible', 'positive', hostile, 'retained-zero-rect'),
    mappedExpect('element-not-visible', 'negative', '#negative', 'strict'),
    { type: 'text-visible', raw: "text 'literal' on page", text: 'literal' },
  ], 'office');

  assert.match(script, /buildProbeExpression/);
  assert.match(script, /_poll_visibility/);
  assert.match(script, /retained-zero-rect/);
  assert.match(script, /--session "?\$?_session/);
  const step = script.slice(script.indexOf('[1/1] visibility-step'));
  assert.doesNotMatch(step, /_poll_snapshot_contains[^\n]*positive/);
  assert.doesNotMatch(step, /_poll_visible[^\n]*positive/);
  assert.match(step, /_poll_visibility[^\n]*visible/);
  assert.match(step, /_poll_visibility[^\n]*not-visible/);
  assert.match(step, /_capture_snapshot/);
});

test('codegen OR probes both operands per attempt and passes both selectors and policies', function () {
  const script = generatedVisibilityFlow([{
    type: 'or-visible',
    raw: 'first visible or second visible',
    elements: [
      mappedExpect(undefined, 'first', '#first', 'strict'),
      mappedExpect(undefined, 'second', '#second', 'retained-zero-rect'),
    ],
  }]);

  const step = script.slice(script.indexOf('[1/1] visibility-step'));
  assert.match(step, /_poll_or_visibility/);
  assert.match(step, /#first/);
  assert.match(step, /#second/);
  assert.match(step, /strict/);
  assert.match(step, /retained-zero-rect/);
  assert.doesNotMatch(step, /_poll_or_visible /);
});

function evidence(matchCount, rendered, zeroRect, nonStyle) {
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

function runGenerated(expects, env, session) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'visibility-codegen-'));
  const browser = path.join(dir, 'agent-browser');
  const log = path.join(dir, 'browser.log');
  const sleep = path.join(dir, 'sleep');
  const browserSource = [
    '#!/usr/bin/env bash',
    'printf \'%s\\n\' "$*" >> "${VISIBILITY_BROWSER_LOG:?}"',
    'case " $* " in *" close "*|" close ") exit 0 ;; esac',
    'case " $* " in *" is enabled "*) printf \'%s\\n\' "${ENABLED_OUTPUT:-true}"; exit "${ENABLED_STATUS:-0}" ;; esac',
    'case "$*" in',
    '  *"#first"*) printf \'%s\\n\' "${FIRST_ENVELOPE:-${VISIBILITY_ENVELOPE:-}}"; exit "${FIRST_STATUS:-${VISIBILITY_STATUS:-0}}" ;;',
    '  *"#second"*) printf \'%s\\n\' "${SECOND_ENVELOPE:-${VISIBILITY_ENVELOPE:-}}"; exit "${SECOND_STATUS:-${VISIBILITY_STATUS:-0}}" ;;',
    '  *) printf \'%s\\n\' "${VISIBILITY_ENVELOPE:-}"; exit "${VISIBILITY_STATUS:-0}" ;;',
    'esac',
  ].join('\n');
  fs.writeFileSync(browser, browserSource, { mode: 0o755 });
  fs.writeFileSync(sleep, '#!/usr/bin/env bash\nexit 0\n', { mode: 0o755 });
  try {
    const result = childProcess.spawnSync('/bin/bash', ['-c', generatedVisibilityFlow(expects, session)], {
      encoding: 'utf8',
      env: Object.assign({}, process.env, env || {}, {
        PATH: dir + path.delimiter + process.env.PATH,
        E2E_BROWSER_RUNTIME: BROWSER_RUNTIME_SHIM,
        VISIBILITY_BROWSER_LOG: log,
        WAIT_TIMEOUT: '1',
      }),
    });
    result.browserLog = fs.existsSync(log) ? fs.readFileSync(log, 'utf8') : '';
    return result;
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

test('generated positive and negative polling execute the shared judgment protocol', function () {
  const positive = runGenerated([
    mappedExpect('element-visible', 'positive', '#positive', 'strict'),
  ], { VISIBILITY_ENVELOPE: evidence(1, 1, 0, 0) });
  assert.equal(positive.status, 0, positive.stdout + positive.stderr);

  const negative = runGenerated([
    mappedExpect('element-not-visible', 'negative', '#negative', 'strict'),
  ], { VISIBILITY_ENVELOPE: evidence(0, 0, 0, 0) });
  assert.equal(negative.status, 0, negative.stdout + negative.stderr);
});

test('generated terminal cardinality failure stops after one positive attempt', function () {
  const result = runGenerated([
    mappedExpect('element-visible', 'positive', '#positive', 'strict'),
  ], { VISIBILITY_ENVELOPE: evidence(2, 1, 1, 0) });

  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.equal(result.browserLog.split('\n').filter(function (line) { return line.includes('eval '); }).length, 1);
  assert.match(result.stdout, /visibility probe failed/);
  assert.doesNotMatch(result.stdout, /after 1s/);
});

test('generated OR never masks a terminal second operand behind a satisfied first operand', function () {
  const result = runGenerated([{
    type: 'or-visible',
    raw: 'first visible or second visible',
    elements: [
      mappedExpect(undefined, 'first', '#first', 'strict'),
      mappedExpect(undefined, 'second', '#second', 'strict'),
    ],
  }], {
    FIRST_ENVELOPE: evidence(1, 1, 0, 0),
    SECOND_ENVELOPE: evidence(2, 2, 0, 0),
  });

  assert.equal(result.status, 1, result.stdout + result.stderr);
  const evalLines = result.browserLog.split('\n').filter(function (line) { return line.includes('eval '); });
  assert.equal(evalLines.length, 2, result.browserLog);
  assert.match(result.browserLog, /"selector":"#first"/);
  assert.match(result.browserLog, /"selector":"#second"/);
  assert.match(result.stdout, /visibility probe failed/);
});

test('generated visibility keeps named sessions and hostile selectors as literal data', function () {
  const marker = path.join(os.tmpdir(), 'visibility-codegen-marker-' + process.pid);
  fs.rmSync(marker, { force: true });
  const hostile = '[data-name="\'$(touch ' + marker + ')\'"]';
  const result = runGenerated([
    mappedExpect('element-visible', 'hostile', hostile, 'strict'),
  ], { VISIBILITY_ENVELOPE: evidence(1, 1, 0, 0) }, 'office');

  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.equal(fs.existsSync(marker), false);
  assert.match(result.browserLog, /--session office eval/);
  assert.match(result.browserLog, /data-name/);
});

test('enabled previsibility preserves terminal cardinality and never reaches the state probe', function () {
  const result = runGenerated([{
    type: 'element-enabled',
    raw: 'control enabled on home',
    elementName: 'control',
    selector: 'role=button[name="Control"]',
    cssSelector: '#control',
    visibilityPolicy: 'strict',
  }], { VISIBILITY_ENVELOPE: evidence(2, 1, 1, 0), ENABLED_OUTPUT: 'true' });

  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.equal(result.browserLog.split('\n').filter(function (line) { return line.includes('eval '); }).length, 1);
  assert.doesNotMatch(result.browserLog, /is enabled/);
  assert.match(result.stdout, /visibility\/state probe failed/);
});

test('compiler dry-run refuses non-CSS mapped visibility before producing a browser script', async function (t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'visibility-compile-'));
  t.after(function () { fs.rmSync(dir, { recursive: true, force: true }); });
  const mappings = path.join(dir, 'mappings');
  const output = path.join(dir, 'compiled');
  fs.mkdirSync(mappings);
  const mappingPath = path.join(mappings, 'missing-css.yaml');
  fs.writeFileSync(mappingPath, JSON.stringify(mapping({
    heading: { selector: 'role=heading[name="Missing CSS"]' },
  })), 'utf8');
  const flowPath = path.join(dir, 'flow.yaml');
  fs.writeFileSync(flowPath, JSON.stringify({
    name: 'missing-css-compile',
    mapping: 'missing-css',
    steps: [{
      id: 'verify-heading',
      type: 'snapshot',
      action: 'Take snapshot',
      expect: ['heading visible on home'],
    }],
  }), 'utf8');

  const result = await compile(flowPath, mappings, output, { dryRun: true });
  assert.equal(result.success, false);
  assert.equal(fs.existsSync(path.join(output, 'missing-css-compile.sh')), false);
  assert.match(result.errors[0], new RegExp(mappingPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.match(result.errors[0], /home\.heading/);
  assert.match(result.errors[0], /css_selector/);
});

test('generated support and CLI derive classifier behavior from the same perturbed source', function (t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'visibility-drift-'));
  t.after(function () { fs.rmSync(dir, { recursive: true, force: true }); });
  const libDir = path.join(dir, 'compiler', 'lib');
  const binDir = path.join(dir, 'bin');
  fs.mkdirSync(libDir, { recursive: true });
  fs.mkdirSync(binDir, { recursive: true });
  const sourcePath = path.join(__dirname, '..', 'lib', 'visibility-probe.js');
  const source = fs.readFileSync(sourcePath, 'utf8');
  const perturbed = source.replace(
    "result = 'raw_multi_match';",
    "result = 'raw_multi_match_perturbed';"
  );
  assert.notEqual(perturbed, source, 'drift perturbation must alter the classifier source');
  const driftModulePath = path.join(libDir, 'visibility-probe.js');
  fs.writeFileSync(driftModulePath, perturbed, 'utf8');
  const cliSource = fs.readFileSync(
    path.join(__dirname, '..', '..', 'bin', 'e2e-visibility-probe.js'),
    'utf8'
  );
  const driftCli = path.join(binDir, 'e2e-visibility-probe.js');
  fs.writeFileSync(driftCli, cliSource, { mode: 0o755 });

  const driftModule = require(driftModulePath);
  const vector = JSON.parse(evidence(2, 1, 1, 0));
  const generatedApi = require('node:vm').runInNewContext(
    driftModule.renderStandaloneSupport(),
    { Buffer: Buffer }
  );
  assert.equal(
    generatedApi.classifyVisibility(vector.data.result, 'strict').result,
    'raw_multi_match_perturbed'
  );
  const cli = childProcess.spawnSync(process.execPath, [
    driftCli,
    'judge', '--policy', 'strict', '--assert', 'visible', '--transport-exit', '0',
  ], { encoding: 'utf8', input: JSON.stringify(vector) });
  assert.equal(cli.status, 2, cli.stderr);
  assert.equal(JSON.parse(cli.stdout).result, 'raw_multi_match_perturbed');
});
