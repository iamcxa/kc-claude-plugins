#!/usr/bin/env python3
"""Replay PR #841's merge ask through a delivery_gate.py.

Usage: replay_841.py <delivery_gate.py> <out.log> [--trunk SHA --status S] [--result FILE] [--not-run]

Builds a throwaway fixture: the task file and folder at state commit b3e749c2 (the
commit the #841 validation briefing names), the workflow README at e8664a72 (the
validation dispatch commit), the gate text = the bound question + briefing summary (state-checkout
absolute paths rewritten to the fixture),
and a stub `gh` serving the PR facts saved in pr841-facts/. Two facts are set to
their ask-time values because #841 is merged now: state OPEN and mergeable
MERGEABLE (merge/ask-1.json exists, and check writes it only when mergeable).
--trunk/--status set what the compare call returns; default eeee0023 diverged,
the trunk tip at the ask (2026-11-11T08:52:08Z).
"""
import json, os, shutil, stat, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE.parents[1]
CODE = Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo")
SLUG = "budget-overrun-holds-and-findings-meet-non-goals"
STATE_COMMIT = "b3e749c251b876ebdbe47864fe91befb9d4b5bb7"
HEAD = "6da9a765ee04e1e2c7836517ba01f75b0ea91d73"

STUB = r'''#!/usr/bin/env python3
import json, os, sys
d, a = os.environ["STUB_DIR"], sys.argv[1:]
open(os.path.join(d, "calls.log"), "a").write(" ".join(a) + "\n")
j = " ".join(a)
if a[:2] == ["pr", "view"]:
    data = json.load(open(os.path.join(d, "pr.json")))
    print(json.dumps({k: data[k] for k in a[a.index("--json") + 1].split(",") if k in data}))
elif a[:2] == ["pr", "checks"]:
    print(open(os.path.join(d, "required.json")).read())
elif a[0] == "api" and "/compare/" in j:
    print(open(os.path.join(d, "compare.json")).read())
elif a[0] == "api" and "actions/runs" in j:
    print(open(os.path.join(d, "runs.json")).read())
elif a[0] == "api" and "/contents/" in j:
    print(open(os.path.join(d, "adr.txt")).read())
elif a[0] == "api" and "/files" in j:
    print(open(os.path.join(d, "files.json")).read())
else:
    sys.exit(1)
'''


def main():
    gate, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    rest = sys.argv[3:]
    trunk = rest[rest.index("--trunk") + 1] if "--trunk" in rest else "eeee002303aca7c14237258253cd9318a5b3248c"
    status = rest[rest.index("--status") + 1] if "--status" in rest else "diverged"
    result = Path(rest[rest.index("--result") + 1]).resolve() if "--result" in rest else None
    d = Path(tempfile.mkdtemp(prefix="replay-841-"))
    try:
        state = d / "state"
        state.mkdir()
        archive = subprocess.run(["git", "-C", str(STATE), "archive", STATE_COMMIT, f"{SLUG}.md", SLUG], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", str(state)], input=archive.stdout, check=True)
        shutil.rmtree(state / SLUG / "merge", ignore_errors=True)
        readme = subprocess.run(["git", "-C", str(CODE), "show", "e8664a72b0f904e5dda3c391d52ab3abaca876b4:docs/dev2/README.md"],
                                capture_output=True, text=True, check=True).stdout
        (state / "README.md").write_text(readme)
        if result:
            (state / SLUG / "merge").mkdir(parents=True, exist_ok=True)
            shutil.copy(result, state / SLUG / "merge" / "result-1.json")
        git = ["git", "-c", "user.name=replay", "-c", "user.email=replay@invalid", "-C", str(state)]
        subprocess.run(git[:-2] + ["init", "-q", str(state)], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-qm", "fixture"], check=True)
        brief = json.loads((STATE / "_archive" / SLUG / "review/validation/briefing-1/index.json").read_text())
        text = brief["question"] + "\n" + brief["artifacts"][0]["summary"] + "\n"
        text = text.replace(str(STATE) + "/", str(state) + "/")
        if "--not-run" in rest:
            text += "Merge result: not run: the replay states that no test ran on the merge result.\n"
        (d / "gate.txt").write_text(text)
        stub, bin_dir = d / "stub", d / "bin"
        stub.mkdir(); bin_dir.mkdir()
        facts = HERE / "pr841-facts"
        for name in ("files.json", "runs.json", "adr.txt", "required.json"):
            shutil.copy(facts / name, stub / name)
        pr = json.loads((facts / "pr.json").read_text())
        pr.update(state="OPEN", mergeable="MERGEABLE")
        (stub / "pr.json").write_text(json.dumps(pr))
        (stub / "compare.json").write_text(json.dumps({"status": status, "base_commit": {"sha": trunk}}))
        (bin_dir / "gh").write_text(STUB)
        (bin_dir / "gh").chmod(stat.S_IRWXU)
        env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}", STUB_DIR=str(stub))
        done = subprocess.run([sys.executable, "-B", str(gate), "check", str(state / f"{SLUG}.md"), "--pr", f"iamcxa/kc-claude-plugins#841",
                               "--text-file", str(d / "gate.txt"), "--head", HEAD], capture_output=True, text=True, env=env)
        out.write_text(f"$ delivery_gate.py check (gate={gate}, trunk={trunk}, status={status}, result={result}, not_run={'--not-run' in rest})\n"
                       f"exit={done.returncode}\n{done.stdout}{done.stderr}")
        print(f"exit={done.returncode} -> {out}")
        return done.returncode
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
