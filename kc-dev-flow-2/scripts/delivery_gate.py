#!/usr/bin/env python3
"""Check what FO is about to ask the Captain to merge.

Usage: delivery_gate.py check <task file or task folder> --pr <owner/repo>#<N> --text-file <file> [--head <sha>] [--sibling-pr <owner/repo>#<N>]... [--workflow-dir <dir>]

A task is `<slug>.md` or `<slug>/index.md`; a folder argument means its `index.md`. Records are read and saved in the task's own folder `<slug>/`.

The dispatched heads are the whole `Candidate: <40-hex head>` lines above the first `## ` heading of the
highest-numbered `<task folder>/dispatch/validation-<N>.md` record; the check reads no validation verdict.
A task whose frontmatter says `profile: prod` must also pass `validation_security.py` (saved security review at
the dispatched head the PR head equals, every finding disposed); a profile that cannot be read as poc, pilot or prod holds.
The PR head is compared, as a prefix, with each line; it passes when it matches one (--head, else `gh pr view --json headRefOid`).
--text-file holds the gate question and summary: it needs a `Sufficiency: <text>` and a `Necessity: <text>` clause on one line each,
at a line start or after a sentence end (presence only; the saved record keeps each cut at 200 characters), and each `Second reviewer: <X> because` needs `<X> not run: <reason>`
or, in one sentence naming <X>, a `review:<id>` or `comment:<id>` token. Each `;`-separated item after `Declined...:` or
`FO declines...:` (up to the next sentence that opens with a label and a colon, a blank line, or a line that opens a new decline; a label
after `e.g.` or `i.e.`, or inside the item, does not start another) needs a bracket, `( )` or `[ ]`, of two or more words holding its reason; this proves a bracket exists, not that
it is a reason. When the newest `## Stage Report: validation` lists `- F<N> Deferred risk:` or `- F<N> Polish:` bullets, fewer
declined items than those bullets holds; a report with no such bullets is not joined.
The PR is also read with `gh pr view` and `gh api --paginate .../pulls/<N>/files`. Exit 1 holds the ask when the head differs,
a confirmation clause is missing, a second reviewer has no stated outcome, a declined item has no bracketed reason, an `ADR: NNNN` the task reserves under
`## Number guards` has no `<adr-path>/NNNN-*.md` in the directory at the PR head (README `adr-path:`, default `docs/adr`;
the directory is read, not the PR's file list; a `--sibling-pr` whose head is a dispatched Candidate and not closed supplies the file instead, and
is recorded as `siblings`), a prod task's security review fails, a check on the head is not finished or finished
other than SUCCESS, SKIPPED or NEUTRAL, no check on the head finished SUCCESS
(an empty rollup, or only skipped and neutral checks), a workflow run on the head is not completed and successful (a skipped run
included), the PR is a draft or not mergeable, its base is not the README's
`trunk:`, or the file list is shorter than `changedFiles`. Exit 2 when the record has no Candidate line, a head, the PR or the
README cannot be read, or an input is unusable. Every problem is printed.
A task whose committed state owes a chief-engineer or engineering-reviewer call also holds: `role_triggers.py` runs on the task folder and stem
(no --review-rounds), reading the task as committed at HEAD of its state checkout, so an edit not yet state-committed is not seen; exit 1 from it
adds one problem line and its `next:` lines, exit 2 holds with its message.
Exit 0 prints `point:` lines (pointers into the records and the changed paths, at most 12, each value an escaped bounded token),
one `class:` line (never, docs-only, script-with-test or other, by allowlist), the saved record `<task>/merge/ask-<N>.json`
and one last `next:` line, the `ASK` line: merge when the approved question named the merge, else ask. The `class:` line ends
`(verdict ask)` when the saved verdict is `ask`.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from design_surfaces import FM_PROFILE, task_folder
from number_guards import task_facts

ROLE_TRIGGERS = Path(__file__).resolve().parent / "role_triggers.py"
CANDIDATE = re.compile(r"^Candidate:[ \t]+([0-9a-f]{40})[ \t]*$", re.M)
RECORD = re.compile(r"^validation-(\d+)\.md$")
SECOND_REVIEWER = re.compile(r"Second reviewer:\s*([\w.-]+)\s+because", re.I)
OUTCOME_TOKEN = re.compile(r"\b(?:review|comment):\d+")
PR = re.compile(r"^([\w.-]+/[\w.-]+)#(\d+)$")
CONVENTIONAL = re.compile(r"^(?:feat|fix|docs|chore|refactor|test|style|perf|ci|build|revert)(?:\([\w./-]+\))?!?: \S[\x20-\x7e]{0,99}$")
CODE = {".py", ".sh", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".go", ".rb"}
NEVER_PATH = [
    re.compile(r"^(?:\.github|\.claude|\.githooks)/|^\.roborev\.toml$|^scripts/"),
    re.compile(r"(?:^|/)(?:hooks|bin)/"),
    re.compile(r"(?:^|/)(?:_mods|migrations)/"),
    re.compile(r"^docs/(?:adr|dev[^/]*)(?:/|$)"),
    re.compile(r"(?:^|/)(?:skills|agents|extensions|references)/"),
    re.compile(r"(?:^|/)(?:CLAUDE|AGENTS)\.md$|(?:^|/)learning\.md$"),
    re.compile(r"(?:^|/)(?:release-please-config|\.release-please-manifest|plugin|marketplace)\.json$"),
    re.compile(r"(?:^|/)[^/]*(?:gate|budget)[^/]*$"),
    re.compile(r"(?:^|/)kc-dev-flow-2/scripts/"),
]
VALIDATION_SECTION = re.compile(r"^## Stage Report: validation[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
FO_DECLINES = re.compile(r"^### FO declines[ \t]*\n(.*?)(?=^#{1,3} |\Z)", re.M | re.S)
DEFERRED = re.compile(r"\bDeferred risk\b|\bdeclined\b|round-3 backlog", re.I)
NOT_RUN = re.compile(r"\b[\w.-]+ not run:\s*\S", re.I)
AC_NOT_RUN = re.compile(r"(?:\bAC-\d+\b|\bacceptance\b).*\bnot run\b", re.I)
AMENDMENT = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2})", re.M)
DECLINE_START = re.compile(r"\bDeclined\b[^:\n]{0,60}:|\bFO declines\b[^:\n]{0,60}:")
DECLINE_END = re.compile(r"(?<![eE]\.[gG]\.)(?<![iI]\.[eE]\.)(?<=[.)\]])\s+(?=[A-Z][^.:\n]{0,40}:)|\n\n|\n(?=[ \t]*(?:[-*+][ \t]+)?(?:[\w.-]+[ \t]+)?(?:Declined|FO declines)\b)")
FINDING = re.compile(r"^\s*[-*]\s*\*{0,2}F\d+\*{0,2}\s*[:(]?\s*\(?\s*(?:Deferred risk|Polish)\b", re.M)
MAX_POINTS = 12
CONFIRMATIONS = {"Sufficiency": "the acceptance criteria this candidate met, from its validation report",
                 "Necessity": "who uses this change and what breaks without it"}
ASK = "next: merge this head if the approved question named the merge and he did not say he merges or holds, else ask for merge with this text. Every other PR, the Release PR included, is asked one at a time."


def clean(line):
    return "".join(ch if ch.isprintable() else ch.encode("unicode_escape").decode() for ch in line)


def emit(*lines):
    for line in lines:
        print(clean(line))


def tok(value, words=6, chars=80):
    return repr(" ".join(str(value).split()[:words])[:chars])


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def dispatched_candidates(task):
    records = [(int(m.group(1)), path) for path in (task_folder(task) / "dispatch").glob("validation-*.md")
               if (m := RECORD.match(path.name))]
    if not records:
        return [], None
    path = max(records)[1]
    try:
        header = re.split(r"^## ", path.read_text(), maxsplit=1, flags=re.M)[0]
    except (OSError, UnicodeDecodeError):
        return [], path
    return CANDIDATE.findall(header), path


def owed_role_calls(task):
    folder = task_folder(task)
    done = subprocess.run([sys.executable, str(ROLE_TRIGGERS), str(folder.parent), folder.name], capture_output=True, text=True)
    return done.returncode, [clean(line) for line in (done.stdout or done.stderr).splitlines()]


def gh(*args):
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError(f"gh not runnable: {error}") from error
    if done.returncode:
        raise RuntimeError(f"gh {args[0]} {args[1]} exited {done.returncode}: {done.stderr.strip()}")
    return done.stdout


def run_gh(repo, number):
    return json.loads(gh("pr", "view", number, "--repo", repo, "--json", "headRefOid"))["headRefOid"]


def pr_facts(repo, number):
    fields = "headRefOid,isDraft,mergeable,statusCheckRollup,title,headRefName,baseRefName,changedFiles"
    return json.loads(gh("pr", "view", number, "--repo", repo, "--json", fields))


def pr_runs(repo, head):
    page = json.loads(gh("api", f"repos/{repo}/actions/runs?head_sha={head}&per_page=100"))
    runs = page["workflow_runs"]
    if page["total_count"] != len(runs):
        raise ValueError(f"the head has {page['total_count']} workflow runs and one page lists {len(runs)}")
    return runs


def sibling_adr_names(siblings, adr_dir, candidates, problems, nexts):
    found = []
    for text in siblings:
        pr = PR.match(text)
        if not pr:
            problems.append(f"--sibling-pr must look like owner/repo#N, got {tok(text)}")
            nexts.append("next: hold the ask; write each sibling PR as owner/repo#N.")
            continue
        repo, number = pr.groups()
        info = json.loads(gh("pr", "view", number, "--repo", repo, "--json", "headRefOid,state"))
        head = str(info["headRefOid"]).lower()
        if info.get("state") == "CLOSED":
            problems.append(f"sibling {text} is closed without merging: an ADR it carries will not land")
            nexts.append("next: hold the ask; reopen the sibling PR or land the ADR file on this PR.")
        elif head not in candidates:
            problems.append(f"sibling {text} head {head[:12]} is not a dispatched candidate ({' '.join(candidates) or 'none'})")
            nexts.append("next: hold the ask; revalidate the sibling head with a Candidate line, or tell the Captain.")
        else:
            found.append((f"{text} head {head[:12]}", adr_names(repo, head, adr_dir)))
    return found


def pr_files(repo, number):
    text, files, decoder, at = gh("api", "--paginate", f"repos/{repo}/pulls/{number}/files"), [], json.JSONDecoder(), 0
    while at < len(text):
        if text[at].isspace():
            at += 1
            continue
        page, at = decoder.raw_decode(text, at)
        files += [f for part in page for f in (part if isinstance(part, list) else [part])]
    return files


def unstated_second_reviewers(text):
    missing = []
    for reviewer in dict.fromkeys(m.lower() for m in SECOND_REVIEWER.findall(text)):
        rest = SECOND_REVIEWER.sub("", text)
        named = re.compile(rf"(?<![\w-]){re.escape(reviewer)}(?![\w-])", re.I)
        not_run = re.search(rf"(?<![\w-]){re.escape(reviewer)}\s+not run:\s*\S", rest, re.I)
        sentences = re.split(r"(?<=[.!?])\s+|\n", rest)
        cited = any(named.search(s) and OUTCOME_TOKEN.search(s) for s in sentences)
        if not (not_run or cited):
            missing.append(reviewer)
    return missing


def declined_items(text):
    items, stop = [], 0
    for start in DECLINE_START.finditer(text):
        if start.start() < stop:
            continue
        rest = text[start.end():]
        end = DECLINE_END.search(rest)
        stop = start.end() + (end.start() if end else len(rest))
        depth, item = 0, ""
        for ch in (rest[:end.start()] if end else rest).strip().rstrip("."):
            depth = max(depth + (ch in "([") - (ch in ")]"), 0)
            if ch == ";" and depth == 0:
                items.append(item.strip())
                item = ""
            else:
                item += ch
        items.append(item.strip())
    return [item for item in items if item and item.lower() not in ("none", "nothing", "n/a")]


def brackets(item):
    found, expect, start = [], [], 0
    for i, ch in enumerate(item):
        if ch in "([":
            start = i + 1 if not expect else start
            expect.append(")" if ch == "(" else "]")
        elif expect and ch == expect[-1]:
            expect.pop()
            if not expect:
                found.append(item[start:i])
    return found


def clause(text, label):
    found = re.search(rf"(?:^[ \t]*|[.!?][ \t]+){label}:[ \t]*(\S[^\n]*)", text, re.M)
    return found.group(1) if found else None


def unstated_confirmations(text):
    return [label for label in CONFIRMATIONS if clause(text, label) is None]


def unreasoned_items(text):
    return [item for item in declined_items(text) if not any(len(b.split()) >= 2 for b in brackets(item))]


def findings_join(task_text, gate_text):
    report = (VALIDATION_SECTION.findall(task_text) or [""])[-1]
    owed, got = len(FINDING.findall(report)), len(declined_items(gate_text))
    if owed and got < owed:
        return (f"declined items ({got}) are fewer than the validation report's Deferred risk and Polish findings ({owed}): "
                "add a declined item for each, naming the fix as its reason when FO fixed it.")
    return None


def adr_names(repo, head, adr_dir):
    try:
        return gh("api", f"repos/{repo}/contents/{adr_dir}?ref={head}", "--jq", ".[].name").split()
    except RuntimeError as error:
        if "HTTP 404" in str(error):
            return []
        raise


def readme_front(path):
    scalars, lists, key = {}, {}, None
    lines = path.read_text(errors="replace").split("\n") if path.is_file() else []
    for line in lines[1:] if lines and lines[0] == "---" else []:
        if line == "---":
            break
        if m := re.match(r"^([\w-]+):[ \t]*(.*?)[ \t]*$", line):
            key, value = m.groups()
            scalars[key] = value.strip("'\"")
            if value.startswith("["):
                lists[key] = [v.strip().strip("'\"") for v in value.strip("[]").split(",") if v.strip()]
        elif key and (m := re.match(r"^[ \t]+-[ \t]+(.*?)[ \t]*$", line)):
            lists.setdefault(key, []).append(m.group(1).strip("'\""))
    return scalars, lists


def find_readme(task, workflow_dir):
    entries = task_folder(task).parent
    for folder in ([Path(workflow_dir)] if workflow_dir else [entries, entries.parent]):
        scalars, lists = readme_front(folder / "README.md")
        if "trunk" in scalars:
            return folder, scalars, lists
    return None, {}, {}


def repo_root(folder):
    return next((p for p in [folder.resolve(), *folder.resolve().parents] if (p / ".git").exists()), None)


def never_paths(paths, workflow_dir, scalars):
    extra = [re.compile(rf"^{re.escape(scalars[k].strip('/'))}(?:/|$)") for k in ("migrations-path", "adr-path") if scalars.get(k)]
    root = repo_root(workflow_dir) if workflow_dir else None
    if root:
        rel = workflow_dir.resolve().relative_to(root).as_posix()
        extra.append(re.compile(r"^README\.md$" if rel == "." else rf"^{re.escape(rel)}/README\.md$"))
    return [p for p in paths if any(r.search(p) for r in NEVER_PATH + extra)]


def classify(paths, never):
    if never:
        return "never"
    if paths and all(p.startswith("docs/") and p.endswith(".md") for p in paths):
        return "docs-only"
    names = {Path(p).name for p in paths}
    is_test = lambda p: Path(p).name.startswith("test_") or re.search(r"(?:\.test|\.spec|_test)\.\w+$", p)
    own_tests = lambda p: {f"test_{Path(p).name}", *(f"{Path(p).stem}{mid}{Path(p).suffix}" for mid in (".test", "_test", ".spec"))}
    code = [p for p in paths if Path(p).suffix in CODE and not is_test(p)]
    if code and all(Path(p).suffix in CODE for p in paths) and all(names & own_tests(p) for p in code):
        return "script-with-test"
    return "other"


def commit_date(path):
    done = subprocess.run(["git", "-C", str(path.parent), "log", "-1", "--format=%cs", "--", path.name], capture_output=True, text=True)
    if not done.returncode and done.stdout.strip():
        return done.stdout.strip()
    return datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).strftime("%Y-%m-%d")


def points_for(task_text, gate_text, record, paths_never, facts, profile_prod, root):
    found = []
    reports = "\n".join(VALIDATION_SECTION.findall(task_text))
    prose = reports + "\n" + gate_text
    found += [("deferred", l) for l in prose.split("\n") if DEFERRED.search(l)]
    for block in FO_DECLINES.findall(task_text) + FO_DECLINES.findall(gate_text):
        found += [("fo-decline", l.strip()) for l in block.split("\n") if re.match(r"^\s*[-*] \S", l)]
    found += [("not-run", l) for l in prose.split("\n") if NOT_RUN.search(l)]
    found += [("acceptance-not-run", l) for l in reports.split("\n") if AC_NOT_RUN.search(l)]
    if record:
        since = commit_date(record)
        found += [("amendment", f"Amendment {n} dated {d}") for n, d in AMENDMENT.findall(task_text) if d >= since]
    found += [("path", p) for p in paths_never]
    if profile_prod:
        found.append(("profile", "prod"))
    surfaces = re.search(r"^Surfaces:(.*)$", task_text, re.M)
    found += [("surface", s) for s in (re.findall(r"[\w-]+", surfaces.group(1)) if surfaces else []) if s in ("db", "ui")]
    if root and (root / "release-please-config.json").exists() and not CONVENTIONAL.match(facts["title"]):
        found.append(("title", facts["title"]))
    found += [("second-reviewer", r) for r in dict.fromkeys(m.lower() for m in SECOND_REVIEWER.findall(gate_text))]
    lines = [f"point: {kind}: {tok(value)}" for kind, value in found]
    return lines[:MAX_POINTS] + ([f"point: more: {len(lines) - MAX_POINTS} not shown"] if len(lines) > MAX_POINTS else [])


def ci_problem(rollup):
    if not rollup:
        return "the check rollup is empty: no check has run on this head"
    bad, succeeded = [], 0
    for item in rollup:
        if item.get("__typename") == "StatusContext":
            result = item.get("state")
            ok = result == "SUCCESS"
        else:
            result = item.get("conclusion") if item.get("status") == "COMPLETED" else None
            ok = result in ("SUCCESS", "SKIPPED", "NEUTRAL")
        succeeded += result == "SUCCESS"
        if not ok:
            bad.append(tok(item.get("name") or item.get("context") or "?", words=3, chars=40))
    if bad:
        return f"{len(bad)} of {len(rollup)} checks on this head are not finished and successful: {' '.join(bad[:5])}"
    return None if succeeded else "no check on this head finished successfully: only skipped or neutral"


def runs_problem(runs):
    newest = {}
    for run in runs:
        key = run.get("workflow_id")
        newest[key] = max(newest.get(key, 0), run.get("run_number", 0))
    bad = []
    for run in runs:
        superseded = run.get("run_number", 0) < newest[run.get("workflow_id")] and run.get("conclusion") in ("cancelled", "skipped")
        if not superseded and not (run.get("status") == "completed" and run.get("conclusion") == "success"):
            bad.append(tok(run.get("name") or "?", words=4, chars=40))
    return f"{len(bad)} of {len(runs)} workflow runs on this head are not finished and successful: {' '.join(bad[:5])}" if bad else None


def write_record(task, rec):
    folder = task_folder(task) / "merge"
    folder.mkdir(parents=True, exist_ok=True)
    taken = [int(m.group(1)) for p in folder.glob("ask-*.json") if (m := re.fullmatch(r"ask-(\d+)\.json", p.name))]
    path = folder / f"ask-{max(taken, default=0) + 1}.json"
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return path


def check(args):
    task, text_file = Path(args.task), Path(args.text_file)
    if task.is_dir():
        task = task / "index.md"
    pr = PR.match(args.pr)
    try:
        task_text, gate_text = task.read_text(), text_file.read_text()
    except OSError as error:
        emit(f"cannot read input: {error}")
        return 2
    if not pr:
        emit(f"--pr must look like owner/repo#N, got {tok(args.pr)}")
        return 2
    repo, number = pr.groups()
    problems, holds, nexts, sibling_notes = [], [], [], []
    workflow_dir, scalars, lists = find_readme(task, args.workflow_dir)
    if not workflow_dir:
        holds.append("cannot find the workflow README with a trunk: next to the task or in --workflow-dir")

    candidates, record = dispatched_candidates(task)
    if not candidates:
        holds.append(f"no latest validation dispatch record under {task_folder(task)}/dispatch has a 'Candidate: <40-hex head>' line")
        nexts.append("next: hold the ask; dispatch validation of this head with a Candidate line, or tell the Captain.")
    if args.head:
        head = args.head.lower()
        if not re.fullmatch(r"[0-9a-f]{7,40}", head):
            holds.append(f"--head must be 7-40 hexadecimal characters, got {tok(args.head)}")
            head = None
    else:
        try:
            head = run_gh(repo, number).lower()
        except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as error:
            holds.append(f"cannot read the head of {args.pr}: {error}")
            head = None
    if candidates and head:
        if not any(c.startswith(head) for c in candidates):
            problems.append(f"PR head {head} differs from dispatched candidate {' '.join(candidates)} (latest validation record {record.name})")
            nexts.append("next: hold the ask; revalidate this head or tell the Captain the difference.")

    facts = files = runs = None
    try:
        facts, files = pr_facts(repo, number), pr_files(repo, number)
        runs = pr_runs(repo, str(facts["headRefOid"]).lower())
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as error:
        holds.append(f"cannot read the pull request {args.pr}: {error}")
    if facts is not None:
        full = str(facts.get("headRefOid", "")).lower()
        if head and not full.startswith(head):
            problems.append(f"PR head is now {full}, not {head}: the checks below belong to another commit")
            nexts.append("next: hold the ask; read the PR head again and revalidate it, or tell the Captain.")
        if (why := ci_problem(facts.get("statusCheckRollup"))):
            problems.append(why)
            nexts.append("next: hold the ask until the required CI has finished green on this head.")
        if runs is not None and (why := runs_problem(runs)):
            problems.append(why)
            nexts.append("next: hold the ask until every workflow run on this head has finished green.")
        if facts.get("isDraft"):
            problems.append("the PR is a draft")
            nexts.append("next: hold the ask; mark the PR ready under the Captain's authority and let its CI finish.")
        if facts.get("mergeable") != "MERGEABLE":
            problems.append(f"the PR is not mergeable: {tok(facts.get('mergeable'), words=1, chars=20)}")
            nexts.append("next: hold the ask until the PR merges cleanly into the trunk.")
        if scalars.get("trunk") and facts.get("baseRefName") != scalars["trunk"]:
            problems.append(f"the PR base {tok(facts.get('baseRefName'), words=1, chars=60)} is not the trunk {tok(scalars['trunk'], words=1, chars=60)}")
            nexts.append("next: hold the ask; the PR does not target the trunk, tell the Captain.")
        if len(files) != facts.get("changedFiles"):
            problems.append(f"the changed-file list has {len(files)} files but the PR reports {tok(facts.get('changedFiles'), words=1, chars=12)}")
            nexts.append("next: hold the ask; the changed-file list is incomplete, tell the Captain.")

    reserved = sorted(task_facts(task)["adr"])
    if facts is not None and reserved:
        adr_dir = (scalars.get("adr-path") or "docs/adr").strip("/")
        try:
            names = adr_names(repo, str(facts["headRefOid"]).lower(), adr_dir)
            others = sibling_adr_names(args.sibling_pr, adr_dir, candidates, problems, nexts)
        except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as error:
            holds.append(f"cannot read {adr_dir} at the head of {args.pr} or a sibling PR: {error}")
        else:
            for number in reserved:
                has = lambda listed: any(re.fullmatch(rf"{number:04d}-.+\.md", name) for name in listed)
                if has(names):
                    continue
                where = [label for label, listed in others if has(listed)]
                if where:
                    sibling_notes.append(f"sibling: reserved ADR {number:04d} is at {where[0]}, a dispatched candidate of this task")
                    continue
                problems.append(f"reserved ADR {number:04d} has no {adr_dir}/{number:04d}-*.md at PR head {str(facts['headRefOid'])[:12]}")
                nexts.append(f"next: hold the ask; land the ADR file on this PR or delete the 'ADR: {number:04d}' line from the task, then run this check again.")
                nexts.append("next: when this task delivers the ADR on another PR, run this check again with --sibling-pr <owner/repo>#<N>.")

    security_errors, security_note = [], None
    at_head = [c for c in candidates if head and c.startswith(head)]
    if at_head:
        try:
            from validation_security import check_task as security_check
            security_errors, security_note = security_check(task, at_head)
        except (OSError, UnicodeDecodeError) as error:
            security_errors = [f"cannot read the validation security review: {error}"]
    for error in security_errors:
        problems.append(error)
        nexts.append("next: hold the ask; run the validation security review at this head, or tell the Captain.")

    for reviewer in unstated_second_reviewers(gate_text):
        nexts.append("next: hold the ask until each second reviewer has an outcome.")
        problems.append(f"second reviewer {reviewer} has no stated outcome: "
                        f"add '{reviewer} not run: <reason>' or a review:<id> or comment:<id> in a sentence naming {reviewer}")

    for item in unreasoned_items(gate_text):
        problems.append(f"declined item has no reason: {tok(item)}")
        nexts.append("next: hold the ask; write each declined item as '<class>, <finding> (<reason, two or more words>)', then run this check again.")

    if (why := findings_join(task_text, gate_text)):
        problems.append(why)
        nexts.append("next: hold the ask; write one declined item for each finding, then run this check again.")

    for label in unstated_confirmations(gate_text):
        problems.append(f"the gate text has no '{label}:' clause: add '{label}: <{CONFIRMATIONS[label]}>'")
        nexts.append("next: hold the ask; add the missing clause to the question or summary.")

    try:
        code, said = owed_role_calls(task)
    except OSError as error:
        code, said = 2, [f"cannot run role_triggers.py: {clean(str(error))}"]
    if code == 1:
        problems.append(f"{task_folder(task).name} owes a special-role call (role_triggers.py reads the task as committed)")
        nexts.extend(said)
    elif code:
        holds.extend(said or [f"role_triggers.py exited {code} with no message"])

    emit(*problems, *holds)
    if problems:
        emit(*dict.fromkeys(nexts))
        return 1
    if holds:
        emit(*(dict.fromkeys(nexts) or ["next: hold the ask and show the Captain these lines."]))
        return 2
    emit(f"PR head {head} equals dispatched candidate {head}; no second reviewer outcome is missing", *sibling_notes)
    if security_note:
        emit(security_note)
    paths = list(dict.fromkeys(p for f in files for p in (f.get("filename"), f.get("previous_filename")) if p))
    never = never_paths(paths, workflow_dir, scalars)
    root = repo_root(workflow_dir)
    release_pr = str(facts.get("headRefName", "")).startswith("release-please--")
    front = re.match(r"---\n(.*?)\n---", task_text, re.S)
    profile_prod = bool(front and (m := FM_PROFILE.search(front.group(1))) and m.group(1) == "prod")
    cls = classify(paths, never or release_pr or profile_prod or bool(re.search(r"^Surfaces:.*\bdb\b", task_text, re.M)))
    points = points_for(task_text, gate_text, record, never, facts, profile_prod, root)
    verdict = "merge" if not points and cls != "never" else "ask"
    emit(*points, f"class: {cls}" + (" (verdict ask)" if verdict == "ask" else ""))

    saved = write_record(task, {"pr": args.pr, "head": full, "class": cls, "verdict": verdict, "model": "not run",
                                "points": points, "next": ASK, **({"siblings": sibling_notes} if sibling_notes else {}),
                                "sufficiency": clean(clause(gate_text, "Sufficiency"))[:200],
                                "necessity": clean(clause(gate_text, "Necessity"))[:200], "time": utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
    emit(f"record: {task_folder(task).name}/merge/{saved.name}", ASK)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="delivery_gate.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("check")
    sub.add_argument("task")
    sub.add_argument("--pr", required=True)
    sub.add_argument("--text-file", required=True)
    sub.add_argument("--head")
    sub.add_argument("--sibling-pr", action="append", default=[])
    sub.add_argument("--workflow-dir")
    args = parser.parse_args(argv)
    return check(args)


if __name__ == "__main__":
    sys.exit(main())
