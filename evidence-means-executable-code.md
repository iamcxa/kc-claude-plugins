---
id: d3xb3q0qwmjpkty23njq6t66
title: Make evidence mean executable code, so the exists count stops lying
status: implementation
source: captain
product: kc-team-ops
planning-window:
planning-outcome:
sprint: journey-map-poc
sprint-readiness: ready
started: 2026-09-10T04:24:57Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-evidence-means-executable-code
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:d3xb3q0qwmjpkty23njq6t66:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:d3xb3q0qwmjpkty23njq6t66-backlog-1
              briefing:
                id: briefing:d3xb3q0qwmjpkty23njq6t66:backlog:attempt-1:revision-1
                digest: sha256:0115adc27e4220103f15f6645bacce4921e2fef6a93b9371a1dc9d887ae9896a
                room-ref: ./evidence-means-executable-code/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:d3xb3q0qwmjpkty23njq6t66:backlog:1
                briefing: briefing:d3xb3q0qwmjpkty23njq6t66:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T04:22:45.065196Z"
                decision: approve
                reason: 'Captain: 先把 evidence 那個 glob 修掉,讓數字誠實了再切 — approving the fix before the plugin extraction, so the extraction carries an honest count rather than a documented lie.'
              application:
                target-stage: ideation
                state: consumed
---

## The problem

The exists count is inflated and the dogfood proved it. `lintEvidenceNotFound` runs
`git grep -l -w -F <symbol>` with no pathspec, so a story passes when its symbol appears
anywhere in the repository — including in prose. The tool's own journey cites
`AskUserQuestion` as evidence, and that string exists only in markdown, one match being an
unrelated skill's documentation. The board reports `12/12 exist` for release 1 on that basis.

A number that counts documentation as implementation is worse than no number, because it is
shown to a team as progress.

## Work profile receipt

**Profile:** POC — bounded exploration.

**Next decision:** whether the exists count can be made honest without losing stories whose
evidence legitimately is not a code symbol.

**Cheapest credible falsifier:** point a story's evidence at a string that exists only in
markdown and confirm the lint fails; point one at a real code symbol and confirm it passes.

**Budget:** one worker dispatch. No browser.

**Observable stop point:** the tool's own journey re-linted, and its exists count restated.

## Accepted outcome

`status: exists` means a symbol backed by something executable. Evidence found only in prose
fails the lint.

## Non-goals

- No cross-repository evidence. That is still a separate item.
- Do not raise evidence to "a passing test". That is a stronger tier and a separate decision;
  this task only stops prose counting as code.
- Do not change the story map's layout or any other projection.

## Acceptance evidence

**AC-1** A story whose evidence appears only in markdown fails `evidence-not-found`.
Demonstrated on a real case, not a constructed one: the current file's `AskUserQuestion`.

**AC-2** A story whose evidence is a real code symbol still passes. The lint has not simply
become stricter for everyone.

**AC-3** The tool's own journey file is re-examined and every story that no longer qualifies
is restated as `gap`, or given evidence that does qualify. Do not delete a story to make the
lint pass.

**AC-4** The exists count is reported before and after. A number that did not move means
either the fix or the demonstration is wrong.

**AC-5** A test covers the prose-only case with a mutation that only it catches.

## Route-back conditions

Return `poc_outcome` to planning.

## Measurement

The release-1 exists count before and after. It is 12/12 today and at least one of those is
documentation.

## Stage Report: implementation

- DONE: Restrict evidence matching to something executable, so a symbol found only in prose no longer counts as implemented.
  `kc-team-ops/lib/lint.mjs` `filesCiting` now filters `git grep` hits through `isExecutableFile` (a curated code-extension set plus `.github/workflows/*.yml`); commit f97e4ff8.
- DONE: Re-examine the tool's own journey and restate as gap any story whose evidence no longer qualifies, never deleting a story to make the lint pass.
  Of the 12 release-1 stories only `ask-which-boards-to-draw` (evidence `AskUserQuestion`) failed the new lint — that symbol names a host tool invoked per `SKILL.md` prose, with no code in this repo issuing the call. Restated `status: gap` with a `question` naming why, evidence field dropped (gap stories carry no evidence); the other 11 keep `evidence: <real .mjs symbol>` unchanged, in `kc-team-ops/skills/kc-journey-map/references/journey.example.yaml`.
- DONE: Report the release-1 exists count before and after; a number that did not move means the fix or the demonstration is wrong.
  Verified by stashing the fix and re-running against the original files: BEFORE — `node lib/journey-lint.mjs …` reports "all lints pass", release-1 exists = 12/12 (the lie). AFTER — same command on the fixed files still reports "all lints pass", release-1 exists = 11/12. The count moved by exactly the one story whose evidence was prose.

### Summary

`lintEvidenceNotFound`'s `git grep` had no pathspec, so a symbol quoted in a `SKILL.md` or reference doc satisfied the same check as a symbol backed by running code. Added an extension/path allowlist (`.mjs/.cjs/.js/.jsx/.mts/.cts/.ts/.tsx/.py/.rb/.sh/.bash/.zsh`, plus `.github/workflows/*.yml`) so prose and data files (`.md`, `.tldr`, the journey's own `.yaml`) never qualify as evidence on their own — CI workflows and shell scripts still do, per the task's explicit non-goal against over-restricting. Did not raise the tier to "passing test" and did not touch any other release or story. Two new tests in `lib/lint.test.mjs` cover the prose-only case and the shell/CI-executable case; reverting the filter (a one-line mutation) makes exactly the prose-only test fail and no other, confirmed by running it. Full suite: 44/44 pass (`node --test lib/*.test.mjs`, after `npm install` to restore `node_modules`, which is gitignored and not part of the diff).
