#!/usr/bin/env python3
"""Check what FO is about to ask the Captain to merge, and judge how often that judgment held.

Usage: delivery_gate.py check <task file> --pr <owner/repo>#<N> --text-file <file> [--head <sha>] [--workflow-dir <dir>]
       delivery_gate.py calibrate <workflow dir> [--repo <git dir>]

check. The dispatched heads are the whole `Candidate: <40-hex head>` lines above the first `## ` heading of the
highest-numbered `<task folder>/dispatch/validation-<N>.md` record; the check reads no validation verdict.
A task whose frontmatter says `profile: prod` must also pass `validation_security.py` (saved security review at the
dispatched head the PR head equals, every finding disposed); a profile that cannot be read as poc, pilot or prod holds.
The PR head is compared, as a prefix, with each line; it passes when it matches one (--head, else `gh pr view --json headRefOid`).
--text-file holds the gate question and summary: each `Second reviewer: <X> because` needs `<X> not run: <reason>`
or, in one sentence naming <X>, a `review:<id>` or `comment:<id>` token.
The PR is also read with `gh pr view` and `gh api --paginate .../pulls/<N>/files`. Exit 1 holds the ask when the head differs,
a second reviewer has no stated outcome, a prod task's security review fails, a check run on the head is not finished and
successful (an empty rollup, SKIPPED and NEUTRAL included), the PR is a draft or not mergeable, its base is not the README's
`trunk:`, or the file list is shorter than `changedFiles`. Exit 2 when the record has no Candidate line, a head, the PR or the
README cannot be read, or an input is unusable. Every problem is printed.
Exit 0 prints `point:` lines (pointers into the records and the changed paths, at most 12, each value an escaped bounded token),
one `class:` line (never, docs-only, script-with-test or other, by allowlist), the saved record `<task>/merge/ask-<N>.json`
and one last `next:` line. The README frontmatter key `merge-grants:` lists `<class>:rule:<threshold>:<method>:ADR <NNNN>`
entries (method squash, merge or rebase; the rule arm ignores the threshold). The `next:` line is the merge line
(`gh pr merge ... --match-head-commit <candidate>`) only when the class is granted and never, no point was printed, the title is
a Conventional Commit, the candidate is the PR head, a listed codex reader exits 0 on the head, a listed roborev left an
`evidence=roborev:` line in the task, and no record of the class is labelled a failure. Otherwise it is the ask line.

calibrate. Labels each `merge/ask-<N>.json` of the workflow's active and archived tasks, keeping the newest per PR and head:
failure when the PR closed unmerged, merged at another head, a revert of its merge commit (`This reverts commit <sha>`) reached the
trunk within 14 days, or its task has a later `### Amendment` date or an Override, reopen or `merge guard --rework` line naming the PR
(amendments carry a date only, so a same-day amendment is not seen); pending when open or younger than 14 days; otherwise clean. Only
records whose rule verdict was merge count. Prints per class n, clean, failures, pending and the exact one-sided 95% lower bound of
clean over n, then one `next:` line. Exit 0; 2 on a configuration error.
"""
import argparse
import datetime
import json
import math
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

CANDIDATE = re.compile(r"^Candidate:[ \t]+([0-9a-f]{40})[ \t]*$", re.M)
RECORD = re.compile(r"^validation-(\d+)\.md$")
SECOND_REVIEWER = re.compile(r"Second reviewer:\s*([\w.-]+)\s+because", re.I)
OUTCOME_TOKEN = re.compile(r"\b(?:review|comment):\d+")
PR = re.compile(r"^([\w.-]+/[\w.-]+)#(\d+)$")
CONVENTIONAL = re.compile(r"^(?:feat|fix|docs|chore|refactor|test|style|perf|ci|build|revert)(?:\([\w./-]+\))?!?: \S[\x20-\x7e]{0,99}$")
GRANT = re.compile(r"^(docs-only|script-with-test|other):rule:(0\.\d{1,4}|1(?:\.0+)?):(squash|merge|rebase):ADR (\d{4})$")
CODE = {".py", ".sh", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".go", ".rb"}
NEVER_PATH = [
    re.compile(r"^(?:\.github|\.claude)/"),
    re.compile(r"(?:^|/)(?:_mods|migrations)/"),
    re.compile(r"^docs/(?:adr|dev[^/]*)(?:/|$)"),
    re.compile(r"^(?:[^/]+/)?(?:skills|agents|extensions|references)/"),
    re.compile(r"(?:^|/)(?:CLAUDE|AGENTS)\.md$|(?:^|/)learning\.md$"),
    re.compile(r"(?:^|/)(?:release-please-config|\.release-please-manifest|plugin|marketplace)\.json$"),
    re.compile(r"(?:^|/)[^/]*(?:gate|budget)[^/]*$"),
    re.compile(r"(?:^|/)(?:test_)?(?:pr_watch|decision_ledger|lint[-_]skills)\.py$"),
]
VALIDATION_SECTION = re.compile(r"^## Stage Report: validation[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
FO_DECLINES = re.compile(r"^### FO declines[ \t]*\n(.*?)(?=^#{1,3} |\Z)", re.M | re.S)
DEFERRED = re.compile(r"\bDeferred risk\b|\bdeclined\b|round-3 backlog", re.I)
NOT_RUN = re.compile(r"\b[\w.-]+ not run:\s*\S", re.I)
AC_NOT_RUN = re.compile(r"(?:\bAC-\d+\b|\bacceptance\b).*\bnot run\b", re.I)
AMENDMENT = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2})", re.M)
MAX_POINTS = 12
WINDOW = datetime.timedelta(days=14)
ASK = "next: ask for merge with this text."
CODEX_READER = Path(__file__).resolve().parent.parent / "extensions/codex/codex_review.py"


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
    records = [(int(m.group(1)), path) for path in (task.with_suffix("") / "dispatch").glob("validation-*.md")
               if (m := RECORD.match(path.name))]
    if not records:
        return [], None
    path = max(records)[1]
    try:
        header = re.split(r"^## ", path.read_text(), maxsplit=1, flags=re.M)[0]
    except (OSError, UnicodeDecodeError):
        return [], path
    return CANDIDATE.findall(header), path


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


def pr_facts(repo, number, fields="headRefOid,isDraft,mergeable,statusCheckRollup,title,headRefName,baseRefName,changedFiles"):
    return json.loads(gh("pr", "view", number, "--repo", repo, "--json", fields))


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
    for folder in ([Path(workflow_dir)] if workflow_dir else [task.parent, task.parent.parent]):
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
        extra.append(re.compile(rf"^{re.escape(rel)}/README\.md$"))
    return [p for p in paths if any(r.search(p) for r in NEVER_PATH + extra)]


def classify(paths, never):
    if never:
        return "never"
    if paths and all(p.startswith("docs/") for p in paths):
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
    bad = []
    for item in rollup:
        if item.get("__typename") == "StatusContext":
            ok = item.get("state") == "SUCCESS"
        else:
            ok = item.get("status") == "COMPLETED" and item.get("conclusion") == "SUCCESS"
        if not ok:
            bad.append(tok(item.get("name") or item.get("context") or "?", words=3, chars=40))
    return f"{len(bad)} of {len(rollup)} checks on this head are not finished and successful: {' '.join(bad[:5])}" if bad else None


def grants_of(lists):
    return {m.group(1): m.groups() for m in map(GRANT.match, lists.get("merge-grants", [])) if m}


def merge_line(number, repo, grant, candidate, title):
    return (f"next: run gh pr merge {number} --repo {repo} --{grant[2]} --match-head-commit {candidate} "
            f"--subject {shlex.quote(title)} --body '' now; when gh pr view says MERGED, tell the Captain with the points above; otherwise ask him.")


def lower_bound(k, n, alpha=0.05):
    if k <= 0 or n <= 0:
        return 0.0
    if k == n:
        return alpha ** (1 / n)

    def tail(p):
        total = 0.0
        for i in range(k, n + 1):
            log = math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p) + (n - i) * math.log1p(-p)
            total += math.exp(log)
        return total
    low, high = 0.0, 1.0
    for _ in range(80):
        mid = (low + high) / 2
        low, high = (low, mid) if tail(mid) > alpha else (mid, high)
    return low


def state_folders(workflow_dir, scalars):
    state = Path(workflow_dir) / scalars["state"] if scalars.get("state") else Path(workflow_dir)
    return sorted(p for p in [*state.glob("*/"), *(state / "_archive").glob("*/")] if (p / "merge").is_dir())


def parse_time(value):
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def revert_time(git_dir, trunk, sha):
    ref = trunk if subprocess.run(["git", "-C", git_dir, "rev-parse", "--verify", "-q", f"origin/{trunk}"], capture_output=True).returncode else f"origin/{trunk}"
    done = subprocess.run(["git", "-C", git_dir, "log", ref, "--fixed-strings", f"--grep=This reverts commit {sha}", "--format=%cI"],
                          capture_output=True, text=True)
    stamps = [parse_time(s) for s in done.stdout.split() if s]
    return min(stamps) if stamps else None


def label(rec, folder, git_dir, trunk, now):
    ref = PR.match(str(rec.get("pr", "")))
    if not ref or not re.fullmatch(r"[0-9a-f]{40}", str(rec.get("head", ""))):
        return "failure", "unreadable record"
    try:
        info = pr_facts(*ref.groups(), fields="state,headRefOid,mergeCommit,mergedAt")
    except (RuntimeError, ValueError) as error:
        return "pending", f"cannot read the PR: {error}"
    if info.get("state") == "OPEN":
        return "pending", "open"
    if info.get("state") != "MERGED":
        return "failure", "closed without merging"
    if str(info.get("headRefOid", "")).lower() != rec["head"]:
        return "failure", "merged at another head"
    merged = parse_time(info["mergedAt"]) if info.get("mergedAt") else None
    sha = (info.get("mergeCommit") or {}).get("oid")
    if sha and merged and (found := revert_time(git_dir, trunk, sha)) and found <= merged + WINDOW:
        return "failure", "its merge commit was reverted"
    task = folder.with_suffix(".md")
    text = task.read_text(errors="replace") if task.is_file() else ""
    at = parse_time(rec["time"])
    if any(d > at.strftime("%Y-%m-%d") for _, d in AMENDMENT.findall(text)):
        return "failure", "an amendment is dated after the ask"
    named = re.compile(rf"(?:merge guard --rework|Override:|\breopen(?:ed)?\b).*(?:#{ref.group(2)}\b|pull/{ref.group(2)}\b)", re.I)
    if named.search(text):
        return "failure", "a rework, reopen or override names the PR"
    if not merged or not sha or now - max(at, merged) < WINDOW:
        return "pending", "inside the 14-day window"
    return "clean", ""


def labelled(workflow_dir, scalars, git_dir, only=None, now=None):
    now = now or utcnow()
    newest = {}
    for folder in state_folders(workflow_dir, scalars):
        for path in sorted((folder / "merge").glob("ask-*.json"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0)):
            try:
                rec = json.loads(path.read_text())
                parse_time(rec["time"])
                rec["class"], rec["verdict"], rec["pr"], rec["head"]
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                rec = dict(pr=str(path), head="", **{"class": "other"}, verdict="merge", time="1970-01-01T00:00:00Z")
            newest[(rec["pr"], rec["head"], str(folder))] = (rec, folder)
    out = []
    for rec, folder in newest.values():
        if rec["verdict"] != "merge" or (only and rec["class"] != only):
            continue
        state, reason = label(rec, folder, git_dir, scalars.get("trunk", "main"), now)
        out.append((rec["class"], state, reason, rec["pr"]))
    return out


def calibrate(args):
    folder = Path(args.workflow_dir)
    scalars, lists = readme_front(folder / "README.md")
    if "trunk" not in scalars:
        emit(f"no workflow README with a trunk: in {folder}")
        return 2
    rows = labelled(folder, scalars, args.repo)
    grants, summary, remove, propose = grants_of(lists), {}, [], []
    for cls, state, _, _ in rows:
        summary.setdefault(cls, dict(clean=0, failure=0, pending=0))[state] += 1
    for cls, c in sorted(summary.items()):
        n = c["clean"] + c["failure"]
        bound = lower_bound(c["clean"], n)
        emit(f"class {cls} arm rule: n={n} clean={c['clean']} failures={c['failure']} pending={c['pending']} lower={bound:.4f}")
        if c["failure"] and cls in grants:
            remove.append(cls)
        elif cls not in grants and cls != "never" and bound >= 0.95:
            propose.append(cls)
    if remove:
        emit(f"next: remove {', '.join(remove)} from merge-grants and tell the Captain")
    elif propose:
        emit(f"next: propose a grant for {', '.join(propose)} to the Captain, with this record.")
    else:
        emit("next: no grant to propose or remove.")
    return 0


def reviewers_clean(lists, repo, number, task_text):
    extensions = lists.get("extensions", [])
    if "codex" in extensions and subprocess.run([sys.executable, str(CODEX_READER), repo, number], capture_output=True, timeout=120).returncode:
        return False
    return "roborev" not in extensions or bool(re.search(r"evidence=roborev:\S+", task_text))


def write_record(task, rec):
    folder = task.with_suffix("") / "merge"
    folder.mkdir(parents=True, exist_ok=True)
    taken = [int(m.group(1)) for p in folder.glob("ask-*.json") if (m := re.fullmatch(r"ask-(\d+)\.json", p.name))]
    path = folder / f"ask-{max(taken, default=0) + 1}.json"
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return path


def check(args):
    task, text_file = Path(args.task), Path(args.text_file)
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
    problems, holds, nexts = [], [], []
    workflow_dir, scalars, lists = find_readme(task, args.workflow_dir)
    if not workflow_dir:
        holds.append("cannot find the workflow README with a trunk: next to the task or in --workflow-dir")

    candidates, record = dispatched_candidates(task)
    if not candidates:
        holds.append(f"no latest validation dispatch record under {task.with_suffix('')}/dispatch has a 'Candidate: <40-hex head>' line")
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

    facts = files = None
    try:
        facts, files = pr_facts(repo, number), pr_files(repo, number)
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

    emit(*problems, *holds)
    if problems:
        emit(*dict.fromkeys(nexts))
        return 1
    if holds:
        emit(*(dict.fromkeys(nexts) or ["next: hold the ask and show the Captain these lines."]))
        return 2
    emit(f"PR head {head} equals dispatched candidate {head}; no second reviewer outcome is missing")
    if security_note:
        emit(security_note)
    paths = list(dict.fromkeys(p for f in files for p in (f.get("filename"), f.get("previous_filename")) if p))
    never = never_paths(paths, workflow_dir, scalars)
    root = repo_root(workflow_dir)
    release_pr = str(facts.get("headRefName", "")).startswith("release-please--")
    profile_prod = bool(re.search(r"^profile:[ \t]*prod[ \t]*$", task_text.split("\n---\n", 1)[0], re.M))
    cls = classify(paths, never or release_pr or profile_prod or bool(re.search(r"^Surfaces:.*\bdb\b", task_text, re.M)))
    points = points_for(task_text, gate_text, record, never, facts, profile_prod, root)
    verdict = "merge" if not points and cls != "never" else "ask"
    emit(*points, f"class: {cls}")

    line, grant = ASK, grants_of(lists).get(cls)
    full = str(facts["headRefOid"]).lower()
    title = str(facts.get("title", ""))
    if (grant and verdict == "merge" and CONVENTIONAL.match(title) and full in candidates
            and reviewers_clean(lists, repo, number, task_text)
            and not any(state == "failure" for _, state, _, _ in labelled(workflow_dir, scalars, root or ".", only=cls))):
        line = merge_line(number, repo, grant, full, title)
    saved = write_record(task, {"pr": args.pr, "head": full, "class": cls, "verdict": verdict, "model": "not run",
                                "points": points, "next": line, "time": utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
    emit(f"record: {task.stem}/merge/{saved.name}", line)
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
    sub.add_argument("--workflow-dir")
    cal = commands.add_parser("calibrate")
    cal.add_argument("workflow_dir")
    cal.add_argument("--repo", default=".")
    args = parser.parse_args(argv)
    return check(args) if args.command == "check" else calibrate(args)


if __name__ == "__main__":
    sys.exit(main())
