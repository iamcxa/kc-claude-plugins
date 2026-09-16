# Learning

This file collects project-specific practices learned from completed kc-dev-flow-2
tasks. Entries are added or removed as a whole; an entry is never edited in place.
Each entry names an Applicability (when it applies), a Practice (what to do), and
the Evidence behind it.

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
only Escape. kc-journey-map/scripts/popup-browser-check.mjs, landed in
ba444ed9b2afc1b6b353286322c9ea5828fed0d6, now hit-tests and real-clicks every
control across 31 checks, including Close in each of the four unavailable render
states; its hitTestable helper is the greppable form of the assertion.

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
non-localhost origin. Both the false limit and its disproof are in the archived
canvas-document-popup task record at closure revision
c560e7ce7109c5ccc4ace87d69ff5506a46e799b. The delivered popup-browser-check.mjs
still prints the superseded LIMIT line at its shared-board-origin block, so the
script alone reproduces the wrong conclusion; agent-browser --help confirms
--args passes browser launch args through.
