#!/usr/bin/env node
// DISPOSABLE design preview of the kc-decision-log read path. Not the product, not a base for it.
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

export const TOOL = { name: 'kc-decision-log', version: '0.1.0-preview', format_baseline: 'dev2 adr_lint.py' };
const NAME = /^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$/;
const SKIP = new Set(['README.md', 'index.md', 'template.md']);
const SECTIONS = ['Status', 'Context', 'Decision', 'Consequences'];
const STATUS = /^(Proposed|Accepted|Deprecated|Superseded by (\d{4}))$/;
const FULL_COMMIT = /^(?:[0-9a-f]{40}|[0-9a-f]{64})$/;
const MAX_BLOB = 1 << 20;
const PYWS = '\\t\\n\\v\\f\\r \\x1c-\\x1f\\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000';
const strip = s => s.replace(new RegExp(`^[${PYWS}]+|[${PYWS}]+$`, 'g'), '');
const bytewise = (a, b) => Buffer.compare(Buffer.from(a), Buffer.from(b));

export class Refusal extends Error {
  constructor(exit, reason, extra = {}) { super(reason); this.exit = exit; this.reason = reason; this.extra = extra; }
}

const GIT_ENV = { ...Object.fromEntries(Object.entries(process.env).filter(([k]) => !k.startsWith('GIT_'))),
  GIT_NO_REPLACE_OBJECTS: '1', GIT_NO_LAZY_FETCH: '1', GIT_OPTIONAL_LOCKS: '0', GIT_TERMINAL_PROMPT: '0' };
function git(clone, args, reason = 'source_unavailable') {
  try {
    return execFileSync('git', ['-C', clone, ...args], { env: GIT_ENV, timeout: 10_000, maxBuffer: MAX_BLOB + 4096, stdio: ['ignore', 'pipe', 'ignore'] });
  } catch { throw new Refusal(3, reason); }
}

export function loadBinding(configPath, id) {
  let config;
  try { config = JSON.parse(readFileSync(configPath, 'utf8')); } catch { throw new Refusal(2, 'config_unreadable', { config: String(configPath) }); }
  const binding = (config.bindings ?? []).find(b => b.id === id);
  if (!binding) throw new Refusal(2, 'binding_not_configured', { configured: (config.bindings ?? []).map(b => b.id) });
  const root = String(binding.adr_root ?? '').replace(/\/+$/, '');
  if (!/^[\w.-]+\/[\w.-]+$/.test(binding.repository ?? '') || !String(binding.clone_path ?? '').startsWith('/')
      || !root || root.startsWith('/') || root.split('/').some(s => s === '..' || s === '.' || s === '')) throw new Refusal(2, 'invalid_binding', { binding: String(id), adr_root: String(binding.adr_root ?? '') });
  return { id: binding.id, repository: binding.repository, clone: binding.clone_path, root };
}

export function openCommit(binding, commit) {
  if (!FULL_COMMIT.test(commit ?? '')) throw new Refusal(2, 'commit_not_full', { received: String(commit ?? '') });
  let url = '';
  try { url = git(binding.clone, ['config', '--get', 'remote.origin.url']).toString().trim(); } catch { /* no origin */ }
  const found = url.replace(/\.git$/, '').split(/[/:]/).slice(-2).join('/');
  if (found.toLowerCase() !== binding.repository.toLowerCase()) throw new Refusal(3, 'repository_mismatch', { configured: binding.repository, origin: found || '(no origin)' });
  let seen = '';
  try { seen = git(binding.clone, ['rev-parse', '--verify', '--quiet', `${commit}^{commit}`]).toString().trim(); } catch { /* absent */ }
  if (seen !== commit) throw new Refusal(3, 'commit_not_found', { commit });
  let kind = '';
  try { kind = git(binding.clone, ['cat-file', '-t', `${commit}:${binding.root}`]).toString().trim(); } catch { /* absent */ }
  if (kind !== 'tree') throw new Refusal(3, 'adr_root_missing', { adr_root: binding.root, commit });
}

function unfence(lines) {
  let fence = null;
  return lines.map(line => {
    const marker = /^ {0,3}(`{3,}|~{3,})/.exec(line)?.[1];
    if (marker && !fence) { fence = marker; return ''; }
    if (fence) {
      if (marker?.[0] === fence[0] && marker.length >= fence.length && /^ {0,3}(`{3,}|~{3,})[ \t]*$/.test(line)) fence = null;
      return '';
    }
    return line;
  });
}

// Format verdict = adr_lint.py's per-file checks, ported without being stricter. Key and Status extraction are separate.
export function parseRecord(name, number, text) {
  const lines = text.replace(/\r\n?/g, '\n').split('\n'), body = lines.join('\n');
  const record = { number, name, legacy: false, errors: [], status_written: '', state: null, superseded_by: null, key: null, key_error: null };
  const sections = new Map(), order = [];
  let current = null;
  for (const line of lines) {
    if (line.startsWith('## ')) { current = strip(line.slice(3)); order.push(current); sections.set(current, []); }
    else if (current !== null) sections.get(current).push(line);
  }
  const statusLines = sections.get('Status') ?? [];
  record.status_written = strip(statusLines.join('\n'));
  const first = strip(statusLines.find(l => strip(l)) ?? '');
  const state = STATUS.exec(first);
  record.state = state ? state[1].startsWith('Superseded') ? 'Superseded' : state[1] : null;
  record.superseded_by = state?.[2] ?? null;
  if (/^Status: Legacy\b/m.test(lines.slice(0, 30).join('\n'))) { record.legacy = true; return record; }
  const title = /^# (\d+)\. \S/.exec(lines.find(l => strip(l)) ?? '');
  if (!title || Number(title[1]) !== Number(number)) record.errors.push('title');
  if (!/^Date: \d{4}-\d{2}-\d{2}$/m.test(body.split('\n## ')[0])) record.errors.push('date');
  if (order.join('|') !== SECTIONS.join('|')) record.errors.push('sections');
  for (const s of SECTIONS) if (!strip((sections.get(s) ?? []).join(''))) record.errors.push(`empty_${s.toLowerCase()}`);
  if (!state) record.errors.push('status');
  const decision = (sections.get('Decision') ?? []).join('\n');
  for (const label of ['**Words:**', '**Options considered:**']) if (!decision.includes(label)) record.errors.push(`missing_${label.replace(/\W/g, '').toLowerCase()}`);
  const keyLines = unfence(lines).filter(l => l.startsWith('**Decision key:**'));
  const keyMatch = keyLines.length === 1 ? /^\*\*Decision key:\*\* ([a-z0-9]+(?:-[a-z0-9]+)*)$/.exec(keyLines[0]) : null;
  if (keyMatch) record.key = keyMatch[1]; else if (keyLines.length) record.key_error = keyLines.length > 1 ? 'duplicate' : 'malformed';
  return record;
}

export function loadView(binding, commit) {
  openCommit(binding, commit);
  const listing = git(binding.clone, ['ls-tree', '-z', commit, `${binding.root}/`]).toString('utf8').split('\0').filter(Boolean);
  const view = { records: [], skipped: [], nonconforming: [], unreadable: [] };
  const decoder = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
  for (const entry of listing) {
    const [meta, path] = entry.split('\t'), [mode, type, oid] = meta.split(' ');
    const base = path.slice(binding.root.length + 1);
    if (type === 'tree' || !base.endsWith('.md')) continue;
    if (SKIP.has(base)) { view.skipped.push(base); continue; }
    const match = NAME.exec(base);
    if (!match) { view.nonconforming.push(base); continue; }
    const record = { number: match[1], name: base, path };
    try {
      if (!mode.startsWith('100')) throw Error('unsupported_mode');
      if (Number(git(binding.clone, ['cat-file', '-s', oid]).toString()) > MAX_BLOB) throw Error('too_large');
      const raw = git(binding.clone, ['cat-file', 'blob', oid]);
      Object.assign(record, { raw, digest: `sha256:${createHash('sha256').update(raw).digest('hex')}`, text: decoder.decode(raw) });
      Object.assign(record, parseRecord(base, match[1], record.text));
      view.records.push(record);
    } catch (error) { view.unreadable.push({ path, why: ['unsupported_mode', 'too_large'].includes(error.message) ? error.message : error instanceof Refusal ? 'git_failed' : 'invalid_utf8' }); }
  }
  view.records.sort((a, b) => bytewise(a.path, b.path));
  view.nonconforming.sort(bytewise);
  const numbers = new Map();
  for (const r of view.records) numbers.set(r.number, [...(numbers.get(r.number) ?? []), r]);
  view.byNumber = numbers;
  view.flagged = [...new Set([
    ...view.records.filter(r => r.errors.length || (r.superseded_by && !numbers.has(r.superseded_by))).map(r => r.name),
    ...[...numbers.values()].filter(group => group.length > 1).flatMap(group => group.slice(1)).map(r => r.name), ...view.nonconforming])].sort(bytewise);
  return view;
}

export function effective(view, id) {
  const group = view.byNumber.get(id), no = (reason, chain = [], extra = {}) => ({ resolution: 'unresolved', reason, chain, effective_id: null, ...extra });
  const origin = group[0];
  if (view.unreadable.length) return no('view_has_unreadable_record', [], { blocking: view.unreadable.map(u => u.path) });
  const unplaceable = view.records.find(r => r.key_error && (r.state === 'Accepted' || r.state === null));
  if (unplaceable) return no('view_has_unplaceable_record', [], { blocking: [unplaceable.path] });
  if (origin.legacy) return no('legacy_record');
  if (origin.errors.length) return no('record_invalid');
  if (origin.key_error) return no('decision_key_invalid');
  if (!origin.key) return no('decision_key_missing');
  const sameKey = view.records.filter(r => r.key === origin.key);
  const undetermined = sameKey.find(r => r.state === null);
  if (undetermined) return no('record_invalid', [], { blocking: [undetermined.path] });
  if (sameKey.filter(r => r.state === 'Accepted').length > 1) return no('conflicting_accepted_records');
  const chain = [];
  for (let current = origin; ;) {
    if (chain.includes(current.number)) return no('cycle', chain);
    chain.push(current.number);
    if (current.errors.length || current.legacy) return no('record_invalid', chain);
    if (current.key !== origin.key) return no('target_key_mismatch', chain);
    if (current.state === 'Accepted') return { resolution: 'resolved', chain, effective_id: current.number, record: current };
    if (!current.superseded_by) return no('no_explicit_accepted_target', chain);
    const next = view.byNumber.get(current.superseded_by);
    if (!next) return no('missing_target', chain);
    if (next.length > 1) return no('ambiguous_target', chain);
    current = next[0];
  }
}

const printable = text => text.replace(/[\u0000-\u0008\u000b-\u001f\u007f-\u009f﻿]/gu, c => (c === '\r' ? '\\r' : `\\u${c.codePointAt(0).toString(16).padStart(4, '0')}`));
const refOf = (binding, commit, r) => ({ binding: binding.id, repository: binding.repository, path: r.path, adr_id: r.number, commit, digest: r.digest });

const REASONS = {
  view_has_unreadable_record: 'a file in the ADR folder cannot be read, so no ruling can be confirmed',
  view_has_unplaceable_record: 'an Accepted record has a doubled or malformed Decision key, so it could conflict with any ruling',
  legacy_record: 'a Legacy record is not format-checked and is never a ruling',
  record_invalid: 'the record (or one it depends on) fails the dev2 format check',
  decision_key_invalid: 'the record has two Decision key lines or a malformed one',
  decision_key_missing: 'the record has no Decision key, so nothing tells whether it is the one in force',
  conflicting_accepted_records: 'more than one Accepted record carries this Decision key',
  cycle: 'the Superseded-by chain loops',
  target_key_mismatch: 'a record in the chain carries a different Decision key',
  missing_target: 'the Superseded-by chain points at a record that does not exist',
  ambiguous_target: 'the Superseded-by chain points at a number used by two files',
  no_explicit_accepted_target: 'the chain ends at a record that is not Accepted (Proposed or Deprecated)',
};
const row = (label, value, width = 15) => `${label.padEnd(width)}${value}`;

function render(result, format) {
  if (format === 'json') return JSON.stringify(result, null, 2);
  if (!result.ok) {
    const d = result.detail ?? {};
    return [`REFUSED ${result.reason}`, ...Object.entries(d).map(([k, v]) => row(`  ${k}`, Array.isArray(v) ? v.join(', ') : v))].join('\n');
  }
  const r = result.reference;
  const out = ['Reference', ...[['Binding', r.binding], ['Repository', r.repository], ['ADR', r.adr_id], ['Path', r.path], ['Commit', r.commit], ['Digest', r.digest]].map(([k, v]) => row(`  ${k}`, v)), ''];
  out.push(row('Status', result.status.written || '(empty)'), row('Decision key', result.decision_key ?? '(none)'),
    row('Format', result.format.legacy ? 'legacy (not checked by adr_lint; Status is not a dev2 state)' : result.format.errors.length ? `NOT dev2-valid: ${result.format.errors.join(', ')}` : 'dev2-valid (adr_lint rules)'));
  if (result.digest_check) out.push(row('Digest check', 'matches the expected digest'));
  if (result.command === 'effective') {
    if (result.resolution === 'resolved') {
      out.push(row('Resolution', result.is_effective ? 'EFFECTIVE: this record is the ruling in force'
        : `NOT EFFECTIVE: superseded; the ruling in force is ADR ${result.effective_id}   (chain ${result.chain.join(' -> ')})`));
      if (!result.is_effective) out.push(row('Ruling ADR', `${result.effective_id} (same commit)`), row('Ruling path', result.effective_reference.path), row('Ruling digest', result.effective_reference.digest));
    } else {
      out.push(row('Resolution', `UNRESOLVED: ${REASONS[result.reason] ?? result.reason} (${result.reason})`));
      if (result.blocking) out.push(row('Blocking', result.blocking.join(', ')));
    }
    const v = result.view;
    out.push(row('Folder', `${v.records} ADR files read; skipped: ${v.skipped.join(', ') || '-'}`), row('Nonconforming', v.nonconforming.join(', ') || '-'), row('Format-invalid', v.invalid_records.join(', ') || '-'));
  }
  out.push('', 'A record is not approval or permission to act.');
  if (result.text !== undefined) out.push('---- source text, bytes untouched (control characters shown escaped) ----', printable(result.text));
  return out.join('\n');
}

export function run(argv) {
  const opts = {};
  const command = argv[0];
  try {
    const bad = problem => new Refusal(2, 'bad_arguments', { problem });
    for (let i = 1; i < argv.length; i += 1) {
      const key = argv[i];
      if (key === '--require-effective') { opts['require-effective'] = true; continue; }
      if (!['--config', '--binding', '--commit', '--id', '--format', '--expect-digest'].includes(key)) throw bad(`unknown flag ${key}`);
      if (argv[i + 1] === undefined) throw bad(`${key} needs a value`);
      opts[key.slice(2)] = argv[++i];
    }
    opts.format ??= 'json';
    if (!['read', 'effective'].includes(command)) throw bad('the command is read or effective');
    if (!['json', 'human'].includes(opts.format)) throw bad(`--format is json or human, not ${opts.format}`);
    if (!opts.config) throw bad('--config is required');
    if (!opts.binding) throw bad('--binding is required');
    if (!/^\d{4}$/.test(opts.id ?? '')) throw bad('--id is four digits, for example 0003');
    if (opts['require-effective'] && command !== 'effective') throw bad('--require-effective belongs to effective');
    if (opts['expect-digest'] !== undefined && !/^sha256:[0-9a-f]{64}$/.test(opts['expect-digest'])) throw new Refusal(2, 'bad_expected_digest', { received: opts['expect-digest'] });
    const binding = loadBinding(opts.config, opts.binding);
    const view = loadView(binding, opts.commit);
    const group = view.byNumber.get(opts.id);
    if (!group) { const bad = view.unreadable.find(u => u.path.includes(`/${opts.id}-`)); throw bad ? new Refusal(5, 'unsupported_record', { path: bad.path, why: bad.why }) : new Refusal(2, 'unknown_id', { id: opts.id }); }
    if (group.length > 1) throw new Refusal(2, 'ambiguous_id', { paths: group.map(r => r.path) });
    const record = group[0], reference = refOf(binding, opts.commit, record);
    if (opts['expect-digest'] && opts['expect-digest'] !== record.digest) throw new Refusal(4, 'digest_mismatch', { expected: opts['expect-digest'], actual: record.digest, reference: record.path });
    const result = { ok: true, command, tool: TOOL, reference, status: { written: record.status_written, state: record.state },
      decision_key: record.key, format: { legacy: record.legacy, errors: record.errors }, authorization: 'none' };
    if (opts['expect-digest']) result.digest_check = 'matched';
    if (command === 'read') result.text = record.text;
    else {
      const e = effective(view, opts.id);
      Object.assign(result, { resolution: e.resolution, reason: e.reason ?? null, blocking: e.blocking ?? null, chain: e.chain, effective_id: e.effective_id, is_effective: e.effective_id === opts.id,
        effective_reference: e.record ? refOf(binding, opts.commit, e.record) : null,
        view: { records: view.records.length, skipped: view.skipped, nonconforming: view.nonconforming, invalid_records: view.records.filter(r => r.errors.length).map(r => r.number) } });
    }
    const notEffective = opts['require-effective'] && !(result.resolution === 'resolved' && result.is_effective);
    return { exit: notEffective ? 6 : 0, stdout: render(result, opts.format), result };
  } catch (error) {
    if (!(error instanceof Refusal)) throw error;
    const result = { ok: false, reason: error.reason, detail: error.extra };
    return { exit: error.exit, stdout: render(result, opts.format === 'human' ? 'human' : 'json'), result };
  }
}

if (realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) {
  const { exit, stdout, result } = run(process.argv.slice(2));
  if (!result.ok && process.argv.includes('human')) console.error(stdout); else console.log(stdout);
  process.exitCode = exit;
}
