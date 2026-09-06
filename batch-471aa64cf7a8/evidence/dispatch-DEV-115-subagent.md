You are a kc-dev-flow build-stage worker running as a LOCAL subagent for a Pilot item, DEV-115. Work only inside your own git worktree; never touch the repository checkout you were launched from. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. Do NOT read or write Linear. Do NOT open a pull request. Do NOT run `git add .`.

Set up first:
- REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1 ; git -C "$REPO" fetch origin main
- WT=$(mktemp -d)/wt ; git -C "$REPO" worktree add "$WT" __BASE__ ; cd "$WT" — every command below runs in $WT.
- git checkout -b feature/dev-115-b1-kc-ship-flow-plugin-skeleton-manifests-marketplace-entry
- When done, push with `git push origin HEAD:refs/heads/feature/dev-115-b1-kc-ship-flow-plugin-skeleton-manifests-marketplace-entry` and leave the worktree in place.

## Brief (DEV-115, profile pilot-product-slice)

## The problem

Ship-flow's stations live as loose repo scripts under `scripts/ship-flow/` with their principles in a prose section of the deprecated `docs/ship-flow/README.md`; nothing versions them, so a principle change is a README edit per adopter (Captain ruling 2026-09-06: ship, dev, plan are three independent units connected only by input/output contracts).

## Accepted outcome

A `kc-ship-flow/` plugin directory exists on `main` with `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, a marketplace entry, a release-please component (`initial-version` policy 0.1.0, `exclude-paths` set so a path-less commit cannot bump it), a CI job triggered only on `kc-ship-flow/**` that runs `kc-ship-flow/scripts/contract-test.py` (initially empty but exit 0), and `references/kernel.md` holding only the heading and the three-flow independence sentence. `scripts/version-parity-check.sh` passes with the eighth plugin. Falsifier: remove the marketplace entry → parity check fails closed.

## Non-goals

* Moving any station script (B2).
* Writing kernel principles (B3).
* A skill (comes with B5's commission).

## Acceptance criteria

* **AC-1** `test -d kc-ship-flow` exits 0 on main and `scripts/version-parity-check.sh` exits 0 with eight plugins
* **AC-2** the B1 CI job runs `kc-ship-flow/scripts/contract-test.py` on a PR touching only `kc-ship-flow/` and its log shows exit 0
* **AC-3** a PR touching only `docs/` does not run the kc-ship-flow job (workflow run list prints none)

Re-verified: `test -d kc-ship-flow` exit 1 2026-09-06

## Implementation notes from the First Officer

Read `release-please-config.json`, `.release-please-manifest.json`, `.claude-plugin/marketplace.json`, `kc-pr-flow/.claude-plugin/plugin.json`, `kc-pr-flow/.codex-plugin/plugin.json`, `.github/workflows/marketplace-parity.yml` and `scripts/version-parity-check.sh` first and mirror their shape exactly for the eighth plugin `kc-ship-flow` (version 0.1.0 in every place the parity check compares; description: 'Batch delivery for kc-dev-flow adopters: dispatch, accept by evidence, review, e2e gate, UAT handoff, close receipt'). Add a new workflow file `.github/workflows/kc-ship-flow.yml` with `paths: [kc-ship-flow/**]` running `python3 kc-ship-flow/scripts/contract-test.py` (which for now prints one line and exits 0). `kc-ship-flow/references/kernel.md` contains only the H1 and this sentence: 'plan-flow, kc-dev-flow and kc-ship-flow are independent units connected only by versioned input/output contracts; this kernel cites neither of the others.' Run `bash scripts/version-parity-check.sh` and `bash scripts/marketplace-verify.sh` if present and record their exits. Commit scope: `feat(kc-ship-flow): …`.

Stage only the files you changed or added. Add no comment line that narrates the change. Run `python3 scripts/kc-dev-flow-contract-test.py` (generous timeout, do not abort) and, once it exists, `python3 kc-ship-flow/scripts/contract-test.py`; record both exits. ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace).

WITHOUT_IT_COMMAND: one self-contained shell line, exits 0 at the candidate and non-zero at BASE_SHA because the behaviour is absent there; reads nothing outside the repository; no `|| echo` / `|| true`; not `test -f`. WITHOUT_IT_REMOVED_VARIANT: one line that alters a read path you changed; after applying it the command exits non-zero. Observe all three exits yourself. Before the final reply write the block to `.context/evidence.md` (create `.context/`, gitignored) and run `bash <path-to-accept-evidence.sh in your tree> .context/evidence.md`; paste its last line as SELF_CHECK. Read CANDIDATE_SHA with `git rev-parse HEAD` AFTER the push and confirm it equals `git ls-remote origin feature/dev-115-b1-kc-ship-flow-plugin-skeleton-manifests-marketplace-entry`.

Final reply: exactly one fenced block, no prose after it:

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-115-b1-kc-ship-flow-plugin-skeleton-manifests-marketplace-entry
BASE_SHA: __BASE__
FILES: <comma-separated>
TESTS: <command> -> exit <code>; <command> -> exit <code>
SURFACE: <path> -> <AC-N> | <command that proves the file earns its place> | <command that removes exactly its contribution>
WITHOUT_IT_COMMAND: <one line>
WITHOUT_IT_REMOVED_VARIANT: <one line>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
SELF_CHECK: <last line printed by accept-evidence.sh>
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: <observed>
AC-2: <observed>
AC-3: <observed>
BLOCKER: none | <what stopped you and at which step>
```
