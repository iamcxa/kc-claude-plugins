## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: e9b04927c24411a57617522ce4d55c32a74ab2f5
BRANCH: feature/dev-94-ac2-r4-static-check-weakest-sufficient
BASE_SHA: 030a0bb763463bed8c97ff1f1af9c00c2565cd5f
FILES: scripts/ship-flow/accept-evidence.sh,scripts/fixtures/ship-flow/mutant-negation-variant.md,scripts/fixtures/ship-flow/real-AC367-r2.md,scripts/fixtures/ship-flow/real-AC4-r3-s29.md,scripts/fixtures/ship-flow/real-AC5-r2.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
WITHOUT_IT_COMMAND: python3 scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_REMOVED_VARIANT: git show 030a0bb763463bed8c97ff1f1af9c00c2565cd5f:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
AC-1: scripts/fixtures/ship-flow/real-AC5-r2.md ACCEPTED; AC-3 line: AC-3 WARN (variant restores 1 of 3 changed read paths)
AC-2: scripts/fixtures/ship-flow/real-AC367-r2.md ACCEPTED; AC-3 line: AC-3 PASS (all changed read paths restored)
AC-3: scripts/fixtures/ship-flow/real-AC4-r3-s29.md REFUSED naming out-of-tree path /home/vercel-sandbox/.claude/plugins/marketplaces/pm-skills/skills
AC-4: scripts/fixtures/ship-flow/mutant-negation-variant.md REFUSED as altering no changed read path: docs/dev/README.md
AC-5_TABLE: DEV-90 ACCEPT→ACCEPT | DEV-91 REFUSE→REFUSE | DEV-92 ACCEPT→ACCEPT | mutant-command-not-found REFUSE→REFUSE | mutant-drop-path REFUSE→ACCEPT(WARN) | mutant-extra-path ACCEPT→ACCEPT | mutant-negation-variant N/A→REFUSE | mutant-out-of-tree REFUSE→REFUSE | mutant-prose-after-semicolon REFUSE→REFUSE | mutant-sha-mismatch REFUSE→REFUSE | mutant-unparseable REFUSE→REFUSE | control-double-assert ACCEPT→ACCEPT | real-AC5-r2 REFUSE→ACCEPT(WARN) | real-AC367-r2 REFUSE→ACCEPT(PASS) | real-AC4-r3-s29 REFUSE→REFUSE
AC-6_TABLE: git show <sha>:<path> > | git show abc123:docs/test.md > docs/test.md | docs/test.md | git checkout <sha> -- | git checkout abc123 -- docs/test.md | docs/test.md | git rm [-f] | git rm -f docs/test.md | docs/test.md | rm [-f] | rm -f docs/test.md | docs/test.md | sed -i[...] | sed -i 's/old/new/' docs/test.md | docs/test.md | > redirection | > docs/test.md | docs/test.md | >> redirection | >> docs/test.md | docs/test.md | mv <path> | mv docs/test.md docs/new.md | docs/test.md
AC-7: python3 scripts/kc-dev-flow-contract-test.py -> exit 0 PASS
BLOCKER: none
