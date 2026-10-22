#!/usr/bin/env bash
# AC-4 install check. Usage: install_check.sh <marketplace-root>. Fresh HOME and CODEX_HOME per host.
# Exit 0 only if both hosts list read-adr.
set -u
ROOT="$(cd "$1" && pwd)"
rc=0
H=$(mktemp -d)
echo "== claude (HOME=$H)"
HOME=$H claude plugin marketplace add "$ROOT" >/dev/null 2>&1
HOME=$H claude plugin install kc-adr@kc-claude-plugins >/dev/null 2>&1
out=$(HOME=$H claude plugin details kc-adr 2>&1); echo "$out" | sed -n '1,9p'
echo "$out" | grep -q "Skills (1)  read-adr" || { echo "FAIL claude: details does not list read-adr"; rc=1; }
C=$(mktemp -d); mkdir -p "$C/codex-home" "$C/cwd"
ln -s "$HOME/.codex/auth.json" "$C/codex-home/auth.json"; : > "$C/codex-home/config.toml"
echo "== codex (CODEX_HOME=$C/codex-home)"
export HOME=$C CODEX_HOME=$C/codex-home
codex plugin marketplace add "$ROOT" >/dev/null 2>&1
codex plugin add kc-adr@kc-claude-plugins 2>&1 | tail -2
codex plugin list -m kc-claude-plugins 2>&1 | grep -E "^PLUGIN|kc-adr"
(cd "$C/cwd" && codex debug prompt-input hi 2>&1 | grep -oE 'kc-adr:read-adr: .{0,40}|\(file: r1/kc-adr/[^)]*\)') | tee "$C/skill-line.txt"
[ -s "$C/skill-line.txt" ] || { echo "FAIL codex: prompt input does not list kc-adr:read-adr"; rc=1; }
exit $rc
