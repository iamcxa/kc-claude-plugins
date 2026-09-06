# POC verdict: standalone batch-station pin

## Verdict: proceed

A standalone `kc-ship-flow/scripts/pin.py` holds the guarantee ship needs — the plugin
bytes a batch ran under are pinned by sha256 — without importing kc-dev-flow's
`profile-contract-loader.py`. Measured:

- `pin.py` is 186 lines; `pin.test.py` is 110 lines. Both stay under the ~200-line
  standalone budget this POC was scoped against, without sharing code with the
  dev-flow loader (`grep -c 'import.*profile_contract_loader' kc-ship-flow/scripts/pin.py`
  prints 0).
- `write` computes a sha256 digest over the bytes of every path declared in
  `kc-ship-flow/schemas/resources.json`, plus the plugin version read from
  `kc-ship-flow/.claude-plugin/plugin.json`, and emits a `kc-ship-flow-batch-pin/v1`
  record with a 64-hex `contract_digest`.
- `check` refuses two independent mutations, each in its own `pin.test.py` case:
  one declared resource's bytes changing (names the resource:
  `CONTRACT_DIGEST_MISMATCH: changed resource: references/kernel.md`), and the
  record's `previous_station` not matching the fixed station order (names the
  expected station: `PREVIOUS_STATION_MISMATCH: ... expected 'dispatched'`).

## What the shape does not cover yet

- `previous_station` is checked against a fixed order table
  (`dispatched, accepted, reviewed, uat, merged, closed`), not against an actual
  prior pin record's own digest. A batch could still present a forged
  `previous_station` label without ever having produced the record it claims to
  follow. Chaining `check` against a real prior `--pin` file (not just a label)
  is a B5 decision, not solved by this POC.
- No lock or atomicity around `write`/`check` — concurrent batches touching the
  same `--pin` path is unhandled, matching this POC's scope (one batch, one
  station, one pin file).

## Non-goals held

- No code or import shared with `kc-dev-flow/scripts/profile-contract-loader.py`.
- No byte-pinning of plan-flow schemas — those stay pinned by `schema` string,
  unchanged by this POC.
