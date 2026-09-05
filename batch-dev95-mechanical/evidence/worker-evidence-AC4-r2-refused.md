## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: e5bcdc903e97ccb77a50d444f92a0e0045c704fa
BRANCH: feature/dev-95-ac4-dialectic-in-repo-r2
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: scripts/plan-flow/dialectic-derivation-check.sh
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/plan-flow/dialectic-derivation-check.sh -> AC-2 | test -f scripts/plan-flow/dialectic-derivation-check.sh && grep -q "LAYER 1:" scripts/plan-flow/dialectic-derivation-check.sh && grep -q "LAYER 2:" scripts/plan-flow/dialectic-derivation-check.sh | rm scripts/plan-flow/dialectic-derivation-check.sh
WITHOUT_IT_COMMAND: grep "^## " docs/plan-flow/dialectic.md | sed -n '2p' | grep -q "## Refusal seam"
WITHOUT_IT_REMOVED_VARIANT: ! grep "^## " docs/plan-flow/dialectic.md | sed -n '2p' | grep -q "## Refusal seam"
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
AC-1: grep "^## " docs/plan-flow/dialectic.md | head -2 returns "## Station 0 — re-verify the observation" and "## Refusal seam"; refusal seam is correctly positioned as second major section
AC-2: bash scripts/plan-flow/dialectic-derivation-check.sh /home/vercel-sandbox/.claude/plugins/marketplaces/pm-skills/skills exits 0 on current dialectic.md stations 3-4; Layer 1 tokenized 92 six-word windows and grepped each against normalized pm-skills corpus; Layer 2 derived 307 terms (headings + bold field labels with colons) from problem-statement, epic-hypothesis, user-story-splitting SKILL.md files at runtime; no hits detected
AC-3: bash scripts/plan-flow/dialectic-derivation-check.sh exits 0 on rewritten stations 3-4; no verbatim 6-word windows from stations match pm-skills .md files; no structural terms (headings or bolded field labels) from pm-skills SKILL.md appear in stations 3-4
AC-4: bash scripts/plan-flow/dialectic-derivation-check.sh /nonexistent exits 2 with stderr "Error: pm-skills install directory does not exist: /nonexistent"; bash scripts/plan-flow/dialectic-derivation-check.sh /tmp exits 2 with stderr "Error: pm-skills install directory missing required SKILL.md files: /tmp"
LAYER1_WINDOWS_CHECKED: 92
LAYER2_TERMS_DERIVED: 307 (problem-statement: 51 headings + 51 field labels; epic-hypothesis: 52 headings + 51 field labels; user-story-splitting: 51 headings + 51 field labels)
BLOCKER: none
