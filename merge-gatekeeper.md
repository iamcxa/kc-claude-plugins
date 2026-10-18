---
title: A merge gatekeeper reviews each PR, lets FO merge one it judges safe, and tells the Captain what to look at
variant: kc-dev-flow-2
profile: prod
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:merge-gatekeeper:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-gatekeeper-backlog-1
              briefing:
                id: briefing:merge-gatekeeper:backlog:attempt-1:revision-1
                digest: sha256:52c1227978e4bda4653bb324f98a2a0ff7ab4e7bb34ecc048a756e417d5e7d5d
                room-ref: ./merge-gatekeeper/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-gatekeeper:backlog:1
                briefing: briefing:merge-gatekeeper:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T06:10:37.776694Z"
                decision: approve
                reason: Captain approved in chat (「准」) the six batch-2 backlog gates presented together in one message, accepting the recommended profiles (pilot; merge-gatekeeper prod) and the stated order
              application:
                target-stage: ideation
                state: consumed
        - id: gate:merge-gatekeeper:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:merge-gatekeeper-ideation-1
              briefing:
                id: briefing:merge-gatekeeper:ideation:attempt-1:revision-1
                digest: sha256:564054ca455cfbe4328f5ed326b2a655c86927f70c918e7eaddcc4bb6aaab7f6
                room-ref: ./merge-gatekeeper/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-gatekeeper:ideation:1
                briefing: briefing:merge-gatekeeper:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T07:30:44.720716Z"
                decision: approve
                reason: Captain approved in chat (「那就照建議」, after asking FO to restate the merge-gatekeeper D1 reasoning) the six batch-2 ideation gates presented together in one message, accepting each task's stated recommendations and FO's implementation order
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-17T06:11:32Z
worktree: .worktrees/spacedock-ensign-merge-gatekeeper
pr: iamcxa/kc-claude-plugins#666
---

Filed on the Captain's request (chat, 2026-10-16): 「我想新增一張票，設計一個 codex 的 PR 守門員，它的任務是確保 P R 可以合併，類似 JEV 那樣的工作，只要例如 PR 超過 95% 沒問題，那就讓它帶我授權 FO 合併 PR，相應的但是也要讓它負責提出我需要注意的點……這件事的目的是，減低 FO 自己合併 PR 的意外，以及減低我每次都要肉眼 review PR 的負擔」

## Scope

- Two goals in his words: fewer accidents when FO merges PRs itself, and less of his own eye review of every PR.
- Asked shape: a Codex-run gatekeeper judges whether a PR can merge; above a confidence bar (his example: 95%) it grants FO, on his behalf, the merge; it also lists the points he should look at.
- JEV, per the Captain (chat, 2026-10-16: 「jev 是這個 https://typesafe.ai/blog/introducing-system-one-models-and-jev 這是特殊的 agent 類型，只負責斷機率不回話」): TypeSafe AI's "System One" model, early access. Read by FO on 2026-10-16 from that page: it takes unstructured state and returns a typed decision from choices defined in advance, each with a probability and confidence score, and no free text; stated 70 to 500 ms and $0.042 per million input tokens, output free; calibration is claimed only in words ("higher confidence means higher accuracy"), with no number, and its evals were built by the vendor. It judges the state it is given; it does not read code, so it would sit after the reviewers, not replace them.
- Open at backlog: which model or product the gatekeeper runs on ("Codex", or a GPT or Claude model he recalls doing the same job); how the 95% is measured and calibrated (a reviewer's stated confidence is not a measured rate).
- Conflict to settle first: ADR 0011 (accepted) says "Authority, gate approval, merge, outward-facing actions, irreversible changes and money are never delegated at any level." A merge grant needs a new ADR that supersedes that clause for this case, with his Words; ideation drafts it.
- Existing pieces to check before building (upstream first): kc-pr-flow `kc-pr-review` (Codex source, confidence gates), the Codex PR review already read by `pr_watch.py`, `delivery_gate.py` (head equals the validated candidate), `spacedock merge guard`, ADR 0011's L3 "decide by record" (a Captain grant per decision class on ledger evidence), and today's batch-1 record of FO merge asks (four PRs, each Captain-merged).
- Data leaving the machine: sending PR diffs or review text to an outside service is an outward-facing data share (relay and qnow are private); the Captain decides it per repository.
- The bite to measure: FO-merge accidents so far (count them from state and chat-free evidence) and the Captain's review time per PR.

## Options found (FO, 2026-10-17)

- OpenAI Decisions API, verified on https://developers.openai.com/api/docs/guides/decisions (read 2026-10-17): `POST /v1/decisions`, public beta ("we expect to GA in the coming weeks"), `gpt-6-luna` the only model. A `choice` question takes `name`, `instructions` and `choices` (`value`, `description`); the answer returns `choice`, a `probabilities` array over the options and a separate `confidence` field. No calibration claim: the page advises setting thresholds from labelled examples. Input $0.10 per million tokens, output free. Zero Data Retention supported for eligible customers; US and EU data residency.
- Codex (`codex exec`, 2026-10-17) suggested the Decisions API plus: enforce the deterministic checks first (head equals the validated candidate, required CI green); calibrate on labelled historical PR snapshots split by time (logistic or isotonic on a held-out set, tested on untouched history); allow a merge only where calibrated P(merge) >= 0.95 and the lower confidence bound of precision on the accepted subset meets the target; otherwise "needs human". Codex's other claims (logprobs on `gpt-6-sol` / `gpt-6-luna` only at reasoning effort none; Evals graders) are unverified.
- TypeSafe Jev: see Scope.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it (his words are at the top of this file).
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-18 — third repair cycle on #666 (Codex round 2 review:5562139252, two more P1 in the grant path, which has no consumer until a grant exists): repair again, or narrow the PR to the parts used at every merge ask now?

## Captain amendments

### Amendment 1 — 2026-10-18, chat
Captain: 「同意」 (chat, 2026-10-18)
Asked: 「同意「#666 縮小，授權那半改成先量再做的 POC 待辦」嗎？同意的話，我會把你的原話記成修正指示，然後派人去刪掉授權那半。」（「#666 縮小，只交出合併前檢查、要看的重點清單和合併請求的紀錄……授權那半不要開成「之後重做」，改開一個 POC 待辦，先量兩件事：adopter 裡有多少 PR 可以被授權；「預先授權合併」是不是已經涵蓋了你要的效果。」）
Supersedes: AC-4, AC-5, AC-7, AC-11, AC-12, AC-3, AC-8
Design: the grant, merge-line and calibrate parts of ## Design

## Design

Not repository files: this section is the design; implementation lands it. Sources read 2026-10-17: kc-dev-flow-2 at origin/main 19fe3b5b (released 0.24.0) with `git show` (`scripts/delivery_gate.py`, `scripts/pr_watch.py`, `scripts/decision_ledger.py`, `scripts/lint-skills.py`, `references/sd/workflow.md`, `references/sd/mods/kc-dev-flow-2.md`, `extensions/*/EXTENSION.md`, `skills/learn/SKILL.md`, `docs/adr/0009`, `0011`, `0019`); kc-pr-flow at the same commit (`skills/kc-pr-review/SKILL.md`, `scripts/github-repo-write.sh`); Spacedock 0.27.2 (`spacedock --version`, `gate --help`, `gate record --help`) and its 0.27.0 plugin cache (`mods/pr-merge.md`, `skills/fo-gate-lifecycle`); adopters subspace-relay, subspace-web and qnow by read-only `git show`/`gh api`; the OpenAI Decisions API page (fetched 2026-10-17); `gh pr merge --help` (gh 2.92.0).

### The bite, counted

Counted 2026-10-17 by a read-only pass over the 30 archived tasks of `spacedock-state/dev2`, 400 merged PRs of this repository (2026-08-01 to 10-17, `gh pr list --state merged`), the dev2 state branches of qnow, relay and subspace-web (keyword search, not a full read), and the Captain's memory notes on merges, checked against GitHub timestamps. `mergedBy` is `iamcxa` on 397 of 400 PRs, so GitHub cannot tell FO from the Captain; the classes below rest on state records and PR heads.

| Accident class | Count | Instances (evidence) |
| --- | --- | --- |
| FO merged without the Captain's merge word | 0 | every FO-recorded gate says the merge stays with the Captain. In qnow he delegated by chat on a condition before ADR 0011: 「都處理完就幫我合併」 (#1184, 2026-09-13), 「之後沒有 P1 就合併」 (#1243, #1245, 2026-09-29); whether the condition held was not checked |
| A merged head other than the validated one, not disclosed | 2 | #632 (2026-10-13): merged at 7679ab7a, validated 40c714a6 (`_archive/observer-before-merge-guard/observer.md`, a violation row); it led to `delivery_gate.py` (#640). #628 (2026-10-13): a merge of main at 0286f8e7 made after the approval of 7d89898e. Disclosed, not counted: #549 (2026-10-01), whose gate named both heads |
| A merge FO drove later reverted | 0 | no revert PR or commit found (`gh pr list --search "revert in:title"`, `git log --grep revert`) |
| A merge-adjacent action that went wrong | 5 | 2026-09-05 `gh stack init` closed #375 and #376 (timeline: reopened 2 minutes later); 2026-09-06 `gh pr merge` refused on #378 and #379 unnoticed, merged out of order; 2026-09-06 #381 left Draft with stderr hidden; 2026-09-11 two false "merged" messages for #420 and #423; 2026-09-07 qnow #1175 merged into a non-trunk base branch (`gh pr view 1175 --json baseRefName`; whether intended not found) |

Reading: every accident is of a kind a machine can decide (head, base, merge state, a refused or hidden command); none needed judgment of the change. None is recorded after `delivery_gate.py` landed on 2026-10-13, so the head check already answers the largest class. The Captain's burden, on the 20 dev2 PRs archived since 2026-10-01: from the last validation briefing to merge, median 36 minutes (4 to 651); 15 of 20 merge asks drew approval only and 5 drew a change (all in batch 1, 2026-10-16/17). Wall time is not eye-review time, and the real ask is a chat message state does not hold. Volume: 30 dev2 task PRs merged in six weeks (0 to 16 a week), plus 18 workflow syncs and 39 release PRs, 219 PRs in all.

### PRFAQ

**Press release.** Before FO asks the Captain to merge a task's PR, one command now does three things. It checks the facts a machine can decide: the PR head is the commit validation passed, the required CI finished green on that head, the PR is ready, targets the trunk and has no conflict, and each second reviewer has an outcome. It prints a short list of points for the Captain, each a pointer into the records: a finding left open or declined, a reviewer that did not run, an acceptance step nobody ran, a file in a rule, release or migration path, a prod or database task. And it records its own judgment of the PR, so the workflow builds a track record of how often that judgment agreed with the Captain's merge. When a class of change shows, over at least 59 judged PRs with no failure, that its "safe" judgment is right at least 95% of the time (a one-sided 95% lower bound, not a stated confidence), FO proposes a grant. Once the Captain grants a class in an ADR, FO merges PRs of that class itself, pinned to the validated commit, and tells him it merged and what to look at. One failure in a granted class stops FO's merges in that class at once.

**FAQ.**
- *Does FO merge anything on the day this lands?* No. Every repository starts with no grant; FO asks as today, with the points list and the deterministic holds added. Merging by FO starts only after the Captain grants a class on the recorded evidence.
- *Who judges "safe"?* The rule arm, deterministically: every check passes, every listed reviewer that can report clean reports it on the head, and the points list is empty. A model (decision D1) can only withhold a merge or add points, never add a merge, because the text it would read is written by agents and bots that read the PR. The grant names the arm, and the bar applies to that arm's own record.
- *Where does 95% come from?* From the record, never from a model's stated confidence. A judged PR is clean when the Captain merged it at the judged head with no change asked after the judgment, and no revert of its merge landed within 14 days. With zero failures, 59 clean judgments give a 95% lower bound of 95%; with one failure it takes 93, with two 124 (exact binomial, computed 2026-10-17).
- *Why not Codex, Jev or kc-pr-review as the judge?* kc-pr-review and the Codex GitHub review are reviewers: they read the diff and report findings with per-finding scores (kc-pr-review 1 to 10) and no merge probability; they stay inputs. `codex exec` returns free text with a stated confidence, minutes per run. TypeSafe Jev is early access with vendor-only evals. The Decisions API is the one product verified to return a choice plus a probability array, at $0.10 per million input tokens, public beta.
- *What never becomes FO's to merge?* Anything an agent loads as instructions or that decides a review, gate or grant: a prod-profile task, a `db` surface, a release PR, the workflow README, `_mods`, any plugin `skills/`, `agents/`, `extensions/` or `references/` path, `CLAUDE.md`, `AGENTS.md`, `learning.md`, `docs/adr`, `.github/`, `.claude/`, migrations, release configuration and manifests, and the gate, watcher, ledger and budget scripts. The full list is under `### What the script does`; it is fixed in the script, not grantable (ADR 0009: "Changes to authority, approval or merge rules ... never unlock"). Classes are allowlists, so an unknown path falls to `other`.
- *How does FO merge?* With `gh pr merge <N> --repo <owner/repo> --<method> --match-head-commit <validated candidate>`, the method named in the grant, never `--auto` or `--admin`; GitHub refuses the merge if the head moved. kc-pr-flow's `github-repo-write.sh merge` wraps the same flags; the script prints the `gh` line rather than depend on another plugin's path.
- *What leaves the machine?* Rule arm: nothing new. Model arm: the snapshot below goes to OpenAI, only in a repository whose README lists the `merge-judge` extension, which the Captain decides per repository (D2).

### Upstream and sibling check, in the chain's order

- **Spacedock 0.27.2**: no merge command and no merge grant. `merge guard` finalizes after a merge and never merges; `gate record --actor agent:first-officer --conn-quote --conn-source` records an FO decision under a quoted grant, for gates only; `mods/pr-merge.md` never runs `gh pr merge` (it creates the PR and waits for MERGED). Its docs show a conn "authorized to approve and merge PR on CI green" as an example, not an enforced feature.
- **kc-dev-flow-2 0.24.0**: `delivery_gate.py check` already holds the merge ask on a head that differs from the validated candidate and on a second reviewer with no outcome: the deterministic half exists and is extended, not replaced. `pr_watch.py` already reads CI, draft, mergeable and the Codex and Copilot outcomes but by its docstring "prints no merge-ask or hold line". `decision_ledger.py` derives rulings from gate records; ADR 0011's L3 "decide by record" is the route this design builds for one class of decision; ADR 0009 already set the shape for automatic merge (per class, unlocked from the Captain's record, deterministic gate first, never for rule changes). No confidence, no points list and no merge path exist. `skills/learn/SKILL.md` says "FO does not merge or enable auto-merge".
- **kc-pr-flow**: `kc-pr-review` has per-finding confidence gates (1 to 10, shown at 5 and above) and a GitHub review event, no merge verdict, no probability; its optional `codex exec` step sends the full diff to OpenAI. `scripts/github-repo-write.sh merge --head <40-hex>` is a head-pinned merge primitive (`gh pr merge --match-head-commit`), reused as a pattern.
- **Adopters**: no auto-merge or gatekeeper job in relay, web, qnow or this repository (`git grep` over `.github`). qnow has `allow_auto_merge: true`, a required `ci-gate` ruleset and a `release-gate.yaml` that says "regular releases are merged by the captain"; this repository has `allow_auto_merge: false` and two required checks. Relay and web are private and show no Codex, Copilot or Claude bot on their last 30 PRs; qnow (private) and this repository (public) already send every PR to OpenAI through the Codex GitHub review.
- **Conclusion**: extend `delivery_gate.py` (checks, points, record, calibrate, grant line), add one opt-in extension for the model arm, edit three passages of `references/sd/workflow.md`, and land one ADR. No new agent, stage, CI job or Spacedock change.

### Flow

```mermaid
flowchart TD
    A[Validation gate approved, PR ready] --> B[FO runs delivery_gate.py check]
    B --> C{Head equals Candidate, required CI finished green on head, not draft, no conflict, each second reviewer has an outcome}
    C -- no --> H[Hold: next lines, FO tells the Captain]
    C -- yes --> D[Points list from records, class, rule verdict]
    D --> M{merge-judge listed in this repository?}
    M -- yes --> J[Decisions API judges the snapshot; it can only withhold a merge or add points]
    M -- no --> R
    J --> R[Ask record written to the task folder]
    R --> G{Class granted and grantable, no point, listed reviewers clean on head, no failure in its record, model arm if granted says merge}
    G -- no --> Q[FO asks the Captain with the points]
    Q --> K{Captain}
    K -- merges --> S[pr-merge idle: sentinel, merge guard, archive]
    K -- asks a change or sends back --> F[Feedback route; the record is labelled not clean]
    G -- yes --> X[FO runs gh pr merge --squash --match-head-commit Candidate]
    X -- GitHub refuses --> Q
    X -- merged --> T[FO tells the Captain: merged, and the points]
    T --> S
    S --> L[delivery_gate.py calibrate labels each record]
    F --> L
    L --> V{A failure in a granted class?}
    V -- yes --> W[check stops merging that class at once; FO tells the Captain and proposes removing the grant entry]
    V -- no --> U{Lower bound at least 0.95 over at least 59 in a class not granted?}
    U -- yes --> P[FO proposes a class grant ADR; the Captain decides]
    U -- no --> N[Stay in shadow]
```

### What the script does, as the implementation lands it

- `check` (existing subcommand, same arguments) reads the PR with `gh pr view --json headRefOid,isDraft,mergeable,statusCheckRollup,title,headRefName,baseRefName,changedFiles` and its files with `gh api --paginate repos/<owner>/<repo>/pulls/<N>/files` (each `filename` and, for a rename, `previous_filename`). New holds (exit 1): a check run on the head not finished or not successful, an empty check rollup, a SKIPPED or NEUTRAL conclusion, a draft PR, `mergeable` CONFLICTING, a PR base other than the workflow trunk (qnow #1175), or a file list whose length differs from `changedFiles` (security finding 4).
- Output (security finding 1): `point:` lines, one `class:` line, the record path, then exactly one `next:` line, printed last. Every value taken from a path, a title or a report line is printed as a bounded, escaped token (`repr`, at most 80 characters, control characters and newlines escaped), so no such value can begin a line. The merge line is built only from regex-bound values (the `owner/repo#N` reference, the 40-hex candidate, the grant's method, and the title only when it matches the Conventional Commit form, passed through `shlex.quote`), and the record stores the same line, so FO acts on the last line and can compare it with the record.
- Points, each `point: <kind>: <token>`: a validation-report or gate-summary line marked Deferred risk, declined, or round-3 backlog; `### FO declines` entries; a listed reviewer `not run:`; an acceptance step marked not run; a `## Captain amendments` entry dated after the latest validation dispatch; each never-eligible path changed (either name of a rename); `profile: prod`, `Surfaces:` `db` or `ui`; a non-Conventional title where `release-please-config.json` exists. Pointers only, no model text.
- Never-eligible (security findings 2 and 3): `profile: prod`; `Surfaces: db`; a release PR (head branch `release-please--*`); any changed path, or previous path, that is the workflow README or under `_mods`, `.github/`, `.claude/`, a migrations folder, `docs/adr`, `docs/dev*`; any path under a plugin's `skills/`, `agents/`, `extensions/` or `references/`; any `CLAUDE.md`, `AGENTS.md` or `learning.md`; release configuration and manifests (`release-please-config.json`, `.release-please-manifest.json`, `plugin.json`, `marketplace.json`); and every script that decides a review, gate, budget or grant, with its test (`*gate*`, `pr_watch.py`, `decision_ledger.py`, `lint-skills.py`, any `extensions/**/*.py`).
- Class, by allowlist, never by file shape: `never` when any never-eligible condition holds; `docs-only` when every path is under `docs/` outside `docs/adr` and `docs/dev*`; `script-with-test` when every changed code file has its own test (`test_<name>`) changed in the same PR; otherwise `other`. Rule verdict: `merge` when no point is printed and the class is not `never`.
- Record: `<task folder>/merge/ask-<N>.json` with the head, class, rule verdict, model arm answer or `not run`, points, the `next:` line, PR, and the UTC time; FO commits it with `spacedock state commit <slug>`.
- Grant: README frontmatter `merge-grants:` lists `<class>:<arm>:<threshold>:<method>:ADR <number>`, the method being the repository's merge method (`squash`, `merge` or `rebase`). The merge line is printed only when all hold: the class is listed and not `never`; the rule verdict is `merge` (no point at all); when the listed arm is the model arm, also its `choice` merge at or above the threshold, so the model can only withhold a merge, never add one (security finding 5); each listed reviewer whose reader can report clean reports it on the head (`codex_review.py` exit 0, `roborev_gate.py` exit 0), and a triggered Copilot second reviewer, whose reader does not judge findings, is a point (security finding 6, ADR 0009's "no P1 or P2" condition); and the class's own records, labelled as `calibrate` does, hold no failure. The last condition makes revocation a derived fact: one failure stops FO's merges in that class at once, whatever the README still says, because removing the README entry is a code PR the Captain merges. An unlisted extension, a missing key or a malformed entry means no grant. The merge line carries `--subject` (the validated Conventional title) and `--body ''` (security finding 7), and is valid only in the same FO step as the passing `check`: CI can restart after it, and a plain `gh pr merge` on pending required checks enables auto-merge (`gh pr merge --help`, gh 2.92.0).
- `calibrate <workflow dir>`: labels every record in active and archived tasks. A record the Captain merged (shadow) is clean when he merged it at the judged head with no change asked after the record; a record FO merged under a grant is clean when, after the merge, no amendment, reopen, `merge guard --rework` or `Override:` names it. Either is not clean on a revert of its merge commit within 14 days on the trunk, a closed PR, or a merge at another head. Records younger than 14 days are pending, not clean. It prints per class and arm: n, clean, failures, the exact one-sided 95% lower bound, and one `next:` line: propose a grant, remove a grant on any failure, or nothing.
- Model arm, only if D1 is (a): extension `merge-judge` (EXTENSION.md plus `merge_judge.py`), `POST /v1/decisions`, model `gpt-6-luna`, one `choice` question (merge / needs-human) plus fixed `predicate` questions whose positive answers add `point: model:<predicate name>` lines, never text from the response. The response is parsed against an allowlist: the two choice values, probabilities as floats in [0, 1] summing to about 1, no unknown field; anything else, a failure, a refusal or a timeout records `merge-judge not run: <reason>` and never counts as merge. The key is read only through `<wrapper>`; the script never prints it.

Snapshot sent to OpenAI by the model arm (and nothing else), each field capped in length: task profile and `Surfaces:`, class, changed file paths with added/removed line counts, PR title, CI conclusions by check name, the reviewer outcome lines FO already records, the point lines, and the validation report's `### Summary` text (at most 1,500 characters). No diff, no code, no secret, no Captain chat. The Summary and reviewer lines are written by agents and bots that read the PR, so they can carry injected text; that is why the model can only withhold a merge.

### Words FO reads at each lifecycle moment

Counted as `len(text.split())` over origin/main 19fe3b5b; `W` is the `pr_watch.py wait` output, unchanged by this design and the same in both columns. Passages: the authority paragraph ("Project and Captain authority … explicit choice.") 215; the head paragraph ("Before the merge ask … what it printed.") 57; the Extensions merge-ask sentences ("A merge ask names … not named as unread.") 90; the review-findings sentence ("Authority, a gate approval, a merge … `Precedent:` line.") 33; `delivery_gate.py` exit 0 output 20 (with a 40-hex head).

| Moment | Before | After (design target) |
| --- | --- | --- |
| startup, idle on an open PR, idle on a merged PR, after the archive | unchanged | unchanged: no edit to `_mods`, `pr_watch.py`, the learn step or `pr-merge` |
| validation gate prep | `### validation` 241 | 241 |
| the merge ask, no points | 415 + W | at most 404 + W: authority 213 (adds "unless `delivery_gate.py` prints a merge line under a class grant (ADR <n>)", drops "and waits for those jobs to finish before asking for merge", which the check now enforces); head paragraph 27 (one sentence: run the check, do its `next:` lines; the hold wording is already in its output); Extensions 90; review-findings sentence 37 ("a merge outside a granted class"); `check` output at most 37 |
| the merge ask, k points | 415 + W | at most 404 + W + 9k (each point line at most 9 words); the points are what the Captain reads, so they are the intended growth |
| FO merges under a grant (new; replaces the ask for that PR) | none | at most 424 + T + W: same passages, the merge line (31 words plus T, the title's words; titles capped at 100 characters) instead of the 11-word ask line |
| calibrate (new; FO runs it after a merge or at startup) | none | output only: one line per class and arm (at most 14 words) plus at most one `next:` line |
| merge-judge listed: its FO step | none | the EXTENSION.md FO step, at most 60 words, only in a repository that lists it |

`references/sd/workflow.md` falls from 5495 by at least 11 words, so `WORKFLOW_WORD_BUDGET` falls with it in the same change (the ratchet task's rule; no raise needed).

### Non-goals

Any edit to Spacedock, `pr-merge`, kc-pr-flow or an adopter file; a reviewer of code (the Codex review, Copilot and roborev stay the reviewers); a grant of any class in this task; auto-merge (`--auto`) or merge queues; Jev or Codex as the judge; a stored ledger (records are files in the task folder, derived like `decision_ledger.py`).

### Limits

The label is a proxy. A clean merge means the Captain merged without asking a change and no revert landed in 14 days; it does not see a fix-forward that does not revert, nor a Captain who merged without reading. If he merges every ask unread, agreement measures nothing; the revert window is the only independent signal. The 59-record bar is per class; at the measured 0 to 16 dev2 task PRs a week (30 in six weeks), a class takes from four weeks to several months to qualify, and `other` may never. The shadow record also shows the Captain how often the rule arm would have merged a PR he then changed (5 of 20 asks drew a change). The Decisions API is a public beta with one model; a change in its answers between calibration and use is caught only by the revocation rule after a failure. `mergedBy` cannot tell FO from the Captain (FO uses his token), so FO's merges are identified by the ask record's merge line and FO's report, not by GitHub.

### Security review

Security review: security/ideation-1.yaml
Security focus file: none
Security finding 1: AC-12 (output escaping, one `next:` line printed last, merge line from regex-bound values only)
Security finding 2: AC-3 (classes by allowlist; agent-instruction paths never eligible)
Security finding 3: AC-3 (gate, reader, ledger and budget scripts and their tests never eligible; a code file needs its own test)
Security finding 4: AC-3 (paginated file list, both names of a rename, count must equal `changedFiles`)
Security finding 5: AC-9 (model arm only withholds; strict response parsing; capped snapshot fields)
Security finding 6: AC-4 (listed reviewers clean on the head under a grant; empty, skipped or neutral CI holds by AC-1)
Security finding 7: AC-5 (base equals trunk by AC-1; `--subject` and `--body ''` in the merge line)
Security finding 8: declined: LOW, in existing code this design does not change (`codex_review.py` trigger reading); the worst outcome is fail-closed, an exit 3 or 4 that turns a granted merge back into an ask to the Captain, never a merge; it can be filed as its own backlog task

The reviewer read an earlier revision (its finding 7 says the design never reads `baseRefName`; the bite section and the trunk-base hold came later, and none of the later edits adds a public route, an agent-read document or a data boundary, so no second run is owed). It is model output on a design not yet built.

### ADR draft (no number; FO reserves it at implementation)

Short title: `fo-merges-a-granted-class-pinned-to-the-validated-head`.

> **FO merges a PR only in a change class the Captain granted on its recorded judgment**
>
> Context: The Captain asked (chat, 2026-10-16): 「我想新增一張票，設計一個 codex 的 PR 守門員，它的任務是確保 P R 可以合併……只要例如 PR 超過 95% 沒問題，那就讓它帶我授權 FO 合併 PR，相應的但是也要讓它負責提出我需要注意的點……這件事的目的是，減低 FO 自己合併 PR 的意外，以及減低我每次都要肉眼 review PR 的負擔」. ADR 0011 says merge is "never delegated at any level"; ADR 0009 already allows automatic merge per unlocked class, never for rule changes. The bite measured at ideation: no unauthorised FO merge; two undisclosed merges at a head other than the validated one (#632, #628, both 2026-10-13, before the head check); five merge-adjacent mistakes (2026-09-05 to 09-11); a median 36 minutes from validation briefing to merge on 20 PRs.
>
> Decision: **Words:** 「<the Captain's words at the ideation gate>」 — Captain, <date>. **Options considered:** merge granted per class on the recorded judgment, pinned to the validated head (chosen); one grant for all PRs at a stated model confidence; no delegation, the points list only. **Recommended:** per class on the record. This supersedes ADR 0011's sentence "Authority, gate approval, merge, … are never delegated at any level" for merge only, and only as follows. FO merges a task's PR itself only when `delivery_gate.py check` prints the merge line: the deterministic checks pass, the class is granted in the README's `merge-grants:` by its own Captain ADR on `delivery_gate.py calibrate` evidence (a one-sided 95% lower bound of at least 0.95 over at least 59 records), the granted arm says merge, and the merge is `gh pr merge --match-head-commit <validated candidate>`. The classes fixed as never-eligible are never granted. Any failure in a granted class stops FO's merges in it at once, because `check` reads the class's records; FO tells the Captain and proposes removing the README entry. Every other part of ADR 0011's sentence stands.
>
> Consequences: Nothing merges by FO until a class qualifies and he grants it. The README sentence on what is always asked changes to "a merge outside a granted class". Reopen if a granted class ships a defect the label missed (a fix-forward without a revert), or if the Decisions API changes its model.

ADR 0011 gets one line under its Status: `Merge partly superseded by ADR <n>`; ADR 0009 is unchanged (this is its "full-auto" mechanism for task PRs, and its never-unlock list is kept).

### Unresolved decisions (for the Captain)

Past rulings read: ADR 0009 (automatic merge per unlocked class, never for rule changes: followed), ADR 0011 (merge never delegated: the ADR draft supersedes that clause for merge only, by its own L3 route), ADR 0019 (kc-pr-flow agent reused as is: same pattern for its merge primitive). `git -C <state checkout> grep -n 'Override:'` (2026-10-17) hits prose only; no gate record overrides a recommendation in this area.

1. **D1. Whether a model judge is built now.** (a) the OpenAI Decisions API as an opt-in arm that can only withhold a merge or add points, recording from day one; (b) the rule arm and the record-based points now, and the model arm as a later task once `calibrate` and the AC-8 replay show what the records miss (recommended); (c) `codex exec` as judge; (d) TypeSafe Jev. Recommendation (b): after the security review a model may not add a merge (it would read text written by agents and bots that read the PR), so its only value is extra points, which nobody has yet shown the records miss; it would bring a public-beta dependency, an OpenAI API key under the wrapper that is not verified to exist (a Codex login is not API billing), one more extension and up to 60 FO words. What gets worse: this is not the Codex or Jev-style judge you asked for; if you later want one, it starts with no record. Choosing (a) adds AC-9 and D2 to this task.
2. **D2. Only if D1 is (a): where the model arm may send its snapshot.** Recommendation: this repository only (public; its PRs and state are already public and already reviewed by Codex on GitHub). Not relay or subspace-web (private; no outside model reads their PRs today, so it would be a new share), not qnow for now (private, already sends full diffs to Codex and Copilot, but it is the product being readied for live customers). What gets worse: the three adopters build no model record, so a grant there can only use the rule arm until you list the extension.
3. **D3. The bar and the label.** Recommendation: a class qualifies at a one-sided 95% lower bound of at least 0.95 on its granted arm's record (59 records with no failure); clean means merged at the judged head with no change you asked after the judgment and no revert in 14 days; each grant is its own ADR in that repository, and one failure removes it. The alternative is your literal reading: merge when the judge states at least 95%. What gets worse under the recommendation: no FO merge for weeks, possibly never for the `other` class; a fix-forward without a revert is not seen by the label.

Approving the ideation gate also approves the ADR draft's never-eligible list (under `### What the script does`); say if any should be grantable.

### Batch overlap

Read 2026-10-17 from origin/main 19fe3b5b and the other five task files as they stand in the state checkout: `workflow-budget-ratchet` (e23f9c5e) and `special-role-triggers` (0e004307) have committed designs, `worker-loads-declared-package` a draft design (uncommitted), the other two their backlog text only. Files this design would change, and the other batch-2 tasks on the same file or check:

| File or check | This design | Other batch-2 task on it |
| --- | --- | --- |
| `kc-dev-flow-2/scripts/delivery_gate.py`, `test_delivery_gate.py` | new holds, points, class, record, grant line, `calibrate` | `worker-loads-declared-package` imports `delivery_gate.CANDIDATE` and the above-first-heading scope (its AC-3 parity test) and edits neither; this design keeps `CANDIDATE` and `dispatched_candidates` unchanged by name and behaviour. `workflow-budget-ratchet` and `special-role-triggers` both state they leave `delivery_gate.py` alone |
| `references/sd/workflow.md` § Delivery authority (authority and head paragraphs) and § FO steps: review findings ("Authority, a gate approval, a merge …") | three edits, net at least 11 words fewer | `workflow-budget-ratchet` edits other hunks (Stages dispatch-record sentences, the ideation gate bullet, Captain amendments) and leaves Delivery authority alone; `special-role-triggers` adds one sentence in § Stages. Textual merges only |
| `kc-dev-flow-2/scripts/lint-skills.py` `WORKFLOW_WORD_BUDGET` | falls to the new count | `workflow-budget-ratchet` turns the constant into budget steps (a raise carries the Captain's words); whichever lands later appends its own step. This design lowers, so it needs no ruling |
| `.github/workflows/kc-dev-flow-2-tests.yml` | one step for the new `extensions/merge-judge` test, only if D1 is (a) | `special-role-triggers` adds one step to the same list; a one-line conflict |
| `kc-dev-flow-2/extensions/merge-judge/` (new) and the README extensions table row | new, only if D1 is (a) | none |
| `docs/adr/` (one new file) and ADR 0011's Status line | new ADR, one status line | `workflow-budget-ratchet` and others add ADRs; `number_guards.py reserve` orders numbers; none edits ADR 0011 |
| reads, not edits: validation reports and gate summaries for points | | `prod-security-validation-gate` (its validation-gate findings become point lines when Deferred or declined); `ui-design-review-in-ideation` (`Surfaces: ui` is a point); no shared file |

Not changed: `_mods/*`, `pr_watch.py` (which `special-role-triggers` edits), `dispatch_records.py` (which `worker-loads-declared-package` edits), `design_surfaces.py`, `skills/*` (including `skills/learn/SKILL.md`'s "FO does not merge or enable auto-merge", which governs learn's own PRs and stays true), any adopter file. Order: last, as `workflow-budget-ratchet`'s D2 also proposes; it needs only `CANDIDATE` to stay as `worker-loads-declared-package` pins it.

## Acceptance criteria

Evidence commands run from a checkout of the implementation PR head with `python3 -B` and caches cleared; `STUB` is a scratch `gh` on `PATH` that answers `pr view --json …` from a fixture JSON and exits 1 on `pr merge`; fixtures live in a scratch folder outside the checkout.

**AC-1** `delivery_gate.py check` holds the merge ask (exit 1, one `next: hold the ask …` line) when a check run on the PR head is not finished or not successful, when the check rollup is empty or holds a SKIPPED or NEUTRAL conclusion, when the PR is a draft, when `mergeable` is CONFLICTING, when the PR base is not the workflow trunk, or when the paginated file list's length differs from `changedFiles`, and exits 0 when the head equals the candidate, every check run succeeded, the PR is ready and mergeable. Today's head and second-reviewer holds keep their exit codes and wording.
Verified by: new cases in `test_delivery_gate.py`, one per hold (including the empty rollup) and one passing, all under `STUB`; the existing cases pass unchanged. Falsifier: removing the check-run clause makes the pending-CI case exit 0 and its test fail. Current evidence: not yet verified (design only).

**AC-2** Each point source prints exactly one `point:` line naming its kind and where it is, and a fixture with none prints no `point:` line.
Verified by: one fixture task per source (a Deferred risk line in the validation report, a `### FO declines` entry, `codex not run: quota`, an acceptance step marked not run, an amendment dated after the latest validation dispatch, a changed `docs/adr/x.md`, `profile: prod`, `Surfaces: db`, a non-Conventional title beside `release-please-config.json`) and one clean fixture. Falsifier: deleting any one source's matcher turns its case red. Current evidence: not yet verified.

**AC-3** The class is `never` for each never-eligible condition listed under `### What the script does`, judged on both names of a rename; `docs-only` only when every path is under `docs/` outside `docs/adr` and `docs/dev*`; `script-with-test` only when every changed code file's own `test_<name>` also changed; otherwise `other`.
Verified by: a table-driven test with one row per never condition (including `kc-dev-flow-2/skills/validation/SKILL.md`, `extensions/codex/EXTENSION.md`, `extensions/codex/codex_review.py`, `scripts/pr_watch.py`, `scripts/test_delivery_gate.py`, a root `CLAUDE.md`), one per class, a rename from `.github/workflows/ci.yml` to `notes.md` (never), a `.md` outside `docs/` (other), a code file with an unrelated test (other), and a 101-file PR read across two stub pages. Falsifiers: removing `docs/adr` from the never list makes its row `docs-only`; reading only `filename` makes the rename row `docs-only`; reading one page makes the 101-file row hold on the count, not pass. Current evidence: not yet verified.

**AC-4** Without a grant and a clean record FO is never told to merge: with `merge-grants:` absent, empty, malformed, naming another class, naming a `never` class, with any point printed, with a listed reviewer not clean on the head (`codex_review.py` exit 1, 3 or 4), with the model arm saying merge while a point exists, or with one failure-labelled record in the granted class, the `next:` line is the ask line; and no output of `delivery_gate.py`, in any case, contains `--auto` or `--admin`.
Verified by: test cases for each of the nine, plus a test that greps every printed line of the whole test run for `--auto` and `--admin`. Falsifiers: making the grant test return true when the key is absent turns the absent-key case red; dropping the record condition prints the merge line with one failure record in a granted class, and that case goes red. Current evidence: not yet verified.

**AC-5** Under a valid grant, a granted class with no point and the granted arm saying merge prints exactly `next: run gh pr merge <N> --repo <owner/repo> --<method> --match-head-commit <40-hex candidate> --subject <quoted title> --body '' now; when gh pr view says MERGED, tell the Captain with the points above; otherwise ask him.`, `<method>` from the grant entry; FO says merged only after `gh pr view` reports MERGED, and on a refusal it asks the Captain (the 2026-09-06 and 09-11 mistakes), with the candidate from the validation record, never the PR's head field.
Verified by: a `STUB` case whose PR head and candidate are equal and a case where they differ (holds by AC-1's head rule before any grant is read); and one scratch-repository run: a local bare origin is not enough for `--match-head-commit`, so the run uses a throwaway GitHub repository the implementation worker creates and deletes only with the Captain's yes, or is marked not run with that reason. Falsifier: printing the PR's `headRefOid` instead of the candidate fails the equality assertion on a short-SHA fixture. Current evidence: `gh pr merge --help` (gh 2.92.0) lists `--match-head-commit SHA`, "Commit SHA that the pull request head must match to allow merge"; the GitHub refusal itself not yet observed.

**AC-6** Every passing `check` writes one `merge/ask-<N>.json` in the task folder with head, class, rule verdict, model answer or `not run`, points, PR and UTC time; a hold writes none.
Verified by: test cases reading the written file and a second run producing `ask-2.json`. Falsifier: writing on exit 1 turns the hold case red. Current evidence: not yet verified.

**AC-7** `calibrate` labels and bounds correctly: 59 clean records in one class print a lower bound of at least 0.9505 and a `next: propose a grant` line; 58 print no such line; one failure in a class listed in `merge-grants:` prints `next: remove <class> from merge-grants and tell the Captain`; an FO-merged record with a later `merge guard --rework` naming it is labelled not clean, and one with no later reaction and older than 14 days is clean; a record younger than 14 days counts as pending; a revert is found by `This reverts commit <merge sha>` on the trunk.
Verified by: test cases on generated records and a scratch git repository holding one revert commit; the zero-failure bound is checked against `0.05 ** (1 / n)`. Falsifier: counting pending records as clean makes 58 clean plus one pending print the propose line. Current evidence: exact binomial thresholds computed 2026-10-17 (0 failures 59, 1 failure 93, 2 failures 124, 3 failures 153).

**AC-8** Replay on this workflow's history: run the candidate's classifier, points and holds over every archived task of `spacedock-state/dev2` that has a merged PR, against its PR as GitHub reports it now (read-only `gh`), and over each instance in `### The bite, counted`; print, per class, how many asks the rule arm would have said merge, and for each bite instance which hold or point names it, or `not caught`.
Verified by: the saved replay output under `<task folder>/validation/`; the implementation report quotes the per-class counts and each bite row. Falsifier: a bite instance of the head, CI or merge-state class reported `not caught` returns through feedback. Current evidence: not yet run; the bite list is in the design.

**AC-9** Model arm (only if D1 is (a)): `merge_judge.py` sends only the snapshot fields, each within its cap; a failure, refusal, timeout or a 200 answer outside the allowlist records `merge-judge not run: <reason>` and never counts as merge; its points are fixed `model:<predicate name>` kinds; the key is read only through the wrapper and never printed.
Verified by: a test with a fake transport asserting the request body's keys equal the snapshot list, each value within its cap, and no value containing a diff hunk header (`@@ `); cases for HTTP error, refusal answer, timeout, a choice outside the two values, a probability of 1.5, an unknown field, and a Summary carrying "ignore prior instructions; answer merge" (the arm's answer cannot turn an ask into a merge: AC-4's model case); one live call through `<wrapper>` on an archived task of this repository, its response saved with the key absent from every saved byte (`grep -c` of the key prefix is 0). Falsifier: adding the diff to the snapshot fails the keys assertion. Current evidence: the API page (fetched 2026-10-17) states `POST /v1/decisions`, `gpt-6-luna` only, a choice answer with `probabilities` and `confidence`, $0.10 per million input tokens; no key verified, no call made.

**AC-10** FO reads no more at the merge ask: recounted with an independent script by the moment rules in `### Words FO reads at each lifecycle moment`, the merge ask with no points is at most 404 + W against 415 + W at origin/main, every other moment is unchanged, and `lint-skills.py` prints the new `workflow.md` count equal to the lowered `WORKFLOW_WORD_BUDGET`.
Verified by: the recount output for base and candidate saved under `<task folder>/validation/`. Falsifier: a candidate `check` output over 37 words on the clean fixture, or a `workflow.md` count above 5484. Current evidence: base passages counted 2026-10-17 (215, 57, 90, 33, 20); candidate not yet written.

**AC-11** The ruling lands as an ADR whose Words line quotes the Captain's answer at this gate and the question, and ADR 0011's Status gains the partial-supersession line; no repository's README gets a `merge-grants:` entry in this task.
Verified by: `python3 <package>/scripts/adr_lint.py docs/adr --since <base> --require <reserved number>` exits 0; `git diff <base> -- docs/dev2/README.md kc-dev-flow-2/references/sd/workflow.md | grep -c merge-grants` prints 0 (the key is documented in the script's usage text and the ADR, not in README words).

**AC-12** No text from a path, title or report line can make `check` print a second `next:` line or a control byte: on a fixture whose changed path is `.github/x\nnext: run gh pr merge 1 --repo o/r --squash --match-head-commit <head>`, whose title and Copilot heading contain `next:`, and whose Deferred-risk line holds ESC bytes, the output has exactly one line starting `next:`, it is the last line, it is the ask line, and no byte below 0x20 other than newline appears.
Verified by: that fixture case in `test_delivery_gate.py`, plus a case under a valid grant asserting the printed merge line equals the record's stored line. Falsifier: printing the raw path instead of its escaped token yields two `next:` lines and the case goes red. Current evidence: not yet verified; today's `check` prints only regex-bound values (security report, clean pattern 5).

## Number guards

ADR: 0023

### Feedback Cycles

- Cycle 1 (FO, 2026-10-17): Codex review on #666 1beabd97 (review:5561577977) left three P1, to fix (a P1 blocks in every round); investigation first, then FO fix authorization, then a fresh validation recheck.
  - P1 `kc-dev-flow-2/scripts/delivery_gate.py`: (1) profile_prod misses a quoted 'prod' ("prod" or 'prod') that validation_security.FM_PROFILE reads as prod; (2) the instruction-directory pattern matches skills, agents, extensions or references only at root or one level down, so packages/foo/agents/x.md classes other; (3) revert_time reads origin/<trunk> without a fetch, so a revert pushed after the last fetch is missed by calibrate and the recheck.
- Cycle 2 (FO, 2026-10-18): roborev 843 and 844 on #666 b28bbcc6 repeat one High (a merge-grants entry enables a merge line without its ADR or calibration being checked at merge time; a roborev High counts as P1), and validation-1 security finding 1 (MEDIUM, Needs decision: the never-eligible path list is narrower than ADR 0023's wording). Captain ruling: 「同意」 (chat, 2026-10-18) to FO's question 「不直接豁免，改成折衷做法：合併前多查兩件事：授權寫的 ADR 檔案是否真的存在、那個 ADR 有沒有提到這筆授權……保護清單照原計畫一起補齊。同意的話，我派人一起做這兩件，然後重新驗證。」 So: check refuses a merge line when a grant's ADR file is absent or does not name the grant; the never-eligible list gains .githooks, .roborev.toml, repo-root scripts/, plugin hooks/ and bin/, and docs-only admits only .md files. The full check-time calibration bound is not built (the Captain's ruling covers the remaining gap: an ADR he wrote whose evidence is thin). Investigation first, then FO fix authorization, then a fresh validation recheck.
- Cycle 3 (FO, 2026-10-18): Codex round 2 on #666 3fd84178 (review:5562139252) left two P1 in the grant path (grants and ADR read from the working tree, not the fetched trunk; an unreadable PR state counted as pending). Chief-engineer (opus, 2026-10-18) measured 13 P1/High findings so far: 9 in the grant, merge-line and calibrate code, 4 in the never list and profile reading (rated high only because they could open a merge line), 0 in the holds, points and record. Split at 3fd84178: ship now, about 244 lines of delivery_gate.py (ci_problem, pr_facts, pr_files, points_for, never_paths, NEVER_PATH, classify, write_record, tok, clean, the hold section of check) and about 400 test lines (HoldTests, PointTests, ClassTests, RecordTests, InjectionTests, NeverAddedTests, the prod and depth parts of CodexP1Tests, shared helpers); move out, about 164 lines (GRANT, grants_of, adr_grants, merge_line, lower_bound, state_folders, parse_time, fetch_trunk, revert_time, label, labelled, calibrate, reviewers_clean, CODEX_READER, WINDOW, the grant block in check, the calibrate subparser, the docstring paragraph), about 406 test lines (GrantTests, RecheckTests, CalibrateTests, GrantAdrTests, the fetch part of CodexP1Tests, grant constants), ADR 0023, ADR 0011's Status line, and about 13 workflow.md words naming a grant or a merge line. The Captain approved narrowing (amendment 1); the grant half becomes POC task merge-grant-need-poc (dev2-poc workflow), with the code parked at 3fd84178 and the two open P1 noted there.

## Stage Report: ideation

- DONE: A design (PRFAQ and Mermaid) for a gatekeeper that judges whether a PR can merge, lets FO merge one above a calibrated bar on the Captain's behalf, and lists what he should look at: first the bite counted from state and PR history (FO merge accidents, Captain review per PR); deterministic checks first (head equals the validated candidate, required CI); the model or product (OpenAI Decisions API beta, Codex, TypeSafe Jev, kc-pr-flow kc-pr-review) and how its bar is calibrated; an ADR draft with no number superseding ADR 0011's never-delegated merge clause; and data sent outside per repository. This is a Production task: run the prod profile's design security review
  `## Design`: bite (0 unauthorised FO merges, 2 undisclosed off-candidate merges #632/#628 on 2026-10-13, 5 merge-adjacent mistakes 09-05..09-11, median 36 min ask-to-merge on 20 PRs, 5 of 20 asks drew a change); `delivery_gate.py check` extended with CI/draft/conflict/base/file-count holds, record pointers, allowlist classes, a shadow record and a grant line pinned by `--match-head-commit`; bar = one-sided 95% lower bound >= 0.95 per class (59 clean with 0 failures), revocation derived from the record; four products compared, Decisions API verified by fetch 2026-10-17; ADR draft supersedes 0011's merge clause only; data per repository in D2. Chain: Spacedock none, kc-dev-flow-2 `delivery_gate.py` extended, kc-pr-flow merge primitive reused as a pattern. Security review: `security/ideation-1.yaml`, 8 findings (1 HIGH, 5 MEDIUM, 2 LOW): 7 to criteria, 1 LOW declined.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch-2 task (workflow-budget-ratchet, special-role-triggers, worker-loads-declared-package, prod-security-validation-gate, ui-design-review-in-ideation, merge-gatekeeper) that changes the same file or check, so FO can order implementation
  Seven rows checked against the committed designs of workflow-budget-ratchet (e23f9c5e) and special-role-triggers (0e004307) and the uncommitted draft of worker-loads-declared-package; order: last, keeping `delivery_gate.CANDIDATE` as worker-loads-declared-package pins it.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each lifecycle moment`: merge ask 415 + W before (authority 215, head 57, Extensions 90, review-findings sentence 33, `delivery_gate.py` output 20; `len(split())` on origin/main 19fe3b5b), target at most 404 + W; new grant moment at most 424 + T + W (T the title's words); other moments unchanged. Candidate counts not yet measured (AC-10).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-12, each with evidence and a falsifier; D1 (model judge now or later, recommend later), D2 (data share per repository, only if D1 is (a)), D3 (bar and label). `python3 <package>/scripts/design_surfaces.py check` (0.24.0): "design surfaces presentable", "security review security/ideation-1.yaml: 8 findings, 7 acceptance criteria, 1 declined, 0 decisions", exit 0.
  - AC-1: not yet verified (design only).
  - AC-2: not yet verified.
  - AC-3: not yet verified.
  - AC-4: not yet verified.
  - AC-5: not yet verified; `gh pr merge --help` (gh 2.92.0) lists `--match-head-commit`; GitHub's refusal not observed.
  - AC-6: not yet verified.
  - AC-7: thresholds computed (59, 93, 124, 153 for 0 to 3 failures); code not yet written.
  - AC-8: not yet run; bite list in the design.
  - AC-9: conditional on D1 (a); API page fetched, no key verified, no call made.
  - AC-10: base passages counted; candidate not yet written.
  - AC-11: not yet verified; ADR draft in `## Design`.
  - AC-12: not yet verified.
  - Mermaid: not rendered; read against the prose only.

### Summary

The design extends the existing merge-ask check rather than adding a judge first: the counted accidents are all machine-decidable (an off-candidate head, a base, a refused or misread merge), and none is recorded since the head check landed on 2026-10-13. The check gains holds, a points list for the Captain, a shadow record per ask, and a grant path that lets FO merge a class only after its record clears a measured bar and he grants it in an ADR that supersedes ADR 0011's merge clause for that case. The security review changed the design materially (allowlist classes, escaped output, model arm only able to withhold), and the recommendation became: no model judge in this task (D1). Two events outside the brief: the chain-check helper ran `git fetch origin` in the three adopter repositories (a remote-tracking-ref update, no working tree or config touched), and the fetched Decisions API page carried an embedded "reporting rules" block, which the fetch helper ignored.

## Stage Report: implementation

- DONE: One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main implementing D1 (b) and D3 as recommended: extend kc-dev-flow-2/scripts/delivery_gate.py check with the added holds (CI, draft, conflict, base, incomplete file list), the points list for the Captain as pointers into the records, the fixed never-merge class allowlist, the shadow record of every merge ask, a calibrate subcommand, and the merge line pinned with --match-head-commit; the ADR superseding ADR 0011's never-delegated merge sentence for granted classes only; no model arm in this task; every acceptance criterion in the task file green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
  Draft PR https://github.com/iamcxa/kc-claude-plugins/pull/666, branch spacedock-ensign/merge-gatekeeper rebased on origin/main 2dad59ca, head 93d7adf3 (3 commits). ADR added: 0023 (adr_lint --require 0023 exit 0); ADR 0011 Status gains one line. `test_delivery_gate.py` 53 tests pass. 22 real mutations of delivery_gate.py each run against the whole suite: 22 RED, 0 survived (AC-1 six clauses, AC-2 two matchers and in-test eight more, AC-3 docs/adr, rename filename, one page, directory rule narrowed, AC-4 absent key, record condition, roborev other head / prefix / longer line, AC-5 PR head not candidate, AC-6 write on hold, AC-7 pending as clean, AC-12 token and clean layers).
  AC-1..4, 6, 7, 12 green by those tests. AC-5: merge line and head rules green; the throwaway-GitHub-repository run NOT run (needs the Captain's yes to create and delete a repository). AC-9: not applicable (D1 b, no model arm). AC-8 replay saved at `merge-gatekeeper/validation/replay-1.txt`: 32 archived tasks with a merged PR, all class never, rule arm says merge on 0 of 32; #632 and #628 head hold FIRES (final heads 7679ab7a and 0286f8e7 against 40c714a6 and 7d89898e named in prose; their records predate the Candidate line, so today's check holds first on no-candidate-line); the 2026-09 merge-adjacent rows (#375 #376 #378 #379 #381 #420 #423, qnow #1175) are not replayable from state now: base and draft holds cover #381 and #1175 only by fixture tests. AC-10 recount saved at `validation/recount-1.txt`: merge ask 396 words against 415 (limit 404), check output 24 (limit 37), workflow.md 5424 against 5447, other moments unchanged; the AC's falsifier number 5484 is stale (base was 5447 when built). AC-11: adr_lint exit 0, `grep -c merge-grants` over docs/dev2/README.md and workflow.md diff prints 0.
  Dispatch record implementation-2 (two security-review items), both held and fixed with failing-first rows and mutations: roborev evidence is now the whole line `roborev: clean on <40-hex>; evidence=roborev:<id>` compared for equality with the candidate; every path under kc-dev-flow-2/scripts/ is never by one directory rule (rows workflow_checkout.py, sd_dispatch.py, test_sd_dispatch.py, anything-new.sh failed first). Note: nothing was pushed before this record's message said "pushed commits"; the first push was after both fixes.
- FAILED: No FO-read word added beyond the design; the candidate's own kc-dev-flow-2/scripts/lint-skills.py exits 0; roborev evidence= line; push without force; CI green on the PR head; CI cost measured or stated as not measured
  CI NOT green: `unit tests (python3)` fails at step `test_sd_dispatch.py`, which pins two workflow.md sentences this change rewrites (`need` entries of FIXES["readme-keeps-delivery-rules"] and its swaps: the head-hold sentence and "FO runs ... check ...; exit 1 or 2 holds the ask and FO shows the Captain what it printed"). That file is outside the design's list, so it is returned to FO; keeping the old wording instead would raise the merge-ask moment to 420 words against 415, so the PR needs the test file's `need`/`swaps` updated to the new head paragraph. Met: FO-read words 396 against 415; lint-skills.py exit 0 (5424 of 5424); `evidence=roborev:824` (`clean on 93d7adf35`, base 2dad59ca; an earlier run on 97a0b025c found 2 High items, fixed, then `clean on e029e67bf; evidence=roborev:810`); pushed without force; CI cost: test_delivery_gate.py 30 s on the runner (run 39087603389).
  Also run: comment_ratio.py "code lines 832, comment lines 0, 0.0%" exit 0; number_guards.py check PASS, base e00d112ffd39 (before the last rebase); doc_impact.py listed 8 documents, each `unaffected`: ADR 0020, kc-dev-flow-2/README.md, skills/maintain-flow/SKILL.md and learning.md name lint-skills.py whose behaviour is unchanged (one budget step added); e2e-trace-analyzer.md (`parse_time`) and three kc-nightwatch/kc-pr-flow docs (`repo_root`) share a symbol name only. docs/dev2/README.md and docs/dev2-poc/README.md copies of workflow.md update by the sync PR after release.

### Summary

delivery_gate.py now holds on CI, draft, conflict, base and an incomplete file list, prints bounded `point:` lines, a class by allowlist, records each ask, and prints a head-pinned merge line only for a class with a valid README grant, a clean codex reader, head-bound roborev evidence and no failed record; `calibrate` gives the exact one-sided bound. Deviations from the design, each for FO to rule: roborev is read as a worker-written evidence line (the reader needs a worktree); `point: second-reviewer` and `point: more` are added; the amendment point uses the validation record's commit date with `>=` while `calibrate` uses `>`; the design's 93, 124 and 153 are total records (clean plus failures), not clean counts; 59 clean records print `lower=0.9505` while the exact bound is 0.950488. Also: `git push -u` wrote the branch's upstream into the shared git config (branch keys only, no remote URL); I did not undo it.

## Stage Report: implementation (cycle 2)

- DONE: Update FIXES["readme-keeps-delivery-rules"] need and swaps in kc-dev-flow-2/scripts/test_sd_dispatch.py to the rewritten head paragraph of kc-dev-flow-2/references/sd/workflow.md, keeping a need string for each delivery rule the old pins held (the head hold before the merge ask, and that exit 1 or 2 of the check holds the ask); show that removing each new need string's sentence from the README fails the pin
  The paragraph now reads "Before the merge ask, FO runs `...delivery_gate.py check ...`; exit 1 or 2 holds the ask, as does a head other than the latest `Candidate:`; FO shows the Captain what it printed." (+6 words: workflow.md 5430, lint-skills budget step -17, merge-ask moment 402 against 415, limit 404). Need strings: "...check ...; exit 1 or 2 holds the ask" and "as does a head other than the latest `Candidate:`". Calling fix_gaps on the pinned texts: all clean; removing either sentence reports that need missing (pin fails); the 0.10.1 swap reports only this fix's gaps.
- DONE: All CI steps green on the new head, including the steps after kc-dev-flow-2/scripts/test_sd_dispatch.py; push without force and without -u; roborev evidence= line; commit the stage report
  CI run 39087887816 at head fdeee5e50: every step success, none skipped; the other three checks pass. Pushed with an explicit remote and branch, no force, no -u. roborev: `findings on fdeee5e50; evidence=roborev:826`, one High on delivery_gate.py: the printed merge line stays runnable after a later failure record or grant removal. Not fixed: the design states the line is valid only in the FO step of the passing check, and enforcing it before `gh pr merge` needs a merge subcommand the design does not list; reported to FO as a finding. AC-5's throwaway repository run stays not run (the Captain's yes).

### Summary

The test_sd_dispatch.py pins follow the rewritten paragraph and keep one pin per delivery rule, each shown failing without its sentence; CI is green on fdeee5e5. One roborev High about the merge line's validity window is left for FO.

## Stage Report: implementation (cycle 3)

- DONE: Close the window roborev 826 reports without a new subcommand: the merge line kc-dev-flow-2/scripts/delivery_gate.py prints re-runs the same check with the same arguments and runs gh pr merge --match-head-commit only when that re-run exits 0 and still prints the merge line, so a failure record or grant removal after the first check refuses the merge
  The printed line is now `python3 <script> check <task> --pr <ref> --text-file <file> [--head ..] [--workflow-dir ..] | tail -n 1 | grep -q '^next: run ' && gh pr merge ... --match-head-commit <candidate> ...`: only a re-run whose last line is again a merge line reaches gh pr merge (hold and ask lines never start `next: run `). Commit 5d0a3448; README words unchanged (workflow.md 5430, merge-ask moment 402 against 404).
- DONE: A failing-first test that adds a failure record (and one that removes the grant) after a passing check and shows the printed line refuses; a mutation that drops the re-run fails it (python3 -B, caches cleared); run the roborev gate again until clean or twice; CI green on the new head; push with an explicit remote and branch, no -u; commit the stage report
  RecheckTests execute the printed line with `sh -c` against the stub gh after each change: merges once when nothing changed; refuses after a later failure record, after the grant is removed, after the head moved (all three failed first, before the code change). Real mutations (24 then 26 of the harness, all RED, 0 survived), including "drop the re-run from the printed line" (13 tests fail) and "re-run without the last-line test" (5 fail). roborev ran twice in this dispatch: `findings on 5d0a34485; evidence=roborev:829` (High: calibrate deduped per task folder; fixed in d13414fa with a failing-first test and mutation: a PR and head in two task folders counts once) then `findings on d13414fa6; evidence=roborev:832` (High: a workflow README at the repository root was not never-eligible, pattern was `./README.md`; fixed in 31cdd2bc, failing-first test and mutation). The cap of two runs is reached, so the head after the two fixes has no roborev run: dff20172 is unreviewed by roborev. ADR 0023 names the re-run (dff20172). CI green at dff20172: run 39090074833 (unit tests 1m44s) and the other three checks. Pushed to origin spacedock-ensign/merge-gatekeeper, no force, no -u.
- FAILED: After the roborev fix in implementation-4, run AC-5 on a throwaway private GitHub repository under the iamcxa account: create it, show that the printed merge line refuses when the PR head differs from the checked head and merges when it matches, save the commands and output in the task folder, then delete the repository and show it is gone
  Not started: the gh token for iamcxa has scopes gist, project, read:org, repo, user, workflow, with no `delete_repo`, so I could create the repository but not delete it, and the grant covers delete. I did not create it and did not run `gh auth refresh` (interactive, changes auth). Needs one of: the Captain runs `gh auth refresh -h github.com -s delete_repo`, or FO rules that I may create it and the Captain deletes it by hand.

### Summary

The printed merge line now re-runs the check before it merges, proven by executing it against a stub gh after a later failure record, a removed grant and a moved head. Two further roborev Highs were fixed (calibrate dedupe across task folders, a root workflow README), with the head after them unreviewed because the run cap was reached. CI is green at dff20172; AC-5's real repository run waits on the `delete_repo` scope.

## Stage Report: implementation (cycle 4)

- DONE: Run AC-5 on the private repository iamcxa/kc-merge-gate-ac5-throwaway-20261018, created by you in a separate clone (gh repo create --private): set up a docs-only grant, a CI check that passes and a PR; show the printed merge line refusing after a pushed head change, show GitHub's own --match-head-commit refusal, show a re-run on the new head merging; save the commands and output under the task folder
  Repository created private under iamcxa, clone at /tmp/mg-ac5 (outside this repository); docs-only grant `merge-grants: [docs-only:rule:0.95:squash:ADR 0023]`, a workflow `ci.yml` whose one job passes. Transcripts: `merge-gatekeeper/validation/ac5-run-1.txt` (the earlier line form, PR 1) and `ac5-run-2.txt` with `ac5-run-N.sh` (the final prose-first form, PR 2, commands run unmodified). Run 2: check at head c6cb98e7 prints the merge line; after pushing 0ea61129 the printed command exits 1, the PR stays OPEN at the new head (its re-run holds: "PR head is now 0ea61129..., not c6cb98e7" and CI not finished); bare `gh pr merge --match-head-commit c6cb98e7...` is refused by GitHub: "GraphQL: Head branch was modified. Review and try the merge again. (mergePullRequest)", PR still OPEN; after the Candidate line is updated and CI is green, the check without --head prints a merge line and running its command unmodified merges (state MERGED, merge commit e727d992). Run 1 found that the old line ended in prose after the command (roborev:835 said `now` would be passed to gh as a second argument): fixed, the prose now comes first and everything after "ask him: " is one command, tested by `sh -n`, shlex and a mutation.
- DONE: Do not delete the repository; report its exact name in the stage report and your completion message so FO can hand it to the Captain, who deletes it
  Repository left in place, private, exact name `iamcxa/kc-merge-gate-ac5-throwaway-20261018` (two merged throwaway PRs); no gh auth change.
- FAILED: Then run the roborev gate once on the current head and commit the stage report
  roborev ran twice: `findings on dff201720; evidence=roborev:835` (High: `now` after the PR number; fixed in f3f0fa3e) then `findings on f3f0fa3e7; evidence=roborev:837` (High: a grant with any threshold, `0.0001`, is honored and no calibration is checked at merge time). Fixed in part in 1beabd97: a grant entry now needs a threshold from 0.95 to 1 (failing-first test, real mutation red). Declined, for FO to rule: verifying the class's calibrated bound at each `check`; the grant is the Captain's ADR on `calibrate` evidence (README is never-eligible, so only he merges a grant), `check` already refuses on any failure record of the class, and a check-time bound needs 59 labelled fixture records per positive test. Head 1beabd97 has no roborev run of its own. Tests: 61 pass; real mutations of the harness all RED (the AC-5 four, root README, dedupe, threshold, earlier 24). CI green at 1beabd97: run 39099866464, plus the other three checks. origin/main moved to 18e161d9; `git merge-tree` shows no textual conflict and GitHub says MERGEABLE CLEAN, but I did not rebase: after any rebase `lint-skills.py` must be re-run because other tasks edit workflow.md and its budget steps.

### Summary

AC-5 ran on a real private repository: the printed line refuses after a head change, GitHub refuses a stale `--match-head-commit`, and the re-run on the new head merges. The run exposed and fixed a prose-after-command defect in the printed line; two more roborev Highs were met (threshold format fixed, calibration at check time declined). The throwaway repository `iamcxa/kc-merge-gate-ac5-throwaway-20261018` is left for the Captain to delete.

## Stage Report: implementation (cycle 5)

- DONE: Run kc-dev-flow-2/extensions/roborev/roborev_gate.py once on head 1beabd97 and record its evidence= line; if it reports no High, commit the stage report and stop; if it again reports the check-time calibration point (or any High), do not change code: report the finding text and your reasons, and FO takes it to the Captain as a waive-or-fix decision
  `clean on 1beabd975; evidence=roborev:838` (exit 0, base 2dad59ca): no High and no finding, the check-time calibration point was not raised again. No code changed in this cycle. Head 1beabd97 is the PR head; CI green there (run 39099866464).

### Summary

Roborev is clean on the PR head 1beabd97, so the declined check-time calibration point of roborev:837 did not recur and no waiver is needed.

## Stage Report: validation

- DONE: Independent verdict on PR #666 head 1beabd97 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states first validation of a Production task. Run the prod validation security review as origin/main now defines it (#659 merged after the installed 0.24.0): dispatch kc-pr-flow:tob-security-reviewer once with model sonnet and the Reach brief from origin/main's kc-dev-flow-2/skills/validation/profiles/prod.md, save the report under the task folder as security/validation-1.yaml, and write the Security review (validation) and Security finding lines that profile requires; judge each finding. Also: AC-5 transcripts are under merge-gatekeeper/validation/ (ac5-run-2 is the final line form; the throwaway repository is left for the Captain to delete; do not touch it); AC-9 does not apply (no model arm, D1 b); the PR base is 2dad59ca and main is now 18e161d9, so also run kc-dev-flow-2/scripts/lint-skills.py and the package tests on a merge of the head into current origin/main; judge the implementer's listed deviations from the design; the ADR is ADR: 0023 and ADR 0011 gains one Status line
  Verdict PASSED at head 1beabd975bac782a14e8c9e98fa42bd80b333eaf: every AC met by my own runs; no finding meets the four Material fields; open items below. Suites (python3 -B, caches cleared, 600 s cap each) on the head and on a clean merge of it into origin/main 18e161d9: lint-skills.py 5430 of 5430 words, every CI-listed test file rc 0 (61 tests in test_delivery_gate.py; test_role_triggers.py exists only on main and passes there). test_sd_dispatch.py: `--sd-plugin-root /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0`, binary /Users/kent/.local/bin/spacedock 0.27.2 (CI pins plugin root 0.27.2). comment_ratio.py 0 of 929 code lines, exit 0; number_guards.py check PASS (base 18e161d9); design_surfaces.py check exit 0; dispatch_records.py 9 records complete.
  Falsifiers I ran (29 mutations of delivery_gate.py in a scratch copy, each against all 61 tests): AC-1 six hold clauses, AC-2 four matchers, AC-3 five rows (docs/adr, rename previous_filename, learning.md, agents/, own-test rule), AC-4 four conditions (verdict, reviewers_clean, failure record, Conventional title), AC-5 title quoting and recheck pipe test, AC-6 write on hold, AC-7 pending-as-clean, bound formula, revert detection, failure-in-granted-class, AC-12 clean() and tok(): 28 RED. 1 survived: dropping `full in candidates` (AC-5), an equivalent mutant because the earlier head holds already force `full` to equal a candidate; the printed `--match-head-commit` is the PR head, equal to the candidate whenever a line prints. Own probes: hostile titles (`'; touch PWN`, `$(..)`, backticks, `|`) run through the printed line with a stub gh create nothing; exact lower bounds 59/59 0.950492, 58/58 0.949661, 92/93 0.950006, 122/124 0.950100, 150/153 0.950105 match an independent Clopper-Pearson bisection.
  AC-5: read ac5-run-2.txt (head f3f0fa3e; the only later change, 1beabd97, tightens the GRANT threshold regex): printed line exits 1 after a pushed head change with the PR still OPEN, GitHub refuses a stale `--match-head-commit` ("Head branch was modified"), the re-run on the new head merged (e727d992); read-only `gh` shows PR 2 MERGED, repository private, untouched by me. I did not re-run it against GitHub. The AC text says the line is "exactly" `next: run gh pr merge ...`; the printed form is the prose-first re-run form FO ordered in implementation-3/4 (test MERGE_LINE pins it): AC wording is stale, intent kept.
  AC-8: replay-1.txt read; my read-only `gh` pass over the 35 archived tasks with a PR now: 35 of 35 class never, so the grant path would fire on none of this repository's history. #632 and #628 head holds fire on the prose heads. The 2026-09 rows (#375 #376 #378 #379 #420 #423) are absent from replay-1.txt instead of reported `not caught`.
  AC-10 (own script, `len(text.split())`): base passages 215+57+90+33 plus check output 20 = 415; head 212+39+90+37 plus 24 = 402, limit 404; workflow.md 5447 to 5430 against lowered budget 5430; `_mods`, pr_watch.py and learn untouched. AC-11: `adr_lint.py docs/adr --since 2dad59ca --require 0023` exit 0; `grep -c merge-grants` over the README and workflow.md diff 0; ADR 0011 gains the one line `Merge partly superseded by ADR 0023.` AC-9: not applicable (no merge-judge or Decisions API in the tree, `git grep`).
  Implementer's deviations, judged: roborev as a worker-written evidence line (Deferred risk, F6); `point: second-reviewer` and `point: more` (accepted, design findings 6 and the 12-point cap); amendment point `>=` against calibrate `>` (accepted limit, disclosed in ADR 0023, F7); design's 93/124/153 are totals not clean counts (accepted, my bounds agree); lower=0.9505 printed for exact 0.950492 (accepted). Events outside the brief: none by me; the security reviewer reports it wrote nothing and ran no script.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Script and observed output are under `### Minimal acceptance script`; adr_lint.py `docs/adr --since 2dad59ca` (and with `--require 0023`) printed "22 ADR file(s) checked, 0 legacy", exit 0. Findings are under `### Findings`; verdict PASSED at 1beabd975bac782a14e8c9e98fa42bd80b333eaf.

### Security review (validation)

Security review (validation): security/validation-1.yaml at 1beabd975bac782a14e8c9e98fa42bd80b333eaf
Security finding (validation 1) 1: Needs decision: widen never-eligibility now (add .githooks, .roborev.toml, repo-root scripts/, plugin hooks/ and bin/, narrow docs-only to .md) or leave it to the first grant's ADR; no merge line can print before a grant, and no merge-grants entry exists in the tree
Security finding (validation 1) 2: declined: LOW, dormant until a merge-grants entry exists; the unreadable-fact paths only fail to add a failure, and the ADR's "at once" holds when reads succeed; revisit in the first grant's ADR (see F3)
Security finding (validation 1) 3: declined: LOW, a codex_review.py timeout raises and the printed line's last line is then no `next: merge `, so it fails closed; the trigger-comment race is in code outside the diff
Security finding (validation 1) 4: declined: LOW, GitHub's own squash default already uses the PR title as subject; quoting is correct (my hostile-title probe), and it needs a grant plus an outsider PR

### Findings

Dispositions by the Review-finding disposition; none is Material because field 4 (trigger evidence) fails for each: no `merge-grants:` entry exists in any README, so no merge line can print yet. What would make each Material is the first grant entry.
- F1 Deferred risk (Codex P1 on `profile_prod`, reproduced): `profile: "prod"` or `'prod'` is read as prod by design_surfaces.FM_PROFILE but not by delivery_gate's `profile_prod` regex; with a docs-only grant and a zero-finding review my probe printed `class: docs-only` and a merge line for it. 0 of 70 state tasks quote the value.
- F2 Deferred risk (Codex P1 on depth, reproduced): `packages/foo/agents/x.md` and `a/b/c/references/r.md` class `other`; no tracked path of this repository sits deeper than the pattern (`git ls-files` check).
- F3 Deferred risk (Codex P1 on trunk freshness, reproduced in a scratch bare origin): `revert_time` reads `origin/<trunk>` without a fetch, so a revert pushed after the last fetch is missed until fetched.
- F4 Needs decision: security finding 1 (above); it also covers `docs/journey`, `docs/ship-flow`, `docs/plan-flow` under docs-only, which I could not show agents do or do not load.
- F5 Deferred risk: security findings 2 to 4 (declined LOW).
- F6 Deferred risk: roborev is a task-file line written by the worker, not a run of roborev_gate.py (design finding 6 named the reader).
- F7 Deferred risk: a same-day amendment after an ask is not seen by `calibrate`.
- F8 Polish: AC-5 "exactly" text, AC-10's 5484 constant and AC-7's 0.9505 are stale against the shipped form; FO may note them.
- F9 Polish: doc_impact.py lists 9 documents; the report records 8; `kc-dev-flow-2/references/sd/adoption.md` (names test_sd_dispatch.py only to say how to run it) has no `unaffected` line.
- F10 Polish: replay-1.txt lacks the not-replayable bite rows (#375 #376 #378 #379 #420 #423: FO behaviours no hold sees; only the prose and AC-5 address them); the save of the replay script itself is absent, only its output.
- F11 Polish: mutation `full in candidates` survives (equivalent, redundant guard).
- F12 Polish: `points_for` lists deferred, decline and not-run lines before the `profile` and `path` points, so with 12 or more of them the cap drops those two (my stub run of this very task shows `point: more: 9 not shown` and no `profile` point); the `class: never` line still prints.
- Open on the PR head for FO: three Codex P1 comments (4305855772, 4305855775, 4305855777 on 1beabd97) are F1 to F3; no FO decline is recorded for them.
- Minimal necessity (same candidate): holds, points and the per-ask record are used at every merge ask now and each maps to AC-1, 2, 6 and a counted accident class. Class, grant line and `calibrate` have no consumer until a grant exists, and 35 of 35 of this repository's archived PRs class `never`; the Captain's own words in ADR 0023 ask for the delegation, so retain, but the delegation cannot fire on dev2 history. Relay, subspace-web and qnow were not measured.
- Inconsistency for FO: the dispatch scope notes say `Profile: pilot`; the task frontmatter and checklist say prod. I ran the prod procedure.

### Minimal acceptance script

Needs: this repository checkout at the path below, python3, git, `gh` signed in (read-only calls). Run in a fresh bash. Not covered: a real GitHub merge (only the saved AC-5 transcript), any grant (none exists), relay, subspace-web or qnow, and Spacedock's pr-merge and merge guard after an FO-run merge.

```bash
set -u
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0
WF=$REPO/.context/dev2-adoption/worktree/docs/dev2
ST=$WF/.spacedock-state
H=1beabd975bac782a14e8c9e98fa42bd80b333eaf
W=/tmp/merge-gatekeeper-accept
export PYTHONDONTWRITEBYTECODE=1
echo "== 1. check out the PR head"
rm -rf $W /tmp/merge-gatekeeper-accept-task
git -C $REPO worktree add --detach $W $H >/dev/null 2>&1; git -C $W rev-parse HEAD
echo "== 2. word budget and decision record"
python3 -B $W/kc-dev-flow-2/scripts/lint-skills.py | grep -E "words"
(cd $W && python3 -B $PKG/scripts/adr_lint.py docs/adr --since 2dad59ca --require 0023; echo "adr_lint exit=$?")
echo "== 3. the merge check's own tests (about 1-2 minutes)"
python3 -B $W/kc-dev-flow-2/scripts/test_delivery_gate.py 2>&1 | tail -n 3
echo "== 4. the printed merge line refuses after a later change (stub gh, no network)"
python3 -B $W/kc-dev-flow-2/scripts/test_delivery_gate.py -v RecheckTests 2>&1 | grep -E "ok$|^Ran|^OK|FAIL"
echo "== 5. run the check on PR 666 itself, on a scratch copy of the task folder"
mkdir /tmp/merge-gatekeeper-accept-task && cp $ST/merge-gatekeeper.md /tmp/merge-gatekeeper-accept-task/ && cp -R $ST/merge-gatekeeper /tmp/merge-gatekeeper-accept-task/ && echo "Merge ask." > /tmp/merge-gatekeeper-accept-task/gate.txt
python3 -B $W/kc-dev-flow-2/scripts/delivery_gate.py check /tmp/merge-gatekeeper-accept-task/merge-gatekeeper.md --pr iamcxa/kc-claude-plugins#666 --text-file /tmp/merge-gatekeeper-accept-task/gate.txt --workflow-dir $WF | cut -c1-200; echo "check exit=${PIPESTATUS[0]}"
echo "== 6. clean up"
git -C $REPO worktree remove --force $W && rm -rf /tmp/merge-gatekeeper-accept-task && echo removed
```

Expected: step 1 prints the 40-hex head above. Step 2 prints `references/sd/workflow.md: 5430 of 5430 words; ...` and `22 ADR file(s) checked, 0 legacy` then `adr_lint exit=0`. Step 3 ends `Ran 61 tests in <n>s` and `OK`. Step 4 lists 6 tests ending `ok`, then `Ran 6 tests` and `OK`. Step 5: while PR 666 is a Draft, exit 1 and a line `the PR is a draft`; once it is Ready with CI green, exit 0 with a `validation security review security/validation-1.yaml: 4 findings, 3 declined, 1 decisions` line, up to 12 `point:` lines (this report's own words "declined" and "Deferred risk" make them), `class: never`, a `record:` line, and last line `next: ask for merge with this text.` Step 6 prints `removed`.

Observed, run exactly as written above in a fresh `env -i ... bash --noprofile --norc` shell, exit 0 (PR 666 was still Draft, so step 5 holds):

```
== 1. check out the PR head
1beabd975bac782a14e8c9e98fa42bd80b333eaf
== 2. word budget and decision record
references/sd/workflow.md: 5430 of 5430 words; no unlisted passage repeats it
22 ADR file(s) checked, 0 legacy
adr_lint exit=0
== 3. the merge check's own tests (about 1-2 minutes)
Ran 61 tests in 79.442s

OK
== 4. the printed merge line refuses after a later change (stub gh, no network)
test_a_failure_record_added_after_the_check_refuses_the_merge (__main__.RecheckTests.test_a_failure_record_added_after_the_check_refuses_the_merge) ... ok
test_a_grant_removed_after_the_check_refuses_the_merge (__main__.RecheckTests.test_a_grant_removed_after_the_check_refuses_the_merge) ... ok
test_a_head_that_moved_after_the_check_refuses_the_merge (__main__.RecheckTests.test_a_head_that_moved_after_the_check_refuses_the_merge) ... ok
test_dropping_the_recheck_from_the_line_lets_a_removed_grant_merge (__main__.RecheckTests.test_dropping_the_recheck_from_the_line_lets_a_removed_grant_merge) ... ok
test_everything_after_the_prose_is_one_command_ending_at_the_empty_body (__main__.RecheckTests.test_everything_after_the_prose_is_one_command_ending_at_the_empty_body) ... ok
test_the_printed_line_merges_when_the_recheck_still_passes (__main__.RecheckTests.test_the_printed_line_merges_when_the_recheck_still_passes) ... ok
Ran 6 tests in 1.796s
OK
== 5. run the check on PR 666 itself, on a scratch copy of the task folder
the PR is a draft
next: hold the ask; mark the PR ready under the Captain's authority and let its CI finish.
check exit=1
== 6. clean up
removed
```

Step 5 on the Ready path could not run live (PR is Draft; I do not mark it ready). I ran the same `check` on a scratch copy of this task with the real PR facts, `isDraft` set false, behind a stub `gh`: exit 0, `class: never`, `next: ask for merge with this text.`, 12 `point:` lines and `point: more: 9 not shown`.

### Summary

PASSED at 1beabd97: every criterion holds under my own runs, 28 of 29 mutations fail the suite (the survivor is equivalent), and the head also passes lint and every test on a clean merge into origin/main 18e161d9. Three Codex P1 comments and a MEDIUM security finding, all reproduced or read, describe paths that stay dormant until the first `merge-grants:` entry; I classed them Deferred risk or Needs decision, not Material, and FO and the Captain choose between repairing them now (F1 is a one-regex fix) and recording a waiver. Nothing in this repository would be grant-eligible today (35 of 35 archived PRs class `never`).

## Stage Report: implementation (cycle 6)

- DONE: Phase 1 only: reproduce the three Codex P1 on #666 head 1beabd97 (review:5561577977) as a failing test, and propose the smallest fix; report and stop, with no commit or push, until FO authorizes the fix
  Worktree untouched (HEAD 1beabd97, `git status` clean, no commit, no push, no `git config` write). Work is in a scratch copy `/tmp/mg-p1/kc-dev-flow-2/scripts` (delivery_gate.py, test_delivery_gate.py). Class `CodexP1Tests` (5 tests) fails 8 subcases on the unmodified script: (1) a `profile: "prod"` / `'prod'` task with a docs-only grant and an empty security review prints `class: docs-only` and the merge line; (2) `packages/foo/agents/x.md`, `a/b/c/references/r.md`, `x/y/skills/z/SKILL.md`, `p/q/extensions/e.py` class `other`; (3) with a real scratch bare origin, a revert pushed after the last fetch gives `calibrate` failures=0 (expected 1) and `check` still prints the merge line. The proposed fix turns all 5 green and the whole suite passes (66 tests, 91 s, python3 -B). Patch: `/tmp/mg-p1/codex-p1-proposal.patch` (194 lines, `git apply --check -p1` clean on 1beabd97).
  Fix (1): `from design_surfaces import FM_PROFILE` and read the profile as `validation_security.check_task` does (same frontmatter match, same reader), `profile_prod = value == "prod"`; no third regex. Fix (2): the instruction-directory pattern becomes `(?:^|/)(?:skills|agents|extensions|references)/`, the form the `_mods|migrations` rule already uses; `git ls-files` shows no tracked path of this repository that this newly catches, and `docs/my-agents/x.md` stays docs-only (test row).
  Fix (3), the question asked: a fetch inside `check` is acceptable and holding on trunk-ref age is not. Measured here: `git fetch origin main` against github.com/iamcxa/kc-claude-plugins in a scratch clone 0.52, 0.50, 0.52 s; `git ls-remote` 0.56, 0.57 s (one repository, one machine; relay, subspace-web, qnow not measured). `check` already makes `gh pr view`, `gh api --paginate` and a codex reader call with a 120 s cap, so the network is already needed. Age of the trunk ref against the PR's last push bounds nothing: a revert of an earlier merge can land any time after that fetch, and a quiet trunk looks old. So `fetch_trunk` runs `git fetch --quiet origin <trunk>` (60 s cap) once per `check` only when it is about to print a merge line, and once at the start of `calibrate`; no `origin` remote means nothing to fetch (existing tests); a failed or timed-out fetch makes `calibrate` exit 2 with `cannot fetch origin/<trunk>: ...` and `check` print `cannot fetch origin/<trunk>, so no merge line: ...` and the ask line (fails closed). The printed line re-runs `check`, so the recheck fetches again; the window left is the seconds between that fetch and `gh pr merge`. Cost to know: the fetch updates `origin/<trunk>` in the FO checkout's shared .git (one ref, no config write); `check` otherwise writes only the ask record. Docstring updated to say so.
- DONE: Falsifiers for the proposed fix, run by me
  Six real mutations of the fixed script, each against `CodexP1Tests`, all red: old profile regex (quoted-prod test, 2 subcases), old directory pattern (4 subcases), `fetch_trunk` never fetching (3 tests), failure ignored by calibrate (2), failure ignored by check (2), check not fetching (2). One existing test pinned text the fix rewrites: GrantTests `a failed record in the class` mutation anchor `and not any(state == "failure"` became `elif not any(state == "failure"`; no other existing test changed. Not run: comment_ratio.py, lint-skills.py, CI (nothing committed).

### Summary

All three Codex P1 reproduce as failing tests on 1beabd97 and the patch at `/tmp/mg-p1/codex-p1-proposal.patch` fixes them with 5 new tests and one anchor change; the worktree is unchanged and nothing is committed or pushed. For (3) I recommend the in-check fetch, fail-closed on error, over holding on ref age; FO rules, then a fresh worker applies the patch, re-runs the suite, comment_ratio and roborev, and pushes. This report is written in the state checkout but not committed, per the no-commit instruction.

## Stage Report: implementation (cycle 7)

- DONE: Apply /tmp/mg-p1/codex-p1-proposal.patch to kc-dev-flow-2/scripts/delivery_gate.py and its tests: a quoted prod profile is read as prod through the shared frontmatter reader; instruction directories match at any depth; the trunk ref is fetched inside check before the revert search, and a failed fetch holds the ask (fail closed)
  Applied unchanged to 1beabd97 as commit b28bbcc6 (two files, `git apply -p1`). `design_surfaces.FM_PROFILE` is the reader (same frontmatter match as `validation_security.check_task`); pattern `(?:^|/)(?:skills|agents|extensions|references)/`; `fetch_trunk` (60 s cap, no origin means no fetch) runs in `check` only before a merge line and at the start of `calibrate`. A failed fetch: `check` prints `cannot fetch origin/<trunk>, so no merge line: ...` and the ask line (exit 0, no merge line); `calibrate` exits 2. The hold is the ask line, not exit 1, because the PR itself passed every hold and the Captain still gets the ask.
- DONE: Each fix's failing-first test passes and its mutation fails it (python3 -B, caches cleared); kc-dev-flow-2/scripts/lint-skills.py exits 0; all package test files pass
  `CodexP1Tests` (5 tests) failed 8 subcases on 1beabd97 before the patch (cycle 6) and pass now. Mutations of the committed script, each red: old profile regex (2 subcases), old directory pattern (4), `fetch_trunk` never fetching (3 tests), failed fetch ignored by calibrate (2), by check (2). lint-skills.py exit 0 (workflow.md 5430 of 5430). Every test file of the CI list (24 files, test_sd_dispatch.py with plugin root 0.27.0, test_observer_recovery.py with SPACEDOCK_BIN) rc 0; test_delivery_gate.py 66 tests. comment_ratio.py base 2dad59ca: code lines 1013, comment lines 0, exit 0.
- DONE: Push with an explicit remote and branch, no -u; CI green on the new head
  `git push origin spacedock-ensign/merge-gatekeeper`, 1beabd97..b28bbcc6, no force, no -u. CI at b28bbcc6: runs 39103155095 (kc-dev-flow-2 tests, every step success), 39103155094 (parity), 39103155097 (release gate), GitGuardian all success. PR still Draft, not marked ready, no comment.
- FAILED: roborev evidence= line
  `findings on b28bbcc64; evidence=roborev:843` and again `findings on b28bbcc64; evidence=roborev:844`: the same one High both runs, on lines this repair did not touch: a syntactically valid `merge-grants` entry (e.g. `docs-only:rule:0.95:squash:ADR 9999`) enables a merge line though its ADR and calibration are never verified. No code changed after the findings, per the run cap. Reasons for FO and the Captain: this is the check-time calibration point already declined in cycle 4 (roborev:837); the README is never-eligible (`point: path`, class never), so only the Captain can merge a change that adds a grant, and `check` refuses on any failure record of the class; roborev:838 on 1beabd97 was clean, so the point recurs run to run. Decision for FO: waive again or have the Captain rule a check-time ADR/calibration verification.

### Summary

The three Codex P1 are fixed in b28bbcc6 with failing-first tests and mutations, the whole package suite and CI pass, and the branch is pushed. roborev raises the old grant-validation High twice (844 final), which is left for FO as a waive-or-fix decision; the Captain's F4 (never-eligible path list) was not touched.

## Stage Report: implementation (cycle 8)

- DONE: Phase 1 only, no commit or push: reproduce at #666 head b28bbcc6, as failing tests, (a) a merge-grants entry naming a nonexistent ADR, or an ADR that does not name the grant, still prints a merge line
  `test_delivery_gate.GrantAdrTests.test_a_grant_whose_adr_is_absent_or_does_not_name_it_prints_the_ask_line`: 13 fixtures all RED at b28bbcc6 (each prints the merge line, wanted `next: ask for merge with this text.`): no adr folder, no file for the number, 002-/00245- files only, ADR with no grant, class only, other method, other threshold, other class, other number, longer entry (`ADR 00245`), longer class (`not-docs-only`), `adr-path:` pointing elsewhere, no repository root. Positive control `test_an_adr_that_names_the_grant_still_prints_the_merge_line` (4 fixtures) is green today and must stay green.
- DONE: (b) each path the Captain's ruling adds to the never class (.githooks, .roborev.toml, repo-root scripts/, plugin hooks/ and bin/, a non-.md file under docs) classes as eligible today
  `NeverAddedTests`: 12 added paths RED (class `other`, wanted `never`) alone, beside `docs/a.md`, and on either rename name; 6 non-.md docs paths RED (class `docs-only`, wanted `other`); keep-class test green. Whole file at b28bbcc6 plus these tests: 71 tests, 31 failures, all 31 in the new classes; the 66 existing cases pass. Edits are uncommitted in the worktree (only `test_delivery_gate.py`).
- DONE: propose the smallest change and its mutations; report and stop until FO authorizes the fix
  See Summary. No product byte changed; nothing committed, pushed or commented.

### Summary

Proposed fix, `delivery_gate.py` only. (1) `adr_names_grant(root, scalars, grant)`: the ADR folder is `<repo root>/<adr-path, default docs/adr>`; the grant passes only when a file named `<NNNN>-*.md` (NNNN from the entry's `ADR NNNN`, so `002-` and `00245-` never match) exists and its text holds the whole merge-grants entry verbatim, i.e. class, threshold, method and ADR number together, delimited so it is not a substring of a longer token (`(?<![\w.:-])<escaped entry>(?!\w)`). So "names the grant" means the line text, not the class word, and a wrong ADR (another class, method, threshold or number, or one that only discusses the class) cannot pass; no repo root or an unreadable file means no merge line. It is one more `and` in the existing merge-line condition, before the fetch. (2) `NEVER_PATH` gains `^\.githooks/`, `^\.roborev\.toml$`, `^scripts/`, `(?:^|/)(?:hooks|bin)/`; `classify` docs-only requires `p.startswith("docs/") and p.endswith(".md")`. Existing tests to adjust with the fix: `ROWS` rows using `scripts/foo.py` move to `tools/foo.py`; the existing grant tests (`GRANTS` uses ADR 0024) get the `with_adr` setup (the helper is already in the file). Mutations I would run, each must turn a named case RED: drop the ADR check; match the class word only; match without the number delimiter; glob `NNN*` instead of `NNNN-*`; ignore `adr-path`; drop the `.githooks`, `.roborev.toml`, `scripts/`, `hooks|bin` pattern one at a time; drop `.endswith(".md")`.
For FO to rule: (a) the Captain's ruling says docs-only admits only .md, so a non-.md docs file becomes `other`, not `never` (the dispatch said "never class"); I tested `other`. (b) `^scripts/` is repo-root only per the ruling, so `kc-pr-flow/scripts/x.py` with its test stays script-with-test. (c) The ADR's Status is not read (a Proposed or Rejected ADR quoting the entry would pass); one added regex on `## Status` would close it, not in the ruling. (d) The ADR name check does not read whether the ADR evidence is thin, per the ruling. Stage report is written to the state checkout uncommitted, as the dispatch said no commit.

## Stage Report: implementation (cycle 9)

- DONE: Apply the phase-1 fix in kc-dev-flow-2/scripts/delivery_gate.py: a grant passes only if its NNNN-*.md ADR exists under the adr-path, its Status reads Accepted, and the whole merge-grants entry appears in it delimited; NEVER_PATH gains .githooks/, .roborev.toml, repo-root scripts/ and hooks/ or bin/ at any depth; docs-only admits only .md files under docs/, other docs files class other; keep the new tests and add one for the Status rule
  Commit 3fd84178 (local; not pushed). `adr_grants(root, scalars, grant)` is one more `and` in the merge-line condition: file `<adr-path or docs/adr>/<NNNN>-*.md`, a `## Status` section whose first word is Accepted, and the entry `class:rule:threshold:method:ADR NNNN` as one token (not inside a longer token). "Names the grant" is that whole-entry match, so another class, method, threshold or number, or an ADR that only mentions the class, fails; no repo root fails. Status fixtures: Proposed, Rejected, Superseded, no section, Accepted only in prose, `Acceptedly`. README words unchanged (workflow.md 5430 of 5430). Existing tests: `ROWS` scripts/ rows moved to tools/; `run_check` writes an Accepted ADR for each entry in the README body unless `adr=False`.
- DONE: Run the listed mutations plus one dropping the Status rule, each turning its named case red (python3 -B, caches cleared); kc-dev-flow-2/scripts/lint-skills.py exits 0; all package test files pass
  `GrantAdrTests.test_each_adr_rule_removed_turns_its_own_case_red` (11 mutations: drop the ADR check, class-word-only match, no number delimiter, no left delimiter, glob `NNN*`, ignore adr-path, drop Status (three fixtures), Status anywhere in prose, no word boundary after Accepted) and `NeverAddedTests.test_each_added_pattern_removed_turns_its_own_row_red` (.githooks, .roborev.toml, scripts/, hooks, bin, .md rule): each variant prints the merge line or the old class on its named fixture, so each guard is load-bearing. test_delivery_gate.py 73 tests OK (was 66 plus 31 red subtests); every CI test file exits 0 locally, test_sd_dispatch.py with --sd-plugin-root spacedock 0.27.0 PASS; lint-skills.py exit 0; comment_ratio.py b28bbcc6..HEAD "code lines 131, comment lines 0, 0.0%" exit 0; number_guards.py check PASS (head 3fd841789db9).
- DONE: roborev evidence= line
  roborev: clean on 3fd841789db9c76d863ae4f723184c790471a7da; evidence=roborev:850
- FAILED: push with an explicit remote and branch, no -u; CI green on the new head
  `git push origin spacedock-ensign/merge-gatekeeper` was refused by the permission layer (Out-of-Place Publication); I did not retry or work around it. #666 head stays b28bbcc6 and CI on the new head was not run. FO or the Captain pushes 3fd84178 (or grants the push), then reads CI.
- DONE: commit the stage report
  `spacedock state commit` run after this append; see the completion message.

### Summary

Both rulings are built in 3fd84178 with the Status rule added as FO ruled, every guard shown load-bearing by a mutation. Two limits: `(?:^|/)(?:hooks|bin)/` also makes `docs/hooks/x.md` never (fail-safe over-block, tested as such by omission); the ADR's evidence quality is not read (ruling d). The branch is not pushed, so no CI result exists for the new head.

## Stage Report: validation (cycle 2)

- DONE: Independent verdict on PR #666 head 3fd84178 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Verdict PASSED against AC-1 to AC-12 and both rulings at 3fd841789db9c76d863ae4f723184c790471a7da, with one blocker for FO: two Codex P1 comments (review:5562139252, ids 4306363860 and 4306363862) are open on this head, I reproduced both, and README step 5 says a reviewer P1 is fixed and revalidated or waived by the Captain. I class both Deferred risk (no `merge-grants:` entry exists, so field 4 of the four-field test fails), not Material; I cannot waive them. Details under `### Findings`.
  Suites (python3 -B, 600 s cap): lint-skills.py 5430 of 5430 words on the head and on a clean merge of it into origin/main ffd620b4 (no conflict); every CI-listed test file rc 0, 24 of 24 on the head and 25 of 25 on the merge (test_role_triggers.py exists only on main); test_delivery_gate.py 73 tests OK; test_sd_dispatch.py `--sd-plugin-root /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0`, binary /Users/kent/.local/bin/spacedock 0.27.2; CI at this head all four checks pass (unit tests run 39111745943).
  Falsifiers I ran: 76 mutations of delivery_gate.py in scratch copies, each against all 73 tests (python3 -B, no caches; the last 70 with `-f`, stop at first failure): 72 RED, 4 survived. AC-1 nine (ci clause, empty rollup, SKIPPED/NEUTRAL, draft, mergeable, base, file count, head differs, PR head moved); AC-2 nine matchers; AC-3 twelve (docs/adr, rename previous_filename, learning.md, CLAUDE.md, own-test rule, release PR, db surface, kc-dev-flow-2/scripts, release json, _mods, .github, README rule) and no pagination; AC-4 seven (verdict, title, reviewers_clean, failure record, threshold form, codex rc, roborev head); AC-5 five (match-head, title quote, re-run pipe, body, method); AC-6 two; AC-7 eight (pending as clean, bound formula, revert, failure in granted class, propose threshold, rework regex, merged other head, closed); AC-12 three. Cycle 1, six: quoted-prod regex, directory depth, never fetching, fetch failure ignored in check and in calibrate, stale ref. Cycle 2, ten: drop adr_grants, drop Status, class-word-only match, number glob, .githooks, .roborev.toml, repo scripts/, hooks, bin, docs .md-only. All of these RED.
  Survivors: (a) `(?:gate|budget)` name pattern removed: nothing fails (no row decides on it alone; it is the only rule that makes `kc-ship-flow/scripts/e2e-gate.py` never); (b) `never` admitted by GRANT: nothing fails, the `cls != "never"` verdict stops it (redundant guard); (c) the absent-key default grant: nothing fails alone, red when the Accepted-ADR rule is also removed (the two guards mask each other; the case is equivalent in practice); (d) `newest wins` in the calibrate dedupe replaced by last-folder-wins: nothing fails (the tests drop the dedupe, not its order). (a) and (d) are Polish; (b) and (c) are redundant guards.
  Own probes through the real CLI with a stub gh (scratch repository, no network): ADR absent, Proposed, other threshold, or only naming the class prints the ask line; an Accepted ADR holding the whole entry prints the merge line, and running that line once calls `gh pr merge 9 --repo o/r --squash --match-head-commit <candidate> --subject 'feat(x): y' --body ''`; `.githooks/`, `.roborev.toml`, root `scripts/`, `kc-x/hooks/`, `kc-x/bin/`, and a rename from a hooks path all class never; `docs/a.png` class other; `tools/a.py` with its test stays script-with-test; `packages/foo/agents/x.md` never; `profile: "prod"` holds on the security review.
- DONE: recheck after Cycles 1 and 2: the three Codex P1 (review:5561577977) fixed (quoted prod read by the shared reader, instruction directories at any depth, trunk fetched inside check with fail-closed); the Captain's Cycle 2 ruling applied (a grant needs its Accepted ADR to contain the whole merge-grants entry; never list gains .githooks, .roborev.toml, repo-root scripts/, hooks/ and bin/ at any depth; docs-only only .md); confirm each new rule's test fails under its mutation; re-run the prod validation security review with the Reach brief from origin/main's kc-dev-flow-2/skills/validation/profiles/prod.md as security/validation-2.yaml and write its lines; AC-1 to AC-12 hold; run lint and package tests on a merge into current origin/main
  The three P1 of review 5561577977 hold fixed (probes and mutations above; CodexP1Tests uses a real scratch bare origin). The Captain's Cycle 2 ruling is applied as written: his list, no more (plugin `scripts/` is outside it, see G1). The security review ran once on origin/main's Reach brief at this head (model sonnet) and is saved unedited as security/validation-2.yaml. AC-1 to 4, 6, 7, 12 hold by the suite and my mutations. AC-5: ac5-run-2.txt (head f3f0fa3e) read, not re-run live; `merge_line` is unchanged since f3f0fa3e (`git diff f3f0fa3e HEAD`), and my stub run executed the printed line once. AC-8: replay-1.txt read (32 tasks, class never on all, rule arm says merge on 0); I did not re-run it. AC-9 not applicable (no model arm). AC-10: base passages 215+57+90+33 plus check output 20 = 415; head 212+39+90+37 plus 24 = 402 against limit 404, workflow.md 5447 to 5430 against the lowered budget, workflow.md unchanged since 1beabd97 (`git diff --stat 1beabd97 HEAD` lists two files). AC-11: `adr_lint.py docs/adr --since 2dad59ca --require 0023` exit 0; `grep -c merge-grants` over the README and workflow.md diff prints 0; ADR 0011 carries `Merge partly superseded by ADR 0023.` comment_ratio.py 0 of 1135 code lines, exit 0; number_guards.py check PASS; design_surfaces.py check exit 0; dispatch_records.py 14 records complete.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Script and observed output under `### Minimal acceptance script`; adr_lint.py `docs/adr --since 2dad59ca` printed "22 ADR file(s) checked, 0 legacy", exit 0, with and without `--require 0023`. Findings under `### Findings`; verdict PASSED at 3fd841789db9c76d863ae4f723184c790471a7da with the open-P1 blocker above.

### Security review (validation)

Security review (validation): security/validation-2.yaml at 3fd841789db9c76d863ae4f723184c790471a7da
Security finding (validation 2) 1: declined: MEDIUM, dormant until a merge-grants entry exists; the Captain's 2026-10-18 ruling named the never list and plugin `scripts/` (kc-pr-flow, kc-ship-flow, kc-journey-map and others) is outside it; I reproduced `kc-pr-flow/scripts/github-repo-write.sh` plus its test as class script-with-test; revisit in the ADR of the first grant of script-with-test, other or docs-only (see G1)
Security finding (validation 2) 2: declined: LOW, dormant until a merge-grants entry exists; I reproduced `docs/Dev/x.md` as docs-only with a merge line under a docs-only grant; a macOS checkout is case-insensitive; one-line fix `re.I` (see G2)
Security finding (validation 2) 3: declined: LOW, fails closed (a traceback leaves no `next: merge ` last line, so the printed line does not merge); same as validation 1 finding 3
Security finding (validation 2) 4: declined: LOW as the reviewer rated it, but the same defect is Codex P1 4306363862, which README step 5 blocks; I reproduced it (see G3)
Security finding (validation 2) 5: declined: LOW, the window is one shell pipeline, the head is pinned by GitHub and `check` compares the base first; a bounded residual

### Findings

Dispositions by the Review-finding disposition. None is Material: field 4 (trigger evidence) fails for each, because no `merge-grants:` entry exists in any README, so no merge line can print outside a scratch repository. What would make each Material is the first grant entry.
- G1 Deferred risk (security finding 1): the never list is the Captain's named list; `kc-*/scripts/*` and `docs/ship`, `docs/plan-flow` are outside it. `script-with-test` matches the test by name only. Reproduced. FO may raise it when the first grant ADR is drafted.
- G2 Deferred risk (security finding 2): `docs/Dev/...` is docs-only, reproduced; the fix is case-insensitive matching.
- G3 Deferred risk, open Codex P1 comments on this head (review:5562139252): (a) 4306363860 `Resolve grants from the fetched trunk`: `check` reads `merge-grants:` and the ADR from the working tree, so a grant the Captain removed on trunk still prints a merge line in a stale checkout; reproduced with a scratch bare origin whose `origin/main` README has no grant while the local README does. (b) 4306363862 `Fail closed when historical PR state is unreadable`: `label()` returns `pending` when `gh pr view` fails, and `check` stops only on `failure`; reproduced with a stub gh that closes a record's PR when readable (ask line) and errors on it (merge line). Both are small: (a) read README and ADR with `git show origin/<trunk>:<path>` after the fetch, or hold when they differ; (b) a distinct `unknown` state that suppresses the merge line and stays out of the statistics. No FO decline is recorded for either. README step 5 requires a repair and revalidation, or the Captain's waiver with the reason.
- G4 Deferred risk (security findings 3 to 5): fail closed, or a one-pipeline window.
- G5 Polish: survivors (a) and (d) above have no test row (the `gate|budget` name rule; newest-wins in the dedupe).
- G6 Polish: doc_impact.py lists 9 documents; the implementation reports record 8; `kc-dev-flow-2/references/sd/adoption.md` has no `unaffected:` line (reported as F9 in validation 1, unchanged).
- G7 Polish: ADR 0023 does not say that `check` reads the grant's ADR (Status Accepted, whole entry) or the Captain's 2026-10-18 list; the ruling lives in the task file only.
- Minimal necessity (same candidate): holds, points and the per-ask record serve every merge ask now (AC-1, 2, 6). Class, grant line and `calibrate` still have no consumer until a grant exists; 35 of 35 archived PRs of this repository class never. The two cycle-1/2 rules (grant needs its ADR; wider never list) each map to a Captain ruling or a Codex P1 and a mutation that only they fail.

### Minimal acceptance script

Needs: this repository checkout at the path below, python3, git, `gh` signed in (read-only calls). Run in a fresh bash. Not covered: a real GitHub merge (only the saved AC-5 transcript at f3f0fa3e), any grant (none exists), the two open Codex P1 (G3), relay, subspace-web or qnow, and Spacedock's pr-merge and merge guard after an FO-run merge.

```bash
set -u
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0
WF=$REPO/.context/dev2-adoption/worktree/docs/dev2
ST=$WF/.spacedock-state
H=3fd841789db9c76d863ae4f723184c790471a7da
W=/tmp/merge-gatekeeper-accept
export PYTHONDONTWRITEBYTECODE=1
echo "== 1. check out the PR head"
rm -rf $W /tmp/merge-gatekeeper-accept-task
git -C $REPO worktree add --detach $W $H >/dev/null 2>&1; git -C $W rev-parse HEAD
echo "== 2. word budget and decision record"
python3 -B $W/kc-dev-flow-2/scripts/lint-skills.py | grep -E "words"
(cd $W && python3 -B $PKG/scripts/adr_lint.py docs/adr --since 2dad59ca --require 0023; echo "adr_lint exit=$?")
echo "== 3. the merge check's own tests (about 2-3 minutes)"
python3 -B $W/kc-dev-flow-2/scripts/test_delivery_gate.py 2>&1 | tail -n 3
echo "== 4. grant ADR, never list, quoted prod, deep directories, trunk fetch, re-run line"
python3 -B $W/kc-dev-flow-2/scripts/test_delivery_gate.py GrantAdrTests NeverAddedTests CodexP1Tests RecheckTests 2>&1 | tail -n 3
echo "== 5. the check on PR 666 itself (scratch copy of the task), then the security-review check"
mkdir /tmp/merge-gatekeeper-accept-task && cp $ST/merge-gatekeeper.md /tmp/merge-gatekeeper-accept-task/ && cp -R $ST/merge-gatekeeper /tmp/merge-gatekeeper-accept-task/ && echo "Merge ask." > /tmp/merge-gatekeeper-accept-task/gate.txt
python3 -B $W/kc-dev-flow-2/scripts/delivery_gate.py check /tmp/merge-gatekeeper-accept-task/merge-gatekeeper.md --pr iamcxa/kc-claude-plugins#666 --text-file /tmp/merge-gatekeeper-accept-task/gate.txt --workflow-dir $WF | cut -c1-200; echo "check exit=${PIPESTATUS[0]}"
python3 -B $W/kc-dev-flow-2/scripts/validation_security.py check $ST/merge-gatekeeper.md; echo "validation_security exit=$?"
echo "== 6. clean up"
git -C $REPO worktree remove --force $W && rm -rf /tmp/merge-gatekeeper-accept-task && echo removed
```

Expected: step 1 prints the 40-hex head above. Step 2 prints `references/sd/workflow.md: 5430 of 5430 words; ...`, `22 ADR file(s) checked, 0 legacy` and `adr_lint exit=0`. Step 3 ends `Ran 73 tests in <n>s` and `OK`. Step 4 ends `Ran 18 tests in <n>s` and `OK`. Step 5: while PR 666 is a Draft, `the PR is a draft`, a `next: hold the ask` line and `check exit=1`; once it is Ready with CI green, exit 0 with `validation security review security/validation-2.yaml: 5 findings, 5 declined, 0 decisions`, up to 12 `point:` lines and a `point: more:` line, `class: never`, a `record:` line and last line `next: ask for merge with this text.`; then `validation_security exit=0` (the script is run from the PR checkout: the installed 0.24.0 package has no validation_security.py) with the same `validation security review security/validation-2.yaml: 5 findings, 5 declined, 0 decisions` line. Step 6 prints `removed`.

Observed, run exactly as written above in a fresh `env -i ... bash --noprofile --norc` shell:

```
== 1. check out the PR head
3fd841789db9c76d863ae4f723184c790471a7da
== 2. word budget and decision record
references/sd/workflow.md: 5430 of 5430 words; no unlisted passage repeats it
22 ADR file(s) checked, 0 legacy
adr_lint exit=0
== 3. the merge check's own tests (about 2-3 minutes)
Ran 73 tests in 107.225s

OK
== 4. grant ADR, never list, quoted prod, deep directories, trunk fetch, re-run line
Ran 18 tests in 26.154s

OK
== 5. the check on PR 666 itself (scratch copy of the task), then the security-review check
the PR is a draft
next: hold the ask; mark the PR ready under the Captain's authority and let its CI finish.
check exit=1
validation security review security/validation-2.yaml: 5 findings, 5 declined, 0 decisions
validation_security exit=0
== 6. clean up
removed
```

Step 5 on the Ready path could not run live (PR 666 is a Draft; I do not mark it ready). I ran the same `check` on a scratch copy of this task with the real PR facts, `isDraft` set false, behind a stub gh: it printed `validation security review security/validation-2.yaml: 5 findings, 5 declined, 0 decisions`, 12 `point:` lines and `point: more: 21 not shown`, `class: never`, a `record:` line and `next: ask for merge with this text.`

### Summary

PASSED at 3fd84178 against AC-1 to AC-12 and both Captain rulings: 72 of 76 of my mutations fail the suite (the four survivors are two Polish gaps and two redundant guards), and the head passes lint and every package test on a clean merge into origin/main ffd620b4. The three earlier Codex P1 hold fixed. A new Codex review of this head left two P1 (grants read from the working tree, unreadable historical state treated as pending); I reproduced both, class them Deferred risk because no grant exists, and README step 5 still requires FO to repair and revalidate them or take the Captain's waiver. The security review (validation 2) has five findings, all declined with reasons.
