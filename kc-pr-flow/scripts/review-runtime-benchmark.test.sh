#!/usr/bin/env bash
# Tests for the deterministic, receipt-only review runtime benchmark.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BENCHMARK="$HERE/review-runtime-benchmark.sh"
FIXTURE="$HERE/../test/fixtures/review-runtime/paired-runs.jsonl"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT

PASS=0
FAIL=0
CASE='all'

if [ "${1:-}" = '--case' ] && [ "$#" -eq 2 ]; then
  CASE="$2"
elif [ "$#" -ne 0 ]; then
  printf 'usage: review-runtime-benchmark.test.sh [--case authority-binding|path-replacement]\n' >&2
  exit 2
fi

case "$CASE" in
  all|authority-binding|path-replacement) ;;
  *)
    printf 'review-runtime-benchmark.test.sh: unknown case: %s\n' "$CASE" >&2
    exit 2
    ;;
esac

pass() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL: %s\n' "$1"; }

assert_eq() { # $1=description $2=expected $3=actual
  if [ "$2" = "$3" ]; then
    pass
  else
    fail "$1 (expected [$2], got [$3])"
  fi
}

assert_ne() { # $1=description $2=unexpected $3=actual
  if [ "$2" != "$3" ]; then
    pass
  else
    fail "$1 (unexpected [$2])"
  fi
}

sha256_text() {
  if command -v shasum >/dev/null 2>&1; then
    printf '%s' "$1" | shasum -a 256 | awk '{print $1}'
  else
    printf '%s' "$1" | sha256sum | awk '{print $1}'
  fi
}

assert_rejected() { # $1=description $2=corpus
  local description="$1" corpus="$2" output rc
  output="$("$BENCHMARK" score --corpus "$corpus" 2>&1)"
  rc=$?
  assert_eq "$description" "2" "$rc"
  if [[ "$output" == *"invalid sanitized corpus"* || "$output" == *"invalid canonical identity"* || "$output" == *"malformed corpus"* || "$output" == *"safe regular file"* ]]; then
    pass
  else
    fail "$description emits a typed validation error"
  fi
}

arm_content_sha256() { # $1=arm JSON
  local canonical
  canonical="$(printf '%s' "$1" | jq -S -c '{
    behavior,
    lanes:(.lanes | sort_by(.capability,.lane_id)),
    candidates:(.observed_candidates | sort_by(.candidate_id)),
    findings:((.observed_findings // []) | sort_by(.finding_id,.candidate_id)),
    uncertain_candidate_refs:(.uncertain_candidate_ids | sort),
    usage
  }')" || return
  sha256_text "$canonical"
}

rehash_arm_receipt() { # $1=input corpus $2=arm name $3=output corpus
  local input="$1" arm_name="$2" output="$3" line arm_json content_sha256 run_id review_key receipt_id
  line="$(<"$input")" || return
  arm_json="$(printf '%s' "$line" | jq -c --arg arm "$arm_name" '.[$arm]')" || return
  content_sha256="$(arm_content_sha256 "$arm_json")" || return
  run_id="$(printf '%s' "$arm_json" | jq -r '.receipt.run_id')" || return
  review_key="$(printf '%s' "$arm_json" | jq -r '.receipt.review_key')" || return
  receipt_id="$(sha256_text "$run_id|$review_key|$content_sha256")" || return
  printf '%s' "$line" | jq -c --arg arm "$arm_name" --arg content_sha256 "$content_sha256" --arg receipt_id "$receipt_id" '
    .[$arm].receipt.content_sha256=$content_sha256 |
    .[$arm].receipt.receipt_id=$receipt_id
  ' >"$output"
}

if [ ! -x "$BENCHMARK" ]; then
  fail "review-runtime-benchmark.sh exists and is executable"
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  exit 1
fi

run_path_replacement_case() {
  local original_report replacement_report replacement_rc real_cat
  original_report="$("$BENCHMARK" score --corpus "$FIXTURE")"
  cp "$FIXTURE" "$TEST_ROOT/path-replacement.jsonl"
  tail -n +2 "$FIXTURE" >"$TEST_ROOT/path-replacement.valid.jsonl"
  mkdir "$TEST_ROOT/path-replacement-bin"
  real_cat="$(command -v cat)"
  # The wrapper deterministically replaces the already-prechecked path at the
  # vulnerable reopen. A descriptor snapshot never invokes this path reader.
  # shellcheck disable=SC2016 # Wrapper variables expand only when the probe runs.
  printf '%s\n' \
    '#!/usr/bin/env bash' \
    'if [ "${1:-}" = "$REPLACEMENT_SOURCE" ] && [ ! -e "$REPLACEMENT_MARKER" ]; then' \
    '  : >"$REPLACEMENT_MARKER"' \
    '  mv "$REPLACEMENT_VALID" "$REPLACEMENT_SOURCE"' \
    'fi' \
    'exec "$REPLACEMENT_REAL_CAT" "$@"' >"$TEST_ROOT/path-replacement-bin/cat"
  chmod +x "$TEST_ROOT/path-replacement-bin/cat"
  replacement_report="$(PATH="$TEST_ROOT/path-replacement-bin:$PATH" \
    REPLACEMENT_SOURCE="$TEST_ROOT/path-replacement.jsonl" \
    REPLACEMENT_VALID="$TEST_ROOT/path-replacement.valid.jsonl" \
    REPLACEMENT_MARKER="$TEST_ROOT/path-replacement.marker" \
    REPLACEMENT_REAL_CAT="$real_cat" \
    "$BENCHMARK" score --corpus "$TEST_ROOT/path-replacement.jsonl" 2>"$TEST_ROOT/path-replacement.err")"
  replacement_rc=$?
  assert_eq "valid-corpus path replacement probe scores" "0" "$replacement_rc"
  assert_eq "one bounded descriptor snapshot preserves the originally selected corpus" "$original_report" "$replacement_report"
}

if [ "$CASE" = 'path-replacement' ]; then
  run_path_replacement_case
  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit
fi

if [ "$CASE" = 'authority-binding' ]; then
  head -n 1 "$FIXTURE" >"$TEST_ROOT/authority-source.jsonl"

  jq -c '
    .baseline.observed_candidates=[] |
    .baseline.uncertain_candidate_ids=[] |
    .shadow.observed_candidates=[] |
    .shadow.uncertain_candidate_ids=[] |
    .disagreement_candidate_fingerprint_ids=[]
  ' "$TEST_ROOT/authority-source.jsonl" >"$TEST_ROOT/candidates-removed.raw.jsonl"
  rehash_arm_receipt "$TEST_ROOT/candidates-removed.raw.jsonl" baseline "$TEST_ROOT/candidates-removed.baseline.jsonl"
  rehash_arm_receipt "$TEST_ROOT/candidates-removed.baseline.jsonl" shadow "$TEST_ROOT/candidates-removed.jsonl"
  assert_rejected "truth-labeled recall cannot survive removal of all canonical candidates and evidence" "$TEST_ROOT/candidates-removed.jsonl"

  changed_evidence='abababababababababababababababababababababababababababababababab'
  drifted="$(jq -c --arg evidence "$changed_evidence" '.baseline.observed_candidates[0].fingerprint.evidence_sha256=$evidence' "$TEST_ROOT/authority-source.jsonl")"
  drifted_fingerprint="$(printf '%s' "$drifted" | jq -c '.baseline.observed_candidates[0].fingerprint')"
  drifted_fingerprint_canonical="$(printf '%s' "$drifted_fingerprint" | jq -S -c 'del(.fingerprint_id)')"
  drifted_fingerprint_id="$(sha256_text "$drifted_fingerprint_canonical")"
  drifted_run_id="$(printf '%s' "$drifted" | jq -r '.baseline.receipt.run_id')"
  drifted_candidate_id="$(sha256_text "$drifted_run_id|$drifted_fingerprint_id")"
  printf '%s' "$drifted" | jq -c --arg fingerprint_id "$drifted_fingerprint_id" --arg candidate_id "$drifted_candidate_id" --arg evidence "$changed_evidence" '
    .baseline.observed_candidates[0].fingerprint.fingerprint_id=$fingerprint_id |
    .baseline.observed_candidates[0].candidate_id=$candidate_id |
    .baseline.observed_findings[0].candidate_id=$candidate_id |
    .baseline.observed_findings[0].evidence_sha256=$evidence
  ' >"$TEST_ROOT/evidence-drift.raw.jsonl"
  rehash_arm_receipt "$TEST_ROOT/evidence-drift.raw.jsonl" baseline "$TEST_ROOT/evidence-drift.jsonl"
  assert_rejected "truth-labeled observed finding must match the expected canonical candidate and evidence" "$TEST_ROOT/evidence-drift.jsonl"

  jq -c '.baseline.usage.input_tokens += 1 | .baseline.usage.total_tokens += 1' \
    "$TEST_ROOT/authority-source.jsonl" >"$TEST_ROOT/stale-content-hash.jsonl"
  assert_rejected "receipt content and identity hashes cannot remain stale after canonical arm content changes" "$TEST_ROOT/stale-content-hash.jsonl"

  printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
  [ "$FAIL" -eq 0 ]
  exit
fi

report="$("$BENCHMARK" score --corpus "$FIXTURE" 2>"$TEST_ROOT/score.err")"
score_rc=$?
assert_eq "valid paired corpus scores" "0" "$score_rc"
assert_eq "report uses the stable schema" "kc-pr-flow.review-benchmark-report/v1" "$(jq -r '.schema' <<<"$report")"
review_key_vector="$(bash -c '. "$1"; review_benchmark_review_key "$2" "$3" "$4" "$5" "$6"' _ "$BENCHMARK" \
  "acme/widgets" "42" "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" \
  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc" 2>/dev/null)"
assert_eq "review keys match the runtime canonical compatibility vector" \
  "f7da797d4da630b15f3780db37ebb6c8c95e5a6519bf0a0eaee9e445eba5cc61" "$review_key_vector"
fingerprint_vector_json="$(jq -c 'select(.pair_id=="pair-a") | .baseline.observed_candidates[0].fingerprint' "$FIXTURE")"
fingerprint_vector="$(bash -c '. "$1"; printf "%s" "$2" | review_benchmark_fingerprint_id' _ "$BENCHMARK" "$fingerprint_vector_json" 2>/dev/null)"
assert_eq "candidate fingerprints derive from canonical typed claim bytes" \
  "561e91fe4d10fa1dc93c3d3c236ca69aabbb1aca4a0c00e26b66be12e65635f7" "$fingerprint_vector"
candidate_id_vector="$(bash -c '. "$1"; review_benchmark_candidate_id "$2" "$3"' _ "$BENCHMARK" \
  "run-pair-a-baseline" "561e91fe4d10fa1dc93c3d3c236ca69aabbb1aca4a0c00e26b66be12e65635f7" 2>/dev/null)"
assert_eq "candidate IDs derive from run and canonical fingerprint identity" \
  "09616cd526af45d680a7008b6992669df1188001632fbbb01f300d361f1511ca" "$candidate_id_vector"
assert_eq "measure order starts with recall" "evidence_recall" "$(jq -r '.measure_order[0]' <<<"$report")"
assert_eq "baseline recall is computed against truth labels" "1/2" "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .evidence_recall.baseline | "\(.matched_count)/\(.expected_count)"' <<<"$report")"
second_report="$("$BENCHMARK" score --corpus "$FIXTURE")"
assert_eq "repeated scoring is byte-identical" "$report" "$second_report"
run_path_replacement_case

assert_eq "measure order follows product success-measure order" \
  "evidence_recall,lane_capability_coverage,external_behavior_parity,finding_candidate_stability,usage_comparability" \
  "$(jq -r '.measure_order | join(",")' <<<"$report")"
assert_eq "completed capabilities are reported deterministically" "code_correctness,security" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .lane_capability_coverage.baseline.completed_capabilities | join(",")' <<<"$report")"
assert_eq "coverage is measured against the declared capability contract" "2/2" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .lane_capability_coverage.baseline | "\(.completed_count)/\(.expected_count)"' <<<"$report")"
assert_eq "incomplete capabilities remain visible" "security" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-b") | .lane_capability_coverage.baseline.incomplete_capabilities | join(",")' <<<"$report")"
assert_eq "matching behavior markers report parity" "true" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .external_behavior_parity.matches' <<<"$report")"
assert_eq "mismatched behavior markers are named" "payload_sha256" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-b") | .external_behavior_parity.mismatched_markers | join(",")' <<<"$report")"
assert_eq "parity mismatch is an explicit failure verdict" "fail" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-b") | .external_behavior_parity.verdict' <<<"$report")"
assert_eq "report retains the exact-head identity" "acme/widgets#42@bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .exact_head | "\(.repository)#\(.pr_number)@\(.head_sha)"' <<<"$report")"
assert_eq "finding stability preserves shadow-only truth-labeled finding" \
  "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .finding_candidate_stability.shadow_only_finding_ids | join(",")' <<<"$report")"
assert_eq "disagreements remain visible" \
  "7c8f84721ed5493c41e968d2675e80e7d52c540c8b54ff7e65d15a4f18efe029" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .finding_candidate_stability.disagreement_candidate_fingerprint_ids | join(",")' <<<"$report")"
assert_eq "uncertain candidates remain separate" \
  "45780b4a82ed65ffbbff72155a8cda1bc95922f960ae09479d7c0f5db55f5a20" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .finding_candidate_stability.shadow_uncertain_candidate_ids | join(",")' <<<"$report")"
baseline_run_id="$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .receipts.baseline.run_id' <<<"$report")"
shadow_run_id="$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .receipts.shadow.run_id' <<<"$report")"
assert_ne "paired arms retain distinct receipt run IDs" "$baseline_run_id" "$shadow_run_id"
assert_ne "paired arms retain distinct receipt IDs" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .receipts.baseline.receipt_id' <<<"$report")" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .receipts.shadow.receipt_id' <<<"$report")"
assert_eq "equivalent cross-run candidates intersect by sanitized fingerprint" \
  "011db06ab9863de2385f9c26d4826e81c619a601fbf2d77936e26d1ea06565a7,561e91fe4d10fa1dc93c3d3c236ca69aabbb1aca4a0c00e26b66be12e65635f7" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .finding_candidate_stability.common_candidate_fingerprint_ids | join(",")' <<<"$report")"
baseline_candidate_id="$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .finding_candidate_stability.baseline_candidate_ids[0]' <<<"$report")"
shadow_candidate_id="$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .finding_candidate_stability.shadow_candidate_ids[0]' <<<"$report")"
assert_ne "equivalent fingerprints retain distinct run-scoped candidate IDs" "$baseline_candidate_id" "$shadow_candidate_id"
assert_eq "report never intersects run-scoped candidate IDs" "false" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .finding_candidate_stability | has("common_candidate_ids")' <<<"$report")"
assert_eq "same-provider reported usage is measured without an improvement claim" "true:measured:-15" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-a") | .usage_comparability | "\(.comparable):\(.efficiency_verdict):\(.deltas.total_tokens)"' <<<"$report")"
assert_eq "estimated usage is unavailable for comparison" "false:unavailable" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-b") | .usage_comparability | "\(.comparable):\(.efficiency_verdict)"' <<<"$report")"
assert_eq "missing usage remains null rather than zero" "null,null,null" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-c") | .usage_comparability.baseline | [.input_tokens,.output_tokens,.total_tokens] | map(if . == null then "null" else tostring end) | join(",")' <<<"$report")"
assert_eq "mismatched provider family is unavailable" "unavailable" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-d") | .usage_comparability.efficiency_verdict' <<<"$report")"
assert_eq "mismatched measurement scope is unavailable" "unavailable" \
  "$(jq -r '.pairs[] | select(.pair_id=="pair-e") | .usage_comparability.efficiency_verdict' <<<"$report")"

head -n 1 "$FIXTURE" >"$TEST_ROOT/one.jsonl"

write_path_variant() { # $1=path $2=output corpus; rehashes the typed fingerprint canonically
  local path="$1" output="$2" raw="$2.raw" line fingerprint canonical fingerprint_id run_id candidate_id old_candidate_id
  line="$(jq -c --arg path "$path" '.baseline.observed_candidates[1].fingerprint.path=$path' "$TEST_ROOT/one.jsonl")" || return
  fingerprint="$(jq -c '.baseline.observed_candidates[1].fingerprint' <<<"$line")" || return
  canonical="$(jq -S -c 'del(.fingerprint_id)' <<<"$fingerprint")" || return
  fingerprint_id="$(sha256_text "$canonical")" || return
  run_id="$(jq -r '.baseline.observed_candidates[1].run_id' <<<"$line")" || return
  old_candidate_id="$(jq -r '.baseline.observed_candidates[1].candidate_id' <<<"$line")" || return
  candidate_id="$(sha256_text "$run_id|$fingerprint_id")" || return
  jq -c --arg fingerprint_id "$fingerprint_id" --arg candidate_id "$candidate_id" --arg old_candidate_id "$old_candidate_id" '
    .baseline.observed_candidates[1].fingerprint.fingerprint_id=$fingerprint_id |
    .baseline.observed_candidates[1].candidate_id=$candidate_id |
    .baseline.observed_findings |= map(if .candidate_id == $old_candidate_id then .candidate_id=$candidate_id else . end)
  ' <<<"$line" >"$raw"
  rehash_arm_receipt "$raw" baseline "$output"
}

write_side_variant() { # $1=side $2=output corpus; rehashes the typed fingerprint canonically
  local side="$1" output="$2" raw="$2.raw" line fingerprint canonical fingerprint_id run_id candidate_id old_candidate_id
  line="$(jq -c --arg side "$side" '.baseline.observed_candidates[1].fingerprint.side=$side' "$TEST_ROOT/one.jsonl")" || return
  fingerprint="$(jq -c '.baseline.observed_candidates[1].fingerprint' <<<"$line")" || return
  canonical="$(jq -S -c 'del(.fingerprint_id)' <<<"$fingerprint")" || return
  fingerprint_id="$(sha256_text "$canonical")" || return
  run_id="$(jq -r '.baseline.observed_candidates[1].run_id' <<<"$line")" || return
  old_candidate_id="$(jq -r '.baseline.observed_candidates[1].candidate_id' <<<"$line")" || return
  candidate_id="$(sha256_text "$run_id|$fingerprint_id")" || return
  jq -c --arg fingerprint_id "$fingerprint_id" --arg candidate_id "$candidate_id" --arg old_candidate_id "$old_candidate_id" '
    .baseline.observed_candidates[1].fingerprint.fingerprint_id=$fingerprint_id |
    .baseline.observed_candidates[1].candidate_id=$candidate_id |
    .baseline.observed_findings |= map(if .candidate_id == $old_candidate_id then .candidate_id=$candidate_id else . end)
  ' <<<"$line" >"$raw"
  rehash_arm_receipt "$raw" baseline "$output"
}

path_case=0
for unsafe_path in '' 'src/./x' 'src//x' 'src/x/' 'src\x' '../x' '/absolute/x' $'src/\tcontrol'; do
  path_case=$((path_case + 1))
  write_path_variant "$unsafe_path" "$TEST_ROOT/unsafe-path-$path_case.jsonl"
  assert_rejected "runtime-unsafe fingerprint path [$path_case] fails after canonical rehash" "$TEST_ROOT/unsafe-path-$path_case.jsonl"
done

write_path_variant 'src/nested/valid-file.sh' "$TEST_ROOT/valid-path.jsonl"
"$BENCHMARK" score --corpus "$TEST_ROOT/valid-path.jsonl" >/dev/null 2>&1
valid_path_rc=$?
assert_eq "canonical nested relative paths remain accepted" "0" "$valid_path_rc"

write_side_variant 'FILE' "$TEST_ROOT/file-side.jsonl"
"$BENCHMARK" score --corpus "$TEST_ROOT/file-side.jsonl" >/dev/null 2>&1
file_side_rc=$?
assert_eq "canonical FILE-side fingerprints remain accepted" "0" "$file_side_rc"

write_side_variant 'HUNK' "$TEST_ROOT/invalid-side.jsonl"
assert_rejected "unknown fingerprint sides remain rejected after canonical rehash" "$TEST_ROOT/invalid-side.jsonl"

sed \
  -e 's/"input_tokens":90/"input_tokens":9007199254740990/' \
  -e 's/"input_tokens":100/"input_tokens":9007199254740991/' \
  -e 's/"total_tokens":120/"total_tokens":9007199254740991/' \
  -e 's/"total_tokens":105/"total_tokens":9007199254740990/' \
  "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/max-safe-usage.raw.jsonl"
rehash_arm_receipt "$TEST_ROOT/max-safe-usage.raw.jsonl" baseline "$TEST_ROOT/max-safe-usage.baseline.jsonl"
rehash_arm_receipt "$TEST_ROOT/max-safe-usage.baseline.jsonl" shadow "$TEST_ROOT/max-safe-usage.jsonl"
max_safe_report="$("$BENCHMARK" score --corpus "$TEST_ROOT/max-safe-usage.jsonl" 2>/dev/null)"
max_safe_rc=$?
assert_eq "maximum IEEE-754 safe usage integer is accepted" "0" "$max_safe_rc"
assert_eq "maximum safe usage integer retains an exact delta" "-1:-1" \
  "$(jq -r '.pairs[0].usage_comparability.deltas | "\(.input_tokens):\(.total_tokens)"' <<<"$max_safe_report")"

sed 's/"input_tokens":9007199254740991/"input_tokens":9007199254740992/' \
  "$TEST_ROOT/max-safe-usage.jsonl" >"$TEST_ROOT/unsafe-integer-usage.jsonl"
assert_rejected "usage above the IEEE-754 safe integer fails closed" "$TEST_ROOT/unsafe-integer-usage.jsonl"

cp "$TEST_ROOT/one.jsonl" "$TEST_ROOT/duplicate.jsonl"
cat "$TEST_ROOT/one.jsonl" >>"$TEST_ROOT/duplicate.jsonl"
assert_rejected "duplicate pair IDs fail closed" "$TEST_ROOT/duplicate.jsonl"

jq -c '.pair_id="malformed pair"' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/malformed-pair-id.jsonl"
assert_rejected "malformed pair IDs fail closed" "$TEST_ROOT/malformed-pair-id.jsonl"

printf '%s\n' '{not-json}' >"$TEST_ROOT/malformed.jsonl"
assert_rejected "malformed JSONL fails closed" "$TEST_ROOT/malformed.jsonl"

: >"$TEST_ROOT/empty.jsonl"
assert_rejected "empty corpus fails closed" "$TEST_ROOT/empty.jsonl"

jq -c '. + {raw_model_output:"forbidden"}' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/raw.jsonl"
assert_rejected "raw provider output fields fail closed" "$TEST_ROOT/raw.jsonl"

jq -c '.baseline.behavior.prompt="forbidden"' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/prompt.jsonl"
assert_rejected "nested prompt fields fail closed" "$TEST_ROOT/prompt.jsonl"

for forbidden_field in source diff excerpt raw; do
  jq -c --arg field "$forbidden_field" '.baseline.behavior += {($field):"forbidden"}' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/$forbidden_field.jsonl"
  assert_rejected "nested $forbidden_field fields fail closed" "$TEST_ROOT/$forbidden_field.jsonl"
done

jq -c 'del(.exact_head.head_sha)' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/missing.jsonl"
assert_rejected "missing exact-head identity fails closed" "$TEST_ROOT/missing.jsonl"

jq -c '.expected_findings += [.expected_findings[0]]' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/duplicate-findings.jsonl"
assert_rejected "duplicate truth labels fail closed" "$TEST_ROOT/duplicate-findings.jsonl"

jq -c '.baseline.usage.input_tokens="100"' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/string-usage.jsonl"
assert_rejected "string token metrics fail closed" "$TEST_ROOT/string-usage.jsonl"

jq -c '.baseline.usage.provenance="unavailable" | .baseline.usage.input_tokens=0' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/zero-unavailable.jsonl"
assert_rejected "unavailable usage cannot zero-fill metrics" "$TEST_ROOT/zero-unavailable.jsonl"

jq -c '.baseline.uncertain_candidate_ids=["9999999999999999999999999999999999999999999999999999999999999999"]' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/orphan-uncertain.jsonl"
assert_rejected "uncertain IDs must reference observed candidates" "$TEST_ROOT/orphan-uncertain.jsonl"

jq -c '.baseline.observed_candidates[0].run_id=.shadow.receipt.run_id' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/candidate-run-mismatch.jsonl"
assert_rejected "candidate IDs remain bound to their receipt run" "$TEST_ROOT/candidate-run-mismatch.jsonl"

jq -c '.shadow.observed_candidates[0].fingerprint.path="src/different-claim.sh"' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/fingerprint-collision.jsonl"
assert_rejected "one fingerprint ID cannot name different typed claims across runs" "$TEST_ROOT/fingerprint-collision.jsonl"

jq -c '.baseline.receipt.review_key="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/receipt-review-mismatch.jsonl"
assert_rejected "receipt identities remain bound to the exact-head review" "$TEST_ROOT/receipt-review-mismatch.jsonl"

jq -c '.exact_head.review_key="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" | .baseline.receipt.review_key=.exact_head.review_key | .shadow.receipt.review_key=.exact_head.review_key' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/arbitrary-review-key.jsonl"
assert_rejected "matching but noncanonical review keys fail closed" "$TEST_ROOT/arbitrary-review-key.jsonl"

jq -c '.shadow.observed_candidates[0].candidate_id=.baseline.observed_candidates[0].candidate_id' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/candidate-id-reuse.jsonl"
assert_rejected "candidate IDs cannot map to distinct run IDs" "$TEST_ROOT/candidate-id-reuse.jsonl"

jq -c '.baseline.observed_candidates[0].candidate_id="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/noncanonical-candidate-id.jsonl"
assert_rejected "arbitrary candidate IDs fail canonical validation" "$TEST_ROOT/noncanonical-candidate-id.jsonl"

jq -c '.shadow.receipt.content_sha256=.baseline.receipt.content_sha256' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/paired-receipt-hash-reuse.jsonl"
assert_rejected "a receipt content hash must match the shadow arm canonical content" "$TEST_ROOT/paired-receipt-hash-reuse.jsonl"

jq -c '.shadow.receipt.receipt_id=.baseline.receipt.receipt_id' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/paired-receipt-id-reuse.jsonl"
assert_rejected "paired receipt IDs must differ" "$TEST_ROOT/paired-receipt-id-reuse.jsonl"

jq -c '.shadow.observed_candidates[0].fingerprint.fingerprint_id="9999999999999999999999999999999999999999999999999999999999999999"' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/noncanonical-fingerprint-id.jsonl"
assert_rejected "identical typed claims cannot use different fingerprint IDs" "$TEST_ROOT/noncanonical-fingerprint-id.jsonl"

jq -s '.[0] as $first | .[1].baseline.receipt.run_id=$first.baseline.receipt.run_id | .[1].baseline.observed_candidates |= map(.run_id=$first.baseline.receipt.run_id) | .[]' "$FIXTURE" >"$TEST_ROOT/run-id-reuse.jsonl"
assert_rejected "one run ID cannot map to distinct exact-head identities" "$TEST_ROOT/run-id-reuse.jsonl"

jq -s '.[0] as $first | .[1].baseline.receipt.content_sha256=$first.baseline.receipt.content_sha256 | .[]' "$FIXTURE" >"$TEST_ROOT/receipt-hash-reuse.jsonl"
assert_rejected "a reused content hash must still match each arm canonical content" "$TEST_ROOT/receipt-hash-reuse.jsonl"

jq -s '.[0] as $first | .[1].baseline.receipt.receipt_id=$first.baseline.receipt.receipt_id | .[]' "$FIXTURE" >"$TEST_ROOT/receipt-id-reuse.jsonl"
assert_rejected "receipt IDs cannot be reused across distinct identities" "$TEST_ROOT/receipt-id-reuse.jsonl"

jq -c 'del(.expected_capability_ids)' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/capability-omitted.jsonl"
assert_rejected "capability contract cannot be omitted" "$TEST_ROOT/capability-omitted.jsonl"

jq -c '.expected_capability_ids=[]' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/capability-empty.jsonl"
assert_rejected "capability contract cannot be empty" "$TEST_ROOT/capability-empty.jsonl"

jq -c '.expected_capability_ids += [.expected_capability_ids[0]]' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/capability-duplicate.jsonl"
assert_rejected "capability contract must be unique" "$TEST_ROOT/capability-duplicate.jsonl"

jq -c '.baseline.lanes[0].capability="unexpected"' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/capability-unexpected.jsonl"
assert_rejected "lane results cannot add undeclared capabilities" "$TEST_ROOT/capability-unexpected.jsonl"

jq -c '.baseline.lanes=[]' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/capability-missing.jsonl"
assert_rejected "lane results must cover every expected capability" "$TEST_ROOT/capability-missing.jsonl"

jq -c '.disagreement_candidate_fingerprint_ids=["9999999999999999999999999999999999999999999999999999999999999999"]' "$TEST_ROOT/one.jsonl" >"$TEST_ROOT/orphan-disagreement.jsonl"
assert_rejected "disagreement IDs must reference a paired observation" "$TEST_ROOT/orphan-disagreement.jsonl"

ln -s "$FIXTURE" "$TEST_ROOT/corpus-link.jsonl"
assert_rejected "symlink corpus is rejected" "$TEST_ROOT/corpus-link.jsonl"

source_probe="$(bash -c 'before_flags=$-; before_umask=$(umask); before_pwd=$PWD; source "$1"; printf "%s|%s|%s|%s|%s|%s" "$before_flags" "$-" "$before_umask" "$(umask)" "$before_pwd" "$PWD"' _ "$BENCHMARK")"
IFS='|' read -r before_flags after_flags before_umask after_umask before_pwd after_pwd <<<"$source_probe"
assert_eq "sourcing preserves caller shell options" "$before_flags" "$after_flags"
assert_eq "sourcing preserves caller umask" "$before_umask" "$after_umask"
assert_eq "sourcing preserves caller working directory" "$before_pwd" "$after_pwd"

if grep -En '(^|[^[:alnum:]_])(claude|codex|gemini|gh|curl)([^[:alnum:]_]|$)' "$BENCHMARK" >"$TEST_ROOT/forbidden-commands"; then
  fail "benchmark contains a forbidden model, network, or GitHub command"
else
  pass
fi

fixture_before="$(shasum -a 256 "$FIXTURE" | awk '{print $1}')"
"$BENCHMARK" score --corpus "$FIXTURE" >/dev/null
fixture_after="$(shasum -a 256 "$FIXTURE" | awk '{print $1}')"
assert_eq "scoring does not mutate the corpus" "$fixture_before" "$fixture_after"

cp "$FIXTURE" "$TEST_ROOT/race.jsonl"
mkdir "$TEST_ROOT/race-bin"
real_jq="$(command -v jq)"
# shellcheck disable=SC2016 # Literal wrapper body expands only when the race probe runs.
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'first=0' \
  'last_arg=""' \
  'for arg in "$@"; do last_arg="$arg"; done' \
  'if [ ! -e "$RACE_MARKER" ]; then' \
  '  first=1' \
  '  printf "%s" "$last_arg" >"$RACE_PATH"' \
  '  if stat -f "%Lp" "$last_arg" >/dev/null 2>&1; then stat -f "%Lp" "$last_arg" >"$RACE_MODE"; else stat -c "%a" "$last_arg" >"$RACE_MODE"; fi' \
  'fi' \
  '"$RACE_REAL_JQ" "$@"' \
  'rc=$?' \
  'if [ "$first" -eq 1 ]; then' \
  '  : >"$RACE_MARKER"' \
  '  printf "%s\n" "{swapped-after-validation}" >"$RACE_CORPUS"' \
  'fi' \
  'exit "$rc"' >"$TEST_ROOT/race-bin/jq"
chmod +x "$TEST_ROOT/race-bin/jq"
race_report="$(PATH="$TEST_ROOT/race-bin:$PATH" RACE_REAL_JQ="$real_jq" RACE_MARKER="$TEST_ROOT/race.marker" RACE_CORPUS="$TEST_ROOT/race.jsonl" \
  RACE_MODE="$TEST_ROOT/race.mode" RACE_PATH="$TEST_ROOT/race.path" \
  "$BENCHMARK" score --corpus "$TEST_ROOT/race.jsonl" 2>"$TEST_ROOT/race.err")"
race_rc=$?
assert_eq "validate and score use one immutable private snapshot" "0" "$race_rc"
assert_eq "source swap after validation cannot alter report bytes" "$report" "$race_report"
assert_ne "validation reads the snapshot rather than the caller path" "$TEST_ROOT/race.jsonl" "$(cat "$TEST_ROOT/race.path")"
assert_eq "private snapshot permissions are restrictive" "600" "$(cat "$TEST_ROOT/race.mode")"

awk '{line[NR]=$0} END {for (i=NR;i>0;i--) print line[i]}' "$FIXTURE" >"$TEST_ROOT/reversed.jsonl"
reversed_report="$("$BENCHMARK" score --corpus "$TEST_ROOT/reversed.jsonl")"
assert_eq "corpus input order does not change sorted report bytes" "$report" "$reversed_report"
assert_eq "sanitized fixture has an exact expected report" \
  "ba424ec4a677c26d1941f50be76c81ae51b7daea8176d26eff5683d7c1d94fa1" \
  "$(sha256_text "$report")"

if jq -r '.. | strings' <<<"$report" | grep -Ei '(improved|release[_ -]?gate|pass[_ -]?threshold)' >/dev/null; then
  fail "baseline report makes an unsupported improvement or release claim"
else
  pass
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
