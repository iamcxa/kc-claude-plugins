# Investigation evidence

Candidate: de564ef9e2b608d4106d96c56448e22f31a6fc5b. No repair applied.

These are public synthetic fixture observations, not live provider/gate evidence.
`commands.json` identifies the commands, exits and outputs. `results.json` names
8 paired real-adapter/check/question cases; `audit-results.json` names 39 paired
guard cases with controlled reviewer rows; `head-results.json` names 5 paired
merge-head cases. A final harness exit 0 means current behavior matches the
expected differences, including unsafe accepts. It does not certify a repair.
`rule-audit.json` inventories 44 rules, including inspected-only shared guards.
`proposal-not-applied.patch` is illustrative and was only counted/context-checked.

To reproduce, copy the five .py files into a fresh, owned dispatch scratch root.
Set `PRODUCT_WORKTREE` to a clean checkout of the candidate above, set `TMPDIR`
to that scratch root, and run each script with `python3 -B` from the product
worktree: investigate.py, adapter_probe.py, audit_probe.py, head_probe.py.
They import the candidate's test fixtures and use its GH executable double;
no live PR operations are performed. Fixture directories must not already exist.
The retained scripts replace only the original worktree constant with the
explicit `PRODUCT_WORKTREE` input. Other path normalization is listed by digest
in normalization.json. The original harness commands ran before normalization.

The initial two audit failures were harness calibration: a duplicate declaration
in both text inputs and a wrong legacy missing-step expected exit. Their output
and assertion files remain. The final audit starts fresh with corrected definitions.
No real task/report/reviewer bodies, private repositories, secrets or personal data
are included; per-case logs and eight saved factual records are synthetic.
