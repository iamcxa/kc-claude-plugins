fix(kc-dev-flow-2): file declined findings only with a bite

A third-or-later review decline keeps its finding and reason in the committed gate summary. FO creates or reuses a backlog task when there is an observed failure naming who it hurts, a repeat in a later round or task, or a Captain request. The rule still keeps declined findings out of an open task's Scope.

Update the dispatch wording pins and record ADR 0064, superseding ADR 0010. The one-line ADR 0047 path construction preserves its supersession assertion while avoiding an adr_lint false positive, as explicitly directed by FO in implementation-1-message-3.

Validation: 11 deterministic acceptance groups pass, including the repository skill lint (5939/5939 words), native dispatch suite, candidate/base wording pins, three archived decline replays, mutation checks, ADR lint, number guards and design-surface check. Two fresh Sonnet candidate readings classify A/B/C ok and D violation; the base reading classifies A/B/C violation. A bounded observer replay reports the old step-5 violation with the base README and no such violation with the candidate README.

Open evidence limit: AC-4's specified bite-clause deletion does not make D ok in either of two independent Sonnet runs; both classify D as Material under the unchanged blocking clause. Per FO's implementation-1-message-4, this is FAILED: falsifier confounded for Captain disposition at the gate; no alternate falsifier or wording change was substituted.

RoboRev not run: FO runs the exact-head review outside the Codex sandbox. Product publication, Draft PR creation and CI are FO-owned; no product push or PR creation was performed by the worker. CI cost per PR was not measured; CI files and triggers are unchanged.
