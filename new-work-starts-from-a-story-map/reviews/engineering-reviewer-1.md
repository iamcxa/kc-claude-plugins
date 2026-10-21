# engineering-reviewer-1

Reviewer: kc-dev-flow-2:engineering-reviewer, opus, 2026-10-22. Read-only. Task at state eca4a766; package origin/main c27e7659 (kc-dev-flow-2 0.27.0, kc-journey-map 1.7.0).

Conclusion: nothing the Captain approved at backlog is withdrawn. Amendment 1 and the FO alignment Result line only add work: the build grows from one kc-dev-flow-2 PR to two, adding a release-preparation surface in kc-journey-map (Cut 1 items 1 to 4, item 8's ADR wording, AC-1 to AC-4) that the backlog gate never saw. Of D1 to D4, only D2 changes an approval rule (the seed check would hold gate prepare on a missing Release review line in every adopter). FO's new D1 variant (rulings in the map question's answer and source, one copy) fits the backlog principle better but needs a journey-map-question schema change the design excludes. Recommendation: adjust, confidence medium.

Departures to state, not waive: (a) a pre-task ruling bypasses footprint and fold under either D1 variant, against fo-batch-sittings AC-8, because journey-handoff.mjs refuses on open questions before any split; (b) the record variant's growing Rulings table works as a ruling ledger, against "No third decision ledger".

Evidence highlights: kc-journey-map lib/schemas.mjs `source` is `{kind: gate or amendment, ref: "<task slug>/<footprint source>", words, date}`, written only by journey-fold.mjs; FO's variant needs a third kind, a defined ref for a pre-task ruling and a version step, while AC-10 requires no schemas.mjs diff. journey-reconcile.mjs counts answered questions with no source as `unsourced`, so the record variant counts pre-task Captain rulings like worker facts; FO's variant tells them apart. GitHub anchors only headings, so `doc: ...#<question id>` will not jump to a table row. design_surfaces.py check_task runs Surfaces and Visible-change checks before `if seed: return errors`; if D2's requirement goes there, four tasks past backlog (kc 2, qnow 2) fail implementation and validation check. The README's "no script checks that line" becomes false under D2 while AC-11 forbids a README diff. D2 proves the line is present, not that the Captain was asked. Flow node P's docs PR has no validation gate, so its merge is the Captain's own word.

Must change before the ideation gate:
1. D1 and the gate question agree; if FO recommends the map variant, revise the design (third source kind and ref, bounded "written only", schema version step, AC-10 and the Not-changed list, AC-2(d)(e), AC-3, Cut 1 items 1, 2(c) and 8, the FAQ and List once).
2. Name the AC-8 departure in the gate question.
3. Make the Result point 4 scope growth explicit (an amendment, or named in the gate question).
4. Record whether the Captain's 「但是這四題有細節要讓我知道的嗎」 was answered.
5. Say exactly where the D2 check goes (seed-only branch) and restate what it proves.
6. Fix the README sentence D2 breaks, or order behind release-acceptance.
7. Reword Flow node P: the pre-task review docs PR is merged by the Captain's own word.
