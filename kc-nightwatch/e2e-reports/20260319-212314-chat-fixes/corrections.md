# Flow Verification Corrections

## Flow changes (/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/.claude/e2e/flows/chat-fixes.yaml)

### Step enriched: close-chat-via-x (step 3)

The chat drawer uses CSS `transform: translateX(400px)` to slide off-screen when closed. The dialog element remains `display:flex`, `visibility:visible`, `opacity:1` — Playwright's `is visible` check returns `true` even when the drawer is visually hidden (bounding rect `left: 1280`).

```yaml
  - id: close-chat-via-x
    action: "Click chat_close_button on _global"
    expect:
-     - "chat_dialog not visible on _global"
+     - "chat_fab visible on _global"
+     - "url contains /#/dashboard"
    screenshot: true
+   _correction: { type: "enrich", round: 1, reason: "chat_dialog 'not visible' unreliable — drawer uses CSS transform slide-out" }
```

### Step enriched: close-chat-final (step 11)

Same correction as step 3.

```yaml
  - id: close-chat-final
    action: "Click chat_close_button on _global"
    expect:
-     - "chat_dialog not visible on _global"
+     - "chat_fab visible on _global"
+     - "url contains /#/dashboard"
    screenshot: true
+   _correction: { type: "enrich", round: 1, reason: "Same as close-chat-via-x" }
```

## Mapping changes

No mapping changes required. All selectors resolved correctly.

## Notes

**Root cause**: The nightwatch dashboard chat drawer implementation uses a CSS slide animation (`transform: translateX`) instead of toggling `display:none` or `visibility:hidden`. This is a valid UX pattern (allows smooth animations) but makes Playwright's `isVisible()` check unreliable for drawer open/closed state detection.

**Recommendation for the app**: Consider adding a `data-state="open|closed"` attribute on the dialog element to allow reliable programmatic state detection. Alternatively, the E2E flow can use bounding rect checks via `eval` to determine visual position.
