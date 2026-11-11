---
title: After a release, adopters' workflow READMEs and the state laws check are brought to it by a named step, and a repository left behind is reported
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:release-rollout-reaches-adopters-and-laws-pin:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:release-rollout-reaches-adopters-and-laws-pin-backlog-1
              briefing:
                id: briefing:release-rollout-reaches-adopters-and-laws-pin:backlog:attempt-1:revision-1
                digest: sha256:b8934f759c9b6a5fe38bbb047c32c266b198d455619c43d52f73c1b9ab54bd03
                room-ref: ./release-rollout-reaches-adopters-and-laws-pin/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:release-rollout-reaches-adopters-and-laws-pin:backlog:1
                briefing: briefing:release-rollout-reaches-adopters-and-laws-pin:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T01:18:34.32566Z"
                decision: approve
                reason: 'The Captain chose 「五張都核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：第 21 批這五張要不要進設計階段。我建議五張都核准：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、工人收到的推送說明與狀態提交工具一致、拒絕一個指令不等於全停。核准代表接受每張任務檔寫的範圍、預算與停止條件，並各派一個設計工人；不代表接受任何設計或修法。前三張標了方向要先對齊，派工前我會各問你一題。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:release-rollout-reaches-adopters-and-laws-pin:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:release-rollout-reaches-adopters-and-laws-pin-ideation-1
              briefing:
                id: briefing:release-rollout-reaches-adopters-and-laws-pin:ideation:attempt-1:revision-1
                digest: sha256:2f9cc11e111185b0124c21ec8458df91a9246850bfbea2042b4173166b034cd5
                room-ref: ./release-rollout-reaches-adopters-and-laws-pin/review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-11T02:19:58.729561Z"
                reason: The Captain answered the six-design question with 「這次比較複雜，一題題過審」 (host question dialog, 2026-11-11); each design gets its own question.
            - id: gate-attempt:release-rollout-reaches-adopters-and-laws-pin-ideation-2
              briefing:
                id: briefing:release-rollout-reaches-adopters-and-laws-pin:ideation:attempt-2:revision-1
                digest: sha256:acb939d10bbb7c3c5cb309053445198f1a50694dd67002ca94c1137014c480d9
                room-ref: ./release-rollout-reaches-adopters-and-laws-pin/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:release-rollout-reaches-adopters-and-laws-pin:ideation:2
                briefing: briefing:release-rollout-reaches-adopters-and-laws-pin:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-11-11T02:42:08.741425Z"
                decision: approve
                reason: 'The Captain chose 「照建議核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：要不要核准「發版後鋪開到採用 repo 與法規檢查」的設計並開始實作。我建議照設計的建議核准：每次發版後跑一個唯讀指令，列出每個採用 repo 的說明檔和法規釘選要不要動；法規檢查維持你點名才裝，釘選在每次說明檔同步合併後跟著移；採用 repo 的清單放在這個 repo 狀態分支的一個檔案，只列已經公開提過的；由我在你每次發版說一聲後派同步 PR，你合併後我移釘選。核准即接受這三項。」. Recommendation: followed.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-11-11T01:25:39Z
worktree: .worktrees/spacedock-ensign-release-rollout-reaches-adopters-and-laws-pin
pr: iamcxa/kc-claude-plugins#838
---

## Scope

- Source: the Captain 「也派工去其他採用的 repo 升級到最新版，此外說明這個法規升級是怎樣，之前好幾個版本都沒做，是否採用的 repo 也都沒升級？」 and 「說明法規如果安裝到每個repo會改變什麼？為何不是預設安裝？」 (chat with this FO, 2026-11-10).
- Selected for batch 21: the Captain chose 「放 1 到 5（建議）」 (host question dialog, 2026-11-11), answering 「第 21 批要放哪幾張？我建議放清單的 1 到 5：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、狀態提交自動推送與派工單矛盾、拒絕一個指令不等於全停。選完後我只為被選中的建任務檔，再一次請你過待辦關卡；選進來不代表接受任何設計。」.
- Bite (FO read at each source, 2026-11-10): this repository's `.github/workflows/dev2-laws.yml` on `spacedock-state/dev2` pinned the kc-dev-flow-2-v0.26.0 tag commit while the package reached 0.38.0, with six commits to `scripts/laws_check.py` in between that never ran hosted; nothing reported it. On the trunks, qnow's workflow README was at 0.37.0 and me-company, subspace-relay, subspace-web and subspace-v0 at 0.35.0; none of the five state branches held the laws workflow. The sync was done by hand that day (kc-claude-plugins PR #833, qnow #1350, relay #498, web #240, v0 #98, me-company #22) from prompts FO keeps outside the package.
- Package fact (kc-dev-flow-2 0.38.1 references/sd/adoption.md, "State laws check"): "Roll it out once per adopter, on the Captain's word"; it names no step after a later release, and states as not verified "the minutes a private adopter pays per run".
- Trial in progress: the laws workflow was installed on iamcxa/qnow `spacedock-state/dev2` at 77b0d1902 on 2026-11-10, on the Captain's choice 「裝 qnow（建議）」, to measure cost; its first run took 28 seconds wall clock (run 42848648288). The design reads the runs since.
- Non-goals: changing what the laws judge; making a failed laws run block a push, dispatch or merge; syncing an adopter without its Captain's merge.

## Budget
- One package PR (the release and adoption references, and a check or script only if the design shows prose cannot report a repository left behind).

## Stop condition
- For a release, one command or named step lists each known adopter with its README marker and laws pin against the released tag, and the design says who moves each and on whose word; or the design shows why not and says what was learned.

## FO alignment

Alignment: needed at ideation; whether the laws check is installed by default, whether its pin follows each release, and who may open an adopter's sync PR are the Captain's call.
Result: the Captain chose 「先報落後，預設與否等數字（建議）」 (host question dialog, 2026-11-11), answering 「「發版後鋪開到採用 repo 與法規檢查」這張任務的設計方向要怎麼定？我建議：設計先做「每次發版列出每個採用 repo 的說明檔版本和法規釘選、落後的報出來」，法規檢查要不要預設安裝、釘選要不要自動跟著發版走，等 qnow 的費用量出來、在設計關卡用數字讓你選。這是設計的方向，細節與證明仍在設計關卡由你核准。」.
Reviewer: kc-dev-flow-2:engineering-reviewer not run 2026-11-11: amendment 1 moves the adopter list out of the repository to the maintainer's machine, which removes a committed file and changes no check; the command already takes the list as a path argument.
Reviewer: kc-dev-flow-2:chief-engineer not run: the five implementation reports are one build, two RoboRev findings (job 1725 settled by Captain amendment 2, job 1727 judged against GitHub's documentation and FO's own read, with two real partial-read gaps fixed), one record of amendment 1 and one rewording of AC-10 with no product change; RoboRev job 1728 is clean on 61529999e, no finding repeats an earlier one, and the next step is the independent validation this dispatch builds.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

### PRFAQ

**After a kc-dev-flow-2 release, one command shows which adopted workflows owe a README sync or a laws pin move, and nothing behind goes unreported.** When the Release PR merges, the maintainer of the package repository runs `python3 <package>/scripts/package_version.py rollout <adopter list>`. It prints one line per listed workflow (repository, workflow directory): the README's release line against the released tag, whether the package's `references/sd/workflow.md` text changed in between (sync owed) or only the release line moved (no sync owed), and the state laws check: installed or not, and whether its pinned package commit lacks a change to `laws_check.py`, `laws.md` or `state-laws.workflow.yml` that the released tag has (pin owed). A repository it cannot read is printed as unreadable and exits 1, never as current. A code search also prints adopted workflows the list does not name, as `unlisted:` lines. FO puts the owed rows to the Captain as one question; on his word each owed README sync is a Draft PR in that adopter that he merges, and the pin follows that merge.

- **Who uses it:** the maintainer / FO of the package repository's `docs/dev2` workflow, once per kc-dev-flow-2 release. No adopter FO reads anything new.
- **Why a script, not prose (budget test):** the hand read for this design took about 40 `gh api` calls: each README's `trunk:`, its release line, the state branch, the pin, the pin's tag, and the workflow.md text between two tags. It also went wrong twice in ways the script must refuse: one loop hid stderr, and an unpaginated branch list showed qnow with no state branch while its laws file was readable. On 2026-11-10 the bite went unreported for twelve releases.
- **FAQ: why not the existing per-dispatch check?** `package_version.py <README>` already prints `README synced from X is behind the loaded package Y: re-sync it` before each worker dispatch. It exits 0, and the workflow tells FO to act only on exit 1. It runs only in a session that has already loaded the newer package, and leaves no record (it is on the observer's chat-only list). Whether adopter FOs saw it cannot be measured. The laws pin has no reader at all. The new step does not depend on any adopter FO noticing.
- **FAQ: what does it not do?** It does not change any law, block anything, write any adopter, or open any PR. It reads and reports. Non-goals are unchanged.

### Flow

```mermaid
flowchart TD
  R[Release PR merged: kc-dev-flow-2-vX.Y.Z tag exists] --> M[Maintainer runs package_version.py rollout LIST]
  M --> G{each listed workflow row}
  G -->|README read fails| U[line: unreadable + gh message]
  G -->|README read| S{release line vs released tag}
  S -->|equal| C1[README current]
  S -->|older, workflow.md text same| C2[no sync owed]
  S -->|older, workflow.md text changed| O1[sync owed]
  G -->|state branch read| L{laws file on state branch}
  L -->|absent| N[laws not installed]
  L -->|pin lacks a laws change in the tag| O2[pin owed]
  L -->|pin has every laws change| C3[pin current]
  M --> Q[code search: adopted workflows not on LIST -> unlisted lines, exit unchanged]
  U --> X{any owed or unreadable?}
  O1 --> X
  O2 --> X
  C1 --> X
  C2 --> X
  N --> X
  C3 --> X
  X -->|no, exit 0| D[done: nothing behind]
  X -->|yes, exit 1| A[FO asks the Captain one question: move these rows?]
  A -->|no| H[stop: rows stay listed at the next release]
  A -->|yes| W[one worker per adopter opens a Draft README sync PR]
  W --> P[Captain merges in that adopter]
  P --> PN[pin committed on that adopter's state branch, one path]
  PN --> D2[next release's report shows the row current]
```

The unreadable branch has no automatic retry. FO shows the Captain the gh message.

### Existing chain and current evidence

- **Spacedock 0.27.3 (first):** no adopter registry and no post-release step. A grep of `skills/`, `mods/` and `docs/` for adopter, fleet or downstream finds only roadmap and spec prose. Its `refit` re-syncs one workflow on request.
- **kc-dev-flow-2 0.38.1 at origin/main (second):** `scripts/package_version.py` holds the README release-line regex (`MARK`) and compares one local README with the loaded package. `scripts/workflow_checkout.py` compares a local README with `origin/<trunk>`. `skills/maintain-flow/SKILL.md` § Observe adopters already says "after each release the maintainer reads the first task each adopter archives on it", which makes it the existing after-release adopter step. `references/sd/adoption.md` § State laws check says "Roll it out once per adopter, on the Captain's word" and names no later step. Archived `batch10-after-release-obligations` moved one pin by hand as a one-off. Conclusion of the bounded existing-code check: extend `package_version.py` with a `rollout` mode that reuses `MARK`, and put the step in § Observe adopters. Build no new script. Two searches: `git grep x-release-please-version origin/main` (consumers are package_version.py and the release-please parity scripts) and `git grep dev2-laws origin/main` (only adoption.md and the template). Exclusion: FO's off-package prompts hold the hand list today, and they cannot be read.
- **Adopters (third, read-only via `gh api`, 2026-11-11):** release 0.38.1 is tag commit `2d827798`. Trunk READMEs (each README's own `trunk:`, all `main`): kc-claude-plugins `docs/dev2` and `docs/dev2-poc` at 0.38.1. qnow, me-company, subspace-relay, subspace-web and subspace-v0 `docs/dev2` at 0.38.0, and qnow, me-company, relay and web `docs/dev2-poc` at 0.38.0. Laws: kc-claude-plugins and qnow pin `ec2bae0d`, the v0.38.0 tag commit; laws files are identical between v0.38.0 and v0.38.1. me-company, relay, web and v0 have `spacedock-state/dev2` but no `.github/workflows` (branch read 200, directory 404, stderr shown). Workflow.md text between 0.38.0 and 0.38.1 is unchanged apart from the release line, so today's expected report owes nothing for the listed rows. Code search (`gh search code x-release-please-version --owner iamcxa --owner spacedock-dev`) also found 4 adopted workflow READMEs FO's hand list lacks: kc-paseo-plugins `docs/dev2` and `docs/dev2-poc` (0.36.0 and 0.34.0, public), and two private repositories this public file does not name (0.21.0 and 0.36.0, one with a non-`main` trunk and a non-`dev2` state branch). It also **missed** subspace-relay and subspace-web, so search cannot be the list (falsifier for discovery-only).
- **Release cadence:** 16 kc-dev-flow-2 tags from 2026-10-20 to 2026-11-11. Across the last 15 releases, workflow.md text changed in 13 and the laws files changed in 5 (0.31.0, 0.33.1, 0.34.0, 0.35.0, 0.38.0). From the 0.26.0 pin to 0.38.1, `laws_check.py` + `laws.md` differ by 298 changed lines.

### The qnow laws trial, measured (read-only, 2026-11-11)

`gh run list --repo iamcxa/qnow --workflow dev2-laws.yml`: 14 runs (42848648288 … 42939515685), 2026-11-10T15:50Z to 2026-11-11T01:31Z. 13 succeeded and 1 failed. Job time was 26–38 s, with one at 69 s, from `gh api …/runs/<id>/jobs` started_at→completed_at. 14 state commits in that window, so 14 of 14 commits were separate pushes. The one failure, run 42855594782, was L3 amendment-append-only, commit `0960af2b`. Read the diff: FO rewrote an already-recorded Captain amendment's `Design:` line, so it is a true violation and the hosted run was its only report.

Package repository for comparison (public): the most recent 500 runs (the `--limit`, not a total, since 2026-11-07) show 90 failed, not classified here.

What GitHub bills, from pages read 2026-11-11:
- **Rate and rounding:** docs.github.com/en/billing/reference/actions-runner-pricing gives "Linux 2-core (x64) | `actions_linux` | $0.006" and says "GitHub rounds the minutes and partial minutes each job uses up to the nearest whole minute". So the 14 runs are 15 billed minutes, about 1.07 per push.
- **Included allowance and public repositories:** docs.github.com/en/billing/concepts/product-billing/github-actions lists GitHub Pro's included usage as "$18 USD" a month (3,000 such minutes), and makes "Standard GitHub-hosted runners in public repositories" free.
- **When the allowance runs out:** the same page: "If your account does not have a valid payment method on file, usage is blocked once you consume the included compute usage". That would stop the account's other private CI too.
- **The timing endpoint is not evidence:** `GET …/runs/<id>/timing` returned `total_ms: 0` for every run. Its page says "This endpoint is in the process of closing down".
- **Who pays:** "Usage is charged to the repository owner". The spacedock-dev adopters bill to that organization, whose usage was not read.

The arithmetic that decides the pick (a calculation on a 10-hour sample, not a measurement): qnow's state branch took 2,045 commits from 2026-10-12 to 2026-11-11. At one push per commit and 1.07 billed minutes per push, that is about 2,190 laws minutes a month, about $13. qnow's own October hosted Linux use before laws was 1,577 minutes (GitHub's billing usage report for the owner account), and the owner's other private repositories added under 20. Laws on qnow alone would take the account from about 1,600 to about 3,800 minutes, past the 3,000 included. The overrun would be billed, or blocked if no payment method is on file. Whether one is on file was not read: the budgets endpoint returned 404. Public adopters (kc-claude-plugins, kc-paseo-plugins) pay nothing. A pin move costs no minutes, because minutes follow pushes, not the pin.

### Side by side for the Captain (decision D1)

| | A: installed by default, pin follows | B: installed on the Captain's word, pin follows (recommended) | C: both on the Captain's word only (today's text) |
| --- | --- | --- | --- |
| Hosted laws on | every adopter with a state branch | the adopters he picks: kc-claude-plugins and qnow today | the same as B |
| Minutes | about 1.07 per state push on each private adopter: qnow ≈ 2,190 a month (arithmetic above). Org adopters billed to the org, not measured | only where picked | the same as B |
| Pin | moved after each README sync merge when a laws file changed (5 of the last 15 releases) | the same | moved only on his word. The 0.26.0 pin sat 298 changed laws lines behind, unreported |
| Report row for an uninstalled adopter | `laws: not installed` owes an install | `laws: not installed`, owes nothing | the same as B, but a pin row never owes |
| Gets worse | qnow-scale adopters overrun the included allowance, and the org bill is unknown | adopters not picked keep no hosted check. Their violations surface only through observer reads | new laws never reach an installed adopter unless he remembers to ask |

### Who moves each, on whose word (decision D3)

- **README (`docs/dev2`, `docs/dev2-poc`):** a three-way-merge sync PR in that adopter, per adoption.md. The report's `sync owed` rows reach the Captain as one question per release. On his yes, the package-repository FO dispatches one worker per owed adopter, and the worker opens a Draft PR. He merges it in that adopter (non-goal kept: no sync without his merge). This is the route that worked on 2026-11-10 (six PRs).
- **Laws pin:** after that adopter's sync PR merges, the same FO commits `.github/workflows/dev2-laws.yml` with the pin set to the commit of the tag the merged README names. It is a one-path, path-scoped commit pushed to that adopter's state branch, as adoption.md's rollout already does, and only for an adopter where laws is installed. The pin never moves ahead of the README, so new laws never judge records written under older README rules.
- **List:** FO edits the list file when the Captain names an adopter, and on an `unlisted:` line only after he says to list it (decision D2).

### Where the list lives (decision D2)

Recommended: `.notes/adopters.md` on this repository's state branch `spacedock-state/dev2`, beside `.notes/fo-feedback/`. Each line holds `owner/repo workflow-dir [state-branch]`. The state branch defaults to `spacedock-state/<basename of workflow-dir>`, and the README's own `trunk:` is read, not stored. That gives 11 rows today: kc-claude-plugins, qnow, me-company, relay and web each with dev2 and dev2-poc, plus v0 dev2. That branch is public. The six repositories already appear there, in 6 to 720 files each, but the two private repositories search found have never appeared there, so they are not listed without his word, and their `unlisted:` lines print only in the maintainer's terminal. Rejected: a file in the package, which would ship a private fleet to every adopter; a trunk file, which needs a PR per list edit; and a file on this machine, which is a hidden machine dependency.

### Words FO reads at each moment

Counted with `wc -w` on origin/main `e8664a72` text and on the script's output for this README:
- **Before each worker dispatch, in every adopter:** `package_version.py <README>` prints 12 words. Unchanged. `references/sd/workflow.md` is unchanged, and so is its lint word budget.
- **Startup, idle on an open or merged PR, after archive, the merge ask:** unchanged (0 words). Nothing is added to workflow.md, the mod or any FO-run script output.
- **Adoption / re-sync (adoption.md):** the 70-word "Roll it out once per adopter…" paragraph is replaced by the D1 ruling and the pin-follows-sync rule. Estimate: 70 → about 90.
- **After a kc-dev-flow-2 release (package repository only):**
  - Before: root `CLAUDE.md` § Post-merge 289 words + `kc-plugin-release` SKILL.md 284 + maintain-flow § Observe adopters 189 = 762, plus FO's off-package prompts, which cannot be counted.
  - After: 762 + a one-row CLAUDE.md pointer (about 25) + about 60 in § Observe adopters + the report, at most 16 words per row (11 rows ≈ 176) + `unlisted:` lines.
  - This moment grows on purpose. It replaces the uncountable prompts, and implementation reports the exact before/after counts with an independent recount.

### ADR draft (no number; FO reserves it at implementation dispatch)

Short title: "After a release the laws pin follows each adopter's README sync, and installing the laws check is the Captain's word" (wording follows his D1 pick). Ruling, the Captain's D1 words verbatim. Options considered: A, B, C above. Consequences: the uninstalled-adopter gap or the minutes, whichever he accepts. Reopen when an adopter's laws pin is found behind a merged README, or when private laws minutes exceed the included allowance.

### Batch overlap

- **adr-required-statement (validation):** changes `references/sd/adoption.md` (§ Captain rulings ledger) and `references/sd/workflow.md`. Shared file: adoption.md, a different section. Also the ADR index.
- **merge-guard-stops-unasked-merges (validation, PR #794):** changes `references/sd/adoption.md` (a new section about 140 words, and § Secret reads), `delivery_gate.py`, `merge_guard.py`, ADR 0063 and `.github/workflows/kc-dev-flow-2-tests.yml`. Shared: adoption.md, a different section, and the ADR index. The CI file is not shared: `test_package_version.py` is already a step.
- **worker-push-words-match-state-commit (ideation):** names `adoption.md` once, and `workflow.md`. Possible shared file: adoption.md.
- **dispatch-carries-reserved-adr-number (ideation):** reads `laws_check.py` and `laws.md` and states no package change. It shares the ADR number reservation only.
- **budget-overrun-holds-and-findings-meet-non-goals (ideation):** `workflow.md` only. None shared.
- **story-done-reports-release-remaining, denied-command-denies-only-that-command (ideation), ops-inbox-r1-setup-and-isolation (implementation), journey-server-host-pilot (validation):** no shared file or check found in their task text.
- **pr-review-lite-value-pilot (implementation):** mentions root `CLAUDE.md` as hashed context, not as an edit. Hashed only: an edit here changes its recorded ancestor hash if its runs re-read it.
- This design changes: `kc-dev-flow-2/scripts/package_version.py`, `kc-dev-flow-2/scripts/test_package_version.py`, `kc-dev-flow-2/skills/maintain-flow/SKILL.md`, `kc-dev-flow-2/references/sd/adoption.md` (§ State laws check), root `CLAUDE.md` (§ Post-merge table, one row), one ADR, and the state-branch file `.notes/adopters.md`.

Recommended order: after adr-required-statement and merge-guard-stops-unasked-merges land their adoption.md edits, rebased on them; independent of the rest.

### Unresolved decisions for the Captain

- **D1, laws install and pin:** recommend B (installed on his word, pin follows each README sync merge). Worse under B: adopters he does not pick keep no hosted laws check.
- **D2, list home and naming:** recommend `.notes/adopters.md` on `spacedock-state/dev2`, naming only repositories already named on that public branch. Worse: the two private adopters search found stay unlisted and appear only as terminal `unlisted:` lines each release.
- **D3, who opens sync PRs and moves pins:** recommend that the package-repository FO dispatches, on his one word per release, Draft sync PRs he merges, then commits each pin after the merge. Worse: this FO writes other adopters' state branches, one disjoint path each, as a concurrent writer with their FOs, and each release with a workflow.md change asks him for up to 6 merges (13 of the last 15 releases changed it).

## Acceptance criteria

**AC-1** `package_version.py rollout <list>` prints one line per list row naming repository, workflow directory, README release line, released version, sync status and laws status. Evidence: a `test_package_version.py` case with a fake `gh` on `PATH` serving fixture READMEs and state files for 3 rows, asserting each printed line. Falsifier: dropping a row or printing a status from the wrong row fails it.

**AC-2** An unreadable row is never current. Evidence: the fake `gh` exits 1 with `Not Found (HTTP 404)` for one README. The line says `unreadable` and quotes the message, and the run exits 1. Falsifier: a mutation that treats a failed read as an empty README (no release line), and so as nothing owed, fails the test.

**AC-3** Sync is owed exactly when the package's workflow.md text differs between the README's tag and the released tag, ignoring the release line. Evidence: two fixtures, release line only (prints `no sync owed`, exit 0) and one changed sentence (prints `sync owed`, exit 1). Falsifier: comparing whole files, release line included, turns the first into `sync owed` and fails.

**AC-4** A pin is owed exactly when `laws_check.py`, `laws.md` or `state-laws.workflow.yml` differ between the pinned commit and the released tag. A pin that is no `kc-dev-flow-2-v*` tag commit prints `pin unrecognised` and is owed. A state branch with no laws file prints `laws: not installed`, owed only under D1 option A. Evidence: fixtures for each of these four cases. Falsifier: comparing pin to tag by equality alone makes the identical-laws fixture owed and fails.

**AC-5** The single-README mode is unchanged. Evidence: the existing `test_package_version.py` cases pass unedited, and for each existing case the script's stdout bytes at base and candidate compare equal (`cmp`). Falsifier: any change to the 12-word per-dispatch output fails.

**AC-6** Search-found workflows missing from the list print as `unlisted: <repo> <path>` and do not change the exit code. A failed search prints `search: unavailable <message>`, not nothing. Evidence: fake `gh search code` fixtures, one success and one exit 1. Falsifier: silence on a failed search fails.

**AC-8** A live run against the real list at the candidate. Evidence: the command, date and full output saved in the task's implementation folder. Two rows chosen by the validator match a by-hand `gh api` read of the same README and laws file. Falsifier: a row whose printed release line or pin differs from the hand read.

**AC-10** Amended by Captain, amendment 1. The step and rules are written once each: maintain-flow § Observe adopters names `package_version.py rollout <list>`, a maintainer-supplied list outside any repository committed nowhere, who moves the README and pin and on whose word; root `CLAUDE.md` § Post-merge carries one pointer row; adoption.md § State laws check states the D1 ruling. No package text names an adopter repository or supplies a list path inside a repository. Evidence: `python3 kc-dev-flow-2/scripts/lint-skills.py` exits 0, including its 12-word repeat check; implementation reports per-moment base/candidate word counts with an independent recount. Falsifier: lint fails, a non-release/non-adoption moment grows, or package text restores an in-repository list.

**AC-11** Amended by Captain, amendment 1. The command takes the maintainer's local list path; it is committed nowhere, and no list file is added to the package or state branch. Evidence: the AC-8 run reads the FO-supplied local file, and fake-gh tests cover a missing and unreadable list returning non-zero. Falsifier: a missing list returns 0 or says nothing is owed, or the candidate adds a list to either repository.

**AC-12** Amended by Captain, amendment 2. When an adopter owes both a README sync and a laws pin move, that same report line states the order in words: sync the README first, merge it, then move the pin. The comparison and debt classification in AC-4 remain unchanged. Evidence: a fake-gh both-owed fixture asserts the complete printed line and exit 1, fails at candidate a1a35a714 before the change, and passes after it; single-debt stdout bytes compare equal to a1a35a714. Falsifier: removing the printed order while still reporting the pin as owed fails the fixture.

## Number guards

ADR: 0075

## Captain amendments

### Amendment 1 — 2026-11-11, host question dialog
Captain: 「這個清單列在本地就好了，那是因為我是作者同時又是這些 repo 的維護者，放進去 dev2 repo 不是很怪嗎」 (host question dialog, 2026-11-11)
Asked: 「採用 repo 的清單要列哪幾行？這份清單會放在這個 repo 公開的狀態分支上。我建議列設計提的 11 行：kc-claude-plugins、qnow、me-company、subspace-relay、subspace-web 各列 dev2 和 dev2-poc，subspace-v0 只列 dev2。我已核對這 11 行在各自的 main 上都有流程說明檔和狀態分支；另外搜尋到的兩個沒公開出現過的私有 repo 不列。」
Supersedes: AC-7, AC-9

Superseded text:

**AC-7** The step and rules are written once each: maintain-flow § Observe adopters names the command, the list path, who moves the README and the pin and on whose word; root `CLAUDE.md` § Post-merge carries one pointer row; adoption.md § State laws check states the D1 ruling. Evidence: `python3 kc-dev-flow-2/scripts/lint-skills.py` exits 0, including its 12-word repeat check. Implementation reports per-moment word counts at base `e8664a72` and candidate, recounted by an independent copy. Falsifier: a lint failure, or a moment other than release and adoption whose count rises.

**AC-9** The list exists at the D2 home with the rows he approves. Evidence: `git show origin/spacedock-state/dev2:.notes/adopters.md` (or the chosen path) lists them, and the AC-8 run reads that file. Falsifier: a row in the AC-8 output that is not in the file, or the reverse.

### Amendment 2 — 2026-11-11, host question dialog
Captain: 「比對不動，把順序寫在那一行（建議）」 (host question dialog, 2026-11-11)
Asked: 「#838（發版後檢查採用 repo 誰落後）被審查工具指出：報告會在流程說明檔還沒同步前就把法規釘選報成「該移」，而先移釘選會讓新版法規檢查誤判舊說明檔底下的紀錄。要怎麼處理？我建議：比對方式不動，兩樣都落後時在那一行明寫「先同步說明檔，合併後再移釘選」，並加一項新的驗收條件；原本第四項驗收條件不改。」
Supersedes: none

## Stage Report: ideation

- DONE: Per the Captain's Result line: design the step that, for a release, lists each known adopter's workflow README marker and laws pin against the released tag and reports those behind, and say where the list of adopters lives; measure the qnow laws trial read-only (gh run list --repo iamcxa/qnow --workflow dev2-laws.yml: runs, durations, failures since 2026-11-10) and present default install and pin-follows-release versus Captain's-word-only side by side with that cost for him to pick at the gate, saying what GitHub bills for those runs only from a source you read
  `package_version.py rollout <list>` in § Design. List: `.notes/adopters.md` on `spacedock-state/dev2` (D2). qnow: 14 runs, 26–69 s jobs, 15 billed minutes, 1 true L3 violation (commit 0960af2b). A/B/C table; billing quoted from two docs.github.com pages read 2026-11-11; org billing and payment method stated as not read.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (story-done-reports-release-remaining, release-rollout-reaches-adopters-and-laws-pin, budget-overrun-holds-and-findings-meet-non-goals, worker-push-words-match-state-commit, denied-command-denies-only-that-command) and live task of other sessions (adr-required-statement, dispatch-carries-reserved-adr-number, journey-server-host-pilot, merge-guard-stops-unasked-merges, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions or held; read only)) that changes the same file or check, so FO can order implementation
  Shared adoption.md with adr-required-statement, merge-guard-stops-unasked-merges and possibly worker-push-words-match-state-commit; shared ADR index. Recommended order: after the first two.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Per-dispatch 12 words unchanged; startup/idle/archive/merge ask unchanged; adoption 70 → about 90; release moment 762 + about 85 + report ≤16 words/row; off-package prompts cannot be counted.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1..AC-9 under `## Acceptance criteria`; D1 (B), D2 (state-branch notes file), D3 (package FO on one word per release), each with what gets worse.
- DONE: AC-1 per-row report line — not yet verified (future fake-gh test); today's expected rows derived by hand read in § Existing chain.
- DONE: AC-2 unreadable never current — not yet verified; the falsifier class was observed in this design's own hand read (hidden stderr).
- DONE: AC-3 sync owed only on workflow.md text change — not yet verified; current fact: 0.38.0→0.38.1 workflow.md differs only in the release line (diff with that line stripped).
- DONE: AC-4 pin owed only on laws file change — not yet verified; current fact: laws files identical v0.38.0→v0.38.1 (`git diff --quiet`).
- DONE: AC-5 single-README mode unchanged — not yet verified; base output measured at 12 words.
- DONE: AC-6 unlisted and search-failure lines — not yet verified; current fact: search found 4 unlisted workflows and missed relay and web.
- DONE: AC-7 rules written once, lint passes, word counts per moment — not yet verified; base counts above at e8664a72.
- DONE: AC-8 live run matches hand reads — not yet verified (implementation).
- DONE: AC-9 list file at the decided home — not yet verified; awaits D2.
- DONE: design_surfaces.py check
  `python3 <package>/scripts/design_surfaces.py check <task>` → "design surfaces presentable", exit 0. The Mermaid rendered with mermaid-cli 11 (syntax only; actors and branches compared with the prose by hand).

### Summary

The design extends the existing `package_version.py` with a read-only `rollout` mode the package maintainer runs after each kc-dev-flow-2 release. It reports, per listed adopter workflow, whether a README sync or a laws pin move is owed. It counts a mismatched version as owed only when the package text actually changed, and it never reports an unreadable repository as current. The measured qnow trial (15 billed minutes for 14 pushes, one true violation caught) and GitHub's published rates put default install over the Pro allowance by arithmetic. So the recommendation is that installing stays on the Captain's word and the pin follows each README sync merge. Code search found four adopted workflows missing from FO's hand list, and it also missed two listed ones, so the list is a file, with search as a cross-check. No repository file, branch or commit was written outside this task file.


## Stage Report: implementation

- DONE: Implement the approved design in the assigned worktree, on the branch based on origin/main; named files only, no version bump.
  Base `e8664a72b0f904e5dda3c391d52ab3abaca876b4`; candidate `a1a35a714510683a44a2ac5ec02241e7cb354f80`; branch `spacedock-ensign/release-rollout-reaches-adopters-and-laws-pin`; six files, clean product worktree.
- DONE: ADR 0075 records the ruling the design names, quoting the Captain's words from the task file and its gate records.
  `docs/adr/0075-release-rollout-reports-adopters-and-laws-pin.md` quotes the ideation approval/question and amendment 1; `adr_lint.py docs/adr --since <base> --require 0075` exits 0 (68 records).
- DONE: AC-1 per-row report line and AC-2 unreadable never current.
  `implementation/rollout-tests.log`: exact three-row fixture; README HTTP404 is quoted with exit 1 while later rows print; dropping a row or swallowing the read failure is rejected (`mutation-1.log`, `mutation-2.log`).
- DONE: AC-3 sync owed only on workflow text changes, and AC-4 pin owed only on laws changes or an unrecognised pin.
  Fixtures cover release-only and sentence changes, each of three laws files, identical laws, unknown pins and absent install; marker-inclusive and SHA-equality mutations fail (`mutation-3.log`, `mutation-4.log`).
- DONE: AC-5 single-README mode unchanged; existing tests retained unedited and stdout bytes compared with base.
  Six original test methods unchanged; eight stdout/exit cases compare equal by `cmp`; changing the matching-output byte fails `cmp` (`mutation-legacy.log`); the dispatch fixture stays 12 words.
- DONE: AC-6 unlisted rows and search-failure diagnostics do not change the owed exit code.
  Fake-gh success/failure cases keep exit 0 or existing exit 1; silencing search failure is rejected (`mutation-5.log`).
- DONE: AC-8 live run at the candidate, with the privacy handling in implementation-1-message-2.
  2026-11-11 command/date/input hash and two independent implementation hand reads are in `implementation/live-summary.json`: 11 listed rows, four unlisted, exit 0; full private output remains only `/tmp/rollout-implementation/live-candidate-output.txt`; changed printed release/pin fail the hand-read comparison.
- DONE: AC-10 rules and per-moment word counts, replacing AC-7 under Captain amendment 1.
  `implementation/word-counts.json`, independently recounted with `wc -w`: release documents 778→897 plus 112 report words; adoption paragraph 70→95; shared workflow 5939→5939; startup/open-PR idle/merged-PR idle/archive/merge ask deltas 0. Repository lint exits 0; copied 12-word repetition fails (`mutation-lint.log`); spans and exclusions in evidence README.
- DONE: AC-11 explicit local list, replacing AC-9; no list file added to either repository.
  AC-7/AC-9 moved verbatim under amendment 1 and fresh AC-10/AC-11 written; the run reads FO's local path, package docs specify outside any repository, and absent/unreadable-list fixtures fail; a missing-list success mutation is rejected (`mutation-6.log`).
- DONE: Repository lint, required ADR/number guards and comment ratio, using the dispatch-designated package scripts.
  All exits 0 in `implementation/checks.json`; repository lint 5939/5939; number guards at the candidate report PASS; 313 added code lines, one comment, 0.3% versus 5%; design_surfaces.py exits 0; no bytecode caches used in mutation runs.
- DONE: Affected documents and bounded existing-code/goal audit.
  `implementation/check-docs.json` lists ADR 0075 and maintain-flow, both updated; adoption and root CLAUDE pointer also updated as designed. Prior design capability audit reused; base lacks rollout (nine new tests fail there); each retained surface serves AC-1–AC-11, the ruling, or release/adoption entry points; no workflow/law/CI/version file changed.
- DONE: Record qnow's current state without treating the post-design change as a defect.
  Independent contents HTTP404 plus state-branch HTTP200 match `laws: not installed`; FO confirms Captain-authorised removal at `dce0a96c0` in implementation-1-message-3.
- SKIPPED: One Draft PR; product push, PR creation, RoboRev and hosted CI are FO-owned under this dispatch.
  No PR opened: no push grant. Prepared title/body: `/tmp/impl-release-rollout-reaches-adopters-and-laws-pin-pr.md`; branch and exact candidate above; all delegated checks are not run, not clean. CI cost per PR not measured; no CI trigger or job changed.
- SKIPPED: Two live rows chosen by the independent validator and behavior replay of a model.
  Validator picks remain due; implementation hand reads are not independent validation. Reporting was exercised at fake-gh and live-gh seams; existing worker dispatch behavior is unchanged, and no model-behavior claim is made.

### Summary

The read-only release command now reports workflow sync and installed-laws pin debt using a maintainer-supplied local list, with unreadable rows explicit and search treated as a cross-check. Captain amendment 1 keeps that list committed nowhere; 17 tests, eight mutation controls, byte comparisons, required checks and the final-candidate live read passed. Product publication, Draft PR, RoboRev, hosted CI and independent validation remain with FO; no adopter was changed.


## Stage Report: implementation

- DONE: Judge RoboRev job 1725 on candidate a1a35a714 against the approved design before changing code.
  `implementation/review-1725/adjudication.md`: the reported comparison is factual and matches AC-4's released-tag target; the separate D1/D3 execution rule waits for the merged README. Recommended disposition: keep the approved comparison; FO owns accepting/declining the High finding.
- DONE: Say which reading the design supports, whether a newer laws check with an older README can misjudge, and what the report prints for both debts.
  `both-owed.log` prints `README:0.38.0 released:0.38.1 sync owed; laws: <old-sha> pin owed`, exit 1; actual 0.26.0/0.38.1 checker probe on the same old README/range exits 0/1 because newer extension-instruction enforcement rejects an old-valid second dispatch (`version-skew.json`).
- DONE: Return a criterion-changing repair to FO as a decision for the Captain; preserve the candidate and criteria.
  A throwaway change from latest-release target to `tags[have]` fails all three existing AC-4 laws-file subcases (`readme-target-violates-ac4.log`); no product or criterion change, no product commit, no product push. Candidate remains `a1a35a714510683a44a2ac5ec02241e7cb354f80` on the assigned branch; base remains `e8664a72b0f904e5dda3c391d52ab3abaca876b4`.
- DONE: Original AC-1, AC-2 and AC-6 row identity, read failure and search diagnostics remain covered.
  All 17 package_version tests reran successfully (`review-1725/tests.log`); the prior exact-row/drop-row, swallowed-read and silent-search mutation evidence remains in the parent implementation folder at this same candidate, not rerun this round.
- DONE: Original AC-3, AC-4 and AC-5 content comparison, laws debt and byte compatibility remain covered.
  The same 17 tests pass; AC-4's counter-proposal fails three subcases. Original eight stdout comparisons and their mutation remain bound to this unchanged candidate; no dispatch output or existing test method was edited.
- DONE: Original AC-10 and AC-11 implement Captain amendment 1 and local-only list ownership.
  Repository skill lint reran at 5939/5939; no product docs/list changed. Parent word-count evidence remains release docs 778→897 plus 112 report words, adoption 70→95, other lifecycle deltas 0; local-list and missing-list evidence retained without rerunning it.
- DONE: Required ADR and comment checks at the unchanged candidate; retain original number-guard evidence.
  Required ADR 0075 lint exits 0 (68 records); comment ratio 313 code lines/one comment, 0.3% under 5%; accepted ADR 0075/0017 hashes recorded in review-1725/adr-references.json. Parent number-guard PASS at this candidate is retained, not rerun.
- DONE: Append a complete superseding implementation report and update the prepared PR text.
  This report; `/tmp/impl-release-rollout-reaches-adopters-and-laws-pin-pr.md` now distinguishes released-tag debt from post-merge pin writes, records probes and the unresolved review disposition. Draft PR #838 exists per FO; no external comment or edit was sent.
- DONE: Preserve artifact scope and concurrent state ownership.
  Product worktree is clean; no new files or edits in its six-file diff. Only this task's report and review evidence are committed path-scoped; the sibling worker-push-words-match-state-commit state edit is left alone. No ADR, version, CI, law or adopter change.
- SKIPPED: Repair the product comparator and write a new product commit.
  The requested comparator change would alter AC-4; dispatch requires stopping and returning that decision. A prospective repair was exercised only in a throwaway copy; no empty commit made.
- SKIPPED: Original AC-8 live run and independent validator's two selections in this assessment round.
  The parent final-candidate live summary (11 listed, four private unlisted, exit 0) and private /tmp output remain; no current live re-read claimed. Validator-selected rows remain due; no adopter was changed, including Captain-authorised qnow removal at dce0a96c0.
- SKIPPED: Product push, RoboRev rerun, review disposition and hosted CI; behavior replay and billed CI cost.
  FO owns publication/review on #838. Local `roborev show --job 1725` failed on sandbox access to its daemon log; review text comes from FO's recorded dispatch, not an independent daemon read. No clean review claimed; no new model replay; per-PR CI cost not measured, no CI workflow changed.

### Summary

This report supersedes the earlier implementation report, retaining its evidence at the unchanged candidate and replacing its outdated no-PR/no-review status with FO's Draft PR #838 and forwarded High finding. The reported early pin debt matches AC-4, while a real-checker probe confirms why moving the pin must wait for README merge; changing the comparator to the README release breaks that approved criterion. No product repair or criterion rewrite was made; the comparator decision and final finding disposition return to FO/Captain, with a clean product worktree and updated handoff text.


## Stage Report: implementation

- DONE: Captain amendment 2 settles RoboRev job 1725; keep AC-4's released-tag comparison and print the order in a both-owed row.
  Candidate `ba98f3ca95c1f879bf460fbb08976f337e18c4c8` appends `; sync README, merge, then move pin` when both debts are true; comparison, debt flags, exit classification and pin writes are unchanged (the command remains read-only).
- DONE: Add one new criterion under a fresh id marked Amended by Captain, amendment 2; leave every prior criterion unchanged.
  AC-12 added with the both-owed fixture and missing-order falsifier; amendment-2/criteria-check.json verifies all 11 prior criterion blocks, including superseded blocks, byte-identical to criteria-before.json.
- DONE: Implement within the design's named files, show single-debt lines byte-identical, and commit locally without pushing.
  Follow-up commit `ba98f3ca9` changes package_version.py and test_package_version.py only; prior `a1a35a714510683a44a2ac5ec02241e7cb354f80`, base `e8664a72b0f904e5dda3c391d52ab3abaca876b4`, branch `spacedock-ensign/release-rollout-reaches-adopters-and-laws-pin`. Five byte/exit comparisons pass in amendment-2/proof-results.json; product worktree clean.
- DONE: AC-12 both-owed order, with a before/after test and executed falsifier.
  amendment-2/tests-before.log: 18 tests, one expected missing-order failure on a1a35a714; tests.log: all 18 pass after the change; missing-order-mutation.log rejects a pin-owed line without order, exit 1. The printed both-owed row is 16 words (both-owed.txt).
- DONE: AC-1, AC-2 and AC-6 row identity, explicit unreadability and search diagnostics remain satisfied.
  All package_version cases pass; original-proofs reruns reject dropping a row, swallowing the read failure and silencing search failure, each exit 1; its eight-control proof-results.json is saved under amendment-2/original-proofs.
- DONE: AC-3, AC-4 and AC-5 text comparisons and single-README behavior remain unchanged.
  Existing laws-change/unknown-pin/absent-install tests pass; marker-inclusive and pin-equality mutations fail; all eight original stdout/exit comparisons with base pass and changed legacy bytes fail cmp (amendment-2/original-proofs/run.log).
- DONE: AC-8 live read at the new candidate, retaining the privacy handling of amendment 1.
  2026-11-11 command, candidate and list hash in amendment-2/live-summary.json: 11 listed rows, four unlisted, exit 0; listed output matches a1a35a714 byte-for-byte, 112 words. Full output stays only /tmp/rollout-amendment-2/live-output.txt; no local list or private unlisted names committed.
- DONE: AC-10 per-moment words and written rules; AC-11 local-only list remains intact.
  amendment-2/word-counts.json: release documents 778→897 versus original base, installation paragraph 70→95, shared workflow 5939→5939 and other lifecycle deltas 0, independently recounted with wc -w; only a both-owed report adds six words. No document or list-path default changed; missing/unreadable-list fixtures and success mutation controls pass again.
- DONE: Repository skill lint, required ADR/number guards, comment maximum and design-surface checks at the candidate.
  amendment-2/checks.json records all exits 0; repository lint 5939/5939; ADR 0075 required, 68 records; number guards PASS on ba98f3ca95c1; comments 323 code lines, one comment, 0.3% under 5%; design surfaces presentable (scope check not run at implementation).
- DONE: Affected documents and ADR 0075 remain correct; scope/goal audit retains only the approved behavior and regression test.
  amendment-2/docs.json: ADR 0075 unaffected because released-tag debt and post-merge sequencing remain its ruling; maintain-flow unaffected because its report command and move-after-merge instructions remain accurate. No existing ADR edited, no new number, version, law, CI or adopter change; removing the new suffix produces the named AC-12 failure.
- DONE: Answer the repeated-symptom step-back questions before useful work; no new profile or orchestration scope.
  role_triggers.py exits 0 with its step-back reminder: still the original read-only rollout outcome; gap immediately testable with fake gh; deleting AC-12 removes the in-row merge sequence even though debt arithmetic survives. Pilot boundary and FO publication ownership retained.
- DONE: Update the prepared PR text and append a complete report superseding earlier implementation reports.
  /tmp/impl-release-rollout-reaches-adopters-and-laws-pin-pr.md names ba98f3ca95c1, amendment 2, single-debt compatibility and validation; this complete report is appended. Only this task's report/evidence is committed path-scoped; concurrent sibling state work remains untouched.
- SKIPPED: Product push, editing Draft PR #838, RoboRev rerun and hosted CI.
  FO owns these under the dispatch; no external review request/comment, ready action or merge performed. RoboRev and hosted CI are not run here, not clean; per-PR billed CI cost not measured, no CI trigger or job changed.
- SKIPPED: Validator-selected two live hand reads and model behavior replay.
  Independent validator choices remain due; this worker's fresh live read and fake-gh controls do not substitute for them. Earlier real-checker version-skew evidence is retained under review-1725, not rerun in this round; no model-behavior claim made.

### Summary

This report supersedes both earlier implementation reports, including the review-1725 Needs decision conclusion, because Captain amendment 2 has settled that question. The comparator remains as AC-4 requires, and AC-12 now makes the README-sync/merge/pin order explicit on the both-owed line; 18 tests, original mutation/byte controls, new missing-order mutation, single-debt byte comparisons, required checks and the new-candidate live run pass. Candidate ba98f3ca95c1 is committed locally without product push; FO owns updating Draft PR #838, rerunning RoboRev/CI and independent validation.


## Stage Report: implementation

- DONE: Judge RoboRev job 1727 using message-7's corrected measurement, GitHub REST documentation and a probe before repairing.
  review-1727/sources.json and refs-probe.json: matching-refs has no documented page/per_page or pagination threshold; 49 component refs and 165 repository tags return without Link, and forced page parameters return identical sets. The first-page truncation premise is not substantiated; Github.releases is byte-identical to ba98f3ca9, so that call is unchanged.
- DONE: Survey every other gh read, fixing supported silent omissions and stating what remains with reasons.
  review-1727/read-survey.json enumerates repo metadata, contents, matching refs, annotated tags, named branch and search. Repo/annotated-tag/named-branch GETs are single objects and remain unchanged; directory-list caps do not apply to exact-file paths. Search and omitted file payloads are repaired below; inherent search index/access/scope limits remain advisory under the approved explicit-list design.
- DONE: Fix code-search completeness reporting within the design's named files, with tests and executed falsifiers.
  Raw REST pages retain total_count/incomplete_results; a 101-item fixture reaches page 2. Timeout, >1000 results or short pages print search: unavailable without changing listed-row debt exit. The old CLI already paginated: its lost metadata, not nonexistent first-page-only behavior, is the repaired seam. Five read-integrity mutations are rejected (review-1727/proof-results.json).
- DONE: Fix successful contents responses that omit the payload, with before/after proof.
  Public 14,216,605-byte OpenAPI file probe returned encoding none and empty content; old Github.content accepted empty text, candidate raises unreadability. Two omitted workflow/laws payload fixtures cannot compare equal now; the missing-guard mutation fails. No raw-download fallback or general file transport was added.
- DONE: Commit only named implementation/test files, preserving branch, base, comparator, Captain amendment 2 and every criterion.
  Candidate `61529999eb4184b44328fe2fbad545b1b0b0ed92`; prior `ba98f3ca95c1f879bf460fbb08976f337e18c4c8`; base `e8664a72b0f904e5dda3c391d52ab3abaca876b4`; branch `spacedock-ensign/release-rollout-reaches-adopters-and-laws-pin`. Follow-up changes package_version.py/test_package_version.py only; product worktree clean, no product push or criterion edits.
- DONE: AC-1, AC-2 and AC-6 row identity, unreadability and search visibility remain satisfied.
  23 package_version tests pass; the prior candidate fails five cases/subcases for hidden completeness/omitted content (tests-before.log). Original row-drop, swallowed-read and silent-search mutations fail again under review-1727/original-proofs; new partial-search diagnostics retain the AC-6 exit policy.
- DONE: AC-3, AC-4 and AC-5 content-based debt and legacy output stay unchanged; AC-12 still prints both-owed merge order.
  23 tests, eight original controls and eight legacy byte/exit comparisons pass; the marker-inclusive/SHA-equality/legacy-output mutations fail. review-1727/order-proofs reruns the missing-order mutation and five prior-candidate byte/exit comparisons; the both-owed line remains 16 words, comparator unchanged.
- DONE: AC-8 fresh live rollout at the candidate, saving counts and exit while preserving private unlisted names.
  review-1727/live-summary.json: 2026-11-11, local-list command/hash and candidate; 11 listed rows, four unlisted, exit 0, no search-unavailable line. Listed output is byte-identical to ba98f3ca9, 112 words. Full output remains only /tmp/rollout-review-1727/live-output.txt; no list or private names committed.
- DONE: AC-10 lifecycle words and AC-11 local-only list ownership remain intact.
  review-1727/word-counts.json retains independently recounted document moments: release 778→897 versus base, adoption 70→95, workflow 5939→5939, other lifecycle deltas 0. Changed diagnostics occur only at release-report time; single-README bytes are unchanged. Missing/unreadable-list tests and missing-list-success mutation pass again; no list file added.
- DONE: Repository lint, ADR 0075 lint, number guards, comment maximum and design-surface checks at the candidate.
  review-1727/checks.json: all recorded exits 0; lint 5939/5939; required ADR lint 68 records; number guards PASS at 61529999eb41; 408 added code lines, one comment, 0.2% under 5%; design surfaces presentable (scope check not run at implementation).
- DONE: Per-document disposition and bounded scope/goal audit.
  review-1727/docs.json lists ADR 0075 and maintain-flow: both unaffected because debt semantics, read-only reporting, error visibility and merge ordering remain correct. No new decision/ADR, dependency, law, CI, version or adopter change; removing metadata/content guards reproduces the named omissions. Previous capability audit reused; this is a named seam repair.
- DONE: Answer the repeated-symptom step-back questions and update PR text plus a complete superseding report.
  Still the original complete read-only report outcome; probes and fake-gh cases test the gap now, no external wait; deleting completeness handling would hide missing results as complete. /tmp/impl-release-rollout-reaches-adopters-and-laws-pin-pr.md names candidate and evidence; this report and task-only evidence are committed path-scoped, preserving sibling state edits.
- SKIPPED: A matching-refs pagination repair and a deliberately fictional paginated-matching-refs fixture.
  Message-7 requires no change to this call when evidence does not support pagination. No documented page size was found, and >100 refs return in one response. This does not claim an experimentally infinite server bound; a future undocumented API change would need new evidence.
- SKIPPED: Product push, updating Draft PR #838, RoboRev rerun and hosted CI.
  FO owns those; job 1727 is assessed from FO's recorded dispatch, not an independent daemon read. No new clean review claimed, external comment/request, ready action or merge. Per-PR billed CI cost not measured; CI triggers/jobs unchanged.
- SKIPPED: Independent validator-selected live hand reads and model behavior replay.
  Two validator choices remain due; this worker's fresh live read is not their validation. No model replay claimed; previous version-skew evidence remains under review-1725 and is not rerun here.

### Summary

This report supersedes all earlier implementation reports for candidate 61529999eb41. The matching-refs High finding's pagination premise is not supported by official documentation or the 49/165-ref probes, so that call remains unchanged; the authorized survey instead repaired two evidenced omissions in code-search metadata and large-file content handling. All 23 package_version tests, original/order controls, five new mutations, required checks and the fresh live rollout pass; product publication, RoboRev/CI and independent validation remain FO-owned.

## Stage Report: implementation

- DONE: Reword AC-10 only, in the task file, without widening or narrowing it.
  The three clauses rejected by the validation dispatch now use superseded AC-7's wording; the command/list constraints, word-count recount and falsifier are unchanged. No amendment wording was added, and no other criterion changed. Exact changed clauses (the checker's sentence boundaries include semicolons):
  Old: root `CLAUDE.md` § Post-merge has one pointer;
  New: root `CLAUDE.md` § Post-merge carries one pointer row;
  Old: adoption.md § State laws check states the installation ruling.
  New: adoption.md § State laws check states the D1 ruling.
  Old: repository `lint-skills.py` exits 0 including its repeat check;
  New: `python3 kc-dev-flow-2/scripts/lint-skills.py` exits 0, including its 12-word repeat check;
- DONE: Check AC-11 and AC-12 for the same defect against their amendments and fix them the same way if they have it.
  AC-11 yields no added-word finding under amendment 1. AC-12 is amendment 2's new criterion, not a replacement; its printed sync/merge/pin order and unchanged AC-4 match that Captain/Asked ruling. Both remain byte-identical.
- DONE: Exercise the validation-dispatch wording check before and after this correction.
  Installed 0.38.1 dispatch_records.py --names --strict on temporary validation-1.md snapshots: original exit 1 flags only has/installation/repository; corrected exit 0. The record names amendments 1 and 2 and candidate 61529999eb4184b44328fe2fbad545b1b0b0ed92. Reverting each corrected clause independently restores its added-word finding. Temporary logs are /tmp/rollout-ac10-wording/{before,after}.log; no real validation record was created and no worker dispatched.
- DONE: Keep the accepted product candidate and prior evidence unchanged.
  Product HEAD 61529999eb4184b44328fe2fbad545b1b0b0ed92 on spacedock-ensign/release-rollout-reaches-adopters-and-laws-pin is clean; base remains e8664a72b0f904e5dda3c391d52ab3abaca876b4. Prior review-1727 evidence and this task's preceding implementation report retain the 23 tests, mutations, live rollout, lint/ADR/number/comment checks and document dispositions; none was modified or rerun for this task-text-only correction.
- DONE: Commit the task file with the state commit command and report the exact old and new sentences.
  Only this task file is changed by this round. The FO-authorized /Users/kent/.local/bin/spacedock state commit release-rollout-reaches-adopters-and-laws-pin --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 publishes it after this append; the three exact old/new clauses are recorded above. Sibling task edits are preserved and excluded.
- SKIPPED: Product push, PR changes, RoboRev, hosted CI and independent validation.
  FO message-8 reports candidate 61529999e pushed to Draft PR #838 and RoboRev job 1728 clean; those are FO's observations, not rerun here. Actual validation dispatch remains FO-owned. No product/evidence/CI/version change, external comment or merge; per-PR CI cost remains not measured.

### Summary

This report supersedes the earlier implementation reports for the message-8/message-9 wording follow-up; their unchanged product evidence remains referenced above. AC-10 restores three inherited AC-7 clauses, AC-11/AC-12 remain unchanged, and the same strict validation-record check changes from the reproduced three-word rejection to exit 0. The product candidate remains 61529999eb4184b44328fe2fbad545b1b0b0ed92; the FO still owns retrying the real validation dispatch.
