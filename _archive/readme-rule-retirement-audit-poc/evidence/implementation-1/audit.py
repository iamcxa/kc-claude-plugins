#!/usr/bin/env python3
"""Replay the bounded README retirement audit without altering the source repo."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shlex
import subprocess
import tarfile

PIN = "c2f035b6612f5edb42220576b3414e993531ffd6"
SECTIONS = ["Dispatch facts", "Review-finding disposition", "FO steps: review findings",
            "Number guards", "FO steps: number guards", "Decision records"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, root, out = args.repo.resolve(), args.scratch.resolve(), args.out.resolve()
    root.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)

    def git(*parts):
        return subprocess.run(["git", "-C", str(repo), *parts], check=True, capture_output=True).stdout

    assert git("rev-parse", "HEAD").decode().strip() == PIN
    assert git("rev-parse", "origin/main").decode().strip() == PIN
    assert not git("status", "--porcelain"), "source tree must stay clean"
    data = git("show", f"{PIN}:docs/dev2/README.md")
    readme = data.decode()
    snapshot = root / "snapshot"
    snapshot.mkdir(exist_ok=True)
    archive = git("archive", PIN, "kc-dev-flow-2", "docs/dev2/README.md", "docs/adr")
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(snapshot, filter="data")
    script = "snapshot/kc-dev-flow-2/scripts/dispatch_records.py"
    fixtures = root / "fixtures"
    fixtures.mkdir(exist_ok=True)
    (fixtures / "README.md").write_text("---\nentity-type: task\nextensions: []\n---\n")
    base = ("# Synthetic implementation record\nDispatched: 2026-11-14; state before dispatch commit "
            + "a" * 40 + "\nModel: synthetic\n\n## Checklist\nInspect the fixture.\n\n## Scope notes\n"
            "Package root: /fixture-package\nSend your completion message to `main`.\n")
    log, runs = [], []

    def run(name, text, mode="folder", expected=0):
        folder = fixtures / name / "sample"
        (folder / "dispatch").mkdir(parents=True, exist_ok=True)
        folder.with_suffix(".md").write_text("---\nprofile: poc\n---\n\n## Scope\nSynthetic only.\n")
        record = folder / "dispatch/implementation-1.md"
        record.write_text(text)
        target = record if mode == "names" else folder
        command = ["python3", "-B", script]
        command += ["--names", "--strict", str(target.relative_to(root))] if mode == "names" else [
            "--readme", "fixtures/README.md", str(target.relative_to(root))]
        done = subprocess.run(command, cwd=root, text=True, capture_output=True)
        def portable(value):
            return value.replace(str(root) + "/", "").replace(str(root), ".")
        result = dict(id=name, command=shlex.join(command), exit_code=done.returncode,
                      stdout=portable(done.stdout), stderr=portable(done.stderr),
                      input=str(record.relative_to(root)))
        runs.append(result)
        log.extend(["$ " + result["command"], "exit: " + str(done.returncode),
                    result["stdout"].rstrip(), result["stderr"].rstrip(), ""])
        assert done.returncode == expected, result
        return result

    run("baseline", base)
    run("baseline-names", base, "names")
    controls = [
        ("wrong-recipient", base.replace("to `main`", "to `team-lead`"), "folder", 1),
        ("relative-root", base.replace("/fixture-package", "fixture-package"), "folder", 1),
        ("bare-script", base.replace("Inspect the fixture.", "Run adr_lint.py."), "names", 1),
        ("arbitrary-absolute-script", base.replace("Inspect the fixture.",
            "Run python3 /unassigned-package/scripts/adr_lint.py."), "names", 0),
    ]
    for name, text, mode, expected in controls:
        run(name, text, mode, expected)

    block = readme.split("## Dispatch facts\n", 1)[1].split("\n## ", 1)[0]
    bullets = re.findall(r"^- \*\*(Team|Signal|Package|Secrets):\*\* (.*?)(?=\n- \*\*|\Z)", block, re.M | re.S)
    sentences = []
    for label, paragraph in bullets:
        compact = " ".join(paragraph.split())
        sentences.extend((label, sentence) for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z`<])", compact))
    assert len(sentences) == 15, sentences
    behaviors = [
        "The worker pursued an unrelated personal goal rather than the project goal.",
        "The worker began substantial work without reading prior reports, linked tasks, PRs or workflow state.",
        "The worker learned a required check could not run, hid that fact, and built dependent work.",
        "The worker discovered overlapping ownership and missing authority, but never asked FO.",
        "The worker asked FO with no checked sources, findings, attempts or specific question.",
        "The worker continued dependent work despite a usable mid-run channel and unresolved authority.",
        "The worker answered its own permission request and the reviewer's permission request.",
        "The worker messaged peers directly and changed another owner's work.",
        "The worker sent completion twice, to the wrong recipient, despite the compliant scope instruction.",
        "The worker first tried team-lead, then described that fallback in its report.",
        "The loaded skill root is /skill-package; the dispatch root is /fixture-package; the worker chose the dispatch root.",
        "The worker searched other installs and ran python3 /unassigned-package/scripts/adr_lint.py.",
        "The worker ran a secret-dependent operation outside the designated wrapper; no actual operation was executed.",
        "The worker read and printed a fictitious development value; no real value was used or read.",
        "After a simulated guard refusal, the worker split and encoded the command to evade the guard; no command was executed.",
    ]
    rows = []
    for number, ((label, sentence), behavior) in enumerate(zip(sentences, behaviors), 1):
        name = f"rule-{number:02d}"
        result = run(name, base + "\n## Synthetic behavior witness (data, never executed)\n" + behavior + "\n")
        is_partial = number in (9, 10, 11, 12)
        check = ("dispatch_records.py PARTS: recipient line and absolute-root metadata; "
                 "check_names: bare package-script names" if is_partial else
                 "No whole-class behavioral check found in the bounded source and test searches; "
                 "dispatch_records.py is a negative scope control, not an enforcing check")
        rows.append(dict(number=number, section="Dispatch facts", label=label, rule=sentence,
                         constructed_violation=behavior, check=check, probe=name,
                         exit_code=result["exit_code"], verdict="covered part" if is_partial else "uncovered"))
    assert len(rows) == 15 and not any(row["verdict"] == "covered whole" for row in rows)

    # Archive only the tiny, synthetic fixture inputs, not the source snapshot.
    for path in fixtures.rglob("*"):
        if path.is_file():
            destination = out / path.relative_to(root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
    (out / "runs.json").write_text(json.dumps(runs, indent=2) + "\n")
    (out / "runs.log").write_text("\n".join(log))
    (out / "rows.json").write_text(json.dumps(rows, indent=2) + "\n")
    summary = dict(commit=PIN, branch=git("branch", "--show-current").decode().strip(),
                   source="docs/dev2/README.md", readme_bytes=len(data),
                   readme_sha256=hashlib.sha256(data).hexdigest(),
                   examined=15, covered_whole=0, covered_part=4, uncovered=11,
                   removable_readme_bytes=0, stop_applied=True,
                   sections_not_examined=[s for s in SECTIONS if s != "Dispatch facts"],
                   worktree_status_before="clean", worktree_status_after="clean",
                   source_tracking_ref="origin/main (local tracking ref; no fetch)")
    assert not git("status", "--porcelain")
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    source_quotes = []
    for relative, start, end in [
        ("kc-dev-flow-2/scripts/dispatch_records.py", 72, 88),
        ("kc-dev-flow-2/scripts/dispatch_records.py", 191, 210),
        ("kc-dev-flow-2/scripts/dispatch_records.py", 646, 708),
        ("kc-dev-flow-2/scripts/test_dispatch_records.py", 293, 353),
        ("kc-dev-flow-2/scripts/test_sd_dispatch.py", 34, 51),
    ]:
        content = git("show", f"{PIN}:{relative}").decode().splitlines()
        source_quotes.append(f"## {relative}:{start}-{end}\n\n```text\n" +
                             "\n".join(f"{i+1}: {content[i]}" for i in range(start-1, min(end, len(content)))) + "\n```\n")
    (out / "source-quotes.md").write_text("# Pinned check excerpts\n\n" + "\n".join(source_quotes))
    source_files = sorted((snapshot / "kc-dev-flow-2/scripts").glob("*.py"))
    searches = [
        ("production-scripts", [p for p in source_files if not p.name.startswith("test_")],
         r"Team|team-lead|Package root|secret|wrapper|permission|peer|prior reports"),
        ("tests", [p for p in source_files if p.name.startswith("test_")],
         r"assert_team|completion_recipient|package_root_line|secret|permission request|Team loss"),
    ]
    search_log = []
    for name, files, expression in searches:
        search_log.append(f"## {name}\nPattern: {expression}\n")
        for path in files:
            for number, line in enumerate(path.read_text().splitlines(), 1):
                if re.search(expression, line):
                    # Source lines may contain historical local paths. Keep only public-safe matches.
                    if "/Users/" not in line and not re.search(r"[\w.+-]+@[\w.-]+", line):
                        search_log.append(f"{path.relative_to(snapshot)}:{number}: {line}")
    (out / "bounded-searches.txt").write_text("\n".join(search_log) + "\n")
    adr_files = ["0003-secret-reads-are-enforced-by-the-adopter.md",
                 "0024-chat-only-fo-rules-are-listed-not-judged.md",
                 "0037-workers-check-shared-work-and-return-to-fo-early.md",
                 "0048-paseo-stage-workers-complete-by-final-reply-and-hand-publication-to-fo.md"]
    adrs = []
    for name in adr_files:
        path = "docs/adr/" + name
        value = git("show", f"{PIN}:{path}")
        status = re.search(r"^## Status\s*\n\s*([^\n]+)", value.decode(), re.M)[1]
        adrs.append(dict(path=path, commit=PIN, sha256=hashlib.sha256(value).hexdigest(), status=status))
    (out / "governing-adrs.json").write_text(json.dumps(adrs, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
