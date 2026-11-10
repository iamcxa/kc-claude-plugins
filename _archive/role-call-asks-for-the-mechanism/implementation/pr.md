fix(kc-dev-flow-2): ask for the shared mechanism in owed role calls

Three failed validations or three dispatches on one symptom now ask the chief engineer what single mechanism produces the findings and what one change closes the class. Declining those calls requires an `unrelated:` reason naming at least two findings with distinct causes; outcome-only declines leave the call owed. The check establishes form, not the truth of the causes.

Preserve trigger thresholds, model/date rules, plain declines for other event families and the existing reminder states. Append the Captain-approved amendment to ADR 0026; the workflow template and version files are unchanged.

Validation: 488 tests completed across test_role_triggers, test_delivery_gate, test_pr_watch and test_dispatch_records (486 passed, 2 environment-dependent checks skipped). Six reverse mutations caught, including the 0.36.0 baseline. At state bd507c059bacfd7c27b748ee50bcee39e049924a, 220 committed tasks had no exit-code changes; one archived task prints the intended new question/template. Repository lint-skills, ADR lint, number guards, design-surfaces and comment ratio pass. Comment ratio is 0.8%, maximum 5%.

The six saved behavioral answers still grade mechanism 3/3 versus current 2/3 generous or 1/3 strict on author re-read; independent validation must re-grade them. RoboRev and hosted CI: not run, delegated to FO. CI cost per PR: not measured; CI configuration is unchanged.

Prepared for one Draft PR from spacedock-ensign/role-call-asks-for-the-mechanism, base 82c9e67ae892b80647c3f6a8b6929f993e42dbc2, candidate ebbac3de0dbf3b9bf9bf4c59611ff06bb5eb4fe9. Product branch not pushed; FO owns publication and local review.
