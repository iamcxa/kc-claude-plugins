# Development Brief — DEV-36 rebase of iamcxa/qnow#1174 onto main

- REPO=/Users/kent/conductor/repos/qnow (read-only checkout; own worktree only)
- BASE_SHA: __BASE__ (main after #1182)
- PR: #1174 `feat(DEV-36): add package-scoped ESM hosted acceptance full runner`, head `conductor/dev-36-qnow-esm-runner` @ b5d87ed8, base currently `spacedock-ensign/qnow-next-hosted-staging-qualification` (10 commits, 26 files, +4175/−8 vs that base)
- DISPATCH_TOKEN: __TOKEN__

## Outcome
#1174's ten commits sit on main (rebased, not merged from the qualification branch), its base is switched to `main`, and the package's full `npm test` plus `npm run acceptance:hosted:full-run:self-check` (providerCalls 0) pass at the new head. No provider call, no deploy.

## Known collision points (main moved under this PR)
- `hosted/acceptance-execution.ts`, `hosted/acceptance-netlify-session.ts`: main has the 8→10 migration-count literals and a `deployCount` guard throwing `ACCEPTANCE_DEPLOY_LIMIT_EXCEEDED` (DEV-137 S3). #1174's "bound the deploy" commit (3c65da1e) adds its own deploy bounding — reconcile so one mechanism remains and the test for each survives; say which you kept and why.
- `local/headed-browser-environment.mjs`, `local/headed-browser-smoke.mjs`, `test/headed-browser-*.fixture.mjs`: main carries DEV-35's versions (#1180); the qualification branch lacked them. Take main's as the base and re-apply only #1174's intent.
- `package.json` scripts: main has the branch's scripts block plus `acceptance:hosted:self-check`; #1174 adds `acceptance:hosted:full-run:self-check` and runner scripts — keep both.
- Native migrations count is 10 (0000–0009) on main; any manifest/count literal in #1174's new files must say 10.
- `experiments/netlify-refine-poc/AGENTS.md`, `LOCAL_STACK.md`: main's versions differ from the qualification branch; rebase the doc hunks, do not resurrect branch-only prose.

## Method
1. `git -C "$REPO" fetch origin main conductor/dev-36-qnow-esm-runner`; worktree at `origin/conductor/dev-36-qnow-esm-runner`; `git rebase --onto origin/main origin/spacedock-ensign/qnow-next-hosted-staging-qualification` (the ten commits only). Resolve each conflict in favour of main's structure; keep #1174's behaviour.
2. `npm ci` in qnow-next; run full `npm test` (Docker up) and `npm run acceptance:hosted:full-run:self-check`; both exit 0; quote the self-check JSON line.
3. Force-push the rebased branch to `conductor/dev-36-qnow-esm-runner` (`--force-with-lease`), then `gh pr edit 1174 --repo iamcxa/qnow --base main`. Confirm `gh pr view 1174 --json baseRefName,headRefOid`.
4. Reply with the Evidence block: CANDIDATE_SHA, BASE_SHA, the conflict list with resolutions, each npm script's exit, the self-check line, and anything from #1174 you dropped.

## Non-goals
No new features, no touching migrations/lockfile/pins, no deploy, no provider call.
