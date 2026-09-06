# POC verdict: standalone batch-station pin

## Verdict: proceed

The standalone `kc-ship-flow/scripts/pin.py` records the declared plugin bytes for
one station without importing kc-dev-flow's `profile-contract-loader.py`.
`verify_record` binds the recorded digest and plugin version to the current
plugin for both `check` and same-station replay. Measured:

- `pin.py` is 229 lines; `pin.test.py` is 288 lines. The implementation remains
  near the ~200-line POC target; the expanded regression suite exceeds it.
  Neither imports `profile_contract_loader`.
- `write` computes a length-prefixed sha256 digest over each declared path and
  its bytes in `kc-ship-flow/schemas/resources.json` (currently the plugin
  manifest and `references/kernel.md`). It separately records the manifest's
  version and emits a `kc-ship-flow-batch-pin/v1` record with a 64-hex digest.
- `check` refuses changed resource bytes (`CONTRACT_DIGEST_MISMATCH`, naming
  the resource), a wrong `previous_station` (`PREVIOUS_STATION_MISMATCH`, naming
  the expected station), and a missing or wrong recorded plugin version
  (`PLUGIN_VERSION_MISMATCH`, naming the recorded and expected versions).
- Replaying `write` for the same batch and station calls `verify_record` before
  returning the existing record. It does not rewrite the pin file or timestamp;
  a refused replay leaves the existing bytes intact. Regression tests cover
  resource drift, altered digest, wrong predecessor, and wrong/missing version,
  alongside first writes, unchanged replay, forward writes, and existing guards.
- `python3 kc-ship-flow/scripts/pin.test.py` passes locally in 3.713 seconds.
  It fails against the original implementation and when either the replay
  verification call or the recorded-version comparison is removed in a temporary
  copy. CI integration is pending separately; hosted CI duration and cost per
  PR are unmeasured.

## What the shape does not cover yet

- Writing a later station retains the existing behavior: it creates a new record
  from the current plugin, even if resource bytes or the version have changed.
  The tests exercise an unchanged transition and a transition with changed bytes
  and version. This does not enforce one unchanged digest across the whole batch.
- `previous_station` is checked against a fixed order table
  (`dispatched, accepted, reviewed, uat, merged, closed`), not against an actual
  prior pin record's own digest. The label does not prove a prior record existed;
  chaining actual records remains outside this POC.
- No lock or atomicity around `write`/`check`; concurrent access to the same
  `--pin` path remains outside this POC.

## Non-goals held

- No code or import shared with `kc-dev-flow/scripts/profile-contract-loader.py`.
- No byte-pinning of plan-flow schemas; those remain pinned by `schema` string.
