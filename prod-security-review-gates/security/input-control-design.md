## Scope

- Confirmed 2026-10-14 on origin/main: `PASSED = re.compile(r"Verdict PASSED[\s\S]{0,160}?" + SHA)` in `kc-dev-flow-2/scripts/delivery_gate.py`; the docstring says only "`Verdict PASSED` within 160 characters". Nothing in the validation skill or stage text states that exact line.
- Every merge ask runs this check, so each new validator wording holds a delivery.
- Candidate fixes: accept a tolerant verdict form (for example `Verdict:? (recommended:? )?PASSED`, case-insensitive), or state one exact verdict line in the validation stage contract and check it there; which, and whether the checker or the contract owns it, is for ideation. Related: `dev2-laws-check`.
- Non-goals: set in `## Design` under Limits.

## Acceptance criteria

`<package>` is the kc-dev-flow-2 package root; paths are relative to `kc-dev-flow-2/` in `iamcxa/kc-claude-plugins`. Base is origin/main `c545b896` (package 0.22.1); every base observation was made on it on 2026-10-15. New tests go in `scripts/test_delivery_gate.py`, which CI already runs (step `test_delivery_gate.py` in `.github/workflows/kc-dev-flow-2-tests.yml`). A "record" is `<task folder>/dispatch/validation-<N>.md`; `S`, `S1`, `S2` are full 40-character lowercase hexadecimal SHAs. The prototype named below is a machine-local copy of origin/main in `/tmp` (not committed, not a repository file); the committed tests carry synthetic fixtures. Every criterion is not yet verified: the implementation does not exist.

**AC-9** A merge ask on a head that no validation was dispatched on exits 1, naming both heads.
Verified by: a test whose latest record carries `Candidate: S1` and `--head S2` exits 1 and prints both SHAs and `next: hold the ask; revalidate this head or tell the Captain the difference.`; the same record with `--head S1`, and with the first 7 characters of `S1`, exits 0. Replay on the real archived task `observer-before-merge-guard` (PR #632, whose head moved from `40c714a6` to `7679ab7a` when `origin/main` was merged in): a scratch copy of its folder in which `dispatch/validation-3.md` gains the line `Candidate: 40c714a64e9967dc0cad04e2ffc4e8f720a12999` exits 1 at `--head 7679ab7a` and 0 at `--head 40c714a6` (both observed on the prototype 2026-10-15); the archived records as written, with no such line, exit 2 (observed).
Falsifier: skip the comparison once a line exists; the `S1`/`S2` case exits 0 and the test fails. Limit: the replay copy carries a line FO did not write at the time. `migration-and-number-guards` cannot be replayed: its archive has no `dispatch/` folder, so the check exits 2 on it (observed), a hold, not the exit 1 that the old report-text check gave at `83cad4f7` against candidate `aff49ab3`.

**AC-10** A record that does not name the head in the one form holds with exit 2, and the hold line prints the form.
Verified by: subTests, each exiting 2 with `Candidate: <40-hex head>` in the output: no `dispatch/` folder; a folder with no `validation-*` record; the latest record with no line; a line with an 8-character SHA; a line with text after the SHA (`Candidate: S (branch x)`); the relay form `Candidate: spacedock <sha>; marketplace <sha>` found in 4 archived records; a valid line under the first `## ` heading instead of above it; a valid line in an older record under a newest record with none. Observed on the prototype for the no-folder, no-line and relay-form cases.
Falsifier: accept any hexadecimal token after `Candidate:`; the 8-character and trailing-text subTests exit 0 or 1 and fail.

**AC-11** The highest-numbered validation record decides, and a record may name several heads.
Verified by: subTests with `validation-2` naming `S1` and `validation-10` naming `S2`: `--head S2` exits 0 and `--head S1` exits 1 naming `S2` (observed on a scratch copy of the archived task `journey-server-host-pilot`, 7 validation records); a record with two `Candidate:` lines exits 0 when `--head` equals either and 1 when it equals neither (the shape of a task that validates two repositories, relay `spacedock-install-beta`).
Falsifier: choose the record by sorted file name; `validation-2` wins over `validation-10` and the first subTest fails.

**AC-12** The check reads no validator prose and claims no verdict.
Verified by: a test whose task file holds a `## Stage Report: validation` section reading `Verdict REJECTED at S` and whose latest record names `S` exits 0, and so does a task file with no validation report at all; no output line of any exit says `passed` or `PASSED`; `grep -c 'Verdict\|PASSED\|REJECTED' kc-dev-flow-2/scripts/delivery_gate.py` prints 0 at the candidate (3 lines at base).
Falsifier: read a `## Stage Report: validation` section and hold on `REJECTED`; the first test exits 2 and fails. Limit: a REJECTED validation at the head FO then asks to merge passes this check; reading PASSED or REJECTED stays FO's judgement at the gate (Captain, amendment 2).

**AC-13** FO reads no more words than at base at the merge ask and none at the other four moments; the dispatch moment is named.
Verified by: with `len(text.split())` as in the learning "Measure the words FO reads at each moment", the merge-ask passage in `references/sd/workflow.md` ("A PR delivers only the commit ..." through "... what it printed.") is 84 words at base and at most 84 at the candidate (prototype 83); the exit 0 output of `delivery_gate.py` is at most 20 words (prototype 20) and the exit 1 output at most 27 (prototype 25), the same two fixtures run on base and candidate; `git diff origin/main -- kc-dev-flow-2/references/sd/mods kc-dev-flow-2/extensions kc-dev-flow-2/scripts/pr_watch.py` is empty, so startup, idle on an open PR, idle on a merged PR and after the archive read the same bytes. The dispatch-record passage ("FO saves those scope notes ..." through "... wrote it.") grows from 64 to 75 words (prototype) at the moment FO writes a validation record; `python3 <package>/scripts/lint-skills.py` prints `references/sd/workflow.md: N of 5511 words` with `WORKFLOW_WORD_BUDGET` unchanged (prototype 5521 fails the budget; dropping the 26-word sentence "A PR delivers only the commit on its head; ... exact commit is pushed.", which no `need` string in `scripts/test_sd_dispatch.py` names, gives 5495).
Falsifier: add one sentence to the merge-ask passage; its count exceeds 84 and the comparison fails. Limit: counts text and script output, not a measured FO session; the exit 2 output grows from 20 to 30 words on the failing path by design (it prints the form), which no passing path reads.

**AC-14** Nothing of #647's verdict parsing remains, and the text pins follow the new wording.
Verified by: at the candidate, `git diff origin/main -- kc-dev-flow-2/skills/validation/principles.md` is empty; `scripts/test_sd_dispatch.py` has no `validation-states-the-verdict-line` entry; its `dispatch-record` and `readme-keeps-delivery-rules` entries name the new `Candidate:` and head wording, each with a `swaps` mutation that deletes it and makes the entry fail; `test_sd_dispatch.py`, `test_delivery_gate.py`, `test_lint_skills.py` and `lint-skills.py` exit 0.
Falsifier: leave the `Candidate:` clause out of `workflow.md`; the `dispatch-record` entry fails. Limit: `test_sd_dispatch.py` needs a Spacedock plugin root (`--sd-plugin-root`); CI's pinned root is the proof where this machine has another version.

## Design

Redone under Captain amendment 2. The bite is unchanged: FO asked the Captain to merge a PR head that no validation had checked (observer-before-merge-guard and migration-and-number-guards, recorded in archived task fo-record-checks). The first design, its count and its PRFAQ are kept verbatim under amendment 2 as history.

### Chain check (read 2026-10-15)

- **Spacedock** 0.27.2: `spacedock dispatch build --help` and `spacedock gate prepare --help` list no code-commit or head field; FO writes the dispatch record itself, and nothing in Spacedock reads a validation head. Nothing to reuse.
- **kc-dev-flow-2** at origin/main `c545b896`: `scripts/dispatch_records.py` requires a `Dispatched:` line with a 40-character SHA, but `references/sd/workflow.md` defines that SHA as "the SHA it dispatches from", and the count below shows it is the workflow or state checkout in 68 of 104 validation records, so it cannot carry the candidate. `Applied: none as of <candidate sha>` records a candidate only for tasks with a `Migration:` line. `delivery_gate.py` takes its head from the validator's report prose: that is the part to replace.
- **kc-dev-flow** (v1): its references use `spacedock merge guard --verdict`; no head record to borrow.
- **Sibling adopters**: relay writes the PR head as the `Dispatched:` SHA, qnow writes `; candidate <40-hex>` on that line, this workflow writes `candidate #<N> <8-hex>`; none has a parser. The count shows what FO already writes; it is not a contract. ADR 0014 D2 (strict equality, hold on a head that differs) and ADR 0015 (the Draft PR exists before validation) are untouched; `git -C <state> grep -n 'Override:'` finds no gate ruling on this question.

### Existing-code capability check

Boundary: `delivery_gate.py check` deciding which head was validated. It works for one form of validator prose and holds on every other. The observation that justifies the change: #647 spent five commits and three Codex P1s of one class (the parser counted prose that was not the stated verdict line) and still read prose; the relay hold (`387b7863`) was one character of spelling. The change repairs the existing script by moving its source from the validator's report to the record FO writes at dispatch; same command, arguments, exits, `next:` lines and second-reviewer code. It adds one `Candidate:` line to a record FO already writes.

### What FO already writes in validation dispatch records (count, read only, 2026-10-15)

Method: every `dispatch/validation*.md` under `~/conductor/repos` and `~/conductor/workspaces` in a state checkout of this workflow, relay, qnow and ss-web (subspace-web), one copy per (repository, task, file name), the largest copy kept: 104 records in 37 tasks (this workflow 44 in 13, qnow 32 in 8, relay 26 in 15, ss-web 2 in 1). "Header" is the text above the first `## ` heading. The scripts are machine-local (`/tmp/gate-redo/count_records.py`, `final.py`, `match.py`) and are not committed; the classification is a heuristic, so read the counts as within a few records.

| Shape of the head in the record header | Records | Where |
| --- | --- | --- |
| one `candidate [#N] <sha>` label (36 short SHAs, 32 full) | 68 | qnow 32, this workflow 35, ss-web 1 |
| no label, one hex token, on the `Dispatched:` line (all full) | 32 | relay 22, this workflow 9, ss-web 1 |
| several hex tokens and no label (a task validating two repositories) | 4 | relay `spacedock-install-beta` |
| records naming exactly one head | 100 of 104 | |

- A `Candidate:` line already exists in 6 records, each followed by free text (the 4 above, one in ss-web, one here); 0 of 104 carry the whole-line form `Candidate: <40-hex>`, so the check would read none of them today.
- The `Dispatched:` SHA names the workflow or state checkout in 68 of 104 records (qnow 32, this workflow 36) and is the PR head in 22 of relay's 26. One line cannot mean both, so the candidate gets its own line.
- 25 of the 37 tasks have more than one validation record, and 22 of those name more than one head across records (repair cycles): the latest record is the one that matters.
- Of 71 records that name one head and pair 1:1 with a validation report in the task file, 70 reports mention that head anywhere; the one that does not is a record whose only hex token is a workflow checkout (my rule misread it, not a validator miss). No validator that checked another head than the dispatched one is observed; the test is crude (a mention anywhere).

### PRFAQ

**Press release.** The merge ask no longer depends on how a validator spells its verdict. When FO dispatches validation it writes one line in the dispatch record, `Candidate: <40-hex head>`, for each head it asks to be validated. Before it asks the Captain to merge, `delivery_gate.py check` compares the PR head with the heads in FO's latest validation record: equal, FO may ask; different, FO revalidates the new head or tells the Captain the difference; no such line, the ask holds and the output names the form. The check reads no report. Whether the validation said PASSED or REJECTED stays FO's reading at the gate.

**FAQ.**
- *Why not keep reading the report?* Five commits on #647 added exclusions (anchors, fences, qualified labels, section order) and the third Codex P1 of one class still found prose the parser counted. The Captain's amendment 2 asks the check to stop there; the head FO dispatched is a fact FO writes, not prose it parses.
- *What does exit 0 prove now?* That FO dispatched validation on this head, not that it passed. That was never provable by a script reading prose either (a `Verdict PASSED` quoted inside a REJECTED report passed base).
- *Why its own line, not the `Dispatched:` SHA?* The count above: that SHA is the workflow checkout in 68 of 104 records.
- *Why not make `dispatch_records.py` check the line?* The check has one owner already: `delivery_gate.py` fails closed and prints the form. A folder-wide PART would fail every earlier record of an in-flight task, and a latest-record-only PART would repeat the selection logic in a second script. What breaks without it: a missing or malformed line is found at the merge ask, not during validation, by exit 2 and one new dispatch; no instance of a malformed line exists yet to justify the second owner.
- *Why not make the validator write anything?* The validator's report is not read, so `skills/validation/principles.md` stays as at base.
- *What about adopters?* A package release (`fix(kc-dev-flow-2): ...`); `workflow.md` changes, so each adopter's README takes the next sync. Until it does, that adopter's FO does not know the line, and the exit 2 hold line prints the form; one revalidation dispatch is the cost for a task in flight at the upgrade.

```mermaid
sequenceDiagram
  participant FO as First Officer
  participant R as validation record (dispatch/validation-N.md)
  participant V as validator
  participant G as delivery_gate.py check
  participant C as Captain
  FO->>R: write Dispatched, Model, Candidate lines (one per head) and sections
  FO->>V: dispatch validation
  V-->>FO: Stage Report (read by FO, not by the check)
  FO->>FO: judge PASSED or REJECTED, as before
  alt REJECTED, or a repair
    FO->>R: new record validation-N+1 with its own Candidate line, then revalidate
  else PASSED
    FO->>G: check task --pr owner/repo#N --text-file question
    G->>R: read the highest-numbered validation record, header only
    alt no valid Candidate line
      G-->>FO: exit 2, prints the form; hold the ask
    else PR head differs from every Candidate
      G-->>FO: exit 1, prints both; revalidate or tell the Captain
    else PR head equals a Candidate (and second reviewer outcomes stated)
      G-->>FO: exit 0
      FO->>C: ask for merge with this text
    end
  end
```

### Edge cases, judged and not solved by adding rules

- **A validator that checked a head other than the one dispatched.** The check reads only the record, so it cannot see this. FO reads the report at the validation gate, and the validation principles already owe "artifact identity" in it; comparing that with the dispatched head is part of that reading. Not observed in the count (above). No rule added.
- **Several validation dispatches.** The highest-numbered record decides, numerically (`validation-10` over `validation-2`); an older head that equals the PR head does not rescue a newer record that names another (AC-11). Observed shape: 22 of 37 tasks.
- **A head moved by a trunk merge after validation.** Exit 1, as ADR 0014 D2 and the Captain's fo-record-checks ruling of 2026-10-13 (hold on any head difference) already say; FO revalidates (a new record) or tells the Captain. observer-before-merge-guard is this case (`40c714a6` to `7679ab7a`, AC-9). No ancestry rule: one revalidation per trunk merge is the stated cost.

### Replay of the two bite cases (archived task fo-record-checks)

| Task, PR | Head at the merge ask | Records as written | With the `Candidate:` line FO would now write |
| --- | --- | --- | --- |
| observer-before-merge-guard, #632 | `7679ab7a` | no line: exit 2 (hold) | latest record names `40c714a6`: exit 1 (differs), the bite caught; exit 0 at `40c714a6` |
| migration-and-number-guards | `83cad4f7` | no `dispatch/` folder (records were not saved then): exit 2 (hold) | not replayable: no record exists; the old check gave exit 1 from report text (candidate `aff49ab3`), the new one fails closed |

Prototype 2026-10-15, `--head` given, no `gh` call.

### Disposition of what PR #647 carries (read only; its head is `0a26ca37`)

| Carried by #647 | Disposition | What breaks without it |
| --- | --- | --- |
| `delivery_gate.py`: `VERDICT`, `LINE_START`, `SENTENCE_END`, `CANDIDATE` window, `first_verdict`, `*` stripping, the four-spelling docstring (the diff touches nothing else in that file) | remove | nothing: no reader of validator prose remains; three P1s of one class came from it |
| `test_delivery_gate.py` additions for those forms (124 lines added) | remove with the parser; the existing second-reviewer, `gh` and exit-line tests keep their logic; their fixture gains a record folder and a few message assertions (`no passing validation report`, `validated candidate`) follow the new wording (they fail on a prototype today because the fixture has no `dispatch/` folder, not because those checks broke) | the parser has no tests to keep; the kept tests still pin the checks that stay |
| `skills/validation/principles.md` verdict sentence | remove (file back to its 617 words at base) | the sentence says a report without the line "holds the merge ask", which would be false |
| `test_sd_dispatch.py` entry `validation-states-the-verdict-line` | remove with the sentence | it pins the removed sentence |

Continue on the #647 branch: first commit restores those four files to `origin/main`, then the change below on top; the PR stays the task's PR, the squash commit is clean, and review rounds keep one history. What gets worse: the PR carries five commits and Codex threads about code that no longer exists. A new branch gives a clean diff but means closing #647, which is the Captain's call, and re-pointing `pr:`.

### Words FO reads at each lifecycle moment (counted with `len(text.split())`, prototype 2026-10-15)

| Moment | Base | Candidate |
| --- | --- | --- |
| Startup; idle on an open PR; idle on a merged PR; after the archive | the mod, the `pr-merge` hooks, `pr_watch.py` output and the `learn` step | byte-identical: none of these files is edited (AC-13) |
| Validation dispatch (FO writes the record; not one of the five moments) | dispatch-record passage 64 words | 75: names `Candidate: <full head SHA>` per head validated |
| The merge ask, exit 0 | head passage 84 + gate output 20 | 83 + 20 |
| The merge ask, exit 1 | head passage 84 + gate output 27 | 83 + 25 |
| The merge ask, exit 2 (failing path) | gate output 20 | 30: it prints the form |

The workflow budget is 5511; the prototype's `workflow.md` is 5521 and fails. Payment, to settle in implementation under the lint's own rule: drop the 26-word sentence "A PR delivers only the commit on its head; a repair validated after the PR was opened reaches it only when that exact commit is pushed." (5495 words, passes). The head check now enforces what it says, and no `need` string pins it. It is existing content, so the implementation lists it under `without-it unanswered` for the Captain; the alternative is raising `WORKFLOW_WORD_BUDGET` by the words added, with the reason in `lint-skills.py`.

### Change, in files

Expected to change: `kc-dev-flow-2/scripts/delivery_gate.py` (about 20 lines: `CANDIDATE` and `RECORD` patterns, `dispatched_candidates(task)`, the hold, differs and equals lines, the docstring), `kc-dev-flow-2/scripts/test_delivery_gate.py` (AC-9 to AC-12, fixture with a record folder), `kc-dev-flow-2/references/sd/workflow.md` (the `Candidate:` clause in the dispatch-record passage; the merge-ask passage names the record), `kc-dev-flow-2/scripts/test_sd_dispatch.py` (the `dispatch-record` and `readme-keeps-delivery-rules` pins follow the new wording). Back to base: `skills/validation/principles.md`. Not changed: `dispatch_records.py`, the mod, `pr_watch.py`, `lint-skills.py` (unless the budget route is taken). Prototype: `/tmp/gate-redo/proto/kc-dev-flow-2` (machine-local); pr-watch-state-per-session names `scripts/pr_watch.py`, `test_pr_watch.py` and `lint-skills.py` word budgets as its reachable files, and this change names `lint-skills.py` only on the budget route.

### Limits

- The check proves FO dispatched validation on this head, not that validation passed or finished; a REJECTED validation at that head still passes it (AC-12). The head FO writes is FO's own statement; a line written after the fact is not detected (ADR 0014 has the same prose-enforced limit).
- The count measures how FO wrote records before any rule; it says nothing about the rate at which FO writes the new line. The hold makes a missing line visible at the ask; the rate is read on the first adopter validation after release.
- A bare line names no PR, so a head equal to any listed line passes for any `--pr` (D1).
- A task in flight at the upgrade, or an adopter whose README is not yet re-synced, holds once (exit 2) and needs one revalidation dispatch.
- Non-goals: reading validator prose; accepting a head from any source other than a `Candidate:` line; ancestry checks for trunk merges; a `dispatch_records.py` PART; any change to `skills/validation`; any adopter file.

### Unresolved decisions for the Captain

- **D1: the line is `Candidate: <40-hex head>`, one per head validated (recommended), or `Candidate: <owner/repo>#<N> <40-hex head>`?** Bare: it can be written before a PR exists (ss-web `holder-panel-header-and-polish` was validated on an unpushed head), and a task over several repositories lists several lines (relay `spacedock-install-beta`, 4 records). What gets worse: the check cannot tell which PR a line was meant for, so a head equal to any listed line passes for any `--pr`; two repositories sharing one 40-hex SHA is not a case I can construct. PR-qualified: each line names its PR and the check matches it to `--pr`; what gets worse: it cannot be written before a PR exists, every line and the workflow sentence grow, and FO must keep the PR id right in each record.


