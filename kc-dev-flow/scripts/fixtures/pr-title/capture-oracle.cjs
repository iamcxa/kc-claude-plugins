#!/usr/bin/env node
'use strict';

// Re-derive release-please-verdicts.tsv from the installed release-please
// parser. Run after `npm ci` in scripts/fixtures/release-please-runtime/
// (repo root, not under kc-dev-flow/):
//
//   node kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs > \
//     kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv
//
// A stop condition, not routine maintenance -- re-run only on a
// release-please version bump or a reported adopter skew (see
// "The title rule's oracle" in pr-merge-extension.md). Declared machine
// dependency: this script needs Node and the runtime's installed
// node_modules; check-pr-title.py and the committed TSV need neither.

const path = require('path');

const RUNTIME_ROOT = path.resolve(
  __dirname, '..', '..', '..', '..',
  'scripts', 'fixtures', 'release-please-runtime'
);
const { parseConventionalCommits } = require(
  path.join(RUNTIME_ROOT, 'node_modules', 'release-please', 'build', 'src', 'commit.js')
);
const releasePleaseVersion = require(
  path.join(RUNTIME_ROOT, 'node_modules', 'release-please', 'package.json')
).version;

// Silences release-please's default logger (its CheckpointLogger enables
// debug output by default), whose parse-failure noise otherwise interleaves
// with the TSV rows on stdout.
const quietLogger = {
  error() {},
  warn() {},
  info() {},
  debug() {},
  trace() {},
};

const SUBJECTS = [
  ['feat(): x', 'empty scope; a (\\w+)(\\(.*\\))?!?: regex would pass it -- the dangerous direction'],
  ['Revert "feat: x"', 'reverts read as prose, not as a type'],
  ['feat x', 'no colon delimiter'],
  ['Add a thing', 'no conventional-commit type prefix'],
  ['feat:x', 'no space after the colon is still a commit'],
  ['FEAT: x', 'the type is not case-normalised before parsing'],
  ['feat: ', 'an empty description still parses'],
  ['  feat: x', 'leading whitespace is tolerated'],
  ['feat(two words): x', 'scope content is unconstrained'],
  ['feat(a)!: x', 'breaking marker'],
  ['fix(a,b): x', 'comma in scope is unconstrained content'],
  ['chore(deps): bump x', 'refusing a correctly non-releasing type moves the judgement call back to draft time'],
  ['docs(dev): state the rule', 'same reasoning as chore'],
];

const today = new Date().toISOString().slice(0, 10);

const header = [
  '# release-please-verdicts.tsv',
  `# Captured ${today} from release-please ${releasePleaseVersion}, this repository's own`,
  "# lockfile at scripts/fixtures/release-please-runtime/ (run `npm ci` there",
  '# first). Agreement with subspace-relay\'s 17.11.1 pin on these rows is a',
  '# separate 2026-09-12 observation, recorded in',
  '# kc-dev-flow/references/pr-merge-extension.md, "The title rule\'s oracle" --',
  "# not re-derived by this file's capture command.",
  '# Re-derive after any release-please version bump, or on a reported adopter',
  '# skew, with:',
  '#   node kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs > \\',
  '#     kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv',
  '# columns: subject<TAB>verdict(parses|drops)<TAB>reason',
];

for (const line of header) {
  process.stdout.write(line + '\n');
}
for (const [subject, reason] of SUBJECTS) {
  const commits = [{ sha: 'oracle', message: subject, files: [], pullRequest: undefined }];
  const parsed = parseConventionalCommits(commits, quietLogger);
  const verdict = parsed.length > 0 ? 'parses' : 'drops';
  process.stdout.write(`${subject}\t${verdict}\t${reason}\n`);
}
