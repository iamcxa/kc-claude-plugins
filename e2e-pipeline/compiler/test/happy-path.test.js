'use strict';

/**
 * happy-path.test.js — the combinations real flows actually use, compiled end to end.
 *
 * WHY THIS EXISTS, GIVEN 1000 OTHER ASSERTIONS
 *
 * The rest of the suite tests units: the parser alone, the resolver alone, one selector
 * form, one expect type. Every S2 issue was a defect in a *combination* — a selector form
 * meeting a visibility path, a fidelity state meeting a `--no-compile` run, a temp root
 * meeting a platform. Units were green throughout.
 *
 * WHY COMPILE-LEVEL AND NOT A BROWSER
 *
 * A browser gate on a PR is slow and, on this runtime, currently impossible (#174: the
 * runtime needs `agent-browser` on PATH, and the runner has neither it nor Chrome for
 * Testing). It would also be the flake source that #122 was about. Compilation is where
 * the combination is decided — resolver + selector policy + visibility path + codegen all
 * run — and it takes milliseconds. The browser layer is tracked separately in #176.
 *
 * WHY THESE COMBINATIONS AND NOT OTHERS
 *
 * Measured against a real consumer corpus (47 flows, 5 mappings) rather than chosen:
 *
 *   selectors  plain CSS 40% · data-testid 28% · text= 14% · role=X[name=/re/] 11%   93%
 *   actions    Click 39% · Navigate 18% · Wait 14% · Fill 11% · Verify 10%           91%
 *   expects    "visible on" 53% · "url contains" 34% · "is visible" 7% · "not" 2%    96%
 *
 * Deliberately absent, because the corpus does not use them: `visibility_policy` (0
 * occurrences), or-expects (0), and `Execute external` (11, ~4%). Adding fixtures for
 * shapes nobody writes would grow the gate without covering anything.
 *
 * WHEN A BUG IS FIXED
 *
 * Add the combination that produced it here. That is the cheap half of #170's rule — an
 * issue found in a consumer runtime leaves behind a scenario, so the next regression in
 * that combination fails before a browser is involved.
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const childProcess = require('node:child_process');

const { compile } = require('../compiler');

const FIXTURES = path.join(__dirname, 'fixtures');

/**
 * A mapping directory named for the app, torn down with the test that made it.
 *
 * `compile` resolves a mapping by filename, so the fixture has to be copied to
 * `<app>.yaml` somewhere. Doing that once at module load leaked an `e2e-happy-map-*`
 * directory into the OS temp root on every invocation — a test that litters the machine
 * it runs on, which over a CI lifetime is exactly the kind of debris that later makes a
 * temp-root guard look flaky.
 */
function mappingDir(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-map-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });
  fs.copyFileSync(
    path.join(FIXTURES, 'happy-path-mapping.yaml'),
    path.join(dir, 'happy-path-app.yaml')
  );
  return dir;
}

const SCENARIOS = [
  {
    slug: 'happy-path-auth-flow.yaml',
    label: 'sign in and reach the dashboard',
    // Selector forms this scenario must actually drive into the generated script.
    mustResolve: ["input[type='email']", '[data-testid="login-submit"]'],
    // …and the assertions those elements are subject to. A selector reaching the script
    // says the element resolved; it does not say the flow still asserts what it wrote.
    // Without these, codegen could drop or invert every expect and this stays green.
    mustAssert: [
      // `url contains` — 34% of corpus expects, on both the start and the landing page.
      /_poll_url_contains '\/login'/,
      /_poll_url_contains '\/dashboard'/,
      // `not visible` — the polarity is the point. An inverted assertion is the failure
      // mode a presence check cannot see.
      /_poll_visibility '\[data-testid="login-error"\]' 'strict' not-visible/,
      // …and its positive counterpart, so a global polarity flip cannot pass either.
      /_poll_visibility '\[data-testid="welcome"\]' 'strict' visible/,
    ],
  },
  {
    slug: 'happy-path-locators-flow.yaml',
    label: 'assert elements located by text=, role regex, and bare role',
    // The css_selector companions, which are what mapped visibility resolves post-#91.
    mustResolve: ['[data-testid="welcome"]', 'button[aria-label="重新整理"]', 'table.results'],
    mustAssert: [
      /_poll_url_contains '\/dashboard'/,
      // The non-CSS-located elements must be asserted through their DOM identity, which
      // is the whole point of the css_selector companion.
      /_poll_visibility 'table\.results' 'strict' visible/,
      /_poll_visibility '\[data-testid="nav-dashboard"\]' 'strict' visible/,
    ],
  },
];

/**
 * Recover a selector's written form from the generated script.
 *
 * An identity crosses two escaping layers on its way to the DOM call:
 *
 *   input[type='email']          ->  input[type='\''email'\'']        bash single quotes
 *   button[aria-label="重新整理"] ->  querySelector("button[aria-label=\"重新整理\"]")
 *                                                                     JS string in bash
 *
 * Both are correct output and neither is recognisable as the selector it came from.
 * Undoing them lets the assertion pin the *identity* rather than codegen's quoting style,
 * which is not what these scenarios are about and would red on a harmless change to it.
 * Normalising also keeps the fixture faithful to the corpus, where `input[type='email']`
 * is a real entry — a fixture bent into an easy-to-assert shape tests the assertion.
 */
function recoverSelectorText(script) {
  return script.split("'\\''").join("'").split('\\"').join('"');
}

function compileScenario(t, slug) {
  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-out-'));
  t.after(function() {
    fs.rmSync(outDir, { recursive: true, force: true });
  });
  return compile(path.join(FIXTURES, slug), mappingDir(t), outDir);
}

describe('happy path: the combinations real flows use', function() {
  for (const scenario of SCENARIOS) {
    test(scenario.label + ' compiles to a runnable script', async function(t) {
      const result = await compileScenario(t, scenario.slug);

      assert.ok(
        result.success,
        'compile must succeed. errors: ' + JSON.stringify(result.errors)
      );
      assert.ok(fs.existsSync(result.outputPath), 'a script must be written');

      const script = fs.readFileSync(result.outputPath, 'utf8');

      // Syntactically valid bash. `bash -n` is the cheapest instrument that can fail here
      // and it catches the whole class of quoting defects codegen can emit — CJK values,
      // regex-bearing selectors, apostrophes.
      const syntax = childProcess.spawnSync('bash', ['-n', result.outputPath], {
        stdio: 'pipe',
      });
      assert.equal(syntax.status, 0, 'bash -n must accept the script: ' + syntax.stderr);

      // The DOM identity each element resolves to has to reach the script. A compile that
      // succeeds while silently dropping a selector would pass every check above.
      const readable = recoverSelectorText(script);
      for (const selector of scenario.mustResolve) {
        assert.ok(
          readable.includes(selector),
          'generated script must carry the resolved identity ' + JSON.stringify(selector)
        );
      }

      // …and the assertion each element is subject to, with its polarity. A resolved
      // selector proves the element survived compilation; it says nothing about whether
      // the flow still checks what it asked for.
      for (const operation of scenario.mustAssert) {
        assert.match(
          readable,
          operation,
          'generated script must emit the assertion ' + operation
        );
      }
    });
  }

  test('a banned selector is refused at compile time, in a realistic mapping', async function(t) {
    // The `refusal` falsifier for #88's gate and #124's ruling. Both are covered by unit
    // tests against synthetic input; this drives the same rule through a mapping shaped
    // like a real one, which is where the corpus actually carries the violation.
    const mappingDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-banned-'));
    const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-banned-out-'));
    t.after(function() {
      fs.rmSync(mappingDir, { recursive: true, force: true });
      fs.rmSync(outDir, { recursive: true, force: true });
    });

    const mapping = fs.readFileSync(
      path.join(FIXTURES, 'happy-path-mapping.yaml'),
      'utf8'
    ).replace(
      'selector: "role=table"',
      'selector: "role=table >> nth=1"'
    );
    assert.match(mapping, />> nth=1/, 'the fixture edit must have applied');
    fs.writeFileSync(path.join(mappingDir, 'happy-path-app.yaml'), mapping, 'utf8');

    const result = await compile(
      path.join(FIXTURES, 'happy-path-locators-flow.yaml'),
      mappingDir,
      outDir
    );

    assert.equal(result.success, false, 'a banned chord must not compile');
    const errors = JSON.stringify(result.errors);
    assert.match(errors, />>nth/, 'the diagnostic must name the class');
    assert.match(errors, /css_selector/, 'and the replacement the ruling settled on');
    assert.deepEqual(
      fs.readdirSync(outDir),
      [],
      'a refused compile must not leave a script behind'
    );
  });
});
