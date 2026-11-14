---
id:
title: The extracted package says five rules that already worked, each once, where its reader loads it
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
---

Five rules were followed by hand today and worked; the extracted package's text does not carry them. Until it does, a First Officer or worker that loads the package cannot follow them, and the package cannot be put into real use with them.

## Scope

- Source: the reform session's scope 3 under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, message 6dd41248, 2026-11-14); it reports that the Captain approved the order with "Go ahead with the plan." in its own conversation (relayed, not a ruling here). Admission is recorded by FO under the grant.
- Outcome: the package text a First Officer and its workers actually load says these five things, each once, each where its reader loads it: (1) a first report to the Captain within about ten minutes of a dispatch, asking nothing; (2) every Captain-facing message about a task carries elapsed and budget minutes, with machine time and waiting-on-a-person time counted apart, and an overrun is said at once; (3) before a third dispatch in one stage, stop, name the assumption the attempts shared, and ask re-cut, continue or close; and at half of a time box ask whether the work still serves its goal; (4) relayed words are not a ruling: only the Captain's first-hand word or a recorded grant is; (5) when a design ran a check during design, the design links each criterion to that run's record.
- For each rule the design states: which approved outcome it serves (by its number in the package's outcomes document), which existing sentence it replaces or makes unnecessary, and the net word change for each reader. If the package grows, the design says by how much and what was removed to pay for it; removing a rule these five make redundant is in scope.
- Where the work lands: the private working repository that holds the extracted package, named here only as that and pinned by commit SHA. Commits and a merge there are inside the grant. Nothing private is written to this state branch.
- Proof: no test that asserts the text contains words. A fresh reader, given only the package as a First Officer or a stage worker would load it, is asked what it must do at minute ten, at an overrun, before a third dispatch, when handed relayed words, and after running a check in design; its answers are compared with the rules.
Non-goals: any other rule; restructuring the three profiles; a new script; re-admitting tests; any change to this repository.
Budget: 2 cycles per stage
Stop condition: two hours from the first dispatch; at half of that, one check whether the work still serves the stated goal, and if not, stop and report instead of finishing; the design needs a decision only the Captain can make; a rule cannot be placed without restructuring a profile.

## Acceptance criteria

**AC-1**: Each of the five rules appears once in the text its reader loads, and for each the design's table names the outcome served, the sentence replaced or made unnecessary, and the net word change per reader.
Verified by: the validator reads the candidate at its commit and checks each row against the files; word counts by the package's own counting command.

**AC-2**: A fresh reader given only the package as loaded answers the five questions in line with the rules, as a First Officer and as a stage worker.
Verified by: the reader's written answers beside the rules, judged by the validator; the reader's prompt holds none of the rules' wording. Limit: one reader per role, one run.

**AC-3**: The package's total words per reader did not grow, or the growth and what paid for it are stated.
Verified by: the counting command at the base and at the candidate.

## FO alignment

Alignment: not needed before ideation: the five rules and the proof are stated in the scope the reform session gave under the Captain's grant; the design returns at the ideation gate and goes to the reform session first.
Surfaces: none
Visible change: none
Release review: not needed: package text with no release on a journey map.
