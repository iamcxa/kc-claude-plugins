---
title: The skill's tail restates rules it already stated
status: backlog
source: cross-model review of the kit, 2026-07-27 — the lowest-risk cut available
design:
id: tmn8fgqy8390zepcp019td74
---

`SKILL.md:1844` onward restates rules already given authoritatively in Steps 5 and 6. Deleting a
restatement removes no information, which makes this the one cut in the slimming track that does
not need a behavioural argument — only proof that the earlier statement is genuinely the
authoritative one and says the same thing.

Ordering: after `skill-ablation-harness` (5b), because "removes no information" is a claim the
harness should confirm rather than a claim the author asserts. This is the natural first real cut
once the harness exists — if the harness cannot show A/A parity on a pure restatement removal,
the harness is not ready.

Method: for each candidate, cite the authoritative statement and the restatement, show they do
not differ in substance, then cut the restatement. A restatement that turns out to say something
the original does not is not redundant — it is an undocumented rule, and it stays.

**AC-1 — Every removed line has a cited surviving statement that says the same thing.**
Verified by: a table of removed-line → surviving-line pairs, and an ablation run showing no material difference. Falsified by: a removal with no cited survivor, or an ablation difference.
