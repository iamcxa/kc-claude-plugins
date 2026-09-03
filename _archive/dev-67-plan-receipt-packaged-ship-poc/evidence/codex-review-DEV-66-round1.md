CLOSED [P1] `scripts/ship-flow/parse-execute-external.py:65` — PyYAML now handles quoted YAML correctly.  
CLOSED [P1] `scripts/kc-dev-flow-contract-test.py:1903` — contract tests now pin the CLI evidence paragraph.  
OPEN [P2] `scripts/fixtures/ship-flow/quoted-run.yaml:13` — `false` behaves identically at every revision, so the fixture still cannot prove SHA pinning.  
CLOSED [P2] `scripts/ship-flow/e2e-cli.sh:69` — every `expect` is validated before commands run.  
CLOSED [P2] `scripts/ship-flow/e2e-cli.sh:49` — parser failure status is captured and checked.  
NEW [P1] `scripts/ship-flow/parse-execute-external.py:70` — shell quoting preserves embedded newlines and tabs, which corrupt the line/tab transport for valid multiline YAML commands.  
NEW [P2] `scripts/ship-flow/parse-execute-external.py:66` — invalid UTF-8 raises uncaught `UnicodeDecodeError`, producing the traceback the parser contract forbids.

```text
Remaining: One open finding and two new findings.
Next: Fix them and rerun review. (you)
Closable: no
```
