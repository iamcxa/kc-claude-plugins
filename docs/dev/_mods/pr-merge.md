---
name: pr-merge
description: Push branches and create/track GitHub PRs for workflow entities
version: 0.13.0
---

# PR Merge

Manages the PR lifecycle for workflow entities processed in worktree stages. Pushes branches, creates PRs, detects merged PRs, and advances entities accordingly.

## Hook: startup

Run the README's lifecycle-hook holder prerequisite as a fresh command before
every entity scan and every outward Git or GitHub action, including after any
approval pause and after each completed state mutation. Do not run it between
an idempotent state write and that write's companion `spacedock state commit`.
A non-holder stops after reporting the registered holder path; it does not run
this scan. The ordinary lifecycle scan
excludes `_archive/`, but a narrow archive-recovery pass also inspects terminal
archived-path files. Classify these restart-visible sets instead of assuming
every live file is a current hosted PR:

Every hook invocation discards prior process variables and reloads the holder
entity, canonical artifacts, refs, and host state. After a captain pause, an
inert candidate artifact persisted in the entity is the only reusable draft;
if none exists or its tuple changed, reconstruct and present it again. Approval
rewrites the same artifact field together with that exact digest's pending
`pr` ref and approved `mod-block` marker in one holder mutation and
`spacedock state commit`; shell variables never carry approval across calls.

The prerequisite freshly fetches `refs/heads/spacedock-state/dev` and classifies
the holder before any entity scan or outward action. It permits normal work
only after local `HEAD` equals that observed tip. On exit 75, anchor identity in
the sole dirty entity index and apply the README's exact frontmatter-diff
recovery. If that authenticated setter or compound prefix is local-behind,
preserve its exact root and ordered action in the README's private recovery
record, restore only that root, fast-forward, compatibility-check, and replay
the full action against the new parent. On exit 76 or 77, run the recognized
outgoing-commit recovery below. A live-root deletion paired with an archive
addition is not a normal set; route it to archive recovery.

1. non-terminal v1 entities with either
   `pr=pr-merge:{number}:artifact-v1:{product-artifact-sha256}`,
   an empty `pr` plus inert
   `mod-block=pr-merge:product-draft:v1:{product-artifact-sha256}`,
   or `pr=pr-merge:pending:artifact-v1:{product-artifact-sha256}` plus
   `mod-block=pr-merge:product-pr:v1:{product-artifact-sha256}`; every form
   requires `pr_artifact_v1`, and its `mod-block` marker must carry the same
   digest;
2. non-terminal legacy hosted-PR entities whose non-empty `pr` has no v1
   artifact suffix;
3. terminal live entities in the working state checkout or last confirmed
   durable state ref, including a durable live root whose working copy
   disappeared during a partial archive; these are either a v1 product plus
   ledger pair, or `pr=direct-commit:{sha}`;
4. terminal roots found under `_archive/`, solely to distinguish a durable
   completed archive from a partial move that must be restored live. Include
   both the v1 pair and `direct-commit:{sha}` legacy form.

The marker is deliberately compact and has one grammar: the fixed prefix plus
64 lowercase hexadecimal SHA-256 characters. It binds the entity frontmatter
field `pr_artifact_v1`, whose value is the unpadded base64url encoding of the
complete canonical product JSON bytes. Those bytes store `repo`, `base`,
`head`, the final approved full `head_oid`, exact `base_oid`, SHA-256 of the
approved binary diff as `diff_sha256`, exact `title`, exact full `body`,
`body_sha256`, exact `audit_link`, and the scanned state-root-relative
`live_path` outside `_archive/`. Canonical means UTF-8 JSON with sorted keys
and separators `,` and `:`, with no trailing newline. `body_sha256` hashes the
exact UTF-8 body bytes, and the marker digest hashes the exact decoded
canonical JSON bytes. Decode and validate the field, recompute both digests,
require the digest in its pending/numbered `pr` ref or draft/approved
`mod-block` to match, and round-trip the field byte-for-byte from the durable
state file before trusting either. Padding, a character outside
`[A-Za-z0-9_-]`, invalid
UTF-8 or JSON, an equivalent but non-canonical base64url spelling,
non-canonical JSON bytes, duplicate decoded keys, a digest mismatch, or a
setter rewrite blocks before any outward action.
An explicitly superseding product artifact additionally requires a 16-character
lowercase hexadecimal `attempt_id` and a non-empty `supersedes` array containing
the prior artifact digest and head branch plus its exact artifact-backed PR ref
or JSON `null` when exhaustive reconciliation found zero PRs. Its `head` is
`docs/pr-{short-id}-attempt-{attempt_id}`.
The artifact field is mod-owned frontmatter metadata and is excluded from
motivation, change, and evidence extraction if drift forces a renewed draft.

Use this codec for both product and ledger artifacts. `encode` accepts only an
already-canonical file and emits its field value. `decode` writes the exact
decoded bytes to a private destination and emits their SHA-256:

```bash
artifact_codec() {
  python3 - "$@" <<'PY'
import base64
import hashlib
import json
import pathlib
import re
import sys


def canonical(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key: {key}")
            result[key] = value
        return result

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    if encoded != raw:
        raise ValueError("artifact is not exact canonical JSON")
    return raw


mode = sys.argv[1]
if mode == "encode" and len(sys.argv) == 3:
    raw = canonical(pathlib.Path(sys.argv[2]).read_bytes())
    print(base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii"))
elif mode == "decode" and len(sys.argv) == 4:
    field = sys.argv[2]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", field):
        raise ValueError("artifact field is not unpadded base64url")
    padding = "=" * (-len(field) % 4)
    raw = base64.b64decode(
        field + padding, altchars=b"-_", validate=True
    )
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    if encoded != field:
        raise ValueError("artifact field has a non-canonical base64url spelling")
    canonical(raw)
    pathlib.Path(sys.argv[3]).write_bytes(raw)
    print(hashlib.sha256(raw).hexdigest())
else:
    raise SystemExit("usage: artifact_codec encode FILE | decode FIELD FILE")
PY
}
```

Artifact marker classification is field-specific in startup, dirty replay, and
outgoing-commit recovery:

- authenticate `pr_artifact_v1` only against its product draft/approved
  `mod-block` and pending/numbered `pr` forms;
- authenticate `ledger_artifact_v1` only against the draft, pending, numbered,
  or merged `ledger_pr` forms listed below.

Never compare a ledger artifact digest with `mod-block`: throughout ledger
draft/finalization that block still carries the independent product artifact
digest. When both artifacts exist, decode and authenticate both independently
and require their `live_path` values to agree.

The lifecycle fixture for this contract uses the installed Spacedock 0.26
binary and a temporary split-root repository. It must set an encoded artifact
and its draft digest `mod-block` in one `status --set`, read the field back from
the entity frontmatter, decode to byte-identical canonical JSON, and complete
`state commit`. Negative cases flip one base64url character, supply padded or
non-canonical JSON, mutate an unused final base64url bit (`Q` to `R`) without
changing the decoded bytes, reuse a valid artifact on a different entity, and
encode a `live_path` for another root; each must stop before a host query or
push. A crash fixture stops after the set, verifies the one anchored
frontmatter-only diff through exact replay, reruns the assignments, and
observes the companion state commit remotely.
A ledger-draft crash fixture keeps a different valid product digest in
`mod-block`, sets `ledger_artifact_v1` with its digest-bearing draft
`ledger_pr`, and proves replay and commit use the ledger ref rather than
rejecting it against the product block.
The dirty-local-behind fixture first authenticates a terminalization
clear-block prefix against local `HEAD` and writes the private recovery record.
One case advances the remote with an unrelated entity append, restores only
the authenticated root, fast-forwards, replays the complete two-set action
from the new parent, and observes the one resulting commit remotely. A second
case advances the same entity with an incompatible semantic-field change; it
must stop cleanly at the remote tip before replay and leave the recovery record
and saved dirty root byte-identical.

For a clean local-ahead holder left by a failed `spacedock state commit`, fetch
the exact state ref again and enumerate `REMOTE_TIP..LOCAL_HEAD` in oldest-first
order. Normal recovery requires exactly one outgoing commit. Its subject must
be exactly `state: update {slug}`; its diff may touch only the flat entity file
or the authenticated folder root for that slug. Decode the artifact field from
that committed index, require its field-specific digest marker and `live_path`,
and compare fresh host state with the one intended assignment array. Seed the
README's disposable Spacedock 0.26 replay from the outgoing commit's parent,
extract the complete committed entity root as its comparison target, and
require exact root-byte equality. This is the only normalization allowance; do
not hand-author an accepted parent-to-commit diff. An explicit
`direct-commit:{sha}` legacy entity uses its authenticated commit/task/path and
unique legacy ledger row instead and must not acquire a v1 field. The body,
unrelated fields, and all other paths must be unchanged. Only then retry:

If the outgoing child is terminal and its parent is the authenticated
blocked/non-terminal state with numbered product and ledger refs, validate it
only as the compound terminalization transaction. Authenticate both artifacts,
both merged PRs, and the landed ledger from the parent; seed the disposable
workflow from that parent; replay the clear-block setter and then the complete
terminal fields/refs setter; and require the final complete root to equal the
committed root byte-for-byte. Never replay the terminal setter alone.

```bash
STATE_REF=refs/heads/spacedock-state/dev
git -C "$STATE" push origin "HEAD:$STATE_REF" || exit 1
git -C "$STATE" fetch --no-tags origin "$STATE_REF" || exit 1
test "$(git -C "$STATE" rev-parse 'HEAD^{commit}')" = \
  "$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}')" || exit 1
```

If the fetched remote advanced and the tips diverged, permit rebase only after
the same one-commit/path/message/artifact check succeeds against its original
parent. Run `git -C "$STATE" rebase "$REMOTE_TIP"`; any conflict halts with
both tips and the conflict preserved. Recompute the rewritten commit, repeat
all checks and the exact replay against its new parent, and only then use the
exact push/observation above. A rewritten compound terminalization commit must
repeat both setters from its new parent and match exactly; validation against
the pre-rebase parent does not carry forward. Multiple or unknown outgoing
commits, an unrelated message/path, a replay mismatch, a corrupt or
wrong-entity artifact, or a host state that no longer derives that transition
blocks. A clean behind holder never enters this path: the README prerequisite
fast-forwards it and observes equality. Archive recovery uses its stricter
signed two-root transaction below. After any recovery, rerun the full holder
prerequisite before scanning or performing an outward action.

The empty-`pr` draft form decodes and authenticates its artifact and draft
`mod-block`, reloads the approved-to-be-presented tuple, and stops at captain
presentation. Before explicit approval it runs no PR lookup, branch push, PR
create, or other outward action. For pending or numbered entities in the first
set, load and authenticate the digest-bound artifact before querying or acting
on its PR. Require its repository and base to equal
`gh repo view --json nameWithOwner` and
`spacedock dispatch trunk --workflow-dir {dir}`; require its full head OID to
equal the quoted local `"$STORED_HEAD"`. After a push, also require fetched
`"origin/$STORED_HEAD"` to equal it; before the exact first push, only an absent
remote head is acceptable. Use the REST list-pulls endpoint for the exhaustive
lookup; the higher-level PR-list head shorthand is not this contract.
Run this complete query for each artifact, with `BODY_FILE` containing its exact
approved body:

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner') || exit 1
OWNER=${REPO%%/*}
BRANCH=$STORED_HEAD
BASE=$STORED_BASE
set -o pipefail || exit 1
PULLS=$(gh api --method GET --paginate "repos/$REPO/pulls" \
  --raw-field state=all \
  --raw-field head="$OWNER:$BRANCH" \
  --raw-field base="$BASE" \
  --raw-field per_page=100 | jq -s 'add') || exit 1
printf '%s\n' "$PULLS" | jq -e \
  --arg repo "$REPO" \
  --arg owner "$OWNER" \
  --arg branch "$BRANCH" \
  --arg oid "$STORED_HEAD_OID" \
  --arg base "$BASE" \
  --arg title "$STORED_TITLE" \
  --rawfile body "$BODY_FILE" '
    type == "array" and all(.[];
      .base.repo.full_name == $repo and
      .head.repo.full_name == $repo and
      .head.user.login == $owner and
      .head.ref == $branch and
      .head.sha == $oid and
      .base.ref == $base and
      .title == $title and
      (.body // "") == $body
    )
  ' >/dev/null || exit 1
```

Explicit `--method GET` keeps the `--raw-field` parameters on the supported
list endpoint; `--paginate` plus `jq -s 'add'` exhausts and combines every
page. The structural pass authenticates the returned repository, head owner,
head branch, full head SHA, base, title, and exact body before candidate
counting. Re-read every returned candidate and additionally require all of
these before it is eligible: current repository URL, same-repository head, exact
`headRefName`, exact `baseRefName`, `headRefOid` equal to the artifact's
`head_oid`, merge-base of the stored base/head OIDs equal to `base_oid`,
recomputed binary-diff SHA-256 for those stored OIDs equal to `diff_sha256`,
exact artifact title, SHA-256 of the exact returned body equal to
`body_sha256`, and the stored audit link present exactly once in that body.
`OPEN`, `MERGED`, and `CLOSED` are all recoverable states because each has a
defined route below. When `pr` already names a number, that exact PR must be
the one eligible result; a missing, different, or additional candidate blocks.

- No eligible candidate and no ineligible result means the outward create did
  not land only when `pr` is the pending ref for this exact artifact.
  Keep the marker and artifact and
  resume creation only when fetched `"origin/$STORED_BASE"` still equals
  `base_oid`,
  the recomputed binary-diff digest still equals `diff_sha256`, and all
  artifact repo/base/head/OID checks pass. Send the stored title and body
  verbatim. Any drift returns to rebase, reconstruction, and renewed captain
  approval. If the pending artifact's exact branch was already pushed, that
  renewal must use immutable supersession on a new branch; never rewrite the
  pushed ref. Do not reconstruct or paraphrase approved prose while claiming
  the old approval. Zero matches for an already-numbered v1 ref is an identity
  failure, never permission to create.
- Exactly one eligible candidate and no ineligible result is recoverable. If
  `pr` is the matching pending ref, atomically set the unchanged
  `pr_artifact_v1={product-base64url}` together with
  `pr=pr-merge:{number}:artifact-v1:{product-artifact-sha256}` and make that
  holder-owned entity mutation durable immediately with `spacedock state
  commit` before following its `OPEN`, `MERGED`, or `CLOSED` route. If `pr` is
  already a numbered artifact-backed ref, require its number and digest to
  match and make no identity rewrite. If persistence fails, retain the marker
  and repeat the same lookup on the next scan.
- More than one result, or any result that fails the metadata/body checks, is
  ambiguous. Do not bind a PR and do not create another one; report every
  candidate to the captain.

This lookup is also mandatory immediately before every product `gh pr create`.
It is a reconciliation operation only: it never pushes, creates, terminalizes,
or archives.

### Immutable supersession

A `CLOSED` retry, corrective PR, or drifted pushed-pending attempt with an
exhaustive zero-candidate result is reachable only after the captain explicitly
approves superseding the authenticated prior attempt. For the pushed-pending
case, first require the old remote branch still equals the old artifact's exact
`head_oid`; an externally changed old ref blocks as an identity violation
rather than becoming a supersession source. Base advancement or another
head/diff input change invalidates the old approval even though no PR exists.
The old remote branch remains immutable audit residue.

Mint a fresh attempt identity with
`python3 -c 'import secrets; print(secrets.token_hex(8))'`, require exactly 16
lowercase hexadecimal characters, and derive a branch that has never been used:

- product: `docs/pr-{short-id}-attempt-{attempt_id}`;
- ledger: `docs/dev-ledger-{short-id}-attempt-{attempt_id}`.

Before approval, require the proposed branch absent from both local refs and an
exhaustive `git ls-remote --heads origin
"refs/heads/{new-branch}"` result. Build the replacement from fresh
`origin/$BASE`, compute the new head/diff/body tuple, and obtain captain approval
for that tuple. The new canonical artifact includes `attempt_id` and a
`supersedes` array with the old artifact digest and head branch plus its exact
numbered PR ref, or JSON `null` when exhaustive reconciliation found no PR.
Retain every prior supersession entry as an append-only audit chain. Encode it
with `artifact_codec`, then persist either
`pr_artifact_v1={new-product-base64url}` together with
`pr=pr-merge:pending:artifact-v1:{new-product-digest}` and
`mod-block=pr-merge:product-pr:v1:{new-product-digest}`, or
`ledger_artifact_v1={new-ledger-base64url}` together with
`ledger_pr=ledger-pr:pending:artifact-v1:{new-ledger-digest}`. The artifact
field and every digest marker are assignments in one `status --set`, followed
immediately by `spacedock state commit`, before any push.

Reconciliation then runs the executable all-state query only for the new
artifact's owner, branch, and base. `CLOSED` or `MERGED` PRs on superseded
branches remain audit history and are not candidates for the new attempt; any
returned PR on the new branch that fails authentication, or more than one
candidate there, still blocks. Push only the new artifact's exact head OID to
the absent new ref. For product and ledger zero-candidate drift alike, exact
reconciliation and any eventual create run only on this new branch. Never
force-push, overwrite, delete, or reuse an old attempt branch. An unexpected
candidate on the new branch blocks; an uncertain create outcome resumes
reconciliation for the same durable new attempt and does not mint another.

The zero-candidate supersession fixture runs both branch families against a
temporary remote: push the old approved branch, return an exhaustive empty PR
result, advance the base, mint and approve a new attempt artifact with
`pr: null`, and push only the new branch. It requires both old refs to retain
their original OIDs, both new refs to be distinct and present exactly once, and
reconciliation to remain scoped to the corresponding new branch.

The second set is fail-closed pre-v0.13 legacy adoption. Parse the plain hosted PR
reference, quote its number in every `gh` call, and show the captain the exact
live identity: repository, base, head branch, full head OID, merge-base OID,
binary-diff SHA-256, exact title, full body plus body digest, audit link, and
live entity path. Even if the PR is already merged, do not terminalize or
start ledger finalization. Require one explicit captain approval to adopt that
identity, then serialize and durably persist the v1 product artifact and
replace the plain ref with
`pr_artifact_v1={product-base64url}` and
`pr=pr-merge:{number}:artifact-v1:{product-artifact-sha256}` in one
holder-owned `status --set` followed immediately by `spacedock state commit`.
Re-run the ordinary artifact authentication on
the next scan. A missing/ambiguous PR, fork head, unavailable exact body, or
captain decline leaves the legacy ref unchanged and blocks auto-advancement.

For an authenticated first-set entity, extract the product PR number and check:

```bash
gh pr view "$PRODUCT_PR_NUMBER" \
  --json state,mergedAt,headRefName,baseRefName,headRefOid,isCrossRepository,url,title,body
```

If the product PR is `MERGED`, it has delivered the pre-merge ledger row but has
not yet earned terminal state. Keep the original product PR in `pr`, retain the
existing `mod-block`, and run this ledger-finalization state machine:

The follow-up uses `ledger_artifact_v1`, the unpadded base64url of its complete
canonical JSON bytes. It carries the same fields and byte rules as the product
artifact
(`repo`, `base`, `head`, `head_oid`, `base_oid`, `diff_sha256`, exact `title`,
exact full `body`, `body_sha256`, `audit_link`, and `live_path`) plus the
authenticated `product_pr`, `product_artifact_sha256`, and
`product_merged_at`. Its SHA-256 binds these lifecycle forms:
For a superseding ledger attempt, the decoded artifact also requires the immutable
supersession contract's `attempt_id` and `supersedes` fields, and its `head`
must be `docs/dev-ledger-{short-id}-attempt-{attempt_id}`.

- before a PR number is known:
  `ledger_pr=ledger-pr:draft:artifact-v1:{ledger-artifact-sha256}` while
  awaiting captain approval, then
  `ledger_pr=ledger-pr:pending:artifact-v1:{ledger-artifact-sha256}`;
- after exact reconciliation:
  `ledger_pr=ledger-pr:{ledger-N}:artifact-v1:{ledger-artifact-sha256}`;
- after terminal verification:
  `ledger_pr=ledger-merge:{ledger-N}:artifact-v1:{ledger-artifact-sha256}`.

The field is bookkeeping metadata for the existing product entity. It is
excluded from PR-body extraction and never creates a task, dispatch, or ledger
row of its own.

1. Resolve `BASE=$(spacedock dispatch trunk --workflow-dir {dir})`, fetch
   `origin "$BASE"`, and select the phase **before** choosing a verifier:

   ```bash
   ledger_phase() {
     python3 - "$1" "${2-}" <<'PY'
import re
import sys

ledger_ref, host_state = sys.argv[1:]
digest = r"[0-9a-f]{64}"


def invalid():
    print("invalid")
    raise SystemExit(44)


if ledger_ref == "":
    if host_state != "":
        invalid()
    print("premerge")
elif re.fullmatch(rf"ledger-pr:draft:artifact-v1:{digest}", ledger_ref):
    if host_state != "":
        invalid()
    print("draft")
elif re.fullmatch(rf"ledger-pr:pending:artifact-v1:{digest}", ledger_ref):
    if host_state != "":
        invalid()
    print("reconcile")
elif re.fullmatch(
    rf"(?:ledger-pr|ledger-merge):[1-9][0-9]*:artifact-v1:{digest}",
    ledger_ref,
):
    if host_state not in {"OPEN", "CLOSED", "MERGED"}:
        invalid()
    print("terminal" if host_state == "MERGED" else "wait")
else:
    invalid()
PY
   }
   ```

   With empty `ledger_pr`, set `PHASE=premerge`. A valid `draft` ref reloads
   its digest-matched `ledger_artifact_v1` tuple and resumes presentation or
   approval instead of rebuilding it from process state. With another non-empty
   `ledger_pr`, authenticate its ledger artifact first. A pending marker enters exact
   reconciliation without inventing a number. A numbered ref queries only its
   authenticated PR; `MERGED` sets `PHASE=terminal`, while `OPEN` or `CLOSED`
   does not run either row verifier. Every accepted digest is exactly 64
   lowercase hexadecimal characters, and every numbered form uses a positive
   decimal PR number with no empty or extra tokens. Any other grammar prints
   `invalid`, returns `44`, and blocks before a verifier or host mutation.
2. In `premerge`, extract the landed ledger without trusting the current
   checkout (`git show "origin/$BASE:docs/dev/ledger.csv" > {private-temp}`)
   and run the README's `ledger_verify premerge {task-id} {slug}
   {private-temp}`. Missing (41), duplicate (42), or incomplete (43) is a
   lifecycle defect: do not invent a value, do not clear `mod-block`, and do
   not terminalize or archive. Report the exact state to the captain. Repair
   is a bounded ledger-finalization PR built from the entity's persisted
   `## Measurement`; if those lines are themselves incomplete, the entity
   stays blocked because the live-only evidence is gone.
3. When the pre-merge row is exact, compute
   `wallclock_hours` from the entity's `started` timestamp to the product PR's
   `mergedAt`, rounded to two decimal hours with trailing zeroes removed.
   Compute `escaped_defects_7d` as `pending:<YYYY-MM-DD>`, seven UTC calendar
   days after the UTC date of `mergedAt`; if that date has already arrived,
   perform the overdue sweep and use the observed integer Severity-1/2 count
   instead. Replace only this task's `pending:done` and `pending:merge` cells
   with those values, using the README's line-preserving `ledger_upsert`.
4. Prepare that replacement on deterministic branch
   `docs/dev-ledger-{short-id}`, cut from fresh `origin/$BASE` in a private
   temporary worktree. Run `ledger_verify terminal {task-id} {slug}
   {ledger-path} {started} {mergedAt}` there and inspect the ledger diff before
   presenting a follow-up PR draft. The captain approval guardrail below
   applies independently to this outward-facing push and PR.
   If this row completes the ten-row baseline cohort, compute after the row
   update and include the frozen README medians in this same commit; otherwise
   the commit contains only `ledger.csv`.
   Before presenting the draft, commit `docs/dev/ledger.csv` locally with
   `docs(dev): finalize ledger for {slug}`, serialize its exact tuple as the
   canonical ledger artifact, encode it, and persist only
   `ledger_artifact_v1={ledger-base64url}` together with
   `ledger_pr=ledger-pr:draft:artifact-v1:{ledger-artifact-sha256}` in one
   `status --set` plus `spacedock state commit`. Present the decoded artifact
   digest; the inert field authorizes no outward action until approved.

   On approval, reload that exact durable artifact. Re-fetch `origin "$BASE"`
   and require its full OID to remain the approved `base_oid`; require the
   private branch HEAD and binary diff to remain the approved OID/digest. Drift
   persists the replacement `ledger_artifact_v1` and its new digest-bearing
   draft ref in one set-plus-commit and requires renewed approval.
   Otherwise set both
   `ledger_artifact_v1={approved-ledger-base64url}` and
   `ledger_pr=ledger-pr:pending:artifact-v1:{ledger-artifact-sha256}` through
   one self-contained holder mutation followed immediately by
   `spacedock state commit`. Re-read the durable entity and verify both
   the decoded artifact/body digests and every field. If this fails, perform no outward
   action.

   Run the executable `gh api --method GET --paginate` query above with the
   ledger artifact's repo, owner, head branch, head OID, base, title, and exact
   body file. Re-read each candidate
   and require same-repository head, exact base/head names, exact full head
   OID, merge-base of the stored base/head OIDs equal to `base_oid`,
   recomputed binary-diff digest for those OIDs, exact artifact title, exact
   body digest, and the audit link exactly once. More than one result or any
   ineligible result blocks. Exactly one eligible result is reused. Only a
   completed zero-result query may continue: fetch
   `origin "$BASE"` and require `"origin/$BASE"` to equal the artifact's
   `base_oid`, recompute its exact binary-diff digest, then require an absent
   remote head or one already equal to `head_oid`. Push only the stored object
   with the quoted explicit refspec
   `git push origin
   "${LEDGER_HEAD_OID}:refs/heads/${LEDGER_HEAD}"`, fetch it back, and repeat
   the exhaustive query immediately before
   `gh pr create --base "$BASE" --head "$LEDGER_HEAD"
   --title "$LEDGER_TITLE" --body-file "$LEDGER_BODY_FILE"`. Title and body
   come only from the authenticated artifact. An uncertain create outcome
   always returns to reconciliation before retry.

   If exhaustive reconciliation is still zero but the exact ledger branch was
   already pushed and the base/head/diff tuple no longer matches, do not update
   that branch. Run immutable supersession after renewed captain approval:
   mint a new ledger attempt branch and artifact whose `supersedes` entry
   records the old digest/branch and `pr: null`, leave the old remote ref
   untouched, and reconcile only the new branch.

   Once exactly one eligible PR exists, atomically replace the pending value
   by setting the unchanged
   `ledger_artifact_v1={ledger-base64url}` together with
   `ledger_pr=ledger-pr:{ledger-N}:artifact-v1:{ledger-artifact-sha256}` and
   immediately run `spacedock state commit`. A crash before this number write
   therefore finds the pending artifact and exact hosted candidate instead of
   creating a duplicate. Never force-push or overwrite a different remote
   head. This follow-up is bookkeeping for the existing entity and creates no
   recursive dev-flow task or ledger row.
5. On every scan with non-empty `ledger_pr`, recompute and authenticate its
   artifact before using a number or state. Pending form runs the zero/one
   reconciliation above. Numbered form requires its exact PR to be the sole
   eligible candidate; zero matches is an identity failure, not permission to
   create. Query the quoted number with
   `gh pr view "$LEDGER_PR_NUMBER"
   --json state,mergedAt,headRefName,baseRefName,headRefOid,isCrossRepository,url,title,body`.
   `OPEN` means wait. `CLOSED` without merge is reported to the captain with
   reopen, captain-approved immutable supersession, or abandon options. A new
   PR must use the supersession contract above; clearing the ref or reusing the
   old branch is not a retry route. On `MERGED`, authenticate the artifact and
   hosted PR again, fetch `origin "$BASE"`, extract its ledger, and run
   `ledger_verify terminal {task-id} {slug} {private-temp} {started}
   {mergedAt}` against the landed file. The verifier must return
   `ledger:exact`. If the only defect is that its dated pending cell became
   overdue while the follow-up waited, perform the escaped-defect sweep and
   use the immutable supersession contract to prepare a corrective finalization
   PR from fresh `origin/$BASE`. Its new artifact records the prior ledger PR,
   digest, and branch in `supersedes`; after independent captain approval,
   persist its pending ref and run exact reconciliation only on its new branch.
   Any other missing, duplicate, incomplete, or still-sentinel result uses the
   same corrective supersession route from persisted Measurement evidence and
   never manual state surgery.
6. Only after that landed terminal verification succeeds, run one
   self-contained holder durability transaction. Spacedock requires a separate
   setter to clear `mod-block`, so issue two setters back-to-back and then
   exactly one `state commit`:

   ```bash
   spacedock status --workflow-dir "$WORKFLOW_DIR" \
     --set "$SLUG" mod-block= &&
   spacedock status --workflow-dir "$WORKFLOW_DIR" --set "$SLUG" \
     status="$TERMINAL" completed="$MERGED_AT" verdict=PASSED worktree= \
     pr_artifact_v1="$PRODUCT_ARTIFACT_B64URL" \
     ledger_artifact_v1="$LEDGER_ARTIFACT_B64URL" \
     pr="pr-merge:$PR_NUMBER:artifact-v1:$PRODUCT_ARTIFACT_SHA256" \
     ledger_pr="ledger-merge:$LEDGER_PR_NUMBER:artifact-v1:$LEDGER_ARTIFACT_SHA256" &&
     spacedock state commit "$SLUG" || exit 1
   ```

   Never run the holder prerequisite or commit between the two setters. A
   commit after only `mod-block=` would create a clean, non-terminal,
   unblocked entity and is forbidden.
   Re-authenticate both artifacts and both exact hosted PRs immediately before
   this transaction. The product digest is copied from the verified product ref and
   the ledger digest from the verified numbered ledger ref, so
   terminal/archive recovery can authenticate `live_path`, both branch heads,
   and both approved bodies. If this command fails, both artifact-backed PR
   references and canonical artifact fields remain available for recovery.
   A dirty crash after the first or second setter is a two-prefix compound
   action: seed the disposable Spacedock 0.26 replay from the freshly fetched
   terminal-ready parent, authenticate its numbered product and ledger refs,
   artifacts, merged host state, and exact landed ledger, then produce an exact
   replay root after setter one and another after setter two. The dirty holder
   must match one of those two roots byte-for-byte and no other path may differ.
   A match reruns both setters idempotently and executes one `state commit`; a
   mismatch blocks. This is the only recovery route for either crash point.

   As a compatibility defense, startup may encounter a clean durable
   non-terminal entity with empty `mod-block`, authenticated numbered product
   and ledger refs, and otherwise terminal-ready evidence from the superseded
   two-commit flow. Classify and authenticate that exact state, then run the
   complete two-set/one-commit transaction. New flow never creates that
   intermediate durable state.

   The terminalization fixture stops once after setter one and once after
   setter two, requires each dirty root to match only its corresponding replay
   prefix, then recovers. In both cases the resulting commit's parent is
   blocked/non-terminal and its child is unblocked/terminal; no intermediate
   state commit exists.
   Use only the configured holder `STATE` after rerunning the README
   prerequisite. Retain the
   authenticated entity index as `LIVE_INDEX`, require it outside `_archive/`,
   and derive the flat file or complete folder `LIVE_ROOT`. Commit only that
   root with normal `spacedock state commit` while it is still live. Record the
   confirmed commit as `TERM_COMMIT` and prove
   every descendant path/byte at `TERM_COMMIT:$LIVE_ROOT` matches the terminal
   root on disk. If any write, commit, push, or round-trip check fails, do not
   clean up or archive.
   Feed that durably committed live terminal file through the recovery path
   below, even in the same hook invocation, so a crash between terminalization,
   cleanup, archive move, and archive commit has a known recovery source.

Before processing the third set, repair the fourth set — or a durable-live
third-set member whose working copy is missing — back to a live retry state.
For a v1 entity, load both digest-bound artifacts and take `LIVE_INDEX` only
from their identical validated `live_path`; for a direct-commit legacy entity,
take it from the unique exact task-id/ref scan result. Derive `LIVE_ROOT` by
the flat/folder rule above. When an archived working copy exists, take
`ARCHIVE_INDEX` and `ARCHIVE_ROOT` only from the unique exact `_archive/`
result. A missing archived copy does not hide a missing live working root
because the third set also scans the durable state ref. Resolve the last state
commit confirmed durable by the holder's `spacedock state commit` as
`DURABLE_STATE`.

Derive transaction roots from the authenticated live path. For flat form,
`LIVE_ROOT=LIVE_INDEX={slug}.md` and
`ARCHIVE_ROOT=ARCHIVE_INDEX=_archive/{slug}.md`. For folder form,
`LIVE_ROOT={slug}`, `LIVE_INDEX={slug}/index.md`,
`ARCHIVE_ROOT=_archive/{slug}`, and
`ARCHIVE_INDEX=_archive/{slug}/index.md`. The archive transaction always owns
the full two roots, not only the index files.

Use this byte-preserving root comparator. Spacedock either inserts its
`archived: YYYY-MM-DDTHH:MM:SSZ` field immediately before the closing
frontmatter delimiter, or replaces one existing blank `archived:` field in
place in the entity index. For folder form it additionally requires the same
relative descendant file set and byte-identical content for every file other
than `index.md`; non-regular descendants fail closed. Before either comparator
or `spacedock status --archive`, the filesystem guard rejects a symlink or
special root and rejects every symlink or special folder descendant without
dereferencing it. The independent Git-tree guard requires the flat root, or
every tracked file below the folder root, to be mode `100644` or `100755`;
mode `120000`, gitlinks, and other non-blob modes fail. The comparator reverses
only the valid UTC-seconds stamp and therefore preserves the product and ledger
refs, both canonical approval artifacts, the entity body, and every per-stage
artifact byte:

```bash
archive_root_guard() {
  python3 - "$1" "$2" <<'PY'
import os
import pathlib
import stat
import sys

root = pathlib.Path(sys.argv[1])
form = sys.argv[2]


def fail(message):
    print(f"archive:unsafe-root:{message}", file=sys.stderr)
    raise SystemExit(1)


if form not in {"flat", "folder"}:
    fail("invalid-form")
if root.is_symlink():
    fail("root-symlink")
try:
    root_mode = root.lstat().st_mode
except OSError:
    fail("root-unavailable")

if form == "flat":
    if not stat.S_ISREG(root_mode):
        fail("flat-not-regular")
else:
    if not stat.S_ISDIR(root_mode):
        fail("folder-not-directory")
    found_index = False
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError:
            fail("descendant-unavailable")
        for entry in entries:
            relative = pathlib.Path(entry.path).relative_to(root).as_posix()
            try:
                mode = entry.stat(follow_symlinks=False).st_mode
            except OSError:
                fail(f"descendant-unavailable:{relative}")
            if stat.S_ISLNK(mode):
                fail(f"descendant-symlink:{relative}")
            if stat.S_ISDIR(mode):
                pending.append(pathlib.Path(entry.path))
            elif stat.S_ISREG(mode):
                if relative == "index.md":
                    found_index = True
            else:
                fail(f"descendant-not-regular:{relative}")
    if not found_index:
        fail("missing-index")
print("archive-root:regular")
PY
}

archive_git_root_verify() {
  python3 - "$@" <<'PY'
import pathlib
import subprocess
import sys

repo, treeish, root, form = sys.argv[1:]
regular_modes = {b"100644", b"100755"}


def fail(message):
    print(f"archive:unsafe-git-root:{message}", file=sys.stderr)
    raise SystemExit(1)


root_path = pathlib.PurePosixPath(root)
if (
    form not in {"flat", "folder"}
    or root_path.is_absolute()
    or root in {"", "."}
    or ".." in root_path.parts
):
    fail("invalid-root")


def ls_tree(*arguments):
    result = subprocess.run(
        ["git", "-C", repo, "ls-tree", "-z", *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        fail("tree-unavailable")
    return [record for record in result.stdout.split(b"\0") if record]


def parse(record):
    try:
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, _oid = metadata.split(b" ", 2)
        path = raw_path.decode("utf-8", "surrogateescape")
    except ValueError:
        fail("malformed-tree-entry")
    return mode, kind, path


top = ls_tree(treeish, "--", root)
if len(top) != 1:
    fail("root-count")
top_mode, top_kind, top_path = parse(top[0])
if top_path != root:
    fail("root-path")

if form == "flat":
    if top_mode not in regular_modes or top_kind != b"blob":
        fail("flat-not-regular")
else:
    if top_mode != b"040000" or top_kind != b"tree":
        fail("folder-not-tree")
    descendants = ls_tree("-r", treeish, "--", root)
    if not descendants:
        fail("empty-folder")
    found_index = False
    prefix = root.rstrip("/") + "/"
    for record in descendants:
        mode, kind, path = parse(record)
        if (
            not path.startswith(prefix)
            or mode not in regular_modes
            or kind != b"blob"
        ):
            fail(f"descendant-not-regular:{path}")
        if path == prefix + "index.md":
            found_index = True
    if not found_index:
        fail("missing-index")
print("archive-git-root:exact")
PY
}

archive_verify() {
  python3 - "$1" "$2" <<'PY'
import datetime
import os
import pathlib
import re
import stat
import sys


def fail(message):
    print(f"archive:mismatch:{message}", file=sys.stderr)
    raise SystemExit(1)


def frontmatter(raw, label):
    lines = raw.splitlines(keepends=True)
    if not lines or lines[0].rstrip(b"\r\n") != b"---":
        fail(f"{label}:missing-frontmatter")
    try:
        close = next(
            index
            for index, line in enumerate(lines[1:], 1)
            if line.rstrip(b"\r\n") == b"---"
        )
    except StopIteration:
        fail(f"{label}:unterminated-frontmatter")
    fields = [
        index
        for index, line in enumerate(lines[1:close], 1)
        if line.startswith(b"archived:")
    ]
    return lines, close, fields


def normalized_index(live, archived):
    live_lines, _live_close, live_fields = frontmatter(live, "live")
    archive_lines, archive_close, archive_fields = frontmatter(archived, "archive")

    if len(live_fields) > 1 or (
        live_fields
        and not re.fullmatch(
            rb"archived:[ \t]*(?:\r?\n)?", live_lines[live_fields[0]]
        )
    ):
        fail("live:archived-not-empty")
    if len(archive_fields) != 1:
        fail("archive:archived-count")

    archive_index = archive_fields[0]
    match = re.fullmatch(
        rb"archived: ([0-9]{4}-[0-9]{2}-[0-9]{2}T"
        rb"[0-9]{2}:[0-9]{2}:[0-9]{2}Z)(\r?\n)?",
        archive_lines[archive_index],
    )
    if match is None:
        fail("archive:invalid-stamp-shape")
    try:
        datetime.datetime.strptime(
            match.group(1).decode("ascii"), "%Y-%m-%dT%H:%M:%SZ"
        )
    except ValueError:
        fail("archive:invalid-stamp-value")

    normalized = archive_lines[:]
    if live_fields:
        if len(archive_lines) != len(live_lines) or archive_index != live_fields[0]:
            fail("archive:stamp-not-replaced-in-place")
        normalized[archive_index] = live_lines[live_fields[0]]
    elif archive_index == archive_close - 1:
        del normalized[archive_index]
    else:
        fail("archive:stamp-not-inserted-at-frontmatter-end")
    return b"".join(normalized)


def descendants(root, label):
    entries = {}
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            children = list(os.scandir(directory))
        except OSError:
            fail(f"{label}:unavailable")
        for child in children:
            path = pathlib.Path(child.path)
            relative = path.relative_to(root).as_posix()
            try:
                mode = child.stat(follow_symlinks=False).st_mode
            except OSError:
                fail(f"{label}:unavailable:{relative}")
            if stat.S_ISLNK(mode):
                fail(f"{label}:non-regular:{relative}")
            if stat.S_ISDIR(mode):
                pending.append(path)
            elif stat.S_ISREG(mode):
                entries[relative] = path.read_bytes()
            else:
                fail(f"{label}:non-regular:{relative}")
    return entries


live_root = pathlib.Path(sys.argv[1])
archive_root = pathlib.Path(sys.argv[2])
for root, label in ((live_root, "live"), (archive_root, "archive")):
    if root.is_symlink():
        fail(f"{label}:root-symlink")
    try:
        mode = root.lstat().st_mode
    except OSError:
        fail(f"{label}:root-unavailable")
    if stat.S_ISREG(mode):
        kind = "file"
    elif stat.S_ISDIR(mode):
        kind = "directory"
    else:
        fail(f"{label}:non-regular-root")
    if label == "live":
        live_kind = kind
    else:
        archive_kind = kind

if live_kind == "file" and archive_kind == "file":
    live = live_root.read_bytes()
    if normalized_index(live, archive_root.read_bytes()) != live:
        fail("archive:unexpected-byte-change")
elif live_kind == "directory" and archive_kind == "directory":
    live_entries = descendants(live_root, "live")
    archive_entries = descendants(archive_root, "archive")
    if live_entries.keys() != archive_entries.keys():
        fail("archive:descendant-path-change")
    if "index.md" not in live_entries:
        fail("live:missing-index")
    if normalized_index(
        live_entries["index.md"], archive_entries["index.md"]
    ) != live_entries["index.md"]:
        fail("archive:unexpected-index-byte-change")
    for relative, content in live_entries.items():
        if relative != "index.md" and archive_entries[relative] != content:
            fail(f"archive:unexpected-byte-change:{relative}")
else:
    fail("archive:root-kind-change")
print("archive:exact")
PY
}
```

The root-safety fixture runs both guards and the comparator against a normal
tracked flat file and a normal tracked folder with `index.md` plus a nested
artifact; both pass. It then replaces the flat root with a symlink and,
separately, adds a symlink descendant whose target is outside the fixture.
Both filesystem cases fail before any target bytes are read. Matching Git-tree
cases with mode `120000` fail `archive_git_root_verify`, including when a
separate working-tree path happens to look regular.

### Archive durability transaction (Spacedock 0.26)

Archiving is the one state mutation that does not use `spacedock state
commit`. In Spacedock 0.26, `status --archive` moves the entity before `state
commit {slug}` resolves it, and that commit cannot stage both the live deletion
and archive addition. Use this explicit holder Git transaction instead:

1. At a fresh transaction boundary, require the clean registered holder, fetch
   the state ref explicitly, and require local `HEAD` to equal that exact tip:

   ```bash
   STATE_REF=refs/heads/spacedock-state/dev
   git -C "$STATE" fetch --no-tags origin "$STATE_REF" || exit 1
   REMOTE_TIP=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}') || exit 1
   LOCAL_HEAD=$(git -C "$STATE" rev-parse 'HEAD^{commit}') || exit 1
   test "$LOCAL_HEAD" = "$REMOTE_TIP" || exit 1
   ARCHIVE_PARENT=$REMOTE_TIP
   ```

   Behind, ahead, or diverged state returns to the holder prerequisite's
   classification; the archive cannot bundle or hide a pre-existing commit.
   Re-authenticate the complete live root at `ARCHIVE_PARENT` and extract it to
   a private temporary location before moving anything. Set
   `ROOT_FORM=flat|folder` from the authenticated index, then require
   `archive_root_guard "$STATE/$LIVE_ROOT" "$ROOT_FORM"` and
   `archive_git_root_verify "$STATE" "$ARCHIVE_PARENT" "$LIVE_ROOT"
   "$ROOT_FORM"` to pass before invoking Spacedock. A filesystem root that is a
   symlink, or a Git root/descendant with mode `120000` or another non-regular
   mode, blocks before the archive command.
2. Run `spacedock status --workflow-dir "$WORKFLOW_DIR" --archive "$SLUG"`.
   Locate exactly one archive index with the same task id and authenticated
   refs, derive the complete `ARCHIVE_ROOT`, and require `LIVE_ROOT` absent.
   Require `archive_root_guard "$STATE/$ARCHIVE_ROOT" "$ROOT_FORM"` before
   `archive_verify` over the extracted parent live root and working archive
   root. Both must pass; neither guard nor comparator follows a symlink.
3. Stage the two whole roots, including untracked folder descendants, and
   prove the candidate commit is exactly the move:

   ```bash
   CACHED_PATHS=$(mktemp "${TMPDIR:-/tmp}/pr-merge-paths.XXXXXX") || exit 1
   git -C "$STATE" add -A -- "$LIVE_ROOT" "$ARCHIVE_ROOT" || exit 1
   test -z "$(git -C "$STATE" diff --name-only)" || exit 1
   test -z "$(git -C "$STATE" ls-files --others --exclude-standard)" || exit 1
   git -C "$STATE" diff --cached --quiet && exit 1
   git -C "$STATE" diff --cached --name-only -z >"$CACHED_PATHS"
   CANDIDATE_TREE=$(git -C "$STATE" write-tree) || exit 1
   archive_git_root_verify \
     "$STATE" "$ARCHIVE_PARENT" "$LIVE_ROOT" "$ROOT_FORM" || exit 1
   archive_git_root_verify \
     "$STATE" "$CANDIDATE_TREE" "$ARCHIVE_ROOT" "$ROOT_FORM" || exit 1
   ```

   Parse `CACHED_PATHS` as NUL-delimited repository-relative paths. Every path
   must equal one root or be its descendant. Independently require the parent
   tree to contain live/no archive and the cached index to contain archive/no
   live; this remains correct when Git represents the move as renames rather
   than separate add/delete records. Extract the archive root from the cached
   index and compare it with the parent live root using `archive_verify`;
   checking only the worktree is insufficient.
4. Create one signed, path-scoped commit and validate its parent, scope, and
   tree before any push:

   ```bash
   git -C "$STATE" commit -s --only \
     -m "docs(dev): archive $SLUG" -- "$LIVE_ROOT" "$ARCHIVE_ROOT" || exit 1
   ARCHIVE_COMMIT=$(git -C "$STATE" rev-parse HEAD^{commit}) || exit 1
   ARCHIVE_TREE=$(git -C "$STATE" rev-parse "$ARCHIVE_COMMIT^{tree}") || exit 1
   test "$(git -C "$STATE" rev-parse "$ARCHIVE_COMMIT^")" = \
     "$ARCHIVE_PARENT" || exit 1
   ```

   Require the commit diff to contain only the two complete roots, its parent
   to contain live/no archive, its tree to contain archive/no live, a valid DCO
   sign-off, both corresponding `archive_git_root_verify` calls to pass, and
   `archive_verify` between roots extracted from the two commits to print
   `archive:exact`. Immediately before push, freshly fetch the state ref again
   and require the outgoing range from that observed tip to contain exactly
   this one commit, with `ARCHIVE_COMMIT^` equal to the observed tip. Any
   pre-existing or additional outgoing commit blocks.
5. Push only the exact state ref:

   ```bash
   git -C "$STATE" fetch --no-tags origin "$STATE_REF" || exit 1
   PUSH_PARENT=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}') || exit 1
   test "$(git -C "$STATE" rev-list --count "${PUSH_PARENT}..HEAD")" -eq 1 ||
     exit 1
   test "$(git -C "$STATE" rev-parse 'HEAD^')" = "$PUSH_PARENT" || exit 1
   test "$(git -C "$STATE" rev-parse HEAD)" = "$ARCHIVE_COMMIT" || exit 1
   git -C "$STATE" push origin "HEAD:$STATE_REF"
   ```

   On a non-fast-forward rejection, fetch `"$STATE_REF"` exactly and rebase
   only the single already-validated archive commit onto the fetched tip. A
   conflict stops with the index and both tips reported; never select
   `ours`/`theirs`, force-push, or discard a conflicting state change.
   After a clean rebase, recompute `ARCHIVE_PARENT`, `ARCHIVE_COMMIT`, and
   `ARCHIVE_TREE`; repeat every scope, root-presence, DCO, and comparator check,
   and require the freshly fetched outgoing range to be exactly that rewritten
   commit before retrying the exact ref push. Bound retries; never force.
6. Fetch `"$STATE_REF"` again as the observation step. Let the fetched commit
   be `OBSERVED_TIP`. Completion requires `ARCHIVE_COMMIT` to be its ancestor,
   the observed object for that commit to have exactly `ARCHIVE_TREE`,
   `OBSERVED_TIP` to contain the same complete `ARCHIVE_ROOT` and no
   `LIVE_ROOT`, no later diff to either root, and the parent-to-observed
   `archive_verify` result to be `archive:exact`. Only this remote observation,
   not a successful local commit or push exit code, declares the archive
   durable.

Every invocation recovers before starting another transaction. Fetch the exact
state ref, then classify the remote tip, local `HEAD`, index, and worktree:

- Remote archive/no live that passes the completed transaction checks above is
  already complete, including a crash after push but before confirmation.
- Remote live/no archive plus a dirty holder whose staged, unstaged, and
  untracked paths are exactly the two authenticated roots is a crash after the
  move or stage. Require the remote live root and local archive root to pass
  both filesystem/Git regular-root guards and `archive_verify`, stage both
  roots again, and resume at step 3. Any unrelated path, non-regular mode, or
  byte blocks with evidence preserved.
- Remote live/no archive plus a clean local `HEAD` ahead by exactly one valid
  root-scoped archive commit is a crash after commit but before push. Require
  the full outgoing range to be that commit alone, recheck its parent, roots,
  regular Git modes, DCO, and comparator, then resume at step 5.
- Remote live/no archive and local `HEAD` equal to it is either untouched or
  restored live. It may re-enter the third scan only after the complete live
  root matches the remote tree.

If a partial move cannot safely finish and the remote still contains the
authenticated complete live root, restore both index and worktree roots from
that remote commit. First extract `REMOTE_TIP:$LIVE_ROOT` to a fresh private
`REMOTE_LIVE_COPY`. The rollback preflight is read-only: every dirty path must
belong to the two authenticated roots, the remote Git root and extracted copy
must be regular, any local live root must equal that copy byte-for-byte, and
any archive root must pass both the filesystem guard and `archive_verify`.
Missing, extra, mismatched, symlink, gitlink, or special-file evidence stops
without changing the index or worktree:

```bash
archive_dirty_scope_verify() {
  python3 - "$@" <<'PY'
import pathlib
import subprocess
import sys

repo, live_root, archive_root = sys.argv[1:]


def fail(message):
    print(f"archive-rollback-scope:mismatch:{message}", file=sys.stderr)
    raise SystemExit(1)


for root in (live_root, archive_root):
    parsed = pathlib.PurePosixPath(root)
    if parsed.is_absolute() or root in {"", "."} or ".." in parsed.parts:
        fail("invalid-root")


def changed(*arguments):
    result = subprocess.run(
        ["git", "-C", repo, *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        fail("git-query")
    return [
        value.decode("utf-8", "surrogateescape")
        for value in result.stdout.split(b"\0")
        if value
    ]


paths = []
paths.extend(changed("diff", "--name-only", "-z"))
paths.extend(changed("diff", "--cached", "--name-only", "-z"))
paths.extend(changed("ls-files", "--others", "--exclude-standard", "-z"))
paths.extend(
    changed(
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "-z",
        "--",
        live_root,
        archive_root,
    )
)
for path in paths:
    if not any(
        path == root or path.startswith(root.rstrip("/") + "/")
        for root in (live_root, archive_root)
    ):
        fail(f"unscoped-path:{path}")
print("archive-rollback-scope:exact")
PY
}

archive_inverse_finish() {
  test -n "${REMOTE_LIVE_COPY-}" || return 1
  test -e "$REMOTE_LIVE_COPY" || test -L "$REMOTE_LIVE_COPY" || return 1
  archive_dirty_scope_verify \
    "$STATE" "$LIVE_ROOT" "$ARCHIVE_ROOT" || return 1
  archive_root_guard "$REMOTE_LIVE_COPY" "$ROOT_FORM" || return 1
  archive_git_root_verify \
    "$STATE" "$REMOTE_TIP" "$LIVE_ROOT" "$ROOT_FORM" || return 1

  live_present=no
  if test -e "$STATE/$LIVE_ROOT" || test -L "$STATE/$LIVE_ROOT"; then
    archive_root_guard "$STATE/$LIVE_ROOT" "$ROOT_FORM" || return 1
    git diff --no-index --quiet -- \
      "$REMOTE_LIVE_COPY" "$STATE/$LIVE_ROOT" || return 1
    live_present=yes
  fi

  archive_present=no
  if test -e "$STATE/$ARCHIVE_ROOT" || test -L "$STATE/$ARCHIVE_ROOT"; then
    archive_root_guard "$STATE/$ARCHIVE_ROOT" "$ROOT_FORM" || return 1
    archive_verify \
      "$REMOTE_LIVE_COPY" "$STATE/$ARCHIVE_ROOT" || return 1
    archive_present=yes
  fi
  test "$live_present" = yes || test "$archive_present" = yes || return 1

  git -C "$STATE" restore --source="$REMOTE_TIP" \
    --staged --worktree -- "$LIVE_ROOT" || return 1
  if test "$archive_present" = yes; then
    git -C "$STATE" rm -r -f --ignore-unmatch -- \
      "$ARCHIVE_ROOT" || return 1
    git -C "$STATE" clean -fd -- "$ARCHIVE_ROOT" || return 1
  fi
}

archive_inverse_finish || exit 1
```

The live-root pathspec is matched against the explicit source tree, so it works
when that path is absent from current archive `HEAD`; never pre-stage the
missing path with `git add`. The exact archive root is then removed from index
and worktree. `git clean` is permitted only for that already-authenticated
archive root and only to remove an exact untracked partial-move residue.
No restore or cleanup starts until the preflight has authenticated the whole
visible prefix; failed preflight evidence remains byte-for-byte and mode-for-mode
where the hook found it.
Require the index tree to equal `REMOTE_TIP^{tree}`, no staged, unstaged, or
untracked root residue, live/no archive, and byte equality with the remote
before calling this a restored-live terminal.

The rollback-preservation fixture snapshots the index, porcelain status, and
root evidence before attempting recovery with four invalid states: changed
archive bytes, a symlink archive root, a FIFO descendant, and an unrelated
dirty path. Each call must fail with the live root still absent and every
snapshot unchanged. Exact flat and folder moves still restore live and remove
only their authenticated archive roots.

#### Unpushed archive restoration pair

An unpushed, already-committed archive needs a distinct recovery gate. The
normal archive push above always requires exactly one outgoing commit and must
never be relaxed to accept two. Enter this pair gate only when a fresh fetch
still shows live/no archive at `REMOTE_TIP`, local `HEAD` is exactly one
previously authenticated archive commit ahead, and no other outgoing commit
exists. Preserve that commit under a reported
`refs/spacedock-recovery/archive/...` ref before changing either root.

A crash while building the inverse may leave that exact archive `HEAD` dirty
at one of two deterministic prefixes: the remote live root has been restored
while the archive root remains, or the remote live root has been restored and
the archive root has been removed/staged. Validate only those states with this
temporary-index replay:

```bash
archive_inverse_prefix_verify() {
  python3 - "$@" <<'PY'
import os
import pathlib
import subprocess
import sys
import tempfile

repo, remote_tip, archive_commit, live_root, archive_root = sys.argv[1:]


def fail(message):
    print(f"archive-inverse-prefix:mismatch:{message}", file=sys.stderr)
    raise SystemExit(1)


def run(*arguments, env=None, text=False, check=True):
    result = subprocess.run(
        ["git", "-C", repo, *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=env,
        text=text,
    )
    if check and result.returncode != 0:
        fail("git-query")
    return result


def commit(value):
    return run("rev-parse", f"{value}^{{commit}}", text=True).stdout.strip()


def tree(value, env=None):
    return run("write-tree", env=env, text=True).stdout.strip()


def exists(value, path):
    return (
        run("cat-file", "-e", f"{value}:{path}", check=False).returncode == 0
    )


for root in (live_root, archive_root):
    parsed = pathlib.PurePosixPath(root)
    if parsed.is_absolute() or root in {"", "."} or ".." in parsed.parts:
        fail("invalid-root")

remote_tip = commit(remote_tip)
archive_commit = commit(archive_commit)
if commit("HEAD") != archive_commit:
    fail("head-not-archive")
if commit(f"{archive_commit}^") != remote_tip:
    fail("archive-parent")
outgoing = run(
    "rev-list", "--reverse", f"{remote_tip}..HEAD", text=True
).stdout.splitlines()
if outgoing != [archive_commit]:
    fail("archive-not-only-outgoing")

if run("diff", "--quiet", check=False).returncode != 0:
    fail("unstaged-change")
if run("ls-files", "--others", "--exclude-standard", "-z").stdout:
    fail("untracked-change")
ignored = run(
    "ls-files",
    "--others",
    "--ignored",
    "--exclude-standard",
    "-z",
    "--",
    live_root,
    archive_root,
).stdout
if ignored:
    fail("ignored-root-residue")

changed_raw = run(
    "diff", "--cached", "--name-only", "-z", archive_commit
).stdout
changed = [
    value.decode("utf-8", "surrogateescape")
    for value in changed_raw.split(b"\0")
    if value
]
if not changed:
    fail("not-dirty-prefix")
for path in changed:
    if not any(
        path == root or path.startswith(root.rstrip("/") + "/")
        for root in (live_root, archive_root)
    ):
        fail(f"unscoped-path:{path}")

descriptor, replay_index = tempfile.mkstemp(prefix="archive-inverse-index-")
os.close(descriptor)
os.unlink(replay_index)
replay_env = os.environ.copy()
replay_env["GIT_INDEX_FILE"] = replay_index
try:
    run("read-tree", archive_commit, env=replay_env)
    run(
        "restore",
        f"--source={remote_tip}",
        "--staged",
        "--",
        live_root,
        env=replay_env,
    )
    live_restored_tree = tree(archive_commit, env=replay_env)
finally:
    try:
        os.unlink(replay_index)
    except FileNotFoundError:
        pass

current_tree = tree(archive_commit)
remote_tree = run(
    "rev-parse", f"{remote_tip}^{{tree}}", text=True
).stdout.strip()
if current_tree == live_restored_tree:
    if (
        not exists(current_tree, live_root)
        or not exists(current_tree, archive_root)
    ):
        fail("live-restored-root-presence")
    print("archive-inverse-prefix:live-restored")
elif current_tree == remote_tree:
    if not exists(current_tree, live_root) or exists(current_tree, archive_root):
        fail("complete-root-presence")
    print("archive-inverse-prefix:complete")
else:
    fail("unknown-prefix")
PY
}
```

Before accepting either prefix, re-run every archive-commit check: exact
message and parent, DCO, two-root scope, regular Git modes, root presence, and
`archive_verify` from `REMOTE_TIP:$LIVE_ROOT` to
`ARCHIVE_COMMIT:$ARCHIVE_ROOT`. Require all staged paths to be inside the two
roots, no unstaged or untracked path anywhere, and no ignored residue inside
either root. An exact `archive-inverse-prefix:live-restored` or
`archive-inverse-prefix:complete` result authorizes only idempotent completion
of the full inverse:

```bash
archive_inverse_finish || exit 1
test "$(archive_inverse_prefix_verify \
  "$STATE" "$REMOTE_TIP" "$ARCHIVE_COMMIT" \
  "$LIVE_ROOT" "$ARCHIVE_ROOT")" = \
  archive-inverse-prefix:complete || exit 1
CANDIDATE_RESTORE_TREE=$(git -C "$STATE" write-tree) || exit 1
test "$CANDIDATE_RESTORE_TREE" = \
  "$(git -C "$STATE" rev-parse "$REMOTE_TIP^{tree}")" || exit 1
archive_root_guard "$STATE/$LIVE_ROOT" "$ROOT_FORM" || exit 1
archive_git_root_verify \
  "$STATE" "$CANDIDATE_RESTORE_TREE" "$LIVE_ROOT" "$ROOT_FORM" || exit 1
test ! -e "$STATE/$ARCHIVE_ROOT" || exit 1
```

The same completion runs from a clean authenticated archive `HEAD`; prefix
verification is required only when staged dirt is already present. The final
candidate must change only the two exact roots relative to `ARCHIVE_COMMIT`,
contain the complete remote live root byte-for-byte, contain no archive root,
and have a whole-tree OID equal to `REMOTE_TIP^{tree}`. Then create exactly one
signed inverse commit:

```bash
git -C "$STATE" commit -s --only \
  -m "docs(dev): restore archive $SLUG" -- \
  "$LIVE_ROOT" "$ARCHIVE_ROOT" || exit 1
RESTORE_COMMIT=$(git -C "$STATE" rev-parse 'HEAD^{commit}') || exit 1
```

Validate the resulting pair with this structural gate:

```bash
archive_restore_pair_verify() {
  python3 - "$@" <<'PY'
import pathlib
import re
import subprocess
import sys

(
    repo,
    remote_tip,
    archive_commit,
    restore_commit,
    live_root,
    archive_root,
    slug,
) = sys.argv[1:]


def fail(message):
    print(f"archive-restore-pair:mismatch:{message}", file=sys.stderr)
    raise SystemExit(1)


def git(*arguments, text=True):
    result = subprocess.run(
        ["git", "-C", repo, *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=text,
    )
    if result.returncode != 0:
        fail("git-query")
    return result.stdout


def commit(value):
    return git("rev-parse", f"{value}^{{commit}}").strip()


def parent(value):
    fields = git("rev-list", "--parents", "-n", "1", value).split()
    if len(fields) != 2:
        fail("parent-count")
    return fields[1]


def signed(value):
    body = git("show", "-s", "--format=%B", value)
    return re.search(r"^Signed-off-by: .+ <[^<>]+>$", body, re.MULTILINE) is not None


def scoped(parent_commit, child_commit):
    raw = git(
        "diff-tree",
        "-r",
        "--no-commit-id",
        "--name-only",
        "-z",
        parent_commit,
        child_commit,
        "--",
        text=False,
    )
    paths = [
        value.decode("utf-8", "surrogateescape")
        for value in raw.split(b"\0")
        if value
    ]
    if not paths:
        fail("empty-commit")
    for path in paths:
        if not any(
            path == root or path.startswith(root.rstrip("/") + "/")
            for root in (live_root, archive_root)
        ):
            fail(f"unscoped-path:{path}")


def exists(value, path):
    result = subprocess.run(
        ["git", "-C", repo, "cat-file", "-e", f"{value}:{path}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


for root in (live_root, archive_root):
    parsed = pathlib.PurePosixPath(root)
    if parsed.is_absolute() or root in {"", "."} or ".." in parsed.parts:
        fail("invalid-root")

remote_tip = commit(remote_tip)
archive_commit = commit(archive_commit)
restore_commit = commit(restore_commit)
outgoing = git(
    "rev-list", "--reverse", f"{remote_tip}..{restore_commit}"
).splitlines()
if outgoing != [archive_commit, restore_commit]:
    fail("outgoing-not-exact-pair")
if parent(archive_commit) != remote_tip or parent(restore_commit) != archive_commit:
    fail("parent-chain")
if git("show", "-s", "--format=%s", archive_commit).rstrip("\n") != (
    f"docs(dev): archive {slug}"
):
    fail("archive-message")
if git("show", "-s", "--format=%s", restore_commit).rstrip("\n") != (
    f"docs(dev): restore archive {slug}"
):
    fail("restore-message")
if not signed(archive_commit) or not signed(restore_commit):
    fail("missing-signoff")
scoped(remote_tip, archive_commit)
scoped(archive_commit, restore_commit)

if (
    not exists(remote_tip, live_root)
    or exists(remote_tip, archive_root)
    or exists(archive_commit, live_root)
    or not exists(archive_commit, archive_root)
    or not exists(restore_commit, live_root)
    or exists(restore_commit, archive_root)
):
    fail("root-presence")
if commit(restore_commit) == archive_commit:
    fail("restore-not-distinct")
remote_tree = git("rev-parse", f"{remote_tip}^{{tree}}").strip()
restore_tree = git("rev-parse", f"{restore_commit}^{{tree}}").strip()
if restore_tree != remote_tree:
    fail("restore-tree-not-exact-inverse")
print("archive-restore-pair:exact")
PY
}
```

Freshly extract and compare `REMOTE_TIP:$LIVE_ROOT` with
`ARCHIVE_COMMIT:$ARCHIVE_ROOT` using `archive_verify`, and require
`archive_git_root_verify` for the remote live root, archived child root, and
restored live root. Only `archive:exact`, three `archive-git-root:exact`
results, and `archive-restore-pair:exact` permit the recovery push. Immediately
refetch and require the same remote root and exact two-commit range before
pushing the pair atomically:

```bash
git -C "$STATE" fetch --no-tags origin "$STATE_REF" || exit 1
PAIR_PARENT=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}') || exit 1
test "$PAIR_PARENT" = "$REMOTE_TIP" || exit 1
test "$(git -C "$STATE" rev-list --count "$PAIR_PARENT..HEAD")" -eq 2 ||
  exit 1
test "$(git -C "$STATE" rev-parse 'HEAD^{commit}')" = \
  "$RESTORE_COMMIT" || exit 1
archive_restore_pair_verify \
  "$STATE" "$PAIR_PARENT" "$ARCHIVE_COMMIT" "$RESTORE_COMMIT" \
  "$LIVE_ROOT" "$ARCHIVE_ROOT" "$SLUG" || exit 1
git -C "$STATE" push --atomic origin "$RESTORE_COMMIT:$STATE_REF" || exit 1
git -C "$STATE" fetch --no-tags origin "$STATE_REF" || exit 1
test "$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}')" = \
  "$RESTORE_COMMIT" || exit 1
```

The observed restored tree equals `REMOTE_TIP` byte-for-byte, so ordinary
startup now sees a clean live terminal state and may retry the normal
single-commit archive transaction. There is no rebase route for the pair: a
moved remote, extra/unknown outgoing commit, wrong message or parent, failed
archive comparator, non-regular Git mode, or non-exact inverse blocks with the
recovery ref preserved. If restoration cannot become durable, leave the remote
live terminal untouched and the holder blocked; never report archive success
or start another entity.

The restoration fixture runs flat and folder roots from an archive `HEAD` where
the live path is absent. For each form it crashes after live restoration and
again after archive removal/staging; prefix verification accepts the exact
state, idempotent completion produces the same signed inverse, and the exact
pair is observed through a disposable atomic push. Extra staged, unstaged, or
untracked dirt and same-root byte drift fail. The pair is accepted only by
`archive_restore_pair_verify`; the normal one-commit archive gate rejects it.
Adding a third commit, changing either message/parent, or making the second
commit anything other than the exact inverse tree also fails before push.

A rebase conflict, remote state containing both roots or neither, changed
descendants, multiple archive candidates, or unattributable dirt always stops
for captain resolution.

For the third scan set — terminal and live — perform this idempotent recovery
and archive transaction:

1. Choose exactly one authenticated terminal route:

   - **v1 hosted route:** require parseable
     `pr=pr-merge:{number}:artifact-v1:{product-artifact-sha256}` and
     `ledger_pr=ledger-merge:{ledger-N}:artifact-v1:{ledger-artifact-sha256}`.
     Recompute both canonical artifact digests, require the two `live_path`
     values to agree, and authenticate both exact numbered PRs through the
     exhaustive reconciliation rules above. Resolve `BASE`, fetch
     `origin "$BASE"`, and require both PRs to remain `MERGED`,
     same-repository, based on `"$BASE"`, and at their stored head OIDs/diffs.
     Retain their exact quoted `headRefName` values for cleanup. The product PR
     must still return the stored non-empty `mergedAt`.
   - **legacy direct-commit route:** require exactly
     `pr=direct-commit:{sha}` with no `ledger_pr`. Resolve `{sha}` unambiguously
     to a commit, fetch `origin "$BASE"`, and require
     `git merge-base --is-ancestor "$DIRECT_COMMIT" "origin/$BASE"`. Extract
     `origin/$BASE:docs/dev/ledger.csv` and run
     `ledger_verify legacy {task-id} {slug} {private-temp}`. That mode accepts
     historical blank/`n/a` metrics but still requires the canonical header,
     exactly one row keyed by task id, eight cells, and the exact slug. It
     never rewrites the row. Any failure blocks and reports the commit/row
     evidence; v0.13 sentinels and artifacts are never minted retroactively.

2. Require the live entity to hold `status={terminal}`, a non-empty
   `completed`, a passed verdict (case-insensitive for the direct-commit legacy
   route), and no non-empty `worktree`. Resolve `DURABLE_STATE` and prove it
   contains this complete terminal root. On the v1 route, require
   `completed="{mergedAt}"`, extract `origin/$BASE:docs/dev/ledger.csv`, and run
   `ledger_verify terminal {task-id} {slug} {private-temp} {started}
   {mergedAt}`. Only `ledger:exact` re-establishes the evidence that authorized
   v1 terminalization. The direct route uses only its reachability plus
   `ledger_verify legacy` evidence from step 1. A missing reference, changed
   timestamp, absent durable live root, or non-zero verifier leaves the entity
   live and reported.
3. On the v1 route, find local worktrees by the two authenticated, quoted PR
   `headRefName` values from `git worktree list --porcelain`. Absence is
   already-clean. Remove only clean worktrees whose recorded branch equals an
   exact authenticated head. A dirty worktree, mismatched branch, or worktree
   removal failure blocks archive. After successful worktree removal, attempt
   only `git branch -d -- "$PR_HEAD"` for the matching local branch. Absence or
   successful deletion is clean; refusal (including the normal squash-merge
   case) retains and reports the branch but does not block archive. Never
   remove `STATE`, the state branch, or the configured recovery checkout. The
   direct-commit route has no PR worktree/branch cleanup.
4. Run
   `spacedock status --workflow-dir "$WORKFLOW_DIR" --archive "$SLUG"`, then
   locate exactly one new `ARCHIVE_ROOT` under `_archive/` whose index carries
   the same task id and authenticated refs. Require `LIVE_ROOT` absent. Extract
   the full durable `LIVE_ROOT` and working `ARCHIVE_ROOT` to private temporary
   locations, then require `archive_verify` to print `archive:exact`; this
   accepts only Spacedock's valid index stamp and rejects a descendant
   path/byte change. Continue at step 3 of the archive durability transaction:
   stage both complete roots, validate and create its signed path-scoped
   commit, push the exact state ref, and observe the archive commit and tree
   remotely. Do not call `spacedock state commit` for this move.
5. An archive move, commit, or durability failure returns through restored-live
   recovery above before the hook reports failure only when the read-only
   rollback preflight authenticates an exact prefix. An archive validation,
   root-mode, comparator, or dirty-scope mismatch remains untouched and blocks;
   it never enters `restore`, `rm`, or `clean`. If the process crashes first,
   the narrow `_archive/` scan supplies the same move, stage, commit, push, or
   observation restart point. The hook may report archived only after step 4's
   remote observation checks pass.

This recovery path never calls `ledger_upsert`, prepares a finalization branch,
pushes a product or ledger branch, opens a PR, or terminalizes again. Its only
possible push is the archive transaction's exact state-ref push, so it cannot
rerun finalization or create a recursive ledger task. All non-archive writes
continue to use their self-contained `status --set` plus `state commit`.
Report each auto-advanced or recovered entity to the captain.

If the product PR is `CLOSED` without merge, report to the captain:
"{entity title} has PR {pr number} which was closed without merging. How to
proceed? Options: reopen it, explicitly approve an immutable superseding
attempt, or abandon it and leave the entity non-terminal pending an explicit
abandonment procedure." Reopen keeps the authenticated identity. The new-PR
option must run the supersession contract: new attempt-derived branch, new
artifact whose `supersedes` records this PR/artifact/branch, durable pending
ref, and reconciliation only on the new branch. Never clear `pr` to
local-merge, reuse the closed branch for a new PR, or overwrite it; those routes
cannot supply a newly authenticated host identity. Wait for the captain's
direction.

If `OPEN`, no action needed — the PR is still in review.

If `gh` is not available, warn the captain and skip PR state checks.

## Hook: idle

Run the same four-set scan and state machine as startup: ordinary PR-pending
entities, empty-`pr` or pending product-PR resume markers, live terminal
recovery, and the narrow partial-archive rollback/completion check. This is the workflow's
lifecycle scan: the generic event loop fires this idle hook and owns no
competing PR or archive scan of its own, so a workflow with no `pr-merge` mod
never reaches for `gh` in its loop. Report any reconciled, advanced, or
recovered entities to the captain.

## Hook: merge

Run the README's lifecycle-hook holder prerequisite as a fresh command before
reading or mutating entity state in this hook, rerun it after the captain's
approval before persisting the artifact or PR reference, and rerun it after
that state commit before any branch push, host query, or PR create.

Resolve the PR base once: `BASE=$(spacedock dispatch trunk --workflow-dir {dir})` — the workflow's configured integration trunk (default `main` when no `trunk:` key is set). `dispatch trunk` emits exactly a **bare branch name** (e.g. `main`), so `$( )` yields `$BASE` clean (command substitution strips the single trailing newline). Always quote `"$BASE"` at use sites — the push, the rebase, the draft, and the `gh pr create --base` below.

Before constructing the draft, enforce the accepted-validation boundary from
the README:

1. Read `task_id` and `slug` from the live entity and run
   `ledger_verify premerge {task-id} {slug}
   {worktree}/docs/dev/ledger.csv`.
2. Require `ledger:exact` (exit 0). Missing (41), duplicate (42), or
   incomplete (43) returns the merge hook without pushing, creating a PR,
   clearing `mod-block`, or cleaning the worktree. Repair the live
   Measurement record and rerun the line-preserving upsert; never substitute
   `0` or `n/a` for missing evidence.
3. Confirm the product-branch diff changes at most this task's row plus
   unrelated rows already brought in as a union. A rework round updates the
   same `task_id`; it never appends a second row.

**PR APPROVAL GUARDRAIL — Do NOT push or create a PR without explicit captain approval.** Before presenting the draft, construct the full PR body so the captain reviews the actual prose that will land on GitHub.

Compute the audit-link inputs first: short SHA via `git rev-parse --short HEAD` in the worktree directory (if it exits non-zero — no commits, detached HEAD — substitute the literal string `main` and report the fallback to the captain); owner/repo via `gh repo view --json nameWithOwner --jq '.nameWithOwner'`; short entity-id slot via `spacedock status --short-id {entity ref}` from the workflow directory (shortest-unique-prefix for sd-b32 workflows, literal stored ID for sequential and slug, matching the status table's ID column).

Build the full PR body using the template below — motivation lead,
`## What changed`, `## Evidence`, `---` separator, `[{short-id}](...)` audit
link, and `Closes {issue}` line if frontmatter `issue` is set. Serialize its
current head/diff/body tuple as the canonical product artifact, encode it, and
persist `pr_artifact_v1={product-base64url}` together with
an empty `pr` and
`mod-block=pr-merge:product-draft:v1:{product-artifact-sha256}` in one
`status --set` plus `spacedock state commit` before pausing. The non-empty
digest-bound draft block prevents terminalization but authorizes no branch
push, PR create, or other outward mutation. Decode the field back from the
durable entity, require its exact bytes to hash to the draft block, and present
that digest with the draft; the captain approves that exact durable artifact.
Never use `status --set --force` to bypass this guard; its refusal means the
approval/finalization ceremony is incomplete.
A post-approval rebase may require reconstruction only by invalidating that
approval and presenting the complete replacement for renewed approval; never
silently rebuild under an earlier approval.

Then present the draft to the captain:

- **Title:** {entity title}
- **Branch:** {branch} -> $BASE
- **Changes:** {N} file(s) changed across {N} commit(s)
- **Files:** {list of changed files}
- **Body:**

  ```
  {constructed body}
  ```

Wait for the captain's explicit approval before pushing. Do NOT infer approval from silence, acknowledgment of the summary, or the gate approval that preceded this step — only an explicit "push it", "go ahead", "yes", or equivalent counts.

**On approval:** Treat the presented draft as approval of a specific
head/diff/body tuple, not of a branch name. Before any outward push, fetch
`origin "$BASE"` and rebase the worktree branch onto it. If
`docs/dev/ledger.csv` conflicts, resolve it as the README's
`task_id`-keyed union: retain every unrelated row from both sides, replay this
task's latest upsert from the live Measurement section, and never take the
whole file from `--ours` or `--theirs`. Re-run `ledger_verify premerge` and the
scope/diff checks after the rebase.

Compare the full HEAD OID, `origin/$BASE` OID, SHA-256 of
`git diff --binary "origin/$BASE"...HEAD`, and audit-link SHA to the tuple the
captain saw. If any value or body input changed, reconstruct the complete title
and body from the now-current entity and HEAD, present the entire revised draft,
and obtain a new explicit captain approval. Repeat the fetch/rebase/comparison
after that approval. No push or create is allowed until one complete approval
survives this check unchanged.

Once the current tuple is approved, reload the inert
`pr_artifact_v1` field from the holder, decode it, and require its digest to be
the one presented. If the refetch/rebase checks changed any field, persist the
replacement encoded field, empty `pr`, and its new digest-bearing draft
`mod-block` in one set-plus-commit and present it again. Otherwise set
`pr_artifact_v1={approved-product-base64url}` and
`pr=pr-merge:pending:artifact-v1:{artifact-sha256}` together with
`mod-block=pr-merge:product-pr:v1:{artifact-sha256}` in one holder mutation
followed immediately by `spacedock state commit`, then re-read the durable
entity and verify the decoded artifact digest, body digest, and every field
byte-for-byte. Replace the prior candidate field value rather than adding
metadata to the entity body; a `mod-block` owned by another mod is a conflict
to report, not something to overwrite. If serialization, field round-trip, or
durability fails, perform no outward action.

Run the startup hook's exact product-PR reconciliation before continuing. One
eligible PR is persisted in `pr` and reused; ambiguity blocks. When none exists,
fetch `origin "$BASE"` and require `"origin/$BASE"` to equal the stored
`base_oid`; never push the local trunk. Recheck the stored `head_oid` and
`diff_sha256`, then push only the exact approved object with the quoted
explicit refspec
`git push origin "${STORED_HEAD_OID}:refs/heads/${STORED_HEAD}"`. If fetched
`"origin/$STORED_HEAD"` already exists, require it to equal
`STORED_HEAD_OID`; a different remote head blocks instead of being updated.
No commit, rebase, body rebuild, or other head-changing action is permitted
after the artifact is durable. If the head push fails, report to the captain
and leave the marker and branch unmerged; a local merge has no host `mergedAt`
or protected-main-safe finalization path and is not a valid fallback.

After the push, fetch the quoted `"$STORED_HEAD"` and require
`"origin/$STORED_HEAD"` to equal `STORED_HEAD_OID`, then run exact
reconciliation again **immediately before** creating anything. If it finds one
eligible PR, persist and reuse it. Only zero host results permits create.
Decode the exact stored body to a private file, verify its SHA-256 again, and
run `gh pr create --base "$BASE" --head "$STORED_HEAD"
--title "$STORED_TITLE" --body-file "$BODY_FILE"`; this avoids shell
re-serialization of the approved bytes. Load title and body only from the
digest-bound artifact rather than rebuilding them. Capture the created
URL/number, re-read it through the same repo/head/base/OID/title/body checks,
and immediately set
the unchanged `pr_artifact_v1={product-base64url}` together with
`pr=pr-merge:{number}:artifact-v1:{product-artifact-sha256}` in one holder
mutation followed immediately by `spacedock state commit`. If create returns
an error or its outcome is uncertain, reconcile
before any retry. If the `pr` write or durable state commit fails after
creation, leave the marker and artifact intact; startup/idle recovers the
single exact candidate without issuing create. Within this mod, only a
completed all-state zero-result reconciliation permits `gh pr create`, and
every uncertain create outcome returns to reconciliation before retry. If
`gh` is not available, warn the captain and leave the marker and branch
unmerged.

### PR body template

Lead with motivation + end-user value; audit metadata goes at the bottom. The goal is that a reviewer or future debugger sees the "why" first and the audit link last.

**Template structure (top to bottom):**

| Section | Required | Content |
|---|---|---|
| Motivation lead | **yes** | 1 sentence, ≤ 25 words, blending motivation and end-user value. No parentheticals. |
| `## What changed` | **yes** | Action-verb bullets, 3–5 total, each ≤ 15 words. One change per bullet. No rationale inside the bullet — if a change needs justification, it belongs in the task body, not the PR. |
| `## Evidence` | **yes when validation ran** | Test suites with `N/N passed` format, 1–2 bullets. Do not include per-test-class breakdowns or enumerated suite lists — one pass ratio per suite, plus at most one line confirming live-probe verification. |
| `## Review guidance` | optional | 1 line pointing reviewer at the critical file or risky change — include only when a stage report explicitly flagged it |
| `---` separator + `[{entity-id}](/{owner}/{repo}/blob/{short-sha}/{path-to-entity-file})` | **yes** | Audit link, at the bottom |
| `Closes {issue}` | **yes when issue set** | Under the audit link, using the value exactly as it appears in frontmatter, e.g., `#48` or `owner/repo#48` |
| `Related: {siblings}` | optional | Under Closes, only when stage reports flagged follow-ups |

**Extraction rules (apply deterministically from the entity file):**

| PR body section | Source in entity file | Transformation |
|---|---|---|
| Motivation lead | Entity body paragraph(s) between closing `---` and the first `##` heading | Condense first paragraph to 1-2 sentences. Lead with impact or action verb — not "This PR" or "This task". Blend motivation + value. |
| What changed | Implementation stage report's `[x]` DONE items | One action-verb bullet per meaningful unit. Collapse sibling bullets that describe the same thing. Drop `[x]` markers. Do NOT include "what we deliberately did NOT change" bullets — scope boundaries belong in the task body, not the PR, unless a validation stage report flagged them as risk. |
| Evidence | Validation stage report items that assert AC verification (typically rerun-test items) | One bullet per suite with `N/N passed` format. Include any quantitative result the stage report explicitly called out (wallclock delta, size %, perf). Fallback to implementation report's self-test items if no validation stage exists. |
| Review guidance | Explicit "focus on X" / "risk here" notes in either stage report | 1 line. **Omit if no such note exists.** |
| Audit link | Short entity id from `spacedock status --short-id {entity ref}` (shortest-unique-prefix for sd-b32, literal stored ID for sequential and slug), path from the file's repo-relative location, short SHA from `git rev-parse --short HEAD` run in the worktree directory | Format as `[{short-id}](/{owner}/{repo}/blob/{short-sha}/{path})` |
| Closes | Entity frontmatter `issue` field (exactly as written) | Prefix `Closes ` |
| Related | Explicit "related task" / "follow-up" mentions in stage reports | 1 line. **Omit if none.** |

Target total length: **60-120 words**.

**Key design decisions:**

1. **Lead with motivation + end-user value.** First content is a 1-2 sentence user-facing impact statement. The audit link moves to the bottom as audit metadata.
2. **Prescribed sections + extraction rules** — not a strict verbatim template, not free-form. The mod specifies headings and source subsections; the FO paraphrases rather than pasting.
3. **Evidence section is conditional on validation stage.** Non-validated workflows fall back to implementation self-test evidence.
4. **Review guidance and Related are opt-in.** They appear only when stage reports explicitly flagged them, to prevent bloat.

After the reconciliation-owned root-scoped commit has persisted the
artifact-backed `pr` field, report the reused or created PR to the captain.

**On decline:** Leave the branch unmerged and ask the captain whether to keep
it or abandon the branch while the entity remains non-terminal pending a
separate abandonment procedure. Local merge is not offered: it cannot supply
the product-PR `mergedAt` or the protected-main-safe ledger-finalization PR
this lifecycle requires.

Do NOT archive yet. The entity stays at its current stage with `pr` set until
the product PR and its protected-main-safe ledger-finalization PR have both
merged. The FO handles final verification, terminal advancement, and archival
through the startup/idle state machine above. After terminal advancement, the
live file remains restart-visible until the terminal recovery path re-verifies
the landed row, removes any authenticated clean worktree, attempts safe branch
deletion without gating on squash-merge refusal, and archives last. A product
`MERGED` state alone never clears the block.
