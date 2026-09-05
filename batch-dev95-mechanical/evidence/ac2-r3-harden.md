You are a kc-dev-flow build-stage worker in a disposable cloud workspace for a POC item. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. No Linear access. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

Rules the accept station enforces on YOUR Evidence too: `CANDIDATE_SHA` read after the final push and confirmed against `git ls-remote`; `WITHOUT_IT_COMMAND` one line, no prose, no exit-masking (`|| echo`, `|| true`), nothing read outside the tree, exit 0 at candidate and a real non-zero at base (not 126/127). Commit scope `ship-flow`.

## Step 1 — work item and Brief

Write this file byte-for-byte to `.context/DEV-94-AC2-r3-work-item.md` (create `.context/`; gitignored):

```markdown
---
title: "POC 4 AC-2 round 3: the accept station fails closed on a command that did not run, an unparseable pair, and an out-of-tree read"
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

`scripts/ship-flow/accept-evidence.sh` (#373) accepted a block on 2026-09-05 whose `WITHOUT_IT_COMMAND` was `<checker> ~/.claude/plugins/... && echo clean || echo derivative; on candidate exits 0, on removed variant exits 1`. The worker had appended prose after a semicolon. `bash -c` ran `on` as a command, exited 127 at `BASE_SHA`, and the station read any non-zero as "the falsifier flips". The real command, run alone at the base, exits 0 — the trailing `echo` masks every exit code — so the pair cannot fail and the First Officer's manual run is what caught it (S29). The same block read a path under `~/.claude/`, outside the candidate tree, which the runtime README forbids and nothing checked. And when the station cannot extract paths from a command it prints `AC-3 SKIP` and continues, which is fail-open on exactly the inputs most likely to be wrong.

## Accepted outcome

The station refuses, naming the reason, when: the base run exits 126 or 127 (the command did not run, so nothing flipped); `WITHOUT_IT_COMMAND` or `WITHOUT_IT_REMOVED_VARIANT` reads or writes a path outside the repository — an absolute path, `~`, `$HOME`, or `..` escaping the root; the command's exit is masked by a trailing `|| <anything>` or `; true`; or AC-3 cannot extract a single path from the command (SKIP becomes REFUSE). Every previously accepted fixture still accepts and every previously refused fixture still refuses for the same reason.

Falsifier and stop: the S29 block is accepted; or any of the six existing fixtures changes outcome; or a legitimate command with `&&` between two real assertions is refused as masked.

## Non-goals

- Do not run the command at the candidate; the station's one execution stays the base run.
- Do not change the Evidence block format or the recorded fixtures' text.
- Do not write to Linear or open a PR.

## Acceptance criteria

- **AC-1** The S29 block, committed as `scripts/fixtures/ship-flow/mutant-prose-after-semicolon.md`, is refused naming the masked exit or the out-of-tree path — whichever the station checks first — and the refusal says which. Recorded.
- **AC-2** A block whose command is `nonexistent-tool --flag` is refused with "command did not run (exit 127)", not accepted as a flip. Committed as `mutant-command-not-found.md`; recorded.
- **AC-3** A block whose command is `cat ~/.claude/anything` is refused naming the out-of-tree path; committed as `mutant-out-of-tree.md`; recorded.
- **AC-4** A block whose command AC-3 cannot parse is refused, not skipped; committed as `mutant-unparseable.md`; recorded. Say what "cannot parse" means in the script's own terms.
- **AC-5** All six existing fixtures under `scripts/fixtures/ship-flow/` produce the same exit and the same reason as before your change. Recorded as a before/after table.
- **AC-6** A control: a command with two real assertions joined by `&&` and no trailing `||` is still accepted. Committed as `control-double-assert.md`; recorded.
- **AC-7** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured.
```

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-94-AC2-r3-work-item.md --local-profile docs/dev/README.md --format text
Follow the shared core, POC base, and build contract. Standalone item; the Brief is the planning authority.

## Step 3 — the S29 block

`git fetch origin spacedock-state/dev && git show origin/spacedock-state/dev:batch-dev95-mechanical/evidence/worker-evidence-AC4-r1-refused.md` — that is the block the station wrongly accepted. Its sibling `worker-evidence-AC5-r1-refused.md` was refused correctly (base exit really 0); keep it refusing.

## Step 4 — commit and push

- git checkout -b feature/dev-94-ac2-r3-accept-station-fail-closed 1b61997b0ca78a6fbab281447f44a47238a8b524
- Stage only the files you changed or added; never `git add .`.
- One commit: fix(ship-flow): refuse an Evidence pair whose command did not run, reads outside the tree, or cannot be parsed
- git push origin HEAD:refs/heads/feature/dev-94-ac2-r3-accept-station-fail-closed
- Do NOT open a pull request. Do NOT write to Linear.

## Step 5 — final reply: exactly one fenced block

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-94-ac2-r3-accept-station-fail-closed
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: <comma-separated>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <one line per changed file: path -> AC-N | proving command | removing command>
WITHOUT_IT_COMMAND: <one line>
WITHOUT_IT_REMOVED_VARIANT: <one line>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
AC-1..AC-6: <one line each: fixture, exit, reason>
AC-5_TABLE: <six lines before/after>
BLOCKER: none | <what stopped you and at which step>
```
