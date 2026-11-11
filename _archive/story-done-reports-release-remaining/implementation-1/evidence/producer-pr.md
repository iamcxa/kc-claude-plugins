feat(kc-journey-map): report filed-task progress after archives

After a task is archived, `journey-progress.mjs --report <slug>` reports its release's completed and remaining stories and the completed tasks' pull request references. The additive `members` fields count filed work while preserving declared development status and delivery acceptance; the journey-progress contract advances to 1.1.0, retaining its v1 wire identifier.

The report reads local Spacedock state, leaves map and canvas unchanged, distinguishes release-only work from unknown stories, and returns a clear `journey progress not run:` diagnostic when observation fails. Plugin versions remain release-please-owned.

Validation: 21 progress/schema tests pass, including the existing isolated canvas refresh. Pinned relay and qnow replays preserve declared status and walk prompts; relay reports the final inbox task as 1/4 stories done with its PR. Reverse mutations catch incorrect membership, refs, report bounds and failed-read handling. The paired dev2 candidate passes all 122 unchanged consumer tests with its Captain-authorized sample update.

Merge this producer before the paired kc-dev-flow-2 change. Product push, Draft PR creation, RoboRev and hosted CI belong to the First Officer and have not run. Actual adopter rollout and the subsequent real archive report remain future acceptance. CI cost was not measured; CI configuration is unchanged.
