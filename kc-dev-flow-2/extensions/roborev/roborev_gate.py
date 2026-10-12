#!/usr/bin/env python3
"""Run one roborev review of a worktree's committed changes since a base and report a bound verdict.

Usage: roborev_gate.py --repo WORKTREE --base SHA [--timeout SECONDS] [--roborev BIN]
Exit 0 clean, 1 findings (the review text follows), 2 bad arguments, 3 incomplete: roborev
missing, its daemon not running, uncommitted changes, a timeout, unreadable output, or a
stored job whose range is not BASE..HEAD. Clean and findings print `evidence=roborev:<job>`.
"""
import argparse
import json
import re
import subprocess
import sys


def run(cmd, timeout=60):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None
    return done


def gate(repo, base, timeout, roborev):
    status = run([roborev, "status"])
    if status is None:
        return 3, "incomplete: roborev is not installed"
    if status.returncode or "Daemon: running" not in status.stdout:
        return 3, "incomplete: the roborev daemon is not running"
    dirty = run(["git", "-C", repo, "status", "--porcelain"])
    if dirty is None or dirty.returncode:
        return 3, f"incomplete: {repo} is not a git worktree"
    if dirty.stdout.strip():
        return 3, "incomplete: commit the changes first; roborev reviews commits, not the working tree"
    head = run(["git", "-C", repo, "rev-parse", "HEAD"]).stdout.strip()
    full_base = run(["git", "-C", repo, "rev-parse", base])
    if full_base is None or full_base.returncode:
        return 2, f"bad --base {base}"
    full_base = full_base.stdout.strip()
    try:
        review = subprocess.run([roborev, "review", "--since", full_base, "--repo", repo, "--wait"],
                                capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 3, f"incomplete: no verdict within {timeout}s"
    job = re.search(r"Enqueued job (\d+)", review.stdout + review.stderr)
    if not job:
        return 3, "incomplete: roborev printed no job id: " + (review.stdout + review.stderr).strip()[-200:]
    shown = run([roborev, "show", "--job", job.group(1), "--json"])
    try:
        record = json.loads(shown.stdout)
    except (AttributeError, ValueError):
        return 3, f"incomplete: job {job.group(1)} has no readable record"
    meta = record.get("job") or {}
    if meta.get("status") != "done" or meta.get("git_ref") != f"{full_base}..{head}":
        return 3, f"incomplete: job {job.group(1)} is {meta.get('status')} for {meta.get('git_ref')}, not {full_base[:9]}..{head[:9]}"
    if record.get("verdict_bool") == 1 and review.returncode == 0:
        return 0, f"clean on {head[:9]}; evidence=roborev:{job.group(1)}"
    if record.get("verdict_bool") == 0:
        return 1, f"findings on {head[:9]}; evidence=roborev:{job.group(1)}\n{record.get('output', '').strip()}"
    return 3, f"incomplete: job {job.group(1)} verdict {record.get('verdict_bool')} with review exit {review.returncode}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--roborev", default="roborev")
    try:
        a = parser.parse_args(argv)
    except SystemExit as stop:
        return 0 if stop.code == 0 else 2
    code, line = gate(a.repo, a.base, a.timeout, a.roborev)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
