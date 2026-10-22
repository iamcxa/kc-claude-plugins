#!/usr/bin/env python3
"""Watch the pull requests FO opened and report what changed since the last look.

  pr_watch.py [--state FILE] add [--codex] [--copilot] owner/repo#N ...
                                                    add PRs; --codex / --copilot also read that review
  pr_watch.py [--state FILE] check                  print each PR and the changes since the last look
  pr_watch.py [--state FILE] wait [SECONDS]         poll until an outcome changes, print it and exit 0
  pr_watch.py [--state FILE] tasks WORKFLOW_DIR     read the workflow's tasks and print each next step

Without --state the list is kept per session in ~/.local/state/kc-dev-flow-2/pr-watch/<id>.json, where id is
$CLAUDE_CODE_SESSION_ID (shared by FO, its workers and its background commands), else a hash of the working
directory; the older shared pr-watch.json is not read.

An outcome is a merge or close, a draft flip, a new or cleared conflict, CI turning green
or failing, a Codex verdict, or Copilot answering or refusing the head; a check or review that only
starts is recorded silently.

A PR with no check runs (`checks=none`) has no outcome to wait for. Once it has shown `checks=none` for
60 seconds on the same head and draft state with mergeStateStatus not BLOCKED, the `unchecked` column
reads `settled` and counts as green (the learn extension's no-applicable-checks rule). The 60 seconds is a
bound, not a proof: a check that starts later is missed, and its later green is still reported.

A Codex or Copilot outcome already there when add first looks is printed as "already" and
reported by the next wait, once.

A Codex comment the reader does not recognize (codex=unrecognized(comment:ID)) is not an outcome. If the
next read RECHECK_SECONDS later still finds that comment unrecognized, wait stops once for that comment and
prints it with the next: lines for the merge ask and the report upstream. A look that fails is not a read.

A merged or closed PR is reported once, then dropped. The codex and copilot columns are read
only for a PR added with --codex or --copilot, from that extension's reader when it is
present. Exit 2 is a configuration error.

tasks adds each open task PR to the watch list, with the codex and copilot columns when the workflow README
lists those extensions, and prints one `fact:` line per open task PR (state, draft, checks, reviewer outcomes
with their review id) and one `next:` line per action FO owes: recording a PR a worker opened, marking a green
draft ready, the observer check ahead of the merge sentinel, keeping one wait running, a task's newest
dispatch record that names a package script without a directory (dispatch_records.py --newest), and a
chief-engineer or engineering-reviewer call a live task owes (role_triggers.py, given the number of review ids
that left inline comments on the task's open PR), and one `next:` line per stage where two or more gates
await the Captain (spacedock status --next; SPACEDOCK_BIN names the executable), and one `next:` line naming
each backlog task that is waiting for its gate, holds a `## FO alignment` section and fails
design_surfaces.py check --seed, when the workflow has an ideation stage. It prints no merge-ask
or hold line: FO runs delivery_gate.py under the README. wait prints a `next:` line after each decisive
change. Exit 2 when a task cannot be read.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import re
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
SCRIPTS = Path(__file__).resolve().parent
CODEX = Path(__file__).resolve().parents[1] / "extensions/codex/codex_review.py"
COPILOT = Path(__file__).resolve().parents[1] / "extensions/copilot/copilot_review.py"
SEED = SCRIPTS / "design_surfaces.py"
FO_HEADING = re.compile(r"^## FO alignment[ \t]*$", re.M)
IDEATION_STAGE = re.compile(r"^[ \t]*-[ \t]+name:[ \t]*ideation[ \t]*$", re.M)
FIELDS = "state,isDraft,mergeable,mergeStateStatus,headRefOid,statusCheckRollup,title"
SETTLE_SECONDS = 60
RECHECK_SECONDS = 180
TRACKED = ("state", "draft", "mergeable", "checks", "unchecked", "head", "codex", "codex-evidence",
           "copilot", "copilot-evidence")
OUTCOMES = {"state": None, "draft": None, "mergeable": {"CONFLICTING"},
            "checks": {"failing", "green"}, "unchecked": {"settled"}, "codex": {"clean", "findings", "error"},
            "copilot": {"answered", "not-run", "error"}}


def default_state():
    session = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    key = session if SESSION_ID.fullmatch(session) else \
        "cwd-" + hashlib.sha256(os.path.realpath(os.getcwd()).encode()).hexdigest()[:12]
    return Path.home() / ".local/state/kc-dev-flow-2/pr-watch" / f"{key}.json"


def outcome(key, old, new):
    if key.endswith("-evidence"):
        return new not in ("-", None)
    return key in OUTCOMES and (OUTCOMES[key] is None or new in OUTCOMES[key] or (key == "mergeable" and old == "CONFLICTING"))


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


def reader(script, repo, number, words=None):
    if not script.exists():
        return "-", "-"
    done = subprocess.run([sys.executable, str(script), repo, number], capture_output=True, text=True)
    evidence = (re.findall(r"evidence=(\S+)", done.stdout) or [None])[-1]
    verdict = (words or {0: "clean", 1: "findings", 3: "running", 4: "not-reviewed", 5: "unrecognized"}).get(done.returncode, "error")
    odd = re.findall(r"unrecognized=(\S+)", done.stdout)
    return (f"{verdict}({odd[-1]})" if odd and verdict == "unrecognized" else verdict), evidence or "-"


def codex(repo, number):
    return reader(CODEX, repo, number)


def copilot(repo, number):
    return reader(COPILOT, repo, number, {0: "answered", 3: "requested", 4: "not-reviewed", 5: "not-run"})


def look(ref, view=gh, review=codex, with_codex=False, with_copilot=False, review_copilot=copilot):
    repo, number = ref.split("#")
    d = view("pr", "view", number, "--repo", repo, "--json", FIELDS)
    snap = {"state": d["state"], "draft": d["isDraft"], "mergeable": d["mergeable"],
            "merge-state": d.get("mergeStateStatus", ""), "checks": checks(d["statusCheckRollup"]), "head": d["headRefOid"][:9], "title": d["title"][:60]}
    read = with_codex and d["state"] == "OPEN"
    snap["codex"], snap["codex-evidence"] = review(repo, number) if read else ("-", "-")
    snap["watch-codex"] = with_codex
    read = with_copilot and d["state"] == "OPEN"
    snap["copilot"], snap["copilot-evidence"] = review_copilot(repo, number) if read else ("-", "-")
    snap["watch-copilot"] = with_copilot
    return snap


def settle(snap, old, clock=time.time):
    key = [snap["draft"], snap["head"]]
    quiet = snap["state"] == "OPEN" and snap["checks"] == "none"
    since = old.get("none-since") if old.get("none-key") == key else None
    since = (since if since is not None else clock()) if quiet else None
    snap["none-key"], snap["none-since"] = (key, since) if quiet else (None, None)
    snap["unchecked"] = "settled" if quiet and clock() - since >= SETTLE_SECONDS and snap.get("merge-state") != "BLOCKED" else "-"
    return snap


def round_line(name, snap):
    evidence = snap.get(f"{name}-evidence", "-")
    return f"next: read the {name} round{'' if evidence in ('-', None) else ' ' + evidence} as FO steps: review findings say."


def facts(ref, snap):
    parts = [ref, snap["state"], f"draft={snap['draft']}", f"checks={snap['checks']}"]
    parts += ["unchecked=settled"] if snap.get("unchecked") == "settled" else []
    for name in ("codex", "copilot"):
        if snap.get(f"watch-{name}"):
            evidence = snap.get(f"{name}-evidence", "-")
            parts.append(f"{name}={snap.get(name, '-')}" + ("" if evidence in ("-", None) else f" {evidence}"))
    return "fact: " + " ".join(parts)


def next_for(ref, snap):
    if snap.get("mergeable") == "CONFLICTING":
        return [f"next: tell the Captain {ref} has a conflict."]
    if snap.get("checks") == "failing":
        return [f"next: tell the Captain {ref} has failing CI."]
    green = snap.get("checks") == "green" or (snap.get("checks") == "none" and snap.get("unchecked") == "settled")
    return [f"next: mark {ref} ready if Delivery authority allows."] if green and snap.get("draft") else []


def wait_next(ref, now, decisive):
    if now.get("state") != "OPEN":
        return ["next: run the idle hooks now."]
    lines = [round_line(name, now) for name in ("codex", "copilot") if {name, f"{name}-evidence"} & set(decisive)]
    return lines + (next_for(ref, now) if {"mergeable", "draft", "checks", "unchecked"} & set(decisive) else [])


def unread_lines(state, first, clock, read):
    lines = []
    for ref, snap in load(state).items():
        if ref not in read:
            continue
        word = snap.get("codex", "")
        if not word.startswith("unrecognized(") or snap.get("codex-reported") == word:
            first.pop(ref, None)
            continue
        if first.get(ref, ("", 0))[0] != word:
            first[ref] = (word, clock())
            continue
        if clock() - first[ref][1] < RECHECK_SECONDS:
            continue
        repo, number = ref.split("#")
        lines += [f"{ref} codex={word}: not recognized on two reads {RECHECK_SECONDS}s apart",
                  f"next: quote that comment's raw text, from `gh api repos/{repo}/issues/comments/{word[word.index(':') + 1:-1]} --jq .body`, "
                  "in the merge ask as Codex unread, never clean; the Captain decides.",
                  "next: this is a kc-dev-flow-2 problem, report it upstream with the comment id and its raw text: in the repository "
                  "that holds kc-dev-flow-2 itself, file a backlog task; elsewhere, if `peers` is listed and a kc-dev-flow-2 maintainer FO "
                  "is reachable, send it through `peers`; otherwise draft the issue and ask the Captain whether to file it."]
        update(state, put={ref: {"codex-reported": word}}, keep_flags=True)
    return lines


def load(state):
    return json.loads(state.read_text()) if state.exists() else {}


@contextlib.contextmanager
def locked(state):
    state.parent.mkdir(parents=True, exist_ok=True)
    with open(state.with_name(state.name + ".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def update(state, put=(), drop=(), keep_flags=False, expected=None):
    with locked(state):
        current = load(state)
        for ref, snap in dict(put).items():
            old = current.get(ref, {})
            flags = {k: bool(old.get(k)) or bool(snap.get(k)) for k in {**old, **snap} if k.startswith("watch-")}
            newer = expected is not None and any(old.get(k) != expected.get(ref, {}).get(k) for k in TRACKED)
            current[ref] = {**old, **flags} if newer else {**old, **snap, **flags} if keep_flags else snap
        for ref in drop:
            current.pop(ref, None)
        temp = state.with_name(state.name + ".tmp")
        temp.write_text(json.dumps(current, indent=1))
        os.replace(temp, state)
        return current


def read_flags(known, ref, codex, copilot):
    return (codex or known.get(ref, {}).get("watch-codex", ref in known),
            copilot or known.get(ref, {}).get("watch-copilot", False))


def record(state, known, snaps):
    already = []
    for ref, snap in snaps.items():
        for key in ("codex", "copilot"):
            stored = known.get(ref, {})
            if snap[key] in OUTCOMES[key] and (snap[key], snap[f"{key}-evidence"]) != (
                    stored.get(key), stored.get(f"{key}-evidence")):
                already.append(f"{ref}: {key} {snap[key]} already (wait reports it)")
                snap[key], snap[f"{key}-evidence"] = "-", "-"
    return already, update(state, put=snaps, keep_flags=True)


def sweep(state, look=look, nexts=None, clock=time.time, read=None):
    seen = load(state)
    start = {ref: dict(entry) for ref, entry in seen.items()}
    changes, rows = [], []
    for ref, old in seen.items():
        old = {"unchecked": "-", **old}
        try:
            now = settle(dict(look(ref, with_codex=old.get("watch-codex", True), with_copilot=old.get("watch-copilot", False))), old, clock)
        except (RuntimeError, KeyError, ValueError) as error:
            rows.append(f"{ref}: not read ({str(error)[:80]})")
            continue
        moved = [k for k in TRACKED if old.get(k) != now.get(k)]
        if moved:
            line = f"{ref} {now['title']}: " + "; ".join(f"{k} {old.get(k)} -> {now.get(k)}" for k in moved)
            decisive = [k for k in moved if outcome(k, old.get(k), now.get(k))]
            changes.append((line, bool(decisive)))
            if decisive and nexts is not None:
                nexts.extend(n for n in wait_next(ref, now, decisive) if n not in nexts)
        if read is not None:
            read.add(ref)
        rows.append(f"{ref:34} {now['state']:7} draft={now['draft']!s:5} {now['mergeable']:11} "
                    f"checks={now['checks']:8} codex={now['codex']:12} "
                    f"copilot={now.get('copilot', '-'):12} {now['title']}")
        seen[ref] = {**old, **now}
    reported = {line.split(" ")[0] for line, _ in changes}
    done = [ref for ref, s in seen.items() if s["state"] != "OPEN" and ref not in reported]
    current = update(state, put={r: s for r, s in seen.items() if r not in done}, drop=done, keep_flags=True, expected=start)
    return changes, rows, bool(current)


def front(path):
    lines = path.read_text(errors="replace").split("\n")
    found = {}
    for line in lines[1:] if lines and lines[0] == "---" else []:
        if line == "---":
            break
        match = re.match(r"^([\w-]+):[ \t]*(.*?)[ \t]*$", line)
        if match:
            found[match.group(1)] = match.group(2).strip("'\"")
    return found


def git(*args):
    done = subprocess.run(["git", *args], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(done.stderr.strip() or f"git {args[2] if len(args) > 2 else ''} failed")
    return done.stdout.strip()


def toplevel(workflow):
    return Path(git("-C", str(workflow), "rev-parse", "--show-toplevel"))


def repo_of(worktree, ask):
    url = git("-C", str(worktree), "remote", "get-url", "origin")
    return ask("repo", "view", url, "--json", "nameWithOwner")["nameWithOwner"]


def review_rounds(ref, ask):
    repo, number = ref.split("#")
    pages = ask("api", f"repos/{repo}/pulls/{number}/comments", "--paginate", "--slurp")
    return len({c["pull_request_review_id"] for page in pages for c in page})


def opened_pr(worktree, ask):
    repo = repo_of(worktree, ask)
    branch = git("-C", str(worktree), "branch", "--show-current")
    listed = ask("pr", "list", "--repo", repo, "--head", branch, "--state", "all", "--json", "number,state")
    found = [p for p in listed if p["state"] in ("OPEN", "MERGED")]
    return f"{repo}#{found[0]['number']}" if found else None


def entities(state):
    found = {}
    for path in sorted(state.iterdir()):
        name = path.name
        if name.startswith(".") or name in ("_archive", "_mods"):
            continue
        if path.is_dir() and (path / "index.md").is_file():
            found[name] = path / "index.md"
        elif path.is_file() and name.endswith(".md") and name != "README.md":
            found.setdefault(path.stem, path)
    return sorted(found.items())


def ready_rows(workflow):
    binary = os.environ.get("SPACEDOCK_BIN") or "spacedock"
    done = subprocess.run([binary, "status", "--workflow-dir", str(workflow), "--next", "--json"], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError((done.stderr or done.stdout).strip()[:120] or "spacedock status --next failed")
    return json.loads(done.stdout)["ready_gates"]


def sittings(rows):
    waiting = {}
    for gate in rows:
        if gate["readiness"] == "awaiting-captain":
            waiting.setdefault(gate["current"], []).append(gate["slug"])
    return [f"next: {len(slugs)} gates await the Captain at {stage} ({', '.join(slugs)}); unless already presented, "
            "present them in one message and record each with his one answer."
            + (" Name the merge order and each shared file from Batch overlap." if stage == "validation" else "")
            for stage, slugs in waiting.items() if len(slugs) > 1]


def seeds(rows, found, readme):
    if not IDEATION_STAGE.search(readme):
        return [], []
    failing, errors = [], []
    for row in rows:
        task = found.get(row.get("slug"))
        if row.get("current") != "backlog" or row.get("readiness") != "needs-preparation" or not task:
            continue
        try:
            if not FO_HEADING.search(task.read_text(errors="replace")):
                continue
            done = subprocess.run([sys.executable, str(SEED), "check", "--seed", str(task)], capture_output=True, text=True)
        except OSError as error:
            errors.append(f"next: report {row['slug']} to the Captain: {str(error)[:120]}.")
            continue
        if done.returncode == 1 and done.stdout.strip():
            failing.append(row["slug"])
        elif done.returncode:
            why = ((done.stdout or done.stderr).strip().splitlines() or [f"exit {done.returncode}"])[-1]
            errors.append(f"next: report {row['slug']} to the Captain: {why[:120]}.")
    line = [f"next: the seed check fails for these backlog tasks ({', '.join(failing)}); before preparing the gate of one, "
            f"fix its ## FO alignment and run `python3 {SEED} check --seed <task>`."] if failing else []
    return line, errors


def tasks(opts, look=look, ask=gh, clock=time.time):
    workflow = Path(opts.args[0]).resolve()
    readme = front(workflow / "README.md")
    state = workflow / readme["state"] if readme.get("state") else workflow
    listed = set(re.findall(r"[\w-]+", readme.get("extensions", "")))
    wait = f"python3 {SCRIPTS / 'pr_watch.py'}" + (f" --state {shlex.quote(str(opts.state))}" if opts.given else "")
    out, snaps, errors, live, rounds = [], {}, [], [], {}
    found = entities(state)
    for slug, task in found:
        meta = front(task)
        if "status" not in meta:
            continue
        live.append(slug)
        if (state / slug / "dispatch").is_dir():
            done = subprocess.run([sys.executable, str(SCRIPTS / "dispatch_records.py"), "--newest", str(state), slug],
                                  capture_output=True, text=True)
            hits = re.findall(r"^(.+?):\d+: bare package script name (\S+)$", done.stdout, re.M)
            if done.returncode == 1 and hits:
                names = ", ".join(dict.fromkeys(name for _, name in hits))
                out.append(f"next: {slug}'s newest dispatch record {hits[0][0]} names {names} without a directory; "
                           "if its worker is live, send a follow-up writing each with its absolute package path "
                           "and save it as the next record, else do nothing.")
            elif done.returncode:
                errors.append(f"next: report {slug} to the Captain: {(done.stdout or done.stderr).strip()[:120]}.")
        pr = meta.get("pr", "")
        try:
            where = toplevel(workflow) / meta["worktree"] if not pr and meta.get("worktree") else None
            if where and not where.is_dir():
                out.append(f"next: record {slug}'s PR with status --set {slug} pr=<owner/repo>#<N>; its worktree is not on this machine.")
            elif where:
                ref = opened_pr(where, ask)
                if ref:
                    out += [f"next: run `spacedock status --workflow-dir {shlex.quote(str(workflow))} --set {slug} pr={ref}`.",
                            f"next: run `spacedock state commit {slug} --workflow-dir {shlex.quote(str(workflow))}`."]
                    pr = ref
            qualified = re.fullmatch(r"([\w.-]+/[\w.-]+)#(\d+)", pr)
            bare = re.fullmatch(r"#?(\d+)", pr)
            if not (qualified or bare):
                continue
            ref = pr if qualified else f"{repo_of(toplevel(workflow), ask)}#{bare.group(1)}"
            known = load(opts.state)
            codex, copilot = read_flags(known, ref, "codex" in listed, "copilot" in listed)
            now = settle(dict(look(ref, with_codex=codex, with_copilot=copilot)), known.get(ref, {}), clock)
            if now["state"] == "OPEN":
                rounds[slug] = review_rounds(ref, ask)
        except (RuntimeError, KeyError, ValueError, OSError) as error:
            errors.append(f"next: report {slug} to the Captain: {str(error)[:120]}.")
            continue
        if now["state"] == "OPEN":
            snaps[ref] = now
            out += [facts(ref, now)] + next_for(ref, now)
        elif now["state"] == "MERGED" and "learn" in listed:
            done = subprocess.run([sys.executable, str(SCRIPTS / "observer_check.py"), str(state), slug],
                                  capture_output=True, text=True)
            if done.returncode:
                out += [f"next: keep {slug} out of pr-merge's scan in this pass.", *done.stdout.splitlines()]
            else:
                check = f"python3 {SCRIPTS / 'observer_check.py'} {shlex.quote(str(state))} {slug}"
                out += [f"next: let pr-merge record {slug}.", f"after pr-merge: run `{check}`.",
                        "after pr-merge: do each next: line it prints."]
    for slug in live:
        asked = [] if slug not in rounds else ["--review-rounds", str(rounds[slug])]
        done = subprocess.run([sys.executable, str(SCRIPTS / "role_triggers.py"), str(state), slug, *asked], capture_output=True, text=True)
        if done.returncode == 1:
            out += done.stdout.splitlines()
        elif done.returncode:
            errors.append(f"next: report {slug} to the Captain: {(done.stdout or done.stderr).strip()[:120]}.")
    try:
        rows = ready_rows(workflow)
        out += sittings(rows)
    except (RuntimeError, KeyError, ValueError, OSError) as error:
        errors.append(f"next: report the awaiting gates to the Captain: {str(error)[:120]}.")
    else:
        line, broken = seeds(rows, dict(found), (workflow / "README.md").read_text(errors="replace"))
        out += line
        errors += broken
    if snaps:
        already, _ = record(opts.state, load(opts.state), snaps)
        out += already + [f"next: run `{wait} wait` in the background, unless one is running.",
                          "next: when it exits, do the next: lines it prints."]
    if out or errors:
        print("\n".join(out + errors))
    return 2 if errors else 0


def main(argv=None, look=look, sleep=time.sleep, ask=gh, clock=time.time):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--state", type=Path)
    parser.add_argument("command", choices=["add", "check", "wait", "tasks"])
    parser.add_argument("--codex", action="store_true")
    parser.add_argument("--copilot", action="store_true")
    parser.add_argument("args", nargs="*")
    try:
        opts = parser.parse_intermixed_args(argv)
    except SystemExit as stop:
        return 0 if stop.code == 0 else 2
    opts.given = opts.state is not None
    opts.state = opts.state or default_state()
    try:
        if opts.command == "tasks":
            if len(opts.args) != 1:
                print("tasks needs one workflow directory")
                return 2
            return tasks(opts, look, ask, clock)
        if opts.command == "add":
            if not opts.args or not all("/" in r and "#" in r for r in opts.args):
                print("add needs owner/repo#N")
                return 2
            known = load(opts.state)
            first = {}
            for ref in opts.args:
                codex, copilot = read_flags(known, ref, opts.codex, opts.copilot)
                first[ref] = settle(dict(look(ref, with_codex=codex, with_copilot=copilot)), known.get(ref, {}), clock)
            already, seen = record(opts.state, known, first)
            print("\n".join(already + [f"watching {len(seen)} PR(s)"]))
            return 0
        if opts.command == "check":
            changes, rows, _ = sweep(opts.state, look, clock=clock)
            print("\n".join(rows + ([line for line, _ in changes] or ["no change since the last look"])))
            return 0
        every = int(opts.args[0]) if opts.args else 60
        first = {}
        while True:
            nexts, read = [], set()
            changes, _, watching = sweep(opts.state, look, nexts, clock, read)
            if any(decisive for _, decisive in changes) or not watching:
                print("\n".join([line for line, _ in changes] + nexts or ["watch list is empty"]))
                return 0
            gave_up = unread_lines(opts.state, first, clock, read)
            if gave_up:
                print("\n".join([line for line, _ in changes] + gave_up))
                return 0
            sleep(every)
    except (RuntimeError, KeyError, ValueError, OSError) as error:
        print(f"configuration error: {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
