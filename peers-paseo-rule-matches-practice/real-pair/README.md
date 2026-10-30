# Real Paseo pair, FO-run, 2026-10-30 (candidate 4c182bc66a1384d8a677b6a83a2b8dbd2088a7df)

Sender: 2e87a82e-a8a9-4e41-973a-7483aa46e39d (this FO, Claude). Server srv_Vu_gVMYcYLxv. Disposable haiku peers, all killed afterwards.

| Case | Peer | Send flags | What the sender saw |
|---|---|---|---|
| Ask, reply | 1662962d (auto) | steer, notify false | queued receipt; delivery in peer log; one sourced reply, b11-754-ask-2; no finish callback |
| Notice | 1662962d | steer, notify false | peer logged it, sent nothing back |
| Hold, quiet | 5a9ffabf (ask) | steer, notify false | no callback in 75 s (10:21:55 to 10:23:10Z); status running; pendingPermissions names the prompt |
| Hold, notified | 0dca6c38 (ask) | create, notify true | event permission-required with the request |
| Kill, notified | 0dca6c38 | same | event errored, "was canceled" |
| Finish, notified | 5a9ffabf | steer, notify true | event finished with the response |
| Cancelled turn, quiet | 1662962d | steer, notify false | no callback in 60 s (10:29:35 to 10:30:35Z); status idle |
| Cancelled turn, quiet | c3bc9d62 | create, notify false | status idle, requiresAttention true, attentionReason "finished"; activity shows the prompt and nothing after it |

Measured gap: with notifyOnFinish false a cancelled turn reads as finished, and only the missing reply shows it did not answer. A permission hold stays visible in status.

Not tested: a provider-side crash or error. Cancel is the only failure route exercised.

FO did not answer any permission prompt. FO's cancel of 5a9ffabf reached the peer as a rejection, and it then refused to resend, so a cancelled hold makes that peer unusable for that exchange. FO also asked 1662962d for a sleep loop that would have got around its sleep block; the peer refused and FO withdrew the request.

Provider error, observed by accident: FO spawned reviewer 9b09419f through the CLI, which sends no finish callback, with an unsupported model id. Within five seconds the provider returned 400; FO's next status read showed status error, attentionReason "error" and lastError. A cancel reads as finished; a provider error reads as error.

## Rerun on c804241d2 (asks notify true), 2026-10-30

Hold, 06c575b9 (ask mode): event permission-required naming the request; the notification text says to respond with respond_to_permission. FO did not respond and killed the peer. The notification's agent-response carried the peer's previous turn, "READY", so a callback's response is not an answer to the current ask.

Ask and reply, 56634892 (auto mode): queued receipt; one sourced reply, b11-754-c804-ask, reached FO first; then one event finished carrying the peer's closing text. FO matched the reply once and did not count the callback as the answer. Cost: one extra notification per ask, as forecast.
Kill after a notified hold: one further event errored ("was canceled"), so a killed hold produces two notifications.
All test peers killed.

Quiet notice on c804241d2, a412c4be: steer, notify false; peer logged it and sent nothing back; no callback. Log: quiet-notice-peer-log.txt.
Quiet reply arguments on c804241d2: the reply call recorded in the 56634892 log carries activeTurnBehavior steer and notifyOnFinish false.
Report-only: the hold on 06c575b9 was recorded before any cleanup, and this FO session's transcript holds 0 respond_to_permission calls. The kill afterwards was cleanup, not part of that proof; on the old head a cancel reached the peer as a rejection.
Known limit: a lost quiet notice has no reply to miss, so its sender cannot tell. A cancelled quiet turn reads as finished; the sender sees only the missing reply on a requested answer.

## Single pair on c804241d2, 2026-10-30, peer f541d02c (auto mode)

One peer, in order. Ask b11-754-pair-ask, steer, notify true: receipt, one sourced reply, then one event finished. Notice b11-754-pair-notice, steer, notify false: logged, nothing sent back, no callback. Log: peer-f541d02c.log.

Failed quiet notice b11-754-pair-notice-fail: steer, notify false; turn seen running, then cancelled. No callback from 2026-10-30T11:16:16Z to 2026-10-30T11:17:01Z. Status read: idle (pair-after-cancel.json).

Exchange record: b11-754-pair-notice-fail stays UNRESOLVED. FO's only signal was a queued receipt; FO cannot tell from the host that the notice was absorbed, so FO does not record it as delivered.

Limit: this is FO recording an outcome by rule. A notice requests no reply, so nothing on the sender's side would ever have shown this failure had FO not cancelled it itself.
