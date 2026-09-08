---
session-date: 2026-09-08
sequence: 1
first-commit: 5b1ad194
last-commit: 0a6c639c
duration: ~21h
---

# Session Debrief — 2026-09-08 #1

One plan session (2026-09-07b-qnow) and one ship batch (ab2fb2635f0c): the staging-qualification work landed on qnow main through three PRs plus one fix PR, then DEV-37's hosted acceptance ran five times in a Conductor cloud workspace and was stopped by the Captain with identity unproven. The batch closed CLOSE OK 74e380e1.

## Shipped
- **DEV-114** `merge-station` — [#391](https://github.com/iamcxa/kc-claude-plugins/pull/391). Merge station verifies base and accepted head, readies all, waits clean, merges in order, stops on the first refusal.
- **DEV-136** `hosted-support-files` — [#1181](https://github.com/iamcxa/qnow/pull/1181). Supporting files for the hosted runner on qnow main (native migrations 0000–0008, identity, api, local, tests); three repair rounds.
- **DEV-137** `hosted-on-main` — [#1182](https://github.com/iamcxa/qnow/pull/1182). `hosted/` byte-identical to the qualification branch except migration-count literals; lockfile restored to the branch's; four repair rounds; migration 0009.
- **DEV-36** `esm-full-runner` — [#1174](https://github.com/iamcxa/qnow/pull/1174). Rebased onto main; four DEV-35 commits dropped as superseded by #1180.
- **DEV-143** `rollback-admission` — [#1183](https://github.com/iamcxa/qnow/pull/1183). Rollback deploy admitted by its own migration count; baseline admission ids surfaced as failureReason.
- **DEV-37** — captain_stopped after five cloud attempts and one deploy (candidate 6a9efddb on main bf1b4ba1, published on staging, migrations 0008/0009 applied); identity census failed with an unrecorded cause. Receipts on `evidence/dev-37-acceptance-receipt`.

## Filed (backlog)
- **DEV-138** — re-decide the Netlify toolchain pins after hosted/ landed.
- **DEV-139** — qnow-next's npm test never runs in CI; wire it as a required path-filtered job.
- **DEV-140** — production: scope qnow_app's read of staff assignments (PoC re-granted table-wide SELECT).
- **DEV-141** — experiments/netlify-refine-poc lifecycle: what graduates, what is deleted (overlaps DEV-23).
- **DEV-142** — Conductor cloud workspace does not run conductor-cloud-setup.sh (no Xvfb, dirty tree).
- **DEV-143** — shipped same session.
- **DEV-144** — read-only-online-build test fails only in the Linux cloud workspace.
- **DEV-145** — surface every run-path admission id; re-decide the rollback pin now that staging carries 10 migrations.
- **DEV-146** — POC: Clerk auth for QNow hosted (phone OTP, backend admin from a Netlify Function); blocks DEV-132.
- **DEV-147** — ship-flow: close-receipt schema forbids the debrief writers' output; validator skips schema when jsonschema is absent.

## Non-PR commits (workflow-only)
State transitions and scaffolding that don't belong to a PR:

- `1826d151`, `0e0f3055`, `d5447537`, `b0eb60de`, `7742c318`, `eb3c54b5` plan-flow session 2026-09-07b-qnow — stations 0–4, lint PASS, receipt re-hashed, approval signed, batch ab2fb263 opened.
- `6f3e2acf`, `c8e5acca`, `64f971ca`, `4ce95479`, `b1fcd027`, `9e4b34c2` ship-flow batch ab2fb263 — DEV-136/137 Briefs; DEV-114 accepted through three rounds; #391 merged; DEV-136 dispatched.
- `0a6c639c` close: batch ab2fb2635f0c — CLOSE OK 74e380e1553c51f0.

53 `state:` commits suppressed. All other session commits are rolled up in the shipped PRs above.

## Decisions
- PoC standard for the staff-assignments grant: option A, migration 0009 re-grants SELECT; production scoped read filed as DEV-140.
- DEV-37 stopped at attempt 5 ("DEV-37 就在這裡停"); the milestone closes with identity unproven.
- Evaluate Clerk auth instead of Netlify Auth plus a self-built OTP (DEV-146, blocks DEV-132).
- DEV-139 (CI for qnow-next) after the PoC; the FO's local full runs were the gate for #1181–#1183.
- Identity probe authorized (three temporary env keys, one census call, deleted); inconclusive because function env is baked at deploy.

## Issues — Workflow
- The FO reported CI as the aggregate gate for two PRs; CI never runs qnow-next's tests (DEV-139).
- The FO's dispatch omitted rules written in the target repo's AGENTS.md three times (DEV-37 attempts 1–3); the package's local-fake rehearsal was used only before attempt 5.
- The DEV-136 worker regenerated package-lock.json instead of carrying the branch's; only a hosted contract constant caught the drift (fixed in DEV-137).
- The blanket 8→10 migration-count ruling in DEV-137 broke the rollback baseline (fixed in DEV-143); a deploy that applies migrations makes the old rollback unrestorable on Netlify (DEV-145).
- Two run receipts reported `failureReason: null` (DEV-143 fixed the pre-deploy ids; DEV-145 covers the rest).
- The close receipt embedding the debrief writers' output was refused once jsonschema was installed (DEV-147).
- The identity-probe cloud session printed its own random secret in its report (key deleted; no reuse).

## Issues — Spacedock
None identified. The cloud-setup gap belongs to Conductor (DEV-142) and is not filed to spacedock per the standing rule.

## Observations
_(none recorded)_

## Agent Testimonial
- Date: 2026-09-08
- Harness/runtime: Claude Code
- Model: Claude Fable 5.1
- Model version/build: claude-fable-5-1
- Session scale: 6 tasks touched; 13 workers dispatched (5 local, 8 cloud sessions); 5 PRs touched/merged

Spacedock's split-root state branch and the ship-flow stations made every ruling and every failed attempt durable, which is what let a five-attempt cloud run be audited afterwards and closed with a receipt. The cost was ceremony around a close receipt whose pinned schema and writers disagree, and a status binary that needs the workflow README on the current branch (it was only on main). The stations did not stop my own dispatch errors; only the target repo's rules and its rehearsal seam did, and I reached for them late.

## What's Next
- Recommended next session (plan): DEV-146 Clerk POC and the DEV-132 decision; the Unplanned formal-architecture tickets DEV-17…23; merge DEV-141 into DEV-23.
- Before any further hosted run: DEV-145 (run-path ids, rollback pin) and DEV-142 (cloud setup).
- Ship-flow fixes: DEV-134, DEV-135, DEV-147; DEV-139 for qnow-next CI after the PoC.
- Conductor cloud workspace 783dccd3 still holds the five attempt logs; archive when no longer needed.
