# Amendment 1 document review

Candidate: fef21735308e7e807d04a93a5506de5284dde436.
Base: 139feeaee7ce037a0c6535568cd6bd103155cbae.

The existing scope-note quote keeps its original first sentence. Its new final
sentence is the exact conditional pointer requested in implementation-1-message-2.
It instructs reading before actual Paseo use, rather than selecting Paseo for
every local check. Existing dispatch-record enforcement remains unchanged.

The 228-word guide routes attended pages, including a login where the Captain
performs human verification, to EXTENSION.md's Human terminals and pages. That
section already owns placement and sign-in/confirmation boundaries. Repository
instructions take precedence. Unattended checks use the repository adapter
directly, without a required Paseo attempt. No challenge automation or bypass is
described. CI remains unchanged.

Retained limits map to their workarounds: Captain keyboard/input method to native
setter, bubbling input event and readback; React Native buttons to a new snapshot
ref and browser_click; 15-second browser_timeout to start/store/poll; untested
signature drawing to browser_drag and a repository-adapter fallback. The observed
visible-tab requirement, background workspace/host placement, cleanup and per-step
tool/reason reporting remain. An unexecuted browser step stays not run.

Both existing browser runs remain evidence at
20eb8255daf0f1267a8c0dd16daf0705a7cf82ba. The attended foreground run records Paseo
screenshots and a ref-based click; the background run records failures and the
per-step agent-browser fallback. Neither run establishes an unattended Paseo
default or executes this amended guide. Fourteen original evidence files retain
their SHA-256 hashes; no browser run, new worker or retained-service cleanup was
performed in this cycle.

EXTENSION.md is 1112 words, versus 1101 at base (+11). Only the listed Paseo
dispatch moment and its copied worker scope note grow; the 228-word guide is
read before Paseo use. Startup/resume, PR-idle, archive and merge-ask passages and
script output are unchanged. Workflow, lint budget, dispatch checker, package
README, adopter files and versions are unchanged. doc_impact.py lists no other
retained document. The superseded criteria and prior stage reports stay intact;
active replacements use AC-6/7/8 with the mandated Captain-amendment marker.
