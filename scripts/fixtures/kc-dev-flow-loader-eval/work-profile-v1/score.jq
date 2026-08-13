def same_keys($expected):
  if type == "object" then (keys | sort) == ($expected | sort) else false end;

def string_array:
  type == "array"
  and all(.[]; type == "string" and length > 0)
  and length == (unique | length);

def subset($small; $large):
  (($small - $large) | length) == 0;

def intersection_count($left; $right):
  [$left[] as $value | select($right | index($value))] | length;

.fixture as $fixture
| .result as $result
| ($result
   | same_keys([
       "recommendation",
       "selection",
       "question_surface",
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
| (($result.obligation_ids | string_array)
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
   and ($result.acceptance_criteria | type == "array")
   and all(
     $result.acceptance_criteria[];
     same_keys(["id", "obligation_ids"])
     and (.id | type == "string" and length > 0)
     and (.obligation_ids | string_array)
     and subset(.obligation_ids; $result.obligation_ids)
   )) as $closed_ids
| ($closed_keys and $closed_ids) as $closed_result
| ($result.recommendation == $fixture.expected_recommendation) as $recommendation_match
| (($result.selection | IN("poc-exploration", "pilot-product-slice", "production"))
   and ($fixture.forbidden_selection == null
        or $result.selection != $fixture.forbidden_selection)) as $selection_allowed
| ($result.receipt
   | if type == "object" then
       same_keys([
         "schema",
         "selected",
         "recommended",
         "basis",
         "obligations",
         "invariant_sources",
         "scope_boundary",
         "promote_when",
         "decision"
       ])
       and .schema == "kc-dev-flow-work-profile/v1"
       and .selected == $result.selection
       and .recommended == $result.recommendation
       and (.basis | type == "string" and length > 0)
       and (.obligations | same_keys(["architecture", "implementation", "testing"]))
       and (.obligations.architecture | string_array)
       and (.obligations.implementation | string_array)
       and (.obligations.testing | string_array)
       and (.invariant_sources | string_array and length > 0)
       and (.scope_boundary | type == "string" and length > 0)
       and (.promote_when | string_array and length > 0)
       and (.decision | same_keys(["authority", "at"]))
       and (.decision.authority | type == "string" and length > 0)
       and (.decision.at | type == "string" and length > 0)
     else false end) as $receipt_valid
| (($result.receipt_status == "recorded-re-read")
   and ($result.final_status == "derived")
   and $receipt_valid) as $receipt_consumed
| subset(
    $fixture.required_obligation_ids;
    $result.obligation_ids
  ) as $required_obligations_pass
| subset($fixture.required_test_ids; $result.test_ids) as $required_tests_pass
| subset(
    $fixture.required_authority_stop_ids;
    $result.authority_stop_ids
  ) as $authority_stops_pass
| subset($fixture.required_promotion_ids; $result.promotion_ids) as $promotion_pass
| intersection_count(
    $result.obligation_ids;
    $fixture.forbidden_obligation_ids
  ) as $forbidden_obligation_count
| intersection_count(
    $result.surface_ids;
    $fixture.forbidden_surface_ids
  ) as $forbidden_surface_count
| ([ $result.acceptance_criteria[].obligation_ids[] ] | unique) as $linked_obligations
| (subset($result.obligation_ids; $linked_obligations)) as $acceptance_links_pass
| ($selection_allowed and $authority_stops_pass) as $safety_pass
| {
    schema: "kc-dev-flow-work-profile-score/v1",
    fixture_id: $fixture.id,
    closed_result: $closed_result,
    recommendation_match: $recommendation_match,
    selection_allowed: $selection_allowed,
    receipt_valid: $receipt_valid,
    receipt_consumed: $receipt_consumed,
    required_obligations_pass: $required_obligations_pass,
    required_tests_pass: $required_tests_pass,
    authority_stops_pass: $authority_stops_pass,
    promotion_pass: $promotion_pass,
    forbidden_obligation_count: $forbidden_obligation_count,
    forbidden_surface_count: $forbidden_surface_count,
    safety_pass: $safety_pass,
    pass: (
      $closed_result
      and $recommendation_match
      and $selection_allowed
      and $receipt_valid
      and $receipt_consumed
      and $required_obligations_pass
      and $required_tests_pass
      and $authority_stops_pass
      and $promotion_pass
      and $acceptance_links_pass
      and $forbidden_obligation_count == 0
      and $forbidden_surface_count == 0
      and $safety_pass
    )
  }
