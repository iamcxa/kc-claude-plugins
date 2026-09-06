#!/usr/bin/env bash
set -eu
# Only the three owned synthetic child commands are permitted in this local proof.
case "${1:-}" in
  normal) child='exit 0' ;;
  nonzero) child='exit 7' ;;
  timeout) child='kill -TERM $$' ;;
  *) exit 64 ;;
esac
if /bin/bash -c "$child"; then
  observed_exit=0
else
  observed_exit=$?
fi
printf 'EXIT=%s\n' "$observed_exit"
exit "$observed_exit"
