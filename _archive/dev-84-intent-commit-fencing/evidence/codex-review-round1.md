Prior findings:

- **CLOSED [BLOCK]** `scripts/ship-flow/intent.sh:14-20` — `flock` replaced by portable atomic `mkdir`.
- **CLOSED [P2]** `scripts/ship-flow/intent.sh:64-73` — workspaces are filtered by project before counting.

New findings:

- **[P1]** `scripts/ship-flow/intent.sh:20,32-34` — trap is installed after lock acquisition and metadata writes. An error before line 34 leaves the lock behind; if `since` was never written, stale cleanup never considers it. `die`/exit 6 after line 34 is covered.
- **[P1]** `scripts/ship-flow/intent.sh:23-25` — stale handling is not host-safe. `kill -0` checks a local PID without recording hostname: it can delete an active remote holder after 120 seconds or retain an abandoned lock because an unrelated local process reused the PID. It does not safely fall back to age only.
- **[P1]** `scripts/ship-flow/intent.sh:24-26` — stale detection and deletion have a TOCTOU race. After the check, the original owner can release and another process can acquire; `rm -rf` then deletes the new owner’s lock, allowing two writers into the critical section.

```text
Remaining: Three new P1 lock-correctness issues
Next: Make trap installation immediate and redesign stale takeover with host-aware, fenced ownership (you)
Closable: no
```
