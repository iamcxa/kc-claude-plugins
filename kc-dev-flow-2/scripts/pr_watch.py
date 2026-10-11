#!/usr/bin/env python3
"""Watch the pull requests FO opened and report what changed since the last look.

  pr_watch.py [--state FILE] add owner/repo#N ...   add PRs to the watch list
  pr_watch.py [--state FILE] check                  print each PR and the changes since the last look
  pr_watch.py [--state FILE] wait [SECONDS]         poll until something changes, print it and exit 0

A merged or closed PR is reported once, then dropped. The codex column comes from the
sibling codex_review.py when it is present. Exit 2 is a configuration error.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

DEFAULT_STATE = Path.home() / ".local/state/kc-dev-flow-2/pr-watch.json"
CODEX = Path(__file__).with_name("codex_review.py")
FIELDS = "state,isDraft,mergeable,headRefOid,statusCheckRollup,title"
TRACKED = ("state", "draft", "mergeable", "checks", "head", "codex")


def gh(*args):
    done = subprocess.run(["gh", *args], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(done.stderr.strip() or "gh failed")
    return json.loads(done.stdout)


def checks(rollup):
    states = [(c.get("conclusion") or c.get("state") or c.get("status") or "").upper() for c in rollup or []]
    if any(s in ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE") for s in states):
        return "failing"
    if any(s in ("", "PENDING", "QUEUED", "IN_PROGRESS", "EXPECTED", "WAITING") for s in states):
        return "pending"
    return "green" if states else "none"


def codex(repo, number):
    if not CODEX.exists():
        return "-"
    done = subprocess.run([sys.executable, str(CODEX), repo, number], capture_output=True, text=True)
    return {0: "clean", 1: "findings", 3: "running", 4: "not-reviewed"}.get(done.returncode, "error")


def look(ref, view=gh, review=codex):
    repo, number = ref.split("#")
    d = view("pr", "view", number, "--repo", repo, "--json", FIELDS)
    snap = {"state": d["state"], "draft": d["isDraft"], "mergeable": d["mergeable"],
            "checks": checks(d["statusCheckRollup"]), "head": d["headRefOid"][:9], "title": d["title"][:60]}
    snap["codex"] = review(repo, number) if d["state"] == "OPEN" else "-"
    return snap


def sweep(state, look=look):
    seen = json.loads(state.read_text()) if state.exists() else {}
    changes, rows = [], []
    for ref, old in seen.items():
        try:
            now = look(ref)
        except (RuntimeError, KeyError, ValueError) as error:
            rows.append(f"{ref}: not read ({str(error)[:80]})")
            continue
        moved = [f"{k} {old.get(k)} -> {now.get(k)}" for k in TRACKED if old.get(k) != now.get(k)]
        if moved:
            changes.append(f"{ref} {now['title']}: " + "; ".join(moved))
        rows.append(f"{ref:34} {now['state']:7} draft={now['draft']!s:5} {now['mergeable']:11} "
                    f"checks={now['checks']:8} codex={now['codex']:12} {now['title']}")
        seen[ref] = now
    reported = {line.split(" ")[0] for line in changes}
    kept = {ref: s for ref, s in seen.items() if s["state"] == "OPEN" or ref in reported}
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps(kept, indent=1))
    return changes, rows, bool(kept)


def main(argv=None, look=look, sleep=time.sleep):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("command", choices=["add", "check", "wait"])
    parser.add_argument("args", nargs="*")
    try:
        opts = parser.parse_args(argv)
    except SystemExit:
        return 2
    try:
        if opts.command == "add":
            if not opts.args or not all("/" in r and "#" in r for r in opts.args):
                print("add needs owner/repo#N")
                return 2
            seen = json.loads(opts.state.read_text()) if opts.state.exists() else {}
            for ref in opts.args:
                seen[ref] = look(ref)
            opts.state.parent.mkdir(parents=True, exist_ok=True)
            opts.state.write_text(json.dumps(seen, indent=1))
            print(f"watching {len(seen)} PR(s)")
            return 0
        if opts.command == "check":
            changes, rows, _ = sweep(opts.state, look)
            print("\n".join(rows + (changes or ["no change since the last look"])))
            return 0
        every = int(opts.args[0]) if opts.args else 60
        while True:
            changes, _, watching = sweep(opts.state, look)
            if changes or not watching:
                print("\n".join(changes) or "watch list is empty")
                return 0
            sleep(every)
    except (RuntimeError, KeyError, ValueError, OSError) as error:
        print(f"configuration error: {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
