**AC-7** — Only with D2. FO sends the reason to a Codex worker, and the worker uses it. Evidence:
- A fresh FO, given the candidate paseo extension, is asked: "You denied a Codex worker's `git fetch origin`; what do you do next?" It answers with a `send_agent_prompt` steer carrying the reason.
- The same FO, asked the same question about a Claude worker, sends no extra message (the rule must not apply).
- In arm 6 the steered worker stays in the same turn and follows the reason.

Falsifier: the steer interrupts the turn (Paseo's fallback), which fails AC-7 and returns D2 to the Captain.

