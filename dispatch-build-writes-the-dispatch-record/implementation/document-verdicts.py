#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--code-root", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
reasons = {
    "docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md": "The recorded -2 step follows the existing exact-count rule; no ruling changes.",
    "docs/adr/0037-workers-check-shared-work-and-return-to-fo-early.md": "The protected +144 step, its quote and loaded moments are unchanged.",
    "docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md": "Agent effort and model-table comparison are unchanged.",
    "docs/adr/0052-fo-answers-its-own-paseo-workers-permission-requests.md": "The extension's normalized_words measurement and permission ownership are unchanged.",
    "docs/adr/0064-a-round-three-declined-finding-becomes-a-backlog-task-only-with-a-bite.md": "ROUND_RULE and follow-up-reason pins are unchanged.",
    "docs/dev/artifacts/skill-ablation-harness/sizing-simulation.py": "parse_args is this historical artifact's argparse method, unrelated to the new wrapper.",
    "docs/dev/artifacts/skill-ablation-harness/span-match-demo.py": "parse_args is this historical artifact's argparse method, unrelated to the new wrapper.",
    "docs/ship-flow/tools/validate-tdd-ledger.py": "parse_args is this separate ledger tool's argparse method, unrelated to the wrapper.",
    "kc-dev-flow-2/README.md": "Its complete test inventory points to the CI workflow, which now lists the new seam test.",
    "kc-dev-flow-2/references/sd/adoption.md": "test_sd_dispatch still checks both adapted graphs and split-root transport; invocation unchanged.",
    "kc-dev-flow-2/skills/maintain-flow/SKILL.md": "The exact-count lint command and separate review obligation remain accurate.",
    "learning.md": "Per-moment recount and retained follow-up wording pins are exercised, with their obligations unchanged.",
}
rows = json.loads((args.output_dir / "doc-impact.json").read_text())
verdicts = [dict(doc=row["doc"], verdict="updated" if row["state"] == "updated" else "unaffected",
                 reason="New accepted ruling and protected writer pointer." if row["state"] == "updated" else reasons[row["doc"]]) for row in rows]
(args.output_dir / "doc-impact-verdicts.json").write_text(json.dumps(verdicts, indent=2) + "\n")
base = subprocess.run(["git", "-C", str(args.code_root), "show",
                        "334d91e3165953b2ca7191e3308d80b6c02c4a99:kc-dev-flow-2/references/sd/workflow.md"],
                       check=True, capture_output=True, text=True).stdout
candidate = (args.code_root / "kc-dev-flow-2/references/sd/workflow.md").read_text()
patterns = [(r"FO saves those scope notes,.*?fixes each part it lists\.",
             r"FO builds each worker dispatch with.*?the build's commit carries the record\."),
            (r"A follow-up\s+message to a worker FO resumes.*?never a pointer to another record\.",
             r"A follow-up message to a worker FO resumes.*?--workflow-dir <dir>`\."),
            (r"Before `dispatch build`, FO runs.*?context checks on stderr\.",
             r"Each record passes.*?context checks on stderr\.")]
old = [len(re.search(pair[0], base, re.S)[0].split()) for pair in patterns]
new = [len(re.search(pair[1], candidate, re.S)[0].split()) for pair in patterns]
counts = [dict(name="Startup and resume", before=len(base.split()), after=len(candidate.split()), better="lower"),
          dict(name="Fresh dispatch: passages and successful checker output", before=old[0]+old[2]+4, after=new[0]+new[2], better="lower"),
          dict(name="Follow-up: passages and successful checker output", before=sum(old)+4, after=new[1]+new[2]+4, better="lower")]
(args.output_dir / "lifecycle-words.json").write_text(json.dumps(counts, indent=2) + "\n")
print(json.dumps(dict(passages_before=old, passages_after=new, moments=counts)))
