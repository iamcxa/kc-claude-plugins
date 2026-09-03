---
title: "Fixture: production work item for surface-map-check contract test"
status: implementation
issue: FIXTURE-PROD
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  route: [shape, build, verify]
  semantics_unchanged: true
```

## Acceptance evidence

* **AC-1** scripts/ship-flow/e2e-cli.sh runs DEV-50's three-step CLI flow to a PASS log and a FAIL-and-halt log.
* **AC-2** docs/dev/README.md states the no-bootstrap-line rule and the committed-carrier rule.
* **AC-3** scripts/kc-dev-flow-contract-test.py asserts both README sentences are present; mutation runs recorded.
