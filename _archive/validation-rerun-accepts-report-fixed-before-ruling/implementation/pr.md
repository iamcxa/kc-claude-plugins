fix(kc-dev-flow-2): accept validation corrections before rulings

Validation dispatch previously rejected every in-place report correction, including corrections committed before the Captain ruled. Accept those corrections when every version keeps the same ordered, non-empty list of whole-word PASSED/REJECTED tokens, then require the clearing ruling to follow the final text's first commit.

Corrections after a new Captain record or gate entry, including a correction committed beside the ruling, still hold dispatch. Give the three rewrite holds specific recovery wording and amend ADR 0045 in place with both approved questions and replies.

Validation:
- Full dispatch-record suite: 125 tests, one native-builder test skipped without its environment parameters; that test then passed separately with the declared Spacedock binary and plugin root.
- Dispatch entry suite: 40 tests passed. Historical-law suite: 84 tests, one optional external-source test skipped.
- Recorded qnow history: tag exit 2, candidate exit 0. Post-ruling rewrite and verdict flip: both remain exit 2 with their intended reason tokens.
- Four state branches: 26 open-decision tasks, only the 10 previously refused for rewritten-report change outcome (8 clear, 1 needs a later ruling, 1 remains refused for an unreadable verdict).
- Eight unit mutations fail their assertions; the restored blanket refusal reproduces the qnow failure, and a separate corpus mutation exposes unintended changes to previously cleared tasks.
- Repository skill lint, ADR lint requiring 0045, number guards, design-surface check and comment-ratio check passed. Added comment ratio: 0.0%, maximum 5%.

RoboRev and hosted CI have not run. CI configuration is unchanged; cost per PR was not measured. No version bump.
