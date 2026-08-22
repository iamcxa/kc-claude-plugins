# Multi-slice guard

`multi_slice_required` is true only when a Pilot or Production shape cannot
deliver its accepted journey as one integrated slice. POC does not use this
reference: recut the experiment to one runnable journey or ask for a different
profile.

## Rules

- Use at most two slices. If a piece can be blocked independently, it is another
  work item rather than a slice.
- Land and demo the first slice before finishing the second. Name the demo in
  advance.
- A slice must change observable behavior. Scaffolding is permitted only for a
  named sibling that will make it reachable.
- A walking skeleton may cross temporary ownership boundaries, but it records
  every fake, stub, hardcode, fixed value, and skipped validation in one shortcut
  inventory. The inventory is the shape-stage form of the shared core's
  scaffolding rule, so each entry names the work item that removes the shortcut
  and the concrete condition that makes it removable.

## Shape receipt

Record the result in the existing work item:

```yaml
journey_slices:
  demo: <first-slice observable journey>
  slices:
    - <slice one and its stop condition>
    - <optional slice two and its stop condition>
  shortcut_inventory:
    - shortcut: <temporary compromise>
      owner: <work item that removes it>
      removal_condition: <observable condition that makes it removable>
```

A body that declares more than two slices, unnamed scaffolding, a walking
skeleton without a shortcut inventory, or an inventory entry with no removal
condition fails shape before implementation.
