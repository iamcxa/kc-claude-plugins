#!/usr/bin/env python3
"""Words FO reads at each lifecycle moment, base (origin/main ad44f0cb, 0.26.0) and candidate, counted with str.split().

Usage: python3 -I -B words.py workflow-0.26.0.md mod-0.26.0.md
The two inputs are the base sources, written by
  git -C <kc-claude-plugins> show ad44f0cb:kc-dev-flow-2/references/sd/workflow.md > workflow-0.26.0.md
  git -C <kc-claude-plugins> show ad44f0cb:kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md > mod-0.26.0.md
The candidate README is the base with one sentence edit (E1 below) applied in memory; script output lines are the
strings proto_gate.py and proto_scope.py print (cycle 3: the rule-4 half is two lines only), typed here so the count is reproducible. A moment's number is every passage and every script output
that instructs a step due then.
"""
import re, sys
text = open(sys.argv[1]).read()
mod = open(sys.argv[2]).read()
w = lambda s: len(s.split())

E1 = ("whether at a gate approval,\nduring implementation or at a validation gate, is an amendment.",
      "whether at a gate approval,\nbetween gates or at a validation gate, is an amendment.")
new = text
for old, rep in (E1,):
    assert old in new, old[:40]
    new = new.replace(old, rep)


def between(t, start, end):
    a = t.index(start)
    return t[a:t.index(end, a) + len(end)]


def passages(t):
    return {
        "ideation Gate content": between(t, "- **Gate content:** Present PRFAQ/Mermaid", "without inventing same-stage rework. Corrections neither replace user approval nor advance stages."),
        "validation Gate content": between(t, "- **Gate content:** Show actual checks", "delivering that work as POC."),
        "Delivery authority": between(t, "Project and Captain authority constrain", "explicit choice."),
        "delivery_gate sentence": between(t, "Before merging or asking, FO runs", "shows the Captain what it printed."),
        "Captain amendments, first sentence": between(t, "A change the Captain makes to what he has accepted", "is an amendment."),
    }


base_p, new_p = passages(text), passages(new)
BASE_PASS = ["PR head 40c714a6 equals dispatched candidate 40c714a6; no second reviewer outcome is missing", "class: never",
             "record: task/merge/ask-1.json",
             "next: merge this head if the approved question named the merge and he did not say he merges or holds, else ask for merge with this text."]
ASK_SENTENCE = "Every other PR, the Release PR included, is asked one at a time."
ASK_NEW = BASE_PASS[-1] + " " + ASK_SENTENCE
NEW_PASS = {
    "pass output, class never (saved verdict ask)": BASE_PASS[:1] + ["class: never (verdict ask)", BASE_PASS[2], ASK_NEW],
    "pass output, saved verdict merge": BASE_PASS[:1] + ["class: docs-only", BASE_PASS[2], ASK_NEW],
}
HOLDS = {
    "R2 findings join": "declined items (3) are fewer than the validation report's Deferred risk and Polish findings (5): add a declined item for each, naming the fix as its reason when FO fixed it, then run this check again.",
    "R1 follow-ups claim": "chat-only-followups.md claims the Captain's acceptance in its title or first paragraph (\"accepted\") before the gate that records it: say what FO declined and cite no ruling.",
    "R3 scope": "Scope changed after the newest amendment (cfa03ada): \"- Captain asked for one more thing, added after amendment 1.\". FO: restore the line; add an '### Amendment N' with 'Supersedes: none' only if the Captain asked for it, with his words verbatim and where he said them. A worker that sees this line reports it to FO and edits neither Scope nor amendments.",
}
out = lambda lines: sum(w(l) for l in lines)
merge_base = sum(w(v) for k, v in base_p.items() if k in ("validation Gate content", "Delivery authority", "delivery_gate sentence")) + out(BASE_PASS)
print("README words: base %d, candidate %d" % (w(text), w(new)))
for k in base_p:
    print(f"  {k}: base {w(base_p[k])}, candidate {w(new_p[k])}")
print("moment                                              base  candidate")
print(f"startup and resume (README whole + 48-word mod)     {w(text)+w(mod):5d}  {w(new)+w(mod):5d}")
print(f"idle open PR / idle merged PR / after archive (mod + pr_watch tasks output, no file in the diff)  {w(mod)} + unchanged  = unchanged")
print(f"dispatch (Stages passage + dispatch_records output)       unchanged  unchanged")
ide_base = w(base_p['ideation Gate content']) + 3
print(f"ideation gate, pass path (Gate content + 'design surfaces presentable')   {ide_base:5d}  {w(new_p['ideation Gate content'])+3:5d}")
print(f"ideation gate, first run after a Scope edit (+R3 hold)          {ide_base:5d}  {w(new_p['ideation Gate content'])+3+w(HOLDS['R3 scope']):5d}")
for k, v in NEW_PASS.items():
    cand = sum(w(new_p[p]) for p in ("validation Gate content", "Delivery authority", "delivery_gate sentence")) + out(v)
    base = merge_base
    print(f"merge ask and merge run (same ASK line), {k:44s} {base:5d}  {cand:5d}")
for k, v in HOLDS.items():
    print(f"  one-time hold line, {k}: +{w(v)}")
print("per-call script lines: base last line", w(BASE_PASS[-1]), "words; candidate:", {k: w(v[-1]) for k, v in NEW_PASS.items()})
