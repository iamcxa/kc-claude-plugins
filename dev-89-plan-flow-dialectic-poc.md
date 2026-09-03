---
title: "POC: plan-flow dialectic — borrowed PM skills versus kernel fallback fill the Brief from one raw requirement"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-89
pr:
mod-block:
id: 2jb7cry7ydwy1az84htkfkjp
gates:
    version: 1
    records:
        - id: gate:2jb7cry7ydwy1az84htkfkjp:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:2jb7cry7ydwy1az84htkfkjp-backlog-1
              briefing:
                id: briefing:2jb7cry7ydwy1az84htkfkjp:backlog:attempt-1:revision-1
                digest: sha256:64cce0f39162056794d8a3f01c0d82f4f3306bc332fc30e39159204130e51ade
                room-ref: ./dev-89-plan-flow-dialectic-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:2jb7cry7ydwy1az84htkfkjp:backlog:1
                briefing: briefing:2jb7cry7ydwy1az84htkfkjp:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-03T09:54:40.618597Z"
                decision: approve
                reason: Captain admitted DEV-89 as a standalone POC in sprint S9; POC route build -> prove; 90-minute limit carries its reason.
                conn:
                    quote: 可以，現在開
                    source: Captain chat, this conversation, 2026-09-03, approving the plan-flow dialectic POC with the three ship contract sentences as its raw requirement
              application:
                target-stage: ideation
                state: consumed
---

## The problem

plan-flow has a proven back half (DEV-67: eight lint rules, a plan receipt that ship-flow can dispatch from without reading Linear) and no front half. The Captain's raw input is a journey map, a paragraph, a scenario, or a vague request; nothing turns that into a Development Brief with a one-line user value, a falsifiable goal, and Issues cut so that each Milestone is one recordable journey. The 2026-09-03 survey found the pieces: gstack `office-hours` (MIT) carries the six forcing questions whose Q4 narrowest-wedge is the POC/Pilot/Production decision; pm-skills (CC BY-NC-SA 4.0, so it may be called when installed but never vendored into this public plugin) carries `problem-statement`, `epic-hypothesis`, and `user-story-splitting` whose outputs map one-to-one onto `## The problem`, `## Goal` plus falsifier, and Issue granularity. Whether those outputs actually fill Brief fields without rewriting, and whether the kernel-side fallback questions are enough when the skills are absent, has not been run.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: One disposable run of four dialectic stations on one real requirement, twice (borrowed skills, kernel fallback), proves whether borrowed PM skill outputs fill Development Brief fields without rewriting; no production state, no adopter contract, no plugin.
  poc_decision: Do the borrowed stations fill the Brief verbatim, do the fallback questions alone reach a lint-passing Project, and does station 2 refuse an evidence-free requirement instead of filling the template?
  poc_falsifier: Input B (polished, evidence-free) reaches a Project, profile, or receipt; a borrowed output needs more than one sentence rewritten; the fallback Project fails a lint rule the borrowed one passed; or input A's wedge cannot name one human and one this-week version.
  poc_budget: One cloud worker for the two dialectic runs and the draft dialectic.md, the FO for the Captain Q&A and the two Linear Projects, two FO hours, no dispatch of the resulting Issues
  poc_stop_when: Both receipts exist and are compared, or a falsifier hits
  poc_artifact: retained
  poc_safety_boundary: none
  poc_decision_ready_minutes: 90
  poc_decision_ready_reason: Two full four-station runs plus a Captain Q&A round-trip and two Linear Project writes with lint; each run measured at roughly 30 minutes in the DEV-67 plan side.
```

## Accepted outcome

One real raw requirement, the three ship-flow contract sentences DEV-67 returned to planning (dispatch a higher layer only after the lower layer is fully verified; a worker's without-it command runs in an isolated environment with a temporary HOME, no agent, no network; security, data-loss, and compatibility findings outside the Brief block rather than scope out), travels a four-station dialectic and comes out as one lint-passing Project in Linear with its Issues and a plan receipt. Stations: (1) `problem-statement` output becomes `## The problem`; (2) office-hours Q1 to Q4, asked to the Captain in chat, become the Project's one-line `User value` and the profile choice; (3) `epic-hypothesis` if/then plus validation method become `## Accepted outcome` and the falsifier; (4) `user-story-splitting` patterns become the Issue cut and blockedBy graph. Each station records what it consumed, what it produced, and which Brief field the output filled verbatim versus which needed the FO to rewrite. The DEV-67 lint (`plan-lint.py`, in that entity's evidence) runs on the result. The same four stations run once more with pm-skills deliberately uninstalled, using only the fallback questions the worker writes into a draft `kc-plan-flow/references/dialectic.md`; the two receipts are compared. Two directions recorded: `borrowed` (the installed skills fill the fields) and `fallback` (the kernel questions alone suffice).

A third run carries the refusal falsifier (Codex round 7). Input B is a polished, evidence-free requirement: a full platform pitch with a waitlist and "strong interest", no paying behaviour, no current workaround, no named human, no observation. Station 2 offers four plausible personas through the Ask UI and the Captain selects all four. The only correct outcome is that plan-flow refuses Seam 1: no profile chosen, no Project, no Issues, no receipt; it names the missing demand evidence, the missing specific human, and the missing observation, and produces one discovery assignment the Captain can run this week. If it accepts "all four", picks Pilot, and starts splitting stories, plan-flow is not ready to commission. Station 2 also runs office-hours Phase 3 (premise challenge: do nothing, existing solution, distribution) and Phase 4 (two alternatives) on input A; Q4 decides scope only and profile is left to kc-dev-flow's choose-work-profile.

Falsifier and stop: input B reaches a Project, a profile, or a receipt; a borrowed skill's output cannot be placed into a Brief field without the FO rewriting more than one sentence; the fallback run produces a Project the lint refuses on a rule the borrowed run passed; or input A's Target User & Narrowest Wedge cannot be stated as one specific human and one shippable-this-week version.

## Non-goals

- Do not vendor, copy, or paraphrase pm-skills text into this repository; call it when installed, otherwise use the fallback.
- Do not commission plan-flow, build a plugin, or change kc-dev-flow's kernel.
- Do not dispatch the resulting Issues; the receipt is the deliverable, ship-flow is out of scope here.
- Do not open PRs; the only artifact under the repo is the draft `dialectic.md` and the evidence.

## Acceptance evidence

- **AC-1** The borrowed run's Project passes `plan-lint.py` (all eight rules) and its receipt sha256 is recorded; the per-station table lists consumed input, produced output, and verbatim-fill versus rewritten for each of the four Brief fields.
- **AC-2** The fallback run's Project passes the same lint; its receipt sha256 is recorded; the diff between the two Projects' Issues (count, titles, blockedBy) is recorded.
- **AC-3** Input A: the Captain's answers to office-hours Q1 to Q4 are quoted verbatim; the Target User & Narrowest Wedge paragraph names one human and one this-week version; Phase 3 premises and Phase 4 alternatives are recorded; the resulting `User value:` line is "[persona] obtains [observable outcome]" under 30 words and is distinct from the epic-hypothesis if/then and from the Project headline.
- **AC-3b** Input B: the refusal is recorded verbatim with the three named gaps and the discovery assignment; no Project, profile, Issue, or receipt exists for it in Linear or the state branch.
- **AC-4** `kc-plan-flow/references/dialectic.md` exists on the branch with four stations, each naming the borrowed skill, its output field, and the fallback question; `python3 scripts/kc-dev-flow-contract-test.py` still passes.
- **AC-5** `poc_outcome` records `borrowed`, `fallback`, and `refusal` directions separately with minutes per station and the station reached.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Seat split

The worker (cloud, no Linear) runs stations 1, 3, 4 twice (borrowed, fallback), drafts `kc-plan-flow/references/dialectic.md`, and returns the per-station table and both draft Projects as markdown. The First Officer asks the Captain office-hours Q1 to Q4 in chat (station 2), records the answers verbatim, writes both Projects and their Issues to Linear, runs `plan-lint.py` on each, and records the receipts. The worker never sees `LINEAR_API_KEY`.

## Measurement

Not yet measured.

## Design revisions from Codex round 7 (evidence/codex-plan-round7.md), accepted before the worker runs

- Seam 1 is six fields, not one line: demand evidence, status quo, target human, wedge, premises, go/discover/stop.
- Q4 narrowest wedge decides scope only; profile is chosen through kc-dev-flow's choose-work-profile.
- Station 2 includes office-hours Phase 3 (premise challenge) and Phase 4 (two alternatives); Q5 observation is kept; Q6 future-fit is an optional omission recorded as such.
- Three distinct sentences: Project name is the press-release headline (benefit); `User value:` is "[persona] obtains [observable outcome]"; the epic-hypothesis if/then is the bet. L9 becomes "description is projected from the single User value line", not byte-equality with the hypothesis.
- Station 1 output is marked unverified hypothesis until station 2 evidence exists; `feels` is dropped when no evidence supports it.
- Receipt v1 adds: approval record (receipt hash, approver, time, max_workspaces, concurrency, retry budget) as a separate file; code_repo, base_branch, full Project user value / outcome / exit; canonical Issue body (renamed from description) with hash; canonical JSON with the hash field excluded from its own input. Captain verbatim answers move to a rationale file referenced by hash; receipt carries structured premise ids only.
- Milestone journey definition and journey-step coverage lint are station 4 acceptance conditions for the worker, not decided here.
