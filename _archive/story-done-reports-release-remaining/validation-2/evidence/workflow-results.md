# Local workflow command results

All commands below ran from exports of 01d23393ebe5bfd63d8bcafc01859c3b146021d2. Each exit is the direct subprocess exit; this is macOS execution, not a claim of local Ubuntu execution.

| Runtime | Command | Exit | Evidence | validation-1 retained record |
| --- | --- | --- | --- | --- |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/lint-skills.py` | 0 | matrix-01-lint-skills.log | run recorded |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_lint_skills.py` | 0 | matrix-02-test_lint_skills.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_design_surfaces.py` | 0 | matrix-03-test_design_surfaces.log | run recorded |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_adr_doc_checks.py` | 0 | matrix-04-test_adr_doc_checks.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_poc_readme.py` | 0 | matrix-05-test_poc_readme.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_comment_ratio.py` | 0 | matrix-06-test_comment_ratio.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_number_guards.py` | 0 | matrix-07-test_number_guards.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/extensions/codex/test_codex_review.py` | 0 | matrix-08-test_codex_review.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/extensions/roborev/test_roborev_gate.py` | 0 | matrix-09-test_roborev_gate.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/extensions/copilot/test_copilot_review.py` | 0 | matrix-10-test_copilot_review.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/extensions/journey-map/test_map_footprint.py` | 0 | matrix-11-test_map_footprint.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py` | 0 | matrix-12-test_release_acceptance.log | run recorded |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_dispatch_records.py` | 0 | matrix-13-test_dispatch_records.log | run recorded |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_delivery_gate.py` | 0 | matrix-14-test_delivery_gate.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_validation_security.py` | 0 | matrix-15-test_validation_security.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_pr_watch.py` | 0 | matrix-16-test_pr_watch.log | run recorded |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_replay_dispatch.py` | 0 | matrix-17-test_replay_dispatch.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_decision_ledger.py` | 0 | matrix-18-test_decision_ledger.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_package_version.py` | 0 | matrix-19-test_package_version.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_workflow_checkout.py` | 0 | matrix-20-test_workflow_checkout.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_observer_check.py` | 0 | matrix-21-test_observer_check.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_merge_audit.py` | 0 | matrix-22-test_merge_audit.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_role_triggers.py` | 0 | matrix-23-test_role_triggers.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_laws_check.py` | 0 | matrix-24-test_laws_check.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_learning.py` | 0 | matrix-25-test_learning.log | no run record |
| Python 3.11.14 | `SPACEDOCK_BIN="$HOME/.local/bin/spacedock" python3 kc-dev-flow-2/scripts/test_dispatch_stage.py` | 0 | matrix-26-test_dispatch_stage.log | no run record |
| Python 3.11.14 | `python3 kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root "$GITHUB_WORKSPACE/.sd-plugin-root"` | 0 | matrix-27-test_sd_dispatch.log | no run record |
| Python 3.11.14 | `SPACEDOCK_BIN="$HOME/.local/bin/spacedock" python3 kc-dev-flow-2/scripts/test_observer_recovery.py` | 0 | matrix-28-test_observer_recovery.log | no run record |
| Node 24.18.0 | `npm ci` | 0 | npm-ci-network.log | installation attempt cancelled; not passed |
| Node 24.18.0 | `npm run doctor` | 0 | node24-doctor-isolated.log | no run record |
| Node 24.18.0 | `npm run typecheck` | 0 | journey-typecheck.log | no run record |
| Node 24.18.0 | `node --test lib/*.test.mjs` | 0 | journey-tests.log | only progress/schema subset; not this full command |
| Node 24.18.0 | `bash scripts/canvas-smoke.sh` | 0 | journey-smoke.log | no run record |
| Node 22.13.0 | `npm ci` | 0 | node22-install.log | installation attempt cancelled; not passed |
| Node 22.13.0 | `npm run doctor` | 0 | node22-doctor-isolated.log | no run record |
| Node 22.13.0 | `npm run typecheck` | 0 | node22-typecheck.log | no run record |
| Node 22.13.0 | `node --test lib/*.test.mjs` | 0 | node22-tests-complete-export.log | only progress/schema subset; not this full command |
| Node 22.13.0 | `bash scripts/canvas-smoke.sh` | 0 | node22-smoke.log | no run record |

## Setup and failed attempts

- Checkout/setup-node actions were substituted by exact git archives and the named native runtimes. Both dependency installations were fresh `npm ci`.
- The hosted Linux amd64 Spacedock installation shell block was not executed on macOS. Native Spacedock 0.27.2 and source pin 4d158a484ec73e184861067f8ed1e20087fdc26a were used; workflow-setup.json records this substitution. The actual hosted installers passed in hosted-dev2.json and hosted-journey.json.
- The sandboxed npm install was interrupted (exit 130); the same command with network access exits 0 in npm-ci-network.log.
- The initial Node 22 doctor exits 1 because this host already has listeners on 5858/3737. Both native doctor reruns use the supported settings JOURNEY_API_PORT=63791 and JOURNEY_CANVAS_PORT=63792 and exit 0; no other server was stopped. The original sandboxed Node 24 port observation is not relied on.
- The first Node 22 export included only kc-journey-map and therefore lacked the root ADR used by schemas.test.mjs; node22-tests.log shows one failure. Extracting the complete same-head repository, without changing tests or product files, yields 276/276 passing in node22-tests-complete-export.log.
- validation-1 had records for only five of the 28 full dev2 commands (lint, design, consumer, dispatch records, watch); the other 23 have no execution record. It ran only the 21 progress/schema producer tests, not the 276-test model command. Its npm installation attempt was cancelled, and doctor/typecheck/canvas-smoke have no record.
- CI definitions are byte-identical; cost per PR is unmeasured.
