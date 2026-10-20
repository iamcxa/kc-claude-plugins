import json, re, secrets, sys, pathlib
base = pathlib.Path(sys.argv[1])
tasks = ["number-guards-readme-shrink", "fo-write-checks", "chat-only-evidence-observer-blind",
         "delivery-gate-settles-skipped-checks", "special-role-calls-fire-when-needed"]
def norm(s):
    s = re.sub(r"\n[ \t]*Reads: \d+, minutes: \d+[ \t]*\n?$", "\n", s.rstrip() + "\n")
    s = s.replace("**", "")
    s = "\n".join(l.rstrip() for l in s.splitlines())
    s = re.sub(r"\n{2,}", "\n", s)
    s = re.sub(r"^(\d+)\. Q:", r"\1. Q:", s, flags=re.M)
    return s.strip() + "\n"
coin = {}
for t in tasks:
    flip = secrets.randbelow(2)
    order = ["a3", "a4"] if flip == 0 else ["a4", "a3"]
    coin[t] = {"X": order[0], "Y": order[1]}
    for lab, arm in zip("XY", order):
        txt = (base / "raw" / t / f"{arm}-answer.md").read_text()
        (base / "blind" / f"{t}-{lab}.md").write_text(norm(txt))
(base / "sealed" / "coin.json").write_text(json.dumps(
    {"note": "Sealed. The blind second reader must not open this file before its scores are saved. a3 = Codex plain prompt, a4 = Codex with the engineering-reviewer lens.",
     "map": coin}, indent=2) + "\n")
