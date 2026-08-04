'use strict';

/**
 * selector-gate.test.js — the compile-time selector gate (#88), driven through the real
 * CLI rather than through compile() directly.
 *
 * The defect this covers is a wiring defect: `scripts/lint-mapping.sh` knew the grammar
 * and nothing on the compiled path called it, so a mapping carrying a banned form
 * compiled green and failed only once a browser was running. A unit test asserting a
 * validator returned false would not have caught that, so these run `bin/e2e-compile.js`
 * as a subprocess and assert on exit code and on whether the `.sh` a browser would run
 * exists.
 *
 * Severity is a function of scope, per the captain's 2026-08-01 ruling:
 *   blocking  selectors the flow resolves
 *   warning   every other banned selector in the loaded mapping file
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync, spawnSync } = require('node:child_process');

const PLUGIN_ROOT = path.join(__dirname, '..', '..');
const CLI = path.join(PLUGIN_ROOT, 'bin', 'e2e-compile.js');
const FIXTURES = path.join(__dirname, 'fixtures');
const GATE_FLOW = path.join(FIXTURES, 'selector-gate-flow.yaml');

/**
 * Run the compile CLI as a subprocess. Never throws — the exit code is the assertion.
 *
 * spawnSync, not execFileSync: the latter returns only stdout, so a successful run's
 * stderr would come back empty and every "it warned about X" assertion on a passing
 * compile would be asserting against ''. That is a check that cannot fail.
 */
function runCompile(args) {
  const res = spawnSync('node', [CLI].concat(args), { encoding: 'utf8' });
  return { status: res.status, stdout: String(res.stdout || ''), stderr: String(res.stderr || '') };
}

function tmpdir(label) {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'selector-gate-' + label + '-'));
}

/** A mappings dir holding one mapping built from `elements`, plus the shared flow. */
function mappingDirWith(elements) {
  const dir = tmpdir('map');
  const lines = ['version: 2', 'app: gate-app', 'base_url: "http://localhost:3000"', 'pages:', '  login:', '    url_pattern: "/login"', '    elements:'];
  for (const [name, selector] of Object.entries(elements)) {
    lines.push('      ' + name + ':');
    lines.push("        selector: '" + selector + "'");
  }
  fs.writeFileSync(path.join(dir, 'selector-gate-mapping.yaml'), lines.join('\n') + '\n', 'utf8');
  return dir;
}

const CLEAN_ELEMENTS = {
  email_input: '[data-testid="email"]',
  submit_button: 'role=switch >> nth=1',   // resolved by the flow -> blocking
  unused_toggle: 'role=switch >> nth=1',   // same string, unresolved -> warning
};

const NO_BASELINE = path.join(os.tmpdir(), 'selector-gate-absent-baseline.tsv');

describe('AC-1 — a banned class on a RESOLVED element blocks; on an unresolved one it warns', function () {
  test('compile exits 1, writes no artifact, and names the offending element', function () {
    const out = tmpdir('out');
    const res = runCompile([GATE_FLOW, '--mappings-dir', FIXTURES, '--output-dir', out, '--selector-baseline', NO_BASELINE]);

    assert.equal(res.status, 1);
    assert.deepEqual(fs.readdirSync(out), [], 'a .sh was written despite the gate blocking');

    // The five diagnostic fields #88 asks for: mapping file, element, class, selector,
    // and replacement guidance.
    assert.match(res.stderr, /selector-gate-mapping\.yaml/);
    assert.match(res.stderr, /login\.submit_button/);
    assert.match(res.stderr, />>nth/);
    assert.match(res.stderr, /role=switch >> nth=1/);
    // Guidance is `css_selector:` since #124 ruled the ban stays whole and the
    // migration is the field mapped visibility already requires.
    assert.match(res.stderr, /css_selector/);
  });

  test('the unresolved sibling is reported in the SAME run, as a non-blocking warning', function () {
    // One command proving both severities. The sibling carries the IDENTICAL selector
    // string to the blocking element — the case a (class, selector) channel split
    // swallows, and the reason the split is exact subtraction on element identity.
    const out = tmpdir('out');
    const res = runCompile([GATE_FLOW, '--mappings-dir', FIXTURES, '--output-dir', out, '--selector-baseline', NO_BASELINE]);
    const warnings = res.stderr.split('\n').filter(function (l) { return l.startsWith('WARNING:'); });
    assert.equal(warnings.length, 1);
    assert.match(warnings[0], /login\.unused_toggle/);
    assert.match(warnings[0], /no step in this flow resolves it/);
    // The two channels name different elements — neither is double-counted, neither lost.
    assert.doesNotMatch(warnings[0], /submit_button/);
    const errors = res.stderr.split('\n').filter(function (l) { return l.startsWith('ERROR:'); });
    assert.ok(errors.every(function (l) { return !l.includes('unused_toggle'); }));
  });

  test('the diagnostic carries a real line number, resolved from the element', function () {
    // The element traversal has no line numbers of its own; they are recovered per finding
    // and are null-rather-than-guessed when they cannot be. Pin the actual lines so a
    // lookup that silently drifted to the wrong element would show up here.
    const out = tmpdir('out');
    const res = runCompile([GATE_FLOW, '--mappings-dir', FIXTURES, '--output-dir', out, '--selector-baseline', NO_BASELINE]);
    assert.match(res.stderr, /selector-gate-mapping\.yaml:20: login\.submit_button/);
    assert.match(res.stderr, /selector-gate-mapping\.yaml:23: login\.unused_toggle/);
  });

  test('--dry-run blocks identically — validation is not a write-time-only check', function () {
    const out = tmpdir('out');
    const res = runCompile([GATE_FLOW, '--mappings-dir', FIXTURES, '--output-dir', out, '--dry-run', '--selector-baseline', NO_BASELINE]);
    assert.equal(res.status, 1);
    assert.deepEqual(fs.readdirSync(out), []);
  });

  test('--json carries the class id and the element, not just a message string', function () {
    const out = tmpdir('out');
    const res = runCompile([GATE_FLOW, '--mappings-dir', FIXTURES, '--output-dir', out, '--json', '--selector-baseline', NO_BASELINE]);
    assert.equal(res.status, 1);
    const doc = JSON.parse(res.stdout);
    assert.equal(doc.ok, false);
    const detail = doc.errors.find(function (e) { return e.selector_class === '>>nth'; });
    assert.ok(detail, '--json errors[] carried no selector_class');
    assert.equal(detail.element, 'submit_button');
    assert.equal(detail.page, 'login');
    assert.equal(detail.mapping_file, 'selector-gate-mapping.yaml');
  });

  test('a mapping with no banned selector compiles and writes its artifact', function () {
    // The negative control. Without it, a gate that rejected everything would pass every
    // assertion above.
    const dir = mappingDirWith({ email_input: '[data-testid="email"]', submit_button: '[data-testid="submit"]' });
    fs.copyFileSync(GATE_FLOW, path.join(dir, 'flow.yaml'));
    const out = tmpdir('out');
    const res = runCompile([path.join(dir, 'flow.yaml'), '--mappings-dir', dir, '--output-dir', out, '--selector-baseline', NO_BASELINE]);
    assert.equal(res.status, 0, res.stderr);
    assert.deepEqual(fs.readdirSync(out), ['selector-gate-flow.sh']);
  });
});

describe('AC-3 — a baseline grandfathers existing findings without hiding new ones', function () {
  const baselineFor = function (element, selector) {
    return 'selector-gate-mapping.yaml\tlogin.' + element + '\t>>nth\t' + selector + '\n';
  };

  const compileWith = function (elements, baselineText) {
    const dir = mappingDirWith(elements);
    fs.copyFileSync(GATE_FLOW, path.join(dir, 'flow.yaml'));
    const baselinePath = path.join(dir, 'baseline.tsv');
    fs.writeFileSync(baselinePath, baselineText, 'utf8');
    const out = tmpdir('out');
    const res = runCompile([path.join(dir, 'flow.yaml'), '--mappings-dir', dir, '--output-dir', out, '--selector-baseline', baselinePath]);
    res.out = out;
    res.baselinePath = baselinePath;
    return res;
  };

  test('a listed element compiles, and says out loud that the flow resolves it', function () {
    const baselineText = baselineFor('submit_button', 'role=switch >> nth=1');
    const res = compileWith(CLEAN_ELEMENTS, baselineText);
    assert.equal(res.status, 0, res.stderr);
    // AC-4 again, on the SUCCESS path. The byte-compare below it runs only on a blocked
    // compile, and a "regenerate the baseline when the compile goes green" write would be
    // added here, not there — leaving the documented "only ever opens for reading"
    // absolute with an enforcement point that cannot see the case it most needs to.
    assert.equal(fs.readFileSync(res.baselinePath, 'utf8'), baselineText);
    assert.deepEqual(fs.readdirSync(res.out), ['selector-gate-flow.sh']);
    // Not silence: depending on grandfathered debt is louder than dormant debt.
    assert.match(res.stderr, /RESOLVES a grandfathered banned selector/);
  });

  test('a NEW element carrying the same banned string still blocks', function () {
    // The hole a (file, class, selector) key would leave open: paste a known-bad selector
    // onto a fresh element and it inherits the licence.
    const elements = Object.assign({}, CLEAN_ELEMENTS, { submit_button: 'role=switch >> nth=1' });
    const res = compileWith(elements, baselineFor('unused_toggle', 'role=switch >> nth=1'));
    assert.equal(res.status, 1);
    assert.match(res.stderr, /login\.submit_button/);
  });

  test('a CHANGED selector on a listed element still blocks', function () {
    const elements = Object.assign({}, CLEAN_ELEMENTS, { submit_button: 'role=switch >> nth=7' });
    const res = compileWith(elements, baselineFor('submit_button', 'role=switch >> nth=1'));
    assert.equal(res.status, 1);
    assert.match(res.stderr, /nth=7/);
  });

  test('a malformed baseline fails loudly rather than silently grandfathering nothing', function () {
    const res = compileWith(CLEAN_ELEMENTS, 'selector-gate-mapping.yaml\tonly-three\tfields\n');
    assert.equal(res.status, 1);
    assert.match(res.stderr, /malformed selector baseline record/);
  });
});

describe('Cross-site: two mappings sharing a basename are refused, not silently merged', function () {
  test('a cross-site flow blocks, and names the SITE\'s own mapping file', function () {
    // `referencedElements` is stamped with the mapping file by a different expression on
    // the cross-site path than on the single-site one, and a mismatch fails OPEN — banned
    // selector, clean compile — with the rest of the suite green.
    //
    // TWO sites, and the banned element lives in the SECOND. A single-site flow would not
    // discriminate: when the cross-site stamp is absent the compiler falls back to the
    // first mapping path, which in a one-mapping flow is the right answer by accident. An
    // earlier version of this test did exactly that and stayed green when the stamp was
    // deleted — it proved nothing.
    const dir = tmpdir('xsite-block');
    const mapping = function (selector) {
      return ['version: 2', 'app: x', 'base_url: "http://localhost:3000"', 'pages:', '  login:',
              '    elements:', '      btn:', "        selector: '" + selector + "'", ''].join('\n');
    };
    fs.writeFileSync(path.join(dir, 'site-a.yaml'), mapping('[data-testid="clean"]'), 'utf8');
    fs.writeFileSync(path.join(dir, 'site-b.yaml'), mapping('role=switch >> nth=1'), 'utf8');
    fs.writeFileSync(path.join(dir, 'flow.yaml'), [
      'name: xsite-block', 'sites:', '  one:', '    mapping: site-a', '  two:', '    mapping: site-b',
      'steps:', '  - id: click-two', '    type: click', '    site: two',
      '    action: "Click btn on login"', '',
    ].join('\n'), 'utf8');

    const out = tmpdir('out');
    const res = runCompile([path.join(dir, 'flow.yaml'), '--mappings-dir', dir, '--output-dir', out, '--selector-baseline', NO_BASELINE]);
    assert.equal(res.status, 1, res.stderr);
    const errors = res.stderr.split('\n').filter(function (l) { return l.startsWith('ERROR:'); });
    assert.ok(errors.length > 0, 'expected a blocking error');
    // The site's OWN mapping, not the first one loaded — this is the assertion the stamp
    // has to earn.
    assert.ok(errors.every(function (l) { return l.includes('site-b.yaml'); }), errors.join('\n'));
    assert.ok(errors.every(function (l) { return !l.includes('site-a.yaml'); }), errors.join('\n'));
    assert.match(res.stderr, /login\.btn/);
    assert.deepEqual(fs.readdirSync(out), []);
  });

  test('a basename collision blocks with a message naming it', function () {
    // The finding identity, the baseline record and the diagnostic all key on the
    // basename. Two sites loading `a/m.yaml` and `b/m.yaml` would make one site's blocking
    // finding suppress the other's warning, and one baseline record grandfather both.
    // Refusing is the enforcement point for the docs' claim that a basename suffices.
    const dir = tmpdir('xsite');
    fs.mkdirSync(path.join(dir, 'a'));
    fs.mkdirSync(path.join(dir, 'b'));
    const mapping = ['version: 2', 'app: x', 'base_url: "http://localhost:3000"', 'pages:', '  login:', '    elements:', '      btn:', "        selector: '[data-testid=\"b\"]'", ''].join('\n');
    fs.writeFileSync(path.join(dir, 'a', 'm.yaml'), mapping, 'utf8');
    fs.writeFileSync(path.join(dir, 'b', 'm.yaml'), mapping, 'utf8');
    fs.writeFileSync(path.join(dir, 'flow.yaml'), [
      'name: xsite-flow', 'sites:', '  one:', '    mapping: a/m', '  two:', '    mapping: b/m',
      'steps:', '  - id: click-one', '    type: click', '    site: one',
      '    action: "Click btn on login"', '',
    ].join('\n'), 'utf8');

    const out = tmpdir('out');
    const res = runCompile([path.join(dir, 'flow.yaml'), '--mappings-dir', dir, '--output-dir', out, '--selector-baseline', NO_BASELINE]);
    assert.equal(res.status, 1, res.stderr);
    assert.match(res.stderr, /share the basename/);
    assert.deepEqual(fs.readdirSync(out), []);
  });
});

describe('AC-4 — the gate cannot regenerate its own baseline', function () {
  test('a blocked compile leaves the baseline file byte-identical', function () {
    const dir = mappingDirWith(CLEAN_ELEMENTS);
    fs.copyFileSync(GATE_FLOW, path.join(dir, 'flow.yaml'));
    const baselinePath = path.join(dir, 'baseline.tsv');
    const before = '# nothing grandfathered yet\n';
    fs.writeFileSync(baselinePath, before, 'utf8');

    const res = runCompile([path.join(dir, 'flow.yaml'), '--mappings-dir', dir, '--output-dir', tmpdir('out'), '--selector-baseline', baselinePath]);
    assert.equal(res.status, 1, 'precondition: this compile must block, or the test proves nothing');
    assert.equal(fs.readFileSync(baselinePath, 'utf8'), before);
  });

  test('the CLI exposes no flag that writes a baseline', function () {
    const help = execFileSync('node', [CLI, '--help'], { encoding: 'utf8' });
    assert.match(help, /--selector-baseline/, 'precondition: the read flag must exist');
    assert.doesNotMatch(help, /update-baseline|write-baseline|regenerate-baseline|--format[= ]baseline/);
  });

  test('the producer is a separate binary that writes nothing', function () {
    const producer = path.join(PLUGIN_ROOT, 'bin', 'e2e-selector-baseline.js');
    const mapping = path.join(FIXTURES, 'selector-gate-mapping.yaml');
    const stdout = execFileSync('node', [producer, mapping], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });

    // It emits records for BOTH banned elements — file scope, not blocking scope — which
    // is what makes an adopted baseline cover pre-existing debt rather than only what one
    // flow happens to reach today.
    const records = stdout.split('\n').filter(function (l) { return l.length > 0 && !l.startsWith('#'); });
    assert.equal(records.length, 2);
    assert.ok(records.some(function (r) { return r.includes('login.submit_button'); }));
    assert.ok(records.some(function (r) { return r.includes('login.unused_toggle'); }));

    // And its output is exactly what the gate accepts — producer and consumer agree by
    // round trip, not by assertion.
    const dir = mappingDirWith(CLEAN_ELEMENTS);
    fs.copyFileSync(GATE_FLOW, path.join(dir, 'flow.yaml'));
    const baselinePath = path.join(dir, 'baseline.tsv');
    fs.writeFileSync(baselinePath, stdout, 'utf8');
    const out = tmpdir('out');
    const res = runCompile([path.join(dir, 'flow.yaml'), '--mappings-dir', dir, '--output-dir', out, '--selector-baseline', baselinePath]);
    assert.equal(res.status, 0, res.stderr);
    assert.deepEqual(fs.readdirSync(out), ['selector-gate-flow.sh']);
  });
});
