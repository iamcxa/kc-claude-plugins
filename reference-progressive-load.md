---
title: Three references load whole on the ordinary path
status: backlog
source: kit cost map, 2026-07-27
design:
id: skw440fyhyv32dhgta3dwjsc
---

`review-triage.md` (246 lines), `compliance-audit.md` (162), and `learned-patterns.md` (1193, on
any non-trivial PR) are read in full on an ordinary review. `gh-api-patterns.md` shows the
alternative already working in this same skill: it is read three times, each by named section
(`SKILL.md:102`, `:108`, `:1826`).

Anthropic's guidance calls this progressive disclosure and reports removing over 80% of Claude
Code's own system prompt with no measurable loss on their evals. **That number is theirs, on their
prompt, against their evals — it is not a target for this kit**, which has neither their prompt
nor their evals. It is a reason to try, not a quota to hit.

**This is a behaviour change, not a mechanical refactor.** If fewer sections load, the model has
less to work from; if all of them still load, nothing is saved. Whichever sections stop loading by
default, something must decide when to fetch them, and that decision is the design work here.

Ordering: after `skill-ablation-harness` (5b), and after the two cheaper cuts, because it is the
first one whose failure mode is a quieter review rather than a broken one.

**AC-1 — A default review loads less reference text and emits the same findings.**
Verified by: measured bytes loaded before and after, plus an ablation run on the frozen corpus showing no material difference. Falsified by: no measured reduction, or an ablation difference.
