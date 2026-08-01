'use strict';

/**
 * selector-policy.js — the banned-selector class table, and the two traversals over it.
 *
 * Before this module the ban lived as inline regexes inside `scripts/lint-mapping.sh`,
 * which nothing on the compiled path invoked: a mapping carrying a banned form compiled
 * green, dry-ran green, and failed only once a browser was already running (#88).
 *
 * What is shared is the *decision* — `classifySelector` — not the traversal. Line numbers
 * and element identity are different facts and neither traversal can produce the other's,
 * so there are two:
 *
 *   scanMappingText  raw bytes  -> findings with `line`     (linter, file-scope warnings)
 *   scanElements     resolved   -> findings with page+element (compile gate, baseline key)
 *
 * The bounded claim this module supports is "one banned-class table, two traversals".
 * Nothing here would stop a second table being added elsewhere; what is tested is that
 * the bash linter's verdicts track THIS table (see the AC-2 drift test).
 *
 * CLASS 1 (`role=<r>[name=…]`) and CLASS 3 (bare `text=`) are RETIRED, not deferred —
 * PR #123 landed the captain's 2026-07-25 ruling after measuring the "canonical"
 * replacement emitted 0 times against 2,183 uses of the banned form. They are absent from
 * the table on purpose and `selector-policy.test.js` pins their absence.
 *
 * Dependencies: Node builtins only. `scripts/lint-mapping.sh` execs this module and is
 * documented as wireable into a consumer `.githooks` without `npm install`; a non-builtin
 * `require` here would break that, and the policy test asserts against it.
 */

/**
 * The policy table. `id` is what appears in linter stderr, in compiler diagnostics, and
 * in a baseline record's class column — one name, so a grep for a class id finds every
 * surface it reaches.
 */
const BANNED_CLASSES = [
  {
    id: '>>nth',
    // `-?` because Playwright accepts negative indices (`nth=-1` is the last match).
    // The pure-bash predecessor matched `[0-9]+` only, so `>> nth=-1` linted clean on
    // main — harmless while the linter was advisory, a hole once it became a gate.
    pattern: />>[ \t]*nth=-?[0-9]+/,
    description: 'Playwright nth chord',
    guidance: 'use the :nth-of-type(N) CSS pseudo-class',
  },
  {
    id: 'has-text',
    pattern: /:has-text\(/,
    description: 'Playwright has-text (broken in agent-browser, times out)',
    guidance: 'no direct replacement — restructure using data-testid, role=<r>[name="<v>"], or text=<v>',
  },
  {
    id: 'find-subcommand',
    pattern: /^find[ \t]+(role|text|label|testid)\b/,
    description: 'agent-browser CLI subcommand chain stored as a selector value',
    guidance: 'use role=<r>[name="<v>"] or [role="<r>"][aria-label="<v>"]',
  },
];

const CLASS_BY_ID = new Map(BANNED_CLASSES.map(function (c) { return [c.id, c]; }));

/**
 * classifySelector(value) -> string[] of banned class ids, in table order.
 *
 * Returns an array rather than a single id because one value can trip more than one
 * class, and `lint-mapping.sh` has always counted those separately. Collapsing them
 * would silently change its error count, which `test/integration-smoke.sh` reads.
 */
function classifySelector(value) {
  if (typeof value !== 'string' || value.length === 0) return [];
  const hits = [];
  for (const cls of BANNED_CLASSES) {
    if (cls.pattern.test(value)) hits.push(cls.id);
  }
  return hits;
}

function guidanceFor(classId) {
  const cls = CLASS_BY_ID.get(classId);
  return cls ? cls.guidance : '';
}

/**
 * Strip an inline trailing YAML comment, trailing whitespace, and one layer of
 * surrounding quotes — the same narrowing `lint-mapping.sh` has applied since PR #8
 * review C2, which established that a `description:` or a comment mentioning a banned
 * form is documentation, not a contract violation.
 */
function normalizeScalar(raw) {
  let v = raw.replace(/^[ \t]+/, '');

  // Quoted scalars are read to their closing quote FIRST, because a `#` inside a quoted
  // value is part of the value, not a comment. The predecessor stripped ` #...` before
  // looking for quotes, so `selector: "div #main >> nth=1"` collapsed to `"div` and the
  // banned chord went unreported — verified against main, which exits 0 on that input.
  // A CSS id selector after a descendant combinator is ordinary, so this was a live hole,
  // not a theoretical one.
  const quote = v[0];
  if (quote === '"' || quote === "'") {
    let i = 1;
    let out = '';
    while (i < v.length) {
      const ch = v[i];
      // Only `\"` and `\\` are unescaped — the two that occur in selectors. Any other
      // escape is left verbatim rather than silently turned into its letter (`\\n` -> `n`),
      // which would be this traversal inventing a value YAML never produced.
      if (quote === '"' && ch === '\\' && (v[i + 1] === '"' || v[i + 1] === '\\')) { out += v[i + 1]; i += 2; continue; }
      if (ch === quote) {
        if (quote === "'" && v[i + 1] === "'") { out += "'"; i += 2; continue; }
        return out;                       // closing quote — the rest of the line is comment
      }
      out += ch;
      i += 1;
    }
    return out;                           // unterminated quote: take what there is
  }

  v = v.replace(/[ \t]+#.*$/, '').replace(/[ \t]+$/, '');
  const single = /^'(.*)'$/.exec(v);
  if (single) return single[1].replace(/''/g, "'");
  const double = /^"(.*)"$/.exec(v);
  // A YAML double-quoted scalar carries backslash escapes, so `"a[name=\"x\"]"` is the
  // value `a[name="x"]`. Undoing the two escapes that occur in selectors makes this
  // traversal agree with the YAML-parsed value the element traversal sees — without it
  // the same element yields two different strings and is reported by both channels
  // instead of one. Only `\"` and `\\` are handled: no selector form in the corpus or the
  // grammar uses another escape, and inventing a general unescaper here would be a second
  // partial YAML implementation.
  if (double) return double[1].replace(/\\(["\\])/g, '$1');
  return v;
}

const SELECTOR_LINE = /^[ \t]*selector:[ \t]*(.*)$/;

/**
 * scanMappingText(text, filePath) -> findings with 1-based line numbers.
 *
 * Line-oriented on purpose: it must run without a YAML parser so the linter stays
 * dependency-free, and a line number is the diagnostic #88 asks for. Only `selector:`
 * field values are scanned.
 *
 * **Block and folded scalars are not read** — `selector: >` or `selector: |` followed by
 * an indented value yields no finding, because the value never appears on a `selector:`
 * line. The pure-bash predecessor carried the same limitation and said so; the caveat is
 * restated here because the port initially dropped it. This bounds the LINTER only: the
 * compiler's blocking gate and `bin/e2e-selector-baseline.js` both traverse parsed YAML
 * via `scanElements`, which sees those values correctly. So the failure mode is a lint
 * that passes where a compile blocks, never the reverse.
 */
function scanMappingText(text, filePath) {
  const findings = [];
  const lines = String(text).split('\n');
  for (let i = 0; i < lines.length; i++) {
    const m = SELECTOR_LINE.exec(lines[i]);
    if (!m) continue;
    const selector = normalizeScalar(m[1]);
    if (selector.length === 0) continue;
    for (const classId of classifySelector(selector)) {
      findings.push({
        file: filePath,
        line: i + 1,
        class: classId,
        selector: selector,
        raw: lines[i],
        guidance: guidanceFor(classId),
      });
    }
  }
  return findings;
}

/**
 * scanElements(records) -> findings carrying element identity.
 *
 * `records` are `{mappingFile, page, element, selector}`. The identity is what makes a
 * baseline record survive reformatting (unlike a line number) and still refuse the same
 * banned string pasted onto a different element (unlike a count).
 */
function scanElements(records) {
  const findings = [];
  for (const rec of records || []) {
    if (!rec) continue;
    for (const classId of classifySelector(rec.selector)) {
      findings.push({
        mappingFile: rec.mappingFile,
        page: rec.page,
        element: rec.element,
        class: classId,
        selector: rec.selector,
        guidance: guidanceFor(classId),
        line: rec.line,
      });
    }
  }
  return findings;
}

/**
 * mappingElementRecords(mappingObject, mappingFile) -> the {mappingFile, page, element,
 * selector} records `scanElements` consumes, for EVERY element in a parsed v2 mapping.
 *
 * Shared by the compiler's warning channel and by `bin/e2e-selector-baseline.js`, so the
 * set a baseline can grandfather and the set the compiler warns about are the same set by
 * construction rather than by two similar loops agreeing.
 */
function mappingElementRecords(mappingObject, mappingFile) {
  const records = [];
  const pages = (mappingObject && mappingObject.pages) || {};
  for (const page of Object.keys(pages)) {
    const elements = (pages[page] && pages[page].elements) || {};
    for (const element of Object.keys(elements)) {
      const el = elements[element];
      if (!el || typeof el.selector !== 'string') continue;
      records.push({ mappingFile: mappingFile, page: page, element: element, selector: el.selector });
    }
  }
  return records;
}

/**
 * locateSelectorLine(text, element, selector) -> 1-based line, or null.
 *
 * The element traversal reads parsed YAML and has no line numbers; #88 asks diagnostics to
 * carry one. Rather than write a second partial YAML parser to get it, this searches
 * forward from the element's own key line for the first `selector:` line whose normalized
 * value matches. It returns null rather than guessing when it cannot find one, and a null
 * line is rendered as the element name alone — a missing line number degrades the message,
 * a wrong one misdirects the fix.
 */
function locateSelectorLine(text, element, selector) {
  const lines = String(text).split('\n');
  // A key line is `name:` with nothing but an optional comment after it. Every
  // `selector:` line is attributed to the NEAREST PRECEDING key line — not to a key
  // scanned forwards within a window, which attributed a sibling element's line to an
  // element that had no `selector:` of its own.
  const KEY_LINE = /^[ \t]*([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(#.*)?$/;
  const candidates = [];
  let owner = null;
  for (let i = 0; i < lines.length; i++) {
    const key = KEY_LINE.exec(lines[i]);
    if (key) { owner = key[1]; continue; }
    const sel = SELECTOR_LINE.exec(lines[i]);
    if (sel && owner === element && normalizeScalar(sel[1]) === selector) candidates.push(i + 1);
  }
  // Exactly one match, or nothing. Two pages may define the same element name with the
  // same selector, and there is no way to tell them apart without parsing the document —
  // so this returns null and the caller prints the element without a line. A missing line
  // number degrades a message; a wrong one sends the reader to the wrong element.
  return candidates.length === 1 ? candidates[0] : null;
}

function findingKey(finding) {
  return [
    finding.mappingFile,
    finding.page + '.' + finding.element,
    finding.class,
    finding.selector,
  ].join('\t');
}

/** One tab-separated baseline record for a finding. Terminated by a newline. */
function baselineRecord(finding) {
  return findingKey(finding) + '\n';
}

/**
 * parseBaseline(text) -> Set of record keys.
 *
 * A malformed record throws rather than being skipped. A baseline that silently drops a
 * line it cannot read is a baseline that silently stops grandfathering, and the gate then
 * reds on something the author believes is listed — a failure that reads as a regression
 * in the mapping rather than as a typo in the baseline.
 */
function parseBaseline(text) {
  const keys = new Set();
  const lines = String(text || '').split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim().length === 0 || line.trimStart().startsWith('#')) continue;
    // `\r` is stripped so a baseline checked out with CRLF endings still matches. Without
    // it every record's selector field carries a trailing `\r`, nothing matches, and the
    // compile reds on findings the author believes are listed — a failure that reads like
    // a regression in the mapping rather than a line-ending problem.
    const fields = line.replace(/\r$/, '').split('\t');
    // The first three fields cannot contain a tab (a filename could in principle; none
    // does here, and one would be a worse problem than this). A selector value can, so
    // everything past the third field is rejoined rather than counted as a malformation.
    if (fields.length < 4 || fields.slice(0, 4).some(function (f) { return f.length === 0; })) {
      throw new Error(
        'malformed selector baseline record at line ' + (i + 1) +
        ': expected 4 tab-separated non-empty fields ' +
        '(mapping-file, page.element, class, selector), got ' + fields.length
      );
    }
    keys.add(fields.slice(0, 3).concat(fields.slice(3).join('\t')).join('\t'));
  }
  return keys;
}

/** True when this exact (mapping file, page.element, class, selector) is grandfathered. */
function isGrandfathered(finding, baseline) {
  if (!baseline || baseline.size === 0) return false;
  return baseline.has(findingKey(finding));
}

// ---------------------------------------------------------------------------
// CLI — the implementation `scripts/lint-mapping.sh` execs.
//
// It lives here rather than in the shell script so the ban has one definition
// site. The script keeps the documented interface (argv, exit codes 0/1/2, the
// `path:line: class: rawline` stderr shape) because `test/integration-smoke.sh`
// and consumer `.githooks` read it.
// ---------------------------------------------------------------------------

function lintCli(argv) {
  const mappingFile = argv[0];
  if (!mappingFile || mappingFile === '--help' || mappingFile === '-h') {
    // Same shape the pure-bash `usage()` printed, generated from the table so it cannot
    // drift from what is actually enforced — the previous version restated the classes
    // by hand in three places.
    const lines = ['Usage: lint-mapping.sh <mapping-yaml-path>', '', '  mapping-yaml-path  Path to the e2e mapping YAML file to lint.', '', '  Checks selector field values (only) for banned tokens:'];
    for (const cls of BANNED_CLASSES) {
      lines.push('    - ' + cls.id.padEnd(18) + cls.description + ' — ' + cls.guidance);
    }
    lines.push('');
    lines.push('  role=<r>[name=...] and bare text= are NATIVE forms (translated by');
    lines.push('  compiler/lib/selector-translate.js) and are not banned.');
    lines.push('');
    process.stderr.write(lines.join('\n') + '\n');
    return 1;
  }
  let text;
  try {
    text = require('node:fs').readFileSync(mappingFile, 'utf8');
  } catch (e) {
    process.stderr.write('Error: file not found: ' + mappingFile + '\n');
    return 1;
  }
  const findings = scanMappingText(text, mappingFile);
  for (const f of findings) {
    process.stderr.write(f.file + ':' + f.line + ': ' + f.class + ': ' + f.raw + '\n');
  }
  if (findings.length > 0) {
    process.stderr.write(
      'lint-mapping: ' + mappingFile + ' — FAIL (' + findings.length + ' banned token(s) found)\n'
    );
    return 2;
  }
  process.stdout.write('lint-mapping: ' + mappingFile + ' — OK\n');
  return 0;
}

if (require.main === module) {
  process.exitCode = lintCli(process.argv.slice(2));
}

module.exports = {
  BANNED_CLASSES: BANNED_CLASSES,
  mappingElementRecords: mappingElementRecords,
  locateSelectorLine: locateSelectorLine,
  classifySelector: classifySelector,
  guidanceFor: guidanceFor,
  scanMappingText: scanMappingText,
  scanElements: scanElements,
  parseBaseline: parseBaseline,
  isGrandfathered: isGrandfathered,
  baselineRecord: baselineRecord,
};
