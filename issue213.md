---
id: 92h25gk5mcagj6wtqrz24nsa
title: "kc-dev-flow: no stage reads PR review feedback, so a PASSED verdict can ship unread reviewer findings"
status: backlog
source: https://github.com/iamcxa/kc-claude-plugins/issues/213
product: kc-dev-flow
sprint:
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
