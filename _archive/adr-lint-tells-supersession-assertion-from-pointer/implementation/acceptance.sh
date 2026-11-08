#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -B "$here/acceptance.py" "${1:?repo}" "${2:?package}" "${3:?sd-plugin-root}" "${4:?workflow}" "${5:?task}" "${6:?output-directory}"
