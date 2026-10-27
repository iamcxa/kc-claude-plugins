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

## Never write git config from a worktree of this repository

### Applicability

When a worker, validator or acceptance script for this repository would exercise a
failure path by writing git configuration (for example `git remote set-url origin
...`, `git config`) from inside a worktree checkout, including the Captain's main
checkout or any worktree of the repository.

### Practice

Do not write git config in any worktree of this repository: every worktree shares
one config, so one write changes every checkout. Run such a step only in a throwaway
`git clone` in a temp directory, and say so in the dispatch scope notes and in the
acceptance script. If a shared value is changed by mistake, restore it from a
recorded original, so record the original value before any config read-modify step.
Bounded: one observed incident; this does not show the ban alone prevented a repeat,
since the acceptance script was also moved into a throwaway clone.

### Evidence

Validation cycle 1 of workflow-checkout-must-match-trunk-readme
(iamcxa/kc-claude-plugins#631) ran `git remote set-url` in a worktree and rewrote
remote.origin.url for every worktree to /nonexistent/origin.git. The validator
restored it by inference (sibling clone and PR repository; the original value was
not recorded) and FO confirmed it against FETCH_HEAD from before the incident. The
later cycles carried an explicit ban in the dispatch records (implementation-2,
implementation-4, validation-2, validation-3) and ran that step in a throwaway clone
with remote.origin.url identical before and after; no repeat was observed in those
cycles. Recorded in
spacedock-state/dev2:_archive/workflow-checkout-must-match-trunk-readme.md at
closure revision 173fd173224bac844133b87d6ca1ef99d9eb25b7 (validation Summary of
cycle 1 and the dispatch/ records). Existing rules checked: implementation
principles ban only `git stash` for the same shared-state reason; the workflow
README's Review-finding disposition allows throwaway-checkout probes but never says
a worktree config write is forbidden, so no rule states this practice.

## Measure the words FO reads at each moment, not one file's size

### Applicability

A kc-dev-flow-2 change whose goal is to cut what First Officer (FO) reads, such as
moving rule text out of the adopted README (references/sd/workflow.md) into a mod,
a script's printed output or another file, where acceptance is stated as a word
count.

### Practice

State the acceptance number as the words FO reads at each lifecycle moment
(startup, idle on an open PR, idle on a merged PR, after the archive, the merge
ask): every passage and every script output that instructs a step due at that
moment, counted the same way for the unchanged base and for the candidate, with
each moment required to fall below its base. Do not accept the size of the one
file the text left (for example WORKFLOW_WORD_BUDGET in
kc-dev-flow-2/scripts/lint-skills.py) as the measure, because that number can fall
while FO's total reading rises. Bounded: one task; the redesign also gave each
step one home, so the count is not shown to be the only cause of the reduction;
the recount script lives only in the archived task's validation folder, not in the
repository; and a validator found the first recount script under-counted one
moment, so recount with an independent copy.

### Evidence

In task fo-lifecycle-mod (iamcxa/kc-claude-plugins#643, closure revision
d2c1d80085b2699e4cad79eecd4c13fe2230647d) the first design's criterion AC-2
bounded only references/sd/workflow.md words (5561 down to 5483); validation
recommended PASSED at that design, yet FO then measured FO's total reading as up
by about 507 words while the README shrank by 80, and the Captain sent the task
back (amendment 3). The redo counted words FO reads per moment, and the landed mod
cut that total from 2036 to 1699 with every moment lower. Recorded in
spacedock-state/dev2:_archive/fo-lifecycle-mod.md under '### Why the cycle-2
design grew' and '### Words FO reads at each moment', and in the Cycle 1 FO line
of its feedback record. Checked 2026-10-15: git grep for a per-moment reading
count over ab9334edf03d3f248bd8e28a6be979307f355f36 finds only the per-file budget
in lint-skills.py; no project rule, selected-profile text or stage principle
states this practice.

## List every input before promising a verdict survives later history

### Applicability

A kc-dev-flow-2 task in this repository that designs or reviews a check run over
committed history (such as the state-branch laws runner) and promises that a
violation, once committed, keeps its verdict after later commits (for example "stays
red until an anchor moves"), or that answers a review finding of the form "a later
change erases a committed violation".

### Practice

Before the design gate, list every input the verdict reads (files read at the run
revision, task files enumerated at the tip, the README or config passed in at run
time) and write the persistence promise as one property test: after the event,
commit every later change the history allows (edit, delete, archive, rename, and a
change to each run-time input) and require the same exit code and output. When a
review finding of this class arrives, treat it as a finding about that list: add the
input it names and every sibling input to the list and to the test in the same
cycle, instead of repairing the one reported read. If an input cannot be pinned to
the event, narrow or drop the promise in the design and ask the Captain, rather than
shipping an absolute that later history can undo. Uncertain: whether this ordering
would have avoided the rework, since the Captain's actual ruling was to drop the
promise.

### Evidence

Task dev2-laws-check (iamcxa/kc-claude-plugins#651, closure revision
f3e31ba99a5c5832c9c0fab276fef9af645bf5f5). The first design promised that a
committed violation stays red. Review then found four ways later history erased one:
reading record bytes at the run revision, re-adding a record, deleting a task, and
removing learn from the README. FO fixed the class with a property test after the
third, and the fourth made FO stop under the circuit breaker; the Captain amended
the design to judge only each push's own range, and round 4 was clean. In the
archived task, the implementation cycle 3 phase 1 report's class audit listed
readme_extensions (the README passed at run time) as an input and noted the property
test could fix it as a constant; the property test's fixture varied edit, delete and
archive of task and record files and not the README, and the next review round
(Feedback Cycles, Cycle 3) reported exactly that input. Bounded: one task; the fix
chosen was to drop the promise, so the record does not show that a property test
varying the README would have been cheaper than that ruling.

## Compare a shrunk rule with what its script rejects before cutting it

### Applicability

A kc-dev-flow-2 change in this repository that shortens a README
(references/sd/workflow.md) rule into a pointer to a script that checks it, such as
dispatch_records.py, design_surfaces.py or observer_check.py, to meet the workflow
word budget.

### Practice

Before cutting a clause, compare each clause of the sentence with what the script
rejects, not only with what its failure messages say: run the script on one input
that the dropped clause forbids, and keep the clause in the README whenever the
script lets that input through. For each kept clause, pin the README phrase with a
need string in test_sd_dispatch.py, because pins written for the removed parts do
not cover it. Bounded: one task; the sentence was restored after an external review
round, so the record does not show that this comparison would have found the gap
before review, and validation had passed the first candidate with the clause
missing.

### Evidence

Task workflow-budget-ratchet (iamcxa/kc-claude-plugins#658, closure revision
098dcbd39972ead7323235a72ffb60761926da65, landed
6ea3a4724515b974c34beb16bc3382683b6d45b9). The first candidate (57673bfd) cut 63
words and shrank the resumed-dispatch sentence of references/sd/workflow.md to 'with
the same check', dropping 'never a pointer to another record'. The author had read
each script's failure output first (design table 'Measured pointer candidates'), and
validation passed that head with 4 of 4 CI checks green. Codex round 1 raised one
P2: kc-dev-flow-2/scripts/dispatch_records.py is_pointer rejects only words in
POINTER_WORDS and its own docstring says 'Reuse the checklist of implementation-2.'
passes, so nothing else forbids that pointer. Repair e65a91ba restored 15 words
(budget step -79 to -64) and added the need string 'never a pointer to another
record' to the resumed-dispatch pin in kc-dev-flow-2/scripts/test_sd_dispatch.py;
with the README phrase removed that pin fails, and Codex round 2 was clean. At
landed revision 6ea3a472 the phrase is in references/sd/workflow.md and in the pin
(git show, checked in this evaluation). The pre-existing pins had not caught the
drop. Recorded in spacedock-state/dev2:_archive/workflow-budget-ratchet.md under
'### Feedback Cycles' and '## Stage Report: implementation (cycle 2)'.

## Update every parser of a script mode in the change that adds a new output line

### Applicability

A kc-dev-flow-2 change in this repository that makes a script mode print a new kind
of line, such as a new diagnostic from `dispatch_records.py --names`, when another
script in the package runs that mode and parses its output.

### Practice

Before the change lands, search the package for every caller of that mode (for
example `git grep -n 'dispatch_records.py' -- kc-dev-flow-2/scripts`) and read what
each caller does with a line it does not recognize; update each parser in the same
change and add a test that feeds the new line to it. Do this per mode, not per
script: the design checked the consumer of `--newest` (`pr_watch.py tasks`) and kept
`--newest` unchanged for it, but did not check the consumer of `--names`. Bounded:
one task; Codex round 1 found the gap, so the record does not show the author would
have found laws_check.py without that review, though the call
`run_check("dispatch_records.py", "--names", ...)` in laws_check.py names the script
and a search by script name lists it; the cost was one repair cycle (phase-1
investigation, FO fix authorization, a fresh validation recheck), and the fix was
one regex.

### Evidence

Task worker-loads-declared-package (iamcxa/kc-claude-plugins#661, closure revision
0b9cf6d72d02ac5241ca4dbb805152c5eb89f0e7, landed
a915acaa39cea0cbc84dda176a8e1241057b2eed). The first head 4989c97b made
`dispatch_records.py --names` print `no 'Candidate: <40-hex head>' line` for a
validation record without one. Validation passed that head with falsifiers on the
new part and on `--newest`. Codex round 1 P2 (review:5558106991):
kc-dev-flow-2/scripts/laws_check.py, function l2_dispatch_record_complete, runs
`dispatch_records.py --names` and its regex matched only 'bare package script name'
lines, so the new line made the L2 law raise Cannot ('output this runner does not
parse', exit 2) instead of reporting an L2 violation. Repair 7d169549 widened that
one regex and added
L2Test.test_a_validation_record_without_a_candidate_line_is_an_l2_violation_not_an_unjudgeable_run,
which fails 1 of 38 under each of three mutations; Codex round 2 was clean. At
landed revision a915acaa, git show of the commit shows the one-line change to
laws_check.py (checked in this evaluation). Recorded in
spacedock-state/dev2:_archive/worker-loads-declared-package.md under '### Feedback
Cycles', '### Bounded existing-code check' and '## Stage Report: implementation
(cycle 2)'. Existing rules checked: implementation principles' Existing-code
capability check covers adding or removing a capability and searching for consumers
before a no-consumer claim, not a printed line that another script parses; the
workflow README's dispatch and delivery rules and the project CLAUDE.md do not state
it; the eight root learning.md entries (blob d4bd974e) cover neither it nor script
output parsing.

## Compare a newly refusing checker's verdicts on every committed task file

### Applicability

A kc-dev-flow-2 change in this repository that makes a checker script newly refuse
something in committed task files, such as an exactly-one or no-duplicate rule added
to design_surfaces.py, when the script also runs in `check --seed` mode or at a gate
over tasks the author did not write.

### Practice

Before the implementation report, run the script from main and from the candidate
over every committed task file (the state checkout and its _archive/) in each mode
the script has (`check` and `check --seed`), compare exit code and message per file,
and explain each changed verdict as intended or repair it. Do not offer the count of
files with zero instances of the new pattern (for example '0 duplicates in 69
files') as the evidence that no existing task newly fails: that count does not
exercise how the script reads lines, such as lines inside fenced blocks. Bounded:
one task; validation's dispatch asked for the check, so this record does not show
the implementer would have run the verdict comparison unprompted; the adopter
corpora were extracted by session scripts under /tmp that are not in the repository,
and the three relay verdict changes in two tasks were judged expected by the
chief-engineer, not independently re-derived.

### Evidence

Task ui-design-review-in-ideation (iamcxa/kc-claude-plugins#663, closure revision
aa74f1046540d98ddd047a92eb252db1e6f115d2, landed
18e161d99b3cd4bbf4a2f755249687418fcf48d7). The round-2 repair added an exactly-one
`Surfaces:` count to design_surfaces.py; its implementation report measured '69
existing task files (45 here, 22 beirut-dev2, 2 montpellier-v2) had 0 duplicates'
and the one-line counts were fence-blind. Validation of cycle 3 then ran base and
candidate `design_surfaces.py check` and `check --seed` over 64 task files here: 63
identical, 1 differed, `_archive/amendment-form-check.md` going from exit 0 to exit
1 with "has 3 'Surfaces:' lines, expected exactly 1" because fenced fixture lines
were counted. The chief-engineer then required a main-versus-candidate verdict
comparison over four corpora (258 task files); after the narrowed repair the
comparison showed 0 verdict changes in this state, subspace-web and qnow and 3
expected changes in two subspace-relay tasks, and the same comparison was repeated
after the roborev High repair. Cost of the miss: one repair cycle plus a fresh
validation recheck. Recorded in
spacedock-state/dev2:_archive/ui-design-review-in-ideation.md under '### Feedback
Cycles' (Cycle 3), '## Stage Report: implementation (cycle 2, round 2)', '## Stage
Report: validation (cycle 3)' and '## Stage Report: implementation (cycle 3)'.
Existing rules checked 2026-10-18: implementation, validation and ideation
principles, the workflow README and the project CLAUDE.md state no per-file
main-versus-candidate verdict comparison for a newly refusing checker (grep of the
package README, references and skills for corpus, newly refus and existing task file
finds nothing); the nine root learning.md entries cover consumers of printed output,
persistence inputs and README pointers, not this.

## Name a new skill mode in the skill's description in the same change

### Applicability

A change in this repository that adds a mode, command or intent to an existing skill
(a new row in the SKILL.md mode table and a reference file) and is reviewed or
accepted before anyone checks the skill's frontmatter description.

### Practice

In the same change that adds the mode, edit the frontmatter `description` of that
SKILL.md to name the new intent and the phrases a user would type for it, and keep
it within the 1024-character limit; the mode-table row alone does not make a request
reach the skill. scripts/skill-frontmatter-lint.sh checks only that name and
description are present and non-empty, and says it does not judge the description
text, so nothing but review catches the omission. Bounded: one task; live
skill-discovery routing was not run, so this record does not show that the added
phrases route a request such as 'accept this release' to the skill, only that the
missing intent was a review P1 and the one-line repair cleared it; and the author's
design named the mode-table row and the reference file but not the description, so
the record does not show the author would have caught it unprompted.

### Evidence

Task release-acceptance (iamcxa/kc-claude-plugins#709, closure revision
99f2a409826eb2be170f3ff16aebb01519df5955, landed
1694ade349babde54f6c9791df77be8c63b48bbb). Codex round 1 on head e3a92e98 left one
P1: kc-journey-map/skills/kc-journey-map/SKILL.md frontmatter description did not
mention the new accept-release mode, so a plain request such as 'accept this
release' might not load the skill. The head had passed validation cycle 1 (263
tests, mutations, clean merge) with the mode-table row and accept-release.md already
in place and the description unchanged. Repair d84ebde0 changed one description line
(698 to 892 characters; four trigger phrases and the accept-release sentence),
skill-frontmatter-lint.sh exited 0 before and after, Codex round 2 found nothing,
and the cost was one investigation, FO fix authorization, one repair cycle and a
fresh validation recheck. FO decided to add no test because a substring test on
metadata proves no routing. Existing rules checked: the project CLAUDE.md and
docs/dev2 README state only that the lint requires a parseable frontmatter with
non-empty name and description; the implementation, ideation and validation
principles and the pilot profile say nothing about a skill's discovery description;
the ten root learning.md entries (blob b6ba5556) cover none of it. Recorded in
spacedock-state/dev2:_archive/release-acceptance/index.md under '### Feedback
Cycles', '## Stage Report: implementation (cycle 1 repair)' and '## Stage Report:
validation (cycle 2)'.
