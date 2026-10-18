---
title: special-role-triggers follow-ups declined at the #664 delivery gate (fence indent, uncommitted task, wording)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO at the #664 delivery gate (head b300d9ba, 2026-10-18); reasons also in that task's gate summary.

- Deferred risk: `kc-dev-flow-2/scripts/role_triggers.py` recognizes a fence opened with 0 to 3 plain spaces, while headings now accept any indent, tab or no-break space, so an event-shaped heading inside a fence opened with such an indent would count. No task writes such a fence today.
- Deferred risk: a live task file that is not committed makes `pr_watch.py tasks` print `cannot tell` and exit 2 (as AC-4 specifies). Material only if FO routinely leaves a live task uncommitted at idle.
- Polish: the implementation report says event B fires on 16 entries; the script gives 17. The design says "the third `- Cycle N` line"; the code uses N >= 3, the sounder reading. Relay's owner-link-and-account Cycle 3 was a validator REJECTED, so a chief-engineer call, not a waiver, is the expected answer there.
