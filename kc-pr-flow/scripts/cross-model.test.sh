#!/usr/bin/env bash
# Unit tests for cross-model.sh — the deterministic logic behind kc-pr-review's
# cross-model reconciliation + Gemini arbitration (Step 5.5 / 5.6).
#
# Plain-bash runner, zero external deps (no bats). Exit non-zero on any failure.
# Run: bash kc-pr-flow/scripts/cross-model.test.sh
#
# Covers the three deterministic functions; the semantic fingerprint *assignment*
# is agent work and is intentionally NOT unit-tested here (see spec §9 R8).

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=cross-model.sh
. "$HERE/cross-model.sh"

PASS=0
FAIL=0
assert_eq() { # $1=desc $2=expected $3=actual
  if [ "$2" = "$3" ]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL: %s\n  expected: [%s]\n  actual:   [%s]\n' "$1" "$2" "$3"
  fi
}
assert_rc() { # $1=desc $2=expected_rc $3=actual_rc
  if [ "$2" = "$3" ]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL(rc): %s\n  expected rc: %s\n  actual rc:   %s\n' "$1" "$2" "$3"
  fi
}

# ---------------------------------------------------------------------------
# cross_model_tool_available
# ---------------------------------------------------------------------------
TMPBIN="$(mktemp -d)"
TMPHOME="$(mktemp -d)"
EMPTYDIR="$(mktemp -d)"
trap 'rm -rf "$TMPBIN" "$TMPHOME" "$EMPTYDIR"' EXIT
printf '#!/bin/sh\nexit 0\n' >"$TMPBIN/gemini"
printf '#!/bin/sh\nexit 0\n' >"$TMPBIN/codex"
chmod +x "$TMPBIN/gemini" "$TMPBIN/codex"

# binary missing -> unavailable
( PATH="$EMPTYDIR"; HOME="$TMPHOME"; unset GEMINI_API_KEY GOOGLE_API_KEY GOOGLE_GENAI_USE_VERTEXAI CODEX_API_KEY OPENAI_API_KEY CODEX_HOME
  cross_model_tool_available gemini ); rc=$?
assert_rc "gemini binary missing -> unavailable" 1 "$rc"

# binary present, no auth -> unavailable
( PATH="$TMPBIN:$EMPTYDIR"; HOME="$TMPHOME"; unset GEMINI_API_KEY GOOGLE_API_KEY GOOGLE_GENAI_USE_VERTEXAI CODEX_HOME
  cross_model_tool_available gemini ); rc=$?
assert_rc "gemini no auth -> unavailable" 1 "$rc"

# binary present + env key -> available
( PATH="$TMPBIN:$EMPTYDIR"; HOME="$TMPHOME"; export GEMINI_API_KEY=x
  cross_model_tool_available gemini ); rc=$?
assert_rc "gemini env key -> available" 0 "$rc"

# binary present + oauth file -> available
mkdir -p "$TMPHOME/.gemini"; : >"$TMPHOME/.gemini/oauth_creds.json"
( PATH="$TMPBIN:$EMPTYDIR"; HOME="$TMPHOME"; unset GEMINI_API_KEY GOOGLE_API_KEY GOOGLE_GENAI_USE_VERTEXAI
  cross_model_tool_available gemini ); rc=$?
assert_rc "gemini oauth file -> available" 0 "$rc"

# vertex env -> available
( PATH="$TMPBIN:$EMPTYDIR"; HOME="$EMPTYDIR"; unset GEMINI_API_KEY GOOGLE_API_KEY; export GOOGLE_GENAI_USE_VERTEXAI=1
  cross_model_tool_available gemini ); rc=$?
assert_rc "gemini vertex env -> available" 0 "$rc"

# vertex flag set to "false" is NOT an auth signal (truthy-only)
( PATH="$TMPBIN:$EMPTYDIR"; HOME="$EMPTYDIR"; unset GEMINI_API_KEY GOOGLE_API_KEY; export GOOGLE_GENAI_USE_VERTEXAI=false
  cross_model_tool_available gemini ); rc=$?
assert_rc "gemini vertex=false -> unavailable" 1 "$rc"

# codex auth.json under HOME -> available
mkdir -p "$TMPHOME/.codex"; : >"$TMPHOME/.codex/auth.json"
( PATH="$TMPBIN:$EMPTYDIR"; HOME="$TMPHOME"; unset CODEX_API_KEY OPENAI_API_KEY CODEX_HOME
  cross_model_tool_available codex ); rc=$?
assert_rc "codex auth.json -> available" 0 "$rc"

# codex env key -> available
( PATH="$TMPBIN:$EMPTYDIR"; HOME="$EMPTYDIR"; unset CODEX_HOME; export OPENAI_API_KEY=x
  cross_model_tool_available codex ); rc=$?
assert_rc "codex OPENAI_API_KEY -> available" 0 "$rc"

# unknown tool -> unavailable (defensive)
( PATH="$TMPBIN:$EMPTYDIR"; HOME="$TMPHOME"
  cross_model_tool_available banana ); rc=$?
assert_rc "unknown tool -> unavailable" 1 "$rc"

# ---------------------------------------------------------------------------
# cross_model_conflict_filter
# Input  TSV: side  stance  fingerprint  file:line  severity  root  summary
# Output TSV: id  bucket  arbitrate  side  fingerprint  file:line  severity  root  summary
# ---------------------------------------------------------------------------
fp_state() { # $1=fingerprint $2=output -> "bucket:arbitrate" or ABSENT
  awk -F'\t' -v fp="$1" '$5==fp{print $2":"$3; f=1} END{if(!f)print "ABSENT"}' <<<"$2"
}

# Agreement: same fp flagged by both -> suppressed (absent from disputes)
OUT="$(printf 'claude\tflag\tfpA\ta.ts:10\tHIGH\tCODE\tnull deref\ncodex\tflag\tfpA\ta.ts:10\tHIGH\tCODE\tnull deref\n' | cross_model_conflict_filter)"
assert_eq "agreement suppressed" "ABSENT" "$(fp_state fpA "$OUT")"

# Claude-only LOW non-CODE -> excluded (immaterial)
OUT="$(printf 'claude\tflag\tfpL\tb.ts:2\tLOW\tDOC\tstale todo\n' | cross_model_conflict_filter)"
assert_eq "claude-only LOW/DOC excluded" "ABSENT" "$(fp_state fpL "$OUT")"

# Claude-only MEDIUM -> included, arbitrate
OUT="$(printf 'claude\tflag\tfpM\tc.ts:3\tMEDIUM\tDOC\tedge case\n' | cross_model_conflict_filter)"
assert_eq "claude-only MEDIUM included" "claude-only:yes" "$(fp_state fpM "$OUT")"

# Codex-only LOW but root=CODE -> included (root overrides severity)
OUT="$(printf 'codex\tflag\tfpC\td.ts:4\tLOW\tCODE\tmissing await\n' | cross_model_conflict_filter)"
assert_eq "codex-only LOW+CODE included" "codex-only:yes" "$(fp_state fpC "$OUT")"

# Contradiction: one flags, other says ok -> always included
OUT="$(printf 'claude\tflag\tfpX\te.ts:5\tHIGH\tCODE\trace\ncodex\tok\tfpX\te.ts:5\tHIGH\tCODE\tno race\n' | cross_model_conflict_filter)"
assert_eq "contradiction included" "contradiction:yes" "$(fp_state fpX "$OUT")"

# Contradiction sorts by the CLAIM (flag) severity, not a higher-severity "ok" row.
# cA: flag HIGH / ok HIGH (claim rank 4). cB: flag LOW / ok CRITICAL (claim rank 2,
# but maxrank 5 from the ok row). Sorting by maxrank would put cB first (the bug);
# sorting by the claim rank keeps cA first and emits cB's claim severity (LOW).
OUT="$(printf 'claude\tflag\tcA\tr.ts:1\tHIGH\tCODE\ta\ncodex\tok\tcA\tr.ts:1\tHIGH\tCODE\tx\nclaude\tflag\tcB\tr.ts:2\tLOW\tCODE\tb\ncodex\tok\tcB\tr.ts:2\tCRITICAL\tCODE\ty\n' | cross_model_conflict_filter)"
assert_eq "contradiction sorts by claim severity, not ok-row" "cA" "$(awk -F'\t' 'NR==1{print $5}' <<<"$OUT")"
assert_eq "contradiction emits claim-row severity" "LOW" "$(awk -F'\t' '$5=="cB"{print $7}' <<<"$OUT")"

# Same file:line, distinct issue keyword -> two separate fingerprints, both kept
OUT="$(printf 'claude\tflag\tf.ts:9|null\tf.ts:9\tHIGH\tCODE\tnull\ncodex\tflag\tf.ts:9|leak\tf.ts:9\tHIGH\tCODE\tleak\n' | cross_model_conflict_filter)"
n=$(awk -F'\t' '$6=="f.ts:9"' <<<"$OUT" | wc -l | tr -d ' ')
assert_eq "same-line distinct bugs stay separate" "2" "$n"

# Cap: contradictions exempt; exclusives capped; over-cap listed not dropped
CAP_IN="$(
  printf 'claude\tflag\tk0\tz.ts:0\tCRITICAL\tCODE\tcontra\ncodex\tok\tk0\tz.ts:0\tCRITICAL\tCODE\tcontra\n'
  for i in 1 2 3 4 5; do printf 'codex\tflag\tk%s\tz.ts:%s\tHIGH\tCODE\tbug%s\n' "$i" "$i" "$i"; done
)"
OUT="$(printf '%s' "$CAP_IN" | CROSS_MODEL_ARB_CAP=2 cross_model_conflict_filter)"
yes_excl=$(awk -F'\t' '$2!="contradiction" && $3=="yes"' <<<"$OUT" | wc -l | tr -d ' ')
overcap=$(awk -F'\t' '$3=="no-overcap"' <<<"$OUT" | wc -l | tr -d ' ')
contra_yes=$(awk -F'\t' '$2=="contradiction" && $3=="yes"' <<<"$OUT" | wc -l | tr -d ' ')
assert_eq "cap limits exclusive arbitration to 2" "2" "$yes_excl"
assert_eq "over-cap exclusives listed (3)" "3" "$overcap"
assert_eq "contradiction exempt from cap" "1" "$contra_yes"

# Ordering: contradiction row gets id D1 (sorted first)
first_bucket=$(awk -F'\t' 'NR==1{print $2}' <<<"$OUT")
assert_eq "contradiction sorted first" "contradiction" "$first_bucket"

# Malformed row (wrong column count) -> skipped, valid rows still processed, rc 0
OUT="$(printf 'garbage-row-no-tabs\nclaude\tflag\tfpOK\tg.ts:1\tHIGH\tCODE\tok\n' | cross_model_conflict_filter)"; rc=$?
assert_rc "malformed row -> rc 0" 0 "$rc"
assert_eq "malformed skipped, valid kept" "claude-only:yes" "$(fp_state fpOK "$OUT")"

# Unknown severity -> handled (included at MEDIUM rank for an exclusive)
OUT="$(printf 'claude\tflag\tfpU\th.ts:1\tWEIRD\tDOC\tmystery\n' | cross_model_conflict_filter)"
assert_eq "unknown severity included" "claude-only:yes" "$(fp_state fpU "$OUT")"

# Multi-row same fingerprint: a later CODE/HIGH row keeps it material + sets the rep
OUT="$(printf 'claude\tflag\tdupfp\tm.ts:1\tLOW\tDOC\tfirst\nclaude\tflag\tdupfp\tm.ts:1\tHIGH\tCODE\tsecond\n' | cross_model_conflict_filter)"
assert_eq "multi-row fp stays material via later CODE/HIGH" "claude-only:yes" "$(fp_state dupfp "$OUT")"
assert_eq "multi-row fp emits max severity" "HIGH" "$(awk -F'\t' '$5=="dupfp"{print $7}' <<<"$OUT")"

# Id prefix (nonce) flows deterministically into emitted ids
OUT="$(printf 'codex\tflag\tpfx\tn.ts:1\tHIGH\tCODE\tx\n' | CROSS_MODEL_ID_PREFIX='z9-' cross_model_conflict_filter)"
assert_eq "id prefix applied" "z9-1" "$(awk -F'\t' 'NR==1{print $1}' <<<"$OUT")"

# Cap top-N is by severity (mixed), over-cap exclusives are listed not dropped
MIX_IN="$(
  printf 'codex\tflag\tm-crit\tz.ts:1\tCRITICAL\tCODE\tc\n'
  printf 'codex\tflag\tm-low\tz.ts:2\tLOW\tCODE\tl\n'
  printf 'codex\tflag\tm-high\tz.ts:3\tHIGH\tCODE\th\n'
  printf 'codex\tflag\tm-med\tz.ts:4\tMEDIUM\tCODE\tm\n'
)"
OUT="$(printf '%s' "$MIX_IN" | CROSS_MODEL_ARB_CAP=2 cross_model_conflict_filter)"
assert_eq "cap keeps CRITICAL" "codex-only:yes" "$(fp_state m-crit "$OUT")"
assert_eq "cap keeps HIGH" "codex-only:yes" "$(fp_state m-high "$OUT")"
assert_eq "cap drops MEDIUM to overcap" "codex-only:no-overcap" "$(fp_state m-med "$OUT")"
assert_eq "cap drops LOW to overcap" "codex-only:no-overcap" "$(fp_state m-low "$OUT")"
assert_eq "highest severity sorted first" "m-crit" "$(awk -F'\t' 'NR==1{print $5}' <<<"$OUT")"

# Empty input -> empty output, rc 0
OUT="$(printf '' | cross_model_conflict_filter)"; rc=$?
assert_rc "empty input rc 0" 0 "$rc"
assert_eq "empty input empty output" "" "$OUT"

# ---------------------------------------------------------------------------
# cross_model_arb_parse "<known-ids-csv>" < gemini_output
# Output TSV: id  verdict   (verdict in REAL_BUG|FALSE_POSITIVE|UNCERTAIN|UNCHANGED)
# rc 0 normally; rc 3 when fewer than half of expected ids parse (whole-arb-failed)
# ---------------------------------------------------------------------------
verdict_of() { awk -F'\t' -v id="$1" '$1==id{print $2}' <<<"$2"; }

# Well-formed
OUT="$(printf 'ARB D1 REAL_BUG — yes\nARB D2 FALSE_POSITIVE — no\nARB D3 UNCERTAIN — meh\n' | cross_model_arb_parse 'D1,D2,D3')"; rc=$?
assert_rc "well-formed rc 0" 0 "$rc"
assert_eq "D1 real" "REAL_BUG" "$(verdict_of D1 "$OUT")"
assert_eq "D2 fp" "FALSE_POSITIVE" "$(verdict_of D2 "$OUT")"
assert_eq "D3 uncertain" "UNCERTAIN" "$(verdict_of D3 "$OUT")"

# Unknown id dropped (injection-safe); known still parsed
OUT="$(printf 'ARB D1 REAL_BUG\nARB D9 FALSE_POSITIVE\n' | cross_model_arb_parse 'D1')"; rc=$?
assert_rc "unknown id rc 0" 0 "$rc"
assert_eq "D1 parsed" "REAL_BUG" "$(verdict_of D1 "$OUT")"
assert_eq "unknown D9 absent" "" "$(verdict_of D9 "$OUT")"

# Duplicate id -> first wins
OUT="$(printf 'ARB D1 REAL_BUG\nARB D1 FALSE_POSITIVE\n' | cross_model_arb_parse 'D1')"
assert_eq "duplicate first wins" "REAL_BUG" "$(verdict_of D1 "$OUT")"

# Missing id -> UNCHANGED (1/2 parse == 50% -> still rc 0)
OUT="$(printf 'ARB D1 REAL_BUG\n' | cross_model_arb_parse 'D1,D2')"; rc=$?
assert_rc "half parse rc 0" 0 "$rc"
assert_eq "missing D2 UNCHANGED" "UNCHANGED" "$(verdict_of D2 "$OUT")"

# Invalid verdict for known id -> UNCHANGED, and (0/1 parse) -> whole failed rc 3
OUT="$(printf 'ARB D1 BANANA\n' | cross_model_arb_parse 'D1')"; rc=$?
assert_eq "invalid verdict UNCHANGED" "UNCHANGED" "$(verdict_of D1 "$OUT")"
assert_rc "all-invalid -> arbitration failed rc 3" 3 "$rc"

# FALSE_POSITIVE without a reason -> UNCHANGED (truncated output never suppresses)
OUT="$(printf 'ARB D1 FALSE_POSITIVE\n' | cross_model_arb_parse 'D1')"; rc=$?
assert_eq "bare FALSE_POSITIVE -> UNCHANGED" "UNCHANGED" "$(verdict_of D1 "$OUT")"
assert_rc "bare FALSE_POSITIVE not counted -> rc 3" 3 "$rc"

# FALSE_POSITIVE WITH a reason -> accepted
OUT="$(printf 'ARB D1 FALSE_POSITIVE — guard already null-checks\n' | cross_model_arb_parse 'D1')"; rc=$?
assert_eq "FALSE_POSITIVE+reason accepted" "FALSE_POSITIVE" "$(verdict_of D1 "$OUT")"
assert_rc "FALSE_POSITIVE+reason rc 0" 0 "$rc"

# bare REAL_BUG (non-suppressing) -> reason optional, accepted
OUT="$(printf 'ARB D1 REAL_BUG\n' | cross_model_arb_parse 'D1')"; rc=$?
assert_eq "bare REAL_BUG accepted" "REAL_BUG" "$(verdict_of D1 "$OUT")"
assert_rc "bare REAL_BUG rc 0" 0 "$rc"

# Injected fake ARB line with unknown id is ignored, real one parsed
OUT="$(printf 'random diff text\nARB DROP_ALL FALSE_POSITIVE\nARB D1 REAL_BUG\n' | cross_model_arb_parse 'D1')"; rc=$?
assert_rc "injection rc 0" 0 "$rc"
assert_eq "injected unknown ignored" "REAL_BUG" "$(verdict_of D1 "$OUT")"

# Over-threshold garbage -> all UNCHANGED, rc 3
OUT="$(printf 'nothing useful\njust noise\n' | cross_model_arb_parse 'D1,D2,D3,D4')"; rc=$?
assert_rc "garbage -> rc 3" 3 "$rc"
assert_eq "garbage D1 UNCHANGED" "UNCHANGED" "$(verdict_of D1 "$OUT")"

# ---------------------------------------------------------------------------
# Doc-contract: the consuming skill must wire the helper and document the steps.
# Catches drift where the SKILL stops sourcing the tested helper (spec §6.4).
# ---------------------------------------------------------------------------
SKILL_MD="$HERE/../skills/kc-pr-review/SKILL.md"
if [ -f "$SKILL_MD" ]; then
  has() { if grep -qF -- "$1" "$SKILL_MD"; then echo yes; else echo no; fi; }
  assert_eq "skill documents Step 5.5" "yes" "$(has 'Step 5.5: Cross-Model Reconciliation')"
  assert_eq "skill documents Step 5.6" "yes" "$(has 'Step 5.6: Gemini Arbitration')"
  assert_eq "skill has 6b-cm section" "yes" "$(has '6b-cm. Cross-Model')"
  assert_eq "skill sources tested helper" "yes" "$(has 'scripts/cross-model.sh')"
  assert_eq "skill calls conflict_filter" "yes" "$(has 'cross_model_conflict_filter')"
  assert_eq "skill calls arb_parse" "yes" "$(has 'cross_model_arb_parse')"
else
  echo "note: SKILL.md not found at expected path; skipping doc-contract checks"
fi

# ---------------------------------------------------------------------------
printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
