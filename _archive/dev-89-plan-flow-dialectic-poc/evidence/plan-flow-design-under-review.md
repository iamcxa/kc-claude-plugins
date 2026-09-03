===== THE DESIGN UNDER REVIEW: plan-flow (2026-09-03, after DEV-67 plan side and DEV-89 station 2) =====

PURPOSE. plan-flow turns one raw requirement (a journey map, a paragraph, a scenario, a vague ask) into a set of Linear objects plus a plan receipt, then stops at the Captain's approval gate. ship-flow reads only the receipt and dispatches one cloud worker per Issue through kc-dev-flow; plan-flow writes Linear, ship-flow never does.

THREE LAYERS, TWO SEAMS (the Captain's model, confirmed):
  WHY            = gstack office-hours (MIT): demand reality, status quo, who bleeds, narrowest wedge, premise challenge, alternatives.
  WHEN/HOW-TO-PLAN = pm-skills (CC BY-NC-SA 4.0: invoked when installed, never vendored; kernel carries a fallback of <=3 questions per station): problem-statement, epic-hypothesis, user-story-splitting, prioritization/roadmap when >1 Project.
  HOW-TO-BUILD   = kc-dev-flow (profile, route, proof depth); ship-flow carries it to UAT.
  Seam 1 = one-line user value + profile. Seam 2 = plan receipt.

STATIONS:
  0 observe: read Linear open Issues, SD debriefs, the ship-defects list, git log (office-hours Phase 1 analogue) -> pain inventory; mined options for the Ask UI.
  1 problem-statement -> `## The problem` (persona / trying to / but / because / feels; final single-sentence problem statement).
  2 office-hours Q1-Q4 asked to the Captain ONE PER TURN through the harness Ask UI: options mined from station 0 first, then free text. Posture verbatim from office-hours: take a position, push twice, never "interesting", no invented pain; if nothing is found, ask; if the material is unfit, say so, then guess and ask again. Output: Target User & Narrowest Wedge (a paragraph, office-hours shape) + profile choice (Q4 narrowest wedge maps to POC/Pilot/Production).
  3 epic-hypothesis -> `## Goal` first sentence as "If we [X] for [who] then [outcome]" + validation measures as the falsifier.
  4 user-story-splitting -> Issues (each a Development Brief: problem / goal / non-goals / AC-N / route-back), blockedBy DAG, Milestone = one recordable journey.
  5 lint (9 rules, mechanical, GraphQL read) -> plan receipt -> Captain approval gate.

LINEAR OBJECT SHAPES:
  Project name       = press-release headline rule: benefit-focused, specific, repeatable, 6-10 words, no "If we", e.g. "Ship gates stop re-asking the three verification questions".
  Project description first sentence = the epic-hypothesis if/then sentence, <=30 words.
  Project content    = `## User value` (that same if/then line, for lint L1) + `## Wedge` (office-hours Target User & Narrowest Wedge paragraph) + `## Outcome` + `## Exit`.
  Initiative         = required only when >1 Project (L5).
  Milestone          = one recordable journey each (L7 warns at >=4 Issues or a forked DAG).
  Issue              = Development Brief + profile receipt + blockedBy; passes kc-dev-flow's linear-admission.py.
  Lint L9 (new)      = description first sentence byte-equals content `## User value`.

PLAN RECEIPT (kc-plan-receipt/v1):
  project{id,name,outcome_hash}, cycle, milestones[], dispatch_order[] (from blockedBy DAG), edges[], issues{id -> url, branch, close_line, profile, body_sha256, description, title}, lint[], provenance{stations[{name, borrowed_skill|fallback, consumed, produced, rewritten_sentences}], captain_answers{q1..q4 verbatim}, user_value_line}, receipt_sha256.
  provenance is new: ship-flow does not read it; the close receipt (ship -> plan) is compared against it so the next plan round knows what to ask.
  Not outputs: dispatch envelopes, workspaces, PRs. plan-flow ends at the approval gate.

EVIDENCE SO FAR: DEV-67 ran stations 4-5 on a real Project (8 lint rules, receipt sufficient for 3 dispatches with no Linear read); DEV-89 station 2 ran with the Captain today (Q1-Q2 in chat, Q3-Q4 via Ask UI with mined options; Captain chose all four "who bleeds" options and "all three sentences, Pilot depth"). Stations 1, 3, 4 with borrowed vs fallback are dispatched to a worker (blocked on quota until 13:00Z).
