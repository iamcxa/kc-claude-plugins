# Sibling-site inventory before code edits

Source: 5bf7cf78866a2f0f6376c15b59fc400519c5ffeb. Numbered lines refer to that source.

- FM_STATUS / scope_hold (49, 958–960): F1: commented status becomes unknown and scope check is not run; reproduced. report; do not change.
- check_task prod ideation security (1097, 1107): F1: missing Security review passes with commented ideation; reproduced. report; leave legacy status variable.
- check_task UI ideation design review (1097, 1111): F1: missing Design review passes with commented ideation; reproduced. report; leave legacy status variable.
- check_task UI validation built-screen review (1097, 1116): F1: missing Built screen review passes with commented validation; reproduced. report; leave legacy status variable.
- main gate question reminder (1147–1149): F1: same exact-match stage read omits reminder for commented backlog/ideation; source confirmed. report; do not change.
- check_task Worth stage predicate (1104): F1: shares raw stage read; owned new check. repair using native parsed single-file read, not another YAML regex.
- check_task Worth Design/section presence (1102–1105): F2: comments can supply required Worth heading and Design boundary; owned new check. repair local visible-line scan; do not alter global readers.
- FO alignment section and split_fo (87–95, 1054–1058): F2: complete commented FO block accepted; reproduced. report; do not change.
- check_criteria required Acceptance criteria (181–190, 1089): F2: complete commented AC section accepted; reproduced. report; do not change.
- section generic selector and AC consumers (134–139, 336, 382, 429): F2: caller-provided comment lines can supply/end a section; downstream amendment/criterion comparisons share it. report; new Worth passes its own filtered lines only.
- parse_amendments owner/required amendment region (229–275): F2: HTML-commented Captain amendments region yields an amendment record; reproduced. report; do not change.
- scope_lines required Scope contents (901–912): F2: fence-aware but HTML-comment-blind first Scope selector; source confirmed. report; do not change.
- validation_report latest Stage Report: validation (821–825): F2: HTML-comment-blind report boundary can select hidden validation report; source confirmed. report; do not change.
- check_seed_fields required bounds sections (1006–1040): Closed HTML comments excluded already; unclosed HTML comment can supply all bounds; both reproduced. report unterminated-comment hole; do not change seed reader.
- alignment_owes_result FO region (152–154): Shares split_fo/unfenced HTML-comment-blind selection; not the Worth consumer. report; do not change.
- check_ui/check_db required body records (111–131): Required labels/artifact checks are HTML-comment-blind body reads, not a stage read; source confirmed. report as related field-read risk, not repaired.
- check_security/check_design_review/check_built_screen required report labels (530, 755, 832): HTML-comment-blind body line reads; status bypasses reproduced separately; label-only hidden input risk source confirmed. report; do not change.
- report_shape/design_report/decline_report required YAML root mappings (509, 594, 740): External YAML report schema checks, not Markdown sections or task stage reads; HTML rendering is not their input contract. not the same Markdown comment hole; out of this repair.

Only the two Worth-check consumers are repaired. sibling-probes.json distinguishes exercised failures from source observations. Native --read works on an absolute standalone file without a workflow README; native-path-probe.json preserves that observation.
