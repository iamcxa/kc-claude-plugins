## Evidence
CANDIDATE_SHA: 4ce46967651c25234f1ed01b18e95d1fdfad2ff5
BRANCH: feature/dev-66-dispatch-carrier-and-e2e-evidence-rules-for-cloud-workers
BASE_SHA: bda45e6bb2716d9276d0542b7c11edd2014ab1be
FILES: docs/dev/README.md, scripts/fixtures/ship-flow/dev-50-cli-flow-failing.yaml, scripts/fixtures/ship-flow/dev-50-cli-flow.yaml, scripts/kc-dev-flow-contract-test.py, scripts/ship-flow/e2e-cli.sh, scripts/ship-flow/parse-execute-external.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
WITHOUT_IT_COMMAND: python3 scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_REMOVED_VARIANT: git checkout bda45e6bb2716d9276d0542b7c11edd2014ab1be -- docs/dev/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: scripts/ship-flow/e2e-cli.sh 0144264343775f4c74f517ccea488a8ef91c44bc scripts/fixtures/ship-flow/dev-50-cli-flow.yaml (DEV-50's three-step CLI flow) -> exit 0, all 3 "Execute external" steps PASS with per-step UTC timestamps; scripts/ship-flow/e2e-cli.sh 0144264343775f4c74f517ccea488a8ef91c44bc scripts/fixtures/ship-flow/dev-50-cli-flow-failing.yaml (third step `false`) -> exit 1, FAIL logged with timestamp at the first failing step, run halted there. Both timestamped logs recorded in .context/dev-66-evidence/ac1-pass.log and ac1-fail.log (gitignored, not part of the committed tree).
AC-2: docs/dev/README.md new "## Ship-flow runtime" section (after "## Task template") states the no-bootstrap-line rule and names the Conductor WAF block as the reason ("the Conductor WAF blocks a dispatch message containing a `curl | tar` bootstrap line"), and states the committed-carrier rule ("it travels on a committed carrier ... the worker fetches and reads with `git show <branch>:<path>`").
AC-3: scripts/kc-dev-flow-contract-test.py now asserts both README sentences are present (four required phrases covering both rules). Mutation runs recorded: removing the no-bootstrap-line sentence -> contract test exit 1 ("Ship-flow runtime omits a dispatch-carrier rule: A dispatch message to a cloud build worker carries no bootstrap or download line"); removing the committed-carrier sentence -> contract test exit 1 ("... it travels on a committed carrier"); README restored -> contract test exit 0. Logs in .context/dev-66-evidence/ac3-mutation-remove-sentence1.log and ac3-mutation-remove-sentence2.log (gitignored, not part of the committed tree).
BLOCKER: none
