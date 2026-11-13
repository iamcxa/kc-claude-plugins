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
or, in one sentence naming <X>, a `review:<id>` or `comment:<id>` token; `answer=review:<id>` is no review.
The gate text also needs one top-level `External rounds: N` line outside fences, using the summary count form below.
Both commands require exactly one configured second-reviewer declaration, including `not triggered` when applicable.
Prod/db cannot claim `not triggered`. Listed Copilot refusals must copy the quote/id from
`<task>/review/copilot-not-run.txt` and offer `Copilot retry: available when the Captain confirms quota is back.`
Missing/unreadable source is exit 2, malformed/different content exit 1; configuration errors need a reason only.
Unsupported Copilot PR types may be skipped; `check` compares that type to the PR title.
Each `;`-separated item after `Declined...:` or
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
(an empty rollup, or only skipped and neutral checks), a workflow run on the head is not completed and successful
(a completed skipped run settles when the required-check list is non-empty), a required check name has no pass entry,
the PR is a draft or not mergeable, its base is not the README's
`trunk:`, or the file list is shorter than `changedFiles`. Exit 2 when the record has no Candidate line, a head, the PR or the
README cannot be read, or an input is unusable. Every problem is printed.
When trunk is not an ancestor of the head, check requires a passing merge-result run matching README `merge-test:`, or a `Merge result: not run: <reason>` line.
A task whose committed state owes a chief-engineer or engineering-reviewer call also holds: `role_triggers.py` runs on the task folder and stem
(no --review-rounds), reading the task as committed at HEAD of its state checkout, so an edit not yet state-committed is not seen; exit 1 from it
adds one problem line and its `next:` lines, exit 2 holds with its message.
Exit 0 from it forwards advisory `next:` lines before the record and ASK, without holding the ask.
Exit 0 prints `point:` lines (pointers into the records and the changed paths, at most 12, each value an escaped bounded token),
one `class:` line (never, docs-only, script-with-test or other, by allowlist), the saved record `<task>/merge/ask-<N>.json`
and one last `next:` line: `ASK_UNQUOTED` when a non-pending validation attempt has no effective Captain approval
quoting its bound question as `answering 「…」` (whitespace ignored), else `ASK`. Withdrawn attempts supply neither
an approval nor a resolution; an unanswered, non-withdrawn attempt keeps the pre-ask line. The `class:` line ends
`(verdict ask)` when the saved verdict is `ask`.

Usage: delivery_gate.py question <task file or task folder> --text-file <file> [--summary-file <file>] [--workflow-dir <dir>]
Runs the text checks of `check` on the validation gate question before `gate prepare`, and also refuses text that names the merge with
`--match-head-commit` and has no sentence of the form "unless he says he merges or holds" (`unless` or `if`, then `he`, `you`, `the Captain` or `Captain`, then `say`, then `merge` or `hold`). Exit 0
prints `gate text complete` then `ASK_FORM`; exit 1 prints each problem; exit 2 when an input cannot be read. `check` does not judge either clause.
Merge-naming text also needs the question file to name removing its clean, pushed worktree, in one sentence.
It requires the newest delivery check record to match the dispatched head, named merge head and clauses, and prints its --reference path.
With --summary-file, ordinary text checks use question plus summary; reviewer checks use only
the summary outside fences. It requires one top-level External rounds: N (nonnegative integer),
optionally followed by a full stop or a semicolon/full stop and detail. Without it, legacy checks apply.
The summary (combined text for legacy calls) needs Captain steps: <task folder>/captain-steps/<N>.md (positive N), passing steps
against the gate text and latest validation report, at a latest dispatched Candidate.
Both `question` and `check` print a claim-source reminder on entry, without adding a hold.
They list count sentences without a task-folder file holding their numbers, then write
Unchecked counts: N into the summary (legacy question: question file; check: ask text).
Check scans the PR body too. The disclosure is automatic and never holds a count;
an unreadable or unwritable input still exits 2.
Both commands mark uncited existing-item effect claims with （未對過紀錄） in
the submitted files; uncited PR-body sentences are copied into the ask with the
mark. Citations must resolve to existing task-folder files. This adds no hold.

Usage: delivery_gate.py steps <record> --text-file <message>
Reads Captain step observations without executing commands. Missing observations, unmatched steps,
unrecorded fenced commands or links (named Markdown files contribute shell or untagged fences;
a URI right after `{` is not a link, nor is a line that is only the Claude Code attribution), missing absolute paths whose top-level directory exists,
and Captain-only steps without a reason hold the ask (exit 1). Unreadable input is exit 2.
Candidate may be none outside a validation gate. The check trusts recorded observations.
Relative Markdown names resolve from the task folder, including names prefixed by its slug.
Report-only Markdown files contribute fenced commands; missing-path checks cover FO's text and Asked lines.
Prose asks, inline code, fences inside a > quote, fences starting on a list-marker line,
and 4-space indented code blocks stay undetected. An unclosed fence in a named Markdown
file becomes one large required step, through the end of the file.

Usage: delivery_gate.py merge-run <task> --pr owner/repo#N [--workflow-dir <dir>] -- <command>
Runs the README `merge-test:` command on an archived merge tree and saves result-N.json and its log beside the task. Missing commit objects are fetched; conflicts exit 2. The temporary tree is removed after the run.
"""
import argparse
import datetime
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from design_surfaces import FM_PROFILE, task_folder
from number_guards import task_facts
from role_triggers import outside_fences
from count_tokens import count_sentences, numbers, prose_lines, sentences
import decision_ledger

ROLE_TRIGGERS = Path(__file__).resolve().parent / "role_triggers.py"
CANDIDATE = re.compile(r"^Candidate:[ \t]+([0-9a-f]{40})[ \t]*$", re.M)
RECORD = re.compile(r"^validation-(\d+)\.md$")
SECOND_REVIEWER = re.compile(r"Second reviewer:\s*([\w.-]+)\s+because", re.I)
OUTCOME_TOKEN = re.compile(r"(?<!(?i:answer=))\b(?:review|comment):\d+")
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
# see docs/adr/0062-a-gate-approval-grants-what-its-quoted-bound-question-says.md
ASK_UNQUOTED = "next: ask for merge with this text: there is no effective Captain validation approval quoting its bound question as `answering 「…」`, so no merge grant applies. Every other PR, the Release PR included, is asked one at a time."
ASK_FORM = "next: before gate prepare, write the question the Captain answers: one decision; its first sentence says what he decides and what you recommend; plain words before ids and paths, and any term he has not seen expanded in eight words or fewer; one sentence saying what approving accepts. Show him this bound question verbatim and record his answer as `answering 「<that question>」`."
MERGE_NOT_RUN = re.compile(r"^Merge result:[ \t]+not run:[ \t]*\S.*$", re.M)
CLAIM_SOURCE = "next: each number or factual claim in this text and the PR body names the command and date that produced it, or says `<whose> report, not run`."


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
    fields = "headRefOid,isDraft,mergeable,statusCheckRollup,title,headRefName,baseRefName,changedFiles,body"
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
        skipped = reviewer == "copilot" and re.search(r"\bcopilot skipped: [\w-]+ PR\b", rest, re.I)
        sentences = re.split(r"(?<=[.!?])\s+|\n", rest)
        cited = any(named.search(s) and OUTCOME_TOKEN.search(s) for s in sentences)
        if not (not_run or cited or skipped):
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


GRANT = re.compile(r"--match-head-commit")
HOLD_OUT = re.compile(r"\b(?:unless|if)\b\s+(?:he|you|the\s+captain|captain)\s+says?\b[^.;\n]{0,30}\b(?:merges?|holds?)\b", re.I)
WORKTREE_REMOVAL = re.compile(r"\bremov(?:e|es|ing)\b[^.;\n]{0,20}\bclean\b[^.;\n]{0,10}\bpushed\b[^.;\n]{0,10}\bworktrees?\b", re.I)


def grant_without_hold_out(text):
    return bool(GRANT.search(text)) and not HOLD_OUT.search(text)


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
    lines = path.read_text().split("\n") if path.is_file() else []
    for line in lines[1:] if lines and lines[0] == "---" else []:
        if line == "---":
            break
        if m := re.match(r"^([\w-]+):[ \t]*(.*?)[ \t]*$", line):
            key, value = m.groups()
            scalars[key] = value[1:-1] if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"" else value
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


def reviewer_config(scalars, lists):
    extensions = set(lists.get("extensions", []))
    second = scalars.get("second-reviewer", "")
    if second and (second not in {"codex", "copilot"} or not {"codex", "copilot"} <= extensions):
        raise ValueError("second-reviewer must name a listed remote reviewer with another remote reviewer listed")
    return second, extensions


def reviewer_problems(task, task_text, text, second, extensions, title=None, head=None):
    problems = []
    if second:
        rows = re.findall(r"(?i)\bsecond reviewer:[ \t]*([^\n]*)", text)
        if len(rows) != 1:
            problems.append("second reviewer declaration missing or duplicated: require exactly one configured reviewer or not triggered")
        elif re.match(r"not triggered(?:[.;(\s]|$)", rows[0], re.I):
            front = re.match(r"---\n(.*?)\n---", task_text, re.S)
            prod = bool(front and (m := FM_PROFILE.search(front[1])) and m[1] == "prod")
            if prod or re.search(r"^Surfaces:.*\bdb\b", task_text, re.M):
                problems.append("second reviewer not triggered contradicts the structured prod/db trigger")
        elif not re.match(re.escape(second) + r"[ \t]+because[ \t]+\S", rows[0], re.I):
            problems.append(f"second reviewer declaration must name {second} because <nonempty trigger>, or not triggered")
    if "copilot" in extensions:
        for skipped in re.finditer(r"(?i)\bcopilot skipped:[ \t]*([^\n]*)", text):
            kind = re.fullmatch(r"([a-z]+) PR[.]?[ \t]*", skipped[1], re.I)
            pr_type = re.match(r"([a-z]+)(?:\([^\n)]*\))?!?: ", title or "")
            if (not kind or kind[1].lower() in {"feat", "fix", "refactor", "perf"}
                    or (title is not None and (not pr_type or kind[1].lower() != pr_type[1]))):
                problems.append("copilot skipped type must be unsupported and match the PR title at check")
        for refusal in re.finditer(r"(?im)(?<![\w-])copilot not run:[ \t]*([^\n]*)", text):
            value = refusal[1].rstrip()
            if value.lower().startswith("configuration error:"):
                if not value[len("configuration error:"):].strip():
                    problems.append("copilot configuration error needs a nonempty reason")
                continue
            saved = task_folder(task) / "review/copilot-not-run.txt"
            try:
                printed = saved.read_text()
            except (OSError, UnicodeDecodeError) as error:
                raise OSError(f"cannot read saved Copilot output {saved}: {error}; save the reader's exit-5 stdout there") from error
            source = re.fullmatch(r'not a review of (?P<head>[0-9a-f]{9}): "(?P<quote>.*)"; answer=review:(?P<id>\d+) at \S+\n?', printed)
            own_line = not text[text.rfind("\n", 0, refusal.start()) + 1:refusal.start()].strip()
            if not source:
                problems.append("saved Copilot output is not a readable exit-5 result")
            elif not own_line or value != f'"{source["quote"]}"; answer=review:{source["id"]}':
                problems.append("copilot not run must copy the saved printed quote and answer id")
            if source and head and not head.lower().startswith(source["head"]):
                disclosure = f'Copilot not read: {head.lower()}; last refusal: {source["head"]}'
                if not re.search(rf"(?im)^{re.escape(disclosure)}[.]?[ \t]*$", text):
                    problems.append(f"Copilot refusal is for {source['head']}, not PR head {head.lower()}; add a separate '{disclosure}' line")
            if not re.search(r"(?im)^Copilot retry: available when the Captain confirms quota is back\.[ \t]*$", text):
                problems.append("copilot not run needs the conditional retry offer")
    return problems, (["next: hold the ask; repair the reviewer declaration, saved quote/id or conditional retry offer."] if problems else [])


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


def points_for(task_text, gate_text, record, paths_never, facts, profile_prod, root, merge_result=None):
    found = [("merge-result", merge_result[1])] if merge_result else []
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
    lines = [f"point: {kind}: {clean(value)}" if kind == "merge-result" else f"point: {kind}: {tok(value)}" for kind, value in found]
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


def runs_problem(runs, settle_skipped=False):
    newest = {}
    for run in runs:
        key = run.get("workflow_id")
        newest[key] = max(newest.get(key, 0), run.get("run_number", 0))
    bad = []
    for run in runs:
        superseded = run.get("run_number", 0) < newest[run.get("workflow_id")] and run.get("conclusion") in ("cancelled", "skipped")
        if not superseded and not (run.get("status") == "completed" and run.get("conclusion") in (("success", "skipped") if settle_skipped else ("success",))):
            bad.append(tok(run.get("name") or "?", words=4, chars=40))
    return f"{len(bad)} of {len(runs)} workflow runs on this head are not finished and successful: {' '.join(bad[:5])}" if bad else None


def required_checks(repo, number):
    done = subprocess.run(["gh", "pr", "checks", number, "--repo", repo, "--required", "--json", "name,bucket"], capture_output=True, text=True, timeout=60)
    if done.stdout.strip():
        checks = json.loads(done.stdout)
        if not isinstance(checks, list) or any(not isinstance(c, dict) or not isinstance(c.get("name"), str) or not c["name"] or not isinstance(c.get("bucket"), str) for c in checks):
            raise ValueError("gh pr checks returned an invalid required-check list")
        return checks
    if "no required checks reported" in done.stderr:
        return []
    raise RuntimeError(f"gh pr checks exited {done.returncode}: {done.stderr.strip()}")


def required_problem(checks):
    passed = {c["name"] for c in checks if c.get("bucket") == "pass"}
    bad = sorted({c["name"] for c in checks} - passed)
    return f"required check without a pass on this head: {' '.join(tok(n, words=3, chars=40) for n in bad[:5])}" if bad else None


def write_record(task, rec):
    folder = task_folder(task) / "merge"
    folder.mkdir(parents=True, exist_ok=True)
    taken = [int(m.group(1)) for p in folder.glob("ask-*.json") if (m := re.fullmatch(r"ask-(\d+)\.json", p.name))]
    path = folder / f"ask-{max(taken, default=0) + 1}.json"
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return path


def text_problems(task_text, gate_text, at_gate=False, reviewer_text=None):
    problems, nexts = [], []
    for reviewer in unstated_second_reviewers(gate_text if reviewer_text is None else reviewer_text):
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
    if at_gate and grant_without_hold_out(gate_text):
        problems.append("the gate text names the merge with --match-head-commit but not 'unless he says he merges or holds'")
        nexts.append("next: hold the gate; add the clause that lets him keep the merge, then run this check again.")
    return problems, nexts


def trunk_position(repo, trunk, head):
    data = json.loads(gh("api", f"repos/{repo}/compare/{trunk}...{head}"))
    if data["status"] not in ("ahead", "identical", "diverged", "behind") or not re.fullmatch(r"[0-9a-f]{40}", str(data["base_commit"]["sha"])):
        raise ValueError("unusable trunk comparison")
    return data["status"], str(data["base_commit"]["sha"]).lower()


def merge_results(task):
    found = []
    for path in (task_folder(task) / "merge").glob("result-*.json"):
        if (m := re.fullmatch(r"result-(\d+)\.json", path.name)):
            found.append((int(m.group(1)), path))
    return [(path, json.loads(path.read_text())) for _, path in sorted(found)]


def merge_result_problem(task, gate_text, head, status, trunk_sha, command):
    if status in ("ahead", "identical"):
        return None, None
    # see docs/adr/0078-a-merge-ask-on-a-moved-trunk-carries-a-test-run-on-the-merge-result.md
    matching = [(p, r) for p, r in merge_results(task) if r.get("head") == head and r.get("trunk") == trunk_sha
                and command and r.get("command") == command]
    if matching:
        path, rec = matching[-1]
        if rec.get("exit") == 0:
            return None, (path.name, f"{tok(command, words=12, chars=120)} exit 0 on {tok(rec.get('tree', '')[:12], words=1, chars=14)} ({path.name})")
        return (f"the merge-result run {path.name} on trunk {trunk_sha[:12]} exited {tok(rec.get('exit'), words=1, chars=12)}",
                None)
    if MERGE_NOT_RUN.search("\n".join(outside_fences(gate_text))):
        return None, ("not run", "not run (the ask says so)")
    return (f"the trunk moved since this head ({status}, trunk {trunk_sha[:12]}) and no merge-result run is recorded at this head and trunk",
            None)


def merge_run(args):
    task = Path(args.task)
    if task.is_dir():
        task = task / "index.md"
    pr = PR.match(args.pr)
    if not pr or not args.run:
        emit("merge-run needs --pr owner/repo#N and a command after --")
        return 2
    repo, number = pr.groups()
    try:
        workflow_dir, scalars, _ = find_readme(task, args.workflow_dir)
        command = scalars.get("merge-test", "")
        if not command or shlex.split(command) != args.run:
            raise ValueError("command must match workflow README merge-test:")
        trunk = scalars.get("trunk") or "main"
        head = (args.head or run_gh(repo, number)).lower()
        trunk_sha = (args.trunk or trunk_position(repo, trunk, head)[1]).lower()
        if not all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in (head, trunk_sha)):
            raise ValueError("head and trunk must be full commit ids")
        git_dir = args.repo_dir or str(repo_root(workflow_dir))
        if any(subprocess.run(["git", "-C", git_dir, "cat-file", "-e", ref + "^{commit}"], capture_output=True).returncode
               for ref in (trunk_sha, head)):
            subprocess.run(["git", "-C", git_dir, "fetch", "-q", "origin", trunk, f"refs/pull/{number}/head"],
                           capture_output=True, check=True, timeout=300)
        merged = subprocess.run(["git", "-C", git_dir, "merge-tree", "--write-tree", trunk_sha, head], capture_output=True, text=True, timeout=300)
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as error:
        emit(f"cannot prepare the merge result: {error}")
        return 2
    if merged.returncode:
        emit(f"cannot prepare the merge result: merge-tree exited {merged.returncode}", merged.stdout, merged.stderr)
        return 2
    tree = merged.stdout.split()[0] if merged.stdout.split() else ""
    folder = task_folder(task) / "merge"
    folder.mkdir(parents=True, exist_ok=True)
    taken = [int(m.group(1)) for p in folder.glob("result-*.json") if (m := re.fullmatch(r"result-(\d+)\.json", p.name))]
    n = max(taken, default=0) + 1
    log = folder / f"result-{n}.log"
    rec = {"pr": args.pr, "head": head, "trunk": trunk_sha, "tree": tree, "command": command}
    start = utcnow()
    scratch = Path(tempfile.mkdtemp(prefix="merge-result-"))
    try:
        archive = subprocess.run(["git", "-C", git_dir, "archive", tree], capture_output=True, check=True, timeout=300)
        subprocess.run(["tar", "-x", "-C", str(scratch)], input=archive.stdout, check=True, capture_output=True)
        with log.open("w") as out:
            done = subprocess.run(args.run, cwd=scratch, stdout=out, stderr=subprocess.STDOUT)
        rec.update(exit=done.returncode)
    except (OSError, subprocess.SubprocessError) as error:
        emit(f"cannot run the merge-result command: {error}")
        return 2
    finally:
        shutil.rmtree(scratch)
    rec.update(seconds=round((utcnow() - start).total_seconds(), 1), time=utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), log=log.name)
    path = folder / f"result-{n}.json"
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    emit(f"merge result {tree[:12]} of {head[:12]} onto trunk {trunk_sha[:12]}: {rec['command']} exit {rec['exit']} in {rec['seconds']}s",
         f"record: {task_folder(task).name}/merge/{path.name}")
    return 0 if rec["exit"] == 0 else 1


def check(args):
    emit(CLAIM_SOURCE)
    task, text_file = Path(args.task), Path(args.text_file)
    if task.is_dir():
        task = task / "index.md"
    pr = PR.match(args.pr)
    try:
        task_text, gate_text = task.read_text(), text_file.read_text()
    except (OSError, UnicodeDecodeError) as error:
        emit(f"cannot read input: {error}")
        return 2
    if not pr:
        emit(f"--pr must look like owner/repo#N, got {tok(args.pr)}")
        return 2
    repo, number = pr.groups()
    problems, holds, nexts, sibling_notes = [], [], [], []
    try:
        workflow_dir, scalars, lists = find_readme(task, args.workflow_dir)
        if not workflow_dir:
            raise ValueError("cannot find the workflow README with a trunk: next to the task or in --workflow-dir")
        second, extensions = reviewer_config(scalars, lists)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        emit(f"cannot read reviewer configuration: {error}")
        return 2

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

    facts = files = runs = required = None
    merge_result = None
    try:
        facts, files = pr_facts(repo, number), pr_files(repo, number)
        runs = pr_runs(repo, str(facts["headRefOid"]).lower())
        required = required_checks(repo, number)
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as error:
        holds.append(f"cannot read the pull request {args.pr}: {error}")
    try:
        body = (facts or {}).get("body") or ""
        copies = scope_pr_copies(task_folder(task), body)
        count_text = "\n".join(line for line in gate_text.splitlines() if line not in copies)
        gate_text = count_disclosure(task_folder(task), count_text + "\n" + body, text_file, gate_text)
        gate_text, = scope_disclosure(task_folder(task), [(text_file, gate_text)], body)
    except (OSError, UnicodeDecodeError) as error:
        emit(f"cannot write count disclosure: {error}")
        return 2
    if facts is not None:
        full = str(facts.get("headRefOid", "")).lower()
        if head and not full.startswith(head):
            problems.append(f"PR head is now {full}, not {head}: the checks below belong to another commit")
            nexts.append("next: hold the ask; read the PR head again and revalidate it, or tell the Captain.")
        if (why := ci_problem(facts.get("statusCheckRollup"))):
            problems.append(why)
            nexts.append("next: hold the ask until the required CI has finished green on this head.")
        if runs is not None and (why := runs_problem(runs, settle_skipped=bool(required))):
            problems.append(why)
            nexts.append("next: hold the ask until every workflow run on this head has finished green.")
        if required is not None and (why := required_problem(required)):
            problems.append(why)
            nexts.append("next: hold the ask until each required check has passed on this head.")
        if facts.get("isDraft"):
            problems.append("the PR is a draft")
            nexts.append("next: hold the ask; mark the PR ready under the Captain's authority and let its CI finish.")
        if facts.get("mergeable") != "MERGEABLE":
            problems.append(f"the PR is not mergeable: {tok(facts.get('mergeable'), words=1, chars=20)}")
            nexts.append("next: hold the ask until the PR merges cleanly into the trunk.")
        if scalars.get("trunk") and facts.get("baseRefName") != scalars["trunk"]:
            problems.append(f"the PR base {tok(facts.get('baseRefName'), words=1, chars=60)} is not the trunk {tok(scalars['trunk'], words=1, chars=60)}")
            nexts.append("next: hold the ask; the PR does not target the trunk, tell the Captain.")
        if scalars.get("trunk") and head and full.startswith(head):
            try:
                status, trunk_sha = trunk_position(repo, scalars["trunk"], full)
                why, merge_result = merge_result_problem(task, gate_text, full, status, trunk_sha, scalars.get("merge-test"))
            except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as error:
                holds.append(f"cannot compare the trunk with {full[:12]}: {error}")
            else:
                if why:
                    problems.append(why)
                    nexts.append(f"next: hold the ask; run `delivery_gate.py merge-run <task> --pr {args.pr} -- <test command>` on the merge result, "
                                 "using the workflow README `merge-test:` command, or write `Merge result: not run: <reason>` in the question the Captain reads.")
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

    found, wanted = text_problems(task_text, gate_text)
    for value in re.findall(r"^Captain steps:[ \t]*(.*)$", "\n".join(outside_fences(gate_text)), re.M):
        found += captain_steps_path_problems(named_file(task_folder(task), value.strip().strip("`\"")), task_folder(task))
    problems += found
    nexts += wanted
    try:
        found, wanted = reviewer_problems(task, task_text, gate_text, second, extensions,
                                         (facts or {}).get("title"), (facts or {}).get("headRefOid"))
    except OSError as error:
        emit(*problems, str(error))
        return 2
    problems += found
    nexts += wanted

    try:
        code, said = owed_role_calls(task)
    except OSError as error:
        code, said = 2, [f"cannot run role_triggers.py: {clean(str(error))}"]
    if code == 1:
        problems.append(f"{task_folder(task).name} owes a special-role call (role_triggers.py reads the task as committed)")
        nexts.extend(said)
    elif code:
        holds.extend(said or [f"role_triggers.py exited {code} with no message"])
    else:
        nexts.extend(line for line in said if line.startswith("next:"))

    # see docs/adr/0051-the-merge-ask-check-requires-the-round-count.md
    missing = summary_round_problems("\n".join(outside_fences(gate_text)))
    problems += missing
    if missing:
        nexts.append("next: hold the ask; record the external round count in the summary.")

    emit(*problems, *holds)
    if problems:
        emit(*dict.fromkeys(nexts))
        return 1
    if holds:
        emit(*(dict.fromkeys(nexts) or ["next: hold the ask and show the Captain these lines."]))
        return 2
    emit(*dict.fromkeys(nexts))
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
    points = points_for(task_text, gate_text, record, never, facts, profile_prod, root, merge_result)
    verdict = "merge" if not points and cls != "never" else "ask"
    emit(*points, f"class: {cls}" + (" (verdict ask)" if verdict == "ask" else ""))

    # see docs/adr/0062-a-gate-approval-grants-what-its-quoted-bound-question-says.md
    front, _ = decision_ledger.split_task(task_text)
    stage = latest_attempt = None
    for line in front or []:
        match = decision_ledger.KEY.match(line)
        if match:
            key, value = match.group("key"), match.group("value") or ""
            if key == "stage":
                stage = value
            elif stage == "validation" and key == "id" and value.startswith("gate-attempt:"):
                latest_attempt = value
    rows = [r for r in decision_ledger.task_rows(task.parent, task) if r["stage"] == "validation"]
    withdrawn = {r["attempt"] for r in rows if r["kind"] == "withdrawal"}
    rows = [r for r in rows if r["attempt"] not in withdrawn]
    captain = [r for r in rows if r["kind"] == "resolution" and r["by"] == "person:captain" and r["decision"] == "approve"]
    answered = any(r["attempt"] == latest_attempt and r["kind"] == "resolution" for r in rows)
    pending = not answered and latest_attempt not in withdrawn
    ask = ASK if pending or captain and decision_ledger.quotes_bound_question(
        max(captain, key=lambda r: r["at"] or "")) else ASK_UNQUOTED
    saved = write_record(task, {"pr": args.pr, "head": full, "class": cls, "verdict": verdict, "model": "not run",
                                "points": points, "next": ask, "merge_result": merge_result[0] if merge_result else None,
                                **({"siblings": sibling_notes} if sibling_notes else {}),
                                "sufficiency": clean(clause(gate_text, "Sufficiency"))[:200],
                                "necessity": clean(clause(gate_text, "Necessity"))[:200], "time": utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
    emit(f"record: {task_folder(task).name}/merge/{saved.name}", ask)
    return 0


def summary_round_problems(text):
    rows = re.findall(r"^External rounds:[ \t]*(.*)$", text, re.M)
    if len(rows) != 1 or not re.fullmatch(r"[0-9]+(?:[.;][ \t]+\S.*|[.]?)?[ \t]*", rows[0]):
        return ["summary needs one top-level External rounds: N line (nonnegative integer)"]
    return []


STEP_FORM = """Candidate: <40-hex head, or none>

### Step 1
Asked: <the step exactly as the message states it>
Ran: <what FO ran, where (fresh shell, real browser), UTC time>
Observed: <the output, or a path in the task folder holding it>
Only he can: <what is left> — <why: his credential, account, device or judgment>"""
STEP_FIELD = re.compile(r"^(Asked|Ran|Observed|Only he can):[ \t]*(.*?)(?=^(?:Asked|Ran|Observed|Only he can):|\Z)", re.M | re.S)
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})([^\n]*)\n(.*?)(?:^[ \t]*\1[`~]*[ \t]*$|\Z)", re.M | re.S)
URL = re.compile(r"https?://[^\s<>`\"')\]]+")
ABS_PATH = re.compile(r'''(?<![\w:/>])(?:"(?:~/|/)[^"\n]+"|'(?:~/|/)[^'\n]+'|(?:~/|/)[^\s`"'()\[\]{}]+)''')
SHELL = {"", "sh", "bash", "zsh", "shell", "console"}
ATTRIBUTION = {"🤖 Generated with [Claude Code](https://claude.com/claude-code)"}


def normalized(text):
    return " ".join(text.split())


def absolute_paths(text):
    paths = []
    for value in ABS_PATH.findall(URL.sub(" ", text)):
        value = re.sub(r":\d+(?::\d+)?$", "", value.strip("\"'").rstrip(".,;:"))
        path = Path(value).expanduser()
        if "<" not in value and ">" not in value and len(path.parts) > 1 and Path(*path.parts[:2]).exists():
            paths.append(path)
    return list(dict.fromkeys(paths))


def fenced_steps(text, shell_only=False):
    return [body.strip() for _, info, body in FENCE.findall(text)
            if body.strip() and (not shell_only or (info.split() or [""])[0] in SHELL)]


def links(text):
    text = "\n".join("" if normalized(line) in ATTRIBUTION else line for line in text.splitlines())
    return [m[0].rstrip(".,;") for m in URL.finditer(text) if text[m.start() - 1:m.start()] != "{"]


def execution_recorded(ran):
    if not re.search(r"\b(?:fresh\s+shell|real\s+browser)\b", ran, re.I):
        return False
    stamp = re.search(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|\+00:00|[ \t]+UTC)(?![\w:+-])", ran)
    if not stamp:
        return False
    try:
        value = re.sub(r"[ \t]+UTC$", "+00:00", stamp[0]).replace("Z", "+00:00")
        return datetime.datetime.fromisoformat(value).utcoffset() == datetime.timedelta(0)
    except ValueError:
        return False


def named_file(folder, value):
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (folder.parent if path.parts[:1] == (folder.name,) else folder) / path


def count_problems(folder, text):
    checked, unchecked = 0, []
    for sentence, values in count_sentences(text):
        contents = []
        for value in re.findall(r"(?<![\w/.-])((?:/?[\w.-]+/)*[\w.-]+\.(?:json|log|md|txt|jsonl|csv|out))\b", sentence):
            path = named_file(folder, value).resolve()
            if not path.is_relative_to(folder.resolve()):
                continue
            try:
                contents.append(path.read_text())
            except (OSError, UnicodeDecodeError):
                continue
        if contents and values <= numbers("\n".join(contents)):
            checked += 1
        else:
            unchecked.append(sentence)
    return checked, unchecked


EXISTING = re.compile(r"舊任務|舊設計|舊的|已經開好|已開好|已開的|既有|已經過了|過了設計關卡|已核准的|進行中的|"
                      r"\balready[- ]filed\b|\bexisting\b|\bfiled before\b|\bpast (?:ideation|the gate)\b", re.I)
EFFECT = re.compile(r"不會|不再|只有|只會|只在|擋|要求|補寫|補標|不受|影響|\brefus|\bblock|\bnot\b|\bonly\b", re.I)
SCOPE_MARK = "（未對過紀錄）"
MARKED = re.compile(r"未驗證|未對過紀錄|\bunverified\b", re.I)
SAVED_FILE = re.compile(r"(?<![\w/.-])((?:/?[\w.-]+/)*[\w.-]+\.(?:json|log|md|txt|jsonl|csv|out))\b")


def scope_claims(folder, text):
    rows = []
    for index, line in prose_lines(text):
        for sentence in sentences(line):
            if not (EXISTING.search(sentence) and EFFECT.search(sentence)):
                continue
            cited = False
            for value in SAVED_FILE.findall(sentence):
                path = named_file(folder, value).resolve()
                if path.is_relative_to(folder.resolve()) and path.is_file():
                    cited = True
                    break
            rows.append((index, sentence, cited, bool(MARKED.search(sentence))))
    return rows


def mark_scope(sentence):
    end = re.search(r"[。；;？?.]+$", sentence)
    point = end.start() if end else len(sentence)
    return sentence[:point] + SCOPE_MARK + sentence[point:]


def scope_pr_copies(folder, text):
    return {"PR body: " + (sentence if marked else mark_scope(sentence))
            for _, sentence, cited, marked in scope_claims(folder, text) if not cited}


def scope_disclosure(folder, sources, extra=""):
    # see docs/adr/0082-existing-item-effect-claims-cite-output-or-carry-a-tool-mark.md
    results, claims = [], []
    copies = scope_pr_copies(folder, extra)
    for destination, text in sources:
        rows = scope_claims(folder, text)
        lines = text.splitlines(keepends=True)
        claims.extend(row for row in rows if lines[row[0]].rstrip("\r\n") not in copies)
        for index, sentence, cited, marked in rows:
            if not cited and not marked:
                lines[index] = lines[index].replace(sentence, mark_scope(sentence), 1)
        results.append("".join(lines))
    external = scope_claims(folder, extra)
    claims.extend(external)
    for _, sentence, cited, marked in external:
        if not cited:
            disclosed = sentence if marked else mark_scope(sentence)
            if disclosed not in results[0]:
                results[0] = results[0].rstrip("\n") + "\nPR body: " + disclosed + "\n"
    if claims:
        emit(f"scope claims: {sum(row[2] for row in claims)} cited, {sum(not row[2] for row in claims)} marked",
             *("marked scope: " + " ".join(sentence.split()[:12]) for _, sentence, cited, _ in claims if not cited))
    for (destination, text), result in zip(sources, results):
        if result != text:
            destination.write_text(result)
    return results


def count_disclosure(folder, text, destination, declared):
    # see docs/adr/0072-counts-cite-saved-output-and-learn-checks-referenced-evidence.md
    checked, unchecked = count_problems(folder, text)
    line = f"Unchecked counts: {len(unchecked)}"
    emit(f"counts: {checked} checked, {len(unchecked)} unchecked",
         *("unchecked count: " + " ".join(sentence.split()[:12]) for sentence in unchecked[:8]))
    declarations = {index for index, row in prose_lines(declared) if row.startswith("Unchecked counts:")}
    updated = [row for index, row in enumerate(declared.splitlines()) if index not in declarations]
    result = line + "\n" + "\n".join(updated).rstrip("\n") + "\n"
    if result != declared:
        destination.write_text(result)
    return result


def inspect_steps(record_path, message, folder, evidence=""):
    text = record_path.read_text()
    header = re.split(r"^### Step \d+[ \t]*$", text, maxsplit=1, flags=re.M)[0]
    candidates = re.findall(r"^Candidate:[ \t]*([^\n]*)$", header, re.M)
    problems = []
    candidate = candidates[0].strip() if len(candidates) == 1 else ""
    if not re.fullmatch(r"[0-9a-f]{40}|none", candidate):
        problems.append("record needs one Candidate: <40-hex head, or none> line")
    chunks = re.split(r"^### Step (\d+)[ \t]*$", text, flags=re.M)
    steps = [(number, dict(STEP_FIELD.findall(body))) for number, body in zip(chunks[1::2], chunks[2::2])]
    if not steps:
        problems.append("record has no Step 1")
    observed = {normalized(fields["Observed"]) for _, fields in steps if fields.get("Observed", "").strip()}
    asked_paths = FENCE.sub(lambda match: "" if normalized(match[3]) in observed else match[0], message)
    texts = [message + "\n" + evidence]
    path_text = FENCE.sub(lambda match: "" if normalized(match[3]) in observed else match[0], texts[0])
    commands = fenced_steps(texts[0])
    named = lambda source: absolute_paths(source) + [named_file(folder, re.sub(r":\d+(?::\d+)?$", "", value)) for value in
                re.findall(r"(?<![\w:/])(?:[~./\w-]+/)?[\w.-]+\.md(?::\d+(?::\d+)?)?", URL.sub(" ", source))]
    own = {path.resolve() for path in named(asked_paths)}
    link_texts = texts.copy()
    for path in dict.fromkeys(named(path_text)):
        if path.suffix.lower() == ".md" and path.is_file() and path.resolve() != record_path.resolve():
            card = path.read_text()
            texts.append(card)
            if path.resolve() in own:
                link_texts.append(card)
            commands += fenced_steps(card, shell_only=True)
    expanded = "\n".join(texts)
    asked = [normalized(fields.get("Asked", "")) for _, fields in steps]
    left = 0
    for number, fields in steps:
        request = normalized(fields.get("Asked", ""))
        if not request or request not in normalized(expanded):
            problems.append(f"step {number} S1: Asked text is not in the message")
        only = fields.get("Only he can", "").strip()
        left += bool(only)
        ran = fields.get("Ran", "").strip()
        unrun = re.fullmatch(r"none\s+[—–-]\s+\S.*", ran)
        if not ran or (not unrun and not execution_recorded(ran)):
            problems.append(f"step {number}: Ran needs fresh shell or real browser and a valid UTC timestamp, or none — <reason>")
        if (not fields.get("Observed", "").strip() or unrun) and not (unrun and only):
            problems.append(f"step {number} S2: no Observed output or justified unrun step")
        if "Only he can" in fields:
            reason = re.fullmatch(r"\S.*?\s+[—–-]\s+(\S.*)", only, re.S)
            if not reason or len(reason[1].split()) < 2:
                problems.append(f"step {number} S3: Only he can needs a reason of two or more words after the dash")
        for path in absolute_paths(fields.get("Asked", "")):
            if not path.exists():
                problems.append(f"step {number} S4: missing path {path}")
    for path in absolute_paths(asked_paths):
        if not path.exists():
            problems.append(f"message S4: missing path {path}")
    required_commands = [body for body in commands if normalized(body) not in observed]
    coverage_text = "\n".join(FENCE.sub(lambda match: "" if normalized(match[3]) in observed else match[0], text)
                              for text in link_texts)
    coverage_text += "\n" + "\n".join(required_commands)
    for item in required_commands + links(coverage_text):
        if not any(normalized(item) in request for request in asked):
            problems.append(f"message S5: unrecorded command or link {tok(item, words=10, chars=160)}")
    return problems, candidate, len(steps), left


def captain_steps_path_problems(record, folder=None):
    path = record.resolve()
    if folder is None:
        folder = next((p for p in path.parents if (p / "index.md").is_file()
                       or (p.parent / f"{p.name}.md").is_file()), path.parent.parent)
    folder = folder.resolve()
    if (path.parent != folder / "captain-steps" or not re.fullmatch(r"[1-9][0-9]*\.md", path.name)
            or not ((folder / "index.md").is_file() or (folder.parent / f"{folder.name}.md").is_file())):
        return [f"Captain steps record {record} is not {folder}/captain-steps/<N>.md (ADR 0054); move it there and name that path."]
    return []


def steps(args):
    try:
        record = Path(args.record).expanduser()
        message = Path(args.text_file).read_text()
        problems, _, count, left = inspect_steps(record, message, record.resolve().parent.parent)
        problems = captain_steps_path_problems(record) + problems
    except (OSError, UnicodeDecodeError) as error:
        emit(f"cannot read input: {error}")
        return 2
    if problems:
        emit(*problems, STEP_FORM)
        return 1
    emit(f"captain steps complete: {count} steps, {left} left to him")
    return 0


def captain_step_problems(task, gate_text, summary):
    declarations = re.findall(r"^Captain steps:[ \t]*(.*)$", "\n".join(outside_fences(summary)), re.M)
    if len(declarations) != 1 or not declarations[0].strip():
        return ["gate text needs one Captain steps: <record path> line"]
    folder = task_folder(task)
    path = named_file(folder, declarations[0].strip().strip("`\""))
    if problems := captain_steps_path_problems(path, folder):
        return problems
    report = (VALIDATION_SECTION.findall(task.read_text()) or [""])[-1]
    problems, candidate, _, _ = inspect_steps(path, gate_text, folder, report)
    if problems:
        return [f"Captain steps record fails: {problems[0]}"]
    candidates, _ = dispatched_candidates(task)
    if candidate not in candidates:
        return [f"Captain steps Candidate {candidate} differs from latest dispatched Candidate {' '.join(candidates) or 'none'}"]
    return []


def matching_delivery_record(task, text):
    records = [(int(m[1]), path) for path in (task_folder(task) / "merge").glob("ask-*.json")
               if (m := re.fullmatch(r"ask-(\d+)\.json", path.name))]
    if not records:
        return None
    path = max(records)[1]
    try:
        record = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    if not isinstance(record, dict) or not isinstance(head := record.get("head"), str) or not re.fullmatch(r"[0-9a-f]{7,40}", head):
        return None
    candidates, _ = dispatched_candidates(task)
    grants = re.findall(r"--match-head-commit\s+([0-9a-f]{7,40})\b", text)
    if not any(candidate.startswith(head) for candidate in candidates) or not grants or not all(head.startswith(sha) for sha in grants):
        return None
    if any(record.get(label.lower()) != clean(clause(text, label) or "")[:200] for label in CONFIRMATIONS):
        return None
    return path


def question(args):
    emit(CLAIM_SOURCE)
    task = Path(args.task)
    if task.is_dir():
        task = task / "index.md"
    try:
        task_text, gate_text = task.read_text(), Path(args.text_file).read_text()
        question_text = gate_text
        workflow_dir, scalars, lists = find_readme(task, args.workflow_dir)
        if not workflow_dir:
            raise ValueError("cannot find the workflow README with a trunk: next to the task or in --workflow-dir")
        second, extensions = reviewer_config(scalars, lists)
        # see docs/adr/0044-delivery-gate-summaries-carry-review-facts-with-legacy-call-compatibility.md
        reviewer_text = None
        if args.summary_file is not None:
            summary = Path(args.summary_file).read_text()
            gate_text, summary = scope_disclosure(task_folder(task), [(Path(args.text_file), gate_text), (Path(args.summary_file), summary)])
            summary = count_disclosure(task_folder(task), gate_text + "\n" + summary, Path(args.summary_file), summary)
            reviewer_text = "\n".join(outside_fences(summary))
            gate_text += "\n" + summary
        else:
            gate_text, = scope_disclosure(task_folder(task), [(Path(args.text_file), gate_text)])
            gate_text = count_disclosure(task_folder(task), gate_text, Path(args.text_file), gate_text)
        found, wanted = reviewer_problems(task, task_text,
                                         gate_text if reviewer_text is None else reviewer_text, second, extensions)
        if reviewer_text is not None:
            missing = summary_round_problems(reviewer_text)
            found += missing
            if missing:
                wanted.append("next: hold preparation; record the external round count in the summary.")
        missing = captain_step_problems(task, gate_text, summary if args.summary_file is not None else gate_text)
        found += missing
        if missing:
            wanted.append("next: hold preparation; run the Captain steps, record the observations at the dispatched head, and check again.")
    except (OSError, UnicodeDecodeError, ValueError) as error:
        emit(f"cannot read input: {error}")
        return 2
    problems, nexts = text_problems(task_text, gate_text, at_gate=True, reviewer_text=reviewer_text)
    delivery_record = None
    # see docs/adr/0071-the-merge-question-carries-its-delivery-check-record.md
    if GRANT.search(gate_text):
        delivery_record = matching_delivery_record(task, gate_text)
        if delivery_record is None:
            problems.append("the newest delivery check record is missing, unreadable or differs from the dispatched head, merge head or clauses")
            nexts.append("next: hold preparation; run delivery_gate.py check on this question and summary, then this check again.")
        elif json.loads(delivery_record.read_text()).get("merge_result") == "not run" and not MERGE_NOT_RUN.search("\n".join(outside_fences(question_text))):
            problems.append("the question itself needs Merge result: not run: <reason>")
            nexts.append("next: hold preparation; put the merge-result not-run line in the question the Captain reads.")
    if GRANT.search(gate_text) and not WORKTREE_REMOVAL.search(question_text):
        problems.append("the gate text names the merge with --match-head-commit but its question does not name removing its clean, pushed worktree")
        nexts.append("next: hold the gate; add 'and removing its clean, pushed worktree' to the question, then run this check again.")
    problems += found
    nexts += wanted
    emit(*problems, *dict.fromkeys(nexts))
    if not problems:
        emit("gate text complete", ASK_FORM)
        if delivery_record is not None:
            emit(f"next: run `spacedock state commit {task_folder(task).name} --workflow-dir {workflow_dir}`, then run `gate prepare` with `--reference {delivery_record}`.")
    return 1 if problems else 0


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
    ask = commands.add_parser("question")
    ask.add_argument("task")
    ask.add_argument("--text-file", required=True)
    ask.add_argument("--workflow-dir")
    ask.add_argument("--summary-file")
    run_merge = commands.add_parser("merge-run")
    run_merge.add_argument("task")
    run_merge.add_argument("--pr", required=True)
    run_merge.add_argument("--head")
    run_merge.add_argument("--trunk")
    run_merge.add_argument("--repo-dir")
    run_merge.add_argument("--workflow-dir")
    run_steps = commands.add_parser("steps")
    run_steps.add_argument("record")
    run_steps.add_argument("--text-file", required=True)
    argv = list(sys.argv[1:] if argv is None else argv)
    cut = argv.index("--") if "--" in argv else len(argv)
    args = parser.parse_args(argv[:cut])
    args.run = argv[cut + 1:]
    return {"question": question, "check": check, "steps": steps, "merge-run": merge_run}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
