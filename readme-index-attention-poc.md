---
title: POC — FO follows the workflow rules at least as well when it starts from an index and reads each rule at the moment it applies
variant: kc-dev-flow-2
profile: poc
merge: pr
status: validation
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
        - id: gate:readme-index-attention-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:readme-index-attention-poc-validation-1
              briefing:
                id: briefing:readme-index-attention-poc:validation:attempt-1:revision-1
                digest: sha256:27189f231ede3d85122e4803cf88e5050ffc1178fd2fc108f5b1e922224d18e9
                room-ref: ./readme-index-attention-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:readme-index-attention-poc:validation:1
                briefing: briefing:readme-index-attention-poc:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T14:34:58.681358Z"
                decision: approve
                reason: Captain approved in chat (「好，就這樣」) closing the POC as failing his bar with no README restructure, after asking whether the model already holds about 5000 words without losing focus; the follow-up is reframed to test, in long sessions, whether rules that reappear at the moment of use reduce violations, and only after a long-session test exists
              application:
                target-stage: done
                state: pending
started: 2026-10-17T13:58:28Z
worktree: .worktrees/spacedock-ensign-readme-index-attention-poc
mod-block: merge:pr-merge
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

## Result

Thirty runs, 2026-10-17, `claude-sonnet-5-5` on every run, no CLI error, no rerun, no tool other than Read. Per-run rows (arm, probe, followed, the deciding line, startup and moment words, files read, tokens, seconds, imputed cost) are in `poc/results.md` and `poc/results.json`; raw stream-json is in `poc/runs/`.

**Against the Captain's bar as registered: FAIL.** Total passes (B 13 of 15, A 13 of 15) and startup words passes (628 of 5499 = 0.114, bar 0.25), but the per-probe condition fails on P1: B followed 1 of 3 where A followed 3 of 3, worse by two runs, and the bar allows one.

| Probe | A followed | B followed | B moment words (min-max) |
| --- | --- | --- | --- |
| P1 bare script name | 3 | 1 | 1388-1713 |
| P2 FO declines | 1 | 3 | 1577-1818 |
| P3 reserve ADR number | 3 | 3 | 1977-2133 |
| P4 amendment entry | 3 | 3 | 1042 |
| P5 follow-up to live worker | 3 | 3 | 1318 |
| Total | 13 | 13 | mean 1546 (A: 5499 at every moment) |

Decisive lines. B-P1-1 and B-P1-2 write every script name as `/opt/kdf2/kc-dev-flow-2/scripts/NAME.py`, but their record holds one script name: both dropped checklist item 3 (`number_guards.py check`), and B-P1-2 says why ("the Number guards rule does not apply and there is no number_guards check item"), so the P1 decider's two-names clause fails them. A-P2-2 and A-P2-3 name `aa6fcc91` once in a header over both findings, so the P2 decider, which wants the revision inside each finding's own text, fails them; their per-finding lines cite the evidence file and line.

**Sensitivity, post-hoc, not the result.** `poc/sensitivity.py`, written after the runs, scores P1 on bare script names only and P2 with the revision allowed in a shared header: A 15 of 15, B 15 of 15, every probe 3 and 3. It would pass the bar. The registered deciders stand as the result; the pass/fail difference rests on two decider choices (a two-names clause in P1, a per-finding revision in P2), not on a rule either arm broke.

**Cost.** Mean tokens per run (input, cache and output): A 26.2k, B 27.6k; total seconds A 98, B 113; imputed `total_cost_usd` A 0.38, B 0.45 for 15 runs each. The imputed figure is the CLI's list price, not a charge. B was not cheaper per run: its prompt is shorter but the runs paid for Read turns, and a system prompt of 5.5k words is cached cheaply.

**Layout of arm B.** `poc/arm-b/README.md` (frontmatter and intro verbatim, then a 21-row table of file and trigger) plus `poc/arm-b/rules/`, 21 files, a lossless verbatim split of the README by heading: `file-naming`, `schema`, `stages` (534 words, the part before the stage subsections), `stage-backlog/-ideation/-implementation/-validation/-done`, `dispatch-facts`, `review-finding-disposition`, `fo-steps-review-findings` (690, the largest), `decision-records`, `fo-steps-decision-records`, `captain-amendments`, `affected-documents`, `number-guards`, `fo-steps-number-guards`, `delivery-authority`, `extensions`, `workflow-state`, `task-template`. `build_arm_b.py` fails when the split is not lossless.

**What the POC does not show.**
- Three of five probes were followed in all six runs, so the matrix could not separate the arms there. Short scenario contexts leave the whole-README arm at ceiling; the observer's violations come from long sessions with the README far back in context, which this did not reproduce.
- B opened 2 to 5 files per probe (mean moment load 1546 words, 28 percent of A) and did open the right file each time; whether an FO with many concurrent duties does so is untested.
- The index was written knowing the probe classes, so B is an upper bound for an index. No must-not-apply probe ran, so over-application after opening a file is untested, apart from B-P1-2 dropping a checklist item after reading number-guards.md.
- One wording per situation, one model, answers instead of a live FO with tools and state, so nothing here shows a drop in the observer's violation counts.
- A-P1-1 and A-P1-2 each tried to Read `EXTENSION.md` five times and found nothing; A without an index also wanders.

**Package checks at exit** (base 6ea3a472 = code HEAD; the code branch has no commit beyond base, correct for this task). `comment_ratio.py`: exit 0, "code lines 0, comment lines 0, 0.0%", not enforced under 20 code lines. `doc_impact.py`: exit 0, 0 documents listed. `number_guards.py check`: exit 0, PASS, migration guard skipped (no `migrations-path:`). `design_surfaces.py check`: exit 1 on this POC task, which has no `## FO alignment` or `## Acceptance criteria` section because the POC route skips ideation; not a finding against this stage. No package file or adopter README changed; no PR opened (no push grant for code; none was needed); no PR or issue comment.

**Cleanup.** The throwaway smoke dirs under /tmp are removed; `poc/arm-a-cwd` is created empty by the runner and is untracked. Nothing else to remove.

## Stage Report: implementation

- DONE: Upstream check first, written into the task file before any run: what Spacedock's first-officer contract loads at boot, what `show-stage-def` and `context-sections:` deliver per stage, what kc-dev-flow-2's `_mods` startup and idle hooks load, and what the 0.14.0 split already moved; say what each gives and whether the index arm needs anything new
  `## Upstream check`: FO boot opens no README body; show-stage-def and context-sections serve workers only; mods are 48 words; #587 moved FO-only text but the FO still loads the whole file; index arm is new for FO-only text only. Committed in state b16f9201, before run 1.
- DONE: Pre-registration committed to the state branch before any run: the five probes, the two arms, the scoring rule per probe and the Captain's bar verbatim
  `## Pre-registration` plus `poc/` (probes.py, arm-a, arm-b, run_probes.py) in state commit b16f9201; probes drawn from 16 observer reports (state 7a696b0a); bar quoted from the backlog briefing.
- DONE: Thirty runs on Sonnet (five probes, three per arm), each recorded with arm, probe, followed or not with the deciding line, words at startup and at the probe's moment, tokens, seconds and cost
  `poc/results.md` and `poc/results.json` hold all 30 rows; raw stream-json under `poc/runs/`; cost is the CLI's imputed figure.
- DONE: Result against the bar, pass or fail, without moving the bar; what the index arm's file layout was; what the POC does not show
  `## Result`: FAIL as registered (P1 B 1 of 3 vs A 3 of 3; totals 13 and 13; startup 0.114 of A); layout and limits written. Post-hoc sensitivity (15 and 15) is labelled as not the result.

### Summary

The index arm loads 11 percent of the README at startup and 28 percent on average at the probe's moment, and follows the probed rules as often in total (13 of 15 each). Under the registered bar it fails on one probe: in two P1 runs B dropped a checklist item after reading number-guards.md, which the P1 decider counts as not followed, while A's two P2 misses came from naming the revision once in a header. Three of five probes sat at ceiling in both arms, so this POC cannot say the index is better, only that it did not clearly do worse once two decider choices are relaxed.

## Stage Report: validation

- DONE: Confirm from state-branch history that the pre-registration (probes, arms, scoring rule, the Captain's bar verbatim) was committed before the first scored run, and that no scored run was rerun or dropped
  State commit b16f9201 (22:10:26) holds `## Pre-registration` with the bar verbatim plus probes.py, run_probes.py, arm-a, arm-b; first raw run file mtime is 22:10:48 and all 30 landed in d72f68cc (22:16:37). `git diff b16f9201 HEAD` shows probes.py, run_probes.py, both arms and the Pre-registration text unchanged. 30 jsonl files, one per cell, every run `is_error` false, model `claude-sonnet-5-5`, no rerun or drop. Caveats: the order rests on file mtimes and commit times (no signed log); b16f9201 also carried a smoke `results.json` row for B-P3-1 (scratch dir, disclosed in the pre-registration, followed true), removed in 69d78173; the scored B-P3-1 is a fresh run of that cell, also followed.
- DONE: Re-score all 30 saved runs yourself from readme-index-attention-poc/poc/runs/ against the registered scoring rule, without using the implementer's scorer output; report per probe and arm, and any run where your reading differs from the registered rule's
  I extracted each answer from the raw stream-json and scored with my own script written from the registered table (not probes.py), after reading all 30 answers. A/B followed: P1 3/1, P2 1/3, P3 3/3, P4 3/3, P5 3/3, total 13/13; identical to results.json run by run (misses B-P1-1, B-P1-2, A-P2-2, A-P2-3). No run where my reading differs from the registered rule. Reading beyond the rule, not scored: B-P4-2 changed the Captain's full-width comma to ASCII in a quote the README says is verbatim; every P3 answer passes, though A-P3-2, B-P3-2 and B-P3-3 place `spacedock state commit` after or around `dispatch build`, which P3 does not test.
- DONE: Judge the P1 result: whether the two B runs that dropped checklist item 3 after reading number-guards.md failed the rule the probe tests or only the scorer's two-script-name proxy; the verdict stays against the registered bar, and any alternative reading is reported as such
  They passed the bare-script-name rule (README Stages: a checklist or scope-notes line naming a package script writes `<package>/scripts/NAME.py`, never the bare name): the one script each record names (doc_impact.py) is absolute and they run dispatch_records.py. They failed only the registered "at least two names" clause, which the README does not state. What differs is not that rule: after opening number-guards.md both edited a checklist the situation gave verbatim; B-P1-2 explains it from the "Applies when Surfaces includes db or the task lands an ADR" sentence (Surfaces none, no ADR in the situation), B-P1-1 drops it with no reason and also rewrites item 2. That is a reading the rule text supports but an instruction override the probe did not set out to measure, and A never did it. Alternative reading (not the result): P1 on the bare-name rule alone is A 3, B 3.
- DONE: Verdict against the Captain's bar (PASSED or REJECTED for the POC as registered), the startup-word ratio recomputed from arm-a and arm-b, and what the POC does not show
  REJECTED as registered. Total 13 vs 13 passes; startup words 628 / 5499 = 0.114 (wc and `len(split())` agree; arm-a is byte-identical to `docs/dev2/README.md` at 6ea3a472; every line of arm-a appears in arm-b's index or rules) passes the 0.25 bar; per-probe condition fails on P1 (B 1 vs A 3, worse by two, the bar allows one). Alternative reading: P2 with the revision named once in a shared header gives A 3, B 3, so P1 and P2 together are two decider choices; the sensitivity is post-hoc and does not change the verdict. Not shown: whether the index helps at all (three probes at ceiling in both arms); long-session attention, which the observer's violations come from; mean moment load is 1546 words, 28 percent of A (not under a quarter), and index runs always opened files because the prompt names `rules/`; no must-not-apply probe; one wording, one model, answers not a live FO; B's prompt differs from A's by more than the README (an intro line and a cwd with files), so B reading files is partly prompted.

### Summary

Re-scoring all 30 raw runs independently reproduces the implementer's numbers: 13 of 15 each, with B 1 of 3 on P1 and A 1 of 3 on P2. The registered bar is not met on P1, so the POC is REJECTED as registered; the P1 misses are a proxy clause plus an unprobed checklist-edit behavior, not a broken bare-name rule, and the pre-registration order and 30-run completeness check out. The Captain may reasonably treat the result as "index not shown worse, not shown better"; that is a new decision, not this verdict.
