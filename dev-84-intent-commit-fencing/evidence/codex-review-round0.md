[P2] scripts/ship-flow/intent.sh:46 — `reconcile` counts exact-name workspaces before filtering by project ID. If two projects contain that name but only one matches the intent, it incorrectly reports `ambiguous intent` instead of adopting the sole project-matching workspace.

```text
Remaining: none
Next: filter candidates by workspace-get project ID before counting (cloud worker)
Closable: unverified
```
