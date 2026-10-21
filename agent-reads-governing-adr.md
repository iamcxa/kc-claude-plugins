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
            - id: gate-attempt:agent-reads-governing-adr-ideation-2
              briefing:
                id: briefing:agent-reads-governing-adr:ideation:attempt-2:revision-1
                digest: sha256:4bf66c1383357c714735271a9a58731234dc290d2f208df1e8192f27d83d11cc
                room-ref: ./agent-reads-governing-adr/review/ideation/briefing-2
---

## Scope

- Source: finding relayed by the decision-log Paseo session (agent 1bcf070c, 2026-10-20), compared against "The ADR your agent never read" (https://tianpan.co/blog/2026/07/02/the-adr-your-agent-never-read). Captain ruling in this session: 「ADR 部分按你說的做」 (2026-10-20), approving FO's proposal 「在 dev2 開一張待辦任務，不開 GitHub issue。做法照你說的，從各 repo 這一層下手」: an instruction-file pointer to `docs/adr`; a hook that lists every ADR title at session start or dispatch, derived from the files so it cannot go stale; a check that the ADR paths AGENTS.md and CLAUDE.md name resolve; this repository and qnow first; a package rule only after the effect is measured.
- Bite, read 2026-10-20: qnow origin/next AGENTS.md lines 24-27 point agents at branch `docs/qnow-target-architecture-adr`, which `git ls-remote` does not find, while `docs/adr/0001-qnow-target-architecture.md` exists on `next` at 165414 bytes (handed to the qnow FO the same day); kc-claude-plugins origin/main CLAUDE.md and AGENTS.md mention ADR 0 times.
- Present in kc-dev-flow-2 0.26.0 (per the relayed finding, to re-read at ideation): verbatim Words/Options/Recommended, FO decision records, ideation reads ADRs in its area, the Precedent rule, comments cite ADRs, `adr_lint.py` checks a Superseded-by target exists. Missing: the implementation worker is not told to read ADRs; no way to find the ADRs "in its area"; validation checks format, not contradiction; no staleness audit or size limit.
- Upstream first: Spacedock and kc-dev-flow-2 hooks and dispatch; ADR 0003 (adopter-owned hooks); the kc-decision-log CLI (PR #681, planning) may later serve as the find-and-read tool; merge-guard-stops-unasked-merges also adds adopter hooks, so the two designs share a hook layout.
- Non-goals: splitting qnow's 165 KB ADR 0001 (qnow's call); contradiction checking at validation unless measurement shows the pointer and list are not enough.

## FO alignment

Correction (FO, 2026-10-21): the ideation gate resolution reason recorded 2026-10-21 reads "add  to CLAUDE.md" because a shell substitution dropped the token; the Captain's D3 ruling is to add one `@AGENTS.md` import line to CLAUDE.md, as the quoted 「可以」 answered.

Peer: kc-decision-log (renamed kc-adr) = Paseo agent 1bcf070c (Captain asked 「可以，但也找adr fo討論一下」, 2026-10-21). Asked: whether the hook slot and later S30 swap match D10/S30, whether the hook should call or avoid duplicating anything of theirs, and any Codex or adopter conflict. Answered 2026-10-21: (1) the slot and swap match; titles from each ADR's H1 are right; nothing needed from them now. (2) Their P1 CLI is dropped; their POC dev2-poc `adr-read-and-route-poc` (96 runs, Claude sonnet and Codex gpt-6.1-sol high) found agents read the governing ADR before deciding in every arm including no help (35/35); the real gap was placing new information (Claude 6/10 to 9/10 with a skill, Codex 5-6/10). The pointer and hook should list titles and say where ADRs live and when to look, never restate an ADR's Decision text. (3) No conflict with a pointer-only AGENTS.md; Codex 0.162.1 silently skipped an untrusted SessionStart hook, so a Codex hook needs a one-time per-project trust step. FO to check their POC record before relying on the 35/35 figure.

Alignment: needed at ideation; which adopters and which hook moment are his to accept.
Result: aligned 2026-10-21 at the batch-5 sitting through D1 to D4 (recorded in the ideation gate resolution reason): first adopters this repository (qnow as its own task), no title hook now (reopen: dev2-poc task moment-of-use-rules-long-session-poc, which exists in the dev2-poc state checkout, not this one), pointer in a new AGENTS.md imported by CLAUDE.md, path check as a path-filtered non-required CI job.
Surfaces: none
Visible change: none
Outside this repository's surfaces: each first adopter's AGENTS.md or CLAUDE.md and its user- or repo-level hook files (this repository and qnow).

## Captain amendments

### Amendment 1 — 2026-10-22, chat
Captain: 「問題是 qnow 那種錯誤是怎樣發生的？」 then 「ADR 讀取那張，路徑檢查改成「禁止指向分支」」 (chat, 2026-10-22, batch-5 sitting)
Asked: 「我改建議用這個更簡單的做法：檢查程式遇到「指向分支」的寫法就直接報錯，要求改成指向主線上的檔案；不去遠端查分支是否存在。」
Supersedes: AC-4
Design: the path check refuses any ADR reference that names a branch or other ref (a `git show REF:path` form) with a reason telling the author to point at the file on the trunk; it does not fetch or resolve refs. A plain repository path is checked for existence. The remote-resolution half of the design is dropped.
Superseded text: **AC-4**: The path check resolves, and fails for the stated reason. Evidence: `python3 scripts/adr-path-check.test.py` exit 0, one case each, each asserting the printed reason: good path 0; missing file 1 `no such file in the tree`; `docs/adr` removed 1 `directory missing or holds no NNNN-*.md`; ref on origin 0; tag 0; ref only in a local branch 1 `not a branch or tag on origin`; `docs/adr/NNNN-x.md` placeholder 0; a fixture holding the five stale lines of qnow's pointer (generic branch name) 1. Falsifiers (run once each by the implementation worker, reported): replace the fetch resolver by `git cat-file -e REF:PATH` and the local-only case turns red; make the directory test always pass and the removed-directory case turns red; make the printed reason empty and every failing case turns red. Current: prototype run 2026-10-21 (above), test file not written.
Override: recommended resolving refs against origin (design D1 option A); Captain chose refusing branch refs; area: ADR path check

## Design

Revision (cycle 2, 2026-10-21): the Captain's gate ruling `revise` removes the title hook (cycle 1 `SessionStart`/`SubagentStart` script, +451 words), keeps the pointer and the named-path check, puts the pointer in a new `AGENTS.md` with one `@AGENTS.md` import line in `CLAUDE.md`, limits the pointer to where ADRs live and when to look, lands qnow as its own task, and runs the check as a path-filtered, non-required CI job. The `## Scope` bullets that describe the hook are the original request and stand as history. The hook's reopen is the dev2-poc task `moment-of-use-rules-long-session-poc`; no task of that name exists in the state checkout today (`ls` 2026-10-21), so FO files it.

Alignment note: `## FO alignment` records `Alignment: needed at ideation` and carries no `Result:` line; FO records the result before `gate prepare`, as in cycle 1.

```mermaid
flowchart LR
  A[AGENTS.md: Decisions paragraph] -->|"@AGENTS.md import"| C[CLAUDE.md]
  A -->|read directly| X[Codex]
  C --> M[Claude main session]
  C --> E[Claude ensign subagent]
  A -.->|names| D[docs/adr/]
  P[PR touching AGENTS.md, CLAUDE.md or docs/adr] --> K[CI job: adr-path-check]
  K -->|reads| A
  K -->|reads| C
  K -->|resolves| D
```

### Chain check (2026-10-21)

- Spacedock 0.27.2: `spacedock --help` lists nothing about ADRs or instruction files. kc-dev-flow-2 at origin/main c27e765: `git grep -n -E 'AGENTS\.md|CLAUDE\.md' origin/main -- 'kc-dev-flow-2/scripts/*.py'` finds no non-test script that reads either file, and `adr_lint.py` (docstring: "Check a docs/adr directory against the dev2 ADR format") reads only `docs/adr`. Nothing checks that an instruction file's ADR path resolves, and nothing tells a worker where ADRs live. Completeness of the missing parts: not found by these two searches.
- Peer boundary rule (kc-adr/kc-decision-log, relayed 2026-10-21; its task `kc-decision-log-cli` states it as "Instruction files point, they do not restate"): the pointer says where ADRs live and when to look, never an ADR's Decision text. This design follows it.
- ADR 0003 (the adopter, not the package, owns hooks) no longer bears: this design ships no hook. ADR 0020 budgets the workflow README (`lint-skills.py`), not `CLAUDE.md`; the word rise below is disclosed anyway.
- Sibling adopters (read-only, 2026-10-21): qnow `origin/next` 348a79d69 `AGENTS.md` lines 24-27 still point at `docs/qnow-target-architecture-adr`; `git ls-remote --heads origin docs/qnow-target-architecture-adr` returns 0 heads, while a local branch of that name exists in `~/conductor/repos/qnow`. qnow is its own task (Captain, D2).
- This repository, `git ls-tree -r --name-only origin/main`: no `AGENTS.md`; `CLAUDE.md` and the five plugin `CLAUDE.md` files name `docs/adr` or ADR 0 times (`grep -c -i -E 'docs/adr|\bADR\b'`); `docs/adr/` holds 28 `NNNN-<slug>.md` files whose slug is the title.

Observed facts (2026-10-21, Claude Code 2.1.305, Codex CLI 0.162.1, scratch repo `/tmp/adrprobe2/imp` with `CLAUDE.md` = `@AGENTS.md` and a marker sentence in `AGENTS.md`):
- `claude -p --model haiku` answered the marker; a `general-purpose` subagent answered it; a real `subagent_type: spacedock:ensign` call answered it. So the import reaches the main session and an ensign.
- `codex exec -s read-only` answered the marker from `AGENTS.md` alone.
- Control: the same `AGENTS.md` with a `CLAUDE.md` that has no import line: `claude -p --model haiku` answered `NONE`. So the import line is what carries the paragraph to Claude Code.
- Not probed: after-compaction reload of `CLAUDE.md`, and a Codex subagent.

### PRFAQ

Press release: every Claude session and ensign in this repository, and every Codex session, now opens with one short paragraph saying decisions are ADRs in `docs/adr/` and to read the one whose title covers what it is about to decide. A CI job refuses a pull request whose `AGENTS.md` or `CLAUDE.md` names an ADR path or `git show REF:path` that does not resolve.

FAQ
- Does an agent now read the ADR when it decides? Not guaranteed, and this task does not claim it. The paragraph reaches the agent (probed); opening the file stays the agent's act. The peer's 96-run POC found the governing ADR read in 35 of 35 runs with no help (relayed, not re-verified here), so the pointer's marginal effect is unmeasured and may sit at a ceiling. That goes to the PR's `without-it unanswered`.
- Why no title list? Ruled out for now; the long-session POC reopens it.
- What breaks without each part? Pointer: qnow shows the failure of a hand-written pointer (stale branch, 0 heads on origin); this repository has no pointer at all (0 hits), which is the recorded gap. Check: it is the only part that would have caught qnow's stale pointer. Import line: without it Claude Code does not see `AGENTS.md` (control probe above answered `NONE`).
- What does it cost? +40 words at FO start and each ensign start (below); one path-filtered CI job per matching PR, minutes not measured (AC-5 records the run).

### Mechanism

1. `AGENTS.md` (new, repo root), 39 words:

       # AGENTS.md

       ## Decisions

       Decisions that bind this repository are ADRs: one file each in `docs/adr/`, named `NNNN-<title>.md`. Before you decide or recommend something a title could cover, run `ls docs/adr` and read the file whose title covers it.

2. `CLAUDE.md`: one added line at the end, `@AGENTS.md`. Nothing else in `CLAUDE.md` moves; moving the rest is task `agents-md-holds-instructions`.
3. `scripts/adr-path-check.py` (Python 3 standard library, run as `python3 -I scripts/adr-path-check.py`) over every tracked `AGENTS.md` and `CLAUDE.md`: (a) each `docs/adr/<name>.md` path named must exist in the tree; (b) each `git show REF:docs/adr/...` must resolve: `HEAD` or a 40-hex SHA by `git cat-file -e`, any other REF by `git fetch --depth=1 origin refs/heads/REF` (then `refs/tags/REF`) and `git cat-file -e FETCH_HEAD:path`, so a branch that exists only locally fails; (c) a bare `docs/adr/` named must exist and hold a `NNNN-*.md`. `NNNN` and `<...>` placeholders are not paths. Exit 1 prints file, reference and reason, one line each.
4. `scripts/adr-path-check.test.py`: fixture repo plus a local bare `origin`; one case per row of AC-4, each asserting the printed reason, not only the exit code.
5. `.github/workflows/adr-path-check.yml`: `on.pull_request.paths` = `AGENTS.md`, `CLAUDE.md`, `**/AGENTS.md`, `**/CLAUDE.md`, `docs/adr/**`, `scripts/adr-path-check*`, the workflow file; `permissions: contents: read`; checkout pinned like `kc-dev-flow-2-tests.yml` (`persist-credentials: false`); two steps, the test then the check. Not added to branch protection (Captain, D4). The repository's required check `marketplace-parity.yml` carries a comment explaining why a required check must not be path-filtered; this job is not required, so the filter is safe.
6. No ADR lands: one paragraph, one import line and one non-required job are cheap to reverse and the Captain's words are in the gate record. No `## Number guards` entry.

Prototype (not a deliverable, `/tmp/adrprobe2/proto/adr_path_check.py`, 2026-10-21): on a scratch repo holding qnow `origin/next` 348a79d69's `AGENTS.md` with qnow's real `origin` URL, the stale text exits 1 with `ref docs/qnow-target-architecture-adr is not a branch or tag on origin`. On a fixture with a bare `origin`: good path 0, branch on origin 0, tag 0, bare `docs/adr/` 0, missing file 1 "no such file in the tree", local-only branch 1, and a plain `git cat-file -e localonly:path` on the same text succeeds (the false pass the fetch resolver avoids). The candidate `AGENTS.md` and `CLAUDE.md` over `docs/adr` from origin/main c27e765: exit 0. Defect found in the prototype: with `docs/adr` deleted it crashed with a traceback and exit 1, so exit 1 alone proved nothing; AC-4 asserts the reason text.

Bite and consumer: bite: qnow's stale pointer (above) and this repository's absent pointer. Consumers: every Claude session, ensign and Codex session in this repository (the paragraph); the CI job (the check); and qnow's own task, which copies the script (the only place the `git show REF:` form can bite today; this repository names no ref, so here the check guards only that `docs/adr/` exists and holds ADR files).

### Words FO reads at each moment

Rule (root learning.md "Measure the words FO reads at each moment, not one file's size"): `len(text.split())` over every passage that instructs a step due at the moment, same count for base and candidate. Counted 2026-10-21 with `wc -w` and Python `len(text.split())` on origin/main c27e765 `CLAUDE.md` (1,314) against the candidate files built in `/tmp/adrprobe2/cand` (`CLAUDE.md` 1,315, `AGENTS.md` 39).

| Moment | Base | Candidate | Change |
| --- | --- | --- | --- |
| FO startup, also resume, clear, fork | workflow text (513 at 0.22.1, not recounted) plus `CLAUDE.md` 1,314 | same plus `CLAUDE.md` 1,315 and `AGENTS.md` 39 | +40 |
| Each ensign start | dispatch file plus `CLAUDE.md` 1,314 | same plus 1,315 and 39 (ensign sees the import: probed) | +40 |
| After compaction | not probed | at most +40 if the host reloads `CLAUDE.md` | at most +40 |
| Idle on an open PR | unchanged text | unchanged | +0 |
| Idle on a merged PR | unchanged text | unchanged | +0 |
| After the archive | unchanged text | unchanged | +0 |
| The merge ask | unchanged text | unchanged | +0 |

Cycle 1 added +451 at the same startup and ensign moments; the hook's removal takes that to +40. No workflow README, mod, skill or script output is edited, so the four non-start rows are equal by construction (AC-6 lists the changed paths; AC-7 recounts).

### Needs decision

The five rulings (no hook, pointer in `AGENTS.md` with the import line, pointer-only boundary, qnow separate, non-required path-filtered job) are the Captain's and are not reopened. Two choices remain:

- **D1: does the `git show REF:path` form belong in this repository's script?** Plainly: this repository names no ref, so only qnow can use that part. Options: (A) build it now, tested by fixtures; (B) check only file paths and the bare directory here, and let qnow's task add the ref form. Recommend A: the recorded bite is a ref form, and a script without it would not have caught it; qnow's copy then stays one file. Worse under A: about half the script serves a consumer outside this repository and is exercised here only by fixtures.
- **D2: does a behaviour measurement gate this task?** Plainly: whether the pointer changes what an agent reads is not measured here, and the peer's POC found reading at 35 of 35 without help. Options: (A) no gate; the PR body lists the unmeasured effect under `without-it unanswered`; (B) a two-arm run (no pointer, pointer; n=5; metric: opened the governing ADR before its first Edit) must run before the PR opens. Recommend A: the peer's ceiling means B would likely show no difference, and the Captain already kept the pointer. Worse under A: the repository ships a paragraph whose read-effect is unknown, and the PR cannot say it works, only that it reaches the agent.

Past rulings: the Captain's batch-5 sitting words are in the gate record above (D1-D4); `git -C <state> grep -n 'Override:'` finds none about instruction-file pointers beyond them.

### Limits

- The paragraph reaches the agent; reading the ADR stays the agent's act and nothing checks it.
- The check sees path and `git show REF:` forms only. Prose such as "the ADR lives on branch X" with no path is not detected.
- Fetching a named ref needs network at check time; in CI a deleted or renamed branch fails the job, which is the intended signal.
- `CLAUDE.md` reload after compaction and Codex subagent loading are unprobed; the plugin-level `CLAUDE.md` files name no ADR and are not changed.
- A non-required job can be merged past (Captain's D4).
- Non-goals: any title list or hook; a package script, rule or `adoption.md` section; qnow, relay and web edits; moving the rest of `CLAUDE.md` (`agents-md-holds-instructions`); splitting qnow's ADR 0001.

### Batch overlap

Files this design changes: `AGENTS.md` (new), `CLAUDE.md` (one line), `scripts/adr-path-check.py` (new), `scripts/adr-path-check.test.py` (new), `.github/workflows/adr-path-check.yml` (new). No `docs/adr/` file, package path, `docs/dev2/` path, `.claude/` or `.codex/` file. Checked 2026-10-21 by grepping each task file in the state checkout for `CLAUDE.md|AGENTS.md`, `.github/workflows` and `docs/adr`.

- new-work-starts-from-a-story-map (ideation): no shared file. Its overlap table lists "agent-reads-governing-adr (one new ADR)" in `docs/adr/`; this revision lands no ADR, so that row is now wrong and FO should drop it.
- codex-reader-reads-receipt-marker: no shared file (`extensions/codex/`, `pr_watch.py`; it mentions `.github/workflows` in its own text, not as a file it changes).
- merge-ask-holds-missing-clauses: no shared file (`delivery_gate.py`, `role_triggers.py`).
- fo-write-checks-parse-top-level: no shared file.
- idle-names-failing-seeds: no shared file.
- agent-reads-governing-adr: this task.
- agents-md-holds-instructions (backlog; not in the dispatch list, same files): it moves the rest of `CLAUDE.md` into `AGENTS.md`, so it must land after this one and keep the `## Decisions` paragraph; the check reads both files, so it survives the move unchanged. Land this first.
- kc-decision-log-p1: no task file in the state checkout (`ls`, 2026-10-21); no shared file known. kc-decision-log-cli (ideation): its text states the pointer-only rule and a placement rule naming `CLAUDE.md or AGENTS.md`, edits neither file. kc-decision-log-handoff-trial (backlog): none.
- pr-review-lite-value-pilot (implementation): its text records an immutable target tree with `CLAUDE.md` files and no tracked `AGENTS.md`; this change creates an `AGENTS.md` on `main` only, so the frozen target is unaffected unless the pilot re-reads `main`; FO confirms before ordering.
- release-acceptance, journey-server-host-pilot: no task file in the state checkout; none known. journey-canvas-hosted-poc: none.
- merge-guard-stops-unasked-merges (backlog): none now (no hook is added here).

Recommended order: this task before agents-md-holds-instructions; otherwise no ordering constraint.

## Acceptance criteria

**AC-1**: The pointer exists, is short and restates no ADR. Evidence: `AGENTS.md` holds the `## Decisions` paragraph; `python3 -c 'print(len(open("AGENTS.md").read().split()))'` prints a number at most 45; for every file in `docs/adr/`, its slug (name without number and `.md`) is not a substring of `AGENTS.md` or of the lines `git diff origin/main -- CLAUDE.md` adds. Falsifier: add one ADR slug to the paragraph and the substring step fails. Current: draft is 39 words, no slug (checked on `/tmp/adrprobe2/cand`).
**AC-2**: `CLAUDE.md` changes by one added line, `@AGENTS.md`. Evidence: `git diff --numstat origin/main -- CLAUDE.md` prints `1	0	CLAUDE.md`. Falsifier: any other count. Current: built in the scratch copy; the committed file not yet.
**AC-3**: The pointer reaches the main session, an ensign and Codex. Evidence: in a clean checkout of the candidate, `claude -p --model haiku` asked "which command do your project instructions tell you to run before deciding?" answers `ls docs/adr`; the same question through a `subagent_type: spacedock:ensign` call answers it; `codex exec -s read-only` answers it. Falsifier: delete the `@AGENTS.md` line and the Claude main and ensign answers lose it (Codex still has it). Current: probed 2026-10-21 with a marker sentence in a scratch repo (main, `general-purpose`, `spacedock:ensign`, Codex all returned it); committed files not yet.
**AC-5**: The job runs on the intended pull requests only and is not required. Evidence: on the implementation PR, a commit adding a nonexistent `docs/adr/` path to `AGENTS.md` gives a red `adr-path-check` run and the fix commit a green one (`gh run list --workflow adr-path-check.yml`); a push touching only an unrelated file starts no run of it; `gh api repos/iamcxa/kc-claude-plugins/branches/main/protection/required_status_checks --jq '.contexts'` does not list it; the green run's duration is recorded as the cost. Falsifier: the broken path runs green, an unrelated push starts the job, or the context is listed as required. Current: not run; cost not measured.
**AC-6**: The change reaches nothing else. Evidence: `git diff --name-only origin/main` lists exactly the five paths in `### Batch overlap`; no path under `kc-dev-flow-2/`, `docs/dev2/`, `docs/adr/`, `.claude/` or `.codex/`. Falsifier: any other path. Current: not yet verified.
**AC-7**: Words are recounted with an independent copy of the counting script. Evidence: base (origin/main) against candidate gives FO startup +40 and ensign start +40 (these two numbers are the measured ones; a different count is reported as measured), and the four non-start moments' texts byte-equal because AC-6's list touches none of them; the report states that the rise is disclosed and that ADR 0020 does not cover `CLAUDE.md`. Falsifier: a differing non-start text, or a startup delta above 45. Current: 1,314 to 1,354 measured in the scratch copy; recount at the candidate not yet run.

**AC-8** (Amended by Captain, amendment 1; replaces AC-4) The path check passes a trunk path and refuses for the stated reason. Evidence: `python3 scripts/adr-path-check.test.py` exit 0, one case each asserting the printed reason: an existing `docs/adr/` path exits 0; a missing path exits 1 naming it; a `git show <branch>:docs/adr/...` reference exits 1 with a reason that says to point at the file on the trunk, with the branch present locally and absent on origin alike. Falsifier: resolving the ref (the branch case exits 0 when the branch exists locally), or exit 1 without the reason.

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

## Stage Report: ideation (cycle 2)

- DONE: Redesign per the Captain's rulings in the ideation gate resolution reason (revise, 2026-10-21): no title hook (remove it from the design, criteria and word counts, and name the dev2-poc long-session POC as its reopen); keep the pointer and the named-path check; the pointer lives in a new AGENTS.md and CLAUDE.md gains one `@AGENTS.md` import line; the pointer only says where ADRs live and when to look and restates no ADR text (kc-adr peer's boundary rule); qnow lands as its own task, not here; the path check runs as a path-filtered, non-required CI job; rewrite the criteria to match and recount the words FO reads
  `## Design` rewritten (hook, settings, byte-identical copy and ADR removed); pointer 39 words plus one import line; check script with fetch-based ref resolver; non-required path-filtered job; AC-1 to AC-7. Probes 2026-10-21 in `/tmp/adrprobe2`: import reaches `claude -p`, `general-purpose` and `spacedock:ensign` subagents and `codex exec`; without the import Claude answers NONE. The dev2-poc task `moment-of-use-rules-long-session-poc` does not exist in the state checkout, so FO files it.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task and live task of other sessions that changes the same file or check, so FO can order implementation
  `### Batch overlap`: five files; agents-md-holds-instructions shares `CLAUDE.md`/`AGENTS.md` (this first); new-work-starts-from-a-story-map lists a new ADR from this task that no longer exists (FO drops that row); pr-review-lite-value-pilot frozen-target note; release-acceptance, journey-server-host-pilot and kc-decision-log-p1 have no task file in the state checkout.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: `CLAUDE.md` 1,314 to 1,315 plus `AGENTS.md` 39, so startup and each ensign start +40 (was +451 in cycle 1), compaction at most +40 (unprobed), four other moments +0 by construction; counted with `wc -w` and `len(text.split())`; AC-7 recounts.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 to AC-7, each with evidence, falsifier and current state (prototype exit codes and reasons measured for the check; AC-2, AC-3 committed files, AC-5 CI run and cost, AC-6 not yet verifiable at ideation). Decisions: D1 whether the `git show REF:` form ships here (recommend A, build it), D2 whether a behaviour measurement gates the task (recommend A, no; peer's 35 of 35 ceiling). The Captain's five rulings are not reopened.

### Summary

The design shrinks to a 39-word `AGENTS.md` paragraph, one `@AGENTS.md` line in `CLAUDE.md`, a standard-library check script with a test, and a path-filtered non-required CI job; the startup rise falls from +451 to +40 words. The check's `git show REF:` form can bite only on qnow today, which D1 states; the pointer's read-effect is unmeasured and goes to `without-it unanswered` (D2). `## FO alignment` still carries no `Result:` line; FO records it before `gate prepare`.
