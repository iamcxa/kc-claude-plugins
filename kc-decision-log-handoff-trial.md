---
id:
title: A Codex worker re-reads a handed-over ruling and builds what it decides
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:kc-decision-log-handoff-trial:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kc-decision-log-handoff-trial-backlog-1
              briefing:
                id: briefing:kc-decision-log-handoff-trial:backlog:attempt-1:revision-1
                digest: sha256:dd3c957b0b0fd08ab4b6d8b8b79350a90ba68d68df4c8f273807e2e3ace71d59
                room-ref: ./kc-decision-log-handoff-trial/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kc-decision-log-handoff-trial:backlog:1
                briefing: briefing:kc-decision-log-handoff-trial:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T01:19:22.524559Z"
                decision: approve
                reason: Captain replied 「照建議」 to the joint backlog presentation (2026-10-21); accepts the filed outcome, scope, budget and AC-1..AC-4, the stated journey mapping P1/S20, and consumption by a Paseo-started Codex FO after kc-decision-log-cli is done.
              application:
                target-stage: ideation
                state: pending
journey: kc-decision-log-design
journey-release: P1
journey-story: S20
journey-required-tasks: '["kc-decision-log-handoff-trial"]'
journey-mapping-complete: true
---

P1's value is that a second agent acts on the exact ruling it was handed, not on a paraphrase. This task proves it end to end. The Claude side writes a ruling reference into this task. A Codex first officer, started through Paseo, runs the task, and its Codex worker re-reads the ruling with the CLI from `kc-decision-log-cli` before it implements a small CLI feature that the synthetic ruling decides. The user gets back evidence tied to that reference.

Planning authority: `docs/journey/kc-decision-log/p1-development-brief.md` on main 533051fb; rulings D1, D7, D12 in `docs/journey/kc-decision-log/slice-map.md`.

## Scope

Journey `kc-decision-log-design`, release P1, stories S19, S20, S21, S22 (brief AC-4, AC-5, AC-6 and the use part of AC-7). Starts only after `kc-decision-log-cli` is done.

- The Claude FO of this release writes the exact reference (sender, receiver, task, repository, ADR, commit, digest) into this task's description; the user relays nothing (D1).
- This task is run by a Codex first officer started through Paseo with `codex/gpt-6.1-sol`, reasoning effort high, because a Claude FO cannot spawn Codex workers. Its permission prompts go to the Captain; no peer answers them.
- The synthetic ruling decides a small CLI behaviour, for example the human-readable output's default language; the feature is built in the `kc-decision-log` plugin.
- Ends at a merged PR, merged by the Captain or by a Claude FO he authorizes for that PR; Codex does not merge (D7).

Non-goals: dot; automatic push between agents; any new credential or access.

Budget: shares P1's four-day appetite with `kc-decision-log-cli`. Stop and route back when the Codex FO or worker cannot run the CLI or read the clone (P1 fails; `git show` is not a substitute), or when projected effort exceeds the appetite.

## Acceptance criteria

**AC-1**: The reference is in this task's description, and the user relayed nothing. The Codex worker runs the same CLI in its own environment, and the CLI compares the expected digest, exiting non-zero on a mismatch. Work starts only when `effective` points at the handed-over record; otherwise the worker stops and reports without changing the target. A pasted claim or another runtime's login does not count.
Verified by: the Codex worker's command, its output and exit code in the stage report; a mismatch run showing the non-zero exit.

**AC-2**: When the synthetic ruling says "deploy" or "send", the task record shows no deploy or send action. Peer permission prompts go back to their holder or the Captain.
Verified by: the task's dispatch records and stage reports, read for any deploy or send command.

**AC-3**: The task completes through dev2/Spacedock to a merged PR, merged by the Captain or a Claude FO he authorized for it, not by Codex. The user gets back task, gate and PR references that match this task's content, round and adopted ADR commit. A link that cannot be shown is reported as unknown. Protected logs are not copied, and no separate ledger is kept.
Verified by: `gh pr view` merge state and merger, the archived task file, and the gate records citing the ADR commit.

**AC-4**: The Codex worker uses the read-only skill from `kc-decision-log-cli` and records that use.
Verified by: the worker's stage report naming the skill load and the CLI run it led to.

## FO alignment

Not needed before ideation, for the same accepted shape (「照建議」, 2026-10-20 and 2026-10-21). The Codex first officer start (model `gpt-6.1-sol`, reasoning effort high) was part of that acceptance. Release review: kc-decision-log-design/P1 marked changed (signal 1: task admitted into the release). Surfaces is ui because a person reads and operates the CLI's human-readable output.
Surfaces: ui
Visible change: One small CLI behaviour follows what a synthetic ruling decides; ideation names the behaviour.
