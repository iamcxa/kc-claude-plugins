---
title: relay agent-front-door replayed as a prod design
variant: kc-dev-flow-2
profile: prod
merge: pr
status: ideation
---

## FO alignment

Surfaces: none
Visible change: none

## Design

### Security review

Security review: security/ideation-1.yaml
Security focus file: none
Security finding 1: AC-5
Security finding 2: Needs decision: set RELAY_OPENAPI_PUBLIC=true only after publish-admission, or record the ADR 29 trigger as accepted
Security finding 3: declined: moot if the OpenAPI link is dropped (finding 2); existing read paths, not new
Security finding 4: AC-6
Security finding 5: AC-7
Security finding 6: AC-8

## Acceptance criteria

**AC-5**: /llms.txt says the document is the author's text, not instructions; the contract test fails without the sentence; AC-1 has a hostile-document run.
**AC-6**: the reviewer section ends with a logout step and the FAQ states the 30-day session.
**AC-7**: the design states the write bound per share and names the control, or scopes a cap.
**AC-8**: the issues repository's owner and triager are recorded before the URL ships.
