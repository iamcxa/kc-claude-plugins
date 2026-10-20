---
title: The kc-dev-flow-2 workflow template says commissioned-by spacedock@, so Spacedock discovery, refit and Compass see dev2 workflows
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:commissioned-by-names-spacedock:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:commissioned-by-names-spacedock-backlog-1
              briefing:
                id: briefing:commissioned-by-names-spacedock:backlog:attempt-1:revision-1
                digest: sha256:0b6e4f741ab8074c0515b6e1e71bf2110a08ee04e0753839968d3d418c79ff48
                room-ref: ./commissioned-by-names-spacedock/review/backlog/briefing-1
---

## Scope

- Source: the Captain, 2026-10-20 (「要，改」), answering FO's question on whether to file and schedule this for the next batch.
- Bite (read 2026-10-20 at spacedock 0.27.0 and kc-dev-flow-2 origin/main ad44f0cb): `kc-dev-flow-2/references/sd/workflow.md` line 2 and this repository's `docs/dev2/README.md` and `docs/dev2-poc/README.md` say `commissioned-by: kc-dev-flow-2` (since c8342ccc, #459, 2026-09-16; no ADR names it). Spacedock recognises a workflow only when the value starts with `spacedock@`: `internal/status/discover_walkup.go` DiscoverWorkflowDir, `internal/status/handlers.go` discoverWorkflows, and the state-checkout hint in `internal/status/native_runner.go`; `docs/schema/workflow-readme.mdschema.yml` requires `^spacedock@([0-9]+\.[0-9]+\.[0-9]+)?$`; `skills/refit/SKILL.md` reads and rewrites that stamp. So auto-discovery, workflow listing, refit's version read and the Compass dashboard drop these workflows; FO works only because every command passes `--workflow-dir`. No kc-dev-flow-2 script reads the value (test fixtures only). subspace-relay, subspace-web and qnow already carry `commissioned-by: spacedock@0.27.0`.
- Consumer: the Captain (Compass shows the dev2 stage strip) and any FO or tool that discovers workflows without `--workflow-dir`.
- Open at ideation: whether any test pins the template's exact frontmatter line (not verified); which spacedock version the template names and how refit keeps it current.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain asked for the change.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: the dev2 workflows of this repository appear in Compass and in Spacedock workflow discovery.
