# kc-ship-flow development closed — 2026-09-16

Captain: 「那就收」 (2026-09-16), after five batches (ship-cloud-wrapper r1–r4 on kc-claude-plugins,
qnow-clerk-poc on qnow): 14 tasks, 12 merged, 2 closed by the Captain; released as kc-ship-flow 0.3.0
(tag 1528bb8e) with kc-dev-flow 4.6.0; local installs synced 2026-09-16.

Rule from here: no batch exists to improve ship-flow itself. A ship defect is fixed only when a
product batch bites it, inside that batch. Two known candidates, unfiled:
- close.py matches a task's debrief by the first `## Shipped` mention; a sibling-naming debrief
  mis-mapped one r4 task (fence corrected by hand). Fix: worker echoes the dispatch token in its
  debrief; close.py matches on it.
- The boot does not state or check the worker runtime (kc-dev-flow >= 4.4.0, Spacedock 0.27.2);
  every batch needed a manual follow-up message.
Unproven: the UAT/e2e station (every batch so far was tooling or POC; receipts say e2e not recorded).
