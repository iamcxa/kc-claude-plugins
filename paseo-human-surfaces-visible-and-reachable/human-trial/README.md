# Attended human-surface trial, FO-run, 2026-11-01, candidate 8aa76f15f

Host srv_Vu_gVMYcYLxv, Captain's visible workspace wks_a8f029f6e72d90cb, cwd the colombo workspace.

Terminal 44e0744d "Human surface trial": FO sent `printf 'surface-ready\n'`. The Captain said 「我用手機貼上了」; capture shows `captain-visible` twice and the terminal re-wrapped to a narrower width. Pasted over Paseo with the phone offline on Tailscale, so the terminal reach does not depend on Tailscale.

Page: /tmp/hs-trial, `python3 -m http.server 52901 --bind 127.0.0.1`, tab 78f6236d in the same workspace.
Intact: naturalWidth 80 and naturalHeight 80, screenshot shows the green square, network shows probe.svg.
Negative control: probe.svg renamed, HTML still 200, svg 404, naturalWidth 0. Then restored.
Serve baseline before any change: serve-baseline.json, ports 8410, 8412, 8531, 8617, 8660, 8725, none owned by this trial.

Desktop tab: the Captain said 「好了」 at step 2; evaluate read result "clicked", naturalWidth 80, naturalHeight 80.

Phone page: no approved private route existed for this page, so FO used the accepted per-task Tailscale Serve fallback: host kentmacbookpro-3, `tailscale serve --https=8413 52901` in foreground terminal ec69258e, tailnet only, lifetime this step. https://kentmacbookpro-3.tail815bb3.ts.net:8413/
Phone pixel-10-pro-xl online, direct; server log 10:23:41 +08 shows the page, the picture and the favicon. The Captain: 「按了」, then asked whether he saw the green square and clicked: 「有」. A phone click sends no request, so that result rests on his word.

Cleanup: Serve and http.server stopped, tab and both terminals closed and read back absent, Serve config equal to serve-baseline.json.

Not verified:
- denied access for an excluded device: the tailnet holds only the Captain's own devices.
- worker URL handback (step 4): no ordinary dispatched worker needed a page in this trial, so it was not exercised.
- relay's real rr replay (step 6): separate.
