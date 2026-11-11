Budget: One cycle per stage.
# comment-sent-when-added-relay implementation

Symptom: none
Dispatched: 8b3e237014fb9b62f650c0e2fea2db0d89ebc432 (relay origin/main), worktree .worktrees/spacedock-ensign-comment-sent-when-added-relay
Model: codex gpt-6.1-sol, reasoning xhigh (the Captain, 2026-10-26: sol or astra)
Captain: 「准」 (chat, 2026-11-09) at the ideation gate.

## Checklist

Implement comment-sent-when-added-relay's Design on the task branch against the Web host contract H1-H8 (web-contract.md): pass sendOnAdd when Web advertises 'send-on-add', one annotation per submit resolved only after relay stores the Result, identical-bytes retry returning the existing Result, the name question inside submit at the first Add with the sign-in hold of one comment, refused/failed text kept, limit refusals carrying codes 'review-full' and 'session-full', and echoed just-sent cards carrying the annotation id, with owning tests that fail on base and pass on the candidate

Write the new Relay ADR 0075 superseding ADR 0067's first-Submit timing as the design states, update the Room protocol, HTTP contract and OpenAPI where the contract changes, keep the existing Room, session, feedback and decision suites green, run the checks the repository requires (unit suite on Linux node:24.18.0 as the reference) and the RoboRev gate, then commit and push the task branch and open a Draft PR

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0
Load the stage skill kc-dev-flow-2:implementation. Profile pilot. Read comment-sent-when-added-relay.md (Design, Acceptance criteria, Number guards ADR: 0075) and comment-sent-when-added-relay/web-contract.md in the state checkout /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state. The Captain approved the ideation gate: 「准」 (chat, 2026-11-09), having seen the corrected fixture pictures.
Web contract: Web's comment-sent-when-added passed its gate and ships inert behind the host option; read Web read-only from ~/conductor/repos/subspace-web after a fetch; do not edit Web. H9-H10 (includes of just-sent comments, decision admissible after 100) belong to owner-decision-after-sent-comments, implemented next on its own branch; do not implement them here, and do not take the decision slot change.
Relay main is 8b3e237014fb9b62f650c0e2fea2db0d89ebc432. Sibling branch in flight: link-trust-per-revision (PR #490, draft) touches public/room-bootstrap.js and room-view.ts; keep your diff narrow and do not absorb it.
Push: under the Captain's standing grant 「SD review 範圍內（relay、web、v0）的 dev2 任務，FO 和工人可以推任務分支、開草稿 PR、改成正式送審；合併、關 PR 和 release 仍由我決定。」 (AGENTS.md), push the task branch (normal push, never --force) and open a Draft PR titled feat(relay): …; do not mark it ready, do not merge.
Local runs: isolated archives under /tmp/comment-sent-when-added-relay-implementation-1/, private HOME/XDG, env -i allowlist; install with pnpm 10.26.1 from /Users/kent/Library/pnpm/store/v3. Linux reference: build a local image FROM node:24.18.0 with apt jq and uuid-runtime, as PR #455/#490 did (see state link-trust-per-revision/implementation-1/ evidence), and run the unit suite there with --network none; the npm registry may be reached only for lockfile-pinned Linux native packages. Known: netlify/routes.test.ts WorkOS token-endpoint case can exceed 5 s on base too; netlify/lib/close-race.wire.test.ts fails on this Mac on base. Run the RoboRev gate with the normal HOME (only that command). Local Netlify dev hits file-watch limits on this Mac; if a signed-in browser run fails twice for setup reasons, stop that leg and say so. Browsers: separate /tmp profile, PLAYWRIGHT_BROWSERS_PATH=/Users/kent/Library/Caches/ms-playwright, never download Chromium, never Kent's Chrome. No secrets, no hosted writes beyond the PR's own Deploy Preview build.
Not allowed: git stash; wildcard deletes; editing installed plugin files; changing Web; messaging anyone but the FO.
Before reporting, run python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 8b3e2370.
Write "## Stage Report: implementation" with the checklist lines verbatim as items into comment-sent-when-added-relay.md on the state checkout; evidence under comment-sent-when-added-relay/implementation-1/, files under 1 MB. Leave state uncommitted; the FO commits.
Send your completion message to `main`; as a Paseo Codex agent, your final message is that completion message.