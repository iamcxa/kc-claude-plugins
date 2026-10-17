### `ideation`

FO may dispatch ideation on a stronger model when the design is hard to reverse,
such as an event model, an architecture or a security boundary, and says so in
the dispatch. The default ensign invokes `kc-dev-flow-2:ideation` before useful work, using the
work item's recorded variant/profile and the skill's own profile routing table.
FO aligns direction and requests research when it can change a decision; the
worker authors the PRFAQ and the artifact each recorded surface owes. When
`## FO alignment` records alignment as needed, FO records the alignment result
as a `Result:` line before dispatching the worker. Missing skill or profile
authority requires a hold report rather than a baseline or default-profile
substitution.
Ideation writes no repository file, branch or commit: the design, the criteria and any
ADR draft live in the task file, and a draft carries no ADR number.

- **Outputs:** Current design definition and acceptance criteria with reproducible
  evidence clauses; unresolved decisions identified for the user.
- **Gate content:** Present PRFAQ/Mermaid with matching actors, order, branches,
  approvals and stops, acceptance evidence/limits, and each recorded
  `Surfaces:` value's artifact. The gate is not presentable without the
  artifact each recorded surface owes. Before `spacedock gate prepare`, FO runs
  `python3 <package>/scripts/design_surfaces.py check <task>`; a non-zero exit,
  including a missing `## Acceptance criteria` section or one that declares no
  criterion, means the gate is not presentable, and FO includes the checker's output in
  the gate material. Required diagram defects or missing current-stage
  evidence block recommendation and gate preparation/presentation; honest
  unverified future checks do not.
  FO may correct design prose/Mermaid to reflect established decisions under an
  actual Captain grant covering that task's exact design section; reuse a matching
  standing grant. Template adoption grants no authority. Record the decision basis;
  preserve scope, acceptance criteria, risk acceptance, product code, worker
  evidence, prior reports, approvals and verdicts. Withdraw an affected open binding
  before editing, then reprepare through the applicable SD lifecycle. Other
  corrections require an authorized author; hold where no supported route applies,
  without inventing same-stage rework. Corrections neither replace user approval nor advance stages.

