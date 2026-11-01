# Independent validation 3 — PR #759

**PASSED for amendment 1's pre-delivery scope**, exact head `cf8e5848654f03fa5c509751298e2f75d7c151ba`. This repair-only review carries validation-2's unaffected judgments forward as explicitly requested; it does not claim new human adoption, runtime, continuation or sync evidence. Pinned main is `9b32877f4b98583fa41ce090664f20b3ffcae122`, merge-base `9f065b01f1c6d6561793a168f584075edb85bf1f`. Candidate and disposable validation checkouts were verified before work. No product repair, product commit, push, PR mutation or agent launch occurred.

## Scope and carry-forward

`scope.json` establishes exactly one commit since validation-2's head `a8536dc5239edc3db6c1b76cb3bb7e1ce0433088`, touching only `kc-dev-flow-2/scripts/model_roster.py` and `kc-dev-flow-2/scripts/test_sd_dispatch.py`. Inspection confirms the only behavior changes are the explicit-absence author fallback and retaining author evidence when the validator has no configured roster. The rest of the original eight-file candidate is byte-identical, including defaults, roles, instructions, ADR, CI and all unchanged tests.

`carry-forward.json` compares state with validation-2's committed evidence at `b0a3ea5f08e791c7afc9df6b92f08eedbf97df05`: current acceptance criteria and amendment are identical; validation-1, validation-2, adoption-trial, cold-fo and archived batch-9 dispatch inputs have no diff. New implementation-3/4 records are inspected and included in the current author replay. Thus:

- AC-2/3: existing real CLI subprocess fixture and full model-free SD suite freshly pass, including wrong roots, absent defaults, malformed/unsupported data, committed change/deletion and historical stage/effort mapping. Validation-2's unchanged negative/mutation judgments carry forward; this run adds both repair falsifiers below.
- AC-6: package lint, full SD suite, current guards and two-file scope check freshly pass. The prior remaining model-free command entries and their seven existing fixture-dependent skips are carried judgments, not rerun claims. The only changed test entry was rerun completely. Static reading counts and instruction/role/law/native/CI judgments carry forward because those bytes are identical.
- AC-7/8: validation-2's expressly bounded FO-record and runtime-evidence judgments carry forward. Original scratch repositories remain gone; their manifests/commits cannot be re-inspected. No fresh host questions or child-runtime calls were made here.
- AC-9: freshly re-exercised configured/absent authors and validators, legacy/configured/explicit-absence headers, unknown/missing/contradictory records and all actual author records; both defects are repaired. Structural names/folder checks still do not establish roster consumption.

Full real-use sufficiency remains subject to first actual adoption, repository-bound uninterrupted configured launch, Sol/high, unchanged continuation, changed-tuple fresh handoff, committed-file startup/sync preservation and overwrite falsifier. These observations are owed after delivery, neither passed nor waived. Historical validation-1 findings F2–F7 retain their validation-2 dispositions. F1 remains resolved in the current author record/report. Independent validation does not grant merge or delivery authority.

## Repair judgments and falsifiers

| Previously reproduced defect | Fresh evidence | Independent negative control |
| --- | --- | --- |
| An author record with `Roster: absent; source README default` and supported `Model:` lost its known tuple. | Fixed CLI retains the author tuple; configured Astra or Sol validator reports the informational OpenAI family. Unknown, missing or contradictory evidence remains unverified under existing tests. | Restore only the old author branches: exit 1 at the explicit-absence author assertion, tuple null rather than known. Running old-head resolver against new tests also fails there. |
| An absent validator roster returned before collecting supplied author records. | Fixed CLI preserves zero/known/unknown author lists while returning README default/null validator and unverified family. Real assigned-root replay retains all seven actual author records. | Restore the early return alone: exit 1 at the author-retention assertion. Independently remove the configured-validator condition: exit 1 because unknown validator is incorrectly labelled same-family. |

`mutations.json`, individual logs and resolver command logs retain primary evidence. Fixed fixture exits 0; each of four controls exits 1. Every run uses a fresh fixture and Python `-B`; no shared imported resolver cache is used. The first probe wrapper failed to import its sibling `poc_readme`; adding the candidate scripts directory to the wrapper's import path corrected the harness before any judgment. Product files were not changed by that correction.

Both prior findings affected normal FO validation records and candidate-author visibility under `value-ac[AC-9]` and `contract[kc-dev-flow-2/references/model-roster.md#stage-launch-or-continuation]`. They were Material and are now resolved. No new Material, Deferred risk, Polish or Needs decision finding is established. Goal sufficiency holds within the amended pre-delivery boundary; both reversion failures establish the necessity of the repairs, and no unrelated production surface changed.

## Author/family evidence

`actual-author-resolve.json` names implementation-1.md, implementation-1-message-1.md, implementation-1-message-2.md, implementation-2.md, implementation-2-message-1.md, implementation-3.md and implementation-4.md. Each retains Codex/gpt-6.1-sol/high/Paseo. The current dispatch record names all four implementation cycles and its actual validator Model header is Codex/gpt-6-astra/high/Paseo; the follow-ups identify the same worker as their cycle. These recorded models are **same-family: openai**, not provider diversity, and that warning must remain visible at the gate. Distinguish this recorded-model comparison from the resolver's absent-roster result: no configured validator tuple means its `family` is correctly `unverified`. This review does not infer actual runtime from a Model header alone.

## Checks and limits

`acceptance.log` records package lint (workflow 5781/5781 words), real Spacedock 0.27.2 with plugin 0.27.3, all model-free dispatch checks, real resolver replay, ADR lint and cleanup. Full script exited 0 in a fresh `bash --noprofile --norc`; SD test elapsed 47.70 seconds. It does not run skill discovery, model execution, human gates, delivery hook body or remote merge.

`guards.json` records exit 0 for ADR lint against pinned main with and without `--require 0047` (45 records, zero legacy), number guard (no findings, no migrations-path), comment ratio (3/333=0.9%, maximum 5%), design surfaces, all 14 dispatch records, current validation names, and document impact. Scope-history replay is intentionally not run at validation. Added comments were read; the repair adds none. Loaded package is the Codex 0.33.1 installation named by the invoked skill; it takes precedence over the dispatch's Claude-cache spelling.

Document dispositions: ADR 0047 and adoption reference were updated by the original candidate and remain correct, unchanged by this repair; package README is unaffected by the repair and its generic test claims remain valid (two-endpoint comparison with newer main labels it updated); learning.md is unaffected, historical practices unchanged. The existing model-roster reference already requires the restored author behavior, so no documentation repair is needed.

The independent fixed replay records 106 subprocess commands and 52 resolver outputs. `output-ledger.json`: README-default JSON 164–743 bytes/1 whitespace word, configured JSON 292–703 bytes/1–2 words, errors 41–146 bytes/4–14 words for these fixture paths. Counts differ with source-path lengths and JSON error strings; do not replace actual output with design examples. Static lifecycle counts are unchanged from validation-2: startup 9710, idle/open 1821, merged/archive 328, merge ask 2258, workflow 5781, configured/absent dispatch 3154/3110, adoption 2914, plus actual outputs. The implementation's paired 78.474→83.616s local SD sample remains its own noisy measurement, not independently repeated here. Billed CI cost per PR is **not measured**; CI files/triggers are unchanged.

Initial read-only GitHub query confirms PR #759 open, non-draft, main base and this exact head, with four successful checks and unit tests in progress. Final GitHub refresh for #759 and #674 failed with `error connecting to api.github.com`; current all-green CI and #674's current status are unverified. Prior native/director/partner remainder is not closed here. FO supplies `clean on cf8e58486; evidence=roborev:1388` in this dispatch; it supersedes the implementation's earlier daemon-unavailable observation but is FO-supplied review evidence, not a validator rerun.

## Captain acceptance script

No product screen changes; command output is the observable surface. Prerequisites: the stated source repo contains pinned commits; Python 3, Git, Spacedock 0.27.2, plugin 0.27.3, assigned dev2 0.33.1 installation and state author record exist. Creating/removing disposable Git worktrees requires metadata access. Run these six steps together in a fresh Bash shell; exact file `acceptance.sh` was run unchanged and exited 0. It verifies local package/CLI behavior and cannot close post-delivery real-use obligations.

```bash
#!/bin/bash
set -euo pipefail
# 1. Create a disposable exact-head checkout; expect detached cf8e5848.
ROSTER_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo'
ROSTER_HEAD='cf8e5848654f03fa5c509751298e2f75d7c151ba'
ROSTER_BASE='9b32877f4b98583fa41ce090664f20b3ffcae122'
ROSTER_CHECK="$(mktemp -d "$ROSTER_SOURCE/.roster-acceptance3.XXXXXX")/candidate"
git -C "$ROSTER_SOURCE" worktree add --detach "$ROSTER_CHECK" "$ROSTER_HEAD"
cd "$ROSTER_CHECK"
test "$(git -C "$ROSTER_CHECK" rev-parse HEAD)" = "$ROSTER_HEAD"
# 2. Check package instructions; expect PASS and workflow 5781/5781 words.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# 3. Exercise real resolver and model-free dispatch; expect all assertions pass.
TMPDIR=/tmp SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock time -p python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3 --keep
# 4. Check the decision record against pinned main; expect 45 ADRs, zero legacy.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/adr_lint.py docs/adr --since "$ROSTER_BASE" --require 0047
# 5. Observe absent roster with a real author; expect retained Sol/high author, null validator, unverified family.
python3 -B kc-dev-flow-2/scripts/model_roster.py resolve --code-root "$ROSTER_CHECK" --stage validation --author-record /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/model-roster-per-repo/dispatch/implementation-4.md
# 6. Check untouched candidate and remove this disposable checkout; expect exit 0.
test -z "$(git -C "$ROSTER_CHECK" status --porcelain)"
cd /tmp
git -C "$ROSTER_SOURCE" worktree remove "$ROSTER_CHECK"
rmdir "${ROSTER_CHECK%/candidate}"
```

Expected and observed output:

1. `Preparing worktree (detached HEAD cf8e58486)`; full-SHA assertion passes.
2. `PASS: basic frontmatter, declared profile routes, role bindings and package script paths`; workflow `5781 of 5781 words`.
3. Roster subprocess replay and all model-free SD dispatch assertions pass; `real 47.70`. Full output retained in acceptance.log, including explicit non-run boundaries.
4. `45 ADR file(s) checked, 0 legacy`; exit 0.
5. `source=readme-default`, `tuple=null`, `digest=null`, `family=unverified`, commit `cf8e5848654f03fa5c509751298e2f75d7c151ba`; one implementation-4.md author with Codex/gpt-6.1-sol/high/Paseo.
6. Clean assertion and removal of the script-owned checkout succeed, exit 0.
