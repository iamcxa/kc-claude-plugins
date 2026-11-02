---
title: Special roles follow the Captain's model table, and the trigger check recognizes Codex models
status: validation
variant: kc-dev-flow-2
profile: pilot
gates:
    version: 1
    records:
        - id: gate:special-roles-follow-the-model-table:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:special-roles-follow-the-model-table-backlog-1
              briefing:
                id: briefing:special-roles-follow-the-model-table:backlog:attempt-1:revision-1
                digest: sha256:b2c65d5d5587dfaa508f2ffe71c13a4672dad8862a220fd572d9f9f14c343bb2
                room-ref: ./special-roles-follow-the-model-table/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:special-roles-follow-the-model-table:backlog:1
                briefing: briefing:special-roles-follow-the-model-table:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-01T17:48:13.754386Z"
                decision: approve
                reason: The Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering the batch 12 sitting 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」; approves Pilot, this outcome and these bounds, with the stated change.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:special-roles-follow-the-model-table:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:special-roles-follow-the-model-table-ideation-1
              briefing:
                id: briefing:special-roles-follow-the-model-table:ideation:attempt-1:revision-1
                digest: sha256:b05649e7beaf13b68e0bf9a99390db658ea137c77a7ff9986bdb62cff917c696
                room-ref: ./special-roles-follow-the-model-table/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:special-roles-follow-the-model-table:ideation:1
                briefing: briefing:special-roles-follow-the-model-table:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-02T03:30:56.911148Z"
                decision: revise
                reason: 'The Captain 「可以」 (chat, 2026-11-02), answering 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」; accepts the direction and asks: D1 an Astra call clears the Fable floor; D2 a chief-engineer call needs opus rank; D3 yes, the template moves ideation and validation to Opus; D4 yes, retire design-director-model-follows-task and leave release-walk passes; D5 a family other than the implementation workers, changing all workers to implementation workers in references/sd/workflow.md at zero words; correct the claim that no log shows effort, because subagent transcripts carry perTurnEffort, and make AC-5 assert xhigh; correct line 81; order before second-round-prompts-a-step-back.'
            - id: gate-attempt:special-roles-follow-the-model-table-ideation-2
              briefing:
                id: briefing:special-roles-follow-the-model-table:ideation:attempt-2:revision-1
                digest: sha256:1833b337ceee43c359355beed816a7e173714071e639b613574dbab08d429163
                room-ref: ./special-roles-follow-the-model-table/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:special-roles-follow-the-model-table:ideation:2
                briefing: briefing:special-roles-follow-the-model-table:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-11-02T04:29:36.017525Z"
                decision: approve
                reason: The Captain 「照建議」 (chat, 2026-11-02), answering 「決定：五張設計進實作、Gemini 這張停在這裡，四個決定都照建議嗎？要改哪件直接說。」; accepts the recommendations stated in that sitting, including D5 for the roster and D1 and D2 for completion.
              application:
                target-stage: implementation
                state: consumed
started: 2026-11-02T04:40:41Z
worktree: .worktrees/spacedock-ensign-special-roles-follow-the-model-table
pr: iamcxa/kc-claude-plugins#764
---

## Scope

- Source: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, items 3 and 5. The Captain, chat 2026-11-02: 「我認為 codex 的實作者可以預設比 claude 多高一個推理等級，例如 Sonnet / high，對應 Sol / xhigh，總監也是」 and 「不要用到 max，最高就是 xigh 就好」.
- The table he approved:

| Role | On Claude | On Codex |
|---|---|---|
| implementation | Sonnet / high | Sol / xhigh |
| chief-engineer | Opus / xhigh | Astra / xhigh |
| engineering-reviewer | Opus / xhigh | Astra / xhigh |
| design-director | Sonnet / high | Sol / xhigh |
| ideation | Opus / high | Astra / xhigh |
| validation | Opus / high | Astra / xhigh |
| observer | Sonnet / high | Sol / high |

- Chief-engineer and engineering-reviewer run on a different family from the workers; so usually Opus / xhigh here, Astra / xhigh when the workers are Claude.
- Bite: `role_triggers.py` ranks Claude model names only, so a Codex engineering-reviewer call on 2026-10-30 had to be recorded as a waiver (`_archive/peers-paseo-rule-matches-practice.md`, FO alignment). `agents/design-director.md` and FO's notes disagreed on its model.
- Consumer: every FO dispatching a special role.
- Upstream first: `agents/*.md`, `scripts/role_triggers.py`, `references/sd/workflow.md` Stages.

## Non-goals

- Host changes; automatic model substitution; changing when a role is called.

## Budget

- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition

- A Reviewer line naming a table model on either family clears its event; a cheaper one does not. Each role's declared settings and the workflow text agree with the table.

## FO alignment

Alignment: needed before ideation; the scope is the Captain's ruling.
Result: aligned at backlog: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Base: `origin/main` 146727ded, kc-dev-flow-2 0.34.0. Probes ran on 2026-11-02 against disposable copies; no repository file changed. This revision carries the Captain's gate rulings of 2026-11-02, D1 to D5 below.

### PRFAQ

**Proposition.** An FO looks up one table to know what a special role or stage worker runs on, a Reviewer line naming a table model clears its event on either family, and the effort each special role declares reaches Claude Code.

**Why does effort need a change when the agent files already say xhigh?** Claude Code does not read the field they use. Its docs list `effort`, with no `reasoning` field, and say unrecognized fields are ignored (code.claude.com/docs/en/sub-agents, Frontmatter reference). `claude -p ... --debug-file` (2.1.316) logged, for all four kc-dev-flow-2 0.34.0 agents, `has a frontmatter key Claude Code does not recognize or apply: "reasoning"`; a probe agent with `effort: high` logged no such line. Subagent transcripts carry `perTurnEffort`, and they show the result: across `~/.claude/projects` on this machine on 2026-11-02, every record of 28 chief-engineer agents reads `high` and of 46 engineering-reviewer agents 43 read `high` and 3 carry no value, against a declared `xhigh`. That is one machine's history. A candidate copy using `effort:` ran as declared under a session at another level: chief-engineer and engineering-reviewer on `claude-opus-5-5` at `xhigh`, design-director and observer on `claude-sonnet-5-5` at `high`. Base ran chief-engineer at the session's `high`.

**Does this make Codex automatic?** No. `dispatch build --host codex` printed `declared model 'opus' ignored on host codex` and emitted `model=null`, and no agent file reaches Codex. The Codex column is what FO passes by hand on the Paseo route; the check only reads what was recorded.

**What about the other agent-file sentence?** "Explicitly request the highest available reasoning level" would pick `ultra` on Codex (`list_models codex`), against 「不要用到 max，最高就是 xigh 就好」. It goes.

**Does the agent file settle the model?** Not alone. A parent that passed `model: haiku` on its Agent call got Haiku at `xhigh`, so the file's model holds when the dispatch passes none, and the workflow's "never cheaper" and the Reviewer line carry the rest. The check reads the recorded line, not the transcript.

**What stays out?** Host changes, automatic substitution, when a role is called, refusing `max` or `ultra` anywhere (the Captain's batch ruling), and the effort of stage workers, which has no dispatch field on Spacedock's route and stays with the backlog seed `dispatch-sets-reasoning-effort`.

```mermaid
flowchart TD
    FO[FO dispatches a special role] --> T[Reads the Model table row]
    T -->|Claude host| C[Agent file sets model and effort]
    T -->|Codex through Paseo| P[FO passes model and thinking by hand]
    C --> R[FO records the Reviewer line under FO alignment]
    P --> R
    R --> K{role_triggers.py ranks the named model}
    K -->|at or above the floor, dated in time| OK[Event clears]
    K -->|below the floor or unknown| OWED[next: line names both families; event stays owed]
```

### Upstream first

- Spacedock: a per-state `model:` works (`[build] effective_model=opus (from stage)` on a disposable workflow); `effort:` on a state is not emitted, and `dispatch build` has no effort field or flag.
- kc-dev-flow-2: `AGENT_MODELS` in `lint-skills.py` already pins the Claude column of the four agents, on the dead field; `RANK` and `rank` in `role_triggers.py` are the check. Both are repaired, not replaced. `model_roster.py` covers stage workers only.
- Sibling adopters: no `docs/dev/README.md` under `~/conductor/repos` (qnow and its worktrees among them) sets a per-stage `model:` or `effort:`. The relay and web repositories have no checkout there and were not read.
- `kc-dev-flow` (v1) agents carry the same dead field; out of scope.

### Each agent file against the table

| Role | Table, Claude | File today | Applies today? | Change |
|---|---|---|---|---|
| chief-engineer | Opus / xhigh | `model: opus`, `reasoning: xhigh` | model yes, effort no | `effort: xhigh`; body sentence below |
| engineering-reviewer | Opus / xhigh | `model: opus`, `reasoning: xhigh` | model yes, effort no | `effort: xhigh`; body sentence below |
| design-director | Sonnet / high | `model: sonnet`, `reasoning: high` | model yes, effort no | `effort: high` |
| observer | Sonnet / high | `model: sonnet`, `reasoning: high` | model yes, effort no | `effort: high` |

Body sentences, replacing "Run as Claude Opus … before advising/giving judgment": chief-engineer `Run on Claude Opus or Codex gpt-6-astra, at xhigh and no higher.`; engineering-reviewer `Run on Claude Opus, Codex gpt-6-astra or a stronger model the dispatch names, at xhigh and no higher.` The director and observer wrappers keep "adds no policy"; FO chooses their model from the table.

### Reviewer rank

`RANK` gains `"astra": 3`, the same rank as `fable` (decision D1). Sol, Terra and Luna get no entry: every floor is opus or above, so a Sol rank would change no result, and an unknown word already ranks -1 and clears nothing. `rank` takes the first word of the model token that is in `RANK` instead of only the leading word, which is what makes `gpt-6-astra` readable and also fixes `claude-opus-5-5`, Paseo's own id, which ranks -1 today.

Chief-engineer calls gain a floor of opus rank (decision D2): base clears one on any model. Waivers and the date rules do not change. The `next:` lines say `on opus or gpt-6-astra` (or `on fable or gpt-6-astra (...)`), and the record template says `<model>` instead of the required model, so an FO on Astra is not told to write opus.

Prototype replay: base and candidate on all 182 tasks of `spacedock-state/dev2`, at its HEAD during this stage, gave 0 changed results. `peers-paseo-rule-matches-practice` without its 2026-11-01 waiver owes the amendments at base and clears on the candidate; with `gpt-6.1-sol` swapped in it stays owed; as `profile: prod`, Astra clears and `opus` stays owed. `test_role_triggers`, `test_pr_watch` and `test_delivery_gate` passed against the prototype before any test edit (25, 129 and 119 tests).

### Table and workflow sentence

The table goes in `references/model-roster.md` as `## Model table`, the seven rows verbatim, because the Stages section already points FO there and `workflow.md` has no spare words. Beneath it: the Codex column goes through Paseo's `settings.thinkingOptionId`, and the family rule: chief-engineer and engineering-reviewer run on a family other than the implementation workers' (D5). "This slice adds no … special-role hosting" loses those two words. `lint-skills.py` reads the field `effort` and refuses a table row whose Claude cell for one of the four agents differs from `AGENT_MODELS`, so the table and the agent files cannot drift apart. No check caps effort in a roster.

`references/sd/workflow.md`, Stages, before:

> `kc-dev-flow-2:chief-engineer`, `kc-dev-flow-2:engineering-reviewer` and `kc-dev-flow-2:observer` run on the model and reasoning their agent files declare, never a cheaper one.

After:

> `kc-dev-flow-2:chief-engineer`, `kc-dev-flow-2:engineering-reviewer`, `kc-dev-flow-2:design-director` and `kc-dev-flow-2:observer` run on its `## Model table` row, never cheaper.

Same file, the review sentence (line 81 at base), before: `use a different family from all workers or ask the Captain`. After: `use a different family from implementation workers or ask the Captain`.

Frontmatter gains `model: opus` on `ideation` and `validation` (decision D3); `implementation` keeps the `sonnet` default. This also names the design director, which the old sentence omitted. Package `README.md` "Opus/xhigh policy" becomes "model table row". The `high` half of the stage rows has no dispatch field on Spacedock's route, so it stays a stated limit until `dispatch-sets-reasoning-effort` lands.

Existing-code check: all of this repairs existing fields, one existing dictionary and one existing sentence. The observation showing need is the debug-log line and the waiver in `_archive/peers-paseo-rule-matches-practice.md`.

### ADR drafts

No number; FO reserves it.

- Amend ADR 0026 (`role-calls-are-owed-on-counts-read-from-task-records-and-a-dated-call-clears-them`): Astra meets the Fable floor (D1), and a chief-engineer call counts only at opus rank or above (D2).
- New, short title `special-roles-and-stage-defaults-follow-one-model-table`: the Captain's table and words from Scope, `effort` as the field that carries it on Claude Code, the family rule (D5), and the table replacing the 2026-10-23 per-task director rule (D4).

### Files changed

`agents/chief-engineer.md`, `agents/engineering-reviewer.md`, `agents/design-director.md`, `agents/observer.md`, `scripts/role_triggers.py`, `scripts/test_role_triggers.py`, `scripts/lint-skills.py`, `scripts/test_lint_skills.py`, `scripts/test_sd_dispatch.py` (the `reviewer-record` fixture quotes the old sentence), `references/model-roster.md`, `references/sd/workflow.md`, `README.md`, and `docs/adr/` (one amended, one new). The first twelve are under `kc-dev-flow-2/`. `scripts/release_acceptance.py` and `extensions/release-acceptance/` do not change. Retiring the seed `design-director-model-follows-task` is FO's state action and changes no repository file.

### The Captain's rulings

From the newest ideation resolution, 2026-11-02. Past rulings read: `docs/adr/` at 146727ded (0021, 0022, 0026, 0030, 0033, 0047) and `git grep 'Override:'` in the state checkout; no `Override:` line concerns a model floor.

- **D1. An Astra call clears the Fable floor.** ADR 0026 D4's floor stays for Claude. Worse: Astra counts as equal to Fable with no measurement, and an Opus call on a `profile: prod` or `Surfaces: db` task still does not clear, so the Stop condition's "a table model clears" holds for Opus on pilot only.
- **D2. A chief-engineer call needs opus rank.** All 35 recorded chief-engineer calls name opus, so nothing recorded changes. Worse: a real call made on Sonnet must be redone or waived.
- **D3. The template moves ideation and validation to Opus.** Worse: every adopter's ideation and validation move to Opus at its next sync, at a cost not measured, and the `high` half is not applied.
- **D4. The table replaces the 2026-10-23 rule for per-task director passes; the seed `design-director-model-follows-task` is retired; release-walk passes stay under ADR 0033.** Worse: with Opus ideation, `ra director-model` prints opus for nearly every Claude-designed walk, about twice the duration by ADR 0022's measurement, while a walk designed on Astra prints sonnet because its match reads only "opus". That asymmetry needs its own task if it bites.
- **D5. The family rule reads "other than the implementation workers", and `references/sd/workflow.md` says the same.** "Line 81" in the ruling is read as line 81 of that file, the sentence the chief-engineer review named with this swap; line 81 of this task file was blank at the commits that review could read (001a9c260, efe03a527). The earlier "Batch gates sentence stays unchanged" is withdrawn. Worse: Opus may review an Opus-written design.

### Decisions for the Captain

None open.

### Beyond the asks

Nothing here changes behaviour past the rulings. Three additions follow from them and are named so they can be struck: AC-5 also asserts the model and all four roles; AC-10 is new evidence for D4; the FAQ records that an Agent `model` argument overrides the file, with no change made for it.

### Words FO reads at each moment

Whitespace split, the counter `lint-skills.py` compares with the budget (base count 5781 equals its budget).

| Moment | Before | After |
|---|---|---|
| Startup and resume (`workflow.md`) | 5781 | 5781, measured on a candidate copy: the sentence goes from 18 words to 14, the two frontmatter lines add 4, the family sentence swaps one word for one; no `WORKFLOW_BUDGET_STEPS` step |
| Stage launch (`model-roster.md`) | the file today | + `## Model table`: 7 rows and about 40 words of note, read only by an FO that opens it; the first special-role dispatch now opens it too |
| Chief-engineer dispatch (agent body) | 23 words | 12 |
| Engineering-reviewer dispatch (agent body) | 31 words | 18 |
| Director and observer dispatch | unchanged | unchanged; one frontmatter key renamed |
| Idle and delivery hold (`next:` line, an event owed) | the line today | +2 words (`or gpt-6-astra`) per owed role |
| Idle, nothing owed | unchanged | unchanged |

### Batch overlap

| Task | Shared | Effect |
|---|---|---|
| worker-completion-reaches-fo-on-paseo | no design yet; its Scope keeps the rule in `extensions/paseo/EXTENSION.md`. Possibly the `workflow.md` `main` sentence and `model-roster.md` | Other sentence; recount the budget if it edits `workflow.md` |
| model-roster-question-needs-both-families | `references/model-roster.md`, different sections; its D4 is this task's D5 wording, and its design leaves that `workflow.md` sentence to this task; D3 feeds its D5; ADR index | Direct: it lands first, this task rebases `model-roster.md` |
| second-round-prompts-a-step-back | `scripts/role_triggers.py` `owed_line` and `check`, `scripts/test_role_triggers.py`, an ADR 0026 amendment | Direct: it lands after this task, on the changed `owed_line` |
| validation-gate-requires-the-question-check | ADR index; its design leaves `workflow.md` and `role_triggers.py` alone, and `delivery_gate.py` `check` calls the changed script | Index only |
| picky-reviewers-may-run-on-gemini | none: `extensions/release-acceptance/EXTENSION.md`, which D4 leaves alone; a director-model change is its non-goal | None |
| adoption-asks-which-extensions | `workflow.md` untouched per its AC-7 | None |
| adr-required-statement | `references/sd/workflow.md` other sections; `docs/adr/` numbering; `lint-skills.py` budget steps if it raises | Shared index; this task's edit nets 0 words on any base |
| comment-check-reaches-delivery-gate | `delivery_gate.py` runs `role_triggers.py`, which it does not edit | None; its hold text prints the longer `next:` line |
| ops-inbox-r1-setup-and-isolation | `docs/adr/` numbering (its AC-6) | Shared index; FO's reserved number covers it |
| adr-silent-undo-probe, journey-canvas-hosted-poc, pr-review-lite-value-pilot | no design file of this task is named in these task files (grep for `role_triggers`, `model-roster`, `lint-skills` and `sd/workflow.md`, 2026-11-02) | None |
| journey-server-host-pilot | no task file by this name at the state checkout's HEAD on 2026-11-02; not read | Unknown; FO names its location if it matters |

Recommended order: worker-completion-reaches-fo-on-paseo, model-roster-question-needs-both-families, this task, second-round-prompts-a-step-back, validation-gate-requires-the-question-check. This task goes before second-round-prompts-a-step-back by the Captain's ruling.

## Acceptance criteria

**AC-1** A call naming a table model clears an engineering-reviewer event and a cheaper one does not. Verified by: `python3 -B -m unittest test_role_triggers` from `kc-dev-flow-2/scripts` with `test_a_call_below_the_required_model_does_not_clear` extended: pilot clears on `gpt-6-astra`, `claude-opus-5-5`; stays owed on `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-6-luna`, `claude-sonnet-5-5`; prod clears on `gpt-6-astra`, `fable`, `claude-fable-5-1`; stays owed on `opus`, `claude-opus-5-5`. Falsifiers: remove `astra` from `RANK` and the Astra cases fail; restore the leading-word `rank` and `claude-opus-5-5` fails.

**AC-2** A chief-engineer call below opus rank leaves its event owed; opus, Astra and a waiver clear it. Verified by: new `test_role_triggers.py` cases for the repair event and the review-round event with `sonnet`, `gpt-6.1-sol`, `opus`, `gpt-6-astra` and a waiver. Falsifier: remove the floor filter and the `sonnet` case fails.

**AC-3** Recorded history keeps its result, and the Bite's case clears without its waiver. Verified by: a one-off replay at validation of base and candidate `check` on every task of `spacedock-state/dev2` at a named commit, reporting 0 changed results or naming each; and a test fixture of that task's shape, `gpt-6-astra` calls with no waiver, exit 1 at base and exit 0 on the candidate. Falsifier: the same fixture with `gpt-6.1-sol` exits 1 on the candidate.

**AC-4** An owed line names both families and leaves the model open. Verified by: `test_role_triggers.py` asserts `on opus or gpt-6-astra` and `on fable or gpt-6-astra (profile prod)` and `<model>` in the record template; `test_pr_watch.py` and `test_delivery_gate.py` pass, running the real script. Falsifier: revert the wording and the assertion fails.

**AC-5** Each role runs at the table's Claude effort and model. Verified by: on the candidate, `claude -p '<one Agent call per role, no model argument>' --plugin-dir <candidate>/kc-dev-flow-2 --debug-file <log> --model sonnet --effort medium --allowedTools Agent --output-format json`, then read `perTurnEffort` and each assistant `model` from `~/.claude/projects/*/<session_id>/subagents/*.jsonl`, naming each by `agentType` in its `.meta.json`. Chief-engineer and engineering-reviewer read `xhigh` and `claude-opus-5-5`; design-director and observer read `high` and `claude-sonnet-5-5`. `grep 'does not recognize or apply' <log>` shows no line for a candidate `kc-dev-flow-2` agent, against four at base 0.34.0. Falsifier: put `reasoning: xhigh` back in chief-engineer; its line returns and its records read the session's level. Limit: `perTurnEffort` is what Claude Code recorded for the turn; a dispatch passing `model` overrides the file.

**AC-6** The table holds the seven approved rows and cannot drift from the agent files. Verified by: `python3 kc-dev-flow-2/scripts/lint-skills.py` exits 0; `test_lint_skills.py` changes one Claude cell and one agent `effort`, each refused, and a roster naming `max` is still accepted by `model_roster.py`. Falsifier: remove the table comparison and the changed-cell case fails.

**AC-7** Workflow text names all four roles, the family sentence names implementation workers, and the word count stays 5781. Verified by: `lint-skills.py` exits 0 with no new `WORKFLOW_BUDGET_STEPS` entry; `git diff` of `references/sd/workflow.md` shows the two sentences and two frontmatter lines; `grep -c 'from implementation workers'` prints 1 and `grep -c 'from all workers'` prints 0; `test_sd_dispatch.py` `reviewer-record` passes on the new sentence. Falsifiers: drop `kc-dev-flow-2:design-director` from the sentence and that fixture fails; restore `all workers` and the first count prints 0.

**AC-8** Stage defaults reach dispatch (D3). Verified by: `spacedock dispatch build` on a disposable copy of the template emits `model` `opus` for ideation and validation and `sonnet` for implementation with `--host claude`, and `null` with `--host codex`. Falsifier: remove the state's `model:` and the build reports `from defaults` with `sonnet`.

**AC-9** The rulings are recorded. Verified by: `python3 kc-dev-flow-2/scripts/adr_lint.py docs/adr` exits 0, ADR 0026 carries the amendment, and the new ADR carries the Captain's words from Scope. Falsifier: `adr_lint.py --require <number>` exits nonzero with the record missing.

**AC-10** Release-walk passes stay and the seed is retired (D4). Verified by: `git diff --stat origin/main -- kc-dev-flow-2/scripts/release_acceptance.py kc-dev-flow-2/extensions/release-acceptance` is empty; `spacedock status` lists `design-director-model-follows-task` no longer in backlog once FO retires it. Falsifier: the seed still at `backlog` after this task's merge fails it.

## Number guards

ADR: 0049

## Stage Report: ideation

- DONE: A design for this task's Scope: the Reviewer rank for Codex models, each agent file against the table, and the workflow sentence that names them
  `## Design`: `astra` ranks with `fable`, `rank` reads any word of the token; all four agents move from the unrecognized `reasoning` to `effort`; one sentence names all four roles and points at `## Model table`. Prototype only, in /tmp; no repository file changed.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (model-roster-question-needs-both-families, second-round-prompts-a-step-back, validation-gate-requires-the-question-check, special-roles-follow-the-model-table) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Direct overlap with the roster task (`model-roster.md`) and the step-back task (`role_triggers.py`); recommended order stated. `### Files changed` lists the files.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: workflow 5781 to 5781 measured on a candidate copy; agent bodies 23 to 12 and 31 to 18; +2 words per owed `next:` line. The "about 40 words" of table note is an estimate. Table form follows root learning.md § Measure the words FO reads at each moment.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-9 below; D1 to D5 under `### Decisions for the Captain`.
- DONE: AC-1 current evidence: prototype `rank` gave astra 3, claude-opus-5-5 2, gpt-6.1-sol, terra and luna -1; Astra clears pilot and prod, `opus` stays owed on prod. Test edits not yet written.
- DONE: AC-2 current evidence: prototype floor passed the three existing suites; no chief-engineer floor case has run. Not yet verified.
- DONE: AC-3 current evidence: 182 tasks, 0 changed; waiver-removed task exit changed from owed to clear on the prototype, Sol stays owed. Fixture not yet written.
- DONE: AC-4 current evidence: none; wording is designed, not prototyped. Not yet verified.
- DONE: AC-5 current evidence: at base, debug log names `reasoning` as unrecognized for all four 0.34.0 agents; `effort` probe logged no line. Candidate run not yet verified; effort actually used was not observable in two attempts.
- DONE: AC-6 current evidence: `lint-skills.py` pins `AGENT_MODELS` today; table check not yet written. Not yet verified.
- DONE: AC-7 current evidence: whitespace count of a candidate copy is 5781; lint itself could not run from my /tmp extract (it needs the repository's `skill-frontmatter-lint.sh`). Not yet verified.
- DONE: AC-8 current evidence: disposable workflow built `opus (from stage)` and `sonnet (from defaults)` on Claude, `model=null` on Codex. Template copy not yet verified.
- DONE: AC-9 current evidence: drafts named, no number. Not yet verified.
- DONE: `design_surfaces.py check` on this file: `design surfaces presentable`, exit 0.

### Summary

The trigger check needs one rank entry and a wider word match to accept Astra, and a replay of 182 recorded tasks changed nothing. The larger finding is that Claude Code ignores the `reasoning` field all four agents use, so their declared effort has never applied; the design renames it to `effort`. Five decisions go to the Captain, chiefly whether Astra meets the Fable floor and whether the template moves ideation and validation to Opus. Proof of the effort a run actually used stays open and belongs to `dispatch-sets-reasoning-effort`.

## Stage Report: ideation (cycle 2)

- DONE: Revise the design under the Captain gate revise of 2026-11-02: the asks are in the reason of the newest ideation resolution in this task file; do exactly those asks, and name anything that would go beyond them
  D1 to D5 are recorded as rulings under `### The Captain's rulings`; the effort claim and AC-5 are corrected; `### Beyond the asks` names three additions. "Line 81" is read as `references/sd/workflow.md` line 81; the D5 entry gives the reason, and FO should say if another line was meant.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (worker-completion-reaches-fo-on-paseo, model-roster-question-needs-both-families, special-roles-follow-the-model-table, second-round-prompts-a-step-back, validation-gate-requires-the-question-check, picky-reviewers-may-run-on-gemini) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Direct overlap with the roster and second-round tasks; this task goes before second-round. New: ops-inbox shares the ADR index, which the earlier table missed. `journey-server-host-pilot` has no task file at the state checkout's HEAD, so it was not read.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: workflow 5781 to 5781 measured on a candidate copy with all three edits; the "about 40 words" of table note is still an estimate.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-10; no decision is open, and each ruling keeps what gets worse under it.
- DONE: AC-1 current evidence: first-cycle prototype `rank` gave astra 3, claude-opus-5-5 2, gpt-6.1-sol, terra and luna -1. Test edits not yet written.
- DONE: AC-2 current evidence: prototype floor passed the three existing suites in cycle 1; no chief-engineer floor case has run. Not yet verified.
- DONE: AC-3 current evidence: cycle 1 replay, 182 tasks, 0 changed; not rerun on this cycle's state. Fixture not yet written.
- DONE: AC-4 current evidence: none; wording is designed, not prototyped. Not yet verified.
- DONE: AC-5 current evidence: candidate copy (`reasoning` renamed to `effort`) under `--effort medium` gave engineering-reviewer `xhigh` on claude-opus-5-5, design-director and observer `high` on claude-sonnet-5-5; under `--effort high` chief-engineer `xhigh` on claude-opus-5-5, and base `high`. Debug log: four unrecognized lines at base, zero on the candidate. Probe copies only, not the implementation; the `reasoning` falsifier at `--effort medium` has not run.
- DONE: AC-6 current evidence: `lint-skills.py` pins `AGENT_MODELS` today; table check not yet written. Not yet verified.
- DONE: AC-7 current evidence: whitespace count of a candidate copy is 5781 with all edits; `all workers` occurs once in the package, at workflow.md line 81, and no script pins it. `lint-skills.py` not run on a candidate. Not yet verified.
- DONE: AC-8 current evidence: cycle 1 disposable workflow built `opus (from stage)` and `sonnet (from defaults)` on Claude, `model=null` on Codex. Template copy not yet verified.
- DONE: AC-9 current evidence: drafts named, no number. Not yet verified.
- DONE: AC-10 current evidence: the seed is at `backlog` today and no release-acceptance file is in `### Files changed`. Not yet verified.
- DONE: `design_surfaces.py check` on this file: `special-roles-follow-the-model-table.md: design surfaces presentable`, exit 0.

### Summary

The design now carries the Captain's five rulings and his three corrections. The claim that no log shows effort was false: transcripts record it, none of the recorded reviewer turns here reached `xhigh`, and a candidate copy ran each role at its declared effort, so AC-5 now asserts `xhigh`. Remaining: that an Agent `model` argument still overrides the file is recorded as a limit, and "line 81" is my reading, stated for FO to correct.

## Stage Report: implementation

- DONE: Implement the approved design; only the files the design names
  Code branch `spacedock-ensign/special-roles-follow-the-model-table`, base `c129cb215c2630d08853eeffae0fd5a2ee7e40c6`, candidate `d14c5ae3b0c9f14eb89cd38a2fb500b2a57119fa`; 14 named files, no version bump, clean code tree.
- SKIPPED: One Draft PR stacked on PR #763
  No PR opened: no push grant. Live #763 is Draft/open at the named base; this branch has no open PR. FO owns push and Draft creation; title/body at `/tmp/impl-special-roles-follow-the-model-table-pr.md`, base branch `spacedock-ensign/worker-completion-reaches-fo-on-paseo`.
- DONE: ADR 0049 records the ruling the design names, quoting the Captain's words from the task file and its gate records
  Added `docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md`, with D1–D5, quoted Words/Asked and protection pointers; appended the approved model-floor amendment to ADR 0026.
- DONE: AC-1: Engineering-reviewer accepts the table models and rejects cheaper calls
  `python3 -B -m unittest test_role_triggers`: 27 pass; pilot Astra/prefixed Opus clear, Sol/Terra/Luna/Sonnet stay owed; prod Astra/Fable clear, Opus stays owed. Removing Astra fails 2 cases; leading-word rank fails 4 (`/tmp/special-roles-implementation/mutations.log`).
- DONE: AC-2: Chief-engineer needs opus rank for repairs and review rounds
  Both event paths exercised with Sonnet, Sol, Opus, Astra and waiver; removing the floor fails 4 cases. Date and waiver regressions pass in the same suite.
- DONE: AC-3: Historical results and the real waived case
  `/tmp/special-roles-implementation/replay.py`: all 184 task files at state `e9c2df74f01cfe7c181f93406a681d89f89e6584`, 0 changed exits; actual peer-policy task minus its waiver: base 1/candidate 0, Sol mutation 1; result rows in `replay-results.json` beside the script.
- DONE: AC-4: Owed lines name both families and leave the recorded model open
  Role tests assert both floors and `<model>`; `test_pr_watch` and `test_delivery_gate` run the real script. Reverting family wording fails 6 cases; all 322 tests across those suites plus skill lint pass on the candidate (`exact-head-unit.log` in the evidence directory).
- DONE: AC-5: Actual Claude model and perTurnEffort reach all four roles
  Candidate session `76d6cece-b168-4c1b-a042-579620483668`: Opus/xhigh for chief-engineer and engineering-reviewer, Sonnet/high for director and observer; four Agent calls without model arguments. `/tmp/special-roles-implementation/native-evidence.json` binds agentType, transcripts and turns; scoped warnings candidate 0/base 4. Base session `a8e828f4-6f73-4af4-8564-91f7dd39cd2a` records medium; reasoning mutation session `1e4d5c54-443c-43c4-9155-c38703965874` restores medium and one warning. Initial sandbox login failure was resolved with native access; no credentials read. An explicit dispatch model can override the file.
- DONE: AC-6: Seven approved rows, effort lint and explicit max acceptance
  Repository lint passes; changed Claude table cell and agent effort are refused; removing the table comparison fails its mutation test. Real resolver accepts committed max and ultra rosters (`roster-effort-controls.log`); no effort cap added. The separately owned adoption-recommendation discrepancy is retained under RoboRev below.
- DONE: AC-7: Four roles, implementation-worker family wording and 5781 words
  Repository lint: 5781/5781, no budget step; family phrase counts 1/0. Real `test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3 --keep` passes; dropping director breaks reviewer-record, restoring all-workers yields phrase count 0 (`dispatch-controls.log`). Workflow words stay 5781; model-roster.md 634→760; complete agent files chief-engineer 129→122 and reviewer 188→179.
- DONE: AC-8: Stage defaults reach actual Spacedock dispatch
  Disposable template builds: Claude ideation/validation opus, implementation sonnet; Codex null for all three. Removing either opus state emits sonnet/from defaults. `/tmp/special-roles-implementation/dispatch-controls.log`; raw CLI evidence at `/private/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/dev-flow-2-sd-l4wp13y5/commands.jsonl` (binary reports 0.27.2).
- DONE: AC-9: Decision lint and missing-record falsifier
  `python3 -B <package>/scripts/adr_lint.py docs/adr --since c129cb215c2630d08853eeffae0fd5a2ee7e40c6 --require 0049`: exit 0, 48 ADR files/0 legacy; empty disposable ADR folder with --require 0049 exits 1, required record missing (`adr-missing-control.log`).
- DONE: AC-10: Release-walk code and extension remain unchanged
  `git diff --stat origin/main -- kc-dev-flow-2/scripts/release_acceptance.py kc-dev-flow-2/extensions/release-acceptance` is empty.
- SKIPPED: AC-10: Retire design-director-model-follows-task after merge
  The seed is still backlog; retiring it is FO's state action, explicitly outside this worker's scope. No post-merge retirement or its falsifier is claimed complete.
- DONE: Repository lint, number guard, comment ratio and design check
  Repository `lint-skills.py` exit 0; <package> number_guards check with the assigned --base: PASS/no findings; comment_ratio base..HEAD 61 code/2 comments, 3.3% ≤ 5%; design_surfaces check exit 0. <package> is `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`.
- SKIPPED: Clean RoboRev verdict and all acceptance criteria green
  Native check exits 1: `findings on d14c5ae3b; evidence=roborev:1397`. High: model-roster.md's xhigh table differs from the still-high `references/model-roster-defaults.json` recommendation. Fix requires a file absent from this design's implementation list; no unapproved edit or retry. The approved sibling `model-roster-question-needs-both-families` owns that JSON and its Opus/high, Sol/xhigh, Astra/xhigh offer (current status implementation). FO must integrate that prerequisite and rerun review; the recommendation on this isolated candidate is not accepted as clean. The initial sandbox-only attempt printed `incomplete: the roborev daemon is not running`; native review produced the bound finding above.
- DONE: Affected-document dispositions
  Updated: ADR 0049 and kc-dev-flow-2/README.md. Unaffected: ADR 0020 (no budget change); ADR 0037 (shared-work rule unchanged); references/sd/adoption.md (dispatch test scope unchanged); skills/maintain-flow/SKILL.md (same commands and budget contract); learning.md (historical evidence unchanged). `doc_impact.py base HEAD` lists these seven documents.
- DONE: CI cost measured or stated as not measured
  CI cost per PR not measured; no CI trigger changed. Stage-model cost increase not measured. Product publication, hosted CI and independent validation remain with FO; local/native checks do not establish those outcomes.

### Summary

The approved role settings, model-floor behavior, table/workflow text and ADRs are locally committed with behavioral and mutation evidence. No product push or PR was made; FO retains sibling integration for RoboRev High 1397, publication, independent validation/CI and the old director seed's retirement. This report claims the bounded implementation and its listed checks, not a clean delivery gate.

## Stage Report: implementation

- DONE: Implement the approved design; only the files the design names
  Code branch `spacedock-ensign/special-roles-follow-the-model-table`, base `c129cb215c2630d08853eeffae0fd5a2ee7e40c6`, candidate `562b1a87198d97bb2ae1d87b72884e390b20e146`; 15 authorized files (the CI repair dispatch adds test_poc_readme.py), no version bump, clean code tree.
- DONE: One Draft PR stacked on PR #763
  FO opened https://github.com/iamcxa/kc-claude-plugins/pull/764, observed Draft/open with base branch `spacedock-ensign/worker-completion-reaches-fo-on-paseo` and published head d14c5ae3b. This worker made no product push; the one follow-up commit is local for FO.
- DONE: ADR 0049 records the ruling the design names, quoting the Captain's words from the task file and its gate records
  Added `docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md`, with D1–D5, quoted Words/Asked and protection pointers; appended the approved model-floor amendment to ADR 0026.
- DONE: AC-1: Engineering-reviewer accepts the table models and rejects cheaper calls
  `python3 -B -m unittest test_role_triggers`: 27 pass; pilot Astra/prefixed Opus clear, Sol/Terra/Luna/Sonnet stay owed; prod Astra/Fable clear, Opus stays owed. Removing Astra fails 2 cases; leading-word rank fails 4 (`/tmp/special-roles-implementation/mutations.log`).
- DONE: AC-2: Chief-engineer needs opus rank for repairs and review rounds
  Both event paths exercised with Sonnet, Sol, Opus, Astra and waiver; removing the floor fails 4 cases. Date and waiver regressions pass in the same suite.
- DONE: AC-3: Historical results and the real waived case
  `/tmp/special-roles-implementation/replay.py`: all 184 task files at state `e9c2df74f01cfe7c181f93406a681d89f89e6584`, 0 changed exits; actual peer-policy task minus its waiver: base 1/candidate 0, Sol mutation 1; result rows in `replay-results.json` beside the script.
- DONE: AC-4: Owed lines name both families and leave the recorded model open
  Role tests assert both floors and `<model>`; `test_pr_watch` and `test_delivery_gate` run the real script. Reverting family wording fails 6 cases; 1009 unit tests from the complete CI job: 1002 pass, 7 skipped (26 commands, including lint and both Spacedock integration scripts); `/tmp/special-roles-ci-repair/suite-results.json` records each command, count and log. The earlier 322 was only a subset, not the CI suite.
- DONE: AC-5: Actual Claude model and perTurnEffort reach all four roles
  Unchanged agent bytes, verified against d14c5ae3b; its candidate session `76d6cece-b168-4c1b-a042-579620483668`: Opus/xhigh for chief-engineer and engineering-reviewer, Sonnet/high for director and observer; four Agent calls without model arguments. `/tmp/special-roles-implementation/native-evidence.json` binds agentType, transcripts and turns; scoped warnings candidate 0/base 4. Base session `a8e828f4-6f73-4af4-8564-91f7dd39cd2a` records medium; reasoning mutation session `1e4d5c54-443c-43c4-9155-c38703965874` restores medium and one warning. Initial sandbox login failure was resolved with native access; no credentials read. An explicit dispatch model can override the file.
- DONE: AC-6: Seven approved rows, effort lint and explicit max acceptance
  Repository lint passes; changed Claude table cell and agent effort are refused; removing the table comparison fails its mutation test. Real resolver accepts committed max and ultra rosters (`roster-effort-controls.log`); no effort cap added. The separately owned adoption-recommendation discrepancy is retained under RoboRev below.
- DONE: AC-7: Four roles, implementation-worker family wording and 5781 words
  Repository lint: 5781/5781, no budget step; family phrase counts 1/0. The real dispatch suite passes against CI plugin commit 4d158a484ec73e184861067f8ed1e20087fdc26a (`/tmp/special-roles-ci-repair/test_sd_dispatch.log`); dropping director breaks reviewer-record, restoring all-workers yields phrase count 0 (`dispatch-controls.log`). Workflow words stay 5781; model-roster.md 634→760; complete agent files chief-engineer 129→122 and reviewer 188→179.
- DONE: AC-8: Stage defaults reach actual Spacedock dispatch
  Disposable template builds: Claude ideation/validation opus, implementation sonnet; Codex null for all three. Removing either opus state emits sonnet/from defaults. `/tmp/special-roles-implementation/dispatch-controls.log`; raw CLI evidence at `/private/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/dev-flow-2-sd-l4wp13y5/commands.jsonl` (binary reports 0.27.2).
- DONE: AC-9: Decision lint and missing-record falsifier
  `python3 -B <package>/scripts/adr_lint.py docs/adr --since c129cb215c2630d08853eeffae0fd5a2ee7e40c6 --require 0049`: exit 0, 48 ADR files/0 legacy; empty disposable ADR folder with --require 0049 exits 1, required record missing (`adr-missing-control.log`).
- DONE: AC-10: Release-walk code and extension remain unchanged
  `git diff --stat origin/main -- kc-dev-flow-2/scripts/release_acceptance.py kc-dev-flow-2/extensions/release-acceptance` is empty.
- SKIPPED: AC-10: Retire design-director-model-follows-task after merge
  The seed is still backlog; retiring it is FO's state action, explicitly outside this worker's scope. No post-merge retirement or its falsifier is claimed complete.
- DONE: Repository lint, number guard, comment ratio and design check
  Repository `lint-skills.py` exit 0; <package> number_guards check with the assigned --base: PASS/no findings; comment_ratio base..HEAD 63 code/2 comments, 3.2% ≤ 5%; design_surfaces check exit 0. <package> is `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`.
- SKIPPED: Clean RoboRev verdict and all acceptance criteria green
  Native check on the repair head exits 1: `findings on 562b1a871; evidence=roborev:1400` (same scope finding as job 1397). High: model-roster.md's xhigh table differs from the still-high `references/model-roster-defaults.json` recommendation. Fix requires a file absent from this design's implementation list; no out-of-scope edit; no finding concerns the CI test repair. The approved sibling `model-roster-question-needs-both-families` owns that JSON and its Opus/high, Sol/xhigh, Astra/xhigh offer (current status implementation). FO must integrate that prerequisite and rerun review; the recommendation on this isolated candidate is not accepted as clean. The initial sandbox-only attempt printed `incomplete: the roborev daemon is not running`; native review produced the bound findings above; no clean review is claimed.
- DONE: Affected-document dispositions
  Updated: ADR 0049 and kc-dev-flow-2/README.md. Unaffected: ADR 0020 (no budget change); ADR 0037 (shared-work rule unchanged); references/sd/adoption.md (dispatch test scope unchanged); skills/maintain-flow/SKILL.md (same commands and budget contract); learning.md (historical evidence unchanged). `doc_impact.py base HEAD` lists these seven documents.
- DONE: CI cost measured or stated as not measured
  CI cost per PR not measured; no CI trigger changed. Stage-model cost increase not measured. Product publication, hosted CI and independent validation remain with FO; local/native checks do not establish those outcomes.

- DONE: Repair the hosted CI failure in DeriveTests.test_only_the_ideation_entry_and_section_are_removed
  Reproduced 9 tests/1 failure at d14c5ae3b. The derivation already removes the entire ideation entry and keeps validation's Opus setting; replace the adjacent-line assertion with entry-bounded checks for model and gate. test_poc_readme.py: 9 pass; a disposable mutant retaining the removed model fails that exact test (`/tmp/special-roles-ci-repair/mutation.log`, python3 -B, no cached input). poc_readme.py is unchanged.
- DONE: Run the whole package test suite the CI job runs, and correct the report's test count
  All 26 Python commands from .github/workflows/kc-dev-flow-2-tests.yml pass: 1009 unit tests (1002 pass, 7 existing conditional skips) plus skill lint and real dispatch/recovery integration. Spacedock binary 0.27.2; plugin checkout exactly 4d158a484ec73e184861067f8ed1e20087fdc26a, CI's pin. Skipped: four optional design/amendment corpora or historical probes, one optional journey YAML integration, one optional real dispatch builder, one obligation-history corpus; no optional corpus or integration inputs were added for this local replay. Local macOS run, no hosted rerun claimed; no CI trigger change or measured cost per PR. Manifest and command logs: /tmp/special-roles-ci-repair/.
- DONE: One follow-up commit on the assigned branch, no product push
  562b1a87198d97bb2ae1d87b72884e390b20e146 changes only kc-dev-flow-2/scripts/test_poc_readme.py (2 added lines, 1 removed). The repair scope is dispatch/implementation-1-message-1.md. FO owns publishing it and observing hosted CI.

### Summary

This complete report supersedes the previous implementation report, correcting its incomplete suite count and its stale no-PR observation. The CI defect was a positional test assertion; the derivation behavior is unchanged and all 26 local CI commands pass (1002 unit tests pass and 7 conditional tests are skipped). FO retains product push/hosted CI, independent validation, the recorded recommendation finding and old director seed retirement; no clean delivery gate is claimed.

## Stage Report: validation

- DONE: Independent verdict on PR #764 head 562b1a87 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at 562b1a87198d97bb2ae1d87b72884e390b20e146 for pre-merge task scope; no new findings in the workflow's four disposition classes. Per-criterion proof, limits and known external ownership: special-roles-follow-the-model-table/validation-1/details.md.
- DONE: Stacked on PR #763. Base spacedock-ensign/worker-completion-reaches-fo-on-paseo. Hosted CI is green at this head. The earlier RoboRev High on model-roster-defaults.json is owned by PR #765. Do not start agents you were not asked to
  Base c129cb215c2630d08853eeffae0fd5a2ee7e40c6 verified; PR #764 remains Draft/open at the candidate with five SUCCESS checks. Only the explicitly required native role probes ran; no other agents started.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-1/acceptance.sh: six steps, fresh /bin/bash --noprofile --norc, exit 0; full output in acceptance-output.log. Required ADR command with the base above and --require 0049: exit 0, 48 files/0 legacy; resolved Codex package command also passes.
- DONE: AC-1: Engineering-reviewer model recognition and floors
  27 role tests pass; Astra removal fails 2 cases and leading-word restoration fails 4. No candidate product bytes changed; mutations.log.
- DONE: AC-2: Chief-engineer floor on both event paths
  Sonnet/Sol remain owed, Opus/Astra/waiver clear; removing the floor fails 4 cases; mutations.log.
- DONE: AC-3: Historical replay and the real waived case
  184 tasks at state fbf834f07625a7ce05a9393bc64aaa1b6cfe83d8: 0 exit changes, 16 approved wording changes, 0 unexpected changes. Actual peer-policy task without waiver: base 1/candidate 0; Sol falsifier 1; replay-results.json and replay-messages.json.
- DONE: AC-4: Both-family owed lines and open model template
  Role, PR-watch and delivery-gate tests exercised the real script; reverting wording fails 6 cases; mutation and corrected suite logs.
- DONE: AC-5: Actual Claude settings for all four roles
  Session 9531c3e0-bf87-4e67-adf0-5ca975635f5c: Opus/xhigh for engineer/reviewer, Sonnet/high for director/observer, four calls without model arguments, no warnings. Fresh base: four medium/four warnings; reasoning-field mutation: medium/one warning; native-turns.json.
- DONE: AC-6: Seven rows, table/agent drift, explicit effort overrides
  Lint and 47 lint tests pass, changed cell/effort refused, removed table check detected; real committed-roster resolver accepts max and ultra; acceptance-output.log, mutations.log and roster-effort-controls.log.
- DONE: AC-7: Four roles, family sentence and fixed workflow budget
  5781->5781 words, no budget-step change, family phrase counts 1/0; real reviewer-record fixture passes. Removing director yields a gap; restoring all-workers yields count 0; controls.log and words.json.
- DONE: AC-8: Stage defaults reach real dispatch
  Six builds: Claude ideation/validation opus, implementation sonnet; Codex null for each. Removing either opus setting produces sonnet/from defaults; dispatch-stage-controls.log and dispatch-stage-records.json.
- DONE: AC-9: Rulings and missing-record check
  ADR 0026 amendment and ADR 0049 quotes match recorded rulings; candidate/all and installed/changed ADR lint pass. Missing required 0049 returns 1; adr-missing-only.log.
- DONE: AC-10: Release-walk implementation remains unchanged
  Required origin/main diff is empty; PR #764 is still open and the old director seed is backlog, so retirement's after-merge condition is not yet due.
- SKIPPED: AC-10: Post-merge seed retirement and its after-merge falsifier
  Explicit FO obligation after merge; no task-state mutation or future pass claimed.
- DONE: Whole CI command set, repair regression, guards and document dispositions
  26 commands run; reconciled 1009 unit tests = 1002 pass/7 existing skips, plus real dispatch/recovery. Seven initial fixture-isolation command failures were corrected without product changes; suite-reconciled.json. POC retained-model mutation fails. Number guard PASS; comment ratio 3.2% <= 5%; all seven document dispositions verified.
- DONE: Judge implementation limits and prerequisite versions
  Native effort is recorded behavior, not quality; model overrides/manual Codex/stage-effort limits stand. Installed 0.34.0 dispatch checker rejects the new completion records; candidate's inherited #763 checker accepts all five. No CI trigger changed; costs unmeasured.
- SKIPPED: Clean integrated-delivery verdict, local review rerun and publication
  Saved exact-head RoboRev 1400 High remains assigned to #765 by dispatch; FO retains sibling integration/re-review and delivery. No product push, PR mutation, repair or gate transition performed.

### Summary

The exact candidate satisfies AC-1 through AC-9 and AC-10's pre-merge boundary with independent native, history, mutation and dispatch evidence; the six-step acceptance script passes. This scoped PASSED recommendation does not certify the integrated stack, and preserves FO's #765 integration/review and post-merge seed-retirement obligations; candidate code is unchanged and the detached validation checkout is removed before handback.


## Stage Report: validation

- DONE: Independent verdict on PR #764 head 8eed70b2 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at 8eed70b260346811a1f2aa035ca1354a2d735576 for pre-merge scope; bounded recheck under the next checklist item, with native/unchanged judgments explicitly carried. No new findings in the four disposition classes; special-roles-follow-the-model-table/validation-2/details.md.
- DONE: Stacked on PR #763. This head only merges PR #763's repair into the head you passed, 562b1a871: confirm that and carry forward your judgements if their inputs are unchanged
  Parents 562b1a87198d97bb2ae1d87b72884e390b20e146 and fef0ae5fa79a77315ce6fce069c0a3ddf06e2daf; full delta exactly matches the sibling's two-file repair; 159 unchanged tracked inputs verified in carry-forward-inputs.json.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-2/acceptance.sh: six steps, fresh /bin/bash --noprofile --norc, exit 0; acceptance-output.log. Required ADR command at pinned origin/main 146727ded0d4ce8014ea0b41a45dc3409d6b269b with --require 0049: 48 files/0 legacy, exit 0; loaded Codex package command also passes.
- DONE: AC-1 and AC-2 — model recognition and both chief-engineer floors
  Fresh 27 role tests pass; no-Astra, leading-word and no-floor mutations fail 2, 4 and 4 cases respectively; mutations.log.
- DONE: AC-3 — current pinned history and real waived-case falsifier
  184 tasks at state 0c56419a56c6c5ff078f17b4e112222ca8c03910: 0 changed exit results; real peer-policy task without waiver base 1/candidate 0; Sol returns 1. Prior message-change adjudication carried; replay.log and replay-results.json.
- DONE: AC-4 — both-family output and consuming checks
  Fresh role suite plus 248 PR-watch/delivery-gate tests pass; reverting both-family wording fails 6 cases; pr-watch-delivery-tests.log and mutations.log.
- DONE: AC-5 — carry native model/effort evidence with unchanged inputs
  Four agent files/probe inputs unchanged; nine saved candidate/base/mutant transcript hashes reverified. Prior Opus/xhigh, Sonnet/high, four base warnings and reasoning-field medium falsifier stand; carried-native-hashes.json. No fresh native agents launched.
- DONE: AC-6 and AC-7 — table agreement, permitted overrides and fixed workflow budget
  Fresh lint, 47 lint tests, seven-row/family fixture checks pass at 5781 words; removed table check fails, dropped director yields a gap, all-workers gives count 0. Explicit max/ultra resolver proof carried unchanged.
- DONE: AC-8 — carry stage-model dispatch and removal controls
  Template, fixture and integration inputs unchanged; validation-1's six stamped builds and two Sonnet/from-defaults falsifiers stand. Prior observed dispatches are not represented as fresh runs.
- DONE: AC-9 — required rulings and missing-record check
  ADR 0026/0049 unchanged and consistent with accepted rulings; changed/all ADR lint passes. Empty-folder --require 0049 yields only required-record-missing, exit 1; adr-missing-only.log.
- DONE: AC-10 — release-walk boundary before merge
  Required origin/main diff empty; hosted PR remains OPEN/Draft and director seed remains backlog, so retirement is not yet due.
- SKIPPED: AC-10 — post-merge retirement and after-merge falsifier
  Explicit FO action after merge; no future pass or task-state mutation claimed.
- DONE: Inherited repair, regression and negative controls
  Dispatch suite 100 tests: 99 pass/1 optional builder skip; laws suite 63: 62 pass/1 optional corpus skip. Five completion mutations detected; restoring old extension parser produces exactly 3 failures. repair-falsifier.log and suite logs.
- DONE: Guards, document dispositions, dispatch records and hosted checks
  Number guard PASS at stack base fef0ae5fa; comments 3.2% <=5%; seven document dispositions unchanged. Candidate accepts all six records and current --names --strict; installed 0.34.0 rejects four newer completion records. Exact head has five SUCCESS hosted checks.
- DONE: Implementation limits and retained integration ownership
  Recorded effort is not quality; manual Codex/stage-effort limits stand; costs unmeasured and CI triggers unchanged. The #765 default-roster discrepancy and integrated re-review remain with FO; no clean integrated-delivery verdict. Prior full CI proof carried where inputs are unchanged.
- SKIPPED: Fresh native probes, full CI replay, local review and publication
  Narrow merge recheck carries unchanged native/integration/full-suite evidence; changed and consuming suites rerun. No repair, product push, PR mutation or gate transition.

### Summary

This second validation report recommends PASSED at 8eed70b260346811a1f2aa035ca1354a2d735576, replacing the earlier head-specific recommendation while retaining its unchanged judgments and limits. The merge contains only the verified sibling repair, the final six-step acceptance script passes, and candidate product bytes remain unchanged; FO retains #765 integration/review, delivery and post-merge retirement.
