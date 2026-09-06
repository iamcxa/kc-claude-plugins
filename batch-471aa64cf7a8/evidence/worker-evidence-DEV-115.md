## Evidence
DISPATCH_TOKEN: dev115-2026-09-06-r2
CANDIDATE_SHA: 054ce4092b297f6cfbda458938f731cd6b6a09b7
BRANCH: feature/dev-115-b1-kc-ship-flow-plugin-skeleton-manifests-marketplace-entry
BASE_SHA: bb5377c30373add0fface212199fb7d9c244c30a
FILES: kc-ship-flow/references/kernel.md (r2),.claude-plugin/marketplace.json,.github/workflows/kc-ship-flow.yml,.release-please-manifest.json,kc-ship-flow/.claude-plugin/plugin.json,kc-ship-flow/.codex-plugin/plugin.json,kc-ship-flow/references/kernel.md,kc-ship-flow/scripts/contract-test.py,release-please-config.json
TESTS: bash scripts/version-parity-check.sh -> exit 0; bash scripts/marketplace-verify.sh -> exit 0; python3 kc-ship-flow/scripts/contract-test.py -> exit 0; python3 scripts/kc-dev-flow-contract-test.py -> exit 0; bash scripts/skill-frontmatter-lint.sh -> exit 0; bash kc-plugin-forge/scripts/plugin-release-contract-check.sh --repo . -> exit 0
SURFACE: kc-ship-flow/.claude-plugin/plugin.json -> AC-1 | bash scripts/version-parity-check.sh | git checkout bb5377c30373add0fface212199fb7d9c244c30a -- kc-ship-flow/.claude-plugin/plugin.json
SURFACE: .claude-plugin/marketplace.json -> AC-1 | bash scripts/version-parity-check.sh | git checkout bb5377c30373add0fface212199fb7d9c244c30a -- .claude-plugin/marketplace.json
SURFACE: .github/workflows/kc-ship-flow.yml -> AC-2,AC-3 | git log -1 --format=%H -- .github/workflows/kc-ship-flow.yml | git rm -f .github/workflows/kc-ship-flow.yml
WITHOUT_IT_COMMAND: [ "$(python3 -c "import json; print(len(json.load(open('.claude-plugin/marketplace.json'))['plugins']))")" = "8" ]
WITHOUT_IT_REMOVED_VARIANT: git checkout bb5377c30373add0fface212199fb7d9c244c30a -- .claude-plugin/marketplace.json
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: 2026-09-06T12:39:29Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: PASS — eight plugins pass version-parity
AC-2: PARTIAL — workflow added; not verified by a real Actions run (no PR per Brief); the FO verifies on the Draft PR
AC-3: PARTIAL — paths filter scoped to kc-ship-flow/**; verified on the Draft PR's run list
BLOCKER: none
