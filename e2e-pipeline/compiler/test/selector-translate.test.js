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

describe('selectorToA11yPattern: text= refuses what it cannot faithfully translate', function () {
  // Correction round 1. The `^text=(.+)$` match always returned non-null, so chorded
  // and regex corpus values compiled to patterns that can never match — a refusal was
  // removed (lint CLASS 3) without adding the matching translation.
  //
  // Invariant under test: A NON-NULL RETURN IS A PATTERN THAT CAN ACTUALLY MATCH.
  // A null return is the documented `_poll_visible` fallback, not a silent pass.

  describe('chorded values drop the chord and translate the base', function () {
    // Mirrors the established `role=X >> nth=N -> X` precedent (selector-translate.js
    // :93-95). Sound here because the chord disambiguates a DOM-level duplicate render
    // (RNW renders text twice) and the a11y snapshot being grepped does not carry that
    // duplicate — so "the nth match" and "a match" coincide for an existence assertion.
    const CHORDED = [
      ['text=預約詳情 >> nth=0', '"預約詳情"'],
      ['text=取消預約 >> nth=0', '"取消預約"'],
      ['text=載入中... >> nth=0', '"載入中..."'],  // dots are literal text, not a regex
      ['text="我的" >> nth=1', '"我的"'],           // quoted base + chord
      ["text='任務' >> nth=1", '"任務"'],
    ];

    for (const [selector, expected] of CHORDED) {
      test(`${selector} -> ${expected}`, function () {
        assert.equal(selectorToA11yPattern(selector), expected);
      });
    }

    test('a chord is never left inside the emitted pattern', function () {
      for (const [selector] of CHORDED) {
        const pattern = selectorToA11yPattern(selector);
        assert.ok(pattern && !pattern.includes('>>'),
          `pattern for ${selector} must not carry the chord: ${JSON.stringify(pattern)}`);
        assert.ok(!/nth=/.test(pattern),
          `pattern for ${selector} must not carry nth=: ${JSON.stringify(pattern)}`);
      }
    });
  });

  describe('regex values are refused (null), not prefix-extracted', function () {
    // Deliberately NOT mirroring the role= regex branch at :86-91. That branch emits
    // `^Save$` for `role=button[name=/^Save$/]` and `a` for `/a|b/` — patterns grep -F
    // can never match. Reproducing it here would recreate the invariant violation this
    // correction exists to remove. CSS/grep has no regex equivalent; refusing is honest.
    const REGEX_FORMS = [
      'text=/Every \\d+h/',
      'text=/^Save$/',
      'text=/Save.*/',
      'text=/a|b/',
      'text=/每日看板/',
    ];

    for (const selector of REGEX_FORMS) {
      test(`${selector} -> null (falls back to _poll_visible)`, function () {
        assert.equal(selectorToA11yPattern(selector), null);
      });
    }

    test('a regex base behind a chord is still refused', function () {
      assert.equal(selectorToA11yPattern('text=/Every \\d+h/ >> nth=0'), null);
    });
  });

  test('an empty or chord-only text= value is refused', function () {
    assert.equal(selectorToA11yPattern('text= >> nth=0'), null);
    assert.equal(selectorToA11yPattern('text=   '), null);
  });

  test('a non-chord trailer after a quoted value is refused rather than guessed', function () {
    assert.equal(selectorToA11yPattern('text="foo"bar'), null);
  });

  test('INVARIANT: every corpus text= shape either returns null or greps its own snapshot line', function () {
    // The falsifiable form of the invariant. Each entry pairs a real corpus selector
    // shape with the snapshot line agent-browser would emit for it. A non-null pattern
    // MUST hit that line via the same `grep -F` the runtime uses; null is allowed
    // (documented fallback) but a non-null near-miss is the bug being fixed.
    const CORPUS = [
      ['text=預約詳情 >> nth=0', '- text "預約詳情" [ref=e9]'],
      ['text="我的" >> nth=1', '- text "我的" [ref=e4]'],
      ['text=載入中... >> nth=0', '- text "載入中..." [ref=e7]'],
      ['text=CarLove', '- text "CarLove" [ref=e1]'],
      ['text=顧客已停用，無法新增或編輯共管者。', '- text "顧客已停用，無法新增或編輯共管者。" [ref=e2]'],
      ['text=/Every \\d+h/', '- text "Every 4h" [ref=e3]'],
      ['text=/^Save$/', '- button "Save" [ref=e5]'],
    ];

    for (const [selector, snapshotLine] of CORPUS) {
      const pattern = selectorToA11yPattern(selector);
      if (pattern === null) continue;  // documented fallback — allowed
      const hit = childProcess.spawnSync(
        'bash', ['-c', 'grep -Fq "$1"', '--', pattern],
        { input: snapshotLine, encoding: 'utf8' }
      ).status === 0;
      assert.ok(hit,
        `non-null pattern ${JSON.stringify(pattern)} for ${selector} must match ${JSON.stringify(snapshotLine)}`);
    }
  });
});
