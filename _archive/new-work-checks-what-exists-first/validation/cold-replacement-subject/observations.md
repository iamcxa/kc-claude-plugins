# Cold dispatch observations

## Result

HELD before substantive ideation: the dispatch-authorized package root does not exist.

## Authorized context

- Assignment: `/tmp/validate-new-work-checks-20261113/cold-replay-2/dispatch.md`.
- Task: `design-surfaces-task-dir-crash`; stage: ideation; recorded variant: kc-dev-flow-2; recorded profile: pilot.
- Entity read successfully: `/tmp/validate-new-work-checks-20261113/cold-replay-2/wf/.spacedock-state/design-surfaces-task-dir-crash.md`.
- Installed `spacedock:ensign` shared core and Codex runtime adapter were read.
- Harness boundaries: only observations/proposal output files may be written; no state/product/Git metadata changes, commits, external writes, child agents, servers, browsers or databases.

## Evidence

1. Reading the required package skill failed with exit 1:
   `/tmp/validate-new-work-checks-20261113/cold-replay-2-2/candidate/kc-dev-flow-2/skills/ideation/SKILL.md`: No such file or directory.
2. `ls -ld /tmp/validate-new-work-checks-20261113/cold-replay-2-2` also reported No such file or directory.
3. The exact generated fetch command succeeded with exit 0:
   `/Users/kent/.local/bin/spacedock dispatch show-stage-def --workflow-dir /tmp/validate-new-work-checks-20261113/cold-replay-2/wf --stage ideation`.
4. The fetched stage definition explicitly says: “Missing skill or profile authority requires a hold report rather than a baseline or default-profile substitution.” It also forbids searching another location for package scripts.
5. A bounded file listing performed concurrently with the stage fetch found an alternative skill under `/tmp/validate-new-work-checks-20261113/cold-replay-2/candidate/kc-dev-flow-2/skills/ideation/SKILL.md`. I did not read it, substitute its root, or execute any package script. Its existence does not authorize replacing the explicit `cold-replay-2-2` package root.
6. No application tests, bug reproducer, implementation or design checks were run. The entity's historical reproduction remains a recorded claim, not a new result from this worker.

## Model identity

The exposed identity is Codex, based on GPT-6. No exact runtime model identifier is exposed in this worker context, so none is inferred.

## Scope and limits

No state or product file was modified. Only this observations file and the separate proposal file were written under the allowed subject-output directory. No child agent or peer/session contact occurred. Working-tree, open-PR, running-agent and task closure checks were not completed; no closure claim is made.
