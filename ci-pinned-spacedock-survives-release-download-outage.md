---
title: CI's pinned Spacedock install survives a GitHub release-download outage
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: FO, from repeated bites on 2026-11-08 and 2026-11-09; no Captain words yet; the backlog gate is his.
- Bite (gh run view --log-failed, FO 2026-11-08 and 2026-11-09): the pinned Spacedock install in iamcxa/kc-claude-plugins CI downloads `spacedock_0.27.2_linux_amd64.tar.gz` from github.com releases with curl and failed with HTTP 504 on runs 42464643158 (twice), 42468880068, 42468880154 and 42468880263 (three attempts each) for PR #812, and on run 42579057014 (three attempts) for PR #818, blocking a required check while the code under test passed; the same URL returned 504 locally at 2026-11-08 10:2x UTC and 200 an hour later.
- Upstream first: the install steps in `.github/workflows/kc-dev-flow-2-tests.yml` and the marketplace version parity workflow; the existing SHA256 pin stays.
- Non-goals: changing the pinned version; changing Spacedock's release hosting.

## Budget
- One CI-only PR; state its CI cost per PR, measured or marked not measured.

## Stop condition
- A run whose release download fails still installs the pinned, checksum-verified Spacedock (for example from a cache or a retry with backoff), with a falsifier showing the checksum still holds a wrong file.

## FO alignment

Alignment: not needed; CI reliability with recorded bites.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
