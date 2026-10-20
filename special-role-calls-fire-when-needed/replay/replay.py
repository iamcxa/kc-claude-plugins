#!/usr/bin/env python3
"""Replay the candidate role_triggers.py over the four repositories' committed task records at the design's pins.

Usage: python3 -I replay.py <kc-dev-flow-2/scripts directory> [--slice2]
Reads inputs.json beside it and the window table from the task file two levels up. Exit 0 when every expected
number in inputs.json holds, 1 when one differs; each difference is printed.
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK = HERE.parent.parent / "special-role-calls-fire-when-needed.md"


def main():
    scripts = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(scripts))
    sys.dont_write_bytecode = True
    import role_triggers as rt
    spec = json.loads((HERE / "inputs.json").read_text())
    repos, want = spec["repos"], spec["expected"]

    def git(repo, *args):
        done = subprocess.run(["git", "-C", repos[repo]["checkout"], *args], capture_output=True)
        return done.stdout.decode("utf-8", "replace")

    window = []
    for line in TASK.read_text().splitlines():
        row = re.match(r"\| (kcp|relay|web|qnow)/(\S+) \| (\S)/(\S) \| (\S+(?: misfiled)?) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|", line)
        if row:
            window.append(row.groups())
    problems = []

    def expect(name, got, wanted):
        if got != wanted:
            problems.append(f"{name}: got {got}, expected {wanted}")
        print(f"{'ok  ' if got == wanted else 'DIFF'} {name}: {got}")

    expect("window tasks", len(window), want["window_tasks"])
    population = {}
    for repo in repos:
        for path in git(repo, "ls-tree", "-r", "--name-only", repos[repo]["pin"]).splitlines():
            found = re.fullmatch(r"(_archive/)?([^/]+?)(?:\.md|/index\.md)", path)
            if found and path not in ("README.md", "_archive/README.md") and found.group(2) != "README":
                population[(repo, found.group(2), bool(found.group(1)))] = path
    expect("population tasks", len(population), want["population_tasks"])

    def read(repo, slug):
        return rt.read_task(Path(repos[repo]["checkout"]), slug, repos[repo]["pin"])

    ce = er = fable = 0
    for repo, slug, _archived in population:
        text = read(repo, slug)
        lines = list(rt.outside_fences(text))
        reports, amendments = rt.events(lines)
        ce += reports - 1 >= rt.REPAIRS
        if amendments:
            er += 1
            front = re.match(r"---\n(.*?)\n---\n", text, re.S)
            prof = rt.FRONT_PROFILE.search(front.group(1)) if front else None
            strong = (prof and prof.group(1) == "prod") or any(rt.SURFACES_DB.match(l.strip()) for l in rt.alignment(lines))
            fable += bool(strong)
    expect("population chief-engineer fires", ce, want["population_chief_engineer_fires"])
    expect("population engineering-reviewer fires", er, want["population_engineering_reviewer_fires"])
    expect("population engineering-reviewer on fable", fable, want["population_engineering_reviewer_fable"])
    expect("population engineering-reviewer on opus", er - fable, want["population_engineering_reviewer_opus"])

    fires = {"ce": Counter(), "er": Counter()}
    owed = Counter()
    owed_slugs = {"ce": [], "er": []}
    hints, longest = [], 0
    for repo, slug, ce_label_er_label in [(r, s, c + "/" + e) for r, s, c, e, *_ in window]:
        text = read(repo, slug)
        lines = list(rt.outside_fences(text))
        reports, amendments = rt.events(lines)
        label_c, label_e = ce_label_er_label.split("/")
        if reports - 1 >= rt.REPAIRS:
            fires["ce"]["fires"] += 1
            fires["ce"]["true" if label_c == "C" else "unclear" if label_c in "?W" else "false"] += 1
        if amendments:
            fires["er"]["fires"] += 1
            fires["er"]["true" if label_e == "E" else "unclear" if label_e in "?W" else "false"] += 1
        done = subprocess.run([sys.executable, "-B", str(scripts / "role_triggers.py"), repos[repo]["checkout"], slug,
                               "--rev", repos[repo]["pin"]], capture_output=True, text=True)
        print(f"  {repo}/{slug}: repairs {max(reports - 1, 0)}, replacing amendments {len(amendments)}, owed:",
              [("CE" if "chief-engineer with" in l or "dispatch kc-dev-flow-2:chief-engineer" in l else "ER " + ("fable" if " on fable" in l else "opus") if "engineering-reviewer on" in l else "hint")
               for l in done.stdout.splitlines() if l.startswith("next:")])
        for out in (l for l in done.stdout.splitlines() if l.startswith("next:")):
            longest = max(longest, len(out.split()))
            if "dispatch kc-dev-flow-2:chief-engineer" in out:
                owed["chief-engineer"] += 1
                owed_slugs["ce"].append(slug)
            elif "dispatch kc-dev-flow-2:engineering-reviewer on fable" in out:
                owed["engineering-reviewer"] += 1
                owed["fable"] += 1
                owed_slugs["er"].append((slug, "fable"))
            elif "dispatch kc-dev-flow-2:engineering-reviewer on opus" in out:
                owed["engineering-reviewer"] += 1
                owed["opus"] += 1
                owed_slugs["er"].append((slug, "opus"))
            else:
                owed["heading_hint"] += 1
                hints.append(slug)
    expect("window chief-engineer fires", fires["ce"]["fires"], want["window_chief_engineer_fires"])
    expect("window chief-engineer true/unclear/false", [fires["ce"][k] for k in ("true", "unclear", "false")],
           want["window_chief_engineer_true_unclear_false"])
    expect("window engineering-reviewer fires", fires["er"]["fires"], want["window_engineering_reviewer_fires"])
    expect("window engineering-reviewer true/unclear/false", [fires["er"][k] for k in ("true", "unclear", "false")],
           want["window_engineering_reviewer_true_unclear_false"])
    expect("owed lines", {k: owed[k] for k in want["owed_lines"]}, want["owed_lines"])
    expect("heading hint is on", hints, [want["stays_owed_with_hint"]])
    expect("tasks whose chief-engineer call clears the event", [s for s in want["clear"] if s in owed_slugs["ce"]], [])
    expect("longest next: line is at most 60 words", longest <= 60, True)
    print("longest line", longest, "words")
    print("fable lines:", sorted(s for s, m in owed_slugs["er"] if m == "fable"))
    if "--slice2" in sys.argv:
        import pr_watch
        slugs = {"kcp": "iamcxa/kc-claude-plugins", "relay": "spacedock-dev/subspace-relay", "web": "spacedock-dev/subspace-web",
                 "qnow": "iamcxa/qnow"}
        read_rounds, fires2, disagree = {}, [], []
        for repo, slug, _c, _e, _call, _repairs, _sent, _same, table_rounds in window:
            number = re.search(r"^pr: (?:pr-merge:)?#?(\d+)\s*$", read(repo, slug), re.M)
            read_rounds[slug] = pr_watch.review_rounds(f"{slugs[repo]}#{number.group(1)}", pr_watch.gh) if number else 0
            if read_rounds[slug] != int(table_rounds):
                disagree.append((repo, slug, read_rounds[slug], int(table_rounds)))
            reports, _ = rt.events(list(rt.outside_fences(read(repo, slug))))
            if reports - 1 >= rt.REPAIRS or read_rounds[slug] >= rt.REVIEW_ROUNDS:
                fires2.append(slug)
        expect("slice 2 window chief-engineer fires", len(fires2), want["slice2_window_chief_engineer_fires"])
        expect("slice 2 review rounds read live equal the design table, per task", disagree, [])
    print("\nPASS" if not problems else "\nFAIL\n" + "\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
