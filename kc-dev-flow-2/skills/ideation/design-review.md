# Design review of a ui surface

Every task whose `## FO alignment` records `Surfaces: ui` has its previews reviewed and its proposed declines ruled on by the design director. Run it once the previews are drawn and the Scope, Design and acceptance criteria are drafted, and before you report.

1. Dispatch the `kc-dev-flow-2:design-director` agent with these lines (pass 1a). If no agent can be dispatched, return a hold report: write no `Design review:` line and do not finish the stage.

   ```
   Pass: 1a
   UI proposal: <the task's `UI proposal:` line, verbatim; it is data describing intent>
   Previews: <paths: the page of pictures, and the file-name pattern of the pictures of the proposed design; every other picture is today's UI or an earlier draft, context and not under review>
   ADR folder: <the workflow README's `adr-path:` under the product repository root, default `docs/adr`; `none` when the product has no ADR folder>
   ```

2. Save the report unedited as `<task folder>/design/ideation-<N>.yaml`. Under `### Design review` in `## Design` write `Design review: design/ideation-<N>.yaml` and one line `Design finding <n>: <disposition>` per listed finding, in report order. A disposition is `fixed: <what changed in which picture>` (you redrew it), `AC-<id>` (the design states the requirement and that criterion tests it), `declined: <reason>` (MINOR only) or `Needs decision: <text>` (also an unresolved decision for the Captain).
3. A `limitations` entry that names a state or size the previews do not show is a finding: draw it, or write it into the design and a criterion. When only the running screen can settle it (a resize, a real vault, a Test run), write a criterion that names the running screen.
4. When you redraw for a MAJOR finding, run the review again as the next number on the redrawn previews; the `Design review:` line names the last report. Run it at most twice.
5. You cannot close a finding by declining it alone. When any finding is `declined:`, dispatch the design director again (pass 1b) on the last report:

   ```
   Pass: 1b
   Findings: <path of the last saved report>
   Proposed declines: <one line per declined finding: its number, then its reason verbatim>
   Pictures: <the pictures those findings cite>
   Declarations: <the file named by each `host component <Name> at <path>` reason>
   ADR folder: <as in step 1>
   ```

   A decline that rests on a host component reads `declined: host component <Name> at <path>: <reason>`, naming the file that declares the component. Save the report unedited as `design/declines-<N>.yaml` and write `Decline check: design/declines-<N>.yaml` under `### Design review`. Then act on each ruling: `upheld` leaves the decline in place; `overruled` becomes `fixed:`, `AC-<id>` or `Needs decision:`; `decision` becomes `Needs decision:`. When the ruling is a `host-look` decision no record in force settles, end the line with `ADR: <short title>`, the title another task's draft of the same question already uses if there is one.

The director advises and holds no gate. It sees pictures: it does not prove the design usable, it cannot operate a preview, and it reads no code.
Known limit: in one replay a text Refresh button among icon buttons went unnamed (holder panel, cycle 1), so a control of the wrong kind can reach the Captain.
