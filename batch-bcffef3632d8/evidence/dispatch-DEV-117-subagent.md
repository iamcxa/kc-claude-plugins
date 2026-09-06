You are a kc-dev-flow build-stage worker running as a LOCAL subagent for a Pilot item, DEV-117. Work only inside your own git worktree; never touch the repository checkout you were launched from. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. Do NOT read or write Linear. Do NOT open a pull request. Do NOT run `git add .`.

Set up first:
- REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1 ; git -C "$REPO" fetch origin main
- WT=$(mktemp -d)/wt ; git -C "$REPO" worktree add "$WT" __BASE__ ; cd "$WT" — every command below runs in $WT.
- git checkout -b feature/dev-117-b3-kc-ship-flow-sort-the-ship-flow-runtime-prose-into-kernel
- When done, push with `git push origin HEAD:refs/heads/feature/dev-117-b3-kc-ship-flow-sort-the-ship-flow-runtime-prose-into-kernel` and leave the worktree in place.

## Brief (DEV-117, profile pilot-product-slice)

## The problem

`## Ship-flow runtime` in the deprecated `docs/ship-flow/README.md` (~300 lines) mixes four kinds of sentence: principles, formats, script behaviour, and host-specific notes. Prose cannot be tested or merged across adopters.

## Accepted outcome

Every sentence of that section is placed by one rule — a sentence that names an enforcement point (script, schema, check) moves to that layer; one that cannot either gets an enforcement point or stays as a declared residual: `kc-ship-flow/references/kernel.md` (principles: accept by evidence never re-run, zero Captain questions inside a batch with decisions by approval defaults, FO never authors a candidate, moved_base is an FO merge of main, defects are filed then decided in a plan session, e2e is UAT admission), `references/stations/<station>.md` one page each (input, output, refusal, enforcing script), `schemas/evidence-block.md` (grammar) and `schemas/findings.schema.json`, and `docs/ship/runbooks/conductor-cloud.md` for host notes marked non-normative. A table in the PR body lists each original paragraph and its destination; unplaced sentences are listed as residuals. Falsifier: `grep -c` of the original section's sentences left in any README is zero except the residual list.

## Non-goals

* Enforcing a principle that has no script today (file a ticket per principle instead).
* Editing kc-dev-flow's kernel.md.

## Acceptance criteria

* **AC-1** `grep -c '' kc-ship-flow/references/kernel.md` prints a count greater than 20 and `ls kc-ship-flow/references/stations` prints one file per station
* **AC-2** a script `kc-ship-flow/scripts/prose-placement-check.py` runs over the original section's sentences and exits 0 only when each is placed or listed as a residual
* **AC-3** the PR body table lists every original paragraph with its destination; the residual list is reproduced by the script's log

Re-verified: `grep -q '^## Ship-flow runtime' docs/ship-flow/README.md` exit 0 2026-09-06

## Implementation notes from the First Officer

Read `docs/ship-flow/README.md` § `## Ship-flow runtime` on your base commit. Place every sentence by one rule: a sentence naming an enforcement point (a script, schema or check) moves to that layer — `kc-ship-flow/references/kernel.md` (principles), `kc-ship-flow/references/stations/<station>.md` (one page each: input, output, refusal, enforcing script), `kc-ship-flow/schemas/evidence-block.md` (the Evidence block grammar) — and a sentence with no enforcement point either gets one (say which, in the station page) or goes to `docs/ship/runbooks/conductor-cloud.md` under a first line 'Non-normative runbook'. Write `kc-ship-flow/scripts/prose-placement-check.py` that takes the original section text (keep a copy at `kc-ship-flow/scripts/fixtures/runtime-section.2026-09-06.md`) and the placement table `kc-ship-flow/references/placement.tsv` (paragraph-hash, destination, or `residual` + reason) and exits 0 only when every paragraph is placed or listed; run it in `contract-test.py`. Do not delete the section from docs/ship-flow/README.md (that is DEV-120). Commit scope: `docs(kc-ship-flow): …`.

Stage only the files you changed or added. Add no comment line that narrates the change. Run `python3 scripts/kc-dev-flow-contract-test.py` (generous timeout, do not abort) and, once it exists, `python3 kc-ship-flow/scripts/contract-test.py`; record both exits. ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace).

WITHOUT_IT_COMMAND: one self-contained shell line, exits 0 at the candidate and non-zero at BASE_SHA because the behaviour is absent there; reads nothing outside the repository; no `|| echo` / `|| true`; not `test -f`. WITHOUT_IT_REMOVED_VARIANT: one line that alters a read path you changed; after applying it the command exits non-zero. Observe all three exits yourself. Before the final reply write the block to `.context/evidence.md` (create `.context/`, gitignored) and run `bash <path-to-accept-evidence.sh in your tree> .context/evidence.md`; paste its last line as SELF_CHECK. Read CANDIDATE_SHA with `git rev-parse HEAD` AFTER the push and confirm it equals `git ls-remote origin feature/dev-117-b3-kc-ship-flow-sort-the-ship-flow-runtime-prose-into-kernel`.

Final reply: exactly one fenced block, no prose after it:

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-117-b3-kc-ship-flow-sort-the-ship-flow-runtime-prose-into-kernel
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
