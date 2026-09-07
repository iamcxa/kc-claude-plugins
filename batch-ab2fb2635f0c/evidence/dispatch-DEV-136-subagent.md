You are a kc-dev-flow build-stage worker running as a LOCAL subagent for a Pilot item, DEV-136, in iamcxa/qnow. Work only inside your own git worktree; never touch the clone you branch from. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. Do NOT read or write Linear. Do NOT open a pull request. Do NOT run `git add .`. Never run `acceptance:hosted:full-run` or anything that deploys or contacts a provider — only the credential-free commands named below.

Set up:
- REPO=/Users/kent/conductor/repos/qnow ; git -C "$REPO" fetch origin main "+refs/heads/spacedock-ensign/qnow-next-hosted-staging-qualification:refs/remotes/origin/spacedock-ensign/qnow-next-hosted-staging-qualification"
- WT=$(mktemp -d)/wt ; git -C "$REPO" worktree add "$WT" __BASE__ ; cd "$WT" ; git checkout -b feature/dev-136-land-the-hosted-runners-supporting-files-on-main-netlify
- Read CLAUDE.md, AGENTS.md and experiments/netlify-refine-poc/AGENTS.md first. Source of the files: `origin/spacedock-ensign/qnow-next-hosted-staging-qualification` (the qualification branch, 48 commits ahead of main). Bring files over with `git checkout origin/spacedock-ensign/qnow-next-hosted-staging-qualification -- <paths>` (or cherry-pick when a commit is clean), never by merging the branch. Do not carry files the 84-cycle record marks superseded (cycle-77 runner-only logic, temporary /tmp runners).

## Brief (DEV-136)

## The problem

The hosted acceptance runner (`experiments/netlify-refine-poc/qnow-next/hosted/`, 26 files) and the rest of the staging-qualification work (48 commits, 92 files: 38 test files, netlify/ config, identity/, local/, one schema, one db, one api file) live only on `spacedock-ensign/qnow-next-hosted-staging-qualification`; main has none of it (0 files under hosted/). DEV-36 (#1174) is based on that branch and DEV-37 cannot run from main. Captain's rule (2026-09-07): work flows main → staging → prod, never the reverse. The 84-cycle qualification record is summarised in `batch-0f273392a113/handoff-hosted-staging-qualification.md` on kc-claude-plugins' state branch.

## Accepted outcome

**Scope split by the Captain (2026-09-07): this ticket is PR 1 of 2 — everything under experiments/netlify-refine-poc/qnow-next that hosted/ imports or its tests need, excluding hosted/ itself; DEV-137 is PR 2 (hosted/).**

The `hosted/` runner and what it needs (package scripts, netlify/ config, identity and local helpers, schema/db/api pieces it imports, its tests) land on main through PRs whose evidence is credential-free: `test:hosted-gates`, `test:netlify-package`, `test:unit`, `acceptance:hosted:full-run:self-check` (providerCalls 0), `type-check`; no provider call, no deploy. Scaffolding the record marks as superseded (cycle 77 runner logic, temporary runners) is not carried. Falsifier: a PR in the set needs a credential to pass its own checks, or main's existing suites regress.

## Surfaces

This PR's own files (supporting files): `experiments/netlify-refine-poc/qnow-next/netlify/`, `experiments/netlify-refine-poc/qnow-next/identity/`, `experiments/netlify-refine-poc/qnow-next/local/`, `experiments/netlify-refine-poc/qnow-next/test/`.

## Non-goals

* Running the hosted journey (DEV-37).
* Deciding customer identity (DEV-132).
* Rebasing #1174 (its own step after this lands).

## Acceptance criteria

* **AC-1** `git ls-tree -r --name-only origin/main experiments/netlify-refine-poc/qnow-next/hosted | wc -l` prints 26 or more after merge; logged.
* **AC-2** From `experiments/netlify-refine-poc/qnow-next` at the merge head: `npm run test:hosted-gates`, `npm run test:netlify-package`, `npm run test:unit`, `npm run type-check`, `npm run acceptance:hosted:full-run:self-check` each exit 0 with logs recorded.
* **AC-3** `git diff --stat origin/main origin/spacedock-ensign/qnow-next-hosted-staging-qualification -- experiments/netlify-refine-poc/qnow-next/hosted | wc -l` prints 0 after merge.

Re-verified: `git -C ~/conductor/repos/qnow ls-tree -r --name-only origin/main experiments/netlify-refine-poc/qnow-next/hosted | grep -q .` exit 1 2026-09-07

## Verification (from experiments/netlify-refine-poc/qnow-next; `npm ci` first)

`npm run type-check`, `npm run test:unit`, and every test file you bring over run under the script that owns it (check package.json at the branch for `test:hosted-gates`, `test:local-db-gate`, `test:native-migrations` and bring the scripts too if their tests come); all exit 0. If a brought test needs Docker PostgreSQL, run it (Docker is available). Record each exit.

Add no comment line that narrates the change. One commit in the repo's Conventional Commit style, stage only the files you added or changed. Push with `git push origin HEAD:refs/heads/feature/dev-136-land-the-hosted-runners-supporting-files-on-main-netlify` (fast-forward on a new branch). Then the Evidence block: WITHOUT_IT_COMMAND one self-contained line exiting 0 at your candidate and non-zero at BASE_SHA (a test file or script path that does not exist at base is fine — exit 2 is non-zero), reading nothing outside the repo; WITHOUT_IT_REMOVED_VARIANT one line altering a read path you added; observe all three exits. Write the block to `.context/evidence.md` (do not stage it) and run `bash /Users/kent/.claude/plugins/local/kc-ship-flow/scripts/accept-evidence.sh .context/evidence.md` from the worktree root; paste its last line as SELF_CHECK (the station may refuse `.ts/.mjs` paths on AC-3 — a known defect, DEV-134; report it as BLOCKER, do not work around it). Read CANDIDATE_SHA with `git rev-parse HEAD` after the push and confirm it equals `git ls-remote origin feature/dev-136-land-the-hosted-runners-supporting-files-on-main-netlify`.

Final reply: exactly one fenced block, nothing after it:

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-136-land-the-hosted-runners-supporting-files-on-main-netlify
BASE_SHA: __BASE__
FILES: <comma-separated or a directory summary with counts>
TESTS: <command> -> exit <code>; ...
SURFACE: <path> -> <AC-N> | <command that proves it> | <command that removes exactly its contribution>
WITHOUT_IT_COMMAND: <one line>
WITHOUT_IT_REMOVED_VARIANT: <one line>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
SELF_CHECK: <last line printed by accept-evidence.sh>
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: <observed> AC-2: <observed> AC-3: <observed>
BLOCKER: none | <what stopped you and at which step>
```
