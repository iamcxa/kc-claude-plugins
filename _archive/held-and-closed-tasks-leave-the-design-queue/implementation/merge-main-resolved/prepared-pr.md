fix(kc-dev-flow-2): distinguish held tasks at startup and idle

Startup and idle output names held tasks by stage and asks for a Held section when its reopen/close quote is missing or unverified. It reads Spacedock's native held query, fails visibly if that query fails, and checks quote provenance against the latest hold or a Captain amendment. FO owns live Held-section edits; closed tasks stay at their stage.

Merged main 46e9d0ed4 into candidate 5859c3ccd25a86c79df3b36cafdda9762bd8142e, preserving its repaired scratch close-out and watcher behavior. The diff against main contains only the two watcher files and decision record 0081.

Validation: all 30 package commands (29 test files plus skill lint) exit 0; 1461 unittest cases pass and 10 optional external-corpus case is skipped, with native dispatch integration also passing. Native acceptance replay and six source mutations pass. The amended word bound is N+20: one held task 17/21, current fifteen 33/35, fabricated hundred across all five stages 120/120. Current held names are checked exactly once; over-bound, missing-name and duplicate-name controls reject.

The literal origin-less CLI retains the known base scratch-origin diagnostic; its held fact is exact and the actual workflow entrance exits 0. RoboRev, independent review, hosted CI and final validation remain FO-owned. CI configuration is unchanged relative to main; cost per PR was not measured.
