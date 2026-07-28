#!/usr/bin/env bash
# review-ablation.sh — A/B harness for judging a cut to the review skill.
#
# Prose has no test. Deleting instruction text from SKILL.md leaves every shell
# assertion green, because they exercise the scripts, not the wording. This
# script is the missing failure signal: run the same frozen PR corpus through
# two builds of the skill and decide, against a rule pre-registered before any
# cut, whether the outcome moved.
#
#   arm      build one arm tree from a baseline and PROVE the ablation took
#            effect by verbatim span match against the enumerated spec
#   run      write the runner's manifest, execute one headless review, and
#            collect its receipt
#   compare  manifests + receipts -> a verdict under the joint permutation rule
#
# Split this way so `compare` is unit-testable against synthetic manifests and
# receipts with no model in the loop.
#
# What a verdict does NOT say is as load-bearing as what it does; both
# sentences ride in the verdict's `certifies` object rather than living only in
# a design document. See kc-pr-flow/CLAUDE.md.
#
# Source-safe: this file declares functions only unless executed directly.

review_ablation_here() {
  local src="${BASH_SOURCE[0]}"
  cd "$(dirname "$src")" && pwd
}

review_ablation_require() {
  local tool
  for tool in "$@"; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      printf 'review-ablation: %s is required\n' "$tool" >&2
      return 69
    fi
  done
}

review_ablation_die() {
  printf 'review-ablation: %s\n' "$1" >&2
  return 1
}

review_ablation_usage() {
  cat >&2 <<'USAGE'
usage:
  review-ablation.sh arm --tree <baseline> --dest <dir> --arm A|A_prime|B
                         [--table <spans.tsv>] [--spans S1,S2,...] [--write-pins]
  review-ablation.sh run --arm-dir <dir> --arm <arm> --experiment-id <id>
                         --nonce <uuid> --run-index <n> --slot-index <n>
                         --repository <owner/name> --pr-number <n>
                         --base-sha <sha> --head-sha <sha>
                         --source-repo <git-dir> [--corpus <corpus.tsv>]
                         --out-dir <dir> --model <id> [--driver-prompt <file>]
  review-ablation.sh compare --mode AA|AB --arms X,Y --manifest-dir <dir>
                             [--alpha 0.05]
USAGE
  return 2
}

# ------------------------------------------------------------------------ arm

review_ablation_arm() {
  local tree='' dest='' arm='' table='' spans='' spans_given='' write_pins='' here core
  here="$(review_ablation_here)" || return 69
  core="$here/review-ablation-core.py"
  table="$here/review-ablation-spans.tsv"

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --tree) tree="$2"; shift 2 ;;
      --dest) dest="$2"; shift 2 ;;
      --arm) arm="$2"; shift 2 ;;
      --table) table="$2"; shift 2 ;;
      --spans) spans="$2"; spans_given='yes'; shift 2 ;;
      --write-pins) write_pins='yes'; shift ;;
      *) review_ablation_usage; return 2 ;;
    esac
  done

  review_ablation_require python3 || return 69
  [ -n "$tree" ] || { review_ablation_usage; return 2; }

  if [ -n "$write_pins" ]; then
    python3 "$core" write-pins --tree "$tree" --table "$table"
    return
  fi

  if [ -z "$dest" ] || [ -z "$arm" ]; then
    review_ablation_usage
    return 2
  fi

  # --spans is forwarded only when the caller actually passed it, so an unset
  # flag means "the enumerated spec" while an explicitly empty one means
  # "nothing" — which the core rejects for an ablated arm rather than silently
  # building a baseline copy labelled B.
  if [ -n "$spans_given" ]; then
    python3 "$core" arm --tree "$tree" --dest "$dest" --arm "$arm" \
      --table "$table" --spans "$spans"
  else
    python3 "$core" arm --tree "$tree" --dest "$dest" --arm "$arm" --table "$table"
  fi
}

# ------------------------------------------------------------------------ run
#
# The manifest is the runner's own record of the run, written BEFORE the agent
# is launched. Its path is not passed directly to the agent, so under ordinary
# operation it is a runner-authored authority for freshness and provenance.
# This is not filesystem isolation: the agent receives a sibling receipt path
# and the runner does not make the manifest or its ancestors unwritable.

review_ablation_run() {
  local arm_dir='' arm='' experiment_id='' nonce='' run_index='' slot_index=''
  local repository='' pr_number='' base_sha='' head_sha='' out_dir='' model=''
  local source_repo='' corpus='' driver_prompt='' here core manifest receipt
  local started prompt_sha rc arm_pins skill_sha arm_manifest_sha checkout_root
  local checkout checkout_head diff_sha runner_output runtime_json actual_model
  local manifest_tmp receipt_tmp runtime_usage runtime_wallclock post_head

  here="$(review_ablation_here)" || return 69
  core="$here/review-ablation-core.py"
  driver_prompt="$here/review-ablation-driver-prompt.md"
  corpus="$here/review-ablation-corpus.tsv"

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --arm-dir) arm_dir="$2"; shift 2 ;;
      --arm) arm="$2"; shift 2 ;;
      --experiment-id) experiment_id="$2"; shift 2 ;;
      --nonce) nonce="$2"; shift 2 ;;
      --run-index) run_index="$2"; shift 2 ;;
      --slot-index) slot_index="$2"; shift 2 ;;
      --repository) repository="$2"; shift 2 ;;
      --pr-number) pr_number="$2"; shift 2 ;;
      --base-sha) base_sha="$2"; shift 2 ;;
      --head-sha) head_sha="$2"; shift 2 ;;
      --source-repo) source_repo="$2"; shift 2 ;;
      --corpus) corpus="$2"; shift 2 ;;
      --out-dir) out_dir="$2"; shift 2 ;;
      --model) model="$2"; shift 2 ;;
      --driver-prompt) driver_prompt="$2"; shift 2 ;;
      *) review_ablation_usage; return 2 ;;
    esac
  done

  review_ablation_require git jq python3 shasum || return 69
  if [ -z "$arm_dir" ] || [ -z "$arm" ] || [ -z "$experiment_id" ] ||
    [ -z "$nonce" ] || [ -z "$run_index" ] || [ -z "$slot_index" ] ||
    [ -z "$repository" ] || [ -z "$pr_number" ] || [ -z "$base_sha" ] ||
    [ -z "$head_sha" ] || [ -z "$source_repo" ] || [ -z "$out_dir" ] ||
    [ -z "$model" ]; then
    review_ablation_usage
    return 2
  fi
  [ -f "$driver_prompt" ] ||
    { review_ablation_die "driver prompt is missing: $driver_prompt"; return 1; }
  [ -d "$arm_dir" ] ||
    { review_ablation_die "arm directory is missing: $arm_dir"; return 1; }
  [ -d "$source_repo" ] ||
    { review_ablation_die "source repo directory is missing: $source_repo"; return 1; }
  [ -f "$corpus" ] ||
    { review_ablation_die "frozen corpus is missing: $corpus"; return 1; }

  arm_dir="$(cd "$arm_dir" && pwd)" || return 1
  source_repo="$(cd "$source_repo" && pwd)" || return 1
  driver_prompt="$(cd "$(dirname "$driver_prompt")" && pwd)/$(basename "$driver_prompt")" ||
    return 1
  corpus="$(cd "$(dirname "$corpus")" && pwd)/$(basename "$corpus")" || return 1
  mkdir -p "$out_dir" || return 1
  out_dir="$(cd "$out_dir" && pwd)" || return 1

  python3 "$core" corpus --table "$corpus" --repository "$repository" \
    --pr-number "$pr_number" --base-sha "$base_sha" --head-sha "$head_sha" ||
    return 1
  arm_pins="$(python3 "$core" arm-manifest --arm-dir "$arm_dir" --arm "$arm")" ||
    return 1
  skill_sha="$(printf '%s' "$arm_pins" | jq -r '.skill_sha256')" || return 1
  arm_manifest_sha="$(printf '%s' "$arm_pins" | jq -r '.arm_manifest_sha256')" ||
    return 1

  if ! git -C "$source_repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    review_ablation_die "source repo is not a git worktree: $source_repo"
    return 1
  fi
  if [ "$(git -C "$source_repo" rev-parse "$base_sha^{commit}" 2>/dev/null)" != "$base_sha" ]; then
    review_ablation_die "frozen corpus base commit is unavailable from source repo: $base_sha"
    return 1
  fi
  if [ "$(git -C "$source_repo" rev-parse "$head_sha^{commit}" 2>/dev/null)" != "$head_sha" ]; then
    review_ablation_die "frozen corpus head commit is unavailable from source repo: $head_sha"
    return 1
  fi

  mkdir -p "$out_dir/manifests" "$out_dir/receipts" "$out_dir/checkouts" || return 1
  manifest="$out_dir/manifests/$arm-$pr_number-$run_index.json"
  receipt="$out_dir/receipts/$arm-$pr_number-$run_index.json"
  runner_output="$out_dir/receipts/$arm-$pr_number-$run_index.runner.json"

  # These deterministic paths may contain a prior attempt. Clear them before
  # launch so a crashed retry cannot be mistaken for a successful fresh run.
  rm -f "$receipt" "$runner_output" || return 1

  checkout_root="$out_dir/checkouts"
  checkout="$(mktemp -d "$checkout_root/$arm-$pr_number-$run_index.XXXXXX")" ||
    return 1
  git clone --quiet --shared --no-checkout "$source_repo" "$checkout" || return 1
  git -C "$checkout" checkout --quiet --detach "$head_sha" || return 1
  checkout_head="$(git -C "$checkout" rev-parse HEAD)" || return 1
  if [ "$checkout_head" != "$head_sha" ]; then
    review_ablation_die "pristine checkout resolved HEAD $checkout_head, expected frozen head $head_sha"
    return 1
  fi
  if [ -n "$(git -C "$checkout" status --porcelain)" ]; then
    review_ablation_die "pristine checkout is dirty before launch: $checkout"
    return 1
  fi
  diff_sha="$(git -C "$checkout" diff --binary "$base_sha...$head_sha" |
    shasum -a 256 | awk '{print $1}')" || return 1

  # The driver prompt is a single fixed file, byte-identical across arms. Its
  # hash is pinned into every receipt so a verdict assembled from receipts with
  # two different prompts is rejected rather than reported.
  prompt_sha="$(shasum -a 256 "$driver_prompt" | awk '{print $1}')" || return 1
  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)" || return 1

  jq -n --arg exp "$experiment_id" --arg nonce "$nonce" --arg arm "$arm" \
    --argjson run "$run_index" --argjson slot "$slot_index" \
    --arg repo "$repository" --argjson num "$pr_number" \
    --arg base "$base_sha" --arg head "$head_sha" \
    --arg skill "$skill_sha" --arg arm_manifest "$arm_manifest_sha" \
    --arg prompt "$prompt_sha" --arg requested_model "$model" \
    --arg checkout "$checkout" --arg checkout_head "$checkout_head" \
    --arg diff "$diff_sha" --arg started "$started" --arg receipt "$receipt" \
    '{schema:"kc-pr-flow.ablation-manifest/v2",
      experiment_id:$exp, nonce:$nonce, arm:$arm,
      run_index:$run, slot_index:$slot,
      pr:{repository:$repo,number:$num,base_sha:$base,head_sha:$head},
      skill_sha256:$skill, arm_manifest_sha256:$arm_manifest,
      driver_prompt_sha256:$prompt, requested_model_id:$requested_model,
      model_id:null,
      checkout:{path:$checkout,base_sha:$base,head_sha:$checkout_head,
                diff_sha256:$diff},
      run_started_at:$started, expected_receipt_path:$receipt}' >"$manifest" || return 1

  # The agent gets the receipt path and the pins it must echo, but not the
  # manifest path. The command runs from a runner-created pristine checkout at
  # the corpus head, with the base-to-head diff independently hashed above.
  (
    cd "$checkout" || exit 1
    KC_PR_FLOW_ABLATION_RECEIPT="$receipt" \
    KC_PR_FLOW_ABLATION_EXPERIMENT_ID="$experiment_id" \
    KC_PR_FLOW_ABLATION_NONCE="$nonce" \
    KC_PR_FLOW_ABLATION_ARM="$arm" \
    KC_PR_FLOW_ABLATION_RUN_INDEX="$run_index" \
    KC_PR_FLOW_ABLATION_SLOT_INDEX="$slot_index" \
    KC_PR_FLOW_ABLATION_REPOSITORY="$repository" \
    KC_PR_FLOW_ABLATION_PR_NUMBER="$pr_number" \
    KC_PR_FLOW_ABLATION_BASE_SHA="$base_sha" \
    KC_PR_FLOW_ABLATION_HEAD_SHA="$head_sha" \
    KC_PR_FLOW_ABLATION_SKILL_SHA256="$skill_sha" \
    KC_PR_FLOW_ABLATION_ARM_MANIFEST_SHA256="$arm_manifest_sha" \
    KC_PR_FLOW_ABLATION_DRIVER_PROMPT_SHA256="$prompt_sha" \
      "${KC_PR_FLOW_ABLATION_EXEC:-claude}" -p "$(cat "$driver_prompt")" \
        --add-dir "$out_dir/receipts" \
        --plugin-dir "$arm_dir" --model "$model" --output-format json
  ) >"$runner_output" 2>&1
  rc=$?

  if [ "$rc" -ne 0 ]; then
    review_ablation_die "headless review exited $rc; receipt discarded, runner output: $runner_output"
    return 1
  fi
  if [ ! -s "$receipt" ]; then
    review_ablation_die "run $arm/$pr_number/$run_index wrote no receipt at $receipt (exit $rc) — FAILED, not empty"
    return 1
  fi

  runtime_json="$(awk 'NF { line=$0 } END { print line }' "$runner_output")"
  if ! printf '%s' "$runtime_json" | jq -e 'type == "object"' >/dev/null 2>&1; then
    review_ablation_die "headless review returned no parseable runtime JSON: $runner_output"
    return 1
  fi
  if [ "$(printf '%s' "$runtime_json" | jq -r '.is_error // false')" = 'true' ]; then
    review_ablation_die "headless review runtime reported is_error:true: $runner_output"
    return 1
  fi
  actual_model="$(printf '%s' "$runtime_json" |
    jq -r '(.modelUsage // {} | keys) as $k |
      if ($k | length) == 1 then $k[0] else empty end')" || return 1
  if [ -z "$actual_model" ]; then
    review_ablation_die "headless review did not report exactly one model id: $runner_output"
    return 1
  fi
  manifest_tmp="$manifest.tmp.$$"
  jq --arg model "$actual_model" '.model_id=$model' "$manifest" >"$manifest_tmp" ||
    return 1
  mv "$manifest_tmp" "$manifest" || return 1

  post_head="$(git -C "$checkout" rev-parse HEAD)" || return 1
  if [ "$post_head" != "$head_sha" ] ||
    [ -n "$(git -C "$checkout" status --porcelain)" ]; then
    review_ablation_die "headless review changed the frozen checkout; expected clean HEAD $head_sha"
    return 1
  fi

  # A run that exited clean without writing a receipt is a FAILED run, never an
  # empty finding set. Observed for real in spike 2: the agent deferred on
  # background work at turn 43, exited is_error:false, and wrote nothing. Had
  # that read as "0 findings", both arms would have compared identical and the
  # harness would have reported "no material difference" for a review that
  # never finished.
  if ! jq -e . "$receipt" >/dev/null 2>&1; then
    review_ablation_die "receipt is not parseable JSON: $receipt — FAILED, never an empty finding set"
    return 1
  fi
  runtime_usage="$(printf '%s' "$runtime_json" | jq -c '
    {input_tokens:.usage.input_tokens,
     output_tokens:.usage.output_tokens,
     cache_creation_input_tokens:.usage.cache_creation_input_tokens,
     cache_read_input_tokens:.usage.cache_read_input_tokens,
     total_cost_usd:.total_cost_usd}
    | if all([.input_tokens,.output_tokens,.cache_creation_input_tokens,
              .cache_read_input_tokens,.total_cost_usd][]; type == "number")
      then . else error("runtime usage is incomplete") end')" || {
        review_ablation_die "headless review runtime usage is incomplete: $runner_output"
        return 1
      }
  runtime_wallclock="$(printf '%s' "$runtime_json" |
    jq -er '.duration_ms | select(type == "number")')" || {
      review_ablation_die "headless review runtime duration_ms is missing: $runner_output"
      return 1
    }
  receipt_tmp="$receipt.tmp.$$"
  jq --arg model "$actual_model" --argjson usage "$runtime_usage" \
    --argjson wallclock "$runtime_wallclock" \
    '.model_id=$model | .usage=$usage | .wallclock_ms=$wallclock' \
    "$receipt" >"$receipt_tmp" || return 1
  mv "$receipt_tmp" "$receipt" || return 1
  review_ablation_guard_record "$(jq -c -n --slurpfile m "$manifest" \
    --slurpfile r "$receipt" --arg p "$receipt" \
    '[{manifest:$m[0],receipt:$r[0],receipt_path:$p}]')" || return 1
  printf '%s\n' "$receipt"
}

# -------------------------------------------------------------------- compare

review_ablation_compare() {
  local mode='' arms='' manifest_dir='' alpha='0.05' here core
  here="$(review_ablation_here)" || return 69
  core="$here/review-ablation-core.py"

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --mode) mode="$2"; shift 2 ;;
      --arms) arms="$2"; shift 2 ;;
      --manifest-dir) manifest_dir="$2"; shift 2 ;;
      --alpha) alpha="$2"; shift 2 ;;
      *) review_ablation_usage; return 2 ;;
    esac
  done

  review_ablation_require jq python3 || return 69
  if [ -z "$mode" ] || [ -z "$arms" ] || [ -z "$manifest_dir" ]; then
    review_ablation_usage
    return 2
  fi
  case "$mode" in
    AA | AB) ;;
    *) review_ablation_die "unknown mode: $mode (want AA or AB)"; return 1 ;;
  esac
  [ -d "$manifest_dir" ] ||
    { review_ablation_die "no manifest directory: $manifest_dir"; return 1; }

  local arm_x arm_y
  arm_x="${arms%%,*}"
  arm_y="${arms##*,}"
  if [ "$arm_x" = "$arm_y" ]; then
    review_ablation_die "--arms names one arm twice ($arm_x); an A/A comparison needs two independently built arms, not one arm against itself"
    return 1
  fi

  # ---- join manifests to receipts, then guard, before any statistic is taken.
  local joined
  joined="$(review_ablation_join "$manifest_dir")" || return 1
  review_ablation_guard "$joined" "$mode" "$arm_x" "$arm_y" || return 1

  # ---- canonicalize findings into fingerprint IDs, reusing the benchmark's
  # already-authored canonicalization rather than reimplementing it.
  local records stats
  records="$(review_ablation_fingerprints "$joined")" || return 1
  stats="$(printf '%s' "$records" | python3 "$core" stats --arms "$arm_x,$arm_y" --alpha "$alpha")" ||
    return 1

  printf '%s' "$stats" | jq -S \
    --arg mode "$mode" --arg x "$arm_x" --arg y "$arm_y" \
    --argjson prov "$(printf '%s' "$joined" | jq -c '{
        experiment_id: (map(.manifest.experiment_id) | unique | .[0]),
        model_id: (map(.manifest.model_id) | unique | .[0]),
        driver_prompt_sha256: (map(.manifest.driver_prompt_sha256) | unique | .[0]),
        corpus: (map(.manifest.pr) | unique)
      }')" \
    '{schema:"kc-pr-flow.ablation-verdict/v3", mode:$mode, arms:[$x,$y]} + $prov + .'
}

# Join every manifest in the directory to the receipt it names. This is where
# AC-3(b) lives: a manifest whose expected_receipt_path holds no file is a
# failed run and stops the verdict.
review_ablation_join() {
  local manifest_dir="$1" manifest path out
  out='[]'
  shopt -s nullglob
  local manifests=("$manifest_dir"/*.json)
  shopt -u nullglob
  if [ "${#manifests[@]}" -eq 0 ]; then
    review_ablation_die "no manifests under $manifest_dir"
    return 1
  fi
  for manifest in "${manifests[@]}"; do
    path="$(jq -r '.expected_receipt_path' "$manifest")" || return 1
    if [ ! -s "$path" ]; then
      review_ablation_die "no receipt at the manifest's expected_receipt_path: $path (manifest $manifest) — a run that wrote no receipt is FAILED, never an empty finding set"
      return 1
    fi
    if ! jq -e . "$path" >/dev/null 2>&1; then
      review_ablation_die "receipt is not parseable JSON: $path — FAILED, never an empty finding set"
      return 1
    fi
    out="$(jq -c -n --slurpfile m "$manifest" --slurpfile r "$path" \
      --argjson acc "$out" --arg p "$path" \
      '$acc + [{manifest:$m[0], receipt:$r[0], receipt_path:$p}]')" || return 1
  done
  printf '%s' "$out"
}

# The five AC-3 guards. Each compares a receipt against runner-authored state,
# the invocation's mode, or the rest of the experiment. The manifest is an
# independent write path in ordinary operation, not an OS-enforced trust
# boundary; review_ablation_run's comment records that residual explicitly.
review_ablation_guard() {
  local joined="$1" mode="$2" arm_x="$3" arm_y="$4" bad

  review_ablation_guard_record "$joined" || return 1

  # (d) duplicate — canonical receipt JSON minus {run_index, slot_index,
  # written_at}. Those three are projected OUT precisely so a receipt copied
  # from one run to another collides; hashing them in (round 1) made the guard
  # unable to fire.
  bad="$(printf '%s' "$joined" | jq -r '
    map(.receipt | del(.run_index, .slot_index, .written_at) | tojson)
    | group_by(.) | map(select(length > 1)) | length')"
  if [ "$bad" != '0' ]; then
    review_ablation_die "duplicate receipts: two runs are identical under the projection (canonical JSON minus run_index/slot_index/written_at) — a copied receipt inflates within-arm agreement"
    return 1
  fi

  # (e) provenance — runner-derived driver_prompt_sha256 and runtime-reported
  # model_id must agree across the WHOLE experiment.
  bad="$(printf '%s' "$joined" | jq -r 'map(.manifest.model_id) | unique | length')"
  if [ "$bad" != '1' ]; then
    review_ablation_die "model_id disagrees across the experiment ($bad distinct values) — a silently substituted model invalidates the comparison"
    return 1
  fi
  bad="$(printf '%s' "$joined" | jq -r 'map(.manifest.driver_prompt_sha256) | unique | length')"
  if [ "$bad" != '1' ]; then
    review_ablation_die "driver_prompt_sha256 disagrees across the experiment ($bad distinct values) — the arms were not driven by the same prompt"
    return 1
  fi

  # (a) mis-armed — a property of the INVOCATION and runner-read arm manifests.
  # Equal skill
  # hashes are required under AA and forbidden under AB, which is what lets one
  # 27-run experiment serve both ACs without copying arm A's receipts.
  local x_sha y_sha
  x_sha="$(printf '%s' "$joined" | jq -r --arg a "$arm_x" \
    'map(select(.manifest.arm == $a) | .manifest.skill_sha256) | unique | join(",")')"
  y_sha="$(printf '%s' "$joined" | jq -r --arg a "$arm_y" \
    'map(select(.manifest.arm == $a) | .manifest.skill_sha256) | unique | join(",")')"
  if [ -z "$x_sha" ] || [ -z "$y_sha" ]; then
    review_ablation_die "no receipts for arm $arm_x or arm $arm_y in this experiment"
    return 1
  fi
  case "$x_sha,$y_sha" in
    *,*,*) review_ablation_die "skill_sha256 is not constant within an arm ($arm_x=$x_sha $arm_y=$y_sha) — the arm tree changed mid-experiment"; return 1 ;;
  esac
  if [ "$mode" = 'AB' ] && [ "$x_sha" = "$y_sha" ]; then
    review_ablation_die "mis-armed pair: arms $arm_x and $arm_y share a skill_sha256 under --mode AB, so nothing was ablated"
    return 1
  fi
  if [ "$mode" = 'AA' ] && [ "$x_sha" != "$y_sha" ]; then
    review_ablation_die "arms $arm_x and $arm_y have differing skill_sha256 under --mode AA, so this is not an A/A comparison"
    return 1
  fi
}

review_ablation_guard_record() {
  local joined="$1" field bad
  for field in nonce arm experiment_id run_index slot_index pr skill_sha256 \
    arm_manifest_sha256 driver_prompt_sha256 model_id; do
    bad="$(printf '%s' "$joined" | jq -r --arg field "$field" '
      map(select(.receipt[$field] != .manifest[$field]))
      | .[0].receipt_path // empty')"
    if [ -n "$bad" ]; then
      review_ablation_die "$field disagrees with its runner-written manifest: $bad"
      return 1
    fi
  done
  bad="$(printf '%s' "$joined" | jq -r '
    map(select(.receipt.written_at < .manifest.run_started_at))
    | .[0].receipt_path // empty')"
  if [ -n "$bad" ]; then
    review_ablation_die "stale receipt: written_at precedes the manifest run_started_at, so the file predates the run that claims it: $bad"
    return 1
  fi
  bad="$(printf '%s' "$joined" | jq -r '
    map(select(
      .manifest.schema != "kc-pr-flow.ablation-manifest/v2" or
      .manifest.checkout.base_sha != .manifest.pr.base_sha or
      .manifest.checkout.head_sha != .manifest.pr.head_sha or
      ((.manifest.checkout.diff_sha256 // "") | test("^[0-9a-f]{64}$") | not)
    )) | .[0].receipt_path // empty')"
  if [ -n "$bad" ]; then
    review_ablation_die "runner manifest lacks valid frozen-checkout proof: $bad"
    return 1
  fi
}

# Canonicalize each finding into a fingerprint ID using the benchmark's own
# canonicalization (review_benchmark_fingerprint_id), so the projection this
# harness compares on is the one already authored and tested, not a second
# implementation that could drift from it.
review_ablation_fingerprints() {
  local joined="$1" here
  here="$(review_ablation_here)" || return 69
  # shellcheck source=/dev/null
  . "$here/review-runtime-benchmark.sh" || return 1

  local rows row pr arm idx findings finding fp ids sevs tokens out
  out='[]'
  rows="$(printf '%s' "$joined" | jq -c '.[]')" || return 1
  while IFS= read -r row; do
    [ -n "$row" ] || continue
    pr="$(printf '%s' "$row" | jq -r '.receipt.pr.number')"
    arm="$(printf '%s' "$row" | jq -r '.receipt.arm')"
    idx="$(printf '%s' "$row" | jq -r '.receipt.run_index')"
    tokens="$(printf '%s' "$row" | jq -r '
      .receipt.usage | (.input_tokens + .output_tokens + .cache_creation_input_tokens)')"
    findings="$(printf '%s' "$row" | jq -c '.receipt.findings[]?')"
    ids='[]'
    sevs='[]'
    while IFS= read -r finding; do
      [ -n "$finding" ] || continue
      fp="$(printf '%s' "$finding" | jq -c \
        '{path,side,anchor_sha256,evidence_sha256,category,claim_key}' |
        review_benchmark_fingerprint_id)" || return 1
      ids="$(printf '%s' "$ids" | jq -c --arg v "$fp" '. + [$v]')"
      sevs="$(printf '%s' "$sevs" | jq -c --arg v "$(printf '%s' "$finding" | jq -r '.severity')" '. + [$v]')"
    done <<<"$findings"
    out="$(printf '%s' "$out" | jq -c \
      --argjson pr "$pr" --arg arm "$arm" --argjson idx "$idx" \
      --argjson ids "$ids" --argjson sevs "$sevs" --argjson tokens "$tokens" \
      '. + [{pr:$pr, arm:$arm, run_index:$idx, fingerprints:$ids, severities:$sevs, tokens:$tokens}]')"
  done <<<"$rows"
  printf '%s' "$out" | jq -c '{runs: .}'
}

review_ablation_main() {
  local command="${1:-}"
  [ "$#" -gt 0 ] && shift
  case "$command" in
    arm) review_ablation_arm "$@" ;;
    run) review_ablation_run "$@" ;;
    compare) review_ablation_compare "$@" ;;
    *) review_ablation_usage ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  review_ablation_main "$@"
fi
