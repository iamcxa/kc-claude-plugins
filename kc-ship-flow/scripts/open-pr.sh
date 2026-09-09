#!/usr/bin/env bash
# Open a Draft PR from a worker's accepted Evidence block, body per the
# pr-merge mod's PR body template (docs/dev/_mods/pr-merge.md § PR body
# template, "Extraction rules").
# Usage: open-pr.sh <evidence-file> <batch-dir> [--dry-run]
#                    (--entity-path <dev-entity-file> | --what-changed-file <file>)
#                    [--lead <file>] [--evidence-file <file>]
#
# <batch-dir> is a batch record directory: <batch-dir>/README.md (entity id
# is the directory's own basename, `batch-` prefix stripped) and
# <batch-dir>/receipt/plan-receipt.json (its `issues` map -- matched to the
# Evidence block's BRANCH for `close_line`, always, in both modes below).
# The audit link's owner/repo, ref, and path all come from the batch-dir's
# own git checkout (origin remote, current branch, `git ls-files`), never
# from CANDIDATE_SHA or cwd's repository.
#
# --entity-path <file> reads a dev entity (the same shape
# `kc-ship-flow/scripts/fenced-dispatch.sh` dispatches): the lead is the
# entity's own `## The problem` first sentence (skipping a leading sentence
# that is only a quoted attribution, e.g. `Captain, <date>: 「...」.`);
# `## What changed` is one bullet per `- [x] ...` item in the last
# `## Stage Report: implementation` section (`[x]` dropped, duplicates
# collapsed); `## Evidence` is one bullet per suite- or runner-labeled
# `N/N` or `exit 0` token found in the last `## Stage Report: validation`
# section -- a bare data/fixture path is never a suite.
#
# Without --entity-path, --what-changed-file <file> supplies the `## What
# changed` bullets verbatim (one per non-empty line, FO-authored); the lead
# comes from the matched batch-receipt issue's `body`'s `## The problem`
# (same rule); `## Evidence` is derived by the same suite/runner scan
# applied to the Evidence block's own TESTS field -- never a count of ACs.
#
# Neither flag given refuses (exit 2, `what-changed required`).
#
# The lead is never a fragment: a first sentence over 25 words is closed at
# the longest clause boundary (`,` `;` `—` `:`) within the first 25 words,
# period-terminated; with no such boundary, `--lead <file>` (one sentence)
# supplies it, else the run refuses (exit 2, `lead required`).
#
# `## Evidence` bullets are admitted only for a token naming a recognized
# suite or test runner (`contract-test.py`, `*.test.sh`, `*.test.py`,
# `*.test.mjs`, `npm test`, `npm run test:*`, `pytest`, `vitest`,
# `node --test`) followed by `N/N passed` or `exit 0`; when no such token is
# found the section is omitted unless `--evidence-file <file>` supplies
# bullets verbatim (one per line).
#
# --dry-run prints the body to stdout and exits 0 without resolving
# CANDIDATE_SHA, binding BRANCH to origin, or calling gh. Every other exit
# path is unchanged from non-dry-run.
#
# Exit codes: 0 PR opened (number on stdout), or --dry-run body printed; 2
# every other exit path -- a usage error; an evidence, batch-dir,
# --entity-path, --what-changed-file, --lead, or --evidence-file argument
# that does not exist; neither --entity-path nor --what-changed-file given;
# an evidence file with no `## Evidence` heading or more than one; an
# Evidence block missing a required field; a BRANCH containing `:` (fork
# syntax); a batch-dir README.md untracked by its own checkout; a batch
# receipt missing or with zero or more than one issue whose `branch` equals
# BRANCH; a first sentence over 25 words with no clause boundary and no
# `--lead` override (`lead required`); an unreachable CANDIDATE_SHA; a
# BRANCH that resolves to zero or more than one ref on origin; a BRANCH
# whose remote head does not equal CANDIDATE_SHA; a `gh pr create` failure;
# or a PR number that cannot be parsed from `gh pr create`'s stdout.
set -euo pipefail

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
log() { echo "$(timestamp) open-pr: $*" >&2; }
die() { log "$*"; exit 2; }

usage() {
  echo "usage: open-pr.sh <evidence-file> <batch-dir> [--dry-run] (--entity-path <file> | --what-changed-file <file>) [--lead <file>] [--evidence-file <file>]" >&2
  exit 2
}

dry_run=0
entity_path=""
what_changed_path=""
lead_path=""
evidence_path=""
args=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      dry_run=1
      shift
      ;;
    --entity-path)
      [ "$#" -ge 2 ] || usage
      entity_path="$2"
      shift 2
      ;;
    --what-changed-file)
      [ "$#" -ge 2 ] || usage
      what_changed_path="$2"
      shift 2
      ;;
    --lead)
      [ "$#" -ge 2 ] || usage
      lead_path="$2"
      shift 2
      ;;
    --evidence-file)
      [ "$#" -ge 2 ] || usage
      evidence_path="$2"
      shift 2
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done
[ "${#args[@]}" -eq 2 ] || usage
evidence_file="${args[0]}"
batch_dir="${args[1]}"

[ -f "$evidence_file" ] || die "evidence file not found: $evidence_file"
[ -d "$batch_dir" ] || die "batch dir not found: $batch_dir"

repo_root="$(git rev-parse --show-toplevel)"

heading_count="$(grep -c '^## Evidence$' "$evidence_file" || true)"
[ "$heading_count" -le 1 ] || die "evidence file has $heading_count '## Evidence' headings, expected at most 1: $evidence_file"

parse_evidence() {
  sed -n '/^## Evidence$/,/^$/p' "$evidence_file"
}

get_field() {
  local key="$1"
  echo "$evidence_text" | grep "^${key}:" | head -1 | sed "s/^${key}: *//" || true
}

evidence_text="$(parse_evidence)"
[ -n "$evidence_text" ] || die "no Evidence block found in $evidence_file"

CANDIDATE_SHA="$(get_field CANDIDATE_SHA)"
BASE_SHA="$(get_field BASE_SHA)"
BRANCH="$(get_field BRANCH)"
TESTS="$(get_field TESTS)"
WITHOUT_IT_COMMAND="$(get_field WITHOUT_IT_COMMAND)"
WITHOUT_IT_REMOVED_VARIANT="$(get_field WITHOUT_IT_REMOVED_VARIANT)"
SELF_CHECK="$(get_field SELF_CHECK)"

for field_name in CANDIDATE_SHA BASE_SHA BRANCH WITHOUT_IT_COMMAND WITHOUT_IT_REMOVED_VARIANT SELF_CHECK; do
  [ -n "${!field_name}" ] || die "incomplete Evidence block: missing $field_name"
done

# Refuse cheap, string-only shapes before any git object lookup: a shallow
# clone (CI's actions/checkout@v4 default depth 1) may not have CANDIDATE_SHA
# as a local object, so the fork-syntax refusal below must fire first and for
# its own reason, not be masked by a SHA-lookup failure. `gh pr create --head`
# accepts `user:branch` fork syntax; refuse it outright.
case "$BRANCH" in
  *:*) die "BRANCH contains ':' (fork syntax refused): $BRANCH" ;;
esac

if [ -z "$entity_path" ] && [ -z "$what_changed_path" ]; then
  die "what-changed required: pass --entity-path <dev-entity-file> or --what-changed-file <file>"
fi
[ -z "$entity_path" ] || [ -f "$entity_path" ] || die "entity file not found: $entity_path"
[ -z "$what_changed_path" ] || [ -f "$what_changed_path" ] || die "what-changed file not found: $what_changed_path"
[ -z "$lead_path" ] || [ -f "$lead_path" ] || die "lead file not found: $lead_path"
[ -z "$evidence_path" ] || [ -f "$evidence_path" ] || die "evidence file not found: $evidence_path"

# --- resolve the batch entity from batch-dir's own git checkout ---
batch_readme_relpath="$(git -C "$batch_dir" ls-files --full-name -- README.md)"
[ -n "$batch_readme_relpath" ] || die "batch-dir README.md is untracked by its own checkout: $batch_dir"
batch_origin_url="$(git -C "$batch_dir" remote get-url origin)"
batch_owner_repo="$(printf '%s\n' "$batch_origin_url" | sed -E 's#\.git$##; s#^git@[^:]+:##; s#^https?://[^/]+/##')"
batch_ref="$(git -C "$batch_dir" rev-parse --abbrev-ref HEAD)"
batch_entity_id="$(basename "$batch_dir")"
case "$batch_entity_id" in batch-*) batch_entity_id="${batch_entity_id#batch-}" ;; esac

plan_receipt="$batch_dir/receipt/plan-receipt.json"
[ -f "$plan_receipt" ] || die "batch receipt not found: $plan_receipt"

# --- match BRANCH to exactly one issue in the batch receipt (its close_line
# and, in --what-changed-file mode, its body's "## The problem" feed the
# body below), then build the pr-merge-shaped body ---
body_tmp="$(mktemp)"
body_err_tmp="$(mktemp)"
trap 'rm -f "$body_tmp" "$body_err_tmp"' EXIT
set +e
python3 - "$plan_receipt" "$BRANCH" "$batch_owner_repo" "$batch_ref" "$batch_readme_relpath" "$batch_entity_id" "$TESTS" "$entity_path" "$what_changed_path" "$lead_path" "$evidence_path" \
  >"$body_tmp" 2>"$body_err_tmp" <<'PY'
import re
import json
import sys

(receipt_path, branch, owner_repo, ref, readme_path, entity_id,
 tests_field, entity_path, what_changed_path, lead_path, evidence_path) = sys.argv[1:12]

with open(receipt_path, encoding="utf-8") as f:
    receipt = json.load(f)

matches = [v for v in receipt.get("issues", {}).values() if v.get("branch") == branch]
if len(matches) != 1:
    print(
        f"{len(matches)} issues in {receipt_path} match BRANCH {branch}, expected exactly 1",
        file=sys.stderr,
    )
    sys.exit(1)
issue = matches[0]

CLAUSE_BOUNDARIES = ",;—:"
TRAILING_WRAPPERS = "'\"」”)]"


def is_quote_only(sentence: str) -> bool:
    # A "Speaker, date: 「quoted text」." sentence -- strip the attribution,
    # then require what remains to be fully wrapped in one matched quote
    # pair (plus only trailing punctuation).
    s = re.sub(r"^[^:\n]{1,60}:\s*", "", sentence.strip())
    for open_q, close_q in (("「", "」"), ("“", "”"), ('"', '"'), ("'", "'")):
        if s.startswith(open_q):
            rest = s[len(open_q):]
            close_idx = rest.rfind(close_q)
            if close_idx != -1 and rest[close_idx + len(close_q):].strip(" .!?") == "":
                return True
    return False


def close_at_clause_boundary(sentence: str):
    # The longest prefix of `sentence` that ends at a clause boundary (`,`
    # `;` an em dash `:`) within the first 25 words, closed with a period.
    # None when no such boundary exists -- never a mid-sentence fragment.
    words = sentence.split()
    limit = min(25, len(words))
    best_idx = None
    for i in range(limit):
        stripped = words[i].rstrip(TRAILING_WRAPPERS)
        if stripped and stripped[-1] in CLAUSE_BOUNDARIES:
            best_idx = i
    if best_idx is None:
        return None
    prefix_words = words[: best_idx + 1]
    last = prefix_words[-1]
    m = re.match(r"^(.*?)[" + CLAUSE_BOUNDARIES + r"]+[" + TRAILING_WRAPPERS + r"]*$", last)
    core = m.group(1) if m else last.rstrip(CLAUSE_BOUNDARIES)
    prefix_words[-1] = core
    return " ".join(prefix_words).rstrip() + "."


def lead_from_problem(body_text: str, lead_override: str):
    m = re.search(r"##\s*The problem\s*\n+(.*?)(?:\n\s*\n|\n##|\Z)", body_text, re.S)
    para = (m.group(1) if m else body_text).strip()
    para = re.sub(r"\s+", " ", para)
    if not para:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", para)
    start = 0
    while start < len(sentences) and is_quote_only(sentences[start]):
        start += 1
    # Exactly the first (non-quote) sentence -- never several joined.
    sentence = sentences[start] if start < len(sentences) else para
    if len(sentence.split()) <= 25:
        return sentence
    cut = close_at_clause_boundary(sentence)
    if cut is not None:
        return cut
    return lead_override or None


def last_section(body_text: str, heading_prefix: str) -> str:
    # The last `## <heading_prefix>...` section (covers a trailing "(cycle
    # N)"), body up to the next `## ` heading or end of text -- the most
    # recent report reflects the entity's final state.
    pattern = re.compile(
        r"^##\s*" + re.escape(heading_prefix) + r".*?\n(.*?)(?=\n##\s|\Z)",
        re.S | re.M,
    )
    found = pattern.findall(body_text)
    return found[-1] if found else ""


def what_changed_from_entity(body_text: str) -> list[str]:
    section = last_section(body_text, "Stage Report: implementation")
    bullets: list[str] = []
    for line in section.splitlines():
        m = re.match(r"^-\s*\[x\]\s*(.+)$", line.strip(), re.I)
        if m:
            text = m.group(1).strip()
            if text not in bullets:
                bullets.append(text)
    return bullets[:5]


# A bullet is admitted only for a token naming a recognized suite or test
# runner -- a bare data/fixture path (e.g. a synthetic evidence.md) is never
# a suite, however path-like or however close to an "N/N"/"exit 0" token.
SUITE_PATTERNS = [
    re.compile(r"\S*\bcontract-test\.py\b"),
    re.compile(r"\S*\.test\.sh\b"),
    re.compile(r"\S*\.test\.py\b"),
    re.compile(r"\S*\.test\.mjs\b"),
    re.compile(r"\bnpm test\b"),
    re.compile(r"\bnpm run test:\S*"),
    re.compile(r"\bpytest\b"),
    re.compile(r"\bvitest\b"),
    re.compile(r"\bnode --test\b"),
]


def find_suite(prefix: str):
    best = None
    best_end = -1
    for pattern in SUITE_PATTERNS:
        for m in pattern.finditer(prefix):
            if m.end() > best_end:
                best_end = m.end()
                best = m.group(0)
    return best


def suite_bullets_from_text(text: str) -> list[str]:
    bullets: list[str] = []
    seen: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        ratio_m = re.search(r"\d+/\d+", line)
        exit0_m = None if ratio_m else re.search(r"\bexit 0\b", line)
        marker = ratio_m or exit0_m
        if not marker:
            continue
        suite = find_suite(line[: marker.start()])
        if not suite:
            continue
        bullet = f"{suite}: {marker.group(0)} passed" if ratio_m else f"{suite}: exit 0"
        if bullet not in seen:
            seen.add(bullet)
            bullets.append(bullet)
    return bullets


lead_override = ""
if lead_path:
    with open(lead_path, encoding="utf-8") as f:
        lead_override = f.read().strip()

if entity_path:
    with open(entity_path, encoding="utf-8") as f:
        entity_text = f.read()
    lead = lead_from_problem(entity_text, lead_override)
    what_changed = what_changed_from_entity(entity_text)
    evidence = suite_bullets_from_text(last_section(entity_text, "Stage Report: validation"))
elif what_changed_path:
    with open(what_changed_path, encoding="utf-8") as f:
        what_changed = [line.strip() for line in f if line.strip()]
    lead = lead_from_problem(issue.get("body", ""), lead_override)
    evidence = suite_bullets_from_text(tests_field.replace(";", "\n"))
else:
    print("what-changed required: pass --entity-path <dev-entity-file> or --what-changed-file <file>", file=sys.stderr)
    sys.exit(1)

if lead is None:
    print("lead required: first sentence exceeds 25 words with no clause boundary; pass --lead <file>", file=sys.stderr)
    sys.exit(1)

if not evidence and evidence_path:
    with open(evidence_path, encoding="utf-8") as f:
        evidence = [line.strip() for line in f if line.strip()]

lines = [lead, "", "## What changed"]
lines += [f"- {b}" for b in what_changed]

if evidence:
    lines += ["", "## Evidence"]
    lines += [f"- {b}" for b in evidence]

lines += ["", "---", f"[{entity_id}](/{owner_repo}/blob/{ref}/{readme_path})"]
close_line = issue.get("close_line", "")
if close_line:
    lines.append(close_line)

print("\n".join(lines))
PY
body_status=$?
set -e
[ "$body_status" -eq 0 ] || die "$(cat "$body_err_tmp")"
body="$(cat "$body_tmp")"

if [ "$dry_run" -eq 1 ]; then
  printf '%s\n' "$body"
  exit 0
fi

git -C "$repo_root" rev-parse --verify "${CANDIDATE_SHA}^{commit}" >/dev/null 2>&1 \
  || die "CANDIDATE_SHA unreachable: $CANDIDATE_SHA"

# Bind BRANCH to CANDIDATE_SHA before ever calling `gh`: a branch whose remote
# head differs from the reviewed commit would open a PR whose diff is not
# what was accepted. Fail closed on any ambiguity.
branch_refs="$(git -C "$repo_root" ls-remote origin "refs/heads/$BRANCH" 2>/dev/null || true)"
branch_ref_count="$(printf '%s\n' "$branch_refs" | grep -c '^[0-9a-f]\{40\}[[:space:]]' || true)"
[ "$branch_ref_count" -eq 1 ] \
  || die "BRANCH $BRANCH resolved to $branch_ref_count refs on origin, expected exactly 1"
branch_sha="$(printf '%s\n' "$branch_refs" | awk '{print $1}')"
[ "$branch_sha" = "$CANDIDATE_SHA" ] \
  || die "BRANCH $BRANCH remote head $branch_sha does not match CANDIDATE_SHA $CANDIDATE_SHA"

title="$(git -C "$repo_root" log -1 --format=%s "$CANDIDATE_SHA")"

body_file="$(mktemp)"
stderr_file="$(mktemp)"
trap 'rm -f "$body_tmp" "$body_err_tmp" "$body_file" "$stderr_file"' EXIT
printf '%s\n' "$body" >"$body_file"

log "opening Draft PR: branch=$BRANCH base=main title=$title"
set +e
pr_stdout="$(gh pr create --draft --base main --head "$BRANCH" --title "$title" --body-file "$body_file" 2>"$stderr_file")"
pr_status=$?
set -e
pr_stderr="$(cat "$stderr_file")"
[ -z "$pr_stderr" ] || log "gh pr create stderr: $pr_stderr"
if [ "$pr_status" -ne 0 ]; then
  die "gh pr create failed (exit $pr_status): $pr_stderr"
fi
log "gh pr create stdout: $pr_stdout"

# Parse the PR number from stdout only (`pull/<number>`); stderr is logged
# above, never scanned for digits, so a `gh` warning or notice on stderr
# cannot be mistaken for the PR number.
pr_number="$(printf '%s\n' "$pr_stdout" | grep -oE 'pull/[0-9]+' | grep -oE '[0-9]+' | tail -1)"
[ -n "$pr_number" ] || die "could not extract PR number from gh stdout: $pr_stdout"

echo "$pr_number"
