#!/bin/bash
N='
[2026-10-28 22:05 +08] web FO notice: spacedock-dev/subspace-web #186 merged at b71f912 (2026-10-28 21:58 +08). No acknowledgement requested.'
OLD='
[2026-10-28 09:40 +08] web FO notice: spacedock-dev/subspace-web #186 merged at b71f912. No acknowledgement requested.'
/tmp/cold-fo/run.sh f-absent1 real "" & /tmp/cold-fo/run.sh f-absent2 real "" & /tmp/cold-fo/run.sh f-notice real "$N" & /tmp/cold-fo/run.sh f-delayed real "$OLD" & wait
/tmp/cold-fo/run.sh f-open open "" & /tmp/cold-fo/run.sh f-down1 down "" & /tmp/cold-fo/run.sh f-down2 down "" & /tmp/cold-fo/run.sh f-down3 down "" & wait
