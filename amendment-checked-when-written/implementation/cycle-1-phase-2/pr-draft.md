feat(kc-dev-flow-2): flag invalid criterion moves in state pushes

When a state commit moves acceptance criteria into a Captain amendment but keeps their ids live or leaves the replacement unmarked, L4 `amendment-moves-use-fresh-ids` reports the introducing commit, amendment and defect during that push's laws run. Record-only amendments remain pending worker work. The runner reuses the existing push walker, task correspondence and one replacement-marker predicate shared with the design check.

Reuse is compared per id within each amendment, then grouped into the existing diagnostic. Repairing AC-1 while an already reported AC-2 remains produces no new event; adding AC-3 reports AC-3 without repeating surviving old ids. The unmarked-replacement comparison is unchanged.

A parser issue skips the affected amendment entry rather than the whole task file. Valid sibling moves are still judged. If a later push only repairs a broken heading, a previously unjudgeable move defect is reported at that repair commit; an already reported sibling defect is not repeated.

Validation at `d7502656c765e36ce3d24be8602862ccc2551254`:
- All 27 package test-file commands exit 0: 1,277 unittest cases run, 11 skipped, plus the model-free CLI harnesses. Local CLI fixtures use Spacedock 0.27.2 with plugin-root 0.27.3; hosted CI uses its pinned root and remains FO-owned.
- `test_laws_check.py`: 79 run, 78 passed and one optional fixture skipped. Unchanged `test_design_surfaces.py`: 217 run, 213 passed and four optional fixtures skipped.
- Each of the three new partial-repair, growth and mixed-change regressions fails with only the runtime fix reverted to the prior candidate, using `python3 -B` and absent bytecode. Nine existing mutation checks also reject their injected regressions, including both whole-file structural skips.
- The complete three-history replay retains the seven named L4 event commits, with headlines and grouped diagnostics identical to the prior candidate at the same pinned ranges. All three full CLI runs still exit 2 for existing L3 ambiguity; this is not an overall-history pass.
- Repository skill lint, package ADR lint, number guards, task-design, role triggers and comment ratio pass. `laws.md` adds 242 words, within the approved 250-word bound. This repair changes only the runner and its tests; workflow text, dispatch records, skills, CI template and versions are unchanged.

No adopter pin is changed. Hosted activation remains open until a containing release is published, the Captain approves the dev2 pin change, and a state-push run prints L4's headline. Product publication, RoboRev and hosted CI remain with the First Officer and have not been run by this worker. CI cost per PR and per state push was not measured; no trigger or job is added.
