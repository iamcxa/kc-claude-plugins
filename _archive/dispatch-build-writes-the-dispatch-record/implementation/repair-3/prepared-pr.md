feat(kc-dev-flow-2): record stage dispatches before building

Build stage-worker dispatches through a package script that writes a record from
the actual checklist/scope notes, runs both record checks, then invokes Spacedock.
The stamp commit includes the record; advance commits before returning its envelope.
Successful checker warnings reach FO before the build, with identical lines printed
once and distinct stage reminders retained. Checker success chatter stays out of
the JSON envelope; existing failure diagnostics and cleanup ownership are preserved.

The wrapper checks the complete task commit scope before selecting a record.
HEAD, index and raw worktree bytes/modes must agree, with no nonignored untracked
work; conflicts, hidden index flags and unsupported types/escapes hold without
builder/cleanup calls. Owners must preserve/reconcile staged and worktree versions
before intentionally committing. Exclusive same-task ownership must last through
check/build/commit/cleanup: this precondition is not a transaction lock and makes
no concurrent-writer safety guarantee.

Captain amendment 1 replaces AC-5 with AC-9 and accepts the pinned Spacedock 0.27.2
no-op retry limit: identical retry succeeds without other tasks' staged content;
with it, retry exits 1 with no envelope and no file/index change, because upstream
checks the whole checkout's staged content before an empty task-scoped commit.
After unstaging that other task, retry recovers without a second record. The old
criterion is preserved verbatim; evidence (a)/(c) and its three falsifiers remain.
Changed input or a later state commit still creates the next round. Failed checks
or builds remove only an invocation-created record still absent from HEAD.

ADR 0070 records the approved package seam. Model/roster stay FO-supplied and
package/workflow preflights remain separate. The three approved workflow passages
reduce the budget from 5933 to 5931; FO follow-up 1 authorizes the observer's
matching chat-only entry. No version bump. The installed 0.35.0 ADR linter has a
known historical ADR 0047 assertion false positive; FO follow-up 2 authorizes the
candidate linter, with the assertion unchanged.

Validation at local candidate bd9d4abce4e0c61a69079d4e822b6ded45cfdc20: original fresh-shell
acceptance passed; 28 checked-in CI Python commands exit 0
(1225 tests reported, 11 optional skips). Evidence:
implementation/repair-3, including 22 real-binary seam tests, 98 unchanged refusal
snapshots, 13 original + 9 scope + 4 warning counterexamples. The warning observer
reads stderr before invoking the real binary; missing, duplicate, late and
whole-stream-only forwarding each fail matching assertions. The original and
scope controls retain committed inputs, clean retry, numbering, advance,
reconciliation and failure recovery contracts.

Product branch remains local; FO owns pushing this candidate, PR review reply,
new-head hosted CI and independent validation. Prior hosted evidence applies to
parent 778367adde2e20e0b3e51966ddba2d9f77f9e614. CI cost per PR is unmeasured;
existing package/workflow path triggers and CI configuration are unchanged by
this repair.
