## Evidence
DISPATCH_TOKEN: dev154-2026-09-09-r3
CANDIDATE_SHA: a2a87725530bf62250b475fdae010506124df35d
BRANCH: feature/dev-154-kc-ship-flow-first-officer-skill-scripts-are-named-by
BASE_SHA: 39cb179be8af4bd71063d51ce7a58e646368e45d
FILES: docs/ship/README.md, kc-ship-flow/skills/first-officer/SKILL.md, kc-ship-flow/scripts/local-profile-check.py, contract-test.py, fixtures/adopter/docs/ship/README.md, 14 references/stations/*.md (path form)
TESTS: AC-1 local-profile-check.py adopter fixture from /tmp -> exit 0 (13 LOCAL_PROFILE_SCRIPT_OK lines); AC-2 grep -c 'kc-ship-flow/scripts/' SKILL.md -> 0; AC-3 contract-test -> exit 0
WITHOUT_IT_COMMAND: python3 kc-ship-flow/scripts/local-profile-check.py kc-ship-flow/scripts/fixtures/adopter/docs/ship/README.md | grep -q LOCAL_PROFILE_SCRIPT_OK
WITHOUT_IT_REMOVED_VARIANT: git show 39cb179be8af4bd71063d51ce7a58e646368e45d:kc-ship-flow/scripts/local-profile-check.py > kc-ship-flow/scripts/local-profile-check.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: accept-evidence: ACCEPT
BLOCKER: none

## FO verification at c4bd54cb
AC-1 from /tmp exit 0 with 13 OK lines; SKILL.md 0 repo-relative mentions, resolves SHIP_SCRIPTS from CLAUDE_PLUGIN_ROOT with a stated fallback; contract-test 0; FO pair: retained 0 / removed 1; 4 comment lines in local-profile-check.py; docs/ship/README.md script paths rewritten to the env-var form (review to confirm spacedock does not read them).

## Round 2 (a2a87725): intent.md converted; prefix guard over README + all station docs (FO mutation on uat-doc.md fails contract-test); stale 'nothing checks' claims rewritten; fallback = two levels above SKILL.md.
