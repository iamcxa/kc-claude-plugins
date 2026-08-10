# State Recovery Runbook

Load this runbook only after `scripts/dev-flow-state-prereq.sh` returns 75, 76,
or 77, a setter/commit transaction is interrupted, or an archive move is
partial. It is procedure, not a second authority: `docs/dev/README.md`, the
selected mods, Spacedock, and the state Git ref retain their declared roles.

## Stop conditions

- Exit 75: holder is dirty.
- Exit 76: holder is clean and locally ahead.
- Exit 77: holder is clean and diverged.
- Any other non-zero result: follow the named prerequisite error; do not infer a
  recovery class.

Do not use `git reset --hard`, broad `git clean`, force-push, `ours`, or
`theirs`. Preserve unknown dirt and the exact holder path for inspection.

## Attribute a dirty holder

The replay contract is `spacedock 0.26.0 (contract 3)`; the README's
`commissioned-by` value records workflow provenance, not the recovery runtime.
Before replay, require the first line of `spacedock --version` to equal that
contract. A different version leaves the evidence untouched.

Read staged, unstaged, and untracked paths from the exact holder. A recoverable
non-archive mutation changes one flat entity file or one complete folder entity
root. Identity comes from that path, never from searching body text.

For a delivery mutation, decode the entity's canonical `pr_artifact_v1` and
require its digest and `live_path` to match the product `mod-block` or `pr` ref.
Legacy `ledger_pr` and `ledger_artifact_v1` bytes are preserved but authorize
nothing. A direct-commit historical route authenticates its commit, task ID, and
anchored path without inventing an artifact.

Reproduce the intended setter in a private disposable workflow seeded from the
dirty parent:

```bash
REPLAY=$(mktemp -d "${TMPDIR:-/tmp}/dev-flow-replay.XXXXXX") || exit 1
REPLAY_WORKFLOW="$REPLAY/docs/dev"
REPLAY_STATE="$REPLAY_WORKFLOW/.spacedock-state"
mkdir -p "$REPLAY_STATE" || exit 1
cp "$WORKFLOW_DIR/README.md" "$REPLAY_WORKFLOW/README.md" || exit 1
git -C "$STATE" archive "$LOCAL_HEAD" "$LIVE_ROOT" |
  tar -x -C "$REPLAY_STATE" || exit 1
spacedock status --workflow-dir "$REPLAY_WORKFLOW" \
  --set "$SLUG" "${EXACT_FIELD_ASSIGNMENTS[@]}" || exit 1
git diff --no-index --quiet -- \
  "$REPLAY_STATE/$LIVE_ROOT" "$STATE/$LIVE_ROOT" || exit 1
```

Require every dirty path inside the authenticated entity root and byte-for-byte
equality with the replay. Corrupt encoding, a wrong digest/path, multiple roots,
or any replay mismatch blocks and preserves evidence.

An exact replay permits rerunning the same setter followed immediately by its
companion `spacedock state commit`. A compound terminalization replays each
ordered setter prefix and then the full sequence; never commit a matched prefix
alone.

## Dirty holder behind remote

Only a dirty root already authenticated and replay-matched against its local
parent may be carried forward.

1. Create a mode-0700 recovery directory outside the repository.
2. Record the local parent, slug, ID, live root, action class, ordered assignment
   arrays as data, authenticated artifact/ref, complete root bytes, and a
   path/digest manifest.
3. Restore only the enumerated entity paths from the local parent. Remove only
   authenticated untracked paths already copied to the recovery record.
4. Require a clean holder, fetch the state ref, prove local HEAD is still its
   ancestor, and fast-forward.
5. Re-resolve the same task and re-authenticate every field the action reads or
   writes. An unrelated append is compatible; deletion, move, identity change,
   or a changed consumed field blocks on the remote tip.
6. Replay the full action from the new tip in a disposable workflow, execute it
   against the holder, compare the complete root, commit, push, fetch, and
   require remote equality.
7. Remove the recovery directory only after equality is observed.

Unauthenticated dirt, dirty divergence, and unknown extra paths have no restore
route. Leave them untouched.

## Clean local-ahead holder

Inspect every commit in `REMOTE_TIP..LOCAL_HEAD`, its full path set, exact
message, and authenticated frontmatter transition. Retry only one recognized
`state: update {slug}` commit that changes one entity root exactly as a pending
lifecycle action would. Push HEAD to the exact state ref, fetch, and require
observed equality.

For divergence, only that recognized outgoing commit may be rebased onto the
fresh state tip. Stop on conflict and revalidate the rewritten commit before
push. Unknown, multiple, or unrelated commits remain blocked.

## Archive recovery

Archive is a path-scoped Git transaction because the supported Spacedock cannot
commit an already archived slug. Before restoring or removing anything, require:

- all dirty paths lie within the authenticated live and archive roots;
- filesystem and Git entries are regular files with permitted modes;
- the remote live root is exact;
- the archive comparator passes, allowing only the deterministic archive stamp;
- the index equals the remote tree or one exact validated archive/live prefix.

A byte, mode, symlink, gitlink, special-file, extra-index, or scope mismatch
leaves all evidence untouched. Normal archive push is one signed commit. The
only two-commit recovery gate is an authenticated archive commit followed by its
exact signed inverse, rooted at the freshly fetched live tip.

After recovery, rerun `scripts/dev-flow-state-prereq.sh`. Resume ordinary
lifecycle work only when it returns 0 and the observed holder equals the remote
state tip.
