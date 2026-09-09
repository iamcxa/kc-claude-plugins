## Evidence
DISPATCH_TOKEN: dev154-2026-09-10-r4
CANDIDATE_SHA: 07608ef2468422184048e9607c704fdf1097561a
BRANCH: feature/dev-154-kc-ship-flow-first-officer-skill-scripts-are-named-by
BASE_SHA: 6b408ac102978d4bbf3614a7109934191520aa9b
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

## moved_base (07608ef2): main (#401, #403) merged into the branch; SKILL.md and e2e-gate.md resolved keeping both intents; FO: contract-test 0, 0 repo-relative prefixes.
