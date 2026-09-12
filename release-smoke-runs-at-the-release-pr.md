---
id: 6kh9dgjpmbvv4z8g8e9bahkx
title: Run the candidate release smoke at the Release PR, not on the Captain's machine
status: backlog
source: Captain, 2026-09-12 — `candidate smoke 是否應該設計在 ci 上？在本地跑幾乎沒意義` and `我想像的是 release-please pr應該要跑這個 smoke 而不是我在本機跑，這樣不太對勁`
product: kc-dev-flow
planning-window:
planning-outcome:
sprint:
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## The problem

`candidate` mode is the release boundary's only pre-publication proof, and at
`kc-dev-flow-v4.4.0` it did not run: the Release PR merged, release-please cut the
tag, and the candidate receipt was written afterwards against the already-published
tree. Nothing refused the publication, because nothing reads a prose instruction.

An authenticated Release-PR CI matrix is not a new idea here. The archived
`kc-dev-flow-published-tag-smoke-review` (verdict PASSED, archived 2026-08-11) named
it as the rejected alternative: it "adds secrets, provider spend, workflow authority,
and a second persistence concern **without improving the accepted manual
release-boundary proof**." That clause is the load-bearing premise, and v4.4.0 is its
first recorded counterexample — the manual proof did not run at all.

Retention itself is settled and is not reopened here: the first containing-tag run at
`kc-dev-flow-v2.2.0` earned it by catching a producer/consumer gap no pre-release
check had seen (Claude emitted `verdict_note` into a closed adjudication object and
the strict consumer refused it).

## Work profile receipt

## Accepted outcome

Publication cannot complete without a candidate proof that actually ran against the
tree being published — enforced by a mechanism, not by an instruction a human must
remember.

## Non-goals

- Reopening keep-or-remove on the smoke. Retention was decided and the mechanism has
  a real catch behind it.
- Moving `published` mode. It already binds the tag to a receipt, invokes no model,
  and gates local sync — it is not the gap.
- Committing the receipt into the checkout. `CLAUDE.md` places it at an operator-owned
  path outside the checkout on purpose.

## Acceptance evidence

Each criterion needs a run that could have failed, not a workflow file that parses.

- **AC-1** The August rejection is re-decided against v4.4.0's counterexample, in
  writing, either way. A CI matrix that re-incurs the three named costs needs the
  Captain; keeping it manual needs a named enforcement point that is not memory.
- **AC-2** Whichever half can run without provider credentials is separated and
  measured. The claim to test: `claude`'s install path completes before the script's
  `claude auth status` call, while `codex`'s install is handed `auth.json` first —
  so the credential-free boundary is a measurement, not a reading of the source.
- **AC-3** If any model-invoking step lands in CI, its exposure is stated against
  this repository's current surface: `iamcxa/kc-claude-plugins` is PUBLIC and its
  workflows reference exactly two secrets, `GITHUB_TOKEN` and `RELEASE_PLEASE_TOKEN`
  (measured 2026-09-12). Codex authenticates by `auth.json`, an account login file,
  not an API key.
- **AC-4** Per-Release-PR cost is stated as a measured number or declared unmeasured.
  A Release PR is re-pushed on every merge to `main`, so a naive trigger re-runs two
  high-effort model invocations each time.
- **AC-5** A nondeterministic required check is either shown not to block merges on
  a flake, or is not made required.

## Route-back conditions

- The credential-free boundary in AC-2 turns out not to exist — then the split is
  not available and this reduces to the enforcement question alone.
- A CI matrix is chosen and its first run cannot reach the release boundary without
  a fork-PR secret exposure.

## Measurement

Baseline to beat: at v4.4.0 the candidate proof ran zero times before publication.
