# Five-layer local commit review packet

Kent approved this delivery grouping with "確認這樣拆". This is a recut of already
approved feature content, not a new feature authorization. The old task approval
and historical stage receipts remain unchanged. Independent validation and exact
local product commit approval are still required; no product commit, push, PR,
merge, release, or delivery acceptance is included in this preparation.

Pinned main: `c9c5752fda853737d4a937ad7f59564c5651ca53`.
Code owner: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-stack-recut`,
branch `codex/journey-stack-recut`. Candidate snapshots are its `.context/layer-1`
through `.context/layer-5` directories. Each has an independent temporary Git
index and no product commit; the parent code worktree remains clean at pinned main.
Raw patches, temporary indexes, test logs, isolated install, browser artifacts,
and native exports live at
`/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-stack-recut`.

## Review the actual candidates

| Layer | Files | Added/deleted lines | Generated lines (share) | Cumulative tree |
|---|---:|---:|---:|---|
| 1 | 24 | +6023/-0 | 5309 (88.15%) | `feec1a91f7479f9f1ff15b8a0bf8650d86271421` |
| 2 | 24 | +1075/-334 | 0 (0.00%) | `9c3eb9fd9ace855df2654f3f122ed8d270cf6a3b` |
| 3 | 34 | +1966/-139 | 1 (0.05%) | `55b4416f5b37649fc0fec4d7eeddcef3561bad9c` |
| 4 | 21 | +625/-376 | 2 (0.20%) | `6b4d5e8a747d9d13a4c8d2a832e0b9395b04beff` |
| 5 | 10 | +433/-27 | 0 (0.00%) | `cefe085d5d9b12b5679421b5607c808d6989a1b7` |

Counts are adjacent-layer Git diffs. Generated means `package-lock.json` and native
`.tldr` data; the latter is serialized onto one line, so line counts understate its
byte volume. `manifest.json` lists every changed path and patch SHA-256. The
original progress scope remains 10 files / 460 changed lines, below its 700-line
limit; its reader plus CLI remains the approved 125 lines, below 260. The larger
recut is separately authorized delivery preparation, not a threshold reset.

1. **Persist an editable canvas.** Add standalone registration, truthful skill
   setup/portability instructions, unchanged locked dependencies, and native
   server/client. Preserve current-main's legacy team-ops journey skill, HTML
   board and registration until the replacement is usable in layer 2.
2. **Plan a story map.** Add YAML activities, stories, horizontal value-release
   bands, render and readback with duplicate/placement refusal. Split shared
   render/read/records/fixtures/tests by functional hunks; no hidden board,
   function-map, evidence model, or selection implementation. Replace the legacy
   drawing skill with the independently usable native story-map workflow here.
3. **Inspect release detail and evidence.** Add optional system/constraint boards,
   function-map, selection, release contracts, executable citation lint, and the
   full worked example. This tree equals pinned main merged with original #394.
4. **Apply existing border/story changes.** Entire original `1166747c..bc51b246`
   delta is retained, including its predecessor corrections and roadmap entry.
5. **Apply local task progress.** Entire original `bc51b246..947501df` delta is retained.

`equivalence.json` records zero tree diffs against all three expected merges and
both endpoints' touched-blob equality for layers 4/5. `patch-proof.json` proves the
five review patches replay consecutively to these trees. This preserves unrelated
current-main updates. Version parity passed in each layer, with package.json and
package-lock.json unchanged across all five. Only layer 3's inherited final blank
line in `lib/storymap.mjs` produces a `git diff --check` warning; exact approved
source preservation leaves that upstream formatting intact.

## Evidence and limits

`validation-summary.json` binds the observed install, browser, native persistence,
export/import, 17/44/67/72 model tests, and isolated boot/render/readback results.
Layer 5's real Spacedock fixtures cover AC-1 through AC-5, including empty-PATH
standalone drawing, full identity, refusal, archived/reopened tasks, story/task
ratio divergence, pending delivery acceptance, and source-preserving canvas readback.
Its behavior evidence remains applicable because the touched blobs match the
approved original endpoints; the newly run full suite also exercises the seam.

The first clean dependency install added 267 packages; layers 2–5 reuse that
installation through explicit symlinks because their dependency bytes match.
Claude marketplace add/install used an isolated HOME and resolved the advertised
skill path. Native browser proof used dedicated ports and a temporary local proxy;
that proxy blocked external toolbar assets, so the screenshots do not prove final
icon appearance. Native shape rendering, UI color editing, save/reopen after server
restart, `.tldr` round trip, PNG export, and live story editing were observed.
The probe browser and ports were stopped; existing preview listeners were preserved.

The existing path-filtered CI lane is adapted to each layer, with no new lanes or
broader triggers. GitHub Actions cost per PR is **unmeasured**. The two-minute
upstream comment is an estimate and is not measurement evidence.
RoboRev observation is `UNAVAILABLE(reason: unsupported)` with zero requests:
there is no authorized committed product tip for the tree-only candidates.

Temporary snapshot repositories, indexes, dependency symlinks, install-home,
browser proxy, probe rooms, and raw probes exist to verify this recut. They become
removable after approved commits reproduce these trees and independent validation
has retained the required evidence. Preserve originals and existing rooms/services.
Next owner: independent validator reviews intermediate-layer usability and safety;
then Kent reviews exact local commits. The provider PR mod owns the later five-Draft
stack through `gh stack`; existing #394 remains untouched and is not a sixth layer.
