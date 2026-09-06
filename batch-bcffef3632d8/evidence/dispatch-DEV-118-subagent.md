You are a kc-dev-flow build-stage worker running as a LOCAL subagent for a POC item, DEV-118. Work only inside your own git worktree; never touch the repository checkout you were launched from. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. Do NOT read or write Linear. Do NOT open a pull request. Do NOT run `git add .`.

Set up first:
- REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1 ; git -C "$REPO" fetch origin main
- WT=$(mktemp -d)/wt ; git -C "$REPO" worktree add "$WT" __BASE__ ; cd "$WT" — every command below runs in $WT.
- git checkout -b feature/dev-118-b4-poc-kc-ship-flow-a-batch-×-station-pin-loader-with-its
- When done, push with `git push origin HEAD:refs/heads/feature/dev-118-b4-poc-kc-ship-flow-a-batch-×-station-pin-loader-with-its` and leave the worktree in place.

## Brief (DEV-118, profile poc-exploration)

## The problem

Ship needs the same guarantee dev-flow has — the plugin bytes a batch ran under are pinned by sha256 — but kc-dev-flow's `profile-contract-loader.py` binds profile × dev stage per work item (`kc-dev-flow-stage-pin/v1`), and importing it would couple the two flows the Captain ruled independent. Whether a small standalone loader is enough is an unexecuted assumption.

## Accepted outcome

A POC `kc-ship-flow/scripts/pin.py` that computes a contract digest over the plugin's declared resources, writes `kc-ship-flow-batch-pin/v1` (batch id, station, plugin version, digest, previous station) and refuses a station whose digest or previous station does not match; one test file with a mutation per refusal; a written verdict (proceed / change) on whether the ~200-line standalone shape holds before B5 depends on it.

## Non-goals

* Sharing code with kc-dev-flow's loader.
* Pinning plan-flow schemas by bytes (they are pinned by `schema` string).

## Acceptance criteria

* **AC-1** `python3 kc-ship-flow/scripts/pin.py write --batch <id> --station accepted` prints a `kc-ship-flow-batch-pin/v1` record with a 64-hex digest and exits 0
* **AC-2** `pin.py check` exits non-zero when one declared plugin resource byte changes, and when the previous station in the record is not the expected one (two mutations, both logged in `pin.test.py`)
* **AC-3** `grep -c 'import.*profile_contract_loader' kc-ship-flow/scripts/pin.py` prints 0

Re-verified: `grep -q batch-pin kc-dev-flow/scripts/profile-contract-loader.py` exit 1 2026-09-06

## Implementation notes from the First Officer

This is a POC (profile poc-exploration): the deliverable is `kc-ship-flow/scripts/pin.py` + `pin.test.py` + a written verdict file `kc-ship-flow/references/poc-batch-station-pin.md` (proceed / change, with the measured reasons). Read `kc-dev-flow/scripts/profile-contract-loader.py` for the digest idea only; import nothing from it (AC-3 greps for that). Record shape: schema `kc-ship-flow-batch-pin/v1`, fields batch, station, plugin_version (read from kc-ship-flow/.claude-plugin/plugin.json), contract_digest over a resource list declared in `kc-ship-flow/schemas/resources.json`, previous_station, written_at. `pin.py write --batch <id> --station <name> --pin <path>` and `pin.py check --pin <path> --station <name>`; the station order is dispatched, accepted, reviewed, uat, merged, closed. Two mutations in the test: one resource byte changed → check exits non-zero naming the resource; previous_station wrong → check exits non-zero naming the expected station. Commit scope: `feat(kc-ship-flow): …`.

Stage only the files you changed or added. Add no comment line that narrates the change. Run `python3 scripts/kc-dev-flow-contract-test.py` (generous timeout, do not abort) and, once it exists, `python3 kc-ship-flow/scripts/contract-test.py`; record both exits. ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace).

WITHOUT_IT_COMMAND: one self-contained shell line, exits 0 at the candidate and non-zero at BASE_SHA because the behaviour is absent there; reads nothing outside the repository; no `|| echo` / `|| true`; not `test -f`. WITHOUT_IT_REMOVED_VARIANT: one line that alters a read path you changed; after applying it the command exits non-zero. Observe all three exits yourself. Before the final reply write the block to `.context/evidence.md` (create `.context/`, gitignored) and run `bash <path-to-accept-evidence.sh in your tree> .context/evidence.md`; paste its last line as SELF_CHECK. Read CANDIDATE_SHA with `git rev-parse HEAD` AFTER the push and confirm it equals `git ls-remote origin feature/dev-118-b4-poc-kc-ship-flow-a-batch-×-station-pin-loader-with-its`.

Final reply: exactly one fenced block, no prose after it:

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-118-b4-poc-kc-ship-flow-a-batch-×-station-pin-loader-with-its
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
