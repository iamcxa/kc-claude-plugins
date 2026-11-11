# RoboRev job 1725: adjudication before repair

Candidate: `a1a35a714510683a44a2ac5ec02241e7cb354f80`, unchanged.
Input: FO's `dispatch/implementation-1-message-4.md`, forwarding one High finding.
Local `roborev show --job 1725` could not access the daemon log in the sandbox;
the full daemon review was not independently read, and no clean review is claimed.

## Recommended disposition

Return the requested comparator change to FO as Needs decision. The factual
premise is reproduced: the pin is compared to the newest release while the
README can still owe sync. This is required reporting under AC-4, rather than an
implementation deviation. The approved design separately makes README merge a
precondition of the actual pin write. Do not change the comparison to the README
release without a Captain amendment of AC-4. Recommend retaining the released-tag
debt report and declining this as a current implementation defect; FO owns the
review disposition. No criterion or product byte changed in this round.

## Four evidence fields

- Released user and normal workflow: package maintainer/FO runs the read-only
  rollout command after release; after Captain approval a worker opens a README
  sync PR, Captain merges it, then FO moves the installed pin to that README tag.
- Observable harm: a prematurely upgraded checker can reject old-release records.
  That version-skew effect is reproduced below. No adopter write or premature pin
  move was reproduced from the reporting command; it has no write capability.
- Protected boundary: `contract[kc-dev-flow-2/references/sd/adoption.md#state-laws-check]`
  says pins do not move ahead of the README; `value-ac[AC-4]` explicitly compares
  pinned laws with the released tag. Reporting debt and executing its move have
  different preconditions in the approved design.
- Trigger evidence: `both-owed.log` shows sync and pin debt together, exit 1.
  `version-skew.json` shows an older checker exit 0 and newer checker exit 1 for
  the same old README and same committed second-dispatch event. Replacing the
  report comparator in a throwaway copy fails all three AC-4 laws-change subcases.

The version-skew risk is real. Treating a debt line as immediate permission to
move a pin would bypass the explicit merge precondition, so the proposed fix
changes the accepted report contract rather than repairing observed reporting
behavior against that contract. Whether to change that contract is the Captain's
choice through FO, not a decision taken by this worker.

## Reproduction

```sh
python3 -B probe.py /absolute/path/to/the/candidate-worktree
```

The probe uses a fake gh fixture for the debt report, a throwaway comparator
mutation, and actual package scripts extracted from existing 0.26.0 and 0.38.1 tag
objects. An adopter configuration line enables roborev in the old template. A
complete second implementation dispatch lacking roborev's scope-note instruction
passes the 0.26.0 laws runner; 0.38.1 requires that instruction on later fresh
implementation records and rejects it under L2. Both runners read the identical
old README and state range. This is a synthetic, model-free compatibility
reproduction, not a claim about a hosted adopter violation. Sources and exact tag
commit IDs are in `version-skew.json`; accepted ADR hashes are in
`adr-references.json`.

No pin or adopter repository was modified. Existing 17 tests, skill lint, required
ADR lint and comment ratio passed again at the unchanged candidate. The prior
candidate's mutation, live-read, number-guard and word-count evidence remains
under the parent implementation folder; those checks were not rerun in this round.
