# Pre-registered grader (written 2026-11-09T14:44:25Z, before any replay run)

Pass ("names the missing attempt identity"): the answer states ONE cause behind the validation findings
(validation-1 F1/F2, validation-2 F5/F6) located in the booking attempt/draft/submission having no identity
of its own that async results (send response, profile save, sign-in return) are checked against.
Accepted wording: attempt id/identity, submission/request identity, draft generation/version/token/epoch,
per-attempt key that late writers compare, "a single owner/state machine for the booking attempt" whose
identity late results check. The cited line must tie it to more than one finding.
Fail: fixing findings one at a time; naming only the screen/symptom (summary.tsx, sign-in detour); naming
only the idempotency key reuse (F6) without generalizing to late writers; "outcome unchanged" answers.
Ruling rule: mechanism arm must pass strictly more runs than current arm. Tie (incl. 3/3 vs 3/3) = does not beat.
Grading: one grader (the ideation worker), quoting the line from each run that passes or fails the rule.
Inputs: /tmp/rcm/inputs (qnow state 27f04824 task+dispatch+validation-1/2 evidence, no png; product 35fd5f65 apps/qnow-app + diff from 232344ce). Leak scan: no 'attempt identity|attemptId|attempt_id|attempt-identity' in inputs.
