# Learning

This file collects project-specific practices learned from completed kc-dev-flow-2
tasks. Entries are added or removed as a whole; an entry is never edited in place.
Each entry names an Applicability (when it applies), a Practice (what to do), and
the Evidence behind it.

## Name only an instrument that actually produces the claimed output

### Applicability

When an acceptance criterion, stage report or PR claim in this repository names an
existing script or the pinned release-please fixture as the instrument that
verifies which package(s) a commit is attributed to.

### Practice

Bind the claim only to output that instrument actually produces. Nothing in this
repository routes a commit to a package: scripts/version-parity-check.sh runs only
scripts/release-please-config-check.sh plus python3 version-string comparisons, and
the single release-please import (scripts/release-metadata.test.sh,
probe_release_please_first_tag) builds a first-release tag string through
buildNewVersion/TagName. A commit's resolved package list can only be obtained by
constructing CommitSplit/CommitExclude ad hoc against
scripts/fixtures/release-please-runtime, so a criterion that asserts an existing
repository check does it cannot be satisfied without adding a script.

### Evidence

Verified on origin/main 2026-09-17: `git grep -n "CommitSplit\|CommitExclude"
origin/main -- scripts .github` returns nothing, and the only
`require('release-please')` is scripts/release-metadata.test.sh inside
probe_release_please_first_tag. The cost of not checking is recorded in
spacedock-state/dev2:_archive/release-please-exclude-paths.md at commit 46186575
(validation-gate attempt-1 withdrawal, then the Captain's route-A amendment of
AC-2).

## exclude-paths guards by the key's presence, not its listed paths

### Applicability

When a new top-level workflow-state directory (docs/dev, docs/dev2, docs/ship and
siblings) is introduced, or when extending the contents of a package's
exclude-paths in release-please-config.json is proposed, at the release-please
17.3.0 pinned by scripts/fixtures/release-please-runtime.

### Practice

Do not add the path. The guard is the presence of the exclude-paths key on a
package entry, not its contents: a commit whose changed paths match no package
directory prefix is never bucketed to any package, so that package's
exclude-paths is never consulted for it. Give a package entry that lacks the key a
value matching its siblings instead. Bounded: this holds only for paths outside
every package directory and only for this pinned version; a path inside a package
directory is still compared.

### Evidence

Merge d701df3de01ec3eb0b1e7f5c227d36cdd9d512e1 (iamcxa/kc-claude-plugins#467) adds
one line, kc-dev-flow's "exclude-paths": ["docs/dev"], and adds docs/dev2
nowhere. The measurement behind that narrowing - ["docs/dev"], ["docs/dev2"],
["unrelated-string"] and [] producing an identical drop, with a pre-change
control resolving the empty commit to [kc-dev-flow] - is in
spacedock-state/dev2:_archive/release-please-exclude-paths.md at commit 46186575,
under the AC-2 items of '## Stage Report: implementation' and '## Stage Report:
validation'.
