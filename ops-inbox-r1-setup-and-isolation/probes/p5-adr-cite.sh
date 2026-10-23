#!/usr/bin/env bash
# P5: kc-adr read-adr step 1 on the project repo, then a machine check of each citation block. Read-only git.
set -u
R=$1; C=$(git -C "$R" rev-parse "$2"); echo "repo: $(git -C "$R" remote get-url origin)"; echo "pinned commit: $C"
echo "ADR files at commit: $(git -C "$R" ls-tree --name-only "$C" docs/adr/ | grep -c '/[0-9]\{4\}-')"
status() { git -C "$R" show "$C:$1" | awk '/^## Status/{f=1;next} f&&NF{print;exit}'; }
digest() { git -C "$R" show "$C:$1" | shasum -a 256 | cut -d' ' -f1; }
echo "-- titles matching the event's terms (ceiling|quota|limit|refus|telemetry), the stand-in for the FO's choice:"
git -C "$R" ls-tree --name-only "$C" docs/adr/ | grep -E 'ceiling|quota|limit|refus|telemetry' | while read -r p; do
  printf '%s | status=%s | sha256:%s\n' "$p" "$(status "$p")" "$(digest "$p")"; done
echo "-- citation check (what ops-gate or validation would run on the FO's record):"
check() { # path commit digest
  git -C "$R" cat-file -e "$2^{commit}" 2>/dev/null || { echo "REFUSE commit-missing $1"; return; }
  git -C "$R" cat-file -e "$2:$1" 2>/dev/null || { echo "REFUSE path-missing $1"; return; }
  local d; d=$(git -C "$R" show "$2:$1" | shasum -a 256 | cut -d' ' -f1); [ "$d" = "$3" ] || { echo "REFUSE digest-mismatch $1"; return; }
  local s; s=$(git -C "$R" show "$2:$1" | awk '/^## Status/{f=1;next} f&&NF{print;exit}'); [ "$s" = Accepted ] || { echo "REFUSE not-in-force($s) $1"; return; }
  echo "OK $1"; }
P=docs/adr/0060-the-signed-in-tier-has-its-own-exact-site-wide-daily-ceiling.md; D=$(digest $P)
check $P $C $D
check $P $C 0000000000000000000000000000000000000000000000000000000000000000
check docs/adr/0099-relay-has-no-ceiling.md $C $D
check $P 1111111111111111111111111111111111111111 $D
SUP=$(git -C "$R" ls-tree --name-only "$C" docs/adr/ | while read -r p; do s=$(status "$p"); case "$s" in Superseded*) echo "$p"; break;; esac; done)
[ -n "$SUP" ] && check "$SUP" $C "$(digest "$SUP")" || echo "no Superseded ADR at this commit"
