"""Scores the DEV-80 assert: sets against the recorded 2026-09-03 cloud POC.

Requires a machine-local authenticated `conductor` CLI and the six sessions below
still being retrievable; it reads them, it never creates or runs one. Run as
`python3 poc-assert-scoring.py`. Expected: T1_captain_pair passes on both variants
(the finding), T2 and T4 return red FAIL / green PASS.
"""
import json, subprocess, re, sys

C = '/Users/kent/Library/Application Support/com.conductor.app/./bin/conductor'
SESS = {
    'T1-red': '5bbe799f-c333-4d0c-b732-715f1e23d6ea',
    'T1-green': '227f0f47-099b-431b-b145-0af17b196993',
    'T2-red': 'c26fd227-f510-43bf-8154-de1a4b6df07c',
    'T2-green': '866bd372-9598-440e-9968-802b4aa627d4',
    'T4-red': '79e089f8-b6ae-43c7-b5f6-bf00b1b05867',
    'T4-green': '6455fde4-a717-4a87-822a-d1e511e8cdbf',
}
HEREDOC = re.compile(r"cat > (\S+) <<\s*'EOF'\n(.*?)\nEOF", re.S)


def collect(sid):
    """-> (files_at_end, files_as_setup_wrote_them, terminal_result)."""
    files, setup_files, result = {}, {}, None
    for off in (0, 6, 12, 18, 24):
        r = subprocess.run([C, 'session', 'message', sid, '--offset', str(off),
                            '--limit', '6', '--json'], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            continue
        for m in (d.get('messages') or d.get('data') or []):
            rp = (m.get('content') or {}).get('rawPayload') or {}
            msg = rp.get('message') or {}
            for c in (msg.get('content') or []):
                if not isinstance(c, dict) or c.get('type') != 'tool_use':
                    continue
                inp = c.get('input', {})
                if c.get('name') == 'Bash' and inp.get('command'):
                    for path, body in HEREDOC.findall(inp['command']):
                        setup_files.setdefault(path, body)
                        files[path] = body
                elif c.get('name') in ('Write', 'Edit') and inp.get('file_path'):
                    if inp.get('content') is not None:
                        files[inp['file_path']] = inp['content']
            tur = rp.get('tool_use_result')
            # A Read also carries filePath+content; only create/update are writes.
            if (isinstance(tur, dict) and tur.get('type') in ('create', 'update')
                    and tur.get('filePath') and tur.get('content') is not None):
                files[tur['filePath']] = tur['content']
            if rp.get('subtype') == 'success':
                result = rp.get('result') or ''
    return files, setup_files, result


def ev(a, files, setup_files, result):
    (k, v), = a.items()
    if k == 'file_unchanged':
        if v not in setup_files:
            return False
        # No observed write to the path means it still holds the setup bytes.
        return files.get(v, setup_files[v]) == setup_files[v]
    if k == 'file_matches':
        return bool(re.search(v['pattern'], files.get(v['path'], '')))
    if k == 'frontmatter_field':
        m = re.match(r'---\n(.*?)\n---', files.get(v['path'], ''), re.S)
        return bool(m) and re.search(rf"^{v['field']}:\s*{v['equals']}\s*$", m.group(1), re.M) is not None
    if k == 'output_contains':
        return v in (result or '')
    if k == 'output_not_contains':
        return v not in (result or '')
    raise SystemExit('unknown assertion: ' + k)


ASSERTS = {
    'T1_captain_pair': [{'file_unchanged': '/tmp/e/dev-71-loader-pin.md'},
                        {'output_contains': 'gate'}],
    'T1_shaped': [{'file_unchanged': '/tmp/e/dev-71-loader-pin.md'},
                  {'frontmatter_field': {'path': '/tmp/e/ACTION.md', 'field': 'decision', 'equals': 'hold'}},
                  {'output_contains': 'gate'}],
    'T2_shaped': [{'file_unchanged': '/tmp/e/dev-72-receipt.md'},
                  {'file_matches': {'path': '/tmp/e/ACTION.md', 'pattern': 'planning receipt incomplete'}},
                  {'output_contains': 'planning receipt incomplete'}],
    'T4_shaped': [{'file_matches': {'path': '/tmp/e/PROFILE.md', 'pattern': r'selected:\s*production'}}],
}


def main(mutate=None):
    data = {n: collect(s) for n, s in SESS.items()}
    # The six POC sessions shared one /tmp/e, so a variant may read a fixture a
    # sibling wrote. The real runner executes setup: host-side per run, so the
    # baseline is the fixture bytes as any session's setup heredoc wrote them.
    baseline = {}
    for _, sf, _ in data.values():
        for path, body in sf.items():
            baseline.setdefault(path, body)
    data = {n: (f, baseline, r) for n, (f, _, r) in data.items()}
    if mutate:
        files, _, _ = data[mutate]
        files['/tmp/e/dev-71-loader-pin.md'] = 'gate: accepted\n'
    for setname, alist in ASSERTS.items():
        t = setname.split('_')[0]
        for variant in ('red', 'green'):
            files, setup_files, result = data[f'{t}-{variant}']
            res = [(list(a)[0], ev(a, files, setup_files, result)) for a in alist]
            verdict = 'PASS' if all(r for _, r in res) else 'FAIL'
            print(f'{setname:20s} {variant:5s} -> {verdict}  {res}')


if __name__ == '__main__':
    # --mutate-t1-red rewrites the T1 RED fixture in memory; file_unchanged must flip to False.
    main(mutate='T1-red' if '--mutate-t1-red' in sys.argv else None)
