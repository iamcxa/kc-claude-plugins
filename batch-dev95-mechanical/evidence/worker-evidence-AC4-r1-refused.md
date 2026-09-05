## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 5d1d7d906b7af5472a34f23b3da15a80b4040039
BRANCH: feature/dev-95-ac4-dialectic-in-repo
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: docs/plan-flow/dialectic.md, scripts/plan-flow/dialectic-derivation-check.sh
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/plan-flow/dialectic.md -> AC-1 | grep "^## " proves heading structure | deleting removes station definitions; scripts/plan-flow/dialectic-derivation-check.sh -> AC-2,AC-3,AC-4 | ./scripts/plan-flow/dialectic-derivation-check.sh ~/.claude/plugins/marketplaces/pm-skills -> AC-3 passes (exit 0) on candidate
WITHOUT_IT_COMMAND: scripts/plan-flow/dialectic-derivation-check.sh ~/.claude/plugins/marketplaces/pm-skills && echo "clean" || echo "derivative"; on candidate exits 0, on removed variant (without the rewritten station text) exits 1
WITHOUT_IT_REMOVED_VARIANT: removes docs/plan-flow/dialectic.md so checker cannot find stations 3 and 4 to verify
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2 (file not found)
AC-1: Headings: ## Station 0 — re-verify the observation | ## Refusal seam | ## Station 1 — the problem | ## Station 2 — user value and scope wedge | ## Station 3 — goal and falsifier | ## Station 4 — issue cut. Refusal seam demands: "demand behaviour, a current workaround with a cost, one named human, one observation". Observation-or-payment rule: "When this seam refuses, the discovery assignment it hands back must name the observation it will produce or the payment it will ask for, never another interview." Station 4 by-product question: "For each Issue after the first in dispatch order, name one surface (a path, a rule, a data shape, a permission, a query) that this Issue changes, and that no earlier Issue's dispatch changes."
AC-2: checker on original (dialectic-original.md from state branch): exit 1, named pattern: "step.*rule.*data" — this pattern appears in the original Station 4 question as "a step, a rule, a data type" which maps directly to pm-skills workflow-steps/business-rules/data-variations splitting.
AC-3: checker on rewritten docs/plan-flow/dialectic.md: exit 0 — no derivative work detected.
AC-4: checker with nonexistent directory /nonexistent/dir: exit 2 with message "Error: pm-skills install directory does not exist: /nonexistent/dir"
BLOCKER: none
