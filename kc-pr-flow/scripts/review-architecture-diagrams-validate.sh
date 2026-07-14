#!/usr/bin/env bash

set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  printf 'usage: %s <diagram-pair.md>\n' "$0" >&2
  exit 2
fi

INPUT="$1"
if [[ ! -r "$INPUT" ]]; then
  printf 'diagram pair is not readable: %s\n' "$INPUT" >&2
  exit 2
fi

LC_ALL=C awk '
function reject(message) {
  printf "diagram validation failed at line %d: %s\n", NR, message > "/dev/stderr"
  invalid = 1
}

function trim(value) {
  sub(/^[[:space:]]+/, "", value)
  sub(/[[:space:]]+$/, "", value)
  return value
}

function phrase_is_safe(value, lower) {
  lower = tolower(value)
  if (value ~ /[][{}<>"`\\;|]/) return 0
  if (value ~ /-->|-\.->|->>|-->>|%%|```/) return 0
  if (lower ~ /[a-z][a-z0-9+.-]*:\/\//) return 0
  if (lower ~ /(javascript|data|mailto):/) return 0
  if (lower ~ /securitylevel|theme[[:space:]]*:/) return 0
  if (value ~ /!\[/) return 0
  return 1
}

function unsafe_construct(value, lower) {
  lower = tolower(value)
  if (lower ~ /[a-z][a-z0-9+.-]*:\/\//) return 1
  if (lower ~ /(javascript|data|mailto):/) return 1
  if (lower ~ /%%[[:space:]]*\{/) return 1
  if (lower ~ /^[[:space:]]*click([[:space:]]|$)/) return 1
  if (lower ~ /^[[:space:]]*script([[:space:]]|$)/) return 1
  if (lower ~ /^[[:space:]]*image([[:space:]:]|$)/) return 1
  if (lower ~ /^[[:space:]]*theme([[:space:]:]|$)/) return 1
  if (lower ~ /^[[:space:]]*securitylevel([[:space:]:]|$)/) return 1
  if (value ~ /!\[/) return 1
  if (value ~ /<[^>]*>/) return 1
  return 0
}

function validate_sequence(value, phrase, declaration, id, refs, count, parts, i) {
  if (value == "autonumber") {
    if (sequence_autonumber) reject("duplicate sequence autonumber")
    sequence_autonumber = 1
    return
  }

  if (value ~ /^(actor|participant)[[:space:]]+[A-Za-z][A-Za-z0-9_]*[[:space:]]+as[[:space:]]+.+$/) {
    declaration = value
    sub(/[[:space:]]+as[[:space:]].*$/, "", declaration)
    sub(/^(actor|participant)[[:space:]]+/, "", declaration)
    if (declaration in sequence_ids) reject("duplicate sequence participant ID")
    sequence_ids[declaration] = 1
    phrase = value
    sub(/^(actor|participant)[[:space:]]+[A-Za-z][A-Za-z0-9_]*[[:space:]]+as[[:space:]]+/, "", phrase)
    if (!phrase_is_safe(phrase)) reject("unsafe participant label")
    sequence_participants++
    return
  }

  if (value ~ /^[A-Za-z][A-Za-z0-9_]*(->>|-->>)[A-Za-z][A-Za-z0-9_]*:[[:space:]]*.+$/) {
    refs = value
    sub(/:.*/, "", refs)
    gsub(/-->>|->>/, " ", refs)
    count = split(refs, parts, /[[:space:]]+/)
    for (i = 1; i <= count; i++) if (parts[i] != "") sequence_refs[parts[i]] = 1
    phrase = value
    sub(/^[^:]*:[[:space:]]*/, "", phrase)
    if (!phrase_is_safe(phrase)) reject("unsafe sequence message")
    sequence_messages++
    return
  }

  if (value ~ /^Note over [A-Za-z][A-Za-z0-9_]*(,[A-Za-z][A-Za-z0-9_]*)*:[[:space:]]*.+$/) {
    refs = value
    sub(/^Note over /, "", refs)
    sub(/:.*/, "", refs)
    count = split(refs, parts, /,/)
    for (i = 1; i <= count; i++) sequence_refs[parts[i]] = 1
    phrase = value
    sub(/^Note over [^:]*:[[:space:]]*/, "", phrase)
    if (!phrase_is_safe(phrase)) reject("unsafe sequence note")
    return
  }

  if (value ~ /^alt[[:space:]]+.+$/) {
    phrase = value
    sub(/^alt[[:space:]]+/, "", phrase)
    if (!phrase_is_safe(phrase)) reject("unsafe alt label")
    sequence_depth++
    sequence_stack[sequence_depth] = "alt"
    return
  }

  if (value ~ /^else[[:space:]]+.+$/) {
    if (sequence_depth < 1 || sequence_stack[sequence_depth] != "alt") reject("else appears outside an alt block")
    phrase = value
    sub(/^else[[:space:]]+/, "", phrase)
    if (!phrase_is_safe(phrase)) reject("unsafe else label")
    return
  }

  if (value == "rect rgb(255, 235, 235)") {
    sequence_depth++
    sequence_stack[sequence_depth] = "rect"
    return
  }

  if (value == "end") {
    if (sequence_depth < 1) {
      reject("unexpected sequence end")
    } else {
      delete sequence_stack[sequence_depth]
      sequence_depth--
    }
    return
  }

  reject("line is outside the documented sequence grammar")
}

function validate_flow(value, label, id, refs, count, parts, i, class_name, definition) {
  if (value ~ /^[A-Za-z][A-Za-z0-9_]*\[".*"\]$/) {
    id = value
    sub(/\[.*/, "", id)
    if (id in flow_ids) reject("duplicate flowchart node ID")
    flow_ids[id] = 1
    label = value
    sub(/^[A-Za-z][A-Za-z0-9_]*\["/, "", label)
    sub(/"\]$/, "", label)
    if (!phrase_is_safe(label)) reject("unsafe flowchart label")
    flow_nodes++
    return
  }

  if (value ~ /^[A-Za-z][A-Za-z0-9_]*[[:space:]]+(-->|-\.->)[[:space:]]+[A-Za-z][A-Za-z0-9_]*$/) {
    refs = value
    gsub(/[[:space:]]+(-->|-\.->)[[:space:]]+/, " ", refs)
    count = split(refs, parts, /[[:space:]]+/)
    for (i = 1; i <= count; i++) if (parts[i] != "") flow_refs[parts[i]] = 1
    return
  }

  if (value ~ /^classDef[[:space:]]+[A-Za-z][A-Za-z0-9_]*[[:space:]]+fill:#[0-9A-Fa-f]+,stroke:#[0-9A-Fa-f]+,color:#[0-9A-Fa-f]+$/) {
    class_name = value
    sub(/^classDef[[:space:]]+/, "", class_name)
    sub(/[[:space:]].*$/, "", class_name)
    definition = value
    sub(/^classDef[[:space:]]+[A-Za-z][A-Za-z0-9_]*[[:space:]]+/, "", definition)
    if (!(class_name in allowed_class_def) || definition != allowed_class_def[class_name]) reject("unsupported flowchart class definition")
    if (class_name in flow_class_defs) reject("duplicate flowchart class definition")
    flow_class_defs[class_name] = 1
    return
  }

  if (value ~ /^class[[:space:]]+[A-Za-z][A-Za-z0-9_]*(,[A-Za-z][A-Za-z0-9_]*)*[[:space:]]+[A-Za-z][A-Za-z0-9_]*$/) {
    refs = value
    sub(/^class[[:space:]]+/, "", refs)
    class_name = refs
    sub(/^.*[[:space:]]+/, "", class_name)
    sub(/[[:space:]].*$/, "", refs)
    if (!(class_name in allowed_class_def)) reject("unsupported flowchart class name")
    flow_class_refs[class_name] = 1
    count = split(refs, parts, /,/)
    for (i = 1; i <= count; i++) {
      flow_refs[parts[i]] = 1
      if (parts[i] in flow_node_classes) reject("flowchart node has multiple class assignments")
      flow_node_classes[parts[i]] = class_name
    }
    return
  }

  reject("line is outside the documented flowchart grammar")
}

BEGIN {
  in_mermaid = 0
  blocks = 0
  sequence_blocks = 0
  flow_blocks = 0
  sequence_participants = 0
  sequence_messages = 0
  sequence_autonumber = 0
  sequence_depth = 0
  flow_nodes = 0
  invalid = 0
  allowed_class_def["implemented"] = "fill:#e7f6e7,stroke:#2e7d32,color:#173d19"
  allowed_class_def["problem"] = "fill:#fde8e8,stroke:#c62828,color:#5f1616"
  allowed_class_def["decision"] = "fill:#fff4cc,stroke:#ad7b00,color:#5c4300"
  allowed_class_def["future"] = "fill:#eeeeee,stroke:#757575,color:#333333"
  allowed_class_def["core"] = "fill:#e8f1fb,stroke:#2962a3,color:#163b61"
}

{
  sub(/\r$/, "")
  line = $0

  if (line ~ /^```mermaid[[:space:]]*$/) {
    if (in_mermaid) reject("nested Mermaid fence")
    in_mermaid = 1
    blocks++
    if (blocks == 1) expected_header = "sequenceDiagram"
    else if (blocks == 2) expected_header = "flowchart TB"
    else expected_header = ""
    block_type = ""
    next
  }

  if (line ~ /^```[[:space:]]*$/) {
    if (!in_mermaid) {
      reject("unexpected closing fence")
    } else if (block_type == "") {
      reject("empty Mermaid block")
    }
    if (block_type == "sequence" && sequence_depth != 0) reject("unclosed sequence control block")
    in_mermaid = 0
    block_type = ""
    next
  }

  if (!in_mermaid) {
    if (line !~ /^[[:space:]]*$/) reject("nonblank content outside Mermaid blocks")
    next
  }

  if (line ~ /[[:cntrl:]]/) {
    reject("control character inside Mermaid block")
    next
  }

  if (unsafe_construct(line)) {
    reject("unsafe Mermaid construct")
    next
  }

  value = trim(line)
  if (value == "") next

  if (block_type == "") {
    if (value != expected_header) {
      reject("diagram type or order does not match the documented pair")
      block_type = "invalid"
    } else if (value == "sequenceDiagram") {
      block_type = "sequence"
      sequence_blocks++
    } else if (value == "flowchart TB") {
      block_type = "flow"
      flow_blocks++
    } else {
      reject("unsupported Mermaid diagram header")
      block_type = "invalid"
    }
    next
  }

  if (block_type == "sequence") {
    validate_sequence(value)
  } else if (block_type == "flow") {
    validate_flow(value)
  } else {
    reject("content follows an invalid diagram header")
  }
}

END {
  for (id in sequence_refs) if (!(id in sequence_ids)) reject("sequence references an undeclared participant")
  for (id in flow_refs) if (!(id in flow_ids)) reject("flowchart references an undeclared node")
  for (id in flow_ids) if (!(id in flow_node_classes)) reject("flowchart node is missing a status class")
  for (class_name in flow_class_refs) if (!(class_name in flow_class_defs)) reject("flowchart uses an undefined class")
  if (in_mermaid) reject("unclosed Mermaid fence")
  if (blocks != 2) reject("expected exactly two Mermaid blocks")
  if (sequence_blocks != 1) reject("expected exactly one sequenceDiagram")
  if (flow_blocks != 1) reject("expected exactly one flowchart TB")
  if (sequence_participants > 10) reject("sequence participant cap exceeded")
  if (sequence_messages > 20) reject("sequence message cap exceeded")
  if (flow_nodes > 30) reject("flowchart node cap exceeded")
  exit invalid ? 1 : 0
}
' "$INPUT"
