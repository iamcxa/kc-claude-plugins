## What

Two rounds of hardening on `scripts/ship-flow/accept-evidence.sh`, the ship-flow accept station from #373, in one PR.

**S29 — fail closed on a command that did not run, an out-of-tree read, and an unparseable pair.** A base run that exits 126 or 127 means "the command did not run", not "the falsifier flipped". A command or variant reading `~`, `$HOME`, an absolute path, or `..` out of the repository is refused. A command whose paths cannot be extracted is refused instead of skipped.

**S30 — the static without-it check refuses only a no-op variant.** It refuses when the variant alters none of the read paths the candidate changed, warns when it alters some, and recognises every shape a variant alters a path with: `git show <sha>:<path> >`, `git checkout <sha> --`, `git rm [-f]`, `rm [-f]`, `sed -i`, `>` and `>>`, `mv`. Paths the command reads that the candidate did not change are inputs and are ignored by this rule.

## Why

On 2026-09-05 the station accepted a block whose command was `<checker> ~/.claude/... && echo clean || echo derivative; on candidate exits 0, ...`: prose after a semicolon ran `on` as a command, exited 127 at the base, and any non-zero read as a flip. The First Officer's manual run caught it.

The first hardening fixed that and then refused two good pairs the same day: a variant written as `rm -f <file>` was invisible to the extractor, and a command that reads its own fixture was refused because the fixture was not restored. The class the strict rule guarded, a variant narrower than the command, has no recorded instance; the entry that claimed one (S24) had been corrected the day before.

## Verified by the First Officer

At the candidate, in a real git worktree, against today's real Evidence blocks:

| block | expected | result |
|---|---|---|
| plan-flow AC-5 round 2 (`rm -f` variant) | accept | ACCEPT, WARN: variant restores 1 of 3 changed read paths |
| plan-flow AC-3/6/7 round 2 (reads a fixture) | accept | ACCEPT |
| plan-flow AC-4 round 3 (the S29 block) | refuse | REFUSE: out-of-tree path |
| this PR's own block | accept | ACCEPT by its own station |

The earlier fixtures keep their outcomes except `mutant-drop-path`, which moves from REFUSE to ACCEPT-with-WARN by design. The without-it pair is the flip itself: `accept-evidence.sh mutant-drop-path.md | grep -q WARN` exits 1 at `BASE_SHA` (the pre-S30 station refuses that fixture and prints no WARN) and 0 at the candidate; the variant restores the one changed file the command reads.

## Residual

- Three Evidence rounds were spent on one commit: round 4's block used the whole contract test as its without-it and reported a base exit that had not been observed; round 5 fixed the block only. Recorded as worker-conduct in the batch evidence.
- The WARN on a partially restored variant is advisory; the base run stays the only execution and decides the pair.
- Fixture files copied from real blocks carry `BASE_SHA`/`CANDIDATE_SHA` that point at branches of this repository; if those branches are deleted, the SHA check on those fixtures needs a clone that still holds the objects.

Part of DEV-94 (POC 4). AC-2 rounds 3–5.
