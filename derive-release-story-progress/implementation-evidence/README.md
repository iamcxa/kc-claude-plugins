# Implementation evidence

Candidate: uncommitted product diff against `bc51b2464659594d3c06806442c77ec15319962b`, branch `codex/journey-progress`. `candidate-manifest.json` pins every product file; its SHA-256 is `f0261937f5c5a92455add6e86215c1a7d2444dec1b6fcd6e3e70bbe537128e99`. The predecessor is preserved. No product file is staged or committed.

## View the isolated fixture

- Partial story map: http://127.0.0.1:3743/?room=progress-mixed&d=v0.0.1.1.page
- Partial release board: http://127.0.0.1:3743/?room=progress-mixed&d=v0.0.1.1.jm-board-R1
- All-done release board: http://127.0.0.1:3743/?room=progress-all-done&d=v0.0.1.1.jm-board-R1
- Durable images: `mixed-storymap.png`, `mixed-board.png`, `all-done-board.png`.

These are disposable examples, not real-project progress or delivery. Partial R1 is 2/3 tasks and 1/2 stories; the mixed model also has an unknown R2 story. The all-done model has two R1 stories and shows 2/2 development-complete, pending delivery acceptance. The saved mixed room includes a native wording edit; its PNG was captured before that edit. The inherited back-to-map hyperlink targets the default frontend 3737; use the direct preview links above for the isolated frontend.

Owned services: frontend 3743 / PID 30751, backend 5863 / PID 30667, started from this worktree. Rooms live only in `.context/progress-probe/rooms`. The disposable Vite configuration in `.context/progress-probe/vite.config.mjs` replaces the client's endpoint in served code with 5863; it does not edit `App.tsx`. The existing 3737 / 3741 / 5858 listeners and existing backend room list matched their pre-check observations. `preserved-services.json` records that comparison. Browser session `journey-progress` was closed.

Scaffolding: keep these two owned services/rooms and `.context/progress-probe` only while candidate review/independent validation needs the preview. Remove them after that review has retained the required PNG/evidence; do not stop the three original services. `node_modules` is an explicit local setup symlink to the predecessor install, excluded from the product manifest; its versions and target are in `dependency-setup.json`. No clean-install claim, new dependency, version, lockfile or CI change. CI cost per PR was not measured.

## Execute the checks

From the worktree root, with the declared dependencies and real Spacedock CLI available:

```bash
node --test kc-journey-map/lib/progress.test.mjs
node --test --test-name-pattern='fresh release boards|editing a release story|same wording' kc-journey-map/lib/read.test.mjs
node --test --test-name-pattern='lintEvidenceNotFound|evidence that greps only in prose|lint rejects unsupported status' kc-journey-map/lib/lint.test.mjs
git diff --check
```

The focused progress test creates a real standalone local workflow and isolated canvas subprocess; it does not substitute a fake task reader. The first successful fixture exposed two actual API differences during implementation: resolved paths can use `/var` while reads return `/private/var`, and all-fields listings fill absent scalar fields with empty strings. The reader canonicalizes compared paths and compares absent/empty scalar values while calculating from the read frontmatter.

`mutations.json` binds six temporarily changed producers to observed failing commands. Removing snapshot pass-through still PATCHed the real canvas, but lost its development label. Dropping either tuple component or substituting task totals failed the ratio assertion. Ignoring derived borders failed red/green/violet expectations. Appending progress to story wording failed source-preserving readback. All mutations were restored before the final green run.

Native editing used the real contenteditable textbox on the release board, then the existing `journey-read.mjs --out` against the original fixture source. `native-edit-proof.json` records that the output bytes differ only by `card: Review required work` becoming `card: Review the required tasks`; authored exists stays exists, derived gap stays red, and no progress fields enter YAML. Before the edit, real `--write` readback reported nothing safe to apply and left source bytes equal. The source/task comparison in the automated CLI test and `all-done-preservation.json` covers reader/render mutation. A later second edit against a source already changed by the first readback correctly produced the existing cross-projection conflict refusal; save-as from the original source supplied the single-edit proof.

`standalone-base-equality.txt` compares drawing-only record properties and sibling ordering against predecessor code for the disposable model. Random tldraw index suffixes were normalized to sibling rank; no other properties were normalized. Empty-PATH drawing also passes while an invalid projection refuses. Focused authored lint retains the executable-symbol versus prose distinction.

## Minimal necessity and scope

- `progress.mjs`: bounded real local reader, strict required mapping and story calculator; tuple/count mutations and malformed fixtures falsify it.
- `journey-progress.mjs`: explicit refresh / optional draw, argument refusal and visible draw-failure observation; actual CLI-to-canvas and unreachable-draw cases falsify it.
- `records.mjs`: shared derived borders, contextual provenance/legend and snapshot lookup; native client synchronization and border mutation falsify it.
- `render.mjs`, `storymap.mjs`: consume the snapshot in both projections, separate proof text, story counts, and sufficient release-label spacing; without-snapshot and wording-leak mutations falsify them.
- `progress.test.mjs`: five focused tests covering the owned reader/calculator and real seams; no broader test harness retained.
- New skill: one home for mapping and explicit refresh/recovery usage. Existing drawing skill: a pointer only. `canvas.md`: projection/readback behavior. `cell-contract.md`: development color and acceptance meaning. Per-section overlap inspection found no copied task list or second tracker.

Comment pass: removed the old story-map release-label comment that restated an authored-only count. Kept the test's prerequisite comment because a missing real Spacedock installation must be visible; no other new code comment block was needed. Drawing-only legend placement and band spacing preserve their predecessor route; extra space applies only with progress. No new abstractions beyond the reader, CLI, and shared presentation helpers; all ten product files map above. Measured scope is 10 changed files, 460 added+deleted lines, and 125 reader+CLI lines, within 10 / 700 / 260 stops.

## Authority and limits

The pinned 4.1.1 Pilot build contract and approved committed entity own this stage. Planning Receipt is absent; no planning provider/comparator was invoked. Project-context impact remains `none`: root PRODUCT.md, ARCHITECTURE.md and CLAUDE.md describe the existing plugin/workflow/provider/delivery boundaries, which this optional local reader leaves intact. The pre-existing journey-plugin catalog omission was not expanded into repair. Exact diff and exercised read-only/standalone behavior support this classification; independent validation still owns its fresh receipt.

RoboRev observation: `UNAVAILABLE(reason: unsupported)`, mode observe, profile pilot-product-slice, provider roborev v0.62.0, reviewer codex / gpt-5.6-terra / medium, minimum severity medium, panel none, timeout 900 s, request cap 1, confirmation cap 1. Actual request/confirmation counts are 0 / 0; no jobs or member states exist and cost coverage is unavailable. Help exposes dirty review, but the pinned exact-input protocol requires a candidate Git tip and Git-object configuration. This authorized uncommitted candidate has no tip object representing its bytes; no canonical provider claim was minted, no unchanged-HEAD review run, and no convenience commit made. Base configuration SHA-256 is `ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1`; the manifest above binds the work handed to independent validation.

Limits: this bounded observation cannot discover work omitted from both the task declaration and metadata, guarantee an atomic filesystem snapshot, establish acceptance/usability/deployment, prove hosted behavior, or claim a clean dependency install. No product commit, push, PR, merge, release, or delivery acceptance is included. The preview services are intentionally live for candidate review; the candidate remains uncommitted for the next independent validation stage.
