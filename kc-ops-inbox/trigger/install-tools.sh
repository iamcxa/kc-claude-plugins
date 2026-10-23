#!/usr/bin/env bash
# Install the pinned Spacedock binary and Claude Code CLI into $OPS_TOOLS_DIR. The installer is checked against a pinned digest
# before it runs, and it checks the release tarball against the release's checksums.txt itself.
set -euo pipefail
: "${OPS_TOOLS_DIR:?}"
SD_VERSION=0.27.2
SD_INSTALLER_SHA256=1eab590f6c5439458179aaac6806b4f73d9729c293033c8c15f6567dc74d007f
CLAUDE_CODE_VERSION=2.1.303
mkdir -p "$OPS_TOOLS_DIR"
curl -fsSL "https://raw.githubusercontent.com/spacedock-dev/spacedock/v$SD_VERSION/install.sh" -o "$OPS_TOOLS_DIR/spacedock-install.sh"
got=$( (sha256sum "$OPS_TOOLS_DIR/spacedock-install.sh" 2>/dev/null || shasum -a 256 "$OPS_TOOLS_DIR/spacedock-install.sh") | cut -d' ' -f1)
[ "$got" = "$SD_INSTALLER_SHA256" ] || { echo "spacedock installer digest $got differs from the pinned $SD_INSTALLER_SHA256" >&2; exit 1; }
SPACEDOCK_PLUGINS=none SPACEDOCK_INSTALL_DIR="$OPS_TOOLS_DIR/bin" SPACEDOCK_INSTALL_VERSION="$SD_VERSION" \
  SPACEDOCK_INSTALL_FROM="https://github.com/spacedock-dev/spacedock/releases/download/v$SD_VERSION" sh "$OPS_TOOLS_DIR/spacedock-install.sh"
"$OPS_TOOLS_DIR/bin/spacedock" --version
if [ -z "${OPS_SKIP_CLAUDE:-}" ]; then
  npm config set prefix "$OPS_TOOLS_DIR/npm"
  npm install -g "@anthropic-ai/claude-code@$CLAUDE_CODE_VERSION" >/dev/null
  "$OPS_TOOLS_DIR/npm/bin/claude" --version
fi
