# Browser Profile Lifecycle Design and Implementation Plan

**Goal:** Make the owned E2E browser runtime compatible with observed
`agent-browser 0.32.0` profile behavior while proving that the first application
navigation keeps the same owned daemon, browser, page, profile, init script, and
network recorder.

## Root cause

The runtime currently sends the application URL to `agent-browser open` before
it verifies the launched Chrome process. A path profile that is unexpectedly
materialized as an `agent-browser-chrome-*` snapshot therefore consumes an
application navigation and only then fails the exact `--user-data-dir` check.
The fallback evidence also treated later `about:blank` and an empty recorder as
application evidence without identifying which browser identity changed.

Live `agent-browser 0.32.0` probing on macOS established two constraints:

- An absolute, runtime-managed path can launch as the exact Chrome
  `--user-data-dir`, including after that profile has been populated.
- `runtime.effectiveLaunch.launchHash` changes across a normal navigation even
  when the namespace, session, daemon PID, Chrome PID, profile, and active tab
  remain stable. It is diagnostic metadata, not an ownership identity.

## Considered approaches

1. **Accept every OS-temp `agent-browser-chrome-*` directory.** Rejected because
   the path shape does not prove which canonical profile sourced the clone.
2. **Copy the canonical profile in the pipeline and pass the copy.** Rejected
   because it makes the pipeline responsible for copying sensitive browser
   state and still cannot prevent an additional opaque agent-browser clone.
3. **Two-phase capability-bound launch.** Selected. Launch only `about:blank`,
   then accept either the exact managed persistent path or an OS-temp snapshot
   structurally bound to that source. Only then consume the application
   navigation. An unbound clone fails before the application URL is requested.

## Runtime contract

The first `open <url>` becomes a transaction:

1. Create a private runtime-owned init script beside the ownership receipt.
2. Launch `open` without an application URL and pass the init script at browser
   startup.
3. Record pre-navigation namespace, session, daemon PID, browser PID, active tab
   identity, actual profile, URL, page count, launch hash, and init/HAR state.
4. Require the Chrome process to use the exact canonical/flow-managed path, or
   prove an `agent-browser-chrome-*` snapshot by daemon ancestry, executable,
   owner, mode, inode, creation time, private temp-root containment, and a
   SHA-256 digest over matching relative-path/size/mode metadata. Profile file
   contents are never read.
5. Start a bounded HAR, navigate once, and record the post-navigation evidence.
6. Require unchanged namespace/session/daemon/browser/tab/profile identities,
   the runtime init marker, a non-blank URL, and at least one document request.
7. Stop and inspect the HAR, retain only sanitized counts/status in the receipt,
   and remove the raw first-navigation HAR and init script.

An initial `open` without a URL leaves `first_navigation.status` as `pending`;
the next `open <url>` completes the same transaction. Later navigations retain
pre/post identity checks without starting another first-navigation recorder.

Any identity reset is an infrastructure failure. The receipt records the
specific changed field and cleanup closes only its bound namespace. Snapshot
cleanup uses the recorded actual path/device/inode and never removes the
canonical profile or a foreign browser directory.

## TDD tasks

1. Add an agent-browser 0.32 integration fixture that can launch either the
   requested path or an OS-temp snapshot and exposes real-shaped session, tab,
   init-script, network-request, and HAR responses.
2. Add failing tests for pre-navigation clone rejection, successful first
   navigation evidence, daemon/browser/tab reset classification, and two-run
   cleanup isolation.
3. Implement the two-phase open transaction and versioned lifecycle receipt.
4. Update mapper, runner, verifier, walkthrough, debug/diagnostic guidance, and
   compiler-generated wrappers to require the lifecycle verdict.
5. Run focused runtime/contract tests, the complete plugin suite, and a live
   0.32 local-page probe with a fresh empty profile.
