# validation gate — canvas-document-popup

Candidate `6f4ec0e3` on `spacedock-ensign/canvas-document-popup`. Validator verdict:
PASSED. FO recommendation: **approve, with one necessity question answered.**

## FO verification of the validator

- Candidate HEAD is `6f4ec0e3` and the worktree is clean — no mutation during the
  stage.
- The Captain's canvas on port 3742 is still served by the same process (PID 6259),
  before and after.
- `agent-browser --help` documents `--args <args>` for browser launch args, so the
  non-localhost mechanism the validator used is a real capability of the project's own
  tool, not an invention.
- `vite.share.config.mts` proxies only `/connect/` and `/uploads/` — the reported
  `npm run share` limit is exactly right.
- `kc-journey-map-tests.yml`'s own header states "the browser is not exercised here".

FO separately ran the delivered `scripts/popup-browser-check.mjs`, `npm run
typecheck`, and `lib/repo-doc.test.mjs` before this stage; all passed.

## What the validator added beyond the implementation

Two things worth recording.

1. **It closed AC-1's open half instead of inheriting it.** Implementation reported the
   shared-board-origin browser run as unachievable here. The validator disproved that:
   Chromium's `--host-resolver-rules=MAP sharedorigin.test 127.0.0.1`, reachable through
   `agent-browser --args`, produces a genuine non-localhost navigation with a real
   `Host` header and needs no root or `/etc/hosts` edit. It then ran the full
   open/render/close loop over that origin against `JOURNEY_ALLOWED_HOSTS`. AC-1 is
   proven, not deferred.
2. **It falsified its own unit-test claim.** Reversing the iteration direction in
   `candidateRefSplits` reddens 2 of the 11 tests, restored afterwards. The
   longest-ref-first ordering is load-bearing and the tests actually detect it.

## Honestly unconfirmed, per the validator

AC-5's full export→import→open round trip and three of AC-4's four branches (bad ref,
bad path, missing heading) were confirmed by reading code that shares a path with
branches it did exercise, not re-executed. The React StrictMode defect the
implementation describes fixing was taken on trust. A genuinely private GitHub
repository was not tested; both the entity and the implementation accept its collapse
into the unmapped state as a design consequence of D1.

FO accepts these as residuals. None is an untested effect claim dressed as a limit:
each names what was read instead of run.

## Goal sufficiency

The approved outcome was that a reviewer can read a chapter without leaving the card
or losing the viewport, and that the board stays portable to a viewer-less tldraw host.
AC-1 through AC-4 are exercised, AC-5 is confirmed by the schema being a standard
`url: T.linkUrl` prop. Sufficient.

## Minimal necessity — the one open question

The diff is 825 insertions. `scripts/popup-browser-check.mjs` is 399 of them, 48%, and
**nothing runs it**: `kc-journey-map-tests.yml` excludes the browser and installs no
`agent-browser` step. This task's entire history is a defect that a wrong evidence
method hid, so an unrun evidence script is precisely the thing worth deciding rather
than assuming.

- **Option A — wire it into CI.** The check becomes enforced. Cost: an
  `agent-browser` install step and browser run time on every PR touching
  `kc-journey-map/**`. FO has not measured that cost and will not guess it.
- **Option B — keep it manual, named in `canvas.md` beside the startup step.** Zero CI
  cost. Nothing enforces it; the next change to this popup can silently break the
  Close control again, which is the exact failure this task already had once.
- **Option C — trim it** to the assertions that caught real defects (the
  `elementFromPoint` hit-test and the real-click-on-Close pair) and drop the rest.

FO recommends A, scoped to a path filter on `kc-journey-map/**`, because option B's
risk already materialised once in this task's own history. FO will measure the CI cost
before proposing the workflow change if the Captain picks A.

## Delivery

Approving this gate is not permission to push or create a PR. The candidate and PR
body are presented separately.
