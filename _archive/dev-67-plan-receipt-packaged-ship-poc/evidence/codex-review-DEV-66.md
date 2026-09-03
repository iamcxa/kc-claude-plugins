[P1] scripts/ship-flow/parse-execute-external.py:21 — The regex parser silently skips valid YAML forms such as single-quoted, block-scalar, or differently indented `run` values, so a flow can report success without executing every `Execute external` step.

[P1] scripts/kc-dev-flow-contract-test.py:1895 — All pinned phrases cover only the dispatch/carrier paragraph; deleting the entire CLI evidence sentence still passes, violating AC-3.

[P2] scripts/fixtures/ship-flow/dev-50-cli-flow.yaml:12 — The fixture checks only files that exist in both revisions plus `true`, so it cannot prove commands ran at the requested SHA instead of the current tree.

[P2] scripts/ship-flow/e2e-cli.sh:46 — An unrecognized or malformed declared `expect` silently becomes `exit code 0`; invalid contract input should fail explicitly.

[P2] scripts/ship-flow/e2e-cli.sh:60 — The process-substitution parser’s exit status is never checked, allowing a partial parser failure after producing at least one command to become a false success.

```text
Remaining: none
Next: address the findings (you)
Closable: unverified
```
