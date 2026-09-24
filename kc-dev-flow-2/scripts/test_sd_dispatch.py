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
                result = run([binary, "dispatch", "build", "--workflow-dir", repo,
                              "--entity-path", entity, "--stage", stage, "--host", host,
                              "--checklist-file", checklist_path, "--stamp"], repo)
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
                if stage == "ideation":
                    gate = definition.split("**Gate content:**", 1)[1]
                    assert "PRFAQ" in gate and "Mermaid" in gate and "Surfaces" in gate and "not presentable" in gate
                else:
                    assert "## Review-finding disposition" in definition

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
