## Decision records

The implementation worker writes one ADR file per decision by its stage principles.
Validation runs `python3 <package>/scripts/adr_lint.py docs/adr --since <base>`, which
requires every record the candidate added or changed, plus `--require <numbers>` for
each `ADR:` number the task's `## Number guards` reserves and any number the
implementation report names; exit 1 or a missing record returns through the existing
feedback route, and exit 2 is a configuration error that returns to FO.

