# Implementation scope stop

No product edits or product commits. The existing three-file boundary cannot safely claim the proposed knowledge predicate is bound to the approval consumed by the locked writer. The First Officer accepted this stop before further implementation.

## Decisive native seam

At upstream base `af70297ddae6ec64444849e8e3fcf57484bc16e1`:

- `internal/gates/operation.go:50-57,522-545` binds a generic Briefing and frozen artifact hashes, with no typed knowledge/no-product delivery semantics. Frozen Git artifacts are useful immutable evidence; inventing a recognized delivery declaration is still new semantics that must be explicitly designed.
- `internal/status/merge.go:438-451` prechecks pending approval, optionally clears mod-block, then calls the gates writer without the prechecked attempt or Briefing digest.
- `internal/gates/delivery.go:26-48,160-206` acquires the entity lock, rereads the current eligible approval, and consumes that approval. Its API has no expected attempt/digest or knowledge-evidence constraint. An approved successor selected between precheck and this lock could differ from the prechecked knowledge authority.
- `internal/gates/io.go:313-369` compares gates and status only; it intentionally preserves other frontmatter/body changes. A prechecked empty PR or no-product assertion is not part of this comparison. General compare-before-replace therefore does not itself enforce the proposed knowledge predicate.
- `internal/cli/help.go:235-272` owns the merge command usage/options. A supported `--delivery knowledge` flag also requires this exact help surface, beyond the three approved files.

Falsifiers for the proposed repair: substitute a different approved attempt after caller precheck; introduce an open PR between precheck and locked write; alter the frozen delivery/evidence artifact; provide a product difference while claiming knowledge. Each must refuse with pending approval and active task unchanged. These are designed tests, not observed current regressions.

## Proposed smallest reshape (not authorized)

Keep one native approval protocol and the same archive/state publisher. Extend the EXISTING `FinalizeTerminalApproval` operation, rather than introducing a second consumer, to accept a knowledge-delivery constraint including the selected attempt ID and Briefing digest. Under its existing lock, compare those exact identities, resolve the frozen approved artifact through existing Git-source validation, require a documented knowledge-only evidence declaration with explicit product scope/base/head and no product difference, and refuse any live PR/sentinel/product commitment. A zero-product claim must be checked against its bound product scope, not accepted as a boolean or arbitrary hash. Absence of a product scope is an explicit typed claim reviewed by the human, not inference from prose.

Reuse Briefing v1 artifacts for the declaration; add no gates frontmatter schema or separate approval receipt. This is new artifact semantics and an extension to the existing locked consumer, which is the explicit route-back condition. Preserve a full entity-byte expectation for the knowledge write so changes to PR/body cannot be retained across that check. Ordinary product delivery continues its existing behavior. Native archive/publish/recovery remains unchanged.

Proposed exact upstream files and estimated gross additions plus deletions:

| File | Estimated gross lines | Purpose |
| --- | ---: | --- |
| `internal/status/merge.go` | 45-70 | Parse explicit route and pass constrained authority to native finalize |
| `internal/status/merge_guard_test.go` | 140-180 | Native positive/refusal/archive/recovery and original-copy cases |
| `mods/pr-merge.md` | 20-30 | Supported knowledge route and evidence contract |
| `internal/gates/delivery.go` (added scope) | 100-140 | Validate exact approval and frozen delivery evidence under existing lock |
| `internal/gates/delivery_test.go` (added scope) | 130-180 | Changed approval, product/PR drift, evidence tamper, single consumption |
| `internal/gates/io.go` (added scope) | 15-25 | Knowledge write compares the whole checked entity snapshot |
| `internal/cli/help.go` (added scope) | 5-10 | Document supported explicit flag |

Estimate: 455-635 gross upstream lines across 7 files; proposed reviewable stop is 7 files / 650 gross lines. This is an estimate, not permission or proof it will fit. The local consumer remains one file / 40 gross lines, applied only after executable proof. Any new schema, additional file, or unresolved product-scope proof returns to design again.

## Original approval and baseline evidence

The original validation Briefing accepts outcome `change`, retained evidence, and owned-resource archival. That semantic human approval persists. Its frozen artifact does not contain a native typed knowledge-delivery declaration; silently adding one would change the Briefing digest, so existing machine-bound authority cannot honestly cover it. The owning First Officer must explicitly bind the corrected declaration through the existing native gate procedure, preserving the old approval as history and deciding whether Kent's existing authorization covers the re-recording. This worker neither rebinds nor promises that new human authorization is unnecessary.

`original-source-hashes.json` captures all 18 files at state HEAD `c0a68624`; `original-readonly-snapshot/` retains byte-identical copies. `copied-original-baseline.json` shows a disposable clone with origin removed: normal guard exits 0 with `signal: blocked`; the explicit route exits 1 with unknown argument. Active task bytes remain unchanged, no archive exists, and original pending approval remains untouched. `scope-stop-readback.json` verifies all real source hashes after the probe. Cloud/provider operations: zero.

`checks.json`: existing focused tests 48 passed, zero failed; full suite interrupted on accepted scope stop; race/gofmt not run because there is no candidate. A local base binary was built and used only for the disposable probe, then removed after retaining its hash. RoboRev observation: UNAVAILABLE, no committed candidate, zero requests. Both exact product diffs are empty (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). No candidate exists for independent review, surface-map acceptance, or required exit tests.
