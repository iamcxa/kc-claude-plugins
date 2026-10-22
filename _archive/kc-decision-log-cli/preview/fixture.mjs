// DISPOSABLE: builds a fictional decision repository (native docs/adr layout) with three commits: D0, D1 (a supersession) and D2 (a file that is not UTF-8) and a side branch commit D3 (a record with two Decision key lines).
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export function adr({ n, title, status = 'Accepted', key, date = '2026-10-09', extra = '' }) {
  return `# ${Number(n)}. ${title}

Date: ${date}

## Status

${status}

## Context

A fictional team at the Cafe\u0301 needed a ruling about "${title.toLowerCase()}".

## Decision

**Words:** 「照這個方向」 — Mira Example, 2026-10-09

**Options considered:**
- the chosen option (chosen)
- the other option — rejected: it costs more

**Recommended:** the chosen option.
${key ? `\n**Decision key:** ${key}\n` : ''}${extra}
## Consequences

Nothing outside this fictional record changes.
`;
}

const ENV = { ...process.env, GIT_AUTHOR_NAME: 'Fixture', GIT_AUTHOR_EMAIL: 'fixture@example.invalid', GIT_COMMITTER_NAME: 'Fixture',
  GIT_COMMITTER_EMAIL: 'fixture@example.invalid', GIT_AUTHOR_DATE: '2026-10-09T09:00:00Z', GIT_COMMITTER_DATE: '2026-10-09T09:00:00Z' };
const git = (dir, ...args) => execFileSync('git', ['-C', dir, ...args], { env: ENV, encoding: 'utf8' }).trim();

export function build() {
  const dir = mkdtempSync(join(tmpdir(), 'kcdl-preview-'));
  git(dir, 'init', '-q', '-b', 'main');
  git(dir, 'remote', 'add', 'origin', 'https://github.com/example/mira-decisions.git');
  const root = join(dir, 'docs/adr');
  mkdirSync(root, { recursive: true });
  const put = (name, text) => writeFileSync(join(root, name), text);
  put('0001-demo-site-is-team-login-first.md', adr({ n: 1, title: 'Demo site is team login first', key: 'team-login-first' }));
  put('0002-export-format-is-csv.md', adr({ n: 2, title: 'Export format is CSV', status: 'Proposed', key: 'export-format' }));
  put('0003-reports-are-weekly.md', adr({ n: 3, title: 'Reports are weekly', key: 'report-cadence' }));
  put('0005-no-key-record.md', adr({ n: 5, title: 'A record with no key' }));
  put('0006-retention-thirty-days.md', adr({ n: 6, title: 'Retention is thirty days', key: 'retention-days' }));
  put('0007-retention-ninety-days.md', adr({ n: 7, title: 'Retention is ninety days', key: 'retention-days' }));
  put('0008-points-at-nothing.md', adr({ n: 8, title: 'Points at nothing', status: 'Superseded by 0099', key: 'dangling' }));
  put('0009-cycle-a.md', adr({ n: 9, title: 'Cycle a', status: 'Superseded by 0010', key: 'cycle' }));
  put('0010-cycle-b.md', adr({ n: 10, title: 'Cycle b', status: 'Superseded by 0009', key: 'cycle' }));
  put('0011-bad-date.md', adr({ n: 11, title: 'Bad date', key: 'bad-date', date: '2026-9-1' }));
  put('0012-crlf-record.md', adr({ n: 12, title: 'CRLF record', key: 'crlf' }).replaceAll('\n', '\r\n'));
  put('0013-bom-record.md', '﻿' + adr({ n: 13, title: 'BOM record', key: 'bom' }));
  put('0016-twin-a.md', adr({ n: 16, title: 'Twin a' }));
  put('0016-twin-b.md', adr({ n: 16, title: 'Twin b' }));
  put('0014-legacy-record.md', '# 14. Legacy record\n\nStatus: Legacy\n\nFree text from before the format.\n');
  for (const name of ['README.md', 'index.md', 'template.md']) put(name, `# ${name}\n`);
  put('notes.md', '# loose notes\n');
  put('alpha.md', '# alpha\n');
  put('Zebra.md', '# Zebra\n');
  put('.gitkeep', '');
  git(dir, 'add', '-A'); git(dir, 'commit', '-q', '-m', 'D0');
  const d0 = git(dir, 'rev-parse', 'HEAD');
  put('0003-reports-are-weekly.md', adr({ n: 3, title: 'Reports are weekly', status: 'Superseded by 0004', key: 'report-cadence' }));
  put('0004-reports-are-daily.md', adr({ n: 4, title: 'Reports are daily', key: 'report-cadence' }));
  git(dir, 'add', '-A'); git(dir, 'commit', '-q', '-m', 'D1');
  const d1 = git(dir, 'rev-parse', 'HEAD');
  writeFileSync(join(root, '0015-not-utf8.md'), Buffer.concat([Buffer.from(adr({ n: 15, title: 'Not UTF8', key: 'broken-bytes' })), Buffer.from([0xff, 0xfe, 0x0a])]));
  git(dir, 'add', '-A'); git(dir, 'commit', '-q', '-m', 'D2');
  const d2 = git(dir, 'rev-parse', 'HEAD');
  git(dir, 'checkout', '-q', '-b', 'side', d1);
  put('0017-two-keys.md', adr({ n: 17, title: 'Two keys', key: 'first-key', extra: '\n**Decision key:** second-key\n' }));
  git(dir, 'add', '-A'); git(dir, 'commit', '-q', '-m', 'D3');
  const d3 = git(dir, 'rev-parse', 'HEAD');
  git(dir, 'checkout', '-q', 'main');
  return { dir, d0, d1, d2, d3 };
}
