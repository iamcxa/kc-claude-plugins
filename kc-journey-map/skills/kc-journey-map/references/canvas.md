# Use the editable canvas

From the installed `kc-journey-map` directory, run `npm ci`, then `npm run canvas`.
Node 22.13.0 or later is required. `npm run doctor` checks dependencies and the
API/client ports 5858 and 3737. Open `http://localhost:3737/?room=my-map` and draw
notes, shapes, frames, and text. Reopen the same room URL to resume editing.
Room databases live in `.rooms/` (override with `JOURNEY_ROOMS_DIR`); retain them
until you have exported a backup. The server binds its API to loopback; the Vite
client is a local development UI. Image uploads have no asset storage.

## Export and import

The CLI export commands require `agent-browser` on PATH. Run them from the plugin
directory while the canvas is running:

```bash
node lib/journey-tldr.mjs export my-map /tmp/my-map.tldr
node lib/journey-tldr.mjs import /tmp/my-map.tldr imported-map
node lib/journey-export.mjs my-map /tmp/my-map.png
```

The `.tldr` file carries editable records and metadata. Import replaces the entire
target room, so choose a new room or export its current contents first. PNG export
captures the shapes' bounds; it is a picture, not an editable backup. Check native
persistence and the document API with `bash scripts/canvas-smoke.sh`.
