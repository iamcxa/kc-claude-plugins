"""Show which test_sd_dispatch.py wording pins the candidate README breaks, and that the proposed pins pass on it and fail on base.

Usage: pins.py PACKAGE_COPY  (a kc-dev-flow-2/ folder whose references/sd/workflow.md is base or candidate)
Imports test_sd_dispatch from that copy; runs no SD binary.
"""
import re, sys
from pathlib import Path
pkg = Path(sys.argv[1]); sys.path.insert(0, str(pkg / "scripts"))
import test_sd_dispatch as t
flat = " ".join((pkg / "references/sd/workflow.md").read_text().split())
print("ROUND_RULE missing:", [p for p in t.ROUND_RULE if p not in flat])
print("follow-up-reason gaps:", t.fix_gaps(t.pinned_texts())["follow-up-reason"])
PROPOSED_ROUND = "Only an observed failure naming who it hurts, a repeat in a later round or task, or a Captain ask makes it a backlog task"
PROPOSED_NEED = ("naming the finding and its reason", PROPOSED_ROUND, "or the one holding it", "it never enters an open task's Scope")
PROPOSED_SWAP = r", naming the finding and its reason\. Only an observed failure.*?The terminal gate lists each such task\."
print("proposed pins missing:", [p for p in PROPOSED_NEED if p not in flat])
print("proposed swap matches:", len(re.findall(PROPOSED_SWAP, flat)))
