---
title: pr_watch.py state is shared by every FO session on a machine, so one session consumes another's changes
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:pr-watch-state-per-session:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:pr-watch-state-per-session-backlog-1
              briefing:
                id: briefing:pr-watch-state-per-session:backlog:attempt-1:revision-1
                digest: sha256:5c446f28bb2bef7bc1b812ca1ad8d73beff036a9cf49a173f254ed64e55eaa7a
                room-ref: ./pr-watch-state-per-session/review/backlog/briefing-1
---

Filed from a package-issue candidate the Captain approved on 2026-10-14 (「1,3」). On 2026-10-14 this workflow's FO ran `pr_watch.py wait` for its own PR and was woken by spacedock-dev/subspace-relay#368 ("checks pending -> green"), a PR the relay FO session had added; the wake consumed that change, so the relay FO's own `check` or `wait` would no longer report it.

## Scope

- `pr_watch.py` keeps one machine-local state file (`~/.local/state/kc-dev-flow-2/pr-watch.json`) for every session; `check` and `wait` report changes "since the last look" and record the look, so concurrent FO sessions in different repositories read and mark each other's PRs.
- Containment used here: `--state /tmp/jm-fo/pr-watch.json` for this session; the relay FO was not told.
- Candidate fix: a per-workflow or per-session default state path (for example keyed by the workflow directory), or per-PR seen markers per caller; plus the Delivery authority and mod text that name the command.
- Related: `fo-lifecycle-mod` (its idle and startup steps run `pr_watch.py add` and `wait`).
- Second report, from the relay FO (task `owner-sees-all-feedback-page`, PR spacedock-dev/subspace-relay#368, 2026-10-14): its `pr_watch.py add` printed "watching 3 PR(s)" because the default state already held iamcxa/kc-claude-plugins#642 and #643 from this workflow's FO; it used a per-session `--state` file. It suggests defaulting the state per session (for example keyed by a session id environment variable) or naming `--state` in the Delivery authority step.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
