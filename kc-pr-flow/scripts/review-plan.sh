#!/usr/bin/env bash
# review-plan.sh — read-only exact-head planning for kc-pr-review.

review_plan_source_runtime() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 69
  # shellcheck source=/dev/null
  . "$here/review-runtime.sh" || return 69
}

review_plan_content_sha256() {
  jq -S -c 'del(.content_sha256)' | review_runtime_sha256
}

review_plan_required_capabilities() {
  jq -S -c '[.lanes[].capability] | sort | unique'
}

review_plan_build_receipt() (
  local event_file="$1" projection projection_hash receipt_id required_capabilities canonical content_sha256
  [ "$#" -eq 1 ] || return 2
  projection="$(review_runtime_replay "$event_file")" || return 3
  jq -e '
    .lifecycle.complete == true and
    (.lanes | length > 0) and
    (.lanes | all(.result.terminal_status == "succeeded")) and
    .uncertain_candidate_ids == []
  ' >/dev/null <<<"$projection" || return 3
  required_capabilities="$(printf '%s' "$projection" | review_plan_required_capabilities)" || return 3
  jq -e '
    type == "array" and length > 0 and
    all(type == "string" and test("^[a-z][a-z0-9._-]{0,63}$")) and
    . == (sort | unique)
  ' >/dev/null <<<"$required_capabilities" || return 3
  projection_hash="$(printf '%s' "$projection" | jq -S -c . | review_runtime_sha256)" || return
  receipt_id="$(printf '%s' "$(jq -r '.run.run_id + "|" + .run.review_key' <<<"$projection")|$projection_hash" |
    review_runtime_sha256)" || return
  canonical="$(jq -S -c --arg receipt_id "$receipt_id" --argjson required_capabilities "$required_capabilities" '
    .run as $run |
    {
      schema:"kc-pr-flow.review-delta-receipt/v1",
      predecessor:{
        repository:$run.repository,pr_number:$run.pr_number,
        base_sha:$run.base_sha,head_sha:$run.head_sha,
        config_hash:$run.config_hash,review_key:$run.review_key,
        run_id:$run.run_id,
        receipt_id:$receipt_id
      },
      known_findings:(.findings | map({
        finding_id,claim_key,anchor_sha256,category,evidence,
        evidence_sha256:.evidence.content_sha256,
        path,side,resolution_state:"unresolved"
      }) | sort_by(.finding_id)),
      required_capabilities:$required_capabilities,
      coverage_gap_refs:[]
    }' <<<"$projection")" || return 3
  jq -e '.required_capabilities | length > 0' >/dev/null <<<"$canonical" || return 3
  content_sha256="$(printf '%s' "$canonical" | review_runtime_sha256)" || return
  jq -S -c --arg hash "$content_sha256" '. + {content_sha256:$hash}' <<<"$canonical"
)

review_plan_validate_receipt() (
  local receipt='' event_file='' projection receipt_hash projection_hash expected_review_key expected_receipt_id expected_content_sha256
  local receipt_source projection_source
  [ "$#" -eq 2 ] || return 2
  receipt="$1"
  event_file="$2"
  receipt_source="$receipt"

  # Reject duplicate members before jq parses either value. A path argument is
  # accepted only when it is an ordinary file; callers normally pass JSON text.
  if [ -f "$receipt" ] && [ ! -L "$receipt" ]; then
    receipt_source="$(cat "$receipt")" || return 3
  fi
  review_runtime_json_has_unique_members "$receipt_source" >/dev/null 2>&1 || return 3
  # Freshness is part of this public boundary: callers provide only the event
  # file, and the projection is always rebuilt through review-runtime replay.
  projection="$(review_runtime_replay "$event_file")" || return 3
  projection_source="$projection"
  receipt_hash="$(printf '%s' "$receipt_source" | jq -S -c . 2>/dev/null)" || return 3
  projection_hash="$(printf '%s' "$projection_source" | jq -S -c . 2>/dev/null | review_runtime_sha256)" || return 3
  expected_review_key="$(printf '%s|%s|%s|%s|%s' \
    "$(jq -r '.run.repository' <<<"$projection_source")" \
    "$(jq -r '.run.pr_number' <<<"$projection_source")" \
    "$(jq -r '.run.base_sha' <<<"$projection_source")" \
    "$(jq -r '.run.head_sha' <<<"$projection_source")" \
    "$(jq -r '.run.config_hash' <<<"$projection_source")" | review_runtime_sha256)" || return
  expected_receipt_id="$(printf '%s' "$(jq -r '.run.run_id' <<<"$projection_source")|$expected_review_key|$projection_hash" |
    review_runtime_sha256)" || return
  # jq emits a line terminator; hash the canonical JSON value itself, matching
  # the producer's command-substitution boundary rather than that terminator.
  expected_content_sha256="$(printf '%s' "$receipt_hash" | jq -S -c 'del(.content_sha256)' 2>/dev/null)" || return 3
  expected_content_sha256="$(printf '%s' "$expected_content_sha256" | review_runtime_sha256)" || return

  jq -e -n \
    --argjson receipt "$receipt_source" \
    --argjson projection "$projection_source" \
    --arg expected_review_key "$expected_review_key" \
    --arg expected_receipt_id "$expected_receipt_id" \
    --arg expected_content_sha256 "$expected_content_sha256" \
    '
      def exact_keys($required):
        (type == "object" and (keys | sort) == ($required | sort));
      def sha256: type == "string" and test("^[0-9a-f]{64}$");
      def sha1: type == "string" and test("^[0-9a-f]{40}$");
      def token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
      def run_token: type == "string" and test("^run-[A-Za-z0-9._-]+$");
      def positive_integer:
        type == "number" and floor == . and . > 0 and . <= 9007199254740991;
      def safe_path:
        type == "string" and length > 0 and length <= 1024 and
        (startswith("/") | not) and (endswith("/") | not) and
        (contains("//") | not) and
        (test("(^|/)\\.\\.?(/|$)|[[:cntrl:]\\\\]") | not);
      def repository: type == "string" and test("^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$");
      def evidence_pointer:
        type == "object" and .schema == "kc-pr-flow.evidence-pointer/v1" and
        (.kind == "git_blob" or .kind == "pr_body" or .kind == "issue" or
          .kind == "review_comment" or .kind == "command" or .kind == "test") and
        (.repository | type == "string" and length > 0 and (test("[[:cntrl:]]") | not)) and
        (.review_key | sha256) and (.base_sha | sha1) and (.head_sha | sha1) and
        (.object_sha | sha1) and (.content_sha256 | sha256) and
        if .kind == "git_blob" then
          exact_keys(["base_sha","content_sha256","head_sha","kind","line","locator","object_sha","path","repository","review_key","schema","side"]) and
          (.path | safe_path) and (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
          (.line == null or (.line | positive_integer)) and
          (.locator == null or (.locator | token)) and
          (if .side == "LEFT" then .object_sha == .base_sha else .object_sha == .head_sha end)
        elif .kind == "pr_body" then
          exact_keys(["base_sha","content_sha256","head_sha","kind","locator","object_sha","pr_number","repository","review_key","schema"]) and
          (.pr_number | positive_integer) and (.locator | token)
        elif .kind == "issue" then
          exact_keys(["base_sha","content_sha256","head_sha","issue_number","kind","locator","object_sha","repository","review_key","schema"]) and
          (.issue_number | positive_integer) and (.locator | token)
        elif .kind == "review_comment" then
          exact_keys(["base_sha","comment_id","content_sha256","head_sha","kind","line","locator","object_sha","path","pr_number","repository","review_key","schema","side"]) and
          (.pr_number | positive_integer) and (.comment_id | positive_integer) and
          (.path | safe_path) and (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
          (.line == null or (.line | positive_integer)) and (.locator | token)
        else
          exact_keys(["base_sha","content_sha256","head_sha","kind","locator","object_sha","path","repository","review_key","schema"]) and
          (.path | safe_path) and (.locator | token)
        end;
      def identity:
        exact_keys(["base_sha","config_hash","head_sha","pr_number","receipt_id","repository","review_key","run_id"]) and
        (.repository | repository) and (.pr_number | positive_integer) and
        (.base_sha | sha1) and (.head_sha | sha1) and (.config_hash | sha256) and
        (.review_key | sha256) and (.run_id | run_token) and (.receipt_id | sha256);
      def projection_run:
        exact_keys(["base_sha","config_hash","head_sha","pr_number","repository","review_key","run_id","schema"]) and
        .schema == "kc-pr-flow.review-event/v1" and
        (.repository | repository) and (.pr_number | positive_integer) and
        (.base_sha | sha1) and (.head_sha | sha1) and (.config_hash | sha256) and
        (.review_key | sha256) and (.run_id | run_token);
      def projection_finding:
        type == "object" and
        ([.finding_id,.review_key,.anchor_sha256,.evidence.content_sha256] | all(sha256)) and
        (.claim_key | token) and (.category | token) and (.path | safe_path) and
        (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
        (.evidence | evidence_pointer);
      def projection_lane:
        type == "object" and
        exact_keys(["capability","lane_id","result","task"]) and
        (.capability | token) and (.lane_id | token);
      def projection:
        exact_keys(["behavior_hashes","candidates","findings","lanes","lifecycle","run","schema","uncertain_candidate_ids","usage_observations"]) and
        .schema == "kc-pr-flow.review-projection/v1" and
        (.run | projection_run) and
        (.lanes | type == "array" and length > 0 and all(projection_lane) and
          all(.result.terminal_status == "succeeded") and
          ([.[].capability] | . == (sort | unique))) and
        (.findings | type == "array" and all(projection_finding) and
          ([.[].finding_id] | . == (sort | unique))) and
        (.uncertain_candidate_ids == []) and
        (.lifecycle | type == "object" and .complete == true) and
        (.behavior_hashes | type == "object") and
        (.candidates | type == "array") and
        (.usage_observations | type == "array");
      def receipt_finding:
        type == "object" and
        exact_keys(["anchor_sha256","category","claim_key","evidence","evidence_sha256","finding_id","path","resolution_state","side"]) and
        (.finding_id | sha256) and (.anchor_sha256 | sha256) and
        (.category | token) and (.claim_key | token) and
        (.evidence_sha256 | sha256) and (.path | safe_path) and
        (.side == "LEFT" or .side == "RIGHT" or .side == "FILE") and
        (.evidence | evidence_pointer) and
        .evidence_sha256 == .evidence.content_sha256 and
        .resolution_state == "unresolved";
      ($projection | projection) and
      ($receipt | exact_keys(["content_sha256","coverage_gap_refs","known_findings","predecessor","required_capabilities","schema"])) and
      $receipt.schema == "kc-pr-flow.review-delta-receipt/v1" and
      ($receipt.content_sha256 == $expected_content_sha256) and
      ($receipt.predecessor | identity) and
      ($receipt.known_findings | type == "array" and all(receipt_finding) and
        ([.[].finding_id] | . == (sort | unique))) and
      ($receipt.required_capabilities | type == "array" and length > 0 and all(token) and
        . == (sort | unique)) and
      ($receipt.coverage_gap_refs | type == "array" and all(token) and
        . == (sort | unique)) and
      ($receipt.predecessor.review_key == $expected_review_key) and
      ($receipt.predecessor.receipt_id == $expected_receipt_id) and
      ([$receipt.predecessor.repository,$receipt.predecessor.pr_number,
        $receipt.predecessor.base_sha,$receipt.predecessor.head_sha,
        $receipt.predecessor.config_hash,$receipt.predecessor.review_key,
        $receipt.predecessor.run_id] ==
       [$projection.run.repository,$projection.run.pr_number,$projection.run.base_sha,
        $projection.run.head_sha,$projection.run.config_hash,$projection.run.review_key,
        $projection.run.run_id]) and
      ($receipt.coverage_gap_refs == []) and
      ($receipt.known_findings == ($projection.findings | map({
        finding_id,claim_key,anchor_sha256,category,evidence,
        evidence_sha256:.evidence.content_sha256,
        path,side,resolution_state:"unresolved"
      }) | sort_by(.finding_id))) and
      ($receipt.required_capabilities == ($projection.lanes | map(.capability) | sort | unique))
    ' >/dev/null 2>&1
)

review_plan_worktree_adapter() {
  python3 - "$@" <<'PY'
import json
import os
import stat
import sys


def open_directory(path):
    if not isinstance(path, str) or not os.path.isabs(path) or os.path.normpath(path) != path:
        raise OSError
    flags = os.O_RDONLY | os.O_DIRECTORY
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise OSError
    descriptor = os.open(os.sep, flags)
    try:
        for component in path.split(os.sep)[1:]:
            next_descriptor = os.open(component, flags | nofollow, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def closed_binding(value):
    if not isinstance(value, dict) or set(value) != {"device", "inode", "path"}:
        raise ValueError
    if not isinstance(value["path"], str):
        raise ValueError
    for key in ("device", "inode"):
        if not isinstance(value[key], int) or isinstance(value[key], bool) or value[key] < 0:
            raise ValueError
    return value


def after_open_test_barrier():
    ready = os.environ.get("KC_PR_FLOW_TEST_GIT_OPEN_READY_FD")
    proceed = os.environ.get("KC_PR_FLOW_TEST_GIT_OPEN_PROCEED_FD")
    if ready is None and proceed is None:
        return
    if ready is None or proceed is None or not ready.isdigit() or not proceed.isdigit():
        raise OSError
    ready_fd = int(ready)
    proceed_fd = int(proceed)
    if ready_fd < 3 or proceed_fd < 3:
        raise OSError
    os.write(ready_fd, b"opened\n")
    if not os.read(proceed_fd, 1):
        raise OSError


try:
    operation = sys.argv[1]
    if operation == "bind" and len(sys.argv) == 3:
        path = sys.argv[2]
        descriptor = open_directory(path)
        try:
            identity = os.fstat(descriptor)
            print(json.dumps(
                {"device": identity.st_dev, "inode": identity.st_ino, "path": path},
                sort_keys=True,
                separators=(",", ":"),
            ))
        finally:
            os.close(descriptor)
    elif operation == "git" and len(sys.argv) >= 4:
        binding = closed_binding(json.loads(sys.argv[2]))
        descriptor = open_directory(binding["path"])
        identity = os.fstat(descriptor)
        if (identity.st_dev, identity.st_ino) != (binding["device"], binding["inode"]):
            os.close(descriptor)
            raise OSError
        after_open_test_barrier()
        os.fchdir(descriptor)
        os.close(descriptor)
        os.execvp("git", ["git"] + sys.argv[3:])
    else:
        raise ValueError
except (IndexError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
    raise SystemExit(2)
PY
}

review_plan_worktree_binding() {
  review_plan_worktree_adapter bind "$1"
}

review_plan_real_worktree() {
  local binding
  binding="$(review_plan_worktree_binding "$1")" || return 2
  jq -r '.path' <<<"$binding"
}

review_plan_git() {
  local binding="$1"
  shift
  review_plan_worktree_adapter git "$binding" "$@"
}

review_plan_git_identity_valid() {
  local worktree="$1" object="$2"
  review_plan_git "$worktree" rev-parse --git-dir >/dev/null 2>&1 || return 1
  [ "$(review_plan_git "$worktree" cat-file -t "$object" 2>/dev/null)" = 'commit' ]
}

review_plan_ancestor() {
  review_plan_git "$1" merge-base --is-ancestor "$2" "$3"
}

review_plan_changed_paths() {
  review_plan_git "$1" diff --name-status --find-renames=50% --find-copies=50% --find-copies-harder "$2..$3"
}

review_plan_changed_diff() {
  review_plan_git "$1" diff --unified=0 --no-ext-diff --no-textconv --no-renames --no-color "$2..$3"
}

review_plan_changed_object_is_safe() {
  local worktree="$1" base_sha="$2" head_sha="$3" path="$4"
  local tree_entry entry_path extra mode type object numstat added removed numstat_path
  tree_entry="$(review_plan_git "$worktree" ls-tree "$head_sha" -- "$path")" || return 1
  [ -n "$tree_entry" ] || return 1
  IFS=$'\t' read -r tree_entry entry_path extra <<<"$tree_entry"
  [ -z "$extra" ] && [ "$entry_path" = "$path" ] || return 1
  read -r mode type object <<<"$tree_entry"
  case "$mode:$type" in
    100644:blob|100755:blob) ;;
    *) return 1 ;;
  esac
  numstat="$(review_plan_git "$worktree" diff --numstat "$base_sha..$head_sha" -- "$path")" || return 1
  [ -n "$numstat" ] || return 1
  IFS=$'\t' read -r added removed numstat_path extra <<<"$numstat"
  [ -z "$extra" ] && [ "$numstat_path" = "$path" ] || return 1
  [ "$added" != '-' ] && [ "$removed" != '-' ]
}

review_plan_safe_path() {
  local path="$1"
  [ -n "$path" ] || return 1
  case "$path" in
    /*|*/|*'//'*) return 1 ;;
  esac
  case "/$path/" in
    *'/./'*|*'/../'*) return 1 ;;
  esac
  [[ "$path" != *$'\n'* && "$path" != *$'\r'* && "$path" != *\\* ]]
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
    case "$status" in
      A|M) ;;
      *) return 2 ;;
    esac
    review_plan_safe_path "$path" || return 2
    [ -z "$extra" ] || return 2
    review_plan_changed_object_is_safe "$worktree" "$predecessor_head" "$head_sha" "$path" || return 2
  done <<<"$changed"
  classification="$(review_plan_classify_hunks "$worktree" "$predecessor_head" "$head_sha" "$receipt" "$changed")" || return 2
  jq -e '
    type == "object" and
    (keys | sort) == ["classification","required_capabilities"] and
    (.classification == "initial" or .classification == "delta" or .classification == "resolve") and
    (.required_capabilities | type == "array" and all(type == "string" and test("^[a-z][a-z0-9._-]{0,63}$")) and
      . == (sort | unique)) and
    (if .classification == "resolve" then .required_capabilities == [] else true end)
  ' >/dev/null 2>&1 <<<"$classification" || return 2
  printf '%s\n' "$classification"
}

review_plan_input_identity_valid() {
  jq -e -n --arg repository "$1" --arg pr_number "$2" --arg base_sha "$3" --arg head_sha "$4" --arg config_hash "$5" '
    ($repository | test("^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")) and
    ($pr_number | test("^[1-9][0-9]*$")) and
    ($base_sha | test("^[0-9a-f]{40}$")) and
    ($head_sha | test("^[0-9a-f]{40}$")) and
    ($config_hash | test("^[0-9a-f]{64}$"))
  ' >/dev/null 2>&1
}

# This shared adapter boundary validates a closed decision before a skill reads
# any field from it. It is deliberately mechanical: routing cannot decide a
# finding, verdict, or posting authority.
review_plan_validate_decision() {
  local decision="$1" repository="$2" pr_number="$3" base_sha="$4" head_sha="$5" config_hash="$6"
  local predecessor_events="$7" delta_receipt="$8" worktree="$9"
  local expected_review_key mode receipt_source predecessor_head inherited_finding_ids
  local receipt_capabilities expected_capabilities route route_mode route_capabilities worktree_binding
  [ "$#" -eq 9 ] || return 2
  review_plan_source_runtime || return
  review_plan_input_identity_valid "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" || return 3
  review_runtime_json_has_unique_members "$decision" >/dev/null 2>&1 || return 3
  expected_review_key="$(printf '%s|%s|%s|%s|%s' "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" |
    review_runtime_sha256)" || return
  jq -e -n \
    --argjson decision "$decision" --arg repository "$repository" --argjson pr_number "$pr_number" \
    --arg base_sha "$base_sha" --arg head_sha "$head_sha" --arg config_hash "$config_hash" \
    --arg review_key "$expected_review_key" '
      def exact_keys($required): type == "object" and (keys | sort) == ($required | sort);
      def sha256: type == "string" and test("^[0-9a-f]{64}$");
      def sha1: type == "string" and test("^[0-9a-f]{40}$");
      def token: type == "string" and test("^[a-z][a-z0-9._-]{0,63}$");
      def sorted_unique_sha256:
        type == "array" and all(.[]; sha256) and . == (sort | unique);
      def sorted_unique_tokens:
        type == "array" and all(.[]; token) and . == (sort | unique);
      def identity:
        exact_keys(["base_sha","config_hash","head_sha","pr_number","repository","review_key"]) and
        .repository == $repository and .pr_number == $pr_number and .base_sha == $base_sha and
        .head_sha == $head_sha and .config_hash == $config_hash and .review_key == $review_key;
      def review_range:
        exact_keys(["from_exclusive","to_inclusive"]) and .to_inclusive == $head_sha and
        (.from_exclusive == null or (.from_exclusive | sha1));
      def fallback:
        exact_keys(["final_verdict_authority","requires_existing_initial_review","router_advisory"]) and
        .router_advisory == true and
        (.requires_existing_initial_review | type == "boolean") and
        .final_verdict_authority == "existing-review-runtime";
      def initial_reason:
        . == ["base_changed"] or . == ["config_changed"] or
        . == ["feature_disabled"] or . == ["identity_mismatch"] or
        . == ["invalid_predecessor"] or . == ["missing_predecessor"] or
        . == ["non_ancestor"] or . == ["unknown_delta"];
      ($decision | exact_keys(["event_ceiling","fallback","identity","inherited_finding_ids","mode","reason_codes","required_capabilities","review_range","schema"])) and
      $decision.schema == "kc-pr-flow.review-plan-decision/v1" and
      ($decision.identity | identity) and
      ($decision.mode == "initial" or $decision.mode == "delta" or $decision.mode == "resolve") and
      ($decision.reason_codes | type == "array" and length > 0 and all(token) and . == (sort | unique)) and
      ($decision.review_range | review_range) and
      ($decision.inherited_finding_ids | sorted_unique_sha256) and
      ($decision.required_capabilities | sorted_unique_tokens) and
      ($decision.event_ceiling == null or $decision.event_ceiling == "APPROVE" or $decision.event_ceiling == "COMMENT") and
      ($decision.fallback | fallback) and
      (if $decision.mode == "initial" then
        $decision.review_range.from_exclusive == null and
        $decision.inherited_finding_ids == [] and
        $decision.required_capabilities == [] and
        $decision.event_ceiling == null and
        $decision.fallback.requires_existing_initial_review == true and
        ($decision.reason_codes | initial_reason)
      else
        ($decision.review_range.from_exclusive | sha1) and
        $decision.review_range.from_exclusive != $head_sha and
        $decision.fallback.requires_existing_initial_review == false
      end)
    ' >/dev/null 2>&1 || return

  mode="$(jq -r '.mode' <<<"$decision")" || return
  [ "$mode" = 'initial' ] && return 0

  worktree_binding="$(review_plan_worktree_binding "$worktree")" || return
  worktree="$worktree_binding"

  receipt_source="$(review_plan_snapshot_receipt "$delta_receipt")" || return
  review_plan_validate_receipt "$receipt_source" "$predecessor_events" || return 3
  jq -e -n \
    --argjson receipt "$receipt_source" --arg repository "$repository" --argjson pr_number "$pr_number" \
    --arg base_sha "$base_sha" --arg config_hash "$config_hash" '
      $receipt.predecessor.repository == $repository and
      $receipt.predecessor.pr_number == $pr_number and
      $receipt.predecessor.base_sha == $base_sha and
      $receipt.predecessor.config_hash == $config_hash
    ' >/dev/null 2>&1 || return 3
  predecessor_head="$(jq -r '.predecessor.head_sha' <<<"$receipt_source")" || return
  review_plan_git_identity_valid "$worktree" "$predecessor_head" || return
  review_plan_git_identity_valid "$worktree" "$head_sha" || return
  review_plan_ancestor "$worktree" "$predecessor_head" "$head_sha" || return
  [ "$predecessor_head" != "$head_sha" ] || return 3
  route="$(review_plan_route_delta "$worktree" "$predecessor_head" "$head_sha" "$receipt_source")" || return
  route_mode="$(jq -r '.classification' <<<"$route")" || return
  route_capabilities="$(jq -S -c '.required_capabilities' <<<"$route")" || return
  [ "$route_mode" = "$mode" ] || return 3
  inherited_finding_ids="$(jq -S -c '[.known_findings[].finding_id] | sort | unique' <<<"$receipt_source")" || return
  receipt_capabilities="$(jq -S -c '.required_capabilities | sort | unique' <<<"$receipt_source")" || return
  expected_capabilities="$receipt_capabilities"
  if [ "$mode" = 'delta' ]; then
    expected_capabilities="$(jq -S -c --argjson route_capabilities "$route_capabilities" \
      '. + ["correctness"] + $route_capabilities | sort | unique' <<<"$receipt_capabilities")" || return
  fi
  jq -e -n \
    --argjson decision "$decision" --arg predecessor_head "$predecessor_head" \
    --argjson inherited_finding_ids "$inherited_finding_ids" --argjson expected_capabilities "$expected_capabilities" '
      ($decision.review_range.from_exclusive == $predecessor_head) and
      ($decision.inherited_finding_ids == $inherited_finding_ids) and
      ($decision.required_capabilities == $expected_capabilities) and
      (if $decision.mode == "resolve" then
        $decision.reason_codes == ["ancestor_append","known_finding_delta","trusted_predecessor"] and
        $decision.event_ceiling == "APPROVE"
      elif $decision.mode == "delta" then
        $decision.reason_codes == ["ancestor_append","expanded_delta","trusted_predecessor"] and
        $decision.event_ceiling == "COMMENT"
      else false end)
    ' >/dev/null 2>&1
}

review_plan_build_decision() {
  local repository="$1" pr_number="$2" base_sha="$3" head_sha="$4" config_hash="$5"
  local mode="$6" reason_codes="$7" from_exclusive="$8" inherited_finding_ids="$9"
  local required_capabilities="${10}" event_ceiling="${11}" full_initial="${12}" review_key fallback
  review_key="$(printf '%s|%s|%s|%s|%s' "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" |
    review_runtime_sha256)" || return
  fallback="$(jq -S -c -n --argjson full_initial "$full_initial" \
    '{router_advisory:true,requires_existing_initial_review:$full_initial,final_verdict_authority:"existing-review-runtime"}')" || return
  jq -S -c -n \
    --arg repository "$repository" --argjson pr_number "$pr_number" --arg base_sha "$base_sha" \
    --arg head_sha "$head_sha" --arg config_hash "$config_hash" --arg review_key "$review_key" \
    --arg mode "$mode" --argjson reason_codes "$reason_codes" --argjson from_exclusive "$from_exclusive" \
    --argjson inherited_finding_ids "$inherited_finding_ids" --argjson required_capabilities "$required_capabilities" \
    --argjson event_ceiling "$event_ceiling" --argjson fallback "$fallback" \
    '{schema:"kc-pr-flow.review-plan-decision/v1",
      identity:{repository:$repository,pr_number:$pr_number,base_sha:$base_sha,head_sha:$head_sha,
        config_hash:$config_hash,review_key:$review_key},
      mode:$mode,
      reason_codes:($reason_codes | sort | unique),
      review_range:{from_exclusive:$from_exclusive,to_inclusive:$head_sha},
      inherited_finding_ids:($inherited_finding_ids | sort | unique),
      required_capabilities:($required_capabilities | sort | unique),
      event_ceiling:$event_ceiling,
      fallback:$fallback}'
}

review_plan_initial_decision() {
  review_plan_build_decision "$1" "$2" "$3" "$4" "$5" initial "[\"$6\"]" null '[]' '[]' null true
}

review_plan_snapshot_receipt() (
  local receipt="$1" snapshot_dir='' snapshot_file=''
  if [ -e "$receipt" ] || [ -L "$receipt" ]; then
    snapshot_dir="$(review_runtime_private_snapshot_dir)" || return
    snapshot_file="$snapshot_dir/receipt.json"
    trap 'review_runtime_remove_private_snapshot_dir "$snapshot_dir" "$snapshot_file"' EXIT
    review_runtime_snapshot_regular_file "$receipt" "$snapshot_file" 'delta receipt' "${KC_PR_FLOW_MAX_RECEIPT_BYTES:-1048576}" || return
    cat "$snapshot_file"
  else
    printf '%s' "$receipt"
  fi
)

review_plan_decide() {
  local repository="$1" pr_number="$2" base_sha="$3" head_sha="$4" config_hash="$5"
  local worktree="$6" predecessor_events="$7" delta_receipt="$8" receipt_source predecessor_repository predecessor_pr
  local predecessor_base predecessor_head predecessor_config route route_mode route_capabilities
  local inherited_finding_ids required_capabilities worktree_binding

  review_plan_input_identity_valid "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" || return 2
  if [ "${KC_PR_FLOW_DELTA_FAST_PATH:-off}" != 'on' ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" feature_disabled
    return
  fi
  if [ -z "$predecessor_events" ] || [ -z "$delta_receipt" ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" missing_predecessor
    return
  fi
  worktree_binding="$(review_plan_worktree_binding "$worktree")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  worktree="$worktree_binding"
  receipt_source="$(review_plan_snapshot_receipt "$delta_receipt")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  review_plan_validate_receipt "$receipt_source" "$predecessor_events" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  }
  predecessor_repository="$(jq -r '.predecessor.repository' <<<"$receipt_source")" || return 3
  predecessor_pr="$(jq -r '.predecessor.pr_number' <<<"$receipt_source")" || return 3
  predecessor_base="$(jq -r '.predecessor.base_sha' <<<"$receipt_source")" || return 3
  predecessor_head="$(jq -r '.predecessor.head_sha' <<<"$receipt_source")" || return 3
  predecessor_config="$(jq -r '.predecessor.config_hash' <<<"$receipt_source")" || return 3
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
  if ! review_plan_git_identity_valid "$worktree" "$base_sha" ||
    ! review_plan_git_identity_valid "$worktree" "$predecessor_head" ||
    ! review_plan_git_identity_valid "$worktree" "$head_sha"; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" invalid_predecessor
    return
  fi
  if ! review_plan_ancestor "$worktree" "$predecessor_head" "$head_sha"; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" non_ancestor
    return
  fi
  route="$(review_plan_route_delta "$worktree" "$predecessor_head" "$head_sha" "$receipt_source")" || {
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  }
  route_mode="$(jq -r '.classification' <<<"$route")" || return 3
  route_capabilities="$(jq -S -c '.required_capabilities' <<<"$route")" || return 3
  if [ "$route_mode" = 'initial' ]; then
    review_plan_initial_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" unknown_delta
    return
  fi
  inherited_finding_ids="$(jq -S -c '[.known_findings[].finding_id] | sort | unique' <<<"$receipt_source")" || return 3
  required_capabilities="$(jq -S -c '.required_capabilities | sort | unique' <<<"$receipt_source")" || return 3
  if [ "$route_mode" = 'resolve' ]; then
    review_plan_build_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" resolve \
      '["trusted_predecessor","ancestor_append","known_finding_delta"]' "\"$predecessor_head\"" \
      "$inherited_finding_ids" "$required_capabilities" '"APPROVE"' false
    return
  fi
  required_capabilities="$(jq -S -c --argjson route_capabilities "$route_capabilities" \
    '. + ["correctness"] + $route_capabilities | sort | unique' <<<"$required_capabilities")" || return 3
  review_plan_build_decision "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" delta \
    '["trusted_predecessor","ancestor_append","expanded_delta"]' "\"$predecessor_head\"" \
    "$inherited_finding_ids" "$required_capabilities" '"COMMENT"' false
}

review_plan_usage() {
  printf 'usage: %s receipt --event-file FILE\n' "${0##*/}" >&2
  printf '       %s decide ...\n' "${0##*/}" >&2
}

review_plan_main_receipt() {
  local event_file=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --event-file)
        [ "$#" -ge 2 ] || { printf 'review-plan: missing value for --event-file\n' >&2; return 2; }
        event_file="$2"
        shift 2
        ;;
      *)
        printf 'review-plan: unknown receipt option: %s\n' "$1" >&2
        return 2
        ;;
    esac
  done
  [ -n "$event_file" ] || { printf 'review-plan: --event-file is required\n' >&2; return 2; }
  review_plan_build_receipt "$event_file"
}

review_plan_main_decide() {
  local repository='' pr_number='' base_sha='' head_sha='' config_hash='' worktree=''
  local predecessor_events='' delta_receipt=''
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --repo|--pr|--base|--head|--config-hash|--repo-worktree|--predecessor-events|--delta-receipt)
        [ "$#" -ge 2 ] || { printf 'review-plan: missing value for %s\n' "$1" >&2; return 2; }
        case "$1" in
          --repo) repository="$2" ;;
          --pr) pr_number="$2" ;;
          --base) base_sha="$2" ;;
          --head) head_sha="$2" ;;
          --config-hash) config_hash="$2" ;;
          --repo-worktree) worktree="$2" ;;
          --predecessor-events) predecessor_events="$2" ;;
          --delta-receipt) delta_receipt="$2" ;;
        esac
        shift 2
        ;;
      *) printf 'review-plan: unknown decide option: %s\n' "$1" >&2; return 2 ;;
    esac
  done
  [ -n "$repository" ] && [ -n "$pr_number" ] && [ -n "$base_sha" ] && [ -n "$head_sha" ] &&
    [ -n "$config_hash" ] && [ -n "$worktree" ] || {
    printf 'review-plan: --repo, --pr, --base, --head, --config-hash, and --repo-worktree are required\n' >&2
    return 2
  }
  review_plan_decide "$repository" "$pr_number" "$base_sha" "$head_sha" "$config_hash" "$worktree" \
    "$predecessor_events" "$delta_receipt"
}

review_plan_main() {
  local command="${1:-}"
  [ "$#" -gt 0 ] && shift
  case "$command" in
    receipt) review_plan_main_receipt "$@" ;;
    decide) review_plan_main_decide "$@" ;;
    *) review_plan_usage; return 2 ;;
  esac
}

review_plan_source_runtime || return 69 2>/dev/null || exit 69
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_plan_main "$@"
fi
