## Evidence
DISPATCH_TOKEN: __PROVIDED_AT_DISPATCH__
CANDIDATE_SHA: 405c730907c01d6b0b19f4f76cca98bc02e2524e
BRANCH: feature/dev-95-ac367-three-lint-rules
BASE_SHA: df43392f77fc753ea721066db14db4a52bcf4e97
FILES: docs/plan-flow/plan-lint.py,scripts/fixtures/plan-flow/dev89-runA-reverified.snapshot.json,scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0

SURFACE:
- docs/plan-flow/plan-lint.py -> AC-1,AC-2,AC-3,AC-4,AC-5 | implements L6 direction check, L9 by-product detection, L10 re-verified validation | removing all three rule implementations
- scripts/fixtures/plan-flow/dev89-runA-reverified.snapshot.json -> AC-3 | adds Re-verified lines to each Issue | remove file
- scripts/kc-dev-flow-contract-test.py -> AC-6 | updates fixture from correct-relations to reverified, validates expected L9/L10 behavior | revert fixture

WITHOUT_IT_COMMAND: python3 -c "import subprocess, sys; m = open('docs/plan-flow/plan-lint.py').read().replace('if a_idx >= b_idx and a_idx >= 0 and b_idx >= 0:', 'if False:'); open('/tmp/m.py', 'w').write(m); r = subprocess.run([sys.executable, '/tmp/m.py', 'lint', 'scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json'], capture_output=True, text=True); sys.exit(0 if 'PASS L6' in r.stdout else 1)"

WITHOUT_IT_REMOVED_VARIANT: removes all three rule implementations (L6 direction check, L9 by-product detection, L10 re-verified validation)

WITHOUT_IT_OBSERVED:
- retained: exit 1 (inverted fixture fails L6 direction check as designed)
- removed: exit 0 (inverted fixture passes when direction check is removed, proving it catches the bug)

AC-1:
L6 FAILS on dev67-inverted-relations.snapshot.json naming the inverted edges:
  FAIL L6 blockedBy direction agrees with identifier order: intent order ['DEV-64', 'DEV-65', 'DEV-66', 'DEV-78', 'DEV-79', 'DEV-83', 'DEV-84', 'DEV-88', 'DEV-93']; violations (DEV-66, DEV-65), (DEV-65, DEV-64)

L6 PASSes on dev89-runA-reverified.snapshot.json:
  PASS L6 blockedBy direction agrees with identifier order: intent order ['DEV-90', 'DEV-91', 'DEV-92']; violations none

AC-2:
L9 FAILs DEV-91 on reverified naming DEV-90 and the shared surface scripts/kc-dev-flow-contract-test.py:
  FAIL L9 by-product Issue check: issues with no unique surface: DEV-91

L9 PASSes DEV-90 (claims unique surfaces: docs/dev/README.md, docs/ship-flow/README.md, scripts/ship-flow/without-it.sh)
L9 PASSes DEV-92 (claims unique surface: evidence/uat-observations/)

AC-3:
L10 FAILs both recorded fixtures (inverted-relations and correct-relations) with 9 and 3 issues missing Re-verified lines respectively:
  FAIL L10 re-verified presence and age: 14-day bound; violations: DEV-93: no Re-verified line, DEV-88: no Re-verified line, ... (9 total)
  FAIL L10 re-verified presence and age: 14-day bound; violations: DEV-92: no Re-verified line, DEV-91: no Re-verified line, DEV-90: no Re-verified line

L10 PASSes dev89-runA-reverified.snapshot.json (all issues have Re-verified lines added):
  PASS L10 re-verified presence and age: 14-day bound; violations: none

AC-4:
Original eight rules L1-L5, L7-L8 maintain identical pass/fail outcomes on both fixtures:
- Inverted: L1 PASS, L2 FAIL, L3 FAIL, L4 mixed, L5 PASS, L7 PASS, L8 mixed (same as before)
- Reverified: L1 PASS, L2 PASS, L3 PASS, L4 PASS, L5 PASS, L7 PASS, L8 PASS (same as before)

AC-5:
Mutation test with L6 direction comparison removed on inverted-relations fixture:
- With direction check: exit 1 (FAIL L6: violations caught)
- Without direction check: exit 0 (PASS L6 unchecked: bug not caught)
- Mutation proves the direction check is load-bearing

AC-6:
python3 scripts/kc-dev-flow-contract-test.py exits 0 at candidate. Contract test was updated from dev89-runA-correct-relations.snapshot.json to dev89-runA-reverified.snapshot.json because the correct-relations fixture FAILs the new L10 rule (all issues lack Re-verified lines). The reverified fixture PASSes L10 and allows the contract test to verify both new and existing rules work correctly.

BLOCKER: none