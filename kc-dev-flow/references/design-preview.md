# Design preview

`user_visible_surface_change` is true when the accepted work adds, removes, or
changes something a person sees or operates. Read it from the surface, not from
the diff: a capability change behind an unchanged surface does not fire it, and
a copy-only change does.

## Rules

- **A text proposal first, then a preview of it.** The preview answers the
  proposal; it does not replace one. A preview arriving without a stated
  proposal asks the Captain to reverse-engineer the intent from a picture.
- **Fidelity over prettiness, cheapness over both.** The preview owes position,
  hierarchy, and labelling — where things sit relative to each other and what a
  reader actually sees written. It does not owe production styling. A throwaway
  static page or the real surface served uncommitted are both enough; a mock
  showing a layout the real shell cannot produce is worse than no preview.
- **Use a mechanism the repository already has** and record which one in the
  `design_preview` receipt. This contract names no tool and adds none. A preview
  mechanism built inside kc-dev-flow would be the standing-enforcement last
  resort, and this obligation does not need one.

The gate is not presentable without both the proposal and the preview.

This is the shape-stage counterpart to the `SURFACE:` evidence
`surface-map-check.py` reads at implementation exit: that one grades a surface
after it is built, and this one puts a human in front of it before.
