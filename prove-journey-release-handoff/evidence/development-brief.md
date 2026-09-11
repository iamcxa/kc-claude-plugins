# Development Brief: Prepare one selected release for development

This is a disposable admission snapshot of accepted intent, for technical shaping only. No delivery profile has been selected and no execution or task admission is authorized.

## The problem

The journey tool can express release slices and show development observations, but does not yet turn an existing board into focused value questions and a development-ready handoff. Repeating plan-value's questionnaire ignores prior decisions; treating every unverified story as missing implementation invents work. Running plan-detail and dev-flow ideation separately repeats technical planning.

## Accepted outcome

A planner selects one release slice, receives only the unresolved questions that affect its user value, and obtains one reviewed Development Brief that dev-flow can consume. Journey-map owns value planning; dev-flow owns technical shaping, implementation and verification. One release delivery scope serves one explicit journey value. The board remains a view of planning intent and recorded development facts, not an acceptance authority.

Kent confirmed the two-entry architecture, proactive board awareness, facts-before-choices questioning and this scope-preparation step in the current conversation. This seed captures that approved direction; profile selection and formal admission remain pending.

## Non-goals

- Do not add a planning Spacedock workflow, another tracker, progress cache, polling daemon or background board monitor.
- Do not reinterpret task completion as verified journey usability, change the three-color calculator, or give the renderer E2E classification rules.
- Do not mechanically turn every story or non-green card into a task, reopen settled choices without changed premises, or require evidence for pure intent mapping.
- Do not import PR392 wholesale, retire its commands, or require migration of existing journey files and consumers.
- Do not perform the separate repository-wide sprint-to-release migration or provider retirement. This route uses existing local standalone admission without requiring Linear.
- Do not build a generic task projector, auto-admission path, new approval system, standing review harness or CI lane.
- Do not extend the predecessor three-PR stack; re-read its delivery/base state before starting this independent change.

## Acceptance criteria

- **AC-1** Given an existing board with an agreed persona, journey, release goal and prior decisions, the agent reuses those answers and asks only a missing value/scope/acceptance decision, one at a time, with a recommendation and its effect. It does not run a fixed six-question interview again.
- **AC-2** On an explicit planning/resume or selected-release preparation request, the agent examines relevant unverified/gap stories and unresolved questions in any status. It distinguishes authored evidence uncertainty from unavailable or incomplete SD observation, investigates accessible facts first, preserves unknowns, and does not invent development work from missing evidence. Already assigned or deliberately deferred work does not trigger the same question again unless its premise changes.
- **AC-3** User decisions retain stable story/release identity and reuse existing journey content and supported safe canvas readback. Ambiguous canvas edits are surfaced rather than silently applied. Later-release uncertainty does not block an independent current release; unresolved decisions that change the current accepted outcome, scope or acceptance cannot be silently treated as approved.
- **AC-4** The selected release produces one Development Brief using the existing admission sections: problem, accepted outcome, non-goals, acceptance criteria and route-back conditions. It cites the journey source revision and release/story identities, separates observations from assumptions and names unresolved technical questions. The brief is an admission snapshot, not another live planning database; a later planning change does not rewrite running tasks automatically.
- **AC-5** The existing dev-flow ideation consumes that brief and prior factual evidence, performs plan-detail's technical gap/dependency/without-it work once, and proposes only necessary tasks with traceable release/story origins. Shared or integration work is not duplicated or forced into a false one-story mapping for progress counts. Existing profile/admission/implementation authority still applies; no task execution or gate approval follows merely from drawing a card.
- **AC-6** Existing map-only use remains independently usable without SD or code evidence, and standalone dev-flow accepts a valid brief without requiring a board. Questioning uses the host's available interaction surface with a clear text fallback. The focused evidence demonstrates known-answer reuse, gap-versus-unknown handling and an actual brief-to-ideation handoff; no new standing test framework is introduced.

## Route-back conditions

Stop and return the changed premise, affected acceptance evidence and recommended change or stop if the accepted outcome or non-goals change. Also return for an unavoidable consumer migration, a new authoritative planning store, automatic status/task writes, or a technical fact that changes the selected release value. Current task mapping cannot be assumed to support shared/integration tasks; shaping must state the bounded handling without broadening the progress feature silently.

## Source and identity

Accepted source: `accepted-source.md`, revision and SHA-256 in `source-revision.json`. The disposable board `journey.yaml` is an agent-authored projection of that accepted prose, not a separately approved change. Selected release `prepare-release` means one selected-release planning-to-development handoff. Story identifiers below are proposed stable handles derived directly from the accepted criteria; they do not claim prior user naming.

| Story identity | Source |
|---|---|
| reuse-decisions | AC-1 |
| investigate-uncertainty | AC-2 |
| preserve-identities | AC-3 |
| produce-development-brief | AC-4 |
| shape-necessary-work | AC-5 |
| preserve-independent-entry | AC-6 |

## Current factual observations and technical unknowns

The inspected local tool already exposes `buildJourneyBoard`, `buildReleaseContract`, and `loadJourney`. `map-from-conversation.md` already forbids restarting settled questions and asks one question at a time, but its four passes do not define selected-release preparation or the Development Brief handoff. This is a bounded reference inspection, not proof that equivalent behavior is absent everywhere.

`read.mjs` exposes identity-based `diffAgainstModel` and `applyDiff`; ambiguity and cross-projection wording conflicts are surfaced. Status/evidence/question round-trip and actual host selection-to-render usability have not been exercised in this experiment. Missing observation is unknown evidence, not an implementation-gap finding. No fix task is authorized by that absence.

The existing standalone Development Brief admission shape is problem, accepted outcome, non-goals, acceptance criteria, route-back conditions. The current stage loader has `validate_admission_brief(path, profile)`; format validation can be invoked without selecting a profile receipt. Current runtime maps Spacedock ideation to selected shape for retained delivery work, while POC skips ideation. Future retained delivery profile/admission remains Captain-owned.

Technical questions for shaping: where the single handoff description belongs; how the existing development intake consumes it once; what bounded representation preserves shared integration origins when current progress mapping cannot be assumed to support multiple story IDs. No new tracker or schema migration is accepted.

Local factual source copies in `facts/`: map-from-conversation.md, read.mjs, render.mjs, release-contract.mjs, and admission-format.txt. These are read-only snapshots for this experiment, not retained product files. File hashes are in `facts-digests.json`.
