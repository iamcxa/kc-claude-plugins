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

Alignment: needed at ideation; the declared model and whether the helper joins are his, after the measurement and the POC.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Status of inputs: Amendment 1 and the backlog gate resolution (the Captain's 「可以」, 2026-10-22) are the scope. The coordinator's later message relays a peer's three suggestions (`intake/paseo-fo-r1.5-intake-2026-10-22.md`); none is in this design as decided, and each is weighed under `## Unresolved decisions for the Captain`. `## FO alignment` has no `Result:` line; the dispatch carries it (model sonnet, helper dropped), so this design went ahead and the gap is in the stage report for FO to fill before `gate prepare`.

### PRFAQ

**Press line.** From the next kc-dev-flow-2 release, a ui task's design review is run by a named agent, `kc-dev-flow-2:design-director`, on sonnet. The author can no longer close a finding alone: every decline the author proposes is ruled on by the design director against the picture, and the declines it upholds are printed in the gate material for the Captain, who keeps the final say. At validation the same agent looks at screenshots of the built screen.

**FAQ.**

- *Why a named agent, when ADR 0022 chose a `general-purpose` agent and rejected "a new agent"?* ADR 0022 says "Reopen if a bite recurs that the review did not name". The 2026-10-22 measurement (intake) is that bite: on 7 kc-paseo-plugins tasks the review raised 93 findings, the author declined 70, and 10 of the 14 findings of the Captain's later critique had already been raised and declined or deferred. The Captain asked for the role in 「我還是希望開設計總監…」 and ruled 「設計總監照建議」 (Amendment 1).
- *Why sonnet?* Amendment 1 point 1; ADR 0022 D3 measured no gain from opus; the replay below ran on sonnet and the shipped agent is replayed on sonnet (AC-7).
- *Does the director gain authority?* No. It advises and holds no gate. What changes is who may close a finding: not the author alone. An overruled finding leaves three exits (fix, criterion, or a Needs decision that reaches the Captain with both views), so the Captain's final say is intact.
- *What does it not do?* It does not review whole releases or operate a running app at ideation (see D-1 below), and it changes neither the eight dimensions nor the severities (Scope non-goal).
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
    F->>K: ideation gate material
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
| `kc-dev-flow-2/scripts/design_surfaces.py`, `test_design_surfaces.py` | Two checks: the decline check at ideation, the built-screen review at validation. Details below. |
| `kc-dev-flow-2/skills/validation/principles.md` | The screenshot sentence now names the director pass and its line. |
| `kc-dev-flow-2/scripts/lint-skills.py`, `test_lint_skills.py` | `AGENT_MODELS` gains `"design-director": ("sonnet", "high")`; one test like `test_observer_keeps_its_declared_model`. |
| `kc-dev-flow-2/README.md` | One sentence in the roles paragraph (retained document: the role would otherwise be undocumented). |
| `docs/adr/0022-ui-ideation-design-review-binds-design.md` | One Amended paragraph: the named agent is now chosen, on the Captain's 2026-10-22 words; the "13 more words" consequence is replaced by the measured count below. No new ADR number. |

Not changed: `references/sd/workflow.md` (so no word-budget step under ADR 0020), `role_triggers.py` (the director is not a `Reviewer:` call), `pr_watch.py`, `delivery_gate.py`, `skills/ideation/principles.md`, the mod, any extension.

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
5. Output: the summary line gains `; decline check design/declines-1.yaml: 6 upheld, 3 overruled, 2 decisions`, and each upheld decline prints one line `upheld decline <n>: <reason as written>`. FO already includes the checker's output in the gate material, so the Captain's list needs no README rule.

A report is model output saved by the author: the check cannot tell it came from the named agent (same limit ADR 0022 records for the review report).

At validation (`status: validation`, a `Surfaces:` including `ui`, and a `Design review:` line in the body, so tasks ideated before the review existed are not caught): a `Built screen review: design/validation-<N>.yaml` line is required in the body or the stage report, naming a report with the `design_review:` shape whose `preview:` value names a screenshot file present in the task folder; a missing line or file is refused with `built screen review not run`. The 4 of 7 paseo validation reports that said "no screenshot of the candidate screen exists" now fail this check instead of passing on prose. At validation a director finding is not "declined" by anyone: the validator lists a MAJOR as a finding and classifies it by the existing four fields (Material, Deferred risk, Polish, Needs decision); a MINOR is Polish unless those fields say otherwise.

### Replay (prototype outside the repository, before proposing)

Method. The wording above was written to `replay/duty.md` and given to a fresh `general-purpose` agent on `model: sonnet`, one per task, for the 7 kc-paseo-plugins tasks whose last design reports hold the 93 findings the measurement counted (70 declined). Each agent got the task's UI proposal, the author's proposed declines verbatim, the preview pictures the findings cite (copied to a folder with nothing else in it) and the two host declaration files of `@getpaseo/plugin` 0.12.0 (`ui.d.ts`, `react-native.d.ts`). It was not told which findings the Captain's critique later matched, nor given the critique. The recorded dispositions are the baseline arm: no wording, all 70 declines closed by the author. Prompts, raw reports, the findings-and-dispositions dump and the mapping are in `replay/` (`replay/README.md` says how to rerun).

Result over all 70 declines: **31 overruled, 18 decision, 21 upheld.** A second run of three tasks (39 declines) agreed on 35 (90%); every row in the table below got the same ruling in both runs. The 4 disagreements are in rows outside the table. 23 of the 31 overruled rulings cite a prop, slot or `children` of the declaration; 9 of the 18 decisions are one question, "accept a departure from the host's look (own 44px buttons, primary or destructive button, row height)", asked in 7 different tasks. Reported `subagent_tokens`: 619k for the seven runs (77k to 115k per task), 273k for the three repeats.

The Captain's critique rows (the measurement lists the row numbers; the mapping to review findings is mine, `replay/mapping.tsv`):

| Critique row | Review finding and recorded disposition | Ruling (runs 1 and 2) | Reaches |
| --- | --- | --- | --- |
| 1 hidden mode switch | browse-vault-survives #11, declined "today's behaviour" | upheld, upheld | still closed; adjacent variable-row-edit #16 (decision, owner T5) and #11 |
| 2 references cut off | variable-row-edit #18, declined "host input scrolls" | overruled, overruled | a fix, but the change named is the Testing state and failure count, not the cut-off |
| 4 flat picker | variable-row-edit #16, declined "T5 owns it" | decision, decision | a decision whose owner is another task |
| 5 add variable in three steps | variable-row-edit #4, declined "today's host rows" | overruled, overruled | fix: one row through the `children` slot |
| 6 one edit wipes every result | variable-row-edit #1, MAJOR Needs decision | not replayed | already at the Captain; no change |
| 7 no next step | plain-failure-reason #10, browse-vault-survives #7, declined "ruled cause form, ADR 0002" | upheld, upheld | still closed |
| 8 connection card noise | variable-row-edit #3, declined "host chrome" | upheld, upheld | still closed |
| 9a unsaved cue | variable-row-edit #2, MAJOR Needs decision | not replayed | already at the Captain; no change |
| 9b Stop managing beside Save; destructive confirm like Keep | variable-row-edit #12 and #13, declined "host has one style" | overruled, overruled (both) | fix: own section, own danger button in the modal body |
| 10 notes posing as rows | browse-vault-survives #1, declined "no weight control" | overruled, overruled | fix: marker through `children` |
| 12 success grey like a hint | variable-row-edit #7 (upheld), test-results-match-draft #6 (overruled) | upheld; overruled | secondary: failure through the `error` prop; primary stays closed |

Reading. Of the 9 rows that were declined (all but 6 and 9a), **5 reach a fix or a decision** (#4, #5, #9b, #10, #12 by its secondary finding) and **4 stay closed** (#1, #2 in substance, #7, #8). The wording works on one class: a decline that says "the host component has no X" while the declaration offers `children`, `error`, `hint`, `placeholder`, `disabled`, `useToast` or a plugin-drawn part (the plugin's own screen already draws its own field pills, per the variable-row-edit #11 decline text). It does not reach the whole-screen class (#1, #2, #8): there each finding on its own picture "misleads nobody", and the harm is the sum. Row 7 was closed by a real Captain ruling (ADR 0002 fixes the cause text), so "upheld" is arguably right there. Limits of this replay: one project, one run per task (three repeated), rulings graded by me from the `ruling` field, the 10 rows were chosen because a later critique vindicated them (hindsight in the selection, not in the agent), the agent saw pictures and a declaration file, not the running host, and the d.ts says a prop exists, not how the host renders it.

Load. The Captain's list at the ideation gate would have been 21 upheld lines over 7 tasks (1 to 6 per task) and 18 decisions (already Needs-decision lines today), and the authors would have owed 31 fixes or criteria they did not owe. That is the price; AC-7 bounds it. Nine of the decisions are the same question, so D-4 asks for one standing ruling.

### Words FO reads at each lifecycle moment

Counted with `wc -w` on `origin/main` e1f43044 (no `kc-dev-flow-2/` change between cebd0ab9 and e1f43044). Same count method for the candidate; each moment needs the candidate count recomputed at validation.

| Moment | Base (words) | Candidate | Basis |
| --- | --- | --- | --- |
| startup (`references/sd/workflow.md`) | 5374 | 5374 | file not edited; AC-8 diffs it |
| idle on an open PR / idle on a merged PR / after the archive / the merge ask | unchanged text | unchanged | `pr_watch.py`, `delivery_gate.py`, `workflow.md` not edited; `pr_watch.py` runs `check --seed`, which returns before the ui checks |
| ideation gate, ui task (checker output) | 13 measured on two archived paseo tasks, plus the design-review summary line (14 words by the test fixture's form) | + decline-check summary (about 13 words) + one line per upheld decline: **30 to 141 words per task, median 60**, simulated from the author's decline text for the 7 tasks (529 words over 21 lines) | simulation, not a run of the new check |
| validation gate, ui task | 13 (no design lines at that status) | + one summary line (about 14 words) | design |

The ideation gate rises, by design: Amendment 1 asks for the list at the gate. The learning "each moment below its base" applies to a change whose goal is to cut what FO reads; this one adds a Captain-owed list and leaves every other moment unchanged. ADR 0022 recorded "13 more words at the ideation gate of a ui task"; the Amended paragraph replaces that number.

### Batch overlap

Files this design changes: `kc-dev-flow-2/agents/design-director.md`, `kc-dev-flow-2/skills/design-director/SKILL.md` and `review-brief.md` (all new); `skills/ideation/design-review.md`; `skills/validation/principles.md`; `scripts/design_surfaces.py` and `test_design_surfaces.py`; `scripts/lint-skills.py` and `test_lint_skills.py`; `kc-dev-flow-2/README.md`; `docs/adr/0022-ui-ideation-design-review-binds-design.md` (one paragraph; no new ADR number). Read 2026-10-22 from the task files in this state checkout at HEAD ec1a9b6a and from the PR lists in their own overlap tables.

| Other task | Same file or check | Order |
| --- | --- | --- |
| fo-write-checks-parse-top-level (batch 5, ideation) | yes: `design_surfaces.py` (`scope_lines`, one docstring clause) and `test_design_surfaces.py` (`ScopeCheckTests`); mine adds functions near `check_design_review` and edits no docstring | different functions; second to merge rebases; either order |
| new-work-starts-from-a-story-map (batch 5, validation, PR #705) | no: its D2 (`design_surfaces.py`, workflow.md, `lint-skills.py`) was dropped; it edits `skills/ideation/principles.md`, which this design leaves alone | none |
| codex-reader-reads-receipt-marker (merged #693), idle-names-failing-seeds (merged #694) | none: `extensions/codex/`, `pr_watch.py` | none |
| codex-reader-counts-code-review-only (batch 5, validation, PR #702) | none: `extensions/codex/`; it reads `README.md`, edits no line of it | none |
| merge-ask-holds-missing-clauses (batch 5, validation, PR #703) | none: `delivery_gate.py`, ADR 0023 and 0026; its table says `lint-skills.py`, `workflow.md`, every skill unchanged | none |
| agent-reads-governing-adr (batch 5, validation, PR #698) | none: `AGENTS.md`, `CLAUDE.md`, `scripts/adr-path-check.py` | none |
| comment-check-reaches-delivery-gate (ideation, resolved `hold`) | would replace one sentence of `skills/validation/principles.md`; mine replaces the screenshot sentence | adjacent hunks; second rebases |
| override-reaches-gate-and-criteria-wait, amendment-form-check-round3-followups (backlog) | `design_surfaces.py` `check_amendments` | different function; order only if pulled forward |
| design-surfaces-task-dir-crash (backlog) | `design_surfaces.py` `main` and task-dir handling; my new checks resolve the report folder with the same helper as `check_design_review` | if it lands first, mine follows its folder handling |
| release-acceptance, journey-server-host-pilot, kc-decision-log-p1 (other sessions) | no task file in this checkout, so not read; release-acceptance's own listing in other tasks' tables says it edits the README Release-review bullet and runs `lint-skills.py` | README: different paragraph; `lint-skills.py` run is unaffected by one `AGENT_MODELS` line |
| kc-decision-log-cli (done), kc-decision-log-handoff-trial (backlog), pr-review-lite-value-pilot (implementation), journey-canvas-hosted-poc (ideation), read-adr-reporting-rule-followup (validation) | none edits these files: `grep` of each task file for `design_surfaces`, `design-review`, `lint-skills`, `validation/principles`, `agents/` finds only reports that ran `design_surfaces.py check` and kc-decision-log-cli's text on past design reviews. Only the check's verdict could change, and only for a task whose `Surfaces:` include `ui` with a `Design review:` line | none |
| ADR index | amends 0022; merge-ask amends 0023 and 0026; no new number from this task | none |

Recommended order: no hard constraint. If fo-write-checks-parse-top-level merges first, rebase this task's `design_surfaces.py` hunks onto it; release as one `feat(kc-dev-flow-2)` PR with the agent, skill and checks together, because the check refuses declines without the report the skill now asks for.

## Acceptance criteria

**AC-1** The agent exists, declares sonnet, and is bound to its skill. Evidence: at the candidate, `python3 <package>/scripts/lint-skills.py` exits 0 with `design-director` in `AGENT_MODELS`, and `python3 -B -m unittest test_lint_skills` (run in `<package>/scripts`) passes a new case. Falsifier: that case changes `model: sonnet` to `model: inherit` in `agents/design-director.md` and expects "design-director agent: existing sonnet/high policy changed"; deleting `skills/design-director/SKILL.md` must give "missing skills: design-director". Not yet verified.

**AC-2** The brief moves with its eight dimensions and two severities unchanged. Evidence: the blockquote in `origin/main:kc-dev-flow-2/skills/ideation/design-review.md` and the blockquote in `skills/design-director/review-brief.md` compared with `diff` differ only in the one sentence that names screenshots for pass 2, and `design-review.md` no longer carries the blockquote. Falsifier: editing one word of one dimension makes `diff` print it. Not yet verified.

**AC-3** One real ui ideation dispatches the named agent twice and the check passes on its output. Evidence: a ui ideation run on the candidate package for one of the six paseo tasks in `ideation` (the first consumer); its transcript shows two Agent calls with `subagent_type: kc-dev-flow-2:design-director` and none with `general-purpose`; `design/ideation-<N>.yaml` and `design/declines-<N>.yaml` exist; `design_surfaces.py check` exits 0 and prints the upheld lines. Falsifier: the same run on the base package shows `general-purpose` and no `declines-<N>.yaml`. A substring check of `design-review.md` is not offered as proof. Not yet verified.

**AC-4** A declined finding passes only with an `upheld` ruling. Evidence: new cases in `test_design_surfaces.py`, one per refusal 1 to 4 above (no `Decline check:` line; missing ruling; ruling for an undeclined finding; `overruled` or `decision` still declined; `host component` with no `<Name> at <path>:`; two `Decline check:` lines), each asserting the refusal's reason text, plus one passing case. Falsifier: for each refusal, a `mutated(...)` copy of the check with that branch removed makes its case fail (the file's existing mutation pattern); the suite also fails if a case asserts only the exit code. Not yet verified.

**AC-5** The gate material lists every upheld decline, not a count. Evidence: a case with 3 declined findings (2 upheld, 1 overruled, the overruled one redisposed to `fixed:`) asserts the output holds exactly two `upheld decline <n>: <reason>` lines with the author's reasons, and that the summary line counts `2 upheld, 1 overruled, 0 decisions`. Falsifier: a mutant that prints only the count fails the case. Not yet verified.

**AC-6** A ui task cannot reach a passing validation check without a built-screen review. Evidence: cases at `status: validation` for a task with `Surfaces: ui` and a `Design review:` line: no `Built screen review:` line is refused with "built screen review not run"; a line naming a report whose `preview:` file is absent from the task folder is refused; a line with a present screenshot passes; a task with no `Design review:` line (ideated before the review) is not refused; `status: implementation` is not refused. Falsifier: mutants that drop the status gate, the file-exists test or the `Design review:` condition each fail a case. Not yet verified.

**AC-7** The shipped agent, not the prototype, rules as the prototype did on the replay. Evidence: rerun the 7 prompts in `replay/prompts/` with `subagent_type: kc-dev-flow-2:design-director` on the candidate, then compare `ruling` fields with `replay/mapping.tsv`: at least 4 of the 5 rows that reached a fix or decision (#4, #5, #9b, #10, #12) do again, and between 10 and 35 of the 70 declines are upheld. The bounds are a margin around the measured 21 upheld, not a measured range; run-to-run agreement was 90% on 39 declines. Falsifier: an agent given the same prompts without the duty wording, or one that upholds all 70 or none, falls outside the bounds. Not yet verified; the prototype result is the 31/18/21 split above.

**AC-8** No FO-read text outside the ui gate changes. Evidence: `git diff <base> <candidate> --stat -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/scripts/pr_watch.py kc-dev-flow-2/scripts/delivery_gate.py kc-dev-flow-2/scripts/role_triggers.py` prints nothing, and `wc -w` of `workflow.md` at the candidate is 5374; `lint-skills.py` passes with `WORKFLOW_BUDGET_STEPS` unchanged. The ideation-gate and validation-gate counts in the table above are recomputed from a real run of the candidate check on the AC-3 task and reported next to the simulated ones. Falsifier: any edit to those files, or a lint budget error. Not yet verified.

**AC-9** The retained documents match the new role. Evidence: `README.md` names the role, its model and that it advises; ADR 0022 carries an Amended paragraph naming the Captain's 2026-10-22 words and replacing the "13 more words" consequence; `python3 <package>/scripts/adr_lint.py docs/adr --since <base>` exits 0; `python3 <package>/scripts/doc_impact.py <base> <candidate>` reports no unread affected document. Falsifier: `adr_lint.py` exits 1 on a malformed Amended paragraph. Not yet verified.

## Unresolved decisions for the Captain

These come from the coordinator's relayed peer suggestions (D-1 to D-3, none approved scope) and from the replay (D-4). Each is outside Amendment 1, so the design above does not depend on any of them.

**D-1 — A release-level, operated, whole-screen design review when two or more ui tasks of one release change the same screen (the peer's suggestion 1).** Recommendation: not now; run it once by hand first, on the next release that has two or more ui tasks on one screen, with this agent and a running app, and decide from what it finds. Reasons: the replay shows the per-task wording leaves rows #1, #2 and #8 closed, so the gap is real; but nobody has run such a review as a stage, and the measurement found two critique rows outside any brief (#3 needs a running app, #13 a screen never pictured); and release review is already being designed by the release-acceptance task (README Release-review bullet), so a second place to define it would collide. What gets worse under this recommendation: the next release with a screen-level defect can again pass every task gate, and the Captain sees it only by using the screen.

**D-2 — Ideation and validation gate presentations show the Captain screenshots, not only text (suggestion 2).** Recommendation: do not add an FO rule now; the checker will already print the `Preview:` path and the screenshot paths it checked, which costs no README words. An FO rule to show pictures needs a `workflow.md` raise, which ADR 0020 allows only with the Captain's quoted words and the moment FO reads it. What gets worse: the gate stays text, so the Captain looks at pictures only if he opens the printed paths.

**D-3 — Previews show the whole page around the change, at desktop and narrow widths (suggestion 3).** Recommendation: leave it out of this task. It changes what `skills/ideation/principles.md` asks an author to draw, a file other tasks touch, and the brief's dimension 8 already lists size and theme combinations as findings. Pass 2 sees the built whole screen at validation. What gets worse: fragment previews keep hiding cross-part effects at ideation, such as Browse vault changing rows in another card, until validation.

**D-4 — One standing ruling for "depart from the host's look" decisions.** 9 of the 18 `decision` rulings in the replay were this single question (own 44px phone buttons, a primary or destructive button, one row height), asked again in 7 tasks. Recommendation: the Captain rules once per kind when it first appears, FO records it as project learning, and the checker prints decision lines grouped by owner so the same question shows once per gate. What gets worse: a standing ruling is made before seeing each screen, and a later screen may deserve a different answer; until he rules, each task asks again. The grouping of printed lines is a small check change that is not in the ACs above; if the Captain wants it, it becomes AC-10.

## Stage Report: ideation

- DONE: Design the kc-dev-flow-2:design-director agent and skill per Amendment 1 and the backlog gate resolution: duty wording (owns the open design decisions; every decline the author proposes is checked against the picture by the design director; upheld declines listed at the ideation gate for the Captain, who keeps the final say), two passes (pictures at ideation, built-screen screenshots at validation, with what only the running screen can settle handed forward), a host-component decline checked against that component, model sonnet; read intake/ui-design-review-measurement-2026-10-22.md and intake/design-role-research-2026-10-22.md; prototype the duty wording outside the repository and replay it on the 10 already-raised kc-paseo-plugins findings (mapping in the measurement intake) to show whether each would now reach the Captain or a fix, before proposing it
  Design above; chain checked (Spacedock: no role; kc-dev-flow-2 0.27.0 and origin/main e1f43044: observer, chief-engineer, engineering-reviewer are the pattern, ADR 0022 chose `general-purpose` and says reopen on a recurring bite; no sibling design role). Replay in `replay/`: 70 declines, 31 overruled, 18 decision, 21 upheld; 5 of 9 declined critique rows reach a fix or decision, 4 stay closed; run 2 agreed on 35 of 39.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, fo-write-checks-parse-top-level, idle-names-failing-seeds, agent-reads-governing-adr) and live task of other sessions (kc-decision-log-p1, kc-decision-log-cli, kc-decision-log-handoff-trial, pr-review-lite-value-pilot, release-acceptance, journey-canvas-hosted-poc, journey-server-host-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Done above; three of the other sessions' tasks (release-acceptance, journey-server-host-pilot, kc-decision-log-p1) have no task file in this checkout and were not read.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Table above: startup 5374 to 5374; the idle, merge-ask moments unchanged by diff; ideation gate rises by 30 to 141 words per ui task (simulated, not a run); validation gate by about 14. AC-8 recomputes from a real run.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-9 each carry an evidence clause and a falsifier; all are "not yet verified" because nothing is built. D-1 to D-4 under `## Unresolved decisions for the Captain`.

### Summary

The design adds one agent, one skill and two checks: a declined finding passes only with an `upheld` ruling that the gate prints, and a ui task needs a built-screen review at validation. The replay shows the wording reaches the "host component has no X" class of declines and not the whole-screen class, so the peer's release-level review is left to the Captain (D-1) with a recommendation to try it once by hand. Needs FO: `## FO alignment` has no `Result:` line for this task (the dispatch carried the result); fill it before `gate prepare`. `design_surfaces.py check` (package 0.27.0) printed "design-director-runs-ui-design-review.md: design surfaces presentable", exit 0. The Scope check printed nothing further because this task's backlog approval and Amendment 1 are the baseline.
