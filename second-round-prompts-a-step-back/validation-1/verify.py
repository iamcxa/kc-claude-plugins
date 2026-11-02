import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

WT = Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back/.context/validation-1-worktree")
P = WT / "kc-dev-flow-2/scripts"
S = Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
ROOT = Path(__file__).resolve().parent
BASE = "3c49c24a3eba3d90093f330c051b682a3335ae23"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
QUESTIONS = ("is what I am solving still the outcome first asked for", "can this gap be tested now, or am I waiting",
             "what breaks if this criterion or process is deleted?")


def run(*args):
    return subprocess.run(list(map(str, args)), capture_output=True, text=True, env=ENV, cwd=WT)


cases = [
    ("paseo-codex-dispatch-practice", "e0dc64f886cf80e7579551a4002a05b4c603f1c9", 0, True),
    ("paseo-codex-dispatch-practice", "1e17be9a0734eb1b122b83335bb7ff96a3a331cb", 0, False),
    ("adr-reserved-when-design-names-one", "c03f77631e6fa06afdaa275ecb3f05559314f9c6", 0, False),
    ("read-adr-honors-adr-folder", "95c1ecc8b1f0477c8c986ee2895b00e8d105b69e", 0, True),
    ("peers-paseo-rule-matches-practice", "ff2063c539a2fbf8c446797d7051fc34c406aff9", 0, True),
    ("paseo-codex-dispatch-practice", "0e5b6f59a8e5a067b2739bf1b78863d96399240f", 1, False),
    ("peers-paseo-rule-matches-practice", "7d203d562789a107d651f3169b6a89b153024d33", 1, False),
    ("peers-paseo-rule-matches-practice", "f0203ee02", 0, False),
]
logs = []
for slug, rev, code, reminder in cases:
    done = run(sys.executable, "-B", P / "role_triggers.py", S, slug, "--rev", rev)
    assert done.returncode == code, done.stdout + done.stderr
    assert ("before the next step" in done.stdout) == reminder, done.stdout
    if reminder or code:
        assert all(q in done.stdout for q in QUESTIONS), done.stdout
    sizes = [len(line.split()) for line in done.stdout.splitlines() if line.startswith("next:")]
    logs.append(f"{slug} {rev} exit={code} words={sizes}\n{done.stdout}")
base = run("git", "show", f"{BASE}:kc-dev-flow-2/scripts/role_triggers.py")
assert base.returncode == 0, base.stderr
(ROOT / "base_role_triggers.py").write_text(base.stdout)
for index in (1, 2, 7):
    slug, rev = cases[index][:2]
    args = [S, slug, "--rev", rev]
    before = run(sys.executable, "-B", ROOT / "base_role_triggers.py", *args)
    after = run(sys.executable, "-B", P / "role_triggers.py", *args)
    assert (before.returncode, before.stdout) == (after.returncode, after.stdout)
logs.append("First-occurrence bytes equal base in three historical replays.")
(ROOT / "replays.log").write_text("\n".join(logs))
print("Historical replays: 8 passed; first-occurrence byte comparisons: 3 passed.", flush=True)

mutations = [
    ("AC-1-headings", "role_triggers.py", "    return failures, replacements\n",
     "    return sum(bool(VALIDATION_REPORT.match(line)) for line in lines), replacements\n",
     "test_role_triggers.py", "StepBackTest.test_two_failed_reports_count_once_each_and_passing_reports_do_not_count"),
    ("AC-2-design-count", "role_triggers.py", "    return failures, replacements\n",
     "    return failures, [date for _, date in events(lines)[1]]\n",
     "test_role_triggers.py", "StepBackTest.test_only_superseding_amendments_count_and_the_two_counts_stay_separate"),
    ("AC-3-idle-drop", "pr_watch.py", '        else:\n            out += [line for line in done.stdout.splitlines() if line.startswith("next:")]\n', "",
     "test_pr_watch.py", "TasksTests.test_second_failed_validation_is_advisory_live_and_silent_archived"),
    ("AC-4-merge-drop", "delivery_gate.py", '    else:\n        nexts.extend(line for line in said if line.startswith("next:"))\n', "",
     "test_delivery_gate.py", "OwedRoleCallTests.test_second_failure_prints_questions_before_ask_without_holding_and_with_other_problems"),
    ("AC-4-merge-hold", "delivery_gate.py", '        nexts.extend(line for line in said if line.startswith("next:"))',
     '        problems.extend(line for line in said if line.startswith("next:"))',
     "test_delivery_gate.py", "OwedRoleCallTests.test_second_failure_prints_questions_before_ask_without_holding_and_with_other_problems"),
    ("AC-5-undated-call", "role_triggers.py", "any(made >= third_date for made in dated) if third_date else calls or waivers",
     "calls or waivers", "test_role_triggers.py", "StepBackTest.test_third_replacement_dates_the_call_or_waiver_and_fourth_owes_no_second_call"),
]
mutation_log = []
for name, file, old, new, test, method in mutations:
    target = ROOT / "mutations" / name / "scripts"
    shutil.copytree(P, target, ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
    source = (target / file).read_text()
    assert source.count(old) == 1, name
    (target / file).write_text(source.replace(old, new))
    for cache in target.rglob("__pycache__"):
        shutil.rmtree(cache)
    done = run(sys.executable, "-B", target / test, method)
    assert done.returncode == 1 and "FAIL:" in done.stderr, name + done.stdout + done.stderr
    (ROOT / (name + ".log")).write_text(done.stdout + done.stderr)
    mutation_log.append(f"{name}: test rejected mutation, exit 1")
    if name == "AC-1-headings":
        slug, rev = cases[2][:2]
        replay = run(sys.executable, "-B", target / file, S, slug, "--rev", rev)
        assert "before the next step" in replay.stdout, replay.stdout
        mutation_log.append("AC-1: c03f77631 wrongly prints the reminder under the headings mutation.")
    if name == "AC-5-undated-call":
        slug, rev = cases[6][:2]
        replay = run(sys.executable, "-B", target / file, S, slug, "--rev", rev)
        assert "dispatch kc-dev-flow-2:chief-engineer" not in replay.stdout, replay.stdout
        mutation_log.append("AC-5: 7d203d562 wrongly clears chief-engineer under the undated-call mutation.")
    print(mutation_log[-1], flush=True)

mod = "kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md"
workflow = "kc-dev-flow-2/references/sd/workflow.md"
assert not run("git", "diff", "--stat", BASE, "--", workflow, mod).stdout
mutant_mod = ROOT / "mutations/AC-6-mod.md"
mutant_mod.write_text((WT / mod).read_text() + "\nUnapproved standing instruction.\n")
different = run("git", "diff", "--no-index", "--", WT / mod, mutant_mod)
assert different.returncode == 1 and "+Unapproved standing instruction." in different.stdout
mutation_log.append("AC-6: a mod-line mutation yields a nonempty diff, exit 1; candidate standing-text diff is empty against assigned base.")
adr = next((WT / "docs/adr").glob("0026-*.md"))
before_amendment = adr.read_text().rsplit("\nAmended 2026-11-02 (Captain:", 1)[0]
assert "two validation reports with a Material or Needs decision F bullet" not in before_amendment
(ROOT / "mutations/AC-7-adr-without-amendment.md").write_text(before_amendment)
mutation_log.append("AC-7: omitted-amendment copy lacks the new event ruling; manual comparison against the two ideation gate records detects it (not a machine verdict).")
(ROOT / "mutations.log").write_text("\n".join(mutation_log) + "\n")
print("Mutations: six behavioral changes rejected; standing-text difference and ADR omission exercised.", flush=True)

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

old = load(ROOT / "base_role_triggers.py", "base_role_triggers")
new = load(P / "role_triggers.py", "candidate_role_triggers")
rev = run("git", "-C", S, "rev-parse", "HEAD").stdout.strip()
paths = run("git", "-C", S, "ls-tree", "-r", "--name-only", rev).stdout.splitlines()
slugs = set()
import re
for path in paths:
    found = re.fullmatch(r"(?:_archive/)?([^/.][^/]*)(?:\.md|/index\.md)", path)
    if found and found[1] not in ("README", "_mods"):
        slugs.add(found[1])
changed = []
for slug in sorted(slugs):
    before = old.check(S, slug, rev)
    after = new.check(S, slug, rev)
    if before != after:
        failures, replacements = new.step_back_events(list(new.outside_fences(new.read_task(S, slug, rev))))
        assert max(failures, len(replacements)) >= 2, (slug, before, after)
        if before[0] != 1 and after[0] == 1:
            assert max(failures, len(replacements)) >= 3 and "dispatch kc-dev-flow-2:chief-engineer" in after[1]
        changed.append(f"{slug}: validations={failures} replacements={len(replacements)} exit={before[0]}->{after[0]}")
header = f"Corpus at {rev}: {len(slugs)} committed live/archive tasks, {len(changed)} changed outputs; every change reaches an approved threshold."
(ROOT / "corpus.log").write_text(header + "\n" + "\n".join(changed) + "\n")
print(header, flush=True)
