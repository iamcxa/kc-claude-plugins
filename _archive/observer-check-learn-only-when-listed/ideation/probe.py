#!/usr/bin/env python3
"""Local probe. Real-adopter output contains counts, never task names or raw output."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


BASE = "8125e6d516d32abbf79c6772de10cde2c20900a8"
REL = "kc-dev-flow-2/scripts/observer_check.py"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "Probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
       "GIT_COMMITTER_NAME": "Probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid",
       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
       "PYTHONDONTWRITEBYTECODE": "1"}


def run(argv, **kwargs):
    return subprocess.run(list(map(str, argv)), capture_output=True, text=True, env=ENV, timeout=30, **kwargs)


def git(repo, *args):
    done = run(["git", "-C", repo, *args])
    if done.returncode:
        raise RuntimeError("git read or synthetic-fixture command failed")
    return done.stdout


def invoke(script, state, slug, *args):
    done = run([sys.executable, script, state, slug, *args])
    return done.returncode, done.stdout


def without_learn(text):
    return "".join(line for line in text.splitlines(keepends=True)
                   if "kc-dev-flow-2:learn" not in line and "learn's notice" not in line)


def fixture(root, base, candidate, emit=True):
    results = []
    for form, field, enabled in [("absent", "", False), ("empty", "extensions: []\n", False),
                                  ("other", "extensions: [peers]\n", False),
                                  ("inline", "extensions: [learn]\n", True),
                                  ("quoted", "extensions: ['learn'] # chosen\n", True),
                                  ("block", 'extensions:\n  - "learn" # chosen\n', True)]:
        for report, content in [("missing", None), ("blank", "\n"), ("present", "ok\n"),
                                ("waiver", "observer not run: fixture\n")]:
            home = root / (form + "-" + report)
            state = home / "state"
            (state / "_archive" / "example").mkdir(parents=True)
            readme = home / "README.md"
            readme.write_text(f"---\nentity-type: task\n{field}---\nlearn mentioned in prose\n")
            git(state, "init", "-b", "main")
            (state / "_archive/example.md").write_text("---\ntitle: example\n---\n")
            if content is not None:
                (state / "_archive/example/observer.md").write_text(content)
            git(state, "add", "--", "_archive")
            git(state, "commit", "-m", "synthetic archive")
            before = invoke(base, state, "example")
            after = invoke(candidate, state, "example")
            expected = before if enabled else (before[0], without_learn(before[1]))
            results.append({"case": form + "/" + report, "passed": after == expected,
                            "base_exit": before[0], "probe_exit": after[0],
                            "base_words": len(before[1].split()), "probe_words": len(after[1].split())})
    if emit:
        print(json.dumps({"cases": results, "passed": sum(x["passed"] for x in results), "total": len(results)}, indent=2))
    return all(x["passed"] for x in results)


def real(base, candidate, workflows):
    results = []
    for workflow in workflows:
        state = workflow / ".spacedock-state"
        files = git(state, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
        slugs = sorted({p.split("/")[1][:-3] for p in files if p.startswith("_archive/")
                        and len(p.split("/")) == 2 and p.endswith(".md")}
                       | {p.split("/")[1] for p in files if p.startswith("_archive/") and p.endswith("/index.md")
                          and len(p.split("/")) == 3})
        counts = {"archived_tasks": len(slugs), "identical": 0, "different": 0, "base_exit_0": 0,
                  "base_exit_1": 0, "base_exit_2": 0, "probe_exit_0": 0, "probe_exit_1": 0, "probe_exit_2": 0}
        for slug in slugs:
            before = invoke(base, state, slug)
            after = invoke(candidate, state, slug, "--readme", workflow / "README.md")
            counts["identical" if before == after else "different"] += 1
            for name, result in [("base", before), ("probe", after)]:
                counts[f"{name}_exit_{result[0]}"] += 1
        results.append(counts)
    print(json.dumps({"corpora": results}, indent=2))
    return all(row["archived_tasks"] > 0 and row["different"] == 0 for row in results)


def historical(root, base, candidate, workflow, before):
    repo = Path(git(workflow, "rev-parse", "--show-toplevel").strip())
    path = (workflow / "README.md").relative_to(repo)
    rev = git(repo, "log", "-1", "--format=%H", f"--before={before}", "--", str(path)).strip()
    readme = root / "historical-readme.md"
    readme.write_text(git(repo, "show", f"{rev}:{path}"))
    assert not any(x.startswith("extensions:") for x in readme.read_text().splitlines())
    state = workflow / ".spacedock-state"
    files = git(state, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    slugs = sorted({p.split("/")[1][:-3] for p in files if p.startswith("_archive/")
                    and len(p.split("/")) == 2 and p.endswith(".md")})
    counts = {"archived_tasks": len(slugs), "intended_changes": 0, "unexpected_changes": 0,
              "exact_original_case_in_current_tree": sum("first-publish-reads-right" in p for p in files)}
    for slug in slugs:
        before = invoke(base, state, slug)
        after = invoke(candidate, state, slug, "--readme", readme)
        good = after == (before[0], without_learn(before[1])) and after != before
        counts["intended_changes" if good else "unexpected_changes"] += 1
    print(json.dumps(counts, indent=2))
    return len(slugs) > 0 and counts["unexpected_changes"] == 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["fixtures", "real", "historical", "mutation"])
    p.add_argument("--code", type=Path, required=True)
    p.add_argument("--scratch", type=Path, required=True)
    p.add_argument("--workflow", type=Path, action="append", default=[])
    p.add_argument("--readme-before")
    a = p.parse_args()
    a.scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="run-", dir=a.scratch) as scratch:
        root = Path(scratch)
        base = root / "base.py"
        base.write_text(git(a.code, "show", f"{BASE}:{REL}"))
        candidate = a.code / REL
        if a.mode == "mutation":
            mutated = root / "mutated.py"
            text = candidate.read_text().replace('return "learn" in readme_extensions(readme)', 'return True')
            assert text != candidate.read_text()
            mutated.write_text("import sys\nsys.path.insert(0, " + repr(str(candidate.parent)) + ")\n" + text)
            ok = not fixture(root, base, mutated, emit=False)
            print(json.dumps({"unconditional_learn_mutation_detected": ok}))
        else:
            ok = (fixture(root, base, candidate) if a.mode == "fixtures" else
              real(base, candidate, a.workflow) if a.mode == "real" else
              historical(root, base, candidate, a.workflow[0], a.readme_before))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
