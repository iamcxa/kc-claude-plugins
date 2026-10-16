# 0016. The amendment check refuses an unnamed move and an unmarked replacement

Date: 2026-10-16

## Status

Accepted

## Context

ADR 0005 made `design_surfaces.py check` refuse an amendment entry with no `Captain:` line and a superseded id still declared. The observer reports on archived tasks `delivery-gate-verdict-form` and `fo-lifecycle-mod` found FO-written amendments that broke the README `## Captain amendments` form while `check` printed `design surfaces presentable` (run 2026-10-16 on the committed archive copies, exit 0 each): six replacement criteria without "Amended by Captain, amendment N", and an entry whose `Supersedes:` line read `none` while seven criteria sat in it. Read-only run over 43 task files with amendment entries in this workflow, relay, qnow and subspace-web (2026-10-16): 74 entries, and the two new rules refuse 10 errors on 8 tasks. Read one by one, 7 errors on 6 tasks break the README form (unmarked or variant-phrased replacements, an unnamed move, a move recorded outside its entry); 1 (`owner-sees-all-feedback-room` amendment 3) moved criteria to a new task and clears with the waiver below; 2 (`staff-multi-branch` amendment 1) moved criteria to a new task, which the waiver covers, and also moved clauses of criteria that stay declared, which no waiver covers.

## Decision

**Words:** 「准」 — Captain, 2026-10-16, at the ideation gate of `amendment-form-check`; the gate question stated that approval accepts each decision as recommended. Decision D1 as recommended: refuse a replacement with no marking phrase, with a waiver written on the `Supersedes:` line.

**Options considered:**
- `check` also refuses an entry holding a criterion its `Supersedes:` line does not name, and an entry that supersedes ids when no criterion says "Amended by Captain, amendment N" and the line lacks "no replacement" (chosen)
- refuse only the moved criterion the line does not name — not chosen: the unmarked replacement then stays visible only to the observer, after the PR
- also scan `Design:` for FO's own words — not chosen: 34 of 35 non-`none` values in the corpus are FO prose the form allows, so no text rule separates a pointer from a paraphrase

**Recommended:** the first option, as the Captain accepted.

The rule later work must follow: `check` exits 1 for a criterion held in an entry that `Supersedes:` does not name, and for an entry whose `Supersedes:` names ids when no criterion in `## Acceptance criteria` or in another entry's moved text carries "Amended by Captain, amendment N" for its number, unless the line says "no replacement". It supplements ADR 0005 and leaves its decision standing.

## Consequences

FO writes one more token on the `Supersedes:` template. A worker can type "no replacement" falsely, and one marked criterion satisfies an entry whose other replacements are unmarked. `check` still cannot see a skipped move or FO's words in `Design:`; the observer keeps both. A partial move of a criterion's clause (corpus: `staff-multi-branch` amendment 1) is refused: the form has no partial move, and naming the id fails the still-declared rule. Entries already archived with these breaks now fail `check`; a runner that executes `check` over closed tasks would report them. Reopen if a task needs a partial supersession.
