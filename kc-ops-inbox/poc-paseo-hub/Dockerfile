FROM ghcr.io/getpaseo/paseo@sha256:9832cb6bcc904bb7fd6c0b22f1880cde38b592a26ecd38ba66c7fcc76fa0d43e

USER root
ARG CLAUDE_CODE_VERSION=2.1.303
ARG SD_VERSION=0.27.2
ARG SD_INSTALLER_SHA256=1eab590f6c5439458179aaac6806b4f73d9729c293033c8c15f6567dc74d007f

RUN apt-get update && apt-get install -y --no-install-recommends gh && rm -rf /var/lib/apt/lists/*
RUN npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"
RUN set -eux; \
    curl -fsSL "https://raw.githubusercontent.com/spacedock-dev/spacedock/v${SD_VERSION}/install.sh" -o /tmp/sd-install.sh; \
    echo "${SD_INSTALLER_SHA256}  /tmp/sd-install.sh" | sha256sum -c -; \
    SPACEDOCK_PLUGINS=none SPACEDOCK_INSTALL_DIR=/usr/local/bin SPACEDOCK_INSTALL_VERSION="${SD_VERSION}" \
      SPACEDOCK_INSTALL_FROM="https://github.com/spacedock-dev/spacedock/releases/download/v${SD_VERSION}" sh /tmp/sd-install.sh; \
    rm /tmp/sd-install.sh; \
    spacedock --version
