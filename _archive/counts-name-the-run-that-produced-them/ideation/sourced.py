"""Read-only: per committed validation briefing, count-bearing sentences and whether each carries a source:
a bracket with a 20YY-MM-DD date, or 'report, not run', or a backticked command/path. Split by briefing commit date."""
import json, re, subprocess, sys
repo, cut = sys.argv[1], sys.argv[2]
NOUN = r"(?:cells?|runs?|tests?|files?|findings?|words?|lines?|PRs?|tasks?|commits?|cases?|records?|steps?|rounds?|tokens?|briefings?|attempts?|skips?)"
COUNT = re.compile(rf"\b\d[\d,]*\s*(?:of|/)\s*\d[\d,]*\b|\b\d[\d,]*\s+{NOUN}\b")
SOURCE = re.compile(r"\([^()]*\b20\d\d-\d\d-\d\d\b[^()]*\)|report, not run|`[^`]+`")
def git(*a): return subprocess.run(["git","-C",repo,*a],capture_output=True,text=True).stdout
rev=git("rev-parse","HEAD").strip()
files=[f for f in git("ls-tree","-r","--name-only",rev).split() if re.search(r"review/validation/briefing-\d+/index\.json$",f)]
out={"before":[0,0,0,0],"after":[0,0,0,0]}  # briefings, briefings with an unsourced count, count sentences, unsourced
for f in files:
    when=git("log","-1","--format=%cI","--diff-filter=A",rev,"--",f).strip()
    k="after" if when>=cut else "before"
    try: d=json.loads(git("show",f"{rev}:{f}"))
    except Exception: continue
    text="\n".join(a.get("summary","") for a in d.get("artifacts",[]))
    sents=[s for s in re.split(r"(?<=[.;])\s+|\n",text) if COUNT.search(s)]
    uns=[s for s in sents if not SOURCE.search(s)]
    o=out[k]; o[0]+=1; o[1]+=bool(uns); o[2]+=len(sents); o[3]+=len(uns)
print(json.dumps({"repo":repo.split("/")[-1] if "spacedock-state" not in repo else "kc-plugin dev2","rev":rev[:9],"cut":cut,"before":out["before"],"after":out["after"]}))
