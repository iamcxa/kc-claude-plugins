---
title: A named design-director role runs the ui design review in place of a general-purpose sonnet agent
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:design-director-runs-ui-design-review:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:design-director-runs-ui-design-review-backlog-1
              briefing:
                id: briefing:design-director-runs-ui-design-review:backlog:attempt-1:revision-1
                digest: sha256:a26c4da383fb5f17a359d53ce8aeccd8035d5bc3e1fcedfb55edc67fda39a563
                room-ref: ./design-director-runs-ui-design-review/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:design-director-runs-ui-design-review:backlog:1
                briefing: briefing:design-director-runs-ui-design-review:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-22T07:27:22.671295Z"
                decision: approve
                reason: 'Captain 「可以」 (chat, 2026-10-22), answering 「設計總監任務可以進入設計階段嗎？我建議可以。」 whose presentation listed what approval accepts: duty wording (owns the open design decisions; upheld declines listed for the Captain, who keeps the final say), two passes (pictures, then built-screen screenshots), host-component declines checked, and a replay of the 10 already-raised paseo findings before shipping; digest a26c4da3. Accepts the FO recommendation as the bound question states.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「我還是希望開設計總監，讓它來做目前指示的內容，等於派出的 general purpose sonnet 改成設計總監。此外，在可用前提，平行多派一個 gpt astra mid 來做設計輔助夥伴，合理嗎？」 (chat, 2026-10-22), then 「可以」 to FO's 「開一張「設計總監」任務，astra 輔助先用 POC 驗證，模型等量測結果再定，可以嗎？」 (chat, 2026-10-22).
- Shape asked for: `skills/ideation/design-review.md` dispatches a named `kc-dev-flow-2:design-director` agent, with an agent file that declares its model like chief-engineer and engineering-reviewer, carrying the existing brief unchanged; a parallel `gpt-6-astra` medium-effort design helper joins only if dev2-poc task design-helper-astra-poc shows it adds findings.
- Inputs before ideation: the read-only measurement of ui design reviews 2026-10-08 to 2026-10-22 (FO-dispatched, 2026-10-22) decides the declared model; dev2-poc task design-helper-astra-poc decides the helper.
- Upstream first: no design-director role in the installed plugins (searched 2026-10-22: `grep -rli 'design director'` over ~/.claude/plugins/cache and ~/.claude/skills found none); gstack `plan-design-review` is interactive, for a person, not a dispatched reviewer; the kc-dev-flow-2 chief-engineer and engineering-reviewer agent files are the pattern.
- Non-goals: changing the brief's eight dimensions or severities; a design review for tasks without `Surfaces: ui`.

## Captain amendments

### Amendment 1 — 2026-10-22, chat
Captain: 「設計總監照建議。這個角色會叫什麼？GPT 同伴仍保留提案，之後再討論」 (chat, 2026-10-22)
Asked: 「設計總監任務的範圍要不要照量測結果調整？」, with FO's four points: (1) the named design director runs the design review and stays on sonnet, since the measurement shows no evidence the model is the problem; (2) the author cannot decline a review finding alone: the design director rules on each finding the author would decline, and the ones it still declines are listed together at the design gate for the Captain; (3) at validation the design director reviews screenshots of the built screen; (4) dev2-poc task design-helper-astra-poc closes without running.
Supersedes: none
Design: the role runs the existing brief on sonnet; the author's declines go to the design director, and the ones it upholds are listed at the ideation gate; validation adds a design director review of screenshots of the built screen; the astra helper is dropped from this task. Evidence: intake/ui-design-review-measurement-2026-10-22.md.

## FO alignment

Captain rulings on D-1 to D-6 (ideation sitting, 2026-10-22, chat, each given to FO's question one at a time; to be bound at the ideation gate):
- D-1 「按你建議」, answering 「「整個畫面實際操作審一次」要不要變成正式的一關？」 with FO's recommendation: it belongs to the release-acceptance task as a second pass on the same operated walk, run by the design director, with a class for works but unusable; this task does not build it.
- D-2 「可以」, answering 「改成「檢查程式印出預覽圖的路徑，隨閘門資料一起給你」，可以嗎？」 (FO had corrected its earlier claim: today design_surfaces.py checks that the Preview file exists but prints only the design review report path and counts): design_surfaces.py check also prints each `Preview:` path, so the paths reach the briefing through the same workflow.md sentence that carries the upheld declines; no further workflow.md words. Override: recommended no FO rule (design D-2); Captain chose the checker printing preview paths; area: screenshots at ui gates.
- D-3 「按建議，這個再等搜集幾輪經驗」, answering 「預覽圖要不要畫出改動處周圍的整頁，桌機和手機寬度都畫？」 with FO's recommendation: not in this task; revisit after more rounds of experience.
- D-4 「可以」, answering 「照這個更正後的建議，可以嗎？」, where FO corrected its first recommendation (project learning) by kc-adr's five questions: a host-look departure ruling is the Captain's ruling on direction, so the first task where it appears lands it as an ADR in that product's repository; the design director reads the relevant ADRs before reviewing; the checker prints same-kind decision lines once per gate. Override: recommended recording it as project learning (design D-4); Captain chose an ADR per kind in the product repository; area: standing design rulings.
- Design guide 「可以」, answering 「設計指南先不做成格式，等設計類 ADR 累積起來再說，可以嗎？」 (raised by his 「這也帶來一個議題，design guide 需要變成一種 format 嗎？還是它就會是一種ADR？」): no design-guide format and no guide written as ADRs; a product's own design rulings are ADRs (D-4); revisit when a product's design ADRs grow enough that a generated index of them would help.
- D-5 「要擋下，不然找它的意義就消失了」, answering 「驗收時，如果設計總監沒有看過實際做好的畫面，要不要直接擋下？」: option A, validation refuses a ui task until a built-screen review with a screenshot that is not an ideation preview exists, or the Captain's quoted waiver.

Alignment: needed at ideation; the declared model and whether the helper joins are his, after the measurement and the POC.
Result: aligned 2026-10-22 by Amendment 1 (model stays sonnet; the astra helper is dropped; dev2-poc design-helper-astra-poc closed without running) and the backlog gate resolution (duty wording, two passes, host-component declines checked, replay before shipping).

Reviewer: kc-dev-flow-2:engineering-reviewer opus 2026-10-22 — do these amendments withdraw what the Captain approved, and what changes in the build?
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Status of inputs: Amendment 1 and the backlog gate resolution (the Captain's 「可以」, 2026-10-22) are the scope. The coordinator's later message relays a peer's three suggestions (`intake/paseo-fo-r1.5-intake-2026-10-22.md`); none is in this design as decided, and each is weighed under `## Unresolved decisions for the Captain`. Cycle 2 follows `reviews/engineering-reviewer-1.md` (verdict adjust); D-5 and D-6 come from it. The prompts of the replay treated the two host declaration files as the declaration path for every host component a decline names; they did not test the `<Name> at <path>` rule (see Replay).

### PRFAQ

**Press line.** From the next kc-dev-flow-2 release, a ui task's design review is run by a named agent, `kc-dev-flow-2:design-director`, on sonnet. The author can no longer close a finding alone: every decline the author proposes is ruled on by the design director against the picture, and the declines it upholds are printed in the gate briefing for the Captain, who keeps the final say. At validation the same agent looks at screenshots of the built screen.

**FAQ.**

- *Would this have caught the complaint that started it?* No. The Captain's Browse complaint (critique row 1, 「我按 broswe 沒料到…」) was a MINOR finding the author declined as "today's behaviour"; the director upholds that decline in both wording runs and in the control arm. Of the four critique rows graded blocking (1 to 4), none reaches a fix on its own finding under this design: row 1 stays closed, row 2 gets a fix for a different part of the finding, row 3 needed a running app, row 4 becomes a decision whose owner is the task the author already named. What the design changes is the class "the host component has no X" (rows 5, 10 and, for the buttons, 9b); the whole-screen class is D-1.
- *Why a named agent, when ADR 0022 chose a `general-purpose` agent and rejected "a new agent"?* ADR 0022 says "Reopen if a bite recurs that the review did not name". The 2026-10-22 measurement is not literally that bite (the review named 10 of the 14 critique findings); the loss is in the disposition: on 7 kc-paseo-plugins tasks the review raised 93 findings and the author declined 70. The Captain asked for the role in 「我還是希望開設計總監…」 and ruled 「設計總監照建議」 (Amendment 1). A new ADR records this (below), with a one-line pointer in ADR 0022.
- *Why sonnet?* Amendment 1 point 1; ADR 0022 D3 measured no gain from opus; every replay arm ran on sonnet and AC-7 reruns the shipped agent on sonnet.
- *Does the director gain authority?* No. It advises and holds no gate. What changes is who may close a finding: not the author alone. An overruled finding leaves three exits (fix, criterion, or a Needs decision that reaches the Captain with both views), so the Captain's final say is intact.
- *What does it not do?* It does not review whole releases or operate a running app at ideation (D-1), and it changes neither the eight dimensions nor the severities (Scope non-goal).
- *First consumer.* The six kc-paseo-plugins tasks now in `ideation` (`project-env-add-variable-one-step`, `-connection-collapse`, `-draft-survives-remount`, `-field-picker-grouped`, `-save-footer-danger-zone`, `-test-summary-failure-mark`) run their next ui design review, and any rework, through it.

```mermaid
sequenceDiagram
    participant A as Author (ideation worker)
    participant D as Design director (sonnet agent)
    participant C as design_surfaces.py check
    participant F as FO
    participant K as Captain
    participant V as Validator
    A->>D: pass 1a: brief, UI proposal, previews
    D-->>A: design_review report (findings, limitations)
    A->>A: write dispositions; propose declines
    A->>D: pass 1b: findings, proposed declines, cited pictures, host declarations
    D-->>A: design_decline_check report (upheld, overruled, decision)
    A->>A: overruled becomes fixed, AC or Needs decision; decision becomes Needs decision; upheld stays declined
    A->>C: run check
    C-->>F: output, one line per upheld decline
    F->>K: gate briefing carrying every upheld decline line
    K-->>F: approve, or overrule any listed decline
    V->>D: pass 2: built-screen screenshots and the criteria that name the running screen
    D-->>V: design_review report
    V->>F: findings in the validation report
    F->>K: validation gate material
```

### What changes

| Part | Change |
| --- | --- |
| `kc-dev-flow-2/agents/design-director.md` (new) | Wrapper like `observer.md`: `model: sonnet`, `reasoning: high` (the observer's pair; no measurement chose between high and another level), `skills: ["kc-dev-flow-2:design-director"]`. Adds no policy. |
| `kc-dev-flow-2/skills/design-director/SKILL.md` (new) | `Invocation: kc-dev-flow-2:design-director`. Holds the duty wording, the two passes, the three rulings, the return shapes, the boundaries. |
| `kc-dev-flow-2/skills/design-director/review-brief.md` (new) | The brief moved verbatim from `design-review.md` (eight dimensions, MAJOR/MINOR). Both passes read it; at validation "previews of a user interface that is not built yet" reads "screenshots of the built screen". |
| `kc-dev-flow-2/skills/ideation/design-review.md` | Step 1 dispatches `kc-dev-flow-2:design-director`; new step for the decline check; hand-forward rule. The brief block is removed (moved). |
| `kc-dev-flow-2/scripts/design_surfaces.py`, `test_design_surfaces.py` | The decline check at ideation; the built-screen review at validation, only if the Captain rules D-5 for it. Details below. |
| `kc-dev-flow-2/references/sd/workflow.md` | One sentence in the ideation Gate content swapped (+10 words): FO includes the checker's output in the gate material at any exit, so every `upheld decline` line reaches the Captain. Cycle 1 said this README rule was unneeded; the evidence below says it is. |
| `kc-dev-flow-2/scripts/lint-skills.py`, `test_lint_skills.py` | `AGENT_MODELS` gains `"design-director": ("sonnet", "high")` with a test like `test_observer_keeps_its_declared_model`; `WORKFLOW_BUDGET_STEPS` gains one raise step (delta 10) carrying the Captain's quoted words 「設計總監照建議」 and the moments FO reads it (startup and resume, and gate prepare at ideation), as ADR 0020 requires. |
| `kc-dev-flow-2/skills/validation/principles.md` | The screenshot sentence names the director pass and its line (if D-5 rules for it). |
| `kc-dev-flow-2/README.md` | One sentence in the roles paragraph (retained document: the role would otherwise be undocumented). |
| `docs/adr/<reserved>-<short title>.md` (new) and `docs/adr/0022-ui-ideation-design-review-binds-design.md` | A new ADR records the decision (draft below; the number is reserved by FO at the implementation dispatch under `## Number guards`, so the draft carries none). ADR 0022 gains one pointer line naming it. |

Not changed: `role_triggers.py` (the director is not a `Reviewer:` call), `pr_watch.py`, `delivery_gate.py`, `skills/ideation/principles.md`, the mod, any extension. `references/sd/workflow.md` changes in the one sentence above and nowhere else.

### Duty wording (as it will stand in `SKILL.md`; tested as `replay/duty.md`)

> You are the design director for one task's ui surface. You own its open design decisions: every finding on the screen ends as a fix, an acceptance criterion, or a decision that has a named owner, and no finding is closed by a reason you have not checked against the picture it concerns.
>
> Decline check. The author may propose to decline a MINOR finding. You check every proposed decline against the picture the finding cites, and rule exactly one of: **upheld** (the picture shows the reason holds, and a person using the screen is not misled, blocked or put at risk by leaving it); **overruled** (the picture still shows what the finding saw, or the reason does not answer it; say the fix, or the criterion that would test it); **decision** (the finding is real, but changing it departs from a host component, another task's work or a recorded ruling; name who decides).
>
> A decline that rests on a host component names the component and the path of its declaration (`declined: host component <Name> at <path>: <reason>`); with no path you rule decision, never upheld. You check it against that declaration, not the author's description. "The component has no X" stands only when the declaration has no prop, slot or children that can supply X and the plugin's own parts cannot either; name the prop or slot you looked for. When the declaration offers a way, the decline is overruled; when only a custom build is possible, it is a decision whose owner is whoever accepts a departure from the host's look.
>
> A decline that rests on another task, a release, a non-goal or "as today" stands only when the picture shows nothing a person would act on wrongly in the meantime. Otherwise it is a decision, and the owner is the task or record cited.
>
> You advise and hold no gate. The Captain keeps the final say: the declines you uphold are listed for him at the design gate.

Two passes, one agent:

- **Pass 1 (ideation), two dispatches.** 1a is today's blind review (previews and UI proposal only, brief unchanged). 1b is the decline check; it adds the findings, the author's proposed declines, the pictures they cite and the declaration files named in `host component … at <path>` lines. It reads no task file and no code. This relaxes ADR 0022's "reads no other file" for 1b only, and only for those named inputs.
- **Pass 2 (validation).** Screenshots of the built screen at the candidate, plus the criteria whose text names the running screen. The report has the same shape as 1a. What the screenshots cannot settle goes in `limitations`; the validator carries each as unverified or checks it with run evidence.
- **Hand-forward.** A pass-1 `limitations` entry that only the running screen can settle (a resize, a real vault, a Test run) becomes an acceptance criterion that names the running screen. This extends the existing step 3 of `design-review.md`; nothing mechanical ties a limitation to a criterion, so that link is by instruction only.

### Ideation records and the check

New line in `## Design` › `### Design review`: `Decline check: design/declines-<N>.yaml`, one per run, naming the saved report. Report shape: `design_decline_check:` with `rulings:`, each item `finding`, `ruling` (`upheld`, `overruled` or `decision`), `evidence`, `change`. The check reads by line pattern, like the existing report checks, because model output carries unquoted colons (6 of the 9 paseo reports fail YAML parsing).

`check_design_review` gains these refusals (each its own test, each with a mutation):

1. A `Design finding n: declined:` line and no `Decline check:` line → refused. More than one `Decline check:` line → refused.
2. A declined finding with no ruling in the report, or a ruling for a finding that is not declined → refused.
3. A declined finding whose ruling is `overruled` or `decision` → refused; it must be `fixed:`, `AC-<id>` or `Needs decision:`. A `decision` ruling needs a `Needs decision:` line.
4. A reason that begins `host component` without `<Name> at <path>:` → refused. The form is checked; whether the path is the right declaration is the director's ruling. A host decline written without the marker is not detectable by script, so the claim is bounded: the check enforces the form where the author writes it, and the director is told to rule `decision` on any decline that names a host component with no path.
5. Output: the summary line gains `; decline check design/declines-1.yaml: 6 upheld, 3 overruled, 2 decisions`, and each upheld decline prints one line `upheld decline <n>: <reason as written>`.

Why the workflow.md sentence is needed (cycle 2). The ideation stage text says "a non-zero exit means the gate is not presentable, and FO includes the checker's output in the gate material"; the clause rides on the non-zero case. Read 2026-10-22 on the paseo state checkout (read-only): the ideation `briefing-1/index.json` of three archived tasks (project-env-browse-vault-survives, project-env-variable-row-edit, project-env-test-results-match-draft) each hold a 77-character question and a one-sentence artifact summary ("r1.5 ideation design for <task>; design, acceptance criteria and stage report in the task file"), with no check output and no mention of the design review. An exit-0 line list would stay out of the briefing the same way, so the promise "listed for him at the design gate" would fail silently. AC-3 tests the briefing itself.

A report is model output saved by the author: the check cannot tell it came from the named agent (same limit ADR 0022 records for the review report).

At validation, only if D-5 rules for it. At `status: validation`, a `Surfaces:` including `ui` and a `Design review:` line in the body (so tasks ideated before the review existed are not caught), a `Built screen review:` line is required in the body or the stage report. Form 1: `Built screen review: design/validation-<N>.yaml`, naming a report with the `design_review:` shape whose `preview:` value names a file that (a) exists in the task folder, (b) is not a file named by, or inside a directory named by, any `Preview:` line, and (c) differs in sha256 from every file under those paths. Clause (b) and (c) close the hole that an ideation picture already in the task folder satisfies the check. Form 2: `Built screen review: waived 「<the Captain's words>」`, checked for a quoted span only (as ADR 0020 checks a raise). A missing line, a missing or ideation-identical file, or a waiver with no quote is refused with `built screen review not run`. The check proves a present file that is not an ideation picture; it cannot prove the picture shows the built screen at the candidate (a validator could save any other picture), so the validation reviewer compares the picture to the candidate by the run evidence already required. At validation a director finding is not "declined" by anyone: the validator lists a MAJOR as a finding and classifies it by the existing four fields (Material, Deferred risk, Polish, Needs decision); a MINOR is Polish unless those fields say otherwise (D-6).

### Replay (prototype outside the repository, before proposing)

Method. The wording above was written to `replay/duty.md` and given to a fresh `general-purpose` agent on `model: sonnet`, one per task, for the 7 kc-paseo-plugins tasks whose last design reports hold the 93 findings the measurement counted (70 declined). Each agent got the task's UI proposal, the author's proposed declines verbatim, the preview pictures the findings cite (copied to a folder with nothing else in it) and the two host declaration files of `@getpaseo/plugin` 0.12.0 (`ui.d.ts`, `react-native.d.ts`). It was not told which findings the Captain's critique later matched, nor given the critique. The recorded dispositions are the baseline: no second check, all 70 declines closed by the author. **Waiver:** every prompt carries the sentence "treat the two declaration files above as the declaration path for every host component a decline names, so none is ruled decision for a missing path". The `<Name> at <path>` rule of the wording was therefore not tested. Real authors wrote no paths, so under the shipped wording the 37 of 70 declines that cite a host component by keyword would start as `decision` until authors adopt the form; the 31/18/21 split and the load below describe compliant authors. Prompts, raw reports, the dump and the mapping are in `replay/` (`replay/README.md` says how to rerun).

Result over all 70 declines (wording arm, run 1): **31 overruled, 18 decision, 21 upheld.** A second wording run on three tasks (browse-vault-survives, test-results-match-draft, variable-row-edit; 39 declines) agreed with run 1 on 35 (90%). The 4 disagreements are in rows outside the table below. Reported `subagent_tokens`: 619k for the seven runs, 273k for the three repeats.

**Control arm (cycle 2).** The same sonnet second check, on the same three tasks and 39 declines, with the two declaration files and the waiver sentence but without the duty wording: the prompt says to check each proposed decline against the pictures and the declarations and gives one clause per ruling (`replay/control/`). One run per task; 272,357 `subagent_tokens`.

| 39 declines, three tasks | overruled | decision | upheld |
| --- | --- | --- | --- |
| wording, run 1 | 15 | 12 | 12 |
| wording, run 2 | 14 | 11 | 14 |
| control (declarations, no wording) | 6 | 10 | 23 |

Agreement on the 39: wording run 1 with run 2, 35; control with run 1, 18; control with run 2, 20. So the wording is not the same check as "look at the declarations": it overrules 14 to 15 where the control overrules 6, and 5 of the control's 23 upheld declines (browse #1, #13; variable-row-edit #9, #15, #18) are overruled in both wording runs. Limits: one control run per task (no measure of its own run-to-run spread), the control prompt is my own wording of a neutral check, and whether the overrules are right (precision) is graded by nobody.

The Captain's critique rows that fall in these three tasks (the measurement lists the row numbers; the mapping to review findings is mine, `replay/mapping.tsv`):

| Critique row | Review finding and recorded disposition | Wording (run 1, run 2) | Control | Reaches |
| --- | --- | --- | --- | --- |
| 1 hidden mode switch (the Captain's Browse complaint) | browse-vault-survives #11, declined "today's behaviour" | upheld, upheld | upheld | closed in all three |
| 2 references cut off | variable-row-edit #18, declined "host input scrolls" | overruled, overruled | upheld | wording: a fix for the Testing state and failure count, not the cut-off |
| 4 flat picker | variable-row-edit #16, declined "T5 owns it" | decision, decision | decision | a decision whose owner is the task the author named, in both arms |
| 5 add variable in three steps | variable-row-edit #4, declined "today's host rows" | overruled, overruled | decision | wording: a fix (one row through the `children` slot); control: a decision |
| 7 no next step | browse-vault-survives #7, declined "ruled cause form, ADR 0002" | upheld, upheld | upheld | closed in all three (plain-failure-reason #10 is outside the three tasks) |
| 8 connection card noise | variable-row-edit #3, declined "host chrome" | upheld, upheld | decision | wording: closed; control: a decision |
| 9b Stop managing beside Save; destructive confirm like Keep | variable-row-edit #12 and #13, declined "host has one style" | overruled both, in both runs | overruled both | a fix in all three: not an effect of the wording |
| 10 notes posing as rows | browse-vault-survives #1, declined "no weight control" | overruled, overruled | upheld | wording: a fix (marker through `children`); control: closed |
| 12 success grey like a hint | variable-row-edit #7 (primary), test-results-match-draft #6 (secondary) | upheld, upheld; overruled, overruled | decision, decision | wording: secondary fix (failure through the `error` prop), primary closed; control: both decisions |

Rows 6 and 9a were already at the Captain as MAJOR Needs decision and are unchanged. Rows 3 and 13 needed a running app or an unpictured screen, and rows 11 and 14 (a whole and a partial miss) are not in these three tasks.

Restated claim. On these three tasks the duty wording reaches a fix for rows 5 and 10 that the control does not (the control rules 5 a decision and leaves 10 closed), and row 9b reaches a fix with or without the wording. Row 4 reaches a decision in both arms and its owner stays the task the author named. Row 12 is qualified: the wording closes the primary finding and fixes the secondary one. Row 8 is closed by the wording and raised as a decision by the control. None of the four blocking rows (1 to 4) reaches a fix on its own finding, and the Captain's own complaint, row 1, is upheld in both wording runs and in the control. The claim "the wording works on one class" holds for the declines that say "the host component has no X": 17 of the 31 run-1 overrules name a declared prop, slot or hook as the means of the fix under the strict reading (`children`, `error`, `hint`, `placeholder`, `disabled`, `trailing`, `info`, `useToast`, `ScrollView`, `FlatList`, `Modal.Content`, `contentContainerStyle`) and 25 under the broad reading (any mention of a declaration file, a Settings* part, a prop, a slot or a backticked name); `replay/count_citations.py out/` prints both, and the 6 left over rule from the picture alone. The earlier figure of 23 had no stated rule and is withdrawn. The wording does not reach the whole-screen class (rows 1, 2, 8): there each finding on its own picture "misleads nobody" and the harm is the sum. Row 7 was closed by a real Captain ruling (ADR 0002 fixes the cause text), so "upheld" is arguably right. Further limits: one project, one wording run per task for 4 of 7 tasks, rulings graded by me from the `ruling` field, the 10 rows were chosen because a later critique vindicated them, the agent saw pictures and a declaration file, not the running host, and the d.ts says a prop exists, not how the host renders it.

Load. At the ideation gate the Captain's list would have been 21 upheld lines over 7 tasks (1 to 6 per task) and 18 decisions (already Needs-decision lines today), and the authors would have owed 31 fixes or criteria they did not owe. That is the price; AC-7 bounds it. Nine of the 18 decisions are the same question, so D-4 asks for one standing ruling.

### Words FO reads at each lifecycle moment

Counted with `wc -w` on `origin/main` b93612f8 (no `kc-dev-flow-2/` change since e1f43044, checked with `git diff --stat e1f43044 origin/main -- kc-dev-flow-2 docs/adr`, 2026-10-22). Same count method for the candidate; each moment needs the candidate count recomputed at validation.

| Moment | Base (words) | Candidate | Basis |
| --- | --- | --- | --- |
| startup and resume (`references/sd/workflow.md`) | 5374 | 5384 | one sentence swapped in the ideation Gate content: measured by applying the swap to the base file, +10 under `wc -w` and +10 under the `lint-skills.py` tokenizer; AC-8 recounts the candidate |
| idle on an open PR / idle on a merged PR / after the archive / the merge ask | unchanged text | unchanged | `pr_watch.py`, `delivery_gate.py` not edited; `pr_watch.py` runs `check --seed`, which returns before the ui checks. The startup moment above is also read at these. |
| ideation gate prepare, ui task (checker output) | 13 measured on two archived paseo tasks, plus the design-review summary line (14 words by the test fixture's form); none of it reaches the briefing (3 archived paseo briefings) | + decline-check summary (about 13 words) + one line per upheld decline: **30 to 141 words per task, median 60**, simulated from the author's decline text for the 7 tasks (529 words over 21 lines); now carried into the briefing | simulation, not a run of the new check; AC-3 and AC-8 report the real count |
| validation gate, ui task | 13 (no design lines at that status) | + one summary line (about 14 words), if D-5 rules for the validation check | design |

The ideation gate rises, by design: Amendment 1 asks for the list at the gate. The learning "each moment below its base" applies to a change whose goal is to cut what FO reads; this one adds a Captain-owed list and leaves the idle and merge moments unchanged. ADR 0022 recorded "13 more words at the ideation gate of a ui task"; the new ADR replaces that number.

### ADR draft (no number; FO reserves one at the implementation dispatch)

File `docs/adr/<reserved>-a-ui-design-review-is-run-by-a-named-director-and-a-decline-needs-its-ruling.md`:

> # <reserved>. A ui design review is run by a named director, and a declined finding is closed only by its upheld ruling
>
> ## Status — Proposed
>
> ## Context — The 2026-10-22 measurement on 7 kc-paseo-plugins tasks: 93 findings, 70 declined by the author (37 citing a host component), 10 of the 14 findings of a later critique already raised and declined at MINOR, 4 of 7 validations without a screenshot of the candidate. ADR 0022 chose a `general-purpose` agent and a worker who dispositions its own findings. A replay of 70 declines with a second sonnet check overruled 31; the same check on 39 of them without the duty wording overruled 6 and upheld 23. The Captain's own Browse complaint stays declined under every arm.
>
> ## Decision — **Words:** 「我還是希望開設計總監，讓它來做目前指示的內容…」 (chat, 2026-10-22), 「可以」 (backlog gate, 2026-10-22), 「設計總監照建議」 (chat, 2026-10-22), and the ideation-gate approval words FO adds. **Options considered:** the named `design-director` agent on sonnet rules each proposed decline and the upheld ones are listed for the Captain (chosen); keep the `general-purpose` agent and the author's own dispositions — not chosen, it is the measured loss; a second sonnet check with the declarations but without the duty wording — not chosen, it upholds 23 of 39 where the wording upholds 12 to 14; opus — not chosen, ADR 0022 D3 measured no gain and the measurement shows no evidence the model is the problem; a gpt-6-astra helper — dropped by the Captain, Amendment 1; a release-level operated whole-screen review — not decided here (D-1). **Recommended:** the first option, as the Captain's 「設計總監照建議」 accepted; the validation pass follows the Captain's ruling on D-5.
>
> ## Consequences — Each ui ideation costs a second director run (77k to 115k tokens per task on the replay) and the Captain reads the upheld lines at the gate (30 to 141 words per task, simulated). The check proves a ruling exists and its form, not that the agent that wrote the report was the named one, nor that an upheld decline is right. The whole-screen class stays open. Reopen if a decline the director upheld is later found wrong at a gate or a critique, or when D-1 is ruled.

ADR 0022 gains one line after its Consequences: `Amended 2026-10-22: the review is run by the named design-director agent and a declined finding needs its ruling; see ADR <reserved>.`

### Batch overlap

Files this design changes: `kc-dev-flow-2/agents/design-director.md`, `kc-dev-flow-2/skills/design-director/SKILL.md` and `review-brief.md` (all new); `skills/ideation/design-review.md`; `skills/validation/principles.md`; `scripts/design_surfaces.py` and `test_design_surfaces.py`; `scripts/lint-skills.py` and `test_lint_skills.py`; `references/sd/workflow.md` (one sentence); `kc-dev-flow-2/README.md`; `docs/adr/` (one new record, number reserved at implementation) and `docs/adr/0022-ui-ideation-design-review-binds-design.md` (one line). Read 2026-10-22 from the task files in this state checkout at HEAD 2160c4af and from the PR lists in their own overlap tables; every task named in the checklist now has a readable file, in the checkout or its `_archive/`.

| Other task | Same file or check | Order |
| --- | --- | --- |
| fo-write-checks-parse-top-level (batch 5, ideation) | yes: `design_surfaces.py` (`scope_lines`, one docstring clause) and `test_design_surfaces.py` (`ScopeCheckTests`); mine adds functions near `check_design_review` and edits no docstring. Its AC-6 lists exactly four changed files and "the same word budget": if mine merges first, its base moves by the +10 step | different functions; second to merge rebases; either order |
| release-acceptance (ideation; its ideation briefing is recorded and has no resolution) | yes: `references/sd/workflow.md` (its Release-review bullet; mine is the ideation Gate content sentence) and, if it adds words, the `WORKFLOW_BUDGET_STEPS` list; its README edit is a different paragraph | different passages; if both add words the later PR recounts and adds its own step (ADR 0020 Consequences); D-1 asks whose stage a whole-screen review is |
| new-work-starts-from-a-story-map (batch 5, validation, PR #705) | no: `references/sd/workflow.md` and `lint-skills.py`'s budget are unchanged by it (its AC-10 diffs both for nothing); it reserves ADR 0029; it edits `skills/ideation/principles.md`, which this design leaves alone | none; my ADR takes the next free number, so reserve after it merges or is released |
| merge-ask-holds-missing-clauses (batch 5, validation, PR #703) | no: `delivery_gate.py`, ADR 0023 and 0026; it adds no ADR number | none |
| codex-reader-counts-code-review-only (batch 5, validation, PR #702) | none: `extensions/codex/`; it reads `README.md`, edits no line of it | none |
| comment-check-reaches-delivery-gate (ideation, resolved `hold`) | would replace one sentence of `skills/validation/principles.md`; mine replaces the screenshot sentence; it adds no `workflow.md` edit and no budget step | adjacent hunks; second rebases |
| codex-reader-reads-receipt-marker (merged #693), idle-names-failing-seeds (merged #694), agent-reads-governing-adr (archived done), kc-decision-log-cli (archived done) | none: `extensions/codex/`, `pr_watch.py` (#694, already in the base), `AGENTS.md`, `scripts/adr-path-check.py` | none |
| override-reaches-gate-and-criteria-wait, amendment-form-check-round3-followups (backlog) | `design_surfaces.py` `check_amendments` | different function; order only if pulled forward |
| design-surfaces-task-dir-crash (backlog) | `design_surfaces.py` `main` and task-dir handling; my new checks resolve the report folder with the same helper as `check_design_review` | if it lands first, mine follows its folder handling |
| journey-server-host-pilot (validation, other session), kc-decision-log-p1 (archived backlog), kc-decision-log-handoff-trial (backlog), pr-review-lite-value-pilot (implementation), journey-canvas-hosted-poc (ideation), read-adr-reporting-rule-followup (validation) | none edits these files: `grep -c` of each task file for `design-review.md`, `lint-skills`, `sd/workflow.md`, `kc-dev-flow-2/agents`, `kc-dev-flow-2/README` found none (journey-server-host-pilot and read-adr-reporting-rule-followup only record runs of `design_surfaces.py check`). Only the check's verdict could change, and only for a task whose `Surfaces:` include `ui` with a `Design review:` line | none |
| ADR directory | new record at the next free number after 0029 (new-work-starts-from-a-story-map); amends 0022 by one line; merge-ask amends 0023 and 0026 | none |

Recommended order: no hard constraint. If fo-write-checks-parse-top-level merges first, rebase this task's `design_surfaces.py` hunks onto it; release as one `feat(kc-dev-flow-2)` PR with the agent, skill, checks and the workflow sentence together, because the check refuses declines without the report the skill now asks for.

## Acceptance criteria

**AC-1** The agent exists, declares sonnet, and is bound to its skill. Evidence: at the candidate, `python3 <package>/scripts/lint-skills.py` exits 0 with `design-director` in `AGENT_MODELS`, and `python3 -B -m unittest test_lint_skills` (run in `<package>/scripts`) passes a new case. Falsifier: that case changes `model: sonnet` to `model: inherit` in `agents/design-director.md` and expects "design-director agent: existing sonnet/high policy changed"; deleting `skills/design-director/SKILL.md` must give "missing skills: design-director". Not yet verified.

**AC-2** The brief moves with its eight dimensions and two severities unchanged. Evidence: the blockquote in `origin/main:kc-dev-flow-2/skills/ideation/design-review.md` and the blockquote in `skills/design-director/review-brief.md` compared with `diff` differ only in the one sentence that names screenshots for pass 2, and `design-review.md` no longer carries the blockquote. Falsifier: editing one word of one dimension makes `diff` print it. Not yet verified.

**AC-3** One real ui ideation dispatches the named agent twice, the check passes on its output, and every upheld decline reaches the briefing FO prepares. Evidence: a ui ideation run on the candidate package for one of the six paseo tasks in `ideation` (the first consumer); its transcript shows two Agent calls with `subagent_type: kc-dev-flow-2:design-director` and none with `general-purpose`; `design/ideation-<N>.yaml` and `design/declines-<N>.yaml` exist; `design_surfaces.py check` exits 0 and prints the upheld lines; and the briefing prepared for that ideation gate (`review/ideation/briefing-<n>/index.json` in the state checkout, in its `question` or an artifact `summary`) contains each printed `upheld decline <n>:` line, so the count of those lines in `index.json` equals the `N upheld` of the summary line. Falsifier: the same run on the base package shows `general-purpose` and no `declines-<N>.yaml`, and the base briefings of three paseo ideations (browse-vault-survives, variable-row-edit, test-results-match-draft, read 2026-10-22) hold no checker output; an FO run with the workflow sentence reverted that leaves a briefing without the lines fails the last clause. A substring check of `design-review.md` is not offered as proof. Not yet verified.

**AC-4** A declined finding passes only with an `upheld` ruling. Evidence: new cases in `test_design_surfaces.py`, one per refusal 1 to 4 above (no `Decline check:` line; missing ruling; ruling for an undeclined finding; `overruled` or `decision` still declined; `host component` with no `<Name> at <path>:`; two `Decline check:` lines), each asserting the refusal's reason text, plus one passing case. Falsifier: for each refusal, a `mutated(...)` copy of the check with that branch removed makes its case fail (the file's existing mutation pattern); the suite also fails if a case asserts only the exit code. Not yet verified.

**AC-5** The gate material lists every upheld decline, not a count. Evidence: a case with 3 declined findings (2 upheld, 1 overruled, the overruled one redisposed to `fixed:`) asserts the output holds exactly two `upheld decline <n>: <reason>` lines with the author's reasons, and that the summary line counts `2 upheld, 1 overruled, 0 decisions`. Falsifier: a mutant that prints only the count fails the case. Not yet verified.

**AC-6 (only if the Captain rules D-5 for the check)** A ui task cannot reach a passing validation check without a built-screen review or a quoted waiver. Evidence: cases at `status: validation` for a task with `Surfaces: ui` and a `Design review:` line: no `Built screen review:` line is refused with "built screen review not run"; a line naming a report whose `preview:` file is absent from the task folder is refused; a line naming a report whose `preview:` file is a byte-copy of a file under a `Preview:` path (an ideation picture) is refused; a line with a present screenshot of different bytes passes; `waived` with a 「…」 quote passes and `waived` without one is refused; a task with no `Design review:` line (ideated before the review) is not refused; `status: implementation` is not refused. Falsifier: mutants that drop the status gate, the file-exists test, the byte comparison against the `Preview:` files, the quote test or the `Design review:` condition each fail a case. Limit stated in the report: the check cannot tell that a different file shows the built screen. Not yet verified.

**AC-7** The shipped agent, not the prototype, rules as the prototype did, and not as the control does. Evidence: run the three prompts in `replay/prompts/` (browse-vault-survives, test-results-match-draft, variable-row-edit) with `subagent_type: kc-dev-flow-2:design-director` on the candidate, then compare `ruling` fields with `replay/out/` and `replay/control/rulings.tsv`: of the 39 declines between 8 and 18 are upheld and at least 12 are overruled; rows #5 (variable-row-edit #4) and #10 (browse-vault-survives #1) are overruled and row #9b (#12, #13) is overruled; row #4 (#16) is a decision. The bounds are a margin around the measured 12 and 14 upheld and 14 and 15 overruled, not a measured range; run-to-run agreement was 90% on 39 declines; the run costs about 273k subagent tokens. Falsifier: the control arm already measured (23 upheld, 6 overruled, #5 a decision, #10 upheld) falls outside the bounds on four counts, and a shipped agent that upholds all or none falls outside them too. Not yet verified; the prototype result is the 15/12/12 and 14/11/14 split above.

**AC-8** FO-read text changes only where this design says. Evidence: `git diff <base> <candidate> --stat -- kc-dev-flow-2/scripts/pr_watch.py kc-dev-flow-2/scripts/delivery_gate.py kc-dev-flow-2/scripts/role_triggers.py` prints nothing; `git diff <base> <candidate> -- kc-dev-flow-2/references/sd/workflow.md` is one hunk in the ideation Gate content; `wc -w` of `workflow.md` at the candidate is 5384; `lint-skills.py` passes with exactly one added `WORKFLOW_BUDGET_STEPS` entry (delta 10, a quoted `captain` value, a `loaded` value). The ideation-gate and validation-gate counts in the table above are recomputed from a real run of the candidate check on the AC-3 task and reported next to the simulated ones. Falsifier: any other edit to those files, a missing `captain` or `loaded` value, or a lint budget error. Not yet verified.

**AC-9** The retained documents match the new role. Evidence: `README.md` names the role, its model and that it advises; a new ADR file at the number FO reserved carries `**Words:**`, `**Options considered:**` and `**Recommended:**` lines and the Captain's quoted words; `python3 <package>/scripts/adr_lint.py docs/adr --since <base> --require <reserved>` exits 0; ADR 0022 carries one line naming that number (checked by a grep in the validation report; no tool parses it); `python3 <package>/scripts/doc_impact.py <base> <candidate>` reports no unread affected document. Falsifier: removing the `**Options considered:**` line from the new record makes `adr_lint.py` exit 1 with "Decision needs a '**Options considered:**' line" (run 2026-10-22 on a fixture of origin/main b93612f). Not yet verified.

## Unresolved decisions for the Captain

D-1 to D-3 come from the coordinator's relayed peer suggestions (none approved scope), D-4 from the replay, D-5 and D-6 from the engineering reviewer's report. Amendment 1 does not depend on any of them, except that the validation pass in the design above is the check D-5 asks about.

**D-1 — Does an operated whole-screen design review become a stage, and whose stage is it? (the peer's suggestion 1)** Recommendation: it is the release-acceptance task's, not this one's: ask that task to add a second pass over the same walk, run by this director, with a class for "works but unusable". Reasons: (1) the hand run is already done: the r1.5 critique is an operated, whole-screen design-director walk on an isolated Paseo, and it found four blocking problems after six per-task gates had passed (intake), so the question is no longer whether to try it but who owns it; (2) read 2026-10-22, `release-acceptance/index.md` (status `ideation`; its ideation briefing is recorded and has no resolution) already defines the trigger (after the last story of a release is built), a fresh worker, an `Environment:` slot and an operated hosted walk, but its report asks "does each story work" (`works | broken | missing-entry-point | not-reachable`) and its finding classes (`defect | known-gap | environment | by-design | not-defect`) have no place for usability, so the files do not collide and the machinery would be built twice; (3) the replay shows the per-task wording leaves rows 1, 2 and 8 closed, so the gap is real. What gets worse under this recommendation: until that task ships its design, nothing stops the next release with a screen-level defect passing every task gate, as r1.5 did, and the Captain meets it by using the screen; and the operated pass needs browser tools the agent file does not give the director in this design. The alternative is a stage owned by this task, which duplicates the trigger and the walker.

**D-2 — Ideation and validation gate presentations show the Captain screenshots, not only text (suggestion 2).** Recommendation: add no FO rule for pictures now; the checker already prints the `Preview:` path and the lines the briefing now carries. A picture rule needs another `workflow.md` raise under ADR 0020. What gets worse: the gate stays text, so the Captain looks at pictures only if he opens the printed paths.

**D-3 — Previews show the whole page around the change, at desktop and narrow widths (suggestion 3).** Recommendation: leave it out of this task. It changes what `skills/ideation/principles.md` asks an author to draw, a file other tasks touch, and the brief's dimension 8 already lists size and theme combinations as findings. Pass 2 sees the built whole screen at validation. What gets worse: fragment previews keep hiding cross-part effects at ideation, such as Browse vault changing rows in another card, until validation.

**D-4 — One standing ruling for "depart from the host's look" decisions.** 9 of the 18 `decision` rulings in the replay were this single question (own 44px phone buttons, a primary or destructive button, one row height), asked again in 7 tasks. Recommendation: the Captain rules once per kind when it first appears, FO records it as project learning, and the checker prints decision lines grouped by owner so the same question shows once per gate. What gets worse: a standing ruling is made before seeing each screen, and a later screen may deserve a different answer; until he rules, each task asks again. Nothing bounds how many overruled findings an author routes to `Needs decision:` instead of fixing, and each such line is a Captain question; the replay measured 18 decisions from the director itself and nothing about how authors would route 31 overrules. The grouping of printed lines is a small check change that is not in the ACs above; if the Captain wants it, it becomes AC-10.

**D-5 — Does validation refuse a ui task that has no built-screen review?** Amendment 1 and the backlog 「可以」 approved that the director reviews screenshots of the built screen at validation; they did not approve a refusal. The design as written turns it into one (AC-6). Cost: on the measurement, 4 of 7 past paseo validation reports (browse-vault-survives, paste-token-check-first, plain-failure-reason, token-works-cause) said no screenshot of the candidate screen exists, so under the check each would have been refused until a screenshot was produced or the Captain waived it. Options: A, refuse until a built-screen report with a screenshot that is not an ideation picture exists, or the Captain's quoted waiver (the design as written, hole closed); B, the check prints `built screen review: <report>` or `not run` in the validation summary and refuses nothing; C, no check, the instruction in `validation/principles.md` only. Recommendation: A. It is the only option that stops the 4-of-7 pattern; B shows it to the Captain but does not stop it. What gets worse under A: a ui validation can stall where the validator cannot run the screen, each stall costs the Captain a waiver or an environment fix, a waiver is checked for a quoted span, not for being his, and the check proves a present, different file, not a picture of the right build. If he rules B or C, AC-6 and the validation hunk of the design are dropped and the rest stands.

**D-6 — At validation, does a MINOR finding of the director default to Polish?** In the design a pass-2 MINOR is Polish unless the four existing fields (Material, Deferred risk, Polish, Needs decision) say otherwise, and a Polish finding can be declined by FO with a bracketed reason at delivery. That is the same path along which the 70 declines closed at ideation (85 of the 93 findings were MINOR). Options: A, keep the default and print only a count of MINORs in the validation summary line; B, print one line per pass-2 MINOR at the validation gate, as upheld declines are printed at ideation; C, no default, every pass-2 MINOR is a Needs decision. Recommendation: A. B would add on the order of 12 lines per ui task (the pass-1 average, 85 MINOR over 7 tasks; pass 2 is not measured) and C turns every polish note into a Captain question. What gets worse under A: a MINOR that a later critique would call blocking can still be declined by FO and the Captain sees a number, not the finding; the list under B is what would have surfaced rows 2 and 8.

## Stage Report: ideation

- DONE: Design the kc-dev-flow-2:design-director agent and skill per Amendment 1 and the backlog gate resolution: duty wording (owns the open design decisions; every decline the author proposes is checked against the picture by the design director; upheld declines listed at the ideation gate for the Captain, who keeps the final say), two passes (pictures at ideation, built-screen screenshots at validation, with what only the running screen can settle handed forward), a host-component decline checked against that component, model sonnet; read intake/ui-design-review-measurement-2026-10-22.md and intake/design-role-research-2026-10-22.md; prototype the duty wording outside the repository and replay it on the 10 already-raised kc-paseo-plugins findings (mapping in the measurement intake) to show whether each would now reach the Captain or a fix, before proposing it
  Design above; chain checked (Spacedock: no role; kc-dev-flow-2 0.27.0 and origin/main e1f43044: observer, chief-engineer, engineering-reviewer are the pattern, ADR 0022 chose `general-purpose` and says reopen on a recurring bite; no sibling design role). Replay in `replay/`: 70 declines, 31 overruled, 18 decision, 21 upheld; the critique-row count is restated in cycle 2 with a control arm; run 2 agreed on 35 of 39.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, fo-write-checks-parse-top-level, idle-names-failing-seeds, agent-reads-governing-adr) and live task of other sessions (kc-decision-log-p1, kc-decision-log-cli, kc-decision-log-handoff-trial, pr-review-lite-value-pilot, release-acceptance, journey-canvas-hosted-poc, journey-server-host-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Done above; three of the other sessions' tasks (release-acceptance, journey-server-host-pilot, kc-decision-log-p1) have no task file in this checkout and were not read.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Table above: startup 5374 to 5374; the idle, merge-ask moments unchanged by diff; ideation gate rises by 30 to 141 words per ui task (simulated, not a run); validation gate by about 14. AC-8 recomputes from a real run.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-9 each carry an evidence clause and a falsifier; all are "not yet verified" because nothing is built. D-1 to D-4 under `## Unresolved decisions for the Captain`.

### Summary

The design adds one agent, one skill and two checks: a declined finding passes only with an `upheld` ruling that the gate prints, and a ui task needs a built-screen review at validation. The replay shows the wording reaches the "host component has no X" class of declines and not the whole-screen class, so the peer's release-level review is left to the Captain (D-1) with a recommendation to try it once by hand. `design_surfaces.py check` (package 0.27.0) printed "design-director-runs-ui-design-review.md: design surfaces presentable", exit 0. The Scope check printed nothing further because this task's backlog approval and Amendment 1 are the baseline.

## Stage Report: ideation (cycle 2)

Cycle 2 supersedes cycle 1 above where they differ (the replay claim, the ADR route, AC-3, AC-6 to AC-9, D-1, D-4, the words table).

- DONE: Cycle 2 revision per reviews/engineering-reviewer-1.md (verdict adjust), keeping every item of Amendment 1 and the backlog gate resolution: (1) name the validation-stage refusal (built screen review not run) as an unresolved decision for the Captain with its cost (it would have failed 4 of 7 past paseo validations), and close the hole that an ideation preview in the task folder satisfies it; name the MINOR-defaults-to-Polish rule at validation as a decision too; (2) extend AC-3 so the upheld-decline lines must appear in the briefing FO prepares, not only in checker output; (3) run a no-wording control arm (same sonnet second check with the host declaration files, without the duty wording) on the same 3 tasks the repeat used, state the result beside the wording arm, state in the task body that the prompts treated the two declaration files as the declaration path, and restate the replay claim to what the arms show (rows #5, #9b, #10 solid; #4 and #12 qualified; none of the four blocking rows reaches a fix; row 1, the Browse complaint, is upheld in both runs); (4) land the decision as a new ADR with a one-line pointer in ADR 0022, and drop the AC-9 falsifier the ADR format checker cannot fail; (5) reframe D-1 as whether an operated whole-screen review becomes a stage and whose stage, citing the r1.5 critique as the hand run already done and reading the release-acceptance task file before claiming a collision; note under D-4 that nothing bounds routing every overrule to Needs decision; (6) remove the stale text that says FO alignment has no Result line, and state the counting rule for the prop, slot or children figure
  (1) D-5 (validation refusal, cost 4 of 7) and D-6 (MINOR to Polish); AC-6 now needs a byte-different, non-`Preview:` file or a quoted waiver. (2) AC-3 reads the prepared briefing; read-only check of 3 archived paseo ideation briefings (77-character question, no checker output) is why the design adds one workflow.md sentence (+10 words, ADR 0020 step). (3) Control arm run on 3 tasks, 39 declines: wording 15/12/12 and 14/11/14 (overruled/decision/upheld), control 6/10/23, control agrees with wording on 18 and 20 of 39; waiver stated under Replay; claim restated with row 9b reached by the control too, and rows 5 and 10 wording-only. (4) ADR draft in the task, pointer line for 0022, AC-9 falsifier replaced by one I ran (removing `**Options considered:**` gives `adr_lint.py` exit 1 on an origin/main fixture). (5) D-1 reframed, `release-acceptance/index.md` read (walk of whether each story works; no usability class); D-4 note added. (6) FO alignment text fixed; counting rule and `replay/count_citations.py`: 17 strict, 25 broad of 31, the 23 withdrawn.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, fo-write-checks-parse-top-level, idle-names-failing-seeds, agent-reads-governing-adr) and live task of other sessions (kc-decision-log-p1, kc-decision-log-cli, kc-decision-log-handoff-trial, pr-review-lite-value-pilot, release-acceptance, journey-canvas-hosted-poc, journey-server-host-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Redone at state HEAD 2160c4af and origin/main b93612f8; every named task file was read (release-acceptance, journey-server-host-pilot, kc-decision-log-p1 included); new overlaps: `workflow.md` and the budget steps with release-acceptance, the ADR number after 0029.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Table under `### Words FO reads at each lifecycle moment`: startup 5374 to 5384 (measured by applying the sentence swap), ideation gate now carries the upheld lines in the briefing, validation gate +14 if D-5 rules for it; idle and merge moments unchanged by diff.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-9 each carry evidence and a falsifier, all "not yet verified" because nothing is built; D-1 to D-6 each carry a recommendation and what gets worse. `design_surfaces.py check` of package 0.27.0 re-run on this file at the end of cycle 2 (result in Summary).

### Summary

The design is the same agent, skill and two checks, now with one `workflow.md` sentence (+10 words) so the upheld declines reach the briefing, and a new ADR instead of an Amended paragraph. The control arm shows the duty wording does move declines (control upholds 23 of 39, the wording 12 to 14), but also that row 9b is reached without it and that the Captain's own Browse complaint stays closed in every arm. Needs the Captain: D-5 (does validation refuse a ui task with no built-screen review) and D-6 first, because they change what is built; D-1 asks that the whole-screen review go to release-acceptance.
