---
title: POC — FO follows the workflow rules at least as well when it starts from an index and reads each rule at the moment it applies
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:readme-index-attention-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:readme-index-attention-poc-backlog-1
              briefing:
                id: briefing:readme-index-attention-poc:backlog:attempt-1:revision-1
                digest: sha256:6ee60a805ace07c0d5f6fadb33187cd393901d1c1da8938e477c801b6c744af4
                room-ref: ./readme-index-attention-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:readme-index-attention-poc:backlog:1
                briefing: briefing:readme-index-attention-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T13:58:03.918571Z"
                decision: approve
                reason: 'Captain approved in chat (「按你建議的 poc 標準可以」) the POC with the recommended bar stated in the gate question: five probes, three runs per arm on Sonnet; pass when the index arm follows the probed rules at least as often in total, is worse on no probe by more than one run, and loads at most a quarter of the whole-README startup words'
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-17T13:58:28Z
worktree: .worktrees/spacedock-ensign-readme-index-attention-poc
---

Filed on the Captain's words (chat, 2026-10-17), after FO said #658 (workflow-budget-ratchet) only cuts words and does not change how the README is read: 「長度的問題是，不應該讓 llm一次讀麽多字，應該只讀必要的，就算是第一次讀入的東西應該是一個索引，讓新的 llm 一直知道去哪裡找什麼，不是一次餵給他一大堆現在還用不到的東西……如果能先解決前面的問題，那文件長度可能就不是核心問題」, then 「合併且開任務，先走poc證明真的比較好再繼續」.

## Scope

- Question the POC answers: does an FO that loads a short index at startup, and each rule passage only at the moment it applies, follow the workflow rules at least as well as an FO that loads the whole README (5447 words on origin/main 6ea3a472), while loading fewer words at each moment?
- Upstream first, before building: whether Spacedock's first-officer contract requires the whole workflow README at boot; what `spacedock dispatch show-stage-def` and the stage `context-sections:` frontmatter already deliver per stage; what kc-dev-flow-2's `_mods` startup and idle hooks load; and the 0.14.0 split of workflow.md by reader (worker vs FO). Say what each already gives.
- Arms: (A) today's whole README; (B) an index README (where each rule lives and when to open it) plus per-moment files, built in a scratch copy only. No change to `kc-dev-flow-2/references/sd/workflow.md` or any adopter README in this POC.
- Probes: the rule classes the observer most often reports as not followed (32 violation lines in 15 observer reports since 2026-10-13, per workflow-budget-ratchet's ideation), for example an ADR number reserved after the first implementation dispatch, a `Reviewer:` line under the wrong heading, a grant quoted from the wrong gate question, a bare package script name in a dispatch record, a dispatch missing the completion line to `main`. Each probe is a fixed FO situation with a checkable right action; the existing replay mechanism in `kc-dev-flow-2/scripts/replay_dispatch.py` and maintain-flow's behaviour replay are checked first.
- Measures: per probe, the rule followed or not per arm, over a pre-registered number of runs; words loaded at each moment per arm; tokens and cost per run.
- Bar: written and committed before any run, and shown at the backlog gate for the Captain to set; the POC reports pass or fail against it without moving it.
- Non-goals: no package or adopter change; no production README restructure; the follow-up task that restructures the README is filed only if the POC passes.

## Upstream check

Written 2026-10-17 before any run. Sources read: Spacedock 0.27.0 `first-officer` skill and `references/first-officer-shared-core.md`, binary 0.27.2 `dispatch --help` / `dispatch show-stage-def --help`, `status --boot --identify --json`; kc-dev-flow-2 0.24.0 `skills/dev`, `skills/maintain-flow`, `references/sd/mods/kc-dev-flow-2.md`, `CHANGELOG.md` 0.14.0 and commit 4064fb5 (#587); docs/dev2 README at origin/main 6ea3a472.

- **Spacedock FO boot.** Startup is `status --boot --identify --json`, then `state ready`, `state sweep`, the startup hooks, `status --next --json`. No step opens the README body; the boot record carries workflow discovery, stage taxonomy and a mods map. The whole-README read by FO is a kc-dev-flow-2 convention (the README calls itself "the adopted workflow's authority"), not a Spacedock requirement. Gives: a boot with no README read. Index arm needs nothing new here.
- **`show-stage-def` and `context-sections:`.** `show-stage-def` prints a stage's README subsection followed by its declared context sections; the dispatch inlines them into the worker's prompt. Gives: per-stage delivery to workers only. FO is never handed a section by moment, so the index arm is new for FO-only text.
- **`_mods` startup and idle hooks.** `kc-dev-flow-2.md` is 48 words: startup runs the idle hook, idle runs `pr_watch.py tasks`; Spacedock opens only registered mod bodies. Gives: a tiny hook load, no rules. Nothing new needed.
- **0.14.0 split by reader (#587).** Moved FO-only text into `## FO steps:` sections and removed Delivery authority and those sections from worker context: implementation dispatch 2516 to 1118 words, validation 2628 to 1230. FO still loads the whole file. Gives: the worker side is done; the FO side is what this POC tests.
- **Existing replay tooling.** `scripts/replay_dispatch.py` rebuilds a closed task's worker dispatch at a package ref, so it cannot test FO-only rules. maintain-flow says "a rule only FO acts on cannot be replayed: a fresh FO answers scenario questions from the README alone". No FO scenario runner exists, so `poc/run_probes.py` is the only new tool: it starts fresh `claude -p` sessions and scores their answers.

## Pre-registration

Committed before any scored run. Files under `readme-index-attention-poc/poc/` in this state checkout. Two `claude -p` calls on a throwaway prompt (isolation check) and one on B-P3 with a scratch run dir (`POC_RUNS_DIR=/tmp/kdf2-probe-smoke`, tooling smoke test) preceded this commit; none counts.

**Captain's bar, verbatim from the backlog gate question (approved 2026-10-17, 「按你建議的 poc 標準可以」):** "Recommended bar: five probes, three runs per arm on Sonnet (30 runs); pass when the index arm follows the probed rules at least as often as the whole-README arm in total, is worse on no probe by more than one run, and loads at most a quarter of the whole-README words at startup. Approving accepts that bar; say a different one if you want it."

**Arms.** A: the whole docs/dev2 README at origin/main 6ea3a472 (`poc/arm-a/README.md`, 5499 words). B: an index README (`poc/arm-b/README.md`, frontmatter and intro verbatim plus a trigger table, 628 words) and 21 rule files (`poc/arm-b/rules/`) made by `poc/build_arm_b.py`, a lossless verbatim split of the same README by heading (Stages split per stage subsection). Only the index is handwritten. Bias disclosed: the index triggers were written knowing the probe classes, as a production index built from observer reports would be, so B is an upper bound for an index.

**Words.** `len(text.split())` of the whole file as loaded, frontmatter included in both arms. Startup words = the README text in the system prompt; moment words = startup plus the distinct rule files the run actually Read (from the stream-json tool calls). The startup bar is 628 / 5499 = 0.114 against 0.25, fixed by the files, not by runs.

**Runner.** `poc/run_probes.py`, fresh `claude -p` 2.1.301, `--model sonnet` (model id recorded from each run's `modelUsage`), effort default, `--tools Read`, `--setting-sources ""`, `--strict-mcp-config`, `--disable-slash-commands`, `--no-session-persistence`, `--system-prompt-file`, `--output-format stream-json --verbose`; the situation goes on stdin. `--bare` is not used: it reads only `ANTHROPIC_API_KEY`, and this machine has none (OAuth). The isolation check found no user CLAUDE.md in context. Only the system prompt differs between arms (shared FO role sentence, plus one line saying the README is the whole definition (A) or an index to `rules/` (B)); cwd is an empty directory (A) or `poc/arm-b` (B). Order is a seeded shuffle (seed 20261017) of the 30 cells. Raw stream-json per run goes to `poc/runs/`; cost is the CLI's `total_cost_usd`, an imputed list-price figure, not a charge.

**Probes.** Chosen from the 16 observer reports in the dev2 state checkout (`git grep -i '^violation' -- '*observer.md'`, state commit 7a696b0a, 33 violation lines). Reports containing each rule class: bare package script name 5; FO declines naming finding, reason, revision, evidence 5; number-guards reserve/record 4; Captain amendments form 3; then three classes at 2 (`Result:` line before ideation dispatch, extension instruction in scope notes, follow-up dispatch record parts). The fifth probe takes the follow-up-dispatch class because the task Scope names its completion line to `main`; the other two tied classes are not probed. Each probe is a fixed situation in `poc/probes.py` with a script decider; a run is "followed" only when the decider is true, and the deciding line is recorded.

| Probe | Rule (README section) | Right action the decider checks |
| --- | --- | --- |
| P1 | bare script name (Stages) | every `*.py` in the saved dispatch record is written `/opt/kdf2/kc-dev-flow-2/scripts/NAME.py` and at least two appear |
| P2 | FO declines (FO steps: review findings, step 2) | the F1 text and the F2 text each name the candidate revision `aa6fcc91` and the evidence file (`cap.py`, `backoff.py`) |
| P3 | reserve ADR number (FO steps: number guards) | a `number_guards.py reserve --kind adr` command appears before `dispatch build` |
| P4 | amendment entry (Captain amendments) | the entry's `Supersedes:` line names `AC-2`, not `none` |
| P5 | follow-up to a live worker (Stages) | the message tells the worker to send its completion message to `main` and carries `Package root: /opt/kdf2/kc-dev-flow-2` |

Deciders were exercised on hand-written right and wrong answers before commit; each flips on the named change.

**Scoring and report.** Per probe, followed count per arm (of 3); total per arm (of 15). Pass = B total >= A total, and for every probe B's count >= A's count - 1, and B startup words <= 0.25 x A's. The bar is not moved after a run; a failed or unparseable run (CLI error, empty result) is rerun once from the same cell and the first failure is reported. Limits fixed in advance: five situations, one wording each, short contexts (no long session behind them), no must-not-apply probe, one model, a scenario answer instead of a live FO with tools.
