feat(kc-dev-flow-2): flag invalid criterion moves in state pushes

When a state commit moves acceptance criteria into a Captain amendment but keeps their ids live or leaves the replacement unmarked, L4 `amendment-moves-use-fresh-ids` reports the introducing commit, amendment and defect during that push's laws run. Record-only amendments remain pending worker work. The runner reuses the existing push walker, task correspondence and one replacement-marker predicate shared with the design check.

Reuse is compared per id within each amendment, then grouped into the existing diagnostic. A partial repair adds no event for surviving old ids; newly introduced reused ids are reported. L4's live-declaration input excludes both backtick- and tilde-fenced examples, so a fake marked criterion in an example cannot hide a real unmarked replacement. This filter is local to `move_defects`; the shared fence/marker helpers, amendment parser and public check/seed functions retain their prior bytes.

A structural issue skips the affected amendment entry rather than the whole task file. Valid sibling moves remain judged. A later heading repair reports a previously unjudgeable move defect without repeating an already reported sibling defect. Unreadable blobs retain the documented cannot-judge behavior (exit 2).

Validation at `864536d1180334fa8a10c1ec7122f2ddf0feea14`:
- All 27 package test-file commands exit 0: 1,282 unittest cases run, 11 skipped, plus model-free CLI assertions. Local CLI fixtures use Spacedock 0.27.2/plugin root 0.27.3; hosted CI remains FO-owned and uses its pinned root.
- `test_laws_check.py`: 84 run, 83 passed and one optional fixture skipped. Unchanged `test_design_surfaces.py`: 217 run, 213 passed and four optional fixtures skipped.
- The five promoted example controls pass; the F3 regression fails with only its input-filter repair reverted. All three earlier partial/growth/mixed regressions fail when their per-id repair is reverted. These negative probes use `python3 -B` with caches absent; nine existing mutation checks also reject their injected regressions.
- The shared design module is byte-identical outside the L4-only helper (55 unchanged functions). All 1,032 check/seed verdicts across the pinned adopter snapshots match the base.
- Full-history replay retains the seven named L4 events with headlines and grouped diagnostics identical to the prior candidate. Newer local tails add no L4 event. All three full CLI runs still exit 2 for existing L3 ambiguity; no overall-history pass is claimed.
- Skill lint, package ADR lint (including explicit required records), number guards, task design, role triggers and comment ratio pass. `laws.md` retains +242 words within the approved +250 bound. This repair changes only the design helper and its laws tests; workflow, skills, dispatch records, CI template and versions are unchanged.

No adopter pin is changed. Hosted activation remains open until a containing release is published, the Captain approves the dev2 pin change, and a state-push run prints L4's headline. Product publication, RoboRev and hosted CI remain with the First Officer and have not been run by this worker. CI cost per PR and per state push was not measured; no trigger or job is added.
