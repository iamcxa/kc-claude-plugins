---
title: Dispatches name the reachable FO, the package's script paths and the secret wrapper, and a report never ends in a false FAILED line
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: done
gates:
    version: 1
    records:
        - id: gate:dispatch-and-report-hygiene:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:dispatch-and-report-hygiene-backlog-1
              briefing:
                id: briefing:dispatch-and-report-hygiene:backlog:attempt-1:revision-1
                digest: sha256:3d7eb68063e7caa0a0a5ba0193029cb4e98dcee67ba791fbd0c188aa4d0b24d8
                room-ref: ./dispatch-and-report-hygiene/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:dispatch-and-report-hygiene:backlog:1
                briefing: briefing:dispatch-and-report-hygiene:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-29T23:28:24.783586Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「可以」 to the FO''s dev2 fix batching, batch A first'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:dispatch-and-report-hygiene:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:dispatch-and-report-hygiene-ideation-1
              briefing:
                id: briefing:dispatch-and-report-hygiene:ideation:attempt-1:revision-1
                digest: sha256:f2446fc48e47ac2133a7fc632c4fadde34c341f480f3618f04e4660426bc5e45
                room-ref: ./dispatch-and-report-hygiene/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:dispatch-and-report-hygiene:ideation:1
                briefing: briefing:dispatch-and-report-hygiene:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T04:11:29.495698Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「准」 — dispatch facts section, FAILED-only rule, secret guard documented not shipped'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:dispatch-and-report-hygiene:validation
          stage: validation
          attempts:
            - id: gate-attempt:dispatch-and-report-hygiene-validation-1
              briefing:
                id: briefing:dispatch-and-report-hygiene:validation:attempt-1:revision-1
                digest: sha256:357f014ae431faa6df3fcf7c0b4e00608cab8e37eabc1e7f051881c76b21a109
                room-ref: ./dispatch-and-report-hygiene/review/validation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-30T04:53:38.490912Z"
                reason: 'Captain 2026-09-30: 「重跑」 — re-run AC-6 with the candidate package loaded in isolated Claude state'
            - id: gate-attempt:dispatch-and-report-hygiene-validation-2
              briefing:
                id: briefing:dispatch-and-report-hygiene:validation:attempt-2:revision-1
                digest: sha256:e57baea97dcc71b656f37c513d707be30088e4fe56f5b0de97124c3f4151a08e
                room-ref: ./dispatch-and-report-hygiene/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:dispatch-and-report-hygiene:validation:2
                briefing: briefing:dispatch-and-report-hygiene:validation:attempt-2:revision-1
                by: person:captain
                at: "2026-09-30T06:49:56.83577Z"
                decision: revise
                reason: 'Captain 2026-09-30: 「准」 — every dispatch''s FO scope notes carry the absolute package root, checklists name scripts as <package>/scripts/NAME.py; back to implementation, then re-run AC-6'
            - id: gate-attempt:dispatch-and-report-hygiene-validation-3
              briefing:
                id: briefing:dispatch-and-report-hygiene:validation:attempt-3:revision-1
                digest: sha256:fc507d43d074ba8b33227ffa114384d445019eaaa567d38f03370a66a9ddbcba
                room-ref: ./dispatch-and-report-hygiene/review/validation/briefing-3
              resolution:
                type: Resolution
                id: resolution:spacedock:dispatch-and-report-hygiene:validation:3
                briefing: briefing:dispatch-and-report-hygiene:validation:attempt-3:revision-1
                by: agent:first-officer
                at: "2026-09-30T07:03:27.883414Z"
                decision: approve
                reason: Validation PASSED on a88175e9; opening a Draft PR only; merge stays with the Captain
                conn:
                    quote: 'No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar'
                    source: ~/.claude/CLAUDE.md, Autonomous action boundaries
              application:
                target-stage: done
                state: consumed
started: 2026-09-30T04:12:30Z
worktree: .worktrees/spacedock-ensign-dispatch-and-report-hygiene
pr: pr-merge:535
verdict: PASSED
completed: 2026-09-30T07:48:53Z
archived: 2026-09-30T07:48:54Z
---

Four dispatch and report defects from qnow dogfooding (2026-09-28..30) that cost retries or leaked secrets.

## Scope

Captain 2026-09-30, approving the FO's batching of the dev2 fixes: 「可以」 — batch A (guardrails) first. This task covers issues #526, #527, #528 and #530.
Evidence (qnow): every worker reported "team-lead was unreachable, sent to main"; a report line "- FAILED: none." blocked `spacedock status --set`; one worker searched the whole filesystem for comment_ratio.py for about three hours; two workers printed the Clerk development secret key despite dispatch-note bans, and a user-level PreToolUse(Bash) guard (block Netlify environment and database API reads, 1Password value reads and reveals, Keychain password reads) has held since.
Non-goals (ideation, 2026-09-30): any change to Spacedock (its dispatch builder, ensign contract or report parser; those are spacedock-dev/spacedock #523, #608 and #625); a secret-guard hook shipped in the package; better regex precision in the Captain's user-level guard; a script or lint that checks stage reports; Codex or Pi behavior beyond the stated limits; edits to any adopter repository; migration and ADR numbering (sibling task `migration-and-number-guards`).

## Acceptance criteria

**AC-1** (#528): A worker that loads a kc-dev-flow-2 skill is told the absolute package root by that skill, and no skill or reference names a package script in a way that leaves the root open.
Verified by: (a) `lint-skills.py` and `test_lint_skills.py`: on a copy of the tree, a bare `comment_ratio.py`, a `/absolute/plugin/scripts/` path, a `{package}` placeholder, and a skill folder that uses `<package>` while its `SKILL.md` lacks a `Package root:` line each exit 1 naming the file; the unmodified tree exits 0. Falsifier: remove the `Package root:` line from `skills/implementation/SKILL.md` and the third case flips. (b) Probe run at validation: `claude -p --plugin-dir <checkout>/kc-dev-flow-2` invoking `kc-dev-flow-2:implementation` prints a `Package root:` value that is an absolute path in which `scripts/comment_ratio.py` exists (the ideation probe showed `${CLAUDE_PLUGIN_ROOT}` expands in a skill body on Claude Code 2.1.284, including inside a dispatched subagent). Limit: Codex expansion is not probed; the skill's fallback sentence says the root is two directories above its own `SKILL.md`.

**AC-2**: The three worker stages receive the same `## Dispatch facts` section through Spacedock, so no FO has to retype it.
Verified by: `test_sd_dispatch.py --sd-plugin-root <active Spacedock root>` asserts `dispatch show-stage-def --stage ideation|implementation|validation` each print `## Dispatch facts` with its `Signal:`, `Package:` and `Secrets:` bullets, and that `dispatch build` for implementation writes a dispatch file containing them. The same test builds each dispatch with `--scope-notes-file` carrying `Package root: <absolute root>` and a script line written with that root, and asserts both appear in the dispatch file, the root line ahead of the checklist. Falsifier: drop `Dispatch facts` from the ideation entry's `context-sections` and the ideation assertion fails; pass `/dev/null` as the scope notes and the root assertion fails. Limit: proves transport, not that a worker obeys or that an FO writes the notes.

**AC-3** (#526): The section names the recipient the runtime lists for the first officer instead of `team-lead`, and a worker sends the completion message once.
Verified by: the behavior run in AC-6 (its transcript shows the first completion `SendMessage` addressed to `main` and accepted). Limit: bounded to Claude Code dispatch; Codex and Pi completion blocks do not use `SendMessage`. The line is a workaround for Spacedock #523/#608 and is deleted when they land; Spacedock's own FO reference still says workers should not send completion to `main`, so a session that follows that sentence over this section will still see the old fallback.

**AC-4** (#527): The report rule is in every stage skill, and the FO's recovery step names the offending line.
Verified by: `test_sd_dispatch.py` writes a task whose committed stage report ends `- FAILED: none.` with an evidence line and asserts `status --set` exits non-zero with "durable, complete", then that `status --read <task> --stage <stage> --checklist` prints `status=FAILED` and `text=none.`; the same report without that bullet asserts `--set` exits 0 (both reproduced by hand at ideation on Spacedock 0.27.2). Falsifier: if Spacedock starts accepting `FAILED: none` (issue #625), the first assertion flips and the rule and test are deleted. Limit: the refusal message itself cannot name the line (Spacedock reports one boolean); a worker's compliance with the sentence is measured only by AC-6 (one run) and by later dispatches.

**AC-5** (#530): Dispatches name one run-time secret wrapper; the package documents the guard contract and ships no hook.
Verified by: `show-stage-def` for implementation and validation prints a `Secrets:` bullet naming the wrapper (AC-2 test); `references/sd/adoption.md` gains a "Secret reads" section stating the contract (a PreToolUse Bash hook that exits 2 and whose message names the wrapper; adopter-owned patterns; the rephrase rule; Codex has no equivalent hook) with no machine-local path; the package tree still has no `hooks/` PreToolUse entry (`git diff --stat` at validation lists none). The ideation probe showed a plugin PreToolUse hook fires in an unrelated project's cwd, which is why shipping is rejected. Limit: enforcement stays in the adopter or user settings; the package cannot verify an adopter installed one.

**AC-6**: One real worker, dispatched from a scratch workflow that carries the candidate `workflow.md`, avoids the three observed failures.
Verified by: at validation, a scratch workflow (`/tmp`, not the repository) built from the candidate; FO builds one implementation dispatch for a trivial task (write one file, run the package's `comment_ratio.py` on a two-commit scratch repo, report) with scope notes carrying `Package root: <absolute root>` and a checklist that writes the script as `<absolute root>/scripts/comment_ratio.py`, and spawns one ensign on it. Pass: its transcript has no failed `SendMessage`, no `find`/`mdfind`/`ls -R` search for a script, its report has no `FAILED:` bullet and `status --set` accepts it. Fail on any one. Limit: N=1; qnow's rate for the signal failure was every worker, so one clean run is informative for it and only weakly informative for `FAILED: none`, which qnow saw once.

## FO alignment

Needed at ideation: the name the runtime actually exposes for the dispatching FO; how every dispatch carries the absolute scripts directory of the installed package version; the report-template rule that FAILED marks only an unmet item; and whether kc-dev-flow-2 ships the secret guard for adopters or documents it, plus how dispatches name one run-time secret wrapper.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none

## Design

**Ruling.** Move the four sentences that FOs now retype by hand into the package, each in the place that reaches the worker without the FO's help: package facts in the stage skills (`Package root:` line, the FAILED rule), and runtime and adopter facts in one new workflow section, `## Dispatch facts`, that Spacedock inlines into every worker stage through `context-sections` (the completion recipient, the meaning of `<package>`, the secret wrapper). Because a worker composes its first commands from the dispatch file before it loads a skill or reads that section, the FO also writes the skill's absolute `Package root:` value into the scope notes of every worker dispatch and writes every package script it names in a checklist or scope note as `<package>/scripts/NAME.py` with that root substituted (Captain 「准」, 2026-09-30, on validation cycle 2). The package ships no secret-guard hook; it documents the contract for adopters. One Captain ruling is asked (Unresolved decisions 1); the design ships with the recommendation.

### What this changes, in plain words

Today each First Officer (FO, the workflow orchestrator) has to remember four things when it dispatches a worker: who to signal, where the package scripts are, not to write "FAILED: none", and how not to leak a key. Every qnow worker that missed one of them lost time or leaked a secret. After this change the worker is told all four by the package itself. The path to the scripts comes from the skill the worker loads anyway, so it always matches the version that worker runs, and the FO also writes that path into the dispatch file the worker reads before anything else; the other three come from one short section every worker stage receives.

### Evidence read 2026-09-30

- **Recipient (#526).** This session's roster lists the addressable agents as `main` and a sibling worker; Spacedock's builder writes `SendMessage(to="team-lead", ...)` (`completionSignalBlock` in `internal/dispatch/build.go`, "pinned to the single name team-lead"), while its own `claude-fo-dispatch.md` says workers reach the lead with `SendMessage(to="main")`. Spacedock issues #523 and #608 (open, no comments) describe the same failure as "harmless, but every worker spends turns discovering it".
- **Scripts (#528).** Three installs of this package exist on this machine: `cache/kc-claude-plugins/kc-dev-flow-2/0.9.0` (the enabled one), `~/.claude/plugins/local/kc-dev-flow-2` (byte-identical today, the path this dispatch named) and `cache/local/kc-dev-flow-2/0.1.0` (disabled, old). Stage text writes `<package>/scripts/...`, `{package}/...` and `/absolute/plugin/scripts/...` and defines none of them.
- **Report (#527).** Reproduced on Spacedock 0.27.2 in a scratch workflow: a committed report ending `- FAILED: none.` makes `status --set` print only "cannot change status away from entered stage ... until a durable, complete ## Stage Report ... is committed", because `hasCompleteStageReport` returns one boolean over five conditions (missing report, no items, an item not DONE/SKIPPED, an item with no evidence line, no Summary) plus uncommitted state. `status --read <task> --stage <stage> --checklist` does name it: `status=FAILED start=13 end=14 text=none.`. Removing the bullet and committing lets `--set` pass.
- **Guard (#530).** `~/.claude/hooks/block-secret-reads.py` is 7 regex rules over the whole command text, exit 2 with a message naming `scripts/with-dev-secrets.sh`. Its false positive happened in this session: my own read-only Bash call was refused in full because its text contained a guarded tool name as test data, and nothing in it ran. A plugin `hooks/hooks.json` PreToolUse hook fired in an unrelated project's cwd under `claude -p --plugin-dir` (probe, this session).

### Chain check (what already exists)

| Layer | Found | Consequence |
| --- | --- | --- |
| Spacedock 0.27.2 | `context-sections` inlines named README sections into `dispatch show-stage-def` (probe: a `Dispatch facts` line printed under the implementation stage). `--scope-notes-file` carries FO text. `status --read --checklist` names report lines. No knob for the completion recipient; the parser and refusal are upstream (#523, #608, #625). | Use the first three; do not build around the last. |
| Claude Code 2.1.284 | `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_SKILL_DIR}` expand in a skill body (probe with a throwaway plugin; also seen in an installed skill inside this subagent). They do not expand in files read with `Read`. | The root line goes in each `SKILL.md`; linked files keep `<package>` bound by it. |
| kc-dev-flow-2 0.9.0 (`b753d344`) | No package-root binding; the report sentence in the three stage skills gives the form but not the FAILED rule; no secret text. `lint-skills.py` has `--root` and mutation tests in `test_lint_skills.py`. | Extend those two files; no new script. |
| Adopters | qnow owns the wrapper (`scripts/with-dev-secrets.sh`, its ADR 0027) and the user-level guard. carlove and subspace-relay: not searched for a guard; not needed for a package that ships none. | The wrapper is an adopter value. |

### PRFAQ

**Press release.** kc-dev-flow-2 workers now start knowing where the package scripts are, who to signal, what a stage report may not contain and how to reach a secret. A worker that implements a task runs `comment_ratio.py` from the exact install it loaded its skills from, sends one completion message that arrives, and writes a report Spacedock accepts on the first `status --set`.

**FAQ.**
- *Why does the skill state the root if the FO also types it into the dispatch, as issue #528 suggests?* A path the FO types can name a different install than the worker loaded (three exist here) and depends on the FO remembering; the skill's own root cannot disagree with the skill, so on disagreement the worker follows the skill's root. The FO's copy exists because of validation cycle 2: a worker composed its first batched command from the dispatch file, whose checklist named `comment_ratio.py` with no root, and ran `find /` before it could read the skill or `## Dispatch facts`. The skill's line is the authority; the FO's line reaches the worker earlier.
- *Why put the recipient in a section rather than a skill sentence?* It is a fact about the runtime, not about the package, and it must vanish when Spacedock fixes #523/#608; one section is one deletion. It reaches the worker at the top of its stage text, before the completion block.
- *Why not fix `FAILED: none` in the parser?* That is Spacedock's (#625 asks for it). The package rule costs one sentence and the test flips if Spacedock changes, telling us to delete the sentence.
- *Why not ship the guard?* A plugin hook fires in every session where the plugin is enabled, in repositories with no dev2 adoption, on machines that already carry the Captain's own copy (it would fire twice). Its patterns are stack-specific (Netlify, 1Password, Keychain), and a package-wide default would refuse text such as a commit message that mentions a guarded tool. Codex has no PreToolUse equivalent, so a hook is Claude-only anyway. What the package can own is the contract and the positive path: name one wrapper.
- *Does a worker really obey a bare sentence?* Not always: qnow had two leaks despite dispatch bans. That is why secrets rest on a hook plus a positive route, and why the FAILED and signal rules are graded by a real run (AC-6), not by text.

### Flow

```mermaid
flowchart TD
    A[FO dispatches a worker stage: ideation, implementation or validation, with Package root in the scope notes] --> B[Spacedock inlines stage text plus Dispatch facts section]
    B --> C[Worker loads its kc-dev-flow-2 skill]
    C --> D[Skill states Package root from CLAUDE_PLUGIN_ROOT]
    D --> E[Worker runs package scripts from that root]
    E --> F[Worker writes stage report: no FAILED bullet unless an item is unmet]
    F --> G[Worker sends completion once to the name its roster lists for the FO]
    G --> H[FO runs status set to leave the stage]
    H -->|accepted| I[Stage advances]
    H -->|refused| J[FO runs status read with stage and checklist]
    J -->|a line is not DONE or SKIPPED| K[FO returns that line to the worker to fix]
    K --> F
    J -->|all lines DONE or SKIPPED| L[Cause is evidence line, Summary or uncommitted report: FO returns that]
    L --> F
    E -.->|worker needs a development secret| M[Runs it as wrapper then command, never reads the value]
    M -.->|guard refuses a command that only mentions a reader| N[Worker rephrases, never splits or encodes the command]
    N -.-> M
```

### Where each rule lives

| Rule | Home | Enforcement point |
| --- | --- | --- |
| `Package root:` line, and "`<package>` in this skill and its linked files is this root; if the value above is not an absolute path it is two directories above this `SKILL.md`" | `skills/{ideation,implementation,validation,dev,learn,evaluate-learning}/SKILL.md` | `lint-skills.py` exit 1 (AC-1); reaches adopters with the package version |
| No bare script name, no `/absolute/plugin`, no `{package}` in `skills/**` and `references/**`; every script is `<package>/scripts/NAME.py` (or a `../../scripts/` link, or maintainer `kc-dev-flow-2/scripts/`) | same tree, `learn`, `evaluate-learning`, `dev` and `references/sd/adoption.md` rewritten to `<package>` | same lint |
| FAILED marks an item actually not met; a report with nothing failed has no FAILED bullet; never write a summary line as a bullet | one sentence in the report-form paragraph of the three stage skills | text plus AC-4 and AC-6 evidence; upstream #625 is the durable fix |
| FO recovery: on a refused `status --set`, run `status --read <task> --stage <stage> --checklist`, return the offending line to the worker, do not edit the report; FO resolves `<package>` from the `Package root:` of `kc-dev-flow-2:dev` | `references/sd/workflow.md` Stages preamble (FO reads the whole README) | FO instruction; AC-4 test proves the command names the line |
| Absolute `Package root:` in the scope notes of every worker dispatch; a script named in a checklist or scope note is `<package>/scripts/NAME.py` with that root substituted, never bare | `references/sd/workflow.md` Stages preamble, and the hand-off sentence in `skills/dev/SKILL.md` | FO instruction; AC-2 test proves scope notes reach the dispatch file, `lint-skills.py` rejects a bare name in the instruction text itself; AC-6 grades a worker on it |
| `## Dispatch facts` (Signal, Package, Secrets) | `references/sd/workflow.md`, added to `context-sections` of ideation, implementation and validation; `Secrets:` holds a `<wrapper>` value adoption resolves (qnow: `scripts/with-dev-secrets.sh`; none: "this project declares no wrapper; run no command that reads a secret value") | AC-2 test; adopters receive it by refit or three-way merge |
| Secret guard contract, no shipped hook | `references/sd/adoption.md` "Secret reads", about 12 lines | ADR 0003 records the boundary; not mechanically enforced |

Section text (final wording fixed at implementation, same meaning):
- `Signal:` send the completion message once, to the first officer by the name your session lists as addressable (`main` under Claude Code dispatch). The completion block's `team-lead` is Spacedock's default and is not registered there (spacedock-dev/spacedock #523, #608); do not try it first and do not describe a fallback in the report.
- `Package:` `<package>` in stage text is the `Package root:` line of the skill you loaded. Run package scripts only from it; never search the filesystem, `/tmp` or another install for them.
- `Secrets:` `<wrapper>` is the only route to a development secret: run a command that needs one as `<wrapper> <command>`. Never read or print a value. If a guard refuses a command that only mentions a secret-reading tool, rephrase it; do not split, encode or wrap the command to pass the guard.

### Failure modes

| Event | Result | Where it shows |
| --- | --- | --- |
| Skill loaded from a host that does not expand the root | Line shows a non-absolute value; fallback sentence gives the rule | Worker follows the sentence; Codex not probed (limit) |
| FO omits the root from the scope notes or writes a script bare in a checklist | A worker may search for the script before it reads the skill, as in validation cycle 2 | Dispatch file; the FO instruction in `workflow.md` is the only control, AC-6 graded it once |
| Worker ignores the recipient line and tries `team-lead` first | One failed call, as today; completion still arrives by task notification | Transcript; Spacedock #523/#608 own it |
| Worker writes `- FAILED: none` anyway | `--set` refused; FO's checklist command names the line | FO recovery step |
| Adopter has not resolved `<wrapper>` | Dispatch shows the literal placeholder | Adoption reference tells the adopter to resolve template values; a dispatch showing it is visible to the Captain at the gate |
| Guard blocks a command that only mentions a reader | Worker rephrases; cost one retry | Stated in `Secrets:`; message wording is the adopter's |
| Worker circumvents the guard by splitting or encoding | Not prevented by the package | Known limit; the sentence forbids it, nothing detects it |
| Adopter or user installs no guard | Bans alone, which failed twice at qnow | Known limit; ADR 0003 |
| Spacedock later fixes #523, #608 or #625 | AC-4's first assertion flips or the section line becomes redundant | Delete the rule; the test says so |

"Workers can always find the package scripts" holds only for workers that load a stage skill on a host that expands the root, or that follow the fallback sentence; the enforcement point is `lint-skills.py` for the text and AC-1(b) for the expansion.

### Evidence plan

Done at ideation, on real tools: the report refusal and its `--checklist` diagnosis (scratch workflow, Spacedock 0.27.2); the `context-sections` transport (scratch workflow); `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_SKILL_DIR}` expansion (throwaway plugin under `claude -p`); a plugin PreToolUse hook firing outside its project (same recipe); the guard false positive (this session). Not done: any candidate edit, lint mutation, Codex expansion, and the AC-6 run; those are validation's.

### ADR

Needed: yes. Ruling: secret-read enforcement is adopter- or user-owned; the package documents the contract, ships no hook, and dispatches name one run-time wrapper; facts only the package knows are stated by its skills, facts about the runtime and the adopter by one inlined section. It is a boundary later work must respect (someone will otherwise propose a shipped hook again), settled by this task's design, so `references/sd/workflow.md` § Decision records requires it before terminal approval, written by the implementation worker. Number: the dispatch says 0003 (migration-and-number-guards takes 0002); the implementation worker asserts nothing beyond what `reserve` gives once that task lands. The decider's words come from the Captain's ideation-gate reply.

### Unresolved decisions

1. **Captain (recommended default in place): document the secret guard, do not ship it.** Shipping means a `hooks/hooks.json` PreToolUse entry in the package: it protects adopters who did nothing, and it works only on Claude Code. Costs: it fires wherever the plugin is enabled, including non-dev2 repositories, and doubles the Captain's user-level guard here; stack-specific patterns would need per-adopter configuration the hook mechanism does not offer; a false positive refuses ordinary text in every project. Under the recommendation, an adopter who never reads `adoption.md` stays unprotected.
2. **Captain, only if wanted (outward-facing, not done).** A comment on spacedock-dev/spacedock #608 and #625 with the qnow counts and the two symbols (`completionSignalBlock`, `hasCompleteStageReport`), so the workarounds here can be deleted. Nothing in this design waits on it.
3. **Note, no decision.** `context-sections` edits touch the same frontmatter lines as the sibling task's (`Number guards`); whichever merges second rebases trivially. Adding `Dispatch facts` to the ideation entry also puts a line inside the block `poc_readme.py derive` removes, so the POC README needs no change.

### Captain acceptance script (after delivery; `PKG` is a checkout of the merged package, run from any directory)

1. `python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py; echo exit=$?` expect `PASS` and `exit=0`.
2. `cp -R $PKG/kc-dev-flow-2 /tmp/acc-kdf2 && printf '\nRun python3 comment_ratio.py a b\n' >> /tmp/acc-kdf2/skills/implementation/principles.md && python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py --root /tmp/acc-kdf2; echo exit=$?` expect a `FAIL:` line naming `principles.md` and `exit=1`.
3. `mkdir /tmp/acc-plug && cp -R $PKG/kc-dev-flow-2 /tmp/acc-plug/ && cd /tmp && claude -p --model haiku --plugin-dir /tmp/acc-plug/kc-dev-flow-2 --allowedTools Skill "Invoke the skill kc-dev-flow-2:implementation and print only its Package root line" < /dev/null` expect an absolute path under `/tmp/acc-plug/kc-dev-flow-2`; then `ls` that path plus `/scripts/comment_ratio.py` shows the file.
4. `python3 $PKG/kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root <active Spacedock plugin root>; echo exit=$?` expect `exit=0` (covers the three `show-stage-def` prints, the scope notes carrying the package root into the dispatch file, and the `FAILED: none` refusal).
5. Read the AC-6 receipt in the validation report: one scratch-workflow worker, its transcript excerpts for the first `SendMessage`, the script invocation and the report tail.

Does not cover: Codex, a real qnow dispatch, a real secret read, whether any adopter installs a guard. Exact strings are fixed at implementation; validation rewrites this script against the shipped text.

### Cost

No new script, no new CI step: `lint-skills.py`, `test_lint_skills.py` and `test_sd_dispatch.py` already run in `.github/workflows/kc-dev-flow-2-tests.yml`. CI minutes per PR: not measured. The AC-6 run is one Sonnet ensign on a trivial task: tokens not measured. Adopter cost: one refit or merge of `workflow.md` for the section and the FO paragraph.

## Number guards

ADR: 0003

## Stage Report: ideation

- DONE: Design, in the task file, the kc-dev-flow-2 package change for issues #526, #527, #528 and #530 — (1) dispatches address the dispatching FO by the name the runtime actually exposes
  `## Design` Ruling and `## Dispatch facts` Signal bullet: workers send once to the roster name (`main`); this session's roster lists `main`; builder pin is `completionSignalBlock`, upstream #523/#608 own the real fix.
- DONE: (2) every dispatch carries the absolute scripts directory of the installed package version and no stage definition names a script by bare name
  Root comes from each skill's `Package root:` line (`${CLAUDE_PLUGIN_ROOT}` expansion probed in a throwaway plugin and inside this subagent), not FO text; three installs found on this machine; lint rule AC-1 rejects bare names, `/absolute/plugin`, `{package}`.
- DONE: (3) the stage-report template rule that FAILED marks only an unmet item and never a summary line such as "FAILED: none", and whether the refusal can name the line
  Rule goes in the three stage skills; refusal cannot name the line (`hasCompleteStageReport` is one boolean, upstream #625) but `status --read --stage --checklist` does, reproduced by hand on Spacedock 0.27.2; FO recovery step and AC-4 test defined.
- DONE: (4) whether kc-dev-flow-2 ships a PreToolUse secret guard for adopters or documents it, and how dispatches name one run-time secret wrapper instead of listing forbidden commands, noting the guard's false positives
  Recommend document, not ship (plugin PreToolUse hook fires in unrelated projects, probed); `Secrets:` bullet names one `<wrapper>`; the guard's false positive reproduced live when this session's own read-only command was refused; Captain ruling 1.
- DONE: Check the chain first (spacedock's dispatch builder and ensign skill, kc-dev-flow-2, adopters) and report what exists
  Chain-check table: Spacedock builder/ensign/parser read at 0.27.0 cache with issues #523, #608, #625 open; `context-sections` transport probed; kc-dev-flow-2 0.9.0 and qnow read; carlove and subspace-relay not searched, stated.
- DONE: ACs with evidence plans
  AC-1..AC-6 each carry `Verified by:` with a falsifier and a limit; only the ideation-time probes are run, no candidate exists yet.
- DONE: Whether an ADR is needed (it would take 0003)
  Yes: secret enforcement is adopter-owned and the package ships no hook; number stated as 0003 per the dispatch, subject to the FO's reservation.
- DONE: The Captain-run minimal acceptance script
  Five steps in Design with expected exit codes and stated non-coverage; strings are rewritten by validation against shipped text.
- DONE: `design_surfaces.py check` passes and the Mermaid flow renders
  Output: `dispatch-and-report-hygiene.md: design surfaces presentable`; flow rendered to SVG with mermaid-cli (syntax only).

### Summary

The design moves the hand-typed dispatch facts into the package: a `Package root:` line in the stage skills (so scripts always come from the loaded install), the FAILED rule in the three stage skills, and one `## Dispatch facts` section inlined into every worker stage for the recipient, `<package>` meaning and the secret wrapper, plus an FO recovery step using `status --read --checklist`. One Captain ruling is asked: document the secret guard rather than ship it. Not verified yet: any candidate edit, Codex expansion, and the AC-6 real-worker run. The completion block said `team-lead`; I signal `main` as the FO instructed.

## Stage Report: implementation

- DONE: Implement dispatch-and-report-hygiene's approved design: every row of the design's "Where each rule lives" table, with the section text given there
  Candidate `c12de14252595a27060a9918870423957007038d` on `spacedock-ensign/dispatch-and-report-hygiene` (base `b753d344`, 3 commits, no version edits, files staged by name); the six rows: `Package root:` line in the six skills, script paths rewritten to `<package>` (learn, evaluate-learning, dev, adoption.md), FAILED rule in the three stage skills, FO recovery paragraph and `## Dispatch facts` (Signal, Package, Secrets) added to `context-sections` of ideation, implementation and validation in `references/sd/workflow.md`, "Secret reads" section in `references/sd/adoption.md`, no `hooks/` directory in the package.
- DONE: ADR 0003 in docs/adr (reserved by the FO; the decider's words are the Captain's 「准」 at the ideation gate on 2026-09-30)
  ADR added: `docs/adr/0003-secret-reads-are-enforced-by-the-adopter.md`; `adr_lint.py docs/adr --require 0003` prints "2 ADR file(s) checked, 0 legacy", exit 0.
- DONE: Every AC with the evidence its "Verified by" names that implementation can produce: AC-1(a), AC-2, AC-4, AC-5 text and no `hooks/` PreToolUse entry
  AC-1(a) and AC-2 and AC-4 by the runs below; AC-5 text is the `Secrets:` bullet in the AC-2 test plus adoption.md "Secret reads" with no machine-local path; `kc-dev-flow-2/hooks` does not exist at the candidate. AC-1(b) and AC-6 are validation's and were not run; AC-3 rests on AC-6.
  `test_lint_skills.py` (21 tests, OK): `test_bare_script_name`, `test_script_named_by_link_label_only`, `test_machine_path_placeholder`, `test_brace_placeholder` and `test_package_placeholder_without_root_line` each mutate a copy and expect their file named; `test_package_placeholder_without_root_line` is the falsifier (removing the `Package root:` line of `skills/implementation/SKILL.md` flips it); `test_cli_exits_one_naming_the_file` expects exit 1 and the path on stdout; `test_valid_scaffold` expects the unmodified tree to lint clean.
  `test_sd_dispatch.py --sd-plugin-root <SD 0.27.0 cache>` on Spacedock 0.27.2 (exit 0) asserts `show-stage-def` prints `## Dispatch facts` with `Signal`, `Package` and `Secrets` bullets for each stage on both hosts; removing `Dispatch facts` from the ideation `context-sections` fails on `AssertionError: ideation` (run after the assert was added).
  The same test writes a report ending `- FAILED: none.` with an evidence line: `status --set` exits non-zero with "durable, complete", `--read --stage implementation --checklist` prints `status=FAILED` and `text=none.`, and after removing the bullet `--set` exits 0.
  Adjusted `test_poc_readme.py` because the ideation entry now has a `context-sections` block (the slice assumed one attribute line); `derive` itself is unchanged and 4 tests pass. Other suites exit 0: `test_learning.py`, `test_design_surfaces.py`, `test_comment_ratio.py`, `test_adr_doc_checks.py`, `skill-frontmatter-lint.sh`.
- DONE: Follow this repo's CLAUDE.md: Conventional Commits, no version edits, stage files explicitly; comments carry only facts the code cannot state; comment_ratio.py and doc_impact.py reported; exact candidate SHA; the Captain-run minimal acceptance script rewritten against the shipped text
  `comment_ratio.py b753d344 HEAD`: code lines 71, comment lines 0, 0.0%. `doc_impact.py b753d344 HEAD` lists three documents: `kc-dev-flow-2/README.md` updated (lint and CLI-test paragraphs), `kc-dev-flow-2/references/sd/adoption.md` updated, `kc-dev-flow-2/skills/maintain-flow/SKILL.md` updated.
  Deviation from AC-2 as worded: the dispatch file written by `dispatch build` carries the `show-stage-def` fetch command, not the stage text, so the test asserts that command in the dispatch file and the facts in its output; the facts follow the stage text in that output, not precede it. Acceptance script is under its own heading below.

### Captain acceptance script (rewritten against candidate `c12de142`; `PKG` is a checkout of the merged package, run from any directory)

1. `python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py; echo exit=$?` prints `PASS: basic frontmatter, declared profile routes, role bindings and package script paths` and `exit=0`.
2. `cp -R $PKG/kc-dev-flow-2 /tmp/acc-kdf2 && printf '\nRun python3 comment_ratio.py a b\n' >> /tmp/acc-kdf2/skills/implementation/principles.md && python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py --root /tmp/acc-kdf2; echo exit=$?` prints `FAIL: skills/implementation/principles.md: script comment_ratio.py is named without <package>/scripts/` and `exit=1` (ran on the candidate).
3. `mkdir /tmp/acc-plug && cp -R $PKG/kc-dev-flow-2 /tmp/acc-plug/ && cd /tmp && claude -p --model haiku --plugin-dir /tmp/acc-plug/kc-dev-flow-2 --allowedTools Skill "Invoke the skill kc-dev-flow-2:implementation and print only its Package root line" < /dev/null` should print a line beginning `Package root: ` with an absolute path under `/tmp/acc-plug/kc-dev-flow-2`; `ls` of that path plus `/scripts/comment_ratio.py` shows the file (not run here; this is AC-1(b), validation's).
4. `python3 $PKG/kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root <active Spacedock plugin root>; echo exit=$?` prints a fourth line beginning `PASS: Dispatch facts (Signal, Package, Secrets) printed for each stage on both hosts` and `exit=0`.
5. Read the AC-6 receipt in the validation report: one scratch-workflow worker, its transcript excerpts for the first `SendMessage`, the script invocation and the report tail.

Does not cover: Codex, a real qnow dispatch, a real secret read, whether any adopter installs a guard.

### Summary

The package now states its own root in each skill that uses `<package>` (lint-enforced), carries the FAILED rule in the three stage skills, and ships `## Dispatch facts` through `context-sections`; the secret guard is documented in adoption.md and recorded in ADR 0003 with no hook. Not run: AC-1(b) and AC-6 (validation's) and Codex expansion. Known limit: a session that follows Spacedock's own "do not send completion to main" sentence over the Signal bullet still sees the old fallback.

## Stage Report: validation

- DONE: Independent verdict on candidate c12de14252595a27060a9918870423957007038d against the approved design and AC-1..AC-6 (recommend REJECTED on AC-6 only)
  Candidate SHA verified in the code worktree (`git rev-parse HEAD` = c12de142, `git status --short` empty before and after); five ACs and every static check below pass, AC-6 fails its "no `find` for a script" line (see Findings).
- DONE: Run the CI workflow's suite list on the candidate (a `git archive` copy under /tmp)
  `lint-skills.py` and `test_lint_skills.py` (21), `test_design_surfaces`, `test_adr_doc_checks`, `test_poc_readme`, `test_comment_ratio`, `test_learning`, `test_sd_dispatch.py --sd-plugin-root <SD 0.27.0 cache>` (spacedock 0.27.2) all exit 0; CI checks out the v0.27.2 plugin root, this run used the 0.27.0 cache root.
- DONE: AC-1(a) lint cases and the `Package root:` falsifier in a /tmp copy
  Mutated copies with bare `comment_ratio.py`, `/absolute/plugin/scripts/`, `{package}/scripts/` and a machine path each exit 1 naming `skills/implementation/principles.md`; deleting the `Package root:` line of `skills/implementation/SKILL.md` exits 1 with "uses <package> but has no 'Package root:' line"; the unmodified tree exits 0.
- DONE: AC-2 and AC-4 via test_sd_dispatch.py, and judge the stated AC-2 deviation
  Removing the ideation `context-sections` block makes the test fail with `AssertionError: ideation` (exit 1); the `FAILED: none.` report is refused ("durable, complete"), `--checklist` prints `status=FAILED` and `text=none.`, and `--set` exits 0 once the bullet is gone; deviation (dispatch file carries the fetch command, facts arrive in its output) is not material because the dispatch file itself shows that fetch command and `show-stage-def` prints the facts after the stage prose, so the design's "before the completion block" sentence is Polish.
- DONE: AC-1(b) `claude -p --plugin-dir` probe from a /tmp copy of the candidate package
  Printed `Package root: /tmp/val-plug/kc-dev-flow-2` (exit 0) and `/tmp/val-plug/kc-dev-flow-2/scripts/comment_ratio.py` exists; the implementation report's step-3 command line exits 1 ("Input must be provided") because `--allowedTools Skill "<prompt>"` swallows the prompt.
- FAILED: AC-6 real-worker run from a scratch workflow carrying the candidate workflow.md (one Sonnet ensign, spawned as a teammate)
  Not met on one line: the worker's first Bash call ended with `find /tmp/val-scratch/cand -name comment_ratio.py -not -path '*/node_modules/*' | head` (empty result, scratch dir only, run before it loaded the skill); the other three lines passed (details in Findings).
- DONE: Build the merge of the candidate with origin/main (b2024574) in /tmp and rerun the suites and show-stage-def
  Clean merge (no conflicts); all nine CI-list suites including `test_number_guards.py` exit 0, `adr_lint.py docs/adr --require 0002 0003` exit 0 (3 ADR files), `skill-frontmatter-lint.sh` exit 0; `show-stage-def` for implementation and validation each print `## Dispatch facts` (Signal, Package, Secrets) and `## Number guards`.
- DONE: Read ADR 0003 with adr_lint, every added comment line, adoption.md "Secret reads", hooks/ PreToolUse, comment_ratio.py and doc_impact.py, and the Captain acceptance script against the shipped text
  ADR 0003 quotes the Captain's 「准」 matching the ideation gate record; `git diff` adds no `#` comment lines in `scripts/*.py`; no machine-local path in adoption.md, the ADR, workflow.md or skills; no `hooks/` in the package and none in the diffstat; `comment_ratio.py b753d344 c12de142` = 71 code / 0 comment lines; `doc_impact.py` lists three documents, all marked `updated` in the implementation report; acceptance script step 3 was wrong as shipped and is corrected below.
- SKIPPED: If this session cannot spawn the AC-6 ensign as a teammate, report AC-6 as FAILED naming what blocked it
  The teammate spawn worked (Agent, `spacedock:ensign`, model sonnet, name `spacedock-ensign-ac6hello-implementation`), so this clause did not apply; AC-6 failed on its own criteria above.

### Findings and limits

- Confound, stated before the run: the worker loaded `kc-dev-flow-2:implementation` from this session's installed 0.9.0 (base `b753d344`), which has no `Package root:` line (grep count 0); the worker reported this and took the root from the skill's base directory. So this run grades Signal, the FAILED rule's absence and Dispatch-facts arrival only; Package-root resolution is graded by AC-1(b). The worker also could not see the candidate's FAILED-rule sentence, which lives in the skill. `<wrapper>` stayed literal in the scratch dispatch (the unresolved-template case in the design).
- AC-6 lines (transcript `agent-a2a2e8800d6cc915d.jsonl`): (1) one `SendMessage` in total: `to: main`, result `{"success":true,"message":"Message queued for the main conversation's next turn."}`; the FO confirms exactly one message arrived and none earlier: PASS. (2) `find /tmp/val-scratch/cand -name comment_ratio.py ...` in Bash call 1, same command that fetched the stage definition, so the facts had not been read: FAIL as worded, not a filesystem-wide search; no `mdfind`, no `ls -R`, and later runs used `<package>` from the skill's directory. (3) report has 0 `FAILED` bullets (commit c7a8ace in the scratch state): PASS. (4) `status --set ac6hello status=validation started` exit 0, `--checklist` shows three DONE: PASS.
- Classification (advisory): AC-6 is Needs decision. No candidate change would stop a worker from running a `find` in the same command that first fetches its stage text; a clean grading needs the candidate installed as the loaded plugin (Captain's call, outside this stage's /tmp-only scope) or a Captain ruling that the find, scoped to the scratch repo, is acceptable at N=1.
- Polish: the design sentence that the section "reaches the worker at the top of its stage text, before the completion block" is wrong; `show-stage-def` prints it after the stage prose and the dispatch file only carries the fetch command.
- Limits: Codex expansion not probed; N=1 worker; CI minutes and tokens not measured; validation ran against the 0.27.0 Spacedock plugin cache with the 0.27.2 binary, not the CI's v0.27.2 plugin root.

### Captain acceptance script (rewritten against the shipped text; `PKG` is a checkout of the merged package, run from any directory)

1. `python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py; echo exit=$?` prints `PASS: basic frontmatter, declared profile routes, role bindings and package script paths` and `exit=0` (ran).
2. `cp -R $PKG/kc-dev-flow-2 /tmp/acc-kdf2 && printf '\nRun python3 comment_ratio.py a b\n' >> /tmp/acc-kdf2/skills/implementation/principles.md && python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py --root /tmp/acc-kdf2; echo exit=$?` prints `FAIL: skills/implementation/principles.md: script comment_ratio.py is named without <package>/scripts/` and `exit=1` (ran).
3. `mkdir /tmp/acc-plug && cp -R $PKG/kc-dev-flow-2 /tmp/acc-plug/ && cd /tmp && claude -p "Invoke the skill kc-dev-flow-2:implementation and print only its Package root line" --model haiku --plugin-dir /tmp/acc-plug/kc-dev-flow-2 --allowedTools=Skill < /dev/null` prints `Package root: /tmp/acc-plug/kc-dev-flow-2`; `ls /tmp/acc-plug/kc-dev-flow-2/scripts/comment_ratio.py` shows the file (ran with the prompt first, and with `--allowedTools=Skill`).
4. `python3 $PKG/kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root <active Spacedock plugin root>; echo exit=$?` prints a fourth line beginning `PASS: Dispatch facts (Signal, Package, Secrets) printed for each stage on both hosts` and `exit=0` (ran).
5. Read the AC-6 receipt above: one send to `main` accepted, no `FAILED` bullet, `status --set` exit 0, and the one scratch-dir `find` that fails the criterion.

Does not cover: Codex, a real qnow dispatch, a real secret read, whether any adopter installs a guard, Package-root resolution by a dispatched worker.

### Summary

Recommend REJECTED, on AC-6 alone: the real worker sent one accepted completion to `main`, wrote a report with no FAILED bullet and got `status --set` accepted, but its first command included a `find` for `comment_ratio.py` (scratch dir only), which the design's pass rule forbids. AC-1(a), AC-1(b), AC-2, AC-4, AC-5, ADR 0003 and the merge with origin/main (clean, all suites exit 0) pass; the implementation report's acceptance script step 3 was wrong as shipped and is corrected here. The run also could not grade Package-root resolution because the loaded skill was the installed 0.9.0; the FO or Captain should decide between re-running with the candidate installed or accepting AC-6 with that limit.

## Stage Report: validation (cycle 2)

- DONE: Re-run AC-6 only on candidate c12de14252595a27060a9918870423957007038d with the candidate package as the only kc-dev-flow-2 the worker can load
  `git archive c12de142` snapshot at `/tmp/val2/snap`; headless `claude --setting-sources local --plugin-dir <snap>/kc-dev-flow-2 --plugin-dir <Spacedock 0.27.0 root>` with `DISABLE_PLUGIN_AUTOLOAD=1` run from `/tmp/val2/runtime` was the FO and built the dispatch (`dispatch build --stamp`) and spawned one Sonnet `spacedock:ensign` teammate; init lists exactly `kc-dev-flow-2` at the snapshot path and `spacedock`.
- DONE: Prove the loaded skill was the candidate (`Package root:` line naming the snapshot path)
  The worker's Skill call 7 (`kc-dev-flow-2:implementation`) returned "Base directory for this skill: /tmp/val2/snap/kc-dev-flow-2/skills/implementation ... Package root: /tmp/val2/snap/kc-dev-flow-2"; it then ran scripts as `python3 /tmp/val2/snap/kc-dev-flow-2/scripts/comment_ratio.py 312f5da HEAD` (exit 0) and `doc_impact.py`.
- FAILED: Pass only with no failed SendMessage, no `find`/`mdfind`/`ls -R` search for a script, no FAILED bullet in its report, and `status --set` accepting it
  Not met on one line: worker Bash call 6 ends with `find / -name comment_ratio.py -not -path '*/node_modules/*' 2>/dev/null | head`, a filesystem-wide search (about 66 s, 5.4 s to 71.9 s in the progress events) that printed ten paths; the other three lines passed (Findings).
- DONE: If the worker still searches before it reads the stage text, say at which call and what it had read by then
  Call 6 of 12, the same command that first fetched the stage text (`show-stage-def ...; cat <entity>; git status; git log; find / ...`); by then it had read only calls 3-5: the dispatch file, `ensign-shared-core.md` and `claude-ensign-runtime.md`; it had not read `## Dispatch facts` or loaded the skill (call 7).
- DONE: Report tokens and wall time of the run
  Wall time 99 s (start 1790744121, exit 1790744220); worker 30,160 tokens, 10 tool uses, 83 s (task_progress); FO session over its three turns: input 16, cache creation 10,976, cache read 117,183, output 1,213 tokens; `total_cost_usd` is imputed and not quoted.

### Findings and limits

- Excerpts: (1) `SendMessage {"to":"main", ...}` returned `{"success":true,"message":"Message queued for the main conversation's next turn."}` and the FO reported the completion message recipient as `main`; no earlier send: PASS. (2) the `find /` above, call 6: FAIL; no `mdfind` or `ls -R` anywhere in the 12 calls; after the skill load every script ran from `/tmp/val2/snap/kc-dev-flow-2`. (3) the report in the scratch state (commit d4bb784) has 3 DONE bullets and no `FAILED`: PASS. (4) the FO ran `status --set ac6hello status=validation` and printed `status: implementation -> validation`, exit 0: PASS.
- Trigger: the FO-authored checklist item in the dispatch file reads "run the package comment_ratio.py from the base commit to HEAD" (copied from the first run's checklist), which names the script with no root; the worker searched for it in the same batched command that fetched the Dispatch facts, so the section that says "never search the filesystem" could not have been read first. Same shape as the first run (scratch-dir `find` in call 1), wider scope this time.
- Classification (advisory): Needs decision. The candidate's text cannot precede a command the worker composes before reading it; whether the rule is met depends on the dispatch file, which the FO writes. Options for the FO or Captain: an FO-authored `--scope-notes-file` carrying the Package sentence (lands in the dispatch file the worker reads first; not tried here), a checklist that writes `<package>/scripts/...`, or accept N=2 as showing Dispatch facts do not preempt a batched first command.
- Limits: N=1 per run; user-level `~/.claude/CLAUDE.md` still loads in the headless session (`--bare` would drop it but also plugins and keychain auth); a permission allowlist (`Bash,Read,Write,Edit,Glob,Grep,Agent,SendMessage,Skill,ToolSearch`) was used instead of bypass; the Spacedock plugin root was the 0.27.0 cache with the 0.27.2 binary, as in the first run; `spacedock:first-officer` was not loaded in the headless FO, so its own completion-handling text was not in play.

### Captain acceptance script (AC-6 receipt, rewritten against this run)

5. Read the AC-6 receipt above: one send to `main` accepted, no `FAILED` bullet, `status --set` exit 0, and one `find /` for `comment_ratio.py` in the worker's first Bash call. Evidence: `/tmp/val2/logs/fo.jsonl` (stream-json, worker events carry `parent_tool_use_id`), scratch repo `/tmp/val2/scratch`.

### Summary

Recommend REJECTED on AC-6 only (the other results from the first run stand): with the candidate as the only loaded kc-dev-flow-2, the worker sent one accepted completion to `main`, resolved `<package>` from the skill's `Package root:` line, wrote a report with no FAILED bullet and got `status --set` accepted, but its first batched Bash call ran `find / -name comment_ratio.py`, before it had read the Dispatch facts. The gap is in what the worker reads before the stage text arrives, not in the candidate's text; the FO or Captain should choose between the dispatch-file options above and accepting the limit.

## Stage Report: implementation (cycle 2)

- DONE: Apply the Captain-authorized correction (FO scope notes carry the absolute package root; script references in checklists and scope notes are `<package>/scripts/NAME.py` with the root substituted) on top of candidate c12de14252595a27060a9918870423957007038d in the same worktree, keeping everything already shipped
  New candidate `a88175e9ed35ce7a62bd5e7caad3070f4d25e6c4` on `spacedock-ensign/dispatch-and-report-hygiene` (merge `079c2be4` of origin/main b2024574, then one fix commit; no version edits, files staged by name): FO instruction added to the `references/sd/workflow.md` Stages preamble, one hand-off sentence in `skills/dev/SKILL.md`, `Package:` bullet cross-references the scope notes; `git diff c12de142 079c2be4` is only the main merge, so nothing shipped was removed.
- DONE: Update the task's design text, ADR 0003, the test that can check the new FO instruction text, and the Captain acceptance script
  Design (Ruling, plain words, FAQ, "Where each rule lives" row, Flow node, Failure modes row), AC-2 and AC-6 "Verified by" and acceptance script step 4 edited in this file; ADR 0003 gains the correction words and rule, `adr_lint.py docs/adr --require 0002 0003` exit 0 (3 files); README test paragraph names the scope-notes check.
  `test_sd_dispatch.py` now builds each of the six stage/host dispatches with `--scope-notes-file` carrying `Package root: <root>` and `<root>/scripts/comment_ratio.py` and asserts both are in the dispatch file, the root line before the checklist text; replacing the notes file with `/dev/null` fails at `AssertionError: ('claude', 'ideation')` (ran, then restored).
  No new lint: the FO instruction text sits in `references/`, where `lint-skills.py` already rejects a bare script name, `{package}` and `/absolute/plugin`; whether an FO writes the notes has no mechanical check and is AC-6's.
- DONE: Merge origin/main (b2024574, migration-and-number-guards) into the branch and rerun the CI workflow's suite list on the result
  Clean merge, no conflicts (`context-sections` now list `Dispatch facts` and `Number guards` together); `lint-skills.py`, `test_lint_skills.py`, `test_design_surfaces`, `test_adr_doc_checks`, `test_poc_readme`, `test_comment_ratio`, `test_number_guards`, `test_learning` and `test_sd_dispatch.py --sd-plugin-root <SD 0.27.0 cache>` (spacedock 0.27.2) all exit 0; `skill-frontmatter-lint.sh` exit 0.
- DONE: Report the new candidate SHA, comment_ratio.py and doc_impact.py output from the base to the new head, and any AC whose "Verified by" text changes
  `/Users/kent/.claude/plugins/local/kc-dev-flow-2/scripts/comment_ratio.py b753d344 HEAD`: code lines 491, comment lines 1, 0.2% (the one comment line is `number_guards.py` line 1 from main, not this task); `comment_ratio.py origin/main HEAD` (this task's own diff): code lines 80, comment lines 0, 0.0%.
  `doc_impact.py b753d344 HEAD` lists `kc-dev-flow-2/README.md`, `references/sd/adoption.md`, `skills/maintain-flow/SKILL.md`: README `updated` (test paragraph names scope notes), adoption.md and maintain-flow `updated` in cycle 1 and unaffected by this fix.
  "Verified by" changed for AC-2 (adds the scope-notes transport assertion and its falsifier) and AC-6 (dispatch carries the root in scope notes and a checklist script written with the absolute root); AC-1, AC-3, AC-4 and AC-5 text is unchanged.

### Captain acceptance script (rewritten against candidate `a88175e9`; `PKG` is a checkout of the merged package, run from any directory)

1. `python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py; echo exit=$?` prints `PASS: basic frontmatter, declared profile routes, role bindings and package script paths` and `exit=0` (ran).
2. `cp -R $PKG/kc-dev-flow-2 /tmp/acc-kdf2 && printf '\nRun python3 comment_ratio.py a b\n' >> /tmp/acc-kdf2/skills/implementation/principles.md && python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py --root /tmp/acc-kdf2; echo exit=$?` prints `FAIL: skills/implementation/principles.md: script comment_ratio.py is named without <package>/scripts/` and `exit=1` (ran).
3. `mkdir /tmp/acc-plug && cp -R $PKG/kc-dev-flow-2 /tmp/acc-plug/ && cd /tmp && claude -p "Invoke the skill kc-dev-flow-2:implementation and print only its Package root line" --model haiku --plugin-dir /tmp/acc-plug/kc-dev-flow-2 --allowedTools=Skill < /dev/null` prints `Package root: /tmp/acc-plug/kc-dev-flow-2`; `ls /tmp/acc-plug/kc-dev-flow-2/scripts/comment_ratio.py` shows the file (ran).
4. `python3 $PKG/kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root <active Spacedock plugin root>; echo exit=$?` prints a fourth line beginning `PASS: Dispatch facts (Signal, Package, Secrets) printed for each stage on both hosts, scope notes with the package root carried into the dispatch file` and `exit=0` (ran).
5. Read the AC-6 receipt in the next validation report: one scratch-workflow worker dispatched with the root in its scope notes and the script written as an absolute path; its first Bash calls, the first `SendMessage`, the script invocation and the report tail. Not run here; it is validation's.

Does not cover: Codex, a real qnow dispatch, a real secret read, whether any adopter installs a guard, whether an FO follows the new instruction (only AC-6 grades it, at N=1).

### Summary

The FO instruction in `workflow.md` now has the FO write the skill's absolute `Package root:` into every worker dispatch's scope notes and write package scripts as `<package>/scripts/NAME.py` with that root substituted; `skills/dev/SKILL.md` hands the root to the FO, ADR 0003 records the rule, and `test_sd_dispatch.py` proves scope notes reach the dispatch file ahead of the checklist. Not proven: that a worker given such a dispatch skips the filesystem search (AC-6, validation's rerun) and that an FO follows the instruction; nothing else shipped changed.

## Stage Report: validation (cycle 3)
- DONE: Independent verdict on candidate a88175e9ed35ce7a62bd5e7caad3070f4d25e6c4 (merge of origin/main b2024574 plus the FO scope-notes correction); recommend PASSED
  Candidate SHA verified in the code worktree (`git rev-parse HEAD`, `git status --short` empty before and after); every check below passes, AC-6 included.
- DONE: Read `git diff c12de142 a88175e9` beyond the main merge
  `git diff 079c2be4 a88175e9` is 5 files (+33/-7): the `workflow.md` Stages-preamble instruction and `Package:` bullet, one `skills/dev/SKILL.md` sentence, ADR 0003, a README line and the `test_sd_dispatch.py` scope-notes assertion; nothing else, and `git diff c12de142 079c2be4` is only the main merge.
- DONE: Run the CI workflow's suite list on a `git archive` copy
  `lint-skills.py`, `test_lint_skills.py`, `test_design_surfaces`, `test_adr_doc_checks`, `test_poc_readme`, `test_comment_ratio`, `test_number_guards`, `test_learning`, `test_sd_dispatch.py --sd-plugin-root <SD 0.27.0 cache>` (spacedock 0.27.2) and `skill-frontmatter-lint.sh` all exit 0 in `/tmp/val3/snap`.
- DONE: Reproduce the new `test_sd_dispatch.py` scope-notes assertion and its `/dev/null` falsifier
  The unmodified test prints "PASS: Dispatch facts ... scope notes with the package root carried into the dispatch file" (fourth PASS line); changing `"--scope-notes-file", notes_path` to `/dev/null` in a /tmp copy fails at `assert f"Package root: {package_root}\n" in body` with `AssertionError: ('claude', 'ideation')`, exit 1.
- DONE: adr_lint on ADR 0003 and its new quote against the gate record
  `adr_lint.py docs/adr --require 0002 0003` exits 0 (3 ADR files); the ADR's second Words line quotes 「准」, Captain, 2026-09-30, and the gate record's `resolution.reason` reads 「准」 with the same date; the ADR's parenthetical gloss names only the package-root half, while its Decision paragraph carries both halves (scope-notes root and `<package>/scripts/NAME` in checklists).
- DONE: Every added comment line
  `git diff -U0 079c2be4 a88175e9` adds no `#` comment line (`comment_ratio.py 079c2be4 a88175e9`: 10 code, 0 comment); `comment_ratio.py origin/main a88175e9`: 80 code, 0 comment; `doc_impact.py origin/main a88175e9` lists README, adoption.md and maintain-flow, all marked `updated` in the implementation reports and unchanged in this diff except the README test line.
- DONE: Earlier results for AC-1, AC-3, AC-4 and AC-5 stand
  This diff touches only the `Package:` bullet wording of `## Dispatch facts` (Signal and Secrets bullets, the FAILED rule in the skills, adoption.md and the lint are unchanged), `show-stage-def` still prints the three bullets and `test_sd_dispatch.py` (AC-2, AC-4, AC-5) passes; `kc-dev-flow-2/hooks` does not exist; AC-3 is re-graded by the AC-6 run below.
- DONE: Re-run AC-6 with the cycle-2 isolation recipe; the headless FO loads `kc-dev-flow-2:dev`, reads the candidate README and builds the dispatch itself
  `git archive a88175e9` snapshot at `/tmp/val3/snap`; `DISABLE_PLUGIN_AUTOLOAD=1 claude --setting-sources local --plugin-dir <snap>/kc-dev-flow-2 --plugin-dir <Spacedock 0.27.0 root> -p` from `/tmp/val3/runtime` (init lists exactly those two plugins, model opus) was the FO; its prompt named the task, workflow dir and binary and said only "start it through the kc-dev-flow-2 entry, read the README, dispatch one worker the way that README says", never the scope-notes rule or the root; it called `Skill kc-dev-flow-2:dev`, read the scratch README, then `Skill spacedock:first-officer` with args ending "Package root: /tmp/val3/snap/kc-dev-flow-2", and built the dispatch (FO call 15) with `--scope-notes-file`.
- DONE: AC-6 pass condition: dispatch file carries `Package root:` naming the snapshot and the script as an absolute path
  The dispatch file the worker read (its call 1) has line 20 `Package root: /tmp/val3/snap/kc-dev-flow-2` before the checklist (line 26), and the scope line and checklist name `/tmp/val3/snap/kc-dev-flow-2/scripts/comment_ratio.py`, although the scratch task title says only "run comment_ratio.py from the base commit to HEAD"; the FO took the root from the skill's `Package root:` line and did not search.
- DONE: AC-6 pass condition: no search for a script in the worker's transcript
  The worker made 10 calls (dispatch file, two ensign references, show-stage-def batch, `Skill kc-dev-flow-2:implementation`, package references, the commit and script run, the report, ToolSearch, SendMessage); a scan of every worker `tool_use` for `find`, `mdfind`, `ls -R`, `locate`, `Glob` and `Grep` finds none, and it ran `python3 /tmp/val3/snap/kc-dev-flow-2/scripts/comment_ratio.py dd224ce HEAD` (exit 0, "code lines 0, comment lines 0, 0.0%") and `doc_impact.py` from the given root.
- DONE: AC-6 pass condition: one accepted SendMessage to main, no FAILED bullet, `status --set` accepting the report
  Worker call 10 `SendMessage {"to":"main", ...}` returned `{"success":true,"message":"Message queued for the main conversation's next turn."}` and was its only send (call 9 was ToolSearch loading the tool); the report (state commit 03afc83) has 3 DONE bullets and no `FAILED`, `--read --stage implementation --checklist` prints three `status=DONE`, and the FO's `status --set ac6hello status=validation` printed `status: implementation -> validation`, exit 0.
- DONE: Report tokens and wall time of the AC-6 run
  Wall time 81 s (`start` 1790751563, `end` 1790751644); worker 31,394 tokens, 10 tool uses, 24 s (`task_progress`); FO session over its three turns: input 40, cache creation 61,885, cache read 846,101, output 4,767 tokens; `total_cost_usd` is imputed and not quoted.
- DONE: Check the Captain acceptance script against the shipped text
  Steps 1 and 2 (`lint-skills.py` exit 0; appended bare `comment_ratio.py` gives `FAIL: skills/implementation/principles.md: script comment_ratio.py is named without <package>/scripts/`, exit 1), step 3 (haiku probe printed `Package root: /tmp/val3/acc-plug/kc-dev-flow-2`, inside a code fence; the script exists) and step 4 (fourth PASS line as written) ran against `/tmp/val3/snap`; step 5 is replaced below.

### Findings and limits

- No finding against the candidate. Polish only: ADR 0003's parenthetical gloss for the correction names the package-root half of the Captain's 「准」; the checklist half is in the Decision paragraph beside it.
- The two new `workflow.md` and ADR sentences ("Every worker dispatch FO builds carries ...", "never the bare script name") are instructions to the FO with no mechanical check; only AC-6 grades them, at N=1. `lint-skills.py` does reject a bare script name in `references/`, which covers the text, not the FO's behavior.
- The run cannot separate which of the two hand-offs the FO followed: the `dev` skill's sentence (the FO's `spacedock:first-officer` args carried the root) or the `workflow.md` preamble (its scope-notes file carries the root and its checklist writes the absolute script path); both are in the candidate.
- Limits: N=1 (Opus FO, Sonnet worker); Spacedock plugin root 0.27.0 cache with the 0.27.2 binary, not CI's v0.27.2 root; user-level `~/.claude/CLAUDE.md` still loads headless; a permission allowlist (`Bash,Read,Write,Edit,Glob,Grep,Agent,SendMessage,Skill,ToolSearch`) replaced bypass; Codex expansion not probed; CI minutes not measured; the `find` failure seen in cycles 1 and 2 was a batched first command written before the section was read, and this run's worker got the absolute path in the dispatch file it reads first, so it did not arise.

### Captain acceptance script (rewritten against candidate `a88175e9`; `PKG` is a checkout of the merged package, run from any directory)

1. `python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py; echo exit=$?` prints `PASS: basic frontmatter, declared profile routes, role bindings and package script paths` and `exit=0` (ran).
2. `cp -R $PKG/kc-dev-flow-2 /tmp/acc-kdf2 && printf '\nRun python3 comment_ratio.py a b\n' >> /tmp/acc-kdf2/skills/implementation/principles.md && python3 $PKG/kc-dev-flow-2/scripts/lint-skills.py --root /tmp/acc-kdf2; echo exit=$?` prints `FAIL: skills/implementation/principles.md: script comment_ratio.py is named without <package>/scripts/` and `exit=1` (ran).
3. `mkdir /tmp/acc-plug && cp -R $PKG/kc-dev-flow-2 /tmp/acc-plug/ && cd /tmp && claude -p "Invoke the skill kc-dev-flow-2:implementation and print only its Package root line" --model haiku --plugin-dir /tmp/acc-plug/kc-dev-flow-2 --allowedTools=Skill < /dev/null` prints `Package root: /tmp/acc-plug/kc-dev-flow-2` (possibly inside a code fence); `ls /tmp/acc-plug/kc-dev-flow-2/scripts/comment_ratio.py` shows the file (ran).
4. `python3 $PKG/kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root <active Spacedock plugin root>; echo exit=$?` prints a fourth line beginning `PASS: Dispatch facts (Signal, Package, Secrets) printed for each stage on both hosts, scope notes with the package root carried into the dispatch file` and `exit=0` (ran).
5. Read the AC-6 receipt above: the dispatch file's `Package root:` line and absolute script path, no `find`/`mdfind`/`ls -R`/`Glob`/`Grep` among the worker's 10 calls, one accepted send to `main`, no `FAILED` bullet, `status --set` exit 0. Evidence: `/tmp/val3/logs/fo.jsonl` (stream-json, worker events carry `parent_tool_use_id`), scratch repo `/tmp/val3/scratch`.

Does not cover: Codex, a real qnow dispatch, a real secret read, whether any adopter installs a guard, whether an FO other than this Opus session follows the new instruction.

### Summary

Recommend PASSED: every static check on a88175e9 passes (nine CI-list suites, adr_lint, the `/dev/null` falsifier, zero added comment lines), and the rerun of AC-6 with the candidate as the only loaded kc-dev-flow-2 shows the headless FO writing the snapshot's `Package root:` and an absolute script path into the dispatch file unprompted, after which the worker made no search, sent one accepted completion to `main`, wrote a report with no FAILED bullet and got `status --set` accepted. N=1; the old `find` failure did not recur, but one run cannot show it never will.
