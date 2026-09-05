## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 6fee7d1f5bcc94e89131cb82bb417fd3f80fb54b
BRANCH: feature/dev-94-ac2-accept-evidence-station-r2
BASE_SHA: 13c31d19574989751db96395dd5d8ca406ebd77f
FILES: scripts/ship-flow/accept-evidence.sh,scripts/fixtures/ship-flow/DEV-90.md,scripts/fixtures/ship-flow/DEV-91.md,scripts/fixtures/ship-flow/DEV-92.md,scripts/fixtures/ship-flow/mutant-drop-path.md,scripts/fixtures/ship-flow/mutant-extra-path.md,scripts/fixtures/ship-flow/mutant-sha-mismatch.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/accept-evidence.sh -> AC-1 | test -f scripts/ship-flow/accept-evidence.sh && grep -q "AC-1.*BASE_SHA" scripts/ship-flow/accept-evidence.sh | git show 13c31d19574989751db96395dd5d8ca406ebd77f:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh
WITHOUT_IT_COMMAND: test -f scripts/ship-flow/accept-evidence.sh && grep -q "AC-1.*BASE_SHA" scripts/ship-flow/accept-evidence.sh
WITHOUT_IT_REMOVED_VARIANT: git show 13c31d19574989751db96395dd5d8ca406ebd77f:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
FIXTURE_DEV90: 0 | ACCEPT - command exits non-zero at base (exit 1 when removed)
FIXTURE_DEV91: 1 | REFUSE - AC-1 catches the pair that cannot fail: WITHOUT_IT_COMMAND already exits 0 at BASE_SHA 00d2dbf5
FIXTURE_DEV92: 0 | ACCEPT - command exits non-zero at base (exit 1 when removed)
MUTANT_DROP_PATH: 1 | REFUSE - AC-3 static path check catches unrestored path docs/ship-flow/README.md (command reads two files, variant restores one)
MUTANT_EXTRA_PATH: 0 | ACCEPT - AC-3 accepts variant that restores all command paths even with extra paths
MUTANT_SHA_MISMATCH: 1 | REFUSE - AC-4 catches invalid CANDIDATE_SHA as unreachable
BLOCKER: none
```