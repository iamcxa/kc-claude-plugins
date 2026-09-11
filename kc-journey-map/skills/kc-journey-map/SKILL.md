---
name: kc-journey-map
description: Plan a user journey as an editable story map with horizontal value release bands and YAML readback.
---

# KC Journey Map

Plan a user journey as an editable story map with horizontal value release bands and YAML readback.

Read [canvas setup and portability](references/canvas.md) before starting.

## Plan and read back a story map

Keep journey intent in a YAML file. Start with
[the example](references/journey.example.yaml) and follow
[the planning contract](references/cell-contract.md). From the plugin directory:

```bash
node lib/journey-render.mjs skills/kc-journey-map/references/journey.example.yaml my-map
node lib/journey-read.mjs skills/kc-journey-map/references/journey.example.yaml my-map
node lib/journey-read.mjs skills/kc-journey-map/references/journey.example.yaml my-map --out /tmp/reviewed-journey.yaml
```

Review the reported changes before applying them. `--write` applies supported edits
to the original file. Drawing by hand is supported; unclaimed cards are reported
for a person to decide, not silently added to YAML.
