# Pilot / Product Slice Base

## Outcome

Deliver a bounded slice for limited real use and likely iteration without
accepting long-term production obligations.

## Working rules

- Keep one user journey integrated through its real persistence and external
  seams.
- Use repository-native structure where it reduces near-term iteration cost;
  reject hypothetical scale and generalized platform work.
- Cover diagnostics, retry or recovery, duplicate handling, and data safety when
  the accepted journey exposes them.
- Test owned logic and real seams. Do not duplicate tests for stable framework or
  vendor behavior.
- Use Chief Engineer advice only for unclear sequencing, a material blocker, or
  a route-changing transition. Science Officer assurance remains risk-triggered.

## Promotion boundary

Stop and request Production when accepted scope adds production data or
credentials, broad exposure, public compatibility, irreversible migration,
unattended recurring operation, SLO/support duty, or release/rollback ownership.
