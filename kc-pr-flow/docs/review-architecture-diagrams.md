# Optional Architecture Diagrams in PR Reviews

`kc-pr-review` can generate two Mermaid diagrams after the normal review draft is complete:

1. A runtime sequence diagram showing how the reviewed behavior executes.
2. An architecture and implementation-status flowchart separating current implementation,
   active findings, product decisions, and explicitly documented future work.

The feature is useful for cross-layer or architecture-heavy PRs. It is opt-in so routine reviews
stay concise.

## Use the option

At the normal confirmation gate, options 1–4 retain their existing meanings. Select `D` to generate
and preview the diagrams:

```text
1. Post inline comments only
2. Post inline comments + advisory
3. Edit review
4. Cancel
D. Generate and preview two architecture diagrams (does not post)
```

Generation is read-only. After both diagrams are visible, choose whether to keep them private or
attach them to the GitHub review body:

```text
5. Post current review + both previewed diagrams
6. Post current review + advisory + both previewed diagrams
7. Edit or regenerate diagrams
```

Options 5 and 6 always attach the pair. Editing either diagram returns to preview before posting.
Before preview and again before posting, `review-architecture-diagrams-validate.sh` validates the
exact generated pair. It fails closed unless the file contains exactly one sequence diagram and one
flowchart using the documented safe grammar and size limits.

## Read the status colors

| Color | Meaning |
|---|---|
| Green | Implemented and verified at the exact reviewed head |
| Red | Active CODE finding, mapped to an inline review item |
| Amber | Author claim, product decision, or unverified contract |
| Gray | Explicitly documented future work or work outside the PR |
| Blue | Neutral architecture needed to understand the path |

The diagrams never change the review event or finding classification. If diagram construction
reveals a possible new issue, the reviewer returns to the normal finding verification flow before
regenerating them.

## Evidence and freshness

Every node and relationship must trace to current-head code, tests or probes, the PR description,
or a linked issue. Author claims and reviewer inferences remain visibly separate from verified
implementation. Unsupported future architecture and speculative completion percentages are not
included.

The preview records the full 40-character PR head SHA. If the author pushes again, both diagrams
become stale along with the review draft and must be regenerated after the unseen delta or rewritten
head is reviewed.

## Safety and readability

PR text and code are untrusted inputs. Diagram labels are concise reviewer-authored summaries, not
copied PR text. Mermaid output excludes executable directives, external links, raw HTML, scripts,
images, and initialization overrides.

The sequence diagram is capped at 10 participants and 20 messages. The flowchart is capped at 30
nodes. Larger designs are collapsed into meaningful layers rather than split into extra diagrams.

For the agent-facing evidence ledger, templates, and assembly contract, see
[`reference/review-architecture-diagrams.md`](../reference/review-architecture-diagrams.md).
