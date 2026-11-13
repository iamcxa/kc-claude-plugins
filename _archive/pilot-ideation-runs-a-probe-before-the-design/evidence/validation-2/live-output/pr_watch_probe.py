#!/usr/bin/env python3
"""Disposable, offline entrypoint probe; no application test suites."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(os.environ["REPLAY_ROOT"]).resolve()
PACKAGE = ROOT / "package/kc-dev-flow-2"
WT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
MODE = sys.argv[1]

def git(*args):
    return subprocess.check_output(["git", "-C", str(WT), *args], text=True).strip()

def invoke(case, mutant=False):
    source = PACKAGE / "scripts/pr_watch.py"
    namespace = {"__file__": str(source), "__name__": "replay_pr_watch"}
    text = source.read_text()
    if mutant:
        old = 'out.append(f"fact: {slug} has no recorded PR; its worktree is not on this machine.")'
        new = 'out.append(f"next: record {slug}\\\'s PR with status --set {slug} pr=<owner/repo>#<N>; its worktree is not on this machine.")'
        assert text.count(old) == 1
        text = text.replace(old, new)
    exec(compile(text, str(source), "exec"), namespace)
    namespace["scratch"].BASE = case / "absent-scratch"
    return namespace["main"](["--state", str(case / "watch.json"), "tasks", str(case / "wf")])

if MODE == "--invoke":
    sys.exit(invoke(Path(sys.argv[2]), "--mutant" in sys.argv))

def fixture(name, tasks):
    case = WT / ".replay-fixtures" / name
    if case.exists():
        raise RuntimeError("Existing fixture will not be overwritten: " + str(case))
    (case / "wf").mkdir(parents=True)
    (case / "bin").mkdir()
    (case / "wf/README.md").write_text("---\nentity-type: task\nextensions: []\nstages:\n  states:\n    - name: implementation\n    - name: validation\n---\n")
    for slug, fields, folder in tasks:
        p = case / "wf" / (slug + "/index.md" if folder else slug + ".md")
        p.parent.mkdir(exist_ok=True)
        p.write_text("---\ntitle: " + slug + "\nstatus: validation\n" + fields + "---\n\nbody\n")
    sd = case / "bin/spacedock"
    sd.write_text("#!/usr/bin/env python3\nimport json,sys\nassert sys.argv[1]=='status'\nassert not any(x in sys.argv for x in ['--set','--advance','--archive'])\nprint(json.dumps({'ready_gates':[]} if '--next' in sys.argv else {'entities':[]}))\n")
    gh = case / "bin/gh"
    gh.write_text("""#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
a=sys.argv[1:]
with open(os.environ['PROBE_CALLS'],'a') as f:f.write(json.dumps(a)+'\\n')
answers=json.loads(Path(os.environ['PROBE_ANSWERS']).read_text())
key=' '.join(a[:3] if a[:2]==['pr','view'] else a[:2])
if key not in answers:raise SystemExit('unexpected provider command: '+str(a))
print(json.dumps(answers[key]))
""")
    sd.chmod(0o755)
    gh.chmod(0o755)
    (case / "answers.json").write_text("{}")
    git("add", str(case / "wf"))
    git("-c", "user.name=Replay", "-c", "user.email=replay@localhost",
        "commit", "-qm", "test(replay): commit synthetic " + name, "--", str(case / "wf"))
    return case

def run(case, answers=None, mutant=False):
    if answers is not None:
        (case / "answers.json").write_text(json.dumps(answers))
    before = {str(p.relative_to(case)): p.read_bytes() for p in (case / "wf").rglob("*") if p.is_file()}
    env = dict(os.environ, PATH=str(case / "bin") + os.pathsep + os.environ["PATH"],
               SPACEDOCK_BIN=str(case / "bin/spacedock"), PROBE_CALLS=str(case / "calls.jsonl"),
               PROBE_ANSWERS=str(case / "answers.json"), PYTHONDONTWRITEBYTECODE="1",
               TMPDIR=str(ROOT / "tmp"))
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "--invoke", str(case)]
    if mutant:
        argv.append("--mutant")
    result = subprocess.run(argv, env=env, cwd=WT, capture_output=True, text=True, timeout=30)
    label = case.name + ("-mutant" if mutant else "")
    (EVIDENCE / (label + ".stdout")).write_text(result.stdout)
    (EVIDENCE / (label + ".stderr")).write_text(result.stderr)
    calls = (case / "calls.jsonl").read_text().splitlines() if (case / "calls.jsonl").exists() else []
    after = {str(p.relative_to(case)): p.read_bytes() for p in (case / "wf").rglob("*") if p.is_file()}
    assert before == after, "workflow input changed"
    row = dict(command=argv, exit=result.returncode, stdout=label + ".stdout", stderr=label + ".stderr",
               input_unchanged=True, provider_calls=calls, watch_exists=(case / "watch.json").exists())
    with (EVIDENCE / "commands.jsonl").open("a") as f:
        f.write(json.dumps(row) + "\n")
    assert result.returncode == 0, row
    return result.stdout.splitlines(), row

def snapshot(state="OPEN"):
    return dict(state=state, isDraft=True, mergeable="MERGEABLE", mergeStateStatus="CLEAN",
                headRefOid="a"*40, statusCheckRollup=[dict(conclusion="SUCCESS")], title="synthetic")

result = {}
if MODE == "AC-1":
    for name, fields, folder in [
        ("absent-flat", "pr: \nworktree: .missing-probe-flat\n", False),
        ("absent-folder", "pr: \nworktree: " + str(ROOT / "tmp/missing-probe-folder") + "\n", True),
    ]:
        case = fixture(name, [(name, fields, folder)])
        lines, row = run(case)
        expected = ["fact: " + name + " has no recorded PR; its worktree is not on this machine."]
        assert lines == expected and not row["provider_calls"] and not row["watch_exists"], row
        changed, mutation = run(case, mutant=True)
        assert changed != expected and any(s.startswith("next: record ") for s in changed)
        result[name] = dict(observed=lines, reverse_mutation_rejected=True)
elif MODE == "AC-2":
    case = fixture("no-worktree", [("bare", "pr: \n", False)])
    lines, row = run(case)
    assert lines == [] and row["provider_calls"] == [] and not row["watch_exists"]
    result["no-worktree"] = lines
    case = fixture("local-discovery", [("local", "pr: \nworktree: .\n", False)])
    answers = {"repo view": {"nameWithOwner": "fixture/repo"}, "pr list": [{"state": "OPEN", "number": 7}],
               "pr view 7": snapshot(), "api repos/fixture/repo/pulls/7/comments": [[]]}
    lines, row = run(case, answers)
    assert any("--set local pr=fixture/repo#7" in s for s in lines)
    assert any("spacedock state commit local" in s for s in lines)
    assert "next: mark fixture/repo#7 ready if Delivery authority allows." in lines
    assert row["watch_exists"]
    result["local-discovery"] = lines
    case = fixture("recorded-pr", [("known", "pr: fixture/repo#7\nworktree: .missing-known\n", False)])
    lines, row = run(case, {"pr view 7": snapshot(), "api repos/fixture/repo/pulls/7/comments": [[]]})
    assert any(s.startswith("fact: fixture/repo#7 OPEN") for s in lines)
    assert not any("--set known" in s or "record known" in s for s in lines)
    result["recorded-pr"] = lines
    case = fixture("merged-pr", [("merged", "pr: fixture/repo#7\nworktree: .missing-merged\n", False)])
    lines, row = run(case, {"pr view 7": snapshot("MERGED")})
    assert lines == []
    case = fixture("after-archive", [])
    lines, row = run(case)
    assert lines == [] and not row["watch_exists"]
elif MODE == "AC-3":
    base = git("rev-parse", "origin/main")
    source = (PACKAGE / "scripts/pr_watch.py").read_bytes()
    pinned = subprocess.check_output(["git", "-C", str(WT), "show", base + ":kc-dev-flow-2/scripts/pr_watch.py"])
    assert source == pinned
    regression = git("show", base + ":kc-dev-flow-2/scripts/test_pr_watch.py")
    assert "def test_an_empty_pr_whose_worktree_is_gone_is_a_fact_and_one_with_no_worktree_field_stays_silent" in regression
    assert not git("diff", base, "--", "kc-dev-flow-2")
    result = dict(base=base, package_source_sha256=hashlib.sha256(source).hexdigest(),
                  product_diff="empty", regression="present, not run", suites="not run",
                  private_adopters_available=0, private_adopters_unavailable=3)
elif MODE == "AC-4":
    product = WT / "kc-dev-flow-2"
    readme = (product / "references/sd/workflow.md").read_text()
    mod = (product / "references/sd/mods/kc-dev-flow-2.md").read_text()
    base = git("rev-parse", "origin/main")
    for relative in ("references/sd/workflow.md", "references/sd/mods/kc-dev-flow-2.md"):
        pinned = subprocess.check_output(["git", "-C", str(WT), "show", base + ":kc-dev-flow-2/" + relative])
        assert (product / relative).read_bytes() == pinned
    # A fixed reader set makes the comparison reproducible, without claiming live FO behavior.
    for moment, log in [("startup", "absent-flat"), ("idle-open", "local-discovery"),
                        ("idle-merged", "merged-pr"), ("after-archive", "after-archive")]:
        output = (EVIDENCE / (log + ".stdout")).read_text()
        words = len((readme + "\n" + mod + "\n" + output).split())
        result[moment] = dict(before=words, after=words, delta=0,
                              reader_set="full workflow + lifecycle mod + synthetic tasks output")
    result["merge-ask"] = dict(before="Not provable now", after="Not provable now",
                              reason="no pending approved delivery; source unchanged")
else:
    raise SystemExit("unknown criterion")
(EVIDENCE / (MODE + ".json")).write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(dict(criterion=MODE, passed=True, result=result), indent=2))
