---
session-date: 2026-09-15
sequence: 3
first-commit: b95ac79f
last-commit: b9200699
duration: ~8h45m (2026-09-14 15:34 through 2026-09-15 00:20, state checkout)
---

# Session Debrief — 2026-09-15 #3

One question — whether the execution group could be aligned to a release — opened three deliveries
and two record repairs. The question itself was mis-framed twice before the Captain named the real
goal, and both corrections came from him rather than from the evidence gathered under the wrong
frame.

## Shipped

- **f0** `retire-the-provider-backed-planning-path` — [#444](https://github.com/iamcxa/kc-claude-plugins/pull/444). Dev-flow's only intake becomes a committed brief: the Planning Receipt tuple, the partial-tuple refusal, the engage reconcile, and both `linear-admission.py` and `engage-reconcile.py` leave the package, and `plan-lint.py`'s L4 rule carries its own admission logic instead of reaching back into kc-dev-flow.
- **tj** `sprint-to-release-contract-migration` — [#454](https://github.com/iamcxa/kc-claude-plugins/pull/454). `release` becomes a queryable scalar grouping field whose value is qualified as `<journey>/<release-id>`, so a kc-journey-map release slice lands in a field instead of prose.
- **ab** `pr-merge-mod-rebases-onto-a-stale-trunk` — [#453](https://github.com/iamcxa/kc-claude-plugins/pull/453). The delivery step fetches the remote trunk and rebases onto the remote-tracking ref instead of pushing the trunk and rebasing onto a stale local one.
- **91** `derive-release-story-progress` — [#417](https://github.com/iamcxa/kc-claude-plugins/pull/417). The code landed on 2026-09-11; its terminal approval had been superseded by a rework and never replaced, so the entity sat at `implementation` while its code shipped. Closed here through a successor gate attempt.

## Filed (backlog)

- **tj** `sprint-to-release-contract-migration` — filed, rescoped twice, shipped same session.
- **f0** `retire-the-provider-backed-planning-path` — filed and shipped same session.
- **ab** `pr-merge-mod-rebases-onto-a-stale-trunk` — filed after the defect bit during f0's delivery; shipped same session.
- **yz** `release-field-r1-evidence-record` — filed by an implementation worker to carry AC evidence. Two reviewers judged it an evidence artifact rather than a deliverable; withdrawn on the Captain's ruling and archived.

## Non-PR commits (workflow-only)

State transitions and record repairs that did not flow through an entity PR:

- [#438](https://github.com/iamcxa/kc-claude-plugins/pull/438) registers the `kc-dev-flow/S10` and `repo-platform/S2` execution groups. A roadmap registration, not an entity delivery.
- `b9200699` archives **7k** `first-cloud-dev-flow-improvement-run` with no delivery verdict.
- `89a118eb` withdraws and archives **yz** `release-field-r1-evidence-record`.

All other session commits are rolled up in the shipped PRs above.

## Decisions

Confirmed as drafted by the Captain; the rulings themselves are recorded in the gate decisions they
bind, and are summarised here only where a later reader would otherwise have to reconstruct them:

- **Dev-flow stops taking over the planning tool.** Work reaches it by the Captain's dictation or by
  expanding a plan; a user may still start in Linear, and dev-flow simply stops reading it.
- **The grouping field is scalar.** One release per work item; shared or integration work keeps its
  multiple release origins in prose, matching what kc-journey-map already does rather than forcing a
  single story owner.
- **Rejected at the prove gate, then approved after the fix.** A bare release id conflated across
  products; the qualification was required and delivered rather than recorded as a known limit.
- **7k is archived without a verdict.** The only verdict that finalizes an entity with nothing to
  merge is `rejected`, and the experiment was not rejected — its outcome is no longer recoverable.

## Issues — Workflow

- **7k's `pr` field held prose where the contract requires a SHA.** `local-merge:accepted-cloud-experiment-change-outcome-no-product-diff` fails `prIndicatesMerged`, which accepts `local-merge:` only with a hex suffix, so `merge guard` read it as an open pull request and refused to finalize — indefinitely, and with a message that names the wrong cause.
- **A superseded terminal approval leaves no trace in the queue.** 91's approval was superseded by a rework and never replaced; the entity sat at `implementation` with merged code for four days. Nothing surfaces this except the startup hook noticing its `pr` field, and clearing that field would have hidden it entirely.
- **Local plugin installs had drifted.** kc-journey-map was not installed at all and kc-dev-flow sat at 4.4.0 against main's 4.5.0, so dispatched workers read stale references. Both synced; the Codex marketplace entry for kc-journey-map had to be added by hand because the packaged helper holds no marketplace authority by design.

## Issues — Spacedock

- **`state commit` refuses an archived entity** ("archived scope is publish-only and will not stage or commit it"), so an FO archive move must fall back to a path-scoped commit and push inside the state checkout. Workable, undocumented. Not filed.
- **`gate record --round` requires a room shape `gate prepare` does not produce.** It wants `briefing.json` plus `briefing.review.jsonl`; the prepared room holds only `index.json`. The feedback-rejection flow's round-recording step is therefore unexecutable in this workflow's room shape — the `### Feedback Cycles` projection was written and the recorder skipped rather than fed fabricated paths. Not filed.
- **A POC's route skip is the FO's to apply, with no reminder.** The profile declares `backlog -> implementation`, but `gate consume` advances to `ideation` because the engine is profile-blind by design. An FO that does not know to apply the skip runs a POC through a stage its own stage definition says it skips. Not filed.
- **`status --set` is absent from `--help`, and four different argument mistakes produce one identical error.** The correct form puts the slug first after `--set`; a slug placed before it, a comma-joined pair list, or any flag after it all yield `--set requires at least one field=value argument`. Cost four attempts before reading the Go test that locks the form. Not filed.

## Observations

Confirmed as drafted. Three things are worth carrying forward:

- **The POC did its job by producing a negative result, and the negative result was still wrong.**
  Its `stop` survived an adversarial recount and a second corpus, and was then invalidated by the
  Captain naming a goal the POC had never been asked about. Rigor inside a frame does not test the
  frame.
- **Every delivery this session hit the same stale-base defect** — three times across f0, ab and tj —
  before the fix for it landed. The cost was a rework round each time, and each rework superseded a
  terminal approval that then had to be re-earned.
- **Both record repairs were invisible until something else scanned them.** 7k and 91 had been
  wrong for days; neither appears in `--next`, and the startup hook found them only because both
  happened to carry a `pr` value.

## Agent Testimonial

- Date: 2026-09-15
- Harness/runtime: Claude Code
- Model: Claude Opus 5
- Model version/build: claude-opus-5[1m]
- Session scale: 6 tasks touched; 12 workers dispatched; 4 PRs merged

The structure earned its cost in two specific places and charged for it in a third.

Where it paid: the gate boundary made a rejection cheap. When the prove-stage reviewer demonstrated
that a bare release id conflates across products, routing that back as an authorized correction with
a concrete assignment took one command and one dispatch, and the corrected work came back with the
forced-collision exercise repeated rather than asserted. Without the boundary I would have been
tempted to note the collision as a known limit and ship — the machinery made fixing it the cheaper
path. The second payoff was the refusal to let a superseded approval be re-spent: it forced 91's
history into the open instead of letting me quietly finalize code that had shipped days earlier.

Where it charged: the contract is large enough that following it correctly consumed real attention
that was not available for the work. Four separate mechanisms — the `--set` argv form, the
stage-report completeness predicate, the POC route skip, the round recorder's room shape — each cost
a failed attempt and a source read before I could proceed, and none of the four failures said what
was actually wrong. Twice I resolved a mechanism question by reading the Go implementation, which is
not a workflow a captain should have to fund.

The honest comparison: driving this without Spacedock, the three deliveries would have landed faster
and at least two of them would have landed wrong — the stale-base rebase would have surfaced as a
GitHub conflict after review rather than before, and the release-id collision would have shipped as
a silent grouping bug. The overhead is real and mostly falls on the dispatcher rather than the
worker.

## What's Next

**Nothing dispatchable.** `status --next` reports zero dispatchable entities.

**Not a queue.** 77 ready gates, almost all `needs-preparation` at `backlog` — unadmitted backlog
stock, not decisions waiting on the captain.

**Other sessions' work, untouched here:** PRs #450, #446, #451 and #194.

**Open design question.** `sprint` cannot retire yet. `release` values must be
`<journey>/<release-id>`, and the repository holds exactly one journey file, so the other eight
products have no legal value to write. The shortest retirement path is to evaluate relaxing the
qualification to accept a product prefix alongside a journey prefix; nothing is filed for it.
