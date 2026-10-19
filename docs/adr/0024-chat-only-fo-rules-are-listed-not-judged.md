# 0024. An FO rule whose only witness is the Captain's chat or a shell run is listed as not judged

Date: 2026-10-19

## Status

Accepted

## Context

The observer reports on six batch-2 tasks marked 18 rows `can't tell`, naming 17 FO rules in 40 rule-report pairs. Each row was judged by one question: who or what can see the evidence, and does anyone need it later. 10 pairs are readable from state (`design_surfaces.py check` replayed at the task-file sha a briefing binds; `merge/ask-<N>.json`, written by `delivery_gate.py check` since 0.25.0). 4 are held by FO alone and no one else sees them (the sufficiency and necessity confirmation before a merge ask). 16 are witnessed only by the Captain's chat or by a shell run that leaves no record. 10 are not chat-only and stay as they are or go to `fo-write-checks` and `captain-question-load`. Replaying `design_surfaces.py check` over history exits 1 in 11 of 82 runs for a section the task's gate did not yet need, which is ADR 0017's reason a law over history is red by age; ADR 0014 already accepts that `workflow_checkout.py` is prose-enforced.

## Decision

**Words:** 「照建議」 — Captain, 2026-10-19, chat, approving the four batch-3 ideation gates presented together. This task's gate question read: "Approving accepts D1 (the observer stops judging the rules only chat can show: the acceptance steps in full, the package and checkout runs, answering a Captain question, the --names run, the four-field assessment, while the rest are read from state or recorded), D2 (Sufficiency: and Necessity: clauses in the delivery gate text, held by delivery_gate.py), D3 (the acceptance steps shown in full stay chat-only), and FO's implementation order below."

**Options considered:**
- D1 list the chat-only rules in the observer skill as not judged, replay or read the ones state holds, and lint each listed phrase against `references/sd/workflow.md` (chosen); keep reporting all of them `can't tell` — not chosen, it names rules the observer can never see
- D2 `delivery_gate.py` holds a merge ask whose text has no `Sufficiency:` or `Necessity:` clause and saves both in `ask-<N>.json` (chosen); list the confirmation as not judged — not chosen, no one but FO sees it
- D3 the acceptance steps in full stay chat-only (chosen); save the observed output and pass it to `gate prepare --reference` — not chosen, it needs a README sentence and a budget raise under ADR 0020

**Recommended:** D1, D2 and D3 as chosen, as the task design stated and the Captain accepted.

An FO rule whose only witness is the Captain's chat, or a shell run that leaves no record, is listed in the observer skill as not judged. It gets a record only when a later reader needs one. `lint-skills.py` fails when a listed phrase is not in `references/sd/workflow.md`, so a reworded rule cannot leave the list unnoticed.

## Consequences

The observer stops reporting 16 of the 40 pairs and reads 10 more from state; a first merge ask without both clauses holds once and the hold line names what to add, and an adopter meets that hold at its first ask after a plugin update. `delivery_gate.py` checks that a clause is present, not that it is true, so `Necessity: yes` passes. Worse: an FO that shortens the acceptance steps or skips `workflow_checkout.py` leaves nothing the observer can show, so only the Captain's attention and the script's own hold catch it. Reopen if an observer report or the Captain finds a listed rule broken with nothing in state or chat to show it, if a gate is found presented where `design_surfaces.py check` exits 1 at its bound sha, or if Spacedock gains a pre-dispatch hook (ADR 0014).
