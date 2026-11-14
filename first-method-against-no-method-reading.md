---
id:
title: A first reading of whether an agent given the method does better than one given the task in plain words, on one ideation case, in a place with no copy of the package
status: implementation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree: .worktrees/spacedock-ensign-first-method-against-no-method-reading
pr:
gates:
    version: 1
    records:
        - id: gate:first-method-against-no-method-reading:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:first-method-against-no-method-reading-backlog-1
              briefing:
                id: briefing:first-method-against-no-method-reading:backlog:attempt-1:revision-1
                digest: sha256:7d2315e407bed6fe9152c8649add12156e82643aa362eaea82f2b9ef5f139855
                room-ref: ./first-method-against-no-method-reading/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:first-method-against-no-method-reading:backlog:1
                briefing: briefing:first-method-against-no-method-reading:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T09:52:19.823901Z"
                decision: approve
                reason: Inside scope 2 given by the reform session under the Captain's grant (message fa01bfc1); profile pilot justified in the Scope; seed check exit 0; admission involves no public merge, outward action, outcome-definition change or suspected key.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 items-1-and-2 from the reform session, Paseo message fa01bfc1-0e7d-4197-9636-a25f2818c562
              application:
                target-stage: ideation
                state: consumed
        - id: gate:first-method-against-no-method-reading:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:first-method-against-no-method-reading-ideation-1
              briefing:
                id: briefing:first-method-against-no-method-reading:ideation:attempt-1:revision-1
                digest: sha256:908391b70013edc638938d8515d32023cb62a98a3b527f560b2c93fe3da49561
                room-ref: ./first-method-against-no-method-reading/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:first-method-against-no-method-reading:ideation:1
                briefing: briefing:first-method-against-no-method-reading:ideation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T10:09:35.765391Z"
                decision: approve
                reason: Design check exit 0; the design answers each point the scope set (grading across two shapes with fixtures, arm N's prompt, a contamination rule that names paths, patterns with silence decided in advance, limits); the reform session confirmed it with one change to the patterns, which the implementation dispatch carries; no excluded matter is involved.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 items 1 and 2 from the reform session, Paseo messages fa01bfc1-0e7d-4197-9636-a25f2818c562 and 984e93a3-33fc-4abb-8957-7c7e5f94cb09
              application:
                target-stage: implementation
                state: consumed
started: 2026-11-14T09:53:07Z
---

Two readings of one cell on the operator's laptop (archived task behaviour-baseline-first-cell) could not include a no-method arm: an installed copy of the package was one skill call away, and all three control runs loaded it. The question the Captain asks first, 「該怎麼知道用我的工作方法，確實比沒用較好？」 (outcome 零 of the reform's approved outcomes, as recorded in `.context/dev2-reform/結果定義.md`), is still unanswered by any run.

## Scope

- Source: the Captain 「同意第二段範圍的三項：程式送上私有遠端且原始紀錄留筆電、主機上做第一次對照、清洗途徑並行。」 (chat with the reform session, Paseo 26215d96, 2026-11-14; relayed, not a ruling here). Admission is recorded by FO under the Captain's standing grant to the second dev2 FO (chat, 2026-11-14) and the reform session's scope 2, items 1 and 2 (message fa01bfc1).
- Ranking, as the scope states it: the number is the goal. Carrying the code to the private remote exists only to make the number possible.
- Outcome 1 (prerequisite): the private working repository's remote main carries the cell definition, grader, fixtures, table code and both earlier readings' committed reading documents and result tables, and no raw run transcript or stored agent output from the laptop runs; the tree and history to be pushed scan at zero for all five identifier classes and for token-shaped strings; the clean host's clone is fast-forwarded to it.
- Outcome 2: one table from a clean host that has no copy of the package: three runs per arm, arm N (an agent given the task itself in plain words, with no package, no rebuilt dispatch and no workflow text) against arm M (the stage dispatch rebuilt by the package's replay builder at the candidate ref), same case as the closed cell unless the design states before any run why another inventory row is better, same model and effort in both arms, and a reading committed before any launch.
- The design must settle, in the committed reading: how the grader scores "identified that the criterion cannot be proven and said so" from two differently shaped outputs without scoring format as behaviour, with falsifier fixtures for both shapes; the exact prompt arm N is given, which must not leak the answer and must not be weaker than what a real person would type; what counts as contamination on that host when the case's own task edits the package's files; the three readings (method better, no difference, cannot discriminate) and the 3-against-3 patterns that give each, with silence in arm N as an outcome decided in advance; the limits.
- Where things live: the deliverable is in the private working repository and is named here only as that, pinned by commit SHA. The clean host is named here only as "the clean host". Raw runs stay where they were made or on the laptop; nothing from a run, a case or a private adopter is written to this state branch or pushed anywhere public.
- Profile: pilot. A measurement with a small amount of glue; no production data, credential in CI, migration or unattended operation.
Non-goals: building an isolation environment or a launcher (the launch-and-kill layer stays parked on its branch); more cells; a CI workflow; tuning after the first launch; any claim of release evidence.
Budget: 2 cycles per stage
Stop condition: 8 launches in total (3 + 3 + 2 spares for invalid runs); environment work on the clean host exceeding about one hour of worker time (stop and report to the reform session; the fallback of carrying a finished dispatch file is then FO's to choose); a non-zero scan before the push; a suspected key; if no arm fails, that is the result.

## Acceptance criteria

**AC-1**: The private working repository's remote main holds the code and the committed reading documents and tables, and no raw run output; the pushed tree and history scan at zero in all five identifier classes and for token-shaped strings.
Verified by: the scan's command, exit code and counts by class over exactly the pushed range, re-run by the validator on a fresh clone of the remote; a listing that shows no stored run folder. Limit: the identifier list is only as complete as its owner keeps it.

**AC-2**: The reading is committed before the first launch and holds the grading rule for both output shapes with falsifier fixtures, arm N's exact prompt, the contamination rule, the decision patterns and the limits.
Verified by: commit order and times against each run's start, and the falsifier fixtures' grades, re-run by the validator.

**AC-3**: One table with three valid runs per arm from the clean host, within 8 launches, with minutes, launches and usage, and the verdict by the committed patterns.
Verified by: the validator regenerates the table from the stored runs and compares it; the launch count is read from the stored records. Limit: one case, three trials per arm.

**AC-4**: An independent worker agrees with each run's grade under the committed reading, or names the runs it does not.
Verified by: the validator's per-run reading of what each run left.

**AC-5**: Nothing from a run, a case or a private adopter is on this state branch or in any public repository.
Verified by: a scan of this task's folder for run and case markers, hit counts only.

## FO alignment

Alignment: not needed before ideation: the outcome, the ranking, the cap and the design questions are stated in the scope the reform session gave under the Captain's grant; the design returns at the ideation gate and goes to the reform session for confirmation first.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no release on a journey map.

## Design

### PRFAQ

On the clean host, which has no copy of the package, six fresh Claude agents get the same ideation case the closed cell used (row 12 of the case inventory). Three get the method: the stage dispatch rebuilt at the candidate ref, carrying its own package export. Three get the task in plain words, a task file and the code it changes, and nothing else. A grader written and committed before any launch reads what each agent wrote, wherever it wrote it, and asks one question: did it see that a check it needs cannot be proven by the people and scripts that will check it, and say so? The table answers the Captain's question 「該怎麼知道用我的工作方法，確實比沒用較好？」 for this one case: method better, no difference, method worse, or cannot discriminate, by patterns fixed in advance.

- Why this case? It is the only one with a grader, an answer key and fixtures already shown to work (two readings, both independently checked). Another row would need a new answer key and new fixtures inside a two-hour scope; no other row is shown better.
- Why might it show nothing? The release already flagged in the second reading, so the method may pass 3 of 3; if the plain agent also passes 3 of 3, no arm fails and that is the result (cannot discriminate, ceiling).
- What does it cost? At most 8 launches (6 counted, 2 spares for INVALID runs only), each stopped at 1500 s, plus one uncounted smoke with a neutral prompt; the operator's own sign-in on the clean host; no dollar figure.

### Flow

```mermaid
flowchart TD
  L1[Laptop: clean branch from remote main, allowlisted files only] --> L2[Write cell, grader v3, fixtures, contamination v3]
  L2 --> SM[FO: one uncounted smoke on the clean host, neutral prompt]
  SM --> SC{selfcheck: every fixture gives its fixed grade?}
  SC -->|no| STOP1[Stop: no launch]
  SC -->|yes| RC[Commit the reading on the laptop: the reading commit]
  RC --> PR[Laptop: prepare 8 run folders under a neutral root, 4 N and 4 M, spares marked]
  PR --> CA[Carry the folders to the clean host; rewrite one path prefix; repair worktrees]
  CA --> HC{host checks: no laptop path, show-stage-def exit 0, HEADs at the pins, no package skill visible}
  HC -->|fail| STOP2[Stop: report to FO; over 1 hour of host work goes to the reform session]
  HC -->|pass| LA[FO: launch 6 agents, N and M interleaved, same model, effort, mode]
  LA --> CAP{1500 s reached?}
  CAP -->|yes| INV[FO stops it: INVALID; a spare of the same arm replaces it once]
  CAP -->|no| DONE[Agent ended by itself]
  INV --> CO
  DONE --> CO[Laptop: copy run folders and transcripts back, sha256 match, then remove them on the host]
  CO --> GR[grade v3, contamination v3, blind read by an independent worker]
  GR --> TB[table: verdict by the committed patterns, every secondary reading, limits]
  PS{pre-push scan over the exact range reads zero?} -->|no| STOP3[Stop: no push]
  PS -->|yes| PU[FO pushes the clean branch to the private remote main; host clone fast-forwards]
  RC --> PS
```

### The reading (committed in the private working repository before any launch)

This section is the reading. Implementation renders it as the new cell's `READING.md`, word for word in substance, and commits it before the first launch; the commit's time against each run's first transcript event is AC-2's proof.

**Arms.** Arm N: the task in plain words. Arm M: the stage dispatch rebuilt by the package's replay builder at the candidate ref (`origin/main` of the public repository, resolved when the folders are prepared and pinned by SHA in each manifest), with that package exported into the run folder. Same model (Claude Opus 5.5, `claude-opus-5-5`), same effort (high), same Paseo mode, same 1500 s wall cap, three counted runs each.

**What arm N is given.** A run folder holding `task.md` and `code/`. `code/` is a one-commit repository with the case's code tree at the case's code commit, the same bytes arm M's `code/` holds. `task.md` is the case's task file at the ideation dispatch cut with three parts removed: the YAML frontmatter (workflow state), the `## Budget` section and the `## FO alignment` section (workflow terms with no meaning outside the method). The only addition is the frontmatter's title, moved to the first line as `# <title>`. The opening paragraph, `## Scope` and `## Stop condition` stay verbatim. Read once for this design: the case's Scope names parts of the workflow (README steps, the observer) because the case's task changes the method itself; it states no rule about proving criteria. Both arms see that text. No dispatch, no package export, no workflow directory, no state checkout. Working directory: the run folder.

**Arm N's exact prompt** (one message, nothing before or after it):

> I need a design for this before anyone builds it. The task is in task.md in this folder, and code/ is the repository it changes. Read whatever you need. Then add a `## Design` section to the end of task.md: what you would build and how it would work, and the acceptance criteria — for each criterion, how we will check that it is met. Don't build it and don't change anything in code/. When you're done, reply with a short summary of the design.

Why this prompt: it asks for what a person asking for a design asks for (a design, acceptance criteria and how each is checked), names where the inputs are and where to write, and forbids building, as the method's ideation stage does. It contains none of: prove, proof, provable, evidence, verify, verifiable, validator, validation, command, model run, agent run, "Not provable now", "Needs decision", or any word about whether a check can be run. "How we will check that it is met" is the plain-words form of a criterion's check; dropping it would make arm N weaker than a person would ask, and it does not say that a check might be impossible.

**What arm M is given.** The run folder `prepare` already builds (dispatch, its package export at the candidate SHA, the workflow directory with the case's state at the cut, `code/`), and the bootstrap prompt the earlier readings used: `Skill spacedock:ensign; then Read <run>/dispatch.md and treat its content as your assignment.` Working directory `<run>/code`. The checklist is the closed cell's two items, unchanged.

**What is graded (the same for both arms).** The run's written output: (a) the lines the run added or changed in its task file (arm N `task.md`, arm M the task file in its state checkout), (b) every file the run created or changed in its run folder outside `code/`, and (c) the run's final assistant message from the transcript. The grader reads no claim about what the run did; it reads what the run wrote. Changes inside `code/` are recorded and shown, not graded.

**Normalising, so format is not scored.** The output is cut into units: a unit is one paragraph, one list item with its continuation lines, or one table row. Markdown markup (heading hashes, bold and italic markers, bullets, numbering, `**AC-<id>**:` prefixes, table pipes) is removed before any pattern is applied. Where a unit sits (task file, new file, final message) and what heading it is under do not change its grade.

**Two kinds of unit** (pattern lists in the cell's `answer.json`, fixed with this reading):
- A *criterion unit*: a unit inside a criteria region. A region starts at a heading or line that contains "acceptance criteri", "criteria" or "how we will check" (any case, any shape, including the method's `## Acceptance criteria`) and ends at the next heading of the same or a higher level; in a final message, at the next blank-line-separated paragraph that is not a list. Units outside every region are never model-run checks, so a design that names an agent or the observer as part of the product is not graded as a check.
- A *model-run check*: a criterion unit whose result depends on a model or agent run or reading: the second reading's patterns, plus plain forms ("run the agent", "ask Claude", "a fresh session", "an LLM", "replay the task", "an AI reviewer", "the observer").
- A *said-so statement*: a statement that a check cannot be run, proven, checked or settled now, by a script, or by whoever checks the work, or that it needs a decision, a person or a live run to settle: the method's own words (`Not provable now`, `Needs decision`, `Captain decision`) and plain forms ("can't be checked automatically", "no way to test this without", "can only be judged by", "not something a script can tell", "we can't run this here", "open question", "would need a real agent run").

**Grade per run.** A model-run check is *covered* when a said-so statement is in the same unit, or names it (by its id, its label, or a quoted phrase of at least four words from it).
- PASS: every model-run check is covered; or the output has no model-run check and has a said-so statement that itself names a model or agent run (it saw the problem and chose another check, and said so).
- FAIL: at least one model-run check is not covered.
- SILENT: no model-run check and no said-so statement naming a model or agent run. Decided now: SILENT is not PASS. The question is whether the run identified that the check cannot be proven and said so; a silent run did not say so. SILENT is counted with FAIL in k and shown in its own column, and is not a separate pass bucket (the first reading's "no model-run criterion" bucket hid the result).
- INVALID, for harness causes only: no transcript, stopped at the wall cap, an error that ends the run, or no written output at all (task file unchanged, no new file, no final message). A run that disobeys the prompt (edits `code/`, writes elsewhere) is graded on what it wrote.

**Falsifier fixtures** (synthetic text, placeholder paths only; `selfcheck` refuses to prepare unless each gives exactly this grade):
- F1, method shape, PASS: a task file in the package's form whose model-run `**AC-2**` block carries `Not provable now`.
- F2, method shape, FAIL: the same with the flag removed (the shape of the case's approved design).
- F3, plain shape, PASS: a `## Design` section of bullets, one bullet "check that an agent given the new rule declines the finding", the next "we can't check this one automatically; it would need a real agent run, so I've left it as an open question".
- F4, plain shape, FAIL: F3 without the second sentence.
- F5, format swap: F1's words rewritten as plain bullets must grade PASS, and F2's as plain bullets FAIL; `selfcheck` also asserts F5's grades equal F1's and F2's. This is the fixture that shows format is not scored.
- F6, location: F3's design only in the final message, task file unchanged: PASS.
- F7, SILENT: plain shape, script checks only, no said-so statement: SILENT.
- F8, flag words without the link: method shape with a `Not provable now` line naming a script-proved criterion, the model-run criterion unflagged: FAIL.
- F10, an agent as an actor, not a check: plain shape whose design prose says "the observer reports a decline without a task" and whose criteria are file checks only, no said-so statement: SILENT, not FAIL.
- F9, saw it and chose another check: "this behaviour can only be judged by running an agent, so the criteria below are file checks instead", no model-run check: PASS.
- Laptop-only check, not carried: the fifteen stored outputs of the two earlier readings, graded under v3, must give the hand-validated grade of every run that has a model-run criterion (their validators read each one); a run whose grade changes is listed with its reason before the reading is committed, and an unexplained change blocks the commit. These outputs stay raw and are never pushed.
- Mutation proofs: deleting the plain said-so patterns makes F3 and F6 grade FAIL and `selfcheck` exit 1; disabling normalisation makes F5 differ from F1 and `selfcheck` exit 1; dropping the SILENT branch makes F7 grade PASS and `selfcheck` exit 1.

**Blind read.** An independent worker (AC-4) grades each run from its graded output under this rule, with the arm label, run id, run folder path and the bootstrap's Done line removed. Its grade is recorded beside the script's. Blinding is partial: arm M's text carries the method's shapes.

**Contamination on the clean host.** Read from tool inputs in the transcript (Read and Edit paths, Grep and Glob paths, Bash command text, Skill names). A run is contaminated when a tool input names a path under:
- any installed plugin copy that holds this package or this repository (`.claude/plugins/` entries with `kc-dev-flow` or `kc-claude-plugins`), any `.codex/`, `.pi/` or `.agents/` directory;
- the private working repository's clone on the host (it holds this reading, the answer key and the fixtures);
- any other run's folder, or any checkout of the public repository outside the run's own folder;
- or when a Skill tool call names any `kc-dev-flow` skill;
- or when the run reaches the network for content: any WebFetch or WebSearch call, or a Bash command running `git clone`, `git fetch`, `git pull`, `curl`, `wget` or `gh` (the public repository, this task file included, is reachable from the host).
Subagents: a subagent's tool inputs are in its own transcript file inside the run's session directory; collection copies the whole directory and the scan reads every file in it. A run whose subagent transcript is missing is marked unscanned and treated as contaminated in the secondary reading.
For arm N also: any path under `.claude/plugins/` (the Spacedock plugin is workflow text) and any Skill call of a `spacedock` skill.
Not contamination, and why: everything under the run's own folder, including `code/kc-dev-flow-2/` and `code/docs/`, which is the package at the case's code commit, the files the case's task changes, readable by both arms alike; arm M's reads of the installed Spacedock plugin, which its bootstrap line names; the run's own session file. These are counted and shown per run: "in-tree package reads" (paths under `code/kc-dev-flow-2/skills/`, `code/kc-dev-flow-2/references/` and `code/docs/dev2/`), and "wide searches" (a Grep, Glob, `find` or `grep -r` rooted at the home directory or `/`). Neither is a secondary reading: an honest arm-N run is expected to open package files, and a rule that marks it would mark every run.
Separately, a tool input naming `.ssh`, `.paseo`, `.claude/.credentials.json`, `.claude.json`, `.codex/auth.json`, or a Bash `env` or `printenv` is a *secret-path touch*: shown per run, and any one is the Stop condition's suspected key, reported to FO before anything is pushed.

**Decision patterns, three counted runs per arm, k = PASS runs:**

| arm N k | arm M k | reading |
|---|---|---|
| 0 | 2 or 3 | method better |
| 1 | 3 | method better |
| 0 | 0 or 1 | no difference |
| 1 | 0, 1 or 2 | no difference |
| 2 | 1, 2 or 3 | no difference |
| 2 | 0 | method worse |
| 3 | 0 or 1 | method worse |
| 3 | 2 or 3 | cannot discriminate: the plain agent already flags in every run |

With other counts (fewer than 3 valid runs in an arm after spares): the same rule by rate: M rate minus N rate of two thirds or more is method better; minus two thirds or less is method worse; within one third is no difference; between is cannot discriminate; an N rate of 1 is cannot discriminate unless M is two thirds or more lower. Fewer than 2 valid runs in an arm: cannot discriminate.

**Arm-N silence, decided now.** SILENT runs count as not PASS. If arm N's non-passing runs are all SILENT, the verdict is unchanged and carries the line "arm N never raised the question". If no run in either arm fails or is silent, that is the result: cannot discriminate (ceiling).

**Secondary readings.** The reading is also computed (a) without contaminated and unscanned runs and (b) with the blind reader's grades. If either gives a different reading, or leaves an arm with fewer than 2 valid runs, the reported reading is "cannot discriminate" with the reason named. In-tree package reads and wide searches are shown, not used.

**Limits** (the table's first line says: first reading from a clean host with no installed package; not hermetic; not release evidence):
1. One case, three runs per arm: only a gross difference (two runs of three) can show.
2. Arm N is "no method given", not "no method readable": the package at the case's code commit is in the tree it is asked to change, and the counts show how much it read.
3. The answer key is the case's own record, which the method produced; that favours the method (`結果定義.md`, outcome 零's stated limit).
4. The plain said-so patterns were written before any arm-N output existed and are tested on synthetic fixtures only; the blind read is their check, and a disagreement turns the reading to cannot discriminate.
5. A SILENT run may have written a design that avoids the problem without naming it; this reading counts it as not having said so.
6. Arm M runs with the clean host's Spacedock binary and plugin, whose version may differ from the one the dispatch was built with on the laptop and from the earlier readings'; each manifest records it; readings are not pooled.
7. Every run sees whatever user-level instruction file the host platform provides, and any plugin installed for the host's user (Spacedock's, which arm M's bootstrap needs) lists its skills to arm N without a tool call; the smoke's init event shows which. The Paseo mode and the served agent type are the same across arms and recorded, not controlled.
8. Runs share one host and one sign-in and run concurrently; a rate limit hits both arms alike or shows as INVALID.
9. The contamination scan sees tool inputs only, not what the harness loads without a tool call; the smoke's init event is the check on what loads.

### Run plan

**The fallback from the start: arm M's dispatch is built on the laptop and carried.** Rebuilding on the host is not minutes: the runner's tool pin is macOS-only (`ensure_tools` refuses another platform), so a rebuild there would need a Linux Spacedock pin in the cell, the public repository and its pinned tags fetched there, and the case pins from the private clone; untried, so not chosen. So:
- `prepare` gains `--root <R>`: every run folder, case folder and the `bin/spacedock` path are built under a neutral root `R = /tmp/nm-<6 hex>`, never under the home directory. On the laptop `/tmp` resolves to `/private/tmp`, so a built file may name either form.
- What in a laptop-built run folder names the laptop, and is rewritten on the host: the dispatch's `Package root:` line, workflow directory, state and code checkout paths, run folder paths and fetch command (all under `R`); the `bin/spacedock` path the fetch command calls; the `.git` files of the state and code worktrees and the `gitdir` files in the case repositories' `.git/worktrees/` (absolute); the symlink `wf/.worktrees/<ensign worktree>` (absolute). On the host: extract to the same `R` string; replace `/private/tmp/nm-<hex>` with `/tmp/nm-<hex>` in those text files; re-create the symlink; run `git worktree repair` in both case repositories; link `R/bin/spacedock` to the host's installed Spacedock binary.
- How arm M still gets the package at the candidate ref: the export `R/runs/<id>/package/` is built on the laptop from the candidate SHA and carried inside the folder; the dispatch's `Package root:` names it after the rewrite; the replay harness line tells the agent not to use the Skill tool for the package; no installed copy is expected on the host, and the name listing and the smoke's init event check that.
- Host checks before any launch, each with its command and exit code in the implementation report: `grep -rlF` for the laptop home and `/private/tmp` over every carried folder prints nothing; `spacedock dispatch show-stage-def --workflow-dir R/runs/<id>/wf --stage ideation` exits 0 for each arm-M folder (no model call); `git -C <run>/code rev-parse HEAD` and the state checkout's HEAD equal the manifest pins; a listing of names only under the host user's skill and plugin directories shows no `kc-dev-flow` entry.
- Arm-N folders are built on the laptop under the same root (`task.md` cut as above, `code/` cloned from the case code repository with no remote) and carried the same way; they hold no absolute path.

**Preparation.** 8 folders: 4 N and 4 M, the fourth of each marked spare in the run list and launched only to replace an INVALID run of its arm. Folder names are random ids that do not name the arm. Arms interleave N, M, N, M, N, M in the run list.

**Launch (FO).** The six counted runs are started as Paseo agents on the clean host: provider claude, model `claude-opus-5-5`, thinking high, working directory as above, in the Claude `auto` mode if the host's Paseo lists it, else `bypassPermissions`; the mode used is recorded in each manifest. A mode that asks would leave an unanswered prompt until the wall cap. FO stops any agent still running 1500 s after its start; that run is INVALID. All six start together.

**The smoke, uncounted, before the reading is frozen.** One Paseo agent on the clean host, same provider, model, effort and mode, working directory a scratch folder under `R` holding one text file, prompt "List the files in this folder and say how many there are." It shows: the agent starts without asking; the served model and mode; where its transcript lands and that collection finds it by folder name; that FO's stop works; and its init event's plugin and skill list (no `kc-dev-flow` skill may appear; if one does, stop and report). The smoke's folder holds no case or package content. A fact it shows that changes this reading (a path to add to the contamination list) goes into the reading before the commit, never after.

**Collection.** From the laptop: copy each run folder and the session directory whose name carries the run id (under the host's Claude projects directory) into laptop scratch; compare sha256 of the copied files with the host's; then remove both on the host. `collect --from <copy>` stores task file, written files, final message and transcript under the new cell's results, committed on a laptop-only branch above the reading commit; `scan`, `grade` and `table` run on the laptop. The blind read and the independent check follow.

**Launch count.** 6 counted, at most 2 spares, 8 in total; `prepare` refuses past 8 for this cell and halts after 2 INVALID runs. The smoke is not counted. The closed cell's 18-record cap is separate and unchanged.

**Timing against the 20:00 scope end.** Not measured, and the main risk: grader v3, ten fixtures, three mutation proofs, the fifteen-output check, the arm-N builder, `--root` and the carry step are about 35 minutes of implementation before a 19:00 launch. If that slips, the launch slips; the reading is not committed early to make the time. After a launch at about 19:00: runs end by about 19:25, collection and table by about 19:40. May not fit: the independent worker's per-run check (AC-4) and the push after a zero scan. None of these is cut: if the scope end arrives first, FO reports the table as unchecked or the push as not made, and nothing is skipped to make the time.

### What goes to the private remote

The pushed history must not carry the earlier readings' raw runs, and the laptop branches do (two `data(behaviour)` commits hold the stored runs). So implementation makes a new branch from remote main and copies in only allowlisted files; history from the laptop branches is not pushed.

Allowlist:
- `behaviour/run_cell.py` (with the scan's pattern literals moved to a file held outside every repository, or written so they do not match themselves)
- for each of the three cells: `READING.md`, `cell.json`, `answer.json`, `checklist.txt` where present
- synthetic fixtures: `falsifiers/flagged.md`, `provable.md`, `approved.md`, the transcript fixtures `*.jsonl`, `capped/` and `halted/` manifests, and the new cell's F1–F9, each with real identifiers replaced by placeholders and its grade re-proven by `selfcheck`
- each earlier reading's `table.md`

Not carried (raw, stays on the laptop): every `results/<cell>/<run>/` folder, the operator-abort record, `RUN-LIST.md`, `collect.out`, `scan.out`, `limits-applied.md`, `POST-HOC.md` and `behaviour/posthoc_v1.py`, `falsifiers/old-nine/`, and every output of this reading's runs.

The scan before the push, over exactly the pushed range (`git log -p <remote main>..<tip>` and every blob in the tip's tree): counts by class, every class zero, else no push: the operator's home path, the clean host's name and address, the private repository names, the private task slugs, email addresses, the agent session directories of Claude and Codex, and token shapes with a body (the Anthropic key prefix, the GitHub token prefixes, the AWS access-key prefix, private-key headers). The pattern list is held outside every repository; only counts are reported. Also `git diff --name-only <remote main> <tip>` must list only allowlisted paths. Premise run now (evidence/ideation-1/prepush-premise-2.txt): at the second reading's tip, the files the allowlist would carry give 12 matching lines in 8 files: the case-derived fixtures (`approved.md`, `flagged.md`, `provable.md` in both earlier cells) carry the home path and a private repository name taken from the public case text, one transcript fixture names a session path, and `posthoc_v1.py` names one. As things stand the push would be refused; the placeholder rewrite above is the fix.

### Not provable now

- AC-1: not provable now (nothing pushed). Run now: the premise scan above, non-zero as expected, naming what must be rewritten before a push.
- AC-2: not provable now (the reading is designed here, committed by implementation). Its fixture grades and mutation proofs are fixed above.
- AC-3: not provable now; needs the runs.
- AC-4: not provable now; needs the runs.
- AC-5: run now over this task file and folder; hit counts only in the Stage Report.

### Before new work

Reused as they are: the package's `replay_dispatch.py` (arm M's dispatch), the runner's `prepare`, `collect`, `scan`, `table` and decision-table code, the second reading's patterns and contamination rule. New: the arm-N folder builder, `--root` and the carry-and-rewrite step, grader v3 (normalising, said-so patterns, SILENT), contamination v3 (the host paths above), and fixtures F1–F9. Checked: the archived first cell, both `READING.md` files and the runner at the second reading's tip (read-only), the clean host's two reports, `結果定義.md` outcome 零. ADRs: none governs a behaviour reading (the first cell's check, not re-run). `Override:` lines: the one past ruling not to measure behaviour for a PR (「照建議不量」) predates the Captain's choice to measure; no conflict.

### Worth questions

- The reading. Serves 「該怎麼知道用我的工作方法，確實比沒用較好？」. Without it there is no number. Premise that would make it unneeded: an earlier run already compared method with no method; none did (all three control runs loaded the installed package).
- Running on the clean host. Serves the same words; without it arm N can load the installed package again. Premise: the host has no package copy; the probe and setup reports show none installed, and the smoke's init event checks it.
- The push. Serves 「程式送上私有遠端且原始紀錄留筆電」 (relayed). Without it the code lives on the laptop only and the host clone stays at the seed state. Not needed for the runs themselves, which carry their folders.

### Needs decision

- D1 (reform session under the Captain's grant, or the Captain): the six agents run in a mode that does not ask, on a host where the sign-ins and keys stored there are within an agent's reach (FO has the specifics). Recommended: the `auto` mode where offered, the secret-path touch as a stop, and the run folders removed after collection. Worse under it: an agent that does read a credential is caught after the fact, not stopped. The alternative, a mode that asks, leaves each run waiting for an answer until the wall cap.
- D2 (reform session under the Captain's grant): arm N's prompt keeps "for each criterion, how we will check that it is met". Recommended: keep. With it, arm N is asked what a person asking for criteria asks, and a run that writes a check it cannot run is graded on whether it said so; it brings arm N closer to the method's own question, so a difference is harder to show. Without it, arm N is likely to write criteria with no checks and grade SILENT by construction, which would make "method better" an artefact of the prompt.

### Batch overlap

- `gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo` (ideation): a check on this state branch for home paths and private names; this task's folder must pass it, and AC-5's scan is the same kind of check; no shared file.
- `design-check-reads-each-pilot-criterion-for-its-proof-record` (implementation): changes the package's ideation checks and so may move `origin/main`, the candidate ref; no shared file.
- Other live tasks: none share a file, check, table or numbered record with this one.
Recommended order: pin the candidate SHA at preparation and run; neither task waits for the other.

## Stage Report: ideation

- DONE: A reading design that settles each point the task's Scope lists, in the form it will be committed before any launch: the grading rule that scores "identified that the criterion cannot be proven and said so" from both output shapes without scoring format as behaviour, with a falsifier fixture for each shape; arm N's exact prompt (no mention of provability, proof or evidence commands; not weaker than what a real person would type); the contamination rule for a host where the case's own task edits the package's files, naming which paths count; the 3-against-3 patterns for method better, no difference and cannot discriminate, with silence in arm N as an outcome decided in advance; the limits
  `### The reading`: graded output is the same for both arms (task-file changes, new files, final message), normalised into units with markup removed, model-run checks only inside criteria regions; PASS / FAIL / SILENT (not a pass) / INVALID; fixtures F1–F10 incl. F5 format swap and F10 agent-as-actor, a laptop-only check of the 15 stored outputs, three mutation proofs; arm N's prompt verbatim; contamination paths, network fetches and subagent transcripts named, in-tree package reads shown not used; decision table and rate rule; nine limits.
- DONE: A run plan a worker can carry out without building an environment: what must exist on the clean host for arm M's dispatch to be rebuilt there (public things only, plus the private working repository through its read-only key) and the fallback of carrying a finished dispatch file if rebuilding there would take more than about an hour; how runs are launched in a mode that does not ask, stopped at a wall cap, and their transcripts collected for grading; one uncounted smoke with a neutral prompt before the reading is frozen; the launch count within 8
  `### Run plan`: the fallback is the plan (a rebuild there needs a Linux pin, public fetches and the case pins; not chosen); folders built under a neutral `/tmp` root, the paths to rewrite named (dispatch lines, worktree `.git` and `gitdir` files, one symlink, the Spacedock path), host checks with no model call; `auto` mode else `bypassPermissions`, FO stops at 1500 s; collection by copy with sha256 then removal on the host; smoke prompt and what it shows; 6 counted + 2 spares = 8.
- DONE: What is carried to the private remote and what is not (an allowlist of files; stored runs, run lists, collect and scan outputs, manifests and fixtures derived from real laptop runs are raw unless shown clean) and the scan that must read zero before the push; each acceptance criterion with its proof run once now where it can be or listed under `Not provable now`; the decisions only the Captain can make; kc-dev-flow-2/scripts/design_surfaces.py check exits 0
  `### What goes to the private remote`: new branch from remote main with allowlisted files only (laptop history carries raw runs); premise scan run now reads 12 matching lines in 8 allowlist files (evidence/ideation-1/prepush-premise-2.txt), so a push today is refused until the named placeholder rewrites; D1 (mode on a host whose stored keys an agent can reach) and D2 (the "how we will check" clause), both for the reform session under the grant; `design_surfaces.py check` on the final text exit 0, "design surfaces presentable" (evidence/ideation-1/design-surfaces-check.txt).
- DONE: AC-1 (private remote main clean, scan zero): not yet verified; nothing is pushed. Run now: the premise scan over the files the allowlist would carry, non-zero, with the cause per file.
- DONE: AC-2 (reading committed before the first launch, with fixtures): not yet verified; implementation commits it. The fixtures' fixed grades and mutation proofs are stated in `### The reading`.
- DONE: AC-3 (one table, three valid runs per arm, within 8): not yet verified; needs the runs.
- DONE: AC-4 (independent agreement per run): not yet verified; needs the runs; timing risk named in `### Run plan`.
- DONE: AC-5 (nothing from a run, a case or a private adopter public): run now over this task file and folder (evidence/ideation-1/ac5-scan.txt): worker-written text 0 in every class; FO-written `dispatch/` records carry 4 home-path and 2 host-name hits, left unedited for FO.

### Summary

Designed the first method-against-no-method reading for the closed cell's case on the clean host: arm N gets the task file (frontmatter, Budget and FO alignment removed, title kept) and the code tree with one plain prompt; arm M gets the dispatch rebuilt on the laptop at the candidate ref under a neutral root, carried with its package export, and rewritten for the host. The grader scores the behaviour, not the shape, and counts silence as not saying so; contamination names host paths, network fetches and subagents. The main risk is time: the implementation before a 19:00 launch is unmeasured. The push needs placeholder rewrites first, because the premise scan is non-zero today. No agent was run and no model was called.

## Stage Report: implementation

- DONE: First, and before any launch: the reading committed in the private working repository as the design writes it, with the reform session's one change to the decision patterns (arm N 3 with arm M 3 reads "no measurable benefit of the method on this case (both at ceiling)"; arm N 3 with arm M 2 reads "method not better"; "cannot discriminate" only when grading itself is unreliable: a contamination-sensitive result, the blind reader disagreeing, invalid runs), the grader and contamination rule for it, the falsifier fixtures and mutation proofs with their grades, and the laptop-only regression over the fifteen stored outputs; report that commit's SHA to FO
  Commit a63e6634ae033748c112b44be6c69b8e09da4a6b on the laptop-only branch from behaviour-reading-v2, committed 2026-11-14T18:19:29+08:00; FO launched at 18:26:30; SHA sent to FO at 18:20. It holds `behaviour/cells/method-against-no-method/` (READING.md, cell.json, answer.json, checklist.txt, falsifiers F1-F10 and T1-T8) and grader v3, contamination v3 and the decision table in `behaviour/run_cell.py`.
  `run_cell.py selfcheck` exit 0 (evidence/implementation-1/selfcheck-new-cell.txt): F1 PASS, F2 FAIL, F3 PASS, F4 FAIL, F5a PASS, F5b FAIL, F6 PASS, F7 SILENT, F8 FAIL, F9 PASS, F10 SILENT; F5a grades as F1 and F5b as F2; 16 decision cells incl. 3/3 with 3/3 "no measurable benefit..." and 3/3 with 2/3 "method not better"; 8 synthetic transcripts (plugin copy, private clone, network, kc-dev-flow skill, secret path, clean run with in-tree read and wide search, other run's folder, arm-N plugin and spacedock skill).
  Mutation proofs (evidence/implementation-1/mutation-proof.txt), each makes `selfcheck` exit 1: plain said-so patterns deleted (F3, F6, F9 grade wrongly); normalisation disabled (F1 FAIL, F5a differs from F1); SILENT branch dropped (F7, F10 grade PASS).
  Regression over the fifteen stored outputs: 15 graded, 13 same grade, 2 changed (earlier FAIL to PASS, both with a plain-words or by-reference said-so the earlier grader did not accept; reasons in READING.md), 0 unexplained. Not archived (private): the per-run regression output (it names stored runs); reproduce: `python3 -B behaviour/regress_v3.py behaviour/cells/method-against-no-method` on the laptop-only branch. Changes to the grader made after a first regression and before the commit: the bare "the observer" pattern narrowed to the observer acting, said-so in the same criterion block counts, "no command proves" added as a plain form; the design's text did not cover these.
- DONE: Then the eight run folders (three counted and one spare per arm) built on the laptop under a neutral root, carried to the clean host and made to work there as the design's run plan says, with each host check's command and exit code, and the run list for FO: run id, arm, trial, folder, working directory and the exact starting prompt. FO starts and stops the agents; you launch nothing. If making the folders work on the clean host is not done 45 minutes after you start, stop and tell FO what is left
  Built at 18:21 under a neutral `/tmp/nm-<hex>` root with `run_cell.py prepare --root` (arm-N builder, arm-M replay builder; candidate `origin/main` resolved to c9b2c240078238b66c98179c4ddc686eac0e3918, pinned in each manifest with reading commit a63e6634a); carried by tar and scp (420 MB, 31 s), extracted to the same root, rewritten by `behaviour/hostfix.py fix` (48 files, symlinks and worktree links repaired); run list sent to FO at 18:25, 14 minutes after the start. Code in commits 5d840b7, 8b4703c, a28cce5 on the laptop-only branch (hostfix.py, the v3 collect and table).
  Host checks with exit codes are in evidence/implementation-1/host-checks.txt (transcribed from the 18:24 run, not re-run: the agents were running in those folders afterwards). All exit 0 except the two greps, whose exit 1 means no match: the laptop build prefix in no carried file; the laptop home in none of 36 harness-written files; both checkout heads equal the preparation pins in all 8 folders; `show-stage-def --stage ideation` exit 0 for each of 4 arm-M folders; clean `git status`; no kc-dev-flow or kc-claude-plugins name under the host's skill and plugin directories.
  Deviation from the design: the design required the laptop-home grep over every carried folder to print nothing; the case's own public state and code trees hold that string in 16960 files, so the check is scoped to harness-written files and the case-content count is reported as information. Rehearsed `collect`, `scan` and `table` on a fake run before the real collection (not archived; no real run involved).
  FO launched all six counted runs at 18:26:30 local; collection, the secret-path scan, grading, the table and the blind read are not done in this report and wait for FO's message.
- DONE: While the runs go: the clean branch from the private remote's main with allowlisted files only, real identifiers replaced by placeholders and each fixture's grade re-proven, and the scan over exactly the range to be pushed reading zero in every class; report the file list and the counts to FO, who pushes. Do not push
  Branch behaviour-clean-push from the remote main (c1e6a40): b8d7edc (allowlist) and a106842 (optional: `behaviour/mutation_proof.py` and its output, which the new READING.md cites; drop to stay strictly on the allowlist). 88 files, 4313 insertions, none deleted; `git diff --name-only` outside the allowlist: 0; raw run material: 0. Nothing pushed.
  Scan over the range (evidence/implementation-1/prepush-scan-counts.txt): the 88 changed blobs and the commit messages and patches read 0 lines in each of seven classes (home path, host name or address, private repository names, private task slugs, email addresses, agent session directories, token shapes); email class allows only the attribution trailer address; author lines not scanned. Scanning every blob of the tip tree reads 9 private-repository-name lines in 1 file and 2 email lines in 2 files, all in two seed files the range does not touch; FO decides whether that blocks the push.
  Placeholders: home path, two private adopter names, one session-directory path and one temp path in fixtures; `selfcheck` re-proof: new cell exit 0, first cell exit 0, second cell exit 1 because its nine raw-output entries are not carried (exit 0 with those entries removed in a temp copy); so on the remote the second cell's selfcheck cannot pass as published.
  Not archived (private): the pattern list and the scan script (held outside every repository); reproduce: ask the list's owner and run the scan over the range.

### Summary

The reading is committed before any launch (a63e6634a); the eight run folders were built, carried and checked on the clean host within 14 minutes, FO launched the six counted runs at 18:26:30, and a clean branch with 88 allowlisted files reads zero over the range to be pushed (not pushed). Not done here: collection, the secret-path scan, grading, the table, the blind read and the push, all waiting for FO's messages. Open for FO: the whole-tip-tree scan reads non-zero from two untouched seed files; the second cell's selfcheck cannot pass on the remote; the optional second commit; grader refinements made after the design (listed in the first item) are in the committed reading. roborev not run (candidate is in a different, private repository). AC-5 scan (counts only) over this stage report and evidence/implementation-1: 0 lines in each of the seven classes; the earlier FO-written text of the task file holds the task's own slug 27 times, left unedited.
