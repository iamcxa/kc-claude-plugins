---
commissioned-by: spacedock@0.25.0
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 2
  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
    - name: implementation
      worktree: true
    - name: validation
      worktree: true
      fresh: true
      feedback-to: implementation
      gate: true
    - name: done
      terminal: true
---

<!--
  Instantiated from the lean SD workflow canonical template
  (spacedock-workflows muscat/docs/lean-sd-workflow/README-template.md @ 82e8b541).
  Methodology only - runtime concerns belong to the spacedock binary.
  Litmus: crash/concurrency/duplicate-delivery correctness -> binary;
  agent reasoning / evidence discipline -> this README.
-->


# kc-claude-plugins — Development Workflow

kc-claude-plugins is Kent's Claude Code plugin monorepo — home of kc-team-ops, kc-pr-flow, kc-hyperfocus, e2e-pipeline, kc-nightwatch, kc-plugin-forge and friends, published through the personal marketplace. The workload is prose-heavy (markdown skills + agents) with a thin executable layer (scripts, hooks). Repo-level conventions live in CLAUDE.md; PRODUCT.md / ARCHITECTURE.md baselines are seeded by this workflow's first tasks.

Tasks move `backlog → ideation → implementation → validation → done`. One
gated design stage (ideation), one worktree build stage (implementation), one
fresh-context verification stage (validation) with `feedback-to`
implementation, and a terminal merge. The spacedock binary owns all runtime
semantics: stage transitions, gate records, worktree lifecycle, state
durability, exactly-once approval. This README owns judgment discipline only.

## Kernel binding

The portable authority and evidence contract is
[`_mods/kernel.md`](./_mods/kernel.md), vendored byte-identically from
`kc-dev-flow/references/kernel.md` and held there by
`scripts/kc-dev-flow-contract-test.py`. Read it as the authority; this README
adds the local mechanism the kernel deliberately does not prescribe.

The binding itself is [`kernel-binding.yaml`](./kernel-binding.yaml) — authority
map, adopted controls, local routes and exceptions. It is not restated here, so
there is one place to read and one place to change. Verify it rather than read
it:

```
python3 <installed kc-dev-flow>/scripts/verify-binding.py docs/dev/kernel-binding.yaml
```

This repository authors the kernel, so the version pinned in that file is
**observational**: it names the newest published release and exists so this
repository receives the same drift signal an adopter receives, from the same
checker. Authority is the in-tree copy above. Between a kernel edit and the next
release, `REBIND_REQUIRED` against our own published package is the expected
reading — the repair is a release, not a text change.

## File Naming

Each task is `{slug}.md` (default) or a folder `{slug}/index.md` when
per-stage artifacts accumulate. Slugs: lowercase, hyphens, no spaces. Task
state lives in the split-root state checkout (`state:` above) so stage
transitions never churn the code branch.

**The state checkout is wired per workspace, not per repo, and only one workspace
is meant to hold it.** This repo is worked through Conductor worktrees, so
`docs/dev/.spacedock-state/` is a *per-workspace* git worktree tracking the
`spacedock-state/dev` branch, and the path is gitignored in the code tree. Plain
`git worktree add` refuses a branch already checked out elsewhere, so at most one
workspace is the **holder**; every other workspace is a **non-holder** and writes
through the detached path below. That refusal is the whole enforcement, and
`git worktree add --force` overrides it — so single-holder is a convention this
section asks you to keep, not an invariant git will hold for you. The two
wirings are not interchangeable and the check that tells them apart is the same
command.

In a workspace where the worktree was never created, the same path is just an
ignored directory — and the degradation is silent: `spacedock new` reports
`created`, `spacedock status` reads the task back, and only
`spacedock state commit` fails (exit 1, git refusing to add an ignored file).
Tasks filed that way exist nowhere but that workspace. Run this before filing and
branch on what it says:

```bash
git -C docs/dev/.spacedock-state rev-parse --abbrev-ref HEAD
```

- `spacedock-state/dev` → **holder**. File normally; `spacedock state commit`
  works.
- a fatal error, or any other branch → **non-holder**. Do not try to check the
  branch out here, and never write into the holder's tree, which may carry a
  sibling session's uncommitted work. Append through a private detached worktree
  and a fast-forward push. Use a path unique to this workspace — a fixed
  `/tmp/sd-state` collides with a concurrent session doing the same thing — and
  **remove the worktree only after a push you watched succeed.** Two non-holders
  can detach from the same tip; the second push is rejected, and a cleanup that
  runs anyway strands a committed task in a directory nobody will look in again:

```bash
SD=$(mktemp -d /tmp/sd-state-XXXXXX)
git worktree add --detach "$SD" origin/spacedock-state/dev
# copy files in, commit, then push — rebasing onto whatever landed meanwhile:
pushed=no
for _ in 1 2 3; do
  git -C "$SD" push origin HEAD:refs/heads/spacedock-state/dev && { pushed=yes; break; }
  git -C "$SD" fetch origin spacedock-state/dev &&
    git -C "$SD" rebase FETCH_HEAD || break
done
if [ "$pushed" = yes ]; then
  git worktree remove "$SD"     # a cleanup failure here is not a push failure
else
  echo "unpushed commit left in $SD"
fi
```

### Lifecycle-hook state prerequisite

The detached worktree above is generic append guidance only. The `pr-merge`
startup, idle, and merge hooks do not scan or mutate entity state from a
non-holder or from a detached substitute. Before each lifecycle action — and
again after an approval pause — run this complete check as a new command:

```bash
REPO_DISCOVERED=$(git rev-parse --show-toplevel) || exit 1
REPO=$(cd "$REPO_DISCOVERED" && pwd -P) || exit 1
WORKFLOW_LITERAL="$REPO/docs/dev"
WORKFLOW_DIR=$(cd "$WORKFLOW_LITERAL" && pwd -P) || exit 1
test "$WORKFLOW_DIR" = "$WORKFLOW_LITERAL" || exit 1
STATE="$WORKFLOW_DIR/.spacedock-state"

WORKTREES=$(git -C "$REPO" worktree list --porcelain) || exit 1
HOLDERS=$(printf '%s\n' "$WORKTREES" | awk '
  BEGIN { RS=""; FS="\n" }
  {
    path=""; branch=""
    for (i = 1; i <= NF; i++) {
      if ($i ~ /^worktree /) path=substr($i, 10)
      if ($i ~ /^branch /) branch=substr($i, 8)
    }
    if (branch == "refs/heads/spacedock-state/dev") print path
  }
')
HOLDER_COUNT=$(printf '%s\n' "$HOLDERS" |
  awk 'NF { count++ } END { print count + 0 }') || exit 1
if test "$HOLDER_COUNT" -ne 1 || test "$HOLDERS" != "$STATE"; then
  echo "lifecycle requires the registered state holder: ${HOLDERS:-<none>}" >&2
  exit 1
fi
if test -L "$STATE"; then
  echo "lifecycle state path must not be a symlink: $STATE" >&2
  exit 1
fi

STATE_TOP_DISCOVERED=$(git -C "$STATE" rev-parse --show-toplevel) || exit 1
STATE_TOP=$(cd "$STATE_TOP_DISCOVERED" && pwd -P) || exit 1
REPO_COMMON_DISCOVERED=$(git -C "$REPO" rev-parse \
  --path-format=absolute --git-common-dir) || exit 1
REPO_COMMON=$(cd "$REPO_COMMON_DISCOVERED" && pwd -P) || exit 1
STATE_COMMON_DISCOVERED=$(git -C "$STATE" rev-parse \
  --path-format=absolute --git-common-dir) || exit 1
STATE_COMMON=$(cd "$STATE_COMMON_DISCOVERED" && pwd -P) || exit 1
test "$STATE_TOP" = "$STATE" || exit 1
test "$STATE_COMMON" = "$REPO_COMMON" || exit 1
STATE_BRANCH=$(git -C "$STATE" symbolic-ref --quiet --short HEAD) || exit 1
test "$STATE_BRANCH" = spacedock-state/dev || exit 1
STATE_REF=refs/heads/spacedock-state/dev
git -C "$STATE" fetch --no-tags origin "$STATE_REF" || exit 1
REMOTE_TIP=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}') || exit 1
LOCAL_HEAD=$(git -C "$STATE" rev-parse 'HEAD^{commit}') || exit 1
if test "$LOCAL_HEAD" = "$REMOTE_TIP"; then
  STATE_RELATION=equal
elif git -C "$STATE" merge-base --is-ancestor "$REMOTE_TIP" "$LOCAL_HEAD"; then
  STATE_RELATION=ahead
elif git -C "$STATE" merge-base --is-ancestor "$LOCAL_HEAD" "$REMOTE_TIP"; then
  STATE_RELATION=behind
else
  STATE_RELATION=diverged
fi
STATE_DIRTY=$(git -C "$STATE" status --porcelain) || exit 1
if test -n "$STATE_DIRTY"; then
  echo "dirty holder ($STATE_RELATION); run attributable recovery" >&2
  exit 75
fi
case "$STATE_RELATION" in
  equal) ;;
  behind)
    git -C "$STATE" merge --ff-only "$REMOTE_TIP" || exit 1
    test "$(git -C "$STATE" rev-parse 'HEAD^{commit}')" = "$REMOTE_TIP" ||
      exit 1
    ;;
  ahead)
    echo "holder has unpushed commits; run outgoing recovery" >&2
    exit 76
    ;;
  diverged)
    echo "holder and remote state diverged; run outgoing recovery" >&2
    exit 77
    ;;
esac
```

The exact `worktree`/subsequent `branch` record pairing in the exhaustive
porcelain read identifies the holder. Any zero/multiple result, different
registered path, symlink, inherited parent identity, wrong common directory,
or wrong branch stops fail-closed and reports the holder path; a non-holder does
not attach, mutate, or emulate that checkout. Cleanliness applies at the
beginning of a fresh transaction. The exact state-ref fetch and relation check
also run before every scan or outward action. A clean behind holder may move
only by fast-forward; no entity is read until its `HEAD` equals the freshly
observed remote tip. Exit 75 means the holder is dirty, 76 means clean
local-ahead, and 77 means clean divergence. Each enters the attributable
recovery below and must rerun this complete prerequisite to observed equality
before normal lifecycle work resumes.

For a non-archive state mutation, the idempotent write and its durability step
are one self-contained operation:

```bash
spacedock status --workflow-dir "$WORKFLOW_DIR" \
  --set "$SLUG" "${EXACT_FIELD_ASSIGNMENTS[@]}" &&
  spacedock state commit "$SLUG"
```

Do not rerun the clean-holder prerequisite between these two commands: the
successful `--set` is expected to make the holder dirty until its companion
commit succeeds.

On restart after `--set` but before commit, read staged, unstaged, and untracked
paths from the exact holder. The one dirty flat path, or one dirty folder's
`index.md`, is the entity-path anchor; do not discover identity by scanning
body text. Decode its unpadded-base64url `pr_artifact_v1` frontmatter value and
require canonical JSON. Product delivery is the only terminalization action,
so classification consumes only the product lifecycle markers:

- `pr_artifact_v1` must hash to the product digest in a
  `pr-merge:product-draft:v1:{digest}` or
  `pr-merge:product-pr:v1:{digest}` `mod-block`, or in its pending/numbered
  `pr` ref as applicable.
- `ledger_pr` and `ledger_artifact_v1` are legacy keys awaiting removal by the
  state migration. Preserve them exactly, including empty or malformed historical
  values, but do not decode, classify, or consume them for any decision. New
  entities do not carry them.

Require the selected decoded artifact's `live_path` to equal this anchored
index path outside `_archive/`.
The explicit `pr=direct-commit:{sha}` legacy route instead authenticates that
commit, task id, and anchored path and never invents an artifact field.
Fresh host state must independently derive the same single pending action.
For flat form, every changed path must equal that entity file; for folder form,
every path must be inside its complete entity directory. Dirty setter recovery
first attributes the dirty root to local `HEAD`. Direct rerun is permitted only
when that commit equals the freshly fetched `REMOTE_TIP`; the safe local-behind
case has the preservation and rebase-forward route below.

Do not hand-list the bytes a setter may normalize. Create a private disposable
workflow, copy this workflow `README.md`, extract the complete authenticated
entity root from `REMOTE_TIP` into its plain `.spacedock-state`, and replay the
exact intended assignment array with the same installed Spacedock 0.26 binary:

```bash
REPLAY=$(mktemp -d "${TMPDIR:-/tmp}/pr-merge-replay.XXXXXX") || exit 1
REPLAY_WORKFLOW="$REPLAY/docs/dev"
REPLAY_STATE="$REPLAY_WORKFLOW/.spacedock-state"
mkdir -p "$REPLAY_STATE" || exit 1
cp "$WORKFLOW_DIR/README.md" "$REPLAY_WORKFLOW/README.md" || exit 1
DIRTY_PARENT="$LOCAL_HEAD"
git -C "$STATE" archive "$DIRTY_PARENT" "$LIVE_ROOT" |
  tar -x -C "$REPLAY_STATE" || exit 1
SPACEDOCK_BIN=$(command -v spacedock) || exit 1
test "$("$SPACEDOCK_BIN" --version | sed -n '1p')" = \
  "spacedock 0.26.0 (contract 3)" || exit 1
"$SPACEDOCK_BIN" status --workflow-dir "$REPLAY_WORKFLOW" \
  --set "$SLUG" "${EXACT_FIELD_ASSIGNMENTS[@]}" || exit 1
git diff --no-index --quiet -- \
  "$REPLAY_STATE/$LIVE_ROOT" "$STATE/$LIVE_ROOT" || exit 1
```

Require every staged, unstaged, and untracked holder path to remain within
that one root, and require the replayed complete root to equal the actual dirty
root byte-for-byte. This exact replay deliberately accepts deterministic YAML
normalization by the supported setter — including quote/comment/spacing
normalization — while an unrelated body or frontmatter edit makes the root
comparison fail. Only an exact replay permits rerunning the same `status
--set` assignments followed immediately by `spacedock state commit "$SLUG"`.
Corrupt encoding, non-canonical JSON, wrong digest, wrong entity/`live_path`,
multiple roots, an untracked path outside the root, or any replay mismatch
blocks with the index and worktree preserved. Remove the private replay after
the verdict. An archive-shaped live deletion/archive addition goes to the
archive recovery contract instead.

An explicitly documented compound holder action uses the same rule for every
deterministic setter prefix. Terminalization is the only such action: replay
the clear-block setter as prefix one and clear-block plus terminal setter as
prefix two, both from the freshly fetched terminal-ready parent. The dirty
complete root must equal exactly one prefix output. Recovery then reruns the
complete two-set sequence and makes one state commit; it never commits a
matched prefix by itself.

If that authenticated dirty setter or compound prefix sits on a local
`HEAD` which is behind the fetched state tip, preserve intent before changing
the holder. Create a mode-0700 private temporary recovery directory outside
the repository and state checkout. Record the local parent commit, anchored
slug, task id, live index/root, action class, exact ordered assignment arrays,
authenticated artifact/ref and lifecycle preconditions, the complete dirty
root bytes, and its path/digest manifest. The assignment record is data, not
shell source, and must round-trip without evaluation. This record is created
only after the local-parent replay above has matched the dirty root exactly.
Unauthenticated dirt and dirty-diverged holders have no restore route and
remain untouched. Dirty-ahead also blocks except for the archive mod's exact
inverse-prefix recovery: local `HEAD` must be the sole authenticated signed
archive commit above the freshly fetched live remote, and staged dirt must
equal either live-root restoration alone or the complete two-root inverse
replayed from that archive parent. That bounded route idempotently finishes
the inverse and enters its separate signed two-commit recovery gate; unknown,
extra, or same-root drift remains untouched.

With that record durable, restore tracked index and worktree bytes only for the
authenticated `LIVE_ROOT` from `LOCAL_HEAD`. Remove only exact untracked paths
already enumerated, authenticated, and copied into the record; never use a
broad reset or clean, `ours`, or `theirs`. Require the complete holder to be
clean, fetch the exact state ref again, require local `HEAD` to remain its
ancestor, and fast-forward to that newly observed tip. Re-resolve the recorded
path and require the same slug and task id. Re-authenticate the same artifacts,
refs, host facts, and lifecycle source values consumed by the action. An
unrelated entity append or a change to an unconsumed field is compatible. A
deletion, move, identity change, or incompatible change to an action-read or
action-written semantic field blocks on the clean remote tip and preserves the
recovery directory; never put the saved dirty bytes back over the new tip.

For a compatible tip, seed a new disposable replay from that tip and replay
the full recorded ordered action: the single setter, or every compound setter
even when the original dirt matched only a prefix. Save its complete expected
root, run that same full sequence against the holder, and require byte-for-byte
equality with the expected supported output before making one
`spacedock state commit`. Keep the recovery directory until the exact push,
fetch, and remote-equality observation succeeds; only then remove it. A failed
commit or concurrent second advance enters the clean outgoing recovery with
the record still available.

A failed `spacedock state commit` may instead leave a clean local commit ahead
of the fetched state tip. The lifecycle mod must inspect every commit in
`REMOTE_TIP..LOCAL_HEAD`, its full path set, exact message, and the authenticated
frontmatter transition. Only one `state: update {slug}` commit, changing the
one anchored entity root exactly as one currently recognized pending lifecycle
action would have done, may be retried. Push only `HEAD` to the exact state ref,
fetch it again, and require observed equality. Unknown or multiple outgoing
commits, another path/message, or an unauthenticated transition blocks.
Archive restoration is the sole separate two-commit recovery gate: when the
remote still has the authenticated live root, it accepts only a signed archive
commit followed by its signed exact inverse, both rooted at that freshly
fetched tip. The restored tree must equal the remote tree byte-for-byte before
the pair is pushed atomically and observed. Normal archive push remains exactly
one commit; extra or unknown commits never enter either gate. Before any
rollback restores live bytes or removes an archive root, a read-only preflight
requires every dirty path inside the two authenticated roots, regular
filesystem and Git modes, an exact remote live copy, and an exact archive
comparator result. It translates the remote live Git tree to an exact relative
path-to-mode map and requires the extracted copy, present working roots, and
present index roots to match; the archive stamp is a byte-only exception and
cannot change the `index.md` mode. It independently requires the current index
tree to equal the remote tree or one exact archive/live prefix derived in a
disposable index from that validated working root. A byte, mode, special-file,
symlink, gitlink, extra index entry, or path-scope mismatch leaves the index
and worktree evidence untouched.

A terminal child whose parent is the authenticated blocked/non-terminal,
numbered-product state is recognized only as the compound terminalization
action. Seed the disposable workflow from that commit parent,
replay `mod-block=` and then the complete terminal field/ref setter, and require
the resulting complete root to equal the committed root byte-for-byte. Never
attempt or validate the terminal setter alone.

For divergence, only that same recognized outgoing commit may be rebased onto
the fetched tip; a conflict stops with both tips and the conflict preserved.
Revalidate the rewritten commit before its exact push. For compound
terminalization, seed from the rewritten commit's new parent and repeat both
setters and exact-root comparison; prior-parent evidence is insufficient.
Never use force, `ours`, or `theirs`. Archive commits use the stricter signed
two-root range contract in `pr-merge`.

Each non-archive holder mutation uses that self-contained Spacedock operation.
Archive uses the path-scoped Git transaction in `pr-merge`, because Spacedock
0.26 cannot resolve an already archived slug for `state commit` or stage both
sides of the move. Lifecycle restart state lives in the entity's digest-bound
artifacts and fields, not shell variables or locks carried across startup, idle,
merge, or captain-approval invocations.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | SD-B32 stored ID from `status --next-id --id-seed <slug>` |
| `title` | string | Human-readable task name |
| `status` | enum | backlog, ideation, implementation, validation, done |
| `source` | string | Where the task came from (captain note, defect, audit) |
| `product` | string | Required primary product for entities created under this contract. Use one plugin slug registered in `.claude-plugin/marketplace.json`, or the reserved `repo-platform` value. |
| `sprint` | string | Optional until scheduled. Once assigned, use `S<number>`; the number is local to `product`. |
| `started` / `completed` | ISO 8601 | `started` at the first transition out of `backlog`; `completed` is the authenticated product-PR `mergedAt` timestamp written by the `done` transition — later observation derives `wallclock_hours` from these durable values |
| `verdict` | enum | PASSED or REJECTED — set at final stage |
| `worktree` | string | Set on first worktree dispatch, cleared at terminal merge |
| `issue` / `pr` | string | External references; `pr` remains empty while a product draft awaits approval, then uses digest-bound pending and numbered artifact forms during hosted delivery, and historically `direct-commit:{sha}` |
| `ledger_pr` | string | Legacy key, removed from new entities and awaiting removal from the live population by the state migration. Historical values of every shape remain readable and preserved; the field authorizes and blocks nothing. |
| `pr_artifact_v1` | base64url string | Unpadded base64url of the exact canonical product approval JSON. Its decoded bytes must hash to the digest in `pr` or the product `mod-block`; blank before a product candidate exists. |
| `ledger_artifact_v1` | base64url string | Legacy key paired with historical `ledger_pr` refs, on the same removal path. Preserved verbatim; never decoded or required. |
| `mod-block` | string | Non-empty lifecycle guard. Product drafts use `pr-merge:product-draft:v1:{digest}`; explicit approval transitions the same artifact to `pr-merge:product-pr:v1:{digest}`. Only authenticated product delivery clears this guard for terminalization. |
| `design` | enum | `required` or `trivial-pass` — set at ideation, or, for a `lane: defect` task that has no ideation stage, at the moment the FO classifies it into that lane. Empty during seed capture and through `backlog`; on the main line it is produced inside `ideation`, so the invariant starts at the ideation gate — never empty at that gate, and never empty in `implementation` or later |
| `lane` | enum | `defect` or `main` — the FO's Defect-lane classification, written when the FO routes the task out of `backlog` (not at seed capture, which authors no classification), so it is queryable (`status --where lane=defect`) instead of re-derived by re-reading every body. `defect` asserts all four conditions in the Defect-lane section hold |

### Product-local sprint identity

The task frontmatter carries one scalar `product`, not a list. Plugin product
values come from the `plugins[].name` slug registry in
`.claude-plugin/marketplace.json`; `repo-platform` is the reserved non-plugin
value. The current registry snapshot is:

- `kc-pr-flow`
- `e2e-pipeline`
- `kc-nightwatch`
- `kc-hyperfocus`
- `kc-team-ops`
- `kc-plugin-forge`
- `kc-dev-flow`
- `repo-platform`

Update this convenience snapshot in the same change that registers a plugin.
Choose the plugin that owns the task's primary outcome. A single-plugin outcome
stays with that plugin even when its implementation touches shared files. A
multi-plugin primary outcome, or an outcome in shared CI, marketplace behavior,
root configuration, or this workflow's schema, belongs to `repo-platform`. Do
not split one outcome into artificial plugin tasks solely to avoid
`repo-platform`.

Sprint numbers are product-local ordinals. They carry no chronology or rank
across products. The stable identity is the pair (`product`, `sprint`), so
cross-product plans and reports use a qualified label such as `kc-pr-flow/S5`
or `e2e-pipeline/S1`. A bare `S1` is meaningful only inside one product section.
Backlog capture requires `product`, while `sprint` remains blank until the
captain or sprint commander schedules the entity:

```yaml
product: kc-pr-flow
sprint: S5
```

These fields are queryable through the normal status filter:

```bash
spacedock status --workflow-dir docs/dev --where 'product=kc-pr-flow'
spacedock status --workflow-dir docs/dev --where 'product=e2e-pipeline'
spacedock status --workflow-dir docs/dev --where 'product=repo-platform'
```

Spacedock 0.26 stores and filters arbitrary frontmatter; it does not validate
the product registry, scalar shape, or requiredness. This repository therefore
binds the optional
[`work-control-profile`](./_mods/work-control-profile.md) capability
`bound_field_validation` to
`scripts/dev-flow-work-context-check.py`:

```yaml
work_controls:
  bound_field_validation:
    mode: required
    adapter: scripts/dev-flow-work-context-check.py
    authority: captain or designated state migration owner
    enforcement:
      - backlog capture before state commit
      - every state-transition review
      - before claiming a product or sprint filtered view is authoritative
```

No other profile capability is declared by this binding. Delivery
reconciliation, landing metadata preview, resource envelopes, and review
convergence remain separately adoptable follow-up controls, not implicit gates.

After the lifecycle-hook state prerequisite has established the clean holder,
validate the exact live task at capture and every transition review:

```bash
python3 "$REPO/scripts/dev-flow-work-context-check.py" validate \
  --task "$TASK_FILE" \
  --marketplace "$REPO/.claude-plugin/marketplace.json" \
  --roadmap "$REPO/docs/dev/ROADMAP.md"
```

`TASK_FILE` is the exact flat task file or folder-form `index.md` selected for
the operation. Exit 1 is a controlled-field `FAIL`; exit 2 is `UNKNOWN` because
a provider input could not be established. Both block a required boundary. The
JSON receipt hashes the exact task, marketplace registry, and roadmap bytes
into `input_revision`, so an edit invalidates the old result.
When a legal setter adds or changes `product` or `sprint`, run the validator on
the resulting exact task before its companion state commit. A failure leaves
the one attributable dirty entity for correction under the existing setter
recovery rules; it never authorizes committing invalid fields.

The blank `product:` and `sprint:` values in the Task Template are authoring
placeholders, not a valid captured seed. `product` must be filled before
capture completes; `sprint` may remain blank after validation.

This contract change does not authorize a bulk rewrite of separated state.
After it lands:

1. One designated state migration owner may backfill inactive backlog entities,
   adding `product` and adding `sprint` only where scheduling already exists.
2. The owner of an active entity adds the fields at that entity's next legal
   state transition; the migration owner does not rewrite it underneath that
   session. For a parked or abandoned active entity, the original owner
   annotates before handoff or closeout; after that owner releases it, a
   captain-designated owner may take over and annotate at the next legal state
   transition. For a terminal `done` entity that still resides in the live
   state path, its closeout or archive owner either annotates it before archive
   or archives it first; the migration owner does not rewrite it or bypass its
   holder.
3. Product backfill is complete when every non-archived entity has a non-empty
   scalar `product` recognized by the registry above.
   Only after that condition holds are product-filter results authoritative;
   before then they omit unannotated entities.
4. Sprint-assignment migration is complete when every non-archived entity
   scheduled under a ROADMAP product sprint has the matching scalar `product`
   and `sprint` pair. Sprint-filter and combined product-plus-sprint query
   results become authoritative only after that condition holds. A genuinely
   unscheduled entity keeps `sprint` blank.
5. Archived entities are a separate, optional historical migration and need
   not be backfilled. A terminal `done` entity still in the live path must be
   annotated or archived by its closeout or archive owner before product-filter
   authority can be declared.

The complete-population audit makes those authority boundaries executable:

```bash
python3 "$REPO/scripts/dev-flow-work-context-check.py" audit \
  --state-dir "$STATE" \
  --marketplace "$REPO/.claude-plugin/marketplace.json" \
  --roadmap "$REPO/docs/dev/ROADMAP.md"
```

The audit requires the exact clean Git worktree root on
`spacedock-state/dev`, requires its Git common directory to equal the
marketplace/roadmap code worktree's common directory, verifies its revision
before and after the read, excludes `_archive/`, hashes the exact live
population it read, reports deterministic JSON, and derives
`product_filter_authoritative` from complete valid live coverage. A wrong
directory or repository, branch, dirty holder, or changing revision is
`UNKNOWN`. It does not
infer that every blank sprint is intentionally unscheduled. Only the captain
or designated migration owner may add `--iteration-migration-complete` after
checking ROADMAP scheduling coverage; invalid live fields still keep
`iteration_filter_authoritative` false. Until the relevant boolean is true, a
product- or sprint-filtered result is advisory and must say that it can omit
unmigrated entities. An empty state root is `UNKNOWN`, not a vacuous
authoritative pass. The command is read-only and never authorizes a bulk
rewrite.

## Proof Policy

Inherited from the spacedock proof discipline; the rules below are binding
in every stage report and every gate review. Numbered, not counted in the
lead-in — a count in prose goes stale the first time one is added, and this
one has already been wrong twice: it said "four" while five existed, then
"seven" until this rule was added.

1. **No prose-grep, and provenance decides independence.** A string match
   over an instruction file the model reads never proves a behavioral claim.
   A grep may serve as one-off evidence for an existence fact in a validation
   report; the same grep committed as a test is banned. Not because it can
   never go red — rewording the matched line, moving the file, or changing the
   pattern all do that — but because **nothing about the behavior can**. It
   reads text. A regression that leaves the wording intact passes straight
   through it, and a rephrasing that broke nothing turns it red: it is
   uncorrelated with the thing it was committed to catch, in both directions.
   The falsifier is an edit to behavior alone that reddens it, and there is
   none. And
   a check the author wrote to grade the author's own artifact is a self-issued
   stamp, not a gate. This is about what closes a gate, not about who may write
   a test: the worker's own RED-before-GREEN tests are exactly the evidence
   this workflow asks for, and they become insufficient only when they are also
   offered as the independent verdict on themselves. Independence at a gate
   comes from the fresh-context validator and the cross-model pass, never from
   the artifact grading itself.
2. **Evidence must be able to fail.** Each AC's cited evidence names the
   concrete change that would flip it. If the author cannot name the
   falsifying edit, the criterion does not count.
3. **Prove behavior by exercising it.** Output bytes, exit codes, resulting
   on-disk state, a browser actually driving the flow. Unit tests prove logic;
   they do not prove wiring. Seam-level claims need runtime or E2E evidence.
4. **Trace every mechanism to value.** Any new mechanism names the value AC it
   serves, the simplest alternative considered, and why that alternative is
   insufficient. A test harness orchestrates and observes the supported
   runtime; it never becomes a second implementation of the system under test.
5. **Automatic must-pass behavior checks live at stage boundaries, never in
   the worker's inner loop.** Hooks that fire on every commit/edit inside a
   work session are limited to fast mechanical checks (format, lint,
   typecheck). Behavioral or corpus/consistency checks, *as must-pass gates*,
   belong to the validation gate and CI: a must-pass check inside the inner
   loop turns "implement the behavior" into "make the check shut up", and the
   worker will drift the implementation — or the check's inputs — to satisfy
   it. This governs checks the tooling forces, never tests the worker chooses
   to run: RED-before-GREEN requires running the behavior's own tests inside
   that loop, and that is the mechanism working, not an exception to it.
6. **A claim must be able to fail, and it is checked when written.** An
   absolute — "exactly", "only", "always", "never", "cannot", "byte-for-byte"
   — written into a reference, a code comment, or a commit message either
   names the enforcement point that makes it true, or is rewritten as the
   bounded claim the code actually supports. This is rule 2 applied to prose:
   the same discipline an AC's evidence gets, because a documented guarantee
   *is* a claim and the next reader builds on it.
   **An enforcement point is what makes the absolute true, not who believes
   it.** The permission check, the schema constraint, the branch that cannot
   be reached, the script that fails closed — those are enforcement points.
   "I checked" is not one, and neither is the author. Where no such mechanism
   exists the absolute is not defensible, and gets rewritten as the bounded
   claim that is. Two consequences worth stating outright.
   **This rule is itself a discipline, not a mechanism, and it does not claim
   otherwise** — nothing checks it automatically, which is why it binds at
   authoring time as something the writer applies rather than a gate someone
   else runs. The validation-stage clause is the backstop for what slips
   through, and a backstop that fires every time is a cost, not a control.
   **Coverage past the author is uneven — and the distinction is read, versus
   checked.** A reference or doc diff reaches validation, which has a clause
   aimed squarely at its guarantees. A code comment reaches validation only
   incidentally, inside a diff a reviewer happens to read closely. A commit
   message is *read* by tooling here — `kc-pr-review` parses issue IDs out of
   it — but by nothing that evaluates a claim in it. So all three get read at
   some rate, and only the first has anything downstream that would test an
   absolute. The thinner that coverage, the more the authoring moment is the
   only moment — four of these shipped in two days, and the two nobody caught
   until later were a commit message and a comment, which are exactly the two
   thin cases. A claim inherited from a report, a reviewer, or an external
   contributor is not exempt — adopt it only after checking it, and say which.
7. **A negative result is a claim, and carries the same bar as a positive
   one.** "The search found nothing" is evidence about the search. "The file is
   unchanged" is evidence about the file, not about the failure. A number
   measured while you were perturbing the system is evidence about the
   perturbation. Before reporting an absence — no such skill, no such caller,
   nothing tracked, not a regression — name the scope actually searched and why
   that scope is the population, or run a second strategy that would have found
   the thing if it existed: one tool, one pattern, one filter is a sample, not a
   census. In this repo the sampling trap is concrete — a plugin's behavior can
   live in `skills/*/SKILL.md`, an `agents/*.md`, a hook script, or the local
   install under `~/.claude/plugins/`, so a single `grep` over one plugin
   directory is never the population. And an unexplained signal is traced, never
   assigned an invented origin — "probably another session" is a story, not a
   cause.
8. **Before trusting what a check found, confirm the check can fail.** A probe
   that silently returns a plausible result where it should have errored is
   worse than no probe, because its output reads as a conclusion. Two shapes
   seen here: a spot-check edit whose target string did not exist, so "the
   suite stayed green" meant the edit never happened rather than that the guard
   was missing; and a section counter that read headings inside fenced code,
   inventing a 742-line region that was not there. Run the check against a case
   it must flag before running it against the case you care about — its silence
   carries information only after you have seen it speak.

## Stages

Every stage report opens with a one-paragraph TL;DR; raw command output,
full diffs, and re-derivations go in collapsed or linked sections. A report
that reads like a session transcript costs reading budget nobody spends.

### `backlog` — capture (this is the todo queue)

Any idea, rabbit hole, defect, or captain note enters as a seed task file:
title, `source`, `product`, and a one-paragraph description. Leave `sprint`
blank unless the task is already scheduled. Target cost: under two minutes.
Capturing a seed triggers NO design work — the gate is where the captain
curates what advances. A seed too vague for the captain to triage is the only
"bad" here.

#### Defect lane — skip `ideation` for a bounded fix

A known defect with a mechanical acceptance test does not need a design stage.
When **all four** hold, the FO advances `backlog → implementation` directly. The
verdict goes in the `lane` frontmatter field so it is queryable, and its
justification in the task body — a classification that lives only in prose gets
re-derived by re-reading every open task, which is the expensive way to learn
something already decided:

1. The root cause is already identified and cited at `file:line`.
2. Acceptance is mechanical — a test that fails before the fix and passes after.
3. It is a single seam: one surface, no cross-layer ripple, no schema change.
4. No design decision is open. If the fix has two defensible shapes, it is not
   in this lane.

Everything else still applies: RED-before-GREEN, the proof policy, the
validation stage, and the merge bar. **The lane removes a design stage, never
verification** — and a defect whose fix turns out to need a design decision
goes back to `ideation` rather than being decided inside implementation.

The lane removes the stage, never the stage's outputs. Ideation produces four
things later stages read back — a design determination, the ACs validation
checks against, the appetite and tolerance the correction-round budget measures
against, and the implementation dispatch sizing — so **the FO writes all four
when it classifies the task into this lane**: `design: trivial-pass` reasoned by
the fourth condition above, one AC that is the mechanical test named by the
second, a one-line estimate with its tolerance, and the sizing (for a bounded
fix, one dispatch, unless the classification says otherwise). That record is the
lane's ideation of record; every clause elsewhere that says "the
ideation-declared X" reads it here. The lane's AC bar is that mechanical test
alone — a bounded fix restores behavior rather than delivering new value, so the
value-AC requirement does not apply, and a defect that needs one is not a bounded
fix and belongs in the main line.

**`design: trivial-pass` here does not contradict the ideation clause that makes
`design: required` mandatory for a UI, contract, interface, schema, or visual
surface.** That list asks whether the task *decides* something about the surface,
not whether it touches one. A bounded repair restores behavior the surface
already documents and decides nothing, so `trivial-pass` is the accurate
determination even when the seam is a UI or a contract. A fix that would change
the surface's shape has an open design decision by definition, which is condition
four failing — so it was never in this lane, and the `required` clause reaches it
in `ideation` where it belongs. If the two readings ever seem to both apply, that
is the tell that condition four is not actually satisfied.

**This attaches to the classification, not to capture.** Seed capture stays what
the `backlog` clause says it is: title, `source`, one paragraph, under two
minutes, no design work, `lane` empty. The four outputs are owed at the moment
the FO advances `backlog → implementation`, which is the moment the task skips a
stage — and a task advanced into this lane missing any of the four is not in it:
that advance is returned for the same reason an ideation gate without a design
determination is returned unread.

Any of the four failing means the main line. When in doubt it is the main line;
the cost of over-shaping one fix is smaller than the cost of designing inside
an implementation stage nobody is reviewing for design.

### `ideation` — one gate for design, plan, and acceptance

The single judgment-heavy stage. Flesh out the problem, decide the approach,
define acceptance criteria and the test plan. The gate reviews all of it at
once. Discipline clauses:

- **The captain authors scope; the agent never infers it for a
  rubber-stamp.** For non-trivial tasks, open ideation by asking the captain
  a few short scope questions (what gets worse without this; the time
  budget; what to keep if forced to cut; what we are happily NOT doing;
  which assumption could be wrong) and compose Problem/Scope from the
  answers verbatim. Skip only with a stated small-scope reason.
- **Appetite is a forcing budget.** Record a time/scope budget in the task
  body, plus the deviation past which the work stops and gets re-cut rather
  than continuing. Those two numbers are the "ideation-declared estimate" and
  the "declared tolerance" the validation stage's correction-round budget
  measures each rework round against; a task that declares neither has nothing
  for that brake to read. When work is about to exceed it: cut scope (defer a
  sub-part to backlog) or park cleanly with re-enterable state and explicit open
  findings — never extend the budget silently, and never compress
  validation to land inside it. Size or budget variance is a drift signal
  to investigate, never a number to hit by padding artifacts or stripping
  tests.
- **The cheapest path that satisfies the AC is the default, and the gate is
  told which one it took.** Ideation answers two questions in the task body
  before choosing an approach: *what is the fastest path?* and *what is the
  smallest cut?* It then records the cheaper option it is taking, the more
  thorough option it is not taking, and why the difference is not needed to
  satisfy the AC. **Default to the cheap one.** This is a scope default, never
  a quality one — the proof policy, the AC bar, RED-before-GREEN and the
  validation stage are untouched, and "cheap" never means thinner evidence.
  **Two cases, and they route differently.** When the cheaper option is a
  different way to satisfy the same ACs — fewer moving parts, a narrower
  mechanism, an existing seam instead of a new one — nothing is being cut, so
  the FO surfaces it at the gate in one line ("taking the cheap path: X") and
  proceeds. When the cheaper option **defers or drops a sub-part** — anything
  phrased "deferring Y" — that is a scope cut, and Gate Authority gives scope
  cuts to the captain alone: it is escalated for an explicit answer, not
  presented for a silent override. A cheap path taken silently is the agent
  authoring scope, which the clause above forbids — and an expensive path taken
  by default is the more common and more expensive mistake, because nobody is
  ever asked to approve it.
- **One-sentence pre-mortem.** Before the gate: "if this ships exactly per
  spec and still fails, the most likely cause is ___" — pick one of {wrong
  problem, criteria that pass without delivering value, wrong framing lens,
  hidden assumption, over-conviction}. This is an orthogonal
  future-failure check the AC rubric structurally cannot generate.
- **Design determination is mandatory, never skipped.** Every task records
  `design: required` (the task **decides** something about a UI, contract,
  interface, schema, or visual surface — its shape, not merely its behavior;
  attach the concrete design decision: wireframe reference, API shape,
  before/after) or `design: trivial-pass` with a one-line reason. **Touching
  such a surface is not the trigger; deciding about it is** — a repair that
  restores behavior the surface already documents decides nothing and is a
  `trivial-pass`, which is what lets the Defect lane classify a single-seam UI
  or contract fix without contradicting this clause. An ideation gate presented
  without a design determination is returned unread.
- **Reverse-recovery audit before any "build/add X"** (brownfield default):
  assume the abstraction may already exist. Layer-trace the path (UI →
  contract → handler → domain → persistence → readback) and classify each
  layer WORKING / EXISTS_BROKEN / STUB / MISSING with file:line. Greenfield
  is allowed only after proof of absence (multi-strategy, multi-language
  search) — the general bar for any absence claim is Proof Policy rule 7.
  A single broken seam means repair scoped to that seam, not a
  rebuild. Full procedure: `_mods/reverse-recovery-audit.md`.
  **Audit against the merge target** (fetch `origin/<trunk>` first), never
  only the working branch — a stale branch shows stale infrastructure, and
  a MISSING verdict read off it can be seven weeks wrong. Implementation
  re-verifies the audit's load-bearing MISSING claims against a fresh
  merge target before building, and escalates instead of building when a
  premise has collapsed.
  **Enforcement facts are read live, never inferred from repo files**: what
  CI actually requires comes from the platform API
  (`gh api repos/iamcxa/kc-claude-plugins/branches/main/protection`), not from
  reading `.github/workflows/`. Most workflow files here are *not* required
  checks, and the required contexts are matched by the **job `name:` string**.
  Adding steps to a required job is identity-safe. Renaming the job does not
  loosen the protection — it **wedges** it: branch protection still requires the
  old context, nothing reports it any more, and the PR sits at "Expected —
  waiting for status to be reported" until either the old name is restored so
  something reports that context again, or the protection is edited to require
  the new one. So a job rename is a change to the merge rules, which
  Judgment Escalation puts on the captain. And the symptom to look for is the
  *missing* context, not a red one: the renamed job still runs and can fail on
  its own merits, but nothing goes red merely because the required context
  stopped being reported — which is why this is caught by reading the
  protection rather than by watching the checks.
  The live-read matters more than usual in this repo because a required check's
  display name can outlive what it checks: the parity context still names the
  README even though per-plugin version badges were retired from it.
- **AC are end-state properties with falsifiable proof.** Each AC names a
  property of the finished task (not a stage action) plus a `Verified by:`
  clause citing proof outside the task's own prose. At least one AC measures
  the end value the task exists for, against a baseline that can move the
  wrong way.
- **Run `status --read <ref> --ac-scan` before presenting the ideation gate;
  every AC must resolve.** The extractor is line-based, so a
  `**AC-N — …**` heading whose bold span wraps onto a second line is invisible
  to it — and house style wraps prose near 95 characters, so a long property
  statement hits this by accident. Keep the bold heading short enough to open
  and close on one line and put detail in the body underneath. This is not
  formatting hygiene: the gate's AC cross-check reads that extractor's output,
  so an unparsed AC set gives the cross-check nothing to anchor against and it
  passes by absence. Three sprint-1 tasks shipped ideation with ACs invisible
  this way, each found only downstream.
- **E2E-first acceptance.** When the task changes full-stack or user-visible
  behavior, at least one AC is verified by exercising the real flow end to
  end (browser drive, CLI invocation, service round-trip). Unit-only proof is
  insufficient for wiring claims. Skip only for docs/config/CI-only tasks,
  and record the skip reason.
- **Doc diff proposed here.** When the task changes behavior that PRODUCT.md,
  ARCHITECTURE.md, or any published doc describes, ideation proposes the
  concrete doc diff (before/after wording) in the task body. The gate reviews
  it; implementation applies it; validation verifies behavior diff and doc
  diff landed together.
- **Spike the riskiest unverified mechanism first**, and record the result in
  the task body — or record "no spike needed: {proven mechanisms relied on}"
  so the determination is auditable.
- **Size the implementation dispatch here.** Default is ONE worker session —
  every extra dispatch pays a cold-start (re-reading the README, task body,
  and surrounding code). Split only when the estimate exceeds ~90 minutes,
  the work has 3+ independent behaviors, or parallel worktree lanes buy real
  wall-clock — and always split along behavior boundaries, each slice a
  complete RED→GREEN loop (never "tests in one dispatch, code in the next").
  Record the sizing decision in the task body so implementation inherits it.

### `implementation` — build in a worktree, test-first

- **RED before GREEN, with evidence.** For each behavior: write the failing
  test, run it, record the RED evidence in the stage report (test name +
  failure output digest), then write the minimum code to pass. GREEN without
  recorded RED is treated by validation as unproven — tests written after the
  fact to confirm existing code do not count.
- **Count new assertions against the RED output.** Every assertion added must be
  *able* to appear as a failure in that run. A case stops at its first failing
  assertion, so later assertions in the same case never execute — compare failing
  *cases* against the cases that should fail, and for the rest ask per assertion
  whether any RED run could reach it. An assertion reachable in RED and green
  anyway holds in the pre-fix world too, so **as evidence for the behavior** it
  is decoration — rewrite it to pin the literal expected value, or delete it.
  The exception is the assertion that is not claiming the behavior: a
  precondition or arrangement check, green by construction in both worlds,
  exists to prove the case exercised what it says it exercised, and deleting it
  makes a later green less trustworthy, not more. Keep those, and say in the RED
  record which they are — an unlabelled green assertion is read as a claim about
  the behavior. This is the mechanical enforcement of "evidence must be able to
  fail"; the RED record aims at it but does not check it, and the tell is an
  added behavior-claiming assertion no RED run can reach.
- **When you change a behavior, audit the tests that arrange the old one.** A
  suite that goes green after a behavior change can mean a fixture was silently
  re-purposed rather than that coverage held. Grep the suite for scenarios that
  *set up* the behavior under repair, and state per scenario whether the edit
  restored its original intent or quietly narrowed it.
- **Name what CI will do differently, before pushing.** Local green is a fact
  about your machine. Two failures here came from that gap and a third case is
  documented as a hazard that has not bitten yet; each has its own cheap
  check — run the one the diff earns, not all three:
  - *Tests added, or materially slowed* → measure the job's remaining margin.
    Job-level cancellation presents as a red check with **no failing
    assertion** — every suite reports passing and the step is killed anyway —
    which reads like a flake and invites a retry instead of a diagnosis. Thin
    margin is a gate-level disclosure, not a CI discovery.
  - *Behavior that depends on OS, libc, locale, or clock* → run that check on
    CI's OS family. A differential's Python reference rendered year 1 as
    `0001` on this macOS and `1` on glibc, so the suite read 139/0 locally and
    red on CI.
  - *A file governed by a CI-pinned tool* → run that exact version, not the
    local one. A newer local ShellCheck retires checks CI still enforces
    (`kc-pr-flow/CLAUDE.md`). This is the documented case, not the bitten one:
    unlike the two above, no red CI here has been traced to it.

  What this is **not**: a general "reproduce CI locally" obligation. The job
  runs on mutable `ubuntu-latest`, so a local container reproduces the
  platform and never the job — setup time, runner speed, and the job-wide cap
  are not in it. Exact-head CI remains the merge authority; this clause only
  moves a predictable red into the minute before the push.
- **RED and GREEN close in the same session, and commit together.** Never
  commit failing tests as a handoff contract for a later worker: an agent
  handed a red suite optimizes for "make it green", and will drift the
  implementation to fit a possibly-wrong test — or the test to fit the
  implementation — instead of delivering the behavior. The RED record is
  stage-report evidence; committed tests arrive with the code that passes
  them. If a session must stop mid-loop, the unfinished RED work stays
  uncommitted and the stage report says exactly where the loop stopped.
- **Scoped tests in the loop, full suite plus ripple at the exit.** During the
  build loop run only the tests scoped to the behavior under change (file,
  module, or tagged subset). Run the full suite once, after scoped
  tests are green, as the stage-exit regression check — not on every
  iteration. Once is the *entry* count, not a cap: a failure that run surfaces
  is fixed and the suite re-run, because the exit condition is a green
  full-suite run on the code being handed over, and a rule that forbade the
  second run would trade the regression for the ceremony. For a change to a surface something else reads, also run the checks
  that actually consume *that* surface — they are not interchangeable, so run
  the ones the diff earns, not all of them:
  - a version value or propagation target — `<plugin>/.claude-plugin/plugin.json`,
    `<plugin>/.codex-plugin/plugin.json`, a `marketplace.json` version string,
    `release-please-config.json`, `.release-please-manifest.json` →
    `scripts/version-parity-check.sh`, which is the required check and the only
    one that reads the release config.
  - `marketplace.json` structure — an added, removed, or retargeted entry, a
    changed `source` → `scripts/marketplace-verify.sh` (schema + clean-`HOME`
    installability).
  - a `*/skills/*/SKILL.md` frontmatter block →
    `scripts/skill-frontmatter-lint.sh`.
  - adding or removing a plugin directory → `version-parity-check.sh` *and*
    `marketplace-verify.sh`, since parity fails closed on a directory with no
    marketplace entry and vice versa, and the entry also has to resolve.
  - a workflow under `.github/workflows/` → no local script validates these;
    the check is the live run, so say in the stage report which workflow was
    touched and whether it is a required context (read it live, per the
    ideation clause).
  **The exit condition is never "the reported error is gone."** That is a
  not-a-regression claim and Proof Policy 7 governs it: the one spec that named
  the bug was never the population. A failure surviving the exit run is written
  off as pre-existing only by the per-failing-line rule the validation stage
  states — never per file, never per impression.
- Minimal diff that satisfies the AC. No unrelated refactoring. Apply the doc
  diff approved at ideation in the same branch.
- The deliverable must be self-contained for a fresh validator: stage report
  says what was produced, where, and how to run it.

### `validation` — fresh eyes, adversarial by default

A fresh-context agent verifies the deliverable against the ideation AC. The
validator checks what was produced; it never finishes the work.

The gate is presented with a filled **evidence block** — one line of *specific,
falsifiable* evidence per item (presence of text is not the bar), and anything
left blank counts as not-done, never a silent pass. It records five lines —
`Lenses:` (the diff classification, and per fired lens its verdict and finding
count), `Diff coverage:` (the measured %), `Adversarial:`, `Cross-model:`,
`E2E:` — each naming what was actually run and what it returned.

**A field whose own clause permits a skip is written `N/A — <why>`, never a bare
`N/A`.** A skip without its reason and a skip with one do not read alike. Three
fields have such a clause — `Adversarial:`, `Diff coverage:`, `E2E:`; `Lenses:`
and `Cross-model:` have none and are therefore never `N/A`. **The condition that
permits the skip lives in that field's own clause, and is not restated here** — for
`E2E:` that is the E2E-first acceptance clause at ideation; for the rest, the
validation clauses in this section. Only two are set here, because nowhere else
states them: `Adversarial: N/A — <why>` for a diff with no behavioral guard to
break, and `Diff coverage: N/A — prose-only diff, no executable surface` for the
markdown-only diffs that are this repo's common case (the coverage clause below
scopes what counts as coverable). `Lenses:` and `Cross-model:` are never `N/A`.
Scale changes how deep each item goes, never whether it runs — this block is
where an agent is tempted to convert "small" into "skipped", and small is not a
skip condition for any of the five. A gate presented without the block is
returned unread — the same bar the ideation stage's design determination is held
to.

**A round fills its field only when it names what it read and what would have
failed it.** Two facts, appended to whichever of the five the round belongs to:

- **What it read** — the exact ref or revision and the path. `origin/main`, a
  stale buffer, a base commit, and this worktree are four different artifacts,
  and a round that read the wrong one produced a verdict about something other
  than the change under review.
- **What would have failed it** — the named claim, AC, or lens the round was
  checking, and the concrete change to *that* which would have flipped the round
  to a finding. This is Proof Policy #2 — "if the author cannot name the
  falsifying edit, the criterion does not count" — applied to the verifying round
  rather than to the criterion. A falsifier that bears on nothing the round was
  checking satisfies the letter and reports nothing: naming a token whose
  presence would have failed the round says only that the round could read.

A round missing either fact leaves its field **not-done**, which this block
already routes: anything left blank counts as not-done, never a silent pass, and
a gate presented without a filled block is returned unread. That is the whole
enforcement point — there is no separate penalty, and nothing downstream reads a
"counted" flag.

This adds no permission. Nothing here lets a required round be skipped, the
cross-model gate's own clause still governs when it is owed, and no check the
author runs substitutes for the independence that clause supplies. It changes
only whether a round that already happened fills the field it was run for.

The first fact is the one this fleet keeps paying for, and it is cheap to state
because the verifier already knows it. Observed across sibling repositories: a
reviewer reading a tree 85 commits behind, a re-review that checked out the base
commit instead of the PR head, a required CI job that resolved to `main` rather
than the branch under test on two separate runs, a relative test path that ran a
same-named file in a different worktree and reported green, and editor
diagnostics that were false three times out of three because the buffer resolved
worktree files against `main`. None of these is a reviewer being insufficiently
rigorous. Each is a rigorous verdict about the wrong bytes, and each was caught
by a side channel rather than by the round itself.

The second fact is what separates a gate that aims from one that only passes. A
verifier that cannot fail returns output at a rate set by its prompt rather than
by the artifact, so its silence is not evidence of correctness — and neither is
its confidence. Where a round cannot name its falsifying result, prefer a check
that can: a mutation that reddens a suite is a stronger claim about a guard than
any reading of it, and it is usually the cheaper one to run.

- Reproduce each AC's `Verified by:` clause; report PASS/FAIL per criterion
  with actual evidence (command output, screenshots, on-disk state) — never
  the implementer's self-report. Same execution order as implementation:
  scoped checks per AC first, one full-suite run at the end — a full-suite
  failure outside the diff's blast radius is reported as context, not
  debugged by the validator.
- **Lens selection is mechanical, not a judgment call.** Classify the diff and
  fire every matching lens; a "touches none" is justified by naming the surfaces
  the diff *does* touch (so a reviewer can check the classification — not by an
  adversarial revert, which tests code, not a skipped lens). Correctness always
  fires; then, by what the diff touches: **security** (auth / permission / trust
  boundary, a hook that runs shell, a workflow with secrets) · **silent-failure**
  (error handling, input validation, fallbacks, swallowed errors) ·
  **type-design** (a new or changed type) · **concurrency** (locks, async
  ordering, shared/mutable state) · **resource-lifecycle** (processes, handles,
  memory, unbounded growth) · **manifest/back-compat** (a change to
  `marketplace.json`, a `plugin.json`, skill frontmatter, or any other contract
  an already-installed copy reads — does an existing install still resolve?).
  The independent cross-model gate (below) always runs and is recorded
  separately; it is not one of these lenses. For prose diffs (skills, agents,
  hooks-as-instructions) — this repo's common case — the correctness lens is
  **exercise-based**: actually invoke the changed skill/hook and observe
  behavior, applying `kc-plugin-forge`'s audit discipline. A prose change
  reviewed only by reading is not reviewed. (Reviewer agents, fully qualified so
  the identifier can be dispatched as written:
  `pr-review-toolkit:code-reviewer`, `pr-review-toolkit:silent-failure-hunter`,
  `pr-review-toolkit:type-design-analyzer`, `kc-pr-flow:tob-security-reviewer`,
  `kc-pr-flow:tob-actions-auditor` for workflow diffs.)
- **A documented guarantee is a claim, and gets the AC treatment.** When a doc
  diff states an absolute — "only", "always", "never", "exactly one" — name the
  input or edit that would falsify it, and check it, exactly as an AC names its
  falsifier. A guarantee the enforcement point does not make is a defect **in
  the doc even when the code is correct**, and a worse one than an undocumented
  gap, because the next reader builds on it. Validation verifies doc *claims*,
  not just doc presence.
- **Verify reviewer citations before acting on findings.** Check every cited
  `file:line` against the actual file — LLM reviewers fabricate plausible
  citations. If more than roughly a third of one reviewer's citations are
  wrong, discard that reviewer's entire round rather than triaging it. And
  when writing off a failure as pre-existing, prove it per failing line
  (blame against the change's commit range), never per file or surface — and
  never from a run whose conditions you were perturbing yourself.
- **Converge by naming residuals.** When a review round's findings stop
  being fixable defects and become a named class the chosen approach
  genuinely cannot solve, stop iterating: record the residual and its
  acceptance reason instead of opening another round. Chasing irreducible
  residuals is gold-plating dressed as rigor.
- **Cross-model gate before merge approval**: run one independent cross-model
  review of the diff. **Cross-vendor is relative to the model running the gate**,
  not a fixed list: pick the first available tool from a different vendor than
  the reviewing model — from a Claude session that is `codex` → `agy`, from a
  codex session it starts at `agy`. A lighter variant from the same family is
  not a second vendor and does not satisfy this. No single vendor is required,
  but skipping the second opinion entirely is not. **Unavailability is
  established by an attempted run that failed** (quota, auth, missing binary),
  never assumed — record which model ran the gate, which reviewer ran, and when
  a preferred one was skipped, the observed failure. A P1 finding is fixed or
  explicitly waived with a recorded reason at the gate — never silently dropped.
- Exercise the E2E AC in the real runtime. Whether the task owes one at all is
  decided by the E2E-first clause at ideation, not here.
- **Coverage is a ratchet, not a target — scoped to executable code only.**
  This repo is prose-heavy: coverage applies ONLY to executable surfaces
  (scripts/, hooks, MCP/server code), where lines added or changed by a task
  meet an 85% bar via a diff-coverage check (the bootstrap task decides the
  tooling). Markdown skill/agent bodies are n/a-by-design — their proof is
  exercised behavior (a real invoke per the E2E clause), never coverage. A
  red coverage check on an executable diff is fixed or explicitly waived at
  the gate with a recorded reason; coverage percent is never an AC by itself.
- **Adversarial spot-check.** For one or two core behaviors, make a
  claim-breaking edit (revert a guard, flip a boundary) in a scratch copy and
  confirm the suite goes red. A suite that stays green under a claim-breaking
  edit is a hole — route back with that evidence.
- **Live-CI red evidence short-circuits per step.** When an AC requires proving
  a required check actually fails on bad input, use a non-draft probe PR
  observed red on live CI — and plan one probe commit per step: steps within a
  CI job short-circuit, so a single red run proves only the first failing step,
  and proving N steps each go red takes N sequential probe commits. Close the
  probe PR without merging, delete its branch, and record the run URLs as gate
  evidence.
- Rejection routes back to implementation (`feedback-to`) with concrete,
  file-anchored fixes. A second consecutive rejection at this gate ends the
  loop and goes to the captain, per Gate Authority. **The trigger is the count,
  not the findings** — a cycle that closes every prior finding and immediately
  surfaces new ones on adjacent surfaces is the stronger stop signal, not a
  fresh start: the approach cannot hold the boundary, and the next cycle finds
  the next surface. Counting only repeated findings never fires on that case,
  and it is the common one.
- **Every correction round carries a budget record.** Each rework round
  appends one entry: the round's actual effort against the ideation-declared
  estimate, the deviation, and the findings disposition. Past the declared
  tolerance, record a design-reset decision (back to ideation to re-cut)
  before opening any further round — the counter-based escalation above and
  this budget-based brake are independent circuit breakers. A round whose
  findings are all declined records `0 fixed` with every decline named:
  "nothing was found" and "everything found was declined" must never read
  alike.
- **Rework re-anchors on the source requirement.** On any route-back, the
  rework agent re-reads the original requirement and diffs it against the
  current ACs before touching code — rework loops naturally optimize
  against intermediate artifacts and silently drop original constraints.
  Any dropped constraint is restored or explicitly justified first. **The diff
  runs the other way too: name every changed file no AC requires, and either
  delete it or state which AC it serves.** A rework loop adds machinery as
  readily as it drops constraints, and added machinery is the more expensive
  direction — it arrives with its own defects and its own review rounds, and
  each round it survives makes it look more load-bearing than it is.
- **One scope checkpoint before the first validation dispatch.** The FO maps
  each changed file to the AC it serves and identifies the ones that map to
  none — do not ask whether an AC *names* the file. ACs are end-state properties
  and rarely name an implementation path, so a name-matching check reports every
  legitimate file as unnamed while a stray one whose path happens to appear in
  an AC slips through.
  **What the FO does with the result depends on whether the set is empty.** Zero
  unmapped files is a notification: one line to the captain (files and lines
  changed, all mapped), and the FO proceeds without waiting. A non-empty set is
  not — an unmapped file is scope nobody authorized, and Gate Authority puts
  scope on the captain. The FO first tries to resolve it itself, exactly as the
  clause above says: delete the file, or state which AC it serves. Whatever
  cannot be resolved that way is escalated by name and the FO waits for an
  answer.
  The checkpoint sits here because the cheapest moment to cut is after the diff
  is real but before review rounds have compounded on it. A round spent
  reviewing machinery nobody wants is paid twice: once to find its defects, once
  to fix them.
- **Accepted validation preserves measurement evidence in the entity.** Keep the
  live `## Measurement` lines and accepted validation coverage so archive retains
  them. Product PR creation and delivery read no measurement of any kind; missing
  token or coverage evidence is not a delivery defect.

### `done` — terminal

Merge after a passed validation gate (merge policy: PR to `main`). An
authenticated product PR observed `MERGED` authorizes the terminal transaction:
clear the product `mod-block`, set `completed` to that product PR's exact
`mergedAt`, set the passed verdict and `done`, commit the live terminal entity
durably, then run the existing fail-closed archive transaction. No measurement
artifact and neither legacy `ledger_*` key is read by that decision. Missing,
stale, incomplete, pending, or malformed measurement cannot block terminal state
or archive.

- **Terminal state is not archival proof.** The `pr-merge` mod retains the
  authenticated product merge reference in the live terminal entity and
  re-verifies that exact merged product PR before cleanup and archive. Legacy
  `ledger_*` keys remain unconsumed bytes. The mod first commits the
  terminal file durably at its live path; the
  archive move is a second root-scoped state transaction and counts only after
  that commit is durable. Flat tasks move one file; folder tasks move the full
  `{slug}/` tree and verify every descendant, allowing only Spacedock's
  deterministic archive stamp in `index.md`. Filesystem and Git-tree guards
  reject symlink roots, symlink descendants, gitlinks, and other non-regular
  modes before Spacedock or the byte comparator can dereference them. Failed
  archive validation is rollback-eligible only after the same read-only guards,
  exact path-and-mode translation from the remote live root, exact comparator,
  two-root dirty-scope check, and whole-index prefix check pass; otherwise the
  crash evidence, including executable bits, remains untouched. Valid source
  modes `100644` and `100755` are both preserved. A narrow
  `_archive/` recovery scan
  restores any partial move from the durable live source, so restart never
  excludes the only retry copy. Recovery repeats product verification and
  exact clean-worktree cleanup; safe local branch deletion is best-effort and
  a squash-merge refusal is reported without blocking archive. Recovery never
  runs measurement import or PR creation.
  Historical terminal `direct-commit:` tasks take a separate read-only route:
  the commit must be reachable from current `origin/main`; that route archives
  without requiring or rewriting any historical measurement.
- **Merge only on observed green CI for the exact HEAD.** A passing local
  suite, a static PR approval, or "CI was green earlier" never substitutes
  for a live CI run observed green on the commit being merged. A red or
  running check at merge time blocks the merge — no exceptions by memory.

## Continuation & handoff

Picking up an in-flight branch — a closed sibling Conductor workspace, a
session-limit resume, a `/kc-session-handoff` record — does **not** inherit the
prior agent's validation. Before advancing: inventory what the prior agent left
(committed **and** uncommitted/WIP working-tree state), re-anchor on the source
requirement, re-classify the diff, and reconcile any upstream drift that landed
on `main` during the hiatus. Those four are owed at whatever stage the work
resumes. The validation evidence block is **not** re-run by the resuming
implementer — that would be the self-report this workflow forbids; it is owed on
entering or re-entering `validation`, against a fresh merge target, by the
fresh-context validator that stage requires.

A prior agent's "mostly done / green tests / one review passed" is a starting
point to verify, never a validation to trust — the continuation frame is exactly
where a half-done validation gets silently inherited as complete. Re-verify every
inherited finding's load-bearing claim against the code, not the prior narrative.
This is the `Rework re-anchors on the source requirement` clause with a broader
trigger (any resumed work), not a separate workflow. In this repo the frame
arrives more often than elsewhere, and the contended surface is **a shared
working tree, not a sibling worktree**: each Conductor workspace has its own
`HEAD`, so a sibling *workspace* cannot move yours, but a second session
operating in the *same* workspace can `git checkout` under you mid-task and take
files with it. So the inventory step reads the working tree it is standing in,
not the last thing you remember writing — and commits from an isolated
`git worktree add` when the tree is contended, since a commit is safe by SHA and
a working tree is not.

## Gate Authority

A gate is a decision point, not a status report. Who holds it depends on the
kind of decision, not on which stage it sits at.

| Seat | Holds | Examples |
|------|-------|----------|
| **Captain** | Direction and irreversibility | Scope authorship; what to work on next; schema / architecture / scope-cut / costly_no; accepting a documented residual against a red gate; any seat disagreement |
| **EM** (`ship-flow:science-officer-em`) | Bounded judgment on completed work | The ideation and validation verdicts — proceed / narrow / return / block |
| **FO** | Nothing adjudicative | Checklist accounting, AC-evidence presence, dispatch, merge mechanics, cleanup |

**Default: EM holds the gate.** The FO assembles the review — checklist
accounting, AC cross-check, reviewer findings — and routes it to EM for the
verdict. The FO neither renders the verdict itself nor forwards a completed,
findings-already-resolved stage to the captain for a rubber stamp.

**Auto-advance.** When a gate has zero Material findings, every AC carries
evidence, and the decision is reversible, EM approves and the FO advances
immediately. The captain is *notified in one line*, not asked. A captain who
wants it back says so; silence is not a gate.

**Escalate to the captain only when one of these holds — and name which:**

- The call is irreversible per Judgment Escalation below.
- Scope is being authored or re-cut. Only the captain holds scope.
- A Material finding survives EM review and changes what ships.
- A gate is red and the ask is to accept the residual on record.
- EM and FO disagree — that goes to the captain, never to a vote.
- Two consecutive rejected cycles closed at the same gate — see the validation
  stage's rejection clause. Unlike the bullets above it, this one fires on
  cycle count alone, whatever the findings were.

Anything else reaching the captain is over-escalation, and it costs more than
it protects: a captain pulled into six ceremonies per task stops reading the
two that mattered.

**Approval is scoped to the decision presented.** "The captain approved the
previous gate" is never authority for a later one.

**Speak consequence, not vocabulary.** A gate presented in the system's own
terms — a migration, a claim path, a corpus freeze — is not a decision the
captain can weigh; it is a request to trust the presenter. The tell is a
captain who answers "go with your recommendation" every time: at that point the
gate costs attention and returns nothing, and the seat has quietly moved back
to the FO without anyone deciding that it should.

Every escalation carries a plain restatement — literally "換句話說" — before it
asks for anything:

- **What breaks if this is wrong**, in terms of what a user or the team can no
  longer do. Not the mechanism; the consequence.
- **How expensive it is to reverse.** "Ships to production" and "one commit to
  revert" are different decisions and must not read the same.
- **What is actually being chosen.** Often it is narrower than the technical
  framing suggests — "restore something that was dropped by accident" is not
  "change how the system behaves", and the captain rules differently on each.

If the restatement cannot be written, the escalation is not ready: either the
FO does not yet understand the consequence, or there is no decision here and it
belongs to EM.

## Judgment Escalation

Irreversible calls — schema, architecture, scope-cut, costly_no, anything
merge-governing — are never self-adjudicated by the working agent.
**Merge-governing means a change to the merge rules themselves** — branch
protection, a required check, the merge policy, the release-please config that
propagates versions — **not a gate verdict that lets this one merge proceed.** A
passed validation gate is the second kind, so it stays inside the auto-advance
rule above; reading it as the first kind would make auto-advance dead for the
only stage it matters at. Route to a
fresh-context engineering-judgment agent (`ship-flow:science-officer-em`) for
independent synthesis, add one cross-vendor pass (codex/gemini) when the call
is contested, and bring the captain a CONVERGED recommendation. The captain
rules; disagreement between seats goes to the captain, not to a vote.

## Canonical Docs Ownership

| File | Owner | Updated |
|------|-------|---------|
| PRODUCT.md / ARCHITECTURE.md | Task lifecycle (ideation proposes, implementation applies, validation verifies) | In the PR that changes the behavior |
| ROADMAP.md / roadmap indexes | Captain (or sprint Commander) | Sprint boundaries, strategy shifts — never tracks task state (that's a `status --where` query) |
| This README | Captain-approved revision | When the workflow cost record says a clause needs tuning |

## Workflow cost record

No ledger. The eight-column `docs/dev/ledger.csv` and its row/verifier machinery
are removed: two of the three terms of the bar it existed to adjudicate are not
observable from this runtime. Across every archived entity, `tokens_if_known`
read `n/a` in all 17 recorded dispatches — three sessions on two runtimes each
noted the runtime does not expose per-worker usage — and no `escaped_defects_7d`
window was ever swept. A comparison that cannot be computed does not referee
anything.

The ledger clause wanted complexity to cost something before it was accepted.
Nothing here enforces that mechanically — the ledger did not either, since its
bar was never computed. What this record supplies instead is the evidence such a
judgment needs, on the axis that has any: not how fast a task ran, but **which
clause of this contract turned out to be expensive.** The enforcement point is
the captain's reading of it, named here so no one mistakes it for a gate.

When a rule in this contract demonstrably delayed or blocked a task, the FO of
that task appends one line below, after the EM accepts validation and before the
PR boundary:

`- <date> · <clause or file> — <what happened>. Cost: <unit>. <resolution, or open>`

The captain reads this section at the sprint boundary, and reads it again before
approving any addition to this contract. Nothing gates on it, no CI job reads it,
and an empty section is not a defect — an empty section means no clause has cost
anything yet, which is the outcome this record is hoping for.

Per-dispatch observations stay where they are already written: the entity's
`## Measurement` block and its stage reports. Those are the task's own evidence,
not a second task universe.

- 2026-08-03 · `## Gate Authority` (this file, 1166-1249) — the 84 lines an agent must
  know *before* acting sit inside a 1300-plus-line document whose remainder is looked
  up by keyword, so the two are reached by opposite means and only one of them works
  when you do not know you need it. A session that deleted 443 lines from this file
  and rewrote its Canonical Docs Ownership row never read its Gate Authority section:
  the heading was printed by that session's own `grep -n '^## '` and skipped for not
  matching the task term.
  Cost: the captain was asked to rule twice on decisions auto-advance already
  delegated, one turn went to re-deriving that rule from scratch, and the turn ended
  by proposing a clause the contract already contained. Open — ruled that the fix
  belongs to this flow rather than to a pointer in a file loaded earlier, since a
  pointer leaves the mixing in place and adds a second thing to keep true.
  Self-reported by the session that paid it; amend or strike as you see it.

## Task Template

```yaml
---
id:
title:
status: backlog
source:
product:
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
pr_artifact_v1:
mod-block:
design:
lane:
---

## Problem

## Proposed approach

## Design determination

`required` (attach decision) or `trivial-pass — <reason>`.

## Acceptance criteria

**AC-1 — <end-state property>.**
Verified by: <reproducible check outside this file>. Falsified by: <the edit that would flip it>.

## Test plan

## Measurement

<one line per dispatch, appended by the FO: `D<n> launched <when> | tokens: <figure on return, or n/a>`>

## Doc diff

<before/after wording for PRODUCT.md / ARCHITECTURE.md, or "none — no described behavior changes">

## Out of scope
```

## Commit Discipline

- Status changes commit at dispatch and merge boundaries (binary-owned).
- State commits are transaction-root-scoped per entity in the state checkout:
  one file for flat form, the complete task directory for folder form — never
  bare `git add -A`.
- Implementation commits land on the worktree branch; merge only after the validation gate passes.
