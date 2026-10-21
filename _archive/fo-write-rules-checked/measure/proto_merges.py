#!/usr/bin/env python3
"""DEFERRED (cycle 3): prototype of the `Merges:` carried-merge rule (cycle 2 R4), kept as the evidence the D7 guard task starts from. Not part of this task's change.
The R1 and R2 functions below are the ones proto_gate.py now carries.

Usage: python3 -I -B proto_merges.py <package scripts dir> <state checkout>
The functions below are what the implementation would add to delivery_gate.py; they import the 0.26.0 module and change none of it.
The R4 cases edit one briefing's `index.json` (the question) or one task file's frontmatter in the working tree for each case
and restore it with `git checkout`, so the state checkout must be a scratch LINKED worktree of a clone (the design's runs used
/tmp/fwrc-work/state-wt at 8eda9070), never the live state checkout. R1 and R2 write nothing.

Cycle-2 rules for the carried merge (the engineering-reviewer's conditions 1 to 5, with condition 5 adapted):
  1. only a `by: person:captain` validation approval is read; an `agent:first-officer` approval never supplies the line
  2. the line is `Merges: <owner/repo>#<N> at <sha>` and the sha is a prefix of the PR head
  3. the line is the LAST sentence of the question, appears once, and has no text after the refs (`none` is allowed)
  4. no carried line when an amendment was committed after the approval (commit time, not the amendment's date)
  5. his words are echoed from the 「」 spans of the approval's reason (Spacedock refuses `conn_quote` on `person:captain`), and no span means ask
"""
import datetime, json, re, subprocess, sys
from pathlib import Path
pkg, state = sys.argv[1], Path(sys.argv[2])
sys.path.insert(0, pkg)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decision_ledger as dl
import delivery_gate as dg
import proto_scope as ps

END = re.compile(r"(?<![eE]\.[gG]\.)(?<![iI]\.[eE]\.)(?<=[.)\]])\s+(?=[A-Z][^.:\n]{0,40}:)|\n\n")
REF = re.compile(r"[\w.-]+/[\w.-]+#\d+")
ITEM = rf"({REF.pattern}) at ([0-9a-f]{{7,40}})"
TAIL = re.compile(rf"Merges: (none|{ITEM}(?:, {ITEM})*)\.?\s*\Z")
FINDING = re.compile(r"^\s*[-*]\s*\*{0,2}F\d+\*{0,2}\s*[:(]?\s*\(?\s*(Deferred risk|Polish)\b", re.M)
CLAIM = re.compile(r"\b(accepted|approved|waived|ruled)\b", re.I)
WORDS = re.compile(r"「([^」]*)」")


def declined_items(text):
    out = []
    for start in dg.DECLINE_START.finditer(text):
        rest = text[start.end():]
        end = END.search(rest)
        depth, item = 0, ""
        for ch in (rest[:end.start()] if end else rest).strip().rstrip("."):
            depth = max(depth + (ch in "([") - (ch in ")]"), 0)
            if ch == ";" and depth == 0:
                out.append(item.strip()); item = ""
            else:
                item += ch
        out.append(item.strip())
    return [i for i in out if i and i.lower() not in ("none", "nothing", "n/a")]


def reasons(item):
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


def unreasoned(text):
    return [i for i in declined_items(text) if not any(len(b.split()) >= 2 for b in reasons(i))]


def findings_join(task_text, gate_text):
    report = (dg.VALIDATION_SECTION.findall(task_text) or [""])[-1]
    owed, got = len(FINDING.findall(report)), len(declined_items(gate_text))
    return f"declined items ({got}) are fewer than the validation report's Deferred risk and Polish findings ({owed})" if owed and got < owed else None


def followups_claim(task):
    path = task.with_name(task.stem + "-followups.md")
    if not path.is_file():
        return None
    text = path.read_text()
    body = text.split("\n---\n", 1)[-1]
    first = next((l for l in body.splitlines() if l.strip()), "")
    title = (re.search(r"^title:\s*(.*)$", text, re.M) or [None, ""])[1]
    hit = CLAIM.search(title) or CLAIM.search(first)
    return f"{path.name} claims the Captain's acceptance (\"{hit.group(1)}\") before the gate that records it" if hit else None


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def merges(question, loose=False):
    """(list of (ref, sha) | [] for `none`, None) or (None, why): why is no-line or loose-line"""
    n = (question or "").count("Merges:")
    if n == 0:
        return None, "no-line"
    i = question.index("Merges:")
    if loose:
        return re.findall(ITEM, question[i:]), None
    before = question[:i]
    if n > 1 or (before and not (before.endswith("\n") or re.search(r"[.!?]\s+$", before))):
        return None, "loose-line"
    m = TAIL.fullmatch(question[i:])
    if not m:
        return None, "loose-line"
    return ([] if m.group(1) == "none" else re.findall(ITEM, m.group(1))), None


def approved(task, as_of=None, only_captain=True):
    """the newest validation approval; by default only a person:captain one, and none after as_of"""
    fm, _ = dl.split_task(task.read_text())
    got = [e for e in dl.gate_entries(fm) if e["stage"] == "validation" and e["kind"] == "resolution" and e.get("decision") == "approve"
           and (not only_captain or e.get("by") == "person:captain") and (as_of is None or ts(e["at"]) <= as_of)]
    if not got:
        return None, None
    return got[-1], dl.question(task.parent, task, got[-1]["room"])


def amended_after(task, entry, by_date=False):
    """an amendment committed after the approval's `at` (by_date: the 0.26.0 rule, an amendment dated on or after its day)"""
    _, body = dl.split_task(task.read_text())
    for number, date in dl.AMENDMENT.findall(body):
        if by_date:
            if date >= entry["at"][:10]:
                return True
            continue
        commit = ps.introducing_commit(task, number)
        if commit is None:
            return True
        when = ps.git(task, "log", "-1", "--format=%cI", commit).stdout.decode().strip()
        if not when or ts(when) > ts(entry["at"]):
            return True
    return False


ASK_RUN = "next: ask the Captain with this text; nothing is carried until he approves it."
ASK_RUN_TEACH = "next: ask the Captain with this text; to carry the merge, end the question with 'Merges: <owner/repo>#<N> at <head>' naming this PR and head."


def next_line(task, pr, head, as_of=None, by_date=False, mutate=(), text=None):
    """(line, why): why is the token that kept the merge from being carried, None when it is carried.
    text is the --text-file content; mutate names a guard to switch off, for the mutation runs: by, grammar, head, amended, quote"""
    entry, question = approved(task, as_of, only_captain="by" not in mutate)
    if entry is None:
        return (ASK_RUN if text is None or dg.clause(text, "Merges") else ASK_RUN_TEACH), "no-captain-approval"
    named, why = merges(question, loose="grammar" in mutate)
    if why is None:
        mine = [sha for ref, sha in named if ref == pr]
        why = "none" if not named else "other-pr" if not mine else "head-differs" if "head" not in mutate and not any(head.startswith(s) for s in mine) else None
    if why is None and "amended" not in mutate and amended_after(task, entry, by_date):
        why = "amended-after"
    words = " / ".join(WORDS.findall(entry.get("reason") or ""))[:100]
    if why is None and "quote" not in mutate and not words:
        why = "no-quote"
    if why is not None:
        teach = f" To carry it, end the question with 'Merges: {pr} at <head>'." if why == "no-line" else ""
        return f"next: ask the Captain to merge; the question he approved does not carry the merge of {pr} at this head ({why}).{teach}", why
    return (f"next: merge {pr} at {head[:12]} with --match-head-commit {head} and no other PR; the question he approved on {entry['at'][:10]} "
            f"ends with that in its Merges: line, and his words were 「{words}」. Ask instead if they say he merges or holds. "
            f"Every other PR, the Release PR included, is asked one at a time."), None


class Edited:
    """edit one tracked file of the scratch worktree for the length of a with-block, then restore it"""
    def __init__(self, rel, fn):
        self.rel, self.fn = rel, fn

    def __enter__(self):
        p = state / self.rel
        p.write_text(self.fn(p.read_text()))

    def __exit__(self, *exc):
        subprocess.run(["git", "-C", str(state), "checkout", "--", self.rel], check=True)


def with_line(task, attempt, tail):
    """a copy-in-place of the task's validation briefing question for `attempt` with `tail` appended; returns the Edited"""
    rel = f"{task.parent.relative_to(state)}/{task.stem}/review/validation/briefing-{attempt}/index.json" if task.parent != state else f"{task.stem}/review/validation/briefing-{attempt}/index.json"

    def fn(raw):
        d = json.loads(raw)
        d["question"] = d["question"].rstrip() + tail
        return json.dumps(d, ensure_ascii=False)
    return Edited(rel, fn)


def run_cases():
    arch = state / "_archive"

    def full(task):
        return dg.dispatched_candidates(task)[0][-1]

    def show(label, task, pr, head, edit=None, **kw):
        if edit is not None:
            with edit:
                line, why = next_line(task, pr, head, **kw)
        else:
            line, why = next_line(task, pr, head, **kw)
        print(f"  {label:70s} -> {why or 'CARRIED'}\n      {line}")
        return why

    src = arch / "special-role-calls-fire-when-needed.md"
    pr, head = "iamcxa/kc-claude-plugins#682", full(src)
    other = "iamcxa/kc-claude-plugins#672"
    print("-- ask run: a task with no validation approval (this task), by what the --text-file holds")
    mine = state / "fo-write-rules-checked.md"
    show("text has a Merges: clause", mine, pr, head, text=f"Deliver it. Merges: {pr} at {head[:8]}")
    show("text has no Merges: clause", mine, pr, head, text="Deliver it. Sufficiency: x. Necessity: y.")
    print("-- R4 on the real special-role-calls approval (Captain, 2026-10-20T03:03Z, reason holds 「合併」); PR head f4447396")
    show("as approved, no Merges: line (the #682 question)", src, pr, head)
    show("+ Merges: <#682> at f4447396", src, pr, head, with_line(src, 1, f" Merges: {pr} at {head[:8]}"))
    show("+ Merges: none", src, pr, head, with_line(src, 1, " Merges: none"))
    show("+ Merges: <#672 Release PR> at f4447396 (the #672 slip)", src, pr, head, with_line(src, 1, f" Merges: {other} at {head[:8]}"))
    show("+ Merges: <#682> at 0123abc (another head)", src, pr, head, with_line(src, 1, f" Merges: {pr} at 0123abc"))
    print("-- shape D: loose grammar")
    show("+ 'Merges: <#682> at f4447396; hold <#672> until this merges'", src, pr, head, with_line(src, 1, f" Merges: {pr} at {head[:8]}; hold {other} until this merges"))
    show("+ two Merges: lines", src, pr, head, with_line(src, 1, f" Merges: {pr} at {head[:8]}. Merges: none"))
    show("+ a sentence after the line", src, pr, head, with_line(src, 1, f" Merges: {pr} at {head[:8]}. Hold {other}."))
    show("+ 'Merges:' not at a sentence start", src, pr, head, with_line(src, 1, f", see Merges: {pr} at {head[:8]}"))
    show("+ refs without a head", src, pr, head, with_line(src, 1, f" Merges: {pr}"))
    print("-- shape A: an FO-recorded approval supplies the line (real FO approvals; Captain only revised)")
    for slug, attempt in (("review-cadence", 2), ("dispatch-and-report-hygiene", 3)):
        t = arch / f"{slug}.md"
        x = "iamcxa/kc-claude-plugins#1"
        show(f"{slug} validation-{attempt} (agent:first-officer) + Merges: line", t, x, "a" * 40, with_line(t, attempt, f" Merges: {x} at aaaaaaa"))
    t = arch / "extension-instruction-reaches-dispatch.md"
    x = "iamcxa/kc-claude-plugins#652"
    h2 = full(t)
    print("-- shape A, synthetic: his second approval re-recorded as agent:first-officer, line on it, his first approval has none")
    swap = Edited(f"_archive/{t.stem}.md", lambda s: s.replace('by: person:captain\n                at: "2026-10-17T02:15:54', 'by: agent:first-officer\n                at: "2026-10-17T02:15:54'))
    with swap:
        show("validation-2 by agent:first-officer + line at ef7a360e", t, x, h2, with_line(t, 2, f" Merges: {x} at {h2[:8]}"))
    print("-- shape B: an approval of an earlier head (extension-instruction-reaches-dispatch, #652)")
    window = ts("2026-10-17T00:30:00Z")
    show("window: only his 10-16 approval of 8d051de7 exists; PR head is ef7a360e", t, x, h2, with_line(t, 1, f" Merges: {x} at 8d051de7"), as_of=window)
    show("after his 10-17 approval of ef7a360e + line at ef7a360e (amendment 1 committed before it)", t, x, h2, with_line(t, 2, f" Merges: {x} at {h2[:8]}"))
    show("the same, with the 0.26.0 date rule for amendments (mutation)", t, x, h2, with_line(t, 2, f" Merges: {x} at {h2[:8]}"), by_date=True)
    print("-- shape C: an amendment committed after the approval")
    c_window = ts("2026-10-17T01:55:00Z")
    h1 = "8d051de7" + "0" * 32
    show("his 10-16 approval + line at 8d051de7, PR head 8d051de7; amendment 1 committed 10-17T01:50Z", t, x, h1, with_line(t, 1, f" Merges: {x} at 8d051de7"), as_of=c_window)
    print("-- condition 5: no word of his in the approval")
    q = arch / "prod-security-validation-gate.md"
    fm, _ = dl.split_task(q.read_text())
    e = [g for g in dl.gate_entries(fm) if g["stage"] == "validation" and g.get("decision") == "approve"][-1]
    qh = full(q)
    show("prod-security-validation-gate (reason quotes him in ASCII quotes, no 「」) + line", q, "iamcxa/kc-claude-plugins#659", qh,
         with_line(q, int(e["room"].rsplit("-", 1)[1]), f" Merges: iamcxa/kc-claude-plugins#659 at {qh[:8]}"))
    print("-- mutations: each switches off ONE guard and must turn the case that only that guard stops")
    print("   (shape A real FO approvals also stop at no-quote: the FO's reason carries no 「」 span, so the synthetic case below is the one only the by: guard stops)")
    with swap:
        show("MUTATION by: shape A synthetic, line on his re-recorded approval", t, x, h2, with_line(t, 2, f" Merges: {x} at {h2[:8]}"), mutate=("by",))
    rc = arch / "review-cadence.md"
    show("MUTATION by alone: shape A real review-cadence validation-2 (stopped by no-quote instead)", rc, "iamcxa/kc-claude-plugins#1", "a" * 40,
         with_line(rc, 2, " Merges: iamcxa/kc-claude-plugins#1 at aaaaaaa"), mutate=("by",))
    show("MUTATION grammar: shape D, findall over the rest of the question", src, pr, head, with_line(src, 1, f" Merges: {pr} at {head[:8]}; hold {other} until this merges"), mutate=("grammar",))
    show("MUTATION head: line at 0123abc, PR head f4447396, no head compare", src, pr, head, with_line(src, 1, f" Merges: {pr} at 0123abc"), mutate=("head",))
    show("MUTATION head alone: shape B window (the amendment guard still stops it)", t, x, h2, with_line(t, 1, f" Merges: {x} at 8d051de7"), as_of=window, mutate=("head",))
    show("MUTATION head and amended: shape B window (nothing left to stop it)", t, x, h2, with_line(t, 1, f" Merges: {x} at 8d051de7"), as_of=window, mutate=("head", "amended"))
    show("MUTATION amended: shape C, no amendment check", t, x, h1, with_line(t, 1, f" Merges: {x} at 8d051de7"), as_of=c_window, mutate=("amended",))
    show("MUTATION quote: no-quote case, no span required", q, "iamcxa/kc-claude-plugins#659", qh,
         with_line(q, int(e["room"].rsplit("-", 1)[1]), f" Merges: iamcxa/kc-claude-plugins#659 at {qh[:8]}"), mutate=("quote",))


def run_census():
    print("-- R2: the presented declined texts of the three gates written after #671 merged (2026-10-19T08:10Z), and fo-write-checks (its own gate, minutes before): 0.26.0 check vs fixed parse")
    for slug in ("captain-question-load", "chat-only-evidence-observer-blind", "special-role-calls-fire-when-needed", "fo-write-checks"):
        for f in sorted((state / "_archive" / slug / "review" / "validation").glob("briefing-*/index.json")):
            d = json.loads(f.read_text())
            text = d["question"] + "\n" + d["artifacts"][0].get("summary", "")
            print(f"   {slug[:38]:38s} items {len(dg.declined_items(text))}->{len(declined_items(text))}  unreasoned {len(dg.unreasoned_items(text))}->{len(unreasoned(text))}")
    print("-- R2: findings join on special-role (F-id bullets in the report vs the declined items of the presented text)")
    task = state / "_archive" / "special-role-calls-fire-when-needed.md"
    d = json.loads((task.parent / "special-role-calls-fire-when-needed/review/validation/briefing-1/index.json").read_text())
    sha = re.search(r"git-root://state/([0-9a-f]{40})/", d["artifacts"][0]["uri"]).group(1)
    old = subprocess.run(["git", "-C", str(state), "show", f"{sha}:special-role-calls-fire-when-needed.md"], capture_output=True).stdout.decode()
    print("  ", findings_join(old, d["question"] + "\n" + d["artifacts"][0].get("summary", "")))
    print("-- R1: follow-ups tasks beside their task, as they stand at the pin")
    for t in sorted(state.glob("*.md")) + sorted((state / "_archive").glob("*.md")):
        hit = followups_claim(t) if not t.stem.endswith("followups") else None
        if hit:
            print("  ", hit)


if __name__ == "__main__":
    run_census()
    run_cases()
