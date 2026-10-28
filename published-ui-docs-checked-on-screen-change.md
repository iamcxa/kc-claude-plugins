---
title: Published user docs that describe a ui screen are checked when that screen changes
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the project-env dev2 FO (kc-paseo-plugins, Paseo 8b2c2fc2) relayed the Captain's request 「跟 dev2 fo 講這個需求」 (2026-10-28) as an intake candidate. Relayed words are not a ruling until the Captain confirms them in this session.
- Need: an adopter publishes user docs from repository Markdown (kc-paseo-plugins GitHub Pages; Install and Prepare 1Password pages carry screen words such as "press Change" and seven screenshots retaken by docs/project-env/capture/capture.sh). When the screen changes, no dev2 step checks those words or pictures.
- Bite: none yet. The adopter FO will send the first real staleness event; until then the adopter carries a dispatch line on its ui tasks and walks the pages at release acceptance.
- Upstream first: `scripts/doc_impact.py` catches docs naming changed paths or code identifiers, not UI labels, step wording or screenshots; `extensions/release-acceptance` walks the release, not the docs; e2e-pipeline `e2e-doc-sync` covers that plugin's own docs only.

## Non-goals

- Writing or rewriting user docs; checking docs for screens the task did not change.

## Budget

- One optional extension, or one addition to an existing one; no new script unless the design shows the capture-and-diff cannot reuse the adopter's own capture script.

## Stop condition

- No ideation before the first staleness event arrives as evidence. After it, done when that event replays as caught.

## FO alignment

Alignment: needed before backlog approval; no bite yet, and whether this is an extension or a release-acceptance step is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
