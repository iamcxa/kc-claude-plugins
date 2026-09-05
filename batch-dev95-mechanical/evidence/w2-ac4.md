You are a kc-dev-flow build-stage worker in a disposable cloud workspace for a POC item. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. You have NO Linear access and must not try to get any. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

Two defects refused earlier rounds of sibling items; do not repeat them. (1) Read `CANDIDATE_SHA` with `git rev-parse HEAD` AFTER your final push and confirm it equals `git ls-remote origin <branch>`. (2) Your `WITHOUT_IT_COMMAND` must exercise behaviour an acceptance criterion names, never `test -f <file>`. (3) Commit scope is `plan-flow`: these files are repo-owned workflow docs under `docs/plan-flow/` and `scripts/plan-flow/`, not the kc-dev-flow plugin. (4) Do not edit `scripts/kc-dev-flow-contract-test.py`; a sibling item owns that file this round and two edits would conflict.

## Step 1 — work item and Brief

Write this file byte-for-byte to `.context/DEV-95-AC4-work-item.md` (create `.context/`; gitignored):

```markdown
---
title: "POC 3 AC-4: the plan dialectic lives in the repository, in this repository's own words, with the refusal check before any persona"
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

The plan dialectic — the stations that turn a raw requirement into a Development Brief — exists only as a draft in a POC's evidence directory on the state branch. Two Codex reviews of DEV-89 found that its stations 3 and 4 were the CC BY-NC-SA pm-skills templates with the words changed (if/then hypothesis plus validation measures; workflow-step / rule / data splits), which is still a derivative work and cannot ship in this public repository. The same reviews found the refusal check sat after station 1, so a persona was written for an evidence-free requirement before anyone asked whether there was evidence; that a discovery assignment could be "go interview someone" with no observation or payment required; and that station 4 had no question that would have caught DEV-91, an Issue whose whole deliverable was a by-product of the Issue before it (S26). Station 0 (re-verify the observation) was added on 2026-09-04 and is in the state-branch copy.

## Accepted outcome

`docs/plan-flow/dialectic.md` holds stations 0 through 4 and the refusal seam, in this order: station 0, refusal seam, stations 1–4. The refusal seam names the four things it demands (a behaviour, a current workaround with a cost, one named human, one observation) and states that no persona, no "who bleeds", and no Project may be written until it passes; when it refuses, the discovery assignment it hands back must name the observation it will produce or the payment it will ask for, never another interview. Stations 3 and 4 are rewritten from what this repository's Briefs actually need — `## Accepted outcome` with a `Falsifier:` line; an Issue cut whose Milestone is one recordable journey and whose `blockedBy` is a DAG — with no sentence, field list, or organizing structure taken from a pm-skills template; borrowed skills are named as a checklist to run after the fallback, never as the primary path. Station 4 gains the by-product question: for each Issue after the first in dispatch order, name one surface (a path, a rule, a data shape) it changes that no earlier Issue's cut already changes; an Issue that cannot name one is not cut.

`scripts/plan-flow/dialectic-derivation-check.sh <pm-skills-install-dir>` decides the licence question mechanically, in two layers: every 6-word window of stations 3 and 4 is grepped against every `.md` under the pm-skills install (verbatim layer), and a fixed list of pm-skills organizing terms (the if/then hypothesis frame, "validation measures", "tiny acts", "workflow-step / rule / data" splitting, and whatever else you find structuring their three skills) may not appear as section, list, or field structure in stations 3 and 4 (structural layer). Exit 0 clean; exit 1 naming the window or term and the pm-skills file it came from.

Falsifier and stop: the checker passes the state-branch original of stations 3 and 4 unchanged (then it is too weak to decide anything and the item stops until it does not); or the rewritten stations still fail either layer; or the refusal seam sits anywhere after station 1.

## Non-goals

- Do not vendor, quote, or paraphrase pm-skills or office-hours text into this repository; the checker exists to prove you did not.
- Do not edit `scripts/kc-dev-flow-contract-test.py`; pins for this file are a later item's.
- Do not change station 0's rule, only its position relative to the refusal seam.
- Do not write to Linear or open a PR.

## Acceptance criteria

- **AC-1** `docs/plan-flow/dialectic.md` exists with headings for station 0, the refusal seam, and stations 1–4 in that order; the refusal seam's text names the four demands and the observation-or-payment rule for a discovery assignment; station 4 carries the by-product question. Recorded as the heading list plus the two quoted rules.
- **AC-2** `scripts/plan-flow/dialectic-derivation-check.sh` run against the state-branch original of `dialectic.md` exits 1 and names at least one window or structural term with its source file. Recorded verbatim. If it exits 0, stop: the falsifier fired.
- **AC-3** The same checker run against the rewritten `docs/plan-flow/dialectic.md` exits 0. Recorded.
- **AC-4** The checker fails closed: run with a nonexistent install directory it exits 2 with a usage message, not 0. Recorded.
- **AC-5** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate (you did not edit it; this proves you broke nothing it pins).

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured.
```

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-95-AC4-work-item.md --local-profile docs/dev/README.md --format text
Follow the shared core, POC base, and build contract. Standalone item; the Brief is the planning authority.

## Step 3 — sources

```
git fetch origin spacedock-state/dev
git show origin/spacedock-state/dev:_archive/dev-89-plan-flow-dialectic-poc/evidence/runs/dialectic.md > /tmp/dialectic-original.md
git show origin/spacedock-state/dev:_archive/dev-89-plan-flow-dialectic-poc/evidence/codex-plan-round7.md   # the derivation and refusal findings
git show origin/spacedock-state/dev:_archive/dev-89-plan-flow-dialectic-poc/evidence/codex-round8.md
```

Install pm-skills ONLY to run the checker against it; it never enters the repository:
`claude plugin marketplace add deanpeters/Product-Manager-Skills && claude plugin install problem-statement@pm-skills epic-hypothesis@pm-skills user-story-splitting@pm-skills -y`, then locate the install with `claude plugin list` (typically under `~/.claude/plugins/`). Pass that directory to the checker. Do not read those skills to write your stations; write stations 3 and 4 from this repository's Brief shape first (see any `## Accepted outcome` / `## Acceptance criteria` in `docs/dev/.spacedock-state/*.md` on the state branch, and `kc-dev-flow/references/kernel.md`), then run the checker.

## Step 4 — commit and push

- git checkout -b feature/dev-95-ac4-dialectic-in-repo 1b61997b0ca78a6fbab281447f44a47238a8b524
- Stage only the files you changed or added; never `git add .`.
- One commit: feat(plan-flow): put the dialectic in the repository with stations 3 and 4 in our own words and the refusal seam first
- git push origin HEAD:refs/heads/feature/dev-95-ac4-dialectic-in-repo
- Do NOT open a pull request. Do NOT write to Linear.

## Step 5 — final reply: exactly one fenced block

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex, read after the final push and confirmed against ls-remote>
BRANCH: feature/dev-95-ac4-dialectic-in-repo
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: <comma-separated>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <one line per changed file: path -> AC-N | proving command | removing command>
WITHOUT_IT_COMMAND: <one self-contained shell line exercising an AC; exits 0 on the candidate, non-zero on the removed variant>
WITHOUT_IT_REMOVED_VARIANT: <removes every surface the command reads>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>
AC-1: <heading list; the two quoted rules>
AC-2: <checker on original: exit, first named window/term and source file>
AC-3: <checker on rewrite: exit>
AC-4: <checker with bad dir: exit and message>
BLOCKER: none | <what stopped you and at which step>
```
