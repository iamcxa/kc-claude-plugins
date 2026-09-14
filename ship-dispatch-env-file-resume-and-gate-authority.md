---
title: "dispatch.sh carries worker credentials through workspace create --env, resumes a task in a fresh workspace, and states that gate decisions are the ship FO's"
status: validation
source: "Captain 2026-09-14 「派」 (ship round 3, harden); findings recorded on spacedock-state/ship questions logs"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: ready
started: 2026-09-14T10:50:16Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-ship-dispatch-env-file-resume-and-gate-authority
issue:
pr:
mod-block:
id: 0dg522wbqd0jpd2jeg8tjq4m
gates:
    version: 1
    records:
        - id: gate:0dg522wbqd0jpd2jeg8tjq4m:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:0dg522wbqd0jpd2jeg8tjq4m-backlog-1
              briefing:
                id: briefing:0dg522wbqd0jpd2jeg8tjq4m:backlog:attempt-1:revision-1
                digest: sha256:123bc52ade833c094732c26402df63137aa3a2d58d2bfcfa9c6bfa68a4cbc9a7
                room-ref: ./ship-dispatch-env-file-resume-and-gate-authority/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:0dg522wbqd0jpd2jeg8tjq4m:backlog:1
                briefing: briefing:0dg522wbqd0jpd2jeg8tjq4m:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T10:49:39.747782925Z"
                decision: approve
                reason: 'Backlog admission criteria met: title/product/source/sprint/sprint-readiness=ready present, 5-item Accepted outcome is the required brief, profile=pilot recommended and consistent with kernel admission (harden round on an already-shipped tool).'
                conn:
                    quote: 准
                    source: Captain 2026-09-14 batch approval, r3 batch of five tasks under the pilot profile
              application:
                target-stage: ideation
                state: consumed
---

On 2026-09-14 (qnow `qnow-clerk-poc`, DEV-146) the Captain provisioned Clerk keys mid-task. Conductor CLI 0.85.0 accepts environment variables only at `conductor workspace create --env KEY=VALUE` (repeatable); `session create` has none and an existing workspace cannot take new ones. The ship FO had to create a second workspace by hand from the task's branch with a hand-written resume boot, because `dispatch.sh` 0.2.0 has no credential surface and no resume mode. On 2026-09-11 (`ship-dispatch-watch-round-2`, task 7z) the Captain's chat approval and the worker's conn-delegated record collided on one gate attempt; today's batch proved the rule that holds: the ship FO records with the Captain's words, workers sync state by merge (never rebase) and never record.

## Accepted outcome

1. `dispatch.sh` accepts `--env-file <path>` (KEY=VALUE lines; values are read into the `conductor workspace create` argv as repeatable `--env` and never printed, logged, or written to the fence; the fence records only the key names) and refuses a file that is world-readable.
2. `dispatch.sh --resume <slug>` creates a fresh workspace from the task's existing branch (read from the entity or the fence), sends a resume boot that names the entity status, gate attempt, PR and candidate SHA, and records the new workspace/session in the fence under the slug with the previous ids kept (`r1`, `r2`, …); the previous workspace is archived only after the new one reports ready.
3. The boot header carries, verbatim: "Gate decisions are recorded by the ship first officer with the Captain's words. Sync state by merge, never rebase. Never record a gate decision." (replacing the r2 wording).
4. `pins/conductor-cli.contract` covers the `--env` and `--branch` shapes; the read-only probes stay as they are.
5. Rehearsal: a `--dry-run` of both modes prints the create command with `--env KEY=***`.

Profile recommendation: pilot.

## Ideation: technical approach (Pilot shape)

### Journey statement

1. DESIGNED — Captain provisions a credential mid-task and hands the ship FO a
   `KEY=VALUE` file. `dispatch.sh --resume <slug> --env-file <path> --conn-quote
   ... --conn-source ...` reads and validates the file (refuses if
   world-readable), builds repeatable `--env KEY=VALUE` argv entries, and never
   writes a value anywhere it persists.
2. DESIGNED — `dispatch.sh` resolves the task's branch (entity frontmatter
   first, fence record as fallback), reads the entity's current `status`,
   latest gate-attempt id, `pr`, and the branch's current SHA, and composes a
   resume boot message naming all four.
3. DESIGNED — `conductor workspace create --project-id ... --branch <task
   branch> --env KEY=VALUE [...] --message-file <resume-boot> --json` runs;
   `dispatch.sh` records the new workspace/session under the slug in the fence
   file, moving the prior round's ids into a `history` array (`round: "r1"`,
   `"r2"`, …) rather than discarding them.
4. DESIGNED — the ship FO (a person or `watch.sh`) polls the new workspace to
   ready via the existing `conductor workspace status` / `session status`
   probes (both already in the contract; no new Conductor verb is added).
   Only after that poll reports ready does `dispatch.sh`/the operator mark the
   prior workspace's fence entry as archived — this is fence-local
   bookkeeping, not a Conductor API call (Conductor's CLI has no
   archive/close/delete verb; confirmed against `pins/conductor-cli.contract`
   and `scripts/fixtures/fake-conductor-dispatch/conductor`'s synthesized
   `--help`, which mirrors the real 0.85.0 surface).
5. DESIGNED — every boot message (fresh dispatch and resume) now carries the
   literal sentence "Gate decisions are recorded by the ship first officer
   with the Captain's words. Sync state by merge, never rebase. Never record a
   gate decision.", replacing the bare "Sync state by merge, never rebase."
   line.
6. OBSERVED (unhappy path, unchanged) — `check_contract` still runs before any
   mutating call in both fresh-dispatch and resume mode; a used-surface
   mismatch still refuses with exit 5 before any `--env`-bearing invocation is
   attempted.

`semantics_unchanged`: no. This changes boot-message wording (item 5), the
fence's on-disk JSON shape (adds `history`, additive/backward-compatible —
see reverse-recovery receipt), and `pins/conductor-cli.contract`'s declared
surface (adds the `--env` token).

Non-goals: no workspace-archive/delete Conductor call is added (none exists to
call); no change to `watch.sh`'s or `close.py`'s fence-reading of the
top-level `workspace`/`session` fields; no change to the read-only probe
lines in the contract file; no multi-credential-file merge (one `--env-file`
per invocation).

### Persistence, recovery, data-safety boundaries

- Credential values live only in process memory and in the transient
  `--message-file`-adjacent argv passed to `conductor workspace create`; they
  are never written to the fence, the boot message, `stdout`/`stderr`, or any
  git-tracked file. The fence and any printed/dry-run line carry key names
  only (`--env KEY=***` in dry-run and log-safe echoes).
- `--env-file` must not be world-readable (checked before it is read) —
  refuse and exit before touching Conductor.
- Fence writes keep the existing single-file, path-scoped commit pattern
  already used for claim/dispatch commits (`git add _ship_fence/<sprint>.json`
  + scoped commit); resume reuses the same commit shape, one commit for the
  claim-carryforward and one for the recorded new workspace id, matching the
  existing two-commit-per-dispatch pattern.
- Resume is additive to the fence schema: the top-level `workspace`/`session`
  fields are overwritten to the new round's ids (so unmodified `watch.sh` and
  `close.py` keep working unchanged), and the prior round's ids move to a new
  `history` array field that only resume ever writes or reads. No existing
  reader is broken by the new field.
- The previous workspace is never deleted or force-torn-down; "archived" is a
  fence-local marker set after a ready observation, so a failed poll leaves
  both workspaces resolvable.

### Task-specific acceptance checks

- `--env-file` with a world-readable file exits non-zero before any
  `conductor` call (proven by a `FAKE_CONDUCTOR_LOG` that stays empty).
- A valid `--env-file` produces one `--env KEY=VALUE` per line in the real
  invocation's argv, and `--env KEY=***` (never the value) in `--dry-run`
  output and any echoed/log line.
- `--resume <slug>` with no prior fence entry for that slug refuses (there is
  nothing to resume).
- `--resume <slug>` with a prior fence entry produces a resume boot message
  containing the entity's status, latest gate-attempt id, `pr`, and a SHA, and
  a fence write that keeps the prior workspace/session id retrievable via
  `history` rather than overwriting it silently.
- Both fresh-dispatch and resume boot messages contain the new three-sentence
  gate-authority wording verbatim; the old bare "Sync state by merge, never
  rebase." line no longer appears alone.
- `pins/conductor-cli.contract` gains the `--env` token; a contract test
  proves `check_contract` refuses when `--env` is dropped from a fixture
  `--help`, matching the existing `FAKE_CONDUCTOR_DROP_SHAPE` pattern.

### Where it touches

| path | lines now | lines after |
|---|---|---|
| `kc-ship-flow/scripts/dispatch.sh` | 209 | ~300 (est.) |
| `kc-ship-flow/pins/conductor-cli.contract` | 7 | 7 (one token added to the existing `workspace create` line) |
| `kc-ship-flow/scripts/dispatch.test.sh` | 200 | ~280 (est., new cases for env-file, resume, gate wording) |
| `kc-ship-flow/scripts/fixtures/fake-conductor-dispatch/conductor` | ~90 (unread beyond line 60) | +`--env` token in synthesized `--help`; unverified until reopened |

`lines after` estimates for `dispatch.sh`/`dispatch.test.sh` are unverified
against the current tree beyond the read spans above; recorded as the
build stage's own count-against-diff obligation, not a prior estimate carried
forward.

### Stop numbers

Diff base: `main` at this entity's `started` timestamp (2026-09-14T10:50:16Z).
Stop and report rather than continuing past: 5 changed files, ~150 changed
lines, or if the resume-mode branch/SHA-resolution logic (item 2 above) grows
past a single helper function — that is the area most likely to run away,
since "read from the entity or the fence" is not yet pinned to one concrete
field name and could sprawl into a multi-source resolver.

### Reverse-recovery audit (`brownfield_capability_change`)

```yaml
reverse_recovery:
  trigger: "add --env-file passthrough, --resume, gate-authority boot wording, and --env/--branch contract coverage to existing dispatch.sh 0.2.0 and pins/conductor-cli.contract"
  boundary: "kc-ship-flow/scripts/dispatch.sh dispatch journey; search: kc-ship-flow/{scripts,pins,skills,CLAUDE.md}"
  layers:
    - surface: "--env-file / --env passthrough"
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: "grep for env|resume across scripts/pins/skills found no existing flag or fence field; accepted outcome names DEV-146 as the forcing incident"
      disproof_hook: "grep -n -- '--env' kc-ship-flow/scripts/dispatch.sh returns nothing pre-change"
    - surface: "--branch contract coverage"
      location: "kc-ship-flow/pins/conductor-cli.contract:4 (already lists --branch on the workspace create line)"
      completeness: WORKING
      need: REQUIRED
      evidence: "line 4 read directly: 'workspace create --project-id --branch --name --agent --model --effort --message-file --json'"
      disproof_hook: "grep -- '--branch' kc-ship-flow/pins/conductor-cli.contract"
    - surface: "--resume / fresh-workspace resume"
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: "dispatch.sh has one code path: query readiness, dispatch every not-yet-fenced slug; no resume flag, no per-slug targeting, no fence history field"
      disproof_hook: "grep -n resume kc-ship-flow/scripts/dispatch.sh returns nothing pre-change"
    - surface: "workspace archive/close Conductor verb"
      location: MISSING
      completeness: MISSING
      need: NO_OBSERVED_CONSUMER
      evidence: "pins/conductor-cli.contract lists auth whoami, workspace list/create/status, session status, sql only; scripts/fixtures/fake-conductor-dispatch/conductor's synthesized --help (mirroring real 0.85.0) has no archive/close/delete verb; two searches (contract file, fixture help text) found none"
      disproof_hook: "grep -iE 'archive|close|delete' kc-ship-flow/pins/conductor-cli.contract kc-ship-flow/scripts/fixtures/fake-conductor-dispatch/conductor"
    - surface: "boot-header gate-authority wording"
      location: "kc-ship-flow/scripts/dispatch.sh:165 ('Sync state by merge, never rebase.' only)"
      completeness: STUB
      need: REQUIRED
      evidence: "current line states the sync rule but never states who records a gate decision; skills/run-batch/SKILL.md:50 already documents Captain-recorded gate decisions at the workflow level, so the boot message is the stub that needs the FO-recorded wording, not a contradiction to resolve"
      disproof_hook: "grep -n 'Gate decisions are recorded' kc-ship-flow/scripts/dispatch.sh returns nothing pre-change"
  decision: build
```

No existing capability is replaced or contradicted: `--branch` coverage
already exists and is left as-is (only `--env` is a genuinely new token);
`workspace archive` is confirmed absent from the Conductor CLI surface, so
"archived" is designed as fence-local bookkeeping rather than inventing an
unsupported contract call; the fence schema change is additive (`history`
field) so `watch.sh` and `close.py` require no change; the gate-authority
sentence extends a stub line rather than overwriting a different existing
claim.

## Stage Report: ideation

- DONE: Load the Pilot `shape` contract and produce a technical approach for the four surfaces
  Journey statement, persistence/recovery boundaries, acceptance checks, where-it-touches table, and stop numbers recorded above.
- DONE: Run reverse-recovery review since this adds new claims to existing dispatch.sh 0.2.0 and pins/conductor-cli.contract
  Receipt above: `--env-file`/`--resume`/archive-verb classified MISSING (build), `--branch` classified WORKING (already covered, left alone), gate wording classified STUB (extend, not replace); decision `build`.
- DONE: Record the admission snapshot into the work item as ideation's Stage Report
  Accepted outcome (5 items, backlog-approved 2026-09-14, `resolution:backlog:1`) is this entity's Development Brief authority; non-goals recorded in the journey statement's `semantics_unchanged: no` paragraph above (no archive/delete Conductor call, no fence-reader changes in `watch.sh`/`close.py`, no multi-file `--env-file` merge).

### Summary

Reverse-recovery audit found `--env-file`, `--resume`, and any workspace-archive Conductor verb genuinely MISSING (build them), `--branch` contract coverage already WORKING (leave it, add only `--env`), and the boot-header gate wording a STUB to extend rather than replace. The chosen designs (additive fence `history` field, fence-local archive bookkeeping, three-sentence gate-authority replacement text) keep `watch.sh` and `close.py` untouched. Open risk carried to build: resolving the resume branch/SHA from "the entity or the fence" is not yet pinned to one field and is named as the stop-number watch area.

## Stage Report: implementation

- DONE: `dispatch.sh` accepts `--env-file <path>` (KEY=VALUE lines into repeatable `--env` argv, never printed/logged/fenced, refuses a world-readable file)
  `kc-ship-flow/scripts/dispatch.sh` `check_env_file_perms`/env-file parsing block; proven by `dispatch.test.sh` case i (dry-run prints `--env KEY=***`, never the value, never in `$LOG`) and case j (0644 file refuses before any conductor call).
- DONE: `dispatch.sh --resume <slug>` creates a fresh workspace from the task's existing branch, sends a resume boot naming status/gate-attempt/PR/candidate SHA, and records the fence under the slug keeping prior ids as `r1`/`r2`/… , archiving the previous workspace only after the new one reports ready
  Branch resolved via `git worktree list --porcelain` against the entity's `worktree` frontmatter field (not a guessed naming convention) in `resolve_branch_for_worktree`/`do_resume`; proven by case k (real mode: fence `history[0]` keeps the prior `ws-prior-round` id, `archived: true` once the fixture's `workspace status` probe reports "ready"), case l (dry-run resolves `--branch` from the real worktree, no create call), case l2 (resume boot body carries `Entity status`, `Latest gate attempt`, `PR`, `Candidate SHA: <40-hex>`), case m (no fence entry for the slug refuses with "nothing to resume").
- DONE: Replace boot header wording verbatim with the gate-authority sentence (replacing the r2 wording), update `pins/conductor-cli.contract` minimally to add `--env` coverage only
  `boot_gate_line` used by both fresh-dispatch and resume boot messages; contract line 4 gained only the `--env` token, `--branch`/other tokens untouched (`git diff kc-ship-flow/pins/conductor-cli.contract` is a one-token diff). Proven by case a2 (fresh-dispatch boot carries the full sentence verbatim).
- DONE: Add `--dry-run` rehearsal for both `--env-file` and `--resume` printing `--env KEY=***`, run/record the existing test suite green
  `dispatch.test.sh` (kc-ship-flow/scripts/dispatch.test.sh): 16/16 passed (a, a2, b, c, d, d2, d3, d4, e, f, i, j, k, l, l2, m) — commit `18addead`. `watch.test.sh` unaffected: 2 passed/9 failed both before and after this change (pre-existing `ModuleNotFoundError: No module named 'yaml'` in this sandbox, confirmed via `git stash`); its 2 passing cases (contract-mismatch refusal, version-only pass-through) stayed green after adding `--env` to `fixtures/fake-conductor-watch/conductor`'s synthesized `--help` (needed so watch.sh's own `check_contract` doesn't trip on the new shared contract token). `contract-test.py`'s one failure (`close.test.py`: `jsonschema required`) is unrelated and pre-existing.

### Summary

Implemented `--env-file` (masked, world-readable-refusing, repeatable `--env` passthrough) and `--resume <slug>` (git-worktree-derived branch resolution, resume boot with live entity facts, fence `history` array preserving prior rounds, one-shot ready probe for archival) in `kc-ship-flow/scripts/dispatch.sh`, replaced the boot-header gate-authority sentence in both fresh-dispatch and resume paths, and added the `--env` token to `pins/conductor-cli.contract`. Key decision: resolved the entity's stop-number risk area (resume branch/SHA resolution) via `git worktree list` matched against the entity's `worktree` field rather than inventing a naming convention, kept to one helper function (`resolve_branch_for_worktree`). Extended both `fake-conductor-dispatch` and `fake-conductor-watch` fixtures with the `--env` token so the shared contract change doesn't regress `watch.sh`'s own contract check. All 16 `dispatch.test.sh` cases pass on commit `18addead`; `watch.test.sh`'s pre-existing unrelated failures are unchanged.
