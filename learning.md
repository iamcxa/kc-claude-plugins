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

## Hit-test canvas controls; don't trust a keypress to prove clickability

### Applicability

kc-journey-map canvas work that renders an interactive control anywhere inside
tldraw's InFrontOfTheCanvas slot, and any claim that a canvas control is verified
by a browser run.

### Practice

Mount click-target UI with createPortal to document.body as a sibling of
`<Tldraw>` rather than in the in-front slot: .tl-canvas__in-front sets
pointer-events: none by design for canvas-space overlays. In the archived record
(closure revision c560e7ce7109c5ccc4ace87d69ff5506a46e799b), a live
getComputedStyle measurement up the Close button's ancestor chain — button, popup
chrome, dialog, .tl-canvas__in-front — read none at every step even though the
dialog used showModal(); no case was observed where showModal()'s top-layer
promotion overrode that inherited value. For each interactive control, assert
document.elementFromPoint at the control's own bounding-box centre resolves to
that control and dispatch a real pointer click asserting the resulting effect. A
passing Escape or other keypress path does not by itself establish that a control
is clickable: in that same record, the passing runs had exercised only Escape,
which in that run was delivered to the focused element and did not go through
hit-testing, so the Close button's click-through defect went undetected until a
real pointer click was tried.

### Evidence

The Captain clicked Close on the ideation preview and the popup would not close,
while that stage's report had already declared the controls verified by real
Playwright runs; reproduction showed a visible button with a sane bounding box
whose own-centre document.elementFromPoint returned `<html>`, traced to tldraw's
`.tl-canvas__in-front { pointer-events: none }`. The passing runs had exercised
only Escape. kc-journey-map/scripts/popup-browser-check.mjs, landed in merge
ba444ed9b2afc1b6b353286322c9ea5828fed0d6 (iamcxa/kc-claude-plugins#468), now
hit-tests and real-clicks every control across 31 checks, including Close in each
of its three unavailable-state cases (bad ref, bad path, unmapped repo); its
hitTestable helper is the greppable form of the assertion. The defect report and
the measured root cause are in
spacedock-state/dev2:_archive/canvas-document-popup.md at commit
c560e7ce7109c5ccc4ace87d69ff5506a46e799b, under '## Material finding — the Close
control does not work' and '## Correction to FO's own root-cause claim'.

## Map a non-localhost origin at Chromium's DNS layer, not with a Host header

### Applicability

A kc-journey-map browser check that must run against a non-localhost origin, such
as exercising JOURNEY_ALLOWED_HOSTS or a shared-board origin, in an environment
with no root and no writable /etc/hosts.

### Practice

Map the hostname at Chromium's own DNS layer by passing
`--host-resolver-rules=MAP <host> 127.0.0.1` through `agent-browser --args`, then
perform a genuine top-level navigation over that origin. Do not record "needs a
DNS or hosts-file mapping this environment cannot make without root" as a limit
before trying it. In the archived record (closure revision
c560e7ce7109c5ccc4ace87d69ff5506a46e799b), the one attempt to substitute
`agent-browser --headers` with a Host override
(`--headers '{"Host":"sharedorigin.test"}'`) against the real Vite dev server
hung and never completed, which the archived record attributes to Host being a
reserved header CDP would not rewrite for that request; that single observation
is the basis for preferring `--host-resolver-rules` over a `--headers` Host
override.

### Evidence

The implementation stage reported the shared-board-origin browser run
unachievable in this environment and substituted a curl --resolve HTTP-layer
check; validation disproved that limit with agent-browser
`--args "--host-resolver-rules=MAP sharedorigin.test 127.0.0.1"`, confirmed first
against a bare HTTP server echoing the received Host header and then by running
the full open, render and close loop against the real canvas over the
non-localhost origin. Both the false limit and its disproof are in
spacedock-state/dev2:_archive/canvas-document-popup.md at commit
c560e7ce7109c5ccc4ace87d69ff5506a46e799b, under '## Stage Report: implementation'
and '## Stage Report: validation'. Verified on origin/main 2026-09-17: `git grep
-n "LIMIT" origin/main -- kc-journey-map/scripts/popup-browser-check.mjs` still
returns the superseded shared-board-origin LIMIT line, so the script alone
reproduces the wrong conclusion; `agent-browser --help` lists --args as browser
launch args.
