## Evidence
CANDIDATE_SHA: b5adfba85b346f6605d507764c67ee19d412a95d
BRANCH: feature/dev-66-dispatch-carrier-and-e2e-evidence-rules-for-cloud-workers
BASE_SHA: bda45e6bb2716d9276d0542b7c11edd2014ab1be
FILES: docs/dev/README.md, scripts/fixtures/ship-flow/dev-50-cli-flow-failing.yaml, scripts/fixtures/ship-flow/dev-50-cli-flow.yaml, scripts/fixtures/ship-flow/quoted-run.yaml, scripts/kc-dev-flow-contract-test.py, scripts/ship-flow/e2e-cli.sh, scripts/ship-flow/parse-execute-external.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
WITHOUT_IT_COMMAND: python3 scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_REMOVED_VARIANT: git checkout bda45e6bb2716d9276d0542b7c11edd2014ab1be -- docs/dev/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: scripts/ship-flow/e2e-cli.sh 0144264343775f4c74f517ccea488a8ef91c44bc scripts/fixtures/ship-flow/dev-50-cli-flow.yaml -> exit 0 (3 steps PASS, timestamped); same sha + dev-50-cli-flow-failing.yaml (third step `false`) -> exit 1, FAIL logged at the failing step. Fix-round regression check: scripts/fixtures/ship-flow/quoted-run.yaml, whose only step is a single-quoted `run: 'false'`, now correctly parses via PyYAML and exits 1 with "FAIL step 1: 'false' exited 1, expected 0" (not "no steps found"). PyYAML-unavailable and malformed-YAML inputs both exit 2 with a clear stderr message instead of a traceback or a silent pass; a flow with zero `Execute external` steps and a flow with an unrecognized `expect` string both exit 2, validated before any step runs. All logs timestamped, recorded in .context/dev-66-evidence/ (gitignored, not part of the committed tree).
AC-2: docs/dev/README.md "## Ship-flow runtime" section states the no-bootstrap-line rule (naming the Conductor WAF block as reason) and the committed-carrier rule, unchanged from the prior round.
AC-3: scripts/kc-dev-flow-contract-test.py now pins phrases from both the dispatch-carrier paragraph and the CLI e2e evidence paragraph. Mutation runs recorded: removing the no-bootstrap-line sentence -> exit 1; removing the committed-carrier sentence -> exit 1; removing the whole "CLI e2e evidence is a timestamped stdout log" paragraph -> exit 1 ("Ship-flow runtime omits the CLI e2e evidence rule: CLI e2e evidence is a timestamped stdout log written by"); README restored -> exit 0 each time. Logs in .context/dev-66-evidence/ac3-mutation-*.log (gitignored, not part of the committed tree).
BLOCKER: none
