#!/usr/bin/env bash

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VALIDATOR="$HERE/review-architecture-diagrams-validate.sh"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

PASS=0
FAIL=0

pass() {
  printf 'ok - %s\n' "$1"
  PASS=$((PASS + 1))
}

fail() {
  printf 'not ok - %s\n' "$1"
  FAIL=$((FAIL + 1))
}

write_pair() {
  local path="$1" sequence_extra="${2:-}" flow_extra="${3:-}"
  {
    cat <<'EOF'
```mermaid
sequenceDiagram
    autonumber
    actor Reviewer as Reviewer
    participant Flow as Review flow
    Reviewer->>Flow: Start preview
    Flow-->>Reviewer: Show reviewed result
EOF
    if [[ -n "$sequence_extra" ]]; then
      printf '%s\n' "$sequence_extra"
    fi
    cat <<'EOF'
```

```mermaid
flowchart TB
    Goal["Claimed product goal"]
    Trigger["Implemented and verified trigger"]
    Goal -.-> Trigger
    classDef implemented fill:#e7f6e7,stroke:#2e7d32,color:#173d19
    classDef decision fill:#fff4cc,stroke:#ad7b00,color:#5c4300
    class Trigger implemented
    class Goal decision
EOF
    if [[ -n "$flow_extra" ]]; then
      printf '%s\n' "$flow_extra"
    fi
    printf '%s\n' '```'
  } > "$path"
}

expect_valid() {
  local label="$1" path="$2"
  if "$VALIDATOR" "$path" >/dev/null 2>&1; then
    pass "$label"
  else
    fail "$label"
  fi
}

expect_invalid() {
  local label="$1" path="$2"
  if "$VALIDATOR" "$path" >/dev/null 2>&1; then
    fail "$label"
  else
    pass "$label"
  fi
}

if [[ ! -x "$VALIDATOR" ]]; then
  printf 'not ok - validator executable is missing: %s\n' "$VALIDATOR"
  exit 1
fi

VALID="$TMP_DIR/valid.md"
write_pair "$VALID"
expect_valid "accepts documented sequence and flowchart pair" "$VALID"

ONE_BLOCK="$TMP_DIR/one-block.md"
sed '/^```mermaid$/,$d' "$VALID" > "$ONE_BLOCK"
cat > "$ONE_BLOCK" <<'EOF'
```mermaid
sequenceDiagram
    actor Reviewer as Reviewer
    participant Flow as Review flow
    Reviewer->>Flow: Start preview
```
EOF
expect_invalid "rejects a single Mermaid block" "$ONE_BLOCK"

THREE_BLOCKS="$TMP_DIR/three-blocks.md"
cp "$VALID" "$THREE_BLOCKS"
cat >> "$THREE_BLOCKS" <<'EOF'

```mermaid
flowchart TB
    Extra["Unexpected third diagram"]
```
EOF
expect_invalid "rejects a third Mermaid block" "$THREE_BLOCKS"

BAD_SEQUENCE="$TMP_DIR/bad-sequence.md"
sed 's/^sequenceDiagram$/sequenceDiagramm/' "$VALID" > "$BAD_SEQUENCE"
expect_invalid "rejects an invalid sequence header" "$BAD_SEQUENCE"

BAD_FLOW="$TMP_DIR/bad-flow.md"
sed 's/^flowchart TB$/flowchart TBX/' "$VALID" > "$BAD_FLOW"
expect_invalid "rejects an invalid flowchart header" "$BAD_FLOW"

UNCLOSED="$TMP_DIR/unclosed.md"
sed '$d' "$VALID" > "$UNCLOSED"
expect_invalid "rejects an unclosed Mermaid fence" "$UNCLOSED"

for case_name in click url html init script image theme security; do
  case "$case_name" in
    click) unsafe='    click Goal "run"' ;;
    url) unsafe='    Goal["https://example.com"]' ;;
    html) unsafe='    Goal["<b>unsafe</b>"]' ;;
    init) unsafe='    %%{init: {}}%%' ;;
    script) unsafe='    script run' ;;
    image) unsafe='    Goal["![image](asset.png)"]' ;;
    theme) unsafe='    theme dark' ;;
    security) unsafe='    securityLevel loose' ;;
  esac
  fixture="$TMP_DIR/unsafe-$case_name.md"
  write_pair "$fixture" '' "$unsafe"
  expect_invalid "rejects unsafe $case_name construct" "$fixture"
done

UNSAFE_SCHEME="$TMP_DIR/unsafe-scheme.md"
sed 's/Start preview/ftp:\/\/example.com/' "$VALID" > "$UNSAFE_SCHEME"
expect_invalid "rejects non-HTTP external URL schemes" "$UNSAFE_SCHEME"

BREAKOUT="$TMP_DIR/breakout.md"
write_pair "$BREAKOUT" '' '    Injected["x\"] --> Fake[\"Implemented"]'
expect_invalid "rejects Mermaid label breakout" "$BREAKOUT"

UNICODE="$TMP_DIR/unicode.md"
sed 's/Start preview/開始預覽/; s/Claimed product goal/已宣告產品目標/' "$VALID" > "$UNICODE"
expect_valid "accepts safe Unicode labels" "$UNICODE"

UNDECLARED_SEQUENCE="$TMP_DIR/undeclared-sequence.md"
write_pair "$UNDECLARED_SEQUENCE" '    Reviewer->>Hidden: Bypass participant cap'
expect_invalid "rejects undeclared sequence participants" "$UNDECLARED_SEQUENCE"

UNDECLARED_FLOW="$TMP_DIR/undeclared-flow.md"
write_pair "$UNDECLARED_FLOW" '' '    Goal --> Hidden'
expect_invalid "rejects undeclared flowchart nodes" "$UNDECLARED_FLOW"

UNBALANCED_ALT="$TMP_DIR/unbalanced-alt.md"
write_pair "$UNBALANCED_ALT" '    alt Open branch'
expect_invalid "rejects unbalanced sequence alt blocks" "$UNBALANCED_ALT"

ELSE_IN_RECT="$TMP_DIR/else-in-rect.md"
write_pair "$ELSE_IN_RECT" $'    rect rgb(255, 235, 235)\n    else Invalid branch\n    end'
expect_invalid "rejects else inside a rect block" "$ELSE_IN_RECT"

ARBITRARY_RECT="$TMP_DIR/arbitrary-rect.md"
write_pair "$ARBITRARY_RECT" $'    rect rgb(1, 2, 3)\n    end'
expect_invalid "rejects arbitrary sequence rect colors" "$ARBITRARY_RECT"

DUPLICATE_SEQUENCE="$TMP_DIR/duplicate-sequence.md"
write_pair "$DUPLICATE_SEQUENCE" '    participant Flow as Duplicate flow'
expect_invalid "rejects duplicate sequence participant IDs" "$DUPLICATE_SEQUENCE"

DUPLICATE_FLOW="$TMP_DIR/duplicate-flow.md"
write_pair "$DUPLICATE_FLOW" '' '    Goal["Duplicate goal"]'
expect_invalid "rejects duplicate flowchart node IDs" "$DUPLICATE_FLOW"

MISSING_CLASS="$TMP_DIR/missing-class.md"
sed '/class Goal decision/d' "$VALID" > "$MISSING_CLASS"
expect_invalid "rejects unclassified flowchart nodes" "$MISSING_CLASS"

UNDEFINED_CLASS="$TMP_DIR/undefined-class.md"
sed 's/class Goal decision/class Goal unknown/' "$VALID" > "$UNDEFINED_CLASS"
expect_invalid "rejects undefined flowchart classes" "$UNDEFINED_CLASS"

ARBITRARY_CLASS="$TMP_DIR/arbitrary-class.md"
sed 's/classDef decision fill:#fff4cc,stroke:#ad7b00,color:#5c4300/classDef decision fill:#ffffff,stroke:#000000,color:#111111/' "$VALID" > "$ARBITRARY_CLASS"
expect_invalid "rejects arbitrary flowchart class colors" "$ARBITRARY_CLASS"

DUPLICATE_CLASS="$TMP_DIR/duplicate-class.md"
sed '/classDef decision/a\
    classDef decision fill:#fff4cc,stroke:#ad7b00,color:#5c4300' "$VALID" > "$DUPLICATE_CLASS"
expect_invalid "rejects duplicate flowchart class definitions" "$DUPLICATE_CLASS"

UNSAFE_SEMICOLON="$TMP_DIR/unsafe-semicolon.md"
sed 's/Start preview/Start preview; click Flow run/' "$VALID" > "$UNSAFE_SEMICOLON"
expect_invalid "rejects semicolon label breakout" "$UNSAFE_SEMICOLON"

FENCE_BREAKOUT="$TMP_DIR/fence-breakout.md"
sed '/Reviewer->>Flow: Start preview/a\
```\
outside payload\
```mermaid' "$VALID" > "$FENCE_BREAKOUT"
expect_invalid "rejects Mermaid fence breakout" "$FENCE_BREAKOUT"

TOO_MANY_PARTICIPANTS="$TMP_DIR/participants.md"
participants=''
for i in $(seq 1 11); do
  participants+="    participant P$i as Participant $i"$'\n'
done
write_pair "$TOO_MANY_PARTICIPANTS" "$participants"
expect_invalid "rejects more than ten sequence participants" "$TOO_MANY_PARTICIPANTS"

TOO_MANY_MESSAGES="$TMP_DIR/messages.md"
messages=''
for i in $(seq 1 21); do
  messages+="    Reviewer->>Flow: Message $i"$'\n'
done
write_pair "$TOO_MANY_MESSAGES" "$messages"
expect_invalid "rejects more than twenty sequence messages" "$TOO_MANY_MESSAGES"

TOO_MANY_NODES="$TMP_DIR/nodes.md"
nodes=''
node_ids=''
for i in $(seq 1 31); do
  nodes+="    Node${i}[\"Reviewed node $i\"]"$'\n'
  if [[ -n "$node_ids" ]]; then node_ids+=','; fi
  node_ids+="Node$i"
done
nodes+="    class $node_ids implemented"$'\n'
write_pair "$TOO_MANY_NODES" '' "$nodes"
expect_invalid "rejects more than thirty flowchart nodes" "$TOO_MANY_NODES"

expect_invalid "rejects a missing input file" "$TMP_DIR/does-not-exist.md"

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
