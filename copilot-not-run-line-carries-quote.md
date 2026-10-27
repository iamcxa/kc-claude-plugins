---
title: The delivery check refuses a `copilot not run` line without the printed quote and a retry offer
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:copilot-not-run-line-carries-quote:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:copilot-not-run-line-carries-quote-backlog-1
              briefing:
                id: briefing:copilot-not-run-line-carries-quote:backlog:attempt-1:revision-1
                digest: sha256:e5a0f48abcb05f28f0bd5e830638c59dbd362eb94fe075425b2a0d1af622275e
                room-ref: ./copilot-not-run-line-carries-quote/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:copilot-not-run-line-carries-quote:backlog:1
                briefing: briefing:copilot-not-run-line-carries-quote:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-27T15:13:03.735763Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-27) answering 「需要你決定：第 8 批 7 張任務的待辦關卡，要不要一起批准進入設計階段？同時把已經做完的 `peers-paseo-host-binding` 關掉。我建議全部批准，也關掉那張。」; accepts FO's recommendation
              application:
                target-stage: ideation
                state: consumed
        - id: gate:copilot-not-run-line-carries-quote:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:copilot-not-run-line-carries-quote-ideation-1
              briefing:
                id: briefing:copilot-not-run-line-carries-quote:ideation:attempt-1:revision-1
                digest: sha256:7ac2eaf2d4b7e40b67cb2a82224053222cbc5dcd0ea2c307ecf1d60500ecf7d4
                room-ref: ./copilot-not-run-line-carries-quote/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:copilot-not-run-line-carries-quote:ideation:1
                briefing: briefing:copilot-not-run-line-carries-quote:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-27T15:56:12.149086Z"
                decision: approve
                reason: Captain 「其他全照建議」 (chat, 2026-10-27) answering 「需要你決定：第 8 批的設計，照首席工程師的建議一起處理，可以嗎？6 張進入實作，1 張直接關掉，再送一份 issue 給 Spacedock。我和首席工程師都建議照這樣做。」, after he declined a second, unanchored batch review (「不須要」); accepts FO's recommendation
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-27T16:00:07Z
worktree: .worktrees/spacedock-ensign-copilot-not-run-line-carries-quote
---

## Scope

- Source: the Captain 「可以，開 A-D」 (chat, 2026-10-26), answering 「需要你決定：下面 5 個套件缺口候選，要開哪幾張待辦？我建議開 A 到 D，E 先不開。」 after the learn backfill of 11 archived tasks (Captain 「補跑」, 2026-10-26).
- Bite: observer report on fo-written-lines-checked-before-dispatch (#724, 2026-10-26): the merge ask said only 'not run (quota)', against `extensions/copilot/EXTENSION.md` ('with the printed quote, and offers a retry'); FO had recorded the same rule in its own notes after the fo-write-checks observer caught it on 2026-10-19, and still missed it.
- Added 2026-10-27 (the Captain 「照建議」 on FO's batch-7 retrospective, item c): a second bite of the same class: the #728 merge ask carried no `second reviewer:` line at all although the change touched review rules, and `delivery_gate.py check` reported 'no second reviewer outcome is missing' (observer report on codex-reader-same-head-unresolved).
- Upstream first: `scripts/delivery_gate.py` (`check`, `question`), `extensions/copilot/EXTENSION.md`, `extensions/copilot/copilot_review.py` exit 5 output.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
Result: aligned 2026-10-27 on the outcome by the Captain's 「全准」 answering this task's backlog briefing-1 question, which named the delivery check refusing a missing second-reviewer line and a copilot not run line without the printed quote and a retry offer; where each check runs is put to him at the ideation gate.
Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-27 — batch 8 review at the ideation gate (the Captain's batch ruling 2026-10-27): per-task disposition, the Captain's decisions, order and batch risk.

## Design

### PRFAQ

**Headline.** Before the Captain sees a delivery question, the existing delivery checker requires the configured second-reviewer declaration and carries a Copilot refusal's actual printed quote and a conditional retry offer into the question. The same check runs again before the merge ask, so a later review round cannot silently drop those facts.

**Who benefits?** FO (First Officer, the workflow coordinator) gets the missing fields at the writing step. The Captain sees what Copilot actually said and can authorize a retry when quota returns; a refusal remains unread review, never a clean round.

**What is the smallest slice?** Repair `delivery_gate.py question` and `check`, their existing tests, and the Copilot extension's instruction at its existing Read step. Keep Spacedock's gate/merge lifecycle, the review reader, the workflow README, the watcher and the observer unchanged. This is a Pilot repair within the approved workflow; it creates no hosted resource, recurring job, new reviewer request, CI trigger or release duty.

**Does this enforce an actual merge?** No. It refuses these two commands with exit 1 for incomplete text and exit 2 for unreadable required input. An agent that bypasses them can still merge; ADR 0027 already records that boundary. It verifies equality with a caller-saved reader output, not that a caller could not forge that file, not provider provenance, and not the truth of a semantic trigger.

### Checked chain and current baseline

1. **Spacedock first:** read its own 0.27.3 `mods/pr-merge.md`, `skills/first-officer/references/fo-merge-core.md` route contract and ensign contract. The upstream mod manages PR lifecycle, authorization and sentinel/archive; it does not define a second reviewer or a Copilot quote. Its hook is not the owner of this package-specific check. No upstream change is proposed.
2. **Package next:** `git fetch origin` succeeded after the managed filesystem required the authorized retry. Examined `origin/main` at `8bf4f3582411e8e4238f19fbadda8ddeca6767be`; its `kc-dev-flow-2/.claude-plugin/plugin.json` is 0.32.0. Installed Codex package bytes equal that commit for `delivery_gate.py`, `copilot_review.py`, `EXTENSION.md` and `references/sd/workflow.md`. `unstated_second_reviewers()` only iterates `Second reviewer: <name> because`; no declaration, or the actual `copilot triggered by ...` spelling, yields no iteration. A canonical `copilot not run: quota` already satisfies the existing outcome check. `question()` currently reads no README. `check()` already resolves README scalars/extensions and stores truncated confirmation clauses in `merge/ask-N.json`.
3. **Reader's own contract:** `copilot_review.py state()` exit 5 prints `not a review of <9-hex head>: "<quote>"; answer=review:<id> at <timestamp>`. `quote()` HTML-unescapes, collapses whitespace, takes 120 characters and changes `evidence=` to `evidence:`. Empty answers may produce an empty quote. A real heading or own line comment changes the classification; no list of quota sentences is proposed.
4. **Sibling adopters, read only:** relay beirut-dev2 `docs/dev2{,-poc}/README.md` and web dev2-fo `docs/dev2{,-poc}/README.md` list no remote reviewers and have empty `second-reviewer`; no declaration should be required there. Relay dhaka's older copies list only learn and no second-reviewer. QNow `conductor/repos/qnow-adopt-dev2/docs/dev2{,-poc}/README.md` list codex and copilot with second-reviewer copilot, as does this workflow: declaration applies. These are local checkout observations, not remote adoption verification.
5. **Prior rulings:** ADR 0013 keeps exit 5 as not run, forbids re-request until the Captain says quota is back and requires positive recognition of a review. ADR 0027 favors the script at the write and records the Captain rejecting a phrase heuristic without useful evidence. Checked `Override:` records; none reverses these two rules. `comment-check-reaches-delivery-gate` was explicitly closed for lack of demonstrated harm; here the two saved problem questions reproduce the reported omissions. No new ADR number is claimed; this repairs the existing rulings.

The bounded existing-code check used both named call sites (`text_problems`, `question`, `check`, `find_readme`, `write_record`) and extension/README/reader callers (`second-reviewer`, `copilot not run`, `answer=review`, `retry`). The rule and formatter exist; the writing check is incomplete. Excluded from the claim: private wrappers, host tool-permission guards, provider-side policies and semantic review of a diff. The existing checker is the implementation seam, not a replacement gate.

### Proposed behavior

- Both commands resolve the workflow README through existing `find_readme`. Add optional `--workflow-dir` to `question` with the same meaning as `check`; current split-root paths resolve through their parent already. Missing/unreadable README is exit 2; do not silently turn reviewer checks off. An empty second-reviewer means no configured second reviewer. A nonempty value not listed in `extensions`, or with no other listed remote reviewer, is configuration error, not permission to request a review.
- When codex and copilot are listed and `second-reviewer` names one, require exactly one case-insensitive `second reviewer:` declaration in the submitted question plus summary: `<configured name> because <nonempty trigger>` or `not triggered`. Do this even when no structured trigger is known: the README already requires the negative declaration. This catches an omitted line without pretending to classify authority or review changes from filenames. `profile: prod` and `Surfaces: db` are structured positive triggers and refuse `not triggered`. The harder-to-reverse dispatch, semantic authority/approval/merge/review change and Captain-request triggers remain FO's stated judgment, checked by the observer; do not silently interpret unrelated prose as a trigger or treat `NEVER_PATH` as this rule.
- Preserve the existing requirement for the named reviewer's outcome. A valid review/comment reference or explicit not-run outcome remains necessary. Do not mistake `answer=review:<id>` for completed-review evidence. For Copilot's existing non-reviewable PR types, preserve `copilot skipped: <type> PR` as the outcome permitted by EXTENSION.md: `check` compares the stated type with `facts.title`; `question` checks the form and leaves title verification to `check`. A supported type (`feat`, `fix`, `refactor`, `perf`) cannot claim this skip. Untriggered second reviewers are not newly requested or listed as unread.
- A Copilot non-review refusal is written on its own line as `copilot not run: "<printed quote>"; answer=review:<id>`. FO saves the existing reader's stdout at `<task folder>/review/copilot-not-run.txt`; this is a declared input, retained with the task, not a machine cache or a new receipt schema. On an observed exit 5, save/copy the printed line; re-reading the provider may be needed if stdout was lost, but never request another review to obtain it. Do not fabricate the quote from the known quota example.
- Each command reads that file only for a refusal. Parse the fixed exit-5 prefix and trailing `answer=review:<id> at <timestamp>`, treating the quote as opaque text (including internal quotes, Unicode and empty quotes). Compare the entire quote and id with the gate line, not mere quote punctuation or a quota keyword. A missing/unreadable saved file is exit 2; a readable but malformed source or a mismatch is exit 1. Report the missing input and repair, without claiming provider authentication. A later head does not erase a task's earlier refusal: ADR 0013's task-level no-retry state survives that push; the saved line explicitly retains the answer's older head. A later actual review supersedes its use in the question. Historical tasks are not rewritten.
- Require a separate, explicit offer: `Copilot retry: available when the Captain confirms quota is back.` This is an offer only. The checker never calls `gh pr edit`, POST, a review request, or a retry; a subsequent request still requires the Captain's quota-restored instruction. A bare word such as `retry`, a negative sentence such as `no retry`, or an offer only in the task body is insufficient.
- Preserve exit-2 configuration errors under the existing extension rule: `copilot not run: configuration error: <nonempty reason>` needs no nonexistent exit-5 quote. A bare `quota` reason is not this branch. This is not an alternate refusal path; whether FO has misreported a real refusal as configuration failure remains an observer/provenance limit. No change to `copilot_review.py`, its classification, request policy, or number of rounds.
- `check` uses the same text/input check as `question` before writing `ask-N.json`. On failure it saves no success record; existing candidate-head, CI, role, ADR, findings and approval checks remain. On success retain current output and authority wording. The source file belongs beside existing task review artifacts; no extra merge-record schema is needed in this slice.

### Journey and stops

```mermaid
flowchart TD
    A[FO reads task and workflow reviewer configuration] --> B[FO writes question and reviewer declaration]
    B --> C{Copilot refusal reported?}
    C -- Yes --> D[FO saves exit-5 stdout and copies quote, answer id and retry offer]
    C -- No --> E[FO runs delivery_gate question]
    D --> E
    E --> F{Text and required source valid?}
    F -- No --> H[Hold; FO repairs text or missing input]
    H --> B
    F -- Yes --> G[FO presents validation gate to Captain]
    G --> I{Captain approves applicable delivery authority?}
    I -- No --> J[Stop or use existing feedback route]
    I -- Yes --> K[FO completes permitted review rounds and updates text]
    K --> L[FO runs delivery_gate check on validated PR head]
    L --> M{Reviewer checks and existing delivery checks pass?}
    M -- No --> H
    M -- Yes --> N[FO follows existing exact-head merge authority]
    D -. Offer only; no automatic request .-> O{Captain confirms quota is back?}
    O -- No --> P[Keep Copilot unread; do not request]
    O -- Yes --> Q[FO may request and read another review]
    Q --> B
```

### Replay over this workflow's saved merge asks

State snapshot for the corpus: `c652d02fd6ba6bfd95f940a395d295387a5677b1`. Scanned all 71 `merge/ask-*.json` files in active/archive tasks. Those records do not store the original full text, so each was joined to its own saved validation briefing using both saved Sufficiency and Necessity strings; task content came from the immutable `git-root://state/<commit>/<path>` artifact URI. This reconstructs candidate text associated with the saved ask; truncated-prefix agreement is not proof the original temporary text was identical. No claim is made that all 71 past calls can be exactly recreated.

- 65 have one full-text candidate. Existing `text_problems`: 62 pass, 3 hold. Proposed local text/source probe: 15 pass, 50 hold; 47 previously passing records change to hold. These are records, including repeat asks, not 47 independent incidents or whole remote delivery verdicts.
- Added reasons overlap: 35 contain a canonical Copilot not-run line but lack the new saved source and explicit retry offer; 13 have a malformed/wrong-name reviewer declaration; 2 omit the declaration entirely. No saved source was invented. Old asks are observations, not a migration backlog; new rules apply on the next invocation.
- `fo-written-lines-checked-before-dispatch` (#724), ask-1 and ask-2: old text check passes; proposal holds `second reviewer: copilot triggered by ... not run (quota)` as malformed. Rewriting only `triggered by` to `because` still leaves no legitimate outcome. With the canonical `copilot not run: quota` outcome it then holds for quote/source/retry. Repairing one field cannot clear all three.
- `codex-reader-same-head-unresolved` (#728), ask-1 and ask-2: old text check passes; proposal holds the wholly absent second-reviewer declaration. The task changes review behavior, but the check catches the omission through configuration, not keyword inference.
- 6 unknown: `adr-protected-path-guard/ask-1`, `kc-adr-format-source/ask-1`, `kc-decision-log-cli/ask-1` have no matching saved full text; `worker-knows-the-team-and-asks-early/ask-1`, `ask-2`, `ask-3` each match two distinct texts. Do not score these as pass, hold or a regression.
- Both actual baseline CLI paths were also exercised with temporary tasks and the package's stub GitHub fixture: absent declaration and `copilot not run: quota` each exited 0 in `question` and in `check` (four observed passes). The actual installed reader's `state()` was exercised on injected API pages for a refusal (exit 5). Five probe cases passed: exact output/quote/id plus offer; altered quote; removed offer; absent output; wrong id. This is a disposable design probe, not a candidate implementation or provider test.

`gh api rate_limit --jq .rate.remaining` failed with `error connecting to api.github.com`. No current GitHub PR state, real quota, provider response or merge is verified. Git fetch success does not remove that limit. The prototype reads local artifacts and makes no provider request.

### Words FO reads at each lifecycle moment

Count with `len(text.split())`, same input bundles in both columns. Reused and reran the archived `peers-rules-name-each-host-binding/validation-merged/fixture-outputs.py` against the installed 0.32.0 package, changing only its `W/kc-dev-flow-2` prefix to the installed package root. All fixture calls passed; they exercise current `pr_watch`, `observer_check` and `delivery_gate` using disposable repositories and stub GitHub data. This table measures a specified reading route, not cognitive load or every possible branch.

Inputs: workflow 5565; package mod 48; Spacedock Startup 133 and Awaiting Completion 507; Delivery authority section 461; Extensions section 224; learn extension 282; learn skill 2918; Copilot extension 740. Actual fixture outputs: open 29, merged 20, archive 28, successful merge check 57. The success fixture has no second reviewer and no not-run outcome, so it measures the unchanged branch; actual reviewer points vary with text.

| Moment and counted bundle | Before | Proposed after |
| --- | ---: | ---: |
| Startup: workflow + package mod + SD Startup + open output | 5775 | 5775 |
| Idle, open PR: mod + SD Awaiting Completion + Delivery authority + open output | 1045 | 1045 |
| Idle, merged PR: preceding instructions + learn extension + merged output | 1318 | 1318 |
| After archive: mod + learn extension + learn skill + archive output | 3276 | 3276 |
| Merge ask, no Copilot read: Delivery authority + Extensions + pass output | 742 | 742 |
| Merge ask, Copilot read: preceding bundle + full Copilot extension | 1482 | 1518 |
| Validation question check, success output only | 3 | 3 |

The 36 added words live only at the Copilot Read step, proposed verbatim:

> On exit 5, save stdout to `<task>/review/copilot-not-run.txt`; copy its quote and `answer=review:<id>` into `copilot not run: "<quote>"; answer=review:<id>`. Add `Copilot retry: available when the Captain confirms quota is back.` The delivery check compares the saved output.

If FO loads the whole Copilot extension at startup as well, that optional read adds 740 before / 776 after there too; do not hide the +36 by counting only the README. The refusal's source capture is a new action. Its exact quoted body and id are data-dependent; carry their actual word count when recounting the candidate. The retry line adds 10 words to the submitted text (count includes `Copilot retry:`). Proposed refusal diagnostics are 13 words for a missing declaration, 11 for quote/id, 7 for retry, with one 14-word repair line when relevant; print all applicable failures once, rather than the former pass output. No reduction claim and no workflow word-budget raise. CI configuration is unchanged; no per-PR CI cost was measured.

### Needs decision

**One decision for the Captain: use the shared `question`/`check` repair with a saved exit-5 output? Recommend yes.** It catches both measured omissions before presentation and again before merge; the saved output lets the check compare the printed quote, rather than accept quotation marks around `quota`; it preserves ADR 0013's no-automatic-retry rule. Worse: one saved file/action on refusal, +36 extension words when read, and a lost source blocks the ask until FO recovers it. Checking only at merge leaves the misleading validation question visible; checking punctuation alone cannot prove the line carries the printed quote. Configuration errors keep their existing reason-only branch. Approval accepts this bounded comparison, not source authentication or semantic trigger inference.

### Batch overlap

Proposed changed files: `kc-dev-flow-2/scripts/delivery_gate.py` (shared reviewer/config/source checks, `question --workflow-dir`, source-loading failures), `kc-dev-flow-2/scripts/test_delivery_gate.py` (both CLI paths and false controls), `kc-dev-flow-2/extensions/copilot/EXTENSION.md` (the 36-word save/copy/offer instruction). No workflow README, reader, watcher, mod, manifest, ADR index or number reservation changes.

| Named task | Same file or check, current task-file evidence | Implementation ordering |
| --- | --- | --- |
| archive-waits-for-observer-report | None: Spacedock archive/observer/learn seam, after actual merge | Independent; do not move reviewer checks into its archive hook |
| idle-hook-names-merged-tasks-without-learn | None: watcher/learn notices and idle outputs | Independent; combine lifecycle word recount if shipped together |
| copilot-not-run-line-carries-quote | This task owns the three files above | One implementation owner |
| dispatch-carries-reserved-adr-number | None: dispatch_records/number_guards and reservation transport | Independent |
| seed-check-requires-schema-fields | None: design_surfaces seed and task schema | Independent; new question tests need valid task fixtures |
| journey-probe-finds-nested-maps | None: adoption map discovery | Independent |
| read-adr-honors-adr-folder | None: kc-adr skill source and synchronized dev2 copy | Independent |
| adr-required-statement | Its older design names workflow/ADR checks, none of these files | Task records explicitly Closed 2026-10-20; frontmatter alone is misleading; no live owner inferred |
| journey-server-host-pilot | None: kc-journey-map host/client/server implementation | Independent, read only |
| ops-inbox-r1-setup-and-isolation | None: relay/ops inbox boundary | Independent, read only |
| pr-review-lite-value-pilot | None: Lite review pilot, not dev2 delivery checker | Independent, read only |
| adr-silent-undo-probe | None: archived scenario harness and experiment | Independent, read only |
| comment-check-reaches-delivery-gate | Direct overlap: delivery_gate.py and test_delivery_gate.py if revived | Explicitly Closed 2026-10-20; do not implement it. If FO reopens it, serialize on this current baseline |
| journey-canvas-hosted-poc | None: hosted journey canvas | Independent, read only |

Recommended order: implement this one repair from the current main baseline after approval; recheck these task files at dispatch. No other task is edited or contacted. Re-run the existing delivery suite when any revived shared-check work lands; shared output recounts must use the combined result.

## Acceptance criteria

**AC-1** Both command paths require the configured reviewer declaration, and honor an explicit untriggered result only where no structured positive trigger applies. Evidence: CLI tests for this workflow and QNow configuration, prod/db positive cases, and relay/web empty configuration; absent line, malformed `triggered by`, wrong reviewer, duplicates and prod/db `not triggered` each hold. Falsifier: remove the configuration-driven requirement and the saved #728 cases pass. Current evidence: corpus/prototype catches the absent and malformed cases; CLI integration and structured-case matrix remain future implementation proof.

**AC-2** Refusal quote and answer id equal the saved reader output in both `question` and `check`, including Unicode, internal quotes, HTML normalization, a >120-character body and the empty-body case. Evidence: run the unchanged real reader on injected pages, save its stdout, then exercise each CLI; alter one quote character/id or substitute `quota` and require exit 1. Missing/unreadable output requires exit 2; malformed readable output exit 1. Falsifier: accept quote punctuation alone or compare only ids. Current evidence: real reader formatter and five local probe cases; the full matrix and CLI error-code split are not implemented.

**AC-3** A refusal requires the explicit conditional retry offer in the submitted text, and neither check requests a review. Evidence: remove offer, write `no retry`, put offer only in the task body, and require exit 1; spy on subprocess calls and reject any request/POST. Exact quote and offer pass their checks. Falsifier: accept any occurrence of `retry` or add a review request. Current evidence: removed-offer probe fails; CLI subprocess controls remain future proof.

**AC-4** Keep adjacent outcomes correct: config error with nonempty reason, untriggered second reviewer, unlisted Copilot, valid review evidence, and Copilot skipped for unsupported PR type; a refusal answer id alone never counts as a review. Evidence: table-driven CLI cases, skipped type compared with PR title during `check`, and run the unchanged `test_copilot_review.py`. Falsifier: classify `answer=review` as a review, require refusal data from an unlisted reviewer, or allow `fix` to claim the docs skip. Current evidence: inspected original extension/reader and adopter configurations; these integration assertions remain unverified.

**AC-5** Replay the saved corpus with per-record provenance and limits, reproducing 71 records, 65 uniquely reconstructed texts, 6 unknown, and the two observed problem tasks holding. Evidence: the embedded replay program below on the named state snapshot and package; separately assert corrected variants of #724/#728 pass the new checks. Do not claim the local replay exercises provider CI or original temporary-file identity. Falsifier: drop the missing-declaration or quote/offer check and the corresponding counterexample passes. Current evidence: measured 62/3 baseline pass/hold versus 15/50 proposed, 47 changed; original 6 unknown retained.

**AC-6** Existing delivery checks and authority boundaries remain exercised; no success ask record is created on a new failure. Evidence: run `test_delivery_gate.py`, with a failure case asserting the task's merge directory has no new ask file, plus a temporary task's valid question followed by modified incomplete text at check. Test missing README/invalid configured reviewer as exit 2 and `--workflow-dir` with a folder task and a split-root task. Falsifier: wire only `question`, only `check`, or write the record before validating. Current evidence: actual baseline fixture command exercised; candidate behavior is not yet implemented.

**AC-7** Count FO's complete applicable passage/output bundles on the same scenarios before/after, preserving unchanged lifecycle rows and declaring the +36-word Copilot instruction, data-dependent source/output and retry costs. Evidence: rerun the named fixture/count recipe and `lint-skills.py` with the source checkout at the candidate; confirm no workflow/CI edits. Falsifier: move instructions into output and count README alone. Current evidence: all table inputs and baseline outputs measured; after values are design projections, not an implemented candidate measurement.

**AC-8** Publish only a design at this stage, with readable matching PRFAQ/Mermaid, named overlaps, and the Captain's unresolved location/source decision. Evidence: installed `design_surfaces.py check <task>` plus rendered diagram and path-scoped state diff showing this entity body only; frontmatter byte comparison. Falsifier: omit a branch/stop, remove the AC declarations or alter frontmatter/product source. Current evidence: final stage report records the actual design check and state commit; approval and implementation are future FO work.

## Reproduction notes

Diagram rendered with the locally installed `@mermaid-js/mermaid-cli` 12.0.0 (`mmdc -i journey.mmd -o journey.png`); extract the Mermaid block above as the input. The sandbox initially blocked Chromium startup; the authorized local render succeeded. Checked actors, approval/stop branches and the conditional retry route against the prose. Retry rejoins question construction so it cannot bypass the validation gate. PNG/SVG are disposable local outputs, not required source dependencies.


For the corpus/probe below, supply the same installed package and state checkout; use the cited state commit in a disposable snapshot if active state has since changed. The code exercises the existing text checker and a deliberately limited proposed predicate; it does not implement CLI config discovery, error-code distinctions, skip-type handling or provider validation. Those are explicitly acceptance work. Run `python3 -B replay.py <package> <state>` after extracting this block. Python stdlib suffices; Git must be able to read the artifact URI commits.

```python
import collections, contextlib, importlib.util, io, json, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
PKG=Path(sys.argv[1])
STATE=Path(sys.argv[2])
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
gate=load('gate',PKG/'scripts/delivery_gate.py')
reader=load('reader',PKG/'extensions/copilot/copilot_review.py')
def proposed(task,text,second='copilot',enabled=True,printed=None):
 errors=[]
 if enabled and second:
  rows=re.findall(r'(?i)\bsecond reviewer:\s*([^\n]+)',text)
  if len(rows)!=1:errors.append('second-reviewer declaration missing or duplicated')
  elif re.match(r'not triggered(?:[.;]|$)',rows[0],re.I):
   if re.search(r'^profile:\s*prod\s*$',task,re.M) or re.search(r'^Surfaces:.*\bdb\b',task,re.M):errors.append('known trigger contradicts not triggered')
  elif not re.match(re.escape(second)+r'\s+because\s+\S',rows[0],re.I):errors.append('second-reviewer declaration malformed or wrong reviewer')
 for m in re.finditer(r'(?im)(?<![\w-])copilot not run:\s*([^\n]*)',text):
  value=m.group(1)
  if value.lower().startswith('configuration error:') and value[len('configuration error:'):].strip():continue
  source=re.fullmatch(r'not a review of [0-9a-f]{9}: "(.*)"; answer=review:(\d+) at (\S+)\s*',printed or '')
  if not source: errors.append('Copilot printed output missing or invalid')
  elif not value.startswith('"'+source[1]+'"; answer=review:'+source[2]):errors.append('Copilot quote or answer id differs')
  if not re.search(r'(?im)^Copilot retry: available when the Captain confirms quota is back\.[ \t]*$',text):errors.append('Copilot retry offer missing')
 return errors

def combined(d):return d.get('question','')+'\n'+'\n'.join(x.get('summary','') for x in d.get('artifacts',[]))
rows=[]
for p in sorted(STATE.rglob('merge/ask-*.json')):
 d=json.loads(p.read_text()); matches=[]
 for b in sorted((p.parent.parent/'review/validation').glob('briefing-*/index.json')):
  j=json.loads(b.read_text());t=combined(j)
  if all(str(d.get(k,'')) in t for k in ['sufficiency','necessity']):matches.append((b,j,t))
 unique={t:(b,j) for b,j,t in matches}
 if len(unique)!=1:
  rows.append(dict(path=str(p.relative_to(STATE)),result='unknown',reason='no full-text match' if not unique else 'ambiguous full-text match'));continue
 t,(b,j)=next(iter(unique.items())); uri=j['artifacts'][0]['uri'];match=re.fullmatch(r'git-root://state/([^/]+)/(.*)',uri)
 if not match:raise ValueError(uri)
 task=subprocess.check_output(['git','-C',str(STATE),'show',match[1]+':'+match[2]],text=True)
 old=gate.text_problems(task,t)[0];new=old+proposed(task,t)
 rows.append(dict(path=str(p.relative_to(STATE)),briefing=str(b.relative_to(STATE)),old=len(old),new=len(new),added=proposed(task,t),result=('hold' if new else 'pass'),has_notrun=bool(re.search('copilot not run:',t,re.I))))
print(json.dumps(rows,indent=2))
print('TOTAL',len(rows),'RESULT',dict(collections.Counter(r['result'] for r in rows)))
print('BASE',dict(collections.Counter(('hold' if r['old'] else 'pass') for r in rows if 'old'in r)))
print('CHANGED',sum(r.get('old')==0 and r.get('new',0)>0 for r in rows))
# Exercise the real existing reader's refusal formatter without any provider request.
body='Copilot was unable to review this pull request because the user who requested the review has reached their quota limit.'
r=dict(id=17,user=dict(login=reader.BOT),commit_id='a'*40,submitted_at='2026-10-27T00:00:00Z',body=body)
code,printed=reader.state('o/r','1',call=lambda *a:dict(headRefOid='a'*40),pages=lambda path:[r] if path.endswith('/reviews') else [])
assert code==5
ok='Second reviewer: copilot because review rules.\ncopilot not run: "'+reader.quote(body)+'"; answer=review:17\nCopilot retry: available when the Captain confirms quota is back.'
tests={'quoted refusal':([],ok,printed),'no quote':(['Copilot quote or answer id differs'],ok.replace(reader.quote(body),'quota'),printed),'no retry':(['Copilot retry offer missing'],ok.split('\nCopilot retry:')[0],printed),'no source':(['Copilot printed output missing or invalid'],ok,None),'wrong id':(['Copilot quote or answer id differs'],ok.replace('answer=review:17','answer=review:18'),printed)}
for name,(want,text,source) in tests.items():
 got=proposed('',text,printed=source);assert got==want,(name,got,want)
print('CONTROLS',len(tests),'passed','READER',code,printed)
```

## Stage Report: ideation

- DONE: A design for /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/delivery_gate.py to refuse a merge ask that lacks the second-reviewer line when the README's trigger holds, and a copilot not run line without the quote /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/extensions/copilot/copilot_review.py printed and a retry offer, replayed over the saved merge asks under merge/ in this workflow's tasks
  Current 0.32.0 at origin/main 8bf4f358; actual question/check each accept absent-declaration and quota-only controls. Embedded replay ran from this task: 71 records, 65 unique text matches, 6 unknown; 62/3 baseline pass/hold becomes 15/50 in the design probe (47 changes). Five real-reader/probe controls pass; removing declaration or quote/offer checks loses the corresponding counterexample.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (archive-waits-for-observer-report, idle-hook-names-merged-tasks-without-learn, copilot-not-run-line-carries-quote, dispatch-carries-reserved-adr-number, seed-check-requires-schema-fields, journey-probe-finds-nested-maps, read-adr-honors-adr-folder) and live task of other sessions (adr-required-statement, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Batch overlap names all 14 requested tasks and all three proposed files. comment-check-reaches-delivery-gate shares the checker/tests but its body says Closed; adr-required-statement is also Closed. No sibling file changed.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Lifecycle table counts full stated instruction/output bundles with len(text.split()); baseline fixtures rerun. Startup 5775, open idle 1045, merged idle 1318, archive 3276, no-Copilot merge 742 unchanged; Copilot-read merge 1482 to projected 1518. No workflow/CI edit; per-PR CI cost unmeasured.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 through AC-8 each state evidence and a falsifier. One unresolved decision recommends shared question/check enforcement plus retained reader stdout; cost and authenticity/semantic limits are explicit. design_surfaces.py: design surfaces presentable (exit 0); Mermaid 12.0.0 render succeeded, with retry routed back through the gate.

### Acceptance evidence

- AC-1: absent/malformed declaration measured in corpus and baseline CLI; proposed prod/db/config CLI integration not implemented.
- AC-2: reader exit-5 formatter plus exact/altered/missing-source/wrong-id probe exercised; Unicode/empty/full CLI matrix remains future proof.
- AC-3: removed-offer counterexample rejected by probe; request-side-effect and negative-wording CLI assertions remain future proof.
- AC-4: live local adopter configs and reader/extension contract checked; adjacent-outcome integration matrix remains future proof.
- AC-5: program extracted from the entity and rerun reproduces 71/65/6, 47 changed and five controls; original transient ask bytes and GitHub delivery verdicts cannot be reconstructed from this alone.
- AC-6: actual baseline question/check controls executed behind the existing stub GitHub fixture; candidate integration, no-new-record and README/folder cases remain future proof.
- AC-7: named archived fixture rerun against installed 0.32.0; all baseline counts measured, after counts are projections. A candidate recount must include data-dependent output and new failure branches.
- AC-8: surface check passed and diagram rendered; original 44-line task prefix preserved byte-for-byte and path-scoped diff check passed. No product edits, branch, PR or new agent.

### Summary

Designed a shared delivery-text repair with a declared saved-output input, one conditional retry offer and explicit limits; the two reported omissions reproduce on the current package. The Captain still decides the recommended enforcement/source choice; implementation, live provider verification and approval remain future work, and the GitHub API returned `error connecting to api.github.com`.
