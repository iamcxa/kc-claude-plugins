"""Write the stop-condition replay texts into OUT from the state checkouts, read at the briefing's bound revision.

Usage: build_texts.py OUT KC_STATE RELAY_STATE
Each text is the validation briefing-1 question and summary; the task text is the task file at the
state commit the briefing artifact binds (git-root://state/<sha>/<path>).
"""
import json, re, subprocess, sys
from pathlib import Path
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
roots = {"kc": sys.argv[2], "relay": sys.argv[3]}
cases = {"pair-once": "relay", "fo-tries-what-it-asks-the-captain": "kc",
         "model-roster-question-needs-both-families": "kc", "rewritten-criteria-checked-against-captain-words": "kc"}
def show(root, spec):
    return subprocess.run(["git", "-C", root, "show", spec], capture_output=True, text=True, check=True).stdout
meta, texts = {}, {}
for slug, repo in cases.items():
    root = roots[repo]
    d = json.loads(show(root, f"HEAD:_archive/{slug}/review/validation/briefing-1/index.json"))
    sha, path = re.match(r"git-root://state/([0-9a-f]{40})/(.+)$", d["artifacts"][0]["uri"]).groups()
    (out / f"{slug}.task.md").write_text(show(root, f"{sha}:{path}"))
    texts[slug] = d["question"] + "\n" + "\n".join(a.get("summary", "") for a in d["artifacts"])
    meta[slug] = {"repo": repo, "folder": f"{root}/_archive/{slug}", "bound": sha}
F30 = "Declined: Deferred risk, F30, a test timeout recurred once in three runs (no pairing route involved).\n"
SEC = ("Declined: Deferred risk, security finding (validation 3) 1, a session budget taken before the address check (polling only, same minute).\n"
       "Declined: Polish, security finding (validation 3) 2, no stricter edge limit on new routes (the shared limit already applies).\n")
t = texts["pair-once"]
v = {"pair-once.bite": t + "\n" + F30,
     "pair-once.silent": t.replace("security 2 LOW declined.", "security review: 2 LOW findings.") + "\n" + F30}
v["pair-once.conforming"] = v["pair-once.silent"] + SEC
v["fo-tries-what-it-asks-the-captain.bite"] = texts["fo-tries-what-it-asks-the-captain"]
v["fo-tries-what-it-asks-the-captain.conforming"] = v["fo-tries-what-it-asks-the-captain.bite"].replace(
    "blocks every round)", "blocks every round; filed as backlog task gate-summary-names-each-decline)")
v["model-roster-question-needs-both-families.bite"] = texts["model-roster-question-needs-both-families"]
v["model-roster-question-needs-both-families.conforming"] = v["model-roster-question-needs-both-families.bite"].replace(
    "could be misread)", "could be misread; receiving task extension-instruction-followups)")
v["rewritten-criteria-checked-against-captain-words.bite"] = texts["rewritten-criteria-checked-against-captain-words"]
v["rewritten-criteria-checked-against-captain-words.conforming"] = v["rewritten-criteria-checked-against-captain-words.bite"].replace(
    "has that shape)", "has that shape; receiving task iamcxa/kc-claude-plugins:tilde-fence-example-criteria)")
for k, x in v.items():
    assert x not in texts.values() or k.endswith(".bite"), k
    (out / f"{k}.txt").write_text(x)
(out / "cases.json").write_text(json.dumps(meta, indent=1))
print(sorted(v))
