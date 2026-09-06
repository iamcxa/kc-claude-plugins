## Ship-flow runtime

This section applies only to a First Officer that dispatches build workers into
Conductor cloud workspaces and reads them back through the `conductor` CLI. It
is this repository's own runtime record, not a kc-dev-flow contract: an adopter
running workers locally, on a Hermes runner, or on another host is not covered
by it and must not treat these sentences as requirements.

Dispatch a higher layer only after the lower layer is fully verified. (DEV-67)

A dispatch message to a cloud build worker carries no bootstrap or download
line: the Conductor WAF blocks a dispatch message containing a `curl | tar`
bootstrap line, and the worker's image already preinstalls `kc-dev-flow` and
`spacedock`, so no dispatch message needs to fetch and unpack them. A task
body longer than the first message does not fit in that message either; it
travels on a committed carrier — a file such as `DISPATCH.md` committed to a
branch the worker fetches and reads with `git show <branch>:<path>` — rather
than being pasted inline.

A worker's without-it command runs in an isolated environment (temporary HOME, no agent, no network). (DEV-67)

CLI e2e evidence is a timestamped stdout log written by
`kc-ship-flow/scripts/e2e-cli.sh <sha> <flow.yaml>`. It runs each of the flow's
`Execute external` steps (e2e-pipeline's `execute.cli` step shape, consumed
read-only) at the pinned `<sha>` and exits non-zero on the first step whose
command's exit code does not match its declared `expect`. `asciinema` and
`script(1)` both hang without a pty, which cloud build workers do not have, so
this stdout log — not a terminal recording — is the CLI e2e evidence of
record for that context.

The worker's Evidence block defines `CANDIDATE_SHA`, `BRANCH`, `BASE_SHA`,
`WITHOUT_IT_COMMAND`, and `WITHOUT_IT_REMOVED_VARIANT`. `WITHOUT_IT_COMMAND` is
one self-contained shell line: it references no file outside the candidate
tree, it exits 0 on the candidate and non-zero once `WITHOUT_IT_REMOVED_VARIANT`
is applied, and the First Officer runs it verbatim, unchanged, in a worktree
with no secrets. `kc-ship-flow/scripts/without-it.sh <sha> <command>
<removed-variant>` runs `<command>` retained, applies `<removed-variant>`, runs
`<command>` again, and exits 0 only when the retained run passes and the
removed run fails.

Security, data-loss, and compatibility findings outside the Brief block the candidate while general improvements are scoped out. (DEV-67)

Ship-flow's workspace-create guarantee is that the production entry issues at
most one `conductor workspace create` call after a committed intent:
`conductor workspace create` is not idempotent and a holder can sleep between
the call and its receipt, so every external action follows one order —
`kc-ship-flow/scripts/intent.sh commit` writes the claim, dispatch token,
project, base branch, and message sha256 to the state branch and pushes it;
`holder.sh check` confirms the writer; the create is called once with the
token in the workspace name; the token, name, and project are read back;
`holder.sh check` runs again; only then `intent.sh adopt` persists the
workspace id. It is not exactly-once and it covers workspace creation only: a
holder that takes over runs `intent.sh reconcile` first, adopting the one live
workspace whose name carries the intent's token and whose project matches,
blocking with `unresolved intent` on zero matches and `ambiguous intent` on
two or more, and in no case does the new holder create a workspace for an
intent it did not commit. `intent.sh commit` and `intent.sh adopt` hold an
flock on `<state-dir>/.ship-lock` around their whole sync-write-commit-push
sequence so two concurrent calls on the same checkout serialize instead of
racing the shared working tree, and the intent binds the dispatched project,
base branch, and message sha256 so reconcile and every adopt refuse a
candidate workspace with `project mismatch` when its project id does not
match the one committed.

The First Officer reads a worker's transcript through `conductor sql` against
`session_transcripts_view`, not `conductor session message --after`: that CLI
truncates its JSON response at 64 KB, which cuts off a long Evidence block, and
its `--after` cursor rejects a sent message's id, which breaks polling from the
FO's own last message. `kc-ship-flow/scripts/worker-transcript.sh <session-id>`
prints the session's last fenced `## Evidence` block, or exits 1 with `no
evidence block` when the transcript has none. One read per invocation; no
polling loop, retry, or daemon.

A Milestone's CLI journey lives at `docs/ship-flow/flows/<milestone-slug>.yaml`
in e2e-pipeline's `Execute external` step shape, consumed read-only by
`kc-ship-flow/scripts/e2e-cli.sh`; the slug lowercases the milestone name, keeps
every Unicode letter and digit, collapses every other run of characters
(including underscore) to a single hyphen, and strips leading/trailing
hyphens -- a name that slugifies to empty refuses with exit 2.
`kc-ship-flow/scripts/e2e-gate.py <plan-receipt.json> <close-receipt.json>` reads
the plan receipt's `dispatch_order` and `milestones` for the batch's named
milestone (the last dispatch-order issue whose entry carries one) and,
independently, the close receipt's per-issue `candidate` for the stacked head
(the last dispatch-order issue whose entry carries one -- not necessarily the
same issue; an issue accepted without a PR carries neither field, so both
lookups skip it), resolves that head to a fixed commit, then picks the
batch's UAT-ready shape: a milestone with a flow file runs `e2e-cli.sh` at
the resolved head and reports its log path and exit code; a milestone with
no flow file records `e2e: not applicable` with the reason and exits 0; no
milestone named exits non-zero and the batch is not UAT-ready.

`kc-pr-review` is a skill; the repository's own
`kc-pr-flow/scripts/review-ablation.sh` runs it headless for its ablation
harness, but this station does not -- it runs `kc-pr-review` only inside a
Claude session, so the review station is two scripts either side of that
session run. `kc-ship-flow/scripts/open-pr.sh <evidence-file>` opens the Draft PR from a
worker's accepted Evidence block: title is the `CANDIDATE_SHA` commit's
subject, body carries `BASE_SHA`, `CANDIDATE_SHA`, the without-it pair, and
the block's own `SELF_CHECK` line, and it prints the opened PR number.
`kc-ship-flow/scripts/disposition.py <findings.json>` then reads the findings
the FO's own session wrote to disk after running `kc-pr-review` on that PR
and dispositions them by `kc-plan-approval/v1`'s `defaults.findings_outside_brief`
rule stated above: an empty or missing findings file is `reviewer-absent`
with the `fallback_to_fo_diff_read` marker, never read as "no findings",
because the two are indistinguishable from a findings file alone.

`kc-ship-flow/scripts/uat-doc.py <batch-dir>` builds the batch's UAT document from
its durable records only -- `receipt/plan-receipt.json`,
`receipt/plan-approval.json`, `receipt/close-receipt(.DRAFT).json`,
`evidence/worker-evidence-<ISSUE>*.md`, and, when present, the `README.md`
`## Decisions made under \`defaults\`` bullets -- so the document lists what
the batch already recorded rather than deciding anything new.
`kc-ship-flow/scripts/notify.sh <channel> <batch-id> <doc-path> --dry-run
--state-dir <dir>` sends one UAT-ready message per batch id: a deterministic
message id keyed on the batch id makes a second call for the same batch id
and state dir a no-op instead of a duplicate send. It has no real-send path;
the First Officer sends the real message.
