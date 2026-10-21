#!/usr/bin/env python3
"""AC-4 text check over a kc-adr plugin tree. Usage: text_check.py <repo-root>. Exit 1 on any failure."""
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
base = root / "kc-adr" / "skills" / "read-adr"
fails = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def read(p):
    try:
        return p.read_text()
    except OSError:
        return ""


skill, writing, prefix = read(base / "SKILL.md"), read(base / "writing.md"), read(base / "prefix.md")
low = skill.lower()
for what, rx in [("stop on digest mismatch", r"digests?.*stop|stop.*(both )?digests?|differ: stop"),
                 ("stop on missing clone or commit", r"stop.*missing clone or commit|missing clone or commit"),
                 ("non-Accepted Status", r"proposed.*deprecated.*not in force|not in force"),
                 ("broken chain stop", r"stop.*broken chain|broken chain")]:
    check(re.search(rx, low, re.S) is not None, f"SKILL.md names the stop: {what}")
order = [low.find(f"\n{i}. ", low.find("where new information goes")) for i in range(1, 6)]
check(all(o > 0 for o in order) and order == sorted(order), "SKILL.md lists the five questions 1..5 in order")
check("**one home.**" in low, "SKILL.md has the one-home rule")
check("**instruction files point, they do not restate.**" in low, "SKILL.md has the pointer rule")
check(len(skill.splitlines()) < 90, f"SKILL.md under 90 lines ({len(skill.splitlines())})")

parts = re.split(r"(?m)^(?=#{1,3} )", writing)
tools_re = re.compile(r"adr-template\.md|adr_lint\.py|number_guards\.py reserve --kind adr")
where = [p for p in parts if p.startswith("## Where the tools are")]
outside = [p for p in parts if not p.startswith("## Where the tools are")]
check(len(where) == 1 and all(len(set(m.group(0) for m in tools_re.finditer(where[0]))) == 3 for _ in [0]),
      "writing.md names adr-template.md, adr_lint.py, number_guards.py reserve --kind adr under '## Where the tools are'")
check(not any(tools_re.search(p) for p in outside), "writing.md names those files nowhere else")
check(re.search(r"kc-dev-flow-2/0\.", writing + skill + prefix) is None, "no literal kc-dev-flow-2/0.* path in the skill files")
check(not tools_re.search(skill + prefix), "SKILL.md and prefix.md name no dev2 tool file")
check("optional" in prefix.lower() and re.search(r"namespaces.*deferred", prefix.lower()) is not None,
      "prefix.md says the prefix is optional and monorepo namespaces are deferred")
tracked = subprocess.run(["git", "-C", str(root), "ls-files", "kc-adr"], capture_output=True, text=True).stdout
check(not re.search(r"adr_lint\.py|number_guards\.py|adr-template\.md", tracked), "git ls-files kc-adr lists no dev2 tool or template")
sys.exit(1 if fails else 0)
