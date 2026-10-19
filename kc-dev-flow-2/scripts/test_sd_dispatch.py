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
MODS = ROOT / "references/sd/mods"
MOD_SCRIPT = re.compile(r"<package>/scripts/([A-Za-z0-9_.-]+)")
STAGES = ("ideation", "implementation", "validation")
ROUND_RULE = ("A round is one verdict of an external reviewer of the delivery",
              "or labelled P1 by the reviewer, blocks in every round",
              "For an external reviewer that has no P1 label, its highest severity level counts as P1 (e.g. RoboRev)",
              "From round 3 a finding that is neither does not start a repair cycle",
              "files it as a new backlog task with `spacedock new`")
WORKER_RULE = ("Before repair authorization, product bytes and the recorded candidate revision stay unchanged",
               "The four evidence fields are", "- **Needs decision:**")
MAIN_LINE = "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here)."
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
        need=("the same release and story `goal` text",
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
        need=("the other, unapplied task renumbers",
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
              "`journey-mapping-complete: true` to another member of the story"),
        old=(),
        swaps=((r"When signal 2 moves a task out of a release, FO clears.*?declaration matches its members\.", ""),)),
    "backlog-revise": dict(
        need=("at `backlog`, which dispatches no worker, FO revises",),
        old=(),
        swaps=((r"; and at `backlog`, which dispatches no worker.*?asks the proposal's author to\.", "."),)),
    "feedback-revise": dict(
        need=("the stage's worker re-reviews it",
              "at a stage with no `feedback-to` that dispatches a worker"),
        old=("at a stage that dispatches a worker, that stage's worker reworks it",),
        swaps=((r"at a stage with no `feedback-to` that dispatches a worker, that stage's worker reworks it; at a stage whose gate has a `feedback-to`.*?re-reviews it;",
                "at a stage that dispatches a worker, that stage's worker reworks it,"),)),
    "fetch-the-inspected-repo": dict(
        need=("FO runs `git -C <repo> fetch`, then", "after `git -C <repo> fetch`, on the PR head"),
        old=("FO runs `git fetch`, then", "after `git fetch`, on the PR head"),
        swaps=((r"FO runs `git -C <repo> fetch`, then", "FO runs `git fetch`, then"),
               (r"after `git -C <repo> fetch`, on the PR head", "after `git fetch`, on the PR head"))),
    "approval-accepts-stated-recommendation": dict(
        need=("accepts that recommendation only when the gate question says so",
              "FO records its handling as FO's reading, never as his ruling"),
        old=(),
        swaps=((r"A Needs decision put to the Captain at a gate carries FO's recommendation\..*?and asks him\. ", ""),)),
    "adr-not-recorded": dict(
        file="skills/implementation/principles.md",
        need=("takes `**Recommended:** not recorded`, never a reconstructed recommendation",
              "a change touches without that line",),
        old=(),
        swaps=((r"An older record a change touches without that line takes `\*\*Recommended:\*\* not recorded`, never a reconstructed recommendation\. ", ""),)),
    "consent-rules": dict(
        need=("A Captain ruling is his reply to the question it settles",
              "given after that question was put",
              "consent he gave earlier to a different question",
              "a choice he raised but did not make",
              "returns a choice he raised to him"),
        old=(),
        swaps=((r"A Captain ruling is his reply to the question it settles.*?rather than to a worker\. ", ""),)),
    "dispatch-record": dict(
        need=("the SHA it dispatches from as `<task>/dispatch/<stage>-<cycle>.md`",
              "outlives the session that wrote it",
              "FO runs `python3 <package>/scripts/dispatch_records.py <task folder>` before committing and fixes each part it lists",
              "for validation a `Candidate: <full head SHA>` line per head validated"),
        old=(),
        swaps=((r"FO saves those scope notes, the checklist, the model it dispatches on.*?fixes each part it lists\. ", ""),)),
    "resumed-dispatch": dict(
        need=("A follow-up message to a worker FO resumes is a dispatch", "never a pointer to another record"),
        old=(),
        swaps=((r"A follow-up message to a worker FO resumes is a dispatch too, with the same check and a checklist of the items that message asks, never a pointer to another record\. ", ""),)),
    "adr-since": dict(
        need=("for each `ADR:` number the task's `## Number guards` reserves",
              "which requires every record the candidate added or changed",),
        old=("validation runs `python3 <package>/scripts/adr_lint.py docs/adr --require <numbers>`",),
        swaps=((r"\. Validation runs `python3 <package>/scripts/adr_lint\.py docs/adr --since <base>`.*?returns to FO\.",
                "; validation runs `python3 <package>/scripts/adr_lint.py docs/adr --require <numbers>` and returns a failure or a missing record through the existing feedback route."),)),
    "applied-none": dict(
        need=("FO records `Applied: none as of <candidate sha>`",
              "reports the missing record to FO instead of re-checking deploys",
              "a validator that finds none of `Applied at:`, `Not applied:` or `Applied: none`"),
        old=(),
        swaps=((r"When FO dispatches validation and nothing was pushed for the task.*?has a skipped record\. ", ""),
               (r" `Applied: none as of <sha>` records that nothing was pushed.*?instead of re-checking deploys\.", ""))),
    "follow-up-reason": dict(
        need=("names the backlog task that already holds it when a later round repeats it",
              "whose body carries the finding and the decline reason",
              "it never enters an open task's Scope",
              "assesses it against its stated reason and earlier rulings",
              "returns the line to FO as a Needs decision"),
        old=(),
        swaps=((r", naming the finding, and files it as a new backlog task.*?The terminal gate lists each such task\.",
                ", naming the finding and its home, and adds a `Follow-up:` line to that task's Scope, the open task whose Scope edits the finding's file, else a new backlog task from `spacedock new`. The terminal gate lists each follow-up and its home."),
               (r"A `Follow-up:` line in Scope is not accepted scope by itself.*?It records which, and why\. ", ""))),
    "decline-settled": dict(
        need=("does not report it again unless the candidate changes",
              "or new evidence would make it Material"),
        old=(),
        swaps=((r" A finding FO declined in a committed gate summary or under `### FO declines` is settled:.*?would make it Material\.", ""),)),
    "late-decline": dict(
        need=("committed with `spacedock state commit <slug> --workflow-dir <dir>`, and the terminal gate",
              "FO writes the decline under `### FO declines`",),
        old=(),
        swaps=((r"When that summary is already consumed, FO writes the decline.*?lists each entry there\. ", ""),)),
    "repair-push-grant": dict(
        need=("approval also covers later external-review rounds on the same PR",
              "a Needs decision and a scope change go to him"),
        old=(),
        swaps=((r", except as follows\. FO's delivery gate question.*?scope change go to him\.",
                ", except as follows. FO's delivery gate question says approval also covers merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it, unless he says he merges or holds, and removing its clean, pushed worktree."),)),
    "asked-line": dict(
        need=("Asked: <the question or proposal he answered",
              "`Asked:` is required when his words do not name"),
        old=(),
        swaps=((r"Asked: <the question or proposal he answered, verbatim, or the commit holding it> ", ""),
               (r"`Asked:` is required when his words do not name what they settle, such as 「同意第三點」\. ", ""))),
    "send-back": dict(
        need=("Sending an approved task back to an earlier stage",
              "`spacedock status --workflow-dir <dir> --set <slug> status=<stage>`",
              "that stage's gate is approved again before the task moves on"),
        old=(),
        swaps=((r"Sending an approved task back to an earlier stage.*?before the task moves on\. ", ""),)),
    "adr-lint-output": dict(
        need=("the `python3 <package>/scripts/adr_lint.py docs/adr --since <base>` command run with its exit code",),
        old=(),
        swaps=((r" the `python3 <package>/scripts/adr_lint\.py docs/adr --since <base>` command run with its exit code,", ""),)),
    "ideation-follow-up": dict(
        file="skills/ideation/principles.md",
        need=("as a proposal, not accepted scope",
              "otherwise return it to FO as a Needs decision"),
        old=(),
        swaps=((r"Treat each `Follow-up:` line in Scope.*?which, and why\. ", ""),)),
    "dispatch-records-check": dict(
        file="skills/validation/principles.md",
        need=("`python3 <package>/scripts/dispatch_records.py <task folder>`",),
        old=(),
        swaps=((r", and run `python3 <package>/scripts/dispatch_records\.py <task folder>`; a missing or incomplete record \(its exit 1\),", "; a missing record,"),)),
    "pr-watch": dict(
        file="references/sd/mods/kc-dev-flow-2.md",
        need=("1. Run `python3 <package>/scripts/pr_watch.py tasks <workflow dir>`.",
              "2. Do each `next:` line it prints, in order.",
              "3. After the `pr-merge` hook, do each `after pr-merge:` line it printed."),
        old=(),
        swaps=((r"1\. Run `python3 <package>/scripts/pr_watch\.py tasks <workflow dir>`\. 2\. Do each `next:` line it prints, in order\. 3\. After the `pr-merge` hook, do each `after pr-merge:` line it printed\.", ""),)),
    "readme-keeps-delivery-rules": dict(
        need=("the sentinel waits for a committed observer report",
              "that grant stands in for a presented body",
              "FO's startup and idle steps are in `_mods/kc-dev-flow-2.md`",
              "Before merging or asking, FO runs `python3 <package>/scripts/delivery_gate.py check <task> --pr <owner/repo>#<N> --text-file <question and summary>`; exit 1 or 2 holds the ask",
              "as does a head other than the latest `Candidate:`"),
        old=(),
        swaps=((r"Where `learn` is listed, the sentinel waits for a committed observer report\. ", ""),
               (r" that grant stands in for a presented body", ""),
               (r" FO's startup and idle steps are in `_mods/kc-dev-flow-2\.md`, copied from `<package>/references/sd/mods/`\.", ""),
               (r"Before merging or asking, FO runs `python3 <package>/scripts/delivery_gate\.py check.*?shows the Captain what it printed\.", "Before the merge ask, FO confirms the head."))),
    "delivery-question-carries-merge": dict(
        need=("merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it, unless he says he merges or holds",
              "removing its clean, pushed worktree."),
        old=(),
        swaps=((r", merging the full head `<package>/scripts/delivery_gate\.py check` passes, with `--match-head-commit` set to it, unless he says he merges or holds, and removing its clean, pushed worktree", ""),)),
    "worker-opens-draft-pr": dict(
        file="skills/implementation/principles.md",
        need=("Where the dispatch scope notes quote the Captain's grant to push the task branch and open a Draft PR, open that PR before the stage report and name it there",
              "otherwise report `no PR opened: no push grant`",
              "Do not invoke local fallback, push the trunk, merge, or clean up an owned worktree unless that specific action is authorized"),
        old=(),
        swaps=((r"Where the dispatch scope notes quote the Captain's grant.*?unless that specific action is authorized\.",
                "Do not invoke local fallback, push the trunk, merge, or clean up an owned worktree unless the specific action is authorized."),)),
    "one-number-per-kind": dict(
        need=("a task holds one number per kind, and a task needing a second ADR or migration returns to FO",),
        old=(),
        swaps=((r"; a task holds one number per kind, and a task needing a second ADR or migration returns to FO\.", "."),)),
    "status-executable": dict(
        need=("run `spacedock status --workflow-dir <dir>",),
        old=(),
        swaps=((r"run `spacedock status --workflow-dir <dir>", "run `status --workflow-dir <dir>"),)),
    "late-ruling-adr": dict(
        need=("including one first required by a ruling in a worker report or mid-stage feedback",),
        old=(),
        swaps=((r", or the task lands an ADR, including one first required by a ruling in a worker report or mid-stage feedback, whose number FO reserves before the next dispatch;", ", or its design lands an ADR;"),)),
    "extensions-core": dict(
        need=("This README's frontmatter `extensions:` lists the ones this repository uses",
              "an unlisted extension is not probed and adds nothing",
              "never counts as a clean result",
              "A merge ask names each listed reviewer that was not read"),
        old=(),
        swaps=((r"Extensions are optional accessories in `<package>/extensions/<name>/`.*?the Captain decides\. ", ""),)),
    "codex-round": dict(
        file="extensions/codex/EXTENSION.md",
        need=("FO reads each round with `python3 <package>/extensions/codex/codex_review.py <owner/repo> <pr>`",
              "so the round is not counted and merge is not asked for",
              "counts one round per `evidence=` id it prints",
              "it comments `@codex review` there"),
        old=(),
        swaps=((r"FO reads each round with.*?no new review by itself\. ", ""),)),
    "roborev-gate": dict(
        file="extensions/roborev/EXTENSION.md",
        need=("`python3 <package>/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`",
              "at most twice",
              "never counts as clean",
              "`roborev review --local` is not used"),
        old=(),
        swaps=((r"\*\*Instruction FO adds to the scope notes:\*\*.*?this local gate never is\.", ""),)),
    "override-record": dict(
        need=("`Override: recommended <option>; Captain chose <option>; area: <area>`",
              "later workers find past rulings with `git grep 'Override:'`"),
        old=(),
        swaps=((r"When the Captain chooses differently from the recommendation, FO writes.*?in the state checkout\. ", ""),)),
    "package-version": dict(
        need=("Before each worker dispatch FO runs `python3 <package>/scripts/package_version.py <this README>`",
              "FO holds the dispatch until the session runs the newer one"),
        old=(),
        swaps=((r" Before each worker dispatch FO runs `python3 <package>/scripts/package_version\.py <this README>`;.*?the session runs the newer one\.", ""),)),
    "second-reviewer": dict(
        need=("frontmatter `second-reviewer:` names the one that joins only when a trigger holds",
              "an untriggered second reviewer is not named as unread"),
        old=(),
        swaps=((r" Where two remote reviewers are listed, frontmatter `second-reviewer:`.*?is not named as unread\.", ""),)),
    "precedent": dict(
        need=("`Precedent: ADR <number> — 「<that ADR's Words line>」`",
              "an ADR on one of them is never a `Precedent:` line",
              "`Precedent: ADR <number> (no Words line) — 「<that sentence>」`"),
        old=(),
        swaps=((r"A decision an accepted ADR already settles is not asked again:.*?never a `Precedent:` line\. ", ""),)),
    "reviewer-record": dict(
        need=("`Reviewer: <agent> <model> <date> — <question>`; `<package>/scripts/role_triggers.py` lists calls owed.",
              "`kc-dev-flow-2:observer` run on the model and reasoning their agent files declare"),
        old=("FO never dispatches them on a cheaper model",),
        swaps=((r"`kc-dev-flow-2:chief-engineer`, `kc-dev-flow-2:engineering-reviewer` and `kc-dev-flow-2:observer` run on.*?<date> — <question>`; `<package>/scripts/role_triggers\.py` lists calls owed\.",
                "`kc-dev-flow-2:chief-engineer` and `kc-dev-flow-2:engineering-reviewer` run on the "
                "model and reasoning their agent files declare; FO never dispatches them on a "
                "cheaper model, because their value is a stronger second judgment."),)),
    "adr-recommended": dict(
        file="skills/implementation/principles.md",
        need=("the options considered and the option recommended inside Decision",
              "`<package>/scripts/adr_lint.py --require` refuses a required record without the recommended line"),
        old=("the decider's own words and the options considered inside Decision",),
        swaps=((r"the decider's own words, the options considered and the option recommended inside Decision; `<package>/scripts/adr_lint\.py --require` refuses a required record without the recommended line\.",
                "the decider's own words and the options considered inside Decision."),)),
    "state-commits-through-sd": dict(
        need=("FO commits task state only through SD commands",
              "never by staging the state checkout with `git add -A`"),
        old=(),
        swaps=((r"FO commits task state only through SD commands.*?into another task's commit\. ", ""),)),
    "rework-state-commit": dict(
        need=("publishes, and reads the task back from the state remote",),
        old=(),
        swaps=((r"`merge guard --rework` supersedes the approval.*?awaiting merge\. ", ""),)),
    "scope-notes-main-line": dict(
        need=("also carry ``Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).``",),
        old=(),
        swaps=((r" Those scope notes, and every follow-up message to a live worker, also carry .*?does not see the Signal fact\.", ""),)),
    "scope-notes-main-line-skill": dict(
        file="skills/dev/SKILL.md",
        need=("follow-up message with a line telling the worker to send its completion message to `main`",),
        old=(),
        swaps=((r" and follow-up message with a line telling the worker to send its completion message to `main`, because the completion block Spacedock appends names `team-lead`\.", "."),)),
}


def mod_scripts_missing():
    return sorted(f"{mod.name}: {name}" for mod in MODS.glob("*.md")
                  for name in MOD_SCRIPT.findall(mod.read_text()) if not (ROOT / "scripts" / name).is_file())


def pinned_texts():
    files = {fix.get("file", "references/sd/workflow.md") for fix in FIXES.values()}
    return {path: " ".join((ROOT / path).read_text().split()) for path in files}


def fix_gaps(texts):
    def text(fix):
        return texts[fix.get("file", "references/sd/workflow.md")]
    return {name: ([p for p in fix["need"] if p not in text(fix)], [p for p in fix["old"] if p in text(fix)])
            for name, fix in FIXES.items()}


def at_0_10_1(texts, name):
    path = FIXES[name].get("file", "references/sd/workflow.md")
    flat = texts[path]
    for pattern, old in FIXES[name]["swaps"]:
        flat, count = re.subn(pattern, lambda _: old, flat)
        assert count == 1, (name, pattern, count)
    return {**texts, path: flat}


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
                                      f"{MAIN_LINE}\n"
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
                assert MAIN_LINE in body and body.index(MAIN_LINE) < body.index("### Completion checklist"), (host, stage)
                if host == "claude":
                    assert 'SendMessage(to="team-lead"' in body, (host, stage)
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
                     "Captain: 「drop AC-2」 (chat)\nSupersedes: AC-2 (no replacement: dropped)\n{moved}")
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
        texts = pinned_texts()
        assert all(gap == ([], []) for gap in fix_gaps(texts).values()), fix_gaps(texts)
        for name, fix in FIXES.items():
            for other, (missing, kept) in fix_gaps(at_0_10_1(texts, name)).items():
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
        assert mod_scripts_missing() == [], mod_scripts_missing()
        mods = sorted(MODS.glob("*.md"))
        assert [mod.name for mod in mods] == ["kc-dev-flow-2.md"], mods
        workflow, entity = seed("mods", "validation", profile="poc")
        for mod in mods:
            shutil.copyfile(mod, workflow / "_mods" / mod.name)
        boot = run([binary, "status", "--workflow-dir", workflow, "--boot"], workflow).stdout
        lines = {line.split(": ", 1)[0]: line.split(": ", 1)[1] for line in boot.splitlines() if ": " in line}
        assert lines["idle"] == "kc-dev-flow-2, pr-merge", boot
        assert lines["startup"] == "kc-dev-flow-2, pr-merge", boot
        assert lines["merge"] == "pr-merge", boot
        synthetic_gate(workflow, entity, "done")
        guarded = json.loads(run([binary, "merge", "guard", entity.stem, "--workflow-dir", workflow,
                                  "--verdict", "passed", "--json"], workflow).stdout)
        assert (guarded["signal"], guarded["hook"]) == ("armed", "pr-merge"), guarded
        workflow, entity = seed("pr-recorded", "validation", profile="poc")
        run([binary, "status", "--workflow-dir", workflow, "--set", entity.stem, "pr=owner/repo#42"], workflow)
        run([binary, "state", "commit", entity.stem, "--workflow-dir", workflow], workflow)
        synthetic_gate(workflow, entity, "done")
        held = json.loads(run([binary, "merge", "guard", entity.stem, "--workflow-dir", workflow,
                               "--verdict", "passed", "--json"], workflow).stdout)
        assert (held["signal"], held["action"]) == ("blocked", "await-pr"), held
        print(f"PASS ({version}): 6 stage/host dispatch handoffs; wrong-stage and missing-stage refusals")
        print("PASS: bold/plain AC scan and range/individual citation controls; mixed-marker refusal and cleaned Claude autodetection")
        print("PASS: both adopted graphs / three profiles, synthetic gate successors, split-root worktree reuse, canonical merge hook arm and no-hook negative control")
        print("PASS: Dispatch facts (Signal, Package, Secrets) printed for each stage on both hosts, scope notes with the package root and the `main` completion line carried into the dispatch file ahead of the checklist beside the builder's `team-lead` block; a FAILED-none report refused, named by the checklist read, accepted once the bullet is gone")
        print("PASS: the round rule is in workflow.md and in no stage definition, Delivery authority and the FO steps sections reach no stage, the worker-visible finding vocabulary stays in both worker stages, and an implementation fixture that lists the FO steps section does inline the round rule; a feedback-reflow repair is built while another entity holds the only implementation slot; the lane and Applied wording is asserted present and its 0.10.0 form is reported as gaps; the " + str(len(FIXES)) + " wording fixes (" + ", ".join(FIXES) + ") are each asserted present, and each reverted alone to its previous text reports only its own gaps")
        print("PASS: criteria and amendment fixtures agree with the real --ac-scan and design_surfaces.py check; the backlog stage definition prints the seed check and a copy without it does not")
        print("PASS: the package mod sorts before pr-merge.md in the idle and startup lines and adds no merge hook, merge guard still arms pr-merge, a recorded pr arms no hook, and no mod names a package script that does not exist")
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
