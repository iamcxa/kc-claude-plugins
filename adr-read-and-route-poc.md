---
id:
title: Agents consult the governing ruling and route new information to its right home
status: validation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-adr-read-and-route-poc
pr:
gates:
    version: 1
    records:
        - id: gate:adr-read-and-route-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-read-and-route-poc-backlog-1
              briefing:
                id: briefing:adr-read-and-route-poc:backlog:attempt-1:revision-1
                digest: sha256:72e549fa889a0d1e074885f27aec4e19dc101a5f34863e6fb3e44150151ef1f4
                room-ref: ./adr-read-and-route-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-read-and-route-poc:backlog:1
                briefing: briefing:adr-read-and-route-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T06:13:26.845458Z"
                decision: approve
                reason: Captain replied 「照建議」 to the six-item batch (2026-10-21), whose item 2 approved this POC backlog gate as filed, starting after kc-decision-log-cli merges. Consume waits for that start condition.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:adr-read-and-route-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:adr-read-and-route-poc-validation-1
              briefing:
                id: briefing:adr-read-and-route-poc:validation:attempt-1:revision-1
                digest: sha256:1d6c26d2a0b1a0643e70d6ff3f387135215ef0db1178e97d11b854bf62287bc0
                room-ref: ./adr-read-and-route-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-read-and-route-poc:validation:1
                briefing: briefing:adr-read-and-route-poc:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T11:20:01.507097Z"
                decision: approve
                reason: 'Captain replied 「照建議」 (2026-10-21) to the three-item batch whose item 1 approved this validation gate: accept the POC result as PASSED and close it, with no delivery PR.'
              application:
                target-stage: done
                state: pending
started: 2026-10-21T06:22:26Z
---

P1 proves the mechanics only: a task description tells the worker to use the skill, so it does. The value the user wants is unproven. Does an agent consult the governing ruling before deciding when nobody reminds it, and does it put new information in the right home rather than turning everything into an ADR? The user, 2026-10-21: 「確保 skill/hook 可以讓 agent 知道要讀 ADR 之外還要知道可以怎樣區分，因為不是全部資訊都要寫到 ADR」; he approved building this POC (「建立這個 POC」). The result also decides whether kc-decision-log could later replace dev2's ADR reading, which must first be proven easier for agents (boundary contract draft, PR #691).

## Scope

Riskiest assumption: a short skill, or a skill plus a session-start hook listing ruling titles, changes what an agent does at decision time.

- Rule under test: the routing table in `docs/journey/kc-decision-log/boundary-contract.md` (PR #691; the draft as the Captain last saw it).
- About ten realistic scenarios over a fictional decision space and a fictional repository with dev2 ADRs. The scenarios cover a cross-repo direction, a task-only trade-off, a working preference, a deferred user-facing feature, an engineering constraint, and a scenario where an existing ruling already settles the question.
- Three conditions: no help; the `read-ruling` skill only; the skill plus a session-start hook that lists ruling titles. Each condition runs on Claude and on Codex, with the model pinned per run and recorded.
- Two measures per run: did the agent consult the governing ruling before deciding (from its tool calls), and did it place each new piece of information in the home the table names. Expected answers are written by hand before any run.
- Uses the CLI and skill from `kc-decision-log-cli`, so it starts after that task merges. The hook is a disposable POC harness, not the shipped S30 hook nor dev2's `agent-reads-governing-adr` hook. Its results and scenarios are offered to that dev2 task.

Non-goals: shipping a hook or a rule; changing dev2; real private rulings (fictional data only); deciding the replacement question (this returns evidence for the next planning decision).

Budget: one working day of active effort. The run count is declared before launch: about 10 scenarios x 3 conditions x 2 hosts, about 60 agent runs; token cost unmeasured. Stop when the declared runs finish, when either host cannot run the harness, or when the run count would exceed the declaration by more than 20%.

## Acceptance criteria

**AC-1**: A results table gives, per condition and host, the share of scenarios where the agent consulted the governing ruling before deciding, and the share where each new piece of information went to the home the table names. Each cell traces to the run's recorded tool calls and outputs.
Verified by: the committed harness re-run from its README reproduces the table's counts within run-to-run variation, which the report states.

**AC-2**: Expected answers for every scenario were committed before the first run, and no scenario or expectation changed after a run without a recorded reason.
Verified by: commit order of the expectations file and the first run log.

**AC-3**: The report states what the result does not prove: sample size, fictional data, the pinned models, the hook being a harness. It also states which rows of the routing table the agents most often got wrong.
Verified by: the report section, checked against the results table.

## FO alignment

Not needed before implementation. The Captain asked for this POC and approved building it (「建立這個 POC」, 2026-10-21); the scope above restates the design he was shown. Release review: not needed: the task belongs to no release (it informs deferred story S30 and dev2 task `agent-reads-governing-adr`).
Surfaces: none
Visible change: none

## Captain amendments

### Amendment 1 — 2026-10-21, chat
Captain: 「先跑 poc」 (P1 FO's Paseo session "decision-log P1 重切與 dev2 交接")
Asked: 「請你決定一件事：先用預覽工具跑四組條件的 POC，再決定任務一的規模嗎？」 with the proposal: 「1. 現在就跑 POC，用設計階段那個可以實際操作的預覽工具。」「2. 多加第四種條件，專門比 CLI 本身：「skill 教 agent 用 git 加 shasum 讀、看 Status 行」對比「skill 加 CLI」。量三件事：做決定前有沒有去查；交接時版本和指紋對不對；資訊放得對不對。」「3. 先講好判斷規則：CLI 那組沒有明顯勝過 git 那組，任務一就縮成「skill 加設定檔」（只有情境裡真的出現主題衝突，才保留一個判斷生效的小腳本）；勝過就照原設計做。」「POC 從約 60 次執行增加到約 80 次。」
Supersedes: none

### Amendment 2 — 2026-10-21, chat
Captain: 「可以」 (P1 FO's Paseo session, reply to a two-item batch)
Asked: 「1. Codex 的第四組（上一則）：只在 Claude 上跑，不繞過 Codex 的 hook 信任機制。」「2. 重建測試世界：照上面「真實規模、不偏袒 CLI、拿掉查詢提示」的做法重建，第一組重跑。總共約 90 次執行：已經用掉的 20 次加上接下來 70 次，在 worker 設的上限 96 次以內。」
Supersedes: none

## Stage Report: implementation

- DONE: Four arms on the same ~10 scenarios, each on Claude (sonnet) and Codex (gpt-6.1-sol, reasoning high). Expected answers committed before the first run. About 80 runs declared; stop if the count would pass +20%.
  Arms A0 to A3 x S1..S10 ran on Claude (claude-sonnet-5-5) and A0 to A2 on Codex; A3 on Codex was not run by Amendment 2 (Codex 0.162.1 silently skipped my untrusted SessionStart hook; no trust bypass). Expectations committed in bf132615, and again in d6cbbe96 before the rebuilt world's first run (reason in CHANGES.md); 96 scenario runs in total (20 on the first, small world; 70 arm runs; 6 repeats), exactly the cap, none over.
- DONE: A results table per arm and host: consulted the governing ruling before deciding; handoff version and digest matched; new information placed in the home the routing table names. Each cell traces to recorded tool calls and outputs, and the harness re-runs from its README.
  Table below; `harness/score.py` regrades results/ from stored traces (no agent needed); the 6 repeats gave the run-to-run variation (1 of 14 measures flipped). Not re-run end to end: a fresh full agent re-run was not done (cap).
- DONE: The Amendment 1 decision rule applied in the report, what the result does not prove, and which routing rows agents got wrong most.
  Rule outcome: the CLI arm does not clearly beat the plain-git arm. See sections below.

### Summary

Both hosts consulted the governing ruling and checked a cited digest in every scored run in every arm, including with no help, so the CLI cannot beat plain git on those two measures. The only measure that moved is where new information goes: the skill helped Claude (6/10 to 9/10 with git, 8/10 with the CLI) and did not help Codex (6/10 to 5/10), and the session-start hook added nothing on Claude. Artifact: harness and results at path `adr-read-and-route-poc/` in the state checkout, branch `spacedock-state/dev2-poc`, final commit is the one holding this report. The code worktree is unchanged; no PR opened: no push grant. No ADR added. `comment_ratio.py` on the harness: 21 of 1037 lines, 2.0% (limit 5%); on the worktree: 0 code lines. `number_guards.py check`: PASS. `doc_impact.py`: 0 documents listed. `design_surfaces.py check` exits 1 for two defects in FO's `## FO alignment` (no `Surfaces:` line, no `Visible change:` line); I did not edit FO's section, so FO owns it.

### Results

Rep 1 of each cell, larger world, counts out of scored scenarios (consulted n=5: S1 S2 S5 S6 S7; handoff n=3: S8 S9 S10; placement n=10; choice matches the ruling n=8).

| Arm | Host | Consulted | Handoff version and digest | New information in the named home | Choice |
| --- | --- | --- | --- | --- | --- |
| A0 no help | claude | 5/5 | 3/3 | 6/10 | 8/8 |
| A0 no help | codex | 5/5 | 3/3 | 6/10 | 8/8 |
| A1 skill + git | claude | 5/5 | 3/3 | 9/10 | 8/8 |
| A1 skill + git | codex | 5/5 | 3/3 | 5/10 | 8/8 |
| A2 skill + CLI | claude | 5/5 | 3/3 | 8/10 | 8/8 |
| A2 skill + CLI | codex | 5/5 | 3/3 | 5/10 | 8/8 |
| A3 + hook | claude | 5/5 | 3/3 | 8/10 | 8/8 |
| A3 + hook | codex | not run | not run | not run | not run |

Per-scenario cells, effort and repeats: `results.md`, `extras.md`. Effort (mean per run, Claude / Codex): tool calls A1 5.5 / 9.9, A2 6.5 / 11.4; tokens A1 120k / 104k, A2 139k / 126k (+16% / +21% for the CLI); seconds 18 / 60 vs 23 / 64. The small first world, no-help arm only (kept in `results-small-world/`): consulted 10/10, handoff 6/6, placement 14/20; it is why the world was rebuilt.

### Decision rule (Amendment 1)

The CLI arm does not clearly beat the plain-git arm on any of the three measures: consulted 5/5 vs 5/5 on both hosts; handoff 3/3 vs 3/3 on both; placement 8 vs 9 on Claude and 5 vs 5 on Codex (A3 with hook 8, no better than A2). The plain-git agents followed the two-step supersession chain (S6, S9) and caught the wrong digest (S10) every time. By the Captain's stated rule, task one shrinks to "skill plus config file". The scenarios did contain topic conflicts (a superseded cadence ruling, S6 and S9), and plain git handled all of them, so this result gives no reason to keep a judgement script. That is the rule applied to this evidence, not a ruling: the Captain decides.

### What this does not prove

- Ceiling: agents read the governing ruling before deciding in all 35 scored consult cells (no-help included), so these scenarios cannot show a skill or CLI raising consultation; the prompt names the decision log's location, and each folder holds 23 records, which `cat` handles.
- The CLI's own strengths were not exercised, by the Captain's instruction to keep the world realistic: no pair of Accepted records under one key, no CRLF, BOM or non-UTF-8 record, no huge folder. "No advantage here" is not "no advantage".
- Size: one run per cell (6 repeats), 3 handoff and 5 consult scenarios; 1 of 14 repeated measures flipped, so a one-scenario gap (10 points) is inside the noise.
- Fictional data, one model per host (sonnet resolved to claude-sonnet-5-5; gpt-6.1-sol at high), headless runs, a skill that is always opened (10 of 10 when listed). The hook is a harness piece and was tested on Claude only; the Codex hook arm is unanswered.
- Placement is graded by pre-registered path rules. Two scenarios (S2, S7) are ambiguous: both mention work put off, so the story map is defensible; with it allowed (post hoc, `extras.md`) Claude A1/A2/A3 reach 10/10 and Codex A1/A2 7/10. Codex also creates a new `tasks/TASK-023.md` in 3 of 10 runs of each skill arm (0 on Claude), which the rules count against it.

### Routing rows agents got wrong most (counts over the 7 rep-1 cells)

- Task-only trade-off vs deferred feature: S7 story map 5/7 runs, S2 story map 4/7 runs (see ambiguity above).
- Over-recording: an engineering constraint also written to the decision space (S5, 2/7, both no-help) and a pointer added to AGENTS.md for a cross-repo rule (S1, 2/7); a new task file where no task exists (S1, S3, S5: 7 runs, all Codex).
- A working preference written as an ADR in the decision space (S3, 1/7, no-help). Rows the skill fixed: agent notes (S8 hunch: no-help 0/2, with skill 6/6) and instruction file (S3 Claude: no-help N, skill Y).

### Findings for the record

- Codex 0.162.1 silently skips an untrusted SessionStart hook: in a scratch project with a fresh CODEX_HOME, no hook text reached the model and stderr showed only an unrelated MCP auth error. I did not verify whether the command ran. The two ways around it (`--dangerously-bypass-hook-trust`, forging a trusted_hash) were denied by the permission system and not used.
- Harness limits: Claude auto memory off and sandbox on; Codex per-run HOME and workspace-write; the 4 smoke runs are in `probes/`; six earlier manual isolation probes are not stored. Cleanup: temp workspaces under /tmp and one probe project folder under ~/.claude/projects removed; the harness itself is disposable and the only persistent change is the state-checkout folder.
- Changes after the first run, each with a reason in `CHANGES.md`: world rebuilt (Amendment 2), S9 grader reading widened after A0 evidence and before any arm run.

## Stage Report: validation

- DONE: Independent check of AC-1..AC-3: re-grade the stored traces with `python3 harness/score.py` and match the results table.
  Regraded in a throwaway copy: `results.md` and `results.json` (76 runs) byte-equal to the committed ones; `extras.py` output also equal. Checked against the stored traces; not re-run end to end (cap spent, as instructed).
- DONE: Confirm from git history that scenarios and expectations were committed before the first run, and that every later change has a dated reason in CHANGES.md.
  `bf132615` (14:41:36) holds scenarios, expectations, score.py and templates; first ledger run starts 14:44:19. Later changes: `d6cbbe96` world rebuild and S9 grader reading (`2bccb244`, 17:21:29, before the first A1-A3 run at 17:21:33) both have dated CHANGES.md entries. Templates are unchanged since `bf132615`. Scenario prompts S1-S10 unchanged; only the handoff footer changed, as CHANGES.md says. One undated change: `score.py` `hook_seen` (diagnostic column only, no measure affected).
- DONE: Confirm 96 runs, the arms and hosts per Amendments 1 and 2, and that Codex arm 4 was not run.
  `ledger.jsonl` has 96 rows (20 small-world A0, 70 arm runs, 6 repeats): A0 20+20, A1 10+10, A2 13+13, A3 claude 10, A3 codex 0; no A3 codex run directory exists. argv in `meta.json`: claude `--model sonnet` (reported claude-sonnet-5-5) x43, codex `gpt-6.1-sol` with high reasoning x33.
- DONE: Check that the report applies the Amendment 1 decision rule to this evidence (CLI arm versus plain-git arm) without overclaiming.
  Counts reproduce: consulted 5/5 vs 5/5 and handoff 3/3 vs 3/3 on both hosts, placement 8 vs 9 (Claude) and 5 vs 5 (Codex); CLI costs +16% / +21% tokens. The report says outright that the rule outcome is not a ruling and that "no advantage here" is not "no advantage". I find no overclaim in the rule application.
- DONE: Check that the "does not prove" limits match the data: ceiling on consult and handoff, untested CLI edge cases, sample size, ambiguous S2 and S7.
  All four are in the report and match results.md/extras.md (35 of 35 consult cells; 1 of 14 repeat measures flipped; S2/S7 lenient 10/10 Claude, 7/10 Codex). Two limits are missing or wrong, see Findings.
- DONE: A minimal acceptance script the FO can run in a fresh shell, and the `adr_lint.py docs/adr --since <base>` command run with its exit code.
  Script below, run by me in a fresh shell: steps 1-4 printed OK. `python3 <package>/scripts/adr_lint.py docs/adr --since origin/main` in the code worktree: "28 ADR file(s) checked, 0 legacy", exit 0. The local `main` ref is stale (a219ca13), so the base is `origin/main` = worktree HEAD c27e7659; the code worktree has no diff, so lint has no added record to require.
- DONE: Record unverified obligations.
  `dispatch_records.py <task folder>` exits 1: no `dispatch/` folder for this task (finding for FO). `comment_ratio.py bf132615^ HEAD` on the state checkout: 22 of 1139 lines, 1.9%, exit 0. `number_guards.py check` PASS, `design_surfaces.py check` exits 0 now, `doc_impact.py origin/main HEAD` lists 0 documents. No `boundary-crossed:` found: the harness is disposable, writes only under /tmp and the state folder, no persistent seam.

### Verdict

Recommend PASSED for the proof as recorded: the table, counts and decision-rule application reproduce from the stored traces, and the order of commits supports AC-2. Material limits and corrections follow; none changes the rule outcome (CLI does not clearly beat plain git).

### Findings

- Missing limit: the handoff measure is partly prompted. The output schema (`ruling_check`) has fields `digest_matches_cited` and `in_force`, so every agent, A0 included, is asked to compare. 3/3 handoff in every arm therefore does not show agents verify unprompted; it shows they verify correctly when asked to report it. The report's "no prompt tells the agent to consult or confirm" holds for the consult measure only.
- Grader widening: without the S9 `alt` reading (added after seeing A0 evidence, documented), A0 codex handoff is 2/3, not 3/3. No effect on A1-A3 or the rule, but the table's A0 cell depends on it.
- Report error: "Rows the skill fixed: agent notes (S8 hunch: ... with skill 6/6)" should be 5/5; five skill-arm rep-1 runs exist (A1 x2, A2 x2, A3 claude).
- Codex hook skip is not verified: the report says no hook text reached the model; whether the command ran is unknown (the report says so). The Codex hook arm stays unanswered.
- Undated `hook_seen` change in `score.py` after the A0 commit; diagnostic only.
- For FO: `dispatch_records.py` exit 1 (no dispatch records); the stored `harness/__pycache__` pyc files are committed to the state branch (disposable, not harmful).

### Minimal acceptance script

Needs python3 and git; no agent, network or secret. Runs in a fresh shell, about 1 minute.

    S=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state
    T=$S/adr-read-and-route-poc
    # 1. regrade stored traces in a scratch copy; expect no diff output and the OK line
    D=$(mktemp -d) && cp -R "$T" "$D/p" && (cd "$D/p/harness" && python3 -B score.py >/dev/null) && diff "$D/p/results.md" "$T/results.md" && cmp "$D/p/results.json" "$T/results.json" && echo "1 OK: regrade equals committed table"
    # 2. run counts; expect "2 OK" with 96 total, A3 codex absent
    python3 -B - "$T" <<'P'
    import json,sys,collections
    L=[json.loads(l) for l in open(sys.argv[1]+"/ledger.jsonl")]
    c=collections.Counter((r["arm"],r["host"]) for r in L)
    assert len(L)==96, len(L)
    assert c[("A3","codex")]==0 and c[("A3","claude")]==10
    print("2 OK:",len(L),"runs",dict(sorted(c.items())))
    P
    # 3. expectations committed before the first run; expect the OK line
    first=$(python3 -B -c "import json;print(int(min(json.loads(l)['started'] for l in open('$T/ledger.jsonl'))))")
    exp=$(git -C "$S" log --format=%ct --diff-filter=A -- adr-read-and-route-poc/harness/expectations.json | tail -1)
    [ "$exp" -lt "$first" ] && echo "3 OK: expectations added $((first-exp))s before first run"
    # 4. decision-record lint; expect "28 ADR file(s) checked, 0 legacy" and exit 0
    cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/.worktrees/spacedock-ensign-adr-read-and-route-poc && python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/scripts/adr_lint.py docs/adr --since origin/main; echo "4 exit $?"

Does not cover: a fresh agent re-run (cap spent), the CLI's edge cases, the Codex hook arm, any model other than the two pinned.
