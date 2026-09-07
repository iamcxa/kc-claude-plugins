You are a kc-dev-flow build-stage worker running as a LOCAL subagent for a Pilot item, DEV-137, in iamcxa/qnow. Work only inside your own git worktree; never touch the clone you branch from. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. Do NOT read or write Linear. Do NOT open a pull request. Do NOT run `git add .`. Never run `acceptance:hosted:full-run` or anything that deploys or contacts a provider — only the credential-free commands named below.

Set up:
- REPO=/Users/kent/conductor/repos/qnow ; git -C "$REPO" fetch origin main "+refs/heads/spacedock-ensign/qnow-next-hosted-staging-qualification:refs/remotes/origin/spacedock-ensign/qnow-next-hosted-staging-qualification"
- WT=$(mktemp -d)/wt ; git -C "$REPO" worktree add "$WT" __BASE__ ; cd "$WT" ; git checkout -b feature/dev-137-land-experimentsnetlify-refine-pocqnow-nexthosted-on-main-pr
- Read CLAUDE.md, AGENTS.md and experiments/netlify-refine-poc/AGENTS.md first. Source of the files: `origin/spacedock-ensign/qnow-next-hosted-staging-qualification` (the qualification branch, 48 commits ahead of main). Bring files over with `git checkout origin/spacedock-ensign/qnow-next-hosted-staging-qualification -- <paths>` (or cherry-pick when a commit is clean), never by merging the branch. Do not carry files the 84-cycle record marks superseded (cycle-77 runner-only logic, temporary /tmp runners).

## Brief (DEV-137)

## The problem

Continuation of DEV-136 (PR 1 of 2). With the supporting files on main, `experiments/netlify-refine-poc/qnow-next/hosted/` (26 files: acceptance operator contract, Netlify session lifecycle with rollback binding, secret-safe readback, canary scan, deploy diagnostics, package entry point) can land as its own reviewable PR. Main has 0 files under hosted/.

## Accepted outcome

`hosted/` lands on main as one PR (cherry-picked from `spacedock-ensign/qnow-next-hosted-staging-qualification`, superseded cycle-77 runner logic excluded), with credential-free evidence: `npm run test:hosted-gates`, `npm run test:netlify-package`, `npm run acceptance:hosted:self-check` (providerCalls 0), `npm run type-check`; no provider call, no deploy. After it merges, #1174 (DEV-36) is rebased onto main.

## Surfaces

This PR's own files (hosted runner): `experiments/netlify-refine-poc/qnow-next/hosted/acceptance-execution.ts`, `experiments/netlify-refine-poc/qnow-next/hosted/acceptance-full-run.mts`, `experiments/netlify-refine-poc/qnow-next/hosted/acceptance-netlify-session.ts`.

## Non-goals

* Running the hosted journey (DEV-37).
* Any change to hosted/ behaviour beyond what the branch already has (#1174's fixes come with DEV-36).

## Acceptance criteria

* **AC-1** `git ls-tree -r --name-only origin/main experiments/netlify-refine-poc/qnow-next/hosted | wc -l` prints 26 or more after merge; logged.
* **AC-2** From `experiments/netlify-refine-poc/qnow-next` at the merge head, the four commands above each exit 0 with logs recorded.
* **AC-3** `git diff --stat origin/main origin/spacedock-ensign/qnow-next-hosted-staging-qualification -- experiments/netlify-refine-poc/qnow-next/hosted | wc -l` prints 0 after merge.

Re-verified: `git -C ~/conductor/repos/qnow ls-tree -r --name-only origin/main experiments/netlify-refine-poc/qnow-next/hosted | grep -q .` exit 1 2026-09-07

## Verification (from experiments/netlify-refine-poc/qnow-next; `npm ci` first)

`npm run type-check`, `npm run test:hosted-gates`, `npm run test:netlify-package`, `npm run acceptance:hosted:self-check` (must print providerCalls 0); all exit 0. Do not run the full run.

Add no comment line that narrates the change. One commit in the repo's Conventional Commit style, stage only the files you added or changed. Push with `git push origin HEAD:refs/heads/feature/dev-137-land-experimentsnetlify-refine-pocqnow-nexthosted-on-main-pr` (fast-forward on a new branch). Then the Evidence block: WITHOUT_IT_COMMAND one self-contained line exiting 0 at your candidate and non-zero at BASE_SHA (a test file or script path that does not exist at base is fine — exit 2 is non-zero), reading nothing outside the repo; WITHOUT_IT_REMOVED_VARIANT one line altering a read path you added; observe all three exits. Write the block to `.context/evidence.md` (do not stage it) and run `bash /Users/kent/.claude/plugins/local/kc-ship-flow/scripts/accept-evidence.sh .context/evidence.md` from the worktree root; paste its last line as SELF_CHECK (the station may refuse `.ts/.mjs` paths on AC-3 — a known defect, DEV-134; report it as BLOCKER, do not work around it). Read CANDIDATE_SHA with `git rev-parse HEAD` after the push and confirm it equals `git ls-remote origin feature/dev-137-land-experimentsnetlify-refine-pocqnow-nexthosted-on-main-pr`.

Final reply: exactly one fenced block, nothing after it:

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-137-land-experimentsnetlify-refine-pocqnow-nexthosted-on-main-pr
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

## Amendments from DEV-136 (2026-09-07)

- Main now carries native migrations 0000–0007 plus `0008_dev25_staff_assignments_privilege` (revokes the branch's pre-DEV-25 `GRANT SELECT ON qnow_staff_assignments TO qnow_app`). Any hosted/ test or artifact list brought from the qualification branch that enumerates migration names must include 0008; do not remove 0008 and do not re-grant.
- Main-existing files the qualification branch modified are already carried (work-control-api, work-control-postgres, packages/db schema test); `test/postgres.integration.test.ts` was NOT carried wholesale because its branch version imports `../hosted/database-admission.js` — DEV-137 brings the branch version of that test with hosted/.
- `test/netlify-package.test.mjs` skips its hosted-artifact sub-test while `hosted/build-artifacts.mjs` is absent; after hosted/ lands it must run and pass (report its exit explicitly).
- `test/tenancy-isolation.integration.test.ts` on main is the ported native-migration version (13/13); do not overwrite it with the branch's deletion.
- The AC script name is `acceptance:hosted:self-check` (not `acceptance:hosted:self-check`).
- Do not touch the @netlify/dev, @netlify/identity, netlify-cli pins (DEV-138).
