You are a kc-dev-flow build-stage worker running as a LOCAL subagent for a Pilot item, DEV-116. Work only inside your own git worktree; never touch the repository checkout you were launched from. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. Do NOT read or write Linear. Do NOT open a pull request. Do NOT run `git add .`.

Set up first:
- REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1 ; git -C "$REPO" fetch origin main
- WT=$(mktemp -d)/wt ; git -C "$REPO" worktree add "$WT" __BASE__ ; cd "$WT" — every command below runs in $WT.
- git checkout -b feature/dev-116-b2-kc-ship-flow-move-the-fourteen-station-scripts-and-their
- When done, push with `git push origin HEAD:refs/heads/feature/dev-116-b2-kc-ship-flow-move-the-fourteen-station-scripts-and-their` and leave the worktree in place.

## Brief (DEV-116, profile pilot-product-slice)

## The problem

`scripts/ship-flow/*` ([accept-evidence.sh](<http://accept-evidence.sh>), [without-it.sh](<http://without-it.sh>), [intent.sh](<http://intent.sh>), [holder.sh](<http://holder.sh>), [fenced-dispatch.sh](<http://fenced-dispatch.sh>), [worker-transcript.sh](<http://worker-transcript.sh>), [open-pr.sh](<http://open-pr.sh>), [disposition.py](<http://disposition.py>), [e2e-cli.sh](<http://e2e-cli.sh>), [e2e-gate.py](<http://e2e-gate.py>), [parse-execute-external.py](<http://parse-execute-external.py>), [uat-doc.py](<http://uat-doc.py>), [notify.sh](<http://notify.sh>), [dev-debrief.py](<http://dev-debrief.py>), [ship-debrief.py](<http://ship-debrief.py>)) and `docs/plan-flow/schema/validate-receipt.py`'s close-receipt half are repo-local; an adopter cannot install them and they are tested only by `scripts/kc-dev-flow-contract-test.py`, which belongs to another flow.

## Accepted outcome

The station scripts and every `*.test.*` move under `kc-ship-flow/scripts/` (git mv, history kept); `kc-ship-flow/scripts/contract-test.py` runs all of them and is what the B1 CI job executes; the ship-flow sections leave `scripts/kc-dev-flow-contract-test.py`; fixtures move to `kc-ship-flow/scripts/fixtures/`. The close-receipt validation stays callable as `validate-receipt.py` but reads `kc-ship-close-receipt.v1.schema.json` from the plugin, while plan-receipt/approval schemas stay in plan-flow and are referenced by their `schema` string only. Falsifier: the moved contract test fails when any one station script is deleted.

## Non-goals

* Changing any station's behaviour.
* Touching plan-receipt / plan-approval schemas (plan-flow owns them).

## Acceptance criteria

* **AC-1** `python3 kc-ship-flow/scripts/contract-test.py` exits 0 on main and its log names every moved station
* **AC-2** `test -e scripts/ship-flow` exits 1 on main
* **AC-3** deleting any one station script makes the contract test exit non-zero (mutation run recorded in the PR body)

Re-verified: `test -f scripts/ship-flow/accept-evidence.sh` exit 0 2026-09-06

## Implementation notes from the First Officer

Use `git mv` for every file so history survives. Move `scripts/ship-flow/*` (all scripts and every `*.test.*`) to `kc-ship-flow/scripts/`, `scripts/fixtures/ship-flow/` to `kc-ship-flow/scripts/fixtures/`, and copy `docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json` to `kc-ship-flow/schemas/` (leave the plan-receipt and plan-approval schemas where they are; ship reads them only by their `schema` string). Write `kc-ship-flow/scripts/contract-test.py` that runs every moved `.test.*` and the ship-flow assertions you cut out of `scripts/kc-dev-flow-contract-test.py`; fix every path inside the moved scripts, tests, fixtures and `docs/ship-flow/flows/*.yaml`. `validate-receipt.py` stays in docs/plan-flow/schema but resolves the close-receipt schema from the installed plugin path first (`kc-ship-flow/schemas/`) and refuses with a named error when absent. Mutation proof for AC-3: delete one moved script, run the contract test, record the non-zero exit, restore it. Commit scope: `refactor(kc-ship-flow): …`.

Stage only the files you changed or added. Add no comment line that narrates the change. Run `python3 scripts/kc-dev-flow-contract-test.py` (generous timeout, do not abort) and, once it exists, `python3 kc-ship-flow/scripts/contract-test.py`; record both exits. ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace).

WITHOUT_IT_COMMAND: one self-contained shell line, exits 0 at the candidate and non-zero at BASE_SHA because the behaviour is absent there; reads nothing outside the repository; no `|| echo` / `|| true`; not `test -f`. WITHOUT_IT_REMOVED_VARIANT: one line that alters a read path you changed; after applying it the command exits non-zero. Observe all three exits yourself. Before the final reply write the block to `.context/evidence.md` (create `.context/`, gitignored) and run `bash <path-to-accept-evidence.sh in your tree> .context/evidence.md`; paste its last line as SELF_CHECK. Read CANDIDATE_SHA with `git rev-parse HEAD` AFTER the push and confirm it equals `git ls-remote origin feature/dev-116-b2-kc-ship-flow-move-the-fourteen-station-scripts-and-their`.

Final reply: exactly one fenced block, no prose after it:

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-116-b2-kc-ship-flow-move-the-fourteen-station-scripts-and-their
BASE_SHA: __BASE__
FILES: <comma-separated>
TESTS: <command> -> exit <code>; <command> -> exit <code>
SURFACE: <path> -> <AC-N> | <command that proves the file earns its place> | <command that removes exactly its contribution>
WITHOUT_IT_COMMAND: <one line>
WITHOUT_IT_REMOVED_VARIANT: <one line>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
SELF_CHECK: <last line printed by accept-evidence.sh>
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: <observed>
AC-2: <observed>
AC-3: <observed>
BLOCKER: none | <what stopped you and at which step>
```
