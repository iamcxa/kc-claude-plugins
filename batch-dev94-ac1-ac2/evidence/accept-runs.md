# Accept-station runs, DEV-94 AC-1 and AC-2, 2026-09-04

First Officer on the laptop. Every run below is the FO's, at the pinned candidate SHA.

## AC-1 — `dev94-ac1.g1`, candidate `14932d5a`, ACCEPTED (PR #372)

| check | result |
|---|---|
| `CANDIDATE_SHA` == remote head | match |
| falsifier: batch approval without `defaults` | exit 1, refused |
| falsifier: same approval with a conforming `defaults` | exit 0 |
| six single-field-missing mutants | all exit 1, each naming its own field |

The FO's first attempt at the conforming block used invented enum values and was
refused — evidence the schema constrains values, not only field presence.

Residual: `kc-plan-receipt.v1.schema.json` moves byte-for-byte with no `SURFACE` line.

## AC-2 round 1 — `dev94-ac2.g1`, candidate claimed `074b7371bfb6`, REFUSED

Two defects, both in the worker's own Evidence rather than its logic:

1. `CANDIDATE_SHA` named a commit absent from the repository. First eight hex
   characters matched the pushed head (`074b7371a0db`), the rest did not — a SHA read
   before a rewrite and never re-read after the final push.
2. `WITHOUT_IT_COMMAND` was `test -f scripts/ship-flow/accept-evidence.py`, which proves
   the file exists and nothing about whether it works — the same empty shape the item
   exists to catch.

Its logic was already right: run against the three recorded blocks it accepted DEV-90
and DEV-92 and refused DEV-91 for the correct reason. Round 2 was told to keep that and
fix the evidence.

## AC-2 round 2 — `dev94-ac2.g2`, candidate `6fee7d1f`, ACCEPTED (PR #373)

| check | result |
|---|---|
| `CANDIDATE_SHA` == remote head | match |
| its own `WITHOUT_IT_COMMAND` at `BASE_SHA` | exit 1 |
| the same command at the candidate | exit 0 |
| six fixtures rerun with the worker's script | reproduce its reported results exactly |

**AC-3b, which the worker did not report — the FO ran it.** Ablation of each check in turn:

| ablation | DEV-91 | narrow-variant mutant |
|---|---|---|
| none | refused | refused |
| base run disabled | **accepted** | refused |
| static path check disabled | refused | **accepted** |

Neither check subsumes the other; both earn their place.

Environment note: a `git archive` export has no `.git`, so every fixture run exits 128
with "not a git repository". The runs above are in a real `git worktree`. A checker that
shells out to git must be exercised where git works.

Residual: one `SURFACE` line for the script, none for the six fixture files.

## Outcome

- AC-1 merged as #372 (`0958df75`), 2026-09-05T02:22Z.
- AC-2 merged as #373 (`1b61997b`), 2026-09-05T02:28Z, retitled `feat(ship-flow)` before squash.
- Round-1 branch deleted from origin after merge; its refusal and Evidence stay in this directory.
- Captain questions between first dispatch and this record: 0 mid-batch. Two asked at batch boundaries (S23 unblock, scope name) — outside the AC-3 window, which opens at dispatch and closes at the UAT message.

## Note on commit bca55597

Its subject says "dispatch round 4"; the dispatch in that same script failed closed with `intent: state checkout dirty` (S30 had been appended before the commit ran), left no intent, and was retried after the commit. The retry is the dispatch of record; see `ac2-r4-dispatch.log`.
