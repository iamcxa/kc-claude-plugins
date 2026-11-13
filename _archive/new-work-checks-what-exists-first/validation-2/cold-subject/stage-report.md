## Stage Report: ideation

- DONE: Prepare the smallest ideation proposal for the assigned task Scope.
  proposal.md repairs the local path entrance; observations.md records the existing-chain check before the proposal was written.
- DONE: Current design definition and acceptance criteria with reproducible evidence clauses; unresolved decisions identified for the user.
  proposal.md contains PRFAQ, matching Mermaid, Worth questions, bounded non-goals, batch overlap and three individual criteria; no material unresolved decision identified.
- DONE: Run design_surfaces.py check and cite its output.
  Unmodified candidate checker on subject-output/proposal.md exited 0: "proposal.md: design surfaces presentable" and "scope check not run: no frontmatter" (proposal-check.log). This checks the standalone proposal, not original task state or gate approval.
- DONE: AC-1 current evidence.
  reproduction.json: basename/default crashes with IsADirectoryError while explicit .md exits 0; seed basename rejects while explicit .md exits 0. Repaired behavior remains unverified; the planned regression fails if raw argument handling is restored.
- DONE: AC-2 current evidence.
  Explicit-file success and current separate mode rules inspected; precedence, dotted directory and malformed-sibling regressions remain future implementation evidence, with different-content fixtures to detect wrong selection or bypass.
- DONE: AC-3 current evidence.
  Missing-input/default traceback and seed controlled failure observed. Corrected unreadable-target behavior remains unverified; restoring an unguarded scope read is the planned falsifier.
- SKIPPED: Write or commit the entity body and stage report to state.
  The isolated harness authorizes writes only under subject-output and explicitly overrides generated state/commit instructions; original state and product files were not edited.
- SKIPPED: Application tests, private task corpus checks and Mermaid rendering.
  No application run is required; servers/browsers are prohibited. The adopter filesystem count probe exposed no state checkout; no private names, titles, rulings or logs were persisted. Rendering remains unverified.

### Summary

The current CLI collision is reproduced and the proposal changes only existing task-path selection and controlled read failure, retaining validators and authority. The proposal is a harness artifact pending the existing design gate, not an implementation or approved task-state update; all scratch/evidence is confined to subject-output and the candidate checker hash remained unchanged.
