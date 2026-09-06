You are a kc-dev-flow build-stage worker in a disposable cloud workspace. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. No Linear access. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

## Round 5 of DEV-94 AC-2 — the code was accepted, the Evidence was refused; this is the last repair round

Round 4's candidate `e9b04927c24411a57617522ce4d55c32a74ab2f5` on `feature/dev-94-ac2-r4-static-check-weakest-sufficient` does what the Brief asked. The First Officer ran it against the four real blocks: the two good pairs are accepted (one with a WARN), the S29 block is refused on the out-of-tree path, round 3's own block is accepted. Do not change the code.

The Evidence was refused by the accept station itself, and one line in it was false:

- `WITHOUT_IT_COMMAND: python3 scripts/kc-dev-flow-contract-test.py` exits **0** at `BASE_SHA 030a0bb7` — the contract test passes at the base, as it should. The block said `at BASE_SHA -> exit 1`. That did not happen; report only exits you observed, and observe them in a worktree at the base, not by reasoning about what should happen.
- The whole contract test is also the wrong instrument: it proves the repository is healthy, not that the station's behaviour changed. The pair must exercise an acceptance criterion of this item.
- The station on `main` could not extract a path from that command (`AC-3 SKIP`); under your own round-3 rule that is a refusal.

A pair that meets every constraint, using only files that exist at both the base and the candidate:

    WITHOUT_IT_COMMAND: bash scripts/ship-flow/accept-evidence.sh scripts/fixtures/ship-flow/mutant-drop-path.md 2>&1 | grep -q 'WARN'
    WITHOUT_IT_REMOVED_VARIANT: git show 030a0bb763463bed8c97ff1f1af9c00c2565cd5f:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh

At the base the round-3 station REFUSES `mutant-drop-path` and prints no WARN, so the grep exits 1; at the candidate it ACCEPTs with a WARN, exit 0; the variant restores exactly the changed file the command reads. Use it, or an equivalent you have actually run on both sides.

## What to do

- `git fetch origin feature/dev-94-ac2-r4-static-check-weakest-sufficient && git checkout -b feature/dev-94-ac2-r4-static-check-weakest-sufficient-r5 e9b04927c24411a57617522ce4d55c32a74ab2f5`
- Run the pair three ways and record each exit: at the candidate; at the candidate after applying the removed variant (then `git checkout -- scripts/ship-flow/accept-evidence.sh`); in a fresh worktree at `BASE_SHA`.
- Run your own new Evidence block through the candidate's station: `bash scripts/ship-flow/accept-evidence.sh <path-to-your-block>` must print ACCEPT. Paste that last line into `SELF_CHECK`.
- Re-state AC-1 through AC-7 from round 4 (`git show origin/spacedock-state/dev:batch-dev94-ac1-ac2/evidence/worker-evidence-AC2-r4.md`), one line each, unchanged unless you observed otherwise.
- `SURFACE:` one line per file in `FILES`, commands in the slots.
- Push to `refs/heads/feature/dev-94-ac2-r4-static-check-weakest-sufficient-r5` (same commit unless you changed code); read `CANDIDATE_SHA` after the push and confirm against `git ls-remote origin`. Commit scope `ship-flow`. No PR, no Linear.

## Final reply: exactly one fenced block

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-94-ac2-r4-static-check-weakest-sufficient-r5
BASE_SHA: 030a0bb763463bed8c97ff1f1af9c00c2565cd5f
FILES: <comma-separated>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <path> -> <AC-N> | <command> | <command>
WITHOUT_IT_COMMAND: <one line>
WITHOUT_IT_REMOVED_VARIANT: <one line>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
SELF_CHECK: <the station's ACCEPT line on this block>
AC-1..AC-7: <one line each>
BLOCKER: none | <what stopped you and at which step>
```
