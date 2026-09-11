# Approved exact local commits and unpublished Draft stack

Approval provenance: Kent answered **批准** to the immediately preceding recommendation accepting the round-3 exact schema comment closure and approving `schema-comment-correction-evidence/local-commit-review.md`. This authorizes exactly three local product commits. It does not authorize push, PR creation/linking, readiness, merge, release, code edits or another review loop. Prior findings/immutable rounds remain unchanged.

Created absent refs in three owned isolated worktrees using ordinary `git commit`, without hook bypass or added author/coauthor attribution. Before each commit the index exactly matched the approved tree and approved path list. After each commit, full parent, tree, subject, changed-file set and clean status matched. `commits.json` and commit transcripts preserve those bindings.

| Local branch | Commit | Parent | Approved tree | Files; + / - |
|---|---|---|---|---|
| `codex/journey-planning` | `0d69be164ccdcd1b3509f3577d6bd03a468f8f36` | `c9c5752fda853737d4a937ad7f59564c5651ca53` | `b5bbc4d8ef0f800072fd9635389c481590ff05fb` | 42; +6994 / -311 |
| `codex/journey-release-inspection` | `818260a8c14b504dae8d3989ba9c710226255b74` | `0d69be164ccdcd1b3509f3577d6bd03a468f8f36` | `058298ebd763f16e395c77ebeea1474a193cddc0` | 35; +2194 / -160 |
| `codex/journey-local-progress` | `aabb8e7e8320b65fa852feae961df2e438d8f002` | `818260a8c14b504dae8d3989ba9c710226255b74` | `8a581c3c1bdbc2d11783f35cc040cfafd72c9f3f` | 10; +427 / -27 |

Exact file lists are copied as `unit-N-files.json`; generated additions are 5,245 lockfile lines in the bottom unit, one full native-JSON line in the middle, and zero in the top. Deleted generated lines are zero. These are approved adjacent candidate counts, with generated lines retained in totals. Retained version parity and 17/17, 67/67, 9/9 producer results remain tied to exact approved source trees; no new tests/install/browser/RoboRev run occurred.

## Concrete unpublished delivery draft

`draft-stack-review.md` contains all three full English titles/bodies in bottom-to-top order. `draft-units.json` binds every canonical worktree/repository/branch/base SHA/candidate SHA/title/body-file tuple, body SHA-256 and mode 0600. Exactly one Candidate line occurs per body. Each body links the approved exact-path manifest and immutable split-root task at committed state SHA `6c2d5af977ffa659bbd94ab862e56be7c225ff6e`, never a code SHA. `preparation-bindings.json` records explicit origin/repository resolution and the absent issue/Planning Receipt.

Live main at preparation moved from approved ancestry `c9c5752fda853737d4a937ad7f59564c5651ca53` to `c1564b218799b3baf07fc5e6c346bb6dcc476a7e`. Commits were not rebased. All exact-pair `merge-tree --write-tree` preflights returned 0; the bottom combined tree is `3319ba6f63257f636ea848a56443cbe9b73bc1c0`. Middle/top results equal their approved trees. No integration conflict was observed; this mechanical preflight does not validate the combined runtime. Full pair commands/results are retained in `merge-preflights.json`.

The installed native `gh stack` is available. Future authorized delivery uses the bound canonical Draft units and links their resulting full PR URLs with `gh stack link --base main`, without `--open` or standalone ghstack. No publication command ran. Existing Draft #394 remains untouched. CI cost per PR is unmeasured; hosted/CI delivery and final user acceptance are not claimed.

All pre-existing registered worktree/branch/HEAD tuples are unchanged; exactly three owned worktrees were added. Original root `codex/journey-stack-recut` remains clean at the approved base. Original tacoma source/dirty lockfile/rooms, old snapshots/branches and running services were not mutated. State remains implementation. Next authority belongs to the Captain: review the concrete full stack before push/PR authorization.
