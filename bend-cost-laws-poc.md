---
title: Prove executable Bend cost laws across the consumer boundary
status: implementation
variant: kc-dev-flow-2
profile: poc
merge:
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:bend-cost-laws-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:bend-cost-laws-poc-backlog-1
              briefing:
                id: briefing:bend-cost-laws-poc:backlog:attempt-1:revision-1
                digest: sha256:04e4ca3b19d9f838692a506fb7b4d11411cd3d8f5f9f4168284789711426cea7
                room-ref: ./bend-cost-laws-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:bend-cost-laws-poc:backlog:1
                briefing: briefing:bend-cost-laws-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-22T01:52:10.972891257Z"
                decision: approve
                reason: Kent answered 60 分鐘（建議） after already accepting dev2 POC and the three-law experiment; this accepts the recorded fixed budget and bounded implementation plus independent validation.
              application:
                target-stage: implementation
                state: consumed
---

Decide whether later PR-flow development should adopt a law-checked executable cost-decision component rather than relying only on schema-shaped summaries.

## Scope

Build a disposable integrated path from recorded or synthetic provider terminal JSON through explicit normalization into actual Bend-checked pure cost logic, then into a caller that consumes the resulting decision. Use public Bend source pinned at `a49524265bdfa5753a4bf38e25f0574a705dd868` in an isolated task-owned directory. No retained plugin change, provider/model/JEV call, credentials, product commit/push/PR/merge or invoice-cap claim.

The fixed experiment ceiling is 3,600 seconds. Prior Cloud routing preflight ran from `2026-09-22T01:22:42.726Z` to `2026-09-22T01:31:18.742Z` and consumes 516.016 seconds. User wait is excluded. Work resumed at `2026-09-22T01:45:13Z` with 3,083.984 seconds remaining. The immutable stop deadline is `2026-09-22T02:36:36.984Z`; commission, acquisition, build, implementation and independent validation all count. Stop and clean up owned processes at the deadline.

Input identity, numeric precision, normalization, foreign/IO/compiler and unsafe-dependency assumptions must remain explicit. A Bend-only abstract model disconnected from the caller is insufficient. Preserve failed attempts. Do not switch versions or weaken a law to pass.

## Acceptance criteria

**AC-1**: A uniquely identified valid reported spend remains known and contributes to the decision even when the review result failed.
Verified by: an integrated recorded/synthetic failed-terminal case at the actual caller boundary, plus a retained-cost mutation that the Bend check or caller assertion rejects.

**AC-2**: One receipt identity contributes at most once.
Verified by: duplicate-identity input across the same consumer path, plus a dedup mutation that the Bend check or caller assertion rejects.

**AC-3**: Unknown, ambiguous or invalid cost never becomes a claim of known zero or complete spend.
Verified by: unknown/ambiguous/invalid inputs across the same consumer path, plus an unknown-handling mutation that the Bend check or caller assertion rejects.

**AC-4**: Exit zero from an unsafe/foreign-dependent proof is not accepted as sufficient evidence.
Verified by: a deliberate unsafe or foreign dependency control whose exit status alone cannot satisfy the acceptance gate, with the remaining trust boundary recorded.

**AC-5**: The POC is bounded, reproducible and disposable.
Verified by: exact source/toolchain/artifact hashes, elapsed breakdown, independent fresh-validator verdict, no owned process remaining, and an explicit statement of what is unproved.
