#!/usr/bin/env python3
"""Replay the four FO-write rules over a dev2 state branch, read-only.

Usage: python3 -I -B replay.py <git repo> <state ref or sha> <package scripts dir> [r1 r2 r3 r4]
Reads committed bytes with `git show` / `git archive`; writes nothing under <git repo>.
r1 follow-ups tasks that claim the Captain's acceptance; r2 declined items and validator findings;
r3 Scope edits after the backlog gate; r4 merge-grant census.
"""
import collections, datetime, json, os, re, subprocess, sys, tempfile
repo, ref, pkg = sys.argv[1:4]
which = set(sys.argv[4:]) or {"r1", "r2", "r3", "r4"}
sys.path.insert(0, pkg)
import decision_ledger as dl, delivery_gate as dg


def git(*a):
    return subprocess.run(["git", "-C", repo, "-c", "core.quotepath=off", *a], capture_output=True).stdout.decode("utf-8", "replace")


def blob(sha, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


HEAD = git("rev-parse", ref).strip()
snap = tempfile.mkdtemp(prefix="replay-")
subprocess.run(f"git -C '{repo}' archive {HEAD} | tar -x -C '{snap}'", shell=True, check=True)
rows = dl.ledger(__import__("pathlib").Path(snap))
files = git("ls-tree", "-r", "--name-only", HEAD).splitlines()
TASK = re.compile(r"(?:_archive/)?([^/]+)\.md$")
tasks = [f for f in files if TASK.fullmatch(f) and not f.endswith("README.md")]
commits = [l.split("|", 2) for l in git("log", "--first-parent", "--reverse", "--format=%H|%cI|%s", HEAD).splitlines()]
BRIEF = re.compile(r"/review/[^/]+/briefing-\d+/index\.json$")
nbrief = sum(1 for f in files if BRIEF.search(f))
nres = sum(1 for r in rows if r["kind"] == "resolution")
print(f"corpus {repo.rsplit('/',1)[-1]} {ref} = {HEAD[:12]}: {len(commits)} commits, {len(tasks)} task files, {nres} gate resolutions, {nbrief} briefings")


def body(text):
    if text is None:
        return []
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        text = text[end + 5:] if end > 0 else text
    return text.splitlines()


def task_events():
    """yield (sha, when, subject, slug, old text, new text) for each commit that edits a task file."""
    prev = {}
    for sha, when, subj in commits:
        out = git("show", "--no-renames", "--name-status", "--format=", sha)
        for line in out.splitlines():
            parts = line.split("\t")
            m = TASK.fullmatch(parts[-1])
            if not m or parts[-1].endswith("README.md") or parts[0][0] == "D":
                continue
            new = blob(sha, parts[-1])
            old = prev.get(m[1])
            prev[m[1]] = new
            yield sha, when, subj, m[1], old, new


if "r1" in which:
    print("\n== R1 follow-ups task that claims the Captain's acceptance (title or first paragraph)")
    CLAIM = re.compile(r"\b(accepted|approved|waived|ruled)\b", re.I)
    seen, flagged = set(), []
    for sha, when, subj, slug, old, new in task_events():
        if not re.search(r"follow-?ups?$", slug):
            continue
        seen.add(slug)
        title = re.search(r"^title:\s*(.*)$", new, re.M)
        first = next((l for l in body(new) if l.strip()), "")
        was = (re.search(r"^title:\s*(.*)$", old or "", re.M) or [None, ""])[1] + next((l for l in body(old) if l.strip()), "")
        for where, text in (("title", title.group(1) if title else ""), ("first paragraph", first)):
            if CLAIM.search(text) and not CLAIM.search(was):
                flagged.append((slug, sha[:8], when[:16], where, text[:110]))
    print(f"follow-ups tasks seen: {len(seen)}; flagged: {len(flagged)}")
    for f in flagged:
        print("  FLAG", f)

if "r2" in which:
    print("\n== R2 declined items and validator findings, per validation briefing")
    FIND = re.compile(r"^\s*[-*]\s*\*{0,2}(?:F\d+\*{0,2}\s*[:(]?\s*\(?\s*)?(Material|Deferred risk|Polish|Needs decision)\b", re.M)
    COUNT = re.compile(r"\b(Deferred risk|Polish)\s*\((\d+)")
    FIND_F = re.compile(r"^\s*[-*]\s*\*{0,2}F\d+\*{0,2}\s*[:(]?\s*\(?\s*(Material|Deferred risk|Polish|Needs decision)\b", re.M)
    ITEM = re.compile(r"^\s*(?:Codex |roborev:\d+ )?(Deferred risk|Polish|Material|Needs decision|P[12])\b", re.I)

    def brackets2(item):
        found, depth, start = [], 0, 0
        for i, ch in enumerate(item):
            if ch in "([":
                start = i + 1 if depth == 0 else start
                depth += 1
            elif ch in ")]" and depth:
                depth -= 1
                if depth == 0:
                    found.append(item[start:i])
        return found

    END2 = re.compile(r"(?<![eE]\.[gG]\.)(?<![iI]\.[eE]\.)(?<=[.)\]])\s+(?=[A-Z][^.:\n]{0,40}:)|\n\n")

    def items2(text):
        out = []
        for start in dg.DECLINE_START.finditer(text):
            rest = text[start.end():]
            end = END2.search(rest)
            depth, item = 0, ""
            for ch in (rest[:end.start()] if end else rest).strip().rstrip("."):
                depth = max(depth + (ch in "([") - (ch in ")]"), 0)
                if ch == ";" and depth == 0:
                    out.append(item.strip()); item = ""
                else:
                    item += ch
            out.append(item.strip())
        return [i for i in out if i and i.lower() not in ("none", "nothing", "n/a")]

    stats = collections.Counter()
    table = []
    for f in sorted(x for x in files if re.search(r"/review/validation/briefing-\d+/index\.json$", x)):
        d = json.loads(blob(HEAD, f))
        art = d["artifacts"][0]
        m = re.search(r"git-root://state/([0-9a-f]{40})/(.+)$", art["uri"])
        text = d["question"] + "\n" + art.get("summary", "")
        whenfull = git("log", "-1", "--format=%cI", m.group(1)).strip()
        when = whenfull[:10]
        report = (dg.VALIDATION_SECTION.findall(blob(m.group(1), m.group(2)) or "") or [""])[-1]
        cur, new = dg.declined_items(text), items2(text)
        stats["briefings"] += 1
        stats["mention Deferred risk, Polish or declin* but carry no Declined/FO declines label"] += \
            bool(re.search(r"declin|Deferred|Polish", text, re.I)) and not dg.DECLINE_START.search(text)
        if not dg.DECLINE_START.search(text):
            continue
        stats["with a decline"] += 1
        stats["current parse < new parse"] += len(cur) < len(new)
        stats["current check would hold the presented text"] += bool(dg.unreasoned_items(text))
        stats["reason in [ ] only"] += any(brackets2(i) and not dg.brackets(i) for i in new)
        late = ts(whenfull) >= ts("2026-10-19T08:10:12Z")
        stats["late (bound sha committed after #671 merged, 2026-10-19T08:10:12Z) with a decline"] += late
        stats["late: the shipped check holds the presented text"] += late and bool(dg.unreasoned_items(text))
        stats["late: bracket-fixed check holds it"] += late and any(len([w for b in brackets2(i) for w in b.split()]) < 2 for i in new)
        stats["all: bracket-fixed check holds it"] += any(len([w for b in brackets2(i) for w in b.split()]) < 2 for i in new)
        fform = collections.Counter(c for c in FIND_F.findall(report) if c in ("Deferred risk", "Polish"))
        anyform = collections.Counter(c for c in FIND.findall(report) if c in ("Deferred risk", "Polish")) or \
            collections.Counter({c: int(n) for c, n in COUNT.findall(report)})
        short_any = bool(anyform) and len(new) < sum(anyform.values())
        stats["F-id bullets"] += bool(fform)
        stats["class bullets or counts, no F id"] += bool(anyform) and not fform
        stats["no countable findings"] += not anyform
        stats["join on any countable form would hold"] += short_any
        stats["join on F-id form would hold"] += bool(fform) and len(new) < sum(fform.values())
        form = "F-id" if fform else "class/count" if anyform else "none"
        table.append((f.split("/review")[0].replace("_archive/", "")[:38], when, form, dict(fform or anyform), f"{len(new)} items", "HOLD-any" if short_any else "ok",
                      "HOLD-F" if fform and len(new) < sum(fform.values()) else "-"))
    for k, v in stats.items():
        print(f"  {k}: {v}")
    for t in table:
        print("  ", t)

if "r3" in which:
    print("\n== R3 Scope edits after the backlog gate closed (Non-goals lines excepted), by era")
    closed = {}
    for r in rows:
        if r["kind"] == "resolution" and r["decision"] == "approve" and r["stage"] == "backlog":
            closed.setdefault(r["task"], ts(r["at"]))
    AMD = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2})", re.M)

    def scope(text):
        m = re.search(r"^## Scope\b[^\n]*\n(.*?)(?=^## |\Z)", text or "", re.M | re.S)
        return m.group(1) if m else ""

    NONGOAL = re.compile(r"\s*(?:[-*]\s*)?(?:Non-goals?\b|Budget\b|Stop condition\b|Follow-up:)", re.I)
    ev = []
    for sha, when, subj, slug, old, new in task_events():
        gate = closed.get(slug)
        if old is None or gate is None or ts(when) <= gate:
            continue
        o, n = collections.Counter(scope(old).splitlines()), collections.Counter(scope(new).splitlines())
        added = [l for l in scope(new).splitlines() if n[l] > o[l] and l.strip() and not NONGOAL.match(l)]
        removed = [l for l in scope(old).splitlines() if o[l] > n[l] and l.strip() and not NONGOAL.match(l)]
        if not added and not removed:
            continue
        dated = [d for _, d in AMD.findall(new) if d >= gate.strftime("%Y-%m-%d")]
        ev.append((slug, sha[:8], when, bool(dated), len(added), len(removed), (added or removed)[0][:100]))
    ERA = ts("2026-09-30T10:00:00Z")
    late = [e for e in ev if ts(e[2]) >= ERA]
    print(f"  events after the gate, all dates: {len(ev)} in {len({e[0] for e in ev})} tasks; "
          f"on or after 2026-09-30 (the amendment rule's day): {len(late)} in {len({e[0] for e in late})} tasks, "
          f"of which an amendment dated on or after the gate exists in {sum(e[3] for e in late)}")
    named = lambda e: bool(re.search(r"Captain|「", e[6]))
    print(f"  of the {len(late)}: first changed line names the Captain or quotes 「」: {sum(named(e) for e in late)}; other: {sum(not named(e) for e in late)}")
    approved = collections.defaultdict(dict)
    for r in rows:
        if r["kind"] == "resolution" and r["decision"] == "approve":
            approved[r["task"]].setdefault(r["stage"], ts(r["at"]))

    def window(e):
        """the stage whose gate was still open when the commit landed: the first stage with no approval before it, else 'after the last gate'"""
        order = sorted(approved[e[0]].items(), key=lambda kv: kv[1])
        for stage, at in order:
            if ts(e[2]) <= at:
                return stage + "-gate-open"
        return "after-" + (order[-1][0] if order else "none")
    print("  window of each held or amended event (the gate that was still open when it landed):",
          dict(collections.Counter(window(e) for e in late)))
    for e in late:
        print("  ", "ok-amended" if e[3] else "HOLD", "captain-line" if named(e) else "other", window(e), e)

if "r4" in which:
    print("\n== R4 validation approvals: does the approved question carry the merge?")
    CARRY = re.compile(r"FO merges it|authorizes FO to merge|merges? that exact checked head", re.I)
    ASKS = re.compile(r"asks you to merge", re.I)
    sentinel = {}
    for f in tasks:
        m = re.search(r"^pr:\s*['\"]?pr-merge:(\d+)", blob(HEAD, f) or "", re.M)
        if m:
            sentinel[TASK.fullmatch(f)[1]] = m[1]
    approvals = [r for r in rows if r["stage"] == "validation" and r["decision"] == "approve"]
    c = collections.Counter()
    for r in approvals:
        q = r["question"] or ""
        c["approvals"] += 1
        c["by captain"] += r["by"] == "person:captain"
        c["question carries the merge"] += bool(CARRY.search(q))
        c["question says FO asks him to merge"] += bool(ASKS.search(q))
        c["with a pr-merge sentinel"] += r["task"] in sentinel
        c["sentinel and no carried merge"] += r["task"] in sentinel and not CARRY.search(q)
    for k, v in c.items():
        print(f"  {k}: {v}")
    asks = [f for f in files if "/merge/ask-" in f]
    cc = collections.Counter()
    for f in asks:
        a = json.loads(blob(HEAD, f))
        cc[(a.get("class"), a.get("verdict"))] += 1
    print("  merge/ask-N.json records (class, verdict):", dict(cc))
