#!/usr/bin/env python3
"""Throwaway proof of concept: check the facts in a question FO puts to the Captain.

state  -- each task a question offers as waiting work is read at a state commit;
          a task whose latest Captain ruling is hold/reject/close, or that is
          archived, is flagged.  Deterministic.
effect -- each accepted-limit sentence of a merge ask is compared, by one bounded
          model call, with record lines this script extracts from the task at a
          state commit; a CONTRADICTED verdict counts only when its quoted record
          line is found verbatim in the extract.
"""
import argparse
import json
import re
import subprocess
import sys
import time

import yaml

STOP_DECISIONS = {"hold", "reject", "rejected", "close", "closed"}


def show(state, sha, path):
    r = subprocess.run(["git", "-C", state, "show", f"{sha}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def ls(state, sha, prefix):
    r = subprocess.run(["git", "-C", state, "ls-tree", "-r", "--name-only", sha, prefix],
                       capture_output=True, text=True)
    return r.stdout.split()


def front(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def rulings(fm):
    out = []
    for rec in ((fm.get("gates") or {}).get("records") or []):
        for att in rec.get("attempts") or []:
            res = att.get("resolution")
            if res:
                out.append((str(res.get("at")), rec.get("stage"), str(res.get("decision")), str(res.get("reason", ""))[:160]))
    return sorted(out)


def state_check(args):
    q = json.load(open(args.question))
    sha = q["state_commit_before_ask"]
    flagged = 0
    rows = []
    for slug in q["claims"]["tasks"]:
        live = show(args.state, sha, f"{slug}.md")
        archived = live is None and show(args.state, sha, f"_archive/{slug}.md") is not None
        text = live or show(args.state, sha, f"_archive/{slug}.md") or ""
        fm = front(text) if text else {}
        rs = rulings(fm)
        last = rs[-1] if rs else None
        stop = archived or (last is not None and last[2] in STOP_DECISIONS)
        flagged += bool(stop)
        rows.append({"task": slug, "status": fm.get("status"), "archived": archived,
                     "latest_ruling": last and {"at": last[0], "stage": last[1], "decision": last[2]},
                     "flag": bool(stop)})
        mark = "FLAG" if stop else "ok"
        why = "archived" if archived else (f"{last[2]} at {last[1]} {last[0][:10]}" if last else "no ruling")
        print(f"{mark} {slug}: status {fm.get('status')}, latest ruling {why}")
    print(f"{q['name']}: asserts {q['claims']['asserts']!r}; {flagged} of {len(rows)} tasks flagged at state {sha[:9]}")
    if args.json:
        json.dump({"question": q["name"], "state": sha, "rows": rows, "flagged": flagged}, open(args.json, "w"), indent=1)
    return 1 if flagged else 0


def record_lines(state, sha, slug):
    """Lines a merge ask's limits must agree with: criteria, findings, deferred risks, the ask record,
    and the head of each saved json/log file those lines name."""
    task = show(state, sha, f"{slug}.md") or ""
    lines = []
    for line in task.splitlines():
        s = line.strip()
        if re.match(r"^\*\*AC-\d+\*\*", s) or re.match(r"^- F\d+ ", s) or re.search(r"Deferred risk|Known limit|Limit:", s):
            lines.append(s[:900])
    asks = sorted(p for p in ls(state, sha, f"{slug}/merge/") if re.search(r"ask-\d+\.json$", p))
    if asks:
        rec = json.loads(show(state, sha, asks[-1]))
        lines += [f"ask sufficiency: {rec.get('sufficiency')}", f"ask necessity: {rec.get('necessity')}"]
        lines += [f"ask {p}" for p in rec.get("points", [])]
    cited = []
    for line in list(lines):
        for name in re.findall(r"[\w./-]+\.(?:json|log)", line):
            path = name if name.startswith(slug) else f"{slug}/{name}"
            body = show(state, sha, path)
            if body and path not in cited:
                cited.append(path)
                lines.append(f"saved {path}: " + " ".join(body.split())[:700])
    return lines


def limits(question):
    m = re.search(r"同意即接受[^：:]*[：:](.*?)(?:Squash merge|$)", question, re.S)
    body = m.group(1) if m else ""
    parts = re.split(r"[；;]|(?:[一二三四五六七八九十]、)|。", body)
    return [p.strip(" ，,") for p in parts if len(p.strip()) > 6]


PROMPT = """You compare one sentence a First Officer wrote to its Captain (in Chinese) with record lines
from the task's own files (in English). Decide only from the record lines below.

Sentence: {sentence}

Record lines:
{record}

Answer with exactly one JSON object and nothing else:
{{"verdict": "CONTRADICTED" | "SUPPORTED" | "NOT_FOUND", "quote": "<the one record line, copied verbatim, that decides it; empty for NOT_FOUND>", "why": "<one short sentence>"}}
CONTRADICTED means a record line says something incompatible with the sentence, including a
sentence that narrows or excludes a case the record says is affected."""


def ask_model(model, sentence, record):
    prompt = PROMPT.format(sentence=sentence, record="\n".join(f"- {r}" for r in record))
    t0 = time.time()
    r = subprocess.run(["claude", "-p", "--model", model, "--tools", "", "--setting-sources", "",
                        "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence",
                        "--output-format", "json"], input=prompt, capture_output=True, text=True, cwd="/tmp")
    secs = round(time.time() - t0, 1)
    o = json.loads(r.stdout)
    u = o.get("usage", {})
    tokens = sum(u.get(k, 0) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    raw = o.get("result", "")
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        v = json.loads(m.group(0)) if m else {}
    except ValueError:
        v = {}
    return v, raw, secs, tokens, u.get("output_tokens", 0)


def effect_check(args):
    q = json.load(open(args.question))
    sha = q["state_commit_before_ask"]
    record = record_lines(args.state, sha, q["task"])
    joined = "\n".join(record)
    out = {"question": q["name"], "state": sha, "record_lines": len(record), "record_chars": len(joined), "runs": []}
    print(f"{q['name']}: {len(record)} record lines ({len(joined)} chars) at state {sha[:9]}")
    flagged_any = False
    for run in range(args.runs):
        for i, sentence in enumerate(limits(q["question"]), 1):
            v, raw, secs, tin, tout = ask_model(args.model, sentence, record)
            quote = (v.get("quote") or "").strip()
            verbatim = bool(quote) and quote.lstrip("- ") in joined
            flag = v.get("verdict") == "CONTRADICTED" and verbatim
            flagged_any |= flag
            out["runs"].append({"run": run + 1, "sentence_no": i, "sentence": sentence, "verdict": v.get("verdict"),
                                "quote_verbatim": verbatim, "flag": flag, "quote": quote[:300], "why": v.get("why"),
                                "seconds": secs, "input_tokens": tin, "output_tokens": tout, "raw": raw[:1200]})
            print(f"run {run + 1} s{i} {'FLAG' if flag else 'ok  '} {v.get('verdict')} verbatim={verbatim} {secs}s {tin}+{tout}tok | {sentence[:60]}")
    if args.json:
        json.dump(out, open(args.json, "w"), ensure_ascii=False, indent=1)
    if args.record_out:
        open(args.record_out, "w").write(joined + "\n")
    return 1 if flagged_any else 0


EXISTING = re.compile(r"舊任務|舊設計|舊的|已經開好|已開好|已開的|既有|已經過了|過了設計關卡|已核准的|進行中的|"
                      r"\balready[- ]filed\b|\bexisting\b|\bfiled before\b|\bpast (?:ideation|the gate)\b", re.I)
EFFECT = re.compile(r"不會|不再|只有|只會|只在|擋|要求|補寫|補標|不受|影響|\brefus|\bblock|\bnot\b|\bonly\b", re.I)
CITED = re.compile(r"[\w./-]+\.(?:json|log|txt|jsonl)\b")


def sentences(text):
    text = re.split(r"Squash merge", text)[0]
    return [s.strip(" ，,") for s in re.split(r"[。；;？?]|(?:[一二三四五六七八九十]、)", text) if len(s.strip()) > 6]


MARKED = re.compile(r"未驗證|未對過紀錄|\bunverified\b", re.I)


def scope_flags(text, exists=None):
    out = []
    for s in sentences(text):
        if EXISTING.search(s) and EFFECT.search(s):
            cited = [c for c in CITED.findall(s) if exists is None or exists(c)]
            marked = bool(MARKED.search(s))
            out.append({"sentence": s, "cited": cited, "marked": marked, "flag": not cited and not marked})
    return out


def scope_check(args):
    if args.question.endswith(".jsonl"):
        items = [json.loads(line) for line in open(args.question)]
    else:
        items = [json.load(open(args.question))]
    total = flagged_q = 0
    report = []
    for q in items:
        exists = None
        if args.state and q.get("task") and q.get("state_commit_before_ask"):
            def exists(c, q=q):
                path = c if c.startswith(q["task"] + "/") else f"{q['task']}/{c}"
                return show(args.state, q["state_commit_before_ask"], path) is not None
        rows = scope_flags(q["question"], exists)
        n = sum(r["flag"] for r in rows)
        total += len(sentences(q["question"]))
        flagged_q += bool(n)
        report.append({"name": q.get("name"), "asked_at": q.get("asked_at"), "rows": rows})
        for r in rows:
            print(f"{'FLAG' if r['flag'] else 'ok  '} {q.get('name') or q.get('asked_at')} | {r['sentence'][:90]}")
    print(f"scope: {len(items)} questions, {total} sentences, "
          f"{sum(len(r['rows']) for r in report)} existing-item sentences, {flagged_q} questions flagged")
    if args.json:
        json.dump(report, open(args.json, "w"), ensure_ascii=False, indent=1)
    return 1 if flagged_q else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("state", "effect", "scope"):
        p = sub.add_parser(name)
        p.add_argument("--state", required=name != "scope", help="state checkout (git) holding the task files")
        p.add_argument("--question", required=True, help="question fixture json")
        p.add_argument("--json", help="write the result here")
        if name == "effect":
            p.add_argument("--model", default="haiku")
            p.add_argument("--runs", type=int, default=1)
            p.add_argument("--record-out")
    a = ap.parse_args()
    return {"state": state_check, "effect": effect_check, "scope": scope_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
