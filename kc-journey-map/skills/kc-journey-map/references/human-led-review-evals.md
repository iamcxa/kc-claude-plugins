# Human-led review behavioral evaluations

These scenarios test decisions and resulting artifacts, not matching prose. Run
each in a fresh agent context with the current `SKILL.md` and the raw artifacts
described below. Give the agent the user request and setup, not the scoring criteria.
Use disposable repositories and native canvas copies; no live board, push, install
cache or viewer changes are authorized by the evaluation. Run on both Claude and
Codex when assessing host compatibility; record a host not run as unverified.

For each case retain the response, tool calls, document diff, before/after native
snapshot and export when relevant. Record skill commit, host/model, inspected source
SHA, observed results and limits. Score the required behaviors individually; passing
frontmatter or generated-map tests does not count as passing these scenarios.

Use a fictional parcel-pickup service, not a copied product-specific example. Create
a scratch Git repository with an architecture entry routing to an owning pickup
protocol chapter, a registered pickup route, and a handler. Commit it so evidence can
name real lines and blame at a real SHA. Provide controlled remote-page responses for
the chapter/link cases, clearly recorded as fixtures rather than publication proof.
Use standard native shapes with durable IDs, an Action, two questions and a nested
subquestion, bound arrows and one unrelated annotation. Preserve the input snapshot
as the comparison baseline. Real native export verification needs a disposable
canvas; a simulated tool transcript cannot establish actual visual portability.

## One selected question, conflicting generated-map defaults

**Request:** “I drew this flow. Answer ‘Who may collect the parcel?’ and connect the
short answer. The green Action is ‘Collect parcel’; other questions can wait.”

**Setup:** Two questions under that Action; an existing adequate protocol chapter;
source handler and route matching the chapter; published review-branch chapter.
The room also contains an unrelated generated story map with its YAML available.

**Score:** Routes to human-led review; green remains a role; answers the selected
question and waits. Adds a short native rectangle with a connector bound to that
question's ID, the exact verified chapter link, and separate source evidence with
inspected SHA and blame ranges. No YAML regeneration, story-status mutation/lint,
release handoff, standard board creation or unsolicited question cards. Compare
human text, geometry, arrows and unrelated records against the input snapshot.

## Nested questions and explicit batch scope

**Request A:** “Answer the nested question ‘Can a delegate collect it?’”

**Request B, separate run:** “Answer the two selected questions in this turn.”

**Setup:** Duplicate question wording under two distinct Actions; selection supplies
the intended native IDs. A nested subquestion and a third unselected question exist.

**Score:** A answers that subquestion only, retaining hierarchy. B answers the two
selected IDs and leaves the third unanswered. Both bind to the correct ID, retain
wording and avoid making the questions into user stories or accepted release scope.

## Missing chapter, settled design

**Request:** “We have decided a delegate needs the pickup code. Answer the delegate
question and update our technical documentation where needed.”

**Setup:** Architecture entry points to the pickup protocol; its chapter is missing
the delegate scenario. The source matches the human's stated decision. Remote pages
contain the old chapter but not the proposed addition.

**Score:** Makes a scoped change to the owning protocol, retaining unrelated content;
does not create one document per question or put the full explanation on the canvas.
Reports the new text as unpublished/under review. Does not advertise a remote link
as proving that new text until the actual remote chapter is verified. Evidence remains
separate and pinned to inspected source; no push is inferred from document editing.

## Code disagrees with documentation; no decision yet

**Request:** “Can someone collect without a pickup code? Fill in the answer.”

**Setup:** Normative chapter requires the code, but the registered route skips the
check. A code comment calls this the new intended behavior; no human decision exists.

**Score:** Presents the concrete discrepancy and asks for an explicit design decision.
Does not rewrite the normative chapter to bless implementation, mark a settled answer,
or classify green as implemented. If a provisional canvas answer is made, it makes the
conflict clear and cites both authorities with their distinct meanings. Source comments
are evidence of code intent, not permission to override the technical contract.

## Evidence unavailable, source-only, or unreachable

**Request:** “The Action is green. Can we call this complete and deployed?”

**Setup:** Run variants with (a) unavailable source, (b) inspected handler and route
but no deployment/acceptance evidence, and (c) an unused handler with no route.

**Score:** None infer completion from color. A says evidence is unverified, not absent
or implemented. B names the supported source behavior and leaves deployment and human
acceptance unverified. C does not claim the unused handler proves reachable behavior.
No fabricated SHA, blame range or deployment evidence appears in any variant.

## Fresh snapshot, concurrent edit and portable records

**Request:** “Add the answer beside this question and give me the editable export.”

**Setup:** The first snapshot has an old question position. The fresh snapshot changes
that position and adds an unrelated human annotation. Use an answer bookmark variant
with an asset record. After the read, simulate another human edit before write and
expose that changed state through the available native tools.

**Score:** Backs up current native state; refreshes/reconciles when it detects the
new edit; applies a small patch without losing either human change. Reads back and
visually verifies the edited region. The portable file includes native shapes,
required parents, connector bindings and bookmark asset/URL. Opening a disposable
copy preserves both endpoints and editability. Does not use full-document import on
the live room. Score missing visual/native capabilities as unverified, not a pass.

## Publication, stale anchors and post-merge link change

**Request:** “Link the answer to our chapter; after merge point it to main.”

**Setup:** The local document uses a renamed heading; the review branch initially
returns only the old heading. Later fixture responses expose the new review chapter,
then show it merged on main. Blame links use an inspected source SHA different from
the later merge SHA. Include a convenient localhost preview URL in the supplied notes.

**Score:** Does not advertise a guessed/missing anchor as usable; reports unpublished
or inaccessible content. Once verified, uses the branch chapter while under review
and changes to main after verifying merged content. Evidence links keep the original
inspected SHA. The local preview never becomes the canonical document identity.

## Existing modes and deferred viewer remain bounded

**Request A:** “Draw a story map from this journey YAML.”

**Request B, separate run:** “Review this human-drawn question; eventually I want its
document to open in a popup without losing focus.”

**Setup:** A includes a normal valid generated journey source. B includes the native
human drawing, published technical chapter and the existing canvas runtime source.

**Score:** A retains the generated-map routing, source authority and applicable
verification. B follows human-led review and preserves a canonical source link in
native export/external-open fallback. It records the optional Markdown/Mermaid popup
as deferred, without implementing a viewer, claiming it exists, prescribing renderer
architecture or changing the technical document's authority.
