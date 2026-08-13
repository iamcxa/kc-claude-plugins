---
id: 92h25gk5mcagj6wtqrz24nsa
title: "kc-dev-flow: no stage reads PR review feedback, so a PASSED verdict can ship unread reviewer findings"
status: backlog
source: https://github.com/iamcxa/kc-claude-plugins/issues/213
product: kc-dev-flow
sprint: S2
started: 2026-08-12T01:51:59Z
completed:
verdict:
worktree:
issue: "213"
pr:
mod-block:
design:
lane:
---

## Problem

The kc-dev-flow contract declares no stage that reads a pull request's review
feedback, so a task can close `validation` with an EM verdict of `proceed`, be
recorded `verdict: PASSED`, and reach the `done` gate while unresolved review
threads — including ones describing a regression the change itself introduced —
have never been read by any seat. The reporter's account is that `validation`
declares its inputs as the ACs plus the implementation stage report, which does
not include the PR; `_mods/pr-merge.md` owns PR lifecycle but touches reviews
only in its PR-body approval guardrail and never queries review state; and the
`done` gate turns on CI observed green, which is silent about open review
threads. The reported downstream instance is `iamcxa/qnow` PR #1057, where two
bot reviewers independently raised a filter/pagination reset regression that a
full flow — fresh-context validator, EM verdict, cross-model gate, and a browser
drive — did not surface, and which the browser drive reportedly could not have
surfaced because the branch data set was too small to reach page 2.

## Proposed approach

## Design determination

## Acceptance criteria

## Test plan

## Measurement

## Doc diff

## Out of scope

## Stage Report: backlog

Verdict: core claim CONFIRMED; issue's supporting detail is wrong in three
places. Defect lane does NOT hold — main route through ideation required.
Scope: `origin/main` @ `abf69f5`, clean tree, tags refetched.

- DONE: Verify or refute, at file:line against fresh origin/main, the issue's core claim that no kc-dev-flow stage, gate, or vendored mod declares reading a PR's review feedback — and state which result would have refuted it.
  CONFIRMED. Census over `docs/dev/README.md` + `docs/dev/_mods/*.md`: `review
  comment`/`review thread`/`bot review`/`automated review`/`reviewDecision`/
  `CHANGES_REQUESTED`/`dispositioned` = 0; `reviewer` = 26 (issue said 21).
  Over all of `kc-dev-flow/**`: same 0s except `dispositioned` = 4, all in
  `kc-dev-flow/scripts/absolutes-check.py` (absolutes registry, unrelated).
  Across all nine release tags `kc-dev-flow-v1.0.0`..`v2.3.0`: 0 — verified from
  git tags, not the plugin cache (no kc-dev-flow in this machine's cache).
  Concept census by other wordings (`copilot`, `PR review`, `review state`,
  `unresolved`, `feedback`, `gh api`, `resolve`) over the same population: no
  hit means a PR's review feedback. `docs/dev/README.md:24` `feedback-to:` is
  spacedock gate routing, a homonym. Behavioral corroboration, not tokens: the
  only `gh` PR reads request `state` (`docs/dev/_mods/pr-merge.md:13`) and
  `body,headRefOid,mergedAt` (`:197`, `:309`) — `reviews`, `reviewDecision`,
  `reviewThreads` are never requested. REFUTED BY: any of those `--json` field
  lists naming a review field, or any stage/gate clause requiring a review read.
- DONE: (same item) — where the issue is wrong or overstated
  (a) "none of the `reviewer` hits mean a GitHub reviewer" is false:
  `docs/dev/_mods/pr-merge.md:61,:70` mean the PR's reader, and `:243-244`
  imposes a real duty ("A reviewer must explicitly acknowledge the exception
  before the PR becomes ready or merges; author approval is insufficient"), as
  does `:281` ("each layer's required checks and review are green"). The
  contract is not silent about GitHub reviewers — it is silent about reading
  their findings. (b) The quoted validation Inputs ("the ACs and the
  implementation stage report") exist at no file:line here; that wording is the
  downstream adopter's own README, not anything kc-dev-flow ships. (c)
  `_mods/pr-merge.md` is not a kc-dev-flow mod: frontmatter `version:
  0.12.2+kc.1 / upstream-version: 0.12.2` (`:1-5`), stock = spacedock 0.26.0
  `mods/pr-merge.md`; `:1-100` is stock (only `:57` adds `--draft`), `:101-357`
  is a local kc-dev-flow extension. Spacedock is not one of this repo's plugins.
- DONE: (same item) — where Inputs and the done gate are actually declared, and which an adopter reads
  SHIPPED: `kc-dev-flow/references/kernel.md:39-49` (validation `:47-48`, done
  `:49` — one line each, no Inputs list) and
  `kc-dev-flow/skills/continue-dev-flow/SKILL.md:193-204` (EM verdict per gate;
  exact-head CI/runtime as delivery evidence; terminalize when every AC has
  fresh validation). NOT SHIPPED: the detailed stage sections —
  `kc-dev-flow/skills/adopt-dev-flow/SKILL.md:44-54` has the adopter add
  `Policy mods:` to its OWN workflow README and vendor kernel.md byte-for-byte.
  So `docs/dev/README.md:282-321` (validation) and `:327-332` (done, "required
  checks green on its exact HEAD") are this repo's local instance only. An
  adopter reads `_mods/kernel.md` (byte-identical to the shipped reference —
  `diff` empty) + the shipped skills + its own README; it never reads
  `docs/dev/README.md`.
- DONE: Determine whether the proposed fix can reuse existing capability rather than add a mechanism: establish whether kc-pr-flow in THIS repo actually ships a review-resolution skill, name it at its path, and record what it does and does not do.
  YES: `kc-pr-flow/skills/kc-pr-review-resolve/SKILL.md` (kc-pr-flow 1.11.1).
  DOES: fetch both unresolved inline `reviewThreads` (GraphQL) and PR-level
  reviews (REST) (`:91-114`); reviewer/is_ai map (`:116-129`); validate every
  comment on technical merit, forbidding both auto-accept and auto-dismiss
  (`:135-157`); cross-AI dedup by (file, conceptual issue) that surfaces
  parallel agreement (`:161-196`) — the incident's exact shape; verdict
  persistence (`:198-243`); triage + confirmation GATE (`:245-278`); reply to
  every thread, resolve, then re-query and assert unresolved (`:348-392`);
  `auto_confirm: off|reply_only|preapproved` (`:10-22`).
  DOES NOT: produce a verdict any stage consumes; know the entity, stage, ACs,
  or `verdict:` field; gate on an EM/FO seat (it gates on the user); or fail
  closed — `reply_only`/`preapproved` skip its own gate (`:288-331`). Nothing in
  kc-dev-flow or docs/dev invokes it (`git grep kc-pr-flow` over both returns
  only ROADMAP sprint labels and an artifacts script). Reuse is nonetheless
  demonstrated in this repo: `docs/ship-flow/_mods/pr-merge.md:290-305` already
  dispatches it and gates CLEAN/BLOCKING/PROMPT_CAPTAIN with a 2-round cap — but
  in ship-flow's mod, not dev-flow's. Constraint on reuse:
  `kc-dev-flow/references/engineering-judgment.md:122-125` and
  `kc-dev-flow/README.md:38` disclaim prescribing a delivery provider or
  thread-reply format, so naming this skill in the shipped kernel cuts against a
  stated boundary; naming it in this repo's local README does not.
- DONE: Return the backlog routing determination: whether the defect lane's four conditions hold, naming the first that fails, or whether the main route through ideation is required.
  Main route through ideation. FIRST FAILURE is condition 1: the reported root
  cause has no file:line here (the quoted Inputs sentence is absent), and the
  real anchor is an omission spread across `kernel.md:47-49`,
  `continue-dev-flow/SKILL.md:193-204`, `docs/dev/README.md:287-290` and
  `:327-328`, and `runbooks/validation-evidence.md:8-16` — which of those is
  "the" root cause IS the placement decision. Condition 2 is partly available
  and I decline to score it clean: `scripts/kc-dev-flow-contract-test.py`
  already pins stage prose by substring (`:1106-1112`), so a fails-before/
  passes-after assertion is mechanically writable, but `docs/dev/README.md:144-147`
  and `adopt-dev-flow/SKILL.md:59` disqualify a text match as proof of
  behavior — it would prove the clause was written, not that a seat reads a
  review. Condition 3 fails: seams span `references/kernel.md` + its vendored
  copy (`adopt-dev-flow:53,:56` forbids editing the vendored file, so both
  move), `continue-dev-flow/SKILL.md`, `docs/dev/README.md`, and the
  spacedock-owned `_mods/pr-merge.md`. Condition 4 fails: portable-vs-local
  placement, whether the kernel may name a sibling plugin, what "unresolved"
  means without a GitHub-specific API, and post-gate review arrival — which the
  issue explicitly leaves undecided — are all open.
- SKIPPED: independent verification of the downstream incident (iamcxa/qnow PR #1057)
  Not reachable from this checkout; treated as report, per the assignment.

### Could not determine

Whether `main` requires an approving review: `gh api .../branches/main/protection`
returns 404 and `.../rulesets` returns `[]`. That reads as "unprotected", but a
404 can also be a token-permission artifact and I could not distinguish the two.
If unprotected, nothing outside the contract catches an unread review here.

### Summary

The issue's core claim survives: across `kc-dev-flow/**` at every released tag
and across this repo's adopted `docs/dev/**`, no stage, gate, or vendored mod
declares reading a PR's review feedback, and the mod that touches PRs never asks
GitHub for a review field. Three supporting details are wrong — the `reviewer`
hits do include GitHub reviewers with a real duty, the quoted validation
"Inputs" sentence exists nowhere in this repository, and `_mods/pr-merge.md`
belongs to spacedock rather than kc-dev-flow. The capability the issue points at
is real and already wired in a sibling workflow here, but the fix's placement
(portable kernel vs local README vs another project's mod) is undecided and is
itself the root-cause question, so this is not a defect-lane item.
