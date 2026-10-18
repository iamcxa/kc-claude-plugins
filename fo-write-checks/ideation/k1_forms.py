"""Score three candidate forms for a declined item against the observer's per-task verdict on the decline rule.
Items: text after `Declined...:` / `FO declines...:` in a validation briefing's question and artifact summaries, split on ';' outside brackets.
Usage: python3 -I k1_forms.py <state checkout>"""
import glob, json, re, sys
S = sys.argv[1]
START = re.compile(r"(?:\bDeclined\b[^:\n]{0,60}:|\bFO declines\b[^:\n]{0,60}:)")
END = re.compile(r"(?<=[.)])\s+(?=(?:Second reviewer|Precedent|Limits?|Not verified|Files outside|Words FO reads|External rounds|RoboRev|Codex|Prod design|Outside the brief|Deferred risk carried|D2 cost|Change to|Declined findings)\b[^.]{0,40}:)|\n\n")
def items(text):
    out = []
    for m in START.finditer(text):
        rest = text[m.end():]
        e = END.search(rest)
        seg = (rest[:e.start()] if e else rest).strip().rstrip(".")
        depth, cur = 0, ""
        for ch in seg:
            depth += (ch in "([") - (ch in ")]")
            depth = max(depth, 0)
            if ch == ";" and depth == 0:
                out.append(cur.strip())
                cur = ""
            else:
                cur += ch
        out.append(cur.strip())
    return [i for i in out if len(i.split()) >= 3]
PAREN = re.compile(r"\(([^()]*)\)")
bracket = lambda it: any(len(p.split()) >= 2 for p in PAREN.findall(it))
forms = {
    "A: reason in brackets (2+ words)": bracket,
    "B: brackets, or after because/since": lambda it: bracket(it) or re.search(r"\b(?:because|since)\b", it, re.I) is not None,
    "C: dash form '<finding> — <reason>'": lambda it: " — " in it,
}
VIOLATION = {"amendment-form-check", "fo-lifecycle-mod", "special-role-triggers", "ui-design-review-in-ideation", "workflow-budget-ratchet", "merge-gatekeeper"}
OK = {"names-check-before-dispatch", "prod-security-validation-gate", "worker-loads-declared-package"}
per = {}
for f in sorted(glob.glob(S + "/**/review/validation/briefing-*/index.json", recursive=True)):
    slug = f.split("/review/")[0].replace(S + "/", "").replace("_archive/", "")
    if slug in VIOLATION | OK:
        d = json.load(open(f))
        its = items(d.get("question", "") + "\n" + "\n".join(a.get("summary", "") for a in d.get("artifacts", [])))
        per[slug] = {n: [i for i in its if not fn(i)] for n, fn in forms.items()}
        per[slug]["items"] = len(its)
total = sum(v["items"] for v in per.values())
for n in forms:
    hit = sorted(s for s in VIOLATION if per.get(s, {}).get(n))
    over = sorted(s for s in OK if per.get(s, {}).get(n))
    print(f"{n}: flags {len(hit)} of {len(VIOLATION)} observer-violation tasks, {len(over)} of {len(OK)} observer-ok tasks; "
          f"items flagged {sum(len(per[s][n]) for s in VIOLATION)} in violation tasks, {sum(len(per[s][n]) for s in OK)} in ok tasks, of {total}")
    for s in over:
        for i in per[s][n]:
            print("   over-flag:", s, "|", i[:100])
