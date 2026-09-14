# Independent recut validation: FAIL

Layer 2 readback silently edits the wrong story when two distinct IDs have the same text.
The actual document API accepted an edit to `a-2`; `journey-read --out` reported
`reworded story a-2` and exited zero, but saved the new text on `a-0`. The intended
`a-2` stayed unchanged. The same instrument then passes the distinct-wording control.
Both source file hashes remain unchanged. The owned server was stopped.

Root cause: layer-2 `kc-journey-map/lib/read.mjs:176` selects the first story by
old wording. Layer 3 retains this selection at line 252; layer 4 already uses
ID selection at line 238. This is an inherited bug made relevant by the proposed
independently usable intermediate delivery units, not a regression in final progress.

The frozen five-tree manifest and producer equivalence/replay receipts were read,
not rerun. All five snapshot working files matched their own indexes before any
correction. Layer 1 retains the old team-ops skill/template/registration and its
new skill references only installed doctor/canvas/export/import/smoke surfaces.
Layer 2 imports only its own story renderer/records/model/read modules plus declared
Node/package dependencies; no board, function-map, evidence, selection or progress
implementation is hidden there. Layers 3/4/5 retain the recorded 44/67/72 passing
checks and final equality evidence; those do not disprove this earlier-layer failure.

`same-wording-proof.json` is actual runtime evidence; `same-wording-probe.mjs`
is the reproduction. Run with Node and `RECUT_SNAPSHOT_ROOT` set to the candidate
worktree's `.context` directory, after its documented dependencies are installed.
It chooses an ephemeral loopback port, creates only local fixture files and rooms
beside itself, then stops only its own process. The original raw evidence is in
`journey-stack-recut/.context/independent-recut-validation`.

No new delivery PR exists for these trees. No provider clean-review claim is made.
GitHub Actions cost remains unmeasured. Existing icon-appearance and shared-install
limits remain. The inherited layer-3 EOF blank line is formatting, not this failure.

No canonical two-file review room exists under the entity. The exposed tools have
no Subspace/Briefing producer; installed `subspace:r` only presents a file or existing
package, with Briefing construction delegated to its interactive binary. No schema,
review decision, gate publication or round receipt was fabricated.

FO disposition: promote only the existing layer-4 ID-selection hunk into layer 2,
carry through layer 3, subtract it from layer 4's delta; retain exact layer-4/5
endpoints and qualify layer-3 equality by that exact hunk. Producer owns correction.
