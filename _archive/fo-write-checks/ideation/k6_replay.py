"""K6: for every task whose `## Number guards` holds `ADR: NNNN` and whose `pr:` is merged, is docs/adr/NNNN-*.md present at the PR head?
Reads GitHub (gh api, read-only). Usage: python3 -I k6_replay.py <state checkout> <owner/repo>"""
import glob, os, re, subprocess, sys
S, REPO = sys.argv[1:3]
def gh(*a):
    r = subprocess.run(["gh", "api", *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None
miss = ok = 0
for f in sorted(glob.glob(S + "/*.md") + glob.glob(S + "/_archive/*.md")):
    t = open(f).read()
    g = re.search(r"^## Number guards[ \t]*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    pr = re.search(r"^pr:[ \t]*(?:pr-merge:)?(\d+)", t, re.M)
    adrs = [int(n) for n in re.findall(r"^ADR:[ \t]*(\d+)[ \t]*$", g.group(1), re.M)] if g else []
    if not adrs or not pr:
        continue
    head = gh(f"repos/{REPO}/pulls/{pr.group(1)}", "--jq", ".head.sha")
    names = (gh(f"repos/{REPO}/contents/docs/adr?ref={head}", "--jq", ".[].name") or "").split()
    for n in adrs:
        here = any(re.match(rf"{n:04d}-.+\.md$", x) for x in names)
        ok += here
        miss += not here
        print(os.path.basename(f)[:-3], f"PR#{pr.group(1)}", head[:8], f"ADR {n:04d}", "present at head" if here else "MISSING at head")
print(f"{ok + miss} reservations; {miss} missing at the PR head")
