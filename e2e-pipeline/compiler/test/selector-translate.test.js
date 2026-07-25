'use strict';

/**
 * selector-translate.test.js — text=V → a11y grep pattern (e2e-selector-canon-review).
 *
 * The codemod spike (docs/dev/.spacedock-state/e2e-selector-lint-gate.md) found bare
 * `text=` is the largest refusal class in the real corpus (83 of 452 unique selectors).
 * This entity un-refuses it: `text=V` translates to the same a11y-grep-pattern shape
 * `[role=/[role=]` already produce, so `_poll_snapshot_contains` (codegen.js:1572,
 * `grep -Fq` against the accessibility snapshot) can match it.
 *
 * The second describe block exercises the translated pattern against real
 * `agent-browser` 0.21.4 snapshot lines (recorded in the entity body's "Empirical
 * record") via the actual `grep -F` binary the runtime uses — not a JS string
 * comparison standing in for it — so AC-3 ("verified by exercising them against a
 * real snapshot, not by reading the branch") has evidence beyond the unit assertion.
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const childProcess = require('node:child_process');

const { selectorToA11yPattern } = require('../lib/selector-translate.js');

describe('selectorToA11yPattern: text=V branch', function () {
  test('text=Save -> "Save" (bare value, no quotes)', function () {
    assert.equal(selectorToA11yPattern('text=Save'), '"Save"');
  });

  test('text=AlphaBtn -> "AlphaBtn"', function () {
    assert.equal(selectorToA11yPattern('text=AlphaBtn'), '"AlphaBtn"');
  });

  test('text="Save" -> "Save" (surrounding double quotes stripped before re-quoting)', function () {
    assert.equal(selectorToA11yPattern('text="Save"'), '"Save"');
  });

  test("text='Save' -> \"Save\" (surrounding single quotes stripped before re-quoting)", function () {
    assert.equal(selectorToA11yPattern("text='Save'"), '"Save"');
  });

  test('text=CJK value round-trips byte-for-byte', function () {
    assert.equal(selectorToA11yPattern('text=儀表板首頁'), '"儀表板首頁"');
  });

  test('existing role-form branches are unaffected (backward compat, unchanged)', function () {
    assert.equal(selectorToA11yPattern('role=button[name="Save"]'), 'button "Save"');
    assert.equal(selectorToA11yPattern('[role="button"][aria-label="Save"]'), 'button "Save"');
  });

  test('still returns null for a genuinely unconvertible form', function () {
    assert.equal(selectorToA11yPattern('css=.some-class'), null);
  });
});

describe('selectorToA11yPattern: text=V pattern greps a real agent-browser snapshot (AC-3)', function () {
  // Fixture recorded verbatim from the entity body's "Empirical record" section —
  // a live `agent-browser` 0.21.4 snapshot of three buttons, two with no `role`
  // and no `aria-label`, one with both.
  const SNAPSHOT_FIXTURE = [
    '- button "AlphaBtn" [ref=e1]',
    '- button "BetaBtn" [ref=e2]',
    '- button "GammaLabel" [ref=e3]',
    '  - StaticText "GammaBtn"',
  ].join('\n');

  function grepDashFqHits(pattern) {
    // Mirrors codegen.js's `_poll_snapshot_contains`:
    //   printf '%s\n' "$_snapshot" | grep -Fq "$_pattern"
    const result = childProcess.spawnSync(
      'bash',
      ['-c', 'grep -Fq "$1"', '--', pattern],
      { input: SNAPSHOT_FIXTURE, encoding: 'utf8' }
    );
    return result.status === 0;
  }

  test('text=AlphaBtn resolves against a button with no role/aria-label attributes', function () {
    const pattern = selectorToA11yPattern('text=AlphaBtn');
    assert.equal(pattern, '"AlphaBtn"');
    assert.equal(grepDashFqHits(pattern), true, 'grep -Fq must hit the snapshot line for a plain <button>AlphaBtn</button>');
  });

  test('text=GammaLabel resolves against the computed (aria-label-wins) accessible name', function () {
    const pattern = selectorToA11yPattern('text=GammaLabel');
    assert.equal(pattern, '"GammaLabel"');
    assert.equal(grepDashFqHits(pattern), true, 'grep -Fq must hit the aria-label-derived name, not the StaticText content');
  });

  test('text=NotPresent does not resolve (negative control — proves the grep is not vacuous)', function () {
    const pattern = selectorToA11yPattern('text=NotPresent');
    assert.equal(grepDashFqHits(pattern), false);
  });
});
