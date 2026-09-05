# Ideation review

- Entity: `profiled-pr-review-capability-protocol`.
- Shaped artifact: `docs/superpowers/specs/2026-09-05-kc-pr-review-capability-protocol-v1.md` at feature commit `41186709`.
- Delivery base: `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`; moving `main` is not rebased into the accepted shape.
- Proposed slice: implement only the default-off Lite path; Standard, Full, and Custom remain protocol-only.
- Exact shape delta: executable Lite has zero expansion reserve; every `ExpansionRequest/v1` ends `ABORTED_INCOMPLETE: unsupported_expansion`.
- Review evidence: 30 fresh Claude Opus 5 xhigh reviews; final verdict PASS with no optional refinements.
- Mechanical baseline: runtime 372/0, posting 156/0, ablation 82/0.
- Recovery: extend the existing `review-ablation` harness; do not build a second measurement runner.
- Implementation stops: more than 20 changed files, more than 4,100 total changed lines, or more than 1,800 focused schema/catalog/fixture/test lines returns to shape.
- Current estimate: 18 changed files, about 4,025 total changed lines, and 1,700 focused lines.
- Authority boundary: no default enablement, posting change, merge, release, Nightwatch, Forge, or paid experiment is authorized here.
- Remaining evidence: implementation does not exist; hosted CI cost per PR and the 33.3% speed result remain unmeasured.
