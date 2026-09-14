# Kernel necessity audit — FAIL / needs reduction

The final candidate `cefe085d5d9b12b5679421b5607c808d6989a1b7` retains removable implementation and misleading documentation. Prior behavior/safety PASS remains valid historical evidence; it does not satisfy the pinned kernel completion invariant (goal sufficiency AND minimal necessity). All 60 changed paths (+9557/-311 from main) are accounted for in [surface-map.md](surface-map.md). Frozen trees and product files were not edited.

## Concrete reduction proposal

1. Remove the unused `frame` export and its attached restatement comment from `lib/records.mjs`. Eight fixture/example projection cases preserve every schema-valid record property, metadata and sibling order. The same comparison distinguishes a missing-border mutant. Opaque fractional-index suffix bytes are normalized to rank, not ignored as ordering.
2. Remove `@fastify/cors` and its server registration, and the unused direct `typescript` compiler declaration. The tested coherent smaller package also removes `@vitejs/plugin-react` and its Vite registration: real native editing, WebSocket persistence, reload, native serialization and Node REST rendering still work. Removing the React plugin loses developer Fast Refresh, so KEEP it in the recommended bounded repair; its removal is an optional excluded alternative. The tested three-dependency private lock removes six package nodes, adds none, changes no resolved versions; this count does not describe the recommended two-dependency reduction. This is not a clean-install proof; shared node_modules was read-only. React, typed source syntax, Vite, tsx and tldraw remain.
3. Keep the existing schema prevalidation/error boundary for this reduction. Bypassing the duplicate schema pass still rejects invalid records but returns 500. A smaller catch-based prototype restores 400 and atomic mixed-batch rejection, but catches unexpected store failures as client errors and loses multi-error/record-ID diagnostics. It is NOT equivalent; narrow error translation is unverified and not part of this proposal.
4. Correct the concrete false/stale claims and trim duplicated prose listed in [documents-comments.md](documents-comments.md). Do not delete complete documents or historical source. Preserve unique contracts and example reproduction instructions.
5. Recommend three delivery units using existing cumulative trees 2, 4, 5 before the proposed reductions: complete editable planning; optional evidence/detail inspection with status borders; explicit local-task progress. This is a reviewability recommendation, not proof of mathematically minimum PR count. Producer must integrate any approved reduction and regenerate/revalidate candidate trees before a new exact local-commit packet exists.

## Without-it observations

| Mechanism removed | Same check and actual result | Control / falsifier |
|---|---|---|
| SQLite disk persistence | Native hand-authored note disappears after server restart; mutant exit 1 | Original survives restart, exit 0; mutation |
| Renderer-owned reconciliation removals | Deleted story remains after re-render; mutant exit 1 | Original deletes stale story while both preserve hand-authored note, exit 0; mutation |
| Release/unassigned bands | Three named story-map checks fail: missing band/line records and explicit unplaced-story-vanished assertion, exit 1 | Original 3 pass, exit 0; existence disproof |
| Standard child status borders | Actual border colors [] instead of red/violet/green, exit 1 | Original same projection test passes, exit 0; existence disproof |
| Executable-file evidence filter | Prose-only match incorrectly satisfies evidence; expected missing `s-1`, actual [], exit 1 | Original reports missing `s-1`, exit 0; refusal |
| Stable story-ID write selection | Prior initial layers 2/3 edited `a-0` when `a-2` was selected; distinct-wording control passed | Promoted existing safety hunk gives exact `a-2` readback; retained independent initial/rereview evidence, no rerun claimed |
| Progress snapshot/identity/story ratio/derived border/source wording | Six retained producer mutations each exit 1 on actual refresh, archived reader or derived projections | Six relevant final file SHA-256 values exactly match producer candidate manifest; reused evidence, not fresh observations |

Commands: from each scratch plugin, the model probes use `node --test --test-name-pattern=... lib/{storymap,render,lint}.test.mjs`; exact arguments and full outputs are in `model-without-it.json`. Runtime probes use `node <scratch>/persistence-reconcile-probe.mjs <variant> persistence|reconcile` and `node <scratch>/schema-probe.mjs <variant> schema`. Frame probe uses `node <scratch>/frame-removal-probe.mjs`; scripts and exact patches are retained in raw evidence. Restored controls are independent copies of the same final candidate.

Dependency proof kept the actual distinct-origin topology: browser client `http://127.0.0.1:61144`, API `http://127.0.0.1:61141`, no proxy. Native keyboard input persisted through the browser WebSocket and survived reload. Browser cross-origin REST `/health` fetch failed with TypeError, demonstrating CORS was absent rather than hidden by a proxy. The supported Node CLI REST render returned 200 and 263 records. Direct browser REST is therefore a lost capability outside the documented browser-WebSocket/CLI-REST path, not a claim of universal CORS equivalence. Test browser session and both owned listeners were closed.

## Layer comparison

Criterion: a delivery unit should expose one accepted person workflow end to end, have a coherent source-of-truth/safety review, and avoid temporary code that a subsequent unit immediately replaces. Infrastructure ownership can justify a further split; fewer PRs alone cannot.

| Existing cumulative endpoints | Total changed review lines | Largest nongenerated unit | Assessment |
|---|---:|---:|---|
| 1,2,3,4,5 | 10996 | 2104 | Five historical units; separate detail/border implementations create avoidable repeated review |
| 1,2,4,5 | 10286 | 2389 | Four viable with separate infrastructure ownership; 710 fewer lines than five |
| 2,4,5 | 10240 | 2389 | Recommended three: complete planning 2081, inspection 2389, progress 460 nongenerated lines |
| 1,4,5 | 10028 | 3544 | Three with thinner infrastructure first but merges planning and inspection into a larger review |
| 4,5 | 9922 | 4152 | Two loses chosen planning/inspection workflow boundary |
| 1,2,3,5 | 10970 | 2104 | Four by merging borders/progress saves only 26 lines and retains temporary detail rewrite |

These totals compare unchanged validated cumulative trees; reductions above are independent and have not been integrated into a new candidate. The recommended grouping uses repository-native parent-branch PR bases if approved; no branch, commit, PR or provider operation was performed. CI cost per PR is unmeasured. The existing five-commit packet remains withdrawn/held.

## Evidence boundaries and owner decision

AC-1..AC-5 retain independent drawing, full identity/story ratios, honest uncertainty, pending acceptance and explicit refresh/source preservation. Those ACs alone do not establish predecessor necessity; the core runtime mutations above cover the broader accepted canvas/story/evidence seams. Not every helper received an individual mutation: direct callers and unique lifecycle responsibility support the remaining keep decisions, not a claim that every line is irreducible. Alternative framework replacement, narrower schema translation and clean-install behavior were not verified. No new framework or full-suite expansion was attempted.

The First Officer should route the bounded producer reduction while preserving Fast Refresh by default, with Captain disposition of the three-unit topology. The current candidate fails minimal necessity regardless of the topology choice. No further audit repair cycle was started.

Raw observations: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-stack-recut/necessity-audit`. `candidate.json` binds changed files; `variants.json` binds exact removal inputs and outputs. Progress reuse: `../implementation-evidence/{candidate-manifest,mutations}.json`; stable-ID red/green: `../stack-recut-independent-validation/{initial,rereview}`. No hosted/provider or delivery acceptance is claimed.
