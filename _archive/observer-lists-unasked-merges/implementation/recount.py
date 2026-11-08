import contextlib, importlib.util, io, json, pathlib, re, statistics, subprocess, sys
from unittest.mock import patch
source, state, out = map(pathlib.Path, sys.argv[1:])
out.mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location("audit", source)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
def g(*args):
    return subprocess.check_output(["git", "-C", str(state), *args], text=True).strip()
# Reuse the freshly fetched local refs, without another fetch for every window.
native_run = subprocess.run
def no_network(command, *args, **kwargs):
    if command[:1] == ["git"] and "fetch" in command:
        return subprocess.CompletedProcess(command, 0, b"", b"")
    return native_run(command, *args, **kwargs)
with patch.object(subprocess, "run", side_effect=no_network), contextlib.redirect_stdout(io.StringIO()):
    records, owners = audit.read_state(state, "iamcxa/kc-claude-plugins")
prs = json.loads((state / "observer-lists-unasked-merges/poc/merged-window.json").read_text())
snapshot = "13d91fadd2fa8e6184b1b925e50638e6aff38aab"
manifest = json.loads(pathlib.Path(__file__).with_name("window-manifest.json").read_text())
archives = [(audit.stamp(g("show", "-s", "--format=%cI", row["rev"])), row["slug"], row["rev"])
            for row in manifest]
archives.sort()
rule = '"merging the full head ~<package>/scripts/delivery_gate.py check~ passes, with ~--match-head-commit~ set to it" (Delivery authority)'.replace("~", chr(96))
caveat = "Coverage: a merge with no ask record may have been approved in chat or recorded in a state checkout this run cannot read; neither shows here."
reported, results = set(), []
def render(raw, cumulative):
    lines = raw.splitlines()
    carried = next(s for s in lines if s.startswith("carried:"))
    output = [f'ok | rule: {rule} | evidence: "{carried} merged PRs" (gh pr list, state refs)']
    for kind in ("release", "sync", "learning"):
        line = next(s for s in lines if s.startswith(kind + ":"))
        if not line.endswith(": none"):
            output.append(f'observed | {kind} PRs carry no task ask | evidence: "{line}" (gh pr list)')
    repeats, seen, gaps = [], set(), False
    for line in lines:
        match = re.match(r"(no ask record|head differs): #(\d+) head (\w{12})", line)
        if not match:
            continue
        token = match.group(0)
        if token in cumulative:
            repeats.append("#" + match[2])
            continue
        verdict = "can't tell" if match[1] == "no ask record" else "violation"
        output.append(f'{verdict} | rule: {rule} | evidence: "{line}" (gh pr list, state refs)')
        seen.add(token)
        gaps = True
    if repeats:
        output.append('observed | already in an earlier observer report | evidence: "' + " ".join(repeats) + '"')
    if gaps:
        output.append(caveat)
    return output, seen
for time, slug, rev in archives:
    born = g("log", "--diff-filter=A", "--format=%cI", "--reverse", snapshot, "--", slug + ".md").splitlines()
    if not born:
        continue
    capture = io.StringIO()
    def selected(repo, trunk, lo, hi):
        return sorted([p for p in prs if lo < audit.stamp(p["mergedAt"]) <= hi], key=lambda p:p["number"])
    with patch.object(audit, "read_state", return_value=(records, owners)), patch.object(audit, "merged_prs", side_effect=selected), contextlib.redirect_stdout(capture):
        audit.audit(state, slug, None, rev)
    raw = capture.getvalue()
    (out / (slug + "-audit.txt")).write_text(raw)
    rendered, newly = render(raw, reported)
    reported.update(newly)
    no_collapse, _ = render(raw, set())
    results.append({"slug":slug, "rev":rev, "words":sum(len(s.split()) for s in rendered),
                    "without_collapse":sum(len(s.split()) for s in no_collapse), "lines":rendered})
    (out / (slug + "-rendered.txt")).write_text("\n".join(rendered) + "\n")
stats = {"snapshot":snapshot, "windows":len(results), "median":statistics.median(x["words"] for x in results),
         "max":max(x["words"] for x in results), "max_task":max(results, key=lambda x:x["words"])["slug"],
         "uncollapsed_max":max(x["without_collapse"] for x in results),
         "scope":"candidate classifications over ideation's 92-PR fixture; chronological verbatim-report collapse simulation"}
(out / "windows.json").write_text(json.dumps(results, indent=2))
(out / "summary.json").write_text(json.dumps(stats, indent=2))
print(json.dumps(stats))
assert stats["windows"] == 54 and stats["median"] <= 60 and stats["max"] <= 320
