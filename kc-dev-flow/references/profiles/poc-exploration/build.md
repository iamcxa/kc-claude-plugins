# POC Build

Working perspective: incubation engineer.

## Mission

Build the smallest end-to-end path that can answer the experiment's question.

## Required output

- one runnable integrated artifact;
- focused checks for owned logic and the riskiest assumption;
- no unrelated structure, abstraction, or test surface.

Stop when the journey can be exercised. Do not open a reviewer loop or improve
production qualities outside the selected boundary.

## Implementation exit observation

```json
{
  "schema": "kc-dev-flow-observation/v1",
  "capability": "review_convergence",
  "mode": "observe",
  "provider": "roborev",
  "trigger": "implementation_exit",
  "reasoning": "medium",
  "minimum_severity": "high",
  "panel": "none",
  "live_batch_timeout_seconds": 600,
  "request_cap": 1,
  "repair_confirmation_cap": 0
}
```
