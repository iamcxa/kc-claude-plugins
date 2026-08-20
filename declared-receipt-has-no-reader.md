---
id: q0z8h3xny0qxv0r5srter8tj
title: Conditional-reference receipt and trigger declarations are read by nothing
status: validation
source: adopter field report on kc-dev-flow 3.0.0, filed as issue #256 (2026-08-19); confirmed on origin/main and the current branch before filing
product: kc-dev-flow
sprint:
started: 2026-08-20T13:52:18Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-declared-receipt-has-no-reader
issue: 256
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:q0z8h3xny0qxv0r5srter8tj:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:q0z8h3xny0qxv0r5srter8tj-backlog-1
              briefing:
                id: briefing:q0z8h3xny0qxv0r5srter8tj:backlog:attempt-1:revision-1
                digest: sha256:b29f07c33f960893825b1e55a02b9f11e3527102175446986dc91ef5e313029b
                request-digest: sha256:916b5961b8f51a1d9210c5dc0be4c24ac424c1f737c87da4d03dab1bc98a2c99
                room-ref: ./declared-receipt-has-no-reader/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:q0z8h3xny0qxv0r5srter8tj:backlog:1
                briefing: briefing:q0z8h3xny0qxv0r5srter8tj:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-20T13:51:10.945911Z"
                decision: approve
                reason: 'Captain answered ''1'' to the gate question, selecting direction 1: the loader emits the selected stage''s declared receipt names and the reference states the bounded guarantee. Production profile accepted per published-contract precedent; the v2 receipt is committed and parses under the profile contract loader.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:q0z8h3xny0qxv0r5srter8tj:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:q0z8h3xny0qxv0r5srter8tj-ideation-1
              briefing:
                id: briefing:q0z8h3xny0qxv0r5srter8tj:ideation:attempt-1:revision-1
                digest: sha256:04a602dbdccf4a576fcc9dbf8879869915ed578010d96e3c40e9be936e4a5ace
                request-digest: sha256:3c566f4bdabf44e70b73b8d7c31655b8cd11404c3a417dbf6b8772a609657edb
                room-ref: ./declared-receipt-has-no-reader/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:q0z8h3xny0qxv0r5srter8tj:ideation:1
                briefing: briefing:q0z8h3xny0qxv0r5srter8tj:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-20T14:24:32.563102Z"
                decision: approve
                reason: 'Captain approved the ideation shape. Reverse-recovery audit fired with decision build; outcome scoped to the selected stage contract''s non-null receipts only; three acceptance-evidence checks named, two RED today. FO independently verified --format json, the 9-contract declaration set with no kernel/base declarations, declared_receipts absent from the loader, and the cited path fail-closed tests at profile-contract-loader.test.py:305-429. Accepted residual: declared_receipts ships with no consumer, which the chosen direction and the bounded docstring guarantee make explicit.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:q0z8h3xny0qxv0r5srter8tj:validation
          stage: validation
          attempts:
            - id: gate-attempt:q0z8h3xny0qxv0r5srter8tj-validation-1
              briefing:
                id: briefing:q0z8h3xny0qxv0r5srter8tj:validation:attempt-1:revision-1
                digest: sha256:5070851c4e3ad4082a0b3a1bc3429f01475d133ca95b1440d74511370562a924
                request-digest: sha256:ff9bafb9434c23ba274f12a02ff072a36c3b505e5f253c001c8117b973e06352
                room-ref: ./declared-receipt-has-no-reader/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:q0z8h3xny0qxv0r5srter8tj:validation:1
                briefing: briefing:q0z8h3xny0qxv0r5srter8tj:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-20T14:47:36.985953Z"
                decision: approve
                reason: 'Captain approved validation at 758c2a70. All three acceptance-evidence items were independently reproduced, not re-read: both mutants recreate their reported failures and are caught only by the isolation assertion, the path fail-closed cases at 305-429 are untouched in a pure-addition test diff, and the byte-parity assertion was proven live by a deliberate tamper-and-restore. The docstring''s three absolutes each trace to a code fact. FO confirmed the worktree clean at 758c2a70 with parity intact. The contract test''s sole failure is pre-existing and now tracked as spacedock-route-test-passes-nowhere.'
              application:
                target-stage: release
                state: pending
---

## Problem

Every stage contract in `kc-dev-flow/references/profiles/**` declares a
`kc-dev-flow-conditional-references/v1` block whose entries carry `path`,
`trigger`, and `receipt`. `scripts/profile-contract-loader.py`
(`check_conditional_references`) reads only `path`, and fails closed when the
named file is not vendored. `trigger` and `receipt` are consumed by nothing —
not the loader, not a skill, not a script. A stage can therefore complete having
produced no `reverse_recovery`, `journey_slices`, or `project_context` receipt
and the route still reports success. The asymmetry is the defect: the same block
enforces one field rigorously and ignores the other two, so a field that names an
obligation reads as a guarantee while providing none.

Confirmed present at `kc-dev-flow-v3.0.0`, on `origin/main`, and on the current
branch: 9 contracts declare receipts; the loader's only entry read is
`entry["path"]`.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: production
  recommended: production
  basis: "A marketplace-published plugin contract consumed by external repositories at a pinned release tag. The change alters the loader's output shape and the conditional-reference reference text, so every adopter reads it at their next pin; it carries compatibility and release obligations and no operational runtime."
  route: [shape, build, verify, release]
  obligations:
    architecture:
      - "Keep the declaration block's schema stable; add a reader for the already-declared `receipt` field rather than a new field or a second declaration surface."
      - "Do not make `trigger` evaluable and do not add a stage-exit enforcement check; that is a separate, larger decision the Captain declined at this gate."
    implementation:
      - "Emit the selected stage's declared receipt names in the loader's JSON output so a caller can read them without re-parsing contracts."
      - "State in the conditional-reference reference exactly what the loader guarantees and what it does not, so the field stops reading as an enforced obligation."
    testing:
      - "A loader test that fails when the declared receipt names are absent from the JSON output, and one that fails when they do not match the selected stage's declarations."
      - "The existing `path` fail-closed behavior stays proven by its current tests."
  scope_boundary: "Excludes evaluable triggers, stage-exit receipt verification, any standing enforcement gate, and any change to which references each contract declares."
  promote_when:
    - "The Captain accepts that a missing receipt must block a stage, not merely be observable."
    - "An adopter needs the receipt names before the loader runs, which would move the declaration out of the contract body."
  decision:
    authority: person:captain
    at: 2026-08-20T13:50:38Z
```

## Shape — reverse recovery

`brownfield_capability_change` is true: this work adds a reader for the already-declared
`receipt` field inside an existing `kc-dev-flow-conditional-references/v1` declaration block.
Audit per `references/reverse-recovery-audit.md`.

```yaml
reverse_recovery:
  trigger: add a reader for the already-declared `receipt` field to an existing conditional-references declaration block
  boundary: >-
    Journey — a caller of profile-contract-loader.py's JSON output learns which receipt
    obligations the selected stage declared, without re-parsing the stage contract's own
    conditional-references block. Searched kc-dev-flow/scripts (the loader and its test file),
    kc-dev-flow/references (kernel.md and every profiles/*/*.md), kc-dev-flow/skills
    (adopt-dev-flow, continue-dev-flow), and kc-dev-flow/README.md for any existing reader or
    consumer.
  layers:
    - surface: declaration (entry.receipt in each stage contract's JSON block)
      location: "kc-dev-flow/references/profiles/{profile}/{stage}.md — 9 contracts, e.g. production/shape.md:19,24,29,34"
      completeness: WORKING
      need: REQUIRED
      evidence: 9 contracts declare a `receipt` string or null per entry; all parse under check_conditional_references today.
      disproof_hook: profile-contract-loader.test.py's existing JSON-parse tests failing
    - surface: reader (code that accesses entry["receipt"])
      location: "MISSING — scripts/profile-contract-loader.py:137-160 (check_conditional_references) destructures only entry[\"path\"]"
      completeness: MISSING
      need: REQUIRED
      evidence: >-
        Two strategies: (1) grep -n "receipt" scripts/*.py outside the test file — every hit is the
        unrelated `## Work profile receipt` / `receipt_route` frontmatter concept, none is
        entry["receipt"]; (2) read check_conditional_references top to bottom — the per-entry loop
        binds only `declared_path = entry["path"]`.
      disproof_hook: check_conditional_references branching on entry.get("receipt")
    - surface: output field (a receipt-name key in load_contracts()/render_text() JSON)
      location: "MISSING — scripts/profile-contract-loader.py:199-234 (load_contracts, render_text)"
      completeness: MISSING
      need: REQUIRED
      evidence: the returned dict's keys are schema/work_item/.../profile/.../loaded; no receipt-name field exists.
      disproof_hook: json.loads(loader --format json output) missing the new key today
    - surface: downstream consumer of declared receipt names
      location: MISSING
      completeness: MISSING
      need: NO_OBSERVED_CONSUMER
      evidence: >-
        Two strategies: (1) grep -rn "declared_receipts\|receipt_names" kc-dev-flow — zero hits; (2)
        grep -rln "profile-contract-loader" kc-dev-flow/**/*.md — only README.md,
        adopt-dev-flow/SKILL.md, and the loader's own test reference it, and none reads a
        receipt-name field from its output. Not searched: any adopter repo outside this workspace.
      disproof_hook: a grep hit for a caller reading a receipt-name key from the loader's JSON output
  decision: build
```

The reader and the output field are genuinely `MISSING`, not `EXISTS_BROKEN` or `STUB` — there is
no prior attempt to recover, and no working mechanism elsewhere already does this. `build` matches
the backlog gate's already-selected direction: add a reader to the existing declaration block, not
a new field or a second declaration surface. The `NO_OBSERVED_CONSUMER` layer is expected, not
disqualifying — the whole defect this work item reports is that nothing reads `receipt` yet; this
task builds the first reader, it does not require a pre-existing caller.

## Accepted outcome and non-goals

**Outcome**

- `profile-contract-loader.py`'s `--format json` output gains a `declared_receipts` field: an
  ordered list of the non-null `receipt` strings declared by the loaded **stage** contract's
  (`profiles/{profile}/{logical_stage}.md`) `kc-dev-flow-conditional-references/v1` block only —
  matching the backlog gate's resolution wording, "the loader emits the selected stage's declared
  receipt names." `null` receipts (e.g. `retained-document-policy`) are excluded, not emitted as
  `null` entries. `kernel.md` and `base.md` never declare that block today (confirmed: only the 9
  stage files do); if a future one of them does, its receipts do **not** feed `declared_receipts` —
  that would be a scope change to which loaded file counts as "the selected stage," a separate
  decision if it is ever proposed, not an automatic consequence of this reader.
- `check_conditional_references`'s docstring in `scripts/profile-contract-loader.py` states the
  exact bounded guarantee: the loader surfaces which receipt names the selected stage declares in
  its output; it does **not** verify a receipt was produced, does **not** evaluate `trigger`, and
  does **not** block a stage that completes without one. `declared_receipts` is an observability
  aid for a caller (e.g. a first-officer stage-report check) — presence in that list is not proof
  of an emitted artifact.

**Non-goals** (mirrors the work-profile `scope_boundary`)

- No evaluable `trigger` — the field stays descriptive text, not a condition the loader runs.
- No stage-exit receipt-verification gate or other standing enforcement.
- No new declaration field and no second declaration surface — the reader consumes the existing
  `receipt` key already present in all 9 contracts.
- No change to which references each contract declares.

## Acceptance evidence

- A loader test in `profile-contract-loader.test.py` that builds a stage contract declaring a
  `kc-dev-flow-conditional-references/v1` block with a named `receipt`, loads it with
  `--format json`, and asserts that name is present in `declared_receipts` — RED today (the key is
  absent from the output entirely), GREEN once the reader exists.
- A loader test that builds two stage contracts with different receipt sets (including one with a
  `null` receipt) and asserts the JSON output's `declared_receipts` matches only the selected
  stage's own non-null declarations — catches a reader that flattens receipts across every loaded
  file (kernel.md + base.md + stage.md) or hardcodes a list instead of deriving it from the
  selected stage's block, and catches a reader that leaks `null` into the list.
- The existing `path` fail-closed tests (unvendored reference, absolute path, root-escaping path —
  `profile-contract-loader.test.py` lines ~305-429) stay green unmodified, proving the new reader
  is additive and does not relax the existing presence check.

## Measurement

No operational runtime — the work-profile basis already states this: a marketplace-published
contract read at adopters' pinned tags, not a running service. Acceptance evidence above (the
loader's own test suite) is the verification; no post-release metric applies.

## Stage Report: ideation

- DONE: Accepted outcome names exactly what the loader will emit and the exact bounded guarantee the conditional-reference reference will state — not a restatement of "make receipts observable".
  `## Accepted outcome and non-goals` names the `declared_receipts` JSON field (ordered, non-null-only, scoped to the selected stage contract) and the exact guarantee text for `check_conditional_references`'s docstring: surfaces receipt names, does not verify, evaluate `trigger`, or block.
- DONE: Acceptance evidence names a check that can fail: a loader test that goes red when the declared receipt names are absent from the JSON output, and red when they do not match the selected stage's declarations.
  `## Acceptance evidence` names two new `profile-contract-loader.test.py` cases (presence RED→GREEN; cross-file/null-leak isolation) plus the existing `path` fail-closed tests staying green as a non-regression check.
- DONE: The reverse-recovery conditional reference fires (this adds a reader to an existing declaration block) — record its audit result, or record the evidence that it does not apply.
  `## Shape — reverse recovery` records the fired audit: reader and output field both classified `MISSING`/`REQUIRED` (two search strategies each), consumer classified `MISSING`/`NO_OBSERVED_CONSUMER` (expected, since this task builds the first reader), decision `build`.

### Summary

Filled the ideation stage's three required sections for the Production route: reverse-recovery audit (fired, decision `build`), accepted outcome + non-goals scoped to the backlog gate's selected direction (a `declared_receipts` JSON field plus a docstring guarantee, no evaluable trigger, no enforcement gate), and falsifiable acceptance evidence for the build stage's TDD loop. No code changed at this stage — the loader, its test file, and the referenced audit doc were read for evidence only.

## Stage Report: implementation

- DONE: Both named loader tests are written first and observed RED against the current loader before the reader exists — record the RED output in the stage report, not just the eventual green.
  Added the presence test and the isolation test to `kc-dev-flow/scripts/profile-contract-loader.test.py` before touching `profile-contract-loader.py`; running it against the unmodified loader produced `profile contract loader test: declared_receipts did not surface the stage's own receipt name: None` (exit 1) — the presence test failing because the `declared_receipts` key was entirely absent from the JSON output.
- DONE: declared_receipts derives from the selected stage contract's own conditional-references block only and excludes null receipts; a reader that flattens across kernel/base/stage or leaks null must fail the isolation test, and the existing path fail-closed tests at profile-contract-loader.test.py:305-429 stay green unmodified.
  `check_conditional_references` now returns each contract's own non-null `receipt` strings; `load_contracts` captures that return value only for `paths[-1]` (the selected stage file), so kernel.md/base.md receipts never reach `declared_receipts`. The isolation test gives kernel.md and base.md their own conditional-references block with distinct receipts and the stage file a non-null plus a null receipt, then asserts `declared_receipts == ["stage_receipt"]`. `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` now prints `profile contract loader test: PASS`; lines 305-429 (unvendored/traversal/absolute/malformed fail-closed cases) are untouched in the diff. Mutation-tested the isolation test's must-fail power (each applied to the real loader file, then `git restore`d): (1) flattening mutant — replaced the `if path == stage_path` scoping with `declared_receipts.extend(receipts)` for every loaded file — failed with `['kernel_receipt', 'base_receipt', 'stage_receipt']`, i.e. the presence test alone did not catch it, the isolation `require` did; (2) null-leak mutant — dropped the `isinstance(receipt, str)` guard so every entry's receipt is appended unconditionally — failed with `['stage_receipt', None]`, again caught only by the isolation `require`.
- DONE: check_conditional_references' docstring states the bounded guarantee (surfaces the declared names; does not verify a receipt was produced, does not evaluate trigger, does not block a stage), and `python3 scripts/kc-dev-flow-contract-test.py` passes — it enforces byte-identical parity with the vendored docs/dev/_mods/profile-contract-loader.py, so the plugin copy and the adopted copy must move together.
  Docstring added: "this surfaces which receipt names this contract's own `kc-dev-flow-conditional-references/v1` block declares. It does not verify that a receipt was produced, does not evaluate `trigger`, and does not block a stage that completes without one." The vendored copy was made byte-identical (`diff kc-dev-flow/scripts/profile-contract-loader.py docs/dev/_mods/profile-contract-loader.py` empty). Residual: in this environment `python3 scripts/kc-dev-flow-contract-test.py` currently exits non-zero on a pre-existing, unrelated failure in `profile-spacedock-route.test.py` (a live `spacedock status --set` CLI smoke unrelated to conditional-references) — confirmed pre-existing via `git stash` on the unmodified worktree, same failure. Concrete symptom: the installed `spacedock` binary (0.27.0-pre8, resolved from `PATH`) writes `verdict: PASSED` (uppercase) to the entity frontmatter, but the test asserts `"verdict: passed" in updated` (lowercase) — a casing mismatch between the installed CLI and the test's expectation, not anything touched by this stage. That test's own designed behavior is to `SKIP` when no `spacedock` binary is on `PATH`; with `spacedock` excluded from `PATH` (its supported skip path, python3 resolution unaffected) the full script prints `kc-dev-flow contract: PASS`, which is where the byte-identical parity assertion and both new loader tests are proven to run and pass end to end.

### Summary

Added a reader for the already-declared `receipt` field: `check_conditional_references` now returns the contract's own non-null receipt names, `load_contracts` surfaces them as an ordered `declared_receipts` list scoped to the selected stage file only (kernel/base excluded, null excluded), and the docstring states the bounded guarantee. Two new loader tests were written first and observed RED, then GREEN after the reader landed; the existing path fail-closed tests are unmodified and still pass. The plugin copy and the vendored `docs/dev/_mods` copy were kept byte-identical. `kc-dev-flow-contract-test.py` is blocked in this environment by a pre-existing, unrelated live-CLI test failure (confirmed pre-existing, not caused by this change); with that unrelated check skipped per its own designed behavior, the full script passes, including the parity and receipt-reader assertions.

## Stage Report: validation

- DONE: At the exact candidate revision, independently confirm all three `## Acceptance evidence` items: both new loader tests pass, the two mutation results reproduce and are caught only by the isolation test, and the existing path fail-closed cases stay unmodified against the merge base.
  At worktree HEAD `758c2a70` (clean, no diff from the state this report describes): `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` prints `profile contract loader test: PASS` (exit 0). `git diff 5b6b3c4b 758c2a70 -- kc-dev-flow/scripts/profile-contract-loader.test.py` shows a pure 95-line addition after line 450, leaving lines 305-429 untouched. Independently re-applied both mutants from the loader source (backed up first, `cp`-restored after each), re-ran the test file each time, and reverted with `cp` back to the original (confirmed via `git status --porcelain` empty and a follow-up green run): flatten mutant (`declared_receipts.extend(receipts)` unconditionally instead of `if path == stage_path`) reproduced `declared_receipts leaked ...: ['kernel_receipt', 'base_receipt', 'stage_receipt']`; null-leak mutant (dropped the `isinstance(receipt, str)` guard) reproduced `... ['stage_receipt', None]`. Both failure messages come from the isolation `require` only — the presence `require` earlier in the script did not fire for either mutant (its fixture has no kernel/base receipt and no null entry), confirming the isolation test is the sole catch for both.
- DONE: Confirm `scripts/kc-dev-flow-contract-test.py`'s ONLY failure is the pre-existing `profile-spacedock-route` verdict-casing mismatch, and that the parity assertion and both new loader tests actually EXECUTE rather than being skipped.
  With the installed `spacedock` binaries on `PATH` (`~/.local/bin/spacedock` 0.27.0-pre8), `python3 scripts/kc-dev-flow-contract-test.py` fails at exactly `profile Spacedock route failed: ... did not terminalize directly` because the CLI writes `verdict: PASSED` where the test asserts lowercase `verdict: passed`; this is the same route-test file byte-for-byte at the branch's merge-base commit (`git show 5b6b3c4b:kc-dev-flow/scripts/profile-spacedock-route.test.py` diffs empty against HEAD), so the mismatch predates and is untouched by this task's commit. The `run()` helper halts the whole script on first non-zero, and this halt happens strictly after the earlier `run([...profile-contract-loader.test.py...], "profile loader")` call at line 256-259 already returned 0 — so the two new loader tests provably executed and passed before the route-test failure was reached. With both `spacedock` binaries excluded from `PATH` (its own designed SKIP path — confirmed `which spacedock` fails), the full script prints `kc-dev-flow contract: PASS`, proving no other latent failure was hiding downstream. Verified the byte-identical parity assertion is live, not silently skipped: temporarily appended a byte to `docs/dev/_mods/profile-contract-loader.py` (backed up first) and re-ran with `spacedock` excluded — the script failed with `self-adopted profile loader differs from package source`; restored the vendored file and reran clean (`diff` empty, `git status --porcelain` empty).
- DONE: Verify the second half of the accepted outcome by reading the shipped `check_conditional_references` docstring against `## Accepted outcome and non-goals`; no test can own the prose claim, and its absolutes must each name what makes them true in the code.
  The docstring's bounded-guarantee paragraph matches the accepted-outcome wording near verbatim ("surfaces which receipt names ... declares. It does not verify that a receipt was produced, does not evaluate `trigger`, and does not block a stage that completes without one."). `grep -n "does not verify\|does not evaluate\|does not block\|__doc__\|docstring" kc-dev-flow/scripts/profile-contract-loader.test.py scripts/kc-dev-flow-contract-test.py` returns no hits — no test asserts on this docstring text, so no test owns the prose claim; it stands on direct code inspection. Verified each absolute against the function body: `grep -n trigger kc-dev-flow/scripts/profile-contract-loader.py` shows `entry["trigger"]`/`entry.get("trigger")` is never read anywhere in the file (the only two hits are the docstring's own prose), which is what makes "does not evaluate `trigger`" true. `grep -n "raise ContractError"` lists every failure path in the file; none branches on `receipt` or `trigger` presence — all are path-related (unparseable JSON, non-list entries, missing/non-string path, absolute path, root-escaping path, unvendored file) — which is what makes "does not block a stage that completes without one" true. `declared_receipts` is populated purely by appending `entry.get("receipt")` when it is a string, with no I/O check against any external artifact, which is what makes "does not verify that a receipt was produced" true.

### Summary

Independently reproduced all three acceptance-evidence claims from the ideation/implementation stage reports at worktree HEAD `758c2a70`: both new loader tests pass and the diff against the pre-task commit is a pure addition outside lines 305-429; both mutants (flatten, null-leak) reproduce the exact reported failure messages and are caught only by the isolation `require`, not the presence `require`. Confirmed the contract test's single failure is the pre-existing, unrelated `profile-spacedock-route` verdict-casing bug (route-test file byte-identical to the pre-task commit), that this failure sits strictly after the loader tests already ran green, and that with `spacedock` off `PATH` the full script — including the byte-identical parity assertion, verified live via a deliberate tamper-and-restore — passes end to end. Confirmed the docstring's three absolutes ("does not verify", "does not evaluate trigger", "does not block") are each independently true against the actual function body (no trigger read anywhere in the file; no receipt/trigger-conditioned raise; no external-artifact check), and that no test asserts on the docstring text, so the prose claim is not test-owned. No code changes; all findings replicate the candidate's claims with no discrepancy.
