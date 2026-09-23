# Ideation principles

FO owns goal and direction alignment. Before design, check `## FO alignment` in
the task file; when the heading is absent, when it records alignment as needed
with no `Result:` line, or when the route includes ideation and records no
`Surfaces:` line, stop and report instead of starting the design. Ask for
research when missing facts can change the decision; the worker authors the
requested artifact, not user approval.
Prefer the smallest working mechanism for the accepted goal. Before proposing an
existing-code capability change, apply the [bounded existing-code check](../implementation/principles.md#existing-code-capability-check);
use or repair what exists before adding a replacement. Record its conclusion in
the same design, with a proportional observation showing why the change is needed.
Use one PRFAQ with a future-facing proposition, short FAQ and acceptance evidence
plan. Mermaid must match the prose's actors, order, alternatives and stops.
Each recorded `Surfaces:` value owes its own artifact, fidelity before prettiness:
- `ui` (a person sees or operates it; read from the surface, not the diff) —
  a short text proposal first, then a preview of it, run and operable for an
  interactive surface rather than a static screenshot; use a mechanism the
  repository already has, mark it disposable, and add no online resource
  without Captain approval.
- `db` (schema, migration or row-level security change) — the schema change
  shown explicitly (a column table, or a Mermaid `erDiagram` when relations
  change) and the migration source of truth named.
- `api` (API, server function or CLI interface change) — the exact
  input/output shape including error cases, or the one named check that pins it.
`none` uses the PRFAQ/Mermaid alone. The gate is not presentable without the
artifact each recorded surface owes. Reconcile material research and feedback
into the same definition before handoff. Correct contradictions in depicted or
required boundaries and missing current-stage evidence before reporting completion;
if blocked, report the concrete gap. Future implementation checks may remain unverified.
In the existing Stage Report checklist, name each acceptance criterion separately with its
actual current evidence or an honest not-yet-verified statement. A range such as
AC-1..AC-3 is not per-criterion mapping; a future proof plan is not a passed result.
Return only unresolved material scope, interface, acceptance-criteria or authority
choices to FO. Keep routine wording and test placement in the recommendation,
not separate user decisions. Do not begin implementation.
