You are a kc-dev-flow build-stage worker in a disposable cloud workspace for a POC item. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. You have NO Linear access and must not try to get any. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

Two defects refused earlier rounds of sibling items; do not repeat them. (1) Read `CANDIDATE_SHA` with `git rev-parse HEAD` AFTER your final push and confirm it equals `git ls-remote origin <branch>`. (2) Your `WITHOUT_IT_COMMAND` must exercise behaviour an acceptance criterion names, never `test -f <file>`. (3) Your commit scope must match the directory your files live in: these files are repo-owned workflow runtime under `docs/plan-flow/` and `scripts/`, so the scope is `plan-flow`, not `kc-dev-flow`.

## Step 1 — work item and Brief

Write this file byte-for-byte to `.context/DEV-95-AC5-work-item.md` (create `.context/`; gitignored):

```markdown
---
title: "POC 3 AC-5: plan-flow's lint, schemas, and validator live in the repository and can run offline"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-95
pr:
mod-block:
---

## The problem

plan-flow's mechanical half exists and has run twice (DEV-67, DEV-89), but none of it is on `main`. The eight-rule lint lives in a POC's evidence directory on the state branch, reads live Linear, and cannot be run by anyone without the API key; the close-receipt schema lives in a batch's receipt directory. Nothing pins any of it, so a refactor could delete the lint and no check would notice. Every plan round so far has started by copying files out of state-branch evidence by hand.

## Accepted outcome

`docs/plan-flow/plan-lint.py` runs the existing eight rules in two modes: `fetch <project-id> <snapshot.json>` writes the project snapshot with the same GraphQL query v0 uses today, and `lint <snapshot.json> [receipt.json]` runs the rules over a snapshot with no network. `kc-ship-close-receipt.v1.schema.json` joins the two schemas already under `docs/plan-flow/schema/`. The two recorded snapshots become fixtures under `scripts/fixtures/plan-flow/`, and `scripts/kc-dev-flow-contract-test.py` requires the new paths and runs `lint` over the correct-relations fixture expecting PASS. The rules themselves do not change: a known defect (L6 passes the inverted-relations fixture, S22) is reproduced and recorded here, and fixed by a separate item.

Falsifier and stop: `lint` over the correct-relations fixture produces a different PASS/FAIL outcome on any rule than the recorded run did; or the contract test still passes with `docs/plan-flow/plan-lint.py` deleted.

## Non-goals

- Do not add, remove, or change any lint rule; L6's known defect is out of scope here.
- Do not touch `dialectic.md`, the approval schema, or `validate-receipt.py`'s checks.
- Do not write to Linear or open a PR.

## Acceptance criteria

- **AC-1** `docs/plan-flow/plan-lint.py` exists, is executable, and `lint` mode runs with no network access (prove it: run with `https_proxy=http://127.0.0.1:9` set, or an equivalent that makes any network call fail, and record the command).
- **AC-2** `lint` over `scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json` prints the same eight rule outcomes as the recorded `lint-runA.txt` (all PASS, L6 order DEV-90, DEV-91, DEV-92); both outputs recorded side by side.
- **AC-3** `lint` over `scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json` reproduces v0's behaviour on L6 and the result is recorded verbatim, including the order it prints, as the baseline the L6 fix will be measured against.
- **AC-4** `scripts/kc-dev-flow-contract-test.py` requires `docs/plan-flow/plan-lint.py`, the three schema files, `docs/plan-flow/schema/validate-receipt.py`, and the two fixtures, and runs `lint` on the correct-relations fixture. Mutation recorded: with `docs/plan-flow/plan-lint.py` deleted the contract test exits non-zero naming it; restored, exit 0.
- **AC-5** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured.
```

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-95-AC5-work-item.md --local-profile docs/dev/README.md --format text
Follow the shared core, POC base, and build contract. Standalone item; the Brief is the planning authority.

## Step 3 — sources, all on the state branch

```
git fetch origin spacedock-state/dev
git show origin/spacedock-state/dev:plan-flow-fixtures/plan-lint.v0.py                            # the lint as it runs today
git show origin/spacedock-state/dev:plan-flow-fixtures/README.md                                  # what the two snapshots are
git show origin/spacedock-state/dev:plan-flow-fixtures/dev89-runA-correct-relations.snapshot.json
git show origin/spacedock-state/dev:plan-flow-fixtures/dev67-inverted-relations.snapshot.json
git show origin/spacedock-state/dev:batch-1016352e0223/receipt/kc-ship-close-receipt.v1.schema.json
git show origin/spacedock-state/dev:_archive/dev-89-plan-flow-dialectic-poc/evidence/lint-runA.txt  # AC-2's expected output
```

The snapshots are exactly what v0's GraphQL query returns for `project`, so `lint` mode is v0 with `d = json.load(...)` in place of the network call. v0's L4 imports `kc-dev-flow/scripts/linear-admission.py` from the working directory for its `section()` parser; keep that, it is on main. The inverted-relations project holds nine Issues; the S22 inversion is among DEV-64/65/66.

## Step 4 — commit and push

- git checkout -b feature/dev-95-ac5-plan-flow-lint-in-repo 1b61997b0ca78a6fbab281447f44a47238a8b524
- Stage only the files you changed or added; never `git add .`.
- One commit: feat(plan-flow): move the lint, schemas, and fixtures into the repository and pin them
- git push origin HEAD:refs/heads/feature/dev-95-ac5-plan-flow-lint-in-repo
- Do NOT open a pull request. Do NOT write to Linear.

## Step 5 — final reply: exactly one fenced block

Large artifacts go on the branch; the harness truncates a long final message near 10K characters.

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex, read after the final push and confirmed against ls-remote>
BRANCH: feature/dev-95-ac5-plan-flow-lint-in-repo
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: <comma-separated>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <one line per changed file: path -> AC-N | proving command | removing command>
WITHOUT_IT_COMMAND: <one self-contained shell line exercising an AC; exits 0 on the candidate, non-zero on the removed variant>
WITHOUT_IT_REMOVED_VARIANT: <removes every surface the command reads>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>
AC-1: <the no-network command and its exit>
AC-2: <recorded vs new, eight lines each>
AC-3: <L6 line verbatim on the inverted fixture>
AC-4: <mutation: exit and message with plan-lint.py deleted; exit restored>
BLOCKER: none | <what stopped you and at which step>
```
