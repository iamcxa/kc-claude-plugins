---
title: A pre-build story interrogation, replayed on batch 3, asks ahead of time the decisions and P1 gaps that batch 3 actually hit, and shows which model and role mix asks them
variant: kc-dev-flow-2
profile: poc
merge: local
status: validation
gates:
    version: 1
    records:
        - id: gate:interrogation-replay-on-batch-3-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:interrogation-replay-on-batch-3-poc-backlog-1
              briefing:
                id: briefing:interrogation-replay-on-batch-3-poc:backlog:attempt-1:revision-1
                digest: sha256:a5555d361feb6b200d07e23e6376f9a6c371f11ad3e624453d9cd0f43abaa7f6
                room-ref: ./interrogation-replay-on-batch-3-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:interrogation-replay-on-batch-3-poc:backlog:1
                briefing: briefing:interrogation-replay-on-batch-3-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-20T08:18:08.275168Z"
                decision: approve
                reason: 'Captain approved in chat (「准」) after the gate briefing: profile poc, the one-task budget and the falsifier as written'
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-20T08:18:17Z
worktree: .worktrees/spacedock-ensign-interrogation-replay-on-batch-3-poc
---

## Scope

- Source: the Captain, 2026-10-20: 「對，雙模型，且等級與角色應該要混合……claude 是否該用特殊角色進來問答？codex 如何確保用的是足夠聰明的模型？codex 是否也可以，或是也該套入特殊角色？我感覺這個階段可以省去批次問答的時間與設計階段的一些問題？有過去的經驗可以挖出來比較的嗎？」; 「特殊角色是 agent profile + skill 所以理論上 codex 可以接 skill」; 「可以開這個 poc」.
- Riskiest assumption: a story interrogation run before a batch starts asks a material share of the questions the batch later stopped on (Captain decisions surfaced at ideation, and P1 or roborev High findings that were design gaps), so moving it earlier saves Captain sittings and repair cycles. Evidence today: two runs on one release (kc-journey-map `references/interrogation.md`: Codex asked 12 of 17 later-hit questions, Claude sonnet 4 of 17; both missed three concurrency issues).
- Decision this POC informs: the interrogation design inside new-work-starts-from-a-story-map (dev2 workflow), and which model and role each interrogator uses.
- Method: kc-journey-map's interrogation prompt and isolation rules, run on the code snapshot each batch-3 task started from (`git archive <base>`; no history), against that task's seed Scope as the "story". Arms, same prompt: (1) Claude sonnet, default effort (today's interrogation); (2) Claude Opus with the kc-dev-flow-2:engineering-reviewer skill's lens; (3) Codex at an explicitly pinned model and high effort; (4) the same Codex with the kc-dev-flow-2:engineering-reviewer skill. Answer key, read from the archived tasks only after the arms ran: every Captain decision (D-items, amendments) and every P1 or roborev High that was a design gap.
- Falsifier: across the arms, fewer than 25% of the answer key items are asked in substance by any arm; or the best arm's hits come with more than three ungrounded questions per hit.
- Budget: start with one task (captain-question-load: two D-items, one amendment, two P1s and a roborev High); report cost and hits; extend to the other batch-3 tasks only on the Captain's word. Stop point: the one-task report, or the falsifier firing.
- Non-goals: changing kc-journey-map or kc-dev-flow-2; picking a production design.

## FO alignment

Alignment: not needed before implementation; the Captain asked for this POC and the one-task budget is stated.

## Stage Report: implementation

- DONE: Run the four interrogator arms in the task Scope on captain-question-load only: snapshot the kc-claude-plugins code at that task's base (find it in the archived task under the dev2 state checkout, _archive/captain-question-load.md and its dispatch records; base 18dbf490) with `git archive <base> | tar -x`, no history; use kc-journey-map's interrogation prompt (kc-journey-map/skills/kc-journey-map/references/interrogation.md at origin/main) with the task's seed Scope (its first committed version) as the story; arm 2 and arm 4 add the kc-dev-flow-2:engineering-reviewer skill's lens to the same prompt; pin Codex's model and effort explicitly with flags you first confirm in `codex exec --help`; audit each event stream for reads outside the snapshot
  All four arms ran to exit 0 (71, 208, 166, 213 s). Snapshot is 18dbf490, 1377 files; seed is state commit 41654262. Claude: `--model sonnet` / `--model opus --effort high`; Codex: `-m gpt-6.1-sol -c model_reasoning_effort="high"` (`-m` confirmed in `--help`; effort has no flag there, so it goes through the documented `-c` override and its application is unverified). Audit: 0 reads outside the snapshot in 18, 23, 27 and 23 calls; the reference Claude command exposed MCP tools, so I added `--strict-mcp-config` (tool list became Glob, Grep, Read).
- DONE: Only after all arms ran, build the answer key from the archived task (its Captain decisions D1, D2, amendments 1 and 2, the Codex P1s and the roborev High that were design gaps) and score each arm: key items asked in substance (quote the question and the key item), ungrounded questions, cost (tokens or reported cost per run, stated as measured or not), wall time; check the falsifier
  Key read after the answers were saved: 7 items K1 to K7. Strict hits 1, 1, 2, 4 of 7 (arm 1 to 4); ungrounded questions 0 of 90 by a mechanical symbol/quote check plus 4 spot checks. Cost: Claude imputed list price 0.291 and 1.920 USD, Codex tokens only (USD not measured). Falsifier not fired (union 57%, best arm 57%; 0 ungrounded per hit). One task, n=1 per arm, one rater.
- DONE: A report saved as interrogation-replay-on-batch-3-poc/report.md in the dev2-poc state checkout, with the four arms' raw question lists, the scoring table and a recommendation for which arm or mix to use, and whether to extend to the other batch-3 tasks
  `interrogation-replay-on-batch-3-poc/report.md` (raw lists, scoring table, quotes, recommendation: arm 4 as primary, extension to the other batch-3 tasks only on the Captain's word with arm 3 as noise control); full answers, both prompts and `run.sh` in `interrogation-replay-on-batch-3-poc/raw/`.

### Summary

The falsifier did not fire: Codex with the engineering-reviewer lens asked 4 of 7 key items, the others 1, 1 and 2; K5 (a hold opt-out) was asked by none. Limits: one task, one run per arm, my own key and scoring, and an 11-item partial column that I did not use for the falsifier. No repository file, branch, commit or PR was created; the temp directory `/tmp/replay-w0OHE1` is left for validation and the removal command is in the report. `comment_ratio.py HEAD HEAD`: exit 0, 0 code lines, 0 comment lines, 0.0% (no diff, base ad44f0cb = HEAD). `number_guards.py check`: exit 0, PASS no findings, migration guard skipped (no migrations-path).

## Stage Report: validation

- DONE: Independent verdict on the POC report against the riskiest assumption and falsifier: re-score the four arms yourself from raw/ against the answer key before reading the implementer's scoring table, then compare item by item; say whether the falsifier holds under your scores
  Key read from `_archive/captain-question-load.md` (D1, D2, amendments 1 and 2, P1s at Cycle 1 and 2, roborev:875/878/881 High) and four raw answers scored before opening report.md. Mine, strict (of 7): arm 1 = 2 (K1 Q1, K7 Q18), arm 2 = 1 (K1 Q4), arm 3 = 2 (K1 Q1, K6 Q15), arm 4 = 3 (K1 Q1, K6 Q13, K7 Q15); implementer: 1, 1, 2, 4. Disagreements: (a) arm 4 K4 Q4 ("stop the action beforehand, or is detecting it afterward sufficient?") is partial, not a hit: it asks prevention versus audit in general, not whether the question-reading check lands in this task, and K4 is the waiver of the very gap K7 names, so counting both double-counts one gap; (b) arm 1 Q18 ("What stops FO from writing 'approving accepts the recommendation' into every gate question ... who audits it?", grounds: delivery_gate checks head and CI but not the question wording) is a K7 hit the report scored as a miss; everything else agrees, including K2, K3 partial, K5 miss for all arms. Falsifier holds under my scores: union 3/7 = 43% (K1, K6, K7), best arm 43%, 0 ungrounded per hit; it still holds at 2/7 = 29% if K7 is also demoted, and fires only if K1 is dropped as story-seeded and K7 is demoted (1/6 = 17%).
- DONE: Judge the stated limits: one task, one run per arm, one rater, the Codex model from models_cache.json and effort not echoed, the isolation flags added to the reference command; say which limit could change the recommendation and what one further run would settle it
  Resolved by me: the Codex effort and model did reach the runs; the two Codex session rollouts under `~/.codex/memories/sessions/2026/10/20/` that contain the prompt carry `"effort":"high"` and `"model":"gpt-6.1-sol"`. Isolation re-audited from the saved streams: arms 1 and 2 had 18 and 23 tool calls, all paths inside the snapshot; arms 3 and 4 had 27 and 23 commands, none with `..`, `~`, `git` or `/Users`; all four exit 0. Four grounds spot-checked true in the snapshot (168 resolutions in ADR 0011, `WORKFLOW_BUDGET_START = 5511`, the "force push between two reads" declined line, "do not prevent a wrong record" in VALIDATION.md). The seed Scope matches state commit 41654262. Remaining limits, ordered by effect on "arm 4 as the pre-build interrogator": run-to-run variance (n=1; the report itself says one arm 3 re-run could move 2 to 4) together with one rater changes the arm 4 lead from 4 versus 2 (report) to 3 versus 2 (mine), which is inside that noise; so the data show Codex arms at least as good as the Claude arms, not that the lens or arm 4 is better than arm 3. Others: K1 is spelled in the seed ("a delivery gate that carries the merge grant by default"), K3 and K4 cannot be asked before the build (a refused edit, a waiver), K5 came from a Captain phrase after the design; Opus ran with an advisor sidecar; Codex also loaded the user's MCP config (an auth error in `a3.err`, no calls). One further run that settles it: re-run arms 3 and 4 once each on this same snapshot and prompts (about 3.5 minutes each, tokens only), score the two new lists blind to arm label by a second reader against the same seven items; arm 4 stays the recommendation only if it again beats arm 3 on strict hits.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output) that shows the raw answers, the key and the hit counts from the committed files, run by you exactly as written in a fresh bash shell, with its observed output; your verdict, with findings classified by the workflow's Review-finding disposition
  Script below; run as a file under `env -i HOME=$HOME PATH=$PATH bash --noprofile --norc`, output matched every expected line. Verdict: PASSED (recommended). The falsifier did not fire; the report's recommendation of arm 4 is stronger than one run supports (F1). `adr_lint.py docs/adr --since ad44f0cb`: exit 0 (26 files). `comment_ratio.py HEAD HEAD`: exit 0, 0 code lines. `number_guards.py check`: exit 0, PASS. `dispatch_records.py <task folder>`: exit 1 (F2). `design_surfaces.py check <task>`: exit 1 (F3). Candidate: report.md and raw/ at state commit 69261bcf; no repository diff (worktree HEAD = base ad44f0cb, status clean). Cleanup: `/tmp/replay-w0OHE1` and `/tmp/replay-dir.txt` removed.

### Acceptance script (five steps, under five minutes, read-only)

Set once, then run each block in a fresh bash shell:

    S=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state/interrogation-replay-on-batch-3-poc
    K=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/captain-question-load.md
    echo "== 1. the committed raw files"; ls "$S/raw"
    echo "== 2. questions per arm"; for a in a1 a2 a3 a4; do printf '%s %s\n' $a "$(grep -cE '^[0-9]+\. ' "$S/raw/$a-answer.md")"; done
    echo "== 3. the questions counted as hits"; for p in a1:1 a1:18 a2:4 a3:1 a3:15 a4:1 a4:4 a4:13 a4:15; do f=${p%%:*}; n=${p##*:}; printf '%s Q%s: ' $f $n; grep -E "^$n\. " "$S/raw/$f-answer.md" | cut -c1-190; done
    echo "== 4. the answer key in the archived task"; grep -nE '^- \*\*D[12]:' "$K" | cut -c1-150; grep -nE '^### Amendment [12]' "$K"; grep -nE '^  - P1 \(|^- F1 roborev' "$K" | cut -c1-210
    echo "== 5. the implementer's hit counts"; grep -E '^\| (Strict hits|Questions asked|Ungrounded)' "$S/report.md"; grep -E '^Union across arms' "$S/report.md"

Observed: step 1 lists a1 to a4 answers, two prompts, run.sh; step 2 prints `a1 25`, `a2 23`, `a3 22`, `a4 20`; step 3 prints the nine question lines (a1 Q1 and Q18, a2 Q4, a3 Q1 and Q15, a4 Q1, Q4, Q13, Q15); step 4 prints D1 at line 261, D2 at 262, Amendments 1 and 2 at 283 and 288, the two P1 lines at 300 and 302, and the roborev F1 lines at 374 and 432; step 5 prints `Strict hits ... 1 (14%) | 1 (14%) | 2 (29%) | 4 (57%)`, questions 25, 23, 22, 20, ungrounded 0 0 0 0, and `Union across arms, strict: K1, K4, K6, K7 = 4 of 7 (57%)`. A pass means the files and counts are as reported; it does not show the scoring is right (compare step 3 with step 4 yourself: a4 Q4 and a1 Q18 are where I disagree), nor that any arm saves a Captain sitting.

### Findings (Review-finding disposition)

- F1 Deferred risk: the report scores arm 4 K4 as a hit (a4 Q4) and arm 1 K7 as a miss (a1 Q18); under my scoring the arm 4 lead is 3 versus 2 and the recommendation "arm 4 as primary" rests on one run per arm. Becomes Material if the Captain commits the interrogation design to arm 4 on the 4 versus 2 gap, or extends to other tasks without the arm 3 control the report already proposes.
- F2 Polish (FO record): `dispatch_records.py` exit 1, `implementation-1.md: roborev worker instruction is absent`; add a line `roborev not run: no repository diff` to that record. The assignment has no diff, so there is nothing for roborev to read.
- F3 Polish (task shape): `design_surfaces.py check` exit 1 for no `Surfaces:` and `Visible change:` line and no `## Acceptance criteria`; a POC skips ideation, so the script cannot pass on this task. FO decides whether to record the exemption or add the two lines.
- No `boundary-crossed:` found: no migration, persistent state, external seam or repository change; the only external write was removal of the temp directory.
- Unverified: whether a different reader would promote the report's 11 partials; whether the Claude arms' ledger-counting questions (procedural asks, plain approval versus missing Override) are value or noise, since no key item covers them.

### Summary

The falsifier holds under my independent scores (union 43%, best arm 43%, 0 ungrounded per hit), so the POC result stands. I disagree on two items, which cut arm 4's lead from 4 versus 2 to 3 versus 2, so I would phrase the recommendation as "Codex arms at least as good as Claude arms; lens and arm 4 unproven" until arms 3 and 4 are re-run once with a blind second reader. Codex effort and model are confirmed from its session rollouts, closing the report's largest unverified limit.
