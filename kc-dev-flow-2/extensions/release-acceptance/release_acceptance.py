#!/usr/bin/env python3
"""Build, check and render a release walk: picky-user reviewer reports, the design director's ruling, one record.

  deferred JOURNEY/RELEASE --workflow-dir D     list findings earlier tasks of the release deferred
  check FOLDER --tier walk|final --workflow-dir D [--prior REPORT]
                                                exit 1 when the walk cannot be accepted as it stands
  director-model FOLDER --workflow-dir D        print the one model the design director runs on for this walk
  build FOLDER --workflow-dir D [--prior REPORT]  write walk/report.json from the walk files and walk/ruling.json
  render FOLDER [--check]                       print record.md from report.json; --check compares walk/record.md
  schema release-acceptance                     print the field table, its version and where the history lives

FOLDER is the acceptance task's folder; every walk file is JSON in FOLDER/walk/. Standard library only.
It decides nothing: the Captain accepts the walk at the validation gate.
"""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from delivery_gate import FINDING  # noqa: E402
from number_guards import frontmatter  # noqa: E402

SCHEMA = "release-acceptance"
WIRE = "release-acceptance/v1"
WALK_WIRE = "release-walk/v1"
FIELDS = (
    ("schema", "the string `release-acceptance/v1` (wire pin: major only)"),
    ("walk", "`{journey, release, source_commit}` of the walk list the reviewers followed"),
    ("target", "`{environment, ref}` the product ran as"),
    ("smoke", "`{result: passed, check, evidence[]}`; reviewers start only after a passed smoke"),
    ("diversity", "`{mode: multi-model|single-model, reviewers, models}`"),
    ("reviewers", "`[{id, model, persona}]`, no other key"),
    ("stories", "one `{id, result, reported_by[], entry, evidence[], cause}` per walk story, the most severe result"),
    ("proof_line", "`{result, evidence[], cause}`, the most severe result"),
    ("walks", "one reviewer's own report each: stories, proof_line, complaints, deferred_verdicts, would_miss, recommend, marks"),
    ("ruling", "`{director{agent, model}, items[], deferred[], tasks[]}`; one director model per walk"),
    ("complaint_rows", "one `{complaint, reviewer, task, status, reason}` per reviewer complaint"),
    ("not_tested", "strings, what the walk did not exercise"),
    ("data_left", "strings, data the walk left in the product"),
    ("prior", "`{digest}` of the first walk's report.json, present only on a re-walk"),
)
VERSIONS = HERE / "contract-versions.json"
ADR_TITLE = "a-release-walk-is-operated-by-reviewers-on-different-models-and-ruled-by-the-design-director-on-one-model-per-walk"
FOOTER = (
    "Current table: python3 kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py schema release-acceptance\n"
    "Every version: kc-dev-flow-2/CHANGELOG.md, written by release-please from each commit.\n"
    f"First shape and each MAJOR: an ADR in the kc-claude-plugins docs/adr/ ({ADR_TITLE}).\n"
    "Read the CHANGELOG when a report carries a schema string you have not seen; read the ADR before removing or renaming a field."
)

SEVERITY = ("missing-entry-point", "broken", "not-reachable", "works")
PROOF_RESULTS = ("works", "broken", "not-reachable")
VERDICTS = ("agree", "disagree", "cannot-tell")
MARKS = ("fixed", "partly-fixed", "deferred", "will-not-fix")
REAL = ("yes", "no", "unverified")
RULINGS = ("solve", "do-not-solve", "decision")
WHEN = ("this-round", "next-release", "later", "never")
CLASSES = ("defect", "works-but-unusable", "polish", "known-gap", "by-design", "not-defect")
ROW_STATUS = re.compile(r"^(?:to-fix|decision|will-not-fix|fixed|partly-fixed|deferred:\S+)$")
REVIEWER_KEYS = {"id", "model", "persona"}
MAX_TASKS = 3

VALIDATION = re.compile(r"^## Stage Report: validation[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)
DECLINED = re.compile(r"\bdeclined:[ \t]*(\S.*)$", re.I)
NEEDS_DECISION = re.compile(r"\bNeeds decision:[ \t]*(\S.*)$")
BUILT_SCREEN = re.compile(r"\bBuilt screen finding\b.*$")
FM_KEY = re.compile(r"^([\w-]+):[ \t]*(.*?)[ \t]*$")
COMPLAINT_LINE = re.compile(r"^Walk complaints:[ \t]*(\S.*)$", re.M)
OPUS = re.compile(r"opus", re.I)
MODEL_LINE = re.compile(r"^Model:[ \t]*(\S.*)$", re.M)


class Refused(Exception):
    pass


def table_text():
    return "| field | rule |\n|---|---|\n" + "\n".join(f"| `{n}` | {r} |" for n, r in FIELDS)


def table_hash():
    return hashlib.sha256(table_text().encode()).hexdigest()


def version_problem(name):
    if name != SCHEMA:
        return f"unknown schema {name!r}; only {SCHEMA}"
    try:
        entry = json.loads(VERSIONS.read_text())[SCHEMA]
        recorded = entry["versions"].get(entry["current"])
    except (OSError, ValueError, KeyError):
        return f"{SCHEMA}: {VERSIONS.name} is unreadable or lacks the schema"
    if recorded is None:
        return f"{SCHEMA}: current version {entry['current']} has no recorded hash in {VERSIONS.name}"
    if recorded != table_hash():
        return (f"{SCHEMA}: the field table changed but version {entry['current']} did not; "
                f"bump `current` and record the new hash {table_hash()} in {VERSIONS.name}")
    return None


def cmd_schema(args):
    problem = version_problem(args.name)
    if args.name == SCHEMA:
        print(f"{SCHEMA} {json.loads(VERSIONS.read_text())[SCHEMA]['current']}")
        print(table_text())
        print(FOOTER)
    if problem:
        print(problem, file=sys.stderr)
        return 1
    return 0


def read_json(path):
    path = Path(path)
    if not path.is_file():
        raise Refused(f"{path.name} is absent")
    text = path.read_text().strip()
    fenced = re.match(r"^```(?:json)?[ \t]*\n(.*)\n```$", text, re.S)
    try:
        return json.loads(fenced.group(1) if fenced else text)
    except ValueError as error:
        raise Refused(f"{path.name} is not JSON: {error}")


def digest_of(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value):
    return isinstance(value, str) and bool(value.strip())


def release_id(value):
    return text(value) and len(value.split()) == 1


def strings(value):
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


class Task:
    def __init__(self, path):
        self.path = Path(path)
        self.slug = self.path.stem
        self.folder = self.path.with_suffix("")
        self.text = self.path.read_text()
        self.fields = {}
        match = re.match(r"---\n(.*?)\n---", self.text, re.S)
        for line in match.group(1).splitlines() if match else []:
            key = FM_KEY.match(line)
            if key and not line.startswith((" ", "-")):
                self.fields[key.group(1)] = key.group(2).strip("'\"")

    def validation_report(self):
        found = VALIDATION.findall(self.text)
        return found[-1] if found else ""


def state_dir(workflow_dir):
    workflow_dir = Path(workflow_dir)
    state = frontmatter(workflow_dir / "README.md").get("state", "")
    return workflow_dir / state if state else workflow_dir


def release_tasks(workflow_dir, journey, release):
    """Live and archived tasks of the release, the acceptance tasks themselves excluded."""
    state = state_dir(workflow_dir)
    tasks = []
    for path in sorted([*state.glob("*.md"), *(state / "_archive").glob("*.md")], key=lambda p: p.stem):
        if path.name == "README.md":
            continue
        task = Task(path)
        fields = task.fields
        if fields.get("journey-release") == release and fields.get("journey", journey) in ("", journey) \
                and "release-acceptance" not in fields:
            tasks.append(task)
    return tasks


def deferred_items(workflow_dir, journey, release):
    """The newest validation report's deferred findings of each task of the release, as [(id, text)]."""
    items = []
    for task in release_tasks(workflow_dir, journey, release):
        counts = collections.Counter()
        for line in task.validation_report().splitlines():
            if FINDING.match(line):
                key = "F" + re.search(r"F(\d+)", line).group(1)
            else:
                kind = next((k for k, rx in (("declined", DECLINED), ("decision", NEEDS_DECISION), ("screen", BUILT_SCREEN))
                             if rx.search(line)), None)
                if kind is None:
                    continue
                counts[kind] += 1
                key = f"{kind}-{counts[kind]}"
            items.append((f"{task.slug}#{key}", line.strip()[:300]))
    return items


def owners_by_story(workflow_dir, journey, release):
    owners = collections.defaultdict(list)
    for task in release_tasks(workflow_dir, journey, release):
        if task.fields.get("journey-story"):
            owners[task.fields["journey-story"]].append(task)
    return owners


def complaint_links(workflow_dir, journey, release):
    """complaint id -> filed task slugs, from each task's one `Walk complaints:` line."""
    links = collections.defaultdict(list)
    for task in release_tasks(workflow_dir, journey, release):
        for line in COMPLAINT_LINE.findall(task.text):
            for cid in re.split(r"[,\s]+", line.strip()):
                if cid and task.slug not in links[cid]:
                    links[cid].append(task.slug)
    return links


def ideation_model(task):
    """(opus?, note) for one task: any ideation dispatch record naming opus counts."""
    if task.fields.get("profile") == "poc":
        return False, f"no ideation stage: {task.slug}"
    models = [m.group(1) for r in sorted(task.folder.glob("dispatch/ideation-*.md"))
              if (m := MODEL_LINE.search(r.read_text()))]
    if not models:
        return False, f"ideation model unrecorded: {task.slug}"
    return any(OPUS.search(m) for m in models), None


def worst(results):
    return min(results, key=SEVERITY.index)


def consolidate(walks, walk_stories):
    rows = []
    for sid in walk_stories:
        got = [(w["reviewer"]["id"], r) for w in walks for r in w.get("stories", [])
               if isinstance(r, dict) and r.get("id") == sid and r.get("result") in SEVERITY]
        if not got:
            continue
        top = worst(r["result"] for _, r in got)
        same = [(who, r) for who, r in got if r["result"] == top]
        rows.append({
            "id": sid, "result": top, "reported_by": [who for who, _ in same],
            "entry": same[0][1].get("entry", ""),
            "evidence": sorted({e for _, r in same for e in r.get("evidence", []) if isinstance(e, str)}),
            "cause": next((r["cause"] for _, r in same if text(r.get("cause"))), ""),
        })
    return rows


def consolidate_proof(walks):
    got = [w["proof_line"] for w in walks if isinstance(w.get("proof_line"), dict) and w["proof_line"].get("result") in PROOF_RESULTS]
    if not got:
        return {"result": "not-reachable", "evidence": [], "cause": "no reviewer performed the proof line"}
    top = worst(p["result"] for p in got)
    same = [p for p in got if p["result"] == top]
    return {"result": top, "evidence": sorted({e for p in same for e in p.get("evidence", []) if isinstance(e, str)}),
            "cause": next((p["cause"] for p in same if text(p.get("cause"))), "")}


def operated(walk):
    return any(isinstance(r, dict) and r.get("result") != "not-reachable" for r in walk.get("stories", []))


def walk_problems(walks, walk_ids, folder, deferred_ids, prior):
    """Reviewer-level refusals: structure, evidence files, complaint ids, deferred verdicts, re-walk marks."""
    out, seen_ids = [], collections.Counter()
    for w in walks:
        who = (w.get("reviewer") or {}).get("id", "?") if isinstance(w.get("reviewer"), dict) else "?"
        row = w.get("reviewer")
        if not isinstance(row, dict) or not all(text(row.get(k)) for k in REVIEWER_KEYS):
            out.append(f"reviewer {who}: needs id, model and persona")
        elif set(row) - REVIEWER_KEYS:
            out.append(f"reviewer {who}: unknown key {sorted(set(row) - REVIEWER_KEYS)}")
        complaints = [c for c in w.get("complaints", []) if isinstance(c, dict)]
        defined = {c.get("id") for c in complaints}
        for c in complaints:
            seen_ids[c.get("id")] += 1
            if not text(c.get("id")) or not text(c.get("seen")) or not isinstance(c.get("rank"), int) or c["rank"] < 1:
                out.append(f"reviewer {who}: complaint {c.get('id')!r} needs id, seen and an integer rank of 1 or more")
            if not strings(c.get("stories")) or set(c["stories"]) - set(walk_ids):
                out.append(f"reviewer {who}: complaint {c.get('id')!r} names a story that is not on the walk")
            out += evidence_problems(folder, f"reviewer {who}: complaint {c.get('id')!r}", c.get("evidence"))
        stories = [r for r in w.get("stories", []) if isinstance(r, dict)]
        counts = collections.Counter(r.get("id") for r in stories)
        out += [f"reviewer {who}: walk story {s} missing" for s in walk_ids if counts[s] == 0]
        out += [f"reviewer {who}: walk story {s} duplicated" for s in walk_ids if counts[s] > 1]
        out += [f"reviewer {who}: story {s} is not on the walk" for s in counts if s not in walk_ids]
        for r in stories:
            tag = f"reviewer {who}: story {r.get('id')}"
            if r.get("result") not in SEVERITY:
                out.append(f"{tag}: result {r.get('result')!r} is not one of {', '.join(SEVERITY)}")
                continue
            if r["result"] == "not-reachable" and not text(r.get("cause")):
                out.append(f"{tag}: not-reachable names no cause")
            cited = r.get("complaints") if strings(r.get("complaints")) else []
            if r["result"] != "works" and not cited:
                out.append(f"{tag}: {r['result']} names no complaint")
            out += [f"{tag}: complaint id {c!r} is not defined" for c in cited if c not in defined]
            if r["result"] == "works" and not r.get("evidence"):
                out.append(f"{tag}: works with no evidence")
            out += evidence_problems(folder, tag, r.get("evidence"))
        proof = w.get("proof_line")
        if not isinstance(proof, dict) or proof.get("result") not in PROOF_RESULTS:
            out.append(f"reviewer {who}: proof line is absent or its result is not one of {', '.join(PROOF_RESULTS)}")
        else:
            if proof["result"] == "not-reachable" and not text(proof.get("cause")):
                out.append(f"reviewer {who}: proof line not-reachable names no cause")
            if proof["result"] == "works" and not proof.get("evidence"):
                out.append(f"reviewer {who}: proof line works with no evidence")
            out += evidence_problems(folder, f"reviewer {who}: proof line", proof.get("evidence"))
        verdicts = {v.get("item"): v for v in w.get("deferred_verdicts", []) if isinstance(v, dict)}
        for item in deferred_ids:
            v = verdicts.get(item)
            if not v or v.get("verdict") not in VERDICTS or not text(v.get("why")):
                out.append(f"reviewer {who}: deferred item {item} has no verdict (agree, disagree or cannot-tell) with a why")
        out += [f"reviewer {who}: verdict on {i}, which is not a deferred item of the release" for i in verdicts if i not in deferred_ids]
        for key in ("would_miss", "recommend"):
            if not isinstance(w.get(key), str):
                out.append(f"reviewer {who}: {key} is absent")
        out += mark_problems(w, who, prior)
    out += [f"complaint id {c!r} used {n} times" for c, n in seen_ids.items() if n > 1]
    return out


def evidence_problems(folder, tag, files):
    if files is None:
        return []
    if not strings(files):
        return [f"{tag}: evidence is not a list of file names"]
    root = (folder / "walk").resolve()
    return [f"{tag}: evidence {f} is not a file in {folder.name}/walk" for f in files
            if not ((root / f).resolve().is_file() and root in (root / f).resolve().parents)]


def prior_owned(prior):
    owned = collections.defaultdict(list)
    for w in (prior or {}).get("walks", []):
        owned[w["reviewer"]["id"]] += [c["id"] for c in w.get("complaints", [])]
    return owned


def mark_problems(w, who, prior):
    marks = w.get("marks")
    if prior is None:
        return [f"reviewer {who}: marks without a prior walk"] if marks else []
    rows = {r["id"]: r for r in prior.get("reviewers", [])}
    if who not in rows:
        return [f"reviewer {who}: not a reviewer of the prior walk"]
    out = []
    if w.get("reviewer") != rows[who]:
        out.append(f"reviewer {who}: id, model or persona differs from the prior walk's row {rows[who]}")
    owned = prior_owned(prior)[who]
    marked = collections.Counter(m.get("complaint") for m in marks or [] if isinstance(m, dict))
    out += [f"reviewer {who}: own prior complaint {c} left unmarked" for c in owned if marked[c] == 0]
    out += [f"reviewer {who}: complaint {c!r} is marked but is not this reviewer's prior complaint" for c in marked if c not in owned]
    for m in marks or []:
        if not isinstance(m, dict):
            continue
        if m.get("status") not in MARKS or not text(m.get("reason")):
            out.append(f"reviewer {who}: mark of {m.get('complaint')!r} needs a status of {', '.join(MARKS)} and a reason")
        elif m["status"] == "deferred" and not release_id(m.get("release")):
            out.append(f"reviewer {who}: deferral of {m.get('complaint')!r} names no release")
    prior_ids = {c for ids in prior_owned(prior).values() for c in ids}
    out += [f"reviewer {who}: new complaint {c['id']!r} reuses a prior complaint id"
            for c in w.get("complaints", []) if isinstance(c, dict) and c.get("id") in prior_ids]
    return out


def diversity_problems(reviewers, diversity):
    mode = (diversity or {}).get("mode")
    models = {r.get("model") for r in reviewers}
    out = []
    if len({r.get("persona") for r in reviewers}) < len(reviewers):
        out.append("two reviewers share a persona")
    if mode not in ("multi-model", "single-model"):
        out.append("diversity.mode is not declared as multi-model or single-model")
    elif mode == "multi-model" and len(models) < 2:
        out.append("diversity.mode multi-model, but the reviewers share one model")
    elif mode == "single-model" and len(models) > 1:
        out.append(f"diversity.mode single-model, but the reviewers use {len(models)} models")
    return out


def structure_problems(report, folder, walk_list, deferred_ids, prior):
    """Refusals both tiers share: schema, walk, smoke, reviewers, stories, consolidation."""
    out = []
    if report.get("schema") != WIRE:
        out.append(f"schema {report.get('schema')!r} is not {WIRE}")
    out += [f"unknown top-level key {k!r}" for k in report if k not in {n for n, _ in FIELDS}]
    walk_ids = [s["id"] for s in walk_list["stories"]]
    if report.get("walk") != {"journey": walk_list["journey"], "release": walk_list["release"]["id"],
                              "source_commit": (walk_list.get("source") or {}).get("commit")}:
        out.append("walk does not match walk.json (journey, release, source_commit)")
    target = report.get("target")
    if not isinstance(target, dict) or not (text(target.get("environment")) and text(target.get("ref"))):
        out.append("target needs a non-empty environment and ref")
    smoke = report.get("smoke")
    if not isinstance(smoke, dict):
        out.append("smoke is absent")
    else:
        if smoke.get("result") != "passed":
            out.append(f"smoke.result is {smoke.get('result')!r}, not passed; reviewers start only after a passed smoke")
        if not text(smoke.get("check")):
            out.append("smoke.check is empty")
        if not smoke.get("evidence"):
            out.append("smoke has no evidence")
        out += evidence_problems(folder, "smoke", smoke.get("evidence"))
    walks = report.get("walks") if isinstance(report.get("walks"), list) else []
    if not walks:
        out.append("no reviewer walks")
    out += walk_problems(walks, walk_ids, folder, deferred_ids, prior)
    returned = {w["reviewer"].get("id") for w in walks if isinstance(w.get("reviewer"), dict)}
    out += [f"prior reviewer {who} is absent from the re-walk, so their complaints are unmarked"
            for who in prior_owned(prior) if prior is not None and who not in returned]
    reviewers = [w.get("reviewer") for w in walks if isinstance(w.get("reviewer"), dict)]
    if report.get("reviewers") != reviewers:
        out.append("reviewers[] does not match the reviewers of walks[]")
    ids = collections.Counter(r.get("id") for r in reviewers)
    out += [f"reviewer id {i!r} appears {n} times" for i, n in ids.items() if n > 1]
    out += diversity_problems(reviewers, report.get("diversity"))
    count = sum(operated(w) for w in walks)
    if count < 2:
        out.append(f"fewer than two reviewers operated the product (reviewers who did: {count})")
    rows = report.get("stories") if isinstance(report.get("stories"), list) else []
    counts = collections.Counter(r.get("id") for r in rows if isinstance(r, dict))
    out += [f"stories[]: walk story {s} missing" for s in walk_ids if counts[s] == 0]
    out += [f"stories[]: walk story {s} duplicated" for s in walk_ids if counts[s] > 1]
    out += [f"stories[]: story {s} is not on the walk" for s in counts if s not in walk_ids]
    bad = {r.get("id") for r in rows if isinstance(r, dict) and r.get("result") not in SEVERITY}
    out += [f"stories[]: story {s} result is not one of {', '.join(SEVERITY)}" for s in sorted(map(str, bad))]
    if not out and [(r["id"], r["result"], r["reported_by"]) for r in rows] != \
            [(r["id"], r["result"], r["reported_by"]) for r in consolidate(walks, walk_ids)]:
        out.append("stories[].result differs from the most severe result across walks")
    if report.get("proof_line") is None or (not out and report["proof_line"].get("result") != consolidate_proof(walks)["result"]):
        out.append("proof_line is absent or differs from the most severe proof line across walks")
    return out


def director_model(workflow_dir, journey, release):
    """(model, reasons, notes): opus when any task of the release ran its ideation on opus, else sonnet."""
    reasons, notes = [], []
    for task in release_tasks(workflow_dir, journey, release):
        opus, note = ideation_model(task)
        if opus:
            reasons.append(f"design-opus:{task.slug}")
        elif note:
            notes.append(note)
    return ("opus" if reasons else "sonnet"), reasons, notes


def ruling_problems(report, workflow_dir, journey, release, deferred_ids, prior):
    out, ruling = [], report.get("ruling")
    if not isinstance(ruling, dict):
        return ["ruling is absent"]
    walks = report["walks"]
    walk_ids = {r["id"] for r in report.get("stories", [])}
    complaints = {c["id"] for w in walks for c in w.get("complaints", [])}
    items = [i for i in ruling.get("items", []) if isinstance(i, dict)]
    covered = {c for i in items for c in i.get("from", []) if isinstance(i.get("from"), list)}
    out += [f"complaint {c} is in no ruling item's from" for c in sorted(complaints - covered)]
    entries = items + [d for d in ruling.get("deferred", []) if isinstance(d, dict)]
    for e in entries:
        tag = f"ruling {e.get('id') or e.get('item')}"
        if e in items:
            if not isinstance(e.get("from"), list) or not e["from"] or set(e["from"]) - complaints - set(prior_complaints(prior)):
                out.append(f"{tag}: from names no complaint, or one that does not exist")
            if not strings(e.get("stories")) or set(e["stories"]) - walk_ids:
                out.append(f"{tag}: stories names a story that is not on the walk")
            if e.get("class") not in CLASSES:
                out.append(f"{tag}: class is not one of {', '.join(CLASSES)}")
            if e.get("real") not in REAL:
                out.append(f"{tag}: real is not one of {', '.join(REAL)}")
        if e.get("ruling") not in RULINGS:
            out.append(f"{tag}: ruling is not one of {', '.join(RULINGS)}")
        if e.get("when") and e["when"] not in WHEN:
            out.append(f"{tag}: when is not one of {', '.join(WHEN)}")
        if e.get("real") == "unverified" and e.get("ruling") != "decision":
            out.append(f"{tag}: real unverified must be ruled decision")
        if (e.get("real") == "no" or e.get("ruling") == "do-not-solve") and not text(e.get("why")):
            out.append(f"{tag}: real no or do-not-solve needs a why")
        if e.get("ruling") == "solve" and not (text(e.get("how")) and text(e.get("when"))):
            out.append(f"{tag}: solve needs a how and a when")
        if e.get("ruling") == "solve" and e.get("when") in ("next-release", "later") and not release_id(e.get("release")):
            out.append(f"{tag}: deferral names no release id (when {e['when']} needs release, one word)")
    ruled = {d.get("item") for d in ruling.get("deferred", []) if isinstance(d, dict)}
    out += [f"deferred item {i} has no director ruling" for i in deferred_ids if i not in ruled]
    out += [f"ruling names deferred item {i}, which is not a deferred item of the release" for i in sorted(map(str, ruled)) if i not in deferred_ids]
    tasks = [t for t in ruling.get("tasks", []) if isinstance(t, dict)]
    if len(tasks) > MAX_TASKS:
        out.append(f"{len(tasks)} backlog tasks proposed, at most {MAX_TASKS}")
    out += [f"task {t.get('title')!r} has no from_items" for t in tasks if not t.get("from_items")]
    ids = {e.get("id") or e.get("item") for e in entries}
    out += [f"task {t.get('title')!r} names unknown item {i}" for t in tasks for i in t.get("from_items", []) if i not in ids]
    filed = complaint_links(workflow_dir, journey, release)
    in_task = {i for t in tasks for i in t.get("from_items", [])}
    out += [f"ruling {e.get('id') or e.get('item')}: solve this-round is covered by no task's from_items and no filed task"
            for e in entries if solves_this_round(e) and (e.get("id") or e.get("item")) not in in_task
            and not any(filed.get(c) for c in e.get("from", []) if isinstance(e.get("from"), list))]
    model = director_model(workflow_dir, journey, release)[0]
    declared = (ruling.get("director") or {}).get("model")
    if declared != model:
        out.append(f"ruling.director.model is {declared!r} but the walk covers tasks that call for {model} (see director-model)")
    return out


def prior_complaints(prior):
    return [c for ids in prior_owned(prior).values() for c in ids]


def derive_status(item):
    ruling, when = item.get("ruling"), item.get("when")
    if ruling == "decision":
        return "decision", item.get("why", "")
    if ruling == "do-not-solve" or when == "never":
        return "will-not-fix", item.get("why", "")
    if when in ("next-release", "later"):
        return f"deferred:{item.get('release', '')}", item.get("how") or item.get("why", "")
    return "to-fix", item.get("how") or item.get("why", "")


def expected_rows(report, prior):
    """(complaint, reviewer, status, reason, planned task) for every complaint of this walk and, on a re-walk, the prior one."""
    ruling = report.get("ruling", {})
    rows = []
    for w in report["walks"]:
        who = w["reviewer"]["id"]
        for c in w.get("complaints", []):
            item = next((i for i in ruling.get("items", []) if c["id"] in i.get("from", [])), {})
            task = next((t.get("title", "") for t in ruling.get("tasks", []) if item.get("id") in t.get("from_items", [])), "none")
            status, reason = derive_status(item)
            rows.append((c["id"], who, status, reason, task))
    if prior:
        planned = {r["complaint"]: r["task"] for r in prior.get("complaint_rows", [])}
        for w in report["walks"]:
            for m in w.get("marks", []):
                status = f"deferred:{m.get('release', '')}" if m.get("status") == "deferred" else m.get("status")
                rows.append((m["complaint"], w["reviewer"]["id"], status, m.get("reason", ""), planned.get(m["complaint"], "none")))
    return rows


def row_problems(report, prior):
    rows = report.get("complaint_rows")
    if not isinstance(rows, list):
        return ["complaint_rows is absent"]
    out = []
    for r in rows:
        if not isinstance(r, dict) or not ROW_STATUS.match(str(r.get("status"))) or not text(r.get("reason")) or not text(r.get("task")):
            out.append(f"complaint_rows: row {r.get('complaint') if isinstance(r, dict) else r!r} needs a task, a status and a reason")
    want = {(c, who, status, reason) for c, who, status, reason, _ in expected_rows(report, prior)}
    have = {(r.get("complaint"), r.get("reviewer"), r.get("status"), r.get("reason")) for r in rows if isinstance(r, dict)}
    if len(rows) != len(want) or have != want:
        out.append("complaint_rows is not one row per reviewer complaint with the status and reason the ruling or the reviewer's mark gives")
    return out


def solves_this_round(entry):
    return entry.get("real", "yes") == "yes" and entry.get("ruling") == "solve" and entry.get("when") == "this-round"


def is_clean(report):
    ruling = report.get("ruling", {})
    return (all(r["result"] == "works" for r in report["stories"]) and report["proof_line"]["result"] == "works"
            and report["smoke"].get("result") == "passed"
            and not any(m.get("status") == "partly-fixed" for w in report["walks"] for m in w.get("marks", []))
            and not any(solves_this_round(e) for e in ruling.get("items", []) + ruling.get("deferred", [])))


def loaded(folder):
    folder = Path(folder)
    walk_dir = folder / "walk"
    if not walk_dir.is_dir():
        raise Refused(f"{walk_dir} is not a directory")
    walk_list = read_json(walk_dir / "walk.json")
    if walk_list.get("schema") != WALK_WIRE:
        raise Refused(f"walk.json schema {walk_list.get('schema')!r} is not {WALK_WIRE}")
    return walk_dir, walk_list


def assemble(folder, walk_list):
    walk_dir = Path(folder) / "walk"
    meta = read_json(walk_dir / "meta.json") if (walk_dir / "meta.json").is_file() else {}
    smoke = read_json(walk_dir / "smoke.json") if (walk_dir / "smoke.json").is_file() else None
    walks = [read_json(p) for p in sorted(walk_dir.glob("reviewer-*.json"))]
    reviewers = [w.get("reviewer") for w in walks if isinstance(w.get("reviewer"), dict)]
    report = {
        "schema": WIRE,
        "walk": {"journey": walk_list["journey"], "release": walk_list["release"]["id"],
                 "source_commit": (walk_list.get("source") or {}).get("commit")},
        "target": meta.get("target", {}),
        "smoke": smoke,
        "diversity": {"mode": (meta.get("diversity") or {}).get("mode"), "reviewers": len(reviewers),
                      "models": len({r.get("model") for r in reviewers})},
        "reviewers": reviewers,
        "stories": [], "proof_line": None, "walks": walks,
        "not_tested": meta.get("not_tested", []), "data_left": meta.get("data_left", []),
    }
    if smoke is None:
        del report["smoke"]
    ids = [s["id"] for s in walk_list["stories"]]
    report["stories"] = consolidate(walks, ids)
    report["proof_line"] = consolidate_proof(walks)
    return report


def prior_of(path):
    if path is None:
        return None, None
    prior = read_json(path)
    return prior, digest_of(path)


def print_environment(report):
    for r in report.get("stories", []):
        if r.get("result") == "not-reachable" and text(r.get("cause")):
            print(f"Captain decision: environment ({r['cause']})")


def print_routes(report, workflow_dir, journey, release):
    owners = owners_by_story(workflow_dir, journey, release)
    for item in report.get("ruling", {}).get("items", []):
        stories = item.get("stories", [])
        if not stories:
            print(f"route {item.get('id')}: bug task, no story")
            continue
        slugs = sorted({t.slug for s in stories for t in owners.get(s, [])})
        print(f"route {item.get('id')}: {slugs[0]}" if len(slugs) == 1 else f"route {item.get('id')}: review-release")


def cmd_check(args):
    try:
        folder = Path(args.folder)
        _, walk_list = loaded(folder)
        journey, release = walk_list["journey"], walk_list["release"]["id"]
        prior, prior_digest = prior_of(args.prior)
        if args.tier == "final":
            report = read_json(folder / "walk" / "report.json")
        else:
            report = assemble(folder, walk_list)
        deferred_ids = [i for i, _ in deferred_items(args.workflow_dir, journey, release)]
    except (Refused, KeyError, OSError) as error:
        print(f"REFUSED: {error}")
        print("clean: no")
        return 1
    try:
        problems = structure_problems(report, folder, walk_list, deferred_ids, prior)
        recorded = (report.get("prior") or {}).get("digest")
        if prior is None and recorded:
            problems.append("the report records a prior digest but no --prior report was given")
        elif prior is not None and args.tier == "final" and recorded != prior_digest:
            problems.append("the prior report's digest does not match the digest the report records")
        if args.tier == "final" and not problems:
            problems += ruling_problems(report, args.workflow_dir, journey, release, deferred_ids, prior)
            problems += row_problems(report, prior)
    except (KeyError, TypeError, AttributeError) as error:
        problems = [f"malformed report: {type(error).__name__} {error}"]
    for p in problems:
        print(f"REFUSED: {p}")
    if problems:
        print_environment(report)
        print("clean: no")
        return 1
    print(f"reviewers: {len(report['reviewers'])} (models: {len({r['model'] for r in report['reviewers']})})")
    if report["diversity"]["mode"] == "single-model":
        print("model consensus is not independent")
    print(f"tier {args.tier}: ok")
    print_environment(report)
    if args.tier == "final":
        print_routes(report, args.workflow_dir, journey, release)
        print(f"clean: {'yes' if is_clean(report) else 'no'}")
    return 0


def cmd_deferred(args):
    journey, _, release = args.release.partition("/")
    if not release:
        print("usage: deferred JOURNEY/RELEASE", file=sys.stderr)
        return 2
    items = deferred_items(args.workflow_dir, journey, release)
    for item_id, line in items:
        print(f"{item_id}: {line}")
    if not items:
        print("deferred: none")
    return 0


def read_ruling(path):
    ruling = read_json(path)
    if not isinstance(ruling, dict):
        raise Refused(f"{Path(path).name} is not an object")
    return ruling.get("release_ruling", ruling)


def cmd_director_model(args):
    try:
        _, walk_list = loaded(Path(args.folder))
        model, reasons, notes = director_model(args.workflow_dir, walk_list["journey"], walk_list["release"]["id"])
    except (Refused, KeyError, OSError) as error:
        print(f"REFUSED: {error}")
        return 1
    for note in notes:
        print(note)
    print(f"director model: {model}" + (f" ({', '.join(reasons)})" if reasons else ""))
    return 0


def cmd_build(args):
    try:
        folder = Path(args.folder)
        walk_dir, walk_list = loaded(folder)
        journey, release = walk_list["journey"], walk_list["release"]["id"]
        prior, prior_digest = prior_of(args.prior)
        report = assemble(folder, walk_list)
        deferred_ids = [i for i, _ in deferred_items(args.workflow_dir, journey, release)]
        problems = structure_problems(report, folder, walk_list, deferred_ids, prior)
        if problems:
            raise Refused("; ".join(problems))
        ruling = read_ruling(walk_dir / "ruling.json")
        meta = read_json(walk_dir / "meta.json") if (walk_dir / "meta.json").is_file() else {}
        report["ruling"] = {"director": {"agent": "kc-dev-flow-2:design-director", "model": meta.get("director_model")},
                            "items": ruling.get("items", []), "deferred": ruling.get("deferred", []), "tasks": ruling.get("tasks", [])}
        if prior is not None:
            report["prior"] = {"digest": prior_digest}
        rows = expected_rows(report, prior)
        links = complaint_links(args.workflow_dir, journey, release)
        report["complaint_rows"] = [
            {"complaint": c, "reviewer": who, "task": ", ".join(links[c]) if links.get(c) else task, "status": status, "reason": reason}
            for c, who, status, reason, task in rows]
    except (Refused, KeyError, OSError, TypeError, AttributeError) as error:
        print(f"REFUSED: {error}")
        return 1
    order = [n for n, _ in FIELDS]
    ordered = {k: report[k] for k in order if k in report}
    target = walk_dir / "report.json"
    target.write_text(json.dumps(ordered, indent=2) + "\n")
    print(f"report: {target}")
    print(f"digest: {digest_of(target)}")
    return 0


def cell(value):
    return re.sub(r"\s+", " ", str(value)).replace("|", "\\|").strip()


def table(head, rows):
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(cell(c) for c in row) + " |" for row in rows]
    return lines


def render_text(report, digest):
    ruling = report.get("ruling", {})
    walk = report["walk"]
    out = [f"# Release walk: {walk['journey']}/{walk['release']}", "", "## Complaints", ""]
    out += table(["complaint", "reviewer", "task", "status", "reason"],
                 [[r["complaint"], r["reviewer"], r["task"], r["status"], r["reason"]] for r in report["complaint_rows"]])
    if report.get("prior"):
        out += ["", f"Re-walk of the walk whose report digest is {report['prior']['digest']}."]
    d = report["diversity"]
    out += ["", "## Summary", "",
            f"- reviewers: {d['reviewers']} (models: {d['models']}); mode: {d['mode']}",
            f"- smoke: {report['smoke']['result']}; proof line: {report['proof_line']['result']}",
            f"- clean: {'yes' if is_clean(report) else 'no'}", "", "## Stories", ""]
    out += table(["story", "result", "reported by", "entry", "cause"],
                 [[s["id"], s["result"], ", ".join(s["reported_by"]), s["entry"], s["cause"]] for s in report["stories"]])
    out += ["", "## Ruling", ""]
    out += [f"Director model: {ruling.get('director', {}).get('model')}", ""]
    out += table(["item", "from", "stories", "real", "ruling", "when", "class", "why"],
                 [[i.get("id"), ", ".join(i.get("from", [])), ", ".join(i.get("stories", [])), i.get("real"), i.get("ruling"),
                   (i.get("when") or "") + (f" ({i['release']})" if i.get("release") else ""), i.get("class"),
                   i.get("why", "")] for i in ruling.get("items", [])])
    out += ["", "## Deferred findings", ""]
    out += table(["item", "ruling", "when", "how"],
                 [[e.get("item"), e.get("ruling"), (e.get("when") or "") + (f" ({e['release']})" if e.get("release") else ""),
                   e.get("how", "")] for e in ruling.get("deferred", [])])
    out += ["", "## Proposed backlog tasks", ""]
    out += table(["title", "scope", "after", "from items"],
                 [[t.get("title"), t.get("scope"), ", ".join(t.get("after", [])), ", ".join(t.get("from_items", []))] for t in ruling.get("tasks", [])])
    out += ["", "## Not tested", ""] + [f"- {cell(n)}" for n in report.get("not_tested", [])]
    out += ["", "## Data left", ""] + [f"- {cell(n)}" for n in report.get("data_left", [])]
    out += ["", f"Report digest: {digest}", ""]
    return "\n".join(out)


def cmd_render(args):
    try:
        path = Path(args.folder) / "walk" / "report.json"
        fresh = render_text(read_json(path), digest_of(path))
    except (Refused, KeyError, OSError, TypeError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1
    if args.check:
        record = Path(args.folder) / "walk" / "record.md"
        if not record.is_file() or record.read_text() != fresh:
            print("REFUSED: walk/record.md differs from a fresh render of report.json")
            return 1
        print("record.md equals a fresh render")
        return 0
    sys.stdout.write(fresh)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("schema")
    p.add_argument("name")
    p.set_defaults(run=cmd_schema)
    p = sub.add_parser("deferred")
    p.add_argument("release")
    p.add_argument("--workflow-dir", required=True)
    p.set_defaults(run=cmd_deferred)
    p = sub.add_parser("check")
    p.add_argument("folder")
    p.add_argument("--tier", choices=("walk", "final"), required=True)
    p.add_argument("--workflow-dir", required=True)
    p.add_argument("--prior")
    p.set_defaults(run=cmd_check)
    p = sub.add_parser("director-model")
    p.add_argument("folder")
    p.add_argument("--workflow-dir", required=True)
    p.set_defaults(run=cmd_director_model)
    p = sub.add_parser("build")
    p.add_argument("folder")
    p.add_argument("--workflow-dir", required=True)
    p.add_argument("--prior")
    p.set_defaults(run=cmd_build)
    p = sub.add_parser("render")
    p.add_argument("folder")
    p.add_argument("--check", action="store_true")
    p.set_defaults(run=cmd_render)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
