"""Count words (str.split, as lint-skills.py budget does) each reader reads per moment, at two refs."""
import json, subprocess, sys
repo, base, cand = sys.argv[1:4]
def show(ref, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{ref}:kc-dev-flow-2/{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""
def section(text, head):
    a = text.index(head); b = text.find("\n### ", a + 1); return text[a:b]
def facts(text):
    a = text.index("## Dispatch facts"); b = text.find("\n## ", a + 1); return text[a:b]
W = "references/sd/workflow.md"
moments = {
  "FO startup/resume (reads the whole adopted README)": lambda r: len(show(r, W).split()),
  "Pilot ideation worker: dispatch stage definition (### ideation + Dispatch facts)": lambda r: len((section(show(r, W), "### `ideation`") + facts(show(r, W))).split()),
  "Pilot ideation worker: skill text (SKILL.md + principles.md + profiles/pilot.md + POC files it points to)": lambda r: sum(len(show(r, p).split()) for p in ["skills/ideation/SKILL.md", "skills/ideation/principles.md", "skills/ideation/profiles/pilot.md"] + (["skills/implementation/profiles/poc.md"] if "POC implementation" in show(r, "skills/ideation/profiles/pilot.md") else [])),
  "Pilot implementation worker: profiles/pilot.md": lambda r: len(show(r, "skills/implementation/profiles/pilot.md").split()),
}
out = {k: {"base": f(base), "candidate": f(cand)} for k, f in moments.items()}
for k, v in out.items(): v["delta"] = v["candidate"] - v["base"]
json.dump(out, sys.stdout, indent=1, ensure_ascii=False); print()
