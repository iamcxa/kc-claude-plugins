# Pilot Build

Working perspective: product engineer.

## Mission

Implement the accepted journey through its real seams with enough diagnostics
and recovery for bounded use.

## Required output

- runnable integrated slice;
- focused tests for owned logic and seam behavior;
- diagnostics and bounded retry/recovery required by the shape contract.

Run scoped tests while iterating and the relevant integrated checks at exit. Do
not add production lifecycle surfaces or a standing review loop.

## Implementation exit observation

```json
{
  "schema": "kc-dev-flow-observation/v1",
  "capability": "review_convergence",
  "mode": "observe",
  "provider": "roborev",
  "trigger": "implementation_exit",
  "reasoning": "medium",
  "minimum_severity": "medium",
  "panel": "none",
  "live_batch_timeout_seconds": 900,
  "request_cap": 1,
  "repair_confirmation_cap": 1
}
```
