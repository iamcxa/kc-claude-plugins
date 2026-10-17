### `validation`

A fresh ensign invokes `kc-dev-flow-2:validation` before useful work and checks
the exact artifact against the accepted profile outcome. It assesses the work;
it does not silently take over implementation. Rejection uses the supported
feedback path after the distinct FO disposition described below. Its recheck of a
repair is dispatched under the lane in Stages.

- **Outputs:** Independent verdict, primary evidence, a minimal acceptance script, the
  `python3 <package>/scripts/adr_lint.py docs/adr --since <base>` command run with its exit
  code, and unverified obligations recorded in the existing SD Stage Report.
- **Gate content:** Show actual checks and acceptance evidence, material findings
  and limits, and the user's pending delivery decision. Before the gate, FO runs the
  stage's minimal acceptance script exactly as written in a fresh shell, then presents
  every step in full beside its observed output, never a pointer or a shortened step.
  A step FO cannot run (a secret, a sign-in, the Captain's own device) is marked not
  run with the reason; an output that differs from the script returns through feedback.
  Before recommending delivery, FO confirms both goal sufficiency and minimal
  necessity from the same candidate's existing route evidence. Passing checks or
  approval replace neither condition; approval is not merge. When a POC report
  records `boundary-crossed:`, FO shows the marker and its evidence with the
  user's choice between profile selection and removing the crossing work with
  recorded cleanup through the feedback route, and does not recommend
  delivering that work as POC.

