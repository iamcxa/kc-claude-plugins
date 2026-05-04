# e2e-pipeline / test/baselines

This directory stores baseline measurement snapshots for the `eval_fallback_hits`
counter introduced in ship-flow entity 001-selector-grammar-alignment (T2.1 + T2.2).

## What is a baseline

A baseline is a JSON file (`fallback-baseline.json`) that records, for each flow YAML,
how many times the e2e-test-runner fell back to `eval`-based DOM resolution instead of
using native agent-browser CLI selectors.

Baselines are captured by running:

```
e2e-pipeline/scripts/measure-fallback-baseline.sh \
  --flows-dir <dir-containing-flow-yamls> \
  --target-url <base-url-of-running-app>
```

## When to run

| Timing | Purpose |
|--------|---------|
| Pre-T2.2 (before `--strict-native-selectors` ships) | Establish baseline hit counts per flow. Shows which flows currently rely on the eval fallback. |
| Post-T2.2 (after strict mode lands) | Re-measure to verify hits dropped. Ideally `eval_fallback_hits: 0` for flows using only native selectors. |
| Post-merge regression check | Any flow showing a higher hit count than its pre-T2.2 baseline indicates a new selector mismatch was introduced. |

## How the baseline is consumed

1. **Pre-mortem signal** — The spec (`docs/ship-flow/001-selector-grammar-alignment/spec.md`,
   Pre-mortem section) identifies "30+ existing flows quietly relying on eval fallback" as
   a key risk. The pre-T2.2 baseline makes this risk concrete and countable before merge.

2. **T2.2 verification** — After `--strict-native-selectors` ships, the captain re-runs the
   measurement script and compares output against this baseline. Any flow with
   `eval_fallback_hits > 0` in the post-T2.2 run is a selector that needs fixing.

3. **Regression test** — In future CI, a post-merge baseline showing a higher hit count
   than the committed pre-T2.2 baseline for an otherwise-unchanged flow signals a new
   selector regression. The gate is `--strict-native-selectors`, not this file; but the
   baseline gives the signal a number.

## File format

```json
{
  "measured_at": "<ISO 8601 timestamp>",
  "target_url": "<base URL used during measurement>",
  "runner_version": "<e2e-pipeline plugin version>",
  "flows": [
    {
      "flow": "<absolute path to flow YAML>",
      "eval_fallback_hits": 3,
      "trace_excerpt": "<relevant lines from runner trace output>"
    }
  ]
}
```

`eval_fallback_hits: null` means the flow was not measured in this run (skeleton mode).

## Skeleton vs measured

When `claude` CLI or `ANTHROPIC_API_KEY` is unavailable, the script runs in **documenter
mode** and writes a skeleton JSON with `null` hit counts. The captain fills in actual counts
after running `/e2e-test <flow>` manually in a Claude Code session with the e2e-pipeline
plugin loaded.

## Notes

- Do not commit `fallback-baseline.json` from a skeleton run as a "real" baseline —
  it would have all `null` values and provide no regression signal.
- The `.gitkeep` file exists only to track this directory in git; delete it once a
  real baseline JSON is committed here.
- The measurement script always exits 0 — it is instrumentation, not a gate.
