# 0022. A ui task's ideation runs one design review that the design check enforces

Date: 2026-10-17

## Status

Accepted

## Context

Three designs reached the Captain with defects visible in their own previews: a holder panel that stated one count twice and drew its Refresh as a text button among icon buttons, a phone refresh icon drawn as a filled square after a redraw, and three disclosure controls with opposite chevrons for one state. Each was sent back, and no stage looked at the previews before the gate. A replay on the archived previews of that bite, with a packaged brief, named the repeated count, the crowded chrome, the cycle-3 phone refresh icon and the opposite chevrons on the first brief that carried an inventory pass, and did not name the cycle-1 text Refresh button; one run per preview, on one project. Opus on the first brief found no more than Sonnet at about twice the duration.

## Decision

**Words:** 「那就照建議」 — Captain, 2026-10-17, chat, answering the ideation gate question 「Approve the design and enter implementation as Pilot? Approving accepts the recommendations D1 (ship although the reviewer found 3 of the 4 named defects, and record the miss: the cycle-1 text Refresh button), D2 (run the reviewer again after a MAJOR is fixed, at most twice), D3 (Sonnet as the reviewer), and FO's implementation order below.」

**Options considered:**
- the ideation worker of every task whose `Surfaces:` include `ui` dispatches one `general-purpose` Sonnet agent with the packaged brief in `skills/ideation/design-review.md`, writes one disposition line per finding, and the existing `design_surfaces.py check` refuses a ui design at ideation without a review that ran or a finding without a disposition (chosen)
- D1 ship although the brief did not name the cycle-1 text Refresh button, and record the miss in the brief (chosen); a third brief revision aimed at that button — not chosen, it fits one example
- D2 run the review again after a MAJOR is fixed by a redraw, at most twice (chosen); one run only — not chosen, the cycle-3 defect came from a redraw
- D3 Sonnet (chosen); Opus — not chosen, no more found at about twice the duration, and not measured on the final brief
- `design:design-critique` — not chosen, interactive and not installed by the package; `ui-verify` — not chosen, it checks values someone already wrote and belongs to validation; a new agent or extension — not chosen, the brief and the existing check suffice

**Recommended:** the first option with D1 to D3 as listed, as the Captain accepted.

A ui task's ideation worker runs the review before reporting. A MAJOR finding is never declined by the worker. The review advises and holds no gate.

## Consequences

Every ui ideation costs one reviewer run (84,374 to 101,404 tokens, 58 to 147 seconds measured on the replay) and one disposition line per finding, 13 to 24 on the replay; a second run after a fixed MAJOR doubles the run. FO reads 13 more words at the ideation gate of a ui task and none elsewhere. The check proves a disposition exists and that the report names the task's `Preview:` line, not that the criterion answers the finding, that a `fixed:` picture was redrawn, or that the second run happened. The report is model output on pictures and cannot operate a preview. Reopen if a bite recurs that the review did not name, or if a replay on a second project finds the brief does not generalize.
