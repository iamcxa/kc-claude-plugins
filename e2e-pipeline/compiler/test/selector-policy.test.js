'use strict';

/**
 * selector-policy.test.js — the shared banned-selector policy (#88).
 *
 * `scripts/lint-mapping.sh` carried the ban as inline bash regexes that nothing on the
 * compiled path could call. This module is the table both consumers now read. Two
 * traversals sit on top of it because line numbers and element identity are different
 * facts: `scanMappingText` reads raw bytes and yields line numbers (what the linter
 * reports), `scanElements` reads resolved element records and yields element identity
 * (what the compiler blocks on and what a baseline record is keyed by).
 *
 * CLASS 1 (`role=X[name=…]`) and CLASS 3 (bare `text=`) are RETIRED, not deferred —
 * PR #123 landed the captain's 2026-07-25 ruling. The retirement has explicit negative
 * tests here because re-adding either is the specific regression this file exists to
 * catch.
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const policy = require('../lib/selector-policy.js');

const {
  BANNED_CLASSES,
  classifySelector,
  locateSelectorLine,
  scanMappingText,
  scanElements,
  parseBaseline,
  isGrandfathered,
  baselineRecord,
} = policy;

describe('BANNED_CLASSES: the table itself', function () {
  test('carries exactly the three classes that survived PR #123', function () {
    assert.deepEqual(
      BANNED_CLASSES.map(function (c) { return c.id; }).sort(),
      ['>>nth', 'find-subcommand', 'has-text']
    );
  });

  test('every class carries replacement guidance a diagnostic can print', function () {
    BANNED_CLASSES.forEach(function (c) {
      assert.equal(typeof c.guidance, 'string');
      assert.ok(c.guidance.length > 0, c.id + ' has empty guidance');
    });
  });

  test('the module requires only Node builtins, so the linter needs no npm install', function () {
    // The docs promise `lint-mapping.sh` stays wireable into a consumer `.githooks`
    // without `npm install`. This is that promise's enforcement point: a `require` of
    // anything outside the builtin set would break it, and it would break here first.
    const source = fs.readFileSync(path.join(__dirname, '..', 'lib', 'selector-policy.js'), 'utf8');
    const re = /require\(\s*['"]([^'"]+)['"]\s*\)/g;
    const requires = Array.from(source.matchAll(re), function (m) { return m[1]; });
    assert.ok(requires.length > 0, 'matched no require() at all — the check would pass by silence');
    requires.forEach(function (spec) {
      assert.ok(
        spec.startsWith('node:') || require('node:module').builtinModules.includes(spec),
        'non-builtin require in selector-policy.js: ' + spec
      );
    });
  });
});

describe('the linter CLI contract two consumers read', function () {
  const { execFileSync, spawnSync } = require('node:child_process');
  const LINTER = path.join(__dirname, '..', '..', 'scripts', 'lint-mapping.sh');

  test('--help exits 0; missing arguments exit 1', function () {
    // A `.githooks` wrapper checking `$?` reads a non-zero `--help` as a failure, so the
    // two cases must not share an exit code even though they print the same text.
    const help = spawnSync('bash', [LINTER, '--help'], { encoding: 'utf8' });
    assert.equal(help.status, 0);
    assert.match(help.stdout, />>nth/);
    assert.equal(spawnSync('bash', [LINTER], { encoding: 'utf8' }).status, 1);
  });

  test('the usage text is generated from the table, so it cannot drift from it', function () {
    const help = spawnSync('bash', [LINTER, '--help'], { encoding: 'utf8' }).stdout;
    BANNED_CLASSES.forEach(function (c) {
      assert.ok(help.includes(c.id), 'usage text omits class ' + c.id);
    });
  });
});

describe('classifySelector: one decision function, three classes', function () {
  // Returns an ARRAY, not a single id: today's bash linter counts one error per class
  // per selector, so a value that trips two classes must stay two findings. Collapsing
  // to a single id would quietly change `lint-mapping.sh`'s error count.
  test('CLASS 2 — the Playwright nth chord', function () {
    assert.deepEqual(classifySelector('.MuiButton-root >> nth=2'), ['>>nth']);
    assert.deepEqual(classifySelector('role=combobox >> nth=0'), ['>>nth']);
    assert.deepEqual(classifySelector("role=row >> nth=1 >> [data-testid^='x-']"), ['>>nth']);
  });

  test('CLASS 4 — Playwright has-text', function () {
    assert.deepEqual(classifySelector('.MuiDialog :has-text("Confirm")'), ['has-text']);
    // The real fixture form: a `>>` chord with no `nth=` is has-text alone, not both.
    assert.deepEqual(classifySelector('.MuiDialog >> :has-text("Confirm deletion")'), ['has-text']);
  });

  test('CLASS 5 — an agent-browser subcommand chain stored as a selector', function () {
    assert.deepEqual(classifySelector('find role button --name "Sign In"'), ['find-subcommand']);
    assert.deepEqual(classifySelector('find text "Search results"'), ['find-subcommand']);
    assert.deepEqual(classifySelector('find testid "x"'), ['find-subcommand']);
  });

  test('a NEGATIVE nth index is banned too', function () {
    // Playwright accepts `nth=-1` (last match). The pure-bash predecessor matched
    // `nth=[0-9]+` only, so this linted clean on main — harmless while the linter was
    // advisory, a hole once its verdict became a refusal. Without this case the fix has
    // no evidence that can fail: reverting `-?` leaves the whole suite green.
    assert.deepEqual(classifySelector('role=button >> nth=-1'), ['>>nth']);
    assert.deepEqual(classifySelector('.row >> nth=-2'), ['>>nth']);
  });

  test('a value tripping two classes yields two ids, in table order', function () {
    assert.deepEqual(
      classifySelector('.MuiDialog >> nth=1 >> :has-text("Confirm")'),
      ['>>nth', 'has-text']
    );
  });

  test('CLASS 1 and CLASS 3 stay retired — re-banning either is the regression', function () {
    assert.deepEqual(classifySelector('role=textbox[name="Email"]'), []);
    assert.deepEqual(classifySelector('role=button[name="Save"]'), []);
    assert.deepEqual(classifySelector('text=Submit'), []);
    assert.deepEqual(classifySelector('text=儀表板首頁'), []);
  });

  test('native forms are clean', function () {
    assert.deepEqual(classifySelector('[data-testid="vehicle-row"]'), []);
    assert.deepEqual(classifySelector('[role="button"][aria-label="通知"]'), []);
    assert.deepEqual(classifySelector('.MuiButton-root:nth-of-type(3)'), []);
    assert.deepEqual(classifySelector('h1'), []);
  });

  test('a non-string is not a selector and is not classified', function () {
    assert.deepEqual(classifySelector(undefined), []);
    assert.deepEqual(classifySelector(null), []);
    assert.deepEqual(classifySelector(42), []);
  });

  test('"find" only fires as a subcommand chain, not as a CSS class named find', function () {
    assert.deepEqual(classifySelector('.finder-panel'), []);
    assert.deepEqual(classifySelector('[data-testid="find-button"]'), []);
  });
});

describe('scanMappingText: line-numbered traversal (the linter s view)', function () {
  const TEXT = [
    'version: 2',
    'pages:',
    '  home:',
    '    elements:',
    '      ok_button:',
    "        selector: '[data-testid=\"ok\"]'",
    '      third_button:',
    "        selector: '.MuiButton-root >> nth=2'",
    '      dialog_heading:',
    '        # migration note: never write :has-text( in a selector',
    '        description: "do not use find role button --name X here"',
    '        selector: \'.MuiDialog :has-text("Confirm")\'',
    '',
  ].join('\n');

  test('reports one finding per violating selector, with its 1-based line', function () {
    const findings = scanMappingText(TEXT, 'm.yaml');
    assert.equal(findings.length, 2);
    assert.equal(findings[0].line, 8);
    assert.equal(findings[0].class, '>>nth');
    assert.equal(findings[1].line, 12);
    assert.equal(findings[1].class, 'has-text');
  });

  test('comments and description values are documentation, not violations (PR #8 C2)', function () {
    const findings = scanMappingText(TEXT, 'm.yaml');
    const lines = findings.map(function (f) { return f.line; });
    assert.ok(!lines.includes(10), 'flagged a comment line');
    assert.ok(!lines.includes(11), 'flagged a description: value');
  });

  test('a quoted value containing # is read whole, not truncated at the hash', function () {
    // `#` inside a quoted scalar is part of the value. Stripping the comment before
    // handling quotes collapsed this to `"div` and the chord went unreported — the linter
    // then passed what the compiler blocks, which is the two consumers disagreeing on the
    // same bytes. Reverting the quote-first ordering must redden this.
    const findings = scanMappingText('  selector: "div #main >> nth=1"\n', 'm.yaml');
    assert.equal(findings.length, 1);
    assert.equal(findings[0].selector, 'div #main >> nth=1');
    assert.equal(findings[0].class, '>>nth');
  });

  test('strips surrounding quotes and a trailing inline comment before classifying', function () {
    const findings = scanMappingText(
      'selector: ".MuiButton-root >> nth=2"   # legacy, migrate me\n',
      'm.yaml'
    );
    assert.equal(findings.length, 1);
    assert.equal(findings[0].selector, '.MuiButton-root >> nth=2');
  });

  test('a double-quoted scalar is unescaped, so both traversals see the same string', function () {
    // Real corpus line: selector: "role=button[name=\"left\"] >> nth=0". The element
    // traversal reads a YAML-parsed value; without this the two channels disagree and the
    // same element is reported as both blocking and a warning.
    const f = scanMappingText('        selector: "role=button[name=\\"left\\"] >> nth=0"\n', 'm.yaml')[0];
    assert.equal(f.selector, 'role=button[name="left"] >> nth=0');
  });

  test("a single-quoted scalar's doubled quote is unescaped", function () {
    const f = scanMappingText("  selector: 'a[title=''x''] >> nth=0'\n", 'm.yaml')[0];
    assert.equal(f.selector, "a[title='x'] >> nth=0");
  });

  test('only \\" and \\\\ are unescaped — any other escape is left verbatim', function () {
    // Turning `\\n` into `n` would be this traversal inventing a value YAML never
    // produced, and would put it out of step with the element traversal for no reason.
    const f = scanMappingText('  selector: "a\\\\nb >> nth=1"\n', 'm.yaml')[0];
    assert.equal(f.selector, 'a\\nb >> nth=1');
  });

  test('an empty selector value (block scalar follows) is skipped, not classified', function () {
    assert.equal(scanMappingText('selector:\n', 'm.yaml').length, 0);
  });

  test('a block/folded scalar is NOT read — bounded, and the bound is the point', function () {
    // The dependency-free text traversal cannot follow `selector: >` onto its value line.
    // Asserted rather than assumed so the docstring's caveat has a check behind it, and so
    // this reads as a stated limit rather than an undiscovered hole. The compiler's
    // blocking gate is unaffected: it traverses parsed YAML.
    const folded = 'elements:\n  foo:\n    selector: >\n      role=switch >> nth=1\n';
    assert.equal(scanMappingText(folded, 'm.yaml').length, 0);
    // ...and the element traversal, which is what blocks, does see it:
    assert.deepEqual(
      scanElements([{ mappingFile: 'm.yaml', page: 'p', element: 'foo', selector: 'role=switch >> nth=1\n' }])
        .map(function (f) { return f.class; }),
      ['>>nth']
    );
  });

  test('carries the file path and the guidance into every finding', function () {
    const f = scanMappingText("  selector: '.a >> nth=1'\n", 'mappings/app.yaml')[0];
    assert.equal(f.file, 'mappings/app.yaml');
    // The chord's guidance is `css_selector:`, not a `:nth-of-type(N)` rewrite (#124).
    // The rewrite is not an equivalence and a codemod getting it wrong silently
    // retargets elements; `css_selector:` is what mapped visibility requires anyway.
    assert.ok(f.guidance.includes('css_selector'));
    assert.equal(f.guidance.includes('nth-of-type'), false);
  });
});

describe('locateSelectorLine: attaches a line, or refuses to invent one', function () {
  test('finds the line of the element that owns the selector', function () {
    const text = 'elements:\n  submit_button:\n    description: "x"\n  cancel_button:\n    selector: "role=switch >> nth=1"\n';
    assert.equal(locateSelectorLine(text, 'cancel_button', 'role=switch >> nth=1'), 5);
  });

  test('does not steal a sibling element line when the element has no selector', function () {
    // A forward-window search attributed `cancel_button`'s line to `submit_button`, which
    // sends a reader to the wrong element with a confident-looking line number.
    const text = 'elements:\n  submit_button:\n    description: "x"\n  cancel_button:\n    selector: "role=switch >> nth=1"\n';
    assert.equal(locateSelectorLine(text, 'submit_button', 'role=switch >> nth=1'), null);
  });

  test('returns null when two pages define the same element with the same selector', function () {
    // Genuinely ambiguous without parsing the document. Null degrades the message; a guess
    // misdirects the fix.
    const text = [
      'pages:', '  login:', '    elements:', '      submit_button:',
      '        selector: "role=switch >> nth=1"',
      '  checkout:', '    elements:', '      submit_button:',
      '        selector: "role=switch >> nth=1"', '',
    ].join('\n');
    assert.equal(locateSelectorLine(text, 'submit_button', 'role=switch >> nth=1'), null);
  });

  test('a key line with a trailing comment still owns its selector', function () {
    assert.equal(locateSelectorLine('  a: # note\n    selector: ".x >> nth=1"\n', 'a', '.x >> nth=1'), 2);
  });
});

describe('scanElements: element-identity traversal (the gate s view)', function () {
  const RECORDS = [
    { mappingFile: 'secha-office.yaml', page: 'vehicles', element: 'row_toggle', selector: 'role=switch >> nth=1' },
    { mappingFile: 'secha-office.yaml', page: 'vehicles', element: 'ok_button', selector: '[data-testid="ok"]' },
    { mappingFile: 'secha-office.yaml', page: 'modal', element: 'holder_btn', selector: 'role=switch >> nth=1' },
  ];

  test('classifies per element and keeps page + element + mapping file', function () {
    const findings = scanElements(RECORDS);
    assert.equal(findings.length, 2);
    assert.equal(findings[0].page, 'vehicles');
    assert.equal(findings[0].element, 'row_toggle');
    assert.equal(findings[0].mappingFile, 'secha-office.yaml');
    assert.equal(findings[0].class, '>>nth');
  });

  test('the same banned string on two elements is two findings, not one', function () {
    // This is the corpus shape that made a (file, class, selector) baseline key wrong:
    // `role=switch >> nth=1` appears three times in one real mapping.
    const findings = scanElements(RECORDS);
    assert.equal(findings.length, 2);
    assert.notEqual(findings[0].element, findings[1].element);
  });
});

describe('baseline: parse, key, and match', function () {
  const BASELINE_TEXT = [
    '# grandfathered selector findings — see docs/ci-integration.md',
    '# produced by: node bin/e2e-selector-baseline.js <mapping.yaml>',
    '',
    'secha-office.yaml\tvehicles.row_toggle\t>>nth\trole=switch >> nth=1',
    'secha-office.yaml\tmodal.holder_btn\t>>nth\trole=switch >> nth=1',
  ].join('\n');

  const finding = function (page, element, selector) {
    return {
      mappingFile: 'secha-office.yaml',
      page: page,
      element: element,
      class: '>>nth',
      selector: selector,
    };
  };

  test('parses records and ignores comments and blank lines', function () {
    const b = parseBaseline(BASELINE_TEXT);
    assert.equal(b.size, 2);
  });

  test('a listed element is grandfathered', function () {
    const b = parseBaseline(BASELINE_TEXT);
    assert.equal(isGrandfathered(finding('vehicles', 'row_toggle', 'role=switch >> nth=1'), b), true);
    assert.equal(isGrandfathered(finding('modal', 'holder_btn', 'role=switch >> nth=1'), b), true);
  });

  test('the same banned string on a NEW element is not grandfathered', function () {
    // The hole a count-keyed or (file, class, selector)-keyed baseline would leave open:
    // paste a known-bad selector onto a fresh element and it inherits the licence.
    const b = parseBaseline(BASELINE_TEXT);
    assert.equal(isGrandfathered(finding('vehicles', 'brand_new_toggle', 'role=switch >> nth=1'), b), false);
  });

  test('a CHANGED selector on a listed element is not grandfathered', function () {
    const b = parseBaseline(BASELINE_TEXT);
    assert.equal(isGrandfathered(finding('vehicles', 'row_toggle', 'role=switch >> nth=7'), b), false);
  });

  test('a listed element in a DIFFERENT mapping file is not grandfathered', function () {
    const b = parseBaseline(BASELINE_TEXT);
    const other = finding('vehicles', 'row_toggle', 'role=switch >> nth=1');
    other.mappingFile = 'secha-app.yaml';
    assert.equal(isGrandfathered(other, b), false);
  });

  test('an empty baseline grandfathers nothing', function () {
    assert.equal(isGrandfathered(finding('vehicles', 'row_toggle', 'role=switch >> nth=1'), parseBaseline('')), false);
  });

  test('baselineRecord round-trips through parseBaseline', function () {
    const f = finding('vehicles', 'row_toggle', 'role=switch >> nth=1');
    assert.equal(isGrandfathered(f, parseBaseline(baselineRecord(f))), true);
  });

  test('a malformed record is refused loudly rather than silently ignored', function () {
    // A baseline that quietly drops a line it cannot read is a baseline that quietly
    // stops grandfathering — the gate then reds on something the human thought was listed.
    assert.throws(function () { parseBaseline('secha-office.yaml\tonly-three\tfields'); }, /baseline/i);
  });
});
