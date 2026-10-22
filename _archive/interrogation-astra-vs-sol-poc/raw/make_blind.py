import re, sys, pathlib
base = pathlib.Path(sys.argv[1])
tasks = ["number-guards-readme-shrink", "fo-write-checks", "chat-only-evidence-observer-blind",
         "delivery-gate-settles-skipped-checks", "special-role-calls-fire-when-needed"]
def norm(s):
    s = re.sub(r"\n[ \t]*Reads: \d+, minutes: \d+[ \t]*\n?$", "\n", s.rstrip() + "\n")
    s = s.replace("**", "")
    s = "\n".join(l.rstrip() for l in s.splitlines())
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip() + "\n"
for t in tasks:
    txt = (base / "raw" / t / "astra-answer.md").read_text()
    (base / "blind" / f"{t}-Z.md").write_text(norm(txt))
