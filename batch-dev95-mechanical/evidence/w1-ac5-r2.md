You are a kc-dev-flow build-stage worker in a disposable cloud workspace. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. No Linear access. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

## Round 2 of DEV-95 AC-5 — the code was accepted, the Evidence was refused

Round 1's candidate `df43392f77fc753ea721066db14db4a52bcf4e97` on `feature/dev-95-ac5-plan-flow-lint-in-repo` is right: the eight `rule()` calls are byte-identical to v0, the contract-test pin fails closed when `plan-lint.py` is deleted, and `lint` runs offline. Do not change it unless you find a defect.

What was refused is the Evidence block's without-it pair, and the accept station refused it mechanically:

    WITHOUT_IT_COMMAND: python3 scripts/kc-dev-flow-contract-test.py && echo "PASS" || echo "FAIL"

`x && echo PASS || echo FAIL` exits 0 whatever `x` does — the trailing `echo` swallows the exit code — so the pair cannot fail, and run at `BASE_SHA` it exited 0. The station's rule is that `WITHOUT_IT_COMMAND` must exit non-zero at `BASE_SHA` and 0 at the candidate, for a reason connected to the change.

## What to do

1. `git fetch origin feature/dev-95-ac5-plan-flow-lint-in-repo && git checkout -b feature/dev-95-ac5-plan-flow-lint-in-repo-r2 df43392f77fc753ea721066db14db4a52bcf4e97`
2. Re-run the round-1 acceptance criteria as they stand (AC-1 through AC-5 in the round-1 Brief, which you can read at `git show origin/spacedock-state/dev:batch-dev95-mechanical/evidence/w1-ac5.md`). Record the results again; they are the evidence for this round.
3. Produce a valid without-it pair. Constraints, each of which the accept station checks:
   - one shell line, nothing after it — no prose, no `; on candidate ...` commentary; the whole line is executed with `bash -c`
   - no `|| echo`, `|| true`, or anything that masks an exit code
   - exits 0 at the candidate; exits non-zero at `BASE_SHA 1b61997b0ca78a6fbab281447f44a47238a8b524` because the behaviour is absent there, not because a command is missing — an exit of 127 (command not found) or 126 does not count
   - reads nothing outside the candidate tree
   - the removed variant restores or removes every path the command reads
   An acceptable shape here is running `docs/plan-flow/plan-lint.py lint` over a committed fixture and asserting on its output; at `BASE_SHA` the file does not exist, so python exits 2 — that is fine, python itself ran.
4. Run your pair yourself at the candidate and in a worktree at `BASE_SHA`, and record both exits in `WITHOUT_IT_OBSERVED`.
5. Push: `git push origin HEAD:refs/heads/feature/dev-95-ac5-plan-flow-lint-in-repo-r2` (this will be the same commit as round 1 unless you changed code). Read `CANDIDATE_SHA` with `git rev-parse HEAD` after the push and confirm against `git ls-remote origin`.
6. Do NOT open a pull request. Do NOT write to Linear. Commit scope, if you commit anything, is `plan-flow`.

## Final reply: exactly one fenced block

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-95-ac5-plan-flow-lint-in-repo-r2
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: <comma-separated, same as round 1 unless changed>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <one line per changed file: path -> AC-N | proving command | removing command>
WITHOUT_IT_COMMAND: <one line>
WITHOUT_IT_REMOVED_VARIANT: <one line>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
AC-1: ...
AC-2: ...
AC-3: ...
AC-4: ...
BLOCKER: none | <what stopped you and at which step>
```
