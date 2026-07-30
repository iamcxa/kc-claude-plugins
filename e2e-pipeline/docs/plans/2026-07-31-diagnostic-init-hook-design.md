# Runtime-Owned Diagnostic Init Hook Design

**Issue:** #110

## Goal

Allow diagnostic consumers to register application-specific JavaScript before
the first application navigation without leaving the owned Chrome for Testing
runtime. Preserve the existing private lifecycle probe and expose only an
explicitly typed, application-sanitized projection after navigation.

## Decision

Add a repeatable runtime option:

```text
--diagnostic-init-script <absolute-path>
```

The option is part of the immutable browser command prefix. The runtime
validates every caller-owned source before starting a browser, creates one
runtime-owned wrapper per source, and passes the wrappers as repeated native
`--init-script` flags alongside the existing private lifecycle probe.
`agent-browser 0.32.0` documents `--init-script` as repeatable, so separate
wrappers preserve script isolation and execution order without combining
unrelated caller programs into one source file.

Each diagnostic source runs inside a wrapper that provides one function:

```js
publishDiagnosticProjection(
  {
    bearer_present: { type: 'boolean' },
    hydration_state: {
      type: 'enum',
      values: ['empty', 'loading', 'ready'],
    },
    request_count: { type: 'integer', min: 0, max: 1000 },
    request_fingerprint: { type: 'sha256' },
  },
  () => ({
    bearer_present: Boolean(observedAuthorization),
    hydration_state: currentHydrationState,
    request_count: observedRequestCount,
    request_fingerprint: safeRequestDigest,
  })
);
```

The schema is the allowlist. Values outside `boolean`, bounded `integer`,
declared `enum`, and `sha256` fail projection retrieval. The runtime never
stores projection values in its receipt. A pseudo-command,
`diagnostic-projection`, invokes fixed runtime-generated `eval` expressions and
returns the current validated projections as JSON.

## Input and provenance contract

Validation uses an open file descriptor with `O_NOFOLLOW` when the platform
provides it. The runtime requires:

- an absolute path;
- a regular file rather than a symlink;
- current-user ownership;
- a readable descriptor whose device and inode match the path inspection.

For each source, the public receipt records only its ordinal, basename, byte
length, SHA-256 content digest, SHA-256 path digest, and lifecycle status. It
does not record source contents, the raw absolute path, projection values,
storage, cookies, tokens, or HAR data.

A private mode-0600 manifest keeps the raw source path, file identity, wrapper
path, marker expression, and projection expression until first navigation is
verified. Before navigation, the runtime reopens and rehashes every caller
source. A missing, replaced, unreadable, ownership-changed, or content-changed
source fails before the application URL is requested. The wrapper files and
private manifest are runtime-owned; caller sources remain caller-owned.

## Lifecycle

1. Parse and validate every diagnostic source before Chrome discovery or
   browser execution.
2. Create the mandatory private lifecycle probe.
3. Create separate runtime-owned wrappers for diagnostic sources.
4. Launch the owned page at `about:blank` with the private probe first and each
   diagnostic wrapper after it.
5. Capture the existing pre-navigation ownership evidence.
6. Revalidate caller sources and wrapper identity.
7. Navigate to the application while the private HAR is active.
8. Prove daemon, browser, page, profile, and URL continuity.
9. Prove the private init marker and every diagnostic marker.
10. Retrieve each projection once to prove its schema and sanitization contract.
11. Record only observation status and safe provenance in the receipt.
12. Delete the runtime-owned wrappers and private manifest.

If the first call opens only `about:blank`, steps 6-12 resume on the later
application `open`. A forced daemon, browser, or page reset remains an
infrastructure failure. A later runtime action verifies the receipt as before;
`diagnostic-projection` additionally requires a verified first-navigation
receipt with observed recorders.

Close and failure cleanup enumerate only the runtime-owned paths authenticated
by the private manifest. They do not unlink caller paths, peer-run paths,
canonical profiles, or personal browser state.

## Alternatives considered

### Pass caller files directly

This is smaller but cannot prove content immutability between `about:blank` and
the application navigation, and it leaves no runtime-controlled observation
marker. It does not satisfy #110.

### Combine all sources into one init file

This makes cleanup simple but changes top-level scope between independent
recorders and allows one syntax/runtime failure to obscure which source failed.
Separate wrappers provide field-specific failures and match the repeatable
native interface.

### Return arbitrary `eval` output

The runtime already permits general `eval`, but treating arbitrary page state
as a diagnostic receipt would recreate the raw-token/raw-storage leak this
issue excludes. The typed projection is deliberately narrower.

## Consumer contract

Mapper, runner, verifier, walkthrough, debug observer, Teams messages, and
compiled scripts carry `diagnostic_init_scripts` only as repeated arguments to
`e2e-browser-runtime.js`. They never translate the option into bare
`agent-browser`, CDP, storage, cookie, or raw HAR commands. The field is optional
and defaults to an empty list, so ordinary E2E runs remain unchanged.

Documentation must state that diagnostic sources and returned projections are
local evidence. Raw browser profiles, cookies, tokens, storage dumps, raw HAR,
and screenshots containing credentials must not be uploaded or committed.
