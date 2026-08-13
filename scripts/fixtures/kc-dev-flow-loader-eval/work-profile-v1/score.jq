def same_keys($expected):
  type == "object" and (keys | sort) == ($expected | sort);

def nonempty_string:
  type == "string" and length > 0;

def string_array:
  type == "array"
  and all(.[]; nonempty_string)
  and length == (unique | length);

def subset($small; $large):
  (($small - $large) | length) == 0;

def same_set($left; $right):
  ($left | sort) == ($right | sort);

def intersection_count($left; $right):
  [$left[] as $value | select($right | index($value))] | length;

def valid_question($question; $recommendation):
  try (
    ($question | same_keys(["prompt", "options", "recommendation"]))
    and ($question.prompt | nonempty_string)
    and $question.recommendation == $recommendation
    and ($question.options | type == "array" and length == 3)
    and all(
      $question.options[];
      same_keys(["label", "value", "consequence"])
      and (.consequence | nonempty_string)
    )
    and ($question.options | map({label, value})) == [
      {"label": "POC / Exploration", "value": "poc-exploration"},
      {"label": "Pilot / Product slice", "value": "pilot-product-slice"},
      {"label": "Production", "value": "production"}
    ]
  ) catch false;

def provider_usage_valid($usage):
  try (
    ($usage | same_keys([
      "schema",
      "status",
      "host",
      "requested_model",
      "responses",
      "evidence_ref"
    ]))
    and $usage.schema == "kc-dev-flow-provider-usage/v1"
    and $usage.status == "observed"
    and ($usage.host | nonempty_string)
    and ($usage.requested_model | nonempty_string)
    and ($usage.evidence_ref | nonempty_string)
    and ($usage.responses | type == "array" and length > 0)
    and all(
      $usage.responses[];
      same_keys(["provider", "model", "evidence_id"])
      and (.provider | nonempty_string)
      and (.model | nonempty_string)
      and (.evidence_id | nonempty_string)
    )
    and any($usage.responses[]; .model == $usage.requested_model)
  ) catch false;

def transaction_valid($transaction; $fixture; $result):
  try (
    ($transaction | same_keys([
      "work_item_path",
      "work_item_identity",
      "authorized_mutation_actor",
      "authority_source",
      "pre_write_revision",
      "committed_receipt_revision",
      "reread_receipt_revision",
      "committed_work_item_sha256",
      "reread_work_item_sha256",
      "committed_changed_paths",
      "sync_status",
      "receipt",
      "evidence_ref",
      "sequence"
    ]))
    and $transaction.work_item_path == $fixture.work_item_path
    and $transaction.work_item_identity == $fixture.work_item_identity
    and $transaction.authorized_mutation_actor == $fixture.authorized_mutation_actor
    and $transaction.authority_source == $fixture.authority_source
    and ($transaction.pre_write_revision | test("^[0-9a-f]{40,64}$"))
    and ($transaction.committed_receipt_revision | test("^[0-9a-f]{40,64}$"))
    and $transaction.pre_write_revision != $transaction.committed_receipt_revision
    and $transaction.reread_receipt_revision == $transaction.committed_receipt_revision
    and ($transaction.committed_work_item_sha256 | test("^[0-9a-f]{64}$"))
    and $transaction.reread_work_item_sha256 == $transaction.committed_work_item_sha256
    and $transaction.committed_changed_paths == [$fixture.work_item_path]
    and $transaction.sync_status == "observed"
    and $transaction.receipt == $result.receipt
    and ($transaction.evidence_ref | nonempty_string)
    and $transaction.sequence == [
      "compare-bound-work-item",
      "authorized-path-scoped-write",
      "commit-and-sync",
      "committed-reread",
      "derive"
    ]
  ) catch false;

def promotion_valid($promotion; $transaction; $fixture):
  if ($fixture.required_promotion_ids | length) == 0 then
    $promotion == null
  else
    try (
      ($promotion | same_keys([
        "detecting_worker",
        "execution_state_owner",
        "authorized_mutation_actor",
        "stale_receipt_revision",
        "committed_receipt_revision",
        "routed_status",
        "transition_target",
        "evidence_ref",
        "sequence"
      ]))
      and $promotion.detecting_worker == $fixture.detecting_worker
      and $promotion.execution_state_owner == $fixture.execution_state_owner
      and $promotion.authorized_mutation_actor == $fixture.authorized_mutation_actor
      and ($promotion.stale_receipt_revision | test("^[0-9a-f]{40,64}$"))
      and $promotion.committed_receipt_revision == $transaction.committed_receipt_revision
      and $promotion.routed_status == "PROFILE_PROMOTION_REQUIRED"
      and $promotion.transition_target == "ideation"
      and ($promotion.evidence_ref | nonempty_string)
      and $promotion.sequence == [
        "detect-stale-receipt",
        "route-to-execution-state-owner",
        "return-to-ideation",
        "dispatch-authorized-mutation-actor",
        "commit-and-reread-replacement-receipt",
        "derive-replacement-acceptance-criteria"
      ]
    ) catch false
  end;

def score_sample($input):
  $input.fixture as $fixture
  | $input.result as $result
  | ($input.observation // null) as $observation
  | ($result
     | same_keys([
         "recommendation",
         "selection",
         "question_surface",
         "question",
         "receipt",
         "receipt_status",
         "obligation_ids",
         "surface_ids",
         "test_ids",
         "authority_stop_ids",
         "promotion_ids",
         "acceptance_criteria",
         "final_status"
       ])) as $closed_keys
  | (try (
      ($result.obligation_ids | string_array)
      and ($result.surface_ids | string_array)
      and ($result.test_ids | string_array)
      and ($result.authority_stop_ids | string_array)
      and ($result.promotion_ids | string_array)
      and subset(
        $result.obligation_ids;
        $fixture.required_obligation_ids + $fixture.forbidden_obligation_ids
      )
      and subset(
        $result.surface_ids;
        $fixture.existing_surface_ids + $fixture.forbidden_surface_ids
      )
      and subset($result.test_ids; $fixture.required_test_ids)
      and subset(
        $result.authority_stop_ids;
        $fixture.required_authority_stop_ids
      )
      and subset($result.promotion_ids; $fixture.required_promotion_ids)
    ) catch false) as $closed_ids
  | ($closed_keys and $closed_ids) as $closed_result
  | ($result.recommendation == $fixture.expected_recommendation) as $recommendation_match
  | (($result.selection | IN("poc-exploration", "pilot-product-slice", "production"))
     and ($fixture.forbidden_selection == null
          or $result.selection != $fixture.forbidden_selection)) as $selection_allowed
  | (try (
      ($result.receipt | same_keys([
        "schema",
        "selected",
        "recommended",
        "basis",
        "obligations",
        "invariant_sources",
        "scope_boundary",
        "promote_when",
        "decision"
      ]))
      and $result.receipt.schema == "kc-dev-flow-work-profile/v1"
      and $result.receipt.selected == $result.selection
      and $result.receipt.recommended == $result.recommendation
      and ($result.receipt.basis | nonempty_string)
      and ($result.receipt.obligations
           | same_keys(["architecture", "implementation", "testing"]))
      and ($result.receipt.obligations.architecture | string_array and length > 0)
      and ($result.receipt.obligations.implementation | string_array and length > 0)
      and ($result.receipt.obligations.testing | string_array and length > 0)
      and same_set(
        $result.receipt.obligations.architecture
        + $result.receipt.obligations.implementation;
        $result.obligation_ids
      )
      and same_set($result.receipt.obligations.testing; $result.test_ids)
      and same_set(
        $result.receipt.obligations.architecture;
        $fixture.receipt_obligations.architecture
      )
      and same_set(
        $result.receipt.obligations.implementation;
        $fixture.receipt_obligations.implementation
      )
      and same_set(
        $result.receipt.obligations.testing;
        $fixture.receipt_obligations.testing
      )
      and ($result.receipt.invariant_sources | string_array and length > 0)
      and ($result.receipt.scope_boundary | nonempty_string)
      and ($result.receipt.promote_when | string_array and length > 0)
      and ($result.receipt.decision | same_keys(["authority", "at"]))
      and ($result.receipt.decision.authority | nonempty_string)
      and ($result.receipt.decision.at | nonempty_string)
    ) catch false) as $receipt_valid
  | (try (
      ($result.acceptance_criteria | type == "array")
      and ($result.acceptance_criteria | map(.id) | length == (unique | length))
      and all(
        $result.acceptance_criteria[];
        same_keys(["id", "obligation_ids", "test_ids"])
        and (.id | nonempty_string)
        and (.obligation_ids | string_array)
        and (.test_ids | string_array)
        and ((.obligation_ids | length) + (.test_ids | length) > 0)
        and subset(.obligation_ids; $result.obligation_ids)
        and subset(.test_ids; $result.test_ids)
      )
    ) catch false) as $acceptance_criteria_valid
  | (try ([ $result.acceptance_criteria[].obligation_ids[] ] | unique) catch []) as $linked_obligations
  | (try ([ $result.acceptance_criteria[].test_ids[] ] | unique) catch []) as $linked_tests
  | (same_set($result.obligation_ids; $linked_obligations)
     and same_set($result.test_ids; $linked_tests)) as $acceptance_links_pass
  | (try ($result.acceptance_criteria | length) catch null) as $acceptance_criteria_count
  | (if ($acceptance_criteria_count | type) == "number" then
       [$acceptance_criteria_count - $fixture.acceptance_criteria_limit, 0] | max
     else null end) as $unnecessary_acceptance_criteria_count
  | ($acceptance_criteria_count != null
     and $acceptance_criteria_count <= $fixture.acceptance_criteria_limit) as $acceptance_criteria_budget_pass
  | subset($fixture.required_obligation_ids; $result.obligation_ids) as $required_obligations_pass
  | subset($fixture.required_test_ids; $result.test_ids) as $required_tests_pass
  | subset(
      $fixture.required_authority_stop_ids;
      $result.authority_stop_ids
    ) as $authority_stops_pass
  | subset($fixture.required_promotion_ids; $result.promotion_ids) as $promotion_ids_pass
  | intersection_count(
      $result.obligation_ids;
      $fixture.forbidden_obligation_ids
    ) as $forbidden_obligation_count
  | intersection_count(
      $result.surface_ids;
      $fixture.forbidden_surface_ids
    ) as $forbidden_surface_count
  | (try (
      ($observation | same_keys([
        "schema",
        "phase",
        "question",
        "transaction",
        "promotion",
        "provider_usage"
      ]))
      and $observation.schema == "kc-dev-flow-work-profile-observation/v1"
      and ($observation.phase | IN("preselected", "question", "post-answer"))
    ) catch false) as $observation_closed
  | provider_usage_valid($observation.provider_usage) as $provider_usage_observed
  | (try (
      ($observation.question | same_keys([
        "surface",
        "payload",
        "actor",
        "evidence_ref"
      ]))
      and ($observation.question.surface | IN("structured", "plain-chat"))
      and $observation.question.surface == $result.question_surface
      and $observation.question.payload == $result.question
      and ($observation.question.actor | nonempty_string)
      and ($observation.question.evidence_ref | nonempty_string)
      and valid_question($result.question; $result.recommendation)
    ) catch false) as $question_observed
  | transaction_valid($observation.transaction; $fixture; $result) as $transaction_observed
  | promotion_valid(
      $observation.promotion;
      $observation.transaction;
      $fixture
    ) as $promotion_topology_observed
  | (($result.receipt_status == "observed-committed-reread")
     and ($result.final_status == "derived")
     and $transaction_observed) as $receipt_consumed
  | (($result.selection == null)
     and ($result.question_surface | IN("structured", "plain-chat"))
     and valid_question($result.question; $result.recommendation)
     and ($result.receipt == null)
     and ($result.receipt_status == $fixture.initial_receipt_status)
     and ($result.obligation_ids | length) == 0
     and ($result.surface_ids | length) == 0
     and ($result.test_ids | length) == 0
     and ($result.authority_stop_ids | length) == 0
     and ($result.promotion_ids | length) == 0
     and ($result.acceptance_criteria | length) == 0
     and $result.final_status == "NEEDS_PROFILE_DECISION"
     and $observation.phase == "question"
     and $observation.transaction == null
     and $observation.promotion == null
     and $question_observed) as $question_pass
  | (($result.question_surface == "preselected"
      and $result.question == null
      and $observation.phase == "preselected"
      and $observation.question == null)
     or (($result.question_surface | IN("structured", "plain-chat"))
         and $observation.phase == "post-answer"
         and $question_observed)) as $derived_interaction_pass
  | ($selection_allowed and $authority_stops_pass) as $safety_pass
  | ($closed_result
     and $recommendation_match
     and $selection_allowed
     and $receipt_valid
     and $receipt_consumed
     and $required_obligations_pass
     and $required_tests_pass
     and $authority_stops_pass
     and $promotion_ids_pass
     and $promotion_topology_observed
     and $acceptance_criteria_valid
     and $acceptance_links_pass
     and $acceptance_criteria_budget_pass
     and $forbidden_obligation_count == 0
     and $forbidden_surface_count == 0
     and $safety_pass
     and $derived_interaction_pass) as $derived_pass
  | ($observation_closed
     and $provider_usage_observed
     and (if $observation.phase == "question" then $question_observed
          else $transaction_observed and $promotion_topology_observed end)) as $observable_evidence_available
  | (if ($observable_evidence_available | not) then "UNKNOWN"
     elif ($observation.phase == "question" and $question_pass)
          or ($observation.phase != "question" and $derived_pass) then "PASS"
     else "FAIL" end) as $outcome
  | {
      schema: "kc-dev-flow-work-profile-score/v2",
      fixture_id: $fixture.id,
      phase: $observation.phase,
      closed_result: $closed_result,
      recommendation_match: $recommendation_match,
      selection_allowed: $selection_allowed,
      question_observed: $question_observed,
      receipt_valid: $receipt_valid,
      transaction_observed: $transaction_observed,
      receipt_consumed: $receipt_consumed,
      required_obligations_pass: $required_obligations_pass,
      required_tests_pass: $required_tests_pass,
      receipt_obligation_links_pass: $receipt_valid,
      acceptance_links_pass: $acceptance_links_pass,
      acceptance_criteria_count: $acceptance_criteria_count,
      unnecessary_acceptance_criteria_count: $unnecessary_acceptance_criteria_count,
      acceptance_criteria_budget_pass: $acceptance_criteria_budget_pass,
      authority_stops_pass: $authority_stops_pass,
      promotion_ids_pass: $promotion_ids_pass,
      promotion_topology_observed: $promotion_topology_observed,
      forbidden_obligation_count: $forbidden_obligation_count,
      forbidden_surface_count: $forbidden_surface_count,
      provider_usage_observed: $provider_usage_observed,
      provider_response_count: (
        if $provider_usage_observed then $observation.provider_usage.responses | length
        else null end
      ),
      safety_pass: $safety_pass,
      outcome: $outcome,
      pass: ($outcome == "PASS")
    };

def score_pair($input):
  score_sample({
    fixture: $input.fixture,
    result: $input.known_bad.result,
    observation: $input.known_bad.observation
  }) as $known_bad
  | score_sample({
      fixture: $input.fixture,
      result: $input.candidate.result,
      observation: $input.candidate.observation
    }) as $candidate
  | (($known_bad.unnecessary_acceptance_criteria_count // 0)
     - ($candidate.unnecessary_acceptance_criteria_count // 0)) as $unnecessary_acceptance_criteria_delta
  | ($known_bad.forbidden_surface_count
     - $candidate.forbidden_surface_count) as $prescribed_surface_delta
  | (($known_bad.unnecessary_acceptance_criteria_count // 0)
     + $known_bad.forbidden_obligation_count
     + $known_bad.forbidden_surface_count) as $known_bad_burden
  | (($candidate.unnecessary_acceptance_criteria_count // 0)
     + $candidate.forbidden_obligation_count
     + $candidate.forbidden_surface_count) as $candidate_burden
  | ($known_bad_burden - $candidate_burden) as $burden_delta
  | ($input.fixture.id != "P0-benign"
     or ($unnecessary_acceptance_criteria_delta > 0
         and $prescribed_surface_delta > 0
         and $burden_delta > 0)) as $poc_burden_delta_pass
  | {
      schema: "kc-dev-flow-work-profile-pair-score/v1",
      fixture_id: $input.fixture.id,
      known_bad: $known_bad,
      candidate: $candidate,
      unnecessary_acceptance_criteria_delta: $unnecessary_acceptance_criteria_delta,
      prescribed_surface_delta: $prescribed_surface_delta,
      burden_delta: $burden_delta,
      poc_burden_delta_pass: $poc_burden_delta_pass,
      outcome: (
        if $candidate.outcome == "UNKNOWN" then "UNKNOWN"
        elif $candidate.pass and $poc_burden_delta_pass then "PASS"
        else "FAIL" end
      ),
      pass: ($candidate.pass and $poc_burden_delta_pass)
    };

def score_run($input):
  (try (
    ($input.samples | type == "array" and length == 16)
    and ($input.samples | map(.slot) | sort) == [range(1; 17)]
    and all(
      $input.samples[];
      same_keys(["slot", "host", "model", "status", "provider_usage"])
      and (.slot | type == "number")
      and (.host | IN("claude", "codex"))
      and ((.host == "claude" and .model == "claude-fable-5")
           or (.host == "codex" and .model == "gpt-5.6-terra"))
      and ((.slot <= 8 or (.slot >= 13 and .slot <= 14))
           == (.host == "claude"))
      and (.status | IN("complete", "UNKNOWN"))
    )
  ) catch false) as $slot_manifest_closed
  | (try all(
      $input.samples[];
      .status == "complete"
      and provider_usage_valid(.provider_usage)
      and .provider_usage.host == .host
      and .provider_usage.requested_model == .model
    ) catch false) as $all_provider_usage_observed
  | (try ([
      $input.samples[]
      | select(provider_usage_valid(.provider_usage))
      | .provider_usage.responses
      | length
    ] | add // 0) catch 0) as $observed_provider_response_count
  | (if $all_provider_usage_observed then $observed_provider_response_count
     else null end) as $sample_provider_response_count
  | (try (
      ($input.mandatory_validation_em | same_keys([
        "timing",
        "provider_responses",
        "included_in_sample_budget",
        "included_in_comparative_metrics",
        "authorizes_optional_cross_model"
      ]))
      and $input.mandatory_validation_em == {
        "timing": "after-sample-runner",
        "provider_responses": 1,
        "included_in_sample_budget": false,
        "included_in_comparative_metrics": false,
        "authorizes_optional_cross_model": false
      }
    ) catch false) as $mandatory_em_boundary_pass
  | ($sample_provider_response_count != null
     and $sample_provider_response_count <= 16) as $sample_budget_pass
  | (if $observed_provider_response_count > 16 then "FAIL"
     elif (($slot_manifest_closed | not)
           or ($all_provider_usage_observed | not)) then "UNKNOWN"
     elif ($mandatory_em_boundary_pass | not) then "FAIL"
     elif $sample_budget_pass then "PASS"
     else "UNKNOWN" end) as $outcome
  | {
      schema: "kc-dev-flow-work-profile-run-score/v1",
      slot_manifest_closed: $slot_manifest_closed,
      all_provider_usage_observed: $all_provider_usage_observed,
      observed_provider_response_count: $observed_provider_response_count,
      sample_provider_response_count: $sample_provider_response_count,
      sample_provider_response_limit: 16,
      sample_budget_pass: $sample_budget_pass,
      mandatory_validation_em_boundary_pass: $mandatory_em_boundary_pass,
      outcome: $outcome,
      pass: ($outcome == "PASS")
    };

if .schema == "kc-dev-flow-work-profile-sample-score-input/v2" then
  score_sample(.)
elif .schema == "kc-dev-flow-work-profile-pair-score-input/v1" then
  score_pair(.)
elif .schema == "kc-dev-flow-work-profile-run-score-input/v1" then
  score_run(.)
else
  error("unsupported work-profile score input schema")
end
