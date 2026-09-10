# Corrected five-layer local commit proposal

Status: corrected candidates frozen; focused independent re-review pending.
This replaces the rejected proposal preserved in `initial-rejected/local-commit-review.md`.
No product commit is authorized by this packet. After independent validation, Kent
must approve these exact local commits; push, PR creation/linking, readiness,
merge/release and closing original Draft #394 remain separate actions.

Pinned main: `c9c5752fda853737d4a937ad7f59564c5651ca53`.

Create five new branches in this order, each with the previous approved layer
commit as its parent; layer 1 starts at pinned main. Preserve existing branches
and worktrees. The existing layer-4 stable-ID writeback safety hunk now first lands
in layer 2 and persists through layer 3. Layer 3 equals its original extraction
merge plus only that hunk; final layers 4/5 remain exactly unchanged.

| Layer | Branch | Files | Additions | Deletions | Generated lines (share) |
|---|---|---:|---:|---:|---:|
| 1 | `codex/journey-canvas-base` | 24 | 6023 | 0 | 5309 (88.15%) |
| 2 | `codex/journey-story-map` | 24 | 1079 | 334 | 0 (0.00%) |
| 3 | `codex/journey-release-detail` | 34 | 1966 | 139 | 1 (0.05%) |
| 4 | `codex/journey-story-borders` | 21 | 620 | 375 | 2 (0.20%) |
| 5 | `codex/journey-release-progress` | 10 | 433 | 27 | 0 (0.00%) |

Generated means lockfile and serialized native board data. CI cost per PR is unmeasured; no dependency/version change. Layer 3 retains inherited EOF whitespace.

## Layer 1

Commit subject: `feat(kc-journey-map): add a persistent editable canvas`
Branch: `codex/journey-canvas-base`
Cumulative tree: `feec1a91f7479f9f1ff15b8a0bf8650d86271421`
Patch SHA-256: `22e5f77c9ca5288d55b7dac0f8c09325f23cca9cf8045cb949c996ffc2a57441`

Exact changed files:

- `.claude-plugin/marketplace.json` (+11/-0)
- `.github/workflows/kc-journey-map-tests.yml` (+58/-0)
- `.release-please-manifest.json` (+1/-0)
- `kc-journey-map/.claude-plugin/plugin.json` (+15/-0)
- `kc-journey-map/.codex-plugin/plugin.json` (+32/-0)
- `kc-journey-map/.gitignore` (+9/-0)
- `kc-journey-map/lib/doctor.mjs` (+68/-0)
- `kc-journey-map/lib/journey-export.mjs` (+60/-0)
- `kc-journey-map/lib/journey-tldr.mjs` (+70/-0)
- `kc-journey-map/package-lock.json` (+5309/-0)
- `kc-journey-map/package.json` (+35/-0)
- `kc-journey-map/scripts/canvas-smoke.sh` (+51/-0)
- `kc-journey-map/server/canvas-server.ts` (+114/-0)
- `kc-journey-map/server/client/App.tsx` (+43/-0)
- `kc-journey-map/server/client/index.css` (+6/-0)
- `kc-journey-map/server/client/index.html` (+13/-0)
- `kc-journey-map/server/client/main.tsx` (+10/-0)
- `kc-journey-map/server/client/vite-env.d.ts` (+1/-0)
- `kc-journey-map/server/rooms.ts` (+47/-0)
- `kc-journey-map/skills/kc-journey-map/SKILL.md` (+10/-0)
- `kc-journey-map/skills/kc-journey-map/references/canvas.md` (+25/-0)
- `kc-journey-map/tsconfig.json` (+16/-0)
- `kc-journey-map/vite.config.mts` (+9/-0)
- `release-please-config.json` (+10/-0)

## Layer 2

Commit subject: `feat(kc-journey-map): plan releases on an editable story map`
Branch: `codex/journey-story-map`
Cumulative tree: `9702db9d0b908b03d44e92dcc87ec20a16a61731`
Patch SHA-256: `982e0a558cbbf4ae0996aeca87490491feb6780d5887eb8998c7654b348d6ee1`

Exact changed files:

- `.claude-plugin/marketplace.json` (+5/-6)
- `.github/workflows/kc-journey-map-tests.yml` (+4/-1)
- `kc-journey-map/.claude-plugin/plugin.json` (+1/-1)
- `kc-journey-map/.codex-plugin/plugin.json` (+4/-4)
- `kc-journey-map/lib/fixture.mjs` (+36/-0)
- `kc-journey-map/lib/journey-read.mjs` (+29/-0)
- `kc-journey-map/lib/journey-render.mjs` (+14/-0)
- `kc-journey-map/lib/model.mjs` (+5/-0)
- `kc-journey-map/lib/read.mjs` (+234/-0)
- `kc-journey-map/lib/read.test.mjs` (+123/-0)
- `kc-journey-map/lib/records.mjs` (+138/-0)
- `kc-journey-map/lib/render.mjs` (+47/-0)
- `kc-journey-map/lib/storymap.mjs` (+232/-0)
- `kc-journey-map/lib/storymap.test.mjs` (+95/-0)
- `kc-journey-map/scripts/canvas-smoke.sh` (+42/-12)
- `kc-journey-map/skills/kc-journey-map/SKILL.md` (+18/-2)
- `kc-journey-map/skills/kc-journey-map/references/cell-contract.md` (+24/-0)
- `kc-journey-map/skills/kc-journey-map/references/journey.example.yaml` (+22/-0)
- `kc-team-ops/.claude-plugin/plugin.json` (+2/-5)
- `kc-team-ops/.codex-plugin/plugin.json` (+4/-7)
- `kc-team-ops/README.md` (+0/-2)
- `kc-team-ops/skills/kc-journey-map/SKILL.md` (+0/-125)
- `kc-team-ops/skills/kc-journey-map/references/board-template.html` (+0/-96)
- `kc-team-ops/skills/kc-journey-map/references/cell-contract.md` (+0/-73)

## Layer 3

Commit subject: `feat(kc-journey-map): inspect release details and evidence`
Branch: `codex/journey-release-detail`
Cumulative tree: `1738d173046d750819cd40e8ee838dd3eace114e`
Patch SHA-256: `1e9565322dacf4ba37b84d61446edbbf06d4cc148250378469616816dc255bd0`

Exact changed files:

- `.claude-plugin/marketplace.json` (+4/-2)
- `.github/workflows/kc-journey-map-tests.yml` (+15/-1)
- `kc-journey-map/.claude-plugin/plugin.json` (+6/-2)
- `kc-journey-map/.codex-plugin/plugin.json` (+10/-5)
- `kc-journey-map/lib/doctor.mjs` (+1/-1)
- `kc-journey-map/lib/fixture.mjs` (+18/-6)
- `kc-journey-map/lib/funcmap.mjs` (+97/-0)
- `kc-journey-map/lib/funcmap.test.mjs` (+56/-0)
- `kc-journey-map/lib/journey-contract.mjs` (+24/-0)
- `kc-journey-map/lib/journey-example.test.mjs` (+46/-0)
- `kc-journey-map/lib/journey-lint.mjs` (+28/-0)
- `kc-journey-map/lib/journey-render.mjs` (+19/-9)
- `kc-journey-map/lib/journey-tldr.mjs` (+5/-1)
- `kc-journey-map/lib/lint.mjs` (+71/-0)
- `kc-journey-map/lib/lint.test.mjs` (+140/-0)
- `kc-journey-map/lib/model.mjs` (+21/-4)
- `kc-journey-map/lib/read.mjs` (+94/-12)
- `kc-journey-map/lib/read.test.mjs` (+61/-2)
- `kc-journey-map/lib/records.mjs` (+7/-1)
- `kc-journey-map/lib/release-contract.mjs` (+43/-0)
- `kc-journey-map/lib/release-contract.test.mjs` (+40/-0)
- `kc-journey-map/lib/render.mjs` (+284/-4)
- `kc-journey-map/lib/storymap.mjs` (+50/-2)
- `kc-journey-map/lib/storymap.test.mjs` (+10/-2)
- `kc-journey-map/scripts/canvas-smoke.sh` (+17/-9)
- `kc-journey-map/server/client/App.tsx` (+1/-1)
- `kc-journey-map/server/rooms.ts` (+2/-1)
- `kc-journey-map/skills/kc-journey-map/SKILL.md` (+144/-14)
- `kc-journey-map/skills/kc-journey-map/references/canvas.md` (+210/-18)
- `kc-journey-map/skills/kc-journey-map/references/cell-contract.md` (+113/-24)
- `kc-journey-map/skills/kc-journey-map/references/example/README.md` (+41/-0)
- `kc-journey-map/skills/kc-journey-map/references/example/draw-a-journey.tldr` (+1/-0)
- `kc-journey-map/skills/kc-journey-map/references/journey.example.yaml` (+215/-18)
- `kc-journey-map/skills/kc-journey-map/references/map-from-conversation.md` (+72/-0)

## Layer 4

Commit subject: `feat(kc-journey-map): show release stories with status borders`
Branch: `codex/journey-story-borders`
Cumulative tree: `6b4d5e8a747d9d13a4c8d2a832e0b9395b04beff`
Patch SHA-256: `10f0cb0e337ff1448761c25e251c916fffc7f356138cefaeca2ce923fe523c16`

Exact changed files:

- `docs/dev/ROADMAP.md` (+15/-0)
- `kc-journey-map/lib/journey-example.test.mjs` (+18/-0)
- `kc-journey-map/lib/lint.mjs` (+4/-3)
- `kc-journey-map/lib/lint.test.mjs` (+7/-0)
- `kc-journey-map/lib/model.mjs` (+3/-0)
- `kc-journey-map/lib/read.mjs` (+55/-65)
- `kc-journey-map/lib/read.test.mjs` (+145/-2)
- `kc-journey-map/lib/records.mjs` (+41/-1)
- `kc-journey-map/lib/release-contract.mjs` (+2/-7)
- `kc-journey-map/lib/release-contract.test.mjs` (+7/-0)
- `kc-journey-map/lib/render.mjs` (+83/-208)
- `kc-journey-map/lib/render.test.mjs` (+93/-0)
- `kc-journey-map/lib/storymap.mjs` (+6/-28)
- `kc-journey-map/lib/storymap.test.mjs` (+17/-4)
- `kc-journey-map/server/client/App.tsx` (+23/-1)
- `kc-journey-map/skills/kc-journey-map/SKILL.md` (+3/-3)
- `kc-journey-map/skills/kc-journey-map/references/canvas.md` (+64/-32)
- `kc-journey-map/skills/kc-journey-map/references/cell-contract.md` (+12/-4)
- `kc-journey-map/skills/kc-journey-map/references/example/README.md` (+10/-4)
- `kc-journey-map/skills/kc-journey-map/references/example/draw-a-journey.tldr` (+1/-1)
- `kc-journey-map/skills/kc-journey-map/references/journey.example.yaml` (+11/-12)

## Layer 5

Commit subject: `feat(kc-journey-map): derive release progress from local tasks`
Branch: `codex/journey-release-progress`
Cumulative tree: `cefe085d5d9b12b5679421b5607c808d6989a1b7`
Patch SHA-256: `fbbd75200e81847937597b35f8c1936d7f304d0a5a85caf8986205d1f90069ca`

Exact changed files:

- `kc-journey-map/lib/journey-progress.mjs` (+28/-0)
- `kc-journey-map/lib/progress.mjs` (+97/-0)
- `kc-journey-map/lib/progress.test.mjs` (+174/-0)
- `kc-journey-map/lib/records.mjs` (+23/-5)
- `kc-journey-map/lib/render.mjs` (+17/-13)
- `kc-journey-map/lib/storymap.mjs` (+6/-8)
- `kc-journey-map/skills/kc-journey-map/SKILL.md` (+4/-0)
- `kc-journey-map/skills/kc-journey-map/references/canvas.md` (+16/-1)
- `kc-journey-map/skills/kc-journey-map/references/cell-contract.md` (+10/-0)
- `kc-journey-map/skills/kc-journey-progress/SKILL.md` (+58/-0)

## Evidence

The task state `stack-recut-evidence/correction/README.md` links same-instrument red/green second-ID proofs, distinct-wording controls, source hashes, stale-wording refusal and affected readback/smoke checks. `manifest.json`, `equivalence.json`, and `patch-proof.json` bind the corrected trees. Independent focused validation must pass before this packet is presented for local-commit approval.
