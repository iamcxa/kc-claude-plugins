# Intake from the kc-paseo-plugins dev2 FO, 2026-10-22 (relayed, not a ruling)

From Paseo agent 8b2c2fc2 (kc-paseo-plugins dev2 FO), on release r1.5 of project-env, kc-dev-flow-2 0.26.0. Its quotes of the Captain are relayed, not rulings in this session.

Gap: a per-task ui design review cannot catch whole-screen UX failures. Six r1.5 tasks each changed one part of the same settings screen; each followed skills/ideation/design-review.md; all gates and validations passed. After merge the Captain used the screen and ruled (relayed) 「這個 UX 完全不行，我按 broswe 沒料到居然是已經輸入的值可以變成選取的，應該進挑惕設計總監視角」. A fresh whole-screen design-director pass that operated an isolated Paseo (not pictures) found four blocking problems: a button that silently switched every row's control mode; truncated references that hid a wrong mapping; a resize that discarded unsaved edits; a flat raw-path picker.

Why the method missed them, as the peer reads it:
1. Each review sees only its task's previews; a cross-part interaction (Browse in one card changing rows in another) belongs to no task.
2. design-review.md says the reviewer "sees pictures: it does not prove the design usable, it cannot operate a preview".
3. The designer dispositions its own findings; most were declined as MINOR.
4. The ideation gate presentation was text only; the Captain saw no screenshot before using the merged screen. README ideation Gate content requires "each recorded Surfaces: value's artifact" but nothing makes FO show pictures to the Captain.
5. Validation checked logic and copy, not the merged screen.

Peer suggestions (not approved scope):
- When two or more tasks in one release record `Surfaces: ui` on the same screen, one whole-screen, operated design review at release level before the first ideation gate, and again on the merged candidate before release acceptance.
- Ideation and validation gate presentations for ui tasks show the Captain screenshots, not only text.
- Previews show the whole page around the change, at desktop and narrow widths.

Evidence named by the peer: /Users/kent/Project/kc-paseo-plugins/docs/dev2/.spacedock-state/ux-review-r1.5/ (index.html, direction-a*.html, shots/); PRs iamcxa/kc-paseo-plugins#15 to #21.
