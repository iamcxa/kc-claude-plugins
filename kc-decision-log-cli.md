---
id:
title: Agents read a ruling at an exact commit with the kc-decision-log CLI
status: ideation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:kc-decision-log-cli:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kc-decision-log-cli-backlog-1
              briefing:
                id: briefing:kc-decision-log-cli:backlog:attempt-1:revision-1
                digest: sha256:58faf03afa587f2be459207b3981906de76b4934138e74a381e6ebaaa70e7dd8
                room-ref: ./kc-decision-log-cli/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kc-decision-log-cli:backlog:1
                briefing: briefing:kc-decision-log-cli:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T01:19:19.23991Z"
                decision: approve
                reason: Captain replied 「照建議」 to the joint backlog presentation of kc-decision-log-cli and kc-decision-log-handoff-trial (2026-10-21); accepts the filed outcome, scope, budget and AC-1..AC-4, and the stated journey mapping P1/S10.
              application:
                target-stage: ideation
                state: consumed
journey: kc-decision-log-design
journey-release: P1
journey-story: S10
journey-required-tasks: '["kc-decision-log-cli"]'
journey-mapping-complete: true
---

The user directs several AI agents and wants one versioned source of his rulings that each agent reads at the same version (「我需要指揮不同 FO，跨產品，跨 LLM，跨工具去達成我的目標」, 2026-10-19). Today no agent has a tool to read a ruling at an exact commit. This task builds that tool and the read-only skill that tells agents to use it; task `kc-decision-log-handoff-trial` then proves a Claude→Codex handoff with it.

Planning authority: `docs/journey/kc-decision-log/p1-development-brief.md` on main 533051fb (sha256 5c2edd0a…; `journey-handoff.mjs --out` passed, assessment digest 5a7ee350…). Rulings D1–D13: `docs/journey/kc-decision-log/slice-map.md` § 已確認選擇. The Captain accepted the handoff on 2026-10-20 (「照建議」) and on 2026-10-21 made this session the release's FO (「照建議」).

## Scope

Journey `kc-decision-log-design`, release P1, stories S01, S10, S11 (brief AC-1, AC-2, AC-3 and the skill part of AC-7).

- A new `kc-decision-log` plugin in this repository: Claude and Codex manifests, a marketplace entry from 0.1.0 marked experimental (`scripts/version-parity-check.sh` requires it), release-please wiring, local install test before release-please (D8).
- The query core copied and rewritten from the prototype in the user's private decision repository (`parse`, `makeSnapshot`, `effective`, `createService`); the prototype stays unchanged. No private ADR content enters this public repository.
- One configured binding, a full commit required, no fetch; JSON and human output; exit codes; an expected-digest comparison option.
- Effective rule kept from the prototype for P1 (D9). `adr_lint.py` is the format oracle in tests (D11).
- A short read-only skill (D10).

Non-goals: CLI writes, numbering, task creation, PR or merge (D3); dot or MCP; more than one decision space; tenant isolation; hooks (S30); reading engineering repositories' dev2 ADRs.

Budget: P1 appetite is four full working days across both tasks; estimate 16–30 active hours, uncalibrated (`p1-estimate.md`). Stop and route back when projected effort exceeds the appetite, or a fix needs a new credential, access grant or host change.

## Acceptance criteria

**AC-1**: With a synthetic decision repository as the only configured binding, the CLI refuses an unconfigured binding, a wrong repository or path, a missing commit or a non-full commit, and exits non-zero; messages may name the reason. It treats neither caller claims nor arbitrary paths as authorization and adds no access.
Verified by: CLI runs against committed synthetic fixtures, each refusal case with its exit code.

**AC-2**: Reading at D0, the CLI claims only D0 after the tracked ref moves to D1. It returns repository, path, ADR ID, full commit, a digest of the raw bytes and the original Status, the same in JSON and human-readable modes.
Verified by: a synthetic repository with D0 and D1 commits; outputs compared, and the digest checked against `git cat-file blob` bytes.

**AC-3**: On synthetic data, the CLI reports Status exactly as written: an Accepted record with a Decision key, Proposed, an explicit same-binding supersession, a missing key, two Accepted records under one key, and a broken chain. `effective` follows D9: a missing key or several Accepted records under one key give `unresolved`. Source text is never edited, and `unresolved` is reported separately from tool failure.
Verified by: committed fixtures with expected results written independently of the parser; `adr_lint.py` run on the fixtures.

**AC-4**: The read-only skill tells an agent holding a ruling reference to re-read it with the CLI, compare the digest, and stop on a mismatch. It loads on Claude and Codex.
Verified by: the skill file and manifest entries, plus a local install that lists the skill on both hosts. Use by a Codex worker is verified in `kc-decision-log-handoff-trial`.

## FO alignment

Not needed before ideation. The Captain accepted the outcome, scope, two-task split, budget and this session as FO (「照建議」, 2026-10-20 and 2026-10-21); the committed brief is the planning authority. Release review: kc-decision-log-design/P1 marked changed (signal 1: task admitted into the release). Surfaces is ui because a person reads and operates the CLI's human-readable output.
Surfaces: ui
Visible change: Agents can run a `kc-decision-log` CLI and load a read-only skill to read one ruling at an exact commit.
