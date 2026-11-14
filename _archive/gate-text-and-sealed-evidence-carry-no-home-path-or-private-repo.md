---
id:
title: Sealed evidence and the delivery gate's own text can be written without a home-directory path or a private repository name, so the state guard can refuse those two classes
status: done
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree: .worktrees/spacedock-ensign-gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo
pr: 872
gates:
    version: 1
    records:
        - id: gate:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo-backlog-1
              briefing:
                id: briefing:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:backlog:attempt-1:revision-1
                digest: sha256:033debd07b66ec73b2dbca7919aa0e3767696c9fd9a4fb1d623987970ee45479
                room-ref: ./gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:backlog:1
                briefing: briefing:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T09:52:32.02113Z"
                decision: approve
                reason: Inside scope 2 given by the reform session under the Captain's grant (message fa01bfc1); profile pilot justified in the Scope; seed check exit 0; admission involves no public merge, outward action, outcome-definition change or suspected key.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 item-3 from the reform session, Paseo message fa01bfc1-0e7d-4197-9636-a25f2818c562
              application:
                target-stage: ideation
                state: consumed
        - id: gate:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo-ideation-1
              briefing:
                id: briefing:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:ideation:attempt-1:revision-1
                digest: sha256:ada38ecbe7b84eb3b3fac33923eff2307eac2534c444ff85a55ae7e2da247b8f
                room-ref: ./gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:ideation:1
                briefing: briefing:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:ideation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T10:22:30.536549Z"
                decision: approve
                reason: Design check exit 0; the design corrects the task's premise with evidence and is three files with no overlap; the reform session confirmed it and ruled D2; D1 stays the Captain's; nothing is installed or flipped by this gate.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 item 3 from the reform session, Paseo messages fa01bfc1-0e7d-4197-9636-a25f2818c562 and 77b18f0b-34ca-4f2f-9607-d1ebcba63eca
              application:
                target-stage: implementation
                state: consumed
        - id: gate:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:validation
          stage: validation
          attempts:
            - id: gate-attempt:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo-validation-1
              briefing:
                id: briefing:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:validation:attempt-1:revision-1
                digest: sha256:264cdad6357db5bf7a1ebbffdd53de65cd3ca60e891ceae240f8866e69082eda
                room-ref: ./gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:validation:1
                briefing: briefing:gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T12:40:06.142684Z"
                decision: approve
                reason: 'Approves closing as stopped with verdict rejected, not delivery: the reform session ruled to stop the line inside the scope it gave under the Captain''s grant; no merge, no PR closed, no outward action beyond recording the finding in the Draft PR body.'
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 item 3 from the reform session, stop ruling in Paseo message 6bc7ea41-57b4-42cb-bcd9-9ba4398b8b1c
              application:
                target-stage: done
                state: consumed
started: 2026-11-14T09:53:13Z
verdict: REJECTED
completed: 2026-11-14T12:40:09Z
archived: 2026-11-14T12:40:09Z
---

The state guard merged in pull request 871 is installed with private task slugs and tailnet hostnames refusing, and private repository names, the email and the home directory only warning. Two of the warning classes cannot move to refuse today, because a refusal there has no legitimate way forward: a home path or a private repository name can sit inside sealed worker evidence, and the delivery gate's own form demands an absolute acceptance command in the gate summary and in the Captain-steps record.

## Scope

- Source: the reform session's ruling under the Captain's standing grant (Paseo 26215d96, message bc65ce97, 2026-11-14), after the Captain referred the guard decision to it with 「你問一下改革者」 (chat with the second dev2 FO, 2026-11-14): option (a) is installed now on the condition that this follow-up is filed. Held at backlog for admission in the reform session's next scope message.
- Bite: the observer's report on the archived task state-branch-writes-carry-no-private-identifiers (observer.md, 2026-11-14) observed absolute home-directory paths in that task's validation briefing summary and in its `captain-steps/1.md`, written by FO because `kc-dev-flow-2/scripts/delivery_gate.py steps` requires the exact acceptance command, which was absolute. The design of that task measured the home class in 75 of the last 200 state commits and the private-repo class in 11.
- Outcome: a redaction path for sealed evidence, and for gate-summary and Captain-steps text, with the delivery-gate form no longer demanding an absolute command; then the guard's private-repo and home classes are set to refuse on the live state checkouts.
- consumer: both First Officers writing gate text and Captain-steps records; workers sealing evidence; the Captain, whose words were 「出現就不準推」.
- Open for the design: what a refused commit's way forward is for each class (rewrite, relative path, a "not archived (private)" line); whether Spacedock's verbatim storage of gate summaries needs an upstream change or is covered by FO writing clean text; how existing records stay valid.
Non-goals: changing anything already on the branch or in its history; the email in commit metadata (the Captain's separate decision); patching Spacedock or filing anything upstream without the Captain.
Budget: 2 cycles per stage
Stop condition: a writer of these classes turns out to be Spacedock's own with no clean-text route for FO; existing records cannot stay valid; a suspected key is found; or the design needs a decision only the Captain can make.

## Acceptance criteria

**AC-1**: A gate summary and a Captain-steps record that pass the delivery-gate checks can be written with no home-directory prefix and no private repository name.
Verified by: a real delivery-gate question and steps check on a throwaway task whose committed bytes are scanned for the two classes, with commands and exit codes.

**AC-2**: Sealed evidence holding a private repository name has a recorded way forward that is not a bypass, and the result commits under the guard with that class at refuse.
Verified by: one real refused commit and one real accepted commit on a throwaway state checkout with private-repo and home at refuse.

**AC-3**: With both classes at refuse on a throwaway copy of the live state branch, a replay of the commits written after the change shows no refusal that lacks a way forward.
Verified by: the replay's per-commit result, counts by class. Limit: a replay of a bounded window, stated in the report.

**AC-4** (added by this design): A gzip evidence file whose only private name sits in its gzip header (file name, comment or extra field) is refused at commit with that class at refuse.
Verified by: one real refused commit of such a file on a throwaway state checkout, and a scan of every `.gz` blob at the live state tip showing that scanning raw bytes adds no hit absent from the decompressed content.

**AC-5** (added by this design): The validation stage's acceptance-script rule tells the validator to write a home path as `~/…`, as an unquoted word of its own, to name no private repository, and to pass paths to a retained script as arguments; a script written that way still runs from a fresh shell after `scratch.py` seals it.
Verified by: the candidate's `skills/validation/principles.md` text, and a throwaway run in which an argument-taking script, sealed by the candidate's `scratch.py`, exits 0 from a fresh `zsh -f` shell while a script holding a literal home path exits nonzero.

## FO alignment

Alignment: not needed before ideation: the outcome and its bite are stated by the reform session's ruling and the observer's report; the open design points return at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance with no release.

## Design

### PRFAQ

**Proposition.** From the release that carries this change, a validator's acceptance command writes a home path as `~/…`, so the Captain-steps record, the delivery question and the validation report that copy it verbatim carry no home-directory prefix and still pass the delivery-gate checks. Sealed evidence holding a private repository name is dropped from `evidence/` and replaced by the existing `Not archived (private): <what>; reproduce: <command>` line, with a placeholder where the command would name the repository. The guard also reads a gzip file's header, so a private name hidden there is refused. Then `private-repo` moves to refuse on the live state checkouts at that release, and `home` moves to refuse once four conditions hold (under `### Order`).

- **Did the delivery-gate form demand an absolute command?** No. `delivery_gate.py steps` and the `question` path (`inspect_steps`, byte-identical on main and at PR 869's head) accept `~/…` and task-relative paths. A `~/` record passed both and committed clean under the guard with `home` at refuse (`evidence/ideation-1/runs/ac1-probe.json`). The absolute form comes from the validation rule that the command "runs unchanged in a fresh shell". The steps check then copies the validator's command verbatim.
- **What about the gate summary that Spacedock stores verbatim?** Every home hit in the three briefings of the window sits in `artifacts[0].summary`, which FO writes (`runs/briefing-fields.txt`). Under PR 869's record route, FO "writes no factual summary": the summary is the `delivery-facts/v1` JSON, whose allowlist holds no path except `captain_steps.path` (`^captain-steps/[1-9][0-9]*\.md$`). The question text is still FO's own, and the guard refuses it at the state commit like any FO text. No upstream change is needed.
- **Why not redact private names automatically in `scratch.py`?** ADR 0079 already says private repository evidence is never archived. A file that names a private repository is that evidence, so the rule is to drop it, not keep it with the name masked. No sealed evidence in the window carried one.
- **Do existing records stay valid?** Yes. No record format changes and nothing on the branch is rewritten. Absolute paths still pass every check. The guard reads only added or changed blobs, and an archive move is a rename with no added bytes.
- **Why can `home` not refuse at this task's merge?** The installed 0.41.0 tools still write absolute `Package root:` lines into dispatch records. Their record check also refuses a `~/` root in a hand-saved message record. Both stay true until a release carrying PR 871 is synced to the workflow README in both sessions.

```mermaid
flowchart TD
  V[Validator] -->|acceptance command, home as ~/ and paths as arguments| R[validation Stage Report]
  V -->|scripts and logs| SC[scratch.py close: home rewritten as ~]
  SC --> EV[evidence/validation-N]
  R --> FO[First Officer]
  FO -->|Asked copied verbatim| CS[captain-steps/N.md]
  FO -->|question text| Q[gate question]
  CS --> ST{delivery_gate.py steps and question}
  Q --> ST
  ST -->|complete| PC
  EV --> PC{pre-commit guard; private-repo refuse, home refuse once the conditions hold}
  CS --> PC
  Q -->|stored by gate prepare, committed by state commit| PC
  PC -->|private name in text, a gz body or a gz header| RF[refused: file and class; change stays staged]
  RF -->|text: write ~ or a placeholder| PC
  RF -->|sealed private evidence: drop the file, add the Not archived line, close again| SC
  PC -->|clean| PP{pre-push guard}
  PP --> RM[origin spacedock-state/dev2]
```

### Before new work

- **This repository at origin/main c9b2c2400 (fetched 2026-11-14), with PR 869's nine files at a5657edd6 laid over it.** Main has changed since PR 869's base c2f035b66 only by PR 871's eight files. None of them overlaps PR 869's list. This design uses `state_guard.py`, `scratch.py`, `delivery_gate.py` and `dispatch_records.py` as they are, and changes only `state_guard.added_bytes` and one validation paragraph.
- **Spacedock 0.27.2.** `gate prepare` stores FO's `--question` and `--summary`. The briefing commits in the window are `state: update <slug>` commits, which run the hooks. No Spacedock writer outside FO text holds a home path in the window.
- **In-force ADRs.** These are all kept, and this design needs no new ADR:
  - ADR 0087: guard modes. Its gzip scan is extended to the header bytes, in line with "binary evidence is left to the guard, which scans its bytes".
  - ADR 0079: private evidence is never archived. It is the way forward for sealed evidence.
  - ADR 0054: `captain-steps/<N>.md` location.
  - ADR 0044 and ADR 0071: the legacy summary and the delivery check record.
  - PR 869's `references/delivery-record.md`: the record route.
- **Override lines.** I ran `git grep -n 'Override:'` on the state branch, filtered for path, home, private, guard, identifier, acceptance and redact. No line in this area matches.
- **Siblings.** Not read: adopters with private state branches are out of scope, and they keep the legacy text route under PR 869.

### Writers verified (main c9b2c2400; PR 869 a5657edd6)

| Writer | Where the class comes from | Demands an absolute or private form? |
|---|---|---|
| `skills/validation/principles.md`, acceptance paragraph (identical at both refs) | "an exact command or URL … FO runs it as written before the gate, so it runs unchanged in a fresh shell and names any checkout or install it needs" | In practice, yes: the one rule that leads to an absolute command. `~/` also runs unchanged in fresh bash and `zsh -f` (probe: exit 0 both). |
| `delivery_gate.inspect_steps` S1 and S5 | `Asked` must be in the question, validation report or linked cards, and every fenced command there must be in an `Asked` | No: it copies whatever form the validator wrote. A report with an absolute command forces an absolute `Asked` (probe `mixed`: `message S5: unrecorded command or link`). |
| `delivery_gate.absolute_paths` and `named_file` (S4) | `ABS_PATH` matches `~/` and `/`, then `expanduser()`; relative paths resolve against the task folder | No: `~/` passes S4 (probe `tilde`). |
| `delivery_gate.captain_step_problems` | `Captain steps:` resolved by `named_file` | No: `captain-steps/1.md` is the contract's own example (`delivery-record.md`, PR 869). |
| `workflow.md` Captain steps ("FO runs each step as written") and FO's `Observed:` paths | FO text | No: `Observed:` needs only non-empty text, so `captain-steps/1-output.log` serves. |
| `workflow.md` "carries that absolute path as a `Package root: <absolute path>` line" | Scope notes and hand-saved `-message-N.md` records | Yes for scope notes, which `dispatch_stage` rewrites since PR 871. For a hand-saved message record, `dispatch_records.PARTS` on main accepts `~/`, and the 0.41.0 copy does not. |
| `scratch.evidence` (main) | Rewrites home in new or changed text before sealing | Breaks scripts: all 18 home sites in the window's sealed `.sh`/`.py` files sit inside quotes or after `=`, where `~` does not expand (`runs/quoted-scripts.txt`). A sealed script holding a literal path exited 1 and an argument-taking one exited 0 (`runs/sealed-script.json`). |
| `state_guard.added_bytes` (main) | Decompresses gzip and scans the content only | Misses a private name held only in a gzip header: such a commit was accepted (`runs/ac2-probe.json`). This is the Codex P2 that FO declined on PR 871, and its trigger, "before any class is set to refuse on the live clone", was already met at install by `private-slug` and `tailnet-host`. |
| FO scope notes (`dispatch/*.md`) | FO text | The only `private-repo` hit in 200 commits, 157 commits before the state tip. |

No writer of either class is Spacedock's own: every remaining hit is text FO or a worker writes.

### Mechanism

**M1. Validation acceptance commands write home as `~/`.** One added sentence after "names any checkout or install it needs." in `skills/validation/principles.md`: "It writes a path under the home directory as `~/…`, an unquoted word of its own, and names no private repository; a retained script takes its paths as arguments rather than holding them, because sealing rewrites the home directory inside it." That is 43 words. The file sits outside the workflow word budget, which `lint-skills.py` `budget_errors` counts on `references/sd/workflow.md` only. `Asked`, the question and the report then all carry `~/`, so S1, S5 and S4 pass as they are.

**M2. The guard reads gzip headers.** In `state_guard.added_bytes`, a gzip blob returns its raw bytes as well as its decompressed content. The header's name, comment and extra field are stored uncompressed, so this covers every member of a multi-member file. Measured on all 110 `.gz` blobs at the live state tip: 92 carry a header name or comment, and the raw scan adds 0 hits absent from the decompressed content (`runs/gz-raw-scan.txt`). Limit: a broad `re:` entry in the owner's list could match random compressed bytes, a false refusal that the refusal message makes visible.

**M3. Sealed private evidence: the way forward, no new code.** On refusal, the worker drops the file from `evidence/<record>/` and writes `Not archived (private): <what>; reproduce: <command>`, with a placeholder such as `<adopter checkout>` where the command would name the repository. The worker then reruns `scratch.py close`, which rebuilds `SHA256SUMS` from the files present, and commits again. All of this was probed: refused, then accepted, and the matched text was never printed. Two limits:
- Editing a name out of an already sealed `.gz` makes `scratch.py` refuse with `evidence digest differs`. Dropping the `.gz`, or replacing it with the redacted plain file, re-seals cleanly (probed).
- A reproduce line that keeps the private name is refused (probed).

**M4. Text classes: the way forward is to rewrite.** This covers FO's question, Captain-steps record, message records and scope notes, and workers' reports and unsealed task-folder files. Writing the path as `~` removes every home hit in the window: 188 of 188 file changes were clean after `rewrite_home` (`runs/residual-200.txt`). A private name is replaced with a placeholder. The guard's refusal line on main already says both.

### Order

1. **This task's PR**, cut from main after PR 869 merges or the Captain holds it. M1 and M2 ship with their tests. Nothing is installed by the release.
2. **`private-repo` to refuse:** once the release carrying this change is synced to the workflow README, FO reinstalls the guard with `--refuse private-repo,private-slug,tailnet-host` on each live state checkout. `check` reports the old copy as `stale` until then.
3. **`home` to refuse**, when all four conditions hold:
   - (a) A release carrying PR 871 is synced to the README in both sessions (the `package_version.py` hold enforces this).
   - (b) Step 2's release, with M1, is synced the same way.
   - (c) No task between its validation report and its delivery gate holds a home path in that report. FO checks with a count-only scan; otherwise the `mixed` case stalls its Captain-steps record.
   - (d) A replay of the commits made after (a) shows no home hit from a dispatch or evidence writer.
4. **`email` (content)** stays at warn. The email in commit metadata stays the Captain's separate decision (Non-goal).

What cannot flip at this task's merge: `home`, because conditions (a) to (d) wait on releases and on in-flight tasks. `private-repo` waits only for the release that carries M2.

### Files this design changes

- `kc-dev-flow-2/scripts/state_guard.py` (M2, `added_bytes`): not in PR 869's list.
- `kc-dev-flow-2/scripts/test_state_guard.py` (M2: a header-only name is refused, and a clean gzip is accepted): not in PR 869's list.
- `kc-dev-flow-2/skills/validation/principles.md` (M1, one sentence): not in PR 869's list.

No change to `references/sd/workflow.md`, `delivery_gate.py`, `scratch.py`, `dispatch_records.py`, `dispatch_stage.py` or any other file in PR 869's list. The workflow text and its word budget are unchanged, and no ADR is added.

### Worth questions

- **M1.** Serves 「出現就不準推」 and the scope's "delivery-gate form no longer demanding an absolute command". Without it, two things break: the first validation after PR 871's release seals scripts whose literal home paths become quoted `~`, which fails FO's run (probed: exit 1), and `home` cannot refuse without stalling every Captain-steps record. Premise that makes it unneeded: validators already pass paths as arguments. Cheap test, run: 11 `.sh`/`.py` files added in the window hold literal home paths, and 18 of 18 sites would be quoted.
- **M2.** Serves the same words. Without it, a header-only name passes at refuse (probed). Premise: no gzip header carries a listed name. Checked: 0 do today, but 92 of 110 carry a name field, so the hole is live for any future file name.
- **M3 and M4.** Serve the same words. They need no code. Premise that would make this task unneeded: the guard's refusal line alone is enough. That premise held for text and failed for the two cases M1 and M2 cover.
- No part serves no Captain words.

### Replay evidence

Evidence paths in this design are under `evidence/ideation-1/`.

`runs/replay-200.txt` replays the last 200 commits of `spacedock-state/dev2`, from 43893a5e9 to 50f66677c (2026-11-14), through main's guard with the live list. It records counts and path kinds only:

| Class | Commits | Where | Fixed by |
|---|---|---|---|
| home | 67 | message records 26, dispatch records 24, evidence 12, task-file reports 5, briefings 3, Captain steps 3, other task-folder files 2 | dispatch records and evidence: the release carrying PR 871; everything else: FO or the worker writing `~`, with residual 0 of 188 |
| private-repo | 1 | FO scope notes in a dispatch record | FO rewrites; 0 in the last 157 commits |
| email | 1 | evidence (a pasted log) | out of scope |
| private-slug, tailnet-host | 0 | | already refuse |

### Acceptance status now

- **AC-1:** probed at the overlay (main plus PR 869) on a throwaway with a scratch HOME, every class but email at refuse (`runs/ac1-probe.json`).
  - `tilde`: steps CLI exit 0; question path with the report has no problems; bash and zsh fresh shells exit 0; commit exit 0; 0 home bytes at HEAD.
  - `absolute`: checks pass, but the commit is refused on the task file, the Captain-steps record and the stored question.
  - `mixed`: S5 fails.
  - Not provable now: the candidate, and a real `question` run with dispatched candidates and `gate prepare`.
- **AC-2:** probed with main's `scratch.evidence` (`runs/ac2-probe.json`). A sealed private name is refused at commit and the name is not printed. After the drop, the Not archived line and a re-seal, the commit is accepted. Not provable now: on the candidate (unchanged code, same route).
- **AC-3:** a counterfactual over the window. Every hit has a way forward once the four conditions in `### Order` hold (`runs/replay-200.txt`, `runs/residual-200.txt`). Not provable now: a replay of commits written after the change.
- **AC-4:** before the fix, a header-only name is accepted (`runs/ac2-probe.json`, `gzip header name only`, exit 0); the false-hit scan shows 0 (`runs/gz-raw-scan.txt`). Not provable now: the candidate's refusal.
- **AC-5:** before the fix, the literal-path script exits 1 after sealing and the argument script exits 0 (`runs/sealed-script.json`). Not provable now: the candidate's text.

### Decisions for the Captain

- **D1. Release order.** Release PR 865 (kc-dev-flow-2 0.42.0, open) carries PR 871. Merging it before M1 lands means each validation whose acceptance script holds a literal home path fails FO's run after sealing. Recommend: merge 865 now anyway, and add an FO scope-notes line to each validation dispatch telling the worker to pass paths as arguments, until M1 ships. What gets worse: it is one more line in each validation dispatch for a release or two. The alternative, holding 865 for this task, delays PR 871's record rewrite, which removes 24 of the 67 home commits.
- **D2. Who flips.** Recommend that FO runs steps 2 and 3 of `### Order` under the reform session's ruling (option (a) "on the condition that this follow-up is filed"), reporting each reinstall's `check` line. What gets worse: a mis-timed `home` flip stops in-flight dispatches until FO reinstalls at warn.

### Batch overlap

- PR 869 (open, the other FO): no shared file.
- `validation-reads-pr-review-comments` (implementation) and `comment-check-reaches-delivery-gate` (ideation) both change `skills/validation/principles.md`, in other paragraphs: a textual overlap only.
- `adoption-asks-which-extensions`, `design-director-runs-where-it-pays` and `ideation-checks-external-prior-art` only name that file.
- No live task names `state_guard.py` or `test_state_guard.py`.
- No shared numbered record: this design adds no ADR.

Recommended order: after PR 869 merges and after `validation-reads-pr-review-comments` merges (the same file).

## Stage Report: ideation

- DONE: The writers verified against the code: where a gate summary, a Captain-steps record and sealed evidence get a home-directory path or a private repository name today, read at the head of open pull request 869 (a5657edd6) and not only at main, because that pull request reshapes the steps and question checks and moves their forms into a contract document; say which lines demand an absolute command
  `### Writers verified (main c9b2c2400; PR 869 a5657edd6)`: `inspect_steps` is byte-identical at both refs and accepts `~/` (probe `tilde`, steps exit 0). The absolute form comes from the validation acceptance paragraph ("runs unchanged in a fresh shell"), copied verbatim by S1 and S5, and from workflow.md's `Package root: <absolute path>`. Briefing home hits are FO's `summary` only (`runs/briefing-fields.txt`). PR 869's record route leaves no FO summary. No writer is Spacedock's own.
- DONE: A design that lets a gate summary and a Captain-steps record pass the delivery-gate checks with no home-directory prefix and no private repository name, gives sealed evidence holding a private repository name a way forward that is not a bypass, keeps existing records valid, names every file it changes and whether the workflow text or its word budget changes, and says by a replay of recent state commits which guard classes could really be set to refuse after it and which still could not, and why
  `### Mechanism`: M1, one validation sentence; M2, the guard reads raw gzip bytes; M3, the ADR 0079 drop-and-record route; M4, rewrite. `### Files this design changes`: three files, none in PR 869's list; workflow text, word budget and ADRs unchanged. `### Order` and `### Replay evidence` (200 commits): `private-repo` can refuse at this task's release; `home` cannot refuse until conditions (a) to (d) hold.
- DONE: Each acceptance criterion with its proof run once now where it can be or listed under `Not provable now` with the reason; the decisions only the Captain can make named; kc-dev-flow-2/scripts/design_surfaces.py check on the task exits 0
  AC-1: probed at main plus PR 869 on a throwaway with every class but email at refuse (`runs/ac1-probe.json`). `tilde`: steps 0, question path clean, fresh bash and zsh 0, commit 0. `absolute`: commit refused on three files. `mixed`: S5 fails. Not provable now: the candidate, and a real `question` run plus `gate prepare` with dispatched candidates.
  AC-2: refused at commit with the name not printed; accepted after drop, Not archived line and re-seal; a reproduce line naming the repository is refused (`runs/ac2-probe.json`). Not provable now: on the candidate.
  AC-3: counterfactual replay of 200 commits; residual 0 of 188 after writing `~` (`runs/replay-200.txt`, `runs/residual-200.txt`). Not provable now: commits written after the change do not exist yet.
  AC-4: a header-only name is accepted today (exit 0); scanning raw bytes adds 0 hits over 110 live `.gz` blobs (`runs/gz-raw-scan.txt`). Not provable now: the candidate's refusal.
  AC-5: after sealing, the literal-path script exits 1 and the argument script exits 0 (`runs/sealed-script.json`). Not provable now: the candidate's text.
  Captain: D1 (release PR 865 order) and D2 (who flips). `design_surfaces.py check` exit 0 (`runs/design-surfaces.txt`). Evidence scanned with the live list: 0 files hit (`runs/evidence-scan.txt`).

### Stop conditions and points for FO

- One stop condition is touched: the design needs Captain decisions D1 and D2. FO decides whether the standing grant covers them. The other stop conditions are not touched: no writer is Spacedock's own, existing records stay valid, and no suspected key was found.
- The Codex P2 that FO declined on PR 871 had the trigger "before any class is set to refuse on the live clone". That trigger was already met when the guard was installed with `private-slug` and `tailnet-host` at refuse, so the gzip-header gap is live today. M2 closes it.
- Release PR 865 ships PR 871's evidence rewrite. All 18 home sites in the window's scripts would become a quoted `~` that does not expand (`runs/quoted-scripts.txt`). Until M1 ships, validation dispatches need a scope-notes line telling the worker to pass paths as arguments (D1).
- Evidence scripts use invented names only, and the probes ran against an invented list with a scratch HOME. The live list was used only for count-only scans.

### Scratch close

```
Scratch removed: /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/ideation-1 (9115092 bytes)
Evidence: evidence/ideation-1/ (20 files, 25.4 KiB)
```

### Summary

The delivery-gate checks never demanded an absolute path: they accept `~/`. The absolute form came from the validation acceptance rule and the steps check's verbatim copying, and PR 869's record route removes FO's gate summary. The design adds one validation sentence and makes the guard read gzip headers (three files, no workflow text, no ADR); sealed private evidence uses ADR 0079's existing route. A 200-commit replay shows `private-repo` can refuse at this task's release, while `home` waits on the releases carrying PR 871 and this change, plus a clean in-flight check; the release order and who flips are Captain decisions D1 and D2.

## Stage Report: implementation

- DONE: One candidate on the assigned branch off origin/main, implementing only the three approved files; no versions, ADRs, live installations or guard modes changed.
  Branch `spacedock-ensign/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo`; base `c9b2c240078238b66c98179c4ddc686eac0e3918`; candidate `d8ce3421219a8ff6112628de7cbf5f46274c634a`; clean product worktree in `evidence/implementation-1/runs/artifact.json`.
- DONE: AC-1 — gate summary and Captain-steps record pass without a home prefix or private repository name.
  `runs/probe.json` and `runs/probe-commands.json`: real steps, question, Spacedock 0.27.2 gate prepare and guarded commit/push exit 0; committed blobs have zero home/private-repo hits; fresh bash/zsh exit 0; absolute-home mutation is refused (1), mixed command forms fail S5 (1).
- DONE: AC-2 — sealed private evidence has a guarded way forward.
  `runs/probe.json`: sealed private evidence and a reproduce line retaining its name each refuse (1); dropping the file, recording a placeholder and re-sealing commits/pushes (0), removes its manifest entry and prints no matched name.
- DONE: AC-3 — bounded post-candidate state replay has no refusal without a way forward.
  `runs/replay.json`: c59f13d255f7bed028e68e7ba3b04a1bb0c9295e..180ee2461a0af267e545467c71fc0e195aaee961, one commit, zero hits in each class, guard exit 0; `runs/replay_only_tip.log` fails (1) when a mutation skips transient earlier commits. This window contains this task's evidence commit, not a subsequent dispatch or live rollout.
- DONE: AC-4 — gzip header-only identifiers refuse and clean gzip commits.
  `runs/guard-tests-candidate.log` and `runs/probe.json`: filename/comment/extra fields refuse, including concatenated and nested gzip; clean gzip commits/pushes. `runs/replay.json`: all 110 gzip blobs at the pinned state tip scanned, 92 named/commented headers, zero raw-only class hits.
- DONE: AC-5 — the approved acceptance-rule sentence and sealed argument-taking script work.
  `runs/mutations.json`: candidate sentence check 0, removed-sentence mutation 1; `runs/probe.json`: candidate scratch sealing followed by fresh zsh gives argument script 0, literal-home script 1.
- DONE: Every acceptance criterion has candidate evidence and its falsifier exercised with Python -B and fresh mutation directories.
  `runs/header-before.log` has nine pre-fix failures; `runs/discard_headers.log` and `runs/discard_inner_headers.log` fail on their mutations. An initial post-fix test fixture reused byte-identical clean content and hit empty commits (`runs/guard-tests.log`); distinct clean bytes corrected it, and the committed candidate's 14 tests pass (`runs/guard-tests-candidate.log`).
- DONE: The repository's complete CI Python list and the required lint/ADR/number/comment checks pass.
  `runs/ci.json`, `runs/ci.xml`: all 29 listed entries pass locally with Spacedock 0.27.2 and plugin root 4d158a484ec73e184861067f8ed1e20087fdc26a; `runs/lint.log`, `runs/adr-lint.log`, `runs/number-guards.log` exit 0; `runs/comment-ratio.log`: 20 code lines, zero comment lines, 0% within 5%. CI cost per PR not measured; no CI file changed.
- DONE: Existing sources, ownership and retained-document impact checked within approved scope.
  FO's post-design ruling (message b80281f6) authorizes current main without waiting for PR 869, superseding that design-order line for these three files; AC-1 uses main's current question route. `runs/doc-impact.log`: ADR 0087 unaffected because its raw-byte/decompression and opt-in boundaries remain; ADR 0079's private-evidence route and ADR 0054's steps rule remain. No new decision record.
- DONE: PR title/body and release conditions prepared for FO.
  `implementation/pr.md` says home stays at warn and lists all four flip conditions, with condition (a)'s release already going out under the Captain's ruling; private-repo waits for this release's README sync and FO reinstall. PR 869's later record route removes FO's handwritten summary. Broad owner regexes can match compressed bytes, the design's stated limit.
- SKIPPED: Product push, Draft PR creation, RoboRev and hosted CI.
  Not run by the worker; FO owns all four. No PR opened: no push grant.
- SKIPPED: Final state commit and sync by this worker.
  The real state commit failed creating the shared index.lock (Operation not permitted); no git-add fallback. FO committed/pushed the initial evidence as 180ee2461a0af267e545467c71fc0e195aaee961 through the live guard with no warning/refusal; final report, PR text and evidence updates await FO's path-scoped commit/sync.
- DONE: Public evidence retained and dispatch scratch closed.
  `runs/evidence-scan.json`: no live-list class hits before sealing; all cited run outputs are under `evidence/implementation-1/` (large files use gzip). The pinned package's required close command exited 0; exact output follows.

### Scratch close

```text
Scratch removed: /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/implementation-1 (975814397 bytes)
Evidence: evidence/implementation-1/ (67 files, 158.9 KiB)
```

### Summary

The candidate scans raw bytes at every gzip layer and adds the one approved validation sentence, with all five criteria exercised on throwaway checkouts and all 29 CI-listed entries passing locally. Implementation is complete; FO retains final state commit/sync, product publication, Draft PR, RoboRev and hosted CI, and the one-commit replay does not satisfy the later live-home-flip conditions.


## Stage Report: validation

- DONE: Independent verdict at PR 872 against the admitted pilot outcome and approved design: REJECTED; F1 below fails AC-4. Product bytes remain unchanged.
  Branch `spacedock-ensign/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo`; base `c9b2c240078238b66c98179c4ddc686eac0e3918`; candidate `d8ce3421219a8ff6112628de7cbf5f46274c634a`; exactly the approved three files and a clean product tree (`evidence/validation-1/runs/artifact.json`). Existing prepared PR text remains `implementation/pr.md`.
- DONE: AC-1 — real delivery-gate steps and question checks, gate preparation, guarded commit and push on an invented linked state checkout with its own remote.
  All exit 0, committed home/private-repo counts are 0, and fresh bash/zsh run the clean command; the absolute-home counterexample refuses and mixed forms fail S5 (`evidence/validation-1/runs/probe.json`, `probe-commands.json`). This uses main's current route, as the reform ruling requires.
- DONE: AC-2 — sealed private evidence is refused, then accepted through the recorded drop-and-reproduce route without bypassing the guard.
  Private evidence and a reproduction line retaining its invented name each refuse (1); dropping it, using a placeholder and resealing commits/pushes (0), removes the stale manifest entry and prints no matched name (`evidence/validation-1/runs/probe.json`).
- DONE: AC-3 — independently replayed every commit in the bounded post-candidate interval with home/private-repo at refuse on an owned copy and remote.
  `c59f13d255f7bed028e68e7ba3b04a1bb0c9295e..52533375e5ec8e5ba41041580138f584ec26a907`: 9 commits, home 1, every other class 0, no unhandled refusal; the home change is clear after rewriting to `~` (`evidence/validation-1/runs/replay-replay-only.json`, `replay-replay-only-commands.json`). This is not a live-home-flip proof; the old writer still emits home once.
- DONE: AC-4 attack assessment — REJECTED by the combined-member counterexample; ordinary header cases and diagnostic privacy hold.
  14 invented cases: clean gzip/binary commit and push; name/comment/extra, combined fields, header CRC, concatenated members, simple nesting, damaged trailer/deflate and a 2 MiB header refuse; two nested-second-member variants commit and push with exit 0; matched-text output count is 0 (`evidence/validation-1/runs/gzip-probe.json`, `gzip-commands.json`).
- DONE: Raw-byte false-positive scan and this task's existing sealed-evidence scan, with explicit class limits.
  All 110 gzip blobs and 89 task evidence files at the pinned state tip were evaluated; home/private-repo have 0 raw-only hits, and own evidence has 0 observed hits. Existing gzip home/private-repo hits are 40/6 and already in decoded content. Tailnet-host remains unverified on 11 files after a per-search limit; do not read its displayed 0 raw-only count as a complete pass (`evidence/validation-1/runs/corpus-final.json`). Earlier stopped attempts are retained in `scan-attempts.json` and are not acceptance evidence.
- DONE: AC-5 — the candidate's acceptance-rule sentence is present and its candidate scratch sealer preserves the argument-taking route.
  After sealing, fresh zsh runs the argument script (0), while the literal-home script fails (1); the retained acceptance command also runs from a fresh shell and reproduces F1 (`evidence/validation-1/runs/probe.json`, `retained-acceptance.log`).
- DONE: Read every current PR conversation comment, review and inline review comment, and verify hosted CI against this candidate.
  PR remains open/Draft at the dispatched head; all three comment/review counts are 0. Five hosted checks succeeded and docs deployment was skipped; the Python job's 29 listed checks succeeded at this head (`evidence/validation-1/runs/pr-final.json`, `review-comments-final.json`, `ci.json`). Local state-guard tests independently passed 14 tests (`guard-tests.log`); the full green CI suite was not repeated locally.
- DONE: Required ADR, retained-document, added-comment, design and dispatch checks, and candidate lint.
  Installed 0.41.0 `adr_lint.py docs/adr --since c9b2c240078238b66c98179c4ddc686eac0e3918` exits 0; role, doc-impact, comment, design, dispatch-record and candidate lint checks all exit 0 (`evidence/validation-1/runs/checks.json` and its named logs). Added comments: 0 of 20 code lines. ADR 0087 is unaffected: its obligation remains; F1 shows an incomplete implementation. No reserved number, migration or added ADR requires a number-guard check.
- DONE: Goal sufficiency, minimum necessity and the minimal acceptance script assessed at the same candidate.
  Sufficiency fails at F1. Raw header scanning is needed by the header-only negative, and the wording is needed by the sealed literal-path negative; no extra product surface was added. The command below runs three observable steps (identity, gate/recovery, gzip attacks) in less than five minutes; current exits are 0 then 1 for the behavioral steps (`evidence/validation-1/runs/retained-acceptance.log`). No UI surface exists.
- SKIPPED: Local RoboRev, publication, review requests, readiness, merge, installations and live mode changes.
  RoboRev was not run by this validator; job 1866 is FO-reported only. Those actions remain FO-owned; no CI configuration changed and CI cost per PR was not measured. Release/README synchronization and the design's four home-flip conditions remain future obligations.
- SKIPPED: State commit and sync after the sandbox refused the supported state command.
  `spacedock state commit` exited 1: shared `index.lock` creation was denied with `Operation not permitted` (`validation/state-commit.json`). No git-add, alternate commit or escalation fallback was used; FO must commit the task report, evidence folder and validation receipts path-scoped, then sync.
- DONE: Public evidence retained and the required installed-package scratch close completed.
  Live-list scan before sealing found 0 hits in each class across 48 files (`evidence/validation-1/runs/privacy-final.json`); `validation/scratch-close.txt` records close exit 0. Exact close output follows; all scratch clones and probes were removed.

### Findings

- F1 Material: `kc-dev-flow-2/scripts/state_guard.py:215` loses gzip member boundaries. Released user/workflow: a worker commits sealed gzip on a guarded linked state branch. Observable harm: an invented listed private name reaches its own remote with commit/push both 0. Boundary: `value-ac[AC-4]` requires header-only refusal; `contract[docs/adr/0087-public-state-writes-and-an-opt-in-git-guard.md#decision]` requires refusal before push. Trigger: a clean text member followed by `gzip(gzip(header-bearing gzip))`; joined decoded output starts with text, so the recursive loop stops. The nested-body companion is the same defect. Return through implementation feedback; assess without repairing. Evidence and a suggested correction are in `evidence/validation-1/runs/findings.json`.

### Minimal acceptance script

Run the command as written: step 1 verifies the pinned candidate; step 2 must pass the real gate and sealed-evidence recovery; step 3 must refuse all invented gzip identifiers. A repaired candidate should pass its updated script; this candidate deliberately returns 1 and names the two unexpected acceptances. It proves no live installation, future writer, complete historical tailnet scan, hosted review or merge.

```sh
python3 -B ~/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/evidence/validation-1/proto/acceptance.py ~/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo /tmp/dev2/kc-claude-plugins-3042bb224e995ded/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/validation-1/captain-check ~/.local/bin/spacedock
```

### Scratch close

Scratch removed: /private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/validation-1 (915613312 bytes)
Evidence: evidence/validation-1/ (49 files, 105.6 KiB)

### Summary

REJECTED at the dispatched candidate: the combined nested gzip member lets a listed private identifier through both hooks, despite the simple header cases and existing tests passing. AC-1, AC-2, bounded AC-3 and AC-5 have independent runtime evidence; the historical tailnet-host comparison remains partly unverified. FO owns the refused state commit/sync and the material-finding disposition before any implementation repair or delivery.
