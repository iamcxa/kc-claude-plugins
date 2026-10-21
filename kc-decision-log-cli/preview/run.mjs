// DISPOSABLE: operates the preview CLI over the fictional repository and checks each run against expectations written by hand
// (not produced by the CLI). Usage: ADR_LINT=<path to adr_lint.py> node run.mjs [--transcript <file>]
import { spawnSync, execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from './fixture.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const { dir, d0, d1, d2, d3 } = build();
const work = mkdtempSync(join(tmpdir(), 'kcdl-run-'));
const labels = new Map();
const config = (patch = {}) => {
  const path = join(work, `cfg-${Math.random().toString(36).slice(2)}.json`);
  labels.set(path, `$CONFIG[${Object.entries(patch).map(([k, v]) => `${k}=${v}`).join(',')}]`);
  writeFileSync(path, JSON.stringify({ bindings: [{ id: 'mira', repository: 'example/mira-decisions', clone_path: dir, adr_root: 'docs/adr', ...patch }] }));
  return path;
};
const cfg = config();
const lines = [], failures = [];
const note = text => { lines.push(text); console.log(text); };
let n = 0;
function scenario(title, args, { exit = 0, env = {}, check = () => {}, show = true, show_json = null } = {}) {
  const shown = args.map(a => (a === d0 ? '$D0' : a === d1 ? '$D1' : a === d2 ? '$D2' : a === d3 ? '$D3' : a === cfg ? '$CONFIG' : labels.get(a) ?? a));
  const done = spawnSync('node', [join(here, 'cli.mjs'), ...args], { encoding: 'utf8', env: { ...process.env, ...env } });
  let parsed = null;
  try { parsed = JSON.parse(done.stdout); } catch { /* human output */ }
  const problems = [];
  if (done.status !== exit) problems.push(`exit ${done.status}, expected ${exit}`);
  if (args.includes('human') && exit !== 0 && exit !== 6 && (done.stdout.trim() || !done.stderr.trim())) problems.push('a human refusal must be on stderr only');
  try { check(parsed ?? (done.stdout || done.stderr), done); } catch (error) { problems.push(error.message); }
  note(`\n### ${++n}. ${title}\n$ kc-decision-log ${shown.join(' ')}${Object.keys(env).length ? `   (env ${Object.keys(env).join(',')} set)` : ''}`);
  if (show) {
    let shownText;
    try { shownText = show_json ? `${JSON.stringify(show_json(parsed), null, 2)}\n(subset of the JSON fields, chosen by the transcript)` : done.stdout.trimEnd(); } catch { shownText = done.stdout.trimEnd(); }
    note(shownText);
    if (done.stderr.trim()) note(`[stderr]\n${done.stderr.trimEnd()}`);
  }
  note(`exit ${done.status}   ${problems.length ? `MISMATCH: ${problems.join('; ')}` : 'as expected'}`);
  failures.push(...problems.map(p => `${n}. ${title}: ${p}`));
}
const eq = (a, b, what) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${what}: got ${JSON.stringify(a)}, expected ${JSON.stringify(b)}`); };
const oracleDigest = (commit, path) => `sha256:${createHash('sha256').update(execFileSync('git', ['-C', dir, 'cat-file', 'blob', `${commit}:${path}`])).digest('hex')}`;
const base = (cmd, commit, id, extra = []) => [cmd, '--config', cfg, '--binding', 'mira', '--commit', commit, '--id', id, ...extra];

note(`Fictional repository: ${dir}\nD0 = ${d0}\nD1 = ${d1}\nD2 = ${d2} (branch main now points at D2: ${execFileSync('git', ['-C', dir, 'rev-parse', 'main'], { encoding: 'utf8' }).trim() === d2})\nD3 = ${d3} (side branch off D1)`);

note('\n## Reading one ruling at an exact commit (AC-2)');
const p3 = 'docs/adr/0003-reports-are-weekly.md';
scenario('read 0003 at D0 although main has moved on, JSON, digest checked against git cat-file bytes', base('read', d0, '0003'), {
  show_json: r => ({ ...r, text: `(${r.text.length} chars, omitted here)` }),
  check: r => { eq(r.reference.commit, d0, 'commit'); eq(r.reference.digest, oracleDigest(d0, p3), 'digest'); eq(r.status.written, 'Accepted', 'status'); },
});
scenario('read 0003 at D0, human', base('read', d0, '0003', ['--format', 'human']), { check: out => { if (!out.includes(oracleDigest(d0, p3))) throw new Error('digest missing'); } });
scenario('read 0003 at D1: new bytes, new digest, Status as written', base('read', d1, '0003'), {
  show_json: r => ({ reference: r.reference, status: r.status }),
  check: r => { eq(r.reference.digest, oracleDigest(d1, p3), 'digest'); eq(r.status.written, 'Superseded by 0004', 'status'); },
});
scenario('read 0012 (CRLF file) in human mode: CR is shown escaped, digest is of the raw bytes', base('read', d1, '0012', ['--format', 'human']), {
  check: out => { if (!out.includes(oracleDigest(d1, 'docs/adr/0012-crlf-record.md')) || !out.includes('\\r')) throw new Error('raw digest or escaped CR missing'); },
});

note('\n## Handoff comparison (expected digest)');
scenario('expected digest matches', base('read', d0, '0003', ['--expect-digest', oracleDigest(d0, p3)]), { show_json: r => ({ ok: r.ok, digest: r.reference.digest }) });
scenario('expected digest from D0 compared at D1: mismatch stops with exit 4', base('read', d1, '0003', ['--expect-digest', oracleDigest(d0, p3)]), { exit: 4, check: r => eq(r.reason, 'digest_mismatch', 'reason') });

scenario('expected digest matches, human: the check is stated', base('read', d0, '0003', ['--expect-digest', oracleDigest(d0, p3), '--format', 'human']), { show: true, check: out => { if (!out.includes('Digest check')) throw new Error('no Digest check row'); } });
scenario('digest mismatch, human: one REFUSED block on stderr, exit 4', base('read', d1, '0003', ['--expect-digest', oracleDigest(d0, p3), '--format', 'human']), { exit: 4, check: out => { if (!out.startsWith('REFUSED digest_mismatch')) throw new Error('no REFUSED line on stderr'); } });

note('\n## What counts as effective (AC-3)');
const verdict = (id, commit = d0) => scenario(`effective ${id}`, base('effective', commit, id, ['--format', 'human']), {});
const want = (id, resolution, reason, effective_id = null, commit = d0) => scenario(`effective ${id} at ${commit === d0 ? 'D0' : commit === d1 ? 'D1' : commit === d2 ? 'D2' : 'D3'}`, base('effective', commit, id),
  { show_json: r => ({ status: r.status, decision_key: r.decision_key, resolution: r.resolution, reason: r.reason, blocking: r.blocking, chain: r.chain, effective_id: r.effective_id, is_effective: r.is_effective }),
    check: r => { eq([r.resolution, r.reason, r.effective_id], [resolution, reason, effective_id], 'verdict'); } });
want('0003', 'resolved', null, '0003');
want('0003', 'resolved', null, '0004', d1);
want('0001', 'resolved', null, '0001', d1);
want('0002', 'unresolved', 'no_explicit_accepted_target');
want('0005', 'unresolved', 'decision_key_missing');
want('0006', 'unresolved', 'conflicting_accepted_records');
want('0008', 'unresolved', 'missing_target');
want('0009', 'unresolved', 'cycle');
want('0011', 'unresolved', 'record_invalid');
want('0014', 'unresolved', 'legacy_record');
scenario('effective 0003 at D1, human', base('effective', d1, '0003', ['--format', 'human']), { check: out => { if (!out.includes('NOT EFFECTIVE') || !out.includes('ADR 0004')) throw new Error('superseded not stated first'); } });
scenario('effective 0003 at D1, JSON in full (same envelope as read plus the resolution fields)', base('effective', d1, '0003'), { check: r => eq([r.ok, r.command, r.status.written, r.resolution, r.effective_id, r.is_effective, r.reference.adr_id], [true, 'effective', 'Superseded by 0004', 'resolved', '0004', false, '0003'], 'envelope') });
scenario('effective 0001 at D1, human: this record is the ruling in force', base('effective', d1, '0001', ['--format', 'human']), { check: out => { if (!out.includes('EFFECTIVE: this record')) throw new Error('not effective line'); } });
scenario('effective with --expect-digest: compared with the requested record (0003 at D1), not the ruling in force', base('effective', d1, '0003', ['--expect-digest', oracleDigest(d1, p3), '--format', 'human']), { check: out => { if (!out.includes('Digest check') || !out.includes('NOT EFFECTIVE')) throw new Error('digest check or answer missing'); } });
scenario('effective --expect-digest with the digest of the ruling in force: refused, because it is not the requested record', base('effective', d1, '0003', ['--expect-digest', oracleDigest(d1, 'docs/adr/0004-reports-are-daily.md')]), { exit: 4, check: r => eq(r.reason, 'digest_mismatch', 'reason') });
scenario('effective --require-effective on a superseded record: exit 6, answer still printed', base('effective', d1, '0003', ['--require-effective', '--format', 'human']), { exit: 6, check: out => { if (!out.includes('NOT EFFECTIVE')) throw new Error('answer missing'); } });
scenario('effective --require-effective on an unresolved record: exit 6', base('effective', d0, '0005', ['--require-effective', '--format', 'human']), { exit: 6 });
scenario('effective --require-effective on the ruling in force: exit 0', base('effective', d1, '0004', ['--require-effective', '--format', 'human']), { check: out => { if (!out.includes('EFFECTIVE: this record')) throw new Error('not effective'); } });
scenario('effective 0002 (Proposed), human', base('effective', d0, '0002', ['--format', 'human']), { check: out => { if (!out.includes('not Accepted')) throw new Error('plain reason missing'); } });
scenario('effective 0011 (fails the format check), human', base('effective', d0, '0011', ['--format', 'human']), { check: out => { if (!out.includes('NOT dev2-valid: date')) throw new Error('format verdict missing'); } });
scenario('effective 0014 (Legacy), human', base('effective', d0, '0014', ['--format', 'human']), { check: out => { if (!out.includes('legacy (not checked')) throw new Error('legacy line missing'); } });
scenario('effective 0005, human: unresolved is exit 0, not a tool failure', base('effective', d0, '0005', ['--format', 'human']), { check: out => { if (!out.includes('UNRESOLVED: the record has no Decision key') || !out.includes('(decision_key_missing)')) throw new Error('plain reason then code expected'); } });

note('\n## Refusals (AC-1)');
scenario('short commit, human: one REFUSED block on stderr, exit 2', base('read', d0.slice(0, 12), '0001', ['--format', 'human']), { exit: 2, check: out => { if (!out.startsWith('REFUSED commit_not_full') || !out.includes(d0.slice(0, 12))) throw new Error('refusal text'); } });
scenario('two files share 0016, human', base('read', d0, '0016', ['--format', 'human']), { exit: 2, check: out => { if (!out.includes('0016-twin-a.md') || !out.includes('0016-twin-b.md')) throw new Error('paths missing'); } });
scenario('commit that does not exist, human', base('read', 'a'.repeat(40), '0001', ['--format', 'human']), { exit: 3, check: out => { if (!out.startsWith('REFUSED commit_not_found') || !out.includes('a'.repeat(40))) throw new Error('refusal text'); } });
scenario('wrong repository, human', ['read', '--config', config({ repository: 'example/other-decisions' }), '--binding', 'mira', '--commit', d0, '--id', '0001', '--format', 'human'], { exit: 3, check: out => { if (!out.includes('example/other-decisions') || !out.includes('example/mira-decisions')) throw new Error('both repositories named'); } });
scenario('wrong ADR path, human', ['read', '--config', config({ adr_root: 'docs/decisions' }), '--binding', 'mira', '--commit', d0, '--id', '0001', '--format', 'human'], { exit: 3, check: out => { if (!out.includes('docs/decisions')) throw new Error('adr_root named'); } });
scenario('ID that does not exist, human', base('read', d0, '0042', ['--format', 'human']), { exit: 2, check: out => { if (!out.includes('0042')) throw new Error('id named'); } });
scenario('binding that is not configured, human: the configured names are listed', ['read', '--config', cfg, '--binding', 'ghost', '--commit', d0, '--id', '0001', '--format', 'human'], { exit: 2, check: out => { if (!out.includes('mira')) throw new Error('configured list'); } });
for (const [what, args, problem] of [
  ['no --id', ['read', '--config', cfg, '--binding', 'mira', '--commit', d0], '--id is four digits'],
  ['id that is not four digits', ['read', '--config', cfg, '--binding', 'mira', '--commit', d0, '--id', '3'], '--id is four digits'],
  ['no --config', ['read', '--binding', 'mira', '--commit', d0, '--id', '0001'], '--config is required'],
  ['unknown --format', ['read', '--config', cfg, '--binding', 'mira', '--commit', d0, '--id', '0001', '--format', 'yaml'], '--format is json or human'],
  ['unknown flag --path', ['read', '--config', cfg, '--binding', 'mira', '--commit', d0, '--id', '0001', '--path', 'docs/adr/0001-demo-site-is-team-login-first.md'], 'unknown flag --path'],
  ['--require-effective on read', ['read', '--config', cfg, '--binding', 'mira', '--commit', d0, '--id', '0001', '--require-effective'], '--require-effective belongs to effective'],
]) scenario(`usage error: ${what}`, args, { exit: 2, check: r => { eq(r.reason, 'bad_arguments', 'reason'); if (!r.detail.problem.includes(problem)) throw new Error(`problem: ${r.detail.problem}`); } });
scenario('malformed --expect-digest', base('read', d0, '0001', ['--expect-digest', 'abc']), { exit: 2, check: r => eq(r.reason, 'bad_expected_digest', 'reason') });
scenario('binding that is not configured', ['read', '--config', cfg, '--binding', 'ghost', '--commit', d0, '--id', '0001'], { exit: 2, check: r => eq(r.reason, 'binding_not_configured', 'reason') });
scenario('short commit', base('read', d0.slice(0, 12), '0001'), { exit: 2, check: r => eq(r.reason, 'commit_not_full', 'reason') });
scenario('ref name instead of a commit', base('read', 'main', '0001'), { exit: 2, check: r => eq(r.reason, 'commit_not_full', 'reason') });
scenario('full-length commit that does not exist', base('read', 'a'.repeat(40), '0001'), { exit: 3, check: r => eq(r.reason, 'commit_not_found', 'reason') });
scenario('wrong repository in the binding', ['read', '--config', config({ repository: 'example/other-decisions' }), '--binding', 'mira', '--commit', d0, '--id', '0001'], { exit: 3, check: r => eq(r.reason, 'repository_mismatch', 'reason') });
scenario('wrong ADR path in the binding', ['read', '--config', config({ adr_root: 'docs/decisions' }), '--binding', 'mira', '--commit', d0, '--id', '0001'], { exit: 3, check: r => eq(r.reason, 'adr_root_missing', 'reason') });
scenario('adr_root that climbs out of the repository', ['read', '--config', config({ adr_root: '../elsewhere' }), '--binding', 'mira', '--commit', d0, '--id', '0001'], { exit: 2, check: r => eq(r.reason, 'invalid_binding', 'reason') });
scenario('two files share the number 0016: refused, both paths named; other IDs unaffected (see 0001 at D1 above)', base('read', d0, '0016'), { exit: 2, check: r => eq([r.reason, r.detail.paths], ['ambiguous_id', ['docs/adr/0016-twin-a.md', 'docs/adr/0016-twin-b.md']], 'ambiguous') });
scenario('ID that does not exist', base('read', d0, '0042'), { exit: 2, check: r => eq(r.reason, 'unknown_id', 'reason') });
const decoy = mkdtempSync(join(tmpdir(), 'kcdl-decoy-')); execFileSync('git', ['-C', decoy, 'init', '-q']);
scenario('caller exports GIT_DIR of another repository: ignored, same digest as scenario 1', base('read', d0, '0003'), {
  env: { GIT_DIR: join(decoy, '.git') }, show_json: r => ({ ok: r.ok, digest: r.reference.digest }), check: r => eq(r.reference.digest, oracleDigest(d0, p3), 'digest'),
});

note('\n## A record that cannot be read at all (D2 adds a file with invalid UTF-8)');
scenario('read the unreadable record: refused, no digest of substituted bytes', base('read', d2, '0015'), { exit: 5, check: r => eq([r.reason, r.detail.why], ['unsupported_record', 'invalid_utf8'], 'reason') });
scenario('read the unreadable record, human', base('read', d2, '0015', ['--format', 'human']), { exit: 5, check: out => { if (!out.startsWith('REFUSED unsupported_record')) throw new Error('refusal text'); } });
scenario('read a normal record in the same view: still works', base('read', d2, '0001'), { show_json: r => ({ ok: r.ok, digest: r.reference.digest }), check: r => eq(r.reference.digest, oracleDigest(d2, 'docs/adr/0001-demo-site-is-team-login-first.md'), 'digest') });
want('0001', 'unresolved', 'view_has_unreadable_record', null, d2);
scenario('effective 0001 at D2, human: the blocking file is named', base('effective', d2, '0001', ['--format', 'human']), { check: out => { if (!out.includes('Blocking') || !out.includes('0015-not-utf8.md')) throw new Error('blocking record not named'); } });
note('\n## An Accepted record whose Decision key cannot be placed (D3, a side commit after D1, adds ADR 0017 with two key lines)');
want('0001', 'unresolved', 'view_has_unplaceable_record', null, d3);
scenario('effective 0001 at D3, human: the blocking file is named', base('effective', d3, '0001', ['--format', 'human']), { check: out => { if (!out.includes('Blocking') || !out.includes('0017-two-keys.md')) throw new Error('blocking record not named'); } });

note('\n## Skipped files and byte-order sort');
scenario('effective view lists what it did not read as ADRs (README, index, template are skipped silently; the rest are named)', base('effective', d0, '0001'), {
  show_json: r => r.view, check: r => eq(r.view.nonconforming, ['Zebra.md', 'alpha.md', 'notes.md'], 'byte order'),
});

note('\n## Format oracle: adr_lint.py on the same D1 tree');
const tree = mkdtempSync(join(tmpdir(), 'kcdl-tree-'));
execFileSync('sh', ['-c', `git -C '${dir}' archive ${d1} docs/adr | tar -x -C '${tree}'`]);
const lint = spawnSync('python3', [process.env.ADR_LINT ?? 'adr_lint.py', join(tree, 'docs/adr')], { encoding: 'utf8' });
const lintFiles = [...new Set(lint.stdout.split('\n').map(l => /^([^:]+\.md):/.exec(l)?.[1]).filter(Boolean))].sort((a, b) => Buffer.compare(Buffer.from(a), Buffer.from(b)));
const { loadView } = await import('./cli.mjs');
const ours = loadView({ clone: dir, root: 'docs/adr', repository: 'example/mira-decisions' }, d1).flagged;
note(`adr_lint.py exit ${lint.status}; files it flags:  ${lintFiles.join(', ')}\npreview view flags:               ${ours.join(', ')}`);
if (JSON.stringify(lintFiles) !== JSON.stringify(ours)) failures.push('lint parity: file sets differ');
note(JSON.stringify(lintFiles) === JSON.stringify(ours) ? 'same set: as expected' : 'MISMATCH');

note(`\n${failures.length ? `FAILURES:\n${failures.join('\n')}` : `All ${n} scenarios and the lint comparison matched their hand-written expectations.`}`);
const at = process.argv.indexOf('--transcript');
if (at > 0) { mkdirSync(dirname(process.argv[at + 1]), { recursive: true }); writeFileSync(process.argv[at + 1], lines.join('\n') + '\n'); }
process.exitCode = failures.length ? 1 : 0;
