# dev2 laws

Invariants of the committed `spacedock-state` history, checked by `<package>/scripts/laws_check.py`
and listed here so a reader can see what each law is for. Each run judges only the events the commits of
one push add, the `before..after` range GitHub reports for a push to the state branch, each read at its own
commit. A violation is reported in the run of the push that added it; the next push is judged on its own
commits, so its run is green again whether or not the violation was repaired. The run reports; it does not
block `merge guard`, a dispatch or a push. `<package>/scripts/test_laws_check.py` fails when this list and
the runner's registry differ.

## L1 observer-before-sentinel

- **Rule.** When the workflow README lists `learn`, an observer report, or its `observer not run: <reason>`
  line, is committed no later than the commit that writes `pr: pr-merge:<N>` in a task's frontmatter.
- **Event.** A commit in the range where a top-level or `_archive/` `<slug>.md` has a parsed `pr:` sentinel
  and its first parent's file, followed through a rename, did not. The sentinel is read from parsed
  frontmatter, not by substring. An archive move that leaves `pr:` unchanged is no event; a `merge guard --rework`
  that clears `pr:` and a later sentinel are two events.
- **Judged by.** `<package>/scripts/observer_check.py <state> <slug> --rev <that commit>`.
- **Bit.** An adopter's first officer archived a task with no observer report (2026-10-14).
  `observer-before-merge-guard` introduced the rule; its report is committed one commit before its sentinel.
- **Bounds.** The README is the one supplied at run time, so a re-run or a local run given a different README
  can judge the same range differently.

## L2 dispatch-record-complete

- **Rule.** Each dispatch record has every part `<package>/scripts/dispatch_records.py` requires and names no package script
  without its directory; a first implementation record carries each `ADR:` or `Migration:` line its task reserves; and each
  Captain amendment of its task is named in a dispatch checklist; an ideation record's task records a `Result:` line when
  its `## FO alignment` says `Alignment: needed`; and no `Captain:` or `Asked:` amendment line holds a JSON backslash-quote. Amendment headings belong in one
  `## Captain amendments` section, with unique numbers, balanced fences, one nonempty `Captain:` and one
  whole-value `Supersedes:` list. Fenced examples and `Superseded text:` are not live metadata;
  `### Feedback Cycles` ends an entry.
- **Event.** A commit in the range that adds a `dispatch/<name>.md` record, status added, or renamed from a path
  that is not a dispatch record. A record added, then corrected or deleted in a later commit of the same push, is
  judged as added; a record deleted and added again is judged at each add. Archiving a task or renaming its folder
  is no event.
- **Judged by.** `<package>/scripts/dispatch_records.py <task folder>` and
  `<package>/scripts/dispatch_records.py --names <records>`, both over the record, its folder and the task file beside the
  folder (or its `index.md`) as committed at that commit. The added checks print `reserved line '<kind>: NNNN' missing from scope notes`,
  `Captain amendment N named in no dispatch checklist`, `'## FO alignment' records alignment as needed with no 'Result:' line`
  and `Captain amendment N Captain line holds a backslash-quote copied from JSON` (or `Asked line`).
  Structural errors print `<dispatch-file>:<line>: Captain amendment form at <task-file>:<line>: <defect>`;
  L2 classifies this known shape as a violation. Unknown output and missing execution evidence remain exit 2.
  Dispatch checks structure without requiring pending worker moves or future artifacts. Full
  `<package>/scripts/design_surfaces.py check` retains move/replacement checks; `check --seed` retains seed-only admission.
- **Bit.** Measured 2026-10-16 on this repository's state branch: 15 missing parts in 10 of 48 records
  added after commit `49da5ddb` at its commit `e73634e6` (4 bare script names, 7 without the completion recipient
  `main`, 4 without an absolute `Package root:`). Measured 2026-10-19 on the same branch at `4e635405`: 4 of 7
  first implementation records whose task reserved a number lacked the line, and 1 of 237 record adds left an
  amendment named in no checklist (`f4bb51b3`).
  Measured 2026-10-26 on the same branch at `91257c14`: 16 of the 24 ideation records of tasks with `Alignment: needed` were
  added with no `Result:` line in their task, and one task file held a backslash-quote on an amendment line.
- **Bounds.** The folder run is given the README supplied at run time, so a first implementation record is also
  judged against that README's `extensions:` list; a different README can judge the same range differently. A record
  whose task file is absent at its commit is not judged for the reserved line or the amendment. The alignment line is read
  only as `Alignment: needed`; another spelling is not judged, and the `Result:` line is checked for presence, not for truth
  or for being written before the dispatch inside one state commit.


## L3 amendment-append-only

- **Rule.** An existing amendment's number, order, header, raw metadata (including multiline `Design:`
  and fenced text) and recorded moved text survive unchanged. `parse_amendments` in `<package>/scripts/design_surfaces.py`
  supplies raw spans; terminal blank separator lines are outside protection. A new entry may follow the
  existing entries. A worker may append `Superseded text:` and criterion blocks to an entry, or more blocks
  after its existing payload, preserving metadata and payload bytes as a prefix. `payload_append_allowed`
  requires the new portion to start with a criterion declaration; it checks shape, not origin or truth.
  Arbitrary metadata extensions and edits to already moved blocks violate the law.
- **Event.** For each changed task in the existing `walk()` push range, compare the first-parent and
  event-commit blobs. A task introduced with amendments establishes initial bytes. Existing amendments
  removed, reordered, renumbered or edited, including task deletion, are reported at that commit even if
  repaired or deleted again later in the same range. The next clean push does not re-report old events.
  No first-introduction scan, second history walker or anchor ledger is used.
- **Paths.** Flat `<slug>.md`, `<slug>/index.md`, and their `_archive/` forms are recognized. Git rename
  records preserve identity; delete/add layout or archive moves use an unambiguous same-slug match.
  Unchanged moves pass; titles do not establish identity. Ambiguous matches, duplicate/malformed protected
  spans and unreadable blobs yield `L3 amendment-append-only: cannot judge` (exit 2), while other law results
  still print. For an unmatched fence, an edit in the known prefix before the fence is a violation; when
  only the uncertain span differs the result is cannot-judge. Prose `Supersedes:` remains extractable as
  raw metadata and cannot conceal a known rewrite.
- **Judged by.** `<package>/scripts/laws_check.py` reads the package/parser version, explicit `before..after`, the existing
  non-merge commit/change list, each event's first-parent/current blobs and Git rename records. L3 uses
  neither runtime README nor working-copy/tip task enumeration. Fixing these inputs fixes L3's result
  despite subsequent task, archive or README changes; L1/L2 retain their own README dependencies.
  Diagnostics identify old/new paths, amendment number, event commit and changed field/span, not an actor.
- **Bit.** Package state rewrites `95fe8ce1bd7ff58798634b733abb4115fecfe23d` (Supersedes),
  `16129ea4c1a238dd885e9f08513ce3a52ad27f2d` (Design paragraphs) and
  `34c820b5db98d5da119a1b021ce6af45d616acdc` (Design bullets before an unmatched fence).
  Parent-to-event CLI replays and the frozen corpus comparison are recorded in [validation](../../VALIDATION.md#amendment-structure-and-push-range-law).
- **Bounds.** The existing walker excludes merge commits themselves and judges their non-merge side
  commits. Uncommitted edits, edits wholly inside an excluded merge commit, earlier pushes, rewritten Git
  history and never-recorded rulings are outside this proof. Missing/truncated parents are exit 2. Missing
  rulings, initial quote fidelity and criterion ids omitted by meaning remain observer duties.
  Reporting happens after commit/push; it does not block push, dispatch, gate preparation or merge guard
  and does not revert a change. Hosted enforcement requires adoption of an actually published package pin
  and an observed state-push run. This candidate changes no CI trigger or pin; CI cost per PR is unmeasured.
