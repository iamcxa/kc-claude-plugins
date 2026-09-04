## Evidence

CANDIDATE_SHA: aafa538b5c70485f88d5c22ffbc4682a3f5a46aa
BASE_SHA: 4bc79749fc0ce9e8563d067a92c5ebead6b87976

SURFACE: .github/workflows/marketplace-parity.yml -> AC-1 | grep -n forge-phase2-runner-contract.test.py .github/workflows/marketplace-parity.yml | git checkout 4bc79749 -- .github/workflows/marketplace-parity.yml
SURFACE: kc-dev-flow/skill-scenarios/choose-work-profile.scenarios.yaml -> AC-4 | grep -n schema: kc-dev-flow/skill-scenarios/choose-work-profile.scenarios.yaml | git rm kc-dev-flow/skill-scenarios/choose-work-profile.scenarios.yaml
SURFACE: kc-dev-flow/skill-scenarios/continue-dev-flow.scenarios.yaml -> AC-4 | grep -n schema: kc-dev-flow/skill-scenarios/continue-dev-flow.scenarios.yaml | git rm kc-dev-flow/skill-scenarios/continue-dev-flow.scenarios.yaml
SURFACE: kc-plugin-forge/README.md -> lifecycle:machine-dependency-disclosure | grep -n PyYAML kc-plugin-forge/README.md | git checkout 4bc79749 -- kc-plugin-forge/README.md
SURFACE: kc-plugin-forge/docs/architecture.md -> lifecycle:project-context-maintenance | grep -n skill-runner.py kc-plugin-forge/docs/architecture.md | git checkout 4bc79749 -- kc-plugin-forge/docs/architecture.md
SURFACE: kc-plugin-forge/docs/commands.md -> lifecycle:project-context-maintenance | grep -n "clean runner" kc-plugin-forge/docs/commands.md | git checkout 4bc79749 -- kc-plugin-forge/docs/commands.md
SURFACE: kc-plugin-forge/reference/clean-profile-test.sh -> AC-1 | grep -n SKILL_RUNNER_MODEL kc-plugin-forge/reference/clean-profile-test.sh | git checkout 4bc79749 -- kc-plugin-forge/reference/clean-profile-test.sh
SURFACE: kc-plugin-forge/reference/parallel-forge.md -> safety-boundary | grep -n skill-runner.py kc-plugin-forge/reference/parallel-forge.md | git checkout 4bc79749 -- kc-plugin-forge/reference/parallel-forge.md
SURFACE: kc-plugin-forge/reference/skill-runner.py -> AC-1 | python3 kc-plugin-forge/reference/skill-runner.py bare /nonexistent-scenario-file.yaml T1 red kc-dev-flow | git rm kc-plugin-forge/reference/skill-runner.py
SURFACE: kc-plugin-forge/reference/skill-scenarios.md -> AC-4 | grep -n forge-skill-scenarios/v1 kc-plugin-forge/reference/skill-scenarios.md | git rm kc-plugin-forge/reference/skill-scenarios.md
SURFACE: kc-plugin-forge/skills/kc-plugin-forge-sanitize-check/SKILL.md -> safety-boundary | grep -n skill-scenarios kc-plugin-forge/skills/kc-plugin-forge-sanitize-check/SKILL.md | git checkout 4bc79749 -- kc-plugin-forge/skills/kc-plugin-forge-sanitize-check/SKILL.md
SURFACE: kc-plugin-forge/skills/kc-plugin-forge/SKILL.md -> AC-1 | grep -n skill-runner.py kc-plugin-forge/skills/kc-plugin-forge/SKILL.md | git checkout 4bc79749 -- kc-plugin-forge/skills/kc-plugin-forge/SKILL.md

BLOCKER: none
