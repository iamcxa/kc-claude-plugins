---
title: "POC: plan-flow dialectic — borrowed PM skills versus kernel fallback fill the Brief from one raw requirement"
status: done
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started: 2026-09-03T09:50:00Z
completed: 2026-09-03T14:03:41Z
verdict: PASSED
worktree:
issue: DEV-89
pr: local-merge:a5937eb
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
        - id: gate:2jb7cry7ydwy1az84htkfkjp:validation
          stage: validation
          attempts:
            - id: gate-attempt:2jb7cry7ydwy1az84htkfkjp-validation-1
              briefing:
                id: briefing:2jb7cry7ydwy1az84htkfkjp:validation:attempt-1:revision-1
                digest: sha256:aae3bf241eae93c953e7b16e332eaa9131093e447ce3868cff5167452f19fb4f
                room-ref: ./dev-89-plan-flow-dialectic-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:2jb7cry7ydwy1az84htkfkjp:validation:1
                briefing: briefing:2jb7cry7ydwy1az84htkfkjp:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-03T13:49:21.888557Z"
                decision: approve
                reason: 'Captain accepted the DEV-89 POC outcome as change: refusal falsifier proceed, borrowed and fallback need rework, nine changes returned to plan-flow POC 3; the run-A Project stays in Linear as planned work.'
                conn:
                    quote: 89我們應該會再走好幾輪才會完成對嗎？如果是就 Ｂ
                    source: Captain chat, this conversation, 2026-09-03 evening, choosing (b) and accepting that DEV-89 closes as change with further rounds
              application:
                target-stage: done
                state: consumed
archived: 2026-09-03T14:03:41Z
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

Dispatch 09:55Z, token acked 21 s; blocked on the shared cloud quota from the first turn until 13:00Z; on resend the worker paused on three consent questions (S19), answered with the dispatch token; worker time for all three runs plus dialectic.md about 3 min of wall-clock writes (its own MINUTES line), evidence delivered at ~13:24Z but truncated at 10 K (S21), run files committed at a5937ebf on request. FO time: station 0 pain inventory, station 2 Q&A with the Captain, schema B, Codex rounds 7 and 8, about 3 h across the quota gap. Both Linear Projects and their lint receipts are not yet written (pending the Captain's ruling on the round-8 P0).

## Stage Report: implementation

- DONE (worker, a5937ebf): run A (borrowed skills, input A), run B (fallback, input A), run C (refusal, input B), compare.md, draft `kc-plan-flow/references/dialectic.md`.
- DONE (FO): station 0 pain inventory (20 pains); station 2 Q1-Q4 with the Captain plus Phase 3 premises and Phase 4 alternatives; receipt v1 and approval v1 schemas with a validator seen to fail six ways; commission skeleton.
- Run C: input B refused with the three named gaps, no profile, no Project, no Issues, no receipt; discovery assignment produced. Codex round 8 rates the refusal sound and the assignment half-formed (interview cannot yield an observation; willingness-to-pay is still stated intent).
- Run A vs B: identical three-Issue cut and blockedBy graph; borrowed skills cost 2-3 rewritten sentences per field, fallback 0. Codex: the zero is definitional (fallback was written to the Brief shape) and the comparison is not independent (one worker, station 2 reused); direction should be fallback-with-borrowed-as-checklist.
- Codex round 8 P0, accepted as a real finding: the Captain chose Alternative A (README sentences plus pins, no enforcement) while the produced `User value:` line says "because ship-flow enforces"; the accepted outcome measures Kent no longer asking, which a document can produce without any runtime guarantee. plan-flow accepted an approach that cannot causally reach its stated value. This is the front-half blocker: a premise falsifier that removes the chosen approach and asks whether the outcome can still hold.
- Codex round 8 licence finding: dialectic.md station 3 questions mirror epic-hypothesis's if/then, tiny acts, validation measures; station 4 question 1 mirrors the splitting patterns (step, rule, data type). Rewording does not remove CC BY-NC-SA derivation. Stations 1 and 2 are sound (office-hours, MIT).
- Codex round 8 ordering finding: the refusal seam sits after station 1 already produced persona, because, feels; the correct order is observe, WHY evidence and refusal check, then the problem statement.

## Design revisions from Codex round 7 (evidence/codex-plan-round7.md), accepted before the worker runs

- Seam 1 is six fields, not one line: demand evidence, status quo, target human, wedge, premises, go/discover/stop.
- Q4 narrowest wedge decides scope only; profile is chosen through kc-dev-flow's choose-work-profile.
- Station 2 includes office-hours Phase 3 (premise challenge) and Phase 4 (two alternatives); Q5 observation is kept; Q6 future-fit is an optional omission recorded as such.
- Three distinct sentences: Project name is the press-release headline (benefit); `User value:` is "[persona] obtains [observable outcome]"; the epic-hypothesis if/then is the bet. L9 becomes "description is projected from the single User value line", not byte-equality with the hypothesis.
- Station 1 output is marked unverified hypothesis until station 2 evidence exists; `feels` is dropped when no evidence supports it.
- Receipt v1 adds: approval record (receipt hash, approver, time, max_workspaces, concurrency, retry budget) as a separate file; code_repo, base_branch, full Project user value / outcome / exit; canonical Issue body (renamed from description) with hash; canonical JSON with the hash field excluded from its own input. Captain verbatim answers move to a rationale file referenced by hash; receipt carries structured premise ids only.
- Milestone journey definition and journey-step coverage lint are station 4 acceptance conditions for the worker, not decided here.

## POC outcome

```yaml
poc_outcome:
  direction: change
  admitted_at: 2026-09-03T09:50:00Z
  decision_ready_at: 2026-09-03T14:05:00Z
  decision_ready_elapsed_seconds: 15300
  captain_interventions_before_decision_ready: 0
  borrowed_direction: change
  fallback_direction: change
  refusal_direction: proceed
  evidence: >-
    Refusal (run C): the evidence-free input B was refused at Seam 1 with the three
    named gaps and no profile, Project, Issue, or receipt; Codex round 8 rates the
    refusal sound. Borrowed (run A): the three pm-skills fill their fields but cost
    2-3 rewritten sentences each because their templates target a different
    artifact; the Issue cut and blockedBy transfer verbatim. Fallback (run B): zero
    rewrites, identical cut, but the zero is definitional and the comparison was not
    independent. The FO wrote run A's Project and three Issues to Linear with the
    Captain-corrected user value (decision b); plan-lint passes all eight rules
    (evidence/lint-runA.txt) after two FO corrections (cycle unset, relation
    direction inverted); receipt v1 (evidence/receipt-runA.json) validates against
    the schema with order DEV-90, DEV-91, DEV-92.
  strongest_limit: >-
    plan-flow accepted an approach that could not causally reach its stated value
    (README-only approach, "enforces" value) until Codex round 8 caught it; the
    Captain resolved it by narrowing the value (b). Relation direction: DEV-67's
    fixture and this run's first write both created Linear relations inverted, and
    the lint, consistent with the same wrong belief, passed; DEV-67's dispatch
    order was therefore reversed (66, 65, 64 instead of 64, 65, 66) and nobody
    noticed because each layer still verified (S22). dialectic.md stations 3 and 4
    derive from CC BY-NC-SA templates by rewording; the refusal seam sits after
    station 1 rather than before it; the discovery assignment asks rather than
    observes. The 90-minute limit was exceeded by the shared cloud quota gap and the
    truncated Evidence block (S21), not by station time (worker: ~3 min).
  reversal_fact: >-
    A repeat where the refusal run accepts input B, or where a borrowed-skill
    output lands verbatim in its field, or where the fallback Project fails a lint
    rule the borrowed one passed.
  cleanup_status_at_decision: complete
```

## POC close measurement

```yaml
poc_close_measurement:
  captain_wait_seconds: 0
  terminal_cleanup_seconds: 60
  cleanup_status: complete
```

## Change returned to planning (plan-flow POC 3 scope)

1. Premise falsifier before Issue cutting: remove the chosen approach and ask whether the accepted outcome can still hold; refuse when the approach builds no mechanism the value names (Codex r8 P0).
2. Three distinct Project sentences (headline, user value as "[persona] obtains [observable outcome]", hypothesis if/then); the Linear description is projected from the user value; no "enforces" unless a runtime mechanism exists.
3. Order: observe -> WHY evidence and refusal check -> frame -> hypothesize -> cut. No persona or "feels" is written before the refusal check passes.
4. Fallback questions are the only artifact-producing path; installed borrowed skills act as a checklist. Rewrite dialectic.md stations 3 and 4 from this repository's own needs; do not carry CC BY-NC-SA template structure under other words.
5. A discovery assignment names an observation or a payment to obtain this week, never another interview.
6. Relation direction: `issueRelationCreate(issueId=X, relatedIssueId=Y, type=blocks)` means X blocks Y; the plan-lint L6 falsifier is a hand-made relation in the Linear UI whose edge must read (X, Y). DEV-67's reversed dispatch order is recorded as S22.
7. Receipt v1 and approval v1 schemas (evidence/schema/) are the seam contract; the rationale file carries station tables and Captain verbatim answers by hash only.
8. market-signal station ("market-seeker"): evidence supplier into Seam 1's demand-evidence field, threshold by `audience` (self/team/market), never a gate; its own falsifier is one known-dead and one known-alive idea told apart by web search alone.
9. Worker Evidence blocks are capped at ~10 K by the harness; run artifacts go on the branch, the block carries paths and hashes (S21). A worker may stop on consent questions when the task arrives by carrier; the go message pre-answers them (S19).

## Cleanup

Worker workspace 43c707f1 and its session archived; carrier branch deleted; candidate branch feature/dev-89-… retained at a5937ebf (dialectic.md draft plus run files) for the Captain's decision on the POC artifact; Linear Project "The three ship-flow guarantees are written down and pinned" with DEV-90/91/92 retained as real planned work (Cycle 1). No run-B Project was written: the Captain's (b) ruling made run A's corrected Project the single canonical output, and run B's cut is identical.
