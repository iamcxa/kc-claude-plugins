---
title: "The POC close path has never been walked end to end, and two defects sit on it"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-poc-close-path
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: xve5t292zy54mncx0xm6m3v0
gates:
    version: 1
    records:
        - id: gate:xve5t292zy54mncx0xm6m3v0:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:xve5t292zy54mncx0xm6m3v0-backlog-1
              briefing:
                id: briefing:xve5t292zy54mncx0xm6m3v0:backlog:attempt-1:revision-1
                digest: sha256:428b3078ab6c5b24debe880d41a5fbe352e745e8b981d87cef75bd5e73592ad2
                room-ref: ./poc-close-path-never-walked/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:xve5t292zy54mncx0xm6m3v0:backlog:1
                briefing: briefing:xve5t292zy54mncx0xm6m3v0:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T07:48:37.215439Z"
                decision: approve
                reason: Captain approved in chat 2026-09-14 after the FO presented both defects with their reproductions, the reason for one task rather than two, and the Pilot selection justified by the previous POC selection on this path running past budget and needing a mid-flight amendment.
              application:
                target-stage: ideation
                state: pending
---

Running a POC to close surfaced two defects on the same path, neither of which any
existing test reaches. Both were found by driving the path, not by reading it, on
the work item `capture-oracle-never-caught-anything` (archived, 2026-09-14).

**A correction round cannot be pinned after a POC prove stage.**
`poc-close-guard.py` reads `## POC outcome` and `## POC close measurement` as
top-level sections of the work item (`one_yaml_section(text, "POC outcome",
"poc_outcome")`), so the prove stage must write them there.
`profile-contract-loader.py`'s `work_item_authority` retains every `##` section
except one matching `^## Stage Report`, so both land inside the accepted-authority
hash. A `kc-dev-flow-feedback/v1` context compares the current authority against
the rejected pin's, so after any prove stage the two can never be equal and the
loader answers `FEEDBACK_CONTEXT_MISMATCH: rejected work item or authority
changed`. Reproduced on the real item. The Captain had ruled two prose findings
should be fixed; the First Officer had to route that pass as an ordinary build
attempt authorized by a section in the work item, because the designed mechanism
was structurally unavailable.

**`poc-close-guard.py` silently misreads an empty `started:`.** Line 63 is
`re.findall(r"^started:\s*([^\n#]+?)\s*$", frontmatter, re.MULTILINE)`. The `\s*`
after the colon matches the newline, so on an empty field the capture group begins
on the following line and returns that key. Reproduced standalone against the
frontmatter shape `spacedock new` emits: the match is `'completed:'`. The guard
then rejects a correct close with `admitted_at must equal frontmatter started`,
naming a comparison the reader cannot see is against the literal string
`completed:`. Nothing errors; the field is simply read as something else.

## Accepted outcome

A POC that reaches its prove stage can be corrected and closed without the First
Officer inventing a route, and `poc-close-guard.py` either reads an empty `started`
as absent or refuses it by name. Which of those two the guard should do, and
whether the POC route gets a correction path at all or the outcome sections move
out of the authority region, are the questions the shape stage answers — both
defects are reported here with their reproductions, not with their fixes.

## Non-goals

- Changing what `## POC outcome` or `## POC close measurement` must contain.
- Changing the `kc-dev-flow-feedback/v1` schema's fields.
- Reopening the archived `capture-oracle-never-caught-anything` item.
- Any change to `spacedock-dev/subspace-relay`.

## Acceptance criteria

- **AC-1** A fixture POC work item that has passed a prove stage accepts a
  `kc-dev-flow-feedback/v1` correction context, or the route it must take instead is
  stated in the POC profile contract where a First Officer will read it. Whichever
  shape is chosen, driving it on the fixture succeeds and the previous behaviour is
  shown to fail.
- **AC-2** `poc-close-guard.py` on a work item whose `started:` is empty either
  reports the field as absent or refuses with a message naming the empty field. It
  does not capture the following frontmatter key. A regression test covers the empty
  field, a populated field, and an absent field; mutating the fix reddens it.
- **AC-3** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 and the existing
  `poc-close-guard.test.py` still passes unchanged, or its change is named and
  justified in the stage report.
- **AC-4** Both defects are reproduced against their pre-fix behaviour at the
  candidate revision, so the tests are seen to fail before they are seen to pass.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: >
    Two coupled defects on one path, with a real design question the First Officer
    must not settle alone: whether the POC route gets a correction path, or the
    outcome sections move out of the authority region, or a POC's answer to findings
    is only its direction and the contract should say so. Pilot rather than POC
    because a shape stage is exactly what that question needs — and because the
    previous item on this path selected POC, ran past its budget, needed a Captain
    amendment mid-flight, and closed with direction `change` for those reasons.
    Selecting POC again would repeat a measured mistake.
  obligations:
    architecture: [No change to the feedback schema's fields or to what the POC outcome sections must contain; the fix lands in the contract or the loader's authority rule, not in an adopter]
    implementation: [scripts/poc-close-guard.py; the POC profile contract or scripts/profile-contract-loader.py depending on shape's ruling; a regression test for the started field]
    testing: [AC-1 to AC-4 at the candidate SHA; both defects reproduced pre-fix]
  scope_boundary: >
    No change to the kc-dev-flow-feedback/v1 schema fields, to the required contents
    of the POC outcome sections, to the archived capture-oracle item, or to
    spacedock-dev/subspace-relay.
  semantics_unchanged: false
```
