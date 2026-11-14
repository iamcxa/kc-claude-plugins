---
id:
title: Sealed evidence and the delivery gate's own text can be written without a home-directory path or a private repository name, so the state guard can refuse those two classes
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo-backlog-1
              briefing:
                id: briefing:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:backlog:attempt-1:revision-1
                digest: sha256:033debd07b66ec73b2dbca7919aa0e3767696c9fd9a4fb1d623987970ee45479
                room-ref: ./gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/review/backlog/briefing-1
---

The state guard merged in pull request 871 is installed with private task slugs and tailnet hostnames refusing, and private repository names, the email and the home directory only warning. Two of the warning classes cannot move to refuse today, because a refusal there has no legitimate way forward: a home path or a private repository name can sit inside sealed worker evidence, and the delivery gate's own form demands an absolute acceptance command in the gate summary and in the Captain-steps record.

## Scope

- Source: the reform session's ruling under the Captain's standing grant (Paseo 26215d96, message bc65ce97, 2026-11-14), after the Captain referred the guard decision to it with 「你問一下改革者」 (chat with the second dev2 FO, 2026-11-14): option (a) is installed now on the condition that this follow-up is filed. Held at backlog for admission in the reform session's next scope message.
- Bite: the observer's report on the archived task state-branch-writes-carry-no-private-identifiers (observer.md, 2026-11-14) observed absolute home-directory paths in that task's validation briefing summary and in its `captain-steps/1.md`, written by FO because `kc-dev-flow-2/scripts/delivery_gate.py steps` requires the exact acceptance command, which was absolute. The design of that task measured the home class in 75 of the last 200 state commits and the private-repo class in 11.
- Outcome: a redaction path for sealed evidence, and for gate-summary and Captain-steps text, with the delivery-gate form no longer demanding an absolute command; then the guard's private-repo and home classes are set to refuse on the live state checkouts.
- consumer: both First Officers writing gate text and Captain-steps records; workers sealing evidence; the Captain, whose words were 「出現就不準推」.
- Open for the design: what a refused commit's way forward is for each class (rewrite, relative path, a "not archived (private)" line); whether Spacedock's verbatim storage of gate summaries needs an upstream change or is covered by FO writing clean text; how existing records stay valid.
Non-goals: changing anything already on the branch or in its history; the email in commit metadata (the Captain's separate decision); patching Spacedock or filing anything upstream without the Captain.
Budget: 2 cycles per stage
Stop condition: a writer of these classes turns out to be Spacedock's own with no clean-text route for FO; existing records cannot stay valid; a suspected key is found; or the design needs a decision only the Captain can make.

## Acceptance criteria

**AC-1**: A gate summary and a Captain-steps record that pass the delivery-gate checks can be written with no home-directory prefix and no private repository name.
Verified by: a real delivery-gate question and steps check on a throwaway task whose committed bytes are scanned for the two classes, with commands and exit codes.

**AC-2**: Sealed evidence holding a private repository name has a recorded way forward that is not a bypass, and the result commits under the guard with that class at refuse.
Verified by: one real refused commit and one real accepted commit on a throwaway state checkout with private-repo and home at refuse.

**AC-3**: With both classes at refuse on a throwaway copy of the live state branch, a replay of the commits written after the change shows no refusal that lacks a way forward.
Verified by: the replay's per-commit result, counts by class. Limit: a replay of a bounded window, stated in the report.

## FO alignment

Alignment: not needed before ideation: the outcome and its bite are stated by the reform session's ruling and the observer's report; the open design points return at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance with no release.
