# implementation-7

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #639 24029378
Model: sonnet

Follow-up message to the live implementation worker: FO fix authorization after its phase-1 reproduction confirmed the Codex round-3 P1 and its class (a wait whose exit is a pr_watch change line instead of a state).

## Checklist

Same checklist as implementation-6.

## Scope notes

Apply a) to e) as proposed, with the stated known limit about the 60 s bound: an opening rule that every wait ends on a state read (`check` row or `gh pr view`), `wait` only as a wake-up, no re-`add` of a listed PR; step 2 green on the Draft read as a state, checks=none counted only after two reads at least 60 s apart; step 4 ready settled at least 60 s after the flip with checks green and nothing pending; the no-applicable-checks premise is "the PR is ready"; resume judged by those states. Tests (1) to (3) with the named mutations, each shown red without the fix. Keep the text short. No pr_watch.py change. Round-1 and round-2 fixes intact. Inside the four files. Roborev gate (base 24029378), push (no force), CI green, stage report committed, completion to `main`. Do not comment, request reviews, mark ready or merge.
