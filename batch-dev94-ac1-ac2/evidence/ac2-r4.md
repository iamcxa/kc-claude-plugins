You are a kc-dev-flow build-stage worker in a disposable cloud workspace. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. No Linear access. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

Your Evidence is read by the station you are fixing: `CANDIDATE_SHA` read after the final push and confirmed against `git ls-remote`; `WITHOUT_IT_COMMAND` one line, no prose, no exit-masking, nothing read outside the tree, exit 0 at candidate and a real non-zero at base; `SURFACE:` lines, one per file, commands in the slots. Commit scope `ship-flow`.

## Round 4 of DEV-94 AC-2 — the hardening is right about what it refuses and wrong about what it lets through

Your base is round 3, `030a0bb763463bed8c97ff1f1af9c00c2565cd5f` on `feature/dev-94-ac2-r3-accept-station-fail-closed`. It passes its seven acceptance criteria. Run against four real Evidence blocks the First Officer accepted or refused on 2026-09-05 it gets two of them wrong, both in the refusing direction (S30):

| block | FO verdict | round-3 station | why the station is wrong |
|---|---|---|---|
| `worker-evidence-AC5-r2-accepted.md` | accept | REFUSE (AC-3: plan-lint.py, fixture not restored) | variant is `rm -f docs/plan-flow/plan-lint.py` — a plain `rm -f` is invisible to `extract_variant_paths`, which only knows `git show X:path` and `git rm` |
| `worker-evidence-AC367-r2-accepted.md` | accept | REFUSE (AC-3: fixture not restored) | command is `plan-lint.py lint <fixture> \| grep ...`; the fixture is an input the command reads, not the surface under test; the variant restores the lint, which is the surface |
| `worker-evidence-AC4-r3-refused.md` | refuse (S29) | REFUSE (out-of-tree) | correct |
| `worker-evidence-AC2-r3-hardening-accepted.md` | accept | ACCEPT | correct |

Two changes, and the four blocks become fixtures so this cannot regress silently.

## Step 1 — work item and Brief

Write this file byte-for-byte to `.context/DEV-94-AC2-r4-work-item.md`:

```markdown
---
title: "POC 4 AC-2 round 4: the static without-it check refuses a no-op variant and warns on a partial one, and sees every way a variant can alter a path"
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
issue: DEV-94
pr:
mod-block:
---

## The problem

The accept station's static check (AC-3) asks whether the removed variant restores every path the command reads. Two things are wrong with that. The variant extractor recognises only `git show <sha>:<path> > <path>` and `git rm`, so `rm -f <path>`, `sed -i ... <path>`, `git checkout -- <path>`, and a bare `> <path>` redirection are read as touching nothing, and a variant that plainly deletes the surface is refused as a no-op. And the rule is over-strict: a real command reads its inputs — `plan-lint.py lint <fixture>` reads the fixture — and those inputs are not the surface; demanding they be restored refuses every pair whose command reads a fixture, which on 2026-09-05 was every good pair. The class the strict rule guards, a variant narrower than the command, has no recorded instance (S24 was corrected: DEV-91 failed at the base, not on a narrow variant).

## Accepted outcome

The variant extractor recognises every shape a variant alters a path with: `git show <sha>:<path> > <path>`, `git checkout <sha> -- <path>`, `git rm [-f] <path>...`, `rm [-f] <path>...`, `sed -i[...] ... <path>`, `> <path>` and `>> <path>` redirections, and `mv <path> ...`. The AC-3 rule becomes: compute the read paths the candidate changed (intersection of the command's read paths with `git diff --name-only BASE_SHA..CANDIDATE_SHA`); REFUSE naming the paths when the variant alters none of them; WARN naming the unrestored ones when it alters some but not all, and continue to the base run. Paths the command reads that the candidate did not change are inputs and are ignored by this rule. Everything else in the station is unchanged.

Falsifier and stop: either FO-accepted real block is still refused; the S29 block or the negation block is accepted; or any of the eleven existing fixtures changes outcome except `mutant-drop-path`, whose documented outcome changes from REFUSE to ACCEPT-with-WARN (its variant restores one of two changed read paths).

## Non-goals

- Do not touch the base run, the out-of-tree check, the 126/127 check, or the SHA check.
- Do not change the Evidence block format.
- Do not write to Linear or open a PR.

## Acceptance criteria

- **AC-1** `scripts/fixtures/ship-flow/real-AC5-r2.md` (a copy of `worker-evidence-AC5-r2-accepted.md`) is ACCEPTED; recorded with the AC-3 line it prints.
- **AC-2** `scripts/fixtures/ship-flow/real-AC367-r2.md` is ACCEPTED, with a WARN or no AC-3 finding — say which and why; recorded.
- **AC-3** `scripts/fixtures/ship-flow/real-AC4-r3-s29.md` is REFUSED naming the out-of-tree path; recorded.
- **AC-4** A block whose variant is `! <the command>` (the AC-4 round-2 shape) is REFUSED as altering no changed read path; committed as `mutant-negation-variant.md`; recorded.
- **AC-5** Every existing fixture's before/after outcome in a table; only `mutant-drop-path` may change, and its new outcome is ACCEPT with a WARN naming the unrestored path. Recorded.
- **AC-6** For each recognised variant shape, one line in the block's Evidence showing the extractor returns the path (a tiny table: shape, sample, extracted path).
- **AC-7** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured.
```

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-94-AC2-r4-work-item.md --local-profile docs/dev/README.md --format text

## Step 3 — the four real blocks

```
git fetch origin spacedock-state/dev
git show origin/spacedock-state/dev:batch-dev95-mechanical/evidence/worker-evidence-AC5-r2-accepted.md
git show origin/spacedock-state/dev:batch-dev95-mechanical/evidence/worker-evidence-AC367-r2-accepted.md
git show origin/spacedock-state/dev:batch-dev95-mechanical/evidence/worker-evidence-AC4-r3-refused.md
git show origin/spacedock-state/dev:batch-dev94-ac1-ac2/evidence/worker-evidence-AC2-r3-hardening-accepted.md
```

Their `BASE_SHA`/`CANDIDATE_SHA` point at real commits on `origin`; fetch `origin/main` and the branches named in their `BRANCH:` lines so the SHA and base-run checks can resolve them (`feature/dev-95-ac5-plan-flow-lint-in-repo-r2`, `feature/dev-95-ac367-three-lint-rules-r2`, `feature/dev-95-ac4-dialectic-in-repo-r3`, `feature/dev-94-ac2-r3-accept-station-fail-closed`).

## Step 4 — commit and push

- git fetch origin feature/dev-94-ac2-r3-accept-station-fail-closed && git checkout -b feature/dev-94-ac2-r4-static-check-weakest-sufficient 030a0bb763463bed8c97ff1f1af9c00c2565cd5f
- Stage only the files you changed or added; never `git add .`.
- One commit: fix(ship-flow): refuse only a variant that alters no changed read path, and recognise every way a variant alters one
- git push origin HEAD:refs/heads/feature/dev-94-ac2-r4-static-check-weakest-sufficient
- No PR, no Linear.

## Step 5 — final reply: exactly one fenced block

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-94-ac2-r4-static-check-weakest-sufficient
BASE_SHA: 030a0bb763463bed8c97ff1f1af9c00c2565cd5f
FILES: <comma-separated>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <path> -> <AC-N> | <command> | <command>
WITHOUT_IT_COMMAND: <one line>
WITHOUT_IT_REMOVED_VARIANT: <one line>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
AC-1..AC-4: <one line each>
AC-5_TABLE: <before/after per fixture>
AC-6_TABLE: <shape | sample | extracted>
BLOCKER: none | <what stopped you and at which step>
```
