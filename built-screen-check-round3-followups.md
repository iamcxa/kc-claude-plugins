---
title: The built-screen check hashes a URL preview and refuses one validation finding named for several MAJORs
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: Codex round 3 on iamcxa/kc-claude-plugins#708 head e033956e (review:5623843736), declined in design-director-runs-ui-design-review's merge ask under workflow.md findings step 5 (from round 3 a finding that is neither Material nor P1 is declined and filed as a new backlog task).
- Findings: comment:4356044042, design_surfaces.py check_built_screen skips an HTTP(S) Preview, so a remote ideation image saved locally passes as the built screenshot (engineering-reviewer-2: 0 of 42 Preview lines in kc-paseo-plugins are URLs, 2026-10-23; fail-closed fix: refuse a built-screen review while any Preview is a URL); comment:4356044048, several MAJOR built-screen findings may name the same F token and pass (two MAJORs fixed by one repair may honestly share one).
- Bite: none observed.
- Non-goals: checking that a screenshot shows the built screen.

## FO alignment

Alignment: not needed before ideation; the findings and their fixes are stated above.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
