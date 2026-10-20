#!/usr/bin/env python3
"""Words FO reads at each lifecycle moment, base (origin/main ad44f0cb, 0.26.0) and candidate, counted with str.split().

Usage: python3 -I -B words.py workflow-0.26.0.md mod-0.26.0.md
The candidate README is the base with one sentence edit (E1 below) applied in memory; script output lines are the
strings the design prints, typed here so the count is reproducible. A moment's number is every passage and every script output
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
NEW_PASS = {
    "ask run, text lacks a Merges line": ["PR head 40c714a6 equals dispatched candidate 40c714a6; no second reviewer outcome is missing", "class: never",
        "record: task/merge/ask-1.json", "next: ask the Captain with this text; to carry the merge, first add a 'Merges: <owner/repo>#<N>' line naming this PR to the question."],
    "ask run, text has a Merges line": ["PR head 40c714a6 equals dispatched candidate 40c714a6; no second reviewer outcome is missing", "class: never",
        "record: task/merge/ask-1.json", "next: ask the Captain with this text; nothing is carried until he approves it."],
    "merge run, Merges line names the PR": ["PR head 40c714a6 equals dispatched candidate 40c714a6; no second reviewer outcome is missing", "class: never (verdict ask)",
        "record: task/merge/ask-2.json",
        "next: merge this head; the question he approved on 2026-10-20 names iamcxa/kc-claude-plugins#682 in its Merges: line. Ask instead if his reason (Captain approved in chat after the gate briefing, FO merges the head with --match-head-commit) says he merges or holds."],
    "merge run, no Merges line for the PR": ["PR head 40c714a6 equals dispatched candidate 40c714a6; no second reviewer outcome is missing", "class: never (verdict ask)",
        "record: task/merge/ask-2.json", "next: ask the Captain to merge; the question he approved names no merge of iamcxa/kc-claude-plugins#682."],
}
HOLDS = {
    "R2 findings join": "declined items (3) are fewer than the validation report's Deferred risk and Polish findings (5): add a declined item or a stated fix for each, then run this check again.",
    "R1 follow-ups claim": "chat-only-followups.md claims the Captain's acceptance in its title or first paragraph (\"accepted\") before the gate that records it: say what FO declined and cite no ruling.",
    "R3 scope": "Scope changed after the backlog gate (fbcb7a9e): \"Captain's scope addition, 2026-10-20: ...\": if the Captain asked for it, add an '### Amendment N' with 'Supersedes: none'; otherwise restore the line.",
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
    print(f"merge ask/merge, {k:40s} {merge_base:5d}  {cand:5d}")
for k, v in HOLDS.items():
    print(f"  one-time hold line, {k}: +{w(v)}")
print("per-call script lines: base last line", w(BASE_PASS[-1]), "words; candidate:", {k: w(v[-1]) for k, v in NEW_PASS.items()})
