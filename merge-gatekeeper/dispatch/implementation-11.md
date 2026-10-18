# implementation-11

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), phase 2 of the Cycle 2 repair: FO fix authorization
Model: sonnet

## Checklist

Apply the phase-1 fix in kc-dev-flow-2/scripts/delivery_gate.py: a grant passes only if its NNNN-*.md ADR exists under the adr-path, its Status reads Accepted, and the whole merge-grants entry appears in it delimited; NEVER_PATH gains .githooks/, .roborev.toml, repo-root scripts/ and hooks/ or bin/ at any depth; docs-only admits only .md files under docs/, other docs files class other; keep the new tests and add one for the Status rule
Run the listed mutations plus one dropping the Status rule, each turning its named case red (python3 -B, caches cleared); kc-dev-flow-2/scripts/lint-skills.py exits 0; all package test files pass; roborev evidence= line; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Number guards: ADR: 0023

Profile: prod. Task merge-gatekeeper, PR iamcxa/kc-claude-plugins#666, your existing worktree and branch. FO rulings on your four points: (a) non-.md docs files class other, as the Captain's ruling says; (b) repo-root scripts/ only, as ruled; (c) add the Accepted Status check, since a Proposed or Rejected ADR is not a grant and the rule is one read inside the ruled ADR check; (d) no evidence check, as ruled. If the new rules add README words, keep the merge-ask limit; a raise needs a Captain ruling. Commit the state report with `spacedock state commit merge-gatekeeper --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
