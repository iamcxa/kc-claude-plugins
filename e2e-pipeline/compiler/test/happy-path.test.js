'use strict';

/**
 * happy-path.test.js — one real-shaped flow, compiled end to end.
 *
 * WHAT THIS HAS AND HAS NOT EARNED
 *
 * **It has never caught an escaped defect.** Checked against the six issues in sprint S2,
 * the sprint whose "combination defects" motivated it: it would have caught none of them.
 * #122 was a load flake, #150 a documentation gap, #148 model prose, #121 a branch the
 * resolver cannot reach, #124 a ruling, #149 a detector. Not one is a compile-level
 * combination.
 *
 * So this guards a class that is real — units pass while their combination breaks — for
 * which this repository has no recorded instance. That makes it speculative, and it is
 * kept small on those grounds rather than grown on the strength of the story. If a year
 * passes without it failing on something a unit test missed, deleting it is the correct
 * outcome, not a loss.
 *
 * An earlier version was larger: two flow fixtures where one covers the same axes, and a
 * third scenario asserting that a banned chord is refused — which `selector-gate.test.js`
 * already asserts, down to the same "exit 1, no artifact, names the class and the
 * replacement". That duplicate is gone.
 *
 * WHY COMPILE-LEVEL AND NOT A BROWSER
 *
 * Compilation is where the combination is decided — resolver, selector policy, visibility
 * path and codegen all run — and it costs under a second. A browser gate on a PR is the
 * flake source #122 was about, and is currently impossible on the runner anyway (#174).
 * The browser layer is #176, on a weekly schedule.
 *
 * WHY THESE COMBINATIONS
 *
 * Measured against a real consumer corpus (47 flows, 5 mappings), not chosen:
 *
 *   selectors  plain CSS 40% · data-testid 28% · text= 14% · role=X[name=/re/] 11%   93%
 *   actions    Click 39% · Navigate 18% · Wait 14% · Fill 11% · Verify 10%           91%
 *   expects    "visible on" 53% · "url contains" 34% · "is visible" 7% · "not" 2%    96%
 *
 * Absent because the corpus does not use them: `visibility_policy` (0), or-expects (0),
 * `Execute external` (11, ~4%).
 *
 * WHAT IT CANNOT CATCH
 *
 * It reads the generated source rather than running it, so two classes stay open:
 * escaping that is wrong but well-formed (`recoverSelectorText` normalises quoting, which
 * also makes a broken emission read like a correct one, and `bash -n` cannot check the
 * JavaScript inside an `eval`), and missing actions (selectors and assertions are pinned;
 * every `open`/`fill`/`click`/`wait` is not). Both need the same instrument — execute the
 * script against a stubbed runtime and assert the argv — tracked in #180.
 *
 * WHEN A BUG IS FIXED
 *
 * Add the combination that produced it here, and say which issue it came from. The first
 * such entry is what would move this file from speculative to earned.
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const childProcess = require('node:child_process');

const { compile } = require('../compiler');

const FIXTURES = path.join(__dirname, 'fixtures');

// The DOM identities that must survive compilation into the script.
const MUST_RESOLVE = [
  "input[type='email']",            // plain CSS, 40% of the corpus
  '[data-testid="login-submit"]',   // data-testid, 28%
  '[data-testid="welcome"]',        // css_selector for a text= element
  'button[aria-label="重新整理"]',   // css_selector for a role-regex element
  'table.results',                  // css_selector for a bare role element
];

// …and the assertions they are subject to, with polarity. A resolved selector proves the
// element survived; it says nothing about whether the flow still checks what it asked for.
const MUST_ASSERT = [
  /_poll_url_contains '\/login'/,
  /_poll_url_contains '\/dashboard'/,
  /_poll_visibility '\[data-testid="login-error"\]' 'strict' not-visible/,
  /_poll_visibility '\[data-testid="welcome"\]' 'strict' visible/,
  /_poll_visibility 'table\.results' 'strict' visible/,
];

/**
 * Recover a selector's written form from the generated script.
 *
 * An identity crosses two escaping layers before it reaches the DOM call — bash single
 * quotes, then a JS string inside them. Undoing both lets the assertion pin the identity
 * rather than codegen's quoting style. It is also the reason this file cannot detect an
 * emission that is wrong but well-formed; see WHAT IT CANNOT CATCH above.
 */
function recoverSelectorText(script) {
  return script.split("'\\''").join("'").split('\\"').join('"');
}

describe('happy path: the combinations real flows use', function() {
  test('the corpus-shaped flow compiles to a runnable script', async function(t) {
    const mappingDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-map-'));
    const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-out-'));
    t.after(function() {
      fs.rmSync(mappingDir, { recursive: true, force: true });
      fs.rmSync(outDir, { recursive: true, force: true });
    });
    fs.copyFileSync(
      path.join(FIXTURES, 'happy-path-mapping.yaml'),
      path.join(mappingDir, 'happy-path-app.yaml')
    );

    const result = await compile(
      path.join(FIXTURES, 'happy-path-flow.yaml'),
      mappingDir,
      outDir
    );

    assert.ok(result.success, 'compile must succeed. errors: ' + JSON.stringify(result.errors));
    assert.ok(fs.existsSync(result.outputPath), 'a script must be written');

    // `bash -n` is the cheapest instrument that can fail on the quoting defects codegen
    // can emit — CJK values, regex-bearing selectors, apostrophes.
    const syntax = childProcess.spawnSync('bash', ['-n', result.outputPath], { stdio: 'pipe' });
    assert.equal(syntax.status, 0, 'bash -n must accept the script: ' + syntax.stderr);

    const readable = recoverSelectorText(fs.readFileSync(result.outputPath, 'utf8'));
    for (const selector of MUST_RESOLVE) {
      assert.ok(
        readable.includes(selector),
        'generated script must carry the resolved identity ' + JSON.stringify(selector)
      );
    }
    for (const operation of MUST_ASSERT) {
      assert.match(readable, operation, 'generated script must emit the assertion ' + operation);
    }
  });
});
