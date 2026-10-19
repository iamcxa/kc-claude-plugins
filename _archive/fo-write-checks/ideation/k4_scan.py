"""Scan every `Design:` line of every Captain amendment entry: is it a verbatim paragraph of the task outside the amendments section?
Usage: python3 -I k4_scan.py <state checkout>"""
import glob, os, re, sys
S = sys.argv[1]
def unfence(t):
    out, inside = [], False
    for l in t.split("\n"):
        if re.match(r"^[ \t]*```", l):
            inside = not inside
            continue
        if not inside:
            out.append(l)
    return "\n".join(out)
def norm(s):
    return re.sub(r"\s+", " ", s).strip().strip("「」\"'`“”").strip()
tot = verbatim = 0
for f in sorted(glob.glob(S + "/*.md") + glob.glob(S + "/_archive/*.md")):
    u = unfence(open(f).read())
    m = re.search(r"^## Captain amendments[ \t]*\n(.*?)(?=^## |\Z)", u, re.M | re.S)
    if not m:
        continue
    outside = norm(u.replace(m.group(0), ""))
    for e in re.split(r"(?m)^(?=### )", m.group(1))[1:]:
        d = re.search(r"^Design:[ \t]*(.*?)(?=^\w[\w ]*:|^###|\Z)", e, re.M | re.S)
        if d:
            val = norm(d.group(1))
            tot += 1
            verbatim += val in outside
            print(os.path.basename(f)[:-3], "|", e.split("\n", 1)[0].strip()[:24], "|", "VERBATIM" if val in outside else "NOT-IN-TASK", "|", val[:90])
print(f"{tot} Design: lines; {verbatim} verbatim; {tot - verbatim} would be flagged")
