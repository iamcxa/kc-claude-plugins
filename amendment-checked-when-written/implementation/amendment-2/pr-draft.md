feat(kc-dev-flow-2): flag invalid criterion moves in state pushes

When a state commit moves acceptance criteria into a Captain amendment but keeps their ids live or leaves the replacement unmarked, L4 `amendment-moves-use-fresh-ids` reports the introducing commit, amendment and defect during that push's laws run. Record-only amendments remain pending worker work. The runner reuses the existing push walker, task correspondence and one replacement-marker predicate shared with the design check.

A parser issue skips the affected amendment entry rather than the whole task file. Valid sibling moves are still judged. If a later push only repairs a broken heading, a previously unjudgeable move defect is reported at that repair commit; an already reported sibling defect is not repeated.

Validation at `72216e2e947e962737a17c6e61ef3800f9d639c4`:
- `test_laws_check.py`: 76 tests run, 75 passed and one optional environment fixture skipped.
- Unchanged `test_design_surfaces.py`: 217 tests run, 213 passed and four optional environment fixtures skipped.
- The three new regression tests fail on the previous candidate and pass after the narrower skip. Nine mutation checks catch disabled reuse, marker, payload, first-parent, registry and per-entry checks, including restoration of the whole-file and first-parent structural skips.
- All seven named historical event commits produce L4 events, including dev2 `bf8c73be99c4` and Relay `06cadae7681f`. The state-branch task evidence binds full-history ranges, output and falsifiers.
- 1,032 task/mode verdicts from three pinned adopter tips match the base design checker.
- Repository skill lint, ADR lint, number guards and comment ratio pass. `laws.md` adds 242 words, within the approved 250-word bound. Workflow text, dispatch records, skills, CI template and versions are unchanged.

No adopter pin is changed. Hosted activation remains open until a containing release is published, the Captain approves the dev2 pin change, and a state-push run prints L4's headline. Product publication, RoboRev and hosted CI remain with the First Officer and have not been run by this worker. CI cost per PR and per state push was not measured; no trigger or job is added.
