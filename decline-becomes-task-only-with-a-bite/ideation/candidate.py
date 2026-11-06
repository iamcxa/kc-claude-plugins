"""Write the candidate README (references/sd/workflow.md with step 5 rewritten) and count words as lint-skills.py does.

Usage: candidate.py BASE_WORKFLOW_MD OUT_MD
"""
import re, sys
from pathlib import Path
OLD = ("FO declines it in the committed gate summary, naming the finding, and\n"
       "   files it as a new backlog task with `spacedock new` whose body carries the finding\n"
       "   and the decline reason, or names the backlog task that already holds it when a later\n"
       "   round repeats it; it never enters an open task's Scope.")
NEW = ("FO declines it in the committed gate summary, naming the finding and\n"
       "   its reason. Only an observed failure naming who it hurts, a repeat in a later round\n"
       "   or task, or a Captain ask makes it a backlog task (`spacedock new`, or the one\n"
       "   holding it); it never enters an open task's Scope.")
words = lambda t: len(t.split())  # lint-skills.py main(): len(read_text().split())
base = Path(sys.argv[1]).read_text()
assert base.count(OLD) == 1, "step 5 text not found once"
cand = base.replace(OLD, NEW)
Path(sys.argv[2]).write_text(cand)
print(f"step 5 sentence: base {words(OLD)} words, candidate {words(NEW)} words, delta {words(NEW) - words(OLD)}")
print(f"workflow.md: base {words(base)} words, candidate {words(cand)} words")
