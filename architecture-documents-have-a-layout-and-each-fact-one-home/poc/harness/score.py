#!/usr/bin/env python3
"""Score every stored chain from its git bundle. Needs no agent. Writes ../results.json and prints a table."""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
FACTS = ["F1 window says 18, not 36", "F2 no-show state named", "F3 no-show keeps deposit",
         "F4 a new ADR carries the owner's words", "F5 ADR 0003 superseded by it", "F6 architecture cites it",
         "F7 reminder says 44, not 20", "F8 SMS idea kept out", "F9 refactor left architecture alone",
         "F10 waitlist and its 25 minutes described"]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout


def arch_files(repo, ref):
    names = git(repo, "ls-tree", "-r", "--name-only", ref).split("\n")
    return sorted(n for n in names if n == "ARCHITECTURE.md" or n == "docs/architecture.md" or n.startswith("docs/architecture/"))


def arch_text(repo, ref):
    return "\n".join(git(repo, "show", f"{ref}:{n}") for n in arch_files(repo, ref))


def adrs(repo, ref):
    names = [n for n in git(repo, "ls-tree", "-r", "--name-only", ref, "docs/adr/").split("\n") if n.endswith(".md")]
    return {n: git(repo, "show", f"{ref}:{n}") for n in names}


def status_of(text):
    m = re.search(r"^## Status\s*\n+\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def has(text, pattern):
    return bool(re.search(pattern, text, re.I))


def score_chain(repo):
    end = "step-6"
    text, records = arch_text(repo, end), adrs(repo, end)
    added = {n: t for n, t in records.items() if int(re.search(r"/(\d{4})-", n).group(1)) > 4}
    ruling = sorted(n for n, t in added.items() if "**Words:**" in t and has(t, r"no exceptions"))
    num = int(re.search(r"/(\d{4})-", ruling[0]).group(1)) if ruling else 0
    old3 = next((t for n, t in records.items() if "/0003-" in n), "")
    noshow = [m.start() for m in re.finditer(r"no[-_ ]show", text, re.I)]
    facts = [
        has(text, r"\b18\b") and not has(text, r"\b36\b"),
        bool(noshow),
        any(has(text[max(0, i - 250):i + 250], r"deposit") for i in noshow),
        bool(ruling),
        bool(num) and has(status_of(old3), rf"^superseded by \[?(adr[- ]?)?0*{num}\b"),
        bool(num) and has(text, rf"\b{num:04d}\b"),
        has(text, r"\b44\b") and not has(text, r"\b20\b"),
        not has(text, r"\bsms\b") and not any(has(t, r"\bsms\b") for t in records.values()),
        arch_text(repo, "step-4") == arch_text(repo, "step-5"),
        has(text, r"wait[- ]?list") and has(text, r"\b25\b"),
    ]
    files = arch_files(repo, end)
    own_step = [  # the fact was already true at the end of the step that changed the behaviour
        has(arch_text(repo, "step-1"), r"\b18\b") and not has(arch_text(repo, "step-1"), r"\b36\b"),
        has(arch_text(repo, "step-2"), r"no[-_ ]show"),
        bool(num) and has(arch_text(repo, "step-3"), rf"\b{num:04d}\b"),
        has(arch_text(repo, "step-4"), r"\b44\b") and not has(arch_text(repo, "step-4"), r"\b20\b"),
        has(arch_text(repo, "step-6"), r"wait[- ]?list"),
    ]
    all_names = git(repo, "ls-tree", "-r", "--name-only", end).split("\n")
    stray = sorted(n for n in all_names if n.endswith(".md") and n not in files and not n.startswith(("docs/adr/", ".flow/"))
                   and n != "README.md")
    later = git(repo, "show", f"{end}:docs/journey/later.md")
    idea_files = sorted(n for n in all_names if n and not n.startswith(".flow/") and has(git(repo, "show", f"{end}:{n}"), r"\bsms\b"))
    return {"idea_files": idea_files, "idea_in_later_md": has(later, r"\bsms\b"), "facts": facts, "score": sum(facts), "own_step": own_step, "adrs_added": len(added), "ruling_adr": num, "arch_files": files, "stray_docs": stray,
            "harbor_club_still_mentioned": has(text, r"harbor club"),
            "layered": {"waitlist_has_own_file": any(re.search(r"docs/architecture/.*wait", n, re.I) for n in files),
                        "map_row_for_waitlist": has(git(repo, "show", f"{end}:docs/architecture.md"), r"\]\(architecture/[^)]*wait")},
            "arch_words": len(text.split())}


def main():
    out = {}
    for bundle in sorted(RESULTS.glob("*/tidepool.bundle")):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "clone", "-q", str(bundle), tmp], check=True, capture_output=True)
            subprocess.run(["git", "-C", tmp, "fetch", "-q", "--tags", str(bundle)], check=True, capture_output=True)
            row = score_chain(tmp)
        metas = [json.loads(p.read_text()) for p in sorted(bundle.parent.glob("step-*.meta.json"))]
        row["tests_pass_at_end"] = bool(metas) and metas[-1]["tests_pass"]
        row["steps_failed"] = [m["step"] for m in metas if m["exit_code"] != 0 or m["timed_out"]]
        row["elapsed_s"] = round(sum(m["elapsed_s"] for m in metas))
        row["usage"] = {k: sum(m["usage"].get(k, 0) for m in metas) for k in sorted({k for m in metas for k in m["usage"]})}
        out[bundle.parent.name] = row
    (HERE.parent / "results.json").write_text(json.dumps({"facts": FACTS, "chains": out}, indent=1))
    for name, row in out.items():
        marks = "".join("1" if f else "0" for f in row["facts"])
        print(f"{name:16} {row['score']:2}/10  {marks}  own-step {sum(row['own_step'])}/5  stray={len(row['stray_docs'])} adrs+{row['adrs_added']} "
              f"tests={'ok' if row['tests_pass_at_end'] else 'FAIL'} failed_steps={row['steps_failed']} {row['elapsed_s']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
