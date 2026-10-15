---
title: delivery_gate.py accepts only "Verdict PASSED", a form no instruction asks validators to write
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:delivery-gate-verdict-form:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-gate-verdict-form-backlog-1
              briefing:
                id: briefing:delivery-gate-verdict-form:backlog:attempt-1:revision-1
                digest: sha256:6a3895b16481341591719201ccf2b3b09407a1c5768747f3a34d2021f08f4a53
                room-ref: ./delivery-gate-verdict-form/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-verdict-form:backlog:1
                briefing: briefing:delivery-gate-verdict-form:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-15T00:24:46.8908Z"
                decision: approve
                reason: 'Captain approved both backlog gates (「准」): schedule as Pilot and enter ideation before the next kc-dev-flow-2 release and adopter sync.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:delivery-gate-verdict-form:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:delivery-gate-verdict-form-ideation-1
              briefing:
                id: briefing:delivery-gate-verdict-form:ideation:attempt-1:revision-1
                digest: sha256:4bd1dbb7aa22ae25d1554b7414c1930a49990aa0bbeb65cda6fe6c2134db990a
                room-ref: ./delivery-gate-verdict-form/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-verdict-form:ideation:1
                briefing: briefing:delivery-gate-verdict-form:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-15T00:41:44.818312Z"
                decision: approve
                reason: 'Captain approved (「准」) after FO presented both open ideation gates and asked him to rule on both: accepts D1 (one verdict line in the validation skill plus three Verdict spellings in the check) and D2 (no bare PASSED) as the gate question states.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-15T00:25:17Z
worktree: .worktrees/spacedock-ensign-delivery-gate-verdict-form
pr: iamcxa/kc-claude-plugins#647
---

Filed on the Captain's 「開」 (2026-10-14), from a package issue the spacedock-dev/subspace-relay FO reported: on relay task `owner-sees-all-feedback-page` (PR spacedock-dev/subspace-relay#368) the validator wrote `Verdict: PASSED, recommended. Artifact: candidate 985200258…`, and `delivery_gate.py check` exited 2 ("no passing validation report … names a candidate SHA"); the relay FO sent the validator back for a one-line report repair (relay state commits 387b786 and 940921b). On this workflow's task `fo-lifecycle-mod` a validator also wrote a "Verdict recommended: PASSED" form.

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


## Captain amendments

### Amendment 1 — 2026-10-15, chat
Captain: 「都按建議核准」 (chat, 2026-10-15)
Asked: 「#647 的 AC-4 要照哪種讀法？我建議最新一次的驗證結論為準。也就是說，同一個版本先通過、後來重驗否決時，檢查要擋下來。代價是要刻意反轉 main 上一個鎖住舊行為的測試。」
Supersedes: AC-4
Design: none
Superseded text:

    **AC-4** A REJECTED or not-passing report holds, including one that quotes an earlier PASSED.
    Verified by: tests exiting 2 for: `Verdict REJECTED at S1: one Material finding.`; the same line followed by `Cycle 1 read Verdict PASSED at S2.` with `--head S2`; a section with no verdict word; and, over several sections, a latest section that is REJECTED above an older PASSED one (the latest section that has a candidate still wins, as in base `test_the_latest_passing_report_names_the_candidate`). Base defect observed 2026-10-15: the second case exits 0 on base (`PR head 2222222b equals validated candidate 2222222b`), so base asks for merge on a REJECTED report. Over the 57 REJECTED sections in the count, base and candidate both accept 0.
    Falsifier: search the whole section for a PASSED line instead of deciding by the first `Verdict` form; the quoting case exits 0 and the test fails.

Replaced by AC-8.

### Amendment 2 — 2026-10-15, chat
Captain: 「好」 (chat, 2026-10-15)
Asked: 「要不要把 #647 退回構想階段，改成「比對 FO 派驗收時記錄的版本」這個方向？」
Supersedes: AC-1, AC-2, AC-3, AC-5, AC-6, AC-7, AC-8
Design: the whole `## Design` is redone at ideation. The bite is unchanged (FO asked the Captain to merge a PR head that no validation had checked: observer-before-merge-guard and migration-and-number-guards, recorded in archived task fo-record-checks). The check stops reading the validator's prose for a verdict: `delivery_gate.py` compares the PR head with the head FO named in its latest validation dispatch record, a line whose form FO writes and `dispatch_records.py` can check. Reading PASSED or REJECTED stays FO's judgement at the gate.
Superseded text:

    `<package>` is the kc-dev-flow-2 package root; paths are relative to `kc-dev-flow-2/` in `iamcxa/kc-claude-plugins`. Base is origin/main `c545b896` (package 0.22.1, #643 merged); every base observation below was made on it on 2026-10-15. New tests go in `scripts/test_delivery_gate.py`, which CI already runs (`.github/workflows/kc-dev-flow-2-tests.yml`, step `test_delivery_gate.py`). "Section" is one `## Stage Report: validation` section; `S` is a 7 to 40 character hexadecimal SHA containing a digit.

    **AC-1** The relay report that held now passes at the same head.
    Verified by: a new test whose validation section carries the verdict line shape of relay task `owner-sees-all-feedback-page` as committed in `387b7863` (`Verdict: PASSED, recommended. Artifact: candidate <40 hex> (branch ..., base <7 hex>), unmodified`) and `--head` equal to that SHA exits 0 and prints `equals validated candidate`; the repaired shape of `940921b0` (`Verdict PASSED, recommended. Artifact: candidate ...`) exits 0 too. Replay on the real files: `git -C /Users/kent/conductor/repos/subspace-relay show 387b7863:owner-sees-all-feedback-page.md > /tmp/r.md` then `python3 <package>/scripts/delivery_gate.py check /tmp/r.md --pr o/r#1 --text-file <any file> --head 985200258eebc7aad832716fa8e4b8b57518921f`: base exits 2 with `no passing validation report ... names a candidate SHA` (observed), candidate exits 0 (observed on a prototype, see Design).
    Falsifier: restore `Verdict PASSED[\s\S]{0,160}?` as the pattern; the `387b7863` case exits 2 and the test fails. Limit: the committed test holds the line shape with synthetic SHAs; the relay repository is read only on this machine.

    **AC-2** Every accepted form is accepted, each with its own test line.
    Verified by: a table-driven test, one subTest per line, each in a validation section and each exiting 0 against the SHA it names: `Verdict PASSED at S (base S2)`; `Verdict: PASSED, recommended. Artifact: candidate S`; `Verdict recommended: PASSED. No Material finding. Candidate S`; `Verdict recommendation: PASSED, with one finding. Candidate S`; `Verdict: recommend PASSED. Candidate S`; `**Verdict: PASSED.** Candidate HEAD S`. In the count (Design) the family covers 92 of 267 PASSED sections where base covers 34.
    Falsifier: the base pattern accepts only the first line; the other five subTests fail on it.

    **AC-3** Forms outside the accepted family still hold, each with its own test line, so the check never guesses a verdict from a bare word.
    Verified by: subTests, each exiting 2 with `names a candidate SHA`: `PASSED. HEAD S, merge-base S2`; `Recommend PASSED. Candidate S`; `Independent verdict: PASSED. Candidate S` (lower-case `verdict`); `Verdict PASSED` followed by 161 characters then `S`; `Verdict PASSED with one finding` (no SHA); `Verdict PASSED or REJECTED naming head S` (a template line that names both outcomes is no verdict; the same line is a positive case in base `test_the_candidate_is_the_sha_after_the_verdict_within_160_characters`, so this test line changes deliberately and the change is named in the commit message). Observed on the prototype 2026-10-15: bare `PASSED.`, `Recommend PASSED.` exit 2.
    Falsifier: add a line-start `PASSED` alternative to the pattern; the first two subTests fail. Limit: these are the leading forms of 132 of the 267 PASSED sections counted; they hold until the validator writes the contract line (AC-6).

    **AC-8** Amended by Captain, amendment 1: the newest validation section decides, even when it carries no counting Verdict form, and a latest REJECTED holds even when an older section PASSED.
    Verified by: tests exiting 2 for `Verdict REJECTED at S1: one Material finding.`; that line followed by `Cycle 1 read Verdict PASSED at S2.` with `--head S2`; a section with no verdict word and no older section; a section carrying `Verdict PASSED at S` then a later `## Stage Report: validation (cycle 2)` section carrying `Verdict REJECTED at S` with `--head S` (the same head), exit 2; and several sections with a latest REJECTED above an older PASSED, exit 2. A newest section with no counting form holds even when an older section passed the head; a latest PASSED names its own SHA. Base test `test_the_latest_passing_report_names_the_candidate` pins an older candidate under a later REJECTED section and flips deliberately; the commit message names the change.
    Falsifier: restore the fall-through (a REJECTED section returns no decision and the walk continues to older sections); the later-REJECTED cases exit 0 or 1 and the tests fail; the same holds for a newest section with no counting form (Cycle 2 P1, 0a26ca37).

    **AC-5** FO reads no more words at any lifecycle moment than on base.
    Verified by: at validation, the word counts per moment as in the learning "Measure the words FO reads at each moment": startup, idle on an open PR, idle on a merged PR, after the archive and the merge ask each take the same passages and script output at base and candidate. Candidate changes no file FO reads: `python3 <package>/scripts/lint-skills.py` prints `references/sd/workflow.md: 5511 of 5511 words` (observed on the prototype), the mod and the adopted README are untouched, and `delivery_gate.py check` prints byte-identical output on base and candidate for the three base test reports that carry no new form (exit 0, 1 and 2 cases of `test_each_exit_ends_with_the_next_line_for_the_ask`, which passes unmodified).
    Falsifier: put the line in `references/sd/workflow.md`; lint-skills.py reports a word count above 5511 and the byte comparison of FO's reading fails. Limit: counts text and script output, not a measured FO session.

    **AC-6** The validation contract states the one line, where the validator reads it and no other reader does.
    Verified by: `skills/validation/principles.md` carries one sentence naming `Verdict PASSED at <sha>` and `Verdict REJECTED at <sha>` (prototype: 617 to 657 words in that file, 5511 words unchanged in workflow.md); a new entry in `scripts/test_sd_dispatch.py` for it, in the form of the existing `dispatch-records-check` entry (`need` string plus a `swaps` mutation that deletes the sentence and makes the test fail); `lint-skills.py` and `test_lint_skills.py` exit 0 (observed on the prototype 2026-10-15). `grep -c 'Verdict PASSED' references/sd/workflow.md` prints 0 at base and at candidate.
    Falsifier: delete the sentence; the `swaps` mutation in the new entry fails.

    **AC-7** A validator that has only the contract writes the line, and the check accepts it. Not yet verified.
    Verified by (at validation, once): a fresh worker is given only the candidate `skills/validation/principles.md` and a finished fixture task (candidate commit `S`, one passing and one failing check) and asked for its `## Stage Report: validation`; `delivery_gate.py check` exits 0 on its report with `--head S`. The same prompt with base `principles.md` is the control, and its verdict line form is recorded.
    Falsifier: the worker writes a form the check holds (exit 2); then the wording of the sentence is repaired and AC-7 is rerun. Limit: one worker and one control is a sample, not a rate; the rate is observed on the first adopter validation after release.

Replaced by AC-9 to AC-14.

Superseded design (the whole first `## Design`, kept as history; the current `## Design` replaces it):

    ### Chain check (read 2026-10-15)

    - **Spacedock** 0.27.2: the stage report has no verdict field. `spacedock status --help` lists `verdict` only as the task frontmatter value `merge guard <slug> --verdict passed|rejected` writes, which FO passes in; nothing parses a validator's report for a candidate. Nothing to reuse.
    - **kc-dev-flow-2** at origin/main `c545b896`: the only parser is `PASSED` in `scripts/delivery_gate.py` (`git grep -n 'Verdict PASSED' origin/main`: that script, its docstring and its test, nothing in `skills/`, `references/` or the mod). `references/sd/workflow.md` says validators "recommend `PASSED` or `REJECTED`" and `skills/validation/principles.md` says "Report verdict, artifact identity, evidence and material limits"; neither gives a line shape. So the checker's form is a rule no one told validators.
    - **kc-dev-flow** (v1): its references use `spacedock merge guard --verdict`; no report-verdict parser to borrow.
    - **Sibling adopters**: relay, qnow and ss-web validators wrote their own forms (count below); none carries a parser. ADR 0014 D2 (strict equality, hold on a head that differs) is untouched: the head comparison stays as is. `git -C <state> grep -n 'Override:'` finds no gate override on this question.

    ### Existing-code capability check

    Boundary: `delivery_gate.py check` reading the validation report. It works for the one form it names (completeness: working code, no consumer for a contract line because none exists). The observation that justifies a change: relay#368's validator held at exit 2 and relay's FO sent it back for a one-line repair (`387b7863` to `940921b0`, one character: `Verdict:` became `Verdict`); the count below shows that form is the common case, not the exception. The change repairs the existing script and adds the missing contract sentence; it adds no new mechanism.

    ### What the validators wrote (count, read only, 2026-10-15)

    Method: every file under `~/conductor/repos` and `~/conductor/workspaces` that has a `## Stage Report: validation` heading and `variant: kc-dev-flow-2` in its frontmatter, one copy per (repository, task file name), the largest copy kept (a state checkout appears under several worktrees). That is 141 tasks (relay 52, qnow 46, this workflow 35, subspace-v0 5, subspace-web 3) and 353 distinct validation sections, 267 of them whose first verdict-bearing line says PASSED. The scripts are machine-local (`/tmp/count3.py`, `/tmp/eval3.py`) and are not committed: the committed test carries one fixture line per form instead. Classification is by the first line of a section holding PASSED or REJECTED that is not a diff reference or the checklist echo; it is approximate (29 sections hold neither word, and one section, relay `remote-comment-include`, has `Verdict PASSED <sha>` but no decision by this rule), so read the counts as within a few sections. `delivery_gate.py` landed 2026-10-13 (#640): these counts measure how validators write when nothing tells them, not how many deliveries were held. One held delivery is known (relay#368).

    ```mermaid
    flowchart TD
      R[validation section in the task file] --> V{first 'Verdict' form: PASSED or REJECTED, optional ':' or 'recommended'}
      V -->|none, or REJECTED, or 'PASSED or REJECTED'| H2[exit 2: no passing report names a candidate SHA]
      V -->|PASSED| W{a SHA within 160 characters after it}
      W -->|no| H2
      W -->|yes| C{equals the PR head, prefix compared}
      C -->|no| H1[exit 1: head differs, revalidate or tell the Captain]
      C -->|yes| OK[exit 0: ask for merge]
      H2 --> LAT[the check tries the next older validation section]
    ```

    | Form of the first verdict line in the 267 PASSED sections | Sections | Base accepts | Candidate accepts |
    | --- | --- | --- | --- |
    | bare `PASSED.` or `PASSED at S` (no word `Verdict`) | 90 | 1 | 12 |
    | `Recommend PASSED` / `Recommendation: PASSED` | 55 | 0 | 1 |
    | `Verdict: PASSED` (and `Independent verdict: PASSED`) | 49 | 0 | 36 |
    | `Verdict PASSED` | 42 | 33 | 33 |
    | `Verdict recommended: PASSED` / `Verdict recommendation:` / `Verdict: recommend` | 22 | 0 | 9 |
    | other | 9 | 0 | 1 |
    | all 267 | 267 | 34 | 92 |

    A section in the first two rows is accepted only when a `Verdict` line with a SHA in range appears later in it. The `Verdict` rows are not accepted in full because the SHA sits beyond 160 characters or is absent (the lower-case `Independent verdict:` spelling is also held).

    Per task (126 tasks with a PASSED section): the check finds a candidate on 17 at base and 50 at the candidate. Of the 57 REJECTED sections, base and candidate both accept none. The candidate still holds 175 PASSED sections: 132 whose first verdict line is a bare `PASSED` or `Recommend PASSED`, and 43 in the other rows.

    ### PRFAQ

    **Press release.** The merge ask no longer depends on how a validator happens to spell its verdict. The validation skill now states one line, `Verdict PASSED at <sha>` or `Verdict REJECTED at <sha>`, and `delivery_gate.py check` reads that line, plus the three near spellings validators have already written (`Verdict: PASSED`, `Verdict recommended: PASSED`, `Verdict: recommend PASSED`). A report that says REJECTED, or that quotes an earlier PASSED after saying REJECTED, holds the ask.

    **FAQ.**
    - *Why both a contract line and a wider check?* The contract line carries the weight: 132 of 267 PASSED sections lead with a bare `PASSED` or `Recommend PASSED`, and 43 more place the SHA beyond 160 characters or omit it, so no spelling tolerance reaches them. The wider check covers validators that read an older package, and the three spellings the two reported holds used. Without the check, the next `Verdict: PASSED` holds a delivery until the validator is sent back; without the contract, 175 of 267 (65%) stay held.
    - *Why not accept a bare `PASSED.`?* Recheck reports quote earlier verdicts (`against PASSED <sha>`, `PASSED baseline`), so a line-start `PASSED` would accept a SHA that is not the candidate. Base already has this fault on the `Verdict PASSED` spelling: a REJECTED report that quotes an earlier `Verdict PASSED at S2` is accepted today (AC-4). The first `Verdict` form decides.
    - *Why keep the 160-character window?* `SHA` accepts any 7 to 40 hex run with a digit (`20261015` is one), so a wider window raises the chance of picking a date or a base. The contract puts the SHA on the verdict line instead.
    - *Why is `Verdict PASSED or REJECTED naming head S` now a hold?* A line naming both outcomes is a template, not a verdict. Base test `test_the_candidate_is_the_sha_after_the_verdict_within_160_characters` pins it as accepted; it changes on purpose (AC-3).
    - *Where does the sentence live?* `skills/validation/principles.md`, which the validator reads and FO does not. FO's `workflow.md`, the mod and the gate's output carry no new word, so no lifecycle moment reads more than at base (AC-5, learning "Measure the words FO reads at each moment"). The workflow word budget stays 5511. The validator also gets the stage definition `show-stage-def` prints, which is `workflow.md`'s `validation` section and is unchanged; the sentence reaches it through the skill, whose `SKILL.md` links `principles.md`.
    - *What reaches adopters?* A package release (`fix(kc-dev-flow-2): ...`); the sentence and the check are package-internal, so there is no adopter file to sync. Adopters whose validators run an older package keep writing their own forms until their pin moves.

    ### Change, in files

    Expected to change: `kc-dev-flow-2/scripts/delivery_gate.py` (the `PASSED` pattern becomes a `VERDICT` pattern plus a `CANDIDATE` window; asterisks are removed from the section before matching; the first verdict form decides; the docstring names the accepted family and the contract line), `kc-dev-flow-2/scripts/test_delivery_gate.py` (AC-1 to AC-4), `kc-dev-flow-2/skills/validation/principles.md` (one sentence, about 40 words), `kc-dev-flow-2/scripts/test_sd_dispatch.py` (one entry for it). Not changed: `references/sd/workflow.md`, the mod, `scripts/lint-skills.py` budgets. Prototype of exactly this on a temporary copy of origin/main (not a repository file): `test_lint_skills.py` and `lint-skills.py` pass; `test_delivery_gate.py` passes except the deliberate case above. `pr-watch-state-per-session` expects `pr_watch.py` and `test_pr_watch.py`; I name no file both change (its design names `scripts/lint-skills.py` word budgets as the only spot both could reach; this change adds no FO-read text).

    ### Limits

    - Counts come from validation reports written before the contract; they say nothing about the rate at which a validator follows the new sentence (AC-7 samples it once; the rate is read on the first adopter validation after release).
    - The check still reads one SHA near the first `Verdict` form; two verdict forms in one section (one REJECTED then PASSED, or the reverse) are decided by the first.
    - The hold line (`no passing validation report ... names a candidate SHA`) is unchanged: a REJECTED report and a report in an unaccepted form print the same line. A line telling FO which one it is would add FO-read words at the failing merge-ask moment (9 words measured on a draft: 10 to 19 on that line); it is left out until a hold shows FO misreading it.
    - Non-goals: accepting bare `PASSED.` or `Recommend PASSED`; widening the 160-character window; making `lint-skills.py` or a hook parse validation reports; changing how `merge guard --verdict` is passed; any adopter file.

    ### Unresolved decisions for the Captain

    - **D1: contract line plus a wider check (recommended), or the contract line only?** The two answers are coupled with D2, so they go together. Both: the wider check also saves deliveries whose validators run an older package, and covers the two forms that held relay and this workflow. What gets worse: two spellings of the verdict are accepted, so a future validator who writes a third spelling (`Verdict on candidate S: PASSED`) is held until the contract reaches it, and the accepted family has to be kept in the docstring. Contract only: one spelling, no regex growth; what gets worse: the next older-package `Verdict: PASSED` holds a delivery as relay#368 did, and the check finds a candidate for 17 of 126 tasks' history, against 50 with the wider check, until validators adopt the sentence.
    - **D2: the check accepts only spellings that contain the word `Verdict` (recommended), or also a bare line-start `PASSED` and `Recommend PASSED`?** Only `Verdict`: no wrong SHA is taken from a quoted earlier verdict. What gets worse: the 132 PASSED sections that lead with a bare `PASSED` or `Recommend PASSED` (49%) stay held until the contract reaches their validators, and each hold costs one validator round trip, as at relay (`387b7863` then `940921b0`). Accepting them: fewer holds now; what gets worse: a recheck report quoting `PASSED <old sha>` could name the old SHA as the candidate and the head comparison (exit 1) becomes the only guard.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

### Feedback Cycles

- Cycle 1 (FO, 2026-10-15): Codex review round 1 on #647 57d58532 (review:5526632675) left one P1, to fix (a P1 blocks in every round); investigation first, then FO fix authorization, then a fresh validation recheck. The validation of 57d58532 dispatched before this finding continues; its judgement of the AC-4 conflict joins the same repair.
  - P1 #647 `scripts/delivery_gate.py` (around line 26): the unanchored `\bVerdict` match accepts a qualified label such as `Independent Verdict: PASSED` or `Prior Verdict: PASSED` as the section's verdict, so a quoted or prior verdict before the real rejection can return success; the new test passes only because it uses lowercase `verdict`.
- Cycle 1, validation (FO, 2026-10-15): validation recommended REJECTED at 57d58532 on one Material finding (F1, AC-7): a fresh validator wrote the stated line `Verdict PASSED at <sha>` exactly, but an earlier echoed checklist item `- DONE: Verdict PASSED or REJECTED naming the head` (FO's own checklist wording) is the first form, and a template line decides as a hold, so the report is held where base exits 0 (1 of 3 runs). The validator also showed AC-4's fall-through: a PASSED section then a later REJECTED section on the same head exits 0 on base and candidate. FO takes it to repair rather than defer, because AC-4 states that a latest REJECTED section above an older PASSED one exits 2. All three go to one repair: the Codex P1 anchor (reproduced by the worker), F1 (reproduced by the validator) and AC-4 (reproduced by the validator).
- Cycle 2 (FO, 2026-10-15): Codex review round 2 on #647 43490668 (review:5527985770) left one P1, to fix: a newest validation section with no counting Verdict form is skipped, so an older section that passed the head decides and the gate exits 0, contrary to the validation rule this PR adds (a report without the verdict line holds) and to amendment 1's reading (the latest verdict decides). Investigation first, then FO fix authorization, then a fresh recheck; the recheck of 43490668 dispatched before this finding continues.
  - P1 #647 `scripts/delivery_gate.py` (around line 43): the newest validation section must stop the search even when it has no parseable verdict.
- Cycle 3 (FO, 2026-10-15): Codex review round 3 on #647 0a26ca37 (review:5528048451) left one P1, the third P1 of one class: the parser counts prose that is not the stated verdict line. FO stopped the recheck of 0a26ca37 and holds the repair for a Captain ruling on the approach (circuit breaker: three rounds of added exclusions).
  - P1 #647 `scripts/delivery_gate.py` (around line 49): a fenced evidence line `Verdict: PASSED at <sha>` before the real `Verdict REJECTED at <sha>` counts at line start, so the check exits 0 despite the rejection.

## Stage Report: ideation

- DONE: A design (PRFAQ and Mermaid) for which verdict lines kc-dev-flow-2/scripts/delivery_gate.py accepts on main (after #643): a tolerant pattern, or one exact verdict line stated in the validation stage contract and checked, or both; with a count of the verdict forms that occur in archived validation reports across this workflow and the adopters on this machine (read only), and what the validation skill or stage text must say
  Both: one contract line in skills/validation/principles.md plus a three-spelling check that lets the first Verdict form decide; count in `## Design`: 353 validation sections in 141 tasks (relay, qnow, this workflow, ss-v0, ss-web), the check finds 34 of 267 PASSED sections at base and 92 on a prototype; chain checked (Spacedock, kc-dev-flow-2, kc-dev-flow v1, adopters).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, replaying the relay report that held (Verdict: PASSED) and the forms found in the count, and showing a REJECTED or not-yet-passing report still holds
  AC-1 to AC-7 below; relay `387b7863` exits 2 at base and 0 on the prototype (observed), a REJECTED report quoting an earlier PASSED exits 0 at base and 2 on the prototype (observed).
- DONE: Unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  D1 (contract plus wider check, or contract only) and D2 (accept only spellings with the word Verdict, or also bare PASSED), coupled, in `## Design`; ADR 0014 D2 and the `Override:` lines read, none contradicts.
- DONE: AC-1 relay report that held passes at the same head
  Current evidence: base exit 2 on `387b7863`, prototype exit 0 on `387b7863` and `940921b0`; not yet verified: the committed test (implementation).
- DONE: AC-2 every accepted form is accepted
  Current evidence: six lines run on the prototype, base accepts one; corpus 34 to 92 of 267; not yet verified: the committed subTest table.
- DONE: AC-3 forms outside the family still hold
  Current evidence: nine lines run on the prototype, the bare, Recommend, lower-case, 161-character, no-SHA and `PASSED or REJECTED` cases all print None; not yet verified: the committed table and the deliberate flip of the base test case.
- DONE: AC-4 REJECTED or not-passing report holds, including one quoting an earlier PASSED
  Current evidence: base exits 0 on the quoting case, prototype exits 2; 57 REJECTED corpus sections accepted by neither; not yet verified: the committed tests.
- DONE: AC-5 FO reads no more words at any moment than base
  Current evidence: prototype lint-skills.py prints 5511 of 5511 words, test_lint_skills.py 26 tests OK; not yet verified: the per-moment recount and the byte comparison of gate output (validation).
- DONE: AC-6 the validation contract states the one line where only the validator reads it
  Current evidence: prototype sentence passes lint-skills.py after the `<package>/scripts/` wording fix; not yet verified: the new test_sd_dispatch.py entry and its mutation.
- DONE: AC-7 a validator with only the contract writes the line
  Not yet verified: no fresh-worker run exists; it is planned once with a control at validation, and the rate is only observable after release.
- DONE: design_surfaces.py check
  `python3 <package>/scripts/design_surfaces.py check <task>` printed `delivery-gate-verdict-form.md: design surfaces presentable`, exit 0 (Surfaces: none).

### Summary

The check holds deliveries because nothing tells validators one verdict line: of 267 PASSED sections written unprompted, base finds a candidate in 34. The design states the line in the validation skill (validator-read, no FO-read words) and widens the check by three spellings with a first-verdict-decides rule, which also closes a base defect that accepts a REJECTED report quoting an earlier PASSED. Files expected: delivery_gate.py, test_delivery_gate.py, skills/validation/principles.md, test_sd_dispatch.py; none shared with pr-watch-state-per-session. The corpus scripts are machine-local and the classification is approximate (stated in Design); the prototype lived in /tmp, no repository file was written.

## Stage Report: implementation

- DONE: One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main changing delivery_gate.py, test_delivery_gate.py, skills/validation/principles.md and test_sd_dispatch.py, AC-1 to AC-6 green with each falsifier shown failing by a mutation run
  PR https://github.com/iamcxa/kc-claude-plugins/pull/647 (Draft), head 57d585326 on base c545b896; 4 files only. The worktree branch sat at 656543f4, so I fast-forwarded it to origin/main (0 own commits lost) before editing.
  AC-1 `test_the_relay_report_that_held_passes_at_the_same_head` fails if the base pattern is restored; real replay of relay `387b7863`: base exit 2, candidate exit 0.
  AC-2 `test_every_accepted_verdict_form_names_its_candidate` (8 lines incl. `**Verdict:** PASSED`) fails on the base pattern (5 lines) and with `*` not stripped (bold line).
  AC-3 `test_forms_outside_the_family_name_no_candidate` fails if a line-start `PASSED` alternative, a 400-character window, an accepted template, or newline-spanning `Verdict\n PASSED` is added.
  AC-4 `test_a_rejected_or_verdictless_report_holds_even_when_it_quotes_an_earlier_passed` and `test_two_rejected_sections_...` fail with a whole-section PASSED search.
  AC-5 lint-skills.py prints `references/sd/workflow.md: 5511 of 5511 words`; a line added to workflow.md gives FAIL 5518 > 5511; `test_each_exit_ends_with_the_next_line_for_the_ask` passes unmodified; `grep -c 'Verdict PASSED' references/sd/workflow.md` prints 0.
  AC-6 new `validation-states-the-verdict-line` entry in `test_sd_dispatch.py`; deleting the sentence fails its fixture check; test_lint_skills.py 26 OK.
- DONE: No word added to any FO-read file (workflow.md budget unchanged), roborev evidence= line, CI green on the PR head, CI cost measured or stated as not measured
  workflow.md untouched. roborev: `clean on 57d585326; evidence=roborev:685`. CI on the PR head: 4 checks pass (unit tests 50s, route gate 8s, version parity 40s, GitGuardian). CI cost not measured (job durations only; no new job).
- DONE: AC-7 left to validation
  Not run here, as assigned.
- DONE: comment_ratio.py, doc_impact.py, design_surfaces.py check
  `code lines 75, comment lines 0, 0.0%`, maximum met, exit 0. doc_impact listed `kc-dev-flow-2/README.md` and `references/sd/adoption.md`: both unaffected: they mention only the `test_sd_dispatch.py --sd-plugin-root` invocation, which is unchanged. design_surfaces: `presentable`. No ADR added.

### Summary

delivery_gate.py now reads the four Verdict spellings, ignores `*`, lets the first Verdict form decide and holds a REJECTED first form or one naming both outcomes; the validation skill states the one line. Two findings for FO: (1) the verdict regex uses `[ \t]` not `\s` between `Verdict` and the outcome, because the report format `- DONE: Verdict` then a next-line `PASSED. HEAD S` would otherwise match as a verdict; (2) AC-4 says a latest REJECTED section above an older PASSED one exits 2, but it also says the latest section with a candidate still wins as in base `test_the_latest_passing_report_names_the_candidate`, which keeps the older candidate (exit 0 or 1 by head); I kept the base behavior, tested the REJECTED-quote and two-REJECTED cases for exit 2, and listed the fall-through as a Limit in the PR. Test_sd_dispatch ran against a spacedock 0.27.0 plugin root (the 0.27.2 root CI pins is not on this machine) with the 0.27.2 binary; CI's live run passed.

## Stage Report: validation

- DONE: Independent verdict on #647 head 57d58532 against AC-1 to AC-6, re-running each evidence command and at least one falsifier per criterion yourself (the relay report that held, each accepted Verdict spelling, forms outside the family, a REJECTED or verdictless report quoting an earlier PASSED, the word budget, the pinned sentence), and judging the implementation's two choices: the [ \t] separator, and AC-4's conflict, where the latest section that names a candidate wins, so a later REJECTED section that names none falls through to an older PASSED one; say whether a REJECTED recheck on the same head as an older PASSED can reach exit 0, with a probe
  Verdict REJECTED at 57d585326cdeed2ae6ecd9e85f7439be84c73ecb (PR #647 head, open Draft, equals the dispatched head; base c545b896): AC-1 to AC-6 hold, AC-7 fails once in three runs on one Material finding below. Candidate and base were read from throwaway worktrees (removed).
  AC-1 `test_delivery_gate` 18 OK, `test_lint_skills` 26 OK, `test_sd_dispatch` (spacedock 0.27.2, `--sd-plugin-root` 0.27.0) PASS. Real relay replay: `387b7863` base exit 2, candidate exit 0; `940921b0` exit 0 on both. Mutation (scratch copy): restoring the base pattern fails 5 tests.
  AC-2 and AC-3 own probe of 36 lines on base and candidate: all six accepted spellings plus `Verdict recommended PASSED`, tab or double space, bold, backticks and `> ` quoting pass; lowercase `verdict`, `Independent verdict`, `Verdict - PASSED`, `| Verdict | PASSED |`, `Verdict is PASSED`, a 161-character gap and `PASSED or REJECTED` or `PASSED / REJECTED` hold. A clean mutation that adds a line-start `PASSED` alternative fails exactly the `PASSED.` and `Recommend PASSED.` subTests; window 400, dropped template guard and `\s` each fail their own test.
  AC-4 quoting case: base exit 0, candidate exit 2; whole-section PASSED search mutation fails 2 tests. AC-4 conflict, judged: keeping base behaviour is consistent with the base test `test_the_latest_passing_report_names_the_candidate`, which pins an older candidate under a later REJECTED section, but AC-4's own sentence that a latest REJECTED section above an older PASSED one exits 2 is not met: it exits 1 on a different head. Probe, same head: PASSED at `1111111a`, then a cycle 2 section `REJECTED at 1111111a`, `--head 1111111a` gives exit 0 on base and on candidate (script step 4). Deferred risk, see Findings.
  AC-5 `lint-skills.py` 5511 of 5511; `git diff --stat` over `references/`, README and the mod is empty and `diff -r` of `references/` is identical; `check` output is identical (exit and bytes) on the five cases of `test_each_exit_ends_with_the_next_line_for_the_ask`. AC-6 `grep -c 'Verdict PASSED' references/sd/workflow.md` 0 on both; deleting the sentence in a scratch package fails `test_sd_dispatch` naming `validation-states-the-verdict-line`; principles.md is 651 words (617 at base), the dispatch of this stage does not carry it to FO.
  `[ \t]` judged sound: replacing it with `\s` fails `test_forms_outside_the_family_name_no_candidate` and, on a re-count of 320 distinct validation sections on this machine (base finds a candidate in 34, candidate in 82, 48 gained, 1 lost), would accept 8 more sections that write a `### Verdict` heading followed by `PASSED.` on a new line; those stay held, as at base, and are outside the stated family. The one lost section is the template echo in `worker-completion-goes-to-main`, the deliberate flip. Not run: a measured FO session.
- DONE: AC-7: one fresh validator run on the package text of the candidate, writing a validation report for a small fixture, with its verdict line checked against the stated form, and one control run on the base text
  Fixture `/tmp/dgv-ac7/seed` (base `7bb5a9ed`, candidate `a63645f8`: `add()` plus a passing test, and `test_legacy` failing identically at base, out of scope). Launch, from inside each copy of the fixture: `claude -p "$(cat ../prompt.txt)" --model sonnet --output-format stream-json --verbose --setting-sources project --disable-slash-commands --strict-mcp-config --permission-mode bypassPermissions --no-session-persistence --max-budget-usd 2`; the stream init names `claude-sonnet-5-5`, 5 turns, about 1000 output tokens each; the only principles.md in reach is the candidate's (run `cand`) or base's (run `ctrl`); the user-level CLAUDE.md was not excluded (no API key for `--bare`). Streams and task copies are in `/tmp/dgv-ac7/`.
  Candidate run 1: the stream's Bash write carries `Verdict PASSED at a63645f886f8e208aa6d6ec41aa25534b619807e`, exactly the stated form, but `delivery_gate.py check --head a63645f8` on the candidate script exits 2 (`names a candidate SHA`); base script exit 0. Cause: the worker echoed my checklist item as `- DONE: Verdict PASSED or REJECTED naming the head, ...` (capital V, protocol says copy items verbatim) ahead of the line, and the candidate's first form is that template, which holds. AC-7 as written (exit 0) is therefore not met on this run.
  Same prompt again (`cand3`) exit 0 (the worker echoed it lower case); a checklist shaped like this dispatch's real items (`cand2`, verdict phrase mid-item) exit 0. So 1 of 3 candidate runs held: a sample, not a rate. Control `ctrl` (base principles.md): `Verdict: PASSED for head a63645f (base 7bb5a9e)`; base script exit 2, candidate script exit 0, so the control form is one the new check reads.
  Repair verified in a scratch copy only: decide by the first form that is not a template (`next((v for v in VERDICT.finditer(section) if not v.group(2)), None)` in place of `VERDICT.search`): 18 tests still OK and the run-1 report exits 0; the template-only line still holds.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition
  Script saved as `/tmp/dgv-accept.sh`, run as `env -i HOME=$HOME PATH=/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin bash --noprofile --norc /tmp/dgv-accept.sh`; it needs the colombo checkout (holds both commits), the read-only relay checkout and python3, no spacedock binary. Six steps, observed output:
```bash
A=/tmp/dgv-accept; R=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo
G=kc-dev-flow-2/scripts/delivery_gate.py; H=985200258eebc7aad832716fa8e4b8b57518921f
run() { python3 -B $A/$1/$G check $2 --pr o/r#1 --text-file $A/text.txt --head $3; }

echo "--- 1 setup: base c545b896 and candidate 57d58532 extracted from $R (no spacedock binary used)"
rm -rf $A && mkdir -p $A/base $A/cand && echo gate > $A/text.txt
git -C $R archive c545b896 kc-dev-flow-2 | tar -x -C $A/base && git -C $R archive 57d58532 kc-dev-flow-2 | tar -x -C $A/cand && echo extracted

echo "--- 2 the relay report that held (subspace-relay commit 387b7863), same head"
git -C /Users/kent/conductor/repos/subspace-relay show 387b7863:owner-sees-all-feedback-page.md > $A/relay.md
for v in base cand; do run $v $A/relay.md $H | head -1 | cut -c1-110; echo "$v exit ${PIPESTATUS[0]}"; done

echo "--- 3 verdict forms: exit codes base/cand (head 0830a3be)"
for L in 'Verdict PASSED at 0830a3be' 'Verdict: PASSED, recommended. Candidate 0830a3be' 'Verdict recommended: PASSED. Candidate 0830a3be' 'Verdict: recommend PASSED. Candidate 0830a3be' '**Verdict: PASSED.** Candidate HEAD 0830a3be' 'PASSED. HEAD 0830a3be' 'Recommend PASSED. Candidate 0830a3be'; do
  printf '## Stage Report: validation\n\n- DONE: x\n  %s\n' "$L" > $A/t.md
  for v in base cand; do run $v $A/t.md 0830a3be >/dev/null; printf '%s ' "$v=$?"; done; echo " <- $L"
done

echo "--- 4 REJECTED reports: quoting an earlier PASSED (head 2222222b), then a REJECTED recheck on the same head as an older PASSED (head 1111111a)"
printf '## Stage Report: validation\n\n  Verdict REJECTED at 1111111a: one Material finding.\n  Cycle 1 read Verdict PASSED at 2222222b.\n' > $A/rej.md
for v in base cand; do run $v $A/rej.md 2222222b >/dev/null; printf '%s ' "quoting $v=$?"; done; echo
printf '## Stage Report: validation\n\n  Verdict PASSED at 1111111a\n\n## Stage Report: validation (cycle 2)\n\n  Verdict REJECTED at 1111111a: new Material finding.\n' > $A/rej2.md
for v in base cand; do run $v $A/rej2.md 1111111a >/dev/null; printf '%s ' "same-head-recheck $v=$?"; done; echo

echo "--- 5 a checklist item echoed verbatim ahead of the contract line (head a63645f8)"
printf '## Stage Report: validation\n\n- DONE: Verdict PASSED or REJECTED naming the head\n  Verdict PASSED at a63645f8\n' > $A/echo.md
for v in base cand; do run $v $A/echo.md a63645f8 >/dev/null; printf '%s ' "$v=$?"; done; echo

echo "--- 6 candidate unit suite, and no FO-read file differs from base"
(cd $A/cand/kc-dev-flow-2/scripts && python3 -B -m unittest test_delivery_gate 2>&1 | tail -3)
diff -r $A/base/kc-dev-flow-2/references $A/cand/kc-dev-flow-2/references && echo "references/ identical to base"
```
  Observed: step 2 base exit 2, cand exit 0 (equals validated candidate 985200258eeb...); step 3 `base=0 cand=0` for the first line, `base=2 cand=0` for lines 2 to 5, `base=2 cand=2` for the last two; step 4 `quoting base=0 quoting cand=2` and `same-head-recheck base=0 same-head-recheck cand=0`; step 5 `base=0 cand=2`; step 6 `Ran 18 tests ... OK` and `references/ identical to base`. Steps 4 (second line) and 5 are the two findings: after repair, step 5 should print `base=0 cand=0`.
  `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since c545b896` run in the candidate worktree: "15 ADR file(s) checked, 0 legacy", exit 0 (the candidate adds no ADR).
  `doc_impact.py c545b896 57d58532` exit 0 lists `kc-dev-flow-2/README.md` and `references/sd/adoption.md` (both mention `test_sd_dispatch.py`); the implementation report records each as `unaffected` with a reason, so each carries a disposition. `design_surfaces.py check` on this task: `design surfaces presentable`, exit 0. `number_guards.py` not owed (Surfaces: none, no ADR).
  Findings by Review-finding disposition. F1 Material: a report carrying the stated line `Verdict PASSED at <sha>` is held when an earlier echoed checklist item begins `Verdict PASSED or REJECTED`; fields: workflow = any validator following the protocol's verbatim-item rule on an FO checklist item that starts with the verdict phrase, then the merge ask; harm = exit 2 and a validator round trip, the harm this task exists to remove, base exit 0 on the same report; criterion = value-ac[AC-7] (and AC-2's intent); the design's own PRFAQ calls a line naming both outcomes "a template, not a verdict" and AC-3 holds it alone, yet the code lets that non-verdict be the deciding first form, so the code contradicts the stated design rule; observed trigger is thin (AC-7 run 1 only, and the real dispatch shape in `cand2` passed): trigger = AC-7 run 1 (`/tmp/dgv-ac7/cand/task.md`), and one real corpus section echoes the capital form (`worker-completion-goes-to-main`, held now, accepted at base only through the template line). Repair is the one line above plus a test line for template-then-real; return through feedback. F2 Deferred risk and Needs decision (which reading of AC-4 holds is the Captain's ruling): a REJECTED recheck on the same head as an older PASSED reaches exit 0 (as at base); no observed trigger (4 REJECTED-after-PASSED sections in the corpus, none on the same SHA); becomes Material when a same-head REJECTED is recorded and FO proceeds to the merge ask; AC-4's multi-section sentence contradicts its own parenthesis, which the Captain may want settled. F3 Polish: the principles.md sentence says a report without the line holds the merge ask, while the three near spellings also pass; and 8 real sections written as a `### Verdict` heading stay held.

### Summary

Verdict REJECTED at 57d585326cdeed2ae6ecd9e85f7439be84c73ecb. AC-1 to AC-6 hold with falsifiers shown failing, the word budget and gate output are unchanged, and the `[ \t]` choice is sound; AC-4's fall-through is base behaviour and a Deferred risk. AC-7 is the finding: a worker that wrote the stated line exactly was held once in three runs because the first-form rule meets a verbatim checklist echo; a one-line repair is verified in scratch and awaits the feedback route. Counts here (320 sections, 34 to 82) are an independent re-count and differ from the design's 267 to 92.

## Stage Report: implementation (cycle 3, repair under Captain amendment 1)

- DONE: Recovery first: the previous worker is unreachable; its two unpushed commits 747d0fc9 and 36ffa7a1 sit on the task branch in the existing worktree of PR iamcxa/kc-claude-plugins#647; check git status and git log, and keep them
  Worktree clean at start; 57d58532, 747d0fc9, 36ffa7a1 present and kept; pushed with the new commit, no force.
- DONE: Move AC-4 verbatim under Captain amendment 1 (task file) as Superseded text and write its replacement as a new AC id saying "Amended by Captain, amendment 1" ... commit the state
  AC-4 block now under `Superseded text:` in Amendment 1; replacement is AC-8; `design_surfaces.py check` exit 0 ("design surfaces presentable"); state commit d058fbfe.
- DONE: Build that rule in delivery_gate.py (walk sections from the latest; the first section with a counting form decides), flip the base test, add the same-head case, mutation shown red; re-run the corpus count
  43490668: `validated_candidate` returns the first section's `first_verdict` result (REJECTED holds, PASSED with no SHA holds, no counting form falls through). Flipped `test_the_latest_passing_report_names_the_candidate` and `test_two_rejected_sections_...` (older PASSED under later REJECTED now None / exit 2); added `test_a_later_rejected_section_holds_a_head_an_earlier_section_passed` (PASSED then cycle-2 REJECTED on 2222222b and prefix 2222222, exit 2) plus a verdictless-latest-falls-through and a latest-PASSED-without-SHA-holds case. Mutation (a REJECTED decision continues the walk): 4 tests fail (the three above), restored green.
  Corpus (141 tasks, read only, /tmp/corpus4.py, machine-local): candidate found 43 tasks with and without this commit; 2 tasks change from a candidate to a hold, both a later PASSED section with no SHA over an older PASSED with one (dev2 worker-completion-goes-to-main, cycles 2 and 3 'recheck at'; ss-web holder-panel-header-and-polish, cycle 2). No REJECTED-over-PASSED task appears in the corpus changed set. Per-section results are unchanged.
- DONE: Suite, mutations, the roborev gate, one push of all commits without force, CI green, stage report appended
  test_delivery_gate.py 22 OK; test_lint_skills.py 26 OK; test_sd_dispatch.py OK (local spacedock 0.27.0 root, CI pins 0.27.2); lint-skills 5511 of 5511 words; comment_ratio 0 of 126 code lines; doc_impact 0 documents. Roborev `clean on 434906685; evidence=roborev:688` (no fix rounds used). Pushed 57d58532..43490668; all four CI checks pass at 43490668 (unit tests, version parity, multi-profile route gate, GitGuardian).

### Summary

The latest validation section with a counting Verdict form now decides, so a later REJECTED holds even on the head an earlier section passed, per AC-8. The side effect to know: a latest PASSED section with no SHA in range now holds instead of falling back to an older PASSED SHA (2 of 141 corpus tasks). Not done here: AC-7's fresh-validator run belongs to validation; the PR stays Draft with no comments, ready or merge.

## Stage Report: validation (cycle 2, recheck at 43490668)

- DONE: Independent recheck of #647 head 43490668 against validation cycle 1 at 57d58532: the Codex round-1 P1 (a qualified or quoted Verdict form taken as the verdict), validation F1 (an echoed template line holding a report that carries the stated line) and AC-8 of Captain amendment 1 (the latest section with a counting form decides; a later REJECTED on the same head holds) each reproduced fixed against 57d58532, each new test shown failing under a mutation you run yourself, AC-1 to AC-3, AC-5, AC-6 and AC-8 re-run at the new head with any change named, the window cut at the next Verdict form judged, and the two corpus tasks that change from a candidate to a hold judged
  Read from a throwaway worktree of 43490668 (PR head per `git ls-remote refs/pull/647/head`, equal) and archives of 57d58532 and base c545b896; worktree removed. Suites at the candidate: `test_delivery_gate` 22 OK, `test_lint_skills` 26 OK, `test_sd_dispatch` PASS (spacedock 0.27.0 plugin root).
  P1, F1 and AC-8 reproduced as exit codes base/57d58532/candidate (own probe, script step 3 to 5): `Independent Verdict: PASSED at S` newline `Verdict REJECTED at S2` 2/0/2; `Prior Verdict: PASSED ...` then REJECTED 2/0/2; `Cycle 1 read Verdict PASSED at S` alone 0/0/2; echoed `- DONE: Verdict PASSED or REJECTED naming the head` then `Verdict PASSED at S` 0/2/0, its REJECTED twin 0/2/2; PASSED then a cycle-2 REJECTED on the same head 0/0/2; PASSED then REJECTED at another SHA, head the passed one, 0/0/2; REJECTED then cycle-2 PASSED 0/0/0; latest section with no counting form falls through to the older PASSED 0/0/0; latest `Verdict PASSED with one finding` (no SHA) over an older PASSED 0/0/2; three sections PASSED, REJECTED, REJECTED 0/0/2.
  Mutations, each run by me on a scratch copy with `python3 -B` and caches cleared, test names that fail: no line-start anchor -> `test_a_qualified_or_quoted_verdict_is_not_the_verdict`; template not skipped -> `test_a_template_line_naming_both_outcomes_is_skipped_not_decisive` and `test_forms_outside_the_family_name_no_candidate`; a REJECTED section continues the walk -> `test_a_later_rejected_section_holds_a_head_an_earlier_section_passed`, `test_the_latest_passing_report_names_the_candidate`, `test_two_rejected_sections_hold_...`; a no-SHA PASSED section falls through -> the same three; window not cut at the next Verdict form -> `test_a_passed_line_without_a_sha_does_not_take_the_sha_of_a_following_rejected_line`; no sentence-end anchor -> the qualified-or-quoted test; no list or heading marker -> the same test; `*` kept -> `test_every_accepted_verdict_form_names_its_candidate`; sections read oldest first -> 8 tests. One mutation survived: removing the `DONE|SKIPPED|FAILED:` marker from `LINE_START` fails no test (Polish below).
  AC-1: real replay of relay `387b7863` exit 2/0/0 and `940921b0` exit 0/0/0 (base/57d58532/candidate). AC-2: the six listed lines plus `**Verdict:** PASSED at S` exit 0 on the candidate (base accepts one). AC-3: the seven listed hold lines, with `Verdict PASSED/REJECTED naming head S`, exit 2 on the candidate. AC-5: `lint-skills.py` 5511 of 5511 words, `diff -r references/` against base is empty, `grep -c 'Verdict PASSED' references/sd/workflow.md` 0 on both, and `delivery_gate.py check` output is byte-identical to base on four cases of `test_each_exit_ends_with_the_next_line_for_the_ask` (exit 0, 1 head, 1 reviewer, 2), a test the candidate leaves unmodified. AC-6: principles.md 651 words, and deleting the sentence in a scratch package fails `test_sd_dispatch` naming `validation-states-the-verdict-line`. Change since cycle 1: the first form must now stand at a line start or after `. ! ?`, a template naming both outcomes is skipped instead of decisive, and a REJECTED or no-SHA PASSED latest section holds; nothing else moved.
  Window cut judged sound: a PASSED form's SHA is read only up to the next `Verdict` match, so a following REJECTED line or a quoted `Verdict: PASSED at old` cannot lend it a SHA; the cost is a fail-closed hold when a non-counting `Verdict` mention sits between the PASSED word and its SHA (`Verdict PASSED. Not cycle 1's Verdict REJECTED. Candidate S`), which the stated one-line form avoids.
  The two corpus tasks (143 task files on this machine, one copy per repository and name; found a candidate: base 20, 57d58532 46, candidate 44; only these two differ) judged correct holds: `worker-completion-goes-to-main` latest counting section reads `Verdict PASSED.` with no SHA, and 57d58532 returned `0830a3be`, the PR's base SHA lifted from a Polish bullet in cycle 1; `holder-panel-header-and-polish` (ss-web) cycle 2 reads `Verdict recommended: PASSED (AC-10 stays an unverified limit)` with no SHA, and 57d58532 returned the older cycle-1 head `15fd489`. Both follow AC-8 (a latest PASSED names its own SHA); each costs one validator round trip, as any hold does.
- DONE: AC-7 again: fresh validator runs on the candidate's package text writing a report for a small fixture, at least two, one of them with the checklist echo that held in cycle 1, each with its verdict line and the result of the candidate's kc-dev-flow-2/scripts/delivery_gate.py recorded
  Three fresh `claude -p` runs on a scratch fixture (`/tmp/dgv2-ac7/r1..r3`, a copy of the cycle-1 fixture: base 7bb5a9ed, candidate a63645f8, one passing and one out-of-scope failing test), the candidate's principles.md (651 words, carries the stated sentence) as the only one in reach. Launch from inside each copy: `claude -p "$(cat ../<prompt>.txt)" --model sonnet --output-format stream-json --verbose --setting-sources project --disable-slash-commands --strict-mcp-config --permission-mode bypassPermissions --no-session-persistence --max-budget-usd 2`; stream init names `claude-sonnet-5-5`, 5 to 7 turns, 1155 to 1810 output tokens; user-level CLAUDE.md not excluded (no API key for `--bare`). Tokens read from each stream's write of the report: r1 `Verdict PASSED at a63645f`, r2 `Verdict PASSED at a63645f886f8e208aa6d6ec41aa25534b619807e`, r3 `Verdict PASSED at a63645f`.
  r1 and r2 (the cycle-1 echo shape: the checklist item began `Verdict PASSED or REJECTED naming the head`, and each worker echoed it capitalised as its `- DONE:` bullet ahead of the line): candidate `delivery_gate.py check --head a63645f8` accepts both (`equals validated candidate`); 57d58532 holds both (`names a candidate SHA`); base accepts both. r3 (a checklist item with the verdict phrase mid-item): the stated line came after a full stop at the end of an evidence line, candidate accepts, 57d58532 and base accept. 3 of 3 accepted by the candidate; 2 of 2 echo runs held by 57d58532 and accepted by the candidate. Sample of three, not a rate: the rate is read on the first adopter validation after release. Streams and fixture copies are in `/tmp/dgv2-ac7/`.
- DONE: A minimal acceptance script the Captain can run (three to six steps), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition
  Script saved as `/tmp/dgv2-accept.sh`, run as `env -i HOME=$HOME PATH=/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin bash --noprofile --norc /tmp/dgv2-accept.sh`; it needs the colombo checkout (holds base, 57d58532 and the candidate), the read-only relay checkout `/Users/kent/conductor/repos/subspace-relay`, git and python3, no spacedock binary. Six steps (a `base=N old=N cand=N` line is the exit code of the check at base c545b896, 57d58532 and 43490668):
```bash
A=/tmp/dgv2-accept; R=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo
G=kc-dev-flow-2/scripts/delivery_gate.py
x() { for v in base old cand; do python3 -B $A/$v/$G check $1 --pr o/r#1 --text-file $A/text.txt --head $2 >/dev/null; printf '%s=%s ' $v $?; done; echo; }
rpt() { printf '## Stage Report: validation\n\n- DONE: x\n  %b\n' "$1" > $A/t.md; x $A/t.md ${2:-2222222b}; }

echo "--- 1 setup: base c545b896, old 57d58532 and candidate 43490668 extracted from $R (python3 and git only; no spacedock binary)"
rm -rf $A && mkdir -p $A/base $A/old $A/cand && echo gate > $A/text.txt
for p in "base c545b896" "old 57d58532" "cand 43490668"; do set -- $p; git -C $R archive $2 kc-dev-flow-2 | tar -x -C $A/$1; done; echo extracted

echo "--- 2 the relay report that held, then its repair, at the same head (exit codes; expect base=2 old=0 cand=0, then 0 0 0)"
H=985200258eebc7aad832716fa8e4b8b57518921f
for c in 387b7863 940921b0; do git -C /Users/kent/conductor/repos/subspace-relay show $c:owner-sees-all-feedback-page.md > $A/relay.md; printf '%s: ' $c; x $A/relay.md $H; done

echo "--- 3 a prior or qualified Verdict before the real rejection (expect old=0 cand=2 on every line)"
rpt 'Independent Verdict: PASSED at 2222222b\n  Verdict REJECTED at 3333333c.'
rpt 'Prior Verdict: PASSED at 2222222b\n  Verdict REJECTED at 3333333c.'
rpt 'Cycle 1 read Verdict PASSED at 2222222b and was withdrawn.'

echo "--- 4 a checklist item echoed ahead of the stated line (expect old=2 cand=0, then the REJECTED twin base=0 old=2 cand=2)"
printf '## Stage Report: validation\n\n- DONE: Verdict PASSED or REJECTED naming the head\n  Verdict PASSED at 2222222b\n' > $A/echo.md; x $A/echo.md 2222222b
sed 's/PASSED at/REJECTED at/' $A/echo.md > $A/echo2.md; x $A/echo2.md 2222222b

echo "--- 5 a later REJECTED section on the head an earlier section passed (expect base=0 old=0 cand=2), and a later PASSED over an earlier REJECTED (0 0 0)"
printf '## Stage Report: validation\n\n  Verdict PASSED at 1111111a\n\n## Stage Report: validation (cycle 2)\n\n  Verdict REJECTED at 1111111a: new Material finding.\n' > $A/rej.md; x $A/rej.md 1111111a
printf '## Stage Report: validation\n\n  Verdict REJECTED at 0999999a\n\n## Stage Report: validation (cycle 2)\n\n  Verdict PASSED at 1111111a\n' > $A/pas.md; x $A/pas.md 1111111a

echo "--- 6 candidate unit suite, and no FO-read file differs from base"
(cd $A/cand/kc-dev-flow-2/scripts && python3 -B -m unittest test_delivery_gate 2>&1 | tail -3)
diff -r $A/base/kc-dev-flow-2/references $A/cand/kc-dev-flow-2/references && echo "references/ identical to base"
```
  Observed (fresh shell, exit 0): step 2 `387b7863: base=2 old=0 cand=0`, `940921b0: base=0 old=0 cand=0`; step 3 `base=2 old=0 cand=2`, `base=2 old=0 cand=2`, `base=0 old=0 cand=2`; step 4 `base=0 old=2 cand=0`, then `base=0 old=2 cand=2`; step 5 `base=0 old=0 cand=2`, then `base=0 old=0 cand=0`; step 6 `Ran 22 tests ... OK` and `references/ identical to base`. It does not cover a measured FO session, a real adopter validator beyond the three fixture runs, or `test_sd_dispatch` (run separately above).
  `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since c545b896` in the candidate worktree: "15 ADR file(s) checked, 0 legacy", exit 0. Also at 43490668: `comment_ratio.py c545b896 43490668 --workflow-dir <dev2>` code lines 126, comment lines 0, exit 0; `doc_impact.py c545b896 43490668` exit 0 lists `kc-dev-flow-2/README.md` and `references/sd/adoption.md` (each already carries `unaffected: <reason>` in the implementation report); `design_surfaces.py check` on this task "presentable", exit 0; `dispatch_records.py` on the task folder "9 dispatch record(s) complete", exit 0.
  Verdict PASSED at 43490668592b01b7acbacf1777a1e6ffc930d4bf, PR #647 head (open Draft, equal to the dispatched head; base c545b896). Findings by Review-finding disposition, none Material. F1 Deferred risk: a template line written with other punctuation, `Verdict PASSED | REJECTED naming head S` (accepted as a verdict, exit 0 when S is the head) or `Verdict PASSED, or REJECTED ...` (counts as PASSED, holds for lack of a SHA), is not recognised as naming both outcomes; no observed trigger (FO's wording and every echo seen is `PASSED or REJECTED`), and it becomes Material if the checklist wording gains such punctuation and a validator echoes its head. F2 Polish: the `DONE|SKIPPED|FAILED:` marker branch of `LINE_START` has no test (mutation survives), so `- DONE: Verdict PASSED at S` is accepted today without a test holding it. F3 Polish: the principles.md sentence says a report without the line holds the merge ask, while the three near spellings also pass; and a quoted earlier verdict at a line start is still decided by the first form (the stated Limit). F4 Polish: a `### Verdict` heading with `PASSED.` on the next line stays held, as at base. F5 Deferred risk: the first counting form decides, so a validator that quotes verdict-shaped text at a line start or after a full stop ahead of its own line is decided by the quote (the stated Limit); observed on this very report, which the candidate's check held until two quoted `. Verdict REJECTED` examples were rewritten; it becomes Material when a validator report of a real task is held this way and FO has no repair but a round trip. F6 scope of this verdict: the dispatched checklist reads AC-8 as the latest section with a counting form deciding, and the verdict is against that reading; the AC-8 text now in this task file (changed after dispatch, citing Cycle 2 P1 review:5527985770) says the newest section decides even with no counting form, and 43490668 does not meet it: a PASSED section then a newest section with no Verdict form exits 0 here (probe 0/0/0, and `test_the_latest_passing_report_names_the_candidate` pins it), which FO already took to repair under `### Feedback Cycles` Cycle 2. My state commit 122d4c90 also carried FO's uncommitted edits to AC-8 and the Cycle 2 entry, because a path-scoped commit takes the whole file.

### Summary

Verdict PASSED at 43490668592b01b7acbacf1777a1e6ffc930d4bf. The Codex P1, F1 and AC-8 each reproduce on 57d58532 and are fixed, every new test fails under its own mutation except the untested marker branch, and 3 of 3 fresh validator reports, including 2 with the echo that held in cycle 1, are accepted by the candidate's check. Two corpus tasks change from a candidate to a hold, both correct under AC-8; one Deferred risk and three Polish items remain, none Material.

## Stage Report: implementation (cycle 4, repair of Cycle 2 P1)

- DONE: Investigation with no candidate change: reproduce on #647 head 43490668 the Codex round-2 P1 and count in the ideation corpus how many tasks would change from a candidate to a hold; send FO the reproduction, the count and the proposed fix with tests and mutations, then wait
  Reproduced (PASSED at 1111111a, then a cycle-2 section with only `Recommend PASSED. Head 1111111a.` or only a FAILED line, `--head 1111111a`: exit 0). Count: 143 tasks, 44 candidates at 43490668, 38 with the fix; 6 rows (5 tasks) turn to a hold, each with a newest section in a bare, Recommend or Independent-verdict form. Sent to `main` before any edit.
- DONE: After FO's fix authorization only: the fix in kc-dev-flow-2/scripts/delivery_gate.py with tests that fail without it (shown failing by a mutation run), the corpus re-count, the roborev gate, push to #647's branch without force, CI green, stage report appended
  0a26ca37: `validated_candidate` returns the newest validation section's `first_verdict` result alone; docstring updated. Flipped `verdictless` in `test_the_latest_passing_report_names_the_candidate` (now None) and added a REJECTED-then-PASSED case (newest wins, `d127ec71`). New `test_the_newest_validation_section_decides_even_when_it_has_no_counting_form`: a held spelling, no verdict word, a FAILED-only item and lower-case `verdict` after an older PASSED each exit 2 with `names a candidate SHA`; a PASSED then PASSED then verdictless run exits 2. Mutation (restore the skip-and-continue walk): the flipped test and all four subTests plus the parent fail (6 failures), restored: 23 OK.
  Re-count at 0a26ca37 is identical to the proposal: 143 tasks, (found, found) 38, (held, held) 99, (found, held) 6. test_lint_skills OK; lint-skills 5511 of 5511; comment_ratio 0 of 143 code lines. Roborev `clean on 0a26ca371; evidence=roborev:689`. Pushed 43490668..0a26ca37 without force; all four CI checks pass (unit tests, version parity, route gate, GitGuardian). PR body Limits, the flipped-test note and the evidence line updated (no comment, no review request, still Draft).
- DONE: AC-8 edit for FO to name at the gate
  AC-8 edited in place on FO's instruction (id kept): the clause "A latest section with no counting form is skipped and the next older section with one decides" is dropped; AC-8 now says the newest validation section decides even when it carries no counting form, and the falsifier covers it. Amendment 1's text is untouched.

### Summary

The newest validation section alone now decides, so a later section in a form the check does not read, or with no verdict, holds the ask instead of letting an older PASSED name the candidate. Side effect to know: 6 corpus rows (5 tasks, archived or in validation) change from a stale older SHA to a hold. AC-7's fresh-validator run belongs to the fresh recheck FO dispatches.


## Stage Report: ideation (cycle 2, redo under Captain amendment 2)

- DONE: Captain amendment 2 applied: AC-1, AC-2, AC-3, AC-5, AC-6, AC-7 and AC-8 moved under amendment 2's `Superseded text:`, and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/design_surfaces.py check on the task file exits 0
  The seven criteria sit verbatim (indented) under `### Amendment 2`, with the first `## Design` kept there as history; a line-by-line comparison against the pre-edit file finds 0 non-blank lines lost. design_surfaces.py check printed `delivery-gate-verdict-form.md: design surfaces presentable`, exit 0; `status --ac-scan` lists only AC-9 to AC-14.
- DONE: A redone `## Design` (PRFAQ and Mermaid) for amendment 2: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/delivery_gate.py compares the PR head with the head FO names in its latest validation dispatch record; the exact form of that line, where in the record it sits, and whether /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/dispatch_records.py checks it on validation records
  Form: its own whole line `Candidate: <40-hex head>`, one per head validated, in the record header above the first `## ` heading (D1 asks whether it carries `<owner/repo>#<N>`). The `Dispatched:` SHA cannot carry it (workflow or state checkout in 68 of 104 records). dispatch_records.py does not check it: delivery_gate.py is the one owner and fails closed with the form printed; reasons and what breaks without it are in the FAQ. Chain checked: Spacedock, kc-dev-flow-2, kc-dev-flow v1, adopters; ADR 0014, ADR 0015 and the `Override:` lines read, none contradicts.
- DONE: A read-only count over archived validation dispatch records (this workflow and the adopters relay, qnow, ss-web on this machine): how many name one candidate head that the proposed line form would carry, and the replay of the two bite cases recorded in archived task fo-record-checks (observer-before-merge-guard, migration-and-number-guards): would the new check have exited 1 at their merge ask
  100 of 104 records (37 tasks) name exactly one head in some shape (68 labelled `candidate`, 32 the sole hex token on `Dispatched:`); 0 carry the whole-line form. observer-before-merge-guard: exit 1 at `7679ab7a` and 0 at `40c714a6` once `validation-3` has the line (prototype), exit 2 on the records as written. migration-and-number-guards: no, exit 2: its archive has no `dispatch/` folder, so the new check fails closed and does not show the bite.
- DONE: A disposition of what PR #647 already carries (the verdict-form parsing in kc-dev-flow-2/scripts/delivery_gate.py, the verdict sentence in kc-dev-flow-2/skills/validation/principles.md, their tests): keep or remove each, with what breaks without it, and whether the work continues on the #647 branch or a new one
  Remove all four parts (parser, its tests, the principles sentence, the `validation-states-the-verdict-line` pin); nothing breaks without them. The existing second-reviewer, gh and exit-line tests stay and only their fixture gains a record folder. Continue on the #647 branch, first commit restoring the four files to origin/main (table in `## Design`).
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Prototype counts with `len(text.split())`: startup, both idle moments and after the archive byte-identical; merge ask passage 84 to 83, exit 0 output 20 to 20, exit 1 27 to 25; validation dispatch passage 64 to 75; workflow.md 5521 against the budget 5511, 5495 without one unpinned 26-word sentence (payment stated in `## Design`).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-9 to AC-14 each carry a Verified by, a Falsifier and a Limit; one decision, D1 (bare `Candidate:` line, recommended, or PR-qualified) with what gets worse under each.
- DONE: AC-9 a merge ask on a head no validation was dispatched on exits 1
  Current evidence: observer-before-merge-guard replay exit 1 and 0 on a scratch copy (prototype); not yet verified: the committed test.
- DONE: AC-10 a record without the one form holds with exit 2 and prints the form
  Current evidence: no-folder (migration-and-number-guards), no-line (this task's own records) and the relay free-form line each exit 2 on the prototype; not yet verified: the committed subTests and the 8-character and trailing-text cases.
- DONE: AC-11 the highest-numbered record decides, and a record may name several heads
  Current evidence: scratch copy of journey-server-host-pilot (validation-10 over validation-2) exit 0 and 1, and a two-line record exit 0 and 1 (prototype); not yet verified: the committed subTests.
- DONE: AC-12 the check reads no validator prose and claims no verdict
  Current evidence: base has 3 lines matching `Verdict|PASSED|REJECTED`; the prototype never reads a report section; not yet verified: the REJECTED-report test and the grep at the candidate (prototype docstring not yet rewritten).
- DONE: AC-13 FO reads no more words than base at the merge ask and none at four moments
  Current evidence: counts in the table above, measured on a /tmp prototype and not on a candidate; not yet verified: the same counts on the shipped text, and the offset that brings workflow.md to 5511 or lower.
- DONE: AC-14 nothing of #647's verdict parsing remains and the pins follow the new wording
  Not yet verified: no candidate exists; the pin entries `dispatch-record` and `readme-keeps-delivery-rules` are the ones to change (grep of test_sd_dispatch.py 2026-10-15).

### Summary

The check now reads the head FO writes when it dispatches validation, not the validator's prose; FO's reading of PASSED or REJECTED stays at the gate. 100 of 104 archived validation records already name one head, but in three shapes and never as a whole `Candidate:` line, so the design adds that one line and a hold that prints it. One real replay shows the bite caught (observer-before-merge-guard); the other (migration-and-number-guards) cannot be replayed because its records were never saved, and the report says so. The prototype and corpus scripts are machine-local in /tmp/gate-redo; no repository file, branch or commit was written, and #647 was read only.
