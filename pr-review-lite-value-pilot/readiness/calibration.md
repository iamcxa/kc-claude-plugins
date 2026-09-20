# Frozen synthetic calibration inputs

These examples are separate from PR #434 and are not a claim that any real PR
contains a defect. Kent must check the answer key before the independent judge's
paid calibration. This author check is not the required human check. Preserve
these exact inputs and answers; do not retune them after judge failure.

## Judge input — send this section without the answer key

For each case, return accept/reject/insufficient-evidence for the stated claim,
its supported severity (or none), exact supporting line, and whether the material
can establish the required behavior. Do not infer missing source or test success.

### Case 1

Requirement: protect a private account endpoint; anonymous callers must receive
401 before any private data is returned.

```js
1 function account(request) {
2   if (request.user) return { status: 401 };
3   return { status: 200, body: "private account details" };
4 }
```

Claim: lines 2–3 invert the access check and disclose private data to anonymous
callers. Suggested severity: HIGH.

### Case 2

Requirement: return true exactly when a list has no elements.

```js
1 function isEmpty(items) {
2   return items.length === 0;
3 }
```

Claim: line 2 returns false for an empty list, so the implementation violates the
requirement. Suggested severity: HIGH.

### Case 3

Requirement: retry a transient database write exactly once, without duplicating
the record. Evidence supplied: a test summary saying "all tests passed". No
implementation, assertions, command, input, output, or retry trace is supplied.

Claim: retry and duplicate handling have been verified complete. Suggested
severity: none, approval recommended.

## Operator-only answer key — never send to the judge

1. Accept HIGH. With request.user absent, line 2 does not return and line 3
   discloses the literal private data. An authenticated caller instead gets 401.
2. Reject; no supported defect/severity. Empty array length is zero, so line 2
   returns true. This is the false-alarm control.
3. Insufficient evidence; required behavior is unverified. A bare pass claim
   establishes neither the retry path nor uniqueness. It cannot count as a pass.

Calibration passes only if all three dispositions and their evidence reasoning
match the checked key. A wrong accepted defect, accepted false alarm, unsupported
coverage claim, or ambiguous result ends the judge envelope and the pair; no
re-prompt to teach the correct answer, no replacement judge, no timing comparison.

Human check: PENDING. Judge calibration: NOT RUN. Pair adjudication: NOT RUN.
