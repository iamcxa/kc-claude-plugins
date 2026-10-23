# 0030. A ui design review is run by a named director, and a declined finding is closed only by its upheld ruling

Date: 2026-10-22

## Status

Accepted

## Context

Measured 2026-10-22 on 7 kc-paseo-plugins tasks: the design review raised 93 findings and the author declined 70 (37 citing a host component); 10 of the 14 findings of a later critique had already been raised and declined at MINOR; 4 of 7 validations had no screenshot of the candidate. ADR 0022 chose a `general-purpose` agent and a worker who dispositions its own findings. A replay of the 70 declines with a second sonnet check overruled 31; the same check on 39 of them without the duty wording overruled 6 and upheld 23. The Captain's own Browse complaint stays declined under every arm.

## Decision

**Words:** 「我還是希望開設計總監，讓它來做目前指示的內容，等於派出的 general purpose sonnet 改成設計總監。」 — Captain, 2026-10-22, chat; 「可以」 at the backlog gate, 2026-10-22; 「設計總監照建議。這個角色會叫什麼？GPT 同伴仍保留提案，之後再討論」 — chat, 2026-10-22; D-4 「可以」, D-5 「要擋下，不然找它的意義就消失了」 and D-6 「可以」 — chat, 2026-10-22; 「可以」 at the ideation gate, 2026-10-22, accepting D-7 as designed and the 15-word raise of the workflow README budget.

**Options considered:**
- the named `design-director` agent on sonnet rules each proposed decline, reads the product's accepted ADRs first, and the upheld ones are listed for the Captain (chosen)
- keep the `general-purpose` agent and the author's own dispositions — not chosen, it is the measured loss
- a second sonnet check with the declarations but without the duty wording — not chosen, it upholds 23 of 39 where the wording upholds 12 to 14
- opus — not chosen, ADR 0022 D3 measured no gain and the measurement shows no evidence the model is the problem
- a gpt-6-astra helper — dropped by the Captain (Amendment 1)
- a design-guide format, or a guide written as ADRs — not chosen, a product's own design rulings are ADRs and a generated index waits until they accumulate
- project learning for a standing host-look ruling — not chosen, a ruling on direction is an ADR in the product's repository
- a release-level operated whole-screen review in this task — not chosen, release-acceptance owns it

**Recommended:** the first option, as the Captain's 「設計總監照建議」 accepted. A host-look departure the Captain rules lands as an ADR in the product's repository at its first appearance. Validation refuses a ui task that has a `Design review:` line and no built-screen review unless the Captain waives it in quoted words; a ui task with no `Design review:` line (ideated before the review existed) is exempt, because `design_surfaces.py check` tests the built-screen rule only where that line exists. At validation the same ruling applies to the MINOR findings the validator proposes to decline.

## Consequences

Each ui ideation costs a second director run (77k to 115k tokens per task on the replay) and the Captain reads the upheld lines and decision groups at the gate (30 to 141 and 17 to 143 words per task, simulated). Each ui validation costs a pass-2 run and, with MINOR findings, a decline-check run (not measured). `design_surfaces.py check` proves a ruling exists and its form; it does not prove that the agent that wrote the report was the named one, that an upheld decline is right, or that a later FO decline cites a ruling. A stall is possible where a validator cannot produce a screenshot of the built screen; the Captain's waiver or an environment fix ends it. The whole-screen operated review is release-acceptance's. This record replaces the 13-word cost ADR 0022 recorded for the ideation gate. Reopen if a decline the director upheld is later found wrong at a gate or a critique.
