# Fictional book-pickup example

[../journey.example.yaml](../journey.example.yaml) is a short illustrative model,
not this plugin's product plan or an implemented library service. Its five stories
are all `unverified`; commands, events, state and read models describe authored intent.
[book-pickup.tldr](book-pickup.tldr) is the matching native editable snapshot with four
pages: Story map, two release boards and Function map.

Open the snapshot in tldraw, or import it into the plugin canvas. Follow
[canvas setup and lifecycle guidance](../canvas.md) to reuse a suitable service or
start one when needed. From the plugin directory, choose an unused room name:

```bash
node lib/journey-tldr.mjs import skills/kc-journey-map/references/example/book-pickup.tldr book-pickup-fresh
open "http://localhost:3737/?room=book-pickup-fresh"
node lib/journey-read.mjs skills/kc-journey-map/references/journey.example.yaml book-pickup-fresh
```

Import replaces the target document. A fresh import should report no drift; after
editing a supported story card, read back its changes before redrawing.

When deliberately updating this packaged snapshot, select all projections:

```bash
node lib/journey-render.mjs skills/kc-journey-map/references/journey.example.yaml book-pickup-fresh --pages story-map,journey-board,function-map
node lib/journey-tldr.mjs export book-pickup-fresh skills/kc-journey-map/references/example/book-pickup.tldr
```

YAML remains the source; a native snapshot is optional for ordinary journey updates.
See [canvas portability](../canvas.md) for native geometry and readback limits.
