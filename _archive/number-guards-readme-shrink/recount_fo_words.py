#!/usr/bin/env python3
"""Recount the words FO reads at each moment from two git revisions of workflow.md.

Independent of the design's count: it parses lines, not the design's passage text.
Usage: recount_fo_words.py <repo> <base-rev> <candidate-rev>
"""
import re
import subprocess
import sys

PATH = "kc-dev-flow-2/references/sd/workflow.md"
R6_LINE = "FAIL R6: <path>: A under the migrations directory; a POC task changes none of it"
R2_LINE = "FAIL R2: <path>: M since <sha>, applied at uat; revert it and add a new migration"
RESERVE_LINE_WORDS = 2  # "Reserve line (2)" in the design: `reserve` is printed as 'Migration: NNNN'


def words(text):
    return len(re.findall(r"\S+", text))


def show(repo, rev):
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:{PATH}"], capture_output=True, text=True, check=True).stdout


def section(text, heading):
    lines = text.split("\n")
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def bullet(lines, name):
    start = next(i for i, l in enumerate(lines) if l.startswith(f"- **{name}.**"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("- **") or lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start:end]).strip()


def moments(text):
    ng = section(text, "## Number guards")
    fo = section(text, "## FO steps: number guards")
    ng_body = [l for l in ng[1:]]
    first_bullet = next(i for i, l in enumerate(ng_body) if l.startswith("- **"))
    head = "\n".join(ng_body[:first_bullet])
    head_lines = [l for l in head.split("\n") if l.strip()]
    applies = head_lines[0]
    config = "\n".join(head_lines[1:])
    reserve = bullet(fo, "Reserve")
    return {
        "FO startup or resume (both sections)": words("\n".join(ng + fo)),
        "FO builds an implementation dispatch": words(ng[0]) + words(applies) + words(config) + words(reserve) + RESERVE_LINE_WORDS,
        "Implementation worker starts (Number guards section, heading included)": words("\n".join(ng)),
        "Validation worker starts (Number guards section)": words("\n".join(ng)),
        "check prints R6 (POC bullet + R6 line)": words(bullet(ng, "POC")) + words(R6_LINE),
        "check prints R2 (Applied bullet + R2 line)": words(bullet(ng, "Applied")) + words(R2_LINE),
        "Merge ask (Check bullet)": words(bullet(ng, "Check")),
        "Collision (Collision bullet)": words(bullet(fo, "Collision")),
        "README total": words(text),
    }


def main():
    repo, base, cand = sys.argv[1:4]
    b, c = moments(show(repo, base)), moments(show(repo, cand))
    bad = 0
    for k in b:
        flag = "ABOVE BASE" if c[k] > b[k] else ("cut" if c[k] < b[k] else "equal")
        bad += c[k] > b[k]
        print(f"{k:58s} base={b[k]:5d} candidate={c[k]:5d} {flag}")
    print("no moment above base" if not bad else f"{bad} moment(s) above base")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
