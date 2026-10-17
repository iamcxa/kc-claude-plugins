## Review-finding disposition

Before repair authorization, product bytes and the recorded candidate revision stay
unchanged. Read-only inspection, non-mutating reproductions, existing tests and
throwaway-checkout probes are allowed. Report/gate commits may advance repository
HEAD without changing the candidate. Validators recommend `PASSED` or `REJECTED`;
new findings or changed evidence re-enter this checkpoint.

The four evidence fields are released user and normal workflow; observable harm;
affected value acceptance criterion or non-negotiable boundary; and trigger
evidence. Field 3 uses `value-ac[AC-N]`, `captain-ruling[YYYY-MM-DD]`, or
`contract[repo/relative/path#anchor]` plus a nonblank claim. `none:` with a rationale
does not establish Material.

- **Material:** all four fields establish supported-workflow harm to a protected
  boundary or value acceptance criterion.
- **Deferred risk:** hypothetical, unsupported, unobserved or unpromised trigger;
  record what would make it material.
- **Polish:** no current user-visible loss or protected boundary is at risk.
- **Needs decision:** the task cannot own the scope, product or compatibility call.

A `Follow-up:` line in Scope is not accepted scope by itself: the first stage of the
receiving task to meet it assesses it against its stated reason and earlier rulings. It builds the line only when the change alters no behaviour that an
accepted criterion, a Captain ruling or a journey contract relies on; otherwise it
returns the line to FO as a Needs decision. It records which, and why.
A finding FO declined in a committed gate summary or under `### FO declines` is settled:
a later validator does not report it again unless the candidate changes the lines or the
evidence the decline names, or new evidence would make it Material.

