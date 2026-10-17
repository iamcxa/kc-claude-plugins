---
title: Follow-ups from round 3 of the prod security check review (#656 F2 to F4)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

# Follow-ups from the third review round of the prod security check

Declined under the round-3 rule of the review-finding disposition (README step 5) at validation-3 of prod-security-review-gates (PR #656, head a741e357). None blocks the task; each is filed here with its reason.

- F2, Polish: the `kc-dev-flow-2/README.md` sentence that lists what `check` verifies omits the security review. Declined because AC-8 of that task forbids a README diff; changing it needs a Captain ruling on AC-8 scope.
- F3, Deferred risk: `check` requires the `Security focus file:` line but cannot tell whether the named file is the true focus. Declined because judging truth needs a reviewer, not the check; no observed wrong focus file.
- F4, Deferred risk: the hand parser reads `severity:` from the item's own line, so a real report with a deeper-indented continuation could be read differently by a YAML parser. Declined because 21 real reports, plain and fence-wrapped, read with 0 false holds, and the shape lock refuses a mismatched severity count.
- Observation, out of scope (implementation-9 report, 2026-10-17): `decision_ledger.py` names a task by `path.stem`, which gives `index` for a folder-form task (`<slug>/index.md`). Not yet shown to cause a wrong ledger entry.
