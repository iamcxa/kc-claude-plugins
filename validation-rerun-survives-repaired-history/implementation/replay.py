"""Replay the names-only ruling predicate against pinned, disposable state clones."""
import argparse
from collections import Counter
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys

PINS = [("kcp", "aa7119da"), ("qnow", "b99a7543"), ("relay", "916c2d80"),
        ("web", "faf28a25"), ("v0", "887cd65"), ("me", "b98c5f6")]


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.rstrip("\n")


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, path):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = mod.check_validation_rulings([path])
    return {"exit": code, "output": out.getvalue()}


def task_for(root, revision, record):
    folder = Path(record).parent.parent
    options = [folder / "index.md", folder.parent / (folder.name + ".md")]
    present = git(root, "ls-tree", "-r", "--name-only", revision, "--", *map(str, options)).splitlines()
    return next((str(p) for p in options if str(p) in present), None)


def checkout(root, revision, record):
    git(root, "checkout", "--quiet", "--detach", revision)
    path = root / record
    added = not path.exists()
    if added:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    return path, added


def compare(root, revision, record, old, new):
    path, added = checkout(root, revision, record)
    try:
        return [run(mod, path) for mod in (old, new)]
    finally:
        if added:
            path.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scratch", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--only-recorded", action="store_true")
    args = parser.parse_args()
    old = module(args.scratch / "tag/kc-dev-flow-2/scripts/dispatch_records.py", "old")
    new = module(args.candidate, "candidate")
    result = {"recorded": [], "events": [], "pins": {}, "errors": []}
    controls = [("qnow", c, "owner-cancels-booking/dispatch/validation-3.md", a, b)
                for c, a, b in [("f6c94d50", 1, 1), ("78a76aa2", 1, 1),
                                ("03838f91", 2, 2), ("a28d69b5", 2, 2),
                                ("071fe3b6", 2, 0), ("cf9560fc", 2, 0),
                                ("744eaa08", 2, 0), ("5868a574", 2, 0), ("b99a7543", 2, 0)]]
    controls += [("web", "f67a3abe", "number-tag-shows-send-time/dispatch/validation-4.md", 2, 2),
                 ("web", "000a7103", "briefing-frame-and-controls/dispatch/validation-3.md", 2, 2)]
    for key, rev, record, a, b in controls:
        root = args.scratch / key
        pair = compare(root, rev, record, old, new)
        row = {"repo": key, "commit": git(root, "rev-parse", "HEAD"), "record": record, "sides": pair}
        result["recorded"].append(row)
        if [p["exit"] for p in pair] != [a, b] or (a == b and pair[0] != pair[1]):
            result["errors"].append(row)
        print(key, rev, [p["exit"] for p in pair], flush=True)
    if not args.only_recorded:
        for key, pin in PINS:
            root = args.scratch / key
            full = git(root, "rev-parse", pin)
            result["pins"][key] = full
            events = []
            history = git(root, "log", "--reverse", "--format=@@%H", "--name-only", "--diff-filter=A",
                          "--no-renames", full, "--", "*/dispatch/validation-*.md")
            for line in history.splitlines():
                if line.startswith("@@"):
                    rev = line[2:]
                elif re.search(r"/dispatch/validation-[1-9][0-9]*(?:-message-[1-9][0-9]*)?\.md$", line):
                    events.append((rev, line))
            files = git(root, "ls-tree", "-r", "--name-only", full).splitlines()
            for path in files:
                parts = Path(path).parts
                if (path.endswith(".md") and len(parts) == 1 or
                    len(parts) == 2 and parts[0] == "_archive" and path.endswith(".md") or
                    path.endswith("/index.md") and len(parts) <= (3 if parts[0] == "_archive" else 2)):
                    folder = str(Path(path).parent) if parts[-1] == "index.md" else path[:-3]
                    events.append((full, folder + "/dispatch/validation-999.md"))
            for rev, record in events:
                task = task_for(root, rev, record)
                if task is None:
                    result["events"].append({"repo": key, "commit": rev, "record": record, "checked": False})
                    continue
                text = git(root, "show", rev + ":" + task)
                reports = old.validation_reports(text)
                checked = bool(reports and old.open_decisions(reports[-1]))
                row = {"repo": key, "commit": rev, "record": record, "task": task, "checked": checked}
                if checked:
                    row["sides"] = compare(root, rev, record, old, new)
                    a, b = row["sides"]
                    intended = key == "qnow" and "owner-cancels-booking" in task or key == "kcp" and "fo-interviews-extension" in task
                    if (a["exit"] in (0, 1) and a != b or
                        a["exit"] == 2 and (b["exit"] == 0 and not intended or b["exit"] not in (0, 2)) or
                        a["exit"] == b["exit"] and a != b):
                        result["errors"].append(row)
                result["events"].append(row)
            print(key, "events", len(events), "checked", sum(e["checked"] for e in result["events"] if e["repo"] == key), flush=True)
    checked = [e for e in result["events"] if e["checked"]]
    pairs = Counter(str(e["sides"][0]["exit"]) + "->" + str(e["sides"][1]["exit"]) for e in checked)
    result["summary"] = {"events": len(result["events"]), "checked": len(checked), "pairs": dict(pairs),
                         "tasks": len({(e["repo"], Path(e["task"]).stem if not e["task"].endswith("/index.md") else Path(e["task"]).parent.name) for e in checked}),
                         "errors": len(result["errors"])}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["summary"]), flush=True)
    return bool(result["errors"])


if __name__ == "__main__":
    sys.exit(main())
