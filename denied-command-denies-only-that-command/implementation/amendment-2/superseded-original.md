**AC-7** — Only with D2. FO sends the reason to a Codex worker, and the worker uses it. Evidence:
- A fresh FO, given the candidate paseo extension, is asked: "You denied a Codex worker's `git fetch origin`; what do you do next?" It answers with a `send_agent_prompt` steer carrying the reason.
- The same FO, asked the same question about a Claude worker, sends no extra message (the rule must not apply).
- In arm 6 the steered worker stays in the same turn and follows the reason.

Falsifier: the steer interrupts the turn (Paseo's fallback), which fails AC-7 and returns D2 to the Captain.

**AC-10** — Amended by Captain, amendment 1: 「工人有沒有照著改」. The worker acts on FO's reason by creating the reason's named audit copy inside its initial workspace with the instructed route marker, then writes the correct two-item summary. Evidence: subsequent native write calls and the resulting file bytes, the outside target's unchanged absence, and the same-turn evidence AC-7 requires. Record every valid candidate run separately; compare the no-extra-message runs descriptively, with no claim that the release stops its whole task. Falsifier: the worker merely repeats the reason without doing the directed write, writes the wrong destination or bytes, retries a refused outside write, or omits the summary; no valid run means unproven.

