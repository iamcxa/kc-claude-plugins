---
id: cx23zq6y1apw1j0kvdf3mns9
title: Dogfood Spacedock projection in kc-claude-plugins Project #1
status: done
source: Captain instruction on 2026-08-14 to continue until Project #1 shows the projection result
product: repo-platform
sprint:
started: 2026-08-14
completed: 2026-08-14T10:06:26Z
verdict: passed
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/worktrees/qa-project-install
issue:
pr: pr-merge:228
mod-block:
design: required
lane: main
archived: 2026-08-14T10:06:26Z
---

Install the merged deterministic projector into `iamcxa/kc-claude-plugins`, project ten selected `docs/dev` entities into user Project #1, and prove visible field values plus a zero-mutation rerun without giving GitHub lifecycle authority.

## Scope

- Install exactly the workflow, config, and vendored projector bytes produced by `setup-github-project-projection`.
- Keep approval scope `selected` for ten reviewed entity slugs and cap the first run fail-closed.
- Create no linked-Issue bindings; projector-owned Issues may be created only for the selected entities.
- Preserve foreign Project items, verify exact receipts, and leave reverse sync, Milestones, status publication, and additional repositories out of scope.

## Acceptance criteria

1. A no-write installer plan reports exactly three target files and Project #1 identity `PVT_kwHOABc8eM4A-a-N`.
2. The committed config pins `main`, `spacedock-state/dev`, `docs/dev`, the `kc-dev-flow` profile, the installed projector digest, ten selected entities, an expiring classic-PAT approval, and a positive mutation cap.
3. CI and a local audit prove installed byte identity, workflow syntax, config validation, and zero secret values in tracked files.
4. A default-branch manual dispatch creates the selected projector-owned Issues and Project items while leaving receipt-less foreign items unchanged.
5. Live readback shows the selected items in Project #1 with `Status`, exact `SD Stage`, and non-empty `SD Product` when present.
6. An identical rerun records zero mutations and zero planned operations.
7. Every external write is journaled in the reconcile artifact; Project #1 remains derived and SD remains authoritative.

## Evidence boundary

The repository secret value is a separate host operation and never enters installer output, git history, task state, or chat. If the dedicated classic PAT secret is absent or its expiry cannot be bounded, stop before external apply while continuing all file-only validation.

## Stage Report: ideation — cycle 1

**Decision: proceed with the three-file selected-scope dogfood installation; live apply remains separately blocked on a dedicated credential and complete expiring envelope.**

- `Lenses:` value is a visible ten-item Project #1 slice; authority stays one-way from SD; mechanism is the merged installer plus its one workflow and vendored deterministic projector; removal remains the scheduled-automation sunset task.
- `Minimal stack:` no service, database, webhook, reverse sync, reusable workflow repository, or LLM runtime is added. The no-write plan at product base `f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7` reports exactly three CREATE files and zero external mutations.
- `Selected envelope:` exactly ten named slugs, no linked human Issues, Project ID `PVT_kwHOABc8eM4A-a-N`, and fail-closed cap 80 subject to the actual dry-run count being no greater than 80.
- `Credential boundary:` repository readback shows no `SPACEDOCK_PROJECT_TOKEN`; the existing `RELEASE_PLEASE_TOKEN` is not dedicated and may not be reused. Secret provisioning is a host operation and blocks only live apply.
- `Cross-model:` PASS — fresh Claude Opus 5, high effort, safe mode, no tools or MCP, returned `proceed`; it found no file-implementation blocker and independently required the dedicated classic PAT, recorded permissions and expiries, rotation owner, fallback blast radius, exact selected scope, dry-run count, manual dispatch, and identical no-op rerun before live apply.
- `Disproof hooks:` any fourth installed file, external mutation during install, plan count above 80, absent or over-broad envelope metadata, receipt-less foreign-item mutation, or a non-zero identical rerun rejects the slice.

## Stage Report: implementation — cycle 1

**Verdict: implementation complete at product commit `cf61b4b5d631358d0f85f28a046c773737cf802f`; Project #1 remains unmutated pending delivery.**

- Installed exactly `.github/workflows/spacedock-project-sync.yml`, `.github/spacedock-project.json`, and `.github/scripts/project-spacedock-state.py`; 1,708 added lines, of which 1,572 are the byte-identical merged projector runtime.
- Installer audit reports all three files `NO_CHANGE`; installed projector SHA-256 is `be538048ee802a8d9e80568c6dc5558eba50a420bb0ee252245cc674ddfc5c18`.
- Live read-only dry-run against Project #1 and state commit `6c98fe0b5c37400366471da012c0c7984bb114e4` reports ten selected entities, zero conflicts, eight backlog and two implementation stages, and schema creation for `SD Stage` plus `SD Product`.
- The first sample exposed two unapproved linked Issues (`issue189`, `issue190`) and correctly refused them. They were replaced with `github-project-projection-dogfood` and `e2e-typed-operands`; no source task or human Issue was changed.
- Armed envelope records Project `PVT_kwHOABc8eM4A-a-N`, `classic-pat`, permission `project`, credential expiry `2026-08-21`, approval expiry `2026-08-20T23:59:59Z`, rotation owner `iamcxa`, explicit fallback blast radius, the exact ten slugs, no linked bindings, and cap 80. The deterministic first-run estimate is 32 writes.
- Repository Actions secret readback confirms `SPACEDOCK_PROJECT_TOKEN`; its value was never read, copied, printed, or stored. `RELEASE_PLEASE_TOKEN` remains separate.
- Focused projector suite PASS 34/34; kc-dev-flow contract PASS; installed config validation PASS; installer audit PASS; Ruff PASS; Python compilation PASS; actionlint PASS; token-pattern scan PASS; staged diff check PASS.
- External authority remains unopened until the default-branch workflow is merged. The first manual dispatch and its identical no-op rerun are validation evidence, not implementation assumptions.

## Stage Report: validation — cycle 1, pre-delivery

**Verdict: exact candidate `cf61b4b5d631358d0f85f28a046c773737cf802f` may enter Draft review; Ready, merge, dispatch, and Project mutation remain pending.**

- `Lenses:` behavior and mapping PASS with ten selected projectable entities and zero conflicts; authority PASS with split tokens and expiring selected scope; security PASS with no credential bytes in tracked or reported data; runtime PASS locally; delivery remains pending GitHub CI and post-merge live proof.
- `Diff coverage:` all 1,572 installed projector lines are byte-identical to merged asset digest `be538048ee802a8d9e80568c6dc5558eba50a420bb0ee252245cc674ddfc5c18`; the novel 136 lines are the generated workflow and config, both covered by installer audit, config validation, actionlint, and contract checks.
- `Adversarial:` the initial sample's two unapproved linked Issue references were refused before writes; the final sample has no linked bindings, no conflicts, a 32-write deterministic count, and cap 80.
- `Cross-model:` Claude Opus 5 High returned `draft_pr_only` with confidence 0.86 and no blockers. It independently identified a schedule-before-first-dispatch race as the merge-time risk and requested independent re-confirmation at Ready/merge.
- `Schedule disposition:` merge only just after a 15-minute cron boundary, dispatch manually immediately, and require ten-item field readback plus an identical zero-operation rerun before schedule evidence is accepted. Any scheduled run that starts first becomes the first apply evidence and must satisfy the same readback/convergence bar; it is never hidden or relabeled manual.
- `E2E:` local live read-only Project observation PASS; GitHub-hosted apply and no-op remain pending delivery.
- `Origin re-observation:` pending the Project #1 manual run; Project #1 remains zero items at this checkpoint.

### Draft delivery and Ready gate

- Draft PR `#228` binds exact base `f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7`, exact candidate `cf61b4b5d631358d0f85f28a046c773737cf802f`, and exactly one matching `Candidate:` line.
- GitHub CI PASS at that head: portable e2e suite, version parity, real-browser decision/proof, and GitGuardian all green; expected non-applicable jobs skipped.
- GitHub PR feedback snapshot is complete at that head: zero reviews, zero issue comments, zero review threads, zero unresolved threads, and no pagination remainder.
- Fresh Claude Opus 5 High Ready gate returned `ready_only / high`, acknowledged the native-stack exception, found zero blockers, and granted no merge, dispatch, or Project mutation authority.
- Ready remains captain authority. Merge-time revalidation must confirm token/approval validity, recount the live plan, and re-observe the cron/manual race.

### Live Project #1 validation

**Verdict: PASS — Project #1 visibly contains all ten selected entities and the identical-input rerun produced zero operations.**

- PR `#228` squash-merged at `2026-08-14T10:00:36Z` as `c00de6c2140db268eb1fe693abfa347b13a9e0b4`. Manual dispatch began two seconds later; no scheduled run existed before it.
- First run `31790461828` completed all 32 planned writes: two fields, Issues `#229` through `#238`, ten Project items, and their managed fields. It then failed the immediate post-apply convergence assertion because GitHub's first re-observation was not yet consistent. The uploaded failure receipt journals every successful operation.
- A later read-only observation against the identical trunk `c00de6c2140db268eb1fe693abfa347b13a9e0b4` and state `d1c9208e0737cdc42a9021e595e16bf875a14ba8` returned ten `NO_CHANGE`, zero mutations, zero orphans, and zero conflicts. The failure is bounded to immediate provider consistency; no lost or partial Project write remained.
- Before the next run, selected entity `roborev-implementation-exit` legitimately advanced from implementation to validation on state `33bed021d985867d7652c034bb3642e6c2bfa2fa`. Run `31790671419` performed exactly two journaled operations for Issue `#235`, then re-observed zero mutations and succeeded.
- Identical-input run `31790729428` used trunk `c00de6c2140db268eb1fe693abfa347b13a9e0b4` and state `33bed021d985867d7652c034bb3642e6c2bfa2fa`; its artifact reports `mode=apply`, zero operations, zero converged mutations, and zero conflicts.
- Project readback reports exactly ten items: eight `Todo` with exact `SD Stage=backlog`, two `In Progress` with exact `SD Stage=validation`, and non-empty `SD Product` only where the source supplies it. Project fields expose options `e2e-pipeline`, `kc-dev-flow`, and `repo-platform` without inventing values for partial entities.
- `E2E:` PASS — create, visible field readback, legitimate state update, provider-settled convergence, and identical no-op rerun all ran on GitHub-hosted Actions with the installed split-token path.
- `Origin re-observation:` Reported scenario: SD tasks were invisible in GitHub | Runtime kind: production repository and private user Project #1 | Artifact/revision: merge `c00de6c2140db268eb1fe693abfa347b13a9e0b4`, state `33bed021d985867d7652c034bb3642e6c2bfa2fa`, runs `31790461828`, `31790671419`, and `31790729428` | Falsifier: fewer than ten qualified items, incorrect Status/SD fields, foreign mutation, unresolved conflict, or non-zero identical rerun | Result: PASS.
