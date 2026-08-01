#!/usr/bin/env node
'use strict';

/**
 * e2e-selector-baseline — print grandfathered selector-baseline records to stdout.
 *
 * Usage:
 *   e2e-selector-baseline <mapping.yaml> [<mapping.yaml> ...]
 *
 * Adopting a baseline is a human act that lands in a diff:
 *
 *   node bin/e2e-selector-baseline.js .claude/e2e/mappings/*.yaml \
 *     > .claude/e2e/selector-baseline.tsv
 *
 * This binary GATES NOTHING and writes NOTHING. It is deliberately separate from
 * `e2e-compile` so the gate has no code path that produces its own baseline — an
 * `--update-baseline` flag runnable inside a build loop turns "fix the selector" into
 * "make the check shut up", which is the failure this separation exists to prevent
 * (#88, EM condition 3).
 *
 * What stdout-only does and does not buy, stated plainly: an agent can redirect stdout as
 * easily as a person can, so this does not enforce human authorship. What it buys is that
 * widening a baseline shows up as a reviewable diff rather than as a side effect of
 * compiling.
 *
 * Scope: every banned selector in the mapping FILE, not only the ones some flow currently
 * resolves. A banned selector on an element that already exists is the pre-existing debt
 * the baseline is for. The cost — a future flow that starts resolving one of those
 * elements compiles green — is bounded by the compiler printing a distinct
 * "this flow RESOLVES a grandfathered banned selector" warning on every such run.
 */

const fs = require('node:fs');
const path = require('node:path');
const yaml = require('js-yaml');

const policy = require('../compiler/lib/selector-policy.js');

function usage(stream) {
  stream.write('Usage: e2e-selector-baseline <mapping.yaml> [<mapping.yaml> ...]\n');
  stream.write('\n');
  stream.write('  Prints one tab-separated record per banned selector found, to stdout:\n');
  stream.write('    <mapping-file>\\t<page>.<element>\\t<class>\\t<selector>\\n');
  stream.write('\n');
  stream.write('  Redirect it yourself; this command never writes a file.\n');
}

/** Flatten a v2 mapping into the {mappingFile, page, element, selector} records the policy scans. */
function elementRecords(mappingObject, mappingFile) {
  const records = [];
  const pages = (mappingObject && mappingObject.pages) || {};
  for (const pageName of Object.keys(pages)) {
    const elements = (pages[pageName] && pages[pageName].elements) || {};
    for (const elementName of Object.keys(elements)) {
      const el = elements[elementName];
      if (!el || typeof el.selector !== 'string') continue;
      records.push({
        mappingFile: mappingFile,
        page: pageName,
        element: elementName,
        selector: el.selector,
      });
    }
  }
  return records;
}

function main(argv) {
  if (argv.length === 0 || argv.indexOf('--help') !== -1 || argv.indexOf('-h') !== -1) {
    usage(argv.length === 0 ? process.stderr : process.stdout);
    return argv.length === 0 ? 1 : 0;
  }

  const out = [];
  for (const mappingPath of argv) {
    let doc;
    try {
      doc = yaml.load(fs.readFileSync(mappingPath, 'utf8'));
    } catch (e) {
      process.stderr.write('Error: cannot read mapping ' + mappingPath + ': ' + e.message + '\n');
      return 1;
    }
    const records = elementRecords(doc, path.basename(mappingPath));
    for (const finding of policy.scanElements(records)) {
      out.push(policy.baselineRecord(finding));
    }
  }

  if (out.length > 0) {
    process.stdout.write('# selector baseline — grandfathered banned selectors\n');
    process.stdout.write('# regenerate with: node bin/e2e-selector-baseline.js <mapping.yaml>...\n');
    process.stdout.write('# a record is <mapping-file> <page>.<element> <class> <selector>, tab-separated\n');
    process.stdout.write(out.join(''));
  }
  process.stderr.write('e2e-selector-baseline: ' + out.length + ' record(s) from ' + argv.length + ' mapping file(s)\n');
  return 0;
}

if (require.main === module) {
  process.exitCode = main(process.argv.slice(2));
}

module.exports = { elementRecords: elementRecords };
