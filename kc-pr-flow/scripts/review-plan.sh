#!/usr/bin/env bash
# review-plan.sh — conservative, read-only exact-head delta routing.

review_plan_source_runtime() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 69
  # shellcheck source=/dev/null
  . "$here/review-runtime.sh" || return 69
}

review_plan_input_identity_valid() {
  jq -e -n --arg repository "$1" --arg pr_number "$2" --arg base_sha "$3" \
    --arg head_sha "$4" --arg config_hash "$5" '
    ($repository | test("^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")) and
    ($pr_number | test("^[1-9][0-9]*$")) and
    ($base_sha | test("^[0-9a-f]{40}$")) and
    ($head_sha | test("^[0-9a-f]{40}$")) and
    ($config_hash | test("^[0-9a-f]{64}$"))
  ' >/dev/null 2>&1
}

review_plan_build_decision() {
  local repository="$1" pr_number="$2" base_sha="$3" head_sha="$4" config_hash="$5"
  local mode="$6" reason_codes="$7" from_exclusive="$8" inherited_ids="$9"
  local capabilities="${10}" ceiling="${11}" requires_initial="${12}" review_key
  review_key="$(printf '%s|%s|%s|%s|%s' "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" |
    review_runtime_sha256)" || return
  jq -S -c -n \
    --arg repository "$repository" --argjson pr_number "$pr_number" \
    --arg base_sha "$base_sha" --arg head_sha "$head_sha" \
    --arg config_hash "$config_hash" --arg review_key "$review_key" \
    --arg mode "$mode" --argjson reasons "$reason_codes" \
    --argjson from_exclusive "$from_exclusive" --argjson inherited "$inherited_ids" \
    --argjson capabilities "$capabilities" --argjson ceiling "$ceiling" \
    --argjson requires_initial "$requires_initial" '
      {
        schema:"kc-pr-flow.review-plan-decision/v1",
        identity:{repository:$repository,pr_number:$pr_number,base_sha:$base_sha,
          head_sha:$head_sha,config_hash:$config_hash,review_key:$review_key},
        mode:$mode,
        reason_codes:($reasons | sort | unique),
        review_range:{from_exclusive:$from_exclusive,to_inclusive:$head_sha},
        inherited_finding_ids:($inherited | sort | unique),
        required_capabilities:($capabilities | sort | unique),
        event_ceiling:$ceiling,
        fallback:{router_advisory:true,requires_existing_initial_review:$requires_initial,
          final_verdict_authority:"existing-review-runtime"}
      }'
}

review_plan_initial_decision() {
  review_plan_build_decision "$1" "$2" "$3" "$4" "$5" initial \
    "[\"$6\"]" null '[]' '[]' null true
}


review_plan_real_worktree() (
  local candidate="$1" real top
  [ "$#" -eq 1 ] && [ -d "$candidate" ] && [ ! -L "$candidate" ] || return 2
  real="$(cd "$candidate" 2>/dev/null && pwd -P)" || return 2
  top="$(review_plan_git "$real" rev-parse --show-toplevel 2>/dev/null)" || return 2
  [ "$top" = "$real" ] || return 2
  printf '%s\n' "$real"
)

review_plan_git() {
  local worktree="$1"
  shift
  env -i PATH="$PATH" LC_ALL=C LANG=C HOME=/dev/null \
    GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null \
    GIT_NO_LAZY_FETCH=1 GIT_NO_REPLACE_OBJECTS=1 GIT_OPTIONAL_LOCKS=0 GIT_TERMINAL_PROMPT=0 \
    git -C "$worktree" --no-replace-objects \
      -c core.attributesFile=/dev/null -c core.fsmonitor=false -c diff.external= "$@"
}

review_plan_git_identity_valid() {
  [ "$(review_plan_git "$1" cat-file -t "$2" 2>/dev/null)" = commit ]
}

review_plan_ancestor() {
  review_plan_git "$1" merge-base --is-ancestor "$2" "$3" >/dev/null 2>&1
}

review_plan_safe_path() {
  local path="$1" part
  [ -n "$path" ] && [ "${#path}" -le 1024 ] || return 2
  case "$path" in
    /*|*/|*//*|*\\*|*$'\n'*|*$'\r'*|*$'\t'*) return 2 ;;
  esac
  IFS=/ read -r -a parts <<<"$path"
  for part in "${parts[@]}"; do
    [ -n "$part" ] && [ "$part" != . ] && [ "$part" != .. ] || return 2
  done
}

review_plan_changed_paths() {
  review_plan_git "$1" -c core.quotePath=true diff --no-ext-diff --no-textconv \
    --no-renames --name-status "$2" "$3" --
}

review_plan_changed_diff() {
  review_plan_git "$1" -c core.quotePath=true diff --no-ext-diff --no-textconv \
    --no-renames --no-color --unified=0 "$2" "$3" --
}

review_plan_tree_entry() {
  local row
  row="$(review_plan_git "$1" ls-tree "$2" -- "$3" 2>/dev/null)" || return 2
  [ -n "$row" ] || return 1
  printf '%s\n' "$row"
}

review_plan_blob_is_safe() (
  local worktree="$1" object="$2" max_bytes="${KC_PR_FLOW_MAX_PLAN_BLOB_BYTES:-1048576}"
  local size snapshot_dir blob_file
  review_runtime_positive_safe_integer "$max_bytes" || return 2
  [ "$max_bytes" -le 16777216 ] || return 2
  [ "$(review_plan_git "$worktree" cat-file -t "$object" 2>/dev/null)" = blob ] || return 2
  size="$(review_plan_git "$worktree" cat-file -s "$object" 2>/dev/null)" || return 2
  [ "$size" = 0 ] || review_runtime_positive_safe_integer "$size" || return 2
  [ "$size" -le "$max_bytes" ] || return 2
  snapshot_dir="$(review_runtime_private_snapshot_dir)" || return 2
  blob_file="$snapshot_dir/blob"
  trap 'review_runtime_remove_private_snapshot_dir "$snapshot_dir" "$blob_file"' EXIT
  review_plan_git "$worktree" cat-file blob "$object" >"$blob_file" 2>/dev/null || return 2
  [ "$(wc -c <"$blob_file" | tr -d ' ')" -eq "$size" ] || return 2
  python3 - "$blob_file" <<'PY'
import pathlib
import sys
data = pathlib.Path(sys.argv[1]).read_bytes()
if b"\0" in data:
    raise SystemExit(2)
try:
    data.decode("utf-8", "strict")
except UnicodeDecodeError:
    raise SystemExit(2)
PY
)

review_plan_changed_object_is_safe() {
  local worktree="$1" predecessor="$2" head="$3" path="$4"
  local row mode type object old_row old_mode old_type old_object rc
  review_plan_safe_path "$path" || return 2
  row="$(review_plan_tree_entry "$worktree" "$head" "$path")" || return 2
  IFS=$' \t' read -r mode type object _ <<<"$row"
  case "$mode:$type" in 100644:blob|100755:blob) ;; *) return 2 ;; esac
  review_plan_blob_is_safe "$worktree" "$object" || return 2
  old_row="$(review_plan_tree_entry "$worktree" "$predecessor" "$path" 2>/dev/null)"
  rc=$?
  if [ "$rc" -eq 1 ]; then return 0; fi
  [ "$rc" -eq 0 ] || return 2
  IFS=$' \t' read -r old_mode old_type old_object _ <<<"$old_row"
  case "$old_mode:$old_type" in 100644:blob|100755:blob) ;; *) return 2 ;; esac
  review_plan_blob_is_safe "$worktree" "$old_object"
}

review_plan_route_state() {
  local worktree="$1" base_sha="$2" head_sha="$3" actual_head status
  review_plan_git_identity_valid "$worktree" "$base_sha" || return 2
  review_plan_git_identity_valid "$worktree" "$head_sha" || return 2
  actual_head="$(review_plan_git "$worktree" rev-parse HEAD 2>/dev/null)" || return 2
  [ "$actual_head" = "$head_sha" ] || return 2
  status="$(review_plan_git "$worktree" status --porcelain=v1 --untracked-files=all 2>/dev/null)" || return 2
  [ -z "$status" ] || return 2
  printf '%s|%s\n' "$worktree" "$actual_head"
}

review_plan_snapshot_inputs() {
  local receipt_file="$1" event_file="$2" config_file="$3"
  local receipt_snapshot="$4" event_snapshot="$5" config_snapshot="$6"
  review_runtime_snapshot_regular_file "$receipt_file" "$receipt_snapshot" 'delta receipt' \
    "${KC_PR_FLOW_MAX_RECEIPT_BYTES:-1048576}" || return
  review_runtime_snapshot_regular_file "$event_file" "$event_snapshot" 'event file' \
    "${KC_PR_FLOW_MAX_EVENTS_BYTES:-16777216}" || return
  review_runtime_snapshot_regular_file "$config_file" "$config_snapshot" 'review config' \
    "${KC_PR_FLOW_MAX_CONFIG_BYTES:-1048576}"
}

review_plan_classify_hunks() (
  local worktree="$1" predecessor_head="$2" head_sha="$3" receipt="$4" changed="$5"
  local snapshot_dir diff_file receipt_file changed_file diff_bytes max_diff_bytes
  snapshot_dir="$(review_runtime_private_snapshot_dir)" || return 2
  diff_file="$snapshot_dir/review.diff"
  receipt_file="$snapshot_dir/receipt.json"
  changed_file="$snapshot_dir/changed.tsv"
  trap 'review_runtime_remove_private_snapshot_dir "$snapshot_dir" "$diff_file" "$receipt_file" "$changed_file"' EXIT
  printf '%s' "$receipt" >"$receipt_file" || return 2
  printf '%s\n' "$changed" >"$changed_file" || return 2
  review_plan_changed_diff "$worktree" "$predecessor_head" "$head_sha" >"$diff_file" || return 2
  diff_bytes="$(wc -c <"$diff_file" | tr -d ' ')" || return 2
  max_diff_bytes="${KC_PR_FLOW_MAX_PLAN_DIFF_BYTES:-4194304}"
  [[ "$max_diff_bytes" =~ ^[1-9][0-9]*$ ]] || return 2
  [ "$max_diff_bytes" -le 16777216 ] && [ "$diff_bytes" -le "$max_diff_bytes" ] || return 2

  python3 - "$receipt_file" "$diff_file" "$changed_file" "$predecessor_head" <<'PY'
import json
import os
import re
import sys


class ParseError(Exception):
    pass


def safe_path(path):
    if not isinstance(path, str) or not path or len(path) > 1024:
        return False
    if path.startswith("/") or path.endswith("/") or "//" in path or "\\" in path:
        return False
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in path):
        return False
    return all(component not in (".", "..", "") for component in path.split("/"))


def boundary_path(path):
    components = path.lower().split("/")
    name = components[-1]
    return (
        any(part in {"test", "tests", "__tests__", "fixture", "fixtures", "contract", "contracts"}
            for part in components[:-1])
        or name.startswith("test_")
        or re.search(r"(?:^|[._-])(?:test|spec|fixture|contract)(?:[._-]|$)", name) is not None
    )


DEPENDENCY_FILES = {
    "package.json", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml",
    "pnpm-workspace.yaml", "bun.lock", "bun.lockb", "deno.lock", "uv.lock",
    "requirements.txt", "requirements-dev.txt", "pyproject.toml", "poetry.lock",
    "pipfile", "pipfile.lock", "setup.py", "setup.cfg", "cargo.toml", "cargo.lock",
    "go.mod", "go.sum", "gemfile", "gemfile.lock", "composer.json", "composer.lock",
    "mix.exs", "mix.lock", "pubspec.yaml", "pubspec.lock", "gradle.lockfile",
}
SECURITY_PATH = re.compile(
    r"(?:^|/)(?:security|secure|policy|policies|auth|authentication|authorization|oauth|oidc|iam|"
    r"acl|rls|middleware|webhook|permission|permissions|rbac|vault|secret|secrets|token|credential|\.env)"
    r"[^/]*(?:/|$)",
    re.IGNORECASE,
)
SECURITY_BODY = re.compile(
    r"(?:auth(?:entication|orization)?|authori[sz]ation|permission|rbac|rls|secret|token|credential|password|"
    r"security|polic(?:y|ies)|webhook|middleware|bypass|subprocess|shell\s*=|eval\s*\(|exec\s*\()",
    re.IGNORECASE,
)
SIGNAL_CATEGORIES = {
    "security": {"security"},
    "supply-chain": {"dependency", "dependencies", "supply-chain"},
    "github-actions": {"github-actions", "workflow"},
}
SIGNAL_CAPABILITIES = {
    "security": "security",
    "supply-chain": "supply-chain",
    "github-actions": "github-actions",
}


def signal_capabilities(path, body):
    capabilities = set()
    lower_path = path.lower()
    name = lower_path.rsplit("/", 1)[-1]
    if SECURITY_PATH.search(path) or SECURITY_BODY.search(body):
        capabilities.add("security")
    if (
        name in DEPENDENCY_FILES
        or re.fullmatch(r"requirements(?:[-_.][a-z0-9_.-]+)?\.txt", name)
        or name.endswith(".lock")
    ):
        capabilities.add("supply-chain")
    workflow_tree = lower_path.startswith(".github/workflows/")
    if workflow_tree and re.fullmatch(r"\.github/workflows/[^/]+\.ya?ml", lower_path) is None:
        raise ParseError
    if workflow_tree or lower_path.startswith(".github/actions/") or name in {"action.yml", "action.yaml"}:
        capabilities.add("github-actions")
    return capabilities


def mapped_signal_capabilities(finding, receipt_capabilities):
    mapped = set()
    category = finding.get("category")
    for signal, categories in SIGNAL_CATEGORIES.items():
        if category in categories or SIGNAL_CAPABILITIES[signal] in receipt_capabilities:
            mapped.add(signal)
    return mapped


def module_token(path):
    stem, _ = os.path.splitext(path)
    return stem.replace("/", ".")


def malformed_result():
    return {"classification": "initial", "required_capabilities": []}


try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        receipt = json.load(handle)
    with open(sys.argv[2], encoding="utf-8", errors="strict") as handle:
        lines = handle.read().splitlines()
    with open(sys.argv[3], encoding="utf-8", errors="strict") as handle:
        changed_lines = handle.read().splitlines()
    predecessor_head = sys.argv[4]

    statuses = {}
    for line in changed_lines:
        fields = line.split("\t")
        if len(fields) != 2 or fields[0] not in {"A", "M"} or not safe_path(fields[1]):
            raise ParseError
        if fields[1] in statuses:
            raise ParseError
        statuses[fields[1]] = fields[0]
    if not statuses or not lines:
        raise ParseError

    findings = receipt.get("known_findings")
    if not isinstance(findings, list) or not findings:
        raise ParseError
    receipt_capabilities = receipt.get("required_capabilities")
    if (
        not isinstance(receipt_capabilities, list)
        or any(not isinstance(capability, str) for capability in receipt_capabilities)
    ):
        raise ParseError
    receipt_capabilities = set(receipt_capabilities)
    parsed_paths = set()
    capabilities = set()
    unmapped = False
    index = 0
    hunk_count = 0

    while index < len(lines):
        header = re.fullmatch(r"diff --git a/(.+) b/(.+)", lines[index])
        if not header or header.group(1) != header.group(2) or not safe_path(header.group(1)):
            raise ParseError
        path = header.group(1)
        if path not in statuses or path in parsed_paths:
            raise ParseError
        parsed_paths.add(path)
        index += 1

        while index < len(lines) and not lines[index].startswith("--- "):
            metadata = lines[index]
            if not (
                re.fullmatch(r"index [0-9a-f]+\.\.[0-9a-f]+(?: [0-7]{6})?", metadata)
                or re.fullmatch(r"new file mode 100(?:644|755)", metadata)
                or re.fullmatch(r"old mode 100(?:644|755)", metadata)
                or re.fullmatch(r"new mode 100(?:644|755)", metadata)
            ):
                raise ParseError
            index += 1
        if index + 1 >= len(lines):
            raise ParseError
        expected_old = "/dev/null" if statuses[path] == "A" else "a/" + path
        if lines[index] != "--- " + expected_old or lines[index + 1] != "+++ b/" + path:
            raise ParseError
        index += 2
        file_hunks = 0

        while index < len(lines) and not lines[index].startswith("diff --git "):
            match = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: .*)?", lines[index])
            if not match:
                raise ParseError
            old_start = int(match.group(1))
            old_count = int(match.group(2) or "1")
            new_count = int(match.group(4) or "1")
            index += 1
            removed = 0
            added = 0
            body_lines = []
            while index < len(lines):
                line = lines[index]
                if line.startswith("diff --git ") or line.startswith("@@ "):
                    break
                if line == r"\ No newline at end of file":
                    index += 1
                    continue
                if line.startswith("-"):
                    removed += 1
                    body_lines.append(line[1:])
                elif line.startswith("+"):
                    added += 1
                    body_lines.append(line[1:])
                else:
                    raise ParseError
                index += 1
            if removed != old_count or added != new_count or old_count + new_count == 0:
                raise ParseError
            body = "\n".join(body_lines)
            mapped = set()
            for finding_index, finding in enumerate(findings):
                evidence = finding.get("evidence", {})
                evidence_line = evidence.get("line")
                direct = (
                    finding.get("path") == path
                    and evidence.get("kind") == "git_blob"
                    and evidence.get("head_sha") == predecessor_head
                    and evidence.get("object_sha") == predecessor_head
                    and isinstance(evidence_line, int)
                    and not isinstance(evidence_line, bool)
                    and (
                        evidence_line == old_start
                        if old_count == 0
                        else old_start <= evidence_line <= old_start + old_count - 1
                    )
                )
                referenced = False
                if boundary_path(path):
                    tokens = {
                        finding.get("claim_key"),
                        evidence.get("locator"),
                        module_token(finding.get("path", "")),
                    }
                    referenced = any(isinstance(token, str) and token and token in body for token in tokens)
                if direct or referenced:
                    mapped.add(finding_index)
            if len(mapped) > 1:
                raise ParseError
            if len(mapped) != 1:
                unmapped = True
            hunk_capabilities = signal_capabilities(path, body)
            if hunk_capabilities:
                mapped_capabilities = set()
                if len(mapped) == 1:
                    mapped_capabilities = mapped_signal_capabilities(findings[next(iter(mapped))], receipt_capabilities)
                missing_capabilities = hunk_capabilities - mapped_capabilities
                if missing_capabilities:
                    capabilities.update(missing_capabilities)
                    unmapped = True
            file_hunks += 1
            hunk_count += 1
        if file_hunks == 0:
            raise ParseError

    if parsed_paths != set(statuses) or hunk_count == 0:
        raise ParseError
    classification = "delta" if unmapped else "resolve"
    print(json.dumps(
        {"classification": classification, "required_capabilities": sorted(capabilities)},
        sort_keys=True,
        separators=(",", ":"),
    ))
except (OSError, UnicodeError, ValueError, TypeError, KeyError, ParseError):
    print(json.dumps(malformed_result(), sort_keys=True, separators=(",", ":")))
PY
)


review_plan_route_delta() {
  local worktree="$1" predecessor_head="$2" head_sha="$3" receipt="$4"
  local changed status path extra classification
  changed="$(review_plan_changed_paths "$worktree" "$predecessor_head" "$head_sha")" || return 2
  [ -n "$changed" ] || return 2
  while IFS=$'\t' read -r status path extra; do
    case "$status" in A|M) ;; *) return 2 ;; esac
    review_plan_safe_path "$path" || return 2
    [ -z "$extra" ] || return 2
    review_plan_changed_object_is_safe "$worktree" "$predecessor_head" "$head_sha" "$path" || return 2
  done <<<"$changed"
  classification="$(review_plan_classify_hunks "$worktree" "$predecessor_head" "$head_sha" "$receipt" "$changed")" ||
    return 2
  printf '%s' "$classification" | jq -e '
    (keys | sort) == ["classification","required_capabilities"] and
    (.classification == "initial" or .classification == "delta" or .classification == "resolve") and
    (.required_capabilities | type == "array" and . == (sort | unique))
  ' >/dev/null 2>&1 || return 2
  printf '%s\n' "$classification"
}


review_plan_decide() (
  local repository="$1" pr_number="$2" base_sha="$3" head_sha="$4" config_hash="$5"
  local worktree="${6-}" event_file="${7-}" receipt_file="${8-}" config_file="${9-}"
  local snapshot_dir receipt_snapshot event_snapshot config_snapshot receipt predecessor_repository
  local predecessor_pr predecessor_base predecessor_head predecessor_config state_before state_after
  local route route_mode route_capabilities inherited_ids capabilities
  review_plan_input_identity_valid "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" ||
    return 2
  review_plan_source_runtime || return
  if [ "${KC_PR_FLOW_DELTA_FAST_PATH:-off}" != on ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" feature_disabled
    return
  fi
  if [ -z "$event_file" ] || [ -z "$receipt_file" ] || [ -z "$config_file" ] || [ -z "$worktree" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" missing_predecessor
    return
  fi
  worktree="$(review_plan_real_worktree "$worktree")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  snapshot_dir="$(review_runtime_private_snapshot_dir)" || return 74
  receipt_snapshot="$snapshot_dir/receipt.json"
  event_snapshot="$snapshot_dir/events.jsonl"
  config_snapshot="$snapshot_dir/config.json"
  trap 'review_runtime_remove_private_snapshot_dir "$snapshot_dir" "$receipt_snapshot" "$event_snapshot" "$config_snapshot"' EXIT
  review_plan_snapshot_inputs "$receipt_file" "$event_file" "$config_file" \
    "$receipt_snapshot" "$event_snapshot" "$config_snapshot" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  review_runtime_validate_delta_receipt_snapshots \
    "$receipt_snapshot" "$event_snapshot" "$config_snapshot" "$worktree" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  receipt="$(cat "$receipt_snapshot")" || return 74
  predecessor_repository="$(jq -r '.predecessor.repository' <<<"$receipt")" || return 3
  predecessor_pr="$(jq -r '.predecessor.pr_number' <<<"$receipt")" || return 3
  predecessor_base="$(jq -r '.predecessor.base_sha' <<<"$receipt")" || return 3
  predecessor_head="$(jq -r '.predecessor.head_sha' <<<"$receipt")" || return 3
  predecessor_config="$(jq -r '.predecessor.config_hash' <<<"$receipt")" || return 3
  if [ "$predecessor_repository" != "$repository" ] || [ "$predecessor_pr" != "$pr_number" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" identity_mismatch
    return
  fi
  if [ "$predecessor_base" != "$base_sha" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" base_changed
    return
  fi
  if [ "$predecessor_config" != "$config_hash" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" config_changed
    return
  fi
  state_before="$(review_plan_route_state "$worktree" "$base_sha" "$head_sha")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  if ! review_plan_ancestor "$worktree" "$base_sha" "$predecessor_head" ||
    ! review_plan_ancestor "$worktree" "$predecessor_head" "$head_sha"; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" non_ancestor
    return
  fi
  [ "$predecessor_head" != "$head_sha" ] || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  }
  route="$(review_plan_route_delta "$worktree" "$predecessor_head" "$head_sha" "$receipt")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  }
  state_after="$(review_plan_route_state "$worktree" "$base_sha" "$head_sha")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  }
  [ "$state_before" = "$state_after" ] || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  }
  route_mode="$(jq -r '.classification' <<<"$route")" || return 3
  [ "$route_mode" != initial ] || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  }
  inherited_ids="$(jq -S -c '[.known_findings[].finding_id] | sort | unique' <<<"$receipt")" || return 3
  capabilities="$(jq -S -c '.required_capabilities | sort | unique' <<<"$receipt")" || return 3
  if [ "$route_mode" = resolve ]; then
    review_plan_build_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" resolve \
      '["trusted_predecessor","ancestor_append","known_finding_delta"]' "\"$predecessor_head\"" \
      "$inherited_ids" "$capabilities" '"APPROVE"' false
    return
  fi
  route_capabilities="$(jq -S -c '.required_capabilities' <<<"$route")" || return 3
  capabilities="$(jq -S -c --argjson extra "$route_capabilities" \
    '. + ["code_correctness"] + $extra | sort | unique' <<<"$capabilities")" || return 3
  review_plan_build_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" delta \
    '["trusted_predecessor","ancestor_append","expanded_delta"]' "\"$predecessor_head\"" \
    "$inherited_ids" "$capabilities" '"COMMENT"' false
)

review_plan_validate_decision() {
  local decision="$1" repository="$2" pr_number="$3" base_sha="$4" head_sha="$5" config_hash="$6"
  local event_file="$7" receipt_file="$8" worktree="$9" config_file="${10}"
  local canonical mode expected
  [ "$#" -eq 10 ] || return 2
  review_plan_source_runtime || return
  review_runtime_json_has_unique_members "$decision" >/dev/null 2>&1 || return 3
  canonical="$(printf '%s' "$decision" | jq -S -c . 2>/dev/null)" || return 3
  [ "$canonical" = "$decision" ] || return 3
  printf '%s' "$canonical" | jq -e \
    --arg repository "$repository" --argjson pr_number "$pr_number" \
    --arg base "$base_sha" --arg head "$head_sha" --arg config "$config_hash" '
      def exact($keys): type == "object" and (keys | sort) == ($keys | sort);
      def sha1: type == "string" and test("^[0-9a-f]{40}$");
      def sha256: type == "string" and test("^[0-9a-f]{64}$");
      def token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
      exact(["event_ceiling","fallback","identity","inherited_finding_ids","mode",
        "reason_codes","required_capabilities","review_range","schema"]) and
      .schema == "kc-pr-flow.review-plan-decision/v1" and
      (.identity | exact(["base_sha","config_hash","head_sha","pr_number","repository","review_key"]) and
        .repository == $repository and .pr_number == $pr_number and .base_sha == $base and
        .head_sha == $head and .config_hash == $config and (.review_key | sha256)) and
      (.mode == "initial" or .mode == "delta" or .mode == "resolve") and
      (.reason_codes | type == "array" and length > 0 and all(token) and . == (sort | unique)) and
      (.inherited_finding_ids | type == "array" and all(sha256) and . == (sort | unique)) and
      (.required_capabilities | type == "array" and all(token) and . == (sort | unique)) and
      (.review_range | exact(["from_exclusive","to_inclusive"]) and .to_inclusive == $head and
        (.from_exclusive == null or (.from_exclusive | sha1))) and
      (.fallback | exact(["final_verdict_authority","requires_existing_initial_review","router_advisory"]) and
        .router_advisory == true and .final_verdict_authority == "existing-review-runtime") and
      (if .mode == "initial" then
        .event_ceiling == null and .review_range.from_exclusive == null and
        .inherited_finding_ids == [] and .required_capabilities == [] and
        .fallback.requires_existing_initial_review == true
       elif .mode == "delta" then
        .event_ceiling == "COMMENT" and .review_range.from_exclusive != null and
        .fallback.requires_existing_initial_review == false
       else
        .event_ceiling == "APPROVE" and .review_range.from_exclusive != null and
        .fallback.requires_existing_initial_review == false
       end)
    ' >/dev/null 2>&1 || return 3
  mode="$(jq -r '.mode' <<<"$canonical")" || return 3
  [ "$mode" != initial ] || return 0
  expected="$(KC_PR_FLOW_DELTA_FAST_PATH=on review_plan_decide "$repository" "$pr_number" \
    "$base_sha" "$head_sha" "$config_hash" "$worktree" "$event_file" "$receipt_file" "$config_file")" ||
    return 3
  [ "$expected" = "$canonical" ] || return 3
}

review_plan_event_allowed() {
  local decision="$1" requested_event="$2"
  shift 2
  [ "$#" -eq 9 ] || return 2
  case "$requested_event" in APPROVE|COMMENT|REQUEST_CHANGES) ;; *) return 3 ;; esac
  review_plan_validate_decision "$decision" "$@" || return 3
  case "$(jq -r '.event_ceiling' <<<"$decision"):$requested_event" in
    APPROVE:APPROVE|APPROVE:COMMENT|APPROVE:REQUEST_CHANGES|\
    COMMENT:COMMENT|COMMENT:REQUEST_CHANGES) return 0 ;;
    *) return 3 ;;
  esac
}

review_plan_main_decide() {
  local repository='' pr_number='' base_sha='' head_sha='' config_hash=''
  local config_file='' repository_path='' predecessor_events='' delta_receipt=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --repo|--pr|--base|--head|--config-hash|--config-file|--repo-worktree|--predecessor-events|--delta-receipt)
        [ "$#" -ge 2 ] || return 2
        case "$1" in
          --repo) repository="$2" ;;
          --pr) pr_number="$2" ;;
          --base) base_sha="$2" ;;
          --head) head_sha="$2" ;;
          --config-hash) config_hash="$2" ;;
          --config-file) config_file="$2" ;;
          --repo-worktree) repository_path="$2" ;;
          --predecessor-events) predecessor_events="$2" ;;
          --delta-receipt) delta_receipt="$2" ;;
        esac
        shift 2
        ;;
      *) return 2 ;;
    esac
  done
  [ -n "$repository" ] && [ -n "$pr_number" ] && [ -n "$base_sha" ] &&
    [ -n "$head_sha" ] && [ -n "$config_hash" ] || return 2
  review_plan_decide "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" \
    "$repository_path" "$predecessor_events" "$delta_receipt" "$config_file"
}

review_plan_main() {
  local command="${1:-}"
  [ "$#" -gt 0 ] && shift
  case "$command" in
    decide) review_plan_main_decide "$@" ;;
    *) printf 'usage: %s decide ...\n' "${0##*/}" >&2; return 2 ;;
  esac
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_plan_main "$@"
fi
