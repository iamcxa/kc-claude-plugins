#!/usr/bin/env python3
"""Exercise real SD dispatch transport in disposable repos; never spawn a model."""

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "references/sd/workflow.md"
STAGES = ("ideation", "implementation", "validation")
ROUND_RULE = ("A round is one verdict of an external reviewer of the delivery",
              "or labelled P1 by the reviewer, blocks in every round",
              "For an external reviewer that has no P1 label, its highest severity level counts as P1 (e.g. RoboRev)",
              "From round 3 a finding that is neither does not start a repair cycle",
              "`Follow-up:` line to that task's Scope")
WORKER_RULE = ("Before repair authorization, product bytes and the recorded candidate revision stay unchanged",
               "The four evidence fields are", "- **Needs decision:**")
SEED_STEP = "design_surfaces.py check --seed"
FO_RECORD = "\n## FO alignment\n\nSurfaces: none\nVisible change: none\n"
LANE_RULE = ("`concurrency` limits only what `status --next` proposes",
             "are dispatched at once in the entity's own worktree",
             "do not wait for another entity's worker in the same stage",
             "is dispatched only after the repair or fix has completed and committed its candidate",
             "replaces that one line with `Not applied: <environment> <sha> - <evidence>`",
             "Without that confirmation the line stays")
OLD_LANE = ("A feedback-reflow repair, the validation recheck of that repair, and an FO fix authorized under "
            "Review-finding disposition step 3 are dispatched at once in the entity's own worktree, after the "
            "existing overlap check against running worktrees; they do not wait for another entity's worker "
            "in the same stage.")
LANE_FORBIDDEN = ("the validation recheck of that repair, and an FO fix",)


def lane_gaps(text):
    flat = " ".join(text.split())
    return ([p for p in LANE_RULE if p not in flat], [p for p in LANE_FORBIDDEN if p in flat])


FIXES = {
    "goal-change": dict(
        need=("the same story ids and the same release and story `goal` text",
              "changes the goal of the release, a story or a task"),
        old=("with the release's story set unchanged since its latest `Release review:` line",),
        swaps=((r"A task whose `journey-story` is already on the map in that release passes with that one check.*?"
                r"in that task's `## FO alignment` reason\.",
                "A task whose `journey-story` is already on the map in that release, with the release's story set "
                "unchanged since its latest `Release review:` line, passes with that one check and marks nothing."),
               (r"changes the goal of the release, a story or a task", "changes its goal"))),
    "shared-environment": dict(
        need=("persistent shared non-production environment",
              "a separate hosting project such as a staging project"),
        old=("persistent shared environment (a non-production database branch)",),
        swaps=((r"persistent shared non-production environment \(a database branch, or a separate hosting project.*?"
                r"own production database\)",
                "persistent shared environment (a non-production database branch)"),)),
    "collision": dict(
        need=("the task whose migration is applied keeps it and the other, unapplied task renumbers",
              "deletes its `Migration:` line", "a shared non-production database that cannot be reset",
              "is deleted and recreated by the Captain", "the one that merges first keeps the number",
              "`Not applied: <environment> <sha> - database reset`",
              "the line stays and the migration counts as applied"),
        old=("Renumber holds for the Captain", "- **Renumber.**"),
        swaps=((r"- \*\*Collision\.\*\*.*?(?= ## Delivery authority)",
                "- **Renumber.** A candidate whose number was taken (R3, R5) renumbers and returns to implementation. "
                "When an `Applied at:` commit holds the migration, FO holds for the Captain: reset that non-production "
                "database branch, then renumber. It applies to non-production branches only; the production branch "
                "cannot be reset."),
               (r"the line stays and the migration counts as applied", "the line stays and Renumber holds for the Captain"))),
    "clear-release-fields": dict(
        need=("journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=",
              "moves that list and `journey-mapping-complete: true` to another member of the story"),
        old=(),
        swaps=((r"When signal 2 moves a task out of a release, FO clears.*?declaration matches its members\.", ""),)),
    "backlog-revise": dict(
        need=("at `backlog`, which dispatches no worker, FO revises",),
        old=(),
        swaps=((r"; and at `backlog`, which dispatches no worker.*?asks the proposal's author to\.", "."),)),
    "feedback-revise": dict(
        need=("at a stage whose gate has a `feedback-to`, the revision goes to that target and the stage's worker re-reviews it",
              "at a stage with no `feedback-to` that dispatches a worker, that stage's worker reworks it"),
        old=("at a stage that dispatches a worker, that stage's worker reworks it",),
        swaps=((r"at a stage with no `feedback-to` that dispatches a worker, that stage's worker reworks it; at a stage whose gate has a `feedback-to`.*?re-reviews it;",
                "at a stage that dispatches a worker, that stage's worker reworks it,"),)),
    "fetch-the-inspected-repo": dict(
        need=("FO runs `git -C <repo> fetch`, then", "after `git -C <repo> fetch`, on the PR head"),
        old=("FO runs `git fetch`, then", "after `git fetch`, on the PR head"),
        swaps=((r"FO runs `git -C <repo> fetch`, then", "FO runs `git fetch`, then"),
               (r"after `git -C <repo> fetch`, on the PR head", "after `git fetch`, on the PR head"))),
    "approval-accepts-stated-recommendation": dict(
        need=("plain approval accepts that recommendation only when the gate question says so",
              "FO records its handling as FO's reading, never as his ruling"),
        old=(),
        swaps=((r"A Needs decision put to the Captain at a gate carries FO's recommendation\..*?and asks him\. ", ""),)),
    "adr-not-recorded": dict(
        need=("An older record a change touches without that line takes `**Recommended:** not recorded`, never a reconstructed recommendation",),
        old=(),
        swaps=((r"An older record a change touches without that line takes `\*\*Recommended:\*\* not recorded`, never a reconstructed recommendation\. ", ""),)),
    "consent-rules": dict(
        need=("A Captain ruling is his reply to the question it settles, given after that question was put",
              "consent he gave earlier to a different question, or a choice he raised but did not make",
              "returns a choice he raised to him rather than to a worker"),
        old=(),
        swaps=((r"A Captain ruling is his reply to the question it settles.*?rather than to a worker\. ", ""),)),
    "dispatch-record": dict(
        need=("FO saves those scope notes, the checklist, the model it dispatches on and the SHA it dispatches from as `<task>/dispatch/<stage>-<cycle>.md`",
              "so the instruction a worker followed outlives the session that wrote it"),
        old=(),
        swaps=((r"FO saves those scope notes, the checklist, the model it dispatches on.*?outlives the session that wrote it\. ", ""),)),
    "resumed-dispatch": dict(
        need=("A follow-up message to a worker FO resumes is a dispatch too, and its record carries the same parts",),
        old=(),
        swaps=((r"A follow-up message to a worker FO resumes is a dispatch too, and its record carries the same parts\. ", ""),)),
    "adr-since": dict(
        need=("Validation runs `python3 <package>/scripts/adr_lint.py docs/adr --since <base>`, which requires every record the candidate added or changed",),
        old=("validation runs `python3 <package>/scripts/adr_lint.py docs/adr --require <numbers>`",),
        swaps=((r"\. Validation runs `python3 <package>/scripts/adr_lint\.py docs/adr --since <base>`.*?returns to FO\.",
                "; validation runs `python3 <package>/scripts/adr_lint.py docs/adr --require <numbers>` and returns a failure or a missing record through the existing feedback route."),)),
    "override-record": dict(
        need=("`Override: recommended <option>; Captain chose <option>; area: <area>`",
              "later workers find past rulings with `git grep 'Override:'`"),
        old=(),
        swaps=((r"When the Captain chooses differently from the recommendation, FO writes.*?in the state checkout\. ", ""),)),
    "adr-recommended": dict(
        need=("the options considered and the option recommended inside Decision",
              "`<package>/scripts/adr_lint.py --require` refuses a required record without the recommended line"),
        old=("the decider's own words and the options considered inside Decision",),
        swaps=((r"the decider's own words, the options considered and the option recommended inside Decision; `<package>/scripts/adr_lint\.py --require` refuses a required record without the recommended line\.",
                "the decider's own words and the options considered inside Decision."),)),
    "state-commits-through-sd": dict(
        need=("FO commits task state only through SD commands",
              "each with `--workflow-dir <dir>`), never by staging the state checkout with `git add -A` or `git add .`"),
        old=(),
        swaps=((r"FO commits task state only through SD commands.*?into another task's commit\. ", ""),)),
    "rework-state-commit": dict(
        need=("After it, FO runs `spacedock state commit <slug> --workflow-dir <dir>`, publishes, and reads the task back",),
        old=(),
        swaps=((r"`merge guard --rework` supersedes the approval.*?awaiting merge\. ", ""),)),
}


def fix_gaps(text):
    flat = " ".join(text.split())
    return {name: ([p for p in fix["need"] if p not in flat], [p for p in fix["old"] if p in flat])
            for name, fix in FIXES.items()}


def at_0_10_1(text, name):
    flat = " ".join(text.split())
    for pattern, old in FIXES[name]["swaps"]:
        flat, count = re.subn(pattern, lambda _: old, flat)
        assert count == 1, (name, pattern, count)
    return flat


def exercise(base, binary, sd_root):
    token = uuid.uuid4().hex[:10]
    artifacts = []
    env = {key: value for key, value in os.environ.items()
           if key not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    env["SPACEDOCK_BIN"] = binary

    def run(args, cwd=base, data=None, expected=0, child_env=None):
        call_env = env if child_env is None else child_env
        result = subprocess.run([str(arg) for arg in args], cwd=cwd, env=call_env,
                                input=data, text=True, capture_output=True, timeout=30)
        with (base / "commands.jsonl").open("a") as log:
            log.write(json.dumps({"argv": [str(arg) for arg in args], "cwd": str(cwd),
                                  "stdin": data, "exit": result.returncode,
                                  "runtime_markers": [key for key in ("CLAUDECODE", "CODEX_THREAD_ID", "PI_CODING_AGENT_DIR") if call_env.get(key)],
                                  "stdout": result.stdout, "stderr": result.stderr}) + "\n")
        if expected is not None and result.returncode != expected:
            raise AssertionError(f"{args}: exit {result.returncode}\n{result.stderr}")
        return result

    def route_definition(profile):
        definition = TEMPLATE.read_text()
        if profile == "poc":
            definition = re.sub(r"    - name: ideation\n.*?(?=    - name: implementation)", "", definition, flags=re.DOTALL)
            definition = re.sub(r"### `ideation`\n.*?(?=### `implementation`)", "", definition, flags=re.DOTALL)
        return definition

    def seed(name, stage, definition=None, profile="pilot", with_mod=True):
        repo = base / name
        repo.mkdir()
        workflow = repo / "docs" / ("dev2-poc" if profile == "poc" else "dev2")
        workflow.mkdir(parents=True)
        (workflow / "README.md").write_text(definition or route_definition(profile))
        (repo / ".gitignore").write_text(".worktrees/\n**/.spacedock-state/\n")
        if with_mod:
            (workflow / "_mods").mkdir()
            shutil.copyfile(sd_root / "mods/pr-merge.md", workflow / "_mods/pr-merge.md")
        run(["git", "init", "--initial-branch=main", repo])
        for key, value in (("user.name", "Dev Flow Fixture"), ("user.email", "fixture@example.invalid"),
                           ("commit.gpgsign", "false"), ("core.hooksPath", "/dev/null")):
            run(["git", "-C", repo, "config", key, value])
        files = [".gitignore", str((workflow / "README.md").relative_to(repo))]
        if with_mod:
            files.append(str((workflow / "_mods/pr-merge.md").relative_to(repo)))
        run(["git", "-C", repo, "add", "--", *files])
        run(["git", "-C", repo, "commit", "-m", "test: seed synthetic CLI workflow"])
        # Commission's orphan-state journey, confined to this disposable repository.
        state = workflow / ".spacedock-state"
        run(["git", "-C", repo, "worktree", "add", "--detach", state])
        run(["git", "-C", state, "checkout", "--orphan", f"spacedock-state/{workflow.name}"])
        run(["git", "-C", state, "rm", "-rf", "."])
        slug = f"df2-{token}-{name}"
        entity = state / f"{slug}.md"
        template = TEMPLATE.read_text().split("```markdown\n", 1)[1].split("```", 1)[0]
        entity.write_text(template.replace("<task-id>", slug).replace("<selected-profile>", profile)
                          .replace("<bounded outcome>", "Synthetic CLI fixture, not product acceptance")
                          .replace("status: backlog", f"status: {stage}"))
        run(["git", "-C", state, "add", "--", entity.name])
        run(["git", "-C", state, "commit", "-m", "test: seed synthetic task state"])
        return workflow, entity

    def request(repo, entity, stage, host):
        return {"schema_version": 2, "entity_path": str(entity), "workflow_dir": str(repo),
                "stage": stage, "host": host, "checklist": ["Inspect the selected stage boundary"]}

    def snapshot(repo, entity):
        return (entity.read_bytes(), run(["git", "-C", repo, "rev-parse", "HEAD"]).stdout,
                run(["git", "-C", repo, "status", "--porcelain=v1", "--untracked-files=all"]).stdout)

    try:
        version = run([binary, "--version"]).stdout.splitlines()[0]
        for stage in STAGES:
            for host in ("claude", "codex"):
                repo, entity = seed(f"{host}-{stage}", stage)
                payload = request(repo, entity, stage, host)
                payload_path = base / f"{host}-{stage}.json"
                payload_path.write_text(json.dumps(payload))
                checklist_path = base / "transport-checklist.txt"
                checklist_path.write_text("Synthetic dispatch only; no worker execution\n")
                notes_path = base / "transport-scope-notes.txt"
                package_root = ROOT
                notes_path.write_text(f"Package root: {package_root}\n"
                                      f"Run {package_root}/scripts/comment_ratio.py from the base to HEAD.\n")
                result = run([binary, "dispatch", "build", "--workflow-dir", repo,
                              "--entity-path", entity, "--stage", stage, "--host", host,
                              "--checklist-file", checklist_path, "--scope-notes-file", notes_path,
                              "--stamp"], repo)
                run([binary, "dispatch", "build", "--validate-only", payload_path], repo)
                envelope = json.loads(result.stdout)
                artifact = Path(envelope["dispatch_file_path"])
                if token not in artifact.name:
                    raise AssertionError("unexpected dispatch artifact ownership")
                artifacts.append(artifact)
                body = artifact.read_text()
                (base / f"{host}-{stage}-dispatch.md").write_text(body)
                assert str(entity) in body and f"Stage: {stage}" in body
                assert str(artifact) in envelope["prompt"]
                assert envelope["subagent_type"] == "spacedock:ensign"
                bootstrap = 'Skill(skill="spacedock:ensign")' if host == "claude" else "$spacedock:ensign"
                assert bootstrap in envelope["prompt"], envelope["prompt"]
                expected = [binary, "dispatch", "show-stage-def", "--workflow-dir", str(repo), "--stage", stage]
                fetches = [shlex.split(command) for command in envelope["fetch_commands"]]
                assert fetches == [expected], fetches
                definition = run(fetches[0], repo).stdout
                assert f"kc-dev-flow-2:{stage}" in definition
                assert "kc-dev-flow:" not in definition
                assert "## Dispatch facts" in definition, stage
                assert "## FO steps" not in definition and "## Delivery authority" not in definition, ("FO-only section reached a stage", host, stage)
                facts = definition.split("## Dispatch facts", 1)[1].split("\n## ", 1)[0]
                for label in ("Signal", "Package", "Secrets"):
                    assert f"- **{label}:**" in facts, (stage, label)
                assert "dispatch show-stage-def" in body and f"--stage {stage}" in body
                assert f"Package root: {package_root}\n" in body, (host, stage)
                assert f"{package_root}/scripts/comment_ratio.py" in body, (host, stage)
                assert body.index("Package root:") < body.index("Synthetic dispatch only"), (host, stage)
                if stage == "ideation":
                    gate = definition.split("**Gate content:**", 1)[1]
                    assert "PRFAQ" in gate and "Mermaid" in gate and "Surfaces" in gate and "not presentable" in gate
                else:
                    assert "## Review-finding disposition" in definition
                    flat = " ".join(definition.split())
                    assert [p for p in WORKER_RULE if p not in flat] == [], ("worker-visible rule missing", host, stage)
                    assert [p for p in ROUND_RULE if p in flat] == [], ("round rule reached a worker", host, stage)

        template_flat = " ".join(TEMPLATE.read_text().split())
        assert [p for p in ROUND_RULE if p not in template_flat] == [], "round rule missing from workflow.md"

        repo, entity = seed("ac-format", "ideation")
        declarations = entity.read_text() + "\n" + "\n".join(
            f"**AC-{number}**: Synthetic parser criterion {number}.\n"
            "Verified by: parser-only fixture; no live work.\n" for number in (2, 3))
        context = "\n## Stage Report: ideation\n\nSynthetic parser context only; no worker ran and no evidence is claimed.\n"
        entity.write_text(declarations + context)
        scan = [binary, "status", "--workflow-dir", repo, "--read", entity.stem, "--ac-scan", "--json"]
        parsed = json.loads(run(scan, repo).stdout)
        ids = ["AC-1", "AC-2", "AC-3"]
        assert [ac["id"] for ac in parsed["acs"]] == ids, parsed
        assert all(ac["citations"] == [] and ac["unevidenced"] == "true"
                   for ac in parsed["acs"]), parsed
        entity.write_text(re.sub(r"\*\*(AC-\d+)\*\*:", r"- \1:", declarations) + context)
        assert json.loads(run(scan, repo).stdout)["acs"] == [], "plain AC unexpectedly recognized"
        entity.write_text(declarations + context + "\n- SKIPPED: AC-1..AC-3 not verified; synthetic range only.\n")
        ranged = json.loads(run(scan, repo).stdout)["acs"]
        assert [ac["id"] for ac in ranged] == ids, ranged
        assert [bool(ac["citations"]) for ac in ranged] == [True, False, True], ranged
        assert ranged[1]["unevidenced"] == "true", ranged
        entity.write_text(declarations + context + "\n" + "\n".join(
            f"- SKIPPED: {ac} not verified; synthetic parser mapping only." for ac in ids) + "\n")
        mapped = json.loads(run(scan, repo).stdout)["acs"]
        assert [ac["id"] for ac in mapped] == ids, mapped
        for ac in mapped:
            assert len(ac["citations"]) == 1, mapped
            assert ac["citations"][0]["text"] == f"- SKIPPED: {ac['id']} not verified; synthetic parser mapping only.", ac

        repo, entity = seed("criteria-parity", "ideation")
        header = entity.read_text().split("\n## Scope", 1)[0] + FO_RECORD
        report = "\n## Stage Report: ideation\n\nSynthetic parser context only; no worker ran.\n"
        checker = ROOT / "scripts/design_surfaces.py"

        def parity(body, extra=""):
            entity.write_text(header + body + report + extra)
            scanned = run([binary, "status", "--workflow-dir", repo, "--read", entity.stem, "--ac-scan", "--json"],
                          repo, expected=None)
            ids = [ac["id"] for ac in json.loads(scanned.stdout)["acs"]] if scanned.returncode == 0 else []
            checked = run(["python3", checker, "check", entity], repo, expected=None)
            return ids, checked

        for label, body, has_criterion in (
                ("absent", "", False),
                ("level-1 heading", "\n# Acceptance criteria\n**AC-1**: x\n", False),
                ("plain list", "\n## Acceptance criteria\n- AC-1: x\n", False),
                ("empty section", "\n## Acceptance criteria\n\n## Notes\n**AC-2**: y\n", False),
                ("unclosed bold", "\n## Acceptance criteria\n**AC-1 x\n", False),
                ("lowercase heading", "\n## acceptance criteria\n**AC-1**: x\n", True),
                ("trailing space", "\n## Acceptance criteria \n**AC-1**: x\n", True),
                ("leading space", "\n ## Acceptance criteria\n**AC-1**: x\n", True),
                ("leading tab", "\n\t## Acceptance criteria\n**AC-1**: x\n", True),
                ("leading no-break space", "\n\xa0## Acceptance criteria\n**AC-1**: x\n", True),
                ("trailing no-break space", "\n## Acceptance criteria\xa0\n**AC-1**: x\n", True),
                ("uppercase heading", "\n## ACCEPTANCE CRITERIA\n**AC-1**: x\n", True),
                ("two spaces inside", "\n## Acceptance  criteria\n**AC-1**: x\n", False),
                ("labelled", "\n## Acceptance criteria\n**AC-1 (VALUE)**: x\n", True),
                ("valid", "\n## Acceptance criteria\n**AC-1**: x\nVerified by: y\n", True),
                ("fenced declaration", "\n## Acceptance criteria\n```\n**AC-1**: x\n```\n", True)):
            ids, checked = parity(body)
            assert bool(ids) == has_criterion, (label, ids)
            assert (checked.returncode == 0) == has_criterion, (label, checked.stdout)
            if not has_criterion:
                assert "cceptance criteria" in checked.stdout, (label, checked.stdout)

        criteria = "\n## Acceptance criteria\n\n**AC-1**: kept.\n{old}"
        amendment = ("\n## Captain amendments\n\n### Amendment 1 — 2026-09-30, chat\n"
                     "Captain: 「drop AC-2」 (chat)\nSupersedes: AC-2\n{moved}")
        old = "**AC-2**: replaced outcome.\nVerified by: y\n"
        ids, checked = parity(criteria.format(old="") + amendment.format(moved="Superseded text:\n" + old))
        assert ids == ["AC-1"] and checked.returncode == 0, (ids, checked.stdout)
        ids, checked = parity(criteria.format(old="**AC-2** (superseded by amendment 1): replaced outcome.\n")
                              + amendment.format(moved=""))
        assert ids == ["AC-1", "AC-2"] and checked.returncode == 1, (ids, checked.stdout)
        assert "supersedes AC-2 but it is still declared" in checked.stdout, checked.stdout
        ids, checked = parity(criteria.format(old="**AC-2** (superseded by amendment 1): replaced outcome.\n")
                              + amendment.format(moved=""), "\n- SKIPPED: AC-2 superseded by amendment 1\n")
        evidenced = json.loads(run([binary, "status", "--workflow-dir", repo, "--read", entity.stem, "--ac-scan", "--json"],
                                   repo).stdout)["acs"]
        assert ids == ["AC-1", "AC-2"] and checked.returncode == 1, (ids, checked.stdout)
        assert [bool(ac["citations"]) for ac in evidenced] == [False, True], evidenced

        backlog = run([binary, "dispatch", "show-stage-def", "--workflow-dir", repo, "--stage", "backlog"], repo).stdout
        assert SEED_STEP in backlog, "backlog stage definition lacks the seed check"
        source = TEMPLATE.read_text()
        trimmed = re.sub(r"- \*\*Seed check:\*\*.*?(?=\n### )", "", source, flags=re.DOTALL)
        assert trimmed != source
        workflow, _ = seed("no-seed-step", "backlog", trimmed)
        bare = run([binary, "dispatch", "show-stage-def", "--workflow-dir", workflow, "--stage", "backlog"], workflow).stdout
        assert "### `backlog`" in bare and SEED_STEP not in bare, "seed step still printed"

        repo, entity = seed("host-detection", "ideation")
        payload = request(repo, entity, "ideation", "claude")
        del payload["host"]
        build = [binary, "dispatch", "build", "--workflow-dir", repo]
        mixed = {**env, "CLAUDECODE": "1", "CODEX_THREAD_ID": "synthetic-foreign-host"}
        refused = run(build, repo, json.dumps(payload), expected=None, child_env=mixed)
        assert refused.returncode != 0 and not refused.stdout.strip(), refused
        assert "ambiguous runtime host sources" in refused.stderr, refused.stderr
        cleaned = {key: value for key, value in mixed.items()
                   if key not in ("CODEX_THREAD_ID", "PI_CODING_AGENT_DIR")}
        envelope = json.loads(run(build, repo, json.dumps(payload), child_env=cleaned).stdout)
        artifact = Path(envelope["dispatch_file_path"])
        assert token in artifact.name, "unexpected dispatch artifact ownership"
        artifacts.append(artifact)
        (base / "autodetected-claude-dispatch.md").write_text(artifact.read_text())
        assert 'Skill(skill="spacedock:ensign")' in envelope["prompt"], envelope["prompt"]
        assert str(entity) in artifact.read_text()

        repo, entity = seed("wrong-stage", "ideation")
        checklist = base / "stamp-checklist.txt"
        checklist.write_text("Inspect the selected stage boundary\n")
        before = snapshot(repo, entity)
        refused = run([binary, "dispatch", "build", "--workflow-dir", repo,
                       "--entity-path", entity, "--stage", "implementation",
                       "--checklist-file", checklist, "--host", "codex", "--stamp"],
                      repo, expected=None)
        assert refused.returncode != 0 and not refused.stdout.strip(), refused
        assert "entity status 'ideation' does not match --stage 'implementation'" in refused.stderr
        assert snapshot(repo, entity) == before, "wrong-stage refusal changed entity or Git state"

        definition = re.sub(r"    - name: validation\n.*?(?=    - name: done)", "",
                            TEMPLATE.read_text(), flags=re.DOTALL)
        definition = re.sub(r"### `validation`\n.*?(?=### `done`)", "", definition, flags=re.DOTALL)
        repo, entity = seed("missing-stage", "implementation", definition)
        refused = run([binary, "dispatch", "build", "--workflow-dir", repo], repo,
                      json.dumps(request(repo, entity, "validation", "codex")), expected=None)
        assert refused.returncode != 0 and not refused.stdout.strip(), refused
        assert "stage 'validation' not found" in refused.stderr
        # Exercise adopted graph order with labelled fixture decisions, not user grants.
        checklist = base / "route-checklist.txt"
        checklist.write_text("Synthetic transport check; execute no worker or delivery hook\n")

        def synthetic_report(entity, stage):
            with entity.open("a") as stream:
                stream.write(f"\n## Stage Report: {stage}\n\n"
                             "- SKIPPED: Synthetic transport check; execute no worker or delivery hook\n"
                             "  Synthetic parser input only; no product work or acceptance.\n\n"
                             "### Summary\n\nSynthetic complete-format report, not worker evidence.\n")
            run(["git", "-C", entity.parent, "add", "--", entity.name])
            run(["git", "-C", entity.parent, "commit", "-m", f"test: synthetic {stage} report input"])

        def synthetic_gate(workflow, entity, target):
            run([binary, "gate", "prepare", entity.stem, "--workflow-dir", workflow,
                 "--question", "Synthetic route test only?", "--artifact", entity,
                 "--summary", "SYNTHETIC fixture; no human acceptance or completed work."], workflow)
            run([binary, "gate", "record", entity.stem, "--workflow-dir", workflow,
                 "--decision", "approve", "--actor", "person:captain",
                 "--reason", "SYNTHETIC TEST ONLY; no real approval or delivery."], workflow)
            result = run([binary, "gate", "consume", entity.stem, "--workflow-dir", workflow], workflow)
            assert f"target-stage={target}" in result.stdout, result.stdout
            return result.stdout

        def stamped(workflow, entity, stage):
            result = run([binary, "dispatch", "build", "--workflow-dir", workflow,
                          "--entity-path", entity, "--stage", stage, "--host", "codex",
                          "--checklist-file", checklist, "--stamp"], workflow)
            envelope = json.loads(result.stdout)
            artifact = Path(envelope["dispatch_file_path"])
            assert token in artifact.name
            artifacts.append(artifact)
            (base / f"{entity.stem}-{stage}.md").write_text(artifact.read_text())
            return re.search(r"^worktree:[ \t]*(.*)$", entity.read_text(), re.MULTILINE)[1]

        for profile in ("poc", "pilot", "prod"):
            workflow, entity = seed(f"route-{profile}", "backlog", profile=profile)
            boot = run([binary, "status", "--workflow-dir", workflow, "--boot"], workflow).stdout
            assert "merge: pr-merge" in boot, boot
            assert (workflow / "_mods/pr-merge.md").read_bytes() == (sd_root / "mods/pr-merge.md").read_bytes()
            run([binary, "state", "ready", "--workflow-dir", workflow], workflow)
            run([binary, "status", "--workflow-dir", workflow, "--validate"], workflow)
            code_head = run(["git", "-C", workflow, "rev-parse", "HEAD"]).stdout
            synthetic_gate(workflow, entity, "implementation" if profile == "poc" else "ideation")
            if profile != "poc":
                stamped(workflow, entity, "ideation")
                synthetic_report(entity, "ideation")
                synthetic_gate(workflow, entity, "implementation")
            implementation_tree = stamped(workflow, entity, "implementation")
            code_root = Path(run(["git", "-C", workflow, "rev-parse", "--show-toplevel"]).stdout.strip())
            assert (code_root / implementation_tree).is_dir(), implementation_tree
            synthetic_report(entity, "implementation")
            # No model ran: this status update stands for a synthetic completion input.
            run([binary, "status", "--workflow-dir", workflow, "--set", entity.stem,
                 "status=validation", "started"], workflow)
            validation_tree = stamped(workflow, entity, "validation")
            assert validation_tree == implementation_tree, (implementation_tree, validation_tree)
            synthetic_report(entity, "validation")
            result = synthetic_gate(workflow, entity, "done")
            assert "approved-awaiting-merge" in result, result
            guarded = json.loads(run([binary, "merge", "guard", entity.stem, "--workflow-dir", workflow,
                                      "--verdict", "passed", "--json"], workflow).stdout)
            assert (guarded["signal"], guarded["action"], guarded["hook"]) == ("armed", "invoke-hook", "pr-merge"), guarded
            assert entity.exists() and "status: validation" in entity.read_text()
            assert run(["git", "-C", workflow, "rev-parse", "HEAD"]).stdout == code_head
            assert not run(["git", "-C", workflow, "status", "--porcelain"]).stdout.strip()

        workflow, entity = seed("failed-none", "implementation")
        stamped(workflow, entity, "implementation")
        report = ("\n## Stage Report: implementation\n\n"
                  "- SKIPPED: Synthetic transport check; execute no worker or delivery hook\n"
                  "  Synthetic parser input only; no product work or acceptance.\n")
        summary = "\n### Summary\n\nSynthetic complete-format report, not worker evidence.\n"
        entity.write_text(entity.read_text() + report + "- FAILED: none.\n  Nothing failed.\n" + summary)
        run(["git", "-C", entity.parent, "add", "--", entity.name])
        run(["git", "-C", entity.parent, "commit", "-m", "test: report ending FAILED none"])
        advance = [binary, "status", "--workflow-dir", workflow, "--set", entity.stem, "status=validation", "started"]
        refused = run(advance, workflow, expected=None)
        assert refused.returncode != 0 and "durable, complete" in refused.stderr + refused.stdout, refused
        named = run([binary, "status", "--workflow-dir", workflow, "--read", entity.stem,
                     "--stage", "implementation", "--checklist"], workflow).stdout
        assert "status=FAILED" in named and "text=none." in named, named
        entity.write_text(entity.read_text().replace("- FAILED: none.\n  Nothing failed.\n", ""))
        run(["git", "-C", entity.parent, "add", "--", entity.name])
        run(["git", "-C", entity.parent, "commit", "-m", "test: report without the FAILED bullet"])
        run(advance, workflow)

        source = " ".join(TEMPLATE.read_text().split())
        assert lane_gaps(source) == ([], []), lane_gaps(source)
        old_lane = re.sub(r"A feedback-reflow repair and an FO fix.*?will be delivered\.", OLD_LANE, source)
        old_lane = re.sub(r"When the push is rejected.*?the migration counts as applied\. ", "", old_lane)
        assert old_lane != source and OLD_LANE in old_lane
        missing, forbidden = lane_gaps(old_lane)
        assert len(missing) == 3 and forbidden == list(LANE_FORBIDDEN), (missing, forbidden)
        no_wait = source.replace("do not wait for another entity's worker in the same stage", "")
        assert lane_gaps(no_wait)[0] == [LANE_RULE[2]], lane_gaps(no_wait)
        assert all(gap == ([], []) for gap in fix_gaps(source).values()), fix_gaps(source)
        for name, fix in FIXES.items():
            for other, (missing, kept) in fix_gaps(at_0_10_1(source, name)).items():
                want = (list(fix["need"]), list(fix["old"])) if other == name else ([], [])
                assert (missing, kept) == want, (name, other, missing, kept)
        leaked = re.sub(r"(    - name: implementation\n.*?        - Number guards\n)", r'\1        - "FO steps: review findings"\n',
                        TEMPLATE.read_text(), count=1, flags=re.DOTALL)
        assert leaked != TEMPLATE.read_text()
        workflow, entity = seed("round-rule-leak", "implementation", leaked)
        leak = run([binary, "dispatch", "show-stage-def", "--workflow-dir", workflow, "--stage", "implementation"], workflow).stdout
        assert "## FO steps: review findings" in leak, "listed FO section not inlined"
        assert [p for p in ROUND_RULE if p not in " ".join(leak.split())] == [], "round rule not inlined when its section is listed"

        workflow, holder = seed("lane", "implementation")
        stamped(workflow, holder, "implementation")
        repair = holder.with_name(holder.name.replace("-lane.md", "-lane-repair.md"))
        repair.write_text(re.sub(r"^(worktree|started):.*\n", "", holder.read_text().replace(holder.stem, repair.stem),
                                 flags=re.MULTILINE))
        run(["git", "-C", repair.parent, "add", "--", repair.name])
        run(["git", "-C", repair.parent, "commit", "-m", "test: second entity in the same stage"])
        stamped(workflow, repair, "implementation")
        feedback = base / "lane-feedback.txt"
        feedback.write_text("Synthetic feedback: repair the named finding only.\n")
        built = run([binary, "dispatch", "build", "--workflow-dir", workflow, "--entity-path", repair,
                     "--stage", "implementation", "--checklist-file", checklist,
                     "--feedback-context-file", feedback, "--feedback-reflow", "--host", "codex"], workflow)
        envelope = json.loads(built.stdout)
        artifacts.append(Path(envelope["dispatch_file_path"]))
        assert token in artifacts[-1].name and str(repair) in artifacts[-1].read_text()
        assert "Synthetic feedback: repair the named finding only." in artifacts[-1].read_text()

        # Missing registration is not fail-closed in upstream SD: demonstrate the limit.
        workflow, entity = seed("no-hook", "validation", profile="poc", with_mod=False)
        boot = run([binary, "status", "--workflow-dir", workflow, "--boot"], workflow).stdout
        assert "merge: pr-merge" not in boot
        synthetic_gate(workflow, entity, "done")
        result = json.loads(run([binary, "merge", "guard", entity.stem, "--workflow-dir", workflow,
                                "--verdict", "passed", "--json"], workflow).stdout)
        assert result["signal"] == "finalized" and not entity.exists(), result
        print(f"PASS ({version}): 6 stage/host dispatch handoffs; wrong-stage and missing-stage refusals")
        print("PASS: bold/plain AC scan and range/individual citation controls; mixed-marker refusal and cleaned Claude autodetection")
        print("PASS: both adopted graphs / three profiles, synthetic gate successors, split-root worktree reuse, canonical merge hook arm and no-hook negative control")
        print("PASS: Dispatch facts (Signal, Package, Secrets) printed for each stage on both hosts, scope notes with the package root carried into the dispatch file; a FAILED-none report refused, named by the checklist read, accepted once the bullet is gone")
        print("PASS: the round rule is in workflow.md and in no stage definition, Delivery authority and the FO steps sections reach no stage, the worker-visible finding vocabulary stays in both worker stages, and an implementation fixture that lists the FO steps section does inline the round rule; a feedback-reflow repair is built while another entity holds the only implementation slot; the lane and Applied wording is asserted present and its 0.10.0 form is reported as gaps; the seventeen wording fixes (goal-change, shared-environment, collision, clear-release-fields, backlog-revise, feedback-revise, fetch-the-inspected-repo, approval-accepts-stated-recommendation, adr-not-recorded, consent-rules, dispatch-record, resumed-dispatch, adr-since, override-record, adr-recommended, state-commits-through-sd, rework-state-commit) are each asserted present, and each reverted alone to its previous text reports only its own gaps")
        print("PASS: criteria and amendment fixtures agree with the real --ac-scan and design_surfaces.py check; the backlog stage definition prints the seed check and a copy without it does not")
        print("Not run: skill discovery/reading, worker execution, human gates, delivery hook body or remote merge")
    finally:
        for artifact in artifacts:
            if artifact.exists() and token in artifact.name:
                artifact.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="keep successful fixture repos and raw CLI evidence")
    parser.add_argument("--sd-plugin-root", type=Path, required=True,
                        help="activated SD plugin root supplying unmodified mods/pr-merge.md")
    args = parser.parse_args()
    if not (args.sd_plugin_root / "mods/pr-merge.md").is_file():
        parser.error("--sd-plugin-root must contain the activated mods/pr-merge.md")
    binary = shutil.which(os.environ.get("SPACEDOCK_BIN") or "spacedock")
    if not binary:
        parser.error("set SPACEDOCK_BIN to the installed Spacedock executable")
    base = Path(tempfile.mkdtemp(prefix="dev-flow-2-sd-")).resolve()
    try:
        exercise(base, str(Path(binary).resolve()), args.sd_plugin_root.resolve())
    except Exception:
        print(f"FAIL: fixtures and raw CLI evidence retained at {base}")
        raise
    if args.keep:
        print(f"Evidence: {base}")
    else:
        shutil.rmtree(base)


if __name__ == "__main__":
    main()
