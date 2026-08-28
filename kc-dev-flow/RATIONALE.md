# Load the Work, Not the Ceremony

The first version of KC Dev Flow did something important: it made it difficult
for an agent to declare victory without evidence. Authority stayed with the
right person. A local success could not quietly become a Production claim. A
reviewer could point at the exact revision that had actually been tested.

Then I saw the bill.

A POC could answer its technical question quickly and still spend most of its
time proving that the process had been followed. Agents loaded a workflow
README, a kernel, stage prose, and several mods before touching the work. A tiny
repair could become worker, review, repair, re-review, state update, and another
evidence block. The process was preventing false success, but it was no longer
helping every kind of work succeed proportionally.

That distinction matters. The problem was not rigor. It was carrying the whole
workshop to tighten one screw.

## Different journeys need different luggage

I do not fully agree with the idea that a good engineering standard should be
applied uniformly. Uniformity feels safe because nothing is omitted. It also
means an experiment carries the same luggage as an operated service.

A POC exists to make one uncertain thing observable. A Pilot must survive
limited real use. Production accepts a continuing operational obligation.
Those are not three quality levels on one checklist. They are different
promises.

This is the practical version of "if shell is enough, do not turn it into Go to
satisfy an unrelated standard." A tool can be excellent and still be too much
tool for the question. The flow should preserve the boundary, then let the
smallest sufficient mechanism through.

That led to three per-item routes:

- POC: build the smallest real journey and prove its riskiest assumption.
- Pilot: shape, build, verify, and deliver a bounded slice for limited use.
- Production: add the lifecycle, compatibility, recovery, ownership, and
  release proof that an operated capability earns.

One repository can carry all three. The promise belongs to the work item, not
to the repository's identity.

## Planning must remain replaceable

Planning and execution answer different questions. Every route begins with one
admitted brief. Pilot and Production use a Development Brief that fixes the
problem, accepted outcome, complete non-goal list, acceptance evidence, and
route-back conditions. POC uses the decision, falsifier, budget, and stop
condition already stored in `kc-dev-flow-work-profile/v3` as its Exploration
Brief. Feature and bug labels do not change this engine.

A Planning Receipt is optional and complete or absent. Provider-backed work
records exactly `source`, `planning-window`, and `planning-outcome`. Its planning
item owns discussion, the accepted goal, priority, and human-facing status; its
window owns time and its outcome owns the accepted result. The committed
execution snapshot preserves those inputs without becoming another planning
authority.

At every provider-backed engage, a repository-local reader normalizes the
provider's current Ready set, including every still-Ready snapshot source
outside the original window/outcome, and the committed execution snapshot. The
First Officer supplies the source, window, and outcome read from the exact work
item; the vendored read-only comparator checks the normalized snapshot against
those expected values and classifies every delta. The First Officer continues
only on one parsed `status: clean` result. The Captain admits a delta before an
authorized actor commits the replacement snapshot. Because reconcile writes
neither side, it is not synchronization.

Without a Planning Receipt, the Captain-approved committed work item is the
planning authority. It invokes no planning provider or comparator and invents
no Cycle or Release/Milestone. A partial receipt is invalid rather than a reason
to guess which authority applies.

That boundary lets a repository replace GitHub Projects with Linear, or the
reverse, without changing KC Dev Flow. Open provider-backed work not yet
admitted to execution may move; an admitted item keeps its provider and reader
until completion. Standalone work has no provider to migrate. Runtime adapters
decide task, worktree, and worker cardinality, retry, resume, and delivery
ceremony. Their local grouping is not a provider Cycle or Milestone authority.
No projector, importer, polling loop, or bidirectional sync is part of the
portable package.

Exploration observes a decision rather than silently creating delivery scope.
After approval, POC or Spike terminalizes and returns `poc_outcome` to planning.
Planning decides whether a new Development Brief exists; KC Dev Flow does not
create or preselect that downstream work.

## Optional prose is still loaded prose

The old design often said that a rule was optional. That did not make reading it
free. An agent still had to load the rule, decide whether it applied, and resist
imitating nearby ceremony. Optional policy can cost almost as much attention as
mandatory policy.

So the new design does not ask the model to ignore most of a large contract. A
loader receives the exact work item and its `kc-dev-flow-work-profile/v3`
receipt. It emits only three things: the shared authority core, the selected
profile base, and the current stage. Unselected profiles are absent.

This is less like highlighting the right shelf in a library and more like
bringing the three books needed for today's work. The model does not get points
for ignoring the other thousand books. It never receives them.

## Roles should improve judgment, not manufacture opposition

An adversarial reviewer can find real defects. It can also manufacture a second
job: disproving plausible objections that do not affect the accepted outcome.
That cost is easy to hide because the review looks rigorous while delivery
stands still.

The replacement is professional rather than agreeable. A fresh verifier treats
the artifact as an answer to the accepted engineering question. It asks only
questions whose answers could change the verdict, then checks those answers
against the exact revision and real behavior. Chief Engineer advises the next
integrated step. Science Officer enters when a claim is contested, high-risk,
or hard to reverse. Neither becomes a general gatekeeper.

The point is not fewer hard questions. It is fewer questions with no decision
behind them.

## Smaller must remain truthful

Proportional does not mean permissive. Every profile keeps Captain authority,
promotion boundaries, exact-revision claims, and the rule that missing evidence
is not a pass. A POC label still cannot authorize Production credentials,
destructive mutation, or an irreversible migration.

At implementation exit, added files, dependencies, abstractions, tests, and
comments must map to the selected stage's required output. LOC and file counts
can start a question; they cannot decide it. Otherwise minimalism becomes a
score to game, and deleting a necessary test looks better than keeping it.

The smaller route must still tell the truth.

## Evidence, not a victory lap

POC now includes bounded exploration as well as technical proof. Its outcome is
a supported `proceed`, `stop`, or `change` decision, not a delivery verdict.
Finite local comparison can show a profile helped in evaluated scenarios; it
cannot establish that the profile always improves development.

The bounded evaluation recorded in [PR #249](https://github.com/iamcxa/kc-claude-plugins/pull/249)
measured lower required policy input and shorter sampled wall time. The work
record owns those measurements; this retained rationale owns the decision they
bought.

I treat those as directional evidence, not a universal speed claim. The samples
are small. Migration has a real cost. The package now contains more separate
contract files even though each work item reads less. Repositories with custom
terminal states or mandatory reviewer roles need an explicit refit.

The interesting claim is narrower: when policy is excluded mechanically, an
agent can reach the first useful integrated result sooner without silently
crossing the authority boundary.

## What would prove this wrong

I would change direction if comparable work showed that POC and Pilot delivery
time did not fall after setup cost, lower profiles crossed promotion boundaries,
or Production defects increased because lifecycle proof had been misplaced. I
would also change direction if agents routinely ignored the emitted stage, if
adopter maintenance repeatedly cost more than the policy saved, or if
verification still created more unsupported challenge work than
decision-changing evidence.

That is why the evaluation must watch end-to-end delivery time, time to the first
integrated journey, material defect escape, rework rounds, policy bytes loaded,
and human decision time together. Optimizing only tokens, LOC, or review count
would recreate the same problem under a different metric.

The goal is not less rigor. It is rigor that arrives when the work earns it.

Load the work, not the ceremony.
