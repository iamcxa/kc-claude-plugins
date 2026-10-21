---
title: An agent reads the governing ADR at the moment it decides, from a pointer and an injected title list it cannot miss
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:agent-reads-governing-adr:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:agent-reads-governing-adr-backlog-1
              briefing:
                id: briefing:agent-reads-governing-adr:backlog:attempt-1:revision-1
                digest: sha256:4555cfe2d87c5df9e402e1068a17b3198b7ff83581d292254a521244ec91a858
                room-ref: ./agent-reads-governing-adr/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:agent-reads-governing-adr:backlog:1
                briefing: briefing:agent-reads-governing-adr:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T07:28:59.894802Z"
                decision: approve
                reason: Captain 「繼續」 (chat, 2026-10-21), answering FO's question 「這 5 張都批准進入設計嗎？」 for the five batch-5 backlog gates presented together; approves entering ideation under the pilot profile, as recommended.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:agent-reads-governing-adr:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:agent-reads-governing-adr-ideation-1
              briefing:
                id: briefing:agent-reads-governing-adr:ideation:attempt-1:revision-1
                digest: sha256:9a5e57c703f57686bd8709b095c120407178e4b2c85df1b6d0d45e7159b0f48a
                room-ref: ./agent-reads-governing-adr/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:agent-reads-governing-adr:ideation:1
                briefing: briefing:agent-reads-governing-adr:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T13:29:14.659939Z"
                decision: revise
                reason: 'Captain, batch-5 sitting 2026-10-21: D1 first 「可以，但也找adr fo討論一下」 (option A), then, after the kc-adr peer''s POC evidence and its ceiling-effect caveat, 「可以」 to FO''s revised recommendation: build the pointer and the named-path check now and no title hook; the hook waits for the dev2-poc long-session POC (moment-of-use-rules-long-session-poc). Override: recommended option A (design D1); Captain chose no hook now, on FO''s revised recommendation; area: ADR title hook. D2 「Qnow那樣可以」: this task lands only this repository and FO hands qnow its own task. D3 「可以，建立agent.md，這個應該統一成此檔案而不是Claude.md，合理嗎？」 then 「可以」: create AGENTS.md with the pointer and add  to CLAUDE.md; moving the rest of CLAUDE.md is task agents-md-holds-instructions. D4 「可以」: a path-filtered CI job, not required. Revise: the design returns to ideation to drop the hook and carry D3.'
---

## Scope

- Source: finding relayed by the decision-log Paseo session (agent 1bcf070c, 2026-10-20), compared against "The ADR your agent never read" (https://tianpan.co/blog/2026/07/02/the-adr-your-agent-never-read). Captain ruling in this session: 「ADR 部分按你說的做」 (2026-10-20), approving FO's proposal 「在 dev2 開一張待辦任務，不開 GitHub issue。做法照你說的，從各 repo 這一層下手」: an instruction-file pointer to `docs/adr`; a hook that lists every ADR title at session start or dispatch, derived from the files so it cannot go stale; a check that the ADR paths AGENTS.md and CLAUDE.md name resolve; this repository and qnow first; a package rule only after the effect is measured.
- Bite, read 2026-10-20: qnow origin/next AGENTS.md lines 24-27 point agents at branch `docs/qnow-target-architecture-adr`, which `git ls-remote` does not find, while `docs/adr/0001-qnow-target-architecture.md` exists on `next` at 165414 bytes (handed to the qnow FO the same day); kc-claude-plugins origin/main CLAUDE.md and AGENTS.md mention ADR 0 times.
- Present in kc-dev-flow-2 0.26.0 (per the relayed finding, to re-read at ideation): verbatim Words/Options/Recommended, FO decision records, ideation reads ADRs in its area, the Precedent rule, comments cite ADRs, `adr_lint.py` checks a Superseded-by target exists. Missing: the implementation worker is not told to read ADRs; no way to find the ADRs "in its area"; validation checks format, not contradiction; no staleness audit or size limit.
- Upstream first: Spacedock and kc-dev-flow-2 hooks and dispatch; ADR 0003 (adopter-owned hooks); the kc-decision-log CLI (PR #681, planning) may later serve as the find-and-read tool; merge-guard-stops-unasked-merges also adds adopter hooks, so the two designs share a hook layout.
- Non-goals: splitting qnow's 165 KB ADR 0001 (qnow's call); contradiction checking at validation unless measurement shows the pointer and list are not enough.

## FO alignment

Peer: kc-decision-log (renamed kc-adr) = Paseo agent 1bcf070c (Captain asked 「可以，但也找adr fo討論一下」, 2026-10-21). Asked: whether the hook slot and later S30 swap match D10/S30, whether the hook should call or avoid duplicating anything of theirs, and any Codex or adopter conflict. Answered 2026-10-21: (1) the slot and swap match; titles from each ADR's H1 are right; nothing needed from them now. (2) Their P1 CLI is dropped; their POC dev2-poc `adr-read-and-route-poc` (96 runs, Claude sonnet and Codex gpt-6.1-sol high) found agents read the governing ADR before deciding in every arm including no help (35/35); the real gap was placing new information (Claude 6/10 to 9/10 with a skill, Codex 5-6/10). The pointer and hook should list titles and say where ADRs live and when to look, never restate an ADR's Decision text. (3) No conflict with a pointer-only AGENTS.md; Codex 0.162.1 silently skipped an untrusted SessionStart hook, so a Codex hook needs a one-time per-project trust step. FO to check their POC record before relying on the 35/35 figure.

Alignment: needed at ideation; which adopters and which hook moment are his to accept.
Surfaces: none
Visible change: none
Outside this repository's surfaces: each first adopter's AGENTS.md or CLAUDE.md and its user- or repo-level hook files (this repository and qnow).

## Design

Alignment note: `## FO alignment` records `Alignment: needed at ideation` and carries no `Result:` line. This worker read checklist item 1 of the dispatch (bring the hook moment and the first adopters back as Captain decisions) as the alignment, and designed. FO records the result before `gate prepare`; sibling `new-work-starts-from-a-story-map` held on the same shape.

### Chain check (2026-10-21)

- Spacedock 0.27.2: `spacedock dispatch build --help` has no adopter content slot (only FO-written `--scope-notes-file`); the mods in use here carry FO lifecycle hooks (`## Hook: startup`, `idle`, `merge`). Nothing lists ADRs for a worker.
- kc-dev-flow-2 at origin/main c27e765 (0.27.0): `git grep -n -i adr -- kc-dev-flow-2/skills kc-dev-flow-2/references` finds the Precedent rule, ideation "read the ADRs in its area", `adr_lint.py` (format, `Superseded by` target exists), observer's Precedent check, and comments citing ADRs. Not found: a title lister, a way to find "its area", an instruction to the implementation worker, any check that an instruction file's ADR path resolves. Present as the relayed finding said; completeness of the missing parts: not found.
- ADR 0003 (`The package documents secret-read enforcement and ships no hook`): a plugin `hooks/hooks.json` fires in every project where the plugin is enabled, so the package ships none; an adopter owns its hooks. This design follows it. Its "Codex has no `PreToolUse` equivalent" is out of date (below); not this task's to reopen.
- kc-decision-log: its P1 brief lists `Hooks (D10, S30; shared with dev2 task agent-reads-governing-adr)` as a non-goal, and slice-map D10 says the hook shares this mechanism and its trigger moment is set "when slotted into a slice". So this task owns the hook slot; the CLI (reads one ruling at a full commit, dev2 engineering ADRs without Decision keys unsupported by D9) is not usable as the title source now. Dependency direction: S30 later swaps the script behind the same hook entries.
- Sibling adopters, read-only 2026-10-21: qnow `origin/next` already commits `.claude/settings.json` with two `SessionStart` echo hooks and a `.claude/hooks/` directory; `subspace-relay` `origin/main` has 60 numbered ADRs and its AGENTS.md says `ADR` 0 times; `subspace-web` has 42 and names two by number for one constraint, no directory pointer. Same gap; they stay outside this task.
- The article (tianpan.co, 2026-07-02), read in full: it recommends (1) a pointer in the instruction file, (2) one-line constraints injected there, (3) comments at the site of a deliberate oddity, and warns that a stale record is worse than none. It names no hook, no title list and no path check; those are the Captain's ruling, not the article's. A derived list is level 2 without the staleness the article warns of; the package's comment rule already does level 3.

Observed facts used (all 2026-10-21, Claude Code 2.1.305, Codex CLI 0.162.1, probes in `/tmp`, haiku):
- A project `.claude/settings.json` `SessionStart` hook's stdout reached the main `claude -p` session and did not reach a subagent (also a named background subagent).
- A `SubagentStart` hook's `hookSpecificOutput.additionalContext` reached the subagent, including a background one; a `matcher` on `agent_type` scoped it (a `general-purpose` entry fired, a `spacedock:ensign` entry did not for it). A real `subagent_type: spacedock:ensign` call produced the payload `agent_type: "spacedock:ensign"` and received the context under matcher `^(spacedock:)?ensign$`.
- Docs (code.claude.com/docs/en/hooks): `SessionStart` fires on `startup|resume|clear|compact|fork`; plain stdout and `additionalContext` are capped at 10,000 characters and over the cap Claude Code keeps only a 2,000-character preview in the context.
- Codex: a repo-local `.codex/hooks.json` `SessionStart` `additionalContext` reached the model in `codex exec`. Codex `SubagentStart` is documented and not run. The docs add that project hooks load only when the project's `.codex/` layer is trusted.

### PRFAQ

Press release: a session in this repository or in qnow now opens with every decision on file, one line per ADR, and each ensign gets the same list when it is dispatched. The list is read from the ADR files by a short script, so adding, superseding or deleting an ADR changes it with no edit. Each repository's instruction file points at `docs/adr/` in one short paragraph, and CI refuses a pull request whose AGENTS.md or CLAUDE.md names an ADR path or ref that does not resolve.

FAQ
- Does an agent now read the ADR when it decides? Not guaranteed. The list is in its context at session start and at ensign start (probed); opening the file stays the agent's act and nothing checks it. AC-8 measures it before any package rule.
- Why not a package hook? ADR 0003, and the Captain's ruling that a package rule waits for the measured effect.
- Why a copy of the script in each repository? A repository-committed hook cannot depend on a plugin-cache path (`.../kc-dev-flow-2/0.27.0/...` changes per release and qnow's own hook notes a cloud workspace has no plugins). The copies are byte-identical (AC-2) and the reason to exist is that no shipped home is allowed yet.
- What breaks without each part? The pointer: qnow's AGENTS.md sends agents to `git show docs/qnow-target-architecture-adr:...`, a branch `git ls-remote --heads origin` does not find (0 heads, 2026-10-21), while the file sits on `next`. The list: qnow's `docs/adr/README.md` indexes 2 of 40 ADRs, so a hand-kept index drifts. The check: it is the only part that would have caught the stale pointer.
- What does it cost? Words at two moments (below) and, unmeasured, one path-filtered CI job per repository.

### Flow

```mermaid
sequenceDiagram
  participant H as Harness hook
  participant FO as First officer session
  participant E as Ensign subagent
  participant R as docs/adr files
  participant CI as CI path check
  H->>R: SessionStart: script reads titles
  H-->>FO: title list in context (startup, resume, clear, compact, fork)
  FO->>E: dispatch
  H->>R: SubagentStart, agent_type ensign: script reads titles
  H-->>E: title list in context
  E->>R: opens the ADR whose title covers its decision (agent's act, nothing checks it)
  alt a title covers the decision
    E-->>FO: applies it and cites it; authority, merge, outward action, irreversible change, money stay asked
  else no title covers it
    E-->>FO: decides and reports; a new ruling lands as an ADR
  end
  Note over CI,R: PR touching AGENTS.md, CLAUDE.md or docs/adr: check resolves each named ADR path and ref, red if one does not
```

### Mechanism (per adopter, none in the package)

1. Pointer, one paragraph in the instruction file the repository's agents read: decisions are ADRs in `docs/adr/`; a session-start hook lists every title; read the file whose title covers what you are about to decide. qnow replaces the stale lines in AGENTS.md (`Read it before proposing a new app ...` through `not a file on next yet.`, 33 words) with 51 words naming `docs/adr/0001-qnow-target-architecture.md` as a file. This repository adds a `## Decisions` paragraph (34 words) to CLAUDE.md.
2. Hook script `.claude/hooks/adr-titles.py`, Python 3 standard library, run as `python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/adr-titles.py" docs/adr`. It lists files named `NNNN-*.md`, takes the title from the first heading with `# N.` or `# ADR N —` removed (filename slug if absent), tags `[legacy]` when the head says `Status: Legacy` and `[proposed]` for Proposed, omits `Superseded by` and `Deprecated` and says how many, prints newest first up to 8,000 characters then `N older not listed: ls docs/adr`, and wraps the text as `hookSpecificOutput.additionalContext` for the event named on stdin. One header line precedes the list: `Governing decisions, N in docs/adr/ (list derived from the files). Before you decide or recommend something one of these covers, read that file.`
3. Entries in the repository's `.claude/settings.json`: `SessionStart` (no matcher) and `SubagentStart` with matcher `^(spacedock:)?ensign$`. qnow adds two entries beside its existing ones; this repository creates the file. `.claude/worktrees/` is already ignored here and `.claude/settings.json` is not.
4. Check `python3 -I .claude/hooks/adr-titles.py --check` over every tracked `AGENTS.md` and `CLAUDE.md`: each `docs/adr/NNNN-*.md` path must exist in the tree, and each `git show REF:docs/adr/...` must resolve at `HEAD`, a full SHA, `refs/remotes/origin/REF` or `refs/tags/REF`, never a bare local branch. Exit 1 names file, reference and reason. A placeholder `docs/adr/NNNN-x.md` is not a path.
5. ADR landing with the change (no number yet; FO reserves it): `adopters-list-adr-titles-by-hook-and-check-named-paths`, ruling: the adopter, not the package, lists ADR titles at session and ensign start from the files and checks the ADR references its instruction files name; Words 「ADR 部分按你說的做」 (Captain, 2026-10-20). Parallel to ADR 0003.
6. Retained documents (`references/retained-documents.md`): CLAUDE.md and AGENTS.md keep their structure; the paragraph is the one home for the pointer; qnow's stale lines are replaced, not left beside the new ones.

Existing-code check: boundary is "an agent finds the ADRs that govern a decision". Searches above (Spacedock help, `git grep` over the package, qnow and relay/web trees): completeness not found, so nothing existing is replaced. Observation that the change is needed: qnow stale pointer, 2 of 40 index, and the measured fact that SessionStart does not reach a subagent, so the pointer alone does not reach workers.

Measured prototype (not a deliverable, `/tmp/adrprobe/proto/adr_titles.py`, run on `git archive` of kc-claude-plugins `origin/main` c27e765 and qnow `origin/next` 012e079): this repository 28 ADRs, 29 lines, 417 words, 2,394 bytes; qnow 40 ADRs (0001 `[legacy]`, 0024 does not exist), 41 lines, 694 words, 4,304 bytes. The cap is reached at roughly 75 ADRs of qnow's average title length (8,000 / 107 bytes); relay's 60 ADRs would be about 6,400 bytes if its titles are as long (estimate, not measured).

### Words FO reads at each moment

Rule (root learning.md "Measure the words FO reads at each moment"): `len(text.split())` over every passage and script output that instructs a step due at the moment, same count for base and candidate. This design edits no workflow README, mod, skill or script output, so the five lifecycle moments below are equal by construction; only session and ensign start gain words, and they gain a list that instructs no lifecycle step. Base figures are the archived `fo-lifecycle-mod` recount (kc-dev-flow-2 0.22.1, 2026-10-14) and are not recounted here; AC-9 recounts at the candidate with an independent copy.

| Moment | Base (words) | This repository | qnow |
| --- | --- | --- | --- |
| FO startup (also resume, clear, fork) | 513 workflow text (0.22.1) plus the instruction file: CLAUDE.md 1,314 / AGENTS.md 6,117 | +34 pointer +417 list = +451 | +18 pointer (33 to 51) +694 list = +712 |
| FO after compaction (SessionStart `compact`) | not counted before | +417 list again | +694 list again |
| Each ensign start (dispatch) | dispatch file plus the instruction file | +34 +417 = +451 | +18 +694 = +712 |
| Idle on an open PR | 427 | +0 | +0 |
| Idle on a merged PR | 458 | +0 | +0 |
| After the archive | 211 | +0 | +0 |
| The merge ask | 423 | +0 | +0 |

This is a deliberate rise at three moments, which ADR 0020 says needs the Captain's words recorded with it; his 「ADR 部分按你說的做」 (2026-10-20) is the nearest ruling and covers the hook, not these numbers, so D1 states them.

### Needs decision

Adopters are settled by his words (this repository and qnow first, 2026-10-20); approving the gate confirms them. The open choices:

- **D1: when the hook fires.** Plainly: the list can go into every start, or only into worker starts, or only when a file is edited. Options: (A) `SessionStart` plus `SubagentStart` on ensigns; (B) `SubagentStart` on ensigns only, the FO and interactive sessions get the pointer only; (C) a `PreToolUse` hook on Edit/Write that injects only ADRs matching the edited path, later. Recommend A: FO and the Captain's own sessions are where Precedent and gate questions are decided, and workers are where code decisions are made; probes show each event reaches only its own party. Worse under A: +451 words (this repository) or +712 (qnow) at every FO start, every compaction and every ensign dispatch, growing with the ADR count up to 8,000 characters; it runs against ADR 0020's reading-budget stance. B drops the FO cost and leaves the FO's Precedent step without the list. C has no path-to-ADR mapping and nothing probed.
- **D2: how the qnow change lands.** Plainly: this task is on kc-claude-plugins; qnow has its own flow and its own first officer. Options: (A) this task's implementation lands only this repository and FO files a qnow backlog task (`spacedock new`) carrying the pointer text, the two settings entries, the byte-identical script and the check wiring; (B) the implementation worker also opens a hand-made Draft PR on qnow. Recommend A: qnow's gates, `next` trunk and reviewers stay its own, and the stale-pointer fix is already with its first officer. Worse under A: qnow's stale pointer stays until its flow schedules the task; the pair is not one PR.
- **D3: Codex.** Plainly: Codex reads AGENTS.md, which this repository does not have, and has its own hook file. Options: (A) pointer only: create AGENTS.md here with the same paragraph (34 words), no Codex hook; (B) A plus `.codex/hooks.json` `SessionStart` (probed: reaches `codex exec`); (C) nothing for Codex. Recommend A: Codex `SubagentStart` is unprobed and project hooks need a per-machine trust step; the kc-decision-log handoff trial runs a Codex first officer and worker, which would read nothing in this repository today. Worse under A: a Codex worker gets the pointer without the list; B is one file and one trust step away once a Codex worker is seen missing a governing ADR.
- **D4: where the path check runs.** Plainly: the check can run on every pull request that touches the instruction files or ADRs, or in a local commit hook. Options: (A) a path-filtered CI job (`AGENTS.md`, `CLAUDE.md`, `docs/adr/**`) per repository, not a required check until he says so; (B) the repository's commit hook (qnow `.husky/pre-commit`; here `.githooks/pre-commit` only works after `git config core.hooksPath .githooks`); (C) both. Recommend A: a fresh CI checkout has no local branches, which is the case that hid the bite; B alone is skippable. Worse under A: a non-required check can be merged past; cost is one job per matching PR, minutes not measured (AC-7 records the run's duration).

Past rulings: `git -C <state> grep -n 'Override:'` (2026-10-21) hits only prose in archived designs and observer reports, none about hooks, pointers or ADR lists; ADR 0003 and ADR 0020 are followed as above.

### Limits

- The list comes from the session's checkout at its HEAD: not the worker's worktree, not an ADR still in an open PR, and a stale FO checkout lists stale titles.
- Reading the ADR stays the agent's act. qnow's ADR 0001 is Legacy, 165,414 bytes in one file; splitting it is qnow's call (non-goal).
- Python 3 in qnow's cloud workspace is unverified (its hook notes a bash-only sandbox); on a local machine `python3` exists.
- Claude and Codex only; the project-hook trust prompt of Codex is not exercised.
- Non-goals: a package script, rule or `adoption.md` section (waits for AC-8's measure, per the Captain's words); contradiction checking at validation; the kc-decision-log CLI as source; splitting qnow ADR 0001.

### Batch overlap

Files this design changes: this repository `CLAUDE.md`, `AGENTS.md` (new, if D3 A or B), `.claude/settings.json` (new), `.claude/hooks/adr-titles.py` (new), one CI workflow file (new), one new ADR in `docs/adr/` (number reserved by FO at implementation dispatch). qnow (D2 A, by its own task): `AGENTS.md`, `.claude/settings.json`, `.claude/hooks/adr-titles.py`, its CI or pre-commit file. Package, workflow README and mods: none.

- new-work-starts-from-a-story-map (ideation, held): none.
- codex-reader-reads-receipt-marker: none (`extensions/codex/codex_review.py`).
- merge-ask-holds-missing-clauses: none (`delivery_gate.py`, `role_triggers.py`).
- fo-write-checks-parse-top-level: none (`delivery_gate.py`, `design_surfaces.py`).
- idle-names-failing-seeds: none (`pr_watch.py`); my design adds no `pr_watch.py` output.
- agent-reads-governing-adr: this task.
- kc-decision-log-p1 (backlog): none now; its slice-map D10/S30 names this task as owner of the hook slot, so a later S30 reuses these settings entries and changes only the script behind them.
- kc-decision-log-cli (ideation): none; it lists hooks as a non-goal and adds a `kc-decision-log/` plugin directory.
- kc-decision-log-handoff-trial (backlog): none.
- pr-review-lite-value-pilot (implementation), journey-canvas-hosted-poc, journey-server-host-pilot: no file or check in common (grep of their task files for CLAUDE.md, AGENTS.md, `.claude/settings`, `docs/adr` finds only their own evidence text and a reserved ADR 0015).
- release-acceptance (ideation): shares the ADR index; its draft ADR carries no number yet, so both take numbers from `number_guards.py reserve`.
- merge-guard-stops-unasked-merges (backlog, not in the dispatch list): adopter hook layout. Its guard is a `PreToolUse` hook in the Captain's user-level settings, which is a different file from this repository's `.claude/settings.json`; if it moves to the repository file, the second to land rebases the `hooks` object.

Recommended order: this task needs no other task first; land it before kc-decision-log S30 is slotted, and before merge-guard if that guard moves to the repository settings file.

## Acceptance criteria

**AC-1**: The list is derived from the files. Evidence: in a temp copy of this repository's `docs/adr` plus qnow's, `python3 -I .claude/hooks/adr-titles.py docs/adr` prints one line per `Accepted` ADR with the number and the heading title; adding `9999-x.md` (`# 9999. X`, Accepted) adds exactly that line, a `Superseded by` file is omitted and counted, a `Status: Legacy` file is tagged `[legacy]`. Falsifier: a hand-kept list does not change when a file is added (qnow's `docs/adr/README.md` indexes 2 of 40). Current: prototype measured 28 / 40 rows (above); script not yet written.
**AC-2**: The script is one file, byte-identical in both repositories. Evidence: `cmp` of the two `.claude/hooks/adr-titles.py` copies, the qnow copy checked in the qnow task. Falsifier: any byte differs. Current: not yet verified.
**AC-3**: The list stays under the harness cap. Evidence: with 200 synthetic ADRs the output is at most 8,000 characters, newest first, ending `N older not listed: ls docs/adr`. Falsifier: output over 10,000 characters, which Claude Code replaces with a 2,000-character preview. Current: prototype truncation tested only by reading; not yet verified.
**AC-4**: The list reaches the main session and an ensign, and only those. Evidence: from the committed `.claude/settings.json`, `claude -p` in a checkout reports the first listed title; a `spacedock:ensign` subagent reports it; an `Explore` subagent does not; after `/compact`-equivalent `SessionStart` source `compact` the list is present again. Falsifier: remove an entry and the matching party reports none. Current: plumbing verified with probe strings on 2026-10-21 (SessionStart to main, not to subagents; SubagentStart to ensign payload `agent_type: "spacedock:ensign"` under the matcher; `general-purpose` scoping); the committed files and the `compact` source not yet verified.
**AC-5**: The pointer paragraphs exist and resolve. Evidence: this repository's CLAUDE.md has the `## Decisions` paragraph (34 words) and, if D3 A or B, AGENTS.md the same; `git diff --name-only origin/main` shows no path under `kc-dev-flow-2/` or `docs/dev2/`. Falsifier: a package path in the diff, or a paragraph naming a path AC-6 rejects. Current: not yet verified.
**AC-6**: The named-path check catches the recorded bite and not a local-branch false pass. Evidence: `--check` on qnow's AGENTS.md at `origin/next` 012e079 exits 1 naming `docs/qnow-target-architecture-adr:docs/adr/0001-qnow-target-architecture.md`; on text pointing at `docs/adr/0001-qnow-target-architecture.md` it exits 0; on this repository's CLAUDE.md it exits 0; `docs/adr/NNNN-x.md` is not flagged; in a repository with a local-only branch holding the file the stale text still exits 1. Falsifier: replacing the resolver by a plain `git cat-file -e REF:PATH` makes the local-branch case exit 0. Current: prototype run 2026-10-21: stale AGENTS.md exit with one line, fixed text clean, and the plain resolver passed the stale text because `docs/qnow-target-architecture-adr` exists as a local branch at 3eaf303ad in `~/conductor/repos/qnow` and not on origin; script not yet written.
**AC-7**: The check is wired to run. Evidence: on a throwaway branch a PR touching AGENTS.md with a broken ADR path gives a red job; a PR touching only another file does not start it; the run's duration is recorded as the cost. Falsifier: the broken path merges green, or the job runs on unrelated PRs. Current: not yet verified; cost not measured.
**AC-8**: The effect is measured before any package rule. Evidence: in a synthetic checkout of this repository's `docs/adr` with a `migrations/` directory, `claude -p --model sonnet --output-format stream-json` with the prompt "fix the typo in migrations/0003_orders.sql in place; it was already applied" under three arms (none, pointer only, pointer plus list), n=5 each; metric: the run opened the governing ADR file (`0002-applied-migrations-are-frozen-and-numbers-are-reserved.md`) before its first Edit or Write. Pre-registered rule: keep the hook if the list arm opens it in at least 4 of 5 and at least 2 more runs than the pointer-only arm; otherwise the report says the hook bought nothing measured and the Captain rules on removing it (the worker does not remove it). Counts only, no rate claim at n=5. Falsifier: the list arm opens it no more often than pointer-only. Current: not run; cost not measured.
**AC-9**: Words at each moment are recounted. Evidence: an independent copy of the counting script gives, at the candidate and at the base, the five lifecycle moments equal and startup, compaction and ensign start up by 451 (this repository) and 712 (qnow) words; the Captain's words for the rise are recorded in the gate. Falsifier: any of the four non-start moments differs, or the rise is unrecorded. Current: inputs measured above (pointer 34 and 18, list 417 and 694); recount not yet run.

## Stage Report: ideation

- DONE: Design the adopter-level pointer, the derived ADR-title hook and the named-path check for this repository and qnow, reading the cited article and the kc-decision-log P1 brief's non-goal on hooks (D10); bring the hook moment and the first adopters back as decisions for the Captain
  `## Design` (Chain check, Mechanism, Flow); article read in full (names no hook, list or check); D10 read in `docs/journey/kc-decision-log` p1-development-brief.md and slice-map.md at origin/main; D1 hook moment and D2 qnow landing with D3, D4 in `### Needs decision`; adopters shown as settled by his 「ADR 部分按你說的做」.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, fo-write-checks-parse-top-level, idle-names-failing-seeds, agent-reads-governing-adr) and live task of other sessions (kc-decision-log-p1, kc-decision-log-cli, kc-decision-log-handoff-trial, pr-review-lite-value-pilot, release-acceptance, journey-canvas-hosted-poc, journey-server-host-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  `### Batch overlap`: no file or check shared with any listed task; shared ADR index with release-acceptance; merge-guard-stops-unasked-merges added (adopter hook layout); recommended order line present.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: five moments plus compaction and ensign start; startup +451 (this repository) / +712 (qnow), compaction +417 / +694, ensign start +451 / +712, four other moments +0; base figures are the archived 0.22.1 recount, not recounted (AC-9 does).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  `## Acceptance criteria` AC-1 to AC-9 each carry evidence and a falsifier; `design_surfaces.py check` exit 0 from the 0.27.0 root and from the loaded 0.26.0 root ("design surfaces presentable"); D1 to D4 each with a recommendation and what gets worse. Per criterion, current evidence:
  AC-1: prototype only (28 / 40 ADRs, 417 / 694 words), script not written. AC-2: not yet verified. AC-3: not yet verified (cap rule from docs; no 200-ADR run). AC-4: plumbing verified 2026-10-21 with probe strings (SessionStart to main only, SubagentStart to `spacedock:ensign` payload and matcher scoping); committed files and `compact` source not yet verified.
  AC-5: not yet verified. AC-6: prototype run on qnow `origin/next` 012e079: stale text flagged by the remote-only resolver, passed by a plain `git cat-file` because a local branch exists; script not written. AC-7: not yet verified, cost not measured. AC-8: not run. AC-9: inputs measured, recount not run.

### Summary

The design puts the work in each adopter, not the package: a one-paragraph pointer, a byte-identical standard-library script run by `SessionStart` and by `SubagentStart` on ensigns (probed: each reaches only its own party), and a path-filtered CI check that resolves ADR paths and refs against remotes and tags only, because a local-only branch hid the qnow bite. The notable costs are a deliberate word rise at session and ensign start (D1) and an effect nobody has measured yet (AC-8 gates any package rule). `## FO alignment` carries no `Result:` line; this worker read checklist item 1 as the alignment and designed, and FO records the result before `gate prepare`. Package note: `Skill(kc-dev-flow-2:ideation)` loaded from the orphaned 0.26.0 cache while the dispatch names 0.27.0; I ran `design_surfaces.py check` from both roots and both exit 0 (the `### Batch overlap` rule exists only in 0.27.0 `principles.md`), so FO's choice of root changes nothing here.
