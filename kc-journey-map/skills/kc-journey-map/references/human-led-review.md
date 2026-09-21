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
- Added cards follow the existing canvas language unless the human requests translation;
  the conversation's language alone does not change the drawing's language.
- A question can inform a later user story. It is not automatically an actionable
  or user-visible story, a task, or accepted release scope. Create those artifacts
  when the human requests that separate planning step. That step is promotion into
  the journey YAML — see [Stories live in the YAML](#stories-live-in-the-yaml) —
  never a story card drawn onto the review page.
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
If unpublished or inaccessible, visibly label the answer or an adjacent native card
with the document path and chapter plus its unpublished/pending-verification state.
Custom metadata alone is insufficient: the native export must explain the answer's
document reference without a custom viewer. Do not advertise an unverified URL as
working or insert a fabricated working link. Publishing is a separate
action within the user's authority; link verification does not grant push permission.

Evidence links stay pinned to the inspected SHA, including after a documentation
link moves to `main`:

`https://github.com/<owner>/<repo>/blame/<full-sha>/<source-path>#L<start>-L<end>`

Use a native shape URL for the answer, or a native bookmark with its asset record,
so the canonical chapter survives copying/export. Do not use a localhost or transient
preview URL as the technical document's canonical identity.

## Stories live in the YAML

A review board carries Actions and questions. Stories are not drawn onto it: the
journey YAML is their only source, and the story-map page is its rendering. A story
drawn onto the review page would be a second copy with no rule for which one wins.

**Every Story owes at least one Question. A Question owes no Story.** The asymmetry
is deliberate. Questions do surface missing stories, so a Story with no Question and
an Activity with no Story are both worth reporting. But mechanism questions — "what
if the store reports a write it did not make" — name no actor and are not
user-visible; they belong under other questions as subquestions, and a Story invented
above one would invent an actor with it.

**Promotion** moves a question's finding into the story spine. It requires explicit
authorization for the named question, and all three of: it names an actor; it is
user-visible; removing it would remove something the user can do. Write the story
into the journey YAML, then re-render the story-map page alone.

**Re-rendering must preserve what it did not generate.** A story-map page usually
carries human shapes added on top of the generated ones, without journey metadata.
Compare the page's records before and after and confirm every non-generated shape
survived; a successful render is not that proof. Without this check, promotion
silently deletes the human's work.

**Coverage is a drift report, both directions**: activities and stories in the YAML
against Actions and questions on the board. Report it in conversation. Adding cards
for what it finds still needs the human, under the existing rule against unsolicited
question cards.

## Questions go forward into the YAML

Promotion moves a finding backward, from a board question into the story spine.
The forward direction is its twin: before a named release is built, each of its
stories carries the design questions that have to be settled first.

On explicit authorization for a named release, write each story's open design
question into that story's `questions:` list. A question the human asked on a
review board stays the human's, in their wording; the rest are the agent's
proposals. Same authorization shape as promotion — a named scope, never a blanket
fill of every silent story.

**A story may not reach `status: exists` while it carries an open question.** That
is the convergence rule, and it is a lint rather than an intention. Without it a
forward board fills with question cards that look like progress and are never
closed — the failure the rule against unsolicited question cards already prevents,
arriving through the front door instead.

The design pass is finite: it ends when no story in the release is silent, each
carrying a settled question or a `deferred` one with its reason. Questions raised
later, while building, are the mechanism ones and cannot be predicted; each is
answered with pinned evidence in the same round or deferred with a named reason.

## Incremental canvas work

Use [canvas.md](canvas.md) for applicable service lifecycle and sizing mechanics.
In this mode, the native drawing preserves human layout and question ownership;
technical documents own design meaning. Never regenerate the review drawing from
YAML. Do not apply story-status lints or release handoff requirements to it, force
standard boards, or convert the human's questions into stories unasked. An
authorized promotion re-renders the story-map page only, under
[Stories live in the YAML](#stories-live-in-the-yaml).

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
