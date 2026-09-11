# Current ideation: default Go test exclusion

## Selected case and queue provenance

Select exactly one retained finding, identity `kc-dev-flow:surface-map-default-go-test-exclusion` (the selected finding's stable deduplication key). The First Officer owns queue selection and duplicate suppression; repeated selection of this key resumes the same case rather than starting another. This is a standalone finding, not a new issue or provider-backed receipt.

The First Officer reports live PR-feedback-first review of kc-dev-flow PR 414 at f4b522e49f0776d89b9596db67cd1f6cdb3572c2, PR 413 at 4182710a11dbff4998a41f65f3ce70cb583bf4cf, and PR 321 at abbe926929af915c2bbb8bb243eca0f6e3ac11f2. Each had zero reviewThreads on the complete first page and empty reviews. No actionable feedback was found. Raw PR JSON was not supplied or independently recaptured by this worker; this is explicitly attributed queue evidence, not a raw provider audit.

Issue dispositions, also supplied by the First Officer: 382 continuation fix already incorporated in loader 4.3.0; 393 profile recommendation needs broader behavioral scope; 396 architecture coverage spans multiple contracts; 409 comment-review enforcement/corpus exceeds two files/150 gross. The retained Go exclusion defect is the next bounded eligible finding. No posting or external mutation occurred.

## Observed baseline and provenance

Product baseline: kc-claude-plugins main object `0ec3380f590cbaf5b01ee1c325eb222da99a3c5a`, resolved by immutable object rather than an absent origin/main ref. No root branch or ref was moved. Source read only from the ordinary coordinator checkout; stopped upstream/product repair worktrees were not accessed.

- `kc-dev-flow/scripts/surface-map-check.py`: 278 lines; SHA-256 b3a35b32caed183863e7bff77545c014e6122641512f7b9f47ec2a79ef758757. Line 44 excludes Python/TypeScript test suffixes but omits `_test.go`; line 229 already preserves `--no-exclude` and explicitly mapped-file enforcement.
- `scripts/kc-dev-flow-contract-test.py`: 2,405 lines; SHA-256 c93cacd816020a4458f2154d0f42f6e44dc505c457ade6f010b8cafa45dd0b19. Lines 2062–2065 pin the Pilot's non-test coverage contract; existing surface-map fixture composition begins at 2112 and checks at 2176–2235.
- Pilot build contract: `kc-dev-flow/references/profiles/pilot-product-slice/build.md`, retained as contract-source.md with exact source hash in baseline.json, requires checking every non-test changed file. Both proposed source files match the pinned main bytes.

The worker freshly ran the real checker against two actual disposable Git commits whose only changed path is `internal/task_test.go` containing `package internal`. Evidence is empty and the existing dev-66 work-item fixture selects Pilot. `baseline.json` retains every argv/stdout/stderr/exit and source/runtime path. Default returned 1, missing SURFACE line, where contract expects 0: DEFECT REPRODUCED. The same fixture with `--no-exclude` returned 1 as intended: EXISTING GUARD OBSERVED. No corrected producer was made or tested during ideation.

## Exact proposed implementation

Only two product files, at most 150 added-plus-deleted lines including tests:

1. `kc-dev-flow/scripts/surface-map-check.py`: add the narrow Go `_test.go` suffix to default test exclusions; preserve current explicit-map, `--no-exclude`, production and POC branches. Estimate 2–4 gross lines.
2. `scripts/kc-dev-flow-contract-test.py`: extend the existing real-Git surface-map fixture composition for this case and controls. Estimate 65–115 gross lines. Reuse existing helper/fixture ownership; no new standing helper or file unless that composition demonstrably fails, which is a scope stop.

Estimated total 67–119 gross, measured stop two files/150. This estimate is not a finished diff. No change to evidence grammar, Git-removal policy, doc/help coverage, upstream code, consumer migration, release/install behavior or the stopped repair delivery units.

## Designed falsifiers and execution boundary

Run one manual local attempt using existing-session host workers. Initial implementation budget: 10 active minutes, then report progress or concrete stop; one independent bounded review follows. No automatic case restart or new paid runtime. Ordinary focused edit/test correction may continue only for this case within the two-file/150 limit. Stop on scope growth, unknown ownership, unsafe writes, or a negative control reported as passing.

| Case | Corrected producer expected | Why it matters |
| --- | --- | --- |
| Only internal/task_test.go, default, no mapping | exit 0 with excluded path | Reproduces and fixes the selected failure |
| Normal internal/task.go, default, no mapping | exit 1 missing map | Prevents weakening non-test enforcement |
| Go test with --no-exclude, no mapping | exit 1 missing map | Preserves explicit strict checking |
| Explicitly mapped Go test under default mode | malformed mapping fails; valid mapping passes | Ensures explicit inclusion still checks its obligation/pair |
| Known defective producer negative control | control detects overbroad exclusion | A disposable producer variant excluding all .go must wrongly accept the unmapped normal file, so the expected-refusal control must fail |

The negative-control producer is confined to disposable isolation and is not a proposed product change. Preserve original pinned checker before-results; retest the same actual case with the candidate and record raw after-results. The normal-Go negative control must distinguish a narrow repair from a misleading green result. A fresh reviewer checks exact final diff, these outputs and retained provenance. No product commit until exact-file confirmation; no push/PR/review publication/merge/install/provider/cloud action. Required relevant existing contract checks run at implementation completion; no unrelated full/race sweep is proposed.

## Usage and honest reporting

Actors: First Officer for queue/admission/coordination, current worker for shaping and the dispatched existing-session implementation worker, plus a fresh existing-session reviewer. Each needs a separately attributed input/cached-input/output/reasoning boundary. Current task-window values remain UNKNOWN until a unique source and start/end boundary are established; unavailable values are not zero and no complete-cost or one-million-token budget claim is permitted.

FO supplied one observation from its own rollout at 2026-09-11T07:41:31.063Z: total_token_usage input 2555435, cached input 2384512, output 7313, reasoning 3123. Source: rollout-2026-09-10T16-17-51-01a08a64-fc57-7e82-8424-76541a8fe60a.jsonl. These are unanchored cumulative fields, not attributed Pilot usage or an independently read measurement; cached/reasoning are subsets and must not be added again. Anchor any future delta to the actual latest Captain 「確認」 turn, not lifetime totals or tool-output text. Other actors remain UNKNOWN unless uniquely attributed. No chat, credentials or new accounting infrastructure was exported.

## Current authority and native-state observation

Captain's confirmed local-only scope overrides historical upstream/closure plans. Original/native knowledge terminalization, archive, cleanup and final check remain explicitly incomplete; local replay does not require or imply them. No forced terminalization or invented sentinel.

After the scope amendment, the First Officer reports that native gate consume unexpectedly accepted old ideation attempt 1, consumed it, advanced this task to implementation and pushed state; the native path did not reject the changed scope as stale. This is a relayed observed state transition, not permission for stopped work. This worker did not call gate consume, edit frontmatter/gates/pins or reinterpret the old approval. FO will bind a fresh implementation-stage pin to the current explicit scope before dispatch. Existing reports and pins remain historical.

## Acceptance mapping

AC-1: single selected key and attributed feedback-first queue disposition. AC-2: real default-failure and strict-refusal baseline observed; candidate/negative-control results designed only. AC-3: actor boundaries and usage unknowns recorded without complete-cost claim. AC-4: exact two-file candidate and fresh independent review planned, not performed. AC-5: retain raw report/evidence and explicitly unclosed original/native state. No implementation completion or delivery acceptance is claimed.
