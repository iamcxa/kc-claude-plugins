# paseo extension

Optional dev2 policy for the Paseo worker handoff.

Requires: peers

Enable only through the adopter's extension choice. Confirmed Paseo peer asks and incoming replies use peers without this listing. The Captain's board, labels and gates remain outside this extension.

Use peers' Paseo binding for identity, send flags, replies, notices and recovery; read Paseo's own skill for current host capabilities. For status changes, follow peers' Current peer facts when delivered. An information-only notice requests no acknowledgement; a same-question correction uses the reply route, otherwise the new-send route. No-action peer finishes and answered worker permission requests require no Captain reply; errors and requests held for the Captain remain material. Preserve worker completion notifications. Listing paseo selects the worker procedure below, not peer-message permission.

## Workers through Paseo

For configured stage workers, resolve and record the repository tuple before build; supply its provider/model and thinkingOptionId through this existing route. Keep generated fields and immediate spawn order. Special roles stay unchanged.

For a listed paseo extension, this is the Paseo exception to the worker-opened Draft PR rule; other hosts keep their delivery owner. It grants no push, PR, ready or merge authority.

Spawn with create_agent, notifyOnFinish true and an explicit modeId, because a Codex child will not inherit a Claude FO's mode. In scope notes and follow-ups, replace the main line with: "Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt." A finished callback starts verification, as in Spacedock's Codex contract; without a Done line it is a handback or a stop, so read it and the report before advancing. Errored and permission callbacks never complete the stage.

Resolve the stage's absolute worktree on the destination host. Pass a matching workspaceId explicitly to create_agent. If Spacedock creates the worktree during dispatch build, chain paseo workspace create --isolation local --path <worktree> --background --json onto that same build command, so create_agent stays the next host action. Paseo's CLI spawn has no finish callback; do not use it for a stage worker. Check current Paseo help before use. A prompt saying cd is not placement. If placement is unavailable or mismatched, hold and return the gap to the Captain. Preserve Spacedock's generated prompt and immediate spawn order.

Add to scope notes: "Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. For a local browser check you drive yourself, first read extensions/paseo/browser.md under your Package root."

FO reconciles the local candidate and any existing PR, then under an applicable Captain grant pushes and opens or updates the Draft PR before validation. When roborev is listed, FO runs its existing gate on that exact base/head and records its result; findings return through the existing repair route. Missing access, authority, a mismatched head or incomplete review holds the dependent step. Preserve CI, independent validation and merge gates. Never widen sandbox permissions to make this practice work.

## Worker permission requests

A permission callback from a worker FO spawned for an open dispatch is FO's to answer; any other agent's follows peers. Read the request first. Allow only what FO could do itself in the task's scope and authority; deny an out-of-scope request with its reason; never pass updatedPermissions. Hold for the Captain a push to a repository he does not own, a merge or close, reading or printing a secret value (running through the secrets wrapper without reading or printing a value is allowed), a deletion beyond task-owned temporary files or another irreversible change, a message to a person or other outward write, spending money, a question asking for his judgment, and anything FO's own host refuses.

Copy agentId and requestId together from that request's block and answer each block once; never type, recall or adapt an id. After a refusal, or with no block in this turn, call get_agent_status for that worker. Read any returned pending request and decide it afresh under the same scope, authority and Captain holds; answer only its returned id. Never apply an approval or denial to a different requestId. If none is pending, the request is gone. Paseo refuses an id not pending for that agent.

Before a routine answer, write exactly one line `APPROVED: <what> FOR: <which worker>`; send no other text before it. After answering, add no status block or report to the Captain. An answered request ends no unit of work. A hold is one Captain message naming only the held request: its worker, action and decision needed. Include no recap of routine approvals; never answer the held request for him.

## Human terminals and pages

For an attended terminal or page in a workflow listing paseo, FO and workers use Paseo when available. Read the installed paseo skill and current tool parameters; missing skill or capability returns to FO. Before dispatch build, resolve the Captain's visible host, workspace ID and cwd separately from the code worktree. Keep the generated build-to-spawn sequence intact.

For each worker needing human interaction, add to scope notes: "Read the listed paseo extension's Human terminals and pages section before opening a human surface. Human host/workspace/cwd: <resolved values>. Code cwd: <assigned worktree>. Existing private page route: <URL or unverified>. Return placement or network gaps to FO."

Create the terminal at the visible cwd; execute the candidate by absolute path or change shell cwd afterwards. Confirm the Captain can find it and perform harmless input before a live request. Browser tools open in the caller's workspace on a connected host, in the background. A worker elsewhere returns the safe URL to its FO to open there. Missing placement or an unsupported product opener holds that step; do not silently substitute the OS browser. Preserve sign-in and confirmation boundaries; cancel an invisible live request before recreating it.

For another device, reuse an approved private route. Tailscale Serve may be a per-task fallback within the task's recorded authority: name host, port, allowed devices, lifetime and cleanup before setup. Return wider exposure or a different network choice to FO. Never infer page reach from localhost or daemon access. Verify the terminal and the page's rendering, expected pictures and intended interaction on the actual second device. HTTP 200 and desktop screenshots are insufficient. Record surface IDs, safe URL, device results, limits and owner in the task. Clean only task-owned surfaces, processes and route changes.
