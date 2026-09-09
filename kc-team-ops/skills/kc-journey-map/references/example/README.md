# The worked example, as a board

`draw-a-journey.tldr` is the example journey rendered onto all five of its pages, in
tldraw's own file format. It is here so the boards can be looked at without running
anything, and opened without this plugin at all.

Two ways in.

**Without the canvas** — drag the file onto [tldraw.com](https://tldraw.com), or open it in
the tldraw desktop app. Everything renders; nothing round-trips, because the journey file
is what round-trips and it is not in here.

**With the canvas** — import it into a room, then read it back against the file it came
from:

```bash
npm install && npm run canvas          # from the plugin directory
node lib/journey-tldr.mjs import skills/kc-journey-map/references/example/draw-a-journey.tldr demo
open "http://localhost:3737/?room=demo"
node lib/journey-read.mjs skills/kc-journey-map/references/example/journey.example.yaml demo
```

The read reports no drift, because the board was rendered from that file. Move a card and
run it again to see what it catches.

**Import replaces the whole target document.** Use a room name nothing else is using.

## What is in it

| Page | Shows |
|---|---|
| Story map | the backbone, its stories, and three release bands |
| RELEASE 1/2/3 — what is missing | one journey board per release, scoped to the steps that release touches |
| Function map | Command, Event, State and Read model over the same columns |

Regenerate it after changing the example:

```bash
node lib/journey-render.mjs skills/kc-journey-map/references/journey.example.yaml draw-a-journey
node lib/journey-tldr.mjs export draw-a-journey skills/kc-journey-map/references/example/draw-a-journey.tldr
```
