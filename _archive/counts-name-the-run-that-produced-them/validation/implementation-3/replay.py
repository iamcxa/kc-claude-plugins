"""Read-only replays of the final pattern over pinned state and completed learn records."""
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

worktree, mode, *inputs = sys.argv[1:]
sys.path.insert(0, str(Path(worktree) / 'kc-dev-flow-2/scripts'))
from count_tokens import count_sentences, numbers
from learning import evaluation, Invalid


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True)


print(json.dumps(dict(script='replay.py', sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     run=datetime.datetime.now(datetime.timezone.utc).isoformat(), mode=mode,
                     candidate=git(worktree, 'rev-parse', 'HEAD').strip(),
                     pattern_sha256=hashlib.sha256((Path(worktree) / 'kc-dev-flow-2/scripts/count_tokens.py').read_bytes()).hexdigest())))
for value in inputs:
    label, repo, *revision = value.split('|')
    if mode == 'gate':
        rev = git(repo, 'rev-parse', revision[0]).strip()
        names = set(git(repo, 'ls-tree', '-r', '--name-only', rev).splitlines())
        tallies = {k: dict(briefings=0, with_count=0, nonzero_disclosure=0, checked=0, unchecked=0) for k in ('before', 'after')}
        for name in sorted(n for n in names if re.search(r'review/validation/briefing-\d+/index\.json$', n)):
            added = git(repo, 'log', '-1', '--format=%cI', '--diff-filter=A', rev, '--', name).strip()
            row = tallies['after' if added >= '2026-11-05T00:00:00Z' else 'before']
            document = json.loads(git(repo, 'show', rev + ':' + name))
            text = '\n'.join(a.get('summary', '') for a in document.get('artifacts', []))
            folder = name.split('/review/')[0]
            sentences = count_sentences(text)
            row['briefings'] += 1
            row['with_count'] += bool(sentences)
            unchecked = 0
            for sentence, wanted in sentences:
                content = []
                for ref in re.findall(r'(?<![\w/.-])((?:/?[\w.-]+/)*[\w.-]+\.(?:json|log|md|txt|jsonl|csv|out))\b', sentence):
                    if PurePosixPath(ref).is_absolute() or '..' in PurePosixPath(ref).parts:
                        continue
                    path = str(PurePosixPath(folder).parent / ref) if ref.split('/')[0] == PurePosixPath(folder).name else folder + '/' + ref
                    if path in names:
                        content.append(git(repo, 'show', rev + ':' + path))
                if content and wanted <= numbers('\n'.join(content)):
                    row['checked'] += 1
                else:
                    row['unchecked'] += 1
                    unchecked += 1
            row['nonzero_disclosure'] += bool(unchecked)
        print(json.dumps(dict(checkout=label, revision=rev, **tallies)))
    elif mode == 'learn':
        entries = with_count = 0
        refused = []
        snapshots = []
        for path in sorted(Path(repo).glob('kc-dev-flow-2/learning/*/record.json')):
            raw = path.read_bytes()
            record = json.loads(raw)
            if record.get('state') != 'completed':
                continue
            snapshots.append((path.parent.name, hashlib.sha256(raw).hexdigest()))
            for decision in record['evaluation']['decisions']:
                if decision['action'] != 'add':
                    continue
                entries += 1
                with_count += bool(count_sentences(decision['entry']['Evidence']))
                try:
                    evaluation(dict(schema_version=1, decisions=[decision]), record['input'])
                except Invalid as error:
                    refused.append(dict(job=path.parent.name, error=str(error)))
        print(json.dumps(dict(store=label, entries=entries, with_count=with_count, refused=refused,
                              record_snapshots=snapshots)))
    else:
        raise ValueError(mode)
