# Independent validation of amendment forms and history law

Verdict: PASSED for PR #749 at da5053febb546b2a7cf6ffe676b0d5a8b7e338a4, base 5725d495bb83a17ec13616bb5421bf5ffdc71f70. No Material, Deferred risk, Polish or Needs decision findings were identified. This is Pilot package validation; Captain acceptance and delivery remain pending.

## Minimal acceptance script

No browser surface changes. Requires the named local repository and state history, Python 3, Git, and the declared Codex package 0.33.0; the script creates and removes its own detached checkout. It checks representative structural cases, permitted appends, prohibited edits, missing-evidence behavior, three historical rewrite events and ADR lint. It does not rerun the four-corpus comparison or establish hosted activation, release or acceptance. Git worktree creation needs access to the repository's shared Git metadata; the first sandbox run was refused there, then the unchanged script passed with tool-approved filesystem escalation.

Run unchanged in a fresh shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/captain-amendment-form-checked/validation-1/acceptance.sh
```

Five exact steps, with expected observations in comments:

```bash
#!/bin/bash
set -eu
# 1. Create an isolated checkout of the exact candidate. Expected: the full SHA below.
SOURCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-amendment-form-checked
STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
README=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/README.md
PACKAGE=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0
HEAD_SHA=da5053febb546b2a7cf6ffe676b0d5a8b7e338a4
BASE_SHA=5725d495bb83a17ec13616bb5421bf5ffdc71f70
RUN_DIR=$(mktemp -d /tmp/captain-amendment-acceptance.XXXXXX)
CHECKOUT="$RUN_DIR/code"
git -C "$SOURCE" worktree add --detach "$CHECKOUT" "$HEAD_SHA"
cleanup() { cd /tmp; git -C "$SOURCE" worktree remove "$CHECKOUT"; rmdir "$RUN_DIR"; }
trap cleanup EXIT
cd "$CHECKOUT"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$CHECKOUT" rev-parse HEAD
export PYTHONDONTWRITEBYTECODE=1
# 2. Check amendment forms and dispatch boundaries. Expected: 8 tests, OK.
(cd "$CHECKOUT/kc-dev-flow-2/scripts" && python3 -B -m unittest test_design_surfaces.AmendmentStructureTests test_dispatch_records.AmendmentDispatchFormTests)
# 3. Check committed edits, allowed appends, paths and missing evidence. Expected: 12 tests, OK.
(cd "$CHECKOUT/kc-dev-flow-2/scripts" && python3 -B -m unittest test_laws_check.L3Test)
# 4. Replay the three real rewrites, then lint ADRs. Expected: each exit=1 with an L3 violation; 42 ADR files, 0 legacy, exit=0.
for EVENT in 95fe8ce1bd7ff58798634b733abb4115fecfe23d 16129ea4c1a238dd885e9f08513ce3a52ad27f2d 34c820b5db98d5da119a1b021ce6af45d616acdc; do
  CODE=0
  OUTPUT=$(python3 -B "$CHECKOUT/kc-dev-flow-2/scripts/laws_check.py" "$STATE" --before "$EVENT^" --after "$EVENT" --readme "$README") || CODE=$?
  printf '%s\nexit=%s\n' "$OUTPUT" "$CODE"
  test "$CODE" = 1
  printf '%s\n' "$OUTPUT" | grep -q 'violation: L3 amendment-append-only'
done
python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA"
printf 'adr_lint exit=0\n'
# 5. Confirm candidate unchanged and remove only this checkout. Expected: PASS and no retained checkout.
test -z "$(git -C "$CHECKOUT" status --porcelain)"
cleanup
trap - EXIT
printf 'PASS: acceptance complete; temporary checkout removed\n'
```

Observed output (exit 0, under one minute):

```text
Preparing worktree (detached HEAD da5053feb)
HEAD is now at da5053feb fix(kc-dev-flow-2): validate amendment records and detect committed rewrites
da5053febb546b2a7cf6ffe676b0d5a8b7e338a4
........
----------------------------------------------------------------------
Ran 8 tests in 0.050s

OK
............
----------------------------------------------------------------------
Ran 12 tests in 16.704s

OK
L1 observer-before-sentinel: 0 events judged in 16cd53a64678..95fe8ce1bd7f, 0 violated
L2 dispatch-record-complete: 0 events judged in 16cd53a64678..95fe8ce1bd7f, 0 violated
L3 amendment-append-only: 1 events judged in 16cd53a64678..95fe8ce1bd7f, 1 violated
violation: L3 amendment-append-only old=read-adr-honors-adr-folder.md new=read-adr-honors-adr-folder.md amendment=1 commit=95fe8ce1bd7f metadata changed (old lines 198-202)
exit=1
L1 observer-before-sentinel: 0 events judged in 1e17be9a0734..16129ea4c1a2, 0 violated
L2 dispatch-record-complete: 0 events judged in 1e17be9a0734..16129ea4c1a2, 0 violated
L3 amendment-append-only: 1 events judged in 1e17be9a0734..16129ea4c1a2, 1 violated
violation: L3 amendment-append-only old=reused-worker-dispatch-leaves-a-record.md new=reused-worker-dispatch-leaves-a-record.md amendment=1 commit=16129ea4c1a2 Superseded text changed or invalid append (old lines 82-101)
exit=1
L1 observer-before-sentinel: 0 events judged in 16129ea4c1a2..34c820b5db98, 0 violated
L2 dispatch-record-complete: 0 events judged in 16129ea4c1a2..34c820b5db98, 0 violated
L3 amendment-append-only: 1 events judged in 16129ea4c1a2..34c820b5db98, 1 violated
violation: L3 amendment-append-only old=fo-interviews-extension.md new=fo-interviews-extension.md amendment=1 commit=34c820b5db98 metadata changed before unmatched fence (old lines 301-346)
exit=1
42 ADR file(s) checked, 0 legacy
adr_lint exit=0
PASS: acceptance complete; temporary checkout removed
```

## Complete proof and limits

- Independently reran the three VALIDATION.md suite commands with all declared replay inputs: 202 design-surface tests, 61 dispatch tests, 57 laws tests, no skips. `design.log`, `dispatch.log`, `laws.log` retain stdout/stderr. The four pinned repositories are declared in `corpora.json`; base scripts were exported from the exact base using `git archive`, and candidate scripts came from a clean detached checkout.
- `historical-laws.json`: three actual parent/event ranges move from base exit 0 to candidate exit 1 with a protected-byte violation. Historical parser tests export full event trees and referenced artifacts; single-field corrections remove only their corresponding form diagnostic. The Feedback Cycles snapshot and unmatched Design fence are included.
- `mutations.json`: ten cache-free source mutants each exit 1 with assertion failures, no runtime errors. `ac5-falsifier.log` deliberately changes the expected corpus size and fails 174 != 175; `ac6-falsifier.log` adds instruction words in a disposable package and fails the measured reading total.
- `corpus-verdicts.json.gz` holds all 988 full/seed/dispatch mode rows for 448 files; `corpus-differences.json.gz` holds 54 differences across 32 files. Decompress with `gzip -dc <file>`. Independently inspected committed headings and Supersedes values for every changed file in `corpus-review.json`: prose, missing metadata, misplaced/malformed headings or duplicate numbers explain each difference. All 32 files match VALIDATION.md's list; no seed verdict changes. Changed success output, override notes and screen summaries disappear because the full check now refuses the malformed form; old move/replacement diagnostics disappear where prose is no longer parsed as a valid list. These are consequences of the explicit structural refusal, not missing files or semantic classification.
- `reading.json`: unchanged lifecycle totals 6959 / 862 / 833 / 333 / 2408; optional feedback startup 7558. Historical L3 output is 21 / 25 / 24 words including nine-word summaries. Instructions, workflow, version and CI trigger bytes are unchanged.
- `checks.json`: exact-head ADR lint exit 0 (42 records, 0 legacy), number guards exit 0 (migration portion not applicable), comments 0/684 = 0.0% (maximum 5%), complete four-record dispatch folder, document impact and diff whitespace checks exit 0. Repository lint also passed: workflow 5754/5754 words, declared routes and paths valid. Registry parity is part of the laws suite. No new ADR is required or reserved; existing ADRs remain unchanged.
- Affected documents: laws.md updated; ADR 0041 unaffected because seed admission is unchanged; learning.md unaffected because its existing history-input, output-consumer and corpus practices were applied, not amended. No changed diagram needs a render.
- Goal sufficiency/minimal necessity: the shared parser and its dispatch consumer catch actual recorded form failures; L2 classification prevents those failures becoming unknown output; L3 reuses the existing range walker to detect the three actual rewrite events. Their deletion/regression mutants fail. Tests and two evidence/reference documents account for the remaining approved files; no extra runtime mechanism or lifecycle invocation was introduced.
- First Officer supplied exact-head RoboRev evidence `roborev:1324` clean and four passing hosted checks (multi-profile route gate, unit tests, version parity, GitGuardian). These are attributed evidence, not independently queried provider results. The sibling validation-rerun task stacks on this candidate; its behavior is outside this verdict.
- Confirmed deployed state workflow still pins package 22219a3e4bc48a69a893bd757923e8c034d1ba6e. The local command replay does not activate that pin. Published-package adoption and an observed state-push execution remain required for hosted enforcement; CI cost per PR is unmeasured and the trigger is unchanged.
- Accepted limits retained: no skipped-ruling discovery, initial quote-fidelity judgment, semantic omitted-id detection, pre-push blocking, automatic repair or permanent-red guarantee. Range proof excludes merge commits themselves, prior pushes, rewritten history and uncommitted edits. Scope-history notes in frozen archive exports are identical for base/candidate; separate full-history replays supply event proof. The selected profile introduces no production obligation.
