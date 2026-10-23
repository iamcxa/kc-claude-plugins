---
title: A named design-director role runs the ui design review in place of a general-purpose sonnet agent
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
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
        - id: gate:design-director-runs-ui-design-review:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:design-director-runs-ui-design-review-ideation-1
              briefing:
                id: briefing:design-director-runs-ui-design-review:ideation:attempt-1:revision-1
                digest: sha256:cafdccd64aa81a9edd08f2342a41f216e44b5a34bd4d7a34b71bd1528b19ef74
                room-ref: ./design-director-runs-ui-design-review/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:design-director-runs-ui-design-review:ideation:1
                briefing: briefing:design-director-runs-ui-design-review:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-22T11:30:35.929803Z"
                decision: approve
                reason: Captain 「可以」 (chat, 2026-10-22), answering 「設計總監的設計已經把你的 6 題裁定全部改進去了，可以開設計閘門。要你決定的是：可以進入實作嗎？我建議可以。」 whose presentation listed that approval accepts D-7 as designed and raising the workflow.md word budget by 15 words, 5374 to 5389 (ideation Gate content +1, validation Gate content +14); digest cafdccd6. Accepts the FO recommendation as the bound question states. Rulings D-1 to D-6 and the design-guide ruling are recorded under FO alignment.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-22T11:31:12Z
worktree: .worktrees/spacedock-ensign-design-director-runs-ui-design-review
pr: iamcxa/kc-claude-plugins#708
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

### Amendment 2 — 2026-10-23, chat
Captain: 「可以」 (chat, 2026-10-23)
Asked: 「同意這樣改嗎？」, where FO stated the two changes: (1) AC-7 is restated to the measured result, with no pass bound: on the final wording both runs overruled more declines than the no-wording control (12 and 9 against 6) and upheld fewer (13 and 18 against 23), and one run missed the original bounds; (2) AC-3 runs at the first kc-paseo-plugins ui ideation after release: the upheld-decline lines must appear in the briefing FO prepares, their count equal to the checker's, and a mismatch returns to kc-dev-flow-2 as a wiring defect.
Supersedes: AC-7, AC-3
Design: AC-7 records the measured runs instead of a bound; AC-3 becomes a post-release check on the first paseo ui ideation, keeping its falsifier (briefing upheld-decline line count equals the checker's count).
Superseded text:
**AC-3** One real ui ideation dispatches the named agent twice, the check passes on its output, and every line it prints reaches the briefing FO prepares. Evidence: a ui ideation run on the candidate package for one of the six paseo tasks in `ideation` (the first consumer); its transcript shows two Agent calls with `subagent_type: kc-dev-flow-2:design-director` and none with `general-purpose`; `design/ideation-<N>.yaml` and `design/declines-<N>.yaml` exist; `design_surfaces.py check` exits 0 and prints the `preview:` lines, the upheld lines and the decision lines; and the briefing prepared for that ideation gate (`review/ideation/briefing-<n>/index.json` in the state checkout, in its `question` or an artifact `summary`) contains each printed `preview:`, `upheld decline <n>:` and `decision <kind>, owner` line, so the count of `upheld decline` lines in `index.json` equals the `N upheld` of the summary line. Falsifier: the same run on the base package shows `general-purpose` and no `declines-<N>.yaml`, and the base briefings of three paseo ideations (browse-vault-survives, variable-row-edit, test-results-match-draft, read 2026-10-22) hold no checker output; an FO run with the ideation workflow sentence reverted that leaves a briefing without the lines fails the last clause. A substring check of `design-review.md` is not offered as proof. Not yet verified.

**AC-7** The shipped agent, not the prototype, rules as the prototype did, and not as the control does. Evidence: run the three prompts in `replay/prompts/` (browse-vault-survives, test-results-match-draft, variable-row-edit) with `subagent_type: kc-dev-flow-2:design-director` on the candidate and `ADR folder: none`, then compare `ruling` fields with `replay/out/` and `replay/control/rulings.tsv`: of the 39 declines between 8 and 18 are upheld and at least 12 are overruled; rows #5 (variable-row-edit #4) and #10 (browse-vault-survives #1) are overruled and row #9b (#12, #13) is overruled; row #4 (#16) is a decision; every `decision` item carries a `kind` from the three values and an `owner`. The bounds are a margin around the measured 12 and 14 upheld and 14 and 15 overruled, not a measured range; run-to-run agreement was 90% on 39 declines; the run costs about 273k subagent tokens. Falsifier: the control arm already measured (23 upheld, 6 overruled, #5 a decision, #10 upheld) falls outside the bounds on four counts, and a shipped agent that upholds all or none falls outside them too. Not yet verified; the prototype result is the 15/12/12 and 14/11/14 split above.

## FO alignment

Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-22 — implementation left AC-7 met in 1 of 3 runs of the shipped agent and AC-3 and the real-flow clause of AC-13 unrunnable without a real adopter ideation; what is the smallest next step?

Captain rulings on D-1 to D-6 (ideation sitting, 2026-10-22, chat, each given to FO's question one at a time; to be bound at the ideation gate):
- D-1 「按你建議」, answering 「「整個畫面實際操作審一次」要不要變成正式的一關？」 with FO's recommendation: it belongs to the release-acceptance task as a second pass on the same operated walk, run by the design director, with a class for works but unusable; this task does not build it.
- D-2 「可以」, answering 「改成「檢查程式印出預覽圖的路徑，隨閘門資料一起給你」，可以嗎？」 (FO had corrected its earlier claim: today design_surfaces.py checks that the Preview file exists but prints only the design review report path and counts): design_surfaces.py check also prints each `Preview:` path, so the paths reach the briefing through the same workflow.md sentence that carries the upheld declines; no further workflow.md words. Override: recommended no FO rule (design D-2); Captain chose the checker printing preview paths; area: screenshots at ui gates.
- D-3 「按建議，這個再等搜集幾輪經驗」, answering 「預覽圖要不要畫出改動處周圍的整頁，桌機和手機寬度都畫？」 with FO's recommendation: not in this task; revisit after more rounds of experience.
- D-4 「可以」, answering 「照這個更正後的建議，可以嗎？」, where FO corrected its first recommendation (project learning) by kc-adr's five questions: a host-look departure ruling is the Captain's ruling on direction, so the first task where it appears lands it as an ADR in that product's repository; the design director reads the relevant ADRs before reviewing; the checker prints same-kind decision lines once per gate. Override: recommended recording it as project learning (design D-4); Captain chose an ADR per kind in the product repository; area: standing design rulings.
- Design guide 「可以」, answering 「設計指南先不做成格式，等設計類 ADR 累積起來再說，可以嗎？」 (raised by his 「這也帶來一個議題，design guide 需要變成一種 format 嗎？還是它就會是一種ADR？」): no design-guide format and no guide written as ADRs; a product's own design rulings are ADRs (D-4); revisit when a product's design ADRs grow enough that a generated index of them would help.
- D-5 「要擋下，不然找它的意義就消失了」, answering 「驗收時，如果設計總監沒有看過實際做好的畫面，要不要直接擋下？」: option A, validation refuses a ui task until a built-screen review with a screenshot that is not an ideation preview exists, or the Captain's quoted waiver.
- D-6 「可以」, answering FO's recommendation put in chat: at validation a design-director MINOR the FO would decline goes to the design director first, as at ideation; the ones it upholds are listed at the validation gate for the Captain. Override: recommended option A, MINOR defaults to Polish with a count (design D-6); Captain chose the ideation mechanism at validation; area: validation MINOR findings.

Alignment: needed at ideation; the declared model and whether the helper joins are his, after the measurement and the POC.
Result: aligned 2026-10-22 by Amendment 1 (model stays sonnet; the astra helper is dropped; dev2-poc design-helper-astra-poc closed without running) and the backlog gate resolution (duty wording, two passes, host-component declines checked, replay before shipping).

Reviewer: kc-dev-flow-2:engineering-reviewer opus 2026-10-22 — do these amendments withdraw what the Captain approved, and what changes in the build?
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Status of inputs: Amendment 1, the backlog gate resolution (the Captain's 「可以」, 2026-10-22), his rulings D-1 to D-6 and his design-guide ruling (all quoted under `## FO alignment`, 2026-10-22) are the scope. Cycle 3 folds those rulings in; D-1 to D-6 are no longer open (ruled lines under `## Unresolved decisions for the Captain`), and the folding raised one question, D-7. Cycle 2 followed `reviews/engineering-reviewer-1.md` (verdict adjust). The replay prompts treated the two host declaration files as the declaration path for every host component a decline names; they tested neither the `<Name> at <path>` rule nor the ADR-reading sentence added in cycle 3 (see Replay and AC-12). Base is origin/main cb35b82b (kc-dev-flow-2 0.28.0): since the cycle-2 base b93612f8 only the release marker line of `workflow.md`, the two plugin manifests and the changelog changed (`git diff --stat b93612f8 origin/main -- kc-dev-flow-2 docs/adr`, 2026-10-22).

### PRFAQ

**Press line.** From the next kc-dev-flow-2 release, a ui task's design review is run by a named agent, `kc-dev-flow-2:design-director`, on sonnet, which first reads the product's accepted design rulings (ADRs). The author can no longer close a finding alone: every decline the author proposes is ruled on by the design director against the picture, and the declines it upholds are printed in the gate briefing for the Captain, who keeps the final say, with the paths of the preview pictures. A question that comes up in every task (may the plugin depart from the host's look) is shown once per gate and, once the Captain rules it, lands as an ADR in the product's repository so later tasks find it ruled. At validation the same agent looks at screenshots of the built screen, validation refuses a ui task until that review exists or the Captain waives it in quoted words, and the MINOR findings the validator would decline are ruled on the same way and listed at the validation gate.

**FAQ.**

- *Would this have caught the complaint that started it?* No. The Captain's Browse complaint (critique row 1, 「我按 broswe 沒料到…」) was a MINOR finding the author declined as "today's behaviour"; the director upholds that decline in both wording runs and in the control arm. Of the four critique rows graded blocking (1 to 4), none reaches a fix on its own finding under this design: row 1 stays closed, row 2 gets a fix for a different part of the finding, row 3 needed a running app, row 4 becomes a decision whose owner is the task the author already named. What the design changes is the class "the host component has no X" (rows 5, 10 and, for the buttons, 9b); the whole-screen class is release-acceptance's (ruled, D-1).
- *Why a named agent, when ADR 0022 chose a `general-purpose` agent and rejected "a new agent"?* ADR 0022 says "Reopen if a bite recurs that the review did not name". The 2026-10-22 measurement is not literally that bite (the review named 10 of the 14 critique findings); the loss is in the disposition: on 7 kc-paseo-plugins tasks the review raised 93 findings and the author declined 70. The Captain asked for the role in 「我還是希望開設計總監…」 and ruled 「設計總監照建議」 (Amendment 1). A new ADR records this (below), with a one-line pointer in ADR 0022.
- *Why sonnet?* Amendment 1 point 1; ADR 0022 D3 measured no gain from opus; every replay arm ran on sonnet and AC-7 reruns the shipped agent on sonnet.
- *Does the director gain authority?* No. It advises and holds no gate. What changes is who may close a finding: not the author alone. An overruled finding leaves three exits (fix, criterion, or a Needs decision that reaches the Captain with both views), so the Captain's final say is intact.
- *What does it not do?* It does not review whole releases or operate a running app at ideation (ruled: release-acceptance owns it, D-1), and it changes neither the eight dimensions nor the severities (Scope non-goal).
- *First consumer.* The six kc-paseo-plugins tasks now in `ideation` (`project-env-add-variable-one-step`, `-connection-collapse`, `-draft-survives-remount`, `-field-picker-grouped`, `-save-footer-danger-zone`, `-test-summary-failure-mark`) run their next ui design review, and any rework, through it.

- *Where does the whole-screen operated review live, and is there a design guide?* The review is release-acceptance's second pass over its operated walk (its Amendment 1, ruled D-1); this task builds none of it. There is no design-guide format: a product's own design rulings are ADRs (ruled), and a generated index waits until they accumulate.

```mermaid
sequenceDiagram
    participant A as Author (ideation worker)
    participant D as Design director (sonnet agent)
    participant R as Product repo ADRs (kc-adr:read-adr)
    participant C as design_surfaces.py check
    participant F as FO
    participant K as Captain
    participant V as Validator
    A->>D: pass 1a: brief, UI proposal, previews, ADR folder
    D->>R: kc-adr:read-adr on the ADR folder, rely on records in force
    D-->>A: design_review report (findings, limitations)
    A->>A: write dispositions; propose declines
    A->>D: pass 1b: findings, proposed declines, cited pictures, host declarations, ADR folder
    D-->>A: design_decline_check report (adrs_read; upheld, overruled, decision with kind and owner)
    A->>A: overruled becomes fixed, AC or Needs decision; decision becomes Needs decision (host-look names an ADR title)
    A->>C: run check at ideation
    C-->>F: Preview paths, one line per upheld decline, decisions grouped by kind and owner
    F->>K: gate briefing carrying every line, at any exit
    K-->>F: approve, or overrule any listed decline
    V->>D: pass 2: built-screen screenshots, the criteria that name the running screen, ADR folder
    D-->>V: design_review report
    V->>D: pass 2b: every MINOR the validator proposes to decline
    D-->>V: design_decline_check report
    V->>C: run check at validation (refuses with no built-screen review, or no ruling)
    F->>C: run check before the validation gate
    C-->>F: built-screen picture path, one line per upheld built-screen decline, decision groups
    F->>K: validation gate material carrying every line
```

### What changes

| Part | Change |
| --- | --- |
| `kc-dev-flow-2/agents/design-director.md` (new) | Wrapper like `observer.md`: `model: sonnet`, `reasoning: high` (the observer's pair; no measurement chose between high and another level), `skills: ["kc-dev-flow-2:design-director"]`. Adds no policy. |
| `kc-dev-flow-2/skills/design-director/SKILL.md` (new) | `Invocation: kc-dev-flow-2:design-director`. Holds the duty wording, the two passes with their decline check, reading the ADR folder, the three rulings and their `kind`, `owner` and `adr` fields, the return shapes, the boundaries. |
| `kc-dev-flow-2/skills/design-director/review-brief.md` (new) | The brief moved verbatim from `design-review.md` (eight dimensions, MAJOR/MINOR). Every pass reads it; at validation "previews of a user interface that is not built yet" reads "screenshots of the built screen". |
| `kc-dev-flow-2/skills/ideation/design-review.md` | Step 1 dispatches `kc-dev-flow-2:design-director` and names `ADR folder:`; new step for the decline check; a `host-look` decision names an ADR title; hand-forward rule. The brief block is removed (moved). |
| `kc-dev-flow-2/scripts/design_surfaces.py`, `test_design_surfaces.py` | At ideation: the decline check, `preview:` path lines, decision lines grouped by kind and owner. At validation: the built-screen review (D-5, ruled), per-finding lines and the decline check for MINOR (D-6, ruled). Details below. |
| `kc-dev-flow-2/references/sd/workflow.md` | Two sentences, +15 words in all (text under "Words FO reads"): the ideation Gate content sentence includes the checker's output at any exit; the validation Gate content gains one sentence that runs the same check for a `ui` task and includes its output. |
| `kc-dev-flow-2/scripts/lint-skills.py`, `test_lint_skills.py` | `AGENT_MODELS` gains `"design-director": ("sonnet", "high")` with a test like `test_observer_keeps_its_declared_model`; `WORKFLOW_BUDGET_STEPS` gains one raise step (delta 15) as ADR 0020 requires: its `captain` value is the Captain's approval words at this task's ideation gate, and its `loaded` value names the moments FO reads `workflow.md` (startup and resume, the ideation and validation gate prepare). The step cannot be written without those words, because no earlier ruling named a `workflow.md` raise (D-2 said none for the preview paths; D-6's 「可以」 answered a question that named no words). |
| `kc-dev-flow-2/skills/validation/principles.md` | The screenshot sentence names the director pass, its lines and the MINOR decline check. |
| `kc-dev-flow-2/README.md` | One sentence in the roles paragraph (retained document: the role would otherwise be undocumented). |
| `docs/adr/<reserved>-<short title>.md` (new) and `docs/adr/0022-ui-ideation-design-review-binds-design.md` | A new ADR records the decision (draft below; the number is reserved by FO at the implementation dispatch under `## Number guards`, so the draft carries none). ADR 0022 gains one pointer line naming it. |

Not changed: `role_triggers.py` (the director is not a `Reviewer:` call), `pr_watch.py`, `delivery_gate.py`, `skills/ideation/principles.md`, the mod, any extension. `references/sd/workflow.md` changes in the two sentences above and nowhere else. No design-guide format and no release-level whole-screen review are built (ruled; see below).

### Duty wording (as it will stand in `SKILL.md`; the part marked * is new in cycle 3)

> You are the design director for one task's ui surface. You own its open design decisions: every finding on the screen ends as a fix, an acceptance criterion, or a decision that has a named owner, and no finding is closed by a reason you have not checked against the picture it concerns.
>
> Decline check. The author may propose to decline a MINOR finding. You check every proposed decline against the picture the finding cites, and rule exactly one of: **upheld** (the picture shows the reason holds, and a person using the screen is not misled, blocked or put at risk by leaving it); **overruled** (the picture still shows what the finding saw, or the reason does not answer it; say the fix, or the criterion that would test it); **decision** (the finding is real, but changing it departs from a host component, another task's work or a recorded ruling; name who decides).
>
> A decline that rests on a host component names the component and the path of its declaration (`declined: host component <Name> at <path>: <reason>`); with no path you rule decision, never upheld. You check it against that declaration, not the author's description. "The component has no X" stands only when the declaration has no prop, slot or children that can supply X and the plugin's own parts cannot either; name the prop or slot you looked for. When the declaration offers a way, the decline is overruled; when only a custom build is possible, it is a decision whose owner is whoever accepts a departure from the host's look.
>
> A decline that rests on another task, a release, a non-goal or "as today" stands only when the picture shows nothing a person would act on wrongly in the meantime. Otherwise it is a decision, and the owner is the task or record cited.
>
> \* Before you review, invoke `kc-adr:read-adr` on the ADR folder the dispatch names (`ADR folder: <path>`, or `none`) and open the records whose titles bear on how the screen looks or on host components. List what you opened in `adrs_read`, each with the Status that skill reports; rely only on the record that skill finds in force. A question a record in force already settles is not a decision: rule it by the record and write `adr: <path>`. If the skill is not available, write `adrs_read: unavailable` and treat no question as settled by a record. A decision names its `kind` (`host-look` when only a custom build departs from the host's look; `other-task` when another task owns the change; `recorded-ruling` when a recorded ruling or non-goal does) and its `owner` (`Captain` for host-look, the task or record for the others).
>
> You advise and hold no gate. The Captain keeps the final say: the declines you uphold are listed for him at the gate.

The starred paragraph carries the Captain's D-4 and mirrors the FO Precedent rule ("a decision an accepted ADR already settles is not asked again", `references/sd/workflow.md`); how a record is read and judged in force is `kc-adr:read-adr`'s (`kc-adr/skills/read-adr/SKILL.md`), not restated here. Upstream check, 2026-10-22: `git grep -n -i 'kc-adr\|read-adr' origin/main -- kc-dev-flow-2` finds no reference, so this is the first kc-dev-flow-2 use of that skill; the agent may run where kc-adr is not installed, which is why the unavailable branch exists. The paragraph was not in the replay's `replay/duty.md`; AC-12 runs it.

Two passes, one agent, each with the same decline check:

- **Pass 1 (ideation), two dispatches.** 1a is today's blind review (previews and UI proposal only, brief unchanged) plus the ADR folder. 1b is the decline check; it adds the findings, the author's proposed declines, the pictures they cite and the declaration files named in `host component … at <path>` lines. It reads no task file and no code. This relaxes ADR 0022's "reads no other file" for the ADR folder and for the named 1b inputs only.
- **Pass 2 (validation), two dispatches.** 2a: screenshots of the built screen at the candidate, plus the criteria whose text names the running screen, plus the ADR folder; the report has the shape of 1a, and what the screenshots cannot settle goes in `limitations` (the validator carries each as unverified or checks it with run evidence). 2b: the validator sends every MINOR it proposes to decline, with its reason and the screenshot the finding cites, and the director rules each as at 1b.
- **Hand-forward.** A pass-1 `limitations` entry that only the running screen can settle (a resize, a real vault, a Test run) becomes an acceptance criterion that names the running screen. This extends the existing step 3 of `design-review.md`; nothing mechanical ties a limitation to a criterion, so that link is by instruction only.
- **Where an ADR comes from.** `ADR folder:` in the dispatch is the product's workflow README `adr-path:` (default `docs/adr`) under the product repository root, the key Number guards already read; no new convention is coined. When a `decision` of kind `host-look` is not settled by an Accepted record, the author's `Needs decision:` line ends `ADR: <short title>` (the existing rule that a design names an ADR by ruling and short title, no number); the Captain's ruling at the gate is then landed by FO's existing decision-records step. Before that ADR is Accepted, tasks in flight each name the same question; FO points the later ones at the first draft's title. The check cannot see across tasks.

### Ideation records and the check

New line in `## Design` › `### Design review`: `Decline check: design/declines-<N>.yaml`, one per run, naming the saved report. Report shape: `design_decline_check:` with `adrs_read:` (each path with the Status `kc-adr:read-adr` reports, or `none` or `unavailable`) and `rulings:`, each item `finding`, `ruling` (`upheld`, `overruled` or `decision`), `evidence`, `change`; a `decision` item also carries `kind` (`host-look`, `other-task` or `recorded-ruling`) and `owner`; an item an Accepted record settled carries `adr: <path>`. The check reads by line pattern, like the existing report checks, because model output carries unquoted colons (6 of the 9 paseo reports fail YAML parsing).

`check_design_review` gains these refusals (each its own test, each with a mutation):

1. A `Design finding n: declined:` line and no `Decline check:` line → refused. More than one `Decline check:` line → refused.
2. A declined finding with no ruling in the report, or a ruling for a finding that is not declined → refused.
3. A declined finding whose ruling is `overruled` or `decision` → refused; it must be `fixed:`, `AC-<id>` or `Needs decision:`. A `decision` ruling needs a `Needs decision:` line.
4. A reason that begins `host component` without `<Name> at <path>:` → refused. The form is checked; whether the path is the right declaration is the director's ruling. A host decline written without the marker is not detectable by script, so the claim is bounded: the check enforces the form where the author writes it, and the director is told to rule `decision` on any decline that names a host component with no path.
5. A `decision` ruling without a `kind` from the three values, or without an `owner`, → refused (D-4: the grouping below needs both).
6. A `Needs decision:` line for a `host-look` decision that does not end `ADR: <short title>` → refused (D-4: the ruling lands as an ADR). The check enforces the title is written, not that an ADR is later landed; that is FO's existing decision-records step.

Output, in the order the gate material needs it:

- the summary line gains `; decline check design/declines-1.yaml: 6 upheld, 3 overruled, 11 decisions in 4 groups`;
- one line per `Preview:` value of the task, `preview: <path>` (D-2): a file value resolved against the task folder as the existing `Preview does not exist` test resolves it, a URL as written;
- each upheld decline prints one line `upheld decline <n>: <reason as written>`;
- decisions print once per group of equal `kind` and `owner` (owner compared trimmed and case-folded): `decision <kind>, owner <owner> (findings 3, 11): <the first item's change>` (D-4). Grouping is per task file, which is what a gate is; the repeat across gates is what the ADR removes.

Replay arithmetic for the grouping (`replay/out/*.yaml`, kind read by me from each `change` text, so approximate): the 18 `decision` rulings of the 7 tasks print as 15 lines; 9 of the 18 are `host-look` with owner Captain, in 6 of the 7 tasks, so before an ADR exists those 6 gates each carry the question once, and after it each carries none.

Why the workflow.md sentence is needed (cycle 2). The ideation stage text says "a non-zero exit means the gate is not presentable, and FO includes the checker's output in the gate material"; the clause rides on the non-zero case. Read 2026-10-22 on the paseo state checkout (read-only): the ideation `briefing-1/index.json` of three archived tasks (project-env-browse-vault-survives, project-env-variable-row-edit, project-env-test-results-match-draft) each hold a 77-character question and a one-sentence artifact summary ("r1.5 ideation design for <task>; design, acceptance criteria and stage report in the task file"), with no check output and no mention of the design review. An exit-0 line list would stay out of the briefing the same way, so the promise "listed for him at the design gate" would fail silently. Read the same way, the `validation/briefing-1/index.json` of the same three tasks hold a 66, 66 and 313 character question and a one-paragraph summary that names FO's rerun of the acceptance script and, in one task, one FO decline in a sentence; none carries a check output. That is why the validation Gate content needs its own clause (D-6). AC-3 tests the briefing itself.

A report is model output saved by the author: the check cannot tell it came from the named agent (same limit ADR 0022 records for the review report).

At validation (D-5 and D-6, both ruled). At `status: validation`, a `Surfaces:` including `ui` and a `Design review:` line in the body (so tasks ideated before the review existed are not caught), the check requires:

- **A built-screen review (D-5, option A).** A `Built screen review:` line in the body or the stage report. Form 1: `Built screen review: design/validation-<N>.yaml`, naming a report with the `design_review:` shape whose `preview:` value names a file that (a) exists in the task folder, (b) is not a file named by, or inside a directory named by, any `Preview:` line, and (c) differs in sha256 from every file under those paths. Clauses (b) and (c) close the hole that an ideation picture already in the task folder satisfies the check. Form 2: `Built screen review: waived 「<the Captain's words>」`, checked for a quoted span only (as ADR 0020 checks a raise). A missing line, a missing or ideation-identical file, or a waiver with no quote is refused with `built screen review not run`. The check proves a present file that is not an ideation picture; it cannot prove the picture shows the built screen at the candidate (a validator could save any other picture), so the validation reviewer compares the picture to the candidate by the run evidence already required.
- **A disposition for every finding of that report (D-6).** One line `Built screen finding <n>: <disposition>` per finding, in report order. A MAJOR is `F<N>`, naming a `- F<N> <Class>:` bullet of the validator's report (the existing four classes; the check confirms the bullet exists, not its class). A MINOR is `declined: <reason>` or `Needs decision: <text>`. A report with a `declined:` line needs one `Built screen decline check: design/validation-declines-<N>.yaml` line naming a `design_decline_check:` report, and the refusals 2 to 5 above apply to it with the finding lines renamed; an `overruled` or `decision` ruling cannot stay `declined:`, it becomes `Needs decision:`, and that is the Captain's to settle at the validation gate (D-7).
- **Output.** The summary line gains `; built screen review design/validation-1.yaml: 12 findings, 9 upheld declines, 2 decisions in 1 group`; `preview: <path>` of the built-screen picture (the D-2 line, for the screen the Captain would open at this gate); `upheld built-screen decline <n>: <reason>`; decision groups as at ideation.

The validator proposes the declines because FO's decline of Polish comes after validation and no check sees FO's gate summary: a MINOR that carries a `declined:` line without an upheld ruling is refused, and a MINOR that FO declines after the stage ends, on its own, is outside the check. That is a bounded claim: the check enforces a ruling on every decline the validator writes and a disposition on every finding; it cannot stop a later FO decline that cites no ruling.

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

Load. At the ideation gate the Captain's list would have been 21 upheld lines over 7 tasks (1 to 6 per task) and 18 decisions (already Needs-decision lines today), and the authors would have owed 31 fixes or criteria they did not owe. That is the price; AC-7 bounds it. Nine of the 18 decisions are the same question, so D-4 (ruled) turns it into one ADR in the product's repository.

### Words FO reads at each lifecycle moment

Counted with `wc -w` on `origin/main` cb35b82b (kc-dev-flow-2 0.28.0). `references/sd/workflow.md` is 5374 words there and at the cycle-2 base b93612f8: the 0.28.0 release changed only its marker comment line (`git diff b93612f8 origin/main -- kc-dev-flow-2/references/sd/workflow.md`, 2026-10-22). Same count method for the candidate; each moment needs the candidate count recomputed at validation.

Candidate text, measured 2026-10-22 by applying both edits to a copy of the base file: the ideation Gate content sentence "…FO runs `python3 <package>/scripts/design_surfaces.py check <task>`; a non-zero exit means the gate is not presentable, and FO includes the checker's output in the gate material." becomes "…FO runs `python3 <package>/scripts/design_surfaces.py check <task>`, includes its output in the gate material at any exit, and treats a non-zero exit as the gate not presentable." (+1 word); and the validation Gate content, after "…and the user's pending delivery decision.", gains "For a `ui` task FO runs `python3 <package>/scripts/design_surfaces.py check <task>` and includes its output." (+14 words). The copy counts 5389 under `wc -w` (+15). `lint-skills.py` on an `origin/main` extract with that copy printed one workflow error, "5389 words exceeds the budget of 5374", and no duplicate-run error against any other skill or reference file.

| Moment | Base (words) | Candidate | Basis |
| --- | --- | --- | --- |
| startup and resume (`references/sd/workflow.md`) | 5374 | 5389 (+15) | measured on the edited copy as above; AC-8 recounts the candidate |
| idle on an open PR / idle on a merged PR / after the archive / the merge ask | `workflow.md` text read at startup, plus the moment's own text | +15 from `workflow.md`, nothing else | `pr_watch.py`, `delivery_gate.py` not edited; `pr_watch.py` runs `check --seed`, which returns before the ui checks |
| ideation gate prepare, ui task (checker output) | 13 measured on two archived paseo tasks, plus the design-review summary line (14 words by the test fixture's form); none of it reaches the briefing (3 archived paseo briefings) | + decline-check summary (about 13 words) + one `preview:` line per Preview (about 2 words each) + one line per upheld decline (**30 to 141 words per task, median 60**, simulated from the author's decline text for the 7 tasks, 529 words over 21 lines) + decision lines (**17 to 143 words per task, median 42**, 387 words over 15 lines, simulated from `replay/out/*.yaml`); all of it now carried into the briefing | simulation, not a run of the new check; AC-3 and AC-8 report the real count |
| validation gate prepare, ui task | 13 (no design lines at that status); the validation summary and acceptance script unchanged | + one summary line (about 15 words) + one `preview:` line (about 2 words) + one line per upheld built-screen decline + decision lines | design; pass 2 has no measurement, so no per-task range is given (the pass-1 average was 12 MINOR per task); AC-8 reports the real count if a consumer reaches validation |

Binding of the raise. FO's ideation gate question for this task names it: "approving adds 15 words to `workflow.md` (ideation +1, validation +14; cycle 2 said +10) and accepts the recommendation for D-7; say if you object". His reply to that question is the `captain` value at implementation; without it, implementation holds rather than writing the step.

The ideation and validation gates rise, by design: Amendment 1 and D-6 ask for the lists at the gates. The learning "each moment below its base" applies to a change whose goal is to cut what FO reads; this one adds a Captain-owed list and 15 words at the moments that read `workflow.md`, and leaves the other text FO reads at the idle and merge moments unchanged. ADR 0022 recorded "13 more words at the ideation gate of a ui task"; the new ADR replaces that number.

### ADR draft (no number; FO reserves one at the implementation dispatch)

File `docs/adr/<reserved>-a-ui-design-review-is-run-by-a-named-director-and-a-decline-needs-its-ruling.md`:

> # <reserved>. A ui design review is run by a named director, and a declined finding is closed only by its upheld ruling
>
> ## Status — Proposed
>
> ## Context — The 2026-10-22 measurement on 7 kc-paseo-plugins tasks: 93 findings, 70 declined by the author (37 citing a host component), 10 of the 14 findings of a later critique already raised and declined at MINOR, 4 of 7 validations without a screenshot of the candidate. ADR 0022 chose a `general-purpose` agent and a worker who dispositions its own findings. A replay of 70 declines with a second sonnet check overruled 31; the same check on 39 of them without the duty wording overruled 6 and upheld 23. The Captain's own Browse complaint stays declined under every arm.
>
> ## Decision — **Words:** 「我還是希望開設計總監，讓它來做目前指示的內容…」 (chat, 2026-10-22), 「可以」 (backlog gate, 2026-10-22), 「設計總監照建議」 (chat, 2026-10-22), 「要擋下，不然找它的意義就消失了」 (D-5, 2026-10-22), 「可以」 (D-6, 2026-10-22), 「可以」 (D-4, 2026-10-22), and the ideation-gate approval words FO adds. **Options considered:** the named `design-director` agent on sonnet rules each proposed decline, reads the product's accepted ADRs first, and the upheld ones are listed for the Captain (chosen); keep the `general-purpose` agent and the author's own dispositions — not chosen, it is the measured loss; a second sonnet check with the declarations but without the duty wording — not chosen, it upholds 23 of 39 where the wording upholds 12 to 14; opus — not chosen, ADR 0022 D3 measured no gain and the measurement shows no evidence the model is the problem; a gpt-6-astra helper — dropped by the Captain, Amendment 1; a design-guide format, or a guide written as ADRs — not chosen, a product's own design rulings are ADRs and a generated index waits until they accumulate; project learning for a standing host-look ruling — not chosen, a ruling on direction is an ADR in the product's repository; a release-level operated whole-screen review in this task — not chosen, release-acceptance owns it. **Recommended:** the first option, as the Captain's 「設計總監照建議」 accepted; a host-look departure the Captain rules lands as an ADR in the product's repository at its first appearance; validation refuses a ui task with no built-screen review unless the Captain waives it in quoted words; at validation the same ruling applies to the MINOR findings the validator proposes to decline.
>
> ## Consequences — Each ui ideation costs a second director run (77k to 115k tokens per task on the replay) and the Captain reads the upheld lines and decision groups at the gate (30 to 141 and 17 to 143 words per task, simulated). Each ui validation costs a pass-2 run and, with MINOR findings, a decline-check run (not measured). The check proves a ruling exists and its form, not that the agent that wrote the report was the named one, nor that an upheld decline is right, nor that a later FO decline cites a ruling. A stall is possible where a validator cannot produce a screenshot of the built screen; the Captain's waiver or an environment fix ends it. The whole-screen operated review is release-acceptance's. Reopen if a decline the director upheld is later found wrong at a gate or a critique.

ADR 0022 gains one line after its Consequences: `Amended 2026-10-22: the review is run by the named design-director agent and a declined finding needs its ruling; see ADR <reserved>.`

### Batch overlap

Files this design changes: `kc-dev-flow-2/agents/design-director.md`, `kc-dev-flow-2/skills/design-director/SKILL.md` and `review-brief.md` (all new); `skills/ideation/design-review.md`; `skills/validation/principles.md`; `scripts/design_surfaces.py` and `test_design_surfaces.py`; `scripts/lint-skills.py` and `test_lint_skills.py`; `references/sd/workflow.md` (two sentences); `kc-dev-flow-2/README.md`; `docs/adr/` (one new record, number reserved at implementation) and `docs/adr/0022-ui-ideation-design-review-binds-design.md` (one line). Read 2026-10-22 from the task files in this state checkout at HEAD ef331cd0, at origin/main cb35b82b, and from the PR lists in their own overlap tables; every task named in the checklist has a readable file, in the checkout or its `_archive/`. Since cycle 2: release-acceptance moved to implementation; the others kept their stage.

| Other task | Same file or check | Order |
| --- | --- | --- |
| fo-write-checks-parse-top-level (batch 5, ideation) | yes: `design_surfaces.py` (`scope_lines`, `check_criteria`, one docstring clause) and `test_design_surfaces.py` (`ScopeCheckTests`); mine adds functions near `check_design_review`, a validation branch and preview/decision lines in `check_task`, and edits no docstring. Its AC-6 lists exactly four changed files and "the same word budget": if mine merges first, its base moves by the +15 step | different functions; second to merge rebases; either order |
| release-acceptance (implementation, no PR yet; Amendment 1 there takes the whole-screen pass, ruled D-1) | yes: `references/sd/workflow.md` (its AC-3 replaces "no script checks that line" in the Release review bullet; mine are the ideation and validation Gate content sentences) and, if it adds words, the `WORKFLOW_BUDGET_STEPS` list; its README edit is a different paragraph; it runs `lint-skills.py` | different passages; if both add words the later PR recounts and adds its own step (ADR 0020 Consequences) |
| new-work-starts-from-a-story-map (batch 5, validation, PR #705) | no: `references/sd/workflow.md` and `lint-skills.py`'s budget are unchanged by it (its AC-10 diffs both against its merge-base for nothing); it reserves ADR 0029; it edits `skills/ideation/principles.md`, which this design leaves alone | none; my ADR takes the next free number, so reserve after it merges or is released |
| merge-ask-holds-missing-clauses (batch 5, validation, PR #703) | no: `delivery_gate.py`, ADR 0023 and 0026; it adds no ADR number | none |
| codex-reader-counts-code-review-only (batch 5, validation, PR #702) | none: `extensions/codex/`; it reads `README.md`, edits no line of it | none |
| comment-check-reaches-delivery-gate (ideation, resolved `hold`) | would add one sentence (+16 words) to `skills/validation/principles.md`; mine replaces the screenshot sentence of the same file; it adds no `workflow.md` edit and no budget step | adjacent hunks; second rebases |
| codex-reader-reads-receipt-marker (merged #693), idle-names-failing-seeds (merged #694), agent-reads-governing-adr (archived done), kc-decision-log-cli (archived done) | none: `extensions/codex/`, `pr_watch.py` (#694, already in the base), `AGENTS.md`, `scripts/adr-path-check.py` | none |
| override-reaches-gate-and-criteria-wait, amendment-form-check-round3-followups (backlog) | `design_surfaces.py` `check_amendments` | different function; order only if pulled forward |
| design-surfaces-task-dir-crash (backlog) | `design_surfaces.py` `main` and task-dir handling; my new checks resolve the report folder with the same helper as `check_design_review` | if it lands first, mine follows its folder handling |
| journey-server-host-pilot (validation, other session), kc-decision-log-p1 (archived backlog), kc-decision-log-handoff-trial (backlog), pr-review-lite-value-pilot (implementation), journey-canvas-hosted-poc (ideation), read-adr-reporting-rule-followup (archived done) | none edits these files: `grep -c` of each task file for `design-review.md`, `lint-skills`, `sd/workflow.md`, `validation/principles`, `kc-dev-flow-2/agents`, `kc-dev-flow-2/README` found none that edits them (journey-server-host-pilot and journey-canvas-hosted-poc only record runs of `design_surfaces.py check`). Only the check's verdict could change, and only for a task whose `Surfaces:` include `ui` with a `Design review:` line | none |
| ADR directory | new record at the next free number after 0029 (new-work-starts-from-a-story-map); amends 0022 by one line; merge-ask amends 0023 and 0026 | none |

Recommended order: no hard constraint. If fo-write-checks-parse-top-level merges first, rebase this task's `design_surfaces.py` hunks onto it; release as one `feat(kc-dev-flow-2)` PR with the agent, skill, checks and the two workflow sentences together, because the check refuses declines without the report the skill now asks for.

## Acceptance criteria

**AC-1** The agent exists, declares sonnet, and is bound to its skill. Evidence: at the candidate, `python3 <package>/scripts/lint-skills.py` exits 0 with `design-director` in `AGENT_MODELS`, and `python3 -B -m unittest test_lint_skills` (run in `<package>/scripts`) passes a new case. Falsifier: that case changes `model: sonnet` to `model: inherit` in `agents/design-director.md` and expects "design-director agent: existing sonnet/high policy changed"; deleting `skills/design-director/SKILL.md` must give "missing skills: design-director". Not yet verified.

**AC-2** The brief moves with its eight dimensions and two severities unchanged. Evidence: the blockquote in `origin/main:kc-dev-flow-2/skills/ideation/design-review.md` and the blockquote in `skills/design-director/review-brief.md` compared with `diff` differ only in the one sentence that names screenshots for pass 2, and `design-review.md` no longer carries the blockquote. Falsifier: editing one word of one dimension makes `diff` print it. Not yet verified.


**AC-4** A declined finding passes only with an `upheld` ruling, and a decision carries what the grouping needs. Evidence: new cases in `test_design_surfaces.py`, one per refusal 1 to 6 above (no `Decline check:` line; missing ruling; ruling for an undeclined finding; `overruled` or `decision` still declined; `host component` with no `<Name> at <path>:`; `decision` with a `kind` outside the three values or no `owner`; a `host-look` `Needs decision:` line with no `ADR: <title>`; two `Decline check:` lines), each asserting the refusal's reason text, plus one passing case. Falsifier: for each refusal, a `mutated(...)` copy of the check with that branch removed makes its case fail (the file's existing mutation pattern); the suite also fails if a case asserts only the exit code. Not yet verified.

**AC-5** The gate material lists every upheld decline, not a count. Evidence: a case with 3 declined findings (2 upheld, 1 overruled, the overruled one redisposed to `fixed:`) asserts the output holds exactly two `upheld decline <n>: <reason>` lines with the author's reasons, and that the summary line counts `2 upheld, 1 overruled, 0 decisions in 0 groups`. Falsifier: a mutant that prints only the count fails the case. Not yet verified.

**AC-6** (D-5 ruled, option A) A ui task cannot reach a passing validation check without a built-screen review or a quoted waiver. Evidence: cases at `status: validation` for a task with `Surfaces: ui` and a `Design review:` line: no `Built screen review:` line is refused with "built screen review not run"; a line naming a report whose `preview:` file is absent from the task folder is refused; a line naming a report whose `preview:` file is a byte-copy of a file under a `Preview:` path (an ideation picture) is refused; a line with a present screenshot of different bytes passes; `waived` with a 「…」 quote passes and `waived` without one is refused; a task with no `Design review:` line (ideated before the review) is not refused; `status: implementation` is not refused. Falsifier: mutants that drop the status gate, the file-exists test, the byte comparison against the `Preview:` files, the quote test or the `Design review:` condition each fail a case. Limit stated in the report: the check cannot tell that a different file shows the built screen. Not yet verified.


**AC-8** FO-read text changes only where this design says. Evidence: `git diff <base> <candidate> --stat -- kc-dev-flow-2/scripts/pr_watch.py kc-dev-flow-2/scripts/delivery_gate.py kc-dev-flow-2/scripts/role_triggers.py` prints nothing; `git diff <base> <candidate> -- kc-dev-flow-2/references/sd/workflow.md` is two hunks, one in the ideation Gate content and one in the validation Gate content; `wc -w` of `workflow.md` at the candidate is 5389; `lint-skills.py` passes with exactly one added `WORKFLOW_BUDGET_STEPS` entry (delta 15, a quoted `captain` value, a `loaded` value). The ideation-gate and validation-gate counts in the table above are recomputed from a real run of the candidate check and reported next to the simulated ones. Verified now in part: the edited copy counts 5389 and `lint-skills.py` on it printed only the budget error (2026-10-22). Falsifier: any other edit to those files, a missing `captain` or `loaded` value, or a lint budget error. The rest is not yet verified.

**AC-9** The retained documents match the new role. Evidence: `README.md` names the role, its model and that it advises; a new ADR file at the number FO reserved carries `**Words:**`, `**Options considered:**` and `**Recommended:**` lines and the Captain's quoted words; `python3 <package>/scripts/adr_lint.py docs/adr --since <base> --require <reserved>` exits 0; ADR 0022 carries one line naming that number (checked by a grep in the validation report; no tool parses it); `python3 <package>/scripts/doc_impact.py <base> <candidate>` reports no unread affected document. Falsifier: removing the `**Options considered:**` line from the new record makes `adr_lint.py` exit 1 with "Decision needs a '**Options considered:**' line" (run 2026-10-22 on a fixture of origin/main b93612f). Not yet verified.

**AC-10** (D-2) The check prints each `Preview:` path. Evidence: a case with a task whose `Preview:` lines name one existing file and one URL asserts the output holds `preview: <resolved path of the file>` and `preview: <the URL as written>`; AC-3 shows the lines in the briefing. Falsifier: a mutant that prints no preview line fails the case; a mutant that prints the value unresolved fails an assertion on the resolved path. Not yet verified.

**AC-11** (D-4) Decisions of the same kind and owner print once. Evidence: a case with 4 `decision` rulings (two `host-look` with owner Captain, one `host-look` with another owner, one `other-task`) asserts 3 `decision` lines, the first naming findings of both Captain items, and the summary `4 decisions in 3 groups`. Falsifier: a mutant printing one line per ruling fails the count; a mutant grouping by `kind` alone fails the case with two owners. Not yet verified.

**AC-12** (D-4) The shipped agent reads the ADR folder through `kc-adr:read-adr` and relies only on a record in force. Evidence: run the `replay/prompts/plain-failure-reason` prompt (its finding 11, "own 44px buttons", was ruled `decision`, which I read as kind `host-look`, in the replay) with `subagent_type: kc-dev-flow-2:design-director` three times on the candidate, on a machine where kc-adr is installed, with the `ADR folder:` in a scratch folder outside the repository: (a) it holds one `Accepted` record that accepts plugin-drawn 44px phone buttons; (b) it holds the same record with Status `Proposed`; (c) `ADR folder: none`. Expected: in (a) finding 11 is not `decision`, its item carries `adr:` naming that file and `adrs_read` lists it as `Accepted`; in (b) and (c) it is `decision` with kind `host-look` and owner `Captain`, and in (b) `adrs_read` lists the record as `Proposed`; the transcript of (a) shows the `kc-adr:read-adr` skill loaded. About three director runs. Falsifier: a shipped agent that ignores the folder gives `decision` in (a); one that relies on a `Proposed` record gives a non-decision in (b). A run where the skill is absent must print `adrs_read: unavailable` and rule `decision`; that branch is run once by hiding the skill. Not yet verified; the sentence was not in the replay.

**AC-13** (D-6) A MINOR the validator would decline is ruled before it is declined, and every finding has a disposition. Evidence: cases at `status: validation` with a built-screen report of 3 findings (one MAJOR, two MINOR): a MINOR `declined:` with no `Built screen decline check:` line is refused; a ruling `overruled` or `decision` on a `declined:` line is refused until the line reads `Needs decision:`; a finding with no `Built screen finding <n>:` line is refused; a MAJOR line `F<N>` naming no `- F<N> ` bullet is refused; the passing case prints `upheld built-screen decline <n>:` once per upheld ruling and a `preview:` line for the screenshot; `status: implementation` is not refused. Falsifier: a mutant per branch (decline-check line, ruling test, disposition test, bullet test, line printing) fails its case. Real-flow evidence: when a paseo consumer reaches validation on the candidate package, its validator's transcript shows the pass-2 and decline-check Agent calls with `kc-dev-flow-2:design-director` and the validation briefing carries each `upheld built-screen decline` line; if none reaches validation before this task's validation, that clause is reported as not run and the wiring is proven only by the AC-3 mechanism on the ideation sentence. Limit: the check cannot see a decline FO writes after the stage. Not yet verified.

**AC-14** (Amended by Captain, amendment 2; replaces AC-7) The measured runs of the shipped agent on the replay prompts are recorded with no pass bound: on the final wording both runs overruled more declines than the no-wording control (12 and 9 against 6) and upheld fewer (13 and 18 against 23), and one run missed the original bounds.

**AC-15** (Amended by Captain, amendment 2; replaces AC-3) At the first kc-paseo-plugins ui ideation after release, the upheld-decline lines appear in the briefing FO prepares, their count equal to the checker's; a mismatch returns to kc-dev-flow-2 as a wiring defect. Falsifier: the briefing's upheld-decline line count equals the checker's count.

## Unresolved decisions for the Captain

### Ruled by the Captain (2026-10-22; his words and FO's question are quoted under `## FO alignment`)

- D-1 ruled: the operated whole-screen design pass belongs to release-acceptance, whose Amendment 1 (2026-10-22, "Design: the release walk gains a second pass over the same operated walk, run by the design director") records it; this task builds none of it and adds no browser instruction to the director. In the design: PRFAQ, FAQ, "Not changed".
- D-2 ruled: `design_surfaces.py check` also prints each `Preview:` path, so the paths reach the briefing through the ideation Gate content sentence that carries the upheld declines; no `workflow.md` words are added for it. In the design: "Ideation records and the check" output list; AC-10.
- D-3 ruled: not in this task; revisit after more rounds of experience. Nothing in the design draws whole-page previews.
- D-4 ruled: a host-look departure ruling becomes an ADR in the product's repository at its first appearance (the `Needs decision:` line names `ADR: <short title>`, and FO's existing decision-records step lands it); the design director reads the relevant ADRs before reviewing; the checker prints same-kind decision lines once per gate. This replaces the earlier project-learning wording. In the design: duty wording (starred paragraph), "Where an ADR comes from", refusals 5 and 6, AC-4, AC-11, AC-12.
- Design guide ruled: no design-guide format and no guide written as ADRs; a product's own design rulings are ADRs (D-4); revisit when a generated index of them would help. Nothing in the design builds a guide.
- D-5 ruled, option A as designed: validation refuses a ui task until a built-screen review with a screenshot that is not an ideation preview exists, or the Captain's quoted waiver. In the design: "At validation"; AC-6.
- D-6 ruled: at validation a design-director MINOR the FO would decline goes to the design director first, as at ideation, and the upheld ones are listed at the validation gate; this replaces the MINOR-to-Polish default. In the design: pass 2b, the per-finding lines, the validation clause in `workflow.md` (+14 words); AC-13.

### Open

**D-7 — How is "the MINOR FO would decline" made checkable at validation, and where does an overruled MINOR go?** FO's decline of Polish comes after the validation stage ends, and no check reads FO's gate summary; the three archived paseo validation briefings (read 2026-10-22) carry one FO decline in one of them and no check output. As designed, the validator proposes every MINOR's disposition: `declined: <reason>` (ruled by the director in pass 2b) or `Needs decision: <text>`; a MINOR the director overrules or sends to a decision cannot stay declined and goes to the Captain as a `Needs decision:` at the validation gate; the check refuses a finding with no disposition. Recommendation: this. Reasons: it is the only place the existing check can enforce the ruling, and it keeps FO's decline rule (`workflow.md` step 2) unchanged. What gets worse under it: the validator, not FO, picks which MINORs to propose for decline, so a MINOR FO later declines on its own is not ruled (the claim is bounded in the design); an overruled MINOR becomes a Captain question where, at ideation, it becomes a fix, and there is no fix route at validation short of the existing FO-authorized repair; a pass-2b run costs on the order of a pass-1b run (77k to 115k tokens at ideation, not measured at validation). Alternative: FO sends the MINORs to the director itself at the gate. That adds more words to `workflow.md` (not drafted) and puts a reviewer dispatch in FO's gate preparation. Past rulings: `git -C <state> grep -n 'Override:'` over the state checkout (2026-10-22) finds one that bears on this, D-6 of this task (recommended MINOR-defaults-to-Polish; Captain chose the ideation mechanism at validation), and D-7 follows it; the other hits are prose in archived tasks about unrelated areas. If the Captain rules the alternative, AC-13 and the validation hunk of the design are redone; the rest stands.

## Number guards

ADR: 0030

### Feedback Cycles

- Cycle 1 (FO, 2026-10-23): Codex review on #708 af4fb87e (review:5623263990) left two P2, to fix (rounds 1 and 2 fix every finding; a P1 blocks in every round); the findings name the line and the input, so FO authorizes the fix directly with validation Polish F4 and F5, then a fresh validation recheck.
  - P2 comment:4355556546: design_surfaces.py reads ruling items anywhere in the decline-check report, not only under design_decline_check.rulings, and accepts items missing their required fields. P2 comment:4355556553: the built-screen F-number lookup searches the whole task body, so an F bullet kept from an earlier validation cycle satisfies a new one.
- Cycle 2 (FO, 2026-10-23): Codex review on #708 f3ac6101 (review:5623395171) left one P1 and three P2, to fix (rounds 1 and 2 fix every finding; a P1 blocks in every round); FO authorizes the fix directly, then a fresh validation recheck.
  - P1 comment:4355670203: the built-screen review, finding and decline-check lookups still scan the whole task body, so a prior cycle's waiver satisfies a later cycle or a preserved line trips the duplicate-line error; scope them to the current validation report as the F-bullet lookup is. P2 comment:4355670210: a scalar design_decline_check root (`|`) is parsed as rulings; validate the root and its direct children. P2 comment:4355670216: an empty evidence: or change: value passes; treat empty as missing. P2 comment:4355670224: ADR 0030 is Proposed, which read-adr treats as not in force; mark it Accepted (the Captain approved the design at the ideation gate).

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

## Stage Report: ideation (cycle 3)

Cycle 3 supersedes cycles 1 and 2 where they differ (the D-1 to D-6 text, AC-3, AC-4, AC-6, AC-8, the words table, the workflow.md change, the overlap table). Amendment 1 and the backlog gate resolution are kept.

- DONE: Cycle 3: fold the Captain rulings D-1 to D-6 and the design-guide ruling recorded under ## FO alignment (2026-10-22) into ## Design and ## Acceptance criteria, then move each from Unresolved decisions to a ruled line: D-1 the operated whole-screen pass belongs to release-acceptance (Amendment 1 there), this task builds none of it; D-2 the design surfaces checker also prints each Preview: path so it reaches the briefing through the same workflow.md sentence, no further workflow.md words; D-3 not in this task; D-4 a host-look departure ruling becomes an ADR in that product repository on first appearance, the design director reads the relevant ADRs before reviewing, the checker prints same-kind decision lines once per gate (replace the project-learning wording); D-5 option A as designed; D-6 at validation a MINOR the FO would decline goes to the design director first and the upheld ones are listed at the validation gate (replace the MINOR-to-Polish default); recount the words FO reads; keep everything Amendment 1 and the backlog gate resolution approved
  Each ruling is a ruled line under `## Unresolved decisions for the Captain` with where it lands; D-1 checked against release-acceptance Amendment 1 (read 2026-10-22); the project-learning and Polish-default wording is gone. The Captain's D-2 sentence "no further workflow.md words" is kept for the preview paths; D-6 needs one validation clause (+14 words) because three archived paseo validation briefings carry no check output: raised as D-7 with the alternative.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, fo-write-checks-parse-top-level, idle-names-failing-seeds, agent-reads-governing-adr) and live task of other sessions (kc-decision-log-p1, kc-decision-log-cli, kc-decision-log-handoff-trial, pr-review-lite-value-pilot, release-acceptance, journey-canvas-hosted-poc, journey-server-host-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Redone at state HEAD ef331cd0 and origin/main cb35b82b (0.28.0); release-acceptance is now in implementation and edits the same `workflow.md`; comment-check also edits `validation/principles.md`; new overlaps are different passages.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Startup and the moments that read `workflow.md`: 5374 to 5389 (+15), measured on an edited copy; `lint-skills.py` on it prints only the budget error. Ideation gate: preview, upheld and decision lines now reach the briefing (simulated 30 to 141 and 17 to 143 words per task); validation gate: one summary line, one preview line, upheld lines (not measured).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1: not yet verified (lint and unit case at the candidate). AC-2: not yet verified (diff of the two blockquotes). AC-3: not yet verified (real ideation run, briefing read). AC-4: not yet verified (six refusal cases with mutants). AC-5: not yet verified (two-line case). AC-6: not yet verified (validation cases with mutants). AC-7: not yet verified (rerun of three replay prompts on the shipped agent). AC-8: partly verified (5389 words and the lone budget error, measured now); the rest not yet verified. AC-9: not yet verified (adr_lint, doc_impact). AC-10: not yet verified (preview-path case). AC-11: not yet verified (grouping case with mutants). AC-12: not yet verified (three fixture runs of the shipped agent). AC-13: not yet verified (validation disposition cases; real-flow clause may not run). One open decision, D-7, with a recommendation and what gets worse.

### Summary

The design now carries every ruling: the director also reads the product's ADRs in force, the checker prints preview paths and groups decisions by kind and owner, validation refuses a ui task without a built-screen review, and the validator's MINOR declines are ruled by the director and listed at the validation gate. FO-read words rise by 15 at startup. Needs the Captain: D-7 (who proposes the MINOR declines at validation, and where an overruled MINOR goes), and approval words that name the +15 `workflow.md` raise, since no earlier ruling does. The director reads ADRs through `kc-adr:read-adr` (first use of that skill in kc-dev-flow-2; unavailable branch defined).

## Stage Report: implementation

- DONE: One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (126efaf06b4d3f06c29d6b071189ed7771c41ee9) implementing the approved cycle-3 design: the kc-dev-flow-2:design-director agent and skill (sonnet), pass 1a and 1b at ideation, pass 2 and 2b at validation, the design surfaces checker changes, the workflow.md sentence and clause (+15 words, 5374 to 5389) with the lint-skills.py budget step carrying the Captain's quoted words, the new ADR 0030 and a one-line pointer in ADR 0022; only the files the design names
  PR https://github.com/iamcxa/kc-claude-plugins/pull/708 (Draft), head af4fb87e, commits a517672e, ec70dfeb, af4fb87e; `git diff --stat` touches only the design's file list; the worktree was behind origin/main and was fast-forwarded to 126efaf0 first.
- FAILED: Every acceptance criterion AC-1 to AC-13 green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared); the AC-7 replay of the shipped agent on the kc-paseo-plugins tasks in the replay folder; the words FO reads measured as AC-8 states
  Green: AC-1, 2, 4, 5, 6, 9, 10, 11, 12, 13 (unit part), 8 (diff part). AC-3 not run (needs a real paseo ideation and FO gate prepare). AC-7 met in 1 of 3 runs. AC-13 real-flow clause not run. Details below.
- DONE: lint-skills.py and adr_lint.py docs/adr --since <base> --require 0030 exit 0; comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured
  Candidate `scripts/lint-skills.py` exit 0 (the 0.28.0 cache copy run with `--root` fails on its own old budget, 5389 vs 5374, and a missing frontmatter script, so it cannot grade the candidate); adr_lint exit 0; comment_ratio 0.8% of 5%; `evidence=roborev:1051` clean on ec70dfeb; roborev:1052 and :1053 on af4fb87e (test-only commit) found three High items, all limits the design states (waiver checked for a quoted span; screenshot checked only to differ from ideation pictures; no `Design review:` line is not caught), left for FO; push plain, CI green on af4fb87e (unit tests 1m44s, parity 58s, others seconds; billed minutes not measured).

### Evidence by criterion
- Package root mismatch: the loaded skill said 0.27.0, the dispatch 0.28.0; roborev, adr_lint, comment_ratio, doc_impact, number_guards ran from 0.28.0, lint-skills and tests from the candidate.
- AC-1: `test_design_director_keeps_its_declared_model` (model: inherit expects the policy error) and `test_design_director_needs_its_skill` (rmtree expects "missing skills: design-director"); 37 tests pass.
- AC-2: the `>` lines of review-brief.md and of the base design-review.md are identical under `diff` (zero differences; the pass-2 reading is stated outside the blockquote); one edited word prints in `diff`; design-review.md has no blockquote.
- AC-4/5/6/10/11/13 (unit): 167 tests in test_design_surfaces.py. Each refusal has a test that fails if its branch is replaced (helper `mutation` asserts the refusal text appears once in the real script and nowhere in the mutant). AC-6 (b) "under a Preview folder" is subsumed by (c) "same bytes": a file under a Preview path always matches its own digest, so one rule and one mutant cover both.
- AC-7: shipped agent via `claude -p --plugin-dir <worktree>/kc-dev-flow-2 --agent kc-dev-flow-2:design-director` (sonnet), replay prompts adapted to Pass: 1b with ADR folder: none (findings inline, not a saved report). Run 1 (before restoring two measured phrases): upheld 15, overruled 10, decision 14; #4 and #13 miss. Run 2 (final wording): 13/12/14, every bound met. Run 3 (final wording): 18/9/12, overruled below 12 and variable-row-edit #4 a decision. Every decision carried a kind and owner. Prototype was 12/15/12 and 14/14/11. Not tuned further; whether the bounds or the wording change is for FO and the Captain.
- AC-8: pr_watch/delivery_gate/role_triggers diff empty; workflow.md diff is 2 hunks; `wc -w` 5389; lint passes with one added step (delta 15, quoted captain, loaded). Real check output on the shipped agent's rulings (dispositions synthetic, decline reasons the authors' own): 203 to 298 words per task for the ideation gate across the 3 tasks and 3 runs; validation count not measured (no consumer reached validation).
- AC-9: README sentence; ADR 0030 Proposed; adr_lint exit 0; with the Options line deleted adr_lint exits 1 "Decision needs a '**Options considered:**' line"; ADR 0022 pointer line. doc_impact: README updated; ADR 0020, maintain-flow SKILL.md and learning.md unaffected (they describe the budget mechanism, not its steps).
- AC-12: three runs on the plain-failure-reason prompt with the shipped agent: (a) Accepted record: finding 11 overruled with `adr:` and `adrs_read` Accepted, transcript shows kc-adr:read-adr loaded; (b) Proposed: decision host-look Captain, listed Proposed; (c) none: decision host-look Captain; (e) kc-adr disabled by settings: `adrs_read: unavailable`, decision. (a) to (c) ran before the wording fix of ec70dfeb; (e) after.
- AC-3 not run. Instead the shipped agent's 1b output for the 3 tasks, with synthetic dispositions, passes `design_surfaces.py check` (exit 0) and prints the preview, upheld and decision lines.
- Real bug found by tests and fixed: `CAPTAIN_QUOTE` was undefined in design_surfaces.py.

### Summary

Built the design-director agent, skill, brief, both checks, the 15-word raise and ADR 0030; unit evidence and the mutation proofs are green and CI passes. Not green: AC-3 (needs a real paseo ideation), the real-flow clause of AC-13, and AC-7, where the shipped agent met the bounds in 1 of 3 runs. FO decides the AC-7 bounds and what to do about the three High roborev items that restate the design's declared limits.

## Stage Report: implementation (cycle 2)

- DONE: Move AC-7 and AC-3 under `Superseded text:` in Captain Amendment 2 and write their replacements marked (Amended by Captain, amendment 2; replaces AC-7) and (Amended by Captain, amendment 2; replaces AC-3), carrying exactly what Amendment 2 states and nothing more, per ADR 0005; change no code
  AC-3 and AC-7 moved verbatim into Amendment 2; replacements are AC-14 (replaces AC-7) and AC-15 (replaces AC-3), fresh ids; `design_surfaces.py check` on this task file prints "design surfaces presentable"; the code worktree is unchanged at af4fb87e.
- DONE: Update the PR #708 body's acceptance and known-limit lines to match the amended criteria, and commit the stage report
  `gh pr edit 708 --body-file` succeeded: the evidence line points to AC-14, the residual line to AC-15, and the `without-it unanswered` section became "Known limit" carrying AC-14.
- DONE: All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report
  No code changed, so no new head: af4fb87e is already on origin, CI green on it, and the package suites passed before it. Roborev on the unchanged head printed `findings on af4fb87ec; evidence=roborev:1057`: the same class of High items as roborev:1052 and :1053 (waiver checked for a quoted span, screenshot checked only to differ from ideation pictures, no `Design review:` line not caught), each a limit the design states; left for FO.

### Summary

Amendment 2 is applied in the task file and the PR body; no code, push or head change.

## Stage Report: validation

- DONE: Independent verdict on PR #708 head af4fb87e against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Head af4fb87e (PR head confirmed by `gh pr view` at the end; base 126efaf0 = origin/main). AC-1 to 13 re-run, AC-14 verified, AC-15 owed; per-criterion evidence and falsifiers under "Evidence by criterion".
- DONE: Judge AC-3 and AC-7 as replaced under Captain Amendment 2 (AC-7 records the measured runs with no pass bound; AC-3 is a post-release check and is reported as owed, not run); read the AC-7 run outputs from the implementation worktree; disposition the three roborev High items against the AC-6 and ADR 0030 text they restate
  AC-14 holds against the run outputs in /tmp/dd-impl/ac7run1, ac7run2, ac7c; AC-15 is owed, not run; roborev items are F1, F2, F3 (Deferred risk).
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Script run with `env -i ... bash --noprofile --norc` (exit 0, output below); adr_lint exit 0 (below); verdict PASSED on af4fb87e with no Material finding.

### Verdict

PASSED, recommended, for head af4fb87ecd6b60c17750175cc9de40da4eecdf82 (base 126efaf06b4d3f06c29d6b071189ed7771c41ee9). No Material finding. Product bytes and the candidate revision were not changed; checked out detached in a throwaway worktree, removed after. CI on the head: 5 of 5 checks SUCCESS, PR Draft, MERGEABLE (`gh pr view 708`).

### Findings

- F1 Deferred risk: a worker can write `Built screen review: waived 「any text」` and pass; the check tests only for a non-empty 「…」 span, not that the words are the Captain's (roborev 1052/1053 High, location `CAPTAIN_QUOTE` use in `check_built_screen`). AC-6 states exactly this ("`waived` with a 「…」 quote passes, without one is refused") and `validation/principles.md` says only the Captain's quoted words waive. Material if a waiver is found whose words the Captain did not say; the compare-with-gate-record step of ADR 0020 is the model to copy then.
- F2 Deferred risk: any task-local file whose bytes differ from every `Preview:` file passes as the built screenshot (roborev 1052/1053 High). AC-6's own Limit states "the check cannot tell that a different file shows the built screen"; my probe: an unrelated file passes, a byte-copy of the ideation preview is refused. Material if a validator is observed submitting a non-candidate picture.
- F3 Deferred risk: a ui task at validation whose `Design review:` line is absent is not refused (roborev 1053/1057 High). AC-6 requires this exemption ("ideated before the review"), the approved design carries it, and the ideation check already refuses a ui task with no `Design review:` line, so only deleting the line after ideation reaches it. Material if a ui task is found at validation with that line removed.
- F4 Polish: ADR 0030 Recommended says "Validation refuses a ui task with no built-screen review unless the Captain waives it", with no word for the F3 exemption; the repository rule that an absolute names its enforcement point applies. One clause naming the exemption fixes it. No profile or behaviour change.
- F5 Deferred risk: pass 2a was never run by a model in implementation (AC-7 and AC-12 runs were pass 1b only). My one pass 2a run (shipped agent, sonnet, fenced YAML, five findings, well formed) copied the `Screenshots:` value verbatim into `preview:`; I passed an absolute path, and the check refuses an absolute `preview:` ("names no screenshot file inside the task folder"). `validation/principles.md` does not say which path form `Screenshots:` takes, and the director must read an absolute path while the check wants a task-folder-relative one. Fail-closed, fixed by editing one line; material if validators are seen stalling on it. The wording fix is one sentence in `validation/principles.md`.
- F6 Deferred risk (limit judged): AC-8's validation-gate word count was not measured on a real run (no consumer reached validation); AC-13's real-flow clause is reported not run, which AC-13 allows; AC-15 (replaces AC-3) is owed at the first kc-paseo-plugins ui ideation after release.
- F7 Polish: AC-14 provenance. The run directory `ac7` is a duplicate of `ac7run2` (same session id, byte-identical), so there are three runs, not four; runs 2 and 3 started minutes before commit ec70dfeb (19:56:58) and I cannot show their SKILL.md bytes equal that commit's. AC-14 sets no bound, so no verdict depends on it.

### Evidence by criterion

- Package root: the skill loaded 0.27.0, the dispatch and checklist say 0.28.0. `adr_lint` ran from both (same output, exit 0); comment_ratio, doc_impact, number_guards, dispatch_records ran from 0.28.0; lint-skills and tests ran from the candidate itself.
- AC-1: candidate `lint-skills.py` exit 0; `test_lint_skills` 37 OK. Falsifiers on a copy: `model: inherit` gives "design-director agent: existing sonnet/high policy changed"; removing the skill folder gives "missing skills: design-director".
- AC-2: `diff` of the base and candidate blockquotes is empty (32 lines each, zero differences, stronger than the criterion's "one sentence"); `design-review.md` has no `>` lines; one edited word prints in `diff`.
- AC-4: all 20 test files pass (design_surfaces 167 tests). My independent falsifier per refusal on a fixture task: for each of the six refusals (no Decline check line; no ruling; overruled still declined; host component without path; decision without kind or owner; host-look without `ADR:` title) the real script exits 1 with that reason and a copy with only that branch removed exits 0.
- AC-5, AC-10, AC-11: real output holds `upheld decline <n>:` lines (2 upheld, 1 overruled gives "2 upheld, 1 overruled, 0 decisions in 0 groups"), `preview: <resolved path>`, and decisions grouped by (kind, trimmed casefolded owner). Mutants (count only; no preview line; unresolved path; group by kind alone; no grouping; no casefold) each change the output as the criterion says.
- AC-6, AC-13: fixture at status validation: no line, absent screenshot, byte-copy of ideation preview, `waived` without quote all refused with their own reasons; different bytes, quoted waiver, no `Design review:` line, and status implementation pass. Mutants dropping the status gate, file-exists test, byte comparison, quote test, `Design review:` condition, decline-check-line rule, F-bullet test, disposition test and the printed upheld line each fail their case (disposition mutant isolated on an input with no ruling).
- AC-8: pr_watch, delivery_gate, role_triggers diff empty; `workflow.md` diff is two hunks, 5389 words; lint passes with one added budget step whose `captain` quote matches the ideation gate resolution; falsifiers: one stray word gives "5390 words exceeds the budget of 5389", a missing `captain` quote gives "has no quoted words". Validation-gate count unmeasured (F6).
- AC-9: ADR 0030 present, `adr_lint --since 126efaf0 --require 0030` exit 0; removing the Options line gives exit 1 "Decision needs a '**Options considered:**' line"; ADR 0022 carries the pointer line (git diff, +2); doc_impact lists ADR 0020, maintain-flow SKILL.md, learning.md as `review`, README `updated`; the implementation report records those three as unaffected (they describe the budget mechanism, not its steps; checked in ADR 0020 and maintain-flow).
- AC-12: I reran on the candidate with my own copies of the scratch ADR folders: (a) Accepted record gives finding 11 `overruled` with `adr:` naming the file, `adrs_read` Accepted, transcript shows a `kc-adr:read-adr` Skill call; (b) Proposed gives `decision`, host-look, Captain, `adrs_read` Proposed, skill called; (c) `none` gives `decision`, host-look, Captain, no skill call; (f) real folder with kc-adr disabled gives `adrs_read: unavailable` and `decision`. The shipped agent's fenced output saved unedited also passes `design_surfaces.py check` against a 13-finding fixture.
- AC-14: verified from the run outputs: run 1 (before the phrases were restored) 15 upheld, 10 overruled, 14 decision; run 2 13/12/14; run 3 18/9/12; control 23/6/10 (counted from replay/control/rulings.tsv). Both final-wording runs overrule more (12, 9 against 6) and uphold fewer (13, 18 against 23); run 3 misses the old overruled bound; every decision carries kind and owner. F7 on provenance.
- Comments: comment_ratio 0.8% of 5% (4 lines, all markdown headings inside a test fixture string); number_guards PASS (no migrations declared); dispatch_records "6 dispatch record(s) complete".

### adr_lint

`python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since 126efaf06b4d3f06c29d6b071189ed7771c41ee9` run in the candidate checkout: "29 ADR file(s) checked, 0 legacy", exit 0 (also with `--require 0030`).

### Minimal acceptance script

Run by me exactly as written in a fresh shell (`env -i`, no profile). It needs git, python3 and network access to github.com; it fetches the head into a temp directory. It covers the checker, the lint and the agent file only. It does not run the model: how the director rules (AC-14, AC-12) and the first real paseo ideation (AC-15) are not covered.

```bash
# Acceptance script for kc-claude-plugins PR #708 (design director), head af4fb87e
# Needs: git, python3, network access to github.com. No secret. Run in a fresh bash shell.
set -u
W=$(mktemp -d) && cd "$W" && git init -q repo && cd repo \
  && git fetch -q --depth 1 https://github.com/iamcxa/kc-claude-plugins.git af4fb87ecd6b60c17750175cc9de40da4eecdf82 \
  && git checkout -q FETCH_HEAD && git log --oneline -1 && S=$PWD/kc-dev-flow-2/scripts && cd "$S"
echo "--- step 1: the plugin lint passes with the 15-word budget raise"
python3 -B lint-skills.py; echo "exit=$?"
echo "--- step 2: the two test suites for this change pass"
python3 -B -m unittest test_design_surfaces test_lint_skills 2>&1 | grep -E "^(Ran|OK|FAILED)"
echo "--- step 3: a ui task at ideation with a declined finding, ruled upheld, prints the gate lines"
T=$W/t; mkdir -p $T/task/design; cd $T
printf '<html></html>\n' > preview.html
cat > task.md <<'T'
---
title: a ui task
profile: pilot
status: ideation
---

## FO alignment

Surfaces: ui
Visible change: a person sees a panel.

## Design

UI proposal: a panel.
Preview: preview.html

### Design review

Design review: design/ideation-1.yaml
Design finding 1: fixed: the header is one line in preview.html
Design finding 2: declined: the inset matches the shell
Design finding 3: AC-2
Design finding 4: Needs decision: the host has no slot for this button ADR: Plugin-drawn buttons
Decline check: design/declines-1.yaml

## Acceptance criteria

**AC-1**: a.
Verified by: a test.
**AC-2**: b.
Verified by: a test.
T
cat > task/design/ideation-1.yaml <<'T'
design_review:
  preview: preview.html
  findings:
    - severity: MAJOR
      dimension: hierarchy
      where: after-desktop.png
      seen: the count is stated twice
      fix: keep one
    - severity: MINOR
      dimension: spacing
      where: after-desktop.png
      seen: tight inset
      fix: widen it
    - severity: MAJOR
      dimension: consistency
      where: after-phone.png
      seen: opposite chevrons
      fix: one convention
    - severity: MINOR
      dimension: consistency
      where: after-phone.png
      seen: button is not the host's
      fix: use the host button
  limitations:
    - the operable preview was not opened
T
cat > task/design/declines-1.yaml <<'T'
design_decline_check:
  adrs_read: none
  rulings:
    - finding: 2
      ruling: upheld
      evidence: after-desktop.png shows the inset equal to the shell's
      change: none
    - finding: 4
      ruling: decision
      evidence: the host declaration has no slot for it
      change: the Captain accepts a custom button or not
      kind: host-look
      owner: Captain
T
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 4: the same task without its Decline check line is refused"
grep -v '^Decline check:' task.md > nocheck.md; mv nocheck.md task.md
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 5: at validation a ui task with no built-screen review is refused"
sed -i.bak 's/^status: ideation/status: validation/' task.md
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 6: the agent declares sonnet"
grep -E '^(model|reasoning):' "$S/../agents/design-director.md"
```

Observed output (exit 0; the temp directory name differs per run):

```
af4fb87 test(kc-dev-flow-2): use neutral words in the waiver fixture
--- step 1: the plugin lint passes with the 15-word budget raise
PASS: basic frontmatter, declared profile routes, role bindings and package script paths
references/sd/workflow.md: 5389 of 5389 words; no unlisted passage repeats it
Not checked: full Agent Skills conformance or host/workflow behavior
exit=0
--- step 2: the two test suites for this change pass
Ran 204 tests in 37.014s
OK
--- step 3: a ui task at ideation with a declined finding, ruled upheld, prints the gate lines
task.md: design surfaces presentable
design review design/ideation-1.yaml: 4 findings, 1 fixed, 1 criteria, 1 declined, 1 decisions; decline check design/declines-1.yaml: 1 upheld, 0 overruled, 1 decisions in 1 group
preview: <temp dir>/t/preview.html
upheld decline 2: the inset matches the shell
decision host-look, owner Captain (findings 4): the Captain accepts a custom button or not
scope check not run: no closed backlog approval
exit=0
--- step 4: the same task without its Decline check line is refused
task.md: a 'Design finding n: declined:' line needs a 'Decline check:' line naming the saved ruling report
scope check not run: no closed backlog approval
exit=1
--- step 5: at validation a ui task with no built-screen review is refused
task.md: built screen review not run: a ui task with a design review needs a 'Built screen review:' line or a quoted waiver
scope check not run: stage is validation, not ideation
exit=1
--- step 6: the agent declares sonnet
model: sonnet
reasoning: high
```

### Summary

PASSED on af4fb87e: the checker, lint, budget raise, ADR and agent file behave as AC-1 to AC-13 state, each falsifier I ran bites, and the shipped agent's rulings reproduce AC-12 and match AC-14's record. The roborev High items are limits that AC-6 states and are Deferred risk; the one new observation is F5 (path form for pass 2a screenshots). Owed after release: AC-15.

## Stage Report: implementation (cycle 3)

- DONE: In kc-dev-flow-2/scripts/design_surfaces.py: read ruling items only from the design_decline_check.rulings list of the saved report and refuse an item missing its required fields; scope the built-screen F-number lookup to the current validation Stage Report; one failing-then-passing test per fix in kc-dev-flow-2/scripts/test_design_surfaces.py, each shown failing on the matching mutant
  Commit 8e96f8e2. `rulings_lines` reads only the `rulings:` list under the `design_decline_check:` root; an item without `evidence` or `change` is refused; `validation_report` returns the last `## Stage Report: validation` section. Tests: `test_a_ruling_outside_the_rulings_list_does_not_count` (mutant: read the whole report) , `test_a_ruling_missing_its_evidence_or_change_is_refused` (mutant: drop the field test), `test_an_f_bullet_must_be_in_the_current_validation_report` (mutant: search the whole body); each asserts the reason text appears once in the real script and not in the mutant. The three saved shipped-agent reports still pass the check (exit 0).
- DONE: Validation Polish F4: ADR 0030 Recommended names the exemption for a ui task with no Design review line; F5: kc-dev-flow-2/skills/validation/principles.md says which path form the built-screen screenshot takes (task-folder-relative), matching what the check reads
  F4 in ADR 0030. F5 in principles.md. Roborev:1059 then found the brief copies `Screenshots:` into `preview:` while principles had said absolute; fixed in f3ac6101: pass 2a takes the task-folder-relative path plus `Task folder:` (principles.md and the pass table and one sentence of SKILL.md). One shipped-agent pass 2a run with that input copied `design/built-1.png` into `preview:`.
- DONE: All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report
  All 20 test files OK (design_surfaces 170, lint_skills 37 re-run at the final head); pushed af4fb87e..f3ac6101 without -u or force; CI green on f3ac6101 (unit tests 2m7s, parity 43s). Roborev: `evidence=roborev:1060` clean on f3ac6101 (roborev:1059 on 8e96f8e2 was the path-form item, fixed).

### Summary

Both Codex P2 and validation Polish F4 and F5 are fixed with a mutation-checked test each; the F5 fix also changed SKILL.md (pass 2a input `Task folder:`) because roborev showed the brief and principles disagreed. AC-14 and AC-15 are untouched.

## Stage Report: validation (cycle 2)

- DONE: Independent verdict on PR #708 head f3ac6101 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Head f3ac610184b2bfc5b424309219186d9d3f5a5ec2 (PR head confirmed by `gh pr view 708`; base 126efaf0); checked out detached in a throwaway worktree, removed after; per-criterion evidence under "Evidence by criterion (cycle 2)".
- DONE: Fresh recheck after the Cycle 1 repair (Codex review:5623263990, two P2) and validation Polish F4 and F5: judge each fix, its test and mutant, and whether AC-1 to AC-13, AC-14 and AC-15 (owed) still hold
  Both P2 and F4, F5 fixed and each P2 test bites on a mutant only it catches; AC-1 to AC-13 hold, AC-14 holds, AC-15 is owed (not run).
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Script run with `env -i ... bash --noprofile --norc` (6 steps, rc 0); adr_lint exit 0; verdict PASSED on f3ac6101, no Material finding.

### Verdict

PASSED, recommended, for head f3ac610184b2bfc5b424309219186d9d3f5a5ec2 (base 126efaf06b4d3f06c29d6b071189ed7771c41ee9). No Material finding. Product bytes and the recorded candidate were not changed. CI on the head: 5 of 5 checks SUCCESS, MERGEABLE; `gh pr view` showed `isDraft: false` at my read (I did not change it).

### Findings

- F1 Deferred risk, unchanged from the first validation (af4fb87e): a worker can write `Built screen review: waived 「any text」` and pass; the commit under review did not touch it.
- F2 Deferred risk, unchanged: any task-local file whose bytes differ from every `Preview:` file passes as the built screenshot (AC-6 states this limit).
- F3 Deferred risk, unchanged: a ui task with no `Design review:` line at validation is not refused (AC-6 requires the exemption).
- F4 Polish, closed: ADR 0030 Recommended now names the exemption and why (`check_task` runs the built-screen rule only where a `Design review:` line exists).
- F5 Deferred risk, closed: `skills/validation/principles.md` and `skills/design-director/SKILL.md` agree on a task-folder-relative path plus `Task folder:`. I ran the shipped agent (sonnet, candidate plugin) once on pass 2a with that input: it opened `design/built-1.png` and wrote `preview: design/built-1.png`; the saved report passes `design_surfaces.py check` (exit 0), and the same report with an absolute `preview:` is refused ("names no screenshot file inside the task folder").
- F6 Deferred risk, unchanged: the validation-gate word count was not measured on a real run; AC-13's real-flow clause is not run (AC-13 allows it); AC-15 is owed at the first kc-paseo-plugins ui ideation after release.
- F7 Polish, unchanged: AC-14 run provenance (duplicate run directory; run start times against commit ec70dfeb); AC-14 sets no bound, so no verdict depends on it.
- F8 Deferred risk, new: the stricter ruling reader (`rulings_lines`) matches the key line only as `rulings:` with nothing after it, and splits on newline. A trailing comment (`rulings: # ruled`) or CRLF line endings give zero rulings, so a valid report is refused with "declined finding N has no ruling" (the base reader accepted both). Fail-closed; the brief's report shape has no comment, and all 17 saved shipped-agent and prototype reports read the same item lists under both versions. Material if a saved report is seen refused for this reason; the fix is a trailing-comment and carriage-return allowance in the key match.

### Evidence by criterion (cycle 2)

- Package root: the skill loaded 0.27.0, the dispatch and checklist say 0.28.0; the scripts I ran (adr_lint, comment_ratio, doc_impact, number_guards, dispatch_records) are identical between the two (`diff -rq` lists only pr_watch, the codex extension, workflow.md and manifests). adr_lint ran from both. lint-skills and the tests ran from the candidate.
- Candidate checks: `lint-skills.py` exit 0 (5389 of 5389 words); all 20 test files OK (design_surfaces 170, lint_skills 37, delivery_gate 86, pr_watch 101); comment_ratio 0.5% of 5% (3 lines, all `##` lines inside a test fixture string); number_guards PASS; dispatch_records "8 dispatch record(s) complete"; doc_impact lists ADR 0020, README, maintain-flow SKILL.md and learning.md as in the first validation (README updated; the other three unaffected per the implementation report).
- P2 one (ruling items read anywhere): my fixtures through the real CLI. Rulings under `notes:` beside `rulings: []`, or under a second top-level key, are refused by f3ac6101 ("declined finding 2 has no ruling") and were accepted by af4fb87e; items without `evidence` and `change` are refused by f3ac6101 and were accepted by af4fb87e; a fenced report with reordered keys, a block scalar holding `finding: 99` and `ruling: overruled` text and a quoted finding number reads correctly in f3ac6101 and was refused by af4fb87e. `evidence` and `change` are required in the `SKILL.md` report shape, so the refusal matches the contract.
- P2 two (F bullet searched in the whole body): fixtures at validation: an `- F1` bullet only in an earlier `## Stage Report: validation`, or only in an implementation report, is refused by f3ac6101 and was accepted by af4fb87e; a bullet in the latest validation report (also one after a fenced block holding a `## ` line, since `check_task` strips fenced lines first) passes.
- Mutants (copy of the candidate scripts, `python3 -B`, baseline 170 OK): reading the whole report fails `test_a_ruling_outside_the_rulings_list_does_not_count` only; dropping the required-fields branch fails `test_a_ruling_missing_its_evidence_or_change_is_refused` only; searching the whole body fails `test_an_f_bullet_must_be_in_the_current_validation_report` only.
- AC-1: on a copy, `model: inherit` gives "design-director agent: existing sonnet/high policy changed"; removing the skill folder gives "missing skills: design-director". AC-2: `diff` of the base and candidate blockquotes is empty; `design-review.md` has no `>` lines. AC-8: pr_watch, delivery_gate, role_triggers diff empty; workflow.md two hunks, 5389 words. AC-9: `adr_lint docs/adr --since 126efaf0 --require 0030` exit 0; with its Options line deleted exit 1 "Decision needs a '**Options considered:**' line"; ADR 0022 carries the pointer line. AC-4, 5, 6, 10, 11, 13: the 170-test suite at the head plus the first validation's per-branch falsifiers, which this delta does not touch except the two repaired branches above.
- AC-12 and AC-14 not rerun: the delta since af4fb87e changed only the pass 2a row and sentence of `SKILL.md`, not passes 1a, 1b or 2b, so the measured 1b runs stand; AC-14 sets no bound. AC-15 is owed, not run.

### adr_lint

`python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since 126efaf06b4d3f06c29d6b071189ed7771c41ee9`, run in the candidate checkout: "29 ADR file(s) checked, 0 legacy", exit 0 (also from 0.27.0 with `--require 0030`, exit 0).

### Minimal acceptance script

Run by me exactly as written in a fresh shell (`env -i`, no profile). It needs git, python3 and network access to github.com; it fetches the head into a temp directory. It covers the checker, the lint, the tests and the agent file only. It does not run the model: how the director rules (AC-14, AC-12), the pass 2a path form with a live model, and the first real paseo ideation (AC-15) are not covered.

```bash
# Acceptance script for kc-claude-plugins PR #708 (design director), head f3ac6101
# Needs: git, python3, network access to github.com. No secret. Run in a fresh bash shell.
set -u
H='##'
W=$(mktemp -d) && cd "$W" && git init -q repo && cd repo \
  && git fetch -q --depth 1 https://github.com/iamcxa/kc-claude-plugins.git f3ac610184b2bfc5b424309219186d9d3f5a5ec2 \
  && git checkout -q FETCH_HEAD && git log --oneline -1 && S=$PWD/kc-dev-flow-2/scripts && cd "$S"
echo "--- step 1: the plugin lint passes with the 15-word budget raise"
python3 -B lint-skills.py; echo "exit=$?"
echo "--- step 2: the two test suites for this change pass"
python3 -B -m unittest test_design_surfaces test_lint_skills 2>&1 | grep -E "^(Ran|OK|FAILED)"
echo "--- step 3: a ui task at ideation, one decline ruled upheld, prints the gate lines"
T=$W/t; mkdir -p $T/task/design; cd $T
printf '<html></html>\n' > preview.html
cat > task.md <<T
---
title: a ui task
profile: pilot
status: ideation
---

$H FO alignment

Surfaces: ui
Visible change: a person sees a panel.

$H Design

UI proposal: a panel.
Preview: preview.html

${H}# Design review

Design review: design/ideation-1.yaml
Design finding 1: fixed: the header is one line in preview.html
Design finding 2: declined: the inset matches the shell
Design finding 3: AC-2
Design finding 4: Needs decision: the host has no slot for this button ADR: Plugin-drawn buttons
Decline check: design/declines-1.yaml

$H Acceptance criteria

**AC-1**: a.
Verified by: a test.
**AC-2**: b.
Verified by: a test.
T
cat > task/design/ideation-1.yaml <<'T'
design_review:
  preview: preview.html
  findings:
    - severity: MAJOR
      dimension: hierarchy
      where: after-desktop.png
      seen: the count is stated twice
      fix: keep one
    - severity: MINOR
      dimension: spacing
      where: after-desktop.png
      seen: tight inset
      fix: widen it
    - severity: MAJOR
      dimension: consistency
      where: after-phone.png
      seen: opposite chevrons
      fix: one convention
    - severity: MINOR
      dimension: consistency
      where: after-phone.png
      seen: button is not the host's
      fix: use the host button
  limitations:
    - the operable preview was not opened
T
cat > task/design/declines-1.yaml <<'T'
design_decline_check:
  adrs_read: none
  rulings:
    - finding: 2
      ruling: upheld
      evidence: after-desktop.png shows the inset equal to the shell's
      change: none
    - finding: 4
      ruling: decision
      evidence: the host declaration has no slot for it
      change: the Captain accepts a custom button or not
      kind: host-look
      owner: Captain
T
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 4: the same rulings placed outside the rulings list are refused"
cat > task/design/declines-1.yaml <<'T'
design_decline_check:
  adrs_read: none
  rulings: []
  notes:
    - finding: 2
      ruling: upheld
      evidence: after-desktop.png shows the inset equal to the shell's
      change: none
T
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 5: at validation, an F bullet kept from an earlier validation report does not count"
mkdir -p $W/v/task/design && cd $W/v
printf 'built screen bytes' > task/design/built-1.png
printf '<html></html>\n' > preview.html
cat > task/design/validation-1.yaml <<'T'
design_review:
  preview: design/built-1.png
  findings:
    - severity: MAJOR
      dimension: hierarchy
      where: built-1.png
      seen: the count is stated twice
      fix: keep one
T
mk() { cat > task.md <<T
---
title: a ui task
profile: pilot
status: validation
---

$H FO alignment

Surfaces: ui
Visible change: a person sees a panel.

$H Design

UI proposal: a panel.
Preview: preview.html

Design review: design/ideation-1.yaml

$H Acceptance criteria

**AC-1**: a.
Verified by: a test.

$H Stage Report: validation

- F1 Behaviour: the count is said twice

$H Stage Report: validation (cycle 2)

- DONE: re-checked
$1
Built screen review: design/validation-1.yaml
Built screen finding 1: F1
T
}
mk ""
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "(now the cycle 2 report names its own F1 bullet)"
mk "- F1 Behaviour: the count is still said twice"
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 6: the agent declares sonnet"
grep -E '^(model|reasoning):' "$S/../agents/design-director.md"
```

Observed output (rc 0; the temp directory name differs per run):

```
f3ac610 fix(kc-dev-flow-2): name one path form for the pass 2a screenshot
--- step 1: the plugin lint passes with the 15-word budget raise
PASS: basic frontmatter, declared profile routes, role bindings and package script paths
references/sd/workflow.md: 5389 of 5389 words; no unlisted passage repeats it
Not checked: full Agent Skills conformance or host/workflow behavior
exit=0
--- step 2: the two test suites for this change pass
Ran 207 tests in 24.570s
OK
--- step 3: a ui task at ideation, one decline ruled upheld, prints the gate lines
task.md: design surfaces presentable
design review design/ideation-1.yaml: 4 findings, 1 fixed, 1 criteria, 1 declined, 1 decisions; decline check design/declines-1.yaml: 1 upheld, 0 overruled, 1 decisions in 1 group
preview: <temp dir>/t/preview.html
upheld decline 2: the inset matches the shell
decision host-look, owner Captain (findings 4): the Captain accepts a custom button or not
scope check not run: no closed backlog approval
exit=0
--- step 4: the same rulings placed outside the rulings list are refused
task.md: declined finding 2 has no ruling in 'design/declines-1.yaml'
scope check not run: no closed backlog approval
exit=1
--- step 5: at validation, an F bullet kept from an earlier validation report does not count
task.md: 'Built screen finding 1:' names F1, but the current validation report has no '- F1 <Class>:' bullet
scope check not run: stage is validation, not ideation
exit=1
(now the cycle 2 report names its own F1 bullet)
task.md: design surfaces presentable
built screen review design/validation-1.yaml: 1 findings, 0 upheld declines, 0 decisions in 0 groups
preview: <temp dir>/v/task/design/built-1.png
scope check not run: stage is validation, not ideation
exit=0
--- step 6: the agent declares sonnet
model: sonnet
reasoning: high
```

### Summary

PASSED on f3ac6101: both Codex P2 and Polish F4, F5 are fixed, each P2 test fails only on its own mutant, the live pass 2a run now writes the relative path the check accepts, and AC-1 to AC-13 and AC-14 hold. One new Deferred risk (F8: a comment or CRLF on the `rulings:` line refuses a valid report, fail-closed); AC-15 stays owed.

## Stage Report: implementation (cycle 4)

- DONE: In kc-dev-flow-2/scripts/design_surfaces.py: scope the built-screen review, finding and decline-check lookups to the current validation report as validation_report(body) already does for the F bullets; refuse a design_decline_check root whose value is a scalar rather than a mapping; treat an empty evidence: or change: value as missing; one failing-then-passing test per fix in kc-dev-flow-2/scripts/test_design_surfaces.py, each shown failing on the matching mutant
  Commit e033956e. `check_built_screen` now reads every `Built screen ...` line from the last validation Stage Report. A `design_decline_check:` line with a value after its colon is refused. An empty `evidence:` or `change:` is missing. Tests: `test_the_review_finding_and_decline_lines_are_read_from_the_current_validation_report_only` (an earlier cycle's waiver no longer satisfies; preserved lines no longer trip the duplicate refusal; mutant: search the whole body, shown failing both ways), `test_a_scalar_design_decline_check_root_is_refused` (mutant: drop the root-value test), `test_an_empty_evidence_or_change_counts_as_missing` (mutant: key-presence only). Narrowing: the built-screen lines must now sit in the validation Stage Report, not anywhere in the body (principles.md says so); AC-6's "in the body or the stage report" is narrowed by this authorization.
- DONE: Set ADR 0030's status to Accepted (the Captain approved the design at the ideation gate, 2026-10-22); docs/adr lint still exits 0
  Status Accepted; `adr_lint.py docs/adr --since 126efaf0 --require 0030` exit 0.
- DONE: All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report
  All 20 test files OK (design_surfaces 173); pushed f3ac6101..e033956e, no -u, no force; CI green on e033956e (unit tests 2m2s, parity 53s); `evidence=roborev:1069` clean on e033956e. The saved shipped-agent decline reports still pass the check.

### Summary

The Cycle 2 P1 and three P2 are fixed with a mutation-checked test each, and ADR 0030 is Accepted. No criterion text changed.

## Stage Report: validation (cycle 3)

- DONE: Independent verdict on PR #708 head e033956e against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Head e033956e955503fcf81c134ace19d9cc9fd1dd25 (PR head confirmed by `gh pr view 708`; base 126efaf0); checked out detached in a throwaway worktree, removed after; AC-1 to AC-13 re-run with my own falsifiers, AC-14 holds, AC-15 owed; evidence under "Evidence by criterion (cycle 3)".
- DONE: Fresh recheck after the Cycle 2 repair (Codex review:5623395171, one P1 and three P2): judge each fix, its test and mutant, ADR 0030 now Accepted, and whether AC-1 to AC-14 still hold (AC-15 owed)
  P1 and the three P2 are fixed, each test fails only on its own mutant; ADR 0030 reads Accepted; AC-1 to AC-14 hold; the P1 fix narrows where the built-screen lines may sit (F9, Deferred risk).
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Script run with `env -i ... bash --noprofile --norc` (6 steps, rc 0); adr_lint exit 0; verdict PASSED on e033956e, no Material finding.

### Verdict

PASSED, recommended, for head e033956e955503fcf81c134ace19d9cc9fd1dd25 (base 126efaf06b4d3f06c29d6b071189ed7771c41ee9). No Material finding. Product bytes and the recorded candidate were not changed; I pushed nothing, commented on no PR and did not touch its Draft state (`gh pr view` shows `isDraft: false`, MERGEABLE, 5 of 5 checks SUCCESS on this head).

### Judgment: does the Cycle 2 repair narrow AC-6 as approved?

Yes, in one place; classified F9 below. The words "in the body or the stage report" are the approved Design's (`### Ideation records and the check`, At validation, the `Built screen review:` bullet). AC-6's own text and evidence cases name no location, and every AC-6 case still holds at this head (my probes below). Before e033956e the review, finding and decline-check lines were read from the whole task body; now from the last `## Stage Report: validation` section only (`validation_report`, applied at the top of `check_built_screen`). Observed through the real CLI against f3ac6101 and e033956e on the same fixtures: a waiver under a body section outside any stage report passes at f3ac6101 and is refused at e033956e; a waiver kept in an earlier validation report no longer satisfies a later one (the Codex P1); identical lines kept in two validation reports no longer trip "2 'Built screen review:' lines"; a waiver in the last validation report passes at both. FO authorized exactly this ("scope them to the current validation report as the F-bullet lookup is", Cycle 2), the Captain's D-5 words 「要擋下，不然找它的意義就消失了」 name no location, and both D-5 exits (a review with a non-ideation screenshot, or a quoted waiver) remain, so the check refuses more, not less.

### Findings

- F1 Deferred risk, unchanged: a worker can write `Built screen review: waived 「any text」` and pass (AC-6 states this limit).
- F2 Deferred risk, unchanged: any task-local file whose bytes differ from every `Preview:` file passes as the built screenshot (AC-6 states this limit).
- F3 Deferred risk, unchanged: a ui task at validation with no `Design review:` line is not refused; ADR 0030 now names the exemption (F4, closed).
- F6 Deferred risk, unchanged: validation-gate word count unmeasured on a real run; AC-13 real-flow clause not run; AC-15 owed at the first kc-paseo-plugins ui ideation after release.
- F7 Polish, unchanged: AC-14 run provenance; AC-14 sets no bound.
- F8 Deferred risk, unchanged: `rulings:  # comment` or CRLF on the `rulings:` key line gives zero rulings and refuses a valid report (fail-closed). The new root check does allow a trailing comment on the `design_decline_check:` line (probe: accepted).
- F9 Deferred risk, new: the built-screen review, finding and decline-check lines, and a Captain waiver, count only inside the last validation Stage Report. (1) Workflow: unreleased; the normal path, the validator writing them in its own report as `validation/principles.md` now says, passes. (2) Harm: a line or waiver FO or the Captain records in the body, or one carried over from an earlier validation cycle, is refused; fail-closed and cured by writing it in the last validation report. (3) Boundary: none established; D-5 and AC-6 hold and are stricter. (4) Trigger: none observed. Material if a Captain waiver given at a validation gate, after the validator's report, is recorded by FO outside that report and the task stalls on the refusal, or if the Captain wants one waiver to carry across validation cycles. It is not Needs decision: no Captain ruling names a location and FO's authorization covers the scoping; it turns into one if the Captain wants the waiver to persist.
- F10 Polish, new: two texts did not follow the narrowing. The approved Design line "in the body or the stage report" is now stale against `validation/principles.md` and the code, and the refusal "built screen review not run: a ui task with a design review needs a 'Built screen review:' line or a quoted waiver" does not say it reads only the last validation Stage Report, so a person whose line sits in the body sees a refusal that looks wrong (probe E). One clause in each fixes it; the implementation report's own line "AC-6 ... is narrowed by this authorization" is the record that exists today.

### Evidence by criterion (cycle 3)

- Package root: the skill loaded 0.27.0, the dispatch and checklist say 0.28.0. adr_lint ran from both and from the candidate's own copy (same output, exit 0); comment_ratio, doc_impact, number_guards, dispatch_records ran from 0.28.0; lint-skills and the tests ran from the candidate.
- Candidate checks: `lint-skills.py` exit 0 (5389 of 5389 words); all 20 test files OK (design_surfaces 173, lint_skills 37, delivery_gate 86, pr_watch 101; `test_observer_recovery` and `test_sd_dispatch` collect 0 tests under unittest, as at the earlier heads); comment_ratio 0.5% of 5% (3 lines in a test fixture string); number_guards PASS; dispatch_records "10 dispatch record(s) complete"; `design_surfaces.py check` on this task file exit 0; doc_impact lists ADR 0020, README (updated), maintain-flow SKILL.md and learning.md, unchanged from the earlier validations; the cycle 4 delta is three hunks of `design_surfaces.py`, one line of `principles.md`, the ADR Status word and tests.
- P1 (lookups scan the whole body): probes A to H on one fixture through the real CLI at f3ac6101 and e033956e. Stale waiver in the cycle 1 report with no line in the cycle 2 report: accepted then, refused now. Identical lines in both reports: refused then ("2 lines"), accepted now. Lines under a `###` sub-heading of the report count; lines in a fence do not; lines in a validation report followed by a later implementation report count. Mutant (copy, `python3 -B`, drop `body = validation_report(body)`): fails `test_an_f_bullet_must_be_in_the_current_validation_report` and `test_the_review_finding_and_decline_lines_are_read_from_the_current_validation_report_only`, nothing else.
- P2 scalar root: `design_decline_check: |`, `: >-` and `: {}` are refused ("a value after its colon, so its children are not a mapping"), the bare line and `:  # note` pass; f3ac6101 passed all of them. Mutant (drop the root test) fails `test_a_scalar_design_decline_check_root_is_refused` only.
- P2 empty evidence or change: `evidence:`, `change:` and `change: ""` are refused ("without 'change'"), `change: none` passes; f3ac6101 accepted all. Mutant (`key not in item`) fails `test_an_empty_evidence_or_change_counts_as_missing`; it also trips the older missing-key test, because that test asserts the real source line, which my mutant edited.
- P2 ADR 0030: Status reads `Accepted`; its Words line carries the ideation-gate 「可以」; `adr_lint docs/adr --since 126efaf0 --require 0030` exit 0 (0.28.0, 0.27.0 and the candidate's copy); with the Options line removed, exit 1 "Decision needs a '**Options considered:**' line".
- AC-1: `model: inherit` gives "design-director agent: existing sonnet/high policy changed"; removing the skill folder gives "missing skills: design-director". AC-2: the 32 `>` lines of the base `design-review.md` and of `review-brief.md` are identical under `diff`; `design-review.md` has none; one edited word prints in `diff`. AC-8: pr_watch, delivery_gate, role_triggers diff empty; `workflow.md` two hunks, 5389 words; one stray word gives "5390 words exceeds the budget of 5389". AC-9: as the ADR line above; ADR 0022 carries the pointer line.
- AC-4, 5, 6, 10, 11, 13: my own harness (`python3 -B`, source mutants on a copy, real CLI). Mutants that bite: no Decline-check line; overruled still declined; host component without `<Name> at <path>`; decision without kind; host-look without `ADR:` title; report without the root; upheld line printing; preview line printing; grouping by kind alone; grouping without case-folding; no built-screen line; ideation byte-copy as screenshot; waiver without quote; declined MINOR without a decline-check line. Real script refuses: F7 naming no bullet; a finding with no disposition. Passing cases pass (waiver with quote, full set).
- AC-12 and AC-14 not rerun: the delta since f3ac6101 touches no agent, SKILL.md or review-brief text. AC-14 holds as recorded; AC-15 is owed, not run.

### adr_lint

`python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since 126efaf06b4d3f06c29d6b071189ed7771c41ee9`, run in the candidate checkout: "29 ADR file(s) checked, 0 legacy", exit 0 (also with `--require 0030`).

### Minimal acceptance script

Run by me exactly as written in a fresh shell (`env -i`, no profile). It needs git, python3 and network access to github.com; it fetches the head into a temp directory. It covers the checker, the lint, the tests, ADR 0030's status and the agent file. It does not run the model: how the director rules (AC-14, AC-12), a live pass 2a run, the decline-check key-line shape (F8) and the first real paseo ideation (AC-15) are not covered.

```bash
# Acceptance script for kc-claude-plugins PR #708 (design director), head e033956e
# Needs: git, python3, network access to github.com. No secret. Run in a fresh bash shell.
set -u
H='##'
W=$(mktemp -d) && cd "$W" && git init -q repo && cd repo \
  && git fetch -q --depth 1 https://github.com/iamcxa/kc-claude-plugins.git e033956e955503fcf81c134ace19d9cc9fd1dd25 \
  && git checkout -q FETCH_HEAD && git log --oneline -1 && R=$PWD && S=$R/kc-dev-flow-2/scripts && cd "$S"
echo "--- step 1: the plugin lint passes with the 15-word budget raise"
python3 -B lint-skills.py; echo "exit=$?"
echo "--- step 2: the two test suites for this change pass"
python3 -B -m unittest test_design_surfaces test_lint_skills 2>&1 | grep -E "^(Ran|OK|FAILED)"
echo "--- step 3: at validation, a waiver kept in an earlier validation report does not satisfy a later one"
V=$W/v; mkdir -p $V/task/design; cd $V
printf 'built screen bytes' > task/design/built-1.png
printf '<html></html>\n' > preview.html
cat > task/design/validation-1.yaml <<'T'
design_review:
  preview: design/built-1.png
  findings:
    - severity: MAJOR
      dimension: hierarchy
      where: built-1.png
      seen: the count is stated twice
      fix: keep one
T
mk() { cat > task.md <<T
---
title: a ui task
profile: pilot
status: validation
---

$H FO alignment

Surfaces: ui
Visible change: a person sees a panel.

$H Design

UI proposal: a panel.
Preview: preview.html

Design review: design/ideation-1.yaml

$H Acceptance criteria

**AC-1**: a.
Verified by: a test.

$H Stage Report: validation

- F1 Behaviour: the count is said twice
$1

$H Stage Report: validation (cycle 2)

- F1 Behaviour: the count is still said twice
$2
T
}
mk "Built screen review: waived 「an earlier cycle's words」" ""
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 4: the same lines kept in both validation reports are accepted"
L='Built screen review: design/validation-1.yaml
Built screen finding 1: F1'
mk "$L" "$L"
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 5: a decline report with an empty evidence is refused"
T=$W/t; mkdir -p $T/task/design; cd $T
printf '<html></html>\n' > preview.html
cat > task.md <<T
---
title: a ui task
profile: pilot
status: ideation
---

$H FO alignment

Surfaces: ui
Visible change: a person sees a panel.

$H Design

UI proposal: a panel.
Preview: preview.html

${H}# Design review

Design review: design/ideation-1.yaml
Design finding 1: declined: the inset matches the shell
Decline check: design/declines-1.yaml

$H Acceptance criteria

**AC-1**: a.
Verified by: a test.
T
cat > task/design/ideation-1.yaml <<'T'
design_review:
  preview: preview.html
  findings:
    - severity: MINOR
      dimension: spacing
      where: after-desktop.png
      seen: tight inset
      fix: widen it
  limitations:
    - the operable preview was not opened
T
cat > task/design/declines-1.yaml <<'T'
design_decline_check:
  adrs_read: none
  rulings:
    - finding: 1
      ruling: upheld
      evidence:
      change: none
T
python3 -B "$S/design_surfaces.py" check task.md; echo "exit=$?"
echo "--- step 6: ADR 0030 is Accepted, its lint passes, and the agent declares sonnet"
grep -A2 '^## Status' "$R"/docs/adr/0030-*.md | tail -1
python3 -B "$S/adr_lint.py" "$R/docs/adr" --require 0030; echo "exit=$?"
grep -E '^(model|reasoning):' "$S/../agents/design-director.md"
```

Observed output (rc 0; the temp directory name differs per run):

```
e033956 fix(kc-dev-flow-2): read the built-screen lines from the current validation report and validate the decline-check root
--- step 1: the plugin lint passes with the 15-word budget raise
PASS: basic frontmatter, declared profile routes, role bindings and package script paths
references/sd/workflow.md: 5389 of 5389 words; no unlisted passage repeats it
Not checked: full Agent Skills conformance or host/workflow behavior
exit=0
--- step 2: the two test suites for this change pass
Ran 210 tests in 18.436s
OK
--- step 3: at validation, a waiver kept in an earlier validation report does not satisfy a later one
task.md: built screen review not run: a ui task with a design review needs a 'Built screen review:' line or a quoted waiver
scope check not run: stage is validation, not ideation
exit=1
--- step 4: the same lines kept in both validation reports are accepted
task.md: design surfaces presentable
built screen review design/validation-1.yaml: 1 findings, 0 upheld declines, 0 decisions in 0 groups
preview: <temp dir>/v/task/design/built-1.png
scope check not run: stage is validation, not ideation
exit=0
--- step 5: a decline report with an empty evidence is refused
task.md: 'design/declines-1.yaml' rules finding 1 without 'evidence'
task.md: declined finding 1 has no ruling in 'design/declines-1.yaml'
scope check not run: no closed backlog approval
exit=1
--- step 6: ADR 0030 is Accepted, its lint passes, and the agent declares sonnet
Accepted
29 ADR file(s) checked, 0 legacy
exit=0
model: sonnet
reasoning: high
```

### Summary

PASSED on e033956e: the Cycle 2 P1 and the three P2 are fixed, each test fails only on its own mutant, ADR 0030 is Accepted, and AC-1 to AC-14 hold. The P1 fix narrows where the built-screen lines and a waiver may sit to the last validation Stage Report, which is stricter than the approved "body or the stage report" and is Deferred risk F9 with a Polish record fix F10; AC-15 stays owed.
