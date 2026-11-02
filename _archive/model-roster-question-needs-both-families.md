---
title: Model roster question asks only when Paseo, Codex and Claude are all available, and offers Claude models
status: done
variant: kc-dev-flow-2
profile: pilot
gates:
    version: 1
    records:
        - id: gate:model-roster-question-needs-both-families:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:model-roster-question-needs-both-families-backlog-1
              briefing:
                id: briefing:model-roster-question-needs-both-families:backlog:attempt-1:revision-1
                digest: sha256:b8a4d203d360d9ab93d9279689d80d5330565e4842f23a72ca3caf3d5a1d5e25
                room-ref: ./model-roster-question-needs-both-families/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:model-roster-question-needs-both-families:backlog:1
                briefing: briefing:model-roster-question-needs-both-families:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-01T17:47:32.607771Z"
                decision: approve
                reason: The Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering the batch 12 sitting 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」; approves Pilot, this outcome and these bounds, with the stated change.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:model-roster-question-needs-both-families:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:model-roster-question-needs-both-families-ideation-1
              briefing:
                id: briefing:model-roster-question-needs-both-families:ideation:attempt-1:revision-1
                digest: sha256:4f7daba3d0826bf70b5a617c5a9423d0bbc2a906f97720df749fa733ca51b30c
                room-ref: ./model-roster-question-needs-both-families/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:model-roster-question-needs-both-families:ideation:1
                briefing: briefing:model-roster-question-needs-both-families:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-02T03:30:47.440487Z"
                decision: revise
                reason: 'The Captain 「可以」 (chat, 2026-11-02), answering 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」; accepts the direction and asks: D1 Opus only; D2 yes, a Claude worker hands publication to FO as worker-completion-reaches-fo-on-paseo owns; D3 yes; D4 chief-engineer and engineering-reviewer differ from the implementation workers, worded by special-roles-follow-the-model-table; AC-6 also proves completion reaches FO; order after the completion task.'
            - id: gate-attempt:model-roster-question-needs-both-families-ideation-2
              briefing:
                id: briefing:model-roster-question-needs-both-families:ideation:attempt-2:revision-1
                digest: sha256:fff8879d3a9f22e5258141d28dddbf88a91ae476df5d1a16a235deeea091fc2b
                room-ref: ./model-roster-question-needs-both-families/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:model-roster-question-needs-both-families:ideation:2
                briefing: briefing:model-roster-question-needs-both-families:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-11-02T04:29:44.687244Z"
                decision: approve
                reason: The Captain 「照建議」 (chat, 2026-11-02), answering 「決定：五張設計進實作、Gemini 這張停在這裡，四個決定都照建議嗎？要改哪件直接說。」; accepts the recommendations stated in that sitting, including D5 for the roster and D1 and D2 for completion.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:model-roster-question-needs-both-families:validation
          stage: validation
          attempts:
            - id: gate-attempt:model-roster-question-needs-both-families-validation-1
              briefing:
                id: briefing:model-roster-question-needs-both-families:validation:attempt-1:revision-1
                digest: sha256:ceb91efd7616158e8786c031754cd1f4ebafbe680e55fff7d22a2130ff5881c4
                room-ref: ./model-roster-question-needs-both-families/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:model-roster-question-needs-both-families:validation:1
                briefing: briefing:model-roster-question-needs-both-families:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-02T10:10:37.602055Z"
                decision: approve
                reason: 'The Captain 「准」 (chat, 2026-11-03), answering 「決定：合併 #765，並接受不修那項縮排問題，可以嗎？」.'
              application:
                target-stage: done
                state: consumed
started: 2026-11-02T04:56:19Z
worktree: .worktrees/spacedock-ensign-model-roster-question-needs-both-families
pr: pr-merge:765
verdict: PASSED
completed: 2026-11-02T10:16:43Z
archived: 2026-11-02T10:16:43Z
---

## Scope

- Source: the Captain, chat 2026-11-02: 「應該預設是用 claude 做 fo 時，就是都預設 claude 家族，codex 亦同，是只有使用者提出時才要寫入 .dev2/model-roster.json」, 「主動詢問不必拿掉，但是應該是條件式的，也就是必須要是有 paseo + codex +cladue 都存在時才可以用」, 「構思改用 opus high」 and 「開，可以」. Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」.
- Bite: 0.34.0 asks with Codex alone and its roster rejects Opus, so the Captain's chosen ideation model cannot be recorded (`model_roster.py`, MODELS and the provider check, read 2026-11-02).
- Consumer: this repository's stage dispatches, through Draft PR iamcxa/kc-claude-plugins#762.
- The question's condition adds Claude available to the existing paseo listed and Codex available; otherwise nothing is asked or written and workers follow the FO's family.
- The recommended set becomes ideation Opus high, implementation Sol xhigh, validation Astra xhigh. FO verified on 2026-11-02 with Paseo list_models that claude-opus-5-5 offers high and that gpt-6.1-sol and gpt-6-astra offer xhigh.
- The roster accepts Claude and Opus. `max` and `ultra` stay accepted and are not recommended; the recommendation stops at xhigh.
- #762 is updated to that set after release, then asked for merge. The interim directive to dispatch on Sol and Astra ends for repositories with no roster.
- Upstream first: `references/model-roster.md`, `references/model-roster-defaults.json`, `scripts/model_roster.py`, `references/sd/adoption.md`; Paseo's list_models.

## Non-goals

- Native dispatch model passthrough (spacedock-dev/spacedock#845); capacity automation; usage measurement.

## Budget

- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition

- A repository lacking any of the three asks nothing and writes nothing; one with all three is asked once; a roster naming Opus resolves and dispatches a real Claude ideation worker with the requested settings. If Paseo cannot apply them, stop and return to FO.

## FO alignment

Alignment: needed before ideation; the scope is the Captain's ruling.
Result: aligned at backlog: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

### PRFAQ

**Proposition.** After this release, kc-dev-flow-2 asks about stage worker models only in a repository whose workflow lists the Paseo extension and whose Paseo host has both Codex and Claude available. Everywhere else it asks nothing and writes nothing, and workers follow the family of the First Officer (FO, the session that dispatches workers). The offered set becomes ideation Opus/high on Claude, implementation Sol/xhigh and validation Astra/xhigh on Codex, and the committed roster file (`.dev2/model-roster.json`) can name it.

**FAQ**

- *Who is asked?* Whoever runs adoption or the introducing sync, once, with all three present and no roster yet. Existing rosters are preserved.
- *Why a script for the condition?* 0.34.0 holds the condition as prose only, so no test can exercise it. `model_roster.py question` reads the workflow frontmatter, the roster path and the output of `paseo provider ls --json`. A missing Paseo gives empty input, which means ask nothing.
- *Does `xhigh` become a cap?* No. The Captain's ruling: 「不用寫了就報錯，接受 `max` 和 `ultra`沒關係」. The recommendation stops at `xhigh`; `max` and `ultra` stay accepted.
- *What does `ultra` mean on Claude?* Paseo has no Claude `ultra`; it lists `ultracode`. The resolver emits the Paseo option id, so a Claude `ultra` row launches `ultracode`. The Captain ruled yes (D3).
- *Who publishes a Claude worker's branch, and how does FO hear it finished?* FO publishes, as for a Codex worker, and the completion route is the one in worker-completion-reaches-fo-on-paseo (D2). This task lands after it and adds neither rule.
- *Is a mixed roster more diverse?* No claim. The `family` flag stays informational. It now names both families, because at 0.34.0 it says `same-family: openai` whenever tuples are present, which would be false once Claude rows exist.

```mermaid
flowchart TD
  A[FO at adoption or introducing sync] --> B[paseo provider ls --json piped to model_roster.py question]
  B --> C{paseo listed, codex and claude available, no roster}
  C -- no --> D[Ask nothing, write nothing; workers follow FO family]
  C -- yes --> E[FO shows the recommended set: Accept or Customize]
  E -- cancel, empty or silence --> D
  E -- Accept or Customize --> F[Reviewed commit of .dev2/model-roster.json]
  G[FO at stage launch] --> H[model_roster.py resolve]
  H -- exit 1: invalid or unsupported --> I[Return to FO, no fallback]
  H -- exit 0: source readme-default --> D
  H -- exit 0: source repository --> J[FO spawns through Paseo with provider, model and thinking_option_id]
  J --> K{Child runtime evidence matches the row}
  K -- no --> I
  K -- yes --> L[Worker runs the stage]
  L --> M[Completion reaches FO by the completion task's route]
  M --> N[FO publishes any candidate branch]
```

### Chain checked

- Spacedock 0.27.3: native dispatch maps `model` to `Agent()` only on Claude (`claude-fo-dispatch.md`), and Codex records a thread-inherited model when the helper emits null (`codex-first-officer-runtime.md`). No stage-model question exists there, so nothing to reuse. spacedock-dev/spacedock#845 stays a non-goal.
- kc-dev-flow-2 at origin/main 146727de (version 0.34.0): `model_roster.py`, `model-roster.md`, `model-roster-defaults.json`, `sd/adoption.md` and `extensions/paseo/EXTENSION.md` own this. The design extends them and replaces nothing.
- Adopters: `gh api repos/<repo>/contents/.dev2/model-roster.json` returns 404 for iamcxa/qnow (`main` and `next`), spacedock-dev/subspace-relay and spacedock-dev/subspace-web (2026-11-02), so no sibling has a roster to borrow or to migrate. No adopter practice was used as the contract.
- Paseo's own surface, read 2026-11-02 through `list_providers`, `list_models` and `paseo provider ls --help` (paseo 0.14.0). The MCP and CLI shapes differ (`id` and boolean `enabled` against `provider` and `"Enabled"`), so `question` takes the CLI JSON only.
- ADRs read: 0047 (this roster; it records the Codex-only set and defers other providers) and 0042 (Paseo Codex workers hand publication to FO). `git grep 'Override:'` in the state checkout shows no past ruling on rosters or models.

### Observations, 2026-11-02

Bite reproduced: a committed roster with ideation `claude`/`claude-opus-5-5`/`high`, resolved by the 0.34.0 script, exits 1 with `stages.ideation.provider: expected codex`.

A real Claude child takes Opus high through Paseo. Three no-tool children, created with `create_agent` in `plan` mode, then killed:

| Requested `thinkingOptionId` | Process argument | Transcript `model` | Transcript `perTurnEffort` |
|---|---|---|---|
| `high` | `--effort high --model claude-opus-5-5` | `claude-opus-5-5` | `high` |
| `low` (control) | `--effort low --model claude-opus-5-5` | `claude-opus-5-5` | `low` |
| `ultracode` | `--effort xhigh --model claude-opus-5-5` | `claude-opus-5-5` | `xhigh`, plus a transcript reminder that ultracode is on and token cost is not a constraint |

The control shows the evidence discriminates. Paseo's `effectiveThinkingOptionId` only echoes the request, so it does not count as evidence.

`auto` mode: this ideation worker is itself a Claude child FO spawned through Paseo; its process shows `--effort high --model claude-opus-5-5 --permission-mode auto`. It was not launched through the resolver; AC-6 owes that. A `bypassPermissions` spawn from this `auto` session was refused by the host's classifier as an unsafe agent, so the route names `auto`.

The build disagrees with a roster row on the template's model. `spacedock dispatch build` on a disposable copy of this workflow's README (0.27.3, 2026-11-02): `--host claude` emits `model: sonnet` and the bootstrap `Skill(skill="spacedock:ensign")`; `--host codex` emits `model: null` and `$spacedock:ensign`. No package text names `--host` (`git grep -- --host` in `references` and `extensions`, origin/main 146727de). See D5.

Not exercised: a child at Sol/xhigh or Astra/xhigh launched from the new set, and any completion reaching FO on the landed route (AC-6). A Claude child publishing is no longer asked of anyone (D2).

### What the design changes

1. `kc-dev-flow-2/scripts/model_roster.py`
   - `MODELS` becomes a provider-to-models table: `codex`: `gpt-6.1-sol`, `gpt-6-astra`; `claude`: `claude-opus-5-5`. `validate` refuses an unknown provider and a model on the wrong provider. The six efforts are unchanged on both.
   - `resolve` output gains `thinking_option_id`, null when absent, otherwise the row's effort, except Claude `ultra`, which becomes `ultracode`. The tuple keeps the written value.
   - `author` accepts a `Roster:` header on either provider. The legacy `Model:` pattern stays Codex-only, so a Claude author has evidence only through the `Roster:` header.
   - `family` becomes `same-family: <openai|anthropic>` when the validator and all authors share a provider, `different-family` otherwise, and stays `unverified` as today when a tuple is missing.
   - New subcommand `question --code-root --readme --providers -`: exit 0 prints `ask`; exit 3 prints `skip: <reason>` naming the first missing condition; exit 1 on a malformed request. It writes nothing. It reads frontmatter with the package's existing reader.
   - The comment citing ADR 0047 moves to the new ADR's path.
2. `kc-dev-flow-2/references/model-roster-defaults.json`: ideation `claude`/`claude-opus-5-5`/`high`, implementation `codex`/`gpt-6.1-sol`/`xhigh`, validation `codex`/`gpt-6-astra`/`xhigh`, each host `paseo`.
3. `kc-dev-flow-2/references/model-roster.md`: the condition sentence becomes the `question` command plus "Ask only on exit 0"; the quoted question shows the new set; the supported-tuple sentence gains Claude and "`max` and `ultra` are accepted, not recommended; Claude's `ultra` is Paseo's `ultracode`, a multi-agent mode"; absence says workers follow FO's family; "existing Codex route" becomes the row provider's route; the launch passes `thinking_option_id`; a new sentence, "A `claude` row spawns in `auto` mode."; Claude child evidence is named as the transcript's `model` and `perTurnEffort`; the family sentence covers both.
4. `kc-dev-flow-2/references/sd/adoption.md` § Before activation: the condition names Codex and Claude.
5. `kc-dev-flow-2/extensions/paseo/EXTENSION.md`: no change here. Under D2, worker-completion-reaches-fo-on-paseo owns the Claude handoff sentence and any widening of ADR 0042. The `auto` clause moved to item 3, because that task's Scope does not name a mode.
6. `kc-dev-flow-2/scripts/test_sd_dispatch.py`:
   - `roster-question-prerequisites` and `roster-adoption-prerequisites` pin the old sentence; both change, with their mutation swaps.
   - `("provider", "claude")` in the malformed list flips to a refused pairing (Claude with `gpt-6-astra`) and an unknown provider.
   - The history replay (`history = {`) asserts `data["stages"][stage] == expected` against the defaults file at Astra/high; it moves to an explicit batch-9 fixture so the new defaults do not rewrite history.
   - New cases for AC-1 to AC-5.
7. New ADR, short title "Stage roster question needs Codex and Claude and offers Opus", number reserved by FO at implementation dispatch. Words: the Captain's 「主動詢問不必拿掉，但是應該是條件式的，也就是必須要是有 paseo + codex +cladue 都存在時才可以用」, 「構思改用 opus high」 and 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02). It restates what stays from 0047 (explicit answer, reviewed commit, read-only resolve, absence keeps README behavior), leaves ADR 0042 to the completion task, and sets 0047's Status to `Superseded by NNNN`, the form `read-adr` follows. Protects: `model_roster.py`, the absent-file return.

Not changed: `references/sd/workflow.md`, so no `WORKFLOW_BUDGET_STEPS` step and no adopter README sync (D4's wording is special-roles-follow-the-model-table's edit there); `extensions/paseo/EXTENSION.md`; `scripts/dispatch_records.py`; `agents/*.md`; `scripts/role_triggers.py`.

Why a script is needed (existing-code check): the bite shows the resolver refuses the row, and the condition has no executable seam today. Without `question`, AC-1 could only pin a sentence, which proves wording rather than behaviour. Cost is one subcommand and about 25 more words at adoption.

### After the package PR

Package PR, then release, then FO updates Draft PR iamcxa/kc-claude-plugins#762: `.dev2/model-roster.json` to the new rows, `selected_from` to the version actually released, `decision` to the 2026-11-02 ruling, then asks the Captain to merge. #762 cannot go first: the released resolver refuses its Opus row until this ships. The interim directive 「接下來派工結束後新的派工盡量用 sol / astra」 lives only in chat and task records (no hit in `docs/dev2/README.md` or `_mods`, 2026-11-02), so ending it changes no file; FO stops applying it where no roster exists.

### Words FO reads at each moment

Whitespace split of the proposed text against origin/main 146727de. The first version's draft was deleted, so the revised rows add the counted new sentence to its counts: `wc -w` gives 7 for the `auto` sentence and 25 for D5's text.

| Moment | What FO reads | Before | After | Change |
|---|---|---|---|---|
| Startup, idle on an open or merged PR, archive, merge | `references/sd/workflow.md` | 5781 | 5781 | 0 |
| Adoption or introducing sync | `sd/adoption.md` | 2242 | 2245 | +3 |
| Adoption or introducing sync | `model-roster.md` § Adoption and introducing sync | 210 | 261 | +51 |
| Adoption or introducing sync | `question` output | 0 | 1 to about 10 | new, one line |
| Stage launch, any repository | `model-roster.md` § Stage launch or continuation | 421 | 451 | +30 |
| Stage launch, roster present | `resolve` JSON | one object | one more key | +1 key |
| Stage launch, `paseo` listed | `extensions/paseo/EXTENSION.md` | 713 | 713 from this task | 0; the completion task's edit is counted there |

FO reads the whole `model-roster.md` when it opens it, so a stage launch costs 634 to 715 words, +81, or 740, +106, under D5. No moment that runs without a roster question or a stage launch changes. No word budget covers these files, so no raise is requested. Other tasks' additions to `model-roster.md` (the `## Model table`) are counted in their files.

### Captain's rulings on this design

Gate of 2026-11-02, the Captain 「可以」, with the asks in the ideation resolution's reason.

- **D1.** Opus only. A Claude row naming another model exits 1. A repository wanting Sonnet/high returns to FO until one string is added.
- **D2.** Yes. A Claude worker hands publication to FO, as worker-completion-reaches-fo-on-paseo owns.
- **D3.** Yes. Claude `ultra` launches Paseo's `ultracode`. Its spend was not measured.
- **D4.** Chief-engineer and engineering-reviewer differ from the implementation workers, worded by special-roles-follow-the-model-table.

### Beyond the asks, for the Captain

One item goes beyond the asks. It is named here and is not adopted in the design or in AC-1 to AC-10.

- **D5. Does stage launch say to build with `--host` set to the row's provider?** Recommended: yes, adding to `model-roster.md` § Stage launch: "Build with `--host` set to the row's provider. A generated Claude alias naming the row's model family, such as `opus` for `claude-opus-5-5`, is no conflict." Without it the recommended set cannot launch by the written route. A generated `sonnet` from a Claude FO conflicts with all three rows, and § Stage launch returns a conflict to FO. A Codex FO would give the Claude row the Codex bootstrap, `$spacedock:ensign`. What gets worse: 25 more words at every stage launch; this task must land after special-roles-follow-the-model-table so the Opus row builds as `opus`; and a customized Claude implementation row still returns to FO while the template says `sonnet`. If the answer is no, AC-6 stops at launch and returns to FO under Stop condition, and AC-11 drops.

### Batch overlap

| Task | State | Same file or check | Effect |
|---|---|---|---|
| worker-completion-reaches-fo-on-paseo | ideation, no design | `extensions/paseo/EXTENSION.md`, which it owns and this task no longer edits; ADR index; possibly `model-roster.md` | this task lands after it; AC-6 needs its route |
| special-roles-follow-the-model-table | ideation, revise | `references/model-roster.md`, a new section; ADR index; its table values match the recommended set; its template `model: opus` feeds D5; it owns D4's sentence in `workflow.md` | rebase `model-roster.md`; order below |
| second-round-prompts-a-step-back | ideation | none: `role_triggers.py`, `pr_watch.py`, the mod | none |
| validation-gate-requires-the-question-check | ideation | ADR index only, per its own overlap section; this task leaves `workflow.md` alone | none beyond the reserved number |
| picky-reviewers-may-run-on-gemini | ideation, no design | none in Scope: the release-acceptance extension and `release_acceptance.py`; its choice stays out of the model roster | none |
| adoption-asks-which-extensions | ideation | `number_guards.py` `frontmatter` becomes a wrapper over `frontmatter_text`; `question` would call that reader. Its files name no `adoption.md` or roster edit. ADR index | signature kept, either order works; re-run tests after the second lands |
| adr-required-statement | validation | `sd/adoption.md`, § Captain rulings ledger, a different section; ADR index | no text conflict; the number comes from FO's reservation |
| adr-silent-undo-probe | ideation | none (`grep` for these files, no hit) | none |
| comment-check-reaches-delivery-gate | ideation | none: `delivery_gate.py`, its tests, validation principles | none |
| journey-canvas-hosted-poc | ideation | none (`grep`, no hit) | none |
| journey-server-host-pilot | validation | none (`grep -r` of its folder, no hit) | none |
| ops-inbox-r1-setup-and-isolation | implementation | ADR index, per validation-gate-requires-the-question-check's overlap section; no file hit | reserved number |
| pr-review-lite-value-pilot | implementation | none (`grep`, no hit for these files) | none |

Tasks with no design have no final file list yet, so those rows read Scope as of 2026-11-02.

Recommended order: worker-completion-reaches-fo-on-paseo, as the Captain ruled, then special-roles-follow-the-model-table if D5 is yes, because the Opus row needs the template's `opus`; then this task; then #762 after this task's release. If D5 is no, special-roles may land either side. This replaces this design's earlier order. If the completion task stops without a route, this task holds and returns to FO.

## Acceptance criteria

**AC-1** `question` decides ask or skip from the three conditions and writes nothing.
Verified by: `test_sd_dispatch.py` runs the subcommand as a subprocess across all eight combinations of `paseo` listed, `codex` available and `claude` available, using `paseo provider ls --json` shaped input, plus an existing roster, empty input and a provider with status `unavailable`. Only all three with no roster exits 0; a file manifest of the fixture is identical before and after. Falsifier: dropping the `claude` check makes the Codex-only case exit 0 and fails the test.

**AC-2** The roster accepts Claude with Opus, refuses wrong pairings and has no effort cap.
Verified by: subprocess `resolve` on committed fixtures. `claude`/`claude-opus-5-5` resolves at each of the six efforts, and `gpt-6.1-sol` and `gpt-6-astra` at `max` and `ultra`. Claude with a `gpt-` model and Codex with `claude-opus-5-5` exit 1 naming the field. Falsifier: a flat model list, or an `xhigh` cap, fails a case. At base the Opus row exits 1 (observed 2026-11-02).

**AC-3** The recommended set matches the Captain's ruling everywhere it is shown.
Verified by: a test reads `model-roster-defaults.json` and asserts the three rows in Scope, resolves them from a committed copy, and asserts the model and effort of each row appear in the quoted question in `model-roster.md`. No recommended effort is `max` or `ultra`. Falsifier: changing one value in either file fails it.

**AC-4** `resolve` emits the Paseo option id for each row.
Verified by: a test asserts `thinking_option_id` equals the effort on every row except Claude `ultra`, which is `ultracode`, is null on absence, and that the tuple keeps `ultra`. Each emitted id is in Paseo's `list_models` for that model at the run's date, recorded by the implementer. Falsifier: passing the effort through unmapped fails the Claude `ultra` case.

**AC-5** `family` tells the truth for both providers.
Verified by: `resolve --stage validation --author-record` with Codex validator and Codex author gives `same-family: openai`, Claude and Claude gives `same-family: anthropic`, Codex validator and Claude author gives `different-family`, and an unknown author stays `unverified`. A `Roster:` header with provider `claude` parses to a tuple and passes `dispatch_records.py --names`. Falsifier: keeping the fixed `same-family: openai` fails the mixed case.

**AC-6** A roster naming Opus resolves and dispatches a real Claude ideation worker with the requested settings.
Verified by: on the candidate package, a committed fixture roster with the recommended set is resolved, FO or the validator spawns a real Claude child through Paseo in `auto` mode with the emitted provider, model and `thinking_option_id`, and the record gives its process arguments and its transcript's `model` and `perTurnEffort`, next to a control child at `low`. The same run spawns a real child at Sol/xhigh and at Astra/xhigh and records that provider's runtime evidence. Paseo's echo and the worker's own statement do not count. Each of the three requested children also ends by the route worker-completion-reaches-fo-on-paseo landed: the spawning session, standing for FO, records the inbound message or finish notification naming the child's agent id and later than the child's last turn, and the child's transcript shows no refused send and no improvised second route. `git merge-base --is-ancestor` shows the candidate's base contains that task's merge commit. Falsifiers: a control reading the same as the requested child voids the run; a child that finishes with no inbound record at the spawner fails it, as the batch 12 route `paseo agent run --no-wait` did. If Paseo cannot apply a row, stop and return to FO, per Stop condition.

**AC-7** Absence keeps README behavior and the text says workers follow FO's family.
Verified by: the existing absent-roster cases still pass unchanged, `resolve` on a repository with no roster gives `source: readme-default` with `thinking_option_id` null and an identical file manifest, and the updated mutation specs for `model-roster.md` and `sd/adoption.md` fail when the condition or the follow sentence is removed.

**AC-8** The ruling lands as an ADR and 0047 points to it.
Verified by: the package's ADR lint exits 0 on `docs/adr`, 0047's Status is `Superseded by NNNN`, and the new record carries the Captain's words above and the rules kept from 0047. The comment in `model_roster.py` cites a file that exists. Falsifier: leaving 0047 `Accepted` means two records state different recommended sets, and a reader following `read-adr` lands on the old one.

**AC-9** Package gates stay green and the workflow text does not change.
Verified by: `git diff --stat origin/main -- kc-dev-flow-2/references/sd/workflow.md` is empty; `python3 kc-dev-flow-2/scripts/lint-skills.py`, `test_sd_dispatch.py` and the release parity check exit 0. Falsifier: any `workflow.md` edit shows in the diff and trips the budget lint.

**AC-10** After release, #762 carries the set from the released package. Owed by FO after delivery, not by the candidate's validation.
Verified by: after the release tag exists, the released `model_roster.py resolve` on #762's head returns the three rows with source `repository`, and `selected_from` equals the published version. FO then asks the Captain to merge. Falsifier: a predicted version, or running against an unreleased script, voids it.

**AC-11** Under D5, each recommended row builds on its provider's host with no conflict. Verified by: `spacedock dispatch build --host <row provider>` on a disposable copy of the candidate's template emits `opus` and the `Skill(` bootstrap for ideation, and `null` and the `$spacedock:ensign` bootstrap for implementation and validation. A case in `test_sd_dispatch.py` pins the two sentences through a mutation spec. Falsifier: leaving out `--host` on a Claude host emits `sonnet` for implementation, as observed 2026-11-02.

## Number guards

ADR: 0050

## Captain amendments

### Amendment 1 — 2026-11-02, chat
Captain: 「照建議」 (chat, 2026-11-02)
Asked: 「決定：四件事都照建議嗎？要改哪件直接說。」, which FO had stated as: 「修這兩個 bug，在原本的票裡修」 and 「#765、#767 的條件不放寬，等前面合併後再驗」
Supersedes: none

### Amendment 2 — 2026-11-02, chat
Captain: 「可以」 (chat, 2026-11-02)
Asked: 「決定：#765 改成共用解析、重跑四個真實代理，然後重新驗證，可以嗎？」, which FO had stated as: 「做一個共用的解析函式，涵蓋單行、多行、引號和註解，兩個工具都用它，並把這些寫法都列成測試。」
Supersedes: none

## Stage Report: ideation

- DONE: A design for this task's Scope: the condition, the recommended set and the accepted models; verify a real Claude child takes Opus high through Paseo before relying on it
  `## Design`. Real no-tool children 2026-11-02: `high` ran `--effort high` with transcript `perTurnEffort` high, the `low` control ran `--effort low`, both `claude-opus-5-5`.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (model-roster-question-needs-both-families, second-round-prompts-a-step-back, validation-gate-requires-the-question-check, special-roles-follow-the-model-table) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Files are listed under `### What the design changes`; the table ends in `Recommended order:`. Real contacts: special-roles (values, D4) and the `number_guards.py` reader.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: `workflow.md` 5781 unchanged; `model-roster.md` 634 to 708; `adoption.md` +3; `EXTENSION.md` +13. Counted on drafted text in a scratch folder, since deleted.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Ten criteria and D1 to D4. `design_surfaces.py check`: "design surfaces presentable", exit 0.
- DONE: AC-1 evidence: not yet verified; future test. Base holds the condition as prose only.
  `question` subcommand does not exist yet.
- DONE: AC-2 evidence: base half observed; candidate half not yet verified.
  0.34.0 `resolve` on an Opus row exits 1, `stages.ideation.provider: expected codex`, 2026-11-02.
- DONE: AC-3 evidence: not yet verified; future test. FO's `list_models` read in Scope and mine agree the three models offer the efforts.
  `list_models` for `claude` and `codex` read 2026-11-02.
- DONE: AC-4 evidence: mapping observed by probe; emission not yet verified.
  `ultracode` is listed for `claude-opus-5-5`; the child ran `--effort xhigh` with the ultracode reminder.
- DONE: AC-5 evidence: not yet verified; future test.
  Base fixes `same-family: openai` in `resolve`, read at origin/main.
- DONE: AC-6 evidence: settings observed on probes in `plan` mode and on this worker in `auto` mode; the resolver-driven run is not yet verified.
  Table under `### Observations, 2026-11-02`.
- DONE: AC-7 evidence: not yet verified on the candidate; base absent-roster cases exist in `exercise_model_roster`.
  Read at origin/main.
- DONE: AC-8 evidence: not yet verified; ADR drafted as ruling and short title, no number.
  `### What the design changes`, item 7.
- DONE: AC-9 evidence: not yet verified; future gate run.
  No `workflow.md` edit is in the design.
- DONE: AC-10 evidence: not yet verified; owed by FO after release. #762 is open, Draft and mergeable at d5a56521, with the old set.
  `gh pr view 762`, 2026-11-02.

### Summary

The design adds a `question` subcommand so the Paseo, Codex and Claude condition can be exercised, makes the roster's models per provider, sets the new recommended set, and keeps `max` and `ultra` accepted. Real children confirmed Paseo applies Opus high, with a low control. Three things the Captain or FO should see: Claude `ultra` is `ultracode`, which is `xhigh` plus a multi-agent mode (D3); the recommended mix makes the "different family from all workers" reviewer rule unsatisfiable (D4); and no run shows a Claude child can publish (D2). This worker ran on Opus/high through Paseo, and its spawned probes used `plan` mode because the host refused `bypassPermissions`.

## Stage Report: ideation (cycle 2)

- DONE: Revise the design under the Captain gate revise of 2026-11-02: the asks are in the reason of the newest ideation resolution in this task file; do exactly those asks, and name anything that would go beyond them
  D1 to D4 recorded as rulings; item 5 and the ADR leave publication to the completion task; AC-6 proves completion; order follows the completion task. Beyond the asks: D5 and AC-11, named, not adopted.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (worker-completion-reaches-fo-on-paseo, model-roster-question-needs-both-families, special-roles-follow-the-model-table, second-round-prompts-a-step-back, validation-gate-requires-the-question-check, picky-reviewers-may-run-on-gemini) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Files are under `### What the design changes`; the table has 13 rows; `Recommended order:` puts the completion task first. Rows for tasks with no design read Scope only.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `model-roster.md` 634 to 715, or 740 under D5; `EXTENSION.md` unchanged by this task; `workflow.md` 5781 unchanged. Base count re-measured; new sentences counted with `wc -w`; the 74-word part is the first version's count, not re-measured.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-11, and one open decision, D5. `design_surfaces.py check`: "design surfaces presentable", exit 0.
- DONE: AC-1 evidence: not yet verified; future test.
- DONE: AC-2 evidence: base half observed in cycle 1; candidate half not yet verified.
- DONE: AC-3 evidence: not yet verified; future test.
- DONE: AC-4 evidence: mapping observed by the cycle 1 probe; emission not yet verified.
- DONE: AC-5 evidence: not yet verified; future test.
- DONE: AC-6 evidence: settings observed on cycle 1 probes; the resolver-driven run and the completion half are not yet verified, and the completion route has no design yet.
- DONE: AC-7 evidence: not yet verified on the candidate.
- DONE: AC-8 evidence: not yet verified; ADR drafted as ruling and short title, no number.
- DONE: AC-9 evidence: not yet verified; no `workflow.md` edit in the design.
- DONE: AC-10 evidence: not yet verified; owed by FO after release. #762 is open, Draft, at d5a56521 (`gh pr view 762`, 2026-11-02).
- DONE: AC-11 evidence: base half observed 2026-11-02 (`sonnet` on Claude, `null` on Codex, both bootstraps); the candidate's `opus` depends on special-roles and is not yet verified.

### Summary

The design now takes the Captain's four rulings: Opus only, publication and completion left to the completion task, `ultra` as `ultracode`, and the reviewer family worded by special-roles. AC-6 also proves completion reaches FO, and the order puts the completion task first. One thing goes beyond the asks and needs the Captain (D5): a disposable build shows the recommended set conflicts with the template's generated `sonnet` on a Claude FO, and nothing tells FO to pick `--host`, so the set cannot launch by the written route; answering yes also places special-roles before this task.

## Stage Report: implementation

- DONE: Implement the approved design and D1 to D5, only in its named files; commit locally without a version bump.
  Branch `spacedock-ensign/model-roster-question-needs-both-families`; assigned base `d14c5ae3b0c9f14eb89cd38a2fb500b2a57119fa`; candidate `e2eb2fb5a9629f52ab540fac1e274c287913cfac`; seven changed files, clean product tree. The existing `laws_check.readme_extensions` reader also covers block-list frontmatter.
- SKIPPED: One Draft PR stacked on PR #764; product push and PR creation belong to FO.
  No PR opened: no push grant. Hosted #764 is OPEN/DRAFT at the assigned base, #763 is OPEN/DRAFT at `c129cb215c2630d08853eeffae0fd5a2ee7e40c6`, and this branch has no open PR (2026-11-02). Title/body: `/tmp/impl-model-roster-question-needs-both-families-pr.md`; base branch `spacedock-ensign/special-roles-follow-the-model-table`.
- DONE: AC-8 — ADR 0050 records the Captain's words and retained rules, superseding 0047.
  Package `adr_lint.py docs/adr --since d14c5ae3b0c9f14eb89cd38a2fb500b2a57119fa --require 0050`: exit 0, 49 records; the resolver pointer targets the new record. Restoring 0047 Accepted fails the regression test.
- DONE: AC-1 — question asks only with all three prerequisites and no roster, and writes nothing.
  Final `test_sd_dispatch.py` subprocess replay covers all eight combinations, existing roster, empty input, disabled/unavailable providers, malformed input, inline/block lists and identical manifests; removing Claude eligibility fails the Codex-only case.
- DONE: AC-2 — provider/model pairing and all six efforts are exercised.
  Committed subprocess fixtures accept all six efforts on Opus, Sol and Astra; wrong providers/models and Sonnet refuse with field errors. Flattening model membership or imposing an xhigh cap fails the replay.
- DONE: AC-3 — the recommendation and quoted question match Opus/high, Sol/xhigh and Astra/xhigh.
  Explicit expected rows are asserted and resolved from committed fixtures; independent defaults and question-effort mutations fail. Historical batch-9 rows now use their own committed fixture.
- DONE: AC-4 — option IDs preserve each effort except Claude ultra to ultracode, with absence null.
  Replay checks every emitted value and retained tuple; live 2026-11-02 capabilities and committed recommended-row resolves: `/tmp/roster-live-capabilities.json`, `/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/roster-native-handoff-sxlhhmg0/{resolved,capabilities}.json`. Unmapped ultra and fabricated absent effort each fail.
- DONE: AC-5 — both provider families, mixed authors and unknown authors are exercised.
  Subprocess replay proves openai/anthropic/different-family/unverified, including a Claude Roster header passing `dispatch_records.py --names` and legacy Claude evidence staying unknown; fixed-openai and mixed-family mutations each fail.
- SKIPPED: AC-6 — real Opus/high with low control, Sol/xhigh, Astra/xhigh and their completion callbacks; every criterion green.
  This criterion assigns spawning to FO or validator; no real child run is claimed here. The committed fixture above is ready. Base contains completion candidate c129cb215 (ancestry exit 0), but #763 has no merge commit and its task's validation report is REJECTED; merge ancestry, native runtime and completion falsifiers remain due. FO was notified before dependent work.
- DONE: AC-7 — absent-roster behavior and worker-family wording are retained.
  Existing absence/linked-root/author cases pass with identical manifests and null option ID; removing either adoption or launch follow-family sentence fails its mutation pin.
- SKIPPED: AC-9 — the literal origin/main workflow diff is empty.
  Assigned-base-to-candidate workflow diff is empty and its 5781-word budget is unchanged. Origin/main-to-candidate contains the inherited #764 workflow change (4 additions, 4 removals); this task made no workflow edit. The local package-gate portion passes below.
- SKIPPED: AC-10 — after release, FO updates #762 from the released package and asks the Captain to merge.
  No release exists for this candidate; no predicted version, unreleased-script proof, #762 edit or merge request is claimed.
- DONE: AC-11 — recommended rows build on their provider's host without a model conflict.
  Real disposable candidate-template builds emit ideation opus/Skill bootstrap and implementation/validation null/Codex bootstrap: `/tmp/roster-provider-host-builds.json`; omitted host under Claude emits implementation sonnet: `/tmp/roster-implicit-host-falsifier.json`. Removing either D5 sentence fails its mutation pin.
- DONE: Repository skill lint, dispatch tests, release parity, design surfaces, number guards and comment ratio run successfully.
  All exit 0 after the last product change (parity's inputs are unchanged); `/tmp/roster-sd-final.log` retains fixtures at `/private/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/dev-flow-2-sd-3mygw6w6`; package number guards use the assigned base and reserved 0050; comments 1/165, 0.6% <= 5%.
- DONE: In-scope acceptance falsifiers were run with python3 -B and no copied caches.
  All 16 mutations fail: `/tmp/roster-mutations-final.log`, raw logs/results `/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/roster-falsifiers-01fodkrh`; runner `/tmp/run_roster_mutations.py`. Exact-base resolver refuses the recommended Opus row with `stages.ideation.provider: expected codex` (`/tmp/roster-base-replay.log`). AC-6/AC-10 falsifiers remain with those deferred criteria.
- SKIPPED: A clean exact-head RoboRev result, hosted CI and independent validation.
  Required post-commit package gate was attempted at the final candidate, exit 3: `incomplete: the roborev daemon is not running` (`/tmp/roster-roborev-final.log`). FO owns review/publication/CI; none is reported clean.
- DONE: Affected documents and reading cost are accounted for; no CI trigger changed.
  `doc_impact.py` lists ADRs 0047/0050 and adoption.md updated; README.md unaffected: its test command and bounded evidence claims remain valid; learning.md unaffected: no practice changed. Against the assigned base, roster.md 760->873 words (adoption 201->259, launch 417->472); adoption.md 2241->2242; workflow 5781 unchanged. CI cost per PR and model spend were not measured.

### Summary

The approved local implementation is committed at e2eb2fb5a9629f52ab540fac1e274c287913cfac with behavior, mutation and package checks. Native runtime/completion proof, upstream merge ancestry, RoboRev, publication, hosted CI, independent validation and the after-release #762 update remain with FO; no product push or PR was made.

## Stage Report: validation

- FAILED: Independent verdict on PR #765 head 57321c0b against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at 57321c0b4e9006c2a80c72b4afb1aa368e1ec2a2: AC-6 native proof incomplete; AC-9 literal diff unmet. AC-6/AC-10 native/release falsifiers not rerun; 16 local mutations detected. Full matrix: [evidence](model-roster-question-needs-both-families/validation/evidence.md).
- DONE: Stacked on PR #764. Base spacedock-ensign/special-roles-follow-the-model-table. Hosted CI is green at this head. AC-6's real Opus high, Sol xhigh and Astra xhigh runs are this batch's real dispatches: read their spawn settings with paseo agent inspect for a2d90652 (Opus), 8a750bcc (Sol) and this validator (Astra). A roster-resolved dispatch from a committed repository roster stays owed after delivery. Judge and classify
  Stack base 562b1a87198d97bb2ae1d87b72884e390b20e146; five hosted checks SUCCESS. All three settings inspected, but echo is not runtime proof. FO message e3223f76 withdrew its unauthorized timing statement; AC-6 remains due as written, findings F1–F3.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  [Five exact steps](model-roster-question-needs-both-families/validation/acceptance.md), [observed output](model-roster-question-needs-both-families/validation/acceptance-output.txt): fresh env/bash, exit 0. Skill-resolved Codex 0.34.0 package adr_lint --since stack base, with/without --require 0050: exit 0, 49 records, 0 legacy.
- DONE: AC-1 — conditional question, read-only behavior and negative inputs.
  Full subprocess matrix and identical manifests pass; missing-Claude mutation asks in a forbidden combination and fails exit 1.
- DONE: AC-2 — provider/model pairings and all six efforts.
  Three models resolve six efforts from committed fixtures; wrong pairs/Sonnet refuse. Flat-list and xhigh-cap mutations fail; exact-base Opus refusal reproduced.
- DONE: AC-3 — the three recommended rows and displayed question agree.
  Opus/high, Sol/xhigh, Astra/xhigh resolve; independent defaults/question mutations fail exit 1.
- DONE: AC-4 — option IDs, retained tuple and absence.
  Every effort exercised; live list_models accepts emitted IDs. Unmapped Claude ultra and fabricated absent effort fail exit 1.
- DONE: AC-5 — truthful author-family comparison and record parsing.
  OpenAI/Anthropic/mixed/unknown cases and Claude Roster headers pass; fixed-family and mixed-family mutations fail exit 1.
- FAILED: AC-6 — integrated real dispatch, runtime/control evidence, completion receipts and dependency merge ancestry.
  Settings inspected for Opus a2d90652, Sol 8a750bcc and Astra 0602ec7c; no bound roster-to-runtime/control run. Opus uses a historical manual send; this validator's receipt is future. #763 remains OPEN, mergeCommit null; candidate ancestry is not merge ancestry.
- DONE: AC-7 — no-roster compatibility and family wording.
  Existing absence/deletion/linked-root cases retain null effort and unchanged manifests; both follow-family text mutations fail.
- DONE: AC-8 — ADR 0050 and superseded ADR 0047.
  Record content and pointer checked; reserved-number ADR lint exit 0; restoring 0047 Accepted fails exit 1.
- FAILED: AC-9 — literal origin/main workflow diff.
  Lint, dispatch suite and parity exit 0; 5781-word budget unchanged. Origin/main diff is inherited 4+/4- from #764; exact stack-base diff empty. Added-word falsifier fails lint. F4.
- SKIPPED: AC-10 — released-package adoption on #762.
  Explicitly post-delivery; no release or consumer update claimed, and no predicted-version proof accepted.
- DONE: AC-11 — provider-specific host builds and omitted-host falsifier.
  Actual template builds emit opus/Claude bootstrap and null/Codex bootstrap; omitted host under Claude emits implementation sonnet. Both D5 sentence mutations fail.
- DONE: Other package gates, affected documents, reading cost and implementation limits.
  Guards/design/comment checks exit 0; comments 1/165 (0.6% <= 5%); all five doc-impact results accounted for. Publication/CI now verified; exact-head RoboRev still unverified. Roster 760->873 words, adoption 2241->2242, workflow 5781 unchanged; CI/model cost unmeasured, no trigger changed.
- FAILED: Installed dispatch-record check; candidate check passes.
  Installed 0.34.0 rejects final-reply scope lines in implementation-1 and validation-1; candidate reports four complete records, exit 0. Version drift is F5, not a reason to rewrite historical dispatches.
- F1 Needs decision: AC-6 roster-resolved runtime and low-control proof is missing; settings echo does not establish the promised integrated journey. No current code malfunction shown; four disposition fields in evidence.md.
- F2 Needs decision: AC-6 lacks compliant matched completion receipts; supplied historical Opus sent manually, and this validator cannot observe its own later callback. No current callback loss asserted.
- F3 Needs decision: AC-6 requires #763's merge commit in the base; only its candidate is an ancestor while the PR remains open. Stack dependency, no product repair proposed.
- F4 Needs decision: AC-9 explicitly compares origin/main; inherited approved parent wording makes it nonempty. Assigned-base equality does not silently replace that criterion.
- F5 Polish: installed checker lacks the candidate's final-reply grammar; candidate records pass. Preserve sent records and report tool-version drift.

### Summary

REJECTED at 57321c0b4e9006c2a80c72b4afb1aa368e1ec2a2 for incomplete accepted evidence, with no demonstrated scoped product-code defect. Local behavior, negative controls, host builds and five-step acceptance pass; the Pilot journey still needs AC-6 proof and the two stack-related requirements reconciled. Product bytes are unchanged; FO retains evidence, gate, review and delivery decisions.


## Stage Report: implementation

- DONE: Repair review:5733419844 and Captain amendment 1 on PR #765: read block and inline extension lists the same way, with a failing mutation.
  `question` applies the existing `decision_ledger.unquote` helper before exact membership testing. Bare, single-quoted and double-quoted extension names now behave alike in both list forms; the shared laws reader is unchanged.
- DONE: One follow-up commit on the assigned branch, only in the approved files, without a version bump or product push.
  Repair base `3c49c24a3eba3d90093f330c051b682a3335ae23`; candidate `bc882e6483ab2ee6a0944bbdcf6d86f20ae8aef1`; branch `spacedock-ensign/model-roster-question-needs-both-families`. Only `scripts/model_roster.py` and `scripts/test_sd_dispatch.py` under kc-dev-flow-2 changed; tested file digests match the committed bytes.
- DONE: Run the whole suite the CI job runs.
  All 26 Python check commands from `.github/workflows/kc-dev-flow-2-tests.yml` exit 0: `/tmp/roster-repair-ci/results.json`, `progress.log`, and per-script logs. Local Darwin CLI 0.27.2 matches CI's version; plugin source is CI's exact commit `4d158a484ec73e184861067f8ed1e20087fdc26a`. This is local evidence; hosted CI after publication remains due.
- SKIPPED: Seven cases disabled by the suite's existing environment conditions.
  Four frozen/historical amendment corpus cases; one Node/yaml journey bridge; one dispatch builder case lacking its optional env variables; one external obligation corpus case. The suite reports 1009 unittest cases including these seven skips; no skip condition was added or changed.
- DONE: Reproduce the failure before repair and run a failing quote-normalization mutation with python3 -B.
  `/tmp/roster-repair-red.log`: quoted block list returns `skip`, exit 1 from the test; `/tmp/roster-repair-green.log`: replay passes, exit 0. `/tmp/roster-repair-ci/quote-mutation.log`: removing normalization restores the same wrong skip and fails exit 1; the mutant copied no caches.
- DONE: AC-1 and AC-7 — prerequisite behavior, absence compatibility and read-only manifests remain exercised.
  The final subprocess replay covers the original eight prerequisite combinations plus all six list/quote forms, missing either provider, and exact rejection of `not-paseo`; every question preserves its fixture manifest. The quoted-block case fails without this repair; existing absent/deletion/linked-root cases remain green.
- DONE: AC-2 to AC-5 — model/effort pairs, recommended rows, option IDs and author families retain their local regression coverage.
  Final `test_sd_dispatch.py` exercises committed fixtures for all six efforts, wrong pairings/Sonnet refusal, Opus/high + Sol/xhigh + Astra/xhigh, ultra-to-ultracode, null absence, both provider families and unknown authors. Prior live option-list evidence remains in `/tmp/roster-live-capabilities.json`; no new native child evidence is claimed.
- DONE: AC-8 — ADR 0050 and the superseded 0047 pointer remain valid.
  Package `adr_lint.py docs/adr --since e891e83582ac10936ffd67fb083b530b009ad847 --require 0050` exits 0, 49 records. This mechanical repair changes no ADR, reservation, ruling or protected pointer.
- DONE: AC-9 — local package gates pass and the literal origin/main workflow diff is now empty.
  At observed main `e891e83582ac10936ffd67fb083b530b009ad847`, `git diff --stat origin/main -- kc-dev-flow-2/references/sd/workflow.md` is empty; skill lint keeps 5781/5781 words and release parity exits 0. Parent #764 has merged; this result uses the retained criterion, without changing its base rule.
- DONE: AC-11 — provider-host builds retain their model and bootstrap assertions.
  The CI-pinned dispatch replay emits opus/Claude bootstrap for ideation and null/Codex bootstrap for implementation and validation; D5 text mutations still execute in that suite. No dispatch or workflow text changed in this repair.
- SKIPPED: AC-6 — a committed-roster-to-runtime run with low control and matched finish receipts remains for FO or fresh validation.
  No runtime or completion proof was produced by this repair. The dependency part is now observed: #763 merged as `52e8eba7bf3746fd93d9132548a8163c66a7a26b`, #764 merged as e891e835, and `git merge-base --is-ancestor 52e8eba7bf3746fd93d9132548a8163c66a7a26b e891e83582ac10936ffd67fb083b530b009ad847` exits 0 for the current PR base.
- SKIPPED: AC-10 — FO's released-package update of #762 and Captain merge request remain post-release work.
  No release, predicted version, consumer edit or merge request is claimed.
- DONE: Captain amendment 1 retains the original conditions and no acceptance criterion is superseded.
  Its `Supersedes: none` is preserved. The quote bug is repaired in this task; the earlier native acceptance evidence still needs fresh validation after the upstream merges, as the Captain required.
- DONE: Required number, comment, design and document-impact checks are accounted for.
  Number guards exit 0 against both pinned stack base `8eed70b260346811a1f2aa035ca1354a2d735576` and current main e891e835; design surfaces exit 0; comments 1/172, 0.6% <= 5%. `doc_impact.py 3c49c24a HEAD`: ADRs 0047/0050 unaffected (existing ruling unchanged), README/adoption unaffected (same commands and intended membership rule), learning.md unaffected (no practice change).
- SKIPPED: Product publication, PR updates, hosted CI and fresh independent validation.
  No product branch push or GitHub write was made. Existing #765 is OPEN, targets main and still has the pre-repair hosted head 3c49c24a at inspection; FO owns publication and revalidation of bc882e648.
- SKIPPED: A clean exact-head RoboRev result.
  Required package gate at candidate bc882e648 and current base e891e835 exits 3: `incomplete: the roborev daemon is not running` (`/tmp/roster-repair-ci/roborev-current-base.log`); no clean review claim. The earlier pinned-stack attempt also exits 3.
- DONE: Scope, reading cost and CI boundaries remain unchanged by the repair.
  Two source/test files implement the named quote bug and its falsifier; no workflow, instruction, version, CI trigger or additional abstraction changed. FO reading counts stay as previously recorded; CI cost per PR and model spend were not measured.

### Summary

This complete report supersedes the earlier implementation report and corrects its missing quoted-block coverage. The single local repair commit is bc882e6483ab2ee6a0944bbdcf6d86f20ae8aef1; all 26 CI commands pass locally, while native AC-6 proof, review, publication, hosted revalidation and post-release work remain with FO.


## Stage Report: validation

- DONE: Independent verdict on PR #765 head 52017322 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at `52017322520dea243f982a015efa7747f8c05c9f`: AC-6 remains incomplete. [Criterion matrix and finding evidence](model-roster-question-needs-both-families/validation-2/evidence.md); 17 local mutations detected, native/release falsifiers explicitly not rerun.
- DONE: This rerun's ruling is Captain amendment 1 in the task file, which keeps the criteria and recheck after the parents merged: #763 and #764 are merged and this head contains main. Re-judge F1 to F5 of validation-1 and the block-list repair. FO's AC-6 run is native-runs/README.md, runtime.json and the child logs; judge it as FO's record and name any gap. Do not start agents yourself
  Amendment 1 retains all criteria. F3/F4 resolved by actual merge ancestry and the empty origin/main workflow diff; quoted-block repair passes its failing mutation. F1/F2 remain incomplete evidence; F5 remains tool-version drift. No agent started.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  [Five exact steps and observed output](model-roster-question-needs-both-families/validation-2/acceptance.md), fresh bash exit 0. Installed ADR lint --since e891e83582ac10936ffd67fb083b530b009ad847, with/without --require 0050: exit 0, 49 records, 0 legacy.
- DONE: AC-1 through AC-5 — prerequisite matrix, provider/model/effort validation, recommendation, option mapping and family comparison.
  Committed subprocess fixtures pass; all six quoted/unquoted list forms preserve manifests. Missing-Claude, flattened-pairing, effort-cap, defaults/question drift, unmapped-ultra and family-lie mutations each fail. Fresh list_models supports all emitted options.
- FAILED: AC-6 — complete roster-to-runtime and matched completion proof at the accepted boundary.
  FO's supplied record reports Opus/high vs low and Sol/Astra xhigh; process arguments and timestamped inbound receipts are not retained there. Current resolution agrees and parents are merged; those facts do not supply the missing process/receipt evidence.
- DONE: AC-7 and AC-8 — absence compatibility and ADR succession.
  Absent/deleted/linked fixtures retain readme-default/null and unchanged files; both follow-family text mutations fail. ADR 0047 points to 0050; restoring Accepted fails.
- DONE: AC-9 and AC-11 — package gates, unchanged workflow and provider-host build behavior.
  All 26 CI commands exit 0 (1009 unittest cases, 7 existing skips), plus release parity. Literal origin/main workflow diff is empty at e891e835; four real disposable builds emit opus/null/null, with omitted-host sonnet as the falsifier; workflow/D5 text mutations fail.
- SKIPPED: AC-10 and fresh native/release falsifiers.
  AC-10 remains explicitly post-release with FO; this dispatch prohibits spawning agents. No synthetic assertion substitutes for a new real-child completion/control run.
- DONE: Required guards, affected documents, reading cost and hosted candidate status.
  Number/design/comment checks pass (1/172 comments, 0.6% <= 5%); all five doc-impact entries accounted for. Roster 760->873, adoption 2241->2242, workflow 5781 unchanged. Five hosted checks SUCCESS at 520173225; CI/model cost unmeasured and triggers unchanged.
- FAILED: Installed dispatch-record check; candidate checker passes.
  Installed 0.34.0 rejects final-reply wording in four records; candidate accepts all six. Historical records are preserved; F5 is Polish.
- SKIPPED: A clean exact-head RoboRev result, product publication and delivery.
  RoboRev exit 3: `incomplete: the roborev daemon is not running`. No product push, PR mutation, release or #762 update; FO retains those obligations.
- F1 Needs decision: AC-6 process/runtime proof remains incomplete in FO's supplied bundle; high/low control and current tuple agreement narrow the earlier gap but do not replace the required process record.
- F2 Needs decision: AC-6's inbound receipts are summarized without the events/timestamps needed to compare against each child's last turn; no callback loss is asserted.
- F5 Polish: installed checker grammar predates the merged final-reply route; the candidate validates all six saved dispatch records.

### Summary

Validation cycle 2 rejects exact head 520173225 for incomplete AC-6 evidence, with no demonstrated scoped product defect. Parent ancestry, the literal origin/main condition and quoted-block repair are now verified; local checks and the five-step acceptance pass. Product bytes stayed unchanged, the detached validation checkout was removed, and FO retains the evidence, gate and delivery decisions.


## Stage Report: implementation

- DONE: Captain amendment 2 — one shared extensions-list reader for model_roster.py and dispatch_records.py, covering inline/block lists, quotes and trailing comments.
  `workflow_extensions.readme_extensions` (shared parser for workflow extension lists) is imported by the roster question and both dispatch membership sites, including extension-instruction checks. The one new module uses only stdlib and the existing decision-ledger helpers; no dependency was added.
- DONE: Three known defects become failing mutations: inline comment naming paseo, quoted block item, and trailing comment on a block item.
  `/tmp/roster-list-reader-repair/mutations.log`: each mutation fails the roster CLI matrix and makes the dispatch checker return the wrong verdict. All run with python3 -B and copied caches excluded; raw evidence/results: `/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/shared-extension-mutations-zyw3yotb`.
- DONE: Empty list and no key are controls; both callers exercise the supported list forms and unchanged files.
  Public subprocess tests cover all bare/single/double-quoted inline/block forms with/without comments, exact names, hash/comma inside quoted names, empty/no-key controls, legacy/final-reply completion and roborev instruction membership. Manifest comparisons pass; empty/no-key controls also pass under all three mutants.
- DONE: Run the whole suite the CI job runs.
  All 26 commands from `.github/workflows/kc-dev-flow-2-tests.yml` exit 0: `/tmp/roster-list-reader-repair/ci/results.json` and per-script logs. Local Darwin CLI 0.27.2 and plugin source pinned by CI at `4d158a484ec73e184861067f8ed1e20087fdc26a`; tested digests match the committed source.
- SKIPPED: Seven cases disabled by existing suite environment conditions.
  Four amendment-corpus/history cases, one Node/yaml bridge, one optional dispatch-builder case, and one external-obligation corpus case; 1009 unittest cases reported including those skips. No skip condition or CI trigger changed.
- DONE: One follow-up commit on the assigned branch, only the amended file list, without a version bump or product push.
  Repair base `52017322520dea243f982a015efa7747f8c05c9f`; candidate `c2643dae831f9685166b7cd564d8d885e88a3f21`; branch `spacedock-ensign/model-roster-question-needs-both-families`. Four files changed: workflow_extensions.py, model_roster.py, dispatch_records.py and test_sd_dispatch.py under kc-dev-flow-2/scripts; product tree clean.
- DONE: Reproduce the missing behavior before fixing it.
  `/tmp/roster-list-reader-repair/red.log`: current code rejects a valid inline list with a trailing comment, test exit 1. `green.log`: both caller matrix and complete roster replay pass, exit 0; the three mutations above independently restore the known defects.
- DONE: AC-1 and AC-7 — conditional question and absence compatibility remain green locally.
  The original eight prerequisite combinations, no-write manifests, malformed/empty/unavailable inputs, existing/absent/deleted/linked rosters and both family-wording mutations pass; the shared-reader matrix adds the repaired list/comment forms without changing roster settings.
- DONE: AC-2 to AC-5 — provider/model/effort validation, recommendation, option IDs and author-family behavior retain their local coverage.
  Committed subprocess fixtures still check all six efforts, wrong pairings/Sonnet refusal, Opus/high + Sol/xhigh + Astra/xhigh, ultra-to-ultracode/null absence, OpenAI/Anthropic/mixed/unknown authors and Claude headers. Earlier live capability evidence is retained; no new child-runtime claim is made.
- DONE: AC-8 — ADR 0050 and the superseded 0047 pointer remain valid.
  Package ADR lint against main `e891e83582ac10936ffd67fb083b530b009ad847`, requiring 0050: exit 0, 49 records. No ADR, reservation, protected pointer or human ruling changed in this repair.
- DONE: AC-9 — local package gates pass and the literal origin/main workflow diff is empty.
  Main pin e891e835; `git diff --stat origin/main HEAD -- kc-dev-flow-2/references/sd/workflow.md` is empty, skill lint stays 5781/5781 words, release parity exits 0. All required CI commands ran after the final source change.
- DONE: AC-11 — provider-host builds retain the model/bootstrap and D5 text assertions.
  The CI-pinned Spacedock replay emits opus/Claude bootstrap for ideation and null/Codex bootstrap for implementation/validation, and runs the two D5 text mutations. No workflow or dispatch envelope was edited.
- SKIPPED: AC-6 — the four real agents and matched runtime/completion evidence requested by amendment 2.
  FO owns those reruns and fresh validation at this new candidate; this implementation worker started no agents. Parent merge ancestry remains present through e891e835; neither old native summaries nor this local suite substitutes for the required new runtime/control/receipt evidence.
- SKIPPED: AC-10 — FO's released-package update of #762 and Captain merge request remain post-release work.
  No release, predicted version, consumer edit or merge request is claimed.
- DONE: Captain amendments 1 and 2 retain the original acceptance conditions.
  Both say `Supersedes: none`; no criterion was moved or relaxed. Amendment 2 authorizes the shared module and dispatch_records.py; its native rerun and independent-validation obligations remain with FO.
- DONE: Compare the changed dispatch-checker mode against main on committed task files, per learning.md.
  Main e891e835 versus this candidate's folder mode, using state commit `dee92bdc0cad3f9a546c39f7820053c20f3dc2b4`: 190 tasks, zero changed exit codes/messages. `/tmp/roster-list-reader-repair/corpus.log`; raw results `/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/extension-record-corpus-2zvjwezx/results.json`.
- DONE: Required guards and affected documents are accounted for.
  Number/design guards exit 0; comments 1/268, 0.4% <= 5%. Seven doc-impact entries unaffected: ADR 0045 (rerun check untouched), 0047/0050 (roster ruling unchanged), 0048 (same selected-extension completion rule), README/adoption (same commands/intended behavior), learning.md (no practice change; corpus practice applied).
- SKIPPED: A clean exact-head RoboRev result, product publication, PR updates and hosted revalidation.
  Required package gate at candidate c2643dae and main e891e835 exits 3: `incomplete: the roborev daemon is not running` (`/tmp/roster-list-reader-repair/roborev.log`). #765 is OPEN against main at hosted head 520173225 when inspected; no product push or GitHub write was made. FO owns review, publication and revalidation.
- DONE: Scope and reading/CI boundaries are preserved.
  The new reader, three replaced parsing sites and caller tests map to amendment 2 and its named falsifiers. No workflow, instruction, version, dependency or CI trigger changed; FO reading counts stay as previously recorded. CI cost per PR and model spend were not measured.

### Summary

This complete report supersedes earlier implementation reports and records the shared-reader repair at c2643dae831f9685166b7cd564d8d885e88a3f21. All 26 CI commands pass locally, all three defect mutations fail in both callers, and 190 committed-task verdicts agree with main; FO retains the four-agent native rerun, review, publication, hosted revalidation and post-release work.

## Stage Report: validation

- DONE: Independent verdict on PR #765 head c2643dae against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at c2643dae831f9685166b7cd564d8d885e88a3f21 against fetched origin/main e891e83582ac10936ffd67fb083b530b009ad847; validation-3/evidence.md maps all eleven criteria, commands, falsifiers and limits. AC-10 is explicitly post-release.
- DONE: This rerun's ruling is Captain amendment 2 in the task file. Re-judge F1, F2 and F5 of validation-2 and the shared list reader. FO's final AC-6 run on this exact head is native-runs/final/README.md and receipts.json; judge it as FO's record and name any gap. Do not start agents yourself
  F1/F2 resolved: the FO run, linked primary transcripts and matched inbound events establish distinct Opus high/low, Codex model/xhigh, and later completion for all four children; no send or second route. F5 remains installed-copy drift; no validator agent started.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-3/acceptance.sh ran unchanged with bash --noprofile --norc, exit 0, all five steps PASS; acceptance.md includes full commands/output. Assigned ADR lint --since e891e83582ac10936ffd67fb083b530b009ad847 exits 0: 49 records, 0 legacy; required 0050 also passes.
- DONE: Re-run package CI commands, criterion mutations and the shared-reader compatibility comparison.
  All 26 commands exit 0, 1009 unittest cases including 7 unchanged skips; 16 criterion mutations fail, and all 3 shared-reader mutations fail in both callers while empty/no-key controls pass. All 190 committed-task verdicts match main.
- DONE: Verify AC-1 through AC-5 and AC-7 through AC-9 with bounded behavioral evidence.
  Both callers preserve manifests; all provider/model/effort and family cases pass; live CLI yields ask and fresh Paseo options match. Mutating prerequisites, pairings, defaults, mapping, family, absence, ADR status or workflow words fails the relevant check.
- DONE: Verify AC-6 and AC-11 at their declared seam.
  FO's committed fixture resolves at this head; process/transcript fields and exact later receipt IDs agree. Equal-control/missing-receipt record falsifiers fail. Provider-host builds emit opus/null/null; omitting --host on Claude emits sonnet. No child was spawned by this validator.
- DONE: Check required guards, affected documents, scope and hosted candidate.
  Number/design guards and parity pass; workflow diff is empty at 5781 words; comments 1/268 (0.4%). All seven affected documents are dispositioned in evidence.md. PR #765 remains OPEN at this exact head with five successful hosted checks.
- SKIPPED: Seven existing environment-conditional suite cases.
  Four amendment/history corpus cases, one Node/yaml bridge, one optional dispatch-builder case and one external-obligation corpus case; no new skip or CI trigger.
- SKIPPED: A clean exact-head RoboRev result and product delivery.
  Local review gate exits 3: incomplete: the roborev daemon is not running. FO retains review and delivery; no product push, PR write, ready transition, merge or release performed.
- SKIPPED: AC-10 — released-package update of consumer PR #762 and Captain merge request.
  Owed by FO after release; #762 is still OPEN/Draft. No predicted version, unreleased-script substitution or pre-release falsifier accepted.
- DONE: Assess goal sufficiency, minimal necessity and implementation limits.
  The bounded Pilot journey passes; base rejects Opus and each retained behavior has a failing counterexample. Nine scoped files, one shared stdlib reader, no dependency/workflow/CI change; cost per PR and model spend not measured.
- DONE: Preserve the candidate and remove owned validation checkouts.
  cleanup.json records the detached checkout and owned fixture copies removed; assigned branch remains clean at c2643dae831f9685166b7cd564d8d885e88a3f21. Other state work is untouched.
- F5 Polish: The assigned Claude 0.34.0 cache rejects six saved final-reply lines, while the loaded Codex 0.34.0 cache and candidate accept all eight records; historical records remain unchanged and no candidate harm is demonstrated. Digests and four disposition fields: validation-3/evidence.md.

### Summary

This report supersedes the earlier validation reports and recommends PASSED for c2643dae831f9685166b7cd564d8d885e88a3f21. The shared-reader repair, current package checks and independently corroborated FO native run meet all currently due criteria; FO retains local review, the delivery decision and AC-10 after release.
