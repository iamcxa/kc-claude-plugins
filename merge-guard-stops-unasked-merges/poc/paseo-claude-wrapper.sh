#!/bin/bash
# Paseo launches "claude --agent spacedock:first-officer <paseo flags>"; drop the agent,
# load only the throwaway folder's project settings, keep every other Paseo flag.
T=/tmp/merge-guard-poc-paseo
out=()
skip=0
for a in "$@"; do
  if [ $skip = 1 ]; then skip=0; continue; fi
  case "$a" in
    --agent) skip=1 ;;
    --setting-sources=*) out+=("--setting-sources=project") ;;
    *) out+=("$a") ;;
  esac
done
printf '%s\n' "$(date -u +%FT%TZ)" "${out[@]}" | sed -E 's/"Authorization":"[^"]*"/"Authorization":"<redacted>"/' > "$T/wrapper-argv.txt"
exec /Users/kent/.local/bin/claude "${out[@]}"
