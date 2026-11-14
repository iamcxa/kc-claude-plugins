---
id:
title: Three or fewer tried ways to run the next real task on the extracted package with private state, each with what it costs the Captain
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:extracted-package-real-use-routes-probe-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:extracted-package-real-use-routes-probe-poc-backlog-1
              briefing:
                id: briefing:extracted-package-real-use-routes-probe-poc:backlog:attempt-1:revision-1
                digest: sha256:1f5a3a54febbff33d51a1a54505fee39d1a478bcaea3c95a0067c72569d2ed82
                room-ref: ./extracted-package-real-use-routes-probe-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:extracted-package-real-use-routes-probe-poc:backlog:1
                briefing: briefing:extracted-package-real-use-routes-probe-poc:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T12:16:04.05381Z"
                decision: approve
                reason: Inside scope 3 given by the reform session under the Captain's grant; no public merge, outward action, outcome-definition change or suspected key is involved in admission.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 3 from the reform session, Paseo message 6dd41248-d90d-4c35-ba36-bc70f9e033d7
              application:
                target-stage: implementation
                state: consumed
---

Nine of the sixteen approved outcomes can only be measured in real use, and nobody uses the extracted package yet. The next real task of the reform should be run by a First Officer and workers that load the extracted package, not the installed one, with its task state in a private place from the first commit.

## Scope

- Source: the reform session's scope 3 under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, message 6dd41248, 2026-11-14); it reports that the Captain approved the order with "Go ahead with the plan." in its own conversation (relayed, not a ruling here). Admission is recorded by FO under the grant.
- Outcome: a probe that answers by trying the smallest step of each route, not by reasoning: where the workflow and its state live (the private working repository is the obvious home; its state branch would be private); how a session loads the extracted package without colliding with the installed package of the same skill names (a temporary plugin name is allowed; the public name is not decided); whether that is cleaner on the laptop or on the clean host, where nothing else is installed but the repository key is read-only and the sign-in can only make model requests; what each route needs from the Captain (a plugin install on his laptop, a write credential on the host, a second host in his daily view). Output: at most three options, each with what was actually tried, what it costs him, and what breaks.
- The probe leaves no lasting change: anything it installs, registers or creates to try a step is removed again and listed, or kept only inside a scratch location it names.
- consumer: the reform session and the Captain choosing a route; bite: no extracted-package task has ever been run.
Non-goals: building the chosen option; migrating the two products; any change to the installed package; retiring the public state branch; hook work; anything on the open pull requests or the release.
Budget: 1 implementation and 1 validation cycles
Stop condition: one hour from dispatch, then stop and bring the options; at half of that, one check whether the probe still serves the stated goal; a step that would need a credential, a plugin install on the Captain's laptop outside a scratch location, or a write to a shared configuration: do not take it, list it as what that route needs from him.

## Acceptance criteria

**AC-1**: The report gives at most three options, and for each: the smallest step actually tried with its command and observed result, what it needs from the Captain, and what breaks.
Verified by: the validator re-runs one tried step per option where it leaves no lasting change, and reads the rest against the recorded outputs. Limit: a probe, not a working setup.

**AC-2**: Nothing the probe did is left behind outside its named scratch locations.
Verified by: the report's list of what was created and removed, checked by the validator on the laptop and, by listing only, on the clean host.

## FO alignment

Alignment: not needed before implementation: the questions and the stop are stated in the scope; the options go to the reform session and the Captain, who choose.
Release review: not needed: a probe.
