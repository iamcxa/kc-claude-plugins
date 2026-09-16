# Human-led architecture review

Use this mode when the human draws the journey and directs its architecture
questions. These are shared Claude and Codex instructions. The agent follows the
human's drawing; technical documents remain the source of truth for the design.
These are operator instructions, not runtime enforcement or a new renderer.

## Meaning and ownership

- The first layer contains human-drawn Actions, which are green in this convention.
  Green identifies the Action role; it says nothing about completion, implementation,
  deployment or acceptance. Preserve existing human colors unless asked to change them.
- Human questions form the next layer. A question may have nested subquestions.
  Preserve its wording, hierarchy, geometry, layout and existing arrows.
- A question can inform a later user story. It is not automatically an actionable
  or user-visible story, a task, or accepted release scope. Create those artifacts
  when the human requests that separate planning step.
- Answer one selected question per turn, then wait for human feedback. Explicit
  batch permission applies to the specified questions; it does not authorize filling
  every remaining card. If no question is selected and the intent is ambiguous,
  ask which one to answer. Suggest new questions in conversation, without adding
  unsolicited question cards to the canvas.

## Resolve the contract before the evidence

Read the selected question and its surrounding action/subquestions, then locate
the owning technical document in the consuming repository's architecture context.

| What is found | Next action |
|---|---|
| An adequate existing chapter | Cite that chapter and answer from its contract, then inspect implementation evidence. |
| Missing or unclear documentation for a settled design | Author or refactor the relevant owning chapter within the authorized scope; keep the technical detail there. Reuse the document structure rather than requiring a new document per question. |
| An undecided design, ambiguous authority, or disagreement between documentation and code | Present the discrepancy and the explicit decision needed in conversation. Do not silently turn current code into the intended contract or rewrite the contract to match it. |

Keep a review-branch document visibly under review; authoring it does not make its
design accepted. Follow the consuming repository's documentation and review rules.
If doc work needs a decision outside the request, report the missing decision and
keep the answer provisional. Unavailable evidence means unverified, not implemented.

Create a short **native rectangle** answer connected to the exact question with a
native bound connector. Use a stable shape identity, not proximity, to identify the
question, especially when labels repeat. Fit the answer to the rectangle; put the
full explanation in the technical chapter. Keep evidence as a separate layer beneath
the answer, rather than blending observed code into the normative answer.

The evidence layer records the inspected repository and full commit SHA, paths and
relevant line ranges, and links to GitHub blame at that SHA. Inspect those lines and
their blame before citing them; also inspect the applicable caller/route when the
claim depends on reachability. Label what the source supports and what remains
unverified. Source inspection alone does not prove deployment, target-user usability
or human acceptance. Cite each repository separately for cross-repository behavior.

## Document and evidence links

The answer links to the **exact technical-document chapter on canonical GitHub**:

`https://github.com/<owner>/<repo>/blob/<review-branch-or-main>/<doc-path>#<chapter>`

Use the review branch while the document is under review. After merge, inspect the
published chapter on `main` and then update the document link. Verify the remote
content and actual heading anchor before advertising the link as usable; a locally
present file, guessed anchor or successful request for the file alone is insufficient.
If unpublished or inaccessible, state that limit and identify the local path/heading
as unpublished. Do not insert a fabricated working link. Publishing is a separate
action within the user's authority; link verification does not grant push permission.

Evidence links stay pinned to the inspected SHA, including after a documentation
link moves to `main`:

`https://github.com/<owner>/<repo>/blame/<full-sha>/<source-path>#L<start>-L<end>`

Use a native shape URL for the answer, or a native bookmark with its asset record,
so the canonical chapter survives copying/export. Do not use a localhost or transient
preview URL as the technical document's canonical identity.

## Incremental canvas work

Use [canvas.md](canvas.md) for applicable service lifecycle and sizing mechanics.
In this mode, the native drawing preserves human layout and question ownership;
technical documents own design meaning. Do not regenerate it from YAML, apply
story-status lints or release handoff requirements, force standard boards, or run
generated-map readback to convert the human's questions into stories.

1. Read a fresh native snapshot before each incremental patch. Identify the selected
   question, its page/parent, nearby records and existing bindings. Back up that
   snapshot before writing. A screenshot helps visual context but cannot prove shape
   identity or bindings; if native access is unavailable, provide a proposed answer
   and report the canvas update as pending.
2. Patch the selected answer, connector and evidence records only, retaining unrelated
   records and human text, positions, sizes, styles, hierarchy and arrows. Use native
   APIs or supported record constructors. Preserve IDs and parents for existing
   records; add bindings for both connector endpoints instead of drawing an unbound
   line. If the canvas changed after the read, refresh and reconcile the small patch
   against current state. Do not restore an old full snapshot over concurrent edits.
3. Read back the changed records and visually inspect the edited region. Confirm text
   fits, connectors attach to the intended question/answer, and nothing covers or moves
   the human's work. A successful API response does not verify the drawing.
4. Export the touched question/answer/evidence with required parents, bindings and
   assets as a portable native `.tldraw` file (the bundled exporter uses `.tldr`).
   Inspect the export and open it in a disposable native canvas, preserving the live
   room. Confirm editable native shapes, both connector endpoints, canonical URLs,
   and any bookmark asset survive. Report separately if visual or export verification
   is unavailable; do not claim that unperformed verification passed.

Report the answer/document/evidence limits and the canvas/export result briefly.
Wait for feedback before the next question. Existing map, check, release-planning
and sequence modes retain their own contracts when the user selects them.

## Compatibility with a future document viewer

A future optional popup may render the linked Markdown chapter and its Mermaid
diagrams without losing the canvas context. Closing it returns focus to the originating
card and preserves the canvas viewport. This is deferred compatibility guidance, not
an implemented capability or a request to build a viewer. The canonical source link
must remain available when the popup is absent, including an external-open fallback
and portable export. Technical documents retain authority; this mode prescribes no
renderer architecture or alternative document store.

For behavioral validation of skill changes, use
[human-led-review-evals.md](human-led-review-evals.md).
