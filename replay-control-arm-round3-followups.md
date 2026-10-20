---
title: replay_dispatch.py builds a control arm free of the completion line even when a supplied scope file carries it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from the third external review round (Codex) of iamcxa/kc-claude-plugins PR #633 (head 01eaf231, review:5501913355), 2026-10-13, task `worker-completion-goes-to-main`, plus one Polish and one Deferred risk its validation cycle 3 recorded. None is P1 or Material, so none started a repair cycle there; each is filed here with its decline reason, per `## FO steps: review findings` step 5.

## Scope

- Finding 1 (Codex P2, `scripts/replay_dispatch.py` around line 93): `--no-completion-line` only skips the helper's own copy; a `--scope` file that already carries the completion directive (scope notes copied from a newer dispatch) still puts it in the control arm, so the "without it" arm is not without it. Candidate fix: reject such scope input in that mode, or strip the directive. Decline reason: the control arm is built by a maintainer following `skills/maintain-flow/SKILL.md`, which names the flag for the unchanged arm; no replay has been run with a copied scope file, and the duplicate is visible in the built `scope.txt`.
- Polish (validation cycle 3): `--scope` with a file already carrying the line writes it twice in the default arm; harmless to a replay.
- Deferred risk (validation cycle 3): the helper adds the line to every replay arm, including the release-tag arm of an unrelated rule's replay; only a routing replay needs `--no-completion-line` on its control arm. Becomes Material if a routing replay is run without the flag and its baseline is read as the unchanged behaviour.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the findings and decline reasons above are the scope.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Closed

Closed by the Captain 2026-10-20 (「照建議關掉 19 張。」) on FO's follow-up triage against origin/main ad44f0cb: maintainer-only tool; skills/maintain-flow/SKILL.md now states the completion-line behaviour and --no-completion-line.
