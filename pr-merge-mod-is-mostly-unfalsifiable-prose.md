---
title: Most of the pr-merge mod is prose no test can falsify
status: backlog
source: EM gate on #142, 2026-08-03 — found while falsifying that PR's own restored coverage
design:
id: 2hrc93vkhepjee9xx9g2437g
---

## Problem

Only two regions of `docs/dev/_mods/pr-merge.md` are extracted and sourced by
`docs/dev/artifacts/terminal-transaction-contract-test.sh`: the
`# decoupled-terminal-transaction:*` markers at 405-432 and the
`# decoupled-archive-comparator:*` markers at 642-789. Everything else in that
~2100-line mod is prose that no test reads.

The legacy direct-commit terminalization route is the concrete case. The mod
requires `git merge-base --is-ancestor "$DIRECT_COMMIT" "origin/$BASE"` at
1753-1757. Deleting that rule outright and re-running the contract test through
`CONTRACT_PR_MERGE` leaves the suite green, because the reachability check the
test exercises is `authenticate_terminal_route()` — the harness's own restatement
of the rule, byte-identical on `main` and on #142's branch. PR #120 disclosed
this when the harness landed ("fixture-authored, not independent upstream
proof"), so the bound is known rather than hidden; it has simply never been
decided.

This is the same defect class as the measurement ledger #142 removed: a rule that
reads as enforced and is not. It matters more here, because the direct-commit
route is one of exactly two terminalization routes and its guard exists to stop a
commit that never reached `main` from being archived as delivered — and the route
is live, not vestigial.

The open decision is which way to close it: extract the prose rule into
executable markers so the mod becomes the tested artifact, or formally accept
fixture-authored coverage for the legacy route and say so where the coverage
lives. A third option worth pricing is retiring the direct-commit route, which
would make the question moot. Naming which regions of a long contract are
executable and which are prose is the general form, and is probably the more
valuable output than fixing this one route.

## Notes

A separate, smaller defect surfaced by the same gate and worth folding in or
splitting off: `absolute-claims-need-an-enforcement-point.md` on the state ref
carries `pr: direct-commit:2527c78`, a 7-character abbreviation, while the guard
requires `^[0-9a-f]{40}$`. That live entity would be refused by the route it
depends on.
