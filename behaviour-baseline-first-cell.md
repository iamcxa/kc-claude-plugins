---
id:
title: One local command runs a real agent on a rebuilt stage dispatch at the released and the candidate package, for one cell, and reports what each arm did
status: implementation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree: .worktrees/spacedock-ensign-behaviour-baseline-first-cell
pr:
gates:
    version: 1
    records:
        - id: gate:behaviour-baseline-first-cell:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:behaviour-baseline-first-cell-backlog-1
              briefing:
                id: briefing:behaviour-baseline-first-cell:backlog:attempt-1:revision-1
                digest: sha256:b5664e5209c5d2fac6204d5ca3778145ad19aafa70dfdaa2431d11c3afe2a0b8
                room-ref: ./behaviour-baseline-first-cell/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:behaviour-baseline-first-cell:backlog:1
                briefing: briefing:behaviour-baseline-first-cell:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T04:42:39.866073Z"
                decision: approve
                reason: Inside scope 1 item C given by the reform session under the Captain's grant; profile pilot justified in the Scope; seed check exit 0; no excluded matter (public merge, outward action, outcome definition, suspected key) is involved in admission.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 1 item C from the reform session, Paseo messages 6ee7ee5b-9ccc-4ef2-8cb6-35f25bfd4e1e and a8df76d7-63cb-4352-9c4b-f44b6004d7f5
              application:
                target-stage: ideation
                state: consumed
        - id: gate:behaviour-baseline-first-cell:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:behaviour-baseline-first-cell-ideation-1
              briefing:
                id: briefing:behaviour-baseline-first-cell:ideation:attempt-1:revision-1
                digest: sha256:9a3e4f21c2dfbc53d2e78f9dd0496eb5da10265d776a02899bdf5cc7090ea12f
                room-ref: ./behaviour-baseline-first-cell/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:behaviour-baseline-first-cell:ideation:1
                briefing: briefing:behaviour-baseline-first-cell:ideation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T05:05:55.363147Z"
                decision: approve
                reason: 'Design check exit 0; the design reuses the package''s replay builder, keeps case and run content off the public branch, stays inside the 18-run cap and the admitted scope; FO verified by git grep that the rule under test is present at the candidate and absent at the release. D1 (credential) is not decided here: it is the Captain''s and no paid run starts before he answers.'
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 1 item C from the reform session, Paseo messages 6ee7ee5b-9ccc-4ef2-8cb6-35f25bfd4e1e and a8df76d7-63cb-4352-9c4b-f44b6004d7f5
              application:
                target-stage: implementation
                state: consumed
started: 2026-11-14T04:43:45Z
---

The package has no check that runs a model and looks at what its instructions cause. An earlier attempt (task validation-reads-pr-review-comments) had 7 valid runs of 12, two runs at the 1800-second cap, and a base that already passed 3 of 3, so it could show nothing (figures from `.context/dev2-reform/改革總計劃.md`, not re-measured here).

## Scope

- Source: the Captain 「同意重建核心：先做行為基準，再從空白頁逐條准入，做成同一個套件的新版本，狀態一開始就放私有。」 (chat with the reform session, Paseo 26215d96, 2026-11-14; relayed, not a ruling here). Admission is recorded by FO under the Captain's grant to the second dev2 FO (chat, 2026-11-14) and the reform session's scope 1 item C. Design input: `.context/dev2-reform/behaviour-ci-design.md` sections B, C and D, a research output with its own stated limits.
- Outcome: a person can run one local command that rebuilds a real stage dispatch at two package refs (the last released tag and a candidate), runs a real agent on each in an isolated home, and reports per cell: base k/n, candidate k/n, the no-skill control, valid/n, minutes, tool calls, tokens and the model id as served. This task delivers the thin runner and ONE cell.
- Where the work lands: the private working repository, not this repository. This task file and its records refer to it only as "the private working repository" and pin it by commit SHA. Run evidence, case bundles and the result table stay there or outside any repository; nothing from a run, a case or a private adopter is written to this state branch, and nothing from that repository is pushed anywhere public.
- Reuse: the package's `scripts/replay_dispatch.py` builds the dispatch; the procedure text in the maintain-flow skill; Spacedock's isolation approach for its live tests as the model for an empty home and config directory. New code is the runner only: launch, hard stop, manifest, grade, table.
- First cell: ideation flags a criterion whose proof the validator cannot produce. Prefer a frozen public archived task cut before the record that caught it; plant a case only if none fits. Cases come from public package tasks on an allowlist.
- Rules for the cell: 3 trials per arm; a wall-clock cap and a tool-call cap per run, set and recorded before the first run; two invalid trials halt the cell; graded on artifacts the model cannot author (workspace bytes, commits, structured stage-report fields), never on its own claim; the transcript shows no read of an installed copy of the skill or of the operator's personal configuration; the model id as served, effort, package refs and Spacedock version are recorded.
- Spend: the operator's own login on this machine; no credential goes into CI; minutes, tool calls and tokens of the first run are recorded and no dollar figure is estimated.
- Profile: pilot. It adds a check at the release boundary of one package; no production data, credential in CI, migration or unattended operation.
Non-goals: the other seven cells; cloud replay; a CI workflow; First Officer behaviour journeys; deleting any existing test; carrying or proving resumable state (Spacedock's capability); tuning the cell until it shows a difference.
Budget: 2 cycles per stage
Stop condition: 18 paid agent runs in total including reruns; two invalid trials in the cell; the cell cannot be made to fail on any arm within the cap (that is a result: report it); the workflow's scripts would force run or case content onto this public branch; a suspected key is found.

## Acceptance criteria

All three arms of the cell run on one host (Claude), one model and effort, with the caps in `### First cell`; "the runner" is `behaviour/run_cell.py` in the private working repository, pinned by commit SHA in the implementation report.

**AC-1**: The one command produces, for one cell, a table with base k/n, candidate k/n, no-skill control, valid/n, minutes, tool calls, tokens and the model id as served, from real agent runs.
Verified by: at the pinned commit, `python3 behaviour/run_cell.py table behaviour/cells/ideation-flags-unprovable-criterion` re-grades every stored run (`grade` is called inside `table`) and prints the table; the validator compares it with the committed `table.md` byte for byte, and counts the run manifests (`ls behaviour/results/ideation-flags-unprovable-criterion/*/manifest.json | wc -l`) against the table's n and the 18-run cap. The model id comes from the stored stream (`message.model` and the result event's `modelUsage` keys), not from the requested alias. Limit: one cell, one host, 3 trials per arm.

**AC-2**: The cell is shown failing on at least one arm, or the report states it could not be made to fail within the cap, with the runs spent.
Verified by: for one FAIL trial, the validator reads its stored `task-after.md` and names the criterion the grader found unflagged, and `python3 behaviour/run_cell.py grade <run dir>` prints that criterion id; or, with no FAIL trial, the table's verdict reads `NO-FAIL` and the manifest count is at most 18.

**AC-3**: Each run was isolated: no read of an installed copy of the skill or of personal configuration appears in its transcript.
Verified by: `python3 behaviour/run_cell.py scan behaviour/cells/ideation-flags-unprovable-criterion` exits 0 and prints one line per run: (a) the stream's init event lists no plugin but the run's own exported Spacedock copy, no skill outside it and no MCP server; (b) no tool input or tool result in the transcript names the operator's home directory, an installed plugin cache, a user-level `CLAUDE.md`, `MEMORY.md`, settings or skills directory; (c) it lists each read of a package `skills/` or `references/` path other than the arm's own export, and a control run with one is labelled `control (read skill)`. Falsifier: the same scan over a stored fixture transcript that reads an installed skill copy exits 1 naming that line.

**AC-4**: Nothing from a run, a case or a private adopter is on this state branch or in any public repository.
Verified by: with the marker list (every run id and session id from the manifests, and the private working repository's name) held outside any repository, `git -C <fresh clone of the public repository> log -p --all --since=<first run start> | grep -c -F -f <markers>` prints 0, and `grep -r -c -F -f <markers>` over this task's file and folder at the pushed state head prints no non-zero count.

**AC-5**: The grader is shown to tell the two outcomes apart before any paid run.
Verified by: `python3 behaviour/run_cell.py selfcheck behaviour/cells/ideation-flags-unprovable-criterion` exits 0 and prints FAIL for the case's own approved design (the task file at the parent of its first superseding amendment, the state cut in row 12), PASS for the same file with the offending criterion moved under a `Not provable now` line, and PASS for a fixture whose criteria are all script-proved; `run` refuses to launch while `selfcheck` fails. Falsifier: deleting the model-run pattern from `answer.json` makes the first fixture grade PASS and `selfcheck` exit 1.

**AC-6**: The runner stops at the spend boundary before launching, not after.
Verified by: `python3 behaviour/run_cell.py run <cell> --dry-run` against two stored fixture result folders, one with 18 launch records and one with 2 INVALID trials, exits 1 with `cap reached` and `cell halted` respectively and starts no process; each stored manifest carries the wall-clock and tool-call caps written before its launch time.

## FO alignment

Alignment: not needed before ideation: outcome, caps and proof are stated in the scope the reform session gave under the Captain's grant; the design returns at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: package tooling with no release on a journey map.
Reviewer: kc-dev-flow-2:engineering-reviewer gpt-6-astra 2026-11-14 — after the fix, can the agent outlive the runner or its caps on any exit path, and may a paid run be asked of the Captain again? (run and attack the six stub proofs; record dispatch/engineering-reviewer-1.md)

## Design

### PRFAQ

Before a kc-dev-flow-2 release, the maintainer runs one command in the private working repository. It rebuilds one real ideation dispatch from a frozen public task, runs a fresh Claude worker on it three times at the last released package, three times at the candidate, and three times with no package at all, each in an empty home with nothing of the operator's set-up. It grades what each worker left in the task file, not what it said, and prints one row: base k/n, candidate k/n, control k/n, valid/n, minutes, tool calls, tokens and the model as served.

- Why this cell first? It aims at the largest measured problem (outcome 三: 50 of 155 approved designs later changed their criteria). Its case is a design that passed its gate with a criterion only a model run could prove, which validation later could not prove.
- Why might it show nothing? The candidate is expected to pass and the others to fail, so the cell would show nothing only if the release or the control also passes. The rule grep (evidence/ideation-1/rule-grep.txt, third check) finds the answer at main only: `references/sd/workflow.md` lines 188-189 ("Every criterion's evidence command runs once on it ... unrunnable: `Not provable now`", added by #864), absent at kc-dev-flow-2-v0.41.0 and at the case-time v0.35.0, and the historical worker on the case-time package did not flag the criterion. If no arm fails within the cap, the report says so and the cell is dropped (CE's rule: a cell must be seen to fail).
- What does it cost? At most 18 paid runs, counted by the runner; 9 scheduled. No dollar figure: minutes, tool calls and tokens of the first trials are recorded first.

### Flow

```mermaid
flowchart TD
  O[Operator: run_cell.py run cell] --> SC{selfcheck: grader falsifiers}
  SC -->|fail| STOP1[Stop: no paid run]
  SC -->|pass| CB[Build case once: clone public repo at row-12 pins, remove origin]
  CB --> LOOP[Next trial, arms interleaved: base, cand, control]
  LOOP --> CAP{launch records under 18 and fewer than 2 INVALID?}
  CAP -->|no| HALT[Stop: cap reached or cell halted]
  CAP -->|yes| B{arm}
  B -->|base or cand| RD[replay_dispatch.py build at the arm's package ref]
  B -->|control| CD[same build, then package lines removed and no package dir]
  RD --> L[Launch claude -p in isolated env; write manifest before start]
  CD --> L
  L --> K{wall cap or tool-call cap hit?}
  K -->|yes| INV[Kill process group; trial INVALID]
  K -->|no| C[Collect stream, task file bytes, state diff]
  INV --> CL[replay_dispatch.py cleanup]
  C --> CL
  CL --> G[grade: PASS, FAIL or INVALID]
  G --> MORE{trials left?}
  MORE -->|yes| LOOP
  MORE -->|no| T[table: per arm k/n, valid/n, minutes, tool calls, tokens, model as served; scan]
```

### Runner

One new file, `behaviour/run_cell.py`, with five subcommands; nothing else in it builds dispatches.
- `selfcheck <cell>`: grades the cell's three falsifier fixtures and exits 1 unless they read FAIL, PASS, PASS (AC-5). `run` calls it first.
- `run <cell> [--trials N] [--dry-run]`: builds the case directory once outside any repository. A full clone would hand the worker the case's later records, 170 tags and every later package (evidence/ideation-1/rule-grep.txt, second check), so the runner instead writes two new one-commit repositories, one from `git archive <state cut>` and one from `git archive <code commit>`, with no remote, tag or history; package refs are exported from a separate clone that no run directory names. `replay_dispatch.py` comes from `git show kc-dev-flow-2-v0.41.0:kc-dev-flow-2/scripts/replay_dispatch.py`; the Spacedock binary is the v0.27.2 release asset checked against its published sha256, and the Spacedock plugin is `git archive v0.27.2` of the public Spacedock repository, so binary and plugin are the same version and neither comes from an installed copy; for each missing trial, interleaved base, cand, control: refuse if the cell's results already hold 18 launch records or 2 INVALID trials (AC-6); call `replay_dispatch.py build --spacedock <run>/bin/spacedock` (the probe found the binary's home path in the dispatch otherwise); write the manifest with caps and pins; launch; enforce caps; collect; call `replay_dispatch.py cleanup`; grade. `--trials 1` runs the first trial of each arm only.
- Launch: `claude -p <bootstrap> --model claude-opus-5-5 --effort high --plugin-dir <run>/spacedock-plugin --setting-sources project,local --strict-mcp-config --output-format stream-json --verbose --permission-mode dontAsk --allowedTools Read,Write,Edit,Glob,Grep,Bash --disallowedTools WebFetch,WebSearch,Agent --add-dir <run> --no-session-persistence`, cwd `<run>/code`. The bootstrap is the line FO's dispatches use (`Skill spacedock:ensign; then Read <run>/dispatch.md`). Model and effort follow this workflow's ideation dispatch (Claude Opus high, FO's trial log).
- Hard stop: the runner reads the stream line by line; it counts `tool_use` blocks and kills the process group at the tool-call cap, and kills at the wall-clock cap. `--max-turns` is not in `claude --help` (evidence/ideation-1/cli-flags.txt), so the count is the runner's.
- `grade <run dir>`: reads only `task-after.md` (the task file bytes after the run) and the stream. It splits criteria by the `**AC-<id>**` grammar under the first `## Acceptance criteria` heading. A criterion is model-run-dependent when its evidence text matches the cell's `answer.json` patterns. PASS: every such criterion is flagged in its own block or in a decisions section naming its id (`Not provable now`, `Needs decision`, `Captain decision`); a design with none reads `PASS (no model-run criterion)`, counted as a pass and shown apart. FAIL: one is unflagged. INVALID: no criterion written, cap hit, process error, or a scan breach. The worker has no `claude`, `codex` or `gh` on PATH, so it cannot have run a model proof itself.
- `table <cell>`: re-grades every run, writes `table.md`, and prints per arm k/n, valid/n, median and total minutes, median tool calls, summed input, output and cache tokens, the model as served, refs with resolved SHAs, Spacedock and CLI versions; verdict PASS, REGRESSION (cand below base), CEILING (base n/n), NO-FAIL (no arm failed), or INVALID (fewer than 2 valid trials on an arm). `total_cost_usd` is shown only as "imputed, not billed".
- `scan <cell>`: AC-3's two checks on every stored run, plus a search of every stored file for an OAuth or API key prefix; a hit stops the run and is reported as a suspected key.

### Isolation

Shown by observation, not by the variables set (CE's lesson):
- Empty `HOME`, empty `CLAUDE_CONFIG_DIR`, `TMPDIR` inside the run, all per run. The probe showed such a run sees no login at all (evidence/ideation-1/auth-probe.txt), so nothing personal is inherited.
- The child environment is an allowlist, not a scrub: `PATH=<run>/bin:/usr/bin:/bin` (copies of the pinned `spacedock` and `python3` only), `HOME`, `CLAUDE_CONFIG_DIR`, `TMPDIR`, `LANG`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, replay author and committer names, and the credential. No `GITHUB_*`, `RUNNER_*`, `CLAUDECODE`, Paseo or SSH variables reach it.
- Credential: one variable, `CLAUDE_CODE_OAUTH_TOKEN`, handed to the runner by the operator's secret wrapper and passed only to the child; never written to a file. `--bare` would need an API key (claude --help), so it is not used.
- No later history: the case repositories hold one commit each (`### Runner`), so `git log` or `git show` in a run reaches nothing after the cut.
- What every arm can still read: the case's own code tree, which for a package task is this repository at the code commit, including the case-time `kc-dev-flow-2/` (the code under design), `CLAUDE.md` and `AGENTS.md`. That is intrinsic to replaying the package's own tasks and is the same for all arms.
- Shown by: the stream's init event (plugins, skills, MCP servers) stored per run, and the transcript scan (AC-3), which also lists every read of a `kc-dev-flow-2/skills/` or `references/` path that is not the arm's own export. A control run that read the case-time skill in its code tree is labelled `control (read skill)` and shown apart, not counted as a no-skill trial and not INVALID. Managed policy settings, if the machine has any, still apply to every arm alike; the manifest records whether that file exists.

### First cell

- Name: `ideation-flags-unprovable-criterion`.
- Case: `replay-cases.tsv` line 12 (header is line 1): outcome 三, cause class proof-needs-evidence-validator-cannot-produce, set tuning, confidence high, scrub light. It is the only row in that class that is tuning, high confidence and light scrub; the two other light rows are held-out and stay unused. Its pins (state commit = the `ideation_dispatch_cut` column, code commit, slug) live only in the private working repository's `cell.json`.
- Arms: base = `kc-dev-flow-2-v0.41.0` (fa022a864, the last release); cand = origin/main `c2f035b66` today, re-read and pinned by SHA in the manifest of the first launch; control = the same dispatch with no package. Both refs build exit 0 (evidence/ideation-1/dispatch-build-probe.txt). `--readme-base-ref kc-dev-flow-2-v0.35.0`, the marker in the case's README.
- Pin choice (D2, decided by FO): base is the last release and candidate is main, as the outcome says; no case-time arm. The dispatch had asked to pin the package to the case's `package_version` (0.35.0) so an arm has not seen the case's answer; the base arm still has not (no such rule at v0.41.0, rule-grep.txt third check), while the candidate carries the answer on purpose, since it is the change under test.
- Control arm: the base dispatch with its `Package root:` line, harness line and fetch-commands block removed and one control line added ("write the design and acceptance criteria into the task file; write your stage report in the state checkout only; do not push"), no package directory in the run, and a workflow README cut to its frontmatter, so nothing tells the worker to hold for a missing skill. Same task, checklist and Spacedock ensign contract as the other arms.
- Checklist: the two items in the probe's `checklist.txt` (a design with criteria in the task file; a stage report naming each criterion with its current evidence). It names no rule under test (maintain-flow).
- Grading: on artifacts, as in `### Runner`; the answer key is the case's own record (the criterion its amendment later superseded needed a model run). The grader reads no claim the worker makes about itself.
- Caps per run, recorded before the first launch: wall clock 1500 s, 150 tool calls. Reason: the earlier attempt's Claude runs hit 1800 s twice, and that task's design note judged 1800 s too long. The first trial of each arm measures this; a change of caps is a new cell version, not an edit.
- Expected reading: base FAIL on most trials (v0.41.0, like the case-time package that let this design through, asks no Pilot design to run or flag each criterion's proof); candidate PASS on most trials (main's workflow.md, which the worker reads through the fetched stage definition, tells it to run each criterion's evidence command once and mark the unrunnable ones `Not provable now`; no `claude`, `codex` or `gh` is on its PATH, so a model-run proof cannot run and must be flagged or replaced); control FAIL (no rule). A candidate at or above 2 of 3 with base at or below 1 of 3 reads as the change working; base passing as often as the candidate reads as the rule not being the cause. The grader's flag word is the candidate's own phrase, so a candidate pass shows the rule was followed, not that the flag was judged well; the validator's read of each graded file (AC-2) is the check on that.

### Files added in the private working repository

- `behaviour/run_cell.py`: the runner (`selfcheck`, `run`, `grade`, `table`, `scan`).
- `behaviour/cells/ideation-flags-unprovable-criterion/cell.json`: case pins, refs, model, effort, caps, trials, launch cap 18.
- `behaviour/cells/ideation-flags-unprovable-criterion/checklist.txt`: the two-item checklist.
- `behaviour/cells/ideation-flags-unprovable-criterion/answer.json`: model-run patterns and flag words for the grader.
- `behaviour/cells/ideation-flags-unprovable-criterion/falsifiers/approved.md`, `flagged.md`, `provable.md`: AC-5 fixtures.
- `behaviour/cells/ideation-flags-unprovable-criterion/falsifiers/leaky-transcript.jsonl`: AC-3's falsifier.
- `behaviour/cells/ideation-flags-unprovable-criterion/falsifiers/capped/` and `halted/`: AC-6's two stored result folders.
- `behaviour/results/ideation-flags-unprovable-criterion/<run id>/`: `manifest.json`, `stream.jsonl`, `task-after.md`, `state.diff`, written by the runner and committed after the runs.
- `behaviour/results/ideation-flags-unprovable-criterion/table.md`: written by `table`.
Case directories, the marker list and the credential stay outside every repository.

### Run plan and spend

- First implementation step, no credential: start the isolated launch exactly as `### Runner` describes, with no `CLAUDE_CODE_OAUTH_TOKEN`, and read the stream's init event for the exported Spacedock plugin and its `ensign` skill. If no init event appears without a login, record that and continue; no paid run before the Captain answers D1.
- Before any paid run: `selfcheck` (AC-5), `run --dry-run` (AC-6), `scan` on the fixtures (AC-3 falsifier).
- Step 1, 3 runs: `run --trials 1`, one per arm; read minutes, tool calls and tokens; stop if any arm is INVALID for a harness reason.
- Step 2, 6 runs: `run --trials 3`.
- Reruns: an INVALID trial is replaced once; a second INVALID halts the cell. Scheduled 9, at most 10 in the cell, and the runner refuses the 19th launch counted over every record, including any made while building the runner.

### Before new work

Checked: the package's `replay_dispatch.py` (used as is) and the maintain-flow procedure (followed: release and change built from the same commits, a checklist naming no rule); the earlier attempt's replay folder on this state branch (`validation-reads-pr-review-comments/implementation/replay/`: `run.py` hard-codes one case, normal home, 1800 s, no tool cap and no table, so its launch pattern is reused and its code is not); Spacedock's live-lane isolation and CE's eval cell, through `.context/dev2-reform/behaviour-ci-design.md` sections A and C (not re-read at source); the v1 published-tag smoke (answers install and load, not behaviour; not merged with this). ADRs: none governs a behaviour runner (`git grep` of `docs/adr` for replay found only ADR 0037, workers return to FO early); ADR 0079 governs the evidence kept here. `Override:` lines: one past ruling chose not to measure behaviour for a PR (「照建議不量」, 2026-10-22); this task is the Captain's later choice to build the measurement, so it does not conflict. Inaccessible: the private working repository's layout (FO gives its path to implementation); paths above are relative to its root.

### Worth questions

- Runner. Serves 「先做行為基準」 and 「該測試的是 skill 是否真的造成想要的結果」. Without it the replay stays hand-built per change and the earlier attempt's failures repeat. Premise that would make it unneeded: an existing runner already does this; checked, none does (above).
- First cell. Serves outcome 三, 「設計階段提出的規劃要真的可行」. Without it the runner proves only that it launches. Premise that would make it unneeded: the release already passes; the rule grep says the release lacks the rule the candidate adds, and the first 3 runs test it.
- Control arm. Serves outcome 零, 「該怎麼知道用我的工作方法，確實比沒用較好？」. Without it a pass on both package arms cannot be told from a strong model passing alone.
- Isolation. Serves outcome 十五, 「隔離個人設定與技能組合影響」. Without it a result depends on whose machine ran it. Premise: the empty home inherits nothing; the auth probe shows it inherits not even the login.
- Caps and halt. Serve the Stop condition the reform session set (18 runs, two invalid). No Captain words of his own; kept because the Stop condition is part of the admitted scope.
- AC-4 scan. Serves 「私有的內容不離開本機」 (outcome 七). Without it nothing checks that run output stayed private.

### Not provable now

- AC-1, AC-2: need the paid runs; the build step they rest on ran now for both package refs (exit 0).
- AC-3: needs real transcripts; the empty-home probe ran now. Whether `--plugin-dir` loads the exported Spacedock copy under an empty config is shown only by the first run's init event.
- AC-4: the markers do not exist until runs happen.
- AC-5, AC-6: need the runner and fixtures, which implementation writes; each runs without a paid call.

### Needs decision

- D1 (Captain): the credential. Recommended: a subscription token he makes himself with `claude setup-token` (his browser login), kept in his secret store and handed to the runner by his wrapper, local only. Without it no isolated run can authenticate (auth probe). Worse under it: a long-lived token for his subscription exists until he revokes it. The alternative is a Console API key, which bills separately.
- D2 (FO): decided. Base is the last release, candidate is main, no fourth arm (FO follow-up, `dispatch/ideation-1-message-1.md`). The cell's expected reading under it is in `### First cell`.

### Batch overlap

- `design-check-reads-each-pilot-criterion-for-its-proof-record` (implementation): changes the package's ideation checks, so it may move the candidate ref; it shares no file with this task (this task's files are in the private working repository). It is the change this cell would measure.
- `state-branch-writes-carry-no-private-identifiers` (ideation): a push filter for this state branch; it shares no file, and this task file carries no private identifier, so a filter would pass it.
- `validation-reads-pr-review-comments` (implementation): the earlier attempt; read only, no shared file.
- Other live tasks: none share a file, check, table or numbered record with this one.
Recommended order: run this cell's paid runs after the proof-record task merges or is closed, so the candidate ref is the change it measures; implementation of the runner can start now.

## Captain amendments

### Amendment 1 — 2026-11-14, chat
Captain: 「行為基準實跑用訂閱權杖，我自己產生後放進密碼庫」 (chat with the second dev2 FO, 2026-11-14)
Asked: asks.jsonl ask 1 in this task's folder (the credential for isolated runs, decision D1 of the design)
Supersedes: none

### Amendment 2 — 2026-11-14, chat (standing grant; ruling given by the reform session)
Captain: 「改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。」 (chat with the second dev2 FO, 2026-11-14)
Asked: not asked of the Captain. Under that grant the reform session (Paseo 26215d96, message a63e845a) ruled on FO's stop report: "continue, do not re-cut. Budget amended to 3 implementation cycles; this is the last one I grant"; the aborted launch "counts toward the 18 launches and is recorded as operator abort; it is not one of the two INVALID trials that halt the cell"; and five proofs with a stub agent command are owed before any further paid run, validated by a different worker running them.
Supersedes: none
Budget: 3 implementation cycles

## Stage Report: ideation

- DONE: A design for the thin runner (launch, hard stop, manifest, grade, table) that reuses scripts/replay_dispatch.py and the maintain-flow procedure, names every file it adds in the private working repository, and states how isolation is achieved and shown (empty home and config directory; no read of an installed skill copy or personal configuration)
  `### Runner`, `### Isolation`, `### Files added in the private working repository`; replay_dispatch.py built the case at both package refs, exit 0 (evidence/ideation-1/dispatch-build-probe.txt); an empty home and config dir shows `loggedIn: false` (auth-probe.txt).
- DONE: The first cell chosen: which archived public package task and cut point it uses (named only by its row in the case inventory, never by content), the package refs for base and candidate, the no-skill control arm, the grading rule on artifacts the model cannot author, and the wall-clock and tool-call caps per run, with the reason the cell is expected to fail on some arm
  `### First cell`: replay-cases.tsv line 12 at its ideation_dispatch_cut; base kc-dev-flow-2-v0.41.0, cand origin/main c2f035b66 (pinned at first launch), control without package; caps 1500 s and 150 tool calls; expected failure rests on rule-grep.txt (no arm asks for a proof run or a flag).
- DONE: Each acceptance criterion with its proof run once now where it can be or listed under `Not provable now` with the reason; the run plan showing the count stays within 18 paid agent runs; the decisions only the Captain can make named; kc-dev-flow-2/scripts/design_surfaces.py check on the task exits 0
  Per criterion below; `### Run plan and spend` schedules 9 runs, at most 10 in the cell, runner refuses the 19th; `### Needs decision` D1 (credential); design_surfaces.py check exit 0, "design surfaces presentable" (design-surfaces-check.txt).
- DONE: AC-1 (table from real runs): not yet verified; needs paid runs. Run now: the dispatch build both package arms rest on, exit 0 twice.
- DONE: AC-2 (cell fails on some arm or NO-FAIL reported): not yet verified; needs paid runs. Run now: rule grep across the three refs, no proof-run rule in any arm.
- DONE: AC-3 (isolation): not yet verified; needs transcripts. Run now: empty-home auth probe; `--plugin-dir` loading under an empty config is shown only by the first init event.
- DONE: AC-4 (nothing private public): not yet verified; markers exist only after runs. This task folder holds no case pin, case content or run output (evidence files name row 12 only).
- DONE: AC-5 (grader falsifiers): not yet verified; the runner is implementation's. Premise checked now: the case's approved design (state cut of row 12) carries the model-run criterion with no flag in its criteria or its Captain decisions section, so the FAIL fixture exists.
- DONE: AC-6 (spend boundary before launch): not yet verified; implementation's, provable without a paid run.

### Summary

Designed the thin runner (`behaviour/run_cell.py`: selfcheck, run, grade, table, scan) on top of the package's replay_dispatch.py, the first cell on row 12 of the case inventory with base = last release, cand = main, a no-package control, artifact grading of unflagged model-run criteria, caps 1500 s / 150 tool calls and at most 10 of the 18 runs. Added AC-5 (grader falsifiers before any paid run) and AC-6 (runner refuses at the spend boundary) and named each criterion's evidence command. Two probes ran with no model call: both dispatch builds exit 0, and an empty home sees no login, so the Captain must supply a credential (D1). No paid run happened.

## Stage Report: ideation

- DONE: A design for the thin runner (launch, hard stop, manifest, grade, table) that reuses scripts/replay_dispatch.py and the maintain-flow procedure, names every file it adds in the private working repository, and states how isolation is achieved and shown (empty home and config directory; no read of an installed skill copy or personal configuration)
  `### Runner`, `### Isolation`, `### Files added in the private working repository`. Case repositories are now one-commit trees with no history or tags (a full clone reached the case's later amendment and 170 tags, rule-grep.txt second check); Spacedock binary and plugin both pinned to the public v0.27.2 release; replay_dispatch.py built the case at both refs, exit 0 (dispatch-build-probe.txt); empty home shows `loggedIn: false` (auth-probe.txt).
- DONE: The first cell chosen: which archived public package task and cut point it uses (named only by its row in the case inventory, never by content), the package refs for base and candidate, the no-skill control arm, the grading rule on artifacts the model cannot author, and the wall-clock and tool-call caps per run, with the reason the cell is expected to fail on some arm
  `### First cell`: replay-cases.tsv line 12 at its ideation_dispatch_cut; base kc-dev-flow-2-v0.41.0, cand origin/main c2f035b66 (pinned at first launch), control without package and with a frontmatter-only README; caps 1500 s and 150 tool calls; expected failure: no arm from 0.35.0 to main adds a rule to prove or flag criteria (rule-grep.txt, both checks). The departure from the case-time pin is named and put to FO as D2.
- DONE: Each acceptance criterion with its proof run once now where it can be or listed under `Not provable now` with the reason; the run plan showing the count stays within 18 paid agent runs; the decisions only the Captain can make named; kc-dev-flow-2/scripts/design_surfaces.py check on the task exits 0
  `### Run plan and spend`: 9 scheduled, at most 10 (13 with D2's fourth arm), runner refuses the 19th; Captain decision D1 (credential), FO decision D2 (base ref); design_surfaces.py check rerun on the final design, exit 0, "design surfaces presentable" (design-surfaces-check.txt).
- DONE: AC-1 (table from real runs): not yet verified; needs paid runs. Run now: the dispatch build both package arms rest on, exit 0 twice.
- DONE: AC-2 (cell fails on some arm or NO-FAIL reported): not yet verified; needs paid runs. Run now: rule grep and the 0.35.0-to-0.41.0 diff on every path an ideation worker reads; no proof-or-flag rule in any arm.
- DONE: AC-3 (isolation): not yet verified; needs transcripts. Run now: empty-home auth probe and the case-clone check that led to one-commit case repositories; `--plugin-dir` loading under an empty config is shown only by the first init event.
- DONE: AC-4 (nothing private public): not yet verified; markers exist only after runs. This task folder holds no case pin, case content or run output (grep for the case slug and its commit prefixes over the task file and folder printed nothing).
- DONE: AC-5 (grader falsifiers): not yet verified; the runner is implementation's. Premise checked now: the case's approved design carries the model-run criterion with no flag in its criteria or its Captain decisions section.
- DONE: AC-6 (spend boundary before launch): not yet verified; implementation's, provable without a paid run.

### Summary

Supersedes the earlier ideation report. The design now builds each case repository from the single pinned tree, because a full clone exposed the case's later amendment and every later package; it states what every arm can still read (the case-time package as the code under design) and has the scan label a control run that read it. It names the departure from the dispatch's case-time pin and puts it to FO as D2, with a fourth-arm alternative inside the 18-run cap; D1, the credential, stays the Captain's. No paid run happened.

Scratch close (`scratch.py close <task folder> ideation-1`, exit 0): `Scratch removed: <scratch root>/ideation-1 (84566127 bytes)`; `Evidence: evidence/ideation-1/ (5 files, 6.3 KiB)`.

## Stage Report: ideation

- DONE: A design for the thin runner (launch, hard stop, manifest, grade, table) that reuses scripts/replay_dispatch.py and the maintain-flow procedure, names every file it adds in the private working repository, and states how isolation is achieved and shown (empty home and config directory; no read of an installed skill copy or personal configuration)
  Unchanged from the previous report: `### Runner`, `### Isolation`, `### Files added in the private working repository`; one-commit case repositories; both refs build exit 0 (dispatch-build-probe.txt); empty home shows `loggedIn: false` (auth-probe.txt).
- DONE: The first cell chosen: which archived public package task and cut point it uses (named only by its row in the case inventory, never by content), the package refs for base and candidate, the no-skill control arm, the grading rule on artifacts the model cannot author, and the wall-clock and tool-call caps per run, with the reason the cell is expected to fail on some arm
  Corrected: the candidate (main c2f035b66) carries the answer in references/sd/workflow.md lines 188-189, absent at v0.41.0 and v0.35.0 (rule-grep-third-check.txt: 0, 0, 2 hits). Expected reading in `### First cell`: base FAIL, candidate PASS, control FAIL; D2 decided by FO: base last release, candidate main, no fourth arm.
- DONE: Each acceptance criterion with its proof run once now where it can be or listed under `Not provable now` with the reason; the run plan showing the count stays within 18 paid agent runs; the decisions only the Captain can make named; kc-dev-flow-2/scripts/design_surfaces.py check on the task exits 0
  Run plan: first step is a no-credential launch smoke reading the init event for the exported Spacedock plugin and its ensign skill; 9 runs scheduled, at most 10, runner refuses the 19th; D1 (credential) is the Captain's; design_surfaces.py check exit 0 on the corrected design (design-surfaces-check-message-1.txt).
- DONE: AC-1 (table from real runs): not yet verified; needs paid runs. Run now: the dispatch build both package arms rest on, exit 0 twice.
- DONE: AC-2 (cell fails on some arm or NO-FAIL reported): not yet verified; needs paid runs. Run now: the corrected grep, which predicts base and control fail and the candidate passes.
- DONE: AC-3 (isolation): not yet verified; needs transcripts. Run now: empty-home auth probe; the no-credential launch smoke (implementation's first step) checks the plugin and skill load before any paid run.
- DONE: AC-4 (nothing private public): not yet verified; markers exist only after runs. The task file and folder hold no case slug, pin or run output.
- DONE: AC-5 (grader falsifiers): not yet verified; the runner is implementation's. Premise checked: the case's approved design carries the model-run criterion unflagged.
- DONE: AC-6 (spend boundary before launch): not yet verified; implementation's, provable without a paid run.

### Summary

Supersedes the earlier ideation reports. FO's correction holds: the candidate's workflow.md asks for each criterion's evidence to run once and for unrunnable ones to be marked `Not provable now`, so the cell now expects the candidate to pass and the release and control to fail; my first grep had left that file out. D2 is recorded as FO's decision (no fourth arm), and a no-credential launch smoke is the first implementation step. Scratch close for ideation-1-message-1, exit 0: `Evidence: evidence/ideation-1/ (7 files, 7.9 KiB)`.

## Stage Report: implementation

- DONE: First, before anything else is built on it: a launch smoke with no credential in the isolated environment the design describes, reading the init event for the exported Spacedock plugin and its ensign skill; record what appears, and if no init event appears without a login, record that and continue
  An init event DOES appear without a login: exported Spacedock 0.27.2 (`spacedock@inline`, path inside the run's own export) with `spacedock:ensign` listed, 4 CLI-bundled `builtin` plugins, 18 bare bundled skills, no MCP server, `apiKeySource: none` (evidence/implementation-1/launch-smoke-init.txt). My first attempt (a hand-written launch line) was refused by the session's permission check and not retried; the second ran through the runner's own launch function (`run <cell> --smoke`). Not shown: whether a credentialed init adds skills or connectors, and whether the plugin's hooks fire (killed at init).
- DONE: The runner and the one cell as the approved design names them, in the private working repository on a branch you create from its main: the five subcommands, the cell files and the falsifier fixtures; AC-5 (grader falsifiers) and AC-6 (spend boundary refuses before launch) shown by commands that cost nothing, with exit codes
  Branch `behaviour-first-cell`, base `c1e6a401b345ba86db9cc696c5cefce2a930ee97`, candidate `758cdd90140c37e394ebc527137ee42842641ae5`: `behaviour/run_cell.py` (selfcheck, run, grade, table, scan), `behaviour/cells/ideation-flags-unprovable-criterion/` (cell.json, checklist.txt, answer.json, three grader fixtures, one leaky transcript, `capped/` with 18 manifests, `halted/` with 2). Local commit only; not pushed. roborev not run (different repository).
  AC-5: `selfcheck` exit 0 prints FAIL, PASS, PASS and the matched criterion ids per fixture (2 model-run criteria in the approved design, 0 in the script-proved one); the same command on a copy with the model-run patterns deleted exits 1 (both grade PASS). `run` calls it first. AC-6: `run <cell> --dry-run --results <fixture>` exits 1 with `cap reached` (18 records) and `cell halted` (2 INVALID); with `subprocess.Popen` and `run` patched to raise, both dry runs still return 1, so no process starts. `run` without the credential variable exits 1 before any record. AC-3 falsifier: `scan` on the leaky transcript exits 1 naming line 4. Evidence: evidence/implementation-1/unpaid-checks.txt.
  Also run at no cost: case build, dispatch build and cleanup for all three arms on one-commit case repositories, exit 0 each, no dispatch names the home directory (case-build-probe.txt); `table`, `grade` and `scan` on six hand-made runs in scratch (not stored).
- DONE: No paid agent run: the Captain has not yet answered decision D1 (the credential). Stop after the unpaid steps and report the exact command the operator runs for the first paid step, the branch, base and candidate SHA, and what remains for AC-1 to AC-4
  First paid step, 3 runs, one per arm: `<operator secret wrapper that exports CLAUDE_CODE_OAUTH_TOKEN> python3 behaviour/run_cell.py run behaviour/cells/ideation-flags-unprovable-criterion --trials 1` (evidence/implementation-1/first-paid-step.txt). Remaining: AC-1, AC-2 and AC-3 need those runs and their real streams; AC-4 needs the marker list and a fresh clone after runs exist. Open risks: the stream parser was checked against an earlier real stream and the no-login init, not a graded run; a credentialed init may add skills or connectors (the runner's init check before the first counted run refuses on that and costs no record; whether that launch makes any API call is not measured).

### Departures from the design, for FO to rule on

- Added `--smoke` and an init-only check inside `run` before any counted launch; added `--results DIR` on `run`, `table`, `scan` (AC-6 needs it to point at fixtures).
- scan (a): the 4 `builtin` plugins and the 18 bundled bare skills (now `bundled_skills` in cell.json) are allowed; any other plugin, namespaced skill or MCP server is a breach, as is a bare skill outside that list.
- scan (b): tool inputs are matched on `.claude/<plugins|skills|CLAUDE.md|settings|projects|agents|commands>` or the operator's home; tool results only on the operator's concrete home (outside the Python runtime prefix), because the case's own CLAUDE.md quotes `~/.claude/plugins` text.
- Both model-run criteria of the approved design match, so the flagged fixture flags both; the design says "the offending criterion" in the singular.
- Tool cap kills when the unique tool_use count exceeds 150; a control run that read a skill stays a valid trial, shown apart.

Scratch close (`scratch.py close <task folder> implementation-1`, exit 0): `Scratch removed: <scratch root>/implementation-1 (199069399 bytes)`; `Evidence: evidence/implementation-1/ (4 files, 8.8 KiB)`.

### Summary

Built the runner and the one cell in the private working repository (branch `behaviour-first-cell`, candidate `758cdd90140c37e394ebc527137ee42842641ae5`, base `c1e6a401b345ba86db9cc696c5cefce2a930ee97`, local only). The no-credential smoke shows an init event with the exported Spacedock plugin and its ensign skill; the grader falsifiers (AC-5) and the spend-boundary refusals (AC-6) pass at no cost. No paid run happened; the state branch carries no case, run or private-repository content, and the task file and evidence are not committed by me (FO commits).

## Stage Report: implementation

- DONE: First, before anything else is built on it: a launch smoke with no credential in the isolated environment the design describes, reading the init event for the exported Spacedock plugin and its ensign skill; record what appears, and if no init event appears without a login, record that and continue
  An init event DOES appear without a login: exported Spacedock 0.27.2 (`spacedock@inline`, path inside the run's own export) with `spacedock:ensign` listed, 4 CLI-bundled `builtin` plugins, 18 bundled bare skills, no MCP server, `apiKeySource: none` (evidence/implementation-1/launch-smoke-init.txt); rerun at the final candidate, same result. My first attempt (a hand-written launch line) was refused by the session's permission check and not retried; the second ran through the runner's own launch function (`run <cell> --smoke`). Not shown: whether a credentialed init adds skills or connectors, and whether the plugin's hooks fire (killed at init).
- DONE: The runner and the one cell as the approved design names them, in the private working repository on a branch you create from its main: the five subcommands, the cell files and the falsifier fixtures; AC-5 (grader falsifiers) and AC-6 (spend boundary refuses before launch) shown by commands that cost nothing, with exit codes
  Branch `behaviour-first-cell`, base `c1e6a401b345ba86db9cc696c5cefce2a930ee97`, candidate `ba8857895701fcab9f60d2dc8ddd85155330f2e4` (two commits; the first, `758cdd90140c37e394ebc527137ee42842641ae5`, is superseded by the second). Local only, not pushed. roborev not run (different repository). Files: `behaviour/run_cell.py`, and under `behaviour/cells/ideation-flags-unprovable-criterion/` cell.json, checklist.txt, answer.json, three grader fixtures, one leaky transcript, `capped/` (18 manifests), `halted/` (2).
  AC-5: `selfcheck` exit 0 prints FAIL, PASS, PASS with the matched criterion ids (2 model-run criteria in the approved design, 0 in the script-proved one); on a copy with the model-run patterns deleted it exits 1. `run` calls it first. AC-6: `run <cell> --dry-run --results <fixture>` exits 1 with `cap reached` (18 records) and `cell halted` (2 INVALID); with `subprocess.Popen` and `run` patched to raise both still return 1, so no process starts; without the credential variable `run` exits 1 before any record. AC-3 falsifier: `scan` on the leaky transcript exits 1 naming line 4. Evidence: evidence/implementation-1/unpaid-checks.txt, all rerun at the final candidate.
  Case build, dispatch build and cleanup for the three arms on one-commit case repositories: exit 0, no dispatch names the home directory (case-build-probe.txt). `table`, `grade`, `scan` ran on six hand-made runs in scratch (not stored).
- DONE: No paid agent run: the Captain has not yet answered decision D1 (the credential). Stop after the unpaid steps and report the exact command the operator runs for the first paid step, the branch, base and candidate SHA, and what remains for AC-1 to AC-4
  First paid step, 3 runs, one per arm: `<operator secret wrapper that exports CLAUDE_CODE_OAUTH_TOKEN> python3 behaviour/run_cell.py run behaviour/cells/ideation-flags-unprovable-criterion --trials 1` (first-paid-step.txt). Remaining: AC-1, AC-2, AC-3 need those runs and their real streams; AC-4 needs the marker list and a fresh clone after runs exist. Open risks: the stream parser was checked against an earlier real stream and the no-login init, not a graded run; a credentialed init may add skills or connectors (the runner's init-only check before the first counted run refuses on that and costs no record; whether that launch makes any API call is not measured).

### Security finding fixed in the second commit

An automated review of the first commit found that the runner ran `git diff` and `git status` inside the worker's state checkout after a run. The worker has an unrestricted shell and could have planted git config or hooks there (a `core.fsmonitor` command, a filter) that the operator's machine would then run. The finding applies. Fixed: every runner git call and every `replay_dispatch.py` call runs with `core.fsmonitor=false`, `core.hooksPath=/dev/null` and no global or system config; the state diff now comes from a file snapshot taken before and after the run, with no git in the worker's tree; a digest of the pinned tools, `replay_dispatch.py` and the three case repositories' config is checked before each launch and after each run, and a change records the run INVALID, deletes the work directory and stops. A probe shows plain git runs a planted fsmonitor command and hook while the runner's git runs neither, and the digest changes on one planted config line (unpaid-checks.txt). Residual, not fixed here: the worker still runs as the operator with an unrestricted shell, so nothing stops it from doing other things as that user; a sandbox around the launch is a separate decision for the Captain.

### Departures from the design, for FO to rule on

- Added `--smoke`, an init-only check inside `run` before any counted launch, and `--results DIR` on `run`, `table`, `scan` (AC-6 needs it to point at fixtures).
- scan (a): the 4 `builtin` plugins and the 18 bundled bare skills (`bundled_skills` in cell.json) are allowed; any other plugin, namespaced skill or MCP server is a breach, as is a bare skill outside that list.
- scan (b): tool inputs are matched on `.claude/<plugins|skills|CLAUDE.md|settings|projects|agents|commands>` or the operator's home; tool results only on the operator's concrete home (outside the Python runtime prefix), because the case's own CLAUDE.md quotes `~/.claude/plugins` text.
- Both model-run criteria of the approved design match, so the flagged fixture flags both; the design says "the offending criterion" in the singular.
- Tool cap kills when the unique tool_use count exceeds 150; a control run that read a skill stays a valid trial, shown apart.
- `state.diff` lists changed files and a unified diff of the task file, not a git diff.

Scratch close (`scratch.py close <task folder> implementation-1`, rerun after the evidence refresh, exit 0): `Scratch removed: <scratch root>/implementation-1 (absent)`; `Evidence: evidence/implementation-1/ (4 files, 9.5 KiB)`. First close: `(199069399 bytes)`.

### Summary

Supersedes the earlier implementation report. Same deliverable (runner and first cell in the private working repository, no paid run), now at candidate `ba8857895701fcab9f60d2dc8ddd85155330f2e4`, which also fixes the review finding that a worker could have planted git config for the runner to execute. The unpaid checks (AC-5, AC-6, the AC-3 falsifier) were rerun at that candidate and pass. The task file and evidence are not committed by me (FO commits).

## Stage Report: implementation

- DONE: Decide from evidence whether the skill named schedule is a skill the CLI itself ships that appears only with a login (not operator configuration), and say what the evidence is; if it is, add it to the cell's allowed bundled skills as a login-only entry, and keep every other unexpected skill, plugin or MCP server a breach.
  Yes. The binary itself registers it as a bundled skill and its prompt builder refuses without a claude.ai login ("API accounts are not supported"); the no-login init lacks it and the credentialed init has it; the isolated run's home is empty and the case tree has no project-level skills (evidence/implementation-1/schedule-skill-evidence.txt). Added as `login_only_skills: ["schedule"]` in cell.json; the scan still breaches on any other plugin, namespaced skill, MCP server or bare skill outside the bundled and login-only lists.
- DONE: Make sure a worker in a run cannot use that skill to act outside the run (it creates scheduled cloud agents): state how the launch prevents it, or prevent it.
  The launch now passes `--disallowedTools` with RemoteTrigger, CronCreate, CronDelete, CronList and `Skill(schedule)` beside WebFetch, WebSearch, Agent; and sets `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` so tool subprocesses do not inherit the token. Shown without a login: the init tool list drops CronCreate, CronDelete and CronList under the deny list (22 tools to 19). Backstop: scan breach (d) marks a run INVALID if the transcript calls any of those tools or the schedule skill (fixture transcript: exit 1, two (d) lines). Not verified without a credentialed run: that the `Skill(schedule)` rule blocks at run time, that RemoteTrigger leaves a logged-in tool list, and that the scrub hides the token from a Bash call. I could not tell from the binary which tool the skill acts through, so the launch denies by name.
- DONE: Captain amendment 1 (in the task file) settles decision D1: the credential is a subscription token the Captain makes and keeps himself; the runner still only reads it from the environment.
  Amendment 1 read in the task file. The runner reads `CLAUDE_CODE_OAUTH_TOKEN` from its environment only, checks presence before any record, passes it to the child process, and never writes it; scan searches every stored file for key prefixes and the literal value. I handled no credential.
- DONE: Re-run the unpaid checks (selfcheck, the two dry runs, the leaky-transcript scan) with exit codes; commit on the same branch in the private working repository; report the new candidate SHA. No paid run and no credential handling by you: the operator re-runs the first paid step.
  Branch `behaviour-first-cell`, base `c1e6a401b345ba86db9cc696c5cefce2a930ee97`, new candidate `6bea0102534dbef98a4be7b4f99a3647f6305c6d` (supersedes `ba8857895701fcab9f60d2dc8ddd85155330f2e4`, which superseded `758cdd90140c37e394ebc527137ee42842641ae5`); local only, not pushed; working tree clean. Exit codes at the candidate (unpaid-checks.txt): selfcheck 0 (FAIL, PASS, PASS plus both transcript fixtures breach); selfcheck on a copy with the model-run patterns deleted 1; dry run on the 18-record folder 1 `cap reached`; on the 2-INVALID folder 1 `cell halted`; neither starts a process (patched-subprocess run); leaky-transcript scan 1 naming line 4; schedule-transcript scan 1 naming lines 2 and 3; `run` without the credential 1 before any record. roborev not run (different repository). No paid run.
  The operator re-runs the first paid step unchanged: `<operator secret wrapper that exports CLAUDE_CODE_OAUTH_TOKEN> python3 behaviour/run_cell.py run behaviour/cells/ideation-flags-unprovable-criterion --trials 1`. If a credentialed init adds anything else, the init check names it before any record is counted.
- DONE: Append a complete new stage report that supersedes the earlier one.
  This report; it carries forward everything in the earlier one that still holds: no case, run or private-repository content is on this state branch (grep of the task file and evidence for the case slug, pin prefixes, any home-directory path and the private repository name: nothing).

### Carried from the earlier reports

- Smoke without a login: an init event appears; the exported Spacedock 0.27.2 with `spacedock:ensign`, 4 CLI-bundled `builtin` plugins, 18 bundled bare skills, no MCP server (launch-smoke-init.txt). Git hardening, the file-snapshot `state.diff`, and the tools-and-case integrity digest are in the runner (security finding from the first review, fixed at `ba8857895701fcab9f60d2dc8ddd85155330f2e4`; the worker still runs as the operator with an unrestricted shell, so a sandbox is the Captain's separate decision). Departures from the design were accepted by FO.
- Remaining for AC-1 to AC-3: the paid runs and their real streams; AC-4: marker list and a fresh clone after runs exist.

Scratch close (`scratch.py close <task folder> implementation-1`, rerun after the evidence refresh, exit 0): `Scratch removed: <scratch root>/implementation-1 (absent)`; `Evidence: evidence/implementation-1/ (5 files, 12.5 KiB)`.

### Summary

Supersedes the earlier implementation reports. The `schedule` skill is a CLI-bundled, login-only skill, so the cell allows it by name as login-only; the launch now denies the scheduling tools and the skill, scrubs the token from tool subprocesses, and the scan fails a run that uses scheduling. Candidate is `6bea0102534dbef98a4be7b4f99a3647f6305c6d`; the unpaid checks pass; no paid run happened; the task file and evidence are not committed by me (FO commits).

## Stage Report: implementation

- DONE: Captain amendment 2 (in the task file): third and last implementation cycle. Fix the launch path: the child's whole process group is killed on interrupt and on runner death; the wall-clock and tool-call caps still fire if the runner dies, so the child cannot outlive its cap under any exit path; one progress line while a run is in flight (arm, trial, elapsed, tool calls); "operator abort" is its own recorded status, counted toward the 18 launches and not as one of the two INVALID trials that halt the cell; the existing aborted launch record is read as that status.
  Cause confirmed in the code: the agent was started in its own session by the runner itself, so a Ctrl-C reached only the runner. Now the agent runs under a guard process that leads its own process group, enforces the wall and tool caps itself, and on interrupt, hangup, termination or runner death writes its result and then kills every descendant it can list and the whole group, itself last. The runner catches Ctrl-C, SIGTERM and SIGHUP, stops the guard, records `operator-abort` with an end time, runs the integrity check and the cleanup, and exits 130. Graded as ABORT: counted as a launch record, not INVALID, and the slot stays open so the trial runs again. The existing aborted record (no end record) now reads `ABORT`, and the dry run reports "1 operator abort, 0 INVALID" (evidence/implementation-1/aborted-record-read.txt). One progress line per interval (default 30 s, `BEHAVIOUR_PROGRESS_S`): `[progress] base t1 elapsed 02:57 tool calls 41/150`.
- DONE: Operator experience: before the first launch the command prints how many runs it will launch, the cap per run, the expected total minutes and how to stop it safely.
  `run` and `run --dry-run` print: runs to launch per arm; cap per run (1500 s, 150 tool calls); expected total minutes, from the median of earlier completed runs when there are any, otherwise "not measured yet" with the ceiling (9 runs x 25 min = 225 min); launch records so far; and how to stop (Ctrl-C once; it counts toward the cap, not toward INVALID; a killed runner is cleaned up by its guard). Shown in aborted-record-read.txt.
- DONE: Five proofs with a stub agent command in place of the real one (no credential, no spend), each a command with its exit code that another worker can run: Ctrl-C during a run leaves no process in the group; SIGKILL of the runner leaves no child past the cap; the wall cap fires on a stub that never exits; progress lines appear; the value of a dummy token set the same way is absent from every file the runner writes (manifest, stream, logs, run directory).
  Run from the private working repository: `python3 -B behaviour/prove_launch.py <name>`, name = ctrlc | sigkill | wallcap | progress | token (a sixth, signalled, covers the review point below). All exit 0 at the candidate: ctrlc (runner exit 130, agent, its background child and guard gone, recorded operator-abort, 1 launch and 0 INVALID); sigkill (guard, agent and background child gone 0.6 s after the runner was killed, against a 30 s cap; the record without an end reads ABORT); wallcap (a stub that never exits is killed at 8.7 s against an 8 s cap; a tool-call burst stops at the 5-call cap in 0.5 s; all processes gone); progress (6 lines for base t1, after the up-front summary); token (the stub saw the dummy token and the scrub switch; the value is in no process argument list and in no file under the results, the work directory or the runner output). Falsifier: the same sigkill proof against a copy whose guard has no runner-death check exits 1 ("still alive after 10s"). The sigkill proof also caught a real defect in my first guard (it crashed on a broken pipe before killing); fixed. The proofs signal only processes they started. Evidence: unpaid-checks.txt.
- DONE: Re-run the earlier unpaid checks; commit on the same branch in the private working repository; report the new candidate SHA; append a complete new stage report that supersedes the earlier ones. No paid run and no credential handling by you.
  Branch `behaviour-first-cell`, base `c1e6a401b345ba86db9cc696c5cefce2a930ee97`, new candidate `16af27c27b19a5ece4979454de46a229f2f928cb` (commits `fc4257b9c60fcdc5e2505203ec39df5e59148a33`, `16af27c27b19a5ece4979454de46a229f2f928cb`); local only, not pushed; the operator's results folder is left untouched and uncommitted. Exit codes (unpaid-checks.txt): selfcheck 0; on a copy with the model-run patterns deleted 1; dry run on the 18-record folder 1 `cap reached`; on the 2-INVALID folder 1 `cell halted`, no process started; leaky-transcript scan 1 (line 4); schedule-transcript scan 1 (lines 2 and 3); `run` without the credential 1 before any record. The scan also read the operator's real partial stream: init seen, no breach, 19 bare skills. roborev not run (different repository). No paid run, no credential handled, no process of the operator's touched.

### Review findings on the first commit, and what changed

An automated review of the first commit of this cycle raised three points; all three apply in principle because the agent runs as the operator.
- The guard's result file sat where the agent could write it. Now the guard reports on a pipe it alone holds and no result file exists; a missing or malformed report grades the run INVALID (`guard-failed`).
- A signal that reaches the guard was recorded as an operator abort, so an agent could signal its way out of being graded. Now it records `signalled` and grades INVALID; only the runner's own caught interrupt records an operator abort (proof `signalled`).
- The abort path skipped the integrity check. It now runs it, records `tampered` (INVALID) if it fails, and skips the cleanup that runs `replay_dispatch.py`.
- Residual, not fixable without a sandbox or another user: the agent runs as the operator and could kill the runner outright; the record then has no end and reads as an operator abort, which counts toward the 18 launches and leaves the trial to run again, so it is visible and bounded but not impossible to game. The earlier residual (a sandbox around the launch is the Captain's separate decision) stands. Also unproven: the guard against the real `claude` (only the stub ran), a descendant that has already detached and been re-parented escapes both the group kill and the descendant sweep, and the sweep uses `ps` (tested on macOS only).

### Carried from the earlier reports

- Departures from the design accepted by FO; the `schedule` skill allowed as login-only with the scheduling tools denied; git hardening and the tools-and-case integrity digest. Remaining for AC-1 to AC-3: the paid runs; AC-4: marker list and a fresh clone after runs exist.

Scratch close (`scratch.py close <task folder> implementation-1`, rerun after the evidence refresh, exit 0): `Scratch removed: <scratch root>/implementation-1 (absent)`; `Evidence: evidence/implementation-1/ (6 files, 15.5 KiB)`.

### Summary

Supersedes the earlier implementation reports. The agent can no longer outlive the runner or its caps on any path the proofs exercise: Ctrl-C, hangup, termination and a killed runner end the whole process group; an interrupt is recorded as an operator abort that counts toward the 18 launches and not as INVALID; the operator sees a progress line per interval and an up-front summary. Six stub-agent proofs pass at candidate `16af27c27b19a5ece4979454de46a229f2f928cb` and the earlier unpaid checks still pass. No paid run happened; the task file and evidence are not committed by me (FO commits).
