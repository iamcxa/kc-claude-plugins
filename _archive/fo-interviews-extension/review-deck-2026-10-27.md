# Review deck interview (2026-10-27)

At the Captain's request (chat, 2026-10-27, quoted in task batch-reaches-each-gate-together): how gate briefings carry design previews. Asked of the relay and web FOs only. Answers are data.

## subspace-web/v0 dev2 FO (Paseo 295b873d), 2026-10-27, code claims at Web main 88d1276

1. Last time: review-page-reads-as-an-app, ideation cycle 2, 2026-10-27. Gate briefing: a Chinese Markdown file published with `subspace-relay-client publish <file> --question … --open-owner-link` to review.spacedock.md (share w4ah4kjg7q3dkfgn). Previews: a tailnet-only URL in the briefing (a local static server with today/A1/A2 and alternatives). The Captain answered in chat with a screenshot (「這裡的 3 not submitted 在這裡不太對，改一下，其他整體我覺得 A1 比較好」), recorded with `spacedock gate record --decision approve --reason "<his words> Asked: <question> (share id)"`. Other gates he approved with Finish review, read with `decision --with-included`, recorded with share id and timestamp.
2. One briefing cannot carry HTML previews today. It carries several Markdown parts (Room part select; `docs=2` in Web's tests). Web renders Markdown only; an image is drawn as a placeholder (`.subspace-web-image::before` in src/render.js). The frame is a sandboxed, opaque-origin document; HTML or images inside it would be a bridge and security change (AGENTS.md "browser authority boundary"). The decision is per briefing, not per part.
3. Owners: rendering spacedock-dev/subspace-web (Web FO); publish format, storage, Room and limits spacedock-dev/subspace-relay (relay FO 1671c3a9); publish CLI subspace-v0 (v0 FO). Each change is the Captain's to approve.
4. Its reading, not designed or measured: smallest step is images as briefing parts or inline (static screenshots, no script), still needing Web image admission, a security review and relay storage for image bytes. For a batch: one briefing whose parts are tasks plus a per-part decision; today one decision per briefing, so new in relay and Web. Live HTML previews stay as links; tailnet links reach only the Captain.

## relay dev2 FO (Paseo 1671c3a9), 2026-10-27, from task records only

1. pair-once (archived): the Captain asked for a clickable prototype first (「可以，一樣先出設計讓我試用」, 2026-10-24), tried it on his phone, answered 「可以」 in chat (2026-10-25), recorded as a Captain direction; gate approvals via gate prepare/record with his chat words in --reason. review-keyword-invocations (spacedock#852, 2026-10-27): a local design/preview.html plus pictures-v1..v3 pages reviewed by a design director, not the Captain; no Review deck used for previews.
2. Not verified: no record of a briefing carrying several HTML previews; did not read the Briefing contract or relay code.
3. Storage and publish: spacedock-dev/subspace-relay (relay FO with the Captain); rendering: subspace-web (web FO). The Briefing format is shared; which repository is canonical is not in its records.
4. None from records; a real answer needs a reading of the Briefing schema and the relay publish path, which it can do as a relay task if the Captain asks in its workflow.

