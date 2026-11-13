feat(kc-dev-flow-2): check Pilot criterion proof records

Pilot designs could reach their gate with an acceptance criterion that recorded no proof. The existing design check now requires loose command, observed-exit and output-path tokens outside the Falsifier, or a named reason under a Not provable now heading. It applies to unapproved Pilot designs in ideation, including those already in progress; ideation-approved designs and other profiles/stages retain their current checks.

Extend the observer's historical-schema sentence and repair the affected fixture records. Workflow text, its 6099-word budget and versions are unchanged. Recognition checks written records, not actual execution: a planned clause with the same tokens can pass.

Validation: design surfaces 244 tests (4 skipped), dispatch records 136 (1 skipped), laws 85 (1 skipped), dispatch stage 52 (none skipped), and the real SD dispatch harness passed. The two archived trial designs replay correctly; 11 guard mutations and a workflow-word mutation are caught. Repository skill lint, ADR lint, number guards and comment ratio pass. The old dispatch-stage base failure omitted SPACEDOCK_BIN; the correctly configured candidate suite passes.

Compatibility replay covers 236 public Pilot tasks, a 113-task adopter source and a drifted 99-task source (previously 98); the former 137-task source was not located, and the 113-task source could not be uniquely identified by count. Private inputs and logs are not archived. The observer's actual post-release behavior, hosted CI and RoboRev remain unverified; CI cost per PR was not measured. No CI configuration changed.

Fixture overlap for the budget sibling is limited to test_dispatch_stage.py::test_worth_requirement_uses_native_stage_for_yaml_status_values and test_sd_dispatch.py's criteria-parity parity() writer. FO owns the product push, Draft PR and RoboRev.
