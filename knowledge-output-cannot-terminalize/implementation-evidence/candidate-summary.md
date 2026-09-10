# Partial implementation candidate

The seven authorized upstream files contain the explicit route, constrained native approval consumer, whole-entity comparison, tests, help and mod contract. The local consumer remains unchanged because native archive integration is still failing. This is not implementation completion or permission to use the candidate on the live experiment.

## Executed evidence

- New native journey test first failed on the base at unknown `--delivery` (knowledge-before.stdout); with the candidate it reaches native approval consumption, then fails at the existing archive check (knowledge-archive.stdout).
- candidate-focused.json: 65 passing test events, zero failures, covering existing merged/open/malformed product delivery and gate behavior plus knowledge approval/evidence/product refusals and consumed resume. candidate-cli.json: 20 passing test events, zero failures.
- Final addition binds product.worktree to the exact current entity path; valid and changed-worktree subcases passed at the final diff (final-worktree-binding.stdout). The broader runs preceded this small addition; they are not falsely labeled a new full final-candidate sweep.
- knowledge-archive.json: one failing native integration test. Its raw output reports active status=done, verdict=PASSED, application=consumed, archive=false, followed by the empty-PR archive refusal. The existing consumed-knowledge retry revalidates original approval, digest, immutable evidence, product state, PASSED and completion without another write; this does not bypass archive.
- The first copied-original-candidate.json lacked a required main Git source and is fixture-limited evidence only. copied-original-candidate-bound-roots.json then copied BOTH product/state object stores, removed both origins, and refused the original reason sentinel with the task bytes unchanged. Neither run proves a typed-declaration positive case or authorizes live rebinding.
- original-preserved-cycle-2.json matches all 18 original task/briefing/pin/evidence files. No live approval, cloud resource, installation, product commit, push, PR, external post or provider request occurred.

## Remaining integrated scope

The only additional product file identified is internal/status/mutate.go, specifically runArchive's empty-PR/merge-hook check at base lines 356-366. It must reuse gates verification of the SAME consumed approval, frozen knowledge proof, terminal PASSED state and empty PR, and bind that validated snapshot to the actual bytes moved under native locking/comparison. A generic consumed boolean, force, fake sentinel, policy rewrite, or alternative archive path is insufficient. Existing product archival retains its current rules.

Estimated remaining additions plus deletions: archive owner 20-35; gates shared archive-proof/byte-binding support 25-45; native positive/archive-once/publish-failure resume/conflict/tamper tests 100-160. With the measured candidate in candidate-readback.json, this is roughly 685-790 gross lines overall, not a promise to fit 650. Recommend one reviewed eight-file/850-gross ceiling (original seven plus mutate.go); local consumer remains one file/40 gross after executable proof. No ninth file is proposed. Exact helper details remain implementation work within that bound.

The copied original still requires an explicitly bound declaration via its native gate owner before a positive synthetic replay. Its semantic human archival approval persists; no typed binding is fabricated from that fact. Preserve the old attempt/history and label any future copied-fixture decisions test-only. Publish interruption proof is limited to a clean committed archive whose publication fails, followed by native state commit recovery; the pre-existing hard crash between rename and archive commit is outside this repair.

## Surface mapping and necessity

- internal/status/merge.go: AC-1/AC-2; removing the route returns the observed unknown-argument failure; it selects the exact attempt/digest and uses existing finalize/archive ownership.
- internal/gates/delivery.go: AC-1/AC-2/AC-4; the focused refusal cases fail if exact selection, frozen proof, trunk/no-diff/clean checkout checks or idempotent consumed validation are removed.
- internal/gates/io.go: AC-2; TestKnowledgeWholeEntityExpectation would accept PR/body drift without the checked full-byte expectation.
- internal/cli/help.go: public flag discoverability; no extra command or policy owner.
- mods/pr-merge.md: explains the executable declaration and refuses invented reason sentinels; its named native journey check remains red until archive integration exists.

The installed surface-map checker requires two committed Git objects, so it was not fed a fake candidate revision or an empty HEAD-to-HEAD diff. This manual map names the five non-test surfaces; executable map/exit observation remains unavailable until a permitted exact candidate object exists. RoboRev is UNAVAILABLE with zero requests. Focused gofmt and diff --check passed; full/race/full-tree formatting and the local contract test remain deferred while the known integration failure is unresolved. No CI change or cost claim.
