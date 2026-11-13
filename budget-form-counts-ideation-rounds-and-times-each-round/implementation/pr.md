feat(kc-dev-flow-2): count ideation budgets and report each round

A task budget can now bound design rounds with `N ideation, N implementation and M validation cycles`. Countable Pilot budgets without an explicit design bound allow two rounds; `dispatch_stage.py` checks that budget before building a design dispatch and leaves special-role holds at their existing implementation/validation boundaries.

The timeline prints each round's start, end, minutes and gate result. ADR 0085 extends ADRs 0077, 0080 and 0084. The workflow's lint word budget decreases by 2 (currently 6099 to 6097); preserve that delta when merging the sibling workflow edit from main. No versions are changed.

Validation: 366 unittest tests run, 4 optional historical-corpus tests skipped; all four required suites pass. A frozen 249-task comparison has zero exit changes, and all 192 archived design rounds have an end and match their dispatch counts. Ten mutation checks fail as expected; removing the new grammar or default wrongly permits the third replayed design dispatch. Lint, ADR lint, number guards and the 5% comment maximum pass (2.6%). Commands, exits, outputs and candidate hashes are retained in the task's evidence/implementation-1 folder on spacedock-state/dev2.

This is a locally prepared candidate. RoboRev, hosted CI, product push and Draft PR creation are assigned to First Officer and have not run here. CI cost per PR was not measured; CI configuration is unchanged. Live behavior after release remains unproved.
