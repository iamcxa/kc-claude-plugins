---
id:
title: A dispatch, its record and sealed evidence reach the public state branch without personal or private identifiers, and a hook refuses a push that carries one
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
---

The workflow state branch of this public repository receives new personal and private identifiers with every dispatch from two First Officers. An audit on 2026-11-14 (`.context/dev2-reform/phase1-version-and-path-audit.md` Part B, a research output; its counts are not re-measured here) reports a home-directory prefix in 4,646 files, names of private adopter repositories in up to 1,055 files each, private task slugs in 488, a personal email in 25 and tailnet hostnames in 6, and no token-like hit for the patterns it ran.

## Scope

- Source: the Captain 「先做甲止血。要不要換新分支，等我看過外洩清單再決定。」 and, on the guard, 「我在想的是在這個新的綁定一個hook，裡面過濾掉關鍵字，出現就不準推」 (both chat with the reform session, Paseo 26215d96, 2026-11-14; relayed, not rulings here). Admission is recorded by FO under the Captain's grant to the second dev2 FO (chat, 2026-11-14) and the reform session's scope 1 item D.
- Outcome: new writes only. After the change, a dispatch, its saved record and sealed evidence written to a state branch carry no home-directory prefix, private repository name, private task slug, personal email or tailnet hostname, while the runtime prompt a worker receives keeps real paths. Beside the writers, a git hook on the state checkout refuses a commit or push whose added lines contain a listed identifier.
- Writers the audit names, to verify against the code before designing: `kc-dev-flow-2/scripts/dispatch_records.py` (requires an absolute `Package root:` line), `kc-dev-flow-2/scripts/dispatch_stage.py` (saves FO text verbatim), `kc-dev-flow-2/scripts/scratch.py` evidence sealing and its scratch paths, worker harness output (cwd, argv, tracebacks), and whether the paths `spacedock dispatch build` makes absolute land on the branch.
- Observed by this FO on 2026-11-14 while dispatching in the POC workflow: saved dispatch records and gate briefing rooms carried the home-directory path by tool design.
- Open for the design: how records keep verifying when a path is written relative or as a placeholder; the order (private repository names, slugs and hostnames guarded first, the home-directory prefix after the writers change, since today's records require an absolute path); how the hook is installed, scoped to state branches in a shared hooks directory, and how a session without it is detected; what a refusal prints (the file and the pattern class, never the matched string) and the way forward that is not a bypass; where the identifier list lives (outside every repository).
- Profile: pilot. It changes what one package writes and adds a local guard; it carries no production data, credential, migration or unattended operation, and nothing already on the branch is touched.
Non-goals: changing or removing anything already on the branch or in its history; a new state branch or a history rewrite (the Captain decides that after he reads the leak list); patching around a Spacedock writer (report it; nothing is filed upstream without the Captain); writing any private name into the package, a fixture, this task file, a pull request or this branch as a pattern.
Budget: 2 cycles per stage
Stop condition: a writer turns out to be Spacedock's own; existing records or digests cannot stay valid under any design; a suspected key is found; or the design needs a decision only the Captain can make.

## Acceptance criteria

**AC-1**: After a real dispatch with sealed evidence on a throwaway state checkout, the bytes actually committed contain none of the five identifier classes, and the prompt the worker received still held real paths.
Verified by: a scan of the committed bytes of that throwaway checkout against an identifier list held outside every repository, with the run's commands and exit codes; not an assertion that a function was called and not a test on a hand-made payload.

**AC-2**: Records and `SHA256SUMS` digests written before the change still pass the existing record and evidence checks.
Verified by: the existing checks run over a sample of archived task folders at the candidate, with exit codes.

**AC-3**: On a throwaway state checkout with a remote, a push whose added lines hold a listed identifier is refused and one without is accepted; the refusal names the file and the pattern class and does not print the matched string; a checkout without the hook is reported as unguarded.
Verified by: one real refused push and one real accepted push, the refusal's output, a scan of the bytes that reached the remote, and the detection output on a checkout with no hook.

**AC-4**: The package, its fixtures, this task file and the pull request contain no private identifier, including as a pattern.
Verified by: the same out-of-repository list scanned over the candidate diff and the pull request text, exit code recorded. Limit: the list is only as complete as its owner keeps it.

## FO alignment

Alignment: not needed before ideation: outcome, constraints and proof are stated in the scope the reform session gave under the Captain's grant; the open design points return at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance with no release.
