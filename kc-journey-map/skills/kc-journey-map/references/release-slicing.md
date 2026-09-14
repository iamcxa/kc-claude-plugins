# Propose the smallest complete release

Read this for map release proposals and `plan-release`. Claude and Codex follow the
same order: **whole map → prose reduction proposal → human decision → release
boundaries → checked Development Brief handoff**. Reuse existing maps and answers.

## Make the choice visible before moving cards

Show the complete journey before negotiating its first slice. Keep later paths on
the map. If no journey outcome or time appetite (the user's investment limit) is
known, ask that missing input early, one decision at a time. Map-only exploration
may remain unbudgeted; it is not development admission. Do not invent a deadline
or infer consent from silence.

Then do the reduction work yourself. State in ordinary prose which person can go
from which starting situation to which observable result, the smallest retained
stories, and which stories can wait and why. For each retained story, ask: **if we
remove this, which observable outcome or necessary constraint breaks?** A story
that changes neither must be proposed for deferral. Test the whole path, not just
a feature list. An empty column belonging to a later outcome is legitimate.

Check necessary constraints explicitly; do not shrink by dropping safety, quality,
authority or correctness conditions. Cite evidence for prerequisites, not story
order. Distinguish already available capabilities from new work. The completion
estimate includes integration and validation; record its evidence and uncertainty
separately from the user's appetite. Story count, lines of code and an unsupported
agent guess do not establish fit. If fit is unknown, investigate the uncertainty
or propose a bounded learning journey with its own observable result.

When the candidate is oversized, incomplete or contains optional retained stories,
produce a smaller complete proposal before offering development handoff. Do not
merely warn and continue to a ready brief. If further reduction changes the user's
goal or a necessary constraint, stop the dependent handoff and ask that concrete
tradeoff; do not loop endlessly or weaken the goal silently. The user may keep a
broad release on the map while its development handoff remains draft.

Use the host's available Ask UI for a concrete unresolved choice, with the prose
recommendation already visible. Ask one decision at a time. If that UI is not
available, use one plain-text question. Reuse explicit prior acceptance when its
scope and premises still match; no answer is not acceptance. After acceptance,
change release membership, preserving IDs, requirements and deferred stories.
Read back human canvas edits first using the existing canvas contract.

## Check the handoff, without inventing another brief

`journey-handoff.mjs` is this skill's guarded handoff entry point. The ordinary
`journey-contract.mjs` command remains an evidence document generator and does not
admit a release. Dev-flow still owns its five-section Development Brief and its
own admission requirements. This helper copies that existing brief unchanged on
pass; it does not validate its section schema or start development.

For one candidate, keep a pre-cut copy of the canonical YAML in the consuming
repository's task scratch directory. This is comparison evidence, not a second
planning authority or an ongoing ledger. Keep the full map in the canonical YAML.
Prepare proposed membership in a scratch candidate YAML while the canonical map remains
unchanged. Use that candidate for the proposal's checks; after acceptance, apply the
reviewed boundaries to the canonical source and check its final bytes before handoff.
Create a compact assessment JSON beside the draft brief. Record:

| Field | Meaning |
| --- | --- |
| `version`, `release`, `goal` | `1`, selected release ID, and exact current release goal |
| `baseline_sha256`, `source_sha256`, `brief_sha256` | SHA-256 of the pre-cut YAML, current YAML and existing draft brief bytes |
| `outcome` | `start`, observable `finish`, `verification`, and assessed `complete: true/false` |
| `constraints[]` | Existing rule `id`, assessed `preserved: true/false`, and `verification`; cover rules on selected activities and any other necessary rules |
| `retained[]` | Each selected story's `id`, assessed `necessary: true/false`, `breaks` (`outcome` or `constraint:<rule-id>`) and removal-test `reason` |
| `deferred[]` | Each story removed from the selected release, or left out of the first cut from unplaced stories: `id` and `reason`; it remains on the map |
| `dependencies[]` | Selected `story`, `prerequisite` story ID or external capability, and factual `evidence`; a prerequisite outside the selected stories also needs assessed `available: true`; use `[]` when none |
| `unresolved[]` | Outstanding value, scope, acceptance or fit decisions; technical questions that do not change these stay in the brief |
| `budget` | Positive numeric `appetite`, `unit` (`hours`, `days` or `weeks`), `user_basis`, positive `estimate` in the same unit, and factual `estimate_basis` |
| `acceptance` | Human `decision: accepted`, `evidence` identifying the actual conversation/decision, and the proposal `digest` |

A removal entry might be:

```json
{"id":"collect-book","necessary":true,"breaks":"outcome","reason":"Without collection the reader cannot take the reserved book home."}
```

Run from the activated plugin root, using absolute paths for consuming artifacts:

```sh
node lib/journey-handoff.mjs <pre-cut.yaml> <journey.yaml> <assessment.json> <brief.md> --digest
```

This checks the candidate and prints a digest of the assessment excluding its
`acceptance` envelope. It does not grant acceptance or emit a brief. Present the
proposal and draft, then record the user's actual decision and that digest in
`acceptance`. If acceptance already exists, verify it covers these exact premises;
do not relabel a changed proposal as an old decision. The digest binds the source,
baseline, brief, budget, removal judgments and other recorded premises.

After applying accepted boundaries and confirming the final source/brief match
that decision, refresh their byte hashes and digest to the reviewed final contents.
Formatting-only changes may be reconciled with the existing decision; changed
value, scope or acceptance requires the human's new decision. Then run:

```sh
node lib/journey-handoff.mjs <pre-cut.yaml> <journey.yaml> <assessment.json> <brief.md> --out <new-attempt-handoff.md>
```

The command refuses missing or stale hashes/acceptance, unsupported assessments,
recorded optional stories, incomplete outcomes, lost constraints, missing deferral
reasons, unresolved decisions and an estimate over appetite. It compares the full
baseline with current YAML, permitting selected or previously unplaced story release changes, the selected
release goal and new release bands; other requirements and membership stay intact.
A requirement correction needs a reconciled full-map baseline before a new cut.

On failure, keep the handoff draft, explain the specific refusal and return to the
reduction proposal or missing decision. Do not bypass it by handing off the input
brief or ordinary release contract as ready. A successful output is specific to
its printed source/assessment/brief hashes: re-run just before handoff if anything
changed. Use a fresh output path per attempt. Existing outputs are refused and
left untouched; a past file is not evidence of a current pass.

The executable checks recorded consistency and explicit verdicts. It cannot prove
semantic completeness, the globally smallest possible journey, evidence truth,
estimate accuracy or authentic human approval; these remain agent analysis and
human review. It also cannot constrain a host that ignores the skill. Report these
limits rather than claiming a universal implementation gate.

## Why these criteria

- [Jeff Patton's story mapping guide](https://jpattonassociates.com/wp-content/uploads/2015/03/story_mapping.pdf)
  supports seeing the whole journey and slicing a coherent outcome for a target user.
- [DORA's small-batch guidance](https://dora.dev/capabilities/working-in-small-batches/)
  supports small, independently validated work and short feedback loops. Its work-batch
  guidance is not a universal release deadline or a story-count limit.
- [Shape Up's appetite](https://basecamp.com/shapeup/1.2-chapter-03)
  separates the amount worth investing from an estimate and makes scope variable.

The removal test and executable admission checks above are this skill's synthesis,
not an industry standard that mechanically proves a minimal release. Technical task
decomposition remains with dev-flow after the accepted value slice is handed off.
