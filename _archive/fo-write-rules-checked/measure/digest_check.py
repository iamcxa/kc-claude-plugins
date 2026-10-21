"""DEFERRED (cycle 3): recompute the digest of every gate briefing bound in a state checkout's task frontmatter and compare it with the recorded `digest:`.
Usage: python3 -I -B digest_check.py <state checkout>        (reads only; sorted compact JSON, sha256, as the second engineering-reviewer read did)
Run 2026-10-20 on the scratch checkout at 8eda9070: `match 155 mismatch 0 missing 0` (digest-check-output.txt).
"""
import hashlib, json, re, sys
from pathlib import Path
state = Path(sys.argv[1])
ok = bad = miss = 0
for task in sorted(list(state.glob("*.md")) + list((state / "_archive").glob("*.md"))):
    text = task.read_text()
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m: continue
    for dg_, room in re.findall(r"digest: (sha256:[0-9a-f]{64})\s+room-ref: (\S+)", m.group(1)):
        p = task.parent / room.lstrip("./") if room.startswith("./") else Path(room)
        p = p / "index.json"
        if not p.is_file():
            miss += 1; continue
        d = json.loads(p.read_text())
        got = "sha256:" + hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        if got == dg_: ok += 1
        else: bad += 1
print("match", ok, "mismatch", bad, "missing", miss)
