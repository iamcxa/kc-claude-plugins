---
id: d3xb3q0qwmjpkty23njq6t66
title: Make evidence mean executable code, so the exists count stops lying
status: ideation
source: captain
product: kc-team-ops
planning-window:
planning-outcome:
sprint: journey-map-poc
sprint-readiness: ready
started:
completed:
verdict:
worktree:
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
